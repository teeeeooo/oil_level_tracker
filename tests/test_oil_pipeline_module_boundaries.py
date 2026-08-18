from __future__ import annotations

import ast
import inspect

from oil_tracker.adapters.vision import (
    oil_pipeline_diagnostics as diagnostics_module,
    oil_pipeline_validation as validation_module,
    oil_shadow_pipeline as pipeline_module,
)
from oil_tracker.adapters.vision.oil_pipeline_validation import OilPipelineValidator
from oil_tracker.adapters.vision.oil_shadow_pipeline import (
    OilHypothesisPipeline,
    _FixedCanonicalReducer,
)


def _relative_imports(module) -> set[str]:
    tree = ast.parse(inspect.getsource(module))
    return {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }


def test_pipeline_dependencies_are_one_way_and_collaborators_are_state_bounded():
    pipeline_imports = _relative_imports(pipeline_module)
    assert "oil_pipeline_diagnostics" in pipeline_imports
    assert "oil_pipeline_validation" in pipeline_imports
    assert "oil_shadow_pipeline" not in _relative_imports(diagnostics_module)
    assert "oil_shadow_pipeline" not in _relative_imports(validation_module)

    pipeline = OilHypothesisPipeline()
    validator = getattr(pipeline, "_OilHypothesisPipeline__validator")
    reducer = getattr(pipeline, "_OilHypothesisPipeline__reducer")

    assert type(validator) is OilPipelineValidator
    assert vars(validator) == {
        "bounds": pipeline.bounds,
        "retained_scalar_limit": reducer.retained_scalar_limit,
    }
    assert type(reducer) is _FixedCanonicalReducer
    assert not hasattr(validator, "reduce")
    assert not {
        "run",
        "reset",
        "_submit",
        "_dispatch",
        "_prepare_run_store",
    } & set(OilPipelineValidator.__dict__)


def test_diagnostics_imports_are_reexports_from_explicit_owner():
    assert pipeline_module.outcome_hypotheses is diagnostics_module.outcome_hypotheses
    assert pipeline_module.oil_runtime_metrics is diagnostics_module.oil_runtime_metrics
    assert pipeline_module.oil_debug_detail is diagnostics_module.oil_debug_detail


def test_private_validation_seams_delegate_to_the_explicit_owner(monkeypatch):
    pipeline = OilHypothesisPipeline()
    marker = object()
    calls: list[tuple[OilPipelineValidator, object]] = []

    def delegated(self: OilPipelineValidator, frame: object) -> object:
        calls.append((self, frame))
        return marker

    monkeypatch.setattr(OilPipelineValidator, "_phase_a", delegated)
    assert pipeline._phase_a(marker) is marker
    validator = getattr(pipeline, "_OilHypothesisPipeline__validator")
    assert calls == [(validator, marker)]

    delegated_methods = (
        "_phase_a",
        "_validate_evidence_graph",
        "_validate_raw_observation_shape",
        "_validate_hypothesis_summaries",
        "_canonical_current",
        "_validate_decision",
        "_validate_reduction",
        "_validate_next_record",
        "_validate_record_value",
        "_expected_resource_summary",
        "_validate_prepared_run_store",
        "_validate_prepared_reset_store",
        "_validate_store_shape",
        "_validate_transition_coherence",
        "_expected_pending_motion",
        "_validate_prepared_outcome",
    )
    for name in delegated_methods:
        source = inspect.getsource(getattr(OilHypothesisPipeline, name))
        assert "self.__validator" in source
        assert len([line for line in source.splitlines() if line.strip()]) <= 12

    store_source = inspect.getsource(OilHypothesisPipeline._prepare_run_store)
    assert "self.__validator" not in store_source
    assert "TemporalStoreState" in store_source
