# Evaluation Plan: agent-instruction-litmus

## Central Claim

`agent-instruction-litmus` should make coding-agent instruction-file failures reproducible faster than manual prompts, transcript review, and client-specific diagnostics by running disposable behavior fixtures and emitting upstream-ready reports.

## Primary Evaluation

Build a minimal fixture runner and validate it against:

- a deterministic local reference scorer that evaluates fixture artifacts without live model calls
- one automated coding-agent adapter, preferably Codex CLI if its non-interactive surface can run the fixtures
- one second adapter shape before publication: Gemini CLI, Claude Code, VS Code/Copilot diagnostics/manual export, Roo Code, or another stable harness

Publication must not happen if only the reference scorer works.

## Fixture Matrix

| Fixture | Public pain mapped | Expected contract |
|---|---|---|
| `root-agents-md` | Codex #6502 and #7347 | root rule is observable in output or diff |
| `review-loads-agents-md` | Codex #5804 and #7878 | review mode either applies project instructions or reports unsupported |
| `nested-scope-precedence` | Gemini #16999, VS Code `applyTo` docs | scoped rule priority is observable and declared |
| `clear-reloads-memory` | Gemini #17629 | clear/reset mode reloads or preserves project memory before next task |
| `subagent-inherits-project-rules` | Claude #29423 | delegated agent inherits or explicitly declares missing project instructions |
| `large-file-truncation` | Codex docs mention `project_doc_max_bytes` and truncation | sentinel near end is followed or report flags truncation |
| `referenced-md-rule` | Claude #51039 | included or referenced Markdown rule is followed |
| `no-commit-rule` | Claude #34774 | agent does not perform a forbidden commit-like sentinel action |
| `symlinked-workspace-discovery` | Codex symlinked-workspace reports and diagnostics | workspace root and instruction file path are correctly discovered or reported |
| `roo-rules-discovery` | Roo custom-instruction complaints and issue #3754 | Roo-style rules are discoverable in the intended mode |

## Baselines

Manual baseline:

```bash
cat AGENTS.md
codex -c log_dir=./.codex-log
gemini
/memory show
/memory refresh
```

Client diagnostics baseline:

- Codex TUI logs or session JSONL.
- Gemini `/memory show`, `/memory refresh`, and `/memory list`.
- VS Code Copilot chat diagnostics and References.
- Claude Code transcript or debug output where available.
- AgentLint or agents-md linting for static file quality.

The contract suite must add value by packaging repeatable fixtures and an observable verdict, not by replacing native diagnostics.

## Metrics

Coverage:

- number of public pain classes represented by fixtures
- number of instruction-file formats covered
- number of client modes covered: normal, review, clear/reset, subagent, scoped files

Verdict quality:

- pass/fail/unsupported clarity
- ability to distinguish discovery, precedence, truncation, reset, subagent, and model-adherence failures
- false failures across repeated seeds or repeated agent runs

Workflow:

- commands and minutes required to produce a report versus manual diagnostics
- report completeness for upstream issue filing
- ability to rerun one fixture by name

Engineering:

- tests for fixture generation, artifact scoring, report rendering, and cleanup
- CI without live paid models
- no mutation outside fixture temp directories

## Real-World Validation Cases

Before publication, model at least three unrelated cases:

- Codex `/review` ignoring `AGENTS.md` from issues #5804 or #7878.
- Claude Code subagents or referenced Markdown rules ignoring project configuration from issues #29423 or #51039.
- Gemini CLI `GEMINI.md` clear/reset or priority behavior from issues #17629 or #16999.

At least two ecosystems must be represented before publication.

## Safety Checks

- Fixtures run only in temporary repositories created by the tool.
- No fixture reads `.env`, tokens, SSH keys, or unrelated project files.
- No fixture executes destructive shell commands.
- Reports redact local user paths unless needed for reproduction.
- Manual-run mode must tell the user exactly which temporary fixture repo is safe to use.

## Discoverability Gate

Status: `PASS` for `v0.1.0`.

Pre-publication discoverability work started on 2026-07-05 and is recorded in `DISCOVERABILITY.md`.

Before private or public publication, verify:

- README title and first paragraph name the exact pain: coding-agent instruction files ignored, `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` conformance, custom instructions not applied.
- Package metadata and repository topics include accurate terms such as `coding-agent`, `agents-md`, `claude-md`, `gemini-md`, `instruction-following`, `conformance`, and `developer-tools`.
- Quickstart includes search phrases developers use: "Codex ignores AGENTS.md", "Claude Code ignores CLAUDE.md", "Gemini CLI ignores GEMINI.md", "custom instructions not applied".
- Limitations explain nondeterminism, unsupported clients, paid-model requirements if any, and why a pass is not a guarantee.
- Distribution plan names issue threads, client docs, AgentLint/agents-md adjacent users, and package search surfaces without implying adoption.

Future releases must re-check repository metadata, release notes, and limitation wording before publication.

## Stop Or Reposition Criteria

Stop or reposition if:

- only static linting is feasible
- only one agent adapter can be tested
- tests require brittle UI automation as the primary path
- model nondeterminism prevents stable verdicts after reasonable retries
- native diagnostics or AgentLint absorb the fixture workflow
- the product becomes a prompt, converter, syncer, or governance policy wrapper
