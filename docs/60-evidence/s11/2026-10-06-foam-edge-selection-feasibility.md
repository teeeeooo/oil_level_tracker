# Foam edge-selection feasibility and two-time review — 2026-10-06

Base source: `731502f568df0c5644734e140e8dfb7294cd03eb`.
Status: bounded appearance-rule audit complete; no rule promoted. FIELD FAIL /
NOT_EVALUATED. Existing runtime, labels and Windows truth are unchanged.

## Ownership and design decision

The [annotated B reply](2026-10-06-boundary-temporal-residuals.md#annotated-b-boundary-reply-received)
shows that a tentatively human-attributed upper Foam edge survives among saved
alternatives even where the existing support top follows a structure. Selection
must therefore separate component material support from physical-front identity.

Existing owners were inspected by responsibility: `foam_front_detector.py` owns
support/component gates; `oil_material_path.py::_path_for_seed` selects polarity
paths with sector contrast/jump/material criteria; `s11_spatial_path_probe.py`
orders candidate-centred sector runs. They do not implement this exact read-only
question over all saved per-column peak intervals with all ties retained. Calling
them here would change inputs and introduce thresholds/proposal decisions. A
small local audit instead consumes the existing front-alternative JSON. It is
not a replacement runtime path generator and has no production caller.

Proposed separation remains: retain same-frame alternatives; establish material
and structural opposition independently; only then assess a front's spatial and
temporal compatibility, with unresolved support remaining unavailable. Physical
identity cannot be supplied by a geometric optimum. This turn tests the proposed
appearance shortcuts before introducing an acceptance mechanism. It does not
implement a purported physical selector with missing evidence.

## Exhaustive saved-inventory audit

Input: canonical `s11-local-foam-front-alternatives-002/report.json`, all14 retained
components, both pre-existing radii4/8, all574 occupied columns (1,148 views).
No image measurement, detector run, decode, strength cutoff or tuned parameter
was added. All93 inputs were rehashed before/after: 88 capture files, four
front-alternative files/receipt, and the red-mark attributed reply.

Counterfactual appearance rules, never runtime selections:

- Strongest: retain every equal-maximum vertical-magnitude peak pixel.
- Lowest: largest source Y among retained peaks.
- Nearest: retain every pixel tied in absolute distance to the original support top.
- Smoothest: minimize sum of absolute adjacent-column Y changes over each maximal
  consecutive, fully observed, nonempty column run. Every integer row in a saved
  plateau remains a state. No jump cutoff, strength weight, start/end anchor,
  private coordinate rule or tie-breaking is used. Forward/backward dynamic
  programming reports every row lying on some globally minimum-cost path.
  Censored, absent-peak and missing columns split runs; none is bridged.

The all-optimal membership calculation was compared against exhaustive path
enumeration on four small branching/tie/one-column examples. There are39 runs in
the saved inventory. This checks the diagnostic arithmetic, not detector efficacy.

The eleven tentatively marked B columns are a post-observation development
comparison, not exact contour truth, a held-out set, or a performance denominator:

| Existing radius | Mark represented | Strongest contains mark | Lowest contains mark | Nearest contains mark | Global minimum-variation membership contains mark |
|---|---|---|---|---|---|
| 4 | 5/11 | 5/11 | 5/11 | 5/11 | 5/11 |
| 8 | 11/11 | 1/11 | 7/11 | 5/11 | 11/11 |

At radius8, each marked B coordinate is also the only optimal Y at its column,
but the complete48-column C2 path is not unique: X596/597 each retains Y846 or
Y852 in the optimal membership. Total minimum variation is19 px. A row's presence
in the membership does not mean arbitrary combinations of such rows form an
optimal path; the audit never joins memberships into a fabricated selected path.

The apparent B success does not validate smoothness as identity. For example,
A X577's existing human-attributed Foam top is Y840, while the smoothest membership
is Y846; C X598–606 moves to Y852 versus original top Y845–846; much of D also
moves toward Y852. These are geometric discrepancies with prior qualitative
Foam-path attribution, not calibrated per-pixel errors. They are sufficient to
withhold a whole-path improvement claim based only on B. Both human rim controls
also produce complete radius8 smooth paths (sample4 C1:78 columns; sample2 C1:9).
Thus existence of a smooth path does not distinguish Foam from structure.

The rule audit rejects promotion of strongest/lowest/nearest/continuity alone.
It does not prove all spatial methods impossible. Neither the larger radius nor
a newly weighted combination is adopted based on this single exposed frame.

## Needed evidence and prepared human checkpoint

The user already established that circular structures stay fixed while surrounding
Foam changes. The missing item is the actual Foam-front location at another saved
time, not the structures' identity again. Frame450's tentative red marks cannot
be transferred across frames. To test later temporal correspondence with a
physical reference rather than appearance self-consistency, prepare exactly two
original saved times: frame420 (14s) and frame480 (16s), anchor450 ±30frames.
These offsets were stated before inspecting the two images; no frame was selected
by favorable algorithm output. Both lie in the already saved13–17s sequence.

The local viewer shows:

- original14s and16s ROI images and their same-coordinate enlarged context;
- anchor15s with the prior approximate tentative annotation, only on that anchor;
- source axes and the old B X-range as location guides, no detector path transferred;
- optional user click points with displayed coordinates and clear/reset control.
  Points are temporary in-browser aids, not automatically submitted or saved labels.

Question: where is the actual Foam upper boundary near the central structure at
14s and16s? Visible portions, occluded, or unclear are valid responses. This is a
bounded two-frame development review, not an independent recording or a request
to relabel the full sequence. No answer is assumed while the question is pending.

All126 preparation inputs are preserved: 124 motion-review outputs, their receipt,
and the prior annotated reply JSON. The same104×104 ROI and source origin[543,798]
are retained. The context display is X[571,619), Y[830,859); full original crops
remain visible. Enlargement adds no information. No new decoding or detector run.
Browser rendering, image loading, coordinate clicks on both frames and point reset
passed without page errors. Test clicks were cleared and are not human replies.

## Artifacts and scope of verification

Local audit: `sample/output/s11-local-edge-selection-audit-001/`.
Local review: `sample/output/s11-local-foam-two-time-review-001/`.
Both preserve scripts, manifests/reports and separate output receipts. No new
production code was introduced, so no runtime suite rerun is claimed or needed
for these saved-data calculations and review preparation.

| Artifact | SHA-256 |
|---|---|
| `s11-local-edge-selection-audit-001/run.py` | `1cf3d7f92fe656a32e5f91a48eba31763726586f6ea2754dc399737a29b2e18b` |
| `s11-local-edge-selection-audit-001/report.json` | `c831a7014c9345521362ada8ef4288a14d5f0bb9156ae73faa2bef1d61183955` |
| `s11-local-edge-selection-audit-001/receipt.json` | `37e09dfa4c820ed7497b0f141c2f06dde8b5e697e53a111c41d732ed0991344d` |
| `s11-local-foam-two-time-review-001/prepare.py` | `54d7a1f1e7e2f39cd4d3e408c5a62d51e8bfd84f356c47e8586e13d6ffde8af5` |
| `s11-local-foam-two-time-review-001/manifest.json` | `194bb6857b5bfcd8275ad281777b0ee6390acff7f8ea74e513f351791108a5a7` |
| `s11-local-foam-two-time-review-001/viewer.html` | `300dfc3342f83bff9ef422e4be14c36db35b5b3521360d25cffdb3e9400dff36` |
| `s11-local-foam-two-time-review-001/receipt.json` | `70334a0d3b7c5b0d4de0baab89cdcec96ce81ba802ceb1eaa22b25db9ce59130` |

The [current work plan](../../00-project/work-plan.md) owns the pending checkpoint.
Windows75-candidate target truth remains separate; no prediction comparison or
[O2 acceptance](../../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance)
is claimed. FIELD FAIL and the independent-recording requirement remain unchanged.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: a mixed component top precedes any reliable physical-front selection; the sampled B alternative is retained, but appearance-only choices lack identity and cannot establish a repaired front.
- Logic-map impact: NONE — saved-JSON rule audits and original-image review have no production caller or decision authority.
- Failure-registry impact: NONE — no motion-only identity, geometry-as-identity or private-coordinate shortcut is promoted; existing recurrence guards apply.
