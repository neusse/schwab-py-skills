"""Helpers for translating CLI strings to schwab-py enums."""

from __future__ import annotations

from enum import Enum
from typing import Any


def enum_value(enum_type: type[Enum], value: str | Enum | None) -> Enum | None:
    """Return an enum member from a CLI-friendly string."""

    if value is None or isinstance(value, enum_type):
        return value
    normalized = value.upper().replace("-", "_")
    try:
        return enum_type[normalized]
    except KeyError as exc:
        choices = ", ".join(member.name.lower().replace("_", "-") for member in enum_type)
        raise ValueError(f"Invalid {enum_type.__name__}: {value}. Choices: {choices}") from exc


def enum_list(enum_type: type[Enum], values: list[str] | None) -> list[Enum] | None:
    if not values:
        return None
    return [enum_value(enum_type, value) for value in values]


def clean_none(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}
