# ADR 0011: Command names follow Odoo conventions

## Status

Accepted

## Context

`indoo` commands were named after CLI conventions rather than Odoo's own
method names. This created a translation step: a developer who knows Odoo
has to learn a second vocabulary to use `indoo`.

Current names and their Odoo equivalents:
- `list` → `search_read`
- `show` → `read`
- `fields` → `fields_get`

Infrastructure commands (`doctor`, `profile`) have no Odoo equivalent and
are not affected.

## Decision

Rename commands to match Odoo method names:
- `list` → `search`
- `show` → `read`
- `fields` → `fields_get`

Underscores are kept as-is — this is the Odoo convention and `indoo` stays
in that universe.

Infrastructure commands stay unchanged:
- `doctor`
- `profile` (and subcommands)

## Consequences

Positive:
- no translation step for developers who know Odoo
- command names are self-documenting in an Odoo context
- consistent vocabulary across code and CLI

Negative:
- breaking change for existing users of `list`, `show`, and `fields`
