# Phase6ak editorial repair: five-record dry run

## Decision

The 115 held records are a `23 topic x 5 reader-suffix` matrix. A suffix alone
does not create an independent reader decision or evidence path. Do not repair
this corpus by applying a shared article body to every record.

The first five rewrites must be completed as distinct editorial transactions,
then compared for repeated openings, heading sequences, source interpretation,
visual element sequence, FAQ pattern, and closing CTA before another group is
started. Every non-selected suffix variant stays held and must be merged,
re-contracted, or rejected before drafting.

## Pilot contracts

### 1. `phase6ak-health-inspection-first-screen-for-hospital-discharge-pressure`

- Reader decision: a hospital-discharge family must decide today whether a
  facility merits a call, a visit, or removal from the short list.
- Claim: a recent inspection record is a triage signal, not a safety verdict;
  read the citation topic, scope, severity, date, and documented correction
  before comparing it with a second candidate.
- Structure: time-boxed decision tree with a red-flag branch and a
  visit-question branch.
- Required sources: Medicare health-inspections explanation, overall-star
  explanation, Nursing Home Checklist, CMS Provider Data Catalog, and the
  relevant facility record.
- Non-overlap: it does not explain staffing averages, payment coverage, or a
  general tour script.

### 2. `phase6ak-medicaid-application-timeline-for-medicaid-pending-searches`

- Reader decision: a family with a pending application must decide which
  state-specific questions to ask before accepting an admission offer.
- Claim: no national processing timeline, income rule, or document list is
  safe to promise; confirm the state's nursing-facility eligibility and level
  of-care rules, the facility's Medicaid participation, and the current
  application status.
- Structure: dependency map from application state to facility participation,
  coverage scope, and escalation route.
- Required sources: Medicaid institutional nursing-facilities guidance,
  Medicaid state-agency contact guidance, Medicare Care Compare, the selected
  state Medicaid agency, and the facility admissions policy.
- Non-overlap: it does not answer Medicare SNF benefit-day coverage or give
  legal/eligibility advice.

### 3. `phase6ak-rn-hours-weekday-weekend-for-families-choosing-this-week`

- Reader decision: a family whose weekday tour looked reassuring must decide
  how to test night/weekend coverage before ranking two facilities.
- Claim: RN/staffing averages describe reported measures, not a guarantee of
  the staffing on one shift; reconcile the latest comparable CMS data with a
  shift-specific call and observation record.
- Structure: two-column evidence-reconciliation worksheet.
- Required sources: Medicare staffing explanation, CMS Five-Star guide,
  Five-Star Technical Users' Guide, Provider Data Catalog, Nursing Home
  Checklist, and each candidate facility profile.
- Non-overlap: it does not turn a staffing measure into an inspection finding
  or a resident-specific clinical recommendation.

### 4. `phase6ak-two-facility-shortlist-review-for-second-opinion-tours`

- Reader decision: after two visits, a family must choose what to verify next
  when public scores and personal observations point in different directions.
- Claim: use resident-fit non-negotiables first; use public-record differences
  only as tie-breakers that create a documented follow-up question.
- Structure: weighted comparison ledger with a tie-break rule.
- Required sources: Medicare Care Compare overview, Nursing Home Checklist,
  current records for both named candidates, and any state inspection records.
- Non-overlap: it does not duplicate a first-tour checklist or a generic
  star-rating explanation.

### 5. `phase6ak-meal-support-observation-for-second-opinion-tours`

- Reader decision: a family returning for a second tour must decide what a
  15-minute meal observation can and cannot establish about dignity, support,
  and escalation questions.
- Claim: record observable facts and ask for the responsible role/process;
  do not infer a clinical diagnosis, neglect finding, or facility-wide quality
  conclusion from one meal.
- Structure: annotated field-observation checklist followed by an escalation
  path.
- Required sources: CMS resident-rights and nutrition guidance, Medicare
  Nursing Home Checklist, relevant state survey resources, and the facility's
  current resident-rights materials.
- Non-overlap: it does not repeat the generic comparison or staffing article.

## Prohibited claims in every rewrite

- Do not label an individual facility safe or unsafe from a public record.
- Do not treat a complaint count as proof of abuse or a citation as a current
  condition without its date and correction context.
- Do not infer a particular shift's staffing from an average measure.
- Do not promise a universal Medicaid timeline, eligibility outcome, or
  document set.
- Do not describe Medicare's 100-day SNF maximum as 100 free days.
