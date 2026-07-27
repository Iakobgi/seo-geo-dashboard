from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas
from app.services.audit_service import perform_audit
from app.services.ai_service import call_openrouter

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/optimize", response_model=schemas.AgentResult)
async def run_agent(
    request: schemas.AgentRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # 1. Run a full audit (scrape + AI analysis), same as a normal audit.
    audit = await perform_audit(request.url, user.id, db, request.model)

    if audit.seo_score >= request.target_score:
        return schemas.AgentResult(
            status="already_at_target",
            audit_id=audit.id,
            current_seo_score=audit.seo_score,
            current_geo_score=audit.geo_score,
            actions=["Current SEO score already meets or exceeds the target."],
        )

    # 2. Ask the AI for a prioritized action plan + rewritten on-page content.
    scrape_like_payload = {
        "title": audit.title,
        "meta_description": audit.meta_description,
        "h1": audit.h1,
        "h2": audit.h2,
        "word_count": audit.word_count,
        "images_count": audit.images_count,
        "links_count": audit.links_count,
        "load_time": audit.load_time,
        "current_seo_score": audit.seo_score,
        "target_seo_score": request.target_score,
    }
    ai_result = await call_openrouter(scrape_like_payload, request.model)

    return schemas.AgentResult(
        status="plan_generated",
        audit_id=audit.id,
        current_seo_score=audit.seo_score,
        current_geo_score=audit.geo_score,
        actions=ai_result.get("suggestions", []),
        generated_content=ai_result.get("generated_content"),
    )
