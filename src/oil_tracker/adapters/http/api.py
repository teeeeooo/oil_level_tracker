"""HTTP routes: the web files and the JSON API. Calls use cases only."""

from __future__ import annotations

import json
import math
import re
import sys
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from oil_tracker.application.editing import Editing, GlassState, InvalidEdits, NotAnalysed, SourceCheck
from oil_tracker.application.inspections import (
    GlassPosition,
    InspectionSetup,
    Inspections,
    InvalidSetup,
)
from oil_tracker.application.ports import (
    DesktopUnavailable,
    InspectionEntry,
    InspectionNotFound,
    RecipeNotFound,
    Region,
    StoredAnalysis,
    UnreadableAnalysis,
    UnreadableEdits,
    VideoUnreadable,
)
from oil_tracker.application.recipes import (
    RecipeDraft,
    Recipes,
    ReferenceChoice,
    VideoDoesNotFit,
)
from oil_tracker.application.videos import OpenedVideo, UnknownVideo, VideoSessions
from oil_tracker.domain.edits import Dropped, Edits, GlassEdits, Memo, Stretch
from oil_tracker.domain.enums import JudgmentMode, SampleOrigin
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import AnalysisSettings, Inspection, needs_compressor_start
from oil_tracker.domain.line import Line
from oil_tracker.domain.problems import Problem
from oil_tracker.domain.recipe import Glass, JudgmentRule, Recipe

from .jobs import Jobs, JobsBusy, UnknownJob

TOKEN_HEADER = "X-OLT-Token"
MAX_BODY_BYTES = 16_000_000  # the edits of a 68-min video with three Glasses are about 2 MB
COPY_CHUNK = 1 << 20
STATIC_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
}
VIDEO_TYPES = {
    ".mp4": "video/mp4",
    ".m4v": "video/mp4",
    ".mov": "video/quicktime",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
    ".avi": "video/x-msvideo",
}
LINE_KEYS = ("oil", "foam", "reference")
_RULE_NUMBERS = ("recovery_limit_sec", "stable_hold_sec", "minimum_valid_coverage_ratio", "allowed_sec", "allowed_px")
_ELLIPSE_NUMBERS = ("center_x", "center_y", "radius_x", "radius_y")


class BadRequest(ValueError):
    pass


class RangeNotSatisfiable(ValueError):
    pass


@dataclass(frozen=True)
class FilePart:
    """Bytes of a file sent as the body, read as they go out: a source video is too large to hold."""

    path: Path
    start: int
    length: int


@dataclass(frozen=True)
class Response:
    status: int
    body: bytes
    content_type: str
    headers: tuple[tuple[str, str], ...] = ()
    file: FilePart | None = None


@dataclass
class ApiContext:
    recipes: Recipes
    inspections: Inspections
    editing: Editing
    videos: VideoSessions
    jobs: Jobs
    web_folder: Path
    token: str


def json_response(value: Any, status: int = 200) -> Response:
    body = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    return Response(status, body, "application/json; charset=utf-8")


def error(status: int, message: str) -> Response:
    return json_response({"error": message}, status)


# ---- JSON mapping -------------------------------------------------------------------


def recipe_summary(recipe: Recipe) -> dict[str, Any]:
    return {
        "id": recipe.id,
        "name": recipe.name,
        "glass_names": [glass.name for glass in recipe.glasses],
        "width": recipe.reference_frame.width,
        "height": recipe.reference_frame.height,
        "updated_at": recipe.updated_at,
    }


def recipe_detail(recipe: Recipe) -> dict[str, Any]:
    frame = recipe.reference_frame
    return {
        "id": recipe.id,
        "name": recipe.name,
        "created_at": recipe.created_at,
        "updated_at": recipe.updated_at,
        "reference_frame": {
            "width": frame.width,
            "height": frame.height,
            "source_name": frame.source_name,
            "time_sec": frame.time_sec,
        },
        "glasses": [
            {
                "id": glass.id,
                "name": glass.name,
                "ellipse": {key: getattr(glass.ellipse, key) for key in _ELLIPSE_NUMBERS},
                "zero_line_y": glass.zero_line_y,
                "judgment_rule": {
                    "mode": glass.judgment_rule.mode.value,
                    **{key: getattr(glass.judgment_rule, key) for key in _RULE_NUMBERS},
                },
            }
            for glass in recipe.glasses
        ],
    }


def problems_json(problems: tuple[Problem, ...]) -> list[dict[str, Any]]:
    return [{"field": p.field, "glass_id": p.glass_id, "message": p.message} for p in problems]


def video_json(opened: OpenedVideo) -> dict[str, Any]:
    info = opened.info
    return {
        "id": opened.id,
        "name": info.name,
        "width": info.width,
        "height": info.height,
        "fps": info.fps,
        "frame_count": info.frame_count,
        "duration_sec": info.duration_sec,
    }


def inspection_summary(entry: InspectionEntry) -> dict[str, Any]:
    inspection = entry.inspection
    return {
        "id": inspection.id,
        "name": inspection.name,
        "folder": entry.folder_name,
        "video_name": inspection.video.name,
        "recipe_name": inspection.recipe.name,
        "glass_names": [glass.name for glass in inspection.recipe.glasses],
        "created_at": inspection.created_at,
        "state": inspection.state.value,
        "failure": inspection.failure,
    }


def inspection_detail(inspection: Inspection) -> dict[str, Any]:
    video, settings = inspection.video, inspection.settings
    return {
        "id": inspection.id,
        "name": inspection.name,
        "created_at": inspection.created_at,
        "state": inspection.state.value,
        "failure": inspection.failure,
        "video": {
            "path": video.path,
            "name": video.name,
            "size_bytes": video.size_bytes,
            "width": video.width,
            "height": video.height,
            "fps": video.fps,
            "frame_count": video.frame_count,
            "duration_sec": video.duration_sec,
            "sha256": video.sha256,
        },
        "recipe": recipe_detail(inspection.recipe),
        "needs_compressor_start": needs_compressor_start(inspection.recipe),
        "settings": {
            "start_sec": settings.start_sec,
            "end_sec": settings.end_sec,
            "compressor_start_sec": settings.compressor_start_sec,
            "sample_count": settings.sample_count,
        },
    }


def analysis_json(stored: StoredAnalysis) -> dict[str, Any]:
    layouts = {layout.glass_id: layout for layout in stored.images}
    analysis = stored.analysis
    return {
        "finished_at": analysis.finished_at,
        "times": list(analysis.times),
        "glasses": [
            {
                "glass_id": draft.glass_id,
                "y0": layouts[draft.glass_id].y0,
                "rows": layouts[draft.glass_id].rows,
                "pieces": layouts[draft.glass_id].pieces,
                "oil": line_json(draft.oil),
            }
            for draft in analysis.drafts
        ],
    }


def line_json(line: Line) -> dict[str, Any]:
    return {"ys": list(line.ys), "origins": [origin.value for origin in line.origins]}


def edits_json(edits: Edits) -> dict[str, Any]:
    return {
        "times": list(edits.times),
        "compressor_start_sec": edits.compressor_start_sec,
        "glasses": [
            {
                "glass_id": glass.glass_id,
                **{key: line_json(getattr(glass, key)) for key in LINE_KEYS},
                "cannot_judge": [{"start_sec": s.start_sec, "end_sec": s.end_sec} for s in glass.cannot_judge],
                "memos": [{"id": m.id, "time_sec": m.time_sec, "y": m.y, "text": m.text} for m in glass.memos],
            }
            for glass in edits.glasses
        ],
    }


def glass_state_json(state: GlassState) -> dict[str, Any]:
    cover = state.coverage
    return {
        "glass_id": state.glass_id,
        "levels": [{"state": run.value.value, "first": run.first, "end": run.end} for run in state.levels],
        "empty": [{"first": run.first, "end": run.end} for run in state.empty],
        "coverage": {
            "total": cover.total,
            "empty": cover.empty,
            "cannot_judge": cover.cannot_judge,
            "valid": cover.valid,
            "valid_ratio": cover.valid_ratio,
        },
    }


def dropped_json(dropped: Dropped) -> dict[str, Any]:
    return {
        "oil_samples": dropped.oil_samples,
        "foam_samples": dropped.foam_samples,
        "reference_samples": dropped.reference_samples,
        "stretches": dropped.stretches,
        "memos": dropped.memos,
        "glasses": list(dropped.glasses),
        "anything": dropped.anything,
    }


def source_check_json(check: SourceCheck) -> dict[str, Any]:
    return {"state": check.state.value, "message": check.message}


def parse_setup(body: Any) -> InspectionSetup:
    try:
        settings = body["settings"]
        compressor = settings["compressor_start_sec"]
        return InspectionSetup(
            inspection_id=_optional_text(body["inspection_id"]),
            video_id=_optional_text(body["video_id"]),
            recipe_id=_text(body["recipe_id"]),
            positions=tuple(
                GlassPosition(
                    _text(raw["id"]),
                    Ellipse(**{key: _number(raw["ellipse"][key]) for key in _ELLIPSE_NUMBERS}),
                    _number(raw["zero_line_y"]),
                )
                for raw in body["glasses"]
            ),
            settings=AnalysisSettings(
                _number(settings["start_sec"]),
                _number(settings["end_sec"]),
                None if compressor is None else _number(compressor),
            ),
            name=_optional_text(body.get("name")),
        )
    except (KeyError, TypeError, ValueError, AttributeError) as failure:
        raise BadRequest(f"검사 설정 요청 형식이 올바르지 않습니다: {failure}") from failure


def parse_edits(body: Any) -> Edits:
    try:
        raw = body["edits"]
        glasses = tuple(
            GlassEdits(
                _text(glass["glass_id"]),
                *(_line(glass[key]) for key in LINE_KEYS),
                cannot_judge=tuple(Stretch(_number(s["start_sec"]), _number(s["end_sec"])) for s in glass["cannot_judge"]),
                memos=tuple(
                    Memo(_text(m["id"]), _number(m["time_sec"]), _optional_number(m["y"]), _text(m["text"]))
                    for m in glass["memos"]
                ),
            )
            for glass in raw["glasses"]
        )
        return Edits(tuple(_number(t) for t in raw["times"]), glasses, _optional_number(raw["compressor_start_sec"]))
    except (KeyError, TypeError, ValueError, AttributeError) as failure:
        raise BadRequest(f"편집 요청 형식이 올바르지 않습니다: {failure}") from failure


def parse_points(body: Any) -> tuple[str, tuple[tuple[int, float], ...]]:
    try:
        return _text(body["glass_id"]), tuple((_index(p["index"]), _number(p["y"])) for p in body["points"])
    except (KeyError, TypeError, ValueError, AttributeError) as failure:
        raise BadRequest(f"점 잇기 요청 형식이 올바르지 않습니다: {failure}") from failure


def byte_range(header: str | None, size: int) -> tuple[int, int] | None:
    """The one byte range a player asks for, as [start, end); None serves the whole file.

    Other forms of the header are ignored, as RFC 9110 §14.2 allows.
    """
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", (header or "").strip())
    if match is None or match.groups() == ("", ""):
        return None
    first, last = match.groups()
    if first == "":
        if int(last) == 0:
            raise RangeNotSatisfiable()
        return max(0, size - int(last)), size
    start = int(first)
    if last != "" and int(last) < start:
        return None
    if start >= size:
        raise RangeNotSatisfiable()
    return start, size if last == "" else min(size, int(last) + 1)


def parse_draft(body: Any) -> RecipeDraft:
    try:
        recipe_id = body["id"]
        if recipe_id is not None:
            recipe_id = _text(recipe_id)
        reference = body.get("reference")
        if reference is not None:
            reference = ReferenceChoice(_text(reference["video_id"]), _number(reference["time_sec"]))
        return RecipeDraft(
            id=recipe_id,
            name=_text(body["name"]),
            glasses=tuple(_glass(raw) for raw in body["glasses"]),
            reference=reference,
        )
    except (KeyError, TypeError, ValueError, AttributeError) as failure:
        raise BadRequest(f"Recipe 요청 형식이 올바르지 않습니다: {failure}") from failure


def _glass(raw: dict[str, Any]) -> Glass:
    rule = raw["judgment_rule"]
    return Glass(
        id=_text(raw["id"]),
        name=_text(raw["name"]),
        ellipse=Ellipse(**{key: _number(raw["ellipse"][key]) for key in _ELLIPSE_NUMBERS}),
        zero_line_y=_number(raw["zero_line_y"]),
        judgment_rule=JudgmentRule(JudgmentMode(rule["mode"]), **{key: _number(rule[key]) for key in _RULE_NUMBERS}),
    )


def _text(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("expected text")
    return value


def _optional_text(value: Any) -> str | None:
    return None if value is None else _text(value)


def _optional_number(value: Any) -> float | None:
    return None if value is None else _number(value)


def _index(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("expected a whole number")
    return value


def _line(raw: Any) -> Line:
    return Line(tuple(_optional_number(y) for y in raw["ys"]), tuple(SampleOrigin(_text(o)) for o in raw["origins"]))


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        raise TypeError("expected a finite number")
    return float(value)


# ---- routes -------------------------------------------------------------------------

Route = tuple[str, re.Pattern[str], Callable[..., Response]]


def routes(ctx: ApiContext) -> list[Route]:
    recipes, inspections, editing, videos, jobs = ctx.recipes, ctx.inspections, ctx.editing, ctx.videos, ctx.jobs

    def list_recipes(_query, _body) -> Response:
        listing = recipes.list()
        return json_response(
            {
                "folder": str(recipes.store.location),
                "recipes": [recipe_summary(r) for r in listing.recipes],
                "unreadable": [{"file": name, "reason": reason} for name, reason in listing.unreadable],
            }
        )

    def get_recipe(_query, _body, recipe_id) -> Response:
        return json_response(recipe_detail(recipes.load(recipe_id)))

    def reference_jpeg(_query, _body, recipe_id) -> Response:
        return Response(200, recipes.load(recipe_id).reference_frame.jpeg, "image/jpeg")

    def save_recipe(_query, body) -> Response:
        result = recipes.save(parse_draft(body))
        if result.recipe is None:
            return json_response({"problems": problems_json(result.problems)}, 422)
        return json_response(recipe_detail(result.recipe))

    def check_recipe(_query, body) -> Response:
        return json_response({"problems": problems_json(recipes.check(parse_draft(body)))})

    def defaults(_query, _body) -> Response:
        rule = JudgmentRule()
        return json_response(
            {"judgment_rule": {"mode": rule.mode.value, **{key: getattr(rule, key) for key in _RULE_NUMBERS}}}
        )

    def open_folder(_query, _body) -> Response:
        recipes.open_folder()
        return json_response({"ok": True})

    def pick_video(_query, _body) -> Response:
        path = recipes.pick_sample_video()
        return json_response({"path": None if path is None else str(path)})

    def open_video(_query, body) -> Response:
        try:
            path = Path(_text(body["path"]))
            recipe_id = body.get("recipe_id")
            recipe_id = None if recipe_id is None else _text(recipe_id)
        except (KeyError, TypeError, AttributeError) as failure:
            raise BadRequest(f"영상 요청 형식이 올바르지 않습니다: {failure}") from failure
        return json_response(video_json(recipes.open_sample_video(path, recipe_id)))

    def frame(query, _body, video_id) -> Response:
        try:
            time_sec = float(query.get("t", ["0"])[0])
            max_size = int(query["max"][0]) if "max" in query else None
            crop = Region(*(int(n) for n in query["crop"][0].split(","))) if "crop" in query else None
        except (ValueError, TypeError) as failure:
            raise BadRequest(str(failure)) from failure
        if not math.isfinite(time_sec):
            raise BadRequest("t must be finite")
        try:
            shown = videos.frame(video_id, time_sec, max_size=max_size, crop=crop)
        except ValueError as failure:
            raise BadRequest(str(failure)) from failure
        headers = (("X-Frame-Index", str(shown.index)), ("X-Frame-Time", f"{shown.time_sec:.6f}"))
        if shown.region is not None:
            r = shown.region
            headers += (("X-Frame-Region", f"{r.x},{r.y},{r.width},{r.height}"),)
        return Response(200, shown.jpeg, "image/jpeg", headers)

    def close_video(_query, _body, video_id) -> Response:
        videos.close(video_id)
        return json_response({"ok": True})

    def list_inspections(_query, _body) -> Response:
        listing = inspections.list()
        return json_response(
            {
                "folder": str(inspections.store.location),
                "inspections": [inspection_summary(entry) for entry in listing.inspections],
                "unreadable": [{"folder": name, "reason": reason} for name, reason in listing.unreadable],
                "job": jobs.running(),
            }
        )

    def open_inspections_folder(_query, _body) -> Response:
        inspections.open_folder()
        return json_response({"ok": True})

    def recipe_choices(query, _body) -> Response:
        if "video_id" not in query:
            raise BadRequest("video_id가 필요합니다.")
        result = inspections.recipe_choices(query["video_id"][0])
        return json_response(
            {
                "recipes": [
                    {
                        **recipe_summary(choice.recipe),
                        "problem": choice.problem,
                        "needs_compressor_start": needs_compressor_start(choice.recipe),
                    }
                    for choice in result.choices
                ],
                "unreadable": [{"file": name, "reason": reason} for name, reason in result.unreadable],
            }
        )

    def check_setup(_query, body) -> Response:
        setup = parse_setup(body)
        problems = inspections.check(setup)
        dropped = Dropped() if problems else inspections.dropped(setup)
        return json_response({"problems": problems_json(problems), "dropped": dropped_json(dropped)})

    def start_analysis(_query, body) -> Response:
        setup = parse_setup(body)
        if jobs.running() is not None:
            raise JobsBusy("다른 분석이 진행 중입니다.")
        result = inspections.prepare(setup)
        if result.inspection is None:
            return json_response({"problems": problems_json(result.problems)}, 422)
        inspection = result.inspection
        job = jobs.start(inspection.id, lambda progress, cancelled: inspections.analyse(inspection, progress, cancelled))
        return json_response({"inspection": inspection_detail(inspection), "job": job})

    def get_inspection(_query, _body, inspection_id) -> Response:
        return json_response(inspection_detail(inspections.load(inspection_id)))

    def get_analysis(_query, _body, inspection_id) -> Response:
        stored = inspections.result(inspection_id)
        if stored is None:
            return error(404, "분석 결과가 없습니다.")
        return json_response(analysis_json(stored))

    def open_inspection_video(_query, _body, inspection_id) -> Response:
        return json_response(video_json(inspections.open_video(inspection_id)))

    def image_piece(_query, _body, inspection_id, glass_id, kind, index) -> Response:
        return Response(200, inspections.image_piece(inspection_id, glass_id, kind, int(index)), "image/png")

    def open_edits(_query, _body, inspection_id) -> Response:
        opened = editing.open(inspection_id)
        return json_response(
            {
                "saved_at": opened.saved_at,
                "unsaved": opened.unsaved,
                "edits": edits_json(opened.edits),
                "glasses": [glass_state_json(s) for s in editing.states(inspection_id, opened.edits)],
            }
        )

    def save_edits(_query, body, inspection_id) -> Response:
        edits = parse_edits(body)
        running = jobs.running()
        if running is not None and running["inspection_id"] == inspection_id:
            raise JobsBusy("이 검사를 다시 분석하는 중에는 저장할 수 없습니다.")
        return json_response({"saved_at": editing.save(inspection_id, edits)})

    def edit_states(_query, body, inspection_id) -> Response:
        states = editing.states(inspection_id, parse_edits(body))
        return json_response({"glasses": [glass_state_json(s) for s in states]})

    def point_line(_query, body, inspection_id) -> Response:
        glass_id, points = parse_points(body)
        drawn = editing.point_line(inspection_id, glass_id, points)
        return json_response({"first": drawn.first, "ys": list(drawn.ys)})

    def source_check(_query, _body, inspection_id) -> Response:
        return json_response(source_check_json(editing.source_check(inspection_id)))

    def check_source_again(_query, _body, inspection_id) -> Response:
        return json_response(source_check_json(editing.check_source(inspection_id)))

    def mark_unsaved(_query, body) -> Response:
        unsaved = body.get("unsaved") if isinstance(body, dict) else None
        if not isinstance(unsaved, bool):
            raise BadRequest("unsaved는 true 또는 false여야 합니다.")
        editing.mark_unsaved(unsaved)
        return json_response({"ok": True})

    def job_status(_query, _body, job_id) -> Response:
        return json_response(jobs.status(job_id))

    def cancel_job(_query, _body, job_id) -> Response:
        return json_response(jobs.cancel(job_id))

    segment = r"([^/]+)"
    return [
        ("GET", re.compile(r"/api/inspections"), list_inspections),
        ("POST", re.compile(r"/api/inspections/open-folder"), open_inspections_folder),
        ("GET", re.compile(r"/api/inspections/recipe-choices"), recipe_choices),
        ("POST", re.compile(r"/api/inspections/check"), check_setup),
        ("POST", re.compile(r"/api/inspections/start"), start_analysis),
        ("GET", re.compile(rf"/api/inspections/{segment}"), get_inspection),
        ("GET", re.compile(rf"/api/inspections/{segment}/analysis"), get_analysis),
        ("POST", re.compile(rf"/api/inspections/{segment}/video"), open_inspection_video),
        ("GET", re.compile(rf"/api/inspections/{segment}/edits"), open_edits),
        ("POST", re.compile(rf"/api/inspections/{segment}/edits"), save_edits),
        ("POST", re.compile(rf"/api/inspections/{segment}/edits/states"), edit_states),
        ("POST", re.compile(rf"/api/inspections/{segment}/point-line"), point_line),
        ("GET", re.compile(rf"/api/inspections/{segment}/source-check"), source_check),
        ("POST", re.compile(rf"/api/inspections/{segment}/source-check"), check_source_again),
        (
            "GET",
            re.compile(rf"/api/inspections/{segment}/images/{segment}/(context|background)-(\d+)\.png"),
            image_piece,
        ),
        ("POST", re.compile(r"/api/editor/unsaved"), mark_unsaved),
        ("GET", re.compile(rf"/api/jobs/{segment}"), job_status),
        ("POST", re.compile(rf"/api/jobs/{segment}/cancel"), cancel_job),
        ("GET", re.compile(r"/api/recipes"), list_recipes),
        ("POST", re.compile(r"/api/recipes"), save_recipe),
        ("POST", re.compile(r"/api/recipes/check"), check_recipe),
        ("POST", re.compile(r"/api/recipes/open-folder"), open_folder),
        ("GET", re.compile(r"/api/defaults"), defaults),
        ("GET", re.compile(rf"/api/recipes/{segment}"), get_recipe),
        ("GET", re.compile(rf"/api/recipes/{segment}/reference\.jpg"), reference_jpeg),
        ("POST", re.compile(r"/api/videos/pick"), pick_video),
        ("POST", re.compile(r"/api/videos"), open_video),
        ("GET", re.compile(rf"/api/videos/{segment}/frame"), frame),
        ("DELETE", re.compile(rf"/api/videos/{segment}"), close_video),
    ]


MediaRoute = tuple[re.Pattern[str], Callable[..., Response]]


def media_routes(ctx: ApiContext) -> list[MediaRoute]:
    """Files the page's own elements load: a <video> cannot send the token header, so it comes in the query."""

    def source_video(range_header, inspection_id) -> Response:
        path = ctx.editing.source_file(inspection_id)
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return error(404, f"원본 영상을 찾을 수 없습니다: {path}")
        kind = VIDEO_TYPES.get(path.suffix.lower(), "application/octet-stream")
        try:
            span = byte_range(range_header, size)
        except RangeNotSatisfiable:
            return Response(416, b"", kind, (("Content-Range", f"bytes */{size}"),))
        if span is None:
            return Response(200, b"", kind, (("Accept-Ranges", "bytes"),), FilePart(path, 0, size))
        start, end = span
        headers = (("Accept-Ranges", "bytes"), ("Content-Range", f"bytes {start}-{end - 1}/{size}"))
        return Response(206, b"", kind, headers, FilePart(path, start, end - start))

    return [(re.compile(r"/media/inspections/([^/]+)/source"), source_video)]


def make_handler(ctx: ApiContext) -> type[BaseHTTPRequestHandler]:
    table = routes(ctx)
    media = media_routes(ctx)
    web_folder = ctx.web_folder.resolve()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args) -> None:
            pass

        def do_GET(self) -> None:
            self._handle("GET")

        def do_POST(self) -> None:
            self._handle("POST")

        def do_DELETE(self) -> None:
            self._handle("DELETE")

        def _handle(self, method: str) -> None:
            url = urlparse(self.path)
            try:
                response = self._dispatch(method, url.path, parse_qs(url.query))
            except BadRequest as failure:
                response = error(400, str(failure))
            except (RecipeNotFound, UnknownVideo, InspectionNotFound, UnknownJob) as failure:
                response = error(404, str(failure))
            except (VideoUnreadable, VideoDoesNotFit, UnreadableAnalysis, UnreadableEdits) as failure:
                response = error(422, str(failure))
            except (NotAnalysed, JobsBusy) as failure:
                response = error(409, str(failure))
            except (InvalidSetup, InvalidEdits) as failure:
                response = error(400, str(failure))
            except DesktopUnavailable as failure:
                response = error(501, str(failure))
            except Exception as failure:  # noqa: BLE001 - report every failure to the UI
                traceback.print_exc(file=sys.stderr)
                response = error(500, f"{type(failure).__name__}: {failure}")
            self._send(response)

        def _dispatch(self, method: str, path: str, query: dict[str, list[str]]) -> Response:
            if not self._host_is_local():
                return error(403, "forbidden host")
            if path.startswith("/media/"):
                return self._media(method, path, query)
            if not path.startswith("/api/"):
                return self._static(method, path) if method == "GET" else error(405, "method not allowed")
            if self.headers.get(TOKEN_HEADER) != ctx.token:
                return error(403, "missing or wrong token")
            body = self._body() if method == "POST" else None
            for route_method, pattern, function in table:
                match = pattern.fullmatch(path)
                if match and route_method == method:
                    return function(query, body, *(unquote(group) for group in match.groups()))
            return error(404, "not found")

        def _media(self, method: str, path: str, query: dict[str, list[str]]) -> Response:
            if query.get("token") != [ctx.token]:
                return error(403, "missing or wrong token")
            for pattern, function in media:
                match = pattern.fullmatch(path)
                if match and method == "GET":
                    return function(self.headers.get("Range"), *(unquote(group) for group in match.groups()))
            return error(404, "not found")

        def _host_is_local(self) -> bool:
            port = self.server.server_address[1]
            return self.headers.get("Host") in {f"127.0.0.1:{port}", f"localhost:{port}"}

        def _body(self) -> Any:
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY_BYTES:
                raise BadRequest("요청이 너무 큽니다.")
            try:
                return json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError as failure:
                raise BadRequest("JSON 형식이 아닙니다.") from failure

        def _static(self, method: str, path: str) -> Response:
            name = "index.html" if path in ("/", "/index.html") else path.removeprefix("/web/")
            target = (web_folder / name).resolve()
            if web_folder not in target.parents or not target.is_file() or target.suffix not in STATIC_TYPES:
                return error(404, "not found")
            return Response(200, target.read_bytes(), STATIC_TYPES[target.suffix])

        def _send(self, response: Response) -> None:
            part = response.file
            self.send_response(response.status)
            self.send_header("Content-Type", response.content_type)
            self.send_header("Content-Length", str(len(response.body) if part is None else part.length))
            self.send_header("Cache-Control", "no-store")
            for key, value in response.headers:
                self.send_header(key, value)
            self.end_headers()
            if part is None:
                self.wfile.write(response.body)
                return
            try:
                with part.path.open("rb") as source:
                    source.seek(part.start)
                    left = part.length
                    while left > 0 and (chunk := source.read(min(COPY_CHUNK, left))):
                        self.wfile.write(chunk)
                        left -= len(chunk)
            except ConnectionError:
                pass  # the player stopped reading (Windows: ConnectionAbortedError); it asks again with another range

    return Handler
