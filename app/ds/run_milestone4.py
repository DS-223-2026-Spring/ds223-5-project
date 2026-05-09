from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.pipeline import Pipeline

from modeling_pipeline import (
    build_feature_dataframe,
    build_target,
    compute_segments,
    compute_top_tags,
    train_and_select_best_model,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = OUTPUT_DIR / "model.pkl"


def build_repeatable_dataset(*, seed: int, n_samples: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    niche_choices = ["Tech", "Fashion", "Fitness", "Food", "Travel"]
    location_choices = ["New York", "Los Angeles", "Austin", "Seattle", "Chicago"]
    tag_vocab = ["Video", "Blog", "Photo", "Reels", "Podcast", "Live", "Tutorials"]
    bios = [
        "Tech enthusiast and reviewer.",
        "Fashion addict and lifestyle creator.",
        "Fitness coach and nutrition nerd.",
        "Food blogger sharing recipes.",
        "Travel storyteller and guide.",
    ]

    follower_count = rng.integers(1000, 300000, size=n_samples)
    niche = rng.choice(niche_choices, size=n_samples)
    location = rng.choice(location_choices, size=n_samples)
    tags = rng.choice(tag_vocab, size=(n_samples, 3), replace=True)
    content_format_tags = [list(dict.fromkeys(row.tolist())) for row in tags]
    bio = rng.choice(bios, size=n_samples)

    niche_effect = np.array([1.2 if x == "Tech" else 0.9 for x in niche], dtype=float)
    location_effect = np.array(
        [1.0 if x in {"New York", "Los Angeles"} else 0.85 for x in location], dtype=float
    )
    tag_effect = np.array([1.0 + 0.03 * len(t) for t in content_format_tags], dtype=float)

    raw = (
        1.5
        + 0.000004 * follower_count
        + 2.0 * niche_effect
        + 1.0 * location_effect
        + 1.2 * (tag_effect - 1.0)
        + rng.normal(0, 1.0, size=n_samples)
    )
    engagement_rate = np.clip(raw, 0, 100)

    return pd.DataFrame(
        {
            "id": np.arange(1, n_samples + 1),
            "niche": niche,
            "follower_count": follower_count,
            "engagement_rate": engagement_rate,
            "location": location,
            "content_format_tags": content_format_tags,
            "bio": bio,
        }
    )


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


def run_milestone4(*, seed: int, n_samples: int, top_k_tags: int, min_tag_freq: int) -> Dict[str, Any]:
    df = build_repeatable_dataset(seed=seed, n_samples=n_samples)
    y, median_engagement_rate = build_target(df)
    top_tags = compute_top_tags(df, top_k=top_k_tags, min_freq=min_tag_freq)
    engineered = build_feature_dataframe(df, top_tags=top_tags)
    tag_feature_cols = [f"tag__{tag}" for tag in top_tags]

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

    # CSV outputs for frontend integration.
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

    # PNG outputs for frontend integration.
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
    parser.add_argument("--n-samples", type=int, default=250)
    parser.add_argument("--top-k-tags", type=int, default=15)
    parser.add_argument("--min-tag-freq", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run_milestone4(
        seed=args.seed,
        n_samples=args.n_samples,
        top_k_tags=args.top_k_tags,
        min_tag_freq=args.min_tag_freq,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
