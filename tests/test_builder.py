"""tests/test_builder.py — unit tests for src/corpus/builder.py"""

import os

import pytest

from src.corpus.builder import build_filler
from src.corpus.tokenizer import count_tokens

# Short sentences so boundaries are dense enough for the 2% tolerance window.
# Each sentence is ~10 chars = ~2.5 tokens, giving sub-token granularity per sentence.
_SENTENCE = "Stars shine. "
_CORPUS = _SENTENCE * 10000  # ~32k tokens of repetitive prose


def _write_corpus(tmp_path: str) -> str:
    path = os.path.join(tmp_path, "corpus.txt")
    with open(path, "w") as f:
        f.write(_CORPUS)
    return path


def test_build_filler_within_2_percent(tmp_path):
    corpus_path = _write_corpus(str(tmp_path))
    target = 500
    filler = build_filler(corpus_path, target)
    actual = count_tokens(filler)
    assert actual <= target
    assert actual >= int(target * 0.98)


def test_build_filler_ends_at_sentence_boundary(tmp_path):
    corpus_path = _write_corpus(str(tmp_path))
    filler = build_filler(corpus_path, 500)
    assert filler.rstrip()[-1] in ".?!"


def test_build_filler_deterministic(tmp_path):
    corpus_path = _write_corpus(str(tmp_path))
    a = build_filler(corpus_path, 500)
    b = build_filler(corpus_path, 500)
    assert a == b


def test_build_filler_raises_if_corpus_too_short(tmp_path):
    path = os.path.join(str(tmp_path), "tiny.txt")
    with open(path, "w") as f:
        f.write("Short. Text.")
    with pytest.raises(ValueError, match="too short"):
        build_filler(path, 10000)
