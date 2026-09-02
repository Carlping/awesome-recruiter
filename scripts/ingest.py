#!/usr/bin/env python3
"""Turn a Google Form dispatch payload into a canonical review YAML file."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = ROOT / "taxonomy"
REVIEWS_PATH = ROOT / "data" / "reviews"
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?886[-\s]?)?0?9\d{2}[-\s]?\d{3}[-\s]?\d{3}(?!\d)"
    r"|(?<!\d)\d{8,}(?!\d)"
)


def load_yaml(name: str) -> dict:
    with (TAXONOMY_PATH / name).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def normalise(value, mapping: dict, field: str):
    if value is None:
        return None
    text = str(value).strip()
    if text in mapping:
        return text
    folded = text.casefold()
    for key, definition in mapping.items():
        candidates = [definition.get("label_zh", ""), *definition.get("aliases", [])]
        if any(folded == str(candidate).strip().casefold() for candidate in candidates):
            return key
    raise ValueError(f"{field} 無法對應 taxonomy：{value!r}")


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().casefold()
    if text in {"是", "yes", "y", "true", "1"}:
        return True
    if text in {"否", "no", "n", "false", "0", ""}:
        return False
    raise ValueError(f"布林值無法解析：{value!r}")


def as_int(value, field: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} 必須是整數：{value!r}") from exc
    if not 1 <= number <= 5:
        raise ValueError(f"{field} 必須介於 1–5")
    return number


def scrub_summary(value) -> str:
    summary = str(value or "").strip()[:300]
    summary = EMAIL_RE.sub("[已移除聯絡資訊]", summary)
    return PHONE_RE.sub("[已移除聯絡資訊]", summary)


def next_id(period: str) -> str:
    prefix = f"rv-{period.replace('-', '')}-"
    numbers = []
    for path in REVIEWS_PATH.glob("**/*.yaml"):
        if path.stem.startswith(prefix):
            suffix = path.stem[len(prefix):]
            if suffix.isdigit():
                numbers.append(int(suffix))
    return f"{prefix}{max(numbers, default=0) + 1:06d}"


def build_record(payload: dict, taxonomies: dict, enums: dict) -> dict:
    recruiter = payload.get("recruiter") or {}
    period = str(payload.get("period", "")).strip()[:7]
    country = normalise(payload.get("country"), taxonomies["country"], "country")
    tw_region_value = payload.get("tw_region")
    tw_region = (
        normalise(tw_region_value, taxonomies["tw_region"], "tw_region")
        if country == "tw" and str(tw_region_value or "").strip()
        else None
    )
    record = {
        "id": next_id(period),
        "submitted_at": date.today().isoformat(),
        "recruiter": {
            "name": str(recruiter.get("name", "")).strip()[:60],
            "type": normalise(recruiter.get("type"), enums["recruiter_type"], "recruiter.type"),
            "company": str(recruiter.get("company", "")).strip()[:120],
            "linkedin": (str(recruiter["linkedin"]).strip() if recruiter.get("linkedin") else None),
        },
        "hiring_company": (
            str(payload["hiring_company"]).strip()[:120]
            if payload.get("hiring_company")
            else None
        ),
        "industry": normalise(payload.get("industry"), taxonomies["industry"], "industry"),
        "country": country,
        "tw_region": tw_region,
        "role_family": normalise(
            payload.get("role_family"), taxonomies["role_family"], "role_family"
        ),
        "seniority": normalise(payload.get("seniority"), enums["seniority"], "seniority"),
        "channel": normalise(payload.get("channel"), enums["channel"], "channel"),
        "period": period,
        "stage_reached": normalise(
            payload.get("stage_reached"), enums["stage_reached"], "stage_reached"
        ),
        "scores": {
            dimension: as_int(
                payload.get(f"score_{dimension}", (payload.get("scores") or {}).get(dimension)),
                f"score_{dimension}",
            )
            for dimension in ("responsiveness", "transparency", "professionalism", "respect", "closure")
        },
        "ghosted": as_bool(payload.get("ghosted")),
        "salary_disclosed_upfront": as_bool(payload.get("salary_disclosed_upfront")),
        "would_engage_again": as_bool(payload.get("would_engage_again")),
        "summary": scrub_summary(payload.get("summary")),
        "source": "form",
        "status": "published",
    }
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", required=True, type=Path)
    args = parser.parse_args()
    with args.payload.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload.get("review"), dict):
        raise ValueError("payload 必須包含 review mapping")
    taxonomies = {
        "industry": load_yaml("industries.yaml"),
        "country": load_yaml("countries.yaml"),
        "tw_region": load_yaml("tw_regions.yaml"),
        "role_family": load_yaml("role_families.yaml"),
    }
    enums = load_yaml("enums.yaml")
    record = build_record(payload["review"], taxonomies, enums)
    output_dir = REVIEWS_PATH / record["submitted_at"][:4]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{record['id']}.yaml"
    with output_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(record, handle, allow_unicode=True, sort_keys=False)
    print(output_path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
