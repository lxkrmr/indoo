## odoo-lab

Small `uv`-managed CLI for inspecting Odoo records while developing custom addons.

### Setup

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync
```

Configure the connection via environment variables:

```bash
export ODOO_URL=http://localhost:8069
export ODOO_DB=odoo
export ODOO_USER=admin
export ODOO_PASSWORD=admin
```

### Examples

```bash
uv run odoo-lab show your.model 42 field_x computed_y
uv run odoo-lab write-and-show your.model 42 field_x computed_y --value field_x=10
uv run python scripts/example_depends_check.py
```
