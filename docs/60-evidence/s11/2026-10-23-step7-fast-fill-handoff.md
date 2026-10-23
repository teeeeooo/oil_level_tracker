# S11 step-7 receipts and fast-fill FULL handoff — 2026-10-23

## Current disposition

S11 is ACTIVE; O2 is OPEN; the Windows field result remains FIELD FAIL. The
[Work Plan](../../00-project/work-plan.md) is the only owner of current state and
authorization. Everything below is committed and pushed.

**Windows is unavailable again** (the user is off work). The user will say
when it returns. No Windows request is queued.

**Changes this session:**
- **No production default changed.**
- **One new opt-in detector option, default OFF (`4f0665b`):** the fast-rise
  association `--oil-fast-rise-association` (`+fast-rise-association-v1`).
  Its local checks failed F2/F3, so it is not adopted.
- **Diagnostics only:**
  - `tests/diagnostics/s11_foam_layer_bottom_follow.py` (FLB-1/FLB-2);
  - `tests/diagnostics/s11_fast_fill_cadence.py` (FFF-1);
  - a fast-rise mode in `s11_initial_full_comparison.py`.

**Checks:**
- Full suite at `3e1e330`: 3,942 passed, 12 skipped (the sample3 quarantine).
- Managed runs: 124, all clean. Governance and catalog checks pass.

## What this session settled

| Item | Outcome | Owner |
|---|---|---|
| Review-014 | Recorded; the strict sample4 references cover 52.0–56.0 s | [Result](../../50-diagnostics/s11/2026-10-22-layer-bottom-topology-2.md#review-014-result--2026-10-23) |
| SBD-1 (54.0–54.5 s early drop) | **Closed, option 1** (user): an ambiguous transition with named limits | [SBD-1](../../50-diagnostics/s11/2026-10-23-strict-boundary-early-drop.md) |
| FLB-1 | Closed without design: the unbounded hand-off fails the controls | [FLB-1](../../50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow.md) |
| FLB-2 | **Closed, no design:** held-out NOT TESTED (no accepted witness before 680.5 s); R2 fails; R4 fails (26 numeric rows inside SPL#4 BASE FULL, one SPL#1 drain row lost); the `detached_layer` witness fires without Foam | [Result](../../50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow-2.md#held-out-result--2026-10-23) |
| Step 7 (Windows) | **Received in two replies.** Identity PASS. Gate SPL#4 prediction PASS (exactly the 14 wrong rows, plus one false Accum EMPTY); SPL#1 unchanged. Report checks PASS (band cells, E2, first-catch guard). Review-012: every mark is the Foam-region bottom, and the output lies 55.5–187 px above it | [Receipt](2026-10-23-step7-windows-receipt.md) |
| Fill-owner gate | **Promotion HELD** (user): gains and losses of the same order; default OFF | [Gate evidence](2026-10-22-fill-owner-contest-local.md) |
| Accum 480–653 s | Stays UNKNOWN; L2 refuses EMPTY (the first catch is about 124 px above the bottom) | [LCR-1](../../50-diagnostics/s11/2026-10-22-reconstruction-late-catch-review.md) |
| LBT-2 Windows S2 | **HELD until Windows returns** (user). Review-012 is its held-out reference; LBT-2 was frozen before review-012 was read | [Work Plan](../../00-project/work-plan.md) |
| FFF-1 (fast-fill FULL) | Mechanism: the per-sample association cap. Option 1 (higher sampling) is ruled out for products. Option 2 was chosen. The local cause check is CONFIRMED | [FFF-1](../../50-diagnostics/s11/2026-10-23-fast-fill-full-review.md) |
| Fast-rise association | Frozen `663e1e9`, implemented `4f0665b`. F1/F4 pass (no change on the controls); F2/F3 fail (no seed on the stand-ins: rows lack the anchor-eligible witness). Not retuned. **User: option 1, wait for the SPL#4 readout** | [Evidence](2026-10-23-fast-rise-local.md), [design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-23-fast-rise-association) |

**User statements recorded this session (verbatim where they decide):**
- "고정 먼저하자" (FLB-2 before the step-7 results).
- "승격 보류 -> 얻는거 잃는게 비슷한 수준으로 보임" (the gate).
- SBD-1: "동의" (option 1). S2: hold until Windows can run.
- Option 1 (sampling rate): "지금 시간도 오래걸려서 디텍터 개선 후에는 검출 속도
  개선을 할 예정이라 1번은 안될거같고. 2번으로 로컬 원인 확인 해보자".
- The fast-rise design: "1. 동의함 대체로 빠른 배출은 저정도 속도보다는 느림 /
  2. 로컬 구현 먼저 동의함". After the checks, option 1: wait for SPL#4.
- Windows source: the user downloads the GitHub ZIP by hand. The ZIP hash is
  not an identity check; per-file SHA-256 values are.

## Next (the user decides each step)

**When Windows returns: one combined request, not yet written.**
1. **Fast-rise, read-only first.**
   - List every Oil candidate in SPL4_B_ref at 20.5–25.5 s: y, tracklet fields,
     authority (anchor-eligible or not), physical proposal, and registered
     motion support and coverage.
   - The question: does a witnessed upward triplet beyond 32 px, in a
     constant-velocity line, exist? The frozen
     [checks](../../30-validation/s11-physical-interface-evidence-repair-validation.md#fast-rise-association-checks--2026-10-23)
     own the next step.
2. **Fast-rise, the SPL#4 run** only if a triplet exists.
   - 0–90 s at 2 fps, both arms with IFO v2 and top-exit v3.
   - Expected: the level is admitted at 21–25 s, and top-exit closes FULL
     inside 22.0–27.0 s.
   - Every differing row is listed and read against the user's timeline.
3. **LBT-2 S2.**
   - Freeze its Windows protocol first, on SPL#1 (④/⑩ settings).
   - Score it on the review-012 table V references.
   - Report all nine segments, with 678.5/679 s unchanged.
4. **Ask for verbatim tool stdout or log lines.** The first step-7 reply came
   as summaries and needed a follow-up.

**If SPL#4 has no witnessed triplet:** the user chooses between a successor
witness protocol (the stand-ins are now seen) and closing option 2 (accept
UNKNOWN on fast fills).

**Open, not scheduled:**
- Detector speed work after the detector work (user).
- LBT-2's named limits: 40 s, 54.0–56 s, Foam removals, sample2 2.0 s.
- The fresh low start (sample5, 4 rows).
- Post-Foam association (`INCOMPATIBLE_BRANCH`) and drain release (F08) on
  SPL#1 Accum.
- A frame review of SPL#4's fast rise.
- Review-006 pending. Next free review ID: review-015.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-IDENTITY`, `OIL-AUTHORITY`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`
- First harmful stage: per the linked records. Fast fill is stopped at `OIL-TRACKLET` association (confirmed locally); the layered-Foam Accum output lies above the marked Foam-region bottom (stage not located).
- Existing feature coverage: per the linked records; the only new detector capability is the default-OFF fast-rise association.
- Execution scope: a handoff summary of committed records; no new run.
- Logic-map impact: NONE — a handoff; the logic map was updated with the fast-rise implementation (`4f0665b`).
- Failure-registry impact: NONE — no new mechanism or failure.
