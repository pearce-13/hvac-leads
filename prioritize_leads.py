from __future__ import annotations

import argparse

from src.hvac_leads.scoring import score_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score and prioritize leads from leads_raw.csv into prioritized_leads.csv"
    )
    parser.add_argument("--input", default="leads_raw.csv", help="Input CSV path.")
    parser.add_argument("--output", default="prioritized_leads.csv", help="Output CSV path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = score_csv(args.input, args.output)
    print(f"Saved {len(frame)} prioritized leads to {args.output}")


if __name__ == "__main__":
    main()
