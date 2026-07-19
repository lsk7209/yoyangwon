"""Apply the reversible public hold used while the AdSense review corpus is repaired.

The hold is intentionally an explicit deployment step: it removes the AdSense
loader and tells crawlers not to index the currently unreviewed static output.
It does not alter source post records, so releasing the hold is a small,
reviewable workflow change rather than a content rollback.
"""

import argparse
import re
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
        "User-agent: *\nDisallow: /\n\n# AdSense review hold: publish only after editorial approval.\n",
        encoding="utf-8",
    )
    (root / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>\n',
        encoding="utf-8",
    )
    changed += hold_rss(root / "rss.xml") if (root / "rss.xml").exists() else 0
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply the Caregos AdSense review hold.")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(f"Applied AdSense review hold to {apply_hold(args.root.resolve())} HTML/RSS files.")


if __name__ == "__main__":
    main()
