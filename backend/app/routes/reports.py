from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app import models
from app.services.email_service import send_report_email

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/audit/{audit_id}/email")
def email_audit_report(audit_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    lines = [
        f"SEO/GEO Audit Report for {audit.url}",
        f"Date: {audit.created_at}",
        f"SEO Score: {audit.seo_score}/100",
        f"GEO Score: {audit.geo_score}/100",
        "",
        "Recommendations:",
    ]
    for rec in audit.recommendations:
        if rec.type == "suggestion":
            lines.append(f"- {rec.suggestion}")

    sent = send_report_email(user.email, "\n".join(lines), subject=f"SEO Report — {audit.url}")
    return {"emailed": sent}
