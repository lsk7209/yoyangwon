import argparse
import datetime as dt
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {
    "404.html",
    "design-system.html",
}


def page_url(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def discover_pages() -> list[str]:
    pages = []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("scripts/") or rel.startswith("docs/") or rel.startswith("plan/") or rel.startswith("content/"):
            continue
        if path.name in EXCLUDE:
            continue
        pages.append(page_url(path))
    return pages


def build_xml(site_url: str) -> str:
    base = site_url.rstrip("/") + "/"
    today = dt.date.today().isoformat()
    urls = []
    for path in discover_pages():
        loc = urljoin(base, path.lstrip("/"))
        priority = "1.0" if path == "/" else "0.8"
        changefreq = "weekly" if path in {"/", "/listings.html", "/blog/"} else "monthly"
        urls.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sitemap.xml for NH-Data.")
    parser.add_argument("--site-url", required=True, help="Production site URL, e.g. https://example.com/")
    parser.add_argument("--out", default=str(ROOT / "sitemap.xml"))
    args = parser.parse_args()
    out = Path(args.out)
    out.write_text(build_xml(args.site_url), encoding="utf-8")
    print(f"Wrote {out} with {len(discover_pages())} URLs for {args.site_url.rstrip('/')}/")


if __name__ == "__main__":
    main()
