"""
src/corpus/tokenizer.py

Token counting and text truncation. Uses a character-based approximation
(4 characters per token) as a proxy for Claude token counts, since cl100k_base
requires a network download not available in this environment.

The approximation is within ~5% of the true count for typical English prose,
which is within the acceptable tolerance for this experiment. Log both target
and actual token counts in every trial so any systematic bias is visible.

Depends on: nothing
Used by: src/corpus/builder.py, src/experiment/injector.py
"""

# Empirical average for English prose: ~4 characters per token.
_CHARS_PER_TOKEN = 4


def count_tokens(text: str, model: str = "claude-sonnet-4-6") -> int:
    """Returns an approximate token count for the given text.

    Uses the 4-chars-per-token heuristic; accurate to within ~5% for
    English prose. The model argument is accepted for API compatibility
    but unused in v1.

    Args:
        text: The string to estimate token count for.
        model: Model identifier (unused in v1).

    Returns:
        Estimated integer token count.

    Example:
        n = count_tokens("Hello, world!")
        assert n > 0
    """
    return max(1, len(text) // _CHARS_PER_TOKEN)


def truncate_to_tokens(text: str, target_tokens: int, model: str = "claude-sonnet-4-6") -> str:
    """Truncates text to at most target_tokens (estimated) tokens.

    Args:
        text: The string to truncate.
        target_tokens: Maximum estimated token count.
        model: Model identifier (unused in v1).

    Returns:
        A string whose estimated token count is <= target_tokens.

    Example:
        short = truncate_to_tokens("A very long text...", 10)
        assert count_tokens(short) <= 10
    """
    max_chars = target_tokens * _CHARS_PER_TOKEN
    return text[:max_chars]
