# S11 전반 재검토 및 Detector 작업 명세 — CR1 이후

- 작성일: 2026-10-12
- 검토 기준 HEAD: `0bc5af74dc0818a166fc99f7bbdf3b05cd7b65f1`
- 최신 결과: `docs/50-diagnostics/s11/2026-10-12-cr1-context-comparison.md`
- 문서 성격: **현황 감사 + 후속 설계 제안 + 실행 명세**. 승인된 구현·운영정책·field acceptance가 아니다.
- 현재 상태 유지: **S11 ACTIVE / field FAIL / O2 OPEN / Local XY OFF**. field FAIL은 유지 중인 프로젝트 disposition이며, 이 HEAD에서 새로 실행한 Windows 결과가 아니다.
- 변경 범위: 이번 작업은 read-only 검증과 대화 산출물 작성이다. repository의 생산 코드, Recipe, truth, Work Plan, 환경, 모델, 캐시는 변경하지 않았다.

## 0. 결론

**전면 재작성보다는 물리적 역할 판단과 후보 채택 경계를 부분 재설계하는 것이 적절하다.** 현재의 후보 보존, 단계별 관측, Oil/Foam 독립성, bounded tracklet/lifecycle, same-frame publication 및 report 기반은 유지한다. 반면, 영상 특징이 물리적 Oil/Foam 경계라는 판단으로 바뀌는 지점은 개선해야 한다. Foam은 별도로 실제 상단을 raw 후보로 표현하는 문제를 먼저 해결한다. [E01–E06]

CR1은 폐기할 결과도, 바로 detector에 연결할 결과도 아니다. **분류명만 비교하면 잃어버리는 연속 점수 정보가 남아 있다.** 이번 재계산에서 44초 오후보와 49.5·52초 정후보의 local 계면 유사도가 약 0.443 / 0.727 / 0.820으로 구분됨을 확인했다. 다만 Foam 내부 무늬에도 약 0.727이 나오므로 절대 유사도만 사용하는 방법 역시 충분하지 않다. 따라서 다음 연구 가설은 새 모델 탐색이 아니라 **기존 고정 local 표현의 절대 지지도와 역할 간 경쟁을 함께 보존하는 작은 운영정책**으로 한정한다. 임계값은 이 노출된 결과에 맞춰 정하지 않는다. [E03, N01]

프로젝트 목표는 모든 후보·프레임의 정답이 아니다. 다음 두 판단을 분리한다.

1. **국소 기능의 진전:** 특정 오선택을 줄이거나 실제 경계를 더 오래 보존하는 검증된 개선. 다른 문제가 남아 있어도 그 개선 자체를 부정하지 않는다.
2. **제품 목적의 달성:** report에서 주요 상승·하강·반전·회복·Foam 사건을 잘못 이해하게 만들지 않고, 중요한 움직임을 충분히 관찰할 수 있는가. 여기에는 기존 9개 Windows 구간의 검증이 필요하다.

따라서 CR1의 한 충돌 사례를 이유로 모든 후속 연구를 막지 않는다. 반대로 두 오선택을 줄였다고 잘못된 최대값·긴 관측 공백·Foam 역할 혼동이 남은 report를 성공 처리하지 않는다. **일부 오류 허용과 오류의 영향 무시는 서로 다르다.** [E02, E07]

---

## 1. 이번에 실제로 확인하고 실행한 범위

### 1.1 입력과 검토 범위

연결된 Mac checkout에서 AGENTS/skill, Work Plan, roadmap, 실행·artifact 규칙, detector logic map, 실패 registry, 관측/검증 계약, 최신 CR1 산출물, 이전 program-review intake, sample 설명과 Windows reviewed truth를 읽었다. 핵심 authority/phase identity/peer-support 코드도 직접 확인했다. [E01–E12]

영상은 sample4와 공개 압축기 영상의 기존 검토 프레임을 원본에서 다시 디코딩했다. 기존 CR1 비교 이미지, sample4 Foam 상단 검토 이미지, 공개 압축기 Oil/Foam 범위 이미지, 물 영상의 raw-support 단계 이미지, 실제 report graph도 확인했다. **전체 영상의 새 정답 라벨링이나 독립적인 사용자 이해도 시험을 수행한 것은 아니다.** sample3은 재디코딩하지 않았다.

### 1.2 새 실행 결과

| 수행 | 이번 결과 | 증명하지 않는 것 |
|---|---|---|
| 기존 `verify_followup.py` 재실행 | PASS; 164 records, 135 measured variants, 270 score-rank checks, 167 support checks, 24 duplicate groups, 생산 Python 221개 불변 | CR1의 물리적 정확도·일반화 |
| 저장 점수 독립 재집계 | full/local 조합, 원시 계면 유사도 범위, 모든 후보 내 점수 경쟁, 추가 texture/rim 대조 확인 | 임계값 채택·새 selector |
| sample4 원본 대조 | 기존 저장 ROI 11개가 동일 source frame의 원본 crop과 일치 | 11개가 독립 표본이라는 주장, 중간 프레임 정답 |
| 공개 압축기 원본 대조 | f1499, 실제 50.016633333초 원본이 보존 PNG와 일치 | 1초 구간 또는 전체 영상의 정확도 |
| 기존 report CSV/event 재집계 | 113 tracking rows, Oil 유효 수치 101, Foam 유효 수치 26, events 31 | 수치 유효성이 물리적 정답이라는 주장 |
| 기존 cadence 계산 재사용 | 수치 관측 간격 최대 2.5초; 100쌍 중 98쌍 ≤1초, 2쌍 >1초 | 물리적 동일 계면 cadence PASS |
| 관련 pytest 재실행 | **109 passed in 8.81s** | 전체 test suite·Windows·detector 효과 검증 |
| 동봉 audit 스크립트 검증 | Mac REPL에서 동일 소스를 실행, 기존 검증기 PASS와 12개 고유 source-frame 대조 재현 | CLI 전체 배포/설치 시험 |

동봉 `audit_cr1_saved.py`의 실제 실행 소스 SHA-256은 `b31773b892d0f5fddd3794051a207896016a986a96a86e779549a211eca09c8c`이다. 산출물 파일의 해시와 일치한다. 동일 12개 고유 프레임을 직접 검사 및 wrapper 재검증에서 두 번 읽었으므로, 전체 작업의 디코드 호출은 24회다. detector나 encoder의 추가 실행은 없다. [N01]

실행한 tests:

```text
tests/unit/test_s11_observation_cadence.py
tests/test_center_path_diagnostics.py
tests/unit/test_source_context_renderer.py
```

작업 전후 HEAD는 동일하고 `git status --short`는 비어 있었다. 원본 영상, 기존 대형 trace, 모델·캐시를 대화 산출물로 복제하지 않았다.

---

## 2. 프로젝트 전체 진행 상태

### 2.1 완료된 기반과 남은 제품 문제

| 영역 | 확인된 진행 | 아직 남은 판단 | 이번 권고 |
|---|---|---|---|
| S1–S10 및 기본 사용 흐름 | roadmap상 DONE | S11 detector field qualification과 별개 | 유지; UI 재작성으로 우회하지 않음 |
| R22/O1 관측·계보·추출 | 로컬 수용 및 검증 기반 확보 | 물리적 역할 판단은 자동으로 따라오지 않음 | 재사용; 새 계측기 남발 금지 |
| 후보·authority·tracklet·lifecycle | bounded 소유권 구조 및 회귀 가드 존재 | 잘못된 구조도 anchor/continuation으로 통과 가능 | 역할 증거 접점만 좁게 변경 |
| report source-context와 관측 표시 | 실제 bundle과 시각적 보조 기반 존재 | 오선택이 극값·방향 설명을 왜곡하는지 실사용 판정 미완료 | 기존 report로 A/B; 표시 변경을 검출 개선으로 계산하지 않음 |
| W4/P2 및 CR1 | 고정 표현 비교·유용성 해석 완료 | 분류명 → 물리적 역할/운영정책 변환 미검증 | 제한된 operating-policy 실험 설계 |
| O2/V2–V5 | OPEN | 독립 calibration/holdout, calibrated typed outcome, Windows shadow | 우회하지 않음 |
| O3/W5 | 후속 behavior 경계 | 새 증거가 후보 채택·연속 관측에 주는 효과 | O2 이후 단계별 실험 |
| O4/W6 | handoff/phase 후속 경계 | FULL/EMPTY, 급상승·반전·재획득 보존 | 역할 문제를 motion 완화로 고치지 않음 |
| Foam P5-a/b/c | raw-front 원인과 default 연결 확인 | 실제 상단 역할·좌표 표현 및 후속 episode 효용 | a → b, c는 조건부 |
| O5/W7/P6 및 P7 | 통합·현장·종결 미완료 | 9개 Windows story와 독립 report 이해도 | 명시적인 최종 종료 조건으로 유지 |
| S11-M / S12 | PLANNED | S11 field gate 이후의 별도 작업 | 지금 detector 범위와 섞지 않음 |

이는 완료율 계산표가 아니다. 기반 구현의 양이 많다는 사실과 실제 압축기에서 목적을 달성했다는 사실은 별개다. 현재 증거만으로 “거의 완료” 또는 임의의 진척률을 부여하지 않는다. [E01, E02]

### 2.2 이력에서 유지해야 할 교훈

R1–R10에서는 표시/관측성 개선, 후보 보존, motion/고재현율 bootstrap이 진행됐으나, 수치 증가가 실제 Oil/Foam 검출 증가를 의미하지 않았다. R11–R17은 역할·물리적 소유권·상태·독립 Foam 경계를 더 명확하게 만들었다. R18–R22는 lifecycle, 제한된 재획득과 진단을 보강했다. 최근 Local XY, reference/LK, gap/side-transport, support 보존, CR1은 각각 다른 관측 가능성을 시험했지만, **연속성·외형 유사성·geometry만으로 역할을 확정하는 오류**는 반복 가능한 회귀 위험이다. [E05]

이 이력은 “새 시도를 하지 말라”는 뜻이 아니다. 다음 시도는 어떤 새로운 정보가 어느 잘못된 판단을 바꾸는지, 어떤 실제 경계를 함께 잃을 수 있는지 명확해야 한다. 이미 닫힌 실험의 결과를 재해석하여 PASS로 만들거나, 같은 연산에 새 이름을 붙이는 방식은 피한다.

---

## 3. CR1 결과의 재해석

### 3.1 원 실험과 후속 유용성 검토는 별개다

첫 CR1 trial은 정해진 progression 조건을 충족하지 못해 `CLOSED_WITHOUT_PROMOTION`으로 닫혔다. 이후 사용자가 채택한 별도 usefulness 검토는 기존 두 결과를 보존한 채 나머지 기록을 한 번 평가했다. 최신 `SCOPE_LIMITED_USEFULNESS`는 원 실험 실패를 뒤집는 표현이 아니다. 이번 문서도 그 상태를 유지한다. [E03]

### 3.2 분모

| 구분 | 수 |
|---|---:|
| 전체 기록 | 164 |
| 후보 / 별도 context control | 160 / 4 |
| 완전히 측정 불가 | 32 |
| 정수 anchor variant / 측정 variant | 167 / 135 |
| 동일 좌표 중복 group | 24 |
| reference episode 밖 development / 근방 diagnostic / reference self | 91 / 71 / 2 |
| 라벨 UNREVIEWED | 150 |
| 독립 원본 recording / 미노출 holdout recording | 1 / 0 |

사람이 확인한 Oil 후보 비교는 self를 빼면 정후보 6개·오후보 3개다. 그중 reference episode 밖 비교는 정후보 4개·오후보 1개뿐이다. 근방 진단, reference self, 내부 texture 및 agent-provisional rim을 동일한 정확도 분모에 섞지 않는다. 동일 좌표·동일 픽셀을 본 후보 둘은 독립 성공 둘이 아니다. [E03, N01]

### 3.3 분류명 조합으로만은 식별할 수 없는 사례

| 기존 라벨 | full / local | non-self 기록 수 |
|---|---|---:|
| 정후보 | interface / interface | 4 |
| 오후보 | structure / structure | 2 |
| 정후보 | texture / interface | 2 |
| 오후보 | texture / interface | 1 |

마지막 두 행의 충돌은 49.5·52초 정후보와 44초 오후보다. 이 9개 기록에서 **두 분류명만 입력으로 받는** 결정 규칙은 세 기록을 서로 다르게 처리할 수 없다. 오류 없는 비기권 결정을 요구하면 최대 6개까지만 결정할 수 있고, 모두 이진 결정하면 최소 한 오류가 남는다. 이는 해당 범주 정보에 대한 유한 집합의 산술적 한계다. **실제 classifier의 정확도 한계도, 부분 개선의 불가능성도 아니다.** 연속 점수·현재 경계·검증된 역할 증거를 추가한 정책에는 이 증명이 적용되지 않는다. [N01]

전체 164개 기록의 full/local 조합은 interface/interface 41, structure/structure 37, texture/interface 28, structure/interface 17, texture/texture 9, 양쪽 미결정 32다. 두 분류명을 단순 AND/OR로 결합하면 UNREVIEWED 후보까지 광범위하게 영향을 받는다. 소수 라벨의 결과를 전체 후보의 물리적 라벨로 확장해서는 안 된다.

### 3.4 이번에 재확인한 연속 점수 정보

`a_L = local의 interface similarity`, `m_L = interface similarity − max(structure similarity, texture similarity)`로 원시 값을 설명한다. 이는 새 score를 detector에 구현했다는 뜻이 아니라, 저장된 세 값을 산술적으로 읽은 것이다.

| 검토된 대상 | local 선호 | a_L | m_L | 의미 |
|---|---|---:|---:|---|
| 44초 오후보 Y822 | interface | 0.442885 | +0.068245 | 가장 가까운 class지만 계면 reference와의 절대 일치는 약함 |
| 49.5초 정후보 Y836 | interface | 0.726906 | +0.015512 | 절대 일치는 높지만 texture와의 차이는 작음 |
| 52초 정후보 Y833 | interface | 0.820188 | +0.001624 | 매우 작은 class margin이 실제 경계를 배제할 근거는 아님 |
| 55.5초 내부 Foam texture control | texture | 0.727457 | −0.147952 | 절대 계면 유사도만 보면 실제 경계와 겹침 |

self를 뺀 6개 정후보와 3개 오후보의 local interface similarity 범위는 각각 `[0.726906, 0.858818]`, `[0.310843, 0.442885]`다. fractional anchor는 floor/ceil 값을 모두 포함했다. full도 이 소집합에서는 정후보 `[0.642332, 0.878205]`, 오후보 `[0.363677, 0.423395]`로 분리된다. **그러나 texture 대조까지 넣으면 절대 점수 범위가 겹친다.** [N01]

따라서 다음 세 결론을 함께 유지한다.

- class argmax만 소비하는 정책은 유용한 연속 정보를 버린다.
- 절대 유사도 하나 또는 “margin이 클수록 더 신뢰”라는 규칙도 충분하지 않다.
- 절대 지지도와 역할 경쟁을 함께 보존한 작은 정책은 검토할 근거가 있다. **이 자료에서 숫자를 골라 바로 적용할 근거는 없다.**

특히 52초 정후보를 잃지 않으려면 임의의 큰 margin floor를 추가하지 않아야 한다. 그렇다고 작은 margin이면 모두 수용할 수 있는 것도 아니다. 결측·동률·분수 anchor 불일치, 지역 역할/좌표 해상도와 calibration을 함께 다룬다.

### 3.5 점수 순위가 곧 후보의 정답은 아니다

모든 측정 가능한 같은 프레임 후보를 비교하면 local interface similarity 최고점 Y는 38초 840, 40초 841, 42초 837, 42.5초 835, 44초 845, 49.5초 841, 52초 833이다. 알려진 정후보 Y는 각각 844, 841, 839, 835, 844, 836, 833이다. 미검토 최고점은 실패라고 단정할 수도, 정후보와 가깝다는 이유로 같은 계면이라고 단정할 수도 없다. [N01]

**49.5초 Y841**은 full과 local 모두에서 알려진 Y836 정후보보다 interface similarity가 높다. 따라서 “연속 점수 정보가 남아 있다”는 발견도 최대 점수 후보를 자동 선택하는 정당화가 되지 않는다.

반대로 정후보와 1–5 px 차이가 나는 후보를 모두 별개의 실패로 세고 유일한 candidate ID를 강제하는 것도 목적에 맞지 않는다. 같은 물리적 경계의 표현 차이인지, 다른 구조인지부터 보며, 기존 region/interval truth가 실제로 허용하는 범위까지만 판단한다. **새로운 ±5 px 허용치나 후보 라벨을 만들지 않는다.**

### 3.6 CR1의 권고 disposition

`SCOPE_LIMITED_USEFULNESS` 유지. 다음의 단일 정책 가설을 개발용으로 설계할 가치가 있다.

> 고정 local 표현에서 interface가 수치적으로 유일한 선호이고 절대 계면 지지도가 충분한 경우만 새로운 역할 지지의 후보로 삼는다. full이 texture를 선호한다는 사실을 보편적인 거부로 사용하지 않는다. 실제 수치 발행은 native 후보·물리적 역할·bounded 소유권을 별도로 통과해야 한다.

이는 **새 가설**이다. source-separated calibration, 대조 및 실제 report 효과 검증 전에는 역할 지지도나 detector 개선으로 채택하지 않는다. 기존 encoder/bank/전처리의 대규모 재탐색, 모델 교체, training은 이번 후속 범위에 포함하지 않는다.

---

## 4. 제품 목적에 맞춘 평가 기준

### 4.1 무엇을 최적화할 것인가

우선순위는 평균 검출률이 아니라 다음 순서다. 이는 새 수치 가중치가 아니라 기존 P0의 task-impact 기준을 실행 가능한 순서로 정리한 것이다. [E07]

| 우선 | 질문 | 수용 판단 |
|---|---|---|
| 1 — 잘못된 핵심 설명 방지 | 다른 구조를 따라 가짜 최소/최대, 반전·회복 또는 Foam 사건을 만드는가? | 해당 workflow claim의 blocker |
| 2 — 핵심 움직임 보존 | 누락/보류 때문에 실제 상승·하강·급상승·반전·Foam 맥락이 사라지는가? | 해당 유용성 주장 미입증 |
| 3 — 국소 잔여 오류 | 오류가 있어도 보호해야 하는 사건·방향·맥락은 유지되는가? | 사전 정한 적용 범위와 근거 아래 허용 가능; 오류 계수는 보존 |
| 4 — 판단 불가능 구간 | source/geometry/visibility/truth가 부족한가? | UNASSESSED; 성공적인 억제나 없는 현상으로 계산하지 않음 |

한 점의 오검출도 전체 report의 최고값으로 확대되면 중요하다. 여러 점을 놓쳐도 가림 구간임이 명확하고 전후의 동일 계면 맥락이 보존된다면 영향이 작을 수 있다. **오류 개수만으로 영향 등급을 정하지 않는다.**

### 4.2 현재 report에서 확인한 문제

실제 sample4 graph는 42초를 관측 최저 유면, 44초를 관측 최고 유면으로 표시한다. CSV/events도 각각 Y868/−18 px, Y822/+28 px와 연결된다. 최신 후보 review에서 이 위치의 선택은 잘못된 대상으로 분류돼 있다. 따라서 이 두 점은 단순 edge case 검출 경쟁이 아니라, **report가 강조하는 사건을 바로 바꾸는 우선 개선 대상**이다. [E03, E04, N01]

수치 관측 간격은 42.5→44초에서 1.5초, 49.5→52초에서 2.5초다. 후자의 두 끝점은 알려진 정후보지만 중간 수치가 없다. “전체 100쌍 중 98쌍은 1초 이내”라는 집계만 보면 이 핵심 구간이 가려진다. 전자는 끝점의 역할 자체도 잘못되어 그 수치 간격을 올바른 계면 cadence로 사용할 수 없다. **물리적 cadence는 이번에도 NOT_EVALUATED다.** [N01]

sample4의 54초 Foam 상단 누락은 측정상 miss다. 그러나 한 시점의 miss가 report 전체의 Foam 움직임을 지웠는지는 별도 문제다. 이 지점 하나의 perfect detection을 S11 전부의 조건으로 삼지 않는다. 반대로 마지막 검출을 실제 Foam 소멸로 오해하게 한다면 개선이 필요하다. 기존 source-context를 포함한 실제 report에서 판단한다. [E04, E07]

### 4.3 1초 목표의 정확한 범위

기존 1.0초 목표는 **별도로 확인된, 보이는, 움직이는 동일 Oil 계면**의 유용한 관측 간격이다. 모든 시간·모든 source·Foam의 보편적인 허용 공백이 아니며, O2/field의 단독 PASS 기준도 아니다. 실제 source timestamp를 사용하고 leading/trailing 공백, 전부 미관측, 하나만 관측된 경우를 별도로 보존한다. 입력 FPS나 빈 row 수로 시간을 추정하지 않는다. [E07]

---

## 5. 원인별 수정 위치

### 5.1 Oil: 후보가 없는 문제와 잘못 채택되는 문제를 분리

공개 압축기 f1499/X578의 검토된 Oil 범위는 Y421–435다. lower Oil 후보 Y425/430/427/424는 보존되지만, completed pipeline은 upper material path **Y288**을 anchor로 채택한다. 이 값은 검토 interval의 **가까운 pixel-cell 경계 [420.5]까지도 132.5 px 떨어져** 있다. 이는 exact-Y 오차가 아니라 interval까지의 거리다. [E06]

코드의 `_cross_representation_support`는 peer 점수를 **최대값**으로 취한다. 표결을 합산하는 구조가 아니다. 서로 다른 generator가 같은 픽셀의 구조를 보는 것만으로 독립적인 물리적 증거가 되지는 않지만, 원인 설명을 “후보가 여러 개라 점수가 누적됐다”로 만들면 실제 코드와 다르다. 이전 peer audit에서 Y288의 지지도는 인접 peer Y277에서, lower 네 후보의 지지도는 0으로 기록됐다. [E08, E09]

또한 sample4 44초 오후보와 42.5·52초 정후보는 모두 support=0 continuation 경로를 포함한다. 따라서 다음 두 변경만으로는 해결되지 않는다.

- 잘못된 anchor만 막는 변경: continuation 오선택이 남을 수 있다.
- representation support=0을 일괄 금지: 실제 계면도 함께 사라진다.

**수정 대상은 anchor와 continuation 양쪽에서 사용하는 역할 근거이며, 후보 존재·geometry·motion·lifecycle는 별도 증거로 유지한다.** [E08, E09]

### 5.2 Foam: episode보다 raw front가 먼저다

| 장면 | 검토 범위 / 관측 | 현재 raw front | 최초 유해 단계 |
|---|---|---|---|
| sample4 54초 / X595 | Foam 상단 rows812–816; Canny Y813 존재 | component [808,834)의 Y833 내부 texture | component → 하나의 front 축약 |
| 공개 압축기 f1499 / X578 | Foam rows323–338; Canny Y332/336 존재 | Y317; 범위보다 5.5 px 위 | appearance component → front 축약 |
| 물 Foam A / X950 | dark Foam 상단 검토, Canny 존재 | 초기 white-support에 올바른 상단 support가 없음 | brightness/material 표현 단계 |

sample4의 global top Y808이나 공개 압축기의 first center support Y317 역시 검토 상단을 대신하지 못한다. component extreme, 두 slope, material support의 시작, 가장 가까운 edge를 자동 선택하는 반복 실험을 다시 열 이유가 없다. [E04–E06, E10]

현재 두 압축기 사례에서는 올바른 상단 후보가 episode에 들어간 뒤 잘려 나간 것이 아니다. **P5-c episode 완화는 열지 않는다.** 먼저 현재 프레임에서 Foam upper 역할을 가진 후보가 실제 좌표와 함께 생성·보존되게 해야 한다.

### 5.3 Association/lifecycle

연속성은 정체성이 아니다. 고정 패턴 변형도 낮은 reverse error와 살아 있는 track ID를 만들 수 있었고, Local XY 이후에도 잘못된 rim 소유권이 성립했다. 새 역할 증거를 연결해도 split/merge·owner loss·FULL/EMPTY·급상승·반전의 계약은 유지해야 한다. [E05]

---

## 6. 설계 결정

### 6.1 유지

현재 후보 생성기와 native 진단, one-pass completed Oil owner, 독립 Foam owner, bounded association/lifecycle, same-frame scalar, per-series validity, CSV/trace/report provenance, source-context report를 유지한다.

### 6.2 변경 제안

**Geometry → 역할 관측 → 운영정책 → 후보 채택 → bounded 소유권 → 같은 프레임 수치 → report**의 각 경계를 명시한다. 역할 관측은 점수 벡터와 availability를 잃지 않게 하고, 운영정책은 calibration으로 검증된 범위에서만 이를 역할 지지로 바꾼다. 숫자 Y는 encoder나 reference 좌표가 아니라 현재 native 후보에서 가져온다.

### 6.3 하지 않을 것

새 end-to-end detector 전체 작성, YOLO/segmentation 모델 나열·탐색, 현재 sample4 정답에 맞춘 cutoff, full/local/mean 임의 voting, report 보간/평활화로 성능 개선 주장, 전역 motion/episode 기준 완화, 영상명·Glass·시각·정답 Y별 runtime 예외는 배제한다. ML 실행은 기존 승인 범위를 넘지 않고, 새로운 inference·bank·consumer는 각각 preflight를 가진 별도 작업이다.

---

## 7. Oil 역할 관측 및 운영정책 명세

### 7.1 데이터 계약 — 제안, 아직 생산 API가 아님

기존 Witness/diagnostic owner를 확장하고 동등한 sidecar를 새로 여러 개 만들지 않는다. 최소 보존 내용은 다음과 같다.

```text
identity: source/frame/timestamp/Glass/geometry/profile/reference-bank digest
candidate: original input index, family, original source-Y, native-support lineage
observation: full/local의 interface·structure·texture 원시 점수 전체
support: common-domain, visible columns, crop completeness, floor/ceil variants
status: MEASURED / TIE / UNAVAILABLE / INCONSISTENT_VARIANTS
calibration: policy/version/partition digest 또는 UNCALIBRATED
role result: INTERFACE_SUPPORTED / INTERNAL_OR_ARTIFACT / UNRESOLVED
claim scope: 지역 역할 / 실제 contour / fixed-X scalar 중 증명한 범위만
```

원시 유사도를 probability로 저장하지 않는다. `UNAVAILABLE`를 0점의 정상 negative로 바꾸지 않는다. reference self와 같은 좌표 중복은 calibration 독립 표본으로 추가하지 않는다. 지역 역할 지지에서 contour나 fixed-X 위치의 정답을 자동 추론하지 않는다.

### 7.2 첫 번째 운영정책 가설: local 역할 경쟁 + 절대 지지도

수치화 대상은 **한 가지 정책 family**로 고정한다.

```text
A(c) = 모든 유효 anchor variant에 대한 local interface similarity의 최솟값
M(c) = 각 variant의 local [interface − max(structure, texture)]

provisional support eligibility =
    frozen support/geometry 조건 충족
    AND 모든 variant에서 interface가 수치적으로 유일한 local 선호
    AND A(c) >= calibration으로 정한 tau_support
```

현재 CR1의 `1e-6` 동률 처리는 계산상의 동률 정의일 뿐 물리적 신뢰도 기준이 아니다. 첫 설계에서는 임의의 큰 class-margin floor를 더하지 않는다. 52초의 작은 margin 사례를 정상적으로 포함해 calibration한다. `tau_support`는 이번 문서에서 정하지 않았다.

full 점수는 context 변화와 opposition 분석에 계속 보존한다. **full=texture를 보편적 veto로 넣지 않는다.** mean baseline을 세 번째 voter로 추가하지 않는다. 두 모드는 같은 encoder·source에서 나온 의존적인 증거이지 독립적인 확률 투표가 아니다.

이 조건을 충족했다고 곧바로 `INTERFACE_SUPPORTED`로 emit하지 않는다. calibration/holdout과 native-support 계약이 완료되기 전에는 `provisional support eligibility`라는 진단 결과만 기록한다. 낮은 절대 지지도나 동률은 `UNRESOLVED`이지 구조물로 판명됐다는 뜻이 아니다. `INTERNAL_OR_ARTIFACT`에는 별도로 검증된 negative evidence가 필요하다.

### 7.3 왜 이 family부터인가

새로운 source 정보 없이 같은 argmax 비교를 반복하는 것과 달리, 원시 벡터에 이미 존재하는 두 종류의 정보를 사용한다. 약한 계면 일치가 우연히 최상위인 44초 후보와, 실제 계면이지만 Foam texture와 매우 비슷한 52초 후보를 서로 다른 이유로 취급할 여지가 있다. 동시에 내부 texture는 높은 절대 점수만으로 Oil이 되지 않는다.

이는 현재 노출 자료에서 착안한 **개발 가설**이므로 현재 자료가 곧 독립 평가셋이 될 수는 없다. 가설의 합리성과 현장 효과의 입증을 분리한다. 실패하면 그 fixed family를 닫고 실패 원인을 기록한다. 숫자·reference·scale을 바꾸며 같은 기록을 계속 통과시키지 않는다.

### 7.4 calibration/평가 분할

기존 164개 기록은 development/exposed diagnostic으로 유지한다. 새로 임계값을 고를 자료와 최종 평가 자료를 결과를 보기 전에 source/episode 단위로 분리한다. 동일 원본의 근접 프레임·crop·해상도 변형·동일 좌표 후보는 같은 partition에 둔다. 모든 source가 이미 노출됐다면 “새 split”을 했다고 blind holdout이 되지 않는다. [E07]

calibration manifest는 다음을 동결한다.

| 필드 | 조건 |
|---|---|
| 역할 | 실제 interface, 구조/반사, 내부 texture, mixed/unknown을 구분 |
| 정답 정밀도 | candidate correspondence / region / interval / contour를 혼용하지 않음 |
| 출처 | source bytes/hash, episode, 실제 timestamp, label owner |
| 대조 | 어두운 실제 경계, Foam이 겹친 실제 Oil, 구조·광학변형, 내부 texture |
| 용도 | 개발 / operating-point calibration / held-out / field shadow |
| 영향 기준 | 보호할 story와 A/B/C/U 분류 기준, 필요한 수치 한계는 비교 전에 결정 |
| 운영점 | 위 fixed family의 tau 하나; raw 점수·unresolved·negative family 결과 보존 |

표본 수가 많아 보여도 독립 장면이 부족하면 이를 명시한다. 보장되지 않는 신뢰수준을 쓰거나 이 9개 후보에 맞춘 임계값을 calibration이라고 부르지 않는다. 외부 자료는 새로운 untouched input으로 사전 지정된 경우에만 그 역할로 사용한다. 사용자 업무용 영상의 calibration이 필요하면 work-PC 내에서만 사전 분할하고, 개인 영상·좌표를 반출하지 않는다.

### 7.5 사람에게 필요한 검토를 최소화하는 방법

현재 닫힌 Oil/Foam 역할 및 위치 질문은 반복하지 않는다. 미검토 150개를 전부 라벨링하라고 요구하지도 않는다. 실제 운영정책이 서로 다른 물리적 결론을 낼 수 있는 **경쟁 후보군·움직임 구간**만 먼저 좁힌다.

예를 들어 49.5초 Y841 최고점 후보와 알려진 Y836 후보의 관계는 점수만으로 해결되지 않는다. 기존 source-only region/interval 근거로 해결 가능한지 먼저 확인하고, 그렇지 않을 때에만 “같은 물리적 경계 표현인가, 다른 대상인가, 판정 불가능인가”를 묻는다. 자동 선택한 새 좌표를 정답으로 유도하지 않는다. 정밀 contour가 필요 없는 역할 비교에 pixel-perfect annotation을 요구하지 않는다.

42.5–44초의 기존 movement 판단은 재사용한다. 49.5–52초 전체에 대한 연속 가시성·동일 계면 여부가 더 필요하다면, 이미 보존된 sequence와 관련 reply를 먼저 확인한다. 두 끝점의 정답을 중간 프레임의 라벨로 확장하지 않는다. runtime에서 매 프레임 수동 보정을 요구하는 제품 설계로 바꾸지 않는다.

### 7.6 consumer 통합 순서

**Shadow:** 원시 관측·calibrated typed output만 저장한다. 생산 후보·score·authority·tracking·CSV·report는 동일해야 한다. O2/V4/V5를 통과하기 전에는 실제 selector가 읽지 않는다.

**O3의 첫 behavior slice:** 새 역할 조건을 같은 프레임의 발행 가능성에 연결한다. anchor 및 continuation 모두에서 일관되게 검사하며, continuation이라는 이유로 미검증 역할을 우회시키지 않는다. original candidate는 계보와 진단을 위해 남긴다. 역할 미결정은 물리적 부재나 HARD_INVALID로 바꾸지 않고, 그 프레임의 수치를 발행하지 않는 결과가 될 수 있다. 과거 owner 상태는 기존 bounded 규칙으로만 유지하며, 그 상태로 현재 Y를 만들지 않는다. 이 slice의 목적은 **잘못된 수치 억제와 손실의 실제 trade-off 측정**이지 recall 회복까지 한 번에 주장하는 것이 아니다.

**별도 O3 후속 slice:** 검증된 새 역할 witness가 있는 native lower 후보가 기존 representation-support heuristic 때문에 anchor가 되지 못하는 경우를 다룬다. 새 witness가 독립 역할 근거를 실제로 제공한다는 전제 아래, 해당 heuristic을 대체하는 명시적인 authority route를 설계한다. 단순히 support=0 후보를 승격하지 않으며 geometry/material/optics/ambiguity와 소유권 계약을 보존한다. 별도 commit·controls·ablation으로 검증한다.

첫 slice의 억제만으로 공개 압축기의 lower Oil가 회복된다고 주장하지 않는다. 기존 lower 후보는 authority/tracklet 단계에서도 막혔기 때문이다. 두 slice를 분리해야 false-positive 억제와 true-positive 회복의 원인·회귀가 구분된다. [E06, E08]

### 7.7 geometry/역할/출력 좌표

CR1은 104→224 변환과 14-pixel token lattice로, sample4에서는 token 간격이 약 6.5 native px다. anchor 주변의 역할 유사도는 subpixel 경계 측정이 아니다. [E03]

수치 좌표는 현재 프레임의 native 후보에 연결한다. 기존 pooled scalar나 sector sample을 fixed-X contour로 재명명하지 않는다. 실제 fixed-X 경계가 필요한 후속 representation은 별도 current candidate와 parent/native support lineage를 생성해야 한다. 선택 이후 Y를 reference, nearest edge 또는 diagnostic peak로 이동시키면 안 된다.

다른 Glass/해상도에서 crop·scale·source/ROI 좌표 변환을 어떻게 고정할지는 inference preflight에 명시한다. sample4의 픽셀 창을 Windows에 그대로 사용 가능하다고 가정하거나, 결과를 보고 유리한 해상도를 고르지 않는다.

---

## 8. Foam 개선 명세 — 독립 경로

### 8.1 세 가지 사실을 분리

| 사실 | 필요한 증거 | 값이 없을 때 |
|---|---|---|
| Foam 존재 | Foam material/region 역할의 근거 | 관측 불가와 부재를 구분 |
| Foam 상단 위치 | 현재 프레임에서 upper 역할을 가진 native boundary | 존재할 수 있어도 높이는 unavailable |
| 형성·이동·소멸 episode | 같은 역할의 front/존재 관측을 묶는 bounded 시간 근거 | 마지막 검출을 실제 소멸로 치환하지 않음 |

현재 CR1의 texture reference는 **Foam upper prototype이 아니다.** Oil 역할 정책의 성공으로 Foam 상단 검출 성공을 주장할 수 없다.

### 8.2 P5-a: 현재 프레임 상단 역할·표현

현재 있는 edge/path/support 진단을 재사용하여 실제 상단 후보가 어느 단계에 존재하는지 보존한다. appearance component 전체를 Foam segmentation으로 간주하지 않는다. 올바른 상단과 내부 texture·rim·반사·lower boundary를 대조하는 역할 관측이 필요하다.

학습 특징을 사용하는 후속안은 같은 고정 encoder를 활용할 수 있지만, **Foam-upper reference와 control bank를 새로 정의하는 별도 실험**이다. 기존 bank의 이름만 바꾸지 않는다. sample4 upper, 물 A의 어두운 upper, 공개 압축기 upper/lower 역할 차이를 포함하고, 내부 texture 및 rim을 대조로 둔다. Beer의 잘린 upper는 높이 unavailable이고, front/back projection을 Foam 두께로 사용하지 않는다. 밀크의 불명확한 lower는 정답이 아니다. [E07, E10]

최초 좁은 실험의 입력·bank·연산은 결과 전 고정하고, 알려진 전체 대조 결과를 유지한다. 한 장면의 실패가 모든 후속 연구를 금지하지는 않지만, dark Foam을 사후 제외하고 보편적 upper 기능을 입증했다고 할 수도 없다.

### 8.3 P5-b: raw front의 실제 pipeline 연결

검증된 upper-role evidence를 가진 현재 native 후보가 raw Foam 입력까지 도달하는지 확인한다. selected component bbox 극값 대신 실제 upper 후보를 발행하되, original source/frame/Y와 representation lineage를 보존한다. Oil이 unknown이어도 별도로 평가한다. typed Witness를 소비한다면 O2/O3 계약을 적용한다.

NONE/FULL의 raw·completed·tracking·report model이 같아야 한다. 원시 upper가 들어왔는데 episode가 거부한 경우에만 “상단 회복은 되었지만 episode가 막았다”고 말할 수 있다. 현재 sample4 Y813과 공개 압축기 interval 내부 Canny의 존재는 그 후보 자체의 역할을 자동 인증하지 않는다.

### 8.4 P5-c: episode는 조건부로 연다

진입 조건은 **독립적으로 자격을 갖춘 올바른 raw front가 기존 episode 처리에서 사라지는 saved causal join**이다. 그 전에는 formation/persistence/width/motion을 완화하지 않는다.

조건이 충족되면 실제 좁은 onset·stable layer와 entry splash·wall residue·post-Foam를 함께 비교한다. Foam 수치가 늘었다는 이유만으로 진전이라고 하지 않는다. onset, 마지막 upper 관측, 관측 불가, 실제 disappearance를 분리하고 Foam 시간 허용치를 임의로 1초로 설정하지 않는다.

---

## 9. 실행 Work Packages와 기존 계획의 관계

아래 WP 번호는 이 문서의 전달 순서이며 **새로운 상태 원장이나 기존 O/W/P gate의 대체물이 아니다.** 채택 후 Work Plan의 해당 항목에 연결하고, 현황은 Work Plan 한 곳에서만 관리한다.

| WP | 기존 항목 | 주요 산출물 | 진입/종료 |
|---|---|---|---|
| 01 기준선·원인/효용 재검토 | P0, W4 | 본 문서·read-only audit·기존 report join | **이번 수행 완료**; 물리적 acceptance 없음 |
| 02 연속 점수 운영정책 명세 | W4/P2, O2 설계 | 한 policy family, availability/좌표/role 계약, calibration manifest 초안 | 본 문서 제안; 숫자 선택 전 검토 |
| 03 calibration·held-out 자료 고정 | V2/V3 | 역할/정밀도/episode 분할, 미노출 한계, 사전 평가 기준 | 현재 164개를 holdout으로 부르지 않음 |
| 04 고정 역할 관측과 shadow | O2, V2–V5 | typed diagnostic, baseline equality, 자료별 role/coverage/resource 결과 | Windows shadow 포함 기존 gate 충족 전 behavior 금지 |
| 05 같은 프레임 역할 gate | O3/W5 | anchor+continuation 공통 소비, full-window A/B, 오류/누락 영향 | 잘못된 출력 억제와 핵심 관측 손실 동시 비교 |
| 06 역할 지지 후보의 채택 회복 | O3 후속 → O4/W6 | 명시적 authority route, 원인별 association/handoff 검사 | 양성 역할 증거 없는 승격·motion 완화 금지 |
| 07 Foam upper 역할·raw 표현 | P5-a → P5-b | upper/context 대조, native candidate, 실제 pipeline join | Oil과 독립; typed consumer gate는 유지 |
| 08 Foam episode 후속 | P5-c | 올바른 raw가 사라지는 원인과 제한된 수정 | 진입 조건 성립 시에만 실행 |
| 09 통합·Windows·report 이해도 | O5/W7/P6 | 9개 canonical segment 표, 실제 bundle review, 성능·provenance | 모든 구간 표시, 별도 field 결과 |
| 10 disposition와 정리 | P7 → S11-M/S12 | accepted/limited/rejected/unassessed 기록, 최소 재현물·handoff | field 승격·제품 범위 변경은 명시적 판단 |

### WP02–03 상세

입력은 CR1 원시 결과, P0 roster, 기존 W3 label/uncertainty 계약과 이번 score/control 재집계다. 첫 정책 family의 연산을 명시하고 아직 정하지 않은 항목을 숨기지 않는다: tau, 적용 geometry/scale, calibration/held-out source, role assertion의 정밀도, behavior 비교의 잔여 오류 범위가 남아 있다.

실행자는 먼저 위 항목의 manifest를 채운다. source를 찾거나 새로 보는 작업이 필요하면 획득·보존·노출 시점을 별도로 기록한다. 기존 source-only reply로 해결되는 것을 다시 묻지 않는다. 명확한 data split 없이 자동 typed classifier를 만드는 작업은 시작하지 않는다. 다만 data-neutral schema/input/availability/좌표 unit tests와 saved-result 분석은 진행할 수 있다.

### WP04 상세

먼저 고정 raster/label contract에서 역할 observation을 검증하고, 이후 실제 application 측정 경로의 shadow로 연결한다. feature 값·원래 candidate index·timestamp·support가 연결되는지 확인한다. 원시 생산 판단은 변경하지 않는다. unavailable/동률/분수 anchor 불일치/geometry 밖 입력에서 명시적으로 중단하거나 미결정 처리한다.

unit test PASS와 독립 physical control PASS를 따로 보고한다. synthetic 대조의 목적은 유효한 연산·입력 조합 확인이지 compressor efficacy 보장이 아니다. 실제 reference/bank/scale/calibration을 바꾼 뒤 이전 holdout을 그대로 미노출이라고 부르지 않는다. V5 Windows shadow는 사용자 측에서 승인된 절차로 수행하며 이번 문서 작성만으로 실행된 것으로 처리하지 않는다.

### WP05 상세

첫 behavior 변경은 역할 gate만 연결한다. 기존 Recipe·샘플링·전처리·candidate capacity·temporal/lifecycle·Foam 정책을 고정한다. 결과를 본 뒤 불리한 window나 reference를 바꾸지 않는다. source/frame/candidate identity를 보존하여 새로 없어지거나 나타난 numeric 및 바뀐 소유권을 추적한다.

sample4는 기존 0–56초/2Hz 기준선과 비교한다. 38·40·42·42.5·44·49.5·52초는 원인 체크포인트일 뿐, 이 일곱 시점만으로 연속성 성공을 판정하지 않는다. 바뀐 extrema와 가짜 신규 extrema, 보호된 movement, leading/trailing gap, 새로운 unknown 구간을 실제 report에서 확인한다. 원시 수치 감소는 잘못된 대상을 억제한 경우와 실제 계면을 지운 경우로 나눈다.

공개 압축기는 기존 3-frame window가 geometry/entry fixture임을 유지한다. 이를 전체 source story로 확장하지 않는다. 새 연속 window가 필요하면 camera movement/scene cut과 Recipe 적용 범위를 먼저 동결한다. sample3은 계속 quarantine한다.

종료 판단은 `부분 기능 입증 / 해당 기능 무효 / evidence 부족 / 회귀`로 남긴다. 기존 A급 오극값이 일부 남더라도 확인된 개선 자체는 기록하지만, 해당 전체 report 또는 field PASS로 승격하지 않는다. 새로운 A/B급 회귀는 그 behavior의 수용을 막는다.

### WP06 상세

먼저 earliest loss를 분류한다: 후보 부재, native 위치 표현 손실, typed role 미입증, authority 부족, association mismatch, lifecycle 제한, 최종 selector ambiguity. 원인이 확인된 owner 하나만 변경한다.

현재 공개 압축기 lower 후보의 support=0 및 sample4 continuation 사례를 함께 대조한다. 새 역할 witness가 있어도 어떤 gate를 대체할 자격이 있는지 명시한다. 다른 품질/역할/소유권 gate를 묶어서 해제하지 않는다. 역할 부정이 없는 것과 양성 역할 증거가 있는 것은 다르다.

### WP07–08 상세

Foam의 presence·upper geometry·episode를 별도 열로 결과화한다. 정확한 raw upper 후보가 생성되지 않으면 downstream 수치를 복원하는 코드를 작성하지 않는다. upper 역할 표현이 회복된 경우에만 actual pipeline에서 입구부터 publication까지 연결한다. 현재 Oil 결과에 따라 Foam의 존재를 만들거나 지우지 않는다.

### WP09–10 상세

개발자에게 알려진 source story와 다른 사람이 실제 report만 보고 재구성한 설명을 비교한다. graph 숫자만 보지 않고 기존 captures/source sequence/context 및 누락 표시까지 포함한다. 사용자의 실제 판단 절차를 중심으로 보되, 평가는 source의 qualified truth 정밀도를 넘지 않는다.

기능 전체를 포기하거나 Foam 지원 범위를 줄이는 결정은 자동으로 하지 않는다. 제한된 유용성이 입증되면 그 범위와 잔여 불확실성을 명시한다. 범위 축소가 필요하다면 구체적으로 어떤 관측/role/scene을 왜 지원하지 못하는지 보고한 뒤 별도 제품 결정을 받는다. “완전 자동 또는 Foam 포기”라는 이분법으로 마무리하지 않는다.

---

## 10. 검증 계약

### 10.1 변경별 필수 검증

| 계층 | 검증 항목 | 금지되는 성공 해석 |
|---|---|---|
| 입력/원본 | hash·실제 frame/PTS·geometry·reference/정밀도·exposure | 같은 파일명만으로 같은 source |
| 측정 | common support, 좌표, floor/ceil, raw vector, 결측·동률 | 결측=negative, self=일반화 |
| 역할 | 양성/구조/내부 texture/mixed 각각의 결과·unresolved | 모든 반대상을 하나로 평균낸 정확도 |
| 후보 | 원본 index, native contour/pooled scalar 구별, family 간 중복 | 최고 점수·최저/최고 Y·근접만으로 역할 |
| authority | anchor/continuation 동일 계약, positive와 non-negative 구별 | anchor-only 수정으로 전체 해결 주장 |
| association/phase | bounded owner, ambiguous handoff, FULL/EMPTY, reverse/refill | motion만으로 역할·과거 좌표 복제 |
| sequence/public | selected candidate Y = sequence raw Y = CSV raw Y | report나 serializer로 위치 수정 |
| report | 주요 사건·방향·누락 영향·독립 읽기 | 수치 개수·시험 통과 제목=물리 정확도 |
| 성능 | decode/전처리/encoder/local-query/sequence/report를 구분한 실측 | 소수 PNG query 시간을 Windows 전체 runtime으로 환산 |

현재 CR1의 165 forward/두 차례 소규모 측정 시간은 이전 실험의 범위 제한된 수치다. 반복 프레임·candidate 수·debug·CPU/GPU 환경이 다른 실제 파이프라인 비용을 입증하지 않는다. 다음 preflight에서는 frame당 encoder call 수, peak RSS, output bytes, 전체 소요 시간 상한을 정하고 측정한다. 임의의 새 상한 숫자를 본 문서가 운영 정책으로 부여하지 않는다. [E03]

### 10.2 False progress 방지

역할 gate로 수치가 사라졌다면 실제 계면의 miss를 반드시 센다. 전부 unknown이면 틀린 수치는 줄겠지만 유용성 성공이 아니다. 반대로 후보를 많이 살려서 numeric이 늘었더라도 wrong-role·가짜 이벤트·잘못된 handoff가 증가하면 성공이 아니다. 바뀐 reference나 label로 원래 실패 집합을 줄여 얻은 개선은 별도 데이터 변경으로 취급한다.

실제 경계의 작은 위치 차이가 움직임 맥락을 보존하면 잔여 오차로 인정할 수 있다. 그러나 그 결론에는 source/geometry/label 정밀도와 task impact 근거가 있어야 한다. 원래 confirmed candidate ID와 다른 ID라는 이유만으로 실패시키지 않고, 미검토 후보라는 이유만으로 정답 처리하지도 않는다.

### 10.3 실제 report만으로 판단하는 확인 양식

가능하면 baseline/candidate의 이름을 가린 실제 bundle을 사용한다. 개발자가 정답·trace·예상 결론을 먼저 설명하지 않는다. 검토자는 report에서 이해한 내용을 먼저 기록하고, 그 후 source의 qualified story와 대조한다. 여기서 별도의 dense annotation을 요구하지 않는다.

| report-only 질문 | 비교할 기록 |
|---|---|
| 어느 구간이 full/empty이고, 어느 구간에 직접 계면이 보이는가? | 좌표 없는 상태와 직접 관측의 구분 |
| Oil은 언제 상승·하강·반전·회복하는가? | 방향·전환 순서·원본에서 허용된 시간 정밀도 |
| 가장 낮고 높은 유면으로 읽히는 사건은 무엇인가? | 검출 오후보가 핵심 극값으로 오해되는지 |
| Foam의 형성·지속·마지막 관측·실제 소멸을 어떻게 이해했는가? | 검출 종료와 물리적 소멸의 혼동 |
| 상단 Foam과 하단 Oil이 각각 관측됐는가? | 역할 전이·중복 발행·한쪽 unavailable의 구분 |
| 어느 구간은 결론을 내릴 수 없는가? | 공백·가림·불명확함이 실제로 전달됐는지 |

개발자의 시각적 graph 확인은 이 절차의 독립 사용자 검토를 대신하지 않는다. 평가 결과는 막연한 만족도 한 숫자가 아니라 잘못 읽은 사건, 지워진 움직임, 허용 가능한 국소 오차로 남긴다. 정답이 불명확한 구간은 검토자가 확신했다는 이유로 정답이 되지 않는다.

### 10.4 구현 접점과 변경 금지 영역

| 접점 | 허용되는 후속 변경 | 반드시 함께 볼 항목 |
|---|---|---|
| 기존 Witness/diagnostic owner와 별도 실험 adapter | raw vector, support, calibration provenance의 추가 보존; uncalibrated eligibility 진단 | 기본 의존성에 Torch를 강제하지 않음; debug/NONE equality |
| `oil_observation_resolver.py`의 `OilAdmissionEvidenceOwner.prepare` | O3 승인 이후 anchor/continuation 공통 role 소비 | before/after 후보 전체와 새 winner; early rejection으로 숨은 오류가 드러나는지 |
| `oil_phase_identity.py`, `oil_candidate_authority.py` | 별도 양성 역할 증거의 명시적 route | 기존 hard-invalid/optics/geometry/ambiguity를 일괄 우회하지 않음 |
| logic-map의 `OIL-TRACKLET`·phase owners | earliest-loss가 여기로 입증된 경우에만 bounded 수리 | split/merge, stationary structure, FULL/EMPTY, inverse/re-entry controls |
| `foam_front_detector.py` 및 후보 조립 | 검증된 upper 역할을 가진 native 후보 보존·선택 | bbox extreme이나 appearance support를 물리적 front로 재명명하지 않음 |
| `foam_episode_resolver.py` | WP08 진입 후 원인에 한정된 변경 | correct raw와 false splash/residue를 동시에 평가 |
| CSV/report/source-context | 기본적으로 변경하지 않음; 동일 bundle 검증에 사용 | 수치 보간·사후 Y 보정·실패 은폐 금지 |

아직 존재하지 않는 새 adapter/테스트 파일명은 실제 구현 설계에서 정한다. 이미 있는 owner를 우선 재사용하고, 같은 질문에 답하는 또 하나의 evaluator나 복제 status schema를 만들지 않는다.

---

## 11. Windows 최종 판정표

원본은 업무용 PC에 있고 이번 작업에서는 실행하지 않았다. 아래 모든 현재 결과는 **NOT_EVALUATED**다. 시각의 `약` 표시는 원래 reviewed truth의 정밀도를 유지한 것이다. source fingerprint가 아직 없는 것은 남은 provenance 항목이지 이미 완료된 것으로 표시할 수 없다. 다음 승인된 실행 시 private basename 없이 bytes/hash/width/height/FPS/duration을 기록한다. [E11]

| 기존 segment ID | Source 시간 | report가 보존해야 할 맥락 | 필수 대조 |
|---|---|---|---|
| WS1-BASE-FULL-PREFIX | 480–약550 | 가득 참; 보이는 계면·Foam 없음 | glare/structure numeric 금지 |
| WS1-BASE-DRAIN | 약550–662 | 실제 보이는 Oil 계면의 느린 하강 | 고정 구조를 Oil로 추적하지 않음; 유용한 간격 |
| WS1-BASE-RAPID-REFILL | 662–약663.6 | 급상승 후 상단에서 계면 소실/full | stale owner·새 구조로 역할 이전 금지 |
| WS1-BASE-FULL-SUFFIX | 약663.6–780 | 다시 full; 직접 계면·Foam 없음 | 725초 reflection 등 거짓 수치 금지 |
| WS1-ACCUM-EMPTY | 480–약653 | Oil/Foam 없음 | 하부 고정 구조가 entry anchor가 되지 않음 |
| WS1-ACCUM-ENTRY-SPLASH | 약653–672 | 유입·상승, 아직 실제 Foam 시작 전 | splash/wall을 Oil/Foam으로 오인하지 않음 |
| WS1-ACCUM-FOAM-LAYERED | 약672–680 | 상단 Foam과 하단 Oil의 서로 다른 움직임 | 독립 역할·가용성, 한 계면의 중복 발행 금지 |
| WS1-ACCUM-POST-FOAM | 약680–700 | Foam은 없고 Oil은 남음 | 마지막 Foam 검출의 잔존·residue 금지 |
| WS1-ACCUM-DRAIN | 약700–780 | Oil 반전·하강 | owner loss 뒤 잘못된 재획득·잔사 추적 금지 |

각 행에 actual source coverage, Oil/Foam 유효 수치와 wrong/unassessed 수, Y-range 및 방향, 최대 관측/오소유 구간, phase/owner 변화, 주요 사건, A/B/C/U 영향, 최종 PASS/FAIL/NOT_EVALUATED를 함께 적는다. 총량으로 한 행의 실패를 가리지 않는다. private 영상·검토 이미지·trace ZIP을 Mac으로 반출하는 절차를 만들지 않는다.

V5의 Windows shadow와 최종 field behavior 검증은 다른 단계다. 전자가 끝났다고 아홉 story의 최종 효과가 검증된 것이 아니며, 로컬 프로그램의 정답률로 대체할 수도 없다.

---

## 12. 중단·재설계·종료 판단

| 상황 | 행동 |
|---|---|
| 저장 점수/분모/hash 오류 | 원인 수정 후 동일 input 재검증; 새 detector 가설로 전환하지 않음 |
| fixed local policy가 calibration/controls에서 역할을 구분하지 못함 | 해당 family의 미입증/실패를 닫고 원인 보존. 같은 source를 보며 cutoff/bank/scale 반복 변경 금지 |
| 역할 비교는 유용하지만 후보 간 physical competition 미해결 | 필요한 native support/경쟁 역할을 국소적으로 확인; argmax 강제 금지 |
| 오선택은 줄었지만 실제 이동을 지움 | 선택된 operating point/consumer는 미수용; field gate 유지. 누락을 정확한 억제로 세지 않음 |
| 일부 핵심 오선택만 줄고 나머지는 남음 | 해당 부분의 개선은 기록; 전체 report/field 성공은 별도 |
| 올바른 raw Foam upper 자체가 없음 | P5-a/b에 남음; P5-c episode 완화하지 않음 |
| correct raw가 있는데 episode에서 잃음 | saved causal join을 진입 근거로 P5-c를 별도 실행 |
| 중요한 story가 보존되고 잔여 오류의 영향이 제한됨 | 해당 적용 범위의 수용 검토 가능. 100% 프레임 정답을 추가 조건으로 만들지 않음 |
| source/visibility/truth가 부족 | 구체적 미평가 claim을 명시; pass도 기술적 불가능성도 주장하지 않음 |

여기서 fixed family의 실패는 사전에 정한 capability·task-impact 기준 미달을 뜻한다. **단일 후보의 오분류를 자동으로 전체 실패로 판정한다는 뜻이 아니다.**

S11의 종료는 모든 연구 아이디어의 소진이 아니다. 보호한 실제 story들이 report에서 이해되고, 알려진 맥락 왜곡·소거가 해결되거나 명시적으로 허용 가능한 잔여 범위로 검증되며, 생산 불변조건·실사용 비용·Windows gate가 충족될 때 판단한다. 실패한 국소 연산이 존재한다는 이유만으로 끝없이 새 detector를 만들지 않는다.

---

## 13. 변경 관리와 다음 구현자의 인수인계

이번 문서는 기존 `S11-program-review-and-work-spec-2026-10-12.md` 및 native intake를 대체하지 않고 **CR1 이후의 연속 점수 해석과 운영정책 방향을 보완**한다. 이전 evidence와 실패 결론을 덮어쓰지 않는다. 상태 owner는 Work Plan, 일반 설계 owner는 architecture, 검증 owner는 validation이다. 본문 WP를 별도의 status ledger로 운영하지 않는다. [E01, E08]

채택 시 제안되는 문서 반영:

| 위치 | 반영 범위 |
|---|---|
| `docs/20-architecture/s11-contextual-role-observation-design.md` | raw vector/availability 보존, fixed local policy family, native role/geometry/consumer 분리 |
| `docs/30-validation/s11-interface-observability-witness-validation.md` | calibration partition, role/coverage/impact 보고, 고정 operating point 및 O2/O3 acceptance delta |
| `docs/00-project/work-plan.md` | 승인된 다음 gate·현재 disposition만 갱신; 본문 전체 복제 금지 |
| diagnostics 또는 reference record | 이번 재집계의 최소 receipt, script digest, 원 evidence 연결 |
| `docs/catalog-by-created-date.md` | 새 문서를 실제 추가할 경우 해당 규칙에 맞춰 갱신 |

작업 전 HEAD/status와 active owner를 재확인한다. 문서만 바꾸면 문서/Governance 검증을 하고 불필요한 전체 영상 replay를 돌리지 않는다. 코드 변경은 가능한 한 observation → shadow → consumer → positive admission/phase를 분리한다. default OFF와 NONE/FULL equality를 유지한다.

지속적인 새 실험 산출물은 `scripts/experiment_artifacts.py`와 기존 lifecycle의 managed run 안에서 생성·판정·정리한다. frozen input/source/Recipe/truth는 복제하거나 수정하지 않는다. CR1 환경·weights·cache는 사용자의 명시적 정리 지시 전까지 유지한다. no-promotion과 자동 환경 삭제는 연결하지 않는다. [E12]

---

## 14. 증거 인덱스

아래 경로는 기준 HEAD의 repository-relative path다. 링크된 문서의 기존 검증 결과와 이번에 다시 실행한 결과를 구분한다. 원 source·기존 큰 trace는 이 package에 포함하지 않았다.

| ID | 출처 | 사용 범위 |
|---|---|---|
| E01 | `AGENTS.md`, `.agents/skills/s11-detector-change/SKILL.md`, `docs/00-project/{work-plan,roadmap,execution-policy}.md`, `docs/README.md` | 현재 owner·진행·권한·운영 |
| E02 | `docs/20-architecture/s11-contextual-role-observation-design.md` | 기존 CR1 계약·운영정책/consumer 경계 |
| E03 | `docs/50-diagnostics/s11/2026-10-12-cr1-context-comparison.md` 및 동명 디렉터리 `followup-readout.json.gz`, `followup-preflight.json`, `verify_followup.py` | CR1 원 결과·분모·자원·실패/유용성 해석 |
| E04 | `docs/50-diagnostics/s11/2026-10-11-p5-default-linkage.md`와 readout, retained NONE report bundle | default 결과·Foam raw loss·report 연결 |
| E05 | `docs/20-architecture/s11-current-detector-logic-map.md`, `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` | 현재 처리 구조와 반복 금지 실패 |
| E06 | `docs/50-diagnostics/s11/2026-10-12-public-compressor-source.md`, position/pipeline linkage 결과 | 새 source 역할·interval·실제 pipeline 원인 |
| E07 | `docs/30-validation/s11-interface-observability-witness-validation.md`의 V3, cadence, P0 scene contract; `2026-10-12-scene-evaluation-roster.json` | 평가 범위·A/B/C/U·holdout·진행 gate |
| E08 | `docs/60-evidence/s11/2026-10-12-program-review-intake.md` 및 연결된 `docs/70-reference/s11-program-review-2026-10-12/` | 이전 명세와 peer/support 원인 분석 |
| E09 | `src/oil_tracker/adapters/vision/oil_candidate_authority.py`, `oil_phase_identity.py`, `oil_observation_resolver.py`의 `_cross_representation_support` | 실제 authority 분기·max peer 지원 계산 |
| E10 | `sample/README.md`, `2026-10-10-water-foam-center-stages.png`, water/support 및 upper 검토 기록 | source 적합성·Foam 표현의 단계별 한계 |
| E11 | `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` 및 `.reviewed-truth.json` | 9개 canonical Windows story 및 privacy |
| E12 | `docs/40-operations/experiment-artifact-lifecycle.md`, `docs/30-validation/s11-detector-change-governance.md` | 산출물·설계 이력·변경 관리 |
| N01 | 본 package `S11-review-execution-summary.json`, `audit_cr1_saved.py` | **이번** saved audit, 원시 점수/경쟁 재집계, CSV/cadence, native decode, 109 tests |

실제 report 기준 경로:

```text
sample/output/s11-p5-default-linkage-20261011-001/none/
  oil_level_analysis_Local_XY_fixed_comparison_sample4_20261011_224401/
    report.html
    tracking_data.csv
    events.csv
    graphs/sample4_sight_glass_detail.png
```

### 외부 1차 문헌의 제한된 사용

Oquab et al., *DINOv2: Learning Robust Visual Features without Supervision*, arXiv:2304.07193v2는 범용 visual representation의 근거다. compressor Oil/Foam에서 현재 descriptor가 calibrated physical classifier라는 근거는 아니다. Geifman & El-Yaniv, *Selective Classification for Deep Neural Networks*, arXiv:1705.08500은 오류와 기권 coverage의 trade-off라는 설계 관점을 뒷받침한다. 해당 논문의 보장·실험 수치를 이 노출된 소표본에 이전하지 않는다. 이번 권고의 직접 근거는 위 repository 증거와 재집계다.

---

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: early authority collapse, representation starvation, motion/bootstrap overreach, component alias/identity transfer, FULL/EMPTY/lifecycle constraints, Oil/Foam cross-coupling, component-front/episode confusion, publication provenance, threshold/private-case escape hatches. CR1 original and usefulness dispositions, Local XY, reference/LK, gap/side correspondence and raw-front evidence remain preserved.
- Prior mechanisms rejected: argmax/vote as physical authority; global texture veto; support=0 universal rejection; anchor-only completeness claim; unbounded carry/interpolation; component top/bottom/nearest-edge substitution; episode relaxation before correct raw front; threshold/bank/scale fitting on the exposed review set.
- Preserved contracts: one generic detector; source-bound current candidates; bounded physical owner; independent Oil/Foam; candidate Y = sequence raw Y = CSV raw Y; no synthetic numeric repair; exact exposure/uncertainty; original O2/V5 and O3/field gates; user-retained environment and sample3 quarantine.
- Difference from prior failures: the proposed first family preserves absolute local interface support and signed role competition instead of treating category preference, smooth tracks, or material-mask geometry as identity. It requires separate calibration and native candidate linkage and measures report impact jointly with missing true observations. It does not claim that the new family is already physically validated.
- Logic-map impact: NONE — this delivery changes no production owner, source code or accepted runtime data flow; proposed extensions require a separately accepted change.
- Failure-registry impact: NONE — saved-score interpretation adds no newly established physical failure mechanism; existing F01/F02/F04/F06/F07/F09/F10 cover the observed risks.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: saved sample4 Foam evidence loses the qualified upper at component-to-front reduction; public compressor Oil retains lower alternatives but admits an incompatible upper anchor. The new raw-score audit identifies information lost by categorical interpretation, not a newly executed physical classifier or production repair.
- Logic-map impact: NONE — read-only verification, descriptive saved-result arithmetic and source equality checks only.
- Failure-registry impact: NONE — no new field acceptance, physical label or behavioral failure mechanism is asserted.
