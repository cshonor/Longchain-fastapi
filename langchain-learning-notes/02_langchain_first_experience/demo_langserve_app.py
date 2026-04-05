"""
LangServe：把 LCEL 链暴露为 HTTP API — 对应 08_deployment_and_observability.md

依赖: pip install langserve fastapi uvicorn（见项目 requirements.txt）

在仓库根目录执行:
  python langchain-learning-notes/02_langchain_first_experience/demo_langserve_app.py

环境变量:
  DEEPSEEK_API_KEY — 必填，供 ChatDeepSeek 调用

可选（LangSmith 追踪）:
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=...
  LANGCHAIN_PROJECT=longchain-notes

启动后:
  文档: http://127.0.0.1:8000/docs
  调用: POST http://127.0.0.1:8000/chain/invoke
  请求体示例: {"input": {"text": "动物"}}
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
try:
    from dotenv import load_dotenv

    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

try:
    from fastapi import FastAPI
    from langchain_core.output_parsers import CommaSeparatedListOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_deepseek import ChatDeepSeek
    from langserve import add_routes
except ImportError:
    print("缺少依赖，请执行: python -m pip install langserve langchain-deepseek fastapi uvicorn")
    sys.exit(1)


def build_app() -> FastAPI:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        print("请配置 DEEPSEEK_API_KEY（.env 或环境变量）。")
        sys.exit(1)

    parser = CommaSeparatedListOutputParser()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一个能生成逗号分隔列表的助手。只输出列表，不要多余说明。\n\n"
                + parser.get_format_instructions(),
            ),
            ("human", "{text}"),
        ]
    )
    chat = ChatDeepSeek(model="deepseek-chat", api_key=key)
    chain = prompt | chat | parser

    app = FastAPI(title="第一个 LangChain 应用", version="0.1.0")
    add_routes(app, chain, path="/chain")
    return app


app = build_app()


if __name__ == "__main__":
    import uvicorn

    os.chdir(_ROOT)
    print("工作目录:", _ROOT)
    print("OpenAPI: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
