# Output Schema

Every intelligence report should contain:

1. **Scope** — brand, accounts, platforms, time window, and collection date.
2. **Executive conclusion** — the most useful answer in a few sentences.
3. **Evidence** — tables or findings with source URLs.
4. **Interpretation** — what the evidence may mean and confidence level.
5. **Actions** — prioritized, brand-safe recommendations or experiments.
6. **Limitations** — missing data, sampling bias, and unresolved questions.

For each post or comment record, prefer these fields:

```text
source_url | platform | account | published_at | collected_at | format |
topic | hook_or_quote | visible_metrics | evidence_type | confidence | notes
```
