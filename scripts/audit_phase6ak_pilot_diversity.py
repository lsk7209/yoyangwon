#!/usr/bin/env python3
"""Write a non-mutating diversity audit for the five phase6ak pilot rewrites."""

from __future__ import annotations

import argparse
import html
import json
import re
from itertools import combinations
from pathlib import Path


PILOT_IDS = (103, 148, 179, 204, 212)
POSTS_DIR = Path("content/posts")
ROLE_WORDS = {
    "a", "an", "and", "as", "at", "before", "by", "cannot", "care", "correction", "data", "decision",
    "do", "for", "from", "home", "how", "in", "into", "is", "it", "not", "of", "official", "on",
    "or", "path", "question", "record", "resident", "scenario", "source", "the", "this", "to", "what",
    "when", "with", "you", "your",
}


def normalized_words(value: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", value.lower()) if word not in ROLE_WORDS}


def h2_signature(body_html: str) -> list[str]:
    headings = re.findall(r"<h2[^>]*>(.*?)</h2>", body_html, flags=re.IGNORECASE | re.DOTALL)
    return [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(item))).strip().lower() for item in headings]


def find_post(post_id: int) -> Path:
    matches = list(POSTS_DIR.glob(f"{post_id}-*.json"))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one post for {post_id}, found {len(matches)}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    records = []
    errors = []
    for post_id in PILOT_IDS:
        source = find_post(post_id)
        record = json.loads(source.read_text(encoding="utf-8"))
        contract = record.get("editorial_contract", {})
        research = record.get("research_evidence", {})
        required_contract = {"reader_job", "decision_moment", "answer_claim", "evidence_plan", "non_overlap_claim", "structure_reason"}
        missing_contract = sorted(key for key in required_contract if not contract.get(key))
        if record.get("review_status") != "needs_human_review":
            errors.append(f"{post_id}: review status is not needs_human_review")
        if missing_contract:
            errors.append(f"{post_id}: missing contract keys {', '.join(missing_contract)}")
        if not research.get("fact_traceability_pass"):
            errors.append(f"{post_id}: fact traceability is not passing")
        records.append({
            "id": post_id,
            "source_path": str(source).replace("\\", "/"),
            "main_keyword": record.get("main_keyword"),
            "template_variation": record.get("template_variation"),
            "h2_signature": h2_signature(record.get("body_html", "")),
            "status": record.get("review_status"),
        })

    pair_similarity = []
    for left, right in combinations(records, 2):
        left_words = normalized_words(" ".join(left["h2_signature"]))
        right_words = normalized_words(" ".join(right["h2_signature"]))
        union = left_words | right_words
        score = round(len(left_words & right_words) / len(union), 6) if union else 0.0
        pair_similarity.append({"left_id": left["id"], "right_id": right["id"], "h2_jaccard": score})

    max_pair_similarity = max((item["h2_jaccard"] for item in pair_similarity), default=0.0)
    h2_signatures_unique = len({tuple(item["h2_signature"]) for item in records}) == len(records)
    variations_unique = len({item["template_variation"] for item in records}) == len(records)
    keywords_unique = len({item["main_keyword"] for item in records}) == len(records)
    if not h2_signatures_unique:
        errors.append("pilot H2 signatures are not unique")
    if not variations_unique:
        errors.append("pilot template variations are not unique")
    if not keywords_unique:
        errors.append("pilot main keywords are not unique")
    if max_pair_similarity >= 0.15:
        errors.append(f"pilot H2 overlap too high: {max_pair_similarity}")

    output = {
        "scope": "five phase6ak pilot rewrites only; non-mutating audit",
        "pilot_ids": list(PILOT_IDS),
        "records": records,
        "pair_similarity": pair_similarity,
        "summary": {
            "max_h2_jaccard": max_pair_similarity,
            "h2_signatures_unique": h2_signatures_unique,
            "template_variations_unique": variations_unique,
            "main_keywords_unique": keywords_unique,
            "human_review_required": True,
            "publication_eligible": False,
            "status": "pass" if not errors else "fail",
            "errors": errors,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
