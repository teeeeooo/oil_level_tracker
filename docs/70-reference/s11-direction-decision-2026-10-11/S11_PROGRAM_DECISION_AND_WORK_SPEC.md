# S11 전체 진행 검토·판단 근거·검출기 작업 명세

**검토 기준:** 2026-10-11, `teeeeooo/oil_level_tracker`, `main @ 5c53aefe3bb3c5d1447b29ccb2f78d1adc5459c6`  
**문서 성격:** 사용자 요청에 대한 독립 검토 및 채택 제안. 현재 Work Plan·제품 계약·검증 게이트를 자동으로 변경하지 않는다.  
**현재 운영 상태:** R22 동작 유지 / R22-3 진단 / Local XY OFF / O2 OPEN / FIELD FAIL.  
**이번 실행:** 저장 증거의 독립 재검증 3종, 집중 테스트 162개, S2 판별식의 추가 수학·데이터 감사. 운영 검출기 변경·새 Windows 실행·commit/push 없음.

---

## 1. 결론과 이번에 내려야 할 결정

### 1.1 권고

**S11의 납품 목표를 ‘모든 영상 외관에서 Foam의 물리적 정체를 완전히 자동 판별’로 확대하지 않는다. 관측 가능하고 검증된 범위의 자동 수치 측정과, 주요 유면·Foam 움직임의 맥락 전달을 목표로 유지한다.**

선택지를 둘 중 하나로 표현해야 한다면 **지원 범위를 명시한 자동측정 쪽을 권고**한다. 다만 현재 검출기를 ‘제한된 범위에서는 완성’이라고 선언하는 결정은 아니다. 어떤 범위에서 실제로 충분한 양성 관측과 올바른 운동 맥락을 제공하는지는 아직 검증해야 한다. 나머지 구간을 전부 UNKNOWN으로 처리하거나 기존 영상 캡처를 보여주는 것만으로 detector 개선을 완료 처리하지 않는다.

기술적으로는 다음 순서를 권고한다.

1. Oil의 잘못된 대상 선택이 최고·최저점과 상승·하강 맥락을 왜곡하는 문제를 핵심 납품 장애로 유지한다.
2. Foam에서는 실제 상단을 내부 무늬로 축약하는 **raw-front 측정 문제**를 다룬다. 아직 올바른 raw front가 들어가지 않은 episode를 먼저 완화하지 않는다.
3. 지원 범위와 실용성 평가를 명시하고, 새로운 판별 가설은 **수학적 양성 도달 가능성 → 물리 대조군 → 전체 동작 → 보고서 맥락** 순서로 검증한다.
4. 범용 자동 판별 연구는 별도 조건부 연구 항목으로 남기되 S11 전체를 무기한 붙잡는 선행 조건으로 두지 않는다.

### 1.2 이 결론이 의미하지 않는 것

- 비학습 영상처리로는 해결할 수 없다는 결론이 아니다. 실패한 유한 개 가설에서 모든 가능한 방법의 실패는 도출되지 않는다.
- 머신러닝 도입, 새 촬영, 조명 변경, 수동 프레임별 라벨링을 요구하는 제안이 아니다. 현재 사용자 제약을 유지한다.
- sample4의 사용자가 확인한 **가시적인** Foam 상단을 ‘지원하지 않는 영상’으로 사후 제외하자는 제안이 아니다.
- 기존 O2/O3, 9개 Windows 구간, same-frame provenance, 독립 Oil/Foam 책임을 완화한 것이 아니다. 범위·출시 계약 변경은 명시적인 채택과 owner 문서 수정이 필요하다.
- 현재 R22 또는 S2를 승격하자는 제안이 아니다. **승격할 신규 물리 역할 판별기는 이번 감사에서도 확보하지 않았다.**

### 1.3 왜 단순히 ‘계속 연구’도, ‘Foam 기능 축소’도 바로 정답이 아닌가

완전 자동 판별 연구를 계속한다는 결정만으로 다음 구현 가설이 생기지는 않는다. 반대로 지원 범위를 줄인다고 해서 검증된 양성 자동측정이 저절로 남지도 않는다. 지금 필요한 결정은 ‘모든 조건을 보장하겠는가’가 아니라 **어떤 관측 범위에서 어느 정도의 오류·공백까지 사용자의 해석을 보존해야 하는가**이다.

제품 SSOT는 이미 완전 무인 판정이 아닌 판독 보조를 목표로 하고, pixel-perfect 오차보다 같은 물리 유면의 충분히 잦은 관측과 운동 맥락을 우선한다. 따라서 목표를 새로 발명할 필요는 없다. 기존 목표가 연구·평가·종료 조건에서 실제로 작동하도록 정리해야 한다. [R01, R02]

---

## 2. 실제로 확인·실행한 범위

| 항목 | 이번 수행 결과 | 해석 한계 |
|---|---|---|
| checkout/remote 확인 | local main과 origin/main 모두 `5c53aef…`; 시작·종료 시 tracked 변경 없음 | 같은 head라는 사실은 성능 증명이 아니다 |
| 프로젝트 상태 | Work Plan, roadmap, 제품 SSOT, execution policy, detector skill/governance, logic map, 실패 registry 및 연결 증거 검토 | 관련 책임 경로를 추적한 검토이며 모든 과거 커밋·전체 소스의 전수 정적 감사는 아니다 |
| 영상 검토 | 저장된 sample4 원본 픽셀 리뷰, 54/55.5/56초 장면, 43.5초 Oil 리뷰, water 10-frame source sheet, public path 그림, 실제 report 그래프·source sequence를 직접 열어 확인 | 이번에는 MP4 전체를 새로 디코딩하거나 연속 재생하지 않았다. 저장 원본 프레임과 해시 검증된 증거를 재사용했다 |
| default linkage 재검증 | 113행, current candidate 2,611개 exact join, NONE/FULL 동등성, 기존 tracking/events 동등성 확인 | 새 detector replay가 아니라 기존 replay 산출물의 독립 재검증 |
| P2-S1 재검증 | 60 input pin, 1,650 role/shift cost, 199,800 BGR 비교, production 221개 파일 불변 | 실패한 모델의 계산 재현이지 모델 성능 PASS가 아님 |
| P5-S2 재검증 | 42 raster, 1,322 query, 2,718,514 side center의 합·비용·결정 재현 | 42개 독립 영상이나 holdout이 아님 |
| 집중 테스트 | **162 passed / 18.13초** | 전체 canonical/GUI/Windows suite 실행 아님 |
| 추가 S2 수학 감사 | 2,556개 variant cost triple, 2,592개 대비가 존재하는 side의 정규화 범위 확인 | 신규 분류기 또는 threshold 탐색이 아님 |
| governance / diff | checker 통과, `git diff --check` 통과 | tracked 변경이 없는 상태의 저장소 검증; 외부 제안서가 자동 채택됐다는 뜻이 아님 |

실행 로그·영수증은 Mac의 다음 ignored 경로에 남겼다.

```text
/Users/sunjaekim/Developer/oil_level_tracker/sample/output/
  s11-direction-decision-5c53aef-001/
```

배포 ZIP에는 재검증 stdout에서 옮긴 요약, 추가 수학 감사 JSON, 재현 도구, 본 명세서를 넣었다. 대형 원본 readout/trace·MP4·기존 이미지 전체를 복제하지 않았다. 원본 데이터 의존성은 §12에 명시한다.

---

## 3. 프로젝트 전체 진행 상태

### 3.1 구현이 끝난 영역과 아직 증명되지 않은 영역

| 영역 | 현재 상태 | 앞으로의 위치 |
|---|---|---|
| Setup, Recipe, readiness, Result Review, export, 복구·반복 시험 흐름 | Phase 1/2 및 S1–S10 완료로 관리 | 검출기 작업의 회귀 보호 대상. 새 UX 프로젝트로 확대하지 않음 |
| Windows packaging/clean-PC 기반 | S10 완료 | 설치 가능성과 현장 검출 유효성을 분리 |
| Oil ownership/phase/sequence 구조 | R22 로컬 채택 | 기존 단일 책임·bounded lifecycle 유지 |
| 관측·lineage·trace | O1 및 R22-3 진단 기반 존재 | 원인 추적에 재사용; 더 많은 진단을 만드는 것 자체가 목적이 아님 |
| P1 center-conditioned 경로/edge·support 보존 | offline 구현·증거 있음 | 후보의 존재와 형상 보존에 재사용; 물리적 정체를 보증하지 않음 |
| O2/W4/P2 판별 | OPEN, P2-S1 실패 종료 | Oil 역할·대상 판별의 선행 장애 |
| P5 Foam | source 위치·default linkage 완료, S2 실패 종료 | raw-front 후보의 역할 판별·선택 미해결 |
| P3 association / P4 phase | 판별 근거를 전제로 하는 후속 작업 | 가설 근거 없이 비용·handoff·phase gate부터 완화하지 않음 |
| Report source-context/episode review | 이미 채택 | detector 개선을 평가하는 최종 소비자. 캡처 추가만으로 개선이라고 하지 않음 |
| 현장 효용 | **FIELD FAIL 유지** | 현행 정확한 후보의 9개 Windows 구간 + report 맥락 검증 필요 |
| S11-M, S12 | PLANNED | S11 핵심 효과 확인 후 구조 정리·UX를 별도 수행 |

S11은 구현량이 부족해서 멈춘 상태라기보다 **관측 형상과 물리 역할을 분리한 뒤, 그 역할을 올바르게 판단하는 근거가 충분하지 않은 상태**다. 진단 인프라·원인 설명은 크게 진전됐지만 이를 검출 성능 회복과 혼동해서는 안 된다. [R02–R05]

### 3.2 진행 방식의 장점과 수정할 점

장점은 명확하다. 기존 실패를 보존하고, trace가 실제 동작을 바꾸지 않는지 확인하며, source/Recipe/truth를 고정하고, missing support를 음성으로 오인하지 않도록 관리하고 있다. 이런 장치는 유지해야 한다.

수정할 점은 **모델 계산 검증이 실제 양성 도달 가능성·사용자 맥락 평가보다 앞서 과도하게 커지는 흐름**이다. S2처럼 합성 양성조차 의도한 class를 선호하지 않는 모델은 수백만 픽셀을 재검증하기 전에 모델/정규화 가정을 점검해야 한다. 정확하게 계산된 실패를 반복해서 쌓는 것보다 ‘이 모델이 필요한 결정을 할 수 있는가’를 먼저 확인하는 편이 개발 효율이 높다.

또한 P5의 범용 물리 판별 문제가 Oil의 모든 유용한 개선을 막는 단일 병목이 되어서는 안 된다. Oil/P2와 Foam/P5는 근거·책임을 분리하고 각자의 진입 조건을 만족한 쪽만 진행한다. 이는 여러 subagent를 쓰자는 뜻이 아니라 **작업 의존성을 분리**하자는 뜻이다.

---

## 4. 증거로 확정된 핵심 장애

### 4.1 sample4: 수치가 많아도 최고·최저점이 틀리면 맥락은 실패한다

현재 controlled default sample4 결과는 113개 sampled row 중 Oil 101개, Foam 26개가 valid numeric이다. 단순 수치 비율로는 Oil 약 89.4%지만 이는 물리적 정확도가 아니다.

실제 report의 movement summary와 그래프는 **42초를 최저점, 44초를 최고점**으로 강조한다. 그런데 기존 source-bound 검토는 두 시각의 선택 Oil 후보를 잘못된 대상으로 분류한다. 40초도 기존 오선택 대조군이다. [R06, R07]

| 관측 | 현재 결과 | 제품 목적에 대한 의미 |
|---|---|---|
| 42초 | Oil Y868, report 최저점 −18px | 이미 검토된 wrong target이 전체 최저점이 됨 |
| 44초 | Oil Y822, report 최고점 +28px | 이미 검토된 wrong target이 전체 최고점이 됨 |
| 43/43.5초 | Oil 최종 수치 없음 | 43.5초의 source에서 Oil 위치는 지역 수준으로 확인됐지만 owner 제한으로 publishable row가 제외됨 |
| 54초 | Foam 최종 수치 없음 | 상단이 실제로 보이지만 올바른 raw front가 downstream으로 전달되지 않음 |

여기서 두 극값의 문제는 ‘몇 프레임을 못 잡은 사소한 edge case’가 아니다. 최저 유면, 회복 방향, 주요 변화 구간을 잘못 읽게 만드는 **고영향 오류**다. 프레임 오류의 개수보다 출력에서 차지하는 역할로 우선순위를 정해야 한다.

보고서의 설정 기반 `PASS/합격` 표시도 현장 검출 정확도나 report 맥락 검증 통과를 뜻하지 않는다. 기존 report는 ‘거품 경계 관측 중단’처럼 검출 종료와 물리적 소멸을 구별하려는 표현을 이미 갖추고 있다. 이 문구 개선을 다시 과제로 제안하지 않는다. 문제의 중심은 위에서 들어오는 numeric observation이다.

### 4.2 Oil 43–43.5초: selector 점수보다 앞의 ownership 문제

기존 causal trace에서 43초 Y836은 두 predecessor와 매칭 가능하다. 기존 owner `0013`은 cost 약 0.8508이고 새로운 `0017`은 약 0.0102지만, established-first 정책 때문에 전자가 가져간다. phase는 별도로 `0017`의 filling owner를 유지한다. 결과적으로 publishable row가 있어도 허용 owner ID에 속하지 않아 selector 전에 사라진다. [R07]

그렇다고 cost-first로 바꾸면 해결되는 것은 아니다. 이미 수행한 전 구간 counterfactual은 15개 Oil row와 19개 phase를 바꾸고, 56초에서 상단 texture로 이동하는 문제를 보였다. **인접성·낮은 매칭 비용만으로 물리 정체를 복구하지 못한다.** 이 실험은 폐기 상태를 유지한다.

판별 근거가 확보된 이후 association을 수정할 때의 목표는 ‘gap을 없애기’가 아니라 **올바른 현재 관측의 물리 owner를 보존하고, stale owner가 그것을 독점하지 못하게 하는 것**이다.

### 4.3 sample4 Foam: 상단이 안 보이는 것이 아니라 잘못 축약한다

54초 f1620, fixed X595에 대해 사용자가 확인한 상단 구간은 source pixel-cell 범위 `[811.5, 816.5]`이다. 이 구간에 실제 Canny edge Y813과 retained white support가 존재한다. 그런데 component C1의 global extent는 Y[808,834)이고 lower-edge 규칙으로 **Y833**을 raw Foam candidate로 내보낸다. Y833은 이미 내부 Foam texture로 확인된 위치다. [R08, R09]

```text
원본/기존 edge Y813
  → 현재 열의 상단 support도 보존됨
  → C1 component-to-front reduction
  → 내부 texture Y833만 Foam candidate로 전달
  → episode formation이 Y833을 거절
  → 최종 Foam 수치 없음
```

이 인과 연결은 이번에 다시 검증한 default/NONE–FULL 일치와 exact candidate join으로 뒷받침된다. scoped replay의 결론을 default에 임의 전이한 것이 아니다.

**금지할 조치:** episode 완화, global bottom→global top 치환, smoothing Y813의 재사용, 현재 열의 nearest edge로 snapping. global top Y808도 확인 구간 밖이다. 현재 smoothed 값이 우연히 Y813이어도 같은 프레임에서 선택된 후보의 provenance를 대체하지 못한다.

### 4.4 Water A: 다른 최초 손실 단계

sample5 A/f1232의 upper Foam interval `[475.5,481.5]`에는 Canny Y477이 있다. 그러나 retained appearance support에 도달하기 전에 lightness/whiteness 조건에서 사라진다. sample4의 component-to-front 문제와 다르다. [R08, R10]

B/f1438과 C/f1643은 water upper surface 양성이지만 Foam layer는 없는 대조군이다. A의 lower boundary는 불명확하다. 따라서 A의 upper edge를 발견했다고 lower Oil 경계나 Foam 두께를 계산할 수 없고, B/C의 물 표면을 Foam으로 재분류해서도 안 된다.

**금지할 조치:** white threshold 일괄 하향, white/warm union, 위에 gap이 있으면 Foam으로 판정, stationary한 표면이면 구조물로 판정. 기존 실패에서 실제 구조물도 그런 특징을 보였다.

---

## 5. 이번에 추가로 확인한 S2 판별식의 구조적 한계

이 절은 최신 종료 문서를 반복한 것이 아니라, frozen S2 readout의 판별 경계를 수식으로 전개하고 전 저장 결과에 검증한 추가 분석이다. 결과는 `evidence/s2-decision-geometry.json`, 재현 도구는 `tools/audit_s2_decision_geometry.py`에 있다.

### 5.1 ‘양성 0/2’보다 한 단계 더 구체적인 설명

S2는 위·아래 side의 특징값을 `a`, `b`로 두고 다음 prototype에 대한 평균제곱오차를 비교한다.

```text
Foam 상단 U: (0, 1)
내부 cellular I: (1, 1)
noncellular N: (0, 0)

C_U = [a² + (b−1)²] / 2
C_I = [(a−1)² + (b−1)²] / 2
C_N = [a² + b²] / 2
```

따라서 정확히 다음 관계가 성립한다.

```text
C_U − C_N = 0.5 − b
C_U − C_I = a − 0.5
```

U가 두 경쟁 설명보다 엄격하게 좋은 최소 비용을 가지려면 **a < 0.5, b > 0.5**가 필요하다. 현재 margin 0.05를 만족하려면 **a ≤ 0.45, b ≥ 0.55**까지 필요하며 cost gate는 별도다.

| 확인된 실제 상단 | 위쪽 a | 아래쪽 b | U가 N보다 불리한 비용 차이 |
|---|---:|---:|---:|
| sample4 f1620/Y813 | 0.05663 | 0.12319 | +0.37681 |
| water A f1232/Y477 | 0.00000 | 0.15653 | +0.34347 |

즉 두 양성은 cutoff 직전에서 아깝게 탈락한 것이 아니다. **원래 최소 비용 순위부터 N이 앞선다.** 같은 특징·prototype을 유지한 채 max-cost 또는 margin만 느슨하게 해도 U가 우승하지 않는다. 이 결과는 S2를 재조정하자는 근거가 아니라, 해당 모델 가정의 실패를 명확하게 닫는 근거다.

### 5.2 ablation에도 별도의 기하학적 제약이 있다

ablation은 비음수 opposing-axis 값 X,Y로 `R0=(X+Y)/2`, 분모로 `P=max(X,Y)`를 사용한다. 따라서 픽셀마다 `P ≤ X+Y ≤ 2P`이고, 대비가 실제로 존재하여 `sum(P)>0`이면 다음이 성립한다.

```text
0.5 ≤ r0 = sum(X+Y) / [2·sum(P)] ≤ 1
```

위쪽 side에 대비가 조금이라도 있으면 ablation의 a는 0.5 이상이다. 그러면 U는 I보다 엄격하게 좋은 비용을 가질 수 없다. 위쪽 대비가 정확히 0인 합성 예제와, 낮은 수준이라도 대비가 있는 실제 영상 사이에 구조적인 차이가 생긴다.

실제 저장 데이터에서도 대비가 존재하는 **2,592개 side 모두** 이 범위에 있었고, 관측된 범위는 `[0.5, 0.742857…]`였다. 총 **2,556개 variant cost triple**에서 위 비용식·차이식을 재현했다. 이는 1,278개 양쪽 측정 가능 query × joint/ablation 2종이며, 44개 unavailable query는 비용 검증 대상이 아니다.

### 5.3 개발 절차에 반영할 수정

다음 모델에는 단순 산술·shape·invariance 테스트 이외에 다음 순서를 적용한다.

- **수학적 가능성 검사:** 특징값의 실제 가능 범위와 prototype/decision 영역이 양성 결정을 허용하는지 먼저 증명한다. 합성 양성에서 무엇을 pass로 볼지 사전에 정한다.
- **양성 도달 검사:** 고정된 대표 양성에서 필요한 관측이 만들어지는지 확인한다. 이 단계 실패가 곧 모델 실패인지, 의도된 범위 밖인지도 실행 전에 고정한다.
- **물리 대조 검사:** 양성 보존과 실제 구조/texture opposition을 함께 본다. missing query를 성공한 음성 판정으로 세지 않는다.
- **전 구간·최종 산출물 검사:** 위 단계를 통과한 뒤 비용이 큰 replay와 report 맥락 평가를 한다.

S2의 27개 기존 focused test와 이번 162개 테스트 통과는 계산·계약의 안정성을 보여준다. 양성의 물리 역할 판별이 통과했다는 의미는 아니다. **S2가 실패한 사실과 모든 conventional CV가 실패한다는 주장은 엄격히 분리한다.**

### 5.4 P2-S1도 threshold 문제가 아니다

P2-S1의 확인된 44초 positive는 cost 0.1561067, margin 0.0513321이고, 확인된 42초 negative는 cost 0.1535881, margin 0.0532660이다. 잘못된 대상이 더 낮은 비용·더 큰 margin으로 우세하다. 이 두 점을 기존 max-cost/min-margin 규칙만으로 원하는 방향으로 분리할 수 없다. 이번 재검증에서도 그대로 재현됐다. [R11]

따라서 P2/S2 모두 ‘threshold를 더 만지면 될 것’이라는 후속 계획은 부적절하다. 그러나 실패 원인은 서로 다르므로 한 가지 일반적 불가능성으로 묶지 않는다.

---

## 6. 권고하는 지원 범위와 종료 계약

### 6.1 세 가지 의미를 분리한다

| 구분 | 필요한 증거 | 허용 출력 | 금지 해석 |
|---|---|---|---|
| Foam 물질 존재 | 해당 물질 역할의 관측 근거 | 존재/불확실 상태, 이미 지원하는 source context | 높이 검출 실패를 물질 부재로 단정 |
| Foam 상단 높이 | 현재 프레임의 가시적인 상단 + 역할 근거 + fixed-X 실제 관측 | 선택된 후보의 수치, 관측 불가/불확실 | bbox extrema, nearest edge, 과거 값의 재사용 |
| Foam 두께 | 동일한 물리 층의 upper/lower 두 경계를 각각 확인 | 두 경계가 유효할 때만 파생량 | beer 앞/뒤 투영 arc 간격 또는 불명확 lower로 두께 생성 |

`NO_EVIDENCE`, `AMBIGUOUS`, visibility loss, role uncertainty는 서로 다른 상태다. 현재 `FoamDecisionStatus` 및 진단 타입을 먼저 재사용하고, 표현할 수 없는 의미만 최소한의 additive diagnostic contract로 보완한다. 새로운 UI 모드나 공개 스키마를 성급하게 추가하지 않는다.

### 6.2 지원 영역은 영상 이름이나 검출 성공으로 정의하지 않는다

지원 범위의 조건은 사전에 관측·입력 특성으로 정의해야 한다. 예를 들어 Recipe로 정의한 측정 열에서 상단이 촬영 범위 안에 있는지, 실제 spatial support가 확보되는지, 포화·가림으로 경계가 소실됐는지를 구분할 수 있다. **‘모델이 맞힌 프레임만 지원’은 순환 정의이므로 금지**한다.

반대로 visibility/support 조건은 물리 역할을 보증하지 않는다. 상단이 보이는 sample4 f1620을 기존 모델 실패만으로 범위 밖에 넣을 수 없다. 공개 water A의 어두운 외관을 제외하려면 제품 입력 범위 자체를 명시적으로 좁히는 별도 승인과 영향을 공개해야 한다. 이를 이번 권고에 자동 포함하지 않는다.

상단 crop-out, 실제 blur/occlusion, lower 불명확 같은 관측 한계는 수치 비생성의 정당한 이유다. stationary Foam, inclination, 어두운 Foam은 그 자체로 구조물·부재가 아니다. 이들은 특징군 또는 측정 가능성의 차이이지 거짓 음성 면허가 아니다.

### 6.3 대상 도메인과 보조 영상의 우선순위

지원 범위 결정이 채택되면 **실제 압축기 Windows 증거 → source-qualified compressor sample4 → 공개 water/beer/milk stress 자료** 순서로 제품 적합성을 판단한다. 공개 물·맥주·우유 영상은 표현 한계와 혼동을 드러내는 유용한 대조군이지만, 모든 외관에서 동일한 수치 성능을 내는 것이 압축기 제품의 납품 목표인지는 별도 문제다.

이것은 기존 S2의 water A 실패를 지우라는 뜻이 아니다. S2는 원래 두 양성을 요구한 frozen 실험으로 계속 실패다. 이후 제품 입력 범위를 명시적으로 바꾸기로 승인한 경우에만 **새 preflight에서** target-domain acceptance와 보조 domain stress의 역할을 구별한다. 영상명·재질 추정·성공 여부로 결과를 사후 제외하지 않는다. 범위 밖 자료에서도 물리 보장이 없는 수치를 확신하며 출판하는 위험은 별도 기록한다.

특히 target Windows의 Accum Foam layer와 sample4의 확인된 visible upper는 검출기가 어려워한다는 이유로 납품 기준에서 없애지 않는다. 핵심 도메인의 유용한 양성조차 남지 않는 제한은 지원 범위 정의가 아니라 기능 철회이며, 다른 사용자 결정이 필요하다.

### 6.4 실용성 통과 조건

**안전성과 유용성을 AND로 평가한다.**

- 지속적 wrong-interface 또는 주요 극값·반전·회복을 지배하는 오선택을 새로 만들지 않는다.
- 사전에 지정한 주요 관측 구간에서 실제 양성 관측과 올바른 운동 순서가 남는다. 전부 UNKNOWN이거나 음성만 좋아진 결과는 실패다.
- 가시성·움직임이 별도로 확인된 Oil 구간의 usable same-interface 관측 간격은 기존 **1초 개발 목표**를 적용한다. 전체 녹화의 미확인 구간에 일괄 적용하지 않는다.
- Foam의 관측 빈도·onset/extinction 오차는 그 역할·시간 truth가 허용하는 범위에서 평가한다. Oil의 1초를 Foam 기준으로 자동 전환하지 않는다.
- 앞뒤 관측을 잇는 report 선이나 source-context 이미지는 numeric coverage를 늘리지 않는다.
- detector 지표 개선과 report-only 이해 가능성을 별도로 기록한다. 후자만 좋아진 경우 detector 개선 성공이라고 하지 않는다.

### 6.5 동일 픽셀 복제 대조군의 정확한 위치

동일한 입력 픽셀과 동일한 메타데이터를 받는 결정론적 함수는 서로 다른 출력으로 구별할 수 없다. 따라서 Foam처럼 보이는 패턴을 픽셀 단위로 복제한 구조물 대조군은 **영상만으로 제공할 수 없는 보장의 경계**를 보여준다.

그렇다고 실제 rim·wall mark·반사·잔류물 대조군을 제거할 수는 없다. 이들은 실제 현장 위험이며 계속 사용한다. 복제 대조군의 실패를 실제 영상 전부에 대한 실패율로 바꾸거나, 모든 양성까지 영구 abstain해야 한다는 결론으로 확대하지 않는다. 기존 contract가 이러한 상황에서 generic adoption을 금지한다면, 그 경계를 변경하는 일은 명시적인 지원 범위 결정·owner 개정 사항이다. 본 문서는 그 게이트를 우회하지 않는다.

---

## 7. Detector 설계 명세: 책임과 변경 경계

### 7.1 보존할 데이터 흐름

```text
current frame + Recipe
  ├─ 실제 edge/path + spatial visibility/support
  ├─ material / structural / internal-texture evidence
  └─ bounded temporal evidence
          ↓
역할이 아직 정해지지 않은 관측 후보와 대립 설명 보존
          ↓
역할·대상·fixed-X scalar 자격을 분리해 평가
          ├─ Oil authority → physical tracklet → phase → selector
          └─ Foam candidate → bounded episode
          ↓
same-frame selected observation만 수치 출판
          ↓
기존 CSV / events / report
```

모듈을 대체하는 전체 재작성은 하지 않는다. edge graph, support face, signed/unsigned alternatives, current-candidate index, native lineage 등 이미 있는 관측 표현을 사용한다. 같은 것을 다른 이름의 generator로 다시 만들지 않는다.

### 7.2 Foam raw-front 책임

**대상 owner:** `foam_front_detector.py`의 `_component_evidence`, `_detached_material_phenotype`, `detect_bottom_connected_foam`; 조립 경계는 `phase_frame_detection.py`, `phase_candidate_assembler.py`.

현재 `FoamComponentEvidence.front_y`에는 물질 support와 최종 상단 관측의 의미가 섞일 수 있다. 설계상 다음을 구분한다.

```text
component/support identity   : 어떤 실제 픽셀 집합을 측정했는가
observed boundary hypothesis: 어떤 현재 edge/path/face가 있는가
role decision               : Foam upper / internal texture / structure / unresolved
scalar eligibility          : 지정한 측정 X에 실제 관측이 존재하는가
selected candidate          : 위 조건을 통과해 downstream에 전달하는 한 관측
```

P5-b 구현에서 요구할 계약은 다음과 같다.

| 항목 | 구현 계약 |
|---|---|
| 후보 보존 | 물질 component를 하나의 global Y로 먼저 축약하지 않는다. 현재 관측된 후보의 정체와 양쪽 support를 보존한다 |
| 측정 위치 | P1의 central-sector pooled Y와 실제 fixed-X intersection을 동일시하지 않는다 |
| 역할 | white/warm, edge strength, 순위, bbox, motion은 단독 승인 근거가 아니다. 양성/대립/불확실 판별 근거가 먼저 필요하다 |
| 경로 불연속 | missing edge를 연결하거나 fitted curve에서 수치를 생성하지 않는다. scalar 없는 path evidence는 별도로 남길 수 있다 |
| downstream 전달 | `BoundaryCandidate`의 same-frame index/source/Y 및 역할 증거를 보존한다. 기존 후보 정렬 후 index로 재결합하지 않는다 |
| 누락 의미 | support 소실, role 불확실, fixed-X 부재, episode 미확인을 구분한다 |
| 자원 | 기존 crop·후보·윈도 cap을 유지하고 새 입력 수·byte 상한을 preflight에 명시한다. 초과는 명시적 unavailable이지 조용한 prefix truncation이 아니다 |

**중요:** 위 책임 분리는 필요한 설계이지 충분한 판별 방법이 아니다. 이미 실패한 upper-perimeter, side-entry, reference cost, relative-motion 방식을 이 인터페이스에 넣는다고 새 근거가 생기지 않는다. 현재 P5-b production consumer 진입은 아직 불가하다. 새 역할 가설이 실제로 성립하지 않으면 구조 변경만 먼저 합치지 않는다.

### 7.3 Oil association 책임

**대상 owner:** `oil_observation_resolver.py`, `oil_candidate_authority.py`, `oil_interface_tracklets.py`, `oil_phase_lifecycle.py`, `oil_interface_selector.py`.

역할 판별이 확보된 뒤 다음을 검증한다.

- 동일한 현재 관측을 여러 owner가 주장할 때, established 상태가 물리 증거를 대체하지 않게 한다.
- 고정된 association window 안에서 owner 유지·handoff·abstain을 평가하고, 새 owner는 독립적인 현재 근거가 있어야 한다.
- 모션만 있는 tracklet과 anchor-supported tracklet의 차이를 유지한다. 같은 Y 또는 더 낮은 cost는 물리 정체가 아니다.
- phase 허용 ID와 실제 publishable row ID가 어긋났을 때 원인을 드러내되, selector가 gate를 넘어 임의의 후보를 출판하지 않는다.
- 초기 EMPTY/FULL, rapid refill, partial-fill 후 drain, residue opposition을 전체 같은 설정으로 확인한다.

P3를 ‘cost-first 재실험’, P4를 ‘handoff predicate 한 줄 삭제’로 구현하지 않는다. 새 현재-frame 역할/target evidence 없이 이것을 진행하면 이미 폐기한 반사·texture 추적을 다시 만들 위험이 크다.

### 7.4 Foam episode 책임

**대상 owner:** `foam_episode_resolver.py`.

현재 max 4 offset / 2.0 source-second bounded witness, 실제 dynamic support, stable/directed formation, Oil과 독립인 publication을 유지한다. P5-c는 **올바른 raw upper front가 episode에 실제로 들어갔으나 잘못 소실된 별도 증거가 있을 때만** 연다.

현재 sample4 f1620의 Y833 거절은 이 조건에 해당하지 않는다. correct raw front의 실패를 가정한 뒤 episode를 조정하는 실험은 현재 우선순위가 아니다.

### 7.5 출판 책임

`detection_processing.py`, `analysis_outcome.py`, CSV/Graph/Report owner는 위 오류를 보정하는 장소가 아니다. 현재의 숫자·단위·validity·provenance를 유지한다. 본 작업에서 새로운 report 기능을 만드는 것은 원칙적으로 제외한다. 지원 범위의 의미를 기존 필드로 표현할 수 없는 경우만 최소 변경을 별도 승인한다.

---

## 8. 전체 작업 순서와 단계별 산출물

아래 작업은 기존 P0–P7/O0–O5 흐름을 대체하는 새 milestone 체계가 아니다. 현재 ledger에 적용할 **순서·완료 조건의 보완안**이다. 승인 전에는 PROPOSED다.

| 단계/기존 연결 | 작업·파일 | 완료 증거 | 진입/중단 조건 |
|---|---|---|---|
| P0 / 평가 계약 | 본 권고를 제품·Work Plan·validation owner에 반영할 채택 diff 작성. 주요 Oil/Foam episode와 story-impact 기준 고정 | 범위 밖 이유, positive/negative/unresolved inventory, 중요 장면과 허용 공백의 근거 | 사용자 범위 결정 없이 게이트 변경 금지. source 재질문은 이미 닫힌 범위에서 하지 않음 |
| P1 재사용 점검 | 기존 edge/support/native lineage와 scalar eligibility 연결 확인 | 원시 관측→후보→현재 역할/수치 경계가 보존됨 | 중복 generator나 전체 rewrite로 확대 금지 |
| P2 / 역할 연구 | 새로운 역할 가설이 필요하면 수식·입력·정규화·경쟁 모델·한 ablation을 사전 고정. 이번 S2 수학 감사 형태의 positive-admissibility 체크 추가 | 특징 가능 범위와 positive decision region이 호환됨. 실제 양성 보존·실제 구조 opposition이 함께 확인됨 | 기존 실패의 weight/radius/reference 변경만이면 진입 불가. no-op/전부 UNKNOWN은 실패 |
| P5-a / Foam 역할 | Oil association과 독립적으로 raw upper-front 역할 가설을 제한된 비용으로 검증 | sample4 upper, water A, B/C no-Foam, earlier front/rim/internal texture, cropped/unclear 모두 disposition 유지 | 양성조차 분류할 수 없는 모델은 대형 replay 전에 종료. 기존 S2는 재사용 승격 금지 |
| P5-b / raw front | 통과한 역할 근거만 기존 Foam owner에 연결. component extrema를 물리 front로 오인하지 않도록 책임 분리 | raw-front 유용성 + counter-control 비회귀 + same-frame provenance + OFF/NONE 동등성 | 판별기 없이 자료구조만 선행 병합하지 않음. 단일점 위치 일치만으로 채택 불가 |
| P3 / Oil association | 통과한 역할·대상 근거를 기존 typed authority/tracklet에 연결 | protected positive 유지, wrong target 대립, full-window owner consistency | cost-only/nearest-Y/매칭 성숙도 단독 근거 금지 |
| P4 / Oil phase | 선행 근거가 충분한 한 가지 phase 실패만 수정 | FULL/EMPTY, drain/refill, owner loss 전체 조건별 전이·방향 보존 | speculative Accum 변경 금지. 새 지속 wrong owner 발생 시 폐기 |
| P5-c / episode | correct raw front의 downstream 소실이 따로 증명된 경우만 | 그 후보가 실제 input이었음을 exact join, 원인 predicate, 양면 대조군으로 증명 | 현재 sample4 내부 texture의 거절을 FN으로 재분류하지 않음 |
| P6 / 통합·현장 | 정확한 단일 candidate head에 local integration/현재 canonical 계약 적용. 이후 Windows 9개 구간 로컬 실행 | 원시 관측 provenance, report 영향, 각 구간 PASS/FAIL/NOT_EVALUATED | 변경 없는 detector를 Windows에서 재실행해 역할 가설을 대신 찾지 않음. 반출 요청 금지 |
| P7 / 종료 | detector 효과·report 맥락·지원 범위를 종합한 disposition | 검증한 범위·남은 불확실·사용자 결론의 정합성, 재현 가능한 증거 | field 실패를 로컬 테스트로 덮지 않음. 미검증 범위는 솔직히 유지 |

### 8.1 실행 순서의 핵심

당장 필요한 것은 새로운 threshold chain이 아니다. 먼저 P0의 범위·story 평가를 고정하고, P2/P5-a 각각에서 **진짜로 다른 관측/측정 연산이 있는지** 판정한다. 없다면 이를 ‘다음 구현’이라고 포장하지 않는다.

반대로 P5-a가 막혔다는 이유만으로 P2의 Oil wrong-extrema 문제를 잊지 않는다. 두 경로 중 하나에 근거가 생기면 해당 consumer에만 제한적으로 연결한다. 통합 Windows 실행은 의미 있는 행동 후보가 생겼을 때 한 번의 정확한 후보 검증으로 묶는다.

### 8.2 연구 예산과 중단 규칙

연구의 상한은 시간 약속이 아니라 **한 preflight·한 hypothesis·한 structural ablation·고정 readout**으로 정의한다. 수행 후 결과를 보고 radius/threshold/reference를 연쇄 변경하지 않는다.

새 가설의 최소 입장권은 다음 다섯 항목이다: 기존 실패에서 없던 관측 또는 측정 연산, 그것이 물리 역할과 연결되는 이유, 같은 입력에서의 구조 대립 설명, missing/tie 정책, 양성이 실제 결정 영역에 도달한다는 증거. 하나라도 빠지면 implementation-ready가 아니다.

단계가 실패하면 실패 원인이 있는 단계까지만 기록한다. downstream 성능이 나쁘다는 이유로 upstream 관측을 사후 라벨링하거나, SOURCE_UNCLEAR를 자동 음성으로 바꾸지 않는다. 논문·제품 비교는 이 입장권을 대신하지 못한다.

---

## 9. 검증 설계: 프레임 정답률 대신 무엇을 볼 것인가

### 9.1 영향도 층위

| 층위 | 예 | 처리 |
|---|---|---|
| A — 맥락을 뒤집는 오류 | 구조물을 따라 지속 상승/하강; wrong target이 전체 최고·최저점; Foam 내부선을 Oil로 교체 | 핵심 실패. 단일 프레임이어도 주요 결론을 바꾸면 우선 수정 |
| B — 주요 사건을 놓침 | 가시적 reversal/rapid refill 대부분 누락; Foam 관측 흐름 단절 | 지정 episode에서 유용성 미달로 평가 |
| C — 맥락을 보존하는 작은 오류 | 짧은 누락·소폭 흔들림, 중요한 방향·극값·사건을 바꾸지 않는 불연속 | 숨기지 않고 보고하되 개별 100% 해결을 종료 조건으로 두지 않음 |
| U — 평가 불가능 | source 가림/blur, 역할·시각·정확 위치 truth 부족 | NOT_EVALUATED/범위 명시. 맞음 또는 틀림으로 강제 계산하지 않음 |

오류 영향도는 결과를 본 다음 유리하게 바꾸는 가중치가 아니다. source에서 중요하다고 확정된 구간과 주요 질문을 먼저 고정해야 한다.

### 9.2 지표

**Oil:** 관측 가능·움직임 확인 구간에서 (a) 같은 물리 interface의 사용 가능한 관측 수, (b) 그 관측 사이 실제 timestamp gap과 최대값, (c) 시작·끝 미관측 시간, (d) 지속 wrong run과 longest missing run, (e) 방향·반전·극값을 결정한 후보의 정체를 보고한다.

**Foam:** upper-front 양성 보존, 실제 no-Foam 구간 false episode, internal texture/rim을 front로 선택한 시간, onset/last-observed/physical disappearance의 구분, 상단 가림과 lower 불명확을 각각 보고한다. 현재 qualified interval은 개별 source frame의 위치 범위이며 주변 시간 truth로 확장하지 않는다.

**Report:** 같은 저장 결과로 생성한 기존 report를 보여 주고 ‘하강/상승/반전/정체를 어떻게 읽는가, 최저/최고는 실제로 타당한가, Foam이 보인 시점과 이후 관측 한계는 무엇인가’를 평가한다. detector debug를 먼저 보여 주어 정답을 유도하지 않는다. 이번 agent 검토는 원인 증거를 이미 알고 수행했으므로 독립적인 report comprehension 실험으로 세지 않는다.

수치 precision·recall이 필요한 경우 물리 label의 분모를 명시한다. native/reduced, 중복 frame, 같은 episode의 인접 관측을 독립 성공 수로 합산하지 않는다. 새로운 설정을 고르기 위한 threshold sweep용 지표로 사용하지 않는다.

### 9.3 고정 대조군의 사용 범위

| 자료 | 검증하는 것 | 검증할 수 없는 것 |
|---|---|---|
| sample4 7 Oil checkpoints/3 wrong target | 확인된 candidate 정체 보호·opposition | 모든 인접 row·tracklet의 정확한 정체 |
| sample4 f1305/43.5초 | 표시된 지역에서 Oil 위치가 존재, owner 소실 원인 | 모든 후보의 exact-Y 정답·전체 track truth |
| sample4 f1620 X595 [811.5,816.5] | Foam upper 위치 interval compatibility | 전체 contour, 이웃 X/frame, 두께 |
| sample4 Y833/837/838 | 검토된 내부 texture를 front로 채택하지 않음 | Canny query가 없을 때 성공적인 분류라고 평가 |
| water A X950 [475.5,481.5] | dark upper Foam 양성 | lower Oil 경계나 두께 |
| water B/C | water upper 위치·Foam 부재 대조 | 영상 전체 Foam precision |
| beer | 앞/뒤 투영과 top crop 구분 | 두 projected arc를 서로 다른 물질층으로 계산 |
| milk | 흰 액체/표면 froth와 불명확 lower 구분 | 불명확 lower에 숫자 부여 |
| base/sample2 기존 truth | 허용된 legacy engineering/경계 의미의 회귀 | 새 fixed-X dense truth, 분쟁 annotation의 자동 정답화 |
| sample3 | 기존 quarantine/legacy regression 규칙 보존 | 새 usable interval 채굴·gap 개선용 튜닝 |

---

## 10. Windows 현장 검증: 9개 구간을 유지한다

source 파일은 Mac에 없으며 이번에 Windows 영상을 열거나 detector를 실행하지 않았다. 아래 요구는 이미 채택된 source-reviewed timeline을 따른다. 새 후보가 생긴 이후 Windows에서 실행하고 사용자가 보고서/텍스트로 결과를 전달하는 절차다. [R12]

| Segment ID | source 시간 | 확인할 운동 맥락 |
|---|---|---|
| WS1-BASE-FULL-PREFIX | 480–약 550초 | full material/no interface; 숫자 Oil/Foam을 만들지 않음 |
| WS1-BASE-DRAIN | 약 550–662초 | 실제 oil-air boundary의 하강, structure/glare 대체 추적 금지 |
| WS1-BASE-RAPID-REFILL | 662–약 663.6초 | 급상승 후 상단 소실/filled closure, 다른 row로 owner 이전 금지 |
| WS1-BASE-FULL-SUFFIX | 약 663.6–780초 | full/no interface 유지, 반사 row를 유면으로 만들지 않음 |
| WS1-ACCUM-EMPTY | 480–약 653초 | Oil/Foam 부재, 숫자 생성 금지 |
| WS1-ACCUM-ENTRY-SPLASH | 약 653–672초 | 실제 rising Oil와 splash/wall mark 구분, Foam은 아직 아님 |
| WS1-ACCUM-FOAM-LAYERED | 약 672–680초 | upper Foam과 lower Oil/Foam boundary를 독립적으로 보존 |
| WS1-ACCUM-POST-FOAM | 약 680–700초 | Foam 소멸 후 Oil 유지, 잔류물을 Foam으로 이어 가지 않음 |
| WS1-ACCUM-DRAIN | 약 700–780초 | Oil 반전·하강, wall residue로 owner 교체 금지 |

각 구간은 실제 sampled coverage, numeric count/run, Y 범위·방향, longest missing/wrong run, owner/phase 전이, PASS/FAIL/NOT_EVALUATED를 별도로 기록한다. 과거의 ‘52 real Foam rows’ 같은 detector cohort 수는 oracle가 아니다.

보안 PC 밖으로 video/image/ZIP을 요청하지 않는다. 기존 alias와 사용자의 same-video 확인에 기반한 identity와, 아직 기록되지 않은 source hash/fingerprint를 구분한다. source identity 보완은 다음 정당한 Windows 검증 시 로컬에서 수행할 수 있지만 현재 역할 연구를 위해 별도 재실행을 요구하지 않는다.

---

## 11. 외부 기술 검토의 의미와 한계

KRÜSS의 DFA100 적용 보고서는 Foam upper/lower 높이를 LED bar와 반대편 line sensor로 측정하고, bubble structure는 별도의 prism/camera 구성으로 분석한다고 설명한다. 이는 **높이·구조·물질 해석을 분리**한다는 설계 참고가 된다. 하지만 현재 sight-glass 영상에 그 측정기의 광학 조건이 존재하는 것은 아니다. 제품 성공 사례를 현재 작은 ROI의 일반 RGB 영상 판별 성공으로 전이하지 않는다. 새로운 장비나 재촬영을 이번 작업의 조건으로 요구하지 않는다. [X01]

판별을 보류하는 시스템은 coverage와 error risk를 함께 평가해야 한다는 selective-classification 연구의 관점도 참고할 수 있다. 여기서는 평가 개념만 사용한다. 해당 논문의 학습 알고리즘 또는 noise-free 이론 보장을 이 프로젝트에 적용했다는 뜻은 아니며, ML 제외 제약도 그대로다. **오류가 줄었다는 이유만으로 거의 모든 출력을 지우는 결과를 채택하지 않는다.** [X02]

---

## 12. 재현 방법과 전달 파일

### 12.1 전달 파일

```text
S11_PROGRAM_DECISION_AND_WORK_SPEC.md   본 명세
README.md                             읽는 순서·실행/제안 경계
HANDOFF.md                            다음 구현자의 짧은 인수인계
STORY_ACCEPTANCE_TEMPLATE.json         평가 양식; 새 truth나 PASS가 아님
evidence/
  session-audit-summary.json           이번 수행 범위·결과 요약
  verifier-stdout.json                 재실행 stdout의 전사본
  s2-decision-geometry.json             추가 수학 감사의 전사본
  focused-tests.log                    집중 테스트 stdout 전사본
tools/
  audit_s2_decision_geometry.py         재현용 stdlib 감사 도구
  reproduce.sh                        기존 verifier/테스트 재실행 명령
MANIFEST.sha256                        배포 파일 해시
```

전사본은 tool에서 읽은 실제 결과를 옮긴 것이다. 추가 수학 감사 JSON과 Python 도구는 Mac 실행 원본의 SHA-256과 **byte equality**까지 확인했다. verifier stdout 요약은 대형 원본 verification receipt의 전체 사본이 아니다. 모든 원본 receipt는 위 Mac audit 경로에 보존되어 있다.

### 12.2 S2 추가 감사 재현

```bash
python3 tools/audit_s2_decision_geometry.py \
  --root /absolute/path/to/oil_level_tracker \
  --out /tmp/s11-decision-geometry-new.json
```

이 감사는 checked-in S2 `readout.json`과 `preflight.json`만 읽는다. MP4·OpenCV·저장 raster가 필요하지 않다. source geometry와 cost triple만 확인하며 detector나 classifier를 실행하지 않는다. 출력 경로가 있으면 덮어쓰지 않는다.

**반면 원래 S2/P2 pixel verifier와 default linkage verifier는 repo의 ignored `sample/output` raster·trace·replay 파일이 필요하다. ZIP만으로 해당 검증 전체를 재현할 수 없다.** 누락되면 새 숫자를 만들거나 임의 대체하지 말고 원본 필요를 명시한다.

### 12.3 이번 실행 결과를 해석하는 규칙

162 tests PASS, verifier 3종 PASS, 수학 감사 VERIFIED를 합쳐 detector 효과 PASS로 변환하지 않는다. 효과가 증명된 새 역할 모델은 없고, 운영 소스·episode·field disposition은 바뀌지 않았다.

신규 구현 전 정확한 checkout을 다시 확인한다. 이후 main이 바뀌면 본 문서를 현재 상태로 읽지 말고, 아래 pinned source와 새 Work Plan 간 차이를 먼저 확인한다.

---

## 13. 기존 문서와의 관계 및 채택 절차

본 문서는 10/01·10/07·10/08·10/10·10/11의 기존 audit, P1 구현, P2/P5 폐기 결론을 대체하지 않는다. `5c53aef`에 고정한 **방향 판단 보완**이다. 특히 다음은 그대로 유지한다.

- P2-S1/S2의 CLOSED WITHOUT PROMOTION과 frozen preflight.
- 기존 source reply 및 정확 위치·지역 해석·불명확 truth의 구분.
- current logic map의 단일 composition, 독립 Oil/Foam, same-frame scalar.
- sample3 quarantine와 Windows 보안 경계.
- Local XY OFF, O2 OPEN, FIELD FAIL.

채택 시 변경 위치는 다음처럼 나눈다.

| 결정 내용 | 수정 owner |
|---|---|
| 현재 진행 순서·명시적인 범위 결정 | `docs/00-project/work-plan.md` |
| 목표·지원 범위·사용자 해석 계약 | `docs/rotary_oil_level_tracker_ssot_spec.md` |
| 관측/역할/scalar 책임과 새 가설 사전 조건 | `docs/20-architecture/s11-interface-observability-witness-architecture.md` |
| positive-admissibility, story-impact, 역할/시간/좌표 평가 | `docs/30-validation/s11-interface-observability-witness-validation.md` |
| 이번 완료 감사·S2 수학 결과 | 채택 시 `docs/50-diagnostics/s11/` 또는 `60-evidence/s11/` |
| 실제 detector owner가 달라질 때 | current logic map 및 필요할 때 failure registry |

roadmap의 milestone DONE 상태나 S11의 FIELD FAIL을 문서 정리 때문에 바꾸지 않는다. 기존 owner 문서를 복사한 평행 SSOT를 만들지 않고 짧은 current state에서 증거 문서를 링크한다.

---

## 14. History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: current R22/R22-3 ownership; F02 proposal representation; F07 component-extreme, white/warm, gap, relative-motion, two-side transport, joint reference, support boundary and current-perimeter comparisons; P2-S1 regional competing exemplars; P5-S2 signed conjunction; default-linkage proof; Oil established-first counterfactual; current Windows reviewed truth.
- Prior mechanisms rejected: threshold/radius/reference rescue of closed models; global extrema substitution; white/chromatic union; motion/nearby edge as physical authority; cost-first-only association; episode relaxation for internal texture; carry/interpolation/report repair; private-identity branches.
- Preserved contracts: independent Oil/Foam authority, bounded state/resources, single composition, same-frame selected candidate provenance, source-bound truth, explicit unavailable, sample3 quarantine, no ML/new filming/private-media export, no silent gate relaxation.
- Difference from prior failures: this review adds an analytic decision-region and ablation-range audit, checks it against all saved S2 costs, and ties project priorities to wrong extrema/report movement. It does not introduce another physical classifier or claim a new observation mechanism.
- Logic-map impact: NONE — current runtime ownership and production behavior are unchanged; proposed consumer contracts remain conditional on later adoption and evidence.
- Failure-registry impact: NONE — known material/structure confusion and provenance constraints remain; the added mathematical explanation closes no new field mechanism and does not rewrite prior results.

## 15. Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: for qualified sample4 f1620, default component-to-front reduction discards the available upper alternative and passes internal Y833; water A separately loses appearance support at the lightness predicate. The Oil 43.5-second final owner restriction is source-qualified at regional scope, with assignment/phase causes captured previously. The S2 mathematical result concerns its unused offline model only, not a newly proved Windows first cause.
- Logic-map impact: NONE — saved-output verification and external proposal only; no production/resolver/publication changes.
- Failure-registry impact: NONE — existing mechanisms cover the observed failures; no new field efficacy or classifier promotion is asserted.

---

## 16. Source index — pinned at 5c53aef

아래 경로는 모두 `teeeeooo/oil_level_tracker @ 5c53aefe3bb3c5d1447b29ccb2f78d1adc5459c6` 기준이다. 문서 내부 인용 [Rxx]는 이 표를 가리킨다. 최신 파일의 상태가 이후 바뀌어도 이 검토의 근거는 바뀌지 않는다.

| ID | 경로 / 확인 내용 |
|---|---|
| R01 | `docs/rotary_oil_level_tracker_ssot_spec.md` — §1.2, source lines 65–71: 판독 보조·운동 맥락·Oil 1초 개발 목표 |
| R02 | `docs/00-project/work-plan.md` — next transition, lines 377–430, 783–886: 현재 gate·실패·method/security/authorization |
| R03 | `docs/00-project/roadmap.md` — milestone map |
| R04 | `docs/20-architecture/s11-current-detector-logic-map.md` — source lines 86–266: 실제 owner/흐름/불변식 |
| R05 | `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` — indexes, F01/F02/F07 및 연결 인과 증거 |
| R06 | `sample/output/s11-p5-default-linkage-20261011-001/none/report.json`, `tracking.json`, `summary.json` 및 실제 detail graph — ignored 파일; R09 manifest/verifier에 연결됨 |
| R07 | `docs/50-diagnostics/s11/2026-10-10-cadence-owner-causality.md` — owner 충돌·counterfactual·protected/wrong observations |
| R08 | `docs/50-diagnostics/s11/2026-10-11-foam-upper-position-review.md` 및 reply/comparison JSON — source interval과 raw 단계 연결 |
| R09 | `docs/50-diagnostics/s11/2026-10-11-p5-default-linkage.md`, 같은 이름 폴더의 preflight/readout/verify.py — default 동일성·최초 손실 단계 |
| R10 | `docs/50-diagnostics/s11/2026-10-10-abc-source-interval-comparison.md` 및 R08의 A/B/C 재확인 — dark upper/물 표면/불명확 lower |
| R11 | `docs/50-diagnostics/s11/2026-10-11-p2-shared-support.md`, 같은 이름 폴더의 preflight/readout/verify.py — 양성 0/6과 dominance witness |
| R12 | `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` — source lines 39–54, 78–102: 9개 구간·평가·source identity |
| R13 | `docs/50-diagnostics/s11/2026-10-11-p5-spatial-conjunction.md`, 같은 이름 폴더의 preflight/readout/verify.py — frozen S2와 전체 결과 |
| R14 | `docs/20-architecture/s11-interface-observability-witness-architecture.md` — source lines 1755–1895: boundary-local/default/S2 계약 |
| R15 | `docs/30-validation/s11-interface-observability-witness-validation.md` — O2/O3, local-source qualification, cadence, P2/P5 entry |
| R16 | `sample/README.md` — source/Recipe, legacy truth, sample3 quarantine, public media 용도 |
| R17 | `docs/README.md`, `docs/00-project/execution-policy.md`, `.agents/skills/s11-detector-change/SKILL.md`, `docs/30-validation/s11-detector-change-governance.md` — 문서·실행·변경 권한 |
| R18 | `src/oil_tracker/adapters/vision/foam_front_detector.py` — `FoamDecisionStatus`, `FoamComponentEvidence`, `FoamDetectionResult`, component/front owner |

외부 1차 자료:

- **X01:** KRÜSS Scientific, *AR279 — Foam behavior of toothpaste*, Measuring method and parameters. `https://pceu.kruss-scientific.com/en/know-how/application-reports/ar279-foam-behavior-of-toothpaste` (접근 2026-10-11). 장비의 광학/측정 책임 구분 참고이며 현 프로젝트 성능 증거가 아니다.
- **X02:** Ran El-Yaniv, Yair Wiener, *On the Foundations of Noise-free Selective Classification*, JMLR 11 (2010), 1605–1641. `https://jmlr.org/beta/papers/v11/el-yaniv10a.html` (접근 2026-10-11). risk–coverage 평가 관점만 참고; 학습·이론 보장 도입 없음.

---

## 최종 판단

**중단해야 하는 것은 detector 개발이 아니라, ‘모든 시각적 혼동을 먼저 해결해야 실용적인 결과를 낼 수 있다’는 무제한 선행 조건이다.**

현재 가장 확실한 제품 장애는 잘못된 Oil 후보가 중요한 극값을 결정하는 것, 그리고 가시적인 Foam 상단이 raw-front 선택에서 내부 무늬로 대체되는 것이다. 이 둘을 generic·same-frame·bounded 방식으로 개선하고, 사전에 정한 관측 범위에서 실제로 운동 맥락을 보존하는지 확인한다. 일부 누락을 허용하되 주요 물리 사건을 지우거나 뒤집지는 않는다.

이번 감사는 그 구현을 승격할 판별기를 확보했다고 보고하지 않는다. 대신 실패한 S2를 과도한 불가능성 주장 없이 수학적으로 설명하고, 지금까지 축적한 증거를 납품 목적·책임 경계·후속 작업·정지 조건으로 연결했다. 현재 상태는 그대로 **O2 OPEN / FIELD FAIL**, 권고 방향은 **검증된 범위의 자동측정 + 운동 맥락 중심 평가**다.
