# 岗位相关路由（列表、画像、图谱)
# routes/job.py
from flask import Blueprint, request, jsonify

job_bp = Blueprint('job', __name__, url_prefix='/api')

@job_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """获取岗位列表（模拟数据）"""
    mock_jobs = [
        {"jobName": "数据分析师", "company": "腾讯", "industry": "互联网", "salary": "20-35K"},
        {"jobName": "前端开发工程师", "company": "字节跳动", "industry": "互联网", "salary": "18-30K"},
        {"jobName": "产品经理", "company": "阿里巴巴", "industry": "互联网", "salary": "25-40K"},
        {"jobName": "Java开发工程师", "company": "美团", "industry": "互联网", "salary": "18-32K"},
        {"jobName": "UI设计师", "company": "网易", "industry": "互联网", "salary": "15-25K"},
        {"jobName": "测试开发工程师", "company": "百度", "industry": "互联网", "salary": "16-28K"},
        {"jobName": "运维工程师", "company": "京东", "industry": "互联网", "salary": "15-26K"},
        {"jobName": "大数据开发", "company": "快手", "industry": "互联网", "salary": "22-38K"},
    ]
    return jsonify({"total": len(mock_jobs), "data": mock_jobs})

@job_bp.route('/job/<name>/profile', methods=['GET'])
def get_job_profile(name):
    """获取岗位画像（模拟数据）"""
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