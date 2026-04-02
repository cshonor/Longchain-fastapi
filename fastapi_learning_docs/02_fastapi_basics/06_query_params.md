# FastAPI 请求参数（Query 参数）

这一章讲的是 **Query 参数**：URL 里 `?` 后面的键值对，例如 `/items?skip=0&limit=10`。

---

## 一、什么是请求参数？

```
/items/?skip=0&limit=10
```

- `skip=0`
- `limit=10`

它们**不是**路径里 `{}` 占位符，FastAPI 会把函数里**未标注为路径参数**、且来自查询串的入参，自动识别为 **Query 参数**。

---

## 二、规则和路径参数一致

- 支持类型注解：`int`、`str`、`bool` 等
- **自动类型转换**
- **自动校验**（传错类型 → 通常 422）
- **自动出现在** `/docs` OpenAPI 文档里

底层同样是 **Pydantic** 在做校验。

---

## 三、三种参数形态（最重要）

### 1. 带默认值 → 可选

```python
async def read_item(skip: int = 0, limit: int = 10):
    ...
```

不传就用默认值，**可传可不传**。

### 2. 显式可选（推荐写法）

```python
async def read_item(q: str | None = None):
    ...
```

`None` 表示「可以不传这个查询参数」。

### 3. 没默认值 → 必传

```python
async def read_item(needy: str):
    ...
```

不传会报校验错误（常见为 `field required`）。

---

## 四、路径参数 + Query 混用

FastAPI 会按**参数名与位置**自动区分：

```python
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,
    item_id: str,
    q: str | None = None,
    short: bool = False,
):
    return {"user_id": user_id, "item_id": item_id, "q": q, "short": short}
```

- `user_id`、`item_id`：来自路径
- `q`、`short`：来自 Query

---

## 五、一句话总结

| 类型 | 在 URL 里长什么样 |
|------|-------------------|
| **路径参数** | `/users/{user_id}` |
| **Query 参数** | `?skip=0&limit=10` |

两者都支持：**类型校验 + 自动转换 + 必选/可选**。

---

## 下一章

**Request Body（请求体）**：`POST` 传 JSON，通常用 Pydantic `BaseModel` 接收，进入更偏「实战」的后端写法。
