# Run FPL AI locally — from clone to prediction

By the end you will have a dashboard (`reports/dashboard/latest.html`) showing how many points the model
expects every player to score in the **next Fantasy Premier League Gameweek**, plus the best XI and captain
picks for it.

Everything below was run from a fresh clone, except `fetch_live.py`, which needs access to the official FPL
website (see section 5 and Troubleshooting).

## 1. What you need

| Requirement | Notes |
|---|---|
| Git | any recent version |
| Python 3.13 or newer | check with `python --version` (on some systems the command is `python3`) |
| Internet access | to GitHub and to `fantasy.premierleague.com` |
| Disk space | about 1.5 GB (most of it is the Python packages) |

## 2. Clone the repository

```bash
git clone -b claude https://github.com/weshy007/fpl-model.git
cd fpl-model
```

Everything else is run from this folder (`fpl-model/`). Once the `claude` branch has been merged into `main`, drop `-b claude`.

## 3. Create an environment and install

macOS / Linux:
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Check the install (about 10 seconds, optional but recommended):
```bash
python -m pytest -q
```
You should see `50 passed`.

Whenever you open a new terminal later, activate the environment again
(`source .venv/bin/activate` or `.venv\Scripts\Activate.ps1`) before running anything.

## 4. Download the history (one time, about a minute)

The model learns from five past seasons. This downloads them and converts them to one clean format.

```bash
python scripts/ingest_data.py    --season 2021-22 --season 2022-23 --season 2023-24 --season 2024-25 --season 2025-26
python scripts/normalize_data.py --season 2021-22 --season 2022-23 --season 2023-24 --season 2024-25 --season 2025-26
```

Expected: the last lines read like `2025-26: 29,747 rows -> data/processed/2025-26/player_gw.csv`.

## 5. Get the current season (every Gameweek)

```bash
python scripts/fetch_live.py
```

This pulls this season's fixtures, prices, injury flags and every player's results so far from the official
FPL API. It takes a few minutes because it makes one request per player and prints progress every 100 players.
It needs to be run again each Gameweek once the previous Gameweek is finished, so the model sees the latest results.

## 6. Predict the next Gameweek

```bash
python scripts/predict_upcoming.py
```

It picks the next Gameweek automatically, trains the model on everything played before it (about 30 seconds
in total) and prints the ten players with the most expected points:

```
GW6 top 10 expected points:
   web_name team position opponent  price  expected_points  availability
        ...                       (your real numbers will appear here)
Dashboard: reports/dashboard/2026-27_gw6.html
```

## 7. Read the result

Open the dashboard:

```bash
open reports/dashboard/latest.html          # macOS
xdg-open reports/dashboard/latest.html      # Linux
start reports\dashboard\latest.html         # Windows
```
(or just double-click the file; no server is needed).

What you will see, top to bottom:

1. **Banners:** whether the form data is up to date (it should say "up to date through GW" followed by the last
   finished Gameweek), and any strong picks who are doubtful or injured.
2. **Top captain picks:** the four players with the highest expected points.
3. **Best XI under FPL rules:** the best 15 players, XI, bench order, captain (C) and vice-captain (V) from scratch
   within £100m, three players per club and the formation limits. It ignores your current squad.
4. **Track record:** appears after you have scored a Gameweek (section 8).
5. **All players:** every player's expected points. Click a column to sort; filter by position, team, price or
   availability. Columns:
   - **Exp. pts:** the model's estimate multiplied by FPL's chance-of-playing flag (so an injured player shows 0).
   - **Model:** the estimate before that availability adjustment.
   - **FPL xP:** FPL's own expected points, for comparison.
   - **Form (5 GW):** the player's average points over the last five Gameweeks.
   - **Own %, Set pieces, Availability:** ownership, penalty/corner/free-kick duties, and the injury news.

The same numbers are saved as a spreadsheet in `data/predictions/<season>_gw<N>.csv`.

## 8. The weekly routine

Repeat these three commands each Gameweek (a few minutes in total):

```bash
python scripts/fetch_live.py          # once the previous Gameweek is finished
python scripts/score_gameweek.py      # grade last Gameweek's saved prediction against real results
python scripts/predict_upcoming.py    # predict the next one; run again just before the deadline for late injury news
```

`score_gameweek.py` compares the model, FPL's own expected points and two simple form baselines on the Gameweek you
predicted, and adds it to the dashboard's **Track record**. It can only grade a Gameweek that you predicted before its
deadline, so run `predict_upcoming.py` at least once before each deadline.

## 9. Optional: re-run the accuracy backtest

```bash
python scripts/build_features.py
python scripts/train_model.py
```

Takes about two minutes. It simulates the 2025-26 season Gameweek by Gameweek, training only on earlier data, and
compares the model with simple baselines. Expected output:

```
                      mae  spearman  top_k_points  captain_points  xi_points
pred_model          0.985     0.723         4.621           6.447     57.026
base_roll5          1.076     0.708         3.876           3.737     46.053
...
```
Lower `mae` is better; higher is better for the rest. Detailed tables are written to `reports/model_results/`, and the
interpretation and limitations are in `docs/model_evaluation.md`.

## 10. Settings and files

- `configs/config.yaml`: seasons, rolling windows, model parameters, output folders.
- `data/`, `models/`, `reports/`: generated output, not tracked by git. Delete them to start from scratch.
- `src/`: the code (`data/`, `features/`, `models/`, `optimization/`, `pipelines/`, `utils/`, `dashboard.py`).
- `scripts/`: the commands used above.
- `docs/`: model evaluation and a guide to the official FPL API.

## 11. Troubleshooting

| Problem | Fix |
|---|---|
| `python: command not found` / wrong version | Use `python3`, or install Python 3.13+ from python.org |
| `ModuleNotFoundError: No module named 'src'` | Activate the environment, run `pip install -e ".[dev]"`, and run commands from the `fpl-model/` folder |
| `No data for <season> ...` | Do section 4 (past seasons) or section 5 (current season) first |
| `fetch_live.py` fails or hangs | Open https://fantasy.premierleague.com/api/bootstrap-static/ in your browser. If it does not load, it is a network or firewall issue. The script retries each request three times and names the one that failed |
| `fetch_live.py` stops with a `KeyError` or column error | The API response differs from what the code expects (this step could not be run against the live site during development). Copy the full error message and report it |
| Cannot use the official API | As a fallback, `python scripts/ingest_data.py --season 2026-27` downloads a community copy of the current season. It can be weeks out of date, in which case the dashboard shows a warning |
| Banner says form data is behind | The latest results were not downloaded yet: run `fetch_live.py` again |
| `No saved prediction for ... GW<N>` | That Gameweek was not predicted before its deadline; only saved predictions can be graded |
| Dashboard looks empty or old | Open `reports/dashboard/latest.html`, then refresh the browser |

Predictions are estimates, not guarantees. This project is not affiliated with the Premier League or Fantasy Premier League.