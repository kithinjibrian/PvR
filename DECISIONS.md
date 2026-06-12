# DECISIONS.md — PvR (Primacy vs. Recency)

Tracks architectural and design questions that are open, deferred, or resolved.

Rules:
- Every open decision blocks implementation of the code it affects.
- The AI must not implement anything that depends on an open decision.
- When a decision is resolved, move it to the RESOLVED section and record the outcome.
- Once resolved, copy the outcome to MEMORY.md as an architectural decision.

---

## OPEN — Requires human input before implementation

### DECISION-001 — Which LLM providers to benchmark

**Status:** open
**Raised:** 2026-06-12 — Session 1
**Resolved by:** human
**Blocks:** utils/api.py, any experiment that calls an LLM

**Question:** Which LLM providers should be included in the primacy vs. recency benchmarks?

**Options:**
- A) Anthropic only (Claude models) — simpler to start, single SDK
- B) Anthropic + OpenAI — broader comparison, two SDKs to maintain
- C) Anthropic + OpenAI + open-source (via Ollama or HuggingFace) — widest coverage, most complexity

**Notes:** The answer determines how the API wrapper in utils/api.py is designed. Starting with A and expanding later is safe because the abstraction can be added incrementally.

---

### DECISION-002 — Dataset / benchmark for retrieval tasks

**Status:** open
**Raised:** 2026-06-12 — Session 1
**Resolved by:** human
**Blocks:** src/utils/data.py, any retrieval experiment

**Question:** Which dataset or benchmark should be used to test primacy vs. recency retrieval?

**Options:**
- A) Synthetic "needle in a haystack" — simple to generate, fully controlled, widely used in LLM evals
- B) SCROLLS / NarrativeQA — real documents, more ecologically valid but harder to control position
- C) Custom dataset built from research papers or Wikipedia — full control over content and position

**Notes:** Option A is the standard approach for this type of experiment and easiest to implement. Options B/C are better for downstream publication claims.

---

### DECISION-003 — Async vs sync API calls in experiment runners

**Status:** open
**Raised:** 2026-06-12 — Session 1
**Resolved by:** human
**Blocks:** src/experiments/, src/utils/api.py

**Question:** Should the experiment runners use async API calls (asyncio + httpx) or synchronous calls with threading?

**Options:**
- A) Synchronous with threading (ThreadPoolExecutor) — simpler code, easier to debug, good for I/O-bound LLM calls
- B) Async (asyncio) — more idiomatic for I/O-bound work, but adds complexity to every caller
- C) Synchronous, single-threaded — simplest possible, acceptable for small experiments

**Notes:** For research experiments that may run hundreds of API calls, parallelism matters for wall-clock time. Option A is the pragmatic default unless the team has strong async experience.

---

## DEFERRED — Acknowledged, not yet needed

### DECISION-004 — Results storage format

**Status:** deferred
**Raised:** 2026-06-12 — Session 1
**Revisit when:** First experiment produces results that need to be stored and compared across runs

**Question:** Should experiment results be stored as JSON, CSV, Parquet, or in a lightweight database (SQLite)?

**Notes:** JSON is fine for initial work. Revisit when result sets are large enough that loading them into pandas becomes slow.

---

## RESOLVED

No resolved decisions yet.
