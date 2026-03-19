from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import odoorpc


def parse_context(values: list[str]) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for item in values:
        key, raw_value = _split_assignment(item)
        context[key] = _coerce_value(raw_value)
    return context


def _split_assignment(item: str) -> tuple[str, str]:
    if "=" not in item:
        raise ValueError(f"Expected KEY=VALUE, got: {item!r}")
    key, value = item.split("=", 1)
    key = key.strip()
    if not key:
        raise ValueError(f"Expected non-empty key in assignment: {item!r}")
    return key, value.strip()


def _coerce_value(raw_value: str) -> Any:
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
class LabConfig:
    url: str
    db: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "LabConfig":
        return cls(
            url=os.environ.get("ODOO_URL", "http://localhost:8069"),
            db=os.environ.get("ODOO_DB", "odoo"),
            user=os.environ.get("ODOO_USER", "admin"),
            password=os.environ.get("ODOO_PASSWORD", "admin"),
        )


class Lab:
    def __init__(self, config: LabConfig, context: dict[str, Any] | None = None) -> None:
        host, protocol, port = self._parse_url(config.url)
        self.config = config
        self.context = context or {}
        self.odoo = odoorpc.ODOO(host=host, protocol=protocol, port=port)
        self.odoo.login(config.db, config.user, config.password)
        if self.context:
            self.odoo.env.context.update(self.context)

    @staticmethod
    def _parse_url(url: str) -> tuple[str, str, int]:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if not parsed.scheme or not parsed.hostname:
            raise ValueError(f"Invalid Odoo URL: {url!r}")
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        return parsed.hostname, parsed.scheme, port

    def record(self, model: str, record_id: int) -> "RecordHandle":
        return RecordHandle(self, model, record_id)

    def with_context(self, values: list[str]) -> "Lab":
        merged = dict(self.context)
        merged.update(parse_context(values))
        return Lab(self.config, context=merged)


class RecordHandle:
    def __init__(self, lab: Lab, model: str, record_id: int) -> None:
        self.lab = lab
        self.model = model
        self.record_id = record_id

    @property
    def _record(self) -> Any:
        return self.lab.odoo.env[self.model].browse(self.record_id)

    def read(self, fields: list[str]) -> dict[str, Any]:
        data = self._record.read(fields)[0]
        return _serialize_mapping(data)

    def write(self, values: dict[str, Any]) -> None:
        self._record.write(values)


def parse_assignments(values: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for item in values:
        key, raw_value = _split_assignment(item)
        parsed[key] = _coerce_value(raw_value)
    return parsed


def _serialize_mapping(values: dict[str, Any]) -> dict[str, Any]:
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
        return _serialize_mapping(value)
    return str(value)
