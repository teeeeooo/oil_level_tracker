from __future__ import annotations

from oil_tracker.domain.enums import InitialObservationState
from oil_tracker.domain.recipe import GlassInspectionConfig
from oil_tracker.domain.session import AnalysisSession, InitialStateConfirmation


def confirm_initial_state(
    glass: GlassInspectionConfig,
    session: AnalysisSession,
    asserted_state: InitialObservationState | None = None,
) -> InitialStateConfirmation:
    """Validate and persist an explicit confirmation for the current run context."""
    state = glass.initial_state if asserted_state is None else asserted_state
    if state is InitialObservationState.AUTO:
        raise ValueError("AUTO cannot be confirmed for final analysis.")
    if state is not glass.initial_state:
        raise ValueError(
            f"Initial-state confirmation for {glass.id} ({state.value}) does not match "
            f"the selected Recipe value ({glass.initial_state.value})."
        )
    confirmation = InitialStateConfirmation(
        state=state,
        input_video_path=session.input_video_path,
        analysis_start_sec=session.analysis_start_sec,
    )
    session.initial_state_confirmations[glass.id] = confirmation
    return confirmation
