"""Create a non-mutating consolidation plan for the held phase6ak matrix.

The plan preserves every source record and keeps all of them held.  It marks
one representative per repeated main-keyword family for an editorial contract
and identifies the suffix-only siblings that must be merged or replaced rather
than independently published.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "content" / "posts"

# These five were deliberately chosen and rewritten as the diversified dry run.
PILOT_IDS = {103, 148, 179, 204, 212}


def load_posts() -> list[dict]:
    rows = []
    for path in sorted(POST_DIR.glob("*.json")):
        post = json.loads(path.read_text(encoding="utf-8-sig"))
        if str(post.get("template_variation", "")).startswith("phase6ak-"):
            post["_path"] = str(path.relative_to(ROOT)).replace("\\", "/")
            rows.append(post)
    return rows


def candidate_for(group: list[dict]) -> dict:
    pilots = [post for post in group if post["id"] in PILOT_IDS]
    if len(pilots) > 1:
        raise ValueError(f"multiple pilot records in one keyword family: {[p['id'] for p in pilots]}")
    return pilots[0] if pilots else min(group, key=lambda post: post["id"])


def build_plan(posts: list[dict]) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for post in posts:
        groups[post["main_keyword"]].append(post)

    representatives = []
    merged = []
    for keyword, group in sorted(groups.items()):
        canonical = candidate_for(group)
        contract_complete = bool(canonical.get("editorial_contract")) and bool(
            canonical.get("research_evidence", {}).get("fact_traceability_pass")
        )
        representatives.append({
            "main_keyword": keyword,
            "id": canonical["id"],
            "slug": canonical["slug"],
            "source_path": canonical["_path"],
            "editorial_status": "needs_human_review" if contract_complete else "needs_contract",
            "publication_status": "held",
            "reason": "One representative is retained because its reader decision must be made distinct before publication.",
        })
        for post in sorted(group, key=lambda item: item["id"]):
            if post["id"] == canonical["id"]:
                continue
            merged.append({
                "id": post["id"],
                "slug": post["slug"],
                "source_path": post["_path"],
                "main_keyword": keyword,
                "merge_target_id": canonical["id"],
                "merge_target_slug": canonical["slug"],
                "editorial_status": "merge_or_recontract",
                "publication_status": "held",
                "reason": "Same main keyword with a suffix-only audience variant; no independent contract or distinct evidence path exists.",
            })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "held phase6ak records; non-mutating editorial consolidation only",
        "summary": {
            "source_records": len(posts),
            "main_keyword_families": len(representatives),
            "representatives_retained": len(representatives),
            "representatives_ready_for_human_review": sum(
                item["editorial_status"] == "needs_human_review" for item in representatives
            ),
            "suffix_variants_held_for_merge_or_recontract": len(merged),
            "publication_eligible": 0,
        },
        "representatives": representatives,
        "suffix_variants": merged,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a non-mutating phase6ak consolidation plan.")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    plan = build_plan(load_posts())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), **plan["summary"]}, indent=2))


if __name__ == "__main__":
    main()
