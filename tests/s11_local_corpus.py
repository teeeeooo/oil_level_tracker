from __future__ import annotations

from pathlib import Path

import pytest

from tests.diagnostics.s11_evidence_probe import (
    LocalCorpusUnavailableError,
    repository_root,
    validate_local_corpus,
)


def require_s11_local_corpus(root: Path | None = None) -> Path:
    resolved = repository_root() if root is None else Path(root)
    try:
        validate_local_corpus(resolved)
    except LocalCorpusUnavailableError as exc:
        pytest.skip(str(exc))
    return resolved
