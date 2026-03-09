# funlogin 用户认证与绑定 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现 funlogin 公共包：用户注册、登录（JWT）、QQ/微信/手机绑定，FastAPI + 异步 SQLAlchemy + 阿里云短信。

**Architecture:** 按功能分模块（auth / bind / oauth / sms），每模块内部 Repository → Service → Router 分层。配置用 Pydantic Settings，支持 SQLite/MySQL/PostgreSQL 切换。

**Tech Stack:** FastAPI, SQLAlchemy 2.0 async, aiosqlite/asyncpg/aiomysql, PyJWT, passlib, httpx, alibabacloud-dysmsapi20170525, Alembic.

**参考设计：** `docs/plans/2025-03-09-funlogin-auth-design.md`

---

## Phase 1: 项目骨架与基础设施

### Task 1: 添加依赖到 pyproject.toml

**Files:**
- Modify: `pyproject.toml`

**Step 1:** 在 `[project]` 下添加 `dependencies` 列表，包含：fastapi, uvicorn, pydantic-settings, sqlalchemy[asyncio], aiosqlite, asyncpg, aiomysql, pyjwt, passlib[bcrypt], httpx, alibabacloud-dysmsapi20170525, alembic

**Step 2:** 安装依赖并验证

Run: `pip install -e .`
Expected: 无报错

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add funlogin dependencies"
```

---

### Task 2: 创建 config.py（Pydantic Settings）

**Files:**
- Create: `src/funlogin/config.py`
- Create: `tests/test_config.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py
from funlogin.config import get_settings

def test_get_settings_returns_settings():
    s = get_settings()
    assert s is not None
    assert hasattr(s, "database_url")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL (ImportError or AttributeError)

**Step 3: Implement config.py**

- 定义 `FunloginSettings` 类继承 `BaseSettings`，包含：database_url, jwt_secret, jwt_algorithm, jwt_access_expire, jwt_refresh_expire, qq_app_id, qq_app_key, wechat_app_id, wechat_app_secret, aliyun_access_key, aliyun_secret, aliyun_sms_sign, aliyun_sms_template
- 使用 `model_config = SettingsConfigDict(env_prefix="FUNLOGIN_")` 或 `env_file=".env"`
- 实现 `get_settings()` 返回单例

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/funlogin/config.py tests/test_config.py
git commit -m "feat: add config with Pydantic Settings"
```

---

### Task 3: 创建 core/database.py（异步 SQLAlchemy）

**Files:**
- Create: `src/funlogin/core/__init__.py`
- Create: `src/funlogin/core/database.py`
- Create: `tests/test_database.py`

**Step 1: Write the failing test**

验证 `create_async_engine` 和 `async_sessionmaker` 能被正确创建，且 `get_async_session` 依赖可用。

**Step 2:** Run test, expect FAIL

**Step 3:** 实现 database.py
- 使用 `create_async_engine(settings.database_url, echo=False)`
- `AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)`
- `async def get_async_session()` 作为 FastAPI 依赖

**Step 4:** Run test, expect PASS

**Step 5: Commit**

```bash
git add src/funlogin/core/*.py tests/test_database.py
git commit -m "feat: add async SQLAlchemy database layer"
```

---

### Task 4: 创建 core/security.py（密码哈希）

**Files:**
- Create: `src/funlogin/core/security.py`
- Create: `tests/test_security.py`

**Step 1:** 写测试：`hash_password("test")` 返回非原文；`verify_password("test", hashed)` 为 True

**Step 2-5:** 实现 + 验证 + Commit

---

### Task 5: 创建 core/jwt.py（JWT 签发与校验）

**Files:**
- Create: `src/funlogin/core/jwt.py`
- Create: `tests/test_jwt.py`

**Step 1:** 写测试：`create_access_token({"sub": "1"})` 返回字符串；`decode_token(token)` 解析出 sub

**Step 2-5:** 实现 + 验证 + Commit

---

## Phase 2: 数据模型与迁移

### Task 6: 创建 models/user.py 和 models/bindings.py

**Files:**
- Create: `src/funlogin/models/__init__.py`
- Create: `src/funlogin/models/user.py`
- Create: `src/funlogin/models/bindings.py`

**Step 1:** 定义 User（id, created_at, updated_at）、UserCredential（user_id, type, identifier, secret_hash, unique constraint on type+identifier）

**Step 2:** 定义 QQBinding、WeChatBinding、PhoneBinding（含 user_id FK 和唯一约束）

**Step 3:** 在 `models/__init__.py` 导出所有模型

**Step 4: Commit**

---

### Task 7: 配置 Alembic 并生成初始迁移

**Files:**
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/001_initial.py`

**Step 1:** 运行 `alembic init alembic`，调整 env.py 使用 async engine 和 FunloginSettings.database_url

**Step 2:** 生成迁移：`alembic revision --autogenerate -m "initial"`

**Step 3:** 运行 `alembic upgrade head` 验证

**Step 4: Commit**

---

## Phase 3: auth 模块（注册、登录）

### Task 8: auth repository

**Files:**
- Create: `src/funlogin/auth/__init__.py`
- Create: `src/funlogin/auth/repository.py`
- Create: `tests/auth/test_repository.py`

**Step 1:** 写测试：create_user, get_user_by_id, get_credential_by_identifier, create_credential

**Step 2-5:** 实现 + 验证 + Commit

---

### Task 9: auth service（注册逻辑）

**Files:**
- Create: `src/funlogin/auth/service.py`
- Create: `tests/auth/test_service.py`

**Step 1:** 写测试：register_with_username_password 成功；重复 username 失败

**Step 2-5:** 实现 + 验证 + Commit

---

### Task 10: auth service（登录逻辑）

**Step 1:** 写测试：login 成功返回 tokens；错误密码失败

**Step 2-5:** 实现 + 验证 + Commit

---

### Task 11: auth router（register, login, refresh）

**Files:**
- Create: `src/funlogin/auth/router.py`
- Create: `tests/auth/test_router.py`（使用 TestClient）

**Step 1:** 写测试：POST /auth/register 返回 200 和 code=0；POST /auth/login 返回 access_token

**Step 2-5:** 实现 + 验证 + Commit

---

## Phase 4: sms 与 oauth 模块

### Task 12: sms/aliyun.py（阿里云短信发送与校验）

**Files:**
- Create: `src/funlogin/sms/__init__.py`
- Create: `src/funlogin/sms/aliyun.py`
- Create: `src/funlogin/sms/code_store.py`（内存/Redis 存验证码，开发阶段内存即可）
- Create: `tests/sms/test_aliyun.py`（mock 阿里云 API）

**Step 1:** 定义 `send_sms_code(phone: str, code: str) -> bool` 和 `verify_code(phone: str, code: str) -> bool`

**Step 2-5:** 实现 + 验证 + Commit

---

### Task 13: oauth/qq.py 和 oauth/wechat.py

**Files:**
- Create: `src/funlogin/oauth/__init__.py`
- Create: `src/funlogin/oauth/qq.py`
- Create: `src/funlogin/oauth/wechat.py`
- Create: `tests/oauth/test_qq.py`（mock httpx）

**Step 1:** 实现 QQ：get_authorize_url(state), exchange_code_for_user_info(code) -> {openid, unionid, nickname, avatar}

**Step 2:** 实现微信类似逻辑

**Step 3-5:** 验证 + Commit

---

## Phase 5: bind 模块

### Task 14: bind repository 和 service

**Files:**
- Create: `src/funlogin/bind/__init__.py`
- Create: `src/funlogin/bind/repository.py`
- Create: `src/funlogin/bind/service.py`
- Create: `tests/bind/test_service.py`

**Step 1:** 写测试：bind_phone, bind_qq, bind_wechat, list_bindings

**Step 2-5:** 实现 + 验证 + Commit

---

### Task 15: bind router

**Files:**
- Create: `src/funlogin/bind/router.py`
- Create: `tests/bind/test_router.py`

**Step 1:** 实现 POST /bind/phone/send-code, POST /bind/phone, GET /bind/qq/authorize, GET /bind/qq/callback, 微信同理, GET /bind/list

**Step 2:** 使用 `get_current_user` 依赖（从 JWT 解析 user_id）

**Step 3:** 写集成测试验证

**Step 4: Commit**

---

## Phase 6: 路由聚合与统一响应

### Task 16: 统一响应格式与异常处理

**Files:**
- Create: `src/funlogin/core/response.py`
- Modify: `src/funlogin/auth/router.py`
- Modify: `src/funlogin/bind/router.py`

**Step 1:** 定义 `success(data)`、`fail(code, message)` 响应结构

**Step 2:** 添加全局异常处理，将 HTTPException 映射为统一格式

**Step 3: Commit**

---

### Task 17: 主 router 与 get_current_user 依赖

**Files:**
- Create: `src/funlogin/router.py`
- Create: `src/funlogin/deps.py`（get_current_user）
- Modify: `src/funlogin/__init__.py`（导出 router）

**Step 1:** `router = APIRouter()`; `router.include_router(auth.router, prefix="/auth")`; `router.include_router(bind.router, prefix="/bind")`

**Step 2:** 实现 `get_current_user` 从 Authorization Bearer token 解析并查询 User

**Step 3:** 写示例 main.py 或 README 集成说明

**Step 4: Commit**

---

## Phase 7: 收尾

### Task 18: 补充 auth 的 phone/email 注册与登录

**Files:**
- Modify: `src/funlogin/auth/service.py`
- Modify: `src/funlogin/auth/router.py`

**Step 1:** 支持 email+password、phone+code 注册与登录

**Step 2:** 写测试覆盖

**Step 3: Commit**

---

### Task 19: 更新 README 与 pyproject description

**Files:**
- Modify: `README.md`
- Modify: `pyproject.toml`

**Step 1:** README 包含：安装、配置项、快速集成示例、API 列表

**Step 2: Commit**

```bash
git add README.md pyproject.toml
git commit -m "docs: add README and usage guide"
```

---

## 执行选项

**Plan 已保存到 `docs/plans/2025-03-09-funlogin-auth-implementation.md`。两种执行方式：**

**1. Subagent-Driven（当前会话）** — 按任务派发子 agent，任务间做代码审查，迭代快  

**2. Parallel Session（独立会话）** — 在新会话中用 executing-plans，按 checkpoint 批量执行  

**请选择？**
