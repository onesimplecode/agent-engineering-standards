# Worked Example: SSRF Allowlist + Redirect-Hop Re-check

`safe_fetch.py` is a **stdlib-only MIT reimplementation** of outbound-fetch
hygiene for agent and ingest pipelines that pull untrusted URLs (TR-SEC-005
open-world output). It is **not** a copy of any private package or AGPL
upstream — the *ideas* (host allowlist, fail-closed address checks, DNS pin,
re-validate every redirect) are what carry over.

## The pattern

| Step | What it does |
|---|---|
| Host allowlist | `ALLOWED_HOSTS` is co-located in the module; widening it is a code review |
| Address check | Every resolved IP must be public unicast; empty DNS fails closed |
| DNS pin | Resolve once, pin `socket.getaddrinfo` for that hostname during the hop |
| Redirect hops | No automatic follow; each `Location` is validated as a new URL |

```bash
# From the public repo root — unit tests (no network):
python3 -m pytest tests/test_ssrf_allowlist_example.py -q
```

## Honest residuals

- **DNS pin ≠ socket pin.** Connecting to the vetted IP while preserving
  `Host`/SNI (true IP-pinned TLS) is a harder, more fragile design. This
  example pins DNS so the stdlib client cannot re-resolve. Edge or sandbox
  runtimes that validate DNS but cannot pin the outbound socket still have a
  narrow resolve-vs-connect window — name that residual in the threat model
  instead of claiming full closure (same honesty bar as Impossible vs. Tedious).
- **Not thread-safe.** The pin monkeypatches process-global `getaddrinfo`.
  Use sequential fetches, or replace with a per-request transport that does
  not share global resolver state.
- **Allowlist is the primary barrier** against arbitrary SSRF; the address
  check and DNS pin are defense in depth against an allowlisted name that
  rebinds or against operator mistakes.

## Trace to standards artifacts

| Artifact | Location |
|---|---|
| External content / open-world fetch | `AGENTS.md` — "Outbound Fetch Hygiene" |
| Impossible vs. tedious | `AGENTS.md`, `templates/threat-model.md` |
| Co-located allowlist discipline | `AGENTS.md` — Guard Pattern (TR-SEC-010) |
| Comparative influences | `ATTRIBUTIONS.md` (private SSRF practice; WorldMonitor SECURITY notes — citation only) |
