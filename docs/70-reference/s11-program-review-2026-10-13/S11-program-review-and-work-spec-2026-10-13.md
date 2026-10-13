# S11 전반 검토 · Detector 재설계 및 작업 명세서

작성일: **2026-10-13**  
검토 기준: `badf7caddebc7e75013ef02c888d2b72f13feb92`  
저장소: `teeeeooo/oil_level_tracker`  
문서 상태: **검토 완료 / 후속 설계 제안 / 생산 구현·승격 아님**

> 목표는 검출률 100%가 아니다. 사용자가 report로 Oil 계면과 Foam의 변화 방향, 주요 전환, 회복 및 관측 공백을 이해하도록 하는 것이다. 맥락을 바꾸지 않는 국소 오류는 허용하지만, 높은 검출 비율로 잘못된 극값이나 거품 사건을 정당화하지 않는다.

이 문서는 10월 12일 CR1 결과에 10월 13일의 판정 정정, 공개 압축기 전이, 미세·대립자 Foam 비교, 최신 handoff까지 반영한다. 현재 실행 권한과 단계 상태는 기존 `docs/00-project/work-plan.md`가 계속 소유한다. 아래 제안은 그 문서를 자동으로 대체하거나 새 실험·학습을 승인하지 않는다.

근거 표기 `[R01]`–`[R18]`은 부록의 **기준 커밋·원본 경로·SHA-256**에 연결된다. `[A01]`은 이번 읽기 전용 재검산, `[A02]`는 이번 native 특징 의존성 시험이다. 수치 원문은 함께 제공한 `S11-evidence-audit-2026-10-13.json`에 있다.

---

## 1. 결론과 우선순위

**전체 detector를 다시 만드는 대신, 현재 후보의 물리적 역할을 판단하는 관측 계층과 Foam의 component-to-front 축약부를 제한적으로 재설계한다.** 기존 경로 생성·추적·상태 전이·report는 재사용한다. 단순 유사도, threshold, episode 완화, 새 UI를 다음 주력 과제로 삼지 않는다.

우선순위는 다음 순서다.

| 우선순위 | 해결할 문제 | 사용자에게 생기는 이득 | 하지 않을 일 |
|---|---|---|---|
| 1 | 구조물·내부 무늬를 Oil로 채택하여 중요한 극값을 만드는 문제 | 유면이 크게 떨어졌다가 급상승했다는 잘못된 해석 억제 | 변화량 필터로 급격한 실제 refill까지 제거 |
| 2 | 실제 Oil 후보의 admission/continuation 손실 | 상승·하강·반전·회복의 흐름 보존 | 모든 공백을 보간하거나 이전 Y로 채우기 |
| 3 | Foam 내부를 상단으로 축약하고 실제 상단을 raw 단계에서 잃는 문제 | Foam의 존재·상단 변화·관측 종료를 구분 | raw가 틀린 상태에서 episode 조건부터 완화 |
| 4 | 통합 detector가 Windows 9개 구간과 report 판독에 주는 변화 확인 | 실사용 판독 보조 가치 확인 | 공개 영상의 좋은 결과를 FIELD PASS로 대체 |

**후속 관측의 권고 방향은 ‘native 경계에 연결된 양측 역할 관측’이다.** 추가적인 물리 역할 정보 없이 같은 R/L 유사도에 조건을 덧붙이는 것은 권고하지 않는다. 역할 지도 정보가 필요한 경우에는 기존 구간·영역 판정을 정밀도를 유지한 약한 감독 정보로 활용하는 작은 task-specific head를 별도 연구 범위로 제안한다. 모델 학습은 현재 승인된 고정 encoder 실험의 연장이 아니므로, 별도 범위 채택 전에는 실행하지 않는다.

이 방향의 유효성은 아직 입증되지 않았다. 이번에 확정한 것은 **문제의 위치, 버려야 할 반복 경로, 재사용할 구현, 다음 실험의 입력·출력·대조·중단 조건 및 통합 순서**다. 새 분류기가 이미 성공했다고 주장하지 않는다.

## 2. 이번에 실제로 확인·실행한 범위

### 2.1 저장소와 증거의 현재성

시작 시 작업 트리는 clean이었다. 최신 기준 HEAD는 `badf7ca…`이며, 오늘 완료된 material-role handoff까지 포함한다. 10월 11일 저장된 기본 실행과 비교한 **생산 Python 파일 221개의 SHA-256이 모두 일치**했다. material-side preflight의 **142개 입력/source pin도 모두 일치**했다. 샘플4 MP4의 SHA-256 역시 현재 sample 문서와 일치한다. 따라서 보존된 기본 실행은 이 기준 코드의 결과를 이해하는 데 직접적인 근거다. 다만 새 환경에서 전체 앱을 다시 실행한 결과는 아니다. [A01, R12, R13, R17]

### 2.2 직접 검토한 영상 기반 산출물

샘플4의 주요 후보 비교, 49.5초 사용자 정정 표시, 공개 압축기의 Foam/Oil 상·하단 표시, 미세 Foam R·대립자 Foam L 원본 패치, 샘플4 report 그래프, 원본 시간–높이 이미지, source sequence 미리보기와 관측 중단 캡처를 직접 보았다. 저장 CSV 및 events와 대조했다.

이는 **원본 영상에서 보존된 프레임·영상 요약·report를 검토한 것**이다. 모든 MP4를 이번 세션에서 전체 재생하거나 모든 프레임을 육안 판독한 것은 아니다. beer/milk와 Windows에 관한 물리적 판단은 기존 검토 근거를 사용했다. sample3은 재개방하지 않았다. [A01]

### 2.3 이번 세션의 검증

| 실행 | 이번 결과 | 의미와 한계 |
|---|---|---|
| material-side 단위 시험 재실행 | **9 passed / 1.12 s** | 해당 계산 계약 검증. 전체 detector 회귀나 물리 정확도 시험 아님 |
| 관리 실행 보존 상태 검사 | **14 runs / errors 0** | 기존 관리 실행 closeout 정상 |
| 142개 material 입력/source pin | 변경 0 | 고정 증거 보존 확인 |
| 221개 생산 source pin | 변경 0 | 저장 기본 실행 이후 생산 코드 불변 확인 |
| native 특징 의존성 canary | 실행 완료 | §5의 특징 footprint 해석 검증. detector 개선 증명 아님 |
| 새 encoder inference / 학습 | **실행하지 않음** | 닫힌 실험을 재시도하지 않음 |
| 전체 영상 replay / Windows | **실행하지 않음** | 실사용·field 결과를 새로 만들지 않음 |
| 생산 코드·Recipe·truth 변경 | **없음** | baseline과 사용자 작업 보존 |

## 3. 프로젝트 전반의 상태

### 3.1 이미 쌓인 기반과 아직 해결되지 않은 것

| 영역 | 현재 판단 | 다음 작업에서의 취급 |
|---|---|---|
| 데스크톱 분석·검토·내보내기·재실행 흐름 | S1–S10 완료 기반 | 재사용. S12 UI 확대를 앞당기지 않음 |
| report의 원본 맥락·관측 공백 설명 | 이미 반영된 개선 | 새 report를 만드는 대신 detector 변경의 효과를 이 report로 평가 |
| 후보·native 경로·lineage 추적 | 상당 부분 구현·증거 확보 | 별도 후보 프레임워크를 다시 만들지 않음 |
| Oil 물리 역할 및 authority | 실제/구조/내부 무늬를 구분할 근거 미충족 | 주력 개선 대상 |
| Foam 독립 raw upper | 실제 상단이 component 축약에서 사라지는 증거 존재 | raw 관측/역할 판별부터 수정 |
| CR1 | 정보적 유용성은 일부 확인, 역할 선택·정책 보정 미완료 | 보존하되 생산 gate로 쓰지 않음 |
| O1 | 로컬 수용 | 관측·lineage 기반 재사용 |
| O2 / W4 | **OPEN** | 물리 관측 계약·shadow·V5가 남음 |
| Windows | **FIELD FAIL 유지** | 통합 후 9개 canonical segment로 재평가 |
| Local XY | **OFF 유지** | 이번 설계에 끼워 넣지 않음 |
| R23 / S11-M / S12 | 아직 진입하지 않음 | 단계 이름을 먼저 바꾸지 않음 |

근거: [R01–R07, R16]. 로컬 시험 수나 완료된 문서 개수로 S11 진행률을 백분율화하지 않는다.

### 3.2 현재 정체의 성격

정체는 단순한 ‘edge 부족’이나 ‘추적기가 약함’ 하나로 설명되지 않는다. 위치 후보가 있는데 역할을 오판하는 경로, 옳은 후보가 선택·유지 단계에서 밀리는 경로, Foam 상단 후보가 raw 축약에서 없어지는 경로가 함께 존재한다. 이들을 하나의 confidence threshold로 해결하려 하면 다시 기존 실패를 반복한다. [R03, R04, R12, R16]

이제는 다음 구분을 실제 실행 인터페이스에 유지해야 한다.

`영상 정보 존재 → native 경로 존재 → 경계의 역할 → 해당 경로의 위치 → 같은 대상의 연속성 → report 공개 가능성`

단계마다 별도 근거가 필요하지만, 모든 프레임에서 모든 단계를 성공시켜야 한다는 뜻은 아니다. 중요한 것은 **허용된 국소 실패를 넘어서 사용자의 이야기 이해가 왜곡되거나 사라지는지**다.

## 4. 최신 증거를 목적 기준으로 다시 해석

### 4.1 높은 숫자 제공률과 잘못된 극값이 동시에 존재한다

샘플4 저장 기본 실행은 0–56초, 2 Hz, **113행**이다. Oil 숫자는 **101행(89.38%)**, Foam 숫자는 **26행**이다. 89.38%는 숫자 제공 비율이지 정확도가 아니다. [A01]

| 시점 | report/CSV 최종 Oil Y | 기존 검토와의 관계 | 맥락 영향 |
|---|---:|---|---|
| 40 s | 865.5 | 별도 raw Oil 후보 Y841과 달리 최종 선택은 잘못된 대상 | 다른 경계로 이동한 결과가 유면 변화처럼 보임 |
| 42 s | 868 | 검토된 잘못된 대상 | `MINIMUM_OIL_LEVEL` 생성 |
| 42.5 s | 835 | 기존 참조 주변의 Oil 관측 | 직전 잘못된 최저값과 큰 대비 |
| 44 s | 822 | 검토된 잘못된 대상 | `MAXIMUM_OIL_LEVEL` 생성 |
| 49.5 s | 836 | 오늘 정정 이후 A의 물리 정답 자격 미확립 | 이전 positive 표를 그대로 사용하면 안 됨 |
| 52 s | 833 | 기존 검토 범위를 유지 | 49.5초 정정과 함께 일괄 재라벨하지 않음 |

Y는 원본 화면에서 아래 방향이 양수다. 따라서 42초 Y868은 낮은 높이, 44초 Y822는 높은 높이로 report 극값에 연결된다. 실제 report에서도 이 두 극값의 마커를 확인했다. **둘은 단순히 틀린 두 점이 아니라 report의 대표 메시지를 바꾸는 두 점**이다. [R11, R12, A01]

이 사실은 ‘몇 개 오류만 있으니 무시’도, ‘모든 프레임의 검출을 완벽하게’도 지지하지 않는다. 대표적인 맥락 왜곡 경로를 먼저 제거하고, 그 과정에서 진짜 상승·하강·refill까지 지우지 않는 것이 맞다.

### 4.2 49.5초 B는 보존할 실용 판단이지 정밀 물리 정답이 아니다

오늘 정정에서 사용자는 B를 검출 한계를 감안한 근사값으로 허용했다. B의 대표 Y는 841, 중심 sector Y는 838이다. A의 Y836과 같은 물리 경계라는 초기 해석은 수정되었다. 붉은 점은 정확한 fixed-X contour·허용 오차·보편적인 proxy 규칙을 새로 정의하지 않는다. [R09]

현재 구분은 다음과 같다.

- **B의 실용적 근사 허용: 유지.** 더 정확한 Y를 강요하기 위해 이 판단을 버리지 않는다.
- **B의 정밀 물리 positive: 미확립.** 학습·보정의 깨끗한 정답으로 승격하지 않는다.
- **A의 현재 물리 대안 positive: 미확립.** 어제의 표만 보고 positive 분모에 계속 넣지 않는다.

B의 local role margin은 약 **−0.0212064**다. 기존 ‘모든 anchor에서 interface 선호 + support threshold’ 정책은 support threshold를 무엇으로 정하든 B를 이 조건에서 제외한다. 이는 **실용 허용과 정책의 충돌**이지, 이미 증명된 물리적 false negative는 아니다. B 한 점을 살리기 위해 sign 조건을 뒤집거나 다른 후보를 자동 정답으로 만들지 않는다. [R09, R16]

### 4.3 Foam은 episode보다 먼저 raw 후보에서 상단을 잃는다

54초의 검토 범위는 X595에서 Foam upper Y812–816이다. 저장 Canny에는 이 범위 안에 Y813이 있지만, raw Foam candidate에는 해당 범위와 맞는 front가 없다. component-to-front 축약은 내부 Y833을 선택한다. **이 범위의 earliest supported harmful stage는 component-to-front reduction**이다. [R12]

여기서 Y813이 범위 안에 있다는 사실만으로 그 edge나 전체 path를 정확한 물리 정답이라고 부르지는 않는다. 하지만 ‘raw에는 맞는 상단이 있었고 episode만 막았다’는 설명은 저장 결과와 맞지 않는다.

기본 실행의 마지막 Foam 숫자는 53초다. 54·55.5·56초의 검토된 상단 시점에는 Foam 숫자가 없다. 다만 현재 report는 종료를 이미 **‘거품 경계 관측 중단’**으로 표현한다. 내부 이벤트 키 `FOAM_END`를 근거로 UI가 물리적 거품 소멸을 단정한다고 비판해서는 안 된다. 다음 투입은 이 문구를 다시 고치는 일이 아니라 raw upper 개선이다. [A01, R12]

### 4.4 R/L 비교는 무엇을 닫았는가

10월 13일 고정 비교에는 **43개 context, 1,335개 기존 center-column edge**가 있다. 측정 1,184개, 필수 support 부족 119개, 보존 RGB 없음 32개다. 이는 검출 정확도 분모가 아니다. [R08, R17]

| 관찰 | 기술적 의미 | 다음 설계 제약 |
|---|---|---|
| sample4 upper-range edge의 upper support 236/275 | 39픽셀은 effective mask 밖. 해당 비교의 입력 계약 불충족 | 불가용을 ‘실제 상단 없음’으로 바꾸지 않음 |
| R은 14.25, L은 51.875 native px/token | 25픽셀 패치가 source별로 서로 다른 token 규모에 놓임 | native 위치 정보와 넓은 의미 문맥을 분리 |
| water A의 upper/lower token overlap 약 0.768 | 양쪽 평균이 상당한 표현 support를 공유 | 별개의 순수 재질 관측·독립 투표라고 부르지 않음 |
| no-Foam B/C도 local L affinity가 높음 | 유사도가 Foam 역할을 직접 뜻하지 않음 | 낮은 점수=없음, 높은 점수=Foam을 금지 |
| large→fine 내부 전이에서도 R/L signed contrast가 양수 | 입자 모양 전이가 외부 상단처럼 보일 수 있음 | fine/coarse를 다른 물리적 물질로 취급하지 않음 |
| 내부 texture guide에 exact center-Canny join이 없음 | 중요한 반례 일부가 이 edge 모집단으로 시험되지 않음 | ‘모든 내부 무늬를 억제했다’고 보고하지 않음 |

R/L 입력 승인, CR1의 일부 정보적 유용성, 새로운 역할 판별기의 유효성은 서로 다른 판단이다. **R/L의 crop·scale·reference·cutoff 재시도로 되돌아가지 않는다.** 이 결과는 모든 학습 방식이 실패한다거나 Foam 자동 측정이 원천적으로 불가능하다는 근거도 아니다.

## 5. 이번 추가 확인: native 특징도 실제 dependency footprint를 밝혀야 한다

### 5.1 질문과 고정된 대조

새로운 encoder나 detector를 실행하지 않고, 기존 `foam_front_detector._texture_evidence`만 대상으로 읽기 전용 canary를 수행했다. 입력은 sample4 f1620의 보존 grayscale/Canny/mask다. `DetectorSettings()` 기본값으로 연산 의존성을 시험했으며, 저장 세션의 Recipe 특징값을 정확히 재현한 것으로 주장하지 않는다. 사전에 고정한 대조는 다음과 같다.

1. 원본 배열은 보존한다.
2. 복사본의 **visible mask 밖** grayscale/Canny만 모두 0으로 바꾼다.
3. 별도 복사본에서는 같은 영역만 255로 바꾼다.
4. visible 영역의 입력 byte는 동일한지 확인한다.
5. 출력 variance, edge density, texture의 변화와 X595/Y813 한 점을 기록한다.

두 입력은 합성 개입이지 실제 촬영 장면이나 물리 정답이 아니다. 마스크 밖 화소가 합법적인 문맥일 수도 있으므로, 민감성 자체를 생산 버그라고 정의하지 않았다. [A02, R14]

### 5.2 결과

visible 7,344픽셀, masked 3,472픽셀에서 측정했다.

| mask 밖 대체값 | visible variance 변화 픽셀 | visible edge-density 변화 픽셀 | visible texture 변화 픽셀 | X595/Y813의 세 특징 변화 |
|---|---:|---:|---:|---|
| 0 | 1,581 | 100 | 430 | 모두 0 |
| 255 | 1,581 | 1,581 | 712 | 모두 0 |

변화 판정은 절대 차이 `>1e-6`의 수치적 canary 기준이다. detector의 물리 판정 threshold가 아니다. 측정 본체 약 0.062초이며 import 시간·전체 앱 비용을 포함하지 않는다. source 배열은 불변이다. [A02]

### 5.3 설계에 주는 결론

**‘출력 화소가 visible’과 ‘특징 계산에 쓰인 전체 화소가 해당 쪽의 유효 support’는 다르다.** 기존 texture 연산은 주변 필터를 계산한 뒤 valid mask를 적용하므로 이 차이는 코드에서도 확인된다. 새 observer는 중심 좌표만 기록하지 말고 실제 receptive field, mask 접촉, 경계 양측 공유를 기록해야 한다. [R14, A02]

동시에 inspected Y813의 기존 native 특징은 두 개입에서 모두 불변이었다. 따라서 ‘큰 25×25 입력을 못 채움 → 해당 위치의 모든 native 관측도 불가능’이라는 추론 역시 맞지 않는다. 이것이 native 경로·양측 관측을 별도로 설계할 이유다.

이 시험은 Y813의 물리 역할을 판별하지 않았고, features를 mask-aware로 바꾸면 Foam 검출이 개선된다는 것도 증명하지 않았다. **새로운 설계 의무를 확인한 결과이지 새 성능 PASS가 아니다.**

## 6. 권고 설계: Native Side-Role Observation, NSR-1

`NSR-1`은 이 문서의 제안 식별자다. R23이나 새로운 제품 detector 버전이 아니다. 기존 WP07/P5-a 및 필요한 WP02–04 관측 계약 안에 채택 여부를 기록한다.

### 6.1 해결할 질문

현재 비교의 질문은 대체로 ‘이 주변이 참조 모습과 닮았는가’였다. 다음 질문은 다음과 같이 바꾼다.

> **관측된 native 경로의 위쪽과 아래쪽은 어떤 역할을 지지하는가? 그 차이는 Foam 외부 상단, Foam 내부 변화, Oil 상단, 고정 구조 또는 미확정 중 무엇과 양립하는가?**

외형 유사도 하나를 추가하는 것이 아니다. **원본 경로에 결속된 위치, 양측 support의 출처, 역할 감독 정보, 반대 역할, 미확정을 함께 유지**하는 변경이다.

### 6.2 재사용 경계

| 책임 | 재사용할 현재 owner | 제안하는 변경 |
|---|---|---|
| source/mask/좌표 | `CurrentFrameEvidenceOwner`, 기존 frame captures | 복제하지 않음. 실제 support provenance 확장만 검토 |
| Oil native 후보·경로 | `oil_material_path`, P1 center-path 진단, 기존 edge/path 관측 | 이미 있는 경로에 연결. 새 center edge 생성기 금지 |
| Foam support와 경계면 | `s11_foam_support_geometry.measure_boundary_faces` | oriented face/inside/outside/censored 정보를 그대로 소비 |
| 후보 연결 | A1 frame/index/source/Y lineage | 대표 Y·sector Y·fixed-X 교차점을 다른 필드로 유지 |
| 역할 관측 | 기존 Witness/CR1 sidecar 경계 | 버전 명시한 diagnostic-only 확장 제안 |
| Oil 소비 | authority/phase identity/admission owners | O2/V5 이후, anchor와 continuation 함께 적용 |
| Foam raw upper | `foam_front_detector` | 역할 확인된 native 경로를 front로 투영하는 별도 변경 |
| 시간 연속성 | 현재 tracklet/lifecycle/selector/episode | 관측의 역할을 만들어내지 않음. downstream loss 증거가 있을 때만 변경 |
| CSV/report | 현재 publication/provenance owners | 관측된 동일 프레임 native candidate Y만 공개 |

새 geometry framework, 두 번째 tracker 또는 별도 report pipeline을 만들지 않는다. 이미 구현된 perimeter/edge graph/P1을 ‘신규 제안’으로 다시 구현하지 않는다. [R03, R15, R16]

### 6.3 관측 데이터 계약

다음은 **제안 schema**이며 현재 구현 API가 아니다. 실제 도입 시 Witness의 기존 버전과 serialization 계약을 검토한다.

```text
NativeRoleObservation
  source / frame / actual_timestamp / glass / geometry_digest
  candidate_binding: index, family, source_y, native_support_id
  path_binding: observed faces/segments, origin, scale, orientation status
  projection: fixed_x, observed intersections, missing/censored reasons
  upper_support / lower_support:
    native pixel membership or compact lossless reference
    requested/observed/censored counts
    actual feature receptive-field reference
    candidate-side crossing and shared-footprint diagnostics
    appearance/role evidence, qualification, unavailable reason
  relation_hypotheses:
    oil_upper / foam_upper / internal_foam / structure_or_optics / unresolved
  physical_qualification
  practical_acceptance: independent, exact subject/scope-bound
  policy_version / calibration_status
  decision: NOT_EVALUATED until the relevant policy is qualified
```

숫자 confidence 하나에 geometry/role/visibility/practical acceptance를 합치지 않는다. `UNKNOWN`은 새로운 물질 종류가 아니라 인식 상태다. 여러 가능한 역할이 남으면 set 또는 미확정으로 유지한다. 모델의 확률 출력도 보정 전에는 신뢰 확률로 해석하지 않는다.

### 6.4 native side support

고정 source Y 주변의 큰 사각형을 물질 양측이라고 가정하지 않는다. 이미 관측된 경로 조각의 orientation에 따라 국소 양측을 만들고, 실제 mask와 crop 접촉을 보존한다. 끊긴 경로를 메워 전체 영역으로 만들거나 0 label을 air로 해석하지 않는다.

구현 규칙:

- source 좌표와 native 해상도를 유지한다. candidate가 없는 위치에 truth interval을 이용해 edge를 만들지 않는다.
- branch/junction에서 양측이 유일하게 정의되지 않으면 `AMBIGUOUS_ORIENTATION`이다. 좋은 결과가 나오는 방향을 골라 쓰지 않는다.
- 재질 전용 특징을 주장하려면 **특징 전체 receptive field**가 해당 경로의 관측된 같은 쪽 support 안에 있어야 한다. 중심만 유효한 값은 context feature로 별도 기록한다.
- 경계를 가로지르는 gradient는 boundary evidence로 쓸 수 있으나 순수한 한쪽 재질 증거로 중복 계산하지 않는다.
- 모든 Canny edge를 물리 장벽으로 취급하지 않는다. Foam 내부 cell edge까지 장벽으로 만들면 support가 다시 조각난다. 어느 path가 해당 경계 가설을 소유하는지 명시한다.
- partial support는 requested/observed/censored를 함께 보존한다. 면적을 줄여 기존 R/L 실패를 PASS로 바꾸지 않는다. 새 연산의 support와 불가용 규칙은 실행 전에 따로 동결한다.
- 실제 support가 없으면 해당 관측은 미확정이다. 그것으로 Foam 없음·FULL·EMPTY를 만들지 않는다.

이 규칙은 순수 물질의 존재를 보증하지 않는다. **물리 역할 판별에 쓰일 정보가 어디에서 왔는지 검증 가능하게 하는 전제**다.

### 6.5 역할 관계와 논리적 제약

다음 관계는 후보의 가능한 의미를 구성하는 제약이다. 표 자체가 pixel classifier이거나 자동 승인 규칙은 아니다.

| 위쪽 역할 | 아래쪽 역할 | 양립 가능한 해석 | 추가로 필요한 것 |
|---|---|---|---|
| gas/headspace | bulk liquid | liquid/Oil upper | 관측 경로와 대상 역할·위치 근거 |
| gas/headspace | Foam region | Foam upper 후보 | 외부 상단/층 경계인지, 내부 기포·독립 splash가 아닌지 |
| Foam region | bulk liquid | liquid/Oil upper 후보 | 같은 층 관계 및 source 경로 결속 |
| Foam region | Foam region | 내부 Foam 변화 | fine/coarse 외형 전이를 외부 상단으로 승격하지 않음 |
| structure/optical context | 임의 | 구조/광학 반례 가능 | 구조물 역할의 긍정적 근거; 단순 정지·저유사도만으로 제외 금지 |
| 어느 한쪽 미확정 | 임의 | 미확정 또는 제한된 역할 집합 | 모르는 쪽을 air로 채우지 않음 |

fine/coarse는 Foam의 **외형 facet**이지 서로 다른 물질 클래스가 아니다. ‘둘 중 한 reference와 가까움’, ‘아래쪽이 더 비슷함’만으로 외부 상단을 결정하지 않는다.

Foam 존재, 상단 좌표, 관측 중단, 물리적 소멸은 별도 claim이다. beer처럼 상단이 crop 밖이어도 존재는 알려질 수 있다. Oil이 불명이어도 Foam 관측을 막지 않고, Foam이 불명이어도 Oil을 무조건 삭제하지 않는다.

### 6.6 역할 정보를 어디서 얻을 것인가

**현재 증거만으로 즉시 신뢰할 수 있는 새 물리 classifier를 작성할 수 있다고 가정하지 않는다.** R/L, old CR1 context, sparse interval 및 구조 반례는 정밀도와 관측 단위가 다르다. 이 차이를 유지하면서 학습·평가 입력으로 컴파일하는 작업이 필요하다.

권고하는 추가 연구는 **원본 해상도의 작은 역할 head + 약한 공간 감독**이다. 새 대형 foundation model 탐색이나 전체 end-to-end tracker 재학습은 권고하지 않는다. 공간적 의미는 학습하더라도 위치 공개는 기존 native path에 제한한다.

약한 감독과 출력 제약으로 dense/region 의미를 학습하는 접근에는 선행 연구가 있다. CCNN은 출력 제약을, ScribbleSup는 sparse spatial annotation을 이용했다. FCN은 거친 의미와 세밀한 공간 정보를 구분하여 결합하는 설계를 제시한다. 이들은 **설계 원리의 근거**일 뿐 Oil/Foam이나 현재 데이터량에서의 성공 증거가 아니다. 본 명세는 논문의 알고리즘을 구현하거나 그 benchmark 성능을 전용하지 않는다. [P01–P03]

**권한 경계:** 현재 저장소의 고정 DINOv2 비교는 training/fine-tuning을 승인하지 않는다. 따라서 아래 prototype은 별도 scope 채택과 사전 동결 후의 제안이다. 이번 세션에서는 학습·weight 변경·새 모델 설치를 하지 않았다. 역할 데이터가 준비되지 않으면 학습은 `NOT_READY`로 종료한다. 이 상태를 끝없는 prototype 추가나 implicit self-labeling으로 우회하지 않는다.

### 6.7 하나의 제한된 prototype 설계안

후속 scope가 채택될 경우, 모델 탐색 대신 다음 **단일 후보 설계**부터 검토·동결한다. 아래 수치는 성능을 맞추기 위한 탐색 결과가 아니라 비용을 제한하기 위한 제안이다.

- source RGB native lattice에서 stride 1의 `3×3 conv(3→8) → ReLU → 3×3 conv(8→16) → ReLU → 3×3 conv(16→16) → ReLU`를 사용한다. pooling/resize로 위치를 만들지 않는다.
- 마지막 native 특징의 receptive field는 7×7이다. 각 사용 지점의 실제 7×7 membership을 기록하며, censored/cross-side feature를 순수 side evidence로 승격하지 않는다.
- 해당 경계 가설이 소유한 유효 side feature를 집계하고 작은 역할 head로 `headspace / bulk-liquid / Foam-region / structure-optics-context` 증거를 낸다. 미확정은 별도 abstention/coverage 상태다.
- 두 Foam 입자 외형은 학습·평가 facet으로 각각 유지한다. 단일 Foam class로 묶었다고 한 외형이 사라진 결과를 숨기지 않는다.
- 원본 native stream만으로 feasibility를 평가한다. CR1 coarse score는 보존된 설명 변수일 뿐 이 prototype의 승인 근거로 더하지 않는다. 나중에 coarse stream을 추가하려면 별도 ablation이 필요하다.
- video ID, filename/hash, frame 번호, 시간, 정답 Y, 사람의 review flag를 모델 feature에 넣지 않는다. Recipe geometry는 support를 정의할 뿐 특정 좌표를 정답으로 주지 않는다.
- 초기 목표는 class/role 분리의 유용성이다. 출력 좌표를 회귀하여 기존 native 후보를 대체하지 않는다.

**알려진 위험:** 7×7 정보만으로 큰 기포나 가스/투명액체를 구분하지 못할 수 있다. 정지된 재질과 굴절 무늬도 비슷할 수 있다. 따라서 이 prototype을 유망하다고 단정하지 않고, §8의 반례·불가용·source 노출을 함께 평가한다. 실패하면 이 한 표현의 feasibility를 닫는다. receptive field를 계속 바꾸며 sample4 한 점을 구제하는 탐색으로 전환하지 않는다.

### 6.8 약한 정답의 컴파일 계약

| 기존 근거 | 허용하는 감독/평가 단위 | 금지하는 변환 |
|---|---|---|
| R/L 승인된 내부 appearance footprint | 해당 영역의 Foam appearance/region example | 625개 픽셀을 각각 독립적인 순수 phase 정답으로 간주 |
| upper containment interval | 그 source/X 범위 안에 특정 역할의 경계가 존재한다는 제약 | interval의 모든 Canny row를 positive로 표시 |
| 내부 texture marker | 해당 marker/context의 내부 역할 반례 | 가장 가까운 edge/path 전체에 라벨 전파 |
| no-Foam source judgment | 검토가 포괄한 장면·영역·시간의 absence/opposition 제약 | 미검토 주변 시간 또는 전체 영상으로 확대 |
| B 실용 근사 승인 | 같은 subject의 practical utility 항목 | 물리 positive, 오차 band, universal proxy 학습 라벨 |
| A 자격 철회·불명확 | physical calibration 제외, 이력 보존 | 예전 positive label을 현재 정답으로 재사용 |
| crop/unassessable | censored/NOT_EVALUATED | true negative 또는 유용한 abstention으로 계산 |

특히 **구간 안에 native 후보 하나가 있다는 사실만으로 그 후보가 실제 경계라는 것은 아니다.** source containment를 후보 bag의 ‘하나 이상 positive’로 바꾸려면 해당 native 관측의 correspondence/reachability가 별도로 확인되어야 한다. 그렇지 않으면 source-level constraint로만 보존한다.

구간 감독의 예를 수식으로 표현하면, source-level boundary distribution `p(y | I, role)`에 대해 `−log Σ[y∈reviewed interval] p(y | I, role)` 같은 부분 위치 제약을 검토할 수 있다. 이것은 **예시 손실**이며 현재 구현·승인된 학습법이 아니다. 후보 recall과 source visibility를 확인하지 않은 상태에서 candidate probability에 그대로 적용하지 않는다. 다중 경계·crop·unassessable에는 별도 상태가 필요하다.

모든 영상의 정밀 contour를 새로 그리는 것이 목표가 아니다. 현재 판정을 먼저 올바른 단위로 재사용하고, 실제 정책을 결정하는 데 부족한 **구체적인 footprint/관계**만 한정한다. R/L, B, Cold117의 닫힌 질문을 다시 묻지 않는다.

## 7. 기존 실패와 무엇이 다른가

| 이미 시험한 방식 | 반복하지 않을 이유 | NSR-1이 추가해야 하는 실제 차이 |
|---|---|---|
| full/local CR1 범주 OR/AND·argmax | category 충돌, 대안 경쟁, 보정 부재 | 역할 감독과 정확한 native binding. 새 점수 이름만 추가하지 않음 |
| R/L signed affinity | 양쪽 Foam 내부 전이·no-Foam과 충돌 | 실제 반대 역할과 내부 전이 supervision. low affinity를 absence로 사용하지 않음 |
| 평균·row distribution·밝기·색상 | 구조물/투명액체/밝은 Foam 혼동 | 새 task supervision이 구분에 기여하는지 직접 비교. 평균값만 다시 시험하지 않음 |
| closed-cell·edge closure·연결 component | rim·잔무늬·기포 내부까지 연결 | 경로의 존재와 물리 역할 분리. closure 단독 채택 금지 |
| reference LK·양측 flow·역추적 일치 | optical warp도 일관된 motion 제공 | motion은 correspondence 보조. 역할 부재를 motion으로 메우지 않음 |
| bounding-box substrate / front min·max | 실제 상단 대신 내부 또는 다른 쪽 경계로 축약 | 역할 확인된 관측 경로에서만 native projection |
| anchor-only veto | continuation 경로로 잘못된 후보가 남음 | 두 admission 경로 및 owner 결과를 함께 검증 |
| episode 완화 | 틀린 raw front의 지속만 늘릴 위험 | 올바른 raw upper가 실제로 사라진 단계가 episode일 때만 수정 |
| zero-support 무조건 제외 | 실제 lower/Oil 후보도 배제 가능 | 독립적인 positive 증거가 대체할 기존 heuristic을 명시 |

NSR-1의 novelty는 ‘경로’, ‘양측’, ‘native’라는 단어 자체가 아니다. 이 도구들은 이미 있다. **같은 native 경로의 role-qualified supervision과 support-aware observation을 실제로 연결해 보겠다는 것**이다. 그 연결이 데이터 준비 단계에서 불가능하면 새 알고리즘을 구현했다고 보고하지 않는다. [R03, R04, R16]

## 8. 첫 실행을 위한 고정 비교와 중단 조건

### 8.1 비교 roster

기존 43개 context의 측정 이력·불가용·노출은 유지한다. 새 방법이 동일 43개를 모두 지원해야만 연구를 시작할 수 있는 것은 아니지만, 지원하지 않는 항목을 빼고 ‘전체 비교 PASS’로 바꾸면 안 된다.

| 묶음 | 고정할 질문 | 필수 반례/보호 |
|---|---|---|
| sample4 Oil | 40·42·44초 wrong target과 실제 후보의 역할 | 38·42.5·52초의 현재 qualified scope, 49.5초의 practical/physical 분리 |
| sample4 Foam | 54초 upper-range의 native reachability와 내부 Y833의 관계 | 후속 internal Y837/Y838, rim, exact join이 없는 항목 |
| water | 어두운 large Foam A와 no-Foam B/C의 구분 | 입자 모양 변화, water surface·고정 패턴·내부 기포 |
| public compressor | 같은 layer의 upper Foam과 lower Oil 역할 | reference-self 여부, 두 경계를 뒤바꾸지 않음 |
| beer | 존재와 상단 좌표의 독립성 | 상단 crop 시 lower를 Foam upper로 복사하지 않음 |
| milk | 불투명한 흰 액체와 froth의 구분 | 흰색 전체를 Foam으로 선언하지 않음; unclear lower 유지 |
| 합성 대조 | support·role contract가 논리적으로 맞는지 | fine/fine, coarse/coarse, fine/coarse, coarse/fine, masked/crop, 구조 무늬 복제 |

실제 physical contour가 없는 guide를 nearby edge에 snap하지 않는다. 그 항목은 **시험되지 않은 중요한 반례**로 남긴다. 이를 다루기 위해 필요한 구체적인 native binding을 먼저 명시한다.

### 8.2 실행 전 동결할 것

실제 source/Recipe/frame/PTS와 native support digest, reference/role qualification, source/episode 분할, 모델·feature 정의, 학습/보정 절차, 한 번의 operating-point 선택 규칙, residual impact 기준, 자원 상한, 전체 output population을 preflight에 적는다.

현재 source는 모두 노출된 개발 증거다. reference 장면이나 그 인접 프레임을 independent holdout으로 바꾸지 않는다. source-disjoint 개발 비교를 할 수는 있지만, 그것 역시 이번 연구자의 untouched independent evaluation은 아니다. Windows 9개 기존 구간도 이미 알려진 qualification 사례다.

새 학습을 채택한다면 run 수·seed·optimizer·epoch/early-stop·정규화·loss weight를 **첫 실행 전에 한 세트로 동결**해야 한다. 지금 데이터 계약이 미완료인데 그 값까지 임의로 골라 학습을 시작하지 않는다. 모델/가중치/환경을 늘려 성공할 때까지 탐색하지 않는다.

### 8.3 세 단계의 판정

**G0 — 입력/표현 준비.** 실제 role·support·반례가 입력에 결속되는가? 이 단계의 종료값은 READY 또는 구체적인 NOT_READY다. 근거를 조작해 READY로 만들지 않는다. G0는 분류 정확도 시험이 아니다.

**G1 — 역할 관측의 개발 유용성.** 새로운 역할 정보가 기존 고정 유사도보다 중요한 혼동을 줄이는가? known target 손실·wrong acceptance·unavailable·unreviewed를 함께 기록한다. all-unknown, 전체 구조물 거절, reference self-match만으로 통과하지 않는다. 특정 appearance를 잃는 결과를 전체 평균에 숨기지 않는다.

**G2 — full-window 및 report 효과.** O2/V5 이후 별도 소비 변경에서 실행한다. wrong extremum 억제와 실제 변화 보존, 독립 Foam raw upper 개선을 같은 전체 구간으로 비교한다. 7개 체크포인트만으로 통과하지 않는다. 독립 report-only 판독과 Windows는 후속 통합 gate다.

### 8.4 중단 규칙

입력 pin 변동, missing role/opposition, native binding 불성립, 표현 공유를 무시한 순수 재질 주장, 자원 초과, source 누출이면 해당 run을 중단한다. 반례 충돌이 남으면 그 표현·정책의 유효성을 닫는다.

이 중단은 ‘문제 자체가 불가능’, ‘Foam 지원 종료’, ‘모든 S11 실패’를 뜻하지 않는다. 동일 근거를 threshold/crop/scale만 바꿔 재시도할 권한도 만들지 않는다. 후속 제안에는 반드시 **새롭게 추가되는 판별 정보**가 있어야 한다.

## 9. 작업 명세 — 현재 WP01–WP10과의 관계

기존 WP 번호를 유지한다. WP02·03의 완료된 adapter/qualification 작업을 다시 수행할 계획으로 쓰지 않는다. 아래 ‘필요 변경’은 기존 상태 위의 delta다. [R01, R16]

| WP / 연결 | 현재 기반 | 필요한 delta·완료 산출물 | 진입/수용 조건 |
|---|---|---|---|
| **WP01 / P0·W4** | baseline/intake 완료 | 이번 정정·full-window baseline·A/B/C/U impact ledger 연결 | source/exposure·범위 보존. 새 detector PASS 아님 |
| **WP02 / operating policy** | 164-row saved-contract adapter 완료 | physical/practical 분리 유지, NSR 입력/정책 delta 설계 | 지원되는 양·음성 역할, 실제 비교군. threshold 미보정 시 NOT_EVALUATED |
| **WP03 / V2·V3** | review qualifier 구현 완료 | weak constraint compiler 및 필요한 최소 native binding | 폐기·철회·불명확 근거를 positive로 살리지 않음 |
| **WP04 / O2** | OPEN | 기존 Witness의 typed shadow 확장, default OFF, V4 equality·resource | 로컬 V4 이후 **V5 Windows shadow**, 그 전 O2 accepted 아님 |
| **WP05 / O3** | 대기 | same-frame role condition을 anchor/continuation 모두에 소비 | O2/V5와 별도 행동 명세. 전체 0–56초 및 canonical 영향 추적 |
| **WP06 / O3→O4** | 대기 | 독립 positive 증거가 어떤 peer heuristic을 대체하는지 구현 | positive reachability 입증. lifecycle 변경은 실제 earliest downstream loss 때만 |
| **WP07 / P5-a·b** | R/L 실험 종료, raw upper 미복구 | NSR feasibility → 독립 Foam raw path/position 구현 | role/native 근거 → 별도 raw-front 행동 검증. min/max front 교체만으로 수용 금지 |
| **WP08 / P5-c** | ENTRY NOT MET | 올바른 raw upper가 downstream에서 사라질 때 episode 수정 | ‘정확한 raw가 있다’는 실제 source/lineage 증거 필수 |
| **WP09 / O5·field** | 대기 | Windows 9개 구간 + baseline/후보 report-only 판독 | V5 shadow와 최종 field를 별도 평가. phenotype/source 한정 결과 구분 |
| **WP10 / disposition** | 대기 | accepted / limited / rejected / unassessed별 종료표·지원 범위 | 목적 달성·남은 위험의 명시적 판정. 자동 S11-M/S12 진입 금지 |

### 9.1 구현을 나눌 commit/검토 단위

**첫 단위 — 관측 계약만.** native support/side role/weak constraint 연결과 source-preserving adapter. 생산 output은 불변이어야 한다. 후속 학습 제안 채택 여부를 여기에서 분리해 기록한다.

**둘째 단위 — 오선택 소비 억제.** qualified role 결과를 두 admission route에 동일하게 소비한다. 기존 후보는 진단에 남긴다. candidate 삭제와 current numeric 보류, owner 유지 가능성을 구분한다.

**셋째 단위 — positive admission.** 옳은 후보가 독립 근거로 진입하도록 한다. ‘틀린 후보가 없어졌으므로 남은 후보가 정답’이라는 규칙은 금지한다. 0-support 후보의 어떤 제한을 대체하는지 named rule로 적는다.

**넷째 단위 — Foam raw front.** material/component 결과에서 역할 확인된 native upper를 공개 가능한 후보로 만든다. Oil final 결과를 prerequisite으로 삼지 않는다.

**다섯째 단위 — 필요할 때만 시간 owner.** 정확한 raw가 있어도 continuity/episode에서 실제 손실된 근거가 있을 때 수행한다. 앞선 변경과 함께 한 번에 섞지 않는다.

**마지막 단위 — 통합 Windows/report.** 앞선 작은 변화가 실제 사용 목적을 달성하는지 평가한다. 새 UI 작업으로 detector 효과를 대체하지 않는다.

## 10. Oil 구현 수용 조건

### 10.1 역할 억제와 positive 복구를 별도로 측정한다

잘못된 구조물을 제거했다는 결과만으로 positive recovery를 선언하지 않는다. `candidate generated → physically qualified → admitted → associated → selected → published`를 현재 A1 lineage로 연결해, 어디에서 실제 후보를 잃었는지 기록한다.

역할 불명은 `HARD_INVALID`나 물리적 없음으로 바꾸지 않는다. 기존 owner의 제한된 상태를 유지할 수 있어도 현재 native 관측이 없는 프레임의 Y를 만들 수는 없다.

### 10.2 전체 구간 보호

sample4는 기존 기본 세션 0–56초/2 Hz를 동일 조건으로 비교한다. 40·42·44초를 고친 뒤 다른 시점의 대안이 새로 극값을 차지하는지 본다. 49.5초 B의 practical 허용은 별도 facet으로 남긴다. B를 정밀 물리 positive로 요구하거나, 반대로 원래 허용된 근사를 무조건 없애는 기준을 만들지 않는다.

Windows BASE의 full-prefix, drain, rapid refill, full-suffix와 Accum의 entry, layer, post-Foam, drain을 함께 보호한다. 급격한 실제 refill은 spike rejection의 negative control이다. 정지한 실제 계면은 motion-only gate의 negative control이다.

### 10.3 금지된 shortcut

샘플명/시간/Y 상수, global threshold 완화, fixed band 제외, nearest truth snap, 앞 프레임 Y carry, role score argmax만으로 승자 선정, FULL/EMPTY에 숫자 생성, 원래 후보와 다른 값을 CSV raw에 공개하는 처리는 수용하지 않는다.

## 11. Foam 구현 수용 조건

새 raw front는 지원 component의 min/max, bounding box 하단/상단 또는 가장 밝은 줄이 아니라 **역할 확인된 현재 native 경로의 투영**이어야 한다. 일부 support만 관측되어도 의미 있는 current path가 있으면 검토할 수 있지만, 마스크나 crop 경계를 물리적 front로 만들면 안 된다.

fixed Glass center X에서 관측된 해당 surface의 투영이 여러 개면 기존 계약에 따라 역할 확인 후 upper image projection을 다룬다. 다른 X로 이동해 성공한 값, lower fallback, 평균·보간으로 만든 값은 쓰지 않는다. 현재 대표 candidate Y를 뒤에서 조용히 재정의하지 않는다.

Foam에 필요한 결과는 세 갈래다.

| 관측 | 가능한 결과 | 허용되지 않는 결과 |
|---|---|---|
| Foam 존재와 상단 모두 관측 | presence + qualified native upper | 상단 대신 내부 texture 공개 |
| Foam 존재는 보이나 상단 crop/불명 | presence, upper unavailable | lower Oil을 Foam upper로 복사 |
| 상단 숫자만 끊김 | observation interruption | 즉시 physical absence/disappearance |

raw upper가 올바르게 구성된 뒤, 보존된 원시 후보가 episode에서 사라지는지를 별도로 비교한다. 순서를 바꾸지 않는다. 불가용인 경우까지 episode를 길게 유지해 그럴듯한 곡선을 만들지 않는다.

## 12. 검증 기준: 맥락 왜곡·소실·국소 잔차를 구분

기존 scene-based P0의 **A/B/C/U impact**를 실제 비교표에 사용한다. 신규 수치 tolerance를 이 문서에서 임의로 만들지 않는다. [R05]

| 구분 | 예 | 처리 |
|---|---|---|
| **A: 맥락 왜곡** | 가짜 최저/최고, 실제 drain을 상승으로 해석, Foam upper를 Oil로 출력 | 해당 workflow claim의 blocker |
| **B: 맥락 소실** | 중요한 반전·refill·Foam episode가 긴 공백으로 사라짐 | 숫자 제공률이 좋아도 usefulness blocker |
| **C: 국소 잔차** | 방향·전환·주요 사건을 바꾸지 않는 짧은 누락·근사 오차 | 허용 가능. 근거·범위·개수는 남김 |
| **U: 판정 불가** | blur/crop/역할 미검토/정밀도 부족 | NOT_EVALUATED. 정답 abstention으로 세거나 denominator에서 조용히 삭제하지 않음 |

1초 Oil 관측 목표는 별도로 qualified된 visible-motion 구간의 개발 목표다. 모든 source·Foam에 적용할 universal acceptance나 1초 보간 허용으로 바꾸지 않는다.

### 12.1 반드시 함께 보고할 값

candidate availability와 role-qualified availability, known wrong target 수와 실제 관측 손실, 원인별 unavailable, 실제 timestamp 기반 관측 간격과 앞/뒤 공백, A/B/C/U 영향, 숫자 제공률, 정확히 결속된 position 평가를 분리한다.

fine/coarse·reference/self·source/episode·native/reduced 구분을 유지한다. 중복 candidate/변형 crop/인접 프레임을 독립적인 성공으로 세지 않는다. native role 여부를 모르는 행에는 위치 오차를 계산하지 않는다.

### 12.2 report-only 판독

baseline과 후보 report를 중립적인 이름으로 제시한다. 개발자가 예상 source story를 알려주기 전에, 별도의 판독자가 Oil 방향·반전·refill/회복·full/empty, Foam 존재·상단·관측 종료, 불확실 구간을 설명하게 한다.

그다음 source 근거와 대조한다. 원본 맥락을 함께 제공하는 **현재 report 자체**가 평가 대상이다. ‘그래프만 보고 모든 물리 현상을 자동 판정’이라는 새로운 제품 목표를 만들지 않는다. 개발자의 자체 설명은 독립 판독을 대신하지 않는다.

이번 검토에서는 이 independent reader 시험을 수행하지 않았다. report의 ‘통과’ 표기나 엔지니어링 검사 PASS도 FIELD PASS가 아니다.

## 13. Windows 검증 명세

원본 업무 영상·이미지는 업무 PC에 유지한다. Mac으로 반출하거나 새 촬영을 요청하는 조건을 만들지 않는다. 준비된 candidate만 반입하여 실행하고, 허용되는 텍스트·지표·source-bound 판정으로 비교한다. [R06]

| Canonical segment | 검토된 흐름 | 핵심 합격 질문 |
|---|---|---|
| WS1-BASE-FULL-PREFIX, 480–약 550 s | FULL, visible Oil 없음, Foam 없음 | 반사·구조물에서 가짜 Oil/Foam 숫자가 생기지 않는가? |
| WS1-BASE-DRAIN, 약 550–662 s | Oil이 천천히 내려감 | 감소 방향·주요 추세가 전달되는가? |
| WS1-BASE-RAPID-REFILL, 662–약 663.6 s | Oil 급상승 후 위로 이탈 | 실제 급상승을 노이즈로 지우지 않는가? |
| WS1-BASE-FULL-SUFFIX, 약 663.6–780 s | FULL, no visible Oil/Foam | 약 725초 반사 등을 계면으로 재진입시키지 않는가? |
| WS1-ACCUM-EMPTY, 480–약 653 s | EMPTY | 가짜 초기 anchor를 만들지 않는가? |
| WS1-ACCUM-ENTRY-SPLASH, 약 653–672 s | 유입·splash·벽 흔적, 상승 Oil, Foam 없음 | splash/벽 흔적을 Foam으로 오인하지 않는가? |
| WS1-ACCUM-FOAM-LAYERED, 약 672–680 s | upper Foam / lower Oil | 두 역할과 각 움직임을 구분하는가? |
| WS1-ACCUM-POST-FOAM, 약 680–700 s | Foam 없음, Oil 존재 | Foam 소실 이후에도 Oil 관측이 유지되는가? |
| WS1-ACCUM-DRAIN, 약 700–780 s | 반전 후 Oil 하강·잔류 흔적 | 잔류물을 계속 Foam으로 보고하거나 반전을 잃지 않는가? |

각 구간은 실제 실행 coverage, valid 숫자 수·연속 구간, Y 범위·방향, 최장 missing/wrong run, wrong role, owner/handoff 변화, A/B/C/U, PASS/FAIL/NOT_EVALUATED를 기록한다. 사람이 준 approximate 시간 경계를 새 exact-pixel truth로 변환하지 않는다.

**V5 shadow와 최종 field는 다르다.** V5는 비소비 관측·기존 동작 동일성·비용을 검증한다. 소비·raw-front 변경 후의 최종 9-segment/report 시험이 field usefulness를 평가한다. 어느 하나를 다른 하나로 대체하지 않는다.

## 14. 자원·변경·재현 관리

기존 CR1 환경·가중치·cache는 사용자 retention 결정에 따라 한 벌을 보존한다. 3 GB cap을 유지하고 새 실험마다 환경·영상·token map을 복사하지 않는다. 새 학습 제안이 채택되더라도 이 cap에 필요한 추가 bytes와 peak RSS가 들어가는지 먼저 계산한다. 현재 canary는 신규 환경이 필요하지 않았다. [R07, R16]

새 지속성 실험은 기존 `experiment_artifacts.py` start/check/finish 계약으로 관리한다. 출력만 외부 폴더로 이동하여 cap이나 closeout을 회피하지 않는다. 입력/hash/실패 사례/전체 compact readout은 남기고 대용량 중복 이미지는 새로 만들지 않는다.

샘플3은 quarantine 상태를 유지한다. 명시적으로 필요한 기존 engineering replay만 별도 purpose wrapper로 수행하고 이를 물리 성능 PASS로 쓰지 않는다. 모든 기존 source/Truth/Recipe·golden bytes는 보호한다.

새 schema·관측 코드, admission 행동, Foam raw front, episode, report는 서로 다른 검토 단위로 유지한다. default OFF 상태에서 NONE/FULL·CSV/events/report 기존 필드 동등성을 확인한다. feature가 실패하거나 불가용일 때도 기존 baseline fallback이 실제로 동일한지 시험한다.

## 15. 종료 기준과 범위 판단

**로컬 개선 인정과 S11 전체 종료를 분리한다.** 특정 source/역할에서 맥락 왜곡을 줄이고 실제 흐름을 보존한 결과는 부분 개선으로 기록할 수 있다. 다른 source가 미검증이라는 이유만으로 그 성과를 없애지 않는다. 반대로 부분 개선을 전체 수용으로 포장하지 않는다.

최종 disposition은 source 이름만 나열하지 말고 다음과 같이 claim별로 구분한다.

- Supported: 어떤 관측 조건에서 Oil/Foam의 어떤 흐름을 전달하는가.
- Limited: 어떤 조건에서는 존재만 보이고 상단 좌표는 불가용인가.
- Rejected: 어떤 방법/조건이 실제 맥락을 왜곡하거나 지웠는가.
- Unassessed: 물리 정답·실행·독립 평가 중 무엇이 없는가.

현재 시점에는 Foam 자동 측정 지원 범위를 축소하는 결정을 권고하지 않는다. 고정 유사도 비교의 실패와 raw-to-front 구조적 문제는 확인되었지만, 역할 감독과 native 경로를 결합한 관측은 아직 시험되지 않았다. **다음의 제한된 연구를 수행할 이유는 있으나, 그 성공을 미리 전제할 이유는 없다.**

## 16. 후속 담당자의 실행 순서

1. 이 문서의 제안과 기존 Work Plan의 승인 상태를 비교하고, 채택한 delta만 기존 owner에 반영한다. 별도 ‘두 번째 Work Plan’을 만들지 않는다.
2. 제공된 audit JSON으로 기준 HEAD·source pin·생산 불변·실제 검증 범위를 확인한다. 현재 HEAD가 달라졌다면 최신 작업과 충돌 여부부터 재검토한다.
3. WP03/07 범위에서 native support·weak constraint의 결속 가능성을 확인한다. 닫힌 질문을 재개하거나 미검토 후보에 라벨을 전파하지 않는다.
4. 역할 head 연구를 채택할 때만 별도 training 범위와 G0 preflight를 승인한다. 채택하지 않은 상태에서는 학습을 시작하지 않는다.
5. 첫 feasibility는 한 표현·한 고정 대조로 완료한다. negative/unknown을 포함한 전체 결과와 실패 원인을 남긴다.
6. 유용성이 확인된 관측만 WP04 shadow→V5→WP05/06 또는 WP07 raw integration으로 보낸다. WP08은 여전히 raw-first 조건을 지킨다.
7. 마지막으로 WP09/10의 Windows·report 판독·지원 범위를 닫는다.

## 17. 이번 작업의 마감 선언

**완료:** 최신 상태·실패 이력·source qualification 검토, 저장 report/CSV/영상 기반 증거 대조, 입력·생산 source 재검산, 9개 focused test, 14개 관리 run check, native feature footprint canary, 이 설계·작업 명세서 및 재현 자료 작성.

**하지 않음:** 새 물리 정답 작성, 새 classifier 학습, encoder 재추론, 전체 영상 replay, 생산 detector 변경, Windows 실행, 독립 판독 시험, S11/O2/FIELD 상태 승격, commit/push.

이번 결과는 ‘detector 개선 성공’이 아니라 **현재 실패와 실용 목표를 연결한 후속 설계 및 검증 가능한 작업 계약**이다. 관측 방법의 성능은 다음 동결된 실험에서 판단한다.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: authority/continuation collapse; native path acquisition and edge reconnection; role-free component extrema; CR1 full/local competition; corrected practical B; fixed public transfer; fine/coarse material-side collisions; flow/cellular/reference failures; same-frame publication and scene-based story acceptance.
- Prior mechanisms rejected: cutoff/crop/scale/reference retries, category fusion, motion-only authority, standalone closure/cellular identity, bbox front replacement, anchor-only filtering, episode relaxation without a correct raw front, sample-specific rules and exact-truth escalation of approximate judgments.
- Preserved contracts: native same-frame provenance, independent Oil/Foam, bounded temporal owners, fixed-X projection after role identification, physical/practical distinction, sample3 quarantine, retained environment cap, O2/V5/O3/field separation.
- Difference from prior failures: the proposed observer adds qualified task-role supervision and actual native feature/side footprint accounting, rather than another score combination. Weak source constraints remain weak and cannot automatically label candidate paths. Training is a separately proposed scope, not executed or implicitly authorized. The new canary tests only feature dependencies and explicitly does not identify a repaired front.
- Logic-map impact: NONE — this external specification and read-only diagnostic add no executing detector owner or production schema.
- Failure-registry impact: NONE — no new production failure family or accepted repair is claimed; the canary constrains interpretation of an existing feature owner.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: sample4 f1620's saved component-to-front reduction selects internal Y833 and yields no raw upper within the qualified range. For the new masked-pixel canary, production harm is NOT_EVALUATED; footprint sensitivity is not itself a detector defect, and the inspected Y813 anchor remains unchanged.
- Logic-map impact: NONE — source arrays and production code are unchanged; only copied arrays pass through the existing feature function.
- Failure-registry impact: NONE — the readout establishes a dependency-footprint constraint, not a new physical failure or accepted detector repair.

## 부록 A. 원본 근거 목록

아래 경로는 기준 HEAD의 저장소 상대 경로다. 전체 SHA-256과 line count는 동봉 audit JSON의 `sources`에 있다. 저장 CSV·sample4 MP4 hash는 같은 JSON의 별도 항목에 있다. 현재 대화에서 복제한 repo 파일을 별도의 정본으로 만들지 않았다.

| ID | 원본 |
|---|---|
| R01 | `docs/00-project/work-plan.md` |
| R02 | `docs/00-project/roadmap.md` |
| R03 | `docs/20-architecture/s11-current-detector-logic-map.md` |
| R04 | `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` |
| R05 | `docs/30-validation/s11-interface-observability-witness-validation.md` |
| R06 | `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` |
| R07 | `docs/60-evidence/s11/2026-10-13-material-role-handoff.md` |
| R08 | `docs/50-diagnostics/s11/2026-10-13-foam-material-sides.md` |
| R09 | `docs/50-diagnostics/s11/2026-10-13-cr1-competitor-role.md` |
| R10 | `docs/50-diagnostics/s11/2026-10-13-cr1-public-transfer.md` |
| R11 | `docs/50-diagnostics/s11/2026-10-12-cr1-context-comparison.md` |
| R12 | `docs/50-diagnostics/s11/2026-10-11-p5-default-linkage/readout.json` |
| R13 | `sample/README.md` |
| R14 | `src/oil_tracker/adapters/vision/foam_front_detector.py` |
| R15 | `tests/diagnostics/s11_foam_support_geometry.py` |
| R16 | `docs/20-architecture/s11-contextual-role-observation-design.md` |
| R17 | `docs/50-diagnostics/s11/2026-10-13-foam-material-sides/preflight.json` |
| R18 | `tests/unit/test_s11_foam_material_sides.py` |
| A01 | 이번 SHA/CSV/event 재검산, 직접 시각 검토, focused test 및 run check |
| A02 | 이번 고정 0/255 masked-pixel native feature canary; 재현 스크립트 동봉 |

## 부록 B. 외부 방법론 근거

논문 저자들이 공개한 abstract와 방법 개요를 확인했다. 아래 문헌의 benchmark 성능, 데이터 규모, 실행 시간 또는 정확도를 본 프로젝트의 예상 성능으로 인용하지 않았다.

- **P01:** Pathak, Krähenbühl, Darrell. *Constrained Convolutional Neural Networks for Weakly Supervised Segmentation*. ICCV 2015. arXiv:1506.03648. 출력 제약을 학습에 사용하는 원리.
- **P02:** Lin et al. *ScribbleSup: Scribble-Supervised Convolutional Networks for Semantic Segmentation*. CVPR 2016. arXiv:1604.05144. sparse spatial annotation을 활용하는 원리.
- **P03:** Shelhamer, Long, Darrell. *Fully Convolutional Networks for Semantic Segmentation*. 2016 journal edition. arXiv:1605.06211. 거친 의미 정보와 세밀한 공간 정보의 역할 분리 원리.

실제 URL은 audit JSON의 `external_method_sources`에 기록했다. 본 문서의 NSR-1, 역할 관계·support·약한 정답 컴파일 및 단계별 수용 계약은 이 저장소의 제약에 맞춘 **새 설계 제안**이다.
