# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import os
from db import get_db, init_db
from config import UPLOAD_FOLDER
from routes import register_blueprints

app = Flask(__name__)
CORS(app)

# 初始化数据库
with app.app_context():
    init_db()

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 注册所有蓝图（路由）
register_blueprints(app)

# 保留根路由和测试路由（方便直接验证）
@app.route('/')
def home():
    return jsonify({"message": "后端运行成功，使用 SQLite 数据库"})

@app.route('/test-db')
def test_db():
    try:
        conn = get_db()
        return jsonify({"status": "数据库连接成功", "db_path": str(conn)})
    except Exception as e:
        return jsonify({"status": "连接失败", "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)