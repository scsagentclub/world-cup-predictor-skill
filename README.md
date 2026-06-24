# World Cup Predictor Skill

[中文](./README.zh.md) | [日本語](./README.ja.md)

A Kimi CLI skill for predicting FIFA World Cup match outcomes, analyzing group-stage qualification scenarios, and researching historical head-to-head records.

## Features

- **Real-time data**: Fetch current fixtures, standings, scores, and FIFA rankings via football-data.org.
- **Match prediction**: Elo-derived model with automatic recent-form adjustment.
- **Group simulation**: Monte Carlo advancement probabilities for each group.
- **Historical H2H**: Head-to-head lookup with API/search fallback.
- **Unified CLI**: `wcp.py` provides a single entry point for all commands.

## Installation

Place this directory in one of the Kimi skill locations, for example:

```bash
~/.config/agents/skills/world-cup-predictor/
```

Or install the packaged skill file:

```bash
kimi skill install world-cup-predictor.skill
```

## Configuration

```bash
cp .env.example .env
# Edit .env and add your API keys
```

- `FOOTBALL_DATA_API_KEY` from [football-data.org](https://www.football-data.org/)
- `API_FOOTBALL_KEY` from [api-football.com](https://www.api-football.com/) (optional, for H2H)

Without API keys the scripts fall back to sample data and web-search hints.

## Quick Start

```bash
python3 scripts/wcp.py standings --fixtures
python3 scripts/wcp.py predict Argentina France --knockout
python3 scripts/wcp.py simulate C
python3 scripts/wcp.py h2h Argentina Brazil
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/wcp.py` | Unified CLI entry point |
| `scripts/fetch_worldcup_data.py` | Fetch live standings, fixtures, results |
| `scripts/predict_match.py` | Predict a single match outcome |
| `scripts/form.py` | Calculate recent team form |
| `scripts/simulate_group.py` | Monte Carlo group advancement simulation |
| `scripts/fetch_h2h.py` | Historical head-to-head lookup |

## References

- `references/tournament_format.md` — World Cup formats and tie-breaker rules.
- `references/prediction_methods.md` — Prediction methodology and calibration notes.

## License

MIT
