"""
response_class / HTML / PlainText / Redirect / Streaming / FileResponse
对应 20_response_classes.md

运行：
  uvicorn fastapi_response_classes_demo:app --reload --app-dir fastapi_learning_docs/02_fastapi_basics

文档：http://127.0.0.1:8000/docs
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    StreamingResponse,
)

app = FastAPI(title="Response classes demo")

_SAMPLE = Path(__file__).resolve().parent / "response_demo_sample.txt"


@app.get("/html", response_class=HTMLResponse)
async def page():
    return "<h1>Hello HTML</h1>"


@app.get("/text", response_class=PlainTextResponse)
async def plain():
    return "Hello World"


@app.get("/redirect")
async def redir():
    return RedirectResponse("/text")


def _byte_lines():
    for i in range(5):
        yield f"line {i}\n".encode()


@app.get("/stream")
async def stream():
    return StreamingResponse(_byte_lines(), media_type="text/plain")


@app.get("/file", response_class=FileResponse)
async def file():
    return FileResponse(_SAMPLE, filename="sample.txt", media_type="text/plain")


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "try": ["/html", "/text", "/redirect", "/stream", "/file"],
    }
