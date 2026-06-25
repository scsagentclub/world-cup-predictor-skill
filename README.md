<div align="center">

# 🏆 World Cup Predictor Skill

**AI Agent skill for FIFA World Cup predictions and analysis**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Agent Compatible](https://img.shields.io/badge/Agent-Compatible-brightgreen.svg)]()

[中文](./README.zh.md) | [日本語](./README.ja.md)

</div>

---

## 🌐 Languages

- [English](./README.md)
- [中文 (Chinese)](./README.zh.md)
- [日本語 (Japanese)](./README.ja.md)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📡 **Real-time Data** | Fetch live fixtures, standings, scores, and FIFA rankings via football-data.org. |
| 🎯 **Match Prediction** | Elo-derived model with automatic recent-form adjustment. |
| 🎲 **Group Simulation** | Monte Carlo advancement probabilities for every group. |
| ⚔️ **Historical H2H** | Head-to-head lookup with API/search fallback. |
| 🖥️ **Unified CLI** | One command entry point for all operations. |

---

## 🤖 Compatible Agents

This skill can be used by any AI Agent platform that supports:

- Running local Python scripts
- Reading markdown skill instructions
- Executing shell commands

Tested / compatible with:

- [Kimi Code CLI](https://kimi.moonshot.cn/)
- [OpenClaw](https://github.com/openclaw)
- [Hermes Agent](https://github.com/hermes-agent)
- Other MCP / ACP compatible agents

---

## 🚀 Quick Start

```bash
# Standings & fixtures
python3 scripts/wcp.py standings --fixtures

# Predict a match
python3 scripts/wcp.py predict Argentina France --knockout

# Group advancement simulation
python3 scripts/wcp.py simulate C

# Head-to-head history
python3 scripts/wcp.py h2h Argentina Brazil
```

### Example Output

```text
Match: Argentina vs France
FIFA points: Argentina 1855 | France 1840
Form adjustment: Argentina +0 | France +0
Elo estimates: 1732.5 vs 1730.0
Expected goals: 1.33 - 1.32
Predicted probabilities: Argentina win 37.4% | Draw 26.1% | France win 36.5%
Most likely score (90 min): 1-1
```

---

## 📦 Installation

### Option 1: Copy to your agent's skills directory

Most agents load skills from a directory like:

```bash
~/.config/agents/skills/world-cup-predictor/
# or
~/.kimi/skills/world-cup-predictor/
# or
~/.claude/skills/world-cup-predictor/
```

Copy this folder there:

```bash
cp -r world-cup-predictor ~/.config/agents/skills/
```

### Option 2: Install packaged skill file

If your agent supports `.skill` packages:

```bash
# Kimi CLI example
kimi skill install world-cup-predictor.skill
```

---

## ⚙️ Configuration

```bash
cp .env.example .env
# Edit .env and add your API keys
```

| Variable | Source | Required |
|----------|--------|----------|
| `FOOTBALL_DATA_API_KEY` | [football-data.org](https://www.football-data.org/) | Recommended |
| `API_FOOTBALL_KEY` | [api-football.com](https://www.api-football.com/) | Optional (for H2H) |

> 💡 Without API keys the scripts fall back to sample data and web-search hints.

---

## 📜 Available Scripts

| Script | Purpose |
|--------|---------|
| `scripts/wcp.py` | Unified CLI entry point |
| `scripts/fetch_worldcup_data.py` | Fetch live standings, fixtures, results |
| `scripts/predict_match.py` | Predict a single match outcome |
| `scripts/form.py` | Calculate recent team form |
| `scripts/simulate_group.py` | Monte Carlo group advancement simulation |
| `scripts/fetch_h2h.py` | Historical head-to-head lookup |

---

## 📚 References

- [`references/tournament_format.md`](./references/tournament_format.md) — World Cup formats and tie-breaker rules.
- [`references/prediction_methods.md`](./references/prediction_methods.md) — Prediction methodology and calibration notes.

---

## 🤝 Contributing

Pull requests and suggestions are welcome! Feel free to open an issue to discuss improvements.

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).
