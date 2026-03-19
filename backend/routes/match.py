from flask import Blueprint, request, jsonify
from db import get_db
import json
import time
import re
from services.llm_service import _call_zhipu

match_bp = Blueprint('match', __name__, url_prefix='/api/match')

def get_student_ability(student_id):
    """
    获取学生能力画像，同时从 assessment_results 表获取最新兴趣测评得分
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT skills, certificates, soft_abilities, user_id
        FROM student WHERE id = ?
    ''', (student_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    student = {
        'skills': set(json.loads(row['skills']) if row['skills'] else []),
        'certificates': set(json.loads(row['certificates']) if row['certificates'] else []),
        'soft_abilities': json.loads(row['soft_abilities']) if row['soft_abilities'] else {},
        'user_id': row['user_id']
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
    从 job_profile 表获取岗位画像信息
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT skills, certificates, soft_abilities FROM job_profile WHERE job_name = ?', (job_name,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {'skills': set(), 'certificates': set(), 'soft_abilities': {}}
    return {
        'skills': set(json.loads(row['skills']) if row['skills'] else []),
        'certificates': set(json.loads(row['certificates']) if row['certificates'] else []),
        'soft_abilities': json.loads(row['soft_abilities']) if row['soft_abilities'] else {}
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

请按以下 JSON 格式返回四个维度的建议（只返回 JSON，不要其他文字）：
{{
    "base": "证书方面的建议",
    "skills": "技能方面的建议",
    "quality": "软能力方面的建议",
    "potential": "发展潜力方面的建议"
}}
"""
    try:
        result = _call_zhipu(prompt, temperature=0.7, max_tokens=800)
        # 解析 JSON
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        analysis = json.loads(result)
        # 确保四个字段都存在
        required = ['base', 'skills', 'quality', 'potential']
        for field in required:
            if field not in analysis:
                analysis[field] = f"暂无具体建议，请针对{field}加强学习。"
        return analysis
    except Exception as e:
        print(f"大模型生成差距分析失败：{e}")
        # 降级方案：返回简单提示
        return {
            "base": "请根据岗位要求补充相关证书。",
            "skills": "建议针对缺失技能进行系统学习。",
            "quality": "可参加团队项目锻炼软能力。",
            "potential": "制定长期提升计划，逐步追赶岗位要求。"
        }

def compute_match(student_ability, job_ability):
    """
    计算学生与岗位的匹配度，并生成差距分析文本
    """
    # 技能相似度（Jaccard）
    if student_ability['skills'] and job_ability['skills']:
        skill_sim = len(student_ability['skills'] & job_ability['skills']) / len(student_ability['skills'] | job_ability['skills'])
    else:
        skill_sim = 0

    # 证书覆盖率
    if student_ability['certificates'] and job_ability['certificates']:
        cert_cov = len(student_ability['certificates'] & job_ability['certificates']) / len(job_ability['certificates'])
    else:
        cert_cov = 0

    # 软能力相似度（余弦）
    all_dims = set(student_ability['soft_abilities'].keys()) | set(job_ability['soft_abilities'].keys())
    if all_dims:
        stu_vec = [student_ability['soft_abilities'].get(d, {}).get('score', 0) for d in all_dims]
        job_vec = [job_ability['soft_abilities'].get(d, {}).get('score', 0) for d in all_dims]
        dot = sum(a*b for a,b in zip(stu_vec, job_vec))
        norm_stu = sum(a*a for a in stu_vec)**0.5
        norm_job = sum(b*b for b in job_vec)**0.5
        soft_sim = dot / (norm_stu * norm_job) if norm_stu and norm_job else 0
    else:
        soft_sim = 0

    # 综合得分（权重可调）
    total = 0.6 * skill_sim + 0.3 * soft_sim + 0.1 * cert_cov

    match_detail = {
        'overall_score': round(total * 100, 1),
        'skill_fit': round(skill_sim * 100, 1),
        'soft_gap': round((1 - soft_sim) * 100, 1),
        'cert_coverage': round(cert_cov * 100, 1)
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

    student_ability = get_student_ability(student_id)
    if not student_ability:
        return jsonify({'error': '学生不存在或无能力数据'}), 404

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT job_name FROM job_profile")
    jobs = [row['job_name'] for row in cursor.fetchall()]
    conn.close()

    results = []
    for job in jobs:
        job_ability = get_job_abilities(job)
        match_detail = compute_match(student_ability, job_ability)
        item = {'job_name': job, **match_detail}
        if 'interest' in student_ability:
            item['interest_scores'] = student_ability['interest']
        results.append(item)

    results.sort(key=lambda x: x['overall_score'], reverse=True)
    return jsonify(results[:limit])

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