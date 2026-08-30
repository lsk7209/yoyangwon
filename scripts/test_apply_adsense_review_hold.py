import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_adsense_review_hold import apply_hold, verify_hold


class AdsenseReviewHoldTests(unittest.TestCase):
    def test_hold_removes_ads_and_blocks_indexing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "nested").mkdir()
            (root / "index.html").write_text(
                '<html><head><meta name="google-adsense-account" content="ca-pub-test">'
                '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-test"></script>'
                '<meta name="robots" content="index, follow">'
                '</head><body><ins class="adsbygoogle">placeholder</ins>home</body></html>',
                encoding="utf-8",
            )
            (root / "nested" / "page.html").write_text("<html><head></head><body>page</body></html>", encoding="utf-8")
            (root / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
            (root / "sitemap.xml").write_text("<urlset><url>old</url></urlset>", encoding="utf-8")
            (root / "rss.xml").write_text("<rss><channel><item>old</item></channel></rss>", encoding="utf-8")

            apply_hold(root)

            homepage = (root / "index.html").read_text(encoding="utf-8")
            nested = (root / "nested" / "page.html").read_text(encoding="utf-8")
            self.assertNotIn("adsbygoogle", homepage)
            self.assertNotIn("google-adsense-account", homepage)
            self.assertIn('name="robots" content="noindex, nofollow, noarchive"', homepage)
            self.assertNotIn('content="index, follow"', homepage)
            self.assertIn('name="robots" content="noindex, nofollow, noarchive"', nested)
            self.assertEqual((root / "robots.txt").read_text(encoding="utf-8").splitlines()[1], "Disallow: /")
            self.assertIn("Sitemap: https://caregos.com/sitemap.xml", (root / "robots.txt").read_text(encoding="utf-8"))
            self.assertNotIn("<url>", (root / "sitemap.xml").read_text(encoding="utf-8"))
            self.assertNotIn("<item>", (root / "rss.xml").read_text(encoding="utf-8"))
            self.assertEqual(verify_hold(root), [])

    def test_verify_hold_fails_closed_for_missing_or_malformed_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(
                '<html><head><meta name="robots" content="noindex, nofollow, noarchive"></head><body>home</body></html>',
                encoding="utf-8",
            )
            (root / "robots.txt").write_text(
                "User-agent: *\nDisallow: /\nSitemap: https://caregos.com/sitemap.xml\n",
                encoding="utf-8",
            )
            (root / "rss.xml").write_text("<rss><channel></channel></rss>", encoding="utf-8")

            missing_errors = verify_hold(root)
            self.assertTrue(any("sitemap.xml is missing" in error for error in missing_errors))

            (root / "sitemap.xml").write_text("<urlset>", encoding="utf-8")
            malformed_errors = verify_hold(root)
            self.assertTrue(any("sitemap.xml is not valid XML" in error for error in malformed_errors))

    def test_verify_hold_rejects_ads_indexability_and_discovery_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(
                '<html><head><meta name="robots" content="index, follow">'
                '<script src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>'
                '</head><body>home</body></html>',
                encoding="utf-8",
            )
            (root / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
            (root / "sitemap.xml").write_text(
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://caregos.com/</loc></url></urlset>',
                encoding="utf-8",
            )
            (root / "rss.xml").write_text("<rss><channel><item><title>live</title></item></channel></rss>", encoding="utf-8")

            errors = verify_hold(root)
            self.assertTrue(any("AdSense marker" in error for error in errors))
            self.assertTrue(any("noindex" in error for error in errors))
            self.assertTrue(any("Disallow: /" in error for error in errors))
            self.assertTrue(any("sitemap.xml contains" in error for error in errors))
            self.assertTrue(any("rss.xml contains" in error for error in errors))
