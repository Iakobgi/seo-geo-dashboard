"""Deterministic SEO scoring system with configurable weights."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from app.services.seo_analysis_service import (
    Finding,
    FindingCategory,
    SeverityLevel,
    CategoryAnalysis,
    SEOAnalysisService,
)
from app.services.crawler_service import CrawlResult


@dataclass
class ScoreBreakdown:
    """Detailed score breakdown for an audit."""
    overall_score: float
    geo_score: float  # Placeholder for Phase 2
    categories: List[CategoryAnalysis]
    formula: str
    finding_counts: Dict[str, int]

    def to_dict(self) -> Dict:
        return {
            "overall_score": self.overall_score,
            "geo_score": self.geo_score,
            "categories": [
                {
                    "category": cat.category.value,
                    "score": cat.score,
                    "weight": cat.weight,
                    "checks_count": cat.checks_count,
                    "passed_checks": cat.passed_checks,
                    "failed_checks": cat.failed_checks,
                    "important_findings": cat.important_findings[:5],
                }
                for cat in self.categories
            ],
            "formula": self.formula,
            "finding_counts": self.finding_counts,
        }


class ScoringService:
    """Service for calculating deterministic SEO scores."""

    # Default weights by category (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        FindingCategory.TITLE_META: 0.20,
        FindingCategory.CONTENT: 0.25,
        FindingCategory.LINKS: 0.15,
        FindingCategory.IMAGES: 0.10,
        FindingCategory.PERFORMANCE: 0.15,
        FindingCategory.STRUCTURED_DATA: 0.15,
        FindingCategory.INDEXABILITY: 0.0,  # Critical issues handled separately
    }

    # Critical indexability issues that cap the score
    CRITICAL_INDEXABILITY_ISSUES = [
        "Page blocked from indexing",
    ]

    def __init__(self, weights: Optional[Dict[FindingCategory, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._validate_weights()

    def _validate_weights(self) -> None:
        """Ensure weights sum to approximately 1.0."""
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    def calculate_score(
        self,
        findings: List[Finding],
        category_analyses: Optional[Dict[FindingCategory, CategoryAnalysis]] = None,
    ) -> ScoreBreakdown:
        """Calculate overall SEO score from findings."""
        # Get or calculate category analyses
        if category_analyses is None:
            service = SEOAnalysisService(self.weights)
            # This would need a crawl result in practice
            raise ValueError("category_analyses required")

        # Count findings by severity
        finding_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "pass": 0,
        }
        for finding in findings:
            severity = finding.severity.value
            finding_counts[severity] = finding_counts.get(severity, 0) + 1

        # Calculate weighted score
        weighted_sum = 0.0
        total_weight = 0.0

        categories_list = []
        for category, analysis in category_analyses.items():
            if category == FindingCategory.DUPLICATE_CONTENT:
                continue  # Handled within title_meta

            weight = self.weights.get(category, 0.0)
            if weight > 0:
                weighted_sum += analysis.score * weight
                total_weight += weight

            categories_list.append(analysis)

        # Normalize if weights don't sum to 1.0
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        # Check for critical indexability issues that cap the score
        indexability = category_analyses.get(FindingCategory.INDEXABILITY)
        if indexability:
            for finding in indexability.findings:
                if finding.title in self.CRITICAL_INDEXABILITY_ISSUES:
                    overall_score = min(overall_score, 10.0)  # Cap at 10

        # Round to 1 decimal place
        overall_score = round(overall_score, 1)

        # Build formula description
        formula = self._build_formula(categories_list, overall_score)

        return ScoreBreakdown(
            overall_score=overall_score,
            geo_score=50.0,  # Placeholder - will be calculated in Phase 2
            categories=categories_list,
            formula=formula,
            finding_counts=finding_counts,
        )

    def _build_formula(self, categories: List[CategoryAnalysis], final_score: float) -> str:
        """Build a human-readable formula description."""
        parts = []
        for cat in categories:
            if cat.weight > 0:
                parts.append(f"{cat.category.value}({cat.score:.0f}×{cat.weight:.0%})")

        if parts:
            return f"Score = {' + '.join(parts)} = {final_score:.1f}"
        return f"Score = {final_score:.1f}"

    def score_from_crawl(self, crawl_result: CrawlResult) -> ScoreBreakdown:
        """Calculate score directly from crawl result."""
        analysis_service = SEOAnalysisService(self.weights)

        # Get findings
        findings = analysis_service.analyze(crawl_result)

        # Get category analyses
        category_analyses = analysis_service.analyze_by_category(crawl_result)

        # Calculate score
        return self.calculate_score(findings, category_analyses)


def calculate_seo_score(crawl_result: CrawlResult) -> ScoreBreakdown:
    """Convenience function to calculate SEO score from crawl result."""
    service = ScoringService()
    return service.score_from_crawl(crawl_result)
