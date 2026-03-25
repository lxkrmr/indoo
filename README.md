# indoo

`indoo` is a small, read-only CLI for inspecting Odoo data over RPC.

It helps developers understand what is in Odoo without mutating it.
The CLI is the primary interface for both humans and agents.
Point the agent to `indoo --help`, not to this README.

## Install

```bash
uv tool install git+https://github.com/lxkrmr/indoo.git
```

To refresh an existing global installation:

```bash
uv tool install --reinstall git+https://github.com/lxkrmr/indoo.git
```

## Quickstart

1. Check the current setup:

```bash
indoo doctor
```

2. Create a profile:

```bash
indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin
```

3. Verify the setup again:

```bash
indoo doctor
```

4. Explore a model's fields:

```bash
indoo fields_get res.partner
indoo fields_get res.partner name email
```

5. Search for records:

```bash
indoo search res.partner
indoo search res.partner name email --limit 20
indoo search res.partner name --domain "[('customer_rank', '>', 0)]"
```

6. Read one record:

```bash
indoo read res.partner 1 name email
```

## Discovery

Use the CLI itself to learn the workflow:

```bash
indoo --help
indoo search --help
indoo read --help
indoo fields_get --help
```

All output is JSON.
