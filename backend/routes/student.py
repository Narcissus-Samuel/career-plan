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
    """上传并解析简历（当前模拟解析）"""
    if 'file' not in request.files:
        return jsonify({"error": "没有上传文件"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # ========== 模拟解析结果 ==========
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
    # ========== 模拟结束 ==========

    os.remove(file_path)
    return jsonify(mock_result)

@student_bp.route('/student', methods=['POST'])
def save_student():
    """将学生信息保存到数据库"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student (name, major, grade, skills, certificates, internships, interests, completeness, competitiveness)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
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


@student_bp.route('/students', methods=['GET'])
def get_students():
    """返回所有学生信息"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student")
    rows = cursor.fetchall()
    students = [dict(row) for row in rows]
    conn.close()
    return jsonify({"total": len(students), "data": students})