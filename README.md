# FPL AI

> Machine-learning-powered decision support for Fantasy Premier League.

FPL AI is an open-source data science and machine learning project that aims to predict Fantasy Premier League (FPL) player performance and turn those predictions into actionable Gameweek decisions.

The system separates two problems:

**Prediction:** What is likely to happen?  
**Optimization:** Given those predictions and FPL constraints, what should I do?

## Project Status

**Early development — working baseline.** A simple end-to-end pipeline exists (data → features → LightGBM expected-points model → squad/XI/captain optimizer → walk-forward backtest). It is a research prototype, not production-ready. See `docs/model_evaluation.md` for results and limitations.

## Goals

- Predict expected points for relevant players.
- Predict expected minutes / probability of starting.
- Recommend the optimal starting XI.
- Recommend bench order.
- Recommend captain and vice-captain.
- Recommend transfers.
- Support multi-Gameweek planning.
- Model risk, ceiling and differential potential.
- Backtest strategies across historical seasons.
- Expose predictions through an API and dashboard.
- Establish reproducible MLOps practices.

## Architecture

```text
                         ┌────────────────────┐
                         │    FPL Data/API    │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │   Data Ingestion   │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ Validation/Cleaning│
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │   Data Storage     │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ Feature Engineering│
                         └─────────┬──────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
            ┌─────────────────┐        ┌─────────────────┐
            │ Minutes Model   │        │ Points Model    │
            │ Start probability│       │ Expected points │
            └────────┬────────┘        └────────┬────────┘
                     └─────────────┬─────────────┘
                                   ▼
                         ┌────────────────────┐
                         │ Prediction Layer   │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ FPL Optimizer      │
                         │ XI / Bench / C / VC │
                         │ Transfers / Plans   │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ API / Dashboard    │
                         └────────────────────┘
```

## Core Principles

### No look-ahead bias

A feature used to predict Gameweek `N` must contain only information available before Gameweek `N`.

Do not use future Gameweek statistics, post-match updates, future injury information, future fixture changes, or aggregates that accidentally include future observations.

### Prediction and decision are separate

The ML model estimates outcomes. The optimization layer converts those estimates into FPL decisions under the applicable rules.

### Beat simple baselines first

A sophisticated model is not useful if it cannot outperform transparent baselines such as recent-point averages or simple form/fixture heuristics.

### Evaluate chronologically

FPL is a temporal prediction problem. Use time-based or walk-forward validation rather than random train/test splitting.

### Optimize for decisions

A model with slightly worse MAE may still be more useful if it produces better player rankings, captaincy decisions or transfer decisions.

### Reproducibility

Data processing, feature generation, training and evaluation should be reproducible from version-controlled code and documented configuration.

## Data

Initial data sources are expected to include the official FPL data/API plus historical datasets and, where legally and operationally appropriate, external football-performance data.

Potential sources:

- Official Fantasy Premier League API
- Historical FPL datasets
- Underlying football statistics
- Team and fixture information
- Injury/availability information
- Other legally usable public football datasets

External datasets retain their original licensing and attribution requirements.

### Player data

- Position
- Price
- Team
- Ownership
- Total points
- Form
- Minutes
- Goals
- Assists
- Bonus
- BPS
- Clean sheets
- Saves
- Transfers

### Underlying performance

- xG
- xA
- Shots
- Shots in box
- Shots on target
- Key passes
- Big chances
- Defensive actions
- Goalkeeper metrics

### Fixture context

- Opponent
- Home/away
- Fixture difficulty
- Team strength
- Opponent strength
- Recent team performance
- Fixture congestion

### Availability

- Player status
- Expected availability
- Injury information
- Recent starts
- Recent minutes
- Rotation indicators

## Machine Learning

The first model family will focus on interpretable, strong tabular methods.

### Baselines

1. Last Gameweek points
2. Rolling 3-GW average
3. Rolling 5-GW average
4. Position-adjusted rolling average
5. Simple form + fixture model

### Candidate models

- Linear regression
- Random Forest
- XGBoost
- LightGBM

Neural networks should only be introduced if experiments justify their additional complexity.

### Prediction targets

Expected points:

```text
next_gw_points
```

Expected minutes:

```text
next_gw_minutes
```

Starting probability:

```text
probability_of_start
```

Ceiling probabilities:

```text
P(points >= 6)
P(points >= 10)
P(points >= 15)
```

## Optimization

The optimizer will consume model predictions and apply FPL rules and manager constraints.

Potential libraries:

- OR-Tools
- PuLP
- Pyomo

Planned decisions:

- Starting XI
- Formation
- Bench order
- Captain
- Vice-captain
- Transfers
- Multi-Gameweek transfer plans

A simplified lineup objective is:

```text
maximize Σ(expected_points[player] × selected[player])
```

subject to the relevant squad, position, club, budget, formation and transfer constraints for the season being simulated.

## Backtesting

Backtesting is a core part of the project.

The system should operate as if it were live at each historical decision point:

```text
Information available before GW10
                ↓
Generate predictions
                ↓
Generate recommendations
                ↓
Observe actual GW10
                ↓
Record performance
                ↓
Move to GW11
```

Questions we want to answer:

- Does the model rank high-performing players correctly?
- Does it outperform simple FPL heuristics?
- Does it improve captaincy decisions?
- Do transfer recommendations create positive expected value?
- How often do recommended transfers improve the squad?
- Does performance remain stable across seasons?
- Does performance change during unusual seasons or congested periods?

## Evaluation

### Regression

- MAE
- RMSE
- Median absolute error

### Ranking

- Spearman correlation
- NDCG@K
- Precision@K
- Recall@K
- Top-K hit rate

### Probabilistic

- Brier score
- Calibration
- Log loss where appropriate

### FPL decision metrics

- Simulated total points
- Points per Gameweek
- Captain points
- Transfer gain
- Hits taken
- Transfer success rate
- Bench points
- Rank/percentile proxies where simulation permits

## Project Structure

```text
fpl-ai/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── model_experiment.md
│   └── workflows/
│       └── ci.yml
├── configs/
│   └── config.yaml
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── README.md
├── docs/
│   └── architecture.md
├── models/
│   └── .gitkeep
├── notebooks/
│   └── .gitkeep
├── reports/
│   ├── figures/
│   └── model_results/
├── scripts/
│   ├── build_features.py
│   ├── generate_predictions.py
│   ├── ingest_data.py
│   └── train_model.py
├── src/
│   └── fpl_model/
│       ├── data/
│       ├── features/
│       ├── models/
│       ├── optimization/
│       ├── pipelines/
│       └── utils/
├── tests/
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_models.py
│   └── test_optimization.py
├── .editorconfig
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── PROJECT_STATUS.md
├── pyproject.toml
├── SECURITY.md
└── README.md
```

## Getting Started

### Requirements

- Python 3.13+
- Git
- A virtual environment
- Optional: PostgreSQL for database-backed development

### Clone

```bash
git clone https://github.com/<your-username>/fpl-ai.git
cd fpl-ai
```

### Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Install

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### Configure

```bash
cp .env.example .env
```

### Quick start

```bash
python scripts/ingest_data.py --season 2021-22 --season 2022-23 --season 2023-24 --season 2024-25 --season 2025-26 --season 2026-27
python scripts/normalize_data.py --season 2021-22 --season 2022-23 --season 2023-24 --season 2024-25 --season 2025-26 --season 2026-27
python scripts/build_features.py
python scripts/train_model.py          # walk-forward backtest + final model
python scripts/generate_predictions.py --season 2025-26 --gameweek 20
```

Or `make pipeline` once the data is downloaded.

### Predict the upcoming Gameweek and open the dashboard

```bash
python scripts/fetch_live.py                 # official FPL API -> data/raw/<current season>/  (~2 min)
python scripts/predict_upcoming.py           # trains, predicts, writes the dashboard
open reports/dashboard/latest.html           # or double-click it; no server needed
```

Every gameweek, repeat (details in `docs/using_the_fpl_api.md`):

```bash
python scripts/fetch_live.py          # fresh results, prices, injury flags
python scripts/score_gameweek.py      # grade last Gameweek's saved prediction -> track record
python scripts/predict_upcoming.py    # predict the next Gameweek (re-run before the deadline for news)
```

The dashboard (a single self-contained HTML file) shows the expected points for every
player in the next unfinished Gameweek, the top captain picks, the best XI under FPL rules,
and a sortable, filterable table. Expected points are the model's estimate multiplied by FPL's
own chance-of-playing flag, so injured players are discounted. The page warns you when the
form data is more than one Gameweek behind the Gameweek being predicted. It also compares the
model with FPL's own expected points (`ep_next`), shows ownership and set-piece takers, and, once
Gameweeks have been scored, a track record of how each predictor actually did.
`fetch_live.py` needs access to `fantasy.premierleague.com`; without it the same pipeline also
works on the community dataset (`scripts/ingest_data.py --season 2026-27`), which can lag.

### Test

```bash
pytest
```

### Lint

```bash
ruff check .
```

### Format

```bash
ruff format .
```

### All checks

```bash
make check
```

## Development Workflow

Create a branch:

```bash
git checkout -b feature/data-ingestion
```

Run checks:

```bash
make check
```

Commit:

```bash
git add .
git commit -m "feat: add initial FPL data ingestion"
```

Push:

```bash
git push -u origin feature/data-ingestion
```

Open a Pull Request against `main`.

## Data and Model Artifacts

Raw data, processed datasets and trained model artifacts are excluded from Git by default.

The repository contains the code needed to reproduce them.

As the project grows, large artifacts may be managed with:

- DVC
- Object storage
- MLflow
- Versioned data releases

## Roadmap

### Phase 0 — Foundation

- [x] Repository structure
- [x] README
- [x] MIT license
- [x] Contribution guidelines
- [x] Code of Conduct
- [x] Security policy
- [x] CI
- [x] Testing foundation

### Phase 1 — Data

- [x] Official FPL API client
- [x] Historical data ingestion
- [x] Fixture ingestion
- [x] Player history ingestion
- [x] Data validation
- [ ] PostgreSQL schema
- [ ] Automated data updates

### Phase 2 — Features

- [x] Rolling form
- [x] Minutes features
- [x] Fixture strength
- [x] Team strength
- [x] Opponent strength
- [x] Home/away effects
- [x] Availability (FPL status flags applied after the model, not learned)
- [x] xG/xA
- [ ] Set-piece involvement
- [ ] Fixture congestion

### Phase 3 — Modeling

- [x] Baseline models
- [x] Time-aware validation
- [ ] XGBoost
- [x] LightGBM
- [x] Model comparison (LightGBM vs baselines)
- [ ] Expected minutes model
- [x] Expected points model
- [ ] Probabilistic predictions

### Phase 4 — Decision Engine

- [x] Starting XI optimizer
- [x] Bench optimizer
- [x] Captain optimizer
- [ ] Transfer optimizer
- [ ] Multi-GW optimizer
- [ ] Risk/differential scoring

### Phase 5 — Backtesting

- [x] Historical season simulator (fresh squad each Gameweek; no transfers yet)
- [ ] Strategy comparison
- [x] Model-vs-baseline analysis
- [x] Captaincy evaluation
- [ ] Transfer evaluation

### Phase 6 — Production

- [ ] REST API
- [ ] FPL team integration
- [x] Dashboard (static HTML)
- [ ] Scheduled inference
- [ ] Model registry
- [ ] Monitoring
- [ ] CI/CD
- [ ] Cloud deployment

## Research Questions

1. Can ML consistently outperform simple FPL form-based heuristics?
2. Which features contribute most to next-GW performance?
3. Does predicting minutes separately improve point predictions?
4. Does ranking players work better than directly predicting points?
5. Does multi-GW optimization outperform single-GW optimization?
6. How should captaincy risk be modeled?
7. Can ownership improve differential decision-making?
8. Does an ensemble outperform individual models?
9. How stable are model rankings across seasons?
10. Can the model produce statistically meaningful improvements in simulated FPL performance?

## Contributing

See `CONTRIBUTING.md`.

## Code of Conduct

See `CODE_OF_CONDUCT.md`.

## Security

See `SECURITY.md`.

## Disclaimer

FPL AI is an independent open-source project for research, experimentation and decision support.

It is not affiliated with, endorsed by, or sponsored by the Fantasy Premier League, the Premier League or any related organization.

Predictions are probabilistic estimates, not guarantees. Football outcomes are inherently uncertain, and users remain responsible for their own FPL decisions.

## License

Source code is licensed under the MIT License. See `LICENSE`.

Third-party datasets, APIs, trademarks and external resources remain subject to their respective terms and licenses.
