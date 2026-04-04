# FastAPI 学习文档（`fastapi_learning_docs`）

本目录存放 **FastAPI 与异步基础** 的系统化学习笔记，与仓库内可运行代码 **`fastapi_app/`** 配套使用：文档讲「为什么、怎么学」，代码里是对照实践的骨架。

- 快速开始入口：**[INTRO.md](./INTRO.md)**

---

## 这份文档解决什么问题

- **学什么**：从 Python 协程 → FastAPI 路由与 Pydantic → 响应与中间件 → 依赖注入 → 安全 → 数据库 → 进阶主题 → **测试体系**，按阶段递进。
- **怎么用**：按下方 `01_`～`08_` 子目录顺序阅读；每章可自建小节 Markdown（如 `xxx_topic.md`）补充练习与踩坑记录。
- **和项目代码的关系**：实现入口见 `fastapi_app/main.py`，模块化结构见 `fastapi_app/api/`、`schemas/`、`core/` 等。

---

## 为什么选 FastAPI（速览）

| 方面 | 说明 |
|------|------|
| **性能** | 异步 I/O 友好，常见场景下吞吐表现好；底层 **Starlette** 负责 ASGI 异步 HTTP / WebSocket。 |
| **数据与规范** | **Pydantic** 做请求/响应校验与序列化，并与 **OpenAPI / JSON Schema** 对齐，适合团队与企业级接口约定。 |
| **开发体验** | 类型提示 + 自动补全；启动后默认 **Swagger UI**（`/docs`），接口即文档。 |

---

## 总路线（详细版）

完整阶段表、周期建议与执行提示见同目录：

- **[LEARNING_GUIDE.md](./LEARNING_GUIDE.md)**

---

## 模块目录（与总表一一对应）

| 目录 | 模块 | 说明 |
|------|------|------|
| [01_python_coroutines](./01_python_coroutines/) | Python 协程 | `asyncio`、`async`/`await`、事件循环、Task / Future |
| [02_fastapi_basics](./02_fastapi_basics/) | FastAPI 基础 | 路由、参数、Body、Pydantic；异步与并发概念速查 |
| [03_response_middleware](./03_response_middleware/) | Response 与中间件 | `response_model`、各类 Response、CORS、自定义中间件 |
| [04_dependency_injection](./04_dependency_injection/) | 依赖注入 | `Depends`、子依赖、带 `yield` 的资源 |
| [05_security](./05_security/) | 安全机制 | OAuth2、JWT、权限与 scopes |
| [06_database](./06_database/) | 数据库访问 | SQLAlchemy 2.0、Session、`get_db` 模式 |
| [07_advanced](./07_advanced/) | 进阶知识 | 异常处理、后台任务、生命周期、子应用等 |
| [08_testing](./08_testing/) | 测试体系 | pytest、分层测试、集成 / 负载 / CI |

---

## 推荐阅读顺序

1. **01** → **02**：先懂协程与 `await`，再写路由与模型。  
2. **03** → **04**：能返回规范响应后，再学依赖注入解耦。  
3. **05** → **06**：安全与持久化通常一起出现在真实业务里。  
4. **07**：收尾工程化能力。  
5. **08**：有接口与分层后，再系统搭测试与 CI。

---

## 与官方文档

- [FastAPI 官方教程](https://fastapi.tiangolo.com/tutorial/)  
- [Pydantic v2](https://docs.pydantic.dev/latest/)  
- [Starlette](https://www.starlette.io/)  
- [asyncio](https://docs.python.org/3/library/asyncio.html)
