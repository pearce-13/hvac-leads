# HVAC Lead Generator

This project pulls HVAC business leads from the **Google Places API** into `leads_raw.csv`, then scores and prioritizes them into `prioritized_leads.csv`.

## What it does

1. Calls Google Places Text Search API using your query.
2. Saves raw lead data to `leads_raw.csv`.
3. Applies a scoring model (rating, review volume, HVAC keyword relevance, business status).
4. Writes ranked results to `prioritized_leads.csv` with `lead_score` and `priority`.

## Prerequisites

- Python 3.10+
- A Google Places API key with billing enabled

## Setup

1. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Set your API key as an environment variable:

   ```bash
   export GOOGLE_PLACES_API_KEY="your_real_google_places_api_key"
   ```

   You can also copy `.env.example` and load it in your shell environment.

> API keys are read from environment variables and are never hardcoded in source code.

## Usage

### 1) Generate raw leads

```bash
python generate_leads.py --query "HVAC contractors in Austin, TX" --output leads_raw.csv --max-results 60
```

### 2) Score and prioritize leads

```bash
python prioritize_leads.py --input leads_raw.csv --output prioritized_leads.csv
```

## Output columns

### `leads_raw.csv`
- `place_id`
- `name`
- `formatted_address`
- `rating`
- `user_ratings_total`
- `business_status`
- `types`
- `lat`
- `lng`

### `prioritized_leads.csv`
All raw columns plus:
- `rating_score`
- `review_volume_score`
- `keyword_score`
- `status_score`
- `lead_score`
- `priority` (`High`, `Medium`, `Low`)

## Notes

- Google Places Text Search typically returns up to 60 results via pagination.
- You can tune scoring in `src/hvac_leads/scoring.py` to fit your sales strategy.
