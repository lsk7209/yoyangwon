"""Create a fail-closed editorial-contract audit for held phase6ak records.

This tool does not rewrite, approve, publish, or schedule content.  It makes
the repeated topic/audience matrix explicit so an editor must give each record
its own evidence plan and non-overlap claim before any prose is changed.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "content" / "posts"


def load_phase6ak_posts() -> list[dict]:
    posts = []
    for path in sorted(POST_DIR.glob("*.json")):
        post = json.loads(path.read_text(encoding="utf-8-sig"))
        if str(post.get("template_variation", "")).startswith("phase6ak-"):
            post["_path"] = str(path.relative_to(ROOT)).replace("\\", "/")
            posts.append(post)
    return posts


def reader_situation(slug: str) -> str:
    marker = "-for-"
    if marker not in slug:
        return "unclassified"
    return slug.split(marker, 1)[1]


def contract_row(post: dict, sibling_slugs: list[str]) -> dict:
    status = post.get("review_status", "needs_editorial_contract")
    rewritten = bool(post.get("rewrite_evidence"))
    contract = post.get("editorial_contract", {})
    research = post.get("research_evidence", {})
    contract_fields = {
        "reader_job", "decision_moment", "answer_claim", "evidence_plan",
        "non_overlap_claim", "structure_reason",
    }
    contract_complete = contract_fields.issubset(contract) and bool(research.get("fact_traceability_pass"))
    return {
        "id": post["id"],
        "slug": post["slug"],
        "source_path": post["_path"],
        "category": post.get("category"),
        "main_keyword": post.get("main_keyword"),
        "expanded_keywords": post.get("expanded_keywords", []),
        "reader_situation": reader_situation(post["slug"]),
        "current_review_status": status,
        "current_template_variation": post.get("template_variation"),
        "rewritten_before_contract_audit": rewritten,
        "sibling_slugs_same_main_keyword": sibling_slugs,
        "editorial_status": "needs_human_review" if contract_complete else "needs_contract",
        "required_before_rewrite": [] if contract_complete else [
            "reader_job",
            "decision_moment",
            "answer_claim",
            "evidence_plan",
            "non_overlap_claim",
            "structure_reason",
            "five_to_eight_source_research_packet",
        ],
        "release_eligibility": "held",
        "reason": (
            "This keyword has repeated audience variants. It cannot be rewritten or approved "
            "from a shared prose skeleton; an editor must prove its separate decision and evidence path."
        ),
    }


def build_audit(posts: list[dict]) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for post in posts:
        groups[str(post.get("main_keyword", ""))].append(post)

    records = []
    group_summary = []
    for keyword, grouped in sorted(groups.items()):
        slugs = sorted(post["slug"] for post in grouped)
        group_summary.append({
            "main_keyword": keyword,
            "record_count": len(grouped),
            "reader_situations": sorted({reader_situation(post["slug"]) for post in grouped}),
            "contract_gate": "required",
        })
        for post in grouped:
            siblings = [slug for slug in slugs if slug != post["slug"]]
            records.append(contract_row(post, siblings))

    completed_contracts = sum(row["editorial_status"] == "needs_human_review" for row in records)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "held phase6ak records only",
        "record_count": len(records),
        "main_keyword_groups": group_summary,
        "summary": {
            "requires_individual_contract": len(records),
            "contract_complete_human_review_pending": completed_contracts,
            "eligible_for_approval": 0,
            "eligible_for_publication": 0,
            "shared_template_rewrite_prohibited": True,
        },
        "records": sorted(records, key=lambda row: row["id"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit held phase6ak records without modifying them.")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    audit = build_audit(load_phase6ak_posts())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), **audit["summary"]}, indent=2))


if __name__ == "__main__":
    main()
