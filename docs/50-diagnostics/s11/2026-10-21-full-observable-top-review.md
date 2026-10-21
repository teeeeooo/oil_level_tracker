# OTR-1 — FULL observable-top design review (B)

**Status: REVIEW COMPLETE — D1, D1b, D2 and D3 DECIDED by the user ([decision record](#decision-record--2026-10-21)).**
The [§6 ④ trace receipt](#6-windows-trace-receipt--2026-10-21) is recorded.
- **27 % rules:** not involved on Windows BASE.
- **Selection:** the last selected row is Y352. At 673.0 s the publishable Y329
  owner row loses to unknown on path cost
  ([receipt](#673-s-selection-cause-receipt--2026-10-21)).
- **Evidence:** from 673.5 s no proposal exists in Y243–339.
- **Decided top-exit design:** would not change ④ BASE. The adopted revision
  (items 1–5, item 3 = 3a) is in a
  [design draft](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-21-top-exit-revision-v2).
  The [predicate check](#predicate-check-receipt--2026-10-21) shows that only
  `independent_anchor` fails on ④. The user chose item 6 = 6a, and the design
  is frozen.

Desk review plus transferred Windows evidence: source reading, closed records,
the retained LBT-1 CSV, one geometry computation with the real mask builder on
retained local Recipes, three read-only ④ trace extractions and review-011, all
relayed by the user. No detector run, flag or tuning. Base HEAD `b9ff06b`. Current authority:
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

### User video review — 2026-10-21 (replaces the proposed review)

The user re-checked the source video. The level rises slowly, rises fast from
about 670 s, and is almost full near 672 s. A very small void disappears near
674–675 s. **FULL output is acceptable from about 672 s**, now recorded in the
[reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#base-full-acceptance--2026-10-21).
No review-011 is needed for this question.

**What this changes:**
- **The target is now "FULL from about 672 s", not "FULL after the void
  vanishes".** By the user's reading of the video, the 673.5–675.5 s frames hold
  an almost-full Glass with a tiny void. Absence of proposals in Y243–339 (R4)
  there is therefore not established as a recall failure.
- **D1b as decided cannot meet this target on ④.** The last evidence lies 86–109
  px (0.11–0.14H) below the observable limit. FULL from about 672–674 s needs an
  endpoint that accepts disappearance inside an upper band, not only at the
  observable limit.
- **The existing 27 % band would cover it.** Y329 and Y352 lie at 0.15–0.18H
  (band end Y420). Using that band moves top-exit into the proximity class that
  produced G, so it needs a two-sided local check (sample4 G, base_sample_1,
  sample2).
- **Even with a band endpoint, current T9 would not fire on ④:**
  - the 2 px downward step at 672.5 s resets its window (R6);
  - the admitted but unselected Y329 at 673.0 s counts as a current interface
    and resets it again (R3).

  A design would need a bounded jitter allowance (for example the existing
  reversal tolerance, 9.27 px for BASE) and a rule for the admitted owner at
  673.0 s. Both must be frozen before any run.

**Open identity question:** "Almost full at about 672 s" may conflict with a
level at Y350 (0.18H below the top). If the real level was already near the top
at 672 s, the selected rows Y350/352 and the Y329 owner are not the level. FULL
by their disappearance would then be right for the wrong reason. Only the user
can say where the level was at about 672 s. This is asked as
[review-011](../../40-operations/s11-current-windows-field-qualification.md#review-011-base-level-at-the-fast-rise-onset)
(requested 2026-10-21; BASE 670.0/671.0/672.0/672.5/673.0 s).

**Reopened for the user:** the D1b endpoint, observable limit (as decided) or
the existing 27 % band, given the 672 s acceptance. D2 (S + persistence) is
unchanged.

### Review-011 result — 2026-10-21

**COMPLETE.** Human review only, on the same ④ bundle, through the O2 workflow:
prepare → link-bundle → 10 plain/idx-guide images → one question per frame →
5 records. The packets are stored on Windows only.

**Provenance**
- Labels SHA-256 `32775814dfc3616b97f6caa7627171059ea12d3a7f718e0367f49d27864598f8`;
  5 revisions.
- Owners are empty, as in review-010 (status reports `missing_owners`).
- The `87817ad` folder no longer existed. The agent used the Windows source
  folder `oil_level_tracker-main`, whose commit was not reported. The O2 tool has
  not changed since `a1bf512` (2026-10-06), and every requested Y was found in the
  packet.
- At f16088 the guide labels of idx9/idx11 (both Y369) overlapped. Only the
  label positions were redrawn and the question asked again; no judgement changed.

**User note:**

> 내가 유면이라고 확인해준 idx들 보다 실제 유면은 약간 더 위에 존재해. 다만
> 디텍터로는 검출이 어려울 것 같아 일정부분 감안해서 idx를 유면이라고 판정했어.
> 대체로 idx들이 유면 경계의 빛반사를 따라가는 것 같더라고.

| Frame / time | Level visible | Level idx | Candidate judgements | Note |
|---|---|---|---|---|
| f16064 / 670.0 s | yes | idx13 | idx13 Y384 = interface | The first answer ("above Y384") was corrected by the user |
| f16088 / 671.0 s | yes | idx9, idx11 | idx9 Y369 = interface, idx11 Y369 = interface | |
| f16112 / 672.0 s | yes | idx10 | idx10 Y350 = interface | |
| f16124 / 672.5 s | yes | above all candidates | idx17 Y352, idx20 Y336, idx10 Y338 = non_interface (reflection) | "모두 빛반사를 잡고있음" |
| f16136 / 673.0 s | yes | idx18 | idx18 Y329 = interface; idx10 Y343 = non_interface | Y329 was not selected; Y343 was not output |

**Findings**

| # | Finding |
|---|---|
| V1 | **The identity question is answered: option (a).** The IFO v2 owner `000366:0319` follows the level in practice, on the reflection just below the real boundary. This holds at 670.0/671.0/672.0 s (Y384/369/350) and at 673.0 s (Y329, unselected). "Almost full near 672 s" is therefore a level about **0.18H below the configured top (Y350)**. At 673.0 s the level is at 0.15H (Y329) |
| V2 | **Two wrong outputs at the end of the rise.** At 672.5 s the published Y352 is a reflection below the level, which is already above Y336. At 673.0 s the true level Y329 is rejected, so R3/H4 is a real miss |
| V3 | **R4 is not a miss to recover.** After 673.0 s, the near-full rise (void gone at 674–675 s) produces no proposal, and FULL is accepted from about 672 s |
| V4 | **The upper-band endpoint is physically supported here.** The last true observation lies 0.15H below the top: inside the existing 27 % band (Y420) and 86 px below the observable limit. An endpoint at the observable limit cannot fire; the upper-band endpoint is supported by this review for this Glass |
| V5 | **Detector rows sit slightly below the real level** (boundary reflection). The user accepted them as the level in practice. This is a practical allowance like review-004, not exact-Y truth |

**What a top-exit revision would need (freeze before any run; nothing is
implemented):**
1. **Endpoint:** the last owner row lies within the existing top band
   (`entrance_band_ratio`, 0.27H). This is D1b′ and replaces the
   observable-limit endpoint; it reuses an existing ratio with no new constant.
2. **Window continuity:** a one-frame lag row like 672.5 s, within the existing
   bounded reversal tolerance (`handoff_direction_reversal_tolerance_px`), must
   not reset the window.
3. **The 673.0 s miss:** either the window counts the admitted, allowed,
   IFO-qualifying same-owner row even when it is not selected, or the selection
   miss is fixed. Choosing needs the reason (publishability or path cost). The
   trace does not store it directly; a read-only recompute of that row's
   confidence from saved features could separate the two.
4. **D2b persistence:** after closure, FULL holds through IFO v2 exposures (the
   721 s class) until a qualified T5 drain release.
5. **Controls:**
   - **Local negatives:** sample4 G (no FULL at 54.5–56 s); base_sample_1 and
     sample2 unchanged; synthetic positive and negative cases.
   - **Positive:** exists only on Windows, so one Windows comparison on ④'s
     inputs is needed. That run needs the user's go.

**User decision (2026-10-21):** adopt D1b′ and items 1–5 as the design
direction. Separate the 673.0 s cause first: the
[read-only extraction](../../40-operations/s11-current-windows-field-qualification.md#673-second-selection-cause-extraction)
reads the decision witness's per-row `publishable` flag. Its
[receipt](#673-s-selection-cause-receipt--2026-10-21) is recorded below.
Nothing is implemented.

### 673 s selection-cause receipt — 2026-10-21

**RECEIVED.** The user relayed the Windows agent's read-only extraction made with
the [673 s request](../../40-operations/s11-current-windows-field-qualification.md#673-second-selection-cause-extraction)
(`a43c737`).
- **Identity:** run `a9ccece3-49bf-47af-a570-b1ca6e9777a4`, BASE 601 records.
- **Read:** `debug/debug_index.json`, `debug/debug_trace.jsonl` and
  `recipe_snapshot.oilrecipe` only. No run, new bundle, tuning or human review.

**Table D — decision witness.** In all five rows the phase is
`observed_interface / INITIAL_FULL_INTERFACE_OBSERVED`, the allowed set is
[`oil-tracklet:000366:0319`], and every 0319 member is `CONTINUATION_ELIGIBLE`
and `continuing`. Each frame has exactly one publishable row, the 0319 row.

| Time (frame) | Resolved | Selected | 0319 row (`oil-row:`) | Admitted / publishable | Members (* = selected) |
|---|---|---|---|---|---|
| 670.0 (16064) | oil | `calibrated_high_recall` 384 | `000380:002` | true / true | `oil_hypothesis` 385, `calibrated_high_recall` 384* |
| 671.0 (16088) | oil | `material_path` 369 | `000382:000` | true / true | `material_path` 369*, `calibrated_high_recall` 369, `phase_transition_scan` 364 |
| 672.0 (16112) | oil | `material_path` 350 | `000384:001` | true / true | `material_path` 350*, `calibrated_high_recall` 351 |
| 672.5 (16124) | oil | `calibrated_high_recall` 352 | `000385:001` | true / true | `calibrated_high_recall` 352* |
| 673.0 (16136) | **unknown** | MISSING | `000386:000` | **true / true** | `phase_transition_scan` 329 |

The requested self-check passed at 670.0–672.5 s: each selected member lies in the
publishable 0319 row.

**Table E — candidate support.** Constant for every 0319 member: trajectory 1.0;
cluster and semantic corridor 0.0; profile `anchor_corridor`; lifecycle
`continuing`; tracklet material conflict 0.0703. Values below are rounded to four
places; the relayed text keeps full precision.

| Time | Source Y | Cross-representation | Effective track opposition | Reject stage |
|---|---|---:|---:|---|
| 670.0 | `oil_hypothesis` 385 | 0.0 | 0.2520 | GLOBAL_PATH_OR_RUN_BOUND |
| 670.0 | `calibrated_high_recall` 384 | 0.0 | 0.2520 | ACCEPTED |
| 671.0 | `material_path` 369 | 0.6471 | 0.0926 | ACCEPTED |
| 671.0 | `calibrated_high_recall` 369 | 0.6602 | 0.0926 | GLOBAL_PATH_OR_RUN_BOUND |
| 671.0 | `phase_transition_scan` 364 | 0.5915 | 0.3705 | GLOBAL_PATH_OR_RUN_BOUND |
| 672.0 | `material_path` 350 | 0.6336 | 0.0926 | ACCEPTED |
| 672.0 | `calibrated_high_recall` 351 | 0.7000 | 0.0926 | GLOBAL_PATH_OR_RUN_BOUND |
| 672.5 | `calibrated_high_recall` 352 | 0.0 | 0.3705 | ACCEPTED |
| 673.0 | `phase_transition_scan` 329 | 0.0 | 0.13960296975296926 | GLOBAL_PATH_OR_RUN_BOUND |

**Table F — 673.0 s and Recipe**

| `S.sequence_emission` | Ambiguity score | No-interface score | `minimum_final_confidence` | `temporal_max_jump_px` |
|---:|---:|---:|---:|---:|
| 0.25947473538089194 | 0.46606323498456764 | 0.4494745842432939 | 0.42 | 32.0 |

**Transcription note:** the publishable `tracklet_id:y` column lists one entry per
member, so a count of 1 can show two or three entries. All belong to the one 0319
row.

#### Findings

| # | Finding | Evidence |
|---|---|---|
| S1 | **Cause (b): path cost.** At 673.0 s the 0319 row is phase-admitted, publishable and allowed, and it is the frame's only publishable row. All four stages are unknown (§6 Table A), so the bounded best path itself chose unknown over a valid Oil node. Publishability is excluded. The profile is `anchor_corridor`, not `anchor_trajectory`, so the row passed on confidence ≥ 0.42, not on the continuing-anchor witness | Tables D and E; `oil_candidate_is_publishable` |
| S2 | **The choice reduces to one inequality.** From 673.5 s the allowed set is empty, so each later lookahead layer is a single unknown node (`_constrain_layer`). Both paths pay one Oil→unknown cost (−0.20): the unknown path at 673.0 s, the Oil path at 673.5 s. The later suffix is shared. Oil wins only if E_oil + T ≥ E_unknown + 0.02 (unknown persistence) | `BoundedOilInterfaceSelector.resolve`, `_transition_score` |
| S3 | **The bar was E_oil ≥ 0.3007, and the row fell below it.** E_unknown = 0.2595 (stored; it matches the formula with best local quality ≈ 0.549). T = −0.0212 for 23 px in 0.5 s (n = 0.719). E_oil is not stored. Its stored terms sum to 0.0195: base −0.18, trajectory +0.30, opposition −0.1005; zero cluster, corridor and representation; no anchor bonus. The unstored terms (material, availability, motion, penalties) therefore sum below 0.2812 | Table F |
| S4 | **The fast last step sets most of the bar.** A stationary same-owner step scores +0.22, for a bar of 0.060. The 23 px step raises the bar by 0.241. That step includes the 672.5 s lag: the committed Y352 is the reflection below the level (V2). On the unknown side, ambiguity 0.466 adds 0.158 | Bar by step: 0 px 0.060; 11 px 0.136; 21 px 0.267; 23 px 0.301 |
| S5 | **This is structural, not a ④ accident.** Once the owner disappears, the barrier empties the allowed set, and the lookahead holds no Oil continuation to reward the last row. The highest row of a fast top exit competes alone against the frame's unknown node and pays the jump cost. A window built only from selected rows will tend to lose that row; whether it does depends on E_oil | S2–S4 |

#### Item 3 options (the user chooses)

| Option | What changes | For | Against |
|---|---|---|---|
| **3a. The window counts the unselected row** (agent lean) | Inside top-exit only. At a frame the selector resolved unknown, the window may count the same owner's row if it is publishable and allowed. Never when a different Oil row was selected | Numeric output unchanged; no new constant; reuses the selector's own publishability predicate. Matches S5: the miss sits in the exit frame itself | FULL rests on a row the numeric output did not publish: the CSV shows UNKNOWN at 673.0 s, then FULL, with no row above Y352. The witness must name the unselected row |
| **3b. Change the selector** | Unknown emission, unknown persistence, jump cost, or a lag-aware jump | 673.0 s Y329 would publish as Oil (V1: it is the level) | A global cost change on every frame of every video; more 721 s-class false rows may be selected. A cost chosen after seeing this result is tuning (F10, freeze rule) |
| **3c. Treat 673.0 s as the disappearance** | The window uses selected rows only; "disappearance" means no selected Oil | Simplest; FULL from 673.0 s | FULL while an admitted, real interface is visible at 0.15H. Weakens "new interface evidence clears" in every video |

#### S6 — a further gap: the anchor predicate

Items 1–5 do not cover every T9 predicate. `independent_anchor` needs a window row
with `ANCHOR_ELIGIBLE` authority and `direct_interface` or
`ordered_lower_interface` identity.
- **Reported:** every 0319 member at 670.0/671.0/672.0/672.5/673.0 s is
  `CONTINUATION_ELIGIBLE`. The 673.0 s row is `continuation_only` (§6 Table B).
- **Window:** with item 2 and 3a, the six-row window evaluated at 673.5 s is
  670.5–673.0 s. Rows 670.5 and 671.5 s are unreported. If neither is an anchor,
  T9 still fails on ④.

Also unreported for the window frames:
- the last row's recent directional agreement (≥ 0.60);
- material-texture availability and conflict for each window row;
- a single admitted tracklet in each window frame;
- any identity contradiction or phase ambiguity;
- a usable raster at 673.5 s. `effective_gray_*` is always written
  (`phase_frame_detection.py:941–948`), so it is likely present.

The artifact and optics terms of the hard contradiction are derived from
candidate features and not stored; checking them would need a recompute.

**Proposed (not sent):** one read-only
[T9 predicate check](../../40-operations/s11-current-windows-field-qualification.md#top-exit-predicate-check)
on the saved trace before the design freeze. If no window row is an anchor, the
user decides a new item 6:
- accept the owner's tracklet-level anchor profile as the anchor proof; or
- keep the per-row rule, and accept that top-exit cannot meet the 672 s target
  on ④.

**User decision (2026-10-21):** item 3 = **3a**. The user sends the
[predicate check](../../40-operations/s11-current-windows-field-qualification.md#top-exit-predicate-check)
to the Windows agent; its receipt is pending. The
[v2 design draft](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-21-top-exit-revision-v2)
collects items 1, 2, 3a, 4 and 5. It is frozen after the receipt settles
item 6. Nothing is implemented.

**User confirmation (2026-10-21):** under D2b, an unusable or opposed frame inside
a top-exit FULL episode publishes UNKNOWN for that frame without ending the
episode.

### Predicate-check receipt — 2026-10-21

**RECEIVED.** The user relayed the Windows agent's read-only extraction made with
the [predicate check](../../40-operations/s11-current-windows-field-qualification.md#top-exit-predicate-check)
(`c94b140`).
- **Identity:** run `a9ccece3-49bf-47af-a570-b1ca6e9777a4`, BASE 601 records.
- **Read:** `debug/debug_index.json` and `debug/debug_trace.jsonl` only. No run,
  new bundle, tuning or human review.

**Table G — frame inputs (670.0–673.5 s, eight frames).**
- **Raster:** the effective gray values were read from `R.state`; they are
  absent from `S`. Mean 93.1–93.5, std 28.7–29.2, range 92–96.
- **State:** EMPTY likelihood 0.0 and `sequence_material_phase_ambiguous` 0.0 in
  every frame.
- **Admitted tracklets:** [`000366:0319`] at 670.0–673.0 s; none at 673.5 s.
- **Identity contradiction:** 8–12 entries per frame are listed as "not none".
  All have the value null.

**Table H — 0319 members.** Constant in every member:
- `CONTINUATION_ELIGIBLE`; identity contradiction `none`; admitted 1.0;
  incompatible 0.0; `continuing`;
- tracklet material conflict 0.0703; recent direction −1;
- `material_texture_conflict` MISSING, because `sequence.candidates` holds no
  features or penalties.

| Time | Row (`oil-row:`) | Members (* = selected) and identity | Recent net progress | Recent agreement |
|---|---|---|---:|---:|
| 670.0 | `000380:002` | `calibrated_high_recall` 384* and `oil_hypothesis` 385: `continuation_only` | 12.0 | 0.8 |
| 670.5 | `000381:001` | `material_path` 377*, `calibrated_high_recall` 377: `direct_interface` | 16.0 | 0.8 |
| 671.0 | `000382:000` | `material_path` 369*, `calibrated_high_recall` 369: `direct_interface`; `phase_transition_scan` 364: `continuation_only` | 19.25 | 0.8 |
| 671.5 | `000383:000` | `material_path` 362*, `calibrated_high_recall` 362: `direct_interface`; `distributed_sobel_path` 352: `continuation_only` | 25.5 | 0.8 |
| 672.0 | `000384:001` | `material_path` 350*, `calibrated_high_recall` 351: `direct_interface` | 42.5 | 1.0 |
| 672.5 | `000385:001` | `calibrated_high_recall` 352*: `continuation_only` | 32.5 | 0.8 |
| 673.0 | `000386:000` | `phase_transition_scan` 329 (not selected): `continuation_only` | 48.0 | 0.8 |
| 673.5 | — | 0319 absent | — | — |

**Transcription note:** the identity contradiction is serialized only for
candidates that hold a sequence ref (`_project_candidates`). The null entries are
candidates without a ref: Foam evidence, raw hypotheses and far rows such as
Y898–953. T9's `opposed` reads refs only, so none of them is a contradiction.

#### Findings

| # | Finding |
|---|---|
| P1 | **`independent_anchor` fails on ④.** No 0319 member at 670.0–673.0 s is `ANCHOR_ELIGIBLE`. With items 1, 2 and 3a, the six-row window evaluated at 673.5 s (670.5–673.0 s) holds no anchor, so v2 as drafted would not fire. Item 6 is needed |
| P2 | **Every other stored predicate passes.** Usable raster (far above the black limits); EMPTY 0; no ambiguity; no ref contradiction; one admitted tracklet per window frame; disappearance at 673.5 s (none admitted). Rows are admitted, compatible and `continuing`, with material conflict 0.07 < 0.45. The last row's direction is upward with agreement 0.8 ≥ 0.60. Progress is 48 px (Y377 → Y329) ≥ 19.3. The endpoint is at 0.152H ≤ 0.27. Steps are −8, −7, −12, +2 (the lag, within 9.27) and −23 (≤ 32). Gaps are 0.5 s |
| P3 | **Material texture is inferred, not stored.** IFO v2 qualified 0319 at 670.0–673.0 s (§6 Table A). Its `current_material_conflict` predicate takes the minimum conflict over the row's texture-available members (default 1.0) and needs < 0.45. So each 0319 row had such a member below the limit. For the single-member rows at 672.5 and 673.0 s that member is the window row itself. Elsewhere the representative is `material_path`, which always sets the key (`oil_material_path.py`) |
| P4 | **Not covered:** the artifact and optics terms of the hard contradiction (not stored), and the hard-unavailable input flags at 673.5 s. The gray values rule out a black frame; the input flags were not extracted |
| P5 | **The owner holds a tracklet-level anchor confirmation.** Every window row has profile `anchor_corridor` (Table E). The tracklet policy assigns it after at least 3 frames with an `ANCHOR_ELIGIBLE` member in the confirmation window (1 for a short observation; `oil_interface_tracklets.py:1068–1089`). The ID prefix 000366 suggests the tracklet began at record offset 366 (663.0 s), inside this refill; row IDs follow the same offsets (000380 = 670.0 s). Four window rows (670.5–672.0 s) are `direct_interface` |

#### Item 6 options (the user chooses)

| Option | Rule | For | Against |
|---|---|---|---|
| **6a. Tracklet-level anchor** (agent lean) | `independent_anchor` passes as in v1 (a window row `ANCHOR_ELIGIBLE` with direct or ordered-lower identity), **or** when the owner's profile is `anchor_corridor`/`anchor_trajectory` and at least one window row is `direct_interface` or `ordered_lower_interface` | Reuses the tracklet policy's anchor confirmation, which the lifecycle already trusts (`_chain_is_strong_anchor_interface`, `_is_current_fill_anchor_handoff`). Keeps a physical-interface row in the window. No new constant. ④ passes (P5) | The anchor can predate the window. Continuing admission bounds this only partly: each row needs an anchor within the grace or corridor bound, or registered aggregate motion. A tracklet confirmed on the real level that later drifts onto a reflection near the top could close (F04-like). The local controls must show it does not |
| **6c. Keep the per-row rule** | No change | Strictest | v2 cannot fire on ④; no Windows positive; top-exit does not meet the 672 s target. The next work moves to the evidence side: why the rows near the top are only `CONTINUATION_ELIGIBLE` |

A wider window or an anchor recency bound would need a new constant, so neither
is proposed.

**User decision (2026-10-21):** item 6 = **6a**. The v2 design is
[frozen](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-21-top-exit-revision-v2)
and implementation with the local controls is authorized. A Windows comparison
needs a separate go.

**Implemented (2026-10-21):** top-exit v2, default OFF. The four frozen local
controls pass with zero top-exit FULL rows and unchanged output; none reached a
disappearance evaluation
([evidence](../../60-evidence/s11/2026-10-21-top-exit-v2-local.md)).

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
    673.0 s: the publishable Y329 owner row loses to unknown on path cost
    (S1–S5). From 673.5 s there is no proposal in Y243–339
    (`OIL-PROPOSAL` / `OIL-RAW-EVIDENCE`). Whether the interface is physically
    visible there is unknown.
- Existing feature coverage:
  - Source reviewed for every top-geometry consumer (T1–T10), `_constrain_layer`,
    image FULL evidence, IFO v2 and top-exit.
  - Recipes checked with the real mask builder: sample4 original, the P5
    snapshot, the October 15 interior Recipe and base_sample_1.
  - Windows BASE geometry comes from the transferred ④ receipt.
  - Top-exit, cost-first, RGB and Local XY are OFF in ④; IFO v2 is ON in ④.
- Execution scope: desk review plus three transferred read-only Windows trace
  extractions (§6, the 673 s receipt and the predicate check) and one human
  review (review-011), all on the existing ④ bundle; no detector, pipeline or
  replay run anywhere. The local work was a read-only geometry
  computation and a read of the retained LBT-1 CSV.
- Logic-map impact: NONE — review only. The map already states that FULL barrier
  frames are coordinate-free and that top-exit uses the configured top.
- Failure-registry impact: NONE — no mechanism changed. The facts above sit
  within the existing F05/F08/F10 rules; the record is kept here.
