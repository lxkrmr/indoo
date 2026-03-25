# ADR 0007: Error messages must include a correct usage example

## Status

Accepted

## Context

When a user or agent passes invalid input, the error message alone is often
not enough to recover. Knowing what went wrong does not automatically tell you
what the correct form is. This is especially true for CLI arguments where the
accepted syntax is not obvious from the option name.

A user who passes `id,name` as a field argument gets told the input is invalid,
but has no immediate hint that space-separated is the expected format.

## Decision

Every error message for invalid user input must include a concrete example of
the correct form. The example should be a real, runnable command or value — not
a description of the format.

Example for an invalid field name:

> Invalid field name: 'id,name'. Use space-separated field names,
> for example: indoo search res.partner id name email

This applies to all validation errors across the CLI, not just field names.

## Consequences

Positive:
- faster self-correction for users and agents
- no need to consult documentation or help text after an error
- consistent recovery UX across all commands

Negative:
- error messages become slightly longer
- examples must be kept accurate when commands change
