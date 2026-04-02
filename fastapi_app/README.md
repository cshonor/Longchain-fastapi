# FastAPI 模块

本文档与 **`fastapi_app/`** 包同级：下面是 FastAPI 学习笔记与约定；可运行代码即本目录下的 Python 模块。仓库内请勿使用名为 `fastapi/` 的**顶层源码目录**：即使只有文档，也可能形成 namespace 包并遮蔽 PyPI 的 `fastapi`，导致无法 `from fastapi import FastAPI`。使用 `fastapi_app` 这类名称即可避免冲突。

- **生产级系统化学习路径（分阶段日程、章节拆解、执行建议）**：见 [LEARNING_GUIDE.md](./LEARNING_GUIDE.md)。
- **按模块分目录的笔记占位**：见 [`fastapi_learning_docs/README.md`](../fastapi_learning_docs/README.md)（`01_`…`07_` 与总表一致）。

下文按**主题速查**整理：从路由与 Pydantic 起步，再到依赖注入、数据层、安全与工程化，最后到部署。

---

## 1. 基础：路由、请求、响应

| 概念 | 要点 |
|------|------|
| **路由** | `@app.get/post/put/delete/patch`；路径参数 `{id}`；查询参数自动从函数参数解析 |
| **请求体** | `POST/PUT` 等用 Pydantic 模型或 `Body()`；表单用 `Form()`；文件用 `UploadFile` |
| **响应** | 返回 `dict`/Pydantic 模型/`Response` 子类；`response_model` 控制序列化与文档 |
| **状态码** | `status_code=` 或在路由里 `raise HTTPException` |

官方文档：[FastAPI — First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)、[Request Body](https://fastapi.tiangolo.com/tutorial/body/)。

---

## 2. Pydantic（数据校验，核心中的核心）

- **请求校验**：入参模型继承 `BaseModel`，字段类型 + `Field()`（默认值、约束、别名）。
- **响应裁剪**：`response_model` + `response_model_exclude_unset` 等，避免把内部字段泄露给客户端。
- **嵌套与复用**：小模型组合成大模型；共用 `shared` 层避免循环引用。
- **V2 习惯**：优先 `model_validate` / `model_dump`；配置用 `model_config = ConfigDict(...)`。

官方文档：[Pydantic 与 FastAPI](https://fastapi.tiangolo.com/tutorial/body-fields/)。

---

## 3. 依赖注入 `Depends`（IOC/DI，FastAPI 灵魂）

- **可测试**：数据库会话、当前用户、配置对象都通过 `Depends(get_xxx)` 注入，便于单测里 override。
- **层级**：路由 → 子依赖 → 子依赖；同一请求内可缓存（默认同一 `Depends` 只执行一次）。
- **与路由解耦**：鉴权、分页参数、公共 Header 校验写成依赖函数，而不是散落在每个路由里。

官方文档：[Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)。

---

## 4. 数据库 + ORM（SQLAlchemy 2.0）

- **风格**：2.0 推荐 `DeclarativeBase`、`Mapped`、`mapped_column`，Session 用 `sessionmaker` + 上下文管理。
- **与 FastAPI 结合**：在 `Depends` 里 `yield` session，请求结束关闭；**不要**把 Session 绑在全局单例上跨请求复用。
- **迁移**：生产环境用 Alembic 管理 schema，与「先改模型再生成迁移」的工作流对齐。

---

## 5. 认证授权（OAuth2 + JWT）

- **密码流（学习/内部 API）**：`OAuth2PasswordBearer` + token URL；登录端点校验密码后发 JWT。
- **JWT 载荷**：`sub`（用户标识）、过期时间 `exp`、按需加 `scopes`；密钥与算法放在配置里，勿写死。
- **授权**：在依赖里解析 JWT → 查用户/角色 → `HTTPException(403)`；或 OAuth2 scopes + `SecurityScopes`。

官方文档：[Security](https://fastapi.tiangolo.com/tutorial/security/)。

---

## 6. 日志、配置、异常统一处理

- **配置**：`pydantic-settings` 的 `BaseSettings` 读环境变量 + `.env`；区分 `dev` / `prod`。
- **日志**：标准库 `logging` 或 `structlog`；在启动时配置一次 handler/级别，中间件或依赖里打结构化日志（request_id、user_id）。
- **异常**：注册 `@app.exception_handler` 或自定义异常基类，统一返回 `{ "detail": "..." }` 与 HTTP 状态码，避免堆栈泄露给客户端。

---

## 7. 路由拆分、项目结构模块化

推荐按**业务域**拆 `APIRouter`，在 `main` 里 `include_router(prefix=..., tags=...)`。

```
fastapi_app/
├── main.py              # create_app、挂载路由、中间件、生命周期
├── api/
│   └── v1/
│       ├── router.py    # 聚合各子路由
│       └── endpoints/   # 按资源拆分
├── core/
│   ├── config.py
│   ├── security.py
│   └── exceptions.py
├── db/
│   ├── session.py       # engine、get_db
│   └── models/          # SQLAlchemy 模型
├── schemas/             # Pydantic（与 ORM 分离）
├── services/            # 业务逻辑（可选）
├── dependencies/        # 可复用 Depends
└── middleware/          # 例如 request timing、CORS 在 main 中注册
```

---

## 8. 中间件、CORS

- **CORS**：`CORSMiddleware` 配置 `allow_origins`（生产不要用 `*` + credentials）、`allow_methods`、`allow_headers`。
- **中间件顺序**：后添加的先执行（像洋葱）；认证日志、request_id 通常靠前。
- **耗时与限流**：可在中间件里记 `process_time`；限流可结合 Redis 或网关。

官方文档：[CORS](https://fastapi.tiangolo.com/tutorial/cors/)、[Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)。

---

## 9. 部署（Docker + 云服务器）

- **进程服务**：生产用 **Uvicorn + Gunicorn**（多 worker）或等价 ASGI 进程管理；前面加 Nginx 终止 TLS、静态资源、反向代理。
- **Docker**：多阶段构建减小镜像；`ENV` 注入配置；健康检查 `GET /health`。
- **云主机**：开放安全组端口、证书续期、日志落盘或集中采集；密钥用环境变量或托管密钥服务，不进镜像。

官方文档：[Deployment](https://fastapi.tiangolo.com/deployment/)。

---

## 本目录职责（摘要）

- API 路由定义；请求/响应模型（Pydantic）；中间件（CORS、日志、认证等）；依赖注入；按需 WebSocket。

最小目录示意（可与上表 `api/v1` 方案二选一演进）：

```
fastapi_app/
├── api/v1/endpoints/    # 或扁平 routes/
├── schemas/             # 或 models/（Pydantic）
├── middleware/
└── dependencies/
```

---

## 延伸阅读

- [FastAPI 官方教程](https://fastapi.tiangolo.com/tutorial/)（按章节顺序过一遍效果最好）
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
