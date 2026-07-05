# Discoverability: agent-instruction-litmus

Date: 2026-07-05 13:19 Europe/Amsterdam.

Status: `PASS` for private release-candidate readiness.

## Target Search Intent

Target users:

- developers debugging coding agents that ignore repository instructions
- agent-tool authors testing instruction-file loading and scope behavior
- maintainers filing upstream issues for `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, review mode, or custom-instruction failures

Natural search phrases:

- `Codex ignores AGENTS.md`
- `Claude Code ignores CLAUDE.md`
- `Gemini CLI ignores GEMINI.md`
- `coding agent custom instructions not applied`
- `AGENTS.md conformance test`
- `agent instruction file fixture`
- `nested AGENTS.md precedence`

## Artifact Review

- README title: `agent-instruction-litmus`; acceptable package/repository name, but release title should add the category phrase.
- README first paragraph: states the exact problem, target users, instruction-file formats, and observable output/diff behavior.
- Quickstart: includes manual, Codex CLI, and opencode paths.
- Fixtures section: names root `AGENTS.md`, review-mode, and nested-scope behavior.
- Package metadata: includes `agents-md`, `claude-md`, `gemini-md`, `coding-agent`, `instruction-following`, `conformance`, and `developer-tools`.
- Limitations: documents nondeterminism, unsupported clients, quota risk, and the narrow meaning of a pass.
- Private GitHub repository metadata: `itscloud0/agent-instruction-litmus` is private with an accurate description and topics.

## Proposed Repository Metadata

Description:

`Behavior fixtures for testing whether coding agents follow AGENTS.md and other instruction files.`

Topics:

- `agents-md`
- `claude-md`
- `gemini-md`
- `coding-agent`
- `instruction-following`
- `conformance`
- `developer-tools`
- `codex-cli`
- `opencode`
- `testing`

Release title:

`agent-instruction-litmus v0.1.0 - behavior fixtures for coding-agent instruction files`

## Distribution Plan

- GitHub repository search through accurate README, description, and topics.
- Python package search through package name, description, and keywords if packaging is later approved.
- Issue-thread references only where the project directly reproduces a relevant behavior class; do not imply maintainers requested this project.
- Adjacent users of AgentLint, agents.md, Codex CLI, Claude Code, Gemini CLI, and opencode who need behavior fixtures rather than static linting.

## Gate Status

- README and package metadata: `PASS`.
- GitHub repository description/topics: `PASS`; verified on the private repository.
- Release title/notes: `PASS` for the planned release title and `RELEASE_NOTES.md`; no public release exists yet.
- Distribution plan: `PASS` as a concrete plan without fabricated adoption.
- Overall discoverability gate: `PASS` for private publication. Public publication still requires final CI, public visibility, and release creation.
