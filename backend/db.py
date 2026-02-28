import sqlite3
import os
import re
from config import SQLITE_DB_PATH, UPLOAD_FOLDER

# 当 Excel 存在时需要 pandas
try:
    import pandas as pd
except ImportError:
    pd = None

COLUMN_ALIASES = {
    "岗位名称": "job_name",
    "地址": "location",
    "薪资范围": "salary_range",
    "公司名称": "company",
    "所属行业": "industry",
    "公司规模": "company_size",
    "公司类型": "company_type",
    "岗位编码": "job_code",
    "岗位详情": "job_description",
    "更新日期": "updated_at",
    "公司详情": "company_info",
    "岗位来源地址": "source_url",
}


def get_db():
    """获取 SQLite 数据库连接，并设置 row_factory 为 Row 类型（支持列名访问）"""
    # 确保数据库文件的目录存在
    db_dir = os.path.dirname(SQLITE_DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row  # 这样查询结果可以通过列名访问，如 row['name']
    return conn


def sanitize_columns(columns):
    """将列名转换为安全的 snake_case 名称"""
    new_cols = []
    for col in columns:
        if col in COLUMN_ALIASES:
            col = COLUMN_ALIASES[col]
        # 只保留字母数字和下划线
        col = re.sub(r"\W+", "_", col)
        col = col.strip(" _").lower()
        if not col:
            col = "col"
        new_cols.append(col)
    return new_cols


def init_db():
    """初始化数据库表结构（如果表不存在则创建）"""
    conn = get_db()
    cursor = conn.cursor()

    # 如果存在 Excel 文件（放在 backend 目录下），则根据它自动创建 job 表并导入数据
    base_dir = os.path.dirname(__file__)
    # 相对路径文件名，可修改或通过配置提供
    excel_filename = '20260226105856_457.xls'
    excel_path = os.path.join(base_dir, excel_filename)
    if pd is not None and os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        # 重命名列并清理名称
        sanitized = sanitize_columns(df.columns.tolist())
        df.columns = sanitized

        # 选择主键：优先 job_code，然后任意唯一列
        pk = None
        if 'job_code' in df.columns:
            pk = 'job_code'
        else:
            for col in df.columns:
                if df[col].is_unique:
                    pk = col
                    break

        # 构造 CREATE TABLE 语句
        col_defs = []
        if pk is None:
            col_defs.append('id INTEGER PRIMARY KEY AUTOINCREMENT')
        for col in df.columns:
            # infer sqlite type
            dtype = str(df[col].dtype)
            if 'int' in dtype:
                typ = 'INTEGER'
            elif 'float' in dtype:
                typ = 'REAL'
            else:
                typ = 'TEXT'
            if col == pk:
                col_defs.append(f"{col} {typ} PRIMARY KEY")
            else:
                col_defs.append(f"{col} {typ}")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS job ({', '.join(col_defs)})")

        # 插入数据
        for _, row in df.iterrows():
            values = [None if pd.isna(x) else x for x in row.tolist()]
            cols = df.columns.tolist()
            placeholders = ','.join('?' for _ in values)
            cursor.execute(
                f"INSERT OR IGNORE INTO job ({','.join(cols)}) VALUES ({placeholders})",
                values,
            )
        conn.commit()
    else:
        # 原来手写的表结构，保留为备用
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

    # 创建学生表（可关联到 users 表）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,      -- 如果用户登录，可保存对应ID
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
    # 如果表已经存在但旧版本没有 user_id 字段，尝试添加
    cursor.execute("PRAGMA table_info(student)")
    cols = [row['name'] for row in cursor.fetchall()]
    if 'user_id' not in cols:
        cursor.execute("ALTER TABLE student ADD COLUMN user_id INTEGER")

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

    # 创建匹配结果表
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

    # 创建报告历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS report_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            job_name TEXT,
            content TEXT,
            format_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 新增：创建用户/管理员、验证码等相关表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',        -- user/admin
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 存储短信验证码或注册验证码，后续可以用于验证
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            code TEXT,
            expires_at TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("数据库初始化完成，文件位置：", SQLITE_DB_PATH)

    # 确保上传目录存在
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
