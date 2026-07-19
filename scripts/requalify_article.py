import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "content" / "posts"


def find_post(slug: str) -> Path:
    matches = []
    for path in POST_DIR.glob("*.json"):
        post = json.loads(path.read_text(encoding="utf-8-sig"))
        if post.get("slug") == slug:
            matches.append(path)
    if len(matches) != 1:
        raise SystemExit(f"expected one post for slug {slug!r}, found {len(matches)}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Approve exactly one Caregos article after its independent quality gate passes.")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--reviewer", required=True, help="Named editorial reviewer; recorded in the article manifest.")
    parser.add_argument(
        "--confirm-human-review",
        required=True,
        choices=["HUMAN_REVIEWED"],
        help="Deliberate approval gate; machine validation alone must not publish an article.",
    )
    args = parser.parse_args()
    path = find_post(args.slug)
    before = path.read_bytes()
    command = [sys.executable, str(ROOT / "scripts" / "validate_article_quality.py"), "--slug", args.slug]
    validation = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if validation.returncode:
        print(validation.stdout, end="")
        print(validation.stderr, end="", file=sys.stderr)
        raise SystemExit("article remains held: individual quality validation failed")
    post = json.loads(before.decode("utf-8-sig"))
    if post.get("review_status") == "approved":
        raise SystemExit("refusing to overwrite an already approved record")
    post["review_status"] = "approved"
    post["reviewed_by"] = args.reviewer
    post["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    post["review_validation"] = {"command": "validate_article_quality.py --slug", "content_sha256_before_approval": hashlib.sha256(before).hexdigest()}
    path.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "approved", "slug": args.slug, "path": str(path), "validation": json.loads(validation.stdout)}, indent=2))


if __name__ == "__main__":
    main()
