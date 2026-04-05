# LangChain 核心笔记：`PromptTemplate` 全解析（含 `ChatPromptTemplate`）

## 一、核心定义

**`PromptTemplate` 是 LangChain 里用来「动态生成提示词」的基础组件**：把**固定指令框架**和**变量**分开——模板里写 `{变量名}`，运行时再 `format` / `invoke` 填入。

在此基础上，**`ChatPromptTemplate`** 把同一思路用到**对话**：用 `system` / `human` 等角色拼出 **消息列表**，与 **ChatModel** 配套。

（与 [LLM / ChatModel](./04_llm_chatmodel_usage.md) 对照：补全接口多用 `PromptTemplate`；对话接口多用 `ChatPromptTemplate`。）

---

## 二、为什么要用它？（三大核心优势）

### 1. 代码解耦，便于维护

- **分离关注点**：提示长什么样、有哪些规则，与业务分支分开写。  
- **一改全改**：模板只维护一处，避免多处复制粘贴后改漏。

### 2. 支持多变量、复杂逻辑

- 多个 `{var}` 一次传入，比到处拼 f-string 更清晰。  
- 需要角色与人设时，用 **`ChatPromptTemplate`** 表达 system / human（及后续多轮）。

### 3. 与 LangChain 生态兼容（LCEL）

- 作为 Runnable 链的**起点**：`prompt | llm | parser` 等。  
- 与 **LLM（补全）**、**ChatModel**、**OutputParser** 等同为管道中的一环，便于测试与扩展。

---

## 三、两种常用类型

### 1. `PromptTemplate`（单段文本）

适合单次任务：摘要、起名、分类等。

```python
from langchain_core.prompts import PromptTemplate

template = "给生产 {product} 的公司取一个好听的名字。"
prompt = PromptTemplate.from_template(template)
final_prompt = prompt.format(product="保温杯")
print(final_prompt)
# 给生产 保温杯 的公司取一个好听的名字。
```

### 2. `ChatPromptTemplate`（多角色消息）

适合多轮、人设、与 **ChatModel** 对接。

```python
from langchain_core.prompts import ChatPromptTemplate

system_template = "你是一个专业的 {role}，只回答 {language} 问题。"
human_template = "{question}"

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        ("human", human_template),
    ]
)

final_messages = chat_prompt.format_messages(
    role="Python 工程师",
    language="中文",
    question="如何高效学习 Python？",
)
# list[BaseMessage]，如 SystemMessage + HumanMessage
```

---

## 四、链式调用（LCEL）

**类型要对齐**：`ChatPromptTemplate` → **消息列表** → 应接 **ChatModel**；`PromptTemplate` → **字符串** → 应接 **LLM（补全）**。

**常见误区**：不少教程把 **`ChatPromptTemplate | Tongyi`** 写在一起；`Tongyi` 属于**补全 LLM**，通常期望字符串输入，与 Chat 模板输出**不配套**。下面用**正确搭配**各给一例。

### 示例 A：`ChatPromptTemplate | ChatModel`

```python
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个助手，围绕 {topic} 帮助用户。"),
        ("human", "{content}"),
    ]
)
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
)

chain = prompt | llm
result = chain.invoke(
    {"topic": "创意生成", "content": "给杯子公司起 3 个名字"}
)
# result 一般为 AIMessage，文本在 result.content
```

### 示例 B：`PromptTemplate | LLM（补全）`

```python
import os

from langchain_community.llms.tongyi import Tongyi
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    "你是起名助手。产品：{product}。请给出 3 个公司名，逗号分隔。"
)
llm = Tongyi(api_key=os.environ["DASHSCOPE_API_KEY"])
chain = prompt | llm
text = chain.invoke({"product": "保温杯"})
```

---

## 五、对比演示：f-string 与 `PromptTemplate`

```python
product = "保温杯"

# f-string：提示与业务混在同一处，复用和测试都费劲
s1 = f"给生产 {product} 的公司取一个好听的名字。"

# PromptTemplate：模板可单测、可入库、可接链
from langchain_core.prompts import PromptTemplate

p = PromptTemplate.from_template("给生产 {product} 的公司取一个好听的名字。")
s2 = p.format(product=product)
```

---

## 六、一句话总结

**`PromptTemplate`（及 `ChatPromptTemplate`）= 提示词的「封装器」。**  
不改变模型本身能力，但能把「拼字符串的小脚本」收成**可维护、可扩展、方便上生产**的结构，并自然接入 **`prompt | llm | parser`** 这类链路。

---

## 延伸阅读

- [自定义 `StringPromptTemplate`（实现 `format`、JSON 人物信息）](./10_custom_string_prompt_template.md)  
- [模块化 Prompt（分层组合、非「一场景一模板」）](./11_modular_prompts.md)  
- [基础链三要素 & 模块](./02_basic_chain_and_modules.md)  
- [环境搭建 & 核心概念](./01_env_and_core_concepts.md)
