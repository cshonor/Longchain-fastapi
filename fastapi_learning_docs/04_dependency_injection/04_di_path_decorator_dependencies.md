# FastAPI 依赖注入（四）路径装饰器依赖

在 **`@app.get` / `@app.post` 等装饰器**上通过 **`dependencies=[Depends(...), ...]`** 声明依赖：依赖会**照常执行**（校验失败会中断请求），但**返回值不会注入**到路由函数参数里。

适用场景：**不需要依赖返回值**，只要**副作用**或前置条件，例如鉴权、配额、写日志；又不想在函数签名里多写几个形参。

（上一篇：[子依赖项](./03_di_sub_dependencies.md)）

---

## 一、使用方式

```python
from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()


async def verify_token(x_token: str = Header(...)):
    if x_token != "token":
        raise HTTPException(status_code=400, detail="无效token")


async def verify_key(x_key: str = Header(...)):
    if x_key != "key":
        raise HTTPException(status_code=400, detail="无效key")


@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]
```

---

## 二、特点

- 依赖**按列表顺序**执行；任一依赖 `raise` 或校验失败，路由函数体**不会执行**。  
- 路由函数**拿不到**这些依赖的返回值，适合「只执行、不消费结果」的检查。  
- 常见用途：登录态、权限、审计日志、限流等。

---

## 一句话

**装饰器上的 `dependencies`** = **只跑前置逻辑、不把结果塞进路由参数**的全局（本路由）依赖。

---

## 可运行示例

见 [`fastapi_dep_path_decorator_demo.py`](./fastapi_dep_path_decorator_demo.py)。
