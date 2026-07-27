from sqlalchemy.orm import Session

from app import models
from app.services.seo_scraper import fetch_and_parse
from app.services.ai_service import call_openrouter


async def perform_audit(url: str, user_id: int, db: Session, model: str = None) -> models.Audit:
    data = await fetch_and_parse(url)
    ai_result = await call_openrouter(data, model)

    audit = models.Audit(
        user_id=user_id,
        url=url,
        title=data.get("title"),
        meta_description=data.get("meta_description"),
        h1=data.get("h1"),
        h2=data.get("h2"),
        word_count=data.get("word_count", 0),
        images_count=data.get("images_count", 0),
        links_count=data.get("links_count", 0),
        load_time=data.get("load_time"),
        seo_score=ai_result.get("seo_score", 50),
        geo_score=ai_result.get("geo_score", 50),
        raw_html=(data.get("html") or "")[:10000],
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    for suggestion in ai_result.get("suggestions", []):
        db.add(models.Recommendation(audit_id=audit.id, type="suggestion", suggestion=suggestion))

    if ai_result.get("generated_content"):
        db.add(models.Recommendation(
            audit_id=audit.id,
            type="generated_content",
            suggestion=str(ai_result["generated_content"]),
        ))

    db.commit()
    db.refresh(audit)
    return audit
