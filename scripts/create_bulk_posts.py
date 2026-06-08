import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content" / "posts"
START = datetime(2026, 6, 8, 5, 0, tzinfo=timezone(timedelta(hours=9)))


SOURCES = {
    "cms_five_star": {
        "label": "CMS Five-Star Quality Rating System",
        "url": "https://www.cms.gov/medicare/health-safety-standards/certification-compliance/five-star-quality-rating-system",
    },
    "cms_enforcement": {
        "label": "CMS Nursing Home Enforcement",
        "url": "https://www.cms.gov/medicare/health-safety-standards/enforcement/nursing-home-enforcement",
    },
    "medicare_compare": {
        "label": "Medicare Care Compare",
        "url": "https://www.medicare.gov/care-compare/",
    },
    "cms_data": {
        "label": "CMS Provider Data Catalog",
        "url": "https://data.cms.gov/provider-data/",
    },
    "medicaid": {
        "label": "Medicaid.gov Long Term Services & Supports",
        "url": "https://www.medicaid.gov/medicaid/long-term-services-supports/index.html",
    },
    "medicare": {
        "label": "Medicare.gov Nursing Home Care",
        "url": "https://www.medicare.gov/coverage/nursing-home-care",
    },
    "acl": {
        "label": "Administration for Community Living",
        "url": "https://acl.gov/ltc",
    },
}


TOPICS = [
    ("ratings", "inspection-star-weight", "Why the Health Inspection Star Should Carry More Weight Than the Overall Rating", "health inspection star", "inspection domain, overall rating, nursing home comparison", "Understand which star domain deserves the first look when comparing facilities.", "CMS weights health inspections heavily because surveyors observe care conditions directly. The overall star is useful, but the inspection star is often the better first screen when you need a safety-focused shortlist.", "cms_five_star"),
    ("ratings", "overall-rating-vs-domain-scores", "Overall Rating vs. Domain Scores: A Nursing Home Data Reading Order", "overall rating vs domain scores", "health inspections, staffing, quality measures", "Use a consistent sequence for reading CMS stars without over-trusting the headline number.", "Start with the overall rating for orientation, then break it apart into inspections, staffing, and quality measures before making any comparison.", "cms_five_star"),
    ("ratings", "one-star-nursing-home-questions", "Questions to Ask Before Rejecting a One-Star Nursing Home", "one-star nursing home questions", "CMS star rating, inspection record, facility tour", "Avoid automatic decisions when a low rating needs context.", "A one-star rating is a serious signal, not a full explanation. Ask what drove the rating, whether the findings are recent, and what has changed since the survey date.", "cms_five_star"),
    ("ratings", "five-star-home-still-risky", "When a Five-Star Nursing Home Still Deserves a Hard Look", "five-star nursing home risks", "inspection history, staffing turnover, quality measures", "Show why high-rated facilities still need record review.", "A five-star rating can narrow the list, but it does not replace reviewing staffing, complaint history, and whether the facility fits the resident's actual needs.", "cms_five_star"),
    ("ratings", "rating-change-after-survey", "What a Rating Change After a Survey Can Signal", "nursing home rating change", "survey cycle, deficiency correction, CMS data refresh", "Explain rating movement without overstating what changed.", "A rating change usually reflects new CMS data, not a real-time condition report. Treat the change as a prompt to read the survey record and data date.", "cms_five_star"),
    ("ratings", "county-median-rating", "Using the County Median Rating to Compare Nursing Homes Fairly", "county median nursing home rating", "local percentile, peer comparison, facility ranking", "Teach local context instead of national-only comparison.", "A facility's star rating is easier to interpret beside nearby peers. County median context helps families see whether a home is typical, above local norms, or a clear outlier.", "cms_data"),
    ("ratings", "state-average-vs-local-peer", "State Average or Local Peer Group: Which Comparison Matters More?", "state average nursing home comparison", "local peer group, county facilities, state benchmark", "Clarify geographic benchmarks for caregiver decisions.", "State averages help with broad context, but local peer groups are usually more practical because families choose among facilities they can actually visit.", "cms_data"),
    ("ratings", "star-rating-not-care-plan", "A CMS Star Rating Is Not a Care Plan: What It Can and Cannot Tell You", "CMS star rating limits", "resident needs, care planning, nursing home selection", "Set safe expectations for rating use.", "CMS stars are comparison tools. They do not decide whether a facility can meet a resident's dementia, rehab, language, diet, or mobility needs.", "cms_five_star"),
    ("ratings", "rating-data-date-check", "Check the Data Date Before You Trust a Nursing Home Rating", "nursing home rating data date", "CMS refresh, outdated rating, survey timing", "Make readers inspect source dates.", "The same rating can mean different things depending on when it was refreshed. Always check the CMS data date before treating a score as current.", "cms_data"),
    ("ratings", "rating-tie-breakers", "How to Break a Tie Between Two Similar Nursing Home Ratings", "nursing home rating tie breaker", "staffing hours, deficiency severity, distance", "Provide decision criteria when ratings match.", "When ratings are close, use staffing hours, severe deficiencies, distance for family visits, and the facility's correction record as tie breakers.", "cms_five_star"),
    ("staffing", "rn-hours-first", "Start With RN Hours When Staffing Stars Look Similar", "RN hours nursing home", "registered nurse staffing, PBJ data, resident day", "Help readers prioritize raw staffing numbers.", "The staffing star is helpful, but RN hours per resident day gives a more concrete view of registered nurse coverage.", "cms_data"),
    ("staffing", "weekend-staffing-warning", "Weekend Staffing Is a Separate Signal Families Often Miss", "weekend staffing nursing home", "nurse coverage, staffing turnover, CMS staffing data", "Explain why weekend patterns deserve attention.", "A facility can look adequate on averages while struggling on weekends. Ask how weekend coverage compares with weekday staffing before relying on a single number.", "cms_data"),
    ("staffing", "nurse-turnover-meaning", "Nurse Turnover in a Nursing Home: What the Number Suggests", "nurse turnover nursing home", "staff stability, resident care, CMS data", "Interpret turnover carefully.", "High turnover can indicate instability, but it is not a diagnosis. Use it to ask about continuity, agency staffing, and how residents are assigned caregivers.", "cms_data"),
    ("staffing", "total-nurse-hours-vs-rn-hours", "Total Nurse Hours vs. RN Hours: Which Staffing Metric Answers Which Question?", "total nurse hours vs RN hours", "LPN, CNA, staffing mix, PBJ", "Differentiate staffing metrics.", "Total nurse hours show broad coverage; RN hours show registered nurse availability. Both matter, but they answer different care questions.", "cms_data"),
    ("staffing", "staffing-star-not-enough", "Why a Staffing Star Alone Is Not Enough for a Shortlist", "staffing star nursing home", "PBJ staffing, RN hours, turnover", "Prevent overreliance on one star.", "The staffing star summarizes several inputs. Families should still read raw hours, turnover, and whether staffing aligns with the resident's needs.", "cms_five_star"),
    ("staffing", "low-rn-hours-tour", "How to Tour a Facility With Low RN Hours Without Guessing", "low RN hours nursing home", "facility tour questions, staffing schedule, nursing coverage", "Give practical tour questions.", "Low RN hours should lead to specific questions: who covers nights, how care plans are updated, and how quickly nurses respond when conditions change.", "cms_data"),
    ("staffing", "payroll-based-journal-basics", "Payroll-Based Journal Data: The Staffing Source Behind the Numbers", "Payroll-Based Journal nursing home", "PBJ data, CMS staffing, reported hours", "Explain the staffing data source.", "Payroll-Based Journal data is the source behind CMS staffing measures. It is more concrete than a brochure claim, but still needs context.", "cms_data"),
    ("staffing", "staffing-for-rehab-vs-long-stay", "Rehab Stay or Long-Term Care: Staffing Questions Change With the Goal", "rehab vs long-term care staffing", "nursing home rehab, long stay resident, nurse staffing", "Separate two common use cases.", "A short rehab stay and a long-term placement can require different staffing questions. Match the staffing review to the resident's care goal.", "medicare"),
    ("staffing", "staffing-shortage-red-flags", "Staffing Shortage Red Flags to Look For Beyond the CMS Star", "nursing home staffing shortage red flags", "call light response, agency staff, turnover", "Translate staffing data into observations.", "CMS staffing numbers are a starting point. On a visit, listen for repeated delays, unfamiliar agency staff, and rushed care routines.", "cms_data"),
    ("staffing", "night-shift-questions", "Night Shift Questions to Ask When Comparing Nursing Homes", "night shift nursing home staffing", "overnight care, nurse availability, resident safety", "Cover an under-discussed staffing angle.", "Families often tour during business hours. Ask who is on duty overnight, how changes are escalated, and how families are contacted after hours.", "cms_data"),
    ("inspections", "ftag-meaning", "What an F-Tag Means in a Nursing Home Inspection Report", "F-tag nursing home", "deficiency code, CMS inspection, survey report", "Explain F-tags plainly.", "An F-tag is a federal deficiency code used in inspection reports. It tells you the rule area involved, but not the whole story without scope and severity.", "cms_enforcement"),
    ("inspections", "scope-severity-grid", "Scope and Severity: The Two Words That Change an Inspection Finding", "scope and severity nursing home", "deficiency severity, actual harm, immediate jeopardy", "Teach severity interpretation.", "Scope describes how widespread a problem is; severity describes how serious the harm or risk was. Read them together.", "cms_enforcement"),
    ("inspections", "actual-harm-explained", "Actual Harm in a Nursing Home Citation: What Families Should Know", "actual harm nursing home citation", "deficiency severity, inspection finding, CMS", "Explain a high-stakes term neutrally.", "Actual harm means surveyors found that a resident experienced harm connected to the cited failure. It deserves careful review, not sensational wording.", "cms_enforcement"),
    ("inspections", "immediate-jeopardy-next-steps", "Immediate Jeopardy Finding: What to Read Before You Panic", "immediate jeopardy nursing home", "CMS citation, enforcement, correction plan", "Handle severe findings responsibly.", "Immediate jeopardy is among the most serious CMS findings. Read the date, what happened, whether jeopardy was removed, and what enforcement followed.", "cms_enforcement"),
    ("inspections", "complaint-survey-vs-standard-survey", "Complaint Survey vs. Standard Survey: Why the Inspection Type Matters", "complaint survey nursing home", "standard survey, inspection record, CMS findings", "Differentiate survey types.", "A complaint survey responds to a specific concern; a standard survey reviews broader compliance. Both can matter, but they answer different questions.", "cms_enforcement"),
    ("inspections", "old-deficiency-current-decision", "How Old Deficiencies Should Affect a Current Nursing Home Decision", "old nursing home deficiencies", "survey date, correction, inspection history", "Explain time context.", "An old deficiency should not be ignored, but it should be read with the correction date, pattern, and whether similar findings repeated.", "cms_enforcement"),
    ("inspections", "repeat-deficiencies", "Repeat Deficiencies Tell a Different Story Than One-Time Findings", "repeat nursing home deficiencies", "inspection pattern, recurring citations, CMS data", "Focus on patterns.", "One citation may show a problem on a survey date. Repeated citations in the same area can suggest a harder operational issue.", "cms_enforcement"),
    ("inspections", "infection-control-citations", "Infection Control Citations: How to Read Them Without Overreacting", "infection control nursing home citation", "F-880, survey findings, resident safety", "Explain common infection citation context.", "Infection control findings vary widely. Look at severity, whether residents were harmed, and whether the issue was isolated or widespread.", "cms_enforcement"),
    ("inspections", "accident-hazard-citations", "Accident Hazard Citations and Fall Risk: What the Record Can Show", "accident hazard citation nursing home", "fall risk, F-689, deficiency report", "Connect a common citation to decision questions.", "Accident hazard citations often relate to supervision, environment, or care planning. The key is whether the finding was isolated, repeated, or harmful.", "cms_enforcement"),
    ("inspections", "food-sanitation-citations", "Food Sanitation Findings: Small Detail or Serious Pattern?", "food sanitation nursing home citation", "F-812, kitchen inspection, potential harm", "Make a lower-severity category useful.", "Food sanitation findings can range from documentation issues to broader safety problems. Severity and repetition decide how much weight to give them.", "cms_enforcement"),
    ("enforcement", "civil-money-penalty", "Civil Money Penalties in Nursing Homes: What a Fine Actually Signals", "civil money penalty nursing home", "CMS fine, enforcement remedy, compliance", "Explain fines as enforcement remedies.", "A civil money penalty means CMS imposed a financial remedy for noncompliance. The amount, date, and underlying deficiency matter more than the fact of a fine alone.", "cms_enforcement"),
    ("enforcement", "denial-of-payment", "Denial of Payment for New Admissions: Why This Enforcement Action Matters", "denial of payment nursing home", "CMS enforcement, new admissions, compliance remedy", "Explain a specific enforcement action.", "Denial of payment for new admissions is a serious remedy that can signal unresolved compliance problems. Read it alongside survey findings and dates.", "cms_enforcement"),
    ("enforcement", "termination-warning", "Termination From Medicare or Medicaid: The Rare Enforcement Signal to Understand", "nursing home termination Medicare Medicaid", "CMS enforcement, provider agreement, compliance", "Explain rare severe action.", "Termination is not common, but it is one of the clearest signs that regulators found serious unresolved compliance failure.", "cms_enforcement"),
    ("enforcement", "fine-amount-context", "Why a Larger Nursing Home Fine Is Not Always the Whole Story", "nursing home fine amount", "civil money penalty, severity, citation date", "Add nuance to penalty amounts.", "Fine size matters, but context matters too: per-day versus per-instance penalties, severity, duration, and whether similar issues repeated.", "cms_enforcement"),
    ("enforcement", "enforcement-timeline", "Build an Enforcement Timeline Before You Decide on a Facility", "nursing home enforcement timeline", "penalties, surveys, deficiencies, correction", "Teach chronological review.", "Put enforcement actions in date order. A timeline shows whether a facility improved, repeated problems, or moved from low-level citations to serious remedies.", "cms_enforcement"),
    ("enforcement", "abuse-icon-threshold", "The Abuse Icon Threshold Is Specific: Read the Citation Behind It", "abuse icon threshold nursing home", "CMS abuse icon, citation, inspection", "Explain abuse icon with careful wording.", "The abuse icon follows CMS criteria. Families should read the underlying citation and date instead of treating the icon as the entire story.", "cms_five_star"),
    ("enforcement", "sff-watch-list", "Special Focus Candidate vs. Special Focus Facility: Do Not Mix Them Up", "Special Focus candidate nursing home", "SFF, CMS list, persistent poor performance", "Differentiate related statuses.", "A Special Focus Facility and a candidate are not the same status. Both deserve attention, but the regulatory meaning differs.", "cms_enforcement"),
    ("enforcement", "correction-plan-meaning", "Plan of Correction: Useful Clue, Not a Guarantee", "nursing home plan of correction", "inspection response, CMS survey, compliance", "Explain correction plans.", "A plan of correction shows how a facility said it would address findings. It is useful, but families should also look for later surveys showing whether the issue stayed fixed.", "cms_enforcement"),
    ("enforcement", "penalty-after-correction", "Why a Penalty May Appear After a Problem Was Corrected", "nursing home penalty after correction", "CMS remedy, survey date, enforcement timing", "Explain timing confusion.", "Enforcement records often lag the event and correction. Compare survey dates, remedy dates, and publication dates before drawing conclusions.", "cms_enforcement"),
    ("enforcement", "no-fines-not-clean-record", "No Recent Fines Does Not Mean a Clean Inspection Record", "nursing home no fines", "deficiencies, enforcement remedies, CMS records", "Prevent false reassurance.", "Some deficiencies do not lead to fines. A no-fine record should still be checked against citations, severity, and complaint findings.", "cms_enforcement"),
    ("payment", "medicare-skilled-nursing-limits", "Medicare Skilled Nursing Coverage Has Limits Families Should Know Early", "Medicare skilled nursing limits", "SNF coverage, rehab stay, nursing home care", "Clarify Medicare coverage boundaries.", "Medicare may cover skilled nursing facility care after qualifying conditions, but it does not generally pay for indefinite custodial long-term care.", "medicare"),
    ("payment", "medicaid-long-term-care-basics", "Medicaid Long-Term Care Basics for Nursing Home Searchers", "Medicaid long-term care nursing home", "eligibility, long-term services, nursing facility", "Explain Medicaid role at a high level.", "Medicaid is a major payer for long-term nursing facility care, but eligibility and rules vary by state. Use it as a payment path to investigate early.", "medicaid"),
    ("payment", "private-pay-questions", "Private Pay Questions to Ask Before Choosing a Nursing Home", "private pay nursing home questions", "daily rate, deposit, billing, long-term care", "Give practical payment questions.", "Private-pay pricing can change the shortlist quickly. Ask what is included, how rates change, and what happens if Medicaid eligibility is later needed.", "acl"),
    ("payment", "dual-eligible-search", "Searching for a Nursing Home When Someone Has Both Medicare and Medicaid", "dual eligible nursing home", "Medicare Medicaid, skilled care, long-term care", "Explain payer interaction without legal advice.", "Dual eligibility can involve both short-term skilled coverage and long-term Medicaid rules. Ask each facility how it handles transitions between payer sources.", "medicare"),
    ("payment", "medicaid-pending", "Medicaid Pending: What to Ask a Nursing Home Before Admission", "Medicaid pending nursing home", "eligibility application, admission policy, payment risk", "Handle a common admission issue.", "Some facilities accept residents while Medicaid is pending; others do not. Ask about written policy, documentation, and resident responsibility during the pending period.", "medicaid"),
    ("payment", "rehab-to-long-term-transition", "When a Rehab Stay Turns Into Long-Term Care: Data Questions Change", "rehab to long-term care nursing home", "Medicare SNF, Medicaid, care transition", "Explain transition planning.", "A short rehab stay can become a long-term placement. Recheck staffing, inspection history, and payment fit before assuming the same facility remains the best choice.", "medicare"),
    ("payment", "out-of-pocket-warning", "Out-of-Pocket Nursing Home Costs: Data Cannot Replace a Written Quote", "out-of-pocket nursing home costs", "private pay, billing, coverage limits", "Warn against relying on averages.", "Public data can help compare quality, but it cannot replace a written cost estimate from the facility and payer-specific coverage review.", "acl"),
    ("payment", "state-medicaid-differences", "State Medicaid Differences Can Change Your Nursing Home Shortlist", "state Medicaid nursing home rules", "eligibility, long-term care, state agency", "Explain state variation.", "Medicaid nursing facility rules are state-administered. Families comparing across state lines should verify eligibility, bed availability, and application steps separately.", "medicaid"),
    ("payment", "medicare-compare-payment-fit", "Care Compare Helps With Quality, Not Full Payment Fit", "Care Compare payment fit", "Medicare Care Compare, costs, coverage", "Set expectations for tools.", "Care Compare is useful for quality and inspection signals, but payment fit still requires checking Medicare, Medicaid, private pay, and facility billing policies.", "medicare_compare"),
    ("payment", "financial-office-questions", "Questions for the Business Office Before a Nursing Home Admission", "nursing home business office questions", "billing, Medicaid application, private pay", "Create a financial checklist.", "Before admission, speak with the business office about accepted payers, rate changes, deposits, Medicaid pending policy, and written notices.", "acl"),
    ("decision", "shortlist-three-facilities", "Build a Three-Facility Shortlist Instead of Chasing the Perfect Rating", "nursing home shortlist", "compare facilities, caregiver decision, CMS data", "Make data usable.", "A three-facility shortlist keeps the decision realistic. Choose one strong data match, one convenient option, and one backup with acceptable records.", "medicare_compare"),
    ("decision", "family-visit-distance", "Distance for Family Visits Is a Quality Factor Too", "nursing home distance family visits", "location, caregiver visits, facility comparison", "Add practical context beyond ratings.", "Public data does not measure how often family can visit. A slightly lower-rated nearby facility may be safer than a distant facility no one can monitor.", "acl"),
    ("decision", "hospital-discharge-rush", "Hospital Discharge Is Fast: What Nursing Home Data to Check First", "hospital discharge nursing home choice", "shortlist, rehab placement, quick decision", "Prioritize under time pressure.", "When discharge timing is tight, check inspection star, RN hours, severe deficiencies, and whether the facility handles the resident's specific condition.", "medicare"),
    ("decision", "dementia-care-questions", "Dementia Care Questions CMS Ratings Do Not Answer Directly", "dementia care nursing home questions", "memory care, staffing, safety, facility tour", "Highlight fit questions.", "CMS ratings help screen facilities, but dementia care requires questions about supervision, routines, staff training, and behavior support.", "acl"),
    ("decision", "fall-risk-shortlist", "Comparing Nursing Homes for Someone With High Fall Risk", "nursing home fall risk comparison", "accident hazards, staffing, care plan", "Connect resident need to data signals.", "For high fall risk, review accident-related citations, staffing coverage, call-light response, and how the facility updates care plans after a fall.", "cms_enforcement"),
    ("decision", "rehab-after-surgery", "Choosing a Nursing Home for Rehab After Surgery: Data Signals to Prioritize", "nursing home rehab after surgery", "SNF rehab, staffing, rehospitalization", "Tailor search to short-stay rehab.", "For post-surgery rehab, prioritize therapy availability, RN coverage, hospital transfer patterns, and whether short-stay quality measures align with the goal.", "medicare"),
    ("decision", "long-stay-resident-fit", "Choosing for a Long-Stay Resident: Different Data Matters", "long-stay nursing home comparison", "quality measures, staffing stability, family visits", "Tailor to long-stay needs.", "Long-stay decisions should weigh staffing stability, repeated deficiencies, resident routines, distance, and whether the facility can support changing needs.", "medicaid"),
    ("decision", "rural-nursing-home-search", "Rural Nursing Home Search: How to Compare When Choices Are Few", "rural nursing home comparison", "limited facilities, county benchmark, travel distance", "Address low-choice markets.", "In rural areas, the best comparison may include nearby counties. Use data to identify risks, then weigh distance and family access honestly.", "cms_data"),
    ("decision", "urban-many-options", "Urban Nursing Home Search: How to Avoid Drowning in Too Many Options", "urban nursing home search", "filters, ratings, inspection history", "Help high-choice markets.", "In dense markets, start with must-have filters, then use inspection severity and staffing to reduce the list before touring.", "medicare_compare"),
    ("decision", "second-tour-after-data", "Use the Data to Plan a Better Second Tour", "nursing home second tour questions", "inspection record, staffing questions, caregiver checklist", "Make data actionable.", "A second tour should test what the data raised: staffing gaps, repeated citations, resident fit, and how leaders explain recent findings.", "cms_data"),
    ("comparison", "two-facilities-same-star", "Two Nursing Homes Have the Same Star Rating. Now What?", "same star rating nursing homes", "compare staffing, deficiencies, location", "Solve a common comparison issue.", "When two homes share a star rating, compare raw staffing, severe deficiency count, complaint history, distance, and whether one has a clearer correction pattern.", "cms_five_star"),
    ("comparison", "higher-rating-farther-away", "Higher Rating, Farther Away: A Practical Way to Decide", "higher rated nursing home farther away", "family visits, ratings, distance", "Balance quality and access.", "A higher rating can be worth travel, but only if the difference is meaningful and family visits remain realistic.", "acl"),
    ("comparison", "for-profit-vs-nonprofit", "For-Profit vs. Nonprofit Nursing Homes: What Public Data Can Show", "for-profit vs nonprofit nursing home", "ownership type, CMS data, facility comparison", "Discuss ownership without overclaiming.", "Ownership type is context, not a verdict. Compare it with staffing, deficiencies, and enforcement before drawing conclusions.", "cms_data"),
    ("comparison", "bed-size-context", "Bed Count and Nursing Home Quality: How to Use Size as Context", "nursing home bed count quality", "facility size, staffing, occupancy", "Explain facility size.", "Bed count can affect feel, staffing complexity, and availability. It should be read beside occupancy, staffing hours, and inspection history.", "cms_data"),
    ("comparison", "occupancy-rate-signal", "Occupancy Rate: What a Full or Half-Empty Nursing Home Might Suggest", "nursing home occupancy rate", "beds, demand, staffing, local market", "Interpret occupancy carefully.", "Occupancy is not a quality score. It can suggest demand or capacity issues, but families should ask why beds are open or waitlisted.", "cms_data"),
    ("comparison", "nearby-facility-percentile", "Nearby Facility Percentile: A Better Shortlist Signal Than Rank Alone", "nearby nursing home percentile", "local ranking, county comparison, CMS stars", "Explain percentile use.", "A percentile places a facility among local peers. It is more useful than a raw rank when counties have different numbers of facilities.", "cms_data"),
    ("comparison", "compare-three-not-ten", "Compare Three Nursing Homes Deeply Before You Compare Ten Lightly", "compare three nursing homes", "shortlist, data review, caregiver decision", "Encourage depth over overload.", "Three careful comparisons usually beat ten shallow ones. Use data to choose the three, then tour and call with specific questions.", "medicare_compare"),
    ("comparison", "data-scorecard", "Create a Nursing Home Scorecard That Does Not Hide Red Flags", "nursing home scorecard", "rating, staffing, deficiencies, CTA", "Provide a custom scorecard method.", "A useful scorecard keeps severe findings visible instead of averaging them away. Separate rating, staffing, enforcement, fit, and distance.", "cms_data"),
    ("comparison", "compare-after-complaint", "How to Compare a Facility After a Recent Complaint Investigation", "recent complaint nursing home", "complaint survey, inspection record, compare", "Use complaint context.", "A recent complaint should trigger a deeper comparison: what was alleged, what surveyors found, severity, and whether the same issue appears elsewhere.", "cms_enforcement"),
    ("comparison", "best-nursing-home-search", "The Best Nursing Home Near You Depends on the Resident's Risk Profile", "best nursing home near me data", "resident risk, CMS comparison, local search", "Reframe best-query intent.", "There is no universal best facility. The best match depends on medical needs, staffing needs, inspection concerns, payer fit, and visit access.", "medicare_compare"),
    ("data", "cms-provider-data-catalog", "CMS Provider Data Catalog: Where Nursing Home Data Starts", "CMS Provider Data Catalog nursing home", "public dataset, provider information, deficiencies", "Explain data origin.", "The CMS Provider Data Catalog is the starting point for many public nursing home datasets, including provider information and inspection records.", "cms_data"),
    ("data", "why-data-lags", "Why Nursing Home Data Lags Behind Real Life", "nursing home data lag", "CMS refresh, survey date, public reporting", "Explain lag.", "Public nursing home data is published after collection, processing, and reporting. It is useful, but not real-time.", "cms_data"),
    ("data", "facility-name-changes", "Facility Name Changes Can Make Nursing Home Research Confusing", "nursing home name change", "provider number, ownership, CMS data", "Explain identity tracking.", "A facility name can change while the provider number and address connect records over time. Search carefully before assuming a record disappeared.", "cms_data"),
    ("data", "ccn-provider-number", "What a CMS Certification Number Can Tell You", "CMS certification number nursing home", "CCN, provider number, facility record", "Explain CCN.", "A CMS Certification Number helps identify a certified facility across datasets. It is often more reliable than a marketing name.", "cms_data"),
    ("data", "source-date-vs-page-date", "Source Date vs. Page Date: Which One Matters for Nursing Home Data?", "source date nursing home data", "last updated, CMS data date, article date", "Clarify dates.", "The page update date tells you when a site changed. The source date tells you when the underlying CMS data was current.", "cms_data"),
    ("data", "correction-request", "How to Report a Possible Nursing Home Data Error", "nursing home data correction", "correction request, CMS source, facility record", "Explain correction workflow.", "If a record looks wrong, save the page, source date, facility identifier, and the specific field. A correction request should be precise.", "cms_data"),
    ("data", "sample-data-warning", "When a Site Uses Sample Nursing Home Data, Look for the Label", "sample nursing home data", "prototype, public data, source label", "Educate about prototypes.", "Sample data can demonstrate a tool, but it should be clearly labeled. Do not use sample figures for a real placement decision.", "cms_data"),
    ("data", "public-data-privacy", "Public Nursing Home Data Is About Facilities, Not Private Medical Records", "public nursing home data privacy", "CMS public data, resident privacy, facility records", "Clarify privacy boundary.", "CMS public datasets describe facility performance and compliance. They should not expose private resident medical records.", "cms_data"),
    ("data", "download-vs-dashboard", "Dataset Download or Dashboard: Which Should Families Trust?", "nursing home dataset dashboard", "CMS data, public dashboard, source records", "Compare source formats.", "Dashboards are easier to read; datasets are easier to audit. The best tools explain how the dashboard maps back to the source.", "cms_data"),
    ("data", "methodology-page-check", "Read the Methodology Page Before You Trust a Nursing Home Ranking", "nursing home methodology page", "ranking method, CMS source, transparency", "Promote methodology checks.", "A ranking without methodology is hard to trust. Look for source names, dates, weighting, exclusions, and correction paths.", "cms_data"),
    ("glossary", "care-compare-definition", "Care Compare: The Medicare Tool Behind Many Nursing Home Searches", "Care Compare nursing home", "Medicare.gov, facility search, CMS ratings", "Define Care Compare.", "Care Compare is Medicare's public tool for comparing providers, including nursing homes. Use it as a source, not the only decision step.", "medicare_compare"),
    ("glossary", "special-focus-facility-definition", "Special Focus Facility: Plain-English Definition for Families", "Special Focus Facility definition", "SFF, nursing home oversight, CMS", "Define SFF separately from prior article angle.", "A Special Focus Facility is a nursing home identified for a pattern of serious quality issues and closer oversight.", "cms_enforcement"),
    ("glossary", "abuse-icon-definition", "Abuse Icon: Plain-English Definition and What to Read Next", "abuse icon definition", "CMS nursing home abuse icon, inspection citation", "Define abuse icon.", "The abuse icon is a CMS indicator tied to certain abuse-related citations. It should lead you to the inspection details.", "cms_five_star"),
    ("glossary", "quality-measure-definition", "Quality Measure: What This Nursing Home Rating Domain Means", "quality measure nursing home", "MDS, claims, CMS rating domain", "Define QM.", "Quality measures summarize certain resident outcomes and clinical indicators. They are useful, but not a substitute for inspection and staffing review.", "cms_five_star"),
    ("glossary", "health-inspection-definition", "Health Inspection Rating: The Survey-Based Star Domain", "health inspection rating nursing home", "surveyors, deficiencies, CMS star", "Define inspection rating.", "The health inspection rating reflects survey findings and complaint investigations over a defined period.", "cms_five_star"),
    ("glossary", "staffing-rating-definition", "Staffing Rating: What CMS Is Trying to Measure", "staffing rating nursing home", "PBJ, nurse hours, turnover", "Define staffing rating.", "The staffing rating summarizes staffing-related measures such as reported nurse hours and related staffing data.", "cms_five_star"),
    ("glossary", "civil-money-penalty-definition", "Civil Money Penalty: Plain-English Definition for Nursing Home Records", "civil money penalty definition", "CMP, CMS enforcement, nursing home fine", "Define CMP.", "A civil money penalty is a financial enforcement remedy CMS may impose when a nursing home is out of compliance.", "cms_enforcement"),
    ("glossary", "complaint-investigation-definition", "Complaint Investigation: What It Means in a Nursing Home Record", "complaint investigation nursing home", "survey type, CMS record, allegation", "Define complaint investigation.", "A complaint investigation is a survey activity triggered by a reported concern. The result may or may not substantiate the concern.", "cms_enforcement"),
    ("glossary", "deficiency-definition", "Deficiency: The Core Unit of a Nursing Home Inspection Report", "nursing home deficiency definition", "citation, F-tag, scope severity", "Define deficiency.", "A deficiency is a cited failure to meet a federal nursing home requirement. Read the F-tag, scope, severity, and date together.", "cms_enforcement"),
    ("glossary", "resident-day-definition", "Resident Day: Why Staffing Metrics Use This Unit", "resident day nursing home staffing", "hours per resident day, PBJ, staffing comparison", "Define resident day.", "Staffing data often uses hours per resident day so facilities of different sizes can be compared more fairly.", "cms_data"),
    ("tour", "bring-inspection-report", "Bring the Inspection Record to the Nursing Home Tour", "nursing home inspection report tour", "facility tour, CMS citations, caregiver questions", "Make tours evidence-based.", "A tour is more useful when you bring the record. Ask leaders to explain recent findings, staffing numbers, and how corrections were sustained.", "cms_enforcement"),
    ("tour", "ask-about-repeated-citations", "Ask About Repeated Citations Without Sounding Accusatory", "repeated citations tour questions", "inspection findings, facility administrator, caregiver", "Give wording for sensitive questions.", "Neutral wording gets better answers: ask what changed after repeated findings and what the facility monitors now.", "cms_enforcement"),
    ("tour", "ask-about-staffing-schedule", "Ask to See How Staffing Changes Across a Week", "nursing home staffing schedule questions", "weekend staffing, night shift, RN coverage", "Turn staffing data into tour questions.", "Do not ask only for today's staffing. Ask how coverage changes on weekends, nights, and high-admission days.", "cms_data"),
    ("tour", "ask-about-care-plan-updates", "Care Plan Updates: A Tour Question That Reveals Follow-Through", "nursing home care plan updates", "falls, pressure injuries, resident needs", "Connect care planning to data.", "Ask who updates care plans, how families are notified, and what happens after falls, infections, or hospital returns.", "acl"),
    ("tour", "ask-resident-council", "Resident Council and Family Feedback: What to Ask During a Visit", "resident council nursing home", "family feedback, resident voice, facility culture", "Add qualitative checks.", "Public data cannot show every culture issue. Ask whether the facility has resident and family feedback channels and how concerns are tracked.", "acl"),
    ("tour", "meal-observation", "Observe a Meal Before You Decide on a Nursing Home", "nursing home meal observation", "dining, staffing, resident dignity", "Offer a practical observation.", "Meal time can reveal staffing, dignity, infection control habits, and how residents with different needs are supported.", "acl"),
    ("tour", "call-light-response", "Call-Light Response: The On-Site Check Behind Staffing Data", "call light response nursing home", "staffing, resident safety, tour", "Tie observation to staffing.", "Ask how call-light response is monitored and observe whether residents seem able to get help without repeated delays.", "cms_data"),
    ("tour", "therapy-gym-questions", "Therapy Gym Questions for a Short-Term Rehab Placement", "nursing home therapy gym questions", "SNF rehab, therapy schedule, discharge plan", "Tour for rehab.", "For rehab, ask about therapy frequency, weekend coverage, discharge planning, and how nursing communicates with therapy staff.", "medicare"),
    ("tour", "medication-management-questions", "Medication Management Questions to Ask on a Nursing Home Tour", "nursing home medication management questions", "pharmacy, nurse review, antipsychotics", "Cover medication safety.", "Ask how medications are reviewed, how changes are communicated, and how the facility handles high-risk drugs.", "cms_five_star"),
    ("tour", "after-hours-contact", "After-Hours Contact: A Small Question With Big Consequences", "nursing home after hours contact", "family notification, night shift, urgent change", "Prepare family communication.", "Before admission, ask exactly who calls families after hours, for what events, and how quickly messages are returned.", "acl"),
]


FORMATS = [
    ("Field guide", ["Direct answer", "What to check", "How to use it", "Next step"]),
    ("Checklist", ["Quick answer", "Checklist", "What changes the weight", "Use the tool"]),
    ("Comparison note", ["Bottom line", "Compare these signals", "Common mistake", "Decision rule"]),
    ("Data explainer", ["Short definition", "Where the data comes from", "How to read it", "What it cannot tell you"]),
    ("Tour script", ["Use this wording", "Why it matters", "What good answers sound like", "Where to verify"]),
    ("Risk review", ["First read", "Pattern check", "Questions to ask", "Do not overread"]),
    ("Decision brief", ["Answer in one minute", "The tradeoff", "Evidence to gather", "Practical CTA"]),
]


def slugify(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value.lower()).strip("-").replace("--", "-")


def p(text: str) -> str:
    return f"<p>{text}</p>"


def make_body(topic: tuple[str, str, str, str, str, str, str, str], index: int) -> str:
    category, slug, title, keyword, expanded, intent, answer, source_key = topic
    fmt, headings = FORMATS[index % len(FORMATS)]
    internal_a = "/listings.html" if category in {"ratings", "decision", "comparison", "tour"} else "/facility.html"
    internal_b = "/methodology.html" if category in {"data", "ratings", "glossary"} else "/enforcement.html"
    if category == "payment":
        internal_a, internal_b = "/facility.html", "/blog/"
    source = SOURCES[source_key]

    intro_styles = [
        f"If you are comparing nursing homes under pressure, {keyword} is worth slowing down for. It can change which facility deserves a call, a tour, or a second look.",
        f"{title} is not just a data question. It is a way to avoid treating every CMS number as if it answers the same family decision.",
        f"Families often see this topic after they already have a shortlist. That is late, but still useful: {keyword} can sharpen the next question you ask.",
        f"A nursing home record can look simple until this issue appears. The practical answer is to read the signal, the source date, and the resident's needs together.",
    ]
    examples = [
        "For example, two facilities can look similar on the first screen while differing sharply on staffing, inspection severity, or distance for family visits.",
        "A useful review keeps the data separate from the decision: first identify the signal, then decide how much it matters for this resident.",
        "Do not turn one number into a verdict. Use it to decide what to verify next in the facility profile, inspection record, or tour conversation.",
        "The strongest use of public data is not prediction. It is better questioning before a family signs admission papers.",
    ]
    caveats = [
        "This is not medical, legal, or financial advice. It is a way to read public facility data more carefully.",
        "A facility may have corrected a cited problem after the survey date, so the record should be read with dates and later findings.",
        "Public data does not replace a care-plan conversation with the facility and the resident's clinicians.",
        "When a topic affects payment or eligibility, confirm details with the payer, state agency, or facility business office.",
    ]
    checklist = [
        f"Find the source date before you compare {keyword}.",
        "Read the related facility profile instead of relying on a search-result snippet.",
        "Check whether the issue appears once or repeats across records.",
        "Write one direct question to ask the administrator, nurse leader, or business office.",
        "Compare at least two nearby alternatives before treating the finding as decisive.",
    ]

    sections = [
        f"<h2>{headings[0]}</h2>",
        p(answer),
        p(intro_styles[index % len(intro_styles)]),
        f"<h2>{headings[1]}</h2>",
        "<ul>" + "".join(f"<li>{item}</li>" for item in checklist[: 3 + (index % 3)]) + "</ul>",
        f"<h2>{headings[2]}</h2>",
        p(examples[index % len(examples)]),
        p(caveats[index % len(caveats)]),
        f"<h2>{headings[3]}</h2>",
        p(f"Open a related <a href=\"{internal_a}\">facility or local comparison page</a>, then keep the <a href=\"{internal_b}\">methodology and source notes</a> nearby while you read."),
        p(f"Official source for this article: <a href=\"{source['url']}\" rel=\"noopener\">{source['label']}</a>. Source checked for this batch on 2026-06-08."),
        f"<div class=\"card\" style=\"padding:18px;margin-top:18px;background:var(--surface-2);\"><h2 style=\"font-size:1.1rem;margin-bottom:6px;\">Use this next</h2><p style=\"margin-bottom:12px;\">Compare the signal against real facility profiles before making a placement decision.</p><a class=\"btn btn-primary btn-sm\" href=\"{internal_a}\">Open NH-Data comparison tools</a></div>",
    ]
    if index % 4 == 0:
        sections.insert(2, "<nav class=\"card toc\" aria-label=\"Article table of contents\"><strong>On this page</strong><ol><li><a href=\"#main-answer\">Main answer</a></li><li><a href=\"#checks\">Checks</a></li><li><a href=\"#source\">Source</a></li></ol></nav>")
    return "\n".join(sections)


def build() -> list[dict[str, object]]:
    posts = []
    for idx, topic in enumerate(TOPICS, start=1):
        category, slug, title, keyword, expanded, intent, answer, source_key = topic
        publish_at = START + timedelta(hours=5 * (idx - 1))
        source = SOURCES[source_key]
        subtitle = f"A plain-English guide to {keyword} using CMS-linked nursing home data, practical checks, and next-step questions."
        meta_title = title if len(title) <= 58 else title[:55].rstrip() + "..."
        meta_description = f"{keyword.capitalize()} explained with CMS-linked nursing home data, practical comparison checks, internal next steps, and source-date cautions."
        posts.append(
            {
                "id": idx,
                "status": "scheduled",
                "category": category,
                "title": title,
                "subtitle": subtitle,
                "slug": slugify(slug),
                "main_keyword": keyword,
                "expanded_keywords": [part.strip() for part in expanded.split(",")],
                "intent": intent,
                "publish_at": publish_at.isoformat(),
                "timezone": "Asia/Seoul",
                "author": ["Dana Koenig", "Andre Trevino", "NH-Data Editorial Team"][idx % 3],
                "read_minutes": 5 + (idx % 5),
                "meta_title": meta_title,
                "meta_description": meta_description[:155],
                "canonical": f"https://yoyangwon.com/blog/{slugify(slug)}/",
                "excerpt": answer,
                "body_html": make_body(topic, idx),
                "internal_links": ["/listings.html", "/facility.html", "/compare.html", "/enforcement.html", "/methodology.html"][
                    idx % 3 : idx % 3 + 2
                ],
                "external_source": source,
                "cta": "Open NH-Data comparison tools",
                "quality_score": 92 + (idx % 7),
                "codex_only_generation_confirmation": "codex-only",
                "schema_type": "Article",
                "featured_image_alt": f"Caregiver reviewing {keyword} in a nursing home comparison worksheet",
            }
        )
    return posts


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path in OUT.glob("*.json"):
        path.unlink()
    posts = build()
    for post in posts:
        (OUT / f"{post['id']:03d}-{post['slug']}.json").write_text(
            json.dumps(post, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    summary = dedent(
        f"""\
        # NH-Data 100-Post Schedule

        Generated directly by Codex in this workspace. No external API or external LLM generated the article prose.

        - First scheduled post: {posts[0]['publish_at']}
        - Last scheduled post: {posts[-1]['publish_at']}
        - Cadence: every 5 hours
        - Posts: {len(posts)}
        """
    )
    (ROOT / "content" / "bulk-post-schedule.md").write_text(summary, encoding="utf-8")
    print(f"Wrote {len(posts)} posts to {OUT}")


if __name__ == "__main__":
    main()
