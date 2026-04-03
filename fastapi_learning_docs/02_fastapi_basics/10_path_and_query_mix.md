# 路径参数与查询参数：混用、校验、同名

用最直白的方式把三件事讲清：**路径里是什么**、**`?` 后面是什么**、**函数里怎么写**、**能不能同名**。  
（与 [路径参数](./02_path_params_8_sentences.md)、[Query 基础](./06_query_params.md)、[`Query(...)` 附加](./09_query_params_query_extra.md) 衔接。）

---

## 一句话总纲

1. **路径参数** = URL 路径里的 `/user/{id}`
2. **查询参数** = URL 后面的 `?id=123&name=xx`
3. **混用** = 在路由函数里**直接一起写**，FastAPI 按规则区分
4. **类型校验** = 参数类型注解写什么，FastAPI 就按什么做转换与校验
5. **不能同名** = 同一函数里路径参数名与查询参数名不能重复（否则 Python 语法或语义冲突）

---

## 1. 路径参数是什么？类型校验在哪？

### 路径参数长什么样

```python
@app.get("/user/{user_id}")
```

`{user_id}` 就是**路径参数**。

### 类型怎么校验？

在函数参数上写类型注解即可，FastAPI 会**自动转换与校验**：

```python
@app.get("/user/{user_id}")
def get_user(user_id: int):
    ...
```

- `int`：必须是合法整数路径段，例如 `/user/abc` 通常会 **422**
- `str`：路径段按字符串接收
- `float`：按数值解析（具体规则以框架行为为准）

更细的约束（数值范围、文档说明、废弃标记等）用 **`Path(...)`**，用法与 `Query(...)` 类似：

```python
from fastapi import Path

@app.get("/user/{user_id}")
def get_user(user_id: int = Path(..., gt=0, le=1000)):
    ...
```

---

## 2. 路径参数 + 查询参数怎么混用？

**直接在同一个函数里写在一起即可。**

FastAPI 会区分：

- 出现在路径 `{xxx}` 里的名字 → **路径参数**
- 未出现在路径里、且来自查询串的 → **Query 参数**

### 示例

```python
@app.get("/user/{user_id}/order/{order_id}")
def get_order(
    user_id: int,
    order_id: str,
    page: int = 1,
    size: int = 10,
):
    ...
```

访问：

```http
GET /user/100/order/abc123?page=2&size=20
```

典型分配：

- `user_id` → `100`
- `order_id` → `abc123`
- `page` → `2`
- `size` → `20`

---

## 3. 能不能同名？同名了怎么办？

### 不能在同名上「路径一个、查询一个」

下面这种**在 Python 里就不合法**（重复参数名）：

```python
# 错误示例：不要写两个同名形参
@app.get("/user/{id}")
def get_user(id: int, id: str = Query(None)):  # SyntaxError
    ...
```

正确做法是 **改名**，让路径参数与查询参数各有一个清晰的名字，例如：

- 路径：`user_id`、`order_id`
- 查询：`q`、`page`、`keyword`、`status`

若前端 Query 的名字和 Python 变量名不一致，可用 `Query(..., alias="...")` 或路径侧 `Path(..., alias="...")` 映射。

---

## 超级精简总结（可背诵）

1. **路径参数**：写在 `/xxx/{param}`；类型注解即校验；需要范围/文档等用 `Path(...)`。
2. **查询参数**：写在 `?a=1&b=2`；需要校验/别名/文档等用 `Query(...)`。
3. **混用**：路径参数与查询参数写在同一函数参数列表；FastAPI 自动归类。
4. **同名**：同一函数内形参名必须唯一；需要时用 `alias` 对接外部名字。

---

## 最最核心的一句话

**路径看 URL 里有没有 `{xxx}`，查询看有没有 `?xxx=`；函数里一起写，FastAPI 自动分；形参名不能撞，撞了必错。**
