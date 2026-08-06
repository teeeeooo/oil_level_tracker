# S11-C Full-Video Production Replay and Visual Forensic Attribution

## Authority and status

S11-C is a read-only diagnostic stage inside `S11 — Real-Field Detector Effectiveness Recovery`. The `S11-C` label is a milestone slice, not an Engineering Workflow Lane C classification. It does not authorize detector source, threshold, Recipe, truth, schema, dependency or runtime-contract mutation. The purpose is to reproduce the field failure class on the Mac local corpus with the actual current production pipeline, then attribute the loss of usable Oil evidence to the responsible current-frame/temporal owners before selecting any S11-D repair.

**Status:** `COMPLETE — exit criterion met; S11-D1 selected`

**Starting production identity:** `main @ c1eb10cb948feccbce438e9e27008824f53baf33`

Detailed S5-B observability and S5-A Foam contracts remain authoritative. S11-C must preserve the distinction between visual/physical truth, current observable evidence and accepted production outcome.

## Evidence that opens S11-C

### Windows canonical is green

The portability-repaired source tree passed the full Windows 11 canonical suite from a GitHub ZIP of the authoritative source with no source edits:

- Windows `10.0.26200`;
- Python `3.14.3`, pytest `9.1.1`, PySide6/Qt `6.11.1`;
- command `python -m pytest`;
- `1321 passed, 0 failed, 23 skipped`, exit `0`, `113.14 s`;
- `16` skips were explicit `S11 local corpus NOT AVAILABLE` because all four ignored MP4s were absent;
- `7` skips were Windows symlink-privilege limitations;
- no unexpected skip family, material warning, hang or crash.

This closes the portability/canonical blocker. It does not establish detector effectiveness.

### Current Windows field BASE still fails after accepted S11 production changes

Controlled field re-validation on the private company video is still diagnostic and the private video remains outside the repository. The reported BASE result already shows a severe effectiveness failure on `1441` analyzed frames:

- valid frames: `0`;
- raw Oil publications: `2`; reported raw Oil range `-31.3..81.7 px`;
- raw Foam publications: `2`;
- fill state: `UNKNOWN_REVIEW 1441/1441`;
- decision status: `ambiguous 1436`, `no_interface_accepted 3`, `boundary_accepted 2`;
- dominant reason: `competing_boundary_artifact_or_no_interface_evidence 1436`;
- candidate proposals: `10,730`, about `7.4/frame`, but only `4` selected (`0.3%`);
- `oil_boundary_score` min/max/mean `0.203 / 0.384 / 0.278`;
- `oil_artifact_score` `0.000 / 0.495 / 0.341`;
- `oil_ambiguity_score` `0.000 / 0.646 / 0.530`;
- `oil_no_interface_score` `0.000 / 0.662 / 0.421`;
- `oil_no_interface_uniformity` `0.000 / 0.961 / 0.002`;
- `oil_decision_confidence` `0.196 / 0.662 / 0.321`;
- overall confidence min/max/mean `0.158 / 0.350 / 0.158`;
- dominant flags: `FOAM_COMPONENT_REJECTED;LOW_CONFIDENCE;OIL_EVIDENCE_AMBIGUOUS;REVIEW_REQUIRED` on `1413` rows, `FOAM_EVIDENCE_AMBIGUOUS;LOW_CONFIDENCE;OIL_EVIDENCE_AMBIGUOUS;REVIEW_REQUIRED` on `22`, and `LOW_CONFIDENCE` on `3` among the reported top groups.

User/LVLM review reports a clearly visible Oil boundary at multiple points including approximately `480`, `504`, `701`, `800`, `900` and `1000 s`. The dominant contradiction is therefore not lack of edge proposals: visually usable Oil exists and candidates are plentiful, but boundary evidence remains weaker than artifact/ambiguity competition and the tracker receives `NO_UPDATE` almost everywhere.

The near-zero BASE no-interface uniformity mean must not be described as proof that PR #85 disabled the uniformity metric. PR #85 changed the accepted no-interface weighting, not the uniformity calculation. S11-C should instead determine why the current normalized scene produces that evidence and whether it is material to the final rejection.

The user also reports a repeatable setup-time contradiction on the same low-transparency/whitish sight glass: after fitting the ellipse to the glass, the preview reports review-needed state, about `16%` confidence, "Oil boundary not in frame" although the boundary is visually near the glass center, and "Foam possible" despite no visible Foam. This is diagnostic evidence, not truth, but it makes low-transparency glass / Foam-like appearance a specific S11-C attribution target.


### Blind 68-frame evidence shows multiple residual modes

The frozen S6-C agent-assisted silver annotations remain unchanged and were created before detector output was inspected. Fresh current-S11 exact-frame comparison found:

- `60` usable rows: `22` visible boundary, `16` no-interface, `22` unclear;
- visible Oil numeric publication `15/22`, but only `7/22` lie inside the frozen visual point/range;
- sample3 visible Oil `0/6`, all six ending in ambiguity;
- sample4 visible Oil `15/16`, but `8` numeric results are outside the frozen range;
- frozen no-interface rows contain `6/16` numeric disagreements, with known silver/user-truth conflict on some sample2 frames;
- frozen Foam-present rows publish Foam `0/5`, while Foam-absent rows publish Foam on `17/24`;
- sample4 publishes Foam on all `16/16` visible rows, including all `10/10` discernible frozen Foam-absent rows;
- Spatial adds no frozen-visible recovery in this 68-frame set and owns all six silver no-interface numeric disagreements, but later user-confirmed sample2 truth prevents treating those six as proven false positives.

This evidence is sufficient to reject a single global-threshold explanation. It is not sufficient for general detector-accuracy PASS.

## S11-C objective

Replay all four Mac local videos through the actual current production analysis/detector path so temporal Foam gating, serialized Oil ownership and tracker behavior are exercised at real cadence. Use the replay output to choose a bounded set of representative frames for direct visual review and candidate-level forensic decomposition.

The four required local MP4 identities remain the checked-in S11-A manifest hashes. Missing corpus is `NOT AVAILABLE`; present wrong identity is a hard failure; correct identity followed by decode failure is a hard failure.

## Generated-output isolation contract

Generated analysis bundles, CSVs, debug images and forensic scratch output are temporary evidence and must not become Git authority. Use the already ignored hierarchy, for example:

`sample/output/s11-c-full-video-forensics/<run-id>/...`

Before and after replay, verify the path is ignored and the repository remains clean. Do not add a new `.gitignore` rule merely for S11-C. Temporary output may be retained through the diagnostic for inspection and then removed by the owning Worker/cleanup step when no longer needed.

A generated bundle is not a golden regression fixture. Reproducibility comes from source identity, MP4 identity, Recipe, execution protocol and compact recorded expectations.

## Full-video replay evidence

For each of `base_sample_1`, `sample2`, `sample3` and `sample4`, report at least:

- analyzed/sampled frame count and cadence/window;
- valid/publication counts for raw/smoothed Oil and raw/smoothed Foam;
- fill-state distribution;
- boundary / ambiguous / no-interface / unavailable decision distribution;
- tracker accept versus `NO_UPDATE` distribution;
- proposal/candidate count and selected count;
- boundary, artifact, ambiguity, no-interface and decision-confidence score distributions;
- dominant flags/reasons;
- material temporal transitions or long missing streaks.

The goal is to compare actual stream behavior, not to infer accuracy from aggregate publication rate alone.

## Representative-frame visual forensics

After the full replay, choose only a bounded diagnostic sample rather than reviewing every frame. Selection may use detector output because these frames are for root-cause attribution, not unbiased accuracy measurement. Keep the independent 68-frame silver evidence separate.

Cover materially different outcomes such as:

- visually clear Oil but production ambiguity / `NO_UPDATE`;
- correct accepted Oil;
- accepted Oil at a visibly wrong Y;
- Foam publication where direct visual review sees no Foam;
- repeated `FOAM_COMPONENT_REJECTED` / `FOAM_EVIDENCE_AMBIGUOUS` scenes;
- accepted no-interface if present;
- Spatial-dependent recovery or suspicious Spatial selection;
- transitions between success and failure in the same video.

For each selected frame, inspect the source frame/ROI directly and compare the visual Oil range with every material Oil candidate, not only the final winner. Record candidate Y/rank and the load-bearing evidence that explains proposal, ranking and acceptance/rejection, including broad/narrow phase strength, scale/polarity consistency, horizontal coverage, visibility/availability, glare/exclusion/static-artifact pressure, boundary/artifact/ambiguity likelihood and Spatial evidence when applicable.

Inspect Foam on the same frames using current whiteness, texture, component geometry, bottom connection, glare overlap, score, temporal status and accepted/rejected state. A low-transparency or whitish sight glass may create Foam-like support because the current Foam owner uses whiteness plus texture/component evidence; S11-C must determine whether that is merely a correlated optical symptom or whether accepted Foam context directly suppresses/re-routes Oil evidence.

Read-only counterfactuals may disable one existing evidence route at a time for attribution, but they must not be reported as production behavior or used to tune a threshold in this stage.

## Required attribution decision

S11-C should distinguish, where evidence permits, among:

1. true Oil candidate not generated;
2. true Oil candidate generated but under-scored;
3. true Oil candidate loses ranking to glass/structure/artifact evidence;
4. candidate is credible but canonical identifiability/acceptance rejects it;
5. Foam evidence or accepted Foam context materially masks/re-routes Oil;
6. Spatial selects or reinforces the wrong evidence class;
7. multiple distinct modes requiring separate owners.

The current evidence already favors multiple modes. S11-C exists to make that attribution reproducible enough to choose a bounded repair, not to prove a preselected theory.

## Regression strategy after attribution

Do not track full output bundles. If a later repair is authorized, distill the demonstrated defect into the smallest reproducible regression surface: exact local frames and/or short production replay windows, compact expected outcomes and the existing local-corpus identity contract. The repair PR should add only the minimum assertions required to prevent recurrence.

The existing portability rule remains: local MP4 absent means explicit corpus-dependent skip, wrong identity hard-fails, and no partial aggregate is accepted. This preserves regression value without redistributing videos or committing large generated bundles.

## Exit and next gate

S11-C is complete when the full-video replay plus representative visual forensics can explain why clearly visible Oil is accepted in some local scenes and rejected in others, and can state which current owner(s) must change next. Additional blind annotations are added only if the existing 68 independent rows plus full replay cannot separate the material failure modes.

No source repair is performed inside this diagnostic. A subsequent S11-D repair is separately classified from the proven blast radius; shared S5-A/S5-B observability, Foam/Oil responsibility or validation-architecture changes remain Lane C candidates, while a truly bounded existing-owner defect may qualify for Lane B.

Detector/general-field accuracy PASS, S11 completion and S12 start are not implied. S12 remains a separate UI/UX successor after a stable S11 detector baseline.


## Completed result and handoff

The completed replay/forensic execution met this document's exit criterion without source, test, Recipe, truth or tracked-document mutation. The local stream reproduces the Windows ambiguity/NO_UPDATE class and separates multiple residual owners. The decision-bearing new evidence is the causal sample4 Foam-context interaction: structural/refractive support can become accepted Foam, and removing only that accepted context from S5-B removes all sample4 Oil publication in the counterfactual replay.

The next source gate is [S11-D1 Foam Structural/Refractive Discrimination and Oil Context Safety](../../60-evidence/s11/s11-d1-foam-structural-refractive-discrimination-oil-context-safety.md). sample3 candidate-generation/identifiability remains a later S11-D2 concern. No new blind annotation is required.

The ignored forensic root is intentionally preserved through the next repair gate:

`sample/output/s11-c-full-video-forensics/s11c-20260805T161456/`

Its recorded hash-list fingerprint is `9dc96fc04f9dcb1e00f5c120650ce6953e26239a0ecb61278cd6287b40519370`. It remains temporary non-Git authority.
