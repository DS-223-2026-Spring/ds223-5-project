from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

APP_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = APP_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(APP_DIR))

try:
    from db.connection import get_engine  # noqa: E402
    from db.crud import delete_many, insert_one, select_many, update_many  # noqa: E402
except ModuleNotFoundError:  # pragma: no cover
    try:
        from backend.db.connection import get_engine  # type: ignore[no-redef]  # noqa: E402
        from backend.db.crud import (  # type: ignore[no-redef]  # noqa: E402
            delete_many,
            insert_one,
            select_many,
            update_many,
        )
    except ModuleNotFoundError:
        get_engine = None  # type: ignore[assignment]
        delete_many = None  # type: ignore[assignment]
        insert_one = None  # type: ignore[assignment]
        select_many = None  # type: ignore[assignment]
        update_many = None  # type: ignore[assignment]


RUN_KEY_DEFAULT = "influencer_high_performer_v1"
FEATURE_SCHEMA_VERSION_DEFAULT = "v1_exclude_engagement_rate_with_top_tags"


def has_backend_dependencies() -> bool:
    return all(
        func is not None
        for func in (get_engine, delete_many, insert_one, select_many, update_many)
    )


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_feature_name(name: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z_]+", "_", name).strip("_")
    return s or "unknown"


def _tag_feature_col(tag: str) -> str:
    return f"tag__{_sanitize_feature_name(tag)}"


def _coerce_tags(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if x is not None]
    if isinstance(value, tuple):
        return [str(x) for x in value if x is not None]
    if isinstance(value, str):
        raw = value.strip()
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed if x is not None]
            except json.JSONDecodeError:
                pass
        if "," in raw:
            return [p.strip() for p in raw.split(",") if p.strip()]
        return [raw] if raw else []
    return [str(value)]


def ensure_model_output_tables(engine: Any) -> None:
    from sqlalchemy import text

    ddl = [
        """
        CREATE TABLE IF NOT EXISTS model_runs (
          id BIGSERIAL PRIMARY KEY,
          run_key TEXT NOT NULL UNIQUE,
          model_name TEXT NOT NULL,
          feature_schema_version TEXT NOT NULL,
          target_definition TEXT NOT NULL,
          dataset_size INTEGER NOT NULL,
          metrics_accuracy DOUBLE PRECISION,
          metrics_f1 DOUBLE PRECISION,
          metrics_roc_auc DOUBLE PRECISION,
          target_median_engagement_rate DOUBLE PRECISION NOT NULL,
          top_tags_json TEXT,
          model_artifact BYTEA,
          artifact_hash TEXT,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS influencer_predictions (
          id BIGSERIAL PRIMARY KEY,
          model_run_id BIGINT NOT NULL,
          influencer_id BIGINT NOT NULL,
          predicted_label SMALLINT NOT NULL CHECK (predicted_label IN (0, 1)),
          predicted_proba DOUBLE PRECISION NOT NULL CHECK (predicted_proba >= 0 AND predicted_proba <= 1),
          confidence_score DOUBLE PRECISION NOT NULL,
          segment_label TEXT NOT NULL,
          is_recommended BOOLEAN NOT NULL,
          target_high_performer_true SMALLINT CHECK (target_high_performer_true IN (0, 1)),
          engagement_rate NUMERIC(5, 2) CHECK (engagement_rate >= 0 AND engagement_rate <= 100),
          follower_count INTEGER CHECK (follower_count >= 0),
          niche TEXT,
          location TEXT,
          tag_count INTEGER CHECK (tag_count >= 0),
          bio_length INTEGER CHECK (bio_length >= 0),
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          CONSTRAINT uq_influencer_predictions UNIQUE (model_run_id, influencer_id)
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_influencer_predictions_model_run_id
        ON influencer_predictions (model_run_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_influencer_predictions_influencer_id
        ON influencer_predictions (influencer_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_model_runs_run_key ON model_runs (run_key);
        """,
    ]

    with engine.begin() as conn:
        for stmt in ddl:
            conn.execute(text(stmt))


def fetch_influencers(engine: Any, limit: Optional[int] = None) -> pd.DataFrame:
    db_columns = [
        "influencer_id",
        "niche",
        "follower_count",
        "engagement_rate",
        "location",
        "content_formats",
        "bio",
    ]
    rows = select_many(
        "influencers",
        columns=db_columns,
        limit=limit,
        engine=engine,
    )
    
    df_columns = [
        "id",
        "niche",
        "follower_count",
        "engagement_rate",
        "location",
        "content_format_tags",
        "bio",
    ]
    if not rows:
        return pd.DataFrame(columns=df_columns)
        
    df = pd.DataFrame(rows)
    df.rename(columns={"influencer_id": "id", "content_formats": "content_format_tags"}, inplace=True)
    df["content_format_tags"] = df["content_format_tags"].apply(_coerce_tags)
    df["bio"] = df.get("bio")
    return df


def compute_top_tags(df: pd.DataFrame, top_k: int = 15, min_freq: int = 2) -> List[str]:
    counter: Counter[str] = Counter()
    for tags in df["content_format_tags"].tolist():
        counter.update(tags)
    filtered = [(t, c) for t, c in counter.items() if c >= min_freq]
    filtered.sort(key=lambda x: (-x[1], x[0]))
    tags = [t for t, _c in filtered][:top_k]
    return tags


def build_feature_dataframe(
    df: pd.DataFrame,
    *,
    top_tags: Sequence[str],
) -> pd.DataFrame:
    engineered = pd.DataFrame(index=df.index)
    engineered["follower_count"] = pd.to_numeric(df["follower_count"], errors="coerce")
    engineered["tag_count"] = df["content_format_tags"].apply(lambda tags: len(tags) if tags else 0)
    engineered["bio_length"] = df["bio"].fillna("").astype(str).apply(len)
    engineered["has_bio"] = (engineered["bio_length"] > 0).astype(int)

    for tag in top_tags:
        engineered[_tag_feature_col(tag)] = df["content_format_tags"].apply(lambda tags: 1 if (tags and tag in tags) else 0)

    engineered["niche"] = df["niche"].astype(str)
    engineered["location"] = df["location"].astype(str)
    return engineered


def build_target(
    df: pd.DataFrame,
    *,
    median_engagement_rate: Optional[float] = None,
) -> Tuple[pd.Series, float]:
    if median_engagement_rate is None:
        median_engagement_rate = float(pd.to_numeric(df["engagement_rate"], errors="coerce").median())
    y = (pd.to_numeric(df["engagement_rate"], errors="coerce") >= median_engagement_rate).astype(int)
    return y, float(median_engagement_rate)


def compute_segments(proba: np.ndarray, n_bins: int = 3) -> List[str]:
    proba_s = pd.Series(proba)
    labels = ["low", "medium", "high"][:n_bins]
    if n_bins == 3:
        try:
            seg = pd.qcut(proba_s, q=[0, 0.33, 0.66, 1], labels=labels, duplicates="drop")
            seg = seg.astype(str)
            return seg.tolist()
        except Exception:
            pass
    out: List[str] = []
    for p in proba:
        if p >= 0.66:
            out.append("high")
        elif p >= 0.33:
            out.append("medium")
        else:
            out.append("low")
    return out


@dataclass(frozen=True)
class ModelCandidateResult:
    model_name: str
    mean_roc_auc_cv: float


def train_and_select_best_model(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    tag_feature_cols: Sequence[str],
    seed: int = 42,
) -> Tuple[Pipeline, Dict[str, Any]]:
    numeric_cols = ["follower_count", "tag_count", "bio_length", "has_bio"] + list(tag_feature_cols)
    categorical_cols = ["niche", "location"]

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
                numeric_cols,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "onehot",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                categorical_cols,
            ),
        ],
        remainder="drop",
    )

    candidates: List[Tuple[str, Any]] = [
        (
            "logistic_regression",
            LogisticRegression(max_iter=5000, class_weight="balanced", random_state=seed),
        ),
        (
            "random_forest",
            RandomForestClassifier(
                n_estimators=400,
                random_state=seed,
                class_weight="balanced_subsample",
            ),
        ),
        (
            "hist_gradient_boosting",
            HistGradientBoostingClassifier(random_state=seed),
        ),
    ]

    if int(y.nunique()) < 2:
        dummy = DummyClassifier(strategy="most_frequent")
        best_pipe: Pipeline = Pipeline([("prep", preprocessor), ("model", dummy)])
        best_pipe.fit(X, y)
        meta = {
            "selected_model_name": "dummy_most_frequent",
            "metrics": {
                "roc_auc": None,
                "accuracy": None,
                "f1": None,
            },
        }
        return best_pipe, meta

    counts = y.value_counts()
    min_class = int(counts.min())
    n_splits = max(2, min(5, min_class))
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=seed,
        stratify=y,
    )

    candidate_scores: List[Dict[str, Any]] = []
    for name, model in candidates:
        pipe = Pipeline([("prep", preprocessor), ("model", model)])
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)

        proba: Optional[np.ndarray] = None
        if hasattr(pipe, "predict_proba"):
            proba = pipe.predict_proba(X_test)[:, 1]

        if proba is not None and len(np.unique(y_test)) == 2:
            roc_auc = float(roc_auc_score(y_test, proba))
        else:
            roc_auc = float("nan")

        f1 = float(f1_score(y_test, y_pred))
        acc = float(accuracy_score(y_test, y_pred))
        candidate_scores.append(
            {
                "model_name": name,
                "roc_auc": roc_auc,
                "f1": f1,
                "accuracy": acc,
            }
        )

    def _key(d: Dict[str, Any]) -> Tuple[float, float, float]:
        roc = d["roc_auc"]
        if roc is None or (isinstance(roc, float) and np.isnan(roc)):
            roc = -1.0
        return (roc, d["f1"], d["accuracy"])

    selected = max(candidate_scores, key=_key)
    selected_name = selected["model_name"]
    selected_model = next(m for n, m in candidates if n == selected_name)

    best_pipe = Pipeline([("prep", preprocessor), ("model", selected_model)])
    best_pipe.fit(X, y)

    meta = {
        "selected_model_name": selected_name,
        "metrics": {
            "roc_auc": selected["roc_auc"],
            "f1": selected["f1"],
            "accuracy": selected["accuracy"],
        },
    }
    return best_pipe, meta


def serialize_artifact(pipeline: Pipeline) -> Tuple[bytes, str]:
    payload = pickle.dumps(pipeline)
    sha = hashlib.sha256(payload).hexdigest()
    return payload, sha


def get_or_create_model_run_id(
    *,
    engine: Any,
    run_key: str,
    model_name: str,
    feature_schema_version: str,
    target_definition: str,
    dataset_size: int,
    target_median_engagement_rate: float,
    top_tags: Sequence[str],
    metrics: Dict[str, Any],
    model_artifact: Optional[bytes],
    artifact_hash: Optional[str],
) -> int:
    existing = select_many("model_runs", where={"run_key": run_key}, columns=("id",), engine=engine)
    updated_at = _utc_now_iso()

    data_row = {
        "run_key": run_key,
        "model_name": model_name,
        "feature_schema_version": feature_schema_version,
        "target_definition": target_definition,
        "dataset_size": int(dataset_size),
        "metrics_accuracy": metrics.get("accuracy"),
        "metrics_f1": metrics.get("f1"),
        "metrics_roc_auc": metrics.get("roc_auc"),
        "target_median_engagement_rate": float(target_median_engagement_rate),
        "top_tags_json": json.dumps(list(top_tags)),
        "model_artifact": model_artifact,
        "artifact_hash": artifact_hash,
        "updated_at": updated_at,
    }

    if not existing:
        res = insert_one("model_runs", data_row, engine=engine, returning=("id",))
        return int(res["id"])

    run_id = int(existing[0]["id"])
    update_many("model_runs", data=data_row, where={"id": run_id}, engine=engine)
    return run_id


def store_predictions(
    *,
    engine: Any,
    model_run_id: int,
    df_raw: pd.DataFrame,
    engineered_df: pd.DataFrame,
    proba: np.ndarray,
    y_true: pd.Series,
    top_tags: Sequence[str],
) -> int:
    segments = compute_segments(proba, n_bins=3)
    predicted_label = (proba >= 0.5).astype(int)
    is_recommended = [seg == "high" for seg in segments]

    tag_feature_cols = [_tag_feature_col(t) for t in top_tags]
    delete_many("influencer_predictions", where={"model_run_id": model_run_id}, engine=engine)

    inserted = 0
    for idx in range(len(df_raw)):
        row = df_raw.iloc[idx]
        eng_row = engineered_df.iloc[idx]
        follower_count = int(row["follower_count"]) if not pd.isna(row["follower_count"]) else None
        niche = row["niche"]
        location = row["location"]
        engagement_rate = float(row["engagement_rate"]) if not pd.isna(row["engagement_rate"]) else None
        tag_count = int(eng_row["tag_count"]) if "tag_count" in engineered_df.columns else None
        bio_length = int(eng_row["bio_length"]) if "bio_length" in engineered_df.columns else None

        payload = {
            "model_run_id": int(model_run_id),
            "influencer_id": int(row["id"]),
            "predicted_label": int(predicted_label[idx]),
            "predicted_proba": float(proba[idx]),
            "confidence_score": float(proba[idx]),
            "segment_label": str(segments[idx]),
            "is_recommended": bool(is_recommended[idx]),
            "target_high_performer_true": int(y_true.iloc[idx]),
            "engagement_rate": engagement_rate,
            "follower_count": follower_count,
            "niche": niche,
            "location": location,
            "tag_count": tag_count,
            "bio_length": bio_length,
        }
        insert_one("influencer_predictions", payload, engine=engine, returning=())
        inserted += 1
    return inserted


def train_and_store(
    *,
    run_key: str = RUN_KEY_DEFAULT,
    feature_schema_version: str = FEATURE_SCHEMA_VERSION_DEFAULT,
    top_k_tags: int = 15,
    min_tag_freq: int = 2,
    db_limit: Optional[int] = None,
    seed: int = 42,
    offline: bool = False,
) -> Dict[str, Any]:
    rng = np.random.default_rng(seed)
    backend_ready = has_backend_dependencies()

    if not offline and not backend_ready:
        offline = True

    if offline:
        n = int(db_limit) if db_limit is not None else 250
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

        follower_count = rng.integers(1000, 300000, size=n)
        niche = rng.choice(niche_choices, size=n)
        location = rng.choice(location_choices, size=n)
        tags = rng.choice(tag_vocab, size=(n, 3), replace=True)
        content_format_tags = [list(dict.fromkeys(row.tolist())) for row in tags]
        bio = rng.choice(bios, size=n)

        niche_effect = np.array([1.2 if x == "Tech" else 0.9 for x in niche], dtype=float)
        location_effect = np.array([1.0 if x in {"New York", "Los Angeles"} else 0.85 for x in location], dtype=float)
        tag_effect = np.array([1.0 + 0.03 * len(t) for t in content_format_tags], dtype=float)

        raw = (
            1.5
            + 0.000004 * follower_count
            + 2.0 * niche_effect
            + 1.0 * location_effect
            + 1.2 * (tag_effect - 1.0)
            + rng.normal(0, 1.0, size=n)
        )
        engagement_rate = np.clip(raw, 0, 100)

        df = pd.DataFrame(
            {
                "id": np.arange(1, n + 1),
                "niche": niche,
                "follower_count": follower_count,
                "engagement_rate": engagement_rate,
                "location": location,
                "content_format_tags": content_format_tags,
                "bio": bio,
            }
        )
    else:
        if not backend_ready:
            raise RuntimeError(
                "DB mode requires backend dependencies (SQLAlchemy + CRUD helpers). "
                "Install app/backend/requirements.txt or run with --offline."
            )
        engine = get_engine()
        ensure_model_output_tables(engine)

        df = fetch_influencers(engine, limit=db_limit)
        if df.empty:
            raise RuntimeError(
                "No rows found in `influencers` table. Load influencer data before running DS scripts."
            )

    df["niche"] = df["niche"].astype(str)
    df["location"] = df["location"].astype(str)
    df["follower_count"] = pd.to_numeric(df["follower_count"], errors="coerce")
    df["engagement_rate"] = pd.to_numeric(df["engagement_rate"], errors="coerce")

    y, median_engagement_rate = build_target(df)
    top_tags = compute_top_tags(df, top_k=top_k_tags, min_freq=min_tag_freq)
    engineered = build_feature_dataframe(df, top_tags=top_tags)

    tag_feature_cols = [_tag_feature_col(t) for t in top_tags]
    best_pipe, meta = train_and_select_best_model(
        engineered,
        y,
        tag_feature_cols=tag_feature_cols,
        seed=seed,
    )

    proba = best_pipe.predict_proba(engineered)[:, 1]

    if offline:
        segments = compute_segments(proba, n_bins=3)
        return {
            "offline": True,
            "selected_model_name": meta["selected_model_name"],
            "metrics": meta["metrics"],
            "dataset_size": int(len(df)),
            "median_engagement_rate": float(median_engagement_rate),
            "top_tags": top_tags,
            "segment_counts": dict(pd.Series(segments).value_counts().to_dict()),
        }

    artifact_bytes, artifact_hash = serialize_artifact(best_pipe)

    run_id = get_or_create_model_run_id(
        engine=engine,
        run_key=run_key,
        model_name=str(meta["selected_model_name"]),
        feature_schema_version=feature_schema_version,
        target_definition="target_high_performer = engagement_rate >= median(engagement_rate)",
        dataset_size=int(len(df)),
        target_median_engagement_rate=float(median_engagement_rate),
        top_tags=top_tags,
        metrics=meta["metrics"],
        model_artifact=artifact_bytes,
        artifact_hash=artifact_hash,
    )

    inserted = store_predictions(
        engine=engine,
        model_run_id=run_id,
        df_raw=df,
        engineered_df=engineered,
        proba=proba,
        y_true=y,
        top_tags=top_tags,
    )

    return {
        "model_run_id": run_id,
        "selected_model_name": meta["selected_model_name"],
        "metrics": meta["metrics"],
        "dataset_size": int(len(df)),
        "median_engagement_rate": float(median_engagement_rate),
        "top_tags": top_tags,
        "predictions_inserted": inserted,
    }


def predict_and_store(
    *,
    run_key: str = RUN_KEY_DEFAULT,
    db_limit: Optional[int] = None,
) -> Dict[str, Any]:
    if not has_backend_dependencies():
        raise RuntimeError(
            "DB mode requires backend dependencies (SQLAlchemy + CRUD helpers). "
            "Install app/backend/requirements.txt."
        )
    engine = get_engine()
    ensure_model_output_tables(engine)

    runs = select_many("model_runs", where={"run_key": run_key}, engine=engine)
    if not runs:
        raise RuntimeError(f"No `model_runs` row found for run_key={run_key!r}. Run training first.")
    run = runs[0]
    model_run_id = int(run["id"])

    if run.get("model_artifact") is None:
        raise RuntimeError("This model_run row has no stored model_artifact BYTEA. Re-run training.")

    pipeline: Pipeline = pickle.loads(run["model_artifact"])
    top_tags = json.loads(run["top_tags_json"]) if run.get("top_tags_json") else []

    df = fetch_influencers(engine, limit=db_limit)
    if df.empty:
        raise RuntimeError("No rows found in `influencers` table.")

    df["niche"] = df["niche"].astype(str)
    df["location"] = df["location"].astype(str)
    df["follower_count"] = pd.to_numeric(df["follower_count"], errors="coerce")
    df["engagement_rate"] = pd.to_numeric(df["engagement_rate"], errors="coerce")

    median_engagement_rate = float(run["target_median_engagement_rate"])
    y, _ = build_target(df, median_engagement_rate=median_engagement_rate)
    engineered = build_feature_dataframe(df, top_tags=top_tags)

    proba = pipeline.predict_proba(engineered)[:, 1]
    inserted = store_predictions(
        engine=engine,
        model_run_id=model_run_id,
        df_raw=df,
        engineered_df=engineered,
        proba=proba,
        y_true=y,
        top_tags=top_tags,
    )

    return {
        "model_run_id": model_run_id,
        "predictions_inserted": inserted,
        "selected_model_name": run.get("model_name"),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train/infer influencer high-performer model and persist outputs to DB.")
    parser.add_argument("--run-key", default=RUN_KEY_DEFAULT)
    parser.add_argument("--top-k-tags", type=int, default=15)
    parser.add_argument("--min-tag-freq", type=int, default=2)
    parser.add_argument("--db-limit", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--offline", action="store_true", help="Run with synthetic data (no DB read/write).")
    parser.set_defaults(offline=not has_backend_dependencies())
    return parser


def main_train() -> None:
    args = build_arg_parser().parse_args()
    if args.offline and not has_backend_dependencies():
        print(
            "Backend dependencies not found; running in offline mode. "
            "Install app/backend/requirements.txt to enable DB mode."
        )
    res = train_and_store(
        run_key=args.run_key,
        top_k_tags=args.top_k_tags,
        min_tag_freq=args.min_tag_freq,
        db_limit=args.db_limit,
        seed=args.seed,
        offline=args.offline,
    )
    print(json.dumps(res, indent=2))


def main_predict() -> None:
    args = build_arg_parser().parse_args()
    res = predict_and_store(run_key=args.run_key, db_limit=args.db_limit)
    print(json.dumps(res, indent=2))

