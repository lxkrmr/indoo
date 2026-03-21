# indoo

`indoo` is a small, agent-friendly CLI for inspecting and updating Odoo
records.

If you are unsure where to start, run `indoo doctor` first.

The product follows a strict KISS approach:
- one recommended installation method
- one default config location
- one obvious setup flow
- explicit output modes for humans and agents
- explicit next-step guidance when something fails

## Install

Use `uv tool install` as the default installation method.
This keeps the install path easy to remember across machines.

Install from GitHub over HTTPS:

```bash
uv tool install git+https://github.com/lxkrmr/indoo.git
```

Or install from GitHub over SSH:

```bash
uv tool install git+ssh://git@github.com/lxkrmr/indoo.git
```

After installation, the `indoo` command is available globally.
That makes it easy to call from both terminals and agents.

To refresh an existing installation from GitHub:

```bash
uv tool install --reinstall git+https://github.com/lxkrmr/indoo.git
```

## Configuration

`indoo` uses one default config file per platform:
- macOS and Linux: `~/.config/indoo/config.toml`
- Windows: `%APPDATA%/indoo/config.toml`

The config file stores an active profile and one or more named Odoo profiles.

Example:

```toml
active_profile = "local"

[profiles.local]
url = "http://localhost:8069"
db = "odoo"
user = "admin"
password = "admin"
```

## Quickstart

1. Install the tool:

```bash
uv tool install git+https://github.com/lxkrmr/indoo.git
```

2. Check the current setup:

```bash
indoo doctor
```

3. Create a profile:

```bash
indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin
```

4. Verify the setup again:

```bash
indoo doctor
```

5. Read a record:

```bash
indoo show res.partner 1 name email
```

6. Inspect field metadata before writing:

```bash
indoo fields res.partner name email
```

7. Update a record and inspect the result:

```bash
indoo write res.partner 1 name --value name="New Name"
```

8. Create a record:

```bash
indoo create res.partner name --value name="Acme"
```

9. Discover the command shape at runtime:

```bash
indoo describe write
indoo describe create
```

## Commands

### `indoo doctor`

Checks whether:
- the config file exists
- profiles are configured
- an active profile is available
- the selected profile can connect to Odoo

If a check fails, `indoo doctor` returns JSON with a concrete `next_command`.

### `indoo profile add`

Create or update a profile and make it active.

```bash
indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin
```

### `indoo profile list`

List saved profiles.

```bash
indoo profile list
indoo --output ndjson profile list
```

### `indoo profile show`

Show the active profile or a specific profile.

```bash
indoo profile show
indoo profile show --profile local
```

### `indoo profile use`

Switch the active profile.

```bash
indoo profile use staging
```

### `indoo show`

Read selected fields from one record.

```bash
indoo show sale.order 42 name amount_total state
```

You can pass context values in `KEY=VALUE` form:

```bash
indoo show sale.order 42 amount_total --context lang="de_DE"
```

Or pass the full context as JSON:

```bash
indoo show sale.order 42 amount_total --context-json '{"lang":"de_DE"}'
```

### `indoo fields`

Describe model fields and their basic metadata.

```bash
indoo fields purchase.order
indoo fields purchase.order name notes state
```

Use this to discover field types before writing data.

### `indoo write`

Write values and read back selected fields.

```bash
indoo write sale.order 42 amount_total --value note="debug run"
```

For agent-generated, nested, or relational payloads, use raw JSON:

```bash
indoo write sale.order 42 amount_total state --json '{"note":"debug run","state":"draft"}'
```

Relational fields accept Odoo-style operations through a small JSON contract:

```bash
indoo write sale.order 42 --json '{
  "tag_ids": [
    {"op": "set", "ids": [1, 2, 3]}
  ],
  "order_line": [
    {"op": "create", "values": {"name": "Line A"}},
    {"op": "update", "id": 10, "values": {"name": "Updated"}},
    {"op": "unlink", "id": 11}
  ]
}'
```

Supported relational operations:
- `create`
- `update`
- `delete`
- `unlink`
- `link`
- `clear`
- `set`

If you do not pass explicit read-back fields, `indoo write` reads back the
payload's top-level field names.

For all mutating commands, prefer `--dry-run` first:

```bash
indoo write sale.order 42 amount_total state --json '{"state":"draft"}' --dry-run
```

### `indoo create`

Create one record and read back selected fields.

```bash
indoo create res.partner name --value name="Acme"
```

You can also create nested relational data with JSON:

```bash
indoo create sale.order --json '{
  "partner_id": 7,
  "order_line": [
    {"op": "create", "values": {"name": "Line A"}}
  ]
}'
```

If you do not pass explicit read-back fields, `indoo create` reads back the
payload's top-level field names.

### `indoo describe` and `indoo schema`

Describe commands as machine-readable JSON at runtime.

```bash
indoo describe
indoo describe write
indoo describe create
indoo schema doctor
```

## Output

`indoo` supports explicit output modes:
- `--output json` for structured machine-readable output
- `--output text` for compact human-readable summaries
- `--output ndjson` for line-delimited JSON on list-style results

JSON remains the default.

Example:

```json
{
  "action": "doctor",
  "checked_profile": "local",
  "config_path": "/Users/me/.config/indoo/config.toml",
  "message": "Profile 'local' is ready to use.",
  "next_command": "indoo show res.partner 1 name --profile local",
  "ok": true
}
```

NDJSON is especially useful for commands that return multiple items:

```bash
indoo --output ndjson profile list
```

Text output is useful for quick interactive checks:

```bash
indoo --output text doctor
```

## Input Rules

`indoo` is designed to be safe for agent-generated input:
- model names and field names are validated
- profile names are validated
- control characters are rejected
- `write --json`, `create --json`, and `--context-json` require JSON objects
- relational operations are only accepted through `--json`
- mutating commands support `--dry-run` so writes can be validated before
  execution

If input is invalid, `indoo` fails early with a concrete error message.

## Troubleshooting

If no config file exists, start here:

```bash
indoo doctor
indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin
indoo doctor
```

If the active profile fails but other profiles exist, run:

```bash
indoo profile list
indoo profile use <name>
indoo doctor
```

## Development

For local development in this repository:

```bash
uv sync
```

Run the CLI from the working tree:

```bash
uv run indoo --help
```

Run tests:

```bash
uv run python -m unittest discover -s tests -v
```
