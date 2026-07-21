from __future__ import annotations

import logging

import oil_tracker.visualization.matplotlib_font as font_policy
from oil_tracker.visualization.matplotlib_font import MatplotlibFontEntry


def test_priority_order_uses_first_real_hangul_font(monkeypatch) -> None:
    entries = [
        MatplotlibFontEntry("Apple SD Gothic Neo", "/fonts/apple.ttf"),
        MatplotlibFontEntry("Noto Sans KR", "/fonts/noto-kr.ttf"),
        MatplotlibFontEntry("Noto Sans CJK KR", "/fonts/noto-cjk.ttf"),
        MatplotlibFontEntry("Malgun Gothic", "/fonts/malgun.ttf"),
    ]
    monkeypatch.setattr(font_policy, "_supports_hangul", lambda _path: True)
    selected = font_policy.resolve_matplotlib_font(entries)
    assert selected.family == "Malgun Gothic"
    assert selected.source == "priority"
    assert selected.supports_hangul


def test_named_candidate_without_hangul_glyph_is_rejected(monkeypatch) -> None:
    entries = [
        MatplotlibFontEntry("Malgun Gothic", "/fonts/broken-malgun.ttf"),
        MatplotlibFontEntry("Noto Sans CJK KR", "/fonts/noto-cjk.ttf"),
    ]
    monkeypatch.setattr(
        font_policy,
        "_supports_hangul",
        lambda path: path.endswith("noto-cjk.ttf"),
    )
    selected = font_policy.resolve_matplotlib_font(entries)
    assert selected.family == "Noto Sans CJK KR"


def test_arbitrary_hangul_capable_font_is_deterministic_fallback(monkeypatch) -> None:
    entries = [
        MatplotlibFontEntry("Z Korean", "/fonts/z.ttf"),
        MatplotlibFontEntry("A Korean", "/fonts/a.ttf"),
    ]
    monkeypatch.setattr(font_policy, "_supports_hangul", lambda _path: True)
    selected = font_policy.resolve_matplotlib_font(entries)
    assert selected.family == "A Korean"
    assert selected.source == "hangul_glyph_fallback"


def test_no_font_warning_is_emitted_once(monkeypatch, caplog) -> None:
    font_policy.reset_matplotlib_font_cache()
    monkeypatch.setattr(font_policy, "_supports_hangul", lambda _path: False)
    monkeypatch.setattr(font_policy.font_manager, "findfont", lambda *_args, **_kwargs: "/fonts/dejavu.ttf")
    with caplog.at_level(logging.WARNING):
        first = font_policy.resolve_matplotlib_font([])
        second = font_policy.resolve_matplotlib_font([])
    assert first.source == second.source == "matplotlib_fallback"
    messages = [record.message for record in caplog.records if "Hangul-capable" in record.message]
    assert len(messages) == 1
