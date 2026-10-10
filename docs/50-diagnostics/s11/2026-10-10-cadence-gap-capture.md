# Sample4 cadence gap — retained candidates and final owner restriction

Date: 2026-10-10. Capture head: `131dae4c7a4378586caa7bc589dec2f145edc2be`.
Follow-up to the [accepted one-second target and saved cadence audit](../../60-evidence/s11/2026-10-10-oil-observation-cadence.md).
No production or physical-label change. The [full machine record](2026-10-10-cadence-gap-capture.json.gz)
preserves preflight, all control witnesses, the two new full captures, source
hashes, scripts, original manifest and verification.

## Scope and observed facts

Reuse the existing A1 diagnostic capture with only the capture-frame set expanded
from seven to nine: add f1290/43s and f1305/43.5s. Run the same full official
sample4 window, 0–56s at 2 FPS and `UNKNOWN_REVIEW`, with the unchanged Recipe
and generic detector. Existing debug projection is enabled only for the nine
captured frames; its returned detections are not modified.

The complete tracking fingerprint remains
`e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1`,
matching the original 113-row result. All seven earlier correct/wrong controls
keep their completed values. The nine captures retain 196 Oil candidates and
152 decision-witness members, joined by exact index/source/Y. Candidates absent
from a decision witness stay in the raw capture; absence is not a physical label.

| Source frame/time | Oil candidates | Current Oil | Completed/stored Oil | Publishable row hypotheses before final owner restriction | Rows matching allowed owner |
|---|---:|---:|---:|---:|---:|
| f1275 / 42.5s | 20 | unavailable | 835 | 3 | 1 |
| f1290 / 43s | 22 | unavailable | unavailable | 2 | 0 |
| f1305 / 43.5s | 21 | unavailable | unavailable | 2 | 0 |
| f1320 / 44s | 24 | unavailable | 822 (previously reviewed wrong target) | 3 | 1 |

For both missing rows, lifecycle state is `filling` / `FILL_MOTION_OWNER` and
allows only `oil-tracklet:000084:0017`. Neither frame has a publishable row in
that ID. Other retained rows belong to `...000079:0013` and `...000079:0014`.
The actual [selector](../../../src/oil_tracker/adapters/vision/oil_interface_selector.py)
constrains Oil nodes to allowed IDs before lookahead scoring. Thus **no Oil node
survives this final owner restriction**, even though some rows were publishable
before it. Completed selection is explicitly `unknown`, with selected candidate
`null`. The default selected-authority `HARD_INVALID` metric for that empty
selection must not be read as evidence that every candidate was hard invalid.

The witness's `phase_admitted`/`publishable` fields describe row membership in
the pre-restriction layers. They do not mean final allowed-owner membership or
that the human has accepted that row's physical identity. This follows the
existing [logic map](../../20-architecture/s11-current-detector-logic-map.md#44-bounded-selection-and-same-frame-projection-oil-selector-oil-projection)
and actual `OilPathLifecycleOwner.resolve` → `BoundedOilInterfaceSelector.resolve`
call path; no new interpretation or detector gate is introduced.

## What still needs physical judgment

At 43s, idx16/Y829 is an anchor-eligible member in the excluded `...0013` row.
Its scalar happens to equal the already reviewed native appearance-chain Y829.
That equality is recorded, not treated as automatic candidate identity: the
[old matcher](../../60-evidence/s11/2026-10-07-a2-patch-correspondence.md) failed
other confirmed seeds/directions and remains closed as a general repair.

At 43.5s the two nearby groups take different paths:

| Guide | Source location and captured members | Actual current route |
|---|---|---|
| ① | idx3 `oil_hypothesis`, scalar Y832; no captured native contour | `CANDIDATE_ONLY`, no admitted/publishable row |
| ② | idx8 `material_path` native central sample and scalar Y837; idx16 `calibrated_high_recall` and idx19 `phase_transition_scan`, scalar Y835 | Members of publishable `...0013`; idx8 continuation, idx16/19 anchors; excluded by allowed-owner restriction |

The second marker groups these source locations for a physical-relation review;
it is not a reviewed Y interval and does not label every other candidate in that
band. A candidate-center marker is not a native contour, and a native sector
sample does not certify the entire width or the exact center-column intersection.

The [clean/marked image](2026-10-10-cadence-gap-source-review.png) and
[frozen question](2026-10-10-cadence-gap-source-review.json) ask whether these two
locations refer to the same actual Oil surface, or which one refers to Oil if
they differ. This is a new, bounded f1305 relation question after the gap capture;
the earlier f1275 position, visible temporal continuity and displayed orange
chain questions remain closed. There is no request for pixel-perfect Y, a fitted
tolerance or wholesale video relabeling. “Neither” and “not assessable” are valid
outcomes. This review is needed before attributing **physical** loss to authority
versus the final owner restriction. The deterministic cause of empty selection
is established; the first harmful stage for actual Oil is not yet established.

Do not remove the owner filter, copy a track ID, privilege a candidate family,
relax thresholds or insert a number to meet the cadence target. Even a reply
identifying one group supplies a scoped control, not a physical classifier or
permission for an O2/O3 bypass. A successor still needs a distinct generic
observation and positive/opposing/unresolved controls under the current
[validation owner](../../30-validation/s11-interface-observability-witness-validation.md).

## Verification and retained artifacts

- Full official 113-row tracking fingerprint unchanged; nine completed raw,
  smoothed and public Oil values agree with the original stored rows.
- All 221 production source hashes remain unchanged; frozen video, original
  replay and human-reply inputs match preflight.
- All 35 old-control raster layers match their original pixel arrays, and the
  two new original ROIs exactly match the prior native context crops at offset
  (32,32). These are 37 source-raster comparisons.
- The clean review panel is an exact sixfold nearest-neighbour copy, checked
  pixel-for-pixel. No smoothing, sharpening, new contour or interpolated frame.
- All 152 decision-witness members join their same-frame raw candidates by
  original index, source and Y. Both missing frames have two pre-restriction
  publishable rows and zero members of the allowed owner.

Local artifacts remain in `sample/output/s11-cadence-gap-capture-20261010-001/`.
The reused capture script writes its manifest before printing the final summary,
so its then-open stdout log subsequently grows. The original manifest is retained;
verification records that single log-pin difference and the final log SHA. All
data/raster pins are unchanged. This has no effect on the detector/result equality.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F03`, `S11-F04`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: UNKNOWN for actual Oil pending the bounded f1305 physical-relation review. The immediate empty-selection cause is confirmed: no publishable Oil row matches the lifecycle's allowed tracklet at f1290/f1305. This does not by itself prove that the excluded rows are correct Oil.
- Logic-map impact: NONE — existing projection, row membership, owner restriction and selector are only observed; no production ownership or decision rule changes.
- Failure-registry impact: NONE — the audit narrows an existing ownership/identity seam and preserves motion, adjacency and threshold counter-controls; no new mechanism is promoted.
