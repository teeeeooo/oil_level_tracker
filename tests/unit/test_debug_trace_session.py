from __future__ import annotations

import pytest

from oil_tracker.domain.session import AnalysisSession, DebugTraceLevel


def test_new_session_defaults_to_basic():
    assert AnalysisSession().debug_trace_level is DebugTraceLevel.BASIC


@pytest.mark.parametrize("level", list(DebugTraceLevel))
def test_session_serializes_explicit_debug_level(level):
    session = AnalysisSession(debug_trace_level=level)
    payload = session.to_dict()
    assert payload["debug_trace_level"] == level.value
    assert AnalysisSession.from_dict(payload).debug_trace_level is level


def test_legacy_session_without_field_reads_as_none():
    assert AnalysisSession.from_dict({}).debug_trace_level is DebugTraceLevel.NONE


def test_invalid_debug_level_is_clear_error():
    with pytest.raises(ValueError, match="Invalid debug_trace_level"):
        AnalysisSession.from_dict({"debug_trace_level": "verbose"})


def test_debug_level_is_not_recipe_schema_data():
    from oil_tracker.domain.recipe import InspectionRecipe

    payload = InspectionRecipe.empty().to_dict()
    assert "debug_trace_level" not in payload
