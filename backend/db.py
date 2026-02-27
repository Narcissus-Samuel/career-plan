import sqlite3
import os
from config import SQLITE_DB_PATH, UPLOAD_FOLDER

def get_db():
    """获取 SQLite 数据库连接，并设置 row_factory 为 Row 类型（支持列名访问）"""
    # 确保数据库文件的目录存在
    db_dir = os.path.dirname(SQLITE_DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row  # 这样查询结果可以通过列名访问，如 row['name']
    return conn

def init_db():
    """初始化数据库表结构（如果表不存在则创建）"""
    conn = get_db()
    cursor = conn.cursor()

    # 创建岗位表（字段根据官方数据定义）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,
            company TEXT,
            industry TEXT,
            salary_range TEXT,
            job_description TEXT,
            company_info TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建学生表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            major TEXT,
            grade TEXT,
            skills TEXT,          -- 存储 JSON 字符串，如 ["Python","SQL"]
            certificates TEXT,     -- 存储 JSON 字符串
            internships TEXT,
            interests TEXT,        -- 存储 JSON 字符串
            completeness INTEGER,  -- 完整度评分
            competitiveness INTEGER, -- 竞争力评分
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建岗位画像表（用于存储大模型生成的岗位画像）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT UNIQUE,
            skills TEXT,           -- JSON 数组
            certificates TEXT,      -- JSON 数组
            soft_abilities TEXT,    -- JSON 对象，如 {"innovation":85,"learning":90}
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建匹配结果表（可选）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            job_name TEXT,
            match_score REAL,
            details TEXT,           -- JSON 对象，存储各维度得分
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("数据库初始化完成，文件位置：", SQLITE_DB_PATH)

    # 确保上传目录存在
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)