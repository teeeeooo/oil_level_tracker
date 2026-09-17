# R23 association experiment closeout — runtime preserved

## Result

The proposed native-polarity association veto was implemented locally and
rejected after regression testing. Its production edits were removed. The
published change contains corrected evidence/design constraints, the archived
non-executing experiment and four regression controls. It does not release an
R23 detector. Runtime remains
`opencv-phase-detector-r22-2-interface-path-diagnostics-v1`; completed resolver
remains `r22-oil-ownership-evidence-replacement-v1`. Field disposition remains
FIELD FAIL and S11 remains active.

The [investigation](../../50-diagnostics/s11/s11-r23-native-polarity-rejection.md)
owns the failure measurements, patch hash, reproduction procedure and latest
human-reviewed localization/identity distinction. The [work plan](../../00-project/work-plan.md)
owns the next implementation gate. No new Windows rerun is requested.

## Verified final scope

- All production source under `src/` is byte-identical to base
  `0963e384e1604b5439e017e5ada2deec5c12b009`, checked with
  `git diff --exit-code 0963e38 -- src`.
- Four positive raster controls cover both translation directions and initial
  contrast polarities before confirmation. They pass on restored source and
  fail against the archived prototype in a disposable baseline checkout.
- `pytest -q -m 'not qt_app'`: **1,531 passed**, 254 deselected.
- `pytest -q -m qt_app`: **254 passed**, 1,531 deselected; **1,785 total**.
- The previously failing two Sample3 owner/continuity tests separately pass
  after restoration. Their assertions, protected truth and golden fingerprints
  were not weakened or updated.
- Source/diagnostic provenance, artifact hashes, changed Markdown links,
  detector governance and whitespace checks pass.

No performance improvement is claimed or needed to justify this publication:
the experiment was rejected and the running source has no new descriptor,
history, association or tracing cost. Prototype replay failures must not be
reported as successful R23 acceptance or a field gain. Earlier R22-2 field
measurements continue to describe the deployed detector.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-TRACKLET`, `OIL-SELECTOR`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: rejected prototype association/confirmation; the final production tree preserves the baseline rather than deploying the regressing veto.
- Logic-map impact: NONE — executing source and runtime identity are unchanged.
- Failure-registry impact: UPDATED — F04 records the failed shortcut and controls that prevent its reintroduction.
