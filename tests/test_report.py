"""The report file (Product SSOT §7, A7; DESIGN.md §5 "Report")."""

import json
from dataclasses import replace
import re
from pathlib import Path

import cv2
import numpy as np

from oil_tracker.adapters.report import HtmlReports
from oil_tracker.application.ports import ImageLayout, ReportInput
from oil_tracker.bootstrap import WEB_FOLDER
from oil_tracker.domain.edits import Decision, GlassEdits, Memo, Stretch, empty_line
from oil_tracker.domain.enums import InspectionState, JudgmentMode, SampleOrigin, Verdict
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import AnalysisSettings, Inspection, ReportHeader, SourceVideo
from oil_tracker.domain.line import Line
from oil_tracker.domain.recipe import Glass, JudgmentRule, Recipe, ReferenceFrame
from oil_tracker.domain.version import GlassVerdict, Version
from oil_tracker.domain.edits import Edits

BASE = Glass("g1", "BASE", Ellipse(640, 300, 80, 200), 380)  # RECOVERY; top y 100, bottom y 500
ACCUM = Glass("g2", "Accum <A>", Ellipse(900, 300, 80, 200), 380, JudgmentRule(JudgmentMode.HOLD_ABOVE_ZERO))
RECIPE = Recipe("r1", "2호기 냉각", ReferenceFrame(1280, 720, "SPL4.mp4", 0.0, b"jpeg"), (BASE, ACCUM), "c", "u")
VIDEO = SourceVideo("/videos/SPL4.mp4", "SPL#4_Cooling.mp4", 5_000, 1280, 720, 10.0, 3000, sha256="abc")
D = SampleOrigin.DRAFT


def inspection(glasses=(BASE, ACCUM), name="1차 냉각"):
    recipe = replace(RECIPE, glasses=tuple(glasses))
    return Inspection(
        "i1", "2026-10-30T05:00:00+00:00", VIDEO, recipe, AnalysisSettings(0.0, 299.5, 30.0), InspectionState.ANALYSED,
        name=name, header=ReportHeader("GB-2 R410A", "냉각 on/off"),
    )


def oil(times, height):
    return Line(tuple(380.0 - height(t) for t in times), (D,) * len(times))


def report_input(seconds=300.0, glasses=(BASE, ACCUM), noise=False):
    times = tuple(0.5 * i for i in range(int(seconds * 2)))
    n = len(times)
    lines = {
        "g1": oil(times, lambda t: -20.0 if t < 60 else 30.0),       # recovers 30 s after the start
        "g2": oil(times, lambda t: -6.0 if 100 <= t < 104.5 else 40.0),  # 4.5 s below zero
        "g3": oil(times, lambda t: 50.0),
    }
    memo = Memo("m1", 62.0, 360.0, '<b>거품</b> "/*DATA*/" <!--PAGES-->')
    decisions = {
        "g1": Decision(None, "", "2026-10-30T05:20:00+00:00"),
        "g2": Decision(Verdict.FAIL, "01:40 부근 거품이 유면을 가림", "2026-10-30T05:21:00+00:00"),
        "g3": Decision(None, "", "2026-10-30T05:22:00+00:00"),
    }
    edits = Edits(
        times,
        tuple(
            GlassEdits(
                g.id, lines[g.id], empty_line(n), empty_line(n),
                cannot_judge=(Stretch(130.0, 150.0),) if g.id == "g1" else (),
                memos=(memo,) if g.id == "g1" else (),
                decision=decisions[g.id],
            )
            for g in glasses
        ),
        30.0,
    )
    verdicts = {"g1": (Verdict.PASS, Verdict.PASS), "g2": (Verdict.FAIL, Verdict.PASS), "g3": (Verdict.PASS, Verdict.PASS)}
    version = Version(1, "2026-10-30T05:22:00+00:00", tuple(
        GlassVerdict(g.id, *verdicts[g.id], "자동", decisions[g.id].override, decisions[g.id].reason, decisions[g.id].checked_at)
        for g in glasses
    ))
    rng = np.random.default_rng(0)
    pieces = {}
    layouts = []
    for g in glasses:
        widths = [min(4096, n - first) for first in range(0, n, 4096)]
        for k, width in enumerate(widths):
            picture = rng.integers(0, 255, (400, width, 3), dtype=np.uint8) if noise else np.full((400, width, 3), 90, np.uint8)
            pieces[(g.id, k)] = cv2.imencode(".png", picture)[1].tobytes()
        layouts.append(ImageLayout(g.id, 90, 400, len(widths)))
    return ReportInput(inspection(glasses), version, edits, tuple(layouts), lambda glass_id, k: pieces[(glass_id, k)])


def data_of(html):
    found = re.search(r'<script type="application/json" id="reportData">(.*?)</script>', html, re.S)
    return json.loads(found.group(1))


def test_the_report_has_the_header_the_final_judgments_and_a_page_per_glass():
    html = HtmlReports(WEB_FOLDER).write(report_input())
    # page 1: the facts, the judgments and every Glass's graph; then a page per Glass (user, 2026-10-30)
    assert html.count('<section class="page') == 3 and html.count('class="page first"') == 1
    first = html[html.index('class="page first"'):html.index("</section>")]
    assert first.count('class="overview-glass"') == 2 and 'class="plot context"' not in first
    for text in ("오일 레벨 검사 보고서", "GB-2 R410A", "냉각 on/off", "SPL#4_Cooling.mp4", "2호기 냉각", "00:00.0 – 04:59.5", "00:30.0"):
        assert text in html, text
    assert "Accum &lt;A&gt;" in html and "<A>" not in html
    # the final judgment only, with the user's reason as "판정 사유" (user, 2026-10-30)
    assert html.count("판정 사유:") == 1 and "01:40 부근 거품이 유면을 가림" in html and "덮어씀" not in html
    assert '<span class="badge big fail">불합격</span>' in html and '<span class="badge big pass">합격</span>' in html
    # the criteria and key times
    assert "30 s" in html and "기동 후 30 s" in html                    # BASE recovered 30 s after the start
    assert "0선 아래로 내려간 최장 시간" in html and "4.5 s, 최대 0선 아래 6.0 px" in html
    assert "01:40.0 – 01:44.5" in html and "02:10.0 – 02:30.0" in html  # the violation; "cannot judge"
    assert '<div class="foot"><span>1차 냉각 · v1</span><span>3 / 3</span></div>' in html


def test_typed_text_is_escaped_and_not_read_again():
    html = HtmlReports(WEB_FOLDER).write(report_input())
    assert "&lt;b&gt;거품&lt;/b&gt; &quot;/*DATA*/&quot; &lt;!--PAGES--&gt;" in html
    assert "<!--PAGES-->" not in html and "<!--SCRIPT-->" not in html
    data = data_of(html)
    assert len(data) == 2 and data[0]["memos"] == [{"n": 1, "t": 62.0, "h": 20.0}]
    assert data[1]["violation"] == {"first": 200, "end": 209, "seconds": 4.5}
    assert data[0]["image"]["pieces"][0]["href"].startswith("data:image/jpeg;base64,")
    assert "export function graphSvg" in html  # render.js, inlined


def test_a_68_minute_video_with_three_glasses_stays_under_5_mb():
    third = Glass("g3", "Disch", Ellipse(400, 300, 80, 200), 380)
    html = HtmlReports(WEB_FOLDER).write(report_input(seconds=68 * 60, glasses=(BASE, ACCUM, third), noise=True))
    assert len(html.encode("utf-8")) < 5_000_000  # A7, with noise, the worst a context image compresses


def test_the_template_marks_are_all_filled():
    html = HtmlReports(WEB_FOLDER).write(report_input(glasses=(BASE,)))
    assert re.search(r"<!--(TITLE|STYLE|PAGES|DATA|SCRIPT)-->", html) is None
    assert "<title>오일 레벨 검사 보고서 · 1차 냉각 · v1</title>" in html
    assert "--oil:" in html and "@page { size: A4 landscape" in html  # the tokens and the print page
    assert Path(WEB_FOLDER / "report.js").read_text(encoding="utf-8") in html
