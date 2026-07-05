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
