# Graph-editing direction handoff — 2026-10-27 (session close)

## Current disposition

S11 is ACTIVE; O2 is OPEN; the Windows field result remains FIELD FAIL. The
[Work Plan](../../00-project/work-plan.md) is the only owner of current state
and authorization. Everything below is committed and pushed to `main`.

- **No production detector default changed.** E4, the contested gate,
  top-exit v3, IFO v2 and fast-rise association stay opt-in and default OFF.
  FIELD FAIL / O2 OPEN and review-006 pending are unchanged.
- **No Windows request is queued.**
- **Managed runs:** 150, all clean.
- **Next free review ID:** review-018.
- **No product direction has changed yet.** The user's proposal below is
  open. It is the first topic of the next session.
- **The earlier handoff of this session,** the
  [fast-fill path handoff](2026-10-27-fast-fill-path-handoff.md), covers E4,
  E2, E1 and OFF-1.

## What this session settled after compaction

| Step | Outcome | Record |
|---|---|---|
| OFF-1 correction | A `full` state node exists only if the raw frame outcome is no-interface (gate 1: absence ≥ 0.58 and ≥ 0.10 over the best boundary), before the lifecycle gate F1 would lift | [OFF-1](../../50-diagnostics/s11/2026-10-27-owner-free-full-review.md#correction-after-compaction-an-earlier-gate-source-desk-check-2026-10-27) |
| FER-1, FULL evidence readout | **E-ABSENT.** No `full` node in 532 local and 1,564 Windows rows. SPL#4 BASE 27.5–63 s stops at gate 1 (absence ≤ 0.545) or gate 2 (FULL ≈ 0.14). F1 as drafted has no evidence | [FER-1](../../50-diagnostics/s11/2026-10-27-full-evidence-readout.md) |
| PSD-1, peer-side desk check of barrier 1 | **NO SEPARATION.** Every peer-position condition also frees R7's protected rows (sample4 Y805–815, sample7 Y384), so E3 is blocked at barrier 1 | [PSD-1](../../50-diagnostics/s11/2026-10-27-peer-side-desk-check.md) |

**What these results mean (agent's judgment, given to the user):**
- Every frame-local handle tried for SPL#4's 2 fps fast fill (E1, E2, E3
  barrier 1, F1) is closed on the traced fields.
- What separates the level from the stale edge is time, and the frame-local
  rules never see it.
- So the agent recommended stopping new mechanism work on the current
  detector.

## The user's new direction (open, to be interviewed)

**What triggered it.** The user compared the Windows reports' graphs with
their source-context images (time × height RGB median,
[`source_context_renderer.py`](../../../src/oil_tracker/adapters/reporting/source_context_renderer.py)).
- The user's verdict on the graphs: "지금 report의 그래프 수준은 프로덕션에
  아예 적용 못하는 수준이고".
- The context images show the level's course far more completely: SPL#4
  BASE fill, FULL and drain diagonal; SPL#1 BASE thin line; SPL#1 Accum dome
  curve.

**The proposal, verbatim:**
> 맥락 이미지 기반이든 어떤 방식이던 그래프를 일단 그려줘. 상단 : 그래프 / 하단 : 맥락
> 이미지 (상하단 순서는 상관없음). 유저가 이 화면에서 그래프를 자유롭고 편하게 수정
> 가능하도록 툴을 쥐어줘. (점과 점을 찍어서 선을 긋고, 선 위의 특정 포인트를 드래그해
> 움직여서 곡선을 만들고, 새로운 선을 추가하고, 메모를 추가하는 등) 결국 유저가 필요한건
> 그래프를 그려내고 판정기준을 만족하는지 판단해서 보고서를 제출하는거거든.

**The user's answers so far:**
1. **Judgment criteria already exist:** "유저가 recipe 생성시 정한 기준선
   대비 상단 유지 등의 조건을 만족하는게 판정 기준이야".
   - In code: `JudgmentRule` per Glass
     ([`recipe.py:77`](../../../src/oil_tracker/domain/recipe.py)) and
     `judge_samples`
     ([`judgment.py`](../../../src/oil_tracker/domain/judgment.py)).
   - The modes are `RECOVERY`, `HOLD_BELOW_ZERO` and `HOLD_ABOVE_ZERO`,
     relative to the Recipe zero line.
   - The rule reads `smoothed_oil_air_level_px_from_zero` and `fill_state`
     (FULL and EMPTY count) with coverage, hold and tolerance fields.
2. **Edit history need not be visible:** "수정 이력이 보일 필요 없어".
3. **First-version scope:** "첫 버전 범위는 나랑 좀 더 의논해보자".

**The user's instruction for the next session:** "새 세션에서 새 버전의 구현
범위와 목적을 나랑 인터뷰해보는걸로 시작하자." The available `grill-me`
Skill fits this interview.

**The agent's view, already given (not decisions):**
- **Complexity drops a lot.**
  - The detector becomes a draft generator.
  - Hard cases become a few edits made with the context image: fast-fill
    FULL, Foam vs Oil, the stale edge.
  - Failures are visible instead of hidden.
- **What stays hard:**
  - point provenance (auto / edited / drawn) in the saved data, even if the
    report does not show history;
  - precision: the report image is compressed (≤ 240 rows, ≤ 360 columns;
    SPL#1 columns are 0.84 s apart), so the tool needs a full-resolution
    image, zoom, the source frame with the line overlaid, and snap-to-edge
    dragging;
  - a curve model with state segments (Oil level, Foam top, FULL, EMPTY,
    unknown);
  - turning the edited curve into samples that `judge_samples` and the
    events can read.
- **Acceptance would change.** It would move from "the detector alone passes
  on Windows" to "the draft plus the user's edits yield a report that meets
  the criteria". That is a product-direction decision for the Work Plan and
  roadmap.
- **CTX-1 becomes optional.** The read-only context-image extraction check
  was proposed earlier. It would now be an optional way to improve the draft,
  not a gate.

**Existing owners to reuse** (look here before adding anything):
- [`ui/result_review_window.py`](../../../src/oil_tracker/ui/result_review_window.py),
  with `ui/widgets/result_review_graph.py`: the graph and video are linked,
  so clicking the graph seeks the frame.
- [`ui/truth_annotation_window.py`](../../../src/oil_tracker/ui/truth_annotation_window.py),
  `ui/truth_annotation_coordinator.py`, `ui/widgets/truth_annotation_canvas.py`
  and [`domain/user_truth.py`](../../../src/oil_tracker/domain/user_truth.py):
  per-frame confirmed / corrected / unusable truth.
- `ui/undo.py`.
- `application/services/review_graph.py` and `graph_axis.py`.
- `application/services/report_presentation.py` and the report template.
- `domain/events.py` and `domain/judgment.py`.

## Interview topics for the next session (a starting list, not decisions)

- **Purpose and user:** who edits, how often, and what "submitted report"
  means.
- **First-version scope:**
  - an Oil line only, or Foam lines too;
  - state segments (FULL, EMPTY, unknown);
  - memos;
  - one Glass or several.
- **The draft source:**
  - the current detector output as is;
  - a context-image extraction;
  - or none (draw from scratch).
- **Precision aids:**
  - full-resolution context image and zoom;
  - the source-frame overlay;
  - snap-to-edge;
  - background-subtracted (per-row temporal median) view.
- **Data:**
  - the curve model (control points, interpolation);
  - provenance stored but not shown;
  - the save format;
  - how the curve becomes samples, and smoothing.
- **Judgment:** reuse `judge_samples` unchanged? How do drawn FULL and EMPTY
  segments map to `fill_state`?
- **Report:**
  - what changes;
  - what the context image shows;
  - no edit history (decided).
- **The fate of S11 and the Windows qualification:**
  - the detector's role;
  - what O2 and FIELD FAIL mean under the new acceptance;
  - which open S11 records to close or freeze.
- **Where it lives:**
  - the existing result review window, or a new window;
  - Windows packaging.

## Photos the user shared (local only, git-ignored)

These are screen photos of Windows reports, kept in closed managed runs under
`sample/output/`. They are not in Git. The bundles stay on Windows.

| Run | File | Content |
|---|---|---|
| `s11-context-image-photos-20261027-001` | `spl4-base-report-graph.jpg` | SPL#4 (sample4) BASE Oil graph. The user named the bundle "top-exit v3 20261022_14048" |
| same | `spl4-base-source-context.jpg` | SPL#4 BASE context image (fill ~24–27 s, FULL ~27–65 s, drain diagonal from ~65 s) |
| same | `spl1-base-report-graph.jpg` | SPL#1 (sample1) BASE Oil graph (PASS; 652 s min, 672 s max) |
| same | `spl1-base-source-context.jpg` | SPL#1 BASE context image (faint thin line ~575–665 s; 0.84 s columns) |
| `s11-context-image-photos-20261027-002` | `spl1-accum-report-graph.jpg` | SPL#1 Accum Oil graph |
| same | `spl1-accum-source-context.jpg` | SPL#1 Accum context image (front ~670–676 s, dome curve 676–785 s) |
| `s11-context-image-photos-20261027-003` | `spl4-accum-report-graph.jpg` | SPL#4 Accum Oil graph (false Oil rows 63–79 s) |
| same | `spl4-accum-source-context.jpg` | SPL#4 Accum context image (white Foam 20–33 s, jagged Foam top falling from 34 s; 0.50 s columns) |

Full paths are
`sample/output/<run>/evidence/<file>` from the repository root. Earlier
review photos are in `s11-review-015-photos-20261027-001`,
`s11-review-016-photos-20261027-001` and `s11-review017-relay-20261027-001`.

## Tools added this session (read-only diagnostics)

- `tests/diagnostics/s11_full_evidence_readout.py` (FER-1). It reads per
  frame where the image FULL evidence stops (gates 1–3). Bundle and local
  modes.
- The earlier tools of this session are listed in the
  [fast-fill path handoff](2026-10-27-fast-fill-path-handoff.md#tools-added-this-session-read-only-diagnostics).

## Working rules confirmed

- Freeze readings before output; disclose conditions written after seeing
  data (PSD-1).
- Windows relays are text with OCR slips; identify runs by run_id and counts,
  and recheck derived counts against listed rows.
- Keep relays and photos in closed managed runs under `sample/output/`.
- Commit and push in logical units without asking. The user decides each
  step.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `OIL-PROJECTION`
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`
- First harmful stage: SPL#4 BASE 2 fps fast fill. `OIL-AUTHORITY` demotes the level (no peer-side handle, PSD-1), and the image FULL evidence never forms (FER-1).
- Existing feature coverage: E4, the contested gate, top-exit v3, IFO v2 and fast-rise association, all default OFF; the E1/E2 drafts and F1 without code.
- Execution scope: a handoff; no run, code or Windows execution in this record.
- Logic-map impact: NONE — a handoff.
- Failure-registry impact: NONE — no new mechanism.
