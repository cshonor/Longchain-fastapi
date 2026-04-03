# FastAPI 中的 `Request` 对象（原始请求）

需要 **IP、原始 Header/Cookie、原始 Body** 等 Starlette/FastAPI 未替你「拆成参数」的信息时，在路由函数里**注入** `Request` 即可。

```python
from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/items/{item_id}")
def read_items(item_id: str, request: Request):
    client_host = request.client.host if request.client else None
    return {"client_host": client_host, "item_id": item_id}
```

> `request.client` 在少数部署方式下可能为 `None`，使用前建议判断。

---

## 常见用途

| 需求 | 典型访问方式 |
|------|----------------|
| 客户端地址 | `request.client.host`（若存在） |
| 请求头 | `request.headers`（类字典） |
| Cookie | `request.cookies` |
| 原始 body | `await request.body()`（需在 **`async def`** 路由里） |
| URL / 路径 | `request.url`、`request.url.path`、`request.query_params` 等 |

本质：**框架已帮你解析成函数参数的部分用类型注解；其余底层细节用 `Request` 自取。**

---

## 与依赖注入

在 `Depends()` 里同样可以声明 `request: Request`，用于**统一日志、鉴权、限流**等横切逻辑。

---

## 可运行示例

见 [`fastapi_request_object_demo.py`](./fastapi_request_object_demo.py)。
