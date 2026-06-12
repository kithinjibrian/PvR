"""
src/analysis/plot.py

Generates three publication-ready figures from aggregated trial results.

Figures produced:
  1. position_vs_accuracy.png  — line chart, one line per context length
  2. accuracy_heatmap.png      — heatmap rows=context length, cols=position
  3. error_breakdown.png       — stacked bar chart, error types by position

Depends on: pandas, matplotlib, src/analysis/aggregate
Used by: scripts/04_analyze.py
"""

import logging
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# Colorblind-safe palette (tab10).
_COLORS = plt.cm.tab10.colors  # type: ignore[attr-defined]

_ERROR_TYPES = ["confabulation", "wrong_retrieval", "refusal", "format_error", "empty", "api_error"]


def plot_position_vs_accuracy(summary: pd.DataFrame, output_path: str) -> None:
    """Plots retrieval accuracy vs fractional position, one line per context length.

    Args:
        summary: DataFrame from accuracy_by_cell(), with columns
                 position_requested, context_length_target, accuracy, n_trials.
        output_path: Path where the PNG will be written.

    Returns:
        None. Saves the figure to output_path.

    Example:
        plot_position_vs_accuracy(summary, "data/results/figures/position_vs_accuracy.png")
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    ctx_lengths = sorted(summary["context_length_target"].unique())
    for i, ctx in enumerate(ctx_lengths):
        subset = summary[summary["context_length_target"] == ctx].sort_values("position_requested")
        positions = subset["position_requested"].tolist()
        accuracies = subset["accuracy"].tolist()
        counts = subset["n_trials"].tolist()

        # Standard error bars from binomial variance.
        errors = [
            np.sqrt(a * (1 - a) / n) if n > 0 else 0
            for a, n in zip(accuracies, counts)
        ]

        label = f"{ctx // 1024}k tokens"
        ax.errorbar(
            positions,
            accuracies,
            yerr=errors,
            marker="o",
            color=_COLORS[i % len(_COLORS)],
            label=label,
            capsize=4,
        )

    ax.set_xlabel("Fractional position of target fact")
    ax.set_ylabel("Retrieval accuracy")
    ax.set_title("Lost in the Middle: Retrieval Accuracy vs. Document Position")
    ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0% (start)", "25%", "50%", "75%", "100% (end)"])
    ax.set_ylim(-0.05, 1.05)
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    log.info("Saved position_vs_accuracy figure to %s", output_path)


def plot_accuracy_heatmap(summary: pd.DataFrame, output_path: str) -> None:
    """Plots a heatmap of accuracy, rows=context length, cols=fractional position.

    Args:
        summary: DataFrame from accuracy_by_cell().
        output_path: Path where the PNG will be written.

    Returns:
        None. Saves the figure to output_path.

    Example:
        plot_accuracy_heatmap(summary, "data/results/figures/accuracy_heatmap.png")
    """
    positions = sorted(summary["position_requested"].unique())
    ctx_lengths = sorted(summary["context_length_target"].unique())

    matrix = np.zeros((len(ctx_lengths), len(positions)))
    for i, ctx in enumerate(ctx_lengths):
        for j, pos in enumerate(positions):
            cell = summary[
                (summary["context_length_target"] == ctx)
                & (summary["position_requested"] == pos)
            ]
            matrix[i, j] = cell["accuracy"].iloc[0] if not cell.empty else float("nan")

    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(matrix, aspect="auto", vmin=0, vmax=1, cmap="RdYlGn")

    ax.set_xticks(range(len(positions)))
    ax.set_xticklabels([f"{p:.0%}" for p in positions])
    ax.set_yticks(range(len(ctx_lengths)))
    ax.set_yticklabels([f"{c // 1024}k" for c in ctx_lengths])
    ax.set_xlabel("Fractional position of target fact")
    ax.set_ylabel("Context length")
    ax.set_title("Retrieval Accuracy Heatmap")

    for i in range(len(ctx_lengths)):
        for j in range(len(positions)):
            val = matrix[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=9)

    fig.colorbar(im, ax=ax, label="Accuracy")
    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    log.info("Saved accuracy_heatmap figure to %s", output_path)


def plot_error_breakdown(df: pd.DataFrame, output_path: str) -> None:
    """Plots a stacked bar chart of error types by position, one subplot per context length.

    Args:
        df: Raw trial DataFrame from aggregate().
        output_path: Path where the PNG will be written.

    Returns:
        None. Saves the figure to output_path.

    Example:
        plot_error_breakdown(df, "data/results/figures/error_breakdown.png")
    """
    ctx_lengths = sorted(df["context_length_target"].unique())
    positions = sorted(df["position_requested"].unique())

    fig, axes = plt.subplots(
        1,
        len(ctx_lengths),
        figsize=(6 * len(ctx_lengths), 5),
        sharey=True,
    )

    if len(ctx_lengths) == 1:
        axes = [axes]

    for ax, ctx in zip(axes, ctx_lengths):
        subset = df[df["context_length_target"] == ctx].copy()
        subset["error_label"] = subset.apply(
            lambda row: "correct" if row["correct"] is True else (row["error_type"] or "unknown"),
            axis=1,
        )

        counts = (
            subset.groupby(["position_requested", "error_label"])
            .size()
            .unstack(fill_value=0)
        )

        all_labels = ["correct"] + _ERROR_TYPES
        for lbl in all_labels:
            if lbl not in counts.columns:
                counts[lbl] = 0
        counts = counts[all_labels]

        bottom = np.zeros(len(positions))
        for j, lbl in enumerate(all_labels):
            vals = [counts.loc[pos, lbl] if pos in counts.index else 0 for pos in positions]
            ax.bar(
                range(len(positions)),
                vals,
                bottom=bottom,
                label=lbl,
                color=_COLORS[j % len(_COLORS)],
            )
            bottom += np.array(vals, dtype=float)

        ax.set_title(f"{ctx // 1024}k context")
        ax.set_xticks(range(len(positions)))
        ax.set_xticklabels([f"{p:.0%}" for p in positions])
        ax.set_xlabel("Fractional position")

    axes[0].set_ylabel("Number of trials")
    axes[0].legend(loc="upper right", fontsize=8)

    fig.suptitle("Error Type Breakdown by Position")
    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    log.info("Saved error_breakdown figure to %s", output_path)
