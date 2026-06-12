"""
scripts/03_run_experiment.py

Runs the full Lost-in-the-Middle retrieval experiment. Builds the trial matrix,
skips already-completed trials (--resume), and writes one JSON result file per
trial before moving to the next.

Usage:
  uv run python scripts/03_run_experiment.py
  uv run python scripts/03_run_experiment.py --dry-run
  uv run python scripts/03_run_experiment.py --resume
  uv run python scripts/03_run_experiment.py --subset 5

Depends on: anthropic, dotenv, src/experiment/designer, src/experiment/runner
Used by: human operator or CI
"""

import argparse
import json
import logging
import os
import sys
import time

import anthropic
from dotenv import load_dotenv

from src.experiment.designer import build_trial_matrix
from src.experiment.runner import run_trial

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

CONFIG = {
    "positions": [0.0, 0.25, 0.5, 0.75, 1.0],
    "context_lengths": [16384, 65536],
    "facts_per_cell": 10,
    "trials_per_fact": 1,
    "model": "claude-sonnet-4-6",
    "max_tokens": 100,
    "temperature": 0,
    "filler_path": "data/filler/corpus.txt",
    "facts_path": "data/facts/facts.json",
    "results_dir": "data/results/raw",
    "scorer": "exact",
    "requests_per_minute": 50,
    "retry_attempts": 3,
    "retry_delay_seconds": 5,
}


def main() -> None:
    """Entry point for the experiment runner."""
    parser = argparse.ArgumentParser(description="Run the Lost-in-the-Middle experiment.")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print trial matrix and exit without API calls.",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Skip trials whose result files already exist.",
    )
    parser.add_argument(
        "--subset", type=int, default=None, metavar="N",
        help="Run only the first N trials.",
    )
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key and not args.dry_run:
        log.error("ANTHROPIC_API_KEY environment variable is not set. Aborting.")
        sys.exit(1)

    with open(CONFIG["facts_path"], encoding="utf-8") as f:
        facts: list[dict] = json.load(f)

    trials = build_trial_matrix(CONFIG, facts)
    if args.subset is not None:
        trials = trials[: args.subset]

    log.info("Trial matrix: %d total trials", len(trials))

    if args.dry_run:
        _print_dry_run(trials, CONFIG)
        return

    if args.resume:
        before = len(trials)
        trials = [t for t in trials if not _result_exists(t, CONFIG["results_dir"])]
        log.info(
            "Resume: skipping %d completed trials, %d remaining.",
            before - len(trials), len(trials),
        )

    client = anthropic.Anthropic(api_key=api_key)
    _min_interval = 60.0 / CONFIG["requests_per_minute"]

    correct_count = 0
    scored_count = 0

    for i, trial in enumerate(trials, start=1):
        start = time.monotonic()
        result = run_trial(trial, CONFIG, client)

        if result["correct"] is True:
            correct_count += 1
        if result["correct"] is not None:
            scored_count += 1

        # Log running accuracy every 10 trials.
        if i % 10 == 0 or i == len(trials):
            accuracy = correct_count / scored_count if scored_count else float("nan")
            log.info(
                "Progress %d/%d — running accuracy %.1f%% (%d/%d scored)",
                i, len(trials), accuracy * 100, correct_count, scored_count,
            )

        # Rate limiting: sleep to maintain requests_per_minute.
        elapsed = time.monotonic() - start
        if elapsed < _min_interval and i < len(trials):
            time.sleep(_min_interval - elapsed)

    log.info("Experiment complete. Results written to %s", CONFIG["results_dir"])


def _result_exists(trial: dict, results_dir: str) -> bool:
    path = os.path.join(results_dir, f"{trial['trial_id']}.json")
    return os.path.isfile(path)


def _print_dry_run(trials: list[dict], config: dict) -> None:
    """Prints the trial matrix in a readable table and exits."""
    total = len(trials)
    log.info("DRY RUN — %d trials planned, no API calls will be made.", total)
    print(f"\n{'TRIAL ID':<60} {'CTX':>8} {'POS':>6}")
    print("-" * 76)
    for t in trials[:20]:
        print(f"{t['trial_id']:<60} {t['context_length']:>8} {t['position']:>6.2f}")
    if total > 20:
        print(f"  ... and {total - 20} more trials")
    print(f"\nTotal trials: {total}")
    expected_minutes = total / config["requests_per_minute"]
    rpm = config["requests_per_minute"]
    print(f"Estimated runtime at {rpm} req/min: ~{expected_minutes:.0f} min")


if __name__ == "__main__":
    main()
