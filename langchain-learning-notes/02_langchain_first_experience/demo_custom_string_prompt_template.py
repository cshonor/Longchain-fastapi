"""
自定义 StringPromptTemplate（人物 JSON 提示）— 对应 10_custom_string_prompt_template.md

在仓库根目录执行（无需 API Key）:
  python langchain-learning-notes/02_langchain_first_experience/demo_custom_string_prompt_template.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from langchain_core.prompts import StringPromptTemplate
from pydantic import Field, field_validator

_ROOT = Path(__file__).resolve().parents[2]
try:
    from dotenv import load_dotenv

    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

INSTRUCTION = (
    "将每个用户的信息用{delimiter}字符分割，并按照JSON格式提取姓名、职业和爱好信息。"
)


class PersonInfoPromptTemplate(StringPromptTemplate):
    """把人物字段序列化为 JSON 片段并拼在指令后，便于引导模型结构化输出。"""

    delimiter: str = "####"
    input_variables: list[str] = Field(
        default_factory=lambda: ["name", "occupation", "fun_fact"],
    )

    @field_validator("input_variables")
    @classmethod
    def validate_input_variables(cls, v: list[str]) -> list[str]:
        required = {"name", "occupation", "fun_fact"}
        if not required.issubset(set(v)):
            raise ValueError(
                "input_variables 须同时包含 name、occupation、fun_fact 三个键名"
            )
        return v

    def format(self, **kwargs: Any) -> str:
        data = {
            k: "" if kwargs.get(k) is None else kwargs[k] for k in self.input_variables
        }
        head = INSTRUCTION.format(delimiter=self.delimiter)
        return head + json.dumps(data, ensure_ascii=False)


def main() -> None:
    os.chdir(_ROOT)
    tpl = PersonInfoPromptTemplate()
    payload = {
        "name": "张三",
        "occupation": "工程师",
        "fun_fact": "喜欢马拉松",
    }

    print("[1] .format(**payload)")
    print(tpl.format(**payload))
    print()

    print("[2] .invoke(payload) — Runnable，一般为 StringPromptValue，文本在 .text")
    pv = tpl.invoke(payload)
    print(getattr(pv, "text", pv))
    print()

    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        print("[3] PromptTemplate | Tongyi — 跳过：未设置 DASHSCOPE_API_KEY")
        return

    try:
        from langchain_community.llms.tongyi import Tongyi
    except ImportError:
        print("[3] 跳过：未安装 langchain-community")
        return

    llm = Tongyi(api_key=key)
    chain = tpl | llm
    print("[3] 链式调用 tpl | Tongyi（仅演示原始补全，未接 JSON 解析器）")
    out = chain.invoke(payload)
    print(out)


if __name__ == "__main__":
    main()
