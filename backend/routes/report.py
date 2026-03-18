from flask import Blueprint, request, jsonify, send_file
from db import get_db
import json
import time
import io
from services.llm_service import _call_zhipu
import markdown
from weasyprint import HTML

report_bp = Blueprint('report', __name__, url_prefix='/api/report')

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

def get_job_profile(job_name):
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

def generate_report_content(student_ability, job_profile, job_name, path_suggestions):
    # 计算差集
    need_skills = set(job_profile['skills']) - set(student_ability['skills'])
    need_certs = set(job_profile['certificates']) - set(student_ability['certificates'])
    soft_gaps = []
    for dim, job_val in job_profile['soft_abilities'].items():
        stu_val = student_ability['soft_abilities'].get(dim, {}).get('score', 0)
        if job_val.get('score', 0) > stu_val + 1:
            soft_gaps.append(dim)

    md = f"""# 职业生涯发展报告

## 1. 自我认知总结
您的教育背景：{student_ability.get('education', '无')}  
实习/工作经历：{student_ability.get('experience', '无')}  
核心技能：{', '.join(student_ability['skills'])}  
证书：{', '.join(student_ability['certificates'])}  

## 2. 人岗匹配分析
目标岗位：**{job_name}**

- **技能匹配度**：需补充技能 {len(need_skills)} 项：{', '.join(need_skills) if need_skills else '无'}
- **证书匹配度**：建议考取证书：{', '.join(need_certs) if need_certs else '无需额外证书'}
- **软能力差距**：需提升 {', '.join(soft_gaps) if soft_gaps else '无'}

## 3. 职业发展路径
### 晋升路径
"""
    if path_suggestions['promotions']:
        for p in path_suggestions['promotions']:
            md += f"- {p['from_job']} → {p['to_job']}：{p.get('description', '')}\n"
    else:
        md += "暂无明确的晋升路径建议。\n"

    md += "\n### 换岗路径\n"
    if path_suggestions['transitions']:
        for t in path_suggestions['transitions']:
            md += f"- {job_name} → {t['to_job']}：{t.get('description', '')}\n"
    else:
        md += "暂无换岗建议。\n"

    md += """
## 4. 分阶段行动计划
- **短期（0-6个月）**：深入学习目标岗位所需技能，补充证书，参与相关项目。
- **中期（6-12个月）**：积累实习或项目经验，提升软能力，考取中级证书。
- **长期（1-3年）**：向高级/专家岗位发展，拓展行业视野。

## 5. 评估与调整
建议每季度进行一次能力复盘，根据行业变化动态调整学习计划。
"""
    return md

@report_bp.route('/generate', methods=['POST'])
def generate():
    data = request.json
    student_id = data.get('student_id')
    job_name = data.get('job_name')  # 可选，如果不传则使用匹配度最高的岗位
    if not student_id:
        return jsonify({'error': '缺少 student_id'}), 400

    student_ability = get_student_ability(student_id)
    if not student_ability:
        return jsonify({'error': '学生不存在'}), 404

    # 如果未指定 job_name，自动选择匹配度最高的岗位
    if not job_name:
        from .match import get_student_ability as get_sa, get_job_abilities, compute_match
        # 获取所有岗位并计算匹配度
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT job_name FROM job_profile")
        jobs = [row['job_name'] for row in cursor.fetchall()]
        conn.close()
        best_job = None
        best_score = -1
        stu_ability_set = get_sa(student_id)  # 获取带set的版本用于匹配
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
    report_md = generate_report_content(student_ability, job_profile, job_name, path_suggestions)

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
    polished = _call_zhipu(prompt, temperature=0.5, max_tokens=2000)
    return jsonify({'polished': polished})

@report_bp.route('/export', methods=['POST'])
def export():
    data = request.json
    markdown_text = data.get('markdown')
    if not markdown_text:
        return jsonify({'error': '缺少markdown内容'}), 400

    html = markdown.markdown(markdown_text, extensions=['extra', 'codehilite'])
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Microsoft Yahei', sans-serif; line-height: 1.6; padding: 20px; }}
            h1 {{ color: #2563eb; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
            h2 {{ color: #1e293b; margin-top: 30px; }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    pdf = HTML(string=full_html).write_pdf()
    return send_file(
        io.BytesIO(pdf),
        download_name='career_report.pdf',
        as_attachment=True,
        mimetype='application/pdf'
    )

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