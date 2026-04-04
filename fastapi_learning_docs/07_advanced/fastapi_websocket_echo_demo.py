"""
WebSocket 基础 echo — 对应 01_websocket.md 第一节

运行：
  uvicorn fastapi_websocket_echo_demo:app --reload --app-dir fastapi_learning_docs/07_advanced

浏览器打开 http://127.0.0.1:8000/ ，输入文字发送即可看到回显。
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="WebSocket echo demo")

HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>WebSocket Echo</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 36rem; margin: 2rem auto; }
    input { width: 70%; padding: 0.4rem; }
    button { padding: 0.4rem 0.8rem; }
    ul { padding-left: 1.2rem; }
  </style>
</head>
<body>
  <h1>WebSocket Echo</h1>
  <form onsubmit="sendMessage(event)">
    <input type="text" id="messageText" autocomplete="off" placeholder="输入后回车或点发送" />
    <button type="submit">Send</button>
  </form>
  <ul id="messages"></ul>
  <script>
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(proto + "//" + location.host + "/ws");
    ws.onmessage = function (event) {
      const li = document.createElement("li");
      li.textContent = event.data;
      document.getElementById("messages").appendChild(li);
    };
    function sendMessage(event) {
      const input = document.getElementById("messageText");
      ws.send(input.value);
      input.value = "";
      event.preventDefault();
    }
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE


@app.websocket("/ws")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        pass
