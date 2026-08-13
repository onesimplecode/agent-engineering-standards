# Threat Model: [Short Title]
Date: YYYY-MM-DD
Related ADR: ADR-NNNN

**Operationalizes:** the design-stage threat-modeling step (TR-SEC-008/009/010),
using the MITRE ATT&CK (https://attack.mitre.org/) and MITRE ATLAS
(https://atlas.mitre.org/) technique catalogs as shared vocabulary.

Attach this to any ADR that introduces a **new network listener, a new
credential or token, a new agent tool permission grant, or a new external
content source**. If none of those apply, skip this assessment and say so in
the ADR. Keep it short — a completed model should fit on one screen; the value
is in forcing the questions, not in exhaustiveness.

## Scope

What feature, pipeline, or infrastructure change is being modeled?

## Trust Boundaries Crossed

Enumerate every boundary this change creates or crosses. Common ones:

- [ ] Network: new listener, new outbound destination
- [ ] Credential: new secret introduced — where stored, what scope, what rotation (TR-SEC-008)
- [ ] Agent: new tool grant or allowlist entry — what can a prompt-injected session now do unprompted (TR-SEC-010)
- [ ] Content: new untrusted input source — RAG, scrape, upload, webhook (TR-SEC-005)
- [ ] Data: PII or private data flowing to a new component (TR-SEC-003 routing)

## Data Classification

- **Data touched:** [describe]
- **Classification:** [Public | Internal | PII/Private]
- **If PII/Private:** local-only routing confirmed in implementation? (TR-SEC-003)

## Applicable Techniques

List only techniques a real attacker could plausibly use against *this*
change — 2 to 5 rows is typical. Cite ATT&CK T-IDs for classic TTPs and ATLAS
AML.T-IDs for AI-specific ones (prompt injection, model/data poisoning,
extraction).

| Technique (ID + name) | Attack path through this change | Mitigation | TR-ID / pattern | Status |
|---|---|---|---|---|
| | | | | |

## Impossible vs. Tedious

For each mitigation listed above, classify it — *does it make the attack
impossible, or just tedious?* Agentic attackers have unlimited patience and
near-zero per-attempt cost, so friction-only controls (rate limits, extra
pivot hops, obscurity) buy time but do not stop them.

| Mitigation | Barrier (removes the capability) or Friction (raises cost only) | If friction: what is the real backstop? |
|---|---|---|
| | | |

Prefer a control that removes a capability over one that throttles it (no
listener over a firewalled one; short-lived tokens over rotated static keys;
a type that has no PII methods over a runtime check). A friction-class
mitigation is acceptable only when its backstop is named.

## Read-boundary vs. topic-avoidance

Do not confuse two different meanings of "ignore":

| Intent | What it is | Threat-model role |
|---|---|---|
| **Read boundary** | The agent *cannot* read a path or corpus (ACL, mount scope, tool deny) | Security control — reduces blast radius under prompt injection (TR-SEC-010 / least agency) |
| **Topic avoidance** | The agent *should not write about* a theme (style guide, editorial deny-list) | Content policy — not a security boundary; a prompt-injected session can still see the material if it is readable |

An ignore file or deny-list that only steers writing is **not** a substitute for
removing read access. Cite this distinction when a design proposes "ignore X"
as a mitigation — say which meaning is intended. (Observation: many knowledge
systems discuss ignore lists; this template does not require shipping one.)

## Unmitigated Residuals

Anything above with Status ≠ done: tag `LUMIA-DEBT: <description> [TR-ID]` in
the affected file, or note a `POC-EXCEPTION` with the tier-graduation
condition.

## Review Trigger

When should this model be revisited? (tier graduation, new deployment
environment, new data source, or the next governance review, TR-GOV-006)
