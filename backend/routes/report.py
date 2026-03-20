from flask import Blueprint, request, jsonify, send_file
from db import get_db
import json
import time
import io
import subprocess
import tempfile
import os
import logging
# 显式导入，方便测试时通过模块名拦截
from services.llm_service import call_llm
import markdown

report_bp = Blueprint('report', __name__, url_prefix='/api/report')

# 配置 weasyprint 可执行文件路径（请根据实际位置修改）
WEASYPRINT_PATH = r'D:\caogao2\tools\weasyprint-windows\dist\weasyprint.exe'

if not os.path.exists(WEASYPRINT_PATH):
    logging.warning(f"WeasyPrint executable not found at {WEASYPRINT_PATH}. PDF export will fail.")

def get_student_ability(student_id):
    """获取学生能力画像，包括兴趣和结构化履历"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT skills, certificates, soft_abilities, education_text, work_text, project_text,
               education_json, work_json, project_json, user_id
        FROM student WHERE id = ?
    ''', (student_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    student = {
        'skills': json.loads(row['skills']) if row['skills'] else [],
        'certificates': json.loads(row['certificates']) if row['certificates'] else [],
        'soft_abilities': json.loads(row['soft_abilities']) if row['soft_abilities'] else {},
        'education': row['education_text'],
        'experience': row['work_text'],
        'project': row['project_text'],
        'education_json': json.loads(row['education_json']) if row['education_json'] else {},
        'work_json': json.loads(row['work_json']) if row['work_json'] else [],
        'project_json': json.loads(row['project_json']) if row['project_json'] else [],
        'user_id': row['user_id']
    }
    if student['user_id']:
        cursor.execute('''
            SELECT dimension_scores FROM assessment_results
            WHERE user_id = ? ORDER BY id DESC LIMIT 1
        ''', (student['user_id'],))
        interest_row = cursor.fetchone()
        if interest_row:
            student['interest'] = json.loads(interest_row['dimension_scores'])
    conn.close()
    return student

def get_job_profile(job_name):
    """获取岗位画像"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT skills, certificates, soft_abilities FROM job_profile WHERE job_name = ?', (job_name,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        'skills': json.loads(row['skills']) if row['skills'] else [],
        'certificates': json.loads(row['certificates']) if row['certificates'] else [],
        'soft_abilities': json.loads(row['soft_abilities']) if row['soft_abilities'] else {}
    }

def get_path_suggestions(job_name):
    """获取岗位图谱建议"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT to_job, relation_type, description FROM job_relations
        WHERE from_job = ? AND relation_type = 'promotion'
    ''', (job_name,))
    promotions = [dict(row) for row in cursor.fetchall()]
    cursor.execute('''
        SELECT to_job, description FROM job_relations
        WHERE from_job = ? AND relation_type = 'transition'
    ''', (job_name,))
    transitions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {'promotions': promotions, 'transitions': transitions}

def generate_report_with_llm(student_ability, job_profile, job_name, path_suggestions):
    """
    【正式实现】使用阿里云百炼大模型生成完整的职业生涯发展报告。
    此函数在生产环境中会真实消耗 API 额度。
    """
    # 构建上下文：将所有原始数据转换为 JSON 字符串
    context = {
        '学生信息': {
            '教育背景': student_ability.get('education', ''),
            '教育结构化': student_ability.get('education_json', {}),
            '实习/工作经历': student_ability.get('experience', ''),
            '工作结构化': student_ability.get('work_json', []),
            '项目经历': student_ability.get('project', ''),
            '项目结构化': student_ability.get('project_json', []),
            '技能列表': student_ability['skills'],
            '证书列表': student_ability['certificates'],
            '软能力评分': student_ability['soft_abilities'],
            '兴趣测评': student_ability.get('interest', {})
        },
        '目标岗位': {
            '名称': job_name,
            '技能要求': job_profile['skills'],
            '证书要求': job_profile['certificates'],
            '软能力要求': job_profile['soft_abilities']
        },
        '岗位图谱建议': {
            '晋升路径': path_suggestions['promotions'],
            '换岗路径': path_suggestions['transitions']
        }
    }
    context_json = json.dumps(context, ensure_ascii=False, indent=2)

    prompt = f"""你是一位专业的职业规划师。请根据以下提供的完整数据，生成一份详细的职业生涯发展报告。
报告应该包括：
- 自我认知总结（基于学生的教育、经历、技能、证书、软能力、兴趣）
- 人岗匹配分析（分析学生与目标岗位的匹配情况，包括优势、差距）
- 职业发展路径（结合岗位图谱建议，为学生规划可能的晋升和换岗方向）
- 分阶段行动计划（制定短期、中期、长期的具体学习与实践计划，必须针对学生的具体情况）
- 评估与调整建议

请确保报告内容个性化、具体，直接基于给定的数据，避免通用模板。使用 Markdown 格式，语气专业且鼓励。

以下是所有数据（JSON 格式）：
{context_json}

请开始生成报告。
"""
    try:
        # 【核心调用】此处走统一封装，可控模式（local/auto/real），并支持测试时热插拔
        result = call_llm(prompt, temperature=0.7, max_tokens=3000)
        
        if not result or not result.strip():
            logging.warning("LLM returned empty content, using fallback.")
            return "# 职业生涯发展报告\n\n抱歉，智能生成服务暂时返回空内容，请稍后重试。"
            
        return result.strip()
    except Exception as e:
        logging.error(f"大模型生成报告失败：{e}")
        # 降级返回简单提示，避免程序崩溃
        return "# 职业生涯发展报告\n\n报告生成服务暂时不可用（API 调用异常），请稍后再试。"

@report_bp.route('/generate', methods=['POST'])
def generate():
    data = request.json
    student_id = data.get('student_id')
    job_name = data.get('job_name')
    
    if not student_id:
        return jsonify({'error': '缺少 student_id'}), 400

    student_ability = get_student_ability(student_id)
    if not student_ability:
        return jsonify({'error': '学生不存在'}), 404

    # 如果没有指定岗位，自动匹配最佳岗位
    if not job_name:
        from .match import get_student_ability as get_sa, get_job_abilities, compute_match
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT job_name FROM job_profile")
        jobs = [row['job_name'] for row in cursor.fetchall()]
        conn.close()
        
        best_job = None
        best_score = -1
        stu_ability_set = get_sa(student_id)
        
        if not stu_ability_set:
            return jsonify({'error': '学生能力数据异常'}), 500
            
        for job in jobs:
            job_ability = get_job_abilities(job)
            match_detail = compute_match(stu_ability_set, job_ability)
            if match_detail['overall_score'] > best_score:
                best_score = match_detail['overall_score']
                best_job = job
        
        job_name = best_job
        if not job_name:
            return jsonify({'error': '没有可匹配的岗位'}), 404

    job_profile = get_job_profile(job_name)
    if not job_profile:
        return jsonify({'error': '岗位画像不存在'}), 404

    path_suggestions = get_path_suggestions(job_name)
    
    # 调用 LLM 生成报告 (真实调用或测试拦截)
    report_md = generate_report_with_llm(student_ability, job_profile, job_name, path_suggestions)

    # 存储报告到数据库
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO report_history (student_id, job_name, content, format_type, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        student_id,
        job_name,
        report_md,
        'markdown',
        int(time.time())
    ))
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'report_id': report_id, 'content': report_md})

@report_bp.route('/polish', methods=['POST'])
def polish():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({'error': '请输入文本'}), 400
    prompt = f"请润色以下文本，使其更专业流畅（保持原意）：\n{text}"
    polished = call_llm(prompt, temperature=0.5, max_tokens=2000)
    return jsonify({'polished': polished})

@report_bp.route('/export', methods=['POST'])
def export():
    data = request.json
    markdown_text = data.get('markdown')
    if not markdown_text:
        return jsonify({'error': '缺少markdown内容'}), 400

    html_content = markdown.markdown(markdown_text, extensions=['extra', 'codehilite'])
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Georgia', 'Times New Roman', serif; line-height: 1.6; color: #2c3e50; max-width: 800px; margin: 0 auto; padding: 40px 20px; background: #fff; }}
            h1 {{ color: #1a5f7a; border-bottom: 2px solid #1a5f7a; padding-bottom: 8px; }}
            h2 {{ color: #2c3e50; margin-top: 30px; }}
            h3 {{ color: #34495e; }}
            p {{ margin: 15px 0; }}
            ul {{ margin: 10px 0 10px 20px; }}
            li {{ margin: 5px 0; }}
            .footer {{ margin-top: 50px; text-align: center; color: #7f8c8d; font-size: 12px; }}
        </style>
    </head>
    <body>
        {html_content}
        <div class="footer">—— 大学生职业规划系统 · 智能生成 ——</div>
    </body>
    </html>
    """

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(styled_html)
        html_path = f.name

    pdf_path = html_path.replace('.html', '.pdf')

    try:
        subprocess.run([WEASYPRINT_PATH, html_path, pdf_path], check=True, capture_output=True, text=True)
        return send_file(
            pdf_path,
            download_name='career_report.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )
    except subprocess.CalledProcessError as e:
        print(f"WeasyPrint error: {e.stderr}")
        # 失败降级：返回 Markdown 文档
        md_bytes = markdown_text.encode('utf-8')
        return send_file(
            io.BytesIO(md_bytes),
            download_name='career_report.md',
            as_attachment=True,
            mimetype='text/markdown'
        )
    except FileNotFoundError:
        # weasyprint不存在时直接返回Markdown
        md_bytes = markdown_text.encode('utf-8')
        return send_file(
            io.BytesIO(md_bytes),
            download_name='career_report.md',
            as_attachment=True,
            mimetype='text/markdown'
        )
    finally:
        try:
            os.unlink(html_path)
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
        except Exception as e:
            print(f"清理临时文件失败: {e}")

@report_bp.route('/history/<int:student_id>', methods=['GET'])
def history(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, job_name, content, format_type, created_at
        FROM report_history
        WHERE student_id = ?
        ORDER BY created_at DESC
    ''', (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@report_bp.route('/<int:report_id>', methods=['GET'])
def get_report(report_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM report_history WHERE id = ?', (report_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': '报告不存在'}), 404
    return jsonify(dict(row))