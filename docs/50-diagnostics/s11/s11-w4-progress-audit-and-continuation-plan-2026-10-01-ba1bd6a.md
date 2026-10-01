# Oil Level Tracker — W4 진행 감사 및 후속 작업 계획

- 작성일: **2026-10-01 KST**
- 감사 대상: `teeeeooo/oil_level_tracker`
- 고정 감사 HEAD: **`ba1bd6a0acf9156d4636316caa2038cf2e8bd905`**
- 비교 시작점: 이전 감사의 `85a01cdf4e3385b51422cf0da675a03a74ab70a7`
- 현재 production 동작: **R22**, diagnostic runtime: **R22-3**
- 현재 field disposition: **FIELD FAIL 유지**
- 문서 성격: 이전 O1–O5/W0–W7 명세에 대한 **W4 시점의 후속 감사와 실행 제안**. 기존 설계 전체를 교체하거나 새 behavior revision을 승인하지 않는다.
- 이번 변경 범위: 공유용 문서 작성. 저장소 source, tests, work-plan, 기존 명세서, private data 및 원격 Git 상태는 변경하지 않았다.

## 0. 결론과 바로 다음 작업

**현재 방향을 폐기할 필요는 없다. 다만 W4의 성과를 “정보를 더 보존했다”와 “실제 계면을 더 잘 판별한다”로 명확히 나누고, 현재의 두 프레임에서 표현을 계속 확장하는 단계를 끝낼 기준이 필요하다.**

지금까지는 상당한 검증 기반을 확보했다. W0의 실패를 보존했고, W1의 목표 불일치와 반례를 테스트로 고정했으며, W3의 identity/local-support/scalar 평가 분리를 구현했다. W4 paired-scale은 한 위치 비교의 집계 손실을 설명했고, 공간 실험은 1차원 평균과 행·열별 평균에서 소실되는 정보까지 확인했다. 최신 joint 출력은 기존 O1 계산을 X/Y 배열로 보존하며 원본 재분석 없이 확인할 수 있는 상태다. [R01][R08][R09][R11][R19]

그러나 **현재까지 입증된 candidate-identity 개선은 없고**, calibrated O2와 W5/O3의 진입 조건도 충족되지 않았다. 최신 Windows 실행의 COMPLETE는 측정·저장 완료를 뜻한다. 현재 남은 직접 작업은 새 descriptor 개발이 아니라 **기존 후속 분석의 통계 한 건과 BASE 같은-X 비교 세 행을 바로잡는 것**이다. [R20]

권고 실행 순서는 다음과 같다.

1. **W4-R0:** 현재 `joint-context-001`의 기존 분석에서 한 통계 정의와 세 same-X 비교를 정리한다. 재추출·재라벨링·동일 동영상 재판독은 하지 않는다.
2. **W4-R1:** 그 결과로 joint-appearance 가설을 `재사용하여 한 번 더 검증 / 이 가설은 종료 / 평가 불가` 중 하나로 닫는다. 자동으로 다른 descriptor를 추가하지 않는다.
3. **W4-R2:** 물리적으로 의미 있는 구별 단서가 남는 경우에만, 기존 표현을 쓰는 **조건부 판별기 한 개**의 사전 명세를 작성한다. 모든 반사를 완벽히 구분하는 표현을 요구하지 않되, 잘못된 확신과 긴 오추적을 허용하지 않는다.
4. **W4-R3:** 구별력 검증에 실제로 부족한 positive/negative/unresolved 장면만 W2로 요청한다. 같은 SPL#1을 독립 holdout으로 바꾸지 않는다.
5. **W4-R4:** 이미 구현된 W3 v2를 사용해 예측·보류·미판독·coverage를 평가한다. 새로운 평가기를 다시 만들지 않는다.
6. **W4-R5:** 조건부 효용이 확인되면 기존 O2 수용 gate를 완료하고 W5로 연결한다. 실패하면 해당 가설을 종료하며, 촬영/자료 전략 변경은 별도 결정으로 남긴다.

이 문서의 `W4-R*`는 **W4 내부의 후속 작업 ID**다. 새 W8 단계나 O1 재시작을 뜻하지 않는다.

## 1. 감사 기준과 확인 범위

### 1.1 고정 snapshot

| 항목 | 직접 확인한 결과 |
|---|---|
| 로컬 branch / upstream | `main` / `origin/main` |
| 로컬·원격 HEAD | 모두 `ba1bd6a0acf9156d4636316caa2038cf2e8bd905` |
| 시작 worktree | clean; modified 0, untracked 0 |
| 이전 감사 이후 변경 | 22개 커밋, 40개 파일, Git diff 기준 +7,619 / -25 lines |
| 위 기간의 `src/` 변경 | **0개** |
| 이번 focused 검증 | 14개 test 파일, **355 passed** |
| Joint artifact 재계산 | 보고된 full hash와 **정확히 일치** |
| 독립 gradient oracle | 24개 constructed raster/mask case, 최대 절대오차 `1.1102230246251565e-16` |
| 이전 10월 감사 원문 | 처음 편입된 `2bce8ea`의 bytes와 현재 bytes 일치 |
| 기존 감사 SHA-256 | `b9fd5f91e3caf0b763237a987eb14571a1f1de758fb253e80fe0a9052087450c` |

변경량에는 기존 10월 감사 문서가 저장소에 처음 편입된 649 lines도 포함된다. 문서·테스트 수나 커밋 수 자체를 생산성 점수로 사용하지 않는다. 이 통계가 말하는 것은 **최근 진행이 production 동작 변경이 아니라 offline 도구·평가·근거 정리였다는 점**이다.

### 1.2 검토 경로

현재 work-plan/ledger, docs router, S11 skill, 실행·governance 계약을 출발점으로 이전 두 명세서와 그 이후 변경분을 추적했다. W0/W1/W3/W4 결과, 사람 판독 근거와 불확실성, structure-context, row/column/joint 표현, 최신 Windows intake를 대조했다. 새 adapter·공간 계산·W3 prediction contract와 호출 경계, 관련 unit/integration controls를 확인했다. [R01–R20][C01–C08]

이 감사는 현재 W4와 관련된 책임 경로의 검토다. 무관한 UI/패키징까지 모든 저장소 파일을 다시 한 줄씩 읽었다거나, 과거 모든 R revision을 재실행했다는 뜻은 아니다.

### 1.3 증거 강도

| 구분 | 이번 문서에서 인정하는 범위 |
|---|---|
| **직접 검증** | Mac checkout의 source·계약·Git 상태, 355 tests, 독립 산술/gradient/display 검사, artifact fingerprint |
| **전달된 Windows 증거** | 현장 원자료에서 생성됐다고 보고된 숫자·hash 보존·COMPLETE·image inspection; 여기서 private bytes를 직접 읽은 것은 아님 |
| **직접 사용자 진술이 기록된 근거** | idx0/idx20의 ±약 5초 문맥과 판독 불확실성. 통계값이나 formal label revision으로 자동 변환하지 않음 |
| **이번 제안** | W4 종료/진입 기준, 조건부 효용 검증, 문서 정리 및 이후 작업 순서 |
| **미확인** | 최신 통계의 실제 reduction domain, BASE 3행의 올바른 같은-X appearance 비교, 새 identity classifier 효용, scalar accuracy, 독립 recording 일반화 |

업무 Windows 영상·파생 이미지·NPZ·상세 라벨은 밖으로 반출하지 않는다. 이 문서에 포함한 private-case 숫자는 이미 저장소에 전달·기록된 범위뿐이다. 원본 파일 확보를 위해 새로운 반출을 요청하지 않는다.

## 2. 이전 명세서와의 관계 및 권한

### 2.1 문서 계층

| 문서 | 현재 역할 | 새 계획과의 관계 |
|---|---|---|
| 2026-09-17 `s11-observation-redesign-execution-review.md` | `577f98a` 기준 관측층 재설계 이유와 O1–O5 순서 | **계승.** 원래 첨부명 `s11-detector-redesign-review-and-execution-spec-2026-09-17-1.md`가 이 이름으로 보존되어 있다. 재작성하지 않는다. |
| 2026-10-01 `s11-detector-improvement-audit-and-work-spec-2026-10-01.md` | `85a01cd` 기준 W0–W7, identity/local/scalar 분리, 후속 감사 | **전체 계획 유지, 즉시 실행 부분만 최신화.** 당시 W0 pending, W3 미구현 문구는 당시 사실이며 현재 상태가 아니다. |
| **본 W4 후속 감사** | `ba1bd6a`에서 실제 완료·미완료를 검증하고 W4-R0–R5 제안 | **Delta/addendum.** 원문을 대체하지 않으며 새 runtime·새 global phase plan을 만들지 않는다. |
| `docs/00-project/work-plan.md` | O/W 작업별 현재 상태·다음 동작 | **유일한 live status owner.** 본 제안을 채택했을 때 진행 상태를 여기 반영한다. |
| Witness Architecture / Validation | 구현 의미·책임 / 수용 조건 | **실제 구현·acceptance owner.** 본 제안과 다르면 그대로 우회하지 말고 해당 owner의 변경으로 명시한다. |
| O2 operations | 실제 실행 방법 | ledger가 선택한 절차만 실행. 이전 커맨드가 남아 있다고 재실행하지 않는다. |
| `60-evidence/s11/` | 수행된 검증과 전달된 Windows 결과 | 성공·실패·정정 모두 보존. 당시 상태를 나중의 상태로 다시 쓰지 않는다. |
| Physical Interface Evidence Repair parent design | W5/O3·W6/O4의 support/association/handoff | **조건부 후속으로 유지.** W4 측정 완료가 이 설계의 behavior 승인으로 이어지지 않는다. |

관계의 기준은 기존 router와 실행 정책이다. 날짜가 더 최신이라는 이유만으로 본 감사가 현재 architecture나 validation을 덮어쓰지 않는다. [R02][R03][R04][R05][R06][G04][G05]

### 2.2 O/W 대응과 본 계획의 위치

```text
O1  관측 추출 ── 기존 로컬 acceptance 유지
O2  W0 → W1 → W3 → W4 (W2는 필요 시 제한적으로 활성화)
                     └─ 본 계획 W4-R0 → R1 → 조건부 R2/R3 → R4 → R5
O2 acceptance ── development/calibration/holdout + operating point + Windows shadow
O3  W5 support / physical association
O4  W6 handoff / phase
O5  W7 통합 behavior의 현장 검증
```

W2를 W3보다 먼저 완료하지 않았다고 절차 위반은 아니다. 현재 W1/W3 계약 검증에는 기존 자료가 충분하여 W2가 **조건부 보류**된 것이고, work-plan에도 그렇게 남아 있다. W4의 특정 sub-experiment 종료 역시 전체 W4 또는 O2의 완료가 아니다. [R01][R09]

### 2.3 선행 명세에서 현재 적용을 바꿔야 하는 지점

| 선행 문서의 작업 | 현재 해석 / 이번 추가 계획 |
|---|---|
| W0 profile을 실행한다 | **이미 완료·미승격 종결.** 다시 실행하지 않는다. |
| W1 목표/집계 계약을 만든다 | **계약·반례가 검증됨.** 새 classifier가 그 계약을 지키는지 검사하는 대상으로 사용한다. |
| W3 predicted local/scalar contract가 필요하다 | **v2 prediction / v3 report로 구현됨.** 재설계보다 재사용이 우선이다. |
| W4 한 challenger를 비교한다 | Local-position comparator는 종료. 공간 probe는 정보 보존 실험이며 identity challenger로 세지 않는다. 본 계획은 남은 identity 검증과 실험 종료를 구체화한다. |
| 더 넓은 문맥이나 temporal support가 도움이 될 수 있다 | **idx0/idx20에 대해서는 ±약 5초가 이미 사용됐다.** 같은 클립을 다시 요구하는 기본 경로는 폐기한다. 다른 장면의 시간 정보까지 무용하다고 일반화하지 않는다. |
| W2 추가 장면은 특정 gap 이후 수집한다 | 유지하되, “세상 모든 반례를 구별할 새 descriptor”를 찾을 때까지 수집·실증을 영구 보류하는 규칙으로 확대하지 않는다. |
| W5 전에 O2의 독립 검증을 완료한다 | 그대로 유지. W7까지 미루거나 SPL#1을 holdout으로 바꾸지 않는다. |

## 3. 현재까지 추가된 증거와 실제 진척

### 3.1 W0 profile: 실패 결과가 명확해졌다

전달된 common-support 결과에서 BASE identity는 combined `5 correct / 7 reversed`에서 profile `2 / 10`으로 악화했다. Accum은 `2 / 0`에서 `1 / 1`로 악화했다. Combined 대비 개선 0, 악화 BASE 3쌍·Accum 1쌍이며 profile-supported 범위에서도 추가 scorable identity pair나 순서 변경이 없다. **W0를 미승격 종료한 판단은 타당하다.** [R08]

이를 “네 밝기 평균으로 모든 이미지의 identity 구별이 불가능함”으로 확대하거나, 더 높은 profile score가 더 작은 step SSE라는 뜻으로 해석하지 않는다. 점수는 competing model과 step의 잔차 차이를 정규화하고 다시 집계한 값이다.

### 3.2 W1 / W3: 앞선 감사의 핵심 요구가 실제로 반영됐다

W1은 partial-positive의 median 실패, max가 고립 glare를 통과시키는 반례, identical-observable의 한계, spatial arrangement·missing support를 executable controls로 고정했다. [R09]

W3는 다음을 구현했다. [R05][C04]

- Candidate `identity decision`, exact geometry별 `local_support`, 원래 candidate Y의 `scalar` decision을 분리한다.
- `s11-o2-shadow-predictions-v2`와 `s11-o2-shadow-report-v3`를 사용하며 v1 호환을 유지한다.
- `--exploratory` opt-in, `EXPLORATORY_UNCALIBRATED`, 빈 `fit_partitions`, regression-only 제약을 명시적으로 검사한다.
- CALIBRATED는 기존 development/calibration 조건을 유지한다.
- Scalar의 `USABLE`은 예측일 뿐이며, 독립 scalar truth가 없어 현재 verified scalar coverage/error는 미측정이다.

**이제 “평가 도구가 없어서 다음 실험을 못 한다”는 상태는 아니다.** 실제 판별 규칙·자료 역할·operating point가 남은 일이다. 이번 355개 검증에는 W1/W3 관련 controls도 포함했다.

### 3.3 W3 funnel: 관측층 이외의 손실도 남아 있다

전달된 W3 audit에는 BASE positive 8/9가 row admission/publishable에 포함됐지만 final selected가 아니며, Accum positive 10은 retained ref 이전에 사라진 것으로 기록돼 있다. 단, row membership을 candidate별 물리 인증으로 읽거나 이를 selector bug·top-k loss로 확정할 수 없다. [R10]

이 근거는 **identity 개선만으로 모든 최종 missing이 해결되지는 않는다**는 기존 설계를 뒷받침한다. W4에서는 이 사실을 보존하고, W5/W6에서 실제 동일 후보를 이용해 단계별 원인을 확인해야 한다. 지금 phase gate를 완화하는 사유는 아니다.

### 3.4 W4 paired-scale: +1은 실재하는 제한적 결과다

| Task | 공통 support baseline C/R/T/U | Paired C/R/T/U | 의미 |
|---|---|---|---|
| BASE interface local position, same X | 5 / 2 / 0 / 1 | 6 / 1 / 0 / 1 | +1 improved / 0 regressed |
| BASE identity-negative local control | 7 / 0 / 0 / 2 | 동일 | 새 집계에 따른 regression 없음 |
| Accum identity-negative local control | 5 / 0 / 0 / 0 | 동일 | 새 집계에 따른 regression 없음 |

C/R/T/U는 correct/reversed/tie/unscorable이며 candidate identity 정확도가 아니다. BASE negative controls에서 legacy→joint baseline의 두 변화는 **support 변화**이고 +1에 합산하지 않는다. [R11]

개선된 한 쌍은 애초에 가설을 만들게 한 idx8 Y397 vs idx10 Y378, X[130,236]이다. 따라서 새 holdout 성공보다 **기존 실패의 원인 설명**에 가깝다. 잔여 역전 idx9 Y382 vs idx10 Y378은 세 scale 모두 차이가 음수여서 동일 양의 가중치나 pairing만으로 뒤집을 수 없다. 잔여 unscorable pair는 joint support가 없다. 이 실험을 종료한 판단이 맞다.

한 scale에서는 두 집계가 같고, 선형 보간 median의 두 scale에서도 같다. 따라서 “negative control 12쌍에서 regression이 없었다”를 12개의 독립된 reducer 개선 검증으로 세면 안 된다. 실제로 reducer가 달라질 수 있는 Accum 3-scale negative pair는 세 개였다. Pairwise 비교에는 cycle도 가능하므로 total candidate ranking이나 selector로 바로 가져오지 않는다. [R11][R05]

### 3.5 사람의 불확실성: 이번 계획을 바꾸는 가장 중요한 새 정보

BASE idx0/idx20은 밝기 반사, 계면의 상승/하강과 형성처럼 보이는 움직임을 **전후 약 5초** 보았어도 사람이 확신하지 못했다고 기록됐다. 더 강한 반사를 근거로 idx0를 고른 경위는 있지만, 실제 계면도 강하게 반사할 수 있어 물리적 결론은 불확실했다. [R13]

따라서 이 쌍은 다음과 같이 다룬다.

- 현재 revision-14의 formal labels와 과거 scores는 reproducibility를 위해 보존한다.
- 그 binary label에 대한 agreement와 **실제로 확정된 물리 정답**을 혼동하지 않는다.
- 자유 서술을 parsing해서 라벨을 바꾸거나 불리한 pair를 분모에서 지우지 않는다.
- 모델이 해당 ID에서 무조건 UNRESOLVED하도록 hardcode하지 않는다. 보류도 입력 기반 규칙과 검증이 필요하다.
- 동일 시간창을 다시 보여 달라고 반복하지 않는다.
- 이 불확실성을 idx0/idx11 같은 별도 구조물 실패나 모든 다른 negative로 확대하지 않는다.

이미 기존 evaluator와 9개 추가 control이 uncertainty / unreviewed / abstention / unavailable / missing을 분리한다. 불확실성 시스템을 새로 만들 필요는 없다. [R14]

### 3.6 Structure-context: “있던 값이 무시된다”는 일부 가설은 닫혔다

BASE/Accum에는 각각 12/14개의 등록 template가 보고됐다. Witness의 geometry-unavailable 문구만으로 template가 없다고 할 수 없다. Feature texture가 양수인데 penalty가 0인 후보도 있지만, typed evidence는 두 container의 maximum을 사용한다. **Feature를 penalty로 복사하는 수정은 근거가 없다.** [R15]

`calibrated_artifact_match`의 누락은 best score 0이나 matcher 미실행을 뜻하지 않는다. 정해진 gate를 넘었을 때만 필드가 저장되는 구현이다. 현재 선택된 숫자는 단순 texture/material/static/glare veto를 지지하지 않았고, 이 조사는 이미 미승격 종료됐다. Schema의 `o`/`0` 전사는 True/111 확인으로 해결됐으므로 재확인하지 않는다.

### 3.7 공간 표현: 단계마다 무엇을 얻었는지 구분해야 한다

| 표현 | 확인된 정보 보존 | 여전히 보증하지 않는 것 | 현재 disposition |
|---|---|---|---|
| 후보 주변 O1 bands | 국소 photometry·geometry·availability·peaks | 원격 구조, 완전한 2D layout, identity | 기존 baseline |
| Full-height same-X row profile | 후보 band 밖의 ordered appearance | 다른 후보까지 포함한 packet 전체에 없던 정보인지, Oil의 정체성 | 1D identity 가설 미승격 종료 |
| Ordered column-side | 같은 row/O1 요약에서도 다른 X 순서 | band 내부 Y 순서·joint topology·identity | 로컬 prototype; 별도 Windows lateral 실행 없음 |
| Unpooled joint X/Y | 기존 gradient stencil의 2D arrangement | derivative polarity·checkerboard alias·masked region·physical identity | 로컬 검증 및 Windows 실행 보고 완료; interpretation 일부 미완료 |

Full-height 사례의 band **envelope**와 실제 interval **union**도 정정됐다. Accum idx10의 spike는 기존 band와 일부 겹치며, 같은 원격 특징이 다른 후보의 O1 측정에 이미 있을 수 있다. “한 후보 밖에서 보임”을 “전체 packet에 새 정보가 추가됨”으로 바꾸면 안 된다. [R16][R17]

Joint map은 새 센서나 독립 관측이 아니라, **이미 저장된 pixel과 O1 계산을 덜 요약한 표현**이다. 그래도 학습·판별에 유용한 정보를 보존할 수 있으며, 정보원이 새롭지 않다는 이유만으로 사용 가치가 없다는 뜻도 아니다. 효용은 실제 task에서 따로 검증해야 한다. [R18][R19][C01]

### 3.8 최신 joint Windows 실행

| 항목 | 기록된 결과 |
|---|---|
| 실행 code | `514c1a8560f250bd9b173df0d366e2d0c1095800` |
| Schema | `s11-o2-joint-context-v1` |
| Joint artifact | `8bf2ba8aa56ff91aaad5dea3f00ea861916831185163bb6d8aee3cc783e11e1b` |
| Outputs | 13개 hash 대상 + COMPLETE receipt = 14 files |
| Preserved stored inputs | 32/32 보고; 이전 31 outputs + receipt |
| BASE | origin [0,211], shape [773,578], 124 points, 1,416 baseline bands MATCH |
| Accum | origin [1199,56], shape [584,462], 158 points, 1,012 baseline bands MATCH |

본 감사에서 **joint artifact를 직접 재계산해 full hash 일치**를 확인했다. 반면 private NPZ/image/report의 파일 hash와 보존은 전달된 결과다. 282 points와 2,428 bands를 독립 identity 사례나 성공 건수로 세지 않는다. Baseline MATCH도 gray/support 관련 지정 필드의 일치이지 과거 모든 pixel·모든 feature·physical label의 인증이 아니다. [R20][C03]

## 4. 감사 발견과 우선순위

여기서 P0는 다음 기술 결정을 내리기 전에 필요한 항목이다. Production에 중대한 계산 bug가 발견됐다는 의미가 아니다.

### F01 — P0: 마지막 통계의 domain이 불명확하다

Accum idx10 X[1388,1473], source Y217에 대해 전달된 max `0.008`과 `vm > 0.05`인 열 83/85는 **같은 채널·유효 pixel·window의 raw maximum/any-exceedance**라면 동시에 참일 수 없다. 원인은 reduction axis, 평균 후 최대, window 차이, 단위, 전사 등으로 아직 미확정이다. 공식 joint runner는 이 custom max나 0.05 통계를 출력하지 않는다. [R20][C02]

필요 조치는 원래 분석 정의 한 건과 같은 NPZ slice의 기준 산술을 대조하는 것이다. 새로운 extraction, algorithm correction, threshold 조절이 아니다. §6 W4-R0와 §9에 범위와 코드 예시를 적었다.

### F02 — P0: BASE 비교가 같은 X에서 이루어지지 않았다

현재 전달된 native table은 idx8의 첫 X, idx9의 둘째 X, idx11의 셋째 X를 비교했다. 서로 다른 scene strip이므로 candidate 사이 appearance 차이의 비교가 완성되지 않았다. **원래 요청한 세 같은-X 행만** 완료하면 된다. 다른 후보·추가 영상은 필요하지 않다. [R20]

같은 X라고 모든 sampling footprint가 같아지는 것은 아니다. 후보별 Y가 다르고 mask/조도/주변 문맥도 달라질 수 있다. 각 window의 실제 support와 crop censoring을 기록하고, 낮은 구조물의 절대 Y를 identity 규칙으로 사용하지 않는다.

### F03 — P0: 표현 개선과 identity 효과의 경계가 흐려질 위험

355개 passing tests는 arithmetic, provenance, interface, 원본 보존과 정의된 counterexample를 검증한다. 실제 영상에서 더 많은 계면을 올바르게 채택할 수 있다는 증거가 아니다. Row→column→joint 진행은 모두 이름 붙인 가설과 반례가 있어 무근거 변경으로 단정할 수 없지만, **다음 단계가 또 다른 표현인가 실제 decision experiment인가를 결정해야 한다.** [R17–R20]

권고: joint inspection 뒤에 동일 두 프레임에 대한 연속 descriptor 확장 루프를 닫고, 충분한 단서가 있으면 기존 표현으로 한정된 conditional utility를 검증한다. 충분하지 않으면 자료·취득 전략의 구체적인 차이를 먼저 정의한다.

### F04 — P0: 반례가 하나 존재하면 영구 기각하는 기준은 과도하다

서로 다른 물리 원인이 같은 관측을 만들면 그 입력에서 완벽한 확정 판별은 불가능하다. 그러나 이것이 **다른 구별 가능한 입력에서도 해당 표현이 쓸모없다**는 결론은 아니다. 지금 필요한 것은 모든 pixel 배열이나 물리 원인을 역복원하는 표현이 아니라, 유용한 조건에서 오류를 낮추고 불명확한 조건에서는 보류하는 판별기다.

이는 “알려진 hard counterexample를 무시하자”가 아니다. 동일 관측·상반된 target은 forced certainty를 금지하는 control로 유지하고, mask·지원 부족·후보 경쟁을 다룬 입력 기반 abstention과 full-denominator coverage를 평가한다. 모든 것을 보류해 false positive만 줄이는 결과도 통과시키지 않는다. Selective prediction의 risk–coverage 관점은 이 평가 설계에 도움이 되지만 특정 신경망 채택을 요구하지 않는다. [W01]

기존 feasibility 문서도 “모든 spatial classifier가 불가능하다는 증명이 아니다”라고 구분하고 있다. 이번 계획은 그 구분을 **실행 종료·진입 기준에 반영**한다. [R17]

### F05 — P1: 사람의 uncertainty를 model 실패/성공과 섞을 위험

현재 formal label을 보존한 rank score는 재현 가능하다. 하지만 idx0/idx20의 역전을 확정 물리 오답으로만 제시하거나, uncertain으로 라벨을 바꿔 pair가 사라진 것을 model 개선으로 세면 부정확하다. [R13][R14]

후속 보고는 (a) 원래 frozen label agreement, (b) 전달된 reference qualification, (c) model support/abstention/unknown inventory를 병기한다. 별도 정식 라벨 정정이 필요한 상황이 오면 기존 record/revision/freeze 경로로 처리하고 원래 결과를 보존한다. 이번 감사는 그 변경을 수행하지 않는다.

### F06 — P1: W4 결과가 downstream missing을 모두 설명하지 못한다

W3 funnel은 post-layer nonselection과 pre-retention unknown을 각각 보여 줬다. 이에 비해 spatial experiments는 candidate 주변 신호를 읽는 연구다. 그 하나가 유효해져도 association/allowed-owner/phase/selector 손실이 남을 수 있다. [R10]

후속 identity 출력에는 member/sector와 contradiction provenance를 유지하고, W5/W6에서 같은 trace의 실패 지점과 연결한다. 좋은 sibling의 평균이 나쁜 member의 contradiction을 지워서는 안 된다. 지금 기존 authority를 우회하는 새 scorer를 덧붙이지 않는다.

### F07 — P1: 현재 work-plan 안에 stale 설명이 남아 있다

`work-plan.md:493–496`의 “별도 predicted near/off contract가 없다”는 문구는 현재 구현된 W3 v2와 상충한다. `work-plan.md:31`의 W4 ledger row도 최신 joint Windows execution보다 앞선 full-height prototype 수준을 중심으로 적혀 있어 상세 handoff와 정보 수준이 다르다. [R01][C04]

권고는 작은 문서 정리다. W3 계약 부재 문장을 historical 조건으로 바꾸거나 현재 v2로 연결하고, W4 row를 “local-position closed / identity open / joint reconciliation pending”으로 압축한다. 오래된 사실이 담긴 **날짜별 원문 감사·evidence는 고치지 않는다.** 이 정리는 detector test 재실행이나 새 classifier 구현의 이유가 아니다.

### F08 — P1: custom 분석의 정의가 transfer 과정에서 소실된다

Schema 문자·hash 철자·guide Y·median/max·interval union 등 상당수 불일치가 source defect가 아니라 보고 전사·해석 경계에서 발생했다. Windows agent는 파일을 직접 읽고 사용자가 텍스트를 전달하는 과정에 OCR이 있다고 기록돼 있다. Windows 계산이 OCR로 이루어졌다고 표현해서는 안 된다. [R13][R15][R16][R20]

다음 custom statistic은 채널·단위·source/local slice·mask·reduction axis·원래 식을 한 행의 data record에 붙여야 한다. 기존 분석에서 자동 생성한 숫자와 서술을 분리한다. 현재 R0를 닫은 뒤에도 같은 문제로 반복될 때만 **기존 report owner에 작은 출력 계약을 보강**한다. 새 trace/evaluator framework부터 만들지 않는다.

### F09 — P2: 검은 preview의 원인을 현재 dtype에 맞게 정확히 설명해야 한다

최신 intake에는 작은 양의 gradient가 quantization으로 0 표시가 될 수 있다는 일반적 문장이 있다. 그러나 현재 uint8 raw gray, 중앙차분, 고정 scale의 실제 조합에서는 **유효한 nonzero gradient의 최소값은 1/510**이다. Vertical display에서 최소 1 code level, magnitude display에서도 반올림 후 최소 1이므로 **이 계산 도메인의 nonzero 값이 PNG byte 0으로 반올림되는 것은 아니다.** [C01][C02][C05]

본 감사에서 256×256=65,536개 이웃값 조합에 대해 확인했다. Magnitude는 한 축만 nonzero인 경우가 최소이며 다른 축을 더해도 작아지지 않는다. 최대 부동소수점 오차는 이 결론을 바꾸지 않는다.

따라서 다음 세 가지를 구분해야 한다.

- **정확한 PNG byte 0 + valid stencil:** 해당 중앙차분 값은 0이다. 다만 checkerboard alias처럼 원영상이 균일하다는 뜻은 아니다.
- **육안으로 검어 보이는 byte 1 이상:** 약한 신호가 거의 검게 보이는 표시·시지각 문제다. 실제 값은 NPZ에서 읽는다.
- **Invalid stencil:** magenta/validity mask로 구분하며 absence·edge termination을 추론하지 않는다.

이 정밀화는 viewer runtime의 bug fix 요구가 아니다. 기존 “검게 보인다는 이유로 실제 계면 부재나 연속성을 주장하지 말라”는 안전한 결론은 그대로 유지한다. 추가 Windows capture나 재실행도 필요하지 않다.

## 5. 유지할 기술 방향과 변경할 연구 방식

### 5.1 계속 유지할 것

Generic detector, 동일 frame에서 선택된 실제 candidate Y만 publication, Oil/Foam 독립성, typed contradiction, bounded history/resource, explicit missingness, O2와 O3의 분리, source·label·artifact 원본 보존은 유지한다. Full rewrite, polarity-only association, static overlap=0을 positive 인증으로 쓰는 규칙, residual/반사를 Y proximity로 넘기는 규칙은 채택하지 않는다. [G02][G03][R05]

### 5.2 지금 변경할 것

**“더 많은 신호 표현을 만들면 해결될 것”이라는 암묵적 기대를 “정해진 task의 conditional gain을 검증한다”로 바꾼다.**

Information retention test의 목표는 무엇이 소실됐는지 밝히는 것이고, classifier experiment의 목표는 실제 입력에서 support/abstention의 효용을 확인하는 것이다. 첫 번째 테스트를 무한히 강하게 만들면서 두 번째를 영원히 미루면 제품 성능 진척을 알 수 없다.

새로운 독립 센서를 가져와야만 classifier를 만들 수 있는 것도 아니다. 동일 raw RGB에서 나온 feature를 여러 독립 vote로 세는 것은 금지하지만, 그 feature를 명시적인 공동 model로 쓰는 것 자체가 금지되는 것은 아니다. 동일 기원을 밝히고 empirical validation으로 효과를 입증해야 한다. 반대로 joint array를 보존했다고 곧바로 연결 영역이나 Oil identity라고 부를 수도 없다.

### 5.3 선호하는 다음 구현 경계

R0/R1 후 구별 가능한 조건이 확인되면 **기존 candidate geometry와 raw/joint evidence를 소비하는 offline selective identity challenger 한 개**가 우선이다. 현재 가장 밝은 선, 연결돼 보이는 선, Y가 더 높은 선을 곧바로 Oil로 매핑하는 방법이 아니다.

이 단계에서 먼저 명세할 것은 다음이다.

| 항목 | 명세 요구 |
|---|---|
| 적용 조건 | 어떤 관측 조건에서 현재 근거로 결정을 내릴 수 있는지; scope 선택은 case ID/사람 라벨이 아니라 입력에 근거 |
| Identity와 geometry | holistic candidate identity, point support, original scalar eligibility의 별도 출력 |
| Positive evidence | 무엇이 구별 단서인지, 기존 field와 다른 점 또는 기존 정보의 새 사용 방식 |
| Opposition | structure/광학/지원 부족·모순을 어떤 입력에서 감지하고 어떻게 남기는지 |
| Abstention | conflicting candidates, 부족한 support, 불확실한 reference와 무관한 runtime 보류 규칙 |
| Counter-controls | stationary positive, partial positive, isolated glare, structural step, missing mask, inverted polarity, identical input |
| 비교 방법 | 사전 고정 baseline·task·support/denominator·실패 조건; case-specific fit 금지 |
| 자원 | CPU/메모리 한계와 기존 frame-local owner 재사용; GPU 강제 도입 없음 |

현재 evidence만으로 위 항목을 채울 수 없으면 새로운 classifier code를 쓰지 않는다. 그 경우 **전체 detector 프로젝트를 포기하는 것이 아니라, R3의 정보가 달라지는 자료/취득 질문으로 이동**한다.

## 6. 후속 실행 명세 — W4-R0부터 R5까지

### W4-R0 — 남은 joint 보고의 범위·단위를 한 번 정리

**현 상태:** 실행 가능한 즉시 다음 작업. 현재 work-plan의 handoff와 일치한다.

**입력:** 기존 `joint-context-001`의 JSON/NPZ/receipt와 원래 custom 분석 note/code. Code checkout update, source video, bundle, labels가 필요하지 않다.

**작업 A — Accum 한 통계**

- Target: review-003, native idx10, source X `[1388,1473)`, source Y `217`.
- Channel: `vertical_magnitude`; 해당 파일에서 확인하고 다른 channel을 같다고 가정하지 않는다.
- Requested source Y `[157,278)` = ±60 inclusive rows, 121 rows.
- Crop origin `[1199,56]` → local X `[189,274)`, local Y `[101,222)`, shape `121×85`.
- Mask: **`gradient_valid`**; effective/visible만 쓰면 stencil-neighbour invalidity를 놓친다.
- Raw max와 `any(valid & value > 0.05)`인 열 수를 **동일 slice**에서 계산한다. Columns denominator 85와 valid를 하나라도 가진 열 수를 모두 남긴다.
- 원래 식이 column mean의 max인지, 다른 window/channel인지, 전사인지 확인한다. 이유가 확인되지 않으면 `origin_of_discrepancy=unresolved`로 둔다.
- 원래 코드가 없으면 새 기준 계산을 원래 계산의 재현이라고 쓰지 않는다.

**작업 B — BASE 세 같은-X 행**

| Source X | idx8 native Y | idx9 native Y | idx11 native Y |
|---|---:|---:|---:|
| [130,236) | 397 | 382 | 901 |
| [236,343) | 396 | 406 | 925 |
| [343,449) | 397 | 419 | 922 |

각 행은 세 marker를 **그 행의 같은 strip**에서 비교한다. Candidate별 정확한 Y와 mask·crop·gradient-valid support를 남기고 `different appearance / shared_or_ambiguous / not_assessable` 중 하나로 적는다. 서로 다른 Y의 pixel window가 동일 support라는 주장이나, 차이가 보이면 identity 성공이라는 주장은 금지한다.

**산출물:** 원래 output directory 밖에 보정 note 한 개. 기초 정의·기준 산술·같은-X 3행·남은 한계만 담는다. 전체 hash/receipt를 다시 수동 전사하거나 전체 보고서를 재작성하지 않는다.

**완료 기준:** 숫자의 비교 domain이 정의되고, 같은-X 3행이 채워지거나 각 미측정 사유가 명시되면 완료다. 물리 identity 결론까지 강제하지 않는다. 원래 식 부재나 mask censoring을 이유로 다음 metadata 요청을 자동 생성하지 않는다.

### W4-R1 — Joint appearance 가설을 종결하거나 한 번의 검증으로 연결

**진입:** R0 완료 또는 기존 분석을 복원할 수 없다는 명확한 결과.

| 결과 | Disposition | 다음 동작 |
|---|---|---|
| 명확한 structural negative와 positive 사이에 입력 기반으로 재현 가능한 arrangement 차이가 남고 반대 controls도 정의 가능 | `CONTINUE_REUSE_ONLY` — 아직 미승격 | 기존 raw/joint 배열을 사용해 R2 명세 한 개 |
| 차이가 소실되거나 class 간 공유되어 현재 제안의 구별 근거가 없음 | `CLOSED_WITHOUT_PROMOTION` | 이 appearance→identity 가설 종료; 필요 시 R3의 다른 정보 질문 |
| mask·crop·지원 부족 또는 원래 분석 부재로 비교가 불가능 | `NOT_ASSESSABLE` | 부족한 정보와 필요한 조건 변화 명시; 같은 추출 반복 금지 |
| idx0/idx20만 분리되지 않음 | 전체 가설의 자동 기각도 성공도 아님 | human ambiguity control 유지; 독립적으로 명확한 다른 대상의 효용과 분리 |

**보존할 negative result:** no new identity gain, no numeric scalar truth, no calibrated O2 acceptance, no new production change. 새로 구별할 수 없는 synthetic collision이 발견됐다는 이유만으로 다음 표현을 자동 구현하지 않는다.

### W4-R2 — 재사용형 conditional identity challenger의 사전 명세

**조건:** R1이 `CONTINUE_REUSE_ONLY`이고 동일 근거로 positive와 negative의 양방향 기대를 기술할 수 있어야 한다. 이는 현재 완료됐다는 뜻이 아니다.

**변경 범위 제안:** 기존 spatial probe는 측정 owner로 고정하고, 판별은 offline 소비 경계로 둔다. `s11_shadow_experiment.py`에 자연스럽게 포함되는 score/decision 실험이면 기존 orchestration을 확장한다. 별도 module이 필요하면 측정과 판단 책임이 왜 분리되어야 하는지 설명한다. Production `src/`나 기존 NPZ/labels는 변경하지 않는다.

**사전 기록:** hypothesis ID 1개, target 1차/보호 지표, 기존 feature/배열, geometry policy, finite resource bound, decision/abstention rule, prior authority와의 관계, input split 역할, 실패 시 종료 기준. 가중치·threshold·대체 geometry를 결과에 맞춰 여러 번 바꾸는 sweep을 하지 않는다.

**Primary endpoint:** 기초적인 정보량 차이가 아니라 **검증 가능한 identity support의 이득과 wrong support의 변화**다. Candidate/point pair 수만으로 sample independence를 주장하지 않는다. 상대 순위만 산출하면 그것을 decision experiment로 바꿔 부르지 않는다.

**필수 보호:** partial positive를 허용하되 isolated-glare max를 금지; 완전한 negative scene에서 top 채택 금지; stationary interface 보호; 동일 관측의 conflicting explanation에서 무조건 확신 금지; 알려진 FULL/EMPTY/Foam meaning 보존; original candidate scalar Y 불변.

**완료 기준:** 구현을 시작하기 전 comparator, data role, expected outcomes, acceptance owner가 정의돼 있고, 그 문서만으로 다음 실행자가 임의 threshold/자료 제외 없이 테스트할 수 있어야 한다.

### W4-R3 — W2를 활성화할 경우의 정확한 조건

**지금 즉시 새 판독을 요청하지 않는다.** R0/R1을 닫는 데는 기존 자료가 충분하다. 추가 자료는 다음 중 실제로 확인한 공백 하나를 위한 것이어야 한다.

| 확인된 공백 | 최소 자료 질문 | 금지되는 반복 |
|---|---|---|
| 적용 범위의 양방향 physical control 부족 | 제안한 같은 arrangement를 갖는 실제 interface와 structure 각각이 있는지 | 모든 후보 재판독, 사후에 쉬운 frame만 골라 성공률 계산 |
| Mask/crop로 핵심 단서가 잘림 | 같은 조건에서 실제 관측 영역이 확보되는지; 기존 저장 source에 있는지 먼저 확인 | 같은 잘린 NPZ 재추출, missing을 0으로 보충 |
| RGB appearance 자체의 심한 ambiguity | 어떤 취득 조건/검증 근거가 달라져야 답이 달라지는지 | idx0/idx20 동일 ±5초 클립 반복, 사람이 반드시 이분법으로 답하도록 요구 |
| Scene-level identity는 확인 가능하지만 scalar truth 없음 | 필요한 X/높이 target만 독립 판독할 수 있는지 | near/off에서 px 정답 생성, native median을 정답으로 사용 |
| 실험은 좋아도 recording 일반화가 불명확 | 데이터의 실제 사용 이력과 다음 recording의 역할 | 같은 SPL#1의 다른 Glass/변환/crop을 독립 holdout이라고 명명 |

이전 W2의 window/frame 예산은 업무량 제한안이지 의무 수집량이 아니다. 이번에는 그 숫자부터 채우지 않는다. SPL#2/3 보류는 유지하고, SPL#1의 bounded shadow 개선 뒤 실제 O2 acceptance에 필요한 단계에서 그 역할을 검토한다. 형식상 recording 이름만 바꿔 partition gate를 우회하지 않는다.

새로운 촬영 조건은 후면 접근이 가능한지, 외부 차광·노출 고정이 가능한지 등의 실제 제약을 먼저 확인한다. 압력 경계·냉매회로 개조, 전용 센서나 GPU 구매를 이 software 계획의 기본 작업으로 포함하지 않는다.

### W4-R4 — 구현된 W3로 실제 출력과 보류를 검증

**진입:** R2의 규칙이 정의되고 허용된 input/control scope가 갖춰짐.

현재 v2 contract를 그대로 사용한다. Exploratory 실행은 명시적 opt-in과 빈 fit declaration을 지키고 **실제 training/calibration을 안 했다고 거짓 표기하는 데 쓰지 않는다**. 학습/threshold 선택이 필요한 경우 먼저 해당 자료 역할과 acceptance owner를 정한다. `CALIBRATED`라고 쓰는 것만으로 chronology나 일반화가 검증되지는 않는다. [R05][C04]

보고해야 할 최소 항목은 §7의 표를 따른다. Known-positive를 모두 보류하거나 미판독 후보를 주로 채택하는 결과는 실용 개선으로 통과하지 않는다. Identity support와 local point accuracy는 별도이고 scalar verified metric은 독립 truth가 없으면 계속 null이다.

**대조 실행:** 같은 입력·mask·geometry·runtime에서 고정 baseline과 challenger를 비교한다. Support가 달라진 결과는 common-support 효과와 별도 coverage 효과로 구분한다. Frame·candidate·point·scale·pair의 분모를 섞지 않는다. 미판독값의 추가 판독으로 결과가 달라졌으면 model gain과 label-support change를 분리한다.

**완료 기준:** 하나의 immutable result와 자동 summary가 해당 가설의 제한된 이득/손해/보류를 설명하고, 미판독·미측정/반대 사례가 드러나야 한다. 이것만으로 W5를 열지는 않는다.

### W4-R5 — O2 수용·후속 행동 연결 또는 가설 종료

**성공 경로:** 적법한 development/calibration/holdout 역할, 고정 operating point, 요구되는 Windows shadow, calibrated error/coverage 및 자원 검증을 기존 O2 owner에서 완료한다. 같은 녹화의 반복 실험으로 대신하지 않는다. 이후 work-plan이 W5/O3를 다음 작업으로 지정할 때만 typed support/association으로 통합한다. [R06]

**실패 경로:** 이 가설과 실패 조건을 evidence에 고정하고 종료한다. 다음 전략은 새 입력 근거가 있을 때만 제안한다. 예컨대 구별 가능한 운전 구간에서의 실증, 조건이 다른 취득, 검증 가능한 자료가 준비된 뒤 경량 supervised challenger는 후보가 될 수 있다. 현재 2프레임에 더 큰 모델을 붙이는 것이 우선이라는 결론은 내리지 않는다.

**정보 불충분 경로:** `NOT_ASSESSABLE`과 정확한 조건을 남긴다. 이것은 모든 detector 접근의 불가능성이나 optical unobservability의 일반적 증명이 아니다. 기존 구현과 근거를 보존한 채, 다음 자료/취득 결정에서 재개 조건을 명확히 한다.

## 7. 새 실험의 수용 지표와 판정 원칙

| 지표 | 정확한 의미 | 같이 보고해야 할 것 |
|---|---|---|
| Verified identity precision | 정체성이 명확히 판독된 supported 후보 중 정답 비율 | 미판독·uncertain 채택 수, 판독 범위 |
| Conservative supported precision | 검증된 정답 support / 전체 support | Unknown을 오답 라벨로 바꾸지 않되 분모에 남김 |
| Visible-frame identity support | 사람이 볼 수 있는 frame 중 검증된 identity support가 있는 비율 | 빈 후보·모든 보류·missing prediction을 분모에서 제외하지 않음 |
| Local-support confusion | exact candidate/basis/X/Y의 near/off와 prediction 비교 | Native/center, unknown point, partial support, unavailable |
| Scalar usability/accuracy | 원래 candidate Y의 출력 가능성·정확도 | 현재 독립 truth가 없어 verified metric 미측정; point와 혼동 금지 |
| No-interface false support | 사람이 계면 부재를 판독한 scene에서 잘못된 support | 기존 review-001 등 negative control을 결정 검증 때 사용 |
| Abstention/availability | UNRESOLVED/UNOBSERVABLE/NOT_EVALUATED/MISSING 각각 | 모두 보류한 결과를 좋은 coverage로 해석하지 않음 |
| Temporal utility | 올바른 관측 간 최장 gap, wrong run, 재획득·최저점·회복 관측 | 실제 episode data가 필요한 후속 지표이며 2개 still로 평가하지 않음 |
| Resource | 같은 input/runtime의 시간·메모리 | test suite 경과시간을 detector FPS로 사용하지 않음 |

가설의 조건부 수용에는 해당 task에서 **실제 verified support의 이득**과 보호 negative의 피해를 함께 확인해야 한다. “차이가 보임”, “synthetic collision을 깸”, “모든 테스트 통과”, “hash 일치”만으로 수용하지 않는다. 반대로 하나의 근본적 ambiguous control이 남았다는 이유만으로 구별 가능한 조건의 효용을 전부 폐기하지 않는다.

Absolute threshold를 이 두 프레임으로 발명하지 않는다. 일반화·최종 field qualification의 수치 기준은 적법한 development/calibration 자료와 제품의 허용 오류·coverage 목적에 맞춰 정하고 holdout 전에 고정한다. Group-wise evaluation은 같은 녹화에서 파생된 관측의 종속성을 보존해야 한다. [W02]

**현재 FIELD FAIL을 유지하는 이유:** 검증된 실제 identity/최종 numeric 개선과 O2 acceptance가 아직 없기 때문이다. 감사에서 코드를 수정하지 않았다는 이유만이 아니며, 앞으로 명시된 수용 기준을 만족하면 그때 상태를 바꾼다.

## 8. 변경 파일·owner와 하지 않을 일

### 8.1 후속 변경의 owner

| 필요 작업 | 기존 owner | 이번 제안의 범위 |
|---|---|---|
| 현재 통계 한 건·3행 보정 | Windows의 기존 analysis note/code | 지금은 source checkout이나 runner를 바꾸지 않고 의미를 정리 |
| Live status의 stale 문구 정리 | `docs/00-project/work-plan.md` | W3 구현 상태와 W4 handoff를 맞추는 문서 변경 |
| 본 문서의 관계 등록 | `docs/README.md` | 기존 두 audit에 본 W4 addendum 한 행 추가; 새 live ledger 금지 |
| 반복되는 custom 통계의 계약 보강이 필요해짐 | `s11_joint_context_run.py` 또는 기존 analysis owner | 작은 자동 summary 확장만; original receipt는 보존하고 새 version/hash로 구분 |
| 공간 측정 추가가 실제로 필요 | `s11_spatial_context_probe.py` | 필요성과 새 정보/재사용을 먼저 명시; 지금 자동 추가하지 않음 |
| Identity challenger | 기존 offline experiment 소비 경계 | Raw measurement와 classifier를 혼동하지 않고 기존 W3 출력으로 연결 |
| Prediction·평가 | `s11_interface_shadow_evaluation.py` | v2/v3 재사용; 동일 evaluator 재구현 금지 |
| 사람 라벨의 정식 수정이 별도로 필요 | 기존 `s11_review_records.py` | Revision/history/freeze 경로; 자유 서술의 자동 변환 금지 |
| Production support/phase | 현재 resolver/tracklet/lifecycle owner | W5/W6 조건이 충족되기 전 수정하지 않음 |

본 감사는 위 변경을 이미 수행한 것이 아니다. 추천하는 저장소 경로는 다음과 같다.

```text
docs/50-diagnostics/s11/s11-w4-progress-audit-and-continuation-plan-2026-10-01-ba1bd6a.md
```

### 8.2 재실행·재요청하지 않을 목록

W0 profile, fixed-score/locality, W4 paired-scale 및 잔여 pair 조사, structure-context schema/field listing, spatial source run, 세 native center union 정정, joint extraction 자체는 다시 하지 않는다. 기존 완료 사항을 바꾸는 실제 입력 오류가 새로 입증될 때만 해당 범위를 좁게 재검증한다.

원본 source hash의 `4d00cb`/`4d08cb` 전사 차이, resolved `02/o2`, 기존 migration/freeze/readiness, idx0/idx20 동일 ±5초 판독은 재요청하지 않는다. 새 라벨·case-specific threshold·full detector replay·새 R번호·SPL#2/3 즉시 개방·전체 repo refactor도 이번 다음 작업이 아니다.

## 9. Windows 실행자에게 넘길 현재 작업 지시

> 현재 work-plan의 joint-context 보고 reconciliation만 마무리한다. 기존 `joint-context-001`의 report/NPZ와 원래 분석 코드·메모를 읽는다. 새 source-video/packet/label이나 extraction run은 만들지 않는다. Accum idx10 source X[1388,1473), Y217에서 채널·단위·mask·reduction axes를 먼저 기록하고, local Y[101,222), X[189,274)의 동일 valid pixel에 대한 maximum과 열별 any(value>0.05)를 계산한다. 원래 max가 평균 후 max인지 다른 범위인지 확인하고, 원래 식이 없으면 unresolved로 남긴다. BASE X[130,236), [236,343), [343,449)의 각 strip에서 idx8/9/11을 같은-X 행으로 비교하고 appearance와 censoring을 구분한다. 기존 원본들은 보존하며, corrected note 하나에 결과와 한계를 모은다. 이 결과는 identity 개선이나 production 승격 판정이 아니다. 이미 해결한 schema/hash·기존 clip 판독은 다시 요구하지 않는다.

### 9.1 한 통계의 기준 산술 예시

아래는 **기존 Windows analysis 안에서 대조할 수 있는 읽기 전용 예시**다. 새 permanent comparator를 만드는 요구가 아니며, 원래 추출 정의를 대신하지도 않는다. 실제 NPZ 값은 이번 감사에서 읽거나 계산하지 않았다. `joint_dir`만 기존 경로로 지정한다.

```python
from pathlib import Path
import hashlib
import io
import json
import numpy as np

joint_dir = Path(r"D:\OilTracker\data\experiments\joint-context-001")
expected = "8bf2ba8aa56ff91aaad5dea3f00ea861916831185163bb6d8aee3cc783e11e1b"
seen = {}

def read_bytes(name: str) -> bytes:
    if not name or Path(name).name != name or "/" in name or "\\" in name:
        raise ValueError("Expected a local basename")
    path = joint_dir / name
    if path.resolve().parent != joint_dir.resolve():
        raise ValueError("Path escaped the existing output directory")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if name in seen and seen[name] != digest:
        raise ValueError("Input changed while reading")
    seen[name] = digest
    return raw

receipt = json.loads(read_bytes("complete.json"))
if (receipt["schema_version"] != "s11-o2-joint-context-v1"
        or receipt["status"] != "COMPLETE"
        or receipt["artifact_sha256"] != expected):
    raise ValueError("Unexpected existing receipt")

def covered(name: str) -> bytes:
    raw = read_bytes(name)
    if receipt["outputs"].get(name) != seen[name]:
        raise ValueError("Read file does not match existing receipt")
    return raw

report = json.loads(covered("experiment.json"))
if report["artifact"]["sha256"] != expected:
    raise ValueError("Unexpected report artifact")
cases = [c for c in report["cases"]
         if c["frame_index"] == 16280 and c["origin"] == [1199, 56]]
if len(cases) != 1:
    raise ValueError("Expected exactly one existing Accum case")
c = cases[0]
points = [p for p in c["points"] if p["candidate_input_index"] == 10
          and p["geometry_basis"] == "native_path"
          and p["source_x_range"] == [1388, 1473] and p["source_y"] == 217]
if len(points) != 1 or c["shape"] != [584, 462]:
    raise ValueError("Exact point or raster geometry mismatch")
with np.load(io.BytesIO(covered(c["numeric_file"])), allow_pickle=False) as arrays:
    full_vm = arrays["vertical_magnitude"]
    full_valid = arrays["gradient_valid"]
    if full_vm.shape != (584, 462) or full_valid.shape != full_vm.shape:
        raise ValueError("NPZ geometry mismatch")
    vm = full_vm[101:222, 189:274]
    valid = full_valid[101:222, 189:274].astype(bool)
    if not np.isfinite(vm[valid]).all():
        raise ValueError("Nonfinite observed values")
    vals = vm[valid]
    maximum = float(vals.max()) if vals.size else None
    count = int(np.any(valid & (vm > 0.05), axis=0).sum())
    result = {
        "channel": "vertical_magnitude",
        "units": "abs(uint8-neighbour difference) / 510",
        "source_x": [1388, 1473], "source_y": [157, 278],
        "local_x": [189, 274], "local_y": [101, 222],
        "window_shape": list(vm.shape),
        "valid_pixels": int(valid.sum()),
        "requested_columns": 85,
        "columns_with_valid_pixels": int(valid.any(axis=0).sum()),
        "raw_valid_pixel_max": maximum,
        "columns_with_any_valid_value_gt_0_05": count,
        "same_domain_invariant": not (maximum is not None and maximum <= 0.05 and count > 0),
        "scope": "One stored analysis claim; no classifier or label decision",
    }
for name in list(seen):
    read_bytes(name)
print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
```

이 예시는 읽은 receipt/report/NPZ의 현재 보존을 확인할 뿐, 읽지 않은 모든 과거 입력을 새로 인증하거나 원래 분석의 생성 경위를 증명하지 않는다. `.05`는 이미 제기된 주장과 같은 비교를 하기 위한 값이며 classifier의 채택 임계값이 아니다. 결과를 출력한 뒤 과거 값에 맞추려고 slice나 threshold를 바꾸지 않는다.

## 10. 이번 직접 검증 기록

### 10.1 통합 focused suite

환경: 프로젝트 `.venv` Python **3.14.4**, pytest **9.1.1**, NumPy **2.5.1**, OpenCV **4.14.0**. Mac 연결에서 실행했다.

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/unit/test_s11_joint_context.py \
  tests/unit/test_s11_lateral_context_probe.py \
  tests/unit/test_s11_spatial_context_probe.py \
  tests/unit/test_s11_spatial_context_run.py \
  tests/unit/test_s11_target_aggregation_contract.py \
  tests/unit/test_s11_shadow_targets.py \
  tests/unit/test_s11_structure_context.py \
  tests/unit/test_s11_paired_scale.py \
  tests/unit/test_s11_identity_profile.py \
  tests/unit/test_s11_shadow_experiment.py \
  tests/unit/test_interface_shadow_evaluation.py \
  tests/unit/test_s11_review_semantics.py \
  tests/unit/test_s11_review_records.py \
  tests/unit/test_oil_interface_witness.py
```

결과: **355 passed in 71.99s**, exit code 0. 그중 saved-output source/CLI, Unicode path, receipt mutation guards 등 integration controls는 test 내부에서 수행된다. 이 시간은 test suite 경과시간이며 detector 처리속도나 Windows 성능 수치가 아니다.

### 10.2 기존 모듈과 독립 gradient 계산 비교

Seed `20261001`로 24개 uint8 raster, effective mask, glare mask를 만들었다. 실제 `measure_joint_context()` 결과를 독립 pixel loop로 구한 중앙차분과 5-pixel validity와 비교했다.

```text
gx = (int(gray[y, x+1]) - int(gray[y, x-1])) / 510
gy = (int(gray[y+1, x]) - int(gray[y-1, x])) / 510
vertical_magnitude = abs(gy)
gradient_magnitude = hypot(gx, gy)
valid = center AND left AND right AND above AND below are visible
```

24개 case의 validity는 모두 정확히 일치했고, magnitude/vertical 최대 절대오차는 `1.1102230246251565e-16`이었다. 이는 측정 operator의 독립 검증이다. 새로운 physical identity 판별 검증은 아니다.

### 10.3 최신 joint artifact

`joint runner`, `spatial probe`, `source adapter`, `O2 evaluator`, `oil_interface_witness`, `oil_interface_diagnostics`, `row_features`의 현재 code hash와 `JOINT_SPEC`으로 fingerprint를 재계산했다.

```text
8bf2ba8aa56ff91aaad5dea3f00ea861916831185163bb6d8aee3cc783e11e1b
```

전달된 Windows artifact와 일치한다. 이 일치로 private source bytes·human label·custom analysis statistics의 진실성이 함께 증명되지는 않는다.

### 10.4 통계 domain의 독립 반례

121×85 배열에서 한 행의 83개 열에만 0.1을 넣으면:

| 계산 | 값 |
|---|---:|
| Raw pixel maximum | 0.1 |
| Maximum of per-column means | 0.0008264462809917356 |
| Columns containing any pixel >0.05 | 83 |

따라서 “최대값 <0.05인데 83열이 초과”는 **max가 평균의 max일 때에는 가능**하다. 실제 Windows 보고가 이 오류였다고 확정한 것은 아니다. Original reduction definition을 먼저 확인해야 하는 이유를 보여 준다.

### 10.5 Preview 검증

모든 65,536개 uint8 이웃값 조합에서 `abs(a-b)/510`의 nonzero가 vertical/magnitude 고정 display의 byte 0이 되는 경우는 0이었다. 유효 zero, 눈에 거의 검게 보이는 nonzero, invalid, 중앙차분 alias를 구분해야 한다는 §4 F09의 근거다.

### 10.6 Governance와 원본 보존

다음 검사를 직접 통과했다.

```bash
python3 scripts/check_detector_governance.py \
  --base-ref 85a01cdf4e3385b51422cf0da675a03a74ab70a7 --include-worktree
git diff --check 85a01cdf4e3385b51422cf0da675a03a74ab70a7..HEAD
```

기존 10월 감사의 bytes가 편입 당시와 동일함을 확인했고, 검사 후 HEAD는 `ba1bd6a...`, worktree는 clean이었다. 기존 source/tests/owner documents를 수정하지 않았다.

### 10.7 이번에 수행하지 않은 검증

Private Windows JSON/NPZ/image의 직접 판독, 현장 R0 수치 재계산, 새 annotation, detector replay, 전체 canonical/Qt suite, Windows viewer 재검증, physical classifier 학습·보정·O2 수용은 수행하지 않았다. 특히 “355 tests 통과”가 이들 미실행 검증의 대체가 되지 않는다.

### 10.8 공유 문서와 포함된 실행 예시 검증

Markdown의 37개 reference 정의와 사용을 점검했고, 35개 저장소 경로가 감사 HEAD에 실제 존재함을 확인했다. 코드 fence, Python 예시 syntax, trailing whitespace와 문서의 History Review / Detector Governance block을 확인했다.

§9.1의 읽기 전용 예시는 별도 container의 합성 receipt/report/NPZ로 검증했다. 같은 slice의 83개 초과 열, invalid peak 제외, 유효 pixel 없음의 null 처리, receipt hash 불일치 거부, nonfinite observed 값 거부, exact point 불일치 거부의 **6개 control이 모두 기대대로 동작**했고 입력 bytes는 유지됐다. 이는 문서 예시 검사이며 Mac의 355개 repository tests와 별도다. Private Windows 수치를 계산한 결과가 아니다.

최종 확인에서도 로컬 HEAD와 `origin/main`은 본 감사 SHA와 일치하고 worktree는 clean이었다. 이번 공유용 문서는 저장소에 추가하지 않았으며 commit/push도 수행하지 않았다.

## 11. 작업 재개와 완료 보고 계약

다음 실행자는 가장 먼저 work-plan HEAD가 본 감사 SHA 이후 바뀌었는지 확인한다. 이미 R0/R1이 완료돼 있다면 해당 evidence를 읽고 이어가며 완료 작업을 반복하지 않는다. Git reset/checkout으로 사용자 진행을 되돌리지 않는다.

각 W4-R 전환은 다음 한 묶음으로 마무리한다.

```text
hypothesis / work item:
exact code and input identity:
observed fact:
not established:
decision: continue_reuse_only | closed_without_promotion | not_assessable
next action and entry condition:
source/labels/production changed: yes/no, exact scope
acceptance owner and field disposition:
```

Live ledger 한 곳만 갱신하고, 실행 방법은 operations, 의미 변경은 architecture/validation, 실제 수치·실패는 evidence에 둔다. Hypothesis가 종료되면 이름과 결과를 보존한다. 테스트나 hash가 늘어났다는 이유로 완료 상태를 승격하지 않는다.

**최종 권고:** 현재 joint 보고를 좁게 정리한 뒤, 기존 픽셀 표현을 더 확장할지 자동으로 묻지 말고 **어떤 입력에서 올바른 계면 관측을 늘릴 수 있는지**를 한정된 decision experiment로 검증하자. 불확실한 두 후보를 반드시 이분법으로 맞히는 과제를 내려놓되, 그로 인해 명확한 다른 구조물 오판과 실제 계면 누락이 해결됐다고 주장하지는 말아야 한다.

## 12. 근거와 출처

저장소 링크는 모두 **본 감사 HEAD에 고정**되어 있다. 이후 main의 변경과 감사 당시 근거를 혼동하지 않도록 했다. `[R01–R20]`처럼 범위로 적은 표시는 해당 표의 관련 자료 집합이며 개별 상세 주장은 인접한 개별 reference를 따른다.

| ID | 자료 |
|---|---|
| R01 | [현재 work-plan / W ledger][R01] — `docs/00-project/work-plan.md` |
| R02 | [문서 관계·권한 router][R02] — `docs/README.md` |
| R03 | [2026-09-17 O1–O5 실행 검토][R03] — `docs/50-diagnostics/s11/s11-observation-redesign-execution-review.md` |
| R04 | [2026-10-01 선행 W0–W7 감사 명세][R04] — `docs/50-diagnostics/s11/s11-detector-improvement-audit-and-work-spec-2026-10-01.md` |
| R05 | [현재 Witness Architecture][R05] — `docs/20-architecture/s11-interface-observability-witness-architecture.md` |
| R06 | [현재 Witness Validation][R06] — `docs/30-validation/s11-interface-observability-witness-validation.md` |
| R07 | [현재 O2 Windows operations][R07] — `docs/40-operations/s11-o2-local-shadow-evaluation.md` |
| R08 | [W0 profile Windows 결과][R08] — `docs/60-evidence/s11/s11-o2-identity-profile-windows-run-001.md` |
| R09 | [W1 목표·집계 controls][R09] — `docs/60-evidence/s11/s11-o2-w1-target-aggregation-controls.md` |
| R10 | [W3 Windows target/context 결과][R10] — `docs/60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md` |
| R11 | [W4 paired-scale Windows 결과·잔여 pair 종결][R11] — `docs/60-evidence/s11/s11-o2-w4-paired-scale-windows-run-001.md` |
| R12 | [Identity context source audit][R12] — `docs/60-evidence/s11/s11-o2-identity-context-source-audit.md` |
| R13 | [사람 판독 근거·시간 문맥·불확실성][R13] — `docs/60-evidence/s11/s11-o2-identity-context-windows-review-001.md` |
| R14 | [Reference uncertainty 평가 검토][R14] — `docs/60-evidence/s11/s11-o2-reference-uncertainty-evaluation-audit.md` |
| R15 | [Structure-context Windows 결과][R15] — `docs/60-evidence/s11/s11-o2-structure-context-audit-windows-run-001.md` |
| R16 | [Full-height spatial Windows 결과·구간 union 정정][R16] — `docs/60-evidence/s11/s11-o2-spatial-context-windows-run-001.md` |
| R17 | [Full-packet novelty·candidate-relative feasibility][R17] — `docs/60-evidence/s11/s11-o2-spatial-context-feasibility-local.md` |
| R18 | [Ordered column-side local prototype][R18] — `docs/60-evidence/s11/s11-o2-lateral-context-prototype-local.md` |
| R19 | [Joint spatial local verification][R19] — `docs/60-evidence/s11/s11-o2-joint-context-local.md` |
| R20 | [최신 joint Windows intake / 미완료 reconciliation][R20] — `docs/60-evidence/s11/s11-o2-joint-context-windows-run-001.md` |
| C01 | [공간 관측 prototype][C01] — `tests/diagnostics/s11_spatial_context_probe.py` |
| C02 | [저장 출력 → joint adapter / viewer][C02] — `tests/diagnostics/s11_joint_context_run.py` |
| C03 | [source-frame adapter / baseline 검증][C03] — `tests/diagnostics/s11_spatial_context_run.py` |
| C04 | [분리된 shadow evaluator v2/v3][C04] — `tests/diagnostics/s11_interface_shadow_evaluation.py` |
| C05 | [기존 O1 gradient·validity 측정][C05] — `src/oil_tracker/adapters/vision/oil_interface_witness.py` |
| C06 | [고정 점수·paired-scale experiment][C06] — `tests/diagnostics/s11_shadow_experiment.py` |
| C07 | [기록된 context/funnel projection][C07] — `tests/diagnostics/s11_shadow_target_audit.py` |
| C08 | [Joint context controls][C08] — `tests/unit/test_s11_joint_context.py` |
| G01 | [S11 governance][G01] — `docs/30-validation/s11-detector-change-governance.md` |
| G02 | [현재 detector logic map][G02] — `docs/20-architecture/s11-current-detector-logic-map.md` |
| G03 | [실패 registry F01–F10][G03] — `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` |
| G04 | [Execution policy][G04] — `docs/00-project/execution-policy.md` |
| G05 | [Physical interface repair parent design][G05] — `docs/20-architecture/s11-physical-interface-evidence-repair-design.md` |
| G06 | [Canonical Windows reviewed truth][G06] — `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` |
| G07 | [제품 SSOT][G07] — `docs/rotary_oil_level_tracker_ssot_spec.md` |

### 외부 확인 자료

- [W01] Geifman & El-Yaniv, *SelectiveNet: A Deep Neural Network with an Integrated Reject Option*, ICML 2019. 이번 계획에는 rejection과 coverage를 함께 평가하는 원리만 사용했다. 이 프로젝트에서 특정 신경망의 성능을 검증하거나 도입을 권고한 근거는 아니다.
- [W02] scikit-learn 공식 Cross-validation 문서. 모델 선택에 사용한 자료의 재평가와 일반화 평가를 분리하고, group 구조·시간 의존성이 있는 자료를 독립 표본처럼 나누지 않는 근거로 사용했다. 현재 설치 library를 바꾸는 권고가 아니다.

확인일: 2026-10-01. 외부 문헌으로 private 영상의 identity를 판정하지 않았다.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R22/R22-3 owner boundaries; W0 profile rejection; W1 target controls and W3 separated prediction/evaluation; W4 paired-scale aggregation, source-context and reference ambiguity; raw structure projections; full-height/column-side/unpooled spatial measurements and collisions; current joint Windows intake and stored-output provenance.
- Prior mechanisms rejected: scalar strength/polarity/motion/source-family identity, forced total ranking from paired relations, envelope-as-union, missing-as-zero, raw-versus-averaged statistic conflation, private coordinate/identity branches, silent label changes, inherited world identity from synthetic image differences, downstream interpolation and premature O3 entry.
- Preserved contracts: generic detector, exact same-frame original candidate Y, independent Oil/Foam, explicit uncertainty/missingness, bounded resources, immutable private evidence and prior audits, current O2/O3/field acceptance boundaries.
- Difference from prior failures: this addendum closes the current measurement-inspection loop before another representation, distinguishes conditional empirical utility from universal identifiability, and reuses already implemented W3 targets rather than restarting previous work.
- Logic-map impact: NONE — audit and proposed continuation only; no production execution or owner changed.
- Failure-registry impact: NONE — no new private physical cause or field repair is established; findings concern evidence scope, evaluation and proposed workflow.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: the latest transferred post-run interpretation loses statistic-domain and same-X comparability; no upstream private detector cause is established. The independent preview finding narrows a display interpretation without changing runtime.
- Logic-map impact: NONE — no source, evaluator, labels, state or publication code was changed by this audit.
- Failure-registry impact: NONE — existing provenance, uncertainty and no-private-shortcut constraints remain in force; FIELD FAIL retained.

[R01]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/00-project/work-plan.md
[R02]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/README.md
[R03]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/50-diagnostics/s11/s11-observation-redesign-execution-review.md
[R04]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/50-diagnostics/s11/s11-detector-improvement-audit-and-work-spec-2026-10-01.md
[R05]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/20-architecture/s11-interface-observability-witness-architecture.md
[R06]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/30-validation/s11-interface-observability-witness-validation.md
[R07]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/40-operations/s11-o2-local-shadow-evaluation.md
[R08]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-identity-profile-windows-run-001.md
[R09]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-w1-target-aggregation-controls.md
[R10]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md
[R11]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-w4-paired-scale-windows-run-001.md
[R12]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-identity-context-source-audit.md
[R13]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-identity-context-windows-review-001.md
[R14]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-reference-uncertainty-evaluation-audit.md
[R15]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-structure-context-audit-windows-run-001.md
[R16]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-spatial-context-windows-run-001.md
[R17]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-spatial-context-feasibility-local.md
[R18]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-lateral-context-prototype-local.md
[R19]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-joint-context-local.md
[R20]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/60-evidence/s11/s11-o2-joint-context-windows-run-001.md
[C01]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/tests/diagnostics/s11_spatial_context_probe.py
[C02]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/tests/diagnostics/s11_joint_context_run.py
[C03]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/tests/diagnostics/s11_spatial_context_run.py
[C04]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/tests/diagnostics/s11_interface_shadow_evaluation.py
[C05]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/src/oil_tracker/adapters/vision/oil_interface_witness.py
[C06]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/tests/diagnostics/s11_shadow_experiment.py
[C07]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/tests/diagnostics/s11_shadow_target_audit.py
[C08]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/tests/unit/test_s11_joint_context.py
[G01]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/30-validation/s11-detector-change-governance.md
[G02]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/20-architecture/s11-current-detector-logic-map.md
[G03]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md
[G04]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/00-project/execution-policy.md
[G05]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/20-architecture/s11-physical-interface-evidence-repair-design.md
[G06]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md
[G07]: https://github.com/teeeeooo/oil_level_tracker/blob/ba1bd6a0acf9156d4636316caa2038cf2e8bd905/docs/rotary_oil_level_tracker_ssot_spec.md
[W01]: https://proceedings.mlr.press/v97/geifman19a.html
[W02]: https://scikit-learn.org/stable/modules/cross_validation.html
