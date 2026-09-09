# Architecture

## Current State

The repository contains the foundation for a data/ML project. Production
ingestion, model training and optimization are intentionally not implemented
yet.

## Target Architecture

```text
External Sources
      |
      v
Data Ingestion
      |
      v
Validation
      |
      v
Storage
      |
      v
Feature Engineering
      |
      +-------------------+
      |                   |
      v                   v
Minutes Model       Points Model
      |                   |
      +---------+---------+
                |
                v
          Prediction Layer
                |
                v
          Decision Engine
                |
        +-------+-------+
        |       |       |
        v       v       v
       XI    Captain Transfers
                |
                v
               API
                |
                v
            Dashboard
```

## Design Rule

Prediction and optimization remain separate modules. This allows model
experiments without rewriting the decision engine and allows the optimizer to
be tested independently from model quality.
