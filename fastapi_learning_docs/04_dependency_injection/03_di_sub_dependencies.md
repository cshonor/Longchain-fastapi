# FastAPI 依赖注入（三）子依赖项

**子依赖**：某个依赖函数的参数里再用 **`Depends(...)`** 引用别的依赖，形成**链式**解析；层数可以很多，FastAPI 会按依赖图**先内后外**依次执行。

（上一篇：[依赖项类](./02_di_class_dependency.md)）

---

## 一、概念

- 依赖里**再依赖**另一个依赖，即「子依赖」。
- 可多层嵌套，深度不限。
- 同一请求内解析顺序由 FastAPI 自动推导。

---

## 二、写法示例

**1. 最内层**（本例从 Query 取两个字符串并拼接）：

```python
def query_extractor(q11: str, q12: str):
    return q11 + q12
```

**2. 外层依赖内层**，并叠加 Cookie：

```python
from fastapi import Cookie

def query_or_cookie_extractor(
    q2: str = Depends(query_extractor),
    last_query: str | None = Cookie(default=None),
):
    return q2 or last_query
```

**3. 路由只声明最外层**：

```python
@app.get("/items/")
async def read_query(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"q_or_cookie": query_or_default}
```

执行顺序：**先** `query_extractor`（满足其参数后得到 `q2`），**再** `query_or_cookie_extractor`。

若希望没有 Query 时只靠 Cookie，需让内层参数可选或带默认值，否则缺少 `q11`/`q12` 会先在校验阶段报错。可运行示例里对 demo 做了可空处理，便于本地试 Cookie。

---

## 三、依赖缓存（同一请求）

- 同一请求中，**同一个依赖可调用对象**若被引用多次，**默认只执行一次**，返回值复用。
- 需要**每次引用都重新执行**时，使用：

```python
Depends(依赖函数, use_cache=False)
```

（可运行示例里用随机数对比「默认缓存」与 `use_cache=False` 的差异。）

---

## 一句话

**子依赖** = 依赖套依赖；FastAPI **按顺序解析**，且**默认在同一请求内缓存**同一依赖的结果。

---

## 可运行示例

见 [`fastapi_dep_sub_deps_demo.py`](./fastapi_dep_sub_deps_demo.py)。
