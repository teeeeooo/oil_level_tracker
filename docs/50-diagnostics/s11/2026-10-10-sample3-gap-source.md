# Sample3 longest numeric gap — bounded source qualification

Date: 2026-10-10. Repository head: `78eb52170ab6b9e61addab02068b31195fbd1f3a`.
Follow-up to the [saved cadence audit](../../60-evidence/s11/2026-10-10-oil-observation-cadence.md)
after closing the [sample4 owner investigation](2026-10-10-cadence-owner-causality.md).
The [machine archive](2026-10-10-sample3-gap-source.json.gz) preserves source pins,
preflight, frame metadata, saved phase witnesses, verification and the question.
No detector or formal truth changes.

## Why this review is needed

The longest sample3 adjacent-numeric interval is **34.5345–81.014267 seconds**,
with 92 unavailable rows over 46.479767 seconds. Those endpoints are numeric
observations, not independently certified physical anchors. The
[existing episode audit](../../60-evidence/s11/2026-10-08-episode-source-review-validation.md#sample3-whole-episode-detector-audit)
already attributes 87 missing rows to FILLED_CAP_VETO. Repeating that count or
disabling the barrier cannot establish whether there was visible Oil to detect.

Freeze 16 uniformly spaced saved-row indices including both endpoints before
inspecting pixels. Add the four old S3 annotation frames for source equality,
giving 19 distinct source frames. Decode ordinally from the original recording;
preserve actual backend times. The
[complete contact sheet](2026-10-10-sample3-gap-contact.png) uses unchanged
360×360 context crops around the existing 240×240 Recipe rectangle. No centre,
ellipse, margin, initial state, source frame or historical label is corrected.

Agent inspection sees full-looking middle views and substantial framing/focus
changes, followed by an upper yellow/brown versus lower dark partition in the
late views. This is an interpretation, not new human truth. It does **not**
justify calling the entire 46.48-second gap a miss on continuously visible Oil,
or calling every intermediate view FULL_NO_INTERFACE.

## One new physical question

The [A/B source image](2026-10-10-sample3-gap-role-review.png) shows:

| View | Source frame/time | Saved Oil | Existing phase restriction | Publishable rows before restriction |
|---|---|---|---|---:|
| A | f2249 / 75.041633s | unavailable | FILLED_CAP_VETO; allowed IDs empty | 5 |
| B | f2339 / 78.044633s | unavailable | FILLED_CAP_VETO; allowed IDs empty | 3 |
| Later numeric return | f2428 / 81.014267s | Y233 | DRAIN_RELEASE_CONFIRMED | 3 |

The [frozen question](2026-10-10-sample3-gap-role-review.json) asks whether the
yellow/brown-to-dark boundary in A and B is actual Oil, another physical/optical
feature, or too unclear to judge. These are the first two uniform-sheet samples
after the soft-focus framing transition that show that late partition in agent
inspection. This adaptive choice is declared; it is not an unbiased performance
sample or a newly claimed holdout.

If the boundary is visible Oil, these exact missing observations warrant a
separate reappearance/phase investigation. Otherwise, they must not be counted
as missed visible Oil; an unclear reply leaves them unscorable. In either case,
there is no automatic candidate, exact-Y, tolerance, entire-window or initial-state
label, and no authority to remove the phase gate. The question remains **OPEN**.

S3-01/02 keep their original qualitative/ruler scope. The old S3-03/f2848 at
95.028267s and S3-04/f3147 at 105.0049s remain human-labeled unusable. The new
question does not reopen them or require whole-video relabeling. No Windows
execution is required for this source judgment.

## Verification

- All 19 context crops exactly equal the declared rectangles in their ordinal
  full frames. The 16 sheet panels retain native pixels with no resize.
- All 16 selected source timestamps match saved cadence rows. All four old S3
  frames match the previously audited originals pixel-for-pixel.
- Both A/B review panels equal twofold nearest-neighbour source pixels. There
  is no sharpening, interpolation, candidate overlay or reconstructed boundary.
- The prior full resolution matches its observer receipt hash. All 151 saved
  frame/time/raw-Oil rows join the cadence audit; four exact phase witnesses
  above are retained, without rerunning detection.
- Source, Recipe, cadence and audit input hashes are unchanged. Native artifacts
  remain in `sample/output/s11-sample3-gap-source-20261010-001/`.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: UNKNOWN pending the physical role/visibility of A/B. The saved empty allowed-owner set is confirmed; a phase veto on visible Oil is not established by an unlabeled numeric gap or internal publishability alone.
- Logic-map impact: NONE — source inspection and existing saved decisions only; no detector ownership or control-flow change.
- Failure-registry impact: NONE — existing fail-closed/phase/identity constraints remain; no new mechanism or field claim is adopted.
