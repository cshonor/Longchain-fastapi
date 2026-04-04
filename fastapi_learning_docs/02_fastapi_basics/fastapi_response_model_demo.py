"""
response_model：过滤字段、exclude_unset、include/exclude、Union、list、dict
对应 18_response_model.md

运行：
  uvicorn fastapi_response_model_demo:app --reload --app-dir fastapi_learning_docs/02_fastapi_basics

文档：http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="FastAPI response_model demo")


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5


class UserIn(BaseModel):
    username: str
    password: str
    email: str
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: str
    full_name: str | None = None


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    return user


# 固定路径写在动态 /items/{item_id} 之前，避免与「列表」路径冲突
@app.get("/items/", response_model=list[Item])
async def list_items():
    return [
        Item(name="A", price=1.0),
        Item(name="B", price=2.0, tax=0.0),
    ]


@app.get(
    "/items/{item_id}",
    response_model=Item,
    response_model_exclude_unset=True,
)
async def read_item_unset(item_id: str):
    if item_id == "1":
        return {"name": "Apple", "price": 1.0}
    return Item(name="Box", description="full", price=2.0, tax=10.5)


@app.get(
    "/items/{item_id}/public",
    response_model=Item,
    response_model_include={"name", "description", "price"},
)
async def read_item_include(item_id: str):
    return Item(name="Secret", description="x", price=9.9, tax=99.0)


class BaseThing(BaseModel):
    title: str


class CarItem(BaseThing):
    wheels: int = 4


class PlaneItem(BaseThing):
    wings: int = 2


@app.get("/things/{kind}", response_model=CarItem | PlaneItem)
async def read_thing(kind: str):
    if kind == "car":
        return CarItem(title="Sedan")
    return PlaneItem(title="Jet")


@app.get("/keyword-weights/", response_model=dict[str, float])
async def keyword_weights():
    return {"hello": 0.3, "world": 0.7}


@app.get("/")
def root():
    return {"docs": "/docs"}
