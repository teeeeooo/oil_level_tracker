# LBW-1 — Foam layer-bottom witness

**Status: CLOSED WITHOUT PROMOTION — S0 FAILED ON SAMPLE4** ([result](#s0-result)). Protocol base HEAD: `9af5483`. Current authority:
[Work Plan](../../00-project/work-plan.md). The user chose this direction after
[ATG-1](2026-10-20-accum-texture-gate.md#decision). This document fixes the
witness definition, its consumers, stages, controls and stop rules before any
output exists. No production code changes until S0 passes.

## Question and mechanism evidence

Two recordings now show the same two-layer failure while Foam lies over Oil:

| Layer | sample4 | Windows Accum (ATG-1) |
|---|---|---|
| 1. Texture-excluded support | AAT-1: accepted boundary rows get support 0.00 (conflict 0.60–0.75) | 673–677 s: every reviewed top-K boundary row gets support 0.00 (conflict 0.60–0.77) |
| 2. Upper owner wins | TPA-1: with support restored, a continuation owner above the boundary (Y805) is selected | 677–679 s: an upper ordered-lower anchor (Y235, Y229) demotes the boundary (`nearest_ordered_lower_interface`); output follows upper rows 177–184 px above it |

Both layers come from one assumption. The detector assumes the first ordered-lower
row below the Foam front is the Oil boundary (`_demote_non_nearest_ordered_lower_anchors`
keeps only the topmost anchor). But the Foam layer has thickness, and its interior
rows are ordered-lower too. What separates the boundary from the interior is a
quantity the detector does not represent: **the bottom of the textured layer**.

The only current proxy is the whole-row scalar `material_terminal_partition_support`.
It is 0.91–1.00 on all nine reviewed Windows boundary rows and 1.00 on sample4's
accepted controls, and 0.00 on most interior rows and wrong targets. It is not a
complete discriminator: the Windows upper anchor Y229 has 0.68, the 679 s upper rows
0.36–0.52, and sample4's pre-Foam 38 s lower rows 1.00. TPA-1 showed that a scalar
exemption alone reproduces layer 2. More scalar stacking on sample4 alone was
judged an overfitting risk; this design is evaluated on both recordings.

## Witness definition (fixed)

This narrows item 1 of the [physical-interface repair design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#1-interface-evidence-and-independence)
(typed interface witness replacing broad-texture vetoes) to one physical role: the
bottom of a textured material layer. All numbers reuse existing constants.

**Inputs (per frame, per Oil candidate):** the material evidence map that
`material_layer_context_features` already reads (`foam.combined_evidence_map`,
saved in traces as `foam_combined_evidence`), `visible = effective & ~glare`, and the
candidate's ROI-local row `y`. The column range and five equal sectors are those of
`generate_material_path_candidates`.

**Per sector s:** column-mean profile `P_s(r)` as `_material_row_profile` restricted
to the sector's visible columns; normalized texture `n_s(r) = unit(P_s(r) / 0.42)`
(the existing row-support normalization), smoothed over ±2 rows (the existing
row-support band). With `d = max(4, round(0.16 × profile height))` (middle of the
existing terminal depth ratios 0.10/0.16/0.22), test rows `y' ∈ [y−2, y+2]`:
- **upper textured:** mean `n_s` over `[y'−d, y'−1]` ≥ 0.60 (the existing
  "inside texture" limit);
- **lower clean:** max `n_s` over `[y'+1, y'+d]` < 0.60, meaning no textured row
  within depth `d` below.

Sector state: `TERMINAL` if some `y'` satisfies both; `INTERIOR` if upper textured
holds but every `y'` fails lower clean; `UNAVAILABLE` if fewer than 50 % of the
sector's columns are visible or either side has fewer than 3 rows; otherwise `OTHER`.

**Decision** (3 = the architecture's distributed-sector count):
- `INTERFACE_SUPPORTED`: at least 3 sectors `TERMINAL`;
- `INTERNAL_OR_ARTIFACT`: at least 3 sectors `INTERIOR`;
- `UNRESOLVED`: otherwise, including any missing input.

The witness is a property of the row, not of the generator. Every family at the same
row reads the same raster. It therefore grants **no independent vote**; it only
qualifies whether the texture veto applies. Unlike CRW-1's gray-band partition count
(which f1200's lower structure Y865.5 passes), it reads material texture on both
sides. A lower vessel structure has clean Oil above it, so it cannot be `TERMINAL`.

## Consumers (S1 only, default OFF)

All three act only in the existing ordered-lower context (Foam material row present,
candidate ordered-lower, Foam seed ≤ 3 s). Outside it, and whenever the witness is
`UNRESOLVED`, behavior is exactly the current one.

1. **Support (`OIL-AUTHORITY`).** In `_cross_representation_support`, a peer excluded
   only by `material_texture_conflict >= 0.60` counts when both candidate and peer
   are `INTERFACE_SUPPORTED`. Artifact/optics exclusions, family rules, tolerance
   and the support formula are unchanged.
2. **Nearest anchor (`OIL-AUTHORITY`).** In `_demote_non_nearest_ordered_lower_anchors`,
   if any anchor is `INTERFACE_SUPPORTED`, "first" is the topmost **supported**
   anchor. Anchors above it that are `INTERNAL_OR_ARTIFACT` are demoted with the
   existing `NON_NEAREST_ORDERED_LOWER`-style record (new failed gate
   `layer_interior_above_supported_bottom`). With no supported anchor, the legacy
   rule applies.
3. **Layer interior (`OIL-PHASE-FILL` via the existing typed channel).** When a
   frame has an `INTERFACE_SUPPORTED` ordered-lower anchor, every Oil ref above it
   and below the Foam material row whose witness is `INTERNAL_OR_ARTIFACT` gets a
   new `OilIdentityContradiction.LAYER_INTERIOR`. Phase lifecycle already reads
   identity contradictions (`contradicted_owner_ids`, chain reset). No new
   selector rule or hard invalidation is added.

**Explicitly unchanged:** the `material_layer_terminal` CANDIDATE_ONLY rule (it made
Windows 675 s idx10 candidate-only; its intent needs separate history review),
top-K pruning, tracklet admission, fill-chain ambiguity, every Foam owner, and the
Foam-collapse targets (air–liquid top / liquid–liquid layer). Observing the
admission and fill-chain layers is part of S1; changing them is not.

## Stages

**S0 — descriptive witness screen, no consumer.** Compute the witness on saved
rasters only. It decides whether S1 may be implemented.
- *sample4:* one FULL-trace run of the existing production analysis on `sample4.mp4`
  0–56 s at 2 Hz with the saved P5 Recipe/session, options OFF, in a new managed
  run. Its rows must equal the saved P5 baseline rows; otherwise stop (input
  mismatch).
- *Windows:* the read-only ④ trace (`trace=full`) through the extraction tool path
  used in ATG-1, extended to read `foam_combined_evidence`, `effective_mask` and
  `glare_mask` PNGs. No run.
- *Self-check (both):* recompute the existing whole-row `raw_material_row_support`
  and `material_terminal_partition_support` from the saved PNGs and compare them
  with the stored features. Tolerance: 0.03 for each (8-bit quantization of a [0,1]
  map). If more than 5 % of read candidates mismatch, the S0 input is invalid: stop.

**S1 — local consumer replay.** Only if S0 passes. Implement the witness at the
frame-evidence seam where `material_layer_context_features` is computed, behind a
default-OFF option, with all three consumers. OFF must be byte-equal on the full
unit suite and the saved sample4 rows. Run sample4 (baseline plus the frozen SOI
population, if the witness can be carried on reused acquisition; otherwise the
baseline only, stated), and `base_sample_1` 0–14.4 s / `sample2` 0–2 s
descriptively. Sample3 stays quarantined.

**S2 — Windows comparison.** Only after S1 passes, and only with a separate user go:
④ settings plus the option, same video/Recipe/ROI/window. It is evaluated on
review-009 (673–678.5 s decision frames), review-004/005 allowances, the 721 s false
anchor and the 723/771 s protections, and all nine segments reported.

## Pre-registered controls

**Positives** (reviewed boundary under Foam):
- sample4 accepted controls under Foam: 40 s Y841, 42 s Y839 (rows Y835/837),
  42.5 s Y835, 44 s Y844, 52 s Y833, 49.5 s practical Y841;
- Windows review-009 interface candidates at 673/675/677/678.5 s (idx sets as
  recorded; Y490–498 / 444–453 / 415).

**Negatives** (must never be `INTERFACE_SUPPORTED`):
- sample4: 42 s Y805 (TPA-1), 42 s Y868, 40 s Y865.5, 44 s Y822, 51–52 s Y861.5–862 (CAF-1);
- Windows: 677 s Y235 and 678.5 s Y229 (interior anchors), selected Y317/269/238 at
  675/677/678.5 s, and the table B interior rows at 673–677 s.

**Report only:** sample4 38 s Y880–887 (pre-Foam, outside the ordered-lower scope);
Windows 679/684 s (Foam-collapse transition).

## Pass and stop rules

**S0 passes only if all hold:**
1. No negative is `INTERFACE_SUPPORTED` (zero tolerance).
2. **Decisive pairs:** Windows 677 s (a reviewed boundary row supported, Y235 not),
   Windows 678.5 s (Y415 supported, Y229 not), sample4 42 s (Y835 or Y837 supported;
   Y805 and Y868 not).
3. In each recording separately, at least 80 % of positive frames have a supported
   reviewed candidate.
4. The self-check is valid.

**S1 stops (closed without promotion) on any of:**
- OFF not byte-equal, or failed provenance/focused tests;
- a named negative newly selected, or a reviewed positive replaced outside the
  [P0 C1 band](../../30-validation/s11-interface-observability-witness-validation.md#local-residual-bounds-and-extremum-display--2026-10-20)
  with an extremum or direction change;
- a Foam coordinate or episode boundary changed;
- any public output change on `base_sample_1`/`sample2` without a reviewed reason.

S1 reports, for every changed case: activation count per consumer, tracklet
admission and fill-chain outcome at the recovered frames (TPA-1's remaining
layers), and A/B/C/U against the baseline.

**No tuning.** On failure, record and stop. Do not change `d`, 0.42, 0.60, ±2,
the 3-sector count or the scope, and do not add a time/Y/Glass exception. A new
definition would be a new, separately frozen protocol.

S11 ACTIVE / O2 OPEN / FIELD FAIL is unchanged by any local result.

## S0 result

Executed once with tool `c2b9865`, committed before the run. Managed run
`sample/output/s11-layer-bottom-witness-20261020-001` is closed. Evidence:
`evidence/sample4-s0.json`, 18.6 kB, SHA-256
`57a1b22a28c13acdef61cac5eb4d3841e964b0ba55e1e5457dfb758fdf7469fe`. The BASIC
trace was discarded.

**Input checks pass.** The sample4 tracking fingerprint equals the saved P5 baseline
(`e447626b…`). The self-check recomputes the stored whole-row features from the
same rasters with 0/196 mismatches.

| Rule | Result |
|---|---|
| 1. No negative supported | **PASS:** 42 s Y805 is `INTERNAL`; 42 s Y867/868, 40 s Y865.5 and 51–52 s Y861.5–862 are `UNRESOLVED`; 44 s Y821/822 is `INTERNAL` |
| 2. Decisive 42 s pair | **FAIL:** Y835/837 are `INTERNAL` (T0–1 / I4–5). Only the hypothesis rows Y839/Y844 are supported (T3 I2) |
| 3. Positive frames ≥ 80 % | **FAIL:** 2/6 (42 s via Y839/844; 49.5 s via `material_path` Y841). 40, 42.5, 44 and 52 s have every in-band candidate `INTERNAL` |
| 4. Self-check | PASS (valid) |

Report-only: the pre-Foam 38 s Y880 and Y887 are `INTERFACE_SUPPORTED`. They lie
outside the ordered-lower scope, but they confirm that this witness alone does not
mark a Foam boundary.

**Why it fails (post-hoc observation, no tuning).** The sample4 ROI is 104 px high,
so `d = 17`. At 42 s the central sectors' texture falls from 0.77–0.81 at Y839 to
0.02–0.14 at Y845–855. It rises again to 0.41–0.98 at Y860–870, the lower vessel
structure (the 42 s Y868 target). The clean Oil band between the Foam bottom and
that structure is about 15 px, thinner than `d`. "No textured row within `d`
below" therefore fails on the real boundary. The two edge sectors stay textured
at 0.54–0.89 through the whole band (wall texture), so at most three sectors can
ever be `TERMINAL`. The relative whole-row scalar (upper mean minus lower mean)
still reads 1.00 here, because it compares averages instead of requiring absence.

**Decision.** S0 fails on sample4, so the frozen rule stops LBW-1 regardless of
Windows. No consumer is implemented, and no Windows S0 extraction is requested.
`d`, the limits and the sector count stay as frozen. Choosing a smaller depth now
would be fit to this sample4 band.

**What carries forward.**
- Negatives were never supported. In particular, Y805 (TPA-1) was
  `INTERNAL_OR_ARTIFACT` and lower structures were `UNRESOLVED`, so an
  interior-versus-bottom distinction is measurable.
- The failure mode is a thin Oil band between two textured regions. Any successor
  definition must hold when the Oil band is thinner than any fixed depth.
- The Windows ④ trace has not yet been read with any witness. It can serve as a
  held-out check for a successor definition frozen before reading it.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: `OIL-AUTHORITY` — texture-excluded cross-representation support, then nearest-ordered-lower demotion under an upper anchor inside the Foam layer (AAT-1, TPA-1, ATG-1).
- Existing feature coverage: reuses the existing material evidence map, row-support normalization (0.42), texture limit (0.60), terminal depth ratios, five-sector grid, ordered-lower context and typed identity-contradiction channel; the physical-interface design's witness contract. CRW-1's gray partition count is not reused as authority (f1200 counterexample). S0 inputs: a new sample4 FULL-trace run of the saved P5 configuration (options OFF), and the ④ FULL+ON v2 saved trace (spatial Artifact templates as recorded for ④; cost-first/RGB/Local XY/top-exit OFF).
- Execution scope: S0 sample4 only — the existing production analysis (P5 configuration, options OFF, BASIC trace in a temporary directory) with witness evaluation on detector-artifact rasters; no detector consumer. Windows S0, S1 and S2 were not run.
- Logic-map impact: NONE — diagnostic screen only; production source and ownership unchanged.
- Failure-registry impact: NONE — a closed diagnostic screen with no runtime mechanism; the counterexample is recorded here.
