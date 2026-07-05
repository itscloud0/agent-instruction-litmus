# Build Results: agent-instruction-litmus

Date: 2026-06-30 09:24 Europe/Amsterdam.

Lifecycle mode: `BUILD`.

## Work Completed

- Added a minimal Python package under `src/agent_instruction_litmus/`.
- Added CLI commands:
  - `fixtures` lists available fixtures.
  - `init` creates disposable fixture repositories.
  - `score` scores completed fixture artifacts.
  - `run --adapter manual` creates a fixture and prints manual-run instructions.
  - `run --adapter codex-cli` detects Codex on `PATH` but remains a feasibility stub; it does not run live model calls yet.
- Added two initial fixtures:
  - `root-agents-md`
  - `review-loads-agents-md`
- Added terminal, JSON, and Markdown report rendering.
- Added README and package metadata.
- Added unit tests for fixture creation, scoring, and CLI behavior.

## Verification

- `PYTHONPATH=src python3 -m unittest discover -s tests` passed: 5 tests.
- `PYTHONPATH=src python3 -m compileall -q src tests` passed.
- `PYTHONPATH=src python3 -m agent_instruction_litmus fixtures` passed and listed both initial fixtures.
- CLI smoke through unit tests created a fixture, wrote the required marker, and scored it as `PASS`.
- Codex executable was detected at `/opt/homebrew/bin/codex`, but automated Codex execution was intentionally not enabled in this build.

## Gate Status

- Build: `PASS` for minimal local fixture generator, scorer, report renderer, manual-run adapter, package metadata, README, and tests.
- Real-world validation: `UNKNOWN`; no live coding-agent fixture has been executed yet.
- Benchmark: `UNKNOWN`.
- Discoverability: `UNKNOWN`; README and metadata exist, but the gate is not complete.
- Publication: `BLOCKED` by validation, benchmark, safety/discoverability, CI, and adapter gates.

## Next Action

Validate the first real adapter path:

1. Run the `root-agents-md` and `review-loads-agents-md` fixtures manually against Codex CLI.
2. Decide whether safe automated Codex execution is feasible without brittle UI automation or uncontrolled paid model calls.
3. If Codex is feasible, add a guarded automated adapter; otherwise keep manual mode and validate Gemini CLI or Claude Code as the second adapter shape.

## 2026-07-02 - Guarded Codex CLI Adapter

Lifecycle mode: `BUILD`.

Work completed:

- Added `agent_instruction_litmus.adapters.run_codex_cli`.
- Changed `run --adapter codex-cli` from a feasibility stub into a guarded live adapter.
- Required explicit `--allow-live` before any Codex/ChatGPT-backed call can run.
- Added `--codex-bin` and `--timeout-seconds` for bounded local validation.
- Stored Codex stdout, stderr, and last-message captures under ignored `.litmus/`.
- Prepared `review-loads-agents-md` with a disposable git repository, committed baseline, and uncommitted review diff before `codex exec review --uncommitted`.
- Copied review last-message output into `agent-output.txt` for normal scoring.
- Documented live quota/cost risk and Codex run behavior in `README.md`.

Verification:

- `PYTHONPATH=src python3 -m unittest discover -s tests` passed: 8 tests.
- `PYTHONPATH=src python3 -m compileall -q src tests` passed.
- `PYTHONPATH=src python3 -m agent_instruction_litmus fixtures` passed.
- Offline tests exercise the live adapter path through a fake Codex executable; CI remains free of live model calls.

Gate status:

- Guarded Codex CLI adapter build: `PASS`.
- Offline engineering verification: `PASS`.
- Live adapter stability: see `VALIDATION_RESULTS.md`.
- Second adapter shape: `UNKNOWN`; Gemini and Claude probes were blocked by local account/auth state.

## 2026-07-04 - Guarded opencode CLI Adapter

Lifecycle mode: `BUILD` with validation follow-up.

Work completed:

- Added `agent_instruction_litmus.adapters.run_opencode_cli`.
- Added `run --adapter opencode-cli --allow-live`.
- Required explicit `--allow-live` before any opencode-backed model call can run.
- Added `--opencode-bin` for local executable selection.
- Stored opencode stdout, stderr, and extracted final text captures under ignored `.litmus/`.
- Preserved `agent-output.txt` when opencode writes the review artifact itself; otherwise the adapter writes extracted text output for scoring.
- Documented live quota risk and opencode run behavior in `README.md`.

Verification:

- `PYTHONPATH=src python3 -m unittest discover -s tests` passed: 11 tests.
- `PYTHONPATH=src python3 -m compileall -q src tests` passed.
- `PYTHONPATH=src python3 -m agent_instruction_litmus fixtures` passed.
- Offline tests exercise the opencode adapter path through a fake executable; CI remains free of live model calls.

Gate status:

- Guarded opencode CLI adapter build: `PASS`.
- Offline engineering verification: `PASS`.
- Live opencode stability: see `VALIDATION_RESULTS.md`.
- Claude Code second-adapter probe remains blocked by invalid local authentication.
- Gemini CLI second-adapter probe remains blocked by account/location eligibility.

## 2026-07-05 - Nested Scope Fixture And Benchmark Prep

Lifecycle mode: `BENCHMARK`.

Work completed:

- Added `nested-scope-precedence`.
- Generated a root `AGENTS.md` fallback rule plus nested `pkg/AGENTS.md` scoped rule.
- Extended fixture scoring with an optional forbidden-marker check so this fixture can reject the root fallback marker when nested precedence should apply.
- Updated README fixture coverage and target-pain wording.
- Added `BENCHMARK_RESULTS.md` and `DISCOVERABILITY.md`.

Verification:

- `PYTHONPATH=src python3 -m unittest discover -s tests` passed: 12 tests.
- `PYTHONPATH=src python3 -m compileall -q src tests` passed.
- `PYTHONPATH=src python3 -m agent_instruction_litmus fixtures` passed.

Gate status:

- Expanded fixture build: `PASS`.
- Local engineering verification: `PASS`.
- Live expanded matrix: see `BENCHMARK_RESULTS.md` and `VALIDATION_RESULTS.md`.
