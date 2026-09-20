# funlogin 示例

## 启动

确保已安装依赖：`uv pip install -e .`
启动后端时会自动创建数据库表。

统一通过项目根目录的 `scripts/setup.sh` 管理后端 / 前端两个示例服务的生命周期
（`start` 后台运行，`run` 前台运行，均需指定 `dev` 或 `prod`）：

```bash
# 前台调试用：后端热重载（端口 8001）
./scripts/setup.sh run backend dev

# 另开一个终端：前端静态测试页（端口 3001）
./scripts/setup.sh run frontend dev

# 或者后台启动 + 查看状态 + 停止
./scripts/setup.sh start backend dev
./scripts/setup.sh status
./scripts/setup.sh stop backend dev
```

`prod` 模式的后端只允许运行**已安装的正式 `funlogin` 包**（`pip install funlogin` /
`uv pip install funlogin`），未安装会直接报错退出，不会回退到源码。

后端地址：http://127.0.0.1:8001 ，API 文档：http://127.0.0.1:8001/docs

## 前端测试页

启动前端服务后访问 http://127.0.0.1:3001 ，页面中的「API 地址」默认为
http://127.0.0.1:8001/api ，可修改后测试注册、登录与绑定列表。
