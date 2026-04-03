# FastAPI 复杂数据类型（UUID、日期时间、Decimal 等）

除 `int`、`float`、`str`、`bool` 外，路径参数、Query、Body 里也可以直接使用 **Python 标准库类型**，仍由 **Pydantic** 做解析与校验，并进入 OpenAPI 文档。  
（与 [Pydantic 复杂 / 嵌套模型](./12_pydantic_complex_nested_models.md) 互补：本节侧重 **stdlib 特殊类型** 在请求/响应里的表现。）

---

## 常见类型速览

| 类型 | 说明 | JSON / 请求体中常见形态（概念上） |
|------|------|-------------------------------------|
| `UUID` | 通用唯一标识 | 字符串，如 `"550e8400-e29b-41d4-a716-446655440000"` |
| `datetime.datetime` | 日期时间 | ISO 8601 字符串，如 `"2008-09-15T15:53:00+05:00"` |
| `datetime.date` | 日期 | 字符串，如 `"2008-09-15"` |
| `datetime.time` | 一天内时间 | 字符串，如 `"14:23:55.003"` |
| `datetime.timedelta` | 时间间隔 | 序列化时通常体现为**一段时间**（具体表示以 Pydantic 版本为准；常见为总秒数等数值形式） |
| `frozenset` | 不可变集合 | 与 `set` 类似；请求中可由列表去重得到，响应中常序列化为列表 |
| `bytes` | 字节串 | 常按**字符串**（如 Base64）等形式在 JSON 中传输，依配置与版本而定 |
| `Decimal` | 十进制数 | JSON 无原生 Decimal，通常以**数字**形式与 `float` 互通呈现 |

具体 Schema、错误信息与序列化细节以**当前 FastAPI + Pydantic 版本文档**为准。

---

## 路径 `UUID` + Body 里多个可选字段（示例）

下面示例与常见教程写法一致：`item_id` 来自路径；其余字段来自 **JSON Body**（多个 `Body` 参数时，根对象上多 key 对应各参数名）。

```python
from datetime import datetime, time, timedelta
from uuid import UUID

from fastapi import Body, FastAPI

app = FastAPI()


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
```

---

## 参考来源

- 麦克煎蛋：《FastAPI 基础学习(十一) 复杂数据类型》，博客园  
  https://www.cnblogs.com/mazhiyong/

转载说明尊重原作者；本文已按 **Pydantic v2 / 现代类型注解** 做了写法整理与示例防护（避免对 `None` 直接做时间运算）。

---

## 可运行示例

见 [`fastapi_complex_data_types_demo.py`](./fastapi_complex_data_types_demo.py)。
