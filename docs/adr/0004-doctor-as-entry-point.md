# ADR 0004: `indoo doctor` as the entry point

## Status

Accepted

## Context

Users and agents need one obvious first command for onboarding and recovery.
Without that, setup failures turn into guesswork and external documentation
becomes too important.

## Decision

`indoo doctor` is the primary onboarding and recovery command.

It should check the local setup, verify profile resolution, test connectivity,
and suggest the next concrete command when something fails.

## Consequences

Positive:
- one clear starting point
- better CLI-only discoverability
- recovery steps can be suggested directly by the tool

Negative:
- `doctor` carries a lot of first-impression responsibility
- its output must stay stable and clear
