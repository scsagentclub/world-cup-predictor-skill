<div align="center">

# 🏆 世界杯预测 Skill

**适用于各类 AI Agent 的 FIFA 世界杯预测与分析工具**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Agent Compatible](https://img.shields.io/badge/Agent-Compatible-brightgreen.svg)]()

[English](./README.md) | [日本語](./README.ja.md)

</div>

---

## 🌐 语言

- [English](./README.md)
- [中文](./README.zh.md)
- [日本語](./README.ja.md)

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📡 **实时数据** | 通过 football-data.org 获取赛程、积分榜、比分和 FIFA 排名。 |
| 🎯 **比赛预测** | 基于 Elo 模型，自动结合近期状态调整。 |
| 🎲 **小组模拟** | 蒙特卡洛模拟每组出线概率。 |
| ⚔️ **历史交锋** | 支持 API 查询，失败时回退到网络搜索。 |
| 🖥️ **统一入口** | 一个命令入口完成所有操作。 |

---

## 🤖 兼容的 Agent

本 skill 适用于任何支持以下能力的 AI Agent 平台：

- 运行本地 Python 脚本
- 读取 markdown 技能说明
- 执行 shell 命令

已测试 / 兼容：

- Kimi Code CLI
- OpenClaw
- Hermes Agent
- 其他 MCP / ACP 兼容 Agent

---

## 🚀 快速开始

```bash
# 积分榜与赛程
python3 scripts/wcp.py standings --fixtures

# 预测单场比赛
python3 scripts/wcp.py predict Argentina France --knockout

# 小组出线模拟
python3 scripts/wcp.py simulate C

# 历史交锋
python3 scripts/wcp.py h2h Argentina Brazil
```

### 示例输出

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

## 📦 安装

### 方式一：复制到你的 Agent skill 目录

大多数 Agent 会从以下目录加载 skill：

```bash
~/.config/agents/skills/world-cup-predictor/
# 或
~/.kimi/skills/world-cup-predictor/
# 或
~/.claude/skills/world-cup-predictor/
```

复制本文件夹到该目录：

```bash
cp -r world-cup-predictor ~/.config/agents/skills/
```

### 方式二：安装打包好的 skill 文件

如果你的 Agent 支持 `.skill` 包：

```bash
# Kimi CLI 示例
kimi skill install world-cup-predictor.skill
```

---

## ⚙️ 配置

```bash
cp .env.example .env
# 编辑 .env，填入你的 API key
```

| 变量 | 来源 | 是否必填 |
|------|------|----------|
| `FOOTBALL_DATA_API_KEY` | [football-data.org](https://www.football-data.org/) | 推荐填写 |
| `API_FOOTBALL_KEY` | [api-football.com](https://www.api-football.com/) | 可选（用于历史交锋） |

> 💡 没有 API key 时，脚本会使用示例数据并提示使用网络搜索。

---

## 📜 脚本说明

| 脚本 | 用途 |
|------|------|
| `scripts/wcp.py` | 统一命令入口 |
| `scripts/fetch_worldcup_data.py` | 获取实时积分榜、赛程、赛果 |
| `scripts/predict_match.py` | 预测单场比赛结果 |
| `scripts/form.py` | 计算球队近期状态 |
| `scripts/simulate_group.py` | 蒙特卡洛小组出线模拟 |
| `scripts/fetch_h2h.py` | 历史交锋查询 |

---

## 📚 参考资料

- [`references/tournament_format.md`](./references/tournament_format.md) — 世界杯赛制与排名规则
- [`references/prediction_methods.md`](./references/prediction_methods.md) — 预测方法论与校准说明

---

## 🤝 贡献

欢迎提交 Pull Request 和建议！如有改进想法，请开启 issue 讨论。

---

## 📄 许可证

本项目采用 [MIT 许可证](./LICENSE)。
