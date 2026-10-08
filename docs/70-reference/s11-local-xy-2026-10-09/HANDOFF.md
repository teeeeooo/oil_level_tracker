# S11 Local XY — 다음 구현 인수인계

기준 HEAD는 `167126e5f095e4011bc8f7dfd51049df87dd84f6`이다. 먼저 `S11_Local_XY_Detector_Work_Spec_2026-10-09.md`의 결정 요약, 실행 결과, WP1–WP5를 읽는다.

## 완료한 것

원본 네 영상의 299개 sampled row baseline fingerprint를 재현했다. sample4의 네 추가 구성 452개 row까지 포함해 751개 result row를 detector와 completed resolver에 통과시켰다. 국소 X·Y 제외는 더 이상 이번 조사 기준으로 ‘전혀 시험하지 않은 가설’이 아니다.

공유 mask 제외와 전역 paired phase 평균은 채택하지 않는다. Oil 후보 측정에만 제외를 적용한 구성은 다음 개발의 출발점이지만, 정확도 개선이나 production 승격이 확인된 구성은 아니다.

## 다음 작업

기존 세 후보 표현의 측정에 opt-in XY scope를 전달하는 WP1부터 시작한다. 빈 범위와 비교차 footprint는 기존 결과와 정확히 동일해야 한다. 이후 제외로 실제 영향을 받은 측정에만 필요한 표본 비교 안전 처리를 적용한다. 기존 A1 lineage를 확장해 남은 표본과 분모를 기록하고, 고정한 full-window 비교로 주요 움직임이 좋아지는지 판정한다.

Foam 공용 mask, template의 후보 전체 rejection, authority·tracklet·phase·selector의 판정 규칙은 이 변경에 섞지 않는다. 40초에서 B가 Oil Y830 / Foam Y840의 inverted topology를 만들고 양쪽 validity를 잃은 사실을 보존한다. Foam raw 좌표 개수 26개가 같다고 최종 Foam 관측 보존으로 평가하지 않는다.

전역 paired 평균을 재튜닝하거나 shared mask의 크기를 확대·축소하는 탐색을 반복하지 않는다. 보호 지점의 근처에 새 Y가 있다는 이유로 물리적 정답 label을 복사하지 않는다. 작은 누락과 주요 움직임 손실을 구분하고, report가 보여 주는 상승·하강·극값·소실·재출현을 우선한다.

## 원본 실행 증거

```text
/Users/sunjaekim/Developer/oil_level_tracker/sample/output/
  s11-local-xy-exclusion-20261009-001/
```

`preflight.json`, `results.json`, `compact-summary.json`, `detailed-summary.json`과 각 variant의 `raw.json`, `completed.json`, `tracking.json`, `report.json`을 사용한다. 실행 helper, 실제 baseline/shared-mask report bundle, 원본 ROI와 비교 그래프도 같은 디렉터리에 있다.

이 전달 ZIP은 명세서와 파생 요약의 묶음이다. 영상·trace·HTML 원본 전체의 백업이 아니다. 원본 실행 디렉터리는 ignored local output이므로 장기 보관은 별도로 결정해야 한다.

## 종료 시점의 상태

production source 220개와 동결 입력 16개 hash는 그대로다. focused pytest는 72개 PASS, 별도 계약 assertion은 12개 PASS였다. tracked worktree는 clean이고 commit/push는 하지 않았다. governance checker PASS는 tracked 변경이 없다는 범위이며 prototype 승격 승인으로 해석하지 않는다.

Windows는 기존 사용자 전달 기록을 검토했을 뿐 새 실행을 하지 않았다. 닫힌 D1/D2 확인 질문을 다시 요청하지 않는다. O2/O3와 아홉 구간 Windows qualification, 기존 FIELD FAIL 상태는 유지한다.
