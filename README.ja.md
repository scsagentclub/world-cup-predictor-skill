# ワールドカップ予測 Skill

[English](./README.md) | [中文](./README.zh.md)

Kimi CLI 用の FIFA ワールドカップ予測スキル。試合結果の予測、グループステージ突破形勢の分析、過去対戦成績の調査ができます。

## 🌐 言語

- [English](./README.md)
- [中文](./README.zh.md)
- [日本語](./README.ja.md)

## 機能

- **リアルタイムデータ**: football-data.org から日程、順位表、スコア、FIFA ランキングを取得。
- **試合予測**: Elo モデルに基づき、直近のフォームを自動反映。
- **グループシミュレーション**: モンテカルロ法で各グループの突破確率を算出。
- **過去対戦 (H2H)**: API 検索に失敗した場合は Web 検索にフォールバック。
- **統一 CLI**: `wcp.py` ですべてのコマンドを実行可能。

## インストール

このディレクトリを Kimi の skill ディレクトリに配置します。例：

```bash
~/.config/agents/skills/world-cup-predictor/
```

またはパッケージ化された skill ファイルをインストール：

```bash
kimi skill install world-cup-predictor.skill
```

## 設定

```bash
cp .env.example .env
# .env を編集して API key を入力
```

- `FOOTBALL_DATA_API_KEY` は [football-data.org](https://www.football-data.org/) から取得
- `API_FOOTBALL_KEY` は [api-football.com](https://www.api-football.com/) から取得（H2H 用、任意）

API key がない場合、サンプルデータを使用し、Web 検索を推奨します。

## クイックスタート

```bash
python3 scripts/wcp.py standings --fixtures
python3 scripts/wcp.py predict Argentina France --knockout
python3 scripts/wcp.py simulate C
python3 scripts/wcp.py h2h Argentina Brazil
```

## スクリプト一覧

| スクリプト | 用途 |
|------------|------|
| `scripts/wcp.py` | 統一 CLI エントリポイント |
| `scripts/fetch_worldcup_data.py` | リアルタイム順位表・日程・結果取得 |
| `scripts/predict_match.py` | 単試合結果予測 |
| `scripts/form.py` | チームの直近フォーム計算 |
| `scripts/simulate_group.py` | モンテカルログループ突破シミュレーション |
| `scripts/fetch_h2h.py` | 過去対戦成績検索 |

## 参考資料

- `references/tournament_format.md` — ワールドカップのフォーマットとタイブレーカー規則
- `references/prediction_methods.md` — 予測手法とキャリブレーション説明

## ライセンス

MIT
