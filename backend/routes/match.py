# routes/match.py
from flask import Blueprint, request, jsonify
import json
from db import get_db

match_bp = Blueprint('match', __name__, url_prefix='/api')

@match_bp.route('/match', methods=['GET'])
def get_match():
    """获取人岗匹配结果（模拟匹配结果，学生信息从数据库读取）"""
    student_id = request.args.get('studentId')
    if not student_id:
        return jsonify({"error": "缺少 studentId 参数"}), 400

    # 从数据库查询学生信息
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, major, grade, skills, certificates, internships
        FROM student
        WHERE id = ?
    ''', (student_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "学生不存在"}), 404

    # 解析 JSON 字段
    student_info = {
        "name": row['name'],
        "major": row['major'],
        "grade": row['grade'],
        "skills": json.loads(row['skills']) if row['skills'] else [],
        "certificates": json.loads(row['certificates']) if row['certificates'] else [],
        "internships": row['internships']
    }

    # TODO: 后续替换为成员3的真实匹配算法调用
    # from services.llm_service import match_jobs
    # matches = match_jobs(student_id)

    # 模拟匹配结果（格式与之前保持一致）
    mock_matches = [
        {
            "rank": 1,
            "jobName": "数据分析师",
            "matchScore": 0.85,
            "details": {"base": 0.9, "skill": 0.88, "quality": 0.8, "potential": 0.82}
        },
        {
            "rank": 2,
            "jobName": "前端开发工程师",
            "matchScore": 0.72,
            "details": {"base": 0.8, "skill": 0.75, "quality": 0.7, "potential": 0.68}
        },
        {
            "rank": 3,
            "jobName": "产品经理",
            "matchScore": 0.65,
            "details": {"base": 0.7, "skill": 0.6, "quality": 0.65, "potential": 0.7}
        },
        {
            "rank": 4,
            "jobName": "Java开发工程师",
            "matchScore": 0.58,
            "details": {"base": 0.68, "skill": 0.6, "quality": 0.55, "potential": 0.6}
        },
        {
            "rank": 5,
            "jobName": "UI设计师",
            "matchScore": 0.52,
            "details": {"base": 0.6, "skill": 0.5, "quality": 0.6, "potential": 0.55}
        }
    ]

    return jsonify({
        "studentInfo": student_info,
        "matches": mock_matches
    })