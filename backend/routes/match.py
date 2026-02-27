# 匹配结果路由
# routes/match.py
from flask import Blueprint, request, jsonify

match_bp = Blueprint('match', __name__, url_prefix='/api')

@match_bp.route('/match', methods=['GET'])
def get_match():
    """获取人岗匹配结果（模拟数据）"""
    student_id = request.args.get('studentId')
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
    student_info = {
        "name": "张三",
        "major": "计算机科学与技术",
        "grade": "大三",
        "skills": ["Python", "SQL"],
        "certificates": ["CET-4"],
        "internships": "某互联网公司实习"
    }
    return jsonify({"studentInfo": student_info, "matches": mock_matches})