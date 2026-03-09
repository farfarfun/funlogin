#!/usr/bin/env python3
"""生成 funlogin 的 OpenAPI (Swagger) JSON 到 docs/openapi.json，便于其他包调用。"""

import json
import os

from fastapi import FastAPI

from funlogin import router

app = FastAPI(
    title="funlogin API",
    description="用户注册、登录（JWT）、QQ/微信/手机绑定",
    version="1.0",
)
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    schema = app.openapi()
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(docs_dir, exist_ok=True)
    out = os.path.join(docs_dir, "openapi.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
    print(f"Written {out}")
