# Design

## Purpose

This document captures the product and design intent behind `indoo`.
It is not a changelog. It exists to explain why the current shape of the
CLI is the way it is, and to keep a small list of planned ideas that are
worth revisiting later.

## Product Direction

`indoo` is a small, clear, agent-friendly CLI for working with Odoo.

Core principles:
- strict KISS approach
- one obvious workflow over multiple competing paths
- global installation via `uv tool install`
- one default config location per platform
- `indoo doctor` as the main onboarding and recovery command
- CLI-first discoverability for humans and agents
- concise, explicit, stable output

## Implemented Decisions

### Global installation via `uv tool install`

`indoo` is designed to be installed and used globally.

Why:
- the tool should feel like a normal command, not a repo-bound script
- users and agents should be able to rely on `indoo` being on `PATH`
- one recommended install path is simpler than mixing local, editable,
  and package-manager-specific instructions

Current public install path:
- `uv tool install git+https://github.com/lxkrmr/indoo.git`

Development remains separate:
- `uv sync`
- `uv run indoo ...`

This keeps user usage and repository development mentally distinct.

### One config path per platform

`indoo` uses one default config file location per platform.

Why:
- agents should not have to guess where configuration lives
- users should not have to choose between multiple config conventions
- predictable paths make troubleshooting easier

Current paths:
- macOS and Linux: `~/.config/indoo/config.toml`
- Windows: `%APPDATA%/indoo/config.toml`

### Named profiles with one active profile

`indoo` stores named Odoo connection profiles and one active profile.

Why:
- users often work against more than one Odoo instance
- naming profiles is simpler than repeatedly passing full connection
  details on every command
- an active profile keeps the default path short for everyday usage

Implemented commands:
- `indoo profile add`
- `indoo profile list`
- `indoo profile show`
- `indoo profile use`

### `indoo doctor` as the entry point

`indoo doctor` is the main onboarding and recovery command.

Why:
- users and agents need one obvious first command
- setup problems should be diagnosed by the CLI itself
- the tool should suggest the next concrete command instead of only
  reporting failure

Current behavior:
- checks config presence
- checks profile availability
- checks active or selected profile resolution
- checks whether the selected profile can connect
- returns machine-readable output with `next_command` on failure

### Explicit output modes

`indoo` supports `json`, `text`, and `ndjson` output modes.

Why:
- agents need stable structured output
- humans sometimes want a compact text summary
- list-style commands benefit from line-delimited JSON

Current default:
- `json`

This keeps the CLI machine-friendly by default while still allowing quick
interactive usage.

### Focused record inspection and update flow

The current command set focuses on a small, concrete workflow:
- inspect one record
- write values
- inspect the result again

Implemented commands:
- `indoo show`
- `indoo write-and-show`
- `indoo describe`
- `indoo schema`

Why:
- this covers the common addon-development loop without trying to become a
  full Odoo shell
- one narrow workflow is easier to explain and automate
- agents benefit from commands with a tight, explicit contract

### Explicit context and JSON input

`indoo` accepts context values as `KEY=VALUE` pairs or as full JSON.
Write payloads can be passed as assignments or as full JSON objects.

Why:
- simple updates should stay easy to type
- nested or agent-generated payloads need a raw JSON path
- supporting both forms avoids forcing every caller into one awkward input
  style while keeping the command surface small

Implemented options:
- `--context`
- `--context-json`
- `--value`
- `--json`
- `--dry-run`

### Early input validation

`indoo` validates model names, field names, profile names, and JSON input
before attempting the Odoo call.

Why:
- invalid input should fail early and clearly
- agents should get precise, stable failure messages
- this reduces accidental writes and avoidable remote round-trips

### Human URLs, internal protocol mapping

Profiles accept normal Odoo base URLs such as `http://localhost:8069` and
`https://example.com`.

Why:
- users should not need to know library-specific protocol names
- internal transport details belong inside the tool, not in the CLI contract

Current behavior:
- `http://...` maps to `jsonrpc`
- `https://...` maps to `jsonrpc+ssl`

This keeps the user-facing interface natural while preserving compatibility
with `odoorpc`.

### Product-ready repository basics

The repository keeps the public usage path obvious.

Implemented decisions:
- GitHub is the primary install source
- `README.md` is user-facing and install-first
- `LICENSE` is MIT
- `.gitignore` covers common Python and build artifacts
- `AGENTS.md` stays in the repository for transparency

Why:
- the repo should be understandable from GitHub alone
- installation should work directly from the repository URL
- internal working rules should be visible rather than implied

## Planned Ideas

These are ideas worth revisiting. They are not promises.

### `indoo fields`

`indoo` exposes field metadata directly from the CLI.

Implemented command:
- `indoo fields MODEL [FIELD ...]`

Why it matters:
- users and agents should not have to guess field types from convention or
  trial and error
- safe writing becomes much easier when the CLI can reveal whether a field
  is `char`, `text`, `selection`, `many2one`, readonly, or required

Current default output per field:
- `name`
- `type`
- `string`
- `required`
- `readonly`
- optional `relation`
- optional `selection`

This keeps field discovery CLI-first and makes write planning much safer
without turning `indoo` into a general-purpose metadata dump.

### Stronger guidance for write safety

Possible direction:
- use field metadata to warn about readonly fields
- make `--dry-run` even more central in mutating flows
- possibly surface clearer hints when a write targets a risky or unusual
  field

Why:
- `write-and-show` is intentionally simple, but write safety can be improved
  without adding much conceptual weight

### Better help text for fast CLI discovery

Possible direction:
- keep refining `--help` output and subcommand help examples
- ensure the intended workflow is obvious from the CLI alone

Why:
- the CLI should remain self-explanatory for both humans and agents
- good help text is a product feature, not an afterthought

### More metadata-oriented discovery commands

Possible direction:
- model-oriented inspection commands beyond `describe`
- compact commands that reveal model capabilities without requiring trial
  and error

Constraint:
- only add them if they preserve the one-obvious-workflow feeling
- avoid turning `indoo` into a sprawling generic Odoo toolbox

### Release discipline

Possible direction:
- lightweight tags or GitHub releases for known-good milestones
- keep versioning and release notes simple

Why:
- GitHub is the primary install source
- users benefit from recognizable stable points in time

## Non-Goals For Now

These are deliberately out of scope unless the product direction changes.

- becoming a full replacement for Odoo shell access
- exposing every possible Odoo RPC operation
- multiple competing install methods
- multiple config locations or layered config resolution
- a large fallback system for every possible environment
- mirroring all Odoo metadata by default

## Working Rule For Future Changes

Before adding a feature, ask:
- does this reinforce one obvious workflow?
- does this improve CLI-only discoverability?
- does this help agents without adding avoidable complexity?
- does this keep defaults explicit and predictable?

If the answer is no, the feature probably does not belong in `indoo` yet.
