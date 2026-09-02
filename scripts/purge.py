#!/usr/bin/env python3
"""Permanently remove a review file and record an id-only tombstone."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REVIEWS_PATH = ROOT / "data" / "reviews"
REMOVED_PATH = ROOT / "data" / "removed.yaml"
REASONS = (
    "pii",
    "defamation_claim",
    "harassment",
    "fake",
    "requester",
    "legal",
)
REVIEW_ID_RE = re.compile(r"^rv-\d{6}-\d{6}$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, dest="review_id")
    parser.add_argument("--reason", required=True, choices=REASONS)
    parser.add_argument("--date", default=date.today().isoformat(), dest="removed_at")
    args = parser.parse_args()
    if not REVIEW_ID_RE.fullmatch(args.review_id):
        parser.error("--id 必須符合 rv-YYYYMM-NNNNNN")
    try:
        date.fromisoformat(args.removed_at)
    except ValueError:
        parser.error("--date 必須是 YYYY-MM-DD")

    with REMOVED_PATH.open(encoding="utf-8") as handle:
        tombstones = yaml.safe_load(handle) or []
    if any(item.get("id") == args.review_id for item in tombstones):
        parser.error(f"{args.review_id} 已是 tombstone，不能重複下架")
    matches = sorted(REVIEWS_PATH.glob(f"**/{args.review_id}.yaml"))
    if not matches:
        parser.error(f"找不到 review：{args.review_id}")
    if len(matches) > 1:
        parser.error(f"review id 不唯一：{args.review_id}")

    review_path = matches[0]
    review_path.unlink()
    tombstones.append(
        {"id": args.review_id, "removed_at": args.removed_at, "reason": args.reason}
    )
    tombstones.sort(key=lambda item: item["id"])
    with REMOVED_PATH.open("w", encoding="utf-8") as handle:
        handle.write("# 已下架紀錄的墓碑。只留 id，不留任何內容。id 永不重用。\n")
        yaml.safe_dump(tombstones, handle, allow_unicode=True, sort_keys=False)

    relative_review = review_path.relative_to(ROOT).as_posix()
    year = review_path.parent.name
    print(f"已刪除：{relative_review}")
    print("請依序執行以下命令清除 git history：")
    print('git add -A && git commit -m "Remove ' + args.review_id + '"')
    print(
        f"git filter-repo --invert-paths --path data/reviews/{year}/{args.review_id}.yaml --force"
    )
    print(
        "git remote add origin https://github.com/Carlping/awesome-recruiter.git   # filter-repo drops the remote"
    )
    print("git push --force --all origin && git push --force --tags origin")
    print(
        "並請透過 https://support.github.com/request 申請 GitHub 清除 cache 與 fork；"
        "文件：https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
