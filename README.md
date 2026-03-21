# indoo

`indoo` is a small, agent-friendly CLI for working with Odoo over RPC.

If you are unsure where to start, run:

```bash
indoo doctor
```

## Install

Use one installation path:

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

4. List records with a safe default limit:

```bash
indoo list res.partner
indoo list res.partner name email --limit 20
```

5. Read one record:

```bash
indoo show res.partner 1 name email
```

6. Inspect fields before writing:

```bash
indoo fields res.partner name email
```

7. Update one record:

```bash
indoo write res.partner 1 name --value name="New Name" --dry-run
indoo write res.partner 1 name --value name="New Name"
```

8. Create one record:

```bash
indoo create res.partner name --value name="Acme"
```

9. Discover command shapes from the CLI itself:

```bash
indoo describe
indoo describe write
indoo describe list
```

## Notes

- `indoo` is designed to be installed and used globally.
- The primary onboarding and recovery command is `indoo doctor`.
- Use `indoo --help` and subcommand help for the intended workflow.
