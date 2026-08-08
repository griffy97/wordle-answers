"""
seed.py — Run once to populate answers.json with the full Wordle history.

Fetches every puzzle from the NYT Wordle API (June 19, 2021 → today).
Dates that return 404 are skipped gracefully.

Usage:
    pip install requests
    python seed.py
"""

import json
import time
from datetime import date, timedelta

import requests


NYT_URL = "https://www.nytimes.com/svc/wordle/v2/{date}.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT = "answers.json"
START = date(2021, 6, 19)


def fetch(target: date, session: requests.Session) -> dict | None:
    r = session.get(NYT_URL.format(date=target.isoformat()), headers=HEADERS, timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    data = r.json()
    return {"word": data["solution"].lower(), "date": data["print_date"]}


def main() -> None:
    session = requests.Session()
    answers = []
    today = date.today()
    total_days = (today - START).days + 1
    skipped = 0

    print(f"Fetching {total_days} dates ({START} → {today})...\n")

    d = START
    while d <= today:
        try:
            entry = fetch(d, session)
            if entry:
                answers.append(entry)
                print(f"  {entry['date']}  {entry['word']}")
            else:
                skipped += 1
        except Exception as e:
            print(f"  {d}  ERROR: {e}")
            skipped += 1
        d += timedelta(days=1)
        time.sleep(0.3)

    answers.sort(key=lambda x: x["date"])

    with open(OUTPUT, "w") as f:
        json.dump(answers, f)

    print(f"\nDone. {len(answers)} answers written to {OUTPUT} ({skipped} skipped).")


if __name__ == "__main__":
    main()
