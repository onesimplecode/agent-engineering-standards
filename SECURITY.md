# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest release tag | yes |
| main branch | best-effort |

## Reporting a Vulnerability

This public repository contains **standards, templates, and reference scripts only** — no
production services, credentials, or user data.

If you believe you have found a security issue:

1. **Do not** open a public issue for sensitive findings.
2. Email the maintainer via GitHub private security advisory (preferred) or the contact method
   listed on the maintainer's GitHub profile.
3. Include: affected file/path, impact, and minimal reproduction if applicable.

## Out of Scope

- Vulnerabilities in the maintainer's private applications not present in this repo.
- Theoretical attacks against example/synthetic content in `examples/worked-example/`.
- Social engineering or prompt-injection examples without a concrete flaw in shipped templates.

## Secret Scanning

Releases are validated with forbidden-path and secret-pattern checks before publication.
If you find a committed secret in this repo, report immediately — it should not be present.
