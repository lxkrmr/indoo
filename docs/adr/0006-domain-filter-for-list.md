# ADR 0006: Domain filter for `indoo search`

## Status

Accepted

## Context

`indoo search` fetches records without any filter. In practice, users and agents
need to narrow results by field values — for example to find products with a
non-zero price or to exclude specific names. Without filtering, the only
workaround is pagination plus external post-processing.

Odoo's native filter primitive is the domain: a list of triples of the form
`('field', 'operator', value)`. Developers already write domains in Python
code and pass them to `.search()` or `.search_read()`. A separate,
CLI-specific filter syntax would introduce a translation step that adds
friction and breaks copy-paste from code.

Odoo also supports prefix operators (`'|'`, `'&'`) inside a domain list for
composing OR and AND logic. This is the standard mechanism and needs no
separate CLI concept.

## Decision

Add `--domain` to `indoo search`. It accepts a domain in Python list-of-tuples
syntax — exactly as it would be passed to `.search()`:

```
--domain "[('bid_price', '>', 0), ('name', 'not ilike', 'Gold')]"
```

- The outer container is a list `[...]`.
- Each filter condition is a triple `('field', 'operator', value)`.
- Prefix operators (`'|'`, `'&'`) are accepted as plain string elements.
- The value is parsed using Python's `ast.literal_eval` so that Python-style
  tuples and strings are handled without requiring JSON brackets.
- The parsed domain is passed as-is to `search_read`. Odoo validates and
  executes it.
- No alternative `--filter` shortcut is added. One way only.

## Consequences

Positive:
- Developers can copy a domain from Python code and paste it directly.
- Prefix operators for OR/AND are supported without extra CLI concepts.
- No translation step between code and CLI.

Negative:
- `ast.literal_eval` accepts Python literal syntax, not JSON. Users familiar
  with JSON may be surprised that double-quoted strings in tuples also work,
  but single-quoted strings are the natural form.
- Invalid domains are rejected by Odoo at query time, not by indoo up front.
  The error message will be an Odoo RPC error.
