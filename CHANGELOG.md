# CHANGELOG

本文件记录 `funlogin` 的版本变更，按版本倒序排列。

> 说明：`funlogin` 在 1.0.10 之前没有维护 CHANGELOG，历史版本号（1.0.1 ~ 1.0.10）
> 对应的具体变更请查阅 git 提交历史。从本文件建立之日起，后续发布均按下述格式记录。

## [未发布]

对照 [todo-list#430](https://github.com/farfarfun/todo-list/issues/430)（org 级合规审计）核实并修复的问题，
基于当前 1.0.10：

### 新增

- 新增 `scripts/setup.sh` + `scripts/services/{backend,frontend}.sh` + `scripts/lib/pid.sh`，统一管理
  `example/` 示例服务的启停（`start` 后台运行、`run` 前台运行，均需指定 `dev`/`prod`；运行时文件落在 `.run/`）

### 修复

- `jwt_secret` 不再有硬编码默认值，未配置直接启动失败，避免多套部署共用同一固定密钥
- `pyproject.toml` 补齐 `license = "MIT"`，与仓库 `LICENSE`、README 三处协议声明保持一致
- 运行时依赖与测试依赖补齐版本下限（如 `fastapi>=0.110`），避免装到过旧版本
- 阿里云短信发送失败时改为记录带上下文的日志（脱敏手机号、签名、模板、错误详情），不再静默吞掉异常
- `.gitignore` 启用 `.idea/`、`.vscode/` 规则，并补充 `.run/`、`logs/`、`*.rar`、`node_modules/`
- 移除 `code_store.py` 中未使用的 `typing.Optional` 导入

### 变更

- 公开函数/路由（`core/response.py`、`auth/router.py`、`oauth/qq.py`、`oauth/wechat.py` 等）补充类型标注与中文 docstring
- 源码内英文注释改为中文（`oauth/qq.py`、`oauth/wechat.py`、`sms/code_store.py`）
- `scripts/generate_openapi.py` 用 `farlog` 记录状态，不再用 `print`
- README 末尾追加组织统一的「关于 farfarfun」区块

## [1.0.10] 及更早

功能性变更（注册/登录/JWT 签发与刷新、QQ 与微信 OAuth 绑定、手机号短信验证码、Alembic 迁移等）
均已完成，详见 git 提交历史；未按本文件格式追溯记录。
