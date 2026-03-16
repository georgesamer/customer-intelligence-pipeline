# Customer Intelligence Pipeline

> End-to-end customer segmentation pipeline using KMeans clustering and a local LLM (Ollama) for AI-powered marketing recommendations.

---

## What it does

Paste a CSV of customer data and run one command — the pipeline automatically:

1. Loads and cleans raw customer data (CSV or JSON)
2. Engineers features like avg purchase amount, lifetime value, and purchase frequency
3. Segments customers into groups using KMeans (K is selected automatically via silhouette score)
4. Generates a visual dashboard with 5 PNG charts
5. Sends each segment's stats to a local LLM (Ollama) and returns actionable marketing strategies

---

## Pipeline flow

```
main.py
  └── CustomerPipeline
        ├── [1/5] CSVLoader          →  load raw data
        ├── [2/5] DataCleaner        →  remove nulls & duplicates
        │         DataTransformer    →  feature engineering + export
        ├── [3/5] ModelTrainer       →  KMeans clustering + save model
        ├── [4/5] Visualizer         →  5 PNG charts
        └── [5/5] CustomerAdvisor    →  Ollama recommendations
```

---

## Project structure

```
customer_pipeline/
│
├── config/
│   ├── features_config.yaml     # Feature definitions and groups
│   └── pipeline_config.yaml     # Cleaning, export, and logging settings
│
├── core/
│   ├── pipeline.py              # Main orchestrator
│   └── config.py                # Central config loader
│
├── data_layer/
│   ├── ingestion/
│   │   └── loaders.py           # CSV and JSON loaders
│   └── processing/
│       ├── cleaner.py           # Missing values, duplicates, outliers
│       └── transformer.py       # Feature engineering + export
│
├── ai_engine/
│   ├── trainer.py               # KMeans training + auto K selection
│   ├── predictor.py             # Load model and run inference
│   ├── visualizer.py            # Generate dashboard charts
│   ├── advisor.py               # Send segments to Ollama
│   └── models/                  # Saved .pkl model files
│
├── utils/
│   ├── logger.py
│   ├── file_utils.py
│   ├── helpers.py
│   └── validators.py
│
├── tests/
│   ├── test_loaders.py
│   ├── test_cleaner.py
│   └── test_pipeline.py
│
├── data/                        # Raw input data
├── outputs/                     # Generated results (auto-created)
├── main.py                      # Entry point
└── requirements.txt
```

---

## Customer segments

| Segment | Description | Strategy |
|---|---|---|
| VIP | High spend, high frequency | Exclusive loyalty program |
| Middle tier | Moderate spend and frequency | Upsell and cross-sell |
| Frequent low | High frequency, low spend | Reward loyalty not spend |
| At risk | Very low purchase count | Win-back campaign |

---

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com) installed and running locally with `llama3.1:latest`

---

## Installation

```bash
pip install -r requirements.txt
ollama pull llama3.1:latest
```

---

## Usage

```bash
# Make sure Ollama is running
ollama serve

# Run the full pipeline
python main.py
```

---

## Output

All results are saved to `outputs/` automatically:

```
outputs/
├── features_*.csv               # Cleaned and engineered features
├── clustered_customers.csv      # Each customer with their segment
├── charts/
│   ├── 00_dashboard.png         # Full dashboard (all charts)
│   ├── 01_cluster_distribution.png
│   ├── 02_avg_spent_per_cluster.png
│   ├── 03_spending_distribution.png
│   └── 04_scatter.png
└── advice/
    ├── advice.json              # Machine-readable recommendations
    └── advice.txt               # Human-readable advisory report
```

---

## Tech stack

| Tool | Purpose |
|---|---|
| pandas / numpy | Data processing |
| scikit-learn | KMeans clustering |
| matplotlib / seaborn | Charts and dashboard |
| Ollama (llama3.1) | AI marketing recommendations |
| PyYAML | Configuration management |
| joblib | Model persistence |
| pytest | Testing |

---

## Sample AI advice output

```
SEGMENT: VIP
----------------------------------------
Customers : 9
Avg spent : $4,110.75
Avg orders: 35.1

Advice:
- Premium Loyalty Program: Offer exclusive rewards and early access to new products.
- Tailored Recommendations: Curated content based on past purchases.
- VIP-only Events: Invitation-only experiences to reinforce the relationship.
Risk: Loyalty fatigue — refresh perks regularly to avoid complacency.
```
