import os
from pathlib import Path

from dotenv import load_dotenv

# 从 longchain 目录加载 .env
_env_path = Path(__file__).parent / ".env"
load_dotenv(_env_path, override=True)

# Deepseek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

# Hunyuan
HUNYUAN_APP_ID = os.getenv("HUNYUAN_APP_ID")
HUNYUAN_SECRET_ID = os.getenv("HUNYUAN_SECRET_ID")
HUNYUAN_SECRET_KEY = os.getenv("HUNYUAN_SECRET_KEY")

# Dashscope
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mod/v1")

# ZhipuAI
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
ZHIPUAI_BASE_URL = os.getenv("ZHIPUAI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
