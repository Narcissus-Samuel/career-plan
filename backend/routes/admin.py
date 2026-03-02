from flask import Blueprint, request, jsonify
from db import get_db
from .auth import admin_required, verify_token

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
