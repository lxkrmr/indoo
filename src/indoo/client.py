from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import odoorpc

from .config import ConnectionProfile
from .validation import validate_json_value, validate_string_value


RELATIONAL_OPERATIONS = {"create", "update", "delete", "unlink", "link", "clear", "set"}


def parse_context(values: list[str]) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for item in values:
        key, raw_value = split_assignment(item)
        context[key] = coerce_value(raw_value)
    return context


def parse_assignments(values: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for item in values:
        key, raw_value = split_assignment(item)
        parsed[key] = coerce_value(raw_value)
    return parsed


def split_assignment(item: str) -> tuple[str, str]:
    validate_string_value(item, label="Assignment")
    if "=" not in item:
        raise ValueError(f"Expected KEY=VALUE, got: {item!r}")
    key, value = item.split("=", 1)
    key = key.strip()
    if not key:
        raise ValueError(f"Expected non-empty key in assignment: {item!r}")
    validate_string_value(key, label="Assignment key")
    return key, value.strip()


def coerce_value(raw_value: str) -> Any:
    validate_string_value(raw_value, label="Value")
    try:
        return validate_json_value(json.loads(raw_value), label="JSON value")
    except json.JSONDecodeError:
        lowered = raw_value.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if lowered == "null":
            return None
        return raw_value


@dataclass(slots=True)
class OdooConnection:
    profile_name: str
    profile: ConnectionProfile
    context: dict[str, Any]
    odoo: Any

    @classmethod
    def connect(
        cls,
        profile_name: str,
        profile: ConnectionProfile,
        context: dict[str, Any] | None = None,
    ) -> "OdooConnection":
        host, protocol, port = parse_odoo_url(profile.url)
        odoo = odoorpc.ODOO(host=host, protocol=protocol, port=port)
        odoo.login(profile.db, profile.user, profile.password)
        merged_context = context or {}
        if merged_context:
            odoo.env.context.update(merged_context)
        return cls(profile_name=profile_name, profile=profile, context=merged_context, odoo=odoo)

    def model(self, model: str) -> "ModelHandle":
        return ModelHandle(self, model)

    def record(self, model: str, record_id: int) -> "RecordHandle":
        return RecordHandle(self, model, record_id)


class ModelHandle:
    def __init__(self, connection: OdooConnection, model: str) -> None:
        self.connection = connection
        self.model = model

    @property
    def _model(self) -> Any:
        return self.connection.odoo.env[self.model]

    def fields(self, field_names: list[str] | None = None) -> list[dict[str, Any]]:
        raw_fields = self._model.fields_get(
            field_names or None,
            attributes=["string", "type", "required", "readonly", "relation", "selection"],
        )
        names = field_names or sorted(raw_fields)
        if field_names:
            missing = [name for name in field_names if name not in raw_fields]
            if missing:
                raise KeyError(f"Unknown fields: {', '.join(missing)}")
        return [normalize_field_info(name, raw_fields[name]) for name in names]

    def create(self, values: dict[str, Any]) -> int:
        return int(self._model.create(transform_payload(values)))


class RecordHandle:
    def __init__(self, connection: OdooConnection, model: str, record_id: int) -> None:
        self.connection = connection
        self.model = model
        self.record_id = record_id

    @property
    def _record(self) -> Any:
        return self.connection.odoo.env[self.model].browse(self.record_id)

    def read(self, fields: list[str]) -> dict[str, Any]:
        data = self._record.read(fields)[0]
        return serialize_mapping(data)

    def write(self, values: dict[str, Any]) -> None:
        self._record.write(transform_payload(values))


def parse_odoo_url(url: str) -> tuple[str, str, int]:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname:
        raise ValueError(f"Invalid Odoo URL: {url!r}")

    if parsed.scheme == "http":
        protocol = "jsonrpc"
        port = parsed.port or 80
    elif parsed.scheme == "https":
        protocol = "jsonrpc+ssl"
        port = parsed.port or 443
    else:
        raise ValueError(
            f"Invalid Odoo URL scheme: {parsed.scheme!r}. Use http:// or https://."
        )

    return parsed.hostname, protocol, port


def normalize_field_info(name: str, raw: dict[str, Any]) -> dict[str, Any]:
    info: dict[str, Any] = {
        "name": name,
        "type": str(raw.get("type", "unknown")),
        "string": str(raw.get("string") or name),
        "required": bool(raw.get("required", False)),
        "readonly": bool(raw.get("readonly", False)),
    }
    relation = raw.get("relation")
    if relation:
        info["relation"] = str(relation)
    selection = raw.get("selection")
    if selection:
        info["selection"] = [list(item) for item in selection]
    return info


def transform_payload(values: dict[str, Any]) -> dict[str, Any]:
    return {key: transform_value(value, path=key) for key, value in values.items()}


def transform_value(value: Any, *, path: str) -> Any:
    if isinstance(value, dict):
        return {key: transform_value(item, path=f"{path}.{key}") for key, item in value.items()}
    if isinstance(value, list):
        if is_relational_command_list(value):
            return [transform_relational_command(item, path=path) for item in value]
        return [transform_value(item, path=f"{path}[]") for item in value]
    return value


def is_relational_command_list(value: list[Any]) -> bool:
    return bool(value) and all(isinstance(item, dict) and item.get("op") in RELATIONAL_OPERATIONS for item in value)


def transform_relational_command(command: dict[str, Any], *, path: str) -> tuple[Any, ...]:
    op = command.get("op")
    if not isinstance(op, str) or op not in RELATIONAL_OPERATIONS:
        raise ValueError(f"{path} contains unsupported relational operation: {op!r}")

    allowed_keys = {
        "create": {"op", "values"},
        "update": {"op", "id", "values"},
        "delete": {"op", "id"},
        "unlink": {"op", "id"},
        "link": {"op", "id"},
        "clear": {"op"},
        "set": {"op", "ids"},
    }[op]
    extra_keys = sorted(set(command) - allowed_keys)
    if extra_keys:
        raise ValueError(f"{path} operation {op!r} does not support keys: {', '.join(extra_keys)}")

    if op == "create":
        values = command.get("values")
        if not isinstance(values, dict):
            raise ValueError(f"{path} operation 'create' requires an object in 'values'.")
        return (0, 0, transform_payload(values))

    if op == "update":
        record_id = require_positive_int(command.get("id"), path=path, key="id", op=op)
        values = command.get("values")
        if not isinstance(values, dict):
            raise ValueError(f"{path} operation 'update' requires an object in 'values'.")
        return (1, record_id, transform_payload(values))

    if op == "delete":
        return (2, require_positive_int(command.get("id"), path=path, key="id", op=op))

    if op == "unlink":
        return (3, require_positive_int(command.get("id"), path=path, key="id", op=op))

    if op == "link":
        return (4, require_positive_int(command.get("id"), path=path, key="id", op=op))

    if op == "clear":
        return (5,)

    ids = command.get("ids")
    if not isinstance(ids, list) or not ids:
        raise ValueError(f"{path} operation 'set' requires a non-empty 'ids' list.")
    return (6, 0, [require_positive_int(item, path=path, key="ids", op=op) for item in ids])


def require_positive_int(value: Any, *, path: str, key: str, op: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{path} operation {op!r} requires a positive integer in '{key}'.")
    return value


def serialize_mapping(values: dict[str, Any]) -> dict[str, Any]:
    return {key: serialize_value(value) for key, value in values.items()}


def serialize_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, tuple) and len(value) == 2:
        return {"id": value[0], "display_name": value[1]}
    if isinstance(value, list):
        if value and all(isinstance(item, int) for item in value):
            return {"ids": value, "count": len(value)}
        return [serialize_value(item) for item in value]
    if isinstance(value, dict):
        return serialize_mapping(value)
    return str(value)
