from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
from pathlib import Path

import cv2
import numpy as np

from benchmark_fixtures import write_catalog
from controlled_dataset_identity import (
    CONTROLLED_CONTRACT_VERSION,
    prepare_controlled_dataset_identity,
)
from oil_tracker.adapters.storage.regression_fixture_exporter import RegressionFixtureExporter
from oil_tracker.application.services.user_truth import TruthFrameContext, UserTruthService
from oil_tracker.domain.detector_benchmark import BenchmarkCategory
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.user_truth import TruthDisposition, TruthErrorType
from user_truth_fixtures import make_truth_bundle


FIXED_TIME = datetime(2026, 7, 21, 18, 0, 0, tzinfo=timezone.utc)
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
class OilControlledScene:
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

    @property
    def usable_truth(self) -> bool:
        return self.fill_state is not FillState.UNKNOWN_REVIEW


class OilControlledVideoReader:
    def __init__(self, source, metadata, scenes):
        self.path = str(source)
        self.metadata = metadata
        self.scenes = {round(scene.timestamp, 6): scene for scene in scenes}
        self.closed = False

    def read_at(self, timestamp):
        scene = self.scenes[round(float(timestamp), 6)]
        return (
            scene.frame.copy(),
            int(round(scene.timestamp * self.metadata.fps)),
            scene.timestamp,
        )

    def close(self):
        self.closed = True


def generate_controlled_oil_dataset(
    tmp_path: Path,
    *,
    contract_version: str = CONTROLLED_CONTRACT_VERSION,
):
    bundle = make_truth_bundle(tmp_path / "controlled-oil")
    _make_recipe_snapshot_base_compatible(bundle)
    scenes = controlled_oil_scenes()
    service = UserTruthService()
    controlled_identity = prepare_controlled_dataset_identity(
        bundle,
        scenes,
        dataset_kind="oil",
        contract_version=contract_version,
        fixed_time=FIXED_TIME,
    )
    identity = controlled_identity.truth_set.bundle_identity
    truth_set = controlled_identity.truth_set
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
        disposition = (
            TruthDisposition.CORRECTED
            if scene.usable_truth
            else TruthDisposition.UNUSABLE
        )
        errors = (
            (TruthErrorType.OTHER,)
            if scene.usable_truth
            else (TruthErrorType.VIDEO_UNUSABLE,)
        )
        annotation = service.make_annotation(
            truth_set,
            identity,
            glass,
            context,
            disposition,
            truth_fill_state=scene.fill_state if scene.usable_truth else None,
            oil_source_y=scene.oil_y if scene.usable_truth else None,
            foam_present=scene.foam_present if scene.usable_truth else False,
            foam_source_y=scene.foam_y if scene.usable_truth else None,
            error_types=errors,
            note=f"controlled oil scene contract: {scene.case_id}",
            official_reference=service.official_reference(
                bundle,
                glass,
                scene.timestamp,
            ),
            now=controlled_identity.timestamp_iso,
        )
        annotation = replace(
            annotation,
            annotation_id=controlled_identity.annotation_id(index, scene.case_id),
            revision=index,
        )
        annotation = truth_set.upsert(
            annotation,
            now=controlled_identity.timestamp_iso,
        )
        annotations.append(annotation)

    reader = OilControlledVideoReader(
        bundle.source_video_path,
        bundle.source_metadata,
        scenes,
    )
    exporter = RegressionFixtureExporter(
        lambda _path: reader,
        clock=lambda: FIXED_TIME,
        dataset_id_factory=lambda: controlled_identity.dataset_id,
    )
    result = exporter.export(
        bundle,
        truth_set,
        annotations,
        tmp_path / "controlled-oil-output",
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
    recipe_path = Path(
        bundle.files.get("recipe_snapshot", bundle.root / "recipe_snapshot.oilrecipe")
    )
    payload = json.loads(recipe_path.read_text(encoding="utf-8"))
    for glass in payload.get("glasses", []):
        settings = glass.get("detector_settings", {})
        for field_name in S5B_SETTING_FIELDS:
            settings.pop(field_name, None)
    recipe_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def controlled_oil_scenes() -> tuple[OilControlledScene, ...]:
    width, height = 320, 240
    rows: list[OilControlledScene] = []
    timestamp = 1.0

    def add(case_id, category, frame, fill_state, **kwargs):
        nonlocal timestamp
        rows.append(
            OilControlledScene(
                case_id,
                category,
                round(timestamp, 3),
                frame,
                fill_state,
                **kwargs,
            )
        )
        timestamp += 0.1

    static = (
        ("clear-upper", BenchmarkCategory.CLEAR_OIL_BOUNDARY, _oil(width, height, 105), FillState.PARTIAL_VISIBLE, 105.0),
        ("clear-center", BenchmarkCategory.CLEAR_OIL_BOUNDARY, _oil(width, height, 132), FillState.PARTIAL_VISIBLE, 132.0),
        ("clear-lower", BenchmarkCategory.CLEAR_OIL_BOUNDARY, _oil(width, height, 160), FillState.PARTIAL_VISIBLE, 160.0),
        ("opposite-polarity", BenchmarkCategory.CLEAR_OIL_BOUNDARY, _oil(width, height, 128, above=65, below=180), FillState.PARTIAL_VISIBLE, 128.0),
        ("weak-valid", BenchmarkCategory.CLEAR_OIL_BOUNDARY, _oil(width, height, 138, above=145, below=95, line=175), FillState.PARTIAL_VISIBLE, 138.0),
        ("structural-plus-real", BenchmarkCategory.STRUCTURAL_HORIZONTAL_EDGE, _structural_plus_oil(width, height, 108, 145), FillState.PARTIAL_VISIBLE, 145.0),
        ("glare-plus-real", BenchmarkCategory.REFLECTION_OR_BLUR, _glare_plus_oil(width, height, 142), FillState.PARTIAL_VISIBLE, 142.0),
        ("reflection-only", BenchmarkCategory.REFLECTION_OR_BLUR, _reflection(width, height), FillState.FULL_NO_INTERFACE, None),
        ("shimmer-only", BenchmarkCategory.TRANSPARENT_OIL_SHIMMER, _shimmer(width, height), FillState.FULL_NO_INTERFACE, None),
        ("full-no-interface", BenchmarkCategory.NO_INTERFACE, _uniform(width, height, 78), FillState.FULL_NO_INTERFACE, None),
        ("empty-no-interface", BenchmarkCategory.NO_INTERFACE, _uniform(width, height, 188), FillState.EMPTY_NO_INTERFACE, None),
        ("rim-line", BenchmarkCategory.STRUCTURAL_HORIZONTAL_EDGE, _rim_line(width, height), FillState.FULL_NO_INTERFACE, None),
    )
    for case_id, category, frame, state, oil_y in static:
        add(case_id, category, frame, state, oil_y=oil_y)

    _add_motion_sequence(
        add,
        width,
        height,
        "slow-motion",
        BenchmarkCategory.CLEAR_OIL_BOUNDARY,
        (120, 123, 126, 129, 132),
        FillState.PARTIAL_VISIBLE,
    )
    _add_motion_sequence(
        add,
        width,
        height,
        "rapid-filling",
        BenchmarkCategory.RAPID_OIL_FLOW,
        (165, 151, 137, 123, 109),
        FillState.FILLING_VISIBLE,
    )
    _add_motion_sequence(
        add,
        width,
        height,
        "rapid-draining",
        BenchmarkCategory.RAPID_OIL_FLOW,
        (108, 122, 136, 150, 164),
        FillState.DRAINING_VISIBLE,
    )
    _add_frames(
        add,
        "transient-false-line",
        BenchmarkCategory.STRUCTURAL_HORIZONTAL_EDGE,
        (
            (_oil(width, height, 132), FillState.PARTIAL_VISIBLE, 132.0),
            (_false_line(width, height, 92), FillState.UNKNOWN_REVIEW, None),
            (_oil(width, height, 134), FillState.PARTIAL_VISIBLE, 134.0),
        ),
    )
    _add_frames(
        add,
        "one-frame-dropout",
        BenchmarkCategory.RAPID_OIL_FLOW,
        (
            (_oil(width, height, 128), FillState.PARTIAL_VISIBLE, 128.0),
            (_uniform(width, height, 112), FillState.UNKNOWN_REVIEW, None),
            (_oil(width, height, 130), FillState.PARTIAL_VISIBLE, 130.0),
        ),
    )
    _add_frames(
        add,
        "multi-frame-dropout",
        BenchmarkCategory.RAPID_OIL_FLOW,
        (
            (_oil(width, height, 128), FillState.PARTIAL_VISIBLE, 128.0),
            (_uniform(width, height, 112), FillState.UNKNOWN_REVIEW, None),
            (_uniform(width, height, 114), FillState.UNKNOWN_REVIEW, None),
            (_oil(width, height, 132), FillState.PARTIAL_VISIBLE, 132.0),
        ),
    )
    _add_frames(
        add,
        "glare-recovery",
        BenchmarkCategory.REFLECTION_OR_BLUR,
        (
            (_oil(width, height, 130), FillState.PARTIAL_VISIBLE, 130.0),
            (_glare(width, height), FillState.UNKNOWN_REVIEW, None),
            (_glare(width, height), FillState.UNKNOWN_REVIEW, None),
            (_oil(width, height, 133), FillState.PARTIAL_VISIBLE, 133.0),
        ),
    )

    for order, frame in enumerate(
        (
            _uniform(width, height, 78),
            _uniform(width, height, 78),
            _oil(width, height, 145),
            _oil(width, height, 143),
        )
    ):
        add(
            f"no-interface-to-visible-{order}",
            BenchmarkCategory.NO_INTERFACE if order < 2 else BenchmarkCategory.RAPID_OIL_FLOW,
            frame,
            FillState.FULL_NO_INTERFACE if order < 2 else FillState.DRAINING_VISIBLE,
            oil_y=None if order < 2 else float(145 - (order - 2) * 2),
            sequence_id="no-interface-to-visible",
            sequence_order=order,
        )
    for order, frame in enumerate(
        (
            _oil(width, height, 145),
            _oil(width, height, 143),
            _uniform(width, height, 78),
            _uniform(width, height, 78),
        )
    ):
        add(
            f"visible-to-no-interface-{order}",
            BenchmarkCategory.RAPID_OIL_FLOW if order < 2 else BenchmarkCategory.NO_INTERFACE,
            frame,
            FillState.DRAINING_VISIBLE if order < 2 else FillState.FULL_NO_INTERFACE,
            oil_y=float(145 - order * 2) if order < 2 else None,
            sequence_id="visible-to-no-interface",
            sequence_order=order,
        )
    _add_motion_sequence(
        add,
        width,
        height,
        "large-jump-new-path",
        BenchmarkCategory.RAPID_OIL_FLOW,
        (125, 126, 168, 170, 172),
        FillState.PARTIAL_VISIBLE,
    )
    for order, polarity in enumerate((1, 1, -1, -1)):
        y = 132 + order
        add(
            f"polarity-change-{order}",
            BenchmarkCategory.CLEAR_OIL_BOUNDARY,
            _oil(
                width,
                height,
                y,
                above=175 if polarity > 0 else 65,
                below=70 if polarity > 0 else 180,
            ),
            FillState.PARTIAL_VISIBLE,
            oil_y=float(y),
            sequence_id="polarity-change",
            sequence_order=order,
        )
    return tuple(rows)


def _add_motion_sequence(add, width, height, sequence_id, category, ys, state):
    for order, y in enumerate(ys):
        add(
            f"{sequence_id}-{order}",
            category,
            _oil(width, height, y),
            state,
            oil_y=float(y),
            sequence_id=sequence_id,
            sequence_order=order,
        )


def _add_frames(add, sequence_id, category, frames):
    for order, (frame, state, oil_y) in enumerate(frames):
        add(
            f"{sequence_id}-{order}",
            category,
            frame,
            state,
            oil_y=oil_y,
            sequence_id=sequence_id,
            sequence_order=order,
        )


def _uniform(width: int, height: int, value: int) -> np.ndarray:
    # Avoid an artificial rectangular patch perimeter inside the effective ellipse.
    return np.full((height, width, 3), value, dtype=np.uint8)


def _oil(
    width: int,
    height: int,
    y: int,
    *,
    above: int = 175,
    below: int = 70,
    line: int = 225,
) -> np.ndarray:
    image = _uniform(width, height, above)
    image[y:] = below
    cv2.line(image, (0, y), (width - 1, y), (line, line, line), 2)
    return image


def _structural_plus_oil(width: int, height: int, structure_y: int, oil_y: int) -> np.ndarray:
    image = _oil(width, height, oil_y, above=170, below=78, line=185)
    cv2.rectangle(
        image,
        (0, structure_y - 3),
        (width - 1, structure_y + 3),
        (245, 245, 245),
        -1,
    )
    return image


def _glare_plus_oil(width: int, height: int, y: int) -> np.ndarray:
    image = _oil(width, height, y)
    cv2.rectangle(image, (126, 92), (137, 176), (255, 255, 255), -1)
    return image


def _reflection(width: int, height: int) -> np.ndarray:
    image = _uniform(width, height, 88)
    cv2.line(image, (130, 90), (190, 175), (225, 225, 225), 4)
    return image


def _shimmer(width: int, height: int) -> np.ndarray:
    image = _uniform(width, height, 82)
    patch = image[90:181, 124:196]
    yy, xx = np.indices(patch.shape[:2])
    patch[:, :, 0] = np.where((xx + yy) % 5 < 2, 150, 55)
    patch[:, :, 1] = np.where((xx * 2 + yy) % 7 < 3, 120, 65)
    patch[:, :, 2] = 70
    return image


def _rim_line(width: int, height: int) -> np.ndarray:
    image = _uniform(width, height, 88)
    cv2.rectangle(image, (0, 79), (width - 1, 84), (230, 230, 230), -1)
    return image


def _false_line(width: int, height: int, y: int) -> np.ndarray:
    image = _uniform(width, height, 105)
    cv2.rectangle(image, (0, y - 3), (width - 1, y + 3), (245, 245, 245), -1)
    return image


def _glare(width: int, height: int) -> np.ndarray:
    image = _uniform(width, height, 90)
    image[80:185, 122:198] = 250
    image[80:185, 122:198:2] = 255
    return image
