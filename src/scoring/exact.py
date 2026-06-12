"""
src/scoring/exact.py

Exact-match scorer for retrieval experiment trials.

Scoring logic (applied in order):
  1. Empty response    → (False, "empty")
  2. Variant match     → (True, None)
  3. Substring match   → (True, None)
  4. NOT FOUND variant → (False, "refusal")
  5. Anything else     → (False, "confabulation")

Depends on: nothing
Used by: src/experiment/runner.py
"""

from typing import Any

# Canonical refusal strings produced by the prompt template.
_REFUSAL_VARIANTS = {"not found", "not_found", "notfound"}


def score(predicted: str, fact: dict[str, Any]) -> tuple[bool, str | None]:
    """Scores a model response against the gold answer using exact and variant matching.

    Args:
        predicted: The raw string returned by the model.
        fact: The full fact dict from facts.json, which must contain
              "answer" (str) and "answer_variants" (list[str]).

    Returns:
        A 2-tuple (correct, error_type):
            (True, None)                 — answer found via variant or substring match
            (False, "empty")             — predicted is blank
            (False, "refusal")           — model said NOT FOUND
            (False, "confabulation")     — model produced a wrong answer

    Example:
        ok, err = score("FV-48291", {"answer": "FV-48291", "answer_variants": ["fv-48291"]})
        assert ok is True and err is None
    """
    stripped = predicted.strip()

    if not stripped:
        return (False, "empty")

    gold_variants: list[str] = fact.get("answer_variants", [fact["answer"]])

    # Normalise to lowercase for case-insensitive comparison.
    stripped_lower = stripped.lower()
    for variant in gold_variants:
        if stripped_lower == variant.lower():
            return (True, None)

    # Substring match — the model sometimes adds punctuation or extra context.
    for variant in gold_variants:
        if variant.lower() in stripped_lower:
            return (True, None)

    if stripped_lower.replace(" ", "").replace("_", "") in _REFUSAL_VARIANTS:
        return (False, "refusal")

    return (False, "confabulation")
