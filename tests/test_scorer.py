"""tests/test_scorer.py — unit tests for src/scoring/exact.py"""


from src.scoring.exact import score

FACT = {
    "id": "fact_001",
    "answer": "FV-48291",
    "answer_variants": ["FV-48291", "fv-48291", "FV 48291"],
}


def test_exact_match_correct():
    ok, err = score("FV-48291", FACT)
    assert ok is True
    assert err is None


def test_variant_match_lowercase():
    ok, err = score("fv-48291", FACT)
    assert ok is True
    assert err is None


def test_substring_match_embedded():
    ok, err = score("The answer is FV-48291 according to records.", FACT)
    assert ok is True
    assert err is None


def test_refusal_not_found():
    ok, err = score("NOT FOUND", FACT)
    assert ok is False
    assert err == "refusal"


def test_empty_response():
    ok, err = score("", FACT)
    assert ok is False
    assert err == "empty"


def test_whitespace_only_response():
    ok, err = score("   ", FACT)
    assert ok is False
    assert err == "empty"


def test_confabulation_wrong_answer():
    ok, err = score("FV-99999", FACT)
    assert ok is False
    assert err == "confabulation"
