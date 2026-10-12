# CR-1 WP1 참조·입력 준비 점검 — 2026-10-12

**결과: 입력 보존·후보 연결 VERIFIED; 참조 support의 사용 범위는 사용자 판단 필요.**
사용자는 정리 체크포인트 이후 자율 진행과 커밋·푸시를 승인했고, 본인 판단이
필요한 지점에서 멈추도록 요청했다. 이번 점검은 clean `main`의 `f97ff8b`에서
시작했다. 현재 상태와 다음 행동은 [Work Plan](../../00-project/work-plan.md)이 소유한다.

WP1 전체가 동결된 것은 아니다. 모델 설치·다운로드·추론과 Windows 실행은
하지 않았다. 따라서 **CR-1 모델 실패나 CLOSED WITHOUT PROMOTION 결과가 아니다.**
기존 후보·지역 라벨은 계속 유효하며, 모든 영상을 정밀 재라벨링해야 한다는
결론도 아니다.

## 확인한 입력과 재사용

[사전 범위](2026-10-12-cr1-reference-preflight/preflight.json),
[실행 감사](2026-10-12-cr1-reference-preflight/audit.json),
[재현기](2026-10-12-cr1-reference-preflight/audit.py)에 입력 hash와 결과를 보존했다.

- 정리 후 남긴 **252개 파일**, 기존 보호 pin **293개**, 원본 영상 **8개**의
  hash가 일치한다. 보호 pin에는 생산 Python 소스 **221개**가 포함된다.
  영상은 hash만 읽었고 sample3를 포함한 어떠한 영상도 decode·scoring하지 않았다.
- 기존 `candidates.inventory`를 그대로 호출하여 7개 캡처의 **160개 후보와
  문맥 대조군 4개**가 기존 고정 목록과 정확히 같음을 확인했다. Oil 확인 후보
  7개, 잘못된 대상 3개, 미검토 후보 150개를 구분한다. 모델 점수는 전부 NOT_RUN이다.
- P0의 로컬 장면 그룹 16개와 Windows 구간 9개를 그대로 연결했다.
  별도 공개 압축기 위치 join의 후보 23개는 isolated-frame 자료이며, 이후
  application-pipeline 후보 index로 바꿔 쓰지 않았다.
- S1/분포/평균 실험의 입력과 inventory 함수만 재사용했다. 닫힌 연산을
  재실행하거나 과거 결과를 새로운 비교로 세지 않았다. 복원 도구의 과거
  검증은 정리 receipt를 재사용했고 폐기 자료의 복구를 요청하지 않았다.

## 멈춘 이유와 근거의 정밀도

[CR-1 참조 계약](../../20-architecture/s11-contextual-role-observation-design.md#wp1-preflight-decisions)은
실제 native support와 사람 검토의 정밀도를 함께 묶도록 하고,
“A regional Oil/Foam reply alone is not an exact contour annotation”이라고 명시한다.
[검증 계약](../../30-validation/s11-interface-observability-witness-validation.md#local-source-and-truth-qualification)은
후보 정체성, 측정 footprint, 실제 contour와 위치 구간을 구분한다.

| 재사용 가능한 자료 | 실제로 확인된 것 | 자동으로 확장할 수 없는 것 |
|---|---|---|
| sample4 f1275, 후보 idx12/Y835 | Oil 후보 정체성과 X595의 위치 구간 | 저장 후보에 native contour가 없다. scalar를 따라 수평 경계를 만들거나 가까운 edge로 이동시킬 수 없다. |
| 기존 S1 Oil/Structure/Texture 참조 | f1275 Oil 주변, f450 rim seed, f1620 내부 texture guide | 기존 문맥 exemplar를 물리 역할이 검토된 전체 경계 strip으로 바꿀 수 없다. 세 참조가 모두 sample4라는 노출도 남는다. |
| sample4 확인/거부 후보 10개 | 원래 index/source/Y 연결; 3개에는 sector 측정 geometry 존재 | 모두 원래 `native_path_review_status=UNREVIEWED`다. 이것은 후보 역할 판단을 취소하지도, sector 전체를 검토 contour로 만들지도 않는다. |
| sample4 f1620 Foam | X595에서 rows812–816이 실제 upper 교점을 포함 | 한 column의 불확실성 구간을 여러 X의 경계나 구간 안 모든 edge의 라벨로 늘릴 수 없다. |
| 공개 압축기 f1499 | X578의 Foam A/Oil B 포함 구간 | A에는 center edge Y332/336, B에는 Y428/431/433이 남는다. 어떤 edge가 참조인지 고르는 판단은 아직 없다. |
| Water A/B/C, beer/milk 및 앞선 근사점 | 각 owner의 역할·가시성·위치 범위 | 정확한 후보/경로, 인접 프레임 또는 채워진 참조 mask로 승격할 수 없다. |

**해석:** 현재 자료로 후보 중심의 *지역 문맥 선호*를 연구할 여지는 있다.
반면 계획의 contour를 따른 상·하측 strip을 어떻게 이 검토 자료에 연결할지는
아직 명시되지 않았다. 모델 점수를 보기 전에 이 비교 단위를 결정해야 한다.
정밀 contour 라벨이 모든 정성 연구의 필수라는 뜻이 아니라, 두 결과가 답하는
질문이 달라 조용히 대체하지 않는다는 뜻이다. 이번 감사는 새 물리 라벨을
생성하는 자동 readiness 판정기가 아니다.

## 사용자에게 제시할 두 진행 범위

1. **기존 후보 중심의 문맥 비교로 한정한다 — 권고.** 기존 후보 좌표와 검토된
   근사 문맥을 그대로 사용하고, 실제 contour의 역할 판정이나 정확한 경계 검출
   성공을 주장하지 않는다. 선택되면 이 제한을 CR-1 owner에 반영하고 참조·동일
   scale의 full/local support·episode 제외·실제 positive/opposition 진입 조건을
   고정한다. 실행 가능성이나 유용성이 이미 입증됐다는 뜻은 아니다.
2. **원래 경로 비교를 유지하고 작은 참조 support 검토를 추가한다.** 기존 캡처의
   관측 경계 조각과 sampling support를 구체적으로 제시해 필요한 역할만 묶는다.
   기존 역할/가시성 답변을 다시 묻거나 whole-video 라벨링·새 촬영을 요구하지 않는다.
   사용자가 구분하기 어렵다면 해당 역할은 미평가로 남긴다.

아직 어느 선택도 채택하지 않았다. Reference bank, source/episode exclusion,
pixel-to-token support와 실행 예산이 함께 성립한 뒤 backend revision·weights·
최소 의존성을 pin하고 설치한다. 기존 **추가 3 GB 상한**, CPU 기준 계측,
실패 시 정리, O2/V5 → 별도 O3/O4 → field 순서는 계속 적용된다.

## 검증과 산출물 종료

기존 환경에서 다음 CLI가 성공했다. Audit은 저장 JSON/hash와 기존 inventory만
읽으며 모델 또는 detector를 import·실행하는 경로를 추가하지 않는다. 기존
inventory import의 일반 진단/전처리 모듈은 로드되지만 해당 연산은 호출하지 않는다.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python \
  docs/50-diagnostics/s11/2026-10-12-cr1-reference-preflight/audit.py \
  --output <새로 시작한 관리 실행의 work>/audit.json
```

관리 실행 `sample/output/s11-cr1-workspace/runs/reference-preflight-20261012-001`은
완료했다. 15,633-byte 감사 JSON을 위 tracked 경로에 한 벌만 보존하고 임시 사본은
제거했다. 환경·모델·cache는 만들지 않았으며, 기존 원본과 생산 의존성은 그대로다.
`experiment_artifacts.py check`는 1개 관리 실행, 오류 0이다. 사용자 판단 전까지
실제 scoring 진입은 보류한다. 시간·RSS·모델 성능은 측정하지 않았다.

추가 검증에서 감사·재현기·preflight hash와 원래 캡처에서 다시 센 160개 후보
ID를 대조했고, 변경 Markdown의 local 링크/anchor **281개**가 통과했다.
`check_detector_governance.py --base-ref f97ff8b --include-worktree`와 whitespace
검사도 통과했다. 새 tracked 기록과 관리 표식의 합계 파일 할당량은 **53,248 bytes**이며
모델 환경·가중치·cache 경로는 없다. 문서와 저장자료 감사 범위여서 detector
회귀시험이나 모델 성능시험을 새로 수행한 것으로 보고하지 않는다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: pre-inference reference/support binding is unresolved; this saved-record audit does not execute or newly locate a production failure. Existing candidate identity and interval judgments do not certify a new contour support.
- Logic-map impact: NONE — existing inventory and saved records are reused without detector, geometry-generator, authority, sequence or publication changes.
- Failure-registry impact: NONE — this is a reference-scope readiness checkpoint, not an empirical mechanism failure, model rejection or field improvement.
