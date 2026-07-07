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
- Publication readiness: `PASS` for `v0.1.0`; CI, safety scan, package build/install, discoverability, public visibility, and release creation completed after this benchmark.

## Follow-Up

After release, extend the matrix through the roadmap issues for Claude Code, Gemini CLI, and large-file truncation behavior when the relevant validation path is available.

## 2026-07-07 Local Truncation Fixture Slice

This maintainer run added the local `large-file-truncation` fixture:

- `large-file-truncation`: a long `AGENTS.md` contains an early fallback marker and a late boundary sentinel marker. A pass means the agent wrote the late sentinel to `result.txt`; a forbidden fallback means the late sentinel was not observed or not followed.

Local verification:

- `PYTHONPATH=src python3.12 -m unittest discover -s tests` passed.
- `PYTHONPATH=src python3.12 -m compileall -q src tests` passed.
- `PYTHONPATH=src python3.12 -m agent_instruction_litmus fixtures` listed all four fixtures.
- Manual scoring smokes distinguished empty artifact, forbidden fallback marker, and expected sentinel marker.

Live adapter matrix:

| Adapter | Fixture | Result | Evidence |
|---|---|---|---|
| Codex CLI | `large-file-truncation` | `PENDING` | Not run in this automation run because `--allow-live` can consume provider quota. |
| opencode CLI | `large-file-truncation` | `PENDING` | Not run in this automation run because `--allow-live` can consume provider quota. |

Gate status:

- Local truncation fixture generation/scoring: `PASS`.
- Live Codex/opencode truncation behavior: `UNKNOWN` until an explicit live benchmark run is acceptable.
