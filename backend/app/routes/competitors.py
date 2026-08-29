"""Competitor analysis routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas
from app.services.audit_service import perform_audit
from app.services.serp_service import SERPService

router = APIRouter(prefix="/competitors", tags=["competitors"])


@router.post("/", response_model="schemas.CompetitorOut")
async def add_competitor(
    name: str,
    url: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Add a competitor to track."""
    existing = db.query(models.Competitor).filter(
        models.Competitor.user_id == user.id,
        models.Competitor.url == url,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Competitor with this URL already exists")

    competitor = models.Competitor(user_id=user.id, name=name, url=url)
    db.add(competitor)
    db.commit()
    db.refresh(competitor)
    return competitor


@router.get("/", response_model=List[dict])
def list_competitors(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """List all competitors for the current user."""
    competitors = (
        db.query(models.Competitor)
        .filter(models.Competitor.user_id == user.id)
        .order_by(models.Competitor.created_at.desc())
        .all()
    )
    result = []
    for c in competitors:
        latest_audit = (
            db.query(models.CompetitorAudit)
            .filter(models.CompetitorAudit.competitor_id == c.id)
            .order_by(models.CompetitorAudit.crawled_at.desc())
            .first()
        )
        result.append({
            "id": c.id,
            "name": c.name,
            "url": c.url,
            "created_at": c.created_at,
            "latest_seo_score": latest_audit.seo_score if latest_audit else None,
            "latest_geo_score": latest_audit.geo_score if latest_audit else None,
            "latest_crawled_at": latest_audit.crawled_at if latest_audit else None,
        })
    return result


@router.post("/{competitor_id}/audit")
async def audit_competitor(
    competitor_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Trigger a full audit of a competitor."""
    competitor = (
        db.query(models.Competitor)
        .filter(models.Competitor.id == competitor_id, models.Competitor.user_id == user.id)
        .first()
    )
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    # Run crawl async and store results
    crawl_task = asyncio.create_task(perform_audit(competitor.url, user.id, db))

    try:
        audit = await crawl_task
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Competitor audit failed: {exc}")

    # Store competitor audit record
    competitor_audit = models.CompetitorAudit(
        competitor_id=competitor_id,
        seo_score=audit.seo_score,
        geo_score=audit.geo_score,
        findings_snapshot={
            "total_findings": len(audit.findings),
            "critical": len([f for f in audit.findings if f.severity == "critical"]),
            "high": len([f for f in audit.findings if f.severity == "high"]),
        },
    )
    db.add(competitor_audit)
    db.commit()
    return {
        "competitor_id": competitor_id,
        "audit_id": audit.id,
        "seo_score": audit.seo_score,
        "geo_score": audit.geo_score,
    }


@router.get("/compare")
def compare_competitors(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Compare all competitors with the user's latest audits."""
    competitors = (
        db.query(models.Competitor)
        .filter(models.Competitor.user_id == user.id)
        .all()
    )

    # Get user's own audits for comparison
    user_audits = (
        db.query(models.Audit)
        .filter(models.Audit.user_id == user.id)
        .order_by(models.Audit.created_at.desc())
        .limit(1)
        .all()
    )
    user_seo = user_audits[0].seo_score if user_audits else None
    user_geo = user_audits[0].geo_score if user_audits else None

    comparisons = []
    for c in competitors:
        latest = (
            db.query(models.CompetitorAudit)
            .filter(models.CompetitorAudit.competitor_id == c.id)
            .order_by(models.CompetitorAudit.crawled_at.desc())
            .first()
        )
        if latest:
            comparisons.append({
                "competitor_id": c.id,
                "name": c.name,
                "url": c.url,
                "seo_score": latest.seo_score,
                "geo_score": latest.geo_score,
                "seo_diff": latest.seo_score - (user_seo or 0),
                "geo_diff": (latest.geo_score or 0) - (user_geo or 0),
                "crawled_at": latest.crawled_at,
            })

    return {
        "user_seo_score": user_seo,
        "user_geo_score": user_geo,
        "competitors": comparisons,
    }


@router.delete("/{competitor_id}")
def delete_competitor(
    competitor_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Delete a competitor."""
    competitor = (
        db.query(models.Competitor)
        .filter(models.Competitor.id == competitor_id, models.Competitor.user_id == user.id)
        .first()
    )
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    db.delete(competitor)
    db.commit()
    return {"status": "deleted"}
