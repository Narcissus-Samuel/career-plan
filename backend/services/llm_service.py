# services/llm_service.py
def parse_resume(file_path):
    """等待成员3实现：解析简历文件，返回学生信息字典"""
    # 模拟返回
    return {
        "name": "李华",
        "major": "软件工程",
        "grade": "大四",
        "skills": ["Java", "Spring"],
        "certificates": ["CET-6"],
        "internships": "某科技公司实习",
        "interests": ["后端开发"],
        "completeness": 90,
        "competitiveness": 80
    }

def match_jobs(student_id):
    """等待成员3实现：根据学生ID计算匹配结果"""
    return [{"jobName": "Java开发工程师", "score": 0.9}]

def generate_report(student_id, job_name):
    """等待成员3实现：生成报告HTML"""
    return "<div>真实报告内容</div>"