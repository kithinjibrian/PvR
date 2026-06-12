"""
scripts/04_analyze.py

Loads trial results from data/results/raw/, aggregates them, and generates
three publication-ready figures in data/results/figures/.

Usage:
  uv run python scripts/04_analyze.py
  uv run python scripts/04_analyze.py --results-dir data/results/raw

Depends on: src/analysis/aggregate, src/analysis/plot
Used by: human operator after experiment run completes
"""

import argparse
import logging
import sys

from src.analysis.aggregate import accuracy_by_cell, aggregate
from src.analysis.plot import plot_accuracy_heatmap, plot_error_breakdown, plot_position_vs_accuracy

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

FIGURES_DIR = "data/results/figures"


def main() -> None:
    """Entry point for the analysis script."""
    parser = argparse.ArgumentParser(description="Generate figures from experiment results.")
    parser.add_argument(
        "--results-dir",
        default="data/results/raw",
        help="Directory containing per-trial JSON result files.",
    )
    args = parser.parse_args()

    df = aggregate(args.results_dir)
    if df.empty:
        log.error("No results found in %s — run the experiment first.", args.results_dir)
        sys.exit(1)

    log.info("Loaded %d trials.", len(df))

    summary = accuracy_by_cell(df)
    if summary.empty:
        log.error("No scored trials available for plotting.")
        sys.exit(1)

    plot_position_vs_accuracy(summary, f"{FIGURES_DIR}/position_vs_accuracy.png")
    plot_accuracy_heatmap(summary, f"{FIGURES_DIR}/accuracy_heatmap.png")
    plot_error_breakdown(df, f"{FIGURES_DIR}/error_breakdown.png")

    log.info("All figures written to %s/", FIGURES_DIR)


if __name__ == "__main__":
    main()
