# Windows Sample 1 Heating Cold-Start Reviewed Truth

## Authority

This document is the validation source of truth for the private field video
identified inside this project as `windows_sample1_heating_coldstart`. The name
is an operator-facing alias, not the source file's real basename. The private
video is not stored in this repository.

The timeline below comes from direct user review of the source video and was
last reconciled on 2026-08-25. The operator confirms that the R14 through R17
Windows comparisons refer to the same physical video. Detector output, graph
shape, a prior implementation's selected row and a prior evidence document
cannot redefine this reviewed physical truth.

The source file hash and media fingerprint have not yet been recorded. Until
they are, the alias plus the operator's same-video confirmation is the available
identity authority; it is not cryptographic source identity.

The machine-readable companion is
[`windows_sample1_heating_coldstart.reviewed-truth.json`](windows_sample1_heating_coldstart.reviewed-truth.json).
Every future Windows field report must enumerate all of its segment IDs.

## Interpretation contract

- Times are source-video seconds. Transition times marked `about` are reviewed
  behavioral boundaries, not frame-exact annotations.
- Source Y increases downward. A rising interface therefore normally has
  decreasing source Y; a falling interface normally has increasing source Y.
- Oil material being present is distinct from a visible Oil boundary. A Glass
  may be full of Oil while exposing no publishable interface.
- Wall splash, adhered residue, glare, the Glass bottom and mechanical
  structures are not Oil or Foam boundaries.
- During a separated Oil/Foam layer, the Foam front is above the lower Oil/Foam
  boundary, so `foam_y < oil_y` in source coordinates.
- This review establishes interval behavior and material identity. It does not
  invent exact source-Y anchors where none were directly re-reviewed.

## Reviewed timeline

| Segment ID | Glass | Interval | Reviewed physical behavior | Required detector meaning |
|---|---|---|---|---|
| `WS1-BASE-FULL-PREFIX` | BASE | 480--about 550 s | Oil fills the Glass; no interface is visible. Foam is absent. | No numeric Oil or Foam boundary. FULL/no-interface may be reported when supported. |
| `WS1-BASE-DRAIN` | BASE | about 550--662 s | Oil slowly leaves the Glass. An oil-air interface appears and generally moves downward. | Track the visible oil-air interface; intermittent absence is a miss, while a lower structure/glare row is a false Oil identity. |
| `WS1-BASE-RAPID-REFILL` | BASE | 662--about 663.6 s | Oil rapidly enters and the interface rises quickly until it disappears at the top. | Track the rising interface while visible, then close it as full material rather than transferring to another row. |
| `WS1-BASE-FULL-SUFFIX` | BASE | about 663.6--780 s | The Glass remains full; no interface is visible. Foam is absent. | No numeric Oil or Foam boundary. A lower/reflection row, including around 725 s, is false. |
| `WS1-ACCUM-EMPTY` | Accum | 480--about 653 s | The Glass is empty; Oil and Foam are absent. | No numeric Oil or Foam boundary. |
| `WS1-ACCUM-ENTRY-SPLASH` | Accum | about 653--672 s | A small amount of Oil enters rapidly, strikes the bottom and splashes. Continued inflow raises the real interface and leaves wall marks. Foam has not started. | Track the rising Oil boundary. Splash and adhered wall marks must not become the Oil owner or Foam. |
| `WS1-ACCUM-FOAM-LAYERED` | Accum | about 672--680 s | Foam appears above Oil, producing an upper Foam layer and a distinct lower Oil/Foam boundary. | Publish the two material identities separately: upper Foam and lower Oil boundary. The Foam top must not become Oil. |
| `WS1-ACCUM-POST-FOAM` | Accum | about 680--700 s | Foam disappears. The Oil boundary remains visible before the later reversal. | Foam must be absent; the visible Oil boundary remains the Oil owner. |
| `WS1-ACCUM-DRAIN` | Accum | about 700--780 s | The Oil level reverses and continuously falls, leaving adhered residue on the Glass wall. | Track the descending Oil interface. Residue is neither a replacement Oil boundary nor Foam. |

BASE Foam is absent throughout the reviewed 480--780 s interval. Accum Foam is
present only in the reviewed `WS1-ACCUM-FOAM-LAYERED` interval.

## Superseded prior interpretations

The latest direct review supersedes these older interpretations wherever they
appear in R14/R16/R17 diagnostics, evidence or validation prose:

- BASE 540 s/Y437 is not a valid Oil anchor. It lies in
  `WS1-BASE-FULL-PREFIX`, where the Glass is full and no interface is visible.
- BASE 674 s/Y435 is not a valid Oil anchor. It lies in
  `WS1-BASE-FULL-SUFFIX`, after the interface disappeared at about 663.6 s.
- BASE 634 s lies inside the real drain interval, but the previously reported
  exact Y360 remains a historical point estimate until it is re-reviewed as a
  frame-exact annotation.
- Accum 758--774.5 s is not a real Foam interval. The latest review establishes
  that Foam disappeared at about 680 s; later wall residue must not be counted
  as Foam.
- The prior aggregate target of “52 real Foam rows” is detector-output cohort
  history, not physical truth and not a future acceptance target.

Historical evidence files remain unchanged as records of what was believed or
measured at the time. This validation owner controls future acceptance when
those records conflict with the latest direct review.

## Mandatory future report shape

Every replay or bundle audit for this sample must report each of the nine
segment IDs separately. For each segment it must include:

- actual sampled time/frame coverage;
- final numeric Oil and Foam row counts and contiguous runs;
- selected source-Y range and direction where a boundary is expected;
- false-boundary identity and longest missing/wrong run;
- material-phase, owner-chain and selected-tracklet transitions when trace is
  available; and
- PASS, FAIL or NOT_EVALUATED against this reviewed behavior.

A report is incomplete if it omits a segment, treats a graph bridge as a
numeric observation, derives truth from detector candidates, or substitutes an
old version's row counts for source review. Exact coordinate accuracy must be
scored only against separately reviewed source-Y annotations; interval-level
presence, absence, ordering and direction remain valid without them.

## Source identity completion

When the private source is next available on Windows, record its SHA-256, byte
size, width, height, FPS and duration in the companion manifest without adding
the real filename. That read-only fingerprint strengthens same-video identity
but does not change the reviewed timeline.
