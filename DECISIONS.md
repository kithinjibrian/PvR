# DECISIONS.md — PvR (Primacy vs. Recency)

Tracks architectural and design questions that are open, deferred, or resolved.

Rules:
- Every open decision blocks implementation of the code it affects.
- The AI must not implement anything that depends on an open decision.
- When a decision is resolved, move it to the RESOLVED section and record the outcome.
- Once resolved, copy the outcome to MEMORY.md as an architectural decision.

---

## OPEN — Requires human input before implementation

No open decisions.

---

## DEFERRED — Acknowledged, not yet needed

No deferred decisions.

---

## RESOLVED

### DECISION-001 — Which LLM providers to benchmark

**Status:** resolved
**Raised:** 2026-06-12 — Session 1
**Resolved:** 2026-06-12 — Session 2

**Question:** Which LLM providers should be included in the primacy vs. recency benchmarks?

**Outcome:** Anthropic only (Claude claude-sonnet-4-6) for v1. Multi-model support (GPT-4o, Gemini) is a documented v2 extension requiring abstraction of the API call in runner.py behind a `call_model(model, prompt)` interface.

**Rationale:** Spec explicitly scopes v1 to Claude only to establish a clean baseline. Multi-model is the first listed extension point.

**Copied to MEMORY.md:** yes

---

### DECISION-002 — Dataset / benchmark for retrieval tasks

**Status:** resolved
**Raised:** 2026-06-12 — Session 1
**Resolved:** 2026-06-12 — Session 2

**Question:** Which dataset or benchmark should be used to test primacy vs. recency retrieval?

**Outcome:** Synthetic "needle in a haystack" — custom `facts.json` of 10+ manually verified facts (categories: identifier, measurement, named_entity, causal) injected into Wikipedia filler prose. Each fact answer must be non-inferable without reading the injected sentence.

**Rationale:** Spec defines a bespoke facts.json format with strict non-inferability requirements. Wikipedia prose used for filler (astronomy, mycology, medieval history, marine biology, classical music — topics with zero overlap with fact specifics).

**Copied to MEMORY.md:** yes

---

### DECISION-003 — Async vs sync API calls in experiment runners

**Status:** resolved
**Raised:** 2026-06-12 — Session 1
**Resolved:** 2026-06-12 — Session 2

**Question:** Should the experiment runners use async API calls or synchronous calls?

**Outcome:** Synchronous, single-threaded with rate limiting. `CONFIG["requests_per_minute"]` controls throughput. Exponential backoff on 429 errors. Results written to disk after each trial before proceeding.

**Rationale:** Spec's runner.py design is synchronous and sequential. Parallelism is unnecessary given the rate limit constraint (50 req/min) and the priority of result durability over speed.

**Copied to MEMORY.md:** yes

---

### DECISION-004 — Results storage format

**Status:** resolved
**Raised:** 2026-06-12 — Session 1
**Resolved:** 2026-06-12 — Session 2

**Question:** Should experiment results be stored as JSON, CSV, Parquet, or SQLite?

**Outcome:** One JSON file per trial in `data/results/raw/<trial_id>.json`. Aggregated to CSV via `src/analysis/aggregate.py` when analysis is run. Schema is fixed in the spec.

**Rationale:** Per-trial JSON files maximize crash resilience (at most one trial lost per crash) and make `--resume` trivial to implement (check if file exists). Aggregation to CSV happens at analysis time, not during the run.

**Copied to MEMORY.md:** yes
