# S11 인수인계 — 판단 및 구현 진입 계약

## 정확한 기준

Repo `teeeeooo/oil_level_tracker`, `main @ 5c53aefe3bb3c5d1447b29ccb2f78d1adc5459c6`. 시작·종료 모두 tracked tree clean. R22 동작/R22-3 진단, Local XY OFF, O2 OPEN, FIELD FAIL 유지. 권위 있는 현재 상태는 repo `docs/00-project/work-plan.md`다. 이 패키지는 **채택 제안**이며 아직 새 SSOT가 아니다.

## 결론

완전 범용 Foam 정체 판별을 S11의 무제한 선행 조건으로 삼지 말고, 검증할 지원 범위와 운동 맥락을 먼저 고정한다. 다만 기존 visible Foam 실패를 사후 범위 밖으로 제외하거나 전부 UNKNOWN으로 만들어 통과하지 않는다. 9개 Windows segment, no-carry, independent Oil/Foam, physical/target/path/scalar 구분은 유지한다.

## 이번에 확인한 중요한 사실

현재 sample4 report가 강조하는 최저점 42초와 최고점 44초는 기존 source review에서 wrong target으로 확인된 Oil 관측이다. Oil numeric 101/113은 이를 상쇄하지 않는다. Oil gross wrong-target은 계속 핵심 우선순위다.

sample4 54초 X595의 상단 interval은 [811.5,816.5]이고 Canny Y813/white support가 살아 있다. 그러나 raw front는 C1의 lower extreme Y833으로 축약된다. episode는 이 내부 texture를 거절한다. Water A는 반대로 lightness/whiteness 단계에서 support가 사라진다. 두 문제를 하나의 threshold나 episode 완화로 해결하려 하지 않는다.

P2-S1과 P5-S2는 계속 CLOSED WITHOUT PROMOTION이다. S2 추가 분석에서 `C_U−C_N=0.5−b`, `C_U−C_I=a−0.5`를 전 비용에 검증했다. 두 실제 Foam 양성의 b는 약 0.123/0.157로 U의 최소 비용 조건 b>0.5를 만족하지 않는다. ablation은 nonzero contrast에서 r0≥0.5이므로 위쪽에 대비가 있으면 U가 I보다 엄격하게 우세할 수 없다. 이것은 모델의 실패 설명이며, 모든 비학습 판별이 불가능하다는 증명이 아니다.

## 실행 기록

verifier 3종 exit 0; 집중 테스트 162 passed/18.13초. 추가 수학 감사는 42 raster/1,322 query, 2,556 cost triple, 대비 있는 2,592 side를 검증했다. 기존 verifier는 221 production source 불변도 확인했다. 이 숫자는 detector 개선·Windows 통과가 아니다.

## 다음 작업자가 하지 말아야 할 것

S2 prototype/threshold/radius 재조정, P2 exemplar 재선택, cost-first association 재실험, global top/bottom 또는 nearest-edge front 치환, Y813 smoothing 재사용, correct raw가 없는 상태의 episode 완화, sample3 재채굴, ML·신규 촬영·Windows 사본 반출·추가 subagent는 현 범위 밖이다.

## 순서

먼저 사용자의 방향 선택을 정확히 읽고 P0/제품/validation owner의 범위·story-impact 계약을 채택 diff로 정리한다. 권한이 없으면 적용하지 않는다. P2와 P5-a는 별도 선행 경로다. 새 역할 가설에는 기존과 다른 관측/측정 연산, 물리 연결, 대립 설명, missing/tie 처리, **positive decision 도달 가능성**이 모두 필요하다. 없는 근거를 implementation-ready라고 쓰지 않는다.

한 역할 가설이 실제 양성/대립 대조군을 통과하면 해당 경로의 consumer만 연결한다. Oil은 authority→association→phase 순서, Foam은 role→raw front→필요할 때만 episode 순서다. 그 후 exact-head full integration과 Windows 9개 구간/report 평가를 수행한다. 기존 report 기능을 더 만드는 작업으로 대체하지 않는다.

전체 모듈 계약·대조군·게이트·인용 근거는 `S11_PROGRAM_DECISION_AND_WORK_SPEC.md` §7–16에 있다.
