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
