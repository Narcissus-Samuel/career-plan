# routes/student.py
from flask import Blueprint, request, jsonify
import os
import json
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER
from db import get_db

student_bp = Blueprint('student', __name__, url_prefix='/api')

@student_bp.route('/parse_resume', methods=['POST'])
def parse_resume():
    """上传并解析简历（当前为模拟数据，待集成真实解析函数）"""
    if 'file' not in request.files:
        return jsonify({"error": "没有上传文件"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # TODO: 后续替换为成员3的真实解析函数调用
    # from services.llm_service import parse_resume as real_parse
    # result = real_parse(file_path)

    # 模拟解析结果（保持与数据库字段一致）
    mock_result = {
        "name": "张三",
        "major": "计算机科学与技术",
        "grade": "大三",
        "skills": ["Python", "SQL", "Excel"],
        "certificates": ["CET-4", "计算机二级"],
        "internships": "某互联网公司数据分析实习（6个月）",
        "interests": ["数据分析", "产品经理"],
        "completeness": 85,
        "competitiveness": 78
    }

    os.remove(file_path)
    return jsonify(mock_result)

@student_bp.route('/student', methods=['POST'])
def save_student():
    """将学生信息保存到 SQLite 数据库"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    # allow optional user_id field
    cursor.execute('''
        INSERT INTO student (user_id, name, major, grade, skills, certificates, internships, interests, completeness, competitiveness)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('user_id'),
        data.get('name'),
        data.get('major'),
        data.get('grade'),
        json.dumps(data.get('skills', [])),
        json.dumps(data.get('certificates', [])),
        data.get('internships'),
        json.dumps(data.get('interests', [])),
        data.get('completeness'),
        data.get('competitiveness')
    ))
    conn.commit()
    student_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": student_id})