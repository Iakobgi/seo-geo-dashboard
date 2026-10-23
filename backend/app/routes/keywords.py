import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas
from app.services.serp_service import SERPService, SERPResult

router = APIRouter(prefix="/keywords", tags=["keywords"])

# Initialize SERP service (falls back to simulated if no provider configured)
_serp_service = SERPService.from_env()


@router.post("/", response_model=schemas.KeywordOut)
async def create_keyword(kw: schemas.KeywordCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    value = kw.keyword.strip()
    if not value:
        raise HTTPException(status_code=400, detail="Enter a keyword to track")
    if kw.audit_id is not None:
        audit = db.query(models.Audit).filter(models.Audit.id == kw.audit_id, models.Audit.user_id == user.id).first()
        if not audit:
            raise HTTPException(status_code=404, detail="Audit not found")
    if db.query(models.Keyword).filter(models.Keyword.user_id == user.id, func.lower(models.Keyword.keyword) == value.lower()).first():
        raise HTTPException(status_code=400, detail="You are already tracking this keyword")
    # Use SERP service for real or simulated ranking data
    result = await _serp_service.search(value)
    keyword = models.Keyword(
        user_id=user.id,
        audit_id=kw.audit_id,
        keyword=value,
        position=result.position,
        previous_position=None,
        volume=result.search_volume,
    )
    db.add(keyword)
    db.commit()
    db.refresh(keyword)
    return keyword


@router.get("/", response_model=List[schemas.KeywordOut])
def list_keywords(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Keyword).filter(models.Keyword.user_id == user.id).order_by(models.Keyword.created_at.desc()).all()


@router.get("/provider")
def keyword_provider(user: models.User = Depends(get_current_user)):
    return {"provider": _serp_service.provider_name, "simulated": _serp_service.provider_name not in ("serpapi", "dataforseo")}


@router.post("/{keyword_id}/refresh", response_model=schemas.KeywordOut)
async def refresh_keyword(keyword_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    keyword = db.query(models.Keyword).filter(models.Keyword.id == keyword_id, models.Keyword.user_id == user.id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    keyword.previous_position = keyword.position
    result = await _serp_service.search(keyword.keyword)
    keyword.position = result.position
    if result.search_volume:
        keyword.volume = result.search_volume
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
