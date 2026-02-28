# routes/job.py
from flask import Blueprint, jsonify
import json
from db import get_db

job_bp = Blueprint('job', __name__, url_prefix='/api')

@job_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """从数据库获取岗位列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT job_name, company, industry, salary_range
        FROM job
        ORDER BY job_name
    ''')
    rows = cursor.fetchall()
    jobs = []
    for row in rows:
        jobs.append({
            "jobName": row['job_name'],
            "company": row['company'],
            "industry": row['industry'],
            "salary": row['salary_range']
        })
    conn.close()
    return jsonify({"total": len(jobs), "data": jobs})

@job_bp.route('/job/<name>/profile', methods=['GET'])
def get_job_profile(name):
    """从 job_profile 表获取岗位画像"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT skills, certificates, soft_abilities
        FROM job_profile
        WHERE job_name = ?
    ''', (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        # 数据库中的 JSON 字段需要反序列化
        profile = {
            "jobName": name,
            "skills": json.loads(row['skills']) if row['skills'] else [],
            "certificates": json.loads(row['certificates']) if row['certificates'] else [],
            "soft_abilities": json.loads(row['soft_abilities']) if row['soft_abilities'] else {}
        }
    else:
        # 如果尚未生成画像，返回一个默认空结构（后续可由成员3补充）
        profile = {
            "jobName": name,
            "skills": [],
            "certificates": [],
            "soft_abilities": {
                "innovation": 0,
                "learning": 0,
                "pressure": 0,
                "communication": 0
            }
        }
    return jsonify(profile)

@job_bp.route('/job/<name>/graph', methods=['GET'])
def get_job_graph(name):
    """获取岗位发展图谱（暂用模拟，后续可从数据库扩展）"""
    # 可考虑在数据库中增加图谱表，当前返回模拟数据
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