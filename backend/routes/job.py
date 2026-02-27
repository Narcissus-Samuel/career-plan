# 岗位相关路由（列表、画像、图谱)
# routes/job.py
from flask import Blueprint, request, jsonify
from db import get_db
import json

job_bp = Blueprint('job', __name__, url_prefix='/api')

@job_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """从数据库获取岗位列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job")
    rows = cursor.fetchall()
    jobs = [dict(row) for row in rows]
    conn.close()
    return jsonify({"total": len(jobs), "data": jobs})

@job_bp.route('/job/<name>/profile', methods=['GET'])
def get_job_profile(name):
    """获取岗位画像，优先从数据库读取，没有则返回默认模拟数据"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT skills, certificates, soft_abilities FROM job_profile WHERE job_name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        # row contains TEXT columns; assume JSON stored if complex
        try:
            skills = json.loads(row['skills']) if row['skills'] else []
            certificates = json.loads(row['certificates']) if row['certificates'] else []
        except Exception:
            skills = row['skills']
            certificates = row['certificates']
        return jsonify({
            "jobName": name,
            "skills": skills,
            "certificates": certificates,
            "soft_abilities": row['soft_abilities'],
        })
    # fallback simulacrum
    mock_profiles = {
        "数据分析师": {
            "jobName": "数据分析师",
            "skills": ["Python", "SQL", "Excel", "Tableau"],
            "certificates": ["计算机二级", "CDA"],
            "soft_abilities": {"innovation": 85, "learning": 90, "pressure": 80, "communication": 85}
        },
        "前端开发工程师": {
            "jobName": "前端开发工程师",
            "skills": ["HTML/CSS", "JavaScript", "Vue", "React"],
            "certificates": ["计算机二级"],
            "soft_abilities": {"innovation": 80, "learning": 95, "pressure": 85, "communication": 75}
        }
    }
    profile = mock_profiles.get(name, mock_profiles["数据分析师"])
    return jsonify(profile)

@job_bp.route('/job/<name>/graph', methods=['GET'])
def get_job_graph(name):
    """获取岗位发展图谱（模拟数据）"""
    graphs = {
        "数据分析师": {
            "vertical": ["初级数据分析师", "中级数据分析师", "高级数据分析师", "数据分析主管"],
            "switch": ["大数据开发", "产品经理", "金融分析师"]
        },
        "前端开发工程师": {
            "vertical": ["初级前端", "中级前端", "高级前端", "前端架构师"],
            "switch": ["UI设计师", "全栈开发", "产品经理"]
        },
        "default": {
            "vertical": ["初级", "中级", "高级", "专家"],
            "switch": ["相关岗位1", "相关岗位2"]
        }
    }
    result = graphs.get(name, graphs["default"])
    return jsonify(result)