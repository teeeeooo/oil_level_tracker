from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
from pathlib import Path

import cv2
import numpy as np

from benchmark_fixtures import write_catalog
from oil_tracker.adapters.storage.json_truth_repository import build_truth_bundle_identity
from oil_tracker.adapters.storage.regression_fixture_exporter import RegressionFixtureExporter
from oil_tracker.application.services.user_truth import TruthFrameContext, UserTruthService
from oil_tracker.domain.detector_benchmark import BenchmarkCategory
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.user_truth import TruthDisposition, TruthErrorType
from user_truth_fixtures import make_truth_bundle

FIXED_TIME = datetime(2026, 7, 21, 15, 0, 0, tzinfo=timezone.utc)
S5A_SETTING_FIELDS = (
    "foam_lightness_threshold",
    "foam_max_chroma",
    "foam_min_whiteness_ratio",
    "foam_max_glare_overlap_ratio",
    "foam_min_evidence_score",
    "foam_strong_evidence_score",
    "foam_persistence_frames",
    "foam_max_front_jump_px",
)
S5B_SETTING_FIELDS = (
    "oil_consensus_tolerance_px",
    "oil_min_consensus_sources",
    "oil_min_polarity_score",
    "oil_no_interface_min_score",
    "oil_path_window",
    "oil_path_beam_width",
    "oil_path_min_margin",
    "oil_tracker_update_confidence",
    "oil_reacquire_frames",
)


@dataclass(frozen=True)
class ControlledScene:
    case_id: str
    category: BenchmarkCategory
    timestamp: float
    frame: np.ndarray
    fill_state: FillState
    oil_y: float | None = None
    foam_present: bool = False
    foam_y: float | None = None
    sequence_id: str | None = None
    sequence_order: int | None = None


class ControlledVideoReader:
    def __init__(self, source, metadata, scenes):
        self.path = str(source)
        self.metadata = metadata
        self.scenes = {round(scene.timestamp, 6): scene for scene in scenes}
        self.closed = False

    def read_at(self, timestamp):
        scene = self.scenes[round(float(timestamp), 6)]
        return scene.frame.copy(), int(round(scene.timestamp * self.metadata.fps)), scene.timestamp

    def close(self):
        self.closed = True


def generate_controlled_foam_dataset(tmp_path: Path):
    bundle = make_truth_bundle(tmp_path / "controlled")
    _make_recipe_snapshot_base_compatible(bundle)
    scenes = controlled_scenes()
    service = UserTruthService()
    identity = build_truth_bundle_identity(bundle)
    truth_set = service.create_set(identity)
    annotations = []
    glass = bundle.recipe.glasses[0]
    for index, scene in enumerate(scenes, 1):
        context = TruthFrameContext(
            glass.id,
            glass.name,
            scene.timestamp,
            scene.timestamp,
            int(round(scene.timestamp * bundle.source_metadata.fps)),
        )
        annotation = service.make_annotation(
            truth_set,
            identity,
            glass,
            context,
            TruthDisposition.CORRECTED,
            truth_fill_state=scene.fill_state,
            oil_source_y=scene.oil_y,
            foam_present=scene.foam_present,
            foam_source_y=scene.foam_y,
            error_types=(TruthErrorType.OTHER,),
            note=f"controlled scene contract: {scene.case_id}",
            official_reference=service.official_reference(bundle, glass, scene.timestamp),
        )
        annotation = replace(
            annotation,
            annotation_id=f"controlled-{index:03d}-{scene.case_id}",
            revision=index,
        )
        truth_set.upsert(annotation)
        annotations.append(annotation)
    reader = ControlledVideoReader(bundle.source_video_path, bundle.source_metadata, scenes)
    exporter = RegressionFixtureExporter(lambda _path: reader, clock=lambda: FIXED_TIME)
    result = exporter.export(
        bundle,
        truth_set,
        annotations,
        tmp_path / "controlled-output",
        source_video_path=bundle.source_video_path,
    )
    assert reader.closed
    write_catalog(
        result.dataset_path,
        [
            {
                "fixture_id": exporter.deterministic_fixture_id(bundle, annotation),
                "category": scene.category.value,
                "sequence_id": scene.sequence_id,
                "sequence_order": scene.sequence_order,
            }
            for annotation, scene in zip(annotations, scenes, strict=True)
        ],
    )
    return result.dataset_path, scenes


def _make_recipe_snapshot_base_compatible(bundle) -> None:
    """Remove additive detector keys before fixture hashes are generated.

    The S5-B controlled comparison intentionally feeds identical fixture bytes to
    the S5-A base detector and the S5-B feature detector. Removing additive S5-A
    and S5-B keys here lets each checkout restore its own dataclass defaults while
    preserving the version-1 recipe and regression fixture schemas.
    """

    recipe_path = Path(
        bundle.files.get("recipe_snapshot", bundle.root / "recipe_snapshot.oilrecipe")
    )
    payload = json.loads(recipe_path.read_text(encoding="utf-8"))
    for glass in payload.get("glasses", []):
        settings = glass.get("detector_settings", {})
        for field_name in S5A_SETTING_FIELDS + S5B_SETTING_FIELDS:
            settings.pop(field_name, None)
    recipe_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def controlled_scenes():
    size = (320, 240)
    times = iter(1.0 + index * 0.25 for index in range(20))
    rows = []

    def add(case_id, category, frame, fill_state, **kwargs):
        rows.append(ControlledScene(case_id, category, next(times), frame, fill_state, **kwargs))

    add("white-foam", BenchmarkCategory.WHITE_FOAM, _foam(*size, 225, False), FillState.FULL_WITH_FOAM, foam_present=True, foam_y=120.0)
    add("low-light-foam", BenchmarkCategory.WHITE_FOAM, _foam(*size, 170, False), FillState.FULL_WITH_FOAM, foam_present=True, foam_y=120.0)
    add("partial-foam", BenchmarkCategory.WHITE_FOAM, _foam(*size, 220, True), FillState.FULL_WITH_FOAM, foam_present=True, foam_y=120.0)
    for order in range(3):
        add(
            f"persistent-foam-{order}",
            BenchmarkCategory.WHITE_FOAM,
            _foam(*size, 205 + order * 5, order == 0),
            FillState.FULL_WITH_FOAM,
            foam_present=True,
            foam_y=122.0 - order,
            sequence_id="persistent-foam",
            sequence_order=order,
        )
    add("variance-shimmer", BenchmarkCategory.TRANSPARENT_OIL_SHIMMER, _shimmer(*size, False), FillState.FULL_NO_INTERFACE)
    add("edge-shimmer", BenchmarkCategory.TRANSPARENT_OIL_SHIMMER, _shimmer(*size, True), FillState.FULL_NO_INTERFACE)
    for order, active in enumerate((False, True, False)):
        add(
            f"transient-shimmer-{order}",
            BenchmarkCategory.TRANSPARENT_OIL_SHIMMER,
            _shimmer(*size, False) if active else _uniform(*size, 105),
            FillState.FULL_NO_INTERFACE,
            sequence_id="transient-shimmer",
            sequence_order=order,
        )
    add("clipped-glare", BenchmarkCategory.REFLECTION_OR_BLUR, _glare(*size), FillState.FULL_NO_INTERFACE)
    add("thin-line", BenchmarkCategory.STRUCTURAL_HORIZONTAL_EDGE, _line(*size), FillState.FULL_NO_INTERFACE)
    add("clear-boundary", BenchmarkCategory.CLEAR_OIL_BOUNDARY, _oil(*size, 130), FillState.PARTIAL_VISIBLE, oil_y=130.0)
    add("full-no-interface", BenchmarkCategory.NO_INTERFACE, _uniform(*size, 80), FillState.FULL_NO_INTERFACE)
    add("empty-no-interface", BenchmarkCategory.NO_INTERFACE, _uniform(*size, 190), FillState.EMPTY_NO_INTERFACE)
    return tuple(rows)


def _base(width, height, value=55):
    return np.full((height, width, 3), value, dtype=np.uint8)


def _foam(width, height, light, partial):
    image = _base(width, height, 45)
    x0, x1, front, bottom = 122, 198, 120, 185
    yy, xx = np.indices((bottom - front, x1 - x0))
    patch = np.where(((xx // 3 + yy // 3) % 2)[..., None] == 0, light, max(80, light - 75)).astype(np.uint8)
    if partial:
        patch[:, patch.shape[1] // 2 :] = 45
    image[front:bottom, x0:x1] = patch
    for y in range(front + 4, bottom, 12):
        for x in range(x0 + 4, x1, 14):
            cv2.circle(image, (x, y), 3, (min(245, light + 15),) * 3, 1)
    return image


def _shimmer(width, height, diagonal):
    image = _base(width, height, 70)
    x0, x1, top, bottom = 122, 198, 116, 185
    patch = image[top:bottom, x0:x1]
    yy, xx = np.indices(patch.shape[:2])
    if not diagonal:
        patch[:, :, 0] = np.where((xx + yy) % 4 < 2, 245, 20)
        patch[:, :, 1] = np.where((xx * 2 + yy) % 5 < 2, 60, 185)
        patch[:, :, 2] = 15
    else:
        patch[:] = (230, 80, 20)
        for offset in range(-60, 100, 7):
            cv2.line(patch, (max(0, offset), 0), (min(patch.shape[1] - 1, offset + 60), patch.shape[0] - 1), (20, 190, 35), 2)
    return image


def _glare(width, height):
    image = _base(width, height, 65)
    image[118:185, 122:198] = 230
    image[118:185, 122:198:2] = 255
    return image


def _line(width, height):
    image = _base(width, height, 60)
    cv2.rectangle(image, (122, 150), (197, 155), (215, 215, 215), -1)
    return image


def _oil(width, height, y):
    image = _base(width, height, 165)
    image[y:185, 122:198] = 75
    cv2.line(image, (122, y), (197, y), (235, 235, 235), 2)
    return image


def _uniform(width, height, value):
    return _base(width, height, value)
