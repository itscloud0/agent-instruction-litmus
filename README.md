# agent-instruction-litmus

`agent-instruction-litmus` is a local behavior fixture runner for developers and agent-tool authors debugging coding-agent instruction files that are ignored, reset, or applied inconsistently. It checks whether rules in `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, Copilot instructions, Cursor rules, or Roo rules are actually followed in observable output or diffs.

The first build is intentionally small. It creates disposable fixture repositories, gives you an exact prompt, and scores the artifacts after an agent or human has run the task. The Codex CLI, opencode, and Gemini CLI adapters are guarded behind an explicit `--allow-live` flag because they can consume model-provider quota.

## Quickstart

Install the published `v0.2.2` release without cloning the repository:

```bash
python -m pip install "git+https://github.com/itscloud0/agent-instruction-litmus.git@v0.2.2"
agent-instruction-litmus fixtures
```

For a one-off run without installing a persistent command, use `uvx`:

```bash
uvx --from "git+https://github.com/itscloud0/agent-instruction-litmus.git@v0.2.2" \
  agent-instruction-litmus fixtures
```

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

Run the guarded Gemini CLI adapter for the fresh-session memory fixture:

```bash
python -m agent_instruction_litmus run \
  --adapter gemini-cli \
  --allow-live \
  --fixture gemini-memory-reload \
  --output /tmp/litmus-gemini-memory
```

The Gemini adapter starts a fresh process in the fixture workspace, which exercises the startup/reset boundary for `GEMINI.md`. Gemini's interactive `/memory reload` and `/clear` commands are not driven by the headless adapter. A provider account or location failure is reported as `BLOCKED` before instruction scoring, rather than as an instruction `FAIL`. See Gemini's [memory management](https://geminicli.com/docs/cli/tutorials/memory-management/) and [headless mode](https://geminicli.com/docs/cli/tutorials/automation/) documentation for the client-side behavior.

## Fixtures

- `root-agents-md`: verifies that a root `AGENTS.md` rule is followed in a normal task.
- `review-loads-agents-md`: verifies that a review-mode response includes a marker required by `AGENTS.md`.
- `nested-scope-precedence`: verifies that a nested `AGENTS.md` rule overrides a root fallback instruction for a scoped file.
- `large-file-truncation`: verifies that a late sentinel in a large `AGENTS.md` overrides an early fallback marker.
- `gemini-memory-reload`: verifies that a fresh or reloaded Gemini CLI session applies a root `GEMINI.md` instruction.

## Limits

- A pass only proves that one fixture passed in one run.
- A fail can mean the instruction file was not loaded, was truncated, was overridden, or was ignored by the model. The report keeps those separate when the artifact allows it.
- The large-file fixture is boundary evidence only: it can expose a missed late sentinel or an early fallback, but a pass is still one-run evidence, not a guarantee for every larger instruction file.
- The Gemini adapter is guarded and reports account/location blocks, but Gemini instruction-following remains unvalidated until an eligible live account is available.
- Automated Claude, Roo, and Copilot adapters are not included yet.
- Live Codex and opencode runs may consume account quota and can vary across repeated model runs.
- No fixture reads `.env` files, secrets, or unrelated project files.

## Post-Release Work

The `v0.2.2` release validates Codex CLI and opencode against the four non-Gemini local fixtures, including one fresh large-file truncation run per adapter. The guarded Gemini adapter and local memory-reload fixture are now present, but the Gemini live gate remains pending the eligible account/location recorded in issue #2. Remaining useful work is tracked in the GitHub issue for Claude Code `CLAUDE.md` behavior.
