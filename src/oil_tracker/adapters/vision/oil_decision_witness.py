from __future__ import annotations

from oil_tracker.domain.detection import PhaseDetection

from .oil_phase_lifecycle import OilMaterialPhase
from .oil_sequence_types import OilCandidateRef, OilSequenceNode


DECISION_WITNESS_SCHEMA_VERSION = "r21-decision-witness-v1"


def _predicate_status(value: object) -> str:
    return "true" if bool(value) else "false"


def _predicate_witness(record: object) -> list[dict[str, object]]:
    if not isinstance(record, dict):
        return []
    predicates = record.get("ordered_predicates")
    if isinstance(predicates, list):
        return [
            {
                "name": str(item.get("name")),
                "status": _predicate_status(item.get("passed")),
            }
            for item in predicates
            if isinstance(item, dict) and "name" in item and "passed" in item
        ]
    predicates = record.get("predicates")
    if isinstance(predicates, dict):
        return [
            {"name": str(name), "status": _predicate_status(passed)}
            for name, passed in predicates.items()
        ]
    return []


def _evaluation_witness(record: object) -> dict[str, object]:
    if not isinstance(record, dict):
        return {"status": "UNAVAILABLE", "predicates": []}
    output = {
        key: record[key]
        for key in (
            "stage",
            "tracklet_id",
            "row_hypothesis_id",
            "row_y",
            "entrance_y",
            "entrance_relative",
            "minimum_progress_px",
            "tracklet_progress_px",
            "directional_agreement",
            "current_material_veto",
            "tracklet_material_conflict",
            "current_material_conflict",
            "first_failed_predicate",
        )
        if key in record
    }
    output["status"] = "EVALUATED"
    output["predicates"] = _predicate_witness(record)
    return output


def build_oil_decision_witness(
    detection: PhaseDetection,
    node: OilSequenceNode,
    refs: tuple[OilCandidateRef, ...],
    *,
    material_phase: OilMaterialPhase,
    material_phase_reason: str,
    material_phase_owner_chain: tuple[str, ...],
    material_phase_diagnostics: dict[str, object],
    phase_admitted_row_hypothesis_ids: frozenset[str],
    publishable_row_hypothesis_ids: frozenset[str],
) -> dict[str, object]:
    """Serialize already-computed Oil decisions without evaluating authority."""

    selected_ref = node.candidate_ref
    rows: dict[str, dict[str, object]] = {}
    for ref in refs:
        row_id = ref.row_hypothesis_id
        row_key = row_id or f"UNASSIGNED:{ref.candidate_offset:03d}"
        row = rows.setdefault(
            row_key,
            {
                "row_hypothesis_id": row_id,
                "tracklet_id": ref.tracklet_id,
                "phase_admitted": (
                    row_id is not None
                    and row_id in phase_admitted_row_hypothesis_ids
                ),
                "publishable": (
                    row_id is not None
                    and row_id in publishable_row_hypothesis_ids
                ),
                "members": [],
            },
        )
        members = row["members"]
        assert isinstance(members, list)
        members.append(
            {
                "candidate_offset": ref.candidate_offset,
                "source": ref.candidate.source,
                "y": float(ref.candidate.y),
                "authority": ref.authority.name,
                "authority_reason": ref.authority_reason.value,
                "phase_identity": ref.phase_identity.value,
                "tracklet_lifecycle": ref.tracklet_lifecycle.value,
                "tracklet_admitted": ref.tracklet_admitted,
                "selected": selected_ref is not None
                and ref.frame_offset == selected_ref.frame_offset
                and ref.candidate_offset == selected_ref.candidate_offset,
            }
        )

    def route(status_key: str, records_key: str) -> dict[str, object]:
        if status_key not in material_phase_diagnostics:
            status = "UNAVAILABLE"
        else:
            status = (
                "EVALUATED"
                if bool(material_phase_diagnostics.get(status_key))
                else "NOT_EVALUATED"
            )
        records = material_phase_diagnostics.get(records_key, [])
        if not isinstance(records, list):
            records = []
        return {
            "status": status,
            "evaluations": [_evaluation_witness(item) for item in records],
        }

    selected = None
    if selected_ref is not None:
        selected = {
            "candidate_offset": selected_ref.candidate_offset,
            "source": selected_ref.candidate.source,
            "y": float(selected_ref.candidate.y),
            "tracklet_id": selected_ref.tracklet_id,
            "row_hypothesis_id": selected_ref.row_hypothesis_id,
        }
    return {
        "schema_version": DECISION_WITNESS_SCHEMA_VERSION,
        "identity": {
            "glass_id": detection.glass_id,
            "frame_index": detection.frame_index,
            "time_sec": float(detection.time_sec),
            "layer": "sequence",
        },
        "phase": {
            "value": material_phase.value,
            "reason": material_phase_reason,
            "owner_chain": list(material_phase_owner_chain),
            "allowed_mode": material_phase_diagnostics.get(
                "allowed_mode", "UNAVAILABLE"
            ),
            "allowed_tracklet_ids": material_phase_diagnostics.get(
                "allowed_tracklet_ids"
            ),
        },
        "routes": {
            "direct": route("release_evaluated", "release_evaluations"),
            "recovery": route(
                "recovery_evaluated", "recovery_ordered_predicates"
            ),
            "delayed": route(
                "delayed_reacquisition_evaluated",
                "delayed_reacquisition_seed_predicates",
            ),
        },
        "rows": list(rows.values()),
        "selection": {
            "resolved_kind": node.kind,
            "selected_candidate": selected,
        },
    }
