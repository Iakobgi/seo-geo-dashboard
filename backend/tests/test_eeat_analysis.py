"""Tests for the E-E-A-T analysis service."""

import pytest
from app.services.eeat_analysis_service import (
    EEAATAnalysisService,
    EEAATDimension,
)


@pytest.fixture
def service():
    return EEAATAnalysisService()


@pytest.fixture
def rich_content():
    """Content with strong E-E-A-T signals."""
    return """
    <h1>How to Fix a Leaky Faucet: A plumber's guide</h1>
    <p>By John Smith, licensed plumber with 15 years of experience.</p>
    <p>I learned this technique from my apprenticeship and have used it on thousands of jobs.</p>
    <p>According to the Plumbing Industry Association, 70% of leaks can be fixed DIY.</p>
    <p>This article was last updated on March 15, 2024.</p>
    <p>Contact us at info@example.com or visit our about us page.</p>
    <p>Our privacy policy and terms of service are available.</p>
    <p>As seen in Forbes and featured in Home Depot guides.</p>
    """


@pytest.fixture
def thin_content():
    """Content with weak E-E-A-T signals."""
    return """
    <h1>Plumbing Tips</h1>
    <p>Some tips about plumbing.</p>
    """


class TestEEATAnalysis:
    """Tests for E-E-A-T analysis."""

    def test_experience_signals(self, service, rich_content):
        """Test experience signal detection."""
        result = service._analyze_experience(rich_content)
        assert result["score"] > 30
        assert len(result["findings"]) > 0

    def test_expertise_signals(self, service, rich_content):
        """Test expertise signal detection."""
        result = service._analyze_expertise(rich_content)
        assert result["score"] > 30

    def test_authoritativeness_signals(self, service, rich_content):
        """Test authority signal detection."""
        result = service._analyze_authoritativeness(rich_content)
        assert result["score"] >= 30

    def test_trustworthiness_signals(self, service, rich_content):
        """Test trust signal detection."""
        result = service._analyze_trustworthiness(rich_content)
        assert result["score"] > 30

    def test_topical_depth(self, service, rich_content):
        """Test topical depth analysis."""
        result = service._analyze_topical_depth(rich_content)
        assert result["score"] > 0

    def test_full_analysis_rich(self, service, rich_content):
        """Test complete E-E-A-T analysis on rich content."""
        analysis = service.analyze(rich_content, rich_content)
        assert analysis.overall_score >= 40
        for dim in EEAATDimension:
            assert dim in analysis.dimensions

    def test_full_analysis_thin(self, service, thin_content):
        """Test complete E-E-A-T analysis on thin content."""
        analysis = service.analyze(thin_content, thin_content)
        assert analysis.overall_score < 60

    def test_overall_score_calculation(self, service, rich_content):
        """Test overall score is weighted average."""
        analysis = service.analyze(rich_content, rich_content)
        weights = {
            EEAATDimension.EXPERIENCE: 0.15,
            EEAATDimension.EXPERTISE: 0.25,
            EEAATDimension.AUTHORITATIVENESS: 0.20,
            EEAATDimension.TRUSTWORTHINESS: 0.25,
            EEAATDimension.TOPICAL_DEPTH: 0.15,
        }
        total = sum(analysis.dimensions[d] * weights[d] for d in analysis.dimensions)
        weight_total = sum(weights[d] for d in analysis.dimensions)
        expected = round(total / weight_total, 1)
        assert abs(analysis.overall_score - expected) < 1

    def test_empty_content(self, service):
        """Test analysis with empty content."""
        analysis = service.analyze("", "")
        assert analysis.overall_score >= 0
        assert len(analysis.dimensions) == 5
