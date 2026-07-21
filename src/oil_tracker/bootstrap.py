from __future__ import annotations

from oil_tracker.adapters.presentation.qt_debug_artifact_presenter import QtDebugArtifactPresenter
from oil_tracker.adapters.presentation.qt_frame_image_converter import QtFrameImageConverter
from oil_tracker.adapters.presentation.review_frame_presenter import (
    ReviewFramePresenter,
    ReviewPresentedVideoReader,
)
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.adapters.storage.redetection_workspace import RedetectionWorkspace
from oil_tracker.adapters.storage.review_png_exporter import ReviewPngExporter
from oil_tracker.adapters.system.logging_config import configure_logging
from oil_tracker.adapters.vision.debug_renderer import DebugRenderer
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.adapters.vision.review_debug_overlay_renderer import ReviewDebugOverlayRenderer
from oil_tracker.adapters.vision.review_overlay_renderer import ReviewOverlayRenderer
from oil_tracker.adapters.vision.source_video_resolver import SourceVideoResolver
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.services.redetection_service import PartialRedetectionService
from oil_tracker.application.use_cases.analyze_video import AnalyzeVideoUseCase
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.preflight_check import PreflightCheckUseCase
from oil_tracker.application.use_cases.preview_detection import PreviewDetectionUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.ui.analysis_completion_coordinator import AnalysisCompletionCoordinator
from oil_tracker.ui.controllers.analysis_controller import AnalysisController
from oil_tracker.ui.controllers.preflight_controller import PreflightController
from oil_tracker.ui.controllers.preview_controller import PreviewController
from oil_tracker.ui.controllers.result_review_controller import ResultReviewController
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.debug_trace_settings import install_debug_trace_selector
from oil_tracker.ui.main_window import MainWindow
from oil_tracker.ui.observation_settings_copy_coordinator import ObservationSettingsCopyCoordinator
from oil_tracker.ui.preflight_coordinator import PreflightCoordinator
from oil_tracker.ui.redetection_result_review_window import RedetectionResultReviewWindow
from oil_tracker.ui.result_actions import ResultActionService
from oil_tracker.ui.result_review_coordinator import ResultReviewCoordinator
from oil_tracker.ui.same_profile_analysis_coordinator import SameProfileAnalysisCoordinator


def build_main_window() -> MainWindow:
    configure_logging()
    repository = JsonRecipeRepository()
    validator = RecipeValidationService()
    workbench = WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
    )
    preview_detector = OpenCvPhaseDetector()
    preview_controller = PreviewController(PreviewDetectionUseCase(preview_detector))
    analysis_detector = OpenCvPhaseDetector()
    pipeline = AnalysisPipeline(
        lambda path: OpenCvVideoReader(path),
        analysis_detector,
        validator,
        JsonlDebugTraceWriterFactory(),
    )
    result_store = OutputBundleStore()
    analysis_controller = AnalysisController(AnalyzeVideoUseCase(pipeline), result_store)
    window = MainWindow(workbench, preview_controller, analysis_controller, DebugRenderer())
    analysis_controller.setParent(window)
    window.destroyed.connect(lambda: analysis_controller.shutdown())
    install_debug_trace_selector(window)
    window.settings_copy_coordinator = ObservationSettingsCopyCoordinator(window)
    preflight_use_case = PreflightCheckUseCase(
        lambda path: OpenCvVideoReader(path),
        OpenCvPhaseDetector,
        validator,
    )
    preflight_controller = PreflightController(preflight_use_case, window)
    window.preflight_coordinator = PreflightCoordinator(window, preflight_controller)
    window.same_profile_coordinator = SameProfileAnalysisCoordinator(window)
    window.result_action_service = ResultActionService()
    window.redetection_service = PartialRedetectionService(
        lambda path: OpenCvVideoReader(path),
        OpenCvPhaseDetector,
        RedetectionWorkspace.create,
    )

    def review_presenter_factory() -> ReviewFramePresenter:
        return ReviewFramePresenter(
            ReviewOverlayRenderer(),
            ReviewDebugOverlayRenderer(),
            QtFrameImageConverter(),
        )

    def review_reader_factory(path):
        return ReviewPresentedVideoReader(
            path,
            reader_factory=OpenCvVideoReader,
            presenter_factory=review_presenter_factory,
        )

    def review_viewer_factory(parent):
        return RedetectionResultReviewWindow(
            source_resolver=SourceVideoResolver(OpenCvVideoReader),
            playback_controller=ResultReviewController(review_reader_factory),
            action_service=window.result_action_service,
            png_exporter=ReviewPngExporter(),
            debug_artifact_presenter=QtDebugArtifactPresenter(QtFrameImageConverter()),
            parent=parent,
        )

    window.result_review_coordinator = ResultReviewCoordinator(
        window,
        window.result_action_service,
        window.same_profile_coordinator,
        window.redetection_service,
        viewer_factory=review_viewer_factory,
    )
    window.analysis_completion_coordinator = AnalysisCompletionCoordinator(
        window,
        window.result_review_coordinator,
        window.same_profile_coordinator,
        window.result_action_service,
    )
    try:
        analysis_controller.completed.disconnect(window._analysis_completed)
    except (RuntimeError, TypeError):
        pass
    analysis_controller.completed.connect(
        window.analysis_completion_coordinator.analysis_completed
    )
    try:
        window.actions["result"].triggered.disconnect(window.open_result)
    except (RuntimeError, TypeError):
        pass
    window.actions["result"].triggered.connect(
        lambda _checked=False: window.analysis_completion_coordinator.open_last_report()
    )
    return window
