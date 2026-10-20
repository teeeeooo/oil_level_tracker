# LBT-1 — layer-bottom topology in the ordered-lower context

**Status: FROZEN — approved by the user 2026-10-20; tool `tests/diagnostics/s11_layer_bottom_topology.py` committed with this text before any run.** Base HEAD:
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

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-IDENTITY`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F01`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: `OIL-TRACKLET` — one physical ID alternates between rows above the Foam material row and the layer bottom (SFR-1); LBQ-1 anchors then fed selection and fill confirmation.
- Existing feature coverage: reuses the LBW-3 witness unchanged, the existing `HARD_INVALID` drop path, the Foam material identity row, seed-age limit and lower separation already used by `ORDERED_LOWER_INTERFACE`, LBQ-1 consumer 1 (context-limited), and the LBQ-1/CAF-1/SOI runner, controls and P0 bounds. Tracklet, phase, selection and Foam owners are unchanged.
- Execution scope: planned — sample4 baseline plus 245 SOI conditions (development) and base_sample_1/sample2 descriptive, diagnostic wrapper only; Windows S2 needs a separate go.
- Logic-map impact: NONE — diagnostic wrapper; no source change.
- Failure-registry impact: NONE — a draft diagnostic with no runtime mechanism; any result is recorded here.
