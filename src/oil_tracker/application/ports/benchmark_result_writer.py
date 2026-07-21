from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Protocol


class BenchmarkResultWriter(Protocol):
    def load_result(self, path: str | Path) -> Mapping[str, Any]: ...

    def write(
        self,
        payload: Mapping[str, Any],
        output_root: str | Path,
        *,
        dataset_id: str,
        timestamp_token: str,
    ) -> Path: ...
