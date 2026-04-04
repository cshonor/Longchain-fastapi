"""
路径装饰器 dependencies= — 对应 04_di_path_decorator_dependencies.md

运行：
  uvicorn fastapi_dep_path_decorator_demo:app --reload --app-dir fastapi_learning_docs/04_dependency_injection

文档：http://127.0.0.1:8000/docs

调用 /items/ 时需 Header：X-Token: token 与 X-Key: key
"""

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI(title="Path decorator dependencies demo")


async def verify_token(x_token: str = Header(...)):
    if x_token != "token":
        raise HTTPException(status_code=400, detail="无效token")


async def verify_key(x_key: str = Header(...)):
    if x_key != "key":
        raise HTTPException(status_code=400, detail="无效key")


@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "items": "/items/",
        "headers": {"X-Token": "token", "X-Key": "key"},
    }
