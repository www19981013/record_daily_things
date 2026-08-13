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
