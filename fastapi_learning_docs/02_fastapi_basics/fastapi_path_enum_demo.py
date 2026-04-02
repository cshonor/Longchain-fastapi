"""
路径参数 + Enum 路径参数（对应笔记）：
  - 02_path_params_8_sentences.md
  - 03_enum_path_params.md

运行（任选其一）：
  在项目根目录 longchain/ 下：
    uvicorn fastapi_path_enum_demo:app --reload --app-dir fastapi_learning_docs/02_fastapi_basics
  或先进入本目录再启动：
    cd fastapi_learning_docs/02_fastapi_basics
    uvicorn fastapi_path_enum_demo:app --reload

文档：http://127.0.0.1:8000/docs
"""

from enum import Enum

from fastapi import FastAPI

app = FastAPI(
    title="Path params + Enum path demo",
    description="Illustrates typed path params, route order, :path, and str+Enum.",
)


# --- 03：Enum 限制路径只能取固定值；非法值 → 422；/docs 有下拉 ---
class ModelName(str, Enum):
    resnet = "resnet"
    alexnet = "alexnet"


@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    return {"model": model_name.value, "message": f"加载 {model_name.value} 模型"}


# --- 02：基础路径参数；int 会自动转换，非数字 → 422 ---
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "type": type(item_id).__name__}


# --- 02：固定路径必须在「会吞掉同名段」的动态路径之前（此处 user_id 为 str）---
@app.get("/users/me", tags=["用户"])
def read_users_me():
    return {"user_id": "me", "note": "固定路由 /users/me"}


@app.get("/users/{user_id}")
def read_user(user_id: str):
    return {"user_id": user_id}


# --- 02：路径里传「含斜杠」的文件路径用 {file_path:path} ---
@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    return {"file_path": file_path}


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "try": [
            "GET /items/42",
            "GET /items/not-a-number   # 422",
            "GET /users/me",
            "GET /users/123",
            "GET /models/resnet",
            "GET /models/vgg16   # 422",
            "GET /files/docs/api/readme.md",
        ],
    }
