# 生产级 FastAPI 系统化学习指南

基于本仓库 `fastapi_app/` 目录的实践约定，下列路径覆盖从异步基础到部署的**完整、正统、生产级** FastAPI 学习链路：基础理论、异步协程、请求与 Response、中间件、依赖注入、安全、数据库与进阶主题。

---

## 总学习规划概览

| 模块 | 核心内容 | 学习周期 | 核心目标 |
| :--- | :--- | :--- | :--- |
| **Python 协程** | 异步编程基础 | 约 3 天 | 理解 `async/await`，能写出异步代码 |
| **FastAPI 基础** | 请求、参数、Body、Pydantic | 约 7–8 天 | 能规范地接收和处理前端数据 |
| **Response 与中间件** | 响应定制、全局拦截 | 约 3 天 | 掌控接口输出，处理跨域、日志等通用逻辑 |
| **依赖注入系统** | IOC/DI 核心 | 约 4 天 | 掌握 FastAPI 的核心抽象，解耦代码 |
| **安全机制** | 认证、授权、JWT | 约 3 天 | 接口安全，防止未授权访问 |
| **数据库访问** | ORM、异步数据库 | 约 4 天 | 熟练操作数据库，保证数据持久化 |
| **进阶知识** | 错误处理、后台任务等 | 约 3–4 天 | 处理生产环境复杂场景 |

合计约 **30 天**可按节奏完成（可按周调整）。

---

## 详细学习内容拆解

### 第一阶段：夯实异步基础（建议先学）

FastAPI 的高吞吐与异步模型密切相关，建议先打地基。

扩展阅读（协程概念沿革：yield / greenlet / gevent / asyncio）：[`01_python_coroutines/python_coroutine_01_overview.md`](./01_python_coroutines/python_coroutine_01_overview.md)。各阶段文档目录见 [本目录 `README.md`](./README.md)。

1. **FastAPI 异步代码、并发和并行**
   - **学什么**：区分进程、线程、协程；理解 `async`（异步函数）、`await`（等待可等待对象）。
   - **重点**：何时用 `async def`、何时仍用同步 `def`（以及阻塞调用不要放进事件循环线程）。
2. **Python 协程（Asyncio 入门）**
   - **学什么**：`asyncio` 基础：任务创建、事件循环概念。
   - **实操**：编写多个异步任务，观察并发调度与完成顺序。

### 第二阶段：FastAPI 核心基础（动手写接口）

重点在**数据规范**与路由组织。

1. **基础（一）概述**：安装环境、第一个 `app`、`APIRouter` 拆分。
2. **基础（二）开发环境**：`requirements.txt`、`uvicorn` 启动与热重载。
3. **基础（三）Pydantic 类型与校验**：`BaseModel`、字段类型、默认值（**核心**）。
4. **基础（四）（五）路径参数与查询参数**：路径 `{id}`、`?key=value`。
5. **基础（六）（七）Request Body**：POST/PUT JSON，与 Pydantic 模型绑定。
6. **基础（八）（九）参数附加信息**：`Field()` 描述、示例、校验（长度、正则等）。
7. **基础（十）复杂模型**：嵌套、列表、递归结构。
8. **基础（十一）复杂数据类型**：`date`、`datetime`、`UUID`、`Enum`。
9. **基础（十二）（十三）Cookie 与 Header**：读取与设置。
10. **基础（十四）Response 与状态码**：200、201、400、401、500 等语义化使用。
11. **基础（十五）直接使用 Request**：原始 Body、客户端 IP 等底层需求。

### 第三阶段：响应与中间件（服务骨架）

1. **Response**
   - **（一）Response 模型**：`response_model`、过滤敏感字段。
   - **（二）直接返回 Response**：`JSONResponse`、`PlainTextResponse` 等。
   - **（三）（四）定制**：响应头、格式、重定向。
2. **中间件**
   - **（一）（二）自定义中间件**：请求前后逻辑（耗时、日志、trace id）。
   - **（三）跨域**：`CORSMiddleware`，生产环境注意 origin 与 credentials。

### 第四阶段：依赖注入系统（核心抽象）

1. **（一）简介**：依赖是什么、为何用 `Depends`。
2. **（二）（三）依赖类与子依赖**：可调用类、依赖链。
3. **（四）路由级依赖**：路由组、装饰器层面的公共依赖（如 `/admin` 鉴权）。
4. **（五）带 yield 的依赖**：资源获取与释放（典型：`yield` 数据库会话）。
5. **（六）可参数化依赖**：工厂、复用与测试替换。

### 第五阶段：安全与数据库（工程化核心）

1. **安全机制**
   - **（一）简介**：API Key、OAuth2 等概念。
   - **（二）（三）JWT**：签发、登录、校验（**必练**）。
   - **（四）OAuth2 scopes**：角色与细粒度权限。
2. **数据库**
   - **（一）SQLAlchemy 同步**：Engine、Session、Model、CRUD。
   - **（二）SQLAlchemy 异步**：`async` session 与高并发场景（生产常见选型）。

### 第六阶段：进阶

1. 表单：`Form()`、文件上传。
2. **错误处理**：全局异常、自定义异常类（生产必备）。
3. **后台任务**：`BackgroundTasks`（邮件、报表等非阻塞后置工作）。
4. **子应用**：多 `FastAPI` 实例挂载、大型项目拆分。
5. **生命周期**：启动/关闭时连接池、缓存等资源的创建与释放。

---

## 执行建议

1. **先动手再加深**：每节先照官方教程或示例敲通，再补理论；协程、`yield` 可先会用再读原理。
2. **善用 Swagger**：每写一个接口在 `/docs` 里试请求与校验，熟悉 OpenAPI 与 Pydantic 联动。
3. **小项目串联**：完成第二阶段后可做迷你「用户系统」：注册登录、CRUD、统一响应、DB 经依赖注入注入。
4. **异步不必畏难**：从路径函数 `async def` 开始，逐步接触纯异步 DB 与 HTTP 客户端。

---

## 与本仓库代码的对应关系

| 主题 | 可在本包中对照的文件或位置 |
| :--- | :--- |
| 应用入口、CORS、中间件 | `main.py` |
| 路由拆分 | `api/v1/router.py`、`api/v1/endpoints/` |
| Pydantic 模型 | `schemas/` |
| 配置与密钥占位 | `core/config.py` |
| OAuth2 占位 | `core/security.py` |
| 统一异常 | `core/exceptions.py` |
| ORM 基类与 Session | `db/models/base.py`、`db/session.py` |
| 可复用依赖 | `dependencies/` |
| 请求耗时中间件示例 | `middleware/request_timing.py` |

更简要的要点速查仍见 [README.md](./README.md)。官方教程：[FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)。
