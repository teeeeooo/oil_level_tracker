"""Strict readers for JSON values and the Windows-safe file name rule, for every saved format."""

from __future__ import annotations

import re
from typing import Any

_FORBIDDEN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED = re.compile(r"^(con|prn|aux|nul|com[0-9¹²³]|lpt[0-9¹²³])(\..*)?$", re.IGNORECASE)


def text(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError(f"expected text, got {type(value).__name__}")
    return value


def number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"expected a number, got {type(value).__name__}")
    return float(value)


def integer(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"expected an integer, got {type(value).__name__}")
    return value


def optional(read, value: Any):
    return None if value is None else read(value)


def safe_stem(name: str) -> str:
    """`name` made safe as a Windows file or folder name (docs/20-architecture/recipe-file.md)."""
    stem = _FORBIDDEN.sub("_", name.strip()).rstrip(". ")
    if not stem:
        stem = "_"
    if _RESERVED.match(stem):
        stem = "_" + stem
    return stem
