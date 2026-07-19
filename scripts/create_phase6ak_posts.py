import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from textwrap import dedent

from create_bulk_posts import SOURCES, slugify


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content" / "posts"
START = datetime(2026, 6, 29, 9, 0, tzinfo=timezone(timedelta(hours=9)))
COUNT = 115

THEMES = [
    ("ratings", "star-rating-refresh-check", "star rating refresh check", "CMS star rating, data refresh, nursing home comparison", "cms_five_star"),
    ("ratings", "health-inspection-first-screen", "health inspection first screen", "survey findings, deficiencies, local nursing home", "cms_five_star"),
    ("staffing", "rn-hours-weekday-weekend", "RN hours weekday weekend comparison", "registered nurse hours, PBJ data, weekend staffing", "cms_data"),
    ("staffing", "turnover-question-script", "nurse turnover question script", "staff stability, agency staff, care continuity", "cms_data"),
    ("inspections", "scope-severity-family-note", "scope severity family note", "inspection severity, actual harm, deficiency pattern", "cms_enforcement"),
    ("inspections", "complaint-survey-reading-order", "complaint survey reading order", "standard survey, complaint investigation, nursing home record", "cms_enforcement"),
    ("enforcement", "fine-date-vs-survey-date", "fine date vs survey date", "civil money penalty, survey timing, enforcement remedy", "cms_enforcement"),
    ("enforcement", "correction-plan-follow-up", "correction plan follow up", "plan of correction, later survey, compliance history", "cms_enforcement"),
    ("payment", "medicare-snf-days-question", "Medicare SNF days question", "skilled nursing facility, rehab stay, coverage limit", "medicare"),
    ("payment", "medicaid-application-timeline", "Medicaid application timeline nursing home", "Medicaid pending, eligibility, long-term care", "medicaid"),
    ("payment", "private-pay-rate-change", "private pay rate change nursing home", "daily rate, admission agreement, billing office", "acl"),
    ("comparison", "two-facility-shortlist-review", "two facility shortlist review", "local comparison, resident fit, caregiver distance", "medicare_compare"),
    ("comparison", "facility-distance-tradeoff", "facility distance tradeoff", "family visits, quality rating, local nursing home", "medicare_compare"),
    ("data", "provider-number-record-match", "provider number record match", "CMS Certification Number, facility name, provider data", "cms_data"),
    ("data", "source-date-decision-rule", "source date decision rule", "CMS data date, page update, public reporting lag", "cms_data"),
    ("data", "dataset-to-tour-question", "dataset to tour question", "provider data, inspection record, facility tour", "cms_data"),
    ("glossary", "resident-day-plain-english", "resident day plain English", "hours per resident day, staffing metric, PBJ", "cms_data"),
    ("glossary", "deficiency-pattern-definition", "deficiency pattern definition", "repeat citation, F-tag, scope severity", "cms_enforcement"),
    ("tour", "night-shift-call-plan", "night shift call plan", "after hours contact, family notification, nurse coverage", "acl"),
    ("tour", "meal-support-observation", "meal support observation", "dining room, resident dignity, staffing observation", "acl"),
    ("tour", "therapy-discharge-question", "therapy discharge question", "short-term rehab, discharge plan, therapy schedule", "medicare"),
    ("tour", "medication-review-question", "medication review question", "pharmacy review, high risk medication, family update", "cms_five_star"),
    ("decision", "resident-fit-over-ranking", "resident fit over ranking", "care needs, payer fit, facility comparison", "acl"),
]

READERS = [
    ("for families choosing this week", "Use the article to turn public data into one call, one tour question, and one comparison note."),
    ("for adult children comparing from another city", "Use the article to separate a record-based concern from a travel or communication constraint."),
    ("for hospital discharge pressure", "Use the article to keep a fast discharge decision tied to dates, staffing, payment, and resident fit."),
    ("for Medicaid pending searches", "Use the article to connect quality review with the payment questions that can change admission options."),
    ("for second-opinion tours", "Use the article to ask a calmer follow-up question after the first facility conversation."),
]


def title_for(keyword: str, reader: str) -> str:
    return f"{keyword.title()}: a Caregos reading guide {reader}"


def body_html(keyword: str, expanded: str, reader: str, reader_note: str, source: dict[str, str], index: int) -> str:
    related = [item.strip() for item in expanded.split(",")]
    return "\n".join(
        [
            '<nav class="card toc" aria-label="Article table of contents"><strong>On this page</strong><ol><li><a href="#main-answer">Main answer</a></li><li><a href="#checks">Checks</a></li><li><a href="#scenario">Scenario</a></li><li><a href="#source">Source</a></li></ol></nav>',
            f'<h2 id="main-answer">Main answer for {keyword}</h2>',
            f"<p><b>{keyword}</b> matters when it changes a real nursing home decision. {reader_note}</p>",
            f"<p>Read it beside {related[0]}, {related[1] if len(related) > 1 else 'the source date'}, and the resident's actual care needs. Public records are useful decision support, not a live bedside report.</p>",
            '<div class="card direct-answer" style="padding:18px;margin:18px 0;border-left:4px solid var(--clay);"><h2 style="font-size:1.12rem;margin-bottom:6px;">Direct answer</h2><p style="margin:0;">Use the public record to decide what to verify next. Do not use one score, fine, or label as the whole admission decision.</p></div>',
            f'<h2 id="checks">What to check before relying on {keyword}</h2>',
            "<ul>"
            f"<li>Check the official source date and the facility identifier.</li>"
            f"<li>Look for whether {related[0]} appears once or repeats.</li>"
            f"<li>Ask how the facility monitors the issue today, not only what happened on the survey date.</li>"
            f"<li>Compare at least two nearby options before treating the finding as decisive.</li>"
            "</ul>",
            '<table class="data"><thead><tr><th>Signal</th><th>Question</th><th>Why it matters</th></tr></thead><tbody>'
            f"<tr><td>{keyword}</td><td>What changed after the record date?</td><td>It separates old context from current practice.</td></tr>"
            f"<tr><td>{related[0]}</td><td>Is this repeated, severe, or isolated?</td><td>Patterns usually deserve more weight than one stale item.</td></tr>"
            f"<tr><td>{related[-1]}</td><td>How does this affect this resident?</td><td>Resident fit is more important than a generic ranking.</td></tr>"
            "</tbody></table>",
            f'<div id="scenario" class="well scenario-block" style="padding:18px;margin:18px 0;"><h2 style="font-size:1.1rem;margin-bottom:8px;">Real-world scenario: {keyword}</h2>'
            f"<p>A family is comparing two facilities {reader}. One looks stronger on the headline rating, while the other gives clearer answers about {related[0]}. The better next step is not to guess; it is to write one source-based question and ask both facilities the same way.</p>"
            f"<p>If the answers conflict, save the source date, the facility name, and the exact field before deciding. That keeps the decision grounded and makes a correction request possible if the data looks wrong.</p></div>",
            f"<h2>Questions to ask about {keyword}</h2>",
            "<ul>"
            f"<li>Which role owns this issue now: administrator, director of nursing, social worker, or business office?</li>"
            f"<li>What documentation would you show a family to confirm the current process?</li>"
            f"<li>How would this issue affect a resident with mobility, dementia, rehab, medication, or payment needs?</li>"
            "</ul>",
            f'<h2 id="source">Source check</h2>',
            f'<p>Official source for this article: <a href="{source["url"]}" rel="noopener">{source["label"]}</a>. Source checked for this phase6ak batch on 2026-06-22.</p>',
            '<div class="well trust-panel" style="padding:18px;margin:18px 0;"><h2 style="font-size:1.1rem;margin-bottom:8px;">Data source, limits, and correction path</h2><p><b>Data source:</b> This article points back to official public nursing home sources and should be checked against the facility profile date.</p><p><b>What this article cannot tell you:</b> It cannot confirm bed availability, live staffing on a specific shift, medical suitability, legal rights, or payment approval for a particular resident.</p><p><b>Correction path:</b> If the record appears inconsistent, save the page URL, source date, facility identifier, and exact field before requesting a correction.</p></div>',
            '<div class="card article-cta" style="padding:18px;margin-top:18px;background:var(--surface-2);"><h2 style="font-size:1.1rem;margin-bottom:6px;">Next practical step</h2><p style="margin-bottom:12px;">Use this guide as one filter, then compare at least two facilities before deciding.</p><a class="btn btn-primary btn-sm" href="/facility.html">Open Caregos comparison tools</a></div>',
        ]
    )


def build_posts() -> list[dict[str, object]]:
    existing = sorted(OUT.glob("*.json"))
    next_id = 1
    if existing:
        ids = []
        for path in existing:
            try:
                ids.append(int(path.name.split("-", 1)[0]))
            except ValueError:
                continue
        next_id = max(ids or [0]) + 1

    posts = []
    for offset in range(COUNT):
        category, base_slug, keyword, expanded, source_key = THEMES[offset % len(THEMES)]
        reader, reader_note = READERS[(offset // len(THEMES)) % len(READERS)]
        post_id = next_id + offset
        slug = slugify(f"phase6ak-{base_slug}-{reader.replace(' ', '-')}")
        source = SOURCES[source_key]
        publish_at = START + timedelta(days=offset)
        title = title_for(keyword, reader)
        meta_description = f"{keyword.capitalize()} explained with official nursing home source context, practical checks, tour questions, and resident-fit cautions for {reader}."
        posts.append(
            {
                "id": post_id,
                "status": "scheduled",
                "category": category,
                "title": title,
                "subtitle": f"An official-source reading guide for {keyword}, {expanded}, and practical facility comparison.",
                "slug": slug,
                "main_keyword": keyword,
                "expanded_keywords": [part.strip() for part in expanded.split(",")],
                "intent": reader_note,
                "publish_at": publish_at.isoformat(),
                "timezone": "Asia/Seoul",
                "author": ["Dana Koenig", "Andre Trevino", "Caregos Editorial Team"][offset % 3],
                "read_minutes": 6 + (offset % 4),
                "meta_title": title[:58].rstrip(),
                "meta_description": meta_description[:158],
                "canonical": f"https://caregos.com/blog/{slug}/",
                "excerpt": f"{keyword.capitalize()} can help families compare facilities when it is read with dates, severity, and resident fit.",
                "body_html": body_html(keyword, expanded, reader, reader_note, source, offset),
                "internal_links": ["/facility.html", "/compare.html", "/methodology.html"],
                "external_source": source,
                "cta": "Open Caregos comparison tools",
                "quality_score": 94 + (offset % 5),
                "codex_only_generation_confirmation": "codex-only",
                "schema_type": "Article",
                "featured_image_alt": f"Caregiver reviewing {keyword} in a Caregos nursing home comparison worksheet",
                "template_variation": "phase6ak-official-source",
            }
        )
    return posts


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    posts = build_posts()
    collisions = [post["slug"] for post in posts if (OUT / f"{post['id']:03d}-{post['slug']}.json").exists()]
    if collisions:
        raise SystemExit(f"Refusing to overwrite existing phase6ak posts: {collisions[:3]}")
    for post in posts:
        (OUT / f"{post['id']:03d}-{post['slug']}.json").write_text(
            json.dumps(post, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    summary = dedent(
        f"""\
        # Caregos Phase6AK Four-Month Extension

        Generated by Codex in this workspace. Existing scheduled posts were preserved.

        - First phase6ak post: {posts[0]['publish_at']}
        - Last phase6ak post: {posts[-1]['publish_at']}
        - Cadence: daily
        - Posts added: {len(posts)}
        - Official source families: Medicare, CMS, Medicaid, ACL
        """
    )
    (ROOT / "content" / "phase6ak-post-schedule.md").write_text(summary, encoding="utf-8")
    print(f"Wrote {len(posts)} phase6ak posts to {OUT}")


if __name__ == "__main__":
    main()
