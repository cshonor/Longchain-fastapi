# 模块化 Prompt 体系：不是「一个场景一套模板」

**核心结论**：Prompt 质量决定模型输出；**`PromptTemplate` / `ChatPromptTemplate` 的价值是把「固定指令骨架」和「动态业务数据」解耦**，并做成**可复用、可组合、可维护**的组件——**不是**「每个场景必须从零写一整块独立字符串」。

与 [自定义 `StringPromptTemplate`](./10_custom_string_prompt_template.md)、[Prompt 与 LCEL](./05_prompt_template.md)、[Chat 模板](./05_prompt_template.md) 一起看。

---

## 一、`PromptTemplate` 到底解决什么问题？

以人物 JSON 类模板为例（见 [10](10_custom_string_prompt_template.md)），本质上两件事：

1. **固定骨架**：例如「用某分隔符分段、按 JSON 提取字段」——**规则不随单次请求变**。  
2. **填充变量**：`name`、`occupation`、`fun_fact` 等——**每次调用会变的数据**。

工程上的收益：**少复制粘贴、可版本管理、可测试、可进链（LCEL）**，而不是「一个类锁死一个业务场景」。

---

## 二、Agent 里是不是「一个场景一套模板」？

更接近的做法：**分层 + 模块化 + 组合**（像拼乐高）。

- **底层**：通用规则（角色、格式、拒答策略、安全边界）——多 Agent 共用。  
- **中层**：功能块（工具说明、检索指令、记忆槽位）——按能力拆。  
- **上层**：场景差异——往往只是 **换 system 文案** 或 **换注入的数据变量**，而不是整条消息结构重写。

### 文本示意（概念）

```text
# 通用角色与格式
system_base = """你是一个专业的 AI 助手……（格式、不编造等）"""

# 功能块
tool_block = """可用工具：{tools_description} ……"""
memory_block = """历史：{chat_history} 当前问题：{user_question}"""

# 场景 = 通用 + 功能 + 一句场景说明
客服 = system_base + memory_block + "你现在是电商客服……{order_info}"
代码 = system_base + tool_block + "你现在是代码助手……{code_requirement}"
```

真实项目里会用 **LangChain 模板对象** 表达上述结构，而不是到处拼裸字符串。

---

## 三、LangChain 里怎么落地？

| 能力 | 典型工具 | 说明 |
| :--- | :--- | :--- |
| 字符串模板、自定义 `format` | `PromptTemplate`、`StringPromptTemplate` | 简单补全链、结构化提取提示 |
| 多角色 / 多轮 | `ChatPromptTemplate` | Agent、RAG、对话 |
| 动态插入消息列表 | `MessagesPlaceholder` | 历史、`agent_scratchpad` 等 |
| Few-shot | `FewShotPromptTemplate` / `FewShotChatPromptTemplate` | 分类、意图等按需带示例 |
| 多步提示 | **`Runnable` 管道** 或多段模板组合 | 旧版文档中的 `PipelinePromptTemplate` 在新栈里不总存在；可用 **`prompt_a | prompt_b`**、或一个 `ChatPromptTemplate` 里多条消息、`partial` 注入 |

### `partial` 换场景：**system 必须是占位符**

下面写法与「只改 system、不动结构」一致。注意：**若 `from_messages` 里 system 写死成常量，就不能再用 `partial(system="...")` 覆盖**；应使用 **`{system_rules}`** 这类变量，再 **`partial(system_rules="...")`**。

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_rules}\n\n你是一个智能助手，在需要时使用提供的工具。"),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad", optional=True),
    ]
)

customer_service = agent_prompt.partial(
    system_rules="你现在是电商客服，优先处理订单查询与售后。",
)
code_assistant = agent_prompt.partial(
    system_rules="你现在是代码助手，优先给出可运行的 Python 示例。",
)

# 同一条骨架，不同场景只换 partial 绑定的 system_rules
msgs = customer_service.format_messages(
    input="我的订单何时发货？",
    chat_history=[],
    agent_scratchpad=[],
)
```

可运行打印示例见：[demo_modular_prompts.py](./demo_modular_prompts.py)。

---

## 四、「成千上万场景」怎么办？

常见误区是以为每个场景都要换一整段 Prompt。实际上：

- 很多场景差异只是 **变量不同**（同一套规则 + 不同的 `order_info`、`user_question`）。  
- 工程上常用：  
  1. **少量通用模板**覆盖大类（客服 / 代码 / 抽取等）；  
  2. **变量 + 代码侧分支**处理长尾差异；  
  3. **Few-shot 动态加载**同一模板、不同示例集，而不是为每个意图复制一整份模板。

---

## 五、Agent 场景的工程化建议

1. **先分层再组合**：通用规则 → 工具/记忆/RAG → 场景文案或数据。  
2. **模板配置化**：大段字符串可放 YAML/JSON/数据库，代码只负责加载与 `partial`/`invoke`。  
3. **优先用 LangChain 模板 API**：少手写 `+` 拼接，多用 `ChatPromptTemplate`、`MessagesPlaceholder`，结构清晰、易测。  
4. **持续迭代**：改一个公共模块能影响所有引用它的场景，降低维护成本。

---

## 六、总结

- **对**：Prompt 要具体，质量直接影响输出。  
- **纠正**：模板机制是为了 **复用与组合**，不是「一场景一文件、全文重写」。  
- **落地**：**通用骨架 + 模块 + 变量 +（必要时）partial / Few-shot**。

---

## 延伸阅读

- [PromptTemplate / ChatPromptTemplate](./05_prompt_template.md)  
- [自定义 StringPromptTemplate](./10_custom_string_prompt_template.md)  
- [LCEL](./07_lcel.md)  
- [Runnable](./09_runnable.md)
