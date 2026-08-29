"""Tests for the SERP service abstraction."""

import pytest
from unittest.mock import AsyncMock, patch
import asyncio

from app.services.serp_service import (
    SERPService,
    SERPResult,
    SimulatedProvider,
    SerpApiProvider,
    DataForSEOProvider,
)


class TestSimulatedProvider:
    """Tests for the simulated SERP provider."""

    @pytest.mark.asyncio
    async def test_search_returns_result(self):
        """Test basic search returns a result."""
        provider = SimulatedProvider()
        result = await provider.search("test keyword")
        assert isinstance(result, SERPResult)
        assert result.keyword == "test keyword"
        assert result.position is not None
        assert 1 <= result.position <= 100

    @pytest.mark.asyncio
    async def test_search_with_domain(self):
        """Test search with domain filtering."""
        provider = SimulatedProvider()
        result = await provider.search("test", domain="example.com")
        assert result.domain == "example.com"
        assert result.provider == "simulated"

    @pytest.mark.asyncio
    async def test_search_deterministic(self):
        """Test that simulated provider is deterministic with same seed."""
        provider1 = SimulatedProvider(seed=42)
        provider2 = SimulatedProvider(seed=42)
        result1 = await provider1.search("keyword")
        result2 = await provider2.search("keyword")
        assert result1.position == result2.position


class TestSERPService:
    """Tests for the SERP service facade."""

    def test_from_env_default(self):
        """Test creating service from env with defaults."""
        with patch.dict('os.environ', {}, clear=True):
            service = SERPService.from_env()
            assert service.provider_name == "simulated"

    def test_provider_name(self):
        """Test provider name is accessible."""
        service = SERPService()
        assert service.provider_name == "simulated"

    @pytest.mark.asyncio
    async def test_search_delegates(self):
        """Test search delegates to provider."""
        service = SERPService()
        result = await service.search("test keyword")
        assert isinstance(result, SERPResult)
        assert result.provider == "simulated"
