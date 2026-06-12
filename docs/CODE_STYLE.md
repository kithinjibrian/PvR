# Code Style — PvR (Primacy vs. Recency)

Documentation rules for all code in this project.
Read this before writing any function, class, or module.

---

## The Two Layers of Documentation

### Layer 1 — Docstrings (what this is)

Every exported function, class, and module gets a docstring.
Internal helper functions get a docstring only if their purpose is not immediately obvious.

**Format (Python / Google style):**

```python
def call_model(prompt: str, model: str) -> Success[str] | Failure[str]:
    """Sends a single prompt to the specified model and returns the response text.

    Wraps API errors as typed Failure values rather than raising. Callers
    must check result["ok"] before accessing result["data"].

    Args:
        prompt: The full prompt string to send.
        model: Model identifier string, e.g. "claude-opus-4-8".

    Returns:
        Success with the response text, or Failure with one of:
        "RATE_LIMITED", "CONTEXT_TOO_LONG", "API_ERROR:<message>".

    Example:
        result = call_model("What is 2+2?", "claude-haiku-4-5-20251001")
        if not result["ok"]:
            logger.warning("API call failed: %s", result["error"])
            return result
        print(result["data"])
    """
```

Rules:
- First line is always a single sentence. Start with a verb: "Sends", "Loads", "Computes", "Returns".
- `Args:` and `Returns:` are required on every exported function.
- `Returns:` must describe both success and failure paths for functions that return Success | Failure.
- One `Example:` block required on every public API function.

### Layer 2 — Inline comments (why this decision was made)

Inline comments explain decisions, not code.

**Good:** `# Retry once — the Anthropic API returns 529 on cold start in some regions`
**Bad:** `# Loop through results`

Rules:
- Comment above the line it explains, not at the end.
- Use inline comments for: magic numbers, non-obvious library usage, performance trade-offs, workarounds for known upstream bugs.
- Never comment what the code does. If the code needs a comment to explain what it does, rewrite it.
- Known issues: `# TODO(#123): Remove after upstream fixes their token counting`

---

## Module-Level Documentation

Every file gets a top-of-file module docstring:

```python
"""
utils/api.py

Thin wrapper around LLM provider SDKs. Converts SDK exceptions to typed
Failure values. Does NOT handle retry logic — that belongs in the caller.

Depends on: config, anthropic SDK
Used by: experiments/
"""
```

---

## What Good Documentation Looks Like

```python
"""
experiments/needle_in_haystack.py

Runs the needle-in-a-haystack retrieval experiment. Inserts a target fact
at a configurable position within a filler context, then measures whether
the model retrieves it correctly.

Depends on: utils/api, utils/data, config
Used by: top-level experiment runner scripts
"""

from pvr.utils.api import call_model
from pvr.config import ModelConfig


def run_trial(
    needle: str,
    haystack: list[str],
    position: float,
    model: str,
) -> Success[TrialResult] | Failure[str]:
    """Runs a single retrieval trial with the needle at the given position.

    Inserts `needle` into `haystack` at the fractional position specified
    by `position` (0.0 = beginning, 1.0 = end), then prompts the model
    to retrieve it.

    Args:
        needle: The fact string the model must retrieve.
        haystack: List of distractor sentences forming the context.
        position: Float in [0.0, 1.0] indicating insertion point.
        model: Model identifier string.

    Returns:
        Success with a TrialResult containing the model response and
        correctness score, or Failure with "API_ERROR:<message>".

    Example:
        result = run_trial("The capital of France is Paris.", distractors, 0.5, "claude-haiku-4-5-20251001")
        if result["ok"]:
            print(result["data"]["correct"])
    """
    insert_idx = int(position * len(haystack))
    context_parts = haystack[:insert_idx] + [needle] + haystack[insert_idx:]
    prompt = _build_prompt(context_parts, needle)

    response = call_model(prompt, model)
    if not response["ok"]:
        return response  # propagate typed failure

    # Score with exact-match — fuzzy matching considered but ruled out
    # because it introduces ambiguity in position-accuracy plots
    correct = needle.lower() in response["data"].lower()
    return {"ok": True, "data": TrialResult(response=response["data"], correct=correct), "error": None}
```

---

## Documentation Anti-Patterns

1. **Describing the code.** `# Loop over sentences` — the code already says that.
2. **Stale docstrings.** A docstring that contradicts the signature is worse than none. Update both in the same edit.
3. **`TODO` without a ticket.** Every TODO gets a ticket reference or a date: `# TODO(2026-07-01): revisit`.
4. **Over-documenting tiny helpers.** A three-line private helper with an obvious name does not need a docstring.
5. **Under-documenting the failure contract.** The `Returns:` section must name every Failure variant. That is the most important part of the docstring for callers.
