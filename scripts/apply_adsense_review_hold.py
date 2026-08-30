"""Apply the reversible public hold used while the AdSense review corpus is repaired.

The hold is intentionally an explicit deployment step: it removes the AdSense
loader and tells crawlers not to index the currently unreviewed static output.
It does not alter source post records, so releasing the hold is a small,
reviewable workflow change rather than a content rollback.
"""

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADSENSE_SCRIPT = re.compile(
    r'\s*<script\b[^>]*pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js[^>]*>\s*</script>',
    re.IGNORECASE,
)
ADSENSE_META = re.compile(
    r'\s*<meta\b[^>]*name=["\']google-adsense-account["\'][^>]*>',
    re.IGNORECASE,
)
ADSENSE_SLOT = re.compile(
    r'\s*<ins\b(?=[^>]*\bclass=["\'][^"\']*\badsbygoogle\b[^"\']*["\'])[^>]*>.*?</ins>',
    re.IGNORECASE | re.DOTALL,
)
ROBOTS_META = re.compile(r'<meta\b[^>]*name=["\']robots["\'][^>]*>', re.IGNORECASE)
RSS_ITEMS = re.compile(r'\s*<item>.*?</item>', re.IGNORECASE | re.DOTALL)
NOINDEX_META = '<meta name="robots" content="noindex, nofollow, noarchive">'
ADSENSE_SLOT_MARKER = re.compile(
    r'<ins\b[^>]*\bclass=["\'][^"\']*\badsbygoogle\b[^"\']*["\']',
    re.IGNORECASE,
)
ROBOTS_CONTENT = re.compile(
    r'\bcontent=["\']([^"\']*)["\']',
    re.IGNORECASE,
)


def hold_html(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    held = ADSENSE_SCRIPT.sub("", original)
    held = ADSENSE_META.sub("", held)
    held = ADSENSE_SLOT.sub("", held)
    if ROBOTS_META.search(held):
        held = ROBOTS_META.sub(NOINDEX_META, held)
    else:
        held = re.sub(r'(<head\b[^>]*>)', r'\1\n' + NOINDEX_META, held, count=1, flags=re.IGNORECASE)
    if held == original:
        return False
    path.write_text(held, encoding="utf-8")
    return True


def hold_rss(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    held = RSS_ITEMS.sub("", original)
    if held == original:
        return False
    path.write_text(held, encoding="utf-8")
    return True


def apply_hold(root: Path) -> int:
    changed = 0
    for page in root.rglob("*.html"):
        if ".git" not in page.parts:
            changed += hold_html(page)

    robots = root / "robots.txt"
    robots.write_text(
        "User-agent: *\nDisallow: /\nSitemap: https://caregos.com/sitemap.xml\n\n# AdSense review hold: publish only after editorial approval.\n",
        encoding="utf-8",
    )
    (root / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>\n',
        encoding="utf-8",
    )
    changed += hold_rss(root / "rss.xml") if (root / "rss.xml").exists() else 0
    return changed


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def verify_hold(root: Path) -> list[str]:
    """Return every reason the public editorial hold is unsafe or incomplete."""

    errors: list[str] = []
    html_pages = [page for page in root.rglob("*.html") if ".git" not in page.parts]
    if not html_pages:
        errors.append("no HTML pages were found")

    for page in html_pages:
        relative = page.relative_to(root)
        try:
            html = page.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative} is not readable UTF-8: {exc}")
            continue

        lowered = html.lower()
        if (
            "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" in lowered
            or "google-adsense-account" in lowered
            or ADSENSE_SLOT_MARKER.search(html)
        ):
            errors.append(f"{relative} contains an AdSense marker")

        robots_tag = ROBOTS_META.search(html)
        robots_content = ROBOTS_CONTENT.search(robots_tag.group(0)) if robots_tag else None
        directives = {
            directive.strip().lower()
            for directive in robots_content.group(1).split(",")
        } if robots_content else set()
        if "noindex" not in directives:
            errors.append(f"{relative} does not declare robots noindex")

    required_text: dict[str, str] = {}
    for filename in ("robots.txt", "sitemap.xml", "rss.xml"):
        path = root / filename
        if not path.is_file():
            errors.append(f"{filename} is missing")
            continue
        try:
            required_text[filename] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{filename} is not readable UTF-8: {exc}")

    robots = required_text.get("robots.txt")
    if robots is not None:
        lines = robots.splitlines()
        if "Disallow: /" not in lines:
            errors.append("robots.txt does not contain the exact Disallow: / line")
        if "Sitemap: https://caregos.com/sitemap.xml" not in lines:
            errors.append("robots.txt does not contain the exact Caregos sitemap line")

    sitemap = required_text.get("sitemap.xml")
    if sitemap is not None:
        try:
            sitemap_root = ET.fromstring(sitemap)
        except ET.ParseError as exc:
            errors.append(f"sitemap.xml is not valid XML: {exc}")
        else:
            discovery_entries = sum(
                1 for element in sitemap_root.iter() if _local_name(element.tag) in {"url", "loc"}
            )
            if discovery_entries:
                errors.append(f"sitemap.xml contains {discovery_entries} URL discovery entries")

    rss = required_text.get("rss.xml")
    if rss is not None:
        try:
            rss_root = ET.fromstring(rss)
        except ET.ParseError as exc:
            errors.append(f"rss.xml is not valid XML: {exc}")
        else:
            rss_items = sum(1 for element in rss_root.iter() if _local_name(element.tag) == "item")
            if rss_items:
                errors.append(f"rss.xml contains {rss_items} item entries")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply the Caregos AdSense review hold.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Validate the existing hold without changing generated files.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    if not args.verify_only:
        changed = apply_hold(root)
        print(f"Applied AdSense review hold to {changed} HTML/RSS files.")

    errors = verify_hold(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("Verified Caregos public editorial hold.")


if __name__ == "__main__":
    main()
