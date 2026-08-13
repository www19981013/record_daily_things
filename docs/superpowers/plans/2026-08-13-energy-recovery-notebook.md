# 精力恢复记事本工具 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建一个只记录"已完成的事"、不列计划、不评价的个人记事本，支持基于 AI 的每周/每月小结（未配置大模型时退化为纯拼接）。

**架构：** FastAPI 后端（REST API）+ Vue 3 前端（SPA），SQLite 存储，AI 层抽象出 `BaseLLM` 接口（默认 OpenAI 兼容的 DeepSeek，环境变量配置，可选）。

**技术栈：** Python 3.11+、FastAPI、SQLAlchemy 2.x、Pydantic v2、httpx、pytest；Vue 3 + Vite。

---

## 文件结构

```
record_daily_things/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 应用、CORS、路由挂载、健康检查
│   │   ├── config.py            # 环境变量读取（LLM 配置），llm_configured()
│   │   ├── db.py                # engine、SessionLocal、Base、get_db
│   │   ├── models.py            # Entry、Summary ORM 模型
│   │   ├── schemas.py           # Pydantic 请求/响应模型
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── entries.py       # 记录 CRUD
│   │   │   └── summaries.py     # 小结生成/查看
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # BaseLLM Protocol
│   │   │   ├── openai_compat.py # OpenAICompatibleLLM
│   │   │   └── prompts.py       # prompt 模板（含"不评价"约束）
│   │   └── services/
│   │       ├── __init__.py
│   │       └── summary_service.py # 周期计算、LLM/拼接小结编排
│   └── tests/
│       ├── conftest.py
│       ├── test_entries.py
│       ├── test_prompts.py
│       └── test_summaries.py
├── frontend/                    # Vite + Vue 3
│   ├── vite.config.js           # dev 代理 /api -> localhost:8000
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── api.js
│       └── components/
│           ├── EntryInput.vue
│           ├── EntryList.vue
│           └── SummaryView.vue
├── backend/requirements.txt
├── .env.example
└── .gitignore
```

**依赖说明：** `httpx` 用于调用 OpenAI 兼容 API；`python-dotenv` 加载 `.env`；`pytest` 测试。前端无自动化测试（手动验证）。

---

## 任务 1：项目脚手架与后端基础

**文件：**
- 创建：`.gitignore`、`.env.example`、`backend/requirements.txt`
- 创建：`backend/app/__init__.py`、`backend/app/main.py`
- 测试：`backend/tests/test_health.py`

- [ ] **步骤 1：初始化 git 并创建项目骨架文件**

```bash
git init
mkdir -p backend/app/routers backend/app/llm backend/app/services backend/tests
```

写入 `.gitignore`：
```
node_modules/
.venv/
__pycache__/
*.pyc
.env
record.db
dist/
.superpowers/
.claude/
```

写入 `.env.example`：
```
LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

写入 `backend/requirements.txt`：
```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
httpx
python-dotenv
pytest
```

- [ ] **步骤 2：创建后端虚拟环境并安装依赖**

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash；Linux/macOS 用 .venv/bin/activate
pip install -r requirements.txt
```

- [ ] **步骤 3：编写失败的测试**

`backend/tests/test_health.py`：
```python
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
```

- [ ] **步骤 4：运行测试验证失败**

```bash
cd backend && python -m pytest tests/test_health.py -v
```
预期：FAIL，报 `ModuleNotFoundError: No module named 'app.main'` 或 `ImportError`。

- [ ] **步骤 5：编写最少实现代码**

`backend/app/__init__.py`：空文件。

`backend/app/main.py`：
```python
from fastapi import FastAPI

app = FastAPI(title="精力恢复记事本")


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **步骤 6：运行测试验证通过**

```bash
cd backend && python -m pytest tests/test_health.py -v
```
预期：PASS。

- [ ] **步骤 7：Commit**

```bash
git add .gitignore .env.example backend/requirements.txt backend/app backend/tests
git commit -m "chore: scaffold backend with FastAPI health endpoint"
```

---

## 任务 2：数据模型与数据库层

**文件：**
- 创建：`backend/app/db.py`、`backend/app/models.py`
- 测试：`backend/tests/test_models.py`

- [ ] **步骤 1：编写失败的测试**

`backend/tests/test_models.py`：
```python
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.models import Entry, Summary


def _make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_create_entry():
    db = _make_session()
    entry = Entry(content="写完周报")
    db.add(entry)
    db.commit()
    db.refresh(entry)
    assert entry.id == 1
    assert entry.content == "写完周报"
    assert isinstance(entry.created_at, datetime)


def test_create_summary():
    db = _make_session()
    start = datetime(2026, 8, 10)
    end = datetime(2026, 8, 17)
    summary = Summary(
        period_type="weekly", period_start=start, period_end=end, content="本周小结"
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    assert summary.period_type == "weekly"
    assert summary.content == "本周小结"
```

- [ ] **步骤 2：运行测试验证失败**

```bash
cd backend && python -m pytest tests/test_models.py -v
```
预期：FAIL，报 `ModuleNotFoundError: No module named 'app.db'`。

- [ ] **步骤 3：编写最少实现代码**

`backend/app/db.py`：
```python
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./record.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

`backend/app/models.py`：
```python
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    period_type: Mapped[str] = mapped_column(String(20))
    period_start: Mapped[datetime] = mapped_column(DateTime)
    period_end: Mapped[datetime] = mapped_column(DateTime)
    content: Mapped[str] = mapped_column(String(10000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
```

- [ ] **步骤 4：运行测试验证通过**

```bash
cd backend && python -m pytest tests/test_models.py -v
```
预期：PASS。

- [ ] **步骤 5：Commit**

```bash
git add backend/app/db.py backend/app/models.py backend/tests/test_models.py
git commit -m "feat: add Entry and Summary models with SQLAlchemy"
```

---

## 任务 3：测试夹具 + 记录（entries）CRUD 路由

**文件：**
- 创建：`backend/tests/conftest.py`
- 创建：`backend/app/schemas.py`、`backend/app/routers/__init__.py`、`backend/app/routers/entries.py`
- 修改：`backend/app/main.py`（挂载路由）
- 测试：`backend/tests/test_entries.py`

- [ ] **步骤 1：编写共享测试夹具与失败的测试**

先创建 `backend/tests/conftest.py`：
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

再创建 `backend/tests/test_entries.py`：
```python
def test_create_entry(client):
    resp = client.post("/entries", json={"content": "写完周报"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["content"] == "写完周报"


def test_list_entries(client):
    client.post("/entries", json={"content": "第一件事"})
    client.post("/entries", json={"content": "第二件事"})
    resp = client.get("/entries")
    assert resp.status_code == 200
    contents = [e["content"] for e in resp.json()]
    assert contents == ["第二件事", "第一件事"]  # 按时间倒序


def test_delete_entry(client):
    created = client.post("/entries", json={"content": "要删除的"}).json()
    resp = client.delete(f"/entries/{created['id']}")
    assert resp.status_code == 204
    assert client.get("/entries").json() == []


def test_delete_missing_entry_returns_404(client):
    resp = client.delete("/entries/999")
    assert resp.status_code == 404
```

- [ ] **步骤 2：运行测试验证失败**

```bash
cd backend && python -m pytest tests/test_entries.py -v
```
预期：FAIL，报 404（路由未挂载）或 `AttributeError`（schemas 未定义）。

- [ ] **步骤 3：编写最少实现代码**

`backend/app/schemas.py`：
```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EntryCreate(BaseModel):
    content: str


class EntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    created_at: datetime


class SummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    period_type: str
    period_start: datetime
    period_end: datetime
    content: str
    created_at: datetime
```

`backend/app/routers/__init__.py`：空文件。

`backend/app/routers/entries.py`：
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db

router = APIRouter(prefix="/entries", tags=["entries"])


@router.post("", response_model=schemas.EntryOut, status_code=201)
def create_entry(payload: schemas.EntryCreate, db: Session = Depends(get_db)):
    entry = models.Entry(content=payload.content)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=list[schemas.EntryOut])
def list_entries(db: Session = Depends(get_db)):
    return db.query(models.Entry).order_by(models.Entry.created_at.desc()).all()


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.get(models.Entry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
```

`backend/app/main.py` 改为：
```python
from fastapi import FastAPI

from .db import Base, engine
from .routers import entries

Base.metadata.create_all(bind=engine)

app = FastAPI(title="精力恢复记事本")
app.include_router(entries.router)


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **步骤 4：运行测试验证通过**

```bash
cd backend && python -m pytest tests/test_entries.py -v
```
预期：PASS。

- [ ] **步骤 5：Commit**

```bash
git add backend/app/schemas.py backend/app/routers backend/app/main.py backend/tests/conftest.py backend/tests/test_entries.py
git commit -m "feat: add entries CRUD endpoints with test fixture"
```

---

## 任务 4：AI 抽象层与 prompt（不评价约束）

**文件：**
- 创建：`backend/app/llm/__init__.py`、`backend/app/llm/base.py`、`backend/app/llm/prompts.py`、`backend/app/llm/openai_compat.py`、`backend/app/config.py`
- 测试：`backend/tests/test_prompts.py`、`backend/tests/test_llm.py`

- [ ] **步骤 1：编写失败的测试**

`backend/tests/test_prompts.py`：
```python
from app.llm.prompts import FORBIDDEN_WORDS, build_summary_prompt


def test_prompt_contains_no_evaluation_rule():
    prompt = build_summary_prompt("本周", ["写完周报", "跑步 30 分钟"])
    assert "禁止任何评价" in prompt
    assert "不要评价" in prompt


def test_prompt_contains_forbidden_words():
    prompt = build_summary_prompt("本周", ["写完周报"])
    for word in FORBIDDEN_WORDS:
        assert word in prompt


def test_prompt_includes_entries():
    prompt = build_summary_prompt("本周", ["写完周报", "跑步 30 分钟"])
    assert "写完周报" in prompt
    assert "跑步 30 分钟" in prompt
```

`backend/tests/test_llm.py`：
```python
import httpx

from app.llm.openai_compat import OpenAICompatibleLLM


def test_generate_sends_chat_completion(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "归类后的小结"}}]}

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)
    llm = OpenAICompatibleLLM(api_key="sk-test", base_url="https://api.deepseek.com", model="deepseek-chat")
    result = llm.generate("hello")

    assert result == "归类后的小结"
    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer sk-test"
    assert captured["json"]["model"] == "deepseek-chat"
```

- [ ] **步骤 2：运行测试验证失败**

```bash
cd backend && python -m pytest tests/test_prompts.py tests/test_llm.py -v
```
预期：FAIL，`ModuleNotFoundError`。

- [ ] **步骤 3：编写最少实现代码**

`backend/app/config.py`：
```python
import os

from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")


def llm_configured() -> bool:
    return bool(LLM_API_KEY)
```

`backend/app/llm/__init__.py`：空文件。

`backend/app/llm/base.py`：
```python
from typing import Protocol


class BaseLLM(Protocol):
    def generate(self, prompt: str) -> str: ...
```

`backend/app/llm/prompts.py`：
```python
FORBIDDEN_WORDS = [
    "优秀", "很棒", "进步", "需要改进", "建议你", "继续保持",
    "表现", "厉害", "加油", "再接再厉",
]

NO_EVALUATION_RULE = (
    "你是一名只做事实性汇总的助手。请仅对用户记录的事项进行归类与汇总，"
    "禁止任何评价、评分、评级、鼓励或批评。"
    "禁止使用以下词汇或类似表达：" + "、".join(FORBIDDEN_WORDS) + "。"
)


def build_summary_prompt(period_label: str, entries: list[str]) -> str:
    joined = "\n".join(f"- {e}" for e in entries)
    return (
        f"{NO_EVALUATION_RULE}\n\n"
        f"以下是用户{period_label}完成的事项：\n{joined}\n\n"
        f"请按主题（如工作、生活、学习等）将这些事项归类汇总，输出一段简洁的小结。"
        f"只做归类与罗列，不要评价。"
    )
```

`backend/app/llm/openai_compat.py`：
```python
import httpx


class OpenAICompatibleLLM:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = httpx.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
```

- [ ] **步骤 4：运行测试验证通过**

```bash
cd backend && python -m pytest tests/test_prompts.py tests/test_llm.py -v
```
预期：PASS。

- [ ] **步骤 5：Commit**

```bash
git add backend/app/config.py backend/app/llm backend/tests/test_prompts.py backend/tests/test_llm.py
git commit -m "feat: add LLM abstraction with no-evaluation prompt"
```

---

## 任务 5：小结服务与 summaries 路由（含拼接降级）

**文件：**
- 创建：`backend/app/services/__init__.py`、`backend/app/services/summary_service.py`、`backend/app/routers/summaries.py`
- 修改：`backend/app/main.py`（挂载 summaries 路由）
- 测试：`backend/tests/test_summaries.py`

- [ ] **步骤 1：编写失败的测试**

`backend/tests/test_summaries.py`：
```python
from datetime import datetime

from app.services.summary_service import get_period


def test_get_period_weekly():
    now = datetime(2026, 8, 13, 15, 0, 0)  # 周四
    start, end = get_period("weekly", now)
    assert start == datetime(2026, 8, 10, 0, 0, 0)  # 周一
    assert end == datetime(2026, 8, 17, 0, 0, 0)


def test_get_period_monthly():
    now = datetime(2026, 8, 13, 15, 0, 0)
    start, end = get_period("monthly", now)
    assert start == datetime(2026, 8, 1, 0, 0, 0)
    assert end == datetime(2026, 9, 1, 0, 0, 0)


def test_summary_fallback_concatenation(client, monkeypatch):
    import app.services.summary_service as svc
    monkeypatch.setattr(svc.config, "llm_configured", lambda: False)

    client.post("/entries", json={"content": "写完周报"})
    client.post("/entries", json={"content": "跑步 30 分钟"})
    resp = client.post("/summaries/weekly")
    assert resp.status_code == 200
    content = resp.json()["content"]
    assert "写完周报" in content
    assert "跑步 30 分钟" in content


def test_summary_uses_llm_when_configured(client, monkeypatch):
    import app.services.summary_service as svc

    class FakeLLM:
        def __init__(self, *args, **kwargs):
            pass

        def generate(self, prompt):
            return "AI 归类后的小结"

    monkeypatch.setattr(svc.config, "llm_configured", lambda: True)
    monkeypatch.setattr(svc, "OpenAICompatibleLLM", FakeLLM)

    client.post("/entries", json={"content": "写完周报"})
    resp = client.post("/summaries/weekly")
    assert resp.json()["content"] == "AI 归类后的小结"


def test_summary_list_and_regenerate(client, monkeypatch):
    import app.services.summary_service as svc
    monkeypatch.setattr(svc.config, "llm_configured", lambda: False)

    client.post("/entries", json={"content": "一件事"})
    client.post("/summaries/weekly")
    client.post("/entries", json={"content": "另一件事"})
    client.post("/summaries/weekly")  # 覆盖刷新

    resp = client.get("/summaries")
    assert len(resp.json()) == 1  # 同周期只保留最新一份
    assert "另一件事" in resp.json()[0]["content"]


def test_invalid_period_type_returns_400(client):
    resp = client.post("/summaries/daily")
    assert resp.status_code == 400
```

- [ ] **步骤 2：运行测试验证失败**

```bash
cd backend && python -m pytest tests/test_summaries.py -v
```
预期：FAIL，`ModuleNotFoundError` 或 404（路由未挂载）。

- [ ] **步骤 3：编写最少实现代码**

`backend/app/services/__init__.py`：空文件。

`backend/app/services/summary_service.py`：
```python
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .. import config, models
from ..llm.openai_compat import OpenAICompatibleLLM
from ..llm.prompts import build_summary_prompt

WEEKDAYS = "一二三四五六日"


def get_period(period_type: str, now: datetime) -> tuple[datetime, datetime]:
    if period_type == "weekly":
        monday = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return monday, monday + timedelta(days=7)
    if period_type == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end = start.replace(year=now.year + 1, month=1)
        else:
            end = start.replace(month=now.month + 1)
        return start, end
    raise ValueError(f"unknown period_type: {period_type}")


def concat_summary(period_label: str, entries: list[models.Entry]) -> str:
    lines = [f"## {period_label}小结", ""]
    current_date = None
    for e in entries:
        d = e.created_at.date()
        if d != current_date:
            current_date = d
            weekday = WEEKDAYS[d.weekday()]
            lines.append(f"### {d.month}月{d.day}日（周{weekday}）")
        lines.append(f"- {e.content}")
    if not entries:
        lines.append("（本期暂无记录）")
    return "\n".join(lines)


def generate_summary(db: Session, period_type: str) -> models.Summary:
    start, end = get_period(period_type, datetime.now())
    period_label = "本周" if period_type == "weekly" else "本月"

    entries = (
        db.query(models.Entry)
        .filter(models.Entry.created_at >= start, models.Entry.created_at < end)
        .order_by(models.Entry.created_at)
        .all()
    )

    if config.llm_configured():
        llm = OpenAICompatibleLLM(config.LLM_API_KEY, config.LLM_BASE_URL, config.LLM_MODEL)
        content = llm.generate(build_summary_prompt(period_label, [e.content for e in entries]))
    else:
        content = concat_summary(period_label, entries)

    # 覆盖刷新：同周期只保留最新一份
    db.query(models.Summary).filter(
        models.Summary.period_type == period_type,
        models.Summary.period_start == start,
        models.Summary.period_end == end,
    ).delete()

    summary = models.Summary(
        period_type=period_type, period_start=start, period_end=end, content=content
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary
```

`backend/app/routers/summaries.py`：
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..services.summary_service import generate_summary

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.post("/{period_type}", response_model=schemas.SummaryOut)
def create_summary(period_type: str, db: Session = Depends(get_db)):
    if period_type not in ("weekly", "monthly"):
        raise HTTPException(status_code=400, detail="period_type must be weekly or monthly")
    return generate_summary(db, period_type)


@router.get("", response_model=list[schemas.SummaryOut])
def list_summaries(db: Session = Depends(get_db)):
    return db.query(models.Summary).order_by(models.Summary.created_at.desc()).all()
```

`backend/app/main.py` 改为：
```python
from fastapi import FastAPI

from .db import Base, engine
from .routers import entries, summaries

Base.metadata.create_all(bind=engine)

app = FastAPI(title="精力恢复记事本")
app.include_router(entries.router)
app.include_router(summaries.router)


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **步骤 4：运行测试验证通过**

```bash
cd backend && python -m pytest tests/test_summaries.py -v
```
预期：PASS。

- [ ] **步骤 5：运行全部后端测试**

```bash
cd backend && python -m pytest -v
```
预期：全部 PASS。

- [ ] **步骤 6：Commit**

```bash
git add backend/app/services backend/app/routers/summaries.py backend/app/main.py backend/tests/test_summaries.py
git commit -m "feat: add summary generation with LLM and concatenation fallback"
```

---

## 任务 6：前端脚手架与记录 UI

**文件：**
- 创建：`frontend/`（Vite + Vue 3 项目）
- 创建：`frontend/src/api.js`、`frontend/src/App.vue`、`frontend/src/components/EntryInput.vue`、`frontend/src/components/EntryList.vue`
- 修改：`frontend/vite.config.js`、`frontend/src/main.js`

- [ ] **步骤 1：用 Vite 脚手架创建前端项目**

```bash
npm create vite@latest frontend -- --template vue
cd frontend
npm install
```

- [ ] **步骤 2：配置 dev 代理**

`frontend/vite.config.js`：
```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

- [ ] **步骤 3：编写 API 客户端**

`frontend/src/api.js`：
```js
const BASE = '/api'

async function request(path, options = {}) {
  const resp = await fetch(`${BASE}${path}`, options)
  if (!resp.ok) throw new Error(`请求失败: ${resp.status}`)
  return resp.status === 204 ? null : resp.json()
}

export const listEntries = () => request('/entries')
export const createEntry = (content) =>
  request('/entries', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
export const deleteEntry = (id) => request(`/entries/${id}`, { method: 'DELETE' })
export const listSummaries = () => request('/summaries')
export const generateSummary = (periodType) =>
  request(`/summaries/${periodType}`, { method: 'POST' })
```

- [ ] **步骤 4：编写记录输入与列表组件**

`frontend/src/components/EntryInput.vue`：
```vue
<script setup>
import { ref } from 'vue'

const emit = defineEmits(['created'])
const content = ref('')

async function submit() {
  if (!content.value.trim()) return
  emit('created', content.value.trim())
  content.value = ''
}
</script>

<template>
  <form class="entry-input" @submit.prevent="submit">
    <textarea
      v-model="content"
      placeholder="今天完成了什么？"
      rows="3"
      @keydown.enter.exact.prevent="submit"
    ></textarea>
    <button type="submit" :disabled="!content.trim()">记录</button>
  </form>
</template>
```

`frontend/src/components/EntryList.vue`：
```vue
<script setup>
import { computed } from 'vue'

const props = defineProps({ entries: { type: Array, default: () => [] } })
const emit = defineEmits(['delete'])

const grouped = computed(() => {
  const map = new Map()
  for (const e of props.entries) {
    const d = new Date(e.created_at).toLocaleDateString('zh-CN')
    if (!map.has(d)) map.set(d, [])
    map.get(d).push(e)
  }
  return [...map.entries()]
})
</script>

<template>
  <div v-if="grouped.length === 0" class="empty">还没有记录，写下今天完成的第一件事吧。</div>
  <section v-for="[day, items] in grouped" :key="day" class="day-group">
    <h3>{{ day }}</h3>
    <ul>
      <li v-for="e in items" :key="e.id">
        <span>{{ e.content }}</span>
        <button class="del" @click="emit('delete', e.id)">×</button>
      </li>
    </ul>
  </section>
</template>
```

- [ ] **步骤 5：编写 App 根组件**

`frontend/src/App.vue`：
```vue
<script setup>
import { onMounted, ref } from 'vue'
import { listEntries, createEntry, deleteEntry } from './api'
import EntryInput from './components/EntryInput.vue'
import EntryList from './components/EntryList.vue'

const entries = ref([])
const tab = ref('record')

async function refresh() {
  entries.value = await listEntries()
}

async function onCreate(content) {
  await createEntry(content)
  await refresh()
}

async function onDelete(id) {
  await deleteEntry(id)
  await refresh()
}

onMounted(refresh)
</script>

<template>
  <div class="app">
    <header>
      <h1>精力恢复记事本</h1>
      <nav>
        <button :class="{ active: tab === 'record' }" @click="tab = 'record'">记录</button>
        <button :class="{ active: tab === 'summary' }" @click="tab = 'summary'">小结</button>
      </nav>
    </header>
    <main v-if="tab === 'record'">
      <EntryInput @created="onCreate" />
      <EntryList :entries="entries" @delete="onDelete" />
    </main>
  </div>
</template>
```

- [ ] **步骤 6：手动验证（浏览器）**

```bash
# 终端 1：启动后端
cd backend && source .venv/Scripts/activate && uvicorn app.main:app --reload

# 终端 2：启动前端
cd frontend && npm run dev
```
打开前端 dev 地址，验证：输入一条 → 点"记录" → 列表出现该条；点"×"删除 → 列表移除。

- [ ] **步骤 7：Commit**

```bash
git add frontend
git commit -m "feat: add Vue frontend with entry input and list"
```

---

## 任务 7：前端小结 UI 与联调

**文件：**
- 创建：`frontend/src/components/SummaryView.vue`
- 修改：`frontend/src/App.vue`（引入 SummaryView）

- [ ] **步骤 1：编写小结组件**

`frontend/src/components/SummaryView.vue`：
```vue
<script setup>
import { onMounted, ref } from 'vue'
import { listSummaries, generateSummary } from '../api'

const summaries = ref([])
const error = ref('')

async function refresh() {
  summaries.value = await listSummaries()
}

async function onGenerate(periodType) {
  error.value = ''
  try {
    await generateSummary(periodType)
    await refresh()
  } catch (e) {
    error.value = '小结生成失败，请稍后重试。'
  }
}

onMounted(refresh)
</script>

<template>
  <div class="summary-view">
    <div class="actions">
      <button @click="onGenerate('weekly')">生成本周小结</button>
      <button @click="onGenerate('monthly')">生成本月小结</button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <article v-for="s in summaries" :key="s.id" class="summary-card">
      <h3>
        {{ s.period_type === 'weekly' ? '本周小结' : '本月小结' }}
        <small>{{ new Date(s.period_start).toLocaleDateString('zh-CN') }}</small>
      </h3>
      <pre class="content">{{ s.content }}</pre>
    </article>
  </div>
</template>
```

- [ ] **步骤 2：接入 App 根组件**

`frontend/src/App.vue` 的 `<script setup>` 中，在 `import EntryList ...` 之后追加：
```js
import SummaryView from './components/SummaryView.vue'
```

`<main v-if="tab === 'record'">...</main>` 之后追加：
```html
<main v-else>
  <SummaryView />
</main>
```

- [ ] **步骤 3：手动验证（浏览器）**

后端、前端两个 dev server 保持运行：
1. 切到「小结」页 → 点「生成本周小结」→ 未配置 `.env` 时显示拼接内容（按日期分组罗列）。
2. 在 `backend/.env` 填入真实 `LLM_API_KEY` 后重启后端 → 再次生成 → 显示 AI 归类小结，且无评价性词汇。
3. 新增记录后再次生成同周期小结 → 内容覆盖刷新，`/summaries` 列表仍只有一条该周期记录。

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/components/SummaryView.vue frontend/src/App.vue
git commit -m "feat: add summary view and wire to backend"
```

---

## 任务 8：运行说明与收尾

**文件：**
- 创建：`README.md`

- [ ] **步骤 1：编写运行说明**

`README.md`：
```markdown
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
```

- [ ] **步骤 2：最终验证**

```bash
cd backend && python -m pytest -v
```
预期：全部 PASS。

- [ ] **步骤 3：Commit**

```bash
git add README.md
git commit -m "docs: add run instructions"
```

---

## 自检记录

- **规格覆盖**：记录 CRUD（任务 3）、不评价约束（任务 4）、AI 小结 + 拼接降级（任务 5）、单用户（无用户表）、环境变量配置（任务 4 的 config.py）、手动触发（POST /summaries/{type}）、云部署预留（SQLAlchemy 抽象 + 前后端解耦）。
- **占位符**：无待定/TODO，每个代码步骤均含实际代码。
- **类型一致性**：`EntryOut`/`SummaryOut` 字段与 `schemas.py` 一致；`get_period` 返回 `(start, end)` 元组在 service 与测试中用法一致；`client` fixture 在任务 3 的 conftest 中统一定义，任务 3、5 的测试直接引用。
