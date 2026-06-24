#!/usr/bin/env python3
"""
Monte Carlo simulation of World Cup group-stage advancement probabilities.

Usage:
    python3 simulate_group.py --group A
    python3 simulate_group.py --group A --n-simulations 20000 --json

Reads current standings and remaining fixtures from football-data.org.
"""

import argparse
import json
import math
import os
import random
import subprocess
import sys
from pathlib import Path

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

# Fallback team strength estimates (FIFA ranking points scale)
TEAM_ESTIMATES = {
    "argentina": 1855, "france": 1840, "spain": 1825, "england": 1810, "brazil": 1800,
    "portugal": 1780, "netherlands": 1760, "belgium": 1750, "germany": 1740, "croatia": 1730,
    "italy": 1725, "uruguay": 1710, "morocco": 1700, "colombia": 1695, "mexico": 1660,
    "japan": 1660, "usa": 1650, "iran": 1640, "denmark": 1640, "senegal": 1635,
    "serbia": 1630, "switzerland": 1625, "australia": 1610, "korea republic": 1610,
    "south korea": 1610, "poland": 1605, "ecuador": 1600, "ukraine": 1600, "canada": 1620,
    "qatar": 1400, "ghana": 1580, "ivory coast": 1560, "bosnia-herzegovina": 1550,
    "czechia": 1540, "turkey": 1590, "paraguay": 1530, "south africa": 1480, "haiti": 1450,
    "scotland": 1580, "sweden": 1570, "tunisia": 1540, "egypt": 1590, "new zealand": 1440,
    "saudi arabia": 1480, "cape verde islands": 1470, "norway": 1600, "iraq": 1460,
    "austria": 1590, "algeria": 1550, "jordan": 1450, "congo dr": 1490, "uzbekistan": 1500,
    "panama": 1520,
}


def _team_name(obj):
    return obj.get("name") if isinstance(obj, dict) else str(obj)


def _fifa_points(team_name, ranking_map=None):
    key = team_name.lower()
    if ranking_map and key in ranking_map:
        return ranking_map[key]
    for k, v in TEAM_ESTIMATES.items():
        if k in key or key in k:
            return v
    return 1500


def _elo(points):
    return 1600 + (points - 1300) / 6.0


def _match_probabilities(team1, team2, ranking_map=None, form_map=None):
    """Return (p1_win, draw, p2_win) for 90 minutes."""
    p1 = _fifa_points(team1, ranking_map)
    p2 = _fifa_points(team2, ranking_map)
    form1 = form_map.get(team1, 0) if form_map else 0
    form2 = form_map.get(team2, 0) if form_map else 0
    r1 = _elo(p1) + 40 + form1  # neutral venue + form
    r2 = _elo(p2) + 40 + form2
    we1 = 1.0 / (1.0 + 10.0 ** ((r2 - r1) / 400.0))
    lambda1 = max(0.3, 2.65 * we1)
    lambda2 = max(0.3, 2.65 * (1.0 - we1))

    # Precompute Poisson PMFs up to 7 goals
    def poisson(lam, k):
        return math.exp(-lam) * (lam ** k) / math.factorial(k)

    max_goals = 7
    d1 = [poisson(lambda1, k) for k in range(max_goals + 1)]
    d2 = [poisson(lambda2, k) for k in range(max_goals + 1)]

    win1 = draw = win2 = 0.0
    for i, pi in enumerate(d1):
        for j, pj in enumerate(d2):
            p = pi * pj
            if i > j:
                win1 += p
            elif i == j:
                draw += p
            else:
                win2 += p
    total = win1 + draw + win2
    if total > 0:
        return win1 / total, draw / total, win2 / total
    return 0.33, 0.34, 0.33


def _sample_score(team1, team2, ranking_map=None, form_map=None):
    """Sample a realistic scoreline given win/draw/loss probabilities."""
    p1, pd, p2 = _match_probabilities(team1, team2, ranking_map, form_map)
    r = random.random()
    if r < p1:
        outcome = "win1"
    elif r < p1 + pd:
        outcome = "draw"
    else:
        outcome = "win2"

    # Generate plausible scores
    if outcome == "draw":
        # Common draws: 0-0, 1-1, 2-2 weighted by Poisson expectation
        scores = [(0, 0), (1, 1), (2, 2), (3, 3)]
        weights = [0.35, 0.45, 0.15, 0.05]
        return random.choices(scores, weights=weights)[0]

    # Winner scores 1-3 goals, loser 0-2 depending on dominance
    we1 = p1 + 0.5 * pd
    dominance = abs(we1 - 0.5) * 2  # 0 to 1
    if outcome == "win1":
        winner_goals = random.choices([1, 2, 3, 4], weights=[0.25, 0.40, 0.25, 0.10])[0]
        loser_goals = random.choices([0, 1, 2], weights=[0.5 - 0.15 * dominance,
                                                         0.35 + 0.05 * dominance,
                                                         0.15 + 0.10 * dominance])[0]
        return (winner_goals, loser_goals)
    else:
        winner_goals = random.choices([1, 2, 3, 4], weights=[0.25, 0.40, 0.25, 0.10])[0]
        loser_goals = random.choices([0, 1, 2], weights=[0.5 - 0.15 * dominance,
                                                         0.35 + 0.05 * dominance,
                                                         0.15 + 0.10 * dominance])[0]
        return (loser_goals, winner_goals)


def _fetch_data():
    """Fetch current World Cup standings and matches via fetch_worldcup_data.py."""
    script = Path(__file__).resolve().parent / "fetch_worldcup_data.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True, text=True, timeout=45
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}


def _normalize_group_label(raw):
    """Normalize group labels like 'Group C', 'GROUP_C', 'C' to 'C'."""
    raw = (raw or "").upper().replace("GROUP", "").replace("_", "").replace(" ", "").strip()
    return raw


def _extract_group(data, group_letter):
    """Return (teams dict, finished matches, remaining matches) for a group."""
    target = group_letter.upper()
    standings = data.get("standings", {})
    groups = {}
    if isinstance(standings, dict) and "standings" in standings:
        standings = standings["standings"]
    if isinstance(standings, list):
        for entry in standings:
            grp = _normalize_group_label(entry.get("group", ""))
            if grp == target:
                for row in entry.get("table", []):
                    team = _team_name(row.get("team", {}))
                    groups[team] = {
                        "points": row.get("points", 0),
                        "gf": row.get("goalsFor", 0),
                        "ga": row.get("goalsAgainst", 0),
                        "gd": row.get("goalDifference", 0),
                        "won": row.get("won", 0),
                        "draw": row.get("draw", 0),
                        "lost": row.get("lost", 0),
                    }

    matches = data.get("matches", {}).get("matches", [])
    finished = []
    remaining = []
    for m in matches:
        grp = _normalize_group_label(m.get("group"))
        if grp != target:
            continue
        home = _team_name(m.get("homeTeam", {}))
        away = _team_name(m.get("awayTeam", {}))
        if m.get("status") == "FINISHED":
            score = m.get("score", {}).get("fullTime", {})
            finished.append({
                "home": home, "away": away,
                "home_goals": score.get("home", 0),
                "away_goals": score.get("away", 0),
            })
        elif m.get("status") in ("SCHEDULED", "TIMED", "IN_PLAY", "PAUSED"):
            remaining.append({"home": home, "away": away, "status": m.get("status")})

    return groups, finished, remaining


def _simulate_one(teams, remaining, ranking_map, form_map=None):
    """Run one simulation and return final sorted table."""
    table = {t: dict(s) for t, s in teams.items()}
    for match in remaining:
        home = match["home"]
        away = match["away"]
        hg, ag = _sample_score(home, away, ranking_map, form_map)
        table[home]["gf"] += hg
        table[home]["ga"] += ag
        table[home]["gd"] = table[home]["gf"] - table[home]["ga"]
        table[away]["gf"] += ag
        table[away]["ga"] += hg
        table[away]["gd"] = table[away]["gf"] - table[away]["ga"]
        if hg > ag:
            table[home]["points"] += 3
            table[home]["won"] += 1
            table[away]["lost"] += 1
        elif hg == ag:
            table[home]["points"] += 1
            table[away]["points"] += 1
            table[home]["draw"] += 1
            table[away]["draw"] += 1
        else:
            table[away]["points"] += 3
            table[away]["won"] += 1
            table[home]["lost"] += 1

    # Sort by points, then GD, then GF
    sorted_table = sorted(
        table.items(),
        key=lambda x: (x[1]["points"], x[1]["gd"], x[1]["gf"]),
        reverse=True
    )
    return sorted_table


def _analyze_needs(probabilities, teams, remaining):
    """Generate human-readable situation assessment from simulation probabilities."""
    needs = {}
    games_left = len(remaining)  # per team, assuming round-robin
    for team in teams:
        adv = probabilities[team]["advance"]
        first = probabilities[team]["1st"]
        second = probabilities[team]["2nd"]
        third = probabilities[team]["3rd"]
        fourth = probabilities[team]["4th"]
        current_pts = teams[team]["points"]
        max_pts = current_pts + games_left * 3

        if fourth == 100.0:
            needs[team] = "已确定小组垫底出局"
        elif adv == 100.0:
            if first == 100.0:
                needs[team] = "已锁定小组第一"
            elif first > 50:
                needs[team] = "已确保出线，有望争头名"
            else:
                needs[team] = "已确保出线"
        elif adv >= 80:
            needs[team] = "出线形势非常有利"
        elif adv >= 50:
            needs[team] = "出线机会较大，末轮不能松懈"
        elif adv >= 20:
            needs[team] = "必须末轮全力争胜，且需看其他场次"
        elif max_pts >= 3:
            needs[team] = "仅存理论出线可能"
        else:
            needs[team] = "已确定出局"
    return needs


def main():
    parser = argparse.ArgumentParser(description="Simulate World Cup group advancement")
    parser.add_argument("--group", required=True, help="Group letter (A-L)")
    parser.add_argument("--n-simulations", type=int, default=10000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    data = _fetch_data()
    if "error" in data:
        print(f"Error fetching data: {data['error']}", file=sys.stderr)
        sys.exit(1)

    teams, finished, remaining = _extract_group(data, args.group)
    if not teams:
        print(f"Group {args.group} not found or no data available.", file=sys.stderr)
        sys.exit(1)

    ranking_map = data.get("ranking_map", {})
    matches = data.get("matches", {}).get("matches", [])

    # Pre-calculate form for each team from finished tournament matches
    form_map = {}
    for team in teams:
        form_info = calculate_form(team, matches=matches)
        form_map[team] = form_info["form_score"]

    counts = {t: {"1st": 0, "2nd": 0, "3rd": 0, "4th": 0, "advance": 0} for t in teams}
    avg_points = {t: 0.0 for t in teams}

    random.seed(42)
    for _ in range(args.n_simulations):
        result = _simulate_one(teams, remaining, ranking_map, form_map)
        for pos, (team, _) in enumerate(result):
            avg_points[team] += result[pos][1]["points"]
            if pos == 0:
                counts[team]["1st"] += 1
            elif pos == 1:
                counts[team]["2nd"] += 1
            elif pos == 2:
                counts[team]["3rd"] += 1
            else:
                counts[team]["4th"] += 1
            # In 2026, top 2 + 8 best 3rd advance; simplify to top 2 guaranteed,
            # 3rd roughly ~60% historically for best 3rd
            if pos < 2:
                counts[team]["advance"] += 1
            elif pos == 2:
                counts[team]["advance"] += 0.55  # approximate best-3rd rate

    n = args.n_simulations
    for t in counts:
        for k in counts[t]:
            counts[t][k] /= n
        avg_points[t] /= n

    output = {
        "group": args.group,
        "simulations": n,
        "current_standings": teams,
        "remaining_matches": remaining,
        "form": {t: form_map[t] for t in teams},
        "probabilities": {
            t: {
                "1st": round(counts[t]["1st"] * 100, 1),
                "2nd": round(counts[t]["2nd"] * 100, 1),
                "3rd": round(counts[t]["3rd"] * 100, 1),
                "4th": round(counts[t]["4th"] * 100, 1),
                "advance": round(min(100, counts[t]["advance"] * 100), 1),
                "avg_points": round(avg_points[t], 1),
            }
            for t in teams
        },
    }

    output["needs"] = _analyze_needs(output["probabilities"], teams, remaining)

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    print(f"Group {args.group} 出线形势模拟 ({n:,} 次)")
    print("=" * 60)
    print("\n当前积分榜:")
    for team, s in sorted(teams.items(), key=lambda x: (x[1]["points"], x[1]["gd"]), reverse=True):
        print(f"  {team:<20} P{s['won']+s['draw']+s['lost']} "
              f"W{s['won']} D{s['draw']} L{s['lost']} "
              f"GF{s['gf']} GA{s['ga']} GD{s['gd']:+d} PTS{s['points']}")

    if remaining:
        print("\n剩余赛程:")
        for m in remaining:
            print(f"  {m['home']} vs {m['away']} [{m['status']}]")

    print("\n近期状态 (Elo 修正):")
    for team in teams:
        print(f"  {team:<20} {output['form'][team]:+d}")

    print("\n模拟概率 (%):")
    print(f"  {'Team':<20} {'头名':>6} {'第二':>6} {'第三':>6} {'第四':>6} {'晋级':>6} {'均分':>6}")
    print("  " + "-" * 62)
    for team in teams:
        p = output["probabilities"][team]
        print(f"  {team:<20} {p['1st']:>6.1f} {p['2nd']:>6.1f} "
              f"{p['3rd']:>6.1f} {p['4th']:>6.1f} {p['advance']:>6.1f} {p['avg_points']:>6.1f}")

    print("\n形势判断:")
    for team in teams:
        print(f"  {team:<20} {output['needs'][team]}")


if __name__ == "__main__":
    main()
