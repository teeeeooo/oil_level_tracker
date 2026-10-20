# LBQ-1 — layer-bottom-qualified ordered-lower authority

**Status: FROZEN — approved by the user 2026-10-20; tool `tests/diagnostics/s11_layer_bottom_qualified_authority.py` committed with this text before any run.** Base HEAD:
`cc503bf`. Current authority: [Work Plan](../../00-project/work-plan.md). This is
step 2 of the [ARV-1 recommendation](2026-10-20-approach-review.md#recommendation),
updated by [review-010](2026-10-20-approach-review.md#review-010-result).

## Question

In layered Foam, can the unchanged [LBW-3 unit](2026-10-20-layer-bottom-witness-3.md#changed-unit-one-change-only)
give the Oil/Foam layer bottom ordered-lower anchor authority, without the
Foam top demoting it? And what does the full pipeline then publish?

Known blockers at the reviewed frames:
- **Support:** texture-only peer exclusion sets cross-representation support to
  0 (AAT-1, ATG-1 673–677 s).
- **Nearest anchor:** the topmost ordered-lower anchor wins. At Windows 677 s
  that anchor is the **air–Foam top** Y235 (review-010).
- **Later layers (TPA-1):** a new anchored tracklet may not be admitted against a
  mature continuation owner; fill-chain ambiguity may suppress output. LBQ-1
  observes these layers but does not change them.

## Witness (unchanged)

The LBW-3 unit, tool `87817ad`: the row witness of LBW-2 on `foam_combined_evidence`,
`effective_mask` and `glare_mask`; the frame's first `INTERFACE_SUPPORTED` Oil
candidate at Y = B; the unit is every supported candidate with Y ≤ B + tol
(same-boundary tolerance, 12 px on sample4 and Windows Accum). No constant,
window, sector count or tolerance changes.

Unit membership is attached to each Oil candidate as the inert feature
`diagnostic_lbw3_unit` (1.0 or 0.0). No production code reads it.

## Consumers (diagnostic wrapper, two only)

Both act only when the frame's unit is non-empty. With an empty unit (including
every `UNRESOLVED` frame such as Windows 678.5/679 s), behaviour is exactly
the current one.

1. **Support (`OIL-AUTHORITY`)** — LBW-1 consumer 1 with the unit in place of
   `INTERFACE_SUPPORTED`. In `_cross_representation_support`, a peer excluded
   *only* by `material_texture_conflict >= 0.60` counts when both the candidate
   and the peer are in the unit. Artifact/optics exclusions, the family and
   `calibrated_raster` rules, the tolerance and the formula are unchanged.
2. **Nearest anchor (`OIL-AUTHORITY`)** — LBW-1 consumer 2, changed by
   review-010. In `_demote_non_nearest_ordered_lower_anchors`, if any anchor is
   in the unit, "first" is the topmost unit anchor. Anchors above it that are
   **not in the unit** are demoted with the existing
   `NON_NEAREST_ORDERED_LOWER` record and failed gate
   `above_supported_layer_bottom`. Anchors below it keep the existing rule.
   - **Why changed:** LBW-1 demoted only upper anchors read as
     `INTERNAL_OR_ARTIFACT`. The reviewed Windows 677 s upper anchor is the
     air–Foam top, which the witness does not read as interior.
   - **Risk accepted before running:** a true Oil anchor above a wrongly
     supported bottom would be demoted. On held-out data the unit held 0/24
     negatives, and none on sample4.

LBW-1 consumer 3 (a new layer-interior contradiction) is **not** included. It
needs a new production enum, and LBQ-1 first tests whether anchors alone change
publication.

**Unchanged:** every identity gate, the `material_layer_terminal`
CANDIDATE_ONLY rule, top-K, tracklet admission, fill-chain ambiguity, the
selector and every Foam owner.

## Execution

A diagnostic wrapper, like TPA-1. No production change, no option and no
Recipe change.
- **sample4 (development):** one run of the existing production analysis
  captures the detector rasters, computes the unit for all 113 frames, and must
  equal the saved P5 fingerprint. Captured candidates must match the saved
  `raw.json` candidates in kind, source and Y, frame by frame. The unit is then
  attached to the saved raw rows. The baseline plus the frozen 245 SOI
  withdrawals run under the wrapper. A withdrawal does not recompute the unit;
  the unit is a raster property of the frame.
- **Descriptive:** `base_sample_1` 0–14.4 s and `sample2` 0–2 s through the
  ordinary analysis entry, with the unit computed live. Sample3 stays
  quarantined.
- **Windows (S2):** not part of this approval. See [below](#windows-stage-s2).

**Contract checks before the results are read:**
- Focused tests: with both consumers off, the wrapper copies equal the
  originals; the inert feature alone changes nothing; consumer 1 counts only a
  unit–unit texture peer; consumer 2 demotes an upper non-unit anchor and leaves
  an empty-unit frame unchanged.
- The existing resolver and phase suites under the wrapper, with the activation
  count reported.
- sample4: the ordinary rows and events reproduce the saved SOI records; every
  provenance join and event link verifies.

## Pre-registered evaluation (sample4)

Use TPA-1's evaluation unchanged: the [P0 C1 band](../../30-validation/s11-interface-observability-witness-validation.md#local-residual-bounds-and-extremum-display--2026-10-20)
±5.2 px and the 13 frozen SOI controls.
- **Accepted:** 38 s Y844, 40 s Y841, 42 s Y839, 42.5 s Y835, 44 s Y844,
  52 s Y833, plus the 49.5 s practical approximation Y841.
- **Opposed:** 38 s Y880/882/887, 40 s Y865.5, 42 s Y868, 44 s Y822, and
  TPA-1's 42 s Y805.
- **User-confirmed wrong (CAF-1):** 51.0–52 s Y861.5–862.

Baseline under LBQ-1 against the ordinary baseline: control preservation,
replacements, report extrema (no new extremum outside C1 of a reviewed
positive; no H3 54.5 s +45 px), gaps (C3 or no worse) and Foam (any change is
F06). All 246 conditions are classified A/B/C/U, and every changed case is
rendered.

**Layer report (the mechanism question).** For each frame where the unit is
non-empty, report:
- whether a unit candidate became an anchor (consumer 1);
- which anchors were demoted (consumer 2);
- the published Oil, its tracklet's authority and admission, and the
  fill-chain state.

## Stop and outcome rules

**Closed without promotion** on any of:
- a failed hard contract (copy equality, inert feature, provenance, focused
  tests);
- a named opposed or wrong target newly selected, or a reviewed positive
  replaced outside C1 with an extremum or direction change;
- a Foam coordinate or episode boundary changed.

**Outcome classes, if no stop rule fires:**
- **P — publication recovered:** the reviewed positives are published within
  C1 where the baseline was wrong or missing. Then S2 may be proposed.
- **L — anchors fixed, selection still wrong:** unit anchors exist and upper
  anchors are demoted, but a continuation owner is still published. LBQ-1
  closes, and the next layer is anchor-versus-continuation selection (ARV-1
  step 2). That layer would also cover Windows 678.5/679 s.
- **N — no anchor change:** consumers do not change authority at the reviewed
  frames. LBQ-1 closes, and the cause is recorded.

No tuning, widening, consumer 3, or time/Y/Glass exception follows the results.
A new definition is a new, separately frozen protocol.

## Windows stage (S2)

Only after outcome P, and only with a separate user go:
1. **review-011 first:** a human review of the unread layered-Foam frames that
   ATG-1 captured in 672–677.5 s, through the O2 workflow. It is completed and
   recorded before any LBQ-1 output is seen. These frames are the held-out set.
2. Then the wrapper runs with the ④ settings on the same video, Recipe, ROI and
   window. It is judged on the review-011 frames (held out) and on
   review-009/010 (development). All nine segments are reported. Windows
   678.5/679 s must stay unchanged; the 721 s false anchor and the 723/771 s
   protections are reported.

S11 ACTIVE / O2 OPEN / FIELD FAIL is unchanged by any local result.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F01`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: `OIL-AUTHORITY` — texture-excluded support, then nearest-ordered-lower demotion under the air–Foam top (AAT-1, TPA-1, ATG-1, review-010).
- Existing feature coverage: reuses the LBW-3 witness unchanged, LBW-1 consumers 1–2 (consumer 2 condition changed by review-010), the TPA-1 wrapper pattern, the CAF-1/SOI runner, P0 bounds and SOI controls. The material-layer, identity, admission, phase and Foam owners are unchanged.
- Execution scope: planned — sample4 baseline plus 245 SOI conditions (development) and base_sample_1/sample2 descriptive, diagnostic wrapper only; Windows S2 needs a separate go.
- Logic-map impact: NONE — diagnostic wrapper; no source change.
- Failure-registry impact: NONE — a draft diagnostic with no runtime mechanism; any stop result is recorded here.
