"""
src/corpus/builder.py

Builds filler text by reading from a corpus file up to a target token count,
ending at a sentence boundary.

Depends on: src/corpus/tokenizer
Used by: src/experiment/injector.py, scripts/03_run_experiment.py
"""

import re

from src.corpus.tokenizer import count_tokens, truncate_to_tokens

# Sentence-ending characters used to find the last clean boundary.
_SENTENCE_END = re.compile(r"[.?!]")


def build_filler(corpus_path: str, target_tokens: int, model: str = "claude-sonnet-4-6") -> str:
    """Reads corpus from start, returning text within 2% of target_tokens at a sentence boundary.

    Reads from the beginning of the corpus file each time for reproducibility.
    The returned text is guaranteed to end with '.', '?', or '!'.

    Args:
        corpus_path: Path to the plain-text corpus file.
        target_tokens: Desired token count for the returned filler text.
        model: Model identifier passed through to the tokenizer.

    Returns:
        A string within 2% of target_tokens that ends at a sentence boundary.

    Raises:
        FileNotFoundError: If corpus_path does not exist.
        ValueError: If the corpus is too short to reach target_tokens.

    Example:
        filler = build_filler("data/filler/corpus.txt", 1000)
        assert filler[-1] in ".?!"
    """
    with open(corpus_path, encoding="utf-8") as f:
        raw = f.read()

    # Allow a 5% overshoot when truncating so we have room to back up to a sentence boundary.
    budget = int(target_tokens * 1.05)
    candidate = truncate_to_tokens(raw, budget, model)

    if count_tokens(candidate, model) < int(target_tokens * 0.98):
        raise ValueError(
            f"Corpus too short: needed {target_tokens} tokens, "
            f"got {count_tokens(candidate, model)} from {corpus_path!r}"
        )

    # Walk backward from the end to find the last sentence boundary.
    for match in reversed(list(_SENTENCE_END.finditer(candidate))):
        trimmed = candidate[: match.end()]
        actual = count_tokens(trimmed, model)
        if actual <= target_tokens:
            # Accept if within 2% below target.
            if actual >= int(target_tokens * 0.98):
                return trimmed

    raise ValueError(
        f"Could not find a sentence boundary within 2% of {target_tokens} tokens in {corpus_path!r}"
    )
