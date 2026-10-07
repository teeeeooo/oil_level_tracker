# S11 2차 전수 감사 · 실행 결과 및 Detector 후속 작업 명세

> 저장소: `teeeeooo/oil_level_tracker`  
> 기준 HEAD: `9f41d2f8a517da21f570f57ed1b4e2009a9d48db`  
> 감사일: 2026-10-07, Asia/Seoul  
> 현행 상태 소유자: `docs/00-project/work-plan.md`  
> 성격: 첨부 1차 감사의 **검증·구현 실험을 포함한 보완 명세**. 새로운 S11 상태 원장이 아니다.  
> 판정: **S11 ACTIVE / W4 OPEN / O2 미승격 / FIELD FAIL 유지**  
> 배포 상태: main·운영 detector 미변경, commit·push·merge 없음. 테스트 수리안은 detached worktree에만 존재한다.

## 0. 결론

**전체 detector를 다시 작성하기보다, 현재 후보가 실제로 무엇을 측정했는지와 그 관측이 어떤 권한을 갖는지를 먼저 일치시켜야 한다.** 1차 감사의 큰 방향은 유지한다. 이번에는 이를 문서상의 제안으로만 남기지 않고 테스트 수리, 새 반례, 실제 후보의 점수 분해, 한 가지 scorer 대체 실험까지 수행했다.

결과를 세 가지로 구분한다.

1. **테스트 기준 수리:** 기존 golden을 바꾸지 않는 A0B 패치를 구현했다. 완료된 비Qt/Qt 재실행의 합집합은 2,326건 통과다. 다만 최초 Qt 검사에서 발생한 멈춤은 별도 미해결 항목으로 남겼다. main에 적용하지 않았으므로 패치의 검사 결과와 main 상태는 다르다.
2. **추가로 입증한 문제:** 상·하단이 서로 다른 X 위치를 평균내면, Y 방향 밝기 변화가 없는 영상에서도 phase-scan response/coverage/scale consistency가 모두 1.0이 된다. 또한 실제 Y854 후보의 강한 paired-edge는 **같은 방향의 두 gradient**에서 발생했고, 그 계측이 boundary 감점 및 artifact 계산에 관여한다.
3. **검출 개선 판정:** 같은 X 위치끼리 비교하는 scorer 하나를 구현·반증했다. 이 변경은 30fps 진단의 Y821 선택을 해결하지 못했다. 가까운 Y가 나온 일부 프레임을 골라 성공으로 승격하지 않는다. 상세한 4영상 비교 결과와 기각 근거는 §6에 기록한다.

**이 감사가 만든 실질 산출물은 검증된 테스트 수리 패치, 실행 가능한 계측·반증 코드, 새 원인 증거, 그리고 다음 변경의 구체적인 소유 경계다. 현장 검출 성능이 개선됐다고 보고하는 산출물은 아니다.**

### 0.1 바로 이어갈 순서

`A0B 테스트 패치 반영·재검증 → A1 기존 witness에 실제 support/계측 좌표/점수 의존성 연결 → 새로운 identity readout의 양면 반증 → O2 shadow 검토` 순서를 유지한다. 이번 paired scorer는 운영 교체안으로 가져가지 않는다. Foam local-front 개선은 Oil 점수 수정과 분리한다.

이 순서는 “계측을 계속 늘리고 Windows에 다시 실행을 요청하라”는 뜻이 아니다. A1은 아래에 열거한 세 가지 결손을 닫는 **유한한 작업**이며, 같은 질문의 반복 조사나 새 descriptor 계열 추가는 완료 조건이 아니다.

---

## 1. 기준·접근·감사 범위

### 1.1 실제 접근과 보존

| 항목 | 확인 내용 |
|---|---|
| 로컬 저장소 | `/Users/sunjaekim/Developer/oil_level_tracker`에 직접 접근 |
| 로컬 HEAD | 1차 감사와 같은 `9f41d2f8…` |
| 원격 main | `git ls-remote origin refs/heads/main`으로 같은 SHA 확인 |
| 시작 main 작업트리 | clean |
| 격리 환경 | `/tmp/s11-second-audit-20261007-jtt0irop/worktree`, 같은 HEAD의 detached worktree |
| 운영 코드 변경 | 없음. 실험 scorer는 별도 Python 프로세스의 함수 교체로만 실행 |
| 테스트 패치 | 3개 테스트 파일, 102 insertions / 9 deletions |
| 보호 대상 | main의 추적 756파일, 원본 MP4/recipe/truth 12 pin, 별도 human ROI·saved sequence |
| 이전 실행 증거 | 1차 감사의 10개 artifact SHA-256을 첨부 명세의 값과 대조, 모두 일치 |

최종 시각·HEAD·hash·테스트 집합은 Mac의 전체 `execution-summary.json`·`final_receipt.json` 및 전달용으로 선별한 `delivery-summary.json`에 기록했다. `/tmp` 실행 위치와 별도 영구 보존 위치는 §11에 구분한다.

### 1.2 ‘전수’의 의미

이번 감사는 다음 목록을 빠짐없이 대조했다.

- 현행 logic-map **20개 노드**와 failure-registry **S11-F01~F10**의 상세 계약.
- 현행 W/O 단계와 witness·shadow·field 승격 조건.
- vision 모듈 **44개 / 24,399행 / AST 함수·메서드 667개**의 전체 inventory.
- canonical 비Qt/Qt 선택, 테스트 기준 변경의 영향, 4영상 고정 application replay.

**756개 파일의 모든 행이나 667개 함수의 모든 실행 분기를 수동으로 검증했다는 뜻은 아니다.** 수동 심층 검토는 geometry, phase-scan, candidate evidence, hypothesis 점수, phase identity, assembly, characterization 및 진단 계약에 집중했다. lifecycle·selector·publication의 현장 정확성은 계약 검토와 실행 회귀 범위를 넘어 보장하지 않는다.

### 1.3 환경과 데이터 역할

Python 3.14.4, OpenCV 4.14.0, NumPy 2.5.1, pytest 9.1.1, PySide6/Qt 6.11.1을 사용하는 기존 Mac `.venv`에서 실행했다. 영상 디코더는 FFMPEG다. 원격 도구가 표시한 일반 Python 요약과 실제 저장소 환경을 혼동하지 않았다.

네 공개 sample은 이미 반복 검토된 **개발·회귀 자료**다. human ROI는 원본 recipe의 대체 truth가 아니라 별도의 고정 진단 조건이다. private Windows 원본 영상은 직접 열람하지 않았고, 새로운 독립 holdout·학습 partition·사람의 정답 라벨을 만들지 않았다.

---

## 2. 첨부 1차 감사에 대한 2차 판정

| 1차 판단 | 2차 판정 | 이번에 추가한 내용 |
|---|---|---|
| canonical 3실패가 남아 있다 | 원인 확인 유지 | 테스트 수리안을 실제 구현하고 mutation guard 13건 추가 |
| phase-scan coverage는 경계 지지가 아니다 | 확인 | 유효 픽셀 수뿐 아니라 **상·하단 X 표본 불일치 자체가 contrast를 생성**하는 반례 |
| broad/narrow 이름이 독립 증거를 보장하지 않는다 | 확인 | paired scorer에서도 같은 중복 식을 유지했음을 명시하여 원인 분리 |
| 같은/반대 부호 pair가 legacy에서 충돌한다 | 확인 및 실제 사례 연결 | 합성이 아니라 실제 Y854 후보의 center/partner gradient가 둘 다 음수임을 확인 |
| Y854의 직접 거부는 boundary advantage | 정확히 재현 | candidate/hypothesis ID를 직접 결합하고 boundary·artifact 항별 합산을 검증 |
| family demotion은 해결책이 아니다 | 유지 | family blacklist 대신 같은 footprint의 계측 교체 하나를 평가했으나 목표 실패가 지속 |
| 30fps와 2fps 결과를 혼용하면 안 된다 | 유지 | 121행 진단과 2fps application 비교를 별도 결과로 작성 |
| Foam component와 front 소유권을 분리해야 한다 | 유지 | 이번 Oil scorer 결과를 Foam 해결 증거로 사용하지 않음 |

이전 명세의 **A0B/A1/A2는 기존 W4 내부 작업명**으로 유지한다. 새로운 R 번호나 병렬 roadmap을 만들지 않는다. 1차 감사에서 이미 기각한 opposite-sign-only pulse repair, family demotion, exact-row Canny 강제를 새 설계로 재포장하지 않는다.

### 2.1 유지되는 단계 상태

W0의 기존 fixed-profile 평가, W1 target/aggregation, W2 bounded geometry review, W3 output/target binding의 완료 범위를 다시 미결로 돌리지 않는다. W4에는 실제 candidate identity를 개선하는 검증된 challenger가 아직 없다. O2 acceptance는 별도의 controls·partition·운영점·Windows shadow 조건을 요구한다. W5/O3 association, W6/O4 lifecycle, W7/O5 통합 field qualification을 이번 로컬 감사로 승격하지 않는다.

75개 기존 review candidate의 physical interface 13개와 target 10개를 동일 지표로 세지 않는다. real-but-nontarget 3개는 반사·잡음 라벨이 아니다. 30/36 region-model order mismatch 역시 83.3% 검출 오류율이 아니다. 이 구분은 기존 원장·검증 문서의 계약을 유지한 것이다.

---

## 3. 실제 구현한 A0B 테스트 수리

### 3.1 바꾼 것

| 파일 | 변경 |
|---|---|
| `tests/test_r16_refactor_characterization.py` | 두 trace 추가만 legacy view에서 분리. 4종 reason 필드의 현재 값을 검증한 뒤 해당 fixture에 한정해 predecessor 표현으로 변환. mutation guard 13건 추가 |
| `tests/test_foam_component_diagnostics.py` | text read 1개에 `encoding="utf-8"` 명시 |
| `tests/unit/test_s11_foam_front_alternatives.py` | text read/write 4개에 `encoding="utf-8"` 명시 |

current-frame에서는 정확히 다음 두 추가만 분리한다.

```text
artifacts.state.foam_component_diagnostics
artifacts.images.foam_component_labels
```

기존 Oil diagnostic 제외 목록은 그대로이며, detection·candidate·score·기존 image/state는 제외하지 않는다. Foam component의 label dtype, boundedness, source 좌표 결합, 저장·복원은 기존 독립 테스트로 계속 검사한다.

completed-window에서는 다음 네 위치만 처리한다.

```text
sequence_metrics.sequence_selected_authority_failed_gates
sequence_metrics.sequence_selected_phase_identity_failed_gates
candidates[0].features.sequence_authority_failed_gates
candidates[0].features.sequence_phase_identity_failed_gates
```

먼저 **11개 프레임, 프레임 순서, 프레임당 후보 1개, 네 필드의 현재 값 44개**를 검증한다. 3~7번 프레임은 `boundary;boundary_advantage;localized_boundary`, 나머지는 빈 문자열이어야 한다. 그 후에만 20개 달라진 이유 leaf를 predecessor의 `boundary;localized_boundary`로 표현하여 기존 hash와 비교한다.

이는 해당 고정 fixture의 버전 호환 검사다. 모든 `failed_gates` 필드를 무시하는 일반 필터도, `boundary_advantage` 제품 결정을 되돌리는 코드도 아니다. `boundary_advantage`의 실제 계산·실패 이유는 최신 구현을 유지한다.

### 3.2 추가한 방어

잘못된 현재 이유 8조건, fixture 구조 훼손 4조건을 거부하고, 별도 1검사에서 입력 불변성·다른 모든 leaf 보존·score 변경 시 fingerprint 변화까지 확인한다. 현재 이유의 문자열이 바뀌면 legacy 변환 전에 실패한다.

기존 golden, `.oiltruth`, `.oilrecipe`, detector cutoff, skip/xfail, 정책 테스트는 변경하지 않았다. frame index를 사용한 fixture 검증은 production의 frame/Y shortcut과 다르다.

### 3.3 실행 결과

| 검사 선택 | 결과 | 시간 / 해석 |
|---|---:|---|
| A0B 최초 targeted | 45 passed | 28.04초; guard 13건 추가 전 |
| characterization + guard | 16 passed | 4.38초; 기존 3건 + 신규 13건 |
| 전체 `not qt_app` | **2,072 passed** | 1,240.69초; 254 deselected |
| 최초 전체 `qt_app` | **STALLED** | native stack 보존 후 해당 감사 프로세스 종료. PASS로 세지 않음 |
| 동일 코드 전체 `qt_app` 재실행 | **254 passed** | 72.33초; 2,072 deselected |
| 완료된 canonical 합집합 | **2,326 passed** | 교집합 0, 실패·오류·skip 0. 최초 Qt 멈춤의 해소를 뜻하지 않음 |
| 별도 계측 prototype | 18 passed | 1.82초; canonical에 합산하지 않음 |
| preflight 집중 재실행 | 3회 모두 통과 | 매회 fresh process의 동일 6건. 새 고유 테스트 18건이 아님 |

이전 감사의 JUnit과 이번 완료 JUnit의 `(classname, name)` 집합을 직접 비교했다. **기존 2,313개가 전부 포함되고, 누락 0개, 새 guard 13개**다. 전체 Qt 재실행의 성공과 최초 Qt 멈춤은 함께 보존한다. 정확한 판정은 **A0B 기능·테스트 계약 수리 검증 완료 / Qt 실행 안정성 미해결**이다.

중복 실행을 테스트 총수에 더하지 않는다. 최초 targeted 45건과 guard 포함 characterization 16건에는 겹치는 3건이 있다. canonical에 포함되는 새 검사는 13건이다. 별도 계측 prototype의 18건은 canonical과 다른 테스트 집합이다.

`check_detector_governance.py --base-ref 9f41d2f8… --include-worktree`와 `git diff --check`는 격리 패치에서 통과했다. 기계 검사가 통과했다는 사실이 test migration의 의미 검토나 detector 성능 평가를 대체하지는 않는다.

### 3.4 적용 상태

**이 패치는 detached worktree에서 검증했으며 main에는 적용하지 않았다.** 따라서 main을 그대로 검사하면 첨부 감사의 3실패 상태가 해소됐다고 말할 수 없다. 후속 담당자는 patch를 review한 뒤 별도 변경으로 적용하고 동일 선택을 재실행한다. 제품 개선 패치와 합쳐 원인 경계를 흐리지 않는다.

### 3.5 별도 발견: Qt 검사 멈춤과 재실행 결과

최초 전체 Qt 검사는 `tests/unit/test_preflight_controller.py`에 진입한 뒤 진행이 멈췄다. 약 8분 동안 종료되지 않는 해당 감사 프로세스의 native stack을 2026-10-07 11:34:34 KST에 수집했다.

```text
GUI/main thread:
PySide signalInstanceConnect → registerSlotConnection
→ Qt QObjectPrivate::connectImpl → QBasicMutex::lockInternal → wait

Worker QThread:
QObject::~QObject → QThreadWrapper::disconnectNotify
→ Shiboken Sbk_GetPyOverride → PyGILState_Ensure → take_gil → wait
```

**Qt mutex와 Python GIL 사이의 lock inversion과 일치하는 대기 양상**이다. 이것은 stack에 근거한 원인 가설이며, 정확한 application/library 결함 위치가 입증됐다는 뜻은 아니다. 증거는 `qt-initial-stall-native.txt`와 최초 `a0b-qt.log`에 남겼다. 이후 이 감사가 시작한 해당 프로세스만 종료했다.

소스를 고치지 않고 전체 Qt를 `-vv -o faulthandler_timeout=30`으로 다시 실행해 **254건 모두 통과**했다. 이어 preflight 파일을 fresh process에서 세 번 반복했고 매번 6건 모두 통과했다. **재실행 통과는 최초 멈춤을 고쳤다는 증거가 아니다.** A0B 패치는 UI controller를 수정하지 않지만, 이것만으로 모든 실행 순서·타이밍과의 인과관계를 배제하지도 않는다.

따라서 최초 Qt run은 PASS에서 제외하고 **`Qt stability OPEN`**을 유지한다. detector identity 문제와 별개로, worker 종료·QObject 수명·signal connection의 bounded 재현 및 소유권 검토가 필요하다. 이 발견을 숨기기 위해 skip/xfail, 테스트 제외, 무제한 재시도 또는 근거 없는 라이브러리 downgrade를 하지 않는다.

---

## 4. 새로 재현한 계측 반례: X 표본 이동에 의한 가짜 상하 contrast

### 4.1 가설과 수식

현재 `_phase_transition_profile`은 sector 안의 upper/lower visible 픽셀을 **각각** 평균낸다. 두 band가 같은 X 위치를 관측한다는 조건은 없다.

```text
pooled_delta = Σx w_lower(x) · mean_lower(x)
             - Σx w_upper(x) · mean_upper(x)
```

Y 방향으로 전혀 변하지 않는 `I(x,y)=f(x)`에서도 위 식은

```text
pooled_delta = Σx [w_lower(x) - w_upper(x)] · f(x)
```

가 되어 0이 아닐 수 있다. 이는 물리 경계의 유무를 추론한 것이 아니라, **표본이 바뀌었을 때 해당 측정량이 어떤 값을 내는지**에 대한 직접 반례다.

### 4.2 입력과 결과

96×100 uint8 영상, local row 48, 5개 sector에서 각 sector의 왼쪽 10열은 80 DN, 오른쪽 10열은 170 DN으로 만들었다. 모든 Y에서 같은 배열이다. 상단은 0~11열, 하단은 8~19열만 보이도록 한 조건에서는 겹치는 X가 4열 존재한다.

| 조건 | 기존 response / coverage / consistency | 같은 X의 paired contrast |
|---|---|---|
| 모든 위치 관측, Y 변화 없음 | 0 / 1 / 0 | 0 |
| 상·하단 X 분포 이동, 공통 4열, Y 변화 없음 | **1 / 1 / 1** | **0** |
| 상·하단 X 지지가 완전히 분리, Y 변화 없음 | **1 / 1 / 1** | **unavailable / null** |
| 공통 X가 있고 실제 30 DN 상하 step 추가 | 혼합된 pooled 값 | 실제 ±30 DN 보존 |

mask 3종 × 실제 step 0/30 × polarity 2종의 **12개 입력**을 고정했다. 역방향도 동일하게 검사했다. ndarray 입력 불변성, JSON finite 직렬화, raster/row/resource bound, 가장자리 censoring을 포함한 **18개 prototype 테스트가 통과**했다.

### 4.3 계측 prototype의 범위

`paired_support.py`는 각 후보의 3개 radius(3/6/10) × 5 sector에 대해 upper/lower pixel count, 실제 공통 X, 각각의 mean X, pooled/paired mean/paired median delta를 보존한다. 공통 X에서는 radius 안의 상·하 샘플이 모두 유효한 경우만 사용한다.

`identity=UNRESOLVED`, `scalar=null`을 반환하며, static opposition과 실제 boundary support는 **미계측**으로 둔다. 유효 sector 수나 gradient의 방향을 Oil identity로 바꾸지 않는다. native curved path에 수직인 profile이 아니라 **수평 row 기반 실험 계측**이다.

이 방식은 완만한 조명 기울기, 반사와 실제 계면의 동일 외관, texture/structure 혼합을 해결하지 않는다. 동일 X가 부족한 실제 경계의 coverage를 잃을 수도 있다. 따라서 이를 새 필수 admission gate로 곧바로 적용할 수 없다.

또한 이 prototype은 정식 O1 adapter가 아니다. 기존 token/schema/trace lifecycle에 아직 통합되지 않았고, 모든 malformed-input·atomic-write·no-overwrite 계약의 완료를 주장하지 않는다. 재실행은 반드시 새 출력 디렉터리에서 한다.

---

## 5. 실제 영상에서 무엇이 달랐는가

### 5.1 직접 확인한 범위

기존 13개 scalar annotation 프레임을 원본 recipe로 다시 디코딩하고, human ROI의 sample4 frame420/450/480을 추가했다. 합계 **16개 frame/recipe 조건**, 서로 다른 source frame은 **15개**다. frame450이 original/human ROI 두 조건에 들어가므로 독립 표본처럼 두 번 세지 않는다.

source frame의 디코더 전후 위치와 timestamp를 확인하고 새 PNG를 보관했다. 이전 13개 crop의 contact sheet와 새 human ROI 원본 crop도 직접 시각 검토했다. Base의 설명선은 원본에 이미 인코딩된 선이며 이번 감사의 정답 overlay가 아니다.

16조건에서 Oil 후보 **377개**를 대상으로 original gray와 normalized raster의 paired 측정을 계산했다. 계측 전후 detection 전체가 **16/16 동일**했다. 이는 post-hoc 계측의 비변경 검사이지, 16개 프레임의 검출 성공이나 새 debug on/off 검증을 뜻하지 않는다.

### 5.2 frame420, Y821의 반증

아래는 human ROI에서 Y821 candidate의 측정 요약이다. 기존 production의 최소 픽셀 조건과 동일한 classifier 점수라고 해석하지 않는다. 이 표의 요약은 관측 가능한 sector를 기술하기 위한 것으로, 실제 교체 실험에서는 별도로 고정한 support floor를 사용했다.

| Raster | Radius | 독립 pooling | paired mean | 해석 |
|---|---:|---:|---:|---|
| original gray | 3 | 0.292101 | 0.292101 | 같은 X에서도 대비 존재 |
| original gray | 6 | 0.208856 | 0.207465 | 변화 작음 |
| original gray | 10 | 0.348472 | 0.167318 | 넓은 범위의 표본 이동 영향 |
| normalized | 3 | 0.754264 | 0.763889 | paired로 바꿔도 강한 응답 유지 |
| normalized | 6 | 0.728733 | 0.454117 | 넓은 범위의 응답 감소 |
| normalized | 10 | 0.621354 | 0.212083 | 넓은 범위의 응답 감소 |

값은 각 sector의 absolute delta를 48 DN으로 나눈 후 요약·clip한 수치다. physical identity 확률이나 새로운 confidence가 아니다. 원본 gray와 normalized는 같은 관측의 서로 다른 변환이므로 독립 두 표로 투표하면 안 된다.

**결론:** X footprint의 불일치는 실제 넓은 band 측정에도 영향을 주지만, Y821의 작은 radius 응답은 남는다. “Y821은 마스크 평균 오류였으므로 paired로 고치면 제거된다”는 가설은 이 사례에서 성립하지 않는다. Y821을 noise/structure로 새로 라벨링하지 않는다.

### 5.3 Y854 거부 원인의 정확한 점수·좌표 lineage

실제 후보 `oil_hypothesis:b348a3b4404fd3c8dad94743`, input index 5와 동일 ID의 semantic hypothesis를 결합했다. 단순한 nearest-Y 매칭이 아니다. read-only hook 전후 반환 detection이 동일했고 다음 합산이 기존 점수와 수치적으로 일치했다.

| Boundary 항 | 기여값 |
|---|---:|
| broad | +0.194139151 |
| narrow | +0.218846156 |
| polarity | +0.010628102 |
| visibility | +0.079693333 |
| pulse subtraction | **−0.071764166** |
| static subtraction | 0 |
| **Boundary 합계** | **0.431542576** |

| Artifact 항 | 기여값 |
|---|---:|
| broad relief 이후 structural 항 | 0.194370461 |
| static contribution | 0 |
| plateau collision | **0.351571737** |
| **Artifact 합계** | **0.545942197** |

`boundary - artifact = −0.114399621`이며, 현행 요구값 `+0.08`에 못 미친다. 앞선 감사의 `boundary_advantage` 진단을 실제 계산 경로까지 연결한 결과다.

더 중요한 점은 다음 좌표 관계다.

```text
최종 후보 scalar Y             = 854
narrow summary의 center Y      = 853
narrow summary의 partner Y     = 851
center signed gradient         = -0.914509773
partner signed gradient        = -0.670646787
두 gradient 관계                = same sign
legacy paired_edge_strength    = 0.747543391
legacy pulse_artifact           = 0.448526035
```

즉, **같은 방향의 인접 gradient가 paired/pulse 계측에 반영되는 현상이 확인된 실제 후보에도 존재한다.** 아울러 scalar Y와 narrow 계측의 중심 Y가 같지 않다. 이는 broad 전이 위치와 proposal 중심을 각각 사용하는 현행 표현의 결과다. `same-frame provenance`가 지켜진다고 모든 feature가 동일한 한 raster row에서 측정됐다는 뜻은 아니다.

현재 pulse 계측은 boundary 감점, structural artifact, plateau collision의 경로에 관여한다. 그러나 이를 세 개의 독립된 물리적 반대 증거라고 볼 수는 없다. 반대로 상관된 항이 있다는 이유만으로 수학적 오류 또는 artifact 전부 무효라고 단정할 수도 없다.

**하지 않은 변경:** pulse를 0으로 만들기, same-sign이면 Oil로 인증하기, plateau opposition 제거, Y854의 narrow features를 임의로 재계산하여 기존 점수 이름에 덮어쓰기. 기존 opposite-sign-only 수정이 안전 controls를 깨뜨렸다는 증거를 유지한다.

---

## 6. 실제 구현·평가한 단일 challenger

### 6.1 고정한 변경

`challenger-plan.json`을 실행 전에 작성했다. 후보 생성기가 원래 반환한 phase-scan 후보의 수·순서·source·Y는 그대로 두고, 그 후보의 phase contrast만 동일한 X 지지로 다시 계산했다.

- normalized raster, radius 3/6/10, 5 sector를 유지한다.
- paired column의 모든 상·하 샘플이 유효해야 한다.
- sector의 최소 support는 원래 25% pixel floor에 대응하도록 고정한다.
- 원래 boundary/ambiguity 가중치, scale consistency 식, authority cutoff는 유지한다.
- 후보 부족 시 새로운 Y를 생성하지 않는다. paired 계측 불가 후보는 남기되 unavailable로 표시하고 해당 evidence/eligibility를 보류한다.
- artifact/texture opposition을 할인하지 않고 family의 authority tier도 일괄 강등하지 않는다.

이것은 **하나의 계측 대체에 대한 인과·반증 실험**이다. 현재 authority 체계에 임시로 연결했으나 O2를 통과한 제품 readout은 아니다. 같은 점수식을 재사용해도 새로운 분포가 자동으로 calibration되는 것은 아니다.

### 6.2 121프레임 human ROI 진단

saved raw 후보를 고정하고 source frame을 다시 디코딩하여 계측한 뒤, baseline과 challenger를 각각 fresh resolver에 통과시켰다. 이전 raw sequence를 재사용했으므로 전체 acquisition을 처음부터 다시 검출한 실험과는 구분한다.

| 항목 | Baseline | Paired challenger |
|---|---:|---:|
| Frame390~510 행 수 | 121 | 121 |
| Oil 수치 행 | 30 | 29 |
| Foam 수치 행 | 104 | 104 |
| Frame420 Oil Y | **821** | **821** |
| Frame450 Oil Y | 없음 | 없음 |
| Frame480 Oil Y | 없음 | 없음 |

달라진 프레임은 400~404다. 400~403에서는 Y821 대신 Y851/849/850/852가 선택됐고, 404에서는 Y821이 보류됐다. 해당 네 좌표에 Y854의 사람 판정을 이전하지 않으며, frame404 보류도 정답을 모르는 상태에서 개선/오류로 단정하지 않는다. **직접 목표로 삼은 frame420의 실패는 남았다.**

### 6.3 보호 collision controls

기존 latent-cause collision **8쌍/16 scene**을 각각 6개의 반복 프레임, 2fps sequence로 만들었다. 총 32개 sequence 실행에서 full detector 후보 생성과 completed resolver까지 비교했다.

모든 조건에서 baseline/challenger의 전체 후보 source/Y 목록이 같았다. completed Oil 수치 출력은 양쪽 모두 0이고, 새로운 수치 승격은 0이었다. 따라서 해당 고정 collision의 ambiguity를 깨지는 않았다. 다만 동일 scene의 반복 프레임은 실제 움직이는 계면을 검증하거나 현장 false-positive rate를 추정하는 자료가 아니다.

### 6.4 4영상 application/report 재생

| 영상 / 원래 고정 구간 | 행 수 | Oil baseline → challenger | Foam 양쪽 | 기존 truth 수치 반환 양쪽 | 조건부 MAE 양쪽(px) |
|---|---:|---:|---:|---:|---:|
| Base / 0–14.4초 | 30 | 28 → 28 | 0 | 3/3 | 12.333 |
| sample2 / 0–2초 | 5 | 4 → 4 | 0 | 2/3 | 6.500 |
| sample3 / 30.03–105초 | 151 | **29 → 27** | 5 | 2/2 | 12.750 |
| sample4 / 0–56초 | 113 | 101 → 101 | 26 | 4/5 | 7.625 |
| 합계 | **299 / 모드** | **162 → 160** | **31 / 모드** | **11/13 / 모드** | 합산 accuracy로 사용하지 않음 |

총 **8개의 fresh-process application/report 실행, 598개 출력 행**을 비교했다. 기존 13개 truth의 비교 레코드는 수치 유무·실제 Y·오차·비교 timestamp까지 양쪽이 같다. Oil 수치의 same-frame provenance 누락은 양쪽 모두 0이다.

sample3의 변화는 단순히 “2행이 사라짐”이 아니다. **새 수치 7행, 기존 수치의 보류 전환 9행으로 순감소가 2행**이며, 상태만 달라진 1행도 있다. 새 수치는 frame2249/2264/2354/2369/2413/2488/2923, 보류 전환은 frame2503/2518/2893/2908/2938/2953/2998/3013/3043이다. 이들은 기존 두 scalar truth 지점 밖이므로 개선/정확도 회귀로 자동 분류하지 않는다. 전체 변화표는 Mac의 `execution-summary.json`에 보존했다.

sample4는 수치 개수가 같아도 frame330의 Oil Y가 **849 → 851**로 바뀌고, frame315/345의 상태가 바뀐다. Base와 sample2의 tracking fingerprint는 그대로다. 이 결과는 숫자 개수나 희소 truth의 MAE만으로 전 구간의 행동 동등성·identity 품질을 판단할 수 없음을 보여준다.

baseline·challenger는 각 영상마다 새 프로세스로 실행했다. 기존 `AnalysisPipeline`과 report/bundle 경로를 사용했고, 같은 UNKNOWN 초기 상태와 고정 2fps window를 유지했다. canonical 검사와 영상 실행 일부가 겹쳤으므로 wall time을 성능 benchmark로 사용하지 않는다.

same-frame provenance 검사, truth의 수치 반환 유무와 오차를 case별로 비교한다. MAE만 낮아지거나 합계 Oil 수치 수가 유지된다는 이유로 통과시키지 않는다. nearest-time evaluator의 13개 기존 truth와 직접 source-frame의 좌표 비교는 서로 다른 평가 단위다.

**판정: `CLOSED_WITHOUT_PROMOTION` — 제품 교체안으로 채택하지 않는다.**

사전에 고정한 보호 truth의 수치 소실·위치 오차 증가·collision 오승격·provenance 손실 조건은 이 실행에서 발생하지 않았다. 따라서 이를 “사전 보호 gate에서 실패했다”고 바꿔 말하지 않는다. 그러나 보호 gate는 필요조건이지 성능 개선의 증명이 아니다. 확인된 frame420 문제는 그대로이고, 희소 truth의 오차도 개선되지 않았으며, 다른 구간에는 아직 물리적 품질이 판정되지 않은 수치 생성·보류 변화가 있다. 이 변경을 채택할 **긍정적인 identity 효과가 입증되지 않았다**는 것이 미승격 이유다.

이는 1차 감사의 family demotion과 별개 실험이다. 1차 변경은 sample2의 기존 truth 수치를 잃었지만, 이번 paired scorer에서는 sample2가 그대로다. 서로 다른 실험의 회귀와 기각 근거를 섞지 않는다. 추가 threshold 조정으로 이 네 영상에 맞추는 반복 탐색은 수행하지 않았다.

### 6.5 fingerprint 해석

이번 baseline의 네 tracking SHA-256은 **1차 감사의 현행-HEAD 재생 값과 모두 정확히 일치**했다.

| 영상 | Baseline SHA-256 | Paired challenger SHA-256 |
|---|---|---|
| base_sample_1 | `5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7` | `5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7` |
| sample2 | `85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976` | `85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976` |
| sample3 | `feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1` | `094badca884828aa49176cfc7feadf0b7248c7a1aefde6b62ca83017b37c77d3` |
| sample4 | `e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1` | `fec8479d30a99fde718c799cd2a4739e3846cbca096c9991d15d0216d03986cb` |


현재 HEAD의 baseline 재현 확인과 과거 historical golden qualification은 다르다. 특히 sample4의 예전 `0f202947…` 값은 바꾸지 않는다. replay helper의 runtime/tracking expectation이 없으므로 `TRACKING_UNVERIFIED` 상태를 유지한다. 이 감사에서 새로 비교한 baseline fingerprint의 일치 여부는 별도 결과다.

challenger는 `HEAD=9f41d2f8…`만으로 실행 정체성이 표현되지 않는다. 외부 `paired_challenger.py`, `paired_support.py`, 사전 plan의 SHA-256을 함께 보존했다. 임시 함수 교체를 하고도 “운영 HEAD 그대로의 결과”라고 표시하지 않는다.

---

## 7. 현행 logic-map 20개 노드 및 실패 이력 대조

| 노드 | 이번 감사·검증 연결 | 판정 / 보호 경계 |
|---|---|---|
| FRAME-EVIDENCE | 원본 디코딩, recipe별 mask, original/normalized 비교 | geometry와 photometric transform을 분리 |
| OIL-RAW-EVIDENCE | signed pair와 upper/lower sampling 측정 | availability·좌표·support의 의미 보강 필요 |
| OIL-PROPOSAL | 원 후보 수/source/Y 유지 검사 | 재생 결과 개선을 위해 candidate universe를 바꾸지 않음 |
| OIL-HYPOTHESIS | 실제 Y854 hypothesis 항별 분해와 ID 결합 | pulse/plateau 중복 의존성과 측정 위치를 명시 |
| OIL-CANDIDATE | phase-scan evidence 재표현의 제한된 반증 | family 이름을 identity로 사용하지 않음 |
| FOAM-CANDIDATE | 현재 geometry/component 계약, 영상의 mixed support 확인 | component score와 front 위치의 identity는 별도 |
| FOAM-IDENTITY | material context와 ordered-lower 의미 대조 | 관측 문맥을 Foam/Oil publication 권한으로 확대하지 않음 |
| OIL-AUTHORITY | actual reason, boundary advantage, challenger admission | threshold 우회 대신 증거 의미부터 수정 |
| OIL-TRACKLET | full sequence 및 collision 재생 | motion·연속성을 독립 identity로 승격하지 않음 |
| OIL-PHASE-INITIAL | canonical 및 초기 상태 계약 | UNKNOWN/FULL/EMPTY가 Y를 생성하지 않음 |
| OIL-PHASE-FILL | 기존 소유 계약·canonical | W4와 fill gate 완화를 섞지 않음 |
| OIL-PHASE-DRAIN | 기존 소유 계약·canonical | private Base/Accum field 실패는 미해결 |
| OIL-SELECTOR | 121행 및 application A/B 결과 비교 | 다른 후보 선택과 같은 후보의 identity 개선을 구분 |
| OIL-PROJECTION | 수치와 같은 프레임 선택 후보 Y 일치 검사 | carry/interpolation 금지 |
| FOAM-EPISODE | Oil 변경 후 Foam 결과도 별도 비교 | 안정 반복을 spatial front의 물리 인증으로 쓰지 않음 |
| SEQUENCE-COMPOSITION | full resolver 경로 사용 | Oil 먼저, Foam 독립, 최종 alias 문맥만 허용 |
| PUBLICATION-PROVENANCE | application 결과와 source binding | provenance 합격 ≠ 검출 합격 |
| RESULT-PRESENTATION | 실제 보고서·그래프 bundle 생성 | 표시가 관측 수치나 정답을 만들지 않음 |
| CSV-PUBLICATION | tracking rows 재조회 | 반환·보류와 truth 매칭을 분리 |
| TRACE-PUBLICATION | A0B 두 namespace/네 reason 필드 계약 | 진단을 전역 무시하는 test repair 금지 |

Failure-registry의 모든 항목을 상세 검토했다. F01 authority collapse, F02 recall starvation, F03 motion overreach, F04 component leakage, F05 state hard-lock, F06 Oil/Foam cross-coupling, F07 false Foam episode, F08 lifecycle dead end, F09 coordinate/provenance ambiguity, F10 global/private shortcut은 모두 **보호해야 할 활성 회귀군**으로 남는다.

이번 새 증거는 특히 F01/F02/F04/F09/F10을 구체화한다. 그러나 새 registry 번호를 추가하거나 기존 실패를 PASS로 바꾸지 않는다. lifecycle·Foam의 오래된 수치와 문구는 역사적 출처로 읽고, 현재 단계 상태는 work-plan을 우선한다.

---

## 8. 후속 구현 명세 — 기존 W4 안에서 끝낼 작업

### A0B — 테스트 수리안 반영

**이번 산출물:** `a0b-test-contract.patch`.

검토자는 golden 불변, 정확한 reason 위치/현재 값 검증, detector 소스 불변을 확인한다. patch 적용 후 targeted 및 비Qt/Qt canonical을 실행하고, 새 guard 13건을 기존 선택과 구분해 기록한다. 적용 HEAD가 달라지면 기존 hash 비교가 왜 달라졌는지부터 확인한다. 출력 동작을 바꿔 test를 맞추지 않는다.

완료는 “이 감사 worktree에서 통과했다”가 아니라 **채택된 실제 source tree에 수리안이 반영되고 해당 identity에서 검증이 끝난 상태**다. 상태 원장은 그때만 갱신한다.

### A0Q — Qt 실행 안정성 확인: detector 변경과 별도

이번 새 이슈를 work-plan에 연결할 때만 사용하는 보완 작업명이며 새로운 O 단계가 아니다. 우선 owner는 `ui/controllers/preflight_controller.py`, `tests/unit/test_preflight_controller.py` 및 기존 Qt lifecycle 검사다.

최초 native stack과 완료된 재실행을 함께 보존하고, fresh process·동일 Qt 선택·제한된 반복 수·외부 timeout을 고정해 멈춤을 재현한다. timeout은 실패 감지 장치이지 테스트 통과 기준이 아니다. worker terminal signal, `deleteLater`, `thread.quit`, `finished` cleanup의 실제 thread와 객체 수명을 관측해 수정 지점을 좁힌다. 수정 시 완료·실패·취소·세대 교체·close/invalidate에 대한 기존 계약을 각각 보호한다.

종료 조건은 특정 수의 재시도가 우연히 모두 통과하는 것이 아니라 **원인에 연결된 수정·회귀 검사·전체 Qt 확인**이다. 이번 감사는 그 수리를 구현하지 않았다. A1의 read-only 계측 탐색 자체를 차단하는 사유는 아니지만, 채택 변경의 전체 실행 안정성 검증에서는 미해결 항목으로 공개한다.

### A1 — 손실 없는 계측/lineage 연결: 세 결손만 닫기

**목적:** authority를 바꾸지 않고, 다음 세 질문에 실제 자료로 답할 수 있게 한다.

| 결손 | 반드시 보존할 값 | 소유 경계 |
|---|---|---|
| upper/lower support 불일치 | 각 band의 count, 실제 공통 X, pooled/paired 값, censoring 이유 | `oil_supplemental_path.py`의 실제 관측 및 기존 diagnostic sidecar |
| pair의 의미 손실 | center/partner source Y, signed 값, validity, same/opposite/zero/unknown, legacy pair 값 | `oil_shadow_observations.py` → 기존 types/진단 adapter |
| score와 scalar의 계측 좌표 분리 | proposal 중심, broad 전이 위치, 최종 candidate scalar, 실제 score 항의 의존 대상 | hypothesis/assembly → `oil_interface_witness` 또는 기존 진단 owner |

실제 데이터 구조·함수명은 기존 owner를 따라 정한다. `phase_candidate_assembler.py`의 기존 frame-local sidecar와 witness 경로를 재사용하고 병렬 resolver를 만들지 않는다. 새 자료가 `PhaseDetection.debug_metrics`, `OilCandidateEvidenceIndex` 또는 resolver 입력으로 새어 들어가지 않도록 검사한다.

이 감사의 prototype은 계산 예시·반례 코드로 가져오되 그대로 제품 모듈에 복사하지 않는다. bool/nonintegral index, 작은/빈 raster, duplicate candidate, source/Y mismatch, ndarray alias, 경로 밖 출력, 부분 저장, 입력 변조, Unicode/foreign cwd 등 기존 O1 계약의 전체 방어를 적용해야 한다.

**필수 동등성:** 기존 candidate 수/순서/source/Y/score/flags, raw·completed 반환, Foam, 이벤트, CSV, 보고서, 기존 diagnostic 필드는 그대로다. 새 namespace만 명시적으로 분리한다. 원본 recipe와 human ROI는 별도 조건으로 유지한다.

**종료 조건:** 새 schema 및 availability 검증, 위 반례/실제 ID fixture, 기존 collision 보호, 기존 4영상 출력 동등성, 후보·sector·scale·trace byte 및 동일 조건의 시간/RSS 상한을 확인한다. 이 작업으로 classifier precision이 좋아졌다고 보고하지 않는다.

### A2 — joint identity readout: 점수 항 제거가 아니라 판단 계약 교체

**진입:** A0B가 실제 채택되고 A1의 lossless 검증이 완료돼야 한다. 이번 paired scorer는 이 gate를 우회하여 채택할 수 없다.

다음 후보 readout은 최소한 다음을 동시에 다뤄야 한다.

- 같은 방향의 shoulder가 있는 실제 계면을, opposite return으로 잘못 해석한 계측만으로 거절하지 않을 것.
- sharp step, brightness/CLAHE response, texture 또는 같은 Y의 다른 family만으로 identity를 인증하지 않을 것.
- 두 물리 해석이 같은 관측을 만드는 기존 collision은 unresolved로 남길 것.
- 실제 support가 겹치는지와 물리적으로 독립된 증거인지 구분하고, pulse → structural → plateau 같은 공유 의존성을 여러 독립 표로 세지 않을 것.

**권장 입력 경계:** 실제 측정 footprint와 원 gray profile, source-bound normalized 보조 view, 계측 좌표 관계, optical/texture opposition 및 missingness. native contour가 존재하면 그 실제 X/Y와 normal 방향에서 읽는다. native path가 없으면 곡선을 만들어 채우지 않는다.

**출력 축:** `physical identity`, `target role`, `scalar/contour usability`를 분리한다. actual interface이나 target이 아닌 내부 경계, partial path만 맞는 candidate, identity는 지지되지만 scalar가 불확실한 경우를 다른 상태로 보존한다. scalar는 원 candidate/contour binding을 유지한다.

규칙형 또는 작고 규제된 모델을 사용할 수 있지만, 모델의 작음은 정확성의 증거가 아니다. 기존 75개 reviewed candidate를 새 학습/보정 세트로 임의 재분류하지 않는다. 새로운 학습이 필요하면 촬영 lineage에 따른 개발·보정 역할을 먼저 고정하고, 노출된 회귀 자료와 untouched holdout을 분리한다.

**유한한 실행 단위:** 입력 feature/schema, 하나의 readout, operating-point 선택 방식, primary endpoint, 보호 cases를 한 번 고정한다. predictor 없이 Windows에 같은 자료를 다시 추출하라고 요청하지 않는다. 고정 readout이 native/partial positive와 negative controls를 함께 통과하지 못하면 원인을 정리하고 해당 안을 닫는다. 동일 regression Y를 맞출 때까지 cutoff를 계속 바꾸지 않는다.

### A3 — Foam local-front 지원 분리

주 owner는 `foam_front_detector.py`이며 material identity·diagnostics·episode tests를 함께 본다. 현재 ROI가 rim을 포함했던 문제, human ROI에서도 구조가 Foam과 연결되는 문제, component 상단 극값의 identity 문제를 분리한다.

component 후보를 유지한 상태에서 반환 front의 column별 실제 support와 구조/반사/혼합 부분을 별도로 보존한다. `component_contains_foam`과 `front_usable`을 같은 boolean으로 쓰지 않는다. front support가 mixed/unresolved이면 scalar 사용 가능성을 별도로 보류한다. 모든 curved front를 평평하게 만들거나 bbox veto를 삭제하는 방식으로 해결하지 않는다.

필수 controls는 rim, 실제 Foam, structure가 없는 curved front, 중앙 구조와 연결된 mixed component, glare, detached/bottom-connected/layer/droplet, no-Foam이다. 원본/human ROI 모두 평가한다. 기존 사람의 정성 판정과 approximate click에 임의의 ±pixel truth tolerance를 붙이지 않는다.

새 front를 선택하게 되는 시점에는 same-frame contour binding과 consumer/schema 변경, 독립 Foam episode 회귀를 함께 제출한다. Oil이 가까워졌다는 이유로 Foam front도 맞다고 평가하지 않는다.

### A4 — 평가·승격 패킷

기존 W3 evaluator와 target binding을 사용한다. 별도 성공률 계산기를 병렬로 만들지 않는다.

| 평가 단위 | 함께 보고할 것 |
|---|---|
| Candidate inclusion | 원 universe, 실제 누락/새 후보, first-loss stage |
| Physical identity | positive/negative/unresolved, wrong positive와 abstention |
| Target role | target / real-but-nontarget / unresolved |
| Scalar | 수치 반환 수, 보류 수, exact-frame 또는 명시적 nearest-time 오차 |
| Contour | 실제 동일 X의 정답 지지, 부분 일치, 미검토 support |
| Temporal | 2fps 운영과 30fps 진단, prefix, 실제 elapsed time와 frame count |
| Data role | recording/session lineage, 기존 노출, 개발/보정/회귀/holdout |
| Cost | 동일 시스템·스레드·입력의 직렬 paired time/RSS/trace bytes |

첫 현장 패킷은 input pin, source+external-code identity, prediction table, operating point, 한계/보류, 반례, 재현 명령을 포함해야 한다. 실행 COMPLETE, local PASS, shadow 판별, production behavior, field qualification은 서로 다른 판정이다.

---

## 9. 적용·기각·롤백 규칙

| 변경 | 허용 | 금지 |
|---|---|---|
| A0B | 정확한 진단 계약 검사와 UTF-8 수정 | golden 변경, skip/xfail, field 상태 승격 |
| A1 | availability/support/lineage를 진단에만 추가 | legacy 점수나 authority를 조용히 변경 |
| A2 | 고정된 새로운 readout의 양면 평가 | source family/Y/polarity를 identity 정답으로 사용 |
| A3 | component와 local front의 소유권 분리 | 시간축 확인으로 오염된 front를 정답으로 인증 |
| 승격 | 고정 조건의 모든 결과와 손실 공개 | 선택된 프레임의 개선만 제시, MAE에서 보류 삭제 |

이번 교체 실험의 보수적 보호 기준은 기존 수치 truth가 사라지거나 기존 오차가 늘면 교체안을 기각하는 것이다. 이는 baseline의 모든 수치가 실제 정답이라는 주장이 아니다. 향후 **확인된 잘못된 수치 → 적절한 보류**의 이득을 평가하려면 그 물리 판정과 risk/coverage 기준을 별도로 제시해야 한다.

prototype rollback은 외부 scorer를 설치하지 않은 새 프로세스에서 실행하는 것이다. main에 남은 runtime monkeypatch는 없다. 테스트 수리 patch의 rollback은 해당 3파일의 patch만 역적용하는 것으로 한정한다. 작업트리 전체 reset/clean, 기존 evidence 삭제, recipe/truth 초기화는 요구하지 않는다.

---
## 10. 기존 문서와 관계 · 하지 않은 일

| 문서 | 유지할 역할 | 이번 명세와 관계 |
|---|---|---|
| `docs/00-project/work-plan.md` | 유일한 현재 W/O 상태·다음 행동 owner | 이 문서로 대체하지 않음 |
| `docs/00-project/roadmap.md` | milestone 순서·상태 | S11 완료나 W5 진입으로 표시하지 않음 |
| `docs/20-architecture/s11-current-detector-logic-map.md` | 실제 runtime owner와 20개 노드 | 운영 flow가 바뀌지 않았으므로 수정 없음 |
| `docs/30-validation/s11-detector-change-governance.md` | 변경 증거·History/Impact 계약 | 패치 검사 및 이 명세에 적용 |
| `docs/30-validation/s11-interface-observability-witness-validation.md` | O1/O2 extraction·shadow·partition·승격 | 이번 prototype의 미완료 범위를 여기와 대조 |
| `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` | 실패 재발 방지 | F01~F10 모두 유지 |
| `docs/50-diagnostics/s11/2026-10-06-foam-structure-reference-audit.md` | 기존 ROI·structure·사람 판정·reason repair 조사 | 판정 보존, 실제 score lineage와 새 반증을 추가 |
| 첨부 `s11-audit-and-detector-work-spec-2026-10-07.md` | 1차 고정 HEAD 감사와 A0B~A5 제안 | 원문 보존. A0B 구현·실험 결과로 구체화 |
| 이 2차 명세 | 새 실행 증거와 채택/미채택 경계 | supporting audit. 병렬 상태 원장 아님 |

이번에는 **하지 않은 일**도 명확하다. private Windows 원본 열람·새 holdout 평가·실제 identity classifier 학습·새 scalar truth 생성·운영 detector 반영·field qualification·hardware/촬영 조건 변경은 수행하지 않았다. 기존 work-plan의 별도 영상 확보 계획도 바꾸지 않았다.

원본 영상을 확인하고 scorer까지 실행한 결과, 지금 채택할 근거가 있는 변경은 테스트 계약 수리와 후속 진단 계약의 구체화다. paired scorer는 실제 실패를 해소하는 수정안으로 남기지 않는다. 다음 단계의 남은 핵심은 **긍정 지지와 반대 증거를 함께 판독하는 candidate identity readout의 검증**이며, 테스트 수 증가나 자료 추출만으로 대신할 수 없다.

---

## 11. 산출물·재실행·인계

### 11.1 파일 구분

| 파일 | 용도 |
|---|---|
| 본 Markdown | 전체 감사 결론·후속 실행 명세 |
| `delivery-summary.json` / Mac `execution-summary.json` | 전달용 선별 요약 / 전체 실행 요약. 두 파일은 byte-for-byte 동일하지 않음 |
| `a0b-test-contract.patch` | 검증한 3개 테스트 파일 변경. 제품 detector patch 아님 |
| `paired_support.py`, `test_paired_support.py` | 계측 prototype와 18개 controls |
| `challenger-plan.json`, `paired_challenger.py` | 실행 전 고정한 단일 scorer 실험. 운영 채택 금지 |
| `run_new_probes.py` | 12 합성 입력·16 real frame/recipe 조건의 post-hoc 계측 |
| `inspect_score_lineage.py`, `score_lineage_summary.json` | 실제 Y854의 ID 결합·점수 분해·같은 방향 pair 증거 |
| `run_paired_sequence.py`, `paired_sequence.json` | 고정 121행의 baseline/challenger 비교 |
| `run_collision_challenger.py`, `collision_challenger.json` | 8쌍 collision의 full sequence 비교 |
| `run_paired_public.py`, `paired_public_results.json` | 4영상 application/report baseline·challenger 결과 |
| `a0b-*.xml/log`, `paired-controls.xml/log` | 실제 pytest 결과; 전체 파일은 Mac 보관본에 있음 |
| `qt-initial-stall-native.txt`, `qt_preflight_stability_probe.json` | 최초 멈춤의 native stack과 집중 재실행 결과; Qt 안정성 미해결 |
| `final_receipt.json` | 입력·소스 보존, 실행 identity, 산출물 hash |

**전달용 ZIP과 Mac의 전체 증거를 구분한다.**

전달 파일 `s11-second-audit-code-and-evidence-2026-10-07.zip`에는 테스트 패치, 재실행 Python 코드, 사전 plan, 계측/score 요약, **선별된 `delivery-summary.json`**, README 및 파일별 SHA-256 manifest가 들어 있다. `delivery-summary.json`은 전체 `execution-summary.json`의 byte-for-byte 복사본이 아니며, 자체 `kind`에 이를 명시한다. 채팅의 별도 JSON 파일도 이 전달용 요약과 동일한 내용이다.

전체 raw frame PNG, 377-candidate 계측, 121행 전체 결과, collision 전체 결과, canonical JUnit/log, Qt native stack, 8개 application/report bundle 및 full receipt는 다음 Mac 경로에 복사·hash 검증했다.

```text
/Users/sunjaekim/Developer/oil_level_tracker/sample/output/s11-second-audit-20261007-001
```

이 위치는 Git 추적 대상 밖의 evidence 보관 디렉터리다. **Git 문서에 편입하거나 work-plan을 수정한 것은 아니다.** 원래 실행 위치는 `/tmp/s11-second-audit-20261007-jtt0irop`이며, JSON 내부 경로는 실행 출처 보존을 위해 그대로 남겼다. 보관 복사본을 읽을 때 그 prefix만 위 영구 보관 위치로 치환한다. 영상·recipe의 원본 경로는 바꾸지 않는다.

detached worktree에는 검증된 테스트 변경만 남겼다. 작업자는 전달 patch를 채택한 뒤 worktree 필요 여부를 판단할 수 있다. 이번 감사에서 사용자 작업트리를 reset하거나 다른 worktree를 삭제하지 않았다. 이 Markdown은 채팅 전달 문서이며 main 추적 문서에 자동 편입하지 않았다.

### 11.2 안전한 재실행

아래 명령은 의도적으로 **실험 코드만 새 디렉터리에 복사**한다. 기존 receipt·JSON·PNG·replay bundle을 덮어쓰지 않는다. `OIL_REPO`에는 동일한 source와 기존 sample 입력을 가진 저장소를 지정한다. saved-sequence 실험은 기존 human ROI recipe와 121행 source JSON도 필요하다.

```bash
export OIL_REPO=/Users/sunjaekim/Developer/oil_level_tracker
export PY="$OIL_REPO/.venv/bin/python"
export PACKET=/path/to/extracted/s11-second-audit-packet
RUN=$(mktemp -d /tmp/s11-second-audit-rerun-XXXXXX)
cp "$PACKET"/*.py "$PACKET"/challenger-plan.json "$RUN"/
export PYTHONDONTWRITEBYTECODE=1
export QT_QPA_PLATFORM=offscreen
export PYTHONPATH="$RUN:$OIL_REPO/src:$OIL_REPO/tests:$OIL_REPO"

"$PY" -m pytest "$RUN/test_paired_support.py" -p no:cacheprovider
"$PY" "$RUN/run_new_probes.py"
"$PY" "$RUN/inspect_score_lineage.py"
"$PY" "$RUN/run_paired_sequence.py"
"$PY" "$RUN/run_collision_challenger.py"
"$PY" "$RUN/run_paired_public.py"
```

재실행은 분포·threshold를 바꾸지 않는 재현이어야 한다. 다른 환경이나 decoder에서 결과가 다르면 그 환경과 원본 pin부터 기록한다. 새 값을 historical golden으로 쓰지 않는다.

A0B는 원하는 실제 개발 branch에서 **기준 HEAD·작업트리를 먼저 확인하고** 다음 순서로 반영한다. 아래는 담당자 검토 후 수행하는 명령이며, 이번 감사가 main에서 실행한 명령은 아니다.

```bash
git apply --check /path/to/a0b-test-contract.patch
git apply /path/to/a0b-test-contract.patch

PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen \
  .venv/bin/python -m pytest -m 'not qt_app' -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen \
  .venv/bin/python -m pytest -m qt_app -vv -o faulthandler_timeout=30 -p no:cacheprovider
.venv/bin/python scripts/check_detector_governance.py \
  --base-ref 9f41d2f8a517da21f570f57ed1b4e2009a9d48db --include-worktree
git diff --check
```

### 11.3 무결성

실행 증거 마감·native 보존 검증: **2026-10-07 11:43:43 KST**. 시작·종료 HEAD와 원격 main은 `9f41d2f8…`로 같고, main status는 clean이다. main 추적 **756파일 SHA-256**, 원본 **12 corpus pin**, 대조한 **1차 artifact 10개**가 모두 보존/일치했다.

| 대상 | SHA-256 |
|---|---|
| 테스트 패치 | `615a94a61cef04242f7bda785e3d702c0480d2053179cc9ce67b1f7352950db5` |
| Mac full `final_receipt.json` | `cdd32762ea2771d72edd9f99de4bc87b840c6ff1291a93766de06dfc94c89104` |
| Mac full `execution-summary.json` | `ac96335704b821221ee299d5b3c00fda92363ec982e9be7c1a1783c0efa602d2` |
| 채팅 전달용 summary JSON | `37d6ff27db4ea4ae8b4eef332e775d1190f4dade1db4c3c04579f80a88d3b22e` |
| 채팅 전달용 code/evidence ZIP | `1e8be03b59dae0291070ca0623b2f4e49a5542838b40b677f1149297bde18f3f` |

전달 코드 파일은 Mac에서 생성한 archive의 내용을 옮긴 뒤 **14개 manifest 대상 파일 각각의 SHA-256을 검증**했다. 전송 후 ZIP 포장 메타데이터는 달라질 수 있으므로 위 채팅 ZIP hash와 Mac의 `portable-code.zip` hash를 같다고 주장하지 않는다. 포함된 코드·패치·요약 bytes는 일치한다. 원본 영상, 폰트, private Windows 자료는 전달 ZIP에 포함하지 않았다. 전체 native receipt는 실행 evidence를 위한 것이며 나중에 작성한 본 Markdown의 hash를 포함하지 않는다.

---

## 12. 근거 위치와 외부 자료의 한계

모든 repository 참조는 기준 HEAD `9f41d2f8a517da21f570f57ed1b4e2009a9d48db`를 뜻한다. 이 문서의 새 측정 수치는 실제 실행 JSON·JUnit·receipt에 연결되며, 웹 문헌에서 가져온 detector 성능 수치가 아니다.

| Source | 확인한 핵심 |
|---|---|
| `oil_supplemental_path.py`, `_phase_transition_profile`, `generate_phase_transition_candidates` | 각 band의 독립 pooling, sector availability, 응답·score 식 |
| `oil_shadow_observations.py:1546–1640` | `_narrow_context`, `_narrow_summary`의 signed/absolute profile와 pair 선택 |
| `oil_shadow_observations.py:1825–2010` | `_narrow_pulse_artifact`, `_scoped_plateau_collision_artifact`, `_semantic_hypothesis` |
| `oil_shadow_observations.py:2040–2084` | merged hypothesis 표현과 score 집계 경계 |
| `oil_candidate_evidence.py`, `oil_phase_identity.py` | evidence 의미와 phase 직접 승인·실패 이유 |
| `phase_candidate_assembler.py` | additive generator·enrichment·frame-local sidecar |
| `geometry_masks.py`, `preprocessing.py` | 원본 recipe mask와 original/normalized 입력 분리 |
| `tests/test_r16_refactor_characterization.py` | legacy hash와 reason version 경계 |
| `tests/test_foam_component_diagnostics.py`, `tests/unit/test_s11_foam_front_alternatives.py` | Foam 진단·front 대안의 보호 및 UTF-8 누락 |
| `tests/oil_observability_fixtures.py`, `tests/test_oil_observability_margin_regression.py` | 동일 관측의 다른 latent cause와 보호 ambiguity |
| `tests/diagnostics/s11_report_observability_replay.py`, `s11_observation_replay_audit.py` | application replay, provenance, 기존 nearest-time truth evaluator |

위 vision 소스의 공통 prefix는 `src/oil_tracker/adapters/vision/`이다. 행 범위는 기준 HEAD에서의 위치이며 patch를 적용한 테스트 파일의 행 번호와 혼용하지 않는다.

외부 1차 자료는 원리와 평가 방법을 확인하는 보조 자료로만 사용했다.

- **[W1] OpenCV 공식 CLAHE 설명** — 국소 histogram 재분배와 contrast limiting을 설명한다. original/normalized lineage를 분리할 근거이지, 특정 Y를 반사라고 라벨링할 근거가 아니다. 확인한 문서는 4.13.0이며 실제 실행 환경 4.14.0과 버전을 구분한다. https://docs.opencv.org/4.13.0/d5/daf/tutorial_py_histogram_equalization.html
- **[W2] scikit-learn 공식 Cross-validation** — test-set 반복 최적화, preprocessing leakage, time/group-dependent 분할의 문제를 설명한다. 촬영 lineage별 역할을 나누더라도 현재 노출된 sample이 untouched holdout으로 바뀌지는 않는다. https://scikit-learn.org/stable/modules/cross_validation.html
- **[W3] El-Yaniv & Wiener, JMLR 2010** — selective classification의 risk–coverage 관점을 참고했다. 이 detector가 해당 논문의 알고리즘이나 통계적 보장을 구현했다는 뜻은 아니다. https://jmlr.org/papers/v11/el-yaniv10a.html

확인일: 2026-10-07. 상용 하드웨어, 추가 센서, 조명 교체를 passive existing-video W4의 새로운 필수 조건으로 넣지 않는다.

---

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-PROPOSAL`, `OIL-HYPOTHESIS`, `OIL-CANDIDATE`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`, `CSV-PUBLICATION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R22/R22-2 owner·witness, W0–W4 target/aggregation/geometry/evaluation, closed region/color/paired-scale experiments, R23 polarity rejection, original/human ROI, mixed Foam/structure, reason repair, 1차 audit의 family demotion과 sampling/prefix 실험.
- Prior mechanisms rejected: same-sign/polarity만으로 identity 결정, pulse/texture opposition 단독 제거, source-family blacklist, private Y/frame 분기, exact-row Canny 강제, global cutoff 완화, 기존 review를 holdout으로 재포장, arbitrary scalar/carry/interpolation, truth/golden 수정으로 회귀 제거.
- Preserved contracts: same-frame numeric provenance, independent Oil/Foam, explicit missing/ambiguous states, bounded candidate/compute, initial/lifecycle safety, 기존 정답·recipe·원장 보존, 독립 Windows qualification.
- Difference from prior failures: 새 score를 바로 채택하지 않고, 같은 X 지지의 측정 반례·실제 후보의 exact ID 점수/좌표 lineage·단일 scorer의 full-sequence 및 application 결과를 함께 확인했다. 기존 동작 golden은 유지하면서 새 diagnostic reason을 먼저 검사한다.
- Logic-map impact: **NONE** — 운영 control flow·owner·authority는 변경하지 않았다. 별도 프로세스의 prototype은 현행 runtime owner로 등록하지 않는다.
- Failure-registry impact: **NONE** — 기존 실패군의 새로운 관측 근거이며, 새로운 field 성공이나 실패군 퇴역을 선언하지 않는다.

## Detector Governance

- Logic-map nodes: 실제 수정한 test contract는 `TRACE-PUBLICATION`; 계측/반증의 대상은 `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-HYPOTHESIS`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `CSV-PUBLICATION`이다. 나머지 노드는 §7의 보호 범위로 감사했다.
- Failure-registry entries: 모든 `S11-F01`~`S11-F10`을 검토했으며, 새 계측과 테스트 수리는 특히 `S11-F01`, `S11-F02`, `S11-F04`, `S11-F09`, `S11-F10`과 연결된다.
- First harmful stage: frame420 human ROI의 확인된 Y854는 생성·보존되어 있으나 `OIL-AUTHORITY`에서 boundary advantage를 충족하지 못한다. 이번에는 동일 hypothesis/candidate ID에서 pulse/plateau 기여와 실제 계측 좌표까지 추적했다. Y821의 물리 identity 및 private Windows 구간 전체의 first loss는 이 결과로 확정하지 않는다.
- Prior mechanisms reviewed: 현행 owner·실패 registry·첨부 1차 감사·reason repair·rejected pulse and family ablations.
- Prior mechanisms rejected: family/Y/polarity shortcut, 단독 artifact 할인, paired scorer의 검증 없는 채택, golden 변경·진단 필드 전역 무시.
- Preserved contracts: 기존 수치의 source binding, 원본 입력, typed uncertainty, 각 계열 독립성, lifecycle safety, 분리된 shadow/behavior/field gates.
- Difference from prior failures: 측정값이 다른 원인으로 생기는 반례와 실제 점수 항을 보존하고, 한 가지 실제 구현의 이익·손실을 모두 보고한다. 테스트 green과 detector effectiveness를 분리한다.
- Validation scope: isolated A0B targeted/canonical, 18 prototype tests, 16 frame/recipe post-hoc cases, 8 collision pairs의 full sequences, 121-row saved-sequence A/B, four-video fresh application A/B, source/input hash·governance 확인.
- Promotion decision: **제품 detector 승격 없음.** A0B test patch만 검증된 적용 후보다. A1 prototype의 전체 witness 통합·자원 계약과 A2 physical identity 개선은 아직 미완료다.
- Logic-map impact: **NONE** — main runtime 소유 경로 변경 없음.
- Failure-registry impact: **NONE** — 현행 실패를 덮어쓰거나 field PASS로 바꾸지 않음.
- Current disposition: **S11 ACTIVE / W4 OPEN / O2 미승격 / FIELD FAIL 유지 / W5·O3 이후 gated.**

---

**인계:** 먼저 실제 적용 HEAD에서 A0B patch를 review·반영한다. 이어서 기존 witness owner 안에서 upper/lower 공통 X, center/partner의 signed 계측, candidate scalar와 score 기여의 좌표·의존성만 lossless로 연결한다. 이번 paired scorer는 해법으로 복사하지 않는다. 기존 collision과 partial real-interface를 동시에 보호하는 identity readout의 예측 결과가 생긴 다음에만 O2 패킷을 만들며, main·Windows field의 합격 여부는 별도로 판정한다.
