#!/usr/bin/env bash
# 启动前端静态服务（端口 3001）
cd "$(dirname "$0")/frontend" && echo "前端: http://127.0.0.1:3001" && python3 -m http.server 3001
