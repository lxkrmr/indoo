from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import odoorpc

from .config import ConnectionProfile
from .validation import validate_json_value, validate_string_value


def parse_context(values: list[str]) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for item in values:
        key, raw_value = split_assignment(item)
        context[key] = coerce_value(raw_value)
    return context


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

    def list(self, fields: list[str], *, limit: int, offset: int, domain: list | None = None) -> list[dict[str, Any]]:
        records = self._model.search_read(domain or [], fields=fields, offset=offset, limit=limit, order="id asc")
        return [serialize_mapping(record) for record in records]


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
