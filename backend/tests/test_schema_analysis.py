"""Tests for the Schema.org analysis service."""

import pytest
from app.services.schema_analysis_service import (
    SchemaAnalysisService,
    SchemaBlock,
)


@pytest.fixture
def service():
    return SchemaAnalysisService()


@pytest.fixture
def html_with_jsonld():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Article",
            "author": {"@type": "Person", "name": "John Doe"},
            "datePublished": "2024-01-15"
        }
        </script>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "What is SEO?", "acceptedAnswer": {"@type": "Answer", "text": "SEO is..."}},
                {"@type": "Question", "name": "How does it work?", "acceptedAnswer": {"@type": "Answer", "text": "It works by..."}}
            ]
        }
        </script>
    </body>
    </html>
    """


@pytest.fixture
def html_without_schema():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>No Schema</title></head>
    <body><p>Simple content without any structured data.</p></body>
    </html>
    """


class TestSchemaAnalysis:
    """Tests for Schema.org analysis."""

    def test_extract_json_ld(self, service, html_with_jsonld):
        """Test JSON-LD extraction."""
        blocks = service._extract_json_ld(html_with_jsonld)
        assert len(blocks) >= 2

    def test_analyze_with_schema(self, service, html_with_jsonld):
        """Test analysis with valid schema."""
        analysis = service.analyze(html_with_jsonld)
        assert analysis.score > 0
        assert len(analysis.blocks) > 0

    def test_analyze_without_schema(self, service, html_without_schema):
        """Test analysis without schema."""
        analysis = service.analyze(html_without_schema)
        assert analysis.score >= 0
        assert len(analysis.blocks) == 0

    def test_validates_article_schema(self, service, html_with_jsonld):
        """Test Article schema validation."""
        analysis = service.analyze(html_with_jsonld)
        article_blocks = [b for b in analysis.blocks if b.type == "Article"]
        assert len(article_blocks) > 0
        assert article_blocks[0].valid

    def test_validates_faq_schema(self, service, html_with_jsonld):
        """Test FAQPage schema validation."""
        analysis = service.analyze(html_with_jsonld)
        faq_blocks = [b for b in analysis.blocks if b.type == "FAQPage"]
        assert len(faq_blocks) > 0
        assert faq_blocks[0].valid

    def test_finding_count(self, service, html_without_schema):
        """Test findings when schema is missing."""
        analysis = service.analyze(html_without_schema)
        assert len(analysis.findings) > 0
        assert any("No structured data" in f.title for f in analysis.findings)

    def test_score_range(self, service, html_with_jsonld):
        """Test that score is within valid range."""
        analysis = service.analyze(html_with_jsonld)
        assert 0 <= analysis.score <= 100
