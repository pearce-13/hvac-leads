from __future__ import annotations

import csv
import math
from pathlib import Path

HIGH_INTENT_KEYWORDS = {
    "hvac",
    "air conditioning",
    "furnace",
    "heating",
    "ac repair",
    "contractor",
    "mechanical",
}


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value: str) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _keyword_score(name: str, types: str) -> float:
    searchable = f"{name} {types}".lower()
    matches = sum(1 for keyword in HIGH_INTENT_KEYWORDS if keyword in searchable)
    return min(matches * 1.5, 10)


def _rating_score(rating: float) -> float:
    return max(0.0, min(rating, 5.0)) * 7


def _review_volume_score(review_count: int) -> float:
    if review_count <= 0:
        return 0.0
    return min(math.log10(review_count + 1) * 15, 30)


def _business_status_score(status: str) -> float:
    normalized = (status or "").upper()
    if normalized == "OPERATIONAL":
        return 10.0
    if normalized == "CLOSED_TEMPORARILY":
        return 3.0
    return 0.0


def _priority_bucket(score: float) -> str:
    if score >= 60:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def score_csv(input_csv: str, output_csv: str) -> list[dict[str, str]]:
    with open(input_csv, newline="", encoding="utf-8") as infile:
        rows = list(csv.DictReader(infile))

    scored_rows: list[dict[str, str]] = []
    for row in rows:
        rating = _to_float(row.get("rating", "0"))
        review_count = _to_int(row.get("user_ratings_total", "0"))
        keyword_score = _keyword_score(row.get("name", ""), row.get("types", ""))
        rating_score = _rating_score(rating)
        review_volume_score = _review_volume_score(review_count)
        status_score = _business_status_score(row.get("business_status", ""))

        lead_score = round(rating_score + review_volume_score + keyword_score + status_score, 2)
        row["rating_score"] = f"{rating_score:.2f}"
        row["review_volume_score"] = f"{review_volume_score:.2f}"
        row["keyword_score"] = f"{keyword_score:.2f}"
        row["status_score"] = f"{status_score:.2f}"
        row["lead_score"] = f"{lead_score:.2f}"
        row["priority"] = _priority_bucket(lead_score)
        scored_rows.append(row)

    scored_rows.sort(key=lambda item: float(item["lead_score"]), reverse=True)

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(scored_rows[0].keys()) if scored_rows else []

    with output_path.open("w", newline="", encoding="utf-8") as outfile:
        if fieldnames:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(scored_rows)

    return scored_rows
