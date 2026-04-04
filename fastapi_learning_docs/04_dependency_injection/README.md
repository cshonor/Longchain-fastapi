# 04 — 依赖注入系统（Dependency injection）

**核心内容**：`Depends`、子依赖、路由级依赖、带 `yield` 的资源管理、可参数化依赖。  
**核心目标**：掌握 IOC/DI 用法，解耦路由与资源（DB、用户、配置）。

对照代码：`fastapi_app/dependencies/`、`db/session.py` 中 `get_db` 模式。

---

## 本章笔记

- [依赖注入简介（`Depends` 与共享逻辑）](./01_di_introduction.md)
- [依赖项类（`CommonQueryParams` 与 `Depends()`）](./02_di_class_dependency.md)
- [子依赖项（链式 `Depends` 与缓存）](./03_di_sub_dependencies.md)
- [Depends 入门 Demo（可直接跑）](./fastapi_depends_intro_demo.py)
- [类依赖 Demo（可直接跑）](./fastapi_dep_class_demo.py)
- [子依赖与 `use_cache` Demo（可直接跑）](./fastapi_dep_sub_deps_demo.py)
