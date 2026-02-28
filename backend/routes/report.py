# routes/report.py
from flask import Blueprint, request, jsonify, send_file
import io

report_bp = Blueprint('report', __name__, url_prefix='/api')

@report_bp.route('/report', methods=['POST'])
def generate_report():
    """生成职业规划报告（模拟HTML）"""
    data = request.json
    student_id = data.get('studentId')
    job_name = data.get('jobName')

    # TODO: 后续替换为成员3的真实报告生成函数
    # from services.llm_service import generate_report as real_generate
    # report_html = real_generate(student_id, job_name)

    report_html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
        <h1 style="color: #409EFF;">{job_name} 职业规划报告</h1>
        <p>亲爱的同学，根据你的能力和兴趣，我们为你量身定制了以下规划：</p>
        <h2>一、个人分析</h2>
        <p>你的专业技能扎实，具备良好的学习能力，但在软能力方面有待提升。</p>
        <h2>二、人岗匹配</h2>
        <p>与 {job_name} 的匹配度为 85%，主要优势在于技能匹配度高，建议补充实战经验。</p>
        <h2>三、发展建议</h2>
        <ul>
            <li>短期（3个月）：学习核心技能，完成一个相关项目。</li>
            <li>中期（1年）：积累实习经验，考取相关证书。</li>
            <li>长期（3年）：成为团队骨干，向专家方向发展。</li>
        </ul>
        <p style="color: #666;">本报告由AI生成，仅供参考。请结合自身情况调整。</p>
    </div>
    """
    return jsonify({"content": report_html})

@report_bp.route('/report/export', methods=['POST'])
def export_report():
    """导出报告文件（模拟Word/PPT）"""
    data = request.json
    format_type = data.get('format', 'word')
    content = data.get('content', '默认内容')

    file_data = io.BytesIO()
    file_data.write(content.encode('utf-8'))
    file_data.seek(0)

    return send_file(
        file_data,
        as_attachment=True,
        download_name=f"report.{format_type}",
        mimetype='application/octet-stream'
    )