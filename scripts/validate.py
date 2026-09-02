#!/usr/bin/env python3
"""Validate review YAML files against the schema and project taxonomies."""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "review.schema.json"
REVIEWS_PATH = ROOT / "data" / "reviews"
TAXONOMY_PATH = ROOT / "taxonomy"
SUBDIVISIONS_PATH = TAXONOMY_PATH / "subdivisions"
REMOVED_PATH = ROOT / "data" / "removed.yaml"
REVIEW_ID_RE = re.compile(r"^rv-\d{6}-\d{6}$")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?886[-\s]?)?0?9\d{2}[-\s]?\d{3}[-\s]?\d{3}(?!\d)"
    r"|(?<!\d)\d{8,}(?!\d)"
)


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_subdivision(country: str) -> dict | None:
    path = SUBDIVISIONS_PATH / f"{country}.yaml"
    return load_yaml(path) if path.exists() else None


def main() -> int:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        schema = __import__("json").load(handle)
    taxonomies = {
        "industry": load_yaml(TAXONOMY_PATH / "industries.yaml"),
        "country": load_yaml(TAXONOMY_PATH / "countries.yaml"),
        "role_family": load_yaml(TAXONOMY_PATH / "role_families.yaml"),
    }
    enums = load_yaml(TAXONOMY_PATH / "enums.yaml")
    for field in ("recruiter_type", "seniority", "channel", "stage_reached", "source", "status"):
        taxonomies[field] = enums[field]

    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    files = sorted(REVIEWS_PATH.glob("**/*.yaml"))
    errors: list[str] = []
    seen: dict[str, Path] = {}

    for path in files:
        try:
            record = load_yaml(path)
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: YAML 解析失敗：{exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{path.relative_to(ROOT)}: 頂層必須是 mapping")
            continue

        for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path) or "$"
            errors.append(f"{path.relative_to(ROOT)}: {location}: {error.message}")

        record_id = record.get("id")
        if record_id:
            if record_id in seen:
                errors.append(
                    f"{path.relative_to(ROOT)}: id {record_id} 重複（{seen[record_id].relative_to(ROOT)}）"
                )
            else:
                seen[record_id] = path
            if path.stem != record_id:
                errors.append(
                    f"{path.relative_to(ROOT)}: id {record_id} 與檔名不一致"
                )

        field_values = {
            "industry": record.get("industry"),
            "country": record.get("country"),
            "role_family": record.get("role_family"),
            "recruiter_type": (record.get("recruiter") or {}).get("type"),
            "seniority": record.get("seniority"),
            "channel": record.get("channel"),
            "stage_reached": record.get("stage_reached"),
            "source": record.get("source"),
            "status": record.get("status"),
        }
        for field, value in field_values.items():
            if value not in taxonomies[field]:
                errors.append(
                    f"{path.relative_to(ROOT)}: {field}={value!r} 不在 taxonomy 中"
                )
        country = record.get("country")
        admin_area = record.get("admin_area")
        metro = record.get("metro")
        subdivision = load_subdivision(country) if country in taxonomies["country"] else None
        if subdivision is None:
            if admin_area is not None or metro is not None:
                errors.append(
                    f"{path.relative_to(ROOT)}: country 沒有 subdivision taxonomy 時 admin_area/metro 必須為 null"
                )
        else:
            if admin_area is not None and admin_area not in subdivision["admin_areas"]:
                errors.append(
                    f"{path.relative_to(ROOT)}: admin_area={admin_area!r} 不在 taxonomy 中"
                )
            if metro is not None and metro not in subdivision["metros"]:
                errors.append(
                    f"{path.relative_to(ROOT)}: metro={metro!r} 不在 taxonomy 中"
                )
            metro_definition = subdivision["metros"].get(metro) if metro else None
            allowed_admin_areas = (metro_definition or {}).get("admin_areas", [])
            if admin_area is not None and metro_definition and allowed_admin_areas:
                if admin_area not in allowed_admin_areas:
                    errors.append(
                        f"{path.relative_to(ROOT)}: admin_area={admin_area!r} 不屬於 metro={metro!r}"
                    )

        summary = record.get("summary")
        if isinstance(summary, str) and (EMAIL_RE.search(summary) or PHONE_RE.search(summary)):
            errors.append(f"{path.relative_to(ROOT)}: summary 不得包含電話或 Email")

    try:
        removed = load_yaml(REMOVED_PATH)
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{REMOVED_PATH.relative_to(ROOT)}: YAML 解析失敗：{exc}")
        removed = []
    if not isinstance(removed, list):
        errors.append(f"{REMOVED_PATH.relative_to(ROOT)}: 頂層必須是 list")
        removed = []
    removal_reasons = enums["removal_reason"]
    for tombstone in removed:
        if not isinstance(tombstone, dict):
            errors.append(f"{REMOVED_PATH.relative_to(ROOT)}: 墓碑必須是 mapping")
            continue
        tombstone_id = tombstone.get("id")
        if not isinstance(tombstone_id, str) or not REVIEW_ID_RE.fullmatch(tombstone_id):
            errors.append(
                f"{REMOVED_PATH.relative_to(ROOT)}: id {tombstone_id!r} 格式錯誤"
            )
        elif tombstone_id in seen:
            errors.append(
                f"{REMOVED_PATH.relative_to(ROOT)}: id {tombstone_id} 重複"
            )
        else:
            seen[tombstone_id] = REMOVED_PATH
        removed_at = tombstone.get("removed_at")
        if isinstance(removed_at, date):
            pass
        elif isinstance(removed_at, str):
            try:
                date.fromisoformat(removed_at)
            except ValueError:
                errors.append(
                    f"{REMOVED_PATH.relative_to(ROOT)}: removed_at={removed_at!r} 不是日期"
                )
        else:
            errors.append(
                f"{REMOVED_PATH.relative_to(ROOT)}: removed_at 必須是日期"
            )
        reason = tombstone.get("reason")
        if reason not in removal_reasons:
            errors.append(
                f"{REMOVED_PATH.relative_to(ROOT)}: reason={reason!r} 不在 removal_reason taxonomy 中"
            )
        if isinstance(tombstone_id, str) and any(
            path.stem == tombstone_id for path in files
        ):
            errors.append(
                f"{REMOVED_PATH.relative_to(ROOT)}: tombstone id {tombstone_id} 仍存在 review 檔案"
            )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"驗證失敗：{len(errors)} 個錯誤", file=sys.stderr)
        return 1
    print(f"驗證成功：{len(files)} 筆 review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
