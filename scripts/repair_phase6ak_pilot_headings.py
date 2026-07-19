#!/usr/bin/env python3
"""Curated, per-record H2 repair for the five held phase6ak pilots.

This is intentionally not a template rewrite.  Each list is a reviewed editorial
sequence for one record, and the command refuses a partial or unexpected change.
It never changes release, review, indexing, or advertising metadata.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


POSTS_DIR = Path("content/posts")

REPAIRS = {
    103: [
        "Why a staffing average cannot answer the weekend-care question",
        "Start with the same resident need on both sides of the comparison",
        "Reconcile weekday and weekend coverage in one evidence sheet",
        "Ask who owns a missed-shift escalation",
        "Sunday coverage remains unresolved after a reassuring tour",
        "Read CMS staffing fields as reported context, not a shift guarantee",
        "Hand the family a comparison record they can verify later",
        "What staffing data cannot establish about this resident's shift",
        "CMS staffing report used for the reconciliation",
        "If the facility answer conflicts with the public record",
        "Do not rank either home until the missing shift is explained",
    ],
    148: [
        "Why an inspection first screen is useful during discharge pressure",
        "Use a 20-minute inspection screen before making the first call",
        "Turn the public record into a discharge-triage card",
        "Read survey findings in chronological order before comparing homes",
        "Use cited concerns to prepare a visit rather than diagnose care",
        "Two calls that change the discharge conversation",
        "Verify the unresolved concern during the tour",
        "Give the discharge team a dated evidence note",
        "What an inspection record cannot tell you today",
        "Inspection timeline and correction records to verify",
        "Pause the shortlist when the timeline does not reconcile",
    ],
    179: [
        "Why a pending Medicaid answer needs a dependency map, not a promise",
        "Map the decision dependencies before accepting a conditional bed",
        "Call in an order that protects the pending application",
        "Separate facility participation from the person's eligibility result",
        "A bed offer arrives before the state decision",
        "Ask for facts that create a documented next step",
        "Keep the case record useful without turning it into benefits advice",
        "Eligibility decisions this map cannot make",
        "State Medicaid records needed for the pending follow-up",
        "Do not treat verbal assurance as an eligibility decision",
        "Next record to obtain before changing the care plan",
    ],
    204: [
        "Why resident fit belongs in the comparison before the score",
        "Write the resident-fit column before looking at a rank",
        "Use a two-home ledger that exposes the real tradeoff",
        "Convert public information into a tie-break question",
        "When the rating and the visit point in different directions",
        "Run a short second-opinion tour around the unresolved fit issue",
        "Share one decision record instead of competing family memories",
        "Information a shortlist cannot supply without the resident",
        "Public-data reference for the screening questions",
        "Keep both candidates until the fit question is answered",
        "What to bring to the final family decision",
    ],
    212: [
        "Why a meal observation needs a purpose before the dining room visit",
        "Set the observation purpose without pretending to inspect care",
        "Use a fifteen-minute dignity-and-support observation note",
        "Separate what you saw from what you need to ask",
        "A second tour after the first question went unanswered",
        "Turn a respectful observation into one answerable question",
        "Keep a private record that helps the resident and family",
        "Questions a dining-room visit leaves open",
        "Resident-rights source used for the observation boundary",
        "Request follow-up when observation and explanation diverge",
        "How to carry the unanswered question into the next visit",
    ],
}


def post_path(post_id: int) -> Path:
    paths = list(POSTS_DIR.glob(f"{post_id}-*.json"))
    if len(paths) != 1:
        raise RuntimeError(f"expected one post for {post_id}, found {len(paths)}")
    return paths[0]


def replace_h2(body: str, headings: list[str]) -> str:
    matches = list(re.finditer(r"(<h2[^>]*>)(.*?)(</h2>)", body, re.IGNORECASE | re.DOTALL))
    if len(matches) != len(headings):
        raise RuntimeError(f"expected {len(headings)} H2 elements, found {len(matches)}")
    pieces: list[str] = []
    cursor = 0
    for match, heading in zip(matches, headings, strict=True):
        pieces.append(body[cursor:match.start()])
        pieces.append(f"{match.group(1)}{heading}{match.group(3)}")
        cursor = match.end()
    pieces.append(body[cursor:])
    return "".join(pieces)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the curated headings")
    args = parser.parse_args()
    changes = []
    for post_id, headings in REPAIRS.items():
        path = post_path(post_id)
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("review_status") != "needs_human_review":
            raise RuntimeError(f"{post_id} is not held for human review")
        new_body = replace_h2(record["body_html"], headings)
        if new_body == record["body_html"]:
            raise RuntimeError(f"{post_id} produced no heading change")
        changes.append((path, record, new_body))
    if args.apply:
        for path, record, new_body in changes:
            record["body_html"] = new_body
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "applied" if args.apply else "checked", "records": [path.name for path, _, _ in changes]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
