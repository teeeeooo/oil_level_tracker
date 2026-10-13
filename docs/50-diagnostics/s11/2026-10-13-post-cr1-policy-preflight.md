# Post-CR1 WP02–03 실행 가능한 사전검사 — 2026-10-13

**판정: 저장 관측 계약 VERIFIED / calibration NOT_READY.** 기준은
`94f9cb48a34f04e2dd0b23cf35666bb26d6eda01`의 clean main이다. 기존 점수를
읽는 [사전검사](../../../tests/diagnostics/s11_contextual_role_preflight.py)를 구현하고
전체 CR1 자료에서 실행했다. 모델·detector 재실행, 임계값 선택, 생산 shadow 연결,
새 물리 라벨은 없다. 현재 gate와 다음 전이는 [Work Plan](../../00-project/work-plan.md)이 소유한다.

## 산출물과 재사용

- [Manifest](2026-10-13-post-cr1-policy-preflight/manifest.json): 입력·원본·geometry/bank hash,
  한 정책 family, 미지정 tau, 자료 노출/분할, calibration 선택 절차, 보존할 25개
  P0/Windows group ID와 별도 공개 압축기 범위, 자원 상한과 남은 진입 조건.
- [전체 readout](2026-10-13-post-cr1-policy-preflight/readout.json.gz): 164개 원래 query와
  실제 candidate 시간·Glass, O1/A1 hash/pointer, availability, minimum local/full
  interface similarity와 signed margin. 원시 벡터·token support는 기존 완전 score
  table의 hash/pointer로 연결한다. 새 복사본이나 분류기 결과가 아니다.
- [역할 검토 화면](2026-10-13-post-cr1-policy-preflight/review.html): 원본 PNG를 참조하며
  기존 O2 `review_geometry`와 joint-context viewer를 재사용한다. 모델 점수는 숨겼다.
  renderer/source/image hash는 HTML 안에 기록했다. 경계·정답 이미지가 아니라
  저장된 표본 위치를 켜고 끄는 검토 화면이다.

기존 O2 도구의 hash·숫자·identity 검증과 새 파일 쓰기를 재사용했다. CR1의 full/local
벡터·floor/ceil envelope는 O1 sector-score와 달라 별도 **offline input adapter**가
필요하다. 기존 frozen CR1 스크립트나 runtime Witness schema를 변경하지 않았다.

## 확인한 사실

| 항목 | 결과와 해석 |
|---|---|
| 원래 모집단 | 160 candidates + 4 context controls = 164; 150 UNREVIEWED, 7 confirmed, 3 rejected, 3 texture guides, 1 agent-observed context |
| 실제 candidate 연결 | 160개 모두 원래 frame/index/source/Y 및 7개 capture의 실제 timestamp에 일치; 임의 최근 frame·좌표 대체 없음 |
| 지원 영역 | distinct supports 137, 같은 지원 영역 duplicate group 24; 중복 후보가 독립 증거로 늘어나지 않음 |
| 측정 가능성 | full/local 각각 132 MEASURED, 32 UNAVAILABLE; 실제 데이터에 tie/disagreement는 없고 해당 경로는 synthetic contract tests로 확인 |
| 기존 O1 | native generator path 표본 31, captured native path 없는 122, bound O1 record 없는 7. 측정 존재는 역할 정답이 아님 |
| 기존 A1 | 80 measured, 73 different-family unavailable, 7 bound record 없음. `unavailable`를 score=0이나 물리적 음성으로 바꾸지 않음 |
| 시간 정밀도 | 160 candidate 시간은 source capture에 묶임. 4개 context control은 이 adapter에서 timestamp를 새로 추정하지 않고 `CONTEXT_CONTROL_TIME_UNBOUND`로 남김 |
| 독립성 | scored recording 1, untouched holdout 0; calibration/holdout source assignment는 빈 목록 |
| 실제 실행 | repository 밖 `/private/tmp`에서 standalone CLI 성공; 모든 decision NOT_EVALUATED, encoder forwards 0 |
| Contract tests | 29 passed in 0.26 s; raw-score 보존, 결측/동률/불일치/수치 오류, hash-valid 자료의 candidate/native/time 오결합 거부, cutoff/holdout 거부, 비-repo cwd와 overwrite refusal |

첫 CLI 시도는 내적의 부동소수점 반올림을 엄격한 `[−1,1]`로 검사해 출력 전에
중단했다. 원 검증기의 `1e-12` score-bound allowance와 맞추고 `1.0000000000000002`
보존 회귀 검사를 추가했다. 원래 점수를 자르거나 바꾸지 않았다. 이는 도구의
입력 검증 수정이며 classifier threshold나 CR1 연구 결과 수정이 아니다.

## 한정한 사용자 판단

49.5 s/f1485의 B는 `material_path` idx8, 대표 Y841이다. 실제 저장된 O1 native
sector 표본 범위는 Y837–843이고, 중심 X595를 포함한 **X586–605 sector 표본은
Y838**이다. A는 이미 확인된 `phase_transition_scan` idx19/Y836이며 captured native
path는 없다. 대표값, 구간 표본, 정확한 X595 교점은 같은 좌표 의미가 아니다.

B의 local interface similarity는 0.829081이지만 texture가 0.850288로 더 높다.
A의 local interface similarity는 0.726906이고 interface signed margin은 +0.015512다.
따라서 절대 score 최댓값과 제안된 local 역할 경쟁은 서로 다른 후보를 설명한다.
이는 B가 오답이라는 판정도, 같은 실제 계면이라는 판정도 아니다.

새 질문은 **B가 기존 확인된 A와 같은 실제 유면을 표현하는지, 다른 무늬·경계인지,
이 화면으로는 구분할 수 없는지**다. A나 이전 다른 source 판단은 다시 묻지 않는다.
답변은 이 후보의 검토 범위에만 연결하며 모든 sector·인접 frame·정확한 scalar
truth로 확대하지 않는다. 판별 불가도 그대로 보존한다.

브라우저 도구는 `file://` navigation을 차단해 자동 렌더링 확인을 수행하지 못했다.
JavaScript 구문과 두 case의 원본 링크·15개 recorded point 연결은 확인했다.
HTML을 사용자에게 제공했지만 실제 화면 열림/사용자 판정 완료를 주장하지 않는다.

## 다음 단계의 조건

WP02의 저장 관측 계약과 WP03의 노출/주장 목록·선택 절차는 구체화했다. 실제
`tau_support`는 여전히 null이다. 적합한 calibration 자료에서만 breakpoint별
positive loss·wrong-target family·unresolved 분모를 보고 한 operating point를
검토하며, 그 전에 보호할 영향 범위와 독립 평가 입력을 고정한다.

현재 source의 재분할은 untouched holdout을 만들지 않는다. B에 대한 새 답변도
이 문제를 해결하지 않는다. geometry/bank 이전, native-role precision, 허용 잔여
영향 및 target-Windows 자원은 별도 미해결 조건이다. 임계값을 알려진 점수 간격에
맞추거나 데이터 부재를 코드로 숨기지 않는다. WP04 runtime shadow는 아직 미진입이며
O2/V5 이전 behavior 소비도 없다. Foam의 raw upper-role 경로는 독립적으로 유지한다.

## 재현과 보존

원본 입력이 있는 checkout에서 새 managed run을 시작하고 다음을 실행한다.
`--root`, manifest와 output을 절대 경로로 주면 다른 cwd에서도 같은 검사를 한다.
readout은 gzip 내부의 논리 JSON으로 비교하며 컨테이너 metadata로 의미를 판단하지 않는다.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B \
  tests/diagnostics/s11_contextual_role_preflight.py \
  --manifest docs/50-diagnostics/s11/2026-10-13-post-cr1-policy-preflight/manifest.json \
  --output <managed-work>/readout.json
```

`policy-preflight-20261013-001`은 출력 없는 tooling-validation 중단으로 닫았다.
`policy-preflight-20261013-002`는 원 점수 재사용 후 읽기 계약·검토 화면만 보존한다.
353,085-byte readout은 동일 논리 내용의 35,100-byte gzip 한 벌로, 검토 화면은
10,448 bytes로 남긴다. PNG·모델·영상·중간 feature 복제본은 없다.
보존 목적은 전체 후보/결측 분모와 original/native 연결, 실제 판단 질문의 조건을
유지하는 것이다. 삭제하면 정책의 부정확한 label/좌표 연결을 재검토하기 어렵다.
원본과 source로 재생성 가능하지만 이 작은 입력/전체 표가 반복 작업보다 작다.
후속 accepted observation 계약이 같은 정보를 대체하면 이 파생 표를 재심사한다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: candidate representative/native-sector/exact-X meanings must be distinguished before a regional descriptor can acquire physical authority; this offline audit identifies no new production failure or accepted classifier.
- Logic-map impact: NONE — new saved-record adapter and preflight only; production extraction, Witness schema, authority, sequence and publication remain unchanged.
- Failure-registry impact: NONE — existing coordinate/provenance and threshold/holdout risks cover the finding; no new mechanism failure or field improvement is asserted.
