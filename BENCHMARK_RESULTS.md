# Benchmark Results: agent-instruction-litmus

Date: 2026-07-05 13:19 Europe/Amsterdam.

Lifecycle mode: `BENCHMARK`.

## Scope

This run expanded the fixture matrix from two to three behavior cases:

- `root-agents-md`: root `AGENTS.md` instruction is followed in a normal edit task.
- `review-loads-agents-md`: review-mode output includes a marker required by `AGENTS.md`.
- `nested-scope-precedence`: nested `pkg/AGENTS.md` overrides a root fallback marker for a scoped file.

## Local Verification

- `PYTHONPATH=src python3 -m unittest discover -s tests` passed with 12 tests.
- `PYTHONPATH=src python3 -m compileall -q src tests` passed.
- `PYTHONPATH=src python3 -m agent_instruction_litmus fixtures` passed and listed all three fixtures.

## Live Adapter Matrix

Run root: `/tmp/agent-instruction-litmus-20260705-live`.

| Adapter | Fixture | Result | Evidence |
|---|---|---|---|
| Codex CLI | `root-agents-md` | `PASS` | `result.txt` contained `INSTRUCTION_LITMUS_ROOT_PASS`. |
| Codex CLI | `review-loads-agents-md` | `PASS` | `agent-output.txt` contained `INSTRUCTION_LITMUS_REVIEW_PASS`. |
| Codex CLI | `nested-scope-precedence` | `PASS` | `pkg/result.txt` contained `INSTRUCTION_LITMUS_NESTED_PASS` and not the root fallback marker. |
| opencode CLI | `root-agents-md` | `PASS` | `result.txt` contained `INSTRUCTION_LITMUS_ROOT_PASS`. |
| opencode CLI | `review-loads-agents-md` | `PASS` | `agent-output.txt` contained `INSTRUCTION_LITMUS_REVIEW_PASS`. |
| opencode CLI | `nested-scope-precedence` | `PASS` | `pkg/result.txt` contained `INSTRUCTION_LITMUS_NESTED_PASS` and not the root fallback marker. |

## Baseline

The manual baseline remains:

- create a disposable fixture with `init`
- open a fresh agent session in the fixture workspace
- paste `TASK.md`
- manually inspect the resulting file or transcript
- run `score`

The guarded adapters improve this for Codex CLI and opencode by creating the fixture, executing the client, capturing stdout/stderr/last message under `.litmus/`, and returning a scored verdict in one command.

## Gate Status

- Expanded fixture matrix: `PASS` for three unrelated instruction-file behavior cases.
- Two adapter shapes: `PASS` for Codex CLI and opencode CLI.
- Reproducible benchmark summary: `PASS` for this three-fixture matrix.
- Publication readiness: `UNKNOWN`; CI, safety scan, package build, final discoverability artifacts, and private repository publication are not complete.

## Follow-Up

Before private publication, run CI/safety/package checks, finish discoverability artifacts, create the private repository only if those gates pass, push, and wait for CI.
