# S11 Interface Observability Witness Architecture

**Status:** O1 extraction implementation contract; later O2–O5 remain proposed.
This document grants no new production authority.
**Parent design:** [Physical Interface Evidence Repair](s11-physical-interface-evidence-repair-design.md).
**Validation:** [Interface Observability Witness Validation](../30-validation/s11-interface-observability-witness-validation.md).
**Assessment:** [Transparent-Interface Detector Direction](../50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md).
**Behavior baseline:** R22-2; O1 adds diagnostic runtime R22-3 only.

## Purpose

Define the smallest observation-layer redesign that can answer three questions
before another temporal repair is attempted:

1. Is the current frame capable of exposing the target uppermost fluid boundary under
   the active optical conditions?
2. Which spatial contour is supported as that target, distinguishing internal
   material interfaces as well as vessel reflections, fitting/wall edges,
   residue stripes or unresolved structures?
3. How uncertain is the contour localization in each part of the sight-glass?

The first implementation is diagnostic-only. It may measure and serialize raw
witnesses, but cannot change candidate count, score, rejection, authority,
tracklet identity, phase state, selector output, Foam output or publication.

## Non-goals

This architecture does not:

- assign a new detector revision/runtime identity before implementation review;
- activate the proposed `OBSERVED_INTERFACE` phase;
- change fill-owner handoff, initial-FULL admission or drain release;
- declare a material/raster path to be the physical interface merely because it
  exists;
- use source family, recurrence, motion or photometric sign as physical identity;
- fit operating thresholds from the 13 public truth frames or from private
  checkpoint coordinates;
- add interpolation, coordinate carry or report-side repair;
- train or deploy a neural network; or
- require export of private Windows media.

## Responsibility boundary

```text
current source frame + Glass ROI/masks + acquisition metadata
  -> bounded contour hypotheses already represented by current candidates
  -> per-sector localization and observability measurements
  -> typed OilInterfaceWitness (trace-only first)
  -> [future, gated] independent support / physical association
  -> existing authority / tracklet / lifecycle / selector / projection
```

The witness is owned at `FRAME-EVIDENCE` / `OIL-CANDIDATE`. It is normalized
once by candidate identity. Later owners consume the same immutable result;
they do not reconstruct a different interface decision from raw dictionaries.

## Core data model

The names below are proposed semantic types. Exact Python module boundaries may
change during implementation review, but their meaning and ownership may not.

### `FrameOpticalObservability`

One record per Glass and source frame:

| Field | Meaning |
|---|---|
| `frame_index`, `glass_id` | exact source identity |
| `acquisition_mode` | passive/uncontrolled, passive/fixed, structured-background, polarized pair or another explicitly configured mode |
| `exposure_identity` | available fixed/auto exposure, gain, white-balance and illumination metadata; missing remains unavailable |
| `visible_fraction` | usable effective-mask support after glare/exclusions |
| `saturation_fraction` | clipped dark/bright support in the effective ROI |
| `glare_fraction` | current optics opposition |
| `texture_reference_available` | whether the acquisition mode provides a usable reference/background channel |
| `status` | `OBSERVABLE`, `DEGRADED`, `UNOBSERVABLE`, or `NOT_EVALUATED` |
| `reasons` | evaluated predicates and unavailable mandatory channels |

`UNOBSERVABLE` means the image does not support a defensible interface decision.
It is not FULL, EMPTY, candidate absence or detector failure. In trace-only mode,
`status` remains `NOT_EVALUATED` while raw availability values are collected.

### `InterfaceContourHypothesis`

A frame-local spatial representation attached to one existing Oil candidate:

| Field | Meaning |
|---|---|
| provenance | candidate input identity, source, source Y, crop transform and generating measurement lineage |
| sector geometry | actual source X range and local/source Y for each available sector |
| localization interval | bounded Y interval or uncertainty for each sector; never inferred from another sector |
| curve summary | optional robust low-order curve/Bézier representation, residual and inlier sectors |
| support mask | which sectors/channels are measured, missing or invalid |
| competing peaks | bounded count and separation of plausible local edge centers |

Initial implementation reuses the existing five-sector material-path grid. Other
candidate families are sampled on the same actual X extents when possible. A
scalar candidate Y remains for compatibility/publication, but it is not treated
as exact truth for every sector of a curved interface.

A curve summary requires at least three valid spatially distinct sectors. It is
a compact descriptor only: fitting cannot invent missing points, recenter the
candidate, add a proposal or grant identity.

### `InterfaceSectorWitness`

One bounded descriptor per valid contour sector. Measurements are made along the
local contour normal where geometry permits; the first implementation may use a
vertical normal with the approximation recorded explicitly.

Required raw groups:

1. **availability and geometry**
   - exact band pixel ranges and valid fractions;
   - candidate/path center, local peak centers and localization uncertainty;
   - curve-normal approximation and mask clipping;
2. **relative photometry**
   - signed and absolute above/below difference at fixed small/medium/large
     scales;
   - locally normalized contrast resistant to global brightness/gain changes;
   - saturation and glare support;
3. **edge topology**
   - normal-aligned gradient magnitude and sign;
   - gradient-direction agreement with the local contour normal;
   - edge-density change above versus below, not edge count alone;
   - width/plateau and competing-peak descriptors;
4. **two-sided material context**
   - near and far material/texture summaries on both sides;
   - internal-stripe evidence when near contrast is not sustained into broader
     region context;
   - current raw material map provenance, never final Foam authority;
5. **structural opposition**
   - static-map, border, exclusion, glare and optics overlap;
   - vessel-contour curvature/fitting-risk descriptor where geometry exists;
   - explicit missing structural reference;
6. **optional acquisition-specific evidence**
   - structured-background displacement and correlation quality;
   - paired-polarization or paired-illumination difference;
   - reference-frame registration uncertainty.

All values retain channel lineage. Values derived from the same grayscale/Sobel
chain cannot be counted as independent evidence merely because they have
different field names.

### `OilInterfaceWitness`

One immutable aggregate per candidate:

| Field | Meaning |
|---|---|
| `contour` | the bounded spatial hypothesis above |
| `sectors` | exact sector witnesses, including unavailable reasons |
| `usable_sector_count` | spatially distinct usable sectors |
| `lineage_groups` | independent/shared raw derivations |
| `observability` | reference to the frame-level optical record |
| `localization_uncertainty_px` | aggregate uncertainty without discarding per-sector intervals |
| `opposition` | typed structural/optical contradictions |
| `decision` | `INTERFACE_SUPPORTED`, `INTERNAL_OR_ARTIFACT`, `UNRESOLVED`, or `NOT_EVALUATED` |
| `decision_reasons` | actual predicates, thresholds and unavailable inputs |

Trace-only implementation sets `decision=NOT_EVALUATED`. A later shadow
classifier may populate the other outcomes, still without affecting production.
Only a separately accepted behavior revision may expose the decision to authority
or association.

## Measurement semantics

### Photometric invariance is bounded, not assumed

Use ratios/local normalization only where denominators and valid support are
explicit. Global brightness/gamma/contrast stress is a robustness control, not
evidence that field illumination changes are equivalent. Sign is retained for
diagnostics, but no universal Oil-dark/Oil-bright rule is allowed.

### Interface versus internal stripe

A localized edge is insufficient. The witness must compare immediate bands with
broader two-sided context and edge-density/material changes. A thin stripe can
produce a strong near contrast yet return to the same material context on both
sides. A true interface may also have weak or inverted gray contrast, so the
classifier requires multiple complementary channels and may remain unresolved.

The existing public probe shows that `abs(near)-abs(far)` is negative for many
truth-near candidates and overlaps remote geometry. That scalar cannot become a
new veto or authority gate by itself.

### Vessel reflection and fitting risk

Where the Glass boundary/shape is known, record whether a candidate follows
high-curvature vessel regions, fixed fittings, cap/border geometry or persistent
static reflections. This is opposition, not automatic rejection: a real
interface can cross a reflective region. The decision must preserve per-sector
support and may classify the result as unresolved when physical causes overlap.

### Localization uncertainty

Uncertainty increases when:

- several comparable peaks exist inside the bounded search interval;
- peak center changes materially with scale or sampling center;
- valid support is clipped by masks/glare;
- only one or two sectors support a curve;
- registration/reference correlation is weak.

Differences between native sector heights and the scalar median describe contour
shape, not localization uncertainty. Preserve that range separately; only local
measurement ambiguity belongs in a sector interval.

Uncertainty is not a score penalty that can be averaged away. Later association
must compare contour intervals/common sectors and may abstain.

### Explicit unobservability

A frame may contain many candidates while remaining physically unobservable.
Examples include homogeneous transparent phases with no stable refractive cue,
severe glare/saturation, unresolved vessel reflections or acquisition changes
that invalidate a reference. Such frames must not be converted into numeric Oil
through persistence, ranking or lifecycle context.

## Independence and lineage

Every raw descriptor carries a derivation identity such as:

- `gray/current-frame/local-normal`;
- `sobel-from-gray/current-frame`;
- `raw-material-map/current-frame`;
- `static-reference/prior-calibration`;
- `structured-background/reference-pair`; or
- `paired-polarization/current-cycle`.

Two candidates or fields sharing the same derivation contribute one lineage
family. Different source strings do not establish independence. A future
independent-support decision requires both physical contour agreement and the
configured lineage rule; hard-invalid peers cannot corroborate.

## Trace schema and bounded storage

Proposed schema identity:
`interface-observability-witness-trace-v1`.

The trace records:

- frame optical observability inputs;
- candidate identity and exact contour/sector coordinates;
- raw sector descriptors, availability and lineage;
- aggregate uncertainty/opposition;
- `NOT_EVALUATED` during extraction stage; and
- later shadow outcomes with evaluated predicates when enabled.

Do not serialize full rasters, unbounded peak lists or frame history. Reuse
frame-local prefix/profile caches. Bounds:

- current existing candidate limits;
- five sectors initially;
- three fixed photometric scales unless separately justified;
- a fixed small number of competing peaks per sector;
- one frame-local record per candidate; and
- no temporal witness history until a later association stage owns a fixed
  window.

Debug NONE performs no witness capture or serialization. Enabling BASIC/FULL
trace must not change detector output. Trace growth and runtime are measured on
all four public videos before acceptance.

## Acquisition modes

Software and acquisition are evaluated as separate axes.

### A — Current passive video

Use the existing camera/fixture. Record whether exposure, gain, white balance
and focus are fixed or automatic. This is the compatibility baseline, not the
assumed final sensing solution.

### B — Fixed passive acquisition

Lock focus, exposure, gain and white balance where hardware permits; use a stable
camera pose and vibration-resistant fixture. Compare observability and witness
stability without changing detector thresholds.

### C — Controlled diffuse illumination

Evaluate front/side/back diffuse illumination or bright-/dark-field pairs as
fixture constraints allow. Where camera response and sight-glass transmission
permit, compare explicitly identified visible and near-infrared illumination;
do not assume either spectrum separates Oil and refrigerant without measurement.
The goal is to create a reproducible interface cue, not simply increase global
brightness.

### D — Structured background / refractive displacement

Place a calibrated random-dot/grid reference behind the visible path when
mechanically possible. Measure local displacement/correlation rather than only
intensity edges. Glass/liquid optical layers require a reference/calibration
procedure; no raw displacement threshold is accepted without it.

### E — Polarization or dedicated sensor escalation

Cross-polarized or paired-polarization captures may suppress/specify reflections
when cycle timing permits. If required operating states remain unobservable,
compare a dedicated optical point switch, float/electronic oil control or other
independent sensor as validation/product sensing. This is an engineering
boundary decision, not a software fallback coordinate.

## Staged implementation and acceptance

### Stage O0 — Baseline probe (`COMPLETE`)

The public probe records current proposal recall and descriptor overlap under
bounded photometric transforms. It changes no behavior and selects no threshold.

### Stage O1 — Typed extraction (`LOCAL ACCEPTANCE RECORDED`)

[Completed O1 evidence](../60-evidence/s11/s11-r22-3-interface-witness-diagnostics.md)
records extraction/equality and resource results; Windows effectiveness and O2
discrimination remain unqualified.

Implement the data types and trace-only measurements. Required checks:

- exact debug-on/off candidate and final output equality;
- source/crop/sector provenance and unavailable values;
- curved contour, clipped mask, glare, duplicate and competing-peak controls;
- photometric transform invariants without polarity assumptions;
- fixed resource bounds and strict finite JSON; and
- no resolver-facing field or candidate mutation.

### Stage O2 — Shadow discrimination

Create explicitly labeled positive, negative and unresolved controls. Select
operating points with declared development/holdout separation. The shadow
classifier writes only diagnostics. Required labels distinguish:

- physical interface;
- internal stripe/residue;
- vessel reflection/fitting/wall edge;
- localization mismatch near the interface;
- insufficient/unobservable evidence; and
- ambiguous competing structures.

Public truth Y alone supplies geometry, not all physical-negative labels. The
already selected private checkpoints are final domain checks, not ad hoc
threshold targets. Any broader private field calibration requires a predeclared
work-PC-only episode-level development/calibration/holdout partition with an
untouched holdout.

### O2 implemented evaluation foundation

`tests/diagnostics/s11_interface_shadow_evaluation.py` is an offline diagnostic
owner, not a production classifier. It reuses `ResultBundleReader`, the indexed
`DebugTraceRepository`, file hashing from truth identity, and benchmark canonical
JSON/percentile helpers. Existing `.oiltruth` remains the product's scalar/state
truth format. O2 separately needs candidate identity/localization labels, exact
sector extents, frozen partitions and abstention denominators; changing the
product truth schema or creating a new GUI is unnecessary for this boundary.

The four commands prepare, combine, freeze and evaluate retain every selected
frame and Oil candidate. Packet preparation never infers labels. Frozen labels
bind to packet and witness content hashes; prediction joins use the same candidate
input identity. The initial split rule keeps entire original-recording groups in
one partition, including transforms, Glasses and reruns. This is intentionally
stricter than episode-only splitting. Previously reviewed data is regression.
Original-recording equivalence across different runs remains a human attestation.

The evaluator measures imported shadow predictions but supplies no model or
operating point. Missing predictions become NOT_EVALUATED; visible empty-candidate
frames remain in the frame denominator. Localization mismatch is positive physical
identity with a separate localization error, never a structure negative. Unknown
physical labels cannot silently become verified positives or negatives. No automatic
O2 acceptance is emitted. Exact-X localization and declared interval width/coverage
are reported independently from identity decisions. Internal classifier independence
and untouched-holdout history cannot be certified by the interchange format.

See the [local procedure](../40-operations/s11-o2-local-shadow-evaluation.md).
This tooling does not complete O2 discrimination acceptance or alter R22-3 runtime.

### O2 durable local review records

The same CLI delegates bundle receipts and human edits to
`tests/diagnostics/s11_review_records.py`. It reuses the existing bundle/index
readers, truth identity/file hashes and `json_recipe_repository.atomic_write_text`.
This companion is an offline persistence boundary, not a second evaluator, truth
GUI or detector. No production imports call it.

`link-bundle` compares every packet frame/witness with the indexed trace and records
manifest/recipe/session/trace/index hashes, run identity and source-video SHA-256.
The initial claim that a selected video produced an older bundle remains an explicit
human attestation; a newly computed hash cannot prove it retroactively. `relink`
requires the same registered bytes and metadata before updating locators. Paths
are relative where possible and absolute across Windows drives. Identity does not
include transport paths. No source images or full trace are copied into labels.

The receipt binds packet hashes and stores a conservative scene key from exact
video bytes, source frame, coordinate dimensions and Glass geometry. Case visibility,
contour and scene-review provenance are separated from execution-specific candidate
labels and witness hashes. This preserves the inputs for later reviewed reuse; no
command transfers a label to a new execution or guesses correspondence. Different
media encodings/geometry require explicit future correspondence review. The receipt
is retained beside each original review even after combine/freeze; it is not an
automatic video authenticity or holdout certificate.

`status` validates v1 and v2 drafts and lists pending/unreviewed/held judgments without
rehashing large live files. `record` applies one sparse human reply to a specified
label-content hash under an exclusive writer lock, validates all packet/candidate
references, archives the entire old draft and atomically replaces the live JSON.
Scene review provenance survives candidate-only corrections. Unmentioned cases and
candidates remain untouched. Drafts may be pending; freeze still rejects pending
visibility or missing review owners. Frozen snapshots are immutable separate files.
History is a local audit trail, not authenticated or signed; external/manual edits
and original-video association remain explicit trust boundaries. An interrupted
writer may leave a stale lock; it must never be automatically broken without
checking for an active writer. Code ZIP replacement never owns the data directory.

### O2 review semantics revision — implemented locally

The transferred [review-002](../60-evidence/s11/s11-o2-windows-review-002.md)
exposes a scope mismatch: a human may recognize an interface proposal holistically
while some of its generated path points lie off the interface. Preserve that
judgment; do not reinterpret it as a guarantee for every point or silently relabel
it as reflection/structure. The following contract is implemented in the existing offline evaluator and record
companion. It changes no detector behavior or witness data. Labels/frozen/report
use v2; packets/witnesses/predictions retain their existing v1 contracts.

#### Separate review questions

| Scope | Question | Stored representation |
|---|---|---|
| Scene | Is the Oil interface visible? | Existing visibility and optional reviewed contour |
| Candidate identity | Does this proposal represent the interface, another object, or remain uncertain? | `identity`: interface / non_interface / uncertain / unreviewed |
| Reviewed geometry | Does this specific displayed segment/point lie near the interface? | `path_reviews[]`: near_interface / off_interface / uncertain / unreviewed |
| Measured localization | What independently reviewed Y interval is acceptable at this X extent? | Existing scene contour; optional, never synthesized from a proposal |

`near_interface` is a qualitative human judgment, not a calibrated px tolerance.
An interface identity and off-interface path parts are a valid combination.
`non_interface` describes physical identity; optional `artifact_tags` may contain
multiple values (reflection, structure, residue, other), with free-text detail.
An empty tag set means no cause was specified, not that identity is uncertain.
A scratch can retain structure plus the user's scratch note, and reflected light
at a scratch may retain both structure/reflection when explicitly reviewed.
Tags are descriptions, not independent evidence votes or mutually exclusive truth.
Legacy `localization_mismatch` remains recorded as reviewed interface identity
with a legacy localization qualification, without inventing sector errors.

Each path review binds the candidate input ID/witness hash, exact source X extent,
reviewed source Y, and geometry basis (native_path or candidate_center). A sector
number alone is insufficient. The displayed geometry must exactly match the bound
witness; a reference candidate at another X cannot certify it. A candidate with
no native path can still be reviewed using its actual candidate-centered geometry;
no synthetic native path is created. Only reviewed geometry gets a judgment;
unreviewed or unavailable portions never inherit a neighbor's label.

Preserve reviewer, original explanation and provenance for each scope. Reviewing a
candidate does not auto-fill path reviews. Record a reviewed overall partial-path
qualification in the note even if exact segment attribution is not yet available.
Do not derive per-sector truth by parsing free text or computing proximity to a
reference. Previously reported direct judgments may be explicitly imported after
exact source/frame/geometry correspondence checks, with their original basis.
A new human question is needed only for information not already established.

#### Evaluation semantics

The [product target](../rotary_oil_level_tracker_ssot_spec.md#다층-유체의-추적-대상)
is the uppermost actual fluid boundary; material-species classification is not
required. Physical interface existence and membership in this target are distinct.
A real lower liquid/liquid boundary is not an artifact, but is not the target
Oil-height boundary. Do not implement this definition as minimum canonical Y
over raw proposals, source-family preference, or a lower-boundary fallback when
the target is occluded. Foam retains its separate owner/output.

The existing v2 evaluator consumes `identity=interface` without a target-role
field. Its mechanics below are unchanged. Historical broad physical-interface
labels must not silently acquire target-specific meaning: preserve original
labels/history and explicitly version/bind target truth before using such a
case for target metrics. A note or target mapping in evidence is not an
implemented evaluator exclusion. No schema migration or runtime change follows
from this target clarification alone.


1. Candidate identity precision/recall uses identity alone; no source family or
   tag count gives extra votes. Unreviewed/uncertain support stays separate and
   visible frames without candidates stay in the denominator.
2. Rename the current label-only frame-support measure to an explicitly
   **identity-support** measure. It cannot assert localization success. Legacy
   interface/localization_mismatch both count as positive identity when mapped.
3. Qualitative path agreement reports supported proposals' reviewed near/off/
   uncertain counts and unreviewed coverage separately. Partial agreement is not
   full-path acceptance. No majority vote or implicit minimum fraction is chosen
   from these few regression examples.
4. Quantitative localization uses only independently reviewed source-X/Y intervals,
   with exact comparable X and geometry. Missing contour yields not_measured/null,
   not zero error. Report the measured extent and missing coverage relative to
   the available/reviewed cases so a small measured subset cannot masquerade as
   complete success. Proposal geometry quality and model-supported geometry quality
   must be distinguishable; wrong/off-interface parts cannot disappear from totals.
5. Do not publish a binary localized-frame PASS until the target geometry coverage
   and tolerance policy is explicitly defined and validated. No currently labeled
   candidate, including a fully near-interface reviewed path, supplies that policy.

#### Explicit uppermost-target binding — implemented offline

`s11_interface_shadow_evaluation.py bind-target` delegates to
`s11_target_truth.py` for the separate `s11-o2-target-truth-v1` snapshot.
This companion owns immutable physical-to-target binding; `s11_review_records`
continues to own mutable human review and the existing evaluator owns metrics.
No product/runtime branch imports the private-case mapping.

- Require v2 physical labels, their exact logical status hash, validated packets,
  exact case/frame/Glass inventory, and an explicit versioned mapping. Bind every
  candidate once with packet/witness and physical-annotation hashes. Retain original
  labels/history in the snapshot, not a rewritten physical labels document.
- Mapping groups explicitly list target/internal-interface indices; only an
  expressly authorized source `non_interface` group may be inherited. Counts,
  source identity, missing/duplicate IDs and target visibility are checked. No
  rank, Y cutoff, material name classifier or nearest-boundary selector is used.
- Target roles are target, internal_interface, other_non_target, uncertain and
  unreviewed. Internal and other non-target map to evaluation non_interface while
  their physical identities remain separate. Empty-case and no-target visibility
  are explicit, not inferred from the proposal list.
- An individually identified wrong Oil target may explicitly map physical
  `uncertain` to target `other_non_target`. The original uncertainty, tentative
  subtype note and review history remain unchanged. This is a negative for the
  target task only; it is not evidence of physical non-interface identity.
  The mapping must list exact candidate indices with attribution; bulk inheritance
  remains restricted to already reviewed source `non_interface`. Unreviewed
  candidates cannot become negatives, and uncertain candidates cannot become
  target-positive or internal-interface truth by this route. Existing snapshots
  keep their projection and hashes; no physical/target schema fields change.
- Snapshot hash covers original physical labels, mapping, bindings and derived
  evaluation content; packet locators remain relocatable. Raw file hashes are
  distinct from logical label hashes. Input bytes are checked before/after binding.
- `load_frozen` recognizes this schema, revalidates packets, recomputes projection
  and compares hashes. It returns an in-memory v2 view to existing metric owners.
  Target reports use `s11-o2-target-shadow-report-v1`, explicit target semantics,
  original physical counts and role counts. Predictions must bind the new
  evaluation-content hash; predictions for old physical truth are rejected.
- Do not transfer source contour/path/entity or artifact-subtype truth to the new
  target view. It remains in the preserved physical snapshot. This initial binding
  implements target identity only; target localization/association truth needs
  its own explicit review and must not be manufactured from role membership.
- New destination only; no source labels/history mutation, training, inference,
  threshold selection or production acceptance. A no-prediction report remains
  NOT_EVALUATED with FIELD FAIL and auto_acceptance=false.


#### W1 target and aggregation contract — design boundary

Live progress, O/W mapping and the next action belong to the
[work-item ledger](../00-project/work-plan.md#s11-work-item-ledger).
[W1 acceptance controls](../30-validation/s11-interface-observability-witness-validation.md#w1-aggregation-challenger-controls--not-yet-acceptance-evidence)
own verification; this design text alone does not complete W1.

Following the [W0 profile result](../60-evidence/s11/s11-o2-identity-profile-windows-run-001.md),
keep three inference targets separate. This section specifies requirements for
the next challenger; it implements no new score, schema field or runtime decision.

| Target | Evaluation truth | Aggregation must not imply |
|---|---|---|
| Candidate identity | Existing holistic `identity` | A majority of near path points, or valid final scalar Y |
| Local path support | Exact geometry-keyed near/off/uncertain judgments | Identity from one strong edge; a px error from qualitative truth |
| Scalar eligibility | Independent scalar truth or a declared contour-to-scalar policy | A native point median may replace the original candidate's Y |

Scene visibility remains an independent denominator, and association/phase is a
later temporal target. Missing scalar truth means eligibility is unverified,
not a measured failure or zero error. Identity may be supported while scalar use
is unknown or contradicted. These are semantic distinctions, not new wire enums.

A candidate with local scores [0,1,0] can be a holistic interface positive with
an off/near/off path. Median pooling can rank it below a negative [0.1,0.1,0.1]
even if the local localization signal is ideal. Conversely, an isolated glare
negative can also have a high central local score: max/top-quantile pooling is
not a general identity repair. Local edge strength is not the same target as
local physical interface support. If the supplied evidence is indistinguishable
for a partial interface and a glare negative, require unresolved model identity;
do not change either human label or claim the aggregator has separated them.

The next candidate-level challenger must retain contributing geometry, measured
extent, missing/contradictory evidence and any independently justified identity
context. It may use existing spatial/region/static evidence only with explicit
semantics and positive/negative controls. Never use human near/off labels to pick
inference sectors. State why its output answers holistic identity before choosing
pooling or a threshold. Do not infer that spatial continuity alone provides identity.

Score-only profile outcomes cannot identify whether the first loss is sampling,
missingness, aggregation or a shape collision. Inspect existing owner definitions
and use bounded synthetic counterexamples first. The
[W1 source review and counter-controls](../60-evidence/s11/s11-o2-w1-target-aggregation-controls.md)
exercise the current owners without installing a replacement aggregation rule.
Preserve existing v2 labels, original v1 experiments and current production
scalar provenance.

The aggregation design boundary is **geometry-indexed evidence before an identity
decision**, not a new scalar pooling formula. Retain all measured support and
opposition with their X/Y/basis, availability and derivation lineage. A median or
maximum may describe that evidence but cannot by itself supply holistic identity.
Even an ideal local-position signal can disagree with the holistic target.
Spatial arrangement is necessary to retain but is not sufficient to distinguish
two physically different scenes with identical supplied observables.

`BandWitness` already retains static/material/glare/visibility context. The current
fixed-score consumer intentionally reads only its specified C/A/L inputs, and the
profile consumer reads four gray means and sampling ranges. Static overlap is not
a non-interface truth label: a real stationary interface or crossing structure
can share it. Production phase/authority context has separate availability and
ownership contracts and is not automatically present in an O2 packet. Any future
use requires exact provenance and positive/negative controls; reusing a production
decision as ground truth would be circular.

For indistinguishable inputs, the required future identity outcome is unresolved,
while both human identities remain intact. The current scorer emits rankings,
not that decision; existing `UNRESOLVED` evaluator controls demonstrate accounting
only. W3 must expose the identity/local/scalar distinctions and coverage together;
W4 must justify one discriminating mechanism before any promotion. No high local
score, majority vote, complete abstention or missing contour can stand in for
successful scalar observation.

The [identity context source audit](../60-evidence/s11/s11-o2-identity-context-source-audit.md)
verifies an additional representation boundary: a candidate's finite bands can
be identical in two different wider rasters. Preserving geometry and all current
context fields does not preserve image evidence outside that support. Material
means describe raw appearance and static overlap describes reference persistence;
neither is an Oil probability. A future context mechanism must identify the
specific additional observable and counterexample, reuse existing extraction and
evaluation owners, and preserve missing/unknown rationale. This does not authorize
automatic band expansion or changing candidate identity from scene proximity.

#### Versioning, migration and implementation boundary

Use a versioned label/frozen/report contract for the changed meaning, with explicit
v1 compatibility. `migrate` must write a new destination, retain the original label
value/notes and origin hash, and reuse unchanged packet/witness evidence. Preserve
old labels, frozen sets, replies, receipts and history. Never overwrite a frozen
v1 result or silently reinterpret its localized-support metric as a v2 result.
No existing R22-3 bundle or source video needs rerunning, rewriting or re-exporting.
New candidate-identity and scene labels stay distinct from per-execution path
reviews; this does not implement automatic new-run candidate matching.

Extend the current O2 evaluator/record companion, not a parallel label system.
The implementation comprises explicit migration, scoped reply validation and
storage, status coverage, separated metrics, focused compatibility/semantic controls
and the agent procedure. It does not add a GUI, detector revision, classifier,
production authority, or owner handoff. Prior image-display/Y-axis requests remain
operational review requirements; a new rendering subsystem is not part of this
contract. Existing Windows reviews can migrate and resume bounded annotation;
local semantic tests do not certify Windows labels or a shadow classifier.

`prepare` now creates `s11-o2-labels-v2`. Old v1 labels remain readable/editable
using their original fields; new fields require explicit `migrate`. The new command
requires an expected source label hash, locks source/destination, creates a new file,
archives the original logical JSON and retains original reply history. The original
file and all old history/receipts/frozen results remain untouched. Migration itself
does not increment the human-reply revision count. Its operator/time describe
conversion, not a new physical review. Legacy candidate objects are preserved in
`legacy_annotation`; unresolved/unobservable map to uncertain identity with their
original distinctions retained there. No free-text parsing creates path labels.

`record` v2 accepts sparse identity/tag/entity changes and per-geometry path upserts.
A path reply contains `geometry_basis`, `source_x_range`, `source_y`, `judgment`;
the enclosing candidate ID and witness hash bind it to one frame/proposal. Exact
witness X/Y/basis matching is required. Absent path reviews remain unreviewed;
an explicit unreviewed judgment resets only that geometry and retains history.
Scoped review metadata records reviewer/note/time/basis. Candidate-only changes
preserve scene attribution; path-only changes preserve identity attribution.
Native and candidate-center geometries have separate coverage denominators.

`freeze` preserves the input label version in the corresponding frozen version.
`combine` requires uniform versions (explicitly migrate mixed inputs first) and
retains source-label hashes/locators; source histories stay in their review folders.
`evaluate` accepts frozen v1/v2 and always writes a new `s11-o2-shadow-report-v2`,
explicitly naming the source label schema. Old reports are never edited or emitted
under a v1 name with new semantics. `visible_frame_identity_support_recall` replaces
the old localization-sounding frame metric. Qualitative path rows/totals distinguish
all proposals from model-supported proposals. Numeric localization separately
reports all interface proposals and supported interface proposals, matched/eligible
sector coverage, per-sector errors, interval width/coverage and not_measured/null.
No missing contour is replaced with candidate geometry; full-path PASS stays null.
Artifact family counts apply only to non-interface identities and may overlap;
identity totals count each candidate once. Packet and source data remain local.

### Stage O3 — Independent support and association

Only after O2 passes may the typed result feed the parent design's independent
support and `SAME_INTERFACE`/`DIFFERENT_INTERFACE`/`UNRESOLVED` association.
R23's photometric-reversal positives and all current tracklet ambiguity controls
remain protected.

### Stage O4 — Handoff and phase behavior

Committed owner handoff and direction-neutral visible-interface phase remain
separate acceptance gates under the parent architecture. No O1/O2 result
implicitly authorizes them.

### Stage O5 — Target-Windows qualification

Run the current canonical Windows procedure. Measure by segment and reviewed
physical identity:

- interface proposal recall;
- supported/wrong-structure/unresolved witness rates;
- contour localization error and uncertainty calibration;
- association split/merge errors;
- numeric Oil accuracy/coverage;
- false numeric publication;
- throughput and trace/storage bounds.

No media export is required by the design. The work-PC runner can produce the
same bounded numeric/decision schema; any export remains subject to local data
policy. Human review on the work PC remains the authority for physical labels.

## O1 implemented measurement contract

Runtime `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1` adds only
`artifacts.state.oil_interface_witness`. Resolver identity remains R22. The
existing `oil_interface_diagnostics` schema and every old field remain unchanged.
The [supplemental execution review](../50-diagnostics/s11/s11-observation-redesign-execution-review.md)
is supporting rationale, not a competing implementation owner.

- `oil_interface_diagnostics.measure_oil_interfaces` retains its original return
  value and accepts an optional typed witness sink. It shares its existing
  native/candidate geometry and frame-local gray/material/static prefix cache
  with `oil_interface_witness`; no second band, path generator or gray-profile
  implementation is introduced.
- `PhaseDebugProjector` requests the sidecar only in the existing debug path,
  serializes frozen records containing only scalar values and tuples, and never
  adds them to detection metrics or candidate dictionaries. Debug NONE does no
  new work. No changes to authority, association, phase or selector are made.
- Existing native sectors are preserved even when their bands are unavailable.
  With no valid captured native path, measure candidate-centered geometry with
  `candidate_center_only` and the original path-unavailable reason. Never borrow
  another candidate's path. Common X comparisons use the native sector extent.
- Base width `b=max(3,min(12,round(crop_height*0.01)))`; new widths are exactly
  `b,2b,3b`. Each uses the existing four-band offset/exclusion contract at that
  width. Record intended and clipped half-open pixel intervals. Existing
  candidate source Y is never rounded away; sampling uses `floor(local_y+0.5)`.
- Gray is raw uint8/255. Delta is below mean minus above mean. Normalization is
  `delta/sqrt(std_above**2+std_below**2+(1/255)**2)` with raw delta and denominator
  retained. The floor is numerical regularization, not calibrated sensor noise
  or a confidence estimate. No universal gain invariance is claimed.
- Edge density uses the existing current Canny raster, valid-mask pixel count
  as denominator. Raw-gray central differences in X/Y supply gradient magnitude
  and absolute vertical-normal alignment `sum(abs(gy))/sum(hypot(gx,gy))`.
  All four neighbors must be visible. A zero denominator is null, not perfect
  alignment. Vertical normal is explicitly an approximation.
- Band saturation counts exact raw endpoints 0/255 inside the effective mask;
  mask exclusion is the fraction outside the effective mask. Their denominator
  is the clipped rectangle area, unlike the old valid_fraction denominator
  (intended area). Missing vessel/fitting geometry stays unavailable; no ellipse
  curvature classifier or acquisition-specific algorithm is introduced.
- At each width `s`, search `[center-s,center+s+1)` on the existing central
  difference of masked row means. Keep signed-gradient plateaus within 1e-12;
  opposite signs are separate peaks, even at equal magnitude. Flat profiles
  have none. Rank by absolute magnitude then lowest source Y; retain at most
  three, with pre-truncation count and boundary-contact flags. The retained
  plateau hull is half-open, uncalibrated, and explicitly incomplete on
  truncation. A single peak is not a physical-interface decision. The same
  gradient profile is searched at three radii, not three independent channels.
- No scalar aggregate uncertainty estimate is invented: it remains null with
  `no_calibrated_uncertainty_estimator`. Contour height range is geometry only.
  O2 must evaluate hull width/coverage and miss/abstention rates together.
- Frame visibility/glare/saturation use effective-mask pixels as denominator;
  empty masks yield null. Exposure/reference metadata is unavailable. Frame
  status and candidate decision remain `NOT_EVALUATED`, even with strong edges.
- Raw gray, its derivatives, Canny and raw material map share current-RGB ancestry.
  Static reference availability is separate. Complementary features are allowed,
  but never counted as independent sensor votes.
- Bound storage by existing candidate count, at most five sectors, two centers,
  three scales and three peaks per scale. Only frame-local raster/profile caches
  exist. Identical native/candidate centers are measured once. No curve fitting,
  registration, polarization/BOS or temporal history is part of O1.

The public probe v2 preserves missing material-conflict as null, verifies joins,
and reuses existing source/runtime provenance helpers. The v1 baseline summary
remains historical evidence; a changed schema/runtime must not overwrite its hash.

## Rollback and promotion

O1/O2 are removable diagnostics. Rollback means deleting the sidecar/trace path
while leaving R22-2 decisions byte-equivalent. Promotion requires:

1. focused extraction and synthetic discrimination PASS;
2. four-video behavior equality during trace/shadow stages;
3. governance and full test suites PASS;
4. measured resource impact;
5. reviewed target-Windows evidence for the exact candidate runtime; and
6. an explicit acceptance record assigning the next detector identity.

Until all applicable gates pass, work-plan status remains `FIELD FAIL` and the
new witness has no production authority.

## W3 separated shadow targets

The existing `s11_interface_shadow_evaluation.py` owns prediction validation and
evaluation. Prediction v1 and no-prediction readiness retain report v2 semantics.
`s11-o2-shadow-predictions-v2` adds `target_spec_id` =
`identity-local-support-original-scalar-v1`, an `operating_point_id` and explicit
`evaluation_regime`. Report v3 adds `targets` by partition while preserving the
existing identity/contour metrics in `partitions`.

Each prediction retains case/candidate/witness identity, `decision` and `reason`.
Its required target fields are:

- `local_support`: a possibly empty list keyed by exact `geometry_basis`,
  `source_x_range`, `source_y` from `review_geometry`. Decisions are
  `NEAR_INTERFACE`, `OFF_INTERFACE`, `UNRESOLVED`, `UNOBSERVABLE`, `NOT_EVALUATED`.
  Each has `availability` and `reason`. An optional `source_y_interval` is
  validated and retained in the prediction fingerprint; it is not scalar truth
  or a new interval-calibration metric.
- `scalar`: `decision` (`USABLE`, `UNUSABLE`, `UNRESOLVED`, `UNOBSERVABLE`,
  `NOT_EVALUATED`), `availability`, `reason`, `policy_id=original_candidate_y_v1`
  and the unchanged original candidate `source_y`. USABLE requires supported
  candidate identity and finite original Y. No average/median of near points or
  inferred contour is substituted for the generator's Y.

Availability is `unavailable` for UNOBSERVABLE, `not_evaluated` for NOT_EVALUATED,
and `available` for other explicit local/scalar decisions. Missing predictions
are counted separately as `MISSING_PREDICTION`. Local counts preserve candidate
identity, basis, qualitative truth, abstention and all available geometry points;
unreviewed or uncertain truth cannot turn a decisive prediction into a verified
success. Empty visible frames remain in frame coverage denominators. Supported
identity need not imply a fully near path or a usable scalar. Scalar results are
always `not_measured` under this contract: labels have no independent scalar
truth or accepted contour-to-scalar policy. USABLE is a prediction, not proof.

CALIBRATED imports retain the nonempty development/calibration fit declaration
and existing frozen/partition checks. EXPLORATORY_UNCALIBRATED requires explicit
`evaluate --exploratory`, empty fit partitions and regression-only cases.
Neither regime grants auto acceptance or verifies training chronology. Existing
rank-experiment output is not a prediction document and is never converted by
thresholding or using labels as inference inputs.

### Human reference uncertainty and model abstention

The existing label and prediction schemas already represent different axes:

| Source | Value | Meaning |
|---|---|---|
| Human candidate identity / local path review | `uncertain` | Reviewed but not resolved for that target |
| Human candidate identity / local path review | `unreviewed` | No completed judgment for that target |
| Model prediction | `UNRESOLVED` | Explicit model abstention; not a human label or verified correct answer |
| Model prediction | `UNOBSERVABLE` | Explicit unavailable-observation outcome; not equivalent to no prediction |
| Model prediction | `NOT_EVALUATED` / absent record | Explicit non-evaluation / missing prediction, accounted separately in v3 targets |

Unknown human truth remains in confusion/inventory and coverage accounting. A
supported identity on uncertain/unreviewed truth is unverified, not a true or false
positive under verified identity precision. Likewise decisive local predictions
on unknown local truth are not reviewed successes. Conditional precision/accuracy
must be read with unverified support, abstention, missing predictions and full
coverage denominators; undefined metrics remain null. A model abstention on a
known positive does not earn recall. Numeric scalar truth remains separate.

A later human explanation can qualify a historical binary judgment without
silently mutating it. The evaluator consumes the pinned structured labels; it
does not parse notes, chat text, glare magnitude or known candidate IDs to replace
truth. Such qualifications belong in linked evidence accompanying interpretation.
Any authorized formal label change must use the existing attributed revision /
freeze / prediction-hash workflow, preserving the original outputs. A different
truth denominator is not a method improvement and must not be pooled with gains
on unchanged truth/support. Rank ties and unavailable scores are not predictions
of UNRESOLVED. This boundary adds no classifier, confidence threshold, new schema
or second labeling system.

### Existing context and recorded funnel audit

`s11_shadow_experiment.py --target-audit` reuses existing label/packet validators,
original v1 reference equality and immutable-input receipts. A small
`s11_shadow_target_audit.py` helper owns only context projection and joining
recorded decision witnesses. It does not score, write trace, rerun authority or
introduce a second label system. Context preserves all actual center/scale/band
rows with missing/null/present, native/center basis and availability; aliases do
not become independent measurements. Descriptive summaries are not a fit dataset
or evidence of general discrimination.

With `--bundle`, reuse `ResultBundleReader`, `DebugTraceRepository` and existing
review-record packet verification. The public debug record model omits the raw
top-level `sequence` snapshot, so the audit reads that one indexed record with a
16 MiB bound and validates its identity. Join R21 decision-witness member
`candidate_offset`, source and Y against the original O1 candidate inventory;
never join score-sorted sequence candidate positions. Expose recorded tracklet,
phase, publishable and selected facts. A missing retained ref cannot distinguish
pre-retention authority rejection from top-k or another earlier loss. An absent
witness stays UNAVAILABLE. Sequence facts do not certify final CSV publication.

This audit supplies the private availability/recorded-loss evidence needed to
select a W4 mechanism. It creates no predictions, human labels or production
changes. [Operations](../40-operations/s11-o2-local-shadow-evaluation.md#w3-targetcontext-audit--기존-자료로-실행)
own the executable handoff and [local evidence](../60-evidence/s11/s11-o2-w3-target-evaluation-local.md)
records the verified boundary.

### Recorded structure-context projection

The optional `--structure-context` extension requires `--target-audit` and the
original indexed `--bundle`. The existing audit helper/experiment runner remain
the owners. Its artifact declares `recorded-structure-context-v1`; the report and
receipt use `s11-o2-structure-context-audit-v1`. Without the flag, the existing
W3 report contract remains unchanged. All original inputs/scores/evaluation must
still reproduce the fixed-score v1 reference before publication.

The projection joins raw trace candidates by original `candidate_input_index`
plus source/kind/canonical Y/local Y/rejected against verified O1 candidates.
Score-sorted positions are not identities. It retains a fixed numeric field list
from **each** of `features` and `penalties`: artifact/static, optics/glare,
border/exclusion, texture conflict, boundary/broad/narrow/polarity context, material
terminal support and registered-artifact match/geometry. Do not merge the two
containers or run `OilCandidateEvidence.from_candidate`: defaults and derived
composites would erase missing-input provenance. Container and field
missing/null/present states are separate; zero is present, booleans/nonfinite
numbers are invalid numeric evidence. Reject reason and feature score are recorded
provenance, not independently validated physical truth.

Read the exact Glass's raw recipe `geometry.artifact_templates`, ellipse and
exclusions, preserving missing/null/empty and registration metadata. The standard
recipe model supplies defaults and is insufficient to prove raw field presence.
An empty template registry does not prove that a physical structure is absent;
a match does not establish non-interface identity. O1's constant
`vessel_fitting_geometry_unavailable` does not describe whether recipe artifact
templates were registered. Existing `artifact_calibration.apply_artifact_templates`
and `OilCandidateEvidence` remain production owners; neither is rerun by this
projection. No new templates, matching thresholds, gates or derived scorer enter
production or shadow decisions. Raw same-frame feature families are correlated,
not independent witnesses. Historical template registration notes do not prove
independent annotation provenance.

The structure payload resides at
`target_audit[].recorded_funnel.structure_context`; it is available independently
of whether a sequence decision witness exists (`recorded_funnel.status` may be
UNAVAILABLE). A summary is generated from these exact projected records. Original
input preservation, bounded indexed reads, exclusive output creation and COMPLETE
receipts apply. This projection closes an input-discovery gap; it is not a W4
identity challenger or an accuracy result.

## W4 paired-scale comparator boundary

The [fixed-score diagnostic specification](../50-diagnostics/s11/s11-o2-fixed-score-experiment.md#w4-paired-scale-local-comparison)
adds one local-position experiment to `s11_shadow_experiment.py`, the existing
score/pair orchestration owner. It compares independently reduced v1 combined
scores with the median of paired differences on exactly the same available
band widths and X range. Measurements, locality, original geometry and candidate
scores stay fixed. Support changes are a separate view, not a method gain.

This tests an observed scale-aggregation loss without granting new physical
identity authority. The W3 context audit does not establish an identity cue;
W1 partial-positive, glare/structure and identical-observable constraints still
apply to any future identity challenger. Pairwise order can cycle and is never
used as a candidate ranking, identity classification, scalar Y, tracklet admission
or phase decision. Existing prediction/evaluator ownership is unchanged. This
bounded W4 sub-experiment does not complete W4 identity work or open W5/O3.

## W4 ordered spatial context — measurement prototype

### Hypothesis and selected scope

Test **ordered full-height appearance within each exact source-X strip** as one
new observable. A finite four-band witness can miss a second remote transition;
pooling or rescoring its existing values cannot recover that missing information.
This is a measurement hypothesis, not a claim that private idx11/idx15 has such a
return, or that a bounded stripe is always a reflection. A wide structural step
and a stationary Oil boundary can be identical; Oil plus a lower reflection can
also have the same profile as a bounded artifact. Neither sustained appearance
nor a return grants identity or NON_INTERFACE authority.

Only spatial sampling extent/order changes. Original candidate geometry, raw-gray
units, masks, labels, O1 packets and v1 scores remain fixed. No temporal bootstrap,
new template, inferred layer identity, source/Y prior, score fusion or fitted
threshold is introduced. W5 association remains behind O2 acceptance.

### Ownership and representation

`tests/diagnostics/s11_spatial_context_probe.py::measure_context` is an isolated,
label-free raster measurement prototype. It reuses `row_features.masked_row_mean`
for arithmetic. A separate diagnostic module is justified because the existing
target audit projects serialized packet/trace fields and owns no image inputs;
adding a wider profile there cannot manufacture absent pixels. Production
`oil_phase_topology.dark_border_cap_conflict`, material-row context, template
matching and `temporal_raster_evidence` remain unchanged. Their boolean caps,
material profiles or motion residuals are not substitutes for this ordered
candidate-strip observation.

Input is uint8 raw gray, explicitly supplied effective/glare masks, integer source
crop origin and exact candidate index/basis/X interval/source Y points. No supplied
point is clipped or replaced by another basis. Reuse one profile for a shared X
interval while retaining every candidate reference. Record every source row's
visible/effective/glare-excluded counts, mean in 0..255 units and row state. A zero
mean with visible support is distinct from missing. Restore empty-row means to
null rather than the arithmetic helper's numeric zero. Do not interpolate across
mask/glare gaps or infer continuation beyond crop/mask support. Counts of one are
measured support, not a declaration of sufficient classifier coverage.

Keep source-row order; do not collapse to another scalar median/histogram. The
prototype still averages horizontally within a strip and is therefore **not** a
full 2-D region-adjacency representation. Horizontal permutation can collide.
`extent_censored=true` explicitly limits observed persistence to the supplied
crop, never the vessel or an unobserved region. Cap inputs at 4096 pixels per axis
and 512 supplied points; these are diagnostic resource limits, not semantic
thresholds. Oversized/invalid inventories fail, never silently drop points.

Output spec `ordered-full-height-strip-context-v1` always has decision
`NOT_EVALUATED`. This is not shadow prediction v2, a total candidate score,
UNRESOLVED classifier output, numeric localization or a production integration.
No artifact is accepted simply because its arrays serialize or synthetic fixtures
differ. The array measurement is used by the read-only source adapter below.

Candidate-relative context is a view of this same shared profile using offsets
from the retained source Y, not a new independent observation or identity owner.
Assess novelty against the entire O1 candidate inventory, including local peak
fields: another candidate can sample a remote feature, and a row outside all
bands can still affect O1's gradient search. A classifier must justify physical
meaning separately from new array detail or sampling extent. Nearest/strongest
peak, brightness return or sustained appearance alone does not grant identity.
The [local feasibility evidence](../60-evidence/s11/s11-o2-spatial-context-feasibility-local.md)
records controls for these boundaries. No profile identity score or production
integration is defined by this measurement contract.

### Real-data entry before any efficacy claim

`tests/diagnostics/s11_spatial_context_run.py` uses the original two source frames already reviewed,
not screenshots/guide annotations or a new video interval. Reuse existing bundle
link verification, indexed packet verification, video reader, recipe mask builder
and preprocessing; expose the exact image/geometry/mask provenance and preserve
all input hashes. Bound to the original reviewed candidate inventory, keep each
basis separate, and use no class labels to choose pixels or profile extent.
Record source video hash, frame/Glass identity, crop origin, decoded raster/mask
hashes, source recipe/settings and code/spec fingerprints. No detector proposal
or resolver rerun is needed. If the decode/mask association cannot be established,
stop that image comparison rather than treating a manually drawn guide as data.

The CLI takes one or two v2 regression label files (one frame each), expected
revisions, the original bundle and original video. Each review's existing sibling
`bundle-link.json` is mandatory. Verify its fingerprint, all five original bundle
file hashes, packet hashes, indexed witness equality, exact scene/frame/Glass and
recipe geometry, and original source-video bytes. Explicit paths relocate reads
without editing links. No fallback to filenames, PNG guides or nearby frames exists.
The existing video reader may advance at most 120 frames from an earlier seek;
only the exact backend-reported frame index is accepted. Overshoot/nonsequential
advance fails. This is source-byte/index association, not a historical decoded
pixel equality proof; source PNG and actual timestamp/raster hashes are retained.

Reuse `build_mask_bundle` and `preprocess` with snapshot Glass settings. Verify
witness crop origin and size. These are reconstructed masks under the recorded
recipe/current code; no stored mask is silently assumed identical. Retain every
existing candidate's candidate-center/native-path point without identity-based
selection, bounded to 512 points (increased from the 128-point array prototype to
cover both bases in the supplied inventories). No proposal/resolver is rerun.

The adapter also reuses the original diagnostic band arithmetic for an explicit
baseline check of available/count/gray mean/gray std/glare fraction. It preserves
original bands and flags mismatches; 1e-10 absolute tolerance applies only to float
arithmetic in 0..1 gray units. `MATCH` is limited to these measured fields. A
`DIFFERENT` baseline forbids attributing changes to sampling extent alone and
requires reconstruction investigation before any information-gain conclusion.

A new output directory contains JSON, automatic summary, raw source/crop/gray and
mask PNGs, and per-X SVG plots with exact candidate markers and unconnected null
gaps. Plots are inspection aids; JSON owns numbers. Input before/after checks cover
labels, packets, links, bundle files and video. `complete.json` is written last,
with hashes of every output and an artifact hash of the spec/direct code owners.
Existing output directories and outputs within bundle/review directories fail.
Execution completion does not assert identity success, O2 acceptance or field PASS.

Inspect whether remote transitions visible in raw images are actually retained
by the profiles, using the unchanged local witness as the representation baseline.
Keep mask/crop censoring and the human-ambiguous idx0/idx20 pair explicit. Do not
report a near/off ranking gain, relabel unknown physics or select thresholds from
this inspection. If the added context is absent, masked, or shared by opposing
physical candidates, close the hypothesis without promotion; do not keep adding
descriptors to fit the same failures. Identity classification and independent
acceptance remain separate work after this information question is answered.

## W4 ordered column-side context — local prototype

The same diagnostic module exposes `measure_lateral_context` to investigate
horizontal arrangement at fixed supplied candidate/native geometry. It reuses
`measure_context` validation/row observations and masked_row_mean on transposed
patches; no path generator, gradient operator or connected-region owner is copied.
The caller supplies one integer band width b (1–128); O1 half-up center c selects
near_above [c-b-1,c-1) and near_below [c+2,c+b+2). The function retains ascending
source-X columns with each side's means/counts and below-minus-above differences,
plus exact requested/clipped local/source ranges and crop-completeness flags.
It does not interpolate the native sector points into a per-pixel contour.

Raw means use 0..255 units. Missing means/deltas are null; observed black is zero.
Partial crop windows and one-pixel counts remain explicit, not declared sufficient.
The original raster/point bounds apply plus 65,536 total point-columns. The spec
`ordered-column-side-context-v1` is local and NOT_EVALUATED with no score or
threshold. The old source CLI remains a row-context runner and does not invoke
this function. Historical outputs are preserved even though current code hashes
change. No private rerun is required for this array-level contract.

This retains some horizontal side appearance, not full two-dimensional topology:
within-band vertical order is lost, and different images can have identical row
and side-column marginals together. No physical class or connected region is
inferred. [Local evidence](../60-evidence/s11/s11-o2-lateral-context-prototype-local.md)
records actual O1 collision controls and the remaining joint-marginal collision.
A future joint pixel/edge relation must be distinguished from existing paths and
aggregate measurements before a classifier or private rollout is proposed.

## W4 unpooled O1 spatial context — stored-output adapter

The next bounded hypothesis is that a candidate's transition arrangement across
X may be inspectable before marginal pooling: a laterally extending transition,
a broken highlight and a terminal structure can differ in two-dimensional shape.
These are appearance hypotheses, not class definitions. Structure/reflection can
also produce coherent boundaries, and the human idx0/idx20 ambiguity is retained.

`measure_joint_context` in the existing spatial probe reuses O1
`oil_interface_witness._extra_channels` without changing it. It preserves the
existing gradient magnitude and absolute vertical derivative at every crop pixel,
plus the existing five-pixel visible-stencil validity mask. It does not run Canny,
select a path, threshold an edge, connect components or infer region ownership.
The unused Canny channel is supplied zeros and discarded. Gradients use gray/255;
central differences have magnitude at most sqrt(0.5) and vertical magnitude at
most 0.5. Stencils can cross a supplied X-strip boundary, exactly as in O1, but
never cross crop/mask/glare invalidity. Invalid storage zeros require the separate
validity array; valid zero is a different state. Raw pixels remain the comparison
owner because derivative polarity and central-difference aliases remain lost.

This is an unpooled view of existing pixels and O1 arithmetic, not an independent
sensor or proof of packet-wide novelty. The known joint row/column marginal
collision is distinguished, but identical pixels and checkerboard/polarity aliases
are explicit counter-controls. No numeric localization or identity score follows.

`tests/diagnostics/s11_joint_context_run.py` is a separate stored-artifact adapter:
the original source runner owns video decoding, bundle/recipe reconstruction and
label binding; this adapter consumes its immutable output without reopening those
inputs. It verifies the original COMPLETE schema, every listed output hash, the
caller-pinned source artifact and its fingerprint, PNG byte/raw-raster identities,
frame/Glass/crop/point bindings, exact recomputed row context and baseline bands.
A baseline other than MATCH stops this comparison. It uses no case-specific
selection, source family rule or historical label to choose pixels. One or two
cases, existing 4096-axis/512-point bounds, 128 files and 512 MiB total source
outputs bound the read. It never substitutes a nearby frame or inferred path.

New outputs are a numeric NPZ per case, fixed-scale PNG previews, experiment JSON,
a compact automatic summary and an offline HTML viewer. Exact witness bands are
linked by candidate index + basis + X + source Y; each requested/clipped interval,
reason and availability remains separate. When O1 deduplicates an exactly coincident
candidate/native center, candidate-center references explicitly name the recorded
native role and `coincident_recorded_native_center` binding. Different Y values
and missing native roles never use this alias. The viewer overlays those bands and the
supplied point, not an inferred contour. NPZ float arrays own numbers, previews
are quantized. Source files are checked again before a new COMPLETE receipt is
written last; overwrites and output nested in the source experiment are rejected.
The input receipt covers stored outputs only, not fresh hashes of the original
video/bundle/labels. No historical decoded-pixel equality is asserted.

Windows may run this adapter on the existing two-frame spatial-context output
and inspect the bounded targets in the [procedure](../40-operations/s11-o2-local-shadow-evaluation.md#unpooled-o1-spatial-context--existing-saved-outputs).
The next decision is whether unpooled arrangement offers a specific observable
worth testing as a future hypothesis, remains shared/ambiguous, or is censored.
No automatic transition to classifier fitting, new collection, relabeling or
production change is authorized by a COMPLETE result. [Local evidence](../60-evidence/s11/s11-o2-joint-context-local.md)
records this adapter's verified scope.

## W4 recorded-band color sides — saved-output measurement

The candidate-guided human rationale motivates one question: do visible side
color differences exist in the retained RGB crop that the numeric gray projection
does not retain? Apparent transparency in the human account is not calibrated
transmission. This diagnostic measures code-value color differences, not Oil
identity, physical transparency, region ownership or contour continuity.

Extend the existing `s11_joint_context_run.py` adapter with `--color-side` and
`measure_color_side` in `s11_spatial_context_probe.py`. Reuse its spatial-source
receipt/hash, raw PNG identity, exact point/center binding, baseline reconstruction
and input-preservation gates. The source is the original spatial-context output,
which retains BGR crop, raw gray, effective and glare masks. Joint output or
annotated guide PNGs cannot substitute for that source. No new decoder, detector,
label reader, gradient map or viewer is introduced. Existing default joint mode
retains its contract. Production runtime and O1 trace schema are unchanged.

`recorded-band-color-side-v1` fixes these semantics before private execution:

- Use all saved candidate/geometry/X/Y points and every recorded width; no
  identity label, source family, reviewed coordinate or magnitude chooses samples.
  Preserve candidate-center/native roles and exact coincident aliases separately.
- Require uint8 BGR crop and exact OpenCV BGR-to-gray equality with saved gray.
  Use B/G/R and saved gray code values in 0..255, float64 arithmetic. This differs
  from O1 normalized gray units; no gamma, white-balance or radiometric calibration
  is claimed. The source masks already have their recorded color-dependent bias.
- Use each recorded band's half-open requested/clipped local interval and exact
  source X. Validate clipping, preserve clipped source Y and existing availability
  and reason. Every channel uses the same `effective & ~glare` pixels; count must
  equal the recorded O1 visible count. This is pixel validity, not gradient-stencil
  validity. Never bridge gaps or fill an unavailable band.
- Within each band, retain visible counts per ordered X column and an observed
  all-visible-pixel B/G/R/gray mean (null if empty). Partial observations of an
  O1-unavailable band remain diagnostic and cannot enable a pair delta.
- For near and far independently, subtract above from below per X column. Require
  both O1 bands available and at least one visible pixel on each side of that
  column. Retain every column delta or null, paired-column count and full width.
  Average deltas with equal column weight over those paired columns only. This
  is deliberately different from subtracting pixel-weighted band averages.
- Report `delta_B`, `delta_G`, `delta_R`, `delta_gray`, and fixed opponent changes
  `delta_B-delta_G`, `delta_R-delta_G`. These are descriptive vectors, not a score,
  norm, ranking or threshold. An achromatic step has zero opponent change, but
  color illumination/reflection can also change these values. Identical pixels
  cannot establish different physical identities. Zero is observed zero; null
  is unavailable. Status is `observed`, `o1_unavailable` or `no_paired_columns`.
- Retain existing raster/point/input limits and additionally cap measured band
  columns at 1,000,000 and sampled pixels at 100,000,000 per case. Ordered columns
  still average vertical structure within bands; no independence across widths,
  overlapping points or candidate-center/native aliases is asserted.

The mode emits `s11-o2-color-side-v1`: experiment JSON (full column support and
numbers), machine-generated CSV (one row per point/width/near-or-far pair), summary
and COMPLETE receipt. Three outputs are hashed; COMPLETE is written last after
input-preservation recheck. No existing output is overwritten. All flags remain
EXPLORATORY_UNCALIBRATED / NOT_EVALUATED / FIELD FAIL / NOT_MEASURED with no
production decision or auto-acceptance. A successful run establishes measurement
execution only. The [Windows procedure](../40-operations/s11-o2-local-shadow-evaluation.md#color-side-measurement--existing-saved-outputs)
uses the retained controls; it does not reopen R1 or grant W4-R2 entry.

## W4 candidate-conditioned region competition — prototype contract

Status: **IMPLEMENTED as a frozen offline appearance prototype; NOT ACCEPTED as an identity challenger**. The completed
[color-side assessment](../60-evidence/s11/s11-o2-color-side-local.md#added-information-assessment-and-measurement-disposition--2026-10-06)
does not justify a chromatic magnitude/sign rule. This proposal names one
testable alternative: a candidate's stored geometry should explain a persistent
two-sided region arrangement better than a smooth field or a bounded internal
ribbon, while retaining structural/optical competing explanations. This is a
hypothesis about candidate-conditioned appearance, not a sufficient physical
identity law. A reflected or structural step can remain indistinguishable.

### Distinct observable and reuse boundary

The observable is **joint X/Y chromatic arrangement relative to the
stored candidate path**, including within-side adjacency and alternative region
boundaries. It is not a new sensor or an independent vote. Existing owners:

| Existing owner | Reuse / limitation |
|---|---|
| `s11_shadow_experiment.profile_scale` | Existing four-mean step/ramp/excursion comparison; do not rename or recolor this scalar model and call it region reasoning |
| `s11_spatial_context_probe.measure_context`, `measure_lateral_context`, `measure_color_side` | Reuse geometry/availability semantics; row/column/band means lose some joint pixel arrangement, including vertical order inside color bands |
| `measure_joint_context` | Reuse the prior spatial-information boundary; its unpooled gray gradients are not unpooled RGB or physical region identity |
| `oil_material_path.material_layer_context` / `_terminal_material_partition` | Existing raw material opposition/row-profile partition support; neither a structure label nor an independent color reference |
| `s11_joint_context_run` | Existing receipt/raster/geometry loader and exact aliases; any eventual saved-output entry extends this owner, never reopens video or introduces another loader |
| W3 `s11_interface_shadow_evaluation` | Existing identity/local/scalar targets and abstention/coverage accounting; use only after a real frozen prediction contract exists |

The color-side full-output collision control shows that coherent horizontal
chromatic runs and a staggered arrangement can share every emitted band mean,
ordered column delta and support value, even with identical full gray pixels.
Therefore neither `color-side.csv` nor even its complete numeric JSON suffices
to reconstruct this observable. Saved unannotated BGR crop and masks are the
potential input; no additional source image acquisition is inferred to be needed.
The test proves a representation limit, not that either synthetic raster is Oil.

### Candidate-conditioned evidence contract

1. **Inputs:** original saved crop/gray/effective/glare arrays, recorded candidate
   index and exact geometry, all widths and availability. No identity/path label,
   Glass name, frame number, truth coordinate or production selected/rejected
   bit enters inference. Candidate/frame identity remains provenance only.
2. **Support:** separate each `(candidate, basis, exact X, source Y, BW)` view.
   The patch is the clipped envelope of its four recorded
   bands, with the same effective/non-glare mask. This deliberately exposes
   unsampled rows between those bands, including the center gap; it is new
   diagnostic support within saved pixels and must be declared as such.
   It does not revise O1 availability. Mark original-band pixels versus added
   envelope pixels, and compare envelope support against original-band-only
   support in a separate ablation. Do not credit support expansion to color.
3. **Geometry:** use recorded native sector Y, never the strongest new edge or
   a human line. A center-only candidate is a horizontal hypothesis with that
   limitation. Sector pieces are not an interpolated contour. No adjacency is
   asserted across missing pixels, non-touching patches or discontinuous sector
   endpoints; retain disconnected evidence and censored extent explicitly.
4. **Competing explanations:** retain three appearance hypotheses: smooth field
   without a candidate boundary; two sides separated at the recorded geometry;
   a bounded stripe/ribbon whose return lies inside visible support. Compare
   within-side variation/adjacency and cross-boundary changes on exactly the
   same pixels. A coherent two-sided appearance is only partition evidence.
   A missing return outside the envelope is censored, not a persistent-region
   success. Neither a ribbon nor a smooth field automatically proves non-Oil:
   a true interface can be overlapped by glare or weakly visible.
5. **Opposition:** preserve recorded material/static/template/glare facts with
   exact provenance as possible explanations when available. This prototype reads the spatial saved-output contract only; material/static/template opposition is explicitly `not_measured`, not absent or favorable. Template match, static overlap,
   low support and distance from another candidate are not automatic negative
   truth. `not_measured`, contradicted and observed-clear must remain distinct.
   A structural step or reflection that explains the same pixels leaves physical
   identity unresolved unless independently justified evidence separates it.
6. **Candidate aggregation:** return a geometry-indexed explanation ledger of
   support, opposition, censoring and unresolved alternatives, preserving every
   sector/width and overlap lineage. Do not choose max/median/majority support as
   holistic identity, count overlapping scales as independent confirmations, or
   demand that every point of a holistic positive be near-interface. No scalar
   Y or temporal association is produced by this proposal.

### Frozen v1 model and implementation boundary

`tests/diagnostics/s11_region_competition.py` owns the bounded raw-pixel model;
`s11_joint_context_run.py --region-competition` extends the existing loader,
receipt, exact geometry/band aliases and input-preservation owner. The separate
module isolates least-squares/adjacency logic from raster extraction; it does
not introduce another acquisition path. Existing O1, color-side and production
code remain the input/behavior owners.

For each exact point/width/support view, fit these fixed models per channel:

- `smooth`: intercept plus normalized X and normalized Y (3 coefficients).
- `partition`: the same plane plus `1[Y >= recorded source_y]` (4 coefficients).
- `ribbon_bw`: the same plane plus `1[abs(Y-source_y) < BW]` (4 coefficients).
- `ribbon_2bw`: the same plane plus `1[abs(Y-source_y) < 2*BW]` (4 coefficients).

X is `(local_x - envelope_x_min) / max(1, envelope_x_max-envelope_x_min)`;
Y is `(local_y - source_y + origin_y) / max(1, envelope_y_max-envelope_y_min)`.
These denominators use geometric pixel extrema, never observed intensity.
Pixel channels are divided by 255. Least squares uses float64, `rcond=1e-10`,
no regularization, no clipping of fitted values and no fitted ribbon width or
center search. Fit columns whose **crop-local X modulo 4 is nonzero**; evaluate
on columns with modulo 4 zero. Held-out here means a spatial computation split,
**not independent calibration/holdout recordings**. Report coefficients, rank,
training and held-out mean squared residuals averaged over pixels **and**
channels. Smooth has lower capacity; no penalized score or winning model is
selected. Errors across gray/BGR are different channel-space losses and are not
by themselves a color-benefit statistic.

Horizontal and vertical squared color differences use only immediate visible
neighbours on the same side of the recorded candidate. Keep pair counts;
missing pairs yield null. Original-band gaps, masks, glare and sector edges are
never bridged by adjacency. A plane fit over separated samples asserts no
physical connectivity. Also report observed vertical indicator-edge pair counts
for each partition/ribbon; a small ribbon residual without both visible return
edges is not an observed return. Within-side adjacency exposes the equal-gray,
full-color-output collision that the older four-mean model cannot represent.

All four O1 bands must be available for a width's model fits. Envelope pixels
cannot rescue an unavailable O1 view. Preserve its support/adjacency diagnostics,
but null all model errors/coefficients with `o1_unavailable`. Fewer than 8 train
or 4 test pixels yields `insufficient_split_support`; deficient design rank
nulls that model and marks the view `incomplete_model_support`. Do not recast
these states as negative identity. Identical native/center aliases are retained
with binding provenance, never counted as independent evidence.

Limits: reuse raster <=4096 per dimension, <=512 points and <=3 widths <=128;
preflight <=262,144 pixels per clipped envelope and <=50,000,000 summed envelope
pixels per case before any fit. No retained per-pixel model arrays, learned
parameters, candidate aggregation, identity threshold or temporal output.
Every view records `physical_identity=UNRESOLVED`; this is an explicit limit of
an appearance model, not successful physical abstention/coverage performance.
Finite windows remain censored regardless of which residual is smallest.

### Comparator, falsification and entry decision

Use a factorial comparison to keep two changes separate:

| Support / representation | Gray-only | Gray plus chromatic channels |
|---|---|---|
| Recorded bands only | Same-pixel, same-weight gray baseline | Same bands/weights with BGR retained |
| Declared candidate envelope | Raw 2-D gray region model | Identical model/support with joint BGR arrangement |

The color ablation must have identical preprocessing, pixel weights, candidate
geometry and model-complexity policy. It cannot gain merely by adding more
summed channels. Achromatic data must not get an artificial advantage or penalty
from triplicating gray. Model choices/parameters are fixed on development
controls, never selected from the returned private signs. A two-dimensional
model that only distinguishes these scenes through gray is spatial-model
evidence, not added color efficacy.

Before Windows entry, apply the [region-competition controls](../30-validation/s11-interface-observability-witness-validation.md#candidate-conditioned-region-competition-controls).
Reject a proposed implementation if its distinction collapses to the old profile,
depends on hidden pixels/truth/source family, mistakes a mask edge for physical
termination, or certifies identical supplied observables with opposite identities.
Failure to find one frozen model that passes the paired controls is a reason to
stop this proposal locally, not run another private descriptor sweep.

The current reviewed Accum pair, censored BASE negative and unresolved BASE pair
remain development/regression controls; they have not become new independent
calibration/holdout examples. The bounded Windows saved-output procedure is now ready after local controls.
No human labeling, detector rerun or acceptance transition is requested.

## A1 support, signed pair and score-coordinate lineage

The additive `artifacts.state.oil_measurement_lineage` namespace uses schema
`oil-measurement-lineage-v1`. Existing witness/diagnostic schemas and detector/
resolver identities remain unchanged. It is diagnostic-only and NOT_EVALUATED.
The second audit's paired scorer remains rejected; no new field supplies an
Oil score, authority, physical identity, scalar, or resolver input.

`phase_candidate_assembler` captures immutable per-index/source/Y JSON bindings
on its existing frame-local diagnostic sidecar. `PhaseDebugProjector` checks the
exact join after calibration and serializes it. Duplicate source/Y candidates
remain separate by input index; stale source/Y and bool/nonintegral indices fail.
No ndarray, mutable input alias, new temporal state or new output writer is added.
NONE bypasses this work. Existing Basic/Full trace and atomic bundle owners persist it.

The measurement owner is extended in place: `oil_pipeline_diagnostics` invokes
existing pure spatial extraction/semantic functions, with optional diagnostic
sinks at the actual broad, narrow and semantic operations. It does **not** rerun
an Oil temporal owner, Foam, authority or resolver. The primary or relative
spatial-fallback hypothesis is joined by exact ID/Y and all three semantic
scores before attaching the reproduced lineage; an unmatched ID or differing
coordinate/score is explicitly unavailable. This bounded spatial reproduction
keeps diagnostic data outside the sealed canonical outcome/temporal command
contract. It costs extra debug work and must be measured. It is not an alternative
classifier or a new implementation of the production score equations.

The three finite additions are:

- Phase scan support: reuse the production pooling operation in
  `oil_supplemental_path` at the selected normalized-raster row, radii 3/6/10 and
  five sectors. Retain upper/lower counts, actual mean X, exact common-X runs,
  pooled difference and complete-column paired mean/median difference. Common X
  requires visible support on both sides; paired X requires all radius samples
  on both sides. Paired availability means at least one complete column; it
  does not apply the production pooling minimum floor. This measurable support
  is diagnostic, not production usability, and is never substituted into production. Crop clipping and insufficient/no-common
  support have separate reasons and null measurements. X runs are half-open
  source-coordinate sets; storage is bounded by crop width, not a fitted span.
- Narrow pair: retain the selected center/partner source Y, signed masked Sobel
  values, validity, same/opposite/zero/unknown relationship, absolute energy,
  legacy pair strength/symmetry and lobe order. Production selects by absolute
  strength/separation/row, without a sign/validity filter. Preserve that result,
  including cases where its selected partner is diagnostically unavailable.
- Score/scalar lineage: retain raw member coordinates/polarity, proposal center,
  sampled broad rows before clipping, broad transition, narrow center/partner,
  scalar Y and actual computed score nodes. Preserve all merged members, primary
  feature owner and mean/max/median merge rules. The dependency graph explicitly
  shares pulse between boundary, structural and plateau terms; these are not
  independent votes. The selected candidate final score may be temporal confidence
  while its feature score remains boundary likelihood. Non-hypothesis/non-phase
  families retain existing diagnostics and explicitly report different-family
  applicability rather than borrowing another candidate's measurements.

Channel lineage is explicit: `canonical_absolute_broad` reads `pre.blurred`
with canonical /255 scaling, while `spatial_relative_broad` uses its existing
relative normalization. Plateau terms read `pre.gray`; narrow values are masked
Sobel /255, and phase support reads `pre.normalized` as float32. These channels
are not interchangeable measures of physical identity.

Storage remains frame-local: at most the existing 12 proposals per spatial route,
10 retained semantic hypotheses per route, 8 raw members per proposal, and existing
candidate budgets. Phase bands add 15 records per retained phase-scan candidate;
exact X support has at most crop-width runs per record. No history or new search
radius is retained. Resource measurements and full equality precede adoption.

## A2 ordered-patch temporal correspondence — bounded diagnostic

Status: frozen diagnostic hypothesis, not an Oil identity classifier. The human
review confirms one actual Oil boundary from 42.5 to 44 s with rapid height
changes; it supplies no intermediate coordinates or speed bound.

Reuse `s11_boundary_temporal_probe` as the offline temporal measurement owner.
Its prior `measure_pair` measures fixed-coordinate registered gray residuals and
cannot recover displaced candidate patterns. `match_ordered_patch` adds exactly
one different observable: the full ordered BGR pattern across both sides of a
recorded candidate, compared at every fully contained integer Y in the same X
strip. Per-channel patch-mean centering removes additive exposure offsets;
normalized squared error retains pixel order. Every loss and all exact ties
(absolute tolerance 1e-12) are retained. No speed penalty, Y-distance cutoff,
polarity gate, source-family preference or motion-to-identity conversion exists.

Freeze the sample4 experiment before inspecting results:

- Use the saved raw 40–45 s context PNGs and the prior recorded five sector X
  intervals. Keep every recorded center/native-path view separately, including
  coincident-center deduplication already performed by the witness; never invent
  missing sectors. Restrict the search to the original 104×104 detector ROI.
- Use the base recorded BW=3 and radius `3*BW+1` (21-row envelope), including
  the previously unsampled center gap. This is expanded raw appearance support,
  not unchanged O1 band support. Glare/material/camera validity is unmeasured;
  no old mask is propagated to a new frame or used as identity evidence.
- Starting templates are the previously reviewed candidates at 40/42/42.5/44 s,
  including the three wrong selections. Y is only the diagnostic anchor query,
  never an intermediate truth or a production input. Retain each sector rather
  than pooling a strongest/median sector into a physical contour.
- Compare sequential next-frame and 15-frame (0.5 s) correspondence over the
  same bounded interval and endpoints. Update a patch only at a unique minimum;
  exact ties or unavailable full support end that sector chain. Compute the
  reverse match for every link and retain the entire reverse alternatives.
  Reciprocal mismatch is reported; it is not silently removed or rescued.
- The chain is an appearance hypothesis, including when seeded at a reviewed
  Oil candidate. It never publishes a coordinate, transfers physical labels,
  creates a same-frame detector candidate or bypasses authority.
- Compare endpoint behavior, reciprocal disagreement, exact ties and divergence
  between cadences. A correct endpoint alone cannot validate intermediate rows.
  Wrong-target controls can remain excellent appearance matches.

The operating policy is measurement-only: `NOT_EVALUATED` identity decisions and
`UNRESOLVED` physical identity for all matches. W3 is reused only after there is a
justified frozen identity prediction contract; this diagnostic does not fabricate
one to obtain an efficacy score. Do not tune widths, weights, thresholds or
cadences after looking at these exposed controls. A failed match closes this
specific correspondence hypothesis; it does not reopen the residual experiment.

## A2 temporal region exchange — design preflight

Status: **FROZEN FOR ONE EXPLORATORY REGRESSION COMPARISON**.
The user identifies A as fluid containing foam/bubbles and B as less-bubbly
liquid in the two displayed f1275/f1320 scenes. This closes the interpretation
question; it supplies neither uniform masks nor chemistry/scalar/path truth.
Both sides can contain fluid. Brightness alone cannot certify the product target.

`tests/diagnostics/s11_temporal_region_readout.py` owns
`joint-temporal-region-exchange-v1`. Unlike the closed ordered-patch search, it
compares joint image-formation models at the original candidate location. It
reuses the prepared 21 exact BGR rasters and per-frame effective/nonglare masks.
No production imports or runtime consumers are introduced. The earlier static
region competition cannot express two-frame region replacement; the ordered
patch matcher cannot compare its appearance match against these nuisance models.

The frozen input is each recorded sector's full-height X strip, anchor plus
immediate native neighbours (-1/+1 frames). Pairwise common valid pixels are used
by every model. Native geometry is used when any native view exists; otherwise
recorded candidate-center views are used. Missing sectors are never invented.
The current cut stays at the recorded source Y, including fractional coordinates;
only the neighbour cut searches integer 1 through height-1. No speed, polarity,
family, track, rejection, label or private-coordinate prior enters inference.

All models share a normalized X/Y affine plane and temporal exposure offset,
fit to raw BGR/255 with float64 least squares. Competitors are smooth, temporal
illumination plane (T*X, T*Y), stationary step, moving step, and moving finite
ribbons of half-width 3 and 6 pixels. Crop-local X modulo 4 equal to zero is
reserved for pixel validation; other columns fit. This computational split is
**not** an independent recording holdout. Each search chooses its training-error
minimum, retains every error and exact tie (absolute tolerance 1e-12), and only
then compares validation error. Image coefficients are nuisance fits, not label
training; `fit_partitions=[]`, `EXPLORATORY_UNCALIBRATED`.

A pair supports the hypothesis only if the moving step has a unique uncensored
minimum and lower validation MSE than every competitor by more than 1e-12.
Every competitor must be measurable; both ribbon returns must be inside the
raster and visible through common masks. Rank deficiency, insufficient pixels,
ties, clipping or competing explanations abstain. Minimum per-frame support is
8 training and 4 validation pixels; rasters are bounded at 256 by 256.
A candidate requires both pairs in all five distinct recorded sectors. This is
a conservative conjunction, not majority/max pooling or independent votes.
Partial native paths therefore remain unresolved even if one strip supports them.

`INTERFACE_SUPPORTED` is a falsifiable, uncalibrated **target-support hypothesis**
for W3 comparison, not established physical identity or an uppermost-target
selector. Shared optical causes and unmodelled texture can still imitate a
moving partition. Raw recorded optical/texture opposition and missingness are
retained separately without counting correlated derivations as new votes.
There are no negative predictions, new coordinates or candidate selection.
Scalar is always `NOT_EVALUATED` with original candidate Y and no path truth.
The +1 input introduces future-frame dependence; this is offline evidence only.

Freeze this code and operating point before inspecting real model results.
Evaluate all 153 original candidates through existing W3, preserving all seven
confirmed targets, three explicitly wrong targets and 143 unreviewed candidates.
Load truth only after inference. Report positive losses, wrong supports and
abstention together. A failure closes this fixed proposal without threshold or
sector-policy tuning on these exposed cases. A pass would still leave independent
O2 identity and Windows field acceptance open. `FIELD FAIL` is unchanged.

## D2 boundary-role design entry

The [D1 closeout](../60-evidence/s11/2026-10-08-next-work-intake.md#d1-saved-record-reconciliation--closed)
locates recorded exclusions, not a new physical discriminator. H-ROLE remains a
design question; no model, operating point or production route is selected here.
The immediate question is whether a target-bound positive and a relevant
non-target have candidate-local support/opposition that justifies a **distinct**
mechanism after the closed appearance and temporal experiments.

### Fixed control matrix and input separation

| Input / existing owner | Preserved role in D2 | What it cannot establish |
|---|---|---|
| Windows passive target snapshot: Accum drain f17383, target idx4/13/17/24; internal idx5/10/18; other 19 | First bounded design contrast: uppermost target versus a real lower boundary and existing non-targets in one frame | No scalar/path truth, optical subtype, per-index individual-review claim or matched optical counter-control is inferred |
| [Reported idx13/native/sector 0 review](../60-evidence/s11/2026-10-08-d2-control-preflight.md#windows-support-review-and-human-reply--bounded-review-closed): X1218–1303/Y315, user describes local shadow/cavity feature distinct from idx10 | Concrete guard against transferring candidate target status to every native measurement | Physical shadow/cavity subtype remains unresolved; no whole-candidate relabel, automatic truth for sectors 1–4, or certified idx12 counter-control |
| Same snapshot: Accum post-Foam f16543 (6 target/22 other); BASE FULL f17383 (21 other) | Retained single-boundary and no-visible-target controls; do not repeat their review | The 75 candidates are not independent scenes or untouched holdout |
| W3 review-003 f16280 idx10/15; review-002 f14386 idx11 | Existing physical-interface/negative rationale and mask-limited structure check | Not an index join to the passive snapshot; physical interface alone is not target/scalar truth |
| W3 review-002 idx0/20 | Preserve the already recorded human ambiguity separately from formal labels | Do not force opposing truth, or let a new score resolve the human uncertainty |
| [Mac A2 bound controls](../60-evidence/s11/2026-10-07-a2-target-binding.md): 7 targets, 3 explicit wrong targets, 143 unreviewed | Local regression and rapid-motion challenge; wrong-target physical identity stays uncertain | No relabeling of all wrong targets as artifacts; no whole-track, source-family or slow-motion shortcut |

The [fixed query manifest](../50-diagnostics/s11/2026-10-08-d2-control-query.json)
pins the existing Windows target artifact, evaluation content, physical-label
hash, first case and complete 26-candidate inventory. These logical pins select
an already bound object; they are not reconstructed raw file hashes. They do not
constitute a frozen classifier or completed D2 model-input manifest. A candidate
key is the bound case/packet/witness/input index, never a naked index or score rank.
Other existing recordings retain their metadata-first partition requirement;
all already exposed Windows/Mac controls here remain regression.

### Reuse and the remaining design condition

Reuse `s11_target_truth.load` through `s11_interface_shadow_evaluation.load_frozen`
for existing snapshot/packet/physical-review verification, `review_geometry` for
exact native/center geometry, and W3 for any later frozen predictions. A narrow
saved-field query belongs in the existing operations procedure; it does not need
a new extractor, review GUI, label store or classifier stub.

The missing condition is **one target/non-target contrast whose candidate-local
distinguishing observation and opposition can be identified on the exact
measured support**. Existing labels already answer identity/target questions;
do not ask those again. The passive batch's role totals do not identify which
of its other 19 drain candidates, if any, supplies this counter-control. Use the
complete existing review provenance and geometry for all 26 before choosing a
pair, so neither nearest Y nor a convenient score silently defines the negative.
If stored support/rationale cannot establish such a contrast, report that exact
missing condition; do not cycle through more scenes or reopen prior rationale.

The [saved-field return](../60-evidence/s11/2026-10-08-d2-control-preflight.md#windows-saved-field-return--query-closed)
preserves that inventory. Role labels, band availability and empty artifact tags
do not establish the distinguishing cue. Candidate-level target truth must not
be broadcast to every native sector: a native segment can differ from its
candidate's canonical Y, and an empty path review leaves local truth unknown.
Keep native and center support separate; neither substitute the center for a
deviating segment nor relabel the whole candidate from segment geometry alone.

For private support inspection, use the already bound JSON and source ROI **on
the Windows security PC**, with existing guides as display aids. The [completed
Windows support-review procedure](../40-operations/s11-o2-local-shadow-evaluation.md#d2--windows-only-support-review)
returns bounded observations/geometry as text; private artifacts remain on Windows.
Mac pixel access is not a design prerequisite. Preserve the same regression case
without repeating the query or expanding recordings. Attribute visual observations
to the Windows reviewer and keep them separate from stored truth and human replies.
Local A2 controls remain useful but cannot establish this Windows input connection.
A later judgment request must show the actual candidate support to the user on
Windows and state precisely what is undecidable; an unavailable local viewing
capability must not become a request to export the image.

### Support-review design disposition

The reported idx13 local feature is a counterexample to **candidate-to-support
truth transfer**, not a demonstrated new identity feature. Keep candidate physical
identity, product target role, local path association and scalar usability
independent. A shadow-or-cavity interpretation is not automatically a formal
`off_interface` judgment: a cavity can itself have a physical boundary. The
reported target-path concern and unresolved physical subtype must both survive.
The unchanged target snapshot supplies no new path/scalar truth.

Reuse W1 review/evaluation owners. `review_geometry` / `geometry_key` bind actual
native/center X/Y; `path_summary` preserves unreviewed points; target projection
intentionally does not transfer physical path truth. No parallel annotation store
or empty classifier is justified. Future scoring must not use the human reply to
mask sector 0, replace it with candidate-center geometry or certify the other four
sectors. A four-of-five rule, native-to-center displacement cutoff or gradient
polarity rule is not a new mechanism supported by this observation.

Idx13/native/sector 0 cannot serve as a clean local target-positive merely because
idx13 is target-bound. Its similar gradient signs to idx12/native/sector 0 do not
establish a target-versus-artifact discriminator or identical features. Retain
idx12 as NOT_ESTABLISHED; further display of that pair alone would not settle the
model-entry condition. The next eligible mechanism must identify an inference-time
distinction between actual target support and its competing local feature, with
exactly bound support/opposition controls. The bounded review may close with this
missing condition; it does not authorize a repeated inventory/review loop.

Before a model freeze, state its distinct observable, formula/model class,
mask/censoring rules, resource bound, operating-point policy and falsification
against this matrix. Keep physical identity, target role, partial-path support
and scalar usability separate. Do not repeat color/region residual ordering,
side-texture margins or standalone appearance matching under a new name.
Expanded pixels and changed model logic require separate comparisons. If an
optical alternative explains the same input, preserve unresolved; abstaining
on every true target is not success. D3 and behavioral O3/O4 gates remain intact.

### Region-connectivity feasibility boundary

The [synthetic feasibility experiment](../60-evidence/s11/2026-10-08-d2-region-connectivity-feasibility.md)
tests global connectivity with exact nominal regions supplied by construction.
It adds a test-only oracle, not a real segmentation or inference owner. Existing
`s11_region_competition._adjacency` remains the immediate-neighbour comparison
owner. Production Foam/artifact connected components do not supply Oil identity.

Four-connected region relations can distinguish patterns with identical row/
column sums and identical local adjacency energy, and can preserve mixed local
support along one candidate. They do not independently certify physical target
identity: a stationary structural partition can provide the same observable as
a fluid partition. A closed feature with its return outside the crop or behind
a mask can also appear as a partition. Unknown support must not be completed to
declare enclosure, and a region touching the viewport is not proven unbounded.

The standalone connectivity-to-identity hypothesis is closed without promotion.
This is not a proof against every conditional spatial or learned classifier:
ambiguous patterns may remain unresolved while other patterns are useful. No
descriptor sweep, learned training, Windows extraction or runtime behavior is
implied by the synthetic result. Any later use of connectivity must state the
additional distinguishing evidence and pass the existing support/identity
controls. Same-observable opposing controls cannot become two confident labels
by exposing truth or fixture names to inference.

### Non-learned contour-contact feasibility question

The [contact-cue preflight](../60-evidence/s11/2026-10-08-d2-contact-observability.md)
asks whether surrounding bubble/texture contours visibly terminate or join at a
candidate boundary, versus crossing its interior. This relationship is a proposed
additional observable, not an implemented identity rule. Existing A2 candidate
truth and qualitative A/B material interpretations do not label such contacts.
The bounded read-only review reuses stored pixels, frozen target bindings and
native/center geometry. Source coordinate references are not contour truth.

No contact extractor or classifier is justified before the relationship can be
attributed on actual support and its opposition stated. A later conditional
proposal must still handle structural contacts, internal interfaces, stationary
targets, missing support and optical superposition; motion or a junction count
alone cannot grant identity. Human confirmation of one contact would permit
measurement design, not candidate-wide truth transfer or O2 acceptance. If the
relationship is shared or unclear, close this cue check without another automatic
review loop. The Work Plan owns the current method scope and user checkpoint.

### Saved-edge contact measurement — fixed v1 preflight

After the [f1320 human reply](../60-evidence/s11/2026-10-08-d2-contact-observability.md#contact-interpretation-received--2026-10-08),
test whether the **existing saved Canny raster** represents the reported contact.
This is an offline representation experiment, not an Oil decision rule. Reuse
captured `preprocessing.canny`, effective/glare masks, W1 native/center geometry
and W3 frozen bindings. No edge threshold, CLAHE, blur, dilation, thinning,
gap completion, scalar relocation, production source or truth file changes.

The new pure diagnostic owner is
`tests/diagnostics/s11_contour_contact_probe.py`: existing region/temporal owners
do not measure local graph arms, so they are not extended into a different
responsibility. It consumes only binary edges and visibility, with no physical
labels, source-family privilege, chosen target or temporal track.

For each observed edge pixel, take its 8-connected component inside a square
patch. Remove the central 3×3 core; each remaining component joining the inner
ring (Chebyshev distance 2) to the patch boundary is an arm. Retain its exact
outer directions. Three separate arms left/right/up yield `upper_contact_shape`;
left/right/down is the mirrored shape; four cardinal arms are a crossing.
Short stubs, corner exits, repeated directions or joined multi-side arms stay
explicitly complex. These names describe raster shape, not physical contact.

Use all three existing witness band widths independently: reference corridor
half-width b, patch radius 2b. A2 has b=3/6/9 and radii 6/12/18. Native geometry
has precedence where present; missing native sectors remain absent. Query exact
source X and distance from the saved Y; retain node coordinates, pattern counts,
requested/in-crop/fully-observed centers at each scale. No best-scale selection,
max/majority rule or candidate score. A patch clipped by the crop or containing
any effective/glare-invalid pixel is unavailable. No-edge and unavailable states
are separate and neither means non-interface. Input preprocessing itself remains
an optical/resolution limitation. Raster bound is 262,144 pixels, at most three
radii in 3..32 and 50 million summed patch pixels per call.

Synthetic controls distinguish upper/lower contact, crossing, plain stationary
boundary, disconnected/gapped strokes, locally reconnecting arms, clipped/masked
support and a same-observable structural T. A clean boundary without bubbles
must not become a physical negative; structural T equality prevents promoting
the marker alone. Coordinate translation, original-input immutability and finite
resource checks accompany these controls.

The local preflight `sample/output/s11-d2-edge-contact-20261008-001/preflight.json`
pins 54 inputs/source files and the runner; its SHA-256 is
`69c2ec764c3618dd5b76bb6e538918012a0c248bdc3756693ffb8fe7318567fe`. It was written before
reading raster measurements. The primary X interval is half-open [566,625).

Freeze source/tests and input pins before the real readout. Use all 153 existing
A2 candidates across seven frames as exposed regression; report seven target,
three wrong-target and 143 unreviewed roles only after measurement. Primary
representation check is the already reviewed f1320 central X566–625 contrast:
does the saved graph retain upper-contact markers near idx9 versus idx21 at each
fixed scale? Other reviewed controls expose missed targets and recurring false
shapes. Counts are correlated edge centers, not independent physical contacts or
confidence. If the graph loses the confirmed contact or yields the same markers
on wrong targets, close this frozen representation without thresholds, geometry
or scale tuning. A favorable representation contrast only permits further
conditional design, not W3 identity predictions, O2 entry or Windows execution.

The [completed saved-edge readout](../60-evidence/s11/2026-10-08-d2-saved-edge-contact.md)
rejects this frozen exact-arm representation without promotion. This does not
reject the human region-level relation or all conditional non-learned mechanisms.

### Ordered-column clearance — fixed v1 preflight

The saved-edge local-arm experiment did not represent the human region-level
contact. The next bounded question is whether **ordered empty runs** above and
below the unchanged candidate preserve its relation to the end of upper texture.
This does not infer a segmented material region or relax the closed T-arm rule.
Initial assistant image inspection sees different spatial relations at the upper
targets and lower wrong-target bands; optical subtypes remain unresolved/tentative.
Prior f1275/f1320 human A/B and target judgments are preserved without extension.

Extend the existing pure saved-edge diagnostic owner
`tests/diagnostics/s11_contour_contact_probe.py` with
`saved-canny-ordered-column-clearance-v1`. The material-path terminal feature
already pools material rows; LBP side histograms and region-fit residuals already
compare sides. None retains the ordered first visible edge per original column.
No new production segmentation, candidate generator or physical authority is added.

For each original sector X column, retain all saved Canny pixels in the reference
band |Y−candidate Y| ≤ b. From just outside each end, scan outward until the first
edge, invalid mask or crop boundary. An edge hit supplies its original source Y,
clear-pixel count and exact distance from the unchanged fractional reference.
A mask/crop stop supplies a censored clear-run lower bound, never a finite edge
distance. An incomplete/hidden reference band is unavailable. Do not skip masked
pixels or connect neighbouring columns; no traced contour is asserted.

Reuse effective/nonglare visibility, native geometry where present (no fallback
for missing native sectors), otherwise center geometry, and b=3/6/9 separately.
No edge recomputation, gap filling, Y snapping, smoothing or scale selection.
Bound rasters to 262,144 pixels and b to 1..32. Preserve every column; summaries
report above/below ordering and median difference only where both edges are found,
with denominators and a separate subset having an edge in the reference band.
Neither positive distance difference nor edge presence is an identity decision.
An optical copy yields the same measurement; a plain true boundary with no other
visible edges remains censored/unknown, never a physical negative.

Synthetic controls precede real readout. Freeze code/tests and the local preflight
`sample/output/s11-d2-column-clearance-20261008-001/preflight.json`, SHA-256
`a619a609f6a11744ed622f4ab556d9c641848a418cdcae1d22bccde0e78125f7`, before numerical measurement.
Use all 153 A2 candidates; join 7 target/3 wrong-target/143 unreviewed roles only
after persisting measurements. Primary comparison remains f1320 X[566,625), idx9
versus idx21. All images are already exposed regression, not blind calibration.
Shared/censored patterns or lost positives forbid cue-only promotion; no threshold,
mask, scale or source-family rescue follows. Temporal/optical opposition and
scalar acceptance remain separate, unmet conditions for any later classifier.

The [ordered-column readout and local shape checkpoint](../60-evidence/s11/2026-10-08-d2-column-clearance.md)
retain spatial contrast and scale-dependent overlap. The subsequent user reply
identifies the local protrusion as a glass-pattern lower semicircle; the existing
static-reference audit exposes its absence from the stored prior. Zero prior is
not optical clearance. Reusing earlier frames requires explicit correspondence
and visibility handling without a threshold decrease, map union or target veto.
No candidate classifier follows from ray ordering or that qualitative reply.

### User-confirmed recipe artifacts — reuse before new inference

The existing recipe workflow is an available source of structural knowledge.
The operator can inspect detector proposals and explicitly register an artifact;
the detector need not rediscover that object's physical category from every frame.
This input is separate from the automatic three-frame static prior. Foam-obscured
preparation frames do not establish a clean structural reference, but also do not
invalidate a separately confirmed, visible setup feature.

Reuse the existing owners: `OpenCvArtifactProposalService` generates candidates,
`RoiEditorDialog` records selected proposals on its private working copy,
`InspectionRecipe` persists `geometry.artifact_templates`, and
`artifact_calibration` owns generic matching. The frame owner checks selected
Oil/Foam and assembled candidates; completed Oil eligibility also consumes the
calibrated-match result. The existing UI and recipe schema are the starting point,
not a request for another registration workflow. Unselected proposals carry no
affirmative fluid/target annotation. The stored point/line/region contains
normalized position, extent and angle, not a sampled curved contour, reference
image, visibility history or reviewed fluid trajectory.

The bounded next comparison uses an explicitly bound registration in a separate
recipe copy, with all other settings fixed. Inspect the existing proposal geometry
against the confirmed structure before registration; a local semicircle reply
does not certify a whole proposed row or rectangle. Preserve original input hashes
and freeze the experimental recipe before reading comparative outcomes. Already
reviewed Mac frames remain exposed regression. Report registration provenance and
candidate matches separately from physical truth and final sequence/report output.

Measure both false-structure suppression and retention of real interfaces away
from, crossing, or stationary at the registered structure, plus obscured/ambiguous
cases. A fixed structure and a fluid interface can occupy the same geometry;
the present hard rejection does not resolve this collision. Do not infer fluid
identity from motion alone or from survival after excluding a competitor. Missing
crossing controls remain an explicit efficacy gap, not automatic permission to
broaden exclusions or relax the matcher. Extend representation or matching only
for a demonstrated limitation of these existing owners, with its own bounded
design and controls. No learned model is included.

User-confirmed per-Glass configuration is an existing generic product input.
It is not a hard-coded Glass/time/Y branch in detector source. Keep configuration
changes visible and comparisons separate from the frozen baseline; do not retune
recipes against holdout outcomes or reinterpret old receipts as registered runs.
The [workflow audit and human reference reply](../60-evidence/s11/2026-10-08-d2-column-clearance.md#reference-reply-and-existing-recipe-workflow)
record the current source and sample inventory. This reuse assessment grants no
new classifier, scalar authority, O2 acceptance or field qualification.

The [bounded existing-workflow comparison](../60-evidence/s11/2026-10-08-d2-recipe-artifact-comparison.md)
shows two distinct limits. A Y844 template derived from the local glass-pattern
vicinity collides with two known targets. A correctly bound Y822 non-target
registration retains all seven reviewed targets at eligibility, yet the complete
sequence loses later target selections after phase/tracklet competition changes.
The positive registration input therefore requires both local collision controls
and downstream target preservation; local rejection counts are insufficient.
Retain existing owners and inspect the saved sequence witnesses before a repair.
Do not restore a known false candidate, add exclusions for each new winner or
treat remaining candidates as physically valid merely because a competitor was
removed. No production registration or matcher change is adopted by this readout.

## History Review

2026-10-08 registered-input comparison: exercised existing setup generation,
explicit UI selection on a copy, unchanged calibrated matching, the complete
analysis pipeline and report presentation. Reviewed F04's changed assignment
competition after pruning, F09's candidate-versus-public distinction and F10's
coincident-position failure. Frozen two-sided controls expose both direct target
veto and later selection loss. The result constrains a future repair without
changing production owners, thresholds, label authority or field disposition.

2026-10-08 recipe-workflow correction: reviewed the existing proposal UI,
normalized artifact persistence, frame checks and completed Oil eligibility,
the earlier structure-context projection and Foam/rim reuse audit, and F04/F09/F10.
Human setup knowledge can reduce an image-only inference burden. The prior
position-calibration collision remains: the same geometry can also contain real
Oil. The next comparison therefore starts from the existing registration workflow
and preserves coincident/stationary/obscured controls. No new production owner,
private coordinate branch, recipe retuning against holdouts or ML is introduced.

2026-10-08 ordered-column preflight: reviewed the frozen local-arm failure,
material-path terminal-row aggregation, side-LBP and temporal-region failures,
and F03/F04/F09/F10. The added observable retains ordered first-edge geometry
with mask/crop censoring, without treating edge absence as material absence.
It does not reuse a failed operating point or change production owners.

2026-10-08 saved-edge contact preflight: the user confirms a local contact relation
and separately hypothesizes glass/low-resolution effects. Reviewed F03/F04/F09/F10,
the failed residual/connectivity/patch proposals, captured Canny preprocessing and
existing W1/W3 geometry/binding owners. This experiment measures ordered local
edge arms, preserving optical aliases and missing support. It never derives
identity from motion, graph contact or a reviewed coordinate. Production logic
and the failure registry remain unchanged.

2026-10-08 contact-cue preflight: reviewed F03/F04 motion/geometry identity
failures, F09 support attribution, F10 retuning, the closed A2 region-exchange
and connectivity experiments, and existing W3 frozen readers. The new action is
only to expose an unannotated local contact relationship for user interpretation
in existing Mac regression pixels. No classifier or label change precedes the
reply, and none of the prior physical/target judgments is reopened. Current
logic and failure registry remain unchanged.

2026-10-08 region-connectivity feasibility: reviewed F03/F04 geometry/motion
authority, F09 missing support and F10 tuning escapes, the existing raw-region
adjacency owner and W1 partial-path/collision controls. Exact synthetic nominal
regions distinguish representation information from physical identity. The
test-only oracle exposes enclosure/censoring and same-observable failures without
an Oil classifier or production route. Standalone connectivity is not promoted;
conditional approaches are not ruled out. Current logic and registry stay intact.

2026-10-08 support-review closeout: the human identifies idx13 sector 0 with a
local shadow/cavity-like feature distinct from idx10; preserve this qualified
interpretation and the fixed candidate role. Existing W1/target-projection source
already separates candidate/path/scalar truth, so no new tool or truth transfer
is needed (F04/F09). Idx12 remains unestablished; equal gradient signs do not
justify a polarity or four-of-five mechanism (F10). D2 model entry remains unmet,
without another automatic Windows request or field/behavior promotion.

2026-10-08 security-PC correction: the user can relay text reports but cannot
export images or ZIPs. The prior transfer prerequisite is withdrawn. Keep the
completed query closed and perform support inspection on Windows with attributed
text returns. F09 requires honest evidence provenance, not direct Mac possession
of the pixels. No new detector mechanism, truth or execution result is claimed.

2026-10-08 D2 return assessment: the saved-field query establishes the reported
26-candidate role/geometry connection, not a discriminator. Preserve mixed
individual/group review and logical/raw hash distinctions (F09). Candidate-level
role does not certify every native segment (F04/F09); empty artifact tags and
distant negatives do not close optical opposition (F10). The initial source/guide
transfer proposal was withdrawn by the security-PC correction above; support
inspection stays on Windows. No new mechanism or executing logic is introduced
and previous failed hypotheses remain closed.

2026-10-08 D2 entry: D1's phase/owner exclusions do not authorize gate relaxation.
Reviewed the completed color/region appearance loop, failed A2 temporal region
exchange and side-texture persistence, and existing target-binding owner. The
new decision is a bounded target-role/support connection before selecting a
mechanism; no new identity algorithm is claimed. F03/F04 prevent motion, owner
and geometry from becoming identity; F09 preserves exact binding and F10 prevents
retuning exposed controls. No executing logic or failure-registry entry changes.

2026-10-07 temporal region exchange: the A/B reply closes the adjacent-region
interpretation gap. One offline two-frame model comparison is frozen before real
inference. F03/F04 guard motion/appearance identity leakage, F09 exact original
candidate binding and missingness, and F10 exposed-case tuning. Unlike previous
static fits and patch matches, competitors share current/adjacent pixels with
explicit static/illumination/ribbon opposition. Residual ordering remains a
falsifiable target hypothesis, never accepted identity by construction.

2026-10-07 ordered-patch diagnostic: reviewed F03/F04 motion and appearance
identity leakage, F09 provenance and F10 private-coordinate/threshold escapes.
The prior Foam residual probe measures change at fixed coordinates, while this
extension searches ordered candidate-side appearance without a displacement
prior. Neither establishes identity. Rapid real motion motivates the cadence
comparison; repeated structures and drift remain explicit counter-controls.


2026-10-07 A2 preparation: explicit wrong-target review can coexist with unknown
physical identity. The target-binding companion now accepts that explicit negative
without rewriting physical truth or inheriting an uncertain group. This corrects
an evaluation representation gap; no classifier, operating point or detector
authority is added. F09 provenance and F10 truth/threshold shortcuts remain guards.

2026-10-07 A1 reuses the existing spatial measurement and frame-local sidecar
owners. Reviewed the second audit's disjoint-X pooling collision, same-sign
Y854 pair, score/scalar coordinate distinction and rejected paired scorer.
Signed opposition and support are retained without changing legacy authority.


2026-10-06 target binding implementation reuses existing packet/label validation,
relocatable locators and W3 metrics. A separate immutable snapshot preserves
physical review while deriving explicitly authorized target roles. It rejects
legacy-prediction reuse and does not infer target path/entity/contour truth.

2026-10-06 target clarification: the user requires the uppermost actual fluid
boundary without mandatory material-species classification. Preserve physical
lower-interface evidence separately from target membership. F04's geometry/alias
identity leakage and F10's private-coordinate shortcut remain prohibited; no
minimum-Y selector or automatic legacy relabeling is introduced.

2026-10-06 implementation: candidate-conditioned region competition is an offline
appearance prototype with fixed planar/partition/ribbon fits, held-out columns
and within-side RGB adjacency. Source discovery reuses the existing four-mean profile, material row
partition, spatial/color probe and saved-output adapter. The equal-gray/full
color-output adjacency collision rejects reconstructing joint RGB arrangement
from reduced summaries. The raw-2D prototype separately tests added
support versus added color and retain optically equivalent structural-step
ambiguity; this is not a new executing detector node or identity acceptance.

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: saved BGR versus O1 gray projection, same-support column-side color differences and apparent-transparency limits; unpooled O1 gradient stencils, central-difference aliases and stored-output binding; ordered column-side preservation and joint-marginal collisions; candidate-relative reindexing, whole-inventory O1 novelty and central-gap peak controls; full-height ordered sampling versus finite-band collisions, existing dark-cap/material-profile and registered-motion owners, recorded raw artifact/static/texture evidence and registered-template ownership without replaying their gates, human reference ambiguity versus model abstention, unchanged-score denominator changes, finite-band distinct-raster collision and material/static provenance, fixed-score separate-median reversal, locality ablation gains/regressions, W3 context limitations, W0 profile identity failures and the October partial-path pooling counterexample; multi-family current proposals, material paths and scalar medians, R22-1 candidate-centered bands, R22-2 native paths, broad texture gates, R16/R21 association, reviewed BASE/Accum checkpoints, and rejected R23 polarity-only association.
- Prior mechanisms rejected: edge/peak-only identity, scalar near/far threshold identity, source-family independence, generator votes, motion-only bootstrap, polarity vetoes, global jump/texture relaxation, private coordinate conditions, stale ID/coordinate transfer, interpolation/carry and downstream repair.
- Preserved contracts: one generic bounded detector, exact current-frame provenance, independent Oil/Foam, typed no-interface state, fail-closed ambiguity/unobservability, bounded history/resources and separate target-Windows qualification.
- Difference from prior failures: the new boundary first measures whether the optical scene is informative, retains contour geometry/uncertainty and derivation lineage, and postpones all temporal authority until interface-versus-structure discrimination is demonstrated.
- Logic-map impact: NONE — this update changes offline target-truth binding only; the previously mapped A1 diagnostic and production decision owners remain unchanged.
- Failure-registry impact: NONE — this architecture refines the response to existing failures without claiming field repair.
