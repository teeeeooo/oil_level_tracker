# Chromatic overlay support guard

This bounded candidate changes only `_digital_overlay_mask` in the shared
preprocessor. The accepted baseline and adoption decision remain in the
[Work Plan](../00-project/work-plan.md). It does not promote the closed RGB model.

The [component audit](../50-diagnostics/s11/2026-10-14-overlay-component-review/readout.json)
shows an input-representation failure: a 103×29 chromatic parent in the reviewed
fluid-interface region becomes a 72×7 core after horizontal opening. The old
predicate interprets that core as a thin HUD stroke and masks its halo. Actual
Base HUD controls have parent heights 10–14 pixels and retain their thin shape.

## Contract

Keep the existing color thresholds, geometry-relative width/height/aspect
requirements, morphological opening and halo dilation. In addition to the opened
core, require every original non-background connected component supplying that
core to satisfy the **same** thin/wide requirements. Background pixels introduced
by even-width morphology are not supporting components. No supporting component
means no overlay classification. Connected thick material is insufficient evidence
of a digitally encoded line; it is not thereby a positive Oil or Foam label.

Saturation and low-chroma caustic opposition remain independent and unchanged.
The effective mask, Recipe, Artifact templates, Local XY, candidate generators,
Oil/Foam authority, sequence owners and publication rules are unchanged. There
are no source IDs, timestamps, reviewed coordinates or learned thresholds in the
production rule. A true HUD connected to a thick colorful region may remain
unclassified by this conservative guard; report that limitation and do not tune
against an exposed frame to recover it.

## Verification and stopping rule

1. Reproduce the thick-cap failure in synthetic preprocessing tests; preserve a
   separate real/synthetic HUD, saturation and vertical caustic controls.
2. Freeze source and a [paired plan](../50-diagnostics/s11/2026-10-14-overlay-component-review/comparison-plan.json).
   Compare original A/B plus Base 150/151/240 with identical source pixels and
   Recipes. B must regain complete upper patches; A and the Base masks must be
   byte-identical. Exercise `OpenCvPhaseDetector.detect(debug=True)` and verify
   its emitted mask equals the directly computed mask. This is availability and
   entry-path validation, not accepted position or physical discrimination.
3. Reuse the existing four-window report/witness runner serially, each source
   and variant in a fresh process, and the unchanged 13-case legacy comparator.
   Substitute only the pinned original preprocessor at both production import
   sites for baseline runs; every other source remains the frozen candidate.
   Preserve all 299 rows, all 13 legacy results, changed rows, provenance, runtime
   and source identity. sample3 uses per-command engineering purpose only;
   physical acceptance remains NOT_EVALUATED. No tuning from its replay.
4. Fail the local repair if HUD preservation, protected legacy agreement or
   provenance fails. Do not reinterpret restored pixels as solved selection,
   movement/report behavior or native training labels. If local gates pass,
   target-Windows behavior remains a separate required qualification.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `FOAM-CANDIDATE`
- Failure-registry entries: `S11-F02`, `S11-F06`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: unchanged R6 chromatic overlay/optical masks; bounded B input qualification and received regional role; D2 and Local XY closures; rim-falsified candidate RGB trial.
- Prior mechanisms rejected: no global glare relaxation, sample-specific exception, crop/scale or cutoff search, RGB retraining, Artifact/exclusion retry or role transfer from patch availability.
- Preserved contracts: one generic mask; independent Oil/Foam authority; original same-frame candidates; fail-closed missing/ambiguous evidence; frozen previous results and original Recipes.
- Existing feature coverage: ellipse/margin and existing default preprocessing run for original Recipes. A/B and Base have no exclusions or Artifact templates. Four-window setup uses existing session/initial-state confirmation and static-reference preparation; Local XY is OFF. D2/Local XY are not reopened.
- Execution scope: planned synthetic and actual-frame preprocessing/detect checks plus the existing completed-window pipeline/report engineering replay. Baseline substitution is confined to the two preprocessing call sites; no private Windows media or new model is executed.
- Difference from prior failures: the additional check retains the original component's geometry before morphology discards its body; it supplies no candidate identity, trained representation or tracker authority.
- Logic-map impact: UPDATED — describes the original-component prerequisite inside the existing shared evidence owner; routing/order is unchanged.
- Failure-registry impact: NONE — this bounded representation repair tests F02/F09 while preserving F06/F10; it supplies no new field verdict.
