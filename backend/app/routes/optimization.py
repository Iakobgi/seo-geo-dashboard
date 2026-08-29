"""Optimization cycle routes for tracking SEO improvements."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app import models
from app.services.optimization_service import OptimizationService
from app.services.audit_service import perform_audit

router = APIRouter(prefix="/optimization", tags=["optimization"])


@router.post("/cycle")
async def create_optimization_cycle(
    url: str,
    target_score: int = 90,
    baseline_seo_score: Optional[float] = None,
    baseline_geo_score: Optional[float] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Start a new optimization cycle."""
    service = OptimizationService(db)
    cycle = service.create_cycle(
        user_id=user.id,
        url=url,
        target_score=target_score,
        baseline_seo_score=baseline_seo_score,
        baseline_geo_score=baseline_geo_score,
    )

    # Run initial audit to get baseline scores
    if baseline_seo_score is None or baseline_geo_score is None:
        try:
            audit = await perform_audit(url, user.id, db)
            if baseline_seo_score is None:
                baseline_seo_score = audit.seo_score
            if baseline_geo_score is None:
                baseline_geo_score = audit.geo_score or 50.0
        except Exception:
            pass

    # Update with actual baseline scores
    cycle.baseline_seo_score = baseline_seo_score
    cycle.baseline_geo_score = baseline_geo_score
    db.commit()
    db.refresh(cycle)

    return {
        "id": cycle.id,
        "url": cycle.url,
        "target_score": cycle.target_score,
        "baseline_seo_score": cycle.baseline_seo_score,
        "baseline_geo_score": cycle.baseline_geo_score,
        "current_seo_score": cycle.current_seo_score,
        "current_geo_score": cycle.current_geo_score,
        "status": cycle.status,
        "created_at": cycle.created_at,
    }


@router.get("/cycle/{cycle_id}")
def get_optimization_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get optimization cycle details with steps."""
    service = OptimizationService(db)
    cycle = service.get_cycle(cycle_id, user.id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Optimization cycle not found")

    steps = (
        db.query(models.OptimizationStep)
        .filter(models.OptimizationStep.cycle_id == cycle_id)
        .order_by(models.OptimizationStep.created_at.asc())
        .all()
    )

    return {
        "id": cycle.id,
        "url": cycle.url,
        "target_score": cycle.target_score,
        "baseline_seo_score": cycle.baseline_seo_score,
        "baseline_geo_score": cycle.baseline_geo_score,
        "current_seo_score": cycle.current_seo_score,
        "current_geo_score": cycle.current_geo_score,
        "status": cycle.status,
        "created_at": cycle.created_at,
        "updated_at": cycle.updated_at,
        "steps": [
            {
                "id": s.id,
                "action": s.action,
                "status": s.status,
                "created_at": s.created_at,
            }
            for s in steps
        ],
    }


@router.get("/cycle/{cycle_id}/steps/pending")
def get_pending_steps(
    cycle_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get pending optimization steps."""
    service = OptimizationService(db)
    cycle = service.get_cycle(cycle_id, user.id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Optimization cycle not found")

    steps = service.get_pending_steps(cycle_id)
    return {
        "cycle_id": cycle_id,
        "steps": [
            {
                "id": s.id,
                "action": s.action,
                "status": s.status,
                "created_at": s.created_at,
            }
            for s in steps
        ],
    }


@router.post("/cycle/{cycle_id}/step/{step_id}/apply")
def apply_optimization_step(
    cycle_id: int,
    step_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Mark an optimization step as applied."""
    service = OptimizationService(db)
    cycle = service.get_cycle(cycle_id, user.id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Optimization cycle not found")

    step = service.update_step_status(step_id, "applied")
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    return {
        "id": step.id,
        "action": step.action,
        "status": step.status,
    }


@router.post("/cycle/{cycle_id}/reaudit")
async def reaudit_optimization_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Re-audit the URL to check progress toward target score."""
    service = OptimizationService(db)
    cycle = service.get_cycle(cycle_id, user.id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Optimization cycle not found")

    try:
        audit = await perform_audit(cycle.url, user.id, db)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Re-audit failed: {exc}")

    # Update cycle with new scores
    cycle.current_seo_score = audit.seo_score
    cycle.current_geo_score = audit.geo_score or 50.0

    # Check if target reached
    if audit.seo_score >= cycle.target_score:
        cycle.status = "completed"
    else:
        cycle.status = "in_progress"

    db.commit()
    db.refresh(cycle)

    return {
        "cycle_id": cycle_id,
        "current_seo_score": cycle.current_seo_score,
        "current_geo_score": cycle.current_geo_score,
        "target_score": cycle.target_score,
        "status": cycle.status,
        "progress": {
            "baseline_seo": cycle.baseline_seo_score,
            "current_seo": cycle.current_seo_score,
            "target_seo": cycle.target_score,
            "improvement": cycle.current_seo_score - (cycle.baseline_seo_score or 0),
        },
    }


@router.get("/cycles")
def list_optimization_cycles(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """List all optimization cycles for the user."""
    service = OptimizationService(db)
    cycles = service.list_cycles(user.id, status)
    return [
        {
            "id": c.id,
            "url": c.url,
            "target_score": c.target_score,
            "baseline_seo_score": c.baseline_seo_score,
            "current_seo_score": c.current_seo_score,
            "status": c.status,
            "created_at": c.created_at,
        }
        for c in cycles
    ]


@router.delete("/cycle/{cycle_id}")
def delete_optimization_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Delete an optimization cycle."""
    service = OptimizationService(db)
    cycle = service.get_cycle(cycle_id, user.id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Optimization cycle not found")
    db.delete(cycle)
    db.commit()
    return {"status": "deleted"}
