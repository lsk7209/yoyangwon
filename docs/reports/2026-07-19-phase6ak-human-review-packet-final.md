# Caregos phase6ak final human-review packet

## Review scope

- 23 retained representatives: individually rewritten, source-backed, and validator-passing.
- 92 suffix-only variants: held for merge or a genuinely new contract; not review candidates for publication.
- Public release remains disabled. No record in this packet has been approved by automation.

## Reviewer decision

For each retained representative, record one of: `approve`, `return_for_rewrite`, or `reject/merge`. Approval means the reviewer has checked source use, reader usefulness, non-overlap, headline/claim accuracy, and current-policy caveats. Do not approve based solely on a validator pass.

## Evidence to inspect

1. `docs/reports/2026-07-19-phase6ak-editorial-contract-audit.json` — 23 contract-complete human-review candidates; zero automatically eligible records.
2. `docs/reports/2026-07-19-phase6ak-consolidation-plan.json` — one retained representative for each of 23 main-keyword families and 92 held variants.
3. `scripts/validate_article_quality.py` — full run passes with 100 approved baseline posts and 115 held posts.
4. `scripts/test_review_gate.py` and `scripts/test_apply_adsense_review_hold.py` — five containment tests pass.

## Retained review IDs

`101, 103, 104, 105, 106, 107, 108, 109, 111, 113, 114, 115, 116, 117, 118, 119, 121, 122, 123, 148, 179, 204, 212`

## Release invariant

Only a named reviewer may run the confirmation-gated approval command for one selected record at a time. Until then every listed record remains `needs_human_review`, absent from public output, noindexed, and ad-blocked.
