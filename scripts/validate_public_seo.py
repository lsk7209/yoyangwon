import json
import os
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "content" / "posts"
BLOG_DIR = ROOT / "blog"
SITE_URL = "https://caregos.com"
CHECK_PUBLIC_TEXT = [BLOG_DIR, ROOT / "rss.xml", ROOT / "sitemap.xml"]


class PageAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.h1 = 0
        self.h2 = 0
        self.title = ""
        self.meta_description = False
        self.canonical = ""
        self.img_without_alt: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1 += 1
        if tag == "h2":
            self.h2 += 1
        if tag == "meta" and values.get("name") == "description" and values.get("content"):
            self.meta_description = True
        if tag == "link" and values.get("rel") == "canonical" and values.get("href"):
            self.canonical = values["href"] or ""
        if tag == "img" and not values.get("alt"):
            self.img_without_alt.append(values.get("src") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data


def parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def current_time() -> datetime:
    value = os.environ.get("SITE_NOW")
    return parse_dt(value) if value else datetime.now(timezone.utc).astimezone()


def load_posts() -> list[dict]:
    posts = []
    for path in sorted(POST_DIR.glob("*.json")):
        post = json.loads(path.read_text(encoding="utf-8-sig"))
        post["_publish_dt"] = parse_dt(post["publish_at"])
        posts.append(post)
    return posts


def html_pages() -> list[Path]:
    return list(ROOT.glob("*.html")) + list(BLOG_DIR.glob("**/index.html"))


def public_text_files() -> list[Path]:
    files: list[Path] = []
    for item in CHECK_PUBLIC_TEXT:
        if item.is_dir():
            files.extend(item.glob("**/*.html"))
        elif item.exists():
            files.append(item)
    return files


def json_ld_graph(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, flags=re.S)
    if not match:
        return []
    data = json.loads(match.group(1))
    if isinstance(data, dict) and isinstance(data.get("@graph"), list):
        return data["@graph"]
    if isinstance(data, dict):
        return [data]
    return []


def audit_html(errors: list[str]) -> None:
    for path in html_pages():
        page = PageAudit()
        page.feed(path.read_text(encoding="utf-8", errors="ignore"))
        rel = path.relative_to(ROOT).as_posix()
        if page.h1 != 1:
            errors.append(f"{rel}: expected one H1, found {page.h1}")
        if path.name != "404.html" and page.h2 < 1:
            errors.append(f"{rel}: expected at least one H2")
        if not page.title.strip():
            errors.append(f"{rel}: missing title")
        if not page.meta_description:
            errors.append(f"{rel}: missing meta description")
        if not page.canonical:
            errors.append(f"{rel}: missing canonical")
        if page.img_without_alt:
            errors.append(f"{rel}: image without alt: {page.img_without_alt[0]}")


def audit_public_encoding(errors: list[str]) -> None:
    for path in public_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        bad = sorted({f"U+{ord(ch):04X}" for ch in text if ord(ch) > 127})
        if bad:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: non-ASCII public text {bad[:6]}")
        if "Scheduled " in text:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: visible Scheduled label remains")


def audit_scheduling(posts: list[dict], errors: list[str]) -> list[dict]:
    now = current_time()
    due = [post for post in posts if post["_publish_dt"] <= now]
    future = [post for post in posts if post["_publish_dt"] > now]
    rss = (ROOT / "rss.xml").read_text(encoding="utf-8")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    if rss.count("<item>") != len(due):
        errors.append(f"rss.xml: expected {len(due)} scheduled items, found {rss.count('<item>')}")
    for post in due:
        slug = post["slug"]
        if not (BLOG_DIR / slug / "index.html").exists():
            errors.append(f"{slug}: due post HTML missing")
        if f"/blog/{slug}/" not in sitemap:
            errors.append(f"{slug}: due post missing from sitemap")
        if f"/blog/{slug}/" not in rss:
            errors.append(f"{slug}: due post missing from RSS")
    for post in future:
        slug = post["slug"]
        if (BLOG_DIR / slug / "index.html").exists():
            errors.append(f"{slug}: future post HTML exists")
        if f"/blog/{slug}/" in sitemap:
            errors.append(f"{slug}: future post leaked into sitemap")
        if f"/blog/{slug}/" in rss:
            errors.append(f"{slug}: future post leaked into RSS")
    return due


def audit_generated_post_schema(due: list[dict], errors: list[str]) -> None:
    for post in due:
        path = BLOG_DIR / post["slug"] / "index.html"
        text = path.read_text(encoding="utf-8", errors="ignore")
        graph = json_ld_graph(path)
        types = [item.get("@type") for item in graph]
        if "Article" not in types:
            errors.append(f"{post['slug']}: missing Article schema")
        if "BreadcrumbList" not in types:
            errors.append(f"{post['slug']}: missing BreadcrumbList schema")
        has_visible_faq = "Brief FAQ" in text
        has_faq_schema = "FAQPage" in types
        if has_visible_faq != has_faq_schema:
            errors.append(f"{post['slug']}: FAQPage schema does not match visible FAQ")
        if "Published " not in text:
            errors.append(f"{post['slug']}: missing Published label")
        if "Article table of contents" not in text:
            errors.append(f"{post['slug']}: missing table of contents")
        if "scenario-block" not in text:
            errors.append(f"{post['slug']}: missing scenario block in public HTML")
        if len(due) > 1 and text.count('class="related-card"') < min(3, len(due) - 1):
            errors.append(f"{post['slug']}: not enough related cards")


def audit_blog_index(due: list[dict], errors: list[str]) -> None:
    path = BLOG_DIR / "index.html"
    graph = json_ld_graph(path)
    item_list = next((item for item in graph if item.get("@type") == "ItemList"), None)
    if not item_list:
        errors.append("blog/index.html: missing ItemList schema")
        return
    items = item_list.get("itemListElement", [])
    if len(items) != len(due):
        errors.append(f"blog/index.html: expected {len(due)} ItemList entries, found {len(items)}")
    serialized = json.dumps(item_list)
    for post in due:
        if f"/blog/{post['slug']}/" not in serialized:
            errors.append(f"blog/index.html: ItemList missing {post['slug']}")


def main() -> None:
    posts = load_posts()
    errors: list[str] = []
    audit_html(errors)
    audit_public_encoding(errors)
    due = audit_scheduling(posts, errors)
    audit_generated_post_schema(due, errors)
    audit_blog_index(due, errors)
    if errors:
        print(json.dumps({"status": "fail", "errors": errors[:50]}, indent=2))
        raise SystemExit(1)
    print(json.dumps({"status": "pass", "scheduled_public_posts": len(due)}, indent=2))


if __name__ == "__main__":
    main()
