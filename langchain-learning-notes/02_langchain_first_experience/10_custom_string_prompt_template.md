# 自定义字符串提示模板：`StringPromptTemplate` + JSON 人物信息

与 [PromptTemplate / from_template](./05_prompt_template.md) 不同，这里用 **`StringPromptTemplate`** 子类**自己实现 `format()`**，把业务数据（如人物字段）编成模型易follow 的提示文本（常带一段 **JSON 样例**）。

---

## 1. 依赖说明

```python
import json

from langchain_core.prompts import StringPromptTemplate
from pydantic import Field, field_validator
```

- **`json`**：把 Python 字典序列化为 JSON 字符串，拼进提示里。  
- **Pydantic**：`langchain_core` 的模板类本身基于 Pydantic；校验写在子类上即可。  
- **`StringPromptTemplate`**：只要求你实现 **`format(**kwargs) -> str`**（以及继承自带的 Runnable 行为）。

**常见误区**：不要再额外继承一个裸的 **`BaseModel`**。`StringPromptTemplate` 的基类已是 Pydantic 模型，**多重继承容易冲突**；用 **`field_validator` / `model_validator`** 写在校验逻辑里即可。

---

## 2. 分隔符与指令文案

```python
delimiter = "####"
INSTRUCTION = """将每个用户的信息用{delimiter}字符分割，并按照JSON格式提取姓名、职业和爱好信息。"""
```

- **`delimiter`**：提示里约定「分段」用的符号（与具体业务文本解析规则一致即可）。  
- **`INSTRUCTION`**：告诉模型要按 JSON 思路处理 **姓名 / 职业 / 爱好**（示例里用 `fun_fact` 表示趣味信息，对应「爱好」类描述）。

---

## 3. 自定义类 `PersonInfoPromptTemplate`

### （1）校验 `input_variables`

强制 **`name`、`occupation`、`fun_fact`** 必须出现在变量列表里，避免漏参导致后续链路与 JSON 字段对不上：

```python
@field_validator("input_variables")
@classmethod
def validate_input_variables(cls, v: list[str]) -> list[str]:
    required = {"name", "occupation", "fun_fact"}
    if not required.issubset(set(v)):
        raise ValueError("input_variables 须同时包含 name、occupation、fun_fact")
    return v
```

若以后要加字段（如 `age`），在 **`required` 与默认 `input_variables`** 里各加一处即可；更进一步可用「配置元组 / 数据类」统一维护字段列表（见文末优化思路）。

### （2）`format`：指令 + JSON 片段

```python
def format(self, **kwargs) -> str:
    data = {k: (kwargs.get(k) or "") for k in self.input_variables}
    head = INSTRUCTION.format(delimiter=self.delimiter)
    return head + json.dumps(data, ensure_ascii=False)
```

- **`(kwargs.get(k) or "")`**：`None` 时落成空字符串，减少模型侧看到大量 `null`（可按业务改成占位文案）。  
- **`ensure_ascii=False`**：中文正常显示。

---

## 4. 应用场景

- **结构化输出**：提示里嵌入 JSON 片段，引导模型按字段生成，便于再接 **`JsonOutputParser`** / Pydantic 解析器。  
- **提前校验**：在 `format` 之前就发现变量配置错误。  
- **接链**：模板仍是 **Runnable**，可 **`prompt | llm | parser`**，与 [LCEL](./07_lcel.md) 一致。

---

## 5. 可运行示例

完整代码与一次 **`format` / `invoke`** 演示见：[demo_custom_string_prompt_template.py](./demo_custom_string_prompt_template.py)。

```bash
python langchain-learning-notes/02_langchain_first_experience/demo_custom_string_prompt_template.py
```

---

## 6. 扩展与维护（优化思路）

- **字段变多**：用常量 `REQUIRED_FIELDS = ("name", "occupation", "fun_fact")` 或小型 **`dataclass`** 描述字段，校验与 `format` 里 **`input_variables` 默认工厂**共用同一份定义，减少改漏。  
- **文档**：在类上写简短 docstring，说明 `invoke` 需要的 dict 键与示例。  
- **与 `PromptTemplate.from_template` 对比**：简单 `{var}` 模板用 **`from_template`** 更快；需要**复杂拼接、校验、多段逻辑**时再考虑 **`StringPromptTemplate` 子类**。

---

## 延伸阅读

- [模块化 Prompt 体系（分层组合）](./11_modular_prompts.md)  
- [PromptTemplate / ChatPromptTemplate](./05_prompt_template.md)  
- [LCEL](./07_lcel.md)  
- [Runnable](./09_runnable.md)
