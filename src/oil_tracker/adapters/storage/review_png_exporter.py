from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Iterable
from uuid import uuid4

from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtGui import QImage


class ReviewPngExportError(ValueError):
    """Base error for a user-correctable Result Review PNG export failure."""


class ReviewPngDestinationError(ReviewPngExportError):
    pass


class ReviewPngEncodingError(ReviewPngExportError):
    pass


class ReviewPngWriteError(ReviewPngExportError):
    pass


class ReviewPngExporter:
    """Encode a detached full-resolution QImage and atomically finalize one PNG."""

    def __init__(
        self,
        *,
        encoder: Callable[[QImage], bytes] | None = None,
        replacer: Callable[[str | os.PathLike, str | os.PathLike], None] = os.replace,
    ) -> None:
        self.encoder = encoder or _encode_png
        self.replacer = replacer

    def export(
        self,
        image: QImage,
        destination: str | Path,
        *,
        protected_roots: Iterable[str | Path] = (),
        overwrite: bool = True,
    ) -> Path:
        if not isinstance(image, QImage) or image.isNull():
            raise ReviewPngEncodingError("저장할 원본 해상도 이미지가 없습니다.")
        path = _normalized_png_path(destination)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            resolved_parent = path.parent.resolve(strict=True)
        except OSError as exc:
            raise ReviewPngWriteError(f"PNG 저장 폴더를 준비할 수 없습니다: {exc}") from exc
        resolved = resolved_parent / path.name
        _ensure_safe_destination(resolved, protected_roots)
        if resolved.is_symlink():
            raise ReviewPngDestinationError("symbolic link PNG destination에는 저장할 수 없습니다.")
        if resolved.exists() and not overwrite:
            raise ReviewPngDestinationError(f"기존 PNG 파일을 덮어쓸 수 없습니다: {resolved}")

        try:
            payload = self.encoder(QImage(image).copy())
        except ReviewPngEncodingError:
            raise
        except Exception as exc:
            raise ReviewPngEncodingError(f"PNG 인코딩에 실패했습니다: {exc}") from exc
        if not payload:
            raise ReviewPngEncodingError("PNG 인코더가 빈 결과를 반환했습니다.")

        temporary = resolved.parent / f".{resolved.name}.tmp-{uuid4().hex}"
        try:
            with temporary.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            self.replacer(temporary, resolved)
        except OSError as exc:
            raise ReviewPngWriteError(f"PNG 파일을 저장할 수 없습니다: {exc}") from exc
        finally:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        return resolved


def _normalized_png_path(destination: str | Path) -> Path:
    path = Path(destination).expanduser()
    if path.suffix.lower() != ".png":
        path = path.with_suffix(".png")
    if not path.name or path.name in {".", ".."}:
        raise ReviewPngDestinationError("PNG destination 파일명이 올바르지 않습니다.")
    return path


def _ensure_safe_destination(destination: Path, protected_roots: Iterable[str | Path]) -> None:
    for value in protected_roots:
        root = Path(value).expanduser()
        try:
            resolved_root = root.resolve(strict=True)
        except OSError as exc:
            raise ReviewPngDestinationError(f"보호할 결과 bundle 경로를 확인할 수 없습니다: {root}") from exc
        if destination == resolved_root or resolved_root in destination.parents:
            raise ReviewPngDestinationError(
                "현재 장면 PNG는 공식 결과 bundle 내부에 저장할 수 없습니다. "
                "bundle 밖의 폴더를 선택해 주세요."
            )


def _encode_png(image: QImage) -> bytes:
    buffer = QBuffer()
    if not buffer.open(QIODevice.OpenModeFlag.WriteOnly):
        raise ReviewPngEncodingError("PNG 메모리 버퍼를 열 수 없습니다.")
    try:
        if not image.save(buffer, "PNG"):
            raise ReviewPngEncodingError("PNG 인코딩에 실패했습니다.")
        return bytes(buffer.data())
    finally:
        buffer.close()
