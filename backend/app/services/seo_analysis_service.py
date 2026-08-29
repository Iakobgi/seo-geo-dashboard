"""Technical SEO analysis engine with structured findings."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import re

from app.services.crawler_service import CrawlResult, CrawledPage


class FindingCategory(str, Enum):
    """Categories for SEO findings."""
    TITLE_META = "title_meta"
    CONTENT = "content"
    LINKS = "links"
    IMAGES = "images"
    PERFORMANCE = "performance"
    STRUCTURED_DATA = "structured_data"
    INDEXABILITY = "indexability"
    DUPLICATE_CONTENT = "duplicate_content"


class SeverityLevel(str, Enum):
    """Severity levels for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    PASS = "pass"


@dataclass
class Finding:
    """A single SEO finding with evidence."""
    category: FindingCategory
    severity: SeverityLevel
    url: str
    title: str
    description: str
    evidence: Dict[str, Any]
    recommendation: str
    impact_score: float  # 0-10, higher = more important

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "impact_score": self.impact_score,
        }


@dataclass
class CategoryAnalysis:
    """Analysis results for a single category."""
    category: FindingCategory
    score: float  # 0-100
    weight: float
    checks_count: int
    passed_checks: int
    failed_checks: int
    findings: List[Finding] = field(default_factory=list)

    @property
    def important_findings(self) -> List[str]:
        """Get titles of high-impact findings."""
        return [f.title for f in self.findings if f.impact_score >= 5.0]


class SEOAnalysisService:
    """Service for analyzing crawled pages and generating SEO findings."""

    # Scoring weights by category
    DEFAULT_WEIGHTS = {
        FindingCategory.TITLE_META: 0.20,
        FindingCategory.CONTENT: 0.25,
        FindingCategory.LINKS: 0.15,
        FindingCategory.IMAGES: 0.10,
        FindingCategory.PERFORMANCE: 0.15,
        FindingCategory.STRUCTURED_DATA: 0.15,
    }

    # Penalties by severity
    SEVERITY_PENALTIES = {
        SeverityLevel.CRITICAL: 15,
        SeverityLevel.HIGH: 10,
        SeverityLevel.MEDIUM: 5,
        SeverityLevel.LOW: 2,
        SeverityLevel.PASS: 0,
    }

    def __init__(self, weights: Optional[Dict[FindingCategory, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def analyze(self, crawl_result: CrawlResult) -> List[Finding]:
        """Analyze crawl results and return all findings."""
        findings: List[Finding] = []

        for page in crawl_result.pages:
            findings.extend(self._analyze_page(page))

        # Site-wide findings
        findings.extend(self._analyze_site_wide(crawl_result))

        return findings

    def analyze_by_category(self, crawl_result: CrawlResult) -> Dict[FindingCategory, CategoryAnalysis]:
        """Analyze and group findings by category with scores."""
        all_findings = self.analyze(crawl_result)

        by_category: Dict[FindingCategory, CategoryAnalysis] = {}
        for category in FindingCategory:
            if category == FindingCategory.DUPLICATE_CONTENT:
                continue  # Handled separately

            category_findings = [f for f in all_findings if f.category == category]
            score, passed, failed = self._calculate_category_score(category_findings)

            by_category[category] = CategoryAnalysis(
                category=category,
                score=score,
                weight=self.weights.get(category, 0.1),
                checks_count=passed + failed,
                passed_checks=passed,
                failed_checks=failed,
                findings=category_findings,
            )

        # Handle duplicate content separately
        dup_findings = [f for f in all_findings if f.category == FindingCategory.DUPLICATE_CONTENT]
        if dup_findings:
            score, passed, failed = self._calculate_category_score(dup_findings)
            by_category[FindingCategory.DUPLICATE_CONTENT] = CategoryAnalysis(
                category=FindingCategory.DUPLICATE_CONTENT,
                score=score,
                weight=0.0,  # Already accounted in title_meta
                checks_count=passed + failed,
                passed_checks=passed,
                failed_checks=failed,
                findings=dup_findings,
            )

        return by_category

    def _calculate_category_score(self, findings: List[Finding]) -> tuple[float, int, int]:
        """Calculate score for a category based on findings."""
        if not findings:
            return 100.0, 1, 0  # No findings = perfect score

        passed = sum(1 for f in findings if f.severity == SeverityLevel.PASS)
        failed = len(findings) - passed

        # Start from 100, subtract penalties
        score = 100.0
        for finding in findings:
            penalty = self.SEVERITY_PENALTIES.get(finding.severity, 0)
            score -= penalty

        return max(0.0, min(100.0, score)), passed, failed

    def _analyze_page(self, page: CrawledPage) -> List[Finding]:
        """Analyze a single page and return findings."""
        findings: List[Finding] = []

        # Title/Meta analysis
        findings.extend(self._analyze_title_meta(page))

        # Content analysis
        findings.extend(self._analyze_content(page))

        # Links analysis
        findings.extend(self._analyze_links(page))

        # Images analysis
        findings.extend(self._analyze_images(page))

        # Performance analysis
        findings.extend(self._analyze_performance(page))

        # Structured data analysis
        findings.extend(self._analyze_structured_data(page))

        # Indexability analysis
        findings.extend(self._analyze_indexability(page))

        return findings

    def _analyze_title_meta(self, page: CrawledPage) -> List[Finding]:
        """Analyze title and meta description."""
        findings: List[Finding] = []

        # Missing title
        if not page.title:
            findings.append(Finding(
                category=FindingCategory.TITLE_META,
                severity=SeverityLevel.CRITICAL,
                url=page.url,
                title="Missing page title",
                description="The page does not have a <title> tag. This is critical for SEO and search rankings.",
                evidence={"title": None},
                recommendation="Add a descriptive <title> tag to the page. Aim for 50-60 characters.",
                impact_score=9.0,
            ))
        else:
            # Title length
            title_len = len(page.title)
            if title_len < 30:
                findings.append(Finding(
                    category=FindingCategory.TITLE_META,
                    severity=SeverityLevel.MEDIUM,
                    url=page.url,
                    title="Title too short",
                    description=f"Page title is only {title_len} characters. Titles should be 50-60 characters for optimal display.",
                    evidence={"title": page.title, "length": title_len},
                    recommendation=f"Expand the title to 50-60 characters. Current: '{page.title}'",
                    impact_score=5.0,
                ))
            elif title_len > 60:
                findings.append(Finding(
                    category=FindingCategory.TITLE_META,
                    severity=SeverityLevel.LOW,
                    url=page.url,
                    title="Title too long",
                    description=f"Page title is {title_len} characters. Search engines may truncate it in results.",
                    evidence={"title": page.title, "length": title_len},
                    recommendation=f"Shorten the title to 50-60 characters. Current: '{page.title[:60]}...'",
                    impact_score=3.0,
                ))
            else:
                findings.append(Finding(
                    category=FindingCategory.TITLE_META,
                    severity=SeverityLevel.PASS,
                    url=page.url,
                    title="Title length is optimal",
                    description=f"Page title is {title_len} characters, within the optimal 50-60 character range.",
                    evidence={"title": page.title, "length": title_len},
                    recommendation="No action needed.",
                    impact_score=0.0,
                ))

        # Missing meta description
        if not page.meta_description:
            findings.append(Finding(
                category=FindingCategory.TITLE_META,
                severity=SeverityLevel.HIGH,
                url=page.url,
                title="Missing meta description",
                description="The page does not have a meta description. This affects click-through rates from search results.",
                evidence={"meta_description": None},
                recommendation="Add a meta description of 150-160 characters that summarizes the page content.",
                impact_score=7.0,
            ))
        else:
            # Meta description length
            desc_len = len(page.meta_description)
            if desc_len < 120:
                findings.append(Finding(
                    category=FindingCategory.TITLE_META,
                    severity=SeverityLevel.MEDIUM,
                    url=page.url,
                    title="Meta description too short",
                    description=f"Meta description is only {desc_len} characters. Aim for 150-160 characters.",
                    evidence={"meta_description": page.meta_description, "length": desc_len},
                    recommendation=f"Expand the meta description. Current: '{page.meta_description}'",
                    impact_score=4.0,
                ))
            elif desc_len > 160:
                findings.append(Finding(
                    category=FindingCategory.TITLE_META,
                    severity=SeverityLevel.LOW,
                    url=page.url,
                    title="Meta description too long",
                    description=f"Meta description is {desc_len} characters. Search engines may truncate it.",
                    evidence={"meta_description": page.meta_description[:160], "length": desc_len},
                    recommendation="Shorten the meta description to 150-160 characters.",
                    impact_score=2.0,
                ))
            else:
                findings.append(Finding(
                    category=FindingCategory.TITLE_META,
                    severity=SeverityLevel.PASS,
                    url=page.url,
                    title="Meta description length is optimal",
                    description=f"Meta description is {desc_len} characters, within optimal range.",
                    evidence={"meta_description": page.meta_description, "length": desc_len},
                    recommendation="No action needed.",
                    impact_score=0.0,
                ))

        return findings

    def _analyze_content(self, page: CrawledPage) -> List[Finding]:
        """Analyze content structure and depth."""
        findings: List[Finding] = []

        # Missing H1
        if not page.h1:
            findings.append(Finding(
                category=FindingCategory.CONTENT,
                severity=SeverityLevel.HIGH,
                url=page.url,
                title="Missing H1 heading",
                description="The page does not have an H1 heading. H1 is important for both SEO and accessibility.",
                evidence={"h1": None},
                recommendation="Add a single H1 heading that describes the main topic of the page.",
                impact_score=7.0,
            ))
        else:
            findings.append(Finding(
                category=FindingCategory.CONTENT,
                severity=SeverityLevel.PASS,
                url=page.url,
                title="H1 heading present",
                description="Page has an H1 heading.",
                evidence={"h1": page.h1},
                recommendation="No action needed.",
                impact_score=0.0,
            ))

        # Word count
        if page.word_count < 300:
            findings.append(Finding(
                category=FindingCategory.CONTENT,
                severity=SeverityLevel.HIGH if page.word_count < 150 else SeverityLevel.MEDIUM,
                url=page.url,
                title="Thin content",
                description=f"Page has only {page.word_count} words. This may be considered thin content by search engines.",
                evidence={"word_count": page.word_count},
                recommendation="Add more substantive content. Aim for at least 300 words, ideally 1000+ for in-depth topics.",
                impact_score=6.0 if page.word_count < 150 else 4.0,
            ))
        elif page.word_count >= 300:
            findings.append(Finding(
                category=FindingCategory.CONTENT,
                severity=SeverityLevel.PASS,
                url=page.url,
                title="Sufficient content length",
                description=f"Page has {page.word_count} words of content.",
                evidence={"word_count": page.word_count},
                recommendation="No action needed.",
                impact_score=0.0,
            ))

        # H2 structure
        if not page.h2:
            findings.append(Finding(
                category=FindingCategory.CONTENT,
                severity=SeverityLevel.LOW,
                url=page.url,
                title="No H2 headings",
                description="The page does not have any H2 headings. H2s help structure content for readers and search engines.",
                evidence={"h2_count": 0},
                recommendation="Add H2 headings to structure your content into logical sections.",
                impact_score=3.0,
            ))

        return findings

    def _analyze_links(self, page: CrawledPage) -> List[Finding]:
        """Analyze internal and external links."""
        findings: List[Finding] = []

        # No internal links
        if page.internal_links_count == 0:
            findings.append(Finding(
                category=FindingCategory.LINKS,
                severity=SeverityLevel.MEDIUM,
                url=page.url,
                title="No internal links",
                description="The page has no internal links. Internal linking helps search engines discover and understand site structure.",
                evidence={"internal_links_count": 0},
                recommendation="Add internal links to other relevant pages on your site.",
                impact_score=5.0,
            ))
        else:
            findings.append(Finding(
                category=FindingCategory.LINKS,
                severity=SeverityLevel.PASS,
                url=page.url,
                title="Internal links present",
                description=f"Page has {page.internal_links_count} internal links.",
                evidence={"internal_links_count": page.internal_links_count},
                recommendation="No action needed.",
                impact_score=0.0,
            ))

        # High external link ratio
        if page.links_count > 0:
            external_ratio = page.external_links_count / page.links_count
            if external_ratio > 0.5 and page.external_links_count > 10:
                findings.append(Finding(
                    category=FindingCategory.LINKS,
                    severity=SeverityLevel.LOW,
                    url=page.url,
                    title="High external link ratio",
                    description=f"{external_ratio:.0%} of links are external. This may indicate a directory or resource page.",
                    evidence={"external_ratio": external_ratio, "external_links": page.external_links_count},
                    recommendation="Ensure external links are relevant and add value. Consider adding more internal links.",
                    impact_score=2.0,
                ))

        return findings

    def _analyze_images(self, page: CrawledPage) -> List[Finding]:
        """Analyze image SEO."""
        findings: List[Finding] = []

        # Images present
        if page.images_count > 0:
            findings.append(Finding(
                category=FindingCategory.IMAGES,
                severity=SeverityLevel.PASS,
                url=page.url,
                title="Images present on page",
                description=f"Page contains {page.images_count} images.",
                evidence={"images_count": page.images_count},
                recommendation="Ensure all images have descriptive alt text.",
                impact_score=0.0,
            ))
        else:
            findings.append(Finding(
                category=FindingCategory.IMAGES,
                severity=SeverityLevel.LOW,
                url=page.url,
                title="No images on page",
                description="The page does not contain any images. Images can enhance user engagement.",
                evidence={"images_count": 0},
                recommendation="Consider adding relevant images to enhance the content.",
                impact_score=1.0,
            ))

        return findings

    def _analyze_performance(self, page: CrawledPage) -> List[Finding]:
        """Analyze page performance metrics."""
        findings: List[Finding] = []

        if page.load_time is not None:
            if page.load_time > 3.0:
                findings.append(Finding(
                    category=FindingCategory.PERFORMANCE,
                    severity=SeverityLevel.HIGH,
                    url=page.url,
                    title="Slow page load time",
                    description=f"Page loaded in {page.load_time:.2f}s. Pages should load in under 3 seconds.",
                    evidence={"load_time": page.load_time},
                    recommendation="Optimize images, minify CSS/JS, and consider using a CDN to improve load times.",
                    impact_score=6.0,
                ))
            elif page.load_time > 2.0:
                findings.append(Finding(
                    category=FindingCategory.PERFORMANCE,
                    severity=SeverityLevel.MEDIUM,
                    url=page.url,
                    title="Moderate page load time",
                    description=f"Page loaded in {page.load_time:.2f}s. Consider optimizing for faster load.",
                    evidence={"load_time": page.load_time},
                    recommendation="Review image sizes and eliminate render-blocking resources.",
                    impact_score=4.0,
                ))
            else:
                findings.append(Finding(
                    category=FindingCategory.PERFORMANCE,
                    severity=SeverityLevel.PASS,
                    url=page.url,
                    title="Good page load time",
                    description=f"Page loaded in {page.load_time:.2f}s.",
                    evidence={"load_time": page.load_time},
                    recommendation="No action needed.",
                    impact_score=0.0,
                ))

        return findings

    def _analyze_structured_data(self, page: CrawledPage) -> List[Finding]:
        """Analyze structured data (JSON-LD, etc.)."""
        findings: List[Finding] = []

        if page.json_ld:
            findings.append(Finding(
                category=FindingCategory.STRUCTURED_DATA,
                severity=SeverityLevel.PASS,
                url=page.url,
                title="Structured data detected",
                description=f"Page contains {len(page.json_ld)} JSON-LD structured data block(s).",
                evidence={"json_ld_count": len(page.json_ld), "types": [sd.get("@type", "Unknown") for sd in page.json_ld if isinstance(sd, dict)]},
                recommendation="Validate structured data using Google's Rich Results Test.",
                impact_score=0.0,
            ))
        else:
            findings.append(Finding(
                category=FindingCategory.STRUCTURED_DATA,
                severity=SeverityLevel.MEDIUM,
                url=page.url,
                title="No structured data detected",
                description="The page does not have JSON-LD structured data. This helps search engines understand content.",
                evidence={"json_ld_count": 0},
                recommendation="Add relevant structured data (Article, Product, FAQPage, etc.) using JSON-LD format.",
                impact_score=5.0,
            ))

        return findings

    def _analyze_indexability(self, page: CrawledPage) -> List[Finding]:
        """Analyze indexability signals."""
        findings: List[Finding] = []

        # noindex check
        if page.noindex:
            findings.append(Finding(
                category=FindingCategory.INDEXABILITY,
                severity=SeverityLevel.CRITICAL,
                url=page.url,
                title="Page blocked from indexing",
                description="The page has a 'noindex' robots meta tag. It will not appear in search results.",
                evidence={"noindex": True},
                recommendation="Remove the noindex directive if this page should be indexed by search engines.",
                impact_score=10.0,
            ))
        else:
            findings.append(Finding(
                category=FindingCategory.INDEXABILITY,
                severity=SeverityLevel.PASS,
                url=page.url,
                title="Page is indexable",
                description="The page can be indexed by search engines.",
                evidence={"noindex": False},
                recommendation="No action needed.",
                impact_score=0.0,
            ))

        # Canonical URL
        if page.canonical_url and page.canonical_url != page.url:
            findings.append(Finding(
                category=FindingCategory.INDEXABILITY,
                severity=SeverityLevel.LOW,
                url=page.url,
                title="Canonical URL points to different URL",
                description=f"Page has a canonical URL pointing to {page.canonical_url}.",
                evidence={"canonical_url": page.canonical_url},
                recommendation="Verify this is intentional. Canonical URLs consolidate ranking signals.",
                impact_score=2.0,
            ))

        return findings

    def _analyze_site_wide(self, crawl_result: CrawlResult) -> List[Finding]:
        """Analyze site-wide issues across all crawled pages."""
        findings: List[Finding] = []

        # Duplicate titles
        for title, urls in crawl_result.duplicate_titles.items():
            findings.append(Finding(
                category=FindingCategory.DUPLICATE_CONTENT,
                severity=SeverityLevel.HIGH,
                url=urls[0],
                title="Duplicate page titles",
                description=f"Multiple pages have the same title: '{title[:50]}...' if truncated",
                evidence={"title": title, "urls": urls},
                recommendation="Create unique titles for each page to improve SEO and user experience.",
                impact_score=6.0,
            ))

        # Duplicate meta descriptions
        for desc, urls in crawl_result.duplicate_meta_descriptions.items():
            findings.append(Finding(
                category=FindingCategory.DUPLICATE_CONTENT,
                severity=SeverityLevel.MEDIUM,
                url=urls[0],
                title="Duplicate meta descriptions",
                description="Multiple pages have the same meta description.",
                evidence={"meta_description": desc[:100], "urls": urls},
                recommendation="Create unique meta descriptions for each page.",
                impact_score=4.0,
            ))

        # Broken internal links
        if crawl_result.broken_internal_links:
            findings.append(Finding(
                category=FindingCategory.LINKS,
                severity=SeverityLevel.HIGH,
                url=crawl_result.start_url,
                title="Broken internal links detected",
                description=f"Found {len(crawl_result.broken_internal_links)} broken internal link(s).",
                evidence={"broken_links": crawl_result.broken_internal_links[:10]},
                recommendation="Fix or remove broken internal links to improve user experience and SEO.",
                impact_score=7.0,
            ))

        # robots.txt
        if not crawl_result.robots_txt_found:
            findings.append(Finding(
                category=FindingCategory.INDEXABILITY,
                severity=SeverityLevel.MEDIUM,
                url=crawl_result.start_url,
                title="No robots.txt found",
                description="The site does not have a robots.txt file. This helps control crawler behavior.",
                evidence={"robots_txt_found": False},
                recommendation="Add a robots.txt file to guide search engine crawlers.",
                impact_score=4.0,
            ))

        return findings


def analyze_crawl_result(crawl_result: CrawlResult) -> List[Finding]:
    """Convenience function to analyze a crawl result."""
    service = SEOAnalysisService()
    return service.analyze(crawl_result)
