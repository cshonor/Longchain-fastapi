# FastAPI 安装 + 入门 Hello World（最标准版）

本篇只做一件事：**用最少步骤把 FastAPI 跑起来，并理解它的开发体验（类型校验 + 自动文档）**。

---

## 一、安装

### Conda（推荐先建环境）

1) 创建并激活环境（示例用 Python 3.11）

```bash
conda create -n fastapi-demo python=3.11 -y
conda activate fastapi-demo
```

2) 安装依赖（纯 conda）

```bash
conda install -c conda-forge fastapi uvicorn -y
```

---

## 二、最小运行代码

新建 `main.py`：

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

运行：

```bash
uvicorn main:app --reload
```

访问：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/items/5?q=test`

---

## 三、自带接口文档（最爽的点）

启动后自动生成，无需手写：

- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`

---

## 四、这篇的核心知识点

1) FastAPI 依赖两大底层：

- **Starlette**：处理 Web、HTTP、异步（ASGI）
- **Pydantic**：数据校验、类型检查、Schema 生成

2) 运行必须靠 **Uvicorn**（或其它 ASGI 服务器）。

3) 接口自带**类型校验**：例如 `item_id: int`，传字符串会直接返回 422 校验错误。

4) 自动生成文档：开发调试非常高效。

---

## 五、本仓库怎么跑（可选）

本仓库的 FastAPI 代码入口在 `fastapi_app/`，启动命令通常是：

```bash
uvicorn fastapi_app.main:app --reload
```

---

下一篇建议：Pydantic 如何做参数校验与响应模型（与本模块主题最衔接）。

