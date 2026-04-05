"""
LLM（Tongyi 补全）与 ChatModel（ChatDeepSeek）对比 — 对应 04_llm_chatmodel_usage.md

在仓库根目录执行（便于加载 .env）:
  python langchain-learning-notes/02_langchain_first_experience/demo_llm_chatmodel_compare.py

环境变量（至少配置一个）:
  DEEPSEEK_API_KEY   — ChatDeepSeek
  DASHSCOPE_API_KEY  — 通义 Tongyi（阿里云 DashScope）

依赖: pip install -r requirements.txt（含 langchain-community、langchain-deepseek）
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 从仓库根目录加载 .env
_ROOT = Path(__file__).resolve().parents[2]
try:
    from dotenv import load_dotenv

    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

PROMPT = "用一句话说明：LangChain 里 LLM（字符串）和 ChatModel（消息列表）调用上差在哪？"


def demo_chat_deepseek() -> None:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        print("[ChatDeepSeek] 跳过：未设置环境变量 DEEPSEEK_API_KEY\n")
        return

    from langchain_core.messages import HumanMessage
    from langchain_deepseek import ChatDeepSeek

    chat = ChatDeepSeek(model="deepseek-chat", api_key=key)
    messages = [HumanMessage(content=PROMPT)]
    out = chat.invoke(messages)
    print("[ChatModel / ChatDeepSeek]")
    print("  输入: list[HumanMessage]")
    print("  输出类型:", type(out).__name__)
    print("  内容:", getattr(out, "content", out))
    print()


def demo_tongyi_llm() -> None:
    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        print("[Tongyi LLM] 跳过：未设置环境变量 DASHSCOPE_API_KEY\n")
        return

    try:
        from langchain_community.llms.tongyi import Tongyi
    except ImportError:
        print("[Tongyi LLM] 跳过：未安装 langchain-community（pip install langchain-community）\n")
        return

    llm = Tongyi(api_key=key)
    out = llm.invoke(PROMPT)
    print("[LLM / Tongyi 补全]")
    print("  输入: str")
    print("  输出类型:", type(out).__name__)
    print("  内容:", out)
    print()


def main() -> None:
    os.chdir(_ROOT)
    print("工作目录:", _ROOT)
    print("提示词:", PROMPT)
    print("-" * 60)
    demo_chat_deepseek()
    demo_tongyi_llm()
    if not os.environ.get("DEEPSEEK_API_KEY") and not os.environ.get("DASHSCOPE_API_KEY"):
        print("请至少在 .env 或环境中配置 DEEPSEEK_API_KEY 或 DASHSCOPE_API_KEY 后重试。")
        sys.exit(1)


if __name__ == "__main__":
    main()
