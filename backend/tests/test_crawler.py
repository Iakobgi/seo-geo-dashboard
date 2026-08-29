"""Tests for the crawler service."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

from app.services.crawler_service import (
    CrawlerService,
    CrawlerConfig,
    CrawlResult,
    CrawledPage,
    crawl_url,
)


@pytest.fixture
def config():
    return CrawlerConfig(
        max_pages=5,
        max_depth=1,
        respect_robots=False,
        timeout=5,
    )


@pytest.fixture
def sample_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="Test description">
        <link rel="canonical" href="https://example.com/test">
    </head>
    <body>
        <h1>Test Heading</h1>
        <h2>Section 1</h2>
        <h3>Subsection</h3>
        <p>This is a test paragraph with some content.</p>
        <img src="test.jpg" alt="Test image">
        <img src="test2.jpg">
        <a href="https://example.com/page1">Internal Link 1</a>
        <a href="https://external.com/page">External Link</a>
    </body>
    </html>
    """


@pytest.fixture
def crawler():
    return CrawlerService()


class TestCrawlerExtraction:
    """Tests for HTML extraction."""

    @pytest.mark.asyncio
    async def test_crawl_extract_data(self, crawler, sample_html):
        """Test that crawler correctly extracts data from HTML."""
        page = crawler._extract_page_data(
            sample_html,
            "https://example.com/test",
            1.5,
            200
        )

        assert page.title == "Test Page"
        assert page.meta_description == "Test description"
        assert page.h1 == "Test Heading"
        assert page.h2 == ["Section 1"]
        assert page.h3 == ["Subsection"]
        assert page.word_count > 5
        assert page.images_count == 2
        assert page.links_count == 2
        # Note: internal/external link counting depends on base domain being set
        assert page.canonical_url == "https://example.com/test"
        assert page.load_time == 1.5

    @pytest.mark.asyncio
    async def test_crawl_basics(self, config):
        """Test basic crawl functionality."""
        crawler = CrawlerService(config)

        # Mock httpx responses
        html1 = """
        <!DOCTYPE html>
        <html>
        <head><title>Page 1</title></head>
        <body>
            <h1>Page 1</h1>
            <a href="https://example.com/page2">Link to Page 2</a>
        </body>
        </html>
        """
        html2 = """
        <!DOCTYPE html>
        <html>
        <head><title>Page 2</title></head>
        <body>
            <h1>Page 2</h1>
            <p>Content on page 2.</p>
        </body>
        </html>
        """

        with patch('app.services.crawler_service.httpx.AsyncClient') as MockClient:
            mock_client = AsyncMock()

            async def mock_get(url, **kwargs):
                mock_response = MagicMock()
                if "page2" in url:
                    mock_response.text = html2
                else:
                    mock_response.text = html1
                mock_response.status_code = 200
                return mock_response

            mock_client.get = mock_get
            MockClient.return_value.__aenter__.return_value = mock_client
            MockClient.return_value.__aexit__.return_value = False

            result = await crawler.crawl("https://example.com/")

            assert result.pages_crawled >= 1
            assert result.start_url == "https://example.com/"
            assert len(result.pages) > 0


class TestURLNormalization:
    """Tests for URL normalization."""

    def test_normalize_url(self, crawler):
        """Test URL normalization."""
        # Should normalize trailing slashes
        assert crawler._normalize_url("https://example.com/page/") == "https://example.com/page"
        assert crawler._normalize_url("https://example.com/page") == "https://example.com/page"

        # Should remove fragment
        assert crawler._normalize_url("https://example.com/page#section") == "https://example.com/page"


class TestInternalURLDetection:
    """Tests for internal URL detection."""

    def test_is_internal_url(self, crawler):
        """Test internal URL detection."""
        crawler._base_domain = "example.com"

        assert crawler._is_internal_url("https://example.com/page")
        assert crawler._is_internal_url("http://www.example.com/page")
        assert not crawler._is_internal_url("https://other.com/page")
        assert not crawler._is_internal_url("https://sub.example.evil.com/page")


class TestRobotsAccess:
    """Tests for robots.txt access control."""

    def test_can_fetch_always_true_when_no_robots(self, crawler):
        """Test that can_fetch returns True when robots.txt not parsed."""
        assert crawler._can_fetch("https://example.com/page")


class TestStructuredDataExtraction:
    """Tests for structured data extraction."""

    def test_json_ld_extraction(self, crawler):
        """Test JSON-LD extraction."""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Test Article"
            }
            </script>
        </head>
        <body></body>
        </html>
        """
        page = crawler._extract_page_data(html, "https://example.com", 0.5, 200)

        assert len(page.json_ld) == 1
        assert page.json_ld[0]["@type"] == "Article"
        assert page.json_ld[0]["headline"] == "Test Article"

    def test_open_graph_extraction(self, crawler):
        """Test Open Graph tag extraction."""
        html = """
        <html>
        <head>
            <meta property="og:title" content="OG Title">
            <meta property="og:description" content="OG Description">
            <meta property="og:image" content="https://example.com/image.jpg">
        </head>
        <body></body>
        </html>
        """
        page = crawler._extract_page_data(html, "https://example.com", 0.5, 200)

        assert page.open_graph["title"] == "OG Title"
        assert page.open_graph["description"] == "OG Description"
        assert page.open_graph["image"] == "https://example.com/image.jpg"

    def test_noindex_detection(self, crawler):
        """Test noindex meta tag detection."""
        html = """
        <html>
        <head>
            <meta name="robots" content="noindex, follow">
        </head>
        <body></body>
        </html>
        """
        page = crawler._extract_page_data(html, "https://example.com", 0.5, 200)

        assert page.noindex == True
        assert page.nofollow == False
