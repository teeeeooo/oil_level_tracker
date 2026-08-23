from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile
from typing import Callable

from oil_tracker.application.ports.review_io import (
    TruthIdentityMismatchError,
    TruthRepositoryError,
)
from oil_tracker.application.services.truth_identity import (
    build_truth_bundle_identity,
    sha256_file,
)
from oil_tracker.domain.user_truth import (
    TruthBundleIdentity,
    TruthValidationError,
    UserTruthSet,
    validate_annotation,
)


@dataclass(frozen=True)
class TruthLoadResult:
    truth_set: UserTruthSet
    path: Path
    warnings: tuple[str, ...] = ()


class JsonTruthRepository:
    extension = ".oiltruth"

    def normalized_path(self, path: str | Path) -> Path:
        candidate = Path(path).expanduser()
        return candidate if candidate.suffix.lower() == self.extension else candidate.with_suffix(self.extension)

    def save(
        self,
        path: str | Path,
        truth_set: UserTruthSet,
        *,
        bundle_root: str | Path,
        bundle=None,
        overwrite: bool = False,
        confirm_overwrite: Callable[[Path], bool] | None = None,
    ) -> Path:
        destination = ensure_truth_destination_outside_bundle(bundle_root, self.normalized_path(path))
        if destination.exists() or destination.is_symlink():
            if destination.is_dir():
                raise TruthRepositoryError("사용자 정답 저장 경로가 파일이 아닌 폴더입니다.")
            allowed = overwrite or (confirm_overwrite is not None and bool(confirm_overwrite(destination)))
            if not allowed:
                raise TruthRepositoryError("기존 사용자 정답 파일 덮어쓰기가 취소되었습니다.")
        if bundle is not None:
            validate_truth_set_for_bundle(truth_set, bundle)
        try:
            payload = json.dumps(
                truth_set.to_dict(),
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            )
        except (TypeError, ValueError, TruthValidationError) as exc:
            raise TruthRepositoryError(f"사용자 정답 JSON을 만들 수 없습니다: {exc}") from exc
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination = ensure_truth_destination_outside_bundle(bundle_root, destination)
        try:
            _atomic_write_text(destination, payload)
        except Exception as exc:
            raise TruthRepositoryError(f"사용자 정답 파일을 저장할 수 없습니다: {exc}") from exc
        return destination

    def load(
        self,
        path: str | Path,
        *,
        expected_identity: TruthBundleIdentity | None = None,
        bundle=None,
    ) -> TruthLoadResult:
        source = self.normalized_path(path)
        if not source.is_file():
            raise TruthRepositoryError(f"사용자 정답 파일이 존재하지 않습니다: {source}")
        try:
            text = source.read_text(encoding="utf-8")
            payload = json.loads(text, parse_constant=_reject_json_constant)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            raise TruthRepositoryError(f"사용자 정답 JSON을 읽을 수 없습니다: {exc}") from exc
        try:
            truth_set = UserTruthSet.from_dict(payload)
        except (TruthValidationError, TypeError, ValueError) as exc:
            raise TruthRepositoryError(str(exc)) from exc
        warnings: tuple[str, ...] = ()
        if expected_identity is not None:
            mismatches = truth_set.bundle_identity.mismatches(expected_identity)
            if mismatches:
                raise TruthIdentityMismatchError(mismatches)
            warnings = truth_set.bundle_identity.metadata_warnings(expected_identity)
        if bundle is not None:
            validate_truth_set_for_bundle(truth_set, bundle)
        return TruthLoadResult(truth_set, source.resolve(), warnings)


def validate_truth_set_for_bundle(truth_set: UserTruthSet, bundle) -> None:
    expected = build_truth_bundle_identity(bundle)
    mismatches = truth_set.bundle_identity.mismatches(expected)
    if mismatches:
        raise TruthIdentityMismatchError(mismatches)
    known_glasses = {glass.id: glass for glass in bundle.recipe.glasses}
    seen = set()
    for annotation in truth_set.annotations:
        glass = known_glasses.get(annotation.glass_id)
        if glass is None:
            raise TruthRepositoryError(
                f"사용자 정답에 result snapshot에 없는 관찰창 ID가 있습니다: {annotation.glass_id}"
            )
        if annotation.key in seen:
            raise TruthRepositoryError("동일 관찰창·frame의 annotation이 중복되어 있습니다.")
        seen.add(annotation.key)
        try:
            validate_annotation(annotation, glass)
        except TruthValidationError as exc:
            raise TruthRepositoryError(f"annotation {annotation.annotation_id}: {exc}") from exc


def ensure_truth_destination_outside_bundle(bundle_root: str | Path, destination: str | Path) -> Path:
    try:
        root = Path(bundle_root).expanduser().resolve(strict=True)
    except OSError as exc:
        raise TruthRepositoryError("공식 결과 bundle 경로를 확인할 수 없습니다.") from exc
    if not root.is_dir():
        raise TruthRepositoryError("공식 결과 bundle 경로가 폴더가 아닙니다.")
    candidate = Path(destination).expanduser()
    try:
        resolved = candidate.resolve(strict=False)
    except OSError as exc:
        raise TruthRepositoryError(f"사용자 정답 저장 경로를 확인할 수 없습니다: {candidate}") from exc
    if resolved == root or root in resolved.parents:
        raise TruthRepositoryError(
            "사용자 정답은 공식 결과 bundle 내부에 저장할 수 없습니다.\n"
            "결과 bundle 밖의 파일을 선택해 주세요."
        )
    return candidate


def _atomic_write_text(path: Path, text: str) -> None:
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _reject_json_constant(value: str):
    raise ValueError(f"JSON에 허용되지 않는 숫자입니다: {value}")
