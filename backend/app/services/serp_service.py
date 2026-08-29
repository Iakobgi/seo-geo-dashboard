"""SERP (Search Engine Results Page) service abstraction.

Supports multiple providers (SerpApi, DataForSEO, etc.) with a
simulated fallback for local development.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
import os
import random


@dataclass
class SERPResult:
    """Result from a SERP provider."""
    keyword: str
    domain: str
    position: int  # 1-based, None if not found
    url: Optional[str] = None
    title: Optional[str] = None
    snippet: Optional[str] = None
    search_volume: Optional[int] = None
    provider: str = "simulated"


class SERPProvider(ABC):
    """Abstract base for SERP providers."""

    @abstractmethod
    async def search(self, keyword: str, domain: Optional[str] = None) -> SERPResult:
        """Search SERP for a keyword and optionally a specific domain."""
        ...


class SimulatedProvider(SERPProvider):
    """Simulated SERP provider for development/testing."""

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    async def search(self, keyword: str, domain: Optional[str] = None) -> SERPResult:
        position = self._rng.randint(1, 50)
        search_volume = self._rng.randint(100, 100000)
        return SERPResult(
            keyword=keyword,
            domain=domain,
            position=position,
            search_volume=search_volume,
            provider="simulated",
        )


class SerpApiProvider(SERPProvider):
    """SerpApi provider for real SERP data."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    async def search(self, keyword: str, domain: Optional[str] = None) -> SERPResult:
        import httpx
        params = {
            "engine": "google",
            "q": keyword,
            "api_key": self._api_key,
        }
        if domain:
            params["gl"] = "us"
            params["hl"] = "en"

        async with httpx.AsyncClient() as client:
            resp = await client.get("https://serpapi.com/search", params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

        organic_results = data.get("organic_results", [])
        position = None
        url = None
        title = None
        snippet = None

        for entry in organic_results:
            if domain and domain.lower() in (entry.get("link") or "").lower():
                position = organic_results.index(entry) + 1
                url = entry.get("link")
                title = entry.get("title")
                snippet = entry.get("snippet")
                break
            elif position is None:
                position = organic_results.index(entry) + 1

        return SERPResult(
            keyword=keyword,
            domain=domain,
            position=position,
            url=url,
            title=title,
            snippet=snippet,
            search_volume=data.get("search_information", {}).get("total_results"),
            provider="serpapi",
        )


class DataForSEOProvider(SERPProvider):
    """DataForSEO provider for real SERP data."""

    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password

    async def search(self, keyword: str, domain: Optional[str] = None) -> SERPResult:
        import httpx
        data = {
            "tasks": [
                {
                    "type": "organic",
                    "language_code": "en",
                    "location_code": 2840,
                    "keyword": keyword,
                    "limit": 10,
                }
            ]
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.dataforseo.com/v3/keywords_data/google/organic/live/advanced",
                auth=(self._username, self._password),
                json=data,
                timeout=30,
            )
            resp.raise_for_status()
            json_data = resp.json()

        results = json_data.get("tasks", [{}])[0].get("result", [])
        position = None
        url = None
        title = None
        snippet = None

        for entry in results:
            if domain and domain.lower() in (entry.get("url") or "").lower():
                position = entry.get("position")
                url = entry.get("url")
                title = entry.get("title")
                snippet = entry.get("snippet")
                break

        return SERPResult(
            keyword=keyword,
            domain=domain,
            position=position,
            url=url,
            title=title,
            snippet=snippet,
            search_volume=None,
            provider="dataforseo",
        )


class SERPService:
    """Facade that selects the appropriate SERP provider."""

    def __init__(self, provider: str = "simulated", **kwargs):
        if provider == "serpapi":
            self._provider: SERPProvider = SerpApiProvider(**kwargs)
        elif provider == "dataforseo":
            self._provider: SERPProvider = DataForSEOProvider(**kwargs)
        else:
            self._provider = SimulatedProvider()
        self._provider_name = provider

    async def search(self, keyword: str, domain: Optional[str] = None) -> SERPResult:
        return await self._provider.search(keyword, domain)

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @classmethod
    def from_env(cls) -> "SERPService":
        """Create SERPService from environment variables."""
        provider = os.getenv("SERP_PROVIDER", "simulated")
        kwargs = {}
        if provider == "serpapi":
            kwargs["api_key"] = os.getenv("SERPAPI_KEY", "")
        elif provider == "dataforseo":
            kwargs["username"] = os.getenv("DATAFORSEO_USERNAME", "")
            kwargs["password"] = os.getenv("DATAFORSEO_PASSWORD", "")
        return cls(provider, **kwargs)
