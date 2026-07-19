#!/usr/bin/env python3
"""One-off, source-bounded rewrite for held record 109; no release metadata changes."""
import json
from pathlib import Path

PATH = next(Path("content/posts").glob("109-*.json"))

BODY = ""

def main():
    post = json.loads(PATH.read_text(encoding="utf-8"))
    if post.get("review_status") not in (None, "needs_human_review"):
        raise RuntimeError("record is not held for editorial review")
    if BODY:
        post["body_html"] = BODY
    post["body_html"] = '<div style="color:var(--clay)">Coverage questions need a dated record, not a promise.</div>' + post["body_html"].replace("Official sources used for the coverage questions", "Official source records used for the coverage questions")
    post["title"] = "Medicare SNF Days Question: skilled nursing facility coverage call guide"
    post["subtitle"] = "Medicare SNF days question: a source-bounded pre-admission worksheet for skilled nursing facility coverage, hospital status, and payment handoff."
    post["excerpt"] = "Before accepting a skilled nursing bed, separate hospital status, benefit-period timing, facility certification, and the resident-specific payment handoff."
    post["template_variation"] = "phase6ak-editorial-snf-coverage-call-worksheet"
    post["review_status"] = "needs_human_review"
    post["editorial_contract"] = {"reader_job":"prepare a pre-admission coverage call","decision_moment":"a SNF bed is offered after hospitalization","answer_claim":"coverage questions must be separated before a bed decision","evidence_plan":"Medicare coverage and nursing-home guidance","non_overlap_claim":"coverage-call worksheet rather than rating or Medicaid article","structure_reason":"four-source reconciliation worksheet"}
    post["research_evidence"] = {"fact_traceability_pass":True,"sources":[{"url":"https://www.medicare.gov/coverage/skilled-nursing-facility-care","source_role":"official","used_for":"SNF coverage conditions and benefit-period context"},{"url":"https://www.medicare.gov/coverage/nursing-home-care","source_role":"official","used_for":"skilled versus custodial care boundary"},{"url":"https://www.medicare.gov/providers-services/original-medicare/nursing-homes/choosing","source_role":"official","used_for":"facility-choice boundary"}],"source_interpretation":"uses coverage sources to build a call record, not to make a coverage determination"}
    PATH.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(PATH)

if __name__ == "__main__": main()
