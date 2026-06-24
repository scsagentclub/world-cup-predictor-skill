---
name: world-cup-predictor
description: Predict FIFA World Cup match outcomes, analyze group-stage qualification scenarios, fetch real-time fixtures/standings/rankings, and research historical head-to-head records. Use when the user asks about World Cup predictions, match forecasts, group stage advancement chances, knockout bracket projections, team form analysis, FIFA rankings, or historical matchups between national teams.
---

# World Cup Predictor

Predict FIFA World Cup results and analyze tournament dynamics using real-time data, historical records, and quantitative models.

## Capabilities

- **Real-time data**: fetch current fixtures, standings, scores, and FIFA rankings.
- **Match prediction**: estimate win/draw/loss probabilities and expected goals.
- **Group analysis**: calculate qualification scenarios, remaining permutations, and tie-breakers.
- **Historical H2H**: retrieve past meetings between two national teams.
- **Knockout projection**: simulate likely bracket paths and champion probabilities.

## Workflow

1. **Identify the tournament edition** (current/default to next/future FIFA World Cup if unspecified).
2. **Gather data** via scripts or web search when scripts cannot retrieve live data.
3. **Apply prediction model** described below.
4. **Present results** with confidence levels and key assumptions.

## Data Sources (in order of preference)

1. `scripts/wcp.py` — unified CLI for standings, predictions, simulation, form, and H2H.
2. `scripts/fetch_worldcup_data.py` — live FIFA/football API data.
3. `scripts/form.py` — automatic recent-form calculation.
4. `scripts/predict_match.py` — probability calculator given two teams.
5. `scripts/simulate_group.py` — Monte Carlo group-stage advancement simulation.
6. `scripts/fetch_h2h.py` — historical head-to-head lookups (API key or search fallback).
7. Web search (`SearchWeb`/`FetchURL`) — for breaking news, lineups, injuries, or when APIs fail.
8. Reference files in `references/` for formats and methodology.

## Quick Commands (Unified CLI)

```bash
python3 ~/.config/agents/skills/world-cup-predictor/scripts/wcp.py help

# Standings + fixtures
python3 ~/.config/agents/skills/world-cup-predictor/scripts/wcp.py standings --fixtures
python3 ~/.config/agents/skills/world-cup-predictor/scripts/wcp.py standings --group A --results

# Match prediction (auto-applies recent form)
python3 ~/.config/agents/skills/world-cup-predictor/scripts/wcp.py predict Argentina France --knockout

# Group advancement simulation
python3 ~/.config/agents/skills/world-cup-predictor/scripts/wcp.py simulate C

# Team recent form
python3 ~/.config/agents/skills/world-cup-predictor/scripts/wcp.py form Mexico

# Head-to-head
python3 ~/.config/agents/skills/world-cup-predictor/scripts/wcp.py h2h Argentina Brazil
```

Individual scripts in `scripts/` can still be called directly for advanced options.

## API Keys

The skill reads API keys from environment variables or from a `.env` file in the skill root:

```bash
FOOTBALL_DATA_API_KEY=<key>
API_FOOTBALL_KEY=<key>
```

If a `.env` file exists, scripts load it automatically. Set keys as environment variables to override the file.

## Prediction Model

Default to a lightweight Elo-derived model unless the user requests a different approach:

1. **Base rating**: use latest FIFA ranking points, converted to Elo scale: `R = 1600 + (FIFA_points - 500) / 6`.
2. **Adjustments**:
   - Home/neutral/away: +40 neutral, +80 home, −40 away (use neutral for most World Cup matches).
   - **Recent form**: automatically calculated from finished tournament matches by `scripts/form.py` and applied in `predict_match.py` and `simulate_group.py` (+0–50 Elo points).
   - Tournament stage factor: slightly favor teams with stronger knockout history for elimination games.
3. **Expected score**: `We = 1 / (1 + 10^((Rb - Ra) / 400))`.
4. **Outcome probabilities** (Poisson goals):
   - Average total goals per World Cup match ≈ 2.65.
   - Split goals by expected score: `lambda_a = 2.65 * We`, `lambda_b = 2.65 * (1 - We)`.
   - Compute win/draw/loss from Poisson distributions.
5. **Most likely score**: find `(a,b)` maximizing `P(a)*P(b)`.

When richer data is available (xG, player availability, betting odds), incorporate it transparently and state the adjustments.

## Group Stage Analysis

For each group, compute and present:

- Current table (played, W-D-L, GF-GA, GD, points).
- Remaining fixtures.
- Monte Carlo advancement probabilities via `scripts/simulate_group.py`.
- Permutations: which results let each team advance (direct qualification or 3rd-place tie-breaker).
- Tie-breaker order: points → goal difference → goals scored → head-to-head points → head-to-head GD → head-to-head goals → fair play → drawing of lots.
- For 3rd-place ranking across groups: points → GD → goals scored → wins → fair play → drawing of lots.

## Head-to-Head Research

Use web search for recent competitive meetings (World Cup, continental championships, Confederations Cup, qualifiers). Summarize:

- Last 5 meetings with scores and competitions.
- All-time World Cup record.
- Notable historical context if relevant.

## Output Format

Structure predictions clearly:

```
Match: Team A vs Team B
Date/Stage: ...
Predicted probabilities: A win X% | Draw Y% | B win Z%
Most likely score: A-B
Key factors:
- FIFA ranking / Elo estimate
- Recent form
- Injuries / suspensions
- Historical H2H
Group scenario (if applicable):
- Current standing
- What each team needs
```

## Limitations

- Predictions are probabilistic, not certain.
- Always disclose data timestamp and missing data.
- For injuries, lineups, and weather, verify via recent web sources close to kickoff.

## References

- `references/tournament_format.md` — World Cup formats and tie-breaker rules.
- `references/prediction_methods.md` — deeper methodology, rating conversions, and calibration notes.
