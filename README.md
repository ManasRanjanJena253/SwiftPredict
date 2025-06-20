# 🚀 SwiftPredict: Lightweight, Local AutoML and Experiment Tracking Suite

Welcome to **SwiftPredict**, a blazing-fast, fully local AutoML + experiment tracking library built for ML engineers, data scientists, and researchers who prefer *privacy*, *flexibility*, and *control*. With an intuitive Python SDK, powerful FastAPI backend, and a modern UI (React/Next.js), SwiftPredict is the perfect open-source companion to your machine learning pipeline.

---

## 🔧 What Is SwiftPredict?

### SwiftPredict is a fully local AutoML library that helps you:

- #### 🧠 Automatically detect your ML task (classification/regression)
- #### ⚙️ Preprocess data intelligently (handle nulls, imbalance, encode categories)
- #### 🏃‍♂️ Run multiple ML models with cross-validation
- #### 📊 Track all your experiments in MongoDB
- #### 📈 Visualize training metrics using matplotlib/seaborn
- #### 🧪 Compare model performance instantly
- #### 🖥️ Access everything via a clean web UI
- #### 🧩 Use a native Python SDK for logging and predictions

All without sending a **single byte to the cloud**.

> ## You own your data. You own your pipeline.

---

## 📦 Installation

### 🐍 Requirements
- Python 3.8+
- MongoDB installed locally and running on default port

### 🔁 Install with pip (editable mode for development)

```bash
git clone https://github.com/ManasRanjanJena253/SwiftPredict.git
cd SwiftPredict
pip install -e .
```

### Make sure mongodb is running locally. You can install it from [MongoDB](https://www.mongodb.com/try/download/community)

---

## ⚙️ How It Works

### 🧱 Modular Architecture

```bash
pgsql
Copy
Edit
SwiftPredict/
├── backend/
│   ├── app/
│   │   ├── services/        ← AutoML core: training, preprocessing
│   │   ├── client/          ← SDK for prediction and logging
│   │   ├── api/             ← FastAPI endpoints
│   │   ├── core/            ← Global settings, config
│   │   └── main.py          ← API entry point
├── frontend/                ← React-based UI (optional)
├── cli.py                  ← CLI launcher

```

---

# 🧪 Quickstart
### 1. Launch the API + UI
```bash
pip install swiftpredict
swiftpredict launch ui
```

---

# Train
>automl = AutoML(logger=logger) 

>automl.train(X, y, task=task)

---

## ✅ Why Use SwiftPredict?

SwiftPredict stands out as a fully local, transparent, and developer-friendly AutoML tool. Here's how it compares to other popular libraries:

| **Feature**                     | **SwiftPredict 🟢** | **Auto-Sklearn ⚪** | **H2O.ai ⚪**     | **Weka ⚪**       |
|---------------------------------|---------------------|--------------------|------------------|------------------|
| Fully Local                     | ✅                  | ❌                 | ❌               | ✅               |
| No Cloud Required               | ✅                  | ❌                 | ❌               | ✅               |
| Customizable Preprocessing      | ✅                  | ⚠️ Limited         | ⚠️               | ❌               |
| MongoDB-based Run Tracking      | ✅                  | ❌                 | ❌               | ❌               |
| Built-in Web UI                 | ✅                  | ❌                 | ✅               | ❌               |
| Python SDK                      | ✅                  | ✅                 | ⚠️ Java Only     | ⚠️               |
| CLI Support                     | ✅                  | ✅                 | ✅               | ✅               |

---

## 📉 Current Limitations
### Although SwiftPredict is powerful for fast iteration and tracking, it is still in its early phase.

### 🔻 Known limitations:
* #### No GPU support yet (only CPU-based scikit-learn and XGBoost models)
* #### No advanced hyperparameter tuning (Bayesian / Optuna-style)
* #### No deep learning models (planned)
* #### Currently supports only classification and regression
* #### Basic visualizations — more dashboards coming

---

## 🚀 What’s Coming Next?
### Here’s our upcoming roadmap :

### 🧠 Algorithmic Improvements
1. #### ✅ Model Ensemble (stacking, voting, weighted averaging)
2. #### 🔲 Gradient boosting chains & hybrid methods
3. #### 🔲 Feature selection via SHAP/Permutation importance
4. #### 🧼 Preprocessing Advancements
5. #### ✅ Advanced binning & quantile transformation
6. #### 🔲 Time-series support

### 🛠 MLOps & UI
1. #### ✅ Streamlit-powered live dashboards
2. #### 🔲 Experiment comparison grid with filters
3. #### 🔲 Model versioning + rollback

---

## 👥 Contributing
### I welcome all contributors — whether you're an AI enthusiast, frontend dev, MLOps engineer, or just someone curious about AutoML.

---

## 👥 How to Contribute

SwiftPredict is not just a library — it's a growing ecosystem. Whether you're a researcher, ML engineer, full-stack dev, or an open-source enthusiast, there are many ways you can contribute and make an impact.

### 🔧 Here are some great ways to get involved:

- **🧠 Add New Models or Preprocessing Techniques**  
  > Enhance SwiftPredict’s AutoML engine by integrating new algorithms (e.g., CatBoost, ExtraTrees), or by writing custom preprocessing utilities like advanced binning, outlier detection, feature generation, etc.

- **🧪 Test the Library & Build on It**
  > Use SwiftPredict in your own projects and experiment with building custom pipelines. Try writing your own `handle_*` functions or test new model selection strategies — if it's useful, consider contributing it!

- **🖼 Improve the Frontend UI**  
  > If you're comfortable with React, TypeScript, or Tailwind CSS — jump into the frontend and help build powerful dashboards, charts, and run explorers.

- **✅ Write Tests / Add CI/CD Support**  
  > Help me build a robust testing suite and automate testing across contributions. Add GitHub Actions, coverage reports, and sanity checks.

- **📝 Improve Documentation**  
  > Good documentation is the backbone of open source. Help by clarifying usage, adding examples, or expanding on internal logic.

- **💡 Report Bugs or Suggest Features**  
  > Found a bug or have a game-changing idea? Open an issue and we’ll discuss it together!

---

### ⚡ Getting Started Is Simple

1. Fork the repo 🍴
2. Create a new branch 🚀
3. Make your changes ✅
4. Submit a pull request with a clear description 📬

We welcome both small and large contributions — whether it's fixing typos, creating a new ensemble strategy, or building an entire UI module. **Every contribution counts.**

> Let’s build the future of open, local-first AutoML together. 💻🧪
Let me know if you also want a CONTRIBUTING.md with formatting guidelines, code style, and environment setup instructions. This will boost the credibility of your repo and help new contributors onboard faster.
---

## 🤝 Contact
### Author: Manas Ranjan Jena

### Email: mranjanjena253@gmail.com

### GitHub: @ManasRanjanJena253

### LinkedIn: manasranjanjena253

---

## 🛡 License

### MIT License — You are free to use, modify, and distribute SwiftPredict with proper attribution.

---

## 💡 Summary
* #### SwiftPredict is the ideal AutoML tool if you:
* #### Want full control over your data and pipeline
* #### Need a fast, local, and visual way to iterate on models
* #### Prefer Python-native workflows without any vendor lock-in
*  #### Care about privacy, reproducibility, and open-source flexibility
* #### No cloud, no noise. Just pure ML automation at your fingertips.