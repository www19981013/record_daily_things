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

前提：服务器已安装 Docker 与 Docker Compose 插件。

1. 上传代码到服务器（`git clone` 或直接拷贝整个目录）
2. 在项目根目录创建 `.env`：
   ```
   LLM_API_KEY=sk-xxx          # 可选，不填则小结退化为纯拼接
   LLM_BASE_URL=https://api.deepseek.com
   LLM_MODEL=deepseek-chat
   AUTH_USER=admin             # 必填：访问时的登录用户名
   AUTH_PASS=你的密码            # 必填：访问时的登录密码
   ```
3. 构建并启动：
   ```bash
   docker compose up -d --build
   ```
4. 云服务器安全组/防火墙放行 **80** 端口，浏览器访问 `http://<服务器IP>`

数据保存在宿主机 `./data/record.db`（SQLite 文件），备份该文件即可。

更新部署：

```bash
git pull && docker compose up -d --build
```

> 访问已启用 HTTP Basic Auth：首次打开会弹出用户名/密码框，输入 `.env` 里的 `AUTH_USER` / `AUTH_PASS` 即可。两者必须都设置，否则 nginx 容器会启动失败。
