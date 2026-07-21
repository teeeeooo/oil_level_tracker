from __future__ import annotations

from types import SimpleNamespace

from oil_tracker.application.ports.progress import AnalysisStage, build_progress_update
from oil_tracker.application.services.analysis_pipeline import SimpleCancellationToken
from oil_tracker.ui.controllers.analysis_controller import AnalysisWorker


class _FailingUseCase:
    def execute(self, _recipe, _session, *, progress, cancellation):
        assert not cancellation.cancelled
        progress(
            build_progress_update(
                AnalysisStage.RESULT_IMAGES,
                0.5,
                message="결과 이미지 생성 중",
            )
        )
        raise OSError("capture write failed")


class _UnusedStore:
    def write_bundle(self, *_args, **_kwargs):
        raise AssertionError("The store must not run after analysis failure.")


def test_worker_failure_identifies_the_active_lifecycle_stage(qtbot) -> None:
    worker = AnalysisWorker(
        _FailingUseCase(),
        _UnusedStore(),
        object(),
        SimpleNamespace(output_directory=""),
        SimpleCancellationToken(),
    )
    messages: list[str] = []
    worker.failed.connect(messages.append)

    worker.run()

    assert messages == [
        "결과 이미지 생성 단계에서 실패했습니다.\ncapture write failed"
    ]
