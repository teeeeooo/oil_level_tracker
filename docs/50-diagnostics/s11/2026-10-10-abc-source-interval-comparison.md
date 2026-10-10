# A/B/C reviewed source intervals and existing-lane comparison

Date: 2026-10-10. Base: `725d5b1a710e6c587b268577ccf85b1357b9713d`.
The user answered **“두 범위 모두 맞음”** to the A/C source review. The
[separate receipt](2026-10-10-upper-projection-ac-reply.json) closes both
position questions; the frozen preparation, pictures and earlier replies stay
unchanged. B's previously reviewed interval remains closed.

| Source at diagnostic X950 | Reviewed role | Inclusive source rows / pixel-cell bounds |
|---|---|---|
| A/f1232, 41.108 s | Foam upper outline | 476–481 / Y[475.5,481.5] |
| B/f1438, 47.981 s | Water upper projection; no Foam layer | 484–489 / Y[483.5,489.5] |
| C/f1643, 54.821 s | Water upper projection; no Foam layer | 489–494 / Y[488.5,494.5] |

These are three exposed stills from **one recording**, not recording-level
independence or a holdout. They qualify uncertainty at one source column, not
exact Y, dense contours, layer thickness, candidate identity or calibrated
Glass height. A's lower liquid–Foam interface remains unclear and unscored.

## What the unchanged saved arrays preserve

The [complete machine record](2026-10-10-abc-source-interval-comparison.json)
binds the preflight, every input, all column measurements, all original C seed
paths at both frozen scales, runner and independent verifier. It joins existing
captures; no video decode, preprocessing, detector or new candidate runs.

| Existing observation | A | B | C |
|---|---|---|---|
| Native Canny rows inside the reviewed interval | 477 | 485, 488 | 491 |
| Retained Foam-appearance face crossings inside it | None | None | None |
| All retained appearance crossings at the column | 14 | 2 | 2 |

For A, all six reviewed rows have whiteness zero and no raw white, chromatic,
recovered-droplet or retained support despite visible texture and an edge. The
saved lightness is 0–57, below the unchanged 125 white-support floor. This
narrows the [earlier regional diagnosis](2026-10-10-water-foam-representation.md)
to the now-reviewed upper position: loss precedes cleanup/component ranking.
It does not establish a replacement predicate or full-application failure.

B/C are no-Foam controls. Missing Foam support at their water surface is not a
Foam miss, but prevents treating appearance perimeters as complete liquid
boundaries. B's retained crossings are Y885.5/890.5; C's are Y886.5/890.5.
The metadata's `decision=NOT_EVALUATED` describes diagnostic interpretation.
The first diagnostic components actually have statuses `ambiguous` for A and
`weak_rejected` for B/C; selected diagnostic rank does not mean accepted Foam.

## The path loss differs between B and C

| Source / fixed scale | Original seeds / eligible paths | Retained paths | Interval-compatible centre samples before / after retention |
|---|---:|---:|---:|
| B native, prior complete audit | 33 / 33 | 6 | 0 / 0 |
| B height 200, prior complete audit | 12 / 12 | 6 | 0 / 0 |
| C native, reused saved capture | 22 / 20 | 6 | 2 / 1 |
| C height 200, reused saved capture | 12 / 12 | 6 | 0 / 0 |

The [B audit](2026-10-10-b-material-path-interval.md) already establishes loss
inside each polarity's per-seed path reduction before final top-k, despite
legal reference-compatible alternatives. C native instead retains candidate
index 1 with a centre-sector sample at source Y490 and original median Y489.
The centre sector spans X[907.5,991.5); it is not an observed contour at X950.
Its scalar compatibility does not certify every side sample or selected output.

C height 200 has no compatible centre sample even before retention. Its nearby
retained sample is Y471.525, with median Y475.675. This readout does not locate
C's earliest loss among resized pixels, pooled profiles, eligibility and path
reduction. B's stronger causal conclusion is not transferred to C. Native-only
C compatibility is not permission to choose a scale after results.

Thus a uniform top-k/threshold repair or a median-to-centre substitution is
unsupported. Current raw edges preserve alternatives but supply no automatic
physical-role selector. Existing connected-edge, appearance and reference
failures remain closed; no new detector mechanism is promoted.

## Legacy regression output now states its actual scope

The existing [casewise comparator](../../../tests/diagnostics/s11_resolver_replacement_compare.py)
now labels its JSON `comparison_scope=legacy_scalar_agreement` and
`physical_acceptance=NOT_EVALUATED`, links the qualification owner, and uses
the same wording in its CLI. This makes the already adopted interpretation
visible at the actual command entry point.

The original 13 cases, numbers, error calculation, numerical epsilon, PASS/FAIL,
exit codes, alignment/runtime/provenance/row-count guards and fingerprints are
unchanged. No failing legacy result is hidden or reclassified as PASS. A
different measurement target still requires explicit reconciliation against
qualified physical evidence before runtime adoption.

Five existing focused tests pass. Four synthetic JSON scenarios also run through
the actual CLI: unchanged and perfect scalar agreement still exit 0; one
regressed case despite a better aggregate and a missing former numeric still
exit 1. All original comparison fields except explanatory prose equal the
frozen comparator. These are tooling checks, not new video accuracy results.

## Verification and next source boundary

Independent pixel-neighbour enumeration verifies all source-coordinate appearance
faces; direct array reads verify three references/18 stage pixels; separate
joins verify all 34 original C seed paths and 12 retained paths. All pinned
inputs and 226 production files match the base. No application replay is needed
for a saved-array join and diagnostic output qualification.

Preserved attempt 001 stopped at a hash-object adapter assertion before array
readout. Attempt 002 incorrectly treated already-source-space unit faces as
local; independent verification rejected its three full face-column lists.
Attempt 003 corrects only that coordinate interpretation and passes. The raw
interval rows, interval-face absence and C path joins also match independently.
No source evidence or historical result was overwritten to repair the reader.

The next [sample4 source preparation](2026-10-10-sample4-center-source-review.md)
asks whether one previously confirmed target-domain Oil boundary has a usable
fixed-column uncertainty interval. It does not repeat its physical-role judgment
or relabel the whole old corpus. A/C/B require no further review; Windows is not
needed for this source question. Current execution state belongs to the
[Work Plan](../../00-project/work-plan.md).

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `FOAM-CANDIDATE`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: A's isolated Foam upper support is absent at the initial absolute-lightness predicate; B's earlier audit establishes per-seed path compression; C native retains compatible geometry and C reduced earliest loss remains unlocalized. Mistaking legacy scalar agreement for new physical acceptance would be an evaluation error.
- Logic-map impact: NONE — no production owner, coordinate, candidate, admission or selection changes; existing saved arrays and comparator are reused.
- Failure-registry impact: NONE — the source-specific readout applies existing representation/identity/provenance limits and introduces no newly accepted physical mechanism.
