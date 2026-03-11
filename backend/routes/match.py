# routes/match.py
from flask import Blueprint, request, jsonify
from db import get_db
from .auth import token_required
import json

match_bp = Blueprint('match', __name__, url_prefix='/api/match')

def calculate_match_score(student, job_profile):
    """简单的规则匹配算法（无需大模型）"""
    # 职业技能匹配
    student_skills = set(student.get('skills', []))
    job_skills = set(job_profile.get('skills', []))
    if job_skills:
        skill_match = len(student_skills & job_skills) / len(job_skills)
    else:
        skill_match = 1.0

    # 软能力匹配（假设软能力得分范围1-5）
    student_soft = student.get('soft_abilities', {})
    job_soft = job_profile.get('soft_abilities', {})
    total_soft = 0
    count = 0
    for ability, target in job_soft.items():
        student_score = student_soft.get(ability, 0)
        if target > 0:
            ratio = min(student_score / target, 1.0)
            total_soft += ratio
            count += 1
    soft_score = total_soft / count if count > 0 else 1.0

    # 证书匹配（简单加分）
    student_certs = set(student.get('certificates', []))
    job_certs = set(job_profile.get('certificates', []))
    cert_score = len(student_certs & job_certs) / len(job_certs) if job_certs else 1.0

    # 实习/项目加分（如果存在）
    potential_score = 0.5
    if student.get('internships'):
        potential_score += 0.3
    if student.get('projects'):
        potential_score += 0.2
    potential_score = min(potential_score, 1.0)

    # 综合权重
    weights = {'skill': 0.5, 'soft': 0.3, 'cert': 0.1, 'potential': 0.1}
    total = (skill_match * weights['skill'] +
             soft_score * weights['soft'] +
             cert_score * weights['cert'] +
             potential_score * weights['potential'])
    return round(total * 100, 2), {
        'skill': round(skill_match * 100, 2),
        'soft': round(soft_score * 100, 2),
        'cert': round(cert_score * 100, 2),
        'potential': round(potential_score * 100, 2)
    }

def generate_analysis(student, job_profile, match_result):
    """生成简单的文本分析"""
    advantages = []
    gaps = []
    suggestions = []

    student_skills = set(student.get('skills', []))
    job_skills = set(job_profile.get('skills', []))
    matched_skills = student_skills & job_skills
    missing_skills = job_skills - student_skills

    if matched_skills:
        advantages.append(f"掌握 {', '.join(matched_skills)} 等核心技能")
    if missing_skills:
        gaps.append(f"缺少 {', '.join(missing_skills)} 技能")
        suggestions.append(f"建议学习 {', '.join(missing_skills)}")

    student_soft = student.get('soft_abilities', {})
    job_soft = job_profile.get('soft_abilities', {})
    for ability, target in job_soft.items():
        cur = student_soft.get(ability, 0)
        if cur < target:
            gaps.append(f"{ability}能力不足（得分{cur}，目标{target}）")
            suggestions.append(f"通过培训或实践提升{ability}")

    if match_result['total'] >= 80:
        advice = "您的匹配度很高，可以积极投递该岗位。"
    elif match_result['total'] >= 60:
        advice = "匹配度良好，建议先弥补短板再投递。"
    else:
        advice = "匹配度较低，建议考虑其他岗位或制定系统提升计划。"

    return {
        'advantages': advantages,
        'gaps': gaps,
        'suggestions': suggestions,
        'advice': advice
    }

@match_bp.route('', methods=['POST'])
@token_required
def match():
    user = request.user
    data = request.json
    job_name = data.get('job_name')
    if not job_name:
        return jsonify({'error': '请提供目标岗位名称'}), 400

    conn = get_db()
    cursor = conn.cursor()

    # 获取学生能力画像（假设student表已有数据）
    cursor.execute('''
        SELECT skills, certificates, internships, projects, soft_abilities
        FROM student WHERE user_id = ?
    ''', (user['id'],))
    student_row = cursor.fetchone()
    if not student_row:
        conn.close()
        return jsonify({'error': '请先完善学生信息'}), 404

    student = {
        'skills': json.loads(student_row['skills']) if student_row['skills'] else [],
        'certificates': json.loads(student_row['certificates']) if student_row['certificates'] else [],
        'internships': student_row['internships'],
        'projects': student_row['projects'],
        'soft_abilities': json.loads(student_row['soft_abilities']) if student_row['soft_abilities'] else {}
    }

    # 获取目标岗位的大类画像
    cursor.execute('''
        SELECT jc.skills, jc.certificates, jc.soft_abilities
        FROM job j
        LEFT JOIN job_categories jc ON j.category_id = jc.id
        WHERE j.job_name = ?
    ''', (job_name,))
    job_row = cursor.fetchone()
    conn.close()

    if not job_row:
        return jsonify({'error': '岗位不存在'}), 404

    job_profile = {
        'skills': json.loads(job_row['skills']) if job_row['skills'] else [],
        'certificates': json.loads(job_row['certificates']) if job_row['certificates'] else [],
        'soft_abilities': json.loads(job_row['soft_abilities']) if job_row['soft_abilities'] else {}
    }

    # 计算匹配度
    total, dimensions = calculate_match_score(student, job_profile)
    analysis = generate_analysis(student, job_profile, {'total': total})

    return jsonify({
        'job_name': job_name,
        'match_score': total,
        'dimensions': dimensions,
        'advantages': analysis['advantages'],
        'gaps': analysis['gaps'],
        'suggestions': analysis['suggestions'],
        'advice': analysis['advice']
    })