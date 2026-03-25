from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import typer


@dataclass(slots=True)
class OutputManager:
    def emit(self, payload: dict[str, Any]) -> None:
        typer.echo(json.dumps(payload, indent=2, sort_keys=True))
