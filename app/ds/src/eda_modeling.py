from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from fastapi.testclient import TestClient
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
DOCS_DIR = ROOT / "docs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def get_test_client() -> TestClient:
    backend_path = ROOT.parent / "backend"
    sys.path.insert(0, str(backend_path))
    from main import app  # pylint: disable=import-outside-toplevel

    return TestClient(app)


def fetch_influencers(client: TestClient) -> List[Dict[str, Any]]:
    response = client.get("/api/v1/influencers/")
    response.raise_for_status()
    return response.json()


def generate_synthetic_record(idx: int) -> Dict[str, Any]:
    niches = ["Tech", "Fashion", "Fitness", "Food", "Travel", "Gaming"]
    locations = ["New York", "Los Angeles", "Chicago", "Austin", "Seattle", "Miami"]
    tags_pool = ["Video", "Blog", "Photo", "Reels", "Podcast", "Livestream"]

    niche = random.choice(niches)
    followers = int(np.clip(np.random.lognormal(mean=10.6, sigma=0.6), 2_000, 2_000_000))
    engagement_rate = float(np.clip(np.random.normal(loc=4.8, scale=1.3), 0.5, 12.0))
    tag_count = random.randint(1, 3)

    return {
        "name": f"Synthetic Creator {idx}",
        "niche": niche,
        "follower_count": followers,
        "engagement_rate": round(engagement_rate, 2),
        "location": random.choice(locations),
        "content_format_tags": random.sample(tags_pool, k=tag_count),
        "bio": "Synthetic profile generated for baseline DS modeling.",
    }


def seed_synthetic_data_if_needed(client: TestClient, minimum_rows: int = 120) -> List[int]:
    current = fetch_influencers(client)
    rows_needed = max(0, minimum_rows - len(current))
    synthetic_ids: List[int] = []

    for i in range(rows_needed):
        payload = generate_synthetic_record(i + 1)
        created = client.post("/api/v1/influencers/", json=payload)
        created.raise_for_status()
        synthetic_ids.append(created.json()["id"])

    return synthetic_ids


def build_dataframe(records: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    df["tags_count"] = df["content_format_tags"].apply(lambda tags: len(tags) if isinstance(tags, list) else 0)
    df["bio_length"] = df["bio"].fillna("").str.len()
    # Target: creator is high performer if engagement beats median.
    df["target_high_performer"] = (df["engagement_rate"] >= df["engagement_rate"].median()).astype(int)
    return df


def run_eda(df: pd.DataFrame) -> Dict[str, Any]:
    null_counts = df.isnull().sum().to_dict()
    describe_stats = df.describe(include="all").replace({np.nan: None}).to_dict()
    corr = df[["follower_count", "engagement_rate", "tags_count", "bio_length", "target_high_performer"]].corr()

    plt.figure(figsize=(8, 5))
    sns.histplot(df["engagement_rate"], kde=True, bins=20)
    plt.title("Engagement Rate Distribution")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "engagement_distribution.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x="niche", y="engagement_rate")
    plt.title("Engagement Rate by Niche")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "engagement_by_niche.png", dpi=150)
    plt.close()

    plt.figure(figsize=(6, 5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "correlation_heatmap.png", dpi=150)
    plt.close()

    eda_summary = {
        "row_count": int(len(df)),
        "column_count": int(df.shape[1]),
        "null_counts": null_counts,
        "correlations": corr.round(3).to_dict(),
        "descriptive_statistics": describe_stats,
    }
    with (OUTPUT_DIR / "eda_summary.json").open("w", encoding="utf-8") as file:
        json.dump(eda_summary, file, indent=2)
    return eda_summary


def run_models(df: pd.DataFrame) -> pd.DataFrame:
    feature_cols = ["follower_count", "engagement_rate", "tags_count", "bio_length", "niche", "location"]
    X = df[feature_cols]
    y = df["target_high_performer"]

    numeric_features = ["follower_count", "engagement_rate", "tags_count", "bio_length"]
    categorical_features = ["niche", "location"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    models = {
        "logistic_regression": LogisticRegression(max_iter=1000),
        "random_forest": RandomForestClassifier(n_estimators=300, random_state=42),
    }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    rows = []
    for model_name, model in models.items():
        pipeline = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        rows.append(
            {
                "model": model_name,
                "accuracy": round(accuracy_score(y_test, predictions), 4),
                "f1": round(f1_score(y_test, predictions), 4),
                "precision": round(precision_score(y_test, predictions), 4),
                "recall": round(recall_score(y_test, predictions), 4),
            }
        )

    results = pd.DataFrame(rows).sort_values(by="f1", ascending=False)
    results.to_csv(OUTPUT_DIR / "baseline_model_comparison.csv", index=False)
    return results


def write_synthetic_manifest(synthetic_ids: List[int]) -> None:
    manifest = {
        "is_synthetic_data_present": bool(synthetic_ids),
        "synthetic_record_count": len(synthetic_ids),
        "synthetic_record_ids": synthetic_ids,
        "note": "These records were generated in app/ds/src/eda_modeling.py and inserted through backend CRUD endpoints.",
    }
    with (DOCS_DIR / "synthetic_data_manifest.json").open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2)


def main() -> None:
    random.seed(42)
    np.random.seed(42)

    client = get_test_client()
    synthetic_ids = seed_synthetic_data_if_needed(client=client, minimum_rows=120)
    records = fetch_influencers(client)

    df = build_dataframe(records)
    run_eda(df)
    model_results = run_models(df)
    write_synthetic_manifest(synthetic_ids)

    print("EDA + modeling completed")
    print(model_results.to_string(index=False))


if __name__ == "__main__":
    main()
