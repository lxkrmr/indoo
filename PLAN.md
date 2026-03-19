# Plan

## Goal

Build `indoo` as a small local CLI that removes Odoo inspection boilerplate during addon development.

## Product Direction

- product name: `indoo`
- strict KISS approach
- one clear workflow over multiple competing paths
- global installation via `uv tool install`
- global config file with named profiles
- `indoo doctor` as the main onboarding and recovery command
- CLI-first discoverability for both humans and agents

## Current Scope

- inspect concrete records
- pass explicit Odoo context values
- write values and read the result again
- keep output easy to share as JSON

## Working Rules

- repository-facing text is English
- conversations with the user may be German
- commit messages are English Conventional Commits with scope
- keep commits small and meaningful
- the agent may commit directly
- the user handles pushing

## Near-Term Priorities

1. Rename the CLI to `indoo`
2. Use one config path per platform
3. Add profile management commands
4. Add `doctor`
5. Keep the README product-ready
