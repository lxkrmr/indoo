# ADR 0003: One config path per platform

## Status

Accepted

## Context

`indoo` should be predictable for users and agents. Multiple config locations,
environment-specific search chains, or layered overrides make discovery and
troubleshooting harder.

## Decision

Use one default config path per platform.

Current paths:
- macOS and Linux: `~/.config/indoo/config.toml`
- Windows: `%APPDATA%/indoo/config.toml`

## Consequences

Positive:
- easier setup and troubleshooting
- no guessing where configuration lives
- simpler CLI guidance

Negative:
- less flexibility for users who prefer custom config layouts
