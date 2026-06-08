import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DATA = ROOT / "content" / "cms" / "public_facilities_sangamon_il.json"
DATA_JS = ROOT / "styles" / "data.js"
PUBLIC_HTML = [
    ROOT / "index.html",
    ROOT / "listings.html",
    ROOT / "facility.html",
    ROOT / "compare.html",
    ROOT / "enforcement.html",
    ROOT / "methodology.html",
    ROOT / "about.html",
    ROOT / "privacy.html",
]


def fail(message: str) -> None:
    raise SystemExit(f"CMS data validation failed: {message}")


def main() -> None:
    if not PUBLIC_DATA.exists():
        fail(f"missing {PUBLIC_DATA.relative_to(ROOT)}")
    if not DATA_JS.exists():
        fail(f"missing {DATA_JS.relative_to(ROOT)}")

    payload = json.loads(PUBLIC_DATA.read_text(encoding="utf-8"))
    metadata = payload.get("metadata", {})
    facilities = payload.get("facilities", [])
    defs = payload.get("defs", {})

    if metadata.get("source") != "CMS Provider Data Catalog":
        fail("metadata source is not CMS Provider Data Catalog")
    if metadata.get("providerDataset") != "4pq5-n9py":
        fail("unexpected provider dataset id")
    if metadata.get("deficiencyDataset") != "r5ix-sfxw":
        fail("unexpected deficiency dataset id")
    if not metadata.get("processingDates"):
        fail("missing CMS processing date")
    if len(facilities) < 1:
        fail("no facilities imported")
    if metadata.get("facilityCount") != len(facilities):
        fail("facility count metadata mismatch")

    required = {"id", "ccn", "name", "address", "overall", "health", "staffing", "qm", "rnHrs", "deficiencies"}
    for facility in facilities:
        missing = sorted(key for key in required if key not in facility or facility[key] in ("", None))
        if missing:
            fail(f"{facility.get('name', 'facility')} missing fields: {', '.join(missing)}")
        if facility["id"] not in defs:
            fail(f"{facility['name']} missing deficiency list")

    js = DATA_JS.read_text(encoding="utf-8")
    for marker in ("window.DATA_SOURCE", "window.FACILITIES", "window.DEFS"):
        if marker not in js:
            fail(f"styles/data.js missing {marker}")
    if "illustrative sample data" in js.lower() or "design prototype" in js.lower():
        fail("styles/data.js contains sample/prototype copy")

    banned = re.compile(r"illustrative sample data|design prototype|not live CMS|sample records", re.I)
    for path in PUBLIC_HTML:
        text = path.read_text(encoding="utf-8")
        if banned.search(text):
            fail(f"{path.relative_to(ROOT)} still contains sample/prototype wording")

    print(
        json.dumps(
            {
                "status": "ok",
                "facilities": len(facilities),
                "processingDates": metadata["processingDates"],
                "providerDataset": metadata["providerDataset"],
                "deficiencyDataset": metadata["deficiencyDataset"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
