# MEMORY.md — PvR (Primacy vs. Recency)

Records resolved architectural decisions and current project state.
Read this at the start of every session before writing any code.

---

## ARCHITECTURAL DECISIONS

### 1. Claude-only API for v1

**Decision:** v1 uses Anthropic's API only (model: `claude-sonnet-4-6`). No multi-model support.

**Why:** Establishes a clean baseline before introducing provider complexity. The spec explicitly scopes v1 to Claude.

**Rules out:** Importing or depending on OpenAI, Google, or any other provider SDK in v1 code. Adding a `provider` parameter to runner.py in v1.

---

### 2. Synthetic needle-in-a-haystack dataset

**Decision:** Target facts are a custom `data/facts/facts.json` of 10+ manually verified facts injected into Wikipedia prose filler. Each fact answer must be non-inferable without the injected sentence.

**Why:** Maximum positional control — the experimenter chooses exactly where each fact appears. Wikipedia filler (astronomy, mycology, medieval history, marine biology, classical music) chosen for zero semantic overlap with fact content.

**Rules out:** Using SCROLLS, NarrativeQA, or any pre-existing QA dataset where fact positions cannot be precisely controlled.

---

### 3. Synchronous single-threaded runner with per-trial JSON persistence

**Decision:** `runner.py` executes trials sequentially. One JSON file written per trial immediately after the API call returns, before processing the next trial. Rate limiting via `requests_per_minute` sleep between calls.

**Why:** Crash resilience (at most one trial lost), trivial `--resume` (check if output file exists), no async complexity. At 50 req/min the rate limit is the bottleneck — parallelism adds no throughput benefit.

**Rules out:** ThreadPoolExecutor, asyncio, and any approach that batches or pipelines API calls in v1.

---

### 4. Per-trial JSON results, aggregated to CSV at analysis time

**Decision:** Raw results stored as one JSON file per trial in `data/results/raw/`. Aggregation to CSV happens in `src/analysis/aggregate.py` when `scripts/04_analyze.py` is run.

**Why:** Per-file storage makes `--resume` a single `os.path.exists()` check. JSON schema is defined in the spec and must not change without updating the spec first.

**Rules out:** SQLite, Parquet, or any database for raw result storage in v1. Writing aggregate CSVs during the experiment run.

---

### 5. `cl100k_base` tiktoken encoding as Claude token-count proxy

**Decision:** `src/corpus/tokenizer.py` uses `tiktoken` with `cl100k_base` encoding to count and truncate tokens. Actual token count sent to Claude may differ by up to 3%.

**Why:** Anthropic does not publish Claude's tokenizer. `cl100k_base` (GPT-4 tokenizer) is the closest available proxy. Both target and actual token counts are logged in every trial result so discrepancy is visible.

**Rules out:** Using the Anthropic API's own token count endpoint for pre-run sizing (too slow and adds API calls before the experiment starts).

---

### 6. Five fractional positions, sentence-boundary-aware insertion

**Decision:** Positions tested: [0.0, 0.25, 0.5, 0.75, 1.0]. Injector walks forward from the target token index to the nearest sentence boundary before inserting. Raises `ValueError` if position drift exceeds 0.02.

**Why:** Sentence-boundary insertion prevents facts from appearing mid-sentence, which would confound retrieval with grammatical malformation. The 2% tolerance is tight enough to be meaningful but loose enough to accommodate sentence lengths.

**Rules out:** Arbitrary-character insertion, mid-word truncation, position drift greater than 2%.

---

### 7. Return-based error handling (no exceptions for predictable API failures)

**Decision:** All API calls return `{"ok": True/False, "data": ..., "error": ...}`. Exceptions are only for programmer errors and startup failures.

**Why:** Predictable API failures (rate limits, context too long, timeouts) must be distinguishable from bugs at the call site. None/null returns are ambiguous.

**Rules out:** Raising exceptions in runner.py for rate limits or API errors. Returning None to signal a failed API call.

---

## CURRENT PROJECT STATE

### Fully Working
- Context engineering system (CLAUDE.md, MEMORY.md, CONTEXT.md, DECISIONS.md, CHANGELOG.md, .llmignore, PRPs/, docs/)
- Spec: `docs/specs/lost-in-the-middle.md`
- PRP: `PRPs/lost-in-the-middle.md`

### In Progress
- Nothing yet — no source code written

### Not Started
- pyproject.toml and uv scaffold
- `data/facts/facts.json` (10+ verified facts)
- `src/corpus/tokenizer.py`
- `src/corpus/builder.py`
- `scripts/01_build_corpus.py`
- `src/experiment/injector.py`
- `src/experiment/designer.py`
- `src/experiment/runner.py`
- `src/scoring/exact.py`
- `src/scoring/llm_judge.py` (scaffold only)
- `src/analysis/aggregate.py`
- `src/analysis/plot.py`
- `scripts/02_validate_facts.py`
- `scripts/03_run_experiment.py`
- `scripts/04_analyze.py`
- All tests

---

## NEXT SESSION START POINT

All decisions resolved. PRP approved (`PRPs/lost-in-the-middle.md`). Spec is `docs/specs/lost-in-the-middle.md`.

Implementation order from the spec (§7):
1. `pyproject.toml` + `uv sync`
2. `data/facts/facts.json` + `scripts/02_validate_facts.py`
3. `src/corpus/tokenizer.py` + tests
4. `src/corpus/builder.py` + tests
5. `scripts/01_build_corpus.py`
6. `src/experiment/injector.py` + `tests/test_injector.py`
7. `src/experiment/designer.py`
8. `src/scoring/exact.py` + `tests/test_scorer.py`
9. `src/experiment/runner.py`
10. `src/analysis/aggregate.py` + `src/analysis/plot.py`
11. `scripts/03_run_experiment.py` + `scripts/04_analyze.py`

Read `docs/CODE_STYLE.md` before writing any function. Write failing tests before implementing.
