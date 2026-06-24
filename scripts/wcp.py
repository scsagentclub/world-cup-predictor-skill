#!/usr/bin/env python3
"""
Unified CLI entry point for the World Cup Predictor skill.

Usage:
    python3 wcp.py standings [--group A] [--fixtures] [--results] [--json]
    python3 wcp.py predict <team1> <team2> [--knockout] [--json]
    python3 wcp.py simulate <group> [--n-simulations 10000] [--json]
    python3 wcp.py h2h <team1> <team2> [--json]
    python3 wcp.py form <team> [--n 5] [--json]
    python3 wcp.py help
"""

import argparse
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


def _script(name):
    return Path(__file__).resolve().parent / name


def _run(cmd):
    """Run a subprocess command and forward exit code."""
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def cmd_standings(args):
    cmd = [sys.executable, str(_script("fetch_worldcup_data.py"))]
    if args.group:
        cmd.extend(["--group", args.group])
    if args.fixtures:
        cmd.append("--fixtures")
    if args.results:
        cmd.append("--results")
    if args.json:
        cmd.append("--json")
    _run(cmd)


def cmd_predict(args):
    cmd = [
        sys.executable, str(_script("predict_match.py")),
        "--team1", args.team1,
        "--team2", args.team2,
    ]
    if args.knockout:
        cmd.append("--knockout")
    if args.json:
        cmd.append("--json")
    _run(cmd)


def cmd_simulate(args):
    cmd = [
        sys.executable, str(_script("simulate_group.py")),
        "--group", args.group,
    ]
    if args.n_simulations:
        cmd.extend(["--n-simulations", str(args.n_simulations)])
    if args.json:
        cmd.append("--json")
    _run(cmd)


def cmd_h2h(args):
    cmd = [
        sys.executable, str(_script("fetch_h2h.py")),
        "--team1", args.team1,
        "--team2", args.team2,
    ]
    if args.json:
        cmd.append("--json")
    _run(cmd)


def cmd_form(args):
    cmd = [
        sys.executable, str(_script("form.py")),
        args.team,
    ]
    if args.n:
        cmd.extend(["--n", str(args.n)])
    if args.json:
        cmd.append("--json")
    _run(cmd)


def cmd_help(args):
    print(__doc__)


def main():
    parser = argparse.ArgumentParser(
        prog="wcp",
        description="World Cup Predictor unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 wcp.py standings --fixtures
  python3 wcp.py predict Argentina France --knockout
  python3 wcp.py simulate C
  python3 wcp.py h2h Argentina Brazil
        """
    )
    parser.add_argument("--json", action="store_true", help="Output JSON where supported")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # standings
    p_standings = subparsers.add_parser("standings", help="Show group standings and fixtures")
    p_standings.add_argument("--group", help="Filter by group letter")
    p_standings.add_argument("--fixtures", action="store_true", help="Show upcoming fixtures")
    p_standings.add_argument("--results", action="store_true", help="Show finished results")
    p_standings.set_defaults(func=cmd_standings)

    # predict
    p_predict = subparsers.add_parser("predict", help="Predict a match outcome")
    p_predict.add_argument("team1", help="Home / first team")
    p_predict.add_argument("team2", help="Away / second team")
    p_predict.add_argument("--knockout", action="store_true", help="Knockout-stage match")
    p_predict.set_defaults(func=cmd_predict)

    # simulate
    p_sim = subparsers.add_parser("simulate", help="Simulate group advancement probabilities")
    p_sim.add_argument("group", help="Group letter (A-L)")
    p_sim.add_argument("--n-simulations", type=int, default=10000, help="Number of Monte Carlo runs")
    p_sim.set_defaults(func=cmd_simulate)

    # h2h
    p_h2h = subparsers.add_parser("h2h", help="Head-to-head history")
    p_h2h.add_argument("team1", help="First team")
    p_h2h.add_argument("team2", help="Second team")
    p_h2h.set_defaults(func=cmd_h2h)

    # form
    p_form = subparsers.add_parser("form", help="Recent team form")
    p_form.add_argument("team", help="Team name")
    p_form.add_argument("--n", type=int, default=5, help="Number of recent matches")
    p_form.set_defaults(func=cmd_form)

    # help
    p_help = subparsers.add_parser("help", help="Show usage help")
    p_help.set_defaults(func=cmd_help)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
