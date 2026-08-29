"""Tests for security utilities."""

import pytest
from app.utils.security import is_safe_url, validate_url


class TestSSRFProtection:
    """Tests for SSRF protection."""

    def test_safe_public_url(self):
        """Test public URLs are allowed."""
        assert is_safe_url("https://example.com/page")
        assert is_safe_url("http://example.com/page")
        assert is_safe_url("https://www.google.com/search?q=test")

    def test_blocked_localhost(self):
        """Test localhost is blocked."""
        assert not is_safe_url("http://localhost:8080/admin")
        assert not is_safe_url("http://127.0.0.1:8080/")
        assert not is_safe_url("http://[::1]:8080/")

    def test_blocked_private_ranges(self):
        """Test private IP ranges are blocked."""
        assert not is_safe_url("http://192.168.1.1/admin")
        assert not is_safe_url("http://10.0.0.1/internal")
        assert not is_safe_url("http://172.16.0.1/private")
        assert not is_safe_url("http://169.254.169.254/latest/meta-data/")

    def test_blocked_invalid_scheme(self):
        """Test invalid schemes are blocked."""
        assert not is_safe_url("file:///etc/passwd")
        assert not is_safe_url("ftp://example.com/file")
        assert not is_safe_url("gopher://example.com/")

    def test_blocked_empty_url(self):
        """Test empty URLs are rejected."""
        assert not is_safe_url("")
        assert not is_safe_url(None)

    def test_validate_url_normalizes(self):
        """Test URL validation and normalization."""
        url = validate_url("example.com/page")
        assert url.startswith("https://")

    def test_validate_url_rejects_private(self):
        """Test validate_url rejects private addresses."""
        with pytest.raises(ValueError):
            validate_url("http://192.168.1.1/admin")

    def test_validate_url_rejects_invalid_scheme(self):
        """Test validate_url rejects invalid schemes."""
        with pytest.raises(ValueError):
            validate_url("file:///etc/passwd")

    def test_validate_url_accepts_public(self):
        """Test validate_url accepts public URLs."""
        url = validate_url("https://example.com/page")
        assert url == "https://example.com/page"
