# Technical Specification — Lost in the Middle: LLM Long-Context Retrieval Experiment

**Status:** Active — source of truth for implementation
**Author:** Kithinji Brian
**Date:** 2026-06-12

---

## 1. Executive Summary

A reproducible research tool that measures how retrieval accuracy degrades as a function of position in long documents for large language models. Reproduces and extends Liu et al. (2023) *"Lost in the Middle"* using current frontier models via API. Primary output: position × accuracy curve across multiple context lengths, revealing whether modern long-context training has eliminated the U-shaped retrieval degradation documented in that paper.

---

## 2. Background

Liu et al. (2023) showed that LLMs exhibit non-uniform retrieval accuracy across document positions — higher accuracy at the beginning and end (primacy and recency effects) and degraded accuracy in the middle. This experiment tests whether that degradation persists in current frontier models at modern context lengths (16k–64k tokens).

---

## 3. Goals

1. Measure retrieval accuracy at five fractional positions (0%, 25%, 50%, 75%, 100%) across two context lengths (16k, 64k tokens) using Claude claude-sonnet-4-6.
2. Produce three publication-ready figures: position-accuracy curve, accuracy heatmap, error-type breakdown.
3. Support resumable runs — a mid-run crash loses at most one trial result.

---

## 4. Non-Goals (v1)

- Multi-model comparison (GPT-4o, Gemini) — documented extension
- Distractor conditions (competing facts)
- Multi-hop retrieval
- LLM-as-judge scoring (scaffolded but not called)
- Confidence elicitation
- Fine-grained position resolution beyond five points

---

## 5. Repository Structure

```
lost-in-the-middle/
├── SPEC.md                          ← Symlinked to docs/specs/lost-in-the-middle.md
├── data/
│   ├── filler/corpus.txt            ← ~150k tokens of Wikipedia prose, git-tracked
│   ├── facts/facts.json             ← Target facts dataset, git-tracked
│   └── results/                     ← Git-ignored
│       ├── raw/                     ← One JSON file per trial
│       ├── aggregated/              ← Rolled-up CSVs
│       └── figures/                 ← PNG/SVG outputs
├── src/
│   ├── corpus/
│   │   ├── builder.py
│   │   └── tokenizer.py
│   ├── experiment/
│   │   ├── designer.py
│   │   ├── injector.py
│   │   └── runner.py
│   ├── scoring/
│   │   ├── exact.py
│   │   └── llm_judge.py
│   └── analysis/
│       ├── aggregate.py
│       └── plot.py
├── scripts/
│   ├── 01_build_corpus.py
│   ├── 02_validate_facts.py
│   ├── 03_run_experiment.py
│   └── 04_analyze.py
├── notebooks/explore_results.ipynb
└── tests/
    ├── test_builder.py
    ├── test_injector.py
    └── test_scorer.py
```

---

## 6. Design / Architecture

### Configuration

All experiment parameters live in a single `CONFIG` dict at the top of `scripts/03_run_experiment.py`. No config files, no CLI flags for core parameters.

```python
CONFIG = {
    "positions": [0.0, 0.25, 0.5, 0.75, 1.0],
    "context_lengths": [16384, 65536],
    "facts_per_cell": 10,
    "trials_per_fact": 1,
    "model": "claude-sonnet-4-6",
    "max_tokens": 100,
    "temperature": 0,
    "filler_path": "data/filler/corpus.txt",
    "facts_path": "data/facts/facts.json",
    "results_dir": "data/results/raw",
    "scorer": "exact",
    "requests_per_minute": 50,
    "retry_attempts": 3,
    "retry_delay_seconds": 5,
}
```

CLI flags for workflow control only:
```bash
uv run python scripts/03_run_experiment.py --dry-run
uv run python scripts/03_run_experiment.py --resume
uv run python scripts/03_run_experiment.py --subset 5
```

### Data Contracts

**`data/facts/facts.json`** — array of fact objects:
```json
{
  "id": "fact_001",
  "category": "identifier",
  "question": "What is the registration number of the blue fishing vessel?",
  "answer": "FV-48291",
  "answer_variants": ["FV-48291", "fv-48291", "FV 48291"],
  "fact_sentence": "The blue fishing vessel carried registration number FV-48291 as per harbor records.",
  "verified": true,
  "notes": "Arbitrary alphanumeric — zero probability of appearing in training data"
}
```

Categories: `identifier`, `measurement`, `named_entity`, `causal`

**`data/results/raw/<trial_id>.json`** — one file per trial:
```json
{
  "trial_id": "fact_001__pos_0.50__ctx_16384__run_0",
  "fact_id": "fact_001",
  "category": "identifier",
  "position_requested": 0.50,
  "position_actual": 0.498,
  "context_length_target": 16384,
  "context_length_actual": 16401,
  "model": "claude-sonnet-4-6",
  "question": "...",
  "gold_answer": "FV-48291",
  "predicted": "FV-29104",
  "correct": false,
  "error_type": "confabulation",
  "scorer": "exact",
  "input_tokens": 16401,
  "output_tokens": 8,
  "latency_ms": 1823,
  "timestamp": "2026-06-12T10:23:01Z"
}
```

`error_type` values: `confabulation`, `wrong_retrieval`, `refusal`, `format_error`, `empty`, `api_error`

### Module Interfaces

#### `src/corpus/tokenizer.py`
```python
def count_tokens(text: str, model: str = "claude-sonnet-4-6") -> int: ...
def truncate_to_tokens(text: str, target_tokens: int, model: str = "claude-sonnet-4-6") -> str: ...
```
Uses `cl100k_base` (GPT-4 tokenizer) as proxy for Claude. Actual count may differ by up to 3% — log both target and actual in every trial.

#### `src/corpus/builder.py`
```python
def build_filler(corpus_path: str, target_tokens: int, model: str) -> str: ...
```
Returns text within 2% of `target_tokens`, ending at a sentence boundary. Reads from start of corpus each time (reproducibility).

#### `src/experiment/injector.py`
```python
def inject(filler: str, fact_sentence: str, position: float, target_tokens: int, model: str) -> dict: ...
```
Returns `{document, position_requested, position_actual, total_tokens, fact_start_token, fact_end_token}`.
Raises `ValueError` if `position_actual` drifts more than 0.02 from `position_requested`.

Position semantics: 0.0 = fact first, 1.0 = fact last, 0.5 = fact at token midpoint.

#### `src/experiment/designer.py`
```python
def build_trial_matrix(config: dict, facts: list[dict]) -> list[dict]: ...
```
Matrix size = `len(positions) × len(context_lengths) × facts_per_cell × trials_per_fact`.

#### `src/experiment/runner.py`
Prompt template (canonical — do not modify without updating this spec):
```
Read the following document carefully, then answer the question.
<document>
{document}
</document>
Question: {question}
Answer with only the specific value or identifier, nothing else. Do not explain. If you cannot find the answer in the document, respond with exactly: NOT FOUND
```
Reliability: exponential backoff on 429 (`2^attempt × retry_delay_seconds`), write result to disk before next trial, log running accuracy every 10 trials.

#### `src/scoring/exact.py`
```python
def score(predicted: str, fact: dict) -> tuple[bool, str]: ...
```
Logic (in order): empty → `(False, "empty")`, variant match → `(True, None)`, substring match → `(True, None)`, NOT FOUND variant → `(False, "refusal")`, else → `(False, "confabulation")`.

#### `src/scoring/llm_judge.py`
Scaffolded for v2. Uses a second API call with a YES/NO judge prompt. Not called in v1.

#### `src/analysis/aggregate.py`
```python
def aggregate(results_dir: str) -> pd.DataFrame: ...
def accuracy_by_cell(df: pd.DataFrame) -> pd.DataFrame: ...
```
Position buckets at 0.0, 0.25, 0.5, 0.75, 1.0. Context length buckets at configured values.

#### `src/analysis/plot.py`
Three figures:
1. `position_vs_accuracy.png` — line chart, one line per context length, error bars
2. `accuracy_heatmap.png` — rows=context length, cols=position, color=accuracy
3. `error_breakdown.png` — stacked bar chart, error types by position, one subplot per context length

All figures: matplotlib, colorblind-safe palette (tab10 or colorbrewer), publication-ready style.

---

## 7. Implementation Plan

| Step | Module | Done when |
|------|--------|-----------|
| 1 | `data/facts/facts.json` | 10+ facts pass `02_validate_facts.py` |
| 2 | `src/corpus/tokenizer.py` | `count_tokens` matches `len(encoding.encode(text))` |
| 3 | `src/corpus/builder.py` | Returns text within 2% of target token count |
| 4 | `scripts/01_build_corpus.py` | `corpus.txt` is ~150k tokens, no answer strings present |
| 5 | `src/experiment/injector.py` | All `test_injector.py` tests pass |
| 6 | `src/experiment/designer.py` | Matrix size equals `positions × lengths × facts × trials` |
| 7 | `src/scoring/exact.py` | All `test_scorer.py` tests pass |
| 8 | `src/experiment/runner.py` | Single trial runs end-to-end, result JSON written correctly |
| 9 | Full run | 100 trials complete with `--resume` surviving a mid-run interrupt |
| 10 | `src/analysis/` | Three figures generated from results |

---

## 8. Open Questions

None at time of writing. All decisions resolved — see `DECISIONS.md`.

---

## 9. References

Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2023). Lost in the Middle: How Language Models Use Long Contexts. *Transactions of the Association for Computational Linguistics*, 12, 157–173.
