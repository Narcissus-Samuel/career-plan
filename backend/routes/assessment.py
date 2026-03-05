from flask import Blueprint, request, jsonify, send_file
import io, json, datetime
from db import get_db
from services import llm_service
from backend.algorithms import score_student_competitiveness
from report_utils import export_report_file

assessment_bp = Blueprint('assessment', __name__, url_prefix='/api/assessment')


@assessment_bp.route('/submit', methods=['POST'])
def submit_assessment():
    """接收测评答案，计算维度分、生成报告并保存历史记录"""
    data = request.json or {}
    user_id = data.get('user_id')
    answers = data.get('answers')  # list of {id, dimension, score}
    if not answers:
        return jsonify({'error': 'answers required'}), 400

    # 计算维度分
    dimension_scores = {}
    for a in answers:
        dim = a.get('dimension')
        score = int(a.get('score') or 0)
        dimension_scores[dim] = dimension_scores.get(dim, 0) + score

    # 计算综合竞争力得分
    student_snapshot = {
        'user_id': user_id,
        'skills': [],
        'certificates': [],
        'internships': None,
        'completeness': int(sum([int(a.get('score') or 0) for a in answers]) / (len(answers) * 5.0) * 100),
    }
    competitiveness = score_student_competitiveness(student_snapshot)
    student_snapshot['competitiveness'] = competitiveness

    # 生成报告内容（HTML）
    # 使用 llm_service 的文本生成接口
    # 以能力得分与建议为上下文，询问生成职业适配建议
    context = {
        'dimension_scores': dimension_scores,
        'competitiveness': competitiveness
    }
    report_html = llm_service.generate_plan_suggestion(student_snapshot, job_name='综合能力测评报告')

    # 保存到 report_history
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO report_history (student_id, job_name, content, format_type) VALUES (?, ?, ?, ?)',
                (user_id, '测评报告', report_html, 'html'))
    conn.commit()
    report_id = cur.lastrowid
    conn.close()

    return jsonify({'report_id': report_id, 'content': report_html, 'dimension_scores': dimension_scores, 'competitiveness': competitiveness})


@assessment_bp.route('/export/<int:report_id>', methods=['GET'])
def export_report(report_id):
    """导出历史报告：默认 HTML，若安装 pdfkit 且请求 ?format=pdf 则尝试生成 PDF"""
    fmt = (request.args.get('format') or 'html').lower()
    res = export_report_file(report_id, fmt)
    if res is None:
        return jsonify({'error': 'not found'}), 404
    return res
