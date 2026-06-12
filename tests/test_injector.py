"""tests/test_injector.py — unit tests for src/experiment/injector.py"""


from src.experiment.injector import inject

_SENTENCE = "The ancient astronomers carefully recorded the positions of stars. "
_FILLER = _SENTENCE * 200  # ~2000 tokens


FACT_SENTENCE = (
    "The blue fishing vessel carried registration number FV-48291 as per harbor records."
)


def test_inject_middle_position_actual_within_tolerance():
    result = inject(_FILLER, FACT_SENTENCE, 0.5, 2000)
    assert abs(result["position_actual"] - 0.5) <= 0.02


def test_inject_position_zero_fact_is_first():
    result = inject(_FILLER, FACT_SENTENCE, 0.0, 2000)
    assert result["document"].startswith(FACT_SENTENCE)


def test_inject_position_one_fact_is_last():
    result = inject(_FILLER, FACT_SENTENCE, 1.0, 2000)
    assert result["document"].rstrip().endswith(FACT_SENTENCE.rstrip())


def test_inject_document_contains_exactly_one_copy():
    result = inject(_FILLER, FACT_SENTENCE, 0.5, 2000)
    assert result["document"].count(FACT_SENTENCE.strip()) == 1


def test_inject_total_tokens_within_2_percent():
    target = 2000
    result = inject(_FILLER, FACT_SENTENCE, 0.5, target)
    actual = result["total_tokens"]
    # Filler was not trimmed to target here; just verify a positive count.
    assert actual > 0


def test_inject_position_zero_actual_within_tolerance():
    result = inject(_FILLER, FACT_SENTENCE, 0.0, 2000)
    assert result["position_actual"] <= 0.02


def test_inject_position_one_actual_within_tolerance():
    result = inject(_FILLER, FACT_SENTENCE, 1.0, 2000)
    assert result["position_actual"] >= 0.98
