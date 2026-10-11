# S11 재개 확인·P1 구현 마감 및 후속 작업 명세서

작성일: 2026-10-11 (Asia/Seoul)  
기준 커밋: `8fea93f2cfa27c455114d0921bbeacb9f697ad13`  
최종 판정: **P1 오프라인 구현·재검증 완료 / production 미채택 / S11 ACTIVE · O2 OPEN · FIELD FAIL 유지**

## 1. 결론 — 실제로 어디까지 진행됐는가

이전 작업은 명세서만 남긴 상태가 아니었다. 원래 `main`과 분리된 작업트리에 P1 소스, 58개 신규 테스트, 고정 23조건 실험, 회귀 검증, 적용 가능한 패치 및 실행 요약이 남아 있었다. 이번 재개에서는 그 상태를 직접 읽고 동일한 코드로 테스트·실험을 다시 수행했다. 최종 패치와 재개 검증 기록을 전달 가능한 파일로 정리했다.

**완료한 것은 “중앙 위치가 다른 경로 대안을 조기 압축으로 잃지 않도록 보존하는 오프라인 구현”이다. 실제 Oil/Foam을 더 정확하게 선택하는 production detector 또는 report 효능 개선이 완료된 것은 아니다.** 기존 함수를 바꾸지 않고 추가한 구현이므로 현재 프로그램의 최종 검출값은 이 기능으로 달라지지 않는다.

제품 목표는 report에서 계면·Foam 움직임의 방향, 주요 변화, 사건의 순서와 존재를 이해하는 것이다. 따라서 이번 성과는 그 목표로 가기 위한 선행 손실의 수리로 계산하고, 최종 목적 달성으로 계산하지 않는다. 반대로 역할 검증이 안 됐다는 이유로 이미 끝난 P1을 계속 튜닝하는 것도 중단한다.

### 확인 시점과 이번 실행을 분리한 기록

| 구분 | 실제 확인/수행 내용 |
|---|---|
| 2026-10-10 첨부 | 전체 감사·P0–P7 제안. 첨부 당시 production 구현 변경 없음 |
| 재개 시 발견한 기존 작업 | 별도 작업트리의 P1 구현, 테스트, 001/002 실험, 패치·실행 요약 |
| 이번에 직접 다시 수행 | 같은 16개 테스트 파일, 23조건 오프라인 재실험, 29개 입력 해시, 원시 결과 23개 해시 비교, governance, diff 및 패치 적용 가능성 검사 |
| 이번에 추가한 것 | 새로운 재개 검증 기록·로그, 전달 패키지, 이 후속 명세서 |
| 이번에 하지 않은 것 | 새 P2 분류기, production 배선, 전체 sequence replay, 새 영상 decode, Windows 실행, report 효능 시험, commit/push/merge |

## 2. 체크아웃·변경 범위

원래 체크아웃은 `/Users/sunjaekim/Developer/oil_level_tracker`, branch는 `main`이다. 검증 종료 시 HEAD는 위 기준 커밋이며 작업트리는 깨끗했다.

구현 체크아웃은 다음과 같다.

```text
/Users/sunjaekim/Developer/oil_level_tracker-s11-center-20261011
branch: work/s11-center-alternatives-20261011
HEAD:   8fea93f2cfa27c455114d0921bbeacb9f697ad13
상태:   4개 tracked 수정 + 5개 untracked 신규 파일, 미커밋
```

| 파일 | 내용 |
|---|---|
| `src/oil_tracker/adapters/vision/oil_material_path.py` | 기존 소스 끝에 오프라인 API·불변 레코드·검증/탐색 보조 함수 178줄 추가 |
| `tests/test_center_path_diagnostics.py` | 신규 58개 테스트 |
| `scripts/s11_center_path_trial.py` | 입력 고정, 저장된 근거 재구성, 대안 보존 및 불변성 실험 |
| `docs/20-architecture/s11-interface-observability-witness-architecture.md` | 구현 설계·한계·History Review |
| `docs/30-validation/s11-interface-observability-witness-validation.md` | 검증 계약과 제외 범위 |
| `docs/50-diagnostics/s11/2026-10-11-center-path-preflight.json` | 고정 입력·연산·예산 |
| `docs/50-diagnostics/s11/2026-10-11-center-path-trial.json` | 23조건 결과 및 개별 근거 해시 |
| `docs/60-evidence/s11/2026-10-11-center-path-implementation.md` | 구현 성과와 반대 증거 |
| `docs/catalog-by-created-date.md` | 문서 목록 반영 |

이번 재검증 전후 위 9개 파일의 해시는 모두 동일했다. 기존 production 소스는 추가된 소스의 정확한 바이트 접두부 및 AST 접두부로 유지되며, 기존 함수 이름을 재정의하지 않았다. `work-plan.md`와 현재 gate도 수정하지 않았다.

소스 SHA-256: `04178a2e222f46b31e81db876f87fc980a11096adb485109cf2961e5b92ee3bc`  
전체 패치 SHA-256: `dac5f084b472249a2e60c009b49d0954dc2baf463927520192b1f976403059f0`

## 3. 구현한 P1의 정확한 계약

### 3.1 무엇을 보존하는가

기존 material-path 처리의 seed/polarity별 단일 승자가 중앙 위치가 다른 대안을 조기에 지울 수 있다. 새 `diagnose_center_path_alternatives()`는 원래 seed, polarity, 중앙 sector row별로 가장 좋은 원시 경로를 보존한다. 중앙 sector는 원래 5개 분할 중 번호 2이며, 중간 sector가 사라졌다고 남은 sector의 중간을 대신 쓰지 않는다.

최적화 순서는 **경로에 포함된 sector 수, 그다음 기존 지역 점수의 합**이다. 지역 점수는 다음과 같이 기존 규칙을 유지한다.

```text
strength + 0.08 × min(1, abs(signed_contrast) / 0.20)
```

중앙 row를 DP 상태에 포함하는 forward 방식으로 대안이 서로 조기에 경쟁하지 않게 한다. 경로는 최대 5개 node의 bounded backtrace로 유지하고, 기존 좌→우 부동소수점 누적 순서를 보존한다. 단순 경로 수 증대나 마지막 top-k 확장이 아니다.

### 3.2 무엇을 바꾸지 않는가

원래 seed 생성, seed 중심 band, 지역 적격 조건, 인접 sector 연결과 jump 제한을 유지한다. 강도·극성 median 후검사는 별도 결과로 표시하며 완화하지 않는다. `PATH`는 해당 원시 그래프에서 경로가 있다는 뜻이지 광학/물리 역할/최종 출력 적격성이 있다는 뜻이 아니다.

`CenterPathDiagnostics`와 `CenterPathAlternative`는 원시 rows, 원래 sector/X 지지 범위, 강도, signed contrast, channel/scale과 가용성을 반환한다. 선택된 Oil/Foam 좌표는 반환하지 않는다. 원시 중앙 sector의 pooled row와 고정된 중앙 X의 실제 contour를 혼동하지 않는다.

기본 상한은 profile 5개, 높이 2160, 레코드 16,384개, bounded predecessor 비교 50,000,000이다. 전체 수집 예산을 넘으면 `UNAVAILABLE`이며, 앞부분의 유리한 결과만 잘라 내보내지 않는다. 중앙 sector나 필수 근거가 없을 때도 음성 검출로 계산하지 않는다.

### 3.3 10월 10일 설계와 달라진 구현 선택

원래 P1의 목적과 기존 그래프·점수 보존 조건은 유지했다. 구현은 중앙 조건을 상태에 넣는 forward DP로 구체화하여, 양방향 결과를 합칠 때 생길 수 있는 누적 순서 차이를 피했다. 원시 목적함수의 최적 경로와 비가산 median 후검사를 통과하는 최적 경로는 같은 문제가 아니므로 구분해 기록했다.

실행기는 source admission guard를 사용하고, 완료된 결과를 덮어쓰지 않는다. 첫 001 실험은 보존됐으며 entry-point guard가 적용된 002와 이번 재개 실행의 raw capture가 일치한다. 이 hardening을 새로운 검출 성능 향상으로 계산하지 않는다.

## 4. 실행·검증 결과

이번 재개 기록의 원본은 [resume-verification.json](resume-verification.json), 실제 테스트 로그는 [pytest.log](pytest.log)다. 이전 구현 마감 기록은 [prior-execution-summary.json](prior-execution-summary.json)이다.

| 검증 | 이번 결과 | 증명 범위 |
|---|---:|---|
| 집중·관련 owner 회귀 테스트 | **396 PASS / 0 fail / 0 error / 0 skip** | 해당 16개 테스트 파일. 전체 저장소 테스트가 아님 |
| 신규 테스트 | 58개 포함 | 이전에 추가한 P1 테스트를 이번에도 재실행 |
| 고정 조건 재실험 | 23/23 완료 | 저장된 crop/NPZ 기반 오프라인 실행 |
| 기존 raw capture와 비교 | **23/23 SHA-256 일치** | 반복 가능성. 독립 검증 데이터 증가가 아님 |
| 입력 파일 해시 | 29/29 일치 | 해당 실험이 핀 고정한 소스·근거 파일 |
| 원시 상태 레코드 | 33,674개 | 적격/부적격/연결 불가를 포함하는 진단 기록 |
| 경로 검산 | 12,477개 | node, jump, 누적 점수, source lineage. 정검출 개수가 아님 |
| 기존 후보 출력 | 23/23 조건에서 호출 전후 동일 | 해당 candidate generator의 필드 비교. 전체 sequence replay가 아님 |
| governance / diff check | PASS | 변경 계약·공백 검사 |
| 원본 HEAD에 패치 적용 검사 | PASS | `git apply --check`; 원본에 실제 적용하지 않음 |
| 기존 변경 파일 보존 | 9/9 해시 동일 | 재검증으로 구현을 추가 수정하지 않음 |

이전 396개와 이번 396개는 같은 테스트 집합의 반복 실행이다. 792개의 독립 테스트로 합산하지 않는다. 23조건은 4개 recording의 12개 native source frame을 원본·기존 축소 조건 등으로 나눈 것이며, 23개 독립 영상이나 미사용 holdout이 아니다. 단위시험에서는 작은 무작위 그래프 40개에 대해 중앙 위치·극성 조합 400개를 전수 경로 oracle과 비교한다.

## 5. 관측된 개선과 그 한계

아래 위치는 검토된 구간과 겹치는 **중앙 sector pooled sample의 source-row 위치**다. 최종 높이·정확한 contour·새롭게 판정한 ground truth가 아니다. 축소 좌표의 소수는 격자 mapping 결과이며 subpixel 정확도 주장이 아니다. 검토 구간은 추출 후 평가에만 사용됐다.

| 조건 | 기존 보존 결과 중 구간과 호환되는 위치 | 새로 보존된 위치 |
|---|---|---|
| 물 B, native | 없음 | 484–489 |
| 물 B, height 200 | 없음 | 약 484.0, 488.1 |
| 물 C, native | 490 | 489–494; 기존 490 유지 |
| 물 C, height 200 | 없음 | 약 492.3 |
| 물 A, native — Foam 상단 역할 | 476 | 476–481 |
| 물 A, height 200 — Foam 상단 역할 | 없음 | 약 475.7, 479.8 |
| Sample4/f1275, native | 836 | 833–841; 기존 836 유지 |

직접적 성과는 **B의 검토 위치와 호환되는 지역 근거가 있는데도 단일 경로 압축에서 사라졌던 문제를, 원래 규칙을 완화하지 않고 오프라인 표현에 남겼다는 것**이다. 결과 확인 후 해당 Y를 seed로 넣거나, crop·band·예산을 바꿔 맞춘 것이 아니다.

A는 하단 Oil의 정답 자료가 아니다. A의 밝기 의존 Foam support 부재와 실제 upper front 역할 판별은 이번 작업으로 해결되지 않았다. Sample4/f1275의 중앙 sector row 역시 이전 보고의 최종 Oil scalar와 동일한 측정량이 아니므로, 836을 최종 scalar의 정정값으로 사용하면 안 된다. Sample4 42.5–44초의 association/owner 문제도 이 단일-frame 표현 수리만으로 해결됐다고 할 수 없다.

### 음성 대조와 upstream 한계

빈 물/맥주/우유 용기에도 median 후검사를 통과한 native 중앙 row가 각각 **245/301/265개** 남았다. 이는 811개의 최종 오검출이 아니라 서로 다른 조건의 기하학적 대안 수다. 그러나 “경로가 있으면 계면”으로 바꾸면 안 된다는 실제 반대 증거다.

이상적인 기울어진 경계라도 기존 seed 자체가 만들어지지 않는 synthetic은 여전히 미해결이다. P1은 seed 이전의 근거·표현 부재를 수리하지 않는다. 이 한계를 감추기 위해 이번 P1에 seed 확장이나 새로운 edge 연결을 덧붙이지 않는다.

## 6. 비용과 production 미채택 판단

이전 002 실험의 실제 진단 호출은 조건별 약 0.036–1.841초였다. 가장 많은 출력은 5,194개 레코드였다. 별도 allocation probe는 해당 최대 레코드 실사 조건에서 약 3.84 MiB의 peak Python traced allocation을 기록했다. 이는 preprocessing·serialization을 제외하며 process RSS나 모든 입력의 최악 비용을 뜻하지 않는다. instrumentation이 켜진 실행 시간은 일반 호출 시간과 구분한다.

따라서 현재의 적절한 배치는 **오프라인/명시적 on-demand 분석**이다. 모든 영상 frame의 기본 detector 경로로 켜지 않는다. 반대 증거와 실행 비용을 함께 고려한 판단이지, “모든 edge case가 해결돼야 한다”는 요구가 아니다.

production 채택을 보류한 이유는 두 가지다. 첫째, 보존된 대안 중 실제 Oil/Foam을 선택하는 새로운 역할 규칙이 검증되지 않았다. 둘째, 이 대안으로 최종 주요 움직임이 더 잘 전달되는지 아직 시험하지 않았다. 기존 최종 출력이 그대로이므로 report가 개선됐다고 주장할 근거도 없다.

## 7. 전체 프로그램에서의 위치

P0–P7은 10월 10일 작업 명세의 패키지 이름이지, 저장소의 O/D/W gate를 대체하는 새 권한 체계가 아니다. 현재 실행 여부는 `docs/00-project/work-plan.md`, detector 구현·검증 계약은 기존 소유 문서가 유지한다.

| 패키지 | 현재 상태 | 이번 이후의 올바른 진행 |
|---|---|---|
| P0 — 평가 범위·baseline | P1용 23조건·29입력 고정 완료. 전체 현장 평가를 완료한 것은 아님 | O2 및 Windows 비교 범위를 별도로 고정·유지 |
| **P1 — 중앙 위치별 경로 보존** | **오프라인 구현·반복 검증 완료, runtime 미채택** | 이 질문에 대한 반복 튜닝 종료; 다음 실험의 근거 입력으로 재사용 |
| P2 — 물리 역할·구조물 경쟁 | 가설/설계 상태, 효능 미검증 | 기존 matcher를 재사용하되 실제 비교 가능한 반대 근거를 같은 support에서 비교 |
| P3 — Oil association 전달 | 미구현/미검증, O2 결과에 의존 | 검증된 현재-frame 역할 근거가 할당·phase owner·최종 선택까지 전달되는지 수리 |
| P4 — lifecycle/phase | 기존 별도 문제 유지 | FULL release, owner loss, 반전/refill의 전체 창 안전성 검증 |
| P5 — Foam front와 episode | 기존 별도 문제 유지 | 내부 texture가 아닌 실제 upper front 측정 후 episode gate 평가 |
| P6 — Windows/report | 이번 미실행 | canonical 9구간과 최종 report의 주요 움직임 해석 평가 |
| P7 — S11 종결 | 미도달 | 핵심 사건의 방향·순서·존재가 전달되며 잔여 오류가 해석을 뒤집지 않는지 판정 |

## 8. 후속 작업 명세 — 반복을 막는 구현 경계

### 8.1 P1 closeout

이번 소스·테스트·preflight·결과를 하나의 review 단위로 유지한다. 리뷰 시 이 패치에 selector, phase, Foam, report 또는 기본 top-k 변경을 합치지 않는다. 별도 작업트리에 이미 구현이 있으므로 같은 patch를 재적용하지 않는다. 새 checkout에서 재현할 때만 기준 HEAD와 깨끗한 상태를 확인한 뒤 적용한다.

P1의 완료 기준은 “원래 그래프 안의 중앙 위치별 대안과 계보를 정확히 보존하고, 기본 동작을 바꾸지 않는다”이다. 이 기준은 만족했다. 추가 threshold, crop, seed, beam 또는 resource budget 탐색으로 P1을 무기한 확장하지 않는다.

### 8.2 P2 — 다음에 코드로 옮길 범위

**목적:** 원시 경로 존재가 아니라, 실제 계면과 구조물/내부 texture의 설명을 같은 현재 관측 support에서 비교한다. 기존 constellation/ordered-patch 구현을 먼저 재사용한다. 새 이름의 비슷한 descriptor를 추가하는 것 자체를 진전으로 계산하지 않는다.

입력은 기존에 승인된 crop/mask, 경로 또는 관측 fragment의 정확한 support, 역할과 위치 불확실성이 검토된 reference다. frame 번호나 검토 Y를 추출기의 분기 조건으로 넣지 않는다. 다음을 실행 전에 고정한다: reference 선택 규칙, parts 분할, 공통 support 산정, 하나의 제한된 공간 변환, residual 식, 비교 불가 조건, operating point 및 하나의 구조적 ablation.

출력 계약은 현재 support의 식별자/가용성, 각 역할 가설의 measured 여부, 공통 support, residual, 모호성 및 이유 코드다. 새 물리 confidence를 임의 합성하거나 최종 좌표를 출력하지 않는다. 같은 픽셀에서 유래한 특징을 독립 투표로 중복 계산하지 않는다. 구조물 reference가 측정 불가이면 positive 승리가 아니라 비교 불가다.

실제 양성·반대 사례의 분모와 판단 범위를 preflight에서 고정한다. 기존 확인된 양성 7개/잘못된 대상 3개의 소유 기록을 그대로 참조하되, 실제 reference 범위·support가 없는 항목은 새 label로 메우지 않는다. f450 rim, f1320 상부 pattern 대 하부 Oil, rim jump, optical warp, 복제 distractor, 정지 실제 계면 및 잘린 upper front를 기존 의미에 맞게 다룬다. synthetic 충돌은 논리 안전성, 실사 비교는 해당 사용 범위의 효능을 검증하며 둘을 같은 분모로 합치지 않는다.

한 개 고정 prototype과 한 개 사전 ablation에서 주요 잘못된 역할 선택 감소와 확인된 실제 경계 보존이 함께 없으면 해당 variant는 **CLOSED WITHOUT PROMOTION**이다. 대부분 비교 불가이거나 모든 것을 UNKNOWN으로 만들었다면 성공이 아니다. 반대로 주요 사건에 효과가 있고 국소 잔여 오류가 해석을 바꾸지 않는다면 모든 반례 해결을 기다리지 않고 다음 제한된 gate로 보낸다.

**현재 한계:** 이 문서에서 새 residual 식/수치 operating point의 효능이 검증된 것은 아니다. P2의 유효한 반대 reference와 수치 계약을 확인하기 전에는 확정된 production 알고리즘 명세라고 부르지 않는다. 이 세션에서 P2를 구현·실험했다고 보고하지 않는다.

### 8.3 P3/P4 — 검증된 역할 근거의 전달

P2 또는 기존 근거가 유효한 역할을 제공하는 구간에서 후보 → one-to-one association → phase owner 허용 집합 → selector → 같은 frame의 최종 원본 후보 위치를 끝까지 추적한다. Sample4의 국소 누락을 채우는 것만으로 끝내지 않고 비교 창 전체에서 구조물로의 이전, 다른 Oil 소실, 새로운 phase 오동작을 확인한다.

과거 실패한 단순 cost-first 정렬, 오래된 track 일괄 폐기, 큰 jump 무조건 허용을 재도입하지 않는다. 현재 근거와 기존 owner가 충돌하는 경우의 handoff·ambiguity·bounded loss를 명시적으로 다룬다. FULL/EMPTY 상태 자체로 좌표를 만들지 않는다. 자동 좌표 보간·hold로 움직임을 꾸미지 않는다.

### 8.4 P5 — Foam을 Oil과 독립적으로 수리

Foam 존재, upper front 가시성, 실제 front 좌표, episode 유지 여부를 분리한다. A의 상단 근거와 Sample4의 내부 texture 오인 사례를 서로 다른 문제로 평가한다. 밝기 threshold 완화나 오래 출력하기만으로 해결했다고 하지 않는다. Oil이 unknown이어도 실제 Foam front는 유효할 수 있고, Foam이 있어도 front가 프레임 밖이면 좌표는 미측정이다.

### 8.5 P6/P7 — report 목적에서 닫기

production challenger가 생긴 뒤 Windows canonical 9구간의 평가를 유지한다. 현장 자료의 반출 제약을 존중하며 기존 절차로 검증한다. 평가 항목은 주요 상승·하강의 방향, 반전·재유입·Foam 형성/소실의 순서와 존재, 주요 극값 주변 관측, 맥락을 지우는 누락, 가짜 장기 추적이다.

기존 채택된 가시적 동일 Oil 이동 구간의 최대 1초 관측 간격 조건은 해당 범위에서 유지하되, 이를 모든 상태의 절대 프레임 검출률 요구로 확대하지 않는다. 판독 불가 구간은 정상 부재나 정검출로 바꾸지 않는다. 모든 검출을 포기하는 방식도 목적을 충족하지 못한다.

S11 종료는 완벽한 프레임 단위 판별이 아니라, 정해진 사용 범위에서 핵심 사건이 전달되고 잔여 누락·오차가 해석을 뒤집지 않는다는 최종 확인으로 판단한다. 이번 P1 반복 검증은 그 최종 확인을 대체하지 않는다.

## 9. 재현·인수인계

### 9.1 기존 작업트리에서 확인

```bash
MAIN=/Users/sunjaekim/Developer/oil_level_tracker
CAND=/Users/sunjaekim/Developer/oil_level_tracker-s11-center-20261011
cd "$CAND"
git status --short
PYTHONPATH="$CAND/src:$CAND" QT_QPA_PLATFORM=offscreen \
  "$MAIN/.venv/bin/python" -m pytest -q tests/test_center_path_diagnostics.py
```

위 명령은 신규 58개만 실행한다. 이번 실행한 전체 396개 파일 목록과 정확한 명령은 `resume-verification.json`의 `test_files`와 `commands`에 있다.

23조건 실험은 완료된 디렉터리를 재사용하지 말고 새 `OUT`에서 실행한다.

```bash
MAIN=/Users/sunjaekim/Developer/oil_level_tracker
CAND=/Users/sunjaekim/Developer/oil_level_tracker-s11-center-20261011
cd "$CAND"
export PYTHONPATH="$CAND/src:$CAND"
OUT="$CAND/sample/output/s11-center-path-manual-$(date +%Y%m%d-%H%M%S)"
"$MAIN/.venv/bin/python" scripts/s11_center_path_trial.py prepare \
  --evidence-root "$MAIN" --out "$OUT"
"$MAIN/.venv/bin/python" scripts/s11_center_path_trial.py run \
  --evidence-root "$MAIN" --out "$OUT"
```

저장된 근거 crop/NPZ가 원래 체크아웃에 있어야 한다. ZIP은 영상·전체 repo·실행 환경·원시 gzip capture를 포함하는 독립 실행 배포판이 아니다. 새 `prepare`는 기존에 정의된 matrix를 다시 핀 고정하므로, 과거와 같은 입력의 재현을 주장하려면 기존 preflight의 입력 해시도 대조해야 한다. corpus admission 제한을 해제하지 않는다.

### 9.2 로컬 결과 위치

```text
<CAND>/sample/output/s11-center-path-20261011-001/          첫 실험·resource probe
<CAND>/sample/output/s11-center-path-20261011-002/          guard 적용 반복·원래 패치/마감
<CAND>/sample/output/s11-center-path-resume-20261011-001/   이번 재검증·로그·실행 영수증
```

이번 재개 폴더의 `resume_verify.py`가 재검증 절차를 기록한다. 원시 상세 gzip 및 JUnit XML은 로컬에 보존했다. 다운로드 ZIP에는 전체 patch, 그 patch의 신규 파일 5개, prior summary, 이번 실행 영수증·선택 로그, 본 명세서와 무결성 검증 도구를 포함한다.

### 9.3 패치 적용과 배포 상태

전체 patch는 기준 커밋의 깨끗한 원본 checkout에 대해 `git apply --check --whitespace=error-all`을 통과했다. 이미 변경이 들어 있는 candidate에는 중복 적용하지 않는다. 새로운 깨끗한 branch/checkout에서 적용할 때에는 현재 HEAD와 작업 상태를 먼저 확인한다. main이 이후 변경됐다면 새 merge-base와 충돌 검토가 필요하다.

이 패키지는 review/handoff 산출물이다. branch commit, main merge, push, 기본 detector 활성화는 수행하지 않았다. 오프라인 진단 코드의 코드리뷰·채택과 물리 선택 성능의 채택은 별개 결정이다.

## 10. 문서 관계와 근거

본 문서는 2026-10-10 `s11-program-audit-and-detector-work-spec`의 **P1 실행 결과·구현 구체화·현재 상태를 보충**한다. 나머지 P2–P7은 새로 완료된 것이 아니라 이번 증거를 반영해 실행 경계를 정리한 후속 명세다. 프로젝트 current plan, reviewed truth, field 판정, detector governance 권한을 대체하지 않는다.

근거는 본 ZIP의 `resume-verification.json`, `prior-execution-summary.json`, `pytest.log`, `replay.log`, `governance.log`, `candidate-files/docs/50-diagnostics/s11/2026-10-11-center-path-{preflight,trial}.json` 및 `candidate-files/docs/60-evidence/s11/2026-10-11-center-path-implementation.md`다. source·패치 해시로 실제 변경과 연결한다. 실행하지 않은 효능과 현재 증거로 확인된 사실은 위에서 구분했다.

## History Review

- Logic-map nodes: `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`.
- Prior mechanisms reviewed: seed/global-band starvation, per-seed winner compression, original length-then-sum objective, non-additive median checks, existing ordered-patch/constellation work.
- Prior mechanisms rejected: top-k/seed threshold sweeps, path presence as fluid identity, source/frame-specific rescue and reopening closed side-match/cost-order variants.
- Preserved contracts: exact same-frame provenance, unavailable is not negative, no production caller, no interpolation/hold, independent physical-role validation and protected corpus admission.
- Difference from prior failures: original graph alternatives are retained and tested with an exhaustive oracle; empty-vessel alternatives and missing seed cases remain disclosed rather than promoted.
- Logic-map impact: NONE — resume verification and handoff do not change the existing runtime call graph.
- Failure-registry impact: NONE — this closes a bounded offline representation task within F02, not the full field risk.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`.
- First harmful stage: per-seed winner compression can discard position-compatible raw paths before deduplication/top-k; this does not identify the physical target or explain every missing output.
- Logic-map impact: NONE — this closeout preserves the existing runtime and changes only verification/handoff records outside the live plan.
- Failure-registry impact: NONE — no new field mechanism or Windows repair is claimed.
