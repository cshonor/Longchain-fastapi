"""
WebSocket Path / Query / Depends — 对应 01_websocket.md 第二节

运行：
  uvicorn fastapi_websocket_auth_demo:app --reload --app-dir fastapi_learning_docs/07_advanced

打开 http://127.0.0.1:8000/ ，填写 item_id、token，点 Connect 后再发消息。
连接 URL 必须带 Query token 或已带 Cookie session（本页未设 Cookie，请填 token）。
"""

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
from fastapi.responses import HTMLResponse

app = FastAPI(title="WebSocket auth demo")

HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>WebSocket Auth</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; }
    input { width: 90%; max-width: 24rem; padding: 0.35rem; margin: 0.25rem 0; display: block; }
    button { margin-top: 0.5rem; padding: 0.4rem 0.8rem; }
    ul { padding-left: 1.2rem; }
  </style>
</head>
<body>
  <h1>WebSocket（Path + Query + Depends）</h1>
  <form onsubmit="connect(event)">
    <label>item_id <input id="itemId" value="foo" /></label>
    <label>token（Query） <input id="token" value="some-key-token" /></label>
    <label>q（可选 Query 整数） <input id="q" placeholder="例如 42" /></label>
    <button type="submit">Connect</button>
  </form>
  <hr />
  <form onsubmit="sendMessage(event)">
    <input id="messageText" placeholder="连接后再发送" />
    <button type="submit">Send</button>
  </form>
  <ul id="messages"></ul>
  <script>
    let ws = null;
    function connect(e) {
      const itemId = document.getElementById("itemId").value;
      const token = document.getElementById("token").value;
      const q = document.getElementById("q").value.trim();
      const proto = location.protocol === "https:" ? "wss:" : "ws:";
      let url = proto + "//" + location.host + "/items/" + encodeURIComponent(itemId) + "/ws?token=" + encodeURIComponent(token);
      if (q) url += "&q=" + encodeURIComponent(q);
      if (ws) ws.close();
      ws = new WebSocket(url);
      ws.onmessage = (ev) => {
        const li = document.createElement("li");
        li.textContent = ev.data;
        document.getElementById("messages").appendChild(li);
      };
      e.preventDefault();
    }
    function sendMessage(e) {
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      const input = document.getElementById("messageText");
      ws.send(input.value);
      input.value = "";
      e.preventDefault();
    }
  </script>
</body>
</html>
"""


async def get_cookie_or_token(
    websocket: WebSocket,
    session: str | None = Cookie(None),
    token: str | None = Query(None),
) -> str:
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE


@app.websocket("/items/{item_id}/ws")
async def websocket_items(
    websocket: WebSocket,
    item_id: str,
    q: int | None = Query(None),
    cookie_or_token: str = Depends(get_cookie_or_token),
):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Token: {cookie_or_token}")
            if q is not None:
                await websocket.send_text(f"q: {q}")
            await websocket.send_text(f"[{item_id}] {data}")
    except WebSocketDisconnect:
        pass
