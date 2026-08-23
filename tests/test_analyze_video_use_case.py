from __future__ import annotations

from pathlib import Path

from oil_tracker.application.use_cases.analyze_video import AnalyzeVideoUseCase


def test_analyze_video_owns_analysis_and_persistence_transaction(tmp_path) -> None:
    result = object()
    recipe = object()
    session = object()
    progress = object()
    cancellation = object()
    calls = []

    class Pipeline:
        def run(self, actual_recipe, actual_session, *, progress, cancellation):
            calls.append(
                ("analyze", actual_recipe, actual_session, progress, cancellation)
            )
            return result

    class Store:
        def write_bundle(
            self,
            actual_result,
            actual_recipe,
            actual_session,
            root,
            *,
            progress,
            cancellation,
        ):
            calls.append(
                (
                    "persist",
                    actual_result,
                    actual_recipe,
                    actual_session,
                    root,
                    progress,
                    cancellation,
                )
            )
            return root / "bundle"

    output = AnalyzeVideoUseCase(Pipeline(), Store()).execute(
        recipe,
        session,
        output_root=tmp_path,
        progress=progress,
        cancellation=cancellation,
    )

    assert output.result is result
    assert output.output_path == Path(tmp_path) / "bundle"
    assert calls == [
        ("analyze", recipe, session, progress, cancellation),
        (
            "persist",
            result,
            recipe,
            session,
            Path(tmp_path),
            progress,
            cancellation,
        ),
    ]
