# CHANGELOG

本文件记录 `funlogin` 的版本变更，按版本倒序排列。

## [未发布]

对照 [todo-list#430](https://github.com/farfarfun/todo-list/issues/430)、
[#565](https://github.com/farfarfun/todo-list/issues/565)、
[#694](https://github.com/farfarfun/todo-list/issues/694)（org 级合规审计）核实并修复的问题，
基于当前 1.0.10：

### 新增

- 新增 `scripts/setup.sh` + `scripts/services/{backend,frontend}.sh` + `scripts/lib/pid.sh`，统一管理
  `example/` 示例服务的启停（`start` 后台运行、`run` 前台运行；后端需指定 `dev`/`prod`，
  前端是纯静态测试页只支持 `dev`；运行时文件落在 `.run/`）
- `pyproject.toml` 新增 `postgres`（`asyncpg`）、`mysql`（`aiomysql`）、`sms-aliyun`
  （`alibabacloud-dysmsapi20170525`）三个 extras，基础安装只保留 SQLite 支持

### 修复

- `jwt_secret` 不再有硬编码默认值，未配置直接启动失败，避免多套部署共用同一固定密钥
- `pyproject.toml` 补齐 `license = "MIT"`，与仓库 `LICENSE`、README 三处协议声明保持一致
- 运行时依赖与测试依赖补齐版本下限（如 `fastapi>=0.110`），避免装到过旧版本
- 阿里云短信发送失败时改为记录带上下文的日志（脱敏手机号、签名、模板、错误详情），不再静默吞掉异常
- `.gitignore` 启用 `.idea/`、`.vscode/` 规则，并补充 `.run/`、`logs/`、`*.rar`、`node_modules/`
- 移除 `code_store.py` 中未使用的 `typing.Optional` 导入
- PostgreSQL、MySQL、阿里云短信 SDK 从核心依赖移入对应 extras，避免只用默认 SQLite 的场景
  被迫装上述重依赖
- CORS 默认配置改为仅放行本机回环地址（`http://127.0.0.1`/`http://localhost`），不再默认
  `allow_origins=["*"]` 搭配 `allow_credentials=True`；生产跨域来源通过
  `FUNLOGIN_CORS_ORIGINS` 显式配置白名单
- 前端示例脚本 `scripts/services/frontend.sh` 去掉 `prod` 模式：纯静态测试页没有独立于
  源码的「正式产物」概念，保留 `prod` 只会诱导把源码目录当生产服务绑 `0.0.0.0` 对外暴露

### 变更

- 公开函数/路由（`core/response.py`、`auth/router.py`、`oauth/qq.py`、`oauth/wechat.py` 等）补充类型标注与中文 docstring
- `auth/service.py`、`bind/service.py`、`auth/repository.py`、`bind/repository.py` 及
  `auth/router.py`/`bind/router.py` 的依赖工厂函数补齐中文 docstring
- 源码内英文注释改为中文（`oauth/qq.py`、`oauth/wechat.py`、`sms/code_store.py`）
- `scripts/generate_openapi.py` 用 `farlog` 记录状态，不再用 `print`
- README 末尾追加组织统一的「关于 farfarfun」区块
- README 标准安装/开发流程改为 `uv venv` + `uv sync`，`pip` 保留为非推荐兼容方式

## [1.0.9]

### 新增

- 新增用户角色管理与信息查询接口（`PATCH /api/auth/role`、`GET /api/auth/me`）

## [1.0.8]

### 变更

- 仅调整版本号，无功能性修改

## [1.0.7]

首个功能完整版本。

### 新增

- 注册/登录支持用户名+密码、邮箱+密码、手机号+短信验证码三种方式
- JWT access/refresh token 签发、校验与刷新
- QQ、微信 OAuth2 授权绑定
- 阿里云短信验证码发送与校验（含本地降级存码）
- Alembic 数据库迁移脚本与初始 schema（`User`、`UserCredential`、`QQBinding`、
  `WeChatBinding`、`PhoneBinding`）

## [1.0.6]

### 变更

- 仅调整版本号，无功能性修改

## [1.0.5]

### 变更

- 仅调整版本号，无功能性修改

## [1.0.4]

### 变更

- 仅调整版本号，无功能性修改

## [1.0.3]

### 变更

- 仅调整版本号，无功能性修改

## [1.0.2]

### 新增

- 项目初始化：基础配置与元数据文件
