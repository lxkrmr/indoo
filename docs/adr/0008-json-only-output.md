# ADR 0008: JSON-only output

## Status

Accepted

## Context

`indoo` is an agent-first CLI. Its primary consumer is an AI agent, not a
human reading a terminal. The tool has supported three output formats:
`json`, `text`, and `ndjson`.

`text` mode required a separate rendering path for every command — roughly
60 lines of formatting logic that needed to be kept in sync with the JSON
output shape. Every new command required two implementations.

`ndjson` mode was partially broken: it checked for an `items` key in the
payload, but the `list` command returns `records`. A list result would be
emitted as a single line rather than one record per line.

Neither `text` nor `ndjson` provided meaningful value for the primary use
case. Agents parse JSON. Humans can read JSON directly or pipe to `jq`.
The global `--output` flag also caused agent confusion: agents would append
`--output json` to subcommands, which failed because `--output` must be
placed before the subcommand name.

## Decision

`indoo` emits JSON only. The `--output` flag is removed entirely.

- `text` mode is removed.
- `ndjson` mode is removed.
- The `OutputFormat` type, the `OutputManager.format` field, and all
  format-branching logic are removed.
- The `default_text` rendering function is removed.
- All `--output` options are removed from the CLI and from `describe` schemas.

Output is always pretty-printed JSON (`indent=2, sort_keys=True`).

## Consequences

Positive:
- no `--output` flag to misplace or misuse
- one output shape per command — no dual maintenance
- simpler `OutputManager`, simpler tests
- no broken `ndjson` path to confuse agents
- agents never need to specify a format

Negative:
- users who preferred `text` for quick terminal reads lose that option
- `ndjson` streaming is no longer available (was broken anyway)
