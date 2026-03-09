# funlogin

用户注册、登录（JWT）、QQ/微信/手机绑定的 FastAPI 公共包。

## 安装

```bash
pip install -e .
# 或
uv pip install -e .
```

## 配置

通过环境变量（前缀 `FUNLOGIN_`）或 `.env` 配置：

| 变量 | 说明 | 默认 |
|------|------|------|
| `FUNLOGIN_DATABASE_URL` | 数据库连接 | `sqlite+aiosqlite:///./funlogin.db` |
| `FUNLOGIN_JWT_SECRET` | JWT 密钥 | `change-me-in-production` |
| `FUNLOGIN_JWT_ALGORITHM` | JWT 算法 | `HS256` |
| `FUNLOGIN_JWT_ACCESS_EXPIRE` | Access Token 过期秒数 | `3600` |
| `FUNLOGIN_JWT_REFRESH_EXPIRE` | Refresh Token 过期秒数 | `604800` |
| `FUNLOGIN_QQ_APP_ID` | QQ 互联 AppID | |
| `FUNLOGIN_QQ_APP_KEY` | QQ 互联 AppKey | |
| `FUNLOGIN_WECHAT_APP_ID` | 微信开放平台 AppID | |
| `FUNLOGIN_WECHAT_APP_SECRET` | 微信开放平台 Secret | |
| `FUNLOGIN_ALIYUN_ACCESS_KEY` | 阿里云 AccessKey | |
| `FUNLOGIN_ALIYUN_SECRET` | 阿里云 Secret | |
| `FUNLOGIN_ALIYUN_SMS_SIGN` | 短信签名 | |
| `FUNLOGIN_ALIYUN_SMS_TEMPLATE` | 短信模板 | |

## 快速集成

```python
from fastapi import FastAPI
from funlogin import router

app = FastAPI()
app.include_router(router, prefix="/api")

# 运行: uvicorn your_app:app
```

## API 接口（三方调用参考）

挂载后基础路径为 `/api`，以下接口均已联调通过。

**统一响应格式：**

```json
{"code": 0, "data": {...}, "message": "ok"}
```

| code | 含义 |
|------|------|
| 0 | 成功 |
| 40001 | 业务错误（如用户名已存在） |
| 40101 | 未登录 / Token 无效 |
| 40102 | Token 已过期 |
| 40301 | 禁止访问 |
| 50001 | 服务端内部错误 |

**需登录接口**：请求头加 `Authorization: Bearer <access_token>`。

---

### 认证 Auth

| 方法 | 路径 | 请求体 | 响应 data 示例 |
|------|------|--------|----------------|
| POST | `/api/auth/send-code` | `{"phone": "13800138000"}` | 无 |
| POST | `/api/auth/register` | `{"username": "alice", "password": "123456"}` 或 `{"email": "a@x.com", "password": "p"}` 或 `{"phone": "138...", "code": "123456"}` | `{"user_id": 1}` |
| POST | `/api/auth/login` | 同 register，二选一 | `{"access_token": "...", "refresh_token": "..."}` |
| POST | `/api/auth/refresh` | `{"refresh_token": "..."}` | `{"access_token": "...", "refresh_token": "..."}` |

---

### 绑定 Bind（需 JWT）

| 方法 | 路径 | 请求体 / 参数 | 响应 data 示例 |
|------|------|---------------|----------------|
| POST | `/api/bind/phone/send-code` | `{"phone": "13800138000"}` | 无 |
| POST | `/api/bind/phone` | `{"phone": "138...", "code": "123456"}` | 无 |
| GET | `/api/bind/qq/authorize` | Query: `redirect_uri=https://...` | `{"url": "...", "state": "..."}` |
| POST | `/api/bind/qq/callback` | `{"code": "...", "redirect_uri": "..."}` | 无 |
| GET | `/api/bind/wechat/authorize` | Query: `redirect_uri=https://...` | `{"url": "...", "state": "..."}` |
| POST | `/api/bind/wechat/callback` | `{"code": "..."}` | 无 |
| GET | `/api/bind/list` | 无 | `{"phone": ["138..."], "qq": [...], "wechat": [...]}` |

---

完整 OpenAPI 3.1 描述见 [docs/openapi.json](docs/openapi.json)，可用于生成客户端或 Mock。

## 数据库

示例应用启动时会自动创建表。若自行集成，在应用启动时调用一次 `await funlogin.core.database.init_db()` 即可建表。

## 开发

```bash
pip install -e ".[test]"
pytest -v
```
