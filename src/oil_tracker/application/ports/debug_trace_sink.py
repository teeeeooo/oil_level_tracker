from __future__ import annotations

from typing import Protocol

from oil_tracker.domain.debug_trace import DebugCaptureDecision, DebugTraceCompletion


class DebugTraceSink(Protocol):
    def write(self, glass, detection, artifacts, decision: DebugCaptureDecision) -> None: ...
    def finalize(self) -> DebugTraceCompletion: ...
    def abort(self) -> None: ...


class DebugTraceSinkFactory(Protocol):
    def create(self, run_id: str, recipe, session) -> DebugTraceSink: ...
