## FEATURE/EXPERIMENT: Implement the full Lost-in-the-Middle positional retrieval experiment

## OBJECTIVE

Build a reproducible pipeline that inserts a target fact at five fractional positions (0%, 25%, 50%, 75%, 100%) within filler documents of two lengths (16k and 64k tokens), sends each to Claude claude-sonnet-4-6, and records whether the model retrieves the correct answer. The output is three publication-ready figures showing how accuracy varies with position and context length.

Full design is in `docs/specs/lost-in-the-middle.md`. This PRP is the implementation checklist — the spec is the authority on all interface contracts and data schemas.

## CONTEXT

- Starting state: pyproject.toml, src/ scaffold, and context engineering files exist; no experiment code written yet
- Ending state: all modules under src/, scripts 01–04, tests/, and data/facts/facts.json implemented and passing
- Related existing code: read `docs/specs/lost-in-the-middle.md` in full before writing any module
- Open decisions: none — all resolved; see DECISIONS.md RESOLVED section

## IMPLEMENTATION REQUIREMENTS

### Must Do

- Follow the exact module interface signatures in the spec (tokenizer, builder, injector, designer, runner, scorer, aggregate, plot)
- Use `cl100k_base` tiktoken encoding as proxy for Claude token counts; log both target and actual token counts in every trial result
- Write one JSON result file per trial immediately after the API call returns (before processing the next trial)
- Support `--dry-run`, `--resume`, `--subset N` flags in `scripts/03_run_experiment.py`
- Use exponential backoff `2^attempt × retry_delay_seconds` on 429 errors; write `error_type="api_error"` result and continue on all other API errors
- Implement `scripts/02_validate_facts.py` with all seven validation rules from the spec before running any experiment

### Must NOT Do

- Do not add multi-model support — CONFIG["model"] is a single string in v1
- Do not call `llm_judge.py` — scaffold it but leave it uncalled; exact match only in v1
- Do not add distractor facts, multi-hop retrieval, or confidence elicitation
- Do not randomize corpus reading start position — always read from the beginning for reproducibility
- Do not modify the canonical prompt template in runner.py without updating the spec first
- Do not use `print()` for experiment output — use `logging`

## ERROR HANDLING REQUIREMENTS

- API RateLimitError (429): exponential backoff, up to `retry_attempts` retries; raise after last retry so the run stops rather than silently skipping
- Any other `anthropic.APIError`: log at WARNING, write result file with `correct=None, error_type="api_error"`, continue to next trial
- `ValueError` from injector (position drift > 2%): propagate up and abort the affected trial; write result with `error_type="injector_error"`
- Missing or malformed fact fields: caught by `02_validate_facts.py` before any API calls

## SECURITY CONSIDERATIONS

- `ANTHROPIC_API_KEY` loaded from environment via `python-dotenv`; crash at startup with a clear error message if missing
- Never log the API key or any fragment of it
- `corpus.txt` and `facts.json` are the only external inputs; validate facts schema in `02_validate_facts.py` before processing

## TESTS TO WRITE

Write these before implementing each module (TDD):

**tests/test_injector.py**
- [ ] Happy path: injecting at 0.5 produces `position_actual` within 0.02 of 0.5
- [ ] Edge: position=0.0 → fact sentence is the first content in the document
- [ ] Edge: position=1.0 → fact sentence is the last content in the document
- [ ] Correctness: returned document contains exactly one copy of `fact_sentence`
- [ ] Token budget: `total_tokens` is within 2% of `target_tokens`
- [ ] Error: raises ValueError when position drift exceeds 0.02

**tests/test_builder.py**
- [ ] Happy path: `build_filler` returns text within 2% of `target_tokens`
- [ ] Boundary: output ends at a sentence boundary (last char is `.`, `?`, or `!`)
- [ ] Determinism: two calls with same args return identical strings

**tests/test_scorer.py**
- [ ] Exact match: correct answer → `(True, None)`
- [ ] Variant match: lowercase variant → `(True, None)`
- [ ] Substring match: answer embedded in longer response → `(True, None)`
- [ ] Refusal: "NOT FOUND" response → `(False, "refusal")`
- [ ] Empty: empty string → `(False, "empty")`
- [ ] Confabulation: wrong answer → `(False, "confabulation")`

## ROLLBACK PLAN

If this experiment needs to be abandoned mid-implementation:
- Branch to return to: `main`
- All data files are gitignored (`data/results/`) — nothing destructive to undo
- Source files can be deleted; no migrations or schema changes

## ACCEPTANCE CRITERIA

- [ ] `uv run python scripts/02_validate_facts.py` passes with 10+ verified facts
- [ ] `uv run pytest` passes (all unit tests green, no API calls made)
- [ ] `uv run mypy src/` passes with no errors
- [ ] `uv run ruff check src/ tests/` passes
- [ ] `uv run python scripts/03_run_experiment.py --dry-run` prints trial matrix and exits without API calls
- [ ] `uv run python scripts/03_run_experiment.py --subset 5` completes 5 trials and writes 5 result JSON files
- [ ] Mid-run interrupt (`Ctrl+C`) followed by `--resume` skips completed trials and finishes the rest
- [ ] `uv run python scripts/04_analyze.py` generates three figures in `data/results/figures/`
- [ ] CHANGELOG.md updated

## VALIDATION

```bash
uv run pytest
uv run mypy src/
uv run ruff check src/ tests/
uv run python scripts/02_validate_facts.py
uv run python scripts/03_run_experiment.py --dry-run
uv run python scripts/03_run_experiment.py --subset 5
uv run python scripts/04_analyze.py
```
