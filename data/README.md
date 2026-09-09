# Data Directory

This directory contains local data artifacts used by the project.

## Structure

```text
data/
├── raw/
├── interim/
└── processed/
```

### raw

Data exactly as retrieved from external sources, with only minimal transport
or serialization changes.

### interim

Cleaned and normalized data produced from raw data.

### processed

Model-ready datasets and feature tables.

## Git Policy

Data files are ignored by Git by default.

Do not commit large datasets or third-party data unless the project maintainers
have explicitly approved it and redistribution is permitted.

Every external dataset should document:

- Source
- Retrieval date
- License/terms
- Attribution requirements
- Transformation steps
