# Model Evaluation Report — Expected Points Model v0.1

Walk-forward backtest of a LightGBM expected-points model against transparent
baselines. Numbers below come from `scripts/train_model.py` (test season 2025-26)
and a second run with 2024-25 as the test season. Training always uses only
Gameweeks that precede the block being predicted.

## 1. Executive summary

**Recommendation: GO as a research baseline / decision-support prototype; NO-GO for any claim
about beating real FPL managers.**

- The model beats every baseline on MAE in both test seasons, with confidence intervals that exclude zero.
- Ranking quality (Spearman) is only marginally better than the rolling 3-GW average.
- The decision metrics (captain points, best-XI points) favour the model but are noisy:
  the 2024-25 captaincy gain is **not** statistically significant.
- The backtest picks a fresh squad each Gameweek and ignores transfers, chips, hits and auto-subs.
  It ranks predictors against each other; its totals are not comparable to real FPL scores.

## 2. Performance analysis

Evaluation rows: players with at least 3 prior appearances. Per-Gameweek values averaged over 38 Gameweeks.

| Test season | Predictor | MAE | Spearman | Top-10 pts | Captain pts | Best-XI pts |
|---|---|---|---|---|---|---|
| 2025-26 | **LightGBM** | **0.985** | 0.723 | **4.62** | **6.45** | **57.0** |
| 2025-26 | rolling 3-GW | 1.079 | **0.724** | 3.98 | 4.21 | 47.0 |
| 2025-26 | rolling 5-GW | 1.076 | 0.708 | 3.88 | 3.74 | 46.1 |
| 2025-26 | last GW | 1.175 | 0.702 | 3.66 | 4.45 | 45.7 |
| 2025-26 | position mean | 1.559 | 0.081 | 1.13 | 1.03 | 24.8 |
| 2024-25 | **LightGBM** | **1.026** | **0.709** | **5.53** | **7.47** | **61.2** |
| 2024-25 | rolling 3-GW | 1.105 | 0.694 | 4.34 | 7.45 | 52.4 |
| 2024-25 | rolling 5-GW | 1.092 | 0.686 | 4.74 | 6.84 | 53.2 |

Paired per-Gameweek difference, model minus rolling 5-GW (mean, 95% CI, n=38):

| Metric | 2025-26 | 2024-25 |
|---|---|---|
| MAE (lower is better) | −0.091 [−0.104, −0.079] | −0.066 [−0.086, −0.046] |
| Spearman | +0.015 [+0.005, +0.025] | +0.023 [+0.012, +0.035] |
| Captain points | +2.7 [+1.0, +4.4] | +0.6 [−1.9, +3.2] (not significant) |
| Best-XI points | +11.0 [+6.4, +15.6] | +8.0 [+0.7, +15.3] |

Against the rolling 3-GW baseline the 2025-26 Spearman difference is −0.001 [−0.010, +0.008], i.e. no ranking gain.

## 3. Generalization

- Every prediction is out-of-sample (walk-forward, refit every 4 Gameweeks, 10 refits per season).
- Two different test seasons give the same ordering of predictors, which supports stability; two seasons is still a small sample.
- Calibration by prediction decile (2025-26) is close: decile means of predicted vs actual points are
  0.02/0.01, 0.22/0.23, 1.37/1.50, 2.85/3.07, 4.00/3.96. Overall bias is −0.04 points (slight under-prediction).
- Not done yet: random seeds / hyper-parameter sensitivity, and any tuning on a separate validation split.

## 4. Computational efficiency

- Final fit on 133k rows: about 4.4 s on CPU. Full walk-forward season (10 refits): about 32 s. Scoring 28k rows: 0.3 s.
- Serialized model: about 860 KB. Squad optimisation (MILP, about 700 candidates): about 0.15 s per Gameweek.
- Building the feature table for five seasons takes about 16 s.
- No scaling concern at this size.

## 5. Interpretability

- Gradient-boosted trees on 28 named rolling features. Gain importance is dominated by minutes
  (`min_last` ≈ 50%), then rolling minutes, season-to-date points, ownership, number of fixtures and rolling ICT.
- Practical reading: the model mostly learns *who will play*, then adjusts for form and fixtures.
- SHAP-style per-player explanations are not implemented.

## 6. Baseline comparison

See section 2. Practical significance: about 0.09 points of MAE per player is small in absolute terms, but the gain concentrates on
the players that matter for selection (top-form players, below).

## 7. Subset performance (2025-26)

| Subset | Rows | Model MAE | Rolling 5-GW MAE |
|---|---|---|---|
| GK | 3,278 | 0.591 | 0.620 |
| DEF | 9,316 | 1.117 | 1.243 |
| MID | 12,709 | 0.951 | 1.040 |
| FWD | 3,117 | 1.085 | 1.134 |
| Form ≤ 0.5 pts | 16,088 | 0.237 | **0.187** |
| Form 0.5–2 | 5,473 | 1.553 | 1.601 |
| Form 2–4 | 4,593 | 2.103 | 2.344 |
| Form > 4 | 2,266 | 2.583 | 3.459 |
| Double Gameweeks | 406 | 1.448 | 1.597 |
| Cold start (< 3 appearances) | 918 | 0.899 | — |

The model is worse than the baseline only for players who have been scoring about zero (mostly non-playing squad members),
where predicting a tiny positive number costs a little MAE.

## 8. Production readiness

Not production-ready. `scripts/predict_upcoming.py` now predicts an unplayed Gameweek (training only on earlier results), but
the live API client has not been exercised against the real endpoint by the developers, the availability discount is a fixed
rule that has not been backtested (no historical injury feed), and scheduled inference, monitoring and a model registry are
still missing. `scripts/generate_predictions.py` replays a past Gameweek with a model that has seen it, so it is in-sample.

## 9. Risks

- **`selected` and `value` ablation:** the capture time of these per-Gameweek fields is not documented in the source dataset.
  Removing both leaves accuracy unchanged on 2025-26 (MAE 0.986 vs 0.985, Spearman 0.720 vs 0.723; MAE gain over the
  5-GW baseline −0.090 [−0.103, −0.077]), so the results do not depend on them. Captain points moved from 6.45 to 5.76, which
  shows how noisy that metric is.
- Only two test seasons; Gameweek-level noise is large (captaincy especially).
- Injury and availability news is not used, so predictions miss late news.
- Backtest ignores transfers, hits, chips, auto-subs and price changes.
- Source data has quirks (duplicate rows in 2025-26, `AM` rows in 2024-25, team names instead of ids); handled in the normalizer.

### Experiment: defensive-contribution features

FPL added defensive-contribution points in 2025-26. Rolling features for them (defensive contribution, recoveries, tackles; only
available from 2025-26) were tested on the 2025-26 walk-forward: MAE 0.997 vs 0.985 for the base model (paired difference
+0.0125 ± 0.0027, Spearman unchanged), although the defender bias shrank (−0.135 to −0.050). Not adopted.

## 10. Recommendations

| Priority | Action | Success criterion |
|---|---|---|
| High | Run `fetch_live.py` on a networked machine and compare the dashboard with the FPL site | Fixtures, prices and flags match |
| Medium | Weight recent seasons more (defensive-contribution rule since 2025-26; defenders under-predicted by 0.135) | Lower DEF bias without worse MAE |
| Medium | Separate minutes model + availability data | Better MAE for rotation-risk players |
| Medium | Persistent-squad transfer simulation | Backtest closer to real FPL rules |
| Low | Try XGBoost / ensembles, seed sensitivity | Stable ranking across seeds |
