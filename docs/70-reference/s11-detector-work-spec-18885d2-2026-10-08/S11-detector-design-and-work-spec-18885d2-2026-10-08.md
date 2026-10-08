# S11 Detector 개선 설계 및 작업 명세서

**기준 저장소:** `teeeeooo/oil_level_tracker`  
**감사 기준 HEAD:** `18885d226a7a7745bc2d062fd750ec263b9c78f6` (`main`)  
**기준 변경:** 2026-10-08, registered artifact reference 캡처·검토·recipe 보존 구현 이후  
**문서 성격:** 현재 코드·증거를 재검토한 후속 설계 제안. 구현 완료, detector 승격, Windows 합격 문서가 아니다.  
**상태 권한:** `docs/00-project/work-plan.md`가 유일한 현재 상태 소유자다. 이 문서의 상태 표는 위 HEAD의 감사 스냅샷이다.

---

## 1. 결론과 이번 작업의 범위

**전면 재설계나 임계값 완화보다, 후보의 실제 영상 근거와 구조물 근거를 구분하고 그 구분을 추적 대상 결정에 연결하는 국소 수정을 권고한다.** 당장 시작할 범위는 현재 D2의 registered-support 비교 계약이다. 다만 이것을 S11 전체의 새 장기 연구 과제로 확대하지 않는다. 한 번의 고정된 비교에서 실제 오추적 감소와 주요 계면 보존 가능성이 보이지 않으면 해당 가설을 종료한다.

이 판단의 이유는 단순하다. 현재 검출기는 경계를 전혀 만들지 못하는 경우뿐 아니라, **경계 후보가 있어도 잘못된 대상이 추적 이력을 차지하거나 phase gate가 실제 움직임을 가리는 경우**가 있다. 반대로 잘못된 후보를 하나 제거하는 것만으로도 나머지 후보 묶음과 추적 이력이 바뀌어, 이전에 추적하던 실제 계면을 놓칠 수 있다. 따라서 “아티팩트 1개를 없앴다”는 단일 프레임 성과를 detector 개선으로 판정하면 안 된다. [S01, S04, S05, S07]

### 이번 감사에서 실제 수행한 일

| 작업 | 이번 수행 결과 | 해석의 한계 |
|---|---|---|
| 현재 checkout·HEAD·작업 트리 확인 | `main @ 18885d2`, 시작 및 마지막 검사에서 tracked 변경 없음 | 원격 Windows runtime 확인은 아님 |
| 현행 상태·아키텍처·검증 계약·최근 원인 분석 검토 | 현재 owner와 구현을 대조함 | 역사 문서의 당시 pending 상태를 현재 지시로 사용하지 않음 |
| Mac sample 4종 영상 직접 확인 | 원본 영상을 순차 디코딩하여 42개 지정 프레임의 ROI를 시각 검토함 | 전체 영상을 프레임별 판독한 것은 아님. 새 human truth를 만들지 않음 |
| 저장된 sample4 비교 시퀀스 재실행 | 현재 `ObservationSequenceResolver`로 113개 × 2변형, **226개 complete detection 전체 동일** | 새 frame detector나 새 challenger 실행이 아님 |
| 관련 코드 검증 | 아래 명시한 8개 테스트 파일에서 **225 passed**, exit 0 | baseline 회귀·입력 계약 검증이지 새 검출력 검증이 아님 |
| 입력 보존 | 영상·recipe는 영상 확인 전후 동일. 시퀀스 검증의 230개 입력 pin 보존 | 과거 Windows 파일을 로컬에서 재해시한 것은 아님 |
| 저장소 검사 | `git diff --check`, detector governance 통과 | tracked 설계·코드 변경이 없는 상태의 검사 |

Windows는 기존에 사용자가 전달한 보고 및 그 정정 기록을 우선 근거로 사용했다. **Windows 원본 영상·전체 CSV·private ZIP은 읽거나 반출하지 않았고, Windows 재실행도 하지 않았다.** 이번 작업에서는 production source, 원본 recipe, truth, golden, Work Plan을 변경하지 않았다. [S01, S02, V01]

### 변경 대상으로 삼지 않는 것

Report source-context와 episode-source review는 이미 main에 채택되어 있다. 새로운 report UI, 또 다른 viewer, detector와 별개의 그래프 보정기를 만드는 일은 이번 개선의 중심이 아니다. 새 ML 모델 도입, detector 전체 교체, private Glass/시각/Y 분기, 결과 보간·carry도 제외한다. [S01, S07]

---

## 2. 현재 S11 상태와 문서 간 관계

| 항목 | 감사 HEAD에서의 상태 | 이번 명세서의 관계 |
|---|---|---|
| S11 | ACTIVE, Windows `FIELD FAIL` | 합격 상태를 변경하지 않음 |
| Accepted detector | R22 behavior + R22-3/O1 diagnostics | 비교 기준으로 유지 |
| O1 | locally ACCEPTED | 다시 구현하거나 추출 체계를 재설계하지 않음 |
| D1 / 기존 W3 readout | CLOSED, 정정 완료 | 73개 inventory를 재조사하지 않음 |
| W4 / D2 | OPEN, 참조 입력 캡처·검토는 구현됨 | 다음의 bounded diagnostic correspondence를 구체화 |
| O2 | OPEN, acceptance 미충족 | shadow·controls·holdout·Windows 계약 보존 |
| D4a / W5 / O3 | 별도 설계 및 진입 gate 필요 | support/association behavior의 후속 적용 범위 |
| D4b / W6 / O4 | 별도 phase/handoff gate 필요 | FULL/EMPTY 및 재진입 검증 후 진행 |
| D5 Foam | 독립 작업 | Oil 변경과 섞지 않고 별도 설계·ablation |
| D6 / W7 / O5 | 통합 후보 이후 | Windows 9개 구간의 최종 검증 |

기존 2026-10-08 next-work specification은 원문 보존된 상위 후속 계획이다. 이번 문서는 **18885d2까지 진행된 reference UI, 등록 후 sequence regression, D1 정정을 반영한 그 다음 설계**다. O/W/D 번호를 새 milestone으로 바꾸지 않는다. [S01, S03]

구현에 채택할 때에는 이 문서 전체를 또 하나의 live Work Plan으로 유지하지 않는다. 현재 상태는 Work Plan, durable input/behavior 계약은 Witness Architecture와 해당 phase/Foam owner, acceptance는 Witness Validation, 실행 결과는 evidence에 반영한다. 감사 원문은 날짜와 기준 HEAD를 유지한다.

---

## 3. 가장 중요한 확인 결과

### 3.1 Windows: gate를 푸는 것과 실제 계면을 식별하는 것은 다르다

D1 정정 후 W3 inventory는 **73개 = retained 45개 + retained 이전의 원인 미상 28개**다. 기록된 첫 경계는 `UNKNOWN_BEFORE_RETAINED_REFS` 28, `TRACKLET_NOT_ADMITTED` 28, `PHASE_HARD_GATE` 7, `OWNER_NOT_ALLOWED` 10이다. 별도의 passive 75개 inventory와 합치면 안 된다. [S02]

`review-001`은 0 not-selected / 11 tracklet rejection / 12 absent ref로 정정되었으며, admitted negative 7개라는 이전 설명은 폐기되었다. 반면 `review-002`에서는 실제 interface idx8/9와 non-interface idx20이 같은 row/tracklet admission을 통과하고 동일한 FULL hard gate에 막힌다. 이 반례 때문에 **gate 완화만으로 회복한 숫자를 실제 계면 회복으로 계산할 수 없다.** [S02]

현재 Windows 첫 물리적 오인 원인과 pre-retention 원인은 일부 미상이다. 미상은 미상으로 남긴다. 기록된 gate를 실제 계면의 최초 실패 원인으로 단정하거나, 후보별 null을 자동으로 false/zero로 바꾸지 않는다.

### 3.2 Sample4: 올바른 아티팩트 등록도 전체 추적을 악화시킬 수 있다

이미 검토된 44 s의 false candidate Y822를 기존 UI 방식으로 별도 recipe에 등록한 비교 결과는 다음과 같다. 원본 recipe에 적용된 변경이 아니다. [S04]

| 비교 단계 | 무등록 baseline | Y822 등록 | 판단 |
|---|---:|---:|---|
| 검토된 실제 target의 matcher eligibility | 7/7 | 7/7 | matcher에서 target을 보존했다고 downstream 성공이 보장되지 않음 |
| 검토된 non-target 중 template 제외 | 0/3 | 1/3 | 의도한 단일 오검출 억제 |
| Oil raw numeric 개수 | 101 | 105 | 숫자 증가를 개선으로 해석하면 잘못됨 |
| Oil-valid 개수 | 101 | 102 | validity와 물리적 정확도는 다름 |
| Foam raw numeric / valid | 26 / 26 | 26 / 23 | Oil 설정 변경의 타 series 결과도 비교 필요 |
| 정확한 기존 reviewed candidate 선택 | 4/7 | 1/7 | 임의 같은-row 대표에 truth를 옮기지 않은 결과 |

이번 감사에서도 동일한 저장 입력을 현재 sequence resolver에 통과시켜 아래 결과를 다시 재현했다. [V01]

| 시각 | baseline 선택 Oil Y | 등록 후 선택 Oil Y | 의미 |
|---|---:|---:|---|
| 44 s | 822 | 842 | false 제거. 새 842의 물리적/scalar 정답은 별도 문제 |
| 49.5 s | 836 | 880 | 기존에 선택하던 reviewed target을 상실 |
| 52 s | 833 | 862 | 다른 시점에서도 reviewed target을 상실 |

직접 확인한 원본 대비 이미지에서 49.5 s의 새 선은 아래쪽 rim 위치에 놓인다. 이 시각 해석은 assistant 판독이며, 정식 human pixel label을 추가하지 않는다. 이미 존재하는 target 대응만으로도 이 등록안을 개선으로 승격하지 않을 근거는 충분하다.

### 3.3 근본 문제는 “선택 점수 하나”가 아니라 후보 구성에 민감한 소유권 연쇄다

기존 저장 시퀀스 원인 분석에서 확인된 계산 경로는 다음과 같다. [S05]

| 시각 | 확인된 경로 | 금지되는 손쉬운 처방 |
|---|---|---|
| 39.5 s | 후보 제거 후 12 px span의 greedy row grouping이 바뀌어 두 established track이 경쟁 | 기존 그룹을 좌표로 고정하거나 제거된 false 후보 복구 |
| 41.5 s | established-first assignment가 가까운 provisional predecessor보다 먼 established predecessor를 우선 | 가까운 Y를 곧 물리적 동일성으로 간주 |
| 44.5 s | 각 owner에 명확한 child가 있어도, 덜 선호되는 중간 row의 merge 경쟁으로 두 owner 종료 | physical-proposal guard를 없애 continuation 강제 |
| 49.5 s | 실제 target은 admitted/publishable이나, committed lower owner에서의 전환이 금지되어 선택 불가 | selector score만 높이거나 owner 전환을 무제한 허용 |
| 52 s | target tracklet 자체가 미승인으로 publishable layer에 못 도달 | 모든 실패를 49.5 s와 같은 selector 문제로 처리 |

이미 실행된 guarded reciprocal probe는 synthetic guard와 기존 tracklet tests를 통과했지만 실제 226개 출력은 하나도 바꾸지 못했다. 해당 clear child들이 기존 physical-proposal witness를 갖지 않았기 때문이다. **그 guard를 제거해 결과를 만들거나 같은 실험을 다시 시작하지 않는다.** [S05]

이는 “모든 후속 알고리즘이 불가능하다”는 결론이 아니다. 물리적 관측과 후보별 support를 구분하지 않은 채 grouping/assignment만 바꾸면 동일한 실패를 되풀이할 가능성이 높다는 설계 근거다.

### 3.4 등록 reference는 유효한 추가 입력이지만 아직 판별기는 아니다

기존 spatial signature는 candidate Y 주변의 shared horizontal mask에서 양 끝 X와 band height를 남긴다. 실제로 **양 끝 두 점만 있는 support와 채워진 수평 support가 동일 signature 및 match score 1.0**을 낸다. whole connected component도 검토한 작은 구조물 밖의 다른 edge에 연결된다. 이 한계 때문에 새 reference 보존은 필요한 진전이다. [S06, C01]

최신 구현은 original/raw Canny/effective/glare/processed support와 provenance를 보존한다. 선택 영역에서 명시적으로 확인한 visible raw Canny만 reviewed support가 된다. 직사각형 전체를 구조물로 라벨링하지 않는다. 한 reference 최대 640×160 원본 픽셀, 1 MiB, Glass당 최대 16개이며, matcher는 아직 이 정보를 소비하지 않는다. [S03, C02, C03]

현재 저장된 UI demonstration은 `mixed_or_uncertain`이다. 이를 사용자가 확정한 `reviewed_support`로 바꾸어 실증 데이터로 사용하는 것은 금지한다. candidate 전체의 non-target 판단도 해당 band의 모든 edge pixel이 구조물이라는 뜻은 아니다.

### 3.5 Sample3와 Foam은 단일 아티팩트 문제 밖의 주요 과제다

기존 sample3 전 구간 분석에는 34.5345–81.014267 s의 46.479767 s adjacent-numeric interval과 92개 missing row가 있다. 이 중 87개 reason은 `FILLED_CAP_VETO`이고 89개에는 내부적으로 publishable row가 있다. **내부 publishability가 물리적 Oil 정답이라는 증거는 아니지만, proposal 개수 증가만으로 설명할 수 없는 episode-scale 누락**이다. [S07]

Foam에는 반대 방향의 두 문제가 동시에 확인되어 있다. sample4 C2는 material-region 수준에서 Foam으로 검토되었지만 bbox substrate 관계가 detached qualification을 막았다. 실제 같은-column gap은 별도 lower rim까지 22–29 px였다. 반면 16 s의 좁은 rim C1은 structural gate를 통과하고 더 높은 score로 공간 후보에 선택되었다. 이 fresh-frame 결과는 `persistence_pending`이므로 실제 false Foam publication으로 단정하지 않는다. [S08, S09]

따라서 Foam은 “substrate veto 제거”나 “가장 높은/매끄러운 edge 선택”이 아니라 **Foam 물질 영역, 실제 front, 구조물과의 관계를 분리하는 수정**이 필요하다. 중앙 원형 구조물 및 sample2 반사에 관한 기존 답변은 재질문하지 않는다.

---

## 4. 성공 기준: 프레임별 recall이 아닌 움직임 맥락

### 4.1 두 개의 결과 축을 분리한다

**제품 결과 축:** 기존 report만 보고 주요 상승·하강·반전·재등장·Foam 발생/소멸의 순서와 불확실성을 이해할 수 있는가? source-context와 source review는 이미 있는 보조 수단으로 사용한다.

**Detector 결과 축:** 실제로 선택된 same-frame 대상과 그 trajectory가 개선되었는가? 오래 지속되는 wrong owner, 가짜 extrema, 틀린 방향, 주요 episode 전체 누락이 감소했는가?

Report에서 원본을 볼 수 있다는 이유만으로 detector 실패를 성공으로 바꾸지 않는다. 반대로 frame-level 완전 검출이 안 되었다는 이유만으로 실제로 도움이 되는 episode 개선을 무가치하게 만들지도 않는다.

### 4.2 허용할 잔여 오차와 차단할 오류

| 종류 | 처리 원칙 |
|---|---|
| 짧은 missing/UNKNOWN, 일부 국소 위치 오차 | episode의 방향·순서·주요 변화를 바꾸지 않는다면 residual로 허용 가능 |
| 고립된 오검출 | 실제 주요 변화나 extrema로 오해하게 하지 않는지 report 수준에서 판정. 모든 1-frame 오류를 연구 재개 조건으로 만들지 않음 |
| 장시간 rim/reflection/residue owner | 주요 맥락을 왜곡하는 우선 수정 대상 |
| 진짜 급상승·급하강 전체 누락 | 짧은 시간이어도 중대 오류. 긴 구간 평균 coverage로 숨기지 않음 |
| Foam front와 Oil 계면의 교환 | 두 series의 의미가 바뀌므로 차단 대상 |
| FULL/EMPTY에서 만들어낸 좌표, 보간된 검출값 | 표현 품질 문제가 아니라 provenance 위반. 허용하지 않음 |

예를 들어 BASE rapid refill은 약 1.6 s의 사건이다. report의 2 s 표시 연결 범위를 detector의 보편적 “허용 missing 시간”으로 사용하면 이 사건 전체를 놓쳐도 통과하는 오류가 생긴다. [S10]

### 4.3 평가표에 반드시 남길 최소 항목

각 consequential episode마다 실제 sampling 범위, 관측/미관측 run, 검토로 확인된 wrong-target run, 변화 방향과 사건 순서, 주요 extrema의 실제 대상 여부, Oil/Foam 분리, phase/owner 전환, 남은 unknown을 기록한다. 정확한 Y truth가 없는 구간에서 RMSE나 pixel recall을 만들지 않는다.

`longest_missing_run`은 숫자가 없는 연속 구간이고, `longest_confirmed_wrong_run`은 실제 대상이 틀렸다고 검토된 연속 구간이다. 후자를 단순히 “Y가 낮음” 또는 기존 detector와 다름으로 계산하지 않는다. 확인되지 않은 run은 `unreviewed`로 별도 표시한다.

중요 사건은 기존 사용자 timeline과 이미 검토된 기록으로 선정한다. 임계값·budget·controls는 결과를 보기 전에 고정한다. 모든 synthetic invariant의 exact PASS와 자연영상 detector recall 100%는 서로 다른 요구다.


### 4.4 실제 추적 대상의 의미를 바꾸지 않는다

액화 냉매와 Oil 등의 여러 유체층이 보일 때 추적 대상은 기존 제품 정의의 실제 상단 유체 경계다. 화학적 유체 종류를 새로 분류하는 기능은 필요하지 않다. 그러나 이것을 모든 후보 중 minimum source Y를 고르는 규칙으로 구현하면 안 된다. Foam과 Oil이 함께 보이면 실제 Oil 계면과 별도 Foam front의 출력 의미를 유지한다. Foam 내부 틈이나 구조물을 Oil 비대상으로 판독했다는 사실만으로 그것이 Foam front 정답이 되는 것도 아니다. [S16]

---

## 5. 다음 설계: 검토된 구조물 support와 현재 후보 근거의 분리

### 5.1 범위와 가설

**가설 H-RS:** proposal의 위치 envelope 대신 검토된 구조물의 실제 reference support와 현재 후보의 원래 영상 근거를 구분하면, 구조물과 공유한 evidence를 독립적인 계면 근거로 잘못 세는 경우를 드러낼 수 있다. 그 결과가 충분히 구분 가능할 때만, 후속 authority/association에서 잘못된 대상의 지속을 줄일 수 있다.

이번 단계에서 검증할 것은 위 문장의 앞부분이다. **Reference와 닮음 = artifact, reference와 다름 = fluid라는 classifier는 제안하지 않는다.** 긍정적인 실제 계면 support와 full-window 개선은 후속 별도 입증 의무다. 하나의 등록 reference가 BASE/Accum 전체 실패를 해결한다고 가정하지 않는다.

이 가설의 추가 입력은 일반적인 edge strength나 smoothness가 아니라 **사용자가 출처와 범위를 명시해 검토한 구조물 support**다. 이전의 connectivity, contact/T-marker, ordered clearance, region/texture, motion-only 실험과 구별되는 부분이다. 단, 같은 reference와 현재 support가 관측상 구별 불가능한 overlap에서는 이 추가 입력만으로 물리적 정체성을 결정할 수 없다.

### 5.2 구현 책임

| 책임 | 기존 owner 및 적용 방식 |
|---|---|
| Reference 해석·무결성 | `domain/artifact_reference.py`, vision `artifact_reference.py`를 재사용 |
| 현재 후보의 measurement lineage | 실제 생성/측정 owner에서 frame-local sidecar로 전달. `FRAME-EVIDENCE`, `OIL-CANDIDATE` |
| 비교 진단 | vision 경계에 작은 pure diagnostic service. 기존 frame/debug 흐름에서 호출하며 별도 분석 pipeline을 만들지 않음 |
| 직렬화 | 기존 `PhaseDebugProjector` / JSONL debug 경로에 bounded sibling record |
| Shadow 평가 | 기존 W3 evaluator, frozen mapping 및 episode comparison 재사용 |
| 행동 소비 | O2 및 별도 O3 이후 `OilAdmissionEvidenceOwner`와 `OilTrackletOppositionOwner`에서만 검토 |

새 파일 이름은 구현 전에 기존 symbol 검색으로 중복을 확인한 뒤 정한다. setup UI에 또 다른 물리 classifier, tracker, preprocessing engine을 넣지 않는다.

### 5.3 입력 계약

비교 입력은 다음을 함께 가진다.

- **Reference binding:** snapshot digest, review state/rect, template/Glass/geometry identity, 원본 크기·crop origin, source frame/time, preprocessing identity, 원본 asset hashes.
- **Current binding:** source frame/time와 candidate original input index/source/kind/Y, recipe/geometry identity, 실제 사용된 현재 frame mask와 measurement provenance.
- **Support basis:** `observed_raw_edge`, `native_measurement_footprint`, `processed_support`, `centered_envelope`, `unavailable`를 구분한다. 원래 측정 footprint가 곧 physical contour는 아니다.
- **Availability:** reference 미검토, 현재 visibility/registration 미확인, mask/glare/crop로 관측 불가, 후보와 support의 정확한 binding 부재를 구분한다.

Shared horizontal-mask band에서 edge를 다시 골라 “그 후보의 실제 contour”라고 부르지 않는다. native sector center를 선으로 보간하거나 가까운 Canny peak를 붙여 missing support를 채우지 않는다. 실제 extractor가 support를 남기지 않는 candidate family는 이번 비교에서 `candidate_support_unavailable`일 수 있다. 이 수치를 성능 분모에서 숨기지 않는다.

### 5.4 고정 v1 진단 규칙

첫 v1은 새 artifact threshold를 학습·선택하지 않는다. 위치 이동이 확립되지 않은 다른 시각에 대해서는 **동일 source-coordinate상의 비교**라는 사실만 기록하며, 이를 cross-time 물리적 correspondence로 표현하지 않는다.

1. Hash/schema/geometry/preprocessing 및 review-state를 검증한다. `reviewed_support`가 아니면 새로운 의미의 reviewed-support 판단은 `NOT_EVALUATED`다. Legacy matcher는 그대로 동작한다.
2. 검토된 reference raw Canny 집합을 `R`, candidate의 실제 observed-edge 집합을 `C`, 양쪽에서 유효하게 관측 가능한 공통 domain을 `V`로 둔다. crop 원점만 정확하게 source 좌표로 변환한다. 값 추정이나 resize는 하지 않는다.
3. 실제 edge ownership이 있는 비교에서만 다음 raw 통계를 낸다: `shared = R∩C∩V`, `reference_only = (R−C)∩V`, `candidate_only = (C−R)∩V`, 그리고 mask/crop/glare로 비교할 수 없는 support. 분모가 0이면 ratio는 null이다.
4. 다른 support basis의 면적/footprint overlap은 별도 namespace에 기록한다. 이를 raw edge match 수에 합치지 않는다. 후보 밖의 reference context도 visibility를 검토하는 자료일 뿐 자동 반증/정답이 아니다.
5. Reference와 현재 edge가 공유되더라도 결과는 `support_overlap_observed`이지 `INTERNAL_OR_ARTIFACT`가 아니다. candidate-only support도 `new_support_observed`이지 `INTERFACE_SUPPORTED`가 아니다. 둘 다 존재하면 mixed relation을 보존한다.
6. 부분 관측, source binding 문제, occlusion 의심/미확인, 실제 fluid/structure 공존 가능성은 명시적으로 unresolved로 남긴다. Optical observability를 mask/glare 여부만으로 확정하지 않는다.
7. `physical_identity`, `product_target`, `path_localization`, `scalar_eligibility`는 별도 항목이며, 이 v1 raw comparison은 어느 항목에도 새로운 positive/negative authority를 주지 않는다.

이 exact-pixel v1은 경계가 1 px 이동하면 차이를 보인다. 그 차이는 구조물 소멸이나 fluid 발생을 뜻하지 않는다. **따라서 localization noise나 camera motion 때문에 통계가 유용하지 않으면 이 v1을 classifier로 밀어붙이지 않는다.** 필요하다면 어떤 추가 observable과 error budget이 필요한지 명시한 별도 개정으로 제한하고, 결과를 보고 tolerance/dilation을 여러 번 바꿔 맞추지 않는다.

### 5.5 Registration 재사용 경계

기존 `temporal_raster_evidence._translation`에는 성공 status와 raw response가 있다. 실패 시 반환되는 `(0, 0)`을 정지의 증거로 읽으면 안 된다. 이 source-backed 경계는 reference consumer에 반드시 반영한다. [C04]

기존 adjacent-frame registration이 성공했다는 사실만으로 수십 초 전 setup reference의 위치가 확립되지는 않는다. baseline v1은 장기간 shift 누적, 새 whole-frame ECC/optical-flow tracker, 무제한 reference 갱신을 추가하지 않는다. 임의의 reference-current pair를 정합하는 확장은 그 pair의 visibility·변환 범위·오차가 검증된 별도 계약이 필요하다.

### 5.6 실제 behavior로 이어질 때의 형태

O2 및 별도 O3 gate 이후의 behavior 후보는 다음 형태로 제한한다.

**A. 해당 후보가 실제로 사용한 증거를 추적한다.** 후보 envelope와 구조물 rectangle이 겹친다는 이유만으로 후보 전체를 지우지 않는다.

**B. 검증된 구조물과 공유한 support를 독립적인 fluid corroboration으로 중복 계산하지 않는다.** 공유되지 않은 증거가 남았다는 사실은 자동 anchor 자격이 아니다. 기존 authority owner가 그 증거의 의미와 품질을 평가한다.

**C. 물리적 모순이 확립된 범위에만 typed opposition을 전달한다.** Reference가 unavailable이면 새 메커니즘은 abstain하며, legacy fallback을 새 physical 판단으로 위장하지 않는다. legacy veto를 해제하거나 narrowed support로 재해석하는 변경도 별도 behavior ablation에 포함한다.

**D. mixed/overlap 후보의 rank나 ID를 diagnostic score만으로 보존·이전하지 않는다.** clear positive support와 competing artifact를 분리할 수 없는 경우에는 정직한 UNKNOWN이 정상 결과다. 다만 all-abstain은 detector 개선 성과가 아니다.

이 단계의 기대효과는 fixed structural support가 잘못된 owner를 만드는 경로를 줄이는 것이다. **투명 계면의 독립적인 positive evidence, 급격한 handoff, initial FULL release는 이것만으로 해결되지 않는다.** 해당 미충족을 다음 stage로 숨겨 넘기지 않는다.

### 5.7 캐시·재현성·버전에서 놓치면 안 되는 사항

현재 코드에서 `snapshot_sha256`은 snapshot JSON을 보호한다. `review_state`와 `review_rect`는 그 JSON 밖에 있다. 따라서 미래 비교 cache key는 snapshot hash만 사용하면 안 된다. 최소한 review state/rect, 현재 candidate/frame/support binding, geometry, preprocessing 및 comparator version을 함께 포함한다. 이것은 현재 UI 기능의 결함 판정이 아니라 **새 consumer에 필요한 계약**이다. [C02]

현재 `correspondence_status`의 `bound_reference`는 recipe context binding을 의미하며 현재 frame의 visibility/물리적 동일성을 보장하지 않는다. 저장된 preprocessing identity를 실제 consumer runtime과 대조하는 책임도 명시한다. [C02, C03]

현재 preflight는 참조 metadata를 behavior identity에서 제외한다. 아직 detector가 소비하지 않으므로 타당하다. **Behavior 소비를 시작하는 변경에서는 metadata digest와 algorithm version이 runtime behavior fingerprint에 들어가야 한다.** Cache invalidation, recipe compatibility, output provenance 검증을 같은 변경에 포함한다. [C05]

---

## 6. 반드시 먼저 고정할 controls와 중단 조건

| Control | 기대 진단/판단 | 근거 역할 |
|---|---|---|
| 검토된 isolated visible structure | binding 및 실제 support overlap을 재현. physical negative 판정은 별도 증거가 있어야 함 | mechanism positive control, fluid-positive와 구별 |
| 구조물에서 떨어진 genuine boundary | reference와의 비공유가 곧 fluid positive가 되지 않음. 기존 실제 target을 불필요하게 잃지 않음 | target preservation |
| 구조물과 교차하는 moving interface | 동일 픽셀을 공유하는 시점은 mixed/unresolved; 교차 전후 진짜 motion을 artifact로 삭제하지 않음 | 충돌 반례 |
| 구조물 위치에 정지한 interface | 정지 또는 template overlap만으로 negative 금지 | stationary collision |
| Foam·반사·crop·mask에 가려진 reference | unavailable/partial/uncertain; absence를 clearance로 바꾸지 않음 | observability control |
| 서로 다른 contour, 같은 envelope | shared-support 정보가 legacy signature의 충돌을 실제로 구분해 기록하는지 확인 | 표현력 계약 |
| 같은 관측 픽셀, 다른 물리적 해석 가능 | physical unresolved 유지 | 관측 한계 계약 |
| Mixed/disconnected support, native path 부재 | 전체 component 확장·nearest-edge 복구·source-family truth 이전 금지 | attribution control |
| Legacy, 변경된 ROI/settings/runtime, 잘못된 hash | 새 비교 unavailable 또는 explicit mismatch, 기존 recipe 동작 호환 | 무결성·migration |
| 후보 순서 변경·복제·무관 후보 제거 | 정확한 binding과 group/association 변화를 검사. 실제 모호성 변화는 따로 기록 | downstream stability |

Synthetic control은 좌표계·무결성·abstention 계약을 검증한다. 실제 영상의 물리적 분리 능력을 증명하지 않는다. 이미 노출된 Mac 영상과 Windows checkpoint를 새 holdout으로 부르지 않는다.

**필수 사전 확인:** 현재 sample4 UI demo는 reviewed-support positive가 아니므로, real reviewed-reference control이 준비되어 있는지 먼저 기존 입력을 확인한다. 준비되지 않았으면 사유를 `reviewed-reference-unavailable`로 기록하고 synthetic/metadata 검증까지만 진행한다. 자동으로 Windows 이미지 반출을 요청하거나 기존 질문을 반복하지 않는다. 새로운 물리 판단이 꼭 필요해진 경우에만 구체적인 한 장면과 한 판단을 사용자에게 제시한다.

---

## 7. 실행 작업 명세

새 milestone을 만들지 않고 기존 D2–D6에 다음 단위 작업을 배치한다. 아래 effort는 우선순위를 설명하는 상대적 제안이며 측정된 개발 일정은 아니다.

### D2-A. Reference–current support 진단 계약 구현

**즉시 가능한 작업:** 기존 reference reader와 실제 후보 lineage를 연결할 최소 schema, input validation, exact raw statistics와 null/abstention 상태를 구현한다. Real input readiness는 위 control 표로 한 번 확인한다.

**변경 책임:** `artifact_reference`, candidate 생성/lineage sidecar, 기존 debug projector. 기존 matcher, scoring, phase, selector, projection, report는 변경하지 않는다.

**산출물:** comparator version 및 frozen preflight, input manifest, per-candidate diagnostic record, synthetic/legacy/context-mismatch tests, debug ON/OFF 전체 detection equality와 bounded-resource receipt.

**완료 조건:** reference state/rect·mask·좌표계·basis를 구분하며, 동일 입력에서 동일 진단이 나온다. Missing support를 0 근거로 바꾸지 않는다. 새 정보가 production detector 출력에 영향을 주지 않는다.

**승격 조건 아님:** 이 완료는 O2 PASS나 artifact classifier 확보를 의미하지 않는다.

### D2-B / D3. 단 한 번의 고정된 shadow comparison과 go/no-go

**진입 조건:** input-bound reviewed structure/target/opposing/unresolved controls, exposure·partition role, 실행 범위와 자원 budget이 고정되어야 한다. 현재 없는 physical labels를 추정해 채우지 않는다.

**실행:** 기존 W3 평가와 저장된 전체 비교 시퀀스를 재사용한다. 비교 규칙이 physical discrimination으로 확장되는 경우는 §5의 진단과 별개로 additional observable, operation point, abstention rule을 먼저 제출한다. Threshold를 결과에 맞추어 조정하지 않는다.

**독립 집계:** wrong-target suppression, real-target retention/recovery, unresolved, unavailable, unreviewed predictions를 별도 집계한다. scalar 정확도와 physical identity도 분리한다.

**필수 회귀:** sample4 0–56 s 전체와 기존 7 target/3 negative binding, 특히 40/42/44 s pre-selector 손실 및 49.5/52 s target 상실을 포함한다. 나머지 세 sample의 overlay·mixed reflection·long-gap 위험도 검사한다. 7/7 최종 recall을 신규 제품 목표로 정한 것이 아니라 기존 증거의 손실을 숨기지 않기 위한 control이다.

**Go:** 구조물 관련 오류를 실제로 구분할 추가 evidence가 있고, 기존 주요 target/episode 보존 및 자원·provenance 방어가 충족된다. O2의 Windows/holdout acceptance는 별도로 충족해야 한다.

**No-go:** geometry만 구분됨, 전부 unresolved, newly supported 결과가 모두 unreviewed, known target보다 negative를 더 잘 admit함, 또는 단일 프레임 개선 대신 뒤 시퀀스가 악화됨. 해당 버전은 CLOSED WITHOUT PROMOTION으로 종료한다.

### D4a / O3. Support-aware authority·association behavior

**진입 조건:** O2 acceptance와 별도 O3 구현 승인. D2의 raw overlap ratio를 곧바로 production score로 쓰지 않는다.

**적용 순서:** actual support lineage → typed optical opposition/independent support → authority → row grouping/tracklet association. 기존 candidate 숫자만 늘리거나 false 후보 제거 후 살아남은 후보에 자동 승리를 주지 않는다.

**필수 owner tests:** candidate-set-dependent grouping, established/provisional competition, clear child와 nonpreferred merge edge, real crossing/split, competitor 제거 후 false-owner inheritance, same-frame member 대표 변경, source-family/physical-proposal distinction. 현재 guarded reciprocal probe를 guard 없이 재사용하지 않는다.

**완료 조건:** 개선된 physical correspondence를 근거로 잘못된 owner 지속이나 주요 target 누락이 줄고, fail-closed ambiguity와 exact projection이 유지된다. “baseline track ID 복원”이 아니라 실제 대상 보존이 목표다.

### D4b / O4. Phase release·reappearance·handoff

**진입 조건:** 해당 현재 후보가 실제 대상이라는 independent support와 O3 조건 충족. sample3 publishable row 수나 Windows hard-gated 후보 수만으로 진입하지 않는다.

**대상:** FULL에서 visible interface 재등장, initial EMPTY에서 실제 lower entry, partial fill 후 drain reversal, rapid refill 후 FULL closure, owner loss 후 bounded reacquisition.

**필수 반대 control:** 처음부터 FULL/EMPTY, static lower rim, residue/foam owner, upward/downward 반대 방향, 서로 경쟁하는 두 owner, old owner가 여전히 보이는 takeover, 새 owner가 아직 provisional인 경우.

**구현 원칙:** 새로운 qualified owner의 same-frame 관측으로만 handoff. ID·좌표·extrema를 복사하지 않으며, owner loss 후 무조건 OPEN으로 풀지 않는다. 기존 phase gate를 전체 삭제하지 않는다.

**완료 조건:** 주요 phase 변화가 실제 report에서 올바른 방향/순서로 전달된다. 짧고 비결정적인 잔여 missing은 별도 명시해 종료할 수 있다.

### D5. Foam material/front와 구조물 오인 개선 — 독립 변경

**설계는 별도로 준비하되 Oil behavior와 한 번에 섞지 않는다.** 동일 reference 기술을 쓰더라도 Foam acceptance가 자동 충족되지는 않는다.

`foam_front_detector`의 material-region 판정, front 후보의 실제 boundary support, structural association, `FoamEpisodeResolver`의 temporal confirmation을 분리한다. 가능하면 기존 retained component와 support geometry를 재사용하며, 이미 수행된 bbox 대 actual-column 비교를 다시 구현하지 않는다.

한 변경에서는 먼저 **부분 rim의 spatial false admission과 실제 Foam-region의 과도한 structural association**에 대한 구조물 근거를 검토한다. 단일 score ordering을 바꾸는 것보다 앞 단계다. Front scalar/episode 변경은 별도 ablation으로 분리한다.

보호할 controls: f450/f480의 human-confirmed rim, central circular structures가 섞인 C2, sample2의 Foam-region reflection, base의 relevant support absence, 기존 detached/warm/white/substrate/noisy/grid 구조물 synthetic tests. Whole C2 material 판단을 contour 정답으로 확대하지 않는다.

검증된 front가 있는 경우에만 같은 frame의 후보 Y를 출력한다. Component minimum Y, mask top, 중앙 구조물 사이를 잇는 보간선으로 새 scalar를 만들지 않는다. Oil가 UNKNOWN이어도 독립적으로 입증된 Foam은 기존 계약에 따라 유효할 수 있어야 한다. [S08, S09]

### D6 / O5. Windows 통합 field qualification

**진입 조건:** 로컬 control 및 owned behavior gate를 통과한 exact runtime 후보. 준비 전 반복적인 Windows 실행/수동 반출 작업을 요청하지 않는다.

기존 Windows 절차로 baseline/candidate를 구분해 실행하고, 다음 절의 9개 구간을 모두 평가한다. Windows 원본은 Windows에 남긴다. 현재 허용된 수동 text/report 전달 범위를 사용하며, private PNG/ZIP 업로드나 Mac pixel 접근을 필수로 만들지 않는다.

통합 결과에서 Oil/Foam/phase/provenance/resource 중 어느 축이 실패했는지 기록한다. Local PASS나 diagnostics-only acceptance를 FIELD PASS로 바꾸지 않는다.

---

## 8. Windows 9개 구간의 제품 수준 acceptance

아래 시간은 source-video 기준의 기존 human-reviewed approximate 경계다. Frame-exact truth로 바꾸지 않는다. [S10]

| Segment ID | 구간 | report가 전달해야 하는 맥락 | 중점 오류 |
|---|---|---|---|
| WS1-BASE-FULL-PREFIX | 480–약 550 s | 가득 찼고 visible 계면/Foam은 없음 | 구조물 선을 실제 Oil 계면처럼 지속 표시 |
| WS1-BASE-DRAIN | 약 550–662 s | 계면이 나타나 대체로 하강 | 주요 drain 전체 누락, lower reflection으로 owner 전환 |
| WS1-BASE-RAPID-REFILL | 662–약 663.6 s | 빠르게 상승해 상단에서 사라짐 | 급상승 삭제, 다른 row로 이어붙임 |
| WS1-BASE-FULL-SUFFIX | 약 663.6–780 s | 다시 FULL, visible 계면/Foam 없음 | refill 이후 false numeric 지속, 약 725 s reflection |
| WS1-ACCUM-EMPTY | 480–약 653 s | Oil/Foam 없음 | stationary lower structure의 입구 계면 오인 |
| WS1-ACCUM-ENTRY-SPLASH | 약 653–672 s | 실제 Oil 진입·상승, 아직 Foam 아님 | splash/residue를 Oil owner 또는 Foam으로 승격 |
| WS1-ACCUM-FOAM-LAYERED | 약 672–680 s | upper Foam과 lower Oil boundary가 분리됨 | 두 series 교환·동일 대상 중복 |
| WS1-ACCUM-POST-FOAM | 약 680–700 s | Foam은 사라지고 Oil 계면은 유지 | 잔류를 Foam episode로 지속, Oil owner 상실 |
| WS1-ACCUM-DRAIN | 약 700–780 s | 반전 후 Oil 계면 하강 | wall residue로 owner 고정, 주요 drain 누락 |

각 구간에 실제 sampled frame/time coverage, numeric/valid 수와 contiguous run, reviewed wrong/missing/unknown run, Y range·direction, phase/owner transition, `PASS / FAIL / NOT_EVALUATED`를 제시한다. Known false run인지 판독되지 않은 숫자는 “정답”이나 “오류”로 강제 분류하지 않는다.

최종 report의 독립 이해도 확인은 간단한 질문으로 진행한다. “언제 계면이 나타났나”, “어느 방향으로 움직였나”, “빠른 refill 뒤 어떤 상태인가”, “Foam은 언제 나타나 사라졌나”, “어느 부분은 판단할 수 없나”를 source truth와 대조한다. 평가자가 baseline/candidate 이름에 유도되지 않도록 동일한 report 조건을 사용한다. 성공 수치를 임의의 100% threshold로 정하지 않고 중요한 사건의 오류와 잔여 한계를 직접 판정한다.

---

## 9. 자원, compatibility, rollback

**자원:** 기존 reference 저장 cap과 candidate/tracklet/window bound를 유지한다. Reference decode는 유효한 cache identity당 재사용하고, frame별 PNG history를 추가하지 않는다. 비교 결과는 count/state/provenance 위주의 bounded record로 남긴다. 추가 latency p50/p95, peak RSS, debug bytes/frame과 총량을 동일 source/session에서 측정한다. 아직 실행하지 않은 비교의 비용을 “미미하다”고 가정하지 않는다.

**Compatibility:** legacy recipe의 serialization과 현재 matcher 결과는 diagnostic 단계에서 동일해야 한다. Corrupt/missing reference나 오래된 preprocessing context가 새 authority를 얻지 않아야 한다. GUI Apply/Cancel/undo는 이미 구현된 경로를 재사용한다.

**Behavior version:** diagnostic-only namespace와 behavior consumer version을 분리한다. 소비가 시작되면 참조 review metadata까지 behavior fingerprint에 포함한다. Existing golden을 새 결과로 덮어쓰지 않는다.

**Rollback:** diagnostic/authority/association/phase/Foam 변경을 논리적으로 나눠, 한 변경 단위만 되돌릴 수 있어야 한다. 원본 recipe와 reviewed mapping은 immutable 비교 기준으로 남긴다. 실험 recipe는 별도 파일이며 UI에서 채택한 것으로 오인하지 않도록 표시한다. 실패한 physical correspondence를 복구하기 위해 false predecessor를 원상 복원하는 것은 rollback 목표가 아니다.

---

## 10. 엣지 케이스에 매몰되지 않기 위한 실행 제한

D2-B의 첫 검토 단위는 **한 개 comparator version, 사전에 고정한 control matrix, 한 번의 frozen comparison**이다. Serialization·좌표 변환 등 명확한 구현 오류 수정은 재검증할 수 있지만, 같은 구조물에서 radius/coverage/score/sector 조건만 계속 바꾸는 것은 새 반복을 정당화하지 않는다.

다음 중 하나면 그 가설을 종료한다: physical positive와 opposing control의 분리 근거가 없을 때, 정보가 대부분 unavailable이라 실제 적용 대상이 없을 때, all-abstain만 만들 때, 단일 false suppression 대신 주요 target/episode를 잃을 때, UI·수동 라벨 부담이 제품 효용보다 커질 때.

종료 후에는 숫자 목표를 억지로 달성하지 않는다. 무엇이 불가능했는지가 아니라 **이번 rule/input으로 무엇을 입증하지 못했는지**를 남긴다. 새로운 가설은 새로운 observable과 영향을 받는 owner를 설명해야 한다. 현재 사용자 범위 밖인 ML, 새 촬영, 대규모 라벨링을 자동 다음 작업으로 넣지 않는다.

반대로 의미 있는 움직임이 전달되고 잔여 문제가 짧은 missing이나 드문 국소 오차라면, 해당 잔여를 명시하고 다음 제품 판단으로 진행한다. 완전한 모든 구조물 분류나 모든 픽셀의 정체성 설명을 S11 종료 조건으로 만들지 않는다.

**범위 경보:** sample4의 작은 semicircle 하나가 아니라 Windows BASE release/refill, Accum layer/drain, sample3 reappearance, Foam onset/disappearance가 우선적인 제품 사건이다. Sample4는 원인을 재현하기 좋은 regression control이지 전체 제품 목적의 대리 지표가 아니다.

---

## 11. 재현 및 실행 증거

### 11.1 이번에 통과한 테스트 명령

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_artifact_reference.py \
  tests/unit/test_artifact_calibration.py \
  tests/unit/test_artifact_proposal.py \
  tests/unit/test_oil_interface_tracklets.py \
  tests/unit/test_oil_observation_resolver.py \
  tests/unit/test_oil_phase_lifecycle.py \
  tests/unit/test_foam_episode_resolver.py \
  tests/gui/test_artifact_support_review.py
```

출력: `225 passed in 103.63s (0:01:43)`, process exit 0. 실행 Python 3.14.4 / OpenCV 4.14.0 / macOS 환경이다. 이 테스트는 전체 repository test suite의 재실행이나 Windows native GUI/packaging 검증이 아니다. 기존 intermittent A0Q를 해소한 것으로 선언하지 않는다.

### 11.2 새로 생성한 로컬 감사 디렉터리

```text
sample/output/s11-current-detector-work-spec-20261008-002/
  AUDIT-RESULT.md
  inspect_samples.py
  source-review-receipt.json
  base_sample_1-source-review.png
  sample2-source-review.png
  sample3-source-review.png
  sample4-source-review.png
  verify_saved_sequences.py
  sequence-verification-preflight.json
  sequence-verification-receipt.json
```

이 디렉터리는 실제 Mac checkout에 존재하며 ignored output이다. Source review는 base 9 / sample2 9 / sample3 12 / sample4 12, 총 42개 프레임이다. 각 sample의 recipe ROI를 그대로 사용했다. 원본 전체 재생이나 새 ground-truth annotation으로 표현하지 않는다.

시퀀스 재현은 저장된 raw detection을 읽고 현재 `ObservationSequenceResolver`를 호출했다. 기존 `AnalysisPipeline` 전체 재실행, 새 image detector, 새 registration consumer를 실행한 것이 아니다. preflight SHA-256은 `b67ea354dd83520042b364ada0d8a1e70914efbc0c016f822e3be76eb3cdcc68`이고 230개 입력 pin을 전후 검증했다.

공유 패키지에는 원본 영상, screenshot, Windows private asset을 포함하지 않는다. `verification-summary.json`은 실제 도구 출력과 receipt에서 옮긴 공유용 요약이며, 원본 native receipt 자체와 동일 파일이라고 주장하지 않는다. 재현 helper는 기존 자료를 읽기만 하며 별도 새 output에 결과를 쓴다.

### 11.3 이번 작업에서 확인하지 않은 것

새 detector 메커니즘의 physical efficacy, 실제 reviewed-reference를 사용하는 current-frame comparison, O2 holdout/Windows shadow PASS, O3/O4 behavior 후보, D5 Foam 개선, Windows 9개 구간 재실행, 독립적인 최종 report 이해도는 **이번 세션에서 검증되지 않았다**. 현재 main의 FIELD FAIL을 유지한다.

---

## 12. 근거 색인

모든 저장소 근거는 위 pinned HEAD 기준이다. 경로는 repo root에 대한 상대경로다. 아래 문서가 역사 기록인 경우 현재 상태가 아니라 해당 관측의 근거로 사용했다.

| ID | 경로 / 핵심 절 | 사용 범위 |
|---|---|---|
| S01 | `docs/00-project/work-plan.md` — Current gate, ledger, Next transition, authorization | 현재 단계·권한·종료된 실험·미해결 |
| S02 | `docs/60-evidence/s11/2026-10-08-next-work-intake.md` — D1 saved-record reconciliation, L266–373 | Windows 전달 기록 정정 45/28, gate와 owner |
| S03 | `docs/60-evidence/s11/2026-10-08-d2-reference-ui.md` | reference UI 구현·87개 당시 검증·demo 한계 |
| S04 | `docs/60-evidence/s11/2026-10-08-d2-recipe-artifact-comparison.md` | 153개 matcher 비교, 113×2 full pipeline의 역사 결과 |
| S05 | `docs/50-diagnostics/s11/2026-10-08-d2-registration-sequence-causality.md` | 39.5/41.5/44.5/49.5/52 s 원인 연쇄와 reciprocal no-op |
| S06 | `docs/60-evidence/s11/2026-10-08-d2-registered-support-design.md` | 46 signature 재현·support 충돌·component 확장 위험 |
| S07 | `docs/60-evidence/s11/2026-10-08-episode-source-review-validation.md` — Sample3 whole-episode detector audit | 46.479767 s gap, 92 missing, 87 FILLED_CAP_VETO; report 채택 |
| S08 | `docs/50-diagnostics/s11/2026-10-06-local-oil-foam-owner-audit.md` | Foam component attribution, bbox/column 관계, mixed support |
| S09 | `docs/60-evidence/s11/2026-10-06-foam-edge-selection-feasibility.md` — Frame480 orange C1 confirmed glass rim | partial rim admission, tentative front와 temporal/public 구별 |
| S10 | `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` | canonical 9개 구간, source identity 및 approximate truth 한계 |
| S11 | `docs/20-architecture/s11-interface-observability-witness-architecture.md` — Registered support reference, L1861–1960 | reference 의미·책임·새 behavior 경계 |
| S12 | `docs/30-validation/s11-interface-observability-witness-validation.md` — V3, V5, O2/O3/field gates | partition·shadow·promotion 계약 |
| S13 | `docs/20-architecture/s11-current-detector-logic-map.md` | 실제 frame/authority/tracklet/phase/selector/Foam 경로 |
| S14 | `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` | F02/F04/F05/F06/F07/F08/F09/F10 재발 방어 |
| S15 | `sample/README.md` 및 4개 `.oilrecipe` | 영상 역할·ROI·원본/provisional/human truth 구분 |
| S16 | `docs/rotary_oil_level_tracker_ssot_spec.md` — 다층 유체의 추적 대상, L1149–1165 | 실제 상단 유체 경계, 별도 Oil/Foam 의미 보존 |
| C01 | `src/oil_tracker/adapters/vision/artifact_calibration.py` | signature, threshold .72, 기존 matching/veto |
| C02 | `src/oil_tracker/domain/artifact_reference.py` | snapshot/review 분리, context binding |
| C03 | `src/oil_tracker/adapters/vision/artifact_reference.py` | bounded PNG capture/decode, reviewed raw-edge mask |
| C04 | `src/oil_tracker/adapters/vision/temporal_raster_evidence.py` — `_translation`, L448–496 | registration status 및 zero fallback 의미 |
| C05 | `src/oil_tracker/application/preflight.py` | reference-only metadata의 현행 behavior identity 제외 |
| V01 | 이번 공유 패키지의 `verification-summary.json`, native audit directory | 이번 세션의 42-frame 검토·226 equality·225 tests·입력 보존 |

---

## 13. History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `TRACE-PUBLICATION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R22/R22-3 current owners; D1 corrected funnel; closed paired/region/texture/contact/connectivity hypothesis records; registered Y822 comparison and downstream causal audit; guarded reciprocal attribution probe; Foam box/column support and rim-admission controls.
- Prior mechanisms rejected: geometry-only template veto as physical identity, nearest/strongest/smoothest/motion-only target selection, physical-proposal guard removal, restoration of a false owner, broad phase/shape/threshold relaxation, component-top scalar promotion, coordinate carry and report interpolation as a detector repair.
- Preserved contracts: one generic detector; separate physical identity/target/path/scalar truth; exact same-frame selected observations; independent Oil/Foam validity; coordinate-free FULL/EMPTY; bounded loss/ambiguity; immutable inputs/labels/goldens; Windows private-data boundary and existing promotion gates.
- Difference from prior failures: explicitly attributed reference support and current measurement lineage are distinguished before any authority or association consumer; support comparison remains diagnostic until a separately validated discriminator exists. Episode-level target preservation, not isolated rejection count, controls promotion. The investigation has an explicit one-cycle go/no-go instead of repeated descriptor tuning.
- Logic-map impact: NONE — this is a delivered proposal and read-only audit; current production owners and flow were not changed.
- Failure-registry impact: NONE — existing failure classes explain the audited mechanisms; no newly accepted physical repair or field result is asserted.

## 14. Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F04`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: registered sample4 at 49.5 s has a committed-owner selection barrier despite admitted/publishable target; at 52 s target loss is tracklet non-admission. Earlier grouping/assignment/merge changes are supported numerical antecedents, not a newly certified first physical cause. Windows pre-retention and first physical failure remain named unknowns. Foam has opposing spatial admission and association defects, with front truth still partial/mixed.
- Logic-map impact: NONE — current code was inspected and unchanged owners were exercised on stored inputs; no new detector behavior or current-state document was adopted.
- Failure-registry impact: NONE — recorded limitations and guards are preserved; local reproducibility and baseline tests do not establish Windows field improvement.
