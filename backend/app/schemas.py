from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EntryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


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
