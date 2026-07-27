from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas
from app.services.audit_service import perform_audit

router = APIRouter(prefix="/audits", tags=["audits"])


@router.post("/", response_model=schemas.AuditOut)
async def create_audit(
    audit_in: schemas.AuditCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    try:
        audit = await perform_audit(audit_in.url, user.id, db, audit_in.model)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not audit URL: {exc}")
    return audit


@router.get("/", response_model=List[schemas.AuditOut])
def list_audits(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return (
        db.query(models.Audit)
        .filter(models.Audit.user_id == user.id)
        .order_by(models.Audit.created_at.desc())
        .all()
    )


@router.get("/{audit_id}", response_model=schemas.AuditDetail)
def get_audit(audit_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit


@router.get("/{audit_id}/recommendations", response_model=List[schemas.RecommendationOut])
def get_audit_recommendations(audit_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit.recommendations


@router.delete("/{audit_id}")
def delete_audit(audit_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    db.delete(audit)
    db.commit()
    return {"status": "deleted"}
