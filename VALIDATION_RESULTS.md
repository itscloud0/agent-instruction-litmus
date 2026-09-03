# Validation Results: agent-instruction-litmus

Date: 2026-07-01 09:12 Europe/Amsterdam.

Lifecycle mode: `VALIDATE`.

## Codex CLI Adapter Feasibility

Environment:

- Codex CLI: `0.133.0` at `/opt/homebrew/bin/codex`.
- Auth: `codex doctor` reported ChatGPT auth configured and provider websocket reachable.
- Doctor caveats: update/install target mismatch, `TERM=dumb` in the shell before setting `TERM=xterm-256color`, and large local rollout cache. These do not block fixture execution.

Commands validated:

- Normal task: `codex exec --ephemeral --skip-git-repo-check --ignore-user-config -C <fixture> -s workspace-write --json -o <capture> - < TASK.md`
- Review task: `codex exec review --ephemeral --ignore-user-config --uncommitted --json -o agent-output.txt`

Important command-shape findings:

- `codex exec` in this version does not accept `-a`; approval policy must not be passed that way.
- `codex exec review --uncommitted` rejects a custom prompt argument. The review fixture must rely on `AGENTS.md` plus the reviewed diff, not a piped `TASK.md` prompt.
- Review mode has no `-C` flag in this version; the adapter must run from the fixture directory.
- Review mode needs a disposable git repository and an uncommitted diff.
- Capture files must be ignored or stored under `.litmus/`; otherwise review mode can review its own generated logs.

## Fixture Results

| Fixture | Adapter path | Result | Evidence |
|---|---|---|---|
| `root-agents-md` | `codex exec` | `PASS` | `result.txt` contained `INSTRUCTION_LITMUS_ROOT_PASS`. |
| `review-loads-agents-md` | `codex exec review --uncommitted` | `PASS` | `agent-output.txt` contained `INSTRUCTION_LITMUS_REVIEW_PASS`. |

## Gate Status

- First real adapter path: `PASS` for Codex CLI feasibility.
- Automated Codex adapter: `UNKNOWN`; feasible but not implemented yet.
- Publication validation: `UNKNOWN`; this still needs at least one second adapter shape and repeated-run stability.
- Benchmark: `UNKNOWN`.
- Discoverability: `UNKNOWN`.

## Follow-Up

Build a guarded Codex CLI adapter that is opt-in for live model calls, stores run captures under `.litmus/`, prepares review fixtures with a local git baseline, and documents that live calls may consume the user's Codex/ChatGPT quota. Then validate a second adapter shape before publication.

## 2026-07-02 - Guarded Codex Adapter Stability

Lifecycle mode: `VALIDATE`.

Implementation validated:

- `run --adapter codex-cli --allow-live` executes Codex only with explicit opt-in.
- Normal task runs use `codex exec --ephemeral --skip-git-repo-check --ignore-user-config -C <fixture> -s workspace-write --json -o <fixture>/.litmus/codex-last-message.txt -`.
- Review task runs use `codex exec review --ephemeral --ignore-user-config --uncommitted --json -o <fixture>/.litmus/codex-last-message.txt`.
- Review fixtures initialize a disposable git baseline and create an uncommitted diff before invoking Codex review.
- Captures are written under `.litmus/`, which generated fixtures ignore.

Repeated live Codex results:

| Fixture | Runs | Result | Evidence |
|---|---:|---|---|
| `root-agents-md` | 2 | `PASS` | Both fresh temp fixture runs returned code 0 and `result.txt` contained `INSTRUCTION_LITMUS_ROOT_PASS`. |
| `review-loads-agents-md` | 2 | `PASS` | Both fresh temp fixture runs returned code 0 and `agent-output.txt` contained `INSTRUCTION_LITMUS_REVIEW_PASS`. |

Second adapter probes:

- Gemini CLI is installed at `/opt/homebrew/bin/gemini`, but a headless `GEMINI.md` fixture probe failed before model execution with `IneligibleTierError` / `UNSUPPORTED_LOCATION` for Gemini Code Assist for individuals.
- Claude Code is installed at `/Users/iliasorokin/.local/bin/claude`, but a headless `CLAUDE.md` fixture probe failed before model execution with HTTP 401 invalid authentication credentials.

Gate status:

- Automated Codex adapter: `PASS`.
- Repeated Codex stability for the two current fixtures: `PASS` for 4/4 live runs.
- Second adapter shape: `UNKNOWN`, blocked by local Gemini eligibility and Claude authentication.
- Publication validation: `UNKNOWN`; publication still requires at least two agent ecosystems, benchmark evidence, discoverability review, CI, and safety checks.

Follow-up:

Run an authenticated second-ecosystem validation, preferably Claude Code with `CLAUDE.md` or Gemini CLI with `GEMINI.md`. If one passes, add the matching fixture and guarded adapter path; if both remain blocked, kill or route before publication because the project must not publish as a Codex-only harness.

## 2026-07-04 - opencode CLI Second Adapter Validation

Lifecycle mode: `VALIDATE`.

Environment:

- opencode CLI: `1.16.2` at `/Users/iliasorokin/.opencode/bin/opencode`.
- Claude Code: `2.1.83` at `/Users/iliasorokin/.local/bin/claude`; headless probe failed before model execution with HTTP 401 invalid authentication credentials.
- Gemini CLI: `0.39.1` at `/opt/homebrew/bin/gemini`; headless probe failed before model execution with `IneligibleTierError` / `UNSUPPORTED_LOCATION` for Gemini Code Assist for individuals.

Implementation validated:

- `run --adapter opencode-cli --allow-live` executes opencode only with explicit opt-in.
- Normal task runs use `opencode run --dir <fixture> --pure --format json --dangerously-skip-permissions <TASK.md>`.
- Review-output runs use `opencode run --dir <fixture> --pure --format json <TASK.md>`.
- Captures are written under `.litmus/`.
- Review scoring preserves `agent-output.txt` when opencode writes it; this matters because opencode may put the marker in the written review artifact while the final assistant summary only says the review was saved.

Clean live opencode results after the preservation fix:

| Fixture | Runs | Result | Evidence |
|---|---:|---|---|
| `root-agents-md` | 2 | `PASS` | Both fresh temp fixture runs returned code 0 and `result.txt` contained `INSTRUCTION_LITMUS_ROOT_PASS`. |
| `review-loads-agents-md` | 2 | `PASS` | Both fresh temp fixture runs returned code 0 and `agent-output.txt` contained `INSTRUCTION_LITMUS_REVIEW_PASS`. |

Adapter-shape note:

- opencode uses the same `AGENTS.md` instruction-file surface as Codex for these first fixtures, but it is a distinct headless coding-agent client, command runner, model/provider stack, capture format, and permission path.
- This satisfies the second adapter shape needed to continue incubation, but it does not complete publication validation by itself.

Gate status:

- Automated opencode adapter: `PASS`.
- Repeated opencode stability for the two current fixtures: `PASS` for 4/4 clean live runs.
- Second adapter shape: `PASS` for Codex CLI plus opencode CLI.
- Claude Code and Gemini-specific adapters: `UNKNOWN`, blocked by local auth/eligibility.
- Publication validation: `UNKNOWN`; still needs benchmark, additional real-world fixture cases, safety, CI, and discoverability review.

Follow-up:

Start benchmark/discoverability work. Add at least one new fixture class next, preferably clear/reset behavior or nested instruction precedence, then run Codex and opencode against the expanded matrix before any private publication.

## 2026-07-05 - Expanded Matrix: Nested Scope Precedence

Lifecycle mode: `BENCHMARK`.

Implementation validated:

- `nested-scope-precedence` creates a root `AGENTS.md` fallback marker and a nested `pkg/AGENTS.md` scoped marker.
- Scoring requires `INSTRUCTION_LITMUS_NESTED_PASS` in `pkg/result.txt`.
- Scoring rejects `INSTRUCTION_LITMUS_NESTED_ROOT_FAIL` if it appears in the same target artifact.

Live results:

| Adapter | Fixture | Result | Evidence |
|---|---|---|---|
| Codex CLI | `root-agents-md` | `PASS` | Existing root marker fixture passed in a fresh run. |
| Codex CLI | `review-loads-agents-md` | `PASS` | Existing review marker fixture passed in a fresh run. |
| Codex CLI | `nested-scope-precedence` | `PASS` | `pkg/result.txt` contained `INSTRUCTION_LITMUS_NESTED_PASS` and not the root fallback marker. |
| opencode CLI | `root-agents-md` | `PASS` | Existing root marker fixture passed in a fresh run. |
| opencode CLI | `review-loads-agents-md` | `PASS` | Existing review marker fixture passed in a fresh run. |
| opencode CLI | `nested-scope-precedence` | `PASS` | `pkg/result.txt` contained `INSTRUCTION_LITMUS_NESTED_PASS` and not the root fallback marker. |

Run root:

- `/tmp/agent-instruction-litmus-20260705-live`

Gate status:

- Expanded matrix across three behavior cases: `PASS`.
- Codex CLI plus opencode CLI validation: `PASS`.
- Benchmark evidence: `PASS`, citing `BENCHMARK_RESULTS.md`.
- Publication readiness: `PASS` for `v0.1.0`; CI, safety/package checks, discoverability, public visibility, and release creation completed after this matrix.

Follow-up:

Post-release work is tracked in roadmap issues for Claude Code, Gemini CLI, and large-file truncation fixtures.

## 2026-07-25 - Large-file Truncation Matrix

Lifecycle mode: `BENCHMARK`.

Local fixture/scorer validation:

- `large-file-truncation` generates a disposable `AGENTS.md` longer than 32,000 characters with an early fallback and a late sentinel.
- The scorer now has regression coverage for a missing file (`MISSING`), an empty artifact (`FAIL`), an existing artifact without the sentinel (`FAIL`), a forbidden fallback (`FAIL`), and the expected sentinel (`PASS`).
- Python 3.12.13 tests, compileall, CLI fixture listing, and both live adapter runs completed from the owned checkout.

Live results:

| Adapter | Version | Result | Evidence |
|---|---:|---|---|
| Codex CLI | 0.144.5 | `PASS` | One fresh disposable run returned code 0 and wrote `INSTRUCTION_LITMUS_TRUNCATION_SENTINEL_PASS` to `result.txt`. Captures: `/tmp/agent-instruction-litmus-truncation-20260725-codex-live`. |
| opencode CLI | 1.16.2 | `PASS` | One fresh disposable run returned code 0 and wrote `INSTRUCTION_LITMUS_TRUNCATION_SENTINEL_PASS` to `result.txt`. Captures: `/tmp/agent-instruction-litmus-truncation-20260725-opencode-live`. |

Interpretation:

- The late sentinel was observed by both supported adapters in one fresh run each.
- This is boundary evidence for the tested client versions, not a general guarantee about larger instruction files, other clients, models, or future versions.

## 2026-09-03 - Immutable CI Action Pins

Lifecycle mode: `MAINTAIN`.

Workflow hardening:

- Pinned `actions/checkout` v4 to commit `11d5960a326750d5838078e36cf38b85af677262`.
- Pinned all three `actions/setup-python` v5 uses to commit `a26af69be951a213d495a4c3e4e4022e16d87065`.
- Verified both full commit SHAs against the corresponding official tag refs with `git ls-remote` before editing.
- Added `tests/test_workflow.py`, which fails if the workflow action refs drift from these reviewed 40-hex commit pins.

Verification:

- Python 3.14.6: `PYTHONPATH=src python3 -m unittest discover -s tests -v` — 20 tests passed.
- `PYTHONPATH=src python3 -m compileall -q src tests` — passed.
- Local `action-pin-check` audit of `.github/workflows` — 3 actions, 0 findings.
- Ruby YAML parse, `git diff --check`, and scoped credential scan — passed.

Interpretation:

- CI now resolves the reviewed external action commits instead of mutable version tags, and the regression test protects the dependency boundary against future drift.
- This hardening changes workflow dependency resolution only; it does not add new client, model, host, benchmark, or adoption evidence.
