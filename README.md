# agent-instruction-litmus

`agent-instruction-litmus` is a local behavior fixture runner for developers and agent-tool authors debugging coding-agent instruction files that are ignored, reset, or applied inconsistently. It checks whether rules in `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, Copilot instructions, Cursor rules, or Roo rules are actually followed in observable output or diffs.

The first build is intentionally small. It creates disposable fixture repositories, gives you an exact prompt, and scores the artifacts after an agent or human has run the task. The Codex CLI and opencode adapters are guarded behind an explicit `--allow-live` flag because they can consume model-provider quota.

## Quickstart

List fixtures:

```bash
python -m agent_instruction_litmus fixtures
```

Create a root `AGENTS.md` fixture:

```bash
python -m agent_instruction_litmus init --fixture root-agents-md --output /tmp/litmus-root
```

Run your agent in `/tmp/litmus-root` using the prompt in `TASK.md`, then score the result:

```bash
python -m agent_instruction_litmus score --fixture root-agents-md --workspace /tmp/litmus-root
```

For review-mode checks, paste the agent review output into `agent-output.txt` before scoring:

```bash
python -m agent_instruction_litmus init --fixture review-loads-agents-md --output /tmp/litmus-review
python -m agent_instruction_litmus score --fixture review-loads-agents-md --workspace /tmp/litmus-review --format markdown
```

Run the Codex CLI adapter only when live model calls are acceptable:

```bash
python -m agent_instruction_litmus run \
  --adapter codex-cli \
  --allow-live \
  --fixture root-agents-md \
  --output /tmp/litmus-codex-root
```

For `review-loads-agents-md`, the adapter initializes a disposable git baseline, creates an uncommitted review diff, stores Codex stdout/stderr/last-message captures under `.litmus/`, copies the final review text to `agent-output.txt`, and scores the fixture.

Run the opencode adapter only when live model calls are acceptable:

```bash
python -m agent_instruction_litmus run \
  --adapter opencode-cli \
  --allow-live \
  --fixture root-agents-md \
  --output /tmp/litmus-opencode-root
```

For `review-loads-agents-md`, the adapter stores opencode stdout/stderr/last-message captures under `.litmus/`, preserves `agent-output.txt` if opencode writes the review file itself, and otherwise scores the extracted final text response.

## Fixtures

- `root-agents-md`: verifies that a root `AGENTS.md` rule is followed in a normal task.
- `review-loads-agents-md`: verifies that a review-mode response includes a marker required by `AGENTS.md`.
- `nested-scope-precedence`: verifies that a nested `AGENTS.md` rule overrides a root fallback instruction for a scoped file.
- `large-file-truncation`: verifies that a late sentinel in a large `AGENTS.md` overrides an early fallback marker.

## Limits

- A pass only proves that one fixture passed in one run.
- A fail can mean the instruction file was not loaded, was truncated, was overridden, or was ignored by the model. The report keeps those separate when the artifact allows it.
- The large-file fixture is boundary evidence only: it can expose a missed late sentinel or an early fallback, but a pass is still one-run evidence, not a guarantee for every larger instruction file.
- Automated Gemini, Claude, Roo, and Copilot adapters are not included yet.
- Live Codex and opencode runs may consume account quota and can vary across repeated model runs.
- No fixture reads `.env` files, secrets, or unrelated project files.

## Post-Release Work

The first release validates Codex CLI and opencode against three fixtures. Remaining useful work is tracked in GitHub issues for Claude Code `CLAUDE.md`, Gemini CLI `GEMINI.md` clear/reset behavior, and live adapter benchmarking for large-file truncation behavior.
