# 05 — 安全机制（Security）

**核心内容**：API Key / OAuth2 概念、JWT 签发与校验、scopes 与授权。  
**核心目标**：保护接口，避免未授权访问。

对照代码：`fastapi_app/core/security.py`、`core/config.py` 中的密钥与过期配置。

---

## 本章笔记

- [安全机制简介（OAuth2、OIDC 与 OpenAPI 安全方案）](./01_security_introduction.md)
- [OAuth2 密码流 + JWT 签发 Token](./02_oauth2_jwt_token.md)
- [OAuth2 + JWT 完整登录验证流程](./03_oauth2_jwt_full_auth_flow.md)
- [OAuth2 scopes（细粒度权限与 Security）](./04_oauth2_scopes.md)
- [OAuth2 + JWT 签发 Demo（可直接跑）](./fastapi_security_oauth2_jwt_token_demo.py)
- [OAuth2 + JWT 完整流程 Demo（可直接跑）](./fastapi_security_oauth2_jwt_full_demo.py)
- [OAuth2 scopes Demo（可直接跑）](./fastapi_security_oauth2_scopes_demo.py)
