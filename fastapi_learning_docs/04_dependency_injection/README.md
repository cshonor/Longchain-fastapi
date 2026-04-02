# 04 — 依赖注入系统（Dependency injection）

**核心内容**：`Depends`、子依赖、路由级依赖、带 `yield` 的资源管理、可参数化依赖。  
**核心目标**：掌握 IOC/DI 用法，解耦路由与资源（DB、用户、配置）。

对照代码：`fastapi_app/dependencies/`、`db/session.py` 中 `get_db` 模式。
