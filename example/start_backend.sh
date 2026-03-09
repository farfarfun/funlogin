#!/usr/bin/env bash
# 在项目根目录启动 funlogin 示例后端（端口 8001）
cd "$(dirname "$0")/.." && uv run uvicorn example.app:app --reload --port 8001
