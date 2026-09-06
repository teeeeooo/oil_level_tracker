from __future__ import annotations

"""Runtime/input provenance for deterministic S11 replay evidence."""

from hashlib import sha256
from importlib import metadata
import json
from pathlib import Path
import platform
import sys

import cv2
import numpy as np


RUNTIME_PROVENANCE_SCHEMA = "s11-replay-runtime-provenance-v1"


class ReplayInputUnavailableError(RuntimeError):
    """A required replay input is not present."""


class ReplayInputIdentityError(RuntimeError):
    """A replay input does not match its frozen authoritative identity."""


def _canonical_sha256(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _package_version(distribution: str) -> str:
    try:
        return metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return "UNAVAILABLE"


def _opencv_videoio_build_details(build_information: str) -> dict[str, str]:
    wanted = (
        "FFMPEG",
        "avcodec",
        "avformat",
        "avutil",
        "swscale",
        "GStreamer",
        "v4l/v4l2",
    )
    details: dict[str, str] = {}
    for raw_line in build_information.splitlines():
        stripped = raw_line.strip()
        for key in wanted:
            prefix = f"{key}:"
            if stripped.startswith(prefix):
                details[key] = stripped[len(prefix) :].strip()
    return details


def _video_backend_name(video_path: Path) -> str:
    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            return "UNAVAILABLE"
        try:
            return str(capture.getBackendName())
        except (AttributeError, cv2.error):
            return "UNKNOWN"
    finally:
        capture.release()


def capture_runtime_provenance(video_path: Path) -> dict[str, object]:
    build_information = cv2.getBuildInformation()
    signature = {
        "python_implementation": platform.python_implementation(),
        "python_version": sys.version.split()[0],
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "platform_machine": platform.machine(),
        "opencv_version": cv2.__version__,
        "numpy_version": np.__version__,
        "opencv_build_sha256": sha256(build_information.encode("utf-8")).hexdigest(),
        "opencv_videoio": _opencv_videoio_build_details(build_information),
        "video_backend": _video_backend_name(video_path),
        "packages": {
            "opencv-python-headless": _package_version("opencv-python-headless"),
            "numpy": _package_version("numpy"),
            "PySide6": _package_version("PySide6"),
            "Jinja2": _package_version("Jinja2"),
            "matplotlib": _package_version("matplotlib"),
        },
    }
    return {
        "schema": RUNTIME_PROVENANCE_SCHEMA,
        "runtime_fingerprint_sha256": _canonical_sha256(signature),
        **signature,
    }


def classify_exact_reproducibility(
    *,
    actual_tracking_fingerprint: str,
    expected_tracking_fingerprint: str | None,
    actual_runtime_fingerprint: str,
    expected_runtime_fingerprint: str | None,
) -> dict[str, str]:
    runtime_status = (
        "UNVERIFIED"
        if expected_runtime_fingerprint is None
        else (
            "MATCH"
            if actual_runtime_fingerprint == expected_runtime_fingerprint
            else "ENVIRONMENT_DRIFT"
        )
    )
    tracking_status = (
        "UNVERIFIED"
        if expected_tracking_fingerprint is None
        else (
            "MATCH"
            if actual_tracking_fingerprint == expected_tracking_fingerprint
            else "MISMATCH"
        )
    )
    if tracking_status == "UNVERIFIED":
        interpretation = "TRACKING_UNVERIFIED"
    elif tracking_status == "MATCH" and runtime_status == "MATCH":
        interpretation = "EXACT_MATCH"
    elif tracking_status == "MATCH" and runtime_status == "ENVIRONMENT_DRIFT":
        interpretation = "TRACKING_MATCH_ENVIRONMENT_DRIFT"
    elif tracking_status == "MATCH":
        interpretation = "TRACKING_MATCH_RUNTIME_UNVERIFIED"
    elif runtime_status == "MATCH":
        interpretation = "TRACKING_MISMATCH_SAME_RUNTIME"
    elif runtime_status == "ENVIRONMENT_DRIFT":
        interpretation = "ENVIRONMENT_DRIFT"
    else:
        interpretation = "UNCLASSIFIED_TRACKING_MISMATCH"
    return {
        "runtime_status": runtime_status,
        "tracking_status": tracking_status,
        "interpretation": interpretation,
    }


def enforce_exact_tracking_contract(
    *,
    actual_tracking_fingerprint: str,
    expected_tracking_fingerprint: str,
    actual_runtime_fingerprint: str,
    expected_runtime_fingerprint: str | None,
) -> dict[str, str]:
    classification = classify_exact_reproducibility(
        actual_tracking_fingerprint=actual_tracking_fingerprint,
        expected_tracking_fingerprint=expected_tracking_fingerprint,
        actual_runtime_fingerprint=actual_runtime_fingerprint,
        expected_runtime_fingerprint=expected_runtime_fingerprint,
    )
    if actual_tracking_fingerprint == expected_tracking_fingerprint:
        return classification
    if classification["runtime_status"] == "ENVIRONMENT_DRIFT":
        return classification
    raise AssertionError(
        "tracking fingerprint mismatch "
        f"classification={classification['interpretation']} "
        f"expected={expected_tracking_fingerprint} "
        f"actual={actual_tracking_fingerprint}"
    )


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_frozen_inputs(
    *,
    root: Path,
    expected_inputs: dict[str, dict[str, str]],
    samples: tuple[str, ...],
) -> dict[str, dict[str, str]]:
    missing: list[str] = []
    mismatches: list[str] = []
    actual_inputs: dict[str, dict[str, str]] = {}
    for sample in samples:
        actual_inputs[sample] = {}
        for suffix in ("mp4", "oilrecipe", "oiltruth"):
            path = root / "sample" / f"{sample}.{suffix}"
            if not path.is_file():
                missing.append(path.as_posix())
                continue
            actual = _file_sha256(path)
            actual_inputs[sample][suffix] = actual
            expected = str(expected_inputs[sample][suffix])
            if actual != expected:
                mismatches.append(
                    f"{path.as_posix()} expected={expected} actual={actual}"
                )
    if mismatches:
        raise ReplayInputIdentityError(
            "S11 replay input identity mismatch: " + "; ".join(mismatches)
        )
    if missing:
        raise ReplayInputUnavailableError(
            "S11 replay input NOT AVAILABLE: " + ", ".join(missing)
        )
    return actual_inputs
