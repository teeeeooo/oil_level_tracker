# S11 Windows comparison checkpoint and design handoff — 2026-10-16

**인계 기준:** `main`, `f63df4abc260ad4987fb8989d5828252947b94c8`까지의 결과.
이번 인계 변경은 문서뿐이며 디텍터 동작은 바꾸지 않는다. 아래는 체크포인트
시점의 요약이고, 이후 상태·권한은 [Work Plan](../../00-project/work-plan.md)이 소유한다.

**지금 Windows에서 추가로 확인할 항목은 없다.** 사용자는 이 지점에서
체크포인트와 handoff를 요청했다. 다음 재개 작업은 **721초 비유면에 대한
구체적인 수정안과 검증 기준 설계**다. 추가 CSV 추출이나 같은 영상 재실행부터
시작하지 않는다. 수정안·구현·향후 현장 검증이 완료됐다는 뜻은 아니다.

**FULL 전환 검증은 미완료다.** 끝난 것은 실행 전 상단 조건 확인이며,
조건 불일치로 ⑧ 비교 자체를 실행하지 않았다. 상단 관측·판정 조건을 정리한
뒤 실제 전환·유지와 기존 출력 보존을 Windows에서 검증해야 한다.
현재 Windows 요청 없음과 향후 Windows 검증 불필요를 혼동하지 않는다.

## 먼저 읽을 범위

1. [Work Plan](../../00-project/work-plan.md)의 맨 위 상태와 fixed execution order.
2. [721초 수신 및 코드 대조](../../50-diagnostics/s11/2026-10-15-initial-full-comparison.md#saved-trace-receipt--bounded-identity-intake-complete).
3. [현재 증거·독립성 설계](../../20-architecture/s11-physical-interface-evidence-repair-design.md#1-interface-evidence-and-independence)와
   [검증 계약](../../30-validation/s11-physical-interface-evidence-repair-validation.md).
   전체 witness 설계는 미채택이며 이미 구현된 동작으로 취급하지 않는다.
4. 실제 변경 owner는 [S11 skill](../../../.agents/skills/s11-detector-change/SKILL.md)과
   [logic-map quick index](../../20-architecture/s11-current-detector-logic-map.md#quick-start--design-index)로 좁힌다.
   별도 FULL 논의가 필요할 때만 [상단 preflight](2026-10-16-top-exit-full.md#windows-geometry-preflight-received--condition-failed)를 읽는다.

## 완료된 Windows 작업과 남은 경계

| 대상 | 체크포인트 결과 | 재개 시 의미 |
|---|---|---|
| ④ FULL+ON v2 | BASE 601행 중 Oil 303, Accum 601행 중 Oil 36; BASE FULL 전환 없음 | 비교 기준이며 채택된 제품 기본값은 아님. 수치 출력 수가 물리적 정확도를 뜻하지 않음 |
| ⑤ cost-first | BASE Oil 93, Accum 22; BASE refill 관측 소실 | REGRESSION / NOT_ADOPTED, 재실행·튜닝 대상 아님 |
| ⑥ candidate RGB | BASE Oil 0, Accum 3; 허용된 실제 계면도 제거 | REGRESSION / NOT_ADOPTED, review-006 미검토는 이 결정을 보류시키지 않음 |
| ⑦ Local XY | BASE Oil 254, Accum 14; 비유면 대체 출력과 허용 계면 소실 | REGRESSION / NOT_ADOPTED. 정정된 새 출력/소실/Y변경 집계까지 종료 |
| ⑧ top-exit FULL | CONDITION FAILED / NOT RUN | 허용 끝점 Y220.870, effective mask 상단 Y243, 마지막 전환 전 선택 Y352. 상단 접근 증거가 없어 FULL 미해결 |
| FULL 전환·유지 본검증 | **미실행 / 미검증** | 로컬에서 상단 관측·판정 조건을 정리한 뒤 Windows 비교 필요. 사전 확인 완료로 이 의무를 닫지 않음 |
| 721초 identity 조사 | `corroborated_material_path` → `anchor_corridor` → IFO v2 허용 → Y694 출력 | 잘못된 앵커 승인 경로 특정 완료. 최초 원시 측정 오류·구체적인 광학 원인은 미확인 |

세 개 비교에서 최종 Foam은 BASE 0 / Accum 40으로 해당 비교 범위에서 유지됐다.
이것이 향후 수정의 Foam 무영향을 보증하지는 않는다. 현재 기본 동작은
R22 + R22-3/O1이며, 실험 옵션은 기본 OFF다. **S11 ACTIVE / O2 OPEN / FIELD FAIL**을
유지한다. 전체 현장 인수와 사람이 보고서에서 움직임·불확실성을 이해하는지는
별도 미완료다.

원본 결과는 [초기 FULL·cost-first 기록](../../50-diagnostics/s11/2026-10-15-initial-full-comparison.md),
[RGB 결과](2026-10-14-candidate-rgb-trial.md#windows-rgb-result--2026-10-16),
[Local XY 정정 집계](2026-10-09-local-xy-implementation.md#saved-output-accounting-closeout--complete)를 재사용한다.

## 반드시 보존할 판단과 데이터 해석

- [정답 시간축](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md):
  BASE 550–652초 하강, 652–674초 회복, 674–675초 FULL 전환,
  675초 이후 FULL. 이전 663.6초 경계는 폐기됐으며 source Y는 아래로 증가한다.
- review-004/005의 복수 허용·대략적 일치·시각적 불확실성을 유지한다.
  강제 선택한 후보 하나만 정답으로 만들거나 주변 후보를 모두 오검출로 바꾸지 않는다.
  Accum f16076@670.5초의 허용 계면 손실은 중요한 양성 보존 대조다.
- 721초 비유면 판단과 723초 material veto, 771초 identity 보호는 재사용한다.
  아지랑이 원인은 미확인이지만 기존 비유면 판단을 철회하는 것은 아니다.
  review-007은 scope 승인, review-008은 BASE Y913 바닥벽 비유면 판단이다.
- 721초 확정 창은 offset 480–485, 약 2.5초, 관측 5개·앵커 표시 행 3개다.
  같은 행의 여러 source를 독립 앵커 프레임으로 더하지 않는다.
  `anchor_corridor`에 별도 motion 확정 조건을 소급 적용해 구현 오류라 하지 않는다.
- 교차 표현 지지값 0.4571은 적격 주변 후보 중 최대값이다. 독립 투표 수나
  계면 확률이 아니다. 실제로 지지한 peer와 측정의 독립성은 이번 전달 자료로
  확인되지 않았다. `semantic_sequence_available=False`도 미저장 키의 부재가
  아니라 코드와 통과 조건에 따른 조건부 추론이다.
- 최종 수치·선택·후보를 구분한다. 경로는 `record.sequence.candidates[]`이며
  witness offset을 이 점수 정렬 배열의 index로 쓰지 않는다. 원시 FULL likelihood는
  `record.state`, release 진단은 `record.sequence.state.sequence_material_phase_diagnostics`다.
- 기존 공간 Artifact veto는 활성이다. 참조 이미지 비교의 `diagnostic_only`나
  미저장 match 필드는 그 기능이 꺼졌다는 뜻이 아니다. FULL의 물리적 상단을
  effective mask 상단으로 바꾸거나 margin을 줄여 preflight를 통과시키지 않는다.

## 다음 작업의 첫 산출물

**현재 프레임의 계면 증거를 이용한 수정안 하나와 양성·음성 검증 계획**을 기존
설계 owner에서 구체화한다. 이 체크포인트에서는 새 알고리즘을 선정하지 않았다.

1. `oil_candidate_authority.py::evaluate_candidate_authority`와
   `oil_observation_resolver.py::_cross_representation_support`의 기존 책임을
   출발점으로 삼는다. normalized evidence, O1 witness/lineage, tracklet/IFO
   소비 경로를 확인해 재사용할 owner와 실제로 바꿀 조건을 명시한다.
2. 같은 경계를 관측한 후보의 지지가 언제 독립적인 물리 계면 근거가 되는지,
   미관측·반사·내부 구조와 어떻게 구분할지 설명한다. 이번 scalar 값만 보고
   임계값을 고르거나 모든 material-path를 막는 것을 수정안으로 삼지 않는다.
3. 721초 음성 억제와 review-004/005 양성 보존, 723/771초 보호 및 최종 Foam
   불변을 함께 검증할 방법을 정한다. 부분 불확실성과 복수 허용을 평가에 남긴다.
   FULL 상단 전환은 별도 미완료 항목으로 유지한다. 상단 관측·판정 조건을
   마련한 뒤 실제 전환·유지, 숫자 Oil 보존과 최종 Foam을 Windows에서 검증한다.
4. 구현·검증은 선택한 변경 범위에 맞춰 진행한다. 새 실험 전에는 기존 기능의
   실제 실행 범위와 통과/중단 기준을 먼저 기록한다. Windows가 실제로 필요해지는
   시점에만 최소 작업을 요청하며, 절차 갱신 때 짧은 전달 프롬프트도 제공한다.

사용자의 기존 커밋·푸시 자율 권한은 유지한다. 현재 요청은 체크포인트 준비이므로
이번 턴에서 후속 구현이나 실험을 시작하지 않는다. 사용자 판단이 필요한 물리적
의미나 Windows 작업 경계에 도달하면 그 이유와 필요한 범위를 알린다.

## 자료 위치와 인계 범위

④ 기준 bundle은 Windows의
`0.windows_diagnostic/bundle/oil_level_analysis_22-3_initial_ON_v2_20261015_171421/`다.
기존 review-001~008은 사용자의
`C:\0.Coding\2.Reference\Oil level tracker\0.windows_diagnostic\data\reviews\` 구조에 남긴다.
review-006은 **unreviewed/pending 보존**, 현재 추가 질문 대상이 아니다.
Windows는 Git clone 없이 GitHub 소스 ZIP을 사용하는 격리 환경이다.

이번 인계는 저장소 문서와 사용자 전달 결과를 연결한다. 비공개 영상·원본 bundle·
labels/replies/images가 이 저장소나 Mac에 복사됐다는 뜻은 아니다. 기존 자료를
이동·삭제·재포장하지 않는다. 앞으로 생성할 대용량 출력은 관리되는
`sample/output/` 아래에 둔다. 저장소 용량 정리와 성능 개선은 별도 유보다.

## 재개용 짧은 프롬프트

```text
Oil Level Tracker 작업을 이어가자.
docs/00-project/work-plan.md와
docs/60-evidence/s11/2026-10-16-windows-comparison-checkpoint.md를 먼저 읽어줘.
현재 Windows 추가 확인은 없고, 세 후보 비교·집계와 721초 조사까지 완료됐어.
다음은 721초 비유면의 앵커 승인을 개선할 수정안과 검증 기준 설계야.
review-004/005의 복수 허용·불확실성, 723/771초 보호와 Foam을 보존해줘.
FULL은 사전 조건 확인만 끝났고, 조건 불일치로 ⑧ 본검증은 실행하지 않았어.
상단 관측·판정 조건을 정리한 뒤 Windows 전환·유지 검증이 남아 있어.
완료된 CSV 분석이나 Windows 재실행부터 시작하지 말고,
수정안을 구체화한 뒤 그 범위로 진행해줘. 커밋·푸시는 자율적으로 해도 돼.
내 판단이나 Windows 작업이 필요한 지점에서는 멈추고 알려줘.
```

현재 Windows 에이전트에 새로 보낼 작업은 없다. 필요할 때 공유할 완료 안내는
[기존 절차의 짧은 프롬프트](../../40-operations/s11-current-windows-field-qualification.md#721-second-identity-investigation)를 그대로 사용한다.

## 체크포인트 검증 범위

문서 governance와 변경 형식 검사, 추가·변경된 상대 링크/anchor 16개가 통과했다.
기존 managed run 81개는 산출물 관리 검사에서 오류 0건이며 새 run은 만들지 않았다.
이번 작업에서 디텍터·영상·CSV·물리적 정확도 테스트를 다시 수행하지 않았다.
원격 게시와 최종 커밋은 Git 이력으로 확인한다. 이 문서의 기준 커밋은 인계 전
결과를 식별하며, 문서 자신을 포함한 커밋으로 바꿔 적지 않는다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: the received 721 s negative gains anchor authority through corroborated_material_path and reaches final Y694. Its earliest misleading raw measurement is unknown. Top-exit separately fails endpoint reachability before Windows execution; no new causal measurement is made here.
- Existing feature coverage: checkpoint reuses ④ initial-FULL v2 and configured spatial Artifact/mask setup, with cost-first/RGB/Local XY/top-exit OFF. The three rejected comparisons, unchanged compared Foam and failed geometry preflight retain their original scopes. This handoff changes neither input setup nor evidence consumers.
- Execution scope: documentation and navigation preparation at f63df4a; no detector, private-video, model, CSV replay or new human review. Windows evidence is transferred, not independently re-extracted. Existing source/control findings are linked; a successor discriminator remains unselected.
- Logic-map impact: NONE — current implementation owners and control flow are unchanged; the handoff routes the next reader to those owners.
- Failure-registry impact: NONE — known identity, lifecycle and provenance limits are preserved; no new detector mechanism or field repair is claimed.
