from flask import Blueprint, request, jsonify
from db import get_db
import json
import time
import re
from services.llm_service import call_llm

match_bp = Blueprint('match', __name__, url_prefix='/api/match')

def extract_years_from_text(text):
    """从文本中提取年限（估算，如“2年”、“18个月”）。"""
    if not text:
        return 0.0
    text = str(text)
    years = 0.0

    # 优先匹配明显的年
    for m in re.findall(r'(\d+(?:\.\d+)?)\s*(?:年|yrs?|years?)', text, flags=re.IGNORECASE):
        try:
            years += float(m)
        except ValueError:
            continue

    # 再匹配月份
    for m in re.findall(r'(\d+(?:\.\d+)?)\s*(?:月|mos?|months?)', text, flags=re.IGNORECASE):
        try:
            years += float(m) / 12.0
        except ValueError:
            continue

    return round(years, 2)


def extract_experience_requirement(text):
    """从岗位描述文本中提取招聘经验要求（min_year, max_year）。"""
    if not text:
        return None
    text = str(text)

    # 例如 1-3年, 3年以上, 经验2年
    m = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*年', text)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r'(\d+(?:\.\d+)?)\s*年以上', text)
    if m:
        v = float(m.group(1))
        return v, None
    m = re.search(r'经验\s*(\d+(?:\.\d+)?)\s*年', text)
    if m:
        v = float(m.group(1))
        return v, None

    return None


def normalize_education_level(level):
    """将教育文本映射为数值等级。"""
    if not level:
        return None
    level = str(level).strip().lower()
    if '博士' in level or 'phd' in level:
        return 4
    if '硕士' in level or 'master' in level:
        return 3
    if '本科' in level or 'bachelor' in level:
        return 2
    if '大专' in level or '专科' in level or 'associate' in level:
        return 1
    if '高中' in level or '中专' in level or '高职' in level:
        return 0
    return None


def get_student_ability(student_id):
    """
    获取学生能力画像，同时从 assessment_results 表获取最新兴趣测评得分
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT skills, certificates, soft_abilities, user_id, major, grade, internships,
               education_json, work_json, project_json
        FROM student WHERE id = ?
    ''', (student_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    skills = set(json.loads(row['skills']) if row['skills'] else [])
    certificates = set(json.loads(row['certificates']) if row['certificates'] else [])
    soft_abilities = json.loads(row['soft_abilities']) if row['soft_abilities'] else {}

    internships = row['internships'] if 'internships' in row.keys() else ''
    major = row['major'] if 'major' in row.keys() else None
    grade = row['grade'] if 'grade' in row.keys() else None

    estimated_exp = extract_years_from_text(internships or '')

    education_json = json.loads(row['education_json']) if row['education_json'] else {}
    work_json = json.loads(row['work_json']) if row['work_json'] else []
    project_json = json.loads(row['project_json']) if row['project_json'] else []

    student = {
        'skills': skills,
        'certificates': certificates,
        'soft_abilities': soft_abilities,
        'user_id': row['user_id'],
        'major': major,
        'grade': grade,
        'internships': internships,
        'experience_years': estimated_exp,
        'education_json': education_json,
        'work_json': work_json,
        'project_json': project_json
    }

    if student['user_id']:
        cursor.execute('''
            SELECT dimension_scores FROM assessment_results
            WHERE user_id = ? ORDER BY id DESC LIMIT 1
        ''', (student['user_id'],))
        interest_row = cursor.fetchone()
        if interest_row:
            student['interest'] = json.loads(interest_row['dimension_scores'])
    conn.close()
    return student


def get_job_abilities(job_name):
    """
    从 job_profile 和 job 表获取岗位画像信息
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT skills, certificates, soft_abilities FROM job_profile WHERE job_name = ?', (job_name,))
    row = cursor.fetchone()

    # 额外从 job 表抓取可能的 experience 要求与教育要求
    cursor.execute('SELECT job_description FROM job WHERE job_name = ?', (job_name,))
    job_row = cursor.fetchone()

    conn.close()

    if not row:
        return {'skills': set(), 'certificates': set(), 'soft_abilities': {}, 'experience_requirement': None, 'education_required': None}

    job_description = ''
    if job_row:
        job_description = job_row['job_description'] if 'job_description' in job_row.keys() and job_row['job_description'] else ''
    exp_req = extract_experience_requirement(job_description)

    edu_req = None
    edu_match = re.search(r'(博士|硕士|本科|大专|专科|高中|phd|master|bachelor|associate)', job_description or '', flags=re.IGNORECASE)
    if edu_match:
        edu_req = normalize_education_level(edu_match.group(1))

    return {
        'skills': set(json.loads(row['skills']) if row['skills'] else []),
        'certificates': set(json.loads(row['certificates']) if row['certificates'] else []),
        'soft_abilities': json.loads(row['soft_abilities']) if row['soft_abilities'] else {},
        'experience_requirement': exp_req,
        'education_required': edu_req
    }

def generate_gap_analysis_with_llm(student_ability, job_ability, match_detail):
    """
    使用大模型根据具体差距生成分析建议
    """
    # 获取缺失的具体技能和证书
    need_skills = list(job_ability['skills'] - student_ability['skills'])
    need_certs = list(job_ability['certificates'] - student_ability['certificates'])
    
    # 软能力差距（列出差距较大的维度）
    soft_gaps = []
    for dim, job_val in job_ability['soft_abilities'].items():
        stu_val = student_ability['soft_abilities'].get(dim, {}).get('score', 0)
        if job_val.get('score', 0) > stu_val + 1:
            soft_gaps.append(dim)

    # 构建提示词
    prompt = f"""
你是一位专业的职业规划师。根据以下学生与目标岗位的匹配数据，为每个维度生成一段具体的、有针对性的改进建议。
要求：
- 每个维度一段话，直接针对缺失项给出建议，不要使用"根据您的情况"之类的开头。
- 语气专业、鼓励，长度适中（每段50-100字）。
- 基于实际缺失项，不要泛泛而谈。

匹配数据：
- 证书覆盖率：{match_detail['cert_coverage']}%
- 缺失的证书：{', '.join(need_certs) if need_certs else '无'}
- 技能匹配度：{match_detail['skill_fit']}%
- 缺失的技能：{', '.join(need_skills) if need_skills else '无'}
- 软能力差距维度：{', '.join(soft_gaps) if soft_gaps else '无'}
- 综合匹配度：{match_detail['overall_score']}%

请按以下 JSON 格式返回五个维度的建议（只返回 JSON，不要其他文字）：
{{
    "base": "证书方面的建议",
    "skills": "技能方面的建议",
    "quality": "软能力方面的建议",
    "potential": "发展潜力方面的建议",
    "recommended_resources": "学习资源建议（课程/书籍/项目）"
}}
"""
    try:
        result = call_llm(prompt, temperature=0.7, max_tokens=800)
        # 解析 JSON
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        analysis = json.loads(result)
        # 确保五个字段都存在
        required = ['base', 'skills', 'quality', 'potential', 'recommended_resources']
        for field in required:
            if field not in analysis or not analysis[field]:
                if field == 'recommended_resources':
                    analysis[field] = "推荐 Coursera、慕课网、书籍等学习资源，并结合项目实战提升。"
                else:
                    analysis[field] = f"暂无具体建议，请针对{field}加强学习。"
        return analysis
    except Exception as e:
        print(f"大模型生成差距分析失败：{e}")
        # 降级方案：返回简单提示
        return {
            "base": "请根据岗位要求补充相关证书。",
            "skills": "建议针对缺失技能进行系统学习。",
            "quality": "可参加团队项目锻炼软能力。",
            "potential": "制定长期提升计划，逐步追赶岗位要求。",
            "recommended_resources": "推荐 Coursera、慕课网、书籍等学习资源，并结合项目实战提升。"
        }

def compute_match(student_ability, job_ability):
    """
    计算学生与岗位的匹配度，并生成差距分析文本
    """
    # 技能相似度（Jaccard）
    if student_ability['skills'] and job_ability['skills']:
        skill_inter = student_ability['skills'] & job_ability['skills']
        skill_union = student_ability['skills'] | job_ability['skills']
        skill_sim = len(skill_inter) / len(skill_union)
    else:
        skill_sim = 0.0

    # 证书覆盖率
    if student_ability['certificates'] and job_ability['certificates']:
        cert_cov = len(student_ability['certificates'] & job_ability['certificates']) / len(job_ability['certificates'])
    else:
        cert_cov = 0.0

    # 软能力相似度（余弦）
    all_dims = set(student_ability.get('soft_abilities', {}).keys()) | set(job_ability.get('soft_abilities', {}).keys())
    if all_dims:
        stu_vec = [student_ability.get('soft_abilities', {}).get(d, {}).get('score', 0) for d in all_dims]
        job_vec = [job_ability.get('soft_abilities', {}).get(d, {}).get('score', 0) for d in all_dims]
        dot = sum(a * b for a, b in zip(stu_vec, job_vec))
        norm_stu = sum(a * a for a in stu_vec) ** 0.5
        norm_job = sum(b * b for b in job_vec) ** 0.5
        soft_sim = dot / (norm_stu * norm_job) if norm_stu and norm_job else 0.0
    else:
        soft_sim = 0.0

    # 教育背景匹配
    education_score = 1.0
    student_edu = normalize_education_level(student_ability.get('grade') or student_ability.get('major'))
    required_edu = job_ability.get('education_required')
    if required_edu is not None:
        if student_edu is None:
            education_score = 0.7
        elif student_edu >= required_edu:
            education_score = 1.0
        else:
            education_score = max(0.0, 1.0 - (required_edu - student_edu) * 0.25)

    # 经验匹配
    exp_score = 1.0
    stu_exp = float(student_ability.get('experience_years') or 0.0)
    exp_req = job_ability.get('experience_requirement')
    if exp_req:
        min_req, max_req = exp_req
        if min_req is not None and stu_exp < min_req:
            exp_score = max(0.0, 1.0 - (min_req - stu_exp) / max(min_req, 1.0))
        elif max_req is not None and stu_exp > max_req:
            exp_score = max(0.0, 1.0 - (stu_exp - max_req) / max(max_req, 1.0) * 0.5)
        else:
            exp_score = 1.0

    # 综合得分（权重调整）
    w_skill = 0.45
    w_soft = 0.20
    w_cert = 0.10
    w_exp = 0.15
    w_edu = 0.10
    total = w_skill * skill_sim + w_soft * soft_sim + w_cert * cert_cov + w_exp * exp_score + w_edu * education_score
    total = max(0.0, min(1.0, total))

    match_detail = {
        'overall_score': round(total * 100, 1),
        'skill_fit': round(skill_sim * 100, 1),
        'soft_gap': round((1 - soft_sim) * 100, 1),
        'cert_coverage': round(cert_cov * 100, 1),
        'education_score': round(education_score * 100, 1),
        'experience_score': round(exp_score * 100, 1)
    }

    # 使用大模型生成差距分析
    match_detail['gap_analysis'] = generate_gap_analysis_with_llm(student_ability, job_ability, match_detail)

    return match_detail

@match_bp.route('/recommend', methods=['GET'])
def recommend():
    """
    获取所有岗位的匹配推荐列表（包含差距分析文本）
    """
    student_id = request.args.get('student_id', type=int)
    limit = request.args.get('limit', 10, type=int)

    if student_id is None:
        return jsonify({'error': '缺少 student_id 参数'}), 400

    student_ability = get_student_ability(student_id)
    if not student_ability:
        return jsonify({'error': '学生不存在'}), 404

    if not student_ability.get('skills'):
        return jsonify({'error': '学生能力数据不完整，请先完善技能信息'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT job_name FROM job_profile")
    jobs = [row['job_name'] for row in cursor.fetchall()]
    conn.close()

    if not jobs:
        return jsonify({'message': '暂无岗位数据', 'results': []}), 200

    results = []
    for job in jobs:
        job_ability = get_job_abilities(job)
        match_detail = compute_match(student_ability, job_ability)
        item = {'job_name': job, **match_detail}
        if 'interest' in student_ability:
            item['interest_scores'] = student_ability['interest']
        results.append(item)

    results.sort(key=lambda x: x['overall_score'], reverse=True)
    filtered = results[:limit]

    if not filtered:
        return jsonify({'message': '暂无匹配岗位', 'results': []}), 200

    return jsonify({'results': filtered, 'total': len(results)})

@match_bp.route('/match', methods=['POST'])
def match():
    """
    计算指定岗位的详细匹配度（用于生成报告）
    """
    data = request.json
    student_id = data.get('student_id')
    job_name = data.get('job_name')
    if not student_id or not job_name:
        return jsonify({'error': '缺少参数'}), 400

    student_ability = get_student_ability(student_id)
    if not student_ability:
        return jsonify({'error': '学生不存在'}), 404

    if not student_ability.get('skills'):
        return jsonify({'error': '学生能力数据不完整，请先完善技能信息'}), 400

    job_ability = get_job_abilities(job_name)
    match_detail = compute_match(student_ability, job_ability)

    # 可选：存入匹配历史
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO match_history (student_id, job_name, match_score, details, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        student_id,
        job_name,
        match_detail['overall_score'],
        json.dumps(match_detail, ensure_ascii=False),
        int(time.time())
    ))
    conn.commit()
    conn.close()

    return jsonify(match_detail)