"""
LCEL：ChatPromptTemplate | ChatDeepSeek | OutputParser — 对应 07_lcel.md

在仓库根目录执行:
  python langchain-learning-notes/02_langchain_first_experience/demo_lcel.py

需环境变量: DEEPSEEK_API_KEY

演示:
  [1] chain.invoke — 完整链，输出 list[str]
  [2] (chat_prompt | chat).stream — 仅模型段流式打印 token 块
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


def build_chain():
    from langchain_core.output_parsers import CommaSeparatedListOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_deepseek import ChatDeepSeek

    parser = CommaSeparatedListOutputParser()
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一个生成逗号分隔列表的助手。用户会传入一个类别，请生成该类别下 5 个简短中文名字。"
                "只输出逗号分隔的文本，不要编号、不要解释。\n\n"
                f"{parser.get_format_instructions()}",
            ),
            ("human", "{text}"),
        ]
    )
    chat = ChatDeepSeek(
        model="deepseek-chat",
        api_key=os.environ["DEEPSEEK_API_KEY"],
    )
    full = chat_prompt | chat | parser
    gen_only = chat_prompt | chat
    return full, gen_only, parser


def main() -> None:
    os.chdir(_ROOT)
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        print("请配置 DEEPSEEK_API_KEY（.env 或环境变量）后重试。")
        print("对应笔记: langchain-learning-notes/02_langchain_first_experience/07_lcel.md")
        sys.exit(1)

    full_chain, gen_only, parser = build_chain()
    inputs = {"text": "动物"}

    print("工作目录:", _ROOT)
    print("-" * 60)
    print("[1] LCEL 完整链: chat_prompt | ChatDeepSeek | CommaSeparatedListOutputParser")
    print("    invoke 输入:", inputs)
    result = full_chain.invoke(inputs)
    print("    输出类型:", type(result).__name__)
    print("    输出:", result)
    print()

    print("[2] 流式: 仅 (chat_prompt | chat).stream（解析器在流结束后才能可靠 parse）")
    print("    流式片段:", end=" ", flush=True)
    buffer = ""
    for chunk in gen_only.stream(inputs):
        # ChatModel 流式一般为 AIMessageChunk
        piece = getattr(chunk, "content", chunk)
        if piece:
            print(piece, end="", flush=True)
            buffer += piece if isinstance(piece, str) else str(piece)
    print("\n")
    if buffer.strip():
        parsed = parser.parse(buffer)
        print("    对拼接全文再 parse 的结果:", parsed)
    print()


if __name__ == "__main__":
    main()
