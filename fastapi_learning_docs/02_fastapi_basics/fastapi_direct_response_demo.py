"""
直接返回 JSONResponse / Response — 对应 19_direct_return_response.md

运行：
  uvicorn fastapi_direct_response_demo:app --reload --app-dir fastapi_learning_docs/02_fastapi_basics

文档：http://127.0.0.1:8000/docs
"""

from datetime import datetime

from fastapi import FastAPI, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Direct Response demo")


class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


@app.put("/items/{item_id}")
def update_item(item_id: str, item: Item):
    payload = {"item_id": item_id, "item": jsonable_encoder(item)}
    return JSONResponse(content=payload)


@app.get("/legacy/")
def get_legacy_data():
    xml_data = """<?xml version="1.0"?>
<shampoo>
  <Header>Apply shampoo here.</Header>
  <Body>You'll have to use soap here.</Body>
</shampoo>
"""
    return Response(content=xml_data.encode("utf-8"), media_type="application/xml")


@app.get("/")
def root():
    return {"docs": "/docs"}
