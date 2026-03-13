from werkzeug.security import generate_password_hash
from db import get_db

def create_admin(username='admin1', password='12345678'):
    conn = get_db()
    cursor = conn.cursor()
    # 检查是否已存在同名用户
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print(f"用户 {username} 已存在，请勿重复创建")
    else:
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, 'admin')
        )
        conn.commit()
        print(f"管理员 {username} 创建成功")
    conn.close()

if __name__ == '__main__':
    create_admin()