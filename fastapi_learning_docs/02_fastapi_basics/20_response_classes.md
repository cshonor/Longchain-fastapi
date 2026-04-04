# FastAPI 定制化 Response（response_class）

默认返回 dict 或 Pydantic 模型时，会走 JSON 序列化（等价于 JSONResponse 路径）。

你可以用 **response_class** 指定整条路由的响应类型，也常可配合 **response_model**（见 [18](./18_response_model.md)）。直接 **return Response(...)** 则完全手写，见 [19](./19_direct_return_response.md)。

---

## 一、Response 基类常用参数

- content：str 或 bytes
- status_code
- headers
- media_type（如 text/html、application/xml）

```python
from fastapi import Response

return Response(content=data, media_type="application/xml")
```

---

## 二、常用内置 Response

### HTMLResponse

```python
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def main():
    return "<h1>Hello HTML</h1>"
```

### PlainTextResponse

```python
from fastapi.responses import PlainTextResponse

@app.get("/text", response_class=PlainTextResponse)
async def plain():
    return "Hello World"
```

### JSONResponse

显式 JSON；手动构造时可配合 jsonable_encoder（见 19）。

### RedirectResponse

默认 307；可改 status_code 为 302 等。

```python
from fastapi.responses import RedirectResponse

@app.get("/go")
async def go():
    return RedirectResponse("/text")
```

### StreamingResponse

大文件、分块、生成器。

```python
from fastapi.responses import StreamingResponse

def gen_bytes():
    for i in range(5):
        yield f"line {i}\n".encode()

@app.get("/stream")
async def stream():
    return StreamingResponse(gen_bytes(), media_type="text/plain")
```

### FileResponse

从磁盘路径返回文件；路径须存在。

```python
from fastapi.responses import FileResponse

@app.get("/file")
async def file():
    return FileResponse("path/to/file.txt")
```

---

## 三、全局 default_response_class（ORJSONResponse）

需安装 **orjson**：

```python
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(default_response_class=ORJSONResponse)
```

---

## 四句话

1. response_class 统一本条路由的响应外壳类型。  
2. 手写 Response 完全自控（见 19）。  
3. 常用：HTML、纯文本、重定向、流式、文件。  
4. 全局可换 ORJSONResponse（需 orjson）。

---

## Demo

[fastapi_response_classes_demo.py](./fastapi_response_classes_demo.py) 与 [response_demo_sample.txt](./response_demo_sample.txt)。
