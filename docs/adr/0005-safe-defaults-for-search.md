# ADR 0005: Safe defaults for `indoo search`

## Status

Accepted

## Context

Record discovery is necessary in a CLI-only workflow. At the same time,
accidentally reading too many records should be avoided.

Not all Odoo models share a universal human-readable field like `name`.
However, every real record can be relied on to have `id`.

## Decision

Add `indoo search MODEL [FIELDS...]` with these defaults:
- default fields: `id`
- always include `id` in results
- default `--limit 10`
- default `--offset 0`

No automatic guessing of `name` or other model-specific identity fields.

## Consequences

Positive:
- safe by default
- simple and predictable contract
- works across models without special casing

Negative:
- default output is less friendly than guessing display fields
- callers must request extra fields explicitly
