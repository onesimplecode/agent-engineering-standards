"""Tests for examples/ssrf-allowlist/safe_fetch.py (v0.9).

No live network: DNS and urlopen are mocked. Contract under test: allowlist,
fail-closed private addresses, redirect hop re-validation, and DNS pin
(no second getaddrinfo for the pinned host during the hop).
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import pytest

EXAMPLE_DIR = Path(__file__).resolve().parent.parent / "examples" / "ssrf-allowlist"
sys.path.insert(0, str(EXAMPLE_DIR))

from safe_fetch import (  # noqa: E402
    ALLOWED_HOSTS,
    SSRFError,
    fetch_url,
    host_is_allowlisted,
    validate_url,
)


def _addrinfo(ip: str):
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    return [(family, socket.SOCK_STREAM, 6, "", (ip, 0))]


class TestHostAllowlist:
    def test_exact_and_subdomain(self):
        assert host_is_allowlisted("feeds.example.com") is True
        assert host_is_allowlisted("rss.feeds.example.com") is True
        assert host_is_allowlisted("evil.com") is False
        assert host_is_allowlisted("example.com") is False  # parent not listed

    def test_allowed_hosts_is_co_located_frozenset(self):
        assert isinstance(ALLOWED_HOSTS, frozenset)
        assert "feeds.example.com" in ALLOWED_HOSTS


class TestValidateUrl:
    def test_rejects_non_allowlisted_host(self):
        with pytest.raises(SSRFError, match="not in ALLOWED_HOSTS"):
            validate_url("https://evil.example.org/x")

    def test_rejects_file_scheme(self):
        with pytest.raises(SSRFError, match="scheme"):
            validate_url("file:///etc/passwd")

    def test_rejects_private_resolution(self):
        with patch("safe_fetch.socket.getaddrinfo", return_value=_addrinfo("10.0.0.5")):
            with pytest.raises(SSRFError, match="private or reserved"):
                validate_url("https://feeds.example.com/item")

    def test_rejects_link_local_metadata_range(self):
        with patch("safe_fetch.socket.getaddrinfo", return_value=_addrinfo("169.254.169.254")):
            with pytest.raises(SSRFError, match="private or reserved"):
                validate_url("https://cdn.example.com/x")

    def test_fails_closed_on_empty_dns(self):
        with patch("safe_fetch.socket.getaddrinfo", return_value=[]):
            with pytest.raises(SSRFError, match="no addresses"):
                validate_url("https://feeds.example.com/item")

    def test_allows_public_allowlisted_host(self):
        with patch("safe_fetch.socket.getaddrinfo", return_value=_addrinfo("93.184.216.34")):
            infos = validate_url("https://feeds.example.com/rss.xml")
            assert infos[0][4][0] == "93.184.216.34"


class TestFetchRedirectHops:
    def test_redirect_to_non_allowlisted_host_is_rejected(self):
        redirect = MagicMock()
        redirect.getcode.return_value = 302
        redirect.headers = {"Location": "https://evil.example.org/steal"}
        redirect.read.return_value = b""
        redirect.__enter__.return_value = redirect
        redirect.__exit__.return_value = False

        with patch("safe_fetch.socket.getaddrinfo", return_value=_addrinfo("93.184.216.34")), \
             patch("safe_fetch.urlopen", return_value=redirect):
            with pytest.raises(SSRFError, match="not in ALLOWED_HOSTS"):
                fetch_url("https://feeds.example.com/start")

    def test_redirect_to_allowlisted_host_that_resolves_private_is_rejected(self):
        """Hop 1 public; Location is allowlisted but rebinds to RFC1918 — must fail."""
        public = _addrinfo("93.184.216.34")
        private = _addrinfo("192.168.1.10")

        def _dns(host, *args, **kwargs):
            if host == "feeds.example.com":
                return public
            if host == "cdn.example.com":
                return private
            raise AssertionError(f"unexpected host {host!r}")

        redirect = MagicMock()
        redirect.getcode.return_value = 302
        redirect.headers = {"Location": "https://cdn.example.com/next"}
        redirect.read.return_value = b""
        redirect.__enter__.return_value = redirect
        redirect.__exit__.return_value = False

        with patch("safe_fetch.socket.getaddrinfo", side_effect=_dns), \
             patch("safe_fetch.urlopen", return_value=redirect):
            with pytest.raises(SSRFError, match="private or reserved"):
                fetch_url("https://feeds.example.com/start")

    def test_successful_body_returned_without_redirect(self):
        resp = MagicMock()
        resp.getcode.return_value = 200
        resp.headers = {}
        resp.read.return_value = b"ok"
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False

        with patch("safe_fetch.socket.getaddrinfo", return_value=_addrinfo("93.184.216.34")), \
             patch("safe_fetch.urlopen", return_value=resp):
            assert fetch_url("https://feeds.example.com/item") == b"ok"

    def test_http_error_status_raises_urlerror(self):
        resp = MagicMock()
        resp.getcode.return_value = 500
        resp.headers = {}
        resp.read.return_value = b"nope"
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False

        with patch("safe_fetch.socket.getaddrinfo", return_value=_addrinfo("93.184.216.34")), \
             patch("safe_fetch.urlopen", return_value=resp):
            with pytest.raises(URLError, match="HTTP 500"):
                fetch_url("https://feeds.example.com/item")


class TestDnsPin:
    def test_no_second_getaddrinfo_for_pinned_host_during_connect(self):
        """During urlopen, a rebind of the process resolver must not be seen
        for the pinned hostname — the pin returns the validated public IP."""
        public = _addrinfo("93.184.216.34")
        rebind = _addrinfo("169.254.169.254")
        call_count = {"n": 0}

        def _dns(host, *args, **kwargs):
            call_count["n"] += 1
            # First call(s) during validate; if pin works, connect-time
            # lookups for this host never hit this function.
            return public

        resp = MagicMock()
        resp.getcode.return_value = 200
        resp.headers = {}
        resp.read.return_value = b"body"
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False

        with patch("safe_fetch.socket.getaddrinfo", side_effect=_dns) as mock_dns, \
             patch("safe_fetch.urlopen") as mock_open:

            def _during_connect(req, timeout=None):
                # Simulate attacker rebinding the *real* resolver mid-flight.
                mock_dns.side_effect = lambda *a, **k: rebind
                pinned = socket.getaddrinfo("feeds.example.com", 443)
                ips = {info[4][0] for info in pinned}
                assert ips == {"93.184.216.34"}, ips
                return resp

            mock_open.side_effect = _during_connect
            assert fetch_url("https://feeds.example.com/item") == b"body"
