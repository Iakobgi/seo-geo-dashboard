"""Multi-page SEO crawler with Playwright for JavaScript rendering."""

import time
import re
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from urllib.parse import urljoin, urlparse, urlunparse
from urllib import robotparser
import httpx
from bs4 import BeautifulSoup


@dataclass
class CrawledPage:
    """Data extracted from a single crawled page."""
    url: str
    status_code: Optional[int] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1: Optional[str] = None
    h2: List[str] = field(default_factory=list)
    h3: List[str] = field(default_factory=list)
    word_count: int = 0
    images_count: int = 0
    links_count: int = 0
    internal_links_count: int = 0
    external_links_count: int = 0
    internal_links: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    load_time: Optional[float] = None
    canonical_url: Optional[str] = None
    noindex: bool = False
    nofollow: bool = False
    json_ld: List[Dict[str, Any]] = field(default_factory=list)
    open_graph: Dict[str, str] = field(default_factory=dict)
    html: Optional[str] = None


@dataclass
class CrawlResult:
    """Results from a multi-page crawl."""
    start_url: str
    pages: List[CrawledPage] = field(default_factory=list)
    pages_crawled: int = 0
    broken_internal_links: List[str] = field(default_factory=list)
    duplicate_titles: Dict[str, List[str]] = field(default_factory=dict)
    duplicate_meta_descriptions: Dict[str, List[str]] = field(default_factory=dict)
    robots_txt_found: bool = False
    sitemap_urls: List[str] = field(default_factory=list)
    crawl_duration: float = 0.0


@dataclass
class CrawlerConfig:
    """Configuration for the crawler."""
    max_pages: int = 10
    max_depth: int = 2
    respect_robots: bool = True
    timeout: int = 15
    user_agent: str = "SEO-GEO-Dashboard-Bot/1.0 (+https://github.com/)"
    rate_limit_delay: float = 0.5  # seconds between requests
    follow_redirects: bool = True
    render_js: bool = False  # If False, use httpx; if True, use Playwright


class CrawlerService:
    """Service for crawling websites and extracting SEO data."""

    def __init__(self, config: Optional[CrawlerConfig] = None):
        self.config = config or CrawlerConfig()
        self._visited: Set[str] = set()
        self._base_domain: Optional[str] = None
        self._robots_parser: Optional[robotparser.RobotFileParser] = None
        self._broken_links: Set[str] = set()

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url)
        # Remove fragment, ensure scheme
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip('/') or '/',
            parsed.params,
            parsed.query,
            ''
        ))
        return normalized

    def _is_internal_url(self, url: str) -> bool:
        """Check if URL belongs to the base domain (handles www and non-www)."""
        if not self._base_domain:
            return False
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        # Strip www. prefix for comparison
        base_without_www = self._base_domain.lower().lstrip("www.")
        netloc_without_www = netloc.lstrip("www.")
        return netloc_without_www == base_without_www or netloc == self._base_domain.lower()

    def _can_fetch(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        if not self.config.respect_robots or not self._robots_parser:
            return True
        try:
            return self._robots_parser.can_fetch(self.config.user_agent, url)
        except Exception:
            return True  # Allow on error

    async def _fetch_robots_txt(self, base_url: str) -> bool:
        """Fetch and parse robots.txt."""
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                resp = await client.get(robots_url, headers={"User-Agent": self.config.user_agent})
                if resp.status_code == 200:
                    self._robots_parser = robotparser.RobotFileParser()
                    self._robots_parser.set_url(robots_url)
                    self._robots_parser.parse(resp.text.splitlines())
                    return True
        except Exception:
            pass
        return False

    async def _fetch_sitemap_urls(self, base_url: str) -> List[str]:
        """Discover sitemap URLs from robots.txt and common locations."""
        sitemap_urls = []
        parsed = urlparse(base_url)

        # Check robots.txt for sitemap directives
        if self._robots_parser and hasattr(self._robots_parser, 'site_maps'):
            sitemaps = self._robots_parser.site_maps()
            if sitemaps:
                sitemap_urls.extend(sitemaps)

        # Check common sitemap locations
        common_paths = ["/sitemap.xml", "/sitemap_index.xml"]
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            for path in common_paths:
                sitemap_url = f"{parsed.scheme}://{parsed.netloc}{path}"
                try:
                    resp = await client.head(sitemap_url, headers={"User-Agent": self.config.user_agent})
                    if resp.status_code == 200 and sitemap_url not in sitemap_urls:
                        sitemap_urls.append(sitemap_url)
                except Exception:
                    continue

        return sitemap_urls

    def _extract_page_data(self, html: str, url: str, load_time: float, status_code: int) -> CrawledPage:
        """Extract SEO data from HTML content."""
        soup = BeautifulSoup(html, "html.parser")
        page = CrawledPage(
            url=url,
            status_code=status_code,
            load_time=round(load_time, 3),
            html=html[:50000]  # Limit stored HTML size
        )

        # Title
        title_tag = soup.find("title")
        if title_tag:
            page.title = title_tag.get_text(strip=True)

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            page.meta_description = meta_desc.get("content", "").strip()

        # Canonical URL
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href"):
            page.canonical_url = urljoin(url, canonical.get("href"))

        # Robots meta
        robots_meta = soup.find("meta", attrs={"name": "robots"})
        if robots_meta:
            content = robots_meta.get("content", "").lower()
            page.noindex = "noindex" in content
            page.nofollow = "nofollow" in content

        # Headings
        h1_tag = soup.find("h1")
        if h1_tag:
            page.h1 = h1_tag.get_text(strip=True)

        page.h2 = [h.get_text(strip=True) for h in soup.find_all("h2")[:10] if h.get_text(strip=True)]
        page.h3 = [h.get_text(strip=True) for h in soup.find_all("h3")[:10] if h.get_text(strip=True)]

        # Word count
        text_content = soup.get_text(" ", strip=True)
        page.word_count = len(re.findall(r"\w+", text_content))

        # Images
        images = soup.find_all("img")
        page.images_count = len(images)

        # Links
        links = soup.find_all("a", href=True)
        page.links_count = len(links)

        for link in links:
            href = link.get("href", "").strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            absolute_url = urljoin(url, href)
            normalized = self._normalize_url(absolute_url)

            if self._is_internal_url(absolute_url):
                page.internal_links_count += 1
                if normalized not in page.internal_links:
                    page.internal_links.append(normalized)
            else:
                page.external_links_count += 1
                if absolute_url not in page.external_links:
                    page.external_links.append(absolute_url)

        # JSON-LD structured data
        json_ld_scripts = soup.find_all("script", type="application/ld+json")
        for script in json_ld_scripts:
            try:
                import json
                data = json.loads(script.string or "{}")
                if isinstance(data, list):
                    page.json_ld.extend(data)
                else:
                    page.json_ld.append(data)
            except Exception:
                continue

        # Open Graph
        og_tags = soup.find_all("meta", property=re.compile(r"^og:"))
        for tag in og_tags:
            prop = tag.get("property", "").replace("og:", "")
            content = tag.get("content", "")
            if prop and content:
                page.open_graph[prop] = content

        return page

    async def _fetch_page_httpx(self, url: str) -> tuple[Optional[str], int, float]:
        """Fetch page using httpx (no JS rendering)."""
        start = time.time()
        try:
            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                follow_redirects=self.config.follow_redirects,
                headers={"User-Agent": self.config.user_agent}
            ) as client:
                resp = await client.get(url)
                load_time = time.time() - start
                return resp.text, resp.status_code, load_time
        except Exception as e:
            return None, 0, 0.0

    async def _crawl_page(self, url: str, depth: int, queue: asyncio.Queue) -> Optional[CrawledPage]:
        """Crawl a single page and queue internal links."""
        normalized = self._normalize_url(url)

        if normalized in self._visited:
            return None

        if not self._can_fetch(url):
            return None

        self._visited.add(normalized)

        # Rate limiting
        await asyncio.sleep(self.config.rate_limit_delay)

        html, status_code, load_time = await self._fetch_page_httpx(url)

        if html is None:
            self._broken_links.add(url)
            return None

        page = self._extract_page_data(html, url, load_time, status_code)

        # Queue internal links if within depth limit
        if depth < self.config.max_depth:
            for internal_url in page.internal_links:
                if self._normalize_url(internal_url) not in self._visited:
                    await queue.put((internal_url, depth + 1))

        return page

    async def crawl(self, start_url: str) -> CrawlResult:
        """Perform a multi-page crawl starting from the given URL."""
        start_time = time.time()
        result = CrawlResult(start_url=start_url)

        # Parse base domain
        parsed = urlparse(start_url)
        self._base_domain = parsed.netloc.lower()

        # Fetch robots.txt
        result.robots_txt_found = await self._fetch_robots_txt(start_url)

        # Discover sitemaps
        result.sitemap_urls = await self._fetch_sitemap_urls(start_url)

        # Initialize crawl queue
        queue: asyncio.Queue = asyncio.Queue()
        await queue.put((start_url, 0))

        pages_by_title: Dict[str, List[str]] = {}
        pages_by_meta: Dict[str, List[str]] = {}

        # BFS crawl
        while not queue.empty() and len(result.pages) < self.config.max_pages:
            url, depth = await queue.get()

            page = await self._crawl_page(url, depth, queue)

            if page:
                result.pages.append(page)

                # Track duplicates
                if page.title:
                    pages_by_title.setdefault(page.title, []).append(page.url)
                if page.meta_description:
                    pages_by_meta.setdefault(page.meta_description, []).append(page.url)

        # Identify duplicates
        result.duplicate_titles = {
            title: urls for title, urls in pages_by_title.items()
            if len(urls) > 1
        }
        result.duplicate_meta_descriptions = {
            desc: urls for desc, urls in pages_by_meta.items()
            if len(urls) > 1
        }

        # Check broken links
        result.broken_internal_links = list(self._broken_links)

        result.pages_crawled = len(result.pages)
        result.crawl_duration = round(time.time() - start_time, 2)

        return result


async def crawl_url(url: str, max_pages: int = 10, max_depth: int = 2, respect_robots: bool = True) -> CrawlResult:
    """Convenience function to crawl a URL with default config."""
    config = CrawlerConfig(
        max_pages=max_pages,
        max_depth=max_depth,
        respect_robots=respect_robots
    )
    crawler = CrawlerService(config)
    return await crawler.crawl(url)
