from __future__ import annotations

from typing import Any


COMMAND_SCHEMAS: dict[str, dict[str, Any]] = {
    "doctor": {
        "summary": "Check config, resolve the active profile, and test Odoo connectivity.",
        "arguments": [],
        "options": [
            {"name": "--profile", "type": "string", "required": False, "description": "Override the active profile."},
        ],
        "examples": ["indoo doctor", "indoo doctor --profile staging"],
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
            {"name": "--domain", "type": "string", "required": False, "description": "Odoo domain filter as a Python list of triples. Example: \"[('purchase_method', '=', 'purchase')]\""},
            {"name": "--profile", "type": "string", "required": False, "description": "Override the active profile."},
            {"name": "--context", "type": "key=value[]", "required": False, "description": "Add Odoo context values."},
            {"name": "--context-json", "type": "object", "required": False, "description": "Pass the full Odoo context as JSON."},
        ],
        "examples": [
            "indoo list res.partner",
            "indoo list res.partner name email --limit 20",
            "indoo list stock.picking name --limit 10 --offset 10",
            "indoo list product.template name --domain \"[('purchase_method', '=', 'purchase')]\"",
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
        ],
        "examples": [
            "indoo fields purchase.order",
            "indoo fields purchase.order name notes state",
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
        "options": [],
        "examples": ["indoo profile list"],
    },
    "profile show": {
        "summary": "Show the active profile or a specific profile.",
        "arguments": [],
        "options": [
            {"name": "--profile", "type": "string", "required": False, "description": "Override the active profile."},
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
        ],
        "examples": ["indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin"],
    },
    "profile use": {
        "summary": "Set the active profile.",
        "arguments": [{"name": "name", "type": "string", "required": True}],
        "options": [],
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
