# Security

`agent-instruction-litmus` creates disposable local fixture repositories and scores their artifacts.

## Model And Account Safety

- Live Codex CLI and opencode runs require explicit `--allow-live`.
- Live adapters can consume provider quota and may send fixture prompts to the configured model provider.
- CI does not run live model calls.
- Fixture captures are written under `.litmus/` inside the disposable fixture directory.

## Data Safety

- Fixtures do not read `.env` files, SSH keys, tokens, browser profiles, or unrelated project files.
- Fixtures are intended to run in temporary directories created by this tool.
- Do not point live adapters at a real repository unless you understand the client permissions and output path.

## Reporting Vulnerabilities

Open a GitHub issue with a minimal reproduction that avoids secrets. For sensitive reports, contact the maintainer privately before publishing details.
