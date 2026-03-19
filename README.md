# indoo

`indoo` is a small, agent-friendly CLI for inspecting and updating Odoo records.

The product follows a strict KISS approach:
- one recommended installation method
- one default config location
- one obvious setup flow
- explicit output modes for humans and agents
- explicit next-step guidance when something fails

## Install

Use `uv tool install` as the default installation method.

For local development in this repository:

```bash
uv tool install .
```

After installation, the `indoo` command is available globally.

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
uv tool install .
```

2. Create a profile:

```bash
indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin
```

3. Verify the setup:

```bash
indoo doctor
```

4. Read a record:

```bash
indoo show res.partner 1 name email
```

5. Update a record and inspect the result:

```bash
indoo write-and-show res.partner 1 name --value name=\"New Name\"
```

6. Discover the command shape at runtime:

```bash
indoo describe write-and-show
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
indoo show sale.order 42 amount_total --context lang=\"de_DE\"
```

Or pass the full context as JSON:

```bash
indoo show sale.order 42 amount_total --context-json '{"lang":"de_DE"}'
```

### `indoo write-and-show`

Write values and read the record again to inspect changes.

```bash
indoo write-and-show sale.order 42 amount_total --value note=\"debug run\"
```

For agent-generated or nested payloads, use raw JSON:

```bash
indoo write-and-show sale.order 42 amount_total state --json '{"note":"debug run","state":"draft"}'
```

### `indoo describe` and `indoo schema`

Describe commands as machine-readable JSON at runtime.

```bash
indoo describe
indoo describe write-and-show
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
- `write-and-show --json` and `--context-json` require JSON objects

If input is invalid, `indoo` fails early with a concrete error message.

## Troubleshooting

If no config file exists, start here:

```bash
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

Install dependencies:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync
```

Run tests:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest discover -s tests -v
```
