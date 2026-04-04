# FastAPI 安全机制（二）OAuth2 + JWT 生成 Token

在 **OAuth2 密码流**场景下，客户端把 `username` / `password` 发到约定端点，服务端校验通过后签发 **JWT**，后续请求在 **`Authorization: Bearer <token>`** 里携带。本篇覆盖 **Token 签发**与 **`POST /token`**；Bearer 校验与解析 `sub` 通常写在依赖里，可与后续笔记衔接。

（上一篇：[安全机制简介](./01_security_introduction.md)）

---

## 一、核心组件

### 1. OAuth2PasswordBearer

- 参数 **`tokenUrl`**：OpenAPI / Swagger 里「去哪里换 Token」的地址（一般是 **`POST /token`**）。
- 用在受保护路由的 `Depends(...)` 里时，会读 **`Authorization: Bearer ...`**；缺失或格式不对时默认 **401**。若当前只实现 `/token`，可先只写配置，实现受保护接口时再注入该依赖。

### 2. OAuth2PasswordRequestForm

- `Depends()` 注入后，按 OAuth2 密码流解析 **`application/x-www-form-urlencoded`** 里的 **`username`**、**`password`**。
- 需要 **`python-multipart`**。

### 3. PyJWT

- **`jwt.encode`**：把载荷（如 `sub`、`exp`）签成 JWT 字符串。
- **`jwt.decode`**：校验与解析（后续笔记常用）。
- 安装：`pip install PyJWT python-multipart`（包名 **PyJWT**，导入 `import jwt`）。

---

## 二、关键配置

```python
SECRET_KEY = "随机长密钥"  # 生产用 openssl rand -hex 32 等，勿提交仓库
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

---

## 三、生成 Token

建议用 **UTC** 的 timezone-aware `datetime` 写 **`exp`**：

```python
from datetime import datetime, timedelta, timezone

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=15)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

旧教程里的 `datetime.utcnow()` 仍是 UTC naive，新项目更推荐 **`datetime.now(timezone.utc)`**。

---

## 四、登录接口（换取 Token）

```python
class Token(BaseModel):
    access_token: str
    token_type: str


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

真实项目须在 `login` 内校验用户名与密码（哈希比对等）；上式仅演示签发。

---

## 五、流程

1. 前端 **`POST /token`**，表单提交 **`username`**、**`password`**。
2. 后端校验通过后 **`jwt.encode`** 生成带 **`exp`** 的 **`access_token`**。
3. 返回 JSON；后续请求带 **`Authorization: Bearer <access_token>`**。

---

## 一句话

**OAuth2PasswordRequestForm 收登录表单，jwt.encode 签发带过期的 Token；OAuth2PasswordBearer 约定 Bearer 与 tokenUrl，与 OpenAPI 对齐。**

---

## 可运行示例

见 [`fastapi_security_oauth2_jwt_token_demo.py`](./fastapi_security_oauth2_jwt_token_demo.py)。依赖见仓库根目录 **`requirements.txt`**。

下一篇：[OAuth2 + JWT 完整登录验证流程](./03_oauth2_jwt_full_auth_flow.md)。
