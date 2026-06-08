import argparse
import csv
import json
from pathlib import Path


REQUIRED_FIELDS = {
    "title",
    "subtitle",
    "main_keyword",
    "expanded_keywords",
    "intent",
    "category",
    "quality_score",
    "codex_only_generation_confirmation",
    "slug",
    "internal_links",
    "external_source",
    "cta",
}

PUBLISH_READY_FIELDS = {
    "meta_title",
    "meta_description",
    "canonical",
    "excerpt",
}

TRUE_VALUES = {"1", "true", "yes", "confirmed", "codex", "codex-only", "ok", "pass"}


def split_count(value: str) -> int:
    parts = value.replace("|", ";").replace(",", ";").split(";")
    return len([part for part in (item.strip() for item in parts) if part])


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]


def validate(rows: list[dict[str, str]], threshold: float, publish_ready: bool) -> list[str]:
    errors: list[str] = []
    seen: dict[str, set[str]] = {"title": set(), "slug": set(), "main_keyword": set()}
    required = set(REQUIRED_FIELDS)
    if publish_ready:
        required |= PUBLISH_READY_FIELDS

    if not rows:
        return ["No rows found."]

    for index, row in enumerate(rows, 1):
        label = row.get("title") or f"row {index}"
        for field in sorted(required):
            if not row.get(field):
                errors.append(f"{label}: missing {field}")

        for field in seen:
            value = row.get(field, "").casefold()
            if value and value in seen[field]:
                errors.append(f"{label}: duplicate {field}")
            seen[field].add(value)

        confirmation = row.get("codex_only_generation_confirmation", "").casefold()
        if confirmation not in TRUE_VALUES:
            errors.append(f"{label}: Codex-only generation not confirmed")

        try:
            score = float(row.get("quality_score", ""))
        except ValueError:
            errors.append(f"{label}: invalid quality_score")
        else:
            if score < threshold:
                errors.append(f"{label}: quality_score {score:g} below {threshold:g}")

        if split_count(row.get("internal_links", "")) < 2:
            errors.append(f"{label}: fewer than two internal links")
        if split_count(row.get("expanded_keywords", "")) < 2:
            errors.append(f"{label}: fewer than two expanded keywords")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Caregos bulk blog tracking CSV.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--threshold", type=float, default=90.0)
    parser.add_argument("--publish-ready", action="store_true")
    args = parser.parse_args()

    errors = validate(read_rows(args.path), args.threshold, args.publish_ready)
    if errors:
        print(json.dumps({"status": "fail", "errors": errors[:50]}, indent=2))
        raise SystemExit(1)
    rows = read_rows(args.path)
    print(json.dumps({"status": "pass", "rows": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
