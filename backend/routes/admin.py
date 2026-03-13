from flask import Blueprint, request, jsonify
from db import get_db
from .auth import admin_required, verify_token
# 新增导入
from services.llm_service import (
    cluster_categories_with_zhipu,
    assign_categories_by_keywords,
    generate_category_profile_with_zhipu
)
from services.llm_service import rebuild_job_graph

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'credentials required'}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()
    if not user:
        return jsonify({'error': 'user not found'}), 404
    from werkzeug.security import check_password_hash
    if not check_password_hash(user['password_hash'], password) or user['role'] != 'admin':
        return jsonify({'error': 'invalid credentials or not admin'}), 401
    token = f"mock-token-{user['id']}"
    return jsonify({'token': token, 'user': {'id': user['id'], 'username': user['username']}})


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username, phone, role, is_active, created_at FROM users')
    rows = cur.fetchall()
    conn.close()
    users = [dict(r) for r in rows]
    return jsonify({'total': len(users), 'users': users})


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username, phone, role, is_active, created_at FROM users WHERE id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'not found'}), 404
    return jsonify(dict(row))


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    data = request.json or {}
    fields = []
    vals = []
    for k in ('username', 'phone', 'role', 'is_active'):
        if k in data:
            fields.append(f"{k} = ?")
            vals.append(data[k])
    if not fields:
        return jsonify({'error': 'no fields provided'}), 400
    vals.append(user_id)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", tuple(vals))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'deleted'})

# ========== 新增接口：自动聚类生成岗位大类 ==========
@admin_bp.route('/cluster-categories', methods=['POST'])
@admin_required
def cluster_categories():
    """
    第一步：调用大模型自动聚类，生成10-15个大类，并存入job_categories表。
    第二步：根据聚类结果，为所有岗位分配category_id（基于关键词匹配）。
    """
    data = request.get_json() or {}
    sample_size = data.get('sample_size', 500)  # 抽样数量，默认500

    # 1. 清空现有大类（确保完全基于大模型生成）
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM job_categories")
    conn.commit()
    conn.close()

    # 2. 调用大模型聚类
    categories = cluster_categories_with_zhipu(sample_size)
    if not categories:
        return jsonify({'error': '聚类失败，未获得有效结果'}), 500

    # 3. 将大类插入数据库
    conn = get_db()
    cursor = conn.cursor()
    category_job_titles_map = {}
    for cat in categories:
        cat_name = cat.get('category_name')
        job_titles = cat.get('job_titles', [])
        if not cat_name:
            continue
        cursor.execute("INSERT INTO job_categories (name) VALUES (?)", (cat_name,))
        conn.commit()
        cat_id = cursor.lastrowid
        category_job_titles_map[cat_name] = job_titles
    conn.close()

    # 4. 为岗位分配类别
    assigned_count = assign_categories_by_keywords(category_job_titles_map)

    return jsonify({
        'message': f'聚类完成，生成了 {len(categories)} 个大类，已为 {assigned_count} 个岗位分配类别',
        'categories': categories
    })

# ========== 新增接口：为所有大类生成通用画像 ==========
@admin_bp.route('/generate-all-category-profiles', methods=['POST'])
@admin_required
def generate_all_category_profiles():
    """为每个大类生成通用画像（技能、证书、软能力）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM job_categories")
    cat_ids = [row['id'] for row in cursor.fetchall()]
    conn.close()

    success = []
    for cat_id in cat_ids:
        if generate_category_profile_with_zhipu(cat_id):
            success.append(cat_id)

    return jsonify({
        'message': f'成功生成 {len(success)} 个大类画像',
        'success_ids': success
    })

@admin_bp.route('/build-job-graph', methods=['POST'])
@admin_required
def build_job_graph():
    """重建岗位图谱（垂直晋升+横向换岗）"""
    try:
        v_count, l_count = rebuild_job_graph()
        return jsonify({
            'success': True,
            'message': f'图谱重建完成，新增垂直路径 {v_count} 条，横向路径 {l_count} 条'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500