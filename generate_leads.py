from __future__ import annotations

import argparse

from src.hvac_leads.google_places import fetch_and_save_raw_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch leads from Google Places API and save them as leads_raw.csv"
    )
    parser.add_argument(
        "--query",
        default="HVAC contractors in Austin, TX",
        help="Google Places text search query.",
    )
    parser.add_argument("--output", default="leads_raw.csv", help="Output CSV path.")
    parser.add_argument(
        "--max-results",
        type=int,
        default=60,
        help="Maximum leads to fetch (Google returns up to 60 for text search).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = fetch_and_save_raw_csv(args.query, args.output, args.max_results)
    print(f"Saved {len(records)} leads to {args.output}")


if __name__ == "__main__":
    main()
