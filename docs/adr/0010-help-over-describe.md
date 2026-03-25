# ADR 0010: Use --help for discovery, remove describe command

## Status

Accepted

## Context

`indoo` had a `describe` command (and a `schema` alias) that returned
machine-readable JSON schemas for each command. The intent was to give agents
a structured discovery path.

In practice, `describe` was a manually maintained copy of the CLI in
`schema.py`. It drifted from the real implementation — the `--domain` option
was missing from `describe list` while being present in the actual CLI. An
agent relying on `describe` for discovery would get incomplete information.

`--help` output is generated directly from the CLI definition and can never
drift. LLM agents read plain text without difficulty. The structured JSON
output of `describe` provided no meaningful advantage over `--help` while
adding a maintenance burden and a source of subtle bugs.

## Decision

Remove the `describe` command and the `schema` alias. Remove `schema.py`.

`--help` is the single discovery mechanism for both humans and agents:

- `indoo --help` describes the tool and lists all commands
- `indoo COMMAND --help` describes a specific command

The top-level `indoo --help` text is the primary entry point. It must clearly
communicate what `indoo` is, what commands are available, and how to get
started.

## Consequences

Positive:
- one discovery path, always accurate
- no manually maintained schema to drift
- less code to maintain and test
- agents get the same information as humans

Negative:
- no structured JSON schema for command signatures
- agents must parse help text rather than a typed object
