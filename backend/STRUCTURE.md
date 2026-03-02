# Backend 文件结构说明

此文档说明 `backend/` 下主要文件与目录含义，便于维护与演示。

- `app.py`：Flask 应用入口，负责注册蓝图与初始化数据库。
- `config.py`：配置项（例如 `SQLITE_DB_PATH`, `UPLOAD_FOLDER` 等）。
- `db.py`：封装 SQLite 连接与 `init_db()`，包含建表逻辑（读取 Excel 的自动导入逻辑）。
- `schema.sql`：完整建表 SQL 脚本，便于迁移或复现数据库。
- `models.py`：数据类（`dataclasses`）用于文档化实体结构（User/Student/Job/Report 等）。
- `algorithms.py`：职业匹配、推荐、评分算法实现（纯 Python，可单元测试）。
- `services/`：第三方服务封装，例如 `llm_service.py`（大模型调用与本地生成逻辑）。
- `routes/`：Flask 蓝图集合，负责 HTTP API：
  - `auth.py`：登录/注册、验证码、token 验证与权限装饰器。
  - `admin.py`：管理员登录与用户管理接口（受权限控制）。
  - `job.py`、`student.py`、`match.py`、`report.py`、`content.py`：项目已有业务路由。
  - `llm.py`：大模型相关 API（推荐、生成规划、QA）。
  - `assessment.py`：新增：测评提交与报告导出。
- `report_history`、`job_profile` 等为数据库表，由 `db.py` 初始化。

备注：当前实现使用轻量原生 sqlite3 与简单 token（`mock-token-<user_id>`），可扩展为 JWT 与 SQLAlchemy。
