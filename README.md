# 精力恢复记事本

只记录已完成的事，不列计划、不评价。支持 AI 每周/每月小结（可选）。

## 后端

cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash；Linux/macOS 用 .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env          # 可选：填入 LLM_API_KEY 以启用 AI 小结
uvicorn app.main:app --reload

## 前端

cd frontend
npm install
npm run dev

## 大模型配置（可选）

在 backend/.env 中设置：

- LLM_API_KEY：必填，缺失则不启用 AI 小结（退化为纯拼接）
- LLM_BASE_URL：默认 https://api.deepseek.com
- LLM_MODEL：默认 deepseek-chat

## 测试

cd backend && python -m pytest -v

## 部署到服务器（Docker）

前提：服务器已安装 Docker 与 Docker Compose 插件（私有仓库需先在服务器配置 GitHub 认证）。

```bash
# 1. 安装 Docker（Ubuntu/Debian 一键脚本，装完重新登录或重启）
curl -fsSL https://get.docker.com | sh

# 2. 拉取代码
git clone https://github.com/www19981013/record_daily_things.git
cd record_daily_things

# 3. 配置环境变量
cp .env.example .env
vim .env          # 见下方配置项

# 4. 构建并启动
docker compose up -d --build

# 5. 验证后端
curl http://localhost:32100/api/health   # 应返回 {"status":"ok"}
```

`.env` 配置项：

```ini
LLM_API_KEY=sk-xxx          # 可选，不填则小结退化为纯拼接
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
AUTH_USER=admin             # 必填：访问时的登录用户名
AUTH_PASS=你的密码            # 必填：访问时的登录密码
APP_PORT=32100              # 对外访问端口，可按需修改
```

最后在云服务器安全组/防火墙放行 **32100**（即 `APP_PORT`）端口，浏览器访问 `http://<服务器IP>:32100`。

数据保存在宿主机 `./data/record.db`（SQLite 文件），备份该文件即可。

### 更新部署

本地推代码后，在服务器上执行：

```bash
git pull && docker compose up -d --build
```

### 修改配置后如何生效

改完 `.env` 后，执行：

```bash
docker compose up -d    # 重新读取 .env 并重建受影响的容器
```

- 不要用 `docker compose restart`：它只是重启现有容器，**不会重新读取 `.env`**，改动不生效。
- `up -d` 会自动判断哪些容器要重建；数据在 `./data` 卷中，重建容器不丢数据。
- 生效范围：`APP_PORT` → 重建 frontend；`AUTH_USER` / `AUTH_PASS` → 重建 frontend（重新生成 htpasswd）；`LLM_*` → 重建 backend。
- 可用 `docker compose config` 查看 compose 解析后的最终配置，确认改动被正确读取。

> 访问已启用 HTTP Basic Auth：首次打开会弹出用户名/密码框，输入 `.env` 里的 `AUTH_USER` / `AUTH_PASS` 即可。两者必须都设置，否则 nginx 容器会启动失败。
