# OTR-1 — FULL observable-top design review (B)

**Status: REVIEW COMPLETE — D1, D1b, D2 and D3 DECIDED by the user ([decision record](#decision-record--2026-10-21)).**
The [§6 ④ trace receipt](#6-windows-trace-receipt--2026-10-21) is recorded.
- **27 % rules:** not involved on Windows BASE.
- **Selection:** the last selected row is Y352; at 673.0 s an admitted Y329 is
  not selected.
- **Evidence:** from 673.5 s no proposal exists in Y243–339.
- **Decided top-exit design:** would not change ④ BASE.

A human visibility check is proposed before implementing. Desk review
only: source reading, closed records, the retained LBT-1 CSV and one geometry
computation with the real mask builder on retained local Recipes. No detector run,
flag, tuning or Windows request was sent. Base HEAD `b9ff06b`. Current authority:
[Work Plan](../../00-project/work-plan.md). Context:
[FULL observable-top handoff](../../60-evidence/s11/2026-10-20-full-observable-top-handoff.md).

## Summary

1. **Every detector site uses the configured ellipse.** The top is
   `center_y − radius_y` and the height is `2·radius_y`. No transition reads the
   effective-mask top or a physical top. The mask enters only indirectly: candidates
   and the image FULL statistic exist only inside it.
2. **The phase lifecycle never publishes FULL.** `_constrain_layer` reduces a frame
   with an empty allowed set to a single UNKNOWN node, which also drops the image
   `full` node. This covers `INITIAL_FULL_BARRIER`, `FILLED_CAP_VETO` and
   `FILL_SPAN_MATERIAL_VETO`
   ([`oil_interface_selector.py:540`](../../../src/oil_tracker/adapters/vision/oil_interface_selector.py)).
   A FULL row comes only from two routes:
   - raw `oil_no_interface_full_likelihood ≥ 0.58` while the allowed set is
     unconstrained or non-empty;
   - the opt-in top-exit route.
3. **The two failures come from different mechanisms.**
   - **sample4 (LBT-1 G):** the 27 % fill confirmation closes a cap at 54.5 s.
     The retained LBT-1 trial CSV publishes **UNKNOWN_REVIEW** at 54.5–56 s, so
     the harm is Oil lost under a false cap, not false FULL rows. The
     user-approved sample4 truth is FOAMING_VISIBLE at 49 s and 56 s (S4-04/S4-05);
     the Glass is never FULL.
   - **Windows BASE ④:** sampled ④ records at 662.5–664.5 s and 721/723 s show
     the motion runtime still in `filled_barrier / INITIAL_FULL_BARRIER`. Oil
     appears only through IFO v2 `observed_interface`. If this also holds at
     672.5–675 s, BASE cannot reach the 27 % fill or refill closures. Top-exit is
     then the only FULL route, and it is blocked three times: it is OFF in ④, its
     endpoint is unreachable, and no selected rise goes above Y352. The
     [§6 receipt](#6-windows-trace-receipt--2026-10-21) confirms this for every
     frame. It also finds no proposal in Y243–339 from 673.5 s.
4. **sample4 Y808 is a different Recipe.** It is the October 15
   agent-selected *interior comparison Recipe* `(595, 842, 37, 34)`, not
   `sample/sample4.oilrecipe` (Y798). Neither is a human-confirmed physical top.

## 1. Where the top geometry decides a transition

### Reference values

sample4 and base_sample_1 were computed with `build_mask_bundle` on retained
Recipes. Windows BASE values come from the transferred
[preflight receipt](../../60-evidence/s11/2026-10-16-top-exit-full.md#windows-geometry-preflight-received--condition-failed).

| Input | Configured top | H | 27 % band end | 40 % release end | Top-exit tolerance | Mask top |
|---|---:|---:|---:|---:|---:|---:|
| sample4 Recipe (P5, SOI…LBT-1, truth) | 798 | 104 | 826.1 | 839.6 | 1.248 | 802 |
| sample4 Oct 15 interior Recipe | 808 | 68 | 826.4 | 835.2 | 1.000 | 811 |
| base_sample_1 | 218 | 296 | 297.9 | 336.4 | 3.552 | 230 |
| Windows BASE (④) | 211.6 | 772.2 | 420.1 | 520.5 | 9.267 | 243 |

Levels relative to the configured top (0 = top, 1 = bottom):
- **sample4:** the reviewed level Y829–844 sits at 0.30–0.44. The LBT-1 unit top
  B was Y820 at 54.5 s (0.21).
- **Windows BASE:** the last selected Y352 sits at 0.18; the mask top Y243 at 0.04.

### Sites that decide a transition

Line references are to current source. Ratios come from
[`OilObservationResolverConfig`](../../../src/oil_tracker/adapters/vision/oil_observation_resolver.py)
and are passed to the phase and selector policies (`_material_phase_policy`,
`_interface_selector_policy`).

| # | Site | Geometry test | Transition it decides | What is published |
|---|---|---|---|---|
| T1 | `_fill_confirmation_profile` ([lifecycle:1909](../../../src/oil_tracker/adapters/vision/oil_phase_lifecycle.py)); `entrance_band_ratio` 0.27, `completed_fill_min_span_ratio` 0.20 | Last chain row ≤ top + 0.27H; rise ≥ 0.20H; agreement ≥ 0.60; plus an independent anchor, or (initial EMPTY) a lower-entrance strong motion | OPEN/FILLING → FILLED_BARRIER: `FILL_SPAN_CONFIRMED`, or `FILL_SPAN_MATERIAL_VETO` if the last row is vetoed (:945–966) | While the terminal owner stays visible and unvetoed: `FILL_OWNER_AT_ENTRANCE`, allowed {owner} (:1051–1061). After that: `FILLED_CAP_VETO`, allowed ∅ → **UNKNOWN, not FULL**. Only T5 lifts it. **This is LBT-1 G** |
| T2 | `_drain_refill_closure` (:2164), R21 same owner | Row ≤ top + 0.27H; rise from the drain low ≥ 0.20H; recent upward progress and agreement; anchor or strong motion; strict material | DRAINING → FILLED_BARRIER, `DRAIN_REFILL_CLOSURE_CONFIRMED` (:1207) | Same as T1 |
| T3 | `_drain_refill_handoff` (:2197), R21 fresh owner | Same band and span; anchor **and** strong motion | DRAINING → FILLED_BARRIER, `DRAIN_REFILL_HANDOFF_CONFIRMED` (:1311) | Same as T1 |
| T4 | `_chain_is_dynamic_fill_owner` (:1621), and the lower-entrance branch of T1 | Origin ≥ top + 0.73H (initial EMPTY), or central 0.27–0.73 with a motion trajectory | OPEN → FILLING owner admission (start of a fill) | Oil of that owner |
| T5 | `_drain_release_evaluation` (:2066); `drain_entrance_ratio` = `completed_fill_release_ratio` 0.40 | Row entrance (minimum member Y) ≤ top + 0.40H; downward; progress ≥ 0.025H; agreement ≥ 0.60; material | FILLED_BARRIER / initial barrier → DRAINING, `DRAIN_RELEASE_CONFIRMED` (:1091) | Oil of the release owner |
| T6 | `_recovery_seed_allowed(stage="initial_full")` (:2950) | Entrance ≤ top + 0.40H | Seed of the R19 initial-FULL recovery chain → DRAINING | Same as T5 |
| T7 | `_edge_transition_cost` ([selector:328](../../../src/oil_tracker/adapters/vision/oil_interface_selector.py)); `entrance_band_ratio` 0.27 | Oil row in the top 0.27H is cheap to switch to or from `full`; bottom 0.27H for `empty` | Path choice between Oil and an image FULL/EMPTY node. The node exists only if raw likelihood ≥ 0.58 and the allowed set is not ∅ | FULL/EMPTY rows from image evidence |
| T8 | `_initial_score` (selector:252), **literal** 0.27/0.73 | First-node score under a confirmed initial FULL/EMPTY | Start of the selected path | — |
| T9 | `close_top_exit_full` ([top-exit:47–49, :135](../../../src/oil_tracker/adapters/vision/oil_top_exit_full.py)), opt-in | Last witness row within max(1, 0.012H) of the configured top; then usable, unopposed absence | After selection, UNKNOWN → coordinate-free FULL (`OIL_TOP_EXIT_FULL`). It resets on any phase-admitted Oil, EMPTY evidence, ambiguity or an unusable frame, and cannot resume | **The only FULL route that survives a cap.** OFF by default; endpoint unreachable on Windows BASE |
| T10 | `reconstruct_initial_state` ([initial_state_reconstruction.py:139–167](../../../src/oil_tracker/application/services/initial_state_reconstruction.py)); 0.32/0.68 in [`oil_boundary_topology.py`](../../../src/oil_tracker/domain/oil_boundary_topology.py) | First two numeric Oil samples checked against the confirmed prior | Report-level FULL/EMPTY label for the leading unresolved interval | Report context, not CSV |

### Related sites that decide no Oil transition

- **Image FULL likelihood** (`_no_interface_evidence`,
  [`oil_shadow_observations.py:2159`](../../../src/oil_tracker/adapters/vision/oil_shadow_observations.py)):
  darkness × uniformity over the effective mask. It uses the observable *area*,
  not a top coordinate.
- **Foam `FOAM_REACH_TOP`** (≤ 0.12, `foam_episode_resolver.py:646–649`): a Foam
  event only.
- **Margin-adjusted top or height:** `analysis_top_y` in `graph_axis.py:46–47`,
  the capture-jump scale in `detection_processing.py:145`, and
  `preflight.py:268`. These are presentation and diagnostics only. They are the
  only places that already treat the mask-equivalent top as "the analysis top".
- **Tracklet policy:** uses top and height only as scale (progress, row tolerance).
- **Dead helper:** `_relative_y` in `oil_observation_resolver.py:2077` has no caller.

### Observations

- Five "near the top" constants are in use: 0.27 (T1–T3, T7), the literal
  0.27/0.73 (T8), 0.32/0.68 (T10), 0.40 (T5–T6) and 0.012H (T9). All are relative
  to the configured ellipse, which can include rim or glass that cannot be
  measured.
- T1–T3 decide a **cap** (Oil suppressed, published UNKNOWN). T9 decides a
  **published FULL**. Today these are different jobs done by different rules.
- No IFO v2 code (`_observe_initial_full_interface`) reads top geometry.

## 2. sample4: Y808 versus Y798

| Recipe | SHA-256 | Ellipse (cx, cy, rx, ry) | Top | Mask top | Used by |
|---|---|---|---:|---:|---|
| `sample/sample4.oilrecipe` | `53688394…b849` | 595, 850, 52, 52 | 798 | 802 | sample4 truth (snapshot hash), P5 bundle (same geometry; snapshot `655cfd92…`), SOI, HPA, CAF, LBQ, LBT |
| Oct 15 interior comparison Recipe, `sample/output/s11-initial-full-roi-20261015-001/evidence/inputs/sample4.oilrecipe` | `4cecd335…9b66` | 595, 842, 37, 34 | **808** | **811** | October 15 initial-FULL and October 16 top-exit local replays only |

`prepare()` in `tests/diagnostics/s11_initial_full_comparison.py` writes the
second Recipe. The
[ROI preparation](2026-10-15-initial-full-comparison.md#roi-preparation) calls it
an agent-selected inner-glass geometry, not a physical boundary label. The
top-exit verification table says "sample4, retained interior Recipe", but its
geometry table omitted that name. The arithmetic: 842 − 34 = 808; the tolerance
is max(1, 68 × 0.012 = 0.816) = 1, as recorded; the computed mask top is 811.

Consequences:
- Use Y798/H104 for every SOI-line and LBT-1 number. Y808/H68 belongs only to the
  October 15–16 local replays.
- The 27 % band ends near Y826 in both Recipes by coincidence. The span threshold
  (20.8 px vs 13.6 px) and the tolerance differ.
- Neither top was reviewed by a human. The October 15 note found rim pixels inside
  the original mask at the *bottom* (Y880/882/887); the top edge was not reviewed.

## 3. Windows BASE: the Y352 gap

**Recorded facts:**
- ④ initial state: BASE FULL / Accum EMPTY, with IFO v2.
- The last selected Oil before the gap is Y352 at f16124 / 672.5 s. Output is
  UNKNOWN from about 673.01 s.
- The mask top is Y243 and the configured endpoint band ends at Y220.9.
- Truth ([reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#base-timeline-correction--2026-10-15)):
  refill 652–674 s, FULL somewhere in 674–675 s, FULL from 675 s.
- Sampled ④ motion phase: `filled_barrier / INITIAL_FULL_BARRIER` at
  662.5–664.5 s, and at 721/723 s (721 s published Y694 through `observed_interface`)
  ([October 15 records](2026-10-15-initial-full-comparison.md#final-output-and-confirmation-reply-received)).

**Not established:** whether Y352 is the real interface. The ④ selections do not
form one verified rise: 662.5 s Y409, then 663.5 s Y418 on a different tracklet,
then 672.5 s Y352. The truth record also keeps a historical 674 s / Y435 estimate
that was never qualified. The fill speed near the top is therefore unknown.

| Hypothesis | Mechanism | Signature in the saved trace |
|---|---|---|
| H1 barrier | After 672.5 s no IFO v2 row qualifies; `INITIAL_FULL_BARRIER` with allowed ∅ → UNKNOWN | Motion phase `filled_barrier / INITIAL_FULL_BARRIER`; IFO evaluated with qualifying []; candidates in Y243–352 exist but fail admission, compatibility or authority |
| H2 evidence | No proposal above Y352 (F02) | No `oil_air` candidate with Y < 352 in raw `candidates[]` |
| H3 27 % closure | A refill or fill closure fired (T1–T3) | Reason `DRAIN_REFILL_*`, `FILL_SPAN_*` or `FILLED_CAP_VETO` |
| H4 selection | The phase admits a row, but a later stage removes it | `sequence_stage_best_path_kind = oil`, then `unknown` after the continuation or spike stage |

Under H1, image FULL cannot publish FULL in the suffix whatever its likelihood,
because the allowed set is ∅. Table C counts both values.

## 4. Decisions for the user

### D1 — what "observable top" means for each Glass

| Option | For | Against |
|---|---|---|
| **A. Effective-mask top** (ellipse + margin, rasterized) | No new input; reachable by construction (no candidate can exist above it); the graph axis already calls it the analysis top | It marks where measurement stops, not where the Glass is full. With margin 0.08 the unmeasured top band is 0.04H (31 px BASE, 4 px sample4). FULL would mean "the liquid left the measured region", so a slow fill could be called FULL while still below the physical top. Changing margin would silently change FULL. It lifts the existing rule against mask-edge substitution, which is the user's call. It fixes neither G nor the Y352 gap alone |
| **B. Human-confirmed physical top**, stored per Glass | Keeps FULL's current physical meaning; can be checked against Windows truth; separates physical state from measurement | Needs a new per-Glass input (Recipe field and UI, or a reviewed-truth record) and a review of every Glass (sample4, BASE, Accum, base_sample_1, sample2). The physical top is usually above the mask (BASE 211.6 vs 243), so top-exit still needs a rule that bridges the last observable row to the physical top. That bridge is option C |
| **C. Both:** the physical top defines FULL; the mask top is the reachable endpoint; a human confirms for each Glass that the band between them cannot hold a stopped interface | Honest about both values; reachable; FULL keeps its physical meaning. The confirmation can be a yes/no on the existing ellipse and margin, with no new coordinate | One confirmation per Glass. A timing error remains while the liquid crosses the band; it is unknown for BASE because the near-top fill speed is unknown (§3) |

**D1b (follows D1): what moves to the new top?**
- **Endpoint only:** T9 plus whatever D2 adds.
- **Everything:** every top-relative ratio (T1–T8, T10) and the height scale.

Moving everything changes fill onset, releases, selector costs and spans at once,
which is the F05/F08 recurrence area.

**Agent lean (not binding):** C with a yes/no per Glass, and endpoint only. It
keeps FULL physical without a new coordinate field, and it is the smallest change
that makes T9 reachable.

### D2 — does top-exit replace the 27 % rule, or add to it?

T1–T3 make a cap; T9 publishes FULL. The choice is whether one rule should do both.

| Option | For | Against |
|---|---|---|
| **R. Replace:** FILLED_BARRIER entry (T1–T3) needs a top-exit (the owner reaches the D1 top, then usable, unopposed absence) | Fixes G in principle (sample4 never reaches Y798–802). One FULL definition for cap and publication | No cap if the rising interface vanishes below the top, which is exactly the Windows gap. After a real fill, lower false anchors (BASE 721 s class) would no longer be capped: the F05 FULL-suffix false Oil (R17: 91 rows). Also changes Accum (initial EMPTY) and UNKNOWN-start BASE runs. Largest change |
| **S. Add:** keep T1–T3; top-exit becomes the FULL publication route | Smallest change; existing cap protections stay | G remains: sample4 54.5–56 s stays UNKNOWN under a false cap. "Full" means one thing to the phase and another to publication. On ④-like runs nothing changes until D3 shows a selected rise to the top |
| **T. Split:** proximity (T1–T3) opens only a *provisional* cap. A bounded same-owner (or qualified successor) observation below the band can withdraw it. Top-exit or image FULL makes it final. A final cap stays irreversible except by a T5 release | Can address G without losing the post-exit cap; keeps the deliberate irreversibility after a real exit | A new reversal rule in the F05/F08 area the handoff warns about. Needs its own two-sided controls: sample4 G, the Windows FULL-suffix false anchors, and Accum fill |

**D2b: what ends a top-exit FULL?**
- **Today (T9):** any phase-admitted Oil row resets it. The BASE FULL suffix
  would end at the first admitted false row (the 721 s class) and could not
  resume.
- **Alternative:** FULL persists under the cap until a qualified T5 drain
  release. This matches the truth (FULL until 780 s) and reuses the cap's existing
  protection, but it no longer reports a visible row inside the suffix.

**Dependency.** If H1 holds, T1–T3 cannot run for ④ BASE (initial FULL). D2
then changes sample4, Accum and UNKNOWN-start runs, not ④ BASE. The Windows FULL
path is D1 + D2b + D3, and G is a separate fill-geometry problem.

**Agent lean (not binding):** S plus D2b persistence for the Windows FULL route.
Treat G as its own follow-up, considering T, because it is a different mechanism
from the Windows miss. Decide D2 after D3 stage 1.

### D3 — how to investigate the Y352 gap

**Is it in the saved ④ trace? Yes, by source.**
- The ④ trace is `trace=full` (Accum 601/601 records,
  [ATG-1](2026-10-20-accum-texture-gate.md)). At FULL level the capture policy
  records every sample.
- Each record holds:
  - raw `candidates[]`;
  - raw `state.oil_no_interface_*`;
  - the final `sequence` snapshot: `sequence.state.sequence_*` (phase, reason,
    stage kinds, selected tracklet, and phase diagnostics including
    `initial_full_observation`, `allowed_tracklet_ids`, `release_*` and
    `recovery_*`);
  - `sequence.candidates[]` (authority, phase identity, tracklet admission and
    failure, reject stage).
- Not stored: the predicate breakdown of the R21 refill closure (only its
  resulting reason), and the true interface position, which needs a human review.

| Option | For | Against |
|---|---|---|
| **(a) Direct read** by the Windows agent, using the key paths below | No new code; fastest; the 721 s investigation used this style | Risk of parsing or transcription error; no recompute self-check |
| **(b) Freeze a small read-only extractor first** (ATG-1 style), then send a ZIP | Reproducible; can self-check | Needs a diagnostic-tool commit and tests before sending |
| **(c) Human review first:** visible Glass top and last visible interface, BASE 672.5–675.5 s | Answers the physical question that D1-B/C needs | Without (a)/(b) it is unknown whether candidates exist. It uses a review ID; review-011 is reserved for the layered-Foam line |

**Agent lean (not binding):** (a) now. Do (c) only if D1 is B or C, choosing the
review ID at that time.

## Decision record — 2026-10-21

**D1 (user):** the analysis ellipse **is** the Glass region. The user draws its
top at the end of the Glass. This is part of the existing ROI setup, not a new
step.

| Quantity | Meaning |
|---|---|
| Physical top | Configured ellipse top `center_y − radius_y`. FULL keeps its physical meaning; T1–T10 already use this top |
| Observable limit | Effective-mask top, `margin_ratio × radius_y` below the physical top. This is the last row any candidate can occupy (BASE Y243, 31 px band; sample4 Y802, 4 px band) |
| FULL precision | The top band. A top-exit FULL means the level has entered the band that cannot be measured |

What this settles:
- **Option C's per-Glass confirmation is the existing ROI drawing.** No new
  Recipe field, checkbox or separate review is needed.
- **The earlier rule is met.** The mask edge does not replace the physical top;
  it only marks how far the rise can be seen below that top.

Caveats:
- **An ellipse drawn smaller than the Glass breaks the contract.** Top-exit would
  then report FULL when the liquid leaves the region, while the Glass continues
  above. The ROI editor text does not state the contract yet; making it explicit
  is a possible UI-text follow-up.
- **sample4's original ellipse does not follow the Glass at the bottom.** The
  October 15 review found the rim (Y880/882/887) inside its mask. That Recipe is
  therefore weak evidence for top behaviour. sample4 never reaches FULL in truth,
  so this does not block the Windows question.
- **The Windows Y352 gap is unaffected.** It is 109 px below the observable limit,
  so D3 remains the first evidence step.

**Also decided by the user (2026-10-21), as proposed:**
- **D1b:** move only the top-exit endpoint, to the observable limit. All other
  top-relative ratios stay on the ellipse.
- **D2:** S — keep T1–T3 as the cap and add top-exit as the FULL publication
  route. Under D2b, a top-exit FULL persists under the cap until a qualified T5
  drain release. G is a separate follow-up.
- **D3:** (a) — the user forwards the §5 request to the Windows agent.

Nothing is implemented yet. The design and tests for D1b/D2 follow after the D3
tables are received, because they show whether a selected rise reaches the
observable limit at all.

## 5. Windows agent request — approved 2026-10-21; the user forwards it

This prompt is for the **Windows agent**. It reads the existing ④ bundle only.

```text
S11 BASE 상단 관측 공백 확인 — 저장된 ④ trace 읽기 전용 추출이야.
재실행·새 bundle·튜닝·비교 실행·새 사람 검토는 하지 마. 파일은 수정·이동하지 마.

목적: ④ FULL+ON v2 bundle의 BASE에서 마지막 선택 Oil Y352(f16124, 672.5초) 이후
mask 상단 Y243까지 출력이 없던 구간이 어느 단계에서 멈췄는지 저장값만 옮겨 적는다.
Y352가 실제 계면인지는 판단하지 않는다.

1. ④ bundle의 debug/debug_index.json과 debug/debug_trace.jsonl만 읽는다.
   index의 records[] 중 glass_name이 BASE인 항목을 timestamp_sec로 찾고,
   byte_offset/byte_length로 해당 줄만 읽는다. 짧은 Python 읽기 코드는 써도 되지만
   결과 파일은 만들지 않는다. Glass 이름이 다르면 실제 이름만 바꾼다.
   경로 표기: Q = sequence(최종 결과), S = sequence.state,
   D = sequence.state.sequence_material_phase_diagnostics, R = record 최상위(현재 프레임 원시값).

2. 머리줄: run_id | trace_level | BASE record 수.

3. 표 A — 670.0~678.0초, 0.5초 간격 17개 시각. 각 시각에서 ±0.3초 안의 가장 가까운
   record를 쓰고, 없으면 NOT_CAPTURED. 인접 시각으로 채우지 않는다. 시각당 한 줄:
   time | frame_index | Q.fill_state | Q.positions.raw_oil_y |
   S.sequence_resolved_kind |
   S.sequence_stage_best_path_kind/_y | S.sequence_stage_continuation_bound_kind/_y |
   S.sequence_stage_spike_suppressed_kind/_y | S.sequence_stage_completed_fill_kind/_y |
   S.sequence_material_phase | S.sequence_material_phase_reason |
   D.allowed_tracklet_ids |
   D.initial_full_observation.evaluated / .motion_phase / .motion_reason / .qualifying_tracklet_ids |
   D.release_stage | D.recovery_stage | S.sequence_selected_tracklet_id |
   R.state.oil_no_interface_full_likelihood | R.state.oil_no_interface_reason |
   Q.flags 중 R17_* / SEQUENCE_* / OIL_* 만

4. 표 B — 672.5, 673.0, 673.5, 674.0, 674.5, 675.0, 675.5초(표 A와 같은 record).
   - 각 시각: R.candidates[] 중 kind=oil_air이고 canonical_y < 352인 후보 수.
   - 각 시각: sequence.candidates[] 중 kind=oil_air이고 canonical_y < 352인 항목을
     배열 순서(점수순) 상위 8개까지, 그리고 총 개수.
     열: time | source | canonical_y | authority | authority_reason | phase_identity |
     tracklet_id | tracklet_lifecycle | tracklet_admitted | tracklet_failure_reason |
     tracklet_incompatible | tracklet_recent_direction | tracklet_recent_net_progress_px |
     reject_stage | selected
   - 672.5초의 선택 행(Y352) 하나를 같은 열로 추가한다.
   - canonical_y < 243인 항목은 비고에 "mask 밖"이라고만 적는다.

5. 표 C — 675.0~720.5초 BASE record 요약(개수만, 해석 없이):
   - record 수, NOT_CAPTURED 수
   - S.sequence_resolved_kind 별 개수
   - (S.sequence_material_phase, S.sequence_material_phase_reason) 조합별 개수, 상위 6개
   - (D.initial_full_observation.motion_phase, .motion_reason) 조합별 개수
   - R.state.oil_no_interface_full_likelihood 최소/중앙값/최대, 0.58 이상 개수
   - R.state.oil_no_interface_reason 별 개수

6. 머리줄과 표 A/B/C를 텍스트로 그대로 돌려준다. 값은 고치거나 반올림하지 않는다.
   키가 없으면 MISSING, 값이 null이면 null로 구분한다. 결론은 "표 A에서 673초 이후
   motion_reason이 무엇인지" 같은 관찰 한 줄만 쓰고, 원인 판정이나 수정 제안은 하지 않는다.
   영상·이미지·JSON·CSV 원본은 보내지 않는다. 반환 후 멈춘다.
   FIELD FAIL / O2 OPEN, review-006 pending, ⑧ NOT RUN 상태는 바뀌지 않는다.
```

The returned tables are transferred Windows evidence. Record them in a new
section of this file.

## 6. Windows trace receipt — 2026-10-21

**RECEIVED.** The user relayed the Windows agent's read-only extraction made with
the §5 request (`0ddcd28`). This is transferred evidence: no private file was
inspected on the Mac, and no run, new bundle, tuning or human review occurred.

- **Identity:** run `a9ccece3-49bf-47af-a570-b1ca6e9777a4`, `trace_level=full`,
  BASE 601 records.
- **Read:** `debug/debug_index.json` and `debug/debug_trace.jsonl` only, by byte
  offset.

### Table A (condensed)

These columns were constant in all 17 rows:
- `release_stage = initial_full_drain_release` and `recovery_stage = initial_full`;
- IFO `evaluated = True`, with motion `filled_barrier / INITIAL_FULL_BARRIER`;
- `R.oil_no_interface_full_likelihood = 0.0` and `R.oil_no_interface_reason = not_available`.

Every stage kind and Y (best path, continuation bound, spike suppressed, completed
fill) equals the resolved kind and Y.

| Time (frame) | Final state / Y | Resolved | Phase / reason | Allowed = IFO qualifying | Selected | Flags |
|---|---|---|---|---|---|---|
| 670.0 (16064) | PARTIAL_VISIBLE / 384 | oil | observed_interface / INITIAL_FULL_INTERFACE_OBSERVED | [000366:0319] | 000366:0319 | OIL_DIRECTION_UNCONFIRMED, R17_RESOLVED_OIL, R17_TRACKLET_CONTINUING, SEQUENCE_RESOLVED_OIL, SEQUENCE_SAME_FRAME_CANDIDATE |
| 670.5 (16076) | PARTIAL_VISIBLE / 377 | oil | same | same | same | same |
| 671.0 (16088) | PARTIAL_VISIBLE / 369 | oil | same | same | same | same |
| 671.5 (16100) | PARTIAL_VISIBLE / 362 | oil | same | same | same | same |
| 672.0 (16112) | PARTIAL_VISIBLE / 350 | oil | same | same | same | same |
| 672.5 (16124) | PARTIAL_VISIBLE / 352 | oil | same | same | same | same |
| 673.0 (16136) | UNKNOWN_REVIEW / null | unknown | observed_interface / INITIAL_FULL_INTERFACE_OBSERVED | [000366:0319] | — | R17_INITIAL_STATE_CONTEXT_ONLY, R17_OBSERVATION_UNAVAILABLE, SEQUENCE_UNAVAILABLE |
| 673.5 (16148) | UNKNOWN_REVIEW / null | unknown | filled_barrier / INITIAL_FULL_BARRIER | [] | — | same as 673.0 |
| 674.0–678.0 (16160–16256, 9 rows) | UNKNOWN_REVIEW / null | unknown | filled_barrier / INITIAL_FULL_BARRIER | [] | — | as 673.0 plus R17_MATERIAL_PHASE_BARRIER |

### Table B (`sequence.candidates[]`, kind `oil_air`, Y < 352)

| Time | Raw count | Rows: source Y / authority / identity / tracklet, lifecycle, admitted / reject stage |
|---|---:|---|
| 672.5 | 4 | `material_path` 322 / — / — / — / TOP_K_PRUNED_OR_HARD_INVALID · `phase_transition_scan` 336 / ANCHOR_ELIGIBLE / direct_interface / 000384:0333 provisional 0, INSUFFICIENT_NET_PROGRESS, recent dir +1, 17 px / INSUFFICIENT_NET_PROGRESS · `material_path` 338 / CONTINUATION_ELIGIBLE / direct_interface / 000384:0333, same / INSUFFICIENT_NET_PROGRESS · `material_path` 287 / — / — / — / TOP_K_PRUNED_OR_HARD_INVALID |
| 673.0 | 2 | `material_path` 343 / — / TOP_K_PRUNED_OR_HARD_INVALID · **`phase_transition_scan` 329 / CONTINUATION_ELIGIBLE / continuation_only / 000366:0319 continuing, admitted 1, incompatible 0, recent dir −1, 48 px / GLOBAL_PATH_OR_RUN_BOUND, not selected** |
| 673.5 | 3 | `distributed_sobel_path` 340, `phase_transition_scan` 348, `material_path` 349 — all TOP_K_PRUNED_OR_HARD_INVALID |
| 674.0 | 3 | `phase_transition_scan` 349, `material_path` 349 — TOP_K_PRUNED_OR_HARD_INVALID · `calibrated_high_recall` 351 / CONTINUATION_ELIGIBLE / continuation_only / 000384:0333 provisional 0, INSUFFICIENT_NET_PROGRESS, recent dir +1, 17 px / MATERIAL_OWNERSHIP_BARRIER |
| 674.5 | 2 | `phase_transition_scan` 346, `material_path` 347 — TOP_K_PRUNED_OR_HARD_INVALID |
| 675.0 | 2 | `phase_transition_scan` 346, `material_path` 346 — TOP_K_PRUNED_OR_HARD_INVALID |
| 675.5 | 2 | `material_path` 348, `phase_transition_scan` 344 — TOP_K_PRUNED_OR_HARD_INVALID |

The 672.5 s selected row was reported as Y352, CONTINUATION_ELIGIBLE /
continuation, continuation_only, `000366:0319` continuing, selected.

### Table C (675.0–720.5 s)

| Item | Result |
|---|---|
| Records | 91; one grid point NOT_CAPTURED |
| Resolved kind | unknown 91 |
| Phase / reason | `filled_barrier / INITIAL_FULL_BARRIER` 90; `observed_interface / INITIAL_FULL_INTERFACE_OBSERVED` 1 |
| IFO motion | `filled_barrier / INITIAL_FULL_BARRIER` 91 |
| Image FULL | Full likelihood min, median and max 0.0; `not_available` 91 |

### Transcription notes (values kept as reported)

- **Y287 at 672.5 s was marked "mask 밖".** By the stated rule (Y < 243) it lies
  inside the mask, so the annotation is disregarded.
- **The 672.5 s selected row** has source `sequence_selected` and null lifecycle
  fields. It appears to be built from `S.sequence_selected_*`, not from a
  `sequence.candidates` entry.
- **Table C threshold:** the agent counted ≥ 0.50 instead of the requested ≥ 0.58.
  With a maximum of 0.0 this changes nothing.
- **Selected-tracklet column:** absent in rows from 673.0 s onward, where nothing
  is selected.
- **The one NOT_CAPTURED grid point** in Table C was not investigated.

### Findings

| # | Finding | Evidence |
|---|---|---|
| R1 | **H3 excluded.** The 27 % rules (T1–T3) never acted on ④ BASE. The motion runtime stays `INITIAL_FULL_BARRIER` throughout, so no drain release, fill closure or refill closure occurs | 17/17 Table A rows and 91/91 Table C records |
| R2 | **The selected rise is the IFO v2 owner `000366:0319`**, which reaches Y384 → Y350 (672.0 s) → Y352 (672.5 s). Its last selected row is 0.18H below the Glass top and 109 px below the observable limit | Table A |
| R3 | **H4 holds for one frame.** At 673.0 s the same owner is still admitted, allowed and IFO-qualifying at **Y329**, with recent upward progress of 48 px. The best path is nevertheless unknown (`GLOBAL_PATH_OR_RUN_BOUND`). The trace does not say whether its confidence failed publishability or the path cost preferred unknown. Even if selected, Y329 is 86 px below the limit | Tables A and B |
| R4 | **H2 holds from 673.5 s.** No Oil proposal exists with Y < 340 during 673.5–675.5 s. The remaining proposals cluster at Y340–351 and are top-K pruned or hard-invalid. One exception is the 674.0 s Y351 row on a provisional downward tracklet, `000384:0333`, rejected by the ownership barrier. During the reviewed FULL transition, nothing is proposed in the top 97 px of the observable region (Y243–339) | Table B |
| R5 | **Image FULL evidence is absent, not merely weak.** No no-interface evidence object is produced, so an unconstrained allowed set would still not publish image FULL here | `not_available`, likelihood 0.0 in 17 + 91 records |
| R6 | **Design note for D2 (not a tuning proposal):** T9's window resets on any downward step. The 672.0 → 672.5 s move is 2 px downward (350 → 352), so a top-exit window would restart at 672.5 s | Table A |

### Consequence for the decided D1b/D2

Implementing D1b and D2 as decided would not change ④ BASE.
- The endpoint (Y243 ± 9.3) is never approached: the closest admitted row is
  Y329 and the last selected row is Y352.
- The binding gap is upstream of top-exit:
  - one selection loss at 673.0 s (`OIL-SELECTOR`);
  - no proposal in Y243–339 from 673.5 s (`OIL-PROPOSAL` / `OIL-RAW-EVIDENCE`,
    F02).
- Widening the endpoint tolerance to cover 86–109 px would be the escape hatch
  F10 forbids.

**Open physical question (only a human can answer it):** during 673.0–675.0 s, is
the rising oil interface visible between the mask top (Y243) and Y340?
- **Visible:** proposal recall at the top of the Glass fails (F02). D1 stands.
  The next work is on the evidence side; top-exit as decided follows.
- **Not visible** (the top region hides it): for BASE the practical observable
  limit is near Y330–340, not the mask top. D1's mask-top limit would then not
  hold for this Glass. FULL would have to be inferred from a disappearance about
  0.12H below the limit, which is the proximity class that produced G. That would
  reopen D1/D2.

**Agent lean (not binding):** pause the D1b/D2 implementation. First answer the
visibility question with one human review through the existing O2 workflow on
the ④ bundle (BASE 673.0, 673.5, 674.0, 674.5, 675.0 s). The question must allow
"visible above every candidate", because no candidate exists above Y340 after
673.0 s. The next free case ID is review-011. The paused layered-Foam line had
earmarked it for Accum 672–677.5 s; IDs are assigned in order, so that line
would take the next one.

## Constraints preserved

- **Unchanged:** default R22 + R22-3/O1 and every experiment flag; FULL CONDITION
  FAILED / ⑧ NOT RUN; O2 OPEN / FIELD FAIL; review-006 pending.
- **Kept:** the 721 s false anchor and the 723/771 s protections.
- **Sample3** stays quarantined.
- **No mask-edge substitution or margin change** happens until the user decides
  D1.
- **Layered-Foam line:** stays paused. LBT-2 option (b) and review-011 (Accum
  672–677.5 s) stay reserved for it.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-PROPOSAL`.
- Failure-registry entries: `S11-F02`, `S11-F05`, `S11-F08`, `S11-F10`.
- First harmful stage:
  - **sample4:** `OIL-PHASE-FILL` — T1 confirms a fill on a row 0.21H from the
    configured top, and the cap then turns the Oil into UNKNOWN (LBT-1 G,
    verified in the retained CSV).
  - **Windows BASE (§6):** the run stays in the `OIL-PHASE-INITIAL` barrier
    throughout, so no 27 % rule acts. The first loss is at `OIL-SELECTOR` at
    673.0 s: the admitted Y329 owner is not selected, for an unstored reason
    (publishability or path cost). From 673.5 s there is no proposal in Y243–339
    (`OIL-PROPOSAL` / `OIL-RAW-EVIDENCE`). Whether the interface is physically
    visible there is unknown.
- Existing feature coverage:
  - Source reviewed for every top-geometry consumer (T1–T10), `_constrain_layer`,
    image FULL evidence, IFO v2 and top-exit.
  - Recipes checked with the real mask builder: sample4 original, the P5
    snapshot, the October 15 interior Recipe and base_sample_1.
  - Windows BASE geometry comes from the transferred ④ receipt.
  - Top-exit, cost-first, RGB and Local XY are OFF in ④; IFO v2 is ON in ④.
- Execution scope: desk review plus one transferred read-only Windows trace
  extraction (§6) from the existing ④ bundle; no detector, pipeline or replay
  run anywhere; no human review. The local work was a read-only geometry
  computation and a read of the retained LBT-1 CSV.
- Logic-map impact: NONE — review only. The map already states that FULL barrier
  frames are coordinate-free and that top-exit uses the configured top.
- Failure-registry impact: NONE — no mechanism changed. The facts above sit
  within the existing F05/F08/F10 rules; the record is kept here.
