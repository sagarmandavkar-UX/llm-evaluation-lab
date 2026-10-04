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
    for model, base in [("compact", 0.78), ("balanced", 0.84), ("reasoning", 0.89)]:
        for i, (domain, difficulty) in enumerate(zip(domains, difficulties)):
            p = base - {"easy": 0, "medium": 0.08, "hard": 0.22}[difficulty]
            correct = int(rng.random() < p)
            error = "none" if correct else rng.choice(["factual", "instruction", "calculation", "citation"])
            rater_2 = correct if rng.random() > 0.07 else 1 - correct
            rows.append((i, model, domain, difficulty, correct, rater_2, error))
    return pd.DataFrame(rows, columns=["item_id", "model", "domain", "difficulty", "rater_1", "rater_2", "error_type"])


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
        records.append({"model": model, "accuracy": values.mean(), "ci_low": low, "ci_high": high, "n": len(group)})
    model_summary = pd.DataFrame(records).sort_values("accuracy", ascending=False)
    errors = (
        judgments.loc[judgments["error_type"] != "none"]
        .groupby(["model", "error_type"]).size().rename("errors").reset_index()
    )
    agreement = {"cohen_kappa": cohen_kappa(judgments["rater_1"], judgments["rater_2"])}
    return model_summary, errors, agreement


def main() -> None:
    out = Path(__file__).parent / "outputs"
    out.mkdir(exist_ok=True)
    summary, errors, agreement = evaluate(make_demo_judgments())
    summary.to_csv(out / "model_scorecard.csv", index=False)
    errors.to_csv(out / "error_taxonomy.csv", index=False)
    (out / "rater_agreement.json").write_text(json.dumps(agreement, indent=2))
    print(summary.to_string(index=False))
    print(json.dumps(agreement, indent=2))


if __name__ == "__main__":
    main()
