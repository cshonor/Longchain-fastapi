# FastAPI 安全机制（四）OAuth2 scopes

**scopes** 是一组**字符串权限标签**（OAuth2 里习惯用**空格分隔**拼成一个 `scope` 字符串）。JWT 载荷里常存 **列表**（如 `["me", "items"]`）或等价字符串；路由用 **`Security(依赖, scopes=[...])`** 声明本接口需要的权限，依赖里结合 **`SecurityScopes`** 与 Token 中的 scopes 做校验。

（上一篇：[OAuth2 + JWT 完整登录验证流程](./03_oauth2_jwt_full_auth_flow.md)）

---

## 一、scopes 是什么

- **细粒度权限**：用短字符串区分能力，如 `me`、`items`、`users:read`。  
- OAuth2 请求里常见形式：**一个**表单字段 **`scope`**，值为 **`"me items"`** 这类空格分隔串。  
- 作用：同一套登录体系下，不同 Token 可携带不同权限，接口按 scope **放行或拒绝**。

---

## 二、使用步骤

### 1. 在 `OAuth2PasswordBearer` 上登记 scopes（给 OpenAPI / Swagger 用）

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    scopes={
        "me": "查看自己信息",
        "items": "查看项目",
        "admin": "管理员权限",
    },
)
```

`tokenUrl` 一般与 **`POST /token`** 路径一致（注意前导 **`/`**）。

### 2. 登录时在 JWT 里写入 scopes

**OAuth2 标准表单字段是 `scope`（单数）**，不是 `scopes`。例如：

```python
# form_data: OAuth2PasswordRequestForm
requested = [s for s in (form_data.scope or "").split() if s]
```

生产环境常见做法：根据**用户角色/数据库**得到 `user_allowed`，再与 **`requested` 求交集**（或只信任服务端分配的权限），把结果写入 Token：

```python
access_token = create_access_token(
    data={
        "sub": user.username,
        "scopes": granted_list,  # 如 ["me", "items"]
    },
)
```

（不要把「客户端声称的权限」原样写进 Token 而不校验。）

### 3. 路由上用 `Security` 声明所需 scope

```python
from fastapi import Security

@app.get("/users/me")
async def read_me(
    current_user: User = Security(get_current_user, scopes=["me"]),
):
    return current_user
```

**`Security`** 在依赖注入上与 **`Depends`** 类似，但会参与 **scopes 的收集与校验**；适合「既要依赖又要权限」的场景。

### 4. 在共享依赖里读取 `SecurityScopes` 并校验 Token

```python
from fastapi.security import SecurityScopes

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    token_scopes = payload.get("scopes", [])
    if isinstance(token_scopes, str):
        token_scopes = [s for s in token_scopes.split() if s]

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=403,
                detail="权限不足",
                headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'},
            )
    ...
```

签名失败、过期等仍应捕获 **`jwt.PyJWTError`** 并返回 **401**；**scope 不够**时常用 **403**，并在 **`WWW-Authenticate`** 里带上 **`scope="..."`** 提示客户端需要哪些权限。

---

## 三、scopes 合并规则

依赖树里若有多处使用 **`Security(..., scopes=[...])`**，FastAPI 会把这些 scope **合并**进当前请求解析用到的 **`SecurityScopes.scopes`**。例如：

- 外层路由需要 **`items`**  
- 其依赖链上另一处 `Security` 需要 **`me`**  

则 **`get_current_user`** 里看到的可能是 **`["me", "items"]`**（顺序不保证）；Token 中必须**同时具备**这些 scope 才能通过（除非你在中间某层已单独校验并收窄）。

---

## 一句话

**scopes = 细粒度权限标签；`Security` = 带 scope 声明的依赖；Token 里带 scopes，在依赖里用 `SecurityScopes` 与 JWT 载荷对照校验。**

---

## 可运行示例

见 [`fastapi_security_oauth2_scopes_demo.py`](./fastapi_security_oauth2_scopes_demo.py)（`johndoe` / `admin`，密码均为 **`secret`**，scopes 不同）。
