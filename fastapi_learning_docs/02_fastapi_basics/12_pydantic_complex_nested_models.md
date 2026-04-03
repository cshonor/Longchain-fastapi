# FastAPI + Pydantic：复杂模型与嵌套模型（速记）

在 [Pydantic 基础](./04_pydantic_study.md)、[Request Body](./07_request_body.md)、[多 Body / embed](./08_request_body_multiple_embed.md) 之上，这一节记 **Field 校验、集合类型、嵌套模型、常用特殊类型、`embed=True`**。

---

## 一、`Field` 字段校验

给模型字段加约束与文档说明，直觉上接近 `Query` / `Path` / `Body` 里的附加信息。

```python
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    description: str | None = Field(default=None, title="描述", max_length=300)
    price: float = Field(..., gt=0, description="必须大于 0")
    tax: float | None = None
```

常用参数（以当前 Pydantic 版本文档为准）：

- `title` / `description`：Schema / 文档说明  
- `gt` / `ge` / `lt` / `le`：数字范围  
- `max_length` / `min_length`：字符串长度  
- `pattern`：字符串模式（不少旧教程写 `regex`，新项目优先 `pattern`）

---

## 二、集合类型（`list` / `set` / `dict`）

### 1. `list` / `set`

```python
class Item(BaseModel):
    tags: list[str] = Field(default_factory=list)
    unique_tags: set[str] = Field(default_factory=set)
```

可变默认值不要用 `= []` / `= set()`，用 **`default_factory`**，避免多个实例共享同一对象。

### 2. `dict` 作请求体

JSON 对象的 **key 在传输层始终是字符串**；若需要「整数下标 → 浮点权重」这类结构，常用 **`dict[str, float]`** 或在模型里用嵌套 / 列表再转换。

```python
@app.post("/index-weights/")
async def create_index_weights(weights: dict[str, float]):
    return weights
```

---

## 三、嵌套模型（重点）

一个 `BaseModel` 里可以嵌套另一个 `BaseModel`，**深度不限**。

### 1. 单层嵌套

```python
class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    image: Image | None = None
```

请求体示例：

```json
{
  "name": "foo",
  "image": { "url": "https://example.com/a.png", "name": "主图" }
}
```

### 2. 模型列表

```python
class Item(BaseModel):
    images: list[Image] | None = None
```

### 3. 深层嵌套

```python
class Offer(BaseModel):
    name: str
    items: list[Item]
```

---

## 四、内置特殊类型（节选）

- `HttpUrl`：URL 格式（`from pydantic import HttpUrl`）  
- `EmailStr`：邮箱（通常需安装 **`email-validator`**）  
- `UUID`、`datetime`、`date` 等：按类型自动校验与解析  

```python
from pydantic import BaseModel, HttpUrl


class Image(BaseModel):
    url: HttpUrl
```

---

## 五、`embed=True`：根上多包一层键

与 [多 Body / embed](./08_request_body_multiple_embed.md) 一致：希望客户端发送：

```json
{ "item": { "name": "...", "price": 1.0 } }
```

而不是直接把字段摊在根上时：

```python
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item = Body(..., embed=True)):
    ...
```

---

## 延伸阅读

- 可运行示例：[`fastapi_pydantic_complex_demo.py`](./fastapi_pydantic_complex_demo.py)
