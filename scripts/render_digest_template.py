#!/usr/bin/env python3
"""Render a markdown template for the X 129 watchlist briefing."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


CN_TZ = ZoneInfo("Asia/Shanghai")
SKILL_DIR = Path(__file__).resolve().parents[1]
WATCHLIST_PATH = SKILL_DIR / "references" / "watchlist.json"


def load_watchlist() -> dict:
    return json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))


def parse_dt(value: str | None, fallback_tz: ZoneInfo) -> datetime | None:
    if value is None:
        return None
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=fallback_tz)
    return dt.astimezone(fallback_tz)


def sector_counts(data: dict) -> list[tuple[str, str, int]]:
    return [
        (sector["id"], sector["label"], len(sector["accounts"]))
        for sector in data["sectors"]
    ]


def build_template(data: dict, start_cn: datetime, end_cn: datetime) -> str:
    generated_at = datetime.now(tz=CN_TZ).strftime("%Y-%m-%d %H:%M")
    window = (
        f"{start_cn.strftime('%Y-%m-%d %H:%M')} ~ "
        f"{end_cn.strftime('%Y-%m-%d %H:%M')} (北京时间)"
    )
    total_entries = sum(len(sector["accounts"]) for sector in data["sectors"])
    unique_handles = len(
        {
            account["handle"].lower()
            for sector in data["sectors"]
            for account in sector["accounts"]
        }
    )
    sectors = sector_counts(data)

    lines = [
        f"# {data['title']}",
        "",
        f"生成时间：{generated_at}（北京时间）",
        f"统计窗口：{window}",
        f"账号池：{total_entries} 条目，{unique_handles} 个去重 handle",
        "",
        "## ① 一句话速览（3-8 条）",
        "",
        "1. **[核心结论]**",
        "   - 事实：",
        "   - 观点/判断：",
        "   - 为什么重要：",
        "   - 来源：",
        "",
    ]

    section_number = 2
    for _, label, count in sectors:
        circled = chr(9311 + section_number)
        lines.extend(
            [
                f"## {circled} {label}（{count} 条目）",
                "",
                "### [主题或账号]",
                "- 结论：",
                "- 事实：",
                "- 观点/判断：",
                "- 为什么重要：",
                "- 来源：",
                "",
            ]
        )
        section_number += 1

    lines.extend(
        [
            f"## {chr(9311 + section_number)} 跨领域信号",
            "",
            "1. [本窗口跨领域共同趋势]",
            "2. [值得继续跟踪的分发/产品/变现变化]",
            "3. [需要警惕的噪音或风险]",
            "",
            f"## {chr(9311 + section_number + 1)} 本窗口无公开更新 / 无高价值更新账号",
            "",
            "- @example_handle",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render markdown template for the X 129 watchlist briefing."
    )
    parser.add_argument(
        "--start",
        help="Start time in ISO-8601. If omitted, derive from --hours.",
    )
    parser.add_argument(
        "--end",
        help="End time in ISO-8601. Defaults to current Beijing time.",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=48,
        help="Window size in hours when --start is omitted. Default: 48.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Write template to this file. If omitted, print to stdout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_watchlist()
    end_cn = parse_dt(args.end, CN_TZ) or datetime.now(tz=CN_TZ)
    start_cn = parse_dt(args.start, CN_TZ)
    if start_cn is None:
        start_cn = end_cn - timedelta(hours=args.hours)
    if start_cn > end_cn:
        raise SystemExit("start time cannot be later than end time")

    content = build_template(data, start_cn, end_cn)
    if args.out:
        args.out.write_text(content, encoding="utf-8")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
