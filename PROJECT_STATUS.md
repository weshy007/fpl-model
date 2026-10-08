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

## Milestone 3 — Upcoming-Gameweek predictions and dashboard: complete (v0.2)

- Official FPL API client (`scripts/fetch_live.py`) writes the same raw files as the community dataset
- `scripts/predict_upcoming.py`: next unfinished Gameweek, trained only on earlier results,
  availability-adjusted expected points per player
- Self-contained HTML dashboard (`reports/dashboard/latest.html`): captain picks, best XI, sortable table
- The API client could not be run against the live endpoint in the development sandbox (network
  blocked); it is covered by tests with a fake server and shares its parsing with the verified
  community-dataset path. Run `fetch_live.py` once to confirm on your machine.

## Milestone 4 — Gameweek-by-Gameweek loop: complete (v0.3)

- Gameweek calendar from the official `events` (next Gameweek, deadline, finished flag)
- Every prediction is saved before the deadline (`data/predictions/`) and later scored against real
  results with `scripts/score_gameweek.py`, next to FPL's own `ep_next` and simple form baselines
- Dashboard shows FPL xP, ownership, set-piece takers and the running track record
- `fetch_live.py` archives a point-in-time player snapshot on every run
- Tested against real records copied from the live `bootstrap-static` payload; still not run end to end
  against the live API from the development sandbox (network blocked)

## Not yet done

- FPL team integration (your own squad), hosted API / auto-refreshing dashboard
- Backtest of the availability adjustment (no historical injury feed)
- Separate minutes model, availability/injury data
- Persistent-squad transfer simulation, multi-Gameweek planning
- PostgreSQL storage, scheduled inference, monitoring
