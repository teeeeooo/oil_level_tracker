# S11 기존 자료 재사용 단계 체크포인트 / 인수인계 — 2026-10-13

사용자의 체크포인트·handoff 요청에 따른 재개용 스냅샷이다. 현행 상태·권한·다음
작업은 [Work Plan](../../00-project/work-plan.md)이 소유한다. 이전
[material-role handoff](2026-10-13-material-role-handoff.md)는 R/L 비교 직후의
역사 기록으로 보존하며, 그 이후 N1–N5 시험과 관리 보완까지 이 문서에서 연결한다.

## 체크포인트

- 저장소 `/Users/sunjaekim/Developer/oil_level_tracker`, 브랜치 `main`.
- 인계 준비 기준 HEAD: **`05a0066f4996005bbcbc6ce66bc3b3efd13e7361`**.
  준비 시작 시 실제 원격 main과 일치했고, clean 작업 트리·등록 worktree 하나였다.
- 이 파일을 추가한 커밋이 이번 인계 체크포인트다. 다음 세션에서는 최신 HEAD와
  Work Plan을 먼저 확인한다. 이 파일의 커밋은 다음 명령으로 찾을 수 있다.
  `git log -1 --format='%H' -- docs/60-evidence/s11/2026-10-13-existing-material-handoff.md`
- 인계 시점 상태: **S11 ACTIVE / O1 로컬 수용 / O2 OPEN / FIELD FAIL /
  R22 behavior·R22-3/O1 diagnostics / Local XY OFF / R23 미개방**.
- 현재 미응답 역할 질문이나 실행 대기 중인 Windows 요청은 없다. 사용자 요청에
  따라 여기서 인계하며, 아래 기존 자료 대조·후속 시험 명세는 아직 작성하지 않았다.

## 완료한 일과 유지할 판단

| 완료 범위 | 이어받을 의미와 근거 |
|---|---|
| 첨부 명세·산출물 인수와 정리 | [10월 13일 인수 기록](2026-10-13-program-review-intake.md). 원본은 보존하고 기존 설계·검증 owner에 반영했다. WP01–WP10의 현재 상태는 Work Plan에만 둔다. |
| N1–N5 역할 결속 | [N1–N3](2026-10-13-native-role-qualification.md), [N4/N5 응답과 시험](2026-10-13-native-surface-trial.md). N1은 외부 Foam/흔들리는 액체 상단 해석 모두 허용, N2/N4는 내부 Foam 변화, N3는 실제 외부 Foam 상단, N5는 원형 rim 구조물이다. N4의 유리 원형 무늬 영향은 사용자 추정이며 확정 원인이 아니다. |
| 한 번의 고정 native 학습 시험 | water의 N1/N2를 학습하고 sample4의 N3/N4/N5를 평가했다. N4/N5는 배제했지만 **필수 양성 N3도 배제**하여 `CLOSED_WITHOUT_PROMOTION`. 새 생산 소비자나 raw-front 복구는 없다. |
| Artifact·마스크 이력 복원 | [D2 등록 비교](2026-10-08-d2-recipe-artifact-comparison.md), [Local XY A–D](2026-10-09-local-xy-spec-intake.md), [구현 시험](2026-10-09-local-xy-implementation.md), [후속 원인 분석](../../50-diagnostics/s11/2026-10-09-local-xy-sequence-causality.md)을 재사용한다. 일부 잘못된 후보 제거와 실제 관측 손실·후속 선택 문제를 함께 보아야 한다. 닫힌 비교를 다시 최초 실험으로 제안하지 않는다. |
| 연구 관리 보완 | `365e39b`와 `05a0066`에서 기존 Skill·기능표·흐름도·정책·검사기를 연결했다. Recipe 등 입력 정의의 누락도 검사에 포함했다. 사용자 수용 완료이며 추가 관리 장치 작업은 남아 있지 않다. |

고정 시험의 다섯 경로는 두 촬영원에서 왔다. 학습 자료 부족과 표현 한계 중
어느 것이 N3 손실을 만들었는지는 분리되지 않았다. 이미 확보한 영상이 부족하다고
결론 내리거나 같은 시험의 seed/crop/head/threshold를 조정해 재개하지 않는다.
N1–N5는 노출된 개발 대조군이다. N3를 학습에 넣은 뒤 같은 N3를 새 전이 성과로
세지 않으며, 공유 픽셀·같은 촬영원의 프레임을 독립 평가 자료로 분할하지 않는다.

현재 [sample4 Recipe](../../../sample/sample4.oilrecipe)는 exclusion 0개·Artifact
template 0개다. 따라서 그 입력의 raw 시험으로 활성화된 Recipe 방어의 실패를
입증할 수 없다. 제외 영역은 Oil/Foam 공간 지원을 함께 제거하고, Artifact template은
일치 후보 전체를 거부하며, 구조물 reference 확인은 진단용 근거다. 이 구분과 실제
실행 여부를 [기능표](../../20-architecture/s11-current-detector-logic-map.md#existing-features-and-run-coverage)에서
추적한다. 과거 D2/Local XY는 N5 하단 rim의 정확한 fragment 시험이 아니므로 그
결과를 모든 마스크의 무용성이나 새 N5 설정의 성공으로 확대하지 않는다.

## 재개 후 첫 산출물

**기존 자료의 역할·관측 근거 대조표와 후속 시험 명세**를 준비한다. 별도 자료 확보나
재학습을 선행 조건으로 두지 않는다. 현재 [관측 설계](../../20-architecture/s11-contextual-role-observation-design.md#native-side-role-observation-and-g0-binding-contract)와
[검증 계약](../../30-validation/s11-interface-observability-witness-validation.md#native-side-role-readiness-and-feasibility)에
실제 변경을 반영하고, 기존 manifest·판정을 참조한다.

1. [water/sample5·beer/sample6·milk/sample7](../../50-diagnostics/s11/2026-10-09-public-video-intake.md),
   [public-miso](../../50-diagnostics/s11/2026-10-12-public-compressor-source.md),
   [Froid117/public-egenie](../../50-diagnostics/s11/2026-10-13-public-compressor-input.md)와
   기존 로컬 자료를 촬영원별로 대조한다. sample3의 기존 분석 제한을 유지한다.
2. 각 자료에 **원문 판정과 정밀도, native 경로 대응, 실제 입력 픽셀과 공유 지원,
   Recipe/실행 설정, 이전 노출·학습 이력, 사용 가능 목적과 미확정점**을 연결한다.
   구간 판정을 구간 내 모든 edge의 정답으로 확장하지 않는다. B는 실용 허용 근사이며
   정밀 물리 양성으로 승격하지 않는다. Froid117의 판정 불가는 그대로 유지한다.
3. 촬영원 단위의 학습·평가 분리와 필요한 양성·반대 사례를 정한다. 학습에 쓰지 않은
   평가 자료와 연구 전체에서 전혀 보지 않은 holdout은 구분한다. 새 영상 요청 전에
   기존 자료로 충족되는 부분과 실제로 빠진 대응 관계부터 명시한다.
4. N3 같은 실제 상단 보존과 N4 내부 변화·N5 구조물 배제를 함께 통과 기준에 넣는다.
   Artifact·마스크의 사용/비사용, 원시 관측·후보 거부·완료 시퀀스·report 중 실행 범위와
   한계를 명시한다. 기존의 실패와 다른 관측 근거·데이터 범위·중단 조건을 제시한다.

새 학습은 이 체크포인트의 실행 범위가 아니다. 후속 학습에는 구체적인 data/split
계약이 먼저 필요하다. 이미 닫힌 질문은 재질문하지 않고, 재사용 검토 후에도 필요한
물리 판정이나 실질적인 설계 선택이 남을 때 사용자 판단을 요청한다.

후속 수용 순서는 Work Plan을 따른다. O2 수용 전 **V5 Windows shadow**가 필요하며
그 지점에서는 멈추고 알린다. Oil 오선택 억제와 독립 양성 admission 복구는 별도
변경이고, Foam은 올바른 raw upper가 확보된 뒤에만 downstream episode 손실을 다룬다.
최종 목표는 잘못된 report 극값 억제, 실제 방향·반전·refill 보존과 독립 Foam 상단
복구이며 Windows 9개 canonical 구간·독립 report 판독 의무가 남는다.

## 운영·검증 인계

- 커밋·푸시는 기존 자율 권한을 유지한다. 실질적인 사용자 판단이나 Windows 작업이
  필요할 때 멈춘다. 현재 별도 승인 대기는 없고, 새 sub-agent 위임도 승인되지 않았다.
- 관리 방식은 기존 [S11 Skill](../../../.agents/skills/s11-detector-change/SKILL.md),
  [관리 계약](../../30-validation/s11-detector-change-governance.md#maintenance-at-change-boundaries),
  검사기와 기존 pre-push/CI를 사용한다. 변경 작성자가 영향받는 문서를 함께 관리한다.
  형식 검사 통과가 내용의 정확성이나 실행 경로 사용을 증명하지는 않는다.
- 이번 인계에서 저장된 [시험 manifest](../../50-diagnostics/s11/2026-10-13-native-surface-trial/trial-manifest.json)의
  **source 11개·입력 판정 문서 4개** SHA-256, manifest/readout의 저장 검증 hash를 확인했다.
  모든 원본 RGB·영상·환경을 다시 검증했다는 주장은 아니다.
- `experiment_artifacts.py check`: **관리 run 22개, 오류 0**. 새 연구 run·영상 복제·ZIP·
  worktree를 만들지 않았다. Git 밖의 입력과 단일 CR1 환경은 기존 manifest 및
  [보존 절차](../../40-operations/experiment-artifact-lifecycle.md)를 따른다.
  새 clone만으로 로컬 입력 전체가 준비되었다고 가정하지 않는다.
- 직전 관리 코드 변경의 **44 tests PASS**, native 시험의 기록된 **49 tests PASS**를
  해당 범위에서 재사용한다. 이번 문서 인계로 detector·학습·Windows·전체 replay를
  재실행하지 않았다. 이번 인계의 **문서 링크·anchor 23개, 재개 경로, governance,
  diff 검사 PASS**이며 runtime/tooling source 변경은 없다.

## 재개용 메시지

```text
oil_level_tracker에서 이어서 진행해줘.
docs/00-project/work-plan.md와
docs/60-evidence/s11/2026-10-13-existing-material-handoff.md를 읽고,
기존 영상·판정·Artifact/마스크 이력을 재사용해 역할·관측 근거 대조표와
후속 시험 명세부터 작성해줘. 닫힌 시험을 재실행하거나 새 학습부터 시작하지 말고,
커밋·푸시는 자율적으로 진행하되 내 판단이나 Windows 작업이 필요하면 멈춰 알려줘.
```

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `FOAM-CANDIDATE`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: 새 원인 판정 없음. 고정 offline 관측기의 N3 양성 손실과 과거 D2/Local XY의 선택·시퀀스 손실을 기존 근거 범위에서 연결하며, 생산 detector의 새 earliest-loss 주장은 하지 않음.
- Existing feature coverage: sample4의 저장 exclusion/template은 각각 0개임을 확인. 공간 mask, 후보 Artifact 거부, reference 진단, Local XY OFF 및 완료 시퀀스를 구분하고 기존 기능표·D2 후속 결과로 재개를 연결함. 실제 설정은 변경하지 않음.
- Execution scope: 저장소·저장 기록·15개 source/판정 문서 pin·manifest/readout hash·관리 run의 읽기 전용 확인 및 인계 문서 작성. 영상 decode, 모델 실행, 검출, Windows, report replay 없음.
- Logic-map impact: NONE — 현재 기능표와 실행 경로는 바뀌지 않고 기존 owner·필수 검토 절차로 재개를 연결함.
- Failure-registry impact: NONE — 새 실패 family나 검출 수용 근거를 추가하지 않고 닫힌 결과와 다음 계획을 인계함.
