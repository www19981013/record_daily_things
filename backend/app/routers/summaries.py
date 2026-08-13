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
