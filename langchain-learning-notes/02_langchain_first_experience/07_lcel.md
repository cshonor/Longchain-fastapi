# LangChain 核心笔记：LCEL 组件组合

## 一、核心概述：什么是 LCEL？

**LCEL**（LangChain Expression Language）是 LangChain 提供的**声明式组合语法**。

**一句话**：用 **`|`** 把实现了 **`Runnable`** 的组件（提示词、模型、解析器等）按顺序接成**一条可执行链路**，输入字典（或单值），得到最终输出。

### 它解决什么问题？

- **写法简单**：少写层层嵌套的手动调用，常见形态一行：`chain = prompt | llm | parser`。
- **接口统一**：链上的每一步都支持相同的 Runnable 调用方式（见下文）。
- **能力齐全**：同一条链上可配合 **流式**、**批量**、**异步** 等（视具体 Runnable 实现而定）。

与 [环境 & 核心概念](./01_env_and_core_concepts.md) 中的 LCEL 引言、[Prompt 模板](./05_prompt_template.md)、[Output Parser](./06_output_parser.md) 衔接阅读。

---

## 二、典型代码：`ChatPromptTemplate | ChatModel | OutputParser`

下面与教程思路一致：**对话模板 → ChatDeepSeek → 逗号列表解析器**。

注意：`BaseOutputParser` 的 **`invoke` 既可接字符串，也可接 `AIMessage`**，因此 **`chat | parser` 类型上是成立的**。

```python
import os

from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek

parser = CommaSeparatedListOutputParser()

chat_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个生成逗号分隔列表的助手。用户会传入一个类别，请生成该类别下 5 个简短名字。"
            "只输出逗号分隔的文本，不要编号、不要解释。\n\n"
            + parser.get_format_instructions(),
        ),
        ("human", "{text}"),
    ]
)

chat = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
)

chain = chat_prompt | chat | parser

if __name__ == "__main__":
    result = chain.invoke({"text": "动物"})
    print(result)  # 期望得到 list[str]，如 ['狗', '猫', ...]
```

### 自定义解析器（教学）

若教程里用**继承 `BaseOutputParser`** 的写法，建议对每个元素 **`strip()`**，避免 `"狗, 猫"` 拆出带空格的项：

```python
from langchain_core.output_parsers import BaseOutputParser


class CommaListParser(BaseOutputParser[list[str]]):
    def parse(self, text: str) -> list[str]:
        return [item.strip() for item in text.strip().split(",") if item.strip()]
```

日常开发可优先用内置的 **`CommaSeparatedListOutputParser`**（对引号、逗号边界更稳妥），见 [06_output_parser.md](./06_output_parser.md)。

### 语法要点：`|`

- **含义**：前一步的输出作为后一步的输入（Runnable 管道）。
- **顺序**：`提示模板 → 模型 → 解析器` 时，模型产出文本或消息，解析器再结构化。
- **补全 LLM**：字符串链路更直观：`PromptTemplate | Tongyi | parser`，见 [05](./05_prompt_template.md)、[06](./06_output_parser.md)。

---

## 三、为什么要用 LCEL？

### 1. 组合清晰

用表达式描述**数据流**，而不是在业务函数里手写「先 format、再 invoke、再 parse」。

### 2. Runnable 统一接口

链中各环节（及整条链本身）都实现 **`Runnable`**，常用方法包括：

| 方法 | 用途 |
| :--- | :--- |
| **`invoke`** | 单次同步调用（最常用） |
| **`stream`** | 流式输出（逐块产出，适合长文本与对话感） |
| **`batch`** | 对多个输入批量跑同一条链 |
| **`ainvoke` / `astream` / `abatch`** | 异步版本 |

### 3. 声明式

强调**接什么组件、什么顺序**；具体调度由框架完成，便于阅读与维护。

---

## 四、与前面笔记的衔接

| 组件 | 在链中的角色 | 作用 |
| :--- | :--- | :--- |
| **`PromptTemplate` / `ChatPromptTemplate`** | 起点 | 把变量渲染成字符串或消息列表 |
| **`LLM` / `ChatModel`** | 中间层 | 生成原始补全或 `AIMessage` |
| **`OutputParser`** | 后处理 | 把模型输出变成 `list` / `dict` 等 |

**常见公式**：

- 补全：**`PromptTemplate | LLM | OutputParser`**
- 对话：**`ChatPromptTemplate | ChatModel | OutputParser`**（解析器需能处理上一步输出；`BaseOutputParser` 已支持从消息中取文本）

类型对齐仍见 [05_prompt_template.md](./05_prompt_template.md)：**不要用 `ChatPromptTemplate` 去接补全型 `Tongyi`（字符串 LLM）**。

---

## 五、流式输出说明

- **整条链** `prompt | chat | parser`：解析器往往在**收到完整模型输出**后才好解析，因此**流式语义**主要体现在「模型段」上。
- **实践**：常用 **`generation = chat_prompt | chat`**，对 `generation.stream({...})` 循环打印 **`AIMessageChunk.content`**；最终需要结构化结果时，再对**完整文本**调用一次 `parser.parse(...)`，或继续用完整 **`invoke`** 走 `chain`。

可运行示例见：[demo_lcel.py](./demo_lcel.py)。

---

## 六、总结

LCEL 的价值在于：用 **`prompt | llm | parser`** 这类表达式，把「提示 → 模型 → 解析」固定成**统一、可组合、可扩展**的工程结构，而不是散落在各处的字符串拼接与临时函数。

---

## 延伸阅读

- [部署与可观测性（LangServe / LangSmith）](./08_deployment_and_observability.md)
- [基础链三要素 & 模块](./02_basic_chain_and_modules.md)
- [LLM / ChatModel](./04_llm_chatmodel_usage.md)
- [Prompt 与 LCEL](./05_prompt_template.md)
- [Output Parser](./06_output_parser.md)
