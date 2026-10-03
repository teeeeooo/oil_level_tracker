# 2026-10-03 문서 정리 기록

- 기준 HEAD: `aa0d1964bf493732fbe33bbdda33f4449f817b47` (`main`), 시작 작업 트리 clean.
- 범위: 첨부 감사 ZIP 5개 전체 대조, 날짜순 색인, 역사 문서 이동, 현재 상태 문서 축약, 관리 규칙.
- 권한: 사용자의 2026-10-03 문서 정리 실행 요청. 첨부의 조사 당시 편집 보류를 이번 정리 허용 범위와 구분했다.
- 이 문서는 완료된 정리의 기록이다. 현재 상태는 [Work Plan](../../../00-project/work-plan.md), 관리 규칙은 [문서 라우터](../../../README.md#document-maintenance-lifecycle)가 소유한다.

## 첨부 검토와 적용 범위

첨부 `oil-level-tracker-docs-audit-2026-10-03.zip`의 계획, 관리 규칙, 날짜순
목록, JSON inventory, 검증 JSON을 모두 읽고 대조했다. HEAD, 246개 경로,
문서 전체 SHA-256 map digest가 첨부 감사와 일치했다. 첨부 파일별 hash와
원본/결과 매핑은 [migration manifest](2026-10-03-docs-migration.json)에 있다.

첨부의 분류체계·기존 basename·완료 증거 보관 원칙을 채택했다. 다운로드용
규칙을 또 다른 현행 owner로 복사하지 않고 `docs/README.md`에 통합했다.
기존 날짜순 자료는 실제 이동 후 경로에 맞춘 [색인](../../../catalog-by-created-date.md)으로 반영했다.
원문 감사 첨부의 제안/미실행 상태를 이번 실행 결과로 덮어쓰지 않았다.

## 아카이브 결과와 의무 승계

A군 7개를 `90-archive/20-architecture/2026` 및
`90-archive/30-validation/2026`으로 이동했다. basename·제목·역사 판정·수치·
본문 의미는 보존하고, 상대 링크 목적지만 재계산했다. 코드·테스트의 직접
소비자 및 보호 문서에서 이동 대상에 대한 유입 참조는 없었다.

| 대상 | 역사적 책임 / 현재 의무의 근거 |
|---|---|
| [Subtractive 설계](../../20-architecture/2026/s11-subtractive-detector-simplification-architecture.md) | A–D 경로는 역사 구조. proposal·ambiguity·hard-safety 의무는 [책임 설계 §Historical preservation boundary](../../../20-architecture/s11-detector-responsibility-architecture.md#historical-preservation-boundary)와 [공통 검증 §Controlled preservation surface](../../../30-validation/s11-real-field-detector-effectiveness.md#controlled-preservation-surface)가 명시적으로 보존. |
| [R2 설계](../../20-architecture/2026/s11-foam-spatial-authority-repair-architecture.md) / [검증](../../30-validation/2026/s11-foam-spatial-authority-repair-validation.md) | D5/Foam-to-Oil 권한은 폐기된 구조. genuine Foam·glare·collision·weak-interface 보호는 같은 공통 검증에 유지. [책임 설계 §Hard safety boundary](../../../20-architecture/s11-detector-responsibility-architecture.md#hard-safety-boundary)가 과거 Foam 기반 Oil 권한 제거를 명시. |
| [R3 설계](../../20-architecture/2026/s11-sequence-observability-integrity-architecture.md) / [검증](../../30-validation/2026/s11-sequence-observability-integrity-validation.md) | border-cap·static/glare·Foam·sample3 음성군은 공통 검증의 controlled preservation 및 [cross-revision 영상 의무](../../../30-validation/s11-real-field-detector-effectiveness.md#cross-revision-checked-in-video-obligations)에 유지. 과거 exact-output 및 owner topology는 현행 의무가 아님. |
| [R4 설계](../../20-architecture/2026/s11-r4-field-residual-authority-architecture.md) / [검증](../../30-validation/2026/s11-r4-field-residual-authority-validation.md) | 과거 static-overlap/onset 수치·D5 routing은 역사 구현. 회귀군은 공통 검증, retrospective 책임은 [불변 관측 경계](../../../20-architecture/initial-state-retrospective-reconstruction-architecture.md#placement-and-immutable-observation-boundary), 보고서 의미는 [Foam presentation episodes](../../../20-architecture/result-observation-report-architecture.md#foam-presentation-episodes)와 [graph 검증](../../../30-validation/result-observation-report-validation.md#static-and-interactive-graph)에 유지. |

각 문서의 기존 HISTORICAL PRE-R6 선언과 명시적 후속 R6 링크도 보존한다.
R6 자체는 역사 문서이며 현재 실행 gate가 아니다. 현재 의무는 위의 지속 owner와
현재 R22/관측 계약에서 읽는다. 과거 조건을 재실행하거나 안전 fixture를 삭제하지 않았다.

B군 20개는 현 위치에 유지했다. 버전 번호만으로 승계를 확정하지 않는다.
파일별 유지 사유와 재검토 조건은 manifest에 기록했다.

- R9/R10 및 R14: Artifact 편집·선택·일괄 적용/삭제·그래프 계약이 섞여 있어 제품/UI 책임의 조항별 승계가 더 필요하다.
- R11–R13/R15/R16: typed evidence, compatibility, proposal, tracklet·material lifecycle, resource 및 검증 의무의 완전한 승계가 확인되지 않았다.
- R18 causal trace: 완료된 실행이어도 관측 필드와 직렬화 의무까지 전부 대체됐다는 뜻은 아니다.
- R20 decision witness: R21이 개념을 구현했지만 R20의 전체 필드·matrix와 동등하다는 판정은 하지 않았다. 남은 기록을 폐기하지 않는다.

S6–S10 및 S11 완료 증거는 정상 보관 위치인 `60-evidence`에 유지했다.
JSON 10개, patch 1개, 9월/10월 감사 원문, 현재 operations와 truth는 바이트 그대로다.

## 현재 상태 문서 정리와 정보 보존

Work Plan은 585줄에서 157줄로 줄이고 사용 중 경로 및 기존 level-2 앵커를
유지했다. 원본 전체는 위 기준 HEAD의 `docs/00-project/work-plan.md` Git blob에
보존된다. 별도의 계속 갱신하는 history 원장은 만들지 않았다.

| 원본 줄 | 현재 보존 위치 / 처리 |
|---|---|
| 1–9 | Work Plan 머리말: S11 ACTIVE, FIELD FAIL, O2 OPEN, Windows color-side 다음 행동 |
| 10–186 | §S11 work-item ledger / §Next transition; 완료 수치는 기존 각 W/O evidence owner에 연결 |
| 187–219 | §Accepted local candidate; R22 behavior, R22-3 diagnostic, R21/R22-2 비교 기준 분리; 측정 수치는 R22/O1 증거에 유지 |
| 220–254 | §Current authorization boundary / §Open field risks and named unknowns; 유효 권한·제한·Sample4 runtime provenance 보존 |
| 255–268 | §Preserved contracts / §Open field risks and named unknowns; same-frame, independent validity, ambiguity, 미검증 field 보존 |
| 269–305 | §Active follow-up design; 현재 설계 링크 유지, checkpoint 인과 세부는 기존 진단 원문에 유지 |
| 306–570 | §Next transition / §Active follow-up design / §Open field risks and named unknowns; review/score 실험 세부는 기존 evidence로 연결, 원본 전사는 기준 Git blob에 보존 |
| 571–585 | §Current authority links 및 각 본문 owner 링크 |

회수 가능한 원문과 증거를 남기며 현재 위험·금지·다음 행동을 삭제하지 않았다.
이미 완료된 W2 geometry, W4-R0/R1/R3, fixed-score/locality/profile 조사를 재개하지
않는다. SPL#2/#3 유보, calibration/scalar truth의 공백, canonical source fingerprint와
Sample4 runtime의 미해결 provenance가 현행 문서에 남아 있다.

roadmap은 52줄을 유지했다. R21에 이미 구현된 decision-witness가 여전히
optional R20 유보 작업이라는 낡은 예시만 제거했다. 근거는
[retained commitments](../../../00-project/retained-commitments.md#unresolved-s11-field-behavior-surfaces)와
[R21 관측 구현](../../../20-architecture/s11-r21-truth-preserving-detector-repair-architecture.md#additive-decision-witness-observability)이다.
마일스톤 순서·공식 상태는 바꾸지 않았다.

recall-index는 긴 실험 경과를 주제별 짧은 경로로 교체했다.
기존 archive의 Work Plan 상대경로 오류 1건을 수정했다.
기존 S11 routing design에는 이번 문서 수명·archive routing과 History Review 근거를 추가했다.
AGENTS/Skills 및 governance checker 자체는 변경하지 않았다.

## 검증과 복구

검증 결과는 같은 배치의 manifest에 기록했다.

- 색인 249개: 실제 파일과 일치하며 중복·누락 없이 폴더/날짜순이다.
- 기존 246개 최초 Git 추가일: KST로 재확인했고 첨부 Markdown/JSON 목록과 모두 일치한다.
- 로컬 Markdown 대상 1,109건, 제목 앵커 99건: 오류 없음. 기존 좌표 표기 세 줄은 링크 정의가 아니므로 원문 확인 후 제외했다.
- 이동 7개: 상대 링크 목적지 외 원문 바이트 동일. 기존 문서 233개 및 허용 편집 외 보호 문서 152개는 경로·내용 그대로다.
- 기존 machine artifact 11개와 문서 외 추적 파일 482개: 내용 동일.
- 기존 detector governance 및 `git diff --check`: 통과.

이는 detector 정확도나 Windows 현장 검증이 아니다. commit/push는 수행하지 않았다.

복구 시 manifest의 원본 경로와 기준 Git blob을 사용하여 해당 파일만 복원하고,
이번 배치가 만든 목적지와 산출물만 제거한다. 다른 사용자의 변경은 건드리지 않는다.
`git reset --hard` 또는 광범위 clean은 사용하지 않는다.
