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

## API 列表

### 认证 (Auth)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/send-code` | 发送手机验证码（phone） |
| POST | `/auth/register` | 注册（username+password / email+password / phone+code） |
| POST | `/auth/login` | 登录 |
| POST | `/auth/refresh` | 刷新 Token |

### 绑定 (Bind)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/bind/phone/send-code` | 发送手机验证码（需 JWT） |
| POST | `/bind/phone` | 绑定手机 |
| GET | `/bind/qq/authorize` | 获取 QQ 授权 URL |
| POST | `/bind/qq/callback` | QQ 回调绑定 |
| GET | `/bind/wechat/authorize` | 获取微信授权 URL |
| POST | `/bind/wechat/callback` | 微信回调绑定 |
| GET | `/bind/list` | 查询绑定列表（需 JWT） |

## 数据库迁移

```bash
alembic upgrade head
```

## 开发

```bash
pip install -e ".[test]"
pytest -v
```
