# Candidate-local RGB 입력과 고정 비교

현재 상태와 다음 행동은 [Work Plan](../../00-project/work-plan.md)이 소유한다.
이 기록은 [고정 후보 계약](../../20-architecture/s11-contextual-role-observation-design.md#candidate-local-rgb-compatibility-successor)의
실제 입력 준비와 단일 실행을 다룬다. 기존 native-surface 학습 결과를 바꾸거나
후보 허용을 native 경로·주변 픽셀의 물리 라벨로 확장하지 않는다.

## 실행 전 입력 고정

`31d6bdb`에서 [plan](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/plan.json),
adapter와 검증 조건을 먼저 커밋했다. 기존 역할·실용적 허용과 전체 후보 결합을
재실행하고 저장 결과와 일치시킨 뒤 원본 RGB 및 유효 mask의 7×7 patch를 검사했다.
source hash가 다른 sample4와 공개 영상을 각각 fit과 노출된 transfer로 분리했다.

[준비 결과](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/prepared.json)는
**INPUTS_READY**다. 전체 187개 기록 = Oil 후보 182개 + 비후보 context 4개 + Foam
후보 1개다. Oil 후보 165개는 필요한 floor/ceil 입력을 모두 갖추고, 17개는 입력
부족으로 남는다. 학습 대조 10개와 공개 비교 5개는 모두 입력이 있다. 불가 후보를
정상 음성으로 세거나 mask 밖 픽셀을 채우지 않았다.

준비 파일은 모든 후보, 각 변형의 patch 중심·개수·배열 hash, 원본·관련 source pin을
포함한다. 원본 픽셀 배열은 복제하지 않는다. 2,703,912-byte 출력의 JSON 표현만
압축해 parser 동등성을 확인한 424,387-byte 파일 하나를 보존했다. SHA-256은
`95af399faaf64f0f07a2ffd486af604527cb0225f6f140414613b7e3f24f7ad0`이다.
관리 실행 `s11-candidate-rgb-preflight-20261014-001`은 큰 중복을 제거하고 닫았으며,
이때 전체 관리 실행 29개 오류 0이었다. 이 단계는 모델을 만들거나 학습하지 않았다.

관련 후보·결합·역할·native 계약 테스트 138개가 통과했다. 실제 준비 entry도
완료했으며 학습은 별도로 준비 결과까지 커밋한 clean HEAD에서 한 번 실행한다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: a regional role preference loses practically accepted candidates before any selector can preserve them; RGB compatibility must retain both accepted alternatives and opposed controls.
- Prior mechanisms reviewed: old CR1 category collision and all-four public sign failure; B practical acceptance; original native-head N3 loss; source-qualified candidate bindings and exact floor/ceil support.
- Difference from prior failures: one fixed native RGB candidate-compatibility trial changes input information and supervision, with sample4-only fit and exposed public transfer. It does not retry native external-surface labels, tune the failed role threshold or choose a new production winner.
- Existing feature coverage: existing saved candidate population, original RGB, effective/glare masks and source pins; Recipe exclusions/templates unchanged, Local XY OFF, no D2 efficacy claim.
- Execution scope: completed input preparation followed by one predeclared offline 1,118-parameter / 1,000-step fit, full-population final inference and mean-color ablation. No production replay, report reading, O2 acceptance or Windows execution.
- Logic-map impact: NONE — offline diagnostic only; production owners and schemas unchanged.
- Failure-registry impact: NONE — no new failure family or accepted detector repair; this checks candidate-level input capability under existing evidence boundaries.
