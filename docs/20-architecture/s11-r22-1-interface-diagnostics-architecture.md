# S11 R22-1 Interface Diagnostics

R22-1 implements only the measurement stage of the
[physical-interface repair proposal](s11-physical-interface-evidence-repair-design.md).
It does not implement interface classification, independent-support promotion,
association changes, handoff changes or the proposed observation phase.

## Identity and isolation

- Detector/package identity: `opencv-phase-detector-r22-1-interface-diagnostics-v1`.
- Completed sequence/Oil resolver: `r22-oil-ownership-evidence-replacement-v1`, unchanged intentionally.
- Added trace payload schema: `r22-1-interface-raster-diagnostics-v1`.

`PhaseDebugProjector` calls `measure_oil_interfaces` after current detection is
complete, only when debug artifacts are requested. Measurements go solely to
`artifacts.state.oil_interface_diagnostics`. They do not enter candidate
features/penalties, detection debug metrics, resolver inputs, state, scores,
selection or publication. Trace NONE does not invoke the measurement function.
No new frame history, proposals or temporal owner is introduced.

## Measurement contract

The function reads the unresized current grayscale crop, effective/glare masks,
raw combined material-evidence raster and optional learned static map. Raw
material is not accepted Foam authority. All Oil candidates are included,
irrespective of rejection, admission or selected status; Foam candidates are
not measured. There is no new top-k filter. Existing candidate production bounds
remain in force.

The crop width is split into five fixed sectors. Band width is
`clamp(round(crop_height * 0.01), 3, 12)` pixels. Candidate local Y is source Y
minus crop origin Y; exact fractional Y is retained and the sampling center is
`floor(local_y + 0.5)`. With center `c` and band width `b`, half-open bands are:

- near above `[c-b-1, c-1)` and near below `[c+2, c+b+2)`;
- far above `[c-3b-1, c-2b-1)` and far below `[c+2b+2, c+3b+2)`.

This excludes the center and its immediate neighbors. Each band records gray
mean/std on the 0--1 scale, raw material mean, static overlap, glare fraction,
valid pixel count/fraction, availability and reason. A band must be completely
inside the crop, have at least eight valid pixels and at least half its area
valid. These are measurement-availability bounds, not Oil acceptance thresholds.
Missing material/static channels remain null with explicit availability; clipped
or obscured gray bands cannot produce valid contrast.

Per sector, record below-minus-above near and far signed contrast, their
absolute-strength difference and the strongest central-difference row gradient
within `c +/- b`. Peak Y is a diagnostic maximum, not a replacement candidate
coordinate or an inferred contour. Equal peaks choose the smaller Y; a flat
profile has no peak. Keeping five sector peaks exposes tilt/curvature that a
single median can hide. A separate summary reports usable near sectors and
median signed contrast; no score or interface decision is derived.

Gray, material, edge and generator labels do not assert independent evidence.
The payload says `diagnostic_only=true` and `classification=not_evaluated`.
Current measurements are inputs to later human/source review, not proof that
two image structures can already be classified reliably.

Frame-local prefix sums have O(crop pixels) construction work and O(crop height)
storage per fixed sector/channel. Every candidate has five sectors and four
bands; no frame raster is retained by this module after return. Serialization
size is linear in the existing Oil candidate count. FULL trace still has the
existing image/storage cost; BASIC still uses the existing sparse capture policy.

## Provenance and trace

Both BASIC and FULL captured records contain
`state.oil_interface_diagnostics`. NONE contains none. The payload includes the
source frame index, crop origin/size, source-Y direction and no-resize contract.

Each measurement's `candidate_input_index` joins to the same named field newly
added to top-level trace `candidates`. It refers to the original
`detection.candidates` position before score sorting. Rejected and duplicate
rows retain distinct indices. It is not a sequence witness `candidate_offset`
or the serialized array position. Matching sequence rows additionally requires
source/Y/identity inspection; this change does not redefine legacy offsets.

The [validation/evidence](../60-evidence/s11/s11-r22-1-interface-diagnostics.md)
records local verification. R22's field failure remains; Windows measurement
collection is the next use of this diagnostic candidate.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R22 false-to-real association, broad texture peer exclusion, R10/R11 smooth wrong-identity paths, and corrected Windows coordinate/candidate inventories.
- Prior mechanisms rejected: using a scalar/peak/source label as identity, filtering rejected diagnostic candidates, changing thresholds or resolver state to improve coverage, and interpreting crop coordinates as source Y.
- Preserved contracts: unchanged R22 Oil/Foam decisions, current-frame coordinates and provenance, bounded diagnostics, no interpolation or new candidate authority.
- Difference from prior failures: independent trace-only measurements expose spatial context without participating in any production decision; original input indices preserve joins after score sorting.
- Logic-map impact: UPDATED — the runtime identity and debug-only measurement route are documented; resolver behavior is unchanged.
- Failure-registry impact: NONE — this adds observability for existing failure classes and makes no repaired-field claim.
