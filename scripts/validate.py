#!/usr/bin/env python3
"""Validate review YAML files against the schema and project taxonomies."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "review.schema.json"
REVIEWS_PATH = ROOT / "data" / "reviews"
TAXONOMY_PATH = ROOT / "taxonomy"
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?886[-\s]?)?0?9\d{2}[-\s]?\d{3}[-\s]?\d{3}(?!\d)"
    r"|(?<!\d)\d{8,}(?!\d)"
)


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> int:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        schema = __import__("json").load(handle)
    taxonomies = {
        "industry": load_yaml(TAXONOMY_PATH / "industries.yaml"),
        "region": load_yaml(TAXONOMY_PATH / "regions.yaml"),
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
            "region": record.get("region"),
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

        summary = record.get("summary")
        if isinstance(summary, str) and (EMAIL_RE.search(summary) or PHONE_RE.search(summary)):
            errors.append(f"{path.relative_to(ROOT)}: summary 不得包含電話或 Email")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"驗證失敗：{len(errors)} 個錯誤", file=sys.stderr)
        return 1
    print(f"驗證成功：{len(files)} 筆 review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
