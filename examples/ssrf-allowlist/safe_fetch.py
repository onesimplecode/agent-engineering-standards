"""Reference implementation: allowlisted outbound fetch with redirect-hop
re-check and DNS pin (TR-SEC-005 adjacent — open-world fetch hygiene).

MIT reimplementation of a pattern practiced in private shared SSRF packages
and observed in open OSINT proxies: never trust a URL just because the first
hop looked safe.

Contract:

1. **Host allowlist** — only reviewed hostnames may be fetched (exact match
   or a subdomain of an allowlisted registrable host).
2. **Fail-closed address check** — every resolved address must be public
   unicast; private/loopback/link-local/multicast/unspecified fail.
3. **DNS pin** — resolve once for validation, then pin ``socket.getaddrinfo``
   for that hostname for the single request so ``urllib`` cannot re-resolve
   (closes the classic resolve-then-connect DNS-rebinding TOCTOU for this
   sequential, stdlib path).
4. **Redirect hop re-check** — automatic redirects are refused; each
   ``Location`` is validated as a fresh URL (allowlist + resolve + pin)
   before the next hop.

Honest residuals (do not paper over):

- This is **DNS pinning**, not true IP/socket pinning (connect-to-IP while
  preserving Host/SNI). Runtimes that cannot pin the outbound socket to the
  vetted address still have a narrow resolve-vs-connect window — document it
  in the threat model rather than claiming closure.
- The ``getaddrinfo`` monkeypatch is **not thread-safe**; safe for sequential
  fetches only.
"""

from __future__ import annotations

import socket
from contextlib import contextmanager
from ipaddress import ip_address
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

# Reviewed outbound hosts for this worked example. Widening this set is a
# code review — same co-located-baseline discipline as TR-SEC-010 guards.
ALLOWED_HOSTS: frozenset[str] = frozenset(
    {
        "feeds.example.com",
        "cdn.example.com",
    }
)

_ALLOWED_SCHEMES = frozenset({"http", "https"})
_MAX_REDIRECTS_DEFAULT = 5


class SSRFError(ValueError):
    """Raised when a URL fails the allowlist, address, or redirect policy."""


def _is_unsafe_address(addr) -> bool:
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def host_is_allowlisted(hostname: str, allowed: frozenset[str] = ALLOWED_HOSTS) -> bool:
    """True if hostname is an exact allowlisted host or a subdomain of one."""
    host = hostname.lower().rstrip(".")
    if not host:
        return False
    for allowed_host in allowed:
        base = allowed_host.lower().rstrip(".")
        if host == base or host.endswith("." + base):
            return True
    return False


def _hostname_or_raise(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise SSRFError(f"scheme {parsed.scheme!r} not permitted for {url!r}")
    hostname = parsed.hostname or ""
    if not hostname:
        raise SSRFError(f"URL has no hostname: {url!r}")
    if not host_is_allowlisted(hostname):
        raise SSRFError(f"host {hostname!r} is not in ALLOWED_HOSTS")
    return hostname


def _resolve_and_validate(hostname: str) -> list:
    try:
        addr_infos = socket.getaddrinfo(hostname, None)
    except OSError as exc:
        raise SSRFError(f"DNS resolution failed for {hostname!r}: {exc}") from exc
    if not addr_infos:
        raise SSRFError(f"DNS resolution returned no addresses for {hostname!r}")
    for addr_info in addr_infos:
        ip_str = addr_info[4][0]
        try:
            addr = ip_address(ip_str)
        except ValueError:
            continue
        if _is_unsafe_address(addr):
            raise SSRFError(
                f"{hostname!r} resolves to private or reserved address {ip_str!r}"
            )
    return addr_infos


def validate_url(url: str) -> list:
    """Validate scheme, allowlist, and resolved addresses. Returns addrinfos."""
    hostname = _hostname_or_raise(url)
    return _resolve_and_validate(hostname)


def _reshape_for_request(addr_infos: list, port, family: int, type_: int) -> list:
    results = []
    for addr_family, addr_type, addr_proto, canonname, sockaddr in addr_infos:
        if family and addr_family != family:
            continue
        effective_type = type_ or addr_type or socket.SOCK_STREAM
        effective_port = port if port is not None else 0
        if addr_family == socket.AF_INET6:
            new_sockaddr = (sockaddr[0], effective_port, sockaddr[2], sockaddr[3])
        else:
            new_sockaddr = (sockaddr[0], effective_port)
        results.append((addr_family, effective_type, addr_proto, canonname, new_sockaddr))
    return results


@contextmanager
def _pinned_resolution(hostname: str, addr_infos: list):
    """Pin getaddrinfo(hostname, ...) to already-validated addresses.

    Not thread-safe (process-global monkeypatch). Sequential fetch only.
    """
    real_getaddrinfo = socket.getaddrinfo

    def _pinned(host, port=None, family=0, type=0, proto=0, flags=0):
        if host != hostname:
            return real_getaddrinfo(host, port, family, type, proto, flags)
        return _reshape_for_request(addr_infos, port, family, type)

    socket.getaddrinfo = _pinned
    try:
        yield
    finally:
        socket.getaddrinfo = real_getaddrinfo


def _one_hop(url: str, timeout: float) -> tuple[int, dict[str, str], bytes]:
    hostname = _hostname_or_raise(url)
    addr_infos = _resolve_and_validate(hostname)
    req = Request(url, method="GET")
    with _pinned_resolution(hostname, addr_infos):
        try:
            with urlopen(req, timeout=timeout) as resp:  # noqa: S310 — guarded above
                headers = {k.lower(): v for k, v in resp.headers.items()}
                return resp.getcode(), headers, resp.read()
        except HTTPError as exc:
            headers = {k.lower(): v for k, v in exc.headers.items()} if exc.headers else {}
            body = exc.read() if hasattr(exc, "read") else b""
            return exc.code, headers, body


def fetch_url(
    url: str,
    *,
    max_redirects: int = _MAX_REDIRECTS_DEFAULT,
    timeout: float = 10.0,
) -> bytes:
    """Fetch ``url`` with allowlist + address checks, DNS pin, and hop re-check.

    Raises ``SSRFError`` on policy failure, ``URLError`` on transport failure.
    """
    current = url
    for _ in range(max_redirects + 1):
        status, headers, body = _one_hop(current, timeout)
        if status in {301, 302, 303, 307, 308}:
            location = headers.get("location")
            if not location:
                raise SSRFError(f"redirect {status} from {current!r} with no Location")
            next_url = urljoin(current, location)
            # Re-validate every hop — do not inherit trust from the previous URL.
            validate_url(next_url)
            current = next_url
            continue
        if status >= 400:
            raise URLError(f"HTTP {status} for {current!r}")
        return body
    raise SSRFError(f"exceeded max_redirects={max_redirects} starting from {url!r}")
