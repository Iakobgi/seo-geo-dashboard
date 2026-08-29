from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas
from app.services.audit_service import perform_audit, create_crawl
from app.services.scoring_service import ScoringService
from app.services.seo_analysis_service import SEOAnalysisService

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


@router.post("/crawl", response_model=schemas.CrawlResultOut)
async def crawl(
    crawl_request: schemas.CrawlRequest,
    user: models.User = Depends(get_current_user),
):
    """Crawl a URL and return page data without creating an audit record."""
    try:
        crawl_data = await create_crawl(
            url=crawl_request.url,
            max_pages=crawl_request.max_pages,
            max_depth=crawl_request.max_depth,
            respect_robots=crawl_request.respect_robots,
        )
        return crawl_data
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not crawl URL: {exc}")


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


@router.get("/{audit_id}/findings", response_model=List[schemas.FindingOut])
def get_audit_findings(
    audit_id: int,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get structured SEO findings for an audit, with optional filters."""
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    findings = db.query(models.Finding).filter(models.Finding.audit_id == audit_id).all()

    # Apply filters
    if category:
        findings = [f for f in findings if f.category == category]
    if severity:
        findings = [f for f in findings if f.severity == severity]

    return findings


@router.get("/{audit_id}/scores", response_model=schemas.ScoreBreakdownOut)
def get_audit_scores(
    audit_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get detailed score breakdown for an audit."""
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    # Get findings
    findings = db.query(models.Finding).filter(models.Finding.audit_id == audit_id).all()

    # Get category analyses from snapshot if available
    snapshot = db.query(models.AuditSnapshot).filter(models.AuditSnapshot.audit_id == audit_id).first()

    if snapshot and snapshot.category_scores:
        # Reconstruct category analyses from saved snapshot
        category_data = snapshot.category_scores
        categories = []
        for cat, score in category_data.items():
            categories.append({
                "category": cat,
                "score": score,
                "weight": 0.15,  # Placeholder - full data in snapshot
                "checks_count": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "important_findings": [],
            })
    else:
        # Calculate on-the-fly from findings
        # This is a simplified version - full analysis would require re-crawling
        scoring_service = ScoringService()
        # Get finding counts for breakdown
        finding_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "pass": 0}
        for finding in findings:
            finding_counts[finding.severity] = finding_counts.get(finding.severity, 0) + 1

        categories = [
            {
                "category": "title_meta",
                "score": audit.seo_score,
                "weight": 0.20,
                "checks_count": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "important_findings": [],
            },
            {
                "category": "content",
                "score": audit.seo_score,
                "weight": 0.25,
                "checks_count": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "important_findings": [],
            },
        ]

    # Find critical findings
    critical_findings = [f for f in findings if f.severity == "critical"]
    important = [f.title for f in critical_findings[:5]]

    return schemas.ScoreBreakdownOut(
        overall_score=audit.seo_score,
        geo_score=audit.geo_score or 50.0,
        categories=categories,
        formula=f"Overall SEO Score: {audit.seo_score}",
        finding_counts=finding_counts,
    )


@router.get("/{audit_id}/findings/{finding_id}", response_model=schemas.FindingOut)
def get_audit_finding(
    audit_id: int,
    finding_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get a specific finding for an audit."""
    finding = (
        db.query(models.Finding)
        .filter(
            models.Finding.id == finding_id,
            models.Finding.audit_id == audit_id
        )
        .first()
    )
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.get("/{audit_id}/history")
def get_audit_history(
    audit_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get audit history (snapshots) for trend analysis."""
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    snapshots = (
        db.query(models.AuditSnapshot)
        .filter(models.AuditSnapshot.audit_id == audit_id)
        .order_by(models.AuditSnapshot.created_at.asc())
        .all()
    )

    return {
        "audit_id": audit_id,
        "url": audit.url,
        "snapshots": [
            {
                "id": s.id,
                "created_at": s.created_at,
                "seo_score": s.seo_score,
                "geo_score": s.geo_score,
                "category_scores": s.category_scores,
                "finding_counts": s.finding_counts,
            }
            for s in snapshots
        ],
        "total_snapshots": len(snapshots),
    }


@router.get("/compare")
def compare_audits(
    audit_id_1: int,
    audit_id_2: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Compare two audits and return differences."""
    audit1 = db.query(models.Audit).filter(models.Audit.id == audit_id_1, models.Audit.user_id == user.id).first()
    audit2 = db.query(models.Audit).filter(models.Audit.id == audit_id_2, models.Audit.user_id == user.id).first()

    if not audit1 or not audit2:
        raise HTTPException(status_code=404, detail="One or both audits not found")

    return {
        "audit_1": {
            "id": audit1.id,
            "url": audit1.url,
            "seo_score": audit1.seo_score,
            "geo_score": audit1.geo_score,
            "created_at": audit1.created_at,
        },
        "audit_2": {
            "id": audit2.id,
            "url": audit2.url,
            "seo_score": audit2.seo_score,
            "geo_score": audit2.geo_score,
            "created_at": audit2.created_at,
        },
        "seo_score_change": audit2.seo_score - audit1.seo_score,
        "geo_score_change": (audit2.geo_score or 50) - (audit1.geo_score or 50),
    }


@router.delete("/{audit_id}")
def delete_audit(audit_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    db.delete(audit)
    db.commit()
    return {"status": "deleted"}
