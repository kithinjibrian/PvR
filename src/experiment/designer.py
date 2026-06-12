"""
src/experiment/designer.py

Builds the trial matrix by crossing positions, context lengths, and facts.

Depends on: nothing (pure data transformation)
Used by: scripts/03_run_experiment.py
"""

from typing import Any


def build_trial_matrix(config: dict[str, Any], facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Returns a flat list of trial descriptors, one entry per API call.

    Matrix size = len(positions) × len(context_lengths) × facts_per_cell × trials_per_fact.
    Facts are selected by cycling through the facts list; if fewer than facts_per_cell
    facts are available the list is reused from the beginning.

    Args:
        config: The experiment CONFIG dict from scripts/03_run_experiment.py.
        facts: Parsed contents of data/facts/facts.json.

    Returns:
        List of trial dicts, each with keys:
            trial_id (str): Unique identifier for this trial.
            fact (dict): The full fact object from facts.json.
            position (float): Fractional injection position.
            context_length (int): Target context length in tokens.
            run_index (int): Trial repetition index (0-based).

    Example:
        matrix = build_trial_matrix(CONFIG, facts)
        assert len(matrix) == len(CONFIG["positions"]) * len(CONFIG["context_lengths"]) \
            * CONFIG["facts_per_cell"] * CONFIG["trials_per_fact"]
    """
    positions: list[float] = config["positions"]
    context_lengths: list[int] = config["context_lengths"]
    facts_per_cell: int = config["facts_per_cell"]
    trials_per_fact: int = config["trials_per_fact"]

    trials: list[dict[str, Any]] = []
    for ctx_len in context_lengths:
        for pos in positions:
            for cell_idx in range(facts_per_cell):
                fact = facts[cell_idx % len(facts)]
                for run in range(trials_per_fact):
                    trial_id = (
                        f"{fact['id']}__pos_{pos:.2f}__ctx_{ctx_len}__run_{run}"
                    )
                    trials.append(
                        {
                            "trial_id": trial_id,
                            "fact": fact,
                            "position": pos,
                            "context_length": ctx_len,
                            "run_index": run,
                        }
                    )
    return trials
