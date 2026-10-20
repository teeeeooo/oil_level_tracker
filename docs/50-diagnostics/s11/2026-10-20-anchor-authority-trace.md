# AAT-1 — why accepted sample4 interface rows lack anchor authority

## Question and execution

Read-only follow-up to [CAF-1](2026-10-20-clean-anchor-fill.md#why-the-lower-structure-is-selected).
Current authority: [Work Plan](../../00-project/work-plan.md).

CAF-1 showed the lower glass structure holding `ordered_lower_interface` anchor
authority while accepted interface rows held continuation only. This trace asks
which gates cause that split.
- **Method:** `tests/diagnostics/s11_anchor_authority_trace.py` wraps
  `evaluate_phase_identity` and `evaluate_candidate_authority` inside the
  completed resolver. It records each Oil candidate's inputs, gate outcomes,
  initial and final authority, tracklet admission and selection. The wrappers
  return the original decisions.
- **Scope:** the 13 SOI control frames plus 51.0/51.5 s on the saved sample4
  baseline (196 candidates). The traced baseline reproduces the saved SOI
  baseline rows exactly.
- **Evidence:** closed managed run `sample/output/s11-anchor-authority-trace-20261020-001`.

No detector behavior, threshold or Recipe changed.

## Findings

1. **After Foam appears, every Oil candidate is ordered-lower.** From 40–42 s
   on, the Foam material row is at Y809–840, so all Oil candidates lie at least
   7 px below it. An ordered-lower candidate is classified
   `ORDERED_LOWER_INTERFACE` only with direct quality, a Foam seed at most 3 s
   old, and cross-representation support of at least 0.12. Otherwise it is
   `CONTINUATION_ONLY`.

2. **Accepted interface candidates have zero cross-representation support.**
   This holds at 42, 42.5, 44, 51, 51.5 and 52 s, even where several families
   agree on one row: at 51 s, `material_path`, `calibrated_high_recall` and
   `phase_transition_scan` are all at Y833 and score 0.00. They fail
   `ordered_lower_cross_representation`. Lower-structure candidates
   (Y861.5–868) score 0.35–0.89 and become anchors. The one accepted exception
   at 49.5 s (Y836/837, support 0.83/0.84) happens to have a low-conflict peer.

3. **Cause: the texture-conflict peer exclusion.** `_cross_representation_support`
   ignores every peer with `material_texture_conflict >= 0.60`. Accepted
   interface candidates have conflict 0.60–0.75, so they cannot support each
   other. Peers around the lower structure have conflict 0.33–0.46 and do count.

4. **The conflict measure reads an Oil/Foam boundary as "inside texture".**
   `material_texture_conflict = row_support × (1 − 0.25 × terminal)`, where
   `row_support` is the raw material-texture density within ±2 rows. The
   boundary under the textured Foam layer has row support of 0.80–1.00. The
   terminal-partition term was meant to discount such a boundary, but its
   maximum 25% reduction leaves 0.75 above the 0.60 limit.

5. **The terminal-partition feature already separates the roles at the
   decisive frames:**
   - accepted interface candidates have terminal support 1.00 at all eight
     accepted frames, and on all 7 accepted controls;
   - the 40/42/44 s opposed targets (Y865.5, Y868, Y822) and the 51–52 s Y862
     structure have 0.00.

   It is not a complete role discriminator. The 38 s opposed lower rows
   (Y880/882/887), before Foam, also have 1.00, but their conflict is already
   below 0.60 and they are not selected. Most Oil candidates have 0.00 (1,399
   at exactly zero).

6. **This defeats a documented design intent.** The [R14 contract](../../20-architecture/s11-r14-phase-component-replacement-architecture.md)
   added the recent-Foam ordered-lower exception because the accepted Foam
   mask "can overlap the physical Oil row and therefore make
   material-texture conflict high". The later peer exclusion in
   `_cross_representation_support` (introduced in `d50f2fa`) removes the
   support that exception needs. The
   [R22 reviewed findings](s11-r22-reviewed-interface-causal-findings.md) and
   the [physical-interface design](../../20-architecture/s11-physical-interface-evidence-repair-design.md)
   record the same blockage for a visible Windows Accum boundary. That design's
   typed-witness replacement of broad-texture vetoes was never implemented.

## Meaning and boundary

The shared root of the reviewed 42 s Y868 wrong target, HPA-1's fill barrier
and CAF-1's false 51–52 s Y862 is now concrete:
- a texture gate built for "inside textured material" also rejects the Oil/Foam
  boundary;
- the terminal-partition signal that would distinguish the two is used only as
  a small discount.

This is evidence for a successor design, not a repair. It does not choose a
threshold, certify terminal support as physical identity, or claim the Windows
Accum blockage has the same cause pixel for pixel. A successor must be
pre-registered against the same sample4 controls and counterexamples (38 s lower
rows, 40/42/44 s opposed, 51–52 s Y862, H3's 54.5 s +45 px) and a full-window
check. Windows layered-Foam segments are the field target that would need the
user's run.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-IDENTITY`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F10`.
- First harmful stage: `OIL-AUTHORITY` cross-representation support. The `material_texture_conflict >= 0.60` peer exclusion zeroes support for accepted Oil/Foam boundary candidates, so they cannot reach the R14 ordered-lower identity, while lower-structure rows can.
- Existing feature coverage: saved sample4 P5 NONE raw candidates and stored Recipe/session, UNKNOWN_REVIEW, margin 0.08, zero exclusions/templates, all experimental options OFF; existing material-texture and terminal-partition features as produced by the saved frame acquisition.
- Execution scope: completed resolver on the saved baseline with read-only wrappers; no frame acquisition rerun, behavior change, report, Windows replay or physical accuracy claim.
- Logic-map impact: NONE — read-only trace; ownership and control flow are unchanged.
- Failure-registry impact: UPDATED — F06 records the Oil/Foam boundary texture-conflict blockage as evidence; no adopted policy.
