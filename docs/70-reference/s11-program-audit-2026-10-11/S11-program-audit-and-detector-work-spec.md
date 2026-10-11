# S11 전반 감사 및 Detector 개선 작업 명세서

- 작성일: 2026-10-11
- 대상: `teeeeooo/oil_level_tracker`
- 확인한 기준 커밋: `4d84f70c5026d92330628bbae7650ac6288a8e12` (`main`)
- 문서 성격: **현재 코드·증거를 확인한 감사 결과와 후속 구현 제안**. 승인된 운영 설계나 현장 합격 선언이 아니다.
- 현재 판정: **S11 ACTIVE / O2 OPEN / FIELD FAIL 유지**.
- 우선순위: detector 개선. 이미 구현된 report·검토 UX를 다시 만드는 작업은 제외한다.
- 실제 실행 결과: [감사 기록](evidence/audit-record.json), [현재 기본 실행 요약](evidence/sample4-current-default-checkpoints.json). 근거 문서의 경로·SHA-256·행 수는 [source ledger](evidence/source-ledger.json).

## 0. 결론과 이번 명세의 결정 사항

**전체 detector를 다시 만드는 것보다, 원시 경계를 물리적 관측으로 만드는 부분을 교체·보강하고 기존 소유권/출력 구조에 제한적으로 연결하는 것이 타당하다.** 현재 병목은 단순 edge 부족만도, 마지막 selector의 점수만도 아니다. 실제 대상이 후보로 남는가, 그 후보가 유리 구조나 Foam 내부 특징과 구분되는가, 같은 물리적 대상의 관측이 시간축에서 보존되는가를 분리해서 고쳐야 한다.[E01][E03][E06][E07]

이번 검토에서 정리한 결정은 다음과 같다.

1. **P1은 다시 구현하지 않는다.** 중심 조건부 경로 대안 보존은 main에 통합된 오프라인 표현 도구다. 물리 판별·운영 detector 개선 완료로 세지는 않는다.
2. **P2-S1은 종료한다.** 10월 11일의 공동 support/reference 비교는 정확히 계산되었지만 판별력이 없었다. 동일 readout의 threshold, patch 크기, reference 위치를 조정하는 후속 작업을 잡지 않는다.
3. **Foam은 episode보다 raw-front를 먼저 수정한다.** sample4 54초의 저장된 scoped/FULL 증거에서는 실제 상단 부근의 경계가 영상과 기존 표현에 남아 있는데, component를 한 좌표로 축약하면서 내부 무늬를 선택한다. Water A에서는 그보다 앞선 밝기 기반 support 추출에서 상단 정보가 빠진다. 두 원인을 한 가지 상단/하단 치환으로 해결할 수 없다.
4. **Oil은 현재 후보의 물리적 역할과 시간 소유권을 함께 검증하되, 구현 변경은 분리한다.** 관측 후보가 없어서 생긴 누락과, 존재하는 후보가 authority/association/phase에서 막힌 누락은 다른 문제다. cost-first 전환이나 phase gate 완화부터 시행하지 않는다.
5. **최종 수용 단위는 움직임의 맥락이다.** 주요 상승·하강·반전·Foam 형성/소멸·FULL/EMPTY를 왜곡하지 않는가를 본다. 개별 frame의 모든 누락·오차를 없애는 것을 S11 종료 조건으로 삼지 않는다. 다만 잘못된 구조를 장시간 따라가서 물리적 이야기를 바꾸는 결과는 실패다.
6. **전체 완료 경로를 유지한다.** 경계/역할 → 같은 frame의 좌표 → association → phase → 독립 Foam episode → 통합 report/Windows 확인까지 계획한다. 첫 실험이 끝날 때마다 다음 작은 실험만 만드는 방식으로 진행하지 않는다.

이 문서에서 제안하는 다음 역할 판별 방식은 **검증할 가설**이다. 이미 성공한 알고리즘처럼 표현하지 않는다. 이번 감사에서 새 운영 판별기를 구현하거나 현장 검출 성능을 개선했다고 주장하지 않는다.

---

## 1. 감사 범위와 증거의 신뢰 수준

### 1.1 직접 확인·실행한 것

| 구분 | 수행 내용 | 이번 결과의 의미 |
|---|---|---|
| 현재 상태 | HEAD, origin/main, worktree, 최근 변경, `work-plan`, roadmap, SSOT, 실행 정책 확인 | 과거 인수인계가 아니라 현재 main 기준으로 판단 |
| 코드/설계 대조 | 현재 logic map, 관련 실패 이력, Foam component→front 구현 및 기존 오프라인 실험 확인 | 실제 변경해야 할 단계와 변경하면 안 되는 소유권 구분 |
| 원본 영상 표본 | base_sample_1, sample2, sample4, water/sample5, beer/sample6, milk/sample7의 **37개 frame을 원본 영상에서 직접 decode** | 정지 이미지 표본 및 시간순 비교. 여섯 영상 전체를 연속 재생·판독했다는 뜻은 아님 |
| 기존 raster 대조 | 공개 water/beer/milk의 기존 full-frame PNG 9개와 새 decode 결과 비교 | **9/9 픽셀 동일** |
| 관련 테스트 | 13개 파일의 경로 보존, Foam, Oil owner, corpus 접근, reference, governance 검사 | **263 passed / 0 failed / 0 error / 0 skipped**, pytest 42.10초. 전체 저장소 suite가 아님 |
| P2 재검산 | 기존 독립 검증기로 원래의 공통 support와 pixel 비용 재구성 | **1,650개 비용 / 199,800개 BGR 값 비교**, 입력 60개 및 production 파일 221개 pin 확인 |
| P5 재검산 | 기존 재현기로 sample4와 water ABC의 저장된 배열/경계/좌표 interval 재결합 | **66개 peak / 19개 gap pair / 25개 graph** 확인, production 파일 221개 불변 |
| 현재 기본 실행 | sample4의 기존 qualification 구간을 현 main·기본 detector로 실행 | 최종 수치는 §1.3 및 실행 기록 참조 |
| 비변경 확인 | governance 및 diff 검사, tracked 상태 확인 | 운영 코드·Recipe·truth를 변경하지 않은 감사 |

환경: Mac 저장소의 기존 `.venv`, Python 3.14.4, OpenCV 4.14.0, NumPy 2.5.1, pytest 9.1.1, PySide6 6.11.1. 버전은 이번 환경에서 실제 import로 확인했으며 제품의 권장 최소 버전이라는 뜻이 아니다.

### 1.2 직접 실행하지 않았거나 주장하지 않는 것

- 보안 Windows 원본 영상, 비공개 이미지 또는 비공개 packet을 이 Mac으로 가져오지 않았다. Windows 결과는 저장소에 보존된 사용자 검토·전달 기록으로 판단했다.
- 새 Windows qualification, 독립 holdout 평가, 사용자 report 이해도 실험, Qt stress, Windows packaging 전체 검증은 하지 않았다.
- sample3은 routine 연구에서 퇴역한 상태를 존중해 이번 영상 표본·현재 실행 대상에서 제외했다. 기존 명시적 legacy regression의 권한은 취소하지 않는다.
- 기존 P1 통합의 `400 passed`, P2 최초 사전 검사의 `80 passed` 등은 **과거 기록**이다. 이번 `263 passed`에 더하지 않는다.
- P2 재검증 JSON의 `execution_head=0914820…`는 원래 비교 실행의 provenance다. 이번 감사 HEAD는 `4d84f70…`다. 원래 실험과 이번 재검산을 구분한다.

### 1.3 현재 기본 sample4 실행

현 main의 기본 detector와 기존 sample4 Recipe/qualification 구간을 사용했다. Local XY는 OFF, debug는 NONE이며, 분석 source time은 0–56초, 간격은 0.5초다. 기존 application pipeline과 bundle 작성까지 실행했다. [체크포인트 요약](evidence/sample4-current-default-checkpoints.json)은 live 실행 출력을 정리한 파생 기록이며, 전체 native receipt는 Mac의 감사 폴더에 보존했다.

| 측정 | 이번 실행 |
|---|---:|
| raw / completed detection / CSV 행 | 113 / 113 / 113 |
| 유효 Oil 수치 행 | **101/113 (89.38%)** |
| 유효 Foam 수치 행 | 26/113 |
| 실행 시간 | 109.05초 |
| 프로세스 peak RSS | 284,016,640 bytes, 약 270.86 MiB |
| output fingerprint | `e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1` |

**89.38%는 출력 유효성 비율이지 물리적으로 올바른 검출률이 아니다.** 시간은 감사용 hash 수집과 bundle 작성을 포함하는 단일 Mac 실행값이다. detector 연산만의 처리량, Windows 속도, 개선 전후 성능 비교로 해석하지 않는다.

| 시각 / frame | 현재 최종 Oil Y | 현재 최종 Foam Y | 해석상 중요한 점 |
|---|---:|---:|---|
| 38.0 s / 1140 | 844 | 없음 | 기존 보호점과 같은 Oil 좌표 |
| 40.0 s / 1200 | 865.5 | 840 | 기존 검토 target Y841과 다른 값 |
| 42.0 s / 1260 | 868 | 819 | 기존 검토 target Y839과 다른 값 |
| 42.5 s / 1275 | 835 | 818 | 기존 보호점과 같은 Oil 좌표 |
| 43.0 s / 1290 | 없음 | 812 | Oil 누락; Foam 유효성은 독립적으로 유지 |
| 43.5 s / 1305 | 없음 | 812 | Oil 누락 지속 |
| **44.0 s / 1320** | **822** | 812 | **기존 검토 Oil target Y844와 다르며, 출력의 최고 Oil event가 됨** |
| 49.5 s / 1485 | 836 | 814 | 기존 보호점과 같은 Oil 좌표 |
| 52.0 s / 1560 | 833 | 813 | 기존 보호점과 같은 Oil 좌표 |
| 54.0 s / 1620 | 없음 | 없음 | 사용자 확인 Foam upper가 있는 시점의 최종 누락 재현 |

기존 검토 target과의 대조는 [E17]의 이미 판독된 checkpoint 맥락을 사용한 것이다. 이번 NONE 실행에서 새 후보 membership을 전수 결합하거나 과거 scalar truth를 새로운 fixed-X truth로 변경한 것은 아니다. 좌표가 같은 보호점도 그것만으로 새로운 물리적 동일성을 승인하지 않는다.

**실사용 목적에 직접 연결되는 결과:** `MAXIMUM_OIL_LEVEL`이 44초, `oil_level_px=28`로 발생한다. 이는 source Y822에 해당한다. 그 시점의 기존 검토 대상은 Y844이므로, 현재 잘못된 대상 선택이 단지 국소 잡음으로 남지 않고 report가 설명할 주요 극값에 들어간다. `MINIMUM_OIL_LEVEL`도 42초의 source Y868에서 산출된다. 이 때문에 “유효 행을 늘리는 것”보다 **잘못된 대상이 주요 사건·극값을 바꾸는 문제를 줄이는 것**을 우선해야 한다.

기존 검토의 두 checkpoint만 비교해도 42.5→44초 target은 Y835→844로 이동한다. 영상 좌표계에서는 아래 방향이다. 반면 현재 최종 Oil 값은 Y835→822여서 위 방향을 암시한다. 중간 두 행이 비어 있다는 사실까지 고려하면, 이 문제는 단순한 22 pixel 오차가 아니라 **중요한 움직임의 방향·반전 해석을 바꿀 수 있는 오대상 선택**이다. 이는 checkpoint 수준의 대조이며 모든 중간 frame의 실제 궤적이나 새 report의 시각적 판독 결과를 확정한 것은 아니다.[E17]

실행은 `JUDGMENT_PASS`도 산출했다. 이는 저장된 측정값에 적용된 RECOVERY 업무 규칙의 결과이지 detector의 물리 검출 성능이나 현장 qualification PASS가 아니다. 이 이벤트 하나로 전체 물리 판정의 참·거짓을 단정하지 않는다.

Oil의 단순 유효 수치 간 최대 간격은 2.5초였지만, 해당 수치가 전부 같은 실제 계면이라는 연속 판독은 없다. 따라서 이를 §3.3의 물리적으로 검증된 1초 cadence 성적표로 바꾸지 않는다. Foam의 단순 수치 간격 1초 역시 별도 Foam 수용 기준이 아니다.

**실행/원인 증거의 경계:** 이번 default/NONE 실행은 54초의 최종 누락을 재현했다. §5.2의 raw Y833→episode 원인은 기존 `v2-sample4-scoped-FULL` 저장 증거를 재검산한 결과다. 새 NONE 실행에서 raw trace를 다시 캡처한 것은 아니므로, 그 세부 원인을 current default의 같은 단계로 자동 전이하지 않는다. 운영 개입 전에는 같은 설정의 실제 candidate/owner 연결을 확인해야 한다.

기존 harness는 임시 디렉터리에 실제 output bundle을 작성한 뒤 필요한 CSV·event·hash 기록을 남기고 bundle을 삭제한다. 따라서 이번에 새 report 파일을 보존하거나 독립 검토자가 report를 판독한 것으로 주장하지 않는다.

### 1.4 증거의 우선순위

`사용자의 원본 물리 판독` → `정확히 결합된 원본/후보/실행 증거` → `일반화 가능한 개발 비교` 순으로 해석한다. detector가 선택했다는 사실은 물리적 정답이 아니며, graph가 매끄럽다는 사실도 같은 대상을 추적했다는 증명이 아니다.

Windows의 9개 구간 판독은 주요 물리 사건의 기준이다. 공개 water/beer/milk와 Mac sample은 메커니즘·강건성 개발에 유용하지만 Windows 현장 효과를 대체하지 않는다. 이미 수차례 본 인접 frame을 이름만 바꾸어 새 holdout으로 취급하지 않는다.[E04][E14][E15]

---

## 2. 프로젝트 전체 진행 상태

### 2.1 무엇이 이미 끝났고 무엇이 남았는가

| 영역 | 현재 상태 | 이번 검토의 판단 |
|---|---|---|
| 기본 분석 제품·Recipe·검토·export | 초기 제품 흐름 및 S1–S10 완료 기록 | 제품 골격을 다시 만들 이유 없음 |
| report 원본 맥락·episode 검토 | main 채택 | 유지. detector 부진을 새로운 화면 작업으로 대체하지 않음 |
| 현행 S11 runtime | R22 behavior + R22-3/O1 진단 기반 | 비교 기준으로 고정. LOCAL PASS와 FIELD PASS는 별개 |
| P1 중심 조건부 경로 보존 | main 통합, 명시적 offline 호출 | 표현 기반 완료. 상시 운영 배선은 미채택 |
| P2-S1 역할 reference 비교 | **채택 없이 종료** | threshold·reference 재조정 계획 삭제 |
| P5 원본 상단 위치/표현 조사 | sample4 위치 확인 및 saved-stage 원인 규명 완료 | 반복 질문·edge generator 추가가 아니라 역할/좌표 축약을 다룰 차례 |
| O2 판별 수용 | OPEN | 현장 shadow, operating point와 holdout을 포함한 수용 미완료 |
| O3/P3 support·association | 진입 전 | O2를 통과하지 않은 appearance 점수를 운영 owner에 넣지 않음 |
| O4/P4 phase/handoff | 후속 | raw 후보·association이 맞는데 phase가 막는 손실에 한해 변경 |
| P5 Foam 구현 | 독립 진행 가능 | Oil 완료를 기다릴 필요는 없지만 자기 검증을 건너뛰지는 않음 |
| O5/P6 Windows qualification | 미완료 | 정확한 통합 후보에 대해 9구간·처리량·provenance 확인 |
| P7 S11 종료 | 미완료 | 목적 달성·잔여 한계·미평가 범위를 구분한 종료 판단 필요 |
| S11-M, S12 | 후속 예정 | 대규모 정리·UI 확장으로 현재 detector 핵심 경로를 우회하지 않음 |

여기에 임의의 “완료율 85%”를 부여하지 않는다. UI, 표현 도구, 물리 판별, 현장 검증의 진척은 서로 대체할 수 없기 때문이다.[E01][E02][E05][E10]

### 2.2 10월 10일 이전 명세와의 관계

원래 P0–P7 프로그램의 방향은 유지하지만 아래 세 가지를 갱신한다.

- P1을 앞으로 해야 할 일로 다시 배치하지 않는다. `e9bef67…`, `5631f1a…` 통합·baseline pin 보완 이후의 상태가 현재 기준이다.
- P2를 “구현할 공동 reference 비교”라고만 적지 않는다. `0914820…`의 고정 실험이 실행되었고 `34ed3d8…` 이후 종료됐다. P2-S1은 성공하지 않았다.
- P5의 “상단이 실제 보이는가/어디인가” 질문은 최신 `4d84f70…`에서 좁은 범위로 해결됐다. 이 답변을 다시 요청하거나 이웃 frame까지 truth를 확대하지 않는다.

이 문서의 작업 묶음은 기존 P/O/W 단계에 대응시키는 실행 제안이며 새로운 병렬 milestone 체계가 아니다. 현재 승인·다음 행동은 계속 `docs/00-project/work-plan.md`가 소유한다.[E01][E05][E06][E07]

### 2.3 진행 방식 자체에 대한 감사

그동안의 작업은 무의미하지 않다. 잘못된 좌표 합성, stale owner 복사, Oil/Foam 상호 누출, 물리 정답과 detector 결과의 혼동을 상당히 분리했다. 또한 “계산 버그인지, 표현이 없는지, 역할 판별이 안 되는지”를 좁힐 수 있게 됐다.

그러나 **진단 도구의 정밀도와 실제 detector 효과 사이의 간격이 커진 상태**다. 이번에도 비용 계산은 맞는데 P2가 실제 양성을 남기지 못한다. 앞으로는 새 descriptor·새 viewer·새 label 형식보다, 하나의 고정 후보를 끝까지 실행해 관측 흐름이 좋아지는지 확인하는 데 개발 예산을 집중해야 한다.

닫힌 실험마다 더 작은 진단 문제를 계속 여는 방식은 중단한다. 새 진단은 다음 중 하나를 바꿀 수 있을 때만 추가한다: 사용할 관측, 개입할 owner, 수용/폐기 결정. 세 가지 모두 바뀌지 않는 추가 통계는 현재 S11의 우선 작업이 아니다.

---

## 3. 목적을 실행 가능한 수용 기준으로 고정

### 3.1 목적과 보존해야 할 무결성은 다르다

제품 목표는 **report에서 사용자가 계면과 Foam의 움직임을 이해하는 것**이다. 원본을 처음부터 다시 보는 작업을 줄이는 시험자 보조 도구이지, 모든 frame의 모든 물리 경계를 무오류로 인증하는 시스템이 아니다.[E03]

다만 아래 무결성은 정확도 목표와 별개로 유지한다.

- 수치값은 같은 source frame의 실제 선택 후보에 연결되어야 한다.
- 누락 값을 interpolation/carry/보고서 smoothing으로 만들어 정확도가 좋아진 것처럼 보이지 않아야 한다.
- Oil과 Foam은 독립적인 유효성을 가지며, 한쪽의 누락/거절이 다른 쪽 좌표를 만들어서는 안 된다.
- FULL/EMPTY의 물질 상태와 “좌표가 없다”는 사실을 혼동하지 않아야 한다.

**물리 판별은 오류 가능한 경험적 판정으로 검증한다.** provenance를 100% 일관되게 유지하는 것과 물리 판별에 100% 정답을 요구하는 것은 같은 조건이 아니다. 알려진 위험한 우회는 막되, 모든 후보에 완벽한 인과 증명이 없다는 이유로 끝없는 준비 단계에 머물 필요는 없다. 반대로 all-UNKNOWN 결과를 안전하다는 이유만으로 개선으로 세지도 않는다.

### 3.2 영향도 A/B/C/U — 최종 검토의 언어

| 등급 | report에서 생기는 문제 | 처리 |
|---|---|---|
| A — 물리적 이야기 왜곡 | 실제 하강을 상승으로 보이게 함, 실제 급격한 회복을 삭제, Foam이 사라진 뒤 residue를 지속 Foam으로 표시, FULL 구간의 구조선을 Oil로 장시간 추적 | 수용을 막는 핵심 실패 |
| B — 중요한 맥락 손실 | 주요 반전 전후가 긴 공백으로 사라짐, 관측이 늦어 사건 순서를 판단하기 어려움, 한 층이 지속적으로 누락 | 보호 대상 구간별 개선 필요 |
| C — 국소 잔여 오차 | 고립된 miss/짧은 흔들림/일부 잘못된 점이 있지만 방향·전환·층 구분·주요 극값의 해석을 바꾸지 않음 | 정량 기록 후 허용 가능. 별도 재조사로 전체 종료를 지연하지 않음 |
| U — 평가 불가 | 상단이 crop 밖, 물리 경계 자체가 불명확, 원본/연결 증거가 없어 수치 정확도를 판정할 수 없음 | PASS/정확한 거절로 세지 않음. 주장 범위에 명시 |

A/B/C/U는 기존 formal gate를 몰래 완화하는 새 판정기가 아니다. episode의 중요성과 실패 영향도를 해석하는 공통 분류다. 결과를 보고 불편한 실패만 C나 U로 바꾸지 않는다. C의 허용 범위와 A/B의 보호 구간은 비교 전에 고정한다.[E05]

고립된 오검지라도 자동 event·극값·회복시간을 바꾼다면 C가 아니라 A/B일 수 있다. 따라서 점 개수뿐 아니라 **잘못된 점이 최종 해석에 미친 영향**을 같이 검사한다.

### 3.3 시간 기준: 기존 1초 목표를 그대로 적용

사용자가 확인한 가시적·움직이는 Oil 구간에서는 같은 물리적 계면의 usable observation 사이를 **실제 source timestamp 기준 1.0초 이내**로 유지하는 것이 개발 목표다. 정확히 1.0초는 포함한다.[E03][E11]

평가 기록은 다음을 분리한다.

- 올바르고 사용 가능한 두 관측 사이 간격의 최대값과 분포.
- 시작부터 첫 관측, 마지막 관측부터 끝까지의 leading/trailing 미관측 구간.
- wrong-target, 단순 numeric이지만 물리적으로 미확인, missing, 판독 불가.
- 관측이 0개 또는 1개뿐인 구간. 빈 분모를 이유로 PASS 처리하지 않는다.

이를 Foam·정지·가림 구간의 보편적인 기준으로 확대하지 않는다. report의 2초 표시 연결과도 구별한다. 0.5초 간격으로 잘못된 rim을 촘촘히 검출한 결과는 1초 목표를 충족한 것이 아니다.

### 3.4 최종 높이의 의미

후속 오프라인 설계의 목표는 기존 Glass의 고정 중심 열에서, 독립적으로 같은 물리적 표면에 속한다고 판단된 투영 가지 중 영상상 위쪽 윤곽을 읽는 것이다. **모든 후보 중 최소 Y**를 선택하는 규칙이 아니다.[E03][E12]

이 기준은 현재 운영값이나 과거 truth를 자동으로 다시 정의하지 않는다. 운영에 반영할 때는 scalar basis/version을 명시하고 비교 값을 분리한다. 다층 유체의 최상단 실제 액체 경계와 Foam의 상단은 각각의 대상이다. 화학적 유체 종류를 분류하는 일은 필수가 아니다.

---

## 4. 영상·검토 자료별 역할

| 자료 | 이번 직접 확인 | 개발에서 보호할 맥락 | 확대해서 주장하면 안 되는 것 |
|---|---|---|---|
| Windows SPL#1 | 기존 사용자 물리 판독 및 전달 증거를 읽음. 원본은 현장에 남음 | FULL→drain→급 refill, EMPTY→유입→층상 Foam→소멸→drain의 9구간 | Mac 결과로 현장 PASS, 정확한 Y/전 구간 새 정답 |
| base_sample_1 | f150,151,240 원본 decode | 약한 유면 영상 위에 강한 설명선 overlay가 생기는 구조 대조 | 밝은 선=계면. 기존 불일치 판독의 재사용 |
| sample2 | f0,30,60 | 강한 반사와 거품/표면 무늬. 고정 geometry의 역사적 0–2초 범위 | 이후 카메라 이동 구간까지 같은 Recipe로 성능 확장 |
| sample4 | 14–56초의 기존 노출 표본 15개와 기본 분석 구간 실행 | 40–44초 움직임, 49.5/52초 보호점, 늦은 Foam 상단·내부 무늬·rim | 한 점의 승인 범위를 이웃 frame/전체 contour/모든 candidate로 확대 |
| sample5 water | 기존 노출 표본 10개 | 기울어진 실제 수면, dark Foam A, Foam 없는 water B/C | 기울어진 수면을 무조건 splash로 거절, A를 liquid-air 양성으로 변경 |
| sample6 beer | f0,146,436 | 얇은 동일 Foam층의 앞뒤 투영, 상단이 원본 화면 밖인 경우 | 투영 두 줄을 두 물리층/층 두께로 해석, 하단으로 upper를 대체 |
| sample7 milk | f0,532,1063 | 밝은 bulk liquid와 표면 거품의 혼동, 불명확한 lower | white=Foam, 불명확한 lower의 Oil 값 생성 |
| sample3 | **이번 routine 조사·decode 없음** | 지정된 legacy regression/engineering replay만 | 장면/geometry 변화가 있는 전체 구간을 연속 유면 recall 시험으로 재개 |

표본 판독은 새로운 human truth가 아니다. 이번 원본 시각 검토에서 보이는 질감·밝기·기하학적 관계는 가설을 점검하는 보조 관찰로 사용했다. 기존 reply의 역할·위치·가시성 권한은 그대로 유지한다.[E04][E07][E08][E09][E14]

---

## 5. 원인 분석: 서로 다른 세 손실을 분리

### 5.1 P2-S1: 계산은 맞고 역할 분리가 안 된다

고정 regional reference 비교는 14개 query, 반 pixel 중심의 양쪽을 포함한 15개 neighbourhood, joint/center-only 30개 기록을 남겼다.[E06]

| 지표 | Joint | Center-only |
|---|---:|---:|
| 모든 선언 중심에서 비교 가능 | 8/14 | 12/14 |
| 초기 reference 이후의 Oil 양성에서 interface 선호 | **0/6** | **0/6** |
| 잘못된 Oil target에서 structure/texture 선호 | **0/3** | **0/3** |

대부분의 미선택은 **정확한 거절이 아니라 abstention/측정 불가**다. 42초와 52초 양성은 세 부분을 모두 요구하는 표현 조건에서 먼저 손실된다. 이 사실을 원본 Oil 부재나 전체 detector의 proposal 부재로 바꿔 말하면 안 된다.

더 결정적인 반례는 다음과 같다.

| 기존 판독 | interface 비용 — 낮을수록 유리 | 역할 margin — 높을수록 유리 |
|---|---:|---:|
| 잘못된 target, 42초 | 0.1535881276 | 0.0532659808 |
| 실제 양성, 44초 | 0.1561067029 | 0.0513320798 |

잘못된 target이 **두 축 모두 더 유리**하다. 따라서 이 readout에 그대로 `cost <= threshold`와 `margin >= threshold`만 적용해서 해당 양성을 받고 해당 음성을 거절할 수 없다. 이 결론은 threshold sweep을 하지 않고도 성립한다.

**처분:** P2-S1의 patch/reference/transform/threshold 조정은 하지 않는다. 신뢰도 숫자가 아니라 관측 표현 또는 역할 비교 자체가 달라져야 한다. 다만 모든 가능한 역할 비교가 실패한다는 보편 명제는 아니다. 새 방식은 기존 반례와 공통 support 손실을 그대로 통과해야 한다.

### 5.2 sample4 Foam의 저장된 scoped/FULL 증거: component 범위가 front를 대신한다

사용자가 승인한 범위는 **f1620 / 54초 / X595 / source rows 812–816**이고, pixel-cell interval은 `[811.5, 816.5]`다. 정확한 Y 하나나 contour 전체를 승인한 것이 아니다.[E07]

```text
원본 영상·Canny                    Y813: interval 호환
  ↓
raw/clean white support            중심 열 Y813부터 존재
  ↓
기존 unsigned/signed alternatives  호환 위치 보존
  ↓
C1 component 전체 범위             global top Y808 / bottom Y833
  ↓  component phenotype·구조 substrate 관계에 따른 lower 선택
저장 실행의 raw Foam 후보          input index 22, Y833 (내부 무늬)
  ↓
episode formation                  해당 잘못된 front trajectory를 거절
최종 Foam                          null
```

실제 코드의 핵심은 `foam_front_detector.py`의 `_detached_material_phenotype`에서 `front_from_lower_edge`에 따라 component의 `ys.min()`/`ys.max()`를 고르고, `_component_evidence`가 이를 후보 위치로 사용하는 경계다. 기준 HEAD에서는 각각 785–823행, 826–1016행이다.[E16]

이 저장 실행에서 고칠 것은 “마지막 gate가 너무 엄격하다”가 아니다. 올바른 Y813 front 후보가 episode로 전달되지 않았다. 저장된 current-frame smoothing 값이 우연히 Y813인 것도 same-frame candidate provenance를 복구하지 않는다. 새 기본 NONE 실행의 최종 누락과 원인 단계의 동일성은 별도 연결 사항이다(§1.3).

또한 `bottom`을 `top`으로 바꾸면 Y808이 되어 여전히 승인 interval 밖이다. `낮은 gap member`, `가장 가까운 edge`, `가장 높은 white pixel`로 바꿔도 물리적 역할은 해결되지 않는다.

### 5.3 Water A: 앞단 support 자체가 밝기에 종속된다

A/f1232의 Foam upper는 X950에서 source rows 476–481 범위로 승인됐고 Canny Y477이 남아 있다. 하지만 중심 상단의 appearance support는 lightness/whiteness predicate에서 먼저 사라진다. cleanup 이후의 component perimeter만 잘 선택하는 개선은 이 사례를 복구하지 못한다.[E08][E09]

이것은 white threshold를 낮추라는 결론이 아니다. beer/milk/empty/rim 및 sample4 내부 무늬에 같은 변경을 적용하면 다른 오검지를 만들 수 있다. 원시 경계 관측과 absolute brightness 기반 material mask를 동일한 허용 관문으로 사용하지 않는 설계가 필요하다.

B/C에는 Foam층이 없다는 판독이 있으므로 A에서 발견한 edge/texture 경로를 “새 Foam 경로”로 일괄 활성화해서도 안 된다. A의 lower가 불명확하다는 사실은 Foam 부재나 Oil 값의 허용을 뜻하지 않는다.

### 5.4 Oil: 마지막 selector에 들어오기 전과 이후를 분리

기존 조사에서는 실제 target-vicinity 후보가 남아도 authority·tracklet·allowed owner 조건에서 사라지거나, 기존 owner 우선순위가 현재 관측과 어긋나는 사례가 기록됐다. 반대로 rank만 바꾸어도 이미 막힌 후보는 마지막 selector에서 회복할 수 없었다.[E13][E17]

sample4의 42.5–44초는 고립된 pixel 오차 문제가 아니다. 원본상 빠른 움직임이 있고, 누락과 다른 target 선택이 연달아 생기면 report에서 변화의 형태가 사라진다. 기존의 cost-first probe는 일부 수치를 되살렸지만 다른 Oil/phase 값과 끝부분의 물리 대상을 바꾸었다. 이를 성공으로 간주해 전역 assignment를 교체하면 안 된다.

향후 각 보호 구간에는 다음 funnel을 기록한다.

```text
원본에서 target 관측 가능
→ 해당 frame의 원시 boundary가 존재
→ candidate가 그 boundary의 측정/provenance를 보유
→ authority에서 살아 있음
→ 물리 association이 같은 대상에 연결
→ phase가 해당 owner를 허용
→ selector가 같은 frame의 후보를 선택
→ public validity·CSV·report에 동일하게 반영
```

각 단계의 수와 **첫 손실 원인**을 따로 남긴다. 정확한 물리적 첫 손실이 증거상 불명확하면 `UNKNOWN`으로 남긴다. 관측이 1개 늘었다는 사실만으로 앞단 문제가 고쳐졌다고 하지 않는다.

---

## 6. 설계 방향: 경계 관측·역할·높이·시간 소유권 분리

### 6.1 유지할 구조

```text
현재 영상 / ROI / 기존 전처리
    ├─ Oil evidence / candidate families
    └─ Foam evidence / raw boundary alternatives
             ↓
같은 frame의 경계 역할 증거 (아직 final observation 아님)
    ├─ Oil authority → directed tracklet → phase → selector → Oil projection
    └─ Foam raw-front selection → 기존 Foam episode
             ↓
기존 ObservationSequenceResolver의 단일 composition
             ↓
TrackingSample / CSV / event / 기존 report
```

새 진단 도구가 두 번째 Oil owner가 되거나 report가 candidate를 다시 선택하는 경로를 만들지 않는다. raw image 관측을 공유할 수는 있지만, 최종 Foam의 승인/거절을 Oil의 mask·cutoff·좌표 선택권으로 바꾸지 않는다.[E12][E18]

### 6.2 최소 내부 계약 — 기존 타입을 확장할 때의 책임

다음은 **제안 스키마**이며 현재 코드에 구현됐다는 뜻이 아니다. 기존 `BoundaryCandidate`/sidecar에 동일 정보가 있으면 재사용하고 중복 공개 API를 만들지 않는다.

| 논리 정보 | 필수 의미 | 금지된 해석 |
|---|---|---|
| `boundary_ref` | source frame, 원본 좌표계, 실제 edge/path/face ID, 측정 support의 연결 | truth Y나 과거 선택값에서 만든 가상 경계 |
| `side_observations` | 경계 양쪽의 현재 픽셀 관측, 각 관측의 support·censoring·provenance | 미측정=0, 밖에 안 보이는 구조=없음 |
| `role_evidence` | liquid upper / Foam upper / 내부 texture / structure / unresolved의 증거와 경쟁 설명 | 단순 순위 1위=물리 대상, 모든 구조를 화학적으로 분류 |
| `center_observation` | 고정 X에서 실제 관측된 같은 경계의 교차점/모호한 대안 | sector median, fit curve 또는 nearest edge를 실측값으로 승격 |
| `scalar_eligibility` | 현재 대상·가시성·고정 X 관측이 수치 출력에 충분한가 | presence만으로 좌표 출력 |
| `association_support` | 기존 owner와의 연속성을 지지/반대/판단 불가로 구분 | 유사 appearance나 track ID 유지 자체가 물리 동일성 |

`UNAVAILABLE`과 `AMBIGUOUS`는 구분한다. 입력이 없어 못 잰 것과, 측정했는데 경쟁 설명이 남은 것은 다른 상태다. 이 구분을 늘리기 위해 UI 페이지를 추가할 필요는 없다. 기존 trace 및 평가 기록으로 충분하다.

### 6.3 Foam의 네 가지 축

아래 축을 독립적으로 다룬다.

1. Foam 물질이 있다고 볼 근거.
2. 목표 upper boundary가 화면에서 관측 가능한지.
3. 해당 frame·고정 X에 사용할 upper coordinate가 있는지.
4. 여러 frame의 관측이 실제 Foam episode를 이루는지.

A는 Foam 존재와 upper 양성을 제공하지만 lower는 불명확하다. beer cropped-upper는 물질/하단이 보여도 upper coordinate를 주지 못한다. sample4 내부 texture는 Foam 내부 관측이지만 front가 아니다. 이 세 가지를 같은 `foam detected` 불리언으로 처리하지 않는다.

---

## 7. 다음 판별 실험의 설계: 무엇을 만들고 무엇을 만들지 않는가

### 7.1 선택할 방향

**기존 관측 경계에 결합된 양측 material support와 구조 설명을 함께 평가하는 방식**을 우선한다. 핵심은 contour 검출을 더 만드는 것이 아니라, 같은 경계의 어느 쪽에 어떤 종류의 현재 영상 지지가 있고 그 관계가 front인지 내부 변화인지 비교하는 것이다.

이는 완성된 classifier 선택이 아니다. 현재 증거만으로 성공을 약속할 정도의 분리 법칙은 확보되지 않았다. 따라서 아래 `P5 역할 비교 feasibility`는 한정된 구현·실험 과제이고, 그 결과가 실패하면 역할 판별 미해결을 정직하게 남긴다. 실패를 report smoothing이나 authority 우회로 숨기지 않는다.

### 7.2 구현할 연산 계약

**입력:** 기존 native raster, 동일 전처리 결과, 실제 edge graph/기존 material-path 및 Foam alternatives, effective/glare 가용성, 이미 등록된 구조 reference의 관측 가능한 지원 범위. human label·source timestamp·sample 이름·정답 좌표는 평가기에만 전달한다.

**연산:**

- 기존 관측된 후보 경계에서 시작한다. P1·edge graph·signed/unsigned alternatives를 재사용하며 새 edge generator나 top-k 확대를 첫 변경으로 넣지 않는다.
- 후보가 실제로 관측된 부분의 양쪽을 별도 측정한다. 같은 후보를 설명하는 material transition, 내부 texture/ribbon, 구조/반사 경쟁 설명은 동일한 현재 픽셀·동일한 변환 자유도에서 비교한다.
- absolute white mask가 0이라는 이유만으로 원시 boundary를 제거하지 않는다. 연속적인 밝기·국소 대비·texture/edge 배열·chromatic 관측은 가용성까지 보존한다. 새 texture 값을 Foam 정답으로 간주하지 않는다.
- component 전체의 높이/면적과 candidate-local front 역할을 분리한다. 동일 material 지지가 경계 양쪽에 이어지는지, 실제 양측 변화가 경계와 맞물리는지, 구조 설명이 같은 support를 설명하는지를 보존한다.
- 전체 2D 배열 또는 관측된 경계의 배치 정보를 활용하더라도, 닫힌 component가 반드시 있어야 한다는 조건이나 missing edge를 메운 연결을 만들지 않는다. 앞뒤 투영·기울어진 수면·censored support를 별도 대안으로 남긴다.
- structure 설명이 없다는 사실을 자동 positive 점수로 바꾸지 않는다. 단순히 비교가 불가능하면 그 상태를 반환한다. geometry/정지/곡률 하나만으로 실제 정지 계면을 구조로 거절하지 않는다.
- 한 가지 물리적 역할이 비교 계약상 지지되고 center 관측이 있을 때만 그 경계를 scalar 후보로 전달한다. 여러 역할이 동등하거나 centre가 없으면 수치를 강제하지 않는다.

**출력:** candidate-bound role support/opposition/unavailable, support 영역, 원래 edge/path ID, scalar eligibility, 이유. 첫 feasibility 단계에서는 final Oil/Foam 값이나 phase를 바꾸지 않는다.

### 7.3 실제 구현 전에 반드시 선택·동결할 항목

“물리적 역할 증거를 더한다”는 문장만으로 구현 완료 처리하지 않는다. 담당 구현자는 real readout을 보기 전에 다음을 한 preflight에 확정한다.

| 동결 항목 | 명세 요구 |
|---|---|
| 현재 support | path/face의 어떤 픽셀과 어느 깊이의 양측 영역을 읽는지, 보간 없는 좌표 연결 |
| 측정/경쟁 모델 | model별 실제 수식 또는 실행 함수, 비교 가능한 출력의 의미 |
| 크기·스케일 | 최대 support, frame/ROI당 비용, 누락과 경계 처리, transform 자유도 |
| 결정 규칙 | 점수 정규화, ambiguity, unavailable, 초기 operating point. post-hoc threshold sweep 금지 |
| 구조 반대 증거 | 어느 현재 support에서 측정되는가. 없거나 censored일 때의 처리 |
| 단일 ablation | 새 결합/배치 정보를 제거한 기존 수준의 비교. 입력 영역·관측수 차이를 별도 기록 |
| 평가 inventory | 양성·잘못된 target·정지 계면·빈 용기·crop 밖·unclear를 모두 고정 |
| 변경 범위 | 기존 detector/episode/Recipe/truth 불변, offline 출력만 |

여기서 **구체 연산이 기존 네 band 평균, plane/step/ribbon residual, cellular global rank, 단순 reference matching과 같다면 새로운 방식으로 인정하지 않는다.** 더 큰 patch 또는 가중치 변경뿐인 경우에는 구현에 들어가지 않고 기존 종료 결과를 재사용한다. 이 조건은 새로운 거대 framework를 만들라는 뜻이 아니라 중복 실험을 줄이기 위한 것이다.[E06][E17][E19]

### 7.4 이전 실패와의 차이를 확인하는 필수 대조

| 이전 접근 | 관찰된 한계 | 새 구현이 설명해야 할 차이 |
|---|---|---|
| White/Chromatic support + component 극값 | sample4 내부 무늬 선택, dark A 상단 support 소실 | mask와 실제 front를 분리하고, 실제 경계의 양측 관측을 사용 |
| 전역 cellular/texture rank | 일부 frame의 위치가 그럴듯해도 실제 reviewed 대상/소유권 개선 없음 | 전역 activity 최댓값이 아니라 candidate-local 역할·경계 결합 |
| 네 band 또는 plane/step/ribbon 비교 | 실제 구조도 유사한 appearance partition을 만들 수 있음 | 기존 출력에 없던 구체 배열/관계 정보와 구조 경쟁을 명시. 이름 변경 금지 |
| P2-S1 regional exemplar | wrong target이 true target보다 비용·margin 모두 유리 | 같은 임계값 재조정이 아닌 다른 정보/연산이 필요 |
| LK/appearance tracking/공동 transform | 구조/광학 warp도 잘 추적됨 | 시간 일치만으로 material identity를 만들지 않음 |
| Cost-first association 또는 selector score 변경 | 일부 누락 개선과 다른 identity/phase 변화가 동반 | 검증된 현재 관측에 기반한 제한된 owner 수정으로 분리 |

### 7.5 고정 control matrix

첫 feasibility는 범위를 크게 늘리지 않고 다음 기존 자료를 모두 ledger에 남긴다.

- sample4: 초기/기존 실제 front, 40–44초 Oil 양성·오대상, 49.5/52초 보호점, late upper 양성, 세 내부 texture 음성, rim 및 mixed control. 미검토 f1635는 미검토로 유지.
- water: inclined 실제 수면, A의 dark Foam upper 및 unclear lower, B/C water upper와 no-Foam, empty.
- beer: 동일 층 앞뒤 투영, cropped upper.
- milk: 밝은 bulk liquid, unclear lower.
- 기존 synthetic copied distractor, optical warp, 정지 계면, 누락/부분 support 및 polarity 반전 control.

서로 다른 영상에 same-scene reference가 없는 경우는 비교 불가로 표시한다. P2처럼 공개 control 전체가 비교 불가인 구현은 **generic adoption 준비가 안 된 상태**다. 이를 실패를 피하기 위해 control을 제외하는 근거로 쓰지 않는다.

### 7.6 진행/중단 판정

feasibility에서 긍정적인 국소 결과가 나와도 바로 O3로 승격하지 않는다. 적어도 다음은 만족해야 다음 단계 설계를 진행할 수 있다.

- 기존 양성을 전부 잃은 채 음성을 거절하는 퇴화 해법이 아니어야 한다.
- sample4에서 기존 raw-front 축약과 다른 유효한 관측 경로를 보여야 한다. 위치만 맞고 다른 물리 경계를 선택한 것은 별도다.
- A/B/C의 서로 다른 역할을 유지해야 한다. A upper를 얻기 위해 B/C를 Foam으로 만드는 변경은 실패다.
- 내부 texture/rim의 잘못된 지지를 함께 보고해야 한다. abstention을 정답 거절로 세지 않는다.
- fixed-X interval은 수치 적합성을 보는 보조 평가일 뿐, 그 interval에 가장 가까운 대안을 inference에서 선택하지 않는다.
- 효과가 작거나 generic control이 미평가이면 그 범위를 분명히 하고 formal O2를 유지한다.

이번 명세의 **운영 제안**은 한 고정 구현 + 한 구조적 ablation 뒤에 반드시 계속/종료 결정을 내리는 것이다. 같은 실패에 대한 threshold/reference/크기 조정 사슬로 넘어가지 않는다. 동일 관측이 true와 false를 구별하지 못하면 새 증거의 가치를 입증하기 전에는 해당 계열을 닫는다.

---

## 8. 구현 작업 묶음과 전체 의존성

### 8.1 전체 순서

```text
P0: 현재 기준·평가 inventory 고정 (대부분 재사용)
              │
P1: offline 표현 보존 완료 ─────────────────────────────┐
              │                                         │
P5-a: Foam 경계 역할 feasibility + raw-front 설계         │
              │                                         │
P2: 다른 물리 역할 관측의 검증 ── O2 shadow/수용 gate ───┘
              │
       ┌──────┴────────┐
P3/O3: Oil authority/association   P5-b: Foam raw-front 운영 연결
       │                              │
P4/O4: phase/handoff             P5-c: 필요가 입증된 episode 수정만
       └───────────────┬──────────────┘
                P6/O5: 통합 회귀·Windows·report 이해 확인
                       │
                P7: S11 종료/범위 제한/실패의 명시적 결정
```

Foam의 독립 진행을 Oil gate 우회로 해석하지 않는다. O2 Windows shadow와 이후 통합 field qualification은 목적이 다르다. operator 실행 부담은 묶어서 줄일 수 있지만, 사전 gate와 최종 gate를 하나의 PASS로 합치지 않는다.

### 8.2 작업별 입력·출력·완료 조건

| 작업 | 코드/문서 소유 경계 | 실행 산출물 | 완료 조건 / 하지 말 일 |
|---|---|---|---|
| P0 — 기준 고정 | `work-plan`, SSOT, witness validation, 기존 inventory | exact SHA, defaults, control manifest, 비교 항목 | 새 truth 시스템 없음. 공개/Windows/퇴역 source 구분. 이번 감사 결과를 재사용 |
| P1 — 유지 | `oil_material_path.py`, `scripts/s11_center_path_trial.py`, 기존 tests | 통합된 offline API·baseline pin 재사용 | 이미 완료. representation을 효과로 포장하지 않음 |
| P5-a/P2 — 역할 feasibility | 기존 `tests/diagnostics` raster/geometry/math owner 우선 | 동결 연산·한 ablation·모든 control readout·종료 결정 | production consumer 없음. P2-S1 재개 금지. §7 조건 준수 |
| P5-b — raw Foam front | `foam_front_detector.py`, `phase_frame_detection.py`, candidate assembly | boundary-local candidate provenance, fixed-X eligibility, trace | 올바른 raw front를 전달하고 component extreme을 물리 위치로 쓰지 않음. 기존 episode 고정 |
| P3/O3 — Oil evidence/association | `oil_phase_identity.py`, `oil_candidate_authority.py`, `oil_interface_tracklets.py`, resolver의 기존 owner | 승인된 typed evidence, 제한된 assignment 변화, split/handoff 진단 | O2 및 별도 O3 계획 후. 전역 cost-first·motion-only anchor 금지 |
| P4/O4 — phase | `oil_phase_lifecycle.py`, 기존 evidence engine/selector 경계 | FULL/drain/refill, initial EMPTY/fill/drain의 닫힌 전환 검증 | 현재 물리 관측이 맞는데 phase가 막는 원인이 입증된 경우만. snapshot 좌표/ID 복사 금지 |
| P5-c — Foam episode | `foam_episode_resolver.py` | 올바른 raw front가 downstream에서 손실되는 별도 원인·수정 | raw 후보가 틀렸으면 이 작업을 열지 않음. 밝기/단일 motion/extent로 episode 승인 금지 |
| P6 — 통합 | `observation_sequence_resolver.py`, application/storage/report 기존 owner, Windows procedure | default A/B, stage funnel, CSV, report, 9구간 평가·resources | sample4만 좋아지는지 확인하는 데서 끝내지 않음. 정확한 code/config/source identity |
| P7 — 종료 | `work-plan`, roadmap, 현행 validation/evidence | 실용 목적 수용/제한/실패, 알려진 잔여 C/U, rollback 정보 | edge-case 무기한 pursuit 금지. FIELD FAIL은 실제 수용 전까지 유지 |

새 helper가 필요하면 기존 책임 안에서 최소 분리한다. 표에 있는 모든 파일을 수정하라는 뜻이 아니다. 한 번에 한 causal seam만 변경하고 해당 테스트와 companion 설계만 갱신한다.

### 8.3 P5-b 상세 작업 명세

**실행 조건:** §7에서 raw boundary의 역할을 구분할 근거가 확인되고 해당 운영 연결의 수용 계획이 승인됨.

1. 기존 component 분석은 material evidence 산출에 남긴다. component `front_y`가 자동으로 최종 raw-front 위치가 되는 책임을 분리한다.
2. 기존 edge/alternative 중 실제 role-supported boundary를 나타내는 후보를 구성한다. 같은 frame의 관측 ID·support·source 좌표를 보존한다.
3. fixed-X에서 관측이 없으면 side-support 또는 물질 존재만으로 scalar를 만들지 않는다. centre gap을 path fitting으로 채우지 않는다.
4. candidate metadata는 판별에 사용된 실제 지원/반대 관측을 담되, debug ON/OFF에 따라 값이 달라지지 않게 한다.
5. 기존 Foam episode와 final composition을 그대로 실행한다.
6. raw-stage 개선과 final 관측 개선을 구분해 비교한다. raw가 고쳐져도 episode가 전부 거절하면 기능 개선 완료가 아니다.
7. default OFF 경로 또는 명시적 versioned candidate 실행을 먼저 보존하고, 채택 전 동일 입력의 기존 출력 기준을 남긴다. 실험 설정을 기본 Recipe로 슬쩍 바꾸지 않는다.

필수 테스트: global top/bottom이 center target과 다른 경우, sample4처럼 내부 texture를 raw front로 전달하는 경우, dark support, foam 없는 water, bright milk, cropped upper, 앞뒤 투영, centre 결손, polarity 반전, 관측 불가/동률, Oil 불변, debug equality, source-Y equality.

### 8.4 P3 상세 작업 명세

검증된 현재 역할 증거가 생겼다면, association에서 **기존 track의 성숙도**와 **현재 frame의 물리적 지지**를 구별한다. 오래 살아남은 track에 자동 우선권을 주어 실제 움직임을 가로채는 문제와, nearest-cost로 구조에 점프하는 문제를 모두 대조한다.

- 현재 frame에서 경쟁하는 row와 parent 비용·역할 지지·충돌·방향을 같은 ledger에 기록한다.
- 기존 bounded window와 one-to-one assignment를 재사용한다. 추가 장기 smoothing/무제한 미래 문맥을 만들지 않는다.
- 역할이 모호한 crossing/split은 같은 ID로 강제 연결하지 않는다. 필요 시 현재 관측을 보존한 채 기존 허용 범위 내에서 확정을 유예하고, bounded 기한 이후에도 불명확하면 UNKNOWN을 유지한다.
- 후보 자체의 authority 부족을 assignment 수정으로 우회하지 않는다.
- sample4의 국소 개선뿐 아니라 40–56초 전체, 정지 실제 계면, rim/texture, partial loss와 큰 실제 움직임을 한 번에 대조한다.
- 결과물은 `누락 복구 수` 외에 `새 wrong-owner run`, `다른 protected row 손실`, `phase 변경`과 `Foam 변경`을 포함한다.

이 작업은 cost-first 실험의 재도입이 아니다. 추가 증거가 실제로 어느 assignment를 바꾸는지 설명할 수 있을 때만 변경한다.

### 8.5 P4 상세 작업 명세

phase의 목적은 이미 관측된 물리적 흐름의 입장·전환·종료를 관리하는 것이다. phase가 경계 좌표를 추론하는 역할이 아니다.

- 초기 FULL의 coordinate-free 상태에서 실제 drain 계면이 나타나면 독립된 현재 관측을 통해 진입해야 한다.
- 실제 급 refill은 급격하다는 이유만으로 smoothing되거나 구조로 handoff되어서는 안 된다. 상단으로 사라진 후 FULL은 좌표 없이 종료한다.
- 초기 EMPTY에서 splash/벽 흔적과 실제 진입을 구분하고, 형성된 fill 이후 owner를 잃었을 때 실제 drain의 복귀가 영구 차단되지 않아야 한다.
- 새 owner를 허용할 때 이전 ID·snapshot 좌표를 복사하지 않는다. 남아 있는 이전 owner, 경쟁 다중 owner, 반대 물질 증거를 그대로 검증한다.

이미 있는 R22 전환 구현을 일괄 교체하지 않는다. 실제 current-row 및 role가 충분한데 어느 predicate가 중요한 맥락을 막는지 확인한 경우에만 그 owner를 수정한다.

---

## 9. 검증 설계 — 점수와 실제 효용의 연결

### 9.1 세 층의 검증

| 층 | 질문 | 대표 산출물 |
|---|---|---|
| 구현 무결성 | 원래 픽셀·후보·좌표·기준값을 보존했는가? | unit, input hash, source identity, debug equality, provenance |
| detector 관측 | 필요한 실제 경계를 남기고 잘못된 구조·texture를 억제하는가? | 역할별 양성/음성/불가, raw→public funnel, interval compatibility, wrong/missing runs |
| 제품 목적 | report에서 방향·반전·주요 Foam 흐름을 읽을 수 있는가? | episode별 A/B/C/U, 사건 순서·방향·관측 공백, report-only 판독 |

첫째만 PASS인 결과를 셋째의 성공으로 옮겨 적지 않는다. 이번 263개 테스트와 P2/P5 재검산은 주로 첫째와 원인 결합을 확인한 것이다.

### 9.2 공정한 비교 조건

기준과 후보는 동일 source/Recipe/분석구간/샘플링/initial state에서 실행한다. detector variant만 한 가지 바꾼다. `Local XY OFF`, 별도 reference 입력 여부, debug level, runtime version, 코드 SHA를 명시한다.

샘플링을 바꿔 발생한 관측 밀도 향상과 판별기 개선을 혼합하지 않는다. 선택한 source time 배열을 저장해 같은 배열로 비교한다. 새 descriptor가 느려져 처리량을 크게 잃지 않는지 native/debug-OFF 비용을 별도로 측정한다.

오프라인 관측 도구와 실제 application 실행도 구분한다. namespace 또는 raw support만 달라진 결과는 detector 품질 개선이 아니다. 최종 candidate/sequence/public 단계까지 원인을 연결해야 한다.

### 9.3 필수 측정값

- 보호된 episode에서 올바른 같은 대상의 numeric 관측 간격과 leading/trailing 공백.
- wrong target의 연속 시간, 명확한 구조로의 handoff, 새 wrong episode.
- 방향·반전·급변의 보존 여부. source Y 방향과 물리 상승/하강을 혼동하지 않음.
- Foam 존재·upper 위치·Oil/Foam 순서·소멸 후 residue 오류의 구분.
- 유효한 uncertainty interval에서만 scalar compatibility 및 interval까지의 최소 거리. 정확한 Y 오차로 과장하지 않음.
- 시작/종료·crop·visibility·unavailable와 각 단계의 첫 손실.
- native debug-OFF 시간, peak memory, debug 추가 비용, 장기 누적/코퍼스 스케일 문제.
- selected candidate = sequence raw = public/CSV raw와 각 series validity.

한 영상의 상관된 frame 100개를 독립 표본 100개로 세지 않는다. 전체 row accuracy가 좋아졌어도 하나의 중요한 rapid refill을 잃으면 별도로 실패 처리한다.

### 9.4 Report-only 목적 검증

최종 후보를 보지 않은 검토자가 **사용자에게 실제 제공할 report만** 보고 다음을 답한다. report에 이미 포함된 원본 맥락 자산은 사용할 수 있다. 이후 원본 물리 판독과 비교한다.

| 질문 | 성공의 의미 |
|---|---|
| 어떤 구간에서 계면이 내려가고 올라가는가? | 주요 방향과 순서가 맞음 |
| 반전·급 refill·최저/회복 흐름은 어디에 있는가? | 중요 사건이 사라지거나 엉뚱한 구조에서 생성되지 않음 |
| Foam은 언제 나타나고 사라지는가? | splash/residue와 실재 Foam 구간을 혼동하지 않음 |
| Oil과 Foam이 동시에 보일 때 어떻게 배치되는가? | 두 독립 대상과 위아래 관계가 맞음 |
| 어느 구간은 수치 판단이 어렵거나 관측이 부족한가? | 근거 없는 연속 그래프가 아니라 불확실성을 읽을 수 있음 |

검토자가 원본을 다시 처음부터 보아야 대부분의 질문에 답할 수 있다면 report-only 목표는 아직 부족하다. 다만 이것을 곧바로 신규 UI 프로젝트로 돌리지 않는다. 어떤 detector 관측 공백/오대상이 판단을 막았는지 먼저 연결한다.

이 검토는 pixel-perfect annotation 작업이 아니다. 이미 있는 사건·방향 판독을 재사용한다. 개발자가 예상 정답을 알고 자신이 만든 report를 읽은 결과는 독립 이해도 평가로 세지 않는다.

---

## 10. Windows 최종 검토 매트릭스

다음은 기존 승인된 물리 판독의 재정리다. 시간은 source-video seconds이며 `약` 경계는 frame-exact truth가 아니다. 모든 현장 보고는 아홉 구간을 빠짐없이 포함한다. 아래 ID는 이 문서의 실행용 별칭이며 원본 판독 파일의 식별자를 변경하지 않는다.[E04]

| 구간 ID | 시간 | 반드시 전달되어야 하는 맥락 | 대표 실패 |
|---|---|---|---|
| `WS1-BASE-FULL-PREFIX` | 480–약550 | Oil은 가득 차 있고 계면은 보이지 않음. Foam 없음 | 구조를 수치 Oil로 추적 |
| `WS1-BASE-DRAIN` | 약550–662 | 실제 계면이 나타나며 전반적으로 하강 | lower 구조/glare owner, 긴 연속 누락 |
| `WS1-BASE-RAPID-REFILL` | 662–약663.6 | 실제 빠른 상승 후 상단으로 소실 | 상승을 smoothing/누락으로 삭제, 다른 선으로 handoff |
| `WS1-BASE-FULL-SUFFIX` | 약663.6–780 | FULL 유지, Oil/Foam 좌표 없음 | 725초 전후 반사선 등을 Oil로 출력 |
| `WS1-ACCUM-EMPTY` | 480–약653 | 빈 상태, Oil/Foam 없음 | 벽/바닥을 Oil 또는 Foam으로 출력 |
| `WS1-ACCUM-ENTRY-SPLASH` | 약653–672 | 유입·splash와 실제 상승 Oil을 구별, Foam 아직 없음 | splash/벽 흔적을 Foam 또는 Oil owner로 선택 |
| `WS1-ACCUM-FOAM-LAYERED` | 약672–680 | Foam upper와 Oil lower가 독립적으로 존재 | Foam upper를 Oil로 선택, 둘 중 하나를 잘못 veto |
| `WS1-ACCUM-POST-FOAM` | 약680–700 | Foam 소멸, Oil 계면 유지 | residue를 Foam으로 유지 |
| `WS1-ACCUM-DRAIN` | 약700–780 | 실제 하강으로 반전하며 벽 잔류 흔적은 대상 아님 | owner-loss 때문에 drain 전체 누락, residue handoff |

구간별로 actual sampling coverage, final Oil/Foam 수치/유효성, 연속 run, source-Y 방향/범위, longest wrong/missing run, owner/phase 전환, PASS/FAIL/NOT_EVALUATED를 기록한다.

정확한 Y anchor가 없더라도 presence/absence, 방향, 사건 순서, Foam 층 구분의 현장 검토는 가능하다. 이를 핑계로 수십 개의 새 pixel 좌표를 먼저 요청하지 않는다. 반대로 정확도 오차가 필요하면 해당 범위의 별도 position truth가 있어야 한다.

원본 SHA-256/크기/해상도/FPS/길이의 확인은 다음 정식 현장 실행에서 현장에 기록한다. 이번 감사에서 private basename이나 원본 파일 반출을 요구하지 않는다. 이전에 이미 종료된 saved-material inventory와 사용자 판독을 반복하지 않는다.

---

## 11. 자원·회귀·rollback

### 11.1 자원 계약

P1의 모든 보존 경로나 pixel graph 전체를 매 frame 무제한으로 운영 경로에 붙이지 않는다. offline conservation은 검증 도구의 성격이고, production에는 기존 bounded model에 맞는 representation/sidecar만 들어가야 한다.

새 구현은 preflight에 frame/ROI당 관측 수·support pixel 수·candidate 수·시간 window·transform 수·메모리 상한을 명시한다. 기존 bound와 성능 기준은 가능한 한 그대로 사용한다. 비교 후에 timeout을 늘려 실패를 숨기지 않는다.

첫 raw-role 판별 단계에 full-video flow cache, 큰 learned model, 외부 서버 inference를 추가하지 않는다. 보안 PC에서 실행 가능한 현재 개발 범위를 유지한다. 학습 모델 도입은 별도의 근거·비용·검증 계획이 필요한 범위 변경으로 다룬다. 조명/센서 교체는 별도 scope 승인 없는 현재 작업의 필수 전제가 아니다.

### 11.2 회귀 계약

국소 구현에는 관련 unit/synthetic와 저장 입력 비교를 사용하고, 운영 consumer 연결 때 default FULL application 비교를 추가한다. field 수용 때는 기존 canonical procedure를 따른다.

sample3은 명시적 legacy regression 또는 engineering replay 권한이 있을 때만 해당 wrapper를 사용한다. 일부 케이스가 실행되지 않았다면 partial/NOT_EVALUATED로 적는다. 빠진 case를 제거한 새 분모를 과거의 full canonical 결과와 비교하지 않는다.

원래 scalar basis와 새로운 fixed-center basis가 다른 경우, 과거 Y 정답을 새 basis의 동일 오차 기준으로 사용하지 않는다. schema/runtime 의미 변경은 기록하고 source-bound uncertainty interval의 실제 범위에서만 비교한다.

### 11.3 rollback 단위

- 역할 측정만 추가한 단계: consumer가 없으므로 source/trace 변경만 제거 가능한 구조.
- raw Foam candidate 연결: 기존 raw-front 경로와 frozen baseline을 보존하고 통합 후보 단위로 되돌릴 수 있어야 함.
- Oil authority/association: phase 변경과 같은 commit에 섞지 않아 원인을 분리.
- phase/episode: 독립 손실이 확인된 owner만 수정. 기존 coordinate-free/no-copy/independence 계약 유지.
- report: 새 numeric/보정 로직을 넣지 않으므로 detector rollback이 report 의미를 뒤집지 않아야 함.

---

## 12. 작업 예산과 종료 규칙

### 12.1 집중할 순서

**첫 구현 우선순위는 P5 raw-front 역할/측정 경계, 다음은 검증된 역할 관측의 Oil association 연결이다.** 이유는 P5에서 현재 원본→후보 손실 위치가 가장 구체적으로 좁혀졌기 때문이다. 이것이 Oil을 나중에 잊어도 된다는 뜻은 아니다. 전체 program에는 Oil 방향/반전 회복과 Windows 사건 검토를 끝까지 남긴다.

자료 정리·viewer 개선·새 표본 수집은 이 두 경로의 결정을 바꾸는 경우에만 수행한다. 이번에 이미 확인한 P2 비용 재검산과 P5 위치 재확인은 반복 작업으로 넣지 않는다.

### 12.2 제안하는 timebox — 일정 약속이 아닌 운영 제한

| 묶음 | 제안 예산 | 예산 종료 시 결정 |
|---|---|---|
| 기존 증거 재사용 및 fixed preflight | 0.5–1 개발일 | 구현 연산·반례가 구체적이지 않으면 코딩 시작하지 않음 |
| P5/P2 한정 feasibility + 한 ablation | 2–4 개발일 | 진전 없음/기존 반례 충돌이면 해당 방식 종료. threshold 사슬로 연장하지 않음 |
| 통과한 raw-front 운영 연결·로컬 비교 | 2–3 개발일 | raw와 final 효과를 함께 판정. 모두 UNKNOWN이면 기능 개선 미달 |
| 승인된 Oil association·필요한 phase 수정 | 3–5 개발일 | 중요한 맥락 개선과 다른 구간 회귀를 함께 결정 |
| 통합·현장·report 검토 | 실행 환경/승인 일정에 따름 | 정확한 후보의 수용/제한/실패 결정 |

이 숫자는 측정된 소요 시간이나 보장 일정이 아니다. 구현 인력·현장 접근을 모르므로 전체 완료 날짜는 정하지 않는다. 목적은 동일 실패 계열에서 무한히 반복하지 않게 하는 것이다.

### 12.3 S11을 닫는 세 가지 가능한 결과

| 결과 | 의미 | 상태 처리 |
|---|---|---|
| 목적 충족·수용 | formal gate와 exact Windows 검토를 통과하고 주요 움직임의 맥락이 유지됨. 잔여 C와 제한된 U를 문서화 | 합의된 S11 완료. 새 edge-case는 후속 backlog |
| 제한된 범위에서 유효 | 특정 촬영/가시성에서 효과는 있으나 generic/field 미평가 또는 중대한 한계가 남음 | 범위 제한을 명시. 전체 FIELD PASS로 바꾸지 않음 |
| 이번 방식은 미달 | 양성 대부분 손실, 구조 오검지, 중요한 흐름 누락 또는 모든 출력 abstain | 그 구현 계열 종료, 현 baseline/판정 유지. 문서가 많아졌다는 이유로 완료 선언하지 않음 |

이전 실패를 전부 다시 고칠 필요는 없다. 현재 목적에 영향을 주는 반복적 A/B를 우선 제거하고, C를 끝없이 줄이지 않는다. 단, 이미 존재하는 입력 무결성·보안·출처·소유권 계약을 edge-case라는 이름으로 삭제하지 않는다.

---

## 13. 문서 반영 범위와 인수인계

이번 산출물은 `sample/output/s11-program-audit-20261011-001/`의 감사 결과와 함께 보존할 수 있다. 아직 운영 설계로 승인한 문서는 아니므로 `work-plan`의 합격 상태나 현행 architecture를 자동 교체하지 않는다.

다음 구현을 채택할 때 필요한 최소 갱신은 다음과 같다.

- `work-plan`: 현재 P2-S1 종료와 P5 위치 checkpoint 완료 이후의 **한 가지 다음 실행 계약**, 수용 상태, 참조 경로.
- witness architecture/validation: 실제 선택된 역할 연산·support·수치·control 및 O2/O3 경계만 갱신.
- logic map: 운영 consumer를 실제로 연결했을 때 정확한 owner 변화만 갱신.
- failure registry: 기존 F02/F04/F07/F09/F10으로 설명되지 않는 새 반복 메커니즘이 확인된 경우에만 추가.
- evidence: 모든 control 결과, 원래 실패, 중단/채택 이유, exact SHA, raw/final 차이와 physical acceptance 범위.

현재 일부 문서의 역사적 표현이 최신 상태와 다르다. 예를 들어 오래된 P2 preflight 제안은 최신 종료 기록보다 우선하지 않는다. 이것은 작은 정리 항목이며, 대규모 docs 재편이나 S11-M을 detector 작업보다 먼저 시작할 이유는 아니다.

### 완료 보고에 반드시 포함할 구분

```text
구현된 것 / 실행된 것 / 검토한 기존 증거
새로 나아진 실제 관측 / 유지된 기존 양성 / 새 wrong-target 또는 공백
아직 미평가인 Windows·holdout·report 항목
정확한 source/config/code identity
채택·미채택·폐기 및 다음 owner
```

“tests PASS”, “후보 증가”, “곡선이 매끈함”만으로 끝내지 않는다.

---

## 14. 외부 연구의 제한적인 활용

Eppel & Kachman의 투명 용기 계면 연구는 용기 경계와 가능한 곡선 주변의 상대 밝기 변화·edge density 변화·법선 대비 gradient 방향 등을 사용한다. Eppel의 후속 곡률 연구는 용기 표면의 반사/구조와 내부 물질을 구분하기 위해 용기 형상 가정을 이용한다.[R01][R02]

이 자료는 **경계 주변 관측과 용기 구조를 함께 보는 방향**의 참고다. 압축기의 작은 원형 sight glass, 기울어진 동적 수면, Foam, 겹친 앞뒤 투영에 그대로 성능이 이전된다는 근거는 아니다. 특히 용기 대칭·곡률 가정을 현재 Recipe ellipse와 동일시하거나, 수평/타원 prior로 실제 급변을 거절하는 설계를 바로 도입하지 않는다. 논문의 정확도 숫자를 S11 예상 검출률로 사용하지 않았다.

- [R01] Sagi Eppel, Tal Kachman. *Computer vision-based recognition of liquid surfaces and phase boundaries in transparent vessels, with emphasis on chemistry applications*. arXiv:1404.7174, 2014. 공식 초록 확인.
- [R02] Sagi Eppel. *Using curvature to distinguish between surface reflections and vessel contents in computer vision based recognition of materials in transparent vessels*. arXiv:1506.00168, 2015. 공식 초록 확인.

이 문서의 구현 제안은 논문 알고리즘을 재현·검증한 결과가 아니라 저장소 원인 분석에 기초한 설계 판단이다. 추가 논문 검색보다 현재 고정 control에서의 한 번의 완결된 비교가 우선이다.

---

## 15. 근거 문서 및 코드 인덱스

모든 저장소 경로는 기준 HEAD `4d84f70…`를 기준으로 한다. [E17]의 cellular closeout만 별도 보존 Git object에서 읽었으며 현재 운영 코드가 아니다. 경로·hash·행 수의 기계 기록은 `evidence/source-ledger.json`에 있다.

| ID | 근거 | 주된 사용 범위 |
|---|---|---|
| E01 | `docs/00-project/work-plan.md` | 현재 authority, S11/O2/FIELD, 닫힌 과제·실행 권한 |
| E02 | `docs/00-project/roadmap.md` | 제품 전반 완료·활성·후속 단계 |
| E03 | `docs/rotary_oil_level_tracker_ssot_spec.md` §1.2, §11.6 | 목적, 1초 목표, 실제 다층 target, 후속 fixed-X 투영 기준 |
| E04 | `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` | 9개 현장 물리 구간·판정 범위 |
| E05 | `docs/60-evidence/s11/2026-10-11-program-intake.md` | P1 통합, 10/10·10/11 원본 명세 관계, gate 비완화 |
| E06 | `docs/50-diagnostics/s11/2026-10-11-p2-shared-support.md` 및 하위 `preflight.json`, `readout.json`, `verify.py` | 0/6, 0/3, 공통 support, dominated pair 및 종료 |
| E07 | `docs/50-diagnostics/s11/2026-10-11-foam-upper-position-review.md`, `...-comparison.py`, `...-position-reply.json` | f1620/X595/812–816, raw→component→candidate→episode 원인 |
| E08 | `docs/50-diagnostics/s11/2026-10-10-water-foam-representation.md` | A의 dark support, unclear lower |
| E09 | `docs/50-diagnostics/s11/2026-10-10-abc-source-interval-comparison.md` | water ABC interval과 기존 경계 결합 |
| E10 | `docs/60-evidence/s11/2026-10-08-episode-source-review-validation.md` | 채택된 report/episode 원본 맥락, detector와 효능 구분 |
| E11 | `docs/30-validation/s11-interface-observability-witness-validation.md` 336–415, 526–552 | operating point·holdout·1초 cadence·O2/O3/field |
| E12 | `docs/20-architecture/s11-interface-observability-witness-architecture.md` | scalar 기준, O1/O2, 지역/시간/reference/representation 계약 |
| E13 | `docs/50-diagnostics/s11/2026-10-09-local-xy-sequence-causality.md` | 후보·소유권·Foam current/final 구분 |
| E14 | `sample/README.md` 및 `2026-10-09-public-scene-controls.md`, `2026-10-10-water-first-source-qualification.md` | 영상별 개발 범위·원본 판독 한계 |
| E15 | `docs/60-evidence/s11/s11-o2-identity-profile-windows-run-001.md`, `s11-o2-w4-r3-existing-evidence-feasibility.md` | 전달된 현장 판별 실패와 닫힌 자료 조사 |
| E16 | `src/oil_tracker/adapters/vision/foam_front_detector.py` 785–823, 826–1016 | component extreme으로 raw front를 정하는 실제 코드 |
| E17 | Git object `e5d4a0430ea69beab59736396a2817c09b5efd69:docs/60-evidence/s11/2026-10-08-cellular-selector-closeout.md` | 종료된 cellular/selector 변경, 표면 rank와 authority 손실 구분 |
| E18 | `docs/20-architecture/s11-current-detector-logic-map.md` | 현재 R22 owner·projection·series 독립성 |
| E19 | `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` | F01–F10 및 반복 금지 메커니즘 |
| E20 | `docs/00-project/execution-policy.md`, `.agents/skills/s11-detector-change/SKILL.md`, `docs/30-validation/s11-detector-change-governance.md` | 실행·보안·이력·검사 범위 |

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PROPOSAL`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: current R22 ownership/projection map; P1 integrated centre alternatives; closed P2-S1 shared-support reference comparison; closed cellular selector and Local XY sequence interventions; region/profile/temporal correspondence limits; current source-qualified Foam upper and water support-stage evidence; canonical Windows reviewed story.
- Prior mechanisms rejected: threshold/reference/transform retuning of P2-S1; global component top/bottom substitution; white-only or blanket union support as physical identity; motion-only bootstrap; cost-first or selector-only recovery; phase relaxation before current physical evidence; report interpolation/carry; routine reuse of retired sample3; repeated closed physical questions.
- Preserved contracts: same-frame selected candidate/sequence/CSV equality; independent Oil/Foam validity; typed unavailable/ambiguity; coordinate-free FULL/EMPTY; bounded physical handoff; original truth and source scope; O2/O3/field gates; current report ownership; Windows private-media boundary.
- Difference from prior failures: this program separates raw representation, boundary role, fixed-X scalar, temporal ownership and episode acceptance, and requires one frozen role comparison to demonstrate useful target retention and opposing controls before runtime integration. No failed appearance score is promoted by presentation or a new authority shortcut.
- Logic-map impact: NONE — this audit and proposed work specification introduce no production consumer or runtime owner change; implementation-specific map updates remain required at the actual integration step.
- Failure-registry impact: NONE — the confirmed cases are covered by existing representation, identity, component-front, provenance and tuning failures; this document claims no new field mechanism or accepted repair.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: in the saved scoped/FULL sample4 evidence, the source-qualified f1620 front survives at Y813 but component-to-front reduction chooses internal Y833 before episode processing; water A loses compatible upper support at the lightness/whiteness predicate. P2-S1 loses required current support for two positives and cannot separate a dominated positive/negative pair with its fixed cost/margin family. Existing Oil physical association and Windows efficacy are not newly solved by this audit.
- Logic-map impact: NONE — only ignored audit outputs and external deliverables were created; production, Recipe, truth and accepted owner boundaries are unchanged.
- Failure-registry impact: NONE — fresh checks verify existing evidence and clarify program consequences without establishing a new accepted detector mechanism.
