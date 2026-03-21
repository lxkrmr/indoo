from __future__ import annotations

from typing import Any


RELATIONAL_COMMAND_SCHEMA = {
    "type": "object[]",
    "description": "Relational operations for one2many and many2many fields.",
    "items": {
        "op": "create|update|delete|unlink|link|clear|set",
        "create": {"values": "object"},
        "update": {"id": "integer", "values": "object"},
        "delete": {"id": "integer"},
        "unlink": {"id": "integer"},
        "link": {"id": "integer"},
        "clear": {},
        "set": {"ids": "integer[]"},
    },
}


COMMAND_SCHEMAS: dict[str, dict[str, Any]] = {
    "doctor": {
        "summary": "Check config, resolve the active profile, and test Odoo connectivity.",
        "arguments": [],
        "options": [
            {"name": "--profile", "type": "string", "required": False, "description": "Override the active profile."},
            {"name": "--output", "type": "json|text|ndjson", "required": False, "description": "Choose the output format."},
        ],
        "examples": ["indoo doctor", "indoo doctor --profile staging --output json"],
    },
    "list": {
        "summary": "List records for one Odoo model with a safe default limit.",
        "arguments": [
            {"name": "model", "type": "string", "required": True},
            {"name": "fields", "type": "string[]", "required": False},
        ],
        "options": [
            {"name": "--limit", "type": "integer", "required": False, "description": "Maximum number of records to return. Defaults to 10."},
            {"name": "--offset", "type": "integer", "required": False, "description": "Number of records to skip before listing results."},
            {"name": "--profile", "type": "string", "required": False, "description": "Override the active profile."},
            {"name": "--context", "type": "key=value[]", "required": False, "description": "Add Odoo context values."},
            {"name": "--context-json", "type": "object", "required": False, "description": "Pass the full Odoo context as JSON."},
            {"name": "--output", "type": "json|text|ndjson", "required": False, "description": "Choose the output format."},
        ],
        "examples": [
            "indoo list res.partner",
            "indoo list res.partner name email --limit 20",
            "indoo list stock.picking name --limit 10 --offset 10",
        ],
    },
    "show": {
        "summary": "Read selected fields from one Odoo record.",
        "arguments": [
            {"name": "model", "type": "string", "required": True},
            {"name": "record_id", "type": "integer", "required": True},
            {"name": "fields", "type": "string[]", "required": True},
        ],
        "options": [
            {"name": "--profile", "type": "string", "required": False, "description": "Override the active profile."},
            {"name": "--context", "type": "key=value[]", "required": False, "description": "Add Odoo context values."},
            {"name": "--context-json", "type": "object", "required": False, "description": "Pass the full Odoo context as JSON."},
            {"name": "--output", "type": "json|text|ndjson", "required": False, "description": "Choose the output format."},
        ],
        "examples": [
            "indoo show sale.order 42 name amount_total",
            "indoo show sale.order 42 name --context-json '{\"lang\":\"de_DE\"}'",
        ],
    },
    "fields": {
        "summary": "Describe model fields and their basic metadata.",
        "arguments": [
            {"name": "model", "type": "string", "required": True},
            {"name": "fields", "type": "string[]", "required": False},
        ],
        "options": [
            {"name": "--profile", "type": "string", "required": False, "description": "Override the active profile."},
            {"name": "--output", "type": "json|text|ndjson", "required": False, "description": "Choose the output format."},
        ],
        "examples": [
            "indoo fields purchase.order",
            "indoo fields purchase.order name notes state",
        ],
    },
    "write": {
        "summary": "Write values to one record and confirm the resulting field values.",
        "arguments": [
            {"name": "model", "type": "string", "required": True},
            {"name": "record_id", "type": "integer", "required": True},
            {"name": "fields", "type": "string[]", "required": False, "description": "Fields to read back after the write. Defaults to top-level payload keys."},
        ],
        "options": [
            {"name": "--value", "type": "key=value[]", "required": False, "description": "Write one or more flat assignments."},
            {"name": "--json", "type": "object", "required": False, "description": "Pass the full write payload as JSON. Use this for relational operations too."},
            {"name": "--dry-run", "type": "boolean", "required": False, "description": "Validate and preview the write without mutating data."},
            {"name": "--context", "type": "key=value[]", "required": False, "description": "Add Odoo context values."},
            {"name": "--context-json", "type": "object", "required": False, "description": "Pass the full Odoo context as JSON."},
            {"name": "--profile", "type": "string", "required": False, "description": "Override the active profile."},
            {"name": "--output", "type": "json|text|ndjson", "required": False, "description": "Choose the output format."},
        ],
        "payload_notes": {
            "simple_assignments": "Use --value for flat scalar or JSON values.",
            "relational_json": RELATIONAL_COMMAND_SCHEMA,
        },
        "examples": [
            "indoo write sale.order 42 state --value state='sale'",
            "indoo write sale.order 42 amount_total state --json '{\"state\":\"draft\"}'",
            "indoo write sale.order 42 --json '{\"tag_ids\":[{\"op\":\"set\",\"ids\":[1,2,3]}]}'",
        ],
    },
    "create": {
        "summary": "Create one record and confirm the resulting field values.",
        "arguments": [
            {"name": "model", "type": "string", "required": True},
            {"name": "fields", "type": "string[]", "required": False, "description": "Fields to read back after create. Defaults to top-level payload keys."},
        ],
        "options": [
            {"name": "--value", "type": "key=value[]", "required": False, "description": "Set one or more flat assignments."},
            {"name": "--json", "type": "object", "required": False, "description": "Pass the full create payload as JSON. Use this for relational operations too."},
            {"name": "--dry-run", "type": "boolean", "required": False, "description": "Validate and preview the create without mutating data."},
            {"name": "--context", "type": "key=value[]", "required": False, "description": "Add Odoo context values."},
            {"name": "--context-json", "type": "object", "required": False, "description": "Pass the full Odoo context as JSON."},
            {"name": "--profile", "type": "string", "required": False, "description": "Override the active profile."},
            {"name": "--output", "type": "json|text|ndjson", "required": False, "description": "Choose the output format."},
        ],
        "payload_notes": {
            "simple_assignments": "Use --value for flat scalar or JSON values.",
            "relational_json": RELATIONAL_COMMAND_SCHEMA,
        },
        "examples": [
            "indoo create res.partner name --value name='Acme'",
            "indoo create sale.order --json '{\"partner_id\":7,\"order_line\":[{\"op\":\"create\",\"values\":{\"name\":\"Line A\"}}]}'",
            "indoo create sale.order state --json '{\"partner_id\":7,\"state\":\"draft\"}' --dry-run",
        ],
    },
    "profile": {
        "summary": "Manage named Odoo connection profiles.",
        "arguments": [],
        "options": [],
        "examples": ["indoo profile list", "indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin"],
    },
    "profile list": {
        "summary": "List all saved profiles.",
        "arguments": [],
        "options": [
            {"name": "--output", "type": "json|text|ndjson", "required": False, "description": "Choose the output format."},
        ],
        "examples": ["indoo profile list", "indoo profile list --output ndjson"],
    },
    "profile show": {
        "summary": "Show the active profile or a specific profile.",
        "arguments": [],
        "options": [
            {"name": "--profile", "type": "string", "required": False, "description": "Override the active profile."},
            {"name": "--output", "type": "json|text|ndjson", "required": False, "description": "Choose the output format."},
        ],
        "examples": ["indoo profile show", "indoo profile show --profile staging"],
    },
    "profile add": {
        "summary": "Create or update a profile and make it active.",
        "arguments": [{"name": "name", "type": "string", "required": True}],
        "options": [
            {"name": "--url", "type": "string", "required": True},
            {"name": "--db", "type": "string", "required": True},
            {"name": "--user", "type": "string", "required": True},
            {"name": "--password", "type": "string", "required": True},
            {"name": "--output", "type": "json|text|ndjson", "required": False, "description": "Choose the output format."},
        ],
        "examples": ["indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin"],
    },
    "profile use": {
        "summary": "Set the active profile.",
        "arguments": [{"name": "name", "type": "string", "required": True}],
        "options": [
            {"name": "--output", "type": "json|text|ndjson", "required": False, "description": "Choose the output format."},
        ],
        "examples": ["indoo profile use local"],
    },
}


def describe_subject(subject: str | None = None) -> dict[str, Any]:
    if not subject:
        return {
            "subject": "commands",
            "summary": "Available commands in indoo.",
            "commands": sorted(COMMAND_SCHEMAS),
        }

    normalized = subject.strip().lower()
    if normalized not in COMMAND_SCHEMAS:
        available = ", ".join(sorted(COMMAND_SCHEMAS))
        raise KeyError(f"Unknown subject {subject!r}. Available subjects: {available}.")

    return {
        "subject": normalized,
        **COMMAND_SCHEMAS[normalized],
    }
