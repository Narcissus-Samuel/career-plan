import os

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite 数据库文件存放路径（会自动创建）
SQLITE_DB_PATH = os.path.join(BASE_DIR, 'instance', 'career.db')

# 文件上传临时目录
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MBa