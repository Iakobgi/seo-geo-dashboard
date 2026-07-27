import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.post("/", response_model=schemas.KeywordOut)
def create_keyword(kw: schemas.KeywordCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # NOTE: real rank tracking requires a SERP API (e.g. SerpApi, DataForSEO).
    # Here we simulate an initial position so the tracker is usable out of the box;
    # swap `simulate_position()` for a real SERP API call when you have a key.
    keyword = models.Keyword(
        user_id=user.id,
        audit_id=kw.audit_id,
        keyword=kw.keyword,
        position=simulate_position(),
        previous_position=None,
        volume=random.randint(50, 5000),
    )
    db.add(keyword)
    db.commit()
    db.refresh(keyword)
    return keyword


@router.get("/", response_model=List[schemas.KeywordOut])
def list_keywords(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Keyword).filter(models.Keyword.user_id == user.id).order_by(models.Keyword.created_at.desc()).all()


@router.post("/{keyword_id}/refresh", response_model=schemas.KeywordOut)
def refresh_keyword(keyword_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    keyword = db.query(models.Keyword).filter(models.Keyword.id == keyword_id, models.Keyword.user_id == user.id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    keyword.previous_position = keyword.position
    keyword.position = simulate_position(keyword.position)
    db.commit()
    db.refresh(keyword)
    return keyword


@router.delete("/{keyword_id}")
def delete_keyword(keyword_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    keyword = db.query(models.Keyword).filter(models.Keyword.id == keyword_id, models.Keyword.user_id == user.id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(keyword)
    db.commit()
    return {"status": "deleted"}


def simulate_position(previous: int = None) -> int:
    """Placeholder ranking simulator. Replace with a real SERP API integration."""
    if previous is None:
        return random.randint(1, 100)
    drift = random.randint(-5, 5)
    return max(1, min(100, previous + drift))
