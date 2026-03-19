from __future__ import annotations

from typing import Any


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
    "write-and-show": {
        "summary": "Write values to one record and read selected fields again.",
        "arguments": [
            {"name": "model", "type": "string", "required": True},
            {"name": "record_id", "type": "integer", "required": True},
            {"name": "fields", "type": "string[]", "required": True},
        ],
        "options": [
            {"name": "--value", "type": "key=value[]", "required": False, "description": "Write one or more flat assignments."},
            {"name": "--json", "type": "object", "required": False, "description": "Pass the full write payload as JSON."},
            {"name": "--dry-run", "type": "boolean", "required": False, "description": "Validate and preview the write without mutating data."},
            {"name": "--context", "type": "key=value[]", "required": False, "description": "Add Odoo context values."},
            {"name": "--context-json", "type": "object", "required": False, "description": "Pass the full Odoo context as JSON."},
            {"name": "--profile", "type": "string", "required": False, "description": "Override the active profile."},
            {"name": "--output", "type": "json|text|ndjson", "required": False, "description": "Choose the output format."},
        ],
        "examples": [
            "indoo write-and-show sale.order 42 amount_total --value note='debug'",
            "indoo write-and-show sale.order 42 amount_total --json '{\"note\":\"debug\",\"state\":\"draft\"}'",
            "indoo write-and-show sale.order 42 amount_total --json '{\"state\":\"draft\"}' --dry-run",
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
