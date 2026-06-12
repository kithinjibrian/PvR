# Discovery Interview Protocol

Use when an experiment or feature request arrives without a PRP.

## When to Run a Discovery Interview

Any time a request is described in one or two sentences without specifying:
- What the experiment measures and how success is defined
- Which models, datasets, or configurations are involved
- What the error and edge-case behavior should be
- Which existing files it touches
- What it must not touch
- Which open decisions in DECISIONS.md are relevant

## Question Sequence

Ask one question at a time. Do not batch questions. Wait for the answer before continuing.

Cover in order:
1. What does it measure — input, processing, output metric
2. Which models or providers are involved
3. Which dataset or context format is used
4. What happens when an API call fails — retry logic, fallback, or abort
5. Edge cases — empty context, max token limits, malformed responses
6. Which existing files it reads from or writes to
7. What it must never modify
8. Are there any open entries in DECISIONS.md this experiment depends on?
9. How results are stored and compared across runs
10. How success is verified — what commands prove it works?

## After the Interview

Write the completed PRP to `/PRPs/[experiment-name].md` using the template.
Present it to the user.
Wait for explicit approval before writing any code.
