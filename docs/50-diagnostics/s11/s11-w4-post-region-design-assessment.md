# S11 W4 post-region design assessment

Date: 2026-10-06. Source inspected: `751fbf7`.
Status: completed local assessment; no new classifier, field run or acceptance.
Current execution state belongs to [work-plan](../../00-project/work-plan.md).

## Decision

Do not turn the completed region experiment into an identity classifier by adding
material/static penalties, choosing a residual threshold, or counting model minima.
Keep the existing reviewed positive/negative cases: they are useful development
controls, not missing merely because physical opposition is unmeasured.

The initial assessment identified **two conditional development routes**, not an
already validated next mechanism. The subsequent input decision below selects
the passive route:

- If additional review of existing passive SPL#1 material is feasible, first
  define a bounded candidate-conditioned RGB/context discrimination study with
  physical identity targets and episode-separated evaluation. A statistical
  classifier need not measure transmission or have another sensor, but its
  identity claim must come from those controls, not the word “physical.”
- If reference/comparison acquisition is feasible, assess the existing witness
  architecture's registered optical-reference route. A measured response relative
  to a known reference could test a different hypothesis from intensity fitting;
  its availability and discriminatory value have not been established here.

Prefer reusing passive inputs if suitable additional review is available; do not
require hardware changes on the strength of these two frames. If neither new
review nor reference acquisition is feasible, retain this experiment's closeout
and name the evidence limit instead of launching another descriptor sweep.
The input capability was unresolved at the initial assessment; the following
user decision closes it without another identity judgment on the reviewed cases.

## Input feasibility resolved — user decision

The user subsequently confirmed that additional review of other intervals/regions
of the same video and of other existing videos is feasible. Comparative filming
is unavailable because the environment cannot be reconstructed. This resolves
the conditional choice above: proceed with passive existing-video evidence;
controlled-reference acquisition is outside the current plan. No repeat feasibility
question is needed.

Other recordings are now eligible for a planned review/partition process, including
SPL#2/#3 if actually available. This supersedes the old blanket deferral for this
scope, but does not assign any recording as holdout or authorize a whole-video
replay. First obtain metadata and prior-exposure history, without inspecting a
potential holdout's pixels or candidate losses.

Source inspection of `s11_interface_shadow_evaluation.validate_labels` adds a
concrete constraint: `previously_reviewed` cases must remain `regression`, and one
`recording_group` (also one bundle run) cannot span partitions. This is stricter
than merely separating episodes in the conceptual design above. Keep all SPL#1
cases in their existing recording group and `regression` partition, even when
new frames/regions are reviewed. They can refine failure understanding and provide
regression checks; they do not supply new calibration or untouched test evidence.
Do not rename groups or change existing labels to bypass this lock.

The first bounded handoff is [passive control review preparation](../../40-operations/s11-o2-local-shadow-evaluation.md#passive-control-review--first-bounded-batch):
three exact saved SPL#1 records selected from predeclared intervals, complete
candidate inventories, candidate-guided review with uncertainty, and a metadata-only
list of other recordings. No classifier fitting or production change is involved.

## What the completed evidence does and does not resolve

[Region closeout](../../60-evidence/s11/s11-o2-color-side-local.md#denominator-reconciliation-closed-and-bounded-region-disposition)
records 108 finite main views with partition < smooth for both identities, and
30/36 model-minimum disagreements in the human-unresolved BASE pair. These show
that the sign of partition improvement or a particular minimum-error model is
not an identity certificate. They do not prove that the full RGB/context input
contains no learnable discrimination, or that a magnitude-based classifier cannot
work with appropriate development/calibration/holdout evidence.

The [human rationale](../../60-evidence/s11/s11-o2-identity-context-windows-review-001.md#candidate-guided-human-rationale-received--2026-10-02)
describes a visible separating boundary and side appearance at Accum idx10,
versus no comparable boundary at idx15. It is candidate-bound qualitative truth;
it is not per-pixel segmentation, measured transmission or proof that every
sector independently distinguishes the classes. No repeat of this question is
needed. Formal identity, local path support and scalar Y remain separate.

## Source audit: opposition is not a new independent measurement by name

| Existing owner | What the implementation measures | Consequence for a next design |
|---|---|---|
| [Material path](../../../src/oil_tracker/adapters/vision/oil_material_path.py), `material_layer_context_features`, `_terminal_material_partition` | Row summaries of the supplied material raster; upper/lower profile difference at three depths; scalar row texture conflict | Preserve available context, but do not describe a row profile as physical liquid/air segmentation or independent evidence |
| [Candidate assembly](../../../src/oil_tracker/adapters/vision/phase_candidate_assembler.py), `assemble_phase_candidates` | Material-path/context input is `foam.combined_evidence_map` from the current raster | Raw shared material evidence is reusable; accepted/public Foam identity is not an Oil label or mask |
| [Foam raster owner](../../../src/oil_tracker/adapters/vision/foam_front_detector.py), `detect_bottom_connected_foam` | Current-image lightness/chroma, whiteness and texture/edge evidence | A different feature name does not provide a new acquisition lineage; do not copy Foam thresholds into an Oil classifier |
| [Static learning](../../../src/oil_tracker/adapters/vision/opencv_phase_detector.py), `learn_static_artifact` | Persistence of horizontal masks in supplied frames, retained at persistence >=0.75 | Existing static maps are recurrence evidence. A stationary true interface can persist too; construction alone does not establish an artifact-only reference |
| [Artifact calibration](../../../src/oil_tracker/adapters/vision/artifact_calibration.py), `artifact_match_score` | Candidate normalized position/extent/angle versus registered template geometry | Registration supplies contextual provenance, but a geometric match does not explain the current pixels or distinguish a crossing true boundary |
| [Registered raster evidence](../../../src/oil_tracker/adapters/vision/temporal_raster_evidence.py), `RegisteredOilMotionTracker` | Adjacent gray rasters, bounded translation, exposure compensation, common support and residual change | Reuse this owner if a later design needs registration; do not rename compensated motion as refractive displacement or physical association |
| [Recorded audit](../../../tests/diagnostics/s11_shadow_target_audit.py) and [region owner](../../../tests/diagnostics/s11_region_competition.py) | Stored context projection and fixed same-frame appearance fits | Reuse provenance/availability and saved-output loading; no second acquisition or evidence-inventory implementation is needed |

This is a source ownership/semantics audit, not proof that any private run used a
particular reference-frame set or that its registration succeeded. Private source
rasters, full CSVs and reference acquisition metadata were not read locally.

The [existing context return](../../60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md#context-availability-and-limits)
already reports material/static/glare fields: material summaries overlap and the
positive/negative direction differs across BASE and Accum. Many static/glare
summaries are zero in both classes. Do not repeat that inventory, interpret zero
as verified absence of opposition, or assume the detailed maps are useless solely
because their summaries overlap.

## Controls already available and the specific remaining gap

| Control | Reuse | What it cannot establish |
|---|---|---|
| Accum f16280 idx10 / idx15 | Main same-frame, same-X reviewed interface/non-interface pair; candidate-guided rationale is recorded | One scene does not establish false-positive behavior for reflective steps across episodes; near/off is not whole-candidate identity |
| BASE f14386 idx11 | Reviewed structure negative, with exact native geometry | Censored sectors are unavailable; depth below Oil and a mask boundary are not the negative mechanism |
| BASE f14386 idx0 / idx20 | Explicit human-unresolved alternative pair, including uncertainty after historical video review | Historical opposite labels cannot be used as clean opposite truth or forced apart by a model |
| Review-001 f11508 | Existing candidate-level non-interface judgments | All 23 candidate labels do not certify an empty vessel, an artifact-only reference raster, or absence of every possible interface |
| BASE f14865 scene A/B and four native paths | Geometry/provenance and unresolved alternative checks | Scene-level approximate boundaries do not become candidate identity or temporal links to f14386 |

The missing test is not simply another far-away negative. It is a counter-control
where the proposed cue is shared by a reviewed non-interface and a true interface,
with usable support, so the mechanism must use additional justified context or
abstain. In particular: a reflective/structural two-sided step, a stationary or
weak true interface, a true interface crossing a registered artifact, and an
unresolved overlapping boundary. These are requirements for validating a next
proposal, not claims that such private controls have already been found.

## Passive-data route: concrete contract before implementation

The proposed question is: **does candidate-conditioned spatial RGB/context reduce
wrong-structure support while retaining reviewed interface support, compared with
the frozen existing baseline and with abstention reported explicitly?**
This would be statistical discrimination, not a transparency estimator.

1. Reuse the saved crop, masks and candidate geometry/provenance owners. Retain
   path-versus-center roles and real unavailable support. Labels, frame/Glass IDs,
   source family, selected/rejected flags and known truth Y are not inference cues.
   Geometry conditions sampling; absolute private coordinates must not encode
   the answer. Keep same-frame derivatives in one lineage.
2. Freeze a bounded review/control manifest and physical episode groups before
   model/threshold selection. Reuse the existing judgments with their uncertainty;
   extra review would target the named counter-control gap only, not repeat W2/R3.
   Keep both candidates, all sectors/scales and augmented copies of one episode
   together. Column holdout or random candidate splits are not independent tests.
3. Define the candidate-level target and abstention accounting with existing W3.
   Report wrong-structure support, interface support and unresolved coverage by
   negative family/support condition. Compare errors at a declared coverage or
   operating point; an all-unresolved system is not a successful discriminator.
   No numeric acceptance threshold or minimum sample count is invented here.
4. Select one model/capacity and calibration policy on development evidence only.
   A candidate-conditioned full-context classifier is a representation proposal,
   not an instruction to train a network on two frames or search feature weights
   until the known pair separates. If usable episode-separated controls cannot be
   assembled, implementation has no justified evaluation endpoint yet.
5. Reuse the O2 acceptance owner for calibration/holdout and exact behavior equality.
   The later input decision above permits planning use of other recordings.
   Existing SPL#1 cases remain regression under the implemented recording-level
   lock; new partitions need an explicit concrete plan, not retrospective
   relabeling of already-inspected examples as untouched holdout.

This route could use the same camera; it does not assume that new reference
hardware is logically necessary. Its immediate dependency is feasible additional
review/evaluation coverage, not more arithmetic on the current two scenes.

## Reference route: alternative feasibility contract

The [witness acquisition modes](../../20-architecture/s11-interface-observability-witness-architecture.md#acquisition-modes)
already name controlled illumination, structured background and polarization.
Do not introduce a second architecture or presume fixture access.

The distinct proposed observable is a registered response of known background or
controlled optical conditions on each side of a candidate, with known reference
state and common visible support. It is a testable hypothesis, not proof that
Oil, vessel curvature and reflection must produce different responses. A natural
background would also require a stable identifiable reference; arbitrary adjacent
frames are not automatically such a reference.

Before implementation, identify what can actually be captured, reference identity,
camera/fixture/illumination consistency, registration support and uncertainty, and
whether the relevant physical state stays comparable across a capture pair.
Reuse registered-raster infrastructure where its contract fits, but its current
global gray motion residual is not this optical response measurement. Test
reflection, lighting change, vessel effects, stationary true interfaces and failed
registration as explicit counter-controls. Missing reference or poor registration
must remain unavailable. No new acquisition or sensor purchase is requested here.

## Next action and stopping boundary

The local assessment and input-scope decision are complete. Execute the linked
bounded review-preparation handoff on Windows, where private material resides.
Stop at a displayed candidate-guided question awaiting the human answer, or at a
named missing-input/presentation limit. Existing uncertainty is not an instruction
to repeat a judgment until it becomes definite.

Other-video metadata supports a subsequent recording-level development/calibration/
holdout allocation. It does not establish enough independent recordings exist;
previous use or shared-session lineage may prevent the desired split. Preserve
that gap explicitly before training. A network architecture, loss, threshold and
sample-count sufficiency remain unselected. No controlled acquisition is requested.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: private identity failure remains unlocalized by these two-frame appearance experiments; this audit identifies input-lineage and evaluation gaps, not a new field cause.
- Prior mechanisms reviewed: region residual/order fits and denominator closeout; material row/terminal context, same-frame Foam raw maps, persistent horizontal masks, registered template geometry and compensated adjacent-frame motion; existing reviewed controls and O2/W3 acceptance.
- Prior mechanisms rejected: material/static penalties renamed as independent physical measurements, minimum-error model as identity, motion-only anchors, truth-distance/Glass rules, missing-as-zero, and two-frame training portrayed as independent field validation.
- Preserved contracts: generic bounded same-frame candidate provenance, separate identity/path/scalar targets, independent Oil/Foam, uncertainty and censored support, unchanged labels and FIELD FAIL, no private rerun or acquisition by implication.
- Difference from prior failures: selects the required evidence/evaluation branch before choosing an algorithm; no extra descriptor or authority is created from the same returned summaries.
- Logic-map impact: NONE — no executing detector, diagnostic code or publication path changed.
- Failure-registry impact: NONE — source lineage and evaluation sufficiency are assessed without claiming a newly established private causal failure or repair.
