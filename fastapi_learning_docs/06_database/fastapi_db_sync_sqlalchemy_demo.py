"""
SQLAlchemy 同步 + SQLite（可改为 mysql+pymysql://...）— 对应 01_sqlalchemy_sync.md

依赖：sqlalchemy、PyJWT、python-multipart、passlib[bcrypt]（见仓库 requirements.txt）
可选 MySQL：pip install pymysql，并修改 SQLALCHEMY_DATABASE_URL

运行：
  uvicorn fastapi_db_sync_sqlalchemy_demo:app --reload --app-dir fastapi_learning_docs/06_database

文档：http://127.0.0.1:8000/docs

流程：POST /register → POST /login → GET /users/me（Authorization: Bearer ...）
"""

from collections.abc import Generator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, mapped_column, sessionmaker

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

SQLALCHEMY_DATABASE_URL = "sqlite:///./demo_sync.db"
_connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class DBUser(Base):
    __tablename__ = "test_user"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String(100), unique=True, index=True)
    password = mapped_column(String(255))
    sex = mapped_column(String(10), nullable=True)
    login_time = mapped_column(Integer, nullable=True)
    create_date = mapped_column(DateTime(timezone=True), nullable=True)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    sex: str | None = None


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="SQLAlchemy sync DB demo", lifespan=lifespan)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user_by_username(db: Session, username: str) -> DBUser | None:
    return db.scalars(select(DBUser).where(DBUser.username == username)).first()


def authenticate_user(db: Session, username: str, password: str) -> DBUser | None:
    user = get_user_by_username(db, username)
    if user is None:
        return None
    if not verify_password(password, user.password):
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


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> DBUser:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or not isinstance(username, str):
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/register", response_model=User)
def register(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    if get_user_by_username(db, form_data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    now = datetime.now(timezone.utc)
    db_user = DBUser(
        username=form_data.username,
        password=get_password_hash(form_data.password),
        sex=None,
        login_time=None,
        create_date=now,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": user.username}, expires_delta=delta)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
def read_me(current_user: DBUser = Depends(get_current_user)):
    return current_user


@app.get("/")
def root():
    return {
        "docs": "/docs",
        "db_url_hint": "修改 demo 内 SQLALCHEMY_DATABASE_URL 可切 MySQL（mysql+pymysql://...）",
        "flow": ["POST /register", "POST /login", "GET /users/me"],
    }
