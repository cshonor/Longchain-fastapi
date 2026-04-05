# LangChain 中 LLM 与 ChatModel 使用总结

概念层对照见：[LLM 与 ChatModel（消息与分工）](./03_llm_and_chatmodel.md)。本篇侧重**选型、参数与可运行示例**。

---

## 一、核心区别与使用场景

### 1. 本质关系

- 在 LangChain 里，**补全型 LLM** 与 **ChatModel** 通常是**两套独立的调用接口**：按业务**任选其一**即可，**不是**必须先建一个再派生另一个。  
- 多轮对话、角色区分、工具调用等优先 **ChatModel**；简单「一段 prompt → 一段文本」可用 **LLM（补全）**。

### 2. 对比表

| 特性 | LLM（补全 / 文本接口） | ChatModel |
|------|------------------------|-----------|
| **输入** | 字符串 `str` | 消息列表 `list[BaseMessage]`，如 `[HumanMessage(...)]` |
| **输出** | 字符串（或封装类型，以版本为准） | 多为 `AIMessage`，文本在 **`content`** |
| **典型用途** | 单次生成、续写、无结构多轮 | 多轮对话、system/user 分工、Agent |
| **示例类** | 如 `Tongyi`（`langchain_community`） | 如 `ChatDeepSeek`、`ChatOpenAI` |

---

## 二、为什么 `ChatDeepSeek` 要写 `model`？

- **`ChatDeepSeek`** 是调用 **DeepSeek API 的通用入口**；平台上有多款模型（能力、价格不同）。  
- **`model="deepseek-chat"`** 等参数用来指定**具体端点/型号**，例如：`deepseek-chat`、`deepseek-coder`、`deepseek-reasoner` 等（以官方文档为准）。

### `Tongyi` 为什么有时「不用写 model」？

- 多数封装会提供 **默认模型名**（如 `qwen-turbo`），故教程里常省略。  
- 仍可**显式指定**，与 ChatDeepSeek 同理：

```python
from langchain_community.llms.tongyi import Tongyi

llm = Tongyi(model="qwen-plus")  # api_key 建议用环境变量，勿写死在仓库里
```

---

## 三、代码示例（可直接运行）

**密钥**：用环境变量（如 `DASHSCOPE_API_KEY`、`DEEPSEEK_API_KEY`）或 `.env`，不要提交到 Git。

### 1. LLM：通义千问（补全）

```python
import os

from langchain_community.llms.tongyi import Tongyi

llm = Tongyi(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    # model="qwen-turbo",  # 可选，默认视版本而定
)

response = llm.invoke("给杯子公司起个名字，直接输出结果")
print("LLM 输出：", response)
```

### 2. ChatModel：DeepSeek

```python
import os

from langchain_core.messages import HumanMessage
from langchain_deepseek import ChatDeepSeek

chat_model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
)

messages = [HumanMessage(content="给杯子公司起个名字，直接输出结果")]
response = chat_model.invoke(messages)
print("ChatModel 输出：", response.content)
```

---

## 四、注意事项

1. **输入不要混用**：`LLM.invoke()` 不要传 `HumanMessage` 列表；`ChatModel` **推荐**始终传消息列表（个别实现曾支持字符串糖，但不作为规范）。  
2. **密钥**：各平台 API Key 必填；生产用环境变量或密钥管理服务。  
3. **依赖**（按需安装）：

```bash
pip install langchain langchain-core langchain-community langchain-deepseek
```

包名与版本以当前 LangChain 文档为准。

---

## 可运行 Demo

仓库内脚本（任选配置密钥后运行）：[`demo_llm_chatmodel_compare.py`](./demo_llm_chatmodel_compare.py)

---

## 延伸阅读

- [概念篇：LLM 与 ChatModel](./03_llm_and_chatmodel.md)  
- [环境搭建 & 核心概念](./01_env_and_core_concepts.md)
