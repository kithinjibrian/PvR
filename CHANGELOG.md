# CHANGELOG — PvR (Primacy vs. Recency)

Follows [Keep a Changelog](https://keepachangelog.com) format.
Updated at the end of every session when something is completed and merged.
Never deleted. Older entries are never modified.

---

## [Unreleased]

### Added
- Context engineering system: CLAUDE.md, MEMORY.md, CONTEXT.md, DECISIONS.md, .llmignore
- PRP templates: PRPs/TEMPLATE.md, PRPs/DISCOVERY.md
- Code style guide: docs/CODE_STYLE.md
- Technical spec: docs/specs/lost-in-the-middle.md — full design and data contracts for the positional retrieval experiment
- PRP: PRPs/lost-in-the-middle.md — implementation checklist and test requirements
- Resolved all four open architectural decisions (provider, dataset, concurrency model, results format)
- Full experiment implementation: pyproject.toml, src/ modules, scripts/01–04, tests/, data/facts/facts.json
  - src/corpus/tokenizer.py — 4-char/token approximation (tiktoken network-blocked in sandbox)
  - src/corpus/builder.py — builds filler text within 2% of target token count at sentence boundary
  - src/experiment/injector.py — injects fact at fractional position with <2% drift enforcement
  - src/experiment/designer.py — builds 100-trial matrix (5 positions × 2 ctx lengths × 10 facts)
  - src/experiment/runner.py — single-trial runner with exponential backoff and result-to-disk-first
  - src/scoring/exact.py — exact/variant/substring match scorer
  - src/scoring/llm_judge.py — scaffolded for v2, raises NotImplementedError
  - src/analysis/aggregate.py — loads raw JSON results into DataFrame
  - src/analysis/plot.py — three publication-ready figures (line, heatmap, stacked bar)
  - scripts/02_validate_facts.py — seven-rule validation gate
  - scripts/03_run_experiment.py — full runner with --dry-run, --resume, --subset
  - scripts/04_analyze.py — analysis + figure generation
  - data/facts/facts.json — 12 verified facts across 4 categories
  - 18 unit tests across test_builder.py, test_injector.py, test_scorer.py (all passing)

---

## [0.0.1] — 2026-06-12

### Added
- Initial repository: LICENSE (GPL-3), README.md, .gitignore
