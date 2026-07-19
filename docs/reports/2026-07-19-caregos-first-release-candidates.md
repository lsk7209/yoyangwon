# Caregos first-release candidate order

## Decision

Use a three-record, low-volume release sequence after real editorial approval. Do not approve, deploy, index, serve ads, or run a scheduler from this document.

| Order | ID | Why this is the first candidate | Required human check |
| --- | --- | --- | --- |
| 1 | 204 — two-facility shortlist review | A resident-fit decision ledger; it frames public data as a screening input, has a clear non-advice boundary, and is less likely to be misread as a coverage determination. | Verify the resident-fit framing, tour questions, sources, and that no facility-specific inference is asserted. |
| 2 | 212 — meal-support observation | A dignity-first observation protocol with explicit limits on what a visit can prove. | Verify respectful wording, privacy boundary, and that observation is not represented as a clinical audit. |
| 3 | 103 — weekday/weekend RN-hours comparison | A staffing reconciliation worksheet with published-data limits and a concrete unresolved-shift decision rule. | Verify staffing-field interpretation, reported-data caveat, and no claim about a specific shift. |

## Per-record production sequence

1. A named editor independently chooses `approve`, `return_for_rewrite`, or `reject/merge` in the final review packet.
2. If approved, run the confirmation-gated approval command for that ID only.
3. Generate the static output locally and verify the one URL is indexable only after approval, has intended ad markup, canonical, and sitemap/RSS inclusion.
4. Deploy only that coherent, approved change set; recheck public HTML after cache propagation.
5. Stop immediately if public source attribution, indexing, ad markup, or content rendering differs from the approved local record.

## Explicitly excluded

- All 92 suffix-only variants remain held.
- Medicare, Medicaid, private-pay, and therapy-discharge candidates are not in the first release group because their individual reader decisions have higher benefits/payment or care-transition sensitivity.
- No Knewstory or Certifi scheduler setting is changed by this sequence.
