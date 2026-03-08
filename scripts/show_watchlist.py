#!/usr/bin/env python3
"""Inspect the watchlist registry for the X 129 watchlist skill."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
WATCHLIST_PATH = SKILL_DIR / "references" / "watchlist.json"


def load_watchlist() -> dict:
    return json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))


def normalize_handle(handle: str) -> str:
    return handle.strip().lower().removeprefix("@")


def build_index(data: dict):
    by_handle: dict[str, dict[str, object]] = {}
    duplicates: dict[str, dict[str, object]] = defaultdict(
        lambda: {"names": set(), "sectors": [], "notes": []}
    )
    total_entries = 0

    for sector in data["sectors"]:
        for account in sector["accounts"]:
            total_entries += 1
            handle = normalize_handle(account["handle"])
            entry = by_handle.setdefault(
                handle,
                {"handle": handle, "names": set(), "sectors": set(), "notes": []},
            )
            entry["names"].add(account["name"])
            entry["sectors"].add(sector["id"])
            entry["notes"].append(account["note"])

            duplicates[handle]["names"].add(account["name"])
            duplicates[handle]["sectors"].append(sector["id"])
            duplicates[handle]["notes"].append(account["note"])

    repeated = {
        handle: info
        for handle, info in duplicates.items()
        if len(info["sectors"]) > 1
    }
    return total_entries, by_handle, repeated


def print_summary(data: dict) -> None:
    total_entries, by_handle, repeated = build_index(data)
    print(f"Title: {data['title']}")
    print(f"Updated at: {data['updated_at']}")
    print(f"Total entries: {total_entries}")
    print(f"Unique handles: {len(by_handle)}")
    print(f"Repeated handles: {len(repeated)}")
    print("Sectors:")
    for sector in data["sectors"]:
        print(f"- {sector['id']}: {sector['label']} ({len(sector['accounts'])})")


def print_sector(data: dict, sector_id: str) -> None:
    match = None
    for sector in data["sectors"]:
        if sector["id"] == sector_id:
            match = sector
            break
    if match is None:
        valid = ", ".join(sector["id"] for sector in data["sectors"])
        raise SystemExit(f"Unknown sector '{sector_id}'. Valid sectors: {valid}")

    print(f"{match['label']} ({len(match['accounts'])})")
    for index, account in enumerate(match["accounts"], start=1):
        print(f"{index:02d}. @{account['handle']} | {account['name']} | {account['note']}")


def print_duplicates(data: dict) -> None:
    _, _, repeated = build_index(data)
    if not repeated:
        print("No repeated handles found.")
        return

    for handle in sorted(repeated):
        info = repeated[handle]
        sectors = ", ".join(info["sectors"])
        names = "; ".join(sorted(info["names"]))
        print(f"@{handle} | sectors: {sectors} | names: {names}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect the X 129 watchlist registry.")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print overall counts and sector sizes. This is the default mode.",
    )
    parser.add_argument(
        "--sector",
        help="Print all accounts in a sector. Example: --sector ai",
    )
    parser.add_argument(
        "--duplicates",
        action="store_true",
        help="Print handles that appear in more than one sector.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_watchlist()

    if args.sector:
        print_sector(data, args.sector)
        return 0
    if args.duplicates:
        print_duplicates(data)
        return 0

    print_summary(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
