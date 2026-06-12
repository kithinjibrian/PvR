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

## SESSION 2 — 2026-06-12 — Spec Integration — closed

Branch: claude/adoring-euler-ike61n

### WHAT WAS DONE

Integrated the full experiment spec into the context system. Stored the spec as
`docs/specs/lost-in-the-middle.md` (canonical source of truth). Created
`PRPs/lost-in-the-middle.md` (implementation checklist). Resolved all four open
decisions (DECISION-001 through DECISION-004) in DECISIONS.md. Updated MEMORY.md
with all seven architectural decisions derived from the spec.

### FILES CREATED OR MODIFIED

docs/specs/lost-in-the-middle.md   — Full technical spec (module interfaces, data contracts, implementation order)
PRPs/lost-in-the-middle.md         — Implementation checklist and test requirements
DECISIONS.md                       — All four decisions moved to RESOLVED
MEMORY.md                          — Seven architectural decisions recorded; NEXT SESSION START POINT updated
CHANGELOG.md                       — Unreleased section updated

### TESTS WRITTEN

None — no source code yet; test cases are listed in PRPs/lost-in-the-middle.md.

### DECISIONS MADE

- DECISION-001 resolved: Claude only (claude-sonnet-4-6) for v1
- DECISION-002 resolved: Synthetic needle-in-a-haystack with custom facts.json
- DECISION-003 resolved: Synchronous single-threaded runner with rate limiting
- DECISION-004 resolved: Per-trial JSON files in data/results/raw/

### PENDING DECISIONS OPENED

None.

### STILL OPEN AT CLOSE

No source code written yet. pyproject.toml does not exist yet.

---

## NEXT SESSION START POINT

Before anything else: append a new session entry to CONTEXT.md with state `open` and the current branch name. Commit it. Do not read any other file or write any code until this is done.

Then read CLAUDE.md, MEMORY.md, DECISIONS.md, and CONTEXT.md in that order. Then read `docs/specs/lost-in-the-middle.md` and `PRPs/lost-in-the-middle.md` in full.

All decisions are resolved. The PRP is approved. Begin implementation at Step 1 of the plan in MEMORY.md:

1. Create `pyproject.toml` (use the exact content from the spec §Dependencies)
2. Run `uv sync --extra dev`
3. Create `data/facts/facts.json` with 10+ manually verified facts following the spec schema
4. Implement `scripts/02_validate_facts.py` and confirm it passes

Write failing tests before implementing each module. Read `docs/CODE_STYLE.md` before writing any function.
