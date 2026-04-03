"""
Pydantic 复杂 / 嵌套模型 + Field + embed=True — 对应 12_pydantic_complex_nested_models.md

运行：
  uvicorn fastapi_pydantic_complex_demo:app --reload --app-dir fastapi_learning_docs/02_fastapi_basics

文档：http://127.0.0.1:8000/docs

可选：EmailStr 需 pip install email-validator
"""

from pydantic import BaseModel, Field, HttpUrl

from fastapi import Body, FastAPI

app = FastAPI(title="Pydantic complex / nested demo")


class Image(BaseModel):
    url: HttpUrl
    name: str = Field(..., min_length=1, max_length=64)


class Item(BaseModel):
    name: str
    description: str | None = Field(default=None, max_length=300)
    price: float = Field(..., gt=0, description="必须大于 0")
    tax: float | None = None
    tags: list[str] = Field(default_factory=list)
    image: Image | None = None


class Offer(BaseModel):
    name: str
    items: list[Item]


@app.post("/items/")
async def create_item(item: Item):
    return item.model_dump(mode="json")


@app.put("/items/{item_id}")
async def update_item_embed(item_id: int, item: Item = Body(..., embed=True)):
    return {"item_id": item_id, "item": item.model_dump(mode="json")}


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer.model_dump(mode="json")


@app.post("/index-weights/")
async def index_weights(weights: dict[str, float]):
    return weights


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "examples": {
            "POST /items/": {
                "name": "A",
                "price": 9.9,
                "image": {"url": "https://example.com/x.png", "name": "thumb"},
            },
            "PUT /items/1 (embed)": {
                "item": {
                    "name": "B",
                    "price": 1.0,
                }
            },
            "POST /index-weights/": {"w1": 0.2, "w2": 0.8},
        },
    }
