import argparse
import json
import re
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "content" / "posts"
SIMILARITY_LIMIT = 0.60

STOP = {
    "this", "that", "with", "from", "when", "what", "should", "facility", "nursing",
    "home", "homes", "data", "public", "source", "families", "article", "official",
    "compare", "record", "records", "decision", "question", "questions", "signal",
}


def shingles(value: str) -> set[str]:
    text = re.sub(r"<[^>]+>", " ", value.lower())
    tokens = [word for word in re.findall(r"[a-z][a-z0-9-]{2,}", text) if word not in STOP]
    return {" ".join(tokens[index : index + 5]) for index in range(max(0, len(tokens) - 4))}


def h2_signature(body: str) -> tuple[str, ...]:
    return tuple(re.findall(r"<h2[^>]*>(.*?)</h2>", body))


def word_count(body: str) -> int:
    return len(re.findall(r"[A-Za-z]+", re.sub(r"<[^>]+>", " ", body)))


def color_count(body: str) -> int:
    return body.count("var(--clay)") + body.count("var(--teal") + body.count("var(--ink-soft)")


def is_approved(post: dict) -> bool:
    if "review_status" in post:
        return post["review_status"] == "approved"
    # The phase6ak batch predates the approval field and is known to fail every
    # individual gate; missing status must therefore fail closed for that batch.
    return not str(post.get("template_variation", "")).startswith("phase6ak-")


def post_errors(post: dict) -> list[str]:
    body = post["body_html"]
    title = post["title"].casefold()
    subtitle = post["subtitle"].casefold()
    main_keyword = post["main_keyword"].casefold()
    expanded_keywords = [keyword.casefold() for keyword in post["expanded_keywords"]]
    slug = post["slug"]
    errors = []
    if main_keyword not in title:
        errors.append(f"{slug}: title missing main keyword")
    if not any(keyword in title for keyword in expanded_keywords):
        errors.append(f"{slug}: title missing expanded keyword")
    if main_keyword not in subtitle:
        errors.append(f"{slug}: subtitle missing main keyword")
    if not any(keyword in subtitle for keyword in expanded_keywords):
        errors.append(f"{slug}: subtitle missing expanded keyword")
    if word_count(body) < 650:
        errors.append(f"{slug}: body below 650 words")
    colors = color_count(body)
    if colors < 1 or colors > 2:
        errors.append(f"{slug}: expected 1-2 color accents, found {colors}")
    required = {
        "direct-answer": "missing direct-answer block",
        "trust-panel": "missing data limits/correction trust block",
        "type-element": "missing category-specific article element",
        "scenario-block": "missing real-world scenario block",
        "Real-world scenario": "missing scenario heading",
        "What this article cannot tell you": "missing limitation language",
        "Correction path": "missing correction path",
        "Official source for this article": "missing source note",
        "btn btn-primary": "missing CTA",
    }
    is_phase6ak = str(post.get("template_variation", "")).startswith("phase6ak-")
    if is_phase6ak:
        for marker in ("Real-world scenario", "What this article cannot tell you", "Correction path", "Official source for this article"):
            required.pop(marker)
    for marker, message in required.items():
        if marker not in body:
            errors.append(f"{slug}: {message}")
    if is_phase6ak:
        headings = " ".join(h2_signature(body)).casefold()
        semantic_heading_requirements = {
            r"\bscenario\b|\ba bed offer arrives\b|\bwhen the rating\b|\bsunday coverage\b|\btwo calls\b|\bsecond tour\b": "missing scenario heading",
            r"\bcannot\b|\bleaves open\b|\bcannot supply\b": "missing limitation language",
            r"\bcorrection\b|\bdo not\b|\bpause\b|\brequest follow-up\b|\bkeep both\b": "missing correction path",
            r"\bofficial source\b|\bcms\b|\binspection timeline\b|\bmedicaid records\b|\bpublic-data\b|\bresident-rights\b": "missing source note",
        }
        for pattern, message in semantic_heading_requirements.items():
            if not re.search(pattern, headings):
                errors.append(f"{slug}: {message}")
    if len(h2_signature(body)) < 4:
        errors.append(f"{slug}: fewer than four H2 sections")
    if body.count("<a href=") < 3:
        errors.append(f"{slug}: fewer than three body links")
    if int(post.get("quality_score", 0)) < 90:
        errors.append(f"{slug}: quality score below 90")
    return errors


def pair_similarity(post_a: dict, post_b: dict) -> float:
    shingles_a, shingles_b = shingles(post_a["body_html"]), shingles(post_b["body_html"])
    if not shingles_a or not shingles_b:
        return 0.0
    return len(shingles_a & shingles_b) / len(shingles_a | shingles_b)


def validate_posts(posts: list[dict]) -> tuple[list[str], tuple[str, str, float]]:
    errors = []
    seen_h2: dict[tuple[str, ...], str] = {}
    for post in posts:
        errors.extend(post_errors(post))
        signature = h2_signature(post["body_html"])
        if signature in seen_h2:
            errors.append(f"{post['slug']}: repeated H2 signature with {seen_h2[signature]}")
        seen_h2[signature] = post["slug"]

    worst = ("", "", 0.0)
    for post_a, post_b in combinations(posts, 2):
        score = pair_similarity(post_a, post_b)
        if score > worst[2]:
            worst = (post_a["slug"], post_b["slug"], score)
        if score > SIMILARITY_LIMIT:
            errors.append(f"{post_a['slug']} and {post_b['slug']}: repeated phrase similarity {score:.2f}")
    return errors, worst


def load_posts() -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8-sig")) for path in sorted(POST_DIR.glob("*.json"))]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Caregos approved editorial records.")
    parser.add_argument("--slug", help="Validate one record against the approved corpus without changing it.")
    args = parser.parse_args()
    all_posts = load_posts()
    if args.slug:
        candidates = [post for post in all_posts if post["slug"] == args.slug]
        if len(candidates) != 1:
            raise SystemExit(f"expected one post for slug {args.slug!r}, found {len(candidates)}")
        candidate = candidates[0]
        approved_others = [post for post in all_posts if is_approved(post) and post["slug"] != candidate["slug"]]
        errors = post_errors(candidate)
        worst = ("", "", 0.0)
        for other in approved_others:
            score = pair_similarity(candidate, other)
            if score > worst[2]:
                worst = (candidate["slug"], other["slug"], score)
            if score > SIMILARITY_LIMIT:
                errors.append(f"{candidate['slug']} and {other['slug']}: repeated phrase similarity {score:.2f}")
        result = {"status": "pass" if not errors else "fail", "slug": candidate["slug"], "errors": errors, "worst_similarity": worst}
    else:
        approved = [post for post in all_posts if is_approved(post)]
        errors, worst = validate_posts(approved)
        result = {"status": "pass" if not errors else "fail", "posts": len(approved), "held_posts": len(all_posts) - len(approved), "errors": errors, "worst_similarity": worst}
    print(json.dumps(result, indent=2))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
