# swiftpredict-v2

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Local-47A248?style=flat-square&logo=mongodb&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-latest-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-latest-006600?style=flat-square)
![LightGBM](https://img.shields.io/badge/LightGBM-latest-02569B?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![PyPI](https://img.shields.io/badge/PyPI-swiftpredict--v2-blue?style=flat-square&logo=pypi&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

A fully local, zero-cloud AutoML and experiment tracking library. One class, five lines of code, a complete machine learning pipeline.

---

## What swiftpredict-v2 Does Differently

Most AutoML libraries are built around the assumption that complexity is acceptable if results are good. You configure pipelines, manage preprocessors, tune encoders, handle class imbalance, split data, scale features, select models, cross-validate, compare results, and log everything yourself. That is hundreds of lines of boilerplate per experiment, repeated every time.

swiftpredict-v2 collapses all of that into a single `fit()` call.

It does not send your data anywhere. There is no API key, no cloud account, no rate limit, and no subscription. Everything runs on your machine, tracked in your local MongoDB instance, viewable in a local web UI that ships as a single HTML file with no build step.

The design philosophy is that a library should remove friction from the actual work, which is understanding your data and iterating on models. swiftpredict-v2 handles everything between loading a CSV and having trained, evaluated, production-ready models so that you can focus on what actually matters.

---

## Features

**Automatic preprocessing pipeline**

Null handling uses statistical heuristics: rows are dropped when missingness is under 10%, otherwise numeric columns are filled with mean or mode depending on normality test results, categorical columns use mode, and datetime columns use interpolation. No configuration required.

**Intelligent categorical encoding**

Categorical columns with five or fewer unique values are one-hot encoded. High-cardinality columns are processed with spaCy lemmatization and stopword removal, then vectorized with TF-IDF and reduced with TruncatedSVD to the minimum number of components that explain 95% of variance. The fitted encoders are stored as attributes on the `AutoML` instance for reuse at inference time.

**Automatic task detection**

The target column is inspected at runtime. String and category types map to classification. Integer targets with 20 or fewer unique values map to classification. Float targets and high-cardinality integers map to regression. No parameter needed.

**Class imbalance handling**

For classification tasks, the minority-to-majority class ratio is computed. If it falls below 0.15, SMOTE is applied automatically before training. The original DataFrame is preserved; resampling happens only on the training split.

**Multi-model training with cross-validation**

For classification: GaussianNB, XGBClassifier, RandomForestClassifier, LGBMClassifier, LogisticRegression. For regression: LinearRegression, XGBRegressor, LGBMRegressor, RandomForestRegressor. All models are trained and evaluated with 5-fold cross-validation. The best model per metric and the overall best model by majority vote are stored and returned.

**Experiment tracking via SwiftPredict SDK**

Every training run is automatically logged to a local MongoDB collection. Parameters, metrics, model names, run IDs, timestamps, tags, notes, and status are all persisted. The SDK can also be used independently of AutoML for tracking DL experiments epoch by epoch.

**Local web UI**

A single `index.html` file with no dependencies, no npm, no build step. Launch it with one CLI command. View all ML and DL projects, inspect run details and metrics, filter by status, add tags and notes, update run status, and delete runs or entire projects.

---

## Prerequisites

- Python 3.10 or higher
- MongoDB Community Edition installed and running locally on the default port (27017)

MongoDB is required for experiment tracking. Install it from [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community) and ensure the service is running before using the SDK or launching the UI.

If MongoDB is running at a non-default URI, set the environment variable before running:

```bash
export MONGO_URI="mongodb://your-host:27017"
```

---

## Installation

```bash
pip install swiftpredict-v2
```

---

## AutoML Usage

### Minimal example

```python
from swiftpredict import AutoML

model = AutoML()
results = model.fit(
    project_name="churn-prediction",
    file_path="data/churn.csv",
    target_column="churned"
)

print(results)
# {
#   "accuracy": "RandomForestClassifier",
#   "f1": "XGBClassifier",
#   "precision": "XGBClassifier",
#   "overall": ["XGBClassifier"]
# }
```

That single `fit()` call handles null imputation, boolean and categorical encoding, text vectorization, correlation-based feature removal, stratified train-test splitting, feature scaling, class imbalance correction, multi-model training with cross-validation, and experiment logging. Everything that would otherwise take 150 to 300 lines of code depending on the dataset.

### Evaluating model performance

```python
# Evaluate the overall best model on the held-out test set
metrics = model.evaluate_performance(key="overall")
print(metrics)
# {"accuracy": 0.94, "f1": 0.93, "roc_auc": 0.97, "precision": 0.94}

# Or evaluate a specific metric's best model
metrics = model.evaluate_performance(key="f1")

# Or evaluate an external model using the same test split
from sklearn.linear_model import LogisticRegression
external = LogisticRegression().fit(model.X_test, model.y_test)
metrics = model.evaluate_performance(model=external)
```

### Exporting a model

```python
# Export the overall best model
model.export_model(model_path="models/best_model.pkl")

# Export the best model for a specific metric
model.export_model(model_path="models/best_f1.pkl", key="f1")
```

### Accessing intermediate pipeline state

The `AutoML` instance retains all fitted preprocessors after training. You can access them directly instead of re-running preprocessing at inference time.

```python
# The preprocessed DataFrame used for training
model.modified_df

# The fitted StandardScaler
model.std_scaler

# List of (column_index, fitted_OneHotEncoder) tuples
model.ohe_lst

# List of (column_index, fitted_TfidfVectorizer, fitted_TruncatedSVD) tuples
model.vectorizer_lst

# Columns removed during preprocessing (by index)
model.removed_columns

# The held-out test features (already scaled)
model.X_test

# The held-out test labels
model.y_test

# Detected task type: "classification" or "regression"
model.task
```

This means you do not need to refit any preprocessor when running inference on new data. Load the `AutoML` instance or individual components and transform directly.

### Optional fit parameters

```python
model.fit(
    project_name="price-regression",
    file_path="data/houses.csv",
    target_column="sale_price",
    drop_id=True,     # Drop columns whose name contains "id" or "index". Default: True
    drop_name=True    # Drop columns whose name is exactly "name". Default: True
)
```

---

## Using the SwiftPredict SDK Independently

The `SwiftPredict` class can be used on its own for any experiment, not just AutoML. It is particularly useful for deep learning projects where you want to log metrics per epoch.

### ML project (single metric value per model)

```python
from swiftpredict import SwiftPredict

logger = SwiftPredict(project_name="sentiment-analysis", project_type="ML")

logger.log_params({"C": 1.0, "solver": "lbfgs"}, model_name="LogisticRegression")
logger.log_or_update_metric(key="accuracy", value=0.91, model_name="LogisticRegression")
logger.log_or_update_metric(key="f1_score", value=0.89, model_name="LogisticRegression")
logger.finalize_run(status="completed", notes="Baseline run", tags=["baseline", "v1"])
```

### DL project (metric value per epoch)

```python
logger = SwiftPredict(project_name="image-classifier", project_type="DL")

for epoch, (train_loss, val_acc) in enumerate(training_loop()):
    logger.log_or_update_metric(key="loss", value=train_loss, model_name="ResNet18", step=epoch)
    logger.log_or_update_metric(key="val_accuracy", value=val_acc, model_name="ResNet18", step=epoch)

logger.finalize_run(status="completed", tags=["resnet", "imagenet"])
```

### Retrieving runs

```python
runs = logger.find_project_runs()
for run in runs:
    print(run["run_id"], run["metrics"])
```

---

## Standalone Preprocessing Utilities

All preprocessing functions used internally by AutoML are also exported at the top level for use in custom pipelines.

```python
from swiftpredict import (
    handle_null_values,
    handle_imbalance,
    handle_cat_columns,
    detect_task,
    get_dtype_columns,
    text_preprocessor,
)

# Detect column types
col_types = get_dtype_columns(df)
# {"categorical": [...], "numeric": [...], "date": [...], "bool": [...]}

# Detect ML task from target column
task = detect_task(df, y="target")  # "classification" or "regression"

# Handle nulls
clean_df = handle_null_values(df)

# Encode categorical columns
encoded_df, ohe_encoders, tfidf_encoders = handle_cat_columns(df, cat_columns=["category", "description"])

# Fix class imbalance
X_resampled, y_resampled = handle_imbalance(df, target_column="label", X_train=X, y_train=y)

# Preprocess a text string
clean_text = text_preprocessor("The quick brown fox jumps!", handle_html=False)
```

---

## Launching the UI

The web UI allows you to view all logged experiments, inspect run details, filter by status, add notes and tags, and delete runs, all from a browser with no extra setup.

**Start the backend and open the UI:**

```bash
swiftpredict launch ui
```

This command starts the FastAPI backend on `http://localhost:8000` and opens `index.html` automatically in your default browser.

**What you can do in the UI:**

- View all ML and DL projects with their run IDs and model names
- Click into any run to see full details including metrics logged
- Filter all projects by status (completed, running, failed, pending)
- Log parameters, add tags, update status, and add notes to any run
- Delete individual runs or entire projects

The UI communicates directly with your local FastAPI backend. MongoDB must be running for any data to appear.

---

## Project Structure

```
swiftpredict-v2/
├── swiftpredict/
│   ├── __init__.py          # Public API exports
│   ├── cli.py               # CLI entry point
│   └── index.html           # Standalone web UI (ships with the package)
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── api/
│       │   └── logger_apis.py     # FastAPI routes
│       ├── client/
│       │   └── swift_predict.py   # Experiment tracking SDK
│       ├── core/
│       │   └── config.py          # MongoDB schema and setup
│       └── services/
│           ├── automl_trainer.py  # AutoML class
│           └── preprocessing.py   # Full preprocessing pipeline
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## API Reference

The FastAPI backend exposes the following endpoints. All are accessible at `http://localhost:8000` when the backend is running.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/projects/ml` | All ML project runs |
| GET | `/projects/dl` | All DL project runs |
| GET | `/projects/{status}` | Runs filtered by status |
| GET | `/{project}/runs/{run_id}` | Details for a specific run |
| GET | `/{project}/plots/available_metrics` | Metrics logged for a project |
| GET | `/{project}/plots/{metric}` | Plot image for a DL metric (PNG stream) |
| POST | `/{project}/runs/{run_id}/log_param` | Log a parameter to a run |
| POST | `/{project}/runs/{run_id}/add_tags` | Add tags to a run |
| POST | `/{project}/runs/{run_id}/update_status` | Update run status |
| POST | `/{project}/runs/{run_id}/add_notes` | Add notes to a run |
| DELETE | `/projects/delete` | Delete a run or entire project |
| DELETE | `/delete_all` | Delete all data |

Interactive documentation is available at `http://localhost:8000/docs` when the backend is running.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection string |

---

## Contributing

Contributions are welcome. Fork the repository, create a branch, make your changes, and open a pull request with a clear description of what was changed and why.

Areas where contributions are particularly useful: additional model types, hyperparameter tuning strategies, time-series support, and UI improvements.

---

## Author

Manas Ranjan Jena
GitHub: [@ManasRanjanJena253](https://github.com/ManasRanjanJena253)
Email: mranjanjena253@gmail.com
LinkedIn: [manasranjanjena253](https://linkedin.com/in/manasranjanjena253)

---

## License

MIT License. Free to use, modify, and distribute with attribution.