from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import odoorpc

from .config import ConnectionProfile


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
    if "=" not in item:
        raise ValueError(f"Expected KEY=VALUE, got: {item!r}")
    key, value = item.split("=", 1)
    key = key.strip()
    if not key:
        raise ValueError(f"Expected non-empty key in assignment: {item!r}")
    return key, value.strip()


def coerce_value(raw_value: str) -> Any:
    try:
        return json.loads(raw_value)
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

    def record(self, model: str, record_id: int) -> "RecordHandle":
        return RecordHandle(self, model, record_id)


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
        self._record.write(values)


def parse_odoo_url(url: str) -> tuple[str, str, int]:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname:
        raise ValueError(f"Invalid Odoo URL: {url!r}")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return parsed.hostname, parsed.scheme, port


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
