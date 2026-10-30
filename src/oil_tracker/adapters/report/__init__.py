"""The report: one self-contained HTML file per submitted version (Product SSOT §7, A7).

Python writes the text and the tables; web/render.js, inlined with web/report.js, draws each Glass's
graph, context image and time axis when the file opens, as the editor does (architecture.md, "One
drawing module"). Everything is inside the file, so it works offline and prints to PDF on A4
landscape (web/report.css). The context image is joined from its cache pieces, scaled down and
embedded as JPEG to keep the file small. The layout follows DESIGN.md §5 "Report".
"""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from oil_tracker.application.ports import ImageLayout, ReportInput
from oil_tracker.domain.edits import GlassEdits, coverage, empty_samples, level_states, runs
from oil_tracker.domain.enums import JudgmentMode, LevelState, Verdict
from oil_tracker.domain.inspection import ANALYSIS_RATE
from oil_tracker.domain.judgment import Judgment, judge
from oil_tracker.domain.recipe import Glass
from oil_tracker.domain.version import GlassVerdict

IMAGE_WIDTH = 2000   # columns of the embedded context image at most; A4 landscape prints about 1,100 px
IMAGE_ROWS = 360     # rows at most
JPEG_QUALITY = 85
KEY_RUNS = 3         # FULL, EMPTY and "cannot judge" stretches listed in the key-time table, each

TITLE = "오일 레벨 검사 보고서"
MODES = {
    JudgmentMode.RECOVERY: "기준점 회복",
    JudgmentMode.HOLD_BELOW_ZERO: "기준점 아래 유지",
    JudgmentMode.HOLD_ABOVE_ZERO: "기준점 위 유지",
}
VERDICTS = {Verdict.PASS: ("합격", "pass"), Verdict.FAIL: ("불합격", "fail"), Verdict.REVIEW: ("검토 필요", "review")}


class HtmlReports:
    """Implements application.ports.ReportWriter from the web folder's drawing module and styles."""

    def __init__(self, web_folder: Path) -> None:
        self._web = web_folder

    def write(self, report: ReportInput) -> str:
        inspection, version, edits = report.inspection, report.version, report.edits
        glasses = {glass.id: glass for glass in inspection.recipe.glasses}
        decided = {glass.glass_id: glass for glass in version.glasses}
        layouts = {layout.glass_id: layout for layout in report.layouts}
        title = inspection.name or inspection.video.name
        # page 1: the facts, the judgments and every Glass's graph; then a page per Glass (user, 2026-10-30)
        order = [(glasses[g.glass_id], decided[g.glass_id]) for g in edits.glasses]
        total = 1 + len(order)

        def page(number: int, body: str, first: bool = False) -> str:
            return (
                f'<section class="page{" first" if first else ""}">{body}'
                f'<div class="foot"><span>{escape(title)} · v{version.number}</span><span>{number} / {total}</span></div></section>'
            )

        pages = [page(1, _first_page(report, title, order) + _overview(order), first=True)]
        data = []
        for index, glass_edits in enumerate(edits.glasses):
            glass = glasses[glass_edits.glass_id]
            judgment = judge(edits.times, glass_edits, glass, edits.compressor_start_sec)
            data.append(_panel(edits.times, glass_edits, glass, judgment, layouts[glass.id], report))
            body = _glass_section(edits.times, glass_edits, glass, judgment, decided[glass.id], index, edits.compressor_start_sec)
            pages.append(page(index + 2, _running_header(report, title) + body))
        parts = {
            "TITLE": escape(f"{TITLE} · {title} · v{version.number}"),
            "STYLE": self._read("tokens.css") + self._read("report.css"),
            "PAGES": "".join(pages),
            "DATA": json.dumps(data, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c"),  # no tag inside
            "SCRIPT": self._read("render.js") + self._read("report.js"),
        }
        return re.sub(r"<!--(TITLE|STYLE|PAGES|DATA|SCRIPT)-->", lambda m: parts[m[1]], self._read("report.html"))

    def _read(self, name: str) -> str:
        return (self._web / name).read_text(encoding="utf-8")


# ---- the text --------------------------------------------------------------------------------------


def _first_page(report: ReportInput, title: str, glasses: list[tuple[Glass, GlassVerdict]]) -> str:
    inspection, version, edits = report.inspection, report.version, report.edits
    settings, header = inspection.settings, inspection.header
    fields = [
        ("압축기 모델", header.compressor_model or "-"),
        ("시험 종류", header.test_type or "-"),
        ("영상 파일", inspection.video.name),
        ("Recipe", inspection.recipe.name),
        ("분석 범위", f"{_clock(settings.start_sec)} – {_clock(settings.end_sec)} (초당 {ANALYSIS_RATE:g} 샘플)"),
        ("압축기 기동", "없음" if edits.compressor_start_sec is None else _clock(edits.compressor_start_sec)),
        ("검사 이름", inspection.name or "-"),
        ("작성", _local(version.submitted_at)),
    ]
    rows = "".join(
        f"<tr><td>{escape(glass.name)}</td><td>{MODES[glass.judgment_rule.mode]}</td><td>{_badge(decided.verdict)}</td></tr>"
        for glass, decided in glasses
    )
    return (
        f'<div class="head"><div><h1>{TITLE}</h1><div class="sub">{escape(title)} · Oil Level Tracker</div></div>'
        f'<div class="ver"><b>v{version.number}</b><div class="sub">제출 {_local(version.submitted_at)}</div></div></div>'
        '<div class="fields">' + "".join(f"<div><span>{k}</span>{escape(v)}</div>" for k, v in fields) + "</div>"
        f'<h2>판정</h2><table class="summary"><tr><th>Glass</th><th>판정 규칙</th><th>판정</th></tr>{rows}</table>'
    )


def _overview(glasses: list[tuple[Glass, GlassVerdict]]) -> str:
    """Every Glass's graph on page 1, sharing what is left of the page (squeezed is fine)."""
    return '<div class="overview">' + "".join(
        f'<div class="overview-glass" data-index="{index}"><div class="label"><b>{escape(glass.name)}</b>'
        f'<span>{MODES[glass.judgment_rule.mode]}</span>{_badge(decided.verdict)}</div>'
        '<div class="plot graph"><svg></svg></div><div class="plot axis"><svg></svg></div></div>'
        for index, (glass, decided) in enumerate(glasses)
    ) + "</div>"


def _running_header(report: ReportInput, title: str) -> str:
    header, version = report.inspection.header, report.version
    model = " · ".join(v for v in (header.compressor_model, header.test_type) if v)
    return (
        f'<div class="strip"><b>{TITLE}</b><span>{escape(title)}</span>'
        + (f"<span>{escape(model)}</span>" if model else "")
        + f'<span class="right">v{version.number} · 제출 {_local(version.submitted_at)}</span></div>'
    )


def _glass_section(
    times: tuple[float, ...], edits: GlassEdits, glass: Glass, judgment: Judgment, decided: GlassVerdict, index: int,
    compressor: float | None,
) -> str:
    # the final judgment only; the user's reason as "판정 사유", never "덮어씀" (user, 2026-10-30)
    reason = f'<div class="reason"><b>판정 사유:</b> {escape(decided.reason)}</div>' if decided.override else ""
    legend = (
        '<span><i style="background:var(--oil)"></i>Oil</span><span><i style="background:var(--foam)"></i>Foam</span>'
        '<span><i style="border-top:1.5px dashed var(--reference);height:0"></i>참조</span><span>세로: 0선 기준 높이 (px)</span>'
    )
    memos = "".join(
        f'<div class="memo"><span class="pin">{n}</span><span class="t">{_clock(m.time_sec)}</span>{escape(m.text)}</div>'
        for n, m in enumerate(sorted(edits.memos, key=lambda m: m.time_sec), start=1)
    )
    return (
        f'<h2>{escape(glass.name)} <span class="mode">{MODES[glass.judgment_rule.mode]}</span> {_badge(decided.verdict, big=True)}</h2>'
        f"{reason}"
        f'<div class="plots" data-index="{index}">'
        f'<div class="label"><b>그래프</b>{legend}</div><div class="plot graph"><svg></svg></div>'
        '<div class="label"><b>맥락 이미지</b></div><div class="plot context"><svg></svg></div>'
        '<div class="plot axis"><svg></svg></div></div>'
        '<div class="two">'
        + _table(("판정 기준", "기준", "결과"), _criteria(edits, times, glass, judgment), numbers=2)
        + _table(("주요 시각", "시각", "내용"), _key_times(times, edits, glass, judgment, compressor))
        + "</div>"
        + (f'<div class="memos">{memos}</div>' if memos else "")
    )


def _criteria(edits: GlassEdits, times: tuple[float, ...], glass: Glass, judgment: Judgment) -> list[tuple[str, str, str]]:
    rule = glass.judgment_rule
    rows = []
    if rule.mode is JudgmentMode.RECOVERY:
        found = judgment.recovery
        rows.append(("회복 한도 (기동 후)", f"{_s(rule.recovery_limit_sec)} s 이내", "회복 없음" if found is None else f"{_s(found.after_sec)} s"))
        rows.append(("회복 뒤 유지", f"{_s(rule.stable_hold_sec)} s 이상", "-" if found is None else "유지"))
    else:
        side = "위로 올라간" if rule.mode is JudgmentMode.HOLD_BELOW_ZERO else "아래로 내려간"
        found = judgment.violation
        limit = f"{_s(rule.allowed_sec)} s 이하 (허용 {_s(rule.allowed_px)} px)"
        rows.append((f"0선 {side} 최장 시간", limit, "없음" if found is None else f"{_s(found.seconds)} s"))
    share = coverage(times, edits).valid_ratio
    rows.append(("유효 비율", f"{round(100 * rule.minimum_valid_coverage_ratio)} % 이상", f"{int(100 * share)} %"))
    return rows


def _key_times(
    times: tuple[float, ...], edits: GlassEdits, glass: Glass, judgment: Judgment, compressor: float | None
) -> list[tuple[str, str, str]]:
    step = 1.0 / ANALYSIS_RATE
    rows = [("압축기 기동", "-" if compressor is None else _clock(compressor), "")]
    if glass.judgment_rule.mode is JudgmentMode.RECOVERY:
        found = judgment.recovery
        rows.append(("0선 회복", "-", "없음") if found is None else ("0선 회복", _clock(times[found.first]), f"기동 후 {_s(found.after_sec)} s"))
    else:
        found = judgment.violation
        side = "위" if glass.judgment_rule.mode is JudgmentMode.HOLD_BELOW_ZERO else "아래"
        if found is None:
            rows.append(("위반", "-", "없음"))
        else:
            span = f"{_clock(times[found.first])} – {_clock(times[found.end - 1] + step)}"
            rows.append(("위반 (가장 긺)", span, f"{_s(found.seconds)} s, 최대 0선 {side} {found.worst_px:.1f} px"))
    levels = runs(level_states(edits.oil, glass))
    for state, name in ((LevelState.FULL, "FULL"), (LevelState.EMPTY, "EMPTY")):
        found_runs = [run for run in levels if run.value is state]
        for run in found_runs[:KEY_RUNS]:
            rows.append((name, _clock(times[run.first]), f"{_s((run.end - run.first) * step)} s 동안"))
        if len(found_runs) > KEY_RUNS:
            rows.append((name, "", f"외 {len(found_runs) - KEY_RUNS}곳"))
    for stretch in edits.cannot_judge[:KEY_RUNS]:
        rows.append(("판단 불가", f"{_clock(stretch.start_sec)} – {_clock(stretch.end_sec)}", ""))
    if len(edits.cannot_judge) > KEY_RUNS:
        rows.append(("판단 불가", "", f"외 {len(edits.cannot_judge) - KEY_RUNS}곳"))
    return rows


def _table(heads: tuple[str, str, str], rows: list[tuple[str, str, str]], numbers: int = 1) -> str:
    """Three columns; the `numbers` after the first are right-aligned figures."""
    cls = ["", ' class="n"', ' class="n"' if numbers == 2 else ""]
    head = "<tr>" + "".join(f"<th{c}>{h}</th>" for c, h in zip(cls, heads)) + "</tr>"
    body = "".join("<tr>" + "".join(f"<td{c}>{escape(v)}</td>" for c, v in zip(cls, row)) + "</tr>" for row in rows)
    return f"<table>{head}{body}</table>"


def _badge(verdict: Verdict, big: bool = False) -> str:
    text, tone = VERDICTS[verdict]
    return f'<span class="badge{" big" if big else ""} {tone}">{text}</span>'


def _clock(seconds: float) -> str:
    """mm:ss.s, as the app shows times (web/ui.js clock)."""
    tenths = round(seconds * 10)
    return f"{tenths // 600:02d}:{(tenths % 600) / 10:04.1f}"


def _local(iso: str) -> str:
    return f"{datetime.fromisoformat(iso).astimezone():%Y-%m-%d %H:%M}"


def _s(value: float) -> str:
    return f"{value:g}" if value == int(value) else f"{value:.1f}"


# ---- the drawing data --------------------------------------------------------------------------------


def _panel(
    times: tuple[float, ...], edits: GlassEdits, glass: Glass, judgment: Judgment, layout: ImageLayout, report: ReportInput
) -> dict[str, Any]:
    """One Glass as web/render.js draws it (its panel), with the memos as numbered pins."""
    zero, ellipse = glass.zero_line_y, glass.ellipse

    def heights(ys: tuple[float | None, ...]) -> list[float | None]:
        return [None if y is None else round(zero - y, 2) for y in ys]

    violation = judgment.violation
    memos = sorted(edits.memos, key=lambda m: m.time_sec)
    return {
        "times": list(times),
        "top": zero - (ellipse.center_y - ellipse.radius_y),
        "bottom": zero - (ellipse.center_y + ellipse.radius_y),
        "compressor": report.edits.compressor_start_sec,
        "lines": {key: heights(getattr(edits, key).ys) for key in ("oil", "foam", "reference")},
        "levels": [{"state": run.value.value, "first": run.first, "end": run.end} for run in runs(level_states(edits.oil, glass))],
        "cannot": [{"start_sec": s.start_sec, "end_sec": s.end_sec} for s in edits.cannot_judge],
        "empty": [{"first": run.first, "end": run.end} for run in runs(tuple(True if f else None for f in empty_samples(times, edits)))],
        "image": {
            "top": zero - layout.y0,
            "rows": layout.rows,
            "pieces": [{"href": _context_image(layout, report), "first": 0, "count": len(times)}],
        },
        "violation": None if violation is None else {"first": violation.first, "end": violation.end, "seconds": violation.seconds},
        "memos": [{"n": n, "t": m.time_sec, "h": None if m.y is None else zero - m.y} for n, m in enumerate(memos, start=1)],
    }


def _context_image(layout: ImageLayout, report: ReportInput) -> str:
    """The context image's pieces joined, scaled down and encoded as a JPEG data URI."""
    pieces = [cv2.imdecode(np.frombuffer(report.context_piece(layout.glass_id, i), np.uint8), cv2.IMREAD_COLOR) for i in range(layout.pieces)]
    picture = np.hstack(pieces)
    height, width = picture.shape[:2]
    size = (min(width, IMAGE_WIDTH), min(height, IMAGE_ROWS))
    if size != (width, height):
        picture = cv2.resize(picture, size, interpolation=cv2.INTER_AREA)
    ok, jpeg = cv2.imencode(".jpg", picture, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    if not ok:
        raise ValueError("맥락 이미지를 보고서에 넣지 못했습니다.")
    return "data:image/jpeg;base64," + base64.b64encode(jpeg.tobytes()).decode("ascii")
