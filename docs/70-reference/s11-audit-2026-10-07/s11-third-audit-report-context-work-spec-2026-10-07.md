# S11 3차 감사 및 작업 명세 — 검출률이 아니라 보고서의 움직임 맥락

> 감사일: 2026-10-07, Asia/Seoul  
> 저장소: `teeeeooo/oil_level_tracker`  
> 실제 기준 HEAD: `a48124c9e9479864c988f6054935d48f8cc4897d`  
> 선행 2차 감사 HEAD: `9f41d2f8a517da21f570f57ed1b4e2009a9d48db`  
> 현재 상태의 유일한 소유자: `docs/00-project/work-plan.md`  
> 성격: 기존 감사의 후속 실행·우선순위 조정 명세. 새 roadmap이나 병렬 상태 원장이 아니다.  
> 운영 상태: **S11 ACTIVE / W4 OPEN / O2 미승격 / FIELD FAIL 유지.** 본 감사는 main을 수정·커밋·push·merge하지 않았다.

## 0. 결론과 권고

**S11을 “모든 프레임의 계면을 맞히는 문제”로 계속 좁히지 말고, “보고서를 본 사용자가 주요 움직임을 이해하는 문제”로 다시 관리해야 한다.** 이는 새로운 제품 방향이 아니라 기존 제품 SSOT §1.2와 이번 사용자 요청에 이미 명시된 목적이다.

이번 감사에서는 실제 저장소와 네 sample을 확인하고, 보고서 수정안을 구현하여 원본과 비교했다. 또한 이전에 유리해 보였던 human ROI를 짧은 진단 구간이 아니라 sample4 전체 56초에 적용해 결과를 확인했다.

핵심 판단은 다음과 같다.

1. **바로 개선할 수 있는 지점은 detector 점수식만이 아니다.** 관련 없는 Foam 플래그가 Oil 최고·최저 표시를 제거하는 실제 결함, 46.48초 관측 공백 연결, 시작·끝 높이 유사성을 구간 전체의 정체로 표현하는 문구, Foam 관측 중단을 실제 소멸로 읽게 하는 문구를 확인했다. 보고서만 수정한 실험은 tracking 수치·상태·flags를 바꾸지 않았다.
2. **검출률·MAE가 좋아 보이는 수치만으로는 목적 달성을 판정할 수 없다.** human ROI에서 Foam 수치는 26→79개로 늘었지만 Oil은 101→59개로 줄고 마지막 Oil 관측이 32초가 됐다. 기존 Oil truth에 값이 반환된 지점도 4/5→2/5로 줄었다. 이 입력 변경을 성공으로 자동 채택하지 않는다. 반대로 적절한 보류일 가능성을 확인하지 않고 전부 검출 회귀라고 단정하지도 않는다.
3. **한 프레임의 실패를 전체 작업의 종료·재개 기준으로 삼지 않는다.** 이전 paired scorer가 frame420의 Y821을 해결하지 못했다는 사실은 유지한다. 다만 앞으로는 해당 실패 하나가 남았다는 이유만으로, 다른 주요 구간의 맥락 개선까지 무조건 기각해서는 안 된다. 주요 구간의 실제 이득과 새 오해를 함께 평가해야 한다.
4. **다음 detector 작업은 중요한 구간의 왜곡에 집중한다.** sample3의 긴 관측 불가 구간과 재관측 이후 하강, sample4의 후반 Oil/Foam 구분·전환, Foam 물질 존재와 front 위치의 분리가 우선이다. 관측 불가능한 구간을 숫자로 채우거나 smooth한 잘못된 선을 만드는 것은 개선이 아니다.

**권장 실행 순서:** 보고서 계약 수리 채택 검토 → 보고서·영상의 구간별 맥락 판정 → 필요한 A1 계측만 완료 → 가장 큰 맥락 왜곡 하나를 대상으로 A2 또는 A3의 단일 변경 검증. A1 전체가 끝나야만 독립적인 보고서 수리를 할 수 있는 것은 아니다. 반대로 보고서 수리로 W4/O2를 통과시킬 수도 없다.

---

## 1. 기준 확인과 2차 감사 이후의 변화

### 1.1 실제 접근

| 항목 | 확인 결과 |
|---|---|
| 로컬 저장소 | `/Users/sunjaekim/Developer/oil_level_tracker` 직접 접근 |
| 시작 local HEAD / remote main | 둘 다 `a48124c9e9479864c988f6054935d48f8cc4897d` |
| 시작 main 작업트리 | clean |
| 2차 감사 이후 production source | `git diff 9f41d2f8… a48124c… -- src` 차이 없음 |
| A0B | `fa2d6d536140fdb08c8b8c68ef369ce89dd49e35`에서 실제 채택됨 |
| A0B 채택 증거 | `docs/60-evidence/s11/2026-10-07-audit-adoption-checkpoint.md` |
| 실험 격리 | `/tmp/s11-third-context-a48124c`, 현재 HEAD의 detached worktree |
| 영구 실행 증거 | `sample/output/s11-third-audit-context-20261007-001` |
| private Windows 영상 | 직접 열람·실행하지 않음 |

첨부 2차 감사의 “A0B는 main 미반영”은 당시 사실이다. 현재 지시로 되풀이하지 않는다. 채택 기록의 2,326개 통과는 이전 실행 증거이며, 이번 실험의 새 검증과 구분한다. 이전 Qt 멈춤은 여전히 별도 미해결 안정성 항목이다.

첨부 ZIP의 SHA-256은 `1e8be03b59dae0291070ca0623b2f4e49a5542838b40b677f1149297bde18f3f`이고, 내부 manifest가 지정한 14개 payload 모두 일치했다. 첨부의 실험 코드나 원문은 수정하지 않았다.

### 1.2 이번 감사 범위

현재 Work Plan·roadmap·execution policy·제품 SSOT·보고서 architecture·S11 logic-map 전체 인덱스·F01~F10 failure 인덱스를 대조했다. 심층 코드 검토는 `RESULT-PRESENTATION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, 보고서와 domain event의 legacy Oil 판정, Oil/Foam 독립성 및 기존 Foam episode 계약에 집중했다.

네 원본 영상에서 **40개 source frame을 새로 디코딩하고 시각 검토**했다. 별도로 **4영상 × baseline/prototype의 8개 fresh application/report 실행**, 그리고 **sample4 human ROI 전체 구간 1개 실행**을 했다. 전자는 598개 출력 행, 후자는 113개 행으로 총 711개 application 출력 행이다. 같은 영상의 두 실행을 독립적인 현장 표본으로 세지 않는다.

2차 감사 이후 `src/`가 같으므로, 이전에 확인된 X support·signed pair·score lineage 문제는 유지되는 근거로 사용했다. 이번에 667개 함수의 모든 분기를 다시 수동 검증했다거나, 이전 377-candidate 계측을 새로 실행했다고 주장하지 않는다.

### 1.3 구분해야 하는 판단

- **관측 개수:** 해당 실행에서 숫자가 반환된 행 수이다. 검출 정확도나 recall이 아니다.
- **기존 scalar truth 비교:** 기존 evaluator의 nearest-time 비교이다. 값이 없는 지점을 MAE 분모에서 제외한 결과만으로 개선이라고 하지 않는다.
- **이번 시각 검토:** 주요 움직임·영상 상태·오해 가능성을 확인한 정성 검토이다. 새 정밀 Y 정답이나 독립 holdout이 아니다.
- **코드 계약 통과:** 값 보존·표시·검사 결과이다. 사용자의 맥락 이해 시험 또는 Windows 현장 합격을 대신하지 않는다.

---

## 2. 2차 감사에 대한 판단 — 보존할 근거와 바꿀 우선순위

| 2차 감사 내용 | 이번 판단 |
|---|---|
| A0B 테스트 계약 수리 필요 | 구현·채택까지 완료된 과거 작업이다. 반복하지 않는다. |
| upper/lower X support 불일치, same-sign pair 의미 손실 | 유효한 계측 결함·위험이다. 수정 후보의 원인을 설명하는 데 필요한 범위만 연결한다. |
| paired scorer 미승격 | 유지. 이번에 점수식을 다시 튜닝하지 않았다. |
| frame420 실패 지속 | 특정 operating point의 유효한 진단점이다. 프로젝트의 유일한 성공 기준은 아니다. |
| numeric count 또는 희소 MAE만으로 평가 금지 | 목적에 부합하므로 유지한다. |
| 기존 truth 한 지점의 값 소실/오차 증가를 항상 기각 기준으로 사용 | 개별 실험의 사전 보호 조건으로는 보존한다. 앞으로 모든 변경에 적용하는 절대 제품 목표로 확대하지 않는다. |
| 모든 후속 작업을 A1→A2에 직렬 종속 | detector authority 변경에는 기존 진입 조건을 지킨다. 독립적인 보고서 표시·문구 수리까지 묶을 이유는 없다. |
| Foam local-front와 Oil identity 분리 | 유지하며 중요도를 높인다. 두 선의 움직임을 이해하는 데 직접 영향을 준다. |

### 2.1 이전 paired scorer를 맥락 지표로 다시 읽은 결과

새로 scorer를 실행한 것이 아니라 **보존된 2차 감사 baseline/challenger CSV**를 동일한 시간축 지표로 다시 집계했다.

| 항목 | baseline | 이전 paired scorer |
|---|---:|---:|
| sample3 Oil 수치 | 29 | 27 |
| sample3 최대 내부 anchor 간 공백 | 46.480초 | 40.507초 |
| sample3 Foam 수치 | 5 | 5 |
| sample4 Oil / Foam 수치 | 101 / 26 | 101 / 26 |

따라서 “순수하게 아무 변화가 없었다”는 설명도 정확하지 않다. sample3의 최장 공백은 약 5.97초 짧아졌다. 하지만 이전 기록대로 다른 구간에서 새 관측과 보류가 교환됐고, 이 새 점들이 올바른 물리 계면인지·중요한 움직임을 더 잘 전달하는지는 판정되지 않았다. **이점이 확인되지 않았다는 미승격 판단은 유지하되, frame420 단일 실패만으로 모든 구간 효과를 지우지는 않는다.**

---

## 3. 실제 보고서에서 확인한 문제

### 3.1 Foam 플래그가 Oil 최고·최저를 사라지게 한다 — 확인된 코드 결함

현행 `report_presentation._is_r7_stream`은 Oil/Foam 구분 없이 하나라도 `R7_`로 시작하는 flag가 있으면 스트림 전체를 legacy R7 Oil로 취급한다. 그 상태에서는 `R7_OIL_ANCHOR`만 최고·최저 후보가 된다.

그러나 현재 Oil은 `R17_RESOLVED_OIL`, `SEQUENCE_RESOLVED_OIL`, `SEQUENCE_SAME_FRAME_CANDIDATE` 등의 flag로 출판되고, 같은 sample에 `R7_FOAM_UNCONFIRMED` 같은 Foam flag가 남을 수 있다. 그 결과 **Oil 숫자는 있는데 Oil anchor 집합이 비어서 최고·최저 landmark와 캡처가 제거된다.**

| 영상 | Oil 숫자 | Oil 수치 행 중 임의 `R7_` 존재 | `R7_OIL_ANCHOR` 행 | 원본 보고서 Oil extrema |
|---|---:|---:|---:|---:|
| Base | 28 | 0 | 0 | 2개 |
| sample2 | 4 | 1 | 0 | 0개 |
| sample3 | 29 | 6 | 0 | 0개 |
| sample4 | 101 | 23 | 0 | 0개 |

또한 움직임 문장은 `trusted or finite` fallback으로 최고·최저를 설명하는 반면, 그래프/capture는 빈 trusted 집합에서 끝난다. **같은 보고서 안에서 설명과 그림이 어긋나는 문제**다.

수정 실험은 legacy Oil을 나타내는 정확한 flag 세 개만 검사했다. 실제 legacy R7 Oil continuation을 anchor로 승격하지 않았고, Foam flag를 Oil 판정에 사용하지 않도록 했다. 이는 detector의 Oil authority gate를 완화한 변경이 아니다.

**중요한 후속 범위:** `domain/events.py`에도 같은 넓은 `R7_` 검사가 존재한다. 이번 보고서 patch는 domain events를 변경하지 않는다. 별도 saved-output 반사실 실험에서는 동일 299행을 유지한 채 이 predicate만 Oil 범위로 제한했을 때 sample2/3/4의 extrema 6개가 복구되고, sample4에서 crossing/recovery event 10개가 추가됐다. Foam event와 입력 sample은 그대로였다. 이 event들이 모두 물리적으로 올바르다는 뜻은 아니므로, event 변경은 별도 수리·검증 대상으로 남겼다.

### 3.2 46.48초의 공백이 하나의 움직임처럼 연결된다

`graph_series.observed_trajectory`는 원래 missing 구간 전후의 finite anchor를 모두 연결한다. 보고서는 이미 실선/점선 및 관측점 marker를 구분한다. **기존 코드가 중간 numeric sample을 생성했다거나, 단독 관측점을 숨겼다는 문제는 아니다.**

다만 elapsed-time 상한이 없다. sample3는 **34.5345–81.0143초**, 46.4798초 간격을 점선 하나로 연결한다. 그 사이 원본에서 영상의 광학적·물질적 상태가 크게 달라진다. 사용자가 점선의 완만한 상승을 실제 관찰된 상승 경로로 읽을 위험이 있다.

prototype은 기존 anchor를 모두 보존한 채, 앞뒤 관측점 간격이 2초를 초과하면 연결하지 않는다. sample3의 세 연결, sample4의 한 연결이 제거됐다. 짧은 공백 연결과 양끝 관측은 남는다.

**2초는 실험 전에 고정한 표시 정책 후보이지 검증된 물리 시정수나 detector threshold가 아니다.** 단지 선을 끊으면 정보 부족이 해결되는 것도 아니다. 긴 공백에는 관측 상태 설명과 제한된 원본 장면 확인이 함께 있어야 한다. 이 보완은 §7에 명시했다.

### 3.3 첫 관측과 마지막 관측이 비슷하다고 “유지”된 것은 아니다

기존 문장은 첫·마지막 높이 차이가 허용폭 이내이면 “비슷한 높이로 유지되었습니다”라고 쓴다. 중간에 하강 후 회복하거나 상승 후 복귀한 경우에도 이 첫 문장은 발생할 수 있다. 매번 작은 폭으로 움직이면 개별 인접 차분의 방향 검사도 큰 전체 변화를 놓칠 수 있다.

prototype은 **양끝 관측값 비교**라고 명시하고, 중간 범위가 큰 경우 전체 정체를 뜻하지 않는다고 덧붙였다. 단일 관측만 있는 경우에는 움직임을 판단하지 않는다. 기존 값의 평활화·삭제·보간은 하지 않았다.

이번 변경은 표현 모순을 줄였지만 **전체 구간을 상승→하강→회복으로 분할해 설명하는 알고리즘까지 구현한 것은 아니다.** 작은 방향 변화마다 새 event를 만드는 대신, 구간별 맥락 판정에 필요한 정도로만 후속 작업을 제한한다.

### 3.4 “Foam 경계가 더 이상 관측되지 않음”과 “Foam 소멸”은 다르다

현행 보고서는 다음 비관측 행을 `거품 소멸` landmark로 표현한다. 하지만 그 행은 실제 소멸뿐 아니라 front 불명확, 후보 거부, 가림, 관측 범위 변화일 수 있다.

sample4의 원본 보고서는 53.5초를 “거품 소멸”로 표시한다. 새로 확인한 54·56초 원본에는 여전히 밝고 기포성으로 보이는 영역이 있다. 이는 정밀 Foam truth를 새로 만든 근거가 아니라, **비관측 행만으로 물리적 소멸을 단정할 수 없다는 소스·영상상의 이유**다.

prototype의 표시 이름은 `거품 경계 관측 시작 / 관측 중단`이다. 중단 설명에는 마지막 관측과 다음 비관측 시각을 모두 쓰고 실제 소멸 여부·시점은 확정하지 않는다고 표시한다. domain EventType, stored timestamp 및 `events.csv`의 이벤트 의미는 바꾸지 않았다. 각 새 실행의 `run_id`는 별도로 생성된다.

---

## 4. 구현 및 검증한 보고서 prototype

### 4.1 변경 범위

| 파일 | 실제 변경 |
|---|---|
| `src/oil_tracker/application/services/graph_series.py` | 선택적 gap 상한, 기존 anchor 보존, 긴 timestamp 점프 분리 |
| `src/oil_tracker/adapters/reporting/graph_renderer.py` | static report Oil 연결에 2초 상한 적용 |
| `src/oil_tracker/application/services/report_presentation.py` | legacy Oil flag 범위, endpoint 문구, Foam 관측 문구 수정 |
| `tests/unit/test_report_context_contract.py` | 신규 17개 parameterized 검사 |
| `docs/20-architecture/s11-report-context-presentation-design.md` | 기존 report architecture의 S11 한정 제안·보호 경계 |
| `docs/catalog-by-created-date.md` | 제안 문서의 Git 미등록 상태와 작성일을 탐색 색인에 연결 |

보고서 prototype에는 detector source 변경, raw Y 변경, per-series validity 변경, 초기 상태 변경, 새 classifier, cutoff 변경이 없다. interactive Result Review와 domain event extractor는 이번 코드 patch 밖이다. 따라서 UI와 static report가 이미 동일한 새 gap 정책을 쓴다고 설명하지 않는다.

### 4.2 네 영상 fresh application/report A/B

원래 recipe, 2fps, 명시적 UNKNOWN 초기 상태, 기존 qualification window, 공식 `AnalysisPipeline` 및 `OutputBundleStore`를 사용했다. 영상·mode마다 새 프로세스로 실행했다.

| 영상 / 구간 | 행 수 | Oil: 원본 → prototype | Foam: 양쪽 | extrema: 원본 → prototype | capture: 원본 → prototype |
|---|---:|---:|---:|---:|---:|
| Base / 0–14.4초 | 30 | 28 → 28 | 0 | 2 → 2 | 3 → 3 |
| sample2 / 0–2초 | 5 | 4 → 4 | 0 | 0 → 2 | 1 → 3 |
| sample3 / 30.03–105초 | 151 | 29 → 29 | 5 | 0 → 2 | 5 → 7 |
| sample4 / 0–56초 | 113 | 101 → 101 | 26 | 0 → 2 | 3 → 5 |
| 합계 / mode | **299** | **162 → 162** | **31** | **2 → 8** | **12 → 18** |

`tracking_data.csv`는 실행별 `run_id`를 제외한 모든 열이 원본/prototype에서 같았다. `events.csv`는 `run_id`와 capture 경로를 제외한 이벤트 의미가 같았고, 실제 event tuple도 일치했다. 네 tracking fingerprint는 원본/prototype에서 정확히 같고, 2차 감사 baseline 값과도 일치했다. 기존 truth 13개 비교도 동일하다. report 생성 전후 tracking fingerprint를 다시 확인했으며 same-frame provenance 누락은 0이다.

| 영상 | baseline = prototype tracking SHA-256 |
|---|---|
| Base | `5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7` |
| sample2 | `85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976` |
| sample3 | `feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1` |
| sample4 | `e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1` |

실제 생성된 prototype 그래프도 직접 확인했다. sample3의 장기 공백 연결은 없어졌고 관측 최고·최저가 표시됐다. sample4도 extrema와 관측 중단 문구가 표시됐다.

**다만 복구된 최고·최저는 “저장된 detector 관측의 extrema”다. 실제 물리 계면의 최고·최저가 새로 검증된 것은 아니다.** 특히 sample4 후반의 급격한 Oil 변화가 잘못된 후보 전환이라면 그 extrema도 물리적으로 틀릴 수 있다. 이번 patch는 기존 관측과 원본 캡처를 함께 검토할 수 있게 만드는 수리이며, 잘못된 detector 값을 숨기는 수리가 아니다.

### 4.3 반례·회귀 검증

신규 검사는 Foam-only legacy namespace 3종, 실제 legacy Oil anchor 보호, U/역U/완만한 왕복의 endpoint 문구, empty/missing/singleton/flat 입력, Foam 비관측 문구, gap 상한 0/1/2/5/무제한의 anchor 불변성을 포함한다.

원본 source에 신규 검사만 적용한 반례 실행은 **13 failed / 4 passed**였다. 실패 13개 중 **8개는 기존 표시·문구 문제**, 5개는 새 `max_gap_sec` API가 없어서 발생한 TypeError이다. 13개 모두를 서로 다른 기존 제품 결함이라고 세지 않는다.

prototype의 관련 graph/report/capture/integration 집중 실행은 **36 passed**였다. 이 안에 신규 17개가 포함돼 있으므로 36과 17을 합산하지 않는다.

| canonical 선택 | 실제 결과 | 해석 |
|---|---:|---|
| 최초 `not qt_app` | **2,077 passed / 12 skipped** | detached worktree에 Git 비추적 MP4가 없어 기존 corpus 검사 12개를 실행하지 못함 |
| `qt_app` | **254 passed** | 이번 실행은 완료. 이전 Qt stall 원인 수리의 증거는 아님 |
| 원본 MP4 4개 연결 후 정확히 누락된 12개 재실행 | **12 passed** | 테스트 코드·skip 조건 변경 없이 입력 접근을 보완함 |
| 완료된 검사들의 고유 합집합 | **2,343 passed** | 기존 2,326개 전부 유지 + 새 17개. 실패 0, 남은 미실행 0 |

이는 **입력 누락 보완 후 완료된 선택들의 합집합**이지, 처음부터 단일 canonical 실행이 skip 없이 통과했다는 뜻이 아니다. 이전/이번 JUnit의 `(classname, name)` 집합을 비교해 기존 검사 누락 0개를 확인했다. 36개 집중 검사와 12개 재실행을 고유 총수에 중복 가산하지 않는다.

최초 비Qt 선택 약 720.56초, Qt 약 75.74초, corpus 보완 약 529.86초는 실행 supervisor가 기록한 wall time이다. 비Qt와 영상 replay 일부가 겹쳤으므로 이 시간으로 detector throughput 개선을 주장하지 않는다. 긴 계산 중 faulthandler가 출력한 stack은 로그에 보존됐고 해당 실행은 계속 진행해 종료됐다. 이번 검증에서 hard timeout이나 Qt stall은 발생하지 않았지만 **기존 Qt 안정성 이슈는 OPEN**이다.

최종 `check_detector_governance.py --base-ref a48124c… --include-worktree`, `git diff --check`, main에서의 `git apply --check`는 통과했다. 마지막 명령은 적용 가능성 검사만 수행했으며 patch를 main에 적용하지 않았다.

### 4.4 채택 판단

**보고서 계약 수리 후보로 검토할 근거가 있다.** 전 구간 관측 불변성과 새 반례 검사를 통과했고 실제 산출물의 기계적 결함을 해소했다. 그러나 사용자 이해도 시험, static report–UI 일관성, domain event compatibility 수리, private Windows qualification까지 완료한 것은 아니다.

2초 gap 정책은 채택 시 명시적으로 결정해야 한다. 최소 범위로 시작하려면 namespace·문구 수리를 먼저 분리하고, gap 정책은 표시 계약 및 사용자 검토를 거쳐 채택할 수 있다. 분리 적용된 patch는 그 실제 source identity에서 관련 검사를 다시 실행한다.

---

## 5. detector 입력 가설 검증: 기존 human ROI를 전체 구간에 적용

### 5.1 가설과 고정 조건

가설: “기존 human-reviewed ROI를 적용하면, 단일 frame의 위치 개선을 넘어 sample4 전체 Oil/Foam 맥락도 개선될 것이다.”

기존 `sample/output/s11-local-human-roi-comparison-001/sample4-human-roi.oilrecipe`의 ellipse만 복사했다. zero line, detector 설정, source 영상, 2fps, 0–56초, UNKNOWN 초기 상태는 그대로 두었다. 원본 recipe 파일은 수정하지 않았다. 신규 ROI를 이번 결과에 맞춰 재조정하지 않았다.

이전의 0–17초 또는 390–510 frame 진단과 달리, 공식 application 경로의 전체 56초 및 static artifact preparation 문맥을 사용한 **별도 입력 반사실 실험**이다. detector 코드 개선 실험과 혼용하지 않는다.

### 5.2 결과

| 지표 | 원래 ROI | 기존 human ROI |
|---|---:|---:|
| 전체 행 | 113 | 113 |
| Oil 수치 | 101 | 59 |
| Foam 수치 | 26 | 79 |
| 마지막 Oil 관측 | 56.0초 | 32.0초 |
| 이후 Oil 미관측 행 구간 | 없음 | 32.5–56.0초 |
| 기존 Oil truth 수치 반환 | 4/5 | 2/5 |
| 수치 반환 지점의 조건부 MAE | 7.625px | 2.000px |

MAE가 낮아졌다는 이유로 성공이라고 하지 않는다. 49·56초에는 값이 없어졌고, 남은 15·30초 비교 오차는 각각 원본 0.5/0.5px에서 1.5/2.5px가 됐다. **조건부 평균의 개선은 더 어려운 지점이 보류된 효과와 분리해야 한다.**

그렇다고 사라진 Oil 숫자 모두를 잘못된 보류라고 확정하는 것도 아니다. 기존 49초 값은 truth와 22px 차이가 있으므로 잘못된 수치를 보류한 것일 수 있다. 후반 Foam 증가와 Oil 미관측이 실제 물질·가림 전환을 더 잘 표현하는지, Foam front가 구조에 붙은 잘못된 선인지가 핵심이다.

### 5.3 판정

**전체 맥락의 개선이 입증되지 않아 자동 채택하지 않는다.** ROI 변경만으로 해결됐다는 가설은 지지되지 않았다. 단일 frame/짧은 구간의 좋은 결과를 전체 구간으로 일반화할 수 없다는 증거다.

후속 구현은 두 질문만 확인하면 된다. (1) 후반 Oil이 실제로 관측 불가해졌는가, 아니면 공개 가능한 계면이 계속 있는데 잃었는가? (2) 늘어난 Foam front가 실제 국소 경계를 따른 것인가, mixed component/구조의 상단을 따라간 것인가? 이것을 확인하기 위해 모든 frame의 정밀 pixel truth를 새로 만들 필요는 없다. 대표 구간과 필요한 source-frame/front support만 연결하면 된다.

---
## 6. 목적에 맞는 S11 평가 계약

### 6.1 1차 평가 단위는 frame이 아니라 의미 있는 구간이다

한 영상의 주요 구간마다 아래 질문에 답할 수 있어야 한다.

| 사용자 질문 | 확인할 보고서 근거 | 실패 예 |
|---|---|---|
| 대체로 상승·하강·정체 중 어떤 움직임인가? | 관측선의 방향, 구간별 요약, 원본 대표 장면 | 실제 하강을 상승으로 읽게 하는 잘못된 선 |
| 하강 후 회복했는가, 계속 낮아졌는가? | turning 구간과 이후 관측, 기준선 관계 | U자 변화를 “계속 유지”로 요약 |
| Foam은 언제 관측되고 어떻게 변했는가? | Foam 관측 시작/변화/중단 및 실제 scene | missing을 소멸로 단정, 구조를 지속 Foam으로 표시 |
| 어느 구간의 계면은 알 수 없는가? | 긴 공백의 명시, Oil/Foam별 관측 상태 | 46초를 측정된 완만한 경로처럼 연결 |
| 중요한 변화의 원본을 쉽게 확인할 수 있는가? | 관측 extrema/전환/긴 공백의 제한된 source capture | 누락된 landmark, 잘못된 시각·좌표의 캡처 |

숫자가 있는 모든 시점을 정답으로 세거나, 없는 모든 시점을 오류로 세지 않는다. FULL/EMPTY, 가림, material은 보이지만 front가 불명확한 경우는 그 상태를 정직하게 전달하는 것도 유효한 제품 출력이다. 다만 검증되지 않은 상태 이름으로 관측 실패를 감추지 않는다.

### 6.2 허용할 오차와 허용하지 않을 오해

**허용 가능한 후보:** 중요한 변화의 순서와 대략적인 크기가 유지되는 짧은 누락, 맥락을 바꾸지 않는 국소 위치 오차, 잘못된 숫자를 적절한 보류로 바꾸는 변경. 이런 변화가 있어도 주요 구간의 설명력이 좋아지면 채택 가능하다.

**우선 제거할 오류:** 긴 시간 다른 물리 경계를 따라가는 선, Oil/Foam 교환, 큰 하강·회복의 반전 또는 소실, 실제로 확인되지 않은 Foam 소멸/발생, 잘못된 단일 점이 주요 extrema로 강조되어 다른 이야기를 만드는 경우.

따라서 “사용자가 일부 오검지를 허용한다”는 말은 오검지 수를 무조건 무시하라는 뜻이 아니다. **그 오류가 그래프의 이야기와 의사 판단을 바꾸는가**가 우선이다. 반대로 모든 오차를 0으로 만드는 것이 완료 조건도 아니다.

### 6.3 보고할 지표

| 등급 | 지표 | 해석상의 제한 |
|---|---|---|
| Primary | 주요 구간별 방향·전환 순서의 영상–보고서 일치, 중대한 잘못된 해석 수 | 사람의 source 검토와 연결한다. 현재 네 영상은 노출된 개발 자료다. |
| Primary | 중요한 구간에서 Oil/Foam 관측 또는 명시적 관측 불가 상태가 전달되는가 | 임의 FULL/EMPTY/FOAM 상태를 만들어 성공으로 세지 않는다. |
| Primary | 잘못된 계면 고정·가짜 급변·가짜 종료가 지속되는 시간 | 단일 frame 개수가 아니라 지속성과 결과 해석 영향을 본다. |
| Secondary | 시간 구간별 numeric 분포, 최대 내부 공백, 시작/끝 미관측 구간 | 숫자 비율은 정확도·recall이 아니다. |
| Secondary | 기존 truth의 반환/보류 및 조건부 MAE, exact-frame 또는 nearest-time 구분 | 반환되지 않은 정답 지점을 별도로 표시한다. |
| Hard guard | same-frame provenance, 입력/정답 불변, Oil/Foam 독립, bounded compute | 제품 목표를 바꿔도 유지한다. |

시간창·중대 오해의 정의·판정할 주요 구간은 비교 전에 고정한다. “어떤 구간도 2초 이상 비면 실패” 같은 일률적인 detector 조건을 이번 표시 상한에서 파생하지 않는다. 필요한 시간 해상도는 실제 압축기 변화의 해석 과제에 맞춰 결정한다.

### 6.4 간단한 사용자 검토 절차

첫 검토에서는 candidate score나 MAE를 먼저 제시하지 않는다. baseline과 변경 보고서를 A/B로 제시하고, 각 주요 구간에 대해 §6.1 질문을 기록한 뒤 원본 영상을 확인한다. 같은 관측값의 보고서 변경이면 문구·표시 효과만, detector/ROI 변경이면 물리 관측과 보고서 효과를 함께 비교한다.

대규모 사용자 연구나 frame 전수 정밀 라벨링을 새로운 필수 조건으로 만들지 않는다. 처음에는 프로젝트 사용자와 검토자가 주요 구간의 일치/불일치/판단 불가 및 근거 frame을 기록하는 것으로 시작할 수 있다. 다만 이 검토를 실제 수행하기 전에 “사용자 이해도 향상 검증 완료”라고 쓰지 않는다.

static report의 `통과` 제목, unit-test PASS, local contract PASS, O2 shadow PASS, FIELD PASS는 서로 다른 의미다. sample4의 현재 보고서 제목이 `통과`라고 표시된다는 이유로 detector 정확성이 검증됐다고 읽어서는 안 된다.

---

## 7. 후속 작업 명세 — 기존 소유 경계 안에서 실행

다음 이름은 이 명세의 실행 묶음이며 **새로운 W/O 단계가 아니다.** 현재 Work Plan의 A0B/A0Q/A1–A4 상태를 복제하거나 자동 갱신하지 않는다.

### 7.1 최우선: RESULT-PRESENTATION 수리 채택 및 공백 설명

**목적:** 이미 저장된 관측을 더 정확히 전달한다. detector 수치 증가가 목표가 아니다.

**입력:** 본 보고서 patch, 현재 HEAD, 17개 새 검사, 4영상 A/B 결과, 기존 report architecture/validation.

**주 owner:** `report_presentation.py`, `graph_series.py`, `graph_renderer.py`; 캡처 확장 시 `image_capture_store.py`; static report 계약은 `result-observation-report-architecture.md`.

**작업:**

- namespace 및 endpoint/Foam 문구 수리를 검토·채택한다. 실제 legacy R7 Oil anchor 보호는 유지한다.
- gap 연결 상한을 표시 정책으로 확정하고 보고서에 밝힌다. source 시간 기준으로 검사하고, 출력 값이나 events의 의미를 바꾸지 않는다.
- 긴 공백을 단순한 빈 공간으로만 남기지 않는다. 가장 중요한 긴 공백 하나에 대해 기존 관측 전후와 필요시 중간 원본 장면을 제한적으로 보여 준다. **중간 장면에는 존재하지 않는 Oil 선을 그리지 않는다.** capture는 scene 확인용이며 synthetic sample/event가 아니다.
- Oil과 Foam의 관측 가능성을 별개로 설명한다. “Oil 미관측, Foam front 관측”과 “둘 다 판독 불가”를 섞지 않는다. material 존재는 기존 승인된 상태 또는 별도 검토 근거가 있을 때만 표시한다.
- interactive Result Review와의 정책 차이를 명시한다. 최종 공용화 시 두 surface의 동일 anchor·gap·event 이름을 함께 검사한다.

**완료 조건:** 실제 채택 source에서 관련 테스트 통과, 4영상 numeric/flags/validity/truth 불변, report extrema/capture 의미 일치, 긴 공백을 실제 운동으로 오해하지 않도록 표시, 새 숫자·backfill 0개. 아직 domain event 수리를 하지 않았다면 report-only derived landmark임을 유지한다.

**종료/제외:** 이 작업에서 새 detector family, classifier, pixel truth, Windows 영상 재수집을 요구하지 않는다. 보고서 수리를 A1 전부 완료 뒤로 미루지 않는다.

### 7.2 별도 좁은 수리: domain event의 legacy Oil compatibility

**문제:** `domain/events._is_r7_sample`의 넓은 `R7_` 검사는 extrema뿐 아니라 Oil appearance, zero crossing/recovery, drop event에도 영향을 준다. 보고서만 고치면 CSV/Review event와 narrative의 차이가 남는다.

**주 owner:** `src/oil_tracker/domain/events.py`, `tests/unit/test_events.py`, 결과 조립 및 event 소비자.

**작업:** report와 event consumer가 동일한 “legacy Oil” 의미를 사용하도록 책임을 한 곳에 정리한다. Foam-only 플래그를 Oil authority로 사용하지 않는다. 기존 legacy R7 anchor/continuation, 기존 debounce·drop·recovery 문턱은 유지한다.

**검증:** 기존 event unit/analysis/judgment/review 회귀, actual R7 stream과 현대 Oil+Foam flag의 양면 controls, 고정 299행 event A/B, source sample 불변을 검사한다. 이번 probe에서 추가된 sample4 event 10개가 보고서의 중요한 변화를 설명하는지 원본과 확인한다. 이벤트가 늘었다는 이유로 성공으로 세지 않는다.

**주의:** event 변경은 보고서-only 변경과 다르다. `events.csv`가 달라지는 것이 의도된 범위임을 별도 명시하고 영향·롤백을 제출한다. 이번 report-only canonical 결과로 이 변경까지 검증됐다고 주장하지 않는다.

### 7.3 A1 — 세 계측 결손을 유한하게 닫되, 질문을 먼저 정한다

2차 감사의 support/pair/scalar lineage 세 결손은 유지한다. 다만 새로운 descriptor를 계속 수집하는 독립 연구 과제가 되어서는 안 된다.

**입력 질문:** (1) 중요한 구간에서 올바른 후보가 생성되지 않는가? (2) 생성되지만 identity/authority에서 사라지는가? (3) Oil/Foam 구분 또는 front 위치 사용 가능성이 잘못 전달되는가?

**필요한 연결:** upper/lower 공통 X와 censoring, center/partner signed 값·source 좌표, proposal/broad/scalar 위치와 score 의존성. 기존 witness/diagnostic owner에만 연결한다. diagnostic scalar를 resolver 권한으로 사용하지 않는다.

**완료 조건:** 세 결손의 lossless 연결, 기존 synthetic 반례 및 실제 candidate ID 재현, 기존 출력 동등성, bounded resource 확인. 완료되면 A1을 닫고 예측 변경으로 이동한다. 같은 질문으로 Windows에 새 추출을 반복 요청하거나, 동일 영상에서 threshold sweep을 끝없이 하지 않는다.

**우선순위 조정:** 특정 isolated Y의 완전한 설명보다, 실제 주요 구간의 first-loss를 구분하는 데 필요한 연결을 먼저 사용한다. W0–W3의 완료 범위를 다시 미결로 돌리지 않는다.

### 7.4 A2 — 큰 Oil 맥락 왜곡 하나를 대상으로 단일 challenger

**주 owner:** 현재 candidate identity/authority owner 및 기존 W3 evaluator. selector나 report에서 누락 좌표를 생성하지 않는다.

**권장 첫 대상:** sample4 후반의 급격한 Oil 전환이 실제 경계 움직임인지 후보 교환인지, 또는 sample3의 재관측 이후 하강이 어떤 구간에서 잃어지는지 중 **맥락 영향이 더 큰 하나**를 먼저 고른다. frame420 하나가 유일한 endpoint가 되어서는 안 된다.

**설계 조건:** `physical identity`, `target role`, `scalar/contour usability`를 구분한다. support 위치와 공유 score 의존성을 고려하되 polarity, family 이름, 일정한 Y, smoothness만으로 Oil을 인증하지 않는다. 실제 같은-frame 후보의 연관을 도울 수는 있어도 앞 프레임 값을 carry하거나 새로운 경로를 만들어 관측으로 출판하지 않는다.

**평가 패킷:** 하나의 입력/feature 계약, 하나의 readout, 사전 operating point, 주요 구간의 예상 개선, 양면 controls, 노출된 회귀 영상과 holdout 구분을 고정한다. 전체 영상 report도 함께 생성한다.

**채택 기준:** 핵심 구간의 방향·순서·관측 가능성 전달이 실질적으로 좋아지고, 새로 지속되는 잘못된 선이나 중대한 거짓 event가 생기지 않으며 hard provenance guard를 통과해야 한다. 일부 위치 오차·짧은 누락이 남아도 이 조건을 충족하면 다음 검토로 진행할 수 있다. 반대로 모든 frame 수가 늘었더라도 잘못된 계면을 길게 따라가면 기각한다.

**유한 종료:** 고정 challenger가 개선 근거를 만들지 못하면 결과와 first-loss를 정리하고 닫는다. 종료된 paired scorer를 이름만 바꿔 다시 열거나, 같은 Y를 맞출 때까지 cutoff를 반복 조정하지 않는다. 이후 behavior 진입은 기존 O2/O3 계약의 실제 변경·승인을 통해 진행한다.

### 7.5 A3 — Foam의 존재와 usable front를 분리

**주 owner:** `foam_front_detector.py`, material identity, component diagnostics, Foam episode resolver의 각 기존 책임.

**입력:** 원래/human ROI 전체 sample4 결과, sample3의 물질·광학 상태 변화 구간, 기존 rim/structure/mixed-component controls.

**작업:** `component_contains_foam`과 `front_usable`을 별도로 표현한다. 실제 반환 front의 X별 support를 보존하고, 구조와 연결된 component 상단 극값을 자동으로 Foam front로 인증하지 않는다. material은 지지되지만 front가 불분명한 상태를 0 높이나 “소멸”로 바꾸지 않는다.

**검증 controls:** 실제 curved front, rim, 중앙 구조 연결, glare, no-Foam, detached/layer/droplet, 부분 support. 원래 ROI와 human ROI를 별도 입력 조건으로 검사한다. Foam front가 더 많이 반환됐다는 사실만으로 성공이라고 하지 않는다.

**채택 기준:** 주요 Foam 관측/변화 구간의 실제 맥락을 더 잘 보존하고, 잘못된 구조 front의 긴 지속을 줄여야 한다. Oil 값의 근접성이나 시간축 연속성만으로 Foam identity를 정답 처리하지 않는다. Oil 검출 성공을 Foam 출판의 필수 선행 조건으로 만들지 않는다.

### 7.6 A4 — 평가 및 현장 승격 패킷

기존 W3 evaluator를 재사용한다. 별도의 임의 “성공률” 계산기를 만들지 않는다. 여기에 §6의 구간별 맥락 판정을 같은 artifact로 붙인다.

패킷에는 source/input pin, 변경 코드 hash, 비교 window/sampling/초기 상태, 전체 prediction/보류 표, 주요 구간의 원본 근거, 잘못된 해석 사례, 자원 사용 및 재현 명령을 포함한다. 조건부 MAE, 관측 수, 사용자 맥락 검토를 서로 다른 열로 둔다.

O2 shadow, O3 behavior, lifecycle 및 통합 FIELD qualification은 현재 소유 계약에 따라 진행한다. **보고서-only 수리는 detector 미승격 상태에서도 별도 채택 가능하지만, S11 종료를 선언하는 근거는 아니다.**

A0Q의 Qt 수명/종료 문제는 별도 bounded 재현·원인 기반 수정이 필요하다. report/identity 개선을 위한 무제한 재실행 루프로 섞지 않는다.

---

## 8. 명세 간 관계와 우선순위 반영

| 문서 | 계속 유지되는 역할 | 이 명세의 영향 |
|---|---|---|
| `docs/rotary_oil_level_tracker_ssot_spec.md` | 제품 목적 | §1.2의 맥락·가독성 우선순위를 실제 평가·작업 순서에 적용 |
| `docs/00-project/work-plan.md` | 유일한 현재 상태와 다음 행동 | 채택 시 RESULT-PRESENTATION 작업과 detector A1–A4의 우선순위를 짧게 연결. 이번 감사가 직접 변경하지 않음 |
| `docs/00-project/roadmap.md` | milestone | S11 완료/field PASS로 변경하지 않음 |
| `result-observation-report-architecture.md` / 대응 validation | 보고서 책임·수용 계약 | namespace, endpoint, 관측 중단, gap·capture 계약의 정식 채택 owner |
| `s11-current-detector-logic-map.md` | 실제 runtime node/owner | 이번에는 동일 owner의 report-only 실험. detector flow 변경 없음 |
| witness architecture/validation | A1/O1/O2의 계측·shadow 계약 | 유지. report-only 작업의 불필요한 선행 blocker로 확대하지 않음 |
| failure registry F01~F10 | 과거 실패의 재발 방지 | F09/F10 및 cross-series coupling 교훈을 재사용. 어떤 실패도 퇴역 처리하지 않음 |
| 첨부 1·2차 감사 | 당시 고정 HEAD의 실행 증거와 제안 | 원문·기각 실험·당시 상태 보존. A0B의 현재 채택 상태와 구간 우선순위를 보완 |
| 본 3차 명세 | 이번 실행 결과와 후속 범위 | 병렬 원장이나 새로운 R 번호를 만들지 않음 |

정식 채택 때 이전 감사 문서를 고쳐 “처음부터 맥락 기준으로 검증됐다”고 만들지 않는다. 기존 검증 기준을 변경하려면 해당 validation owner에 새 적용 범위·구간 판정·hard guard를 명시한다. 지금까지의 FIELD FAIL과 미검증 사실은 그대로 남는다.

---

## 9. 적용·재실행·롤백

### 9.1 전달물과 전체 증거의 구분

채팅 Markdown은 실행 요약과 작업 명세다. 별도 code/evidence ZIP에는 검토용 report patch, 실제 테스트·재실행·집계 코드, 선별 JSON과 무결성 정보가 들어 있다. **전체 영상·40개 raw crop·전체 JUnit/log·9개 report bundle의 복사본은 아니다.** 원본 영상과 폰트, private Windows 자료는 전달 ZIP에 넣지 않는다.

Mac 전체 증거:

```text
/Users/sunjaekim/Developer/oil_level_tracker/sample/output/s11-third-audit-context-20261007-001
```

주요 하위 경로:

```text
visual-audit/context-metrics.json          # 이전 A/B 시간축 재집계 + 12 input pin + 40 frame 기록
visual-audit/*-contact-sheet.png           # 새 디코딩 원본 crop의 시각 검토판
replays/baseline/*/result.json             # current main의 fresh 실행
replays/prototype/*/result.json            # report-only 수정의 fresh 실행
replays/human-roi/sample4/result.json      # 별도 입력 반사실 실행
replays/*/*/oil_level_analysis_*/          # 실제 HTML/graph/capture/CSV bundle
report-focused.xml / .log                 # 36개 관련 검사
baseline-counterexamples.xml / .log       # 원본에 대한 반례 실행
canonical-*.xml / .log                    # 완료 선택 및 corpus 보완 결과
corpus-mount-recovery.json                # 격리 worktree MP4 누락 및 보완 기록
event-namespace-result.json               # 별도 domain event predicate 반사실
prototype-plan.json                      # 사전 report 실험 범위
delivery-summary.json                    # 선별 전달 요약; 전체 실행 원본과 구분
```

### 9.1.1 최종 무결성과 실행 환경

실행 증거 마감은 **2026-10-07 13:31:27 KST**다. 시작·마감 local HEAD와 remote main은 `a48124c9e9479864c988f6054935d48f8cc4897d`로 같다. main status는 clean이며, **추적 768개 파일의 SHA-256이 모두 시작값과 같고 원본 corpus 12개 pin 및 기존 human ROI 파일도 보존**됐다.

| 전달 대상 | SHA-256 |
|---|---|
| `report-context.patch` — 17,814 bytes | `a4b4682755c30255e40216f053ead9eac20d75f90a8c350a1590e9e9f34c8235` |
| `validation-summary.json` | `bbcbeb673210a8c2f8cd7c5e4d698c4a8a638464877eed20091171ee444ab558` |
| 채팅 code/evidence ZIP — 29,174 bytes | `bfa96bf51e7bb993501060a158e8480802358f7f3b34f2465921b2c0edc44901` |

Mac에서 생성한 payload를 채팅 실행 환경으로 옮긴 뒤 **manifest가 지정한 14개 파일의 bytes를 각각 hash 검증**했다. 채팅 ZIP은 동일 payload를 다시 포장한 것이므로 ZIP 메타데이터까지 Mac `portable-code-evidence.zip`과 같다고 주장하지 않는다. Markdown은 전달용 문서이며 위 native 실행 receipt에 그 이후 작성된 본문 hash가 포함된 것은 아니다.

실행 환경은 Python **3.14.4**, macOS **26.6.2 arm64**, OpenCV **4.14.0**, NumPy **2.5.1**, Matplotlib **3.11.1**, PySide6 **6.11.1**, pytest **9.1.1**이다. 격리 source는 실제 경로 `/private/tmp/s11-third-context-a48124c`이며 `/tmp/s11-third-context-a48124c`는 같은 위치다. 저장소 Python 환경을 사용한 Mac 실행 결과와 채팅 환경의 전송·문서 작성 작업을 구분한다.

### 9.2 검토 후 patch 적용

main에서 자동 적용하지 않았다. 다른 변경이 진행됐다면 현재 HEAD와 source diff부터 확인한다. 기존 수정이나 untracked 자료를 reset/clean하지 않는다.

```bash
# 현재 개발 checkout에서, patch 내용을 review한 후 실행
BASE=a48124c9e9479864c988f6054935d48f8cc4897d
git status --short
git diff "$BASE" -- src/oil_tracker/application/services/graph_series.py \
  src/oil_tracker/application/services/report_presentation.py \
  src/oil_tracker/adapters/reporting/graph_renderer.py

git apply --check /path/to/report-context.patch
git apply /path/to/report-context.patch

PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen \
  .venv/bin/python -m pytest \
  tests/unit/test_report_context_contract.py \
  tests/unit/test_graph_series.py tests/unit/test_graph_renderer.py \
  tests/unit/test_report_presentation.py tests/unit/test_image_capture_store.py \
  tests/integration/test_analysis_and_reporting.py -p no:cacheprovider

.venv/bin/python scripts/check_detector_governance.py \
  --base-ref "$BASE" --include-worktree
git diff --check
```

source code와 테스트가 적용됐다는 사실을 확인한 다음 relevant canonical 선택과 fixed replay를 수행한다. detached worktree에서는 git에 없는 sample MP4의 접근 여부를 사전에 확인한다. skip을 PASS로 세지 않는다.

### 9.3 application 비교 재실행

아래 경로에는 기존 파일이 없는 새 RUN을 사용한다. `run_context_replay.py`의 output 디렉터리는 이미 존재하면 실패하도록 되어 있다.

```bash
export OIL_REPO=/Users/sunjaekim/Developer/oil_level_tracker
export SOURCE=/path/to/reviewed-isolated-source
export PACKET=/path/to/extracted/code-evidence
export RUN=$(mktemp -d /tmp/s11-context-rerun-XXXXXX)

PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen \
  "$OIL_REPO/.venv/bin/python" "$PACKET/run_context_replay.py" \
  --root "$OIL_REPO" --source "$SOURCE" \
  --output "$RUN/sample3" --sample sample3 --mode prototype
```

Base, sample2, sample4도 동일 방식으로 각자 새 출력 디렉터리에서 실행한다. baseline은 변경되지 않은 exact source checkout을 지정한다. `--mode baseline` 문자열만 바꿔도 patched source가 원본으로 돌아가는 것은 아니다.

human ROI 재실행은 기존 검토 recipe가 있을 때 sample4에만 적용한다. 입력 변경 효과를 다시 보고, production recipe를 덮어쓰지 않는다.

### 9.4 롤백

report patch를 적용한 파일만 역적용한다. detector source나 원본 recipe/truth를 reset할 이유가 없다. legacy event 실험은 별도 프로세스 내 함수 대체였으므로 원래 source를 새 프로세스로 시작하면 원상태다. source event module에 남은 monkeypatch는 없다.

본 감사 worktree는 source review용이다. patch·코드·증거가 영구 경로에 보존된 뒤에만 해당 worktree의 유지/삭제를 결정한다. 다른 기존 worktree나 이전 audit evidence를 삭제하지 않는다.

---

## 10. 아직 해결하지 않은 것과 완료 경계

이번에 **구현·실행한 것**은 report-only 수리, 시간축 재평가, fresh application/report A/B, 전체구간 human ROI 반사실, domain event namespace의 별도 saved-output probe 및 관련 검사다.

다음은 완료됐다고 주장하지 않는다.

- Oil/Foam physical identity classifier 개선, A1 witness 통합 또는 A2/O2 승격;
- human ROI의 일반적 우수성 또는 늘어난 Foam front의 물리 정확성;
- 각 sample의 전 frame 정밀 정답, source 노출이 없는 holdout 평가;
- long-gap 문맥 capture의 정식 report 통합, interactive Review의 동일 정책 적용;
- domain event compatibility patch의 production 채택;
- 실제 사용자 이해도 검증, private Windows 재검증 또는 FIELD PASS;
- 이전 Qt stall의 원인 수리.

관측된 시행 문제도 보존했다. 원본 crop 수집 스크립트의 첫 실행은 append 경계의 개행 누락으로 SyntaxError가 났고 수정 후 정상 실행됐다. 최초 governance 실행은 companion 문서가 진단 폴더에 있어 설계 문서 요건을 만족하지 못했고, 실제 report 책임·불변성을 담은 S11 design 제안으로 분류한 뒤 통과했다. 첫 canonical 비Qt 선택에서는 worktree에 ignored MP4가 없어 12개 corpus 검사가 skip됐으며, 이를 숨기지 않고 입력 연결과 정확한 해당 검사 재실행으로 보완했다. 상세 판정은 §4.3과 receipt에 남긴다.

**핵심 종료 원칙:** 다음 회차에서 “한두 프레임이 아직 틀리므로 다시 모든 detector를 분석한다”로 돌아가지 않는다. 주요 구간의 그래프가 어떤 잘못된 이야기를 만드는지 먼저 정하고, 그 이야기를 바꾸는 가장 작은 작업을 실행·평가한다. 주요 움직임이 충분히 전달되고 hard guard가 지켜지면, 남은 국소 오차는 명시한 한계로 관리하며 다음 단계로 진행할 수 있다.

---

## 11. 근거와 재현 출처

| ID | 근거 | 사용 범위 |
|---|---|---|
| S1 | 첨부 `s11-second-audit-and-detector-work-spec-2026-10-07.md`, §3/6/8/11 | A0B 당시 상태, rejected scorer, 기존 A1–A4, evidence 구분 |
| S2 | current HEAD의 `docs/00-project/work-plan.md`, adoption checkpoint | 실제 현재 단계와 A0B 채택 |
| S3 | `docs/rotary_oil_level_tracker_ssot_spec.md` §1.2 및 report architecture | 움직임 맥락·보고서 책임 |
| S4 | `src/oil_tracker/application/services/report_presentation.py` | legacy Oil 판정, extrema, endpoint 요약, Foam episode 문구 |
| S5 | `graph_series.py`, `graph_renderer.py` | anchor/run/bridge 생성 및 실제 static graph |
| S6 | `src/oil_tracker/domain/events.py` | 별도 event consumer의 legacy Oil 범위 |
| E1 | `visual-audit/context-metrics.json` 및 raw crop/contact sheet | source-frame 확인, 기존 A/B 시간축 기술 통계 |
| E2 | `replays/*/*/result.json` 및 실제 bundle | fresh 9실행, 모든 CSV tracking 열/기존 truth/event 의미 비교 |
| E3 | `event-namespace-result.json` | 동일 299행에서 별도 predicate의 event 영향 |
| E4 | JUnit/log, source/input receipt, patch hash | 실제 검사·실행 정체성·보존 |
| W1 | Matplotlib 공식 `Plotting masked and NaN values` | missing point 제거와 masked/NaN gap 표시의 차이에 대한 보조 원리 |

W1 URL: `https://matplotlib.org/stable/gallery/lines_bars_and_markers/masked_demo.html`

외부 자료는 missing 표시에 대한 일반 원리만 뒷받침한다. 2초 gap cap의 최적성, 특정 frame의 Oil/Foam 정답, 이 프로젝트의 현장 성능을 입증하는 자료로 사용하지 않았다. 새 수치 결과의 근거는 repository source와 실제 실행 artifact다.

## History Review

- Logic-map nodes: `RESULT-PRESENTATION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `FOAM-CANDIDATE`, `FOAM-EPISODE`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`; F01~F10 인덱스와 current route를 대조했다.
- Prior mechanisms reviewed: R1 report/run/bridge 구분, R7 Oil anchor-only 보호와 Foam flag 공존, current R22 ownership, 두 첨부 감사의 lossless 계측 및 rejected paired scorer, 기존 original/human ROI 진단.
- Prior mechanisms rejected: scalar interpolation/carry, source-family blacklist, global cutoff 완화, 특정 Y/frame shortcut, numeric count/조건부 MAE만으로 승격, Foam 미관측을 실제 소멸로 인증.
- Preserved contracts: 원본 source/recipe/truth, same-frame selected candidate와 출판 좌표의 일치, Oil/Foam 독립, 명시적 보류, bounded 자원, 독립 field qualification.
- Difference from prior failures: 한 frame의 identity 완벽화 대신 실제 보고서의 해석 결함을 수리하고, 같은 관측값의 표시 A/B와 전체구간 입력 반사실을 분리했다. 2초 표시는 새로운 관측값이나 identity 권한을 만들지 않는다.
- Logic-map impact: NONE — 기존 RESULT-PRESENTATION owner 안의 격리 실험이며 main runtime flow를 바꾸지 않았다.
- Failure-registry impact: NONE — 기존 실패의 재발 방지 범위이며 현장 실패를 PASS로 바꾸지 않았다.

## Detector Governance

- Logic-map nodes: 변경한 runtime source는 `RESULT-PRESENTATION`; 별도 probe는 `PUBLICATION-PROVENANCE`의 domain event 소비 의미와 관련된다. detector identity source는 변경하지 않았다.
- Failure-registry entries: 실제 수리의 핵심은 `S11-F09`/`S11-F10`, 후속 과제는 cross-series coupling 및 local-front 관련 기존 실패군이다.
- First harmful stage: 이번에 입증한 보고서 결함의 최초 단계는 `RESULT-PRESENTATION`이다. human ROI 전체구간 Oil 손실의 최초 detector 단계와 증가한 Foam front의 물리 identity는 이번 scalar/report 실험만으로 확정하지 않는다.
- Promotion decision: report-only prototype은 채택 검토 후보. detector/O2/Windows 승격 없음. human ROI는 입력 실험으로 보관. event predicate는 별도 probe이며 report patch와 결합 채택하지 않음.
- Logic-map impact: NONE — 기존 owner와 provenance 경계 유지.
- Failure-registry impact: NONE — 새 field 성공 선언이나 기존 실패 퇴역 없음.

**최종 인계:** A0B를 다시 하지 않는다. 저장된 관측을 제대로 보여 주는 report 수리를 먼저 검토하고, 이후 source–report의 주요 구간 불일치를 기준으로 필요한 A1과 단일 A2/A3 작업을 진행한다. “검출률 100%” 대신 “사용자가 주요 움직임과 알 수 없는 구간을 이해할 수 있는가”를 종료 판단의 중심에 둔다.
