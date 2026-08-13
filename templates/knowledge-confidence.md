# Knowledge Confidence Labels

Use this vocabulary when a system synthesizes **claims** from multiple sources
(topic pages, research briefs, compiled knowledge). It answers *"how strongly do
the notes support this claim?"* — not *"where did this passage come from?"*
(provenance / trust tags are a separate concern).

## Frozen labels

Keep tokens in English even when the surrounding page is another language — they
are machine-checkable identifiers, not prose.

| Label | Meaning |
|---|---|
| `confirmed` | Directly supported by authoritative evidence, or repeated high-quality evidence from independent sources |
| `source-backed` | One credible source, not independently confirmed |
| `contested` | Incompatible claims from credible sources that current evidence does not settle |
| `watchlist` | Weak, early, or possibly transient — worth rechecking |
| `saved-context` | Deliberately saved by the user; no claim about truth or importance |

## Contested claims

When sources disagree, record the disagreement under a contested section (or
equivalent) and label supporting lines `contested`. **Never resolve a contested
claim by recency alone** — a newer note does not overturn an older credible
source without independent corroboration.

## Independence

Do not treat translated halves of the same bilingual note, or duplicate
ingestions of one resource under different URLs, as independent corroboration.

## Related

- Registry: use with TR-AGT-006 (deterministic structure) and data-quality controls
  that are not permission boundaries (see operating model).
- Private dogfood: private-repo ADR-043 / write-path confidence labeling.
