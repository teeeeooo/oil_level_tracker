# S11 Interface Observability Witness Validation

**Contract status:** proposed acceptance for the trace-only and shadow stages of
the [Interface Observability Witness Architecture](../20-architecture/s11-interface-observability-witness-architecture.md).
This contract does not accept a production classifier, temporal association,
owner handoff or direction-neutral phase behavior. The
[work plan](../00-project/work-plan.md) owns the current execution gate.

## Acceptance boundary

The first implementation exists to measure whether current images contain a
defensible Oil/refrigerant interface cue and to describe candidate contour
geometry without changing R22-2 decisions.

A passing O1/O2 implementation must demonstrate all of the following:

- extraction is bounded, deterministic and provenance-preserving;
- unavailable or optically unobservable evidence remains explicit;
- curved/localized contour geometry is retained instead of silently collapsed
  into one physical row;
- multi-cue descriptors and derivation lineage are measured without granting
  candidate authority;
- positive, negative and unresolved controls remain distinct;
- debug/shadow execution cannot change any production candidate, sequence,
  Foam, event, CSV or report output; and
- no operating point is selected from private checkpoint coordinates or from
  the 13 public truth frames alone.

Passing this contract authorizes only the next declared stage. It never changes
`FIELD FAIL` to field-qualified.

## Baseline V0 — completed characterization

The completed
[public probe](../50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md)
and its [machine summary](../50-diagnostics/s11/s11-interface-witness-public-probe-summary.json)
form the pre-implementation characterization baseline:

- 13 usable truth frames from four authoritative public videos;
- original plus six bounded brightness/gamma/contrast transforms;
- 91 frame/transform measurements;
- a candidate within 8 px on all 13 frames for every variant;
- median 23–24 Oil candidates and 3–4 near-truth candidates per frame; and
- substantial overlap in current near/far contrast and peak-offset summaries.

These results establish neither physical identity labels nor classifier
thresholds. `remote_geometry_not_proven_negative` remains an unlabeled geometry
partition. V0 is complete and reproducible, but it does not satisfy any later
behavior gate.

## V1 — typed extraction and invariance

### Data model controls

Construct `FrameOpticalObservability`, `InterfaceContourHypothesis`,
`InterfaceSectorWitness` and `OilInterfaceWitness` only from current-frame inputs
and exact candidate provenance. Required unit controls:

1. straight and curved interfaces with three to five valid sectors;
2. fractional source Y, non-zero crop origin and inset effective-mask geometry;
3. one or more missing sectors, clipped bands and insufficient valid pixels;
4. glare, saturation, border, exclusion and static-map opposition;
5. multiple comparable local peaks and scale-sensitive centers;
6. native material-path geometry and candidate-centered geometry on identical X
   support;
7. duplicate candidates, source/Y mismatch and candidate permutation; and
8. finite-value enforcement for every serialized field.

Missing values remain unavailable/null with a reason. Tests must not convert
missing measurements to zero or infer one sector from another.

### Exact non-behavior contract

Run identical detections with witness capture disabled and enabled. Compare:

- candidate count, order, source, kind, Y, all features/penalties/scores and
  selected/rejected flags;
- current-frame detection state, confidence and flags except the new diagnostic
  namespace;
- completed Oil/FULL/EMPTY sequence resolution;
- final Foam episode and composition;
- `TrackingSample`, events, judgments, CSV and report rows; and
- existing R22-2 diagnostic fields after removing only the new witness member.

Any difference is a failure. The witness sidecar may not enter
`PhaseDetection.debug_metrics`, `OilCandidateEvidenceIndex` or resolver-facing
state during O1/O2.

### Trace identity and joins

Basic and Full trace records must include:

- source frame and Glass identity;
- crop/source transforms;
- pre-sort candidate input identity and exact source/Y join;
- actual sector X/Y ranges and localization uncertainty;
- descriptor availability, derivation lineage and raw opposition;
- `decision=NOT_EVALUATED` in O1; and
- bounded reason lists with strict finite JSON.

A score-sorted trace array index, resolver offset and source-frame index are
separate identities. Tests must exercise sorting, duplicates and completed
sequence annotation without breaking the join.

### O1 concrete extraction controls

Use the measurement definitions in the architecture's O1 contract. In addition
verify an exact step/stripe pair, translated curved paths with polarity reversal,
flat/competing signed plateaus, truncation, fractional coordinate joins, missing
channels, and rejected duplicate/permuted candidates. Hulls are descriptive, not
calibrated confidence intervals. Local shape variation must not widen them.

All existing R22-2 diagnostics must remain equal without removing any old field;
only the sibling `oil_interface_witness` namespace is new. Baseline is source
commit `8842bf1` (same production as R22-2). Snapshot current-frame candidates,
completed decisions, CSV/events and old diagnostics on all four public windows
for NONE/BASIC/FULL, using the same decoder/runtime and serial scheduling.
A changed diagnostic version is expected; detector scores/coordinates are not.

Human-visible frames remain in the evaluation denominator regardless of model
UNOBSERVABLE/UNRESOLVED output. Previously reviewed private checkpoints are
regression controls, never untouched holdout. Acquisition metadata absence alone
cannot invalidate passive RGB evidence.

## V2 — raster controls before shadow classification

### Positive controls

Include at least:

- a low-contrast straight material step;
- a curved interface with different sector Y values;
- a stationary interface with two-sided material change;
- real translation in both directions;
- global brightness, contrast, gamma and exposure-like change;
- contrast-polarity reversal during genuine translation;
- a textured interface whose broad material score is high; and
- partial glare/mask clipping with at least three usable sectors.

The witness must retain the physical curve and uncertainty. Photometric sign may
change without forcing `DIFFERENT_INTERFACE` or an internal-structure label.

### Negative controls

Include at least:

- thin internal bright and dark stripes with similar near contrast;
- wall/fitting/cap/border edges;
- static and moving vessel reflections;
- residue/texture bands on both sides;
- one-sector or spatially disjoint edges;
- duplicate/renamed descendants of one measurement;
- high-gradient glare and saturation boundaries;
- homogeneous opaque FULL-like and transparent low-information scenes; and
- a wrong predecessor followed by a real interface within the existing jump
  bound.

A strong edge, recurrence, source-family count, native path, polarity, motion or
candidate score alone cannot produce positive identity.

### Unresolved controls

Explicitly construct cases where:

- two physical contours remain plausible;
- valid sectors are fewer than the distributed minimum;
- contour centers vary materially with scale;
- reflection and interface evidence overlap;
- reference/background registration is poor;
- exposure metadata or required acquisition reference is unavailable; or
- the interface has no stable cue in the sampled passive image.

Expected outcome is unresolved/unobservable with reasons, not a forced positive
or negative class.

### Localization labels

Controls and human review must distinguish:

- physical interface with acceptable localization;
- physical interface with localization mismatch;
- different internal/optical structure;
- unresolved competing structure; and
- unobservable frame.

A point near the interface but offset cannot be reused as a certified material
negative. Scalar candidate Y is evaluated against contour-sector labels only
where that mapping is meaningful.

## V3 — operating-point discipline

Before a shadow classifier is allowed to emit
`INTERFACE_SUPPORTED`, `INTERNAL_OR_ARTIFACT` or `UNRESOLVED`:

1. freeze a labeled raster/control manifest with source identity, label owner and
   intended use;
2. separate development, calibration and held-out cases before choosing numeric
   operating points;
3. keep photometric transforms of one source case in the same partition;
4. keep descendants/nearby frames from one physical episode in the same
   partition unless leakage is explicitly ruled out;
5. do not use the already selected private checkpoint coordinates as ad hoc
   threshold targets; any private field calibration requires a predeclared
   work-PC-only episode-level development/calibration/holdout split;
6. report confusion by physical label, not only mean Y error;
7. report unresolved coverage separately from wrong positive/negative decisions;
8. retain raw scalar evidence and lineage next to the typed outcome; and
9. document every selected operating point and all holdout results.

The 13 public truth frames may test geometry/proposal recall and robustness but
lack certified negative identity labels. They cannot, by themselves, calibrate
an interface classifier.

Required shadow metrics include:

- interface-supported precision/recall on labeled controls;
- internal/artifact rejection by negative family;
- unresolved/unobservable rate by evidence-availability condition;
- per-sector and aggregate localization error;
- uncertainty coverage: reviewed contour must fall inside the declared interval
  at the reported rate;
- photometric-pair decision consistency where physical identity is unchanged;
- duplicate/lineage independence violations; and
- wrong-structure support count, which is reported explicitly even when final Y
  happens to be near truth.

No universal numeric acceptance threshold is invented by this document. The
first implementation proposal must present measured distributions and a bounded
operating point for review before O3 behavior work.

### O2 evaluation-tool acceptance

The offline foundation uses `s11-o2-review-packet-v1`, `s11-o2-labels-v1`,
`s11-o2-frozen-labels-v1` and `s11-o2-shadow-predictions-v1`. The
[operational procedure](../40-operations/s11-o2-local-shadow-evaluation.md)
defines fields and invocation. Required controls for this foundation are:

- real bundle → indexed exact-frame lookup → complete raw/witness candidate join;
- source/frame/Glass mismatch, duplicate IDs and absent witness rejection;
- no candidate filtering by score, selected/rejected status or authority;
- freeze refusal of pending visibility, altered packet/candidate/label hashes, missing
  frames/candidate labels and nonfinite values;
- recording-group partition locking, same-run alias prevention and regression-only
  handling of already reviewed cases; no random adjacent-frame partition;
- visible empty-candidate frames, missing predictions, unknown labels and
  abstentions retained in their proper denominators;
- physical identity versus localization-mismatch labels and family-specific wrong
  support counts; exact-X localization and explicit unmatched measurements;
- imported prediction identity, frozen-label targeting and operating-point
  declaration checks, without claiming verification of model internals;
- no-prediction readiness emits NOT_EVALUATED, never PASS;
- deterministic results, no-overwrite output and execution from a non-repo cwd
  with UTF-8/non-ASCII paths.

Durable review controls additionally require:

- loading and editing existing v1 drafts without regenerating packets or labels;
- archive-before-atomic-replace, stale-revision/overlapping-writer rejection and
  failed-save preservation with a successful retry;
- scene review provenance unchanged by a candidate-only correction; omitted
  candidates/frames unchanged and all inventories still checked;
- a moved data tree remains readable without the old code path; existing frozen
  labels remain unchanged after later draft corrections;
- real indexed bundle linkage, including rejection of a modified packet even if
  its local hash was recomputed, and exact bundle/video checks on relink;
- unverified initial video association explicitly recorded as human attestation,
  different source bytes and changed trace rejection, non-ASCII paths and CLI
  dispatch from a foreign cwd;
- absent live paths reported without losing the archived judgments, and Windows
  cross-drive locator handling without placing paths in content identity;
- no candidate-label transfer across executions and no physical inference from a
  source hash, filename, candidate index, static Y or geometry proximity.

Synthetic scripted predictions test metric arithmetic and guards only. They are
not an image classifier, V2 discrimination evidence or an untouched holdout.
Every report remains non-qualifying. For tooling-only changes with no detector
imports used for execution and no runtime wiring, focused controls plus the
canonical suites establish this boundary; repeating all four detector replays
is required only if extraction/production execution changes or evidence is
otherwise invalidated. Existing O1 equality evidence remains authoritative.

## V4 — public-video equality and resources

Run all four authoritative public videos under the current qualification windows
with witness capture/shadow disabled and enabled.

Required equality during O1/O2:

- every tracking row and event row except run identity;
- all raw candidates and completed sequence objects;
- all existing diagnostic fields after excluding the new namespace;
- Oil/Foam validity and numeric coordinates;
- report presentation and captures; and
- deterministic rerun fingerprints under the same recorded runtime.

Record runtime provenance, wall time, peak memory, trace bytes and per-frame
witness counts. The implementation must retain fixed bounds from the architecture:
existing candidate limits, five sectors initially, fixed scales/peak count and no
temporal raster history. A resource regression is reported and reviewed; it is
not hidden by asynchronous execution or a different sampling window.

Run the full canonical non-Qt and Qt test groups in separate process groups,
plus detector governance and whitespace/link checks. Historical Sample4 runtime
provenance remains unresolved and its golden is not silently replaced.

## V5 — target-Windows shadow qualification

The work-PC runner may retain private media locally and export only policy-
permitted bounded numeric/decision reports. Each evaluated frame/segment must
record the exact candidate runtime, witness schema, Recipe/Glass identity and
source-frame mapping.

Review by canonical segment and physical label:

- proposal/contour recall for reviewed visible interfaces;
- supported-interface, wrong-structure and unresolved outcomes;
- per-sector localization and uncertainty coverage;
- frame observability status and reason;
- association split/merge errors once O3 is separately implemented;
- final numeric Oil accuracy/coverage only after behavior is enabled;
- false numeric publication and FULL/EMPTY safety; and
- throughput, memory and trace/storage bounds on target hardware.

For BASE, verify that a localization mismatch is not converted into a different-
structure negative and that a false predecessor cannot manufacture real-boundary
motion history. For Accum, inspect the actual boundary witness, eligible peers,
material compatibility and owner exclusion separately. Then evaluate every
canonical segment; the selected checkpoints do not represent the full field
failure.

The existing selected checkpoint reports are final domain checks, not ad hoc
training targets. If broader private field calibration becomes necessary, first
freeze a work-PC-only episode-level development/calibration/holdout manifest and
retain a genuinely untouched private holdout. A failing shadow result returns to
V1–V3 with a named mechanism; it does not authorize a Glass/timestamp/Y branch
or unpartitioned threshold relaxation.

## Promotion gates

### O1 extraction acceptance

Requires V1 PASS, V4 exact behavior equality and bounded resources. Promotion
means only that trace-only witness extraction may remain in the candidate
runtime. `decision` stays `NOT_EVALUATED`.

### O2 shadow acceptance

Requires V2/V3 controls and holdouts PASS, V4 exact behavior equality, and a
reviewed Windows shadow report under V5. Promotion means the typed decision may
be recorded in diagnostics only.

### O3 behavior entry

Requires a separate implementation plan against the parent
[physical-interface validation](s11-physical-interface-evidence-repair-validation.md).
Only then may typed witness results feed independent support or physical
association. Owner handoff and visible-interface phase remain later distinct
gates.

### Field qualification

Requires the existing current-candidate Windows accuracy/throughput procedure
and explicit acceptance for the exact promoted runtime. Local/public PASS and
shadow discrimination never establish field qualification by themselves.

## Required evidence record

Each accepted stage must create a completed evidence document containing:

- implementation base/head and runtime/schema identities;
- changed files and owner boundaries;
- control/manifest identities and partition policy;
- focused/full test results;
- four-video equality and resource measurements;
- shadow confusion/localization/uncertainty results where applicable;
- target-Windows report identity and reviewed conclusions;
- known failures, exclusions and rollback route; and
- explicit statement of what was **not** accepted.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: current evidence supports an upstream contour/observability and physical-discrimination gap; exact private first harmful stages remain segment-specific until reviewed.
- Prior mechanisms reviewed: R22/R22-2 evidence and diagnostics, public probe, reviewed BASE/Accum checkpoints, R23 rejection, and existing parent validation.
- Prior mechanisms rejected: threshold widening, polarity/source/motion identity, unpartitioned calibration, private-coordinate tuning, missing-as-zero, stale identity/coordinate transfer, interpolation/carry and downstream repair.
- Preserved contracts: generic bounded detector, exact current-frame provenance, independent Oil/Foam, typed no-interface state, fail-closed ambiguity/unobservability, bounded resources and separate Windows field acceptance.
- Difference from prior failures: extraction, discrimination, behavior and field qualification are independent gates with explicit positive/negative/unresolved labels and leakage controls.
- Logic-map impact: NONE — this validation contract does not change the executing R22-2 control flow.
- Failure-registry impact: NONE — it adds acceptance obligations for existing named mechanisms without claiming a new cause or repair.
