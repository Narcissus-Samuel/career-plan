import os
import time
import json
import tempfile
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from db import get_db
from services.llm_service import _call_zhipu
import pdfplumber
from docx import Document

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

@profile_bp.route('/submit', methods=['POST'])
def submit_profile():
    """提交手动填写的表单数据（包括个人信息和简历文本）"""
    data = request.json
    user_id = data.get('user_id')
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    education = data.get('education', '')
    work = data.get('work', '')
    project = data.get('project', '')
    skills_certs = data.get('skills_certs', '')
    summary = data.get('summary', '')

    if not all([name, phone, email]):
        return jsonify({'error': '姓名、手机、邮箱为必填项'}), 400

    # 拼接文本供大模型提取能力
    full_text = f"""
教育经历：{education}
工作经历：{work}
项目经历：{project}
技能与证书：{skills_certs}
自我总结：{summary}
    """.strip()

    prompt = f"""
请从以下用户输入的文本中提取能力信息，返回严格的JSON格式：
- skills：技能列表（字符串数组）
- certificates：证书列表（字符串数组）
- soft_abilities：软能力评分对象，键为软能力名称，值为包含score（1-5分）和description的对象
- education：教育经历（简要字符串，可选）
- experience：工作/实习经历（简要字符串，可选）

用户文本：
{full_text}

只返回JSON，不要其他文字。
"""
    result = _call_zhipu(prompt, temperature=0.3, max_tokens=2000)
    try:
        ability = json.loads(result)
    except:
        return jsonify({'error': 'AI解析失败', 'raw': result}), 500

    # 计算简历完整度（简单根据填写项）
    completeness = 0
    total = 5
    if education: completeness += 1
    if work: completeness += 1
    if project: completeness += 1
    if skills_certs: completeness += 1
    if summary: completeness += 1
    completeness = round((completeness / total) * 100)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student (
            user_id, name, phone, email,
            education_text, work_text, project_text, skills_certs_text, summary,
            skills, certificates, soft_abilities,
            completeness, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, name, phone, email,
        education, work, project, skills_certs, summary,
        json.dumps(ability.get('skills', []), ensure_ascii=False),
        json.dumps(ability.get('certificates', []), ensure_ascii=False),
        json.dumps(ability.get('soft_abilities', {}), ensure_ascii=False),
        completeness,
        int(time.time())
    ))
    student_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'student_id': student_id,
        'completeness': completeness,
        'skills': ability.get('skills', []),
        'certificates': ability.get('certificates', []),
        'soft_abilities': ability.get('soft_abilities', {})
    })

@profile_bp.route('/upload', methods=['POST'])
def upload_resume():
    """上传简历文件（PDF/Word）"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    file = request.files['file']
    user_id = request.form.get('user_id', type=int)

    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型，仅支持 PDF、Word 文档'}), 400

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': '文件大小不能超过 10MB'}), 400

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext == 'pdf':
            text = extract_text_from_pdf(tmp_path)
        elif ext in ('doc', 'docx'):
            text = extract_text_from_docx(tmp_path)
        else:
            text = ""
    except Exception as e:
        os.unlink(tmp_path)
        return jsonify({'error': f'文件解析失败：{str(e)}'}), 500

    os.unlink(tmp_path)

    if not text.strip():
        return jsonify({'error': '无法从文件中提取文本内容'}), 400

    prompt = f"""
请从以下简历文本中提取能力信息，返回严格的JSON格式：
- skills：技能列表（字符串数组）
- certificates：证书列表（字符串数组）
- soft_abilities：软能力评分对象，键为软能力名称，值为包含score（1-5分）和description的对象
- education：教育经历（简要字符串）
- experience：工作/实习经历（简要字符串）

简历文本：
{text}

只返回JSON，不要其他文字。
"""
    result = _call_zhipu(prompt, temperature=0.3, max_tokens=2000)
    try:
        ability = json.loads(result)
    except:
        return jsonify({'error': 'AI解析失败', 'raw': result}), 500

    # 存储到数据库（无个人信息，暂时置空）
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student (
            user_id, name, phone, email,
            education_text, work_text, skills, certificates, soft_abilities,
            completeness, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, '', '', '',
        ability.get('education', ''), ability.get('experience', ''),
        json.dumps(ability.get('skills', []), ensure_ascii=False),
        json.dumps(ability.get('certificates', []), ensure_ascii=False),
        json.dumps(ability.get('soft_abilities', {}), ensure_ascii=False),
        50,  # 默认完整度，可后续更新
        int(time.time())
    ))
    student_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'student_id': student_id,
        'skills': ability.get('skills', []),
        'certificates': ability.get('certificates', []),
        'soft_abilities': ability.get('soft_abilities', {}),
        'raw_text_preview': text[:500] + ('...' if len(text) > 500 else '')
    })

@profile_bp.route('/<int:student_id>', methods=['GET'])
def get_profile(student_id):
    """获取学生能力画像"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, user_id, name, phone, email,
               education_text, work_text, project_text, skills_certs_text, summary,
               skills, certificates, soft_abilities, completeness, created_at
        FROM student WHERE id = ?
    ''', (student_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': '学生不存在'}), 404
    profile = dict(row)
    profile['skills'] = json.loads(profile['skills']) if profile['skills'] else []
    profile['certificates'] = json.loads(profile['certificates']) if profile['certificates'] else []
    profile['soft_abilities'] = json.loads(profile['soft_abilities']) if profile['soft_abilities'] else {}
    return jsonify(profile)