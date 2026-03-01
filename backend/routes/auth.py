import io
import random
import string
import datetime
import time
from flask import Blueprint, request, jsonify, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
from captcha.image import ImageCaptcha  # 需要安装：pip install captcha
from db import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# 用于记录短信发送频率（简单内存存储，生产环境应使用Redis）
last_send_time = {}

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

# ---------- 图形验证码 ----------
@auth_bp.route('/captcha', methods=['GET'])
def get_captcha():
    """生成图形验证码图片"""
    # 生成4位随机字符（大写字母+数字）
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    # 存储到session
    session['captcha'] = captcha_text
    # 生成图片
    image = ImageCaptcha(width=120, height=40)
    data = image.generate(captcha_text)
    return Response(data.read(), mimetype='image/png')

# ---------- 短信验证码（模拟） ----------
@auth_bp.route('/send_code', methods=['POST'])
def send_code():
    """生成并保存短信验证码（模拟），需先验证图形验证码（可选，建议加）"""
    data = request.json or {}
    phone = data.get('phone')
    if not phone:
        return jsonify({'error': 'phone required'}), 400

    # 检查发送频率（60秒内只能发一次）
    now = time.time()
    if phone in last_send_time and now - last_send_time[phone] < 60:
        return jsonify({'error': '发送过于频繁，请稍后再试'}), 429
    last_send_time[phone] = now

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

    # 真实环境应当发送短信，此处只打印到控制台，并返回模拟码（调试用）
    print(f"验证码 {code} 已发送至手机 {phone}")
    return jsonify({'code': code, 'message': '验证码已发送'})  # 保留code便于调试

# ---------- 注册 ----------
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    phone = data.get('phone')
    password = data.get('password')
    sms_code = data.get('code')       # 短信验证码
    captcha_input = data.get('captcha')  # 图形验证码

    # 验证图形验证码
    if not captcha_input:
        return jsonify({'error': '请输入图形验证码'}), 400
    session_captcha = session.pop('captcha', None)  # 使用后立即删除
    if not session_captcha or session_captcha.lower() != captcha_input.lower():
        return jsonify({'error': '图形验证码错误'}), 400

    # 基础验证
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    if phone and not sms_code:
        return jsonify({'error': '短信验证码不能为空'}), 400

    # 检查用户名或手机号是否已存在
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? OR phone = ?",
        (username, phone if phone else '')
    )
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return jsonify({'error': '用户名或手机号已被注册'}), 400

    # 验证短信验证码（如果提供了手机号）
    if phone and sms_code:
        cursor.execute(
            "SELECT code, expires_at FROM verification_codes WHERE phone = ? ORDER BY id DESC LIMIT 1",
            (phone,)
        )
        row = cursor.fetchone()
        if not row or row['code'] != sms_code:
            conn.close()
            return jsonify({'error': '短信验证码错误'}), 400
        try:
            exp = datetime.datetime.fromisoformat(row['expires_at'])
            if datetime.datetime.now() > exp:
                conn.close()
                return jsonify({'error': '短信验证码已过期'}), 400
        except Exception:
            pass
        # 验证成功后删除该短信验证码（防止重复使用）
        cursor.execute("DELETE FROM verification_codes WHERE phone = ? AND code = ?", (phone, sms_code))
        conn.commit()

    # 创建用户
    pw_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (username, phone, password_hash) VALUES (?, ?, ?)",
        (username, phone, pw_hash)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': user_id, 'username': username})

# ---------- 登录 ----------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    identifier = data.get('username') or data.get('phone')
    password = data.get('password')
    captcha_input = data.get('captcha')  # 图形验证码

    # 验证图形验证码
    if not captcha_input:
        return jsonify({'error': '请输入图形验证码'}), 400
    session_captcha = session.pop('captcha', None)
    if not session_captcha or session_captcha.lower() != captcha_input.lower():
        return jsonify({'error': '图形验证码错误'}), 400

    if not identifier or not password:
        return jsonify({'error': 'credentials required'}), 400

    user = _get_user_by_identifier(identifier)
    if not user:
        return jsonify({'error': 'user not found'}), 404

    if not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'invalid credentials'}), 401

    # 生成简单 token
    token = f"mock-token-{user['id']}"
    return jsonify({'token': token, 'user': {'id': user['id'], 'username': user['username'], 'role': user['role']}})

# ---------- 用户管理接口（原有，未修改）----------
@auth_bp.route('/users', methods=['GET'])
def list_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, phone, role, is_active, created_at FROM users")
    rows = cursor.fetchall()
    conn.close()
    users = [dict(r) for r in rows]
    return jsonify({'total': len(users), 'users': users})

@auth_bp.route('/users/<int:user_id>/role', methods=['PUT'])
def change_role(user_id):
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