# docs

## openapi.json

[openapi.json](./openapi.json) 为 funlogin API 的 **OpenAPI 3.1 (Swagger)** 描述，便于其他包或前端根据规范生成客户端或做联调。

- 路径前缀：`/api`（认证 `/api/auth/*`，绑定 `/api/bind/*`）
- 生成方式：在项目根目录执行  
  `uv run python scripts/generate_openapi.py`  
  会覆盖当前 `docs/openapi.json`。

其他项目可基于该 JSON 使用 OpenAPI Generator、Swagger Codegen 等工具生成调用代码，或直接用于 Mock/文档展示。
