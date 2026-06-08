# GSC Sitemap Submission Report

Date: 2026-06-07

## Site Type

Static HTML/CSS/JS site.

Evidence:

- No `wp-config.php`
- No `package.json`
- No `next.config.js`
- Root contains static `.html` pages and `styles/`

## Target Checked

- `https://caregos.com/`
- `https://www.caregos.com/`
- `sc-domain:caregos.com`

## Live Sitemap Check

`https://caregos.com/sitemap.xml` returns HTTP 200 and XML, but the live sitemap currently contains only:

- `https://caregos.com/lander`

The local implementation sitemap contains 11 URLs for the static Caregos site, but this local sitemap is not yet live at the production domain.

## GSC API Result

Search Console API can add the properties, but all three are currently:

- `siteUnverifiedUser`

Sitemap submission returns 403:

- insufficient permission for `https://caregos.com/`
- insufficient permission for `https://www.caregos.com/`
- insufficient permission for `sc-domain:caregos.com`

## Site Verification API Result

The current OAuth token has Search Console scope but not Site Verification scope. Site Verification API token request returns 403 insufficient authentication scopes.

## Current Local Automation

Added:

- `sitemap.xml`
- `robots.txt` with sitemap reference
- `scripts/generate_sitemap.py`
- `scripts/gsc_submit_sitemap.py`
- Absolute production canonicals using `https://caregos.com/`
- `design-system.html` and `/plan/` excluded from search results; `/plan/` is also excluded from generated sitemap.
- Public pages include absolute canonicals, RSS alternates, one H1 per page, ordered heading levels, and required image alt text.
- `rss.xml`, `ads.txt`, and `llms.txt` are present in the site root.

Command to run after live deployment and GSC verification:

```powershell
python scripts\generate_sitemap.py --site-url https://caregos.com/
python scripts\gsc_submit_sitemap.py --site-url https://caregos.com/ --sitemap sitemap.xml
```

## Blocker

GSC "Success" status cannot be reached through the Search Console API until both are true:

1. The production domain serves the generated `sitemap.xml`.
2. The connected Google account has verified owner/full-user permission for the property.

## Latest Local Validation

Run on 2026-06-07:

- Public HTML pages checked: 11
- Generated sitemap URLs: 11
- SEO structure issues: 0
- Broken local references: 0
- Manual AdSense slots found: 0
