# funlogin 用户认证与绑定 设计文档

**日期：** 2025-03-09  
**状态：** 已定稿

---

## 1. 目标与范围

开发一个 Python 公共包 **funlogin**，提供完整的用户注册、登录、QQ 绑定、微信绑定、手机绑定等服务端能力。接入方可作为 FastAPI 路由直接挂载，或使用底层 Service 自定义实现。

---

## 2. 技术选型

| 项目 | 选型 |
|------|------|
| Web 框架 | FastAPI |
| 数据库 | 异步 SQLAlchemy（开发用 SQLite，生产可切换 MySQL/PostgreSQL） |
| 认证 | JWT（无状态） |
| 第三方 | QQ 互联、微信开放平台 OAuth；阿里云短信 |

---

## 3. 架构与目录结构

```
src/funlogin/
├── __init__.py
├── config.py              # 配置（Pydantic Settings）
├── models/                # 共享数据模型
│   ├── __init__.py
│   ├── user.py            # User, UserCredential
│   └── bindings.py        # QQ/微信/手机绑定记录
├── core/                  # 核心基础设施
│   ├── __init__.py
│   ├── database.py        # 异步 SQLAlchemy 引擎与会话
│   ├── jwt.py             # JWT 签发与校验
│   └── security.py        # 密码哈希
├── auth/                  # 注册与登录
│   ├── __init__.py
│   ├── repository.py
│   ├── service.py
│   └── router.py
├── bind/                  # QQ/微信/手机绑定
│   ├── __init__.py
│   ├── repository.py
│   ├── service.py
│   └── router.py
├── oauth/                 # 第三方 OAuth 实现
│   ├── __init__.py
│   ├── qq.py
│   └── wechat.py
├── sms/                   # 短信验证码（阿里云）
│   ├── __init__.py
│   └── aliyun.py
└── router.py              # 汇总路由
```

---

## 4. 数据模型

| 表/模型 | 字段 | 说明 |
|--------|------|------|
| **User** | id, created_at, updated_at | 主用户表 |
| **UserCredential** | user_id, type, identifier, secret_hash | type: username/email/phone；identifier 为账号；secret_hash 为密码或空 |
| **QQBinding** | user_id, openid, unionid, nickname, avatar_url, created_at | QQ 绑定记录 |
| **WeChatBinding** | user_id, openid, unionid, nickname, avatar_url, created_at | 微信绑定记录 |
| **PhoneBinding** | user_id, phone, created_at | 手机号绑定 |

- User 与 Credential 分离：一个 User 可有多种登录方式
- 绑定表分别维护 QQ/微信/手机绑定关系
- 唯一约束：同一 openid/unionid/phone 仅能绑定一个 user_id

---

## 5. API 接口清单

### 认证（auth）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/register` | 注册（username/email/phone + password 或 phone + code） |
| POST | `/auth/login` | 登录，返回 JWT |
| POST | `/auth/refresh` | 刷新 Token |

### 绑定（bind）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/bind/phone/send-code` | 发送手机验证码（需 JWT） |
| POST | `/bind/phone` | 绑定手机（需 JWT） |
| GET | `/bind/qq/authorize` | 跳转 QQ 授权页 |
| GET | `/bind/qq/callback` | QQ OAuth 回调 |
| GET | `/bind/wechat/authorize` | 跳转微信授权页 |
| GET | `/bind/wechat/callback` | 微信 OAuth 回调 |
| GET | `/bind/list` | 查询当前用户绑定列表（需 JWT） |

---

## 6. 错误处理与响应格式

**成功：** `{"code": 0, "data": {...}, "message": "ok"}`  
**失败：** `{"code": 40001, "data": null, "message": "..."}`

| code | 含义 |
|------|------|
| 0 | 成功 |
| 40001 | 业务错误 |
| 40101 | 未登录 / Token 无效 |
| 40102 | Token 已过期 |
| 40301 | 禁止访问 |
| 50001 | 服务端内部错误 |

---

## 7. 配置与集成

**配置项：** DATABASE_URL, JWT_SECRET, JWT_*EXPIRE, QQ_APP_ID/KEY, WECHAT_APP_ID/SECRET, ALIYUN_* 等，通过 Pydantic Settings + 环境变量。

**集成方式 1：** `app.include_router(funlogin.router, prefix="/api")`  
**集成方式 2：** 使用 AuthService / BindService 等底层服务自定义路由。

**数据库迁移：** Alembic。

---

## 8. 依赖

- fastapi, uvicorn, pydantic-settings
- sqlalchemy[asyncio], aiosqlite, asyncpg, aiomysql
- pyjwt, passlib, httpx
- alibabacloud-dysmsapi20170525
