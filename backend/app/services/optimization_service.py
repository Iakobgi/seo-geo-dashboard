"""Optimization cycle service for tracking SEO improvements over time."""

from sqlalchemy.orm import Session
from typing import List, Optional

from app import models


class OptimizationService:
    """Service for managing optimization cycles and re-audits."""

    def __init__(self, db: Session):
        self._db = db

    def create_cycle(
        self,
        user_id: int,
        url: str,
        target_score: int,
        baseline_seo_score: float = None,
        baseline_geo_score: float = None,
    ) -> models.OptimizationCycle:
        """Create a new optimization cycle."""
        cycle = models.OptimizationCycle(
            user_id=user_id,
            url=url,
            target_score=target_score,
            baseline_seo_score=baseline_seo_score,
            baseline_geo_score=baseline_geo_score,
        )
        self._db.add(cycle)
        self._db.commit()
        self._db.refresh(cycle)
        return cycle

    def add_step(
        self,
        cycle_id: int,
        action: str,
        status: str = "pending",
    ) -> models.OptimizationStep:
        """Add an optimization step to a cycle."""
        step = models.OptimizationStep(
            cycle_id=cycle_id,
            action=action,
            status=status,
        )
        self._db.add(step)
        self._db.commit()
        self._db.refresh(step)
        return step

    def update_step_status(
        self,
        step_id: int,
        status: str,
        audit_snapshot_id: int = None,
    ) -> Optional[models.OptimizationStep]:
        """Update an optimization step's status."""
        step = self._db.query(models.OptimizationStep).filter(
            models.OptimizationStep.id == step_id
        ).first()
        if not step:
            return None
        step.status = status
        if audit_snapshot_id:
            step.audit_snapshot_id = audit_snapshot_id
        self._db.commit()
        self._db.refresh(step)
        return step

    def get_cycle(self, cycle_id: int, user_id: int) -> Optional[models.OptimizationCycle]:
        """Get an optimization cycle with its steps."""
        cycle = self._db.query(models.OptimizationCycle).filter(
            models.OptimizationCycle.id == cycle_id,
            models.OptimizationCycle.user_id == user_id,
        ).first()
        if cycle:
            self._db.refresh(cycle)
        return cycle

    def list_cycles(self, user_id: int, status: Optional[str] = None) -> List[models.OptimizationCycle]:
        """List optimization cycles for a user."""
        query = self._db.query(models.OptimizationCycle).filter(
            models.OptimizationCycle.user_id == user_id
        )
        if status:
            query = query.filter(models.OptimizationCycle.status == status)
        return query.order_by(models.OptimizationCycle.created_at.desc()).all()

    def mark_cycle_completed(
        self,
        cycle_id: int,
        user_id: int,
        current_seo_score: float,
        current_geo_score: float,
    ) -> Optional[models.OptimizationCycle]:
        """Mark a cycle as completed with final scores."""
        cycle = self.get_cycle(cycle_id, user_id)
        if not cycle:
            return None
        cycle.current_seo_score = current_seo_score
        cycle.current_geo_score = current_geo_score
        cycle.status = "completed"
        self._db.commit()
        self._db.refresh(cycle)
        return cycle

    def get_pending_steps(self, cycle_id: int) -> List[models.OptimizationStep]:
        """Get all pending steps for a cycle."""
        return self._db.query(models.OptimizationStep).filter(
            models.OptimizationStep.cycle_id == cycle_id,
            models.OptimizationStep.status == "pending",
        ).order_by(models.OptimizationStep.created_at.asc()).all()
