from flask import Blueprint, request, jsonify
from db import get_db
import json
import time

match_bp = Blueprint('match', __name__, url_prefix='/api/match')

def get_student_ability(student_id):
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
    # 获取最新兴趣测评结果（按创建时间倒序取第一条）
    cursor.execute('''
        SELECT dimension_scores FROM assessment_results
        WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
    ''', (student['user_id'],))
    interest_row = cursor.fetchone()
    conn.close()
    if interest_row:
        student['interest'] = json.loads(interest_row['dimension_scores'])
    else:
        student['interest'] = None
    return student

def get_job_abilities(job_name):
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

def compute_match(student_ability, job_ability):
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
    return {
        'overall_score': round(total * 100, 1),
        'skill_fit': round(skill_sim * 100, 1),
        'soft_gap': round((1 - soft_sim) * 100, 1),
        'cert_coverage': round(cert_cov * 100, 1)
    }

@match_bp.route('/recommend', methods=['GET'])
def recommend():
    student_id = request.args.get('student_id', type=int)
    limit = request.args.get('limit', 10, type=int)

    student_ability = get_student_ability(student_id)
    if not student_ability:
        return jsonify({'error': '学生不存在或无能力数据'}), 404

    # 获取所有有画像的岗位
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT job_name FROM job_profile")
    jobs = [row['job_name'] for row in cursor.fetchall()]
    conn.close()

    results = []
    for job in jobs:
        job_ability = get_job_abilities(job)
        match_detail = compute_match(student_ability, job_ability)
        results.append({'job_name': job, **match_detail})

    results.sort(key=lambda x: x['overall_score'], reverse=True)
    return jsonify(results[:limit])

@match_bp.route('/match', methods=['POST'])
def match():
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