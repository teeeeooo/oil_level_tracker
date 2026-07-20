from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
from uuid import uuid4

import cv2

from oil_tracker.adapters.storage.debug_trace_repository import DebugTraceError


class DebugCaseExportError(ValueError):
    pass


class DebugCaseExporter:
    CONTEXT_OFFSET_SEC = 1.0
    CLIP_BEFORE_SEC = 2.0
    CLIP_AFTER_SEC = 2.0

    def export(
        self,
        bundle,
        repository,
        record_id: str,
        destination_parent: str | Path,
        *,
        source_video_path: str | Path | None = None,
    ) -> Path:
        bundle_root = _resolve_bundle_root(bundle.root)
        requested_parent = Path(destination_parent).expanduser()
        parent = _ensure_export_outside_bundle(bundle_root, requested_parent, strict=False)
        parent.mkdir(parents=True, exist_ok=True)
        parent = _ensure_export_outside_bundle(bundle_root, parent, strict=True)

        name = datetime.now().strftime("debug_case_%Y%m%d_%H%M%S")
        final = parent / name
        if final.exists() or final.is_symlink():
            raise DebugCaseExportError(f"기존 debug package를 덮어쓸 수 없습니다: {final}")
        temporary = parent / f".{name}.tmp-{uuid4().hex[:8]}"
        warnings: list[str] = []
        record = repository.load_record(record_id)
        source = Path(source_video_path).expanduser() if source_video_path else None
        if source is not None and not source.is_file():
            source = None
        try:
            _ensure_export_outside_bundle(bundle_root, parent, strict=True)
            temporary.mkdir(parents=False, exist_ok=False)
            if temporary.is_symlink():
                raise DebugCaseExportError("디버그 재현 패키지 임시 폴더가 안전하지 않습니다.")
            _ensure_export_outside_bundle(bundle_root, temporary, strict=True)

            detection_payload = asdict(record)
            (temporary / "detection_debug.json").write_text(
                json.dumps(detection_payload, ensure_ascii=False, indent=2, allow_nan=False),
                encoding="utf-8",
            )
            recipe_source = bundle.files.get("recipe_snapshot") or bundle.root / "recipe_snapshot.oilrecipe"
            if not Path(recipe_source).is_file():
                raise DebugCaseExportError("recipe snapshot이 없어 debug package를 만들 수 없습니다.")
            shutil.copy2(recipe_source, temporary / "recipe_snapshot.oilrecipe")

            artifact_map = {
                "overlay": "candidate_overlay.png",
                "original_roi": "roi_crop.png",
                "normalized": "normalized.png",
                "sobel": "sobel.png",
                "canny": "canny.png",
                "effective_mask": "effective_mask.png",
                "glare_mask": "glare_mask.png",
                "foam_mask": "foam_mask.png",
            }
            for key, filename in artifact_map.items():
                image = repository.load_image(record, key)
                if image is None:
                    if key in {"overlay", "original_roi"}:
                        raise DebugCaseExportError(f"필수 debug artifact가 없습니다: {key}")
                    warnings.append(f"optional artifact unavailable: {key}")
                    continue
                _write_png(temporary / filename, image)

            decoded = {}
            if source is None:
                warnings.append("원본 영상을 찾을 수 없어 source frame, context frame과 short clip을 만들지 못했습니다.")
            else:
                decoded = self._write_source_context(temporary, source, record.timestamp_sec, warnings)
                self._write_short_clip(temporary, source, record.timestamp_sec, warnings)

            manifest = {
                "schema_version": 1,
                "run_id": bundle.run_id,
                "record_id": record.record_id,
                "glass_id": record.glass_id,
                "frame_index": record.frame_index,
                "trace_timestamp_sec": record.timestamp_sec,
                "source_video": str(source) if source is not None else None,
                "decoded_timestamps": decoded,
                "clip_window_sec": [
                    max(0.0, record.timestamp_sec - self.CLIP_BEFORE_SEC),
                    record.timestamp_sec + self.CLIP_AFTER_SEC,
                ],
                "warnings": warnings,
                "files": sorted(path.name for path in temporary.iterdir() if path.is_file()),
            }
            (temporary / "manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False),
                encoding="utf-8",
            )

            _ensure_export_outside_bundle(bundle_root, parent, strict=True)
            if temporary.is_symlink():
                raise DebugCaseExportError("디버그 재현 패키지 임시 폴더가 안전하지 않습니다.")
            _ensure_export_outside_bundle(bundle_root, temporary, strict=True)
            if final.exists() or final.is_symlink():
                raise DebugCaseExportError(f"기존 debug package를 덮어쓸 수 없습니다: {final}")
            os.replace(temporary, final)
            return final
        except Exception:
            shutil.rmtree(temporary, ignore_errors=True)
            raise

    def _write_source_context(self, directory: Path, source: Path, timestamp: float, warnings: list[str]) -> dict[str, float]:
        capture = cv2.VideoCapture(str(source))
        if not capture.isOpened():
            warnings.append("원본 영상을 열 수 없어 source/context frame을 만들지 못했습니다.")
            return {}
        duration = _duration(capture)
        targets = {
            "frame.png": _clamp(timestamp, 0.0, duration),
            "context_before.png": _clamp(timestamp - self.CONTEXT_OFFSET_SEC, 0.0, duration),
            "context_after.png": _clamp(timestamp + self.CONTEXT_OFFSET_SEC, 0.0, duration),
        }
        decoded: dict[str, float] = {}
        try:
            for filename, target in targets.items():
                capture.set(cv2.CAP_PROP_POS_MSEC, target * 1000.0)
                ok, frame = capture.read()
                if not ok or frame is None:
                    warnings.append(f"context frame decode failed: {filename}")
                    continue
                actual = float(capture.get(cv2.CAP_PROP_POS_MSEC)) / 1000.0
                _write_png(directory / filename, frame)
                decoded[filename] = actual
        finally:
            capture.release()
        return decoded

    def _write_short_clip(self, directory: Path, source: Path, timestamp: float, warnings: list[str]) -> None:
        capture = cv2.VideoCapture(str(source))
        if not capture.isOpened():
            warnings.append("short clip source open failed")
            return
        writer = None
        try:
            fps = float(capture.get(cv2.CAP_PROP_FPS)) or 0.0
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = _duration(capture)
            start = _clamp(timestamp - self.CLIP_BEFORE_SEC, 0.0, duration)
            end = _clamp(timestamp + self.CLIP_AFTER_SEC, 0.0, duration)
            if fps <= 0 or width <= 0 or height <= 0 or end <= start:
                warnings.append("short clip metadata is unavailable")
                return
            output = directory / "short_clip.mp4"
            writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
            if not writer.isOpened():
                warnings.append("short clip codec/writer initialization failed")
                return
            capture.set(cv2.CAP_PROP_POS_MSEC, start * 1000.0)
            written = 0
            max_frames = int((end - start) * fps) + 3
            while written < max_frames:
                ok, frame = capture.read()
                if not ok or frame is None:
                    break
                actual = float(capture.get(cv2.CAP_PROP_POS_MSEC)) / 1000.0
                if actual > end + 1.0 / fps:
                    break
                writer.write(frame)
                written += 1
            if written == 0:
                warnings.append("short clip contained no decodable frames")
                writer.release()
                writer = None
                output.unlink(missing_ok=True)
        except Exception as exc:
            warnings.append(f"short clip failed: {type(exc).__name__}")
        finally:
            if writer is not None:
                writer.release()
            capture.release()


def _resolve_bundle_root(root: str | Path) -> Path:
    candidate = Path(root).expanduser()
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise DebugCaseExportError("공식 결과 bundle 경로를 확인할 수 없습니다.") from exc
    if not resolved.is_dir():
        raise DebugCaseExportError("공식 결과 bundle 경로가 폴더가 아닙니다.")
    return resolved


def _ensure_export_outside_bundle(bundle_root: Path, destination_parent: Path, *, strict: bool) -> Path:
    try:
        resolved_destination = destination_parent.resolve(strict=strict)
    except OSError as exc:
        raise DebugCaseExportError(f"내보내기 폴더 경로를 확인할 수 없습니다: {destination_parent}") from exc
    if resolved_destination == bundle_root or bundle_root in resolved_destination.parents:
        raise DebugCaseExportError(
            "디버그 재현 패키지는 공식 결과 bundle 내부에 저장할 수 없습니다.\n"
            "결과 bundle 밖의 폴더를 선택해 주세요.\n"
            f"거부된 폴더: {resolved_destination}"
        )
    return resolved_destination


def _write_png(path: Path, image) -> None:
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise DebugCaseExportError(f"PNG encoding failed: {path.name}")
    path.write_bytes(encoded.tobytes())


def _duration(capture) -> float:
    fps = float(capture.get(cv2.CAP_PROP_FPS)) or 0.0
    count = float(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or 0.0
    return max(0.0, count / fps) if fps > 0 else 0.0


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return min(maximum, max(minimum, float(value)))
