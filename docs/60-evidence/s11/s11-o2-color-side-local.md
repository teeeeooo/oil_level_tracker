# S11 recorded-band color-side measurement — local verification

Date: 2026-10-02. Starting repository HEAD: `5e3ec32d93bcf047a6350dff0dd2d1cb8c9f42c3`.
Scope: offline diagnostic source, tests and contracts. No production detector,
O1 trace, label, threshold or accepted field state changes.

## Question and implementation

The [candidate-guided human rationale](s11-o2-identity-context-windows-review-001.md#candidate-guided-human-rationale-received--2026-10-02)
identified apparent side transparency/subtle color and a traversing reflective
boundary for Accum idx10, absent at idx15. Existing positive/negative labels are
retained. The answer is qualitative, not calibrated transparency, exact region
truth or permission to treat gray alignment as identity.

The existing saved-output adapter now accepts `--color-side`; the existing
spatial probe owns `measure_color_side`. It consumes original spatial-context
BGR/gray/effective/glare rasters and recorded bands. It reuses receipt, artifact,
raw identity, geometry/center binding, baseline and preservation gates. It does
not introduce a second loader, detector, video decoder or color-space search.

The [contract](../../20-architecture/s11-interface-observability-witness-architecture.md#w4-recorded-band-color-sides--saved-output-measurement)
fixes B/G/R/gray code-value units, identical visible pixels, per-column
below-minus-above, equal column weights and separate near/far vectors. Opponent
changes B-G/R-G expose chromatic variation but do not label its cause. Empty or
O1-unavailable pairs stay null; partial band observations are explicitly
ineligible. Source X order is retained, vertical band order is averaged.

Output schema: `s11-o2-color-side-v1`; spec: `recorded-band-color-side-v1`.
Three hashed outputs (`experiment.json`, `summary.md`, `color-side.csv`) plus
COMPLETE receipt. Full input recheck precedes the last receipt write.

## Local verification

Executed with repository `.venv/bin/python`:

```text
python -m pytest -q tests/unit/test_s11_spatial_context_probe.py tests/unit/test_s11_spatial_context_run.py tests/unit/test_s11_joint_context.py tests/unit/test_s11_color_side.py
98 passed
```

Nineteen color-specific controls plus shared color/default-mode input guards and
two-case geometry controls cover:

- BGR `[0,0,100]` to `[0,51,0]`: both OpenCV gray30, side delta
  `[0,51,-100,0]`; reversed polarity reverses the vector. This demonstrates
  retained color information, not a whole-O1 witness collision or physical truth.
- Achromatic steps, including zero: opponent deltas zero, observed state retained.
- Mask/glare-hidden color changes: no leakage. Empty and disjoint-column support:
  no fabricated delta. Unequal per-column counts: equal-column result remains
  distinct from pixel-weighted band averaging. Negative differences do not wrap.
- Recorded unavailable/clipped bands: partial observations remain visible in
  diagnostics but pair deltas are null. Count/range/shape/gray/duplicate/resource
  violations reject execution.
- Actual producer fixture, Unicode non-repository CLI cwd, closed stdin and
  explicit UTF-8: native/center roles, exact aliases, CSV numbers, all output
  hashes and source-byte preservation. Two cases keep their own frame/Glass.
- Saved non-gray BGR fixture with unchanged gray180/80: expected near-side delta
  `[-86,-100,-106,-100]` and opponent `[14,-6]` without a new joint gradient map.
- Shared malformed-source guards run in both modes; mutation during color
  measurement/publication and BGR-to-gray mismatch leave no COMPLETE receipt.
- Existing spatial-source and default unpooled-joint regressions remain passing.

These are local synthetic controls, including the real adapter entry. They do
not claim native Windows execution, private RGB separation, physical identity,
calibrated optical transmission or a validated ranking/operating point.

## Code identity for handoff

The local artifact fingerprint over schema/spec/seven code hashes is:
`3425f2db6f176ed52db382b4c2b4db4e94a6cccbf516e6270005ad8806815bcf`.
This is the new diagnostic's code/spec identity, not a private measurement result.

| File | SHA-256 |
|---|---|
| `tests/diagnostics/s11_joint_context_run.py` | `25e2b5c877c8243a4f6db418acaac9acb36a28ad5bf3dbaf504c8d9dc719e726` |
| `tests/diagnostics/s11_spatial_context_probe.py` | `95e3619650da9dc9b31876ed1072608beb9c958deb8ae44cec2273200d7507b7` |

The input source artifact remains
`6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910`.
Original source-runner bytes and production code are unchanged. The retained
joint output is not regenerated; new runner/probe bytes naturally change a future
joint-mode code fingerprint and do not revise old receipts.

## Windows boundary and remaining unknown

Follow [Color-side measurement — existing saved outputs](../../40-operations/s11-o2-local-shadow-evaluation.md#color-side-measurement--existing-saved-outputs)
on the existing spatial-context-001 directory. Return machine summary, 3-output
hash checks, 32-input preservation and fixed CSV subsets: Accum idx10/15 native
all five sectors/three widths/near-far; BASE idx11 native support; unresolved
idx0/20 center control. Numeric arrays remain local. No new human question,
video/bundle read, label edit, overlay or detector run is required.

Whether private color sides differ usefully, overlap, or become unavailable is
unknown until that measurement. Reflections and illumination can create identical
color evidence; the same data cannot independently establish causality. Existing
mask construction may remove color cues. No universal sign, magnitude rule,
spatial continuity or identity gain follows from this diagnostic. W4-R1 remains
closed without promotion; W4-R2 and O2 acceptance remain unmet, FIELD FAIL /
NOT_EVALUATED unchanged. [Validation owner](../../30-validation/s11-interface-observability-witness-validation.md#recorded-band-color-side-controls)
and [canonical reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
continue to own acceptance and field interpretation.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: private identity failure remains unknown; source review establishes that gray side projections omit chromatic values, but no supplied same-support private color result establishes this as the cause of detector failure.
- Prior mechanisms reviewed: O1 gray/support bands, saved BGR crops, color-dependent glare/Foam owners, row/column pooling and joint-gradient aliases, existing candidate-guided human rationale and unresolved BASE control.
- Prior mechanisms rejected: gray alignment or color magnitude as identity, truth-Y distance, shared reflected appearance as physical continuity, missing-as-zero, label-conditioned pixel selection and private-coordinate thresholds.
- Preserved contracts: generic bounded diagnostic, exact saved geometry/provenance, independent Oil/Foam, unchanged labels, fail-closed unavailable support and separate Windows field acceptance.
- Difference from prior failures: fixed same-pixel channel measurement tests information retention and counterexamples before any classifier; it grants no selection or production authority.
- Logic-map impact: NONE — the saved-output diagnostic does not alter the executing detector path or production publication.
- Failure-registry impact: NONE — no private causal failure or field repair is established by the synthetic color controls.
