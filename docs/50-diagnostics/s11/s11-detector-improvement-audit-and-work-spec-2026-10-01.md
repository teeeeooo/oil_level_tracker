# Oil Level Tracker detector 개선 감사 및 작업 명세서

- 작성일: 2026-10-01 KST
- 감사 대상: `teeeeooo/oil_level_tracker`
- 기준 커밋: `85a01cdf4e3385b51422cf0da675a03a74ab70a7`

문서 성격: 기준 커밋에 대한 감사 결과와 후속 작업 제안. 현재 architecture, validation, work-plan의 승인 상태를 이 문서만으로 변경하지 않는다.

## 1. 최종 판단

**현재의 제한된 관측층 재설계 방향은 유지하는 것이 타당하다. 전면 재작성이나 대형 영상 AI로의 즉시 교체를 뒷받침하는 근거는 없다. 다만 다음 단계의 중심을 같은 세 프레임의 점수 조합에서, 평가 목표와 부분 경로 집계의 정합성 및 실제 시간 구간에서의 효용 검증으로 옮겨야 한다.**

지금까지의 작업은 헛수고가 아니다. 후보와 원영상 좌표의 연결, identity와 path review의 분리, 라벨 이력 보존, 동일 support 비교, 원본 보존, 자동 결과 생성이 상당히 잘 구축됐다. 최신 실험 구현도 이 감사에서 재현됐다. 그러나 그 기반이 좋아졌다는 사실과 production detector가 현장에서 좋아졌다는 사실은 다르다. 현재 승인된 동작은 R22이며, R22-3은 관측용 sidecar를 추가한 상태다. 최신 커밋의 `--identity-profile`은 offline 탐색 실험이고 Windows 결과는 아직 대기 중이다. [현재 상태][R01] [최신 실험][R02]

가장 중요한 새 발견은 **정답의 의미와 집계 목표가 어긋날 수 있다는 점**이다. 인간은 경로 일부가 틀려도 실제 계면을 대표하는 후보를 `interface`로 판독한다. 그런데 실험은 여러 경로점의 점수를 중앙값으로 줄여 후보 identity를 평가한다. review-002의 candidate 10은 실제로 `off / near / off`이면서 `interface`다. 따라서 후보 순위 실패만 보고 “특징량에 정보가 없다”고 결론 내릴 수 없다. 실제 scorer를 이용한 합성 반례로 이 가능성을 확인했다. [부분 경로 판독][R07] [라벨 의미][R08] [점수 집계][R09]

권고 순서는 다음과 같다.

1. 이미 구현된 identity-profile을 현재 입력으로 한 번 실행하고 제한된 가설 검증으로 종결한다.
2. 후보 identity, 경로 부분의 적합성, 최종 scalar 높이의 유효성을 각각 정의하고 집계 목표를 맞춘다.
3. 결과에서 확인한 특정 공백에 한해 SPL#1 내부의 작은 장면 묶음을 판독한다.
4. 기존 관측량과 구조물 문맥을 재사용하는 challenger 한 개를 비교한다. 필요한 경우에만 새로운 광학 신호를 검토한다.
5. 실제 shadow 출력의 오류와 관측 빈도를 함께 평가하고, O2 수용에 필요한 적법한 자료 분할·operating point·독립 검증을 O3 이전에 완료한다.
6. 이후에만 support/association, handoff/phase를 순서대로 통합하고 현장 구간 전체를 검증한다. 독립 자료가 아직 없으면 탐색 결과를 보존하고 통합 gate는 대기로 둔다.

`FIELD FAIL`은 유지한다. 이 감사에서 production detector를 수정하거나 현장 성능 개선을 승인하지 않았다.

## 2. 감사 범위와 증거의 강도

### 2.1 확인한 기준 상태

| 항목 | 확인 결과 |
|---|---|
| 사용자 지정 SHA | `85a01cdf4e3385b51422cf0da675a03a74ab70a7` |
| Mac checkout HEAD와 origin/main | 모두 지정 SHA와 일치 |
| 감사 시작 상태 | clean, modified 0, untracked 0 |
| 저장소 목록 | tracked 692개; `src/` Python 213개, `tests/` Python 223개, `docs/` Markdown 212개 |
| 현재 production 동작 | R22 Oil ownership/evidence replacement |
| 현재 진단 runtime | `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1` |
| 최신 커밋의 변경 | offline identity-profile 실험, 관련 테스트와 문서 6개 |
| 현장 상태 | 기존 Windows 보고에 따른 FIELD FAIL; 최신 profile 현장 실행 대기 |

전체 파일 목록으로 범위를 파악한 뒤 S11의 입력·관측·후보·identity·association·phase·선택·출력 경로와 관련 절차를 추적했다. 692개 파일 모두를 한 줄씩 검토했다는 의미는 아니다. UI/패키징의 무관한 세부 구현은 이번 성능 개선 감사의 상세 범위에 포함하지 않았다.

### 2.2 실제 검토한 책임 경로

| 영역 | 주요 검토 대상 | 감사 방식 |
|---|---|---|
| 현재 권한과 목적 | AGENTS, S11 skill, work-plan, execution-policy, docs router, product SSOT | 현재 owner와 역사 자료 구분 |
| 기존 실패 | logic-map 인덱스 및 관련 노드, F01–F10, R23 기각과 연결된 진단 | 동일 실패의 재도입 여부 |
| 관측 추출 | `phase_frame_detection.py`, `oil_interface_diagnostics.py`, `oil_interface_witness.py`, `oil_material_path.py` | 값의 정의, caller, sidecar 경계, scalar 축약 |
| production 결정 | `oil_observation_resolver.py`, `oil_interface_tracklets.py`, `oil_phase_lifecycle.py`, selector 및 연결 경로 | 후보에서 publication까지 권한 추적 |
| 현장 증거 | O2 review 001/002/003, comparison, fixed-score, reversal follow-up, locality, inventory, local evidence | 전사된 사실·추론·미검증 항목 구분 |
| 평가와 기록 | `s11_shadow_experiment.py`, `s11_interface_shadow_evaluation.py`, `s11_review_records.py` | 집계·분모·support·입력 연결·원본 보존 |
| 검증 | 최신 evidence 지정 6개 focused suite, 독립 수학 oracle, 집계 반례, governance | 지정 HEAD 직접 실행 |
| 외부 근거 | 액면 영상인식 원논문, 압축기 혼합물 발포 연구, 광학 제조사, 선택적 예측·분할 검증 자료 | 원문 및 공식 자료와 전이 한계 확인 |

### 2.3 이번에 직접 검증한 것과 검증하지 못한 것

**직접 확인:** Git 정체성, 현재 코드와 문서, 164개 focused test, profile 수학 계산, artifact fingerprint, 합성 집계 반례, production과 offline 실험의 분리.

**저장소에 남은 사용자 보고로 확인:** Windows의 review revision과 candidate/path 판독, fixed-score/ablation 결과, 해당 PC에서의 receipt 및 입력 해시 보존. 원본 private JSON과 영상을 여기서 독립 재실행한 결과가 아니다.

**아직 미확인:** 최신 identity-profile Windows 결과, 현재 전체 구간 검출률, 정량 contour 오차, independent-recording 일반화, 최신 후보의 Windows 처리속도. 원영상·라벨·상세 trace를 업무 PC 밖으로 옮겨 이 공백을 메우지 않는다.

## 3. 제품 목표와 현재 단계의 재정렬

### 3.1 목표는 충분히 자주 올바른 유면을 관측하는 것이다

제품 SSOT는 완전 무인 판정 대신 시험자의 판독을 정량적으로 보조한다고 정의한다. pixel-perfect Y보다 유면 하강·상승·정체·최저점·회복을 읽을 수 있는 관측 빈도와 시간 분포를 우선할 수 있지만, 구조물이나 반사를 계속 따라가는 gross wrong-interface는 허용하지 않는다. [제품 목표][R03]

그러므로 다음 세 항목을 함께 만족해야 개선이다.

- 실제로 보이는 계면을 더 자주 올바르게 관측한다.
- 긴 오추적과 관측 공백을 줄여 흐름·최저점·회복을 더 잘 드러낸다.
- 보이지 않는 계면, FULL/EMPTY, Foam 부재 구간에 숫자를 만들지 않는다.

MAE만 줄이기 위해 대부분을 보류하거나, coverage만 늘리기 위해 구조물을 채택하는 결과는 목적에 맞지 않는다. 현재 rank 실험은 이 최종 목적의 일부를 조사하는 단계다.

### 3.2 최근 진행의 정확한 의미

`cfed402..85a01cdf`의 34개 커밋을 분류하면 문서/정책만 변경한 커밋 26개, 테스트·진단 도구를 변경한 커밋 8개다. source 변경을 포함한 것은 O1 관측 sidecar 구현 1개이며 이 1개는 테스트·도구 변경 분류에도 포함된다. O1 커밋 `4840d79` 이후 target까지 `src/` diff는 없다.

이는 최근 작업이 성능이 입증된 detector 반복 개정이 아니라 **측정과 평가를 신뢰할 수 있게 만드는 연구 준비 및 가설 실험**이었다는 뜻이다. 문서 커밋의 수만으로 낭비를 판정할 수는 없다. 다만 수동 전사와 후속 보고의 오류를 정리하던 단계는 끝내고, 한 실험이 다음 결정을 낼 수 있도록 절차를 압축할 시점이다.

### 3.3 단계별 현재 상태

| 단계 | 현재 확인 수준 | 아직 주어지지 않은 권한 |
|---|---|---|
| O1 typed extraction | 로컬 accepted; trace-only, lineage/geometry/availability 보존 | 실제 계면 판정 |
| O2 fixed-score와 locality | Windows 실행 보고 완료; mixed/negative 결과 | calibrated classifier, production admission |
| O2 identity-profile | 구현·로컬 검증 완료; Windows 대기 | 구조물과 실제 계면 확정 구분 |
| O2 calibrated shadow | 실제 모델과 operating point 미완성 | O3 행동 통합 |
| O3 support/association | 제안 단계 | 물리적 owner 변경 |
| O4 handoff/phase | 별도 후속 제안 | 초기 FULL 또는 fill/drain 조건 완화 |
| O5 field qualification | 미충족 | FIELD PASS |

R22-3 witness는 debug projector의 sidecar에 기록되며 현재 authority/tracklet에 입력되지 않는다. 관측 실험이 좋아져도 production 결과가 저절로 좋아지지 않는다. [O1 구현 경계][R08] [debug caller][R10]

## 4. 현재 자료가 말해 주는 것

### 4.1 라벨과 독립 표본 수

아래는 최신 active revision 3/14/4에 대한 저장소의 전사 보고를 합산한 것이다.

| Review | 장면 | 전체 후보 | interface | non_interface | unreviewed |
|---|---|---:|---:|---:|---:|
| 001 r3 | BASE f11508, 보이는 계면 없음 | 23 | 0 | 23 | 0 |
| 002 r14 | BASE f14386 | 23 | 6 | 2 | 15 |
| 003 r4 | Accum f16280 | 27 | 2 | 1 | 24 |
| 합계 | 세 프레임 | 73 | 8 | 26 | 39 |

후보 identity 판독은 34/73개이고, 39/73개인 약 53.4%는 미판독이다. 전체 native 위치 55개 중 near 15, off 12, unreviewed 28로, 명시적으로 판독된 위치는 27/55개다. interface 후보 소속 판독 위치도 near 15와 off 4를 함께 포함한다. candidate-center의 path review는 없고 세 contour 배열은 모두 비어 있다. 따라서 숫자 Y의 정확도는 미측정이다. [review 001][R11] [review 002][R07] [review 003][R12] [comparison][R13]

video inventory는 이 세 review의 현재 범위를 SPL#1 한 녹화로 기록한다. review-002/003의 동일 recording-A는 명시적이다. review-001의 실제 private group 문자열까지 여기서 읽은 것은 아니므로 그 세부 정체성은 Windows 보고 범위로 유지한다. [녹화 inventory][R14]

**73개 후보, 55개 위치, 수십 개 pair는 독립된 수십 장면이 아니다.** 특히 002의 identity 12쌍은 여섯 positive와 두 negative의 조합이다. 같은 프레임의 glare·광학 조건·후보를 재사용한다. public probe의 91개도 13프레임 × 7변형이며 91개의 독립 현장 사례가 아니다.

### 4.2 현재 fixed-score 결과

각 셀은 `correct / reversed / tie / unscorable`이다. 아래 숫자는 Windows 전사 보고이며, without-locality의 BASE 숫자는 저장소에 명시된 전이 결과로부터의 파생값이다.

| 후보 identity 비교 | Contrast | Alignment | Combined | Without locality |
|---|---|---|---|---|
| BASE review-002, 12쌍 | 6 / 6 / 0 / 0 | 0 / 12 / 0 / 0 | 5 / 7 / 0 / 0 | 3 / 9 / 0 / 0, 파생값 |
| Accum review-003, 2쌍 | 1 / 1 / 0 / 0 | 2 / 0 / 0 / 0 | 2 / 0 / 0 / 0 | 기존 순서 변화 없음 |

locality 제거는 BASE same-X 위치 비교 두 쌍을 개선했지만 후보 identity 두 쌍과 structural negative control 두 쌍을 악화했다. 즉 위치를 더 잘 구분하는 점수가 물리적 identity도 더 잘 구분한다는 보장은 없다. 늘어난 support에서 새로 계산 가능한 위치가 생겼다는 사실도 정확도 향상이 아니다. [고정 점수 결과][R04] [locality 결과][R05]

review-001은 negative만 23개 있으므로 “positive보다 낮게 순위를 매겼다”는 평가 자체가 없다. operating point가 없으면 이 장면에서 전부 보류할 수 있는지도 알 수 없다. review-002의 기존 top 후보 1/15 등 미판독 후보는 정답도 오답도 확정할 수 없다.

### 4.3 public 후보 recall의 올바른 해석

13개 usable public truth 프레임에서 7개 photometric 조건 모두 truth 8px 이내 후보가 있었다. 동시에 프레임당 후보 중앙값은 23–24개, truth 근처 후보는 3–4개였다. 이는 public set에서 후보 부족보다 구별·선택 문제가 중요하다는 근거다. 모든 private 구간의 후보 recall이 충분하다는 증거는 아니다. [관측 validation V0][R06]

## 5. 핵심 감사 발견

우선순위의 P0는 다음 설계 결정을 내리기 전 해결할 항목을 뜻한다. 현재 offline 실험에서 production 사고를 일으키는 bug가 확인됐다는 의미가 아니다.

### A01 P0  후보 identity와 부분 경로 중앙값의 목표 불일치

**관찰:** candidate 10은 holistic `interface`지만 native 세 점이 `off / near / off`다. 기존 score와 새 profile은 scale median 후 preferred point median을 사용한다. 라벨 owner는 후보 identity가 모든 path point의 정확성을 인증하지 않는다고 명시한다. [R07] [R08] [R09]

**재현:** 실제 `score_candidate()`와 `evaluate_case()`를 사용한 합성 예에서 interface 후보의 위치별 이상적 local score가 `[0, 1, 0]`, negative가 `[0.1, 0.1, 0.1]`이면 후보 중앙값은 0과 0.1이다. identity 순위는 reversed지만 interface 내부 near/off 비교 두 쌍은 correct다.

**의미:** local signal이 올바르게 동작해도 holistic candidate 순위는 실패할 수 있다. 실제 profile이 near/off 분류기라는 전제나 실제 Windows 실패 원인 확정은 아니다. descriptor 정보 부족, 잘못된 샘플링 geometry, support 변화, pooling 목표, 동일 광학 구조를 구별해야 한다.

**필요 조치:** W1에서 identity·local support·scalar publication의 계약을 분리한다. 기존 라벨을 median에 맞게 수정하지 않는다. 즉시 max나 상위 quantile로 바꾸지도 않는다. 고립 glare 한 점이 후보 전체를 통과시키는 반대 실패를 함께 다뤄야 한다.

### A02 P0  순위 실험을 실제 판정으로 바꾸는 단계가 아직 없다

**관찰:** 현재 script는 calibrated decision을 내지 않으며 별도 schema다. “가장 높은 후보”는 no-interface 장면에도 존재한다. evaluator는 후보 decision과 선택적 interval을 받을 수 있지만 독립적인 predicted near/off 출력 계약은 없다. [R02] [R09] [R15]

**의미:** 후보 pair 정확도가 올라가도 실제 채택/거부율, visible-frame coverage, false publication은 계산되지 않는다.

**필요 조치:** W3에서 기존 evaluator를 확장하는 명시적 shadow 출력 계약을 정의한다. identity support, point localization, 최종 scalar 사용 가능성을 분리한다. 기존 qualitative path summary를 predicted localization classifier의 성능으로 보고하지 않는다.

### A03 P0  같은 세 프레임에서의 적응적 모델 선택

**관찰:** fixed-score, locality, profile이 동일 regression labels에서 이어진다. 코드가 라벨을 읽지 않고 점수를 계산하는 것은 좋은 통제다. 하지만 이전 라벨 결과를 보고 사람이 다음 공식을 선택하는 과정까지 독립 검증이 되는 것은 아니다.

**의미:** 이 데이터는 가설 반박과 회귀 확인에는 유용하지만 generalization, calibration 또는 untouched holdout의 증거가 아니다. 학습 라이브러리의 공식 지침도 test 데이터가 모델 선택에 들어가면 안 된다고 설명한다. [W08] [W09]

**필요 조치:** 현재 profile은 한 번의 제한된 검증으로 마친다. 추가 장면은 이름 붙인 공백을 해소할 때만 수집하고, 같은 녹화의 다른 구간을 independent-recording holdout이라고 부르지 않는다. SPL#2/3 보류와 기존 recording-group guard를 유지한다.

### A04 P1  정보 손실과 관측 불가능성을 혼동할 위험

**관찰:** 새 profile은 네 band 평균이 step/ramp/excursion 중 어느 형태에 가까운지 비교한다. 같은 네 평균을 갖는 구조물 step은 실제 계면과 동일하게 나온다. 이 반례는 기존 unit test에도 의도적으로 포함돼 있다. [R02] [R16]

**의미:** profile이 성공해도 실제 계면 확정은 아니고 실패해도 raw image 전체에 정보가 없다는 뜻은 아니다. band 평균 압축, vertical-normal 근사, mask clipping, far-band 결측, point pooling에서 정보가 손실될 수 있다.

**필요 조치:** 실패는 최소한 `measurement unavailable`, `geometry mismatch`, `aggregation mismatch`, `shape collision`, `identity cue insufficient`, `cause unresolved`로 분류한다. 이미 관측한 region/static/texture 문맥을 먼저 검토하고 실제 필요가 확인될 때만 descriptor를 확장한다.

### A05 P1  common support 비교는 잘 돼 있으나 전체 효용은 별도다

**관찰:** 방법 비교는 공통 scale/point에 제한하며 support 확장 결과를 분리한다. 이는 올바른 구현이다. 다만 공통 support는 각 후보 내부의 비교 가능성을 맞추는 것이며, 모든 후보가 동일한 visible footprint와 mask 품질을 갖는다는 뜻은 아니다. native가 있으면 측정 불가 시 center로 조용히 대체하지 않는 것도 현재 의도된 계약이다. [R09]

**필요 조치:** support가 줄어든 뒤 남은 쉬운 사례의 점수만 좋아진 것을 개선으로 세지 않는다. 후보·위치·scale·frame의 availability를 각각 보고하고, 모든 human-visible frame은 model abstention과 관계없이 coverage 분모에 남긴다.

### A06 P1  observation만 좋아져도 기존 owner와 phase에서 다시 막힐 수 있다

**관찰:** 현재 production에는 기존 scalar corroboration, tracklet, fill/drain admission이 남아 있다. R23 polarity-only association은 protected positive를 손상시켜 기각됐다. [R17] [R18] [R19]

**필요 조치:** O2 이후 identity 결과를 별도 sidecar 또는 raw dictionary로 여러 owner가 다시 해석하지 않도록 하나의 typed owner에서 소비한다. witness identity가 맞는지와 owner 연결이 맞는지, phase가 허용하는지, 최종 scalar가 맞는지를 순차 검증한다. sign·source family·Y 근접·motion만으로 identity를 부여하지 않는다.

### A07 P1  시간 구간의 효용을 아직 평가하지 못한다

**관찰:** 세 프레임은 entry, drain, rapid refill, layered Foam, post-Foam, reversal의 전체 동작을 대표하지 않는다. canonical truth에는 아홉 구간이 존재하고 모든 field report에 각각의 결과를 요구한다. [R20] [R21]

**필요 조치:** 후속 proof의 기본 단위를 프레임 pair에서 bounded episode로 올린다. long wrong run, longest gap, reacquisition, entry/minimum/recovery의 관측 여부를 함께 측정한다. exact Y가 없을 때도 presence·identity·방향·부재는 평가하고, 좌표 정확도만 NOT_EVALUATED로 둔다.

### A08 P1  전사 과정의 신뢰 경계와 반복 비용

**관찰:** comparison 이력에는 OCR 기반 코드 오판의 철회, 최대값/중앙값 복사 오류, normalized 값 전사 정정이 남아 있다. 최신 자동 JSON-to-summary 재생성으로 해당 조사는 닫혔다. 새 hash는 과거 파일이 바뀌지 않았음을 소급 증명하지 않는다. [R13] [R22]

**필요 조치:** 이미 닫힌 조사나 migration을 반복하지 않는다. 현장에서는 하나의 runner가 계산한 JSON과 summary를 사용하고, 밖에서는 허용된 동일 summary만 해석한다. source/hash·commit·recipe·revision·support를 한 execution record에 묶는다. canonical source companion의 fingerprint 미기재는 확인된 full local identity와 운영자 provenance로 좁게 정리하며 detector 재실행 사유로 삼지 않는다.

### A09 P2  일부 문서의 current-owner 링크가 오래됐다

**관찰:** `real-world-validation-plan.md:10`은 current detector gate를 R20으로, `s11-real-field-detector-effectiveness.md:7–22`는 current owner를 R21로 가리킨다. 최상위 work-plan과 docs router는 R22/R22-3 및 O2를 가리킨다. [R01] [R23] [R24]

**필요 조치:** 후속 문서 수정 시 current 링크를 work-plan 또는 현재 revision-neutral owner로 좁게 정정한다. 과거 evidence의 당시 상태를 최신 상태로 재작성하지 않는다. 이 링크 정리는 기술 실험의 선행 blocker가 아니다.

### A10 P1  측정 대상과 광학 조건을 성능 지표에 연결해야 한다

기존 SSOT의 `oil_air` 명칭과 실제 냉매/오일 혼합물, Oil/Foam 층의 물리적 경계를 혼동하지 않아야 한다. 실제 제품 의미는 기존 필드·Foam 분리 계약을 유지하고, review 지침에 “관측 가능한 액체 경계 또는 분리된 Oil/Foam의 하부 경계”를 명확히 설명하는 것이 우선이다. API 이름을 일괄 바꾸는 작업이 아니다. [R03] [R20]

혼합물의 감압·탈기는 실제 Foam을 만들 수 있으므로 모든 기포를 영상 noise로 취급할 수 없다. sight-glass 높이가 순수 오일 질량이나 윤활 충분성을 직접 측정한다는 주장도 이번 detector 범위에 포함하지 않는다. [W05]

## 6. 외부 기술과의 비교 및 선택

외부 논문의 성능 숫자를 이 압축기의 acceptance 값으로 옮기지 않는다. 아래는 채택 가능한 원리와 전이 한계다.

| 접근 | 원문 근거와 현재 적용 가치 | 한계와 결정 |
|---|---|---|
| 경계 상대 contrast, edge density, normal alignment | Eppel·Kachman은 투명 액면 후보를 여러 영상 속성으로 평가한다. [W01] | 현재 O1과 상당 부분 겹친다. 새로 동일 feature 세트를 만드는 작업은 불필요하다. |
| 부분 곡선/경로 | Eppel의 후속 연구는 영상 비용과 Dijkstra 경로를 사용한다. [W02] | 현재 native path를 먼저 평가한다. 끝점·연속곡선 가정을 만족하지 않는 장면에 경로를 강제로 만들지 않는다. 후보 recall/geometry 결함이 확인될 때만 challenger가 된다. |
| 구조물 reference | 액면과 동일한 형태의 반사/표시는 단일 이미지 형상만으로 확정 구분이 어려우며 empty reference나 다른 시점이 추가 단서가 될 수 있다. [W01] | 기존 static-artifact owner와 등록 품질을 먼저 확인한다. 정지한 실제 계면을 reference에 흡수하지 않는 통제가 필요하다. |
| 고정 노출·차광·확산광 | CCS 공식 사례는 광원 배치에 따라 표면 반사가 액면을 가리거나 액면이 더 잘 보이는 차이를 제시한다. [W03] | 제조사 사례는 압축기 성능 보증이 아니다. 외부 fixture에서 가능한 작은 비교를 권고한다. |
| 편광 | Edmund Optics는 편광으로 glare/hot spot을 줄이는 구성을 설명한다. [W04] | 계면을 드러내는 유용한 반사도 줄 수 있다. 실제 target/distractor 구별과 판독 가능 비율로 평가한다. |
| dedicated optical oil switch | BITZER와 KRIWAN은 적외선·광학 원리의 액면 감시를 제공한다. [W06] [W07] | 점위치의 액면 존재 감시는 연속 높이 추적과 다르다. 호환되는 기존 센서가 있다면 독립 검증 신호로 검토하며 제품의 delay를 tracker에 복사하지 않는다. |
| local segmentation AI | SAM 2 계열은 prompt 기반 영상 segmentation 및 판독 보조가 가능하다. [W10] | class-agnostic mask가 Oil identity를 보증하지 않는다. 우선 업무 PC 내부의 annotation 보조나 별도 challenger로만 검토한다. GPU를 production 필수로 만들지 않는다. |
| 보류를 포함한 평가 | SelectiveNet 등은 예측 오류와 coverage의 관계를 함께 평가한다. [W11] | 특정 신경망 도입 권고가 아니다. 기존 deterministic detector에도 같은 평가 원리가 필요하다. |
| 일반화와 confidence | 독립 group 분할과 dataset shift 연구는 익숙한 조건의 성능·calibration이 다른 조건을 보증하지 않음을 뒷받침한다. [W08] [W09] [W12] | 현재 score나 peak hull을 확률·신뢰구간으로 해석하지 않는다. |

**선택:** 현재 관측량과 owner를 재사용하는 제한된 개선을 1순위로 둔다. 구조물과 진짜 계면이 같은 표현으로 충돌하는 것이 확인되면 독립된 문맥이나 광학 관측을 추가한다. 학습 모델은 현장 데이터·평가계약·로컬 실행 조건이 준비된 뒤 같은 평가기로 비교할 대안이며, 지금 즉시 전체 detector를 대체할 근거는 없다.

## 7. 후속 작업 명세

이 절의 W0–W7은 제안된 실행 순서다. W0의 기존 pending 실험 이외에 새로운 실행, 데이터 수집, behavior 변경을 이미 수행했다는 의미는 아니다. 기존 recording-group guard, SPL#2/3 보류, Windows 내부 데이터 보존을 유지한다.

### W0  현재 identity-profile 실험을 변경 없이 종결

**목적:** sustained two-region 형태가 현재 reviewed identity 쌍을 stripe/ramp 대비 더 잘 정렬하는지 한 번 확인한다.

**입력:** review-001/002/003 active v2 revision 3/14/4, 기존 R22-3 packet, 최초 fixed-score v1 `experiment.json`. locality 결과를 reference로 바꾸지 않는다.

**실행:** 기존 `s11_shadow_experiment.py --identity-profile --reference ...`를 사용한다. 새 출력 폴더, 원본 receipt 확인, 현재 입력과 원래 v1 결과 재현, 전후 입력 해시 검증을 기존 운영 절차대로 수행한다. 새 라벨·freeze·영상 탐색·detector replay가 필요하지 않다. [R25]

**결과:** `experiment.json`, `summary.md`, `complete.json`. 새 결과는 `identity_profile[]` 아래의 두 view이고 최상위 기존 `scores/evaluation`은 v1 재현 자료다.

**수용 기준:** 실행이 정확히 완료되고 아래의 결정이 가능하면 이 탐색 실험은 종결된다. 탐색의 종결은 classifier acceptance가 아니다.

| 결과 유형 | 내릴 결정 | 다음 작업 |
|---|---|---|
| common support에서 일부 순위 개선 | 새 형태 가설의 제한된 지지; physical identity 확정 아님 | W1 목표/집계 확인 후 필요한 장면만 W2 |
| candidate identity 개선 없음 | 이 표현·geometry·집계 조합의 한계 | W1에서 원인 분해; 즉시 feature 추가 금지 |
| 새 필수 band 때문에 support 크게 감소 | applicability 문제를 별도 기록 | 결측 원인과 해당 optical/geometry 조건만 확인 |
| 동일 구조 step과 구별 안 됨 | 이미 알려진 식별 한계가 현실에서도 중요할 가능성 | W4의 구조 문맥/다른 관측 가설 검토 |
| unknown top 또는 일부 off path 때문에 해석 불가 | 효과 미확인 | 결정에 필요한 소수 대상만 W2에서 추가 판독 |
| reference/receipt/입력 정체성 오류 | 비교 실행 미성립 | 입력을 수정해 맞추지 말고 정체성만 복구 |

이 결과를 보고 동일 세 프레임에서 weight, sign, epsilon, template를 여러 번 바꾸는 반복은 하지 않는다. W0의 기존 출력은 이후에도 보존한다.

### W1  identity와 경로 support 및 scalar 높이 계약 정렬

**목적:** partial-path 후보를 수용하는 인간 정답과 model objective의 관계를 확정한다.

**변경 owner:** 현재 witness architecture의 O2 review semantics, witness validation, fixed-score diagnostic. 현재 v2 라벨과 기존 frozen 자료는 그대로 보존한다.

**필수 구분:**

| 층 | 질문 | 필요한 정답/출력 | 이 층의 성공이 보증하지 않는 것 |
|---|---|---|---|
| Scene | 계면을 관측할 수 있는가 | visible/no-visible/uncertain와 판독 문맥 | 특정 후보의 정답 |
| Candidate identity | 이 proposal이 실제 계면을 대표하는가 | 기존 holistic identity | 모든 path 점의 위치 정확도 |
| Local support | 특정 X·Y에서 실제 계면을 지지하는가 | point의 near/off/uncertain 및 필요시 contour interval | 후보 scalar Y의 정확도 |
| Scalar eligibility | 현재 후보의 최종 Y를 숫자로 사용할 수 있는가 | 독립 scalar truth 또는 정의된 contour-to-scalar 계약 | 다음 프레임에서도 같은 owner임 |
| Association/phase | 이전 관측과 같은 계면이고 현재 phase에 유효한가 | 시간 구간의 physical identity/transition | 관측이 없는 현재 frame의 좌표 |

**필수 통제 사례:** 완전한 path positive; 일부만 맞는 positive; 고립된 높은 glare 점을 가진 negative; 실제 정지 계면; 구조물과 교차하는 진짜 계면; missing native와 계산 가능한 center; 측정 일부가 잘린 mask; 같은 형태의 구조 step.

**설계 결과:** local evidence를 어떻게 candidate-level identity에 합칠지 이유를 명시한다. spatial support의 분포·연결성·반대 근거를 보존하는 구조를 먼저 검토한다. threshold나 집계 변경은 하나의 사전 명세된 challenger로 비교하며 labels를 이용해 inference 시점의 유효 sector를 선택하지 않는다.

candidate identity가 positive라도 final scalar Y가 off일 수 있다. 이 경우 O2에서는 `identity supported, scalar unusable/unknown`을 보고할 수 있어야 한다. production에서 support 점들의 평균으로 기존 candidate Y를 몰래 바꾸지 않는다. 향후 geometry를 수정하려면 같은 frame의 새로운 명시적 candidate와 생성 provenance를 upstream에서 만들어 별도 검증해야 한다.

**완료 기준:** A01 반례와 반대 glare 사례의 기대 결과가 모순 없이 정의되고, 동일 의미의 정답과 예측을 비교할 수 있다. 현재 profile 결과로 이 계약이 자동 승인되지는 않는다.

### W2  이름 붙인 공백에 한해 SPL#1 장면을 제한적으로 확장

**목적:** 개발 루프를 끝낼 수 있는 반례와 시간 문맥을 확보한다. 전체 영상 재라벨링을 목표로 삼지 않는다.

**기본 절차:** 기존 bundle/packet/record 도구와 저장 구조를 재사용한다. 먼저 원영상만 보고 계면의 가시성·물리적 대상·짧은 시간 문맥을 기록한 뒤 후보 overlay와 비교한다. detector가 제시하지 않은 계면도 scene truth에 남길 수 있어야 한다.

**권고 최초 예산:** 장면을 새로 요구할 필요가 생기면 6–9개 짧은 window, window당 3–5개 대표 프레임 정도를 상한 계획의 출발점으로 삼는다. 이는 통계적 충분 표본 수가 아니라 업무량을 제한하기 위한 제안이다. 빠른 refill·Foam transition의 시간 판독에는 해당 window를 연속으로 보고, sparse anchor만으로 지속시간 성능을 확정하지 않는다. 이미 충분한 기존 자료가 있으면 새 capture는 생략한다.

| 필요한 장면 | 막으려는 잘못된 결론 |
|---|---|
| 정지한 진짜 계면과 고정 구조물 | 움직이지 않으면 구조물이라는 규칙 |
| 부분적으로만 맞는 path와 고립 glare | median 실패를 feature 부족으로, max 성공을 identity로 해석 |
| weak/reversed contrast 계면 | 보편적인 밝기 부호 규칙 |
| FULL/EMPTY no-interface | top score를 자동 채택 |
| entry와 rapid refill | 강한 jump 제한으로 실제 변화 삭제 |
| Oil/Foam 분리와 post-Foam residue | Foam 상단·벽면 흔적을 Oil로 승격 |
| direction reversal | phase가 맞는 관측을 영구 차단 |

기존 미검토 top 후보를 추가 판독할 때는 전체 39개를 무조건 완료하지 않는다. 모델 간 선택이 달라지는 후보와 실제 채택 예정 후보를 우선하고, 선택한 이유를 남긴다. 이 능동 선택 자료는 hard-case 개발 자료다. 성능 추정을 위한 장면 선정에는 별도의 사전 고정된 시간/상태 기준을 적용해 어려운 사례만의 편향을 구분한다.

**partition:** 세 기존 review는 regression으로 유지한다. 같은 SPL#1의 새로운 window도 현재 guard에서 같은 recording group이다. 여러 새 frame을 만들었다고 holdout이 생긴 것이 아니다. SPL#2/3는 기존 결정대로 지금 선행 조건으로 요구하지 않는다. SPL#1 shadow 개선을 확인한 뒤, W5 이전의 O2 수용 gate에서 독립 자료의 필요 범위와 역할을 검토한다. 각 녹화의 실제 사용 이력을 먼저 확인하며 SPL#2/3를 자동으로 untouched holdout에 배정하지 않는다. [R14]

**완료 기준:** 선택한 가설의 positive·negative·partial·unresolved controls가 있고, 실제로 보이는 계면의 missing candidate도 분모에 남는다. 필요한 X에서만 사람이 contour interval을 추가한다. near/off 판독으로 정확한 Y를 역생성하지 않는다.

### W3  실제 shadow 결정과 평가를 기존 owner에서 완성

**목적:** ranking을 넘어 판정 보류를 포함한 사용 가능성을 평가한다.

**재사용:** `s11_interface_shadow_evaluation.py`의 packet/frozen/prediction join과 `s11_review_records.py`의 이력·revision 기능. `oil_decision_witness.py`의 기존 truth-linked 실패 funnel도 재사용한다. 해당 witness가 보존하는 authority·admission·row membership·selection을 연결해, 원후보 → 측정 → authority/top-k → association → phase allowed set → selector → publication 중 어디서 실제 후보를 잃었는지 기록한다. witness는 결정 사실을 직렬화하며 authority를 다시 계산하지 않는다. 새 labeling system, GUI, 병렬 trace framework는 만들지 않는다. [R29]

**출력 계약 제안:** 현재 candidate-level identity decision은 유지한다. 별도의 geometry-keyed predicted local support가 필요한 경우 prediction schema를 명시적으로 version-up하고 v1 호환을 보존한다. 최소 정보는 candidate input ID, witness hash, geometry basis, 정확한 X/Y, identity outcome, local outcome/interval, availability와 reason, model/spec/operating-point identity다.

**평가:** candidate identity confusion, point near/off confusion, scalar localization, frame coverage와 unknown을 서로 다른 분모로 계산한다. `uncertain`, `unreviewed`, missing prediction, abstention, unobservable을 합쳐 negative로 처리하지 않는다. 정체성이 판독된 accepted 후보만의 오류율은 조건부 지표이며 단독 수용 기준으로 사용하지 않는다. 기존 evaluator의 `verified_identity_precision`과 `conservative_supported_precision`을 함께 보고한다. 후자는 전체 supported 후보를 분모로 삼아 미판독 채택을 숨기지 않는다. Unknown은 오답으로 재라벨링하지 않지만 검증된 성공에도 포함하지 않는다. `supported_count`, `wrong_non_interface_support_count`, `unverified_support_count`와 verified visible coverage를 병기하고, 모델 간 판독 범위가 달라졌으면 성능 변화와 확인 범위 변화를 분리한다. [R15]

**operating point와 partition 계약:** 현재 evaluator는 비어 있지 않은 `fit_partitions`를 요구하고 `development`/`calibration`만 허용한다. SPL#1 regression 자료에서 탐색한 값은 별도 `EXPLORATORY_UNCALIBRATED` 진단 결과로만 남긴다. 이는 보고 상태의 제안이며 기존 prediction enum을 임의로 확장하는 뜻이 아니다. 기존 experiment 결과와 연결해 보존하고, `fit_partitions`를 사실과 다르게 적어 calibrated prediction으로 import하지 않는다. 기존 regression 자료를 development로 재라벨링하거나 recording-group guard를 완화하지 않는다. 현재 세 review나 13 public truth만으로 보편 threshold를 정하지 않는다. 적법한 development/calibration 자료에서 목적·오류 비용에 따라 operating point를 정하고 고정한 후 holdout에서 평가하는 절차는 W4 이후, W5 이전의 O2 수용 gate에서 완료해야 한다. [R15]

**완료 기준:** W3에서는 출력·평가 계약 구현과 통제 사례 및 탐색 결과의 평가까지 완료할 수 있다. calibrated O2 수용 완료와 구분한다. 모든 negative scene에서 강제로 top을 채택하지 않고, visible frame을 모두 보류하거나 미판독 후보를 주로 채택하는 결과도 좋은 모델로 통과시키지 않는다. 기존 v1 score result를 prediction schema로 이름만 바꿔 가져올 수 없다.

### W4  정보가 부족한 지점에 한 가지 challenger를 투입

W1/W2에서 원인을 확인한 뒤 아래 중 하나를 선택한다. 모든 접근을 동시에 개발하지 않는다.

| 관찰된 병목 | 우선 challenger | 필요한 양방향 통제 |
|---|---|---|
| 유효 local signal이 pooling에서 사라짐 | 부분 support와 반대 근거를 유지하는 candidate 집계 | partial positive와 isolated-glare negative |
| path가 계면을 잘못 샘플링 | 기존 native geometry와 별도의 offline local contour/normal 표현 비교 | curved/occluded positive와 strong structure |
| step 형태의 구조물과 진짜 계면 충돌 | 기존 static/region/texture 문맥의 명시적 결합 또는 등록 reference | 정지한 진짜 계면과 조명·진동으로 변한 구조물 |
| single frame은 애매하지만 짧은 sequence에서 구분 가능 | identity를 조건으로 하는 bounded temporal support | 실제 정지 계면, polarity reversal, crossing, gap |
| 사람이 현재 영상에서 판독할 수 없음 | 외부 광학 조건 비교 | 동일 운전 상태·고정 알고리즘 비교 |
| scene diversity 확보 후 수공 feature의 제한이 지속 | CPU 목표의 경량 학습 challenger | recording 단위 평가, abstention, 동일 runtime 비용 |

광학 비교는 먼저 카메라 고정·focus/노출·gain/white balance, 외부 차광, 확산 조명·입사각을 비교한다. 편광·배경 패턴·후면광은 광학 접근이 가능한 경우에만 확장한다. 단일 sight glass 뒤에 불투명 구조가 있으면 backlight/BOS가 성립하지 않을 수 있다. 압력 경계나 냉매 회로의 변경을 이 software 명세의 작업으로 포함하지 않는다.

**실험 고정:** 하나의 spec과 primary endpoint를 정하고 가설에서 의도적으로 바꾸는 변수를 선언한 뒤 나머지 비교 조건을 고정한다. 점수·집계 비교는 같은 input/geometry/runtime을 사용한다. Geometry 비교는 source frame·ROI·runtime과 평가 목표를 고정하고 geometry 변화와 그 영향을 기록한다. 광학 비교는 대응되는 운전 상태와 고정 detector를 기준으로 취득 조건의 차이와 반복 간 차이를 기록한다. matched-support와 expanded-support, 반례와 정지 조건은 결과 전에 정의한다.

**O1/O2 geometry 경계:** production 후보 inventory·geometry·결정의 equality를 유지한다. Geometry challenger는 동일 프레임에서 별도의 offline 진단 표현으로 먼저 생성하고, 독립 ID·변환·생성 provenance를 기록한다. 원래의 R22-3 packet·witness·reference·hash를 수정해 비교를 성립시키지 않는다. 기존 path judgment는 exact geometry에 묶여 있으므로 변경 경로에 자동 이전하지 않는다. 판독 범위별 대응을 확인하고 필요한 추가 판독을 거쳐야 한다. 실제 production candidate generation 변경은 별도의 upstream behavior 계획과 수용 조건을 충족한 후에만 적용한다.

새 support reference를 전체 평가 영상의 미래 frame으로 몰래 학습하지 않는다. 제품은 녹화 영상의 completed-window 분석이므로 시간 문맥 자체는 허용되지만, 모델·라벨·reference 각각이 본 시간 범위를 명시하고 동일 범위의 baseline과 비교한다.

**종료 기준:** 주요 오류가 감소하지 않거나 반대 controls에서 새 gross error가 생기면 해당 가설을 기각한다. 일부 conditional benefit만 있으면 적용 가능 조건과 missingness를 보고한다. 다음 descriptor를 계속 쌓기 전에 이번 가설에서 배운 원인을 한 문단으로 확정한다.

#### W4에서 W5로 넘어가기 전: O2 수용 gate

SPL#1의 제한된 shadow 개선이 확인되면 O3 이전에 다음을 완료한다.

1. 자료의 원본 recording group과 과거 모델 선택·판독·reference 사용 이력을 확인한다. 현재 regression을 그대로 보존하면서 development/calibration/holdout 역할을 적법하게 충족할 독립 자료를 확보한다.
2. 기존 architecture/validation owner에 적용 대상, acceptance 수치, operating-point 선택 자료와 선택 절차를 명시한다. 이 단계에서 SPL#2/3의 후속 사용 여부를 검토할 수 있지만 이미 보았거나 튜닝에 쓴 자료를 untouched라고 주장하지 않는다.
3. 모델·spec·operating point를 고정한 뒤 holdout 및 요구되는 Windows shadow 평가를 수행하고, unknown 포함 보수적 precision·visible coverage·구간별 실패를 함께 판정한다.
4. 충족된 근거를 current owner와 work-plan에 반영한 뒤 W5에 진입한다. 필요한 독립 자료가 없다면 탐색 결과와 구현을 보존하고 O2 수용 및 O3 진입은 pending으로 둔다.

이는 SPL#2/3를 지금 당장 요구하는 변경이 아니다. 기존 guard를 우회하는 available-corpus behavior 예외도 이 문서가 자동 승인하지 않는다. W7은 통합된 behavior의 최종 현장 검증이며, O2 선행 holdout을 처음 확보하는 단계로 미뤄 두지 않는다.

### W5  O3 support와 association을 별도 통합

**진입 조건:** 바로 앞 O2 수용 gate에서 자료 분할·operating point·validation/holdout/Windows shadow 기준을 충족하고 현재 work-plan이 O3를 실제 다음 단계로 지정해야 한다. SPL#1 rank 개선이나 W3 계약 구현만으로 진입하지 않는다.

**변경 owner:** `oil_observation_resolver.py`의 typed evidence/admission, `oil_interface_tracklets.py`의 association, 관련 selector 경로. 관측 결과는 하나의 불변 typed owner에서 전달한다.

**필수 검증:** same-frame provenance; partial contour agreement; hard-invalid peer 배제; 동일 current-RGB 계열을 여러 독립 표로 세지 않음; 정지 계면; 반사와의 crossing; polarity reversal; 진짜 계면이 후보에 있어도 잘못된 owner 때문에 막히는 경우; 충분한 근거가 없는 association의 unresolved.

복합 후보·tracklet에서는 실제로 기여한 member/sector와 hard contradiction의 provenance를 유지한다. 깨끗한 sibling의 높은 점수나 aggregate min/median/max가 모순된 member를 대신 인증하지 못하는 통제 사례를 넣는다. 기존 material-path veto와 R22의 typed/ordered contradiction 보호는 이미 있으므로, 이를 현재 전부 소실되는 결함으로 해석하지 않고 새 집계·통합의 회귀 보호로 사용한다.

**보존:** Oil/Foam 독립성, 같은 frame의 실제 후보에서만 숫자 선택, 모호함의 fail-closed, bounded history. 기존 corroboration을 우회하는 별도 점수 owner를 덧붙이지 않는다. 대체하는 규칙은 해당 구현 단계에서 명시하고 폐기 경로도 함께 검토한다.

### W6  O4 handoff와 phase를 각각 검증

**진입 조건:** W5가 물리적 identity와 연결을 입증했다.

**작업:** committed fill-owner handoff, fill 종료, drain 재진입, 초기 FULL 상태에서 보이는 계면을 받아들이는 phase 계약을 각각 작은 변경으로 다룬다. 기존 `oil_phase_lifecycle.py`와 현재 parent design을 따른다. [R17] [R19]

R23처럼 단일 polarity change를 association veto로 삼지 않는다. prior가 strong하다고 현재 관측을 영구 차단하지 않고, 시간 만료만으로 새로운 physical owner를 만들지도 않는다. phase 종료와 다른 identity로의 handoff는 별도 사실이다.

**완료 기준:** 각 변경에 양방향 synthetic controls, public 보호 관측, same-runtime 비교가 있으며 새로운 missing frame 숫자나 Foam 권한 침범이 없다. 최종 scalar Y가 잘못된 proposal이면 identity만 통과했다고 publication하지 않는다.

### W7  목적 중심 Windows qualification

**진입 조건:** 실제 behavior 후보가 확정되고 해당 검증 범위가 current owner로 지정됐다. current pushed SHA와 runtime을 고정한다.

**SPL#1:** canonical 아홉 구간 모두에 `PASS / FAIL / NOT_EVALUATED`를 보고한다. 정확한 Y anchor가 없는 경우 좌표 정확도만 미측정으로 남기고 presence/absence/identity/direction은 평가한다.

**독립 녹화:** W5 이전에 확보한 O2 검증 범위와 사용 이력을 이어받아 통합 behavior의 일반화를 평가한다. SPL#2/3는 SPL#1 shadow 개선 후 정한 후속 범위와 기존 보류 결정을 따른다. O2 결과를 보고 모델을 다시 선택했다면 해당 자료의 역할을 갱신하고 이를 다시 untouched라고 주장하지 않는다. 동일 녹화의 변환·crop·여러 Glass·재실행은 같은 group이다. 실제 unseen recording 수와 O2 이후 재사용 범위를 함께 적는다.

**검증 강도:** production/추출 경로를 변경할 때 해당 owner가 요구하는 full non-Qt와 Qt suite, 네 public video equality 또는 의도된 delta, runtime/메모리, target-Windows 동작을 수행한다. O1/O2 추출 변경은 exact behavior equality가 필수다. 의도된 behavior delta 허용은 해당 behavior 단계에서 별도로 수용한 변경에만 적용한다. offline consumer만 바꾼 작업에 매번 전체 detector replay를 요구하지 않는다.

## 8. 수용 지표와 판정 규칙

### 8.1 분모를 고정한 지표

| 지표 | 정의/분모 | 주요 해석 제한 |
|---|---|---|
| Proposal recall | 인간이 계면을 볼 수 있는 frame 중 허용 geometry 안의 후보가 하나 이상 존재한 비율 | 후보 identity 성공과 다르다. tolerance는 truth 품질에 맞춰 사전 정의한다. |
| Verified visible coverage | 인간이 볼 수 있는 frame 중 검증된 올바른 same-frame numeric observation이 있는 비율 | 모델이 unobservable이라 선언해도 해당 frame을 분모에서 빼지 않는다. |
| Accepted identity error / verified precision | 정체성이 판독된 accepted 후보 중 오답 비율 / 정답 비율 | 조건부 지표이므로 단독 gate로 쓰지 않는다. accepted-but-unreviewed 수를 반드시 병기한다. |
| Conservative supported precision | 기존 evaluator의 검증된 정답 supported 수 / 전체 supported 수 | unknown을 오답으로 재라벨링하지 않지만 분모에는 남긴다. scalar 유효성·visible coverage와 별개다. |
| No-interface false publication | 정답이 no-visible-interface인 frame에서 numeric Oil을 낸 비율 | FULL과 EMPTY를 분리한다. Foam 부재의 false episode도 별도다. |
| Localization | 독립 contour interval과 정확히 같은 X에서의 error, P90/P95, matched coverage | near/off를 px 값으로 바꾸지 않는다. 선택된 쉬운 sector만 보고하지 않는다. |
| Scalar error | 독립 scalar truth 또는 사전 정의한 contour-to-scalar target 대비 최종 candidate Y 오차 | candidate identity, native-point error를 scalar error로 대체하지 않는다. |
| Wrong-run duration | gross wrong identity를 연속 출력한 구간의 최대/분포 | 평균 frame error가 작아도 긴 구조물 추적은 별도 실패다. |
| Missing-run duration | human-visible interval 내 올바른 numeric이 없는 연속 시간 | sequence 경계와 sampling 간격을 기록한다. |
| Reacquisition / event timing | visible entry·가림 종료·회복 기준 통과 후 올바른 관측까지 시간, 놓친 이벤트 수 | exact source sampling과 판독 전이 시간의 오차를 반영한다. |
| Resource | debug off wall time, median/tail 처리시간, peak/장기 메모리, trace bytes | 다른 sampling/runtime/동시 실행끼리 speedup 비교 금지 |

독립 Y interval `[lo, hi]`를 사용하는 point error는 `max(lo-y, 0, y-hi)`처럼 interval 바깥 거리로 정의할 수 있다. 이는 제안된 명시적 오차 정의이며 annotation width, predicted interval width와 coverage를 함께 보고해야 한다. 구간을 넓혀서 오차만 낮추는 결과를 허용하지 않는다.

### 8.2 수치 목표를 임의로 발명하지 않는 구체적 gate

현재 세 프레임으로 “95% 검출” 같은 절대 수치를 정할 근거는 없다. 다음 절차로 실행 가능한 기준을 만든다.

1. 개발 전 baseline의 visible coverage, longest gap/wrong run, event 관측, runtime을 같은 입력에서 기록한다.
2. 해당 변화의 primary endpoint 한 개와 보호 endpoint를 사전 지정한다.
3. SPL#1 개선 주장에는 해당 endpoint의 명확한 개선과 다른 named segment의 새로운 gross wrong-interface/false-Foam 없음이 필요하다. support가 바뀌면 전체 eligible denominator 결과도 함께 본다. conditional precision만 좋아지고 미판독 채택이 늘어난 경우에는 통과시키지 않으며, conservative supported precision과 verified visible coverage를 함께 판정한다.
4. 최종 현장 gate에서는 canonical no-interface/empty/foam-absent 의미를 만족하고 아홉 구간 중 하나의 알려진 실패도 총평균으로 상쇄하지 않는다.
5. 허용 px 또는 mm 오차, 허용 gap·event delay, 최소 usable coverage는 실제 label 오차와 제품 판독 목적에 맞춰 개발 단계에서 수치화하고 holdout 전에 고정한다. 이 값이 미정이면 exploratory progress만 보고하고 qualification은 보류한다.

관측된 오류 0건은 모집단 오류율 0%를 증명하지 않는다. 현재 3프레임이나 서로 종속된 pair로 좁은 confidence interval을 만들지 않는다. 독립 구간·녹화가 충분해진 경우에만 cluster/recording 단위 uncertainty 분석을 추가한다.

### 8.3 반드시 지킬 실패 판정

- BASE 전체 reviewed interval에서 false Foam episode가 발생하면 실패다.
- FULL/EMPTY no-interface에서 구조물·glare를 numeric Oil로 채택하면 실패다.
- 눈에 보이는 실제 계면을 계속 놓친 결과를 모델의 `UNOBSERVABLE`로 제외해 통과시키지 않는다.
- 원본 후보가 없는 frame의 interpolation/carry/predicted Y를 numeric observation으로 출판하면 실패다.
- 성능 보고에서 일부 canonical segment, missing prediction 또는 unknown top을 감추면 평가 불완전이다.
- 동일 source-family, delta/normalized delta, 여러 scale을 독립 sensor vote로 세어 acceptance를 만들면 실패다.

## 9. 실제 구현 파일과 재사용 경계

아래 변경은 해당 W 단계에 진입한 뒤 적용할 위치다. 이번 감사에서 코드를 수정한 목록이 아니다.

| 파일/owner | 후속 역할 | 그대로 재사용할 부분 |
|---|---|---|
| `tests/diagnostics/s11_shadow_experiment.py` | W0 기존 실행, W1/W4 필요시 별도 명시된 aggregation challenger | 기존 modes, reference 재현, 동일 support, 불변 입력, 자동 summary |
| `tests/diagnostics/s11_interface_shadow_evaluation.py` | W3 identity/localization/scalar 평가 계약 확장 | packet/frozen validation, exact join, unknown 분모, version compatibility |
| `tests/diagnostics/s11_review_records.py` | W2 범위별 인간 판독 기록 | revision/hash/atomic save/history/bundle link; 병렬 label system 금지 |
| `src/oil_tracker/adapters/vision/oil_decision_witness.py` | W3의 truth-linked 실패 위치 연결 | 기존 authority/admission/selection 직렬화; 결정 재계산 금지 |
| `src/oil_tracker/adapters/vision/oil_interface_diagnostics.py` | 필요한 경우만 실제 측정 확장 | 기존 geometry, raw-gray/material/static prefix cache |
| `src/oil_tracker/adapters/vision/oil_interface_witness.py` | 필요한 경우만 typed local support 표현 보강 | immutable witness, availability, lineage, bounded storage |
| `src/oil_tracker/adapters/vision/oil_material_path.py` | geometry recall/scalar 결함이 확인되고 별도 behavior gate를 충족한 뒤 upstream proposal 검토 | W4 offline challenger와 구분; O1/O2 production equality; downstream 좌표 덮어쓰기 금지 |
| `src/oil_tracker/adapters/vision/oil_observation_resolver.py` | W5 typed support/admission | 단일 authority와 hard-invalid 보호 |
| `src/oil_tracker/adapters/vision/oil_interface_tracklets.py` | W5 physical association | bounded tracklet와 provenance |
| `src/oil_tracker/adapters/vision/oil_phase_lifecycle.py` | W6 handoff/phase | 현재 state evidence와 owner 경계 |
| 현재 architecture/validation/operations owners | 각 단계의 계약·실행·수용 기준 | 현재 문서 분류; evidence와 current state를 중복하지 않음 |

새 파일이 필요하면 위 owner로 책임을 수용할 수 없는 구체적 이유를 먼저 기록한다. 기존 관측 파이프라인과 똑같은 sidecar 계산기, 별도 comparator, 별도 라벨 편집기부터 만들지 않는다.

## 10. 현장 실행과 보고 절차 압축

### 10.1 W0 실행 예시

실제 Windows 경로는 기존 영구 데이터 위치를 사용한다. 아래는 운영 문서에 있는 호출 형태를 보여 주는 예시다.

```powershell
$pythonExe = ".\.venv\Scripts\python.exe"
$labelsOne = "D:\OilTracker\data\reviews\review-001\labels-v2.json"
$labelsTwo = "D:\OilTracker\data\reviews\review-002\labels-v2.json"
$labelsThree = "D:\OilTracker\data\reviews\review-003\labels.json"
$referenceExperiment = "D:\OilTracker\data\experiments\fixed-score-current-labels-001\experiment.json"
$profileOutput = "D:\OilTracker\data\experiments\identity-profile-001"
& $pythonExe tests/diagnostics/s11_shadow_experiment.py `
  --labels $labelsOne $labelsTwo $labelsThree `
  --identity-profile --reference $referenceExperiment --output $profileOutput
if ($LASTEXITCODE -ne 0) { throw "Identity profile failed; preserve inputs." }
```

실행 전 기존 reference 폴더의 complete receipt를 검증하고, 실행 후 새 schema/status/output hashes를 기존 운영 절차대로 확인한다. 현재 코드의 reference 동등성 검사는 이전 receipt의 역사적 생성 경위까지 자동 인증하지 않는다. [R25]

### 10.2 한 번의 결과 전달에 필요한 최소 내용

1. 코드 commit 또는 ZIP/실험 artifact의 full identity, runtime, 입력 revision, reference identity.
2. reference의 입력·점수·평가 동일성, COMPLETE 여부, 입력 보존 확인.
3. review별 common-support와 profile-supported 결과를 구분한 자동 표.
4. newly scorable/lost support와 결측 원인; top의 reviewed/unknown 상태.
5. 명명된 실패 후보에서 point → scale → candidate 집계를 추적한 최대 3개 예시.
6. 관찰된 사실, 가능한 원인, 아직 모르는 것을 나눈 결정 한 단락.

수치를 수동으로 다시 계산하거나 코드 사진을 OCR하여 별도 comparator를 만들지 않는다. 이미 확인한 migration, 과거 freeze/readiness, report 정정은 입력이 달라지거나 해당 근거를 사용하는 새 오류가 없는 한 반복하지 않는다. 작업 PC의 원자료와 history를 코드 ZIP 밖에 보존하는 기존 구조를 사용한다.

## 11. 독립 검증 기록

### 11.1 최신 focused suite 재현

| 항목 | 실행 결과 |
|---|---|
| HEAD | `85a01cdf4e3385b51422cf0da675a03a74ab70a7` |
| Python | 프로젝트 `.venv`, 3.14.4 |
| pytest / NumPy / OpenCV | 9.1.1 / 2.5.1 / 4.14.0 |
| 플랫폼 | macOS 26.6.2 arm64 |
| 결과 | 164 collected, 164 passed |
| pytest 시간 | 41.61 s |
| 파일별 수 | 22 + 42 + 34 + 32 + 21 + 13 |

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -p no:cacheprovider \
  tests/unit/test_s11_identity_profile.py \
  tests/unit/test_s11_shadow_experiment.py \
  tests/unit/test_interface_shadow_evaluation.py \
  tests/unit/test_s11_review_semantics.py \
  tests/unit/test_s11_review_records.py \
  tests/unit/test_oil_interface_witness.py
```

최신 evidence의 164개 scope를 이번에는 같은 head에서 한 번의 6파일 실행으로 재확인했다. `HEAD^` 대비 governance와 whitespace 검사도 통과했다. 이는 현재 offline consumer의 구현 검증이다. 현장 efficacy·full suite·Qt·public replay를 이번에 재검증했다는 뜻은 아니다.

### 11.2 artifact fingerprint

독립 재계산 결과가 최신 evidence와 정확히 일치했다.

```text
776c8639cd2ac39a7ed7c9a5833348c6339a390d95fc1a5830a0967b481f6519
```

이는 fingerprint에 포함된 코드·spec의 정체성 증거다. 실제 Windows checkout 전체나 private input 파일을 직접 검증한 증거로 확대하지 않는다.

### 11.3 독립 최소제곱 oracle

난수 seed `10101`로 만든 4-band profile 2,000개에서 기존 analytical offset/amplitude projection과 별도 `numpy.linalg.lstsq` 계산을 비교했다. SSE 최대 차이는 약 `2.22e-16`, 최종 score 최대 차이는 약 `8.33e-16`이며 모두 `1e-12` 안에서 일치했다.

현재 수식 구현에 계산 오류가 있다는 근거는 발견하지 못했다. 동일 gray profile을 갖는 구조물과 액면의 물리적 구별, partial-path pooling 문제는 이 수학 검증으로 해결되지 않는다.

### 11.4 이번 감사의 완료 범위

최신 코드·관련 절차·현재/역사 증거를 대조했고, 계산 및 focused 검증을 재현했으며, 후보 identity와 부분 경로 집계 사이의 대안 실패 원인을 확인했다. Windows private 원자료의 직접 검증과 후속 명세의 구현은 별도의 아직 수행되지 않은 작업이다. 이 문서는 현장 검출률을 새로 산출한 보고서가 아니다.

## 12. 다음 실행자가 바로 할 일

- 현재 커밋과 active revision 3/14/4 및 원본 v1 reference로 W0를 한 번 완료한다.
- 결과를 유지한 채 A01의 partial-path/identity 집계 해석을 확인한다.
- 해당 결과가 요구하는 최소 gap만 W1 계약과 W2 scene 목록에 연결한다.
- 한 가지 challenger와 primary endpoint를 사전 명세하고 기존 평가 owner에서 비교한다.
- SPL#1 탐색 결과를 calibrated prediction으로 위장하지 않고, O3 이전에 적법한 자료 분할·operating point·O2 독립 검증 gate를 완료한다. 필요한 자료가 없으면 이 gate는 pending으로 보존한다.
- O2, O3, O4, O5의 권한을 나누고 기존 FIELD FAIL을 성급히 승격하지 않는다.

전면 재작성, 반복 threshold sweep, 전체 라벨 재생성, SPL#2/3 즉시 개방, 과거 R23 재실행은 현재 결론에서 요구되지 않는다.

## 13. 근거 목록

### 저장소 근거

아래 링크는 모두 감사 기준 SHA에 고정된다. line anchor는 인용한 핵심 지점이며, 최신 branch가 이후 바뀌더라도 이 감사의 근거는 고정된다.

| ID | 근거 |
|---|---|
| R01 | [Current Work Plan][R01] — 현재 candidate, FIELD FAIL, pending profile, 기존 제약 |
| R02 | [Fixed-score experiment specification][R02] — profile 가설과 구조 step 한계 |
| R03 | [Product SSOT][R03] — 판독 보조, coverage와 gross identity 목표 |
| R04 | [First Windows fixed-score result][R04] — reviewed pair 결과와 unknown |
| R05 | [Windows locality result][R05] — improvement/regression과 파생 WL 수치 |
| R06 | [Witness validation][R06] — public 13프레임과 단계별 수용 |
| R07 | [Windows review-002][R07] — partial path와 holistic interface |
| R08 | [Witness architecture][R08] — O1 실제 정의, v2 review semantics, O2–O5 |
| R09 | [Offline score implementation][R09] — 집계, support, reference, profile |
| R10 | [Debug witness caller][R10] — production에서 sidecar 경계 |
| R11 | [Windows review-001][R11] — no-visible-interface, 23 negatives |
| R12 | [Windows review-003][R12] — Accum r4 positive/negative/path |
| R13 | [Windows comparison record][R13] — 전사 정정, 73 proposals, 55 native points |
| R14 | [Video inventory][R14] — SPL#1 범위와 SPL#2/3 보류 |
| R15 | [Shadow evaluator][R15] — labels/predictions/identity/localization |
| R16 | [Identity-profile tests][R16] — structure tie와 shape 계산 controls |
| R17 | [Rejected R23 investigation][R17] — polarity-only association 기각 |
| R18 | [Current logic map][R18] — 현행 executing owner |
| R19 | [Physical interface repair proposal][R19] — support/association/handoff 분리 |
| R20 | [Canonical Windows reviewed truth][R20] — 아홉 구간의 의미 |
| R21 | [Current Windows qualification][R21] — 실제 field acceptance 실행 |
| R22 | [Score reversal follow-up][R22] — 정체성·support·보고 해석 경계 |
| R23 | [Real-world validation plan][R23] — 제품 지표와 stale current link |
| R24 | [S11 umbrella validation][R24] — 지속 오추적·Foam·source-review oracle |
| R25 | [O2 Windows operations][R25] — 현재 identity-profile 실행 절차 |
| R26 | [Latest local identity-profile evidence][R26] — 164 scope와 artifact hash |
| R27 | [Mechanism failure registry][R27] — F01–F10 및 재도입 금지 |
| R28 | [Detector governance][R28] — 이 문서와 후속 변경의 검사 계약 |
| R29 | [Existing decision witness][R29] — truth-linked authority/admission/selection 직렬화 |

### 외부 원문과 공식 자료

웹 확인일: 2026-10-01 KST. 특정 제품 구매나 논문의 성능 수치 전이를 권고하는 목록이 아니다.

| ID | 출처 | 이 명세에서 사용하는 근거 |
|---|---|---|
| W01 | [Eppel & Kachman, 2014][W01] | 액면 주변 feature와 §6.2의 동일 형상 반사 구별 한계 |
| W02 | [Eppel, 2015][W02] | 제약된 경계 경로와 endpoint 가정 |
| W03 | [CCS BCBL 공식 조명 사례][W03] | 반사와 액면 가시성이 조명 조건에 의존 |
| W04 | [Edmund Optics 편광 기술문서][W04] | glare 저감 원리와 광학 비교 |
| W05 | [Fortkamp et al., Purdue ICEC 2012][W05] | 냉매/오일 감압과 발포의 실제 물리 과정 |
| W06 | [BITZER OLC-K1 공식 설명][W06] | 적외선 액면 감시와 기동/운전 조건 분리 |
| W07 | [KRIWAN Level Monitor 공식 설명][W07] | optical single-point measurement의 범위 |
| W08 | [scikit-learn grouped/time-dependent validation][W08] | 동일 recording group의 종속성과 분할 |
| W09 | [scikit-learn common pitfalls][W09] | 모델 선택에 test 정보를 사용하는 leakage |
| W10 | [Meta SAM 2 공식 설명][W10] | prompt/correction, annotation 보조 및 시간적 안정성 한계 |
| W11 | [SelectiveNet, ICML 2019][W11] | 보류를 포함한 risk–coverage 평가 개념 |
| W12 | [Ovadia et al., NeurIPS 2019][W12] | dataset shift에서 calibration의 한계 |

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-PROPOSAL`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R22 ownership and R22-3 extraction; public candidate probe; corrected BASE/Accum reviews; rejected R23 polarity association; fixed-score/locality/profile experiments; current evidence, partition and publication contracts.
- Prior mechanisms rejected: global threshold or polarity repair, motion/source-family identity, arbitrary candidate-Y changes, private coordinate branches, stale owner carry, downstream interpolation, unpartitioned model selection and reclassification of unknown labels as negatives.
- Preserved contracts: generic detector across Glass identities, exact same-frame numeric candidate provenance, independent Oil/Foam ownership, fail-closed ambiguity, bounded resource use and separate Windows qualification.
- Difference from prior failures: this audit distinguishes candidate identity, partial-path support, final scalar eligibility and sequence ownership; it tests target/aggregation consistency before expanding descriptors and requires bounded falsifiable experiments.
- Logic-map impact: NONE — this document audits the fixed current head and proposes staged work without changing production control flow or adding a runtime owner.
- Failure-registry impact: NONE — the partial-path aggregation counterexample is an evaluation-design risk, not a newly established private production cause or an accepted detector repair.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PROJECTION`, `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: the reproducible new counterexample first fails at offline candidate aggregation versus holistic identity evaluation; the first harmful stage in each private field sequence remains bounded by existing reviewed evidence and is not inferred from this synthetic control.
- Logic-map impact: NONE — this is an audit and proposed work specification; no detector, resolver, score tool, label, or output owner was changed by the audit.
- Failure-registry impact: NONE — no claim of new physical failure causality or FIELD PASS is made; existing failure classes and current acceptance remain authoritative.

[R01]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/00-project/work-plan.md
[R02]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/50-diagnostics/s11/s11-o2-fixed-score-experiment.md#L222
[R03]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/rotary_oil_level_tracker_ssot_spec.md#L65
[R04]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/60-evidence/s11/s11-o2-fixed-score-windows-run-001.md#L21
[R05]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/60-evidence/s11/s11-o2-locality-ablation-windows-run-001.md#L21
[R06]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/30-validation/s11-interface-observability-witness-validation.md
[R07]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/60-evidence/s11/s11-o2-windows-review-002.md#L147
[R08]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/20-architecture/s11-interface-observability-witness-architecture.md
[R09]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/tests/diagnostics/s11_shadow_experiment.py#L92
[R10]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/src/oil_tracker/adapters/vision/phase_frame_detection.py#L788
[R11]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/60-evidence/s11/s11-o2-windows-review-001.md
[R12]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/60-evidence/s11/s11-o2-windows-review-003.md
[R13]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/60-evidence/s11/s11-o2-windows-review-comparison.md
[R14]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/60-evidence/s11/s11-o2-video-inventory.md
[R15]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/tests/diagnostics/s11_interface_shadow_evaluation.py#L399
[R16]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/tests/unit/test_s11_identity_profile.py
[R17]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/50-diagnostics/s11/s11-r23-native-polarity-rejection.md
[R18]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/20-architecture/s11-current-detector-logic-map.md
[R19]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/20-architecture/s11-physical-interface-evidence-repair-design.md
[R20]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md
[R21]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/40-operations/s11-current-windows-field-qualification.md
[R22]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/60-evidence/s11/s11-o2-fixed-score-reversal-followup.md
[R23]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/30-validation/real-world-validation-plan.md
[R24]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/30-validation/s11-real-field-detector-effectiveness.md
[R25]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/40-operations/s11-o2-local-shadow-evaluation.md#L148
[R26]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/60-evidence/s11/s11-o2-identity-profile-local.md
[R27]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md
[R28]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/docs/30-validation/s11-detector-change-governance.md
[R29]: https://github.com/teeeeooo/oil_level_tracker/blob/85a01cdf4e3385b51422cf0da675a03a74ab70a7/src/oil_tracker/adapters/vision/oil_decision_witness.py#L65
[W01]: https://arxiv.org/pdf/1404.7174
[W02]: https://arxiv.org/abs/1501.04691
[W03]: https://www.ccs-grp.com/products/series/334
[W04]: https://www.edmundoptics.com/knowledge-center/application-notes/optics/introduction-to-polarization/
[W05]: https://docs.lib.purdue.edu/icec/2049/
[W06]: https://www.bitzer.de/shared_media/html/at-170/en-GB/820181899877320459.html
[W07]: https://www.kriwan.com/en/products/level-monitor
[W08]: https://scikit-learn.org/stable/modules/cross_validation.html
[W09]: https://scikit-learn.org/stable/common_pitfalls.html
[W10]: https://ai.meta.com/blog/segment-anything-2/
[W11]: https://proceedings.mlr.press/v97/geifman19a.html
[W12]: https://proceedings.neurips.cc/paper/9547-can-you-trust-your-models-uncertainty-evaluating-predictive-uncertainty-under-dataset-shift.pdf
