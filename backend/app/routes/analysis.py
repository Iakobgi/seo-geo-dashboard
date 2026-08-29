"""Analysis routes for SEO, GEO, Schema.org, and E-E-A-T analysis."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas
from app.services.geo_analysis_service import GEOAnalysisService, GEOAnalysis
from app.services.schema_analysis_service import SchemaAnalysisService, SchemaAnalysis
from app.services.eeat_analysis_service import EEAATAnalysisService, EEAATAnalysis

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/{audit_id}/seo")
def get_seo_analysis(
    audit_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get full SEO analysis for an audit."""
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    # Get findings from database
    findings = db.query(models.Finding).filter(models.Finding.audit_id == audit_id).all()

    return {
        "audit_id": audit_id,
        "seo_score": audit.seo_score,
        "findings_count": len(findings),
        "critical_findings": len([f for f in findings if f.severity == "critical"]),
        "high_findings": len([f for f in findings if f.severity == "high"]),
        "medium_findings": len([f for f in findings if f.severity == "medium"]),
        "low_findings": len([f for f in findings if f.severity == "low"]),
        "pass_findings": len([f for f in findings if f.severity == "pass"]),
    }


@router.get("/{audit_id}/geo")
def get_geo_analysis(
    audit_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get GEO analysis for an audit."""
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    # Get GEO score from audit
    geo_score = audit.geo_score or 50.0

    return {
        "audit_id": audit_id,
        "geo_score": geo_score,
        "answerability": round(geo_score * 0.9, 1),  # Placeholder - should come from analysis
        "passage_citability": round(geo_score * 0.85, 1),
        "question_structure": round(geo_score * 0.8, 1),
        "entity_clarity": round(geo_score * 0.75, 1),
        "attribution": round(geo_score * 0.7, 1),
        "structured_content": round(geo_score * 0.8, 1),
    }


@router.get("/{audit_id}/schema")
def get_schema_analysis(
    audit_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get Schema.org analysis for an audit."""
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    # Get schema-related findings
    schema_findings = [
        f for f in db.query(models.Finding)
        .filter(models.Finding.audit_id == audit_id, models.Finding.category == "structured_data")
        .all()
    ]

    return {
        "audit_id": audit_id,
        "schema_score": 75.0,  # Placeholder - should come from analysis
        "findings": [
            {
                "severity": f.severity,
                "title": f.title,
                "description": f.description,
                "recommendation": f.recommendation,
            }
            for f in schema_findings
        ],
        "block_count": len(schema_findings),
    }


@router.get("/{audit_id}/eeat")
def get_eeat_analysis(
    audit_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get E-E-A-T analysis for an audit."""
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id, models.Audit.user_id == user.id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    # Calculate from SEO score as placeholder
    base_score = audit.seo_score or 50.0

    return {
        "audit_id": audit_id,
        "overall_eeat_score": round(base_score * 0.9, 1),
        "experience": round(base_score * 0.85, 1),
        "expertise": round(base_score * 0.9, 1),
        "authoritativeness": round(base_score * 0.88, 1),
        "trustworthiness": round(base_score * 0.92, 1),
        "topical_depth": round(base_score * 0.87, 1),
    }


@router.post("/crawl/geo")
async def analyze_crawl_geo(
    crawl_data: dict,
    user: models.User = Depends(get_current_user),
):
    """Analyze crawl data for GEO metrics."""
    try:
        text = crawl_data.get("text", "")
        html = crawl_data.get("html", "")

        service = GEOAnalysisService()
        analysis = service.analyze(text, html)

        return {
            "overall_score": analysis.overall_score,
            "metrics": {
                "answerability": analysis.metrics.get("answerability", 50),
                "passage_citability": analysis.metrics.get("passage_citability", 50),
                "question_structure": analysis.metrics.get("question_structure", 50),
                "entity_clarity": analysis.metrics.get("entity_clarity", 50),
                "attribution": analysis.metrics.get("attribution", 50),
                "structured_content": analysis.metrics.get("structured_content", 50),
            },
            "findings": [
                {
                    "metric": f.metric.value,
                    "severity": f.severity,
                    "title": f.title,
                    "description": f.description,
                    "recommendation": f.recommendation,
                }
                for f in analysis.findings
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"GEO analysis failed: {str(e)}")


@router.post("/crawl/schema")
async def analyze_crawl_schema(
    crawl_data: dict,
    user: models.User = Depends(get_current_user),
):
    """Analyze crawl data for Schema.org structured data."""
    try:
        html = crawl_data.get("html", "")

        service = SchemaAnalysisService()
        analysis = service.analyze(html)

        return {
            "overall_score": analysis.score,
            "blocks": [
                {
                    "type": b.type,
                    "properties": list(b.properties.keys()),
                    "valid": b.valid,
                    "errors": b.errors,
                }
                for b in analysis.blocks
            ],
            "findings": [
                {
                    "severity": f.severity,
                    "title": f.title,
                    "description": f.description,
                    "recommendation": f.recommendation,
                }
                for f in analysis.findings
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Schema analysis failed: {str(e)}")


@router.post("/crawl/eeat")
async def analyze_crawl_eeat(
    crawl_data: dict,
    user: models.User = Depends(get_current_user),
):
    """Analyze crawl data for E-E-A-T signals."""
    try:
        text = crawl_data.get("text", "")
        html = crawl_data.get("html", "")

        service = EEAATAnalysisService()
        analysis = service.analyze(text, html)

        return {
            "overall_score": analysis.overall_score,
            "dimensions": {
                "experience": analysis.dimensions.get("experience", 50),
                "expertise": analysis.dimensions.get("expertise", 50),
                "authoritativeness": analysis.dimensions.get("authoritativeness", 50),
                "trustworthiness": analysis.dimensions.get("trustworthiness", 50),
                "topical_depth": analysis.dimensions.get("topical_depth", 50),
            },
            "findings": [
                {
                    "dimension": f.dimension.value,
                    "severity": f.severity,
                    "title": f.title,
                    "description": f.description,
                    "recommendation": f.recommendation,
                }
                for f in analysis.findings
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"E-E-A-T analysis failed: {str(e)}")
