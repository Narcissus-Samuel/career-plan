# 初始化蓝图，导出所有蓝图
# routes/__init__.py
from .student import student_bp
from .job import job_bp
from .match import match_bp
from .report import report_bp
from .auth import auth_bp
from .content import content_bp   # 新增

def register_blueprints(app):
    app.register_blueprint(student_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(match_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)  # 新增