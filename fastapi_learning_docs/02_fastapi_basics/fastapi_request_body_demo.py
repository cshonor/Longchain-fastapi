"""
Request Body（Pydantic BaseModel）示例，对应 07_request_body.md。

运行：
  uvicorn fastapi_request_body_demo:app --reload --app-dir fastapi_learning_docs/02_fastapi_basics

文档：http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Request Body demo")


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.post("/items/")
async def create_item(item: Item):
    return item


@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    q: str | None = None,
):
    return {
        "item_id": item_id,
        "q": q,
        "name": item.name,
        "price": item.price,
        "as_dict": item.model_dump(),
    }


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "try_post_items": {
            "url": "POST /items/",
            "body": {
                "name": "Apple",
                "description": "red",
                "price": 1.5,
                "tax": 0.1,
            },
        },
        "try_put": "PUT /items/42?q=debug  + JSON body same as above",
    }
