from __future__ import annotations

from typing import Any


def reject_control_chars(value: str, *, label: str) -> None:
    for char in value:
        if ord(char) < 32 and char not in ("\n", "\r", "\t"):
            raise ValueError(f"{label} contains unsupported control characters.")


def validate_profile_name(name: str) -> str:
    reject_control_chars(name, label="Profile name")
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
    if not name or any(char not in allowed for char in name):
        raise ValueError("Profile name may only contain letters, numbers, '.', '-' and '_'.")
    return name


def validate_model_name(model: str) -> str:
    reject_control_chars(model, label="Model name")
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._")
    if not model or any(char not in allowed for char in model):
        raise ValueError("Model name may only contain letters, numbers, '.' and '_'.")
    if "?" in model or "#" in model or "%" in model:
        raise ValueError("Model name must not contain query, fragment, or encoded characters.")
    return model


def validate_field_names(fields: list[str]) -> list[str]:
    validated: list[str] = []
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._")
    for field in fields:
        reject_control_chars(field, label="Field name")
        if not field or any(char not in allowed for char in field):
            raise ValueError(
                f"Invalid field name: {field!r}. "
                "Use space-separated field names, "
                "for example: indoo list res.partner id name email"
            )
        validated.append(field)
    return validated


def validate_string_value(value: str, *, label: str) -> str:
    reject_control_chars(value, label=label)
    return value


def validate_json_value(value: Any, *, label: str) -> Any:
    if isinstance(value, str):
        return validate_string_value(value, label=label)
    if isinstance(value, list):
        return [validate_json_value(item, label=label) for item in value]
    if isinstance(value, dict):
        validated: dict[str, Any] = {}
        for key, item in value.items():
            validate_string_value(str(key), label=f"{label} key")
            validated[str(key)] = validate_json_value(item, label=label)
        return validated
    return value
