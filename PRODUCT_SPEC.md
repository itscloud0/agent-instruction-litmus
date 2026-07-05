# PRODUCT_SPEC: agent-instruction-litmus

## User Persona

Developers, maintainers, and agent-tool authors who rely on repository instruction files such as `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules`, or `.roo/rules` and need to know whether a coding agent actually loads and follows critical project rules before trusting it on real work.

## Job To Be Done

When adopting or upgrading a coding agent in a real repository, verify in 5-30 minutes whether the agent respects the repo's instruction files for loading, precedence, truncation, scoped rules, review modes, clear/resume behavior, and subagent behavior.

## Painful Problem

Instruction files are now treated as the control plane for coding agents, but users cannot distinguish three failure modes:

- the agent did not discover the file
- the harness loaded the file but lost or truncated critical rules
- the model saw the rule but did not follow it in the current mode

Today this is diagnosed manually through transcripts, logs, screenshots, and scattered bug reports. A repo can appear "AI-ready" because `AGENTS.md` or `CLAUDE.md` exists while the current agent still ignores a required test rule, language rule, no-commit rule, scoped directory rule, or review-mode rule.

## Proposed Better Workflow

Run a local instruction-adherence fixture suite against an installed agent or captured agent run:

```bash
agent-instruction-litmus init-fixtures
agent-instruction-litmus run --adapter codex-cli --fixture review-loads-agents-md
agent-instruction-litmus run --adapter gemini-cli --fixture clear-reloads-gemini-md
agent-instruction-litmus report --format markdown
```

The tool creates disposable fixture repositories with small sentinel tasks, runs the agent through a stable adapter when available, and reports:

- which instruction file should have applied
- which observable action proves the rule was followed or ignored
- whether the failure is discovery, precedence, truncation, mode-specific, or model-adherence
- a compact reproduction report for upstream issue filing

## Core v0.1 Feature Set

- Local CLI only. No hosted service.
- Disposable fixture repositories with deterministic sentinel tasks.
- Adapter interface for headless or semi-headless clients.
- Built-in manual-run adapter so users can paste a prompt and then let the CLI score the resulting diff/output.
- First automated adapter target: Codex CLI if the current CLI surface can run non-interactive fixtures without paid or UI-only flows.
- Second adapter target before publication: Gemini CLI, Claude Code, VS Code/Copilot diagnostic export, or another stable harness.
- JSON and Markdown reports.
- Fixture cleanup and no mutation outside temporary repositories.
- Documentation of unsupported clients and limits.

## Candidate Fixtures

- `root-agents-md`: root `AGENTS.md` requires an observable text or diff marker.
- `nested-scope-precedence`: nested instruction file overrides a root rule for a subdirectory task.
- `review-loads-agents-md`: review mode must apply the same repo rule as normal work mode or explicitly report unsupported.
- `large-file-truncation`: critical sentinel near the end of a long instruction file detects truncation.
- `clear-reloads-memory`: after `/clear` or equivalent reset, the next turn still obeys or reloads the project instruction file.
- `symlinked-workspace-discovery`: instruction discovery works or fails clearly when the workspace root is a symlink.
- `subagent-inherits-project-rules`: delegated agent or subagent follows the same project rule or reports unsupported.
- `conflict-priority`: global, project, and nested rules conflict; report which priority the harness used.
- `copilot-applyto-glob`: VS Code/Copilot-style `applyTo` rules are applied only to matching files.
- `roo-rules-discovery`: Roo-style workspace rules are discovered and applied in the expected mode.

## Non-Goals

- No new rule converter or sync tool.
- No generic `AGENTS.md` linter.
- No prompt-writing assistant.
- No governance gateway or policy engine.
- No broad model leaderboard.
- No secret scanning, package scanning, or MCP scanning.
- No claims that a passed fixture proves full future compliance.
- No publication if only one proprietary UI-only client can be tested.

## Existing Tools And Why This Is Different

- AgentLint statically lints agent harness files and scores `AGENTS.md`, `CLAUDE.md`, hooks, CI, and related configuration. `agent-instruction-litmus` would run behavior fixtures and score actual agent output, not just source files.
- `agents-md` linters and generators improve the file content itself. They do not prove the active agent loaded and obeyed the file in review, clear/resume, scoped, or subagent modes.
- AGENTIF and IFScale benchmark model instruction following. They do not test installed coding-agent harness behavior around repo file discovery, precedence, slash commands, or mode-specific memory.
- "Evaluating AGENTS.md" studies whether repository context files improve coding-agent task success and cost. It is research evidence, not a local conformance harness for a user's installed toolchain.
- VS Code/Copilot and Gemini CLI expose diagnostics such as loaded instruction files or memory listings. Diagnostics help inspect loaded context, but they do not provide cross-client fixture reports or upstream-ready repros.

## Why Upstream Contribution Is Insufficient

Each client must fix its own instruction loading, precedence, and mode behavior. The recurring failure class spans Codex, Claude Code, Gemini CLI, Roo Code, and VS Code/Copilot-style instruction systems. A shared fixture corpus can turn repeated anecdotal reports into comparable reproductions.

The standalone incubation remains justified only if at least two adapter shapes are feasible and the fixtures produce actionable failures beyond static linting. If the useful output collapses into an AgentLint rule, a Gemini/Codex bugfix, or a one-off Claude hook, route it upstream and kill the project.

## Why This Strengthens Ilia's Profile

This is practical coding-agent reliability infrastructure: fixture design, local adapters, instruction precedence, context lifecycle, and reproducible reports for real client behavior. It is not a prompt package or another context-file generator.

## Publish Criteria

- Value, demand, product, validation, usability, engineering, distribution, and discoverability gates are recorded as `PASS`, `FAIL`, or `UNKNOWN`.
- At least six public pain signals map to fixtures.
- At least three unrelated real-world cases are modeled.
- At least two agent ecosystems are validated, or the project is killed before publication.
- A meaningful baseline compares against manual prompt/testing plus available diagnostics such as Codex logs, Gemini `/memory`, and VS Code Copilot diagnostics.
- Reports are useful enough to attach to upstream issues without exposing secrets.
- CI runs fixture and report-rendering tests without requiring live paid models.
- README states the exact problem, target users, limitations, supported adapters, and search terms naturally.
