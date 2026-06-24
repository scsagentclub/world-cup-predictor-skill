# 世界杯预测 Skill

[English](./README.md) | [日本語](./README.ja.md)

用于 Kimi CLI 的 FIFA 世界杯预测技能：预测比赛结果、分析小组出线形势、查询历史交锋记录。

## 🌐 语言

- [English](./README.md)
- [中文](./README.zh.md)
- [日本語](./README.ja.md)

## 功能特性

- **实时数据**：通过 football-data.org 获取赛程、积分榜、比分和 FIFA 排名。
- **比赛预测**：基于 Elo 模型，自动结合近期状态调整。
- **小组模拟**：蒙特卡洛模拟每组出线概率。
- **历史交锋**：支持 API 查询，失败时回退到网络搜索。
- **统一入口**：`wcp.py` 一个命令入口完成所有操作。

## 安装

将此目录放到 Kimi 的 skill 目录中，例如：

```bash
~/.config/agents/skills/world-cup-predictor/
```

或者安装打包好的 skill 文件：

```bash
kimi skill install world-cup-predictor.skill
```

## 配置

```bash
cp .env.example .env
# 编辑 .env，填入你的 API key
```

- `FOOTBALL_DATA_API_KEY` 从 [football-data.org](https://www.football-data.org/) 获取
- `API_FOOTBALL_KEY` 从 [api-football.com](https://www.api-football.com/) 获取（可选，用于历史交锋）

没有 API key 时，脚本会使用示例数据并提示使用网络搜索。

## 快速开始

```bash
python3 scripts/wcp.py standings --fixtures
python3 scripts/wcp.py predict Argentina France --knockout
python3 scripts/wcp.py simulate C
python3 scripts/wcp.py h2h Argentina Brazil
```

## 脚本说明

| 脚本 | 用途 |
|------|------|
| `scripts/wcp.py` | 统一命令入口 |
| `scripts/fetch_worldcup_data.py` | 获取实时积分榜、赛程、赛果 |
| `scripts/predict_match.py` | 预测单场比赛结果 |
| `scripts/form.py` | 计算球队近期状态 |
| `scripts/simulate_group.py` | 蒙特卡洛小组出线模拟 |
| `scripts/fetch_h2h.py` | 历史交锋查询 |

## 参考资料

- `references/tournament_format.md` — 世界杯赛制与排名规则
- `references/prediction_methods.md` — 预测方法论与校准说明

## 许可证

MIT
