# Longchain-FastAPI

基于 LangChain 与 FastAPI 的 LLM 应用 API 项目。

## 项目结构

```
longchain/
├── longchain/       # LangChain 相关逻辑（链、提示、模型等）
├── fastapi/         # FastAPI 路由、接口与中间件
├── rag/             # RAG 检索增强生成相关
├── longgraph/       # LongGraph 图相关
├── mcp/             # MCP 相关
├── environment.yml  # Conda 环境配置
├── requirements.txt # pip 依赖
└── README.md
```

## 技术栈

- **LangChain** - 大语言模型应用开发框架
- **FastAPI** - 高性能 Python Web 框架

## 环境要求

- Python 3.10+（LangChain 1.2 要求）
- Anaconda 或 Miniconda

## 快速开始（Anaconda）

### 1. 克隆项目

```bash
git clone https://github.com/cshonor/Longchain-fastapi.git
cd Longchain-fastapi
```

### 2. 创建 Conda 环境

```bash
conda env create -f environment.yml
```

### 3. 激活环境

```bash
conda activate longchain-fastapi
```

### 4. 运行服务

```bash
uvicorn main:app --reload
```

### 更新环境

```bash
conda env update -f environment.yml
```

## 其他方式（pip + venv）

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

## 配置

复制 `env.example` 为 `.env`，填写所需 API Key：

```bash
copy env.example .env   # Windows
# cp env.example .env   # Linux/Mac
```

支持的 LLM 服务：Deepseek、OpenAI、Anthropic、Hunyuan、Dashscope、ZhipuAI。

## License

MIT
