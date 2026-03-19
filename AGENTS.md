# AGENTS

## Purpose
- Build `indoo` as a small, clear, agent-friendly CLI for working with Odoo.
- Optimize for a single obvious workflow instead of multiple competing paths.

## Language Rules
- All repository-facing text must be in English.
- This includes documentation, README content, CLI help text, code comments, and commit messages.
- Conversations with the user may be in German.

## Product Rules
- The product name is `indoo`.
- Follow a strict KISS approach.
- Prefer one clear way over multiple options.
- Avoid fallback systems unless they are truly necessary.
- Make defaults obvious and predictable.

## Installation
- Recommend `uv tool install` as the default installation method.
- Design the tool so it can be installed and used globally.

## Configuration
- Use one default config location per platform.
- macOS and Linux: `~/.config/indoo/config.toml`
- Windows: `%APPDATA%/indoo/config.toml`

## CLI UX
- The primary onboarding and recovery command is `indoo doctor`.
- Help text must be sufficient to understand the workflow without reading Markdown files.
- Errors must explain what failed and suggest the next concrete command.
- Output should be concise, explicit, and stable.
- Prefer machine-friendly output where useful.

## Agent Friendliness
- An agent must be able to discover and use `indoo` through the CLI alone.
- Do not assume access to README files, plans, or other Markdown documents.
- `indoo --help` and subcommand help must expose the intended workflow clearly.
- Commands should guide the user or agent toward the next step instead of failing silently.

## Commits
- Use Conventional Commits with scope.
- Format: `type(scope): short description`
- Keep commits small and meaningful.
- Commit messages must be in English.
- The agent may commit directly in this repository.
- Do not push unless the user explicitly asks for it.
