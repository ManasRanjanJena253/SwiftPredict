# Contributing to swiftpredict-v2

Thank you for considering a contribution. This document covers everything you need to get the project running locally, understand the codebase, and submit changes that will be accepted.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Areas Open for Contribution](#areas-open-for-contribution)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Bugs](#reporting-bugs)

---

## Project Overview

swiftpredict-v2 has three components that work together:

1. **AutoML pipeline** (`backend/app/services/`) — preprocessing, model training, evaluation
2. **Experiment tracking SDK** (`backend/app/client/`) — MongoDB-backed run logging
3. **FastAPI backend** (`backend/app/api/`) — REST API serving the web UI and SDK

Changes to the AutoML pipeline should not break the SDK, and changes to the API should not break the UI. Keep these boundaries in mind when contributing.

---

## Prerequisites

- Python 3.10 or higher
- MongoDB Community Edition running locally on port 27017
- Git

Optional but recommended:
- A virtual environment manager (venv or conda)
- spaCy English model: `python -m spacy download en_core_web_sm`

---

## Local Setup

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/SwiftPredict.git
cd SwiftPredict

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. Install in editable mode with all dependencies
pip install -e .

# 4. Download the spaCy model
python -m spacy download en_core_web_sm

# 5. Ensure MongoDB is running
# Linux: sudo systemctl start mongod
# macOS: brew services start mongodb-community
# Windows: start the MongoDB service from Services panel

# 6. Verify the install
python -c "from swiftpredict import AutoML, SwiftPredict; print('Setup OK')"
```

---

## Project Structure

```
swiftpredict-v2/
├── swiftpredict/
│   ├── __init__.py          # Public exports
│   ├── cli.py               # CLI entry point (swiftpredict launch ui)
│   └── index.html           # Standalone web UI
├── backend/
│   └── app/
│       ├── api/
│       │   └── logger_apis.py     # All FastAPI routes
│       ├── client/
│       │   └── swift_predict.py   # SwiftPredict SDK class
│       ├── core/
│       │   └── config.py          # MongoDB schema and collection setup
│       └── services/
│           ├── automl_trainer.py  # AutoML class
│           └── preprocessing.py   # Full preprocessing pipeline
├── pyproject.toml
├── CONTRIBUTING.md
└── README.md
```

The public API is defined in `swiftpredict/__init__.py`. Any new function or class intended for end users must be exported there.

---

## Development Workflow

```bash
# Create a branch for your change
git checkout -b feature/your-feature-name

# Make your changes, then test them manually
python -c "
from swiftpredict import AutoML
model = AutoML()
result = model.fit('test', 'your_dataset.csv', 'target_column')
print(result)
"

# Start the backend and verify the UI works
swiftpredict launch ui

# Commit with a clear message
git add .
git commit -m "feat: add support for CatBoost in model zoo"

# Push and open a PR
git push origin feature/your-feature-name
```

Commit message prefixes:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `refactor:` for code restructuring without behavior change
- `test:` for adding or fixing tests

---

## Code Style

- Follow PEP 8. Line length limit is 100 characters.
- All public functions must have a docstring describing args, return values, and any notable behavior.
- Type hints are required for all function signatures.
- Do not leave commented-out code in PRs.
- Variable names should be descriptive. Single-letter names are only acceptable as loop indices.

Example of the expected docstring format:

```python
def handle_null_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handles missing values using statistical heuristics.

    Drops rows when null count is under 10% of total rows.
    Otherwise fills numeric columns with mean or mode depending on
    normality, and categorical columns with mode.

    Args:
        df (pd.DataFrame): Input DataFrame with potential null values.

    Returns:
        pd.DataFrame: Cleaned DataFrame with no null values.
    """
```

---

## Areas Open for Contribution

The following are the most impactful areas where contributions are needed.

**Model zoo expansion**

Adding CatBoost, ExtraTreesClassifier, ExtraTreesRegressor, or SVMs to the model zoo in `preprocessing.py`. The pattern is consistent — add the import, add the class to the relevant list in `model_zoo()`, and handle any constructor differences in `train_model()`.

**Hyperparameter tuning**

Currently all models train with default parameters. Adding Optuna or a grid search wrapper around `train_model()` would significantly improve result quality. This should be opt-in via a parameter on `AutoML.fit()`.

**Outlier detection**

The preprocessing pipeline does not currently handle outliers. A function following the pattern of `handle_null_values()` that uses IQR or z-score clipping would be a clean addition to `preprocessing.py`.

**Time-series support**

`detect_task()` currently returns only classification or regression. A third task type, forecasting, with appropriate model selection (Prophet, ARIMA wrappers, or sklearn-compatible regressors with lag features) is a significant open area.

**Test suite**

There are no automated tests yet. Adding pytest-based unit tests for `handle_null_values`, `detect_task`, `handle_imbalance`, and `handle_cat_columns` using small synthetic DataFrames would be an excellent contribution and does not require deep knowledge of the rest of the codebase.

**UI improvements**

The `swiftpredict/index.html` UI is a single vanilla HTML/CSS/JS file. Improvements to the run details view, metric visualization for ML projects (currently only DL projects have metric plots), or a dark mode toggle are all welcome.

---

## Submitting a Pull Request

1. Ensure your branch is up to date with `main` before opening the PR.
2. Fill out the PR template completely.
3. Keep PRs focused. One feature or fix per PR.
4. If your change touches the preprocessing pipeline, include a note about which datasets or task types you tested it on.
5. If your change adds a new dependency, justify it in the PR description. Prefer dependencies already in the stack (scikit-learn, pandas, numpy, scipy) over new ones.

PRs that pass a manual end-to-end test (`AutoML.fit()` on a classification and regression dataset without errors) will be reviewed within a few days.

---

## Reporting Bugs

Open an issue using the Bug Report template. Include:

- Python version and OS
- The exact command or code that triggered the bug
- The full traceback
- The dataset shape and column types if the bug is in the preprocessing pipeline (you do not need to share the actual data)

---

## Contact

Manas Ranjan Jena
GitHub: [@ManasRanjanJena253](https://github.com/ManasRanjanJena253)
Email: mranjanjena253@gmail.com