"""Knowledge base routes for RAG-powered SEO/GEO insights."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app import models
from app.services.rag_service import RAGService, KnowledgeResult

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/search")
def search_knowledge(
    q: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Search the SEO/GEO knowledge base."""
    service = RAGService(db)
    results = service.search(q, limit)
    return {
        "query": q,
        "results": [
            {
                "title": r.title,
                "content": r.content,
                "category": r.category,
                "source": r.source,
                "relevance_score": r.relevance_score,
            }
            for r in results
        ],
        "count": len(results),
    }


@router.get("/articles")
def list_articles(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """List all knowledge articles, optionally filtered by category."""
    service = RAGService(db)
    articles = service._seed_articles

    if category:
        articles = [a for a in articles if a.get("category") == category]

    return {
        "articles": [
            {
                "title": a["title"],
                "content": a["content"],
                "category": a["category"],
                "source": a["source"],
            }
            for a in articles
        ],
        "count": len(articles),
    }


@router.post("/articles")
def create_article(
    title: str,
    content: str,
    category: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Add a custom knowledge article (admin feature)."""
    article = models.KnowledgeArticle(
        title=title,
        content=content,
        category=category,
        source=source or "user-contributed",
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return {
        "id": article.id,
        "title": article.title,
        "category": article.category,
        "source": article.source,
        "created_at": article.created_at,
    }


@router.delete("/articles/{article_id}")
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Delete a user-contributed knowledge article."""
    article = db.query(models.KnowledgeArticle).filter(models.KnowledgeArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(article)
    db.commit()
    return {"status": "deleted"}


@router.get("/context")
def get_context(
    q: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get formatted RAG context for use in AI prompts."""
    service = RAGService(db)
    context = service.get_rag_context(q, limit)
    return {
        "query": q,
        "context": service.format_context_for_prompt(context),
        "article_count": len(context.relevant_articles),
        "articles": [
            {
                "title": r.title,
                "category": r.category,
                "relevance_score": r.relevance_score,
            }
            for r in context.relevant_articles
        ],
    }
