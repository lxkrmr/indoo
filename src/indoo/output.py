from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

import typer

OutputFormat = Literal["json", "text", "ndjson"]


@dataclass(slots=True)
class OutputManager:
    format: OutputFormat = "json"

    def emit(self, payload: dict[str, Any], *, text: str | None = None) -> None:
        if self.format == "text":
            typer.echo(text or default_text(payload))
            return
        if self.format == "ndjson":
            if "items" in payload and isinstance(payload["items"], list):
                for item in payload["items"]:
                    typer.echo(json.dumps(item, sort_keys=True))
                return
            typer.echo(json.dumps(payload, sort_keys=True))
            return
        typer.echo(json.dumps(payload, indent=2, sort_keys=True))


def default_text(payload: dict[str, Any]) -> str:
    if payload.get("ok") is False:
        message = str(payload.get("message", "Command failed."))
        next_command = payload.get("next_command")
        if next_command:
            return f"{message}\nNext: {next_command}"
        return message

    action = payload.get("action")
    if action == "doctor":
        return str(payload.get("message", "Setup looks good."))
    if action == "profile_add":
        return str(payload.get("message", "Profile saved."))
    if action == "profile_use":
        return str(payload.get("message", "Profile activated."))
    if action == "profile_list":
        profiles = payload.get("profiles", [])
        active = payload.get("active_profile")
        lines = [f"Active profile: {active or 'none'}"]
        for profile in profiles:
            marker = "*" if profile["name"] == active else "-"
            lines.append(f"{marker} {profile['name']} {profile['url']} db={profile['db']} user={profile['user']}")
        return "\n".join(lines)
    if action == "profile_show":
        profile = payload.get("profile", {})
        return f"{profile.get('name')}: {profile.get('url')} db={profile.get('db')} user={profile.get('user')}"
    if action == "describe":
        subject = payload.get("subject", "command")
        summary = payload.get("summary", "")
        return f"{subject}: {summary}".strip(": ")
    if action == "show":
        model = payload.get("model")
        record_id = payload.get("id")
        return f"Read {model}#{record_id}"
    if action == "fields":
        model = payload.get("model")
        fields = payload.get("fields", [])
        lines = [str(model)]
        for field in fields:
            parts = [f"- {field['name']}: {field['type']}"]
            if field.get("relation"):
                parts.append(f"-> {field['relation']}")
            flags: list[str] = []
            if field.get("required"):
                flags.append("required")
            if field.get("readonly"):
                flags.append("readonly")
            if field.get("selection"):
                options = ", ".join(item[0] for item in field["selection"])
                flags.append(f"[{options}]")
            if flags:
                parts.append(", ".join(flags))
            lines.append(" ".join(parts))
        return "\n".join(lines)
    if action == "write_and_show":
        model = payload.get("model")
        record_id = payload.get("id")
        if payload.get("dry_run"):
            return f"Validated write for {model}#{record_id}. No changes were applied."
        changed = payload.get("changed", {})
        return f"Updated {model}#{record_id}. Changed fields: {', '.join(changed) or 'none'}"
    return json.dumps(payload, sort_keys=True)
