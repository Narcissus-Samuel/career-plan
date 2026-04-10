from flask import Blueprint, request, jsonify
from db import get_db
import json
import time
import re
from functools import lru_cache
from services.llm_service import call_llm
from routes.auth import token_required

match_bp = Blueprint('match', __name__, url_prefix='/api/match')


# ====================== 工具函数 ======================
def extract_years_from_text(text):
    """从文本中提取年限（估算，如“2年”、“18个月”）。"""
    if not text:
        return 0.0
    text = str(text)
    years = 0.0

    for m in re.findall(r'(\d+(?:\.\d+)?)\s*(?:年|yrs?|years?)', text, flags=re.IGNORECASE):
        try:
            years += float(m)
        except ValueError:
            continue
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


# ====================== 学生能力获取 ======================
def get_student_ability(student_id):
    """获取学生能力画像，同时从 assessment_results 表获取最新兴趣测评得分"""
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


# ====================== 岗位能力获取（带缓存） ======================
@lru_cache(maxsize=256)
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
        return {
            'skills': set(),
            'certificates': set(),
            'soft_abilities': {},
            'experience_requirement': None,
            'education_required': None
        }

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


# ====================== 大类预筛选 ======================
def get_relevant_categories(student_ability):
    """
    根据学生的专业、兴趣、技能，返回可能感兴趣的大类 ID 列表（最多5个）
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM job_categories")
    all_cats = cursor.fetchall()
    conn.close()

    # 规则1：兴趣映射（如果有兴趣测评）
    interest = student_ability.get('interest', {})
    interest_to_cat = {
        'I': '技术研发',
        'R': '技术研发',
        'A': '产品设计',
        'E': '市场营销',
        'S': '运营管理',
        'C': '行政办公'
    }
    if interest:
        # 取兴趣得分最高的维度
        top_dim = max(interest.items(), key=lambda x: x[1])[0]  # 如 'I'
        pref_cat_name = interest_to_cat.get(top_dim, '')
        if pref_cat_name:
            pref_cat_ids = [c['id'] for c in all_cats if c['name'] == pref_cat_name]
            if pref_cat_ids:
                return pref_cat_ids[:3]

    # 规则2：专业关键词匹配
    major = student_ability.get('major', '') or ''
    major_lower = major.lower()
    keyword_to_cat = {
        '计算机': '技术研发',
        '软件': '技术研发',
        '设计': '产品设计',
        '市场': '市场营销',
        '营销': '市场营销',
        '人力': '运营管理',
        '行政': '行政办公'
    }
    for kw, cat_name in keyword_to_cat.items():
        if kw in major_lower:
            cat_ids = [c['id'] for c in all_cats if c['name'] == cat_name]
            if cat_ids:
                return cat_ids[:3]

    # 默认：返回前三个大类（或全量）
    return [c['id'] for c in all_cats[:3]]


# ====================== 差距分析生成（仅用于详情接口） ======================
def generate_gap_analysis_with_llm(student_ability, job_ability, match_detail):
    """
    使用大模型根据具体差距生成分析建议
    """
    need_skills = list(job_ability['skills'] - student_ability['skills'])
    need_certs = list(job_ability['certificates'] - student_ability['certificates'])

    soft_gaps = []
    for dim, job_val in job_ability['soft_abilities'].items():
        stu_val = student_ability['soft_abilities'].get(dim, {}).get('score', 0)
        if job_val.get('score', 0) > stu_val + 1:
            soft_gaps.append(dim)

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
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        analysis = json.loads(result)
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
        return {
            "base": "请根据岗位要求补充相关证书。",
            "skills": "建议针对缺失技能进行系统学习。",
            "quality": "可参加团队项目锻炼软能力。",
            "potential": "制定长期提升计划，逐步追赶岗位要求。",
            "recommended_resources": "推荐 Coursera、慕课网、书籍等学习资源，并结合项目实战提升。"
        }


# ====================== 匹配度计算（核心） ======================
def compute_match(student_ability, job_ability, generate_gap=False):
    """
    计算学生与岗位的匹配度，可选择是否生成 LLM 差距分析
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

    if generate_gap:
        match_detail['gap_analysis'] = generate_gap_analysis_with_llm(student_ability, job_ability, match_detail)
    else:
        match_detail['gap_analysis'] = {}   # 前端可显示“点击查看详细分析”
    return match_detail


# ====================== 接口：推荐岗位列表（优化版，无 LLM 调用） ======================
@match_bp.route('/recommend', methods=['GET'])
def recommend():
    """
    获取推荐岗位列表（基于大类预筛选 + 唯一岗位名称去重 + 缓存）
    仅计算匹配分数，不生成 LLM 差距分析，响应速度快
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

    # 获取相关的大类ID
    relevant_cat_ids = get_relevant_categories(student_ability)

    conn = get_db()
    cursor = conn.cursor()

    # 根据大类筛选唯一的岗位名称
    if relevant_cat_ids:
        placeholders = ','.join('?' for _ in relevant_cat_ids)
        cursor.execute(f"""
            SELECT DISTINCT job_name
            FROM job
            WHERE category_id IN ({placeholders})
        """, relevant_cat_ids)
    else:
        cursor.execute("SELECT DISTINCT job_name FROM job")

    unique_job_names = [row['job_name'] for row in cursor.fetchall()]
    conn.close()

    # 降级：如果没有找到任何岗位，使用 job_profile 中的名称
    if not unique_job_names:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT job_name FROM job_profile")
        unique_job_names = [row['job_name'] for row in cursor.fetchall()]
        conn.close()

    if not unique_job_names:
        return jsonify({'message': '暂无岗位数据', 'results': []}), 200

    results = []
    for job_name in unique_job_names:
        job_ability = get_job_abilities(job_name)   # 已加缓存
        match_detail = compute_match(student_ability, job_ability, generate_gap=False)  # 关键：不生成分析
        item = {'job_name': job_name, **match_detail}
        if 'interest' in student_ability:
            item['interest_scores'] = student_ability['interest']
        results.append(item)

    results.sort(key=lambda x: x['overall_score'], reverse=True)
    filtered = results[:limit]

    return jsonify({'results': filtered, 'total': len(results)})


# ====================== 接口：单岗位详细匹配（生成 LLM 分析并保存） ======================
@match_bp.route('/match', methods=['POST'])
def match():
    """
    计算指定岗位的详细匹配度，并生成 LLM 差距分析（用于报告生成）
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
    match_detail = compute_match(student_ability, job_ability, generate_gap=True)   # 这里生成分析

    # 保存到数据库（确保 details 完整）
    try:
        conn = get_db()
        cursor = conn.cursor()
        details_json = json.dumps(match_detail, ensure_ascii=False)
        cursor.execute('''
            INSERT INTO match_history 
            (student_id, job_name, match_score, details, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            student_id,
            job_name,
            match_detail['overall_score'],
            details_json,
            int(time.time())
        ))
        conn.commit()
        print("✅ 匹配记录已保存，details=", details_json)
    except Exception as e:
        print("❌ 保存失败：", e)
    finally:
        conn.close()

    return jsonify(match_detail)


# ====================== 接口：匹配历史 ======================
@match_bp.route('/history/<int:student_id>', methods=['GET'])
@token_required
def get_match_history(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, job_name, match_score, details, created_at
        FROM match_history
        WHERE student_id = ?
        ORDER BY created_at DESC
    ''', (student_id,))
    rows = cursor.fetchall()
    conn.close()

    history = []
    for r in rows:
        history.append({
            'id': r['id'],
            'job_name': r['job_name'],
            'match_score': r['match_score'],
            'details': r['details'],   # 包含完整的 gap_analysis
            'created_at': r['created_at']
        })
    return jsonify({'history': history})
# ====================== 流式匹配接口（边生成边返回） ======================
from flask import Response, stream_with_context
import time

@match_bp.route('/match-stream', methods=['POST'])
def match_stream():
    """
    流式生成人岗匹配报告，实时返回匹配分数和差距分析的各部分内容
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

    # 先计算匹配分数（不调用 LLM）
    match_detail = compute_match(student_ability, job_ability, generate_gap=False)

    def generate():
        # 1. 发送基础分数（一次性）
        base_info = {
            'overall_score': match_detail['overall_score'],
            'skill_fit': match_detail['skill_fit'],
            'soft_gap': match_detail['soft_gap'],
            'cert_coverage': match_detail['cert_coverage'],
            'education_score': match_detail['education_score'],
            'experience_score': match_detail['experience_score']
        }
        yield f"data: {json.dumps({'type': 'base', 'data': base_info})}\n\n"

        # 2. 生成差距分析（流式）
        # 调用 LLM 获取五个字段的文本，为了流式效果，我们一次性生成后拆分发送（模拟流式）
        # 如果您的 call_llm 支持流式，可改为真正的 token 级流式；这里先使用同步生成再拆分。
        full_analysis = generate_gap_analysis_with_llm(student_ability, job_ability, match_detail)
        # 按字段逐个发送
        for key in ['base', 'skills', 'quality', 'potential', 'recommended_resources']:
            text = full_analysis.get(key, '')
            yield f"data: {json.dumps({'type': 'gap', 'field': key, 'text': text})}\n\n"
            time.sleep(0.05)  # 轻微延迟，让前端感知流式

        # 3. 保存完整匹配结果到数据库（可选）
        match_detail['gap_analysis'] = full_analysis
        try:
            conn = get_db()
            cursor = conn.cursor()
            details_json = json.dumps(match_detail, ensure_ascii=False)
            cursor.execute('''
                INSERT INTO match_history 
                (student_id, job_name, match_score, details, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                student_id,
                job_name,
                match_detail['overall_score'],
                details_json,
                int(time.time())
            ))
            conn.commit()
        except Exception as e:
            print("保存失败", e)
        finally:
            conn.close()

        # 4. 发送完成信号
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')