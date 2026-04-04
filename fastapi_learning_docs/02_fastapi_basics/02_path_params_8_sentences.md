# FastAPI 路径参数（8 句话吃透）

## 1. 路径参数是什么？
URL 里用 `{}` 包起来的变量，比如 `/items/{item_id}`。  
浏览器访问 `/items/123`，`item_id` 就拿到 `123`。

---

## 2. 加类型 `: int` 会发生两件大事
1. **自动类型转换**：`/items/3` → 拿到的是 **int 3**，不是字符串  
2. **自动校验**：`/items/abc` → 直接报错（422），不让进接口  

底层还是 **Pydantic** 在干活。

---
```python
from fastapi import FastAPI

app = FastAPI()

# 加了类型 : int
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

```
    
## 3. 路径顺序非常重要

```python
@app.get("/users/me")
@app.get("/users/{user_id}")
```

**固定路径必须写在动态路径前面**，否则 `/users/me` 可能会被当成 `user_id="me"`。

---

## 4. 想用固定几个值？用 Enum

```python
from enum import Enum


class ModelName(str, Enum):
    resnet = "resnet"
    alexnet = "alexnet"
```

这样路径只能传这几个值，传别的直接报错；文档里还会自动下拉选择。
```python
from enum import Enum
from fastapi import FastAPI

app = FastAPI()

# 1. 定义枚举：继承 str + Enum（关键！）
class ModelName(str, Enum):
    resnet = "resnet"
    alexnet = "alexnet"

# 2. 路径参数用枚举类型标注
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    # 3. 直接用枚举成员判断
    if model_name is ModelName.resnet:
        return {"model": model_name, "msg": "ResNet 深度学习模型"}
    
    # 或用 .value 获取字符串
    if model_name.value == "alexnet":
        return {"model": model_name, "msg": "AlexNet 经典模型"}

    return {"model": model_name}

 ```   
---

## 5. 路径里想传文件路径？用 `:path`

在路径参数后加 :path，告诉 Starlette（FastAPI 底层）：这个参数可以包含斜杠 /，直到 URL 结束FastAPI。

```python
@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    return {"file_path": file_path}
```

可以接收 `/a/b/c.txt` 这种带斜杠的路径。
```python
from fastapi import FastAPI

app = FastAPI()

# 关键：{file_path:path}
@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    return {"file_path": file_path}

```

对比（不加 :path）：

路径：@app.get("/files/{file_path}")
访问 /files/a/b/c.txt → 404 Not Found（因为 /a/b/c.txt 被当成多级路径，找不到路由）

关键细节（必看）

1. 为什么能包含斜杠？

   
普通路径参数（{item_id}）：遇到 / 就停止匹配
:path 参数（{file_path:path}）：匹配到 URL 末尾，允许中间有多个 /FastAPI

注意：不包含开头的 /

访问 /files//home/user/file.txt（双斜杠）
file_path 值为：home/user/file.txt（没有开头的 /）
如果需要绝对路径（/home/user/file.txt），手动拼接：

```python
运行
full_path = f"/{file_path}"
```
---

## 6. 接口可以加标签、说明、弃用标记

```python
@app.get("/xxx", tags=["用户"], deprecated=True)
def xxx():
    return {"ok": True}
```

这些都会显示在 `/docs` 接口文档里。

---

## 7. 这一章的本质
**FastAPI 把 URL 里的参数，自动变成强类型、自动校验、自动注入到函数参数。**  
不用你自己切字符串、判断类型。

---

## 8. 对你以后的用处
后面写 **LangChain + RAG 接口** 时会大量用到：

- `/query/{user_id}`
- `/rag/{document_id}`
- `/model/{model_name}`

一句话总结：  
**路径参数 + 类型注解 = 自动校验 + 自动转换 + 自动文档**  

