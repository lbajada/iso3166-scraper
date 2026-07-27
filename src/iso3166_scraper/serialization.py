"""JSON serialization helpers for ISO 3166 data models."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

_KEY_RENAMES = {"code3166_2": "3166-2_code"}


def _normalize(value: Any) -> Any:
    """Recursively normalize a nested structure for JSON output.

    - Empty strings are converted to ``None``.
    - Internal field names are mapped to their public JSON keys
      (e.g. ``code3166_2`` → ``3166-2_code``).
    """
    if isinstance(value, str):
        return None if value == "" else value
    if isinstance(value, dict):
        return {
            _KEY_RENAMES.get(k, k): _normalize(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return value


def serialize(obj: Any) -> Any:
    """Convert a dataclass (or list thereof) to a JSON-ready dict."""
    raw = asdict(obj) if hasattr(obj, "__dataclass_fields__") else obj
    return _normalize(raw)
