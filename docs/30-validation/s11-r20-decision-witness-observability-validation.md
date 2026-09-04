# S11-R20 판정 위트니스 관측 검증·작업 명세

**Status:** `DESIGN ONLY — NOT_IMPLEMENTED / VALIDATION NOT RUN`

## 목적과 실행 경계

이 문서는 Sol이 승인한 `ADAPT existing owner-bound observational witnesses`
설계의 향후 I1/I2 검증·작업 명세이다. 현재 R20 detector 동작이나 field gate를
대체하지 않는다. 이 문서 작성 시 production/source/test/config 수정, detector
실행, local replay 및 Windows replay는 수행하지 않았고 아래 모든 결과는
`NOT_RUN`이다. I1 관측 구현, I2 독립 검증, B 행동 설계는 각각 별도 authority와
사용자 승인을 받아야 하며 이번 문서가 coding gate 또는 R21 승인으로 작동하지
않는다.

권한은 [현재 logic map](../20-architecture/s11-current-detector-logic-map.md),
[S11 책임 아키텍처](../20-architecture/s11-detector-responsibility-architecture.md),
[R20 lifecycle validation](s11-r20-delayed-drain-reacquisition-validation.md),
[검토된 Windows truth](windows-sample1-heating-coldstart-reviewed-truth.md),
그리고 [R20 Windows 증거 통합](../60-evidence/s11/s11-r20-windows-evidence-consolidation.md)에
분리되어 있다. User-report의 수치/해시는 provenance일 뿐이며 private bundle의
독립 검증을 의미하지 않는다.

## 검증 대상 계약

### 1. Source-driven witness semantics

검증 구현은 기존 owner가 실제 계산한 불변 evaluation을 한 번 직렬화해야 한다.
각 witness predicate는 다음을 구분한다.

| 상태 | 의미 | 금지된 해석 |
|---|---|---|
| `true` | 실제 branch에서 평가되어 통과 | 입력이 없는데 추정된 pass |
| `false` | 실제 branch에서 평가되어 실패 | short-circuit 또는 누락을 false로 대체 |
| `NOT_EVALUATED` | short-circuit/비방문/선행 종료로 평가하지 않음 | 모든 branch를 평가한 완전한 진단 |
| `UNAVAILABLE` | input/evidence/schema가 없어 판정 불가 | 측정된 clean/negative |

`first_failed`는 실제 evaluation 순서가 관측될 때만 제공한다. modal label,
summary count, telemetry ID 또는 새 계산 결과로 first harmful stage를 만들지
않는다. confidence/score/policy 공식은 복제하지 않고, 실효 값과 owner의 판정
결과를 join한다.

### 2. Authority and lifecycle

다음은 기존 owner와 같은 순서로 관측되어야 한다: initial state → fill owner/
owner loss/grace → direct → near → delayed → continuation/handoff → progress/
direction/material/ambiguity/expiry/reset → selector/projection. `false`는 평가된
실패이고 `NOT_EVALUATED`/`UNAVAILABLE`은 각각 비방문과 입력불가이다. attempt
consumed transition, seed/reset frame과 active summary를 분리한다. `evaluated=True`
frame 수, evaluation record 수, chain summary 수를 서로 대체하지 않는다.

numeric row는 phase row, allowed owner, same-frame member, selected candidate를
join해야 한다. 현재 checkout의 lifecycle/tracklet row aggregate는 각각
`median`이며, source semantics는 [lifecycle source](../../src/oil_tracker/adapters/vision/oil_phase_lifecycle.py#L2921)
와 [tracklet source](../../src/oil_tracker/adapters/vision/oil_interface_tracklets.py#L482)에
있다. private report의 arithmetic mean은 `USER-REPORT / UNVERIFIED`로 남기며,
row aggregate와 selected candidate Y를 동일시하지 않는다. 단, selected candidate
Y = sequence raw Y = CSV raw Y는 필수 불변식이다.

### 3. Foam and publication

Foam은 raw present/pending/current absent/final episode, track/segment membership,
formation branch와 confirmation frame/IDs를 독립적으로 관측한다. Oil unknown이어도
Foam owner가 독립적으로 평가될 수 있어야 하고, Oil/Foam composition은 한 번이다.
후속 evidence가 포함되었다는 사실과 제거 시 결과가 달라지는 counterfactual은
다르므로 후자는 `NOT_EVALUATED`이다. graph bridge, report, CSV, trace는 detector
authority나 coordinate repair가 아니다.

진단 on/off의 authoritative output은 동일해야 한다: candidate/authority/tracklet
ID, phase/reason/allowed IDs, selection/projection, sample/event/CSV, Foam fields,
cardinality와 Glass/frame/time identity. On에서만 추가되는 것은 bounded diagnostic
fields뿐이다.

## Acceptance matrix

모든 행은 향후 I2에서 실행할 acceptance이며 현재 결과는 `NOT_RUN`이다.

| Gate | 준비/양성·음성 조건 | 합격 기준 | 현재 결과 |
|---|---|---|---|
| Identity/provenance envelope | source frame/time, Glass, layer, row/track/candidate/owner, source/build/config/schema identity가 있거나 명시적 unknown | private 경로·truth coordinate 없이 portable join; reported source hash를 run identity로 사용하지 않음 | `NOT_RUN` |
| Predicate status | pass/fail, short-circuit, missing input/schema를 각각 발생시키는 synthetic cases | source-driven `true`/`false`와 `NOT_EVALUATED`/`UNAVAILABLE` 정확; 누락을 false/0으로 채우면 FAIL | `NOT_RUN` |
| First-failure ordering | direct/near/delayed, material, reversal, progress, step, ambiguity를 각기 선행/후행으로 제어 | 실제 방문 순서만 `first_failed`; summary/modal label로 대체하면 FAIL | `NOT_RUN` |
| Attempt/chain units | seed→consumed→reset, duplicate anchor, context reset, grace 및 expiry | transition event, evaluated frame, evaluation record, chain summary cardinality가 분리되고 one-attempt 유지 | `NOT_RUN` |
| Row/member join | 홀수·짝수 member Y, 같은 row의 여러 IDs, aggregate와 selected Y가 다른 fixture | source median과 selected same-frame member join을 구분; selected=sequence=CSV Y | `NOT_RUN` |
| Publishability/selector | allowed owner absent, member absent, confidence OR branch, selector abstain, unknown | 실제 방문 AND/OR와 abstain이 일치; confidence 공식 재계산·telemetry authority이면 FAIL | `NOT_RUN` |
| Lifecycle safety | initial EMPTY/FULL, owner loss, reversal, duplicate/many-to-one, material-opposed, stale/distant seed | 기존 R20 phase/reason/allowed IDs/selection과 byte-equivalent; 새 transition·좌표·ID copy 없음 | `NOT_RUN` |
| Foam independence | raw present, pending→final, current absent, Oil unknown, segment boundary | Foam membership/formation witness 일치; Oil cross-veto·counterfactual 필수성 주장은 FAIL | `NOT_RUN` |
| On/off equivalence | 같은 synthetic inputs와 기존 four-video fixtures를 diagnostics on/off로 실행 | authoritative output·cardinality·ordering이 동일하고 additive diagnostics만 차이 | `NOT_RUN` |
| Schema/resource bounds | cap, missing field, old consumer, longest ownerless interval, max members/chains | 기존 finite window/cap 유지, run-long buffer 없음, missing/cap 명시; consumer downgrade 없음 | `NOT_RUN` |
| Existing regression | lifecycle/resolver/tracklet/selector/trace/coordinator/publication/Qt/full suite, no golden regeneration | 기존 negative controls·fingerprints·same-frame provenance 보존; 변경 시 FAIL/별도 disposition | `NOT_RUN` |
| Canonical field qualification | nine reviewed segments, 1,202 rows, presence/absence/order/direction and false identity | interval FAIL은 Y anchor 없이도 유효; exact Y accuracy만 anchor 없으면 `NOT_EVALUATED`; report provenance PASS는 effectiveness PASS 아님 | `NOT_RUN` |

## Canonical nine-segment field matrix

이 표는 향후 Windows replay의 최소 report shape이다. 현재 private bundle/replay는
없으므로 각 결과는 `NOT_RUN`이며, truth는 [reviewed-truth authority](windows-sample1-heating-coldstart-reviewed-truth.md)가
소유한다.

| Segment ID | 기대되는 관측 | 판정 | 현재 결과 |
|---|---|---|---|
| `WS1-BASE-FULL-PREFIX` | Oil/Foam boundary 없음; supported FULL만 coordinate-free | interval PASS/FAIL, exact Y `NOT_EVALUATED` if no anchors | `NOT_RUN` |
| `WS1-BASE-DRAIN` | visible downward Oil interface; lower structure/glare false identity 배제 | presence/direction 및 false run | `NOT_RUN` |
| `WS1-BASE-RAPID-REFILL` | visible rising interface 후 full closure; 다른 row transfer 금지 | presence/order/closure | `NOT_RUN` |
| `WS1-BASE-FULL-SUFFIX` | Oil/Foam boundary 없음; lower/reflection row false | interval PASS/FAIL | `NOT_RUN` |
| `WS1-ACCUM-EMPTY` | Oil/Foam boundary 없음 | interval PASS/FAIL | `NOT_RUN` |
| `WS1-ACCUM-ENTRY-SPLASH` | rising Oil boundary; splash/wall mark 비권한 | presence/direction/identity | `NOT_RUN` |
| `WS1-ACCUM-FOAM-LAYERED` | upper Foam과 lower Oil을 독립 publish; Foam top→Oil 금지 | ordering/independent validity | `NOT_RUN` |
| `WS1-ACCUM-POST-FOAM` | Foam absent; visible Oil owner 유지 | absence/presence/identity | `NOT_RUN` |
| `WS1-ACCUM-DRAIN` | descending Oil interface; wall residue 비권한 | presence/direction/false identity | `NOT_RUN` |

## Dependencies, unknowns, risks and rollback

| Future package | Dependency | Boundary |
|---|---|---|
| I1 | 이 설계의 field-to-source mapping, 별도 implementation approval | owner evaluation 한 번 직렬화, production decisions/output 불변 |
| I2 | I1, independent validator, synthetic fixtures와 기존 corpus | local witness/equivalence/resource/schema 검증; field replay를 전제로 하지 않음 |
| B | I2 plus physical identity와 two-sided evidence, fresh Sol design gate | 어떤 predicate를 바꿀지와 safety 반례를 특정하기 전 행동 변경 금지 |

Named unknown은 다음과 같다: Base 최초 physical loss; Accum raw-vs-association,
drain candidate identity/direction, snapshot non-update 및 selector abstain; Check01
continuation predicate; Check03 source/branch identity; Check04 chain creation count;
Check05 raw Foam identity와 post-672 necessity; Check06 confidence OR branch; Check07
row-member join 및 private mean/current median 관계; private build/config/source
identity; exact reviewed Y anchors. Unknown은 `false`나 `PASS`가 아니다.

위험은 evaluation 재실행에 따른 순서/동작 변경, confidence duplicate formula,
telemetry authority, unbounded memory, schema 누락 오독, historical run/source 혼동이다.
실패 시 rollback은 additive diagnostic field/schema와 이 문서 routing만 철회하고,
원래 detector output·field FAIL evidence·reviewed truth·golden을 수정하지 않는다.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-PROPOSAL`, `OIL-HYPOTHESIS`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `TRACE-PUBLICATION`, `RESULT-PRESENTATION`
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: current logic map and F01–F10 registry details; S11 responsibility architecture; R18 causal trace architecture/validation; R20 lifecycle architecture/validation; reviewed truth; and R20 Windows consolidation/intake.
- Prior mechanisms rejected: global threshold/case escape, motion-only authority, stale owner/coordinate transfer, Foam cross-veto, selector/projection repair, interpolation/carry, confidence recomputation, unbounded telemetry and private identity.
- Preserved contracts: typed authority, bounded ownership, initial-state safety, source-driven witness status, independent Foam, exact same-frame sequence/CSV provenance, fail-closed ambiguity/material and bounded resources.
- Difference from prior failures: this is a future validation contract for additive observation only; all current decision owners and output semantics remain the authority.
- Logic-map impact: NONE — this is a new `DESIGN ONLY — NOT_IMPLEMENTED` validation contract and does not change current control flow.
- Failure-registry impact: NONE — no causal mechanism or field result is added; F01–F10 remain unchanged.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: future implementation must not infer one; current Base/Accum physical loss and Check06 detection-versus-association stage remain unknown, while reported Foam false publication is an episode-confirmation observation and publication is not the harmful stage.
- Logic-map impact: NONE — no detector implementation or owner map is changed by this validation-only specification.
- Failure-registry impact: NONE — the existing causal guards remain authoritative and no new mechanism is asserted.
