# LBT-1 — layer-bottom topology in the ordered-lower context

**Status: CLOSED WITHOUT PROMOTION — stop rules fired on sample4; the baseline improves and shows outcome G ([result](#results-and-decision)).** Frozen and approved by the user 2026-10-20; tool `tests/diagnostics/s11_layer_bottom_topology.py` (`142ec42`) committed with this text before any run. Base HEAD:
`a7fa2e4`. Current authority: [Work Plan](../../00-project/work-plan.md). This
protocol implements the [SFR-1 recommendation](2026-10-20-selection-fill-review.md#recommendation).

## Question

[SFR-1](2026-10-20-selection-fill-review.md#finding-1--both-lbq-1-failures-come-from-one-mixed-identity-owner)
found that one Oil physical ID alternates between rows above the Foam material
row and the layer bottom. In LBQ-1, anchors on its bottom rows made it published
(42.5 s Y805) and fill-confirmed (48.5 s).

LBT-1 asks: while Foam is layered and the witness supports a layer bottom, does
removing every Oil row above that bottom stop the mixing? And does Oil then
publish the layer bottom?

## Witness (unchanged)

The [LBW-3 unit](2026-10-20-layer-bottom-witness-3.md#changed-unit-one-change-only),
tool `87817ad`, computed as in LBQ-1. B is the frame's topmost unit row. Two
inert features are attached to every Oil candidate:
- `diagnostic_lbw3_unit`: 1.0 or 0.0;
- `diagnostic_lbw3_unit_top`: B, or absent when the unit is empty.

No production code reads either feature.

## Changes (diagnostic wrapper)

**Ordered-lower context (frame).** Both changes use only existing values:
- a Foam material identity row R exists;
- its seed age is ≤ 3 s (the existing `ORDERED_LOWER_INTERFACE` limit);
- the unit is non-empty;
- B ≥ R + the existing lower separation.

Outside the context, behaviour is exactly the current one. This includes
pre-Foam frames and every frame with an empty unit, such as Windows 678.5/679 s.

1. **E1 — topology (`OIL-AUTHORITY`).** In context, an Oil candidate with
   Y < B gets `HARD_INVALID` from `evaluate_candidate_authority`
   (reason `ineligible`, failed gate `above_layer_bottom`). The existing path
   then drops it from refs, tracklets, fill chains and selection. Candidates at
   or below B are untouched.
2. **Support (`OIL-AUTHORITY`)** — LBQ-1 consumer 1, now limited to the
   context. A peer excluded *only* by `material_texture_conflict >= 0.60` counts
   when both the candidate and the peer are in the unit **and** the candidate is
   ordered-lower (`composition_lower_reserve`, the existing flag). This closes
   LBQ-1's disclosed scope gap.

**Dropped:** LBQ-1 consumer 2 (unit-qualified nearest anchor). It never activated
on sample4. Under E1, no anchor above B can exist, so its Windows 677 s case is
covered. Keeping it would add a second path for the same effect.

**Unchanged:** the witness, every other authority and identity gate, the
`material_layer_terminal` rule, tracklet association, fill chains and
confirmation (0.27 entrance band, 20 % span), selection and every Foam owner.

**Accepted risks, recorded before running:**
- **Wrong unit:** a true Oil row above it would be removed. Held-out evidence is
  0/24 negatives, and E1 applies only in context.
- **Fill geometry ([SFR-1 finding 2](2026-10-20-selection-fill-review.md#finding-2--the-unit-marks-a-role-band-not-a-position)):**
  B reaches Y820–826 inside the sample4 entrance band. An in-unit anchored chain
  may still confirm a fill.

## Execution

As in LBQ-1, with the same runner:
- **sample4 (development):** capture and P5 fingerprint check, candidates equal
  to `raw.json`, then the baseline plus the frozen 245 SOI withdrawals under the
  wrapper.
- **Descriptive:** `base_sample_1` 0–14.4 s and `sample2` 0–2 s through the
  ordinary analysis entry. Sample3 stays quarantined.
- **Windows:** not part of this approval.

**Contract checks before the results are read:**
- Focused tests:
  - with both changes off, the copies equal the originals;
  - the inert features alone change nothing;
  - E1 invalidates a row above B only in context, and never a row at or below B;
  - out-of-context frames (no Foam row, old seed, empty unit, B above R + separation) are unchanged;
  - consumer 2's absence is confirmed.
- The existing resolver, phase, authority and tracklet suites under the wrapper,
  with activation counts.
- sample4: ordinary rows/events reproduce the SOI records; provenance and event
  links verify.

## Pre-registered evaluation

LBQ-1's evaluation unchanged:
- [P0 C1](../../30-validation/s11-interface-observability-witness-validation.md#local-residual-bounds-and-extremum-display--2026-10-20)
  ±5.2 px;
- accepted 38 s Y844, 40 s Y841, 42 s Y839, 42.5 s Y835, 44 s Y844, 52 s Y833,
  49.5 s practical Y841;
- opposed 38 s Y880/882/887, 40 s Y865.5, 42 s Y868, 44 s Y822, 42.5 s Y805;
- wrong 51–52 s Y861.5–862;
- extrema, gaps, Foam, and A/B/C/U for all 246 conditions.

**Layer report per in-context frame:**
- E1 removed rows;
- any tracklet holding rows both above R and in the unit (the SFR-1 mixing;
  expected none);
- each fill chain's profile and last row relative to B;
- the published row, its authority and lifecycle.

## Stop and outcome rules

**Closed without promotion** on any of:
- a failed hard contract;
- a named opposed or wrong target newly selected;
- a reviewed positive replaced outside C1 with an extremum or direction change;
- a Foam coordinate or episode boundary changed.

**Outcome classes:**
- **P — publication recovered, no stop rule.** S2 may be proposed.
- **G — fill geometry.** A fill is confirmed by a chain whose rows are in-unit.
  It closes and names the next question: the entrance band in a layered Glass.
  E1 is not widened.
- **M — mixing persists.** A tracklet still holds rows on both sides inside the
  context. It closes, and the remaining route is recorded.
- **L — other later owner.** Mixing is gone and no fill is confirmed, but
  publication is still wrong. It closes, and the owner is recorded.

No tuning, widening, re-adding consumer 2, or time/Y/Glass exception follows
the results.

## Windows stage (S2)

As in [LBQ-1](2026-10-20-layer-bottom-qualified-authority.md#windows-stage-s2):
only after P, and only with a separate user go. Review-011 of the unread 672–677.5 s
layered frames comes first (held out), then the ④-settings run. Windows
678.5/679 s must stay unchanged, and all nine segments are reported.

S11 ACTIVE / O2 OPEN / FIELD FAIL is unchanged by any local result.

## Results and decision

Tool `142ec42`. Managed run `sample/output/s11-layer-bottom-topology-20261020-001`
(closed; 10 files kept, the ordinary baseline render reused from SOI).
`comparison.json` SHA-256 `8d9d6e4ffb50cd71c9cb5c18bb8992ce6214e220c49e8a36ab8ca98de0340952`;
`layers.json` SHA-256 `01ae0cea3047a690c13297fd50d1f5bffbddfc96be434d5b4a4a9ce7a46a0d0c`.

**Contracts: all PASS.**
- Focused tests: 13 PASS.
- Resolver, phase, authority and tracklet suites under the wrapper: 257 PASS
  with zero activations.
- sample4 capture equals P5. Captured candidates equal `raw.json` in all 113
  frames. The inert features alone leave the ordinary result unchanged.
- Ordinary rows/events reproduce all 246 SOI records. 55,596 rows and 14,967
  event links verify.

**Stop rules fired → CLOSED WITHOUT PROMOTION.**

| Rule | Result |
|---|---|
| Named opposed newly selected | **FAIL in 1 of 246 conditions:** `all_oil-f001185` publishes 40 s Y865.5 (its ordinary counterpart: Y831). 40 s lies outside the context, because the Foam row (Y840) is below B (Y832) |
| Reviewed positive lost outside C1 with an extremum/direction change | PASS: none |
| Foam coordinate or episode changed | **FAIL in 5 conditions** (all baseline Foam unchanged). Same set as LBQ-1. In `all_oil-f001170` the Foam rows at 44.5–46 s are published only when Oil is, so the two episodes merge |

**Baseline (the primary result) against the ordinary baseline:**

| Control | Ordinary | LBT-1 | Reading |
|---|---|---|---|
| 38 s Y844 | 844 | 844 | unchanged |
| 40 s Y841 / opposed Y865.5 | 865.5 | 831 | opposed removed; replacement 10 px off (outside context; U) |
| 42 s Y839 / opposed Y868 | 868 | **835** | recovered within C1 |
| 42.5 s Y835 / opposed Y805 | 835 | **833** | kept within C1; Y805 never selected |
| 44 s Y844 / opposed Y822 | 822 | **842** | recovered within C1 |
| 49.5 s practical Y841 | 836 | 836 | unchanged |
| 52 s Y833 / wrong Y862 | 833 | 833 | unchanged; Y862 never selected |

- **Report extrema:** the wrong minimum 42 s Y868 disappears. The new extrema
  are max 51.5 s Y828 and min 2.0 s Y858 (an unchanged pre-Foam value).
- **Pre-Foam 0–38 s:** unchanged. The context limit closed LBQ-1's scope gap.
- **New Oil values:** 39.5/41.5/43/43.5/50–51.5 s publish Y828–838.
- **New gaps:** 40.5/41/44.5/45.5 s. The ordinary run had Y864 (opposed
  structure) at 40.5/41 s and Y837/843 at 44.5/45.5 s.

**Outcome G observed (pre-registered).** At 54.5 s, B is Y820 (inside the Y826
entrance band). The in-unit anchored chain of tracklet 100:0021 confirms a
fill (`FILL_SPAN_CONFIRMED`, `unknown_fill_anchored`). 54.5–56 s become
`FILLED_CAP_VETO`; the ordinary run published Y851–852 there, which is
unreviewed.

**Mixing check:** the SFR-1 mixing is gone. Tracklets 79:0013/90:0020 no longer
hold Y805–813 with layer-bottom rows. One tracklet (1:0000) spans the pre-Foam
period and the 39.5–40 s frames, where the Foam row lies below B. This is outside
the context and is not the SFR-1 pattern.

**Descriptive:**
- `base_sample_1`: no unit, no change.
- `sample2`: the 2.0 s Y603 becomes no output (13 E1 removals). The
  agent-assisted provisional truth, not user-confirmed, records 2.0 s as
  `no_interface` / full-like.

**Reading.**
- E1 does what SFR-1 predicted. It removes the mixed identity, and the baseline
  publishes the layer bottom at 42–52 s within C1. This is the best baseline
  of the line.
- Three things remain:
  1. **Fill geometry (G):** a layer bottom that rises into the entrance band is
     read as a completed fill.
  2. **Foam composition coupling:** in the same all-Oil withdrawal conditions
     as TPA-1/LBQ-1, Foam publication follows Oil publication (F06).
  3. **One out-of-context withdrawal:** at 39.5–40 s, Foam appears below the
     unit, and the condition reverts to the opposed Y865.5.
- None of these are reasons to widen E1. No tuning follows. Windows S2 is not
  proposed.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-IDENTITY`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F01`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: `OIL-TRACKLET` — one physical ID alternates between rows above the Foam material row and the layer bottom (SFR-1); LBQ-1 anchors then fed selection and fill confirmation.
- Existing feature coverage: reuses the LBW-3 witness unchanged, the existing `HARD_INVALID` drop path, the Foam material identity row, seed-age limit and lower separation already used by `ORDERED_LOWER_INTERFACE`, LBQ-1 consumer 1 (context-limited), and the LBQ-1/CAF-1/SOI runner, controls and P0 bounds. Tracklet, phase, selection and Foam owners are unchanged.
- Execution scope: sample4 baseline plus 245 SOI conditions (development) and base_sample_1/sample2 descriptive, diagnostic wrapper only; Windows S2 not run.
- Logic-map impact: NONE — diagnostic wrapper; no source change.
- Failure-registry impact: NONE — a closed diagnostic with no runtime mechanism; the fill-geometry and Foam-composition counterexamples are recorded here.
