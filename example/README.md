# funlogin 示例

## 启动

确保已安装依赖：`uv pip install -e .`  
启动后端时会自动创建数据库表。

在 **项目根目录** 执行（脚本会自行切换到正确目录）：

```bash
# 终端 1：启动后端（端口 8001）
./example/start_backend.sh

# 终端 2：启动前端静态服务（端口 3001）
./example/start_frontend.sh
```

后端地址：http://127.0.0.1:8001 ，API 文档：http://127.0.0.1:8001/docs

## 前端测试页

运行 `start_frontend.sh` 后访问 http://127.0.0.1:3001

然后访问 http://127.0.0.1:3001 ，页面中的「API 地址」默认为 http://127.0.0.1:8001/api ，可修改后测试注册、登录与绑定列表。
