"""
src/analysis/aggregate.py

Loads all per-trial JSON result files and aggregates them into DataFrames
for downstream plotting.

Depends on: pandas, json, os
Used by: scripts/04_analyze.py
"""

import json
import logging
import os
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)


def aggregate(results_dir: str) -> pd.DataFrame:
    """Loads all trial JSON files from results_dir into a single DataFrame.

    Skips files that cannot be parsed and logs a warning for each.

    Args:
        results_dir: Path to the directory containing per-trial JSON files.

    Returns:
        DataFrame with one row per trial and columns matching the result schema.
        Returns an empty DataFrame if no valid files are found.

    Example:
        df = aggregate("data/results/raw")
        print(df.columns.tolist())
    """
    records: list[dict[str, Any]] = []
    if not os.path.isdir(results_dir):
        log.warning("Results directory not found: %s", results_dir)
        return pd.DataFrame()

    for fname in sorted(os.listdir(results_dir)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(results_dir, fname)
        try:
            with open(path, encoding="utf-8") as f:
                records.append(json.load(f))
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("Skipping unreadable result file %s: %s", path, exc)

    if not records:
        log.warning("No valid trial result files found in %s", results_dir)
        return pd.DataFrame()

    df = pd.DataFrame(records)
    log.info("Loaded %d trial results from %s", len(df), results_dir)
    return df


def accuracy_by_cell(df: pd.DataFrame) -> pd.DataFrame:
    """Computes mean accuracy grouped by position_requested and context_length_target.

    Excludes trials where correct is None (API or injector errors).

    Args:
        df: DataFrame returned by aggregate().

    Returns:
        DataFrame with columns: position_requested, context_length_target,
        accuracy, n_trials, n_errors.

    Example:
        summary = accuracy_by_cell(df)
        print(summary)
    """
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["scored"] = df["correct"].notna()

    total = (
        df.groupby(["position_requested", "context_length_target"])
        .size()
        .reset_index(name="n_total")
    )

    valid = df[df["scored"]].copy()
    valid["correct_bool"] = valid["correct"].astype(bool)

    stats = (
        valid.groupby(["position_requested", "context_length_target"])
        .agg(accuracy=("correct_bool", "mean"), n_trials=("correct_bool", "count"))
        .reset_index()
    )

    result = stats.merge(total, on=["position_requested", "context_length_target"], how="left")
    result["n_errors"] = result["n_total"] - result["n_trials"]
    return result.drop(columns=["n_total"])
