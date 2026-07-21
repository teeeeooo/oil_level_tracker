from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import logging
from pathlib import Path
import warnings

from matplotlib import font_manager, rcParams
from matplotlib.font_manager import FontProperties
from matplotlib.ft2font import FT2Font

LOGGER = logging.getLogger(__name__)
FONT_PRIORITY = (
    "Malgun Gothic",
    "Noto Sans CJK KR",
    "Noto Sans KR",
    "Apple SD Gothic Neo",
)
_HANGUL_PROBES = ("가", "유", "면", "거", "품")
_warning_emitted = False
_configured_selection: "MatplotlibFontSelection | None" = None


@dataclass(frozen=True)
class MatplotlibFontEntry:
    family: str
    path: str


@dataclass(frozen=True)
class MatplotlibFontSelection:
    family: str
    path: str
    source: str
    supports_hangul: bool

    @property
    def properties(self) -> FontProperties:
        return FontProperties(fname=self.path) if self.path else FontProperties(family=self.family)


def resolve_matplotlib_font(
    entries: tuple[MatplotlibFontEntry, ...] | list[MatplotlibFontEntry] | None = None,
) -> MatplotlibFontSelection:
    """Resolve a real Hangul-capable font, using the process cache by default."""

    if entries is None:
        return _resolve_installed_font()
    return _select_font(tuple(entries))


@lru_cache(maxsize=1)
def _resolve_installed_font() -> MatplotlibFontSelection:
    entries = tuple(
        MatplotlibFontEntry(str(item.name), str(item.fname))
        for item in font_manager.fontManager.ttflist
        if getattr(item, "name", None) and getattr(item, "fname", None)
    )
    return _select_font(entries)


def _select_font(entries: tuple[MatplotlibFontEntry, ...]) -> MatplotlibFontSelection:
    usable = tuple(entry for entry in entries if _supports_hangul(entry.path))
    for preferred in FONT_PRIORITY:
        match = next((entry for entry in usable if entry.family.casefold() == preferred.casefold()), None)
        if match is not None:
            selection = MatplotlibFontSelection(match.family, match.path, "priority", True)
            LOGGER.debug(
                "Selected Matplotlib Korean font family=%s source=%s path=%s",
                selection.family,
                selection.source,
                selection.path,
            )
            return selection
    if usable:
        match = sorted(usable, key=lambda entry: (entry.family.casefold(), entry.path))[0]
        selection = MatplotlibFontSelection(match.family, match.path, "hangul_glyph_fallback", True)
        LOGGER.debug(
            "Selected Matplotlib Korean font family=%s source=%s path=%s",
            selection.family,
            selection.source,
            selection.path,
        )
        return selection
    fallback_path = font_manager.findfont("DejaVu Sans", fallback_to_default=True)
    selection = MatplotlibFontSelection("DejaVu Sans", str(fallback_path), "matplotlib_fallback", False)
    _warn_no_hangul_font(selection)
    return selection


def configure_matplotlib_korean_font() -> MatplotlibFontSelection:
    """Configure the chosen family once and return the cached selection."""

    global _configured_selection
    selection = resolve_matplotlib_font()
    if _configured_selection != selection:
        rcParams["font.family"] = [selection.family]
        rcParams["axes.unicode_minus"] = False
        _configured_selection = selection
    return selection


def apply_font_to_axes(axes, selection: MatplotlibFontSelection | None = None) -> None:
    selection = selection or configure_matplotlib_korean_font()
    properties = selection.properties
    artists = [
        axes.title,
        axes.xaxis.label,
        axes.yaxis.label,
        *axes.get_xticklabels(),
        *axes.get_yticklabels(),
        *axes.texts,
    ]
    legend = axes.get_legend()
    if legend is not None:
        artists.extend(legend.get_texts())
        if legend.get_title() is not None:
            artists.append(legend.get_title())
    for artist in artists:
        artist.set_fontproperties(properties)


def reset_matplotlib_font_cache() -> None:
    """Testing hook; normal application code relies on the process cache."""

    global _configured_selection, _warning_emitted
    _resolve_installed_font.cache_clear()
    _configured_selection = None
    _warning_emitted = False


def _supports_hangul(path: str) -> bool:
    try:
        font = FT2Font(str(Path(path)))
        return all(font.get_char_index(ord(character)) != 0 for character in _HANGUL_PROBES)
    except (OSError, RuntimeError, ValueError):
        return False


def _warn_no_hangul_font(selection: MatplotlibFontSelection) -> None:
    global _warning_emitted
    if _warning_emitted:
        return
    _warning_emitted = True
    LOGGER.warning(
        "No installed Hangul-capable Matplotlib font was found; using %s. Korean graph text may be unavailable.",
        selection.family,
    )
    warnings.filterwarnings("ignore", message=r"Glyph .* missing from font", category=UserWarning)
