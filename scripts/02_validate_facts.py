"""
scripts/02_validate_facts.py

Validates data/facts/facts.json against the seven rules from the spec before
any experiment run. Exits with code 1 and a clear error message on failure.

Rules validated:
  1. File parses as a JSON array.
  2. At least 10 facts present.
  3. Each fact has all required fields: id, category, question, answer,
     answer_variants, fact_sentence, verified.
  4. Each id is unique.
  5. category is one of: identifier, measurement, named_entity, causal.
  6. answer_variants is a non-empty list containing the answer string.
  7. verified is true for every fact.

Usage:
  uv run python scripts/02_validate_facts.py
  uv run python scripts/02_validate_facts.py --facts-path path/to/facts.json

Depends on: json, argparse
Used by: CI gate before scripts/03_run_experiment.py
"""

import argparse
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

REQUIRED_FIELDS = {
    "id", "category", "question", "answer", "answer_variants", "fact_sentence", "verified"
}
VALID_CATEGORIES = {"identifier", "measurement", "named_entity", "causal"}


def validate(facts_path: str) -> list[str]:
    """Validates a facts.json file and returns a list of error messages.

    Returns an empty list if all seven validation rules pass.

    Args:
        facts_path: Path to the facts.json file.

    Returns:
        List of human-readable error strings; empty on success.

    Example:
        errors = validate("data/facts/facts.json")
        if errors:
            for e in errors:
                print(e)
    """
    errors: list[str] = []

    # Rule 1 — parses as JSON array
    try:
        with open(facts_path, encoding="utf-8") as f:
            facts = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return [f"Rule 1 failed: Cannot parse {facts_path!r}: {exc}"]

    if not isinstance(facts, list):
        return [f"Rule 1 failed: {facts_path!r} must be a JSON array, got {type(facts).__name__}"]

    # Rule 2 — at least 10 facts
    if len(facts) < 10:
        errors.append(f"Rule 2 failed: Expected >= 10 facts, got {len(facts)}")

    seen_ids: set[str] = set()

    for i, fact in enumerate(facts):
        label = f"facts[{i}]"

        # Rule 3 — required fields
        missing = REQUIRED_FIELDS - set(fact.keys())
        if missing:
            errors.append(f"Rule 3 failed: {label} missing fields: {sorted(missing)}")
            continue  # skip further checks on this fact since fields are absent

        fact_id: str = fact["id"]

        # Rule 4 — unique ids
        if fact_id in seen_ids:
            errors.append(f"Rule 4 failed: Duplicate id {fact_id!r} at {label}")
        seen_ids.add(fact_id)

        # Rule 5 — valid category
        if fact["category"] not in VALID_CATEGORIES:
            errors.append(
                f"Rule 5 failed: {label} ({fact_id}) category {fact['category']!r} "
                f"not in {sorted(VALID_CATEGORIES)}"
            )

        # Rule 6 — answer_variants is non-empty list containing the answer
        variants = fact["answer_variants"]
        if not isinstance(variants, list) or len(variants) == 0:
            errors.append(
                f"Rule 6 failed: {label} ({fact_id}) answer_variants must be a non-empty list"
            )
        elif fact["answer"] not in variants:
            errors.append(
                f"Rule 6 failed: {label} ({fact_id}) answer {fact['answer']!r} "
                f"not in answer_variants {variants}"
            )

        # Rule 7 — verified is true
        if fact["verified"] is not True:
            errors.append(f"Rule 7 failed: {label} ({fact_id}) verified must be true")

    return errors


def main() -> None:
    """Entry point for the validation script."""
    parser = argparse.ArgumentParser(
        description="Validate facts.json before running the experiment."
    )
    parser.add_argument(
        "--facts-path",
        default="data/facts/facts.json",
        help="Path to facts.json (default: data/facts/facts.json)",
    )
    args = parser.parse_args()

    log.info("Validating %s …", args.facts_path)
    errors = validate(args.facts_path)

    if errors:
        for error in errors:
            log.error("%s", error)
        log.error("Validation FAILED with %d error(s).", len(errors))
        sys.exit(1)

    with open(args.facts_path, encoding="utf-8") as f:
        facts = json.load(f)

    log.info("Validation PASSED — %d facts, all rules satisfied.", len(facts))


if __name__ == "__main__":
    main()
