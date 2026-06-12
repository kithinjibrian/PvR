"""
src/experiment/injector.py

Inserts a target fact sentence at a fractional position within filler text,
then measures the actual position of the injected fact in the resulting document.

Depends on: src/corpus/tokenizer
Used by: src/experiment/runner.py
"""

from typing import Any

from src.corpus.tokenizer import count_tokens

# Maximum allowed drift between requested and actual fractional position.
_MAX_DRIFT = 0.02


def inject(
    filler: str,
    fact_sentence: str,
    position: float,
    target_tokens: int,
    model: str = "claude-sonnet-4-6",
) -> dict[str, Any]:
    """Inserts fact_sentence into filler at the given fractional position.

    Splits the filler text at the token index closest to `position * target_tokens`,
    ensuring the split happens at a sentence boundary. Raises ValueError if the
    actual position drifts more than 2% from the requested position.

    Args:
        filler: The background text to inject into.
        fact_sentence: The single sentence containing the target fact.
        position: Fractional position in [0.0, 1.0]. 0.0 = fact first, 1.0 = fact last.
        target_tokens: Expected total token count of the final document.
        model: Model identifier passed through to the tokenizer.

    Returns:
        A dict with keys:
            document (str): Full text with fact_sentence injected.
            position_requested (float): The position argument passed in.
            position_actual (float): Actual fractional token position of the fact.
            total_tokens (int): Token count of the full document.
            fact_start_token (int): Token index where fact_sentence begins.
            fact_end_token (int): Token index where fact_sentence ends.

    Raises:
        ValueError: If position_actual drifts more than 0.02 from position_requested.

    Example:
        result = inject("Long filler text.", "The vessel ID is FV-001.", 0.5, 500)
        assert abs(result["position_actual"] - 0.5) <= 0.02
    """
    if position == 0.0:
        document = fact_sentence.rstrip() + " " + filler.lstrip()
    elif position == 1.0:
        document = filler.rstrip() + " " + fact_sentence.lstrip()
    else:
        # Split proportionally within the filler so the fact lands at `position`.
        filler_tokens = count_tokens(filler, model)
        desired_token = int(position * filler_tokens)
        # Split filler at a word/sentence boundary near the desired token index.
        split_char = _find_split_char(filler, desired_token, model)
        before = filler[:split_char].rstrip()
        after = filler[split_char:].lstrip()
        document = before + " " + fact_sentence.rstrip() + " " + after

    total_tokens = count_tokens(document, model)

    # Locate the fact_sentence within the document to compute actual position.
    fact_start_char = document.find(fact_sentence.strip())
    if fact_start_char == -1:
        # The fact sentence may have been merged with surrounding whitespace; search loosely.
        fact_start_char = document.find(fact_sentence.strip()[:20])

    prefix = document[:fact_start_char]
    fact_start_token = count_tokens(prefix, model)
    fact_end_token = fact_start_token + count_tokens(fact_sentence, model)

    # Guard against division by zero for very short documents.
    position_actual = fact_start_token / total_tokens if total_tokens > 0 else 0.0

    drift = abs(position_actual - position)
    if drift > _MAX_DRIFT:
        raise ValueError(
            f"Position drift {drift:.4f} exceeds maximum {_MAX_DRIFT}. "
            f"Requested {position}, got {position_actual:.4f}"
        )

    return {
        "document": document,
        "position_requested": position,
        "position_actual": position_actual,
        "total_tokens": total_tokens,
        "fact_start_token": fact_start_token,
        "fact_end_token": fact_end_token,
    }


def _find_split_char(text: str, desired_token: int, model: str) -> int:
    """Returns the character index of the sentence boundary nearest to desired_token.

    Scans forward through sentence-ending punctuation to find the split
    point whose token count is closest to desired_token.

    Args:
        text: The filler text to split.
        desired_token: Target token index for the split point.
        model: Model identifier for the tokenizer.

    Returns:
        Character index at which to split text.
    """
    import re

    sentence_ends = [m.end() for m in re.finditer(r"[.?!]\s", text)]
    if not sentence_ends:
        # No sentence boundaries found; fall back to a space split.
        spaces = [m.end() for m in re.finditer(r"\s+", text)]
        sentence_ends = spaces if spaces else [len(text) // 2]

    best_idx = sentence_ends[0]
    best_diff = abs(count_tokens(text[:sentence_ends[0]], model) - desired_token)

    for char_idx in sentence_ends[1:]:
        diff = abs(count_tokens(text[:char_idx], model) - desired_token)
        if diff < best_diff:
            best_diff = diff
            best_idx = char_idx

    return best_idx
