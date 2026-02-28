# routes/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db
import datetime
import random

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


def _get_user_by_identifier(identifier):
    """根据用户名或手机号查找用户"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? OR phone = ?", (identifier, identifier)
    )
    user = cursor.fetchone()
    conn.close()
    return user


@auth_bp.route('/send_code', methods=['POST'])
def send_code():
    """生成并保存短信验证码（模拟）"""
    data = request.json or {}
    phone = data.get('phone')
    if not phone:
        return jsonify({'error': 'phone required'}), 400

    code = f"{random.randint(0, 999999):06d}"
    expires = datetime.datetime.now() + datetime.timedelta(minutes=5)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO verification_codes (phone, code, expires_at) VALUES (?, ?, ?)",
        (phone, code, expires.isoformat())
    )
    conn.commit()
    conn.close()

    # 真实环境应当发送短信，此处返回给客户端以便调试
    print(f"verification code {code} saved for phone {phone}")
    return jsonify({'code': code})


@auth_bp.route('/register', methods=['POST'])
def register():
    """根据前端传来的用户名/手机号/密码/验证码创建新用户"""
    data = request.json or {}
    username = data.get('username')
    phone = data.get('phone')
    password = data.get('password')
    code = data.get('code')

    # 简单验证
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    # 验证码检查（如果有手机号）
    if phone and code:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT code, expires_at FROM verification_codes WHERE phone = ? ORDER BY id DESC LIMIT 1",
            (phone,)
        )
        row = cursor.fetchone()
        conn.close()
        if not row or row['code'] != code:
            return jsonify({'error': 'invalid code'}), 400
        try:
            exp = datetime.datetime.fromisoformat(row['expires_at'])
            if datetime.datetime.now() > exp:
                return jsonify({'error': 'code expired'}), 400
        except Exception:
            pass

    # 检查用户名或手机号是否已存在
    existing = _get_user_by_identifier(username) or (_get_user_by_identifier(phone) if phone else None)
    if existing:
        return jsonify({'error': 'user already exists'}), 400

    pw_hash = generate_password_hash(password)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, phone, password_hash) VALUES (?, ?, ?)",
        (username, phone, pw_hash)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': user_id, 'username': username})


@auth_bp.route('/login', methods=['POST'])
def login():
    """验证用户凭据并返回简单token"""
    data = request.json or {}
    identifier = data.get('username') or data.get('phone')
    password = data.get('password')
    if not identifier or not password:
        return jsonify({'error': 'credentials required'}), 400

    user = _get_user_by_identifier(identifier)
    if not user:
        return jsonify({'error': 'user not found'}), 404

    if not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'invalid credentials'}), 401

    # 生成简单 token（生产应使用 JWT 或 session）
    token = f"mock-token-{user['id']}"
    return jsonify({'token': token, 'user': {'id': user['id'], 'username': user['username'], 'role': user['role']}})


@auth_bp.route('/users', methods=['GET'])
def list_users():
    """列出所有用户（可用于管理员界面）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, phone, role, is_active, created_at FROM users")
    rows = cursor.fetchall()
    conn.close()
    users = [dict(r) for r in rows]
    return jsonify({'total': len(users), 'users': users})


@auth_bp.route('/users/<int:user_id>/role', methods=['PUT'])
def change_role(user_id):
    """修改用户角色，例如 'user' -> 'admin'"""
    data = request.json or {}
    new_role = data.get('role')
    if new_role not in ('user', 'admin'):
        return jsonify({'error': 'invalid role'}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'id': user_id, 'role': new_role})
