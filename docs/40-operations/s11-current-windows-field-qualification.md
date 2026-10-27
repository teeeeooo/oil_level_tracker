# S11 Current Windows Field Qualification

**Status:** `ACTIVE PROCEDURE / DRAFT REQUEST`. The read-only [FER-1 FULL evidence readout request](#fer-1-full-evidence-readout-request) is QUEUED (2026-10-27; readings frozen before output in [FER-1](../50-diagnostics/s11/2026-10-27-full-evidence-readout.md)). The read-only [E1 partition readout request](#e1-partition-readout-request) is COMPLETE (2026-10-27, [result](../50-diagnostics/s11/2026-10-27-partition-contradiction-readout.md#windows-readout--2026-10-27-rerun)) after a void first relay (tool defect): neither Foam scope frees SPL#4's demoted level at 25.5–27.0 s (not ordered-lower; no eligible Foam front from 24.0 s); on SPL#1 Accum both reach the reviewed level in 3 frames but free 2,644 (A) or 1,874 (B) rows. [Review-017](#review-017-e2-hit-frame-review) is COMPLETE (2026-10-27, [result](../50-diagnostics/s11/2026-10-27-owner-above-readout.md#review-017-result--2026-10-27)): SPL#1 Accum 669.5–671.5 s are correct rows (COST ×3, within 10 px of the marks); SPL#4 Accum 65.0–67.0 s shows no Oil boundary (all Foam; 66.0 s UNREAD by the letter); E2's user-truth tally is 4 gains against 12 costs. The read-only [E2 owner-above readout request](#e2-owner-above-readout-request) is COMPLETE (2026-10-27, [result](../50-diagnostics/s11/2026-10-27-owner-above-readout.md#windows-readout--2026-10-27)): SPL#4 BASE 0 hits; nothing admitted lies above 0018 at 27.0–34.5 s, so E2 leaves the 14 wrong-target rows; SPL#1 Accum 7 hits (4 remove rows 142–187 px above the review-012 marks); SPL#4 Accum 1. The [E4 SPL#4 comparison request](#e4-spl4-comparison-request) is COMPLETE / **PASS against its frozen condition** (2026-10-27, [receipt](../60-evidence/s11/2026-10-27-fill-owner-colocation-local.md#windows-spl4-comparison--2026-10-27)): exactly 23.0 and 23.5 s co-located, publishing Y781.0 and Y757.0 (+13.0 and −4.5 px from the review-015 marks); every other row equal; E4 stays default OFF. The [step-15 level peer readout](#step-15-level-peer-readout) is COMPLETE (2026-10-27, [result](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#step-15-result--2026-10-27)): LOWER-OWNER-PEER; the stale owner's lower boundary (Y693–721, 0018 in three frames) is the likely partition peer that demotes the level. The [step-14 level authority readout](#step-14-level-authority-readout) is COMPLETE (2026-10-27, [result](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#step-14-result--2026-10-27)): RECURRENCE-LED; every demotion reads exactly 0.80, which points to the same-frame superior-partition rule (inference). The [step-13 coverage readout and review-016 request](#step-13-coverage-readout-and-review-016) is COMPLETE (2026-10-27, [result](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#step-13-result--2026-10-27)): coverage ELIGIBILITY (the level is a candidate in 7 of 7 rows, builder-eligible in 2); Oil FULL onset 27.5 s. The [review-015 SPL#4 fast-rise level review](#review-015-spl4-fast-rise-level-review) is COMPLETE (2026-10-27, [result](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#review-015-result--2026-10-27)): OWNER-LEVEL at 22.5–24.0 s (both owners on the level); the level is above both owners at 24.5–27.0 s; the Oil is not at the top by 27.0 s. The read-only [step-12 fill-owner trace readout request](#step-12-fill-owner-trace-readout-request) is COMPLETE (2026-10-27, [receipt](../60-evidence/s11/2026-10-27-step12-windows-receipt.md)): NOT CONFIRMED by FOR-1's frozen rule (W1 holds; W2 fails on 0035, a fresh confirmation 22.0–24.5 s); the 0018 half of the question-1 reading holds. The [step-11 speed timing request](#step-11-speed-timing-request) is COMPLETE (2026-10-26, [receipt](../60-evidence/s11/2026-10-26-step10-11-windows-receipt.md#step-11--speed-timing-and-identity)): identity PASS on all three runs (rows; trace bytes for S-1 and P-1); FULL 224.9 → 160.1 s sequential and 110.3 s parallel; NONE 90.9 → 79.5 s parallel. The read-only [step-10 stage readout request](#step-10-stage-readout-request) is COMPLETE (2026-10-26, [receipt](../60-evidence/s11/2026-10-26-step10-11-windows-receipt.md#step-10--stage-readout)): S-A by the letter, dropped at phase (`OIL-PHASE-FILL`), with a named limit. The [step-9 combined request](#step-9-combined-request) is COMPLETE (2026-10-26, [receipt](../60-evidence/s11/2026-10-26-step9-windows-receipt.md)): T-1 identity PASS including trace bytes; CAD-1 C1 fails (no FULL at 6 fps; outcome C with a named limit); Windows timing recorded. The [step-8 combined request](#step-8-combined-request) is COMPLETE (2026-10-26, [receipt](../60-evidence/s11/2026-10-26-step8-windows-receipt.md)). F: 0 qualifying SPL#4 triplets, so no SPL#4 run. L: LBT-2 S2 closes without a design (S2 and S3 fail; S4 C8 A0 B4). The read-only [step-7 follow-up request](#step-7-follow-up-request) is COMPLETE (2026-10-23). The [FLB-2 held-out request](#flb-2-held-out-request) is COMPLETE ([result](../50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow-2.md#held-out-result--2026-10-23)): FLB-2 closes with no design: the held-out case is NOT TESTED (R3), and R2 and R4 fail. The [step-7 combined request](#step-7-combined-request) is COMPLETE ([receipt](../60-evidence/s11/2026-10-23-step7-windows-receipt.md)). Identity PASS. The gate's SPL#4 prediction PASS: exactly the 14 wrong-target BASE rows go UNKNOWN, plus one false Accum EMPTY sample, and SPL#1 is unchanged. Report checks PASS (band cells, E2, first-catch guard). Review-012 is answered. Gate promotion is HELD (user, 2026-10-23); it stays default OFF. The read-only [SPL#4 opposition follow-up](#spl4-opposition-follow-up) is COMPLETE ([receipt](../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-opposition-follow-up-receipt--2026-10-22)): the opposing source is `OIL-PHASE-FILL` `FILL_OWNER_AMBIGUOUS` between two low owners, and the ⑩ Accum census is complete. The [SPL#4 top-exit promotion evidence request](#spl4-top-exit-promotion-evidence) is COMPLETE / **P FAIL** ([receipt](../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-receipt--2026-10-22)): no top-exit FULL row, candidate identical to the reference; R not evaluated; N and U pass; top-exit stays default OFF. The [report confirmation run](#report-confirmation-run) is COMPLETE / **PASS against its written expectation** ([receipt](../60-evidence/s11/2026-10-21-initial-state-report-local.md#windows-report-confirmation--2026-10-22)): BASE reconstruction ACCEPTED and judged PASS on its level, Accum UNRESOLVED, tracking data identical to ⑩. The [⑩ top-exit v3 comparison](#top-exit-v3-comparison) is COMPLETE / **PASS against its pre-registered outcome** ([receipt](../60-evidence/s11/2026-10-21-top-exit-v3-local.md#windows-top-exit-v3-comparison--2026-10-21)): BASE FULL from 674.0 s, no Accum FULL, pre-closure rows unchanged. Top-exit v3 stays default OFF. The [⑨ top-exit v2 comparison](#top-exit-v2-comparison) is COMPLETE / **FAIL against its pre-registered outcome** ([receipt](../60-evidence/s11/2026-10-21-top-exit-v2-local.md#windows-top-exit-v2-comparison--2026-10-21)): BASE FULL started at 663.0 s. Top-exit stays default OFF and NOT ADOPTED. The top-exit predicate check is COMPLETE ([receipt](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#predicate-check-receipt--2026-10-21)). The 673 s selection-cause extraction is COMPLETE ([receipt](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#673-s-selection-cause-receipt--2026-10-21)). Review-011 is COMPLETE ([result](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#review-011-result--2026-10-21)). Review-010 is COMPLETE ([result](../50-diagnostics/s11/2026-10-20-approach-review.md#review-010-result)). The [LBW-3 held-out check](#lbw-3-held-out-witness-check) is COMPLETE ([result](../50-diagnostics/s11/2026-10-20-layer-bottom-witness-3.md#windows-held-out-result)). The Accum texture-gate extraction and review-009 are COMPLETE ([ATG-1](../50-diagnostics/s11/2026-10-20-accum-texture-gate.md#decision)). Bounded 721 s saved-evidence intake is COMPLETE. The false-anchor route is identified; no behavioral repair is qualified. Top-exit preflight is COMPLETE / CONDITION FAILED; ⑧ was NOT RUN and is not requested. The three prior candidates and accounting remain CLOSED.

**October 15 truth correction:** the user corrected BASE to drain at 550–652 s,
refill at 652–674 s and reach FULL within 674–675 s. The exact transition frame
is unknown; post-transition FULL counts start at 675 s. The bounded
[Refill owner and false-output follow-up](#refill-owner-and-false-output-follow-up)
is now CLOSED. Cost-first/review-005 and the
[returned RGB comparison](../60-evidence/s11/2026-10-14-candidate-rgb-trial.md#windows-rgb-result--2026-10-16)
are CLOSED as **REGRESSION / NOT_ADOPTED**. The
[returned Local XY comparison](../60-evidence/s11/2026-10-09-local-xy-implementation.md#windows-local-xy-result--2026-10-16)
also closes the tested configuration without adoption: partial BASE suppression
coexists with a reviewed replacement artifact and an allowed Accum observation
loss. All three candidate runs and the
[saved-output accounting closeout](#priority-3-local-xy-saved-output-closeout)
are complete. The user subsequently authorized the [top-exit FULL comparison](#top-exit-full-comparison), followed by a separate investigation of the 721 s non-interface output. Its received geometry preflight failed before execution; FULL remains unresolved. The [721 s investigation](#721-second-identity-investigation) has now returned its bounded evidence and is complete. The [Accum texture-gate extraction](#accum-texture-gate-extraction) is also complete; no Windows extraction or run is requested; the Work Plan owns the next local repair-design boundary.
Review-006 remains unreviewed/pending. Cost-first/RGB/Local XY remain OFF outside retained trial data.
Earlier completed inspection steps below are retained for reference and must not
be repeated merely because the reviewed timing changed.

This document is the executable target-Windows field procedure for whichever S11 detector candidate the current Work Plan names. It intentionally does not hard-code R7–R12 or any future revision number. A candidate becomes the subject of this procedure only when `docs/00-project/work-plan.md` and the user's granted scope make Windows qualification current.

## FER-1 FULL evidence readout request

**QUEUED 2026-10-27.** A read-only design input for path F
([OFF-1](../50-diagnostics/s11/2026-10-27-owner-free-full-review.md)). The
user agreed (2026-10-27): "시작하자". The readings are frozen before any
output in [FER-1](../50-diagnostics/s11/2026-10-27-full-evidence-readout.md#frozen-readings).
No detector run: the tool reads the saved step-7 FULL-debug bundles.

**What it answers:**
- **SPL#4 BASE 27.5–63.0 s (R1, R3, R4):** does the image FULL evidence pass
  gate 1 (frame outcome no-interface) and gate 2 (FULL likelihood ≥ 0.58)?
  If not, what stops it?
- **SPL#4 Accum 20–90 s and SPL#1 Accum 650–700 s (R2):** sustained `full`
  nodes on Foam, with or without an eligible Foam front.
- **The rest:** context and whole-recording summaries.

**Read on the Mac, not judged.** Nothing in path F is implemented. FIELD
FAIL / O2 OPEN and review-006 pending are unchanged.

Prompt for the Windows agent (the user forwards it):

```text
S11 FER-1 읽기 전용 요청 — 저장된 bundle의 FULL debug trace에서 프레임별 FULL 증거가 어디서 멈추는지 읽는다. 검출기 실행 없음.
튜닝·Recipe/ROI/margin/임계값 변경·재실행은 하지 마. 사람 확인은 없다.
값만 원문 그대로 돌려주고 판정·수정 제안 없이 멈춰. bundle은 복사·수정하지 않는다.
출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = "src;."
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_full_evidence_readout.py
        f205eb2e222c6af2573169305ed5073ed686c50841ab87c676cddd777f2eedee
      - tests/diagnostics/s11_cadence_field.py
        986bd0374f760d6637847be034930bf681b439593b52f34332a0bd575d28e8db
      - tests/diagnostics/s11_layer_bottom_topology_2_field.py
        0830bef44a0a7d00e1ff5f700a9ad06de2913839117379bfd21d55f3aa8cf433
 0-2. bundle 2개(이름으로 찾는다, 복사·수정 금지):
      - B4 = step-7 oil_level_analysis_SPL4_B_ref_20261023_150316
      - B1 = step-7 oil_level_analysis_SPL1_B_ref_20261023_152751

1. 실행 9개 (소스 폴더에서, <out>은 새 출력 폴더, 명령은 한 줄로):
 X-1. python -m tests.diagnostics.s11_full_evidence_readout bundle --bundle <B4> --glass-name BASE --start 27.5 --end 63.0 --out <out>\spl4_base_full
 X-2. python -m tests.diagnostics.s11_full_evidence_readout bundle --bundle <B4> --glass-name BASE --start 20 --end 70 --no-frames --out <out>\spl4_base_context
 X-3. python -m tests.diagnostics.s11_full_evidence_readout bundle --bundle <B4> --glass-name Accum --start 20 --end 90 --no-frames --out <out>\spl4_accum_window
 X-4. python -m tests.diagnostics.s11_full_evidence_readout bundle --bundle <B1> --glass-name Accum --start 650 --end 700 --no-frames --out <out>\spl1_accum_window
 X-5. python -m tests.diagnostics.s11_full_evidence_readout bundle --bundle <B1> --glass-name BASE --start 650 --end 700 --no-frames --out <out>\spl1_base_window
 X-6. python -m tests.diagnostics.s11_full_evidence_readout bundle --bundle <B4> --glass-name BASE --no-frames --out <out>\spl4_base_all
 X-7. python -m tests.diagnostics.s11_full_evidence_readout bundle --bundle <B4> --glass-name Accum --no-frames --out <out>\spl4_accum_all
 X-8. python -m tests.diagnostics.s11_full_evidence_readout bundle --bundle <B1> --glass-name BASE --no-frames --out <out>\spl1_base_all
 X-9. python -m tests.diagnostics.s11_full_evidence_readout bundle --bundle <B1> --glass-name Accum --no-frames --out <out>\spl1_accum_all
 오류가 나면 그 실행만 멈추고 오류 원문을 돌려준다(다른 실행은 계속).

2. 각 실행의 stdout을 원문 그대로 돌려준다.
 - 첫 4줄(full evidence readout ... / status ... / gate ... / published full ...)과 마지막 줄(json ... sha256)은 반드시 포함.
 - run start ... 줄은 전부. 한 실행에서 40줄을 넘으면 처음 40줄과 전체 개수.
 - X-1의 frames 목록은 전부(약 72줄).

3. 머리줄: 소스 폴더, 0-1의 SHA-256 3개, 두 bundle의 전체 경로.
   값은 고치거나 반올림하지 않는다. 결론·판정·수정 제안 없이 멈춘다.
   path F는 구현되지 않았고 E4·top-exit·fill-owner gate는 기본 OFF로 남는다.
   FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## E1 partition readout request

**COMPLETE 2026-10-27** ([result](../50-diagnostics/s11/2026-10-27-partition-contradiction-readout.md#windows-readout--2026-10-27-rerun)):
neither scope frees SPL#4's level at 25.5–27.0 s; SPL#1 Accum scope A 2,644
rows, scope B 1,874.

The first relay was VOID: every run printed
`demoted 0` because the tool read the trace's top-level detector candidates,
which are written before sequence resolution and carry no resolved tier. The
tool now joins the sequence snapshot to them. On a local FULL-debug bundle
(sample2) its bundle path now equals its local path: 67 demoted rows, 0 join
misses. The prompt below is the rerun.

A read-only design input for the
[E1 draft](../20-architecture/s11-physical-interface-evidence-repair-design.md#october-27-foam-aware-partition-contradiction-e1).
The user agreed (2026-10-27): "응 진행하자". The local reading is
[FPC-1](../50-diagnostics/s11/2026-10-27-partition-contradiction-readout.md):
every local post-track demotion rests on texture alone, and both scopes are
broad. No detector run: the tool reads saved FULL-debug bundles.

**What it answers:**
- **SPL#4 BASE 25.5–27.0 s:** does scope A or B free the level's demoted rows
  near the review-015 marks?
- **SPL#1 Accum 669–678 s:** what do the scopes free there? Read against the
  review-017 and review-012 marks; the Foam-layer rows lie 142–187 px above
  the marks.
- **Both recordings, both Glasses:** the total exposure.

**Read on the Mac, not judged.** The result decides whether a narrow E1 scope
exists. Nothing in E1 is implemented. FIELD FAIL / O2 OPEN and review-006
pending are unchanged.

Prompt for the Windows agent (the user forwards it):

```text
S11 E1 읽기 전용 요청(재요청) — 저장된 bundle의 FULL debug trace를 고친 readout 도구로 다시 읽는다. 검출기 실행 없음.
첫 요청의 결과(모든 실행 demoted 0)는 도구 결함으로 무효다. 첫 출력 폴더는 지우지 말고 새 출력 폴더를 쓴다.
튜닝·Recipe/ROI/margin/임계값 변경·재실행은 하지 마. 사람 확인은 없다.
값만 원문 그대로 돌려주고 판정·수정 제안 없이 멈춰. bundle은 복사·수정하지 않는다.
출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = "src;."
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_partition_contradiction_readout.py
        a7315bf82a821895779b06a6a8d294147de235c92fc5650fc432caa069195e02
      - tests/diagnostics/s11_cadence_field.py
        986bd0374f760d6637847be034930bf681b439593b52f34332a0bd575d28e8db
      - tests/diagnostics/s11_layer_bottom_topology_2_field.py
        0830bef44a0a7d00e1ff5f700a9ad06de2913839117379bfd21d55f3aa8cf433
      - src/oil_tracker/adapters/vision/oil_candidate_evidence.py
        2d56e9c57dd8cbe44fd73c37e2ab62d26febd26819e1cc3c12250b18a062d5b6
 0-2. bundle 2개(이름으로 찾는다, 복사·수정 금지):
      - B4 = step-7 oil_level_analysis_SPL4_B_ref_20261023_150316
      - B1 = step-7 oil_level_analysis_SPL1_B_ref_20261023_152751

1. 실행 6개 (소스 폴더에서, <out>은 새 출력 폴더, 명령은 한 줄로):
 F-1. python -m tests.diagnostics.s11_partition_contradiction_readout bundle --bundle <B4> --glass-name BASE --start 20 --end 35
      --marks 24.0:730.0,24.5:657.5,25.0:634.3,25.5:550.0,26.0:490.5,26.5:426.0,27.0:382.5 --out <out>\spl4_base_window
 F-2. python -m tests.diagnostics.s11_partition_contradiction_readout bundle --bundle <B1> --glass-name Accum --start 660 --end 690
      --marks 669.0:501.0,669.5:506.0,670.0:513.0,670.5:492.0,671.0:476.0,671.5:471.0,672.0:493.5,672.5:490.0,673.0:498.5,673.5:501.5,674.0:493.0,674.5:495.5,675.0:499.5,675.5:499.5,676.0:488.5,676.5:468.0,677.0:456.0,677.5:432.5
      --out <out>\spl1_accum_window
 F-3. python -m tests.diagnostics.s11_partition_contradiction_readout bundle --bundle <B4> --glass-name BASE --no-frames --out <out>\spl4_base_all
 F-4. python -m tests.diagnostics.s11_partition_contradiction_readout bundle --bundle <B4> --glass-name Accum --no-frames --out <out>\spl4_accum_all
 F-5. python -m tests.diagnostics.s11_partition_contradiction_readout bundle --bundle <B1> --glass-name BASE --no-frames --out <out>\spl1_base_all
 F-6. python -m tests.diagnostics.s11_partition_contradiction_readout bundle --bundle <B1> --glass-name Accum --no-frames --out <out>\spl1_accum_all
 오류가 나면 그 실행만 멈추고 오류 원문을 돌려준다(다른 실행은 계속).

2. 각 실행의 stdout을 원문 그대로 돌려준다.
 - 첫 줄(partition contradiction readout ... | demoted | texture-only | scope A | scope B)과 마지막 줄(json ... sha256)은 반드시 포함.
 - F-1, F-2의 frames 목록과 mark 근처 행 목록은 전부. mark 근처 행이 실행마다 80줄을 넘으면 처음 80줄과 전체 개수.

3. 머리줄: 소스 폴더, 0-1의 SHA-256 4개, 두 bundle의 전체 경로.
   값은 고치거나 반올림하지 않는다. 결론·판정·수정 제안 없이 멈춘다.
   E1·E2는 구현되지 않았고 E4·top-exit·fill-owner gate는 기본 OFF로 남는다.
   FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Review-017 E2 hit-frame review

**COMPLETE 2026-10-27** ([result](../50-diagnostics/s11/2026-10-27-owner-above-readout.md#review-017-result--2026-10-27)):
SPL#1 Accum 669.5–671.5 s COST ×3; SPL#4 Accum all Foam (66.0 s UNREAD).

The user asked (2026-10-27): "review017 진행하고
확인해서 E2가 구현 할 의미가 있는지 한번 확인해보자". No detector run.
- **Task:** the user marks the Oil boundary on raw zooms of the four E2 hits
  that lack reviewed truth, plus neighbours and an anchor:
  - SPL#1 Accum 669.0–672.0 s, 7 panels; 672.0 s is review-012's anchor;
  - SPL#4 Accum 65.0–67.0 s, 5 panels.
- **Coordinates:** `read-marks` turns the marks into source coordinates, so
  only text comes back.

**Pre-registered (judged on the Mac):** the
[review-017 readings](../50-diagnostics/s11/2026-10-27-owner-above-readout.md#review-017--readings-frozen-2026-10-27-before-its-output):
- each hit is COST, GAIN or UNREAD against the mark ± C1;
- the tally is read by the user.

**Stop:** a SHA-256 mismatch, a missing file, a `STOP` line (other than the
one allowed re-save) or an error. The agent reports it and does not retry.

Prompt for the Windows agent (the user forwards it):

```text
S11 review-017 요청 — SPL#1 Accum 669.0~672.0초와 SPL#4 Accum 65.0~67.0초 원본 확대 이미지에 사용자가 Oil 경계를 표시한다. 검출기 실행 없음.
튜닝·Recipe/세션 변경·재실행은 하지 마. 값은 도구 출력과 사용자 말을 원문 그대로 돌려줘.
요약·재구성·판정·수정 제안 없이 멈춰. 출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_review_zoom.py
        34378c1dbbe229ba3b6961d870adc8bf984fb4763627bd4783ba6e41610a7363
 0-2. 쓰는 파일(복사·수정 금지):
      - SPL#1: review-012에서 쓴 SPL#1 영상, step-7 bundle oil_level_analysis_SPL1_B_ref_20261023_152751 안의
        recipe_snapshot.oilrecipe와 tracking_data.csv
      - SPL#4: SPL#4_Cooling_onoff_#2.mp4 (53165455 bytes인지 확인), step-7 bundle
        oil_level_analysis_SPL4_B_ref_20261023_150316 안의 recipe_snapshot.oilrecipe와 tracking_data.csv
 0-3. 새 출력 폴더 <out>를 만든다(예: C:\review017_out).

1. 프레임 고르기 — 각 bundle의 tracking_data.csv에서 Accum Glass 행의 frame_index를 timestamp_sec 순서대로 모은다
   (glass_id는 recipe_snapshot의 Accum Glass id):
 - S1 = SPL1_B_ref, 669.0 <= timestamp_sec < 672.25 (기대 7개: 16040, 16052, 16064, 16076, 16088, 16100, 16112)
 - S4 = SPL4_B_ref, 65.0 <= timestamp_sec < 67.25 (기대 5개: 1950, 1965, 1980, 1995, 2010)
 기대와 다르면 실제 값을 쓰고 머리줄에 그대로 적는다.

2. 확대 이미지 만들기 — 소스 폴더에서:
   python -m tests.diagnostics.s11_review_zoom prepare --video <SPL#1 영상> --recipe <SPL1_B_ref 폴더>\recipe_snapshot.oilrecipe --glass-name Accum
     --frames <S1을 쉼표로 이은 값> --review-id review-017 --out <out>\review017_spl1
   python -m tests.diagnostics.s11_review_zoom prepare --video <SPL#4 영상> --recipe <SPL4_B_ref 폴더>\recipe_snapshot.oilrecipe --glass-name Accum
     --frames <S4를 쉼표로 이은 값> --review-id review-017 --out <out>\review017_spl4
   (Glass 이름이 Accum이 아니면 Recipe의 이름을 그대로 쓴다.) 각 폴더에 review-zoom.png와 review-zoom.json이 생긴다.
   stdout(JSON)은 원문 그대로 보관한다.

3. 두 review-zoom.png를 하나씩 사용자에게 열어 주고 이렇게 묻는다(문장 그대로, 두 이미지 모두):
   "각 칸에서 엄격 기준의 Oil 경계(촘촘한 Foam이 끝나는 곳, 그 아래 기포 섞인 구간부터 Oil)를 빨간색 짧은 가로선 하나로 표시해 주세요.
    촘촘한 경계가 무너져 특정하기 어려우면 대략 표시하고 '대략'이라고, 촘촘한 경계가 안 보이면 Foam 영역의 최하단을 표시하고
    '최하단'이라고, 가득 차서 경계가 보이지 않으면 표시 없이 '가득'이라고, Oil 경계가 안 보이면 '안 보임'이라고 칸별로 알려 주세요.
    경계 말고 다른 선(튐, 앞쪽 호, 흘러내린 자국 등)이 눈에 띄면 표시하지 말고 칸별로 말로만 알려 주세요.
    이미지 크기는 바꾸지 말고 같은 크기로 저장해 주세요."
   사용자가 저장한 파일마다:
     python -m tests.diagnostics.s11_review_zoom read-marks --manifest <out>\review017_spl1\review-zoom.json --marked <SPL#1 표시한 파일>
     python -m tests.diagnostics.s11_review_zoom read-marks --manifest <out>\review017_spl4\review-zoom.json --marked <SPL#4 표시한 파일>
   "STOP"이 나오면(크기가 다름) 사용자에게 원래 크기로 다시 저장해 달라고 하고 한 번만 다시 읽는다.

4. 돌려줄 것 — 원문 그대로. 값은 고치거나 반올림하지 않는다.
 - 머리줄: 소스 폴더, 0-1의 SHA-256, 두 영상 경로와 크기, 1의 S1·S4 frame_index.
 - 각 prepare stdout에서: video.sha256, video.size_bytes, recipe.sha256, glass(id, name, ellipse),
   zoom_source_xyxy, scale, image.sha256, frames(frame_index, decoded_time_sec).
 - 표 R1(SPL#1), 표 R4(SPL#4) — 칸별 한 줄: frame | decoded_time_sec | 표시 수 | y_range | marks(x:y, 최대 8개) | 사용자 말(원문)
   각 표 머리줄에 read-marks의 marked_image.sha256과 changed_not_red_px를 적는다.
 - 이미지 원본(review-zoom.png, 표시한 파일)은 Windows에 보존한다(예: 0.Windows_diagnostic\data\reviews\review-017\).

5. 결론·판정 없이 멈춘다. E2는 구현되지 않았고 E4·top-exit·fill-owner gate는 기본 OFF로 남는다.
   FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## E2 owner-above readout request

**COMPLETE 2026-10-27** ([result](../50-diagnostics/s11/2026-10-27-owner-above-readout.md#windows-readout--2026-10-27)):
SPL#4 BASE 0 hits (nothing admitted above 0018 at 27.0–34.5 s); SPL#4 Accum
1; SPL#1 BASE not exercised; SPL#1 Accum 7.

A read-only design input for the
[E2 draft](../20-architecture/s11-physical-interface-evidence-repair-design.md#october-27-undercut-fill-owner-e2);
the local reading is [OAR-1](../50-diagnostics/s11/2026-10-27-owner-above-readout.md).
No detector run: the new tool reads saved FULL-debug bundles.

**Bundles:**
- SPL#4: step-7 `SPL4_B_ref` (BASE, Accum) and the E4 `SPL4_C_coloc` (BASE);
- SPL#1: step-7 `SPL1_B_ref` (BASE, Accum).

**What it answers:**
- **SPL#4 BASE 27.5–34.0 s:** is an admitted tracklet more than 32 px above
  0018 in any of the 14 wrong-target rows? A context listing covers
  27.0–34.5 s, so near misses are visible too.
- **SPL#4 BASE 22.5–24.0 s (E4 arm):** are the co-located rows undercut?
- **SPL#1:** how many single-owner rows would E2 stop, and where? This is
  the long negative.

**Read on the Mac, not judged:** the result fills the draft's SPL#4 and SPL#1
predictions. Then the user decides whether E2 is frozen. Nothing in E2 is
implemented. FIELD FAIL / O2 OPEN and review-006 pending are unchanged.

Prompt for the Windows agent (the user forwards it):

```text
S11 E2 읽기 전용 요청 — 저장된 bundle의 FULL debug trace를 새 readout 도구로 읽는다. 검출기 실행 없음.
튜닝·Recipe/ROI/margin/임계값 변경·재실행은 하지 마. 사람 확인은 없다.
값만 원문 그대로 돌려주고 판정·수정 제안 없이 멈춰. bundle은 복사·수정하지 않는다.
출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = "src;."
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_owner_above_readout.py
        5f31ad216c5d2f9218891100ee40b41cf6d8adc265398b4f3de5ee32facf76c9
      - tests/diagnostics/s11_cadence_field.py
        986bd0374f760d6637847be034930bf681b439593b52f34332a0bd575d28e8db
      - tests/diagnostics/s11_layer_bottom_topology_2_field.py
        0830bef44a0a7d00e1ff5f700a9ad06de2913839117379bfd21d55f3aa8cf433
 0-2. bundle 3개(이름으로 찾는다, 복사·수정 금지):
      - B4 = step-7 oil_level_analysis_SPL4_B_ref_20261023_150316
      - C4 = E4 oil_level_analysis_SPL4_C_coloc_20261027_145145
      - B1 = step-7 oil_level_analysis_SPL1_B_ref_20261023_152751

1. 실행 5개 (소스 폴더에서, <out>은 새 출력 폴더):
 R-1. python -m tests.diagnostics.s11_owner_above_readout --bundle <B4> --glass-name BASE --context 27.0 34.5 --out <out>\spl4_ref_base
 R-2. python -m tests.diagnostics.s11_owner_above_readout --bundle <B4> --glass-name Accum --out <out>\spl4_ref_accum
 R-3. python -m tests.diagnostics.s11_owner_above_readout --bundle <C4> --glass-name BASE --context 22.5 24.0 --out <out>\spl4_coloc_base
 R-4. python -m tests.diagnostics.s11_owner_above_readout --bundle <B1> --glass-name BASE --out <out>\spl1_ref_base
 R-5. python -m tests.diagnostics.s11_owner_above_readout --bundle <B1> --glass-name Accum --out <out>\spl1_ref_accum
 오류가 나면 그 실행만 멈추고 오류 원문을 돌려준다(다른 실행은 계속).

2. 각 실행의 stdout을 원문 그대로 돌려준다.
 - 첫 줄(owner-above readout ... | step | rows | single-owner published | hits)은 반드시 포함.
 - hits 목록은 실행마다 최대 60줄, 넘으면 처음 60줄과 전체 개수.
 - context 목록(R-1, R-3)은 전부.
 - 마지막 줄(json ... sha256 ...)은 반드시 포함.

3. 머리줄: 소스 폴더, 0-1의 SHA-256 3개, 세 bundle의 전체 경로.
   값은 고치거나 반올림하지 않는다. 결론·판정·수정 제안 없이 멈춘다.
   E2는 구현되지 않았고 E4·top-exit·fill-owner gate는 기본 OFF로 남는다.
   FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## E4 SPL#4 comparison request

**COMPLETE 2026-10-27 / PASS** ([receipt](../60-evidence/s11/2026-10-27-fill-owner-colocation-local.md#windows-spl4-comparison--2026-10-27)):
identity PASS; exactly 23.0 and 23.5 s co-located within 32 px of the marks;
every other row equal. BASE review events now start at 24.0 s.

The Windows check frozen with the
[co-located fill owners (E4)](../20-architecture/s11-physical-interface-evidence-repair-design.md#october-27-co-located-fill-owners-e4).
The [local checks](../60-evidence/s11/2026-10-27-fill-owner-colocation-local.md)
matched the frame prediction but stopped on sample5 event changes outside the
predicted frames. The user accepted those changes and chose to go on
(2026-10-27): "1번으로 진행하자. 범위 밖 변경이지만 오히려 신뢰도가 올라가는
변경으로 생각됨". This is a comparison, not field qualification.

**Runs:** SPL#4 0–90 s, the step-7 `SPL4_B_ref` session (2 fps, FULL debug,
compressor start 10.0 s, both Glasses EMPTY), two runs on the same source.
- `SPL4_C_ref`: IFO v2 + top-exit v3.
- `SPL4_C_coloc`: the same plus E4 (`fill_owner_colocation=True`).

**Pre-registered (judged on the Mac):**
- **Identity:** `SPL4_C_ref` equals step-7 `SPL4_B_ref` in every tracking row.
  Since step 7, `src` changed only in default-OFF options (fast-rise, E4) and
  in output-identical speed work (step 11 confirmed it).
- **Pass (frozen with the design):**
  - BASE: exactly 23.0 and 23.5 s become `FILL_OWNER_COLOCATED`;
  - each publishes a numeric row within 32 px of the review-015 mark (Y768.0,
    Y761.5);
  - every other BASE and Accum row is equal.
- **Events and retrospective:** not in the frozen condition. They are listed
  and read on the Mac against the reviewed truth (review-015/016: BASE Oil FULL
  from 27.5 s). Sample5 showed that added rows can change them.
- **Stop:** a hash or identity mismatch, a wrong resolver version or a run
  error. The agent stops and reports.

**Source:** latest `main` (E4 at `9ee11a4`); the request lists four SHA-256
values. No Recipe, ROI, margin, threshold or session change. E4, top-exit and
the gate stay default OFF; FIELD FAIL / O2 OPEN and review-006 pending are
unchanged.

Prompt for the Windows agent (the user forwards it):

```text
S11 E4 비교 요청 — SPL#4 0–90초, 기준 1개 + 후보(E4) 1개 실행. 읽기·비교만 하고 판정은 Mac에서 한다.
튜닝·Recipe/ROI/margin/임계값 변경·추가 재실행은 하지 마. 사람 확인은 없다.
값만 원문 그대로 돌려주고 판정·수정 제안 없이 멈춰. 새 bundle은 Windows에 보존한다.
출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - src/oil_tracker/adapters/vision/oil_phase_lifecycle.py
        39e214fe4ae038615a149d1c8106d44b830cd20ceefc376f54294b8c67b7ecfa
      - src/oil_tracker/adapters/vision/opencv_phase_detector.py
        64a0bb5ebd90bf1b569495fdc4707ea3965cbe7fbe193bdeeeeaeb77eba002cd
      - src/oil_tracker/adapters/vision/observation_sequence_resolver.py
        f4fc2fbc4f2c1b9366d193fd3cd0ff68b52c6f5283377478092e1d8959983461
      - src/oil_tracker/adapters/vision/oil_observation_resolver.py
        7e3b430d540a4363efc6d632693c5d629a7ccd2ccb8e45f9fa37528d72e382a3
 0-2. 영상·Recipe·세션은 step-7의 SPL4_B_ref(oil_level_analysis_SPL4_B_ref_20261023_150316)와 같다.
      - 영상: SPL#4_Cooling_onoff_#2.mp4(53165455 bytes), Recipe: sample4_test_artifact_R22.oilrecipe(수정하지 않는다)
      - 0–90초, 2fps, FULL debug, compressor_start 10.0초,
        두 Glass initial_state EMPTY_NO_INTERFACE(메모리의 Recipe와 세션 initial_state_confirmations, Recipe 파일은 그대로)
      - headless 방식도 step-7과 같다(AnalysisPipeline + OutputBundleStore + JsonlDebugTraceWriterFactory).
        cost-first/RGB/Local XY/fill_owner_contest/fast_rise_association은 OFF, Glass 병렬 옵션은 쓰지 않는다.

G. 비교 실행 2개 (같은 소스, 차이는 fill_owner_colocation 하나)
 G-1. 기준: OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True), run_name "SPL4_C_ref"
 G-2. 후보: OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True, fill_owner_colocation=True),
      run_name "SPL4_C_coloc"
 G-3. trace의 sequence_resolver_version: 둘 다 "+initial-full-observation-v2"와 "+top-exit-full-v3"가 있어야 하고,
      "+fill-owner-colocation-v1"은 후보에만 있어야 한다. 아니면 멈추고 값만 알려줘.

표기:
 - 행 = tracking_data.csv 한 줄. 시간은 timestamp_sec. 목록은 frame/time으로 쓴다.
 - S = debug record의 sequence.state, P = S.sequence_material_phase_diagnostics, C = sequence.candidates[].
   키가 없으면 MISSING, null이면 null.
 - 다른 행 = 같은 (glass_id, frame_index)에서 fill_state, raw_oil_air_level_y, raw_foam_front_y,
   oil_is_valid, foam_is_valid, flags 중 하나라도 다른 행.
 - 선택 후보 = C 중 selected가 true인 항목의 canonical_y:tracklet_id, 없으면 "없음".

1. 머리줄: 두 run_id·run_name, 소스 폴더, 0-1의 SHA-256 4개, 두 sequence_resolver_version, 두 bundle 경로,
   영상 SHA-256·size·fps·frame_count, Recipe SHA-256, Glass별 행 수(기대 181),
   (glass_id, frame_index) 대응 결과(중복·누락·timestamp 불일치 수).

2. 표 I — 신원: SPL4_C_ref ↔ step-7 SPL4_B_ref. Glass별 다른 행 수와 목록(최대 10개).

3. 표 G — Glass별(BASE/Accum):
 a. 기준 ↔ 후보 다른 행 수
 b. 후보에서 S.sequence_material_phase_reason이 FILL_OWNER_COLOCATED인 행 수와 그 행들의 frame/time 전부
 c. 기준·후보 각각 S.sequence_material_phase_reason별 행 수(FILL_OWNER_AMBIGUOUS, FILL_OWNER_COLOCATED만)
 d. 다른 행 목록(Glass별 최대 40개, 넘으면 개수만), 각 한 줄:
    frame | time | 기준 fill_state / raw_oil_air_level_y | 후보 fill_state / raw_oil_air_level_y |
    기준 S.sequence_material_phase_reason | 후보 S.sequence_material_phase_reason |
    후보 P.dynamic_fill_owner_ids | 후보 P.allowed_tracklet_ids | 후보 선택 후보
 e. 후보의 FILL_OWNER_COLOCATED 행마다, C 중 kind = oil_air이고 tracklet_id가 P.dynamic_fill_owner_ids에 있는 항목 전부,
    각 한 줄: time | frame | canonical_y | tracklet_id | selected

4. 표 E — 이벤트와 재해석(두 bundle 비교):
 a. retrospective_interpretation.json의 Glass별 status, start_time_sec, end_time_sec, reason(원문) — 기준과 후보
 b. events.csv에서 기준에만 있는 줄과 후보에만 있는 줄(capture 경로 열은 비교에서 빼고, 줄은 원문 그대로).
    Glass별 최대 20줄, 넘으면 개수만.
 c. review_index.json의 Glass별 result_status와 effective_state_aware_coverage_ratio — 기준과 후보

5. 머리줄과 표 I, G, E를 원문 그대로 돌려준다. 값은 고치거나 반올림하지 않는다.
   결론·판정·수정 제안 없이 멈춘다. E4·top-exit·fill-owner gate는 기본 OFF로 남고,
   FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Step-15 level peer readout

**COMPLETE 2026-10-27** ([result](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#step-15-result--2026-10-27)):
LOWER-OWNER-PEER. The user chose (2026-10-27, "1번으로 진행하자") a
read-only readout of the same-frame partition peers of the demoted level
rows. No detector runs.

**Pre-registered (judged on the Mac):** P1–P3 and the outcome in
[FOR-2](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#step-15--readings-frozen-2026-10-27-before-its-output).
The tool's local check passed (run `s11-level-peer-check-20261027-001`).

**Stop:** a SHA-256 mismatch, a missing file, a `STOP` line or an error. The
agent reports it and does not retry.

Prompt for the Windows agent (the user forwards it):

```text
S11 step-15 읽기 전용 요청 — SPL4_B_ref 저장 trace에서 강등된 수면 후보와 같은 프레임의 partition 후보를 읽는다. 검출기 실행 없음.
튜닝·Recipe/세션 변경·재실행은 하지 마. 값은 도구 stdout을 원문 그대로 돌려줘.
요약·재구성·개수 세기·판정·수정 제안 없이 멈춰. 출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_level_peer_readout.py
        d66616490b7e1b5275194af790de63f803258c8f8a1d808d731322f2515fb87d
      - tests/diagnostics/s11_level_authority_readout.py
        60175903819fe4a36da80af63b694dd824c4e2eb406fa57e30662f46e060a8d5
      - tests/diagnostics/s11_level_coverage_readout.py
        9d085a23c708dd9404521896907203f9545898e9419cb47ca97ed4370c9d27f1
      - tests/diagnostics/s11_cadence_field.py
        986bd0374f760d6637847be034930bf681b439593b52f34332a0bd575d28e8db
      - tests/diagnostics/s11_layer_bottom_topology_2_field.py
        0830bef44a0a7d00e1ff5f700a9ad06de2913839117379bfd21d55f3aa8cf433
 0-2. 쓰는 bundle(복사·수정 금지): step-7의 oil_level_analysis_SPL4_B_ref_20261023_150316
      (tracking_data.csv, recipe_snapshot.oilrecipe, debug\debug_trace.jsonl 확인)
 0-3. 새 출력 폴더 <out>를 만든다(예: C:\step15_out).

R. 읽기 1개 — 소스 폴더에서:
 R-1. python -m tests.diagnostics.s11_level_peer_readout --bundle <SPL4_B_ref 폴더> --glass-name BASE
        --marks 24.5:657.5,25.0:634.3,25.5:550.0,26.0:490.5,26.5:426.0,27.0:382.5 --out <out>\r1

1. 돌려줄 것 — stdout 원문 그대로. 값은 고치거나 반올림하지 않는다.
 - 머리줄: 소스 폴더, 0-1의 SHA-256 5개, bundle 경로.
 - R-1 전체: 첫 줄("level peer readout …"), "-- frames" 머리줄과 행 전부,
   "-- partition peers" 머리줄과 행 전부, 마지막 "json … sha256" 줄.

2. 결론·판정 없이 멈춘다. FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Step-14 level authority readout

**COMPLETE 2026-10-27** ([result](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#step-14-result--2026-10-27)):
RECURRENCE-LED. The user chose (2026-10-27, "응 그렇게 진행하자") a
read-only readout of why the reviewed level rows at 25.5–27.0 s fall below
the builder tier. No detector runs.

**Pre-registered (judged on the Mac):** A1–A3 and the outcome in
[FOR-2](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#step-14--readings-frozen-2026-10-27-before-its-output).
The tool's local check passed (run `s11-level-authority-check-20261027-001`).

**Stop:** a SHA-256 mismatch, a missing file, a `STOP` line or an error. The
agent reports it and does not retry.

Prompt for the Windows agent (the user forwards it):

```text
S11 step-14 읽기 전용 요청 — SPL4_B_ref 저장 trace에서 수면 표시 근처 후보의 등급(authority) 근거를 읽는다. 검출기 실행 없음.
튜닝·Recipe/세션 변경·재실행은 하지 마. 값은 도구 stdout을 원문 그대로 돌려줘.
요약·재구성·개수 세기·판정·수정 제안 없이 멈춰. 출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_level_authority_readout.py
        60175903819fe4a36da80af63b694dd824c4e2eb406fa57e30662f46e060a8d5
      - tests/diagnostics/s11_level_coverage_readout.py
        9d085a23c708dd9404521896907203f9545898e9419cb47ca97ed4370c9d27f1
      - tests/diagnostics/s11_cadence_field.py
        986bd0374f760d6637847be034930bf681b439593b52f34332a0bd575d28e8db
      - tests/diagnostics/s11_layer_bottom_topology_2_field.py
        0830bef44a0a7d00e1ff5f700a9ad06de2913839117379bfd21d55f3aa8cf433
 0-2. 쓰는 bundle(복사·수정 금지): step-7의 oil_level_analysis_SPL4_B_ref_20261023_150316
      (tracking_data.csv, recipe_snapshot.oilrecipe, debug\debug_trace.jsonl 확인)
 0-3. 새 출력 폴더 <out>를 만든다(예: C:\step14_out).

R. 읽기 1개 — 소스 폴더에서:
 R-1. python -m tests.diagnostics.s11_level_authority_readout --bundle <SPL4_B_ref 폴더> --glass-name BASE
        --marks 24.5:657.5,25.0:634.3,25.5:550.0,26.0:490.5,26.5:426.0,27.0:382.5 --out <out>\r1

1. 돌려줄 것 — stdout 원문 그대로. 값은 고치거나 반올림하지 않는다.
 - 머리줄: 소스 폴더, 0-1의 SHA-256 4개, bundle 경로.
 - R-1 전체: 첫 줄("level authority readout …"), "-- candidates" 머리줄과 행 전부, 마지막 "json … sha256" 줄.

2. 결론·판정 없이 멈춘다. FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Step-13 coverage readout and review-016

**COMPLETE 2026-10-27** ([result](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#step-13-result--2026-10-27)):
ELIGIBILITY; Oil FULL onset 27.5 s. The user chose (2026-10-27): correct the SPL#4 BASE
truth to the review, run review-016, and check candidate coverage ("3.
확인하자"). No detector runs.
- **R:** the read-only level coverage readout on `SPL4_B_ref` at the
  review-015 marks, 24.0–27.0 s.
- **V:** review-016, the user marks SPL#4 BASE 27.0–30.0 s on a raw zoom.

**Pre-registered (judged on the Mac):** C1–C4 and M1–M3 in
[FOR-2](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#step-13--readings-frozen-2026-10-27-before-its-output).
The tool's local check passed (run `s11-level-coverage-check-20261027-001`).

**Stop:** a SHA-256 mismatch, a missing file, a `STOP` line (other than the
one allowed re-save) or an error. The agent reports it and does not retry.

Prompt for the Windows agent (the user forwards it):

```text
S11 step-13 요청 — (R) SPL4_B_ref 저장 trace에서 수면 표시 근처 후보 읽기 + (V) review-016 사람 표시. 검출기 실행 없음.
튜닝·Recipe/세션 변경·재실행은 하지 마. 값은 도구 출력과 사용자 말을 원문 그대로 돌려줘.
요약·재구성·개수 세기·판정·수정 제안 없이 멈춰. 출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_level_coverage_readout.py
        9d085a23c708dd9404521896907203f9545898e9419cb47ca97ed4370c9d27f1
      - tests/diagnostics/s11_cadence_field.py
        986bd0374f760d6637847be034930bf681b439593b52f34332a0bd575d28e8db
      - tests/diagnostics/s11_layer_bottom_topology_2_field.py
        0830bef44a0a7d00e1ff5f700a9ad06de2913839117379bfd21d55f3aa8cf433
      - tests/diagnostics/s11_review_zoom.py
        34378c1dbbe229ba3b6961d870adc8bf984fb4763627bd4783ba6e41610a7363
 0-2. 쓰는 파일(복사·수정 금지):
      - bundle: step-7의 oil_level_analysis_SPL4_B_ref_20261023_150316
        (tracking_data.csv, recipe_snapshot.oilrecipe, debug\debug_trace.jsonl 확인)
      - 영상: SPL#4_Cooling_onoff_#2.mp4 (53165455 bytes인지 확인)
 0-3. 새 출력 폴더 <out>를 만든다(예: C:\step13_out).

R. 읽기 1개 — 소스 폴더에서:
 R-1. python -m tests.diagnostics.s11_level_coverage_readout --bundle <SPL4_B_ref 폴더> --glass-name BASE
        --marks 24.0:730.0,24.5:657.5,25.0:634.3,25.5:550.0,26.0:490.5,26.5:426.0,27.0:382.5 --out <out>\r1

V. review-016 — SPL#4 BASE 27.0~30.0초, 사람 표시
 V-1. 소스 폴더에서:
      python -m tests.diagnostics.s11_review_zoom prepare --video <SPL#4 영상> --recipe <SPL4_B_ref 폴더>\recipe_snapshot.oilrecipe --glass-name BASE
        --frames 810,825,840,855,870,885,900 --review-id review-016 --out <out>\review016
 V-2. review-zoom.png를 사용자에게 열어 주고 이렇게 묻는다(문장 그대로):
      "각 칸에서 Oil 수면(아래쪽 Oil 몸체가 끝나고 위쪽 공기나 Foam이 시작되는 경계)을 빨간색 짧은 가로선 하나로 표시해 주세요.
       Foam이 덮고 있으면 Foam 아래 Oil이 시작되는 엄격 경계를 표시하고 'Foam 아래'라고, 특정하기 어려우면 대략 표시하고 '대략'이라고,
       Oil이 가득 차서 수면이 없으면 표시 없이 '가득'이라고, 수면이 안 보이면 '안 보임'이라고 칸별로 알려 주세요.
       Oil이 뿌옇거나(잔여 기포) 투명해지는 정도가 보이면 칸별로 말로 알려 주세요. 이미지 크기는 바꾸지 말고 같은 크기로 저장해 주세요."
      사용자가 저장한 파일로:
        python -m tests.diagnostics.s11_review_zoom read-marks --manifest <out>\review016\review-zoom.json --marked <표시한 파일>
      "STOP"이 나오면(크기가 다름) 사용자에게 원래 크기로 다시 저장해 달라고 하고 한 번만 다시 읽는다.

1. 돌려줄 것 — 모두 원문 그대로. 값은 고치거나 반올림하지 않는다.
 - 머리줄: 소스 폴더, 0-1의 SHA-256 4개, bundle 경로, 영상 경로와 크기.
 - R-1 stdout 전체: 첫 줄("level coverage readout …"), "-- frames" 머리줄과 행 전부,
   "-- near groups" 머리줄과 행 전부, 마지막 "json … sha256" 줄.
 - V-1 prepare stdout에서: video.sha256, recipe.sha256, glass(id, name), zoom_source_xyxy, scale, image.sha256,
   frames 7개(frame_index, decoded_time_sec).
 - 표 R16 — 칸별 한 줄: frame | decoded_time_sec | 표시 수 | y_range | marks(x:y, 최대 8개) | 사용자 말(원문)
   머리줄에 read-marks의 marked_image.sha256과 changed_not_red_px를 적는다.
 - 이미지 원본은 Windows에 보존한다(예: 0.Windows_diagnostic\data\reviews\review-016\).

2. 결론·판정 없이 멈춘다. FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Review-015 SPL#4 fast-rise level review

**COMPLETE 2026-10-27** ([result](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#review-015-result--2026-10-27)):
OWNER-LEVEL at 22.5–24.0 s; the level is above both owners at 24.5–27.0 s.
The user chose (2026-10-27, "그렇게하자") to have the
level reviewed on SPL#4 before the questions-2/3 design is frozen. No detector
runs. The user marks the Oil surface on a raw zoom of the original video, and
`read-marks` turns the marks into source coordinates, so only text comes back.

**What it answers:** the
[review-015 readings](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#review-015--readings-frozen-2026-10-27-before-its-output)
of FOR-2. Is the level above both fill owners in SPL#4 BASE 22.5–27.0 s, or is
an owner (0035 in particular) the level?

**Material:** SPL#4 BASE 20.0–27.0 s, 15 panels (source frames 600–810, every
15th). The Recipe is the `SPL4_B_ref` bundle's snapshot.

**Pre-registered (judged on the Mac):** K1–K4 and the outcome in FOR-2.

**Stop:** a SHA-256 mismatch, a missing file, a `STOP` line (other than the
one allowed re-save) or an error. The agent reports it and does not retry.

Prompt for the Windows agent (the user forwards it):

```text
S11 review-015 요청 — SPL#4 BASE 20.0~27.0초 원본 확대 이미지에 사용자가 Oil 수면을 표시한다. 검출기 실행 없음.
튜닝·Recipe/세션 변경·재실행은 하지 마. 값은 도구 출력과 사용자 말을 원문 그대로 돌려줘.
요약·재구성·판정·수정 제안 없이 멈춰. 출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_review_zoom.py
        34378c1dbbe229ba3b6961d870adc8bf984fb4763627bd4783ba6e41610a7363
 0-2. 쓰는 파일(복사·수정 금지):
      - 영상: SPL#4_Cooling_onoff_#2.mp4 (53165455 bytes인지 확인)
      - Recipe: step-7 bundle oil_level_analysis_SPL4_B_ref_20261023_150316 안의 recipe_snapshot.oilrecipe
 0-3. 새 출력 폴더 <out>를 만든다(예: C:\review015_out). review015 하위 폴더는 도구가 만든다.

1. 확대 이미지 만들기 — 소스 폴더에서:
   python -m tests.diagnostics.s11_review_zoom prepare --video <SPL#4 영상> --recipe <recipe_snapshot.oilrecipe> --glass-name BASE
     --frames 600,615,630,645,660,675,690,705,720,735,750,765,780,795,810 --review-id review-015 --out <out>\review015
   review-zoom.png와 review-zoom.json이 생긴다. stdout(JSON)은 원문 그대로 보관한다.

2. review-zoom.png를 사용자에게 열어 주고 이렇게 묻는다(문장 그대로):
   "각 칸에서 Oil 수면(아래쪽 Oil 몸체가 끝나고 위쪽 공기나 Foam이 시작되는 경계, 차오르는 중이면 지금 Oil이 올라온 높이)을
    빨간색 짧은 가로선 하나로 표시해 주세요. Foam이 덮고 있으면 Foam 아래 Oil이 시작되는 곳을 표시하고 'Foam 아래'라고,
    특정하기 어려우면 대략 표시하고 '대략'이라고, 가득 차서 수면이 보이지 않으면 표시 없이 '가득'이라고,
    수면이 안 보이면 '안 보임'이라고 칸별로 알려 주세요. 수면 말고 다른 경계(튐, 앞쪽 호, 줄기 등)가 눈에 띄면
    표시하지 말고 칸별로 말로만 알려 주세요. 이미지 크기는 바꾸지 말고 같은 크기로 저장해 주세요."
   사용자가 저장한 파일로:
     python -m tests.diagnostics.s11_review_zoom read-marks --manifest <out>\review015\review-zoom.json --marked <표시한 파일>
   "STOP"이 나오면(크기가 다름) 사용자에게 원래 크기로 다시 저장해 달라고 하고 한 번만 다시 읽는다.

3. 돌려줄 것 — 원문 그대로. 값은 고치거나 반올림하지 않는다.
 - 머리줄: 소스 폴더, 0-1의 SHA-256, 영상 경로와 크기.
 - 1의 prepare stdout에서: video.sha256, video.size_bytes, recipe.sha256, glass(id, name, ellipse),
   zoom_source_xyxy, scale, image.sha256, frames 15개(frame_index, decoded_time_sec).
 - 표 R — 칸별 한 줄: frame | decoded_time_sec | 표시 수 | y_range | marks(x:y, 최대 8개) | 사용자 말(원문)
   머리줄에 read-marks의 marked_image.sha256과 changed_not_red_px를 적는다.
 - 이미지 원본(review-zoom.png, 표시한 파일)은 Windows에 보존한다(예: 0.Windows_diagnostic\data\reviews\review-015\).

4. 결론·판정 없이 멈춘다. FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Step-12 fill-owner trace readout request

**COMPLETE 2026-10-27** ([receipt](../60-evidence/s11/2026-10-27-step12-windows-receipt.md)):
NOT CONFIRMED; W1 holds, W2 fails first on 0035. The user chose to check the question-1 reading first
("(B) 확인 먼저 하고 (A)로 넘어가는걸로 하자"). It reads the saved
`SPL4_B_ref` FULL trace only. It runs no detector and writes only a readout
file.

**What it answers:** the
[Windows trace readout readings](../50-diagnostics/s11/2026-10-27-fill-owner-recency-local.md#windows-trace-readout--readings-frozen-2026-10-27-before-its-output)
of FOR-1. Is SPL#4's 22.5–27.0 s ambiguity a reappearing 0018 whose new chain
is dynamic from its fixed confirmation fields?

**Readout:** `s11_fill_owner_trace_readout` on `SPL4_B_ref`, BASE 20.0–28.0 s.
Its local check passed on a sample5 FULL bundle.

**Pre-registered (judged on the Mac):** W1–W3 and the verdict in FOR-1.

**Stop:** a SHA-256 mismatch, a missing bundle file, a `STOP` line or an
error. The agent reports it and does not retry.

Prompt for the Windows agent (the user forwards it):

```text
S11 step-12 읽기 전용 요청 — step-7의 SPL4_B_ref bundle trace에서 fill owner 값을 뽑는다. 검출기 실행 없음.
튜닝·Recipe/세션 변경·재실행은 하지 마. 사람 확인은 없다.
값은 도구 stdout을 원문 그대로 돌려줘. 요약·재구성·개수 세기·판정·수정 제안 없이 멈춰.
출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_fill_owner_trace_readout.py
        2c50291e623b3b67e5d04a21cdcd7d6ba856b83f4e46f08d95966ae41e7f95cf
      - tests/diagnostics/s11_cadence_field.py
        986bd0374f760d6637847be034930bf681b439593b52f34332a0bd575d28e8db
      - tests/diagnostics/s11_layer_bottom_topology_2_field.py
        0830bef44a0a7d00e1ff5f700a9ad06de2913839117379bfd21d55f3aa8cf433
 0-2. 쓰는 bundle(복사·수정 금지):
      - SPL4_B_ref: step-7의 oil_level_analysis_SPL4_B_ref_20261023_150316
      tracking_data.csv, recipe_snapshot.oilrecipe, debug\debug_trace.jsonl이 있는지 확인한다.
 0-3. 새 출력 폴더 <out>를 만든다(예: C:\step12_out).

R. 읽기 1개 — 소스 폴더에서:
 R-1. python -m tests.diagnostics.s11_fill_owner_trace_readout --bundle <SPL4_B_ref 폴더> --glass-name BASE --start 20.0 --end 28.0 --out <out>\r1

1. 돌려줄 것 — 모두 stdout 원문 그대로. 값은 고치거나 반올림하지 않는다.
 - 머리줄: 소스 폴더, 0-1의 SHA-256 3개, bundle 경로.
 - R-1 전체: 첫 줄("fill-owner trace readout …"), "-- frames" 머리줄과 행 목록 전부,
   "-- owner rows" 머리줄과 행 목록 전부, 마지막 "json … sha256" 줄.

2. 결론·판정 없이 멈춘다. FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Step-11 speed timing request

**COMPLETE 2026-10-26** ([receipt](../60-evidence/s11/2026-10-26-step10-11-windows-receipt.md#step-11--speed-timing-and-identity)): identity PASS on all three runs. It was READY 2026-10-26, to run after step 10.
It measures speed steps (가)–(다) on Windows. The user chose the order "2는
가,나,다 순으로 하나씩 해보자". This is a timing and identity request, not
field qualification.

**What it answers:**
- whether each run still reproduces `SPL4_B_ref` in every row and, with a
  trace, in every trace byte;
- the Windows wall time against step 9 (T-1 224.9 s, T-2 90.9 s);
- for the parallel runs, how long the parent waited on the workers, which
  shows the critical path.

**Runs:** the step-7 `SPL4_B_ref` session, through
`tests/diagnostics/s11_cadence_field.py run`.

| Run | Rate / debug | Glass loop | Covers |
|---|---|---|---|
| S-1 | 2 fps / FULL | sequential | (가) staging rename, (다) background PNG |
| P-1 | 2 fps / FULL | parallel | (가), (나), (다) |
| P-2 | 2 fps / NONE | parallel | (나) |

Then three identity comparisons against `SPL4_B_ref`.

**Pre-registered (judged on the Mac):**
- all three reproduce the rows; S-1 and P-1 also reproduce the trace bytes;
- the parallel runs report `used True`;
- timing is reported, not scored.

**Stop:** a SHA-256 mismatch, a missing bundle file, a `STOP` line or a run
error. The agent reports it and does not retry.

**Source:** latest `main`. The parallel loop is opt-in and default OFF, and the
product is unchanged by it. No Recipe, session or detector-option change.
FIELD FAIL / O2 OPEN and review-006 pending are unchanged.

Prompt for the Windows agent (the user forwards it):

```text
S11 step-11 속도 측정 요청 — SPL#4를 2fps로 세 번(FULL 순차, FULL 병렬, NONE 병렬) 다시 실행하고, 신원 비교 3개를 돌린다.
튜닝·Recipe/ROI/margin/임계값/세션 변경·추가 재실행은 하지 마. 사람 확인은 없다.
값은 도구 stdout을 원문 그대로 돌려줘. 요약·재구성·개수 세기·판정·수정 제안 없이 멈춰. 새 bundle은 Windows에 보존한다.
출력 폴더 경로는 영문·숫자·밑줄만 쓴다.
실행 중에는 다른 무거운 작업을 하지 않는다(시간 측정이다). 병렬 실행은 Python 프로세스 3개를 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_cadence_field.py
        986bd0374f760d6637847be034930bf681b439593b52f34332a0bd575d28e8db
      - src/oil_tracker/application/services/parallel_glass_detection.py
        f543d4cc2f01c7e37b96e24da8a9471c65266e2165e7f4fa89398e4260ce8303
      - src/oil_tracker/application/services/detection_run.py
        904ba24240d4ec893afd09afd11100d3fc7bb7323f7212948a3c14c16f84f988
      - src/oil_tracker/application/services/analysis_pipeline.py
        263318e3cbcf049dc11158122ba96e7eaa8e83ad715380362ab35f16a8988cbf
      - src/oil_tracker/adapters/storage/jsonl_debug_trace_writer.py
        f205d5821a5c8689b58d8a03989cd89e2122d3aaf7af96b53ff489ed2be405ec
      - src/oil_tracker/adapters/storage/output_bundle_store.py
        f879f1a2fcb6b7e74c2082f5d8534bb3ba2cbea973ec6dd8241062f403282c34
      - src/oil_tracker/adapters/vision/opencv_phase_detector.py
        b73ddb1560c644b10f3e3e26a028b3e2ef5364775f091c3ae8b0ebb22264b87c
 0-2. step-7의 SPL4_B_ref bundle 폴더를 그대로 쓴다(복사·수정 금지).
 0-3. 새 출력 폴더 <out>를 만든다(예: C:\step11_out).

R. 실행 3개 — 소스 폴더에서, 이 순서대로 하나씩:
 R-1. S-1: python -m tests.diagnostics.s11_cadence_field run --reference-bundle <SPL4_B_ref 폴더> --out <out>\s1 --run-name SPL4_S1_2fps_full_seq
 R-2. P-1: python -m tests.diagnostics.s11_cadence_field run --reference-bundle <SPL4_B_ref 폴더> --out <out>\p1 --parallel-glasses --run-name SPL4_P1_2fps_full_par
 R-3. P-2: python -m tests.diagnostics.s11_cadence_field run --reference-bundle <SPL4_B_ref 폴더> --out <out>\p2 --debug none --parallel-glasses --run-name SPL4_P2_2fps_none_par
      "STOP: video not found"가 나오면 그 실행만 --video <SPL#4 영상 경로>를 붙여 한 번 다시 실행한다.
      다른 STOP이나 오류는 출력을 그대로 적고 멈춘다. 다시 시도하지 않는다.

C. 신원 비교 3개 — 소스 폴더에서:
 C-a. python -m tests.diagnostics.s11_cadence_field identity --reference <SPL4_B_ref 폴더> --trial <R-1 bundle> --out <out>\id_s1
 C-b. python -m tests.diagnostics.s11_cadence_field identity --reference <SPL4_B_ref 폴더> --trial <R-2 bundle> --out <out>\id_p1
 C-c. python -m tests.diagnostics.s11_cadence_field identity --reference <SPL4_B_ref 폴더> --trial <R-3 bundle> --out <out>\id_p2

1. 돌려줄 것 — 모두 stdout 원문 그대로. 값은 고치거나 반올림하지 않는다.
 - 머리줄: 소스 폴더, 0-1의 SHA-256 값 전부, SPL4_B_ref 경로.
 - R-1, R-2, R-3 전체: "run …", "bundle …", "parallel glasses …"(있으면), "window …", "timing …" 줄과 "-- stages" 목록 전부.
 - C-a, C-b, C-c 전체: 첫 세 줄, changed 목록(있으면), 마지막 "json … sha256" 줄.

2. 결론·판정 없이 멈춘다. FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Step-10 stage readout request

**COMPLETE 2026-10-26** ([receipt](../60-evidence/s11/2026-10-26-step10-11-windows-receipt.md#step-10--stage-readout)): S-A by the letter, dropped at phase, with a named limit. It was READY 2026-10-26. The user chose a
read-only follow-up on the step-9 C-1 bundle ("1-(a)로 진행하고"). It runs no
detector and writes only readout files.

**What it answers:** the
[stage follow-up](../50-diagnostics/s11/2026-10-26-cadence-diagnostic.md#stage-follow-up-frozen-2026-10-26-before-its-output).
Was a rising BASE tracklet admitted at 6 fps, and if so, at which path stage
was it dropped?

**Readouts:**
- **Q-1:** `s11_fast_rise_readout` on C-1, BASE 20.5–25.5 s.
- **Q-2:** `s11_cadence_field stages` on C-1, BASE 20.0–28.0 s.
- **Q-3:** `s11_cadence_field stages` on `SPL4_B_ref`, BASE 20.0–28.0 s.

**Pre-registered (judged on the Mac):** the rising-chain reading and S-A/S-B
of the stage follow-up.

**Stop:** a SHA-256 mismatch, a missing bundle file, a `STOP` line or an
error. The agent reports it and does not retry.

Prompt for the Windows agent (the user forwards it):

```text
S11 step-10 읽기 전용 요청 — step-9의 C-1(6fps) bundle과 SPL4_B_ref에서 단계별 값을 뽑는다. 검출기 실행 없음.
튜닝·Recipe/세션 변경·재실행은 하지 마. 사람 확인은 없다.
값은 도구 stdout을 원문 그대로 돌려줘. 요약·재구성·개수 세기·판정·수정 제안 없이 멈춰.
출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_cadence_field.py
        986bd0374f760d6637847be034930bf681b439593b52f34332a0bd575d28e8db
        (ZIP을 c9c22ba 시점에 받았다면 2b0925610b201eedc7b4a1f5d61837f6047f105335029aa8c642cdc404a34b7c도 맞다. stages 기능은 같다.)
      - tests/diagnostics/s11_fast_rise_readout.py
        96a5cab616d3db67d626f719ca48f0e7c2bbeb0a33bceffde88f8deb797cdbbc
      - tests/diagnostics/s11_layer_bottom_topology_2_field.py
        0830bef44a0a7d00e1ff5f700a9ad06de2913839117379bfd21d55f3aa8cf433
 0-2. 쓰는 bundle(복사·수정 금지):
      - C-1: step-9의 oil_level_analysis_SPL4_C1_6fps_full_20261026_150634
      - SPL4_B_ref: step-7의 oil_level_analysis_SPL4_B_ref_20261023_150316
      각 bundle에 tracking_data.csv, recipe_snapshot.oilrecipe, debug\debug_trace.jsonl이 있는지 확인한다.
 0-3. 새 출력 폴더 <out>를 만든다(예: C:\step10_out).

Q. 읽기 3개 — 소스 폴더에서:
 Q-1. python -m tests.diagnostics.s11_fast_rise_readout --work <out>\q1 --bundle <C-1 폴더> --glass-name BASE --start 20.5 --end 25.5
 Q-2. python -m tests.diagnostics.s11_cadence_field stages --bundle <C-1 폴더> --glass-name BASE --start 20.0 --end 28.0 --out <out>\q2
 Q-3. python -m tests.diagnostics.s11_cadence_field stages --bundle <SPL4_B_ref 폴더> --glass-name BASE --start 20.0 --end 28.0 --out <out>\q3

1. 돌려줄 것 — 모두 stdout 원문 그대로. 값은 고치거나 반올림하지 않는다.
 - 머리줄: 소스 폴더, 0-1의 SHA-256 3개, 두 bundle 경로.
 - Q-1 전체: 첫 세 줄, "-- rows" 목록 전부, "-- constant-velocity triplets" 목록 전부, 마지막 "json … sha256" 줄.
 - Q-2, Q-3 전체: "stages …" 줄, 머리줄, 행 목록 전부, 마지막 "json … sha256" 줄.

2. 결론·판정 없이 멈춘다. FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Step-9 combined request

**COMPLETE 2026-10-26 ([receipt](../60-evidence/s11/2026-10-26-step9-windows-receipt.md)).** Step 4 of the
order the user agreed ("응 순서에 동의함. 진행하자"). This is a diagnostic and
timing request, not field qualification.

**What it answers:**
- **CAD-1 cadence:** the
  [frozen protocol](../50-diagnostics/s11/2026-10-26-cadence-diagnostic.md).
  Does denser observation (6 fps) alone admit the SPL#4 BASE fast rise and
  close FULL inside the user's window?
- **Timing:** where a Windows run spends its time, at 2 fps with FULL debug
  and without a trace. This informs the next speed step
  ([RTP-1](../50-diagnostics/s11/2026-10-26-run-time-profile.md)).
- **B-1 on Windows:** `SPL4_B_ref` was written before the trace-cost change
  (`914c8e6`). T-1 must reproduce its rows and its trace bytes once the run ID
  is normalized.

**Runs:** the step-7 `SPL4_B_ref` session, through
`tests/diagnostics/s11_cadence_field.py`:

| Run | Rate | Debug |
|---|---|---|
| T-1 | 2 fps | FULL (as saved) |
| T-2 | 2 fps | NONE |
| C-1 | 6 fps | FULL (as saved) |

Then three comparisons: identity T-1, identity T-2 and cadence C-1, each
against `SPL4_B_ref`.

**Pre-registered (judged on the Mac):**
- readings C1–C5 and outcomes A–D of the CAD-1 protocol;
- T-1 identity first;
- timing is reported, not scored.

**Stop:** a SHA-256 mismatch, a missing bundle file, a `STOP` line or a run
error. The agent reports it and does not retry. The one exception is a
moved video, which gets a single rerun with `--video`.

**Source:** latest `main`. No Recipe, ROI, margin, threshold or session
change except the rate and debug level named per run. Top-exit, the gate and
the fast-rise association stay default OFF in the product. FIELD FAIL / O2
OPEN and review-006 pending are unchanged.

Prompt for the Windows agent (the user forwards it):

```text
S11 step-9 묶음 요청 — SPL#4를 2fps FULL, 2fps NONE, 6fps FULL로 한 번씩 다시 실행하고, 비교 3개를 돌린다.
튜닝·Recipe/ROI/margin/임계값/세션 변경·추가 재실행은 하지 마. 사람 확인은 없다.
값은 도구 stdout을 원문 그대로 돌려줘. 요약·재구성·개수 세기·판정·수정 제안 없이 멈춰. 새 bundle은 Windows에 보존한다.
출력 폴더 경로는 영문·숫자·밑줄만 쓴다(OpenCV 이미지 저장은 한글 경로에서 실패할 수 있다).
실행 중에는 다른 무거운 작업을 하지 않는다(시간 측정이 들어 있다).
크기 예상: T-1 bundle 약 0.6 GB, C-1 약 1.8 GB. C-1은 T-1보다 약 3배 오래 걸린다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_cadence_field.py
        c3c1dbeaf0efa18f14f386af562323069ef4ed9b8ccb4b9108a7e17bb5626958
      - tests/diagnostics/s11_layer_bottom_topology_2_field.py
        0830bef44a0a7d00e1ff5f700a9ad06de2913839117379bfd21d55f3aa8cf433
      - src/oil_tracker/adapters/storage/jsonl_debug_trace_writer.py
        76a65eaf6cab13c054c21d1792510675ea9e6f12861e08e2c9c78984e9d1fae2
      - src/oil_tracker/adapters/vision/oil_interface_tracklets.py
        b35e70a3003b30c4f83a9e52699f8ac430094b4fd79d76d8b6acaf9f6aa4caab
      - src/oil_tracker/adapters/vision/oil_observation_resolver.py
        65f866563c467ba2a210509aaa37c83deb4da264072de3de4c5642d90a8e3196
      - src/oil_tracker/adapters/vision/oil_top_exit_full.py
        10dd3605a9ab0afb4ce4c0ae5a69477b1157318b0246ae972716d4202bb6f77d
 0-2. 기록: python -c "import sys, cv2; print(sys.version); print(cv2.__version__)"
      그리고 PowerShell: Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
 0-3. step-7의 SPL4_B_ref bundle 폴더를 그대로 쓴다(복사·수정 금지).
      session.json, recipe_snapshot.oilrecipe, tracking_data.csv, debug\debug_trace.jsonl, debug\debug_index.json이 있는지 확인한다.
 0-4. 새 출력 폴더 <out>를 만든다(예: C:\step9_out).

R. 실행 3개 — 소스 폴더에서, 이 순서대로 하나씩:
 R-1. T-1: python -m tests.diagnostics.s11_cadence_field run --reference-bundle <SPL4_B_ref 폴더> --out <out>\t1 --run-name SPL4_T1_2fps_full
 R-2. T-2: python -m tests.diagnostics.s11_cadence_field run --reference-bundle <SPL4_B_ref 폴더> --out <out>\t2 --debug none --run-name SPL4_T2_2fps_none
 R-3. C-1: python -m tests.diagnostics.s11_cadence_field run --reference-bundle <SPL4_B_ref 폴더> --out <out>\c1 --sampling-fps 6 --run-name SPL4_C1_6fps_full
      각 실행은 "bundle <경로>" 줄로 새 bundle 위치를 알려 준다.
      "STOP: video not found"가 나오면 그 실행만 --video <SPL#4 영상 경로>를 붙여 한 번 다시 실행한다.
      다른 STOP이나 오류는 출력을 그대로 적고 멈춘다. 다시 시도하지 않는다.

C. 비교 3개 — 소스 폴더에서:
 C-a. python -m tests.diagnostics.s11_cadence_field identity --reference <SPL4_B_ref 폴더> --trial <R-1 bundle> --out <out>\id_t1
 C-b. python -m tests.diagnostics.s11_cadence_field identity --reference <SPL4_B_ref 폴더> --trial <R-2 bundle> --out <out>\id_t2
 C-c. python -m tests.diagnostics.s11_cadence_field cadence --reference <SPL4_B_ref 폴더> --trial <R-3 bundle> --out <out>\cad

1. 돌려줄 것 — 모두 stdout 원문 그대로. 값은 고치거나 반올림하지 않는다.
 - 머리줄: 소스 폴더, 0-1의 SHA-256 값 전부, 0-2의 출력, SPL4_B_ref 경로.
 - R-1, R-2, R-3 전체: "run …", "bundle …", "window …", "timing …" 줄과 "-- stages" 목록 전부.
 - C-a, C-b 전체: 첫 세 줄, changed 목록(있으면), 마지막 "json … sha256" 줄.
 - C-c 전체: reference/trial 두 블록(각 run_id 줄과 C1–C5 줄, break 줄), "-- trial BASE" 목록 전부,
   "-- shared 2 fps grid" 목록 전부, 마지막 "json … sha256" 줄.

2. 결론·판정 없이 멈춘다. top-exit, fill-owner gate, fast-rise association은 제품 기본 OFF로 남고,
   FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Step-8 combined request

**COMPLETE 2026-10-26 ([receipt](../60-evidence/s11/2026-10-26-step8-windows-receipt.md)).** Windows is available
(user, 2026-10-26). The user approved sending these two items together, with
the SPL#4 run decided on the Mac after its readout ("그렇게 진행하자"). This
is a readout and comparison request, not field qualification.

**What it answers:**
- **F, the SPL#4 fast-rise readout:** the frozen first Windows step of the
  [fast-rise association checks](../30-validation/s11-physical-interface-evidence-repair-validation.md#fast-rise-association-checks--2026-10-23).
  It is read-only on the step-7 `SPL4_B_ref` bundle at 20.5–25.5 s.
  - The question: does a witnessed upward triplet beyond the 32 px cap, in a
    constant-velocity line, exist?
  - The tool: `tests/diagnostics/s11_fast_rise_readout.py`. Its reader
    equals the live builder locally.
- **L, LBT-2 S2:** the
  [frozen S2 protocol](../50-diagnostics/s11/2026-10-22-layer-bottom-topology-2.md#windows-s2-protocol-frozen-2026-10-26).
  - The `SPL1_B_ref` session is rerun twice from the same source: a reference
    arm and the LBT-2 arm.
  - Two comparisons follow: the rerun against `SPL1_B_ref` (identity), and
    LBT-2 against the rerun.
  - The tool: `tests/diagnostics/s11_layer_bottom_topology_2_field.py`.

**Not in this request:**
- the SPL#4 fast-rise run (step 2 of the checks). The Mac proposes it only if
  F finds a qualifying triplet on BASE;
- a human review;
- SPL#1 after 780 s.

**Pre-registered (judged on the Mac, not on Windows):**
- **F** (the [readout rule](../60-evidence/s11/2026-10-23-fast-rise-local.md#windows-readout-tool--2026-10-26)):
  - one or more qualifying triplets on SPL#4 BASE: propose the SPL#4 run;
  - none: no run, and the user chooses the next step.
  - Accum is reported by its counts only.
- **L:** readings S1–S5 and the outcomes of the S2 protocol, scored on
  review-012 table V (C1 29.16 px; ordinary C0 A8 B4).
- **Stop:** a SHA-256 mismatch, a missing bundle file, a `STOP` line or a run
  error. The agent reports it and does not retry. The one exception is a
  moved video, which gets a single rerun with `--video`.

**Source:** latest `main`. The request lists six SHA-256 values. No Recipe,
ROI, margin, threshold or session change. Top-exit stays default OFF in the
product, as do the gate and the fast-rise association; both S2 arms carry
IFO v2 + top-exit v3, as `SPL1_B_ref` did. FIELD FAIL / O2 OPEN and
review-006 pending are unchanged.

Prompt for the Windows agent (the user forwards it):

```text
S11 step-8 묶음 요청 — (F) SPL#4 fast-rise 읽기 전용 추출 + (L) LBT-2 S2 비교 실행 2개와 비교 2개.
튜닝·Recipe/ROI/margin/임계값/세션 변경·추가 재실행은 하지 마. 사람 확인은 없다.
값은 도구 stdout을 원문 그대로 돌려줘. 요약·재구성·개수 세기·판정·수정 제안 없이 멈춰. 새 bundle은 Windows에 보존한다.
출력 폴더 경로는 영문·숫자·밑줄만 쓴다(OpenCV 이미지 저장은 한글 경로에서 실패할 수 있다).
L의 두 실행은 step-7의 SPL#1 실행과 크기가 비슷하다(FULL debug, bundle 하나에 약 2 GB).

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_fast_rise_readout.py
        96a5cab616d3db67d626f719ca48f0e7c2bbeb0a33bceffde88f8deb797cdbbc
      - tests/diagnostics/s11_layer_bottom_topology_2_field.py
        0830bef44a0a7d00e1ff5f700a9ad06de2913839117379bfd21d55f3aa8cf433
      - tests/diagnostics/s11_layer_bottom_topology_2.py
        d1eff07242b1059d2b8b5899d46858d817c15bb70cd8bb12a719e5675dc3f5ab
      - tests/diagnostics/s11_layer_bottom_topology.py
        2fa3722a7d6e1debe117e3fb82726b83fc840e69c21348846e8d9b0765359a5d
      - src/oil_tracker/adapters/vision/oil_interface_tracklets.py
        b35e70a3003b30c4f83a9e52699f8ac430094b4fd79d76d8b6acaf9f6aa4caab
      - src/oil_tracker/adapters/vision/oil_observation_resolver.py
        65f866563c467ba2a210509aaa37c83deb4da264072de3de4c5642d90a8e3196
 0-2. step-7의 SPL4_B_ref, SPL1_B_ref bundle 폴더를 그대로 쓴다(복사·수정 금지).
      각 bundle에 session.json, recipe_snapshot.oilrecipe, tracking_data.csv, debug\debug_trace.jsonl이 있는지 확인한다.
 0-3. 새 출력 폴더 <out>를 만든다.

F. SPL#4 fast-rise — 읽기 전용, 검출기 실행 없음. 소스 폴더에서:
 F-1. python -m tests.diagnostics.s11_fast_rise_readout --work <out>\fr_base --bundle <SPL4_B_ref 폴더> --glass-name BASE --start 20.5 --end 25.5
 F-2. python -m tests.diagnostics.s11_fast_rise_readout --work <out>\fr_accum --bundle <SPL4_B_ref 폴더> --glass-name Accum --start 20.5 --end 25.5 --summary-only
 Glass 이름이 BASE/Accum이 아니면 Recipe의 이름을 그대로 쓴다. "STOP"이나 오류가 나오면 출력을 그대로 적고 L로 넘어간다.

L. LBT-2 S2 — SPL1_B_ref의 세션을 그대로 다시 실행한다(480–780초, 2fps, FULL debug, 초기 확정값 그대로). 소스 폴더에서:
 L-1. 기준: python -m tests.diagnostics.s11_layer_bottom_topology_2_field run --reference-bundle <SPL1_B_ref 폴더> --out <out>\s2 --arm reference --run-name SPL1_S2_ref
 L-2. LBT-2: python -m tests.diagnostics.s11_layer_bottom_topology_2_field run --reference-bundle <SPL1_B_ref 폴더> --out <out>\s2 --arm lbt2 --run-name SPL1_S2_lbt2
      각 실행은 "bundle <경로>" 줄로 새 bundle 위치를 알려 준다.
      "STOP: video not found"가 나오면 그 실행만 --video <SPL#1 영상 경로>를 붙여 한 번 다시 실행한다.
      다른 STOP이나 오류는 출력을 그대로 적고 멈춘다. 다시 시도하지 않는다.
 L-3. 비교 2개. truth는 소스 폴더의 docs\30-validation\windows_sample1_heating_coldstart.reviewed-truth.json이다.
      신원: python -m tests.diagnostics.s11_layer_bottom_topology_2_field compare --reference <SPL1_B_ref 폴더> --trial <L-1 bundle> --truth <truth> --out <out>\cmp_identity
      S2:   python -m tests.diagnostics.s11_layer_bottom_topology_2_field compare --reference <L-1 bundle> --trial <L-2 bundle> --truth <truth> --out <out>\cmp_s2

1. 돌려줄 것 — 모두 stdout 원문 그대로. 값은 고치거나 반올림하지 않는다.
 - 머리줄: 소스 폴더, 0-1의 SHA-256 6개, 두 step-7 bundle 경로.
 - F-1 전체: 첫 세 줄, "-- rows" 목록 전부, "-- constant-velocity triplets" 목록 전부, 마지막 "json … sha256" 줄.
 - F-2 전체(네 줄).
 - L-1, L-2 전체: "arm …", "bundle …", "window …" 줄. L-2는 "operations …" 줄과 "-- F", "-- units" 목록 전부도.
 - L-3 두 비교 전체: run_id·version 두 줄, "changed rows" 줄, "-- segments" 표, "-- held-out" 목록, "-- watch" 목록,
   "-- changed" 목록, 마지막 "json … sha256" 줄. changed 목록이 120줄을 넘으면 앞 120줄과 전체 수만 적는다.

2. 결론·판정 없이 멈춘다. top-exit, fill-owner gate, fast-rise association은 제품 기본 OFF로 남고,
   FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Step-7 follow-up request

**COMPLETE 2026-10-23** ([receipt](../60-evidence/s11/2026-10-23-step7-windows-receipt.md#follow-up-reply--2026-10-23)). Read-only. The first step-7 reply
([receipt](../60-evidence/s11/2026-10-23-step7-windows-receipt.md)) came back
mostly as summaries and left out these items:
- the identity (table I);
- the gate's SPL#4 comparison, the only pre-registered prediction;
- the report checks;
- tables A and K;
- the FLB-2 lines that settle R3's label.

This request reads the saved bundles and logs only. It runs no detector and
writes nothing.

- **Judged on the Mac** against the step-7 pre-registered readings.
- **Stop:** a missing bundle or log. The agent says which one and goes on.

Prompt for the Windows agent (the user forwards it):

```text
S11 step-7 보충 요청 — 이미 만든 bundle·로그·review 자료를 읽기만 한다. 검출기 실행·재실행·새 분석·파일 수정은 없다.
지난 답은 요약이 많아 판정에 필요한 항목이 빠졌다. 아래 항목만 파일 값 그대로 돌려줘. 요약·재구성·개수 추정·판정은 하지 마.
step-7에 쓴 소스 폴더, 네 bundle(SPL4_B_ref/SPL4_B_gate/SPL1_B_ref/SPL1_B_gate), FLB-2 로그 4개를 그대로 쓴다.
정의(행, S/P/K/C, 다른 행)는 docs/40-operations/s11-current-windows-field-qualification.md의
"## Step-7 combined request" 프롬프트와 같다. 찾는 파일이 없으면 없다고 적고 다음 항목으로 넘어간다.

1. 머리줄
   - 네 bundle의 session.json run_id(전체)와 run_name, Glass별 tracking_data.csv 행 수.
   - step-7 소스 폴더에서 계산한 그 프롬프트 0-1의 SHA-256 6개, 소스 ZIP의 SHA-256(64자인지 확인).
2. 표 I — SPL4_B_ref ↔ 지난 SPL4_A_top_exit_v3 bundle, SPL1_B_ref ↔ ⑩ bundle.
   비교한 두 bundle의 run_id, Glass별 다른 행 수와 목록(최대 10개).
3. 표 G — SPL4_B_ref ↔ SPL4_B_gate, BASE와 Accum 각각: 그 프롬프트 3의 a~d 그대로.
   c의 각 행은 정해진 8칸을 모두 쓴다.
4. 리포트 — SPL1_B_ref: 그 프롬프트 4와 5 그대로
   (Glass별 retrospective status·interval·reason·provenance, 카드 판정과 판정 안내 원문,
    review_index.json의 result_status와 effective_state_aware_coverage_ratio, 범례 질문의 답).
5. 표 A와 표 K — 그 프롬프트 6과 11 그대로.
6. FLB-2 로그(%TEMP%\flb2_spl1_accum.log, flb2_spl1_base.log, flb2_spl4_accum.log, flb2_spl4_base.log)에서 복사:
   - 실행마다 첫 두 줄("run_id …"와 "frames …") 원문.
   - spl1_accum의 "-- all rows 668.0-682.0 s --" 아래 줄 전부를 7칸(time | frame | ordinary | FLB-2 | state | reason | bottom) 그대로.
   - spl4_base의 "-- changed rows --" 아래 38줄 전부를 7칸 그대로.
   로그에 없으면 해당 flb2-bundle-*.json의 같은 값을 쓰고 출처를 적는다.

7. 결론·판정 없이 멈춘다. top-exit와 fill-owner gate는 기본 OFF로 남고,
   FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## FLB-2 held-out request

**COMPLETE 2026-10-23** ([result](../50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow-2.md#held-out-result--2026-10-23)):
closed with no design (held-out NOT TESTED; R2 and R4 fail). Read-only: it runs the frozen
[FLB-2](../50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow-2.md) desk
emulation on the step-7 reference bundles (`SPL1_B_ref`, `SPL4_B_ref`). It does
not run the detector, write into a bundle or change any setting.

- **Judged on the Mac** with the frozen scoring and readings R1–R4, together
  with step-7 review-012 table V.
- **Stop:** a SHA-256 mismatch, a missing FULL debug trace (the tool prints
  `STOP`) or an error. The agent reports and does not retry.

Prompt for the Windows agent (the user forwards it):

```text
S11 FLB-2 요청 — step-7에서 만든 기준 bundle을 읽기만 하는 모의 실행. 검출기 실행·새 분석·재실행은 없다.
튜닝·Recipe/세션 변경·bundle 수정은 하지 마. 값만 원문 그대로 돌려주고 판정·수정 제안 없이 멈춰.
출력 폴더 경로는 영문·숫자·밑줄만 쓴다.

0. 준비
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - tests/diagnostics/s11_foam_layer_bottom_follow.py
        ca6f91d846674815973fb6d09571caab2df8e20ea73d7e464c3f8ba3234a0749
      - src/oil_tracker/adapters/vision/foam_material_identity.py
        e65fd5f574e1910b86815e663ac59f1edaad7c706d17fd3073fb24e6475570d9
 0-2. step-7의 SPL1_B_ref, SPL4_B_ref bundle 폴더를 그대로 쓴다(복사·수정 금지).
      각 bundle에 debug\debug_trace.jsonl과 recipe_snapshot.oilrecipe가 있는지 확인한다.
 0-3. 새 출력 폴더 <out>를 만들고 그 안에 spl1_accum, spl1_base, spl4_accum, spl4_base 폴더를 만든다.

1. 실행 4개 — 소스 폴더에서. Glass 이름이 Accum/BASE가 아니면 Recipe의 이름을 그대로 쓴다.
   python -m tests.diagnostics.s11_foam_layer_bottom_follow --work <out>\spl1_accum --bundle <SPL1_B_ref 폴더> --glass-name Accum --start 668 --end 682
   python -m tests.diagnostics.s11_foam_layer_bottom_follow --work <out>\spl1_base --bundle <SPL1_B_ref 폴더> --glass-name BASE --start 668 --end 682
   python -m tests.diagnostics.s11_foam_layer_bottom_follow --work <out>\spl4_accum --bundle <SPL4_B_ref 폴더> --glass-name Accum --start 25 --end 36
   python -m tests.diagnostics.s11_foam_layer_bottom_follow --work <out>\spl4_base --bundle <SPL4_B_ref 폴더> --glass-name BASE --start 25 --end 36
   "STOP"이나 오류가 나오면 그 실행의 출력을 그대로 적고 다음 실행으로 넘어간다. 다시 시도하지 않는다.

2. 돌려줄 것
 - 머리줄: 소스 폴더, 0-1의 SHA-256 두 개, 두 bundle 경로.
 - 실행마다 stdout 전체를 원문 그대로: 첫 줄(run_id … C1), 둘째 줄(frames … changed),
   "-- changed rows --" 목록, "-- all rows … --" 목록, 마지막 "json … sha256" 줄.
   changed rows가 60행을 넘으면 앞 60행과 전체 수만 적는다.
 - 값은 고치거나 반올림하지 않는다. 생성된 json은 Windows에 보존한다.

3. 결론·판정 없이 멈춘다. top-exit와 fill-owner gate는 기본 OFF로 남고,
   FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Step-7 combined request

**COMPLETE 2026-10-23** ([receipt](../60-evidence/s11/2026-10-23-step7-windows-receipt.md)), with the
[follow-up request](#step-7-follow-up-request) for the items the first reply left out. Windows is available again
(user, 2026-10-23). This is step 7 of the Mac-only order in the
[Work Plan](../00-project/work-plan.md): one request that collects the Windows
items queued since 2026-10-22. It is a comparison and readout request, not
field qualification.

**What it answers:**
- **G, the gate on real field video:** the
  [contested fill-owner gate](../20-architecture/s11-physical-interface-evidence-repair-design.md#october-22-contested-fill-owner-gate)
  (`--oil-fill-owner-contest`, default OFF) against its reference, on SPL#4
  0–90 s and SPL#1 480–780 s. Four runs.
- **R, report checks:** per-sample band cells, E2 and the first-catch guard
  (L2) on the SPL#1 reference report.
- **D, read-only readouts** from the SPL#1 reference bundle: the Accum geometry
  and 640–672 s rows (LCR-1), fill ownership at Accum 653–682 s (DSR-1 option 1),
  the contested hypotheses at 680–700 s (option 2), the drain release
  evaluations at 700–780 s (option 3), and SPL#4's `temporal_max_jump_px`
  (the fast-fill admission inference).
- **V, review-012:** the user marks the strict Oil boundary on Accum
  672.0–677.5 s (the `WS1-ACCUM-FOAM-LAYERED` segment) on a raw zoom made with
  `tests/diagnostics/s11_review_zoom.py`, the generalised review-014 generator.
  Its `read-marks` mode turns the marks into source coordinates on Windows, so
  only text comes back.

**Not in this request:** LBT-2's S2 (a separate go after review-012); a human
check of the 22 Accum drain rows and a SPL#4 fast-rise frame review (after the
readouts); SPL#1 after 780 s (the user may supply scenes).

**Pre-registered (judged on the Mac, not on Windows):**
- **Identity:** each reference equals its earlier bundle in every tracking row
  (SPL#4: `SPL4_A_top_exit_v3`; SPL#1: ⑩). Since those runs, `src` changed only
  in report code, the default-OFF gate and the reconstruction guard.
- **G, SPL#4 BASE:** the 14 wrong-target numeric rows at 27.5–34.0 s
  (Y704–739) become rows without numeric Oil, each with phase reason
  `FILL_OWNER_CONTESTED`. Any other differing row is listed and read
  separately.
- **G, SPL#4 Accum and SPL#1:** no prediction; every differing row is listed.
  The Mac reads them against the reviewed truth: a removed numeric row inside a
  visible-interface segment is a loss; one inside a FULL, EMPTY or wrong-target
  span is a removed false output.
- **R:** BASE retrospective ACCEPTED, 479.98–548.01 s, provenance
  `initial_state_retrospective_v3`; Accum UNRESOLVED; no legend entry without
  a visible band.
- **D, V:** no criterion; they inform the user's next choices.
- **Stop:** a hash or identity mismatch, a wrong resolver version, a run error
  or a rescaled marked image. The agent stops and reports.

**Source:** latest `main`; the request lists six SHA-256 values. No Recipe,
ROI, margin, threshold or session change; top-exit and the gate stay default
OFF; FIELD FAIL / O2 OPEN and review-006 pending are unchanged.

Prompt for the Windows agent (the user forwards it):

```text
S11 step-7 묶음 요청 — (G) fill-owner gate 비교 실행 4개 + (R) 리포트 확인 + (D) 읽기 전용 추출 + (V) review-012 사람 표시.
튜닝·Recipe/ROI/margin/임계값 변경·추가 재실행은 하지 마. 사람 확인은 V의 표시 한 번뿐이고 사용자가 한다.
값만 원문 그대로 돌려주고 판정·수정 제안 없이 멈춰. 새 bundle은 Windows에 보존한다.
출력 폴더 경로는 영문·숫자·밑줄만 쓴다(OpenCV 이미지 저장은 한글 경로에서 실패할 수 있다).
인접 행 = 다음 2fps 표본(간격 0.75초 미만). "0.5초 간격"으로 묶지 마.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - src/oil_tracker/adapters/vision/oil_phase_lifecycle.py
        69ea87d223139f882bb1426923112876c15691494e169361fa6ba2a7d369e2bf
      - src/oil_tracker/adapters/vision/opencv_phase_detector.py
        ef774ff0824caa495eea7dc9cfecd5453b0cd887b1a5e20c48f078c6fa7e2eaa
      - src/oil_tracker/adapters/vision/oil_top_exit_full.py
        10dd3605a9ab0afb4ce4c0ae5a69477b1157318b0246ae972716d4202bb6f77d
      - src/oil_tracker/application/services/initial_state_reconstruction.py
        eceac0e8b594f3d9aa761b0ad4bbf9ca6b0e75a71b50a8a4542ace10420fd82f
      - src/oil_tracker/adapters/reporting/graph_renderer.py
        dd85223ed6eba3ac8446980ddd6a5019de8d707bd016b0465ea32bf978ed17cb
      - tests/diagnostics/s11_review_zoom.py
        34378c1dbbe229ba3b6961d870adc8bf984fb4763627bd4783ba6e41610a7363
 0-2. 영상·Recipe는 지난번과 같다. Recipe 파일은 수정하지 않는다.
      - SPL#4: SPL#4_Cooling_onoff_#2.mp4(53165455 bytes), sample4_test_artifact_R22.oilrecipe
        — 지난 SPL4_A 실행과 같은 파일.
      - SPL#1: ⑩(…_top_exit_v3_20261021_170933)과 같은 영상·Recipe(ROI/margin/exclusion/Artifact·영점/스케일).
        ⑩ bundle의 session/recipe_snapshot과 SHA-256이 같은지 확인한다.

G. 비교 실행 4개 (같은 소스, 차이는 fill_owner_contest 하나)
   headless 방식은 지난번과 같다(AnalysisPipeline + OutputBundleStore + JsonlDebugTraceWriterFactory).
   cost-first/RGB/Local XY는 OFF.
 G-1. SPL#4 — 지난 SPL4_A와 같은 세션: 0–90초, 2fps, FULL debug, compressor_start 10.0초,
      두 Glass initial_state EMPTY_NO_INTERFACE(메모리의 Recipe와 세션 initial_state_confirmations, Recipe 파일은 그대로).
      기준: OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True), run_name "SPL4_B_ref"
      후보: OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True, fill_owner_contest=True), run_name "SPL4_B_gate"
 G-2. SPL#1 — ⑩과 같은 세션: 480–780초, 2fps, FULL debug, compressor_start 485초,
      BASE FULL / Accum EMPTY 초기 확정값.
      기준: OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True), run_name "SPL1_B_ref"
      후보: 기준 + fill_owner_contest=True, run_name "SPL1_B_gate"
 G-3. trace의 sequence_resolver_version: 기준 둘은 "+initial-full-observation-v2"와 "+top-exit-full-v3"가 있고
      "+fill-owner-contest-v1"이 없어야 한다. 후보 둘은 셋 다 있어야 한다. 아니면 멈추고 값만 알려줘.

표기:
 - 행 = tracking_data.csv 한 줄. 시간은 timestamp_sec. 목록은 frame/time으로 쓴다.
 - S = debug record의 sequence.state, P = S.sequence_material_phase_diagnostics,
   K = P.fill_owner_contest (후보에만 있음), C = sequence.candidates[]. 키가 없으면 MISSING, null이면 null.
 - 다른 행 = 같은 (glass_id, frame_index)에서 fill_state, raw_oil_air_level_y, raw_foam_front_y,
   oil_is_valid, foam_is_valid, flags 중 하나라도 다른 행.

1. 머리줄: 네 run_id·run_name, 소스 폴더, 0-1의 SHA-256 6개, 네 sequence_resolver_version, 네 bundle 경로,
   영상 SHA-256·size·fps·frame_count, Recipe SHA-256, Glass별 행 수(SPL#4 기대 181, SPL#1 기대 601),
   두 쌍의 (glass_id, frame_index) 대응 결과(중복·누락·timestamp 불일치 수).

2. 표 I — 신원: SPL4_B_ref ↔ 지난 SPL4_A_top_exit_v3, SPL1_B_ref ↔ ⑩. Glass별 다른 행 수와 목록(최대 10개).

3. 표 G — 영상별·Glass별(SPL#4 BASE/Accum, SPL#1 BASE/Accum):
 a. 기준 ↔ 후보 다른 행 수
 b. 후보에서 K.gated가 true인 행 수, 그 첫 행과 마지막 행의 frame/time
 c. 다른 행 목록(Glass별 최대 40개, 넘으면 개수만), 각 한 줄:
    frame | time | 기준 fill_state / raw_oil_air_level_y | 후보 fill_state / raw_oil_air_level_y |
    후보 S.sequence_material_phase_reason | K.gated | K.contested_tracklet_ids | 후보 P.allowed_tracklet_ids
 d. 후보 S.sequence_material_phase_reason별 행 수(FILL_OWNER_AMBIGUOUS, FILL_OWNER_CONTESTED만)

R. 리포트 확인 — SPL1_B_ref bundle
 4. Glass별: retrospective status, interval, reason, provenance(값 그대로),
    리포트 카드의 판정과 "판정 안내" 문장 원문, review_index.json의 result_status와
    effective_state_aware_coverage_ratio.
 5. graphs 폴더: combined_levels.png 아래 범례 항목 목록, BASE·Accum 상세 그래프의 범례 항목 목록,
    범례에 있는데 그래프에 보이는 띠가 없는 항목(없으면 "없음"), 상태 줄과 상세 그래프 띠의 위치·무늬가 같은지(예/아니오).

D. 읽기 전용 추출 — SPL1_B_ref bundle (SPL#4는 D-5만). 파일을 수정하거나 새 결과 파일을 만들지 않는다.
 6. 표 A — Accum 기하: Recipe 타원 cx, cy, rx, ry, margin_ratio, P.policy.maximum_jump_px(첫 record),
    BASE도 같은 값을 한 줄.
 7. 표 B — Accum 640.0~672.0초 행 전부, 각 한 줄:
    time | frame | fill_state | raw_oil_air_level_y | raw_foam_front_y | flags
 8. 표 F — Accum 653.0~682.0초 행 전부, 각 한 줄:
    time | frame | fill_state | raw_oil_air_level_y | S.sequence_material_phase / S.sequence_material_phase_reason |
    P.dynamic_fill_owner_ids | P.allowed_tracklet_ids | P.established_fill_owner : P.established_fill_last_y |
    선택 후보(C 중 selected가 true인 항목의 canonical_y:tracklet_id, 없으면 "없음")
 9. 표 H — Accum 680.0~700.0초 행 전부. 각 행에서 C 중 kind = oil_air이고 tracklet_id가 비어 있지 않은 항목을
    canonical_y 오름차순 최대 4개, 각 한 줄:
    time | frame | canonical_y | tracklet_id | tracklet_lifecycle | tracklet_admitted | tracklet_incompatible |
    tracklet_failure_reason | selected | reject_stage
    (트랙 종료 이유 termination_reason은 trace에 없다. 찾지 말고 "trace에 없음"으로 둔다.)
10. 표 J — Accum 700.0~780.0초:
 a. raw_oil_air_level_y가 비어 있지 않은 행 수와 목록(time | frame | raw_oil_air_level_y)
 b. P.release_evaluated가 true인 행, 각 한 줄:
    time | frame | S.sequence_material_phase | P.release_stage | P.release_selected_tracklet_id | P.release_ambiguous |
    P.release_evaluations의 각 항목 tracklet_id:row_y:first_failed_predicate (최대 4개)
    50행이 넘으면 앞 50행과 전체 수만.
11. 표 K — SPL4_B_ref BASE: P.policy.maximum_jump_px(첫 record)와 Recipe의 temporal_max_jump_px 값.

V. review-012 — SPL#1 Accum 672.0~677.5초, 사람 표시
12. SPL1_B_ref의 tracking_data.csv에서 Accum의 timestamp_sec가 672.0 이상 677.75 미만인 행의 frame_index를 순서대로 모은다
    (기대 12개 안팎). 소스 폴더에서:
      python -m tests.diagnostics.s11_review_zoom prepare --video <SPL#1 영상> --recipe <⑩ Recipe> --glass-name Accum
        --frames <쉼표로 이은 frame_index> --review-id review-012 --out <새 출력 폴더>\review012
    (Glass 이름이 Accum이 아니면 Recipe의 이름을 그대로 쓴다.) review-zoom.png와 review-zoom.json이 생긴다.
13. review-zoom.png를 사용자에게 열어 주고 이렇게 묻는다(문장 그대로):
    "각 칸에서 엄격 기준의 Oil 경계(촘촘한 Foam이 끝나는 곳, 그 아래 기포 섞인 구간부터 Oil)를 빨간색으로 표시해 주세요.
     촘촘한 경계가 무너져 특정하기 어려우면 대략 표시하고 '대략'이라고, 촘촘한 경계가 안 보이면 Foam 영역의 최하단을 표시하고
     '최하단'이라고, Oil 경계가 안 보이면 '안 보임'이라고 칸별로 알려 주세요. 이미지 크기는 바꾸지 말고 같은 크기로 저장해 주세요."
    사용자가 저장한 파일로:
      python -m tests.diagnostics.s11_review_zoom read-marks --manifest <...>\review012\review-zoom.json --marked <표시한 파일>
    "STOP"이 나오면(크기가 다름) 사용자에게 원래 크기로 다시 저장해 달라고 하고 한 번만 다시 읽는다.
14. 표 V — 칸별 한 줄: frame | decoded_time_sec | 표시 수 | y_range | marks(x:y, 최대 8개) | 사용자 말(대략/최하단/안 보임 등, 원문)
    머리줄에 review-zoom.json의 zoom_source_xyxy, scale, image.sha256, read-marks의 marked_image.sha256과
    changed_not_red_px를 적는다. 이미지 원본은 Windows에 보존한다.

15. 머리줄과 표 I/G, 4~5의 답, 표 A/B/F/H/J/K/V를 원문 그대로 돌려준다. 값은 고치거나 반올림하지 않는다.
    결론·판정·수정 제안 없이 멈춘다. top-exit와 fill-owner gate는 기본 OFF로 남고,
    FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## SPL#4 opposition follow-up

**COMPLETE 2026-10-22.** The
[receipt](../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-opposition-follow-up-receipt--2026-10-22)
names `OIL-PHASE-FILL` `FILL_OWNER_AMBIGUOUS` (two low owners) as the source and
completes the ⑩ Accum census. Do not repeat. The request below is kept as the
record.

**Requested 2026-10-22 — read-only; the user forwarded it and relayed the
result.** The user chose this after the
[SPL#4 receipt](../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-receipt--2026-10-22),
as the diagnosis its decision rule requires. Nothing is run; two saved bundles
are read.

**What it answers:**
- **Which source opposed BASE 22.5–27.0 s:** the fill lifecycle's chain
  ambiguity or a candidate identity contradiction. Tables D and E give the
  phase reason, the ambiguity flag, the stage at which each row became
  UNKNOWN, and the Oil candidates with their tracklets, directions and
  contradictions.
- **The three failed disappearance evaluations** (table F).
- **How much wrong-target numeric Oil** the production default publishes in
  the reviewed FULL interval, 25–63 s (table G; both arms are identical).
- **The full ⑩ Accum census:** all 64 rows, ungrouped. The agent grouped
  them wrongly before; they will be regrouped here at adjacent 2 fps samples
  (table H).

**Readings fixed before the extraction:**
- **Fill ambiguity:** `FILL_CHAIN_AMBIGUOUS` with the ambiguity flag 1 on the
  opposed frames means `OIL-PHASE-FILL` handoff ambiguity, where several
  upward tracklets compete for the chain.
- **Identity contradiction:** a flag of 0 with a non-`none` identity
  contradiction on a current candidate points to `OIL-AUTHORITY` /
  `OIL-TRACKLET`.
- **Anything else,** or a mix, is recorded as it is.
- **Not decided here:** whether a candidate is the real level needs a human
  review; the tables give positions only.
- **Use:** no criterion, tuning or detector change follows. The answer informs
  the user's choice of a later FULL route for fast fills.

Prompt for the Windows agent (the user forwards it):

```text
S11 SPL#4 후속 진단 — 저장된 bundle 2개 읽기 전용 추출이야.
재실행·새 bundle·튜닝·비교 실행·사람 검토는 하지 마. 파일은 수정·이동하지 말고 결과 파일도 만들지 마.
값만 원문 그대로 돌려주고 원인 판정·수정 제안 없이 멈춰.

대상:
 (가) SPL#4 후보 bundle: ...\SPL4_top_exit_evidence\oil_level_analysis_SPL4_A_top_exit_v3_20261022_142048
 (나) ⑩ bundle: …_top_exit_v3_20261021_170933 (지난 C 진단과 같은 bundle)
각 bundle에서 debug/debug_index.json, debug/debug_trace.jsonl, tracking_data.csv만 읽는다.
index에서 glass_name과 timestamp_sec로 record를 찾아 byte_offset으로 읽는다.
표기: S = sequence.state, W = S.sequence_decision_witness, C = sequence.candidates[],
T = S.sequence_material_phase_diagnostics.top_exit_full. 키가 없으면 MISSING, 값이 null이면 null.
후보 위치는 C의 canonical_y를 쓴다.

1. 표 D — (가) BASE, 21.0~28.0초 15개 record(0.5초 간격) 각 한 줄:
   frame | time | fill_state | raw_oil_air_level_y | raw_foam_front_y |
   S.sequence_material_phase / S.sequence_material_phase_reason | S.sequence_material_phase_ambiguous |
   S.sequence_material_phase_owner_chain | W.phase.allowed_tracklet_ids |
   S.sequence_stage_best_path_kind:y / sequence_stage_continuation_bound_kind:y /
   sequence_stage_spike_suppressed_kind:y / sequence_stage_completed_fill_kind:y |
   W.selection.resolved_kind | W.selection.selected_candidate(source:y:tracklet_id) |
   C 중 identity_contradiction이 none이 아닌 항목 수와 그 source:canonical_y:값

2. 표 E — (가) BASE, 22.0~24.5초 6개 record에서 C 중 kind = oil_air 이고 tracklet_id가 비어 있지 않은 항목,
   canonical_y 오름차순 최대 8개, 각 한 줄:
   frame | source | canonical_y | tracklet_id | row_hypothesis_id | tracklet_lifecycle | tracklet_admitted |
   tracklet_incompatible | tracklet_failure_reason | tracklet_direction | tracklet_directional_agreement |
   phase_identity | identity_contradiction | authority | selected | reject_stage

3. 표 F — (가) BASE 0~90초에서 T.reason이 TOP_EXIT_NOT_PROVEN인 행 전부(지난번 3개), 각 한 줄:
   frame | time | T.predicates 중 false인 키 | T.witness(frame_index:y:selected 목록) | T.anchor_source

4. 표 G — (가) BASE 25.0~63.0초에서 raw_oil_air_level_y가 비어 있지 않은 행 수와 목록:
   frame | time | raw_oil_air_level_y | fill_state | T.reason

5. 표 H — (나) Accum: 지난 C 진단 c의 64개 행 전부를 시간 순서대로 각 한 줄(묶음은 만들지 않는다):
   time | frame | 그 행의 INCOMPATIBLE_BRANCH 후보 중 최소 canonical_y | T.reason | T.witness 수

6. 머리줄(두 bundle의 run_id, Glass별 record 수)과 표 D/E/F/G/H를 원문 그대로 돌려준다.
   값은 고치거나 반올림하지 않는다. 결론은 "22.5~27.0초 record의 sequence_material_phase_reason 값" 같은
   관찰 한 줄만 쓴다. top-exit 기본 OFF, FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## SPL#4 top-exit promotion evidence

**COMPLETE 2026-10-22 — P FAIL against the frozen entry conditions.** The
[receipt and verdict](../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-receipt--2026-10-22)
are in the promotion evidence: no top-exit FULL row, the candidate equal to
the reference in every row, R not evaluated, N and U passing. Do not rerun.
The request below is kept as the record of what was asked.

**Requested 2026-10-22 — the user forwarded it and relayed the result.** One
request, three parts:
- **A, evidence:** two runs on SPL#4 (`SPL#4_Cooling_onoff_#2.mp4`) 0–90 s,
  reference IFO v2 against candidate IFO v2 + top-exit v3. They test the
  [promotion acceptance](../30-validation/s11-physical-interface-evidence-repair-validation.md#top-exit-v3-promotion-acceptance--2026-10-22)
  under its SPL#4 entry conditions.
- **C, read-only diagnosis:** a census of `INCOMPATIBLE_BRANCH` blank rows in
  the saved ⑩ bundle. It has no pass criterion; it tells whether such blanks
  come in runs of two or more inside the top band, the closure's known risk.
- **E, report confirmation:** the combined-graph strip and source patterns
  (E1/E2) on the candidate's report.

**Source:** code head `933ff49`; later commits are documents only. The Windows
agent checks five SHA-256 values before running. The six local negatives were
rerun at this head before the request.

**Pre-registered (from the entry conditions; judged by the agent, not on
Windows):**
- **BASE:**
  - P1, the first FULL row in 22.0–27.0 s; P2, no candidate-only FULL row
    before 22.0 s;
  - P3, from the first FULL row to 61.0 s only FULL or D2b UNKNOWN rows and no
    Oil coordinate; P4, the rows before it equal the reference;
  - R1, the episode end in 61.0–65.0 s; R2, no candidate-only FULL row in
    65.0–90.0 s;
  - U1, rows from the episode end equal the reference, pending rows aside.
- **Accum:** N1, no top-exit FULL row; N2, rows, events and report card equal.
- **Near misses:** a transition at 20–22 / 27–29 s or 59–61 / 65–67 s is
  UNDECIDED and goes to a Windows review of only 22–27 s or 61–65 s.
- **E1/E2:** the strip lies under the combined lines with BASE above Accum,
  each row matches its detail graph, and the patterns match the legend.
- **Stop:** any identity mismatch, an overlay the user rejects, a wrong
  resolver version or a run error. The agent stops and reports.

**Identity correction (2026-10-22):** the first attempt stopped at the size
check: the file is 53,165,455 bytes, but the request expected a mistyped
53,165,445. The user confirmed 53,165,455 from the file properties. No
detector run had started; the agent resumes at step 0-3 with the overlay it
already made.

**Not done:** tuning, Recipe/ROI/margin/threshold changes, extra reruns and
human review beyond the overlay check. Top-exit stays default OFF; O2 OPEN /
FIELD FAIL and review-006 pending are unchanged. The receipt goes in a new
section of the
[promotion evidence](../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md).

Prompt for the Windows agent (the user forwards it):

```text
S11 top-exit 승격 증거 요청 — SPL#4 두 실행(A) + ⑩ trace 읽기 전용 진단(C) + 리포트 띠 확인(E).
튜닝·Recipe/ROI/margin/임계값 변경·추가 재실행·사람 검토는 하지 마.
사람 확인은 0-3의 Recipe 확인 한 번뿐이고, 사용자가 한다.
값만 원문 그대로 돌려주고 판정·수정 제안 없이 멈춰. 새 bundle은 Windows에 보존한다.

0. 준비와 신원
 0-1. 최신 main 소스 ZIP(933ff49 이후)을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
      소스 폴더에서: $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
      실행 전 SHA-256 확인(하나라도 다르면 실행하지 말고 값만 알려줘):
      - src/oil_tracker/adapters/vision/oil_top_exit_full.py
        10dd3605a9ab0afb4ce4c0ae5a69477b1157318b0246ae972716d4202bb6f77d
      - src/oil_tracker/adapters/reporting/graph_renderer.py
        649affbe66800c7375d752708a0b940cee2502d8cd1a245d5c1c10e2f511e78d
      - src/oil_tracker/application/services/initial_state_reconstruction.py
        9fd04d25a10860fb5ba506311170209e71a9cfb09803f6166a1de5a4f93e1eed
      - src/oil_tracker/application/services/report_presentation.py
        6a1b0b512f8008bda71de4ae6bcb452e0c7a9295753b4edff06f446a10d6469f
      - tests/diagnostics/s11_initial_full_comparison.py
        b4ff712f21c1301627409acc4392030ea117d8390ee472baa57b3cd8cc0d81b3
 0-2. 영상은 SPL#4_Cooling_onoff_#2.mp4, Recipe는 이 영상용 기존 Recipe(Artifact 포함)를 쓴다.
      Recipe 파일은 수정하지 않는다. 새 출력 폴더 경로는 영문·숫자·밑줄만 쓴다
      (OpenCV 이미지 저장은 한글 경로에서 실패할 수 있다). 소스 폴더에서 실행:
        python -m tests.diagnostics.s11_initial_full_comparison --roi-overlay <새 출력 폴더>\roi --video <영상 경로> --recipe <Recipe 경로> --times 0,55
      roi-overlay.json에서 video(sha256, size_bytes, fps, frame_count, duration_sec, width, height),
      recipe(sha256, name), glasses(name, id, ellipse, margin_ratio, exclusions, artifact_templates, band_end_y)를
      그대로 적는다. size_bytes가 53165455가 아니면 멈추고 값만 알려줘.
 0-3. roi-overlay.png를 사용자에게 보여 주고 묻는다:
      "두 Glass 모두 초록 타원이 잔 내부 전체(안쪽 테두리부터 바닥 위까지)인가?"
      아니라고 하면 실행하지 말고 그 답만 알려줘.

1. 두 실행 (같은 소스·영상·Recipe·세션, 차이는 top_exit_full 하나)
   - 세션: 분석 0–90초, 2fps, FULL debug, compressor_start 없음.
   - 초기 상태: 메모리의 Recipe에서 두 Glass의 initial_state를 EMPTY_NO_INTERFACE로 두고,
     세션 initial_state_confirmations에도 두 Glass를 EMPTY_NO_INTERFACE(이 영상 경로, 시작 0초)로 넣는다.
     ⑩에서 BASE FULL / Accum EMPTY를 넣은 방식과 같다. Recipe 파일은 그대로 둔다.
   - ⑩과 같은 headless 방식(AnalysisPipeline + OutputBundleStore + JsonlDebugTraceWriterFactory):
     기준: OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=False), run_name "SPL4_A_ref"
     후보: OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True), run_name "SPL4_A_top_exit_v3"
     cost-first/RGB/Local XY는 OFF.
   - trace의 sequence_resolver_version: 기준은 "+initial-full-observation-v2"만 있어야 하고,
     후보는 "+top-exit-full-v3"도 있어야 한다. 아니면 멈추고 값만 알려줘.
   - 두 bundle은 0-2의 새 출력 폴더 아래에 둔다.

2. 머리줄: 두 run_id·run_name, 소스 폴더, 0-1의 SHA-256 5개, 두 sequence_resolver_version,
   두 bundle 경로, 0-2 값, 0-3 사용자 답, Glass별 행 수(기대 181),
   두 실행의 (glass_id, frame_index) 대응 결과(중복·누락·timestamp 불일치 수).

표기:
 - 행 = tracking_data.csv 한 줄. T = 후보 debug record의 sequence.state.sequence_material_phase_diagnostics.top_exit_full.
 - FULL 행 = fill_state가 FULL_NO_INTERFACE 또는 FULL_WITH_FOAM.
 - 다른 행 = 같은 (glass_id, frame_index)에서 fill_state, raw_oil_air_level_y, raw_foam_front_y,
   oil_is_valid, foam_is_valid, flags 중 하나라도 다른 행.
 - 목록은 frame/time으로 쓴다. 시간은 timestamp_sec.

3. 표 P — BASE
 a. 후보에서 flags에 OIL_TOP_EXIT_FULL이 있는 첫 행: frame/time/fill_state/T.reason (없으면 "없음")
 b. 기준과 후보에서 같은 frame이 모두 FULL인 행 수와 목록
 c. 후보에만 FULL인 행 중 22.0초 이전 행 수와 목록
 d. a의 행부터 61.0초 이전까지: 행 수, T.reason별 행 수,
    T.reason이 TOP_EXIT_FULL_CONFIRMED / TOP_EXIT_FULL_CONTINUING / TOP_EXIT_FULL_FRAME_UNAVAILABLE이 아닌 행 목록,
    raw_oil_air_level_y가 비어 있지 않은 행 목록
 e. a 이후 처음으로 T.episode_end가 있는 행: frame/time/T.episode_end/fill_state/raw_oil_air_level_y (없으면 "없음")
 f. 후보에만 FULL인 행 중 65.0~90.0초 행 수와 목록
 g. e 이후 처음으로 raw_oil_air_level_y가 있는 후보 행: frame/time/raw_oil_air_level_y
 h. T.confirmation이 PENDING / CONFIRMED / CANCELLED인 후보 행 목록

4. 표 N — Accum
 a. 후보에서 OIL_TOP_EXIT_FULL 행 수와 목록
 b. 기준·후보 각각의 FULL 행 수와 목록
 c. 기준·후보의 다른 행 수와 목록(최대 10개)
 d. events.csv의 Accum 행 중 두 실행이 다른 행 수와 목록(시간·event_type·note)
 e. 리포트 Accum 카드의 이동 요약·판정·"판정 안내" 문장이 두 실행에서 같은지(예/아니오), 다르면 두 문장 원문

5. 표 U — BASE 다른 행
 a. 표 P a의 행 이전에서 다른 행 수와 목록(최대 10개)
 b. 표 P e의 행부터 90초까지, T.confirmation이 PENDING인 행을 뺀 다른 행 수와 목록(최대 10개)
    (e가 "없음"이면 "해당 없음")

6. 표 Q — BASE, 20.0~28.0초와 59.0~67.0초(0.5초 간격) 각 한 줄:
   frame | time | 기준 fill_state / raw_oil_air_level_y | 후보 fill_state / raw_oil_air_level_y |
   T.reason | T.confirmation | T.predicates와 T.confirmation_predicates 중 false인 키 |
   T.witness 수와 마지막 y | T.episode_end | T.motion_phase
   키가 없으면 MISSING.

7. 표 S — 참고값: 두 실행의 Glass별 retrospective status·interval·barriers,
   review_index.json의 result_status와 effective_state_aware_coverage_ratio.

8. 리포트 띠 확인(E1·E2) — 후보 bundle의 graphs 폴더
 a. combined_levels.png: 선 그래프 아래 상태 줄이 있는지, 줄 이름(위→아래), 아래 범례 항목 목록
 b. BASE 상세 그래프: 범례 항목 목록, "FULL 판정" 띠가 단색인지, "초기 상태 재구성"이 있으면 빗금인지
 c. 상태 줄의 BASE·Accum 줄이 각 상세 그래프 띠와 위치·무늬가 같은지(예/아니오, 다르면 어디)

9. C 진단 — 저장된 ⑩ bundle(…_top_exit_v3_20261021_170933) 읽기 전용.
   파일을 수정하거나 새 결과 파일을 만들지 않는다.
   debug/debug_index.json, debug/debug_trace.jsonl, recipe_snapshot.oilrecipe, tracking_data.csv만 읽는다.
   Glass별(BASE, Accum):
 a. Recipe 타원 cy, ry와 띠 끝 Y = cy − ry + 0.54 × ry
 b. 빈 행 = raw_oil_air_level_y가 비어 있고 FULL 행이 아닌 행. 빈 행 수.
 c. 빈 행 중 그 record의 sequence.candidates[]에 tracklet_failure_reason = INCOMPATIBLE_BRANCH인 항목이 하나라도 있는 행 수
 d. c의 행이 0.5초 간격으로 이어지는 묶음 목록: 시작~끝 시간, 행 수, 묶음 안 그 후보들의 최소 y,
    최소 y ≤ 띠 끝 Y인지(예/아니오). 최대 30개, 넘으면 개수만.
 e. 행 수 2 이상이면서 d가 "예"인 묶음 수

10. 머리줄과 표 P/N/U/Q/S, 8의 답, 9의 표를 원문 그대로 돌려준다. 값은 고치거나 반올림하지 않는다.
    키가 없으면 MISSING, 값이 null이면 null. 결론·판정·수정 제안 없이 멈춘다.
    top-exit는 기본 OFF로 남고, FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Report confirmation run

**COMPLETE 2026-10-22 — PASS against the expectation written before the run.**
The [receipt and verdict](../60-evidence/s11/2026-10-21-initial-state-report-local.md#windows-report-confirmation--2026-10-22)
are recorded in the local verification. No failure condition occurred. Do not
rerun. The request below is kept as the record of what was asked.

**Requested 2026-10-21 — one run; the user forwards it and relays the result to a
new session.**
- **What it shows:** the frozen and implemented
  [initial-state continuing-run rule, labelled bands and judgment reason](../60-evidence/s11/2026-10-21-initial-state-report-local.md)
  on real Windows data.
- **Conditions:** ⑩'s (IFO v2 + top-exit v3), one run with run name
  `22-3_initial_ON_v2_top_exit_v3_report_v2`.
- **Identity:** by run ID, run name and hashes; circled labels may be misread in
  OCR transcription.

**Expected (written before the run; judged by the agent, not on Windows):**
- **Tracking data:** `tracking_data.csv` equals ⑩'s in every compared field;
  detector code is unchanged.
- **BASE:**
  - **Reconstruction:** `ACCEPTED`, provenance `initial_state_retrospective_v2`,
    interval 479.98–548.006 s. Evidence frames 13151 / 13606 / 13618
    (548.51 / 567.48 / 567.98 s).
  - **Coverage:** effective 553/601 ≈ 0.920; observed stays 0.692.
  - **Judgment:** decided by the level. PASS if no valid smoothed level is below
    zero for more than 1 s; the note ends with
    `provenance=retrospective_initial_state`.
  - **Report:** `판정 안내` gives the level sentence plus `첫 검출 이전 구간은 확정한
    초기 상태로 재구성해 판정에 포함했습니다.`
  - **Graph:** the legend shows `초기 상태 재구성 (FULL)` and `FULL 판정`, with blue
    bands at 480–548 s and 674–780 s.
- **Accum:** `UNRESOLVED`, barrier `AUTHORITATIVE_FOAM`; `REVIEW_REQUIRED` with
  coverage 6.0%. `판정 안내` names the 6.0% / 70.0% shortfall.
- **Overall:** `REVIEW_REQUIRED`, because of Accum.
- **Failure:**
  - any tracking-row difference;
  - BASE not accepted, or a different interval or evidence;
  - Accum accepted;
  - raw English note text in the report;
  - a missing band or label.

  A BASE FAIL on the level is a result, not a failure of this check.
- **Record:** the receipt goes in a new section of the
  [local verification](../60-evidence/s11/2026-10-21-initial-state-report-local.md).

Prompt for the Windows agent (the user forwards it):

```text
S11 리포트 확인 실행 — ⑩과 같은 조건으로 한 번만 실행해줘.
run_name은 "22-3_initial_ON_v2_top_exit_v3_report_v2"로 한다.
튜닝·ROI/margin/임계값 변경·추가 재실행·새 사람 검토는 하지 마.

0. 최신 main 소스 ZIP(139ba87 이후)을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
   실행 전 SHA-256 확인(다르면 실행하지 말고 값만 알려줘):
   - src/oil_tracker/application/services/initial_state_reconstruction.py
     9fd04d25a10860fb5ba506311170209e71a9cfb09803f6166a1de5a4f93e1eed
   - src/oil_tracker/adapters/reporting/graph_renderer.py
     a4776e06ff95f0ad44acd308f18e417d2645ffb2189ddac11ff870dd1217ebf5
   - src/oil_tracker/application/services/report_presentation.py
     6a1b0b512f8008bda71de4ae6bcb452e0c7a9295753b4edff06f446a10d6469f
   - src/oil_tracker/adapters/vision/oil_top_exit_full.py
     10dd3605a9ab0afb4ce4c0ae5a69477b1157318b0246ae972716d4202bb6f77d

1. ⑩과 같은 영상·Recipe·ROI/margin/exclusion/Artifact·영점/스케일,
   480–780초, 2fps, FULL debug, compressor_start 485초,
   BASE FULL / Accum EMPTY 초기 확정, 같은 headless 방식,
   OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True).
   출력은 기준 bundle 폴더 아래 새 폴더에 둔다.

2. 머리줄: run_id, run_name, 소스 폴더, 위 4개 SHA-256, sequence_resolver_version, 출력 bundle 경로.

3. ⑩ bundle(…_top_exit_v3_20261021_170933)과 tracking_data.csv를 (glass_id, frame_index)로 대응해
   fill_state, raw_oil_air_level_y, raw_foam_front_y, is_valid, oil_is_valid, foam_is_valid, flags 중
   하나라도 다른 행 수 (Glass별, 최대 10개 목록).

4. review_index.json: Glass별 result_status, observed_coverage_ratio,
   effective_state_aware_coverage_ratio, retrospective_status.

5. retrospective_interpretation.json: Glass별 status, provenance, interval, frame_interval,
   evidence_frame_indices, evidence_timestamps_sec, barriers, reason 원문.

6. events.csv: JUDGMENT_PASS / JUDGMENT_FAIL / REVIEW_REQUIRED 중 note가 있는 행,
   FULL_NO_INTERFACE_START 행 전체 (glass_id, 시간, note 원문).

7. BASE tracking_data.csv: is_valid=True 행 중 smoothed_oil_air_level_px_from_zero 최솟값과
   그 frame_index/timestamp_sec.

8. 리포트 HTML: Glass별 "판정 안내" 문장 원문.
   BASE 상세 그래프 PNG: 범례 항목 목록, 그리고 480–548초와 674–780초에
   파란 띠가 보이는지(예/아니오).

값만 원문 그대로 돌려주고 판정·수정 제안 없이 멈춰. 새 bundle은 Windows에 보존한다.
```

## Top-exit v3 comparison

**COMPLETE 2026-10-21 — PASS against the pre-registered outcome.** The
[receipt and verdict](../60-evidence/s11/2026-10-21-top-exit-v3-local.md#windows-top-exit-v3-comparison--2026-10-21)
are recorded in the v3 evidence. BASE FULL started at 674.0 s; the 663.0 s
pending closure was cancelled at 663.5 s. Do not rerun. The procedure below is
kept as the record of what was requested.

**Requested 2026-10-21 — one run, authorized by the user's choice of option B.**
The comparison is ④ FULL+ON v2 (existing bundle, reused) against ⑩ FULL+ON v2
+ top-exit v3. Only `initial_full_observation` and `top_exit_full` are ON;
cost-first, RGB and Local XY stay OFF. ⑨ (v2) failed and is not rerun.

- **Source:** the [frozen v3 design](../20-architecture/s11-physical-interface-evidence-repair-design.md#october-21-top-exit-revision-v3)
  (`e88d387`), with
  [local controls PASS](../60-evidence/s11/2026-10-21-top-exit-v3-local.md).
  The Windows agent checks the module SHA-256
  `10dd3605a9ab0afb4ce4c0ae5a69477b1157318b0246ae972716d4202bb6f77d` before
  running.
- **Run:** identical to ④ and ⑨:
  - video, Recipe and ROI/margin/exclusion/Artifact, zero and scale;
  - 480–780 s, 2 fps, FULL debug, compressor start 485 s;
  - BASE FULL / Accum EMPTY initial confirmations.

  The output goes to a new folder; the bundle stays on Windows.
- **Pre-registered outcome (unchanged from ⑨; judged here, not on Windows):**
  - **BASE:**
    - the first FULL falls within 672–675 s; 674.0 s is expected;
    - no FULL before 672 s;
    - FULL holds through 675–780 s with no numeric Oil.
  - **Accum:** zero FULL rows.
  - **Both Glasses:** rows before closure match ④ exactly.
  - **Failure:** FULL before 672 s or in Accum; a changed row before closure; or
    FULL ending inside 675–780 s.
- **Tables:**
  - **P:** the pre-registered values;
  - **Q:** the top-exit records at 662.5–664.0 s and 672.5–675.0 s, including
    `confirmation` and its false predicates;
  - **R:** the standard interval accounting.

  **Spot checks:**
  - BASE 721/723/771 s;
  - FULL rows carry no Oil coordinate;
  - the raw image FULL likelihood is unchanged;
  - 675–780 s fill states match ⑨.

  The diagnostics explain a failure; they are not extra criteria.
- **Not done:** tuning, ROI/margin/threshold changes, extra reruns, new human
  review. If identity or the run fails, the agent stops and reports. Top-exit
  stays default OFF; O2 OPEN / FIELD FAIL and review-006 pending are unchanged.
  Record the receipt in a new section of the
  [v3 evidence](../60-evidence/s11/2026-10-21-top-exit-v3-local.md).

Prompt for the Windows agent (the user forwards it):

```text
S11 ⑩ top-exit FULL v3 비교 실행 — ④·⑨와 같은 조건으로 한 번만 실행해줘.
튜닝·ROI/margin/임계값 변경·추가 재실행·새 사람 검토는 하지 마.
새 실행은 반드시 "⑩"으로 표기해줘(⑧·⑨와 섞이지 않게).

비교: ④ FULL+ON v2 (기존 bundle 재사용) ↔ ⑩ FULL+ON v2 + top-exit v3
(initial-full-observation과 top-exit-full만 ON, cost-first/RGB/Local XY OFF)
v3 = v2 + "이탈 다음 프레임도 이탈이어야 FULL 확정". 이탈 프레임 자체는 UNKNOWN으로 남는다.

0. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
   실행 전 src/oil_tracker/adapters/vision/oil_top_exit_full.py의 SHA-256이
   10dd3605a9ab0afb4ce4c0ae5a69477b1157318b0246ae972716d4202bb6f77d 인지 확인한다.
   다르면 실행하지 말고 그 값만 알려줘.
   자세한 절차는 docs/40-operations/s11-current-windows-field-qualification.md의
   "Top-exit v3 comparison"에 있다.

1. ④와 같은 영상·Recipe·ROI/margin/exclusion/Artifact·영점/스케일,
   480–780초, 2fps, FULL debug, compressor_start 485초,
   BASE FULL / Accum EMPTY 초기 확정값으로 실행한다.
   ⑨와 같은 headless 방식(AnalysisPipeline + AnalyzeVideoUseCase +
   OutputBundleStore + JsonlDebugTraceWriterFactory)을 새 소스 폴더에서 쓰고
   OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True)로 만든다.
   GUI를 쓰면 소스 폴더에서:
     $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
     python -m oil_tracker --initial-full-observation --oil-top-exit-full
   trace의 sequence_resolver_version에 "+initial-full-observation-v2+top-exit-full-v3"가
   있어야 하고 cost-first/RGB/Local XY 접미사는 없어야 한다.
   실제 사용한 경로를 기록한다. 출력 bundle의 절대 경로는 한 곳만 적는다.
   ⑨ bundle의 실제 위치도 한 곳으로 확인해서 적어줘(지난 보고에 경로가 두 개였다).

2. ④와 ⑩의 tracking_data.csv를 (glass_id, frame_index)로 일대일 대응한다.
   Glass별 행 수와 중복·누락·timestamp 불일치를 한 줄로 적는다(기대 601행).

3. 표 P — 사전 등록 확인값 (값만):
   - BASE 첫 FULL_NO_INTERFACE 행의 frame/time
   - BASE 672.0초 이전 FULL 행 수
   - BASE 675–780초: 행 수, FULL 행 수, 숫자 Oil 행 수,
     FULL이 아닌 행 목록(frame/time/fill_state/아래 T.reason, 최대 20개)
   - BASE 첫 FULL 이후 처음으로 FULL이 아닌 행:
     frame/time/fill_state/T.reason/T.episode_end (780초까지 없으면 "없음")
   - Accum FULL 행 수와 목록
   - ④와 ⑩이 다른 행 수: BASE는 첫 FULL 이전, Accum은 전체.
     fill_state, raw_oil_air_level_y, raw_foam_front_y, oil_is_valid,
     foam_is_valid, flags 중 하나라도 다르면 다른 행이다. 최대 10개 목록.
   - BASE 전체에서 T.confirmation이 PENDING / CONFIRMED / CANCELLED인 행의
     frame/time 목록

4. 표 Q — BASE 662.5~664.0초(4개)와 672.5~675.0초(6개), 0.5초 간격 record.
   각 한 줄:
   frame | time | ⑩ fill_state | ⑩ raw_oil_air_level_y | T.reason |
   T.confirmation | T.confirmation_predicates 중 false인 키 |
   T.predicates 중 false인 키 | T.anchor_source |
   T.witness(frame_index:y:selected 목록) |
   T.disappearance_frame_index | T.confirmation_frame_index | T.episode_end
   T = sequence.state.sequence_material_phase_diagnostics.top_exit_full.
   키가 없으면 MISSING.

5. 표 R — 기존 구간 함수로 각 행을 한 구간에만 배정한 구간표.
   BASE 480–550 / 550–652 / 652–674 / 674–675 / 675–780초 + OUTSIDE,
   Accum 480–653 / 653–672 / 672–680 / 680–700 / 700–780초 + OUTSIDE.
   열: 표본 | ④ Oil | ⑩ Oil | 신규 | 소실 | 양쪽 숫자 Y 변경 | ④ FULL | ⑩ FULL |
   Foam 좌표·validity가 다른 행 수.

6. 확인 4가지 (값만):
   - BASE 721 / 723 / 771초 record의 ④·⑩ fill_state와 raw_oil_air_level_y
   - ⑩ FULL 행 중 raw_oil_air_level_y가 비어 있지 않거나
     flags에 OIL_TOP_EXIT_FULL이 없는 행 수
   - ⑩ FULL 행 중 record.state.oil_no_interface_full_likelihood가
     ④의 같은 record 값과 다른 행 수
   - BASE 675–780초에서 ⑨와 ⑩의 fill_state가 다른 행 수와 목록(최대 10개)

7. 머리줄(④·⑩ run_id, 소스 폴더, 모듈 SHA-256, sequence_resolver_version,
   실행 경로, ⑩·⑨ bundle 경로)과 표 P/Q/R, 확인 4가지를 원문 그대로 돌려준다.
   값은 고치거나 반올림하지 않는다. 판정·수정 제안 없이 반환 후 멈춘다.
   ⑩ bundle은 Windows에 보존한다. top-exit는 기본 OFF로 남고,
   FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Top-exit v2 comparison

**COMPLETE 2026-10-21 — FAIL against the pre-registered outcome.** The
[receipt and verdict](../60-evidence/s11/2026-10-21-top-exit-v2-local.md#windows-top-exit-v2-comparison--2026-10-21)
are recorded in the v2 evidence. BASE FULL started at 663.0 s (18 rows before
672 s). Accum, the rows before closure and the 675–780 s hold passed. Do not
rerun; any successor needs a new frozen design and the user's go. The procedure
below is kept as the record of what was requested.

**Requested 2026-10-21 — one run, authorized by the user.** The comparison is
④ FULL+ON v2 (existing bundle, reused) against ⑨ FULL+ON v2 + top-exit v2.
Only `initial_full_observation` and `top_exit_full` are ON; cost-first, RGB and
Local XY stay OFF. ⑧ named the v1 run, which was never executed; v2 takes ⑨ so
the two cannot be confused.

- **Source:** the [frozen design](../20-architecture/s11-physical-interface-evidence-repair-design.md#october-21-top-exit-revision-v2),
  implemented at `1f68c46` with
  [local controls PASS](../60-evidence/s11/2026-10-21-top-exit-v2-local.md).
  The Windows agent checks the module SHA-256
  `7b493c1ed99ff19418830179f513d24764fe2f8db7eb0cc02cc202cc774411a3` before
  running.
- **Run:** identical to ④:
  - video, Recipe and ROI/margin/exclusion/Artifact, zero and scale;
  - 480–780 s, 2 fps, FULL debug, compressor start 485 s;
  - BASE FULL / Accum EMPTY initial confirmations.

  Output goes to a new folder under `sample/output/`; the bundle stays on
  Windows.
- **Pre-registered outcome (frozen before the run; judged by the agent here, not
  on Windows):**
  - **BASE:** the first FULL falls within 672–675 s (673.5 s expected); no FULL
    before 672 s; FULL holds through 675–780 s with no numeric Oil.
  - **Accum:** zero FULL rows.
  - **Both Glasses:** rows before closure match ④ exactly.
  - **Failure:** FULL before 672 s or in Accum; a changed row before closure; or
    FULL ending inside 675–780 s.
- **Tables:**
  - **P:** the pre-registered values;
  - **Q:** BASE 670.0–674.0 s top-exit diagnostics, including the witness with
    `selected` and the `anchor_source`;
  - **R:** the standard interval accounting.

  Spot checks: BASE 721/723/771 s, FULL rows carry no Oil coordinate, and raw
  image FULL likelihood is unchanged.
- **Not done:** tuning, ROI/margin/threshold changes, extra reruns, new human
  review. If identity or the run fails, the agent stops and reports. Top-exit
  stays default OFF; O2 OPEN / FIELD FAIL and review-006 pending are unchanged.
  Record the receipt in a new section of the
  [v2 evidence](../60-evidence/s11/2026-10-21-top-exit-v2-local.md).

Prompt for the Windows agent (the user forwards it):

```text
S11 ⑨ top-exit FULL v2 비교 실행 — ④와 같은 조건으로 한 번만 실행해줘.
튜닝·ROI/margin/임계값 변경·추가 재실행·새 사람 검토는 하지 마.

비교: ④ FULL+ON v2 (기존 bundle 재사용) ↔ ⑨ FULL+ON v2 + top-exit v2
(initial-full-observation과 top-exit-full만 ON, cost-first/RGB/Local XY OFF)

0. 최신 main 소스 ZIP을 새 폴더에 풀고 기존 Windows Python 환경을 쓴다.
   실행 전 src/oil_tracker/adapters/vision/oil_top_exit_full.py의 SHA-256이
   7b493c1ed99ff19418830179f513d24764fe2f8db7eb0cc02cc202cc774411a3 인지 확인한다.
   다르면 실행하지 말고 그 값만 알려줘.
   자세한 절차는 docs/40-operations/s11-current-windows-field-qualification.md의
   "Top-exit v2 comparison"에 있다.

1. ④와 같은 영상·Recipe·ROI/margin/exclusion/Artifact·영점/스케일,
   480–780초, 2fps, FULL debug, compressor_start 485초,
   BASE FULL / Accum EMPTY 초기 확정값으로 실행한다.
   GUI를 쓰면 소스 폴더에서:
     $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
     python -m oil_tracker --initial-full-observation --oil-top-exit-full
   창 제목에 "초기 FULL 관측 비교"와 "상단 이탈 FULL 비교"가 보여야 한다.
   기존 headless 실행기를 쓰면
   OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True)로 만든다.
   trace의 sequence_resolver_version에 "+initial-full-observation-v2+top-exit-full-v2"가
   있어야 하고 cost-first/RGB/Local XY 접미사는 없어야 한다.
   실제 사용한 경로를 기록하고, 출력은 sample/output/ 아래 새 폴더에 둔다.

2. ④와 ⑨의 tracking_data.csv를 (glass_id, frame_index)로 일대일 대응한다.
   Glass별 행 수와 중복·누락·timestamp 불일치를 한 줄로 적는다(기대 601행).

3. 표 P — 사전 등록 확인값 (값만):
   - BASE 첫 FULL_NO_INTERFACE 행의 frame/time
   - BASE 672.0초 이전 FULL 행 수
   - BASE 675–780초: 행 수, FULL 행 수, 숫자 Oil 행 수,
     FULL이 아닌 행 목록(frame/time/fill_state/아래 T.reason, 최대 20개)
   - BASE 첫 FULL 이후 처음으로 FULL이 아닌 행:
     frame/time/fill_state/T.reason/T.episode_end (780초까지 없으면 "없음")
   - Accum FULL 행 수와 목록
   - ④와 ⑨가 다른 행 수: BASE는 첫 FULL 이전, Accum은 전체.
     fill_state, raw_oil_air_level_y, raw_foam_front_y, oil_is_valid,
     foam_is_valid, flags 중 하나라도 다르면 다른 행이다. 최대 10개 목록.

4. 표 Q — BASE 670.0~674.0초, 0.5초 간격 9개 record. 각 한 줄:
   frame | time | ⑨ fill_state | ⑨ raw_oil_air_level_y |
   T.reason | T.anchor_source | T.predicates 중 false인 키 |
   T.witness(frame_index:y:selected 목록) | T.episode_end
   T = sequence.state.sequence_material_phase_diagnostics.top_exit_full.
   키가 없으면 MISSING.

5. 표 R — 기존 구간 함수로 각 행을 한 구간에만 배정한 구간표.
   BASE 480–550 / 550–652 / 652–674 / 674–675 / 675–780초 + OUTSIDE,
   Accum 480–653 / 653–672 / 672–680 / 680–700 / 700–780초 + OUTSIDE.
   열: 표본 | ④ Oil | ⑨ Oil | 신규 | 소실 | 양쪽 숫자 Y 변경 | ④ FULL | ⑨ FULL |
   Foam 좌표·validity가 다른 행 수.

6. 확인 3가지 (값만):
   - BASE 721 / 723 / 771초 record의 ④·⑨ fill_state와 raw_oil_air_level_y
   - ⑨ FULL 행 중 raw_oil_air_level_y가 비어 있지 않거나
     flags에 OIL_TOP_EXIT_FULL이 없는 행 수
   - ⑨ FULL 행 중 record.state.oil_no_interface_full_likelihood가
     ④의 같은 record 값과 다른 행 수

7. 머리줄(④·⑨ run_id, 소스 폴더, 모듈 SHA-256, sequence_resolver_version,
   실행 경로)과 표 P/Q/R, 확인 3가지를 원문 그대로 돌려준다.
   값은 고치거나 반올림하지 않는다. 판정·수정 제안 없이 반환 후 멈춘다.
   ⑨ bundle은 Windows에 보존한다. top-exit는 기본 OFF로 남고,
   FIELD FAIL / O2 OPEN, review-006 pending은 바뀌지 않는다.
```

## Top-exit predicate check

**COMPLETE 2026-10-21 — reference record; do not re-ask.** [Receipt](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#predicate-check-receipt--2026-10-21):
only `independent_anchor` fails on ④. Saved ④ trace only; no run.
The [673 s receipt](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#673-s-selection-cause-receipt--2026-10-21)
(S6) found that the adopted revision items 1–5 do not cover every top-exit
predicate. The likely blocker is `independent_anchor`: a window row must be
`ANCHOR_ELIGIBLE` with `direct_interface` or `ordered_lower_interface` identity.
Every reported 0319 member is `CONTINUATION_ELIGIBLE`; rows at 670.5 and 671.5 s
are unreported. This request copies the stored inputs of the remaining
predicates for 670.0–673.5 s. It does not evaluate them; the artifact and optics
terms are not stored and are not requested.

```text
S11 top-exit 판정 조건 점검 — 저장된 ④ trace 읽기 전용 추출이야.
재실행·새 bundle·튜닝·비교 실행·새 사람 검토는 하지 마.
파일은 수정·이동하지 말고 결과 파일도 만들지 마.

목적: top-exit FULL의 나머지 판정 조건 입력값을 ④ BASE 670.0~673.5초에서
저장값 그대로 옮겨 적는다. 충족 여부는 판정하지 않는다.

1. 지난번처럼 ④ bundle의 debug/debug_index.json과 debug/debug_trace.jsonl만 읽는다.
   index에서 glass_name=BASE, timestamp_sec로 record를 찾아 byte_offset으로 읽는다.
   경로 표기: S = sequence.state, W = S.sequence_decision_witness,
   C = sequence.candidates[], R = record 최상위.

2. 표 G — f16064 / f16076 / f16088 / f16100 / f16112 / f16124 / f16136 / f16148
   (670.0~673.5초, 0.5초 간격) 각 한 줄:
   frame | effective_gray_mean / effective_gray_std / effective_gray_dynamic_range |
   oil_no_interface_empty_likelihood | S.sequence_material_phase_ambiguous |
   W.rows 중 phase_admitted=true인 row의 tracklet_id 목록(중복 제거) |
   C 중 identity_contradiction이 none이 아닌 항목 수와 그 source:y:값
   앞의 두 칸은 S에서 읽고, S에 키가 없으면 R.state 값을 쓰고 "(R)"을 붙인다.

3. 표 H — 같은 8개 frame에서 W.rows 중 tracklet_id = oil-tracklet:000366:0319인
   row의 member마다, source와 y가 같은 C 항목을 찾아 한 줄:
   frame | row_hypothesis_id | source | y | selected | authority | phase_identity |
   identity_contradiction | tracklet_admitted | tracklet_incompatible |
   tracklet_lifecycle | tracklet_material_conflict | tracklet_recent_direction |
   tracklet_recent_directional_agreement | tracklet_recent_net_progress_px |
   material_texture_conflict(C.features 또는 C.penalties의 값, 둘 다 없으면 MISSING)
   0319 row가 없으면 "0319 없음", 같은 source·y가 여럿이거나 없으면 "대응 불명".

4. 머리줄(run_id, BASE record 수)과 표 G/H를 텍스트 원문 그대로 돌려준다.
   값은 고치거나 반올림하지 않는다. 키가 없으면 MISSING, 값이 null이면 null.
   결론은 "authority가 ANCHOR_ELIGIBLE인 0319 member가 있는 frame" 같은 관찰 한 줄만 쓴다.
   원인 판정·수정 제안 없이 반환 후 멈춘다.
   FIELD FAIL / O2 OPEN, review-006 pending, ⑧ NOT RUN 상태는 바뀌지 않는다.
```

Record the receipt in OTR-1.

## 673-second selection-cause extraction

**COMPLETE 2026-10-21 — reference record; do not re-ask.** [Receipt](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#673-s-selection-cause-receipt--2026-10-21):
the 673.0 s row was publishable; the bounded path chose unknown (path cost).
Saved ④ trace only; no run. This is item 3 of the
[top-exit revision](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#review-011-result--2026-10-21).
Review-011 confirmed that Y329 at 673.0 s (`oil-tracklet:000366:0319`) is the
level, yet nothing was selected.

The trace splits two causes:
- **(a) publishability:** the row was never in the publishable layer.
- **(b) path cost:** it was publishable, but the bounded path chose unknown.

`sequence.state.sequence_decision_witness.rows[]` (`r21-decision-witness-v1`,
present since `fe6eb95`, so also in ④'s `4c72ebb`) stores each row's
`publishable` flag. That flag is computed before the allowed-set filter, so one
saved value separates (a) from (b):
- **For (a):** `sequence.candidates[]` gives the clause inputs
  (`trajectory_support`, `tracklet_confirmation_profile`).
- **For (b):** the stored unknown-node emission and the Recipe jump limit explain
  the path choice.

The confidence value itself is not stored. Recomputing it would need a frozen
tool and is left for a later step only if needed.

```text
S11 673초 선택 누락 원인 확인 — 저장된 ④ trace 읽기 전용 추출이야.
재실행·새 bundle·튜닝·비교 실행·새 사람 검토는 하지 마.
파일은 수정·이동하지 말고 결과 파일도 만들지 마.

목적: review-011에서 실제 유면으로 확인된 673.0초 Y329(oil-tracklet:000366:0319)가
왜 선택되지 않았는지 저장값으로 구분한다.
(가) 출력 후보 자격(publishable)에서 빠졌는지,
(나) 자격은 있었는데 경로 선택이 unknown을 골랐는지.

1. ④ bundle의 debug/debug_index.json, debug/debug_trace.jsonl, recipe_snapshot.oilrecipe만 읽는다.
   지난번처럼 index에서 glass_name=BASE, timestamp_sec로 record를 찾아 byte_offset으로 읽는다.
   경로 표기: S = sequence.state, W = S.sequence_decision_witness,
   C = sequence.candidates[], R = record 최상위.

2. 표 D — f16064 / f16088 / f16112 / f16124 / f16136
   (670.0 / 671.0 / 672.0 / 672.5 / 673.0초) 각 한 줄:
   frame | W.phase.value / W.phase.reason | W.phase.allowed_tracklet_ids |
   W.selection.resolved_kind | W.selection.selected_candidate(source, y, row_hypothesis_id) |
   W.rows 중 tracklet_id = oil-tracklet:000366:0319인 각 row:
     row_hypothesis_id, phase_admitted, publishable,
     members(source:y:authority:tracklet_lifecycle:selected) |
   W.rows 중 publishable=true인 row 수와 그 tracklet_id:y 목록
   0319 row가 없으면 "0319 없음"으로 둔다.

3. 표 E — 표 D의 0319 member마다, source와 y가 같은 C 항목을 찾아 한 줄:
   frame | source | y | trajectory_support | cluster_support | semantic_corridor_support |
   cross_representation_support | effective_track_opposition | tracklet_confirmation_profile |
   tracklet_lifecycle | tracklet_material_conflict | reject_stage
   같은 source·y가 여럿이거나 없으면 "대응 불명"으로 두고 다른 항목으로 채우지 않는다.

4. 표 F — f16136(673.0초)과 Recipe 값 한 줄:
   S.sequence_emission | R.state.oil_ambiguity_score | R.state.oil_no_interface_score |
   recipe_snapshot의 BASE glass detector_settings.minimum_final_confidence |
   detector_settings.temporal_max_jump_px

5. 자체 확인: 670.0~672.5초에 선택된 0319 row는 publishable=true여야 한다.
   아니면 그 행에 "불일치"만 표시하고 원인은 조사하지 않는다.

6. 머리줄(run_id, BASE record 수)과 표 D/E/F를 텍스트 원문 그대로 돌려준다.
   값은 고치거나 반올림하지 않는다. 키가 없으면 MISSING, 값이 null이면 null.
   결론은 "673.0초 0319 row의 publishable 값" 같은 관찰 한 줄만 쓴다.
   원인 판정·수정 제안 없이 반환 후 멈춘다.
   FIELD FAIL / O2 OPEN, review-006 pending, ⑧ NOT RUN 상태는 바뀌지 않는다.
```

Record the receipt in OTR-1.

## Review-011 BASE level at the fast-rise onset

**COMPLETE 2026-10-21 — reference record; do not re-ask.** [Result](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#review-011-result--2026-10-21). Human review only; no run or extraction. This answers
the open identity question in
[OTR-1 §6](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#6-windows-trace-receipt--2026-10-21).

The user's video review says:
- the level rises fast from about 670 s;
- it is almost full near 672 s;
- FULL is acceptable from about 672 s
  ([reviewed truth](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#base-full-acceptance--2026-10-21)).

In ④ the IFO v2 owner `000366:0319` is selected at Y384 → Y350 → Y352
(670.0–672.5 s), and an admitted Y329 is not selected at 673.0 s. The question is
whether those rows are the real level.
- **If they are:** an upper-band top-exit endpoint is physically justified.
- **If the level was far above them:** the detector missed the fast rise.

Reuse:
- **Source:** the review-010 source folder (`87817ad`). Neither `src/` nor the O2
  tool has changed since.
- **ID:** review-011 is the next free case ID. The paused layered-Foam line had
  earmarked it; that line takes the next ID instead.

```text
S11 review-011 — BASE 빠른 상승 구간의 실제 유면 위치 확인. 기존 ④ bundle로 사람 검토만 해.
실행·재실행·추출·튜닝은 하지 마.

목적: 사용자가 영상에서 본 "670초부터 빠르게 차올라 672초 부근 거의 full"과
④ 검출선(670초 Y384 → 672초 Y350 → 672.5초 Y352, 673초 미선택 Y329)이
같은 유면인지 사용자가 직접 확인한다.

0. 소스는 review-010 때 쓴 소스 폴더(87817ad)를 그대로 쓴다. O2 도구와 src는 그 뒤 바뀌지 않았다.
   bundle은 같은 ④ FULL+ON v2 bundle이다. 이동·수정하지 않는다.

1. s11-o2-local-shadow-evaluation.md의 "3. 에이전트 질문 → 사용자 회신 → 기록·재개"
   절차를 그대로 쓴다. 같은 ④ bundle로 새 review-011을 prepare한다
   (BASE, f16064 / f16088 / f16112 / f16124 / f16136) → link-bundle.
   selection의 recording_group/partition은 review-010과 같게 둔다.
   review-001~010(특히 006)은 열거나 고치지 않는다.

2. 표시할 후보. packet 후보 목록에서 canonical_y를 반올림한 값이 일치하는 idx를 찾아
   가이드에 표시한다. 같은 Y에 idx가 여럿이면 모두 표시한다.
   못 찾으면 "없음"으로 보고하고 다른 후보로 바꾸지 않는다.
   - f16064 / 670.0초: Y384 (출력)
   - f16088 / 671.0초: Y369 (출력)
   - f16112 / 672.0초: Y350 (출력)
   - f16124 / 672.5초: Y352 (출력), Y336, Y338
   - f16136 / 673.0초: Y329 (미선택), Y343

3. 질문 전에 plain / idx-guide 이미지를 열고 파일 경로를 알려준다.
   프레임마다 두 가지만 묻는다.
   Q1 "실제 유면(오일–공기 경계)이 보이나요? 보이면 표시한 후보 중 유면에 있는 idx는?
       유면이 표시한 후보들보다 위에 있으면 '후보보다 위', 아래면 '후보보다 아래'."
   Q2 "표시한 각 후보는 무엇인가요? 유면 / 유면 아님(구조·반사·기타) / 판단 보류"
   거의 가득 차서 경계가 안 보이면 '안 보임'으로 답해도 된다.
   여러 idx와 판단 보류를 허용한다. 에이전트가 고르거나 좌표를 추정하지 않는다.
   사용자가 가이드 눈금으로 대략 위치를 말하면 그 말만 비고에 그대로 적는다.

4. 사용자 답을 record로 저장한다.
   - visibility: 유면 보임 → visible, 안 보임 → not_visible, 판단 어려움 → uncertain
   - 후보 identity: 유면 → interface, 유면 아님 → non_interface
     (구조·반사면 artifact_tags에 structure/reflection), 판단 보류 → uncertain
   - '후보보다 위/아래'와 대략 위치는 reply note에 한 줄로 남긴다. contour는 비워 둔다.

5. 프레임별로 한 줄만 반환한다.
   frame | 유면 보임 | 유면 idx (또는 후보보다 위/아래) | 후보별 판정(idx=유면/아님/보류 …) | 비고
   영상·이미지·JSON 원본은 보내지 않는다. 원인 판정이나 수정 제안 없이 멈춘다.
   FIELD FAIL / O2 OPEN, review-006 pending, ⑧ NOT RUN 상태는 바뀌지 않는다.
```

Record the receipt in OTR-1. Then the user chooses the D1b endpoint:
- **Rows are the level:** the upper band, with a frozen local two-sided check first.
- **Level far above:** fast-rise recall comes first.

## Review-010 upper-row roles at Foam-collapse onset

**COMPLETE — reference record; do not re-ask.** [Result](../50-diagnostics/s11/2026-10-20-approach-review.md#review-010-result). Human review only; no run or extraction. Step 1 of the
[ARV-1 recommendation](../50-diagnostics/s11/2026-10-20-approach-review.md#recommendation).
It asks whether the published/anchor rows above the reviewed boundary are the
air–liquid top (the collapse fallback target), Foam interior or something else.
It uses the [O2 procedure](s11-o2-local-shadow-evaluation.md#3-에이전트-질문--사용자-회신--기록재개)
on the same ④ bundle. The O2 tool and `src/` are unchanged since `1c21444`, so
the LBW-3 source folder (`87817ad`) is reused. Review-001–009 are not opened or
changed. Roles are kept in the reply note because the label schema has no role
field.

```text
S11 review-010 — Foam 붕괴 시작 구간 위쪽 행의 역할 확인. 기존 ④ bundle로 사람 검토만 해.
실행·재실행·추출·튜닝은 하지 마.

목적: 677 / 678.5 / 679초에 현재 출력이나 anchor로 쓰이는 위쪽 행이
air–액체(또는 air–Foam) 상면인지, Foam 내부인지 사용자가 직접 확인한다.

0. 소스는 LBW-3 때 풀어둔 소스 폴더(87817ad)를 그대로 쓴다. O2 도구는 그 뒤 바뀌지 않았다.
   bundle은 같은 ④ FULL+ON v2 bundle이다. 이동·수정하지 않는다.

1. s11-o2-local-shadow-evaluation.md의 "3. 에이전트 질문 → 사용자 회신 → 기록·재개"
   절차를 그대로 쓴다. 같은 ④ bundle로 새 review-010을 prepare한다
   (Accum, f16232 / f16268 / f16280) → link-bundle.
   selection의 recording_group/partition은 review-009와 같게 둔다.
   review-001~009(특히 006, 009)는 열거나 고치지 않는다.

2. 질문할 후보. packet 후보 목록에서 canonical_y를 반올림한 값이 일치하는 idx를
   찾아 가이드에 표시한다. 같은 Y에 idx가 여럿이면 모두 표시한다.
   못 찾으면 "없음"으로 보고하고 다른 후보로 바꾸지 않는다.
   - f16232 / 677.0초: idx11 Y235 (anchor), idx16 Y269 (출력)
   - f16268 / 678.5초: idx16 Y229 (anchor), idx21 Y238 (출력), Y392, Y403
   - f16280 / 679.0초: Y391, Y392
   참고로 보여줘도 되는 기존 답: 679초 상면 Y213(R22),
   유체–유체 층 idx11/20/25 Y412–416(review-009).

3. 질문 전에 plain / idx-guide 이미지를 열고 파일 경로를 알려준다.
   프레임마다 두 가지만 묻는다.
   Q1 "맨 위 상면이 보이나요? 보이면 종류(air–Foam / air–액체)와,
       그 상면에 있는 후보 idx는? (없으면 '후보 없음')"
   Q2 "표시한 각 후보는 무엇인가요? 상면 / Foam 내부 / 유체–유체 층 / 기타 / 판단 보류"
   여러 idx와 판단 보류를 허용한다. 에이전트가 고르거나 좌표를 추정하지 않는다.

4. 사용자 답을 record로 저장한다.
   - visibility는 장면 판정 그대로 둔다.
   - 후보 identity는 다음과 같이 둔다.
     · air–액체 상면, 유체–유체 층 → interface
     · air–Foam 상면, Foam 내부, 기타 → non_interface
     · 판단 보류 → uncertain
   - 역할은 reply note에 한 줄로 남긴다.
     예: "role: idx16=foam_interior; idx21=air_liquid_top"
     역할 값: air_foam_top / air_liquid_top / foam_interior / liquid_liquid / other / uncertain

5. 프레임별로 한 줄만 반환한다.
   frame | 상면 보임(종류) | 상면 idx | 후보별 역할(idx=역할 …) | 비고
   영상·이미지·JSON 원본은 보내지 않는다. 원인 판정이나 수정 제안 없이 멈춘다.
   FIELD FAIL / O2 OPEN, review-006 pending, ⑧ NOT RUN 상태는 바뀌지 않는다.
```

## LBW-3 held-out witness check

**COMPLETE — reference record; do not re-run.** Saved ④ trace only, no run. [LBW-3](../50-diagnostics/s11/2026-10-20-layer-bottom-witness-3.md)
asks whether a raster witness for the bottom of a textured layer, taken as the
frame's first supported bottom, separates the reviewed Accum boundary from
Foam-interior anchors and wrong selections. sample4 passed as development data.
This trace has not been read by any witness definition and is the decisive
held-out check. Positives and negatives are fixed by `candidate_input_index` from
review-009 and the ATG-1 tables. The tool reads each record's saved
`foam_combined_evidence`, `effective_mask` and `glare_mask` PNGs. It recomputes the
stored whole-row texture features as a self-check, and writes nothing.

```text
S11 LBW-3 독립 확인. 기존 ④ bundle(trace=full)을 읽기만 해. 재실행, 튜닝, 새 bundle,
새 질문은 하지 마. 이 결과로 정의를 바꾸지도 않아.

1. 아래 ZIP을 새 폴더에 풀고 그 폴더에서 실행해.
   https://github.com/teeeeooo/oil_level_tracker/archive/87817ad37328dffc041f0b3c5b023897f9b66ec9.zip

   $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
   python -B -m tests.diagnostics.s11_layer_bottom_witness bundle --bundle "<④ bundle 폴더>" --glass Accum --definition lbw3 --pos "16136:10,26;16184:10,22,25;16232:10,23,25,26;16268:12,24" --neg "16136:25,12,2,20,3;16184:14,24,11,18,17;16232:11,16,24,18,1;16268:16,21"

2. 다음 줄만 출력 그대로 돌려줘. 값은 고치지 마.
   - 머리줄 1개(run_id … definition=lbw3 tol=…)
   - [F]로 시작하는 줄 전부(4줄)와 [S] 줄
   - [W] 줄 중 role이 pos인 줄 전부, role이 neg이면서 끝에 "| first"가 붙은 줄
   NOT_CAPTURED, NOT_FOUND, 오류 메시지가 있으면 그 줄도 그대로 적어줘.

3. 반환 후 멈춰. 원인 판정이나 수정 제안은 하지 마. 영상, 이미지, JSON, CSV 원본은 보내지 마.
```

## Accum texture-gate extraction

**COMPLETE — reference record; do not re-run.** Saved trace only, no run. It asked whether the reviewed
Accum layered-Foam boundary (`WS1-ACCUM-FOAM-LAYERED`, about 672–680 s) loses
anchor authority by the sample4 mechanism of
[AAT-1](../50-diagnostics/s11/2026-10-20-anchor-authority-trace.md#findings):
an ordered-lower candidate needs cross-representation support of at least 0.12,
and texture-conflicted peers (conflict ≥ 0.60) are excluded, so support stays 0.
Context is in the [texture-authority handoff](../60-evidence/s11/2026-10-20-texture-authority-handoff.md#decided-next-step-user-2026-10-20).
Same mechanism means the texture/authority direction is relevant in the field;
a different one stops sample4-only work on it.

### Source-based field coverage of the ④ trace

④ FULL+ON v2 ran commit `4c72ebb`. Between that commit and the tool commit, the
trace writer, phase identity, candidate authority and the cross-support function
are unchanged. The only resolver/evidence differences are OFF-by-default flags
and an RGB eligibility guard whose feature is absent in ④. Saved fields were
determined from the writer, not from the bundle.

| Needed value | In the ④ trace? | Path / limit |
|---|---|---|
| `material_texture_conflict`, `material_terminal_partition_support`, `raw_material_row_support` | Yes, for every Oil candidate in a captured record | top-level `candidates[].features` (raw frame input) |
| Phase identity and failed gates, `ordered_lower`, cross-representation support, authority tier/reason/failed gates, tracklet admission/failure, selection, reject stage | Yes, but only for the per-frame top-K resolver refs | `sequence.candidates[]`; null for top-K-pruned or hard-invalid candidates such as the R22 Y217 peer |
| Foam material row and seed age | **No** | Only eligible Foam-front rows are saved. Seed age ≤ 3 s is visible only through the absence of the `ordered_lower_recent_direct_foam` gate |
| Why support is 0: which peer was excluded and by which condition | **No** | Needs derived evidence (artifact signature, optics opposition, eligibility, representation family) that the trace does not store |
| Capture of every target frame | Not guaranteed | BASIC trace stores only marker frames (Foam, no selection, ambiguity and similar). The tool reports `NOT_CAPTURED` instead of substituting a neighbour |

Saved values alone cannot separate "excluded by texture" from "no independent
peer" or other exclusions. The read-only tool
`tests/diagnostics/s11_accum_texture_gate_extract.py` therefore reads the saved
records and applies the current source functions to the saved features. It does
not run the detector, resolver or pipeline and writes nothing. It recomputes
every stored support value with the resolver function itself (`recompute n/n`).
On any mismatch the per-peer attribution for that frame is invalid.

Pattern codes (mechanical, no physical judgement): `TEX0` = ordered-lower,
continuation-only, failing only the cross-representation gate, with at least
one peer excluded only by texture, and support ≥ 0.12 once those peers are kept
(`sup*`), which is the AAT-1 mechanism. `TEX_WEAK` = texture exclusion present
but `sup*` < 0.12. `NOPEER` = no other-family peer within tolerance.
`OTHER_EXCL` = peers excluded by other conditions. `GATE_OTHER` = direct
quality or Foam recency also fails.

Targets are 673, 675, 677, 678.5 and 679.0 s in the layered interval, plus 684 s
after Foam. 679.0 s is source frame 16280, whose human-reviewed Y213 is in the
[R22 findings](../50-diagnostics/s11/s11-r22-reviewed-interface-causal-findings.md#accum-authority-and-independent-support).
Table C counts all captured Accum frames in 671–681 s.

**Boundary Y is a human review, not an agent estimate.** It uses the existing
[O2 review procedure](s11-o2-local-shadow-evaluation.md#3-에이전트-질문--사용자-회신--기록재개)
on the same ④ bundle as a new **review-009** (review-001–008 are taken). Use
`prepare` → `link-bundle` → plain/idx-guide images → one question per frame →
`record`. Table B prints `candidate_input_index` as `idx`, the same key the
packet uses, so answers join without matching on Y. Review-006 (Accum 675/676/677
s, RGB packet) overlaps this interval but stays pending and untouched; review-009
does not answer or overwrite it. Several acceptable candidates and `uncertain`
are valid answers, as in review-004.

### Request text for the Windows agent

[Source ZIP](https://github.com/teeeeooo/oil_level_tracker/archive/1c21444addad7758fa3db1d426485c1c65d5cb0f.zip)
(commit `1c21444`).

```text
S11 Accum 텍스처 gate 확인 — 저장된 ④ trace 읽기 전용 추출이야. 재실행·튜닝·비교 실행은 하지 마.

목적: ④ FULL+ON v2 bundle의 Accum 층상 Foam 구간(약 672–680초)에서
실제 Oil/Foam 경계 후보가 "텍스처 충돌 peer 제외 → 표현 간 지지 0 →
ORDERED_LOWER 실패 → anchor 미승인"으로 막히는지 확인한다.

1. 위 ZIP을 새 폴더에 풀고, 그 폴더에서 기존 Windows Python으로 실행한다.
   bundle은 이동·수정하지 않고 경로만 넘긴다. 이 명령은 읽기만 한다.

   $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
   python -B -m tests.diagnostics.s11_accum_texture_gate_extract --bundle "<④ FULL+ON v2 bundle 폴더>" --glass Accum

   Glass 이름이 다르면 오류 메시지에 나온 실제 이름으로 --glass만 바꾼다.
   다른 시각·옵션·bundle로 넓히지 않는다.

2. 출력된 머리줄 2개(run_id/trace/records/tol, resolver)와 표 A, B, C를
   그대로 텍스트로 돌려준다. 값을 고치거나 반올림·재해석하지 않는다.
   표 B가 25행을 넘으면 각 시각의 pattern이 TEX0/TEX_WEAK/NOPEER/OTHER_EXCL/
   GATE_OTHER인 행과 * 표시(선택) 행만 남긴다.

3. 표 A의 recompute가 n/n이 아니면 해당 시각을 "재계산 불일치"로 표시만 하고
   원인 조사는 하지 않는다. NOT_CAPTURED / NO_SEQUENCE도 그대로 둔다.
   인접 프레임이나 다른 후보로 채우지 않는다.

4. 표 A에서 캡처된 목표 프레임만 새 review-009로 사람 검토를 한다.
   s11-o2-local-shadow-evaluation.md의 "3. 에이전트 질문 → 사용자 회신 → 기록·재개"
   절차를 그대로 쓴다: 같은 ④ bundle로 prepare(Accum glass_id, 표 A의 frame) →
   link-bundle → 질문 전 plain/idx-guide 이미지를 열어 경로를 알려줌 → 한 프레임씩 질문 →
   사용자 답을 record로 저장. selection의 recording_group/partition은 review-004와 같게 둔다.
   질문은 프레임당 하나: "아래쪽 Oil/Foam 경계가 보이나요? 보이면 그 경계에 있는 후보 idx는?"
   여러 idx 허용, 판단 보류(uncertain) 허용. 에이전트가 고르거나 좌표를 추정하지 않는다.
   review-006은 열거나 답하지 않는다. 679.0초(f16280)는 기존 검토값 Y213을 참고로 보여줘도 된다.
   반환은 프레임별 한 줄: frame | visibility | interface idx | non_interface idx(답한 경우) | 비고.

5. 영상·이미지·JSON·CSV·packet 원본은 보내지 않는다. 표, 검토 줄, 결론 한 줄만 반환하고 멈춘다.
   결론 한 줄에는 "표 C에서 TEX0가 몇 프레임" 같은 관찰만 쓰고, 원인 판정이나
   수정 제안은 하지 않는다. FIELD FAIL / O2 OPEN, review-006 pending,
   ⑧ NOT RUN 상태는 바뀌지 않는다.
```

Receipt goes to a new `50-diagnostics/s11/` record compared with AAT-1. The
returned tables are relayed Windows evidence, not local verification. The Work
Plan changes only if the direction changes.

### First return and boundary-row follow-up

**First return RECEIVED** and recorded in
[ATG-1](../50-diagnostics/s11/2026-10-20-accum-texture-gate.md). The bundle is ④,
and 102/102 stored support values were reproduced. Review-009 recorded the visible
boundary candidates. Table B's five-row cap omitted every reviewed candidate, so
the gate question is still open. The follow-up reads exactly those candidates
with `--rows` ([source ZIP](https://github.com/teeeeooo/oil_level_tracker/archive/125af541a1647673cf79e2c66cc28ca840ba3a8d.zip),
commit `125af54`). Review-009 is reused and not re-asked.

```text
S11 Accum 경계 후보 후속 추출. 기존 ④ bundle 읽기 전용이야.
재실행, 새 bundle, 튜닝, 새 질문은 하지 마. review-009는 다시 묻지 않고 그대로 써.

1. 아래 ZIP을 새 폴더에 풀고 그 폴더에서 실행해.
   https://github.com/teeeeooo/oil_level_tracker/archive/125af541a1647673cf79e2c66cc28ca840ba3a8d.zip

   $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
   python -B -m tests.diagnostics.s11_accum_texture_gate_extract --bundle "<④ bundle 폴더>" --glass Accum --rows "16136:10,26;16184:10,22,25;16232:10,23,25,26;16268:12,24;16280:11,20,25"

2. 출력된 머리줄과 표 D를 그대로 돌려줘. 값은 고치지 마.
   NOT_TOPK, NOT_FOUND_OR_AMBIG, NOT_CAPTURED도 그대로 둬.

3. 기록 확인 두 가지만 답해줘. 파일은 보내지 마.
   - review-009 labels.json에서 f16400(684초) case의 visibility 저장값
   - 처음 표 B의 673.0초 Y367 idx25 행 원문
     (전사된 숫자 열이 4개였어. 출력 원문의 해당 줄만 다시 적어줘.)

4. 반환 후 멈춰. 원인 판정이나 수정 제안은 하지 마.
```

## 721-second identity investigation

**수신 완료 / 추가 Windows 작업 없음.** ④ 저장 trace의 여섯 표본 위치에서
실제 관측 5개와 앵커 표시 행 3개가 확인됐고, 721초 선택 member의 승인 이유는
`corroborated_material_path`였다. 이후 `anchor_corridor` 확정과 IFO v2 허용을
통해 Y694가 출력됐다. 이번 확인은 이 경로를 특정했으며 오검출을 수정한 것은
아니다. [수신·소스 대조 기록](../50-diagnostics/s11/2026-10-15-initial-full-comparison.md#saved-trace-receipt--bounded-identity-intake-complete)을 따른다.

`semantic_sequence_available=False`는 미저장 키의 부재만으로 확정하지 않는다.
코드는 전체 시퀀스의 semantic anchor 집합으로 계산한다. 성공한 분기와 제공된
corridor/motion 값으로부터의 조건부 추론으로 기록하며 추가 추출은 요청하지
않는다. 비유면 판정은 유지하고, 아지랑이라는 광학적 원인만 미확인으로 남긴다.
FULL preflight CONDITION FAILED / ⑧ NOT RUN, O2 OPEN / FIELD FAIL을 유지한다.

**아래는 완료된 추출 절차의 참조 기록이며 다시 실행하지 않는다.**

이미 확인된 값은 재사용한다: BASE `oil-tracklet:000474:0424`, ④의
f17287@721.012s 선택 `material_path`, row `oil-row:000482:002`, Y694;
확정 profile `anchor_corridor`, 창 offset 480–485(약 720–722.5초).
723초의 material veto와 771초의 identity 보호, 기존 8행 번들 비교 및
전체 트랙릿 궤적은 다시 추출하지 않는다. 아지랑이라는 원인은 미확인이다.

1. **확정 창만, 표본당 한 행으로 정리한다.** ④ BASE의 분석 표본 offset
   480–485를 실제 source frame/time과 대응하고 해당 tracklet의 row만 읽는다.
   각 행에는 frame/time, row ID, 앵커로 표시된 member의
   `source/Y/authority_reason`, `initial_authority/post_track_authority/authority`,
   최종 선택 여부를 적는다. 같은 row의 여러 source를 독립 anchor 프레임으로
   중복 계산하지 않는다. 저장 전후 단계가 다르면 차이를 그대로 남기고,
   최종 authority를 과거 confirmation 입력이라고 단정하지 않는다.
2. **721초 실제 선택 member만 작은 `키 / 경로 / 값` 표로 보충한다.**
   `record.sequence.candidates[]`에서 source/Y/row/tracklet을 모두 맞춘다.
   다음 저장 항목을 확인한다: `authority_reason`, `phase_identity`,
   `cross_representation_support`, `semantic_corridor_support`,
   `track_opposition`, `effective_track_opposition`, `tracklet_material_conflict`,
   `identity_contradiction`. 이어 `oil_candidate_authority.py`의 해당 reason
   분기에서 쓰는 원시 features/penalties 중 핵심 항목만 최대 10개 덧붙인다.
   원시 후보 대응이 유일하지 않으면 UNAVAILABLE로 남긴다. 저장되지 않은
   점수를 새로 만들거나 다른 Y/유사 후보로 대신 채우지 않는다.
3. `anchor_corridor`는 충분한 compatible 관측과 앵커 수로 확정되는 경로다.
   motion 0.36/coverage 0.44가 0.50보다 작다는 이유만으로 구현 오류로
   판정하지 않는다. 확인할 것은 **이미 비유면으로 판정된 경계가 어떤
   authority reason과 입력 때문에 앵커가 되었는지**다. 단조성, source 이름,
   국소 움직임만으로 아지랑이나 실제 계면을 분류하지 않는다.
4. `calibrated_artifact_match`가 없다는 것은 공간 Artifact 기능 OFF의 증거가
   아니다. `sequence.candidates`는 점수 정렬되어 있으므로 witness의
   `candidate_offset`을 그 배열 인덱스로 사용하지 않는다. null/빈 배열/미저장을
   구분하고 없는 필드는 추정하지 않는다. 723초 차이는 기존 회신의 material
   veto로 설명 가능한 범위까지만 비교한다.
5. **두 작은 표와 결론 한 문단을 반환하고 멈춘다.** 앵커 승인 분기와 아직
   확인되지 않은 인과를 분리한다. 전체 JSON/601행 CSV/116개 후보/네 bundle
   비교를 다시 반환하지 않는다. 재실행·튜닝·추가 자동 조사로 확장하지 않는다.
   review-004/005의 복수 허용·대략적 일치와 review-006 pending은 유지한다.

전달용 짧은 프롬프트 — 완료 상태 공유, 새 작업 요청 아님:

```text
docs/40-operations/s11-current-windows-field-qualification.md의
“721-second identity investigation”은 회신 수신으로 완료됐어.
corroborated_material_path → anchor_corridor → Y694 출력 경로를 기록했어.
semantic_sequence_available=False는 직접 저장값이 아니라 코드상 조건부 추론이야.
④ bundle과 기존 review 자료를 보존해줘. 추가 추출·재실행·튜닝·새 판정은 없어.
FULL은 사전 조건 확인만 완료됐고 ⑧ 본검증은 미실행이야. 지금은 실행하지 않아.
상단 관측·판정 조건을 정리한 뒤 FULL 전환·유지 Windows 검증이 필요해.
다음 수정안과 검증 범위를 정리한 뒤 필요한 작업을 전달할게.
```

## Top-exit FULL comparison

**v1 이력 — [⑨ top-exit v2 비교](#top-exit-v2-comparison)로 대체됨. 아래 ⑧
절차는 실행하지 않는다.**

**FULL 전환 검증 자체는 미완료다.** 아래의 완료 상태는 사전 조건 확인에만
해당한다. 상단 관측·판정 조건을 정리한 뒤 실제 FULL 전환·유지와 기존 관측
보존의 Windows 비교가 남는다. 현재 추가 실행 요청은 없다.

**preflight 수신 완료: CONDITION FAILED / ⑧ NOT RUN.** BASE의 허용 끝점
Y220.870보다 effective mask 상단 Y243이 아래에 있어 조건에 도달할 수 없다.
마지막 선택 Y352는 mask 상단보다도 109px 아래다. 이는 사용자 정답 Y나 실제
마지막 계면 가시 시각을 뜻하지 않는다. [수신 기록](../60-evidence/s11/2026-10-16-top-exit-full.md#windows-geometry-preflight-received--condition-failed)을 따른다.
아래는 이전 조건부 절차이며 **현재 ⑧ 실행을 요청하지 않는다**. FULL은 물리적
상태의 의미를 유지하며, mask 경계로 바꾸거나 margin을 줄이지 않는다.

**이전 조건부 순서: ④ v2 기반 FULL 전환 검증 → 그다음 721초 부근 비유면 조사.**
새 후보 ⑧은 `initial_full_observation=True, top_exit_full=True`이며
cost-first/RGB/Local XY는 OFF다. 디텍터·resolver에
`+initial-full-observation-v2+top-exit-full-v1`이 붙는다. 같은 조건의 기존
④ bundle을 재사용한다. 이 비교는 아직 채택된 기본 동작이 아니다.

**전체 실행 전, 기존 자료로 상단 조건부터 확인한다.** 로컬 두 Recipe에서는
margin이 설정 ellipse 상단을 제외해 새 조건의 끝점에 도달할 수 없었다.
Windows에서도 같다고 단정하지 않고, 기존 ④ Recipe와 674–675초 직전 자료로
BASE의 아래 값만 확인한다. 디텍터 재실행이나 새 전체 CSV 분석은 필요 없다.

- `geometry_top_y = ellipse.center_y - ellipse.radius_y`와
  `endpoint_tolerance_px = max(1, 2 * ellipse.radius_y * 0.012)`.
- 기존 `build_mask_bundle`의 effective mask에서 가장 작은 **source Y**.
  crop 원점을 더하고, mask 밖의 후보를 도달 가능한 실제 관측으로 세지 않는다.
- 상단 소실 직전의 마지막 허용 계면 관측 시각/Y/owner와 원본의 가시 상단.
  기존 리뷰가 없으면 LVLM 관찰과 사용자 판정을 구분하고 위치 불확실성을 남긴다.

effective mask의 상단이 `geometry_top_y + endpoint_tolerance_px`보다 아래이거나,
설정 상단과 실제 가시 상단의 대응을 확인할 수 없으면 **여기서 멈추고 위 값과
사유만 반환한다. ⑧ 전체 실행은 하지 않는다.** 이를 해결하려고 margin/ROI/임계값을
변경하거나 mask 끝을 물리적 FULL 경계로 간주하지 않는다. 이 경우 다음 수정은
상단 입력의 의미를 먼저 정한 뒤 진행한다. 조건이 도달 가능하고 물리적 대응이
확인되면 아래의 동일 조건 비교를 한 번 수행한다.

1. Work Plan이 지정한 게시 소스에서 기존 headless 실행기/AnalysisPipeline을
   재사용한다. 디텍터는 아래와 같이 생성한다. GUI를 사용하면 같은 ZIP 루트에서
   `python -m oil_tracker --initial-full-observation --oil-top-exit-full`로 실행한다.
   창 제목에는 `상단 이탈 FULL 비교`가 표시된다. GUI를 여는 것만으로 분석이
   시작되지는 않는다. 실제 수행한 경로를 기록한다.

   ```python
   detector = OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True)
   ```

2. 기존 영상·Recipe·ROI/margin/exclusion/Artifact·영점·스케일을 유지한다.
   480–780초, 2fps, FULL debug, compressor_start=485초,
   BASE FULL / Accum EMPTY 초기 확인값을 그대로 사용한다. 새 출력은
   `sample/output/`의 관리되는 실행 폴더에 둔다. ④ 조건이 맞으면 다시 돌리지 않는다.
3. BASE/Accum 각 601개의 `(glass_id, frame_index)`를 일대일 대응하고,
   기존 정규 구간표로 Oil 숫자/Y·FULL/UNKNOWN·Foam 좌표/validity/episode 변화를
   정리한다. 이 구현은 **기존 숫자 Oil을 모두 보존**해야 한다. 숫자 값/선택이
   바뀌면 먼저 계약 위반으로 보고하고 임의 튜닝하지 않는다. 최초 FULL과 연속
   유지 범위, FULL 종료 사유를 보고한다. 시간 정답으로 CSV 상태를 덮어쓰지 않는다.
4. 674–675초 전환과 직전 마지막 관측을 중심으로 다음을 짧게 확인한다.
   - `sequence.state.sequence_material_phase_diagnostics.top_exit_full`의
     `reason`, `predicates`, `witness`, `geometry_top_y`, `endpoint_tolerance_px`.
     source frame과 resolver offset을 구분한다. FULL이 없으면 마지막 상단 접근
     후보의 실제 실패 조건만 보고한다. 전체 빈 프레임/JSON을 다시 분석하지 않는다.
   - 원본에서 같은 실제 상승 계면이 상단으로 사라졌는지, **설정 ellipse 상단이
     물리적 Glass의 가시 상단과 맞는지** 확인한다. margin/effective-mask 끝이나
     crop 밖 소실만으로 FULL 성공을 인정하지 않는다. top 불일치/가림이 있으면
     그 사실을 보고하고 ROI 또는 임계값을 바꾸지 않는다.
   - FULL 행은 Oil 좌표가 비어 있고 `OIL_TOP_EXIT_FULL`이 있으며, raw
     `record.state.oil_no_interface_full_likelihood`는 원래 값 그대로다.
     `sequence_state_image_evidence=0`을 새 이미지 FULL 판정으로 설명하지 않는다.
     witness의 마지막 선택 Y·frame/owner가 실제 직전 관측과 맞는지 확인한다.
5. review-004/005의 복수 허용·대략적 일치와 review-007/008은 재사용한다.
   review-006은 pending으로 보존한다. 이번 top-exit 장면에서만 새로운 사용자
   판단이 필요하면 기존 review 폴더의 packet/plain/guide 방식으로 최소한만 질문한다.
   LVLM 관찰을 사용자 확정으로 저장하지 않는다. 정확한 전환 프레임이 불확실하면
   674–675초 범위를 유지한다.
6. 721초 비유면과 723/771초 보호 지점은 **최종 출력 변화 유무만** 함께 남긴다.
   원인 조사·억제 수정은 이번 FULL 결과를 받은 뒤 별도 단계다. 현재 숫자를
   FULL로 덮거나 새 후보를 추가해 오검출이 해결됐다고 처리하지 않는다.
   FULL 성공/미해결, 기존 관측 보존, 실제 top 대응, 최종 Foam 영향을 반환하고
   멈춘다. O2 OPEN / FIELD FAIL과 기본 OFF를 유지한다.

이전 조건부 프롬프트 — 현재 실행하지 않음:

```text
④ FULL+ON v2 bundle: <기준 번들 경로>
최신 소스 ZIP: <소스 경로>
기존 영상·Recipe·review 폴더: <경로>

docs/40-operations/s11-current-windows-field-qualification.md의
“Top-exit FULL comparison”의 실행 전 상단 조건을 기존 ④ 자료로 먼저 확인해줘.
설정 상단·effective mask 상단·마지막 실제 관측이 맞지 않으면 전체 재실행 없이
문서에 적힌 값과 사유만 알려줘. ROI/margin/임계값은 바꾸지 마.
조건이 맞을 때만 ⑧을 실행·비교해줘.
initial-full-observation과 top-exit-full만 ON, cost-first/RGB/Local XY는 OFF야.
같은 조건의 ④는 재사용하고, 기존 headless 실행기 또는 문서의 GUI 실행을 사용해줘.
기존 숫자 Oil이 유지되는지와 674–675초 상단 소실→FULL 전환·유지 여부를 확인해줘.
721초 부근은 변화 유무만 기록해줘. 원인 조사는 다음 단계야.
기존 사용자 판정은 재사용하고, 튜닝·추가 재실행 없이 결과를 알려줘.
```

## 1. Preconditions and identity

Before running private media:

1. Confirm Windows qualification is authorized and identify the candidate from `docs/00-project/work-plan.md`.
2. Record the exact pushed source SHA being qualified. Do not qualify an unpushed or subsequently mutated head as though it were the reviewed candidate.
3. Read the candidate's current architecture and validation/work specification linked by the Work Plan. Record expected detector/resolver/schema identities from those owners rather than from historical checklists.
4. Read `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` and `docs/30-validation/windows_sample1_heating_coldstart.reviewed-truth.json` completely enough to enumerate all nine `WS1-*` segments.
5. Run the `windows-qualification` and `s11-detector-change` Skill contracts. Resolve any required governance/history owner before interpreting results.

If source, candidate identity, or reviewed-truth authority is ambiguous, stop before execution rather than blending revision evidence.

An isolated Windows machine may use a GitHub source ZIP extracted into a folder;
Git installation, cloning and network access on that machine are not prerequisites.
Bind the archive to its published commit and verify extracted source-file hashes.
An existing completed bundle may be reused when its actual producing source,
video, Recipe and session conditions are established. Review an uncertain older
bundle as historical output first; do not silently label it the designated baseline
or require a rerun solely because `.git` or complete debug trace is absent.
The [retired overlay comparison](s11-overlay-support-windows-comparison.md)
records the ZIP/manual-GUI/bundle workflow, not a current candidate request.
A GUI launch alone does not start an analysis; a manual run requires the
operator to complete setup and start analysis. Use the Work Plan for current
candidate identity, not the retired comparison's commit or branch.

### October 15 first initial-FULL comparison

**Completed historical procedure.** All three subsequent candidate comparisons
and their bounded accounting are also complete. Do not replay this handoff.

This is the first exploratory OFF/ON comparison named by the Work Plan, before
cost-first assignment, candidate RGB or Local XY. False positives are permitted
for inspection and must be reported. Formal field acceptance still follows the
nine-segment procedure below. The [comparison record](../50-diagnostics/s11/2026-10-15-initial-full-comparison.md)
separates local implementation/verification from subsequent qualitative Windows feedback.

Windows 담당자는 다음 순서로 진행한다.

1. Work Plan에 지정된 커밋의 소스 ZIP을 별도 폴더에 풀고 기존 Windows Python
   환경을 사용한다. 원본 영상과 bundle은 Windows에 보관한다. ZIP 커밋/URL,
   실제 import 경로, Python/OpenCV/NumPy 버전을 기록한다.
2. 원본을 보며 **BASE와 Accum 각각 유체가 움직일 수 있는 용기 내부 전체**로
   ROI를 확인한다. 시작·하강·재충전·종료 장면을 확인하고 외부 rim/컵 테두리를
   제외한다. 순간적인 액면 높이에 맞춰 ROI를 줄이지 않는다. Recipe를 한 번
   저장한 뒤 OFF/ON에 동일하게 사용한다. Mac sample4 좌표를 옮겨 쓰지 않는다.
3. 기준 비교는 기존 480–780초 창, 같은 FPS·영점·스케일·초기 상태·판정 설정을
   사용한다. BASE는 FULL, Accum은 EMPTY 초기 확인을 유지한다. ROI가 바뀌면
   이전 bundle을 같은 조건의 OFF 결과로 간주하지 말고 OFF부터 실행한다.
   기존 bundle은 생성 소스와 입력/설정이 같은 경우 재사용할 수 있다.
4. 아래 OFF 실행으로 GUI에서 직접 분석을 시작하고 완료 bundle을 보존한다.
   GUI를 닫은 뒤 ON으로 다시 열어 같은 조건으로 분석한다. 결과 경로/이름을
   구분하고, 실행 중 설정을 조정하지 않는다. 두 실행의 debug 수준도 같게
   두며 기본 BASIC이면 충분하다. 원인 추적에 필요한 추가 상세 실행은 결과를
   읽은 다음 결정한다.

ZIP 루트에서 PowerShell로 실행한다. `python`은 기존 Windows 환경의 Python을
가리켜야 한다. `PYTHONPATH`는 다른 ZIP의 editable 설치가 선택되는 것을 막는다.

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
python -c "import oil_tracker; print(oil_tracker.__file__)"
python -m oil_tracker
```

OFF GUI를 닫은 후 같은 터미널에서 실행한다.

```powershell
python -m oil_tracker --initial-full-observation
```

ON 창 제목에는 `초기 FULL 관측 비교`, detector/resolver 버전에는
`+initial-full-observation-v1`이 붙어야 한다. 이 옵션은 Recipe 초기 상태를
자동 변경하지 않는다. 원시 후보·association·기존 drain/refill 규칙을 유지하면서
초기 FULL에서 허용되는 현재 계면 후보만 방향 미확정으로 출력한다. 새 출력의
CSV flag는 `OIL_DIRECTION_UNCONFIRMED`이고 보고서는 이를 방향 요약/하강 시작
판정에 사용하지 않는다고 설명한다. 후보가 없거나 다른 hard gate에 막힌 지점,
이미 drain/refill 상태로 전환한 뒤의 손실은 이 옵션의 해결 범위가 아니다.

먼저 BASE의 약 550–652초 하강과 652–674초 회복, 674–675초 FULL 전환이 원본과 대조해
얼마나 드러나는지, 앞뒤 FULL 구간에 잘못된 선이 생기는지 확인한다. 보고서만
읽은 판단과 원본 대조 결과를 구분한다. Accum과 Foam 변화도 함께 기록하되
정확한 Y truth가 없는 곳은 위치 정확도를 단정하지 않는다. 아래 9개 구간을
모두 열거하고 아직 보지 않은 곳은 `NOT_EVALUATED`로 남긴다.

Mac에 전달할 최소 결과는 **소스/ROI/설정 동일 여부, 구간별 OFF→ON 관측 변화,
복원된 움직임, 오검출과 긴 공백, 보고서 해석 가능 여부, 실제 runtime**의 텍스트
요약이다. 비공개 영상·이미지·bundle을 Mac으로 전송할 필요는 없다. 이 결과를
받아 첫 수정의 효과와 남은 실패를 판단한 뒤 승인된 세 후보 비교 순서를 적용한다.

### October 15 completed-bundle inspection

FULL+ON의 BASE 출력은 확인됐지만, 첫 하강 등장 누락과 중간 하강·상승의 추가
누락이 남았다. 사용자가 정정한 실제 상단 이탈 후 상태는 **기존/ON 모두
`UNKNOWN_REVIEW`**다. 원하는 동작은 실제 상승 계면을 상단까지 추적한 뒤
계면이 밖으로 사라지면 좌표 없는 `FULL_NO_INTERFACE`로 전환하는 것이다.
이 단계에서는 Windows에 있는 **완료 bundle을 읽고 텍스트 결과를 전달**한다.
사용자 요청에 따라 이번 저장 결과 점검에서는 해시 비교와 실행환경 검증을
생략한다. 이 생략을 이유로 재실행이나 추가 환경 확인을 요구하지 않는다.

사용자는 **① 초기 FULL+OFF, ② 초기 UNKNOWN+OFF, ③ 초기 FULL+ON**의 세 bundle을
보유하고 있다고 확인했다. 기존 ②↔③ 점검을 다음 세 비교로 보완한다.

| 비교 | 점검 목적 |
|---|---|
| **①↔③ — 주 비교** | 초기 FULL을 고정하고 ON으로 복원된 관측과 추가 손실 확인 |
| ①↔② | OFF를 고정하고 초기 상태 FULL/UNKNOWN에 따른 추적 차이 확인 |
| ②↔③ | UNKNOWN+OFF에서 보였지만 FULL+ON에서 놓친 실제 유면 구간과 최초 차단 단계 확인 |

①↔③에서 옵션 외 소스·설정이 같아야 ON의 효과를 분리할 수 있고, ①↔②에서도
초기 상태 외 조건이 같아야 한다. ②↔③은 초기 상태와 옵션을 함께 바꾸므로
그 차이를 ON만의 회귀로 해석하지 않는다. 세 비교 모두 기존 결과를 재사용한다.

1. 세 결과에 저장된 ROI, 분석 창, FPS, 초기 상태와 설정 차이를 기록한다.
   사용자 번호 ①②③을 결과 표에도 유지한다. ON은
   `analysis_manifest.json`의 Glass별 `sequence_resolver` 버전 접미사
   `+initial-full-observation-v1`로 확인한다. HTML 상단 버전만으로 판정하지 않는다.
2. `tracking_data.csv`를 Glass와 실제 frame/time으로 맞춘다. 첫 하강 등장,
   중간 하강·상승에서 추가로 누락되는 첫 지점, 상승의 마지막 실제 관측과
   직후 UNKNOWN 구간을 찾는다. 각 지점과 앞뒤 인접 표본에 대해 세 결과의
   `raw_oil_air_level_y`, `fill_state`, `oil_is_valid`/`is_valid`, confidence,
   flags를 작은 표로 남긴다. 숫자 관측 없음과 숫자는 있지만 유효하지 않음을
   구분한다. CSV 차이 자체를 실제 유면의 정답으로 삼지 않는다.
3. 해당 frame/time이 저장된 `debug/debug_trace.jsonl`에 있으면 원시 `state`와
   완료 결과 `sequence.state`를 함께 읽는다. 실제 저장된
   `sequence_decision_witness`의 phase/reason/allowed IDs, row admission/
   publishability, selected candidate와
   `sequence_material_phase_diagnostics.initial_full_observation`의 실패 조건을
   옮긴다. 원시 `oil_no_interface_full_likelihood`도 함께 기록한다. 상단 이탈은
   **재충전 종료 자체가 안 됨 / 종료됐지만 FULL 상태 후보가 없음 / 상태 후보가
   있어도 허용 집합이나 선택 단계에서 차단됨**을 구분하고, 저장 증거가 없는
   분기는 `UNAVAILABLE`로 남긴다. BASIC trace에 해당 행이 없는 것은 원시 후보가
   없었다는 뜻이 아니다. 가까운 trace 행을 같은 프레임의 결정으로 대체하지 않는다.
4. 아래의 9개 정답 구간 표에 CSV 관측 범위·Oil/Foam 수·공백과 실제로 확인한
   판정만 기록한다. 아직 시각 검토하지 않은 부분은 `NOT_EVALUATED`로 남기고,
   끝에는 처음 확인 가능한 손실 단계와 부족한 증거를 적는다. 원본·이미지·bundle은
   Windows에 유지하며, 이 점검만을 위해 영상을 다시 분석하거나 옵션을 바꾸지 않는다.

새 스크립트나 별도 검출 경로는 필요하지 않다. 기존 CSV/JSONL과 저장된 결정
기록을 사용한다. 점검 결과로 다음 수정 범위를 정한 뒤 추가 실행 필요성을
판단한다. 대용량 점검 출력을 만드는 경우 기존 [관리 출력 규칙](experiment-artifact-lifecycle.md)을
따라 `sample/output/` 안에 보관한다.

### October 15 audit reconciliation

전달된 첫 점검문은 BASE의 774초 숫자 관측을 실제 상단 이탈로 해석했지만,
정정된 정답에서는 BASE가 674–675초 사이 FULL에 도달한 뒤 780초까지 계면이 없다.
또 source Y는 아래로 증가하므로 `dir=+1`을 상승으로 해석할 수 없다.
[수신 기록의 정정 사항](../50-diagnostics/s11/2026-10-15-initial-full-comparison.md#windows-three-bundle-audit-intake--reconciliation-required)을
읽고 기존 세 bundle에서 다음 내용만 다시 추출한다. 새 분석·해시 비교·환경
검증은 하지 않는다.

1. **548.5–550초:** ②의 Y363 출력과 ③의 Y367 출력 사이에 ③이 처음 허용되는
   시점과 앞선 누락 조건을 확인한다. 550초 한 점이 있다는 사실만으로 첫 등장
   누락 전체가 해결됐다고 판정하지 않는다.
2. **약 550–652초 하강 구간:** ②에 숫자 Oil이 있고 ③에는 없는 첫 지점과
   바로 앞뒤 표본을 찾는다. 실제 후보와 실패 조건을 기록하고, ②의 출력이라는
   이유만으로 물리적으로 옳은 유면이라고 확정하지 않는다.
3. **662–664초의 기존 표본:** 재충전 도중의 CSV와 저장 trace를 비교한 기록이다.
   상단 이탈은 674–675초이며, 기존 표본이나 774초의 마지막 숫자 출력으로
   대체하지 않는다. 후보 Y·상태·허용 ID·선택·초기 FULL 관측 조건을 함께 읽는다.

원본 JSONL 한 행을 `record`라고 할 때 필드 위치는 다음과 같다.

| 내용 | 실제 저장 경로 |
|---|---|
| 원시 FULL 가능도 | `record.state.oil_no_interface_full_likelihood` |
| 최종 상태/좌표 | `record.sequence.fill_state`, `record.sequence.positions.raw_oil_y` |
| 최종 결정 | `record.sequence.state.sequence_decision_witness` |
| motion/허용 집합 진단 객체 (`diag`) | `record.sequence.state.sequence_material_phase_diagnostics` |
| release / recovery / established fill | `diag.release_stage`, `diag.release_evaluated`, `diag.release_evaluations`, `diag.recovery_qualifying_tracklet_ids`, `diag.recovery_selected_tracklet_id`, `diag.recovery_ambiguous`, `diag.established_fill_present` 등 |
| ON 관측 조건 | `diag.initial_full_observation`의 `motion_phase`, `motion_reason`, `blocked_by_current_state`, `evaluations`, `qualifying_tracklet_ids` |

release 계열은 `initial_full_observation`의 **상위 객체**에 있다. 원시 가능도는
`sequence.state`가 아니라 원시 `state`에 있다. BASIC/FULL은 저장 프레임·이미지가
다를 수 있지만, 저장된 행의 메타데이터/sequence 직렬화에는 별도 필드 생략 분기가
없다. 올바른 경로에도 값이 없을 때만 해당 경로와 함께 `UNAVAILABLE`로 남긴다.

`selected_authority_tier=HARD_INVALID`는 선택 후보가 없을 때의 기본값이기도 하며,
모든 원시 후보가 hard-invalid라는 증거가 아니다. recovery의 일부 `passed=true`도
최종 release 성공과 다르므로 qualifying/selected ID와 최종 phase reason을 함께
기록한다. `observed_interface`는 현재 프레임의 관측 허용 결과이며, 그 전후의
motion runtime은 계속 초기 `filled_barrier`일 수 있다.

결과는 세 구간의 작은 표와 최초 확인 가능한 차단 조건으로 요약한다. 기존 정답과
반대인 675초 이후 숫자 출력은 실제 상승 복원으로 집계하지 않는다.
674–675초 전환 표본은 별도 판정하며, 663.6초를 FULL 경계로 사용하지 않는다. 첫 점검의
전체 observed 0/0.514/0.308과 회고적 ACCEPTED 홀드는 물리적 정답률이 아니다.

### Remaining three-record extraction

**완료.** 표 A/C와 별도 false-key 답변으로 필요한 세 행을 확보했다.
표 B의 누락 열은 원문 false-key 목록으로 바로잡았다. f13271은
`anchor_eligible, interface_identity`, f15884는 `anchor_eligible`, f15908은
`current_confirmed_owner, anchor_eligible`에서 실패한다. 세 raw outcome은
boundary/ambiguous이므로 FULL likelihood 0은 기본값이다. 상세 근거는
[진단 기록](../50-diagnostics/s11/2026-10-15-initial-full-comparison.md#three-record-predicate-intake)에
보존했다. 전체 JSON·후보 표·동일 세 행을 다시 요청하지 않는다.

### October 15 v2 Windows comparison

로컬 검증과 게시를 마친 v2 소스는 Work Plan의 현재 ZIP 링크를 사용한다.
이번에는 **기존 ③ FULL+ON v1과 새 ④ FULL+ON v2**를 비교한다.
① FULL+OFF와 ② UNKNOWN+OFF는 보존하고, ②는 누락 위치를 찾는 참고로만 쓴다.
추가 해시 비교·환경 감사나 기존 세 실행의 재분석은 요청하지 않는다.

1. 새 소스 폴더에서 기존 Windows Python으로 아래 GUI를 실행한다. 창 제목은
   `초기 FULL 관측 비교`, 실행 결과의 resolver 접미사는
   `+initial-full-observation-v2`다. 옵션 없이 실행하면 계속 OFF다.
2. 기존과 같은 영상·Recipe·ROI·480–780초·2 fps를 사용하고, BASE 초기 FULL과
   Accum 초기 EMPTY를 유지한다. GUI에서 직접 분석을 시작하고 새 bundle에 저장한다.
   BASIC trace면 이번 수치 비교에 충분하다. 원본 영상으로 위치/움직임을 대조한다.
3. 기존 ③과 새 ④의 첫 등장, 553.5/662.5/663.5초 출력, 실제 652–674초 재충전
   궤적을 비교한다. 숫자가 늘어난 것과 실제 유면이 복원된 것을 구분한다.
   675–780초의 최종 숫자 출력은 FULL 구간의 오검출로 별도 집계한다.
   674–675초는 FULL 전환 창이며 정확한 전환 프레임은 미확인이다.
   774초를 상단 이탈로 해석하지 않으며 source Y 감소가 상승이다.
4. 결과는 짧은 표로 전달한다: 구간별 유효한 복원/오검출/남은 공백,
   실제 상단에 닿는 마지막 계면의 시각과 위치, Accum/Foam 변화.
   새로운 실패가 나타날 때만 해당 판정의 false predicate 키를 덧붙인다.
   전체 JSON이나 66행 후보 표를 반복 전송할 필요는 없다.

721.01초에 대한 후속 표는 대상이 BASE이며 네 bundle 모두 같은
`oil-tracklet:000474:0424` 후보를 가진다고 보고한다. 후보 범위는 약
717–750.5초/Y675–748, 116회이며 여러 source의 같은 프레임 후보를 포함한다.
최종 출력의 첫/마지막 시각이나 116개 유효 관측으로 해석하지 않는다.
아래 [721초 후보/최종 출력 확인](#721-second-candidate-and-output-check)에
후속 최종 출력 수신 결과를 기록했다. 기존 전체 트랙릿 비교나 대상 Glass
확인을 반복하지 않는다.

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
python -m oil_tracker --initial-full-observation
```

v2는 이미 승인된 현재 관측에 매번 새 앵커를 요구하던 조건을 수정한다.
방향 라벨은 계속 `PARTIAL_VISIBLE + OIL_DIRECTION_UNCONFIRMED`다.
**상단 소실 → FULL 전이는 이번 변경에 포함되지 않는다.** 이 결과에서 실제
재충전 owner의 연속성을 review로 확인한다. 이후 합의한
[세 후보 개별 비교](#three-candidate-windows-comparisons)를 먼저 수행하고,
그 결과에 근거해 FULL 전이를 별도로 구현한다. 중간 소실을 FULL로 바꾸거나
정답 시각을 코드에 넣어서는 안 된다. 정식 FIELD PASS는 여전히
아래의 전체 9개 구간과 현재 acceptance owner가 판단한다.

### V2 final output reconciliation

**수신 완료.** BASE 최종 CSV는 ③ 185/601행 → ④ 303/601행 숫자 Oil,
첫 출력 550.01→548.51초, FULL_NO_INTERFACE는 모두 0행이다.
f13271/f15884/f15908도 v1의 빈 값에서 v2의 sequence/CSV Y364/409/418로
복원됐다. 관측 허용 수정이 최종 출력에 도달했으므로 이전의 “숫자 출력 변화
없음” 결론은 폐기한다. 집계와 여섯 기준 행을 다시 추출할 필요는 없다.

+118은 순증가이며, 실제 유면을 118행 더 맞췄다는 뜻은 아니다. 298개 빈 행도
FULL 구간을 포함하므로 전부 누락으로 세지 않는다. 검토된 물리 구간별 결과와
실제 재충전 위치 대응은 아래 후속 절차로 구분한다. 상세 수신값은
[진단 기록](../50-diagnostics/s11/2026-10-15-initial-full-comparison.md#final-base-csv-reconciliation-received)에 둔다.

### 721-second candidate and output check

**수신 완료.** 721.012초 BASE는 ①/③이 빈 값, ②/④가 최종 CSV Y694를
출력한다. 723.014초에는 ②만 Y707을 출력하고 ①/③/④는 빈 값이다.
따라서 후보는 공통이지만, v2는 721초에 v1이 차단하던 비유면 출력을 허용했다.
723초 재질 veto는 유지한다. 8행 비교나 전체 트랙릿 궤적을 다시 요청하지 않는다.

확정 정보는 ④의 720초 후보에서 `anchor_corridor`로 수신했다.
`confirmation_start/end_frame=480/485`는 분석 표본 순번이므로 2fps에서
약 2.5초 창이다. 과거 확정 창의 +1과 최근 창의 -1을 연속 시점의 물리적
방향 반전으로 읽지 않는다. `phase_admitted`/`publishable`은 최종 phase 제한
이전 후보 목록의 표시이며, True여도 최종 선택은 보장되지 않는다. FULL 구간의
720/771초 빈 출력을 새 결함으로 간주해 차단을 해제하지 않는다.

### Refill owner and false-output follow-up

**CLOSED — 결과 수신 완료.** [정정 집계와 review-004](../50-diagnostics/s11/2026-10-15-initial-full-comparison.md#corrected-segment-counts-and-review-004-closeout)를
재사용한다. 아래 추출·검토 단계와 이전 전달문은 수행 이력으로 남기며 다시
요청하지 않는다. 사용자 설명에 따라 여섯 프레임의 후보 선택은 애매한 계면에서의
허용 가능한 대안/선호 판정이다. 유일한 정밀 정답이나 두 건의 확정 오검출로
확대하지 않는다. 여러 후보와 불확실성을 함께 보존하고, 선택을 강요하지 않는다.
f15776@657.991초는 REFILL이며 반환문의 DRAIN 표기만 정정한다.
다음 Windows 실행은 1순위 cost-first 옵션의 로컬 준비가 끝난 뒤 별도 전달한다.

**수신 완료:** BASE 601개의 고유 키가 1:1 대응하고 timestamp 차이는 0건이다.
전체 185→303, 새 출력 119−소실 1=118이 일치한다. OUTSIDE는
f11508@479.9795초, 소실 1행은 f15776@657.9907초(v1 Y437→v2 빈 칸)다.
f15896의 IFO는 `evaluations=[]`(0행), `blocked_by_current_state=False`,
`qualifying_tracklet_ids=[]`이며 “전부 통과”가 아니다. 기존 여섯 행과 721초
선택 객체/CSV도 확인 완료다. 이 값들을 다시 추출하거나 질문하지 않는다.

**사용자 정답 정정:** BASE는 550–652초 하강, 652–674초 회복,
674–675초 사이 FULL 도달이다. [정답 소유 문서](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#base-timeline-correction--2026-10-15)와
JSON을 갱신했다. 이전 경계의 중복 없는 표는 산술상 맞지만 물리 구간별
평가에는 더 이상 사용하지 않는다. 663.6초 이후 출력을 모두 오검출로 보는
해석도 철회한다. 이번 요청은 **저장 CSV의 구간 재배정 → 필요한 이미지/idx
review**까지만이며, 세 후보 실행은 로컬 준비·검증 후 별도 전달한다.

1. **새 정답 경계로 한 번만 재집계한다.** 기존에 검증한 BASE 행 매칭을
   재사용하고 CSV의 실제 시각으로 다음 구간을 배정한다.

   | 정답 구간 | 집계용 경계 |
   |---|---|
   | WS1-BASE-FULL-PREFIX | 480 ≤ t < 550 |
   | WS1-BASE-DRAIN | 550 ≤ t < 652 |
   | WS1-BASE-RAPID-REFILL / REFILL | 652 ≤ t < 674 |
   | WS1-BASE-RAPID-REFILL / FULL_TRANSITION | 674 ≤ t < 675 |
   | WS1-BASE-FULL-SUFFIX | 675 ≤ t ≤ 780 |
   | OUTSIDE | 위 구간 밖 표본 |

   `WS1-BASE-RAPID-REFILL`은 기존 ID만 유지한다. REFILL과 FULL_TRANSITION은
   그 안의 서로 겹치지 않는 하위 구간이며, 상위 합계와 함께 중복 가산하지 않는다.
   674–675초의 정확한 FULL 도달 프레임은 미확인이다. 이 구간의 숫자를
   시각만으로 정답/오검출로 판정하지 않는다. 675초는 전환 후 집계 경계다.
   `(glass_id, frame_index)`의 기존 1:1 매칭 행마다 **구간 하나만** 배정한다.
   시간은 `float(row["timestamp_sec"])`이고, 가장 가까운 표본으로 경계를
   옮기거나 양끝 포함 집계를 따로 더하지 않는다.

   ```python
   def base_segment(t):
       if 480 <= t < 550:
           return "FULL_PREFIX"
       elif 550 <= t < 652:
           return "DRAIN"
       elif 652 <= t < 674:
           return "REFILL"
       elif 674 <= t < 675:
           return "FULL_TRANSITION"
       elif 675 <= t <= 780:
           return "FULL_SUFFIX"
       return "OUTSIDE"
   ```

   구간별 표본/v1 Oil/v2 Oil/새 출력/소실/순증가만 전달한다. OUTSIDE를 포함한
   합계는 계속 **601 / 185 / 303 / 119 / 1 / +118**이어야 한다. 다른 값이면
   맞춰 고치지 말고 불일치를 보고한다. 숫자 0은 빈 칸과 구분한다.
   f15776@657.9907초의 소실 1행과 기존 662–664.5초 여섯 표본은 이제 모두
   REFILL에 속한다. 소실 행이 실제 유면 손실인지는 아직 미평가다.
   이전 663.6–780초의 42→109행 및 새 출력 67행은 옛 시각 구간의 측정으로만
   보존한다. 새 FULL_SUFFIX 오검출 수로 재사용하거나 총 출력에서 추정하지 않는다.
2. **f15896 IFO 확인은 완료다.** 빈 evaluations와 빈 qualifying 집합을
   재질문하지 않는다. 기존 일곱 `INCOMPATIBLE_BRANCH` 후보는 admitted=0으로
   IFO 입력 전에 제외된 기록이며 실제 유면 후보인지 여부는 별도 영상 판정이다.
3. **기존 review 방식으로 실제 유면을 확인한다.** 기존 명목 662/662.5/663/
   663.5/664/664.5초 여섯 표본부터 진행한다. 원본 열람 가능 여부를 먼저 적고,
   [O2의 packet 준비·회신 저장 절차](s11-o2-local-shadow-evaluation.md#1-먼저-한-프레임의-검토-packet-만들기)를
   재사용한다. 기존 review-001/002/003과 판정 이력은 보존하고, 새 표본은 별도
   review 폴더에 둔다. `prepare`는 이미지를 자동 생성하지 않으므로 원본과
   가이드를 별도로 준비한다. 필요한 O1 witness/geometry가 없는 경우에는
   준비 불가 범위를 적고, native 경로나 다른 번들의 idx를 추정해 채우지 않는다.

   - 질문 전에 **무주석 원본과 후보 가이드를 실제로 표시**하고 파일 위치를
     알려준다. 실제 input idx, source Y 눈금, 필요한 X 구간을 표시하며
     packet/프레임별 번호와 최종 선택 선을 구분한다. 움직임 비교가 필요한
     프레임은 나란히 보여준다. 새 이미지 도구보다 기존 가이드 도구를 우선한다.
   - 원본상 계면 `보임/안 보임/판별 불가`, 선택 선과의 `일치/불일치/판별 불가`,
     서로 다른 후보가 같은 실제 계면을 따라가는지 확인한다. 식별 가능한
   source Y/범위와 Glass 내부 상단을 적되 정밀 좌표를 강제로 요구하거나
   ROI 상단을 실제 Glass 상단으로 대신하지 않는다. 마지막 실제 계면의
   정확한 시각·위치는 후속 FULL closure에 필요할 때 별도로 확인한다.
   - 사용자의 실제 답을 `record`로 labels/replies/history에 남기고 `status`로
     재개한다. 에이전트의 이미지 해석과 사용자 직접 판정을 구분한다. 기존
     첫 등장·중간 하강 판정은 정확한 대응이 확인된 것만 재사용하며, 새 출력이나
     소실 중 다음 판정에 필요한 미검토 표본만 추가한다. 같은 idx라는 이유로
     다른 번들에 판정을 복사하지 않는다.
   - 721초 비유면 출력은 기존 음성 대조로 보존한다. 아지랑이라는 광학적 원인
     확정이나 전체 후보 재라벨링을 다음 비교의 선행 조건으로 삼지 않는다.
     원본 열람/표시가 불가하면 그 한계를 기록하고 사람 판정 완료로 쓰지 않는다.
     숫자 표로 실제 영상 판정을 대신하거나 미확인 값을 정답으로 채우지 않는다.

**현재 분석의 종료 조건:** 1의 새 경계 표 하나로 CSV 작업을 끝내고,
이미 완료한 2와 소실/OUTSIDE 식별은 재사용한다. 중복·불일치는 명시적으로
해결하거나 미확인으로 남기며 숫자를 맞춰 쓰지 않는다. 298개 빈 프레임의
원인 전수 조사나 전체 후보/predicate
추출로 확대하지 않는다. 3은 필요한 대응 판정과 남은 불확실성/접근 한계를
저장하면 종료한다. 판별 불가는 유효한 기록이며, 해당 정확도 주장은 미평가로
유지한 채 후보 비교 준비로 진행한다. 모든 누락의 해결이 종료 조건은 아니다.

Y433.5→409는 감소이고 409→418은 증가(아래쪽 이동)다. 서로 다른 선택
tracklet을 곧바로 하나의 실제 상승 계면이나 승인된 handoff로 해석하지 않는다.
664.497초는 요청한 여섯 행의 마지막일 뿐 마지막 실제 계면 시각이 아니다.
사용자가 674–675초 FULL 도달을 직접 정정했으므로 같은 구간 질문을 반복하지 않는다.
Windows 에이전트의 LVLM 판독은 후보별 사용자 판정이 아니다. 기존 여섯 프레임은
재충전 도중의 위치/대응 검토로 재사용한다. BASE/Accum을 명확히 표시하고,
서로 다른 tracklet ID만으로 실제 계면이 다르다고 단정하지 않는다. f15896의
빈 출력은 위치가 잘못된 선과 구분한다. 전환 구간의 정확한 프레임/Y 확인은
후속 FULL closure 판단에 필요할 때만 수행한다.

FULL 전환 구현 완료는 다음 세 후보 비교의 선행 조건이 아니다. 개별 비교 후
유효한 결과를 바탕으로 기존 lifecycle의 refill closure/handoff 책임을 재사용한다.
초기 FULL 관측 허용은 motion owner를 만들지 않는다. 중간 관측 소실·오검출의
소실·고정 정답 시각을 FULL 근거로 사용하지 않는다.
재실행·해시 비교·전체 JSON은 필요 없으며, 723/771초 veto는 유지한다.
이번 작업은 제한된 BASE 진단이다. Accum/Foam 최종 동일성과 전체 구간 승인은
아직 별도 미확인으로 남긴다.

완료된 요청의 이전 전달문 — 재전달하지 않음:

```text
③ v1: <v1 번들 경로>
④ v2: <v2 번들 경로>
원본 영상: <영상 경로>
review 폴더: <review 폴더 경로>
docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md와
docs/40-operations/s11-current-windows-field-qualification.md의
“Refill owner and false-output follow-up” 절을 읽고 진행해줘.
사용자 정정은 BASE 550–652초 하강, 652–674초 회복, 674–675초 사이 FULL이야.
기존 CSV를 새 경계로 한 번만 재집계하고 674–675초는 전환 구간으로 따로 보여줘.
총 601행 / 185→303 / 새 출력119−소실1=118은 유지돼야 해.
완료된 f15896 IFO·소실 행·OUTSIDE 확인은 반복하지 마.
이후 필요한 미검토 장면만 기존 O2 방식으로 BASE/Accum이 명확한 원본·idx
가이드를 보여주고 내 답을 review에 저장해줘. 기존 여섯 프레임은 재충전 도중이야.
에이전트 판독을 내 판정으로 쓰지 말고, detector 재실행·해시 비교는 하지 마.
```

### Three-candidate Windows comparisons

**승인된 순서:** 완료된 CSV/review 재사용 → 공통 기준·로컬 옵션 준비 → 아래 세
후보를 각각 Windows에서 비교 → 유효한 결과에 근거한 FULL 전환·통합 검증.
이 절은 실행 순서이며 세 후보 옵션이 이미 준비됐거나 합격했다는 뜻은 아니다.

공통 기준은 **④ FULL+ON v2**다. ③ v1은 완료된 CSV 비교용, ② UNKNOWN+OFF는
누락 위치 참고용으로 보존한다. v2도 오검출을 포함하므로 물리 정답으로 쓰지 않는다.
Windows의 유체 이동 범위를 포함하는 용기 내부 ROI를 한 번 확인한 뒤 영상,
Recipe/ROI, 480–780초, 2fps, BASE FULL/Accum EMPTY를 고정한다. ROI나 공통
설정을 바꿔야 하면 같은 조건으로 v2 기준 실행도 준비하고 이전 수치와 섞지 않는다.

| 우선순위 | 개별 비교 | 확인할 효과와 반대 대조 |
|---|---|---|
| 1 | v2 + cost-first assignment | 실제 유면 연결·방향·재충전 추적 회복과 다른 경계로의 잘못된 연결 |
| 2 | v2 + candidate-local RGB | 실제 유면/반사·rim 구별과 실제 유면의 잘못된 제거; 기존 고정 가중치 재사용 |
| 3 | v2 + Oil-only Local XY | 사전에 지정한 구조물 영향 감소와 실제 Oil 관측·최종 Foam 결과의 손실 |

각 후보는 하나씩만 추가한다. 1번 위에 2번을 누적하지 않는다. RGB 모델과
Local XY 범위는 결과 열람 전에 고정하며 재학습·cutoff/영역 탐색을 반복하지 않는다.
각 로컬 준비는 기존 책임과 실행 경로를 재사용하고 필요한 검증 후 소스/실행 옵션,
Windows 절차와 짧은 전달 프롬프트를 함께 제공한다. GUI 실행/완료 bundle과
단순 shadow 측정은 구분하며, shadow 점수만으로 최종 추적 효과를 주장하지 않는다.

각 비교는 같은 형식으로 종료한다: 구간별 최종 CSV 변화, 달라진 주요 장면의
review, 실제 유면 회복·소실과 비유면 출력 변화, Accum/Oil·Foam 부작용,
**효과 있음 / 효과 없음·악화 / 판단 근거 부족** 및 근거. 숫자 출력 증가만으로
성공 처리하지 않는다. 필요한 불확실성만 추가 확인하고 실패한 후보의 전체
원인 해결을 다음 후보의 조건으로 삼지 않는다. 실패 결과를 남기고 다음 순위로
진행하며, 세 후보가 끝나면 자동으로 네 번째 실험을 만들지 않는다.

개별 결과를 확보한 뒤 선택한 구성에서 증거에 기반한 상단 소실→FULL을
구현·검증하고, 아래 전체 9개 구간 및 Oil·Foam 보고서 이해 가능성을 확인한다.
721초 오검출과 723/771초 보호 조건을 보존하며, 개별 성공을 조합의 성공으로
간주하지 않는다. 유효 후보가 없으면 결과와 한계를 기록하고 다음 방향은 사용자와
결정한다. 현재 accepted baseline과 O2/FIELD FAIL은 실제 승인 근거 전까지 유지한다.

### Priority 1 cost-first comparison

**실행 결과 수신 / 악화·미채택 — 2026-10-16.** BASE 재충전 Oil 39→0으로
채택하지 않는다. 아래 실행 절차는 완료 이력이며 재실행 요청이 아니다.
후속 [Cost-first result closeout](#cost-first-result-closeout)도 완료됐다.
구현 `2083277`과 게시 handoff 소스의 옵션은 그대로 보존한다.

이번 비교는 **④ FULL+ON v2 ↔ ⑤ FULL+ON v2 + cost-first**다. 여기서 OFF/ON은
cost-first만 뜻하며, 두 조건 모두 초기 FULL 관측 옵션 v2를 켠다. 초기 FULL+OFF나
UNKNOWN+OFF, v1과 비교하는 작업이 아니다. 후보 2·3은 아직 준비 전이다.

1. Work Plan의 이번 후보 소스를 사용한다. 기존 ④ bundle은 영상·Recipe/ROI·
   480–780초·2fps·BASE FULL/Accum EMPTY·debug 수준이 같으면 재사용한다.
   용기 내부 ROI가 전체 유면 이동 범위를 포함하는지 한 번 확인한다. ROI나
   설정을 바꾸면 새 소스에서 두 조건을 모두 실행하고 옛 수치와 섞지 않는다.
   초기 상태는 GUI에서 별도로 확인하며 실행 옵션이 자동으로 바꾸지 않는다.
2. 새 소스 폴더에서 아래 PowerShell 명령으로 GUI를 연다. 기존 Windows Python
   환경을 사용하고 분석 시작부터 완료 bundle 생성까지 수행한다. 같은 조건에서
   cost-first만 바꾸며, 기본 BASIC debug로 충분하다. 별도 가중치나 대용량
   Mac 실험 자료는 필요 없다. 결과는 `sample/output/` 아래 서로 다른 폴더에 둔다.

   ```powershell
   $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
   python -m oil_tracker --initial-full-observation --oil-cost-first-assignment
   ```

   기준 v2를 재실행할 필요가 있을 때는 GUI를 닫고 같은 폴더에서 실행한다.

   ```powershell
   python -m oil_tracker --initial-full-observation
   ```

   후보 창에는 `초기 FULL 관측 비교`와 `Oil cost-first 비교`가 함께 표시된다.
   trace의 `record.sequence.state.sequence_resolver_version`에는
   `+initial-full-observation-v2+cost-first-assignment-v1`이 붙는다.
   기준에는 cost-first 접미사가 없다. raw `record.state`와 completed `sequence`
   를 혼동하지 않는다. cost-first는 모든 Glass의 Oil 연결에 적용되므로 Accum도
   비교한다. Foam의 직접 정책은 그대로지만 최종 합성 결과까지 같다고 가정하지 않는다.
3. 두 최종 `tracking_data.csv`를 Glass/frame으로 대응시키고 실제 timestamp를
   사용한다. BASE는 480–550 / 550–652 / 652–674 / 674–675 / 675–780초의
   서로 겹치지 않는 구간과 OUTSIDE로 집계한다. 새 출력·소실·양쪽 숫자이나 Y가
   달라진 행을 구분하고 총합을 맞춘다. Accum은 기존 canonical 구간별 Oil/Foam
   최종 수치·유효성·가시 구간 변화를 함께 요약한다. 후보/admitted 수를 최종 출력으로
   대체하지 않는다. 기준의 기존 601/303은 동일 조건일 때만 대조 수치로 쓴다.
4. 변경 장면만 기존 O2 review 절차로 확인한다. review-004의 여섯 프레임과 사용자
   설명을 재사용하고, 새 후보 idx는 새 packet의 frame/source Y로 연결한다.
   **복수 후보 허용·대략적 일치·판단 불가**를 보존하고 단일 Y를 강제로 고르거나
   기존 두 선호 차이를 확정 오검출로 바꾸지 않는다. 필요한 새 review/reply는
   별도 review 폴더에 기록하고 review-004를 덮어쓰지 않는다.
5. 우선 확인점은 첫 하강, 652–674초 재충전(특히 f15896@662.996초의 누락),
   721초 비유면 출력, 723/771초 보호 조건, FULL 구간의 새 숫자 출력이다.
   현재 선택·CSV와 실제 장면을 함께 보고 유면 회복/소실, 다른 경계로 연결됨,
   판단 불가를 구분한다. 달라지지 않은 프레임은 재판정을 요구하지 않는다.
   원인 확인은 중요한 변경 사례의 최초 확인 가능한 단계까지로 제한하며
   전체 빈 프레임 분석이나 추가 상세 재실행을 자동으로 시작하지 않는다.
6. 간단한 집계표와 변경 장면 판정, Accum/Foam 영향, **효과 있음 / 효과 없음·악화 /
   판단 근거 부족**을 반환한다. 상단 소실→FULL은 이번 변경의 구현 범위가 아니다.
   결과를 보며 임계값·ROI·모델을 조정하거나 다음 후보를 누적하지 않는다.

기존 실행용 프롬프트 (완료 이력; 다시 보내지 않음):

```text
기준 ④ FULL+ON v2 bundle: <기준 번들 경로>
새 cost-first 소스: <새 소스 폴더>
기존 review-004: <review-004 폴더>

docs/40-operations/s11-current-windows-field-qualification.md의
“Priority 1 cost-first comparison”과 work-plan의 현재 후보를 읽고 진행해줘.
기준과 같은 조건으로 FULL+ON v2 + cost-first를 GUI에서 실행해 비교해줘.
두 조건 모두 --initial-full-observation을 켜고, 후보에만
--oil-cost-first-assignment를 추가해줘. 설정이 같으면 기존 기준 bundle을 재사용해줘.
최종 CSV 구간별 변화와 달라진 장면, Accum/Foam 영향을 간단히 정리해줘.
review-004의 복수 허용 후보와 불확실성을 유지하고, 추가 판단이 필요할 때만
O2 review로 질문·회신을 저장해줘. 임계값 조정이나 다음 후보 실행은 하지 말아줘.
```

### Cost-first result closeout

**완료 이력 — review-005 회신 수신. 다시 요청하지 않음.** 601행 집계,
Accum new 17/lost 31, review-004 여섯 행과 Accum 두 장면의 사용자 회신을
받았다. 사용자가 확정한 Windows 보관 위치는 기존
`0.windows_diagnostic/data/reviews/review-005/`다. 아래 최초 요청의 저장 경로는
이 후속 결정으로 대체됐으며 review-005를 다시 이동하지 않는다.
⑤는 BASE 전체 재충전 관측 소실로
**악화·미채택**이다. 721초와 FULL suffix의 비유면 숫자 제거는 함께 기록한다.
Accepted baseline, O2 OPEN / FIELD FAIL, cost-first → RGB → Local XY 순서는
그대로다. 다음 보완은 Accum 부작용 기록을 마치는 작업이며 미채택을 재심사하거나
새 알고리즘 진입조건을 만드는 작업이 아니다.

1. 기존 ④/⑤ CSV만 사용해 각 Glass 601행의 누락 없는 집계를 마무리한다.
   BASE 표에 빠진 **674–675초 FULL_TRANSITION 2행 / OUTSIDE 1행**을 추가한다.
   Accum은 BASE 구간을 쓰지 말고 **480–653 / 653–672 / 672–680 / 680–700 /
   700–780초 + OUTSIDE**로 다시 배정한다. 구간은 앞 포함·뒤 제외, 마지막은
   780초 포함으로 한 행을 한 곳에만 넣는다. 각 구간의 Oil/Foam 최종 숫자 수,
   새 출력/소실, 전체 합계를 반환한다. 현재 Accum 표의 기준 Oil 합계는 34이며
   전체 36과 2행 차이가 있다. 실제 CSV로 배정하고 임의로 채우지 않는다.
2. review-004의 **f15872 / f15884 / f15896 / f15908 / f15920 / f15932**를
   6행으로 대응해 두 조건의 최종 Oil Y/valid/fill_state를 적는다. 이전 요약에서
   빠진 f15884도 포함한다. 기존 사용자 판정·복수 허용·대략적 일치·불확실성을
   재사용하며 BASE 6장면과 721초는 다시 질문하지 않는다. 빈 CSV는 원시 후보
   부재라는 뜻이 아니다. 723/771초 UNKNOWN 유지만 확인됐으면 그렇게 적고,
   실제 predicate가 같다는 결론으로 확대하지 않는다. 이 확인을 위한 전체 trace
   추적이나 원인 규명을 추가 작업으로 만들지 않는다.
3. 새 O2 review는 **Accum 두 장면까지만** 준비한다.

   - **신규 Oil:** 727–779초 중 ④ 빈 값 → ⑤ 숫자 출력인 장면 1개.
   - **Oil 소실:** 670–674초 중 ④ 숫자 출력 → ⑤ 빈 값인 장면 1개.

   각 범위에서 조건을 만족하는 첫 표본을 택하고, 움직임/정체가 애매할 때만
   인접 3–5프레임을 같은 장면의 문맥으로 보여준다. 해당 변경이 없으면
   `NOT_FOUND`로 남기고 범위를 넓히지 않는다. 670–674초 전체를 Foam으로
   부르지 말고 실제 시각에 맞는 canonical 구간을 적는다.
4. [O2 질문·회신·기록 절차](s11-o2-local-shadow-evaluation.md#3-에이전트-질문--사용자-회신--기록재개)를
   재사용한다. 신규 출력은 ⑤ 선택 선, 소실은 ④ 선택 선을 해당 bundle/frame에
   연결하고 주석 없는 원본과 가이드를 함께 준비한다. 새 packet·이미지·reply는
   `sample/output/reviews/<새 review 폴더>/`에 저장하고 review-004는 보존한다.
   질문은 실제 Oil 계면인지, Foam 상단/반사/잔류물 등 다른 대상인지, 판단 불가인지로
   제한한다. 선택된 선이 완벽하다고 가정하지 않고 복수 허용/대략적 일치를 받는다.
   LVLM은 참고 관찰로 분리하고 사용자 회신은 기존 `record` 명령으로 저장한다.
   판독이 어려우면 uncertainty를 남기고 이 장면을 종료한다.
5. 보완 집계와 두 장면의 판정/불확실성만 반환한다. 판단 불가도 유효한 종료다.
   ⑤ 재실행·임계값/ROI 조정·전체 빈 프레임 분석은 하지 않는다. 이 보완을
   받은 뒤 로컬에서 **우선순위 2번 candidate-local RGB**를 준비하며, cost-first를
   누적하지 않는다. Windows 담당자는 새 후보를 임의로 실행하지 않는다.

이전 보완용 프롬프트 (완료 이력; 다시 보내지 않음):

```text
④ FULL+ON v2 bundle: <기준 번들 경로>
⑤ cost-first bundle: <후보 번들 경로>
기존 review-004: <review-004 폴더>

docs/40-operations/s11-current-windows-field-qualification.md의
“Cost-first result closeout”을 읽고 저장된 결과만 보완해줘.
BASE 누락 구간, Accum의 정답 구간별 집계, review-004 여섯 행(f15884 포함)을
마무리해줘. BASE와 721초는 기존 판정을 재사용해줘.
새 O2 review는 Accum 신규 Oil(727–779초) 1장면과 소실(670–674초) 1장면만
준비하고 사용자 회신을 기록해줘. 복수 허용·대략적 일치·판단 불가를 유지해줘.
새 파일은 sample/output/reviews/ 아래 별도 폴더에 저장해줘.
⑤는 악화·미채택이며 기존 O2/FIELD 상태와 1→2→3 순서는 유지해줘.
디텍터 재실행이나 추가 튜닝 없이 보완표와 두 장면 결과만 반환해줘.
```

### Priority 2 candidate RGB comparison

**완료된 실행 절차.** [Windows 회신](../60-evidence/s11/2026-10-14-candidate-rgb-trial.md#windows-rgb-result--2026-10-16)에서
BASE 303→0, Accum 36→3이며 ⑥은 **악화·미채택**이다. 회신은 headless
pipeline/use-case 실행으로 기록하고 GUI 재실행을 요구하지 않는다. review-006은
미검토로 보존하며 RGB 종료를 위해 추가 질문하지 않는다. 아래 명령은 실행 이력이다.

구현 소스는 `d7e19baf32df012ad113ed2318dd278a7258de80`이다. 이 커밋 또는
이후 문서만 갱신한 전달용 ZIP을 사용하며, 실제 받은 ZIP의 revision을 실행 기록에 남긴다.

실행한 비교는 **④ FULL+ON v2 ↔ ⑥ FULL+ON v2 + candidate RGB**다.
⑤ cost-first 결과 위에 RGB를 추가하지 않는다. 고정 가중치/입력은 이전 RGB
실험과 같고, 새 부분은 그 판정을 최종 Oil 후보 자격 조건에 연결한 것이다.
기존 rim 오수용 3건은 남는다. RGB 허용은 물리적 정답이나 확률이 아니며,
입력 부족/판정 불일치는 별도로 기록한다. 모델 재학습이나 cutoff 조정은 없다.

1. 새 소스 ZIP을 별도 폴더에 풀고 기존 Windows Python 환경을 사용한다.
   작은 고정 가중치는 소스의 `src/oil_tracker/resources/models/`에 포함되어
   있으므로 별도 다운로드/Torch 설치는 필요 없다. 영상·Recipe/ROI·480–780초·
   2fps·BASE FULL/Accum EMPTY·debug 수준을 ④와 동일하게 유지한다. 기존 ④는
   조건이 같으면 재사용하며, 이번 기준이 FULL debug이면 후보도 FULL로 실행한다.
   설정을 변경했다면 같은 조건의 v2 기준을 새로 만들고 옛 수치와 섞지 않는다.
2. 새 소스 폴더에서 아래 명령으로 GUI를 연 뒤 직접 분석을 시작한다.

   ```powershell
   $env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
   python -m oil_tracker --initial-full-observation --oil-candidate-rgb
   ```

   기준 재실행이 필요한 경우에는 `python -m oil_tracker --initial-full-observation`을
   사용한다. 초기 FULL/EMPTY 설정은 옵션이 바꾸지 않으므로 GUI에서 유지한다.
   후보 창에는 `초기 FULL 관측 비교`와 `Oil RGB 비교`, trace의 completed
   `sequence_resolver_version`에는 `+initial-full-observation-v2+candidate-rgb-v1`이
   있어야 한다. cost-first 접미사는 없어야 한다. 소스가 잘못 선택되거나 가중치
   오류로 실행이 중단되면 그 결과만 알리고 옵션을 끄거나 모델을 교체하지 않는다.
3. 완료 bundle의 최종 CSV를 Glass/frame으로 대응시킨다. BASE는
   480–550 / 550–652 / 652–674 / 674–675 / 675–780초 + OUTSIDE,
   Accum은 480–653 / 653–672 / 672–680 / 680–700 / 700–780초 + OUTSIDE로
   중복 없이 집계한다. 마지막 780초만 포함하고 나머지 구간 끝은 제외한다.
   각 구간의 표본·숫자 Oil/Foam·새 출력·소실·양쪽 숫자이나 Y 변경을 반환한다.
   최종 Oil/Foam 유효성/상태/flags도 비교하며, 모델 허용/후보 수를 CSV로 대신하지
   않는다. 동일 조건의 기준은 BASE 601/303 Oil, Accum 601/36 Oil이다.
4. RGB는 모든 Glass의 Oil 후보에 적용된다. raw `record.state.oil_candidate_rgb`의
   판정 수와 후보 `oil_candidate_rgb_decision`/`oil_candidate_rgb_variants`를 통해
   허용·거부·UNKNOWN·UNAVAILABLE을 구분한다. 거부/미측정 후보도 trace에 남는다.
   숫자 감소가 실제 계면 제거인지 비유면 제거인지 분리하고, 기본값 OFF와
   비교해 최종 Foam이 같은지 확인한다. raw 후보 없음과 최종 선택 없음은 다르다.
5. review-004의 여섯 BASE 프레임, review-005의 Accum f17431/f16076,
   721초 비유면 출력과 723/771초 최종 거부를 기존 판정 범위에서 대조한다.
   idx는 packet마다 달라질 수 있으므로 정확한 frame/source Y/후보를 연결한다.
   복수 허용·대략적 일치·판단 불가를 유지하고 이미 답한 장면은 다시 질문하지 않는다.
   새로 달라진 중요한 장면에만 기존 O2 절차로 plain/guide와 질문을 준비한다.
   사용자 회신 전에는 unreviewed/pending이며 LVLM 관찰은 참고로 구분한다.
6. 새 분석 bundle/대용량 실행 출력은 `sample/output/` 아래에 둔다. Windows의
   사용자 검토 packet·labels·replies는 사용자가 지정한 기존
   `0.windows_diagnostic/data/reviews/`의 **새 review 폴더**에 저장하고 이전
   review-004/005를 보존한다. 사용자 회신은 기존 `record` 명령으로 기록한다.
7. 구간별 집계·주요 변경 장면·Accum/Foam 영향과 **효과 있음 / 효과 없음·악화 /
   판단 근거 부족**을 반환한다. 전체 빈 프레임 원인 분석이나 추가 튜닝은 하지 않는다.
   FULL 전환은 이번 RGB 변경 범위 밖이며 accepted baseline과 O2/FIELD 상태는
   유지한다. 다음 Local XY는 별도 준비 후 v2와 비교한다.

이전 실행용 프롬프트 (완료 이력; 다시 보내지 않음):

```text
④ FULL+ON v2 bundle: <기준 번들 경로>
새 RGB 소스: <새 소스 폴더>
기존 review-004/005: <기존 review 폴더>

docs/40-operations/s11-current-windows-field-qualification.md의
“Priority 2 candidate RGB comparison”을 읽고 진행해줘.
기준과 같은 조건으로 --initial-full-observation --oil-candidate-rgb를 켜서
GUI 분석을 완료해줘. cost-first와 Local XY는 끄고, 조건이 같으면 ④를 재사용해줘.
최종 CSV 구간별 증감과 주요 변경 장면, Accum/Foam 영향을 정리해줘.
review-004/005의 사용자 판정과 복수 허용·대략적 일치를 재사용하고,
새 판단만 기존 review 폴더의 새 packet으로 질문·기록해줘.
재학습·임계값/ROI 조정 없이 결과를 반환해줘.
```

### Priority 3 Local XY input preparation

**완료 이력: review-007로 입력 준비 완료. 아래 준비 절차를 반복하지 않는다.**
당시 실행은 다음 [Local XY comparison](#priority-3-local-xy-comparison)에 기록되어 있다.
[saved-output closeout](#priority-3-local-xy-saved-output-closeout)까지 완료됐다. 기존
[`OilMeasurementScope`](../../src/oil_tracker/adapters/vision/oil_measurement_scope.py)는
지정된 source X/Y 영역의 Oil 측정만 제외하는 구현이며 자동 구조물 검출기가 아니다.
현재 GUI에는 이를 켜는 flag가 없고, 기존 진단 runner의 rectangle은 Mac sample4용이다.
새 `--oil-local-xy` 옵션이 있다고 가정하거나 Mac 좌표를 Windows에 복사하지 않는다.
[구현 재사용과 입력 경계](../60-evidence/s11/2026-10-09-local-xy-implementation.md#windows-input-preparation--2026-10-16)를 읽는다.

1. 기존 ④ bundle, 같은 Recipe, 원본 영상과 review 폴더를 사용한다. Recipe의
   Artifact template, support reference, exclusion 설정과 기존 회신에서 이미
   확인한 **고정 구조물 영역**이 있는지 확인한다. 이미 충분히 확인한 영역은
   재질문하지 않는다. 후보 idx/한 점의 비유면 판정은 사각형 전체의 제외 허용이 아니다.
2. 적용할 Glass별로 **한 번 고정할 scope 집합**을 준비한다. 각 영역의 원본
   frame/time, 이미지 크기, source 좌표 `[x0,x1) × [y0,y1)`, 보이는 구조물과
   기존 판정 근거를 표에 적는다. ROI-local 좌표면 crop origin을 명시해 source로
   변환한다. 범위는 고정 구조물 근거로 정하며, 검출률을 보고 넓히거나 이동하지 않는다.
   717–750.5초의 흔들리는 비유면 tracklet 전체를 고정 제외 띠로 바꾸지 않는다.
   구조물 확인과 별개로 실제 계면이 그 영역을 통과할 가능성도 그대로 기록한다.
3. 기존 자료에 충분한 영역 판정이 없으면 **구체적인 구조물 장면 하나**의 plain/
   guide를 준비한 뒤 사용자에게 해당 표시 범위의 역할과 실용적인 제외 범위를
   확인한다. 막연한 좌표 요청이나 기존 계면 재질문은 하지 않는다. 적절한 영역을
   찾지 못하거나 혼합/불명확하면 `NOT_PREPARED`로 반환한다. 임의 mask로 대체하지 않는다.
   새 질문·원본·reply는 `0.windows_diagnostic/data/reviews/`의 새 폴더에 두며,
   회신 전은 pending/unreviewed, LVLM 관찰은 참고다. 기존 record/history 방식을
   사용하되, 후보 판정만으로 sampling rectangle이 확정됐다고 저장하지 않는다.
4. 확인된 입력은 기존 `OilMeasurementScope.bind`에 필요한 Glass/geometry/settings,
   frame size와 원본 reference를 연결해 보존한다. 같은 reference가 기존 Artifact
   전체 후보 veto에도 쓰이면 충돌로 보고하고 template을 끄거나 삭제하지 않는다.
   공유 Recipe exclusion과 Oil-only scope를 혼동하지 않고 Recipe/ROI는 그대로 둔다.
5. **영역 표·판정 상태·적용 가능한 Glass·충돌/없는 입력만 반환**한다. private
   이미지/영상/packet은 Windows에 남긴다. RGB의 721/723초 요약과 eligible 수 충돌은
   이전 근거와 구분해 보존하되 전체 CSV/trace 분석이나 추가 RGB 질문을 재개하지 않는다.
   review-006은 아직 미검토이며, Foam 하단이 실제 Oil/Foam 계면이면 정상 Oil 대상이다.
6. 이 입력으로 실행 경로를 준비한 뒤 **④ v2 ↔ ⑦ v2+Oil-only Local XY**를 한 번
   비교한다. 양쪽 initial-FULL v2, cost-first/RGB OFF, 같은 480–780초/2fps/초기값/
   debug 조건이다. 적용 scope는 detector의 `+oil-local-xy-v1:<digest>`와 manifest로
   구분하며 resolver 접미사가 바뀐다고 가정하지 않는다. 실제 실행은 다음 handoff이며,
   raw Foam뿐 아니라 최종 Foam 좌표/validity/episode까지 비교한다. 실행 출력은
   `sample/output/`에 둔다. FULL 전환과 최종 채택은 세 비교 이후의 별도 단계다.

이전 입력 준비용 프롬프트 (완료 이력; 다시 보내지 않음):

```text
④ FULL+ON v2 bundle: <기준 번들 경로>
Recipe·원본 영상: <경로>
기존 review 폴더: <경로>

docs/40-operations/s11-current-windows-field-qualification.md의
“Priority 3 Local XY input preparation”을 읽고 적용 영역만 준비해줘.
기존 Recipe/review에서 확인된 고정 구조물 영역을 우선 재사용하고,
Glass·근거 프레임·원본 X/Y 범위·판정 상태를 표로 반환해줘.
새 판단이 꼭 필요하면 구체적인 한 장면의 plain/guide를 준비해서 질문해줘.
Mac sample4 좌표를 복사하거나 ROI를 바꾸지 말고 디텍터는 아직 실행하지 마.
RGB는 악화·미채택으로 종료하고 review-006은 미검토 상태로 보존해줘.
```

### Priority 3 Local XY comparison

**완료 이력: ④ FULL+ON v2 ↔ ⑦ FULL+ON v2 + Oil-only Local XY 실행 완료·미채택.**
아래 실행 절차를 반복하지 않는다. 후속
[saved-output closeout](#priority-3-local-xy-saved-output-closeout)까지 완료됐다.
Review-007의 Accum 승인(reply-001)과 BASE 승인(reply-002)을 재사용한다.
[입력 수신·Artifact 설명 정정·실행 경계](../60-evidence/s11/2026-10-09-local-xy-implementation.md#windows-scope-receipt-and-comparison-handoff--2026-10-16)를 읽는다.
알고리즘은 기존 `oil-local-xy-v1` 그대로이며, 이번에 고정한 Windows 입력으로
한 번 비교한다. cost-first/RGB는 OFF다.

1. **적용 범위는 두 Glass, 사각형 세 개다.** 같은 Recipe에서 아래 prefix에
   유일하게 대응하는 활성 Glass의 **전체 ID**를 사용한다. 배열 순서로 Glass를
   추정하지 않는다. 원본 크기는 `(1920,1080)`이며 좌표는 source 기준 half-open이다.

   | Glass | 영역 | source X/Y | 생성할 Rect | 원본 reference |
   |---|---|---|---|---|
   | BASE `8f94fb85` | R11 | `[100,163) × [468,710)` | `Rect(100,468,63,242)` | f17287 / 721 s |
   | BASE `8f94fb85` | R12 | `[106,114) × [713,757)` | `Rect(106,713,8,44)` | 같은 BASE reference |
   | Accum `8fb6ebc7` | R11 | `[1612,1622) × [321,430)` | `Rect(1612,321,10,109)` | f17335 / 723 s |

   Review-007의 원본 reference/판정 연결을 재사용해 각 scope의 reference digest를
   얻는다. guide·확대 crop의 digest를 원본 대신 쓰거나 임의 값을 넣지 않는다.
   기존 packet에서 확인 가능한 입력을 사용자에게 다시 옮겨 달라고 요청하지 않는다.
   영역을 움직이거나 넓히지 않고, 717–750.5초 전체 Y 궤적을 제외 띠로 만들지 않는다.
2. **Artifact 설정은 그대로 유지한다.** 현재 Recipe는 BASE 12 / Accum 14개의
   template에 support reference가 없다고 확인됐다. 동일 좌표 template은 Local XY와
   공존할 수 있고 기존 공간 후보 veto도 계속 작동한다. `diagnostic_only`는 참조
   비교 상태이지 후보 제거 OFF가 아니다. 실제 입력에 같은 reference digest를 쓰는
   `support_reference`가 발견되어 `validate()`가 실패하면 해당 차이만 보고한다.
   이를 피하려고 template을 끄거나 reference를 바꾸지 않는다.
3. **RGB 비교 때 사용한 headless 실행기를 재사용한다.** Recipe/세션 로딩,
   `AnalysisPipeline`, `AnalyzeVideoUseCase`, `OutputBundleStore`는 유지하고 아래
   detector 설정만 전달한다. `base_glass`/`accum_glass`와 reference digest는 위에서
   확인한 실제 Windows 입력이다. 새 GUI flag나 Mac 진단 runner를 가정하지 않는다.

   ```python
   from oil_tracker.adapters.vision.oil_measurement_scope import OilMeasurementScope
   from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
   from oil_tracker.domain.geometry import Rect

   scopes = (
       OilMeasurementScope.bind(
           base_glass, frame_size=(1920, 1080),
           reference_sha256=base_reference_sha256,
           rectangles=(Rect(100, 468, 63, 242), Rect(106, 713, 8, 44)),
       ),
       OilMeasurementScope.bind(
           accum_glass, frame_size=(1920, 1080),
           reference_sha256=accum_reference_sha256,
           rectangles=(Rect(1612, 321, 10, 109),),
       ),
   )
   detector = OpenCvPhaseDetector(
       initial_full_observation=True,
       cost_first_assignment=False, candidate_rgb=False,
       oil_measurement_scopes=scopes,
   )
   ```

   실행 전 scope ID 집합이 BASE/Accum의 전체 ID 집합과 같고, 사각형 수가 각각
   2/1인지 확인한다. 두 scope의 `validate(glass, original_frame)`로 설정/geometry/
   크기/reference 충돌 검사를 수행한다. 이후 pipeline 내부의 프레임별 검사도 유지한다.
   `detector.version`과 `measurement_scope_manifest`를 실행 기록에 저장한다.
   detector의 `+oil-local-xy-v1:<digest>`로 적용을 구분하며, resolver는
   `+initial-full-observation-v2`를 유지한다. resolver만 보고 Local XY OFF로 오판하지 않는다.
4. 같은 영상·Recipe·공유 ROI/exclusion·Artifact·480–780초·2fps·FULL debug,
   BASE FULL / Accum EMPTY 초기 확정값으로 실행한다. 조건이 맞는 ④는 재사용하고
   ⑦만 생성한다. 새로운 대용량 출력은 `sample/output/`의 관리되는 실행 폴더에
   둔다. 기존 [산출물 관리 절차](experiment-artifact-lifecycle.md)를 재사용한다.
   Recipe/설정을 바꾸거나 RGB 모델을 재학습하지 않는다. 이번 실행은 headless
   production 경로 비교이며 GUI 조작 검증으로 기록하지 않는다.
5. **적용 확인과 최종 출력 비교를 함께 한다.** Glass별 scope와 측정 lineage에서
   실제 eligible 영역과의 교집합, `original/excluded/remaining/used_counts`,
   common-X/지원 부족 여부를 대표 영향 프레임에서 확인한다. 명목 사각형 면적이나
   Y 겹침만으로 측정 제외가 작동했다고 결론내리지 않는다. 범위 밖 동작과 기존
   Artifact 거부가 유지되는지도 확인한다. 측정이 바뀌므로 raw Oil 후보 동일성을
   요구하지 않고, 최종 선택 후보 → completed trace → CSV 좌표 일치를 확인한다.
6. 기존 구간 함수를 재사용해 BASE/Accum **각 601행**을 중복 없이 한 구간씩 집계한다.
   BASE는 480–550 / 550–652 / 652–674 / 674–675 / 675–780초와 OUTSIDE다.
   Accum은 480–653 / 653–672 / 672–680 / 680–700 / 700–780초와 OUTSIDE이며
   기존 canonical 함수의 경계 포함 규칙을 유지한다. 기준 Oil은 BASE 303,
   Accum 36이다. Oil 신규/소실/양쪽 숫자 Y 변경, fill/flags 변화를 구분한다.
   Foam은 raw 좌표뿐 아니라 completed/CSV 좌표, validity, confidence,
   confirmed frame/episode 및 Oil/Foam 순서 충돌까지 대조한다. raw Foam 불변을
   최종 Foam 무영향으로 줄여 쓰지 않는다.
7. Review-004 여섯 프레임과 review-005 두 장면, BASE 721초와 723/771초를 재사용한다.
   복수 허용·대략적 일치·판단 불가를 유지하고 새 판단이 필요한 **중요한 변경 장면**만
   기존 `0.windows_diagnostic/data/reviews/`의 새 packet/plain/guide로 질문·record한다.
   Review-006은 pending으로 보존하며, Foam–Oil 하단 경계도 정상 Oil 대상일 수 있다.
   BASE 721초 기존 최종 CSV Y694와 723초 빈 출력을 다른 Glass/후보 Y와 섞지 않는다.
   새로 출력이 줄었다는 이유만으로 오검출 개선이나 실제 계면 손실을 단정하지 않는다.
8. 영역 적용 확인, 구간별 증감, 실제 허용 계면의 유지/손실, 비유면 출력과 최종 Foam
   영향, 효과 있음/없음·악화/판단 근거 부족을 간략히 반환한다. 전체 빈 프레임 원인
   분석·scope/임계값 튜닝·추가 재실행은 하지 않는다. FULL 전환 구현과 최종 채택은
   세 비교 이후 판단하며 accepted baseline과 O2 OPEN / FIELD FAIL은 유지한다.

이전 비교 실행용 프롬프트 (완료 이력; 다시 보내지 않음):

```text
④ FULL+ON v2 bundle: <기준 번들 경로>
최신 소스와 기존 RGB 실행기: <경로>
review-007 및 기존 review 폴더: <경로>

docs/40-operations/s11-current-windows-field-qualification.md의
“Priority 3 Local XY comparison”을 읽고 ⑦을 실행·비교해줘.
승인된 BASE R11·R12와 Accum R11을 모두 적용하고, 기존 RGB headless 실행기를
재사용해줘. initial-FULL v2 ON, cost-first/RGB OFF이며 조건이 같은 ④는 재사용해줘.
기존 Artifact/ROI 설정과 승인 영역은 그대로 유지해줘.
두 Glass의 최종 CSV 증감, 실제 계면 유지/손실, 비유면 출력과 최종 Foam 영향을
정리해줘. 기존 사용자 판정은 재사용하고 새 판단이 필요한 변경 장면만 질문해줘.
출력은 sample/output/에 두고, 튜닝이나 추가 재실행 없이 결과를 알려줘.
```

### Priority 3 Local XY saved-output closeout

**완료 이력 — 정정 회신 수신, 다시 요청하지 않음.**
[정정된 두 구간표와 최종 FULL 행 수](../60-evidence/s11/2026-10-09-local-xy-implementation.md#saved-output-accounting-closeout--complete)를
수신했다. Glass별 601개 키가 일대일 대응하고 timestamp 불일치·중복·누락은 0건이다.
BASE 303→254(신규 5, 소실 54, 순감소 49), Accum 36→14(신규 1, 소실 23,
순감소 22)로 일치한다.
BASE Y 변경은 23행이며, 그중 DRAIN/REFILL의 두 행은 각각 −0.5px다.
Accum f17239@719.0s는 양쪽 Y385.0인 유지 행으로, 이전 소실 과계상을 정정했다.
④·⑦ 모두 두 Glass의 최종 `FULL_NO_INTERFACE` 행은 0건이다.
86%/42% 효과 비율은 철회한다. BASE f17383/Y913 비유면과 Accum f16076 허용
계면 소실에 따라 ⑦ **REGRESSION / NOT_ADOPTED**, O2 OPEN / FIELD FAIL을 유지한다.

세 후보 비교와 CSV 보완은 여기서 마감한다. 아래 번호 절차와 이전 프롬프트는
완료 이력이며 재실행하지 않는다. 추가 집계·후보 튜닝·이미지 질문 없이 기존
산출물과 pending review-006을 보존한다. 다음 구현 방향은 Work Plan의 사용자
판단 지점이며, ④ 기반의 증거 있는 상단 이탈→FULL 전환 복구가 제안 상태다.

1. 두 `tracking_data.csv`를 `(glass_id, frame_index)`로 일대일 대응한다. 중복,
   키 차이, timestamp 불일치 여부와 Glass별 행 수를 한 줄로 보고한다. 기대값은
   각 Glass 601행이며, 어긋나면 숫자를 맞추지 말고 차이를 적는다. Oil 숫자 행은
   최종 CSV의 `raw_oil_air_level_y`가 비어 있지 않은 행으로 일관되게 정의한다.
2. 기존 구간 함수로 각 행을 **한 구간에만** 배정해 BASE/Accum 표를 하나씩
   반환한다. BASE는 FULL_PREFIX/DRAIN/REFILL/FULL_TRANSITION/FULL_SUFFIX/
   OUTSIDE, Accum은 EMPTY/ENTRY_SPLASH/FOAM_LAYERED/POST_FOAM/DRAIN/OUTSIDE다.
   기존 canonical 경계 규칙을 재사용하고 경계 행을 양쪽에 넣지 않는다.
   각 행에는 `표본 수, ④ Oil, ⑦ Oil, 신규, 소실, 양쪽 숫자 Y 변경, 순증감`을
   적고 합계를 포함한다. Y 변경은 신규·소실에 중복 집계하지 않는다.
   별도로 Glass별 ④/⑦ `FULL_NO_INTERFACE` 행 수도 반환한다. 이를 시간 정답으로
   덮어쓰거나 기존 v2 결과만 보고 ⑦도 0이라고 추정하지 않는다.
3. **확인할 산술 차이는 두 가지다.** BASE는 전체 303→254이나 세부 신규/소실을
   합하면 신규 5·소실 54·순감소 49다. 717–751초 세부 소실은 7+7+35=49이며
   725–733초에는 7개의 대체 숫자 출력이 남는다. 기존 42행 설명이 무엇을 세었는지
   짧게 정정한다. Accum은 세부 기준 14+13+10=37이 전체 36과 다르고,
   소실 24·신규 1도 순감소 22와 맞지 않는다. 원인이 된 중복/누락/오기 등을
   실제 CSV에서 확인해 **해당 행의 frame/time과 정정 이유만** 덧붙인다.
   기존 86%/42%는 순증감·소실·물리 판정을 섞은 비율이므로 효과 지표로 사용하지 않는다.
4. 물리 판정은 기존 범위 그대로 둔다. Review-004는 662–664.5초 여섯 프레임의
   실용적 허용 판정이고, review-005 f16076은 확인된 소실 사례다. 이것만으로
   Accum 소실 14행 모두의 과거 Y가 정확했다고 확장하지 않는다. Review-008은
   f17383/Y913 바닥벽 판정이다. BASE는 canonical truth상 675초 이후 계면이
   없으므로 그 뒤 새 숫자나 Y 이동을 실제 계면 복원으로 세지 않는다.
   Accum 신규 683.5초/Y205는 기존 판단이 없으면 미평가로 유지한다.
5. Foam 좌표·validity·episode 동일성은 **이번 비교에서 보고된 불변**으로
   보존하고 재검토하지 않는다. 이 불변을 일반적인 무영향/정확성 보장으로
   바꾸지 않는다. Scope 측정량·후보·tracklet·최초 차단 단계의 새 원인 분석은
   이번 요청에 포함하지 않는다. 요약에 없는 사항은 미확인으로 남긴다.
6. **두 구간표 + FULL 행 수 + 산술 정정 설명**만 반환하면 이 보완은 끝난다.
   기존 packet/reply와 pending review-006을 보존한다. 세 후보의 미채택 판단과
   O2 OPEN / FIELD FAIL은 유지한다. 다음 구현 방향은 Work Plan의 사용자 판단
   지점으로 돌리며, ④ 기반 FULL 전환 복구는 제안 단계다.

이전 집계 정정용 프롬프트 (완료 이력; 다시 보내지 않음):

```text
④ bundle: <기준 번들 경로>
⑦ Local XY bundle: <비교 번들 경로>

docs/40-operations/s11-current-windows-field-qualification.md의
“Priority 3 Local XY saved-output closeout”을 읽고 기존 CSV 집계만 정정해줘.
BASE/Accum의 중복 없는 정규 구간표(신규·소실·Y 변경 포함)와
각 bundle의 FULL_NO_INTERFACE 행 수를 반환해줘.
BASE 순감소 49와 실제 소실 수, Accum 세부 합계 37과 전체 36의 차이를
확인해서 원인이 된 행과 정정 이유만 알려줘. 86%/42% 효과 비율은 철회해줘.
기존 사용자 판정과 Foam 비교 결과를 재사용하고, 디텍터 재실행·튜닝·새 질문은 하지 마.
```

완료 상태 공유용 짧은 프롬프트 (추가 점검 요청 없음):

```text
④↔⑦ Local XY 비교와 CSV 정정은 완료로 마감해줘.
⑦ REGRESSION/NOT_ADOPTED, O2 OPEN/FIELD FAIL을 유지하고 기존 bundle과
review-004~008을 보존해줘. review-006은 미검토 상태 그대로야.
추가 집계·질문·재실행 없이 다음 작업 지시를 기다려줘.
```

## 2. Private source identity

For `windows_sample1_heating_coldstart`, record without exposing the real filename:

- SHA-256;
- byte size;
- width and height;
- FPS;
- duration; and
- Recipe/Glass/ROI settings used for the run.

Use the operator alias only. The source fingerprint strengthens identity; it does not redefine the reviewed timeline.

## 3. Execute the supported production path

Run the current supported Windows production workflow with the candidate named by the Work Plan. Preserve the normal detector, completed-window resolver, publication/report path, and same-frame provenance owners.

Do not:

- tune thresholds or add case-specific configuration during qualification;
- use detector proposals, overlays, prior row counts, graph bridges, or an old bundle as physical truth;
- interpolate/carry a missing numeric observation;
- replay a historical R7–R12 procedure instead of the current candidate contract; or
- convert a diagnostic-only trace field into publication authority.

Collect the current validation contract's required runtime/performance/provenance evidence. General GUI scaling and packaging obligations remain in `manual-gui-windows-checklist.md` when those surfaces are part of the current qualification scope.

## 4. Reconcile all reviewed segments

Report every segment from the reviewed-truth owner individually:

- `WS1-BASE-FULL-PREFIX`
- `WS1-BASE-DRAIN`
- `WS1-BASE-RAPID-REFILL`
- `WS1-BASE-FULL-SUFFIX`
- `WS1-ACCUM-EMPTY`
- `WS1-ACCUM-ENTRY-SPLASH`
- `WS1-ACCUM-FOAM-LAYERED`
- `WS1-ACCUM-POST-FOAM`
- `WS1-ACCUM-DRAIN`

For each segment record sampled coverage, Oil/Foam numeric runs, selected source-Y range/direction where physically reviewable, longest missing/wrong-interface run, relevant lifecycle/owner transitions when available, and `PASS`, `FAIL`, or `NOT_EVALUATED`.

Exact coordinate accuracy is `NOT_EVALUATED` where no reviewed source-Y anchor exists. Presence/absence, material identity, ordering, direction, false-boundary rejection, and same-frame provenance remain valid acceptance dimensions without exact Y anchors.

## 5. Field disposition

A run is not `FIELD PASS` merely because local/canonical tests passed or aggregate coverage improved. Apply the current candidate validation contract plus canonical reviewed truth.

Any supported failure must identify the earliest harmful stage that the available evidence can establish. If the stage cannot be established, record the missing evidence and keep it unknown rather than inventing a causal mechanism.

A field `FAIL` does not authorize another detector revision automatically. Any follow-on behavior change starts from the newly observed failing stage and the current failure registry/logic map under a separately authorized detector task.

## 6. Evidence and closeout

Store completed field measurements under the current `docs/60-evidence/s11/` owner; causal investigation belongs under `docs/50-diagnostics/s11/`. Include the required `## Detector Governance` block from `docs/30-validation/s11-detector-change-governance.md`.

Update `docs/00-project/work-plan.md` only when field disposition, accepted baseline, named blocker/unknown, or next transition changes. Update the Roadmap only if formal milestone state changes. Do not rewrite archived R7–R12 procedures or older field evidence to match the new result.
