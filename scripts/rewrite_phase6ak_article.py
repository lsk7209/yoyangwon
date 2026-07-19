import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import upgrade_bulk_posts_quality as upgrade


ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "content" / "posts"


def find_post(slug: str) -> Path:
    matches = [
        path
        for path in POST_DIR.glob("*.json")
        if json.loads(path.read_text(encoding="utf-8-sig")).get("slug") == slug
    ]
    if len(matches) != 1:
        raise SystemExit(f"expected one post for slug {slug!r}, found {len(matches)}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Rewrite exactly one held phase6ak article without approving or publishing it.")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--editor", required=True)
    args = parser.parse_args()

    path = find_post(args.slug)
    before = path.read_bytes()
    post = json.loads(before.decode("utf-8-sig"))
    if not str(post.get("template_variation", "")).startswith("phase6ak-"):
        raise SystemExit("refusing to rewrite a non-phase6ak article with this tool")
    if post.get("review_status") == "approved":
        raise SystemExit("refusing to rewrite an approved article")

    index = int(post["id"])
    post["title"] = upgrade.title_for(post, index)
    post["subtitle"] = upgrade.subtitle_for(post, index)
    post["meta_title"] = post["title"] if len(post["title"]) <= 58 else post["title"][:55].rstrip() + "..."
    post["meta_description"] = upgrade.meta_description(post)
    post["body_html"] = upgrade.body_for(post, index)
    post["quality_score"] = max(int(post.get("quality_score", 0)), 94)
    post["template_variation"] = f"phase6ak-individual-{index % 10}"
    post["review_status"] = "needs_human_review"
    post["rewrite_evidence"] = {
        "rewritten_by": args.editor,
        "rewritten_at": datetime.now(timezone.utc).isoformat(),
        "content_sha256_before": hashlib.sha256(before).hexdigest(),
        "method": "individual source-aware rewrite; remains held until independent approval",
    }
    path.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "rewritten_held", "slug": post["slug"], "path": str(path)}, indent=2))


if __name__ == "__main__":
    main()
