# Contributing to FPL AI

Thank you for considering contributing to FPL AI.

This project combines data engineering, machine learning, optimization and
software engineering. Contributions should prioritize correctness,
reproducibility and maintainability.

## Before You Start

Please read:

- `README.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`

For larger changes, open an issue first so the proposed approach can be
discussed before significant implementation work begins.

## Development Setup

```bash
git clone https://github.com/<your-username>/fpl-ai.git
cd fpl-ai

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
pre-commit install
```

Run:

```bash
make check
```

## Branches

Use descriptive branches:

```text
feature/data-ingestion
feature/minutes-model
feature/fixture-features
fix/fixture-date-validation
docs/improve-readme
```

## Commits

Prefer conventional-style messages:

```text
feat: add historical fixture ingestion
fix: prevent future-gameweek leakage
docs: document feature pipeline
test: add lineup constraint tests
refactor: simplify prediction interface
```

## Pull Requests

A good pull request should:

1. Explain what changed.
2. Explain why it changed.
3. Include tests where appropriate.
4. Update documentation where necessary.
5. Avoid unrelated changes.
6. Pass CI.
7. Preserve reproducibility.

## Machine Learning Contributions

For ML changes, document:

### Hypothesis

What are you testing?

### Data

- Seasons
- Gameweeks
- Data sources
- Filtering rules

### Features

Describe newly introduced features.

### Validation

Use time-aware validation and explain the train/validation/test periods.

### Baseline

Compare the new approach with an existing baseline.

### Metrics

Report relevant metrics such as MAE, RMSE, Spearman correlation,
NDCG@K, Top-K hit rate, calibration metrics and FPL simulation metrics.

### Leakage analysis

Explicitly consider whether the new feature could contain information that
would not have been available at prediction time.

### Reproducibility

Include enough information for another contributor to reproduce the result.

## Data Contributions

Do not commit large raw datasets unless explicitly approved.

Do not add data that cannot legally or ethically be redistributed.

Document:

- Source
- Retrieval date
- License/terms
- Attribution requirements
- Transformation process

## Review Philosophy

Reviews should focus on:

- Correctness
- Reproducibility
- Leakage
- Test coverage
- Maintainability
- Performance
- Documentation

Methodological disagreements should be resolved through evidence,
experiments and clearly stated assumptions.

## Questions

Open a GitHub Discussion or Issue for general project questions.
