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
