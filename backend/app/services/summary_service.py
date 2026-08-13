from datetime import datetime, timedelta

from fastapi import HTTPException
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
        try:
            content = llm.generate(build_summary_prompt(period_label, [e.content for e in entries]))
        except Exception:
            raise HTTPException(status_code=502, detail="小结生成失败，请稍后重试")
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
