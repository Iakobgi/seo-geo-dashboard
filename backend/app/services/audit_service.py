"""Audit service orchestrating crawler, analysis, and scoring pipeline."""

from sqlalchemy.orm import Session
from datetime import datetime

from app import models
from app.services.crawler_service import CrawlerConfig, CrawlerService
from app.services.seo_analysis_service import SEOAnalysisService
from app.services.scoring_service import ScoringService
from app.services.geo_analysis_service import GEOAnalysisService
from app.services.schema_analysis_service import SchemaAnalysisService
from app.services.eeat_analysis_service import EEAATAnalysisService
from app.services.ai_service import call_openrouter
from app.services.rag_service import create_rag_service


async def perform_audit(url: str, user_id: int, db: Session, model: str = None) -> models.Audit:
    """Perform a full SEO audit using the new pipeline."""
    # Configure crawler
    config = CrawlerConfig(
        max_pages=10,
        max_depth=2,
        respect_robots=True
    )
    crawler = CrawlerService(config)

    # Crawl the site
    crawl_result = await crawler.crawl(url)

    # Analyze with SEO analysis service
    analysis_service = SEOAnalysisService()
    category_analyses = analysis_service.analyze_by_category(crawl_result)

    # Calculate scores
    scoring_service = ScoringService()
    score_breakdown = scoring_service.score_from_crawl(crawl_result)

    # Run GEO analysis
    geo_service = GEOAnalysisService()
    geo_analysis = geo_service.analyze(crawl_result.pages[0].html or "")
    geo_score = geo_analysis.overall_score

    # Run Schema analysis
    schema_service = SchemaAnalysisService()
    schema_analysis = schema_service.analyze(crawl_result.pages[0].html or "")

    # Run E-E-A-T analysis
    eeat_service = EEAATAnalysisService()
    eeat_analysis = eeat_service.analyze(crawl_result.pages[0].html or "", crawl_result.pages[0].html or "")

    # Use first page as primary audit data
    primary_page = crawl_result.pages[0] if crawl_result.pages else None

    # Extract data for audit
    title = primary_page.title if primary_page else None
    meta_description = primary_page.meta_description if primary_page else None
    h1 = primary_page.h1 if primary_page else None
    h2 = primary_page.h2 if primary_page else []
    word_count = primary_page.word_count if primary_page else 0
    images_count = primary_page.images_count if primary_page else 0
    links_count = primary_page.links_count if primary_page else 0
    load_time = primary_page.load_time if primary_page else None

    audit = models.Audit(
        user_id=user_id,
        url=url,
        title=title,
        meta_description=meta_description,
        h1=h1,
        h2=h2,
        word_count=word_count,
        images_count=images_count,
        links_count=links_count,
        load_time=load_time,
        seo_score=score_breakdown.overall_score,
        geo_score=geo_score,
        raw_html=(primary_page.html or "")[:10000] if primary_page else None,
    )
    db.add(audit)
    db.flush()  # Get audit.id without committing

    # Save findings
    all_findings = []
    for category, analysis in category_analyses.items():
        for finding in analysis.findings:
            finding_model = models.Finding(
                audit_id=audit.id,
                category=finding.category.value,
                severity=finding.severity.value,
                url=finding.url,
                title=finding.title,
                description=finding.description,
                evidence=finding.evidence,
                recommendation=finding.recommendation,
                impact_score=finding.impact_score,
            )
            db.add(finding_model)
            all_findings.append(finding)

    # Create audit snapshot
    snapshot_data = {
        "crawl_result": {
            "pages_crawled": crawl_result.pages_crawled,
            "pages": [p.url for p in crawl_result.pages],
            "duplicate_titles": crawl_result.duplicate_titles,
            "duplicate_meta_descriptions": crawl_result.duplicate_meta_descriptions,
            "broken_internal_links": crawl_result.broken_internal_links,
            "robots_txt_found": crawl_result.robots_txt_found,
            "sitemap_urls": crawl_result.sitemap_urls,
            "crawl_duration": crawl_result.crawl_duration,
        },
        "category_analyses": {
            cat.value: {
                "score": analysis.score,
                "weight": analysis.weight,
                "checks_count": analysis.checks_count,
                "passed_checks": analysis.passed_checks,
                "failed_checks": analysis.failed_checks,
                "findings_count": len(analysis.findings),
            }
            for cat, analysis in category_analyses.items()
        },
        "findings": [f.to_dict() for f in all_findings],
        "geo_analysis": {
            "overall_score": geo_analysis.overall_score,
            "metrics": {k.value: v for k, v in geo_analysis.metrics.items()},
        },
        "schema_analysis": {
            "overall_score": schema_analysis.score,
            "types_found": schema_analysis.types_found,
            "has_errors": schema_analysis.has_errors,
        },
        "eeat_analysis": {
            "overall_score": eeat_analysis.overall_score,
            "dimensions": {k.value: v for k, v in eeat_analysis.dimensions.items()},
        },
    }

    snapshot = models.AuditSnapshot(
        audit_id=audit.id,
        snapshot_data=snapshot_data,
        seo_score=score_breakdown.overall_score,
        geo_score=geo_score,
        category_scores={cat.value: analysis.score for cat, analysis in category_analyses.items()},
        finding_counts=score_breakdown.finding_counts,
    )
    db.add(snapshot)

    # Generate AI recommendations with RAG context (optional)
    if model:
        try:
            # Build RAG context from findings
            rag_service = create_rag_service(db)
            query = f"SEO and GEO improvements for {url}. Findings: {[f.title for f in all_findings[:5]]}"
            rag_context = rag_service.format_context_for_prompt(rag_service.get_rag_context(query, limit=3))

            ai_result = await call_openrouter({
                "url": url,
                "title": title,
                "meta_description": meta_description,
                "findings": [f.to_dict() for f in all_findings[:20]],  # Limit findings
            }, model, rag_context=rag_context)

            for suggestion in ai_result.get("suggestions", []):
                db.add(models.Recommendation(audit_id=audit.id, type="suggestion", suggestion=suggestion))

            if ai_result.get("generated_content"):
                db.add(models.Recommendation(
                    audit_id=audit.id,
                    type="generated_content",
                    suggestion=str(ai_result["generated_content"]),
                ))
        except Exception:
            pass  # Continue even if AI fails

    db.commit()
    db.refresh(audit)
    return audit


async def create_crawl(
    url: str,
    max_pages: int = 10,
    max_depth: int = 2,
    respect_robots: bool = True,
) -> dict:
    """Perform a crawl without creating a full audit record."""
    config = CrawlerConfig(
        max_pages=max_pages,
        max_depth=max_depth,
        respect_robots=respect_robots
    )
    crawler = CrawlerService(config)
    crawl_result = await crawler.crawl(url)

    return {
        "start_url": crawl_result.start_url,
        "pages_crawled": crawl_result.pages_crawled,
        "pages": [
            {
                "url": p.url,
                "status_code": p.status_code,
                "title": p.title,
                "meta_description": p.meta_description,
                "h1": p.h1,
                "h2": p.h2,
                "word_count": p.word_count,
                "images_count": p.images_count,
                "links_count": p.links_count,
                "internal_links_count": p.internal_links_count,
                "external_links_count": p.external_links_count,
                "load_time": p.load_time,
                "canonical_url": p.canonical_url,
                "noindex": p.noindex,
            }
            for p in crawl_result.pages
        ],
        "broken_internal_links": crawl_result.broken_internal_links,
        "duplicate_titles": crawl_result.duplicate_titles,
        "duplicate_meta_descriptions": crawl_result.duplicate_meta_descriptions,
        "robots_txt_found": crawl_result.robots_txt_found,
        "sitemap_urls": crawl_result.sitemap_urls,
        "crawl_duration": crawl_result.crawl_duration,
    }
