# ADR 0009: indoo is an inspection tool

## Status

Accepted

## Context

`indoo` was built as a CLI to inspect Odoo data. Over time, mutation commands
(`write`, `create`) were added. While technically functional, they create a
problematic dynamic: a separate path to change Odoo data that bypasses the
UI and the ORM-level business logic that the UI exercises.

The goal of Odoo development is to make things accessible and configurable
through the UI. `indoo` exists to give developers better insight during that
process — to verify what is happening, not to make changes happen.

Mutation commands also carry risk. A wrong `write` or `create` produces data
that may go unnoticed until it surfaces in the UI. Unlike a bad read, a bad
write cannot be trivially ignored.

## Decision

`indoo` is an inspection tool. Mutation commands are out of scope until a
concrete use case justifies an exception.

The following commands are removed:
- `write`
- `create`

The following will not be added without a concrete justification:
- `unlink`
- `indoo call` or any other general mutation primitive

If a developer needs to mutate Odoo data, the right path is through the UI
or through tested application code — not through `indoo`.

## Consequences

Positive:
- clear, focused scope
- no risk of accidental data mutation via `indoo`
- enforces the principle that Odoo data should be manageable through the UI
- smaller surface area to maintain and test

Negative:
- existing users of `write` and `create` lose those commands
- some debugging workflows may require a separate tool for mutations
