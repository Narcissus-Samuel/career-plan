# 项目整体结构说明

本项目为前后端分离的大学生职业规划系统，使用 Vue 3 + Vite 构建前端，Flask + SQLite 构建后端。

```
frontend/                # 前端代码
  index.html             # 入口html
  package.json           # npm依赖与脚本
  vite.config.js
  src/
    main.js              # Vue应用入口
    app.vue              # 顶层组件
    style.css            # 全局样式
    router/              # 路由定义
      index.js
    views/               # 所有页面视图组件
      Home.vue
      Login.vue
      Register.vue
      AdminLogin.vue
      AdminDashboard.vue
      StudentInfo.vue
      MatchResult.vue
      Report.vue
      JobPortrait.vue
      AbilityAssessment.vue
      CareerPlanning.vue
      ReportGenerate.vue
      ResourceLibrary.vue
      AboutUs.vue
      CareerInterestTest.vue
      AbilityAnalysis.vue
      DevelopmentPath.vue
      ReportExport.vue
      ...                # 其他页面多数为功能占位或完整表单

backend/                 # 后端代码
  app.py                 # Flask 应用入口
  config.py
  db.py                  # SQLite工具与初始化
  schema.sql             # 建表脚本
  models.py              # dataclass实体定义
  algorithms.py          # 职业匹配/推荐算法
  requirements.txt       # Python依赖
  STRUCTURE.md           # 后端结构说明
  routes/                # 蓝图（路由）
    auth.py              # 登录/注册/权限
    admin.py             # 管理员接口
    job.py
    student.py
    match.py
    report.py            # 报告生成与导出
    content.py
    llm.py               # 大模型相关接口
    assessment.py        # 测评提交与导出
  services/              # 服务封装
    llm_service.py       # 大模型与实用功能

.gitignore
README.md                # 项目总说明（可自行添加）
```

说明：
- 后端使用原生 sqlite3，采用 `db.init_db()` 动态创建表并支持 Excel 导入。
- 前端页面均使用 Element Plus / 原生组件实现 UI，部分页面使用 Canvas 绘图。
- 通过 `axios` 实现前端与后端的数据交互，授权使用简单 Bearer token `mock-token-<id>`。
- 大模型模块支持通过 deepseek API 调用，或本地模板回复。

```
```
