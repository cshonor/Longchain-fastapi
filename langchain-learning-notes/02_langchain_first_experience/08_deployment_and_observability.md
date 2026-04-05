# LangChain 应用：部署与可观测性

承接 [LCEL 组件组合](./07_lcel.md)：链在本地用 `invoke` / `stream` 跑通之后，通常还需要 **对外暴露为服务**（部署），以及 **追踪与调试**（可观测性）。本章对应两块官方能力：**LangServe**、**LangSmith**。

---

## 一、使用 LangServe 部署 LCEL 链

### 1. 核心作用

**LangServe** 把已写好的 **Runnable / LCEL 链** 挂到 **FastAPI** 上，自动生成 HTTP 路由，便于被其它服务、前端或脚本调用。

- 将 **`prompt | chat | parser`** 这类链变成 **REST 风格 API**  
- 常见附带：**OpenAPI 文档**、**invoke / stream** 等端点（具体以当前 `langserve` 版本为准）

### 2. 依赖与安装

项目根目录 `requirements.txt` 已包含 **`langserve`**；若单独安装：

```bash
python -m pip install "langserve>=0.3"
```

### 3. 代码示例（与书中结构一致，已做工程化修正）

下面与教程一致：**`ChatPromptTemplate | ChatDeepSeek | 输出解析器`**。修正点：

- **`ChatDeepSeek`** 需传入 **`api_key`**（建议 `DEEPSEEK_API_KEY` 环境变量）。  
- 解析器优先使用内置 **`CommaSeparatedListOutputParser`**，并在 system 中拼接 **`get_format_instructions()`**，格式更稳；若手写 `split(",")`，记得对每项 **`strip()`**。

```python
import os

from fastapi import FastAPI
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek
from langserve import add_routes

parser = CommaSeparatedListOutputParser()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个能生成逗号分隔列表的助手。只输出列表，不要多余说明。\n\n"
            + parser.get_format_instructions(),
        ),
        ("human", "{text}"),
    ]
)
chat = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
)
chain = prompt | chat | parser

app = FastAPI(title="第一个 LangChain 应用", version="0.1.0")
add_routes(app, chain, path="/chain")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
```

### 4. 关键 API

- **`add_routes(app, chain, path="/chain")`**：把链挂到指定路径前缀下。  
- 启动后通常包括（以实际版本与 `/docs` 为准）：  
  - **`POST /chain/invoke`**：单次调用  
  - **`POST /chain/stream`**：流式（若 Runnable 支持）  
  - **`/docs`**：Swagger / OpenAPI 交互文档  

### 5. 启动与调用示例

在**仓库根目录**启动可运行示例（见 [demo_langserve_app.py](./demo_langserve_app.py)）：

```bash
python langchain-learning-notes/02_langchain_first_experience/demo_langserve_app.py
```

使用 **curl** 调用 `invoke`（请求体一般为 **`input` 包一层**，与 LangServe 约定一致）：

```bash
curl -s -X POST "http://127.0.0.1:8000/chain/invoke" ^
  -H "Content-Type: application/json" ^
  -d "{\"input\": {\"text\": \"动物\"}}"
```

（Linux / macOS 将 `^` 换为 `\` 续行即可。）

浏览器打开 **`http://127.0.0.1:8000/docs`** 可对照实际路径与请求体 schema。

**PowerShell** 单次调用示例：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/chain/invoke" -Method Post `
  -ContentType "application/json" `
  -Body '{"input":{"text":"动物"}}'
```

---

## 二、使用 LangSmith 做可观测性（监控与调试）

### 1. 核心作用

**LangSmith** 用于在平台上查看一次调用从 **Prompt → 模型 → Parser** 各步的 **输入/输出、耗时、token** 等，便于排错与优化。

### 2. 启用方式（环境变量）

在运行链或 LangServe 进程的**同一环境**中设置（示例为 Linux / macOS）：

```bash
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="你的 LangSmith API Key"
# 可选：项目名，便于在控制台筛选
export LANGCHAIN_PROJECT="longchain-notes"
```

**Windows PowerShell** 示例：

```powershell
$env:LANGCHAIN_TRACING_V2 = "true"
$env:LANGCHAIN_API_KEY = "你的 LangSmith API Key"
$env:LANGCHAIN_PROJECT = "longchain-notes"
```

也可写入仓库根目录 **`.env`**（勿提交到 Git），与 [其它 Demo](./demo_lcel.py) 一样用 `python-dotenv` 加载。

启用后，**`invoke` / `stream`** 等调用可被记录到 LangSmith（以官方当前行为为准）。控制台：[https://smith.langchain.com/](https://smith.langchain.com/)

### 3. 典型能看到的维度

- 各 Runnable 步骤的输入与输出  
- 耗时、token 用量（视模型与集成而定）  
- 异常与调用栈，便于定位是哪一环失败  

---

## 三、概念对照表

| 工具 | 作用 | 一句话 |
| :--- | :--- | :--- |
| **LCEL** | 用 **`|`** 组合 Runnable | 应用**核心逻辑**怎么写 |
| **LangServe** | 把链暴露成 **HTTP API** | **部署**、给外部调用 |
| **LangSmith** | 追踪与调试 | **可观测性**、排错与优化 |

---

## 四、从开发到上线（流程）

1. **开发**：用 LCEL 写链（如 **`prompt | llm | parser`**），本地 `invoke` / `stream` 验证。  
2. **部署**：用 **LangServe + FastAPI + uvicorn** 把链挂成服务。  
3. **运维**：用 **LangSmith** 看调用轨迹与指标，迭代提示词与链结构。

---

## 延伸阅读

- [环境搭建 & 核心概念](./01_env_and_core_concepts.md)（文中已提到 LangServe / LangSmith）  
- [LCEL 组件组合](./07_lcel.md)  
- 可运行服务示例：[demo_langserve_app.py](./demo_langserve_app.py)
