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
