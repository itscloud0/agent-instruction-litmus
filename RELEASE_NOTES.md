# agent-instruction-litmus v0.2.2

## Fixed

- Align the runtime `__version__` with the published package metadata so installed clients can report the actual release version.

# agent-instruction-litmus v0.2.1

## Added

- `gemini-memory-reload`, a disposable `GEMINI.md` startup/reset-boundary fixture.
- A guarded Gemini CLI adapter with ignored `.litmus/` captures and explicit `--allow-live` opt-in.
- `BLOCKED` adapter reports for account-tier, unsupported-location, and authentication failures that happen before instruction scoring.

## Limits

- Gemini CLI 0.39.1 is installed locally, but live validation remains blocked by the account/location eligibility recorded in issue #2. No Gemini instruction-following support claim is made until a live `PASS` is available.

# Unreleased

# agent-instruction-litmus v0.2.0

Second release adds the large-file truncation fixture and publishes its first two-client benchmark.

## Included

- `large-file-truncation`, a disposable fixture with an early fallback marker and a late instruction sentinel beyond the 32,000-character boundary.
- Scorer regression coverage that distinguishes missing files, empty artifacts, missing sentinels, forbidden fallback markers, and passing sentinels.
- Benchmark and validation evidence for Codex CLI 0.144.5 and opencode 1.16.2.

## Validated

- Python 3.12.13 test suite, compileall, CLI fixture listing, and package checks passed.
- Codex CLI and opencode each passed one fresh `large-file-truncation` run with return code 0 and the expected sentinel in `result.txt`.

## Limits

- A pass is one-run boundary evidence, not a guarantee for every larger instruction file, client, model, or future version.
- Live model runs remain opt-in and may consume provider quota.

# agent-instruction-litmus v0.1.0

Initial release candidate for `agent-instruction-litmus`.

## Included

- Local CLI for coding-agent instruction-file behavior fixtures.
- Fixture generation for disposable repositories.
- Scoring for terminal, JSON, and Markdown reports.
- Manual-run adapter.
- Guarded Codex CLI adapter behind `--allow-live`.
- Guarded opencode CLI adapter behind `--allow-live`.
- Three behavior fixtures:
  - `root-agents-md`
  - `review-loads-agents-md`
  - `nested-scope-precedence`
- Benchmark, validation, safety, and discoverability documentation.

## Validated

- Codex CLI passed all three fixtures in a fresh live matrix.
- opencode CLI passed all three fixtures in a fresh live matrix.
- Local tests passed on the release candidate.

## Limitations

- This is not a static linter, prompt generator, rule converter, policy gateway, or model leaderboard.
- A pass only proves one fixture passed in one run.
- Live model runs can vary and may consume provider quota.
- Claude Code and Gemini CLI adapters are not included in this release candidate because local authentication or account eligibility blocked headless validation.
- CI intentionally avoids live model calls.
