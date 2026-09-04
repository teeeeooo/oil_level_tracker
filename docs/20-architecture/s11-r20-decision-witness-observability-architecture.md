# S11-R20 판정 위트니스 관측 아키텍처

**Status:** `DESIGN ONLY — NOT IMPLEMENTED`

## 결정과 권한 경계

이 문서는 Sol 설계 gate의 `PASS — ADAPT` 결정을 문서화한다. 목표는
R20의 기존 판정 owner가 이미 계산한 입력·분기·상태 전이를 bounded
decision-witness로 관측하는 후속 설계이다. 이 문서는 detector 동작, 임계값,
재시도 정책, R21 또는 새 owner를 승인하지 않는다. 현재 production owner와
field gate는 [S11 책임 아키텍처](s11-detector-responsibility-architecture.md),
[R20 아키텍처](s11-r20-delayed-drain-reacquisition-architecture.md),
[R20 검증 계약](../30-validation/s11-r20-delayed-drain-reacquisition-validation.md)이
계속 소유한다.

Windows bundle, raw checkpoint, private video 및 frame-exact Y annotation은
이 checkout에 없다. [R20 Windows 증거 통합](../60-evidence/s11/s11-r20-windows-evidence-consolidation.md)의
Check01–Check07 수치는 user-report provenance로만 취급한다. 보고된 현재 source
video hash는 source 속성일 뿐 run/build/binary identity가 아니다. repository의
현재 source semantics와 역사적 실행 산출물을 섞지 않으며, `FIELD FAIL`을
publication provenance `PASS`로 승격하지 않는다.

## ADAPT / REUSE / REJECT 결정

새 관측은 기존 owner-boundary에 붙인다. 신규 recovery owner, 전역 threshold,
case-specific branch 또는 R21 정책은 `REJECT`한다. 다음 표는 구현 지시가
아니라 이후 별도 승인된 I1의 책임 경계이다.

| 기존 책임 | 결정 | 관측 계약과 경계 |
|---|---|---|
| `FRAME-EVIDENCE` / `OIL-RAW-EVIDENCE` / `OIL-PROPOSAL` / `OIL-CANDIDATE` | `REUSE` | source frame, candidate/member, evidence availability와 기존 provenance를 그대로 연결한다. proposal은 physical truth나 authority가 아니다. |
| `OIL-AUTHORITY` / `OIL-TRACKLET` | `REUSE` | typed tier, row hypothesis, tracklet, confirmation, handoff 및 ambiguity를 existing result로 참조한다. motion·direction·recurring Y만으로 identity를 만들지 않는다. |
| `OIL-PHASE-INITIAL` / `OIL-PHASE-FILL` / `OIL-PHASE-DRAIN` (`OilMaterialPhaseLifecycleOwner`) | `ADAPT` | direct/near/delayed/reentry/continuation의 실제 방문 branch, 입력, 비교, policy, 결과와 short-circuit 상태를 같은 evaluation에서 기록한다. 새 transition은 만들지 않는다. |
| `OIL-SELECTOR` / `OIL-PROJECTION` | `REUSE` | allowed owner, selected node와 same-frame candidate를 관측으로 join한다. selector가 upstream gap을 복구하거나 projection이 좌표를 만들지 않는다. |
| `FOAM-CANDIDATE` / `FOAM-IDENTITY` / `FOAM-EPISODE` | `ADAPT` | raw/pending/current absent/final episode와 formation witness를 연결한다. Foam policy와 Oil cross-veto는 바꾸지 않는다. |
| `SEQUENCE-COMPOSITION` / `PUBLICATION-PROVENANCE` / `CSV-PUBLICATION` | `REUSE` | 한 번의 Oil-then-Foam composition과 독립 validity, selected→sequence→CSV provenance를 검증 대상으로 재사용한다. |
| `TRACE-PUBLICATION` (`JsonlDebugTraceWriter`) | `ADAPT` | bounded additive JSONL snapshot과 schema/version/source identity를 기록한다. trace는 detector authority가 아니며 기존 consumer가 누락을 false/0으로 해석하지 않게 한다. |

## 관측 모델

### 공통 identity envelope

각 witness record는 가능한 값만 다음 identity에 연결한다: source frame/time,
Glass, layer(`current`/`sequence`/`public`), row hypothesis, tracklet, candidate,
phase/owner chain, 실제 decision owner 및 route. runtime build/source/config/schema
identity는 확보된 값만 기록하고 나머지는 `unknown`으로 둔다. source video hash는
binary identity와 별도의 provenance field이며 private 경로·실제 파일명·truth
coordinate를 기록하지 않는다.

`current`, `sequence`, `public`은 서로 다른 시간/권한 층이다. selected delayed
tracklet, owner-chain ID, debug label 및 report bridge는 물리 interface의 정답이
아니다. transition event의 frame/time과 나중에 붙은 summary label도 별도 값으로
남긴다. 예를 들어 attempt가 consumed된 시점과 `attempt_consumed` barrier label을
하나의 시각으로 덮어쓰지 않는다.

### Lifecycle witness

`OilMaterialPhaseLifecycleOwner`가 실제로 방문한 branch만 기록한다. direct → near
→ delayed 우선순위, initial state, owner/loss/grace, seed, continuation, handoff,
reversal, material, progress, step, ambiguity, expiration, reset의 순서와 입력을
기록한다. 각 predicate는 다음 상태를 갖는다.

- `true`: 해당 predicate가 실제 평가되어 통과했다.
- `false`: 해당 predicate가 실제 평가되어 실패했다.
- `NOT_EVALUATED`: short-circuit, branch 비방문 또는 이전 단계 종료로 평가되지
  않았다.
- `UNAVAILABLE`: 필요한 input/evidence/schema가 없어서 판정할 수 없었다.

`false`를 누락이나 비방문으로 채우지 않는다. `first_failed`는 실제 평가 순서를
증명할 때만 사용하며, modal failure label이나 가장 흔한 실패 수를 first cause로
승격하지 않는다. witness는 기존 evaluation의 불변 결과를 직렬화하고 trace를
위해 predicate를 다시 실행하지 않는다. 구현 시 boolean을 새 공식으로 계산하거나
방문하지 않은 branch를 진단 목적으로 실행하면 계약 위반이다.

시도/chain 기록도 단위를 분리한다. `seed identity`, attempt consumed transition
frame, reset frame/reason 및 context change는 active summary와 다르다. 생성/소비
횟수는 transition event만 세고, `evaluated=True` frame 수, evaluation record 수,
chain summary 수를 서로 바꾸지 않는다. event ID는 run/episode 범위에만 유효하며
control flow 입력이 아니다. R20의 established-fill episode당 one-attempt 정책은
그대로이다.

### Row/member/selection join

row의 `tracklet_id`/`row_hypothesis_id`, member IDs/Y, representative ref,
publishable member와 selected candidate를 명시적으로 join한다. 현재 checkout의
source semantics는 다음과 같다.

- `OilMaterialPhaseLifecycleOwner._rows`는 member Y의 `median`을 row `y`로
  사용한다([`oil_phase_lifecycle.py:2921`](../../src/oil_tracker/adapters/vision/oil_phase_lifecycle.py#L2921)).
- directed tracklet row hypothesis도 member Y의 `median`을 사용한다
  ([`oil_interface_tracklets.py:482`](../../src/oil_tracker/adapters/vision/oil_interface_tracklets.py#L482)).
- Check07A의 private-report “arithmetic mean”과 네 member Y252 산술은 raw
  checkpoint가 없어 `USER-REPORT / UNVERIFIED`이다. source semantics가 과거
  report binary의 semantics를 증명하지 않는다.

따라서 row aggregate Y와 selected candidate Y가 다를 수 있다는 사실 자체를
오류나 publishability로 해석하지 않는다. 반대로 numeric publication의 불변식은
selected candidate Y = sequence raw Y = CSV raw Y이다. snapshot/seed Y, state,
retained graph 또는 interpolation으로 좌표를 만들거나 보정하지 않는다.

### Publishability witness

phase row 존재, allowed owner, owner의 same-frame member, publishability AND/OR
branch 방문/결과, 실효 confidence threshold와 selector abstain을 각각 기록한다.
confidence를 새 공식으로 복원하거나 duplicate formula를 저장하지 않는다. branch가
short-circuit되어 완전한 evidence가 아니면 `NOT_EVALUATED`/`UNAVAILABLE`을 그대로
표시한다. selector 결과가 witness의 authority가 되지 않으며 projection은 선택된
현재 row만 복사한다.

### Foam confirmation witness

raw present, pending, current absent와 final candidate를 분리하고 bounded
track/segment membership, 실제 formation branch, confirmation에 사용된 frame/ID를
join한다. 후속 frame이 평가 범위에 들어왔다는 사실과 “그 frame이 없으면 결과가
달라진다”는 counterfactual은 다르므로 후자는 이 설계에서 `NOT_EVALUATED`이다.
기존 episode finalize 정책, 독립 Oil/Foam validity, Oil-first/Foam-second composition은
바꾸지 않는다. Foam evidence는 Oil mask/veto/coordinate source가 아니다.

## Bounded schema와 불변식

진단 snapshot은 기존 candidate/row/chain/window cap 내부에서만 만든다. run 전체를
새 buffer로 축적하지 않고, 누락·cap·구 schema를 소비자가 명시적으로 알 수 있게
한다. 진단 저장 실패는 기존 debug 실패 정책을 따르며 새 관측을 fallback authority로
사용하지 않는다. diagnostics off는 allocation/serialization을 최소화하지만 다음
authoritative output은 on/off에서 동일해야 한다: candidate/authority/track IDs,
phase/reason/allowed IDs, selection/projection, sample/event/CSV, Foam fields와
완료-window cardinality/frame identity.

보존해야 할 안전 계약은 initial EMPTY hard gate, coordinate-free FULL barrier,
distinct physical IDs, reciprocal bounded handoff, ambiguity/material fail-closed,
직접→near→delayed 우선순위, no carry/interpolation/backfill, 독립 Foam, exact
same-frame sequence/CSV provenance이다. telemetry ID, report, graph bridge, state
prior, confidence copy는 권한이 없다.

## 비목표, 의존성 및 rollback

이 문서의 대상은 향후 I1 관측 구현과 I2 검증의 계약뿐이다. I1/I2/B는 이번 실행의
coding gate가 아니며, 별도 authority와 사용자 승인이 필요하다. I2가 통과해도 행동
변경이나 R21 승인으로 이어지지 않는다. B는 물리 identity와 two-sided evidence가
확보된 뒤 새 Sol design gate를 다시 통과해야 한다.

| 항목 | 의존성/완료 조건 |
|---|---|
| I1 관측 구현 | 이 문서와 field-to-source mapping 승인, 기존 owner evaluation의 단일 결과 직렬화, production output 불변; 별도 구현 승인 필요 |
| I2 로컬 검증 | synthetic lifecycle/trace, 기존 fixture equivalence, bounded-resource 및 schema consumer 검증; I1 완료 후 독립 validator 필요 |
| B 행동 설계 | I2 및 별도 물리 identity/two-sided evidence, 변경 predicate와 safety 반례 명시, fresh design gate 필요 |
| field qualification | canonical nine segments replay와 reviewed truth 비교; exact Y anchor 없이는 coordinate accuracy를 `NOT_EVALUATED`로 유지 |

주요 위험은 (1) 관측을 위해 evaluation을 다시 실행해 순서를 바꾸는 것, (2) confidence
공식을 복제하는 것, (3) telemetry ID가 authority가 되는 것, (4) unbounded memory,
(5) 누락을 false/0으로 오독하는 schema consumer, (6) historical source/run identity
혼동이다. 대응은 단일 evaluation serialization, explicit status, cap/missing marker,
on/off equivalence와 source attribution이다. 어떤 authoritative output이라도 달라지면
구현을 중지하고 관측 변경만 revert한다. rollback은 이 설계/링크와 향후 additive
schema만 철회하며 field FAIL evidence, 원본 report, golden을 덮어쓰거나 삭제하지 않는다.

## Named unknowns

다음은 문서화로 해소되지 않으며 행동 변경의 근거가 아니다: Base 실제 interface
최초 손실 stage; Accum raw detection 대 association 및 drain candidate/identity/
direction; owner-bounded selector abstain predicate; Check01 continuation predicate;
Check03 branch/source identity; Check04 chain creation event 수; Check05 raw Foam
object identity와 post-672 evidence necessity; Check06 confidence OR branch; Check07
row-member join과 private mean/현재 source median 관계; private build/config/member
join; exact reviewed Y anchors. interval-level field FAIL은 Y anchor 부재로
`NOT_EVALUATED`로 낮추지 않으며, coordinate accuracy만 anchor 부재 시
`NOT_EVALUATED`이다.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-PROPOSAL`, `OIL-HYPOTHESIS`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `TRACE-PUBLICATION`, `RESULT-PRESENTATION`
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: current logic map and failure registry details for the affected nodes/F01–F10; S11 responsibility architecture; R18 causal trace architecture/validation; R20 delayed-reacquisition architecture/validation; reviewed truth; and the R20 Windows consolidation/intake.
- Prior mechanisms rejected: new recovery owner, global threshold or entrance widening, motion-only/bootstrap authority, stale ID/coordinate transfer, Foam cross-veto, selector/projection repair, interpolation/carry, private case branch, confidence recomputation and trace authority.
- Preserved contracts: typed authority, bounded physical ownership, initial-state safety, source-driven same-frame provenance, independent Oil/Foam validity and composition, fail-closed ambiguity/material, exact selected-candidate/sequence/CSV equality and bounded resources.
- Difference from prior failures: this is a non-behavioral, owner-bound observational design. It serializes results already computed by the decision path and retains unknowns instead of substituting thresholds, repeated attempts or private identity.
- Logic-map impact: NONE — this document is `DESIGN ONLY — NOT IMPLEMENTED` and does not change the current control-flow owner map.
- Failure-registry impact: NONE — no new causal mechanism is asserted and existing F01–F10 guards remain unchanged.
