# 02 — FastAPI 基础（FastAPI basics）

**核心内容**：路由、路径/查询参数、Request Body、Pydantic 模型与校验。  
**核心目标**：规范接收并校验前端数据，熟悉 `/docs` OpenAPI。

---

## 这部分学完你会得到什么（为什么 FastAPI “快”）

1. **FastAPI 快**
   性能常被拿来与 Go、Node.js 做对标；底层主要靠两个核心：
   - **Starlette**：负责异步 HTTP、WebSocket（ASGI 基座）
   - **Pydantic**：负责参数校验、数据格式与 Schema（JSON Schema）

2. **简单好上手**
   - 写法直观，编辑器自动补全友好
   - 自带 Swagger 接口文档（`/docs`），接口写完自动生成
   - 开发速度快，输入输出更稳定，bug 更少

3. **稳定、规范**
   - 可用于企业级项目
   - 遵循标准：OpenAPI（Swagger）、JSON Schema

---

## 本模块要解决的三个问题

- **如何使用 FastAPI 写接口？**（路由、参数、Body、Response）
- **如何使用 FastAPI 写异步？**（`async/await`、并发与并行的边界）
- **如何使用 FastAPI 连数据库？**（这一块主要在 `06_database/` 展开；此模块先打基础）

---

## 目录（按文档逐步补充）

（在此目录下按章节添加笔记或示例文件名，如 `03_pydantic.md`。）

- [FastAPI 安装 + 入门 Hello World](./01_fastapi_install_hello_world.md)
- [FastAPI 路径参数（8 句话吃透）](./02_path_params_8_sentences.md)
- [Enum 路径参数严格校验](./03_enum_path_params.md)
- [路径参数 + Enum 路径参数 Demo（可直接跑）](./fastapi_path_enum_demo.py)
- [FastAPI + Pydantic 最小 Demo（可直接跑）](./fastapi_pydantic_demo.py)
- [Pydantic 自动类型校验（FastAPI 稳的关键）](./04_pydantic_study.md)
- [FastAPI 异步代码、并发和并行](./05_fastapi_async_code_concurrency_parallel.md)
- [FastAPI 请求参数（Query）](./06_query_params.md)
- [Query 请求参数 Demo（可直接跑）](./fastapi_query_params_demo.py)
- [FastAPI Request Body（请求体 JSON）](./07_request_body.md)
- [Request Body Demo（可直接跑）](./fastapi_request_body_demo.py)
- [Request Body：多模型、embed、Body 标量](./08_request_body_multiple_embed.md)
- [多 Body / embed / Body 标量 Demo（可直接跑）](./fastapi_multiple_body_demo.py)
- [Query 参数附加信息（Query 校验/别名/废弃）](./09_query_params_query_extra.md)
- [Query(...) 附加信息 Demo（可直接跑）](./fastapi_query_extra_demo.py)
- [路径参数与查询参数混用、Path、同名](./10_path_and_query_mix.md)
- [路径 + Query 混用 Demo（可直接跑）](./fastapi_path_query_mix_demo.py)
