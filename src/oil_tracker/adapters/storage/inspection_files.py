"""Inspection folders: docs/20-architecture/inspection-folder.md."""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

from oil_tracker.application.ports import (
    GlassImages,
    ImageLayout,
    InspectionEntry,
    InspectionListing,
    InspectionNotFound,
    StoredAnalysis,
    StoredEdits,
    UnreadableAnalysis,
    UnreadableEdits,
)
from oil_tracker.domain.edits import Decision, Edits, GlassEdits, Memo, Stretch
from oil_tracker.domain.enums import InspectionState, SampleOrigin, Verdict
from oil_tracker.domain.inspection import Analysis, AnalysisSettings, GlassDraft, Inspection, SourceVideo
from oil_tracker.domain.line import Line

from .files import atomic_write_text
from .recipe_files import UnreadableRecipe, recipe_from_json, recipe_to_json
from .values import integer, number, optional, safe_stem, text

INSPECTION_FORMAT = "oil-level-tracker-inspection"
ANALYSIS_FORMAT = "oil-level-tracker-analysis"
EDITS_FORMAT = "oil-level-tracker-edits"
SCHEMA_VERSION = 1
EDITS_SCHEMA_VERSION = 2  # 2 adds each Glass's decision (V2-4); 1 still reads, as undecided
INSPECTION_FILE = "inspection.json"
RECIPE_FILE = "recipe.json"
CACHE = "cache"
ANALYSIS_FILE = "analysis.json"
EDITS_FILE = "edits.json"
LINE_KEYS = ("oil", "foam", "reference")
IMAGE_KINDS = ("context", "background")
_SAFE_ID = re.compile(r"^[A-Za-z0-9-]{1,64}$")


class UnreadableInspection(ValueError):
    pass


# ---- inspection.json ----------------------------------------------------------------------


def inspection_to_json(inspection: Inspection) -> str:
    video, settings = inspection.video, inspection.settings
    data = {
        "format": INSPECTION_FORMAT,
        "schema_version": SCHEMA_VERSION,
        "id": inspection.id,
        "name": inspection.name,
        "created_at": inspection.created_at,
        "video": {
            "path": video.path,
            "name": video.name,
            "size_bytes": video.size_bytes,
            "width": video.width,
            "height": video.height,
            "fps": video.fps,
            "frame_count": video.frame_count,
            "sha256": video.sha256,
        },
        "settings": {
            "start_sec": settings.start_sec,
            "end_sec": settings.end_sec,
            "compressor_start_sec": settings.compressor_start_sec,
        },
        "state": inspection.state.value,
        "failure": inspection.failure,
    }
    return json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def inspection_from_json(inspection_text: str, recipe_text: str) -> Inspection:
    data = _document(inspection_text, INSPECTION_FORMAT, "검사", UnreadableInspection)
    try:
        recipe = recipe_from_json(recipe_text)
    except UnreadableRecipe as error:
        raise UnreadableInspection(f"Recipe 사본: {error}") from error
    try:
        video, settings = data["video"], data["settings"]
        return Inspection(
            id=text(data["id"]),
            created_at=text(data["created_at"]),
            video=SourceVideo(
                path=text(video["path"]),
                name=text(video["name"]),
                size_bytes=integer(video["size_bytes"]),
                width=integer(video["width"]),
                height=integer(video["height"]),
                fps=number(video["fps"]),
                frame_count=integer(video["frame_count"]),
                sha256=optional(text, video["sha256"]),
            ),
            recipe=recipe,
            settings=AnalysisSettings(
                start_sec=number(settings["start_sec"]),
                end_sec=number(settings["end_sec"]),
                compressor_start_sec=optional(number, settings["compressor_start_sec"]),
            ),
            state=InspectionState(data["state"]),
            failure=optional(text, data["failure"]),
            name=optional(text, data.get("name")),  # absent in files written before names
        )
    except (KeyError, TypeError, ValueError) as error:
        raise UnreadableInspection(f"검사 내용이 올바르지 않습니다: {error}") from error


# ---- cache/analysis.json --------------------------------------------------------------------


def analysis_to_json(analysis: Analysis, images: Sequence[GlassImages]) -> str:
    layout = {image.glass_id: image for image in images}
    data = {
        "format": ANALYSIS_FORMAT,
        "schema_version": SCHEMA_VERSION,
        "finished_at": analysis.finished_at,
        "times": list(analysis.times),
        "glasses": [
            {
                "glass_id": draft.glass_id,
                "y0": layout[draft.glass_id].y0,
                "rows": layout[draft.glass_id].rows,
                "pieces": len(layout[draft.glass_id].context_png),
                "oil": _line_json(draft.oil),
            }
            for draft in analysis.drafts
        ],
    }
    return json.dumps(data, ensure_ascii=False, allow_nan=False) + "\n"


def analysis_from_json(analysis_text: str) -> StoredAnalysis:
    data = _document(analysis_text, ANALYSIS_FORMAT, "분석", UnreadableAnalysis)
    try:
        drafts, layouts = [], []
        for raw in data["glasses"]:
            glass_id = text(raw["glass_id"])
            drafts.append(GlassDraft(glass_id, _line_from(raw["oil"])))
            layouts.append(ImageLayout(glass_id, integer(raw["y0"]), integer(raw["rows"]), integer(raw["pieces"])))
        analysis = Analysis(tuple(number(t) for t in data["times"]), tuple(drafts), text(data["finished_at"]))
        return StoredAnalysis(analysis, tuple(layouts))
    except (KeyError, TypeError, ValueError) as error:
        raise UnreadableAnalysis(f"분석 내용이 올바르지 않습니다: {error}") from error


# ---- edits.json ------------------------------------------------------------------------------


def edits_to_json(edits: Edits, saved_at: str) -> str:
    data = {
        "format": EDITS_FORMAT,
        "schema_version": EDITS_SCHEMA_VERSION,
        "saved_at": saved_at,
        "times": list(edits.times),
        "compressor_start_sec": edits.compressor_start_sec,
        "glasses": [
            {
                "glass_id": glass.glass_id,
                **{key: _line_json(getattr(glass, key)) for key in LINE_KEYS},
                "cannot_judge": [{"start_sec": s.start_sec, "end_sec": s.end_sec} for s in glass.cannot_judge],
                "memos": [{"id": m.id, "time_sec": m.time_sec, "y": m.y, "text": m.text} for m in glass.memos],
                "decision": _decision_json(glass.decision),
            }
            for glass in edits.glasses
        ],
    }
    return json.dumps(data, ensure_ascii=False, allow_nan=False) + "\n"


def edits_from_json(edits_text: str) -> StoredEdits:
    data = _document(edits_text, EDITS_FORMAT, "편집", UnreadableEdits, (1, EDITS_SCHEMA_VERSION))
    first = data["schema_version"] == 1
    try:
        glasses = tuple(
            GlassEdits(
                text(raw["glass_id"]),
                *(_line_from(raw[key]) for key in LINE_KEYS),
                cannot_judge=tuple(Stretch(number(s["start_sec"]), number(s["end_sec"])) for s in raw["cannot_judge"]),
                memos=tuple(
                    Memo(text(m["id"]), number(m["time_sec"]), optional(number, m["y"]), text(m["text"]))
                    for m in raw["memos"]
                ),
                decision=Decision() if first else _decision_from(raw["decision"]),
            )
            for raw in data["glasses"]
        )
        edits = Edits(tuple(number(t) for t in data["times"]), glasses, optional(number, data["compressor_start_sec"]))
        return StoredEdits(edits, text(data["saved_at"]))
    except (KeyError, TypeError, ValueError) as error:
        raise UnreadableEdits(f"편집 내용이 올바르지 않습니다: {error}") from error


def _decision_json(decision: Decision) -> dict[str, Any]:
    override = None if decision.override is None else decision.override.value
    return {"override": override, "reason": decision.reason, "checked_at": decision.checked_at}


def _decision_from(raw: Any) -> Decision:
    return Decision(optional(lambda v: Verdict(text(v)), raw["override"]), text(raw["reason"]), optional(text, raw["checked_at"]))


def _line_json(line: Line) -> dict[str, Any]:
    return {"ys": list(line.ys), "origins": [origin.value for origin in line.origins]}


def _line_from(raw: Any) -> Line:
    return Line(tuple(optional(number, y) for y in raw["ys"]), tuple(SampleOrigin(o) for o in raw["origins"]))


def _document(
    raw: str, expected_format: str, label: str, failure: type[ValueError], versions: tuple[int, ...] = (SCHEMA_VERSION,)
) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise failure("JSON 형식이 아닙니다.") from error
    if not isinstance(data, dict) or data.get("format") != expected_format:
        raise failure(f"{label} 파일이 아닙니다.")
    version = data.get("schema_version")
    if type(version) is not int or version not in versions:
        raise failure(f"지원하지 않는 {label} 파일 버전입니다: {version!r}")
    return data


# ---- folders --------------------------------------------------------------------------------


def folder_name_for(inspection: Inspection) -> str:
    """The user's inspection name, or YYYYMMDD-HHMM_<video name> in local time (Product SSOT §8)."""
    if inspection.name is not None:
        name = safe_stem(inspection.name)
        return "_" + name if name.startswith(".") else name  # the listing skips a folder whose name starts with a dot
    created = datetime.fromisoformat(inspection.created_at).astimezone()
    return f"{created:%Y%m%d-%H%M}_{safe_stem(Path(inspection.video.name).stem)}"


class InspectionFolders:
    """The Inspections folder. Implements application.ports.InspectionStore."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder

    @property
    def location(self) -> Path:
        return self.folder

    def create(self, inspection: Inspection) -> str:
        base = folder_name_for(inspection)
        self.folder.mkdir(parents=True, exist_ok=True)
        for attempt in range(1, 1000):
            name = base if attempt == 1 else f"{base}_{attempt}"
            try:
                (self.folder / name).mkdir()
            except FileExistsError:
                continue
            self._write(self.folder / name, inspection)
            return name
        raise OSError(f"검사 폴더 이름을 정하지 못했습니다: {base}")

    def list_inspections(self) -> InspectionListing:
        entries: list[InspectionEntry] = []
        unreadable: list[tuple[str, str]] = []
        seen: set[str] = set()
        for path, result in self._read_all():
            if isinstance(result, str):
                unreadable.append((path.name, result))
            elif result.id in seen:
                unreadable.append((path.name, "다른 폴더와 검사 ID가 같습니다."))
            else:
                seen.add(result.id)
                entries.append(InspectionEntry(path.name, result))
        entries.sort(key=lambda entry: entry.inspection.created_at, reverse=True)
        return InspectionListing(tuple(entries), tuple(unreadable))

    def load(self, inspection_id: str) -> Inspection:
        return self._find(inspection_id)[1]

    def save(self, inspection: Inspection) -> None:
        self._write(self._find(inspection.id)[0], inspection)

    def save_analysis(self, inspection_id: str, analysis: Analysis, images: Sequence[GlassImages]) -> None:
        folder = self._find(inspection_id)[0]
        if {image.glass_id for image in images} != {draft.glass_id for draft in analysis.drafts}:
            raise ValueError("Every analysed Glass needs its images.")
        partial = folder / (CACHE + ".partial")
        shutil.rmtree(partial, ignore_errors=True)
        for image in images:
            _check_id(image.glass_id)
            glass_folder = partial / image.glass_id
            glass_folder.mkdir(parents=True)
            for kind, pieces in zip(IMAGE_KINDS, (image.context_png, image.background_png)):
                for index, data in enumerate(pieces):
                    (glass_folder / _piece_name(kind, index)).write_bytes(data)
        (partial / ANALYSIS_FILE).write_text(analysis_to_json(analysis, images), encoding="utf-8")
        cache = folder / CACHE
        shutil.rmtree(cache, ignore_errors=True)
        partial.rename(cache)

    def load_analysis(self, inspection_id: str) -> StoredAnalysis | None:
        path = self._find(inspection_id)[0] / CACHE / ANALYSIS_FILE
        if not path.is_file():
            return None
        return analysis_from_json(path.read_text(encoding="utf-8"))

    def clear_analysis(self, inspection_id: str) -> None:
        folder = self._find(inspection_id)[0]
        for name in (CACHE, CACHE + ".partial"):
            shutil.rmtree(folder / name, ignore_errors=True)

    def image_piece(self, inspection_id: str, glass_id: str, kind: str, index: int) -> bytes:
        _check_id(glass_id)
        if kind not in IMAGE_KINDS or index < 0:
            raise InspectionNotFound(f"그림을 찾을 수 없습니다: {kind} {index}")
        path = self._find(inspection_id)[0] / CACHE / glass_id / _piece_name(kind, index)
        try:
            return path.read_bytes()
        except FileNotFoundError as error:
            raise InspectionNotFound(f"그림을 찾을 수 없습니다: {kind} {index}") from error

    def save_edits(self, inspection_id: str, edits: Edits, saved_at: str) -> None:
        atomic_write_text(self._find(inspection_id)[0] / EDITS_FILE, edits_to_json(edits, saved_at))

    def load_edits(self, inspection_id: str) -> StoredEdits | None:
        path = self._find(inspection_id)[0] / EDITS_FILE
        if not path.is_file():
            return None
        return edits_from_json(path.read_text(encoding="utf-8"))

    def _write(self, folder: Path, inspection: Inspection) -> None:
        atomic_write_text(folder / RECIPE_FILE, recipe_to_json(inspection.recipe))
        atomic_write_text(folder / INSPECTION_FILE, inspection_to_json(inspection))

    def _find(self, inspection_id: str) -> tuple[Path, Inspection]:
        for path, result in self._read_all():
            if isinstance(result, Inspection) and result.id == inspection_id:
                return path, result
        raise InspectionNotFound(f"검사를 찾을 수 없습니다: {inspection_id}")

    def _read_all(self) -> list[tuple[Path, Inspection | str]]:
        if not self.folder.is_dir():
            return []
        found: list[tuple[Path, Inspection | str]] = []
        for path in sorted(p for p in self.folder.iterdir() if p.is_dir() and not p.name.startswith(".")):
            try:
                inspection_text = (path / INSPECTION_FILE).read_text(encoding="utf-8")
                _document(inspection_text, INSPECTION_FORMAT, "검사", UnreadableInspection)  # its reason first
                recipe_text = (path / RECIPE_FILE).read_text(encoding="utf-8")
                found.append((path, inspection_from_json(inspection_text, recipe_text)))
            except UnreadableInspection as error:
                found.append((path, str(error)))
            except (OSError, UnicodeDecodeError) as error:
                found.append((path, f"파일을 읽을 수 없습니다: {error}"))
        return found


def _piece_name(kind: str, index: int) -> str:
    return f"{kind}-{index:03d}.png"


def _check_id(glass_id: str) -> None:
    if not _SAFE_ID.match(glass_id):
        raise InspectionNotFound(f"Glass ID가 올바르지 않습니다: {glass_id!r}")
