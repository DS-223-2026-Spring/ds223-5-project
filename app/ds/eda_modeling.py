from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_dataset() -> pd.DataFrame:
    """Build example data with explicit synthetic labeling."""
    np.random.seed(42)

    # Base records can be treated as seed examples.
    base = pd.DataFrame(
        [
            {
                "name": "Alex Doe",
                "niche": "Tech",
                "follower_count": 50000,
                "engagement_rate": 4.5,
                "location": "New York",
                "campaign_conversions": 120,
                "synthetic_data": False,
            },
            {
                "name": "Jane Smith",
                "niche": "Fashion",
                "follower_count": 120000,
                "engagement_rate": 5.2,
                "location": "Los Angeles",
                "campaign_conversions": 240,
                "synthetic_data": False,
            },
        ]
    )

    # Synthetic rows used to make baseline modeling feasible.
    n_synth = 198
    synth = pd.DataFrame(
        {
            "name": [f"Synthetic Creator {i+1}" for i in range(n_synth)],
            "niche": np.random.choice(
                ["Tech", "Fashion", "Fitness", "Food", "Travel"], size=n_synth
            ),
            "follower_count": np.random.randint(3000, 300000, size=n_synth),
            "engagement_rate": np.round(np.random.uniform(1.0, 10.0, size=n_synth), 2),
            "location": np.random.choice(
                ["New York", "Los Angeles", "Austin", "Seattle", "Chicago"], size=n_synth
            ),
            "campaign_conversions": np.random.randint(5, 600, size=n_synth),
            "synthetic_data": True,
        }
    )

    df = pd.concat([base, synth], ignore_index=True)
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
        "campaign_conversions",
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
        "engagement_rate",
        "campaign_conversions",
        "niche",
        "location",
    ]
    target = "target_high_performer"

    X = df[features]
    y = df[target]

    numeric_cols = ["follower_count", "engagement_rate", "campaign_conversions"]
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
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_cols,
            ),
        ]
    )

    models = {
        "logistic_regression": LogisticRegression(max_iter=1000),
        "random_forest": RandomForestClassifier(n_estimators=250, random_state=42),
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
    df = build_dataset()
    df.to_csv(OUTPUT_DIR / "modeling_dataset.csv", index=False)
    run_eda(df)
    results = train_and_compare_models(df)
    print("EDA and modeling complete.")
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
