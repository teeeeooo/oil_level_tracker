from __future__ import annotations

from pathlib import Path

from oil_tracker.application.ports.review_io import BundleAssetError


class BundleAssetResolver:
    def resolve_file(self, root: str | Path, relative_path: str | Path, *, label: str = "결과 파일") -> Path:
        return self._resolve(root, relative_path, expect_directory=False, label=label)

    def resolve_directory(self, root: str | Path, relative_path: str | Path = ".", *, label: str = "결과 폴더") -> Path:
        return self._resolve(root, relative_path, expect_directory=True, label=label)

    def _resolve(
        self,
        root: str | Path,
        relative_path: str | Path,
        *,
        expect_directory: bool,
        label: str,
    ) -> Path:
        root_path = Path(root).expanduser()
        if not root_path.exists() or not root_path.is_dir():
            raise BundleAssetError(f"{label}의 결과 bundle 폴더가 존재하지 않습니다: {root_path}")
        root_resolved = root_path.resolve(strict=True)
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise BundleAssetError(f"{label} 경로는 결과 bundle 내부의 상대경로여야 합니다: {relative_path}")
        candidate = root_path / relative
        try:
            resolved = candidate.resolve(strict=True)
        except FileNotFoundError as exc:
            raise BundleAssetError(f"{label}이 존재하지 않습니다: {candidate}") from exc
        except OSError as exc:
            raise BundleAssetError(f"{label} 경로를 확인할 수 없습니다: {exc}") from exc
        try:
            resolved.relative_to(root_resolved)
        except ValueError as exc:
            raise BundleAssetError(f"{label} 경로가 결과 bundle 밖으로 벗어납니다: {relative_path}") from exc
        if expect_directory and not resolved.is_dir():
            raise BundleAssetError(f"{label}은 폴더여야 합니다: {resolved}")
        if not expect_directory and not resolved.is_file():
            raise BundleAssetError(f"{label}은 파일이어야 합니다: {resolved}")
        return resolved


def resolve_bundle_asset(root: str | Path, relative_path: str | Path) -> Path:
    return BundleAssetResolver().resolve_file(root, relative_path)
