# Step-12 Windows receipt — 2026-10-27

**Status: RECEIVED / NOT CONFIRMED by the frozen rule (W1 holds; W2 fails
first on 0035). The 0018 half of the question-1 reading holds; the 0035 half
is revised.** The reply to the
[step-12 fill-owner trace readout request](../../40-operations/s11-current-windows-field-qualification.md#step-12-fill-owner-trace-readout-request)
came back through the user as verbatim stdout, relayed by OCR. It is judged by
the readings frozen before its output in
[FOR-1](../../50-diagnostics/s11/2026-10-27-fill-owner-recency-local.md#windows-trace-readout--readings-frozen-2026-10-27-before-its-output).

Read-only: no detector run, no tuning. Top-exit, the fill-owner gate and the
fast-rise association stay default OFF. FIELD FAIL / O2 OPEN and review-006
pending are unchanged.

## Run and identity

| Run | Run ID | Bundle (Windows) |
|---|---|---|
| SPL4_B_ref (step 7, read only) | `005e0d58-024e-4c38-b5eb-becfc552e0cb` | `oil_level_analysis_SPL4_B_ref_20261023_150316` |

- **Run ID** equals the [step-7 receipt](2026-10-23-step7-windows-receipt.md).
- **Source:** the agent reports all three SHA-256 values matched. Two relayed
  values carry OCR-like slips: the readout tool's `…856883F…` against
  `…856b83f…` (`b`/`8`), and `s11_cadence_field.py`'s `…D20E0DB` against
  `…d28e8db` (`8`/`0`). The request said to stop on a mismatch and the tool
  ran, so these are read as OCR errors (inference; not re-hashed).
- **Readout:** BASE 20.0–28.0 s, 17 rows, all traced. H 543.4 px, so `P`
  needs recent progress ≥ 13.585 px. Readout JSON SHA-256 `7feac0a2…`
  (stays on Windows).

## Units

The confirmation frames and the recent end are **sequence offsets** at 2 fps
(`frame_offset` in `oil_interface_tracklets.py`), not source frames: the
20.0 s row's recent end is 40 and the 22.0 s row's is 44. The printed row
frame (660 at 22.0 s) is the source frame. The frozen W2 did not name the
unit. It is judged in offsets, where the 22.0 s row is 44. Compared with 660,
every row would pass trivially; that reading is not taken.

## Readings

**W1, handoff and reappearance: HOLDS.**
- 22.0 s: owner chain `0025:0018;0042:0035`, dynamic owner only `0042:0035`.
- 22.5 s: dynamic owners `0025:0018` and `0042:0035`, allowed set empty,
  `FILL_OWNER_AMBIGUOUS`. Both have an owner row (0018 Y785; 0035 Y742, Y753).

**W2, fixed fields: FAILS, first at the 22.5 s 0035 row.**
- **0018 (holds):** all 8 owner rows in 22.5–27.0 s carry fixed direction −1,
  net 21.5 px, agreement 1.0, profile `anchor_corridor`, confirmation 25–29
  (12.5–14.5 s). The confirmation ended before offset 44, so the revision
  clause for 0018 is not triggered.
- **0035 (fails):** all 5 owner rows carry fixed direction −1, net 39.0 px,
  agreement 0.75, profile `anchor_trajectory`, confirmation **44–49**
  (22.0–24.5 s). The end, 49, is not before 44. The lifecycle reads
  `confirmed` at 24.5 s. Rows from 22.0 s already carry the confirmation:
  the tracklet resolver writes the witness's fields back to every observation
  from the witness start to the confirmation offset (source,
  `oil_interface_tracklets.py`).

**W3, recent fields (reported only):**

| Tracklet | Rows in 22.5–27.0 s | `P` pass | Candidate Y over the window |
|---|---:|---:|---|
| `0025:0018` | 8 (22.5, 23.0, 23.5, 24.0, 25.5, 26.0, 26.5, 27.0) | 7 (all but 27.0) | 785 → 704–714 |
| `0042:0035` | 5 (22.5, 23.0, 23.5, 24.5, 25.0) | 2 (24.5, 25.0) | 742–753 → 708–709 |

- Both owners have a row in 3 of the 10 ambiguous frames (22.5–23.5 s); the
  other 7 have one. 0035 has no row after 25.0 s and stays a dynamic owner
  through 27.0 s (a retained chain).
- At 27.5 s only 0018 is a dynamic owner: `FILL_MOTION_OWNER`, published Y721.
- The recent direction is upward in 12 of the 13 owner rows in 22.5–27.0 s
  (0035 at 23.0 s reads +1). The owners are not stationary in this window,
  as the handoff put it. Both rise; 0018 by about 70–80 px.

## Verdict

**NOT CONFIRMED** by the frozen rule. The first failing part is W2, at 0035.

**Question-1 reading, revised:**
- **Holds:** at 22.5 s the reappearing 0018 starts a chain that is dynamic at
  once from fixed fields of a confirmation that ended at 14.5 s.
- **Revised:** 0035 is not on stale fields. It holds a fresh
  `anchor_trajectory` confirmation over 22.0–24.5 s (net 39 px upward).
- **So the ambiguity is** an old chain (0018) against a freshly confirmed
  rising tracklet (0035). Both rise during the window.
- **Not tested here:** whether either is the level. The upper provisional
  rows (FFF-1) are outside this readout.

This fits FOR-1's NO-SEP (inference): low owners rise too, so the owners' own
motion does not decide between them. The questions-2/3 desk review (A) is next.

## Relayed stdout (verbatim as relayed; OCR)

```text
fill-owner trace readout BASE 20.0-28.0 s | bundle C:\0.Coding\2.Reference\Oil level tracker\0.windows_diagnostic\bundle\step7_gate_comparison\oil_level_analysis_SPL4_B_ref_20261023_150316 | run_id 005e0d58-024e-4c38-b5eb-becfc552e0cb | H 543.3977528889886 | P progress >= 13.585 px
-- frames: time | frame | fill | oil | phase | reason | owner chain | established owner / last y | dynamic owners | allowed --
20.000 | 600 | FOAMING_VISIBLE | 801.0 | filling | FILL_MOTION_OWNER | oil-tracklet:000025:0018 | oil-tracklet:000025:0018 / 801.0 | oil-tracklet:000025:0018 | oil-tracklet:000025:0018
20.500 | 615 | PARTIAL_VISIBLE | 801.0 | filling | FILL_MOTION_OWNER | oil-tracklet:000025:0018 | oil-tracklet:000025:0018 / 801.0 | oil-tracklet:000025:0018 | oil-tracklet:000025:0018
21.000 | 630 | PARTIAL_VISIBLE | 802.0 | filling | FILL_MOTION_OWNER | oil-tracklet:000025:0018 | oil-tracklet:000025:0018 / 802.0 | oil-tracklet:000025:0018 | oil-tracklet:000025:0018
21.500 | 645 | UNKNOWN_REVIEW | None | filling | FILL_MOTION_OWNER | oil-tracklet:000025:0018 | oil-tracklet:000025:0018 / 802.0 | oil-tracklet:000025:0018 | oil-tracklet:000025:0018
22.000 | 660 | PARTIAL_VISIBLE | 756.0 | filling | FILL_MOTION_OWNER | oil-tracklet:000025:0018;oil-tracklet:000042:0035 | oil-tracklet:000042:0035 / 756.0 | oil-tracklet:000042:0035 | oil-tracklet:000042:0035
22.500 | 675 | UNKNOWN_REVIEW | None | filling | FILL_OWNER_AMBIGUOUS | - | oil-tracklet:000042:0035 / 756.0 | oil-tracklet:000025:0018,oil-tracklet:000042:0035 | (none)
23.000 | 690 | UNKNOWN_REVIEW | None | filling | FILL_OWNER_AMBIGUOUS | - | oil-tracklet:000042:0035 / 756.0 | oil-tracklet:000025:0018,oil-tracklet:000042:0035 | (none)
23.500 | 705 | UNKNOWN_REVIEW | None | filling | FILL_OWNER_AMBIGUOUS | - | oil-tracklet:000042:0035 / 756.0 | oil-tracklet:000025:0018,oil-tracklet:000042:0035 | (none)
24.000 | 720 | UNKNOWN_REVIEW | None | filling | FILL_OWNER_AMBIGUOUS | - | oil-tracklet:000042:0035 / 756.0 | oil-tracklet:000025:0018,oil-tracklet:000042:0035 | (none)
24.500 | 735 | UNKNOWN_REVIEW | None | filling | FILL_OWNER_AMBIGUOUS | - | oil-tracklet:000042:0035 / 756.0 | oil-tracklet:000025:0018,oil-tracklet:000042:0035 | (none)
25.000 | 750 | UNKNOWN_REVIEW | None | filling | FILL_OWNER_AMBIGUOUS | - | oil-tracklet:000042:0035 / 756.0 | oil-tracklet:000025:0018,oil-tracklet:000042:0035 | (none)
25.500 | 765 | UNKNOWN_REVIEW | None | filling | FILL_OWNER_AMBIGUOUS | - | oil-tracklet:000042:0035 / 756.0 | oil-tracklet:000025:0018,oil-tracklet:000042:0035 | (none)
26.000 | 780 | UNKNOWN_REVIEW | None | filling | FILL_OWNER_AMBIGUOUS | - | oil-tracklet:000042:0035 / 756.0 | oil-tracklet:000025:0018,oil-tracklet:000042:0035 | (none)
26.500 | 795 | UNKNOWN_REVIEW | None | filling | FILL_OWNER_AMBIGUOUS | - | oil-tracklet:000042:0035 / 756.0 | oil-tracklet:000025:0018,oil-tracklet:000042:0035 | (none)
27.000 | 810 | UNKNOWN_REVIEW | None | filling | FILL_OWNER_AMBIGUOUS | - | oil-tracklet:000042:0035 / 756.0 | oil-tracklet:000025:0018,oil-tracklet:000042:0035 | (none)
27.500 | 825 | FILLING_VISIBLE | 721.0 | filling | FILL_MOTION_OWNER | oil-tracklet:000025:0018 | oil-tracklet:000025:0018 / 722.0 | oil-tracklet:000025:0018 | oil-tracklet:000025:0018
28.000 | 840 | FILLING_VISIBLE | 704.0 | filling | FILL_MOTION_OWNER | oil-tracklet:000025:0018 | oil-tracklet:000025:0018 / 707.5 | oil-tracklet:000025:0018 | oil-tracklet:000025:0018
-- owner rows (one per tracklet and frame): time | frame | tracklet | candidate ys | any selected | lifecycle | admitted | profile | confirmation start / end | fixed dir / net / agree | recent dir / net / agree | recent end | motion support / coverage | P | dynamic --
20.000 | 600 | oil-tracklet:000025:0018 | 801.0 | True | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | 1 / 7.0 / 0.75 | 40 | 0.5210024437685166 / 0.8 | False | True
20.500 | 615 | oil-tracklet:000025:0018 | 801.0 | True | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | 1 / 8.0 / 1.0 | 41 | 0.33764395320247875 / 0.7333333333333333 | False | True
21.000 | 630 | oil-tracklet:000025:0018 | 802.0 | True | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | 1 / 7.5 / 1.0 | 42 | 0.13773843293585836 / 0.5333333333333333 | False | True
21.000 | 630 | oil-tracklet:000042:0035 | 749.0 | False | provisional | 0.0 | none | - / - | 0 / 0.0 / 0.0 | 0 / 0.0 / 0.0 | 42 | 0.0 / 0.0 | False | False
21.500 | 645 | oil-tracklet:000025:0018 | 802.0 | False | continuing | 0.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | 1 / 3.0 / 1.0 | 43 | 0.023846921348169396 / 0.3333333333333333 | False | True
21.500 | 645 | oil-tracklet:000042:0035 | 740.0 | False | provisional | 0.0 | none | - / - | 0 / 0.0 / 0.0 | 0 / 0.0 / 0.0 | 43 | 0.0 / 0.0 | False | False
22.000 | 660 | oil-tracklet:000042:0035 | 756.0 | True | provisional | 1.0 | anchor_trajectory | 44 / 49 | -1 / 39.0 / 0.75 | 1 / 7.0 / 0.5 | 44 | 0.710298112124143 / 0.72 | False | True
22.500 | 675 | oil-tracklet:000042:0035 | 742.0,753.0 | False | provisional | 1.0 | anchor_trajectory | 44 / 49 | -1 / 39.0 / 0.75 | -1 / 1.5 / 0.6666666666666666 | 45 | 0.710298112124143 / 0.72 | False | True
22.500 | 675 | oil-tracklet:000025:0018 | 785.0 | False | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | -1 / 16.0 / 0.75 | 45 | 0.21719260036051508 / 0.4 | True | True
23.000 | 690 | oil-tracklet:000042:0035 | 757.0,758.0,769.0 | False | provisional | 1.0 | anchor_trajectory | 44 / 49 | -1 / 39.0 / 0.75 | 1 / 9.0 / 0.5 | 46 | 0.710298112124143 / 0.72 | False | True
23.000 | 690 | oil-tracklet:000025:0018 | 781.0 | False | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | -1 / 20.0 / 0.75 | 46 | 0.41687673564416905 / 0.5333333333333333 | True | True
23.500 | 705 | oil-tracklet:000025:0018 | 757.0,765.0,766.0 | False | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | -1 / 37.0 / 1.0 | 47 | 0.6002352262102068 / 0.6 | True | True
23.500 | 705 | oil-tracklet:000042:0035 | 742.0 | False | provisional | 1.0 | anchor_trajectory | 44 / 49 | -1 / 39.0 / 0.75 | -1 / 7.0 / 0.6 | 47 | 0.710298112124143 / 0.72 | False | True
24.000 | 720 | oil-tracklet:000025:0018 | 756.0 | False | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | -1 / 46.0 / 1.0 | 48 | 0.7781407464768273 / 0.76 | True | True
24.500 | 735 | oil-tracklet:000042:0035 | 717.0 | False | confirmed | 1.0 | anchor_trajectory | 44 / 49 | -1 / 39.0 / 0.75 | -1 / 39.0 / 0.75 | 49 | 0.710298112124143 / 0.72 | True | True
25.000 | 750 | oil-tracklet:000042:0035 | 708.0,708.0,709.0 | False | continuing | 1.0 | anchor_trajectory | 44 / 49 | -1 / 39.0 / 0.75 | -1 / 39.5 / 0.75 | 50 | 0.656378362907842 / 0.6799999999999999 | True | True
25.500 | 765 | oil-tracklet:000025:0018 | 714.0,719.0 | False | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | -1 / 64.5 / 1.0 | 51 | 0.7225 / 0.7 | True | True
26.000 | 780 | oil-tracklet:000025:0018 | 715.0,722.0,722.0 | False | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | -1 / 43.0 / 0.6666666666666666 | 52 | 0.47253431284334513 / 0.5 | True | True
26.500 | 795 | oil-tracklet:000025:0018 | 721.0,723.0 | False | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | -1 / 34.0 / 0.6666666666666666 | 53 | 0.22253431284334513 / 0.25 | True | True
27.000 | 810 | oil-tracklet:000025:0018 | 704.0,710.0,714.0 | False | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | -1 / 6.5 / 0.6666666666666666 | 54 | 0.10670945709823723 / 0.2 | False | True
27.500 | 825 | oil-tracklet:000025:0018 | 715.0,721.0,723.0,724.0 | True | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | 1 / 5.5 / 0.75 | 55 | 0.15663559043361813 / 0.27999999999999997 | False | True
28.000 | 840 | oil-tracklet:000025:0018 | 704.0,705.0,710.0,711.0 | True | continuing | 1.0 | anchor_corridor | 25 / 29 | -1 / 21.5 / 1.0 | -1 / 9.0 / 0.6 | 56 | 0.2605296586946818 / 0.3333333333333333 | False | True
json fill_owner_trace_readout.json sha256 7feac0a29ff8b362edb64acf06a353ce2b3909059ba4bf813e14e61bd51d08bd
```

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`
- First harmful stage: SPL#4 2 fps 22.5–27.0 s is `OIL-PHASE-FILL` `FILL_OWNER_AMBIGUOUS` between a reappearing 0018 chain on fixed fields from a confirmation that ended at 14.5 s and a freshly confirmed rising 0035 (confirmation 22.0–24.5 s), both rising; read from the relayed trace. Upstream, the rising level is not an admitted `OIL-TRACKLET` owner (FFF-1).
- Existing feature coverage: reads the saved step-7 `SPL4_B_ref` FULL trace (IFO v2 + top-exit v3 arm, 2 fps) with a read-only tool; the recent-motion `P` is the lifecycle's existing refill-witness test, used only as a reading.
- Execution scope: one read-only Windows readout of a saved bundle (run `005e0d58…`); no detector run, user review, tuning, flag or threshold change.
- Logic-map impact: NONE — a receipt; detector code and owners are unchanged.
- Failure-registry impact: NONE — fits `S11-F04` (stale continuation) and `S11-F05` (EMPTY-phase ownership); `S11-F02` stays open.
