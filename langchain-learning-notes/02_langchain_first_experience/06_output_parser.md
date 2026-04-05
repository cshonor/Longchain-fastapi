# 输出解析器（Output Parser）

## 一、这页在讲什么？

**输出解析器**负责把模型返回的**原始文本**，转成程序里好用的**结构化数据**（`list`、`dict`、Pydantic 模型等）。

与 [PromptTemplate / LCEL](./05_prompt_template.md) 组合时，典型形态是：

```text
prompt | llm | parser
```

---

## 二、能解决什么问题？

- 模型输出是字符串，例如 `"杯语, 暖杯坊, 水韵"`，不能直接当 `list` 用。  
- 解析器把「字符串 → 列表 / JSON / 对象」的规则**单独封装**，业务代码只拿结构化结果。

---

## 三、`BaseOutputParser` 与 `parse()`

- **`BaseOutputParser`**：基类，继承后实现 **`parse(self, text: str) -> T`** 即可定义自己的解析规则。  
- 框架会把 LLM 的字符串（或消息里的文本）交给 **`parse_result` → `parse`**；在链里 **`parser` 也是 Runnable**，可 **`invoke`**，故能接在 `llm` 后面。  
- 要解析 JSON，可在 `parse()` 里 `json.loads()`；要解析逗号分隔，可 `split(",")` 并 **`strip()`** 每一项。

**自定义示例（教学用，逻辑直观）：**

```python
from langchain_core.output_parsers import BaseOutputParser


class CommaSeparatedListOutputParser(BaseOutputParser[list[str]]):
    """将模型输出解析为逗号分隔的字符串列表（教学示例）。"""

    def parse(self, text: str) -> list[str]:
        return [item.strip() for item in text.strip().split(",") if item.strip()]
```

**生产环境**：`langchain_core.output_parsers` 里已有 **`CommaSeparatedListOutputParser`**，内部用 `csv` 处理引号、空格等边界情况，并带 **`get_format_instructions()`** 可写进提示词，让模型更守格式。

---

## 四、教程代码里常见的一处混用（勘误）

有的示例会写：

```python
from langchain_community.llms.tongyi import Tongyi
from langchain_core.messages import HumanMessage

llm = Tongyi()
messages = [HumanMessage(content=text)]
# ...
llms_response = llm.invoke(text)  # 实际走的是字符串
```

**`Tongyi` 属于补全类 LLM**，`invoke` 的输入应是**字符串**（或 PromptValue），**不是** `HumanMessage` 列表。  
若要用消息列表，应换 **ChatModel**（如 `ChatTongyi` / `ChatDeepSeek`）并配合 **`ChatPromptTemplate`**，见 [LLM / ChatModel](./04_llm_chatmodel_usage.md)。

下面示例统一用：**字符串提示 + `Tongyi` + 解析器**。

---

## 五、分步调用 vs 链式调用

### 1. 先调模型，再 `parse`

```python
import os

from langchain_community.llms.tongyi import Tongyi
from langchain_core.output_parsers import CommaSeparatedListOutputParser

llm = Tongyi(api_key=os.environ["DASHSCOPE_API_KEY"])
parser = CommaSeparatedListOutputParser()

prompt = "给生产杯子的公司取三个合适的中文名字，以英文逗号分隔输出，不要编号或其它说明。"
raw = llm.invoke(prompt)
names = parser.parse(raw)
```

### 2. `PromptTemplate | LLM | parser`（推荐）

**补全 LLM** 输出字符串，与 **`PromptTemplate`**、**`BaseOutputParser` 子类**类型一致，可直接管道：

```python
import os

from langchain_community.llms.tongyi import Tongyi
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate

parser = CommaSeparatedListOutputParser()
prompt = PromptTemplate.from_template(
    "{format_instructions}\n\n产品：{product}。请给出 3 个简短的中文公司名，逗号分隔。"
)
llm = Tongyi(api_key=os.environ["DASHSCOPE_API_KEY"])

chain = prompt | llm | parser
names = chain.invoke(
    {
        "format_instructions": parser.get_format_instructions(),
        "product": "保温杯",
    }
)
# names 为 list[str]
```

**类型对齐**：`ChatPromptTemplate` → 消息列表 → 接 **ChatModel**；若再接解析器，模型侧通常先用 **`StrOutputParser`** 得到字符串，再接 JSON 等解析器（视版本与封装而定）。入门阶段记住：**字符串链路用 `PromptTemplate | LLM | parser` 最直观**。

---

## 六、其它常见解析器（了解即可）

- **`StrOutputParser`**：把 **ChatModel** 的 `AIMessage` 等转成纯字符串，常用于 `chat | StrOutputParser()`。  
- **`JsonOutputParser`** / **`PydanticOutputParser`**：约束输出为 JSON 或 Pydantic 模型（需提示词配合格式说明）。

---

## 七、核心优势（小结）

- **解耦**：解析规则独立，可单测、可复用。  
- **接链**：与 **`prompt | llm | parser`** 一致，和 LangChain Runnable 生态对齐。

---

## 延伸阅读

- [PromptTemplate / ChatPromptTemplate 与 LCEL](./05_prompt_template.md)  
- [LCEL 组件组合与 Runnable 接口](./07_lcel.md)  
- [基础链三要素 & 模块](./02_basic_chain_and_modules.md)  
- 可运行示例：[demo_output_parser.py](./demo_output_parser.py)
