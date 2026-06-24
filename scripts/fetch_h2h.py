#!/usr/bin/env python3
"""
Fetch historical head-to-head record between two national teams.

Usage:
    python3 fetch_h2h.py --team1 "Argentina" --team2 "Brazil"

Environment variables:
    API_FOOTBALL_KEY - api key for api-football.com (supports H2H endpoint)

Without an API key, the script prints a web search query template and sample data.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def _load_dotenv():
    """Load environment variables from .env next to SKILL.md."""
    skill_dir = Path(__file__).resolve().parent.parent
    env_file = skill_dir / ".env"
    if env_file.exists():
        with env_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value


_load_dotenv()


def http_get(url, headers=None, timeout=20):
    req = Request(url, headers=headers or {})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except HTTPError as e:
        return json.dumps({"error": f"HTTP {e.code}: {e.reason}", "url": url})
    except URLError as e:
        return json.dumps({"error": f"URL error: {e.reason}", "url": url})


def main():
    parser = argparse.ArgumentParser(description="Fetch H2H record")
    parser.add_argument("--team1", required=True)
    parser.add_argument("--team2", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    key = os.environ.get("API_FOOTBALL_KEY")
    result = {
        "team1": args.team1,
        "team2": args.team2,
        "api_key_available": bool(key),
    }

    if key:
        # API-Football v3 H2H endpoint
        url = f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={quote(args.team1)}-{quote(args.team2)}&last=10"
        data = http_get(url, headers={"x-apisports-key": key})
        try:
            result["api_response"] = json.loads(data)
        except json.JSONDecodeError:
            result["api_response"] = {"raw": data[:1000]}
    else:
        result["note"] = "No API_FOOTBALL_KEY provided. Use web search fallback."
        result["web_search_queries"] = [
            f"{args.team1} vs {args.team2} head to head",
            f"{args.team1} {args.team2} all matches history",
            f"{args.team1} vs {args.team2} World Cup history",
        ]
        result["sample_matches"] = [
            {"competition": "FIFA World Cup", "date": "2022-12-18", "score": f"{args.team1} 3-3 {args.team2} (penalties 4-2)"},
            {"competition": "Friendly", "date": "2019-11-15", "score": f"{args.team1} 1-0 {args.team2}"},
        ]

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"Head-to-Head: {args.team1} vs {args.team2}")
    if not key:
        print("No API_FOOTBALL_KEY found; use web search with these queries:")
        for q in result["web_search_queries"]:
            print(f"  - {q}")
    if "api_response" in result:
        print(json.dumps(result["api_response"], indent=2, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()
