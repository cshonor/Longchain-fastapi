"""
OAuth2 scopes + JWT — 对应 04_oauth2_scopes.md

运行：
  uvicorn fastapi_security_oauth2_scopes_demo:app --reload --app-dir fastapi_learning_docs/05_security

文档：http://127.0.0.1:8000/docs

账号（密码均为 secret）：
  - johndoe：Token 含 scopes me、items，可访问 /users/me、/items，不可 /admin
  - admin：Token 含 me、items、admin，可访问全部
"""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

_shared_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "full_name": "John Doe",
        "disabled": False,
        "hashed_password": _shared_hash,
    },
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin",
        "disabled": False,
        "hashed_password": _shared_hash,
    },
}

USER_SCOPES: dict[str, list[str]] = {
    "johndoe": ["me", "items"],
    "admin": ["me", "items", "admin"],
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    scopes={
        "me": "查看自己信息",
        "items": "查看项目",
        "admin": "管理员权限",
    },
)
app = FastAPI(title="OAuth2 scopes demo")


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


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


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=15)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="无效的认证凭据",
    headers={"WWW-Authenticate": "Bearer"},
)


def _token_scopes(payload: dict) -> list[str]:
    raw = payload.get("scopes", [])
    if isinstance(raw, str):
        return [s for s in raw.split() if s]
    if isinstance(raw, list):
        return list(raw)
    return []


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> UserInDB:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError:
        raise credentials_exception

    username = payload.get("sub")
    if username is None or not isinstance(username, str):
        raise credentials_exception

    token_scopes = _token_scopes(payload)
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，缺少 scope",
                headers={"WWW-Authenticate": authenticate_value},
            )

    user = get_user(fake_users_db, username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scopes = USER_SCOPES.get(user.username, [])
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": scopes},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: UserInDB = Security(get_current_active_user, scopes=["me"]),
):
    return current_user


@app.get("/items")
async def read_items(
    current_user: UserInDB = Security(get_current_active_user, scopes=["items"]),
):
    return {"message": "items ok", "user": current_user.username}


@app.get("/admin")
async def admin_only(
    current_user: UserInDB = Security(get_current_active_user, scopes=["admin"]),
):
    return {"message": "admin only", "user": current_user.username}


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "users": {"johndoe": USER_SCOPES["johndoe"], "admin": USER_SCOPES["admin"]},
        "password": "secret",
    }
