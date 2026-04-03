"""
路径参数 + 查询参数 + Path / Query 校验 — 对应 10_path_and_query_mix.md

运行：
  uvicorn fastapi_path_query_mix_demo:app --reload --app-dir fastapi_learning_docs/02_fastapi_basics

文档：http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, Path, Query

app = FastAPI(title="Path + Query mix demo")


@app.get("/user/{user_id}")
def get_user(
    user_id: int = Path(..., gt=0, le=1000, description="User id in path"),
):
    return {"user_id": user_id}


@app.get("/user/{user_id}/order/{order_id}")
def get_order(
    user_id: int,
    order_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    q: str | None = Query(None, description="Optional keyword"),
):
    return {
        "user_id": user_id,
        "order_id": order_id,
        "page": page,
        "size": size,
        "q": q,
    }


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "try": [
            "GET /user/42",
            "GET /user/0   # 422 if gt=0 violated",
            "GET /user/1001   # 422 if le=1000 violated",
            "GET /user/1/order/abc123?page=2&size=20&q=test",
        ],
    }
