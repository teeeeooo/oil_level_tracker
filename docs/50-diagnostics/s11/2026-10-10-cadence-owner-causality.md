# Sample4 cadence gap — source reply and owner causality

Date: 2026-10-10. Executed head: `78eb52170ab6b9e61addab02068b31195fbd1f3a`.
The [machine archive](2026-10-10-cadence-owner-causality.json.gz) retains the frozen
preflight, complete baseline/probe traces, all 113 row witnesses, input/source
hashes, control joins and reproduction scripts. Production is unchanged.

## Source judgment closed

The user answered **“2가 oil이 1은 foam이나 glass 표면의 무늬로 보임”**.
The [bound reply](2026-10-10-cadence-gap-source-reply.json) identifies guide ②
as the Oil location and guide ① as opposing Foam-or-glass-pattern context;
the latter subtype remains unresolved. The original
[question](2026-10-10-cadence-gap-source-review.json) and
[image](2026-10-10-cadence-gap-source-review.png) stay frozen.

This closes the physical relation needed by the
[gap capture](2026-10-10-cadence-gap-capture.md). At f1305/43.5s, the displayed
Oil location is represented in a publishable row but excluded by the final
allowed-owner restriction. This is not exact Y, a tolerance interval, all-sector
candidate truth or a label for every other candidate in that box. Neither a
whole tracklet nor the earlier appearance chain inherits this local role.

## Why the retained Oil location is excluded

The unchanged saved-candidate resolver reproduces **113/113 complete detections**,
including diagnostics. No video decode or detector extraction is needed for this
trace. The existing October 9 raw candidates and full owner trace are hash-bound
and identical to the later nine-frame capture at the relevant frames.

At 43s, the same Y836 row has these two eligible predecessor matches:

| Tracklet | Previous row | Predicted Y | Match cost | Established at assignment time |
|---|---:|---:|---:|---|
| `000079:0013` | Y809 at 42.5s | 809 | 0.850825 | yes |
| `000084:0017` | Y839.5 at 42.5s | 835 | 0.010200 | no |

`DirectedInterfaceTrackletBuilder._established_first_pairs` ranks established
status before cost. The older `0013` therefore claims the only child; `0017`
has no residual assignment for the existing reciprocal-exchange mechanism.
This is deliberate implemented precedence, not a sorting typo. At 43.5s the
Y835 row remains on `0013`. No ambiguity is declared at these two assignments.

The phase resolver sees the subsequently bounded-confirmed `0017` history as
its dynamic filling owner and retains its last row Y839.5/frame-offset85 during
the gap. Its confirmation witness ends at offset88/44s, whose selected Y822
candidate was already reviewed as a wrong target. Thus “established” during
causal assignment and “admitted/confirmed” in the completed bounded witness
refer to different stages; they are not a serialization contradiction.

Current-anchor handoff is actually evaluated for the excluded row at both
missing frames. The first failed predicate is its `MOTION_TRAJECTORY` profile:
this route requires `ANCHOR_CORRIDOR` or `ANCHOR_TRAJECTORY`. The captured gap,
admission, compatibility, motion and geometric bounds otherwise pass. At 43.5s,
the material-path member is also continuation-only; the two anchor members are
other proposal types. An offline predicate recomputation therefore also fails
the material-path-anchor condition. That later condition is **short-circuited
in the original call**, not a second executed rejection reason.

Both frames consequently retain the stale allowed ID `0017`, while every
publishable row belongs to another ID. The selector removes all Oil nodes
before scoring. This establishes a supported causal chain through assignment,
phase ownership and final exclusion. It does not certify `0017` as the right
physical identity across its whole history, or date the first historical
physical association error.

## One frozen attribution counterfactual

Before execution, freeze one probe: remove only established-status precedence
from `_established_first_pairs`; retain cost, reciprocal reservations, ambiguity,
confirmation, all authority/phase policies and selector behavior. Apply it
generically over the complete saved 0–56s window. No timestamp, Glass, coordinate,
reviewed label, threshold change or follow-up rescue enters the probe.

| Time | Baseline Oil | Cost-order-only probe | Physical scope |
|---|---:|---:|---|
| 38s | 844 | 844 | same confirmed candidate |
| 40s | 865.5 | unavailable | known wrong candidate removed; true target not recovered |
| 42s | 868 | unavailable | known wrong candidate removed; true target not recovered |
| 42.5s | 835 | 835 | same confirmed candidate |
| 43s | unavailable | 836 | new selection; exact physical identity unreviewed |
| 43.5s | unavailable | 835 | selected location in reviewed guide ②; no exact-Y claim |
| 44s | 822 | 842 | known wrong selection replaced; replacement candidate unreviewed |
| 49.5s | 836 | 836 | same confirmed candidate, different track ID |
| 52s | 833 | 833 | same confirmed candidate, different track ID |
| 56s | 851 | 811 | agent source inspection places new selection in upper texture, apart from the already reviewed lower Foam–Oil boundary region |

All **15 changed Oil rows** remain in the archive, including new abstentions
at 45.5/46/55.5s and unreviewed additions elsewhere. Numeric observations rise
only from 101 to 102. All four protected exact candidates remain selected;
none of the three known rejected exact candidates remains selected. Those
counts do not certify the changed alternatives. Phase values change on 19 rows,
including FILLING→OPEN over 42.5–51.5s, so this is not an isolated local handoff
repair despite the single assignment-policy intervention.

At 56s, use the earlier [yellow-Foam/dark-Oil regional judgment](../../60-evidence/s11/2026-10-09-local-xy-implementation.md)
and [original source context](2026-10-09-local-xy-foam-front-review.png).
The upper Y811 reading is an agent-observed opposition to that lower target
region, not a new formal point/candidate label. Baseline Y851 is not declared
exact truth merely because the alternative moves away from it.

**CLOSED WITHOUT PROMOTION.** The probe confirms that maturity precedence can
divert a nearby row and create this gap. Cost ordering alone supplies no physical
identity and does not satisfy the one-second same-interface target, O2 or O3.
No further sorting, threshold or handoff relaxation is justified by this result.
The current [validation gates](../../30-validation/s11-interface-observability-witness-validation.md#o3-behavior-entry)
and separate phase-repair contract remain in force.

## Verification

- Independent raw-candidate joins cover all 113 rows in each variant and all
  101/102 selected observations by frame, candidate index, source and Y.
- Baseline complete fields equal the pinned saved result; all 221 production
  source files and every preflight input remain unchanged.
- All six Foam coordinate/confidence fields remain equal in 113 rows. This
  does not claim equality for unrelated shared diagnostics or a new report run.
- Four executed current-anchor calls at the two missing frames agree with an
  independent predicate recomputation; short-circuit scope is preserved.
- Runtime patches are restored. Both full completed outputs remain locally
  pinned in `sample/output/s11-cadence-owner-causality-20261010-001/`.
- No Windows execution, production adoption, legacy-truth edit or field gain.

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: source-qualified f1305 Oil location is lost at final owner restriction. Earlier assignment precedence and failed current-anchor handoff are captured causal contributors; the first historical physical track-identity error remains unqualified. The counterfactual does not establish physical identity from proximity or motion.
- Logic-map impact: NONE — observe the existing assignment/phase/selector path and reject a local attribution probe; production ownership is unchanged.
- Failure-registry impact: NONE — the failed probe fits existing identity-by-motion/adjacency and owner-handoff constraints; no new physical mechanism is promoted.
