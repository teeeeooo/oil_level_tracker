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

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F10`.
- First harmful stage: HPA-1 places it at row aggregation/association, then inherited fill confirmation. The saved chain shows fill authority resting only on material-contradicted anchors. Whether removing that authority repairs context without new errors is the open question.
- Existing feature coverage: saved sample4 P5 NONE raw candidates and stored Recipe/session; UNKNOWN_REVIEW initial state, ellipse margin 0.08, zero user exclusions/templates, unchanged saved static/artifact/raster outcomes; all experimental options OFF. Material conflict limits and anchor authority are the existing resolver values. Stage 2 uses the stored base_sample_1/sample2 Recipes through the ordinary analysis entry.
- Execution scope: stage 1 runs the completed resolver, samples, events and report presentation on reused current-frame acquisition, and adds CSV/graphs for changed cases. Stage 2 runs full extraction and completed analysis for two local recordings. No GUI, private Windows replay, physical accuracy claim or independent human report reading.
- Logic-map impact: NONE — diagnostic wrapper only; production source, defaults and runtime ownership are unchanged.
- Failure-registry impact: NONE — evidence is recorded here; any registry pointer follows the results.
