# FastAPI 依赖注入（二）依赖项类

**核心点**：依赖项**不必是函数**，只要是**可调用**即可。类名本身可调用（`类名(...)` 得到实例），因此可以把**类**当作依赖项；FastAPI 会像调用函数一样，用请求参数去填 **`__init__`**。

（上一篇：[依赖注入简介](./01_di_introduction.md)）

---

## 一、从函数依赖到类依赖

### 函数依赖（回顾）

```python
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}
```

### 类依赖

把原来函数参数挪到 **`__init__`**，解析规则与 Query 等一致：

```python
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit
```

路由里拿到的 `commons` 是 **`CommonQueryParams` 实例**，用属性访问即可。

---

## 二、在路由中使用

```python
@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    response = {}
    if commons.q:
        response["q"] = commons.q

    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response["items"] = items
    return response
```

### 简写（更常用）

类型注解已经写明是 `CommonQueryParams` 时，可写 **`Depends()`**，由注解推断要实例化的类：

```python
async def read_items(commons: CommonQueryParams = Depends()):
    ...
```

---

## 三、为什么用类？

- **结构清晰**：参数是对象属性，比散落字典键名更直观。  
- **可扩展**：可在类上加方法，封装校验、计算或与存储交互。  
- **类型安全**：IDE 与类型检查能跟上，少写错字段名。

---

## 一句话

**函数依赖** → 返回值当参数用；**类依赖** → **先构造实例**再注入，更适合稍复杂、可带行为的公共逻辑。

---

## 可运行示例

见 [`fastapi_dep_class_demo.py`](./fastapi_dep_class_demo.py)。
