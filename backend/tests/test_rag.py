"""Tests for the RAG knowledge base service."""

import pytest
from app.services.rag_service import RAGService, KnowledgeResult


@pytest.fixture
def service():
    from unittest.mock import MagicMock
    db = MagicMock()
    return RAGService(db)


class TestRAGSearch:
    """Tests for RAG knowledge search."""

    def test_search_seo(self, service):
        """Test searching for SEO-related content."""
        results = service.search("SEO optimization title tags", limit=3)
        assert len(results) > 0
        assert all(isinstance(r, KnowledgeResult) for r in results)
        assert all(r.relevance_score > 0 for r in results)

    def test_search_geo(self, service):
        """Test searching for GEO-related content."""
        results = service.search("GEO generative engine optimization", limit=3)
        assert len(results) > 0

    def test_search_schema(self, service):
        """Test searching for Schema.org content."""
        results = service.search("Schema.org structured data JSON-LD", limit=3)
        assert len(results) > 0

    def test_search_no_results(self, service):
        """Test search with no matching content."""
        results = service.search("qwertyzxcv non-existent random nonsense 99999", limit=5)
        assert len(results) == 0

    def test_limit_results(self, service):
        """Test that limit is respected."""
        results = service.search("SEO", limit=2)
        assert len(results) <= 2

    def test_format_context(self, service):
        """Test context formatting for prompts."""
        context = service.get_rag_context("SEO best practices")
        formatted = service.format_context_for_prompt(context)
        assert isinstance(formatted, str)
        assert len(formatted) > 0

    def test_format_empty_context(self, service):
        """Test formatting with no results."""
        context = service.get_rag_context("qwertyzxcv non-existent random nonsense 99999")
        formatted = service.format_context_for_prompt(context)
        assert "No additional knowledge" in formatted

    def test_article_titles(self, service):
        """Test that returned articles have titles."""
        results = service.search("content depth")
        for r in results:
            assert r.title
            assert r.content
            assert r.relevance_score > 0
