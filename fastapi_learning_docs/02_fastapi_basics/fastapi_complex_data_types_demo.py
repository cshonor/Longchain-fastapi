"""
UUID / datetime / time / timedelta 等复杂类型 — 对应 13_complex_data_types_stdlib.md

思路参考：博客园《FastAPI 基础学习(十一) 复杂数据类型》（麦克煎蛋）

运行：
  uvicorn fastapi_complex_data_types_demo:app --reload --app-dir fastapi_learning_docs/02_fastapi_basics

文档：http://127.0.0.1:8000/docs
"""

from datetime import datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI(title="FastAPI complex stdlib types demo")


@app.put("/items/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: datetime | None = Body(default=None),
    end_datetime: datetime | None = Body(default=None),
    repeat_at: time | None = Body(default=None),
    process_after: timedelta | None = Body(default=None),
):
    if start_datetime is None or end_datetime is None or process_after is None:
        return {
            "item_id": str(item_id),
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "repeat_at": repeat_at,
            "process_after": process_after,
            "start_process": None,
            "duration": None,
        }
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": str(item_id),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


class PriceIn(BaseModel):
    amount: Decimal


@app.post("/price/")
async def post_decimal(p: PriceIn):
    return {"amount": p.amount, "type": type(p.amount).__name__}


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "try_put_items": {
            "item_id": "550e8400-e29b-41d4-a716-446655440000",
            "body": {
                "start_datetime": "2008-09-15T10:00:00",
                "end_datetime": "2008-09-15T18:00:00",
                "repeat_at": "14:23:55",
                "process_after": 3600,
            },
        },
        "note": "process_after 在 JSON 中常以秒数等形式传入；以 /docs 中 Schema 为准",
    }
