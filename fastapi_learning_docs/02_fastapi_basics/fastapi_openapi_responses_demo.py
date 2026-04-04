"""
装饰器 responses={...} 补充 OpenAPI — 对应 21_openapi_responses_parameter.md

运行：
  uvicorn fastapi_openapi_responses_demo:app --reload --app-dir fastapi_learning_docs/02_fastapi_basics

文档：http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="OpenAPI responses= demo")


class Item(BaseModel):
    id: str
    value: str


class Message(BaseModel):
    detail: str


common = {
    403: {"description": "No permission"},
}


@app.get(
    "/items/{item_id}",
    response_model=Item,
    responses={
        **common,
        404: {"model": Message, "description": "Item not found"},
        200: {
            "description": "Item by ID",
            "content": {
                "application/json": {
                    "example": {"id": "foo", "value": "The foo fighters"},
                }
            },
        },
    },
)
async def read_item(item_id: str):
    if item_id == "missing":
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(id=item_id, value="ok")


@app.get("/")
def root():
    return {"docs": "/docs", "try": "GET /items/foo  and  GET /items/missing"}
