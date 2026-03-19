## odoo-lab

Small `uv`-managed CLI for inspecting Odoo records while developing custom addons.

### Setup

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync
```

Create a project-local `.odoo-lab.toml`:

```toml
[profiles.local]
url = "http://localhost:8069"
db = "odoo"
user = "admin"
password = "admin"
```

### Examples

```bash
uv run odoo-lab show your.model 42 field_x computed_y --profile local
uv run odoo-lab write-and-show your.model 42 field_x computed_y --profile local --value field_x=10
uv run python scripts/example_depends_check.py
```

The CLI reads connection data only from `.odoo-lab.toml` or from a file passed with `--config`.
