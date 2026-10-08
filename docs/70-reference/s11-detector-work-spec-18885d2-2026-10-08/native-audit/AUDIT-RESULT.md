# S11 current detector design audit — result

Source: main @ `18885d226a7a7745bc2d062fd750ec263b9c78f6`.
This folder contains new ignored audit evidence, not a production patch.

## Executed in this audit

- `inspect_samples.py`: 42 selected source frames across four Mac samples; contact sheets inspected; source video and recipe hashes preserved. Not exhaustive video truth.
- `verify_saved_sequences.py`: current unchanged `ObservationSequenceResolver`, 113 complete detections per stored variant, 226/226 entire outputs equal; 230 input pins preserved.
- Focused baseline tests: `225 passed in 103.63s (0:01:43)`, exit 0. This test result is transcribed from actual tool process output, not a saved pytest log.
- Test files: unit `test_artifact_reference.py`, `test_artifact_calibration.py`, `test_artifact_proposal.py`, `test_oil_interface_tracklets.py`, `test_oil_observation_resolver.py`, `test_oil_phase_lifecycle.py`, `test_foam_episode_resolver.py`; GUI `test_artifact_support_review.py`.
- Tracked tree remained clean; HEAD unchanged; `git diff --check` and detector governance passed.

## Decision

Continue with a bounded diagnostic comparison of explicitly reviewed structural reference support and the current candidate's actual measurement lineage. Do not equate overlap with artifact identity or no-match with fluid authority. Preserve mixed/unavailable support and legacy behavior.

Require whole-sequence target preservation before behavioral adoption. The registered Y822 variant reproduces later losses: 49.5 s Y836->880; 52 s Y833->862. Do not restore the false predecessor, remove physical-proposal guards or relax global gates to recover counts.

D1 is CLOSED with corrected 73=45 retained+28 absent. O2 remains OPEN and Windows FIELD FAIL remains. No new detector efficacy, Windows execution, label change, original recipe change, tracked document change, commit or push occurred.

## Delivered specification

The conversation attachment `S11-detector-design-and-work-spec-18885d2-2026-10-08.md` contains the full Korean design, D2-D6 work packages, canonical Windows nine-segment acceptance, controls, resource/compatibility/rollback and one-cycle go/no-go rules. The full attachment is not copied into this native folder. `docs/00-project/work-plan.md` remains the current-state authority.
