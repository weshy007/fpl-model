UV ?= uv
UV_RUN := $(UV) run

.PHONY: score predict pipeline install test test-cov lint format format-check check clean

install:
	$(UV) sync --extra dev

score:
	$(UV_RUN) python scripts/score_gameweek.py

predict:
	$(UV_RUN) python scripts/predict_upcoming.py

pipeline:
	$(UV_RUN) python scripts/build_features.py
	$(UV_RUN) python scripts/train_model.py

test:
	$(UV_RUN) pytest

test-cov:
	$(UV_RUN) pytest --cov=src/fpl_model --cov-report=term-missing

lint:
	$(UV_RUN) ruff check .

format:
	$(UV_RUN) ruff format .

format-check:
	$(UV_RUN) ruff format --check .

check:
	$(UV_RUN) ruff check .
	$(UV_RUN) ruff format --check .
	$(UV_RUN) pytest

clean:
	$(UV_RUN) python -c "import pathlib, shutil; [shutil.rmtree(path) if path.is_dir() else path.unlink() for pattern in ('.pytest_cache', '.ruff_cache', '.coverage', 'htmlcov', 'build', 'dist', '*.egg-info') for path in pathlib.Path('.').glob(pattern) if path.exists()]"
