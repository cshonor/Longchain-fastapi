"""
模块化 Prompt（客服 / 代码两场景，同一 ChatPromptTemplate 骨架）— 对应 11_modular_prompts.md

无需 API Key。在仓库根目录执行:
  python langchain-learning-notes/02_langchain_first_experience/demo_modular_prompts.py
"""

from __future__ import annotations

import os
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

_ROOT = Path(__file__).resolve().parents[2]
try:
    from dotenv import load_dotenv

    load_dotenv(_ROOT / ".env")
except ImportError:
    pass


def build_agent_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{system_rules}\n\n"
                "你是一个智能助手；在需要时使用提供的工具，回答简洁、不要编造事实。",
            ),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad", optional=True),
        ]
    )


def print_messages(title: str, tmpl: ChatPromptTemplate, **kwargs) -> None:
    msgs = tmpl.format_messages(**kwargs)
    print(title)
    for i, m in enumerate(msgs):
        print(f"  [{i}] {type(m).__name__}: {m.content!r}")
    print()


def main() -> None:
    os.chdir(_ROOT)
    base = build_agent_prompt()

    customer = base.partial(
        system_rules="你现在是电商客服，优先处理订单查询、物流与售后。",
    )
    coder = base.partial(
        system_rules="你现在是代码助手，优先给出可运行的 Python，并简短说明思路。",
    )

    history = [
        HumanMessage(content="你好"),
        AIMessage(content="您好，需要什么帮助？"),
    ]

    print("工作目录:", _ROOT)
    print("-" * 60)
    print_messages(
        "[1] 客服场景（同一骨架，partial 绑定 system_rules）",
        customer,
        input="我的订单什么时候发货？单号 SF123。",
        chat_history=history,
        agent_scratchpad=[],
    )
    print_messages(
        "[2] 代码场景（只换 partial，消息结构不变）",
        coder,
        input="用 Python 读一个 CSV 并打印前 5 行。",
        chat_history=[],
        agent_scratchpad=[],
    )


if __name__ == "__main__":
    main()
