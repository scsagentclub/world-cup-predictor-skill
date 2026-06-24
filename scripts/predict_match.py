#!/usr/bin/env python3
"""
Predict a FIFA World Cup match outcome using a lightweight Elo-derived model.

Usage:
    python3 predict_match.py --team1 "Argentina" --team2 "France" [--fifa1 1855 --fifa2 1840]
    python3 predict_match.py --team1 "Brazil" --team2 "Germany" --knockout

If FIFA points are omitted, the script attempts to read them from the output of
fetch_worldcup_data.py or uses placeholder estimates.
"""

import argparse
import json
import math
import os
import subprocess
import sys
from itertools import product
from pathlib import Path

# Import form calculator from sibling module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from form import calculate_form


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

AVG_TOTAL_GOALS = 2.65  # historical World Cup average per match
HOME_ADVANTAGE = 80
NEUTRAL_ADVANTAGE = 40
AWAY_PENALTY = -40

TEAM_ESTIMATES = {
    # Fallback estimates when live rankings unavailable (FIFA ranking points, approx scale 1000-1900)
    "argentina": 1855, "france": 1840, "spain": 1825, "england": 1810, "brazil": 1800,
    "portugal": 1780, "netherlands": 1760, "belgium": 1750, "germany": 1740, "croatia": 1730,
    "italy": 1725, "uruguay": 1710, "morocco": 1700, "colombia": 1695, "japan": 1660,
    "mexico": 1660, "usa": 1650, "iran": 1640, "denmark": 1640, "senegal": 1635,
    "serbia": 1630, "switzerland": 1625, "australia": 1610, "korea republic": 1610,
    "south korea": 1610, "poland": 1605, "ecuador": 1600, "ukraine": 1600, "qatar": 1400,
}


def fifa_to_elo(fifa_points):
    """Convert FIFA ranking points to an Elo-like scale centered near 1600."""
    return 1600 + (fifa_points - 1300) / 6.0


def fetch_data():
    """Try to load current rankings and matches from the fetch script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fetch_script = os.path.join(script_dir, "fetch_worldcup_data.py")
    try:
        result = subprocess.run(
            [sys.executable, fetch_script, "--json"],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        return data.get("ranking_map", {}), data.get("matches", {}).get("matches", [])
    except Exception:
        return {}, []


def get_fifa_points(team_name, ranking_map, override=None):
    if override is not None:
        return override
    for name, pts in ranking_map.items():
        if team_name.lower() in name.lower() or name.lower() in team_name.lower():
            return pts
    return TEAM_ESTIMATES.get(team_name.lower(), 1500)


def poisson_pmf(lam, k):
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def predict(team1, team2, fifa1=None, fifa2=None, knockout=False, venue="neutral",
            form1=None, form2=None, auto_form=True, matches=None):
    ranking_map, fetched_matches = fetch_data()
    p1 = get_fifa_points(team1, ranking_map, fifa1)
    p2 = get_fifa_points(team2, ranking_map, fifa2)

    # Auto-calculate form from recent matches if not explicitly provided
    form_info1 = form_info2 = None
    if auto_form and matches is None:
        matches = fetched_matches
    if auto_form and form1 is None:
        form_info1 = calculate_form(team1, matches=matches)
        form1 = form_info1["form_score"]
    elif form1 is None:
        form1 = 0
    if auto_form and form2 is None:
        form_info2 = calculate_form(team2, matches=matches)
        form2 = form_info2["form_score"]
    elif form2 is None:
        form2 = 0

    r1 = fifa_to_elo(p1) + form1
    r2 = fifa_to_elo(p2) + form2

    if venue == "home":
        r1 += HOME_ADVANTAGE
    elif venue == "away":
        r1 += AWAY_PENALTY
    else:
        r1 += NEUTRAL_ADVANTAGE
        r2 += NEUTRAL_ADVANTAGE

    we1 = 1.0 / (1.0 + 10.0 ** ((r2 - r1) / 400.0))

    # Expected goals per team
    lambda1 = max(0.3, AVG_TOTAL_GOALS * we1)
    lambda2 = max(0.3, AVG_TOTAL_GOALS * (1.0 - we1))

    # Compute outcome probabilities
    max_goals = 7
    dist1 = [poisson_pmf(lambda1, k) for k in range(max_goals + 1)]
    dist2 = [poisson_pmf(lambda2, k) for k in range(max_goals + 1)]

    win1 = draw = win2 = 0.0
    matrix = {}
    for i, pi in enumerate(dist1):
        for j, pj in enumerate(dist2):
            p = pi * pj
            matrix[(i, j)] = p
            if i > j:
                win1 += p
            elif i == j:
                draw += p
            else:
                win2 += p

    # Tail beyond max_goals approximated by mass at max_goals boundary
    tail = 1.0 - sum(dist1) * sum(dist2)
    if tail > 0:
        win1 += tail * we1
        win2 += tail * (1 - we1 - draw / (win1 + draw + win2)) if (win1 + draw + win2) > 0 else 0

    # Most likely scoreline
    best_score = max(matrix, key=matrix.get)

    return {
        "team1": team1,
        "team2": team2,
        "fifa_points": {"team1": p1, "team2": p2},
        "elo_equivalent": {"team1": round(r1, 1), "team2": round(r2, 1)},
        "expected_goals": {"team1": round(lambda1, 2), "team2": round(lambda2, 2)},
        "probabilities": {
            "team1_win": round(win1 * 100, 1),
            "draw": round(draw * 100, 1),
            "team2_win": round(win2 * 100, 1),
        },
        "most_likely_score": f"{best_score[0]}-{best_score[1]}",
        "knockout": knockout,
        "form": {
            "team1": form1,
            "team2": form2,
            "team1_details": form_info1,
            "team2_details": form_info2,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Predict a World Cup match")
    parser.add_argument("--team1", required=True)
    parser.add_argument("--team2", required=True)
    parser.add_argument("--fifa1", type=float)
    parser.add_argument("--fifa2", type=float)
    parser.add_argument("--knockout", action="store_true")
    parser.add_argument("--venue", choices=["home", "away", "neutral"], default="neutral")
    parser.add_argument("--form1", type=float, default=None, help="Manual form adjustment for team1 (-50 to +50)")
    parser.add_argument("--form2", type=float, default=None, help="Manual form adjustment for team2 (-50 to +50)")
    parser.add_argument("--no-auto-form", action="store_true", help="Disable automatic form calculation from recent matches")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = predict(
        args.team1, args.team2,
        fifa1=args.fifa1, fifa2=args.fifa2,
        knockout=args.knockout, venue=args.venue,
        form1=args.form1, form2=args.form2,
        auto_form=not args.no_auto_form
    )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    p = result["probabilities"]
    form = result.get("form", {})
    print(f"Match: {result['team1']} vs {result['team2']}")
    print(f"FIFA points: {result['team1']} {result['fifa_points']['team1']} | "
          f"{result['team2']} {result['fifa_points']['team2']}")
    if not args.no_auto_form:
        print(f"Form adjustment: {result['team1']} {form.get('team1', 0):+d} | "
              f"{result['team2']} {form.get('team2', 0):+d}")
    print(f"Elo estimates: {result['elo_equivalent']['team1']} vs {result['elo_equivalent']['team2']}")
    print(f"Expected goals: {result['expected_goals']['team1']} - {result['expected_goals']['team2']}")
    print(f"Predicted probabilities: {result['team1']} win {p['team1_win']}% | "
          f"Draw {p['draw']}% | {result['team2']} win {p['team2_win']}%")
    print(f"Most likely score (90 min): {result['most_likely_score']}")
    if args.knockout:
        print("Note: knockout-stage draws are resolved in extra time/penalties after 90 minutes.")


if __name__ == "__main__":
    main()
