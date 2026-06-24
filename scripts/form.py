#!/usr/bin/env python3
"""
Team form calculator based on recent finished matches.

Usage:
    python3 form.py "Argentina"
    python3 form.py "Mexico" --n 5 --json

Reads finished matches from the current World Cup data fetched via
fetch_worldcup_data.py. Returns a form score that can be added to an
Elo-like rating.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


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


def _team_name(obj):
    return obj.get("name") if isinstance(obj, dict) else str(obj)


def _normalize(name):
    """Normalize team name for matching."""
    return name.lower().replace(" ", "").replace("-", "")


def fetch_current_matches():
    """Fetch current World Cup finished matches via fetch_worldcup_data.py."""
    script = Path(__file__).resolve().parent / "fetch_worldcup_data.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True, text=True, timeout=45
        )
        data = json.loads(result.stdout)
        return data.get("matches", {}).get("matches", [])
    except Exception:
        return []


def calculate_form(team_name, matches=None, n=5):
    """
    Calculate recent form for a team from finished matches.

    Returns a dict with:
      - form_score: Elo adjustment (-50 to +50)
      - last_matches: list of recent results
      - wins, draws, losses
      - gf, ga, gd
    """
    if matches is None:
        matches = fetch_current_matches()

    team_norm = _normalize(team_name)
    results = []
    for m in matches:
        if m.get("status") != "FINISHED":
            continue
        home = _team_name(m.get("homeTeam", {}))
        away = _team_name(m.get("awayTeam", {}))
        is_home = team_norm in _normalize(home)
        is_away = team_norm in _normalize(away)
        if not (is_home or is_away):
            continue

        score = m.get("score", {}).get("fullTime", {})
        hg = score.get("home", 0) or 0
        ag = score.get("away", 0) or 0

        if is_home:
            team_goals, opp_goals = hg, ag
            opponent = away
            venue = "H"
        else:
            team_goals, opp_goals = ag, hg
            opponent = home
            venue = "A"

        if team_goals > opp_goals:
            outcome = "W"
        elif team_goals == opp_goals:
            outcome = "D"
        else:
            outcome = "L"

        results.append({
            "opponent": opponent,
            "venue": venue,
            "outcome": outcome,
            "team_goals": team_goals,
            "opp_goals": opp_goals,
            "gd": team_goals - opp_goals,
            "competition": m.get("competition", {}).get("name", "World Cup"),
            "date": m.get("utcDate", ""),
        })

    # Sort by date descending and take last n
    results.sort(key=lambda x: x.get("date", ""), reverse=True)
    recent = results[:n]

    wins = sum(1 for r in recent if r["outcome"] == "W")
    draws = sum(1 for r in recent if r["outcome"] == "D")
    losses = sum(1 for r in recent if r["outcome"] == "L")
    gf = sum(r["team_goals"] for r in recent)
    ga = sum(r["opp_goals"] for r in recent)
    gd = gf - ga

    # Base form from W/D/L
    base = wins * 12 + draws * 0 - losses * 12
    # Goal difference bonus/penalty (capped)
    gd_bonus = max(-15, min(15, gd * 3))
    # Scale by number of matches (fewer matches = less confident)
    confidence = min(1.0, len(recent) / 5.0)
    form_score = round((base + gd_bonus) * confidence)
    # Hard cap
    form_score = max(-50, min(50, form_score))

    return {
        "team": team_name,
        "matches_considered": len(recent),
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "gf": gf,
        "ga": ga,
        "gd": gd,
        "form_score": form_score,
        "last_matches": recent,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate team form")
    parser.add_argument("team", help="Team name")
    parser.add_argument("--n", type=int, default=5, help="Number of recent matches")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = calculate_form(args.team, n=args.n)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"Team: {result['team']}")
    print(f"Recent form (last {result['matches_considered']} matches): "
          f"W{result['wins']} D{result['draws']} L{result['losses']} "
          f"GF{result['gf']} GA{result['ga']} GD{result['gd']:+d}")
    print(f"Form Elo adjustment: {result['form_score']:+d}")
    print("\nLast matches:")
    for m in result["last_matches"]:
        print(f"  {m['date'][:10]} {m['venue']} {m['outcome']} vs {m['opponent']} "
              f"({m['team_goals']}-{m['opp_goals']})")


if __name__ == "__main__":
    main()
