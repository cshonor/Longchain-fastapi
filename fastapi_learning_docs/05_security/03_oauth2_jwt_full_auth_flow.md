# FastAPI 安全机制（三）OAuth2 + JWT 完整登录验证流程

把 **注册/存库时的密码哈希**、**登录换 Token**、**Bearer 鉴权**、**解析当前用户** 串成一套标准做法，与 OpenAPI 文档、Swagger「Authorize」一致。

（上一篇：[OAuth2 + JWT 签发 Token](./02_oauth2_jwt_token.md)）

---

## 一、本节覆盖什么

1. 密码用 **Passlib + bcrypt** 哈希存储与校验（不存明文）。  
2. **OAuth2 密码流**：表单提交用户名、密码。  
3. 校验通过 → **签发 JWT**（`sub` 一般为用户名，`exp` 为过期时间）。  
4. 后续请求 **`Authorization: Bearer <token>`**。  
5. **`OAuth2PasswordBearer`** 取出 Token → **`jwt.decode`** → 查用户 → **`Depends(get_current_user)`** 注入当前用户。

---

## 二、依赖安装

```bash
pip install PyJWT python-multipart passlib bcrypt
```

（仓库根目录 `requirements.txt` 中已包含等价依赖，可用 **`passlib[bcrypt]`** 一次安装 bcrypt 后端。）

---

## 三、流程（背诵版）

1. 客户端提交 **用户名 + 密码**。  
2. 后端 **查用户 + `verify_password`**。  
3. 通过则 **`jwt.encode`** 得到 **access_token**。  
4. 客户端保存 Token，受保护请求统一带 **Bearer**。  
5. 依赖里 **`jwt.decode`** 校验签名与过期，读 **`sub`**，再 **`get_user`**。  
6. 路由参数 **`current_user: User = Depends(get_current_user)`**（或再包一层校验 **`disabled`**）。

---

## 四、核心代码结构

### 1. 配置 + 假用户表 + 上下文

```python
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import PyJWTError
from pydantic import BaseModel
from passlib.context import CryptContext

SECRET_KEY = "你的密钥"  # 生产环境勿写死在仓库
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
app = FastAPI()
```

表中哈希示例对应明文密码 **`secret`**（与 FastAPI 官方教程一致，仅作本地演示）。

### 2. 用户模型

```python
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str
```

受保护接口用 **`response_model=User`** 返回，避免把 **`hashed_password`** 序列化给客户端。

### 3. 密码工具

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 4. 查用户与登录校验

```python
def get_user(db: dict, username: str) -> UserInDB | None:
    if username in db:
        return UserInDB(**db[username])
    return None


def authenticate_user(db: dict, username: str, password: str) -> UserInDB | None:
    user = get_user(db, username)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
```

### 5. 签发 JWT

```python
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=15)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 6. 登录路由

```python
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

### 7. 鉴权依赖：当前用户

解析 Token 时**不要**写裸 **`except:`**，应捕获 **`PyJWTError`**（签名错误、过期、格式错误等）：

```python
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="无效的认证凭据",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or not isinstance(username, str):
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = get_user(fake_users_db, username)
    if user is None:
        raise credentials_exception
    return user
```

需要拒绝 **`disabled`** 用户时，再定义 **`get_current_active_user`**，在内部 **`Depends(get_current_user)`** 并检查 **`disabled`**。

### 8. 受保护路由

```python
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    return current_user
```

---

## 五、精简总结

1. **Passlib（bcrypt）**：哈希与验密码。  
2. **OAuth2PasswordRequestForm**：标准登录表单。  
3. **JWT**：签发与携带身份。  
4. **OAuth2PasswordBearer**：从请求头取 Bearer Token。  
5. **`get_current_user`（及可选 `get_current_active_user`）**：可复用的鉴权依赖。

---

## 一句话

**登录校验通过后签发 JWT；之后每个受保护路由依赖里 decode Token、还原用户，接口不写重复鉴权代码。**

---

## 可运行示例

见 [`fastapi_security_oauth2_jwt_full_demo.py`](./fastapi_security_oauth2_jwt_full_demo.py)（账号 **`johndoe` / `secret`**）。

下一篇：[OAuth2 scopes](./04_oauth2_scopes.md)。
