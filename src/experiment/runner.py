"""
src/experiment/runner.py

Executes a single trial: builds the document, calls the Claude API, scores the
response, and writes the result to disk before returning.

Depends on: anthropic SDK, src/corpus/builder, src/experiment/injector,
            src/corpus/tokenizer, src/scoring/exact
Used by: scripts/03_run_experiment.py
"""

import json
import logging
import os
import time
from datetime import UTC, datetime
from typing import Any

import anthropic

from src.corpus.builder import build_filler
from src.experiment.injector import inject
from src.scoring.exact import score

log = logging.getLogger(__name__)

# Canonical prompt template — do not modify without updating docs/specs/lost-in-the-middle.md.
_PROMPT_TEMPLATE = """\
Read the following document carefully, then answer the question.
<document>
{document}
</document>
Question: {question}
Answer with only the specific value or identifier, nothing else. Do not explain. If you cannot find the answer in the document, respond with exactly: NOT FOUND"""  # noqa: E501


def run_trial(
    trial: dict[str, Any], config: dict[str, Any], client: anthropic.Anthropic
) -> dict[str, Any]:
    """Executes one retrieval trial and returns the full result dict.

    Builds filler text, injects the fact at the requested position, calls the
    Claude API, scores the response, and writes the result JSON to disk.
    Handles API errors according to PRP error-handling rules.

    Args:
        trial: Trial descriptor from designer.build_trial_matrix, containing
               trial_id, fact, position, context_length, run_index.
        config: The experiment CONFIG dict from scripts/03_run_experiment.py.
        client: An authenticated anthropic.Anthropic client.

    Returns:
        Result dict matching the data/results/raw/<trial_id>.json schema.

    Raises:
        anthropic.RateLimitError: After all retry attempts are exhausted on 429.

    Example:
        result = run_trial(trial, CONFIG, client)
        assert result["trial_id"] == trial["trial_id"]
    """
    fact = trial["fact"]
    position = trial["position"]
    ctx_len = trial["context_length"]
    trial_id = trial["trial_id"]

    # Build filler text for this context length.
    filler = build_filler(config["filler_path"], ctx_len, config["model"])

    # Inject the target fact at the requested position.
    try:
        injected = inject(filler, fact["fact_sentence"], position, ctx_len, config["model"])
    except ValueError as exc:
        log.warning("Injector error on %s: %s", trial_id, exc)
        result = _make_error_result(trial, config, "injector_error", str(exc))
        _write_result(result, config["results_dir"])
        return result

    document = injected["document"]
    prompt = _PROMPT_TEMPLATE.format(document=document, question=fact["question"])

    # Call the model with exponential backoff on rate limit errors.
    api_result = _call_with_retry(prompt, config, client)

    if api_result["ok"]:
        predicted = api_result["data"]["text"]
        output_tokens = api_result["data"]["output_tokens"]
        latency_ms = api_result["data"]["latency_ms"]
        correct, error_type = score(predicted, fact)
    else:
        predicted = ""
        output_tokens = 0
        latency_ms = 0
        correct = None
        error_type = "api_error"
        log.warning("API error on trial %s: %s", trial_id, api_result["error"])

    result = {
        "trial_id": trial_id,
        "fact_id": fact["id"],
        "category": fact["category"],
        "position_requested": position,
        "position_actual": injected["position_actual"],
        "context_length_target": ctx_len,
        "context_length_actual": injected["total_tokens"],
        "model": config["model"],
        "question": fact["question"],
        "gold_answer": fact["answer"],
        "predicted": predicted,
        "correct": correct,
        "error_type": error_type,
        "scorer": config["scorer"],
        "input_tokens": injected["total_tokens"],
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    _write_result(result, config["results_dir"])
    return result


def _call_with_retry(
    prompt: str,
    config: dict[str, Any],
    client: anthropic.Anthropic,
) -> dict[str, Any]:
    """Calls the Claude API with exponential backoff on 429 errors.

    Args:
        prompt: The full prompt string.
        config: Experiment config dict.
        client: Authenticated Anthropic client.

    Returns:
        dict with ok=True and data={text, output_tokens, latency_ms}, or
        ok=False and error=<message> for non-rate-limit API errors.

    Raises:
        anthropic.RateLimitError: After all retries exhausted.
    """
    retry_attempts: int = config["retry_attempts"]
    retry_delay: float = config["retry_delay_seconds"]

    for attempt in range(retry_attempts + 1):
        try:
            start = time.monotonic()
            response = client.messages.create(
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
                messages=[{"role": "user", "content": prompt}],
            )
            latency_ms = int((time.monotonic() - start) * 1000)
            first = response.content[0] if response.content else None
            text = first.text if isinstance(first, anthropic.types.TextBlock) else ""
            return {
                "ok": True,
                "data": {
                    "text": text,
                    "output_tokens": response.usage.output_tokens,
                    "latency_ms": latency_ms,
                },
                "error": None,
            }
        except anthropic.RateLimitError:
            if attempt >= retry_attempts:
                raise
            wait = (2**attempt) * retry_delay
            log.warning(
                "Rate limited (attempt %d/%d). Waiting %.1fs.",
                attempt + 1, retry_attempts, wait,
            )
            time.sleep(wait)
        except anthropic.APIError as exc:
            return {"ok": False, "data": None, "error": f"API_ERROR: {exc}"}

    # Should never reach here, but satisfies type checker.
    raise RuntimeError("Exhausted retries without raising RateLimitError")


def _make_error_result(
    trial: dict[str, Any], config: dict[str, Any], error_type: str, error_msg: str
) -> dict[str, Any]:
    """Constructs a minimal result dict for a failed trial.

    Args:
        trial: Trial descriptor dict.
        config: Experiment config dict.
        error_type: One of the defined error_type strings.
        error_msg: Human-readable error description (not stored, only logged).

    Returns:
        Result dict with correct=None and the given error_type.
    """
    return {
        "trial_id": trial["trial_id"],
        "fact_id": trial["fact"]["id"],
        "category": trial["fact"]["category"],
        "position_requested": trial["position"],
        "position_actual": None,
        "context_length_target": trial["context_length"],
        "context_length_actual": None,
        "model": config["model"],
        "question": trial["fact"]["question"],
        "gold_answer": trial["fact"]["answer"],
        "predicted": "",
        "correct": None,
        "error_type": error_type,
        "scorer": config["scorer"],
        "input_tokens": 0,
        "output_tokens": 0,
        "latency_ms": 0,
        "timestamp": datetime.now(UTC).isoformat(),
    }


def _write_result(result: dict[str, Any], results_dir: str) -> None:
    """Writes a single trial result to disk as a JSON file.

    Args:
        result: The result dict to serialize.
        results_dir: Directory path where result files are written.
    """
    os.makedirs(results_dir, exist_ok=True)
    path = os.path.join(results_dir, f"{result['trial_id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    log.debug("Wrote result to %s", path)
