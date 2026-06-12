## FEATURE/EXPERIMENT: [one sentence]

## OBJECTIVE
[2–3 sentences describing what "done" looks like from a researcher's perspective]

## CONTEXT

- Starting state: [which files currently exist and are relevant]
- Ending state: [which files will be created or modified]
- Related existing code: [specific file paths to read before starting]
- Open decisions that must be resolved first: [list any DECISIONS.md entries that block this]

## IMPLEMENTATION REQUIREMENTS

### Must Do
- [specific requirement]
- [specific requirement]

### Must NOT Do
- [explicit exclusion — be specific about why]
- [explicit exclusion]

## ERROR HANDLING REQUIREMENTS

- [Which errors this experiment must surface and how]
- [API rate limits: how to handle and retry]
- [What the caller receives on each failure path — use the project's Success/Failure pattern]

## SECURITY CONSIDERATIONS

- [API key handling — must be loaded from environment, never hardcoded]
- [Input validation — what config/dataset parameters must be validated before use]
- [Data exposure — what must never appear in logs]

## TESTS TO WRITE

List the specific test cases before any implementation begins:
- [ ] Happy path: [describe]
- [ ] Error path: [describe each Failure variant]
- [ ] Edge case: [describe]

## ROLLBACK PLAN

If this experiment needs to be abandoned mid-implementation:
- Branch to return to: [branch name]
- State the codebase should be in: [describe]

## ACCEPTANCE CRITERIA
- [ ] [testable criterion]
- [ ] [testable criterion]
- [ ] All existing tests pass
- [ ] New tests written and passing
- [ ] `uv run mypy src/` passes with no errors
- [ ] `uv run ruff check src/ tests/` passes
- [ ] CHANGELOG.md updated

## VALIDATION
Run these commands to verify completion:
```bash
uv run pytest tests/
uv run mypy src/
uv run ruff check src/ tests/
```
