import argparse
import json
import os
import sys
import tempfile
import time
import urllib.request
from urllib.parse import urljoin

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


CLIENT_SECRETS = r"D:\env\adsense_oauth_client.json"
TOKEN_FILE = r"D:\env\gsc_token.json"
SCOPES = ["https://www.googleapis.com/auth/webmasters"]


def get_credentials() -> Credentials:
    with open(TOKEN_FILE, encoding="utf-8") as f:
        token_data = json.load(f)
    with open(CLIENT_SECRETS, encoding="utf-8") as f:
        client = json.load(f)["installed"]
    token_data.setdefault("client_id", client["client_id"])
    token_data.setdefault("client_secret", client["client_secret"])
    token_data.setdefault("token_uri", "https://oauth2.googleapis.com/token")
    token_data.setdefault("universe_domain", "googleapis.com")
    if "token" not in token_data and "access_token" in token_data:
        token_data["token"] = token_data["access_token"]

    fd, tmp = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(token_data, f)
        creds = Credentials.from_authorized_user_file(tmp, SCOPES)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass

    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        merged = json.loads(creds.to_json())
        merged["access_token"] = merged.get("token", "")
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2)
    return creds


def fetch_status(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Caregos sitemap verifier"})
    with urllib.request.urlopen(req, timeout=20) as res:
        body = res.read(512).decode("utf-8", errors="replace")
        return res.status, body


def find_property(service, site_url: str) -> str | None:
    normalized = site_url.rstrip("/") + "/"
    host = normalized.split("//", 1)[-1].split("/", 1)[0]
    candidates = {normalized, "sc-domain:" + host.removeprefix("www.")}
    sites = service.sites().list().execute().get("siteEntry", [])
    for site in sites:
        if site.get("siteUrl") in candidates and site.get("permissionLevel") in {"siteOwner", "siteFullUser"}:
            return site["siteUrl"]
    return None


def list_matching_properties(service, site_url: str) -> list[dict]:
    normalized = site_url.rstrip("/") + "/"
    host = normalized.split("//", 1)[-1].split("/", 1)[0]
    needle = host.removeprefix("www.")
    sites = service.sites().list().execute().get("siteEntry", [])
    return [s for s in sites if needle in s.get("siteUrl", "")]


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit sitemap.xml to Google Search Console and verify status.")
    parser.add_argument("--site-url", required=True, help="Production site URL, e.g. https://example.com/")
    parser.add_argument("--sitemap", default="sitemap.xml", help="Sitemap path or full URL.")
    parser.add_argument("--wait", type=int, default=8, help="Seconds to wait before status check.")
    args = parser.parse_args()

    site_url = args.site_url.rstrip("/") + "/"
    sitemap_url = args.sitemap if args.sitemap.startswith("http") else urljoin(site_url, args.sitemap.lstrip("/"))

    print(f"site_type=static-html")
    print(f"site_url={site_url}")
    print(f"sitemap_url={sitemap_url}")

    try:
        status, head = fetch_status(sitemap_url)
        print(f"sitemap_http_status={status}")
        if "<urlset" not in head and "<sitemapindex" not in head:
            print("sitemap_fetch=not_xml")
            return 2
    except Exception as exc:
        print(f"sitemap_fetch_error={exc}")
        return 2

    service = build("webmasters", "v3", credentials=get_credentials())
    prop = find_property(service, site_url)
    if not prop:
        for match in list_matching_properties(service, site_url):
            print(f"gsc_property_candidate={match.get('siteUrl')} permission={match.get('permissionLevel')}")
        print("gsc_property=not_found_or_no_write_permission")
        print("result=blocked")
        return 3

    print(f"gsc_property={prop}")
    try:
        service.sitemaps().submit(siteUrl=prop, feedpath=sitemap_url).execute()
        print("submit=ok")
    except HttpError as exc:
        print(f"submit_error={exc}")
        return 4

    time.sleep(max(args.wait, 0))
    try:
        sm = service.sitemaps().get(siteUrl=prop, feedpath=sitemap_url).execute()
    except HttpError as exc:
        print(f"status_error={exc}")
        return 5

    print(f"is_pending={sm.get('isPending', False)}")
    print(f"errors={sm.get('errors', 0)}")
    print(f"warnings={sm.get('warnings', 0)}")
    print(f"last_submitted={sm.get('lastSubmitted', '')}")
    print(f"last_downloaded={sm.get('lastDownloaded', '')}")
    print("result=success" if sm.get("errors", 0) == 0 and sm.get("warnings", 0) == 0 else "result=submitted_with_issues")
    return 0


if __name__ == "__main__":
    sys.exit(main())
