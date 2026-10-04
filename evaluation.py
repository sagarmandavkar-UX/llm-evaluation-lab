"""Measure LLM quality with bootstrap intervals, error slices, and rater agreement."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def make_demo_judgments(seed: int = 11, n: int = 240) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    domains = rng.choice(["sql", "finance", "healthcare", "policy"], n)
    difficulties = rng.choice(["easy", "medium", "hard"], n, p=[0.35, 0.45, 0.20])
    rows = []
    profiles = [("compact", 0.78, 420, 0.002), ("balanced", 0.84, 780, 0.008), ("reasoning", 0.89, 1450, 0.025)]
    for model, base, latency, cost in profiles:
        for i, (domain, difficulty) in enumerate(zip(domains, difficulties)):
            p = base - {"easy": 0, "medium": 0.08, "hard": 0.22}[difficulty]
            correct = int(rng.random() < p)
            error = "none" if correct else rng.choice(["factual", "instruction", "calculation", "citation"])
            rater_2 = correct if rng.random() > 0.07 else 1 - correct
            confidence = float(np.clip(rng.normal(p + (0.05 if correct else -0.05), 0.10), 0.02, 0.98))
            rows.append((i, model, domain, difficulty, correct, rater_2, error, confidence, max(50, rng.normal(latency, latency * 0.18)), cost))
    return pd.DataFrame(rows, columns=["item_id", "model", "domain", "difficulty", "rater_1", "rater_2", "error_type", "confidence", "latency_ms", "cost_usd"])


def bootstrap_interval(values: np.ndarray, seed: int = 0, draws: int = 2000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = rng.choice(values, size=(draws, len(values)), replace=True).mean(axis=1)
    return tuple(np.quantile(means, [0.025, 0.975]).tolist())


def cohen_kappa(a: pd.Series, b: pd.Series) -> float:
    observed = float((a == b).mean())
    pa, pb = a.value_counts(normalize=True), b.value_counts(normalize=True)
    expected = sum(float(pa.get(v, 0) * pb.get(v, 0)) for v in set(pa.index) | set(pb.index))
    return (observed - expected) / (1 - expected) if expected < 1 else 1.0


def evaluate(judgments: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    records = []
    for model, group in judgments.groupby("model"):
        values = group["rater_1"].to_numpy(dtype=float)
        low, high = bootstrap_interval(values, seed=sum(map(ord, model)))
        record = {"model": model, "accuracy": values.mean(), "ci_low": low, "ci_high": high, "n": len(group)}
        if "confidence" in group:
            record["brier_score"] = float(np.mean((group["confidence"] - values) ** 2))
        if "latency_ms" in group:
            record["median_latency_ms"] = float(group["latency_ms"].median())
        if "cost_usd" in group:
            record["cost_per_correct"] = float(group["cost_usd"].sum() / max(group["rater_1"].sum(), 1))
        records.append(record)
    model_summary = pd.DataFrame(records).sort_values("accuracy", ascending=False)
    errors = (
        judgments.loc[judgments["error_type"] != "none"]
        .groupby(["model", "error_type"]).size().rename("errors").reset_index()
    )
    agreement = {"cohen_kappa": cohen_kappa(judgments["rater_1"], judgments["rater_2"])}
    return model_summary, errors, agreement


def validate_judgments(judgments: pd.DataFrame) -> dict[str, int | bool]:
    required = {"item_id", "model", "domain", "difficulty", "rater_1", "rater_2", "error_type"}
    missing = required.difference(judgments.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    duplicate_pairs = int(judgments.duplicated(["item_id", "model"]).sum())
    if duplicate_pairs:
        raise ValueError(f"Found {duplicate_pairs} duplicate item-model judgments")
    return {
        "rows": len(judgments),
        "items": int(judgments["item_id"].nunique()),
        "models": int(judgments["model"].nunique()),
        "complete_model_item_matrix": len(judgments) == judgments["item_id"].nunique() * judgments["model"].nunique(),
    }


def slice_scorecard(judgments: pd.DataFrame) -> pd.DataFrame:
    """Accuracy and sample size for every model/domain/difficulty slice."""
    return (
        judgments.groupby(["model", "domain", "difficulty"], as_index=False)
        .agg(accuracy=("rater_1", "mean"), n=("rater_1", "size"))
        .sort_values(["domain", "difficulty", "accuracy"], ascending=[True, True, False])
    )


def paired_model_differences(judgments: pd.DataFrame, seed: int = 29, draws: int = 2000) -> pd.DataFrame:
    """Paired bootstrap accuracy differences on the common item set."""
    matrix = judgments.pivot(index="item_id", columns="model", values="rater_1").dropna()
    rng = np.random.default_rng(seed)
    records = []
    models = list(matrix.columns)
    for i, challenger in enumerate(models):
        for baseline in models[i + 1:]:
            differences = matrix[challenger].to_numpy() - matrix[baseline].to_numpy()
            boot = rng.choice(differences, size=(draws, len(differences)), replace=True).mean(axis=1)
            records.append({
                "model_a": challenger,
                "model_b": baseline,
                "accuracy_difference": float(differences.mean()),
                "ci_low": float(np.quantile(boot, 0.025)),
                "ci_high": float(np.quantile(boot, 0.975)),
            })
    return pd.DataFrame(records)


def main() -> None:
    out = Path(__file__).parent / "outputs"
    out.mkdir(exist_ok=True)
    judgments = make_demo_judgments()
    quality = validate_judgments(judgments)
    summary, errors, agreement = evaluate(judgments)
    summary.to_csv(out / "model_scorecard.csv", index=False)
    errors.to_csv(out / "error_taxonomy.csv", index=False)
    slice_scorecard(judgments).to_csv(out / "slice_scorecard.csv", index=False)
    paired_model_differences(judgments).to_csv(out / "paired_comparisons.csv", index=False)
    (out / "rater_agreement.json").write_text(json.dumps({**agreement, "data_quality": quality}, indent=2))
    print(summary.to_string(index=False))
    print(json.dumps(agreement, indent=2))


if __name__ == "__main__":
    main()
