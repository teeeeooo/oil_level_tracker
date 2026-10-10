# S11 Interface Observability Witness Validation

**Contract status:** proposed acceptance for the trace-only and shadow stages of
the [Interface Observability Witness Architecture](../20-architecture/s11-interface-observability-witness-architecture.md).
This contract does not accept a production classifier, temporal association,
owner handoff or direction-neutral phase behavior. The
[work plan](../00-project/work-plan.md) owns the current execution gate.

## Acceptance boundary

The first implementation exists to measure whether current images contain a
defensible target-fluid-boundary cue and to describe candidate contour
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

### Candidate identity versus partial-path review — implementation acceptance

This supplements the localization distinctions above. The v2 offline persistence
and evaluator implement this contract; it does not qualify a classifier or field
behavior. Legacy v1 inputs use explicit compatibility paths.
See the [review semantics revision](../20-architecture/s11-interface-observability-witness-architecture.md#o2-review-semantics-revision--implemented-locally).
Required controls before resuming large-scale annotation:

- an interface candidate with some reviewed off-interface sectors retains its
  identity, reports partial path agreement and cannot pass full-path localization;
- all paths qualitatively near-interface but no contour still gives no numeric
  position-error/tolerance certificate;
- scalar candidate Y, nearest-reference distance and same-number/different-X
  sectors cannot create path truth or localization matches;
- an unreviewed path portion does not inherit a reviewed neighbor or candidate's
  identity; missing native geometry is not synthesized;
- a reviewed non-interface scratch/reflection overlap retains multiple user tags
  and original notes; missing subtype does not force an uncertain identity;
- legacy interface/localization_mismatch/negative/uncertain/unreviewed judgments
  migrate explicitly with original labels and hashes, without invented per-sector
  judgments, intervals, reviewer chronology or altered packet data;
- old frozen labels/reports remain intact and readable; changed report semantics
  have a distinct version and no silent reuse of the old localization name;
- no prediction remains NOT_EVALUATED; visible empty-candidate frames, missing
  predictions, unreviewed support and localization coverage remain visible;
- stage-separated identity metrics, qualitative path counts, geometry errors and
  missing contour are verified on constructed controls. Full-path binary success
  remains unavailable without a declared coverage/tolerance policy;
- record/status/freeze and migration use the existing archive/atomic-write/revision
  guards, with source/witness checks and foreign-cwd/non-ASCII path tests.

Transferred review-002 IDs 8/9/10/12 retain the user's holistic interface labels.
Its report statements do not substitute for independently reviewed per-X contour
intervals. Coordinate arithmetic corrections must not become physical relabeling.
These reviewed cases remain regression, not classifier-fitting or untouched-holdout
proof. No field acceptance follows from passing the schema/evaluator controls.

### W1 aggregation challenger controls — not yet acceptance evidence

The [product target](../rotary_oil_level_tracker_ssot_spec.md#다층-유체의-추적-대상)
is the uppermost actual fluid boundary, not every physical liquid/liquid
interface. Target-specific evaluation additionally needs controls for two and
three actual boundaries, a reflection/structure above the target, an occluded
upper target with a visible lower interface, and FULL with no visible target.
Unknown material names must not force failure when target identity is otherwise
supported. Conversely, geometric height alone must not grant identity or replace
a missing target with a lower boundary. Foam remains independently evaluated.
These are acceptance obligations, not newly passed tests.

Preserve broad physical-interface labels and their original review basis. Before
feeding them to the current v2 identity evaluator, require explicit, versioned
target-truth attribution; notes alone do not change its positive-label counting.
A real internal boundary can be target-negative without being a reflection or
structure. Do not invent artifact tags, near/off labels or scalar truth during
that mapping. Candidate and boundary counts remain separate denominators.

The offline binding implementation is covered by
`tests/unit/test_s11_target_truth.py`: retained source/history bytes, exhaustive
role assignment, genuine internal-interface negatives, three-boundary explicit
mapping without material names, no fallback for an unavailable upper target,
wrong physical/target prediction hashes, no transferred path/scalar/entity truth,
packet/frame/Glass conflicts, incomplete/duplicate mappings, source drift,
partition leakage, snapshot projection tampering and new-output-only behavior.
The actual CLI is exercised from a foreign cwd with non-ASCII paths and relocated
packet files. These constructed controls verify binding/evaluation mechanics;
they do not prove real-image uppermost-interface discrimination. Target reports
must state both physical and target-role counts and remain NOT_EVALUATED without
predictions. Runtime and Windows field acceptance remain separate.

Use the architecture's [W1 target contract](../20-architecture/s11-interface-observability-witness-architecture.md#w1-target-and-aggregation-contract--design-boundary).
The [work-item ledger](../00-project/work-plan.md#s11-work-item-ledger) owns live
status and completion-evidence links. Existing v2 persistence tests do not
prove these new model controls pass. Keep labels fixed and specify the model's
primary identity endpoint plus protected local/scalar outcomes before comparison.

| Control | Required interpretation / protected outcome |
|---|---|
| Full reviewed interface path | Identity target positive; local truth near; scalar still unverified without its own truth |
| Partial interface, off/near/off | Preserve positive identity and two local off judgments; do not equate median failure with feature failure |
| Isolated high glare in a negative | Preserve negative identity; max score alone cannot accept it |
| Same observable vector for partial positive and glare negative | Model ambiguity remains unresolved; opposite truth labels do not supply inference-time context |
| Stationary interface / same-shape structural step | No motion requirement; no shape-only identity certificate |
| True interface crossing structure | Preserve contributing and contradictory regions; clean sibling evidence cannot erase a contradiction |
| Unavailable native path / usable center | Existing native preference and missingness remain explicit; no silent fallback |
| Clipped mask and partial scales | Report support extent/availability; conditional score gains cannot hide coverage loss |

The [D2 connectivity controls](../../tests/unit/test_s11_region_connectivity_contract.py)
use ideal nominal-region fixtures to add three representation-level obligations:
preserve different region pairs along a mixed path; do not certify enclosure
when a return is masked/cropped; and do not turn a same-observable structural
partition into physical identity. A component count can differ while existing
row/column sums and adjacency energy agree. These tests establish added geometric
information and its limits, not a model's ability to recover real targets.
The [feasibility result](../60-evidence/s11/2026-10-08-d2-region-connectivity-feasibility.md)
does not require perfect classification of every ambiguous reflection, authorize
training, or satisfy O2. A later conditional model must demonstrate useful support
outside its abstentions without leaking the synthetic labels into inference.

For any tested pooling change, compare on fixed inputs/geometry and equal support,
then report expanded support separately. Count candidates, points and scales
separately; do not pool correlated pairs into an independent success rate. Human
path labels evaluate predictions and must not select inference-time sectors.
Without independent scalar truth or a predeclared contour-to-scalar target,
scalar accuracy stays not_measured. No averaging of support points may silently
replace production candidate Y. The W3 output schema below implements these separate targets and preserves
v1 compatibility; the W1 controls themselves add no prediction enum.

For the selected [fixed-center target](../20-architecture/s11-interface-observability-witness-architecture.md#fixed-center-height-target--selected-for-the-offline-challenger),
verify fixed source/ROI conversion, deterministic native-column rounding,
independent Oil/Foam missingness, current selected-boundary provenance and reuse
of the existing px/mm conversion. A static inclined boundary must not change
height solely because visible side coverage changes; loss at the fixed column
must not relocate the measurement or carry a prior Y. Mask/crop censorship and
multiple physical alternatives must remain explicit. Recognition may use the
whole available image and temporal context.

The [176-raster readout](../50-diagnostics/s11/2026-10-09-fixed-center-readout.md)
checks coordinate extraction against direct pixel-neighbor enumeration and
retains every support crossing. Its five constructed controls cover this narrow
geometry prerequisite only. No physical selector runs: null role outputs are
NOT_EVALUATED, not successful abstentions or measured target coverage. Existing
qualitative replies remain qualitative; defining a target does not manufacture
scalar truth. Physical-role efficacy and integration still require their own
fixed controls before any runtime scalar change.

W1 completion requires reproducible partial-positive and glare counter-controls,
a stated aggregation/identity rationale, and explicit handling of indistinguishable
inputs. The target distinctions alone do not satisfy model or calibrated O2
acceptance. [Local W1 evidence](../60-evidence/s11/s11-o2-w1-target-aggregation-controls.md)
maps the controls to `tests/unit/test_s11_target_aggregation_contract.py` and
records the source boundary. Those tests reproduce limitations of the existing
ranker and exercise scripted evaluator outcomes; they are not a passing identity
challenger. The identical-observable counterexample has opposite constructed
truth labels and requires unresolved inference, not relabeling or a tie-breaking
candidate index. A scripted unresolved output must preserve the visible-frame
denominator and report zero support recall, rather than treating abstention as
successful observation. No new Windows annotation is required until a specific
missing distinction is named.

The [identity context source audit](../60-evidence/s11/s11-o2-identity-context-source-audit.md)
adds actual-raster sampling controls: a remote intensity return outside all candidate
bands must leave that local witness unchanged, whereas a return within measured
support must be observed. Cover both polarities. Neither result supplies physical
truth or justifies automatic band expansion; test any proposed contextual cue
against a stationary same-shape structure and partial real interface separately.

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

The offline foundation uses `s11-o2-review-packet-v1`, `s11-o2-labels-v2`,
`s11-o2-frozen-labels-v2`, `s11-o2-shadow-report-v2` and
`s11-o2-shadow-predictions-v1`. Label/frozen v1 reads remain supported; migration
is explicit and old report files are preserved. The
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

## W3 separated target and audit controls

The [W3 contract](../20-architecture/s11-interface-observability-witness-architecture.md#w3-separated-shadow-targets)
is exercised by `tests/unit/test_s11_shadow_targets.py` through the existing
scorer/evaluator and real CLI paths. Required controls:

- v1 report compatibility and original fixed-score inputs/scores/evaluation
  equality; exploratory opt-in must not weaken calibrated or recording-group gates;
- exact candidate/witness/geometry matching, no duplicate local points or implicit
  native/center substitution, original scalar Y and explicit operating-point ID;
- identity-positive/off-path coexistence, missing versus explicit abstention,
  unverified predictions on unknown truth, empty visible frames and zero useful
  coverage for all-abstain outputs;
- no scalar accuracy/verified observation claim without independent truth, even
  when scripted predictions declare USABLE;
- human uncertain identity/local truth crossed with supported/rejected, abstained,
  unobservable, not-evaluated and missing model outcomes: no verified success from
  unknown truth, no disappearance from inventory or full coverage denominators;
- rationale-only text changes never reclassify structured truth; changed label
  content needs matching prediction provenance. A constructed alternate uncertain
  or unreviewed identity may remove rank pairs while scores remain identical;
  that is changed truth support, not classifier improvement. Original evaluation
  remains reproducible and no private labels are altered by these controls;
- context missing/null/zero and availability distinctions, including meaningful
  glare/exclusion fractions on unavailable optical bands;
- exact indexed bundle/packet/recorded sequence joins; rejection of wrong or
  ambiguous member identity; unknown earlier losses remain unknown;
- outside-repository cwd and Korean/spaced paths, no-overwrite outputs, immutable
  inputs and COMPLETE receipts only after successful verification.

These are contract and integration tests with scripted predictions, not classifier
acceptance. The Windows existing-data audit must reproduce the original reference,
preserve all input hashes and return recorded-context/funnel availability. An
UNAVAILABLE funnel is a reported evidence gap, not permission to infer a rejection
cause. Select W4 only after naming the distinguishing observable and counter-control;
scalar calibration and O2 acceptance remain separate. Production code is unchanged,
so this offline extension does not require another detector replay or field run.

### Recorded structure-context controls

`tests/unit/test_s11_structure_context.py` must cover the optional bundle-only
projection through the real CLI as well as constructed counter-controls:

- require target-audit + original bundle; retain unchanged v1 inputs, scores and
  evaluation and use a distinct audit artifact/receipt schema;
- original indices despite score-sorted raw rows; reject duplicate/missing/raw
  identity mismatches and wrong/duplicate recipe Glass IDs;
- preserve features versus penalties, container missing/null, numeric zero versus
  null/missing; reject booleans, strings and nonfinite numeric values;
- raw template missing/null/empty/nonempty inventory and duplicate template IDs;
  never turn empty registration or match magnitude into physical identity;
- actual indexed bundle/packet/recipe join, non-repository cwd, Unicode/spaced
  output path, preserved inputs, matching output hashes, no overwrite and no
  COMPLETE after input mutation.

Windows must report all existing reviews with pinned revisions 3/14/4, original
reference equality and all 12 input hashes preserved. It must not infer a new
identity, score, gate or abstention rule from this audit. If recorded fields or
registrations are absent, report the gap; do not fill them by rerunning detection
or registering templates. Reading a historical recipe cannot establish when or
independently of which evaluations its templates were annotated. BASE idx0/idx20
uncertainty remains qualified; no labels/denominators change.

## W4 paired-scale controls

The [local comparator](../20-architecture/s11-interface-observability-witness-architecture.md#w4-paired-scale-comparator-boundary)
must show both a synthetic repaired reversal and the inverse new regression;
claiming that pairing always improves order is prohibited. Controls also cover
one/two-scale equality, ties/zero, null support, disjoint widths, width permutations,
wrong basis/X and duplicate-width rejection, antisymmetry, metadata blindness,
and a three-point cycle demonstrating that no total ordering is justified.

Existing task inventories retain interface/off separately from non-interface/off,
and native paths separately from centers. Unknown paths remain in denominators.
The reference CLI must preserve original inputs/scores/evaluation, verify receipt
hashes, reject drift/overwrites/mode conflicts and work outside repo cwd with
Korean/spaced paths. Production decisions and numeric localization remain absent.

Windows must report primary `native_path/interface_location_same_x` and separate
`native_path/identity_negative_control_same_x` on identical joint support for both
reducers. Legacy-to-joint support changes are reported separately, including lost
pairs and shared-scale count histograms. No primary net improvement or any native
negative-control regression rejects replacement on the supplied controls. No task
pooling, no success from zero pairs, no holdout or field claim follows from these
correlated regression comparisons. W1 identity/scalar controls and O2 calibration
requirements remain unsatisfied by a favorable local-position result.

## Ordered spatial-context prototype controls

The [measurement contract](../20-architecture/s11-interface-observability-witness-architecture.md#w4-ordered-spatial-context--measurement-prototype)
is exercised by `tests/unit/test_s11_spatial_context_probe.py`. Its primary endpoint
is information retention at fixed raster/geometry/masks, not classifier accuracy:

- Constructed step/remote-return pairs at two return extents and both polarities
  have identical complete original O1 candidate witnesses and fixed scores, while
  the full-height observation distinguishes the remote rows.
- Hidden returns under mask or glare remain indistinguishable; unavailable rows
  stay null with exact support counts, never become zero/continuous evidence.
- Identical physical aliases, stationary steps, and Oil-with-return appearances
  remain NOT_EVALUATED. No truth labels are inputs to the probe.
- Equal global histograms with different vertical row order remain distinguishable;
  horizontal permutations with equal strip means remain a documented collision.
- Exact nonzero crop origin and candidate/basis/source geometry survive; shared
  intervals reuse one profile without treating candidate aliases as independent.
- Observed black pixels differ from missing rows; one-pixel support stays visible
  as such; empty inventory creates no candidate or successful prediction.
- Reject duplicate/invalid geometry, boolean indices/origins, nonintegral X,
  wrong shape/type and resource-bound violations. Input arrays/points stay intact.

Candidate-relative feasibility additionally requires checking the whole O1
inventory, not only one candidate. The spatial control suite now includes both
an identical complete two-candidate witness with a distinguishable remote return,
and a return already detected by another candidate. A central band-gap spike
also demonstrates that O1 peak fields can contain information missing from band
means. Both polarities are exercised. These are information-boundary controls,
not synthetic physical identity labels; [feasibility evidence](../60-evidence/s11/s11-o2-spatial-context-feasibility-local.md)
records the no-promotion decision and the next proposed representation boundary.

Real-data acceptance requires a separately verified source-frame adapter and
image/profile correspondence on the existing two frames. The synthetic passing
endpoint is insufficient to infer private stripe shape, classifier separation,
scalar truth or Windows qualification. Fail the identity hypothesis if opposing
classes remain observationally identical; report mask/crop censoring. Any classifier
proposal needs separate positive/negative/unresolved controls and an operating
point before O2 acceptance. The source adapter and Windows procedure now implement
this entry; the transferred spatial run and bounded inspection are recorded in
[Windows evidence](../60-evidence/s11/s11-o2-spatial-context-windows-run-001.md).
Physical efficacy and independent local raw-crop verification remain unestablished.

Source-adapter controls use a real synthetic indexed bundle, generated video and
existing bundle-link owner. A real CLI subprocess must run from a non-repository
Unicode directory with explicit UTF-8 and closed stdin. Verify exact point inventory,
original witness preservation, decoded frame/crop/mask identities, every output
hash and every input hash; exercise two different frames in one original bundle.
Wrong video/bundle/packet/link/scene/revision, writer locks, decoder overshoot,
wrong dimensions/crop and input mutations during measurement/publication must
leave no COMPLETE receipt. Existing output cannot be overwritten. Baseline-band
controls must show both identical gray/support and explicit reconstruction drift.
No detector efficacy assertion follows from these constructed entry controls.

The Windows run uses only review-002 rev14 and review-003 rev4. Report baseline
`MATCH`/`DIFFERENT` and mismatched-band counts independently of execution COMPLETE.
A mismatch requires inspecting reconstruction before comparing representations;
do not fit a tolerance to make private data pass. Identity remains NOT_EVALUATED.

## Ordered column-side context controls

`tests/unit/test_s11_lateral_context_probe.py` validates the local array function
in the [column-side contract](../20-architecture/s11-interface-observability-witness-architecture.md#w4-ordered-column-side-context--local-prototype).
Require equal complete O1 witnesses and full-height row context but distinct
ordered column sides on the sector-mirrored fixture, under both polarities.
Keep masks, source geometry and auxiliary channels fixed; do not infer physical
labels from synthetic shapes. Hidden differences must remain indistinguishable.

Verify half-up centers, nonzero source origins, separate geometry bases, exact
half-open ranges, clipping, sparse/zero/null states, no wraparound, inventory/width
bounds, empty inputs, serialization and input preservation. Explicitly retain
both within-band vertical-order loss and a joint row/column marginal collision.
Neither this function nor a passing distinction test asserts connected regions,
Oil identity, sufficient classifier support or numeric localization.

[Local evidence](../60-evidence/s11/s11-o2-lateral-context-prototype-local.md)
includes the existing source-runner entry/receipt regressions because the shared
module changed. No Windows lateral CLI, physical efficacy or O2 acceptance is
claimed by these local controls.

## Unpooled O1 spatial-context controls

The [joint-context contract](../20-architecture/s11-interface-observability-witness-architecture.md#w4-unpooled-o1-spatial-context--stored-output-adapter)
is diagnostic only. Require the known joint row/column collision to differ in
unpooled gradients under both polarities, while mask/glare-hidden changes remain
indistinguishable. Verify stencil neighbours, crop borders, observed zeros,
orientation, nonzero origins, unchanged inputs, and retained identical-pixel and
central-difference checkerboard aliases. No synthetic shape is physical truth.

Exercise the saved-output CLI from a non-repository Unicode directory with UTF-8
and closed stdin. Use actual O1 extraction, PNG bytes/raw raster identities, source
artifact and COMPLETE receipt format. Verify every new output hash, exact bands,
NPZ array hashes and old-file preservation, including two frame/Glass cases.
Native and candidate-center roles stay distinct; exactly coincident deduplicated
centers have an explicit alias, and absent noncoincident centers must fail.
Reject mismatched byte/raster/artifact/schema/point/frame/baseline information,
path traversal, oversized PNG dimensions, existing/nested output, and changes
during measurement or publication without a COMPLETE receipt. Check viewer
initial rendering and point/scale/overlay switching on synthetic output.

Windows execution remains required on the private saved outputs. Return the
machine summary plus the bounded appearance inspection; flag unreadable images
rather than inventing interpretation. Stop on provenance/baseline failures. A
successful local adapter or Windows receipt does not resolve Oil identity, the
human ambiguity control, numeric localization or O2 acceptance.

## Recorded-band color-side controls

The [fixed color-side contract](../20-architecture/s11-interface-observability-witness-architecture.md#w4-recorded-band-color-sides--saved-output-measurement)
requires an equal-gray, different-BGR step to retain signed channel differences;
achromatic steps must have zero opponent change, including observed zero.
Assert BGR order, polarity, float subtraction without uint8 wraparound, ordered
columns and equal-column weighting under unequal pixel counts. Identical pixels
remain unclassified regardless of their possible physical cause. Synthetic color
separation is information retention, not private identity discrimination.

Masks/glare must prevent hidden colors from changing output. Empty bands and
nonoverlapping column support cannot manufacture deltas. Unavailable/clipped O1
bands may report partial observed means, but must not become eligible pairs.
Validate clipping, count agreement, raster/gray/channel equality, duplicate
points and resource bounds. Every input stays unchanged.

Reuse the actual O1 producer fixture and saved-output receipt for the color CLI,
including non-repository Unicode paths, UTF-8, closed stdin, two frame/Glass cases,
all roles and coincident-center aliases. A non-gray BGR fixture must produce the
expected vectors without calling the joint-map builder. Verify CSV numbers,
three hashed outputs plus receipt, unchanged source files and all no-decision
flags. Run shared input-failure guards in both modes; color/gray mismatch and
input mutation during measurement/publication must leave no COMPLETE receipt.
Retain existing spatial-source and default joint regressions.

The color-side Windows run and saved-value corrections were received as attributed
evidence; see the [completed assessment](../60-evidence/s11/s11-o2-color-side-local.md#added-information-assessment-and-measurement-disposition--2026-10-06).
This measurement is CLOSED WITHOUT PROMOTION, not a pending repeat run.
Report all predeclared primary sectors/widths/near-far pairs and unavailable
states, without choosing a favorable channel or aggregating labels into a score.
Review-003 idx10/15 is the main descriptive contrast; BASE idx11 is censored
supporting evidence and idx0/20 remains a human-unresolved control. No measured
separation alone grants physical identity, W4-R2, O2 acceptance or field PASS.

## Candidate-conditioned region competition controls

The [frozen prototype](../20-architecture/s11-interface-observability-witness-architecture.md#w4-candidate-conditioned-region-competition--prototype-contract)
implements fixed raw-pixel appearance models. Synthetic appearance controls and
future physical-identity controls must be reported separately.

| Control | Required result / falsification |
|---|---|
| Equal-gray chromatic arrangement with identical full color-side output | Demonstrate the band/column reduction collision; a future raw 2-D model must expose the changed arrangement rather than reread identical summaries |
| Achromatic two-sided boundary, both polarities | Color must not become a mandatory interface cue; adding channels must not rescale the gray decision by channel count |
| Smooth illumination ramp vs two-sided region vs returning ribbon | Same support and declared model capacity; report appearance explanations, not synthetic appearance names as physical truth |
| Coherent reflected/structural step vs Oil with identical supplied pixels/context | Unresolved physical identity; no geometry/brightness/color certificate |
| Partial true path and isolated artifact with equally strong local evidence | Preserve support and opposition geometry; no max, majority or center-line identity shortcut |
| Glare/mask gap through an apparent boundary; return beyond crop | No region bridge or inferred termination; censored evidence stays censored |
| Artifact template crossing a real boundary; stationary interface | Neither static overlap nor template match becomes a blanket negative label |
| Original bands vs enlarged envelope; gray vs BGR | Attribute any benefit to the correct support/model/color change, using the full factorial comparison |
| Unequal edge support, alias centers and overlapping widths | Same valid pixels per ablation; no sample multiplication or independent-vote claim |

Executable controls now reside in `tests/unit/test_s11_region_competition.py`:

- Held-out residual distinguishes affine ramp, signed partition and both fixed
  ribbon widths on noiseless synthetic fixtures in both intensity polarities.
- Achromatic BGR and gray have equivalent losses within floating-point tolerance;
  equal-gray chromatic steps are representable only by the BGR comparator.
- The full-color-side-output collision has different raw within-side horizontal
  adjacency. This is a representation/appearance distinction, not Oil accuracy.
- Hidden pixels cannot affect errors or adjacency; band gaps are not bridged;
  changing only center-gap pixels changes envelope views but not band-only views.
- Held-out pixels do not fit coefficients. Low split support, deficient rank,
  O1 unavailable and crop clipping remain explicit with null model fits.
- Opposite physical interpretations, static/template metadata and selected/
  rejected hints cannot alter fits. Actual optical opposition is not measured;
  this control preserves uncertainty, not detection of real structures.
- Exact roles, separate points, aliases, all widths and factorial views survive
  the real CLI. Receipt validation, source mutation failure, resources and
  Unicode/non-repository cwd/closed stdin are exercised. No candidate pooling.

The full physical matrix is **not** certified by these tests: real partial paths,
weak/overlapped true boundaries, structure attribution and independent physical
identity discrimination remain unvalidated. The synthetic model capacity is a
shared affine plane plus a fixed offset, not a general segmentation algorithm.
A ribbon outside the two frozen widths, curved illumination or crossing texture
can fit poorly under every model. Do not tune widths or choose new thresholds
from the first private report.

Windows entry is only the [frozen saved-output evaluation](../40-operations/s11-o2-local-shadow-evaluation.md#region-competition--existing-saved-outputs).
Return all model errors with support/censoring and all four ablations. If only
gray changes explain the difference, credit spatial/support information, not
color. If competing appearances remain shared or censored, report that result
and close the bounded run. No smallest-error-to-identity rule follows.
Actual identity evaluation must use W3 truth/abstention/coverage semantics and
independent partitions required by O2 acceptance. The existing two frames supply
no new holdout evidence; W4-R2 entry remains unmet.

## A2 preparation: uncertain physical identity, definite wrong target

Exercise `bind-target` through the actual CLI with an explicitly indexed
`other_non_target` judgment whose original physical identity is `uncertain`.
The saved source labels/history must remain byte-identical; the frozen snapshot
must retain physical uncertainty, while W3 counts support as a wrong target.
Tentative artifact notes must not become physical artifact tags or local/scalar
truth. Loading/re-evaluating the snapshot must preserve these distinctions.

Reject uncertain-to-target-positive, unreviewed-to-negative and implicit bulk
inheritance of uncertain identities. Keep all existing immutable snapshot, exact
packet/witness binding, wrong-label prediction, relocation, drift and recording
partition protections. This additive accepted mapping leaves old valid snapshots
unchanged. No calibrated classifier or operating-point claim follows from binding.

## A1 lossless lineage acceptance

For `oil-measurement-lineage-v1`, remove **only** its sibling namespace when
comparing existing diagnostic state. Keep all old golden fingerprints. Test
independent-X false pooled contrast, complete common-X controls, empty/clipped
rasters, nonfinite/censored support, bool/nonintegral indices, duplicate identity,
source/Y mismatch, same/opposite/zero/unknown signed pairs, and unchanged legacy
pair values. Preserve raw profile dtypes in real fixtures; float32 conversion is
not lossless for a float64 energy profile.

A retained human-ROI sample4/f420 fixture binds the known Y854 hypothesis to
center Y853 and partner Y851 with same-sign gradients. It is regression data,
not an adopted input recipe or calibrated scalar truth. Also verify exact
current/completed/old-debug equality at the seven reviewed interval observations,
including the three newly confirmed Oil alternatives.

Exercise the real debug NONE/Basic/Full entry and existing writer/output safety,
foreign-CWD/Unicode and bundle lifecycle controls. The new namespace must remain
absent from detection metrics, candidate features and resolver-facing evidence.
Run all four official windows serially in fresh baseline/candidate processes,
with identical runtime, inputs and copy mode. Compare raw/completed detections,
all old state, CSV/events and report presentation; record time, RSS, trace bytes,
per-frame candidate/sector/scale bounds and exact reproduction failures. Resource
cost remains explicit; passing extraction never establishes physical efficacy.
Canonical non-Qt and externally bounded Qt runs, governance and whitespace/link
checks remain required. A0Q is not repaired by a passing Qt run.

## Registered support input controls

The optional registered-support input must preserve exact original pixels,
candidate input indices, actual playback identity distinct from detector-internal
zero, independently hashed raw/processed/visibility images and bounded crops
without rescaling. Missing native geometry stays missing. Mixed connected and
disconnected edges, masking/glare and empty scopes must not become whole-area
or whole-component labels. Changing scope requires renewed confirmation.

Verify nested cancel, outer cancel/apply, real MainWindow entry, relocated recipe
save/load from a non-repository cwd, reopening without video, and view resizing.
Legacy/missing/corrupt/oversized evidence cannot become usable references;
changed ROI/dimensions/Glass/settings/template geometry cannot transfer old
attribution. Verify resource limits and unchanged matcher/frame detections and
preflight identity with/without metadata. Genuine interfaces away from, crossing
or stationary at structures, obscuration and physical mixing still need opposing
and unresolved controls before any future reference consumer. Local UI checks
do not imply Windows display/packaging or O2 field acceptance.

## Registered support comparison gates

The [comparison contract](../20-architecture/s11-interface-observability-witness-architecture.md#registered-support-diagnostic-comparison--planned-contract)
has three distinct acceptance levels. These do not replace V2–V5 or O2/O3:

1. **D2-A diagnostic contracts.** First freeze a bounded reference-readiness and
   candidate-family/basis matrix, common reviewed domain, availability/count
   denominators, lineage identities and incremental latency/RSS/trace caps.
   Synthetic/legacy/context controls may proceed without a real reviewed
   reference, but that absence must block real efficacy claims. Test explicit
   review-state/rectangle changes with the same snapshot hash, preprocessing
   mismatch, crop/mask censoring, empty support/zero denominators, missing native
   geometry, disconnected/mixed support, permutation and duplicate candidates.
   A shared band, centered envelope or sparse native samples cannot become
   candidate-owned raw edges. Outside-scope pixels remain unreviewed; mask
   eligibility is not optical visibility. Require reproducible diagnostics,
   bounded resources and complete debug ON/OFF detector equality through the
   actual entry path. Completion does not require physical decisions.
2. **D2-B information feasibility.** With input-bound real controls and frozen
   exposure/partition roles, compare isolated reviewed structure, target away
   from structure, moving crossing, stationary coincidence, optical obscuration,
   different contours in one envelope and identical pixels with different
   physical causes. Preserve basis-specific unavailable denominators and all
   unresolved results. Execute one fixed comparison; noise-dominated exact-pixel
   results may close without promotion. Do not adjust tolerance/dilation afterward.
   Raw information gains alone do not satisfy O2.
3. **D3 physical efficacy / O2.** A physical decision extension first requires
   a named additional observable, reproducible decision/abstention rule and V3
   operating-point/partition discipline. Apply the all-unresolved/no-useful-
   support no-go here, not to a trace-only comparator intentionally emitting
   `NOT_EVALUATED`. Separate wrong-target suppression, true-target retention and
   recovery, unavailable/unresolved and unreviewed outputs; scalar accuracy is
   independent. Newly admitted but unreviewed outputs are not successful targets.

Physical controls may be reviewed at the boundary/region and short-sequence
level appropriate to the claim; they do not require classifying every small
contour in every frame. Preserve approximate annotations as qualitative evidence
without deriving masks, exact scalar tolerances or per-pixel labels. Distinguish
these from exact machine input binding. A known safe short temporal witness does
not certify its initialization, other sectors/directions or stationary/crossing
controls. The [reference + temporal-context result](../60-evidence/s11/2026-10-09-d2-sequence-context-feasibility.md)
does not test pixel withdrawal. A next challenger must identify a distinct
measurement/evidence operation with controls, rather than reuse overlap or
persistence as identity. The local XY proposal below supplies that bounded
design entry, not efficacy proof. No further micro-labeling or relaxed
acceptance follows. Episode outcomes remain relevant alongside these gates.

The October 9 diagnostic implementation covers available contrast footprints,
not candidate-owned edge intersections. Its [evidence and receipt](../60-evidence/s11/2026-10-09-d2-reference-measurement-comparison.md)
retain hand-calculated mask/count controls, explicit nulls, legacy/context
failure controls, duplicate/index binding, real detector entry and BASIC/FULL
serialization. NONE must bypass comparison. Tests must keep decision/physical/
target/path/scalar fields `NOT_EVALUATED` and visibility `NOT_ESTABLISHED` even
for disjoint, identical or stationary synthetic inputs.

Frozen implementation budgets are 16 templates, 128 Oil candidates, 512 pairs,
8,388,608 compared crop pixels and 1 MiB record size, with all-or-none exhaustion.
The initial resource preflight separately limits one-reference paired median
increment to 10 ms and incremental Python allocation to 32 MiB; the latter is
**not RSS**. Record process RSS separately and do not infer worst-case/Windows
performance from a small one-reference local fixture. Completion of this
measurement slice cannot close missing raw-edge or real opposing controls.

Reuse the full sample4 0–56 s paired sequence and its fixed seven target/three
negative bindings, including 40/42/44 s upstream losses and 49.5/52 s regression.
Cover the other three samples' overlay, reflection and long-gap risks. These are
exposed regression controls, not a new 100% final-recall product requirement or
held-out proof. Later behavior must preserve major movement/episode outcomes;
a better single frame cannot hide downstream harm. Engineering defects can be
fixed and rerun; a failed mechanism does not authorize outcome-driven tuning.
O2 Windows shadow/holdout acceptance, O3 authority/association entry, later phase
controls and nine-segment integrated field qualification remain separate gates.

## Local XY measurement exclusion controls

The [implemented fixed comparison](../60-evidence/s11/2026-10-09-local-xy-implementation.md)
now satisfies the technical OFF/debug/sampling/report checks below and rejects
this configuration for efficacy. The 54–56 s regional Foam–Oil clarification is
closed; both output series remain required. These controls govern a future
substantively new hypothesis, not an instruction to repeat the closed run.

Apply these to the [proposed Oil measurement scope](../20-architecture/s11-interface-observability-witness-architecture.md#local-xy-oil-measurement-exclusion--proposed-contract).
The [intake evidence](../60-evidence/s11/2026-10-09-local-xy-spec-intake.md)
records A–D as completed, unpromoted prototypes. Do not rerun those variants or
the 72 historical tests just to restate their results. The next implementation
needs focused evidence for its changed contract and real entry path.

1. **Scope and identity:** OFF, empty union and no eligible intersection preserve
   complete legacy output. Check source/crop clipping, half-open bounds, other
   Glass isolation, overlapping rectangles, malformed/mismatched bindings,
   same-X/other-Y eligibility, input immutability and explicit bounded exhaustion.
   Scope policy/version participates in run identity. An explicit sampling
   policy is not a new physical label.
2. **Measurements:** freeze original support denominators and the full dependency
   policy, including material-profile normalization, before running. Check a
   horizontal ramp, real vertical step, asymmetric removal, no common columns,
   complete/partial sector loss and unchanged primitive measurements. Apply a
   numerical guard only to affected eligible samples, with unchanged floors.
   Do not assume that primitive locality implies unchanged ranked candidates
   elsewhere in an actively changed frame. No zero fill or global paired-mean
   replacement; upstream influence remains a named limitation.
3. **Executing lineage:** verify scoped measurements through the real assembler
   and detector, with actual denominators/unavailable reasons and matching
   A1/native geometry. NONE/BASIC/FULL yield the same physical result; sidecars
   cannot create authority. Verify selected-candidate/completed/CSV provenance
   and distinguish created/removed/changed proposals without transferring labels.
4. **Frozen comparison:** baseline versus one scoped candidate across sample4
   0–56 s and the other three existing windows; freeze any one necessary ablation
   before results. Preserve seven target/three wrong-target bindings and inspect
   the whole interval, especially 40/42/44/49.5/52 s and its end. OFF on other
   samples is compatibility evidence, not cross-Glass physical efficacy.
   Generic multi-Glass/coordinate controls test the input contract separately.
   Use actual baseline/challenger HTML/CSV/report outputs, not raw-coordinate
   charts alone, and evaluate both final series validity and Foam episodes.
5. **Outcome and stop:** missing observations, false owners, major movement and
   extrema must be reported separately from numeric count. Preserve B's 40 s
   inverted-topology counter-control. A new nearby Y has no inherited truth.
   Freeze resource limits, run timing comparisons serially, and do not treat
   the concurrent prototype timings as acceptance. If protected movement is
   lost or no useful physical improvement is established, close that fixed
   mechanism; fix a demonstrated implementation defect separately, without
   threshold/rectangle sweeps or gate bypasses. Ask for new human judgment only
   where a concrete changed physical correspondence affects the conclusion.

These local checks do not satisfy O2 opposing/holdout/Windows controls, authorize
an authority/phase rewrite, or change FIELD FAIL. They also do not add a 100%
per-frame recall or per-pixel semantic-labeling requirement to the product.

## Local source and truth qualification

The [2026-10-10 source/annotation audit](../60-evidence/s11/2026-10-10-local-truth-and-evaluation-audit.md)
qualifies future local physical comparisons. A historical user-approved scalar
is not automatically pixel-exact, candidate-identity truth or a contour at the
new fixed-center X. Original truth files, test fixtures and past experiment
outcomes stay identified; a correction is an explicit reference revision, not
a detector improvement.

Before selecting a new mechanism or inspecting its scores, freeze the source
frames/intervals and each claim's role, authority, visibility, geometry and
measurement semantics. Use the complete seven-recording audit inventory as
the routing basis, not an all-or-nothing four-video accuracy gate:

| Evidence stratum | Required interpretation |
|---|---|
| Engineering compatibility | Keep decode/input identity, independent series, same-frame provenance, output integrity and appropriate runtime checks, even on physically ambiguous images. Historical replay windows are input scope, not continuous physical truth. |
| Qualified physical positives/opposition | Use clearly visible source-bound claims. Water settling/empty-pattern context is the first development entry; retain inclined-water, beer, milk and existing target-domain controls at their actual annotation scope. Agent interpretation stays distinct from human truth. |
| Unobservable, disputed or geometry-incompatible claims | Report explicitly as unresolved/unassessable for that physical metric. Do not force an exact Y, infer absence from invisibility, or credit an abstention as correct identity. Inspect unsupported numerics as robustness failures only where source evidence supports that judgment. |
| Legacy scalar agreement | Report the original complete 13-case comparison under its original values and semantics. Preserve its PASS/FAIL; it is not by itself decisive physical acceptance/rejection for a different measurement target or an unresolved reference. |

The current legacy comparator and tests are not weakened by this contract.
Any future conflict between an old assertion and a newly qualified physical
target must be reconciled explicitly before runtime adoption; do not hide a
failing check or preserve a demonstrated wrong behavior solely to satisfy an
incompatible oracle. A genuine loss on a compatible, supported positive remains
a regression. All-abstain is not successful development.

Numeric fixed-center error requires compatible source/time/pixel binding,
target role, declared X, visible intersection and reviewed point/interval
semantics. The audited 13 historical points have no such transfer certified.
Original agent proposal ranges are not automatically approved error tolerances;
do not derive tolerances from candidate residuals. A label revision retains its
reason/history and reruns baseline and candidate against the same frozen version.
Unchanged predictions plus fewer decisive labels are not an accuracy gain.

A reviewed one-surface/front-back relation is an identity relation, not two
independent physical positives or a filled Y tolerance interval. Preserve both
projected branches and the reply's exact scope; the approximate marker points
are not contour truth. Before a decisive scalar comparison, declare which
projection is the measurement target and review its actual coordinate/support.
The [pending convention proposal](../20-architecture/s11-interface-observability-witness-architecture.md#same-surface-projected-branches--scalar-convention-pending)
does not modify current labels or scoring. A future implementation must retain
physical-target ambiguity, distinguish branch occlusion from interface absence,
avoid fallback to another projection when its chosen one is unavailable, and
reject an unrelated higher edge. Correct physical identity with an unqualified
scalar remains two separate outcomes; it is not a successful numeric observation.

Keep every qualified/unqualified case, denominator, missing output and reason
visible. Do not select only easy frames after results or turn crop-center geometry
into calibrated Glass geometry. Scope difficult cases by observation/role,
not by discarding a whole recording. Existing human-confirmed positives,
wrong-target controls and major-event judgments remain at their original scope;
CBR-1's wrong-rim closure is not reopened by this audit.

All seven recordings remain exposed development/regression evidence. Clearer
public drinking-glass images do not replace target-domain, independent-holdout,
O2 or Windows obligations. Qualitative mechanism development can proceed while
a disputed legacy claim remains quarantined; formal relabeling or a decisive
numeric accuracy claim needs its specific missing review, not repeated review
of all prior questions.

## CBR-1 offline comparison entry

This is the validation boundary for the
[proposed current-boundary comparison](../20-architecture/s11-interface-observability-witness-architecture.md#cbr-1-current-boundary-reference-comparison--proposed-offline-contract),
qualified by the [cc17924 intake](../60-evidence/s11/2026-10-10-cc17924-handoff-intake.md).
It supplies no passing model or replacement O2 gate.

Before coding the measurement, freeze source/input/reference identities,
geometry basis, current-to-reference correspondence, side stencil, common support,
tie semantics and combined resource limits. Select one operation; at most one
structurally distinct ablation may be declared before observing results.
Control fixtures must cover masked/absent/mixed references, stationary inclined
fronts, center-only loss, side-only visibility, multiple intersections,
junctions/duplicate faces, same-shape structure, copied texture, optical warp,
true-boundary/structure crossing, independent Oil/Foam availability, coordinate
conversion and budget exhaustion. Exact synthetic labels never enter inference.

The first real-data scope is the complete exposed 167-raster/198-query plan
(195 continuation queries after the three initial queries), with every candidate
and every missingness reason retained. Initial reference frames are initialization,
not continuation success. Keep native-rate results and the actual configured
analysis cadence separate; no hidden LK/native-rate acquisition prerequisite is
permitted. Report geometry availability → side comparability → provisional role
comparison → fixed-center availability, separately from physical target quality.
Oil f1348 remains an agent-observed suspect wrong region, not new user point truth.

Before that comparison, bind the existing positive/opposing/unresolved controls
and named event intervals to a written progression rule: useful non-initial target
support in the intended role, no new P0 event reversal/loss or false major episode,
and no increase in P1 wrong-owner runs traded for coverage. Enumerate missing and
wrong-owner runs, visibility denominators, onset/offset/direction/reappearance,
improved/worsened/unassessable intervals, and actual sampled times. Exact errors
and run classifications require compatible truth; otherwise report NOT_MEASURED
and attributed qualitative evidence. P2 residuals may be listed without claiming
field acceptance. Raw counts, a favorable screenshot or all-UNKNOWN cannot pass.
Define the applicable intervals and qualitative adjudication before results;
do not invent tolerances afterward. If available evidence cannot judge the rule,
retain NOT_ASSESSABLE and name the missing distinction.

Only a useful bounded result proceeds to the existing four Mac regression
windows (including full sample4) and public water/beer/milk opposition controls.
For a future successor, those sources are interpreted under
[local source and truth qualification](#local-source-and-truth-qualification),
not as seven uniformly reliable numeric oracles. CBR-1's frozen result is retained.
These already exposed recordings are not fresh holdouts; public crop centers
are not calibrated Glass centers. Compare fixed-center scalar error only where
truth declares compatible measurement semantics. Existing candidate-Y truth and
W3 records remain intact. D5 Foam uses its own controls and single-change
comparison; Oil results cannot satisfy Foam acceptance.

Measurement feasibility keeps physical decisions NOT_EVALUATED. A later frozen
physical rule still requires V2/V3 controls, partition/holdout evidence, a reviewed
operating point, V4 behavior equality and V5 Windows shadow review for O2. Existing
holdout limitations stay open; this plan neither manufactures an untouched split
nor repeats the closed recording-availability question. O3/O4 and the exact-runtime
nine-segment field procedure remain later gates. No new Windows request is part
of this intake. Stop the fixed variant if useful role support is absent or it
needs manual seed rescue, retuning, filled gaps or downstream gate relaxation.

The [2026-10-10 complete comparison](../50-diagnostics/s11/2026-10-10-current-boundary-reference.md)
applies this stop condition: 88 focused measurement tests and all 198 independently
checked query outcomes pass computational checks, while the physical progression
condition fails. Lower-rim Foam appearances and ambiguous Oil analysis-grid
outputs do not justify broader regression or Windows qualification. The Structure
plan's zero center outputs are unavailable comparisons, not successful negatives.
Exact real optical-discrimination/center-error efficacy remains unqualified;
no existing O2 requirement is satisfied merely by those computational checks.

## Detector Governance

The 2026-10-10 CBR-1 intake adds offline entry and progression conditions; its
complete frozen comparison then triggers the stop rule without promotion.
The subsequent local-truth audit qualifies source/annotation uses before a
successor's physical comparison; it preserves original labels, test outputs
and the failed experiment's disposition.
The later same-surface reply also separates projected-branch semantics from
physical identity and reviewed coordinate precision; its proposed scalar
convention remains unadopted while the user choice is pending.
H0's support-face intersection loses available partition geometry, while CBR-1
admits wrong-region appearance despite current geometry. Private first physical
causes and field effectiveness remain unqualified. F07's Foam front/texture
distinction is preserved alongside the guards below.

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`, `FOAM-CANDIDATE`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: current evidence supports an upstream contour/observability and physical-discrimination gap; exact private first harmful stages remain segment-specific until reviewed.
- Prior mechanisms reviewed: R22/R22-2 evidence and diagnostics, public probe, reviewed BASE/Accum checkpoints, R23 rejection, and existing parent validation.
- Prior mechanisms rejected: threshold widening, polarity/source/motion identity, unpartitioned calibration, private-coordinate tuning, missing-as-zero, stale identity/coordinate transfer, interpolation/carry and downstream repair.
- Preserved contracts: generic bounded detector, exact current-frame provenance, independent Oil/Foam, typed no-interface state, fail-closed ambiguity/unobservability, bounded resources and separate Windows field acceptance.
- Difference from prior failures: extraction, discrimination, behavior and field qualification are independent gates with explicit positive/negative/unresolved labels and leakage controls.
- Logic-map impact: NONE — the clarification changes no implementation or acceptance owner; the mapped diagnostic route and production flow remain unchanged.
- Failure-registry impact: NONE — it adds acceptance obligations for existing named mechanisms without claiming a new cause or repair.


## A2 temporal correspondence diagnostic controls

The frozen [ordered-patch contract](../20-architecture/s11-interface-observability-witness-architecture.md#a2-ordered-patch-temporal-correspondence--bounded-diagnostic)
requires synthetic controls for a large displacement with additive exposure,
reciprocal recovery, duplicate-pattern ambiguity, constant-pattern ambiguity,
perfect stationary-structure match without identity, ordered-pixel differences
hidden by pooling, unavailable border support and invalid inputs. Existing gray
residual results must remain unchanged. Real runs retain source/geometry/spec
hashes, all forward/reverse alternatives and both native/0.5-second cadences.
Endpoint and intermediate physical agreement remain separate. No W3 identity or
field claim follows from correspondence alone.

## A2 temporal region-exchange controls

Freeze the architecture contract and source before real inference. Synthetic
controls cover large positive/negative displacement, both contrast polarities,
stationary structure, moving ribbons, additive exposure, masked unavailability,
invalid inputs, input immutability, finite serialization, full least-squares
numerical equivalence and incomplete/duplicate-sector aggregation. The existing
region-competition regression suite must remain passing.

Run the real saved-input adapter over all 153 candidates and verify source,
packet, raster, masks and immutable target-snapshot hashes. Keep every competitor
and searched cut, exact ties, support and abstention reasons. W3 is the sole
identity/target evaluator; no hand-written success metric replaces it. Compare
all seven reviewed positives and three reviewed wrong targets to the unchanged
selection baseline. Report unreviewed supports separately without creating truth.
Any protected-positive loss prevents adoption even if all wrong targets abstain.
Scalar/contour, independent recording generalization and field remain unevaluated.
