# Prediction Methodology Reference

## Lightweight Elo Model

Default model used by `predict_match.py`.

### 1. Rating Conversion

FIFA ranking points are converted to an Elo-like scale:

```
Elo ≈ 1600 + (FIFA_points - 1300) / 6
```

This centers roughly at 1600 and spans ~1000–1900 for current national teams.

### 2. Venue Adjustment

- Neutral site (most World Cup matches): +40 to both sides.
- Host / true home: +80 to home side.
- Away: −40 to away side.

### 3. Form Adjustment

Use last 5 competitive matches to add/subtract up to 50 Elo points:

- 4–5 wins: +40 to +50
- 2–3 wins: +10 to +30
- Mixed: 0
- 2–3 losses: −10 to −30
- 4–5 losses: −40 to −50

### 4. Expected Score

```
We = 1 / (1 + 10^((Rb - Ra) / 400))
```

`We` is the expected share of total goals for team A.

### 5. Goal Model

Total goals per World Cup match ≈ 2.65. Expected goals:

```
lambda_A = 2.65 * We
lambda_B = 2.65 * (1 - We)
```

Use independent Poisson distributions to derive:

- Win / draw / loss probabilities.
- Most likely scoreline.
- Over/under probabilities.

### 6. Knockout Considerations

For knockout matches, the 90-minute draw probability is important because extra time and penalties shift advancement odds. Report:

- 90-min win/draw/loss.
- Approximate advancement probability accounting for extra-time/pens (historically ~50/50 once level after 90 min).

## Enhanced Models (when data is available)

- **Expected goals (xG)**: use team xG for/against over recent competitive matches.
- **Elo ratings**: use specialized Elo databases (e.g., eloratings.net) directly.
- **Betting odds**: convert implied probabilities to a market estimate, removing vig.
- **Simulation**: Monte Carlo tournament simulation using match-level probabilities.

## Calibration Notes

- The default model tends to understate upsets slightly; consider widening underdog win probability by 10–20% in high-variance knockout games.
- Weather, injuries, red cards, and tactical matchups are not captured by rating models; incorporate via qualitative adjustments and state them explicitly.
