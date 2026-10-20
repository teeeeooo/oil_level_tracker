# CAF-1 — clean-anchor fill qualification

## Question and mechanism evidence

Base HEAD: `ba937a0`. Current authority: [Work Plan](../../00-project/work-plan.md).
This is the successor that the [HPA-1 boundary](2026-10-17-history-phase-amplification.md#successor-boundary)
called for. It qualifies physical role before inherited track maturity becomes
fill authority. It does not repeat H1/H2, the median/history donors, Y818
exclusion, cost-first, profile tuning, generic anchor privilege or terminal-veto
quarantine alone.

The saved HPA-1 capture of the primary loss (selected Oil withdrawn at 42.5 s)
contains the qualifying fill chain behind the 44–56 s Oil gap. It spans frames
79–88, Y867→821.
- **Contradicted rows:** 7 of its 10 observations carry `material_veto`. A
  material-path node in the row has material-texture conflict at or above the
  existing limit.
- **Contradicted anchors:** every observation with `independent_anchor`
  (frames 80, 81, 82, 84, 86, 87) is one of those contradicted rows.
- **How it qualifies:** `_fill_confirmation_profile` returns
  `UNKNOWN_FILL_ANCHORED` when any chain observation has an independent anchor,
  without looking at that row's current material evidence.
- **Result:** the terminal row is also vetoed, so `_transition_open` creates
  `FILLED_BARRIER / FILL_SPAN_MATERIAL_VETO`, and later rows inherit
  `FILLED_CAP_VETO`. This is an internal barrier, not observed FULL.

The anchor and the vetoing material-path node can be different members of the
same row. The row is then an anchor whose physical role is contested in the same
frame.

## Hypothesis and intervention

**CAF-1:** an observation may grant anchor-based fill authority only when its own
current row is material-clean (`independent_anchor and not material_veto`).

The diagnostic wraps `OilMaterialPhaseLifecycleOwner._fill_confirmation_profile`.
It evaluates the unchanged profile on a copy of the chain in which contradicted
rows do not count as independent anchors. This applies to both the
`UNKNOWN_FILL_ANCHORED` test and the anchor term of empty-entrance motion. Nothing
else changes:
- chain evolution, geometry/span/direction predicates and material limits;
- assignment, row aggregation and terminal-veto handling;
- initial FULL/EMPTY constraints, other anchor uses and every Foam owner.

The predicate uses only current-row booleans that already exist: no threshold, no
stored baseline, no donor value, no video/time/Y exception. A clean anchor
anywhere in the chain still qualifies exactly as before. Rows without anchors are
unaffected.

## Scope and execution

**Stage 1, sample4 sensitivity.** Run the frozen SOI population: baseline plus
all 245 single-time withdrawals from the saved sample4 raw/Recipe (0–56 s, 2 Hz,
113 rows, all options OFF, initial state UNKNOWN_REVIEW). Run both the ordinary
policy and CAF-1 at the current HEAD. Ordinary rows must reproduce the saved SOI
rows exactly. Saved presentations are not compared, because the 2026-10-20
supported-extremum report rule changes report landmarks. Verify every same-frame
Oil/Foam provenance join and typed event link. Render CSV/graphs for every case
whose public output changes, against its ordinary counterpart.

**Stage 2, whole-video controls, only if stage 1 has no stop condition.**
`base_sample_1` and `sample2` with their stored Recipes through the ordinary
analysis entry, ordinary versus CAF-1. Compare against their stored truth where
reviewed. Sample3 stays quarantined. No other recording has a Recipe, and none is
created for this study.

**Contract checks before stage 1.**
- Focused boundary tests: a clean anchor still qualifies; contradicted-only
  anchors do not; anchor-free and empty-entrance paths keep their rules;
  initial-FULL/EMPTY constraints hold.
- The existing `tests/unit/test_oil_phase_lifecycle.py` under the wrapper, with
  the activation count reported. Zero activations would mean those tests are no
  evidence for the new branch.

Private Windows pixels are unavailable here. No Windows run, Recipe change,
production flag or physical FULL claim is part of this study.

## Pre-registered evaluation

Judge outcomes with the
[P0 local-residual bounds](../../30-validation/s11-interface-observability-witness-validation.md#local-residual-bounds-and-extremum-display--2026-10-20).
Sample4's Glass diameter is 104 px, so the C1 band is ±5.2 px. The 13 frozen SOI
controls are the reviewed reference:
- accepted: 38 s Y844, 40 s Y841, 42 s Y839, 42.5 s Y835, 44 s Y844, 52 s Y833,
  plus the 49.5 s practical approximation Y841;
- opposed: 38 s Y880/882/887, 40 s Y865.5, 42 s Y868, 44 s Y822.

Primary loss (selected Oil at 42.5 s), each judged against its ordinary result:
1. **Fill:** no fill qualifies from the contradicted-anchor chain. The 44–56 s
   Oil gaps satisfy C3.
2. **52 s:** the output is within C1 of Y833, or missing (a C3 question). Any
   other value is one targeted user question.
3. **Wrong targets:** no reviewed opposed target is newly selected.
4. **Report extrema:** a supported report extremum that the ordinary result does
   not have is a targeted question, unless it lies within C1 of a reviewed
   positive.
5. **Foam:** coordinates are unchanged.

Population and baseline:
- Baseline under CAF-1: list every public change and classify it A/B/C/U. A
  new A at a reviewed control is a stop condition.
- All 246 conditions: activation count; Foam-coordinate changes against the
  ordinary policy (any change is reported as F06 coupling); every changed case
  is classified and rendered.
- H3's contrary case: the 52/52.5 s whole-Oil losses must not gain a supported
  54.5 s +45 px report maximum. If one appears, it is A unless reviewed otherwise.

**Stop rule.** A new A-class result at a reviewed control, a failed hard
contract (provenance, FULL/EMPTY or boundary test), or Foam coupling that
creates or erases a Foam episode closes CAF-1 without promotion. No predicate
widening, threshold or tuning follows the outputs.

**If stage 1 and stage 2 pass:** CAF-1 becomes a candidate for a default-OFF
option and a Windows comparison on the nine canonical segments. That needs the
user's Windows run. Local results alone are not field acceptance; S11 ACTIVE /
O2 OPEN / FIELD FAIL is unchanged.

## Results and decision

**CAF-1 CLOSED WITHOUT PROMOTION.** The user confirmed that a restored
50.5–52 s Y862–866 run is a wrong target, which triggers the stop rule. Managed
runs `sample/output/s11-clean-anchor-fill-20261020-001` (stage 1) and
`…-corpus-20261020-001` (stage 2) are closed and check clean.

### Contract checks
- Boundary tests: 6 PASS.
- Existing phase suite under the wrapper: 89 PASS with **zero activations**, so
  it is no evidence for the new branch.

### Stage 1, sample4 (246 conditions)
- Ordinary rows and events reproduce the saved SOI population exactly. 55,596
  rows and 14,261 event links verify with zero provenance errors.
- CAF-1 activates in 4 conditions. The **baseline is unchanged**, and no case
  changes a Foam coordinate or Foam landmark.
- H3's 52/52.5 s whole-Oil losses do not activate, so the 54.5 s +45 px maximum
  does not appear.

| Withdrawn input | Oil numerics (ordinary → CAF-1) | Outcome against the pre-registered criteria |
|---|---:|---|
| Selected Oil, 42.5 s (primary) | 84 → 104 | No fill; gaps after 42.5 s are at most 1 s (C3 met). The trajectory mostly matches the baseline, including the baseline's existing wrong 44 s Y822. 51.0–52.0 s gives **Y861.5/862/862** instead of the accepted 52 s Y833 and becomes the supported report minimum at 51.5 s. |
| Selected Oil, 48 s | 90 → 103 | 52 s Y833 and 49.5 s Y836 (within C1 of the practical Y841); otherwise as in the baseline. |
| All Oil, 45 s | 89 → 101 | Same false **50.5–52 s Y866–862** run as the primary case. |
| All Foam, 48.5 s | 90 → 101 | 52 s Y833 and 49.5 s Y836; matches the baseline from 48.5 s on. |

The 51–52 s output was 29 px from the accepted value and changed a report
extremum, so it became the single targeted question. The user answered that it
is wrong (`user-judgment.json`, `y862-question.png` in the stage 1 evidence). It
is a three- to four-sample run that sets the report minimum: a context-distorting
(A) error.

### Why the lower structure is selected

The saved witnesses show the cause directly.
- **51–52 s:** the Y861.5–862 `material_path` row holds `ANCHOR_ELIGIBLE` /
  `ordered_lower_interface` authority on an admitted tracklet in **both** the
  baseline and CAF-1. Every candidate in the Y822–838 row holds only continuation
  authority, and that tracklet is not admitted.
- **Baseline protection was incidental:** the baseline stays in `FILLING`,
  bounded to the contradicted fill's owner, so the lower anchor cannot be
  selected. CAF-1 removes that fill, the phase becomes unconstrained `OPEN`, and
  the selector takes the anchor-authority row and keeps it.
- **Same pattern at 42 s:** the reviewed wrong Y868 is selected from the lower
  tracklet 79:0014 (anchors Y864/868). The Y825–837 row nearer the accepted Y839
  holds continuation authority only. Tracklet 79:0014 is the same owner that
  forms HPA-1's fill chain.
- **Material conflict does not discriminate:** accepted interface candidates
  score 0.59–0.98 (40 s Y841 0.60, 42 s Y839 0.59, 52 s Y833 0.67), and the wrong
  lower anchors score 0.59–0.83. In this small yellow-oil glass the bulk texture
  itself conflicts. The material veto is therefore not a physical-role signal,
  and CAF-1 removed the barrier mostly by coincidence.

The upstream cause is role assignment in `OIL-AUTHORITY`. The lowest-ordered
boundary receives anchor authority even when it is the lower glass structure.
This is the F04 geometry-as-identity shortcut, not a fill-profile defect.

### Stage 2, other recordings (descriptive, run at the user's request after the stop)
- `base_sample_1` 0–14.4 s and `sample2` 0–2 s, ordinary versus CAF-1: **zero
  activations, zero output changes**.
- These qualification windows contain no anchor-based fill decision, so the
  result shows neither benefit nor safety beyond them. Sample3 stays
  quarantined; no other recording has a Recipe.

### Successor boundary

Do not retry material-veto anchor filtering, at fill or authority level. Do not
add a fixed lower band, a Y/time exception, or a recurrence/stationarity veto
(F04 forbids recurring Y as identity). A successor must give the lowest-ordered
row a qualified physical role (interface versus vessel structure) before it can
hold anchor authority. It must keep the accepted rows and the H3/CAF-1
counterexamples (42 s Y868, 51–52 s Y862, 54.5 s +45 px). Prior role
discriminators (RGB, PWC, NCT, SCM) failed and are not reopened by this result.

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F10`.
- First harmful stage: `OIL-AUTHORITY` grants `ordered_lower_interface` anchor authority to the sample4 lower structure while accepted interface rows hold continuation only. HPA-1's barrier and CAF-1's 51–52 s error both follow from that; the fill profile only decides which of them is visible.
- Existing feature coverage: saved sample4 P5 NONE raw candidates and stored Recipe/session; UNKNOWN_REVIEW initial state, ellipse margin 0.08, zero user exclusions/templates, unchanged saved static/artifact/raster outcomes; all experimental options OFF. Material conflict limits and anchor authority are the existing resolver values. Stage 2 uses the stored base_sample_1/sample2 Recipes through the ordinary analysis entry.
- Execution scope: stage 1 runs the completed resolver, samples, events and report presentation on reused current-frame acquisition, and adds CSV/graphs for changed cases. Stage 2 runs full extraction and completed analysis for two local recordings. No GUI, private Windows replay, physical accuracy claim or independent human report reading.
- Logic-map impact: NONE — diagnostic wrapper only; production source, defaults and runtime ownership are unchanged.
- Failure-registry impact: UPDATED — F04 records the lower-structure anchor-authority evidence and F05 records CAF-1's closure; no new failure class or adopted policy.
