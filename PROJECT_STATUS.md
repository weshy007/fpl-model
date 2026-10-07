# Project Status

## Milestone 0 — Foundation: complete

Package structure, CI, tests, contribution docs, security policy, data policy.

## Milestone 1 — Historical data pipeline: complete

Raw download (5 seasons, 2021-22 to 2025-26) → validated canonical `player_gw` tables.
The normalizer handles double gameweeks, negative points, team names, `GKP`, assistant-manager rows
and exact duplicate source rows.

## Milestone 2 — Simple model: complete (v0.1)

- Leakage-checked rolling features (player form, minutes, team and opponent form, fixture context)
- LightGBM expected-points model vs transparent baselines, walk-forward validated
- MILP squad / XI / bench / captain optimizer (`scipy.optimize.milp`)
- Decision backtest and written evaluation: `docs/model_evaluation.md`

## Not yet done

- Live ingestion for the upcoming Gameweek, FPL team integration, API/dashboard
- Separate minutes model, availability/injury data
- Persistent-squad transfer simulation, multi-Gameweek planning
- PostgreSQL storage, scheduled inference, monitoring
