# Optional material-reference design choice — 2026-10-09

Source inspected at `7406903ab928cdde8bbfe65ae85c6e010bc6a3a9`.
This is a **proposal awaiting a product-scope choice**, not an accepted runtime
contract, implementation or finding that automatic detection is impossible.
The [Work Plan](../../00-project/work-plan.md) owns the current transition.

## Why this choice is now concrete

The [retained-support audit](2026-10-09-retained-support-boundaries.md) preserves
the complete geometry but shows why a shared appearance label is insufficient:
glass, reflection and fluid-looking support can share that label. The beer reply
also prevents treating two projected arcs as two material interfaces. The milk
reply preserves a genuinely unresolvable lower-interface reference rather than
inventing a coordinate below its visible upper outline.

Read-only source tracing confirms these distinct responsibilities:

| Existing owner | Actual entry and authority | Reuse boundary |
|---|---|---|
| [Frame evidence collector](../../../src/oil_tracker/adapters/vision/phase_frame_detection.py) | Calls `detect_bottom_connected_foam` before template rejection of the resulting Foam candidate | Existing artifact setup cannot separate already mixed Foam support |
| [Artifact calibration](../../../src/oil_tracker/adapters/vision/artifact_calibration.py) | `apply_artifact_templates` matches candidate envelope geometry and rejects the whole matching candidate | It is neither a partial contour mask nor a material identity seed |
| [Artifact reference capture](../../../src/oil_tracker/adapters/vision/artifact_reference.py), [immutable reference](../../../src/oil_tracker/domain/artifact_reference.py) | Preserve bounded original pixels, geometry/settings identity, source position and review scope; the saved support is deliberately not consumed by the matcher | Reuse capture, integrity and invalidation patterns; do not silently give negative-reference data a positive material role |
| [User truth service](../../../src/oil_tracker/application/services/user_truth.py), [truth domain](../../../src/oil_tracker/domain/user_truth.py) | Result-review annotations and benchmark/export provenance | Do not feed these evaluation labels into runtime or relabel them as Recipe inputs |
| [Recipe](../../../src/oil_tracker/domain/recipe.py) | Current configuration and artifact references; no positive Oil/Foam reference field | A positive reference would be an explicit new input contract, not an already implemented option |

The public empty/filling/filled original sheets were inspected again. They can
oppose interpretations based only on brightness or common motion, but they do not
certify every fixed-glass pixel or provide a full material segmentation. No new
image interpretation was saved as human truth and no new detector run was made.

## Two alternatives for the next bounded design

**A — keep the present input workflow.** Continue an automatic material-boundary
challenger using current video, geometry and optional structure references.
No positive target initialization is available. Current unresolved appearance
and optical cases remain part of its required opposing controls. Existing failed
rules cannot be repeated with retuned thresholds.

**B — additionally investigate an optional positive material reference.** While
setting up an analysis, the operator may select a clearly visible example of the
actual Oil boundary and, separately if visible, the Foam front. The examples may
come from different frames. This is optional; absent or unclear fronts need no
input, and the existing automatic workflow remains available. It introduces
semantic information about a desired target, alongside the existing negative
structure references, without a trained model.

B is the recommended **feasibility branch**, not a promised detector solution.
It directly addresses uncertain initial target identity instead of expecting a
negative glass reference to identify everything else as fluid. Its cost is an
extra optional setup interaction. A source-bound example cannot be silently
reused as truth for another video; changed video/geometry may require a new
example. Neither choice authorizes a mandatory new setup step.

## Concrete limits of option B

1. Use a visible preview candidate/short boundary vicinity as a reference, with
   native source pixels, video/frame identity and independent role `Oil` or
   `Foam`. The operator does not enter exact XY numbers or label every frame.
   An approximate vicinity is not an exact contour or a mask of pure material.
   If it contains several unresolved boundaries, the reference stays ambiguous;
   the prototype cannot manufacture a target candidate from the click alone.
2. Keep one optional reference per visible role for the first experiment. Do not
   ask for hidden milk boundaries, label the two beer arcs as different roles,
   or import existing benchmark truth into the live detector.
3. A reference initializes a semantic hypothesis. Every later numeric output
   still needs a current-frame observed boundary and independent role evidence.
   A remembered Y, appearance similarity, low tracking error or shared component
   ID cannot carry numeric authority through disappearance, crossing or drift.
4. On ambiguity/loss, abstain for the affected role. Oil and Foam availability
   remain independent. Automatic processing must not stop to demand repeated
   operator corrections. No interpolation or fixed-coordinate exception follows.
5. Preserve bounded reference capture/integrity patterns from the existing owner;
   use a separately typed role if implementation becomes justified. Do not extend
   the meaning of `ArtifactSupportReference` or the truth schema by accident.

The matching, material-side evidence and abstention mechanism still require a
fixed preflight. This proposal does **not** declare template tracking alone a
physical solution or approve production integration.

## Work after the choice

If B is selected, first prepare an offline source-bound prototype and its frozen
controls, before UI/schema work. Compare reference-assisted versus unassisted
behavior on the same disclosed development exposures. Protect the existing
sample4 actual fronts, glass-rim and internal-texture controls, inclined water,
beer perspective arcs, milk's unknown lower interface, true structure crossings,
optical warp and the prior rim-jump counterexample. Initializing from a reference
and scoring that same reference is not recovery success. Separate initialized,
later observed, lost and falsely reacquired outputs.

Stop the branch if the new input merely makes a tracker confidently follow glass
or internal texture, or requires repeated manual rescue. Keep the failed result;
do not compensate by enlarging reference masks or relaxing authority/phase gates.
Only a useful bounded result justifies proposing Recipe/UI integration. Existing
Mac regressions and the Windows field gate remain required for behavior adoption.

If A is selected, close B as a declined workflow extension and continue the
automatic challenger design with the same existing inputs. Neither branch
requires another milk/beer interpretation, ML, Windows execution or file export
at this decision point. No branch has been executed by this note.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PROPOSAL`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: retained appearance support can mix structure and fluid before candidate rejection; a positive reference is an untested proposal for initial identity, not a diagnosed complete repair.
- Logic-map impact: NONE — source tracing and a proposed optional input change no runtime owner or authority.
- Failure-registry impact: NONE — no new mechanism was executed; prior geometry, appearance, tracking and truth-leakage limits remain applicable.
