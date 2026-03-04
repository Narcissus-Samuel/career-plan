# routes/path.py
from flask import Blueprint, request, jsonify
from db import get_db
from .auth import token_required
import json

path_bp = Blueprint('path', __name__, url_prefix='/api/path')

# ---------- 获取所有路径类型 ----------
@path_bp.route('/types', methods=['GET'])
def get_path_types():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, icon, name, description, color, progress,
               create_time, target_time, core_goal, ability_base, challenges
        FROM path_types
        ORDER BY id
    ''')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ---------- 获取指定路径的详细阶段（模板） ----------
@path_bp.route('/types/<int:path_id>/stages', methods=['GET'])
def get_path_stages(path_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, period, status, goals, milestones
        FROM path_stage_templates
        WHERE path_id = ?
        ORDER BY sort_order
    ''', (path_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            'id': r['id'],
            'name': r['name'],
            'period': r['period'],
            'status': r['status'],
            'goals': json.loads(r['goals']) if r['goals'] else [],
            'milestones': json.loads(r['milestones']) if r['milestones'] else []
        })
    return jsonify(result)

# ---------- 获取学习资源列表 ----------
@path_bp.route('/learning-resources', methods=['GET'])
def get_learning_resources():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, icon, color, title, description, duration, priority, link FROM learning_resources ORDER BY priority')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ---------- 获取导师列表 ----------
@path_bp.route('/mentors', methods=['GET'])
def get_mentors():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, avatar, name, title, field, introduction, services, contact FROM mentors')
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        row_dict = dict(r)
        row_dict['services'] = json.loads(row_dict['services']) if row_dict['services'] else []
        result.append(row_dict)
    return jsonify(result)

# ---------- 获取实践机会列表 ----------
@path_bp.route('/practices', methods=['GET'])
def get_practices():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, type, color, title, description, requirements, link FROM practices')
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        row_dict = dict(r)
        row_dict['requirements'] = json.loads(row_dict['requirements']) if row_dict['requirements'] else []
        result.append(row_dict)
    return jsonify(result)

# ---------- 获取用户当前路径规划进度 ----------
@path_bp.route('/user-progress', methods=['GET'])
@token_required
def get_user_progress():
    user = request.user
    path_id = request.args.get('pathId', type=int)
    if not path_id:
        return jsonify({'error': '缺少pathId'}), 400

    conn = get_db()
    cursor = conn.cursor()
    # 这里需要根据你的业务逻辑设计：可能有一个user_path_progress表，存储用户对某个路径的进度
    # 目前简单返回一个空结构，需要你根据实际需求扩展
    # 例如：查询用户对该路径的阶段目标完成状态等
    conn.close()
    return jsonify({})

# ---------- 保存用户路径进度 ----------
@path_bp.route('/user-progress', methods=['POST'])
@token_required
def save_user_progress():
    user = request.user
    data = request.json
    # 根据前端传递的数据保存进度，需要设计相关表（如user_plan_stages, user_plan_goals等）
    # 此处留空，需根据具体业务实现
    return jsonify({'message': '保存成功'})