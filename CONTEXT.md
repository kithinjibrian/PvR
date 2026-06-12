# CONTEXT.md — PvR (Primacy vs. Recency)

Session handoff file. Updated at the end of every session.
Read at the start of the next session alongside CLAUDE.md, MEMORY.md, and DECISIONS.md.

Every session has a name and a state: open | closed.
A session is closed only after CONTEXT.md is committed and pushed.

---

## SESSION 1 — 2026-06-12 — Context Engineering Setup — closed

Branch: claude/adoring-euler-ike61n

### WHAT WAS DONE

Set up the complete context engineering system for the PvR project. Created all ten
interlocking files that form the AI session environment: CLAUDE.md (behavioral rules),
MEMORY.md (architectural decisions), CONTEXT.md (this file), DECISIONS.md (open questions),
CHANGELOG.md (shipping history), .llmignore (protected files), PRPs/TEMPLATE.md,
PRPs/DISCOVERY.md, docs/CODE_STYLE.md, and this session handoff.

### FILES CREATED OR MODIFIED

CLAUDE.md              — Behavioral rules for AI coding assistants
MEMORY.md              — Resolved architectural decisions (empty to start)
CONTEXT.md             — Session handoff log (this file)
DECISIONS.md           — Pending decisions register with initial open questions
CHANGELOG.md           — Human-readable shipping history
.llmignore             — Files the LLM must never touch
PRPs/TEMPLATE.md       — PRP template for new features/experiments
PRPs/DISCOVERY.md      — Discovery interview protocol
docs/CODE_STYLE.md     — Code documentation rules and patterns

### TESTS WRITTEN

None — no source code exists yet.

### DECISIONS MADE

- Used return-based error handling pattern (typed Success/Failure dicts) rather than exceptions for predictable API failures.
- uv chosen as package manager (reflected in CLAUDE.md commands).
- src/ layout with experiments/, utils/, config.py as top-level structure.

### PENDING DECISIONS OPENED

- DECISION-001: Which LLM providers to benchmark against
- DECISION-002: Dataset / benchmark to use for retrieval tasks
- DECISION-003: Whether to use async API calls for experiment runners

### STILL OPEN AT CLOSE

- No source code has been written yet. The project has only LICENSE, README.md, .gitignore, and the context engineering files.

---

---

## SESSION 2 — 2026-06-12 — Spec Integration — open

Branch: claude/adoring-euler-ike61n

---

## NEXT SESSION START POINT

Before anything else: append a new session entry to CONTEXT.md with state `open` and the current branch name. Commit it. Do not read any other file or write any code until this is done.

Then read CLAUDE.md, MEMORY.md, DECISIONS.md, and CONTEXT.md in that order.
Confirm you've read them by summarizing: current stack, last thing built, any open decisions blocking today's work, and what we're doing this session.

Three open decisions must be resolved before writing experiment code: DECISION-001 (which providers), DECISION-002 (which dataset), DECISION-003 (async vs sync). Present these to the user for resolution before writing any PRP for the core experiments.

First task once decisions are resolved: write a PRP for the project scaffold (pyproject.toml, src/ directory structure, config.py, utils/api.py wrapper).
