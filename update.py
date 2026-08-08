"""
update.py — Called daily by the GitHub Action (19:01 UTC = 12:01 PDT) to append answers.

Fetches today and the last 6 days that are not yet in answers.json.
The 7-day window recovers from Action failures without re-checking older history.
"""

import json
import sys
from datetime import date, timedelta

import requests


NYT_URL = "https://www.nytimes.com/svc/wordle/v2/{date}.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT = "answers.json"


def fetch(target: str) -> dict | None:
    r = requests.get(NYT_URL.format(date=target), headers=HEADERS, timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    data = r.json()
    return {"word": data["solution"].lower(), "date": data["print_date"]}


def main() -> None:
    with open(OUTPUT) as f:
        answers = json.load(f)

    existing = {a["date"] for a in answers}
    today = date.today()

    # Check today and up to 6 days back (handles missed Action runs).
    candidates = [
        (today - timedelta(days=i)).isoformat()
        for i in range(0, 7)
        if (today - timedelta(days=i)).isoformat() not in existing
    ]

    added = 0
    for target in candidates:
        try:
            entry = fetch(target)
            if entry and entry["date"] not in existing:
                answers.append(entry)
                existing.add(entry["date"])
                added += 1
                print(f"Added: {entry['date']} = {entry['word']}")
        except Exception as e:
            print(f"Skipped {target}: {e}", file=sys.stderr)

    if added > 0:
        answers.sort(key=lambda x: x["date"])
        with open(OUTPUT, "w") as f:
            json.dump(answers, f)
        print(f"answers.json updated ({added} new {'entry' if added == 1 else 'entries'}).")
    else:
        print("answers.json is already up to date.")


if __name__ == "__main__":
    main()
