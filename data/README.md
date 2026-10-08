# Data

Contents of `raw/`, `interim/` and `processed/` are generated and not tracked by Git.

```bash
python scripts/ingest_data.py --season 2021-22 --season 2022-23 --season 2023-24 --season 2024-25 --season 2025-26
python scripts/normalize_data.py --season 2021-22 --season 2022-23 --season 2023-24 --season 2024-25 --season 2025-26
```

Historical gameweek data comes from
[vaastav/Fantasy-Premier-League](https://github.com/vaastav/Fantasy-Premier-League)
and keeps its original licence and attribution requirements.
Expected-stat columns (xG/xA) only exist from 2022-23 onwards.
