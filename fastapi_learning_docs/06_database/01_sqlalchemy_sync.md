# FastAPI 数据库（一）SQLAlchemy 同步引擎

**目标**：用 **SQLAlchemy 同步 ORM** 连 **MySQL**（或其它支持的数据库），在 FastAPI 里完成 **注册 / 登录（JWT）/ 查当前用户** 的常见骨架。  
**约定**：**DB 模型**描述表结构；**Pydantic 模型**描述接口入参、出参；**Session** 按请求创建、结束关闭。

（安全相关前置：[OAuth2 + JWT 完整流程](../05_security/03_oauth2_jwt_full_auth_flow.md)。）

---

## 一、核心概念

1. **SQLAlchemy**：ORM，把表映射成 Python 类。  
2. **DB Model（ORM 模型）**：与表一一对应，字段多用 **`=`**（`Column` / `mapped_column`）。  
3. **Pydantic Model**：校验与序列化 JSON，字段用 **`:`** 类型注解。  
4. **Session**：一次请求内使用的**工作单元**；用完必须 **`close`**，常用 **`yield` 依赖**托管。

---

## 二、安装依赖

```bash
pip install sqlalchemy pymysql
```

MySQL 驱动使用 **`pymysql`** 时，连接串形如 **`mysql+pymysql://...`**。本地练习也可先用 **SQLite**（见文末 demo）。

---

## 三、引擎与 Session（固定骨架）

SQLAlchemy **2.x** 推荐 **`DeclarativeBase`**（旧版 `declarative_base()` 仍可用，但新代码不必再写）：

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@host:3306/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
```

---

## 四、数据库模型（DB Model）

```python
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import mapped_column


class DBUser(Base):
    __tablename__ = "test_user"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String(100), unique=True, index=True)
    password = mapped_column(String(255))  # 存哈希，不存明文
    sex = mapped_column(String(10), nullable=True)
    login_time = mapped_column(Integer, nullable=True)
    create_date = mapped_column(DateTime(timezone=True), nullable=True)
```

---

## 五、Pydantic 模型（返回给前端）

**不要**把密码字段放进对外 **`response_model`**。Pydantic v2 用 **`from_attributes=True`** 从 ORM 对象构造（等价于 v1 的 **`orm_mode = True`**）：

```python
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    sex: str | None = None
```

---

## 六、`get_db`（yield 依赖）

```python
from collections.abc import Generator


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

路由或依赖里写 **`db: Session = Depends(get_db)`**。

---

## 七、常用三块逻辑

### 1. 注册（插入）

示例沿用 **OAuth2 表单**（`username` / `password`）只为和登录字段一致；生产可改为独立 **`Body` / Pydantic** 模型。

```python
@app.post("/register", response_model=User)
def register(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    hashed_pw = get_password_hash(form_data.password)
    db_user = DBUser(username=form_data.username, password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

需处理**用户名重复**（唯一约束冲突）等异常。

### 2. 登录（查库 + 验密 + JWT）

```python
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
```

`authenticate_user` 内部用 **`select(DBUser).where(DBUser.username == ...)`** 查行，再 **`verify_password`**。

### 3. 当前用户（Bearer + DB）

用**函数**查用户，不要凭空写 **`DBUser.get_by_username`**（除非你在模型上自己封装了类方法）：

```python
def get_user_by_username(db: Session, username: str) -> DBUser | None:
    return db.scalars(select(DBUser).where(DBUser.username == username)).first()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    if username is None:
        raise HTTPException(401, detail="无效凭证")
    user = get_user_by_username(db, username)
    if user is None:
        raise HTTPException(401, detail="用户不存在")
    return user


@app.get("/users/me", response_model=User)
def read_me(current_user: DBUser = Depends(get_current_user)):
    return current_user
```

**注意**：这里是**同步 Session**；若路由写成 **`async def`**，在协程里直接跑同步 IO **会阻塞事件循环**。同步引擎章节优先用 **`def` 路由**，或下一篇换**异步引擎 / `run_in_threadpool`**。

---

## 八、必须记住

1. **ORM 字段**：`Column` / `mapped_column`；**Pydantic**：类型注解 **`:`**。  
2. Pydantic v2：**`model_config = ConfigDict(from_attributes=True)`** 才能从 ORM 转输出模型。  
3. **`get_db`**：**`yield` + `finally: db.close()`**。  
4. 需要访问数据库的依赖或路由：**`db: Session = Depends(get_db)`**。  
5. 查询优先 **SQLAlchemy 2.0 风格**：**`select(...).where(...)`** + **`db.scalars(...)` / `db.execute(...)`**。

---

## 一句话

**FastAPI + 同步 SQLAlchemy：表映射成类，`get_db` 按请求管 Session，Pydantic 只管 API 形状与安全输出。**

---

## 可运行示例

默认 **SQLite** 文件，便于零配置运行；把 **`SQLALCHEMY_DATABASE_URL`** 换成 **`mysql+pymysql://...`** 即可切 MySQL：

[`fastapi_db_sync_sqlalchemy_demo.py`](./fastapi_db_sync_sqlalchemy_demo.py)
