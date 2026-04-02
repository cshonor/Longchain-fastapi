"""
Query 请求参数（对应笔记 06_query_params.md）。

运行（任选其一）：
  在项目根目录 longchain/ 下：
    uvicorn fastapi_query_params_demo:app --reload --app-dir fastapi_learning_docs/02_fastapi_basics
  或先进入本目录再启动：
    cd fastapi_learning_docs/02_fastapi_basics
    uvicorn fastapi_query_params_demo:app --reload

文档：http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

app = FastAPI(
    title="Query params demo",
    description="Optional defaults, optional None, required query, path + query mix.",
)


# --- 带默认值：不传则用 skip=0、limit=10 ---
@app.get("/items")
def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


# --- 可选 Query：q 可省略 ---
@app.get("/search")
def search(q: str | None = None):
    return {"q": q}


# --- 必传 Query：不传 needy → 422 ---
@app.get("/need")
def need_query(needy: str):
    return {"needy": needy}


# --- 路径参数 + Query 混用（与笔记示例一致）---
@app.get("/users/{user_id}/items/{item_id}")
def read_user_item(
    user_id: int,
    item_id: str,
    q: str | None = None,
    short: bool = False,
):
    return {
        "user_id": user_id,
        "item_id": item_id,
        "q": q,
        "short": short,
    }


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "try": [
            "GET /items",
            "GET /items?skip=20&limit=5",
            "GET /search",
            "GET /search?q=hello",
            "GET /need?needy=must-pass   # omit needy → 422",
            "GET /users/1/items/foo?q=bar&short=true",
        ],
    }
