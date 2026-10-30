"""A submitted version: the edits locked with each Glass's judgment (Product SSOT §3, A9)."""

from __future__ import annotations

from dataclasses import dataclass

from .edits import Edits
from .enums import Verdict
from .judgment import Judgment, final_verdict
from .recipe import Recipe

MAXIMUM_VERSIONS = 999  # versions\NNN


@dataclass(frozen=True)
class GlassVerdict:
    """One Glass's judgment as submitted."""

    glass_id: str
    verdict: Verdict           # the final one, which the report shows
    computed: Verdict          # the app's own result, kept as the user's record (DESIGN.md §2.4)
    computed_reason: str
    override: Verdict | None
    reason: str                # the user's "판정 사유"; "" without an override
    checked_at: str


@dataclass(frozen=True)
class Version:
    number: int
    submitted_at: str
    glasses: tuple[GlassVerdict, ...]


def unchecked(edits: Edits) -> tuple[str, ...]:
    """The Glasses still to check before submitting (§3)."""
    return tuple(glass.glass_id for glass in edits.glasses if glass.decision.checked_at is None)


def version_of(number: int, submitted_at: str, edits: Edits, judgments: dict[str, Judgment], recipe: Recipe) -> Version:
    """The version of checked edits, a Glass per Glass of the Recipe copy in its order."""
    if unchecked(edits):
        raise ValueError("모든 Glass를 확인해야 제출할 수 있습니다.")
    decisions = {glass.glass_id: glass.decision for glass in edits.glasses}
    return Version(
        number,
        submitted_at,
        tuple(
            GlassVerdict(
                glass.id,
                final_verdict(judgments[glass.id], decisions[glass.id]),
                judgments[glass.id].verdict,
                judgments[glass.id].reason,
                decisions[glass.id].override,
                decisions[glass.id].reason,
                decisions[glass.id].checked_at,  # type: ignore[arg-type] - checked above
            )
            for glass in recipe.glasses
        ),
    )
