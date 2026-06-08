import argparse
import json
import math
import re
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROVIDER_DATASET = "4pq5-n9py"
DEFICIENCY_DATASET = "r5ix-sfxw"
API_BASE = "https://data.cms.gov/provider-data/api/1/datastore/query"
SPRINGFIELD_IL = (39.7817, -89.6501)


def fetch_dataset(dataset: str, conditions: list[tuple[str, str]], limit: int = 5000, offset: int = 0) -> dict:
    params: dict[str, str | int] = {"limit": limit, "offset": offset}
    for index, (field, value) in enumerate(conditions):
        params[f"conditions[{index}][property]"] = field
        params[f"conditions[{index}][value]"] = value
        params[f"conditions[{index}][operator]"] = "="
    url = f"{API_BASE}/{dataset}/0?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Caregos CMS ETL"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_all(dataset: str, conditions: list[tuple[str, str]], page_size: int = 500) -> list[dict]:
    rows: list[dict] = []
    offset = 0
    while True:
        payload = fetch_dataset(dataset, conditions, limit=page_size, offset=offset)
        batch = payload.get("results", [])
        rows.extend(batch)
        if len(batch) < page_size:
            return rows
        offset += page_size


def to_float(value, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(str(value).replace(",", ""))
    except ValueError:
        return default


def to_int(value, default: int = 0) -> int:
    return int(round(to_float(value, float(default))))


def slugify(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text or "facility"


def title_case_name(value: str) -> str:
    small = {"of", "and", "the", "on", "at"}
    words = []
    for word in value.split():
        lower = word.lower()
        words.append(lower if lower in small else lower[:1].upper() + lower[1:])
    return " ".join(words)


def haversine(lat: float, lon: float, origin: tuple[float, float] = SPRINGFIELD_IL) -> float:
    if not lat or not lon:
        return 0.0
    lat1, lon1 = map(math.radians, origin)
    lat2, lon2 = map(math.radians, (lat, lon))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return round(3958.8 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)


def severity_bucket(code: str) -> tuple[str, str, str]:
    code = (code or "").upper()
    scope = {"D": "Isolated", "G": "Isolated", "J": "Isolated", "E": "Pattern", "H": "Pattern", "K": "Pattern", "F": "Widespread", "I": "Widespread", "L": "Widespread"}.get(code, "Isolated")
    if code in {"G", "H", "I"}:
        return scope, "high", "Actual harm"
    if code in {"J", "K", "L"}:
        return scope, "high", "Immediate jeopardy"
    if code in {"D", "E", "F"}:
        return scope, "mid", "Potential for harm"
    return scope, "low", "No actual harm"


def deficiency_to_public(row: dict) -> dict:
    tag = str(row.get("deficiency_tag_number") or "").lstrip("0")
    code = row.get("scope_severity_code", "")
    scope, sev, harm = severity_bucket(code)
    return {
        "date": row.get("survey_date", ""),
        "ftag": f"{row.get('deficiency_prefix', 'F')}-{tag or '000'}",
        "scope": scope,
        "sev": sev,
        "harm": harm,
        "text": row.get("deficiency_description", ""),
        "survey": row.get("survey_type", "Health"),
    }


def normalize_provider(row: dict, percentile_by_ccn: dict[str, int], defs: list[dict]) -> dict:
    ccn = row.get("cms_certification_number_ccn", "")
    beds = to_int(row.get("number_of_certified_beds"))
    residents = to_float(row.get("average_number_of_residents_per_day"))
    occupancy = round((residents / beds) * 100) if beds else 0
    lat = to_float(row.get("latitude"))
    lon = to_float(row.get("longitude"))
    name = title_case_name(row.get("provider_name", ""))
    abuse = str(row.get("abuse_icon", "")).upper() == "Y"
    sff_status = row.get("special_focus_status", "")
    return {
        "id": f"{slugify(name)}-{ccn}",
        "ccn": ccn,
        "name": name,
        "city": f"{title_case_name(row.get('citytown', ''))}, {row.get('state', '')}",
        "address": f"{title_case_name(row.get('provider_address', ''))}, {title_case_name(row.get('citytown', ''))}, {row.get('state', '')} {row.get('zip_code', '')}",
        "ownership": row.get("ownership_type", ""),
        "beds": beds,
        "occupancy": occupancy,
        "overall": to_int(row.get("overall_rating"), 0),
        "health": to_int(row.get("health_inspection_rating"), 0),
        "staffing": to_int(row.get("staffing_rating"), 0),
        "qm": to_int(row.get("qm_rating"), 0),
        "pctile": percentile_by_ccn.get(ccn, 0),
        "trend": [to_int(row.get("overall_rating"), 0)],
        "trendNote": "CMS current release",
        "rnHrs": round(to_float(row.get("reported_rn_staffing_hours_per_resident_per_day")), 2),
        "totalHrs": round(to_float(row.get("reported_total_nurse_staffing_hours_per_resident_per_day")), 2),
        "turnover": round(to_float(row.get("total_nursing_staff_turnover"))),
        "deficiencies": len(defs),
        "sevHigh": len([item for item in defs if item.get("sev") == "high"]),
        "fines": to_int(row.get("total_amount_of_fines_in_dollars")),
        "sff": bool(sff_status),
        "sffStatus": sff_status,
        "abuse": abuse,
        "distance": haversine(lat, lon),
    }


def percentile_map(rows: list[dict]) -> dict[str, int]:
    valid = [(row.get("cms_certification_number_ccn", ""), to_float(row.get("overall_rating"))) for row in rows]
    valid = [(ccn, rating) for ccn, rating in valid if ccn and rating]
    result = {}
    for ccn, rating in valid:
        below_or_equal = len([1 for _, value in valid if value <= rating])
        result[ccn] = round((below_or_equal / len(valid)) * 100)
    return result


def js_assign(name: str, value) -> str:
    return f"window.{name} = {json.dumps(value, ensure_ascii=True, indent=2)};"


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch CMS Provider Data and generate styles/data.js.")
    parser.add_argument("--state", default="IL")
    parser.add_argument("--county", default="Sangamon")
    parser.add_argument("--out", default=str(ROOT / "styles" / "data.js"))
    parser.add_argument("--raw-dir", default=str(ROOT / "content" / "cms"))
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    providers = fetch_all(PROVIDER_DATASET, [("state", args.state), ("countyparish", args.county)])
    if not providers:
        raise SystemExit(f"No CMS provider rows found for {args.county}, {args.state}.")

    percentile_by_ccn = percentile_map(providers)
    defs_by_ccn: dict[str, list[dict]] = {}
    raw_defs_by_ccn: dict[str, list[dict]] = {}
    for row in providers:
        ccn = row.get("cms_certification_number_ccn", "")
        raw_defs = fetch_all(DEFICIENCY_DATASET, [("cms_certification_number_ccn", ccn)], page_size=500)
        raw_defs.sort(key=lambda item: item.get("survey_date", ""), reverse=True)
        raw_defs_by_ccn[ccn] = raw_defs
        defs_by_ccn[ccn] = [deficiency_to_public(item) for item in raw_defs[:10]]

    facilities = [
        normalize_provider(row, percentile_by_ccn, defs_by_ccn.get(row.get("cms_certification_number_ccn", ""), []))
        for row in providers
    ]
    facilities.sort(key=lambda item: (item["city"], item["name"]))
    public_defs = {facility["id"]: defs_by_ccn.get(facility["ccn"], []) for facility in facilities}
    metadata = {
        "source": "CMS Provider Data Catalog",
        "providerDataset": PROVIDER_DATASET,
        "deficiencyDataset": DEFICIENCY_DATASET,
        "state": args.state,
        "county": args.county,
        "facilityCount": len(facilities),
        "processingDates": sorted({row.get("processing_date", "") for row in providers if row.get("processing_date")}),
    }

    (raw_dir / "provider_info_sangamon_il.json").write_text(json.dumps(providers, ensure_ascii=True, indent=2), encoding="utf-8")
    (raw_dir / "health_deficiencies_sangamon_il.json").write_text(json.dumps(raw_defs_by_ccn, ensure_ascii=True, indent=2), encoding="utf-8")
    (raw_dir / "public_facilities_sangamon_il.json").write_text(json.dumps({"metadata": metadata, "facilities": facilities, "defs": public_defs}, ensure_ascii=True, indent=2), encoding="utf-8")

    js = "\n".join(
        [
            "/* Generated from CMS Provider Data Catalog. Do not edit by hand.",
            f"   Dataset: Provider Information ({PROVIDER_DATASET}), Health Deficiencies ({DEFICIENCY_DATASET}). */",
            js_assign("DATA_SOURCE", metadata),
            js_assign("FACILITIES", facilities),
            "window.DEFS = " + json.dumps(public_defs, ensure_ascii=True, indent=2) + ";",
            "window.DEFICIENCIES = window.DEFS[window.FACILITIES[0]?.id] || [];",
            "",
        ]
    )
    Path(args.out).write_text(js, encoding="utf-8")
    print(json.dumps({"status": "ok", "facilities": len(facilities), "out": args.out, "source": metadata}, indent=2))


if __name__ == "__main__":
    main()
