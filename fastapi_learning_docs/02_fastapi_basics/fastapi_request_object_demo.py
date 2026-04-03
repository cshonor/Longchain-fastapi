"""
注入 Request 读取客户端、头、cookies、原始 body — 对应 17_request_object.md

运行：
  uvicorn fastapi_request_object_demo:app --reload --app-dir fastapi_learning_docs/02_fastapi_basics

文档：http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, Request

app = FastAPI(title="FastAPI Request object demo")


@app.get("/items/{item_id}")
def read_items(item_id: str, request: Request):
    client_host = request.client.host if request.client else None
    return {
        "item_id": item_id,
        "client_host": client_host,
        "path": request.url.path,
        "user_agent": request.headers.get("user-agent"),
    }


@app.post("/raw-body/")
async def raw_body(request: Request):
    body = await request.body()
    return {"length": len(body), "preview": body[:200].decode("utf-8", errors="replace")}


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "try": [
            "GET /items/abc",
            "POST /raw-body/  with raw bytes or JSON body",
        ],
    }
