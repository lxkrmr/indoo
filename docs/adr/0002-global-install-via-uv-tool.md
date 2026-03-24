# ADR 0002: Global installation via `uv tool install`

## Status

Accepted

## Context

`indoo` should feel like a normal command for both humans and agents.
A repo-local or editable-only workflow makes usage and testing less realistic.

## Decision

One installation path:

```bash
uv tool install git+https://github.com/lxkrmr/indoo.git
```

Use the globally installed `indoo` command as the default usage and testing
path.

To pick up changes after development: push first, then reinstall from the
remote URL. Never install from a local path.

```bash
# correct
uv tool install --reinstall git+https://github.com/lxkrmr/indoo.git

# not allowed
uv tool install --reinstall /path/to/local/indoo
```

Local path installs bypass the real delivery chain and break the
"eat your own dog food" principle.

## Consequences

Positive:
- the real user workflow stays front and center
- the command is expected on `PATH`
- testing naturally reflects the delivered tool
- no gap between what is tested locally and what users install

Negative:
- repository changes are not visible in the global install until pushed
  and reinstalled
- contributors must push before they can smoke-test the installed command
