from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Wire up backend imports so we can query the DB
APP_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = APP_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from db.connection import get_engine, wait_for_db
from db.crud import select_many

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_dataset_from_db() -> pd.DataFrame:
    """Pull influencer data from the live database."""
    engine = get_engine()
    wait_for_db(engine)

    rows = select_many(
        "influencers",
        columns=(
            "influencer_id",
            "full_name",
            "niche",
            "follower_count",
            "engagement_rate",
            "location",
            "is_synthetic",
        ),
        engine=engine,
    )
    if not rows:
        raise RuntimeError("No rows found in `influencers` table. Seed the DB first.")

    df = pd.DataFrame(rows)
    df.rename(columns={"influencer_id": "id", "full_name": "name"}, inplace=True)
    df["synthetic_data"] = df.pop("is_synthetic")


    df["target_high_performer"] = (
        df["engagement_rate"] >= df["engagement_rate"].median()
    ).astype(int)
    return df


def run_eda(df: pd.DataFrame) -> None:
    null_counts = df.isnull().sum().rename("null_count")
    null_counts.to_csv(OUTPUT_DIR / "null_counts.csv")

    corr_cols = [
        "follower_count",
        "engagement_rate",
        "target_high_performer",
    ]
    corr = df[corr_cols].corr()
    corr.to_csv(OUTPUT_DIR / "correlation_matrix.csv")

    plt.figure(figsize=(8, 5))
    sns.histplot(df["follower_count"], bins=25, kde=True)
    plt.title("Follower Count Distribution")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "distribution_follower_count.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.histplot(df["engagement_rate"], bins=20, kde=True, color="orange")
    plt.title("Engagement Rate Distribution")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "distribution_engagement_rate.png", dpi=150)
    plt.close()

    plt.figure(figsize=(7, 5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "correlation_heatmap.png", dpi=150)
    plt.close()


def train_and_compare_models(df: pd.DataFrame) -> pd.DataFrame:
    features = [
        "follower_count",
        "niche",
        "location",
    ]
    target = "target_high_performer"

    X = df[features]
    y = df[target]

    numeric_cols = ["follower_count"]
    categorical_cols = ["niche", "location"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_cols,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical_cols,
            ),
        ]
    )

    models = {
        "logistic_regression": LogisticRegression(max_iter=1000),
        "random_forest": RandomForestClassifier(n_estimators=250, random_state=42),
        "hist_gradient_boosting": HistGradientBoostingClassifier(random_state=42),
    }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    rows: list[dict[str, float | str]] = []
    for model_name, model in models.items():
        pipe = Pipeline([("prep", preprocessor), ("model", model)])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        rmse = mean_squared_error(y_test, preds) ** 0.5

        rows.append(
            {
                "model": model_name,
                "accuracy": round(accuracy_score(y_test, preds), 4),
                "f1": round(f1_score(y_test, preds), 4),
                "rmse": round(float(rmse), 4),
            }
        )

    results = pd.DataFrame(rows).sort_values(by="f1", ascending=False)
    results.to_csv(OUTPUT_DIR / "baseline_model_comparison.csv", index=False)
    return results


def main() -> None:
    df = fetch_dataset_from_db()
    df.to_csv(OUTPUT_DIR / "modeling_dataset.csv", index=False)
    run_eda(df)
    results = train_and_compare_models(df)
    print(f"EDA and modeling complete. {len(df)} influencers from DB.")
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
