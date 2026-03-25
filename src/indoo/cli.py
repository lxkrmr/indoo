from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from typing import Annotated, Any

import typer

from .client import OdooConnection, parse_context
from .config import ConnectionProfile, IndoConfig, default_config_path
from .output import OutputManager
from .validation import (
    validate_field_names,
    validate_json_value,
    validate_model_name,
    validate_profile_name,
    validate_string_value,
)

app = typer.Typer(
    help=(
        "indoo is a read-only CLI for inspecting Odoo data. "
        "It helps developers understand what is in Odoo without mutating it. "
        "Start with 'indoo doctor' to verify your setup. "
        "Then use 'indoo fields_get MODEL' to explore a model, "
        "'indoo search MODEL' to find records, "
        "and 'indoo read MODEL ID FIELDS' to read a specific record."
    ),
    no_args_is_help=True,
)
profile_app = typer.Typer(
    help="Manage Odoo connection profiles. Start with 'indoo profile add ...'.",
    no_args_is_help=True,
)
app.add_typer(profile_app, name="profile")


@dataclass(slots=True)
class AppState:
    output: OutputManager


def get_state(ctx: typer.Context) -> AppState:
    state = ctx.obj
    if state is None:
        state = AppState(output=OutputManager())
        ctx.obj = state
    return state


def emit(ctx: typer.Context, payload: dict[str, Any]) -> None:
    get_state(ctx).output.emit(payload)


def fail(
    ctx: typer.Context,
    message: str,
    *,
    details: dict[str, Any] | None = None,
    code: int = 1,
) -> None:
    payload: dict[str, Any] = {"ok": False, "message": message}
    if details:
        payload.update(details)
    emit(ctx, payload)
    raise typer.Exit(code=code)


def error_message(exc: Exception) -> str:
    if isinstance(exc, KeyError) and exc.args:
        return str(exc.args[0])
    return str(exc)


def load_config() -> IndoConfig:
    return IndoConfig.load()


def connect(profile_name: str | None, context_items: list[str], context_json: str | None) -> OdooConnection:
    context = parse_json_object(context_json, label="Context JSON") if context_json else {}
    if context_items:
        context.update(parse_context(context_items))
    config = load_config()
    resolved_name, profile = config.resolve_profile(profile_name)
    return OdooConnection.connect(resolved_name, profile, context=context)


def parse_json_object(raw_json: str, *, label: str) -> dict[str, Any]:
    validate_string_value(raw_json, label=label)
    try:
        value = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} must be valid JSON: {exc.msg}.") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return validate_json_value(value, label=label)


def parse_domain(raw: str) -> list:
    try:
        value = ast.literal_eval(raw)
    except (ValueError, SyntaxError) as exc:
        raise ValueError(
            f"Domain must be a Python list of triples, "
            f"for example: [('name', 'ilike', 'Gold')]. Error: {exc}"
        ) from exc
    if not isinstance(value, list):
        raise ValueError(
            "Domain must be a list, for example: [('name', 'ilike', 'Gold')]."
        )
    return value


def build_profile_items(config: IndoConfig) -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "url": profile.url,
            "db": profile.db,
            "user": profile.user,
            "is_active": name == config.active_profile,
        }
        for name, profile in sorted(config.profiles.items())
    ]


ContextOption = Annotated[
    list[str],
    typer.Option(
        "--context",
        "-c",
        help="Context entry in KEY=VALUE form. VALUE can be JSON.",
    ),
]

ContextJsonOption = Annotated[
    str | None,
    typer.Option(
        "--context-json",
        help="Full Odoo context as a JSON object.",
    ),
]

FieldArgument = Annotated[
    list[str],
    typer.Argument(help="Fields to read from the record."),
]

ProfileOption = Annotated[
    str | None,
    typer.Option(
        "--profile",
        "-p",
        help="Profile name. Defaults to the active profile.",
    ),
]

LimitOption = Annotated[
    int,
    typer.Option(
        "--limit",
        min=1,
        help="Maximum number of records to return. Defaults to 10.",
    ),
]

OffsetOption = Annotated[
    int,
    typer.Option(
        "--offset",
        min=0,
        help="Number of records to skip before listing results.",
    ),
]

DomainOption = Annotated[
    str | None,
    typer.Option(
        "--domain",
        help=(
            "Odoo domain filter as a Python list of triples. "
            "Example: --domain \"[('bid_price', '>', 0), ('name', 'not ilike', 'Gold')]\""
        ),
    ),
]


@app.callback()
def main_options(ctx: typer.Context) -> None:
    ctx.obj = AppState(output=OutputManager())


@app.command("search")
def list_records(
    ctx: typer.Context,
    model: Annotated[str, typer.Argument(help="Technical model name, for example res.partner.")],
    fields: Annotated[list[str], typer.Argument(help="Optional fields to read for each record.")] = [],
    limit: LimitOption = 10,
    offset: OffsetOption = 0,
    domain: DomainOption = None,
    profile: ProfileOption = None,
    context_items: ContextOption = [],
    context_json: ContextJsonOption = None,
) -> None:
    """Search and read records for one model. Wraps Odoo's search_read.

    Use --domain to filter by field values using Odoo domain syntax:

      indoo search product.product id name --domain "[('bid_price', '>', 0)]"

    The domain is a Python list of triples ('field', 'operator', value).
    Prefix operators '|' and '&' are supported.
    """
    try:
        validate_model_name(model)
        validated_fields = validate_field_names(fields) if fields else []
        validated_profile = validate_profile_name(profile) if profile else None
        read_fields = list(dict.fromkeys(["id", *validated_fields])) if validated_fields else ["id"]
        parsed_domain = parse_domain(domain) if domain else []

        connection = connect(validated_profile, context_items, context_json)
        records = connection.model(model).list(read_fields, limit=limit, offset=offset, domain=parsed_domain)
        emit(
            ctx,
            {
                "ok": True,
                "action": "search",
                "model": model,
                "profile": connection.profile_name,
                "context": connection.context,
                "domain": parsed_domain,
                "fields": read_fields,
                "limit": limit,
                "offset": offset,
                "count": len(records),
                "records": records,
            },
        )
    except Exception as exc:
        fail(ctx, error_message(exc), details={"action": "search", "model": model})


@app.command("read")
def show_record(
    ctx: typer.Context,
    model: Annotated[str, typer.Argument(help="Technical model name, for example sale.order.")],
    record_id: Annotated[int, typer.Argument(help="Record ID to inspect.")],
    fields: FieldArgument,
    profile: ProfileOption = None,
    context_items: ContextOption = [],
    context_json: ContextJsonOption = None,
) -> None:
    """Read fields from a single record. Wraps Odoo's read. Use 'indoo fields_get MODEL' first if needed."""
    try:
        validate_model_name(model)
        validated_fields = validate_field_names(fields)
        validated_profile = validate_profile_name(profile) if profile else None
        if not validated_fields:
            raise ValueError("Provide at least one field to inspect.")

        connection = connect(validated_profile, context_items, context_json)
        record = connection.record(model, record_id)
        emit(
            ctx,
            {
                "ok": True,
                "action": "read",
                "model": model,
                "id": record_id,
                "profile": connection.profile_name,
                "fields": validated_fields,
                "context": connection.context,
                "record": record.read(validated_fields),
            },
        )
    except Exception as exc:
        fail(ctx, error_message(exc), details={"action": "read", "model": model, "id": record_id})


@app.command("fields_get")
def fields_command(
    ctx: typer.Context,
    model: Annotated[str, typer.Argument(help="Technical model name, for example purchase.order.")],
    fields: Annotated[list[str], typer.Argument(help="Optional field names to inspect.")] = [],
    profile: ProfileOption = None,
) -> None:
    """Describe fields and their metadata for one Odoo model. Wraps Odoo's fields_get."""
    try:
        validate_model_name(model)
        validated_fields = validate_field_names(fields) if fields else []
        validated_profile = validate_profile_name(profile) if profile else None

        connection = connect(validated_profile, [], None)
        field_items = connection.model(model).fields(validated_fields or None)
        if validated_fields and not field_items:
            raise ValueError(f"No matching fields were found for model {model!r}.")

        emit(
            ctx,
            {
                "ok": True,
                "action": "fields_get",
                "model": model,
                "profile": connection.profile_name,
                "fields": field_items,
            },
        )
    except Exception as exc:
        fail(ctx, error_message(exc), details={"action": "fields_get", "model": model})


@app.command("doctor")
def doctor(
    ctx: typer.Context,
    profile: ProfileOption = None,
) -> None:
    """Check config, profile resolution, and Odoo connectivity. Start here when unsure."""
    config_path = default_config_path()
    details: dict[str, Any] = {
        "action": "doctor",
        "config_path": str(config_path),
    }

    try:
        validated_profile = validate_profile_name(profile) if profile else None
        config = load_config()
    except FileNotFoundError:
        fail(
            ctx,
            f"Config file not found at {config_path}.",
            details={
                **details,
                "next_command": "indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin",
            },
        )
    except Exception as exc:
        fail(ctx, error_message(exc), details=details)

    available_profiles = sorted(config.profiles)
    details["available_profiles"] = available_profiles
    details["active_profile"] = config.active_profile

    if not available_profiles:
        fail(
            ctx,
            "No profiles are configured.",
            details={
                **details,
                "next_command": "indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin",
            },
        )

    try:
        resolved_name, resolved_profile = config.resolve_profile(validated_profile)
    except KeyError as exc:
        next_command = (
            f"indoo profile use {available_profiles[0]}"
            if available_profiles
            else "indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin"
        )
        fail(ctx, error_message(exc), details={**details, "next_command": next_command})

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
            ctx,
            f"Profile {resolved_name!r} could not connect: {exc}",
            details={
                **details,
                "checked_profile": resolved_name,
                "next_command": next_command,
            },
        )

    emit(
        ctx,
        {
            "ok": True,
            **details,
            "checked_profile": resolved_name,
            "message": f"Profile {resolved_name!r} is ready to use.",
            "next_command": f"indoo read res.partner 1 name --profile {resolved_name}",
        },
    )


@profile_app.command("list")
def profile_list(ctx: typer.Context) -> None:
    """List saved profiles."""
    try:
        config = load_config()
    except FileNotFoundError:
        fail(
            ctx,
            f"Config file not found at {default_config_path()}.",
            details={
                "action": "profile_list",
                "next_command": "indoo profile add local --url http://localhost:8069 --db odoo --user admin --password admin",
            },
        )

    profiles = build_profile_items(config)
    emit(
        ctx,
        {
            "ok": True,
            "action": "profile_list",
            "config_path": str(config.path),
            "active_profile": config.active_profile,
            "profiles": profiles,
        },
    )


@profile_app.command("show")
def profile_show(
    ctx: typer.Context,
    profile: ProfileOption = None,
) -> None:
    """Show one profile or the active profile."""
    try:
        validated_profile = validate_profile_name(profile) if profile else None
        config = load_config()
        resolved_name, resolved_profile = config.resolve_profile(validated_profile)
    except Exception as exc:
        fail(ctx, error_message(exc), details={"action": "profile_show"})

    emit(
        ctx,
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
        },
    )


@profile_app.command("add")
def profile_add(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Profile name to create or update.")],
    url: Annotated[str, typer.Option(help="Odoo base URL, for example http://localhost:8069.")],
    db: Annotated[str, typer.Option(help="Database name.")],
    user: Annotated[str, typer.Option(help="Login user.")],
    password: Annotated[str, typer.Option(help="Login password.")],
) -> None:
    """Create or update a profile and make it active. Run 'indoo doctor' right after."""
    try:
        validated_name = validate_profile_name(name)
        validated_url = validate_string_value(url, label="Profile URL")
        validated_db = validate_string_value(db, label="Database name")
        validated_user = validate_string_value(user, label="User name")
        validated_password = validate_string_value(password, label="Password")
        config_path = default_config_path()
        config = IndoConfig.load(config_path) if config_path.exists() else IndoConfig.create_empty(config_path)
        config.add_profile(
            validated_name,
            ConnectionProfile(
                url=validated_url,
                db=validated_db,
                user=validated_user,
                password=validated_password,
            ),
            make_active=True,
        )
        config.save()
    except Exception as exc:
        fail(ctx, error_message(exc), details={"action": "profile_add"})

    emit(
        ctx,
        {
            "ok": True,
            "action": "profile_add",
            "config_path": str(config.path),
            "active_profile": config.active_profile,
            "profile": {
                "name": validated_name,
                "url": validated_url,
                "db": validated_db,
                "user": validated_user,
            },
            "message": f"Profile {validated_name!r} is ready.",
            "next_command": "indoo doctor",
        },
    )


@profile_app.command("use")
def profile_use(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Profile name to activate.")],
) -> None:
    """Set the active profile."""
    try:
        validated_name = validate_profile_name(name)
        config = load_config()
        config.use_profile(validated_name)
        config.save()
    except Exception as exc:
        fail(ctx, error_message(exc), details={"action": "profile_use"})

    emit(
        ctx,
        {
            "ok": True,
            "action": "profile_use",
            "config_path": str(config.path),
            "active_profile": config.active_profile,
            "message": f"Profile {validated_name!r} is now active.",
            "next_command": "indoo doctor",
        },
    )


def main() -> None:
    app()
