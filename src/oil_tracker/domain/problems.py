"""A problem found by a check, tied to a field the screen can mark."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    field: str
    message: str
    glass_id: str | None = None
