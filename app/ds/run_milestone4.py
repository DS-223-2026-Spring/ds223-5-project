from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.pipeline import Pipeline

# Wire up backend imports for DB access
APP_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = APP_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from db.connection import get_engine, wait_for_db
from db.crud import select_many

from modeling_pipeline import (
    _tag_feature_col,
    build_feature_dataframe,
    build_target,
    compute_segments,
    compute_top_tags,
    train_and_select_best_model,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = OUTPUT_DIR / "model.pkl"


def _coerce_tags(val):
    """Convert comma-separated string to list of tag strings."""
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [t.strip() for t in val.split(",") if t.strip()]
    return []


def fetch_dataset_from_db() -> pd.DataFrame:
    """Pull influencer data from the live database."""
    engine = get_engine()
    wait_for_db(engine)

    rows = select_many(
        "influencers",
        columns=(
            "influencer_id",
            "niche",
            "follower_count",
            "engagement_rate",
            "location",
            "content_formats",
            "bio",
        ),
        engine=engine,
    )
    if not rows:
        raise RuntimeError("No rows found in `influencers` table. Seed the DB first.")

    df = pd.DataFrame(rows)
    df.rename(columns={"influencer_id": "id", "content_formats": "content_format_tags"}, inplace=True)
    df["content_format_tags"] = df["content_format_tags"].apply(_coerce_tags)
    return df


def _save_plot_distribution(series: pd.Series, *, title: str, xlabel: str, output_name: str) -> None:
    plt.figure(figsize=(8, 5))
    plt.hist(series, bins=25, alpha=0.8, edgecolor="black")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150)
    plt.close()


def _save_plot_bar(df: pd.DataFrame, *, x_col: str, y_col: str, title: str, output_name: str) -> None:
    plt.figure(figsize=(8, 5))
    plt.bar(df[x_col], df[y_col], color="#1f77b4")
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150)
    plt.close()


def _build_feature_importance_table(model: Pipeline) -> pd.DataFrame:
    prep = model.named_steps["prep"]
    estimator = model.named_steps["model"]
    feature_names = prep.get_feature_names_out()

    if hasattr(estimator, "feature_importances_"):
        values = np.asarray(estimator.feature_importances_, dtype=float)
        metric_name = "importance"
    elif hasattr(estimator, "coef_"):
        values = np.asarray(estimator.coef_[0], dtype=float)
        metric_name = "coefficient"
    else:
        return pd.DataFrame(columns=["feature", "value"])

    table = pd.DataFrame({"feature": feature_names, "value": values})
    table["abs_value"] = table["value"].abs()
    table = table.sort_values("abs_value", ascending=False).drop(columns=["abs_value"])
    table = table.rename(columns={"value": metric_name})
    return table


def run_milestone4(*, seed: int, top_k_tags: int, min_tag_freq: int) -> Dict[str, Any]:
    df = fetch_dataset_from_db()
    y, median_engagement_rate = build_target(df)
    top_tags = compute_top_tags(df, top_k=top_k_tags, min_freq=min_tag_freq)
    engineered = build_feature_dataframe(df, top_tags=top_tags)
    tag_feature_cols = [_tag_feature_col(tag) for tag in top_tags]

    pipeline, meta = train_and_select_best_model(
        engineered,
        y,
        tag_feature_cols=tag_feature_cols,
        seed=seed,
    )
    proba = pipeline.predict_proba(engineered)[:, 1]
    pred = (proba >= 0.5).astype(int)
    segments = compute_segments(proba, n_bins=3)

    dump(pipeline, MODEL_PATH)

    # CSV outputs for downstream tooling
    summary_df = pd.DataFrame(
        [
            {
                "selected_model_name": meta["selected_model_name"],
                "dataset_size": int(len(df)),
                "median_engagement_rate": float(median_engagement_rate),
                "accuracy": meta["metrics"]["accuracy"],
                "f1": meta["metrics"]["f1"],
                "roc_auc": meta["metrics"]["roc_auc"],
            }
        ]
    )
    summary_df.to_csv(OUTPUT_DIR / "model_performance_summary.csv", index=False)

    predictions_df = pd.DataFrame(
        {
            "id": df["id"],
            "niche": df["niche"],
            "location": df["location"],
            "follower_count": df["follower_count"],
            "engagement_rate": df["engagement_rate"],
            "predicted_label": pred,
            "predicted_probability": proba,
            "segment": segments,
        }
    )
    predictions_df.to_csv(OUTPUT_DIR / "predictions.csv", index=False)

    segment_summary = (
        predictions_df.groupby("segment", as_index=False)
        .agg(count=("segment", "count"), avg_probability=("predicted_probability", "mean"))
        .sort_values("count", ascending=False)
    )
    segment_summary.to_csv(OUTPUT_DIR / "segment_summary.csv", index=False)

    top_tags_df = pd.DataFrame({"tag": top_tags})
    top_tags_df.to_csv(OUTPUT_DIR / "top_tags.csv", index=False)

    feature_importance_df = _build_feature_importance_table(pipeline)
    if not feature_importance_df.empty:
        feature_importance_df.to_csv(OUTPUT_DIR / "feature_importance.csv", index=False)

    # PNG outputs
    _save_plot_distribution(
        df["engagement_rate"],
        title="Engagement Rate Distribution",
        xlabel="Engagement Rate",
        output_name="engagement_rate_distribution.png",
    )
    _save_plot_distribution(
        pd.Series(proba),
        title="Predicted Probability Distribution",
        xlabel="Predicted Probability",
        output_name="predicted_probability_distribution.png",
    )
    _save_plot_bar(
        segment_summary,
        x_col="segment",
        y_col="count",
        title="Predicted Segment Counts",
        output_name="segment_counts.png",
    )

    results = {
        "model_path": str(MODEL_PATH),
        "outputs_dir": str(OUTPUT_DIR),
        "selected_model_name": meta["selected_model_name"],
        "metrics": meta["metrics"],
        "dataset_size": int(len(df)),
    }
    with (OUTPUT_DIR / "run_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Milestone 4: train final model, save model.pkl, and export PNG/CSV artifacts."
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--top-k-tags", type=int, default=15)
    parser.add_argument("--min-tag-freq", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run_milestone4(
        seed=args.seed,
        top_k_tags=args.top_k_tags,
        min_tag_freq=args.min_tag_freq,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
