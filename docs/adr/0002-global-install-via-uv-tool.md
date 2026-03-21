# ADR 0002: Global installation via `uv tool install`

## Status

Accepted

## Context

`indoo` should feel like a normal command for both humans and agents.
A repo-local or editable-only workflow makes usage and testing less realistic.

## Decision

Recommend one installation path:

```bash
uv tool install git+https://github.com/lxkrmr/indoo.git
```

Use the globally installed `indoo` command as the default usage and testing
path.

## Consequences

Positive:
- the real user workflow stays front and center
- the command is expected on `PATH`
- testing naturally reflects the delivered tool

Negative:
- repository changes are not visible in the global install until refresh or
  reinstall
- contributors must remember when they are testing repo code versus installed
  code
