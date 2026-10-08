# S11 다음 작업 계획 명세서
## Windows 우선 · 계면 정체성 및 admission 개선 · 움직임 맥락 기준

- 작성일: 2026-10-08
- 문서 상태: **다음 작업의 실행 명세 / detector 개선 효과는 아직 미입증**
- 프로젝트: `teeeeooo/oil_level_tracker`
- 검토 기준 main: `49c6d3aebeaf90aea96cd5be4c0e91115011f5a7`
- 검토한 handoff delivery: `e5d4a0430ea69beab59736396a2817c09b5efd69`
- delivery branch: `work/s11-spatial-identity-20261008`
- delivery의 실험 base: `c4814bdc25c4da22776d985fbb7a2d66fbc4e1e8`
- 이번 작업의 변경 범위: 저장소·증거·선택 프레임 검토, 검증, 실행 계획 작성. **생산 코드·main·recipe·truth 변경, commit, push, detector 승격은 하지 않았다.**

> **완료 목표는 모든 프레임에서 Oil/Foam을 검출하는 것이 아니다. 기존 report 산출물로 사용자가 실제 계면의 상승·하강·재등장과 Foam의 생성·소멸을 이해하도록 하는 것이다. 일부 짧은 누락은 허용하지만, 다른 구조를 계면으로 추적하여 잘못된 운동이나 재료 전환을 확신하게 만드는 결과는 줄여야 한다.**

이 문서의 `[S#]`는 말미의 commit 고정 출처를 가리킨다. 사실, 기존 기록의 해석, 새 제안 및 아직 측정하지 않은 항목을 구분한다.

---

## 1. 최종 권고

**다음 detector 작업은 selector 점수 조정이 아니라, 후보별 실제 경계의 역할을 판단하는 근거와 그 근거가 admission까지 전달되는 경로를 개선하는 방향으로 진행한다.**

실행 순서는 다음과 같다.

1. 기존 Windows W3 원본 audit에서 **이미 있는 후보가 어느 기록 경계에서 배제되는지 한 번만 좁혀 확인**한다. 후보 유지 이전 손실, tracklet 미승인, phase/owner 제한, 최종 선택 미해결을 구분한다.
2. 실제 유체 경계 여부와 제품의 추적 대상 여부를 분리하는 **후보별 경계 역할 검증 가설**을 설계한다. 처음부터 새로운 전역 점수·최대값 선택기로 만들지 않는다.
3. 새 근거의 효용을 먼저 shadow에서 시험한다. **잘못된 계면 출력을 보류하는 효과**와 **실제 계면을 회복하는 효과**를 별도로 평가한다. 하나의 잘못된 Y를 반드시 다른 Y로 대체할 필요는 없다.
4. 실제 구별 능력이 확인된 뒤에만 support/admission 연결과 phase 재획득을 각각 검증한다. FULL/EMPTY 안전 장벽을 먼저 푸는 방식은 사용하지 않는다.
5. Foam은 별도의 material/front/episode 경로에서 개선한다. 최종 판정은 Windows의 9개 구간과 **수정하지 않은 기존 report**로 한다.

**이번에 폐기할 접근은 “더 좋은 후보 순위가 있으니 selector를 조정하면 해결된다”는 전제다.** 최근 실험의 sample4 세 오추적은 목표 후보가 selector에 도달하지 못해 개선되지 않았다. 반대로 Windows에는 유지된 후보가 최종 선택되지 않은 사례도 있다. 서로 다른 손실을 하나의 점수 문제로 처리할 수 없다. [S2][S4][S10]

새 가설의 알고리즘과 수치 operating point를 이 문서에서 검증된 해법처럼 확정하지 않는다. 현재 공개된 Windows 증거만으로는 이를 정당화할 전체 픽셀·대응 반례가 부족하다. 대신 **선택할 입력, 반증 조건, 코드 경계, 산출물, 다음 단계 진입 조건을 확정**한다. D2에서 수학적 규칙 또는 학습 모델을 별도로 고정하지 못하면, 빈 분류기를 구현하거나 descriptor를 계속 추가하지 않는다.

---

## 2. 현재 S11 상태와 이번에 실제로 확인한 범위

### 2.1 main과 handoff의 관계

| 항목 | 확인 결과 | 해석 |
|---|---|---|
| 현재 checkout | main `49c6d3a…`; tracked 작업 트리 clean | handoff의 unchanged main과 일치 |
| 최근 delivery | `e5d4a04…`, 별도 diagnostic branch | main에 채택된 detector 변경이 아님 |
| main 대비 delivery의 생산 코드·의존성·recipe·truth 차이 | 없음 | 최근 실험은 detector 배포 성능 개선이 아님 |
| Cellular/boundary/selector 실험 | CLOSED WITHOUT PROMOTION | 중단된 실행을 이어야 하는 상태가 아님 |
| S11 현장 상태 | FIELD FAIL 유지; W4/O2 미충족 | 로컬 테스트와 provenance 검증으로 승격 불가 |
| report 개선 | source context / source sequence 계열 개선은 기존 main에 반영 | 새로운 UI 개편을 다음 detector 작업의 선행 조건으로 삼지 않음 |

main의 Work Plan은 현재 상태의 소유자이고, delivery의 closeout은 **main 바깥에서 완료된 실험의 증거**다. 둘을 합쳐 읽되, 별도 브랜치의 완료를 main 채택으로 쓰거나 종료된 실험을 다시 pending으로 쓰지 않는다. [S1][S2][S3][S9]

### 2.2 이번 검토에서 새로 수행한 확인

| 확인 | 이번 결과 | 범위 제한 |
|---|---:|---|
| handoff ZIP manifest의 파일 크기·SHA-256 검증 | **872개 모두 일치** | 아카이브 무결성이지 물리적 정확도는 아님 |
| 현재 4개 영상 + 4개 recipe + 4개 truth의 intake pin 대조 | **12/12 일치** | truth의 적용 범위·주석 의미는 별도 보존 |
| 원본 영상에서 새로 읽은 프레임 | **36개** | 네 영상 전체 연속 재생·전수 판독은 아님 |
| sample4 7개 원본 crop과 보존 crop의 픽셀 대조 | **7/7 동일** | 새 contour 또는 물성 truth를 만들지 않음 |
| 저장된 observer OFF/ON sample 비교 | **299행, `run_id` 외 모든 필드 동일** | 새 detector 실행이 아니라 보존된 application 출력 재검증 |
| delivery 소스의 관련 계약 테스트 | **294 passed / 0 failed / 0 skipped** | 8개 focused module; full suite·Qt·Windows 실행 아님 |
| 종료 시 tracked 상태 및 생산 diff | clean / 차이 없음 | ignored audit 산출물만 추가 |

초기 audit 스크립트는 서로 다른 실행의 `final-samples.json`에 **파일 바이트 동일성**을 요구하여 실패했다. 모든 필드 차이를 조사한 결과 네 영상 모두 `run_id`만 달랐다. 첫 실패 JSON과 스크립트는 보존했고, 별도 비교 기록으로 이 차이를 명시했다. 이전 출력의 값이나 hash를 수정해 통과시킨 것이 아니다. [S13]

인수인계의 `2548 passed`, 복구한 12개, 217개, 마지막 17개는 서로 범위가 다르거나 겹친다. 이번 294개에 합산하지 않는다. 이번 검토는 **새 Windows 성능, 새 전체 application replay, 독립적인 report 이해도 검증을 수행하지 않았다.** [S1][S2][S13]

---

## 3. Windows 증거에서 정해야 할 우선순위

### 3.1 반드시 유지할 9개 구간

아래 시간은 canonical reviewed truth의 구간이며 일부 경계는 `about`이다. runtime에 넣을 timestamp 규칙이 아니다. Source Y는 아래로 증가한다. [S5]

| Segment ID | 구간(s) | 사용자가 report에서 이해해야 할 내용 | 다음 detector 작업의 핵심 질문 |
|---|---|---|---|
| `WS1-BASE-FULL-PREFIX` | 480–약 550 | 가득 차 있지만 보이는 계면은 없음; Foam 없음 | 새 identity/admission이 내부 구조를 계면으로 만들지 않는가? |
| `WS1-BASE-DRAIN` | 약 550–662 | 계면이 나타나 전반적으로 하강 | 보이는 목표가 후보·정체성·phase 중 어디서 막히는가? |
| `WS1-BASE-RAPID-REFILL` | 662–약 663.6 | 빠르게 상승하고 위로 사라짐 | 상승을 유지하고 FULL로 닫히는가, 다른 줄로 갈아타는가? |
| `WS1-BASE-FULL-SUFFIX` | 약 663.6–780 | 다시 가득 차며 보이는 계면 없음 | 재획득 기능이 반사·하부 구조를 재등장으로 오인하는가? |
| `WS1-ACCUM-EMPTY` | 480–약 653 | Oil/Foam 계면 없음 | 정지한 바닥·구조를 entry로 잘못 승인하지 않는가? |
| `WS1-ACCUM-ENTRY-SPLASH` | 약 653–672 | Oil 유입·상승, splash와 벽 흔적; 아직 Foam 아님 | 실제 계면, splash, 벽 흔적의 ownership을 구별하는가? |
| `WS1-ACCUM-FOAM-LAYERED` | 약 672–680 | 위 Foam front와 아래 Oil 경계가 함께 존재 | Foam top을 Oil로 바꾸지 않고 두 시리즈를 구분하는가? |
| `WS1-ACCUM-POST-FOAM` | 약 680–700 | Foam은 사라지고 Oil 경계는 유지 | Foam 종료 뒤 Oil 정체성이 유지·재획득되는가? |
| `WS1-ACCUM-DRAIN` | 약 700–780 | Oil 경계가 하강하며 벽 잔류 흔적이 남음 | 잔류 흔적으로 옮겨 붙지 않고 하강 맥락을 전달하는가? |

9개를 한 평균으로 합치지 않는다. 특히 FULL/EMPTY 안전 대조, BASE의 가시 계면 구간, Accum의 Foam 전후 전환은 각각 보고한다. 정확한 source-Y 주석이 없는 구간은 pixel MAE를 만들지 않는다.

### 3.2 영향도 판단: 역사적 R20과 현재 설계 입력을 구별한다

R20 Windows 통합 기록은 BASE의 가시 drain/refill에서 Oil 출력 0, Accum의 Foam 시작 전 7개 잘못된 Foam 출력, 678.5112–711.0020s 사이 약 32.49초의 Oil publication 간격을 보고한다. 이것은 **전체 움직임이나 전환을 놓치는 문제가 작은 위치 오차보다 중요함을 보여 주는 역사적 현장 입력**이다. 현재 main에서 같은 수치가 재현된다는 뜻은 아니다. 원본 Windows bundle을 이번에 직접 열지 않았다. [S7]

따라서 우선순위는 다음과 같다.

- **P1: 긴 계면 부재·잘못된 owner 유지 때문에 전체 상승/하강을 잃는 문제.** BASE drain/refill과 Accum post-Foam/drain을 중심으로 판단한다.
- **P2: Oil/Foam 역할 혼동과 잘못된 episode 전환.** Entry splash를 Foam으로 읽거나 Foam top·잔류 구조를 Oil로 읽는 문제다.
- **P3: 국소 좌표 오차와 짧은 누락.** 주요 방향·전환을 뒤집거나 중요한 excursion을 지우는 경우에만 상위 문제로 올린다.

이 순서는 제품 목적에 따른 제안이다. R20의 건수를 최신 main 성능표로 옮겨 적어 우선순위의 수치 근거로 사용하지 않는다.

### 3.3 Windows W3가 실제로 보여 주는 경계

W3의 3개 review에는 총 **73개 후보(23/23/27)**가 있다. 48개는 retained refs에 있고 25개는 없다. 이 inventory는 뒤의 passive 75개 batch와 다르다. [S4]

| 증거 | 확정 가능한 내용 | 아직 확정할 수 없는 내용 |
|---|---|---|
| review-002 / idx0, review-003 / idx10 | packet에는 있으나 retained refs에는 없음 | 후보 생성 실패인지, authority/retention의 어느 단계인지 |
| review-002 / idx8·9 | 검토된 interface; admitted row에 있으나 최종 선택 안 됨 | selector 결함, allowed-owner 제외, ambiguity, suppression 중 무엇인지 |
| review-002 / idx10·12·16 | continuation 수준이며 tracklet admission flag는 false | 실제 정체성 부족인지, 어떤 조건이 최초로 유해했는지 |
| review-003 / idx19 | 검토된 interface; admitted row에 있으나 최종 선택 안 됨 | row membership만으로 해당 member가 실제 publication 조건을 모두 통과했는지 |
| review-001의 admitted 후보, review-002 / idx20 | 음성 후보도 admitted row에 들어갈 수 있음 | admission을 곧 물리적 정체성으로 간주할 수 없음 |

`phase_admitted`와 `publishable`은 constructed row의 membership 정보다. 이를 각 member의 독립적인 계면 인증서로 읽지 않는다. `selected_candidate=None`도 단일 실패 원인이 아니다.

Material 요약값은 양성·음성 사이에 겹치고, 어떤 사례에서는 음성이 더 크다. static/glare가 0이라는 사실 역시 계면을 증명하지 않는다. **전역 material threshold의 증가·감소 어느 쪽도 이 증거에서 정당화되지 않는다.** [S4]

### 3.4 목표 정의는 이미 해결된 항목이다

Windows passive batch의 물리 주석은 **13 interface / 62 non_interface**다. 사용자가 추적 대상을 최상위 실제 유체 경계로 명확히 한 후, target 역할은 **10 target / 3 real internal interface / 62 other non-target**으로 구분됐고 Windows binding도 완료됐다. 상태는 `BOUND_NOT_EVALUATED`이며 prediction 성능은 없다. [S6]

다음 작업은 다음을 재개하지 않는다.

- 최상위 경계가 목표인지 다시 묻기.
- 3개의 실제 내부 경계를 가짜 반사로 relabel하기.
- 13개의 broad interface를 모두 target positive로 학습·평가하기.
- 완료된 75개 batch를 다시 bind하거나 같은 후보를 다시 판독하기.

**최상위 실제 유체 경계라는 정의와 Foam 독립 검출은 함께 유지한다.** Foam front를 Oil target으로 삼지 않으며, 가려진 상부 target 대신 보이는 내부 경계를 승격하지 않는다. 최소 Y 후보를 선택하는 방식은 물리적 정체성 판정이 아니다.

---

## 4. Mac 샘플의 역할과 이번 영상 확인

Mac은 Windows 대신 성능을 증명하는 calibration/holdout이 아니라 **기존 회귀·반례·메커니즘 확인 자료**로 쓴다. [S2][S8]

| 영상 | 이번에 읽은 프레임 수 | 확인한 용도와 제한 |
|---|---:|---|
| `base_sample_1` | 6 | 약한 경계와 영상에 원래 들어 있는 High/1/3/Low 안내선. README에 안내선 시작 f151이 명시돼 있다. 강한 수평선 대응 반례로 보존하고 임의 exclusion으로 숨기지 않는다. |
| `sample2` | 5 | 안정 window의 bubbly appearance와 강한 반사. 단일 texture/basin 최대값을 계면 정체성으로 쓸 수 없는 회귀 자료다. |
| `sample3` | 10 | fill/agitation/drain과 관측 불량을 분리할 필요. f2010 crop은 거의 검게 보였다. 모든 긴 공백을 실제 계면 누락으로 판정하지 않는다. |
| `sample4` | 15 | 기존 7개 판독 지점과 42.5–44s 중간 움직임. native 프레임에서 변화가 보이지만, 중간 프레임의 정확한 contour truth를 새로 작성한 것은 아니다. |

Contact sheet의 `frame_index / OpenCV FPS` 표시는 nominal time이다. 정확한 join은 source frame ID와 원래 실행의 timestamp를 쓴다. 특히 base의 보고 FPS는 30.059287…이고, source PTS/기존 application timestamp와 임의로 동일시하지 않는다.

### 4.1 sample4는 “세 점 복구 대회”가 아니라 잘못된 움직임의 회귀 사례다

| 프레임 / 시간 | 검토된 목표 후보 Y | baseline = selector 실험 Y | selector 직전 목표 후보 상태 |
|---|---:|---:|---|
| 1140 / 38s | 844 | 844 | 존재, 선택 유지 |
| 1200 / 40s | 841 | 865.5 | retained refs 이전에 없음; 더 이른 원인은 이 replay에서 미확정 |
| 1260 / 42s | 839 | 868 | candidate-only / insufficient authority / tracklet 미승인 |
| 1275 / 42.5s | 835 | 835 | 존재, 선택 유지 |
| 1320 / 44s | 844 | 822 | candidate-only / material-layer-terminal / tracklet 미승인 |
| 1485 / 49.5s | 836 | 836 | 존재, 선택 유지 |
| 1560 / 52s | 833 | 833 | 존재, 선택 유지 |

이 표는 closeout의 **정확한 member join**이다. 같은 Y 또는 가까운 Y의 다른 후보에 사람의 identity 주석을 옮기지 않는다. [S2]

중요한 예는 42.5→44s다. 검토된 endpoint는 `835→844`인데 기존 결과는 `835→822`다. Source Y가 아래로 증가하므로, 해당 두 endpoint에서 **검토된 하강을 결과가 상승 방향으로 표현**한다. 이는 단순 수 px 차이가 아니라 맥락 문제다. 다만 중간 운동 전체를 두 점으로 보간해서 truth로 만들지는 않는다.

다음 가설은 이 세 오류를 모두 고치지 않아도 검토 가치가 있다. **기존에 맞게 전달되던 움직임을 보존하면서 잘못된 큰 이동·역방향 해석을 줄이는가**가 우선이다. 모든 출력을 없애거나 중요한 excursion까지 지워서 이를 달성한 것처럼 보이면 실패다.

### 4.2 저장된 검출 수를 검출률로 읽지 않는다

| 영상 | 관측 행 | baseline valid numeric Oil | selector 실험 valid numeric Oil | valid numeric Foam, 양쪽 동일 |
|---|---:|---:|---:|---:|
| base | 30 | 27 | 26 | 0 |
| sample2 | 5 | 4 | 4 | 0 |
| sample3 | 151 | 29 | 30 | 5 |
| sample4 | 113 | 101 | 101 | 26 |

이 값은 보존된 실험의 `projected_counts`이며 이번에 새 detector를 돌려 얻은 값이 아니다. Raw numeric과 valid numeric은 다르다. 예를 들어 base baseline의 raw numeric Oil은 28이지만 valid numeric은 27이다. 후보 수·행 수 증가를 물리 정확도나 이해도 향상으로 바꾸어 쓰지 않는다. [S2][S13]

---

## 5. 종료된 실험과 반복 금지 범위

| 종료된 접근 | 확보된 결론 | 다음 작업에서 반복하지 않을 것 |
|---|---|---|
| H1: material opposition 때 terminal FULL 확인 보류 | 기존 안전 대조에서 null이어야 할 Oil Y64가 출력됨 | terminal 조건 완화로 출력량부터 늘리기 |
| H1b: terminal은 null, FILLED barrier만 지연 | ownership barrier 대조 실패; sample3 Oil 29→65는 correctness 미입증 | cap/barrier를 미루고 coverage 증가를 성과로 보고 |
| LabPics 고정 material rank | 두 view 모두 검토된 목표 7개를 top tie set으로 선택하지 못함 | 같은 checkpoint/readout을 threshold·채널 선택으로 재해석 |
| Cellular global / extent / co-located readout | 각각의 한계와 양성 손실 보존; 국소 모양과 generic identity는 다름 | basin 크기·가중치·tensor 반경을 연속 조정해 같은 실험 반복 |
| Selector emission permutation | 네 영상 검증 완료; sample4 세 오류 0개 개선 | 이미 배제된 member를 selector 점수로 되살리려는 시도 |
| 과거 motion/texture/whole-track 접근 | 매끄러운 이동·같은 track·texture 부호만으로 정체성 불충분 | motion-only anchor, 전체 family/track 권한, 교차 재료 identity 복사 |

기존 실험이 실패했다는 사실이 모든 학습 모델이나 모든 물리 표현의 실패를 뜻하지는 않는다. 그러나 다른 모델 이름이나 descriptor를 붙였다는 이유만으로 새 가설이 되는 것도 아니다. **무엇을 새로 관찰하고 어떤 반례를 구별하는지**가 달라야 한다. [S2][S9][S10][S11]

---

## 6. 다음 작업의 성공 기준: 맥락 개선과 측정 정직성

### 6.1 제품 endpoint와 안전 불변량을 분리한다

**제품 endpoint**

- 계면의 주요 상승·하강, 재등장, reversal, 상단 소실이 report에서 제대로 읽힌다.
- Oil과 Foam의 역할·생성·소멸이 혼동되지 않는다.
- 짧은 누락을 허용하더라도 긴 잘못된 owner 유지나 가짜 극값이 줄어든다.
- 원래 없던 계면과 관측 불량에 의한 UNKNOWN을 구별할 수 있다.

**변경하지 않을 안전 불변량**

- 숫자는 해당 프레임의 정확한 후보에서 나온다. 보간·carry·snapshot Y 출력은 금지한다.
- Oil/Foam의 validity와 ownership은 독립적이다.
- FULL/EMPTY는 좌표를 만들지 않는다. 모호한 identity는 UNKNOWN으로 남긴다.
- production이 truth, case index, frame/time, Glass 이름·ID, 파일 hash를 판정 근거로 사용하지 않는다.
- 경로·sidecar·추가 진단이 기존 production 판단에 우연히 입력되지 않는다.

“일부 누락 허용”은 안전 불변량 완화가 아니다. 반대로 모든 sparse annotation을 정확히 선택하지 못했다는 이유만으로 맥락 개선까지 부정하는 기준도 사용하지 않는다.

### 6.2 보고할 지표

| 지표 | 정의·보고 방법 | 오용 방지 |
|---|---|---|
| 주요 동작 판독 | 9개 구간별 rise/fall/reversal/disappearance 및 Foam 사건 판독 | 단순 선형회귀 기울기로 전체 물리 운동을 확정하지 않음 |
| 잘못된 target 부담 | 확인된 wrong-target 관측 수, 연속 run, 최대 지속 범위 | unreviewed를 정답/오답으로 자동 분류하지 않음 |
| 보이는 계면의 누락 | reviewed-visible 구간의 missing run과 최대 길이 | 실제 no-interface 또는 관측 불량과 분리 |
| 유용한 episode coverage | 주요 운동을 실제 관측이 뒷받침하는지 | all-abstain은 성공이 아님 |
| 잘못된 전환 | 가짜 Foam onset/잔존, Oil/Foam 교환, 거짓 FULL/EMPTY 의미 | 행 단위 평균이 전환 오류를 가리지 않음 |
| 실제 관측량 | raw numeric, valid numeric, missing, UNKNOWN을 각각 보고 | raw=valid, numeric=correct로 바꾸지 않음 |
| provenance | frame/member/source/Y, owner chain, 최종 sample 연결 | 같은 Y의 다른 후보는 같은 truth가 아님 |
| 처리 비용 | wall time, memory, trace bytes, 후보·sector·상태 상한 | window/cadence 변경으로 비용 차이를 숨기지 않음 |

시간 가중 지표를 추가할 때는 sample의 시간 지지 구간 정의를 먼저 고정한다. 직접 확인하지 않은 프레임 사이에 물리 오차나 실제 계면을 보간하지 않는다. 긴 missing run은 마지막 관측–다음 관측의 elapsed time과 missing sample span을 구별한다. Approximate truth 경계 부근은 판정 보류/경계 불확실성을 명시한다.

수치 acceptance threshold를 이번 7개 지점이나 현재 Mac 분포에서 발명하지 않는다. 새 실험의 quantitative endpoint는 calibration 전에 등록하고, **의미 있는 개선 + 주요 동작 비열화 + 불변량 유지**를 함께 검토한다. O2/현장 validation 계약을 수정해야 하면 해당 owner에 별도로 반영하며, 종료된 실험의 기준을 소급 변경하지 않는다. [S5][S12]

---

## 7. 실행 작업 패키지

### D0. 인수인계와 baseline 고정 — 이번 검토 완료

**산출물**: 본 명세서, 별첨 검증 요약, 로컬 audit 디렉터리.

다음 구현자는 새 branch를 고정된 main에서 만들고 필요한 diagnostic만 최소 단위로 가져온다. `e5d4a04` 전체를 “detector 개선”으로 main에 합치지 않는다. 인수인계 ZIP의 archived source/measurements는 읽기 전용으로 유지하고, 모든 새 실행에는 새 output 디렉터리를 쓴다.

**다시 할 필요가 없는 일**: 같은 종료 실험을 재개하기 위한 전수 inventory, 7-frame label 재작성, 기존 selector permutation의 추가 sweep.

### D1. Windows의 이름 붙은 손실 질문 하나 해결 — 최우선, 제한된 readout

**목표**: “선택되지 않음”을 실제 기록 가능한 경계까지 좁힌다. 물리 정체성이나 최초 원인을 추정해서 채우지 않는다.

**입력**

- 첫 W3 target audit의 원본 `experiment.json`.
- 원본 raw SHA-256: `ba5fe04b28473f70387e363ef7d40077f559c80b1852755d997e1dd04171937f`.
- delivery의 기존 `tests/diagnostics/s11_candidate_loss_audit.py`.

**실행**: 기존 stdlib-only reader를 Windows에서 한 번 실행한다. 원본이 다른 revision이면 기존에 기록된 그 artifact hash를 사용한다. 같은 hash를 맞추기 위해 파일이나 pin을 편집하지 않는다.

**필수 출력**

- 기존 case/frame/Glass/packet/witness 연결.
- candidate offset, source, Y와 retained 여부.
- authority/tracklet/row membership과 실제 recorded allowed mode / allowed IDs.
- 모든 기록된 exclusion 및 최종 선택의 관측 여부.
- raw 물리 주석과 product target-role 적용 여부를 구분한 결과.

이 reader는 broad physical label을 보존하지만 `target_role=NOT_IMPORTED`다. passive target truth와 자동으로 결합되는 도구가 아니다. 서로 다른 73개·75개 inventory를 index 번호로 교차 결합하지 않는다. [S4][S6][S10]

**분기 결정표**

| readout 결과 | 다음 작업 경계 | 금지되는 결론 |
|---|---|---|
| `UNKNOWN_BEFORE_RETAINED_REFS` | 같은 실행의 pre-retention 기록이 있을 때만 eligibility/authority/retention 비교 | top-k 또는 candidate generation을 임의로 범인 지정 |
| `TRACKLET_NOT_ADMITTED` | 후보 identity와 tracklet confirmation을 구분하여 D2 대조 구성 | 장기 smoothing으로 tracklet을 강제로 승인 |
| `PHASE_HARD_GATE` / `OWNER_NOT_ALLOWED` | D2 identity가 확보된 후 D4의 phase/owner 조건 비교 | gate가 있으므로 gate를 삭제 |
| `FINAL_SELECTION_UNRESOLVED` | representative selection, allowed owner, ambiguity, suppression의 실제 입력을 확인 | publishable row였으니 selector bug라고 단정 |
| 필요한 filter 필드 자체 없음 | `UNAVAILABLE`로 종료; 필요한 정확한 필드만 명시 | 새 대규모 audit·전체 영상 재판독 자동 요청 |

**완료 조건**: 특정한 수정 대상 owner를 지목할 만큼 기록이 있는지, 아니면 어떤 필드가 없는지를 분명히 남긴다. 결과가 unknown이어도 readout 작업은 종료할 수 있다. **하지만 그 결과를 detector 개선 완료로 보고하지 않는다.**

**자료가 없는 경우**: 이번 Mac 환경에는 Windows 원본이 없으므로 D1 실행은 하지 않았다. 이때 D2의 계약·대조군·fixture 설계는 진행할 수 있다. Windows 원인을 추측한 production 변경만 보류한다. 완료된 W3/target-binding 작업을 전체 재실행하지 않는다.

### D2. 후보별 경계 역할 검증 가설 설계 — 주 detector 설계 작업

**가설명(신규 제안)**: `H-ROLE — candidate-local boundary-role evidence`.

**질문**: 기존 candidate의 실제 공간 지지와 반대 근거를 함께 보존하면, 전체 material/texture 점수나 같은 track에 의존하지 않고 “실제 target 경계 / 실제 내부 경계 / 다른 구조 / 모호함”을 구별할 수 있는가?

이것은 성능이 확인된 분류기 이름이 아니라, 다음에 반증할 설계 가설이다.

**기존 실험과 달라야 하는 핵심**

- 단순 후보 순위가 아니라 **각 member의 정체성과 역할**을 출력한다.
- 위·아래 영역의 material 점수 최대값이 아니라, 후보 contour가 어떤 관측 가능한 영역을 실제로 가르는지와 반대 근거가 어디에 놓였는지를 유지한다.
- 분리된 관측을 scalar median/max로 모두 축약한 뒤 identity로 승격하지 않는다.
- 반사/구조와 실제 경계가 동일하게 보이는 대조에서는 unresolved를 낸다. 평활성, 방향, 밝기, polarity, 상대 높이를 인증서로 쓰지 않는다.

**입력 계약**

1. 원본 source-frame과 recipe의 bounded ROI, effective/glare mask.
2. 정확히 연결된 기존 후보와 native contour/sector. native와 candidate-centered geometry를 묵시적으로 교환하지 않는다.
3. 후보 주변의 양측 관측, 유효 픽셀, clipping·occlusion·artifact opposition의 실제 공간 범위.
4. 필요하면 ROI의 2-D 문맥. 관측 범위를 확대하면 같은 support에서의 모델 변경과 support 확장의 효과를 분리한다.
5. 없는 값은 null+reason. 같은 신호에서 파생된 채널/후보는 독립 투표로 세지 않는다.

**선택해야 할 설계 사항**

- 어떤 추가 observable이 Windows의 실제 양성/대응 음성을 나누는가?
- 단일 후보 중심 band 밖에서 얻는 정보가 구별에 필요한가, 아니면 이미 있는 정보의 재집계인가?
- 실제 계면과 같은 형태의 반사·정지 구조를 무엇으로 구별하는가? 구별 불가능한 경우 범위는 어디까지인가?
- full path, 부분 path, scalar usability를 어떤 별도 출력으로 유지하는가?
- 필요한 모델 용량, mask 처리, resource bound, threshold/calibration 방법은 무엇인가?

**수식/모델 고정 전 진입 조건**

- Windows 기반의 target positive, 그와 같은 local cue를 공유하는 target-negative, unresolved control이 있어야 한다.
- 기존 75개 batch의 멀리 떨어진 group negatives만으로 hard-negative 대조가 충족됐다고 하지 않는다.
- 다른 기존 recording을 사용할 때는 픽셀을 보기 전에 metadata와 과거 노출 이력으로 development/calibration/holdout 역할을 고정한다. 이미 본 자료는 regression이다.
- 학습형 challenger를 선택한다면 별도 W4-R2/O2 데이터·partition 진입 조건을 먼저 충족한다. 이번 handoff 종료가 학습 착수 승인인 것은 아니다.

**반증 및 작업량 제한**

같은 구별 질문에 대해 하나의 frozen challenger와 사전 명시한 대조만 실행한다. 핵심 반례가 그대로 남으면 그 가설은 종료한다. 후속 variant는 실패 후 임의 threshold/반경 조정이 아니라 **새 observable 또는 명시적으로 다른 메커니즘**을 요구한다. descriptor 추가 자체를 진척으로 계산하지 않는다.

**완료 산출물**: concrete algorithm/operating-point 설계, fixed input manifest, positive/negative/unresolved matrix, 기대되는 판정의 이유, 적용 불가능 범위. 자료가 부족하면 부족한 **구별 조건 하나**를 명시한다. “영상 더 많이 필요”라는 포괄적인 요청으로 끝내지 않는다.

### D3. Shadow 및 움직임 반사실 검증 — detector 효용 검증

**원칙**: official detector는 그대로 유지한다. D2의 결과가 production에 읽히지 않는 별도 sidecar를 생성하고, W3의 기존 평가 소유자를 재사용한다.

**서로 다른 효과를 분리해서 평가한다.**

| 비교 | 물어볼 질문 | 제한 |
|---|---|---|
| Identity/target shadow | 실제 target을 보존하며 내부 경계·다른 구조를 구별하는가? | 점수만 생성하거나 전부 unresolved로 내면 개선 아님 |
| 선택적 wrong-target 보류 | 명시적인 현재 프레임 반대 근거가 있는 오추적을 줄이는가? | 단지 불안정하거나 반대 방향이라는 이유로 진짜 운동을 삭제하지 않음 |
| Same-frame target 회복 | 기존 후보 중 실제 목표가 있을 때 유용하게 전달되는가? | 없는 후보의 Y를 생성하거나 HARD_INVALID를 우회하지 않음 |
| 기존 report 반사실 | 주요 운동과 Foam 전환의 이해가 개선되는가? | graph smoothing/보간으로 detector 실패를 감추지 않음 |

보류와 회복은 별도 대조다. 두 가지를 동시에 바꿔 원인을 알 수 없게 하지 않는다. 반사실 출력은 real production 결과와 이름·directory·schema로 분리하고, truth를 입력한 oracle 결과를 구현 성능처럼 보고하지 않는다.

**필수 평가**

- 모든 양성/음성/unresolved 및 human-visible의 분모 유지.
- target identity와 path/scalar 품질 분리. 물리 interface인 내부 경계도 target-negative임을 보존.
- sample4의 7개는 회귀 사례로 전부 보고하되 **7/7을 프로젝트 보편 완료 조건으로 만들지 않음**.
- sample2의 구조·반사, base의 설명선, sample3의 관측 불량/재등장, sample4의 excursion을 함께 보호.
- 후보 수, source order, missingness, duplicate/lineage 독립성 및 입력 hash 불변 확인.

**O2 종료 조건**: 현재 validation owner가 요구하는 controls, operating point, partition/holdout, behavior equality, Windows shadow 근거를 충족한다. 이번 36프레임과 294테스트로 이 조건을 갈음하지 않는다. [S12]

### D4. Admission·재획득 연결 — O2 뒤에만 수행

D4는 하나의 대형 패치가 아니라 **D4a support/admission 연결(W5/O3)**과 **D4b phase/owner transition(W6/후속 gate)**으로 분리한다.

**D4a**

- 새 candidate-local 근거가 실제로 필요한 첫 경계에만 연결한다. 이미 후보가 없는 경우 selector 변경으로 돌아가지 않는다.
- 현재 `evaluate_candidate_authority`, evidence 준비/retention, tracklet confirmation과의 관계를 명시한다.
- 단일 global enum/점수 추가로 기존 모든 guard를 통과시키지 않는다.
- candidate identity, continuation 가능성, 독립 anchor 가능성은 각각 별도 요건이다.
- 기존 후보 집합에서 충분한 개선이 가능한지 먼저 본다. 정말 proposal 부재가 확인된 경우에만 별도 proposal 설계를 연다.

**D4b**

- FULL 이후 실제 target의 재등장, partial-fill owner 소실 이후 재획득, rapid refill closure를 각각 양방향 대조한다.
- “barrier가 오래 유지됨”이 아니라 **새 현재-frame physical target witness + bounded confirmation + 해당 transition의 물리 조건**이 있어야 한다.
- stationary target은 identity 대조에서 유효할 수 있지만, stationary row를 drain release로 자동 승인하지 않는다. 정체성과 방향성 전이 조건을 구분한다.
- 새 owner ID는 명시적으로 연결하고 이전 ID/Y를 복사하지 않는다. ambiguity, 실제 no-interface, 관측 불량은 별도 보존한다.
- H1/H1b가 깨뜨린 terminal null/ownership 안전 대조를 반드시 유지한다.

**검증 방법**: 변경 직전·직후 같은 입력, 같은 cadence, 같은 recipe에서 authority→retention→tracklet→phase→selector→projection의 차이를 비교한다. 한 단계만 바꾸어도 이후 Oil/Foam/episode/event가 달라질 수 있으므로 전체 결과를 함께 기록한다.

**완료 조건**: 목표 Windows 구간의 움직임을 회복하고 인접 FULL/EMPTY·residue·반사 대조를 악화시키지 않는 근거가 있어야 한다. 출력량 증가, selected tracklet 생김, source provenance 통과만으로 완료 처리하지 않는다.

### D5. Foam front·episode 개선 — 독립 경로, 별도 비교

**1차 목표**: ENTRY-SPLASH 오인과 FOAM-LAYERED의 실제 front를 구분하고 POST-FOAM/DRAIN에서 잔류 흔적을 계속 Foam으로 읽지 않게 한다.

**구현 질문**

- material component의 bbox/면적이 아니라 실제 front를 지지하는 픽셀/column과 반대 근거가 무엇인가?
- 같은 component 안에 구조와 Foam이 섞였을 때 component 전체의 신뢰/불신을 front의 판정으로 전파하고 있지 않은가?
- raw candidate, pending, confirmed episode, final numeric 사이 어디서 오인이 생기는가?
- 안정된 실제 Foam layer를 살리면서 splash의 순간 motion·extent만으로 episode를 승인하지 않을 수 있는가?

**보존 조건**

- Oil이 UNKNOWN이어도 실제 Foam을 publish할 수 있어야 한다.
- 반대로 Foam 후보/마스크/잔류 seed가 Oil을 포괄적으로 veto하지 않아야 한다.
- 기존 bounded formation/stable-layer 요건과 same-frame Foam provenance를 유지한다.
- 672s 같은 truth 경계는 평가에만 쓰며 runtime switch가 아니다.

R20의 7개 pre-Foam 출력 중 일부는 current raw가 없고 나중에 episode 확정됐다. 그러나 post-672 증거가 그 확정에 필수였는지는 현재 자료로 모른다. 필요 시 같은 저장 입력의 bounded-prefix 대조로 확인하되, **이미 future leakage가 증명됐다고 쓰지 않는다.** [S7]

Oil 지원 변경과 Foam 변경은 각각 단독 ablation을 먼저 만들고 나중에 합친다. mac sample4의 한 component/몇 픽셀 수정에 이 작업을 축소하지 않는다.

### D6. 최종 Windows 실행과 기존 report 검토

**진입**: D3/D4의 해당 gate를 통과하고, 정확한 candidate runtime과 recipe·source identity·partition을 고정했을 때.

**출력**

- Windows 9개 구간 모두에 대한 실제 sampled coverage, valid numeric Oil/Foam, contiguous runs, 방향, wrong/missing run, owner/phase 전이.
- 실제 기존 HTML report 및 동일 결과의 CSV/trace. 새 report 스타일·smoothing을 비교 변수로 넣지 않는다.
- report만 본 사용자가 이해한 주요 동작과, 허용된 source comparison으로 확인한 결과.
- 개선한 구간과 남은 실패를 같이 명시. 미평가를 PASS로 바꾸지 않음.

**판독 질문**

1. 언제 Oil 계면이 나타나고, 어느 방향으로 움직이며, 다시 사라지는가?
2. Foam은 언제 생기고 사라지며 Oil 경계와 구분되는가?
3. 빠른 reversal/상승·하강을 다른 구조로의 jump 때문에 반대로 읽게 되지는 않는가?
4. 가득 차서 경계가 없는 것과 영상을 판독할 수 없는 상태를 혼동하지 않는가?

이미 report가 제공하는 source context·source sequence는 제품 산출물의 일부로 사용한다. 그러나 원본 영상만 보고 이해할 수 있었다는 사실을 detector 수치 개선으로 보고하지 않는다. **report 전체 이해도**와 **숫자 경로의 물리적 신뢰도**는 별도의 결과로 남긴다.

독립 판독자를 실제로 사용하지 않았으면 independent comprehension PASS라고 쓰지 않는다. Windows qualified 여부는 정확한 최종 runtime에 대해 기존 field acceptance owner가 결정한다.

---

## 8. 코드 수정 경계와 재사용 계획

아래 “예정” 파일은 아직 구현되지 않은 제안이다. 새 파일을 만드는 것보다 기존 소유자 확장을 우선하고, 같은 기능의 두 번째 owner를 만들지 않는다.

| 소유 경계 | 현재 코드/도구 | 다음 변경의 원칙 |
|---|---|---|
| 기존 W3 손실 readout | `tests/diagnostics/s11_candidate_loss_audit.py` (delivery) | D1에서 그대로 재사용; 모델/영상 실행 없음 |
| Raw candidate evidence | `oil_candidate_evidence.py`, `OilCandidateEvidenceIndex` | 현재 missingness/정규화 보존; 새 diagnostic을 기존 input처럼 위장하지 않음 |
| Authority | `oil_candidate_authority.py::evaluate_candidate_authority` | D4a의 유력 연결점; early candidate-only 조건의 원인을 먼저 확인 |
| 후보 준비·retention | `oil_observation_resolver.py`의 admission 준비 경로 | candidate 생성, hard invalid, retention을 분리; top-k 무조건 확대 금지 |
| Physical tracklet | `oil_interface_tracklets.py` | 강한 현재 identity와 temporal correspondence 구분; ID 복사 금지 |
| Material phase | `oil_phase_lifecycle.py`, `OilPathLifecycleOwner` | D4b 별도 gate; inferred FULL 제거부터 시작하지 않음 |
| Selector/대표 member | `oil_interface_selector.py::build_interface_layers` | 동일 row에서도 representative 선정이 별도 seam임을 유지; upstream 배제는 여기서 못 고침 |
| Projection | `OilResolutionProjectionOwner` | 선택된 같은 프레임 후보 Y만 출력 |
| Foam | `foam_front_detector.py`, `foam_material_identity.py`, `foam_episode_resolver.py` | D5에서 front 지지와 component/episode 역할 분리 |
| Oil/Foam 합성 | `observation_sequence_resolver.py` | Oil→Foam 단일 합성 및 독립성 유지 |
| Shadow 평가 | 기존 W3 target evaluator / `s11_target_truth.py` | 기존 의미·분모·binding 재사용; 별도 손작성 정확도 계산기로 대체하지 않음 |
| H-ROLE prototype (예정) | 예: `tests/diagnostics/s11_boundary_role_shadow.py` | D2 설계 고정 뒤에만 생성; production import 금지 |
| Episode 의미 평가 (예정) | 기존 결과/validation에 bounded 비교를 추가 | 기존 report를 재작성하지 않으며 truth로 수치를 보정하지 않음 |

현재 selector는 `_phase_admitted`와 publishability를 통과한 후보 중 row hypothesis별 representative를 만든 뒤 allowed owner, bounded competition 등을 적용한다. 따라서 **후보 존재 → authority → tracklet → row representative → owner 허용 → 최종 선택**을 하나의 “검출 성공/실패”로 축약하면 수정 위치를 잘못 고르게 된다. [S11]

### 8.1 H-ROLE sidecar의 최소 정보 계약 — 제안, 현행 schema 아님

| 필드 묶음 | 최소 내용 |
|---|---|
| provenance | source/case/frame/Glass, candidate input identity, source/Y, witness hash, model/spec hash |
| geometry | native/center 구분, 실제 X/Y support, mask/clipping/occlusion, missing 이유 |
| 물리 판정 | 실제 경계 / 비경계 / unresolved / unavailable를 원래 review와 분리 |
| 제품 역할 | target / internal boundary / other non-target / unresolved; Foam 역할 별도 |
| 공간 근거 | 지지 영역과 반대 영역의 정확한 연결, 같은 신호의 derivation lineage |
| 국소·scalar 품질 | 부분 path agreement, scalar usable 여부; 없는 scalar truth는 NOT_MEASURED |
| 제한 | 적용 가능 조건, 보류 이유, model ambiguity; production authority는 없음 |

새 enum 문자열을 기존 production schema가 지원하는 것처럼 쓰지 않는다. 실제 구현 단계에서 기존 typed witness/target evaluator와 호환되는 명시적 version을 선택한다. Broad physical review는 원본으로 남기고 target projection과 추론 결과를 각각 별도 artifact로 저장한다.

---

## 9. 필수 양면 대조와 반증 매트릭스

| 실제/구성 상황 | 보호해야 할 결과 | 이 대조가 막는 잘못된 개선 |
|---|---|---|
| 정지한 실제 계면 / 같은 모양의 정지 구조 | identity를 motion 존재만으로 결정하지 않음 | 정지 계면 전부 삭제, 구조를 smooth track으로 승격 |
| 부분적으로 보이는 계면 / 한 sector의 강한 반사 | 실제 지지와 반대 영역을 각각 보존 | max로 반사 승인, median으로 부분 계면 삭제 |
| 동일한 supplied 관측에 다른 물리 해석 가능 | unresolved, 보이는 프레임 분모 유지 | 임의 tie break 또는 label 누설 |
| 2·3개 실제 유체 경계 / 그 위의 반사 | target과 internal을 구분 | min-Y 후보를 target으로 선언 |
| 상부 target 가림 / 하부 내부 경계만 보임 | 하부를 target 대체재로 쓰지 않음 | coverage를 위한 identity 교체 |
| FULL 계속 유지 / 실제 계면 재등장 | 앞에서는 null, 뒤에서는 증거 기반 admission | H1/H1b와 같은 barrier 이완 |
| 실제 rapid refill / top 구조·rim | 상승 후 소실을 닫고 새 구조로 이동하지 않음 | 같은-owner 가정으로 가짜 후속 관측 |
| entry splash / 실제 layered Foam / wall residue | 독립된 Foam front/episode 구분 | 밝기·한 번의 motion·면적 변화만으로 Foam 승인 |
| 영상 불량·유효 mask 부족 / 진짜 missing boundary | unavailable와 no-interface를 구분 | missing을 깨끗한 재료 또는 FULL로 간주 |
| 큰 실제 excursion / 틀린 먼 구조 | 실제 excursion은 유지하고 구조 오추적은 보류 | jump 크기나 smoothness만으로 오류 제거 |
| 같은 Y의 다른 member / 중복 representation | 정확한 identity·lineage 보존 | proximity를 truth나 독립 투표로 전환 |
| native polarity 반전 / exposure 변화 | 물리 정체성을 임의로 바꾸지 않음 | signed contrast를 재료 교체로 해석 |

Synthetic fixture는 구조적 계약과 불가능성을 확인한다. 실제 Windows의 구별 성능이나 independent holdout을 대신하지 않는다. False publication만 줄고 target support도 사라진 경우를 “안전해졌으니 성공”으로 닫지 않는다. [S11][S12]

---

## 10. 단계 전환, 중단 조건, 작업 예산

### 10.1 의존 관계

```text
D0 완료
  ├─ D1: 기존 Windows audit의 제한된 기록 질의
  └─ D2: 역할/대조군/구체 알고리즘 계약 설계
          ↓ 필요한 물리 대조·partition 확보
       D3: frozen shadow + 반사실 비교
          ↓ O2 acceptance
       D4a: support/admission (W5/O3)
          ↓ 별도 phase/owner 설계 및 gate
       D4b: 재획득·closure (W6/후속 단계)

D5 Foam: Oil과 별도 설계·단독 비교 → 해당 gate 뒤 통합
D6: 정확한 최종 runtime의 Windows 9구간 + 기존 report → field 판정
```

D1의 원본이 없다는 이유로 문서·fixture 작업까지 멈출 필요는 없다. 반대로 D2의 설계만 끝났다고 Windows physical identity나 O2를 통과한 것은 아니다.

### 10.2 작업이 끝나는 지점을 사전에 고정한다

| 상황 | 종료/분기 |
|---|---|
| closed selector/terminal/cellular 규칙의 실행 완료 | 그대로 종료 유지; threshold 변형으로 continuation하지 않음 |
| 기록 질의가 원인을 더 좁히지 못함 | 정확한 missing field만 명시하고 D1 종료; 반복 inventory 금지 |
| 지지·반대 관측이 본질적으로 동일 | 가설 반증/범위 제한; 추가 label로 inference 정보를 창조하지 않음 |
| Mac 한 구간만 개선, 다른 source에서 광범위한 잘못된 경로 생성 | generic replacement 기각 |
| 잘못된 값을 없앴지만 중요한 운동도 사라짐 | context 개선 실패 |
| 일부 짧은 오류가 남으나 주요 운동·전환이 더 정확히 전달됨 | 부분적 제품 개선으로 기록 가능; 독립적인 field 승격 기준은 별도 |
| 다수 장면·phase를 고치려면 한꺼번에 여러 owner 수정 필요 | identity/support, phase, Foam으로 패치 분리 |
| 새 descriptor가 입력 구별력을 추가하지 않음 | 추가 구현 중단; 다음 필요한 observable을 명명 |

업무량의 중심은 D2–D5 detector 근거·행동 검증이어야 한다. 출처 고정과 문서 정리는 이를 지원하는 수준에 머문다. **추가 dashboard, report 스타일 개편, 새 범용 audit framework, 반복 라벨링 도구 재작성은 이번 계획에서 제외한다.**

---

## 11. 재현 및 다음 실행 명령

### 11.1 기존 Windows audit의 제한된 질의

다음은 **delivery에서 제공되는 기존 reader**의 명령 형식이다. main에 파일이 없으면 delivery의 그 파일을 검증된 복사본으로 가져온다. 전체 dependency 설치 없이 실행하도록 만들어진 도구다.

```powershell
py -3 tests/diagnostics/s11_candidate_loss_audit.py `
  --audit <기존-W3-experiment.json> `
  --expected-sha256 ba5fe04b28473f70387e363ef7d40077f559c80b1852755d997e1dd04171937f `
  --output <존재하지-않는-새-output-directory>
```

위 hash는 첫 W3 원본 audit 전용이다. 다른 artifact에 적용하지 않는다. 경로는 실제 Windows 위치로 대체해야 하는 명시적인 placeholder이며, 이번에 실행한 명령이 아니다.

### 11.2 이번에 실행한 focused tests

delivery를 `git archive`로 새 ignored 디렉터리에 풀고, 동일 프로젝트 venv 및 archive의 `PYTHONPATH=src:.`에서 실행했다.

```sh
python -m pytest -q \
  tests/unit/test_s11_candidate_loss_audit.py \
  tests/unit/test_s11_saved_detection_replay.py \
  tests/unit/test_s11_shadow_targets.py \
  tests/unit/test_s11_target_truth.py \
  tests/unit/test_oil_phase_identity_diagnostics.py \
  tests/unit/test_oil_phase_lifecycle.py \
  tests/unit/test_oil_observation_resolver.py \
  tests/unit/test_foam_episode_resolver.py \
  --junitxml=../focused-contracts.xml
```

결과: **294 passed in 29.52s**. 환경 복사/해결 과정까지 포함한 전체 소요와 test runner의 시간을 혼동하지 않는다.

### 11.3 실제 구현 후 요구할 검증

현재 계약의 full non-Qt / 별도 bounded Qt, 네 영상 official windows, detector governance 및 문서 link/whitespace, 해당 Windows shadow/behavior 절차를 변경 범위에 따라 수행한다. 이번 focused PASS를 그 검증의 대체 증거로 재사용하지 않는다.

```sh
python3 scripts/check_detector_governance.py --base-ref <구현-base> --include-worktree
git diff --check
```

Qt/A0Q의 기존 불확실성은 별도 현안이다. 이 문서의 주 detector 가설을 해결한 것처럼 닫지도, 관련 없는 UI 검증을 detector 연구의 무한 선행 조건으로 늘리지도 않는다.

---

## 12. 기존 문서·계획과의 관계

| 기존 소유 문서/증거 | 본 명세서의 관계 |
|---|---|
| `docs/00-project/work-plan.md` | 현재 execution 상태 owner 유지. 본 문서는 다음 항목을 등록할 제안이며 main 상태를 자동 변경하지 않음 |
| `docs/00-project/roadmap.md` | S11 목적·단계 체계 유지; 별도 장기 프로젝트로 분기하지 않음 |
| canonical Windows reviewed truth | 9개 구간·물리 의미 최상위. historical detector 결과로 수정하지 않음 |
| passive control review / target-truth binding | 완료된 target 의미·binding 재사용; prediction 검증만 별도 |
| interface witness architecture/validation | O2→behavior→field gate 유지. 새 역할 가설은 해당 설계·검증 owner에 명시적으로 연결 |
| Windows-first terminal / LabPics closeout | negative result와 reusable reader만 재사용; rejected behavior는 부활시키지 않음 |
| cellular basin / selector closeout | 최근 실험 완료 증거. 다음 단계는 해당 fixed ranking의 continuation이 아님 |
| source context / episode review 설계 | 이미 반영된 report를 평가 매체로 재사용; UI 개편 제외 |
| failure registry / logic map | 수정 위치와 no-repeat 계약 owner. 새 원인·실행 경로가 확인될 때만 갱신 |

다음 구현의 기록은 설계, 실행 결과, acceptance를 나눈다. main Work Plan에 별도 브랜치 실험 상태를 반영할 경우에도 `CLOSED WITHOUT PROMOTION`과 실제 적용 여부를 그대로 적는다. 설계 제안이 자동 승인 또는 main 채택으로 읽히게 작성하지 않는다.

---

## 13. 다음 작업자의 제출물과 완료 판정

### 13.1 최소 제출물

1. **설계 및 입력 manifest**: 구체 H-ROLE/owner 가설, 반례, 역할·partition, operating point, 필요한 소스 경계.
2. **검증 bundle**: 원본 불변 증거, shadow predictions, W3 평가, 변경 단계별 차이, 9개 Windows 구간 중 평가한 범위와 미평가 구분.
3. **비교 결과 및 인수인계**: 기존 report 기준의 맥락 개선/악화, 실제 적용 commit, 유지 실패, rejection/rollback 경로.

### 13.2 완료 상태를 세 단계로 구분한다

- **설계/도구 완료**: 입력·join·계약·실행이 검증됨. detector 효과는 미입증일 수 있다.
- **국소 detector 개선**: 특정 episode의 잘못된 운동 해석이 줄고 중요한 관측이 보존됨. Windows/holdout 미평가를 명시한다.
- **현장 채택 가능**: 정확한 runtime이 현재 acceptance를 통과하고, Windows 9구간 및 기존 report에서 유용성이 확인됨.

이번 문서와 294개 테스트는 첫 범주다. 최근 handoff도 종료된 실험·검증 도구의 전달이지 개선 detector 채택이 아니다. 현재 **FIELD FAIL을 그대로 유지한다.**

---

## 14. History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: Windows W3 recorded funnel/context, passive target binding, R20 transferred field consolidation, H1/H1b terminal contradiction, LabPics fixed ranking, cellular basin/extent/boundary, selector permutation, current authority/selector source and relevant failure entries.
- Prior mechanisms rejected: global material/texture rank, phase-cap relaxation, motion/source/track/height-only identity, truth-driven candidate substitution, same-Y label transfer, interpolation/carry, all-abstain success, repeated closed reviews.
- Preserved contracts: exact same-frame numeric provenance, independent Oil/Foam ownership and validity, coordinate-free FULL/EMPTY, bounded ambiguity/unavailability, immutable truth and evidence, no private-case behavior, O2/behavior/field separation.
- Difference from prior failures: first locate the recorded loss seam; separate physical identity, product target role and scalar usability before admission; evaluate selective false-track suppression and true-target recovery separately against episode context, not global rank or raw output count.
- Logic-map impact: NONE — 이번 산출물은 계획·증거 검토이며 executing production owner나 control flow를 변경하지 않았다. 향후 D4/D5 구현 때 실제 경로 변경을 해당 owner에 반영해야 한다.
- Failure-registry impact: NONE — 기존 실패군에 대한 설계 우선순위를 정했을 뿐 새로운 Windows 최초 원인이나 성공한 repair를 주장하지 않는다.

## 15. Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: sample4의 최근 saved selector 실험에서는 f1200 목표가 retained refs 이전에 없고 f1260/f1320은 authority/tracklet 단계에서 selector에 도달하지 않는다. 그보다 이른 f1200 원인 및 private Windows의 최초 물리적 실패는 이번 검토로 확정하지 않는다. Windows W3의 admitted-row/unselected는 allowed owner·대표 member·ambiguity·suppression을 구별하지 못한다.
- Logic-map impact: NONE — 새 diagnostic 파일과 이미지 확인은 ignored audit 디렉터리에서만 수행했고 생산 코드·main·recipe·truth를 바꾸지 않았다.
- Failure-registry impact: NONE — 인수인계 무결성과 테스트/영상 대응을 확인했으나 새 field failure class나 detector efficacy를 확정하지 않았다.

---

## 16. 고정 출처와 검증 산출물

### 16.1 출처 레지스터

`M = 49c6d3aebeaf90aea96cd5be4c0e91115011f5a7`, `D = e5d4a0430ea69beab59736396a2817c09b5efd69`.

| ID | 출처 | 본 문서에서 사용한 범위 |
|---|---|---|
| S1 | 첨부 `HANDOFF.md` (2026-10-08) | 종료 상태, branch/base/delivery/main, 복구·재실험 금지 경계 |
| S2 | D: `docs/60-evidence/s11/2026-10-08-cellular-selector-closeout.md` 및 JSON companion | 7개 member join, 4개 paired selector 결과, 검증 범위 |
| S3 | M: `docs/00-project/work-plan.md`, `roadmap.md` | live 상태, 기존 report 채택, O2/W4·A0Q 등 분리 |
| S4 | M: `docs/60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md` | Windows 73개 candidate의 transferred funnel/context, 한계 |
| S5 | M: `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` | canonical 9구간, source-Y·ordering·미평가 계약 |
| S6 | M: `docs/60-evidence/s11/s11-o2-passive-control-review-001.md`의 최신 완료 절 | target 정의, 75개 batch의 10/3/62 역할, Windows binding 완료 |
| S7 | M: `docs/60-evidence/s11/s11-r20-windows-evidence-consolidation.md` | 역사적 R20의 broad impact와 확인 불가 항목. 현재 main 실측 아님 |
| S8 | M: `sample/README.md`, hash가 일치한 4개 영상·recipe·truth | source 범위, 설명선·blur·reframing, truth 역할과 local qualification window |
| S9 | D: `docs/20-architecture/s11-cellular-basin-shadow-design.md` | 종료된 cellular 변형의 frozen 계약과 selector 제한 |
| S10 | D: `docs/60-evidence/s11/2026-10-08-windows-first-detector-closeout.md`; `tests/diagnostics/s11_candidate_loss_audit.py` | H1/H1b/LabPics 실패와 기존 Windows readout 재사용 |
| S11 | M: `docs/20-architecture/s11-current-detector-logic-map.md`; `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md`; `oil_candidate_authority.py`, `oil_interface_selector.py` | 실제 owner, authority·representative·selector 경계, 금지된 과거 메커니즘 |
| S12 | M: `docs/30-validation/s11-interface-observability-witness-validation.md`; `s11-detector-change-governance.md` | O2/behavior/field, 대조군·partition·missingness·governance |
| S13 | 이번 local audit `sample/output/s11-next-plan-audit-20261008-001/` | 872개 무결성, 12개 pin, 36프레임, 7 crop equality, 299행 field 비교, 294 tests |

### 16.2 현지 저장 위치와 중요한 hash

로컬 저장소:

```text
/Users/sunjaekim/Developer/oil_level_tracker
```

검토한 handoff ZIP:

```text
sample/output/s11-spatial-identity-20261008-001/
  s11-spatial-identity-handoff-2026-10-08.zip
SHA-256: b9c08d8e9449f1f180826b1bc690a6d26162731a7e2588753e1c3240c26d046e
```

이번 ignored audit:

```text
sample/output/s11-next-plan-audit-20261008-001/
  review_source_frames.py
  source-review-receipt.json
  *-fresh-contact.png
  fresh-f*-bgr.png
  delivery-snapshot/
  focused-contracts.log
  focused-contracts.xml
  verify_plan_inputs.py
  initial-byte-check.json
  compare_saved_samples.py
  observer-invariance-review.json
  finalize_audit.py
  verification-summary-final.json
```

`verification-summary-final.json` SHA-256:

```text
73692f779bd422f884591d78c14bea6225cd1026a03503995e6273950ab73deb
```

이 문서와 함께 제공하는 `S11-next-work-verification-2026-10-08.json`은 tool 결과를 정리한 **별도 공유용 요약**이다. 위 현지 receipt의 byte-identical 복사본이라고 주장하지 않는다. 원본 영상·crop·환경·cache는 공유용 문서에 포함하지 않는다.

### 16.3 남겨야 할 불확실성

Windows private 영상·원본 packet·전체 audit JSON을 이번에 직접 읽거나 실행하지 않았다. 다른 recording의 independent role/holdout 준비 여부도 확인되지 않았다. 새 H-ROLE 분류기, 새 operating point, 새 admission 행동, 현장 성능은 아직 없다. 원본 프레임 확인과 계약 테스트가 보여 주는 것은 **다음 실험을 정확히 설계할 근거와 실행 기반**이지, 성공한 detector가 아니다.

**다음 단계의 기준은 명확하다. 더 많은 선을 그리는 것이 아니라, 실제 계면·Foam의 운동을 더 정확하게 이해하게 만드는 detector 변경을 하나씩 증명한다.**
