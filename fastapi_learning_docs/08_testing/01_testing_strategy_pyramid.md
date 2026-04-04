# FastAPI 项目测试体系总览

下面把**企业级后端常见测试概念**拆成三类，并对应到 **FastAPI + 本仓库 `fastapi_app/`** 的落地方式：**单元与替身** → **按分层测** → **集成 / 安全 / 负载 / CI**。

（官方入门：[FastAPI — Testing](https://fastapi.tiangolo.com/tutorial/testing/)，使用 **`TestClient`** 或 **`httpx.AsyncClient`**。）

---

## 一、概念对应关系

1. **基础单元测试工具与替身（Test Doubles）**  
2. **按代码分层的测试（Web / Service / DAO）**  
3. **进阶测试类型（集成、安全、负载、自动化）**  

---

### 1. 单元测试地基：`pytest` 与 Test Doubles

| 术语 | 含义 | 在 FastAPI 项目里 |
|------|------|-------------------|
| **pytest** | Python 最常用的测试运行框架；FastAPI 文档示例基于它。 | 统一跑用例、插件（覆盖率、`pytest-asyncio` 等）。 |
| **Monkeypatch** | 运行时替换属性/函数，隔离外部环境。 | 例如替换某模块里的 `requests.post`，避免真实 HTTP。 |
| **Stub** | 只返回预定数据，**不**强调“是否被调用”。 | 给 Service 传入“假的 DAO 返回值”。 |
| **Mock** | 可断言**调用次数、参数**；常配合 **`pytest-mock`**（`mocker`）。 | 测 Service 是否按预期调了外部 API。 |
| **Fake** | 可运行的简化实现（如内存库代替 MySQL）。 | DAO 测试用 **SQLite 内存库** 或事务回滚的测试库。 |

**示例**：被测代码调用 `requests.post`，用 Mock 断网测试：

```python
# 被测模块（示例）
import requests

def call_openai(prompt: str) -> str:
    response = requests.post(
        "https://api.openai.com/v1/chat",
        json={"prompt": prompt},
        timeout=30,
    )
    return response.json()["answer"]


def test_call_openai(mocker):
    mock_post = mocker.patch("requests.post")
    mock_resp = mocker.Mock()
    mock_resp.json.return_value = {"answer": "test"}
    mock_post.return_value = mock_resp

    result = call_openai("hello")
    assert result == "test"
    mock_post.assert_called_once()
```

**注意**：若代码里是 `from myapp.http import post`，应在 **`myapp.http.post` 被使用处** 所在模块上 patch（**在用到的命名空间 patch**），而不是盲目写 `"requests.post"`。

---

### 2. 按分层测试（与典型目录对应）

| 层级 | 典型对应 | 测试目标 | 常用手段 |
|------|----------|----------|----------|
| **Web / API** | `fastapi_app/api/` 路由、`main.py` 挂载 | 状态码、Body、`response_model`、鉴权、422 | **`pytest` + `TestClient`**（或异步 **`httpx.AsyncClient` + `ASGITransport`**） |
| **Service** | 业务函数、领域逻辑 | 规则是否正确，**不**连真实 DB / 外网 | **`pytest` + Mock/Fake** 注入依赖 |
| **DAO / Repository** | SQLAlchemy Session、CRUD | SQL 与读写是否正确 | **`pytest` + SQLite 内存 / 测试库事务回滚** |

**落地顺序建议**：

- **Web**：`client.get("/path")` / `client.post(...)` 断言 JSON 与状态码。  
- **Service**：Mock 掉 `get_db`、外部 SDK，只测纯逻辑。  
- **DAO**：对**真实 Session** 但**隔离库**跑 CRUD，必要时再抽集成测试。

---

### 3. 进阶类型

| 类型 | 含义 | 在项目中怎么用 |
|------|------|----------------|
| **集成测试** | 多模块 + 真实或容器化依赖一起跑 | 例如 API + Service + 测试库，跑完整「请求 → 入库 → 响应」。 |
| **外部 API 契约 / 探测** | 第三方是否可用、响应格式是否变 | 单独标记的慢测（`@pytest.mark.slow`），可定时跑，避免拖垮每次 CI。 |
| **安全测试** | 未授权访问、注入、错误配置等 | 自动化用例 + **OWASP ZAP** 等扫描；依赖与 [安全章节](../05_security/) 设计一致。 |
| **负载 / 性能** | 并发、延迟、错误率 | **Locust**、**k6** 等对 `/chat` 等热点路径压测。 |
| **CI 全流程** | 提交即跑测 | **GitHub Actions / GitLab CI** 执行 `pytest`，可选覆盖率门槛。 |

---

## 二、FastAPI 落地路线图（建议顺序）

### 第一步：单元地基

- Web：`TestClient(app)` 覆盖主要路由与错误路径。  
- Service：`pytest-mock` / `Monkeypatch` 隔离外依。  
- DAO：内存 SQLite 或专用测试数据库 + `fixture` 管理 Session。

### 第二步：集成

- 串起「HTTP → Service → DB」一条链路；数据库可用 Docker 或 CI 服务容器。

### 第三步：上线前

- 抽样负载测试；CI 中跑单元 + 关键集成；安全扫描按周期执行。

---

## 三、一句话

**单元测试**保证模块写得对，**集成测试**保证拼起来能跑，**安全 / 负载 / CI** 降低上线风险；在 FastAPI 里**核心跑具是 `pytest`**，Web 层优先 **`TestClient`**，其余概念都围绕**分层与替身**展开。

---

## 延伸阅读

- 目录结构、`conftest.py`、`fixture` 分层可在本目录后续补 **`02_tests_layout.md`** 或直接在 `fastapi_app/tests/` 里按上述分层落文件。  
- 异步路由测试见官方 **Async Tests** 与 **`httpx.AsyncClient`** 说明。
