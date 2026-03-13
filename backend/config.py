import os
from dotenv import load_dotenv

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite 数据库文件存放路径（会自动创建）
SQLITE_DB_PATH = os.path.join(BASE_DIR, 'instance', 'career.db')

# 文件上传临时目录
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MBa

# 加载 .env 文件中的变量
load_dotenv()

ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
if not ZHIPU_API_KEY:
    raise ValueError("请设置 ZHIPU_API_KEY 环境变量或在 .env 文件中配置")

# 阿里云 API Key（从环境变量读取）
ALIYUN_API_KEY = os.getenv('ALIYUN_API_KEY')
if not ALIYUN_API_KEY:
    raise ValueError("请设置 ALIYUN_API_KEY 环境变量或在 .env 文件中配置")