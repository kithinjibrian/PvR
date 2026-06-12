"""
src/scoring/llm_judge.py

Scaffolded LLM-as-judge scorer for v2. Not called in v1.

In v2 this will use a second API call with a YES/NO judge prompt to handle
paraphrase matches and flexible answer formats that exact.py cannot score.

Depends on: anthropic SDK (not yet wired)
Used by: nothing in v1
"""

from typing import Any


def score(predicted: str, fact: dict[str, Any], model: str) -> tuple[bool, str | None]:  # noqa: ARG001
    """Placeholder LLM judge — raises NotImplementedError until v2.

    Args:
        predicted: The raw string returned by the primary model.
        fact: The full fact dict from facts.json.
        model: Model identifier to use for the judge call.

    Returns:
        Never returns in v1 — always raises.

    Raises:
        NotImplementedError: Always. Implement in v2.

    Example:
        # Do not call this in v1.
    """
    raise NotImplementedError("LLM judge is scaffolded for v2 and not called in v1.")
