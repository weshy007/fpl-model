# FPL AI

> Machine learning-powered Fantasy Premier League decision support.

## Overview

## Objectives

## System Architecture

## Features

## Data Sources

## Machine Learning

## Optimization

## Project Structure

## Installation

## Usage

## Model Evaluation

## MLOps

## Roadmap

## Contributing

## License

│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── pyproject.toml
├── Makefile
│
├── configs/
│   └── config.yaml
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── README.md
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_baseline_model.ipynb
│   └── 04_model_evaluation.ipynb
│
├── src/
│   └── fpl_model/
│       ├── __init__.py
│       │
│       ├── data/
│       │   ├── __init__.py
│       │   ├── ingestion.py
│       │   ├── validation.py
│       │   └── preprocessing.py
│       │
│       ├── features/
│       │   ├── __init__.py
│       │   ├── player_features.py
│       │   ├── team_features.py
│       │   └── fixture_features.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── minutes.py
│       │   ├── points.py
│       │   └── evaluation.py
│       │
│       ├── optimization/
│       │   ├── __init__.py
│       │   ├── squad.py
│       │   ├── transfers.py
│       │   └── lineup.py
│       │
│       ├── pipelines/
│       │   ├── __init__.py
│       │   ├── ingestion.py
│       │   ├── training.py
│       │   └── prediction.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── config.py
│           └── logging.py
│
├── tests/
│   ├── __init__.py
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_models.py
│   └── test_optimization.py
│
├── models/
│   └── .gitkeep
│
├── reports/
│   ├── figures/
│   └── model_results/
│
└── scripts/
    ├── ingest_data.py
    ├── build_features.py
    ├── train_model.py
    └── generate_predictions.py