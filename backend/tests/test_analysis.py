"""Tests for the SEO analysis service."""

import pytest
from app.services.seo_analysis_service import (
    SEOAnalysisService,
    Finding,
    FindingCategory,
    SeverityLevel,
    CrawledPage,
)


@pytest.fixture
def service():
    return SEOAnalysisService()


@pytest.fixture
def sample_page():
    return CrawledPage(
        url="https://example.com",
        status_code=200,
        title="Test Page Title - A Good 50 Character Title Here",
        meta_description="This is a well-written meta description that is between 150 and 160 characters long for optimal SEO display in search results.",
        h1="Main Heading",
        h2=["Section 1", "Section 2"],
        h3=["Subsection 1"],
        word_count=500,
        images_count=5,
        links_count=10,
        internal_links_count=8,
        external_links_count=2,
        load_time=1.5,
        canonical_url="https://example.com",
        json_ld=[{"@type": "Article", "headline": "Test Article"}],
    )


class TestTitleMetaAnalysis:
    """Tests for title and meta analysis."""

    def test_analyze_title_meta_pass(self, service, sample_page):
        """Test title and meta analysis with valid data."""
        findings = service._analyze_title_meta(sample_page)
        pass_findings = [f for f in findings if f.severity == SeverityLevel.PASS]
        # Title length check passes and meta description check passes
        assert len(pass_findings) >= 2

    def test_analyze_title_meta_missing_title(self, service, sample_page):
        """Test title analysis when title is missing."""
        page = CrawledPage(
            url="https://example.com",
            title=None,
            meta_description="Test description",
        )
        findings = service._analyze_title_meta(page)
        critical_findings = [f for f in findings if f.severity == SeverityLevel.CRITICAL]
        assert len(critical_findings) >= 1
        assert any("Missing page title" in f.title for f in critical_findings)

    def test_analyze_title_meta_short_title(self, service, sample_page):
        """Test title analysis when title is too short."""
        page = CrawledPage(
            url="https://example.com",
            title="Short",
            meta_description="Test description",
        )
        findings = service._analyze_title_meta(page)
        medium_findings = [f for f in findings if f.severity == SeverityLevel.MEDIUM]
        assert len(medium_findings) >= 1
        assert any("Title too short" in f.title for f in medium_findings)

    def test_analyze_title_meta_long_title(self, service, sample_page):
        """Test title analysis when title is too long."""
        page = CrawledPage(
            url="https://example.com",
            title="A" * 80,
            meta_description="Test description",
        )
        findings = service._analyze_title_meta(page)
        low_findings = [f for f in findings if f.severity == SeverityLevel.LOW]
        assert len(low_findings) >= 1
        assert any("Title too long" in f.title for f in low_findings)


class TestContentAnalysis:
    """Tests for content analysis."""

    def test_analyze_content_pass(self, service, sample_page):
        """Test content analysis with valid data."""
        findings = service._analyze_content(sample_page)
        pass_findings = [f for f in findings if f.severity == SeverityLevel.PASS]
        assert len(pass_findings) >= 2

    def test_analyze_content_missing_h1(self, service, sample_page):
        """Test content analysis when H1 is missing."""
        page = CrawledPage(
            url="https://example.com",
            h1=None,
            word_count=500,
        )
        findings = service._analyze_content(page)
        high_findings = [f for f in findings if f.severity == SeverityLevel.HIGH]
        assert len(high_findings) >= 1
        assert any("Missing H1" in f.title for f in high_findings)

    def test_analyze_content_thin(self, service, sample_page):
        """Test content analysis with thin content."""
        page = CrawledPage(
            url="https://example.com",
            h1="Test",
            word_count=100,
        )
        findings = service._analyze_content(page)
        high_findings = [f for f in findings if f.severity == SeverityLevel.HIGH]
        assert len(high_findings) >= 1
        assert any("Thin content" in f.title for f in high_findings)


class TestPerformanceAnalysis:
    """Tests for performance analysis."""

    def test_analyze_performance_good(self, service, sample_page):
        """Test performance analysis with good load time."""
        findings = service._analyze_performance(sample_page)
        pass_findings = [f for f in findings if f.severity == SeverityLevel.PASS]
        assert len(pass_findings) >= 1

    def test_analyze_performance_slow(self, service, sample_page):
        """Test performance analysis with slow load time."""
        page = CrawledPage(
            url="https://example.com",
            load_time=4.0,
        )
        findings = service._analyze_performance(page)
        high_findings = [f for f in findings if f.severity == SeverityLevel.HIGH]
        assert len(high_findings) >= 1
        assert any("Slow page" in f.title for f in high_findings)


class TestStructuredDataAnalysis:
    """Tests for structured data analysis."""

    def test_analyze_structured_data_pass(self, service, sample_page):
        """Test structured data analysis with JSON-LD present."""
        findings = service._analyze_structured_data(sample_page)
        pass_findings = [f for f in findings if f.severity == SeverityLevel.PASS]
        assert len(pass_findings) >= 1

    def test_analyze_structured_data_missing(self, service, sample_page):
        """Test structured data analysis when missing."""
        page = CrawledPage(
            url="https://example.com",
            json_ld=[],
        )
        findings = service._analyze_structured_data(page)
        medium_findings = [f for f in findings if f.severity == SeverityLevel.MEDIUM]
        assert len(medium_findings) >= 1
        assert any("No structured data" in f.title for f in medium_findings)


class TestIndexabilityAnalysis:
    """Tests for indexability analysis."""

    def test_analyze_indexability_pass(self, service, sample_page):
        """Test indexability analysis with indexable page."""
        findings = service._analyze_indexability(sample_page)
        pass_findings = [f for f in findings if f.severity == SeverityLevel.PASS]
        assert len(pass_findings) >= 1

    def test_analyze_indexability_noindex(self, service, sample_page):
        """Test indexability analysis with noindex."""
        page = CrawledPage(
            url="https://example.com",
            noindex=True,
        )
        findings = service._analyze_indexability(page)
        critical_findings = [f for f in findings if f.severity == SeverityLevel.CRITICAL]
        assert len(critical_findings) >= 1
        assert any("blocked from indexing" in f.title.lower() for f in critical_findings)


class TestSiteWideAnalysis:
    """Tests for site-wide analysis."""

    def test_analyze_site_wide_duplicates(self, service):
        """Test site-wide duplicate detection."""
        from app.services.crawler_service import CrawlResult

        crawl_result = CrawlResult(
            start_url="https://example.com",
            pages=[
                CrawledPage(url="https://example.com/page1", title="Page 1"),
                CrawledPage(url="https://example.com/page2", title="Page 1"),
            ],
            duplicate_titles={"Page 1": ["https://example.com/page1", "https://example.com/page2"]},
        )

        findings = service._analyze_site_wide(crawl_result)
        dup_findings = [f for f in findings if f.category == FindingCategory.DUPLICATE_CONTENT]
        assert len(dup_findings) >= 1
        assert any("Duplicate page titles" in f.title for f in dup_findings)


class TestFindingSerialization:
    """Tests for finding serialization."""

    def test_findings_to_dict(self, service):
        """Test finding serialization."""
        finding = Finding(
            category=FindingCategory.TITLE_META,
            severity=SeverityLevel.HIGH,
            url="https://example.com",
            title="Test Finding",
            description="Test description",
            evidence={"test": "data"},
            recommendation="Test recommendation",
            impact_score=7.0,
        )

        data = finding.to_dict()

        assert data["category"] == "title_meta"
        assert data["severity"] == "high"
        assert data["url"] == "https://example.com"
        assert data["title"] == "Test Finding"
        assert data["impact_score"] == 7.0
        assert data["evidence"] == {"test": "data"}


class TestScoreCalculation:
    """Tests for score calculation."""

    def test_category_score_calculation(self, service):
        """Test category score calculation."""
        findings = [
            Finding(
                category=FindingCategory.TITLE_META,
                severity=SeverityLevel.PASS,
                url="https://example.com",
                title="Pass",
                description="Pass",
                evidence={},
                recommendation="None",
                impact_score=0.0,
            ),
            Finding(
                category=FindingCategory.TITLE_META,
                severity=SeverityLevel.CRITICAL,
                url="https://example.com",
                title="Critical",
                description="Critical",
                evidence={},
                recommendation="Fix",
                impact_score=9.0,
            ),
        ]

        score, passed, failed = service._calculate_category_score(findings)

        assert passed == 1
        assert failed == 1
        # Score should be 100 - 15 (critical penalty) = 85
        assert score == 85.0
