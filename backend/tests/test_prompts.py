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
