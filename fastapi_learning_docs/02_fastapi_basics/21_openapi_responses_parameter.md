# FastAPI 装饰器参数 `responses`（OpenAPI / Swagger 高级声明）

在 `@app.get` / `post` 等装饰器里传入 **`responses={...}`**，用来在 **OpenAPI 文档**（`/docs`、`/redoc`）中**补充或覆盖**「不同 HTTP 状态码」下的响应说明：描述、Schema、示例、多种 `media_type` 等。

**注意**：这首先是**文档与客户端生成代码**的契约说明；**实际**返回仍由你的路由逻辑决定，应与之保持一致，避免文档撒谎。

（与 [`response_model`](./18_response_model.md)、[直接 Response](./19_direct_return_response.md) 配合理解：前者约束「成功体」，后者手写响应；`responses` 常用来把 **404/403** 等错误体也写进文档。）

---

## 一、`responses` 字典长什么样

键：**HTTP 状态码**（`int`，如 `200`、`404`）。  
值：描述该状态码响应的 **OpenAPI 片段**，常用字段包括：

- `description`：人类可读说明  
- `model`：Pydantic 模型（生成 JSON Schema，与 `response_model` 类似）  
- `content`：多种媒体类型，例如 `application/json`、`image/png` 等  

概念示例：

```python
responses = {
    404: {
        "model": Message,
        "description": "Resource not found",
    },
    200: {
        "description": "OK",
        "content": {
            "application/json": {
                "example": {"id": "bar", "value": "The bar"},
            }
        },
    },
}
```

具体键名以当前 **FastAPI 版本文档**为准（不同版本对 `model` / `content` 的简写支持略有演进）。

---

## 二、成功用 `response_model`，错误码用 `responses`

```python
@app.get(
    "/items/{item_id}",
    response_model=Item,
    responses={404: {"model": Message, "description": "Item not found"}},
)
```

含义（文档层面）：200 走 `Item`；404 可描述为 `Message` 形状。

---

## 三、多种 `media_type`（如 JSON 或图片）

在对应状态码下用 `content` 列出多种类型，便于文档展示「本接口可能返回哪一种表示」：

```python
responses = {
    200: {
        "description": "JSON or image",
        "content": {
            "application/json": {},
            "image/png": {},
        },
    }
}
```

---

## 四、描述与 `example`

把说明和示例写清楚，方便前端与联调：

```python
responses = {
    404: {"model": Message, "description": "Item not found"},
    200: {
        "description": "Item by ID",
        "content": {
            "application/json": {
                "example": {"id": "bar", "value": "The bar"},
            }
        },
    },
}
```

---

## 五、复用公共片段（合并字典）

```python
common = {
    403: {"description": "No permission"},
    404: {"description": "Not found"},
}

@app.get("/x", responses={**common, 200: {"description": "OK"}})
```

同一项目里可把 `common` 提到模块级，减少重复。

---

## 一句话

**`responses` 主要是给 OpenAPI 用的「多状态码、多媒体类型、示例与描述」声明**；与 `response_model`、手写 `Response` 分工不同，常一起用才能把文档写全。

---

## 可运行示例

见 [`fastapi_openapi_responses_demo.py`](./fastapi_openapi_responses_demo.py)。
