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
    #让前端首页的 contentList 从数据库动态加载。
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        img_url TEXT,
        stage TEXT,
        type TEXT,
        category TEXT,               -- 分类：direction/template/case
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

    # ========== 新增：发展路径规划相关表 ==========
    # 用户扩展信息表（关联 users.id）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            name TEXT,
            gender TEXT,
            grade TEXT,
            major TEXT,
            target TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # 兴趣选项表（预定义）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            sort_order INTEGER DEFAULT 0
        )
    ''')

    # 用户兴趣关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interests (
            user_id INTEGER NOT NULL,
            interest_id INTEGER NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, interest_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (interest_id) REFERENCES interests(id) ON DELETE CASCADE
        )
    ''')

    # 能力维度表（预定义）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ability_dimensions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            code TEXT NOT NULL UNIQUE,
            sort_order INTEGER DEFAULT 0
        )
    ''')

    # 用户能力评估记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ability_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dimension_id INTEGER NOT NULL,
            score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (dimension_id) REFERENCES ability_dimensions(id) ON DELETE CASCADE
        )
    ''')

    # 用户规划主表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            target TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # 规划阶段表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plan_stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            period TEXT,
            status TEXT DEFAULT 'pending',
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plan_id) REFERENCES user_plans(id) ON DELETE CASCADE
        )
    ''')

    # 阶段目标表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plan_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stage_id) REFERENCES plan_stages(id) ON DELETE CASCADE
        )
    ''')

    # 阶段里程碑表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plan_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            date TEXT,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stage_id) REFERENCES plan_stages(id) ON DELETE CASCADE
        )
    ''')

    # 发展路径类型表（预定义模板）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS path_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            icon TEXT,
            name TEXT NOT NULL,
            description TEXT,
            color TEXT,
            progress INTEGER DEFAULT 0,
            create_time TEXT,
            target_time TEXT,
            core_goal TEXT,
            ability_base TEXT,
            challenges TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 路径阶段模板表（关联 path_types）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS path_stage_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            period TEXT,
            status TEXT DEFAULT 'pending',
            sort_order INTEGER DEFAULT 0,
            goals TEXT,       -- JSON数组，存储目标内容列表
            milestones TEXT,  -- JSON数组，存储里程碑对象 {name, date}
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (path_id) REFERENCES path_types(id) ON DELETE CASCADE
        )
    ''')

    # 学习资源表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            icon TEXT,
            color TEXT,
            title TEXT NOT NULL,
            description TEXT,
            duration TEXT,
            priority TEXT,
            link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 导师表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mentors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avatar TEXT,
            name TEXT NOT NULL,
            title TEXT,
            field TEXT,
            introduction TEXT,
            services TEXT,   -- JSON数组
            contact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 实践机会表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS practices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            color TEXT,
            title TEXT NOT NULL,
            description TEXT,
            requirements TEXT, -- JSON数组
            link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 报告记录表（区别于 report_history，用于存储生成的报告内容）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            type TEXT,
            format TEXT,
            content TEXT,      -- 报告内容（JSON或文本）
            file_path TEXT,    -- 生成的文件路径（可选）
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # ---------- 插入预定义数据 ----------
    # 兴趣选项
    cursor.execute("SELECT count(*) as cnt FROM interests")
    if cursor.fetchone()['cnt'] == 0:
        cursor.executemany('INSERT INTO interests (name, sort_order) VALUES (?, ?)', [
            ('技术研发', 1), ('产品设计', 2), ('市场营销', 3), ('运营管理', 4),
            ('教育培训', 5), ('金融投资', 6), ('行政办公', 7), ('创业管理', 8)
        ])

    # 能力维度
    cursor.execute("SELECT count(*) as cnt FROM ability_dimensions")
    if cursor.fetchone()['cnt'] == 0:
        cursor.executemany('INSERT INTO ability_dimensions (name, code, sort_order) VALUES (?, ?, ?)', [
            ('沟通能力', 'communication', 1),
            ('学习能力', 'learning', 2),
            ('团队协作', 'teamwork', 3),
            ('专业技能', 'professional', 4),
            ('创新能力', 'innovation', 5)
        ])

    conn.commit()
    conn.close()
    print("数据库初始化完成，文件位置：", SQLITE_DB_PATH)

    # 确保上传目录存在
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)