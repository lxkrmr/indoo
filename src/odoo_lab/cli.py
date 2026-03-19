from __future__ import annotations

import json
from typing import Annotated, Any

import typer

from .client import Lab, LabConfig, parse_assignments, parse_context

app = typer.Typer(help="Inspect Odoo records with an OdooRPC-backed CLI.")


def _emit(payload: dict[str, Any]) -> None:
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


def _connect(context_items: list[str]) -> Lab:
    config = LabConfig.from_env()
    context = parse_context(context_items) if context_items else None
    return Lab(config=config, context=context)


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


@app.command("show")
def show_record(
    model: Annotated[str, typer.Argument(help="Technical model name, e.g. sale.order.")],
    record_id: Annotated[int, typer.Argument(help="Record ID to inspect.")],
    fields: FieldArgument,
    context_items: ContextOption = [],
) -> None:
    """Read selected fields from a single record."""
    if not fields:
        raise typer.BadParameter("Provide at least one field to inspect.")

    lab = _connect(context_items)
    record = lab.record(model, record_id)
    _emit(
        {
            "ok": True,
            "action": "show",
            "model": model,
            "id": record_id,
            "fields": fields,
            "context": lab.context,
            "record": record.read(fields),
        }
    )


@app.command("write-and-show")
def write_and_show_record(
    model: Annotated[str, typer.Argument(help="Technical model name, e.g. sale.order.")],
    record_id: Annotated[int, typer.Argument(help="Record ID to mutate.")],
    fields: FieldArgument,
    values: ValueOption,
    context_items: ContextOption = [],
) -> None:
    """Write values, then re-read selected fields to inspect recomputation effects."""
    if not fields:
        raise typer.BadParameter("Provide at least one field to inspect.")
    if not values:
        raise typer.BadParameter("Provide at least one --value assignment.")

    lab = _connect(context_items)
    record = lab.record(model, record_id)
    parsed_values = parse_assignments(values)
    before = record.read(fields)
    record.write(parsed_values)
    after = record.read(fields)

    changed = {
        field: {"before": before.get(field), "after": after.get(field)}
        for field in fields
        if before.get(field) != after.get(field)
    }

    _emit(
        {
            "ok": True,
            "action": "write_and_show",
            "model": model,
            "id": record_id,
            "context": lab.context,
            "write": parsed_values,
            "fields": fields,
            "before": before,
            "after": after,
            "changed": changed,
        }
    )


def main() -> None:
    app()
