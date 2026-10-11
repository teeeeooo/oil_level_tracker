# S11 현 main 프로그램 감사 명세 인수·타당성 검토 — 2026-10-11

**범위:** 제공 ZIP의 명세·증거, 연결된 Mac의 관련 worktree와 상세 감사 산출물
확인·보존·중복 정리, 명세 검토 및 후속 계획 반영. 새 detector 구현·실험은 아니다.
**시작:** clean `main` = `origin/main` =
`4d84f70c5026d92330628bbae7650ac6288a8e12`; 원격 fetch 후에도 동일했다.
**결론:** 원인 분리와 P5 우선 방향은 타당하다. 구체 역할 연산은 아직 미선정이며,
운영 연결 전 기본 실행의 원인 연결 및 별도 수용 설계가 필요하다.
S11 ACTIVE / O2 OPEN / FIELD FAIL, Local XY OFF와 기존 종료 실험을 유지한다.

## 보존과 배치

| 자료 | 위치 | 보존 범위 |
|---|---|---|
| 첨부 원본 9파일 | [원본 안내](../../70-reference/s11-program-audit-2026-10-11/README.md), [명세](../../70-reference/s11-program-audit-2026-10-11/S11-program-audit-and-detector-work-spec.md) | README·명세·SHA256SUMS·JSON 6개, 파일명/bytes 보존. 체크섬 8/8 일치 |
| 로컬 감사 산출물 | [import manifest](../../70-reference/s11-program-audit-2026-10-11/import-manifest.json) | 기존 61파일 전부 분류. 일반 파일 57개 중 고유 52개 이동, 동일 JSON 5개는 첨부 원본 재사용. ZIP/Base64 4개는 내부 17 member와 decode 결과까지 확인 |
| 전체 기본 replay | [native receipt](../../70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-current-default.json) | 전체 113행 CSV, 31 events, raw/completed hash, source/runtime/Recipe/truth identity. 첨부 12개 checkpoint 요약과 구별 |
| 전체 P5 재검산 | [native P5](../../70-reference/s11-program-audit-2026-10-11/native-evidence/p5-independent-verification.json) | 첨부 요약의 모든 필드를 포함하는 원본 388,846 bytes |
| 이미지·기존 시험 | [native evidence](../../70-reference/s11-program-audit-2026-10-11/native-evidence/) | crop 37개·contact sheet 6개, 과거 263건 JUnit/log, 원본 수집 스크립트·요약·실행 로그 |
| 이번 직접 검증 | [기계 receipt](2026-10-11-program-audit-intake.json) | 보존 hash·source Git object·저장 결과 교차검산·정리 결과. 과거 시험과 구분 |

`70-reference`는 외부 원문과 그 감사에서 나온 원본 산출물의 출처를 소유한다.
이 문서는 이번 인수의 판단·검증을 소유하고, 채택한 설계/검증 조건은 기존
Witness Architecture/Validation, 진행 순서는 Work Plan에 반영했다.
원문과 machine 기록의 과거 경로·수치·판정은 고치지 않았다. 이동된 파일은
manifest의 `source → preserved_at`으로 찾는다. 입력 영상, upstream raster/NPZ,
환경과 Git 이력은 별도이며 패키지 하나만으로 재실행 가능한 bundle은 아니다.
원래 replay harness가 삭제한 임시 HTML report는 이 패키지에도 없다.
원본 Python 수집 스크립트는 역사 자료이며 production/test discovery에 등록하지 않는다.

## 타당성 판단과 반영

| 항목 | 검토 결과 | 반영 또는 제한 |
|---|---|---|
| 원인과 개입 순서 | 타당 | sample4의 component→front 축약과 water A의 밝기 기반 support 손실을 구분. raw front가 잘못됐을 때 episode 완화로 우회하지 않음 |
| 기본 sample4 결과 | 저장 원본으로 확인 | 101/113 유효 Oil 수치는 검출 정확도가 아님. 44 s의 Y822가 최대 Oil event를 구성하며, 기존 검토 target Y844와 다른 점을 주요 해석 위험으로 보존 |
| scoped/FULL 원인과 default/NONE 결과 | 연결 범위 제한이 핵심 | 새 NONE receipt에는 raw trace가 없음. P5의 Y813→Y833 원인을 기본 실행의 같은 단계로 자동 전이하지 않고, 운영 개입 전 같은 설정의 candidate/owner/public 연결과 debug equality를 검증 |
| 역할 판별 제안 | 방향은 타당, 구현 명세는 미완성 | 실제 support·연산/수식·동률/미측정·수치 규칙·자원 bound·한 ablation을 동결해야 함. 기존 네 band/plane/step/ribbon/CBR-1/P2-S1과 구체적으로 다른 정보가 없으면 재명명 실행하지 않음 |
| P1·P2-S1 | 재개 불필요 | P1은 offline 표현 도구로 유지. P2-S1의 계산 정합성과 판별 실패를 구분하고 threshold/reference/transform 조정 금지 |
| Foam/Oil 의존성 | 명시적 분리가 필요 | P5는 Oil association 완료를 기다리지 않고 설계 가능. 자기 raw-front 수용 계약이 필요하며, typed Witness 소비자는 기존 O2/O3 gate를 충족해야 함. Foam 국소 성공이 Oil/O2 수용을 대신하지 않음 |
| 전체 P0–P7 완료 경로 | 유지할 가치 있음 | P5-a 고정 비교 → 수용된 raw-front 연결/P5-c 조건부 → O2/O3 이후 Oil association·필요 phase → 통합·Windows·report → 명시적 종료/제한/실패 결정 |
| A/B/C/U·report-only 검토 | 평가 관점으로 채택 | 하나의 잘못된 점도 극값·사건을 바꾸면 A/B가 될 수 있음. 보호 구간·허용 잔여를 비교 전에 고정. 기존 report를 보존해 기대 답을 모르는 검토자가 판독해야 함 |
| 1초 cadence·holdout·현장 | 기존 계약 그대로 | 판독된 가시적·움직이는 같은 Oil에만 적용. 이웃 frame은 holdout이 아니며 9구간·O2 shadow와 최종 field gate를 합치지 않음 |
| 개발일 timebox | 운영 제안으로만 사용 | 측정된 일정/완료 약속 아님. 한 구현+한 ablation 후 계속/종료를 결정하되 수용 절차를 생략하지 않음 |

현재 `_detached_material_phenotype`와 `_component_evidence`는 component의
상하 극값을 front로 사용한다. 기존 코드와 저장 P5 결과는 명세의 원인 설명을
지지한다. 이것이 새로운 역할 판별기의 성공 가능성을 증명하지는 않는다.
참조 논문의 [경계 주변 관측](https://arxiv.org/abs/1404.7174)과
[용기 곡률/대칭 가정](https://arxiv.org/abs/1506.00168)은 공식 초록과 부합한다.
이 검토에서는 이를 sight glass 성능 보장이나 새 곡률 heuristic의 근거로 채택하지 않았다.

즉시 다음 산출물은 실제 연산과 반례를 명시한 **하나의 P5-a preflight**다.
운영 코드 변경은 이 인수 범위에 포함하지 않는다. 현재 실행 순서와 단계별
진입/완료/중단 조건은 [Work Plan](../../00-project/work-plan.md#adopted-program-and-immediate-p5-source-checkpoint),
책임 경계는 [architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#boundary-local-role-feasibility--october-11-audit-adoption),
수용 조건은 [validation](../../30-validation/s11-interface-observability-witness-validation.md#boundary-local-role-feasibility-and-default-run-linkage)에 있다.
Roadmap의 순서·상태와 retained commitments는 바꾸지 않았다.

## 직접 검증과 한계

- 첨부 9파일, native 일반 파일 57개, 컨테이너 내부 17 member의 보존 hash 확인.
  두 Base64는 각각 원래 ZIP과 완전히 동일하게 decode된다.
- source ledger의 27개 Git object를 지정 ref에서 읽어 SHA-256·행 수 일치 확인.
  현재 production 221파일, replay harness와 영상/Recipe/truth 3개 pin도 일치했다.
- full native CSV 113행에서 Oil 101/Foam 26 유효 수치, 시간 배열 0–56 s/0.5 s,
  첨부 checkpoint 12개와 event 3개를 검산했다. 전체/선택 요약은 각각 31/3 events를
  보존하며 모두 native 기록과 일치한다. 수치 간격 Oil 2.5 s/Foam 1.0 s는
  물리적 동일 계면 cadence가 아닌 미확인 수치의 간격이다.
- P2의 readout/preflight/verifier hash와 dominated-pair 부등식 일치 확인.
  P5 첨부 요약은 full native 결과의 정확한 부분집합이며 입력 322개와 runner hash도 일치.
  이미 수행된 비용·stage 재계산을 새로 실행한 것으로 세지 않았다.
- 원본 영상 6개의 hash/크기, 기존 full-frame PNG 9개의 raw BGR hash를 확인했다.
  보존 PNG 43개를 decode 검사하고 contact sheet 6개를 직접 보았다.
  영상 37 frame을 이번에 다시 decode하거나 새로운 물리 truth를 만든 것은 아니다.
- 과거 JUnit이 13개 파일의 263 passed / 실패·오류·skip 0을 담는지 확인했다.
  문서 인수이므로 pytest·detector·Windows·report 이해도 평가를 반복하지 않았다.

추가·변경한 로컬 링크/앵커 93개와 신규 카탈로그 64파일, S11 governance 및
전체 변경의 `git diff --check`를 통과했다. 제공 원문의 공백도 변경하지 않았다.

기본 출력의 수치·event 일치는 보존 및 계산 검증이다. 주요 움직임의 실제 개선,
새 classifier, full canonical suite, 독립 holdout 또는 field PASS를 뜻하지 않는다.

## 워크트리와 중복 정리

`git worktree list`, `.git/worktrees`, Codex managed worktree의 Git 연결과
Developer의 관련 sibling checkout을 확인했다. 이 Mac에는 현재 main 하나만
있으며 병합할 활성 worktree 변경은 없다. 이전 P1 worktree 정리는
[앞선 통합 기록](2026-10-11-program-intake.md#정리-범위와-재현)에서 완료됐다.
과거 실험 브랜치 ref를 중복 worktree로 세지 않았으며, 기존 미채택 실험 코드를
정리 명목으로 삭제하거나 main으로 병합하지 않았다. 다른 기계의 디스크까지
확인했다는 주장은 하지 않는다.

보존 커밋 `1841f87`의 모든 목적지 bytes까지 확인한 뒤
`sample/output/s11-program-audit-20261011-001/`의 61개 파일과 빈 폴더를 정리했다.
고유 52개는 repo에 이동되고, 같은 JSON 5개와 전달 컨테이너 4개는
보존본을 재사용한다. 원본 미디어·upstream 실험 입력·사용자 첨부 ZIP은 유지한다.
정리한 원래 파일 크기는 12,334,316 bytes이며, 완료 결과와 삭제 전후 수치는
[receipt](2026-10-11-program-audit-intake.json)의
`cleanup`이 기록한다. 원문이 과거 출력 경로를 적었다는 이유로 중복 폴더를
유지하지 않고 manifest로 복구 위치를 제공한다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: preserved scoped/FULL sample4 evidence locates component-to-front reduction choosing internal Y833 after a qualified Y813 alternative survives; water A loses dark upper support earlier. The default/NONE receipt confirms final outputs/events but lacks the corresponding raw-stage join. No new causal or physical acceptance is claimed.
- Logic-map impact: NONE — source files, runtime consumers and detector control flow are unchanged; this intake adds provenance routing and successor-design/acceptance conditions only.
- Failure-registry impact: NONE — existing representation, role, Foam-front, provenance and tuning entries already cover the preserved findings; no new mechanism or accepted repair is established.
