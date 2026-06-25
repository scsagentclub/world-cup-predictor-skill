<div align="center">

# 🏆 ワールドカップ予測 Skill

**あらゆる AI Agent に対応した FIFA ワールドカップ予測・分析ツール**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Agent Compatible](https://img.shields.io/badge/Agent-Compatible-brightgreen.svg)]()

[English](./README.md) | [中文](./README.zh.md)

</div>

---

## 🌐 言語

- [English](./README.md)
- [中文](./README.zh.md)
- [日本語](./README.ja.md)

---

## ✨ 機能

| 機能 | 説明 |
|------|------|
| 📡 **リアルタイムデータ** | football-data.org から日程、順位表、スコア、FIFA ランキングを取得。 |
| 🎯 **試合予測** | Elo モデルに基づき、直近のフォームを自動反映。 |
| 🎲 **グループシミュレーション** | モンテカルロ法で各グループの突破確率を算出。 |
| ⚔️ **過去対戦 (H2H)** | API 検索に失敗した場合は Web 検索にフォールバック。 |
| 🖥️ **統一 CLI** | `wcp.py` ですべてのコマンドを実行可能。 |

---

## 🤖 対応 Agent

本 skill は以下の能力を持つ AI Agent プラットフォームで利用可能です：

- ローカル Python スクリプトの実行
- markdown スキル説明の読み取り
- shell コマンドの実行

テスト済み / 対応：

- [Kimi Code CLI](https://kimi.moonshot.cn/)
- [OpenClaw](https://github.com/openclaw)
- [Hermes Agent](https://github.com/hermes-agent)
- その他 MCP / ACP 互換 Agent

---

## 🚀 クイックスタート

```bash
# 順位表と日程
python3 scripts/wcp.py standings --fixtures

# 単試合予測
python3 scripts/wcp.py predict Argentina France --knockout

# グループ突破シミュレーション
python3 scripts/wcp.py simulate C

# 過去対戦
python3 scripts/wcp.py h2h Argentina Brazil
```

### 出力例

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

## 📦 インストール

### 方法 1：Agent の skill ディレクトリにコピー

多くの Agent は以下のようなディレクトリから skill を読み込みます：

```bash
~/.config/agents/skills/world-cup-predictor/
# または
~/.kimi/skills/world-cup-predictor/
# または
~/.claude/skills/world-cup-predictor/
```

本フォルダをそこにコピー：

```bash
cp -r world-cup-predictor ~/.config/agents/skills/
```

### 方法 2：パッケージ化された skill ファイルをインストール

お使いの Agent が `.skill` パッケージに対応している場合：

```bash
# Kimi CLI の例
kimi skill install world-cup-predictor.skill
```

---

## ⚙️ 設定

```bash
cp .env.example .env
# .env を編集して API key を入力
```

| 変数 | 取得元 | 必須 |
|------|--------|------|
| `FOOTBALL_DATA_API_KEY` | [football-data.org](https://www.football-data.org/) | 推奨 |
| `API_FOOTBALL_KEY` | [api-football.com](https://www.api-football.com/) | 任意（H2H 用） |

> 💡 API key がない場合、サンプルデータを使用し、Web 検索を推奨します。

---

## 📜 スクリプト一覧

| スクリプト | 用途 |
|------------|------|
| `scripts/wcp.py` | 統一 CLI エントリポイント |
| `scripts/fetch_worldcup_data.py` | リアルタイム順位表・日程・結果取得 |
| `scripts/predict_match.py` | 単試合結果予測 |
| `scripts/form.py` | チームの直近フォーム計算 |
| `scripts/simulate_group.py` | モンテカルログループ突破シミュレーション |
| `scripts/fetch_h2h.py` | 過去対戦成績検索 |

---

## 📚 参考資料

- [`references/tournament_format.md`](./references/tournament_format.md) — ワールドカップのフォーマットとタイブレーカー規則
- [`references/prediction_methods.md`](./references/prediction_methods.md) — 予測手法とキャリブレーション説明

---

## 🤝 コントリビューション

Pull Request やご提案を歓迎します！改善案があれば issue を立ててご相談ください。

---

## 📄 ライセンス

このプロジェクトは [MIT ライセンス](./LICENSE) の下で公開されています。
