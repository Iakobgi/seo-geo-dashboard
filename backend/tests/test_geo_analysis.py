"""Tests for the GEO analysis service."""

import pytest
from app.services.geo_analysis_service import (
    GEOAnalysisService,
    GEOMetric,
    GEOFinding,
)


@pytest.fixture
def service():
    return GEOAnalysisService()


@pytest.fixture
def sample_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SEO Guide 2024 - Complete Tutorial</title>
        <meta name="description" content="Learn SEO from scratch with our comprehensive guide covering technical SEO, on-page optimization, and GEO strategies.">
    </head>
    <body>
        <h1>What is SEO and How Does It Work?</h1>
        <h2>What is Search Engine Optimization?</h2>
        <p>SEO refers to the practice of improving website visibility in search engines.</p>
        <h2>How to Improve Your SEO Score</h2>
        <p>To improve SEO, focus on content quality, technical performance, and user experience.</p>
        <h2>Why Does SEO Matter?</h2>
        <p>SEO drives organic traffic and is essential for online visibility.</p>
        <h2>FAQ</h2>
        <ul>
            <li>What is SEO?</li>
            <li>How long does SEO take?</li>
        </ul>
        <p>According to Google's guidelines, quality content is the foundation of SEO.</p>
        <p>Published on January 15, 2024 by John Smith, SEO Expert.</p>
        <img src="seo-chart.jpg" alt="SEO performance chart">
        <table>
            <tr><th>Factor</th><th>Impact</th></tr>
            <tr><td>Content</td><td>High</td></tr>
        </table>
    </body>
    </html>
    """


class TestGEOAnalysis:
    """Tests for GEO analysis functionality."""

    def test_analyze_answerability(self, service, sample_html):
        """Test answerability analysis."""
        result = service._analyze_answerability(sample_html)
        assert "score" in result
        assert 0 <= result["score"] <= 100

    def test_analyze_passage_citability(self, service, sample_html):
        """Test passage citability analysis."""
        result = service._analyze_passage_citability(sample_html)
        assert "score" in result
        assert 0 <= result["score"] <= 100

    def test_analyze_question_structure(self, service, sample_html):
        """Test question structure analysis."""
        result = service._analyze_question_structure(sample_html)
        assert "score" in result
        assert 0 <= result["score"] <= 100

    def test_analyze_entity_clarity(self, service, sample_html):
        """Test entity clarity analysis."""
        result = service._analyze_entity_clarity(sample_html)
        assert "score" in result
        assert 0 <= result["score"] <= 100

    def test_analyze_attribution(self, service, sample_html):
        """Test attribution analysis."""
        result = service._analyze_attribution(sample_html)
        assert "score" in result
        assert 0 <= result["score"] <= 100

    def test_analyze_structured_content(self, service, sample_html):
        """Test structured content analysis."""
        result = service._analyze_structured_content(sample_html, sample_html)
        assert "score" in result
        assert 0 <= result["score"] <= 100

    def test_full_analysis(self, service, sample_html):
        """Test complete GEO analysis."""
        analysis = service.analyze(sample_html, sample_html)
        assert analysis.overall_score > 0
        assert len(analysis.metrics) == 6
        for metric in GEOMetric:
            assert metric in analysis.metrics

    def test_empty_content(self, service):
        """Test analysis with empty content."""
        analysis = service.analyze("", "")
        assert analysis.overall_score >= 0
        assert len(analysis.metrics) == 6

    def test_overall_score_calculation(self, service):
        """Test overall score is weighted average."""
        analysis = service.analyze("", "")
        weights = {
            GEOMetric.ANSWERABILITY: 0.25,
            GEOMetric.PASSAGE_CITABILITY: 0.15,
            GEOMetric.QUESTION_STRUCTURE: 0.20,
            GEOMetric.ENTITY_CLARITY: 0.15,
            GEOMetric.ATTRIBUTION: 0.10,
            GEOMetric.STRUCTURED_CONTENT: 0.15,
        }
        total = sum(analysis.metrics[m] * weights[m] for m in analysis.metrics)
        weight_total = sum(weights[m] for m in analysis.metrics)
        expected = round(total / weight_total, 1)
        assert abs(analysis.overall_score - expected) < 1
