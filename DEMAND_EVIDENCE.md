# Demand Evidence: agent-instruction-litmus

## Gate Summary

- Value gate: `PASS`.
- Target user: developers, maintainers, and coding-agent client authors who depend on repo instruction files to steer agents.
- Job to be done: verify whether the active agent actually loads and follows project instruction files before trusting it on real work.
- First 5-30 minute outcome: run a disposable fixture and get a report showing whether a specific `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, Copilot, Cursor, or Roo instruction rule was followed, ignored, truncated, or not loaded.
- Repeated public pain: `PASS`.
- Independent sources: `PASS`.
- Current workarounds reviewed: `PASS`.
- Existing tools reviewed: `PASS`.
- Clear standalone gap: `PASS`, narrowly for behavioral instruction-file conformance fixtures, not static linting.
- Upstream-insufficiency: `PASS`, narrowly because the failure class spans multiple clients and modes.
- Credible distribution path: `PASS`, through affected issue threads, coding-agent users, client authors, and harness-quality/tooling communities. No traction claimed.
- Measurable success criteria: `PASS`.
- Build, benchmark, discoverability, private publication, and public publication: `UNKNOWN`.

## Public Pain Signals

- OpenAI Codex issue #6502 reports Codex repeatedly ignoring `AGENTS.md` instructions around TDD and green tests before commit. Source: https://github.com/openai/codex/issues/6502
- OpenAI Codex issue #5804 reports `/review` ignoring `AGENTS.md`, with a simple language-rule reproduction. Source: https://github.com/openai/codex/issues/5804
- OpenAI Codex issue #7878 separately reports `/review` skipping `agents.md`. Source: https://github.com/openai/codex/issues/7878
- OpenAI Codex issue #7347 reports Codex ignoring `agents.md` and becoming hard to use productively. Source: https://github.com/openai/codex/issues/7347
- Anthropic Claude Code issue #7777 reports Claude ignoring instructions in `CLAUDE.md` and agent files, with a repro label. Source: https://github.com/anthropics/claude-code/issues/7777
- Anthropic Claude Code issue #51039 reports Claude ignoring custom instructions from memory and referenced Markdown files, including a "question only, do not modify code" rule. Source: https://github.com/anthropics/claude-code/issues/51039
- Anthropic Claude Code issue #29423 reports Task subagents not loading project `CLAUDE.md` or `.claude/rules`, silently ignoring project configuration. Source: https://github.com/anthropics/claude-code/issues/29423
- Anthropic Claude Code issue #22309 reports `CLAUDE.md` instructions being treated as optional background rather than directives, with a startup-procedure reproduction. Source: https://github.com/anthropics/claude-code/issues/22309
- Anthropic Claude Code issue #34774 reports a `CLAUDE.md` rule forbidding commits being ignored. Source: https://github.com/anthropics/claude-code/issues/34774
- Google Gemini CLI issue #12738 reports a `GEMINI.md` rule not to delete a file being ignored even though the chat claimed the file was loaded. Source: https://github.com/google-gemini/gemini-cli/issues/12738
- Google Gemini CLI issue #17629 reports `GEMINI.md` instructions being ignored after `/clear`. Source: https://github.com/google-gemini/gemini-cli/issues/17629
- Google Gemini CLI issue #16999 refactored `GEMINI.md` loading because flattening global, extension, and project context made conflict resolution ambiguous. Source: https://github.com/google-gemini/gemini-cli/issues/16999
- Roo Code users report `.roo/rules` and `.roorules` custom instructions not appearing in the system prompt or stopping after VS Code restart. Source: https://www.reddit.com/r/RooCode/comments/1l01h5w/roo_keeps_ignoring_my_custom_instructions/
- Roo Code issue #3754 proposes hierarchical file-based mode prompting because custom-instruction loading and priority need clearer structure. Source: https://github.com/RooCodeInc/Roo-Code/issues/3754
- VS Code Copilot documentation includes a troubleshooting section for instruction files not being applied and points users to diagnostics, file locations, glob matching, and settings. Source: https://code.visualstudio.com/docs/agent-customization/custom-instructions
- The AGENTIF benchmark paper finds current models struggle with long, complex agentic instructions and tool specifications. Source: https://arxiv.org/abs/2505.16944
- IFScale measures instruction following degradation as instruction density increases, showing that high-density instruction sets fail in systematic ways. Source: https://arxiv.org/abs/2507.11538
- The "Evaluating AGENTS.md" paper finds repository context files do not generally improve task success and increase inference cost by over 20 percent, while noting that instructions inside context files are generally followed. Source: https://arxiv.org/abs/2602.11988
- "Instruction Adherence in Coding Agent Configuration Files" studies how file-structure variables affect Claude Code adherence, but is limited to a controlled study shape rather than a local cross-client harness. Source: https://arxiv.org/abs/2605.10039

## Current Workarounds

- Manually ask the agent to summarize its loaded instruction files.
- Inspect Codex logs, session JSONL, Gemini `/memory show`, VS Code Copilot diagnostics, or Claude transcripts.
- Add sentinel rules such as "always answer in language X" and test by hand.
- Restart the agent, run `/memory refresh`, clear local config, or repeat the same rule in the prompt.
- Duplicate `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules`, `.roo/rules`, and Copilot instruction files.
- Use static linting or quality scoring for instruction-file content.

## Existing Tools Reviewed

### Codex AGENTS.md Diagnostics

Source: https://developers.openai.com/codex/guides/agents-md

Codex documents loaded-file auditing through TUI logs or session JSONL, discovery troubleshooting, fallback-name checks, truncation settings, and profile confusion. This helps inspect Codex specifically, but it is not a behavior fixture suite and does not cover Claude, Gemini, Roo, or Copilot.

Gate impact: does not eliminate the cross-client behavioral conformance gap.

### Gemini CLI Memory Commands

Source: https://google-gemini.github.io/gemini-cli/docs/cli/commands.html

Gemini exposes `/memory show`, `/memory refresh`, and `/memory list` for `GEMINI.md` instructional context. This is useful diagnostics for one client, but it does not score whether the loaded rules are followed in a task, after `/clear`, or under conflicting scopes.

Gate impact: does not eliminate the fixture-report gap.

### VS Code Copilot Instruction Diagnostics

Source: https://code.visualstudio.com/docs/agent-customization/custom-instructions

VS Code documents `.instructions.md` files, `applyTo` matching, diagnostics, and settings for instruction application. This is useful client-native troubleshooting, but it is not a reusable benchmark across agents or a diff/output-based adherence report.

Gate impact: useful baseline, not a replacement.

### AgentLint

Source: https://github.com/0xmariowu/AgentLint

AgentLint is the strongest adjacent tool. It statically checks agent harness quality across context files, CI, hooks, safety, continuity, and related config, including `AGENTS.md` and `CLAUDE.md`.

This project must not duplicate AgentLint. The only justified gap is behavioral: create fixtures, run the active agent or a recorded/manual adapter, and classify observable adherence failures.

Gate impact: standalone gap remains `PASS` only for behavioral fixtures. Static linting is `FAIL` as a new flagship.

### AGENTIF And IFScale

Sources:

- https://github.com/THU-KEG/AgentIF
- https://arxiv.org/abs/2507.11538

These are instruction-following benchmarks for models or agentic scenarios. They help explain the failure mode, but they do not test a user's installed coding-agent harness for instruction-file discovery, precedence, truncation, slash/review modes, clear/resume, or subagent inheritance.

Gate impact: does not eliminate the local coding-agent harness gap.

### Evaluating AGENTS.md

Source: https://arxiv.org/abs/2602.11988

This paper evaluates whether repository-level context files help coding-agent task success and cost. It is demand evidence that context files need rigorous evaluation, not a ready-to-run conformance suite for a user's local agent.

Gate impact: supports the value gate and baseline design.

## Standalone Gap

The validated standalone gap is narrow:

> a local fixture-based conformance harness that verifies observable coding-agent instruction-file behavior across clients and modes.

It is not a linter, converter, prompt package, governance gateway, or model leaderboard.

## Distribution Path

- Affected Codex, Claude Code, Gemini CLI, Roo Code, and Copilot/VS Code issue threads can use fixture reports as reproducible evidence.
- AgentLint and agents-md linter users are adjacent, but this project must position as behavioral verification, not file-quality scoring.
- Search surfaces: GitHub, package search, coding-agent reliability communities, issue comments, and docs posts around `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, "instructions ignored", "coding agent instruction compliance", and "agent rules not applied".

No users, maintainer interest, downloads, stars, or adoption are claimed.

## Success Criteria

- At least six fixture cases map directly to public pain signals.
- At least two adapter shapes are validated before publication.
- Manual-run mode produces useful output even when an agent cannot be automated safely.
- Reports distinguish discovery failure, truncation, precedence conflict, reset/resume failure, subagent inheritance failure, and model adherence failure where observable.
- A generated Markdown report can be attached to an upstream issue without leaking secrets.

## Kill Or Reposition Criteria

- Kill if the first build is only a static `AGENTS.md`/`CLAUDE.md` linter.
- Kill if no second stable adapter shape is feasible without brittle UI automation.
- Kill if model nondeterminism makes fixture verdicts too noisy to interpret.
- Kill if the only useful output is a Codex, Gemini, Claude, Roo, or VS Code upstream bugfix.
- Route upstream if AgentLint or a client-native diagnostics feature absorbs the behavioral fixture workflow before standalone value is proven.
