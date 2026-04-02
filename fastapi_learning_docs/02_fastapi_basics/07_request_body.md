# FastAPI Request Body（请求体）

这一章讲的是 **Request Body**：前端用 `POST` / `PUT` 等放在**请求体**里的 **JSON**，不是 URL 里的路径或 `?` 查询串。

---

## 一、什么是 Request Body？

就是 **`POST` / `PUT`（等）时，HTTP body 里的一段 JSON**。  
和路径参数、Query 参数区分开：Body 是「正文里的一大段结构化数据」。

---

## 二、怎么接收？（四步固定套路）

1. 从 Pydantic 导入 `BaseModel`
2. 写一个类，继承 `BaseModel`
3. 用类型注解定义字段（可选字段用默认值或 `| None`）
4. 路由函数里写一个参数，类型就是这个类

```python
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
```

```python
@app.post("/items/")
async def create_item(item: Item):
    return item
```

---

## 三、FastAPI 自动帮你做了什么？

1. **解析 JSON** 为 Python 数据
2. **按模型做类型与约束校验**（不符合则通常返回 **422**）
3. **得到 Pydantic 模型实例**，可直接当对象用
4. **生成 OpenAPI / `/docs`** 里的请求体 Schema

一般不需要自己读 `Request`、不需要手写 `json.loads`、不需要手写一层层类型判断。

---

## 四、怎么用这个数据？

用 **属性访问**：

```python
item.name
item.price
item.tax
```

需要普通 `dict` 时，Pydantic v2 用 **`model_dump()`**（v1 里常用 `dict()`，新项目以 v2 为准）：

```python
item.model_dump()
```

---

## 五、三种参数可以一起混用

FastAPI 会按**参数类型与声明**自动区分：

| 来源 | 典型写法 |
|------|-----------|
| 路径 | `item_id: int`（出现在路径 `{item_id}` 里） |
| Query | 可选查询串，例如 `Optional[str]` 或带默认值的 `int` / `bool` |
| Body | `item: Item`（Pydantic `BaseModel`） |

```python
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    q: str | None = None,
):
    return {"item_id": item_id, "item": item, "q": q}
```

---

## 六、一句话总结

**Request Body = 用 Pydantic 模型接收 JSON：自动校验、自动解析、自动变成对象。**  
这是写后端接口时**最常用、最核心**的一环之一。

---

## 你已经掌握的 FastAPI 三大传参方式

1. **路径参数**：`/user/{id}`
2. **Query 参数**：`?skip=10`
3. **请求体 JSON**：`item: Item`

后面写 **LangChain + RAG** 一类接口时，大量请求会以 JSON Body 形式进来，本章就是基础。
