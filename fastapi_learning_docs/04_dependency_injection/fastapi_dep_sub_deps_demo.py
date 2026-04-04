"""
子依赖与 use_cache — 对应 03_di_sub_dependencies.md

运行：
  uvicorn fastapi_dep_sub_deps_demo:app --reload --app-dir fastapi_learning_docs/04_dependency_injection

文档：http://127.0.0.1:8000/docs

试 Cookie：GET /items/ 不带 q11/q12，请求头加 Cookie: last_query=from_cookie
"""

import random

from fastapi import Cookie, Depends, FastAPI

app = FastAPI(title="Sub-dependencies demo")


def query_extractor(q11: str = "", q12: str = ""):
    """内层：拼接 Query（默认可空，便于演示仅靠 Cookie）。"""
    return q11 + q12


def query_or_cookie_extractor(
    q2: str = Depends(query_extractor),
    last_query: str | None = Cookie(default=None),
):
    return q2 or last_query


@app.get("/items/")
async def read_query(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"q_or_cookie": query_or_default}


def roll() -> float:
    return random.random()


@app.get("/cache-roll/")
def cache_roll(a: float = Depends(roll), b: float = Depends(roll)):
    """同一请求内 roll 只执行一次，a 与 b 相等。"""
    return {"a": a, "b": b, "cached_same": a == b}


@app.get("/no-cache-roll/")
def no_cache_roll(
    a: float = Depends(roll),
    b: float = Depends(roll, use_cache=False),
):
    """第二次不缓存，a 与 b 通常不同。"""
    return {"a": a, "b": b, "usually_different": a != b}


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "try": [
            "/items/?q11=he&q12=llo",
            "/items/  （加 Header Cookie: last_query=only_cookie）",
            "/cache-roll/",
            "/no-cache-roll/",
        ],
    }
