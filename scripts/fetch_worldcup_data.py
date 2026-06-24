#!/usr/bin/env python3
"""
Fetch current FIFA World Cup data: standings, fixtures, results, and rankings.

Usage:
    python3 fetch_worldcup_data.py [--group A] [--team "Argentina"] [--fixtures]

Environment variables:
    FOOTBALL_DATA_API_KEY - api key for football-data.org (free tier available)
    API_FOOTBALL_KEY      - api key for api-football.com

If no API key is available, the script prints the best free/public endpoints
and returns sample data so the skill can fall back to web search.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
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

# Public / free endpoints
FIFA_RANKINGS_URL = "https://inside.fifa.com/api/ranking-table?locale=en&dateId=current"
FOOTBALL_DATA_WC = "https://api.football-data.org/v4/competitions/WC/matches"
FOOTBALL_DATA_STANDINGS = "https://api.football-data.org/v4/competitions/WC/standings"

# Cache configuration
CACHE_DIR = Path.home() / ".cache" / "world-cup-predictor"
CACHE_FILE = CACHE_DIR / "api_cache.json"
CACHE_TTL_SECONDS = int(os.environ.get("WCP_CACHE_TTL", "300"))


def _cache_path():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_FILE


def _load_cache():
    try:
        with _cache_path().open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(cache):
    try:
        with _cache_path().open("w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def cached_fetch(fetch_func, endpoint, api_key=None):
    """Fetch with simple file-based caching."""
    now = datetime.now(timezone.utc).timestamp()
    cache = _load_cache()
    entry = cache.get(endpoint)
    if entry and (now - entry.get("ts", 0)) < CACHE_TTL_SECONDS:
        return entry["data"]

    if api_key:
        data = fetch_func(endpoint, api_key)
    else:
        data = fetch_func(endpoint)

    try:
        parsed = json.loads(data) if isinstance(data, str) else data
    except Exception:
        parsed = data

    cache[endpoint] = {"ts": now, "data": parsed}
    _save_cache(cache)
    return parsed

SAMPLE_STANDINGS = {
    "note": "SAMPLE DATA - provide API key or use web search for live data",
    "groups": {
        "A": [
            {"team": "Netherlands", "played": 3, "won": 2, "drawn": 1, "lost": 0, "gf": 5, "ga": 1, "gd": 4, "points": 7},
            {"team": "Senegal", "played": 3, "won": 2, "drawn": 0, "lost": 1, "gf": 5, "ga": 4, "gd": 1, "points": 6},
            {"team": "Ecuador", "played": 3, "won": 1, "drawn": 1, "lost": 1, "gf": 4, "ga": 3, "gd": 1, "points": 4},
            {"team": "Qatar", "played": 3, "won": 0, "drawn": 0, "lost": 3, "gf": 1, "ga": 7, "gd": -6, "points": 0},
        ]
    }
}


def http_get(url, headers=None, timeout=20):
    req = Request(url, headers=headers or {})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except HTTPError as e:
        return json.dumps({"error": f"HTTP {e.code}: {e.reason}", "url": url})
    except URLError as e:
        return json.dumps({"error": f"URL error: {e.reason}", "url": url})


def fetch_football_data(endpoint, api_key):
    headers = {"X-Auth-Token": api_key}
    return http_get(endpoint, headers)


def fetch_fifa_rankings():
    data = http_get(FIFA_RANKINGS_URL)
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        parsed = {"error": "Unable to parse FIFA rankings", "raw": data[:500]}
    return parsed


def normalize_rankings(parsed):
    """Extract team->points mapping from FIFA API response shapes."""
    mapping = {}
    if isinstance(parsed, dict):
        items = parsed.get("rankings") or parsed.get("items") or parsed.get("data") or []
    elif isinstance(parsed, list):
        items = parsed
    else:
        items = []
    for item in items:
        name = item.get("team", {}).get("name") or item.get("teamName") or item.get("country")
        points = item.get("points") or item.get("totalPoints")
        if name and points is not None:
            mapping[name] = int(points)
    return mapping


def main():
    parser = argparse.ArgumentParser(description="Fetch World Cup data")
    parser.add_argument("--group", help="Filter standings by group letter")
    parser.add_argument("--team", help="Filter fixtures/results by team name")
    parser.add_argument("--fixtures", action="store_true", help="Show upcoming fixtures")
    parser.add_argument("--results", action="store_true", help="Show finished results")
    parser.add_argument("--rankings", action="store_true", help="Show FIFA rankings")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    fd_key = os.environ.get("FOOTBALL_DATA_API_KEY")
    af_key = os.environ.get("API_FOOTBALL_KEY")

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "keys_available": {"football_data": bool(fd_key), "api_football": bool(af_key)},
    }

    # Standings
    if fd_key:
        output["standings"] = cached_fetch(fetch_football_data, FOOTBALL_DATA_STANDINGS, fd_key)
    else:
        output["standings"] = SAMPLE_STANDINGS

    # Fixtures / results
    if fd_key:
        output["matches"] = cached_fetch(fetch_football_data, FOOTBALL_DATA_WC, fd_key)
    else:
        output["matches"] = {
            "note": "SAMPLE DATA - provide FOOTBALL_DATA_API_KEY for live fixtures",
            "matches": [
                {"homeTeam": "Argentina", "awayTeam": "France", "status": "SCHEDULED", "stage": "FINAL"}
            ]
        }

    # Rankings
    rankings_raw = fetch_fifa_rankings()
    try:
        rankings_parsed = json.loads(rankings_raw) if isinstance(rankings_raw, str) else rankings_raw
    except json.JSONDecodeError:
        rankings_parsed = {"error": "FIFA rankings parse failed"}
    output["rankings"] = rankings_parsed
    output["ranking_map"] = normalize_rankings(rankings_parsed)

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    # Human-readable summary
    print(f"World Cup Data Fetch ({output['timestamp']})")
    print("=" * 50)
    if not fd_key and not af_key:
        print("No API keys found. Set FOOTBALL_DATA_API_KEY or API_FOOTBALL_KEY for live data.")
        print("Fallback: use web search for current standings/fixtures/rankings.\n")

    rankings = output.get("ranking_map", {})
    if rankings:
        print("Top 10 FIFA Rankings (points):")
        for team, pts in sorted(rankings.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {team}: {pts}")
        print()

    # Normalize standings to {group: [rows]}
    def _team_name(obj):
        return obj.get("name") if isinstance(obj, dict) else obj

    def _normalize_standings(raw):
        groups = {}
        # Sample data shape
        if isinstance(raw, dict) and "groups" in raw:
            for grp, rows in raw["groups"].items():
                groups[grp] = rows
            return groups
        # football-data.org shape: standings is a list
        if isinstance(raw, dict) and "standings" in raw and isinstance(raw["standings"], list):
            for entry in raw["standings"]:
                grp = entry.get("group", "?").replace("Group ", "")
                rows = []
                for r in entry.get("table", []):
                    rows.append({
                        "team": _team_name(r.get("team", {})),
                        "played": r.get("playedGames", 0),
                        "won": r.get("won", 0),
                        "drawn": r.get("draw", 0),
                        "lost": r.get("lost", 0),
                        "gf": r.get("goalsFor", 0),
                        "ga": r.get("goalsAgainst", 0),
                        "gd": r.get("goalDifference", 0),
                        "points": r.get("points", 0),
                    })
                groups[grp] = rows
            return groups
        return groups

    groups = _normalize_standings(output.get("standings", {}))
    if groups:
        print("Group Standings:")
        for grp in sorted(groups.keys()):
            if args.group and grp.upper() != args.group.upper():
                continue
            print(f"  Group {grp}:")
            for r in groups[grp]:
                print(f"    {r['team']:<20} P{r['played']} W{r['won']} D{r['drawn']} L{r['lost']} "
                      f"GF{r['gf']} GA{r['ga']} GD{r['gd']:+d} PTS{r['points']}")
        print()

    matches = output.get("matches", {})
    match_list = matches.get("matches", [])
    if args.team:
        match_list = [m for m in match_list if args.team.lower() in
                      (_team_name(m.get("homeTeam", {})).lower(),
                       _team_name(m.get("awayTeam", {})).lower())]
    if args.fixtures and match_list:
        upcoming = [m for m in match_list if m.get("status") in ("SCHEDULED", "TIMED", "IN_PLAY", "PAUSED")]
        print("Upcoming fixtures (filtered):")
        for m in upcoming[:15]:
            home = _team_name(m.get("homeTeam", {}))
            away = _team_name(m.get("awayTeam", {}))
            status = m.get("status", "SCHEDULED")
            stage = m.get("stage", "")
            utc = m.get("utcDate", "")
            matchday = m.get("matchday", "")
            print(f"  {home} vs {away} [{status}] {stage} MD{matchday} {utc}")
    if args.results and match_list:
        print("Results (filtered):")
        for m in match_list[:10]:
            if m.get("status") == "FINISHED":
                home = _team_name(m.get("homeTeam", {}))
                away = _team_name(m.get("awayTeam", {}))
                sc = m.get("score", {}).get("fullTime", {})
                home_goals = sc.get("home") if sc.get("home") is not None else "?"
                away_goals = sc.get("away") if sc.get("away") is not None else "?"
                print(f"  {home} {home_goals}-{away_goals} {away}")


if __name__ == "__main__":
    main()
