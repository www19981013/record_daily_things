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


def test_summary_llm_failure_returns_502(client, monkeypatch):
    import app.services.summary_service as svc

    class FailingLLM:
        def __init__(self, *args, **kwargs):
            pass

        def generate(self, prompt):
            raise RuntimeError("boom")

    monkeypatch.setattr(svc.config, "llm_configured", lambda: True)
    monkeypatch.setattr(svc, "OpenAICompatibleLLM", FailingLLM)

    client.post("/entries", json={"content": "一件事"})
    resp = client.post("/summaries/weekly")
    assert resp.status_code == 502
    assert "小结生成失败" in resp.json()["detail"]
