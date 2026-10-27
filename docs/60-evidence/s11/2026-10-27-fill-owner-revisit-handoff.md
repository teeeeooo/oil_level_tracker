# S11 fill-owner gate revisit handoff — 2026-10-27

## Current disposition

S11 is ACTIVE; O2 is OPEN; the Windows field result remains FIELD FAIL. The
[Work Plan](../../00-project/work-plan.md) is the only owner of current state
and authorization. Everything below is committed and pushed to `main`
(latest `9c421c3` before this handoff).

- **No production detector default changed.** FIELD FAIL / O2 OPEN and
  review-006 pending are unchanged.
- **No Windows request is queued.** Steps 12–15 and reviews 015–016 are
  answered.
- **Managed runs:** 137, all clean.
- **Next free review ID:** review-017.

## What this session settled

The revisit's three questions were answered on reviewed truth. The detail is
in [FOR-1](../../50-diagnostics/s11/2026-10-27-fill-owner-recency-local.md)
and [FOR-2](../../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md).

| Item | Outcome |
|---|---|
| FOR-1 (local) | NO-SEP: an owner's own recent motion does not separate a low owner from the level (sample5 low 72.7 % vs level 80.0 %). Do not retry an owner-own-motion test |
| Step 12 (Windows trace) | NOT CONFIRMED by the frozen rule. 0018 reappears and is dynamic at once from fixed fields of a confirmation that ended at 14.5 s; 0035 is a fresh confirmation (22.0–24.5 s). Both owners rise |
| Review-015 (user) | OWNER-LEVEL at 22.5–24.0 s: both owners are on the level. The fast rise is 24.0–27.0 s, 347.5 px, with 5 of 6 steps beyond the 32 px cap. The timeline's "FULL at 24–25 s" was Foam |
| SPL#4 truth (user) | Corrected to the review: Oil FULL from 27.5 s (review-016), cloudy with residual bubbles until about 42 s, drain at 63 s. Recorded in the [validation owner](../../30-validation/s11-physical-interface-evidence-repair-validation.md#top-exit-v3-promotion-acceptance--2026-10-22). Old frozen windows are not re-judged |
| Step 13 (coverage) | ELIGIBILITY: the level is a candidate in 7 of 7 rows at 24.0–27.0 s, but builder-eligible only at 24.5–25.0 s (`0040`) |
| Step 14 (authority) | RECURRENCE-LED: the level rows are initially eligible and are demoted after tracking, every one at exactly 0.80 |
| Step 15 (peers) | LOWER-OWNER-PEER: in all 4 demoted frames the same-frame partition peer is the lower boundary at Y693–721, which is 0018 itself at 25.5–26.5 s. The level's texture conflict under Foam (0.62–0.83) supplies the demotion's contradiction (`S11-F06` family; AAT-1, TPA-1) |
| Partition desk review | At 2 fps the fast rise meets three barriers in series: authority (the partition demotion), the association cap and the fill-chain handoff. Lifting one alone does not reach FULL |

**Corrections made in the session (do not repeat the wrong readings):**
- `TRACK_OPPOSITION` is not opposition by other tracks. It is either the
  height-bucket recurrence penalty (continuous) or the same-frame
  superior-partition rule (exactly 0.80).
- The SPL#4 owners in 22.5–27.0 s are not stationary.

**User decisions, verbatim where they decide:**
- "(B) 확인 먼저 하고 (A)로 넘어가는걸로 하자".
- Review-015: "그렇게하자".
- Truth and reviews: "1. review 기준으로 변경 2. review 16도 진행 약 27s에서
  oil full 되고 뿌연 상태(잔여 기포)가 점점 투명해지면서 약 42s oil 투명도
  회복됨 3. 확인하자".
- The order E4 → E2 → E1 → E3: "결국 E3까지 가긴해야되는데 하나씩
  짚어보자는거네. 추천 순서대로 진행하자".
- **E4 approved as drafted:** "일단 구현은 이대로 진행해보자".

## Next: implement E4 as drafted

**Owners:**
- [E4 design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-27-co-located-fill-owners-e4)
  (status DRAFT → set to APPROVED/FROZEN when coding starts);
- its [frozen checks](../../30-validation/s11-physical-interface-evidence-repair-validation.md#co-located-fill-owner-checks--2026-10-27).
- Use the `s11-detector-change` Skill; History Review block in the design doc.

**Where (mirror the contested gate, `fill_owner_contest`):**
- **Lifecycle:** `src/oil_tracker/adapters/vision/oil_phase_lifecycle.py`.
  - Work in `_transition_open`, in the last `else` branch that sets
    `FILL_OWNER_AMBIGUOUS` (about line 1059).
  - Under a new policy flag `fill_owner_colocation_enabled`, check:
    - every dynamic owner has a row in `rows` (`row.tracklet_id`, `row.y`);
    - max − min of those rows' Y ≤ `self.policy.maximum_jump_px`.
  - If so: `allowed_tracklet_ids = dynamic_fill_owner_snapshot`, reason
    `FILL_OWNER_COLOCATED`. Do not add the frame to `ambiguous_frames` and
    add no contest marks.
  - Leave every state field as in the ambiguous branch.
- **Wiring:** the same files and lines as `fill_owner_contest`:
  - `bootstrap.py` 64/77/122;
  - `__main__.py` 32/40/57, flag `--oil-fill-owner-colocation`;
  - `oil_observation_resolver.py` 168/1493/2224;
  - `observation_sequence_resolver.py` 72/80/91, version suffix
    `+fill-owner-colocation-v1`;
  - `opencv_phase_detector.py` 53/62/69/90/106: refuse cost-first, RGB and
    Local XY.
- **Tests:**
  - new `tests/unit/test_oil_fill_owner_colocation.py`, modelled on
    `tests/unit/test_oil_fill_owner_contest.py`;
  - extend `tests/gui/test_initial_full_comparison_launch.py` (around lines
    65/93) and `tests/test_oil_production_cutover.py`.
- **Local controls:** add an E4 comparison mode to
  `tests/diagnostics/s11_initial_full_comparison.py`, beside
  `fill_owner_contest_comparison` (about lines 292–440 and 617).
  - Run the six controls in a managed run (`scripts/experiment_artifacts.py`)
    and score K1–K3 with a frozen script.
- **Prediction to score** (from the kept FOR-1 readouts):
  - sample5: exactly 9.5, 10.0 and 11.0 s become `FILL_OWNER_COLOCATED`;
    11.0 s may publish a low row (K3 risk);
  - sample7 and the other four controls: no change.
- **Logic map:** update `OIL-PHASE-FILL` with the new opt-in row when it is
  implemented, as the gate did.

**After E4:** the Windows SPL#4 comparison (pass: exactly 23.0 and 23.5 s
become co-located, within 32 px of the review-015 marks; everything else
equal), then E2 → E1 → E3, each frozen before code.

## Tools added this session (read-only diagnostics)

- `tests/diagnostics/s11_fill_owner_recency.py` (FOR-1)
- `tests/diagnostics/s11_fill_owner_trace_readout.py` (step 12)
- `tests/diagnostics/s11_level_coverage_readout.py` (step 13)
- `tests/diagnostics/s11_level_authority_readout.py` (step 14)
- `tests/diagnostics/s11_level_peer_readout.py` (step 15)

Review photos and relayed outputs are kept outside Git in the closed managed
runs:
- `s11-review-015-photos-20261027-001`
- `s11-review-016-photos-20261027-001`
- `s11-step14-relay-20261027-001`
- `s11-step15-relay-20261027-001`

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`
- First harmful stage: SPL#4 2 fps fast rise is demoted at `OIL-AUTHORITY` by the same-frame partition rule (lower boundary Y693–721 as peer; Foam texture conflict as contradiction), then capped at `OIL-TRACKLET` association and `OIL-PHASE-FILL` handoff; 22.5–24.0 s loses correct output to `FILL_OWNER_AMBIGUOUS` between two owners on the level.
- Existing feature coverage: reads the saved step-7 `SPL4_B_ref` FULL trace (IFO v2 + top-exit v3, 2 fps) and the FOR-1 local runs; the E4 draft reuses the contested gate's wiring and controls.
- Execution scope: a handoff summary of committed records; no new run.
- Logic-map impact: NONE — a handoff; E4 is not yet implemented.
- Failure-registry impact: NONE — the findings fit existing entries.
