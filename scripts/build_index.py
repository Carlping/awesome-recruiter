#!/usr/bin/env python3
"""Build static-site JSON indexes from published review YAML files."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REVIEWS_PATH = ROOT / "data" / "reviews"
OUTPUT_PATH = ROOT / "site" / "data"
DIMENSIONS = ("responsiveness", "transparency", "professionalism", "respect", "closure")


def read_records() -> list[dict]:
    records = []
    for path in sorted(REVIEWS_PATH.glob("**/*.yaml")):
        with path.open(encoding="utf-8") as handle:
            record = yaml.safe_load(handle)
        if record.get("status") == "published":
            records.append(record)
    return records


def flatten(record: dict) -> dict:
    recruiter = record["recruiter"]
    flattened = {
        "id": record["id"],
        "submitted_at": record["submitted_at"].isoformat()
        if hasattr(record["submitted_at"], "isoformat")
        else record["submitted_at"],
        "recruiter_name": recruiter["name"],
        "recruiter_type": recruiter["type"],
        "recruiter_company": recruiter["company"],
        "recruiter_linkedin": recruiter.get("linkedin"),
        "hiring_company": record.get("hiring_company"),
        "industry": record["industry"],
        "country": record["country"],
        "tw_region": record.get("tw_region"),
        "role_family": record["role_family"],
        "seniority": record["seniority"],
        "channel": record["channel"],
        "period": record["period"],
        "stage_reached": record["stage_reached"],
        "ghosted": record["ghosted"],
        "salary_disclosed_upfront": record["salary_disclosed_upfront"],
        "would_engage_again": record["would_engage_again"],
        "summary": record["summary"],
        "source": record["source"],
        "status": record["status"],
    }
    flattened["recruiter_key"] = (
        f"{recruiter['name']}|{recruiter['company']}".lower()
    )
    for dimension in DIMENSIONS:
        flattened[f"score_{dimension}"] = record["scores"][dimension]
    flattened["score_avg"] = round(
        sum(record["scores"][dimension] for dimension in DIMENSIONS) / len(DIMENSIONS),
        2,
    )
    return flattened


def labels(mapping: dict) -> dict[str, str]:
    return {key: value["label_zh"] for key, value in mapping.items()}


def main() -> int:
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    records = [flatten(record) for record in read_records()]
    with (ROOT / "taxonomy" / "enums.yaml").open(encoding="utf-8") as handle:
        enums = yaml.safe_load(handle)
    taxonomy = {}
    for filename, output_key in (
        ("industries.yaml", "industries"),
        ("countries.yaml", "countries"),
        ("tw_regions.yaml", "tw_regions"),
        ("role_families.yaml", "role_families"),
    ):
        with (ROOT / "taxonomy" / filename).open(encoding="utf-8") as handle:
            taxonomy[output_key] = labels(yaml.safe_load(handle))
    for key in (
        "recruiter_type",
        "seniority",
        "channel",
        "stage_reached",
        "score_dimensions",
    ):
        taxonomy[key] = labels(enums[key])

    aggregates: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        aggregates[record["recruiter_key"]].append(record)
    recruiters = []
    for key, group in sorted(aggregates.items()):
        def average(field: str) -> float:
            return round(sum(item[field] for item in group) / len(group), 2)

        averages = {
            dimension: average(f"score_{dimension}") for dimension in DIMENSIONS
        }
        aggregate = {
            "recruiter_key": key,
            "name": group[0]["recruiter_name"],
            "company": group[0]["recruiter_company"],
            "type": group[0]["recruiter_type"],
            "review_count": len(group),
            "avg": averages,
            "avg_overall": round(sum(item["score_avg"] for item in group) / len(group), 2),
            "ghosted_rate": round(
                sum(1 for item in group if item["ghosted"]) / len(group), 2
            ),
            "latest_period": max(item["period"] for item in group),
        }
        aggregate.update({f"avg_{dimension}": value for dimension, value in averages.items()})
        recruiters.append(aggregate)

    def write(name: str, value) -> None:
        with (OUTPUT_PATH / name).open("w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    write(
        "index.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "count": len(records),
            "reviews": records,
        },
    )
    write("taxonomy.json", taxonomy)
    write("recruiters.json", recruiters)
    print(f"索引建置成功：{len(records)} 筆 published review，{len(recruiters)} 位 recruiter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
