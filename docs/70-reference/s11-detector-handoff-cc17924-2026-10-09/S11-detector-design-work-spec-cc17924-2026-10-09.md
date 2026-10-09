# S11 Detector 집중 설계·작업 명세서

**기준:** `teeeeooo/oil_level_tracker` / `main` / `cc179244c89ea59bd097fa165ea493942629e23e`  
**작성일:** 2026-10-09  
**문서 상태:** 현재 체크아웃을 검토하고 오프라인 실험을 수행한 후 작성한 **후속 구현 제안**. S11 완료·O2 수용·runtime 변경 승인을 뜻하지 않는다.  
**작업 위치:** `/Users/sunjaekim/Developer/oil_level_tracker`  
**이번 실행 자료:** `sample/output/s11-design-audit-cc17924-20261009-001/`

> 목적은 detector의 프레임별 검출률 100%가 아니다. 기존 report를 보고 사용자가 계면/Oil과 Foam의 상승·하강·출현·소멸·재등장 맥락을 이해할 수 있게 하는 것이다. 단발 누락·오검지는 이 맥락을 바꾸지 않는 범위에서 잔여 결함으로 관리한다. 반면 잘못된 물체를 오래 따라가거나 주요 반전·급격한 재유입을 지워 버리는 오류는 우선 수정한다.

---

## 1. 결론과 이번에 확정할 범위

**전체 detector·report를 다시 만드는 대신, 현재 영상의 경계 후보에서 역할을 판별하는 앞단을 좁게 교체·검증한다.** 우선순위는 `FRAME-EVIDENCE → OIL-CANDIDATE / FOAM-CANDIDATE`에 있다. 현재 물리적 경계인지 확인되지 않은 후보를 살리려고 tracklet·phase·episode gate부터 낮추지 않는다.

기존의 고정 Glass 중앙 X 측정 결정은 유지한다. 인식은 주변 영상까지 사용하되 숫자는 선택된 **현재 경계가 중앙을 실제로 지나는 위치**에서만 읽는다. 이 원칙 자체는 경계를 인식하는 알고리즘이 아니다.

이번에 실행한 **참조 양쪽 seed + 현재 영상 minimax 영역 분할**은 정식 후보로 채택하지 않는다. 후속 저장 배열 비교에서 기존 밝기-support 경계에 좌표를 맞추도록 요구하는 조건이 추가 누락을 만든다는 사실은 확인했지만, 그 조건을 제거해도 역할 혼동과 분절이 남았다. 따라서 다음 실험은 영역 확장이나 LK 생존점 구제가 아니라 **현재 관측 경계 자체에서 참조 양쪽 모습을 재측정하는 방식**으로 한정한다.

이번 제안의 범위는 아래와 같다.

| 구분 | 결정 |
|---|---|
| 현재 report와 source-context/episode-review | 재사용. 새로운 report UI 작업으로 우회하지 않는다. |
| 고정 중앙 측정 | 선택 완료. 다시 질문하거나 다른 X의 median으로 대체하지 않는다. |
| Local XY 제외 | 시험 완료·비채택 상태와 OFF 유지. ‘아직 시험하지 않았다’는 이전 문구는 현재 상태가 아니다. |
| 고정 패턴 matching, LK 생존/최근접 edge | 단독 물리적 역할 판별기로 재사용하지 않는다. |
| 이번 minimax 분할 및 좌표 비교 | 계산과 관측 표현 검증 자료로 보존. physical selector로 승격하지 않는다. |
| 다음 설계 | 현재 경계 위치에서 직접 역할 비교. 아래 D2-A/D2-B로 한 번의 제한된 challenger를 만든다. |
| O3/O4/Windows field qualification | 선행 gate 충족 후 별도 작업. 이번 문서로 통과 처리하지 않는다. |

**성능 개선이 입증된 production detector를 이번에 만들었다고 주장하지 않는다.** 완료한 것은 현행 상태 조사, 영상·증거 검토, 새 후보의 제한된 실행 및 반증, 계산 검증, 후속 구현 계약 작성이다.

## 2. 현재 S11 상태와 증거의 우선순위

### 2.1 현재 owner에서 확인한 상태

`docs/00-project/work-plan.md` 상단과 work-item ledger가 현재 상태의 유일한 owner다. 이번 조사 기준으로 다음과 같다. [E01]

| 항목 | 현재 상태 | 해석 |
|---|---|---|
| S11 | ACTIVE | 완료 단계가 아니다. |
| 수용 baseline | R22 behavior + R22-3/O1 diagnostics | 진단 구현과 detector 효과를 구분한다. |
| O1 | locally ACCEPTED | 관측 추출·진단을 재사용할 수 있다는 의미다. |
| W4 / O2 | OPEN | 후보 identity challenger 및 O2 acceptance 미완료다. |
| 최근 사용자 Windows 판정 | FIELD FAIL | 이번 Mac 실험으로 변경되지 않는다. |
| Local XY WP1–WP5 | 구현·검증 후 CLOSED WITHOUT PROMOTION | opt-in 코드가 존재해도 기본 동작은 OFF다. |
| Report adjuncts | main-adopted | 이해도와 수치 identity의 독립적인 검증까지 완료됐다는 뜻은 아니다. |
| 다음 전이 | bounded current-boundary/side-role proposal | 현재 측정 위치를 고르는 질문은 끝났고, 현재 물리적 경계를 고르는 문제만 남았다. |

과거 MD에 남은 `pending`, `아직 시험하지 않음`, 오래된 R18/R20 상태는 최신 owner를 덮어쓰지 않는다. 과거 Windows exact Y 추정도 최신 사용자 reviewed truth를 덮어쓰지 않는다.

### 2.2 이번에 직접 수행한 확인

| 작업 | 이번 실행 결과 | 주장하지 않는 것 |
|---|---|---|
| Git 기준 확인 | 시작 시 `main@cc17924`, 추적 작업 트리 clean | 원격 Windows 환경 상태 확인은 아님 |
| 마지막 checkpoint 무결성 | 기존 413개 경로 + 추적 중인 그림 2개, **415개 SHA-256 일치**, 불일치 0 | detector 재실행이나 정확도 검증은 아님 |
| production source 확인 | 위 검증에 **221개 Python source pin** 포함 | 전체 시스템 성능 PASS는 아님 |
| 원본 재디코드 | 기존 4개 Mac 영상에서 **18개 선택 프레임**, 요청/반환 frame index 확인 | 4개 영상 전체 프레임 전수 육안 판독은 아님 |
| 추가 샘플 검토 | water/beer/milk의 기존 9개 native-frame 자료 및 기존 판단 재사용 | 새 독립 holdout이나 신규 정답 작성은 아님 |
| 새 오프라인 실험 | 167개 고유 raster, 198개 plan/frame query | 198개의 독립 영상·독립 정확도 표본은 아님 |
| 별도 좌표 ablation | 같은 198개 저장 결과의 geometry query만 변경 | seed·분할 모델·threshold 재조정은 아님 |
| 독립 계산 검증 | 구성 제어 9개. 이 중 하나에서 32개 작은 graph를 별도 threshold-reachability oracle과 대조 | 물리적 Oil/Foam 정답률은 아님 |
| 저장 결과 검증 | 첫 실험 198개, geometry ablation 198개 결과의 중앙 face 선택을 각각 직접 대조 | 두 검증을 396개 독립 영상 성공으로 합산하지 않음 |
| 기존 집중 테스트 | **84 passed in 9.06 s** | 전체 suite 또는 Windows field PASS는 아님 |

검증 스크립트의 최초 두 실행에는 `portable_figures` manifest의 상대 경로와 객체형 hash 해석 오류가 있었다. 이 두 항목만 수정해 전체 검증을 통과했다. 실험 코드·입력·seed·수치 결과를 고친 것은 아니다. 상세 이력은 `verification-correction.txt`에 보존했다.

### 2.3 이번에 다시 실행하지 않은 것

production 전체 분석, Windows detector/benchmark, 기존에 종료한 D1/D2 조사, template·Local XY·LK 실험의 parameter sweep, UI/Recipe 변경, `.oiltruth` 수정은 하지 않았다. 변경하지 않은 production baseline을 다시 계산해 새 효과로 포장하지 않는다.

## 3. 영상과 검토 증거에서 본 실제 문제

### 3.1 샘플별 용도

| 자료 | 이번 확인 범위 | 설계에서 보호할 내용 |
|---|---|---|
| `base_sample_1` | f0/150/151/433 원본 ROI | 약한 경계 위로 강한 설명용 수평선이 등장한다. 강한 수평 edge를 Oil로 간주하지 않는다. |
| `sample2` | f0/30/60, 기존 0–2 s 고정 geometry 범위 | 형광등 반사·미세 기포가 있는 정적 장면. 움직임이 작다는 이유로 실제 경계를 무조건 거부하지 않는다. |
| `sample3` | f930/1800/2550/3090, 기존 고정 geometry 범위 | fill/agitation/drain와 blur/reframing 문맥을 분리한다. 재등장 공백을 report smoothing으로 감추지 않는다. |
| `sample4` | f420/480/1275/1320/1560/1620/1680 및 저장 연속 raster | 작은 ROI에서 유리·Foam 내부 질감·실제 경계가 겹친다. 52 s selection과 54–56 s admission 문제를 같은 현상으로 뭉치지 않는다. |
| `sample5` water | 기존 empty/inclined/settled 3개 원본 자료 | 사용자가 수면에 가깝다고 판단한 경사 형태를 수평성·완전 연결성 조건으로 제거하지 않는다. |
| `sample6` beer | 기존 empty/forming/layer 3개 자료 | 앞/뒤로 보이는 두 arc는 같은 얇은 Foam 층이라는 사용자 판단을 보존한다. 두 높이를 Oil/Foam 각각 또는 두께로 자동 해석하지 않는다. |
| `sample7` milk | 기존 empty/pouring/settled 3개 자료 | 흰 bulk liquid를 Foam으로 보지 않는다. 아래 Foam–milk 경계의 불명확함과 위쪽 front의 가용성을 분리한다. |

첫 4개 영상의 Recipe·truth와 public 3개 영상의 진단 crop은 동등한 calibration이 아니다. public crop center X950/1350/1120을 production Glass center로 취급하지 않는다. 기존 모든 노출 자료는 개발/회귀 자료이며 untouched holdout으로 이름을 바꾸지 않는다. [E04, E11]

18개 재디코드 프레임의 영상·Recipe hash, 요청/반환 frame, 명목 시간과 decoder timestamp, crop 좌표 및 decoded-pixel hash는 `visual-review.json`에 남겼다. 순간 화면에서 추가로 판단한 것은 agent의 정성적 관찰이지 사용자 정답이 아니다.

### 3.2 반복하지 않을 원인 분석

**Local XY 실패는 국소 제외라는 개념 전체가 불가능하다는 뜻은 아니다.** 현재 시험한 설정에서는 downstream ownership이 바뀌고, 56 s에 유리 테두리 후보를 선택하는 문제를 해결하지 못했다. 52 s에는 target-vicinity 후보가 admitted/publishable 상태인데 선택되지 않았고, 54–56 s에는 target-vicinity 후보의 tracklet admission 자체가 실패했다. 이것을 하나의 threshold 부족으로 설명하면 안 된다. [E06, E07]

**54–56 s에 표시된 일부 cyan Foam 후보의 최종 거부는 실제 front를 놓친 증거가 아니다.** 사용자가 해당 세 특징을 Foam 내부 질감으로 판단했다. 이 후보들을 살리려고 formation 조건을 낮추는 것은 목표와 반대다. 별도로 실제 upper boundary가 보인다는 판단은 보존하되, 그 위치나 후보 ID까지 확정됐다고 확장하지 않는다. [E07, E08]

**고정 패턴과 LK는 역할 판별을 대신하지 못했다.** 이전 고정 패턴의 유일한 최적 일치가 유리 아래로 이동했고, LK는 22/22·21/21 point ID를 유지하면서 일부 영역에서 경계를 벗어났다. 다만 45 s 오른쪽 그룹이 Foam–Oil 경계에 남아 보인다는 사용자 답변은 부분적 대응으로 보존한다. ‘모두 실패’, ‘정확한 생존점 whitelist’ 어느 쪽으로도 바꾸지 않는다. [E09]

**기존 경계 보존 구현은 유용하지만 역할 판별과 다르다.** saved support는 유리의 둘레도 정확히 그린다. lossless pixel/face 수, 긴 곡선, 가까운 edge, label ID는 ‘무엇의 경계인가’를 답하지 않는다. 중앙 X 읽기의 176-raster/792-crossing 검증도 같은 한계를 가진다. [E02, E10]

## 4. 이번 실행 실험과 후속 ablation

### 4.1 H0: reference-paired-minimax-partition-v1

가설은 ‘이미 지정된 역할 참조의 위/아래 모습을 이용해 현재 영상에서 두 영역을 다시 나누면, 점을 그대로 따라가는 것보다 현재 경계를 찾는 데 도움이 되는가’였다.

입력과 연산을 실행 전 고정했다.

1. 기존 Foam f420의 22개 대략적 점, Oil f1275의 21개 힌트, rim f450의 한 점을 그대로 사용했다. 초기 프레임은 continuation 실적에서 제외했다.
2. 기존 reference stencil과 동일한 ±2 row를 사용했다. 현재 측정 위치는 기존 native-rate LK 위치이며, 각 위/아래 pixel이 초기 같은 쪽 색상에 반대쪽보다 엄격히 가까울 때에만 seed로 남겼다. 수작업 생존점 선택은 하지 않았다.
3. 현재 visible BGR raster의 4-neighbour graph에서 edge cost를 `max(abs(BGR neighbour difference))`로 정했다. 각 seed class까지의 minimum-bottleneck cost를 계산했다. 두 cost가 같거나 지원이 없으면 UNKNOWN이다. 별도 거리 tie-break나 morphology는 없다.
4. 처음에는 X595에서 **기존 brightness-support face**와 일치하면서 위 pixel=A, 아래 pixel=B인 face만 후보로 남겼다. 현재 결과가 하나여도 `PROVISIONAL_APPEARANCE_ONLY`이며 physical decision은 `NOT_EVALUATED`다.

이는 `cv.watershed`나 random-walker 구현을 호출한 것이 아니다. marker 기반 분할의 개념을 참고한 작은 정수 graph 실험이다. OpenCV 공식 설명도 marker의 의미를 입력으로 지정하는 방식이며, 알고리즘이 Oil/Foam 의미를 스스로 제공한다는 근거는 아니다. [P01]

### 4.2 G1: 같은 분할의 현재 face를 직접 읽는 좌표 ablation

원본/분할 overlay를 검토하자 넓은 두 영역은 나뉘는데 기존 brightness face 조건에서 값이 사라지는 경우가 있었다. 따라서 seed·모델·mask·입력은 전혀 바꾸지 않고 **이미 저장된 분할 결과**만 다시 읽었다.

기존 `measure_boundary_faces`를 그대로 호출해 A–B 현재 face를 열거하고 X595 교차 Y를 읽었다. `A → UNKNOWN → B`를 연결하지 않았고, 다른 X나 과거 Y로 보간하지 않았다. 이 비교는 모델 개선이 아니라 **후보 geometry를 어느 표현에서 읽느냐**의 차이를 분리한다.

| 계획 | 초기 제외 프레임 | H0: 기존 support face에 맞춘 단일 후보 | G1: 현재 partition face의 단일 후보 | G1 단일 후보 없음 |
|---|---:|---:|---:|---:|
| Oil, f1276–1350 | 75 | 3 | 15 | 60 |
| Foam, f421–510 | 90 | 21 | 50 | 40 |
| Rim opposition, f451–480 | 30 | 0 | 0 | 30 |

이 표의 수치는 **정확도·물리적 검출 recall이 아니라 후보 가용성**이다. 같은 native 영상의 인접 프레임이다. rim의 한 점은 양성 참조들과 정보량·위치가 맞춰진 대조군도 아니다. rim에서 0이 나온 결과를 false-positive 0%라고 해석할 수 없다.

G1의 가장 긴 연속 단일 후보 구간은 Oil 4개 native frame, Foam 10개 native frame이었다. 실제 report sampling cadence와 동일한 평가가 아니므로 이를 보고서 연속성 점수로 환산하지 않는다. H0/G1은 기존 LK의 native-frame 위치를 재사용했으므로, production의 더 낮은 sampling cadence에서 같은 결과가 나온다는 증거도 없다.

### 4.3 결과 판정

좌표 ablation으로 확인된 것은 **이전 brightness-support 표현과의 정확한 일치를 강제하면 현재 분할이 가진 geometry를 추가로 잃을 수 있다**는 점이다. 새 알고리즘의 경계를 예전 Foam mask의 경계에 억지로 맞추는 연결 방식은 채택하지 않는다.

그러나 G1도 physical selector로는 채택하지 않는다. 특히 Oil f1348에서 X595/Y825.5를 제안했다. 해당 원본의 표시 위치는 agent 검토상 밝은 Foam 내부로 보이며, 실제 하부 경계보다 위의 특징으로 이동한 것으로 판단된다. 이는 신규 사용자 point truth가 아니라 **별도로 표시한 agent-observed wrong-region 의심 사례**다. f1350에서는 중앙 후보가 없다. 45 s 오른쪽 LK 그룹에 대한 기존 사용자 답변과는 대상·범위가 다르므로 그 판단을 번복하지 않는다.

따라서 결과는 다음과 같이 분리한다.

- **확인:** 순수 좌표 query에서 발생한 추가 누락; 정확한 현재 geometry provenance를 보존할 필요.
- **확인:** 산술·mask·동점·좌표 변환의 동작과 source 무변경.
- **미해결:** 현재 physical role의 신뢰성, reference-side 순도, late drift, 실제 report 개선.
- **결정:** H0 및 G1 조합은 비채택. 알고리즘·seed·window·distance를 retune해 구제하지 않는다. 현재 geometry를 독립적으로 보존한다는 원칙만 다음 설계에 반영한다.

## 5. 개선 목표: 프레임 수가 아니라 사건과 움직임

### 5.1 결함 심각도

| 우선순위 | 현상 | 허용·처리 기준 |
|---|---|---|
| P0 — 맥락 전도 | 실제 하강이 상승처럼 보임, 급격한 refill이 통째로 사라짐, Foam이 없는데 주요 episode 생성 | 해당 구간의 개선/비회귀를 명시적으로 입증해야 한다. 다른 영상의 숫자 증가로 상쇄하지 않는다. |
| P1 — 긴 오소유·긴 누락 | 유리·잔류물로 owner 이동, 실제 layered interval 대부분 누락, 재등장 이후 긴 공백 | 잘못된 run 및 가장 긴 missing run을 줄이는 것을 우선한다. |
| P2 — 국소 잔여 결함 | 단발 miss, 짧은 잘못된 후보, 작은 jitter | 주요 사건·방향·extrema 해석이 유지되면 공개된 잔여 결함으로 허용 가능하다. |

이것은 새 detector gate가 아니라 작업 우선순위·검토 rubric이다. ‘2초 이하는 전부 허용’ 같은 보편 숫자는 쓰지 않는다. 약 1.6초의 rapid-refill을 통째로 잃는 것은 짧아도 P0다. 반대로 장시간 완만한 하강의 한 프레임 누락은 P2일 수 있다.

### 5.2 매번 제출할 고정 비교 항목

기존 report와 같은 시간축에서 Oil/Foam을 각각 다음으로 평가한다.

- 출현·소멸, 상승/하강, 반전, 재등장, layered interval의 해석이 원본/기존 reviewed truth와 일치하는지.
- 기대 가시구간 내 실제 관측 support, longest missing run, longest wrong-owner run, 잘못된 주요 extrema/episode.
- baseline 대비 개선된 주요 구간, 새로 악화된 구간, 해석 불가능한 구간을 각각 표시.
- 정확한 scalar truth가 있는 범위에서만 오차를 계산하고, 없는 곳은 `NOT_MEASURED`로 남김.

모든 raw frame의 정답률이나 전체 coverage 하나로 합격시키지 않는다. 전부 UNKNOWN을 출력한 방법도 성공이 아니다. 반면 하나의 고립된 P2 때문에 다른 주요 구간의 실사용 개선을 무조건 폐기하지도 않는다. O2/field gate는 기존 owner의 절차대로 별도로 판단한다.

## 6. 다음 challenger: 현재 관측 경계에서의 참조 조건부 역할 비교

**제안 이름:** `current-boundary-reference-comparison-v1` — 이하 CBR-1. 새 milestone이나 수용된 detector 버전이 아니다. **아래 설계는 이번에 구현·성능 검증하지 않았다.**

### 6.1 H0와의 차이

H0는 ‘이전 점이 이동한 곳’에서 두 seed를 정한 뒤 전체 region을 확장했다. seed가 내부 질감으로 이동해도 분할은 수치적으로 정상 실행됐다.

CBR-1은 순서를 바꾼다.

```text
현재 원본 pixels와 실제 관측 edge/face
    → 현재 boundary 후보와 해당 후보의 양쪽 pixels
    → 역할이 지정된 초기 참조와의 비교 + 구조/내부질감 경쟁 설명
    → 후보별 역할 근거 또는 UNRESOLVED
    → 그 후보의 현재 Xcenter 교차 Y
    → [검증·수용 전까지 diagnostic only]
```

**후보의 측정 위치를 LK·과거 Y로 정하지 않는다.** 역할 비교는 언제나 현재 관측 geometry 위에서 수행한다. 현재 candidate가 없는 자리에 reference 모양을 그려 넣지 않는다. 기존 completed-window owner를 우회하는 tracking engine도 만들지 않는다.

### 6.2 입력 계약

| 입력 | 사용 방법 | 금지 |
|---|---|---|
| 현재 원본 crop, effective/glare availability, 원점 | 기존 preprocessing/geometry owner 재사용 | 정규화·mask를 몰래 변경해 새 support를 얻기 |
| 현재 edge/face/fragment 대안 | 관측된 실제 pixel geometry만 보존 | hole fill, 가장 가까운 경계로 snapping, 강제 수평화 |
| 선택적 Oil/Foam positive reference | 각각 독립적인 source-bound 역할 예시. 이미 허용된 기존 참조를 개발 입력으로 명시 | `.oiltruth` 자동 유입, mandatory setup, 매 프레임 사용자 보정 |
| 기존 negative structure reference | 유효한 source/geometry/settings 범위에서 경쟁 설명으로 사용 | negative 미일치를 ‘실제 유체’ 증명으로 사용 |
| 시간·frame·Glass ID | join/provenance 전용 | 영상명·시각·특정 Y를 inference 분기로 사용 |

대략적인 경계 참조는 pure material mask가 아니다. 초기 참조의 양쪽이 실제로 구분되지 않거나 여러 boundary가 섞인 경우 해당 reference comparison은 `UNAVAILABLE`이다. 신규 측정 입력이 실제로 필요하다는 것이 확인되기 전에는 정확한 좌표·조밀한 라벨을 사용자에게 요구하지 않는다.

### 6.3 최초 prototype의 고정 연산

D2-A에서 다음 연산을 하나의 preflight로 고정하고 구현한다. 실행 후 결과에 맞춰 stencil·reference·순서를 바꾸지 않는다.

1. **현재 후보 geometry:** 기존 observed-edge/지원 face 표현을 사용한다. 서로 다른 geometry basis는 구분한다. Oil 후보를 accepted Foam mask 또는 예전 brightness-support face와의 일치 여부로 제한하지 않는다. 이미 존재하는 bounds를 넘으면 truncated/UNAVAILABLE을 기록한다.
2. **현재 위치에서 양쪽 측정:** 기존 reference stencil/지원 폭을 재사용한다. 각 실제 fragment의 source X/Y 및 위·아래 유효 pixels를 보존한다. 관측되지 않은 fragment 사이를 연결하거나 보간하지 않는다. 폭·좌표·지원이 다른 비교를 하나로 섞지 않는다.
3. **같은 pixels에서 경쟁 설명:** 역할 참조의 A/B, 뒤바뀐 B/A, A/A 또는 B/B의 같은-side 설명, 사용 가능한 structure-reference 설명을 비교한다. 보존된 native BGR의 같은 지지집합에서 L1 residual을 계산한다. gray-only 비교는 동일 support의 사전 고정 ablation으로만 허용한다. 자유 gain/offset fitting, reference 자동 갱신, 별도 학습은 하지 않는다.
4. **모델 계산 예:** 유효 대응점 집합 S에서 `L_AB = mean_S(|current_A-ref_A| + |current_B-ref_B|)`. B/A, A/A, B/B 및 유효 structure 설명도 동일한 S·동일 가중치로 계산한다. 이것은 appearance loss이며 물리적 확률이 아니다. S가 다르면 수치를 직접 순위 비교하지 않는다.
5. **최초 shadow 판단:** 현재 중앙 교차가 있고, A/B 설명이 같은 pixels의 swapped/same-side 설명보다 엄격히 우세한 후보를 provisional role hypothesis로 남긴다. 실제로 측정된 구조 경쟁 설명이 동등하거나 더 우세하면 UNRESOLVED다. 여러 현재 후보가 남으면 최초 v1에서는 하나를 임의로 고르지 않고 UNRESOLVED로 남긴다. 측정되지 않은 opposition은 ‘없음’이나 favorable vote로 바꾸지 않는다.
6. **물리적 역할/승격 분리:** 위 수치 우세는 단독 physical identity certificate가 아니다. paired controls와 실제 영상 비교에서 유효한 operating point가 확인되기 전에는 typed positive authority를 주지 않는다. 같은 관측으로 구별할 수 없는 대안은 그대로 unresolved로 평가한다.
7. **고정 중앙 숫자:** 후속 역할/eligibility가 검증된 경우에만 선택 후보의 실제 중앙 교차값을 사용한다. face면 half-pixel, 다른 관측 표현이면 그 표현의 좌표 정의를 명시한다. 모양 fitting에서 생성한 숫자나 다른 X의 값은 쓸 수 없다.

이 방식도 성공이 보장되지 않는다. 특히 조명 변화·참조의 양쪽 혼합·겹친 구조에서 대거 abstain하거나 잘못된 feature를 선택할 수 있다. 차이는 단순한 threshold 완화가 아니라 **수치적인 역할 근거를 현재 선택 후보의 위치에 결박한다는 점**이다. 이것이 f1348류의 drift를 줄이는지, 동시에 실제 경계를 충분히 남기는지를 다음 한 번의 실험으로 확인한다.

### 6.4 최소 구현 위치와 데이터

첫 구현은 production이 아니라 기존 `tests/diagnostics/s11_boundary_temporal_probe.py`의 좁은 함수 확장으로 한다. `s11_foam_support_geometry.measure_boundary_faces`와 기존 raster/preprocess loader를 재사용하고 별도 segmentation/추적 framework는 만들지 않는다.

함수 이름은 구현 시 확정하되 책임은 `현재 후보 geometry → source-bound reference 비교 결과` 하나다. 최소 출력은 다음과 같다.

```text
frame / role / candidate-geometry identity / geometry_basis
source_origin / fixed_center_x / all observed center crossings
reference identity and declared role
exact measured side support, masks, missingness and residuals
measured / contradicted / not_measured opposing explanations
provisional hypothesis or unresolved reason
same-frame provisional_y, physical_decision scope, no public consumer
```

여러 실제 액체 계면이 있는 장면에서는 현행 product target을 보존한다. 임의의 실제 내부 계면을 Oil 목표로 바꾸지 않으며 Foam 역할은 별도다.

새 formal truth schema나 Recipe field를 만들지 않는다. W3 adapter는 기존 identity·target·local path·scalar의 구분을 유지한다. 현행 W3의 original candidate Y를 새 center Y로 덮어쓰지 않는다.

## 7. 작업 명세: D2–D6 안에서 실행

별도 live roadmap을 만들지 않고 기존 D/W/O 라벨을 그대로 세분한다. 아래는 **제안된 작업 순서**이며 `work-plan.md`의 현재 gate를 자동 변경하지 않는다.

| 작업 | 입력 / 구현 범위 | 산출물 및 완료 조건 | 중단·보호 조건 |
|---|---|---|---|
| **D2-A: 현재 경계에서 reference 비교** | CBR-1 preflight; 기존 reference·native pixels·diagnostic helper | 최초 연산·UNKNOWN·bounds를 구현하고 positive/negative/unresolved 구성 제어 통과. 향후 파일: `test_s11_current_boundary_reference.py` 등 좁은 unit test | 참조를 학습 데이터로 확장하거나 seed를 매 프레임 수작업 수정해야 하면 이 variant 종료 |
| **D2-B: geometry 독립성** | 기존 source geometry/face/edge owner | 신규 후보를 옛 Foam support에 맞추지 않음. 고정 center·mask·다중 교차·좌표 basis별 provenance 검증 | unobserved gap을 채우거나 side median으로 값을 만들면 불합격 |
| **D3-1: 첫 실제 영상 비교** | 기존 167-raster/198-query plan 전체, 초기 제외, 현행 분석 cadence도 별도 명시 | 후보→역할→중앙 가용성→provisional 출력의 funnel과 시간축 sheet. f1348 같은 wrong-region 사례 및 기존 true-front controls 포함 | 한두 표시 프레임만 좋아졌으면 계속 확장하지 않음. 누락을 줄인 대가로 wrong owner가 늘면 승격 보류 |
| **D3-2: 기존 회귀 범위** | 4개 기존 Mac 영상의 고정 window, user truth/상태 근거, public 3종 control | 원래 sampling·Recipe 유지. 기존 scalar와 center scalar는 분리. source grouping/exposure·누락 분모 포함 | public 3종을 calibration/holdout으로 오인하거나 정확한 Y를 임의 생성하면 중단 |
| **D5: Foam raw-front 비교** | 같은 경계/참조 비교 원리, 독립 Foam 역할, 기존 real-front/rim/internal-texture controls | `component appearance`와 `physical front`가 다른 경우를 구분. 실제 front의 시간 맥락을 개선하는 결과 제출 | 세 내부-texture 후보를 회복 대상으로 삼거나 Oil gate를 이용해 Foam을 승인하지 않음 |
| **O2 / D3 Windows shadow** | 로컬 challenger와 operating point 고정 후, 기존 secure 절차 | 실행 필요성이 생긴 시점에 로컬 Windows 절차 준비. exact source/runtime·target-specific 판단·UNKNOWN/coverage·opposition을 검토 | 지금 즉시 Windows 파일 요청·반출·재라벨링하지 않음. shadow는 field qualification이 아님 |
| **D4a / W5 / O3: 제한된 통합** | O2 및 별도 통합 계약 충족 후 | 검증된 현재 evidence가 existing candidate/authority owner로 들어가는 단일 경로. debug NONE/BASIC/FULL, provenance·기본 OFF 비교 | source family privilege, unselected Foam/Oil의 상대 series veto, 강제 anchor 금지 |
| **D4b / W6 / O4: association·phase** | 실제 identity가 입증된 출력에서만 남는 lifecycle 손실 | confirmed interface의 first harmful stage가 association/phase일 때 그 owner만 수정. FULL/EMPTY와 owner handoff controls | 현재 미확인 후보를 살리기 위해 confirmation·ambiguity·phase gate부터 완화하지 않음 |
| **D6 / W7 / O5: 최종 검증** | 통합된 exact runtime, 현재 report, canonical Windows 9구간 | 사건·방향·layering·wrong/missing runs, exact provenance와 target throughput을 모두 보고 | Mac PASS·단위 테스트·숫자 증가로 FIELD FAIL을 바꾸지 않음 |

### 7.1 비교 범위와 탐색 예산

최초 CBR-1은 하나의 고정 연산으로 실시한다. 구조적으로 다른 ablation은 사전에 지정한 한 개까지 허용하되, 여러 seed/window/threshold 조합을 훑지 않는다. 이 예산은 detector runtime 제한이 아니라 연구 진행 규칙이다.

첫 비교에서 원본·현재 후보·역할 근거·중앙 결과를 같은 sheet로 제출한다. 효과가 없으면 원인을 `참조 입력 / 현재 후보 없음 / 역할 비교 / 중앙 unavailable / 통합 이후 gate`로 분리하고 해당 variant를 종료한다. 동일 메커니즘의 이름을 바꾸어 반복하지 않는다.

반대로 주요 실제 경계 구간을 유의미하게 회복하고 주요 negative control에서 맥락을 왜곡하지 않는다면, 모든 작은 edge case가 해결되기를 기다리지 않고 정해진 다음 검증 범위로 진행한다. 잔여 P2는 기록하고 분리한다. 이 진행 판단은 field 수용과 동일하지 않다.

### 7.2 새 기능보다 먼저 금지할 변경

새 UI·Recipe 설정, 강제 사용자 marker, detector 전체 교체, ML 도입, source/context 렌더러 추가, report interpolation, 기존 label 재정의, local mask 확대, generic threshold sweep은 이번 범위가 아니다. 성능 optimization도 실제 유용한 후보가 확인된 뒤 한다. native-rate LK를 runtime의 숨은 전제조건으로 추가하지 않는다.

## 8. 검증 계약과 자료 오염 방지

### 8.1 구성 제어

좌표/행동 무결성은 정확하게 검사한다. 고정 center에서 경사진 정지 경계, 중앙만 가림, side-only visible, 다중 교차, mask/crop censoring, no reference, 한 역할만 visible, independent Oil/Foam availability, source→ROI→px/mm 및 None 보존을 포함한다.

역할 비교는 실제 front, stationary real front, same-shape structure, 내부 texture, true boundary와 structure의 교차, refraction/warp, 반복 무늬·copied distractor, reference의 양쪽이 섞인 사례를 포함한다. 초기 frame의 정답을 이후 추적 성과로 세지 않는다. geometric adjacency나 동일 관측의 유일한 수치 minimum만으로 물리적 역할을 승인하지 않는다.

reference가 없는 자동 경로가 계속 작동하는지와, reference-assisted 경로의 차이가 무엇인지 분리한다. 기존 automatic detector와 ‘UNINITIALIZED인 작은 probe’를 비교해 assisted 성능 향상이라고 주장하지 않는다.

### 8.2 기존 정답과 새 center target

4개 `.oiltruth`에는 기존 bundle-bound 검토가 있다. 이것을 reference 입력으로 자동 전환하지 않는다. 정성적 경계 판단을 exact point label로 만들지 않는다. **기존 scalar Y annotation에는 고정 중앙 X 의미가 명시되지 않을 수 있으므로**, 새 center Y와 기존 Y의 차이를 그대로 MAE로 계산하지 않는다. 측정 위치 의미가 호환되는 범위만 사용하고 나머지는 원래 target의 회귀/정성 문맥 평가에 남긴다.

sample3의 unusable/focus-loss 판단을 valid로 바꾸지 않는다. milk의 아래 경계 unknown을 absent Foam으로 바꾸지 않는다. beer의 front/back projection을 다른 물질 계면 두 개로 분류하지 않는다. Windows alias의 operator same-video confirmation과 cryptographic source fingerprint도 구분한다.

### 8.3 runtime 통합 무결성

실제 통합 시에는 다음을 exact-match contract로 유지한다. 이는 100% detector 검출률 요구와 다르다.

```text
selected same-frame candidate Y == completed-sequence raw Y == CSV raw Y
current frame / timestamp / Glass identity preserved
Oil validity independent of Foam validity
no interpolation / carry / copied track coordinates
trace capture has no inference authority
report reads published observations; does not repair them
```

기본 동작 변경이 없는 단계에서는 baseline equality를 확인한다. 의도적인 후보 변경 후 모든 출력이 baseline과 같아야 한다고 요구하지는 않는다. 변경 영역·회귀 보호 영역·같은-frame provenance를 각각 평가한다.

## 9. Windows에서는 9개 사건을 빠짐없이 평가

아래 시간은 현행 사용자 reviewed truth의 대략적 전이 구간이다. 새로운 exact Y를 만들지 않는다. private 원본 영상·PNG·ZIP 반출을 요청하지 않는다. [E03]

| Segment ID | 원본 시간 | 사용자가 report에서 읽어야 하는 맥락 | 주된 오류 |
|---|---|---|---|
| `WS1-BASE-FULL-PREFIX` | 480–약 550 s | FULL, Oil/Foam 경계 없음 | 아래 구조물을 Oil로 표시 |
| `WS1-BASE-DRAIN` | 약 550–662 s | Oil 경계 출현 후 대체로 하강 | 긴 누락·유리/반사 추적 |
| `WS1-BASE-RAPID-REFILL` | 662–약 663.6 s | 빠른 상승 후 상단으로 소멸 | 사건 전체 누락, 다른 row로 갈아타기 |
| `WS1-BASE-FULL-SUFFIX` | 약 663.6–780 s | 계속 FULL, 경계 없음 | 725 s 부근 등을 false boundary로 표시 |
| `WS1-ACCUM-EMPTY` | 480–약 653 s | EMPTY, 두 경계 없음 | 고정 테두리/잔류물을 경계로 표시 |
| `WS1-ACCUM-ENTRY-SPLASH` | 약 653–672 s | Oil 유입·상승, Foam 아직 없음 | splash/벽 자국을 Oil owner 또는 Foam으로 승인 |
| `WS1-ACCUM-FOAM-LAYERED` | 약 672–680 s | 위 Foam와 아래 Oil 경계를 독립적으로 표시 | Foam top을 Oil로 선택, 한 series가 다른 것을 지움 |
| `WS1-ACCUM-POST-FOAM` | 약 680–700 s | Foam 소멸, Oil 경계는 유지 | 사라진 Foam을 계속 표시 |
| `WS1-ACCUM-DRAIN` | 약 700–780 s | Oil 반전·하강, 벽 자국과 분리 | residue로 owner 이동·거짓 Foam |

각 구간에 actual sampled frame/time coverage, final Oil/Foam numeric rows와 contiguous runs, Y 범위/방향, longest wrong/missing run, owner/phase transition, PASS/FAIL/NOT_EVALUATED를 남긴다. 각 구간의 결론은 report 및 필요한 원본 확인으로 설명한다. 옛 ‘52 real Foam rows’나 540/674 s의 폐기된 Y anchor를 목표로 쓰지 않는다.

## 10. 기존 문서와의 관계

| 기존 owner/자료 | 이번 문서의 관계 |
|---|---|
| `docs/00-project/work-plan.md`, `roadmap.md` | 현재 상태·단계 authority 유지. 이번 문서는 병렬 workplan이 아니다. |
| `s11-current-detector-logic-map.md` | 기존 owner 재사용. 추적·phase·projection 순서를 변경하지 않는다. |
| `s11-interface-observability-witness-architecture.md` | W1 target/aggregation 및 fixed-center 계약 구체화에 필요한 후속 후보 제안. 해당 계약을 교체하지 않는다. |
| `s11-interface-observability-witness-validation.md` | O2/O3/O4/O5 gate 그대로 적용. 새 focus 테스트는 대체 acceptance가 아니다. |
| October 8 initial/18885d2 specification | D2/D3/D5를 현재 head의 실제 실험 결과로 좁힌다. D4a/D4b/D6 gating은 보존한다. |
| October 9 Local XY package | 미시험 항목을 다시 제안하지 않는다. 종료된 variant의 이유를 보존한다. |
| fixed-center handoff | 그 checkpoint에서 재개한 조사·실험 및 다음 구현 제안이다. ‘실제 경계 판별 미완료’ 상태를 완료로 바꾸지 않는다. |
| Failure registry F02/F04/F06/F07/F09/F10 | 관측 표현·역할 전이·series 교차결합·오래된 provenance/threshold 실패와의 관계를 명시한다. |

## 11. 재현·실행 인계

이번에 사용한 파일은 기존 Mac 체크아웃의 다음 디렉터리에 있다.

```text
sample/output/s11-design-audit-cc17924-20261009-001/
  side_partition_probe.py
  partition-trial/preflight.json
  partition-trial/readout.json
  partition-trial/*-f*.npz
  verify_probe.py
  verification.json
  verification-correction.txt
  center_projection_ablation.py
  center-projection-ablation-preflight.json
  center-projection-ablation.json
  inspect_visuals.py
  visual-preflight.json
  visual-review.json
  *-source-review.png
  *-partition-review.png
  oil-late-ablation-review.png
  focused-tests.log
```

`sample/output/`와 MP4는 ignored 로컬 자료다. 새 clone에 자동으로 내려오지 않는다. 없는 자료를 재현 완료라고 가정하지 않는다. 최종 전달 파일은 문서·요약·계획이며 원본 영상이나 Windows 자료를 포함하지 않는다.

### 동일 체크아웃에서 결과 확인

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker

git rev-parse HEAD
git status --short

.venv/bin/python sample/output/s11-design-audit-cc17924-20261009-001/verify_probe.py

PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_s11_foam_support_geometry.py \
  tests/unit/test_s11_boundary_temporal_probe.py \
  tests/unit/test_oil_measurement_scope.py \
  tests/unit/test_artifact_reference_diagnostics.py
```

H0 재실행은 기존 출력 폴더를 덮어쓰지 않는다. 확인 목적 없이 종료한 detector 실험을 다시 실행하지 않는다. 꼭 재현해야 할 때만 같은 입력 hash를 확인하고 새로운 출력 경로를 지정한다.

```bash
.venv/bin/python sample/output/s11-design-audit-cc17924-20261009-001/side_partition_probe.py \
  --root /Users/sunjaekim/Developer/oil_level_tracker \
  --out /Users/sunjaekim/Developer/oil_level_tracker/sample/output/s11-h0-reproduction-NEW
```

`verify_probe.py`와 저장 배열 ablation runner의 경로는 이번 로컬 디렉터리에 고정된 조사용 스크립트다. 다른 기계에서 자동으로 동작하는 배포 CLI라고 취급하지 않는다. 정식 재사용이 필요할 때만 기존 diagnostic CLI의 경로·입력 계약에 맞춰 정리한다.

### 다음 작업 착수 메시지

```text
cc17924 기반 S11 detector 설계·작업 명세서를 현재 HEAD와 대조하여 intake해줘.
work-plan과 fixed-center target의 owner는 유지하고 D2-A/D2-B CBR-1만 먼저 구현해.
이번 H0 minimax 분할과 G1 geometry ablation은 비채택 결과이므로 retune하지 마.
현재 관측 경계 위치에서 역할 참조를 비교하고, 예전 LK 위치나 Foam mask에
숫자를 맞추지 마. 진단·역할·중앙 숫자·공식 출력을 분리해.
기존 198-query plan 전체와 opposing controls에서 실제 맥락 개선을 확인한 뒤
범위를 넓혀. 초기 frame 성공, coverage 증가, 전부 UNKNOWN을 개선으로 세지 마.
머신러닝·새 UI·mandatory reference·phase gate 완화는 하지 마.
새 Windows 실행이나 새 물리적 판단이 실제로 필요한 지점에서만 전달 절차를 준비해.
```

## 12. 근거 색인

문서 경로는 repository root 기준이다. 이번 숫자의 상세 근거는 로컬 실행 파일과 별도 `S11-execution-summary-cc17924-2026-10-09.json`을 참조한다.

| ID | 근거 |
|---|---|
| E01 | `docs/00-project/work-plan.md` — 상단 current gate/next transition, work-item ledger |
| E02 | `docs/60-evidence/s11/2026-10-09-fixed-center-handoff.md`; `docs/50-diagnostics/s11/2026-10-09-fixed-center-readout.md` 및 JSON |
| E03 | `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` — 해석 계약·9개 구간·폐기한 과거 해석 |
| E04 | `sample/README.md`; 4개 `.oilrecipe`·`.oiltruth` — 고정 geometry, corpus/truth 의미 |
| E05 | `docs/20-architecture/s11-current-detector-logic-map.md`; `src/oil_tracker/domain/geometry.py` |
| E06 | `docs/60-evidence/s11/2026-10-09-local-xy-implementation.md` |
| E07 | `docs/50-diagnostics/s11/2026-10-09-local-xy-sequence-causality.md` |
| E08 | `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` — F02/F04/F06/F07/F09/F10 |
| E09 | `docs/50-diagnostics/s11/2026-10-09-material-reference-feasibility.md`; `2026-10-09-material-reference-design-choice.md` |
| E10 | `docs/50-diagnostics/s11/2026-10-09-reference-current-boundary.md` |
| E11 | `docs/50-diagnostics/s11/2026-10-09-public-scene-controls.md`; 후속 public-water/material-reference/retained-support 판단 기록 |
| E12 | `docs/20-architecture/s11-interface-observability-witness-architecture.md` — W1·fixed-center·region competition·Local XY |
| E13 | `docs/30-validation/s11-interface-observability-witness-validation.md` — W1 controls·O2/O3/field gates |
| E14 | `src/oil_tracker/adapters/vision/foam_front_detector.py` — `detect_bottom_connected_foam`, `_structural_substrate_relation`, `_detached_material_phenotype` |
| E15 | `tests/diagnostics/s11_foam_support_geometry.py`; `tests/diagnostics/s11_boundary_temporal_probe.py` |
| E16 | 이번 로컬 실행 폴더의 `verification.json`, `center-projection-ablation.json`, `visual-review.json`, `focused-tests.log` |
| P01 | OpenCV official: “Image Segmentation with Watershed Algorithm”, https://docs.opencv.org/4.13.0/d3/db4/tutorial_py_watershed.html — marker input/unknown semantics 참고용. H0 구현·S11 효과의 증거는 아님. |

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PROPOSAL`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: Local XY saved causal replay; fixed reference matching and LK correspondence; current support/perimeter and fixed-center readout; region competition; Foam internal-texture and structural-substrate failures; canonical Windows reviewed truth.
- Prior mechanisms rejected: threshold/window/mask tuning of closed variants; nearest-edge rescue; seed survival as identity; brightness-support extremes as physical fronts; production phase/episode relaxation before identity.
- Preserved contracts: fixed-center target; independent Oil/Foam observation; same-frame selected geometry; no interpolation/carry; separate original candidate Y and challenger scalar; staged O2/O3/O4/O5 acceptance; no Windows media export; current work-plan ownership.
- Difference from prior failures: the proposed CBR-1 compares reference-side evidence at current observed candidate geometry, rather than carrying semantic seed positions through LK and globally flooding regions. H0/G1 remain rejected probes; the geometry ablation isolates a representation dependency without claiming semantic repair.
- Logic-map impact: NONE — no executing production owner or authority path is changed; the future helper is a proposal for an existing offline diagnostic boundary.
- Failure-registry impact: NONE — the observed limits instantiate already recorded representation, correspondence and role-identity failure classes; this document retains the named probe and its limits without changing registry conclusions or claiming a new field cause.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PROPOSAL`, `OIL-CANDIDATE`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: in the new offline probe, the legacy support-face intersection adds a proven geometry-stage loss; current side/reference correspondence still leaves ambiguous regions and a later agent-observed wrong-region proposal. The first exact physical identity break is not certified by dense truth. No new production/Windows first-cause claim follows.
- Logic-map impact: NONE — saved-output experiments and a proposed next diagnostic do not change runtime ownership or publication.
- Failure-registry impact: NONE — existing failure classes and closed user judgments are preserved; the experiment is not promoted and no field disposition changes.
