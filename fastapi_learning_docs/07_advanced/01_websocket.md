# FastAPI WebSocket 核心用法

WebSocket 在单条 TCP 连接上提供全双工通信，适合聊天、推送、实时行情。FastAPI 通过装饰器注册 WebSocket 路由，参数类型为 `WebSocket`（底层 Starlette）。

可选对比：HTTP 请求与 [中间件](../03_response_middleware/01_custom_http_middleware.md)。

---

## 一、基础 echo

1. `await websocket.accept()`：完成握手后才能收发。  
2. 循环中使用 `receive_text` / `send_text`（或 `receive_bytes` / `send_bytes`）。  
3. 浏览器使用 `new WebSocket(url)`；页面是 HTTPS 时需 `wss://`。

客户端断开时，`receive_*` 会抛出 **`WebSocketDisconnect`**，应捕获并结束处理。

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


@app.websocket("/ws")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        pass
```

---

## 二、Path、Query、Cookie、Depends

可与普通路由一样使用**路径参数**、**Query**、**Cookie**、**Header**；也可用 **`Depends`** 做鉴权。

拒绝连接时，在 **`accept` 之前**使用 **`raise WebSocketException(code=...)`**，避免依赖标注为 `str` 却未返回的情况。

```python
from fastapi import Cookie, Depends, Query, WebSocket, WebSocketException, status

async def get_cookie_or_token(
    websocket: WebSocket,
    session: str | None = Cookie(None),
    token: str | None = Query(None),
) -> str:
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@app.websocket("/items/{item_id}/ws")
async def websocket_items(
    websocket: WebSocket,
    item_id: str,
    q: int | None = Query(None),
    cookie_or_token: str = Depends(get_cookie_or_token),
):
    await websocket.accept()
    ...
```

前端 URL 建议用 **`ws:`** / **`wss:`** 与 **`location.host`** 拼接，避免写死 `localhost`。

---

## 三、常用 API 速记

| 调用 | 作用 |
|------|------|
| `await websocket.accept()` | 接受握手 |
| `await websocket.receive_text()` | 接收文本 |
| `await websocket.send_text(s)` | 发送文本 |
| `await websocket.receive_bytes()` | 接收二进制 |
| `await websocket.send_bytes(b)` | 发送二进制 |
| `await websocket.close(code=...)` | 主动关闭 |
| `raise WebSocketException(code=...)` | 握手阶段拒绝（如策略违规 1008） |

---

## 可运行示例

- [基础 echo + 单页 HTML](./fastapi_websocket_echo_demo.py)  
- [Path / Query / Depends 鉴权 + HTML](./fastapi_websocket_auth_demo.py)

```bash
uvicorn fastapi_websocket_echo_demo:app --reload --app-dir fastapi_learning_docs/07_advanced
```

---

内容整理自博客园「麦克煎蛋」等 FastAPI WebSocket 教程，按当前版本补充 `WebSocketException` 与 `WebSocketDisconnect`。
