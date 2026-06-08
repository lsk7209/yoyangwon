import json
import re
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "content" / "posts"


def shingles(value: str) -> set[str]:
    text = re.sub(r"<[^>]+>", " ", value.lower())
    tokens = [w for w in re.findall(r"[a-z][a-z0-9-]{2,}", text) if w not in STOP]
    return {" ".join(tokens[i : i + 5]) for i in range(max(0, len(tokens) - 4))}


STOP = {
    "this", "that", "with", "from", "when", "what", "should", "facility", "nursing",
    "home", "homes", "data", "public", "source", "families", "article", "official",
    "compare", "record", "records", "decision", "question", "questions", "signal",
}


def h2_signature(body: str) -> tuple[str, ...]:
    return tuple(re.findall(r"<h2[^>]*>(.*?)</h2>", body))


def word_count(body: str) -> int:
    text = re.sub(r"<[^>]+>", " ", body)
    return len(re.findall(r"[A-Za-z]+", text))


def color_count(body: str) -> int:
    return body.count("var(--clay)") + body.count("var(--teal") + body.count("var(--ink-soft)")


def main() -> None:
    posts = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(POST_DIR.glob("*.json"))]
    errors = []
    if len(posts) != 100:
        errors.append(f"expected 100 posts, found {len(posts)}")

    seen_h2 = {}
    for post in posts:
        body = post["body_html"]
        title = post["title"].casefold()
        subtitle = post["subtitle"].casefold()
        main_keyword = post["main_keyword"].casefold()
        expanded_keywords = [keyword.casefold() for keyword in post["expanded_keywords"]]
        h2s = h2_signature(body)
        if main_keyword not in title:
            errors.append(f"{post['slug']}: title missing main keyword")
        if not any(keyword in title for keyword in expanded_keywords):
            errors.append(f"{post['slug']}: title missing expanded keyword")
        if main_keyword not in subtitle:
            errors.append(f"{post['slug']}: subtitle missing main keyword")
        if not any(keyword in subtitle for keyword in expanded_keywords):
            errors.append(f"{post['slug']}: subtitle missing expanded keyword")
        if word_count(body) < 650:
            errors.append(f"{post['slug']}: body below 650 words")
        colors = color_count(body)
        if colors < 1 or colors > 2:
            errors.append(f"{post['slug']}: expected 1-2 color accents, found {colors}")
        if "direct-answer" not in body:
            errors.append(f"{post['slug']}: missing direct-answer block")
        if "trust-panel" not in body:
            errors.append(f"{post['slug']}: missing data limits/correction trust block")
        if "type-element" not in body:
            errors.append(f"{post['slug']}: missing category-specific article element")
        if "scenario-block" not in body:
            errors.append(f"{post['slug']}: missing real-world scenario block")
        if "Real-world scenario" not in body:
            errors.append(f"{post['slug']}: missing scenario heading")
        if "What this article cannot tell you" not in body:
            errors.append(f"{post['slug']}: missing limitation language")
        if "Correction path" not in body:
            errors.append(f"{post['slug']}: missing correction path")
        if len(h2s) < 4:
            errors.append(f"{post['slug']}: fewer than four H2 sections")
        if h2s in seen_h2:
            errors.append(f"{post['slug']}: repeated H2 signature with {seen_h2[h2s]}")
        seen_h2[h2s] = post["slug"]
        if body.count("<a href=") < 3:
            errors.append(f"{post['slug']}: fewer than three body links")
        if "Official source for this article" not in body:
            errors.append(f"{post['slug']}: missing source note")
        if "btn btn-primary" not in body:
            errors.append(f"{post['slug']}: missing CTA")
        if int(post.get("quality_score", 0)) < 90:
            errors.append(f"{post['slug']}: quality score below 90")

    vectors = [(post["slug"], shingles(post["body_html"])) for post in posts]
    worst = ("", "", 0.0)
    for (slug_a, a), (slug_b, b) in combinations(vectors, 2):
        if not a or not b:
            continue
        score = len(a & b) / len(a | b)
        if score > worst[2]:
            worst = (slug_a, slug_b, score)
        if score > 0.60:
            errors.append(f"{slug_a} and {slug_b}: repeated phrase similarity {score:.2f}")

    if errors:
        print(json.dumps({"status": "fail", "errors": errors[:30], "worst_similarity": worst}, indent=2))
        raise SystemExit(1)
    print(json.dumps({"status": "pass", "posts": len(posts), "worst_similarity": worst}, indent=2))


if __name__ == "__main__":
    main()
