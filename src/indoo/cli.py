from __future__ import annotations

import json
from typing import Annotated, Any

import typer

from .client import OdooConnection, parse_assignments, parse_context
from .config import ConnectionProfile, IndoConfig, default_config_path

app = typer.Typer(
    help="Indoo is a small CLI for inspecting and updating Odoo records.",
    no_args_is_help=True,
)
profile_app = typer.Typer(help="Manage Odoo connection profiles.", no_args_is_help=True)
app.add_typer(profile_app, name="profile")


def emit(payload: dict[str, Any]) -> None:
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


def connect(profile_name: str | None, context_items: list[str]) -> OdooConnection:
    config = IndoConfig.load()
    resolved_name, profile = config.resolve_profile(profile_name)
    context = parse_context(context_items) if context_items else {}
    return OdooConnection.connect(resolved_name, profile, context=context)


def fail(message: str, *, details: dict[str, Any] | None = None, code: int = 1) -> None:
    payload: dict[str, Any] = {"ok": False, "message": message}
    if details:
        payload.update(details)
    emit(payload)
    raise typer.Exit(code=code)


ContextOption = Annotated[
    list[str],
    typer.Option(
        "--context",
        "-c",
        help="Context entry in KEY=VALUE form. VALUE can be JSON.",
    ),
]

FieldArgument = Annotated[
    list[str],
    typer.Argument(help="Fields to read from the record."),
]

ValueOption = Annotated[
    list[str],
    typer.Option(
        "--value",
        "-v",
        help="Value assignment in KEY=VALUE form. VALUE can be JSON.",
    ),
]

ProfileOption = Annotated[
    str | None,
    typer.Option(
        "--profile",
        "-p",
        help="Profile name. Defaults to the active profile.",
    ),
]


@app.command("show")
def show_record(
    model: Annotated[str, typer.Argument(help="Technical model name, for example sale.order.")],
    record_id: Annotated[int, typer.Argument(help="Record ID to inspect.")],
    fields: FieldArgument,
    profile: ProfileOption = None,
    context_items: ContextOption = [],
) -> None:
    """Read selected fields from a single record."""
    if not fields:
        fail("Provide at least one field to inspect.")

    try:
        connection = connect(profile, context_items)
        record = connection.record(model, record_id)
        emit(
            {
                "ok": True,
                "action": "show",
                "model": model,
                "id": record_id,
                "profile": connection.profile_name,
                "fields": fields,
                "context": connection.context,
                "record": record.read(fields),
            }
        )
    except Exception as exc:
        fail(str(exc), details={"action": "show", "model": model, "id": record_id})


@app.command("write-and-show")
def write_and_show_record(
    model: Annotated[str, typer.Argument(help="Technical model name, for example sale.order.")],
    record_id: Annotated[int, typer.Argument(help="Record ID to update.")],
    fields: FieldArgument,
    values: ValueOption,
    profile: ProfileOption = None,
    context_items: ContextOption = [],
) -> None:
    """Write values and read the record again to inspect changes."""
    if not fields:
        fail("Provide at least one field to inspect.")
    if not values:
        fail("Provide at least one value assignment with --value.")

    try:
        connection = connect(profile, context_items)
        record = connection.record(model, record_id)
        parsed_values = parse_assignments(values)
        before = record.read(fields)
        record.write(parsed_values)
        after = record.read(fields)

        changed = {
            field: {"before": before.get(field), "after": after.get(field)}
            for field in fields
            if before.get(field) != after.get(field)
        }

        emit(
            {
                "ok": True,
                "action": "write_and_show",
                "model": model,
                "id": record_id,
                "profile": connection.profile_name,
                "context": connection.context,
                "write": parsed_values,
                "fields": fields,
                "before": before,
                "after": after,
                "changed": changed,
            }
        )
    except Exception as exc:
        fail(str(exc), details={"action": "write_and_show", "model": model, "id": record_id})


@app.command("doctor")
def doctor(profile: ProfileOption = None) -> None:
    """Check the current setup and suggest the next concrete step."""
    config_path = default_config_path()
    details: dict[str, Any] = {
        "action": "doctor",
        "config_path": str(config_path),
    }

    try:
        config = IndoConfig.load()
    except FileNotFoundError:
        fail(
            f"Config file not found at {config_path}.",
            details={
                **details,
                "next_command": "indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin",
            },
        )

    available_profiles = sorted(config.profiles)
    details["available_profiles"] = available_profiles
    details["active_profile"] = config.active_profile

    if not available_profiles:
        fail(
            "No profiles are configured.",
            details={
                **details,
                "next_command": "indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin",
            },
        )

    try:
        resolved_name, resolved_profile = config.resolve_profile(profile)
    except KeyError as exc:
        next_command = (
            f"indoo profile use {available_profiles[0]}"
            if available_profiles
            else "indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin"
        )
        fail(str(exc), details={**details, "next_command": next_command})

    try:
        OdooConnection.connect(resolved_name, resolved_profile)
    except Exception as exc:
        alternatives = [name for name in available_profiles if name != resolved_name]
        next_command = (
            f"indoo profile use {alternatives[0]}"
            if alternatives
            else "indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin"
        )
        fail(
            f"Profile {resolved_name!r} could not connect: {exc}",
            details={
                **details,
                "checked_profile": resolved_name,
                "next_command": next_command,
            },
        )

    emit(
        {
            "ok": True,
            **details,
            "checked_profile": resolved_name,
            "message": f"Profile {resolved_name!r} is ready to use.",
            "next_command": f"indoo show res.partner 1 name --profile {resolved_name}",
        }
    )


@profile_app.command("list")
def profile_list() -> None:
    """List saved profiles."""
    try:
        config = IndoConfig.load()
    except FileNotFoundError:
        fail(
            f"Config file not found at {default_config_path()}.",
            details={
                "action": "profile_list",
                "next_command": "indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin",
            },
        )

    emit(
        {
            "ok": True,
            "action": "profile_list",
            "config_path": str(config.path),
            "active_profile": config.active_profile,
            "profiles": [
                {
                    "name": name,
                    "url": profile.url,
                    "db": profile.db,
                    "user": profile.user,
                }
                for name, profile in sorted(config.profiles.items())
            ],
        }
    )


@profile_app.command("show")
def profile_show(
    profile: ProfileOption = None,
) -> None:
    """Show one profile or the active profile."""
    try:
        config = IndoConfig.load()
        resolved_name, resolved_profile = config.resolve_profile(profile)
    except Exception as exc:
        fail(str(exc), details={"action": "profile_show"})

    emit(
        {
            "ok": True,
            "action": "profile_show",
            "config_path": str(config.path),
            "active_profile": config.active_profile,
            "profile": {
                "name": resolved_name,
                "url": resolved_profile.url,
                "db": resolved_profile.db,
                "user": resolved_profile.user,
            },
        }
    )


@profile_app.command("add")
def profile_add(
    name: Annotated[str, typer.Argument(help="Profile name to create or update.")],
    url: Annotated[str, typer.Option(help="Odoo base URL, for example http://localhost:8069.")],
    db: Annotated[str, typer.Option(help="Database name.")],
    user: Annotated[str, typer.Option(help="Login user.")],
    password: Annotated[str, typer.Option(help="Login password.")],
) -> None:
    """Create or update a profile and make it active."""
    config = IndoConfig.load() if default_config_path().exists() else IndoConfig.create_empty()
    config.add_profile(
        name,
        ConnectionProfile(url=url, db=db, user=user, password=password),
        make_active=True,
    )
    config.save()

    emit(
        {
            "ok": True,
            "action": "profile_add",
            "config_path": str(config.path),
            "active_profile": config.active_profile,
            "profile": {
                "name": name,
                "url": url,
                "db": db,
                "user": user,
            },
            "message": f"Profile {name!r} is ready.",
            "next_command": "indoo doctor",
        }
    )


@profile_app.command("use")
def profile_use(
    name: Annotated[str, typer.Argument(help="Profile name to activate.")],
) -> None:
    """Set the active profile."""
    try:
        config = IndoConfig.load()
        config.use_profile(name)
    except Exception as exc:
        fail(str(exc), details={"action": "profile_use"})

    config.save()
    emit(
        {
            "ok": True,
            "action": "profile_use",
            "config_path": str(config.path),
            "active_profile": config.active_profile,
            "message": f"Profile {name!r} is now active.",
            "next_command": "indoo doctor",
        }
    )


def main() -> None:
    app()
