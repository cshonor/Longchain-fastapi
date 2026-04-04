"""
类作为依赖项 — 对应 02_di_class_dependency.md

运行：
  uvicorn fastapi_dep_class_demo:app --reload --app-dir fastapi_learning_docs/04_dependency_injection

文档：http://127.0.0.1:8000/docs
"""

from fastapi import Depends, FastAPI

app = FastAPI(title="Class dependency demo")

fake_items_db = [{"item_id": i, "name": f"Item {i}"} for i in range(100)]


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends()):
    response: dict = {}
    if commons.q:
        response["q"] = commons.q

    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response["items"] = items
    return response


@app.get("/items-explicit/")
async def read_items_explicit(commons: CommonQueryParams = Depends(CommonQueryParams)):
    """与 /items/ 等价，显式传入类名。"""
    return await read_items(commons)


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "try": ["/items/?skip=0&limit=5&q=foo", "/items-explicit/?skip=0&limit=3"],
    }
