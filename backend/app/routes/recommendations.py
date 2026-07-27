from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app import models

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.patch("/{rec_id}/apply")
def apply_recommendation(rec_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rec = db.query(models.Recommendation).filter(models.Recommendation.id == rec_id).first()
    if not rec or rec.audit.user_id != user.id:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.status = "applied"
    db.commit()
    return {"status": "applied"}


@router.patch("/{rec_id}/dismiss")
def dismiss_recommendation(rec_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rec = db.query(models.Recommendation).filter(models.Recommendation.id == rec_id).first()
    if not rec or rec.audit.user_id != user.id:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.status = "dismissed"
    db.commit()
    return {"status": "dismissed"}
