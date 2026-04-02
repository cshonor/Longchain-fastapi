# 02 — FastAPI 基础（FastAPI basics）

**核心内容**：路由、路径/查询参数、Request Body、Pydantic 模型与校验。  
**核心目标**：规范接收并校验前端数据，熟悉 `/docs` OpenAPI。

---

## 这部分学完你会得到什么（为什么 FastAPI “快”）

FastAPI 的“快”通常来自两点：

- **Starlette**：负责 ASGI 异步 HTTP / WebSocket 等底层能力
- **Pydantic**：负责参数校验、数据序列化、类型提示与 JSON Schema

它带来的直接收益：

- **上手快**：写法直观、编辑器补全友好
- **开发快**：自带 Swagger（`/docs`）与 OpenAPI，接口写完自动生成文档
- **更规范**：遵循 OpenAPI（Swagger）与 JSON Schema，适合企业级项目落地
- **更稳定**：请求/响应模型统一，减少输入输出不一致导致的 bug

---

## 本模块要解决的三个问题

- **如何使用 FastAPI 写接口？**（路由、参数、Body、Response）
- **如何使用 FastAPI 写异步？**（`async/await`、并发与并行的边界）
- **如何使用 FastAPI 连数据库？**（这一块主要在 `06_database/` 展开；此模块先打基础）

---

## 目录（按文档逐步补充）

（在此目录下按章节添加笔记或示例文件名，如 `03_pydantic.md`。）

- [FastAPI 异步代码、并发和并行](./fastapi_async_code_concurrency_parallel.md)
