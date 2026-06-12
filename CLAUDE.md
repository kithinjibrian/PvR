# CLAUDE.md — PvR (Primacy vs. Recency)

Behavioral instructions for AI coding assistants. Each rule exists to prevent a specific mistake.

---

## SESSION HANDOFF RULE — NON-NEGOTIABLE

Every session in `CONTEXT.md` must have:
- A **name** — short descriptive title of what the session accomplished
- A **state** — `open` while work is in progress, `closed` once handoff is done
- A **branch** — the git branch this session's work lives on

Format:
  ## SESSION {n} — {YYYY-MM-DD} — {Name} — {state}
  Branch: {branch-name}

Rules:
- **Step 1 of every session, no exceptions:** append a new session entry to `CONTEXT.md` with state `open` and the current branch name. Do this before reading any other file, before planning, before writing any code. The entry must exist and be committed before any other work begins.
- Mark it `closed` only after CONTEXT.md is updated and committed and pushed.
- Never leave a session `open` at the end of a turn.
- Never start a new session without closing the previous one first.
- The NEXT SESSION START POINT block is always rewritten at the end of every session.
- Sessions are never deleted — the full history stays in this file.

The open entry looks like this — write it immediately:

  ## SESSION {n} — {YYYY-MM-DD} — {Name} — open
  Branch: {branch-name}

Replace `{Name}` with a short title for what this session intends to do.
Commit this entry before proceeding.

---

## PRP RULE — NON-NEGOTIABLE

Never write code for a new feature or experiment without a PRP file in /PRPs.

If a feature/experiment request is given without a PRP:
1. Do not write any code.
2. Run a discovery interview — one question at a time.
3. Cover: what it does, which models/datasets are involved, edge cases, error states, what files it touches, what it must not touch.
4. Write the PRP to /PRPs/[feature-name].md.
5. Present it to the user for approval.
6. Only build after explicit approval.

A vague prompt is not a starting point. It is the beginning of a discovery.

---

## SCOPE RULE — NON-NEGOTIABLE

One PRP at a time. Never implement more than one experiment or feature's scope in a single session.

If mid-implementation you discover the scope is larger than the PRP described:
1. Stop immediately. Do not continue implementing.
2. Document what was discovered.
3. Update or create a new PRP for the expanded scope.
4. Get approval before continuing.

The model does not decide that something is "small enough to add." The human decides.

---

## TESTING RULE — NON-NEGOTIABLE

Write the test before writing the implementation. No exceptions.

Rules:
- For every new function, write a failing test first. Then write the minimum code to make it pass.
- Tests live in `tests/`. Mirror the source tree: `src/experiments/retrieval.py` → `tests/experiments/test_retrieval.py`.
- What to test: behavior visible to callers — inputs, outputs, and error paths.
- What NOT to test: implementation internals, third-party library behavior, LLM API response formats.
- Every new exported function must have at least one test covering its happy path and one covering each error path.
- After any non-trivial change, run the full test suite before considering the task done.

If the PRP does not describe what to test, add the test cases to the PRP before writing any code.

---

## SECURITY RULE — NON-NEGOTIABLE

Never hardcode API keys, tokens, or credentials. Not even in comments or example values.

- All API keys (Anthropic, OpenAI, etc.) must be loaded from environment variables or a `.env` file (never committed).
- Never log API keys, response metadata containing billing info, or user PII.
- Never construct shell commands by string concatenation — use `subprocess` with argument lists.
- Validate all external inputs (dataset files, config parameters) before processing.

If you are unsure whether something has a security implication, stop and ask before implementing.

---

## PENDING DECISIONS RULE — NON-NEGOTIABLE

Before writing any code that depends on an unresolved architectural question, check `DECISIONS.md`.

- If the decision is listed as `open`, stop. Do not implement. Ask the user to resolve it first.
- If the decision is listed as `resolved`, follow the outcome recorded there — do not re-litigate it.
- If you encounter a new unresolved question mid-implementation, add it to `DECISIONS.md` as `open` and stop. Do not guess.

Never make an architectural choice silently. If you are guessing, you are making a decision that belongs in DECISIONS.md.

---

## FILE SIZE RULE

No file exceeds 300 lines.

When a file reaches the limit:
1. Stop before adding more code.
2. Propose a split to the user — show the proposed new file names and what moves where.
3. Wait for approval.
4. Split, then continue.

Do not ask "should I split this?" — propose the specific split.

---

## PROTECTED FILES — NON-NEGOTIABLE

Never read, modify, or delete the following files or directories under any circumstances:

- `.env` and `.env.*` (environment files — contain API keys)
- `*.lock` files (uv.lock, poetry.lock, etc.)
- `LICENSE`

If a task seems to require touching a protected file, stop and ask the user how to proceed.

See also: `.llmignore` at the project root.

---

## CODE DOCUMENTATION RULE — NON-NEGOTIABLE

Read `docs/CODE_STYLE.md` before writing any function, class, or module.

Every exported function, class, and type must have a docstring. Every non-obvious decision inside a function must have an inline comment explaining *why*, not what.

---

## COMMANDS

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Type check
uv run mypy src/

# Lint
uv run ruff check src/ tests/

# Run a script
uv run python src/[script].py
```

Run typecheck and tests after every non-trivial change. Do not consider a task done until both pass.

---

## STACK

- Python 3.11+
- uv (package manager and virtual environment)
- pytest (testing)
- mypy (type checking)
- ruff (linting and formatting)
- Anthropic Python SDK (Claude API access)
- Research/data: numpy, pandas, matplotlib (add as needed)

---

## ARCHITECTURE RULES

- `src/` contains all source code. No runnable scripts at the project root.
- `src/experiments/` contains individual experiment scripts.
- `src/utils/` contains shared utilities (API clients, data loaders, metrics).
- `src/config.py` contains all configuration constants. No magic numbers in experiment code.
- `tests/` mirrors `src/`. Every module in `src/` has a corresponding test file.
- Results and data are never committed. They go in `results/` and `data/` which are gitignored.
- Experiment configurations are versioned in `configs/` as YAML files — not hardcoded in scripts.

---

## ERROR HANDLING — NON-NEGOTIABLE

This project uses **return-based error handling** for expected failures. Do not raise exceptions for predictable failures.

```python
# The pattern — use TypedDict or dataclass for results
from typing import TypedDict, Literal

class Success[T](TypedDict):
    ok: Literal[True]
    data: T
    error: None

class Failure[E](TypedDict):
    ok: Literal[False]
    data: None
    error: E

# Usage — wrap API calls
def call_model(prompt: str) -> Success[str] | Failure[str]:
    try:
        response = client.messages.create(...)
        return {"ok": True, "data": response.content[0].text, "error": None}
    except anthropic.RateLimitError:
        return {"ok": False, "data": None, "error": "RATE_LIMITED"}
    except anthropic.APIError as e:
        return {"ok": False, "data": None, "error": f"API_ERROR: {e}"}
```

- **Never** raise an exception inside an experiment runner for a predictable API failure.
- **Never** return `None` to signal failure — the caller cannot distinguish "no result" from "error".
- **Always** wrap third-party API calls in a thin adapter that converts exceptions to typed errors.

---

## FILE ORGANIZATION

```
pvr/
├── .llmignore
├── CLAUDE.md
├── MEMORY.md
├── CONTEXT.md
├── DECISIONS.md
├── CHANGELOG.md
├── PRPs/
│   ├── TEMPLATE.md
│   ├── DISCOVERY.md
│   └── [experiment-name].md
├── configs/               # YAML experiment configurations
├── data/                  # Raw datasets (gitignored)
├── results/               # Experiment outputs (gitignored)
├── src/
│   ├── config.py          # Global constants and settings
│   ├── experiments/       # Individual experiment scripts
│   └── utils/             # Shared utilities (api, metrics, data)
├── tests/                 # Mirrors src/
├── docs/
│   ├── CODE_STYLE.md
│   └── source/            # Meetings, research, constraints
└── reports/               # EOD reports
```

---

## ANTI-PATTERNS

1. **Never hardcode model names in experiment code.** They belong in `configs/` YAML files or `src/config.py`.
2. **Never commit API keys or `.env` files.** Load from environment — crash loudly at startup if missing.
3. **Never make API calls in tests.** Mock all LLM clients in `tests/`. Real API calls belong in integration tests gated by a flag.
4. **Never store raw results in git.** Results go in `results/` (gitignored). Summarized tables go in `docs/`.
5. **Never write a one-shot script at the repo root.** All runnable code lives in `src/`.
6. **Never silently swallow API errors.** Return them as typed failures and log at WARNING level.
7. **Never use `print()` for experiment output.** Use Python's `logging` module with structured log levels.

---

## KNOWN ISSUES — DO NOT FIX

None yet.
