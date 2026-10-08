# FPL AI — setup and run instructions

Predict every player's points for the next Fantasy Premier League Gameweek, see them in a
dashboard, and check each week how the predictions actually did.

## 1. Get the code (from the bundle)

`fpl-model-claude.bundle` is a git bundle with the `claude` branch (it contains all earlier commits too).
Put it next to your clone, then pick **one** case.

**A. Fresh clone**
```bash
git clone https://github.com/weshy007/fpl-model.git
cd fpl-model
git fetch ../fpl-model-claude.bundle claude:claude
git checkout claude
```

**B. You already have the `claude` branch from an earlier bundle**
```bash
cd fpl-model
git stash                                   # only if you have uncommitted changes
git checkout claude
git fetch ../fpl-model-claude.bundle claude
git merge --ff-only FETCH_HEAD
```

Then publish it if you want it on GitHub:
```bash
git push -u origin claude
```

### Clean up leftover folders (important when upgrading from the earlier bundle)

Git does not delete a folder that still holds untracked files such as `__pycache__`. The old
`src/fpl_model/` folder (and stale copies of `src/data`, `src/models`, ...) can survive and look
like duplicate directories. Remove them:

```bash
rm -rf src/fpl_model
find . -name __pycache__ -type d -prune -exec rm -rf {} +
```
Windows PowerShell:
```powershell
Remove-Item -Recurse -Force src\fpl_model -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

`src/` should now contain exactly: `__init__.py  dashboard.py  data/  features/  models/  optimization/  pipelines/  utils/`.

## 2. Install (Python 3.13+)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```
(or with uv: `uv sync --extra dev`, then prefix commands with `uv run`).

The code is imported as `import src`, so run everything from the repository root.

## 3. One-time data download (past seasons)

```bash
python scripts/ingest_data.py    --season 2021-22 --season 2022-23 --season 2023-24 --season 2024-25 --season 2025-26
python scripts/normalize_data.py --season 2021-22 --season 2022-23 --season 2023-24 --season 2024-25 --season 2025-26
```

## 4. Predict the next Gameweek

```bash
python scripts/fetch_live.py          # this season from the official FPL API, ~2-3 minutes
python scripts/predict_upcoming.py    # trains (~5 s), predicts, writes the dashboard
```
Open `reports/dashboard/latest.html` (double-click it). Check the banner at the top: it should say form
data is up to date through the last finished Gameweek, and the subtitle shows the deadline. The
prediction is also saved to `data/predictions/<season>_gw<N>.csv` so it can be graded later.

The dashboard shows top captain picks, the best XI under FPL rules, a sortable/filterable table
(expected points, FPL's own expected points, ownership, set-piece takers, availability) and,
after your first scored Gameweek, a track record.

## 5. Every Gameweek

```bash
python scripts/fetch_live.py          # once the previous Gameweek is finished
python scripts/score_gameweek.py      # grade last Gameweek's saved prediction (adds to the track record)
python scripts/predict_upcoming.py    # next Gameweek; re-run before the deadline for late injury news
```
`score_gameweek.py` only works for a Gameweek you predicted before its deadline, so there is
nothing to score until you have made, and then played, a prediction.

## 6. Other commands

| Command | What it does |
|---|---|
| `python scripts/build_features.py` then `python scripts/train_model.py` | Rebuild the feature table and re-run the walk-forward backtest (~1-2 min). Results in `reports/model_results/` |
| `python scripts/generate_predictions.py --season 2025-26 --gameweek 20` | Replay a past Gameweek (in-sample, for demonstration only) |
| `python -m pytest` | Run the tests (49) |
| `ruff check . && ruff format --check .` | Lint and format check |
| `make predict`, `make score`, `make pipeline`, `make check` | Shortcuts (need `uv`) |

Settings (seasons, rolling windows, model parameters, output folders) are in `configs/config.yaml`.

## 7. Project layout

```
src/
  dashboard.py     self-contained HTML dashboard
  data/            download, official FPL API client, schema, validation, normalization, next-Gameweek rows
  features/        player, team and fixture features (no look-ahead)
  models/          LightGBM points model, walk-forward validation, metrics
  optimization/    squad / XI / bench / captain optimizer, decision backtest
  pipelines/       ingestion, training, upcoming prediction, track record, replay
  utils/           config and logging
scripts/           command-line entry points (section 3-6)
tests/  configs/  docs/  data/  models/  reports/
```
`data/`, `models/` and `reports/` outputs are generated and not tracked by git.
More detail: `docs/model_evaluation.md` (accuracy and limitations) and `docs/using_the_fpl_api.md`.

## 8. What changed in this restructure

- Removed the extra `src/fpl_model/` layer: the packages now live directly in `src/`.
- Removed unused placeholders: `src/models/minutes.py`, `src/optimization/transfers.py`,
  `src/data/preprocessing.py` (nothing imported them; their two small tests went with them) and the
  empty `notebooks/` and `reports/figures/` folders.
- `pyproject.toml` now builds the `src` package directly (`module-name = "src"`, `module-root = ""`).
- Results are unchanged: backtest MAE 0.985 vs 1.076 for the rolling 5-GW baseline.

## 9. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'src'` | Run `pip install -e ".[dev]"` and run scripts from the repo root |
| `data/processed/... not found` | Do the one-time download in section 3 |
| `fetch_live.py` fails or times out | Make sure https://fantasy.premierleague.com/api/bootstrap-static/ opens in your browser; the script retries each request 3 times and names the failing URL |
| Banner says form data is behind | `fetch_live.py` did not finish, or the last Gameweek is not marked finished yet; run it again later |
| `No saved prediction for ... GW<N>` | That Gameweek was not predicted before its deadline; only saved predictions can be scored |
| Python older than 3.13 | Install 3.13+ (or `uv` and use `uv run`) |

Predictions are estimates, not guarantees. Not affiliated with the Premier League or Fantasy Premier League.
