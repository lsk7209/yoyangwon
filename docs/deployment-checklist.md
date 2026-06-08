# Caregos Deployment Checklist

## Before GitHub Push

- Production domain is currently set to `https://caregos.com/` in canonical URLs and sitemap generation.
- Keep `design-system.html` and `/plan/` noindexed or exclude them from production if they are not needed.
- Keep AdSense Auto Ads only; do not add manual ad slots.
- Confirm GSC property and GA4 property ID for the final domain.
- Verify CMS dataset IDs before replacing sample data with production data.

## Vercel Notes

This workspace is static and can be served as-is. No Vercel CLI, project linking, aliases, environment variables, or deployment commands were run.

## GSC / GA4 Required Inputs

- Final site URL.
- GSC verified property or service-account access.
- GA4 property ID or a token mapping for this domain.

## Current GSC Finding

- `https://caregos.com/`, `https://www.caregos.com/`, and `sc-domain:caregos.com` can be added to the connected GSC account, but currently return `siteUnverifiedUser`.
- Search Console sitemap submission returns 403 until ownership verification is completed.
- The current OAuth token has Search Console scope but not Site Verification scope, so the Site Verification API cannot issue/complete verification tokens without reauthorization.
- The live `caregos.com` domain does not currently serve this local static site, so adding verification files locally is not enough; the file must be deployed to the live host first.
- The live `https://caregos.com/sitemap.xml` currently contains only `/lander`; it must be replaced by the generated sitemap before GSC submission can show the intended URLs.
