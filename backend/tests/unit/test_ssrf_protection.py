"""
Tests for SSRF Protection Utilities

Feature: Security Hardening
"""

import pytest
from src.utils.ssrf_protection import (
    is_ip_blocked,
    validate_url_for_ssrf,
    SSRFProtectionError,
)


class TestIsIPBlocked:
    """Test IP blocking logic."""
    
    def test_blocks_localhost_ipv4(self):
        """Should block localhost IP."""
        assert is_ip_blocked("127.0.0.1") is True
        assert is_ip_blocked("127.0.0.100") is True
    
    def test_blocks_private_networks(self):
        """Should block RFC 1918 private networks."""
        assert is_ip_blocked("10.0.0.1") is True
        assert is_ip_blocked("10.255.255.255") is True
        assert is_ip_blocked("172.16.0.1") is True
        assert is_ip_blocked("172.31.255.255") is True
        assert is_ip_blocked("192.168.0.1") is True
        assert is_ip_blocked("192.168.255.255") is True
    
    def test_blocks_link_local(self):
        """Should block link-local addresses (AWS metadata)."""
        assert is_ip_blocked("169.254.169.254") is True
        assert is_ip_blocked("169.254.0.1") is True
    
    def test_blocks_multicast(self):
        """Should block multicast addresses."""
        assert is_ip_blocked("224.0.0.1") is True
        assert is_ip_blocked("239.255.255.255") is True
    
    def test_blocks_localhost_ipv6(self):
        """Should block IPv6 localhost."""
        assert is_ip_blocked("::1") is True
    
    def test_allows_public_ips(self):
        """Should allow public IP addresses."""
        assert is_ip_blocked("8.8.8.8") is False  # Google DNS
        assert is_ip_blocked("1.1.1.1") is False  # Cloudflare DNS
        assert is_ip_blocked("13.107.42.14") is False  # Microsoft
    
    def test_blocks_invalid_ip(self):
        """Should block invalid IP addresses."""
        assert is_ip_blocked("not-an-ip") is True
        assert is_ip_blocked("999.999.999.999") is True


class TestValidateURLForSSRF:
    """Test URL validation for SSRF protection."""
    
    def test_allows_valid_public_urls(self):
        """Should allow URLs with public IPs."""
        # Test with actual IP address (no DNS needed)
        hostname, ip = validate_url_for_ssrf("https://8.8.8.8")
        assert hostname == "8.8.8.8"
        assert ip == "8.8.8.8"
        assert not is_ip_blocked(ip)
    
    def test_blocks_localhost_urls(self):
        """Should block localhost URLs."""
        with pytest.raises(SSRFProtectionError) as exc_info:
            validate_url_for_ssrf("http://localhost:8000/api")
        assert "blocked" in str(exc_info.value).lower()
        
        with pytest.raises(SSRFProtectionError) as exc_info:
            validate_url_for_ssrf("http://127.0.0.1:8000")
        assert "blocked" in str(exc_info.value).lower()
    
    def test_blocks_private_ip_urls(self):
        """Should block private network URLs."""
        private_ips = [
            "http://10.0.0.1",
            "http://192.168.1.1",
            "http://172.16.0.1",
        ]
        for url in private_ips:
            with pytest.raises(SSRFProtectionError) as exc_info:
                validate_url_for_ssrf(url)
            assert "blocked" in str(exc_info.value).lower()
    
    def test_blocks_aws_metadata_url(self):
        """Should block AWS metadata endpoint."""
        with pytest.raises(SSRFProtectionError) as exc_info:
            validate_url_for_ssrf("http://169.254.169.254/latest/meta-data/")
        assert "blocked" in str(exc_info.value).lower()
    
    def test_blocks_invalid_scheme(self):
        """Should block non-http(s) schemes."""
        with pytest.raises(SSRFProtectionError) as exc_info:
            validate_url_for_ssrf("file:///etc/passwd")
        assert "scheme" in str(exc_info.value).lower()
        
        with pytest.raises(SSRFProtectionError) as exc_info:
            validate_url_for_ssrf("ftp://example.com")
        assert "scheme" in str(exc_info.value).lower()
    
    def test_blocks_url_without_hostname(self):
        """Should block URLs without hostname."""
        with pytest.raises(SSRFProtectionError):
            validate_url_for_ssrf("http://")
    
    def test_handles_invalid_url(self):
        """Should raise error for malformed URLs."""
        with pytest.raises(SSRFProtectionError):
            validate_url_for_ssrf("not a valid url at all")
