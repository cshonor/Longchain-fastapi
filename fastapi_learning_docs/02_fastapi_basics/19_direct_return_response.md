# FastAPI 直接返回 `Response` 对象（精简）

返回 **`dict` / Pydantic 模型** 时，FastAPI 会用 **`jsonable_encoder`** 等机制序列化，再默认包成 **`JSONResponse`**。

当你**自己返回** `Response`、`JSONResponse`、`StreamingResponse` 等时：**框架不再替你套用 `response_model`、也不再自动 JSON 包装**（除非你返回的就是带 `content` 的 `JSONResponse`）。适合要**完全控制**正文、状态码、头、媒体类型时。

（与 [`response_model`](./18_response_model.md)、[自定义状态码](./16_response_status_code.md) 对照：一个管「声明式过滤/文档」，一个管「手写响应」。）

---

## 核心逻辑

| 返回类型 | 典型行为 |
|----------|-----------|
| `dict`、Pydantic 模型 | 自动 JSON 化（经 `jsonable_encoder` 等） |
| `JSONResponse` / `Response` 等 | **按你给的** `content`、`media_type`、`headers` 原样返回 |

---

## 1. 手动 `JSONResponse` + `jsonable_encoder`

先把模型、含 `datetime` 等字段的结构转成 **JSON 可序列化** 的纯数据结构，再交给 `JSONResponse`。

```python
from datetime import datetime

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


@app.put("/items/{item_id}")
def update_item(item_id: str, item: Item):
    json_data = jsonable_encoder(item)
    return JSONResponse(content=json_data)
```

---

## 2. 非 JSON：`Response` + `media_type`

例如返回 **XML**、纯文本、HTML 等：

```python
from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/legacy/")
def get_legacy_data():
    xml_data = """<?xml version="1.0"?>
<shampoo>
  <Header>Apply shampoo here.</Header>
  <Body>You'll have to use soap here.</Body>
</shampoo>
"""
    return Response(content=xml_data.encode("utf-8"), media_type="application/xml")
```

（`content` 一般为 **`bytes`**；字符串可先 `.encode("utf-8")`。）

---

## 常用场景

- 自定义响应头、Cookie、状态码（也可配合 [16](./16_response_status_code.md)）  
- 返回 XML、纯文本、HTML、文件流、二进制  
- 兼容旧客户端或特殊协议  
- 需要**绕过**默认 JSON 与 `response_model` 过滤链时  

---

## 可运行示例

见 [`fastapi_direct_response_demo.py`](./fastapi_direct_response_demo.py)。
