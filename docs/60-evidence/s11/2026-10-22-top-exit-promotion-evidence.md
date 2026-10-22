# Top-exit v3 promotion evidence — 2026-10-22

**Status:**
- **N class (local negatives):** PASS on all six controls. No control reached a
  top-exit witness or a pending closure, so the closure predicates are still
  unexercised on real video.
- **P and R classes:** no evidence yet. The Windows candidate SPL#4 (the
  user's "sample4") has its truth, windows and entry conditions frozen; it has
  not been run.

The criteria are the
[pre-registered promotion acceptance](../../30-validation/s11-physical-interface-evidence-repair-validation.md#top-exit-v3-promotion-acceptance--2026-10-22);
nothing here changes them. Top-exit v3 stays default OFF; FIELD FAIL / O2 OPEN
are unchanged. Current authority is the [Work Plan](../../00-project/work-plan.md).

## Local negatives (N class) — 2026-10-22

**Truth and Recipes:**
- **User confirmation (2026-10-22):** sample5 (water) and sample7 (milk) start
  EMPTY and never become full, and the shown ellipses are correct. The other
  four controls keep their earlier never-FULL scope.
- **Recipes:** managed run `sample/output/s11-empty-fill-roi-20261022-001`
  froze them before any detector run. The ellipse is the vessel interior from
  the inner rim to the top of the solid base, measured with edge profiles on the
  empty first frame.

  | Control | Ellipse (cx, cy, rx, ry) | Top 27 % band end | Recipe SHA-256 |
  |---|---|---|---|
  | sample5 | 960.5, 593.0, 142.5, 257.0 | Y474.8 | `d6394f9a…2b89de` |
  | sample7 | 1130.0, 600.0, 287.0, 303.0 | Y460.6 | `effd31e1…c9ca9c9c` |

**Runs:**
- **Arms:** IFO v2 in both; top-exit v3 OFF against ON. 2 fps, debug NONE;
  cost-first, RGB and Local XY OFF.
- **Run `s11-top-exit-negatives-20261022-001`** (head `cba4067`): the four
  existing controls plus sample7.
  - sample5 failed before producing any output. Its window ended at the nominal
    duration, 54.855 s, which lies past the last decodable frame (about
    54.82 s).
  - The window end was moved to 54.8 s (`60d6a9d`) before any sample5 output
    existed.
- **Run `s11-top-exit-negatives-20261022-002`** (head `60d6a9d`): sample5
  alone.

| Control | Initial state | Rows | Numeric Oil / Foam | FULL rows OFF / ON | Top-exit FULL rows | Arms equal (raw inputs, rows, events, report) | Pending closures | N1/N2 |
|---|---|---:|---:|---:|---:|---|---:|---|
| sample4, original Recipe | UNKNOWN | 113 | 101 / 26 | 0 / 0 | 0 | Yes | 0 | PASS |
| sample4, Oct 15 interior Recipe | FULL (stress) | 113 | 16 / 76 | 0 / 0 | 0 | Yes | 0 | PASS |
| base_sample_1 | FULL (stress) | 30 | 12 / 0 | 0 / 0 | 0 | Yes | 0 | PASS |
| sample2 | FULL (stress) | 5 | 0 / 0 | 0 / 0 | 0 | Yes | 0 | PASS |
| sample7 (milk) | EMPTY | 90 | 21 / 3 | 0 / 0 | 0 | Yes | 0 | PASS |
| sample5 (water) | EMPTY | 111 | 23 / 4 | 0 / 0 | 0 | Yes | 0 | PASS |

- **The four existing controls** reproduce v3's row counts and top-exit reason
  counts exactly.
- **Summaries:** `…-001/evidence/summary.json` (`d5aca30f…3ac13`) and
  `…-002/evidence/summary.json` (`ca43c875…77b0d6`); the per-control
  `comparison.json` files are kept beside them.

**Verdict: N1/N2 PASS on all six.**

**What it does not show:**
- **No witness or pending closure anywhere.** The closure predicates, including
  the two-frame-blank risk, remain unexercised on real video, as for the
  original four controls.
- **No owner entered the band.**
  - sample5: the selected Oil spans Y604–819 against a band end of Y474.8. The
    settled surface at about Y491 is never selected; the last Oil rows
    (50.5–54.5 s) sit at Y654–696, roughly 160–200 px lower. This is a
    wrong-target observation on a development scene, not scored here.
  - sample7: the selected Oil spans Y635–773 against Y460.6. No Oil row is
    selected after 31.5 s.
- **What it adds:** the IFO-inactive EMPTY-initial path now shows that top-exit
  adds no output when no owner reaches the band.

**Reported, not scored:**
- **Fill cap:** no `FILLED_CAP_VETO` in any control.
- **Initial-state reconstruction (ON arm):**
  - sample5: UNRESOLVED. The continuing run broke on a step above the jump
    limit: the first catch is 8.5 s Y819, the next 20.0 s Y604.
  - sample7: UNRESOLVED.
  - The FULL-stress controls (base_sample_1 CONFLICT, sample2 ACCEPTED) are
    stress conditions, not truth.

## Windows SPL#4 (user alias "sample4") — 2026-10-22

`SPL#4_Cooling_onoff_#2.mp4`, a Windows recording the user calls "sample4". It
is **not** the Mac `sample/sample4.mp4`, which is 56 s long with one Glass. The
user reviewed it by eye and relayed approximate times. Recorded verbatim:

```text
BASE
11s : Oil 유입 시작하지만 glass 최 하단에 약간만 보임
18~19s : 유면은 glass 최하단, glass 표면으로 oil 쏟아지면서 흘러내리는 자국 남음
21s : Oil 빠르게 차오르면서 유면 빠른 속도로 상승
23s : 유면 상승하면서 Foam 발생 시작
24~25s : 빠른 속도로 Foam + Oil 차오르면서 Full 도달
25s 이후 : Foam이 빠른 속도로 위로 밀려 올라감 glass는 가득 찬 Oil과 잔여 Foam의 흔적으로 꽉참 (연기가 가득 찬 것 처럼 교반 작용 일어남)
50s 부근 : 투명도 회복 (25s 이후 계속 Full 유지)
63s : 상단에서 유면 내려오기 시작함 (Full 해제)
65s : 상단에서 내려오기 시작한 유면 위쪽에 Foam 발생
~85s : 상단 Foam이 두꺼워지면서 유면이 밀려 내려옴. Foam은 Full ↔ 해제 반복

Accum
14s : 유체 유입 시작되면서 Foam 발생 (최하단)
~28s : 빠른 속도로 Foam 성장하면서 glass 최상단 도달 (Foam이 Full ↔ 해제 반복)
28s : Full 해제됨 Foam이 아래로 내려오기 시작
~85s : Foam이 위아래로 출렁이면서 아래쪽으로 조금씩 내려옴 (지속적으로 유체 유입 되면서 빠른 속도로 출렁임)
```

The agent then asked five questions: identity, Recipe, window and initial
states, Foam at the top, and timing. The user's answers, verbatim:

```text
1. 아예 다른 영상임
파일명 : SPL#4_Cooling_onoff_#2.mp4
용량 : 53,165,445 바이트 (디스크 할당 53,166,080 바이트)
영상 길이 : 4분 20초
프레임 : 30
해상도 : 1920*1080

2. Recipe 있음 (artifact 포함)
3. 둘 모두 empty에서 시작
4. Full 아님이 정답임, 25~63s은 oil로 가득찬 full
5. 대략적인 구간으로 시도해보고 불충분하면 22–27 s와 61–65 s 구간만 Windows에서 사람 검토로 다듬자
```

**Frozen before any output on this recording** in the
[SPL#4 entry conditions](../../30-validation/s11-physical-interface-evidence-repair-validation.md#top-exit-v3-promotion-acceptance--2026-10-22):

| Glass | Reviewed interval | Class | Frozen window |
|---|---|---|---|
| BASE | EMPTY at 0 s, Oil from about 11 s | Initial state | IFO v2 is inactive, so top-exit acts alone |
| BASE | FULL reached at 24–25 s | **P** | first FULL row in 22.0–27.0 s; none before 22.0 s |
| BASE | FULL, filled with Oil, 25–63 s | P3 hold | FULL or D2b UNKNOWN, no Oil coordinate, from the first FULL row to 61.0 s |
| BASE | Drain from FULL at 63 s | **R** | episode end in 61.0–65.0 s |
| BASE | Not FULL after the drain, including Foam at the top from about 65 s | R2 | no candidate-only FULL row in 65.0–90.0 s |
| Accum | EMPTY at 0 s, never Oil-FULL; Foam at the top from about 28 s | **N** | N1/N2 over 0–90 s |

- **Window:** 0–90 s, as proposed in question 3. The user confirmed the initial
  states and did not object to the window. The timeline ends at about 85 s,
  and 90–260 s stays unseen.
- **Timing:** the approximate windows are scored first. A miss within 2 s
  outside a window triggers a Windows review of only 22–27 s or 61–65 s.
- **Not yet known:** the recording's SHA-256 and decoded frame count, and the
  Recipe's hash and ellipses. The run records them first.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F05`, `S11-F06`, `S11-F08`, `S11-F10`
- First harmful stage: none observed. No control formed a top-exit witness or a pending closure, so the closure stage is NOT_EVALUATED on real video. The sample5 wrong-target Oil rows are a selection observation outside these criteria.
- Existing feature coverage: reuses the initial-FULL/top-exit comparison runner. Its extension adds frozen empty-fill Recipes, an EMPTY initial state and an N1/N2 summary. Also reused: the IFO v2 and top-exit v3 options, production default detector settings and the four existing control Recipes. The EMPTY-initial path, where IFO is inactive, is exercised for the first time. Windows "sample4" is a user visual timeline only.
- Execution scope: two local managed runs (`cba4067`, `60d6a9d`) over six controls at 2 fps with debug NONE, plus a frozen-ROI run before them. No Windows execution, private media, human review beyond the user's confirmations, tuning or post-result rule change. sample5's window end was corrected before any sample5 output existed. SPL#4 is recorded from the user's visual timeline and answers only; its windows were frozen before any detector run on it.
- Logic-map impact: NONE — evidence only; detector code and owners are unchanged, and the runner is diagnostics.
- Failure-registry impact: NONE — no new mechanism or failure; the unexercised closure is a named limit, not a result.
