# routes/profile.py
from flask import Blueprint, request, jsonify
from db import get_db
from .auth import token_required  # 引入认证装饰器
import json

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')

# ---------- 获取用户基础信息 ----------
@profile_bp.route('/base', methods=['GET'])
@token_required
def get_base_info():
    user = request.user
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, gender, grade, major, target
        FROM user_profiles WHERE user_id = ?
    ''', (user['id'],))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    else:
        return jsonify({})  # 返回空对象，前端自行处理默认值

# ---------- 保存/更新用户基础信息 ----------
@profile_bp.route('/base', methods=['POST'])
@token_required
def save_base_info():
    user = request.user
    data = request.json
    name = data.get('name')
    gender = data.get('gender')
    grade = data.get('grade')
    major = data.get('major')
    target = data.get('target')

    conn = get_db()
    cursor = conn.cursor()
    # 使用 INSERT OR REPLACE 或先检查再更新
    cursor.execute('''
        INSERT INTO user_profiles (user_id, name, gender, grade, major, target)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name=excluded.name,
            gender=excluded.gender,
            grade=excluded.grade,
            major=excluded.major,
            target=excluded.target,
            updated_at=CURRENT_TIMESTAMP
    ''', (user['id'], name, gender, grade, major, target))
    conn.commit()
    conn.close()
    return jsonify({'message': '保存成功'})

# ---------- 获取兴趣列表（预定义） ----------
@profile_bp.route('/interests', methods=['GET'])
def get_interests():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM interests ORDER BY sort_order')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ---------- 获取用户选择的兴趣 ----------
@profile_bp.route('/user-interests', methods=['GET'])
@token_required
def get_user_interests():
    user = request.user
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.id, i.name, ui.description
        FROM user_interests ui
        JOIN interests i ON ui.interest_id = i.id
        WHERE ui.user_id = ?
    ''', (user['id'],))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ---------- 保存用户选择的兴趣 ----------
@profile_bp.route('/user-interests', methods=['POST'])
@token_required
def save_user_interests():
    user = request.user
    data = request.json
    interests = data.get('interests', [])  # 格式：[{id: 1, description: 'xxx'}, ...]
    description = data.get('interestDesc', '')

    conn = get_db()
    cursor = conn.cursor()
    # 先删除旧记录
    cursor.execute('DELETE FROM user_interests WHERE user_id = ?', (user['id'],))
    # 插入新记录
    for item in interests:
        cursor.execute('''
            INSERT INTO user_interests (user_id, interest_id, description)
            VALUES (?, ?, ?)
        ''', (user['id'], item['id'], description))
    conn.commit()
    conn.close()
    return jsonify({'message': '保存成功'})

# ---------- 获取能力维度列表 ----------
@profile_bp.route('/ability-dimensions', methods=['GET'])
def get_ability_dimensions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, code FROM ability_dimensions ORDER BY sort_order')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ---------- 获取用户能力评估 ----------
@profile_bp.route('/ability', methods=['GET'])
@token_required
def get_ability():
    user = request.user
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ad.id, ad.name, ad.code, aa.score, aa.description
        FROM ability_assessments aa
        JOIN ability_dimensions ad ON aa.dimension_id = ad.id
        WHERE aa.user_id = ?
        ORDER BY ad.sort_order
    ''', (user['id'],))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ---------- 保存用户能力评估 ----------
@profile_bp.route('/ability', methods=['POST'])
@token_required
def save_ability():
    user = request.user
    data = request.json
    abilities = data.get('abilities', [])  # 格式：[{code: 'communication', score: 4, description: 'xxx'}]
    description = data.get('abilityDesc', '')

    conn = get_db()
    cursor = conn.cursor()
    # 删除旧记录
    cursor.execute('DELETE FROM ability_assessments WHERE user_id = ?', (user['id'],))
    # 插入新记录
    for item in abilities:
        # 根据code获取dimension_id
        cursor.execute('SELECT id FROM ability_dimensions WHERE code = ?', (item['code'],))
        dim = cursor.fetchone()
        if dim:
            cursor.execute('''
                INSERT INTO ability_assessments (user_id, dimension_id, score, description)
                VALUES (?, ?, ?, ?)
            ''', (user['id'], dim['id'], item['score'], description))
    conn.commit()
    conn.close()
    return jsonify({'message': '保存成功'})