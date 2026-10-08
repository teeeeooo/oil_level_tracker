# S11 국소 X·Y 제외 기반 Detector 설계·작업 명세서

- 작성일: 2026-10-09
- 기준 저장소: `teeeeooo/oil_level_tracker`
- 확인한 HEAD: `167126e5f095e4011bc8f7dfd51049df87dd84f6`
- 문서 성격: 최신 상태 검토 + 실제 영상 재실행 결과 + 다음 구현 명세
- 상태: **설계 제안 / 실험 완료 / production 미적용 / 기존 FIELD FAIL 유지**
- 동반 결과: [실행 결과 요약 JSON](S11_Local_XY_Execution_Summary_2026-10-09.json)

## 1. 결정 요약

**다음 개발 대상은 ‘Oil 후보의 측정 영역에만 적용하는 국소 X·Y 제외’다. 기존 공유 `effective_mask`에 제외 영역을 추가하는 방식이나, 상·하부 평균을 전체적으로 paired-X 방식으로 교체하는 방식은 채택하지 않는다.**

이번 작업은 최신 문구를 재해석하는 데서 끝내지 않았다. 원본 영상을 읽어 기존 네 샘플의 기준 결과를 재현한 뒤, sample4의 0–56초 전체 구간에서 네 가지 추가 비교를 실행했다. 총 751개의 sampled result row를 실제 detector와 completed-window resolver에 통과시켰다. 결과는 다음과 같다.

1. **‘국소 X·Y 제외가 아직 시험되지 않았다’는 최신 커밋의 설명은 당시 상태에 대해 정확했다.** 기존 template rejection과 reference footprint 비교는 국소 픽셀 제외 재검출이 아니었다. 이번 실행에서 이 구분을 유지한 채 실제 제외를 시험했다.
2. **기존 공유 마스크를 이용한 국소 제외는 실사용 관점에서 실패했다.** 뒤쪽 Oil 관측이 41–56초 동안 끊겼고 Foam 관측도 크게 줄었다. 잘못된 한 후보를 없애는 대신 움직임의 뒷부분을 잃었다.
3. **제외를 Oil의 특정 후보 측정 경로로 한정하면 이 긴 단절은 발생하지 않았다.** 44초의 잘못된 Y822 출력은 Y842로 바뀌었고, 뒤쪽 움직임을 계속 표현했다. 다만 40초의 잘못된 선택, 42초 누락, 변경된 좌표의 정확성·물리적 대응은 해결되지 않았다. 따라서 개발 우선순위이지 채택 가능한 detector가 아니다.
4. **paired-X는 수치적 안전장치와 물리적 분류기를 구분해야 한다.** 합성 입력에서는 불균형한 측정 영역이 만드는 가짜 대비를 제거했지만, 실제 phase scanner에 전역 적용하면 마스크가 없어도 긴 누락이 발생했다. 기존 경로 전체의 평균 연산을 일괄 교체해서는 안 된다.
5. **대규모 detector 재설계, dense contour 재구현, 추가 ML 도입은 현재 증거로 정당화되지 않는다.** 우선 기존 후보 생성기를 유지하고 측정 범위·남은 지지·변경 영향 범위를 명확하게 만드는 제한된 구현을 진행한다.

제품 목적은 **report를 통해 계면과 Foam의 상승·하강·반전·소실·재출현을 이해하는 것**이다. 작은 누락을 모두 없애는 것이 아니라, 잘못된 경계가 주요 극값·급격한 이동·재충만·Foam 에피소드로 오해되는 일을 줄여야 한다. 이번 결과에서 수치 개수의 증가만으로 개선을 선언하지 않은 이유도 여기에 있다.

---

## 2. 최신 S11 상태와 이번 명세서의 위치

### 2.1 현재 상태

| 항목 | 확인한 상태 | 이번 작업에서의 처리 |
|---|---|---|
| S11 | ACTIVE | 종료·성공으로 변경하지 않음 |
| R22 및 O1 진단 | 기존 로컬 수용 상태 유지 | 기존 동작·진단 경로를 기준으로 사용 |
| D1 Windows 기록 대조 | CLOSED, 원인 미상 항목은 별도 유지 | 이미 닫힌 기록 확인을 반복하지 않음 |
| D2 reference measurement | 진단 구현 완료, 물리적 판단 승격 아님 | 측정 범위와 후보 전체 거부를 구분 |
| reference/appearance/temporal 비교 | 기존 제한된 가설은 미승격으로 종료 | 같은 겹침률·seed·threshold 탐색을 재개하지 않음 |
| 국소 X·Y sampling exclusion | HEAD에서 PROPOSED / NOT TESTED | 이번 별도 실험에서 실제 실행 |
| O2 / field qualification | 미완료 | 변경하지 않음 |
| report 실사용 개선 | 기존 개선 유지 | 이번 개발 우선순위에서 UI·report 개편 제외 |

상태 근거는 `docs/00-project/work-plan.md`와 2026-10-09 D2 evidence 문서다. 이번 산출물은 해당 문서들을 수정하거나 소급 변경하지 않는다. **저장소 HEAD에서의 ‘미시험’ 기록과, 이번 ignored output 디렉터리에서 완료한 실험은 서로 다른 시점의 사실이다.** [R01–R03, E01]

### 2.2 기존 명세·검증과의 관계

이 명세서는 다음을 대체하지 않는다.

- `s11-detector-change-governance.md`: 변경 통제와 기존 실패 방지 계약.
- `s11-current-detector-logic-map.md`: runtime owner와 current/sequence/public의 구분.
- `s11-interface-observability-witness-validation.md`: O2/O3, field 승격 및 기존 증거 사용 규칙.
- `windows-sample1-heating-coldstart-reviewed-truth.md`: Windows 영상의 물리적 구간 truth.

추가하는 것은 **최신 커밋에서 남겨 둔 국소 제외 분기의 실행 결과와, 그 결과에 근거한 다음 제한된 detector 구현 작업**이다. 40·42·44초 개별 Y에 맞춘 특별 처리나 기존 phase hard gate 우회는 허용하지 않는다.

---

## 3. 무엇을 시험했고, 무엇을 시험하지 않았는가

### 3.1 반드시 구별할 네 가지 연산

| 연산 | 실제 의미 | 이번 판단 |
|---|---|---|
| `apply_artifact_templates` | 공간 signature가 맞는 후보 전체를 거부 | 국소 측정 제외와 다름 |
| D2 reference overlap | 후보의 측정 footprint와 검토 범위의 겹침을 집계 | 픽셀 제거도 재검출도 아님 |
| 공유 ROI exclusion | 특정 X·Y 픽셀을 Oil·Foam 공용 `effective_mask`에서 제거 | 이번 A 실험에서 실행, 채택 거절 |
| Oil 측정 전용 exclusion | 기존 Oil 후보 생성기의 sampling aperture에서만 특정 X·Y를 제거 | 이번 B 실험에서 실행, 후속 개발 대상으로 유지 |

`MaterialPathEvidence.rows`는 현재 최대 다섯 개 sector의 선택된 Y다. 이것을 이미 존재하는 dense contour로 간주하거나, 일부 sector의 대응을 전체 경계의 물리적 truth로 확장해서는 안 된다. [R04–R07]

### 3.2 고정한 영역과 입력

```text
source-frame half-open rectangle:
    X = [563, 598)
    Y = [816, 828)

width × height = 35 × 12 = 420 pixels
sample4 ROI crop origin = (543, 798)
ROI size = 104 × 104 pixels
```

이 범위는 기존 reference 검토의 공간 범위를 재사용했다. 기존에 사람이 구조·무늬라고 검토한 것은 **125개의 eligible edge pixel**이다. 이번 420픽셀 제외는 이보다 넓은 **측정에서 빼는 정책**이지, 420픽셀 모두를 구조물로 분류한 새로운 truth가 아니다.

원본 이미지를 검게 칠하거나 0으로 치환하지 않았다. 기존 recipe와 truth는 변경하지 않았다. 공유 마스크 실험만 메모리상의 recipe 복사본에 `ExclusionZone`을 추가했고, 원본 파일은 보존했다. 이후 비교도 동일한 영역을 사용했으며, 결과를 보고 사각형을 확대하거나 검출 임계값을 바꾸지 않았다. [E01–E03]

### 3.3 실험 행렬

| 이름 | 변경 위치 | 유지한 부분 |
|---|---|---|
| 기준 | 원래 detector | 전체 |
| A: `local_xy_rectangle` | 기존 geometry exclusions → 공유 effective mask | 기존 생성·선택 알고리즘과 thresholds |
| B: `oil_measurement_only` | assembler의 material/raster-material path 및 phase-transition 후보 측정 mask | 공유 전처리, Foam, Oil hypothesis, 기타 후보 family, enrichment, authority·phase·selector |
| C: `oil_measurement_paired_phase` | B + phase scanner의 상·하부 평균을 complete-common-X 평균으로 변경 | 기존 최소 면적 기준과 나머지 결정 규칙 |
| D: `paired_phase_no_exclusion` | XY 제외 없이 C와 같은 paired phase 평균만 적용 | 원본 recipe 및 mask |

B는 ‘Oil 전체에서 구조물의 모든 영향을 제거한 detector’가 아니다. **세 후보 표현의 측정 영역을 바꾼 owner ablation**이다. C와 D의 paired 연산도 새로운 물리적 분류기가 아니라 고정한 수치 연산 비교다.

A 결과를 확인한 뒤 B/C의 owner 비교를 사전 고정했다. D는 paired 연산이 기존 ellipse/glare의 비대칭 support에도 영향을 준다는 점을 분리하기 위한 무마스크 대조다. 모두 이미 노출된 regression 데이터이며 독립 holdout이 아니다. [E01, E04, E05]

---

## 4. 실제 실행 결과

### 4.1 기준 재현

기존 qualification session을 사용했다. sampling은 2 FPS, initial state는 기존 재실행 도구가 사용하는 `UNKNOWN_REVIEW`다.

| 샘플 | 실행 구간 | sampled row | 이전 기준 fingerprint와 일치 |
|---|---:|---:|---|
| base_sample_1 | 0–14.4초 | 30 | 일치 |
| sample2 | 0–2초 | 5 | 일치 |
| sample3 | 30.03–105초 | 151 | 일치 |
| sample4 | 0–56초 | 113 | 일치 |
| 합계 | | **299** | 네 샘플 모두 일치 |

sample4의 기준 fingerprint는 `e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1`이다. 추가 네 비교의 452개 row를 합쳐 **751개 result row**를 재실행했다. 이는 751개의 독립적인 정답 frame이나 751개의 서로 다른 원본 frame을 의미하지 않는다. [E01, E06]

### 4.2 sample4 전체 구간 결과

아래 수치는 **raw 좌표가 null이 아닌 개수**다. valid coverage나 정확도가 아니다. 특히 B의 40초에는 Oil과 Foam 좌표가 남아 있어도 두 series의 validity가 false다.

| 구분 | Oil 수치 row | Foam 수치 row | public 값/상태 변경 row | 최장 Oil 비수치 연속 구간 |
|---|---:|---:|---:|---|
| 기준 | 101 | 26 | 0 | 50–51.5초, 4 samples |
| A: 공유 XY 제외 | 77 | 6 | 48 | **41–56초, 31 samples** |
| B: Oil 측정 XY 제외 | 105 | 26 | 31 | 0–1초, 3 samples |
| C: B + 전역 paired phase | 79 | 26 | 49 | **41–56초, 31 samples** |
| D: paired phase만 적용 | 78 | 26 | 50 | **40.5–56초, 32 samples** |

구간 길이는 첫·마지막 sample 시각을 표기했다. 예를 들어 41–56초는 endpoint span 15초, 2 FPS sample-support 환산은 15.5초다. 두 정의를 섞어 같은 ‘누락 시간’으로 보고하지 않는다. [E01, E06]

### 4.3 기존 검토 지점의 completed raw Y

Y는 source-frame 좌표이며 아래쪽으로 증가한다. ‘기존 검토 대상 Y’는 사용자가 해당 후보의 대응을 확인한 좌표이지 새 detector의 픽셀 오차 허용범위가 아니다.

| 시각 | 기존 검토 대상 Y | 기준 completed Y | A: 공유 제외 | B: Oil 측정 제외 | C / D |
|---:|---:|---:|---:|---:|---:|
| 38초 | 844 | 844 | 844 | 844 | 844 |
| 40초 | 841 | 865.5, 잘못된 대상 | 830 | 830 | 831 |
| 42초 | 839 | 868, 잘못된 대상 | 없음 | 없음 | 없음 |
| 42.5초 | 835 | 835 | 없음 | 840 | 없음 |
| 44초 | 844 | 822, 잘못된 대상 | 없음 | 842 | 없음 |
| 49.5초 | 836 | 836 | 없음 | 835 | 없음 |
| 52초 | 833 | 833 | 없음 | 830 | 없음 |

B는 44초의 기존 잘못된 Y822를 선택하지 않으면서 뒤쪽 경계를 계속 산출한다. 따라서 단순 공통 마스크보다 다음 개발의 출발점으로 적합하다. 그러나 Y842·835·830을 기존 검토 좌표와 가깝다는 이유만으로 정답으로 계산하지 않았다. 40초는 검토 대상과 다른 출력을 내고, 42초는 검토상 계면이 있는데도 수치가 없다. **B를 ‘검출률 개선 성공’ 또는 7개 중 몇 개 성공으로 환산하지 않는다.** [R08, E01, E06]

### 4.4 report 맥락에 미친 영향

기준과 A는 실제 `OutputBundleStore`의 HTML·CSV·그래프까지 생성했고 그래프를 직접 확인했다. 나머지 세 비교는 completed data와 report presentation을 생성하고 별도의 비교 그래프로 확인했다. B/C/D에 대해 실제 HTML을 전부 렌더링·검수했다고 주장하지 않는다.

기준 report에서는 이미 잘못된 대상으로 검토된 42초와 44초의 관측이 주요 최저·최고 유면 지점으로 표현된다. 이는 단순한 한 frame 오차보다 제품 목적에 중요하다. 사용자가 report에서 급격한 하강·상승을 읽을 수 있기 때문이다. A는 그 뒤쪽 움직임을 대부분 잃어버렸고 Foam도 여러 짧은 관측으로 분절됐다. ‘틀린 후보를 지웠다’만으로 이를 개선이라고 평가할 수 없다.

B의 장점은 뒤쪽 움직임이 유지된다는 것이다. 그렇지만 comparison chart의 raw 좌표와 report에서 유효하게 취급할 관측은 구분해야 한다. 40초에는 다음 변화가 기록됐다.

```text
기준: Oil Y865.5 / Foam Y840 / distinct_lower_oil
B:    Oil Y830   / Foam Y840 / inverted_topology
      oil_is_valid = false
      foam_is_valid = false
      R7/R8_FOAM_OIL_TOPOLOGY_CONFLICT
```

B의 current Foam 관련 metrics와 current Foam 좌표는 113개 row 모두 기준과 같았다. 그런데 final validity는 40초에서 달라졌다. **Foam 검출 입력이 그대로라는 것과, 최종 Foam 관측이 그대로라는 것은 다르다.** 새 Oil 선택이 composition에서 어떤 결과를 만드는지도 반드시 평가해야 한다. 여기서 topology veto를 해제해 숫자를 살리는 것은 이번 개선 범위가 아니다. [E06]

### 4.5 긴 단절의 위치

A/C/D에서 42·42.5·44·49.5·52초의 completed phase는 `filled_barrier / FILLED_CAP_VETO`로 기록됐다. B에서는 이 지점들이 `open` 상태로 남았다. 이는 변경이 단일 후보 점수에 그치지 않고 completed phase 경로까지 파급되었다는 실행 증거다.

다만 이 상태표만으로 ‘최초 물리적 오판의 원인이 정확히 어느 픽셀/조건인가’까지 확정하지 않는다. mask → 후보 변화 → track/phase 변화의 중간 원인과 final hard gate를 구분한다. 해결책은 hard gate를 제거하는 것이 아니라, 먼저 변경된 후보와 지지의 의미를 바로잡는 것이다.

---

## 5. 수치·기하 계약에서 확인한 문제

### 5.1 국소성은 이미 구현할 수 있다

기존 `geometry_masks.build_mask_bundle`의 직사각형 제외는 source 좌표를 crop으로 변환해 `effective_mask`만 변경한다. 실험에서는 f1320에서 정확히 420개의 기존 유효 픽셀이 제외됐고, 범위 밖 mask는 동일했다. 같은 X 구간의 **source Y844**도 원래대로 사용할 수 있었다.

따라서 ‘특정 X 열을 영상 전체 높이에서 버려야 한다’는 전제는 잘못이다. 문제는 XY를 표현할 수 있는지가 아니라 **어느 측정 owner에 적용하고 어떤 부작용을 허용할지**다. [R05, E03]

### 5.2 상·하부가 서로 다른 X를 보면 가짜 대비가 생길 수 있다

현재 phase scanner는 상부와 하부의 유효 픽셀을 각각 평균한다.

```text
contrast = mean(lower[lower_valid]) - mean(upper[upper_valid])
```

세로 방향으로는 변화가 없고 가로 방향으로만 밝기가 증가하는 합성 입력에서, 상부의 왼쪽 일부만 빼면 기존 연산의 대비가 **−24**가 됐다. 동일한 완전 공통 X에서 양쪽을 비교하면 **0**, 실제 40단계 밝기 변화가 있는 양성 대조에서는 **40**을 유지했다.

이는 mask가 새로운 경계를 만들어서는 안 된다는 수치 계약을 뒷받침한다. 그러나 C/D의 영상 결과는 ‘complete-common-X를 모든 기존 평균에 적용하면 좋아진다’는 주장을 반박한다. 기존 glare·ellipse의 비대칭 support까지 한꺼번에 재해석했기 때문이다.

**후속 설계는 제외와 실제로 교차하는 측정 footprint에만 필요한 안전 처리를 적용해야 한다. 제외와 교차하지 않는 연산은 기존 결과를 정확히 보존한다. 이 국소화된 안전 처리 자체는 아직 실영상으로 시험하지 않았다.** [E03–E05]

### 5.3 sampling exclusion은 모든 픽셀 의존성 제거가 아니다

전처리는 gray → CLAHE → Gaussian 5×5 → Sobel 3×3 → Canny → horizontal closing 순서로 진행한다. 일부 mask는 그 뒤에 적용된다. 따라서 제외 영역의 픽셀을 평균에 직접 넣지 않더라도 주변의 blurred/Sobel/Canny 결과에 그 픽셀이 영향을 줄 수 있다.

고정한 합성 대조에서 제외 영역 내부의 원본만 바꾸었을 때, 제외 영역 밖의 변경 수는 다음과 같았다.

| 표현 | 영역 밖 변경 원소 수 |
|---|---:|
| gray | 0 |
| normalized | 0 |
| blurred | 124 |
| Sobel absolute | 184 |
| Canny | 16 |
| horizontal mask | 14 |

이는 한 합성 입력에서의 결과이며 모든 영상·CLAHE 상황에 대한 보편적 개수가 아니다. 원본을 0으로 칠하면 존재하지 않던 Sobel 경계도 생성됐다.

초기 구현은 **‘제외 영역의 모든 광학 영향이 제거됐다’가 아니라 ‘정의된 측정 aperture에서 샘플을 제외했다’**고 명시한다. 영향 제거가 실제 실패 원인으로 확인되기 전부터 전체 CLAHE나 contour pipeline을 재작성하지 않는다. kernel support를 고려할 필요가 생기면, dilation은 결과 맞추기용 조절값이 아니라 해당 연산의 고정 stencil에서 유도되는 측정 유효성 규칙이어야 한다. 물리적 artifact label의 확장이 아니다. [R06, E03]

### 5.4 제외 후 신뢰도를 부풀리면 안 된다

제외된 증거는 clean evidence가 아니다. 남은 두 sector만 보고 ‘남은 것 중 100%가 맞는다’고 원래 다섯 sector의 지지로 승격해서는 안 된다.

기록해야 하는 값은 원래 유효 면적, 제외 면적, 실제 사용 면적, 원래 sector 수, 실제 사용 sector 수, support 부족 원인이다. 평균은 실제 사용한 표본으로 계산하되, 가시성과 coverage의 분모를 제거 후 남은 부분으로만 바꾸어 confidence를 자동 상승시키지 않는다. 데이터가 부족하면 `INSUFFICIENT_SUPPORT`이며 `INTERFACE_SUPPORTED`, `NO_INTERFACE`, `FULL`의 근거가 아니다.

---

## 6. 제안하는 detector 구조

### 6.1 변경 경계

```text
원본 frame / 기존 ROI / 기존 전처리
          │
          ├── 기존 Foam raster·motion·temporal 경로 ─── 그대로 유지
          ├── 기존 Oil hypothesis 및 기존 context ─── 그대로 유지
          │
          └── Oil 후보 측정 owner
                   │
                   ├── 원래 sampling support V
                   ├── opt-in 국소 XY exclusion E
                   └── 사용 support M = V ∩ not(E)
                             │
                       기존 후보 생성·재측정
                             │
                 실제 사용 영역과 부족 원인을 lineage에 보존
                             │
                 기존 authority / track / phase / selector
                             │
                    completed 결과 / 기존 report
```

초기 변경의 중심은 `phase_candidate_assembler.py`, `oil_material_path.py`, `oil_supplemental_path.py`다. 공용 `geometry_masks.py`는 기존의 실제 전체 ROI 제외 기능을 그대로 유지한다. Oil만을 위한 의도를 공용 `geometry.exclusions`에 다시 숨겨 넣지 않는다.

### 6.2 입력 정책

첫 구현에서는 UI·Recipe schema 확장보다 detector의 opt-in 실행 문맥을 우선한다. 예를 들어 다음 의미의 immutable 입력을 전달한다. 이름은 제안이며 현재 존재하는 API라고 주장하지 않는다.

```python
OilMeasurementScope(
    source_rects=tuple_of_rects,
    coordinate_basis="source_frame",
    application_scope="oil_candidate_measurement",
    source_binding=geometry_and_reference_binding,
)
```

기본값은 `None` 또는 빈 영역이며 기존 동작과 정확히 같다. 입력은 기존 `Rect`와 좌표 변환 유틸리티를 재사용한다. 등록 reference를 자동으로 whole-candidate rejection으로 전환하지 않는다. 단순 제외 정책과 검토된 edge label의 출처·의미를 별도로 저장한다.

필수 계약:

- 영역은 half-open source 좌표로 정의하고 crop 경계에서 일관되게 clipping한다.
- 영역 밖, 같은 X의 다른 Y, 다른 Glass에는 영향을 주지 않는다.
- 원본 frame·recipe·truth를 수정하지 않는다.
- 잘못된 binding이나 좌표 입력은 실행 전 validation에서 명시적으로 거부한다. 조용히 더 큰 범위를 적용하지 않는다.
- 해당 기능이 없는 기존 recipe/session은 기존 경로를 그대로 사용한다.
- 제품 저장 형식과 UI는 물리적 효과가 입증된 이후 별도 변경으로 다룬다.

### 6.3 측정 연산

각 측정 footprint `W`에 대해 먼저 `W ∩ E`가 비어 있는지 확인한다.

```text
if W와 E가 교차하지 않음:
    기존 측정값·availability·후보 생성 결과를 그대로 재사용
else:
    제외 후 실제 표본과 남은 공간 지지를 계산
    대조 양쪽의 표본 분포가 비교 가능한지 확인
    부족/불일치는 typed unavailable로 유지
    실제 재측정한 기존 후보 표현만 반환
```

상·하부 비교를 국소적으로 보호하는 최초 구현 후보는 다음이다.

- 제외로 영향을 받은 sector/scale에서만 양쪽에 모두 완전한 표본이 있는 X 집합을 계산한다.
- 기존 최소 표본 면적 기준을 그대로 적용한다. 이를 낮춰 좌표를 생산하지 않는다.
- 해당 집합이 부족하면 그 측정은 unavailable이다. 다른 sector의 실제 지지는 유지한다.
- 영향을 받지 않은 sector/scale의 legacy pooled 연산은 바꾸지 않는다.

이 규칙은 **다음 실행에서 확인할 가설**이다. 이번에 실패한 C/D는 전역 치환이었으므로 이 국소 규칙의 결과를 대신하지 않는다. 반대로 국소 규칙이 반드시 성공한다고도 가정하지 않는다.

### 6.4 후보와 lineage

새로운 dense contour 추적기를 먼저 만들지 않는다. 기존 후보 family와 bounded proposal budget을 유지한다. 기존 A1 lineage와 material-path sidecar에 다음 의미의 정보만 필요한 범위로 추가한다.

| 항목 | 의미 |
|---|---|
| frame / Glass / source binding | 어떤 원본 관측인지 |
| family / original proposal identity | 변경 전후 대응을 추적할 기준 |
| native sampling windows | 실제 읽은 X·Y 범위, 중심선 envelope와 구분 |
| original valid / excluded / used count | 실제 분모와 제외량 |
| original sectors / usable sectors | support 소실을 숨기지 않기 위한 수 |
| sampling/preprocessing basis | 어떤 raster와 aperture를 사용했는지 |
| status / first unavailable reason | available, insufficient, invalid binding 등의 구분 |

원래 후보를 통째로 제거한 뒤 다른 후보에 그 identity를 붙이지 않는다. 새 좌표나 새 path는 재측정된 후보의 원래 권한 수준을 갖는다. ‘구조물 일부를 뺐으니 나머지는 진짜 계면’이라는 authority는 부여하지 않는다.

### 6.5 downstream 정책

이번 구현에서 authority, tracklet, phase, selector의 판단 규칙을 동시에 고치지 않는다. 선택 결과와 phase가 달라지는 것은 가능하지만, 그 변화는 후보 측정 변경의 결과로 추적해야 한다.

`FILLED_CAP_VETO`로 막혔다고 veto 자체를 낮추거나 초기 FULL/EMPTY 진입 조건을 바꾸지 않는다. Foam의 `inverted_topology`를 발견했다고 Foam validity를 강제로 true로 만들지 않는다. 먼저 후보가 어떤 남은 지지로 선택됐는지 검증한다. 원래 규칙의 독립된 결함이 확인되면 기존 O3/phase 절차 아래 별도 수정으로 분리한다.

---

## 7. 구현 작업 명세

### WP0 — 이번 실행 결과 보존: 완료

입력 pin, 기준 재현, 네 추가 비교, 72개 focused test, 12개 계약 검사, 실제 report 두 종류, 나머지 presentation과 비교 그래프를 보존한다. 이 작업을 새 audit 단계로 다시 시작하지 않는다.

### WP1 — Oil 측정 범위 입력과 기존 후보 경로 연결

**목표:** B의 제한된 owner 경계를 명확한 opt-in 코드 경로로 구현한다. 단순히 진단 필드를 더 추가하는 작업으로 끝내지 않는다.

| 항목 | 명세 |
|---|---|
| 주요 파일 | `phase_candidate_assembler.py`, `oil_material_path.py`, `oil_supplemental_path.py` |
| 연결 파일 | `opencv_phase_detector.py`, `phase_frame_detection.py`의 실행 문맥 전달부만 필요시 수정 |
| 재사용 | 기존 Rect/좌표 유틸리티, 기존 sector/scale/후보 예산, A1 lineage |
| 기본 동작 | 범위가 없으면 정확히 legacy와 동일 |
| 금지 | Foam 공용 mask 변경, template rejection과 중복 적용, family 권한 상향 |
| 산출물 | opt-in 구현, 범위 계약 테스트, 변경 owner 도식 |
| 완료 기준 | 실제 후보 생성에서 XY가 제외되고 다른 X/Y가 보존됨. empty/no-intersection 입력은 기준값과 일치 |

기존 geometry exclusions는 작업장의 전체 가림 영역 지정 기능으로 남긴다. Oil 측정 전용 정책을 넣기 위해 기존 exclusion의 의미를 바꾸지 않는다.

### WP2 — 영향을 받은 측정만 안전하게 재계산

**목표:** 제외가 상·하부 비교의 표본 집합을 왜곡할 때, 없는 경계를 만들거나 confidence를 부풀리지 않게 한다.

| 항목 | 명세 |
|---|---|
| 주요 파일 | `oil_supplemental_path.py`의 band 평균/프로파일, `oil_material_path.py`의 sector support |
| 핵심 변경 | 제외 footprint와 교차하는 연산만 별도 처리; 비교 가능한 남은 지지와 unavailable 명시 |
| 유지 | 제외와 무관한 연산의 결과, 기존 최소 면적과 proposal thresholds |
| 테스트 | 가로 밝기 ramp, 실제 세로 step, 비대칭 제외, 공통 X 없음, 일부 sector 소실, same-X-other-Y 회복 |
| 산출물 | local-only 측정 규칙과 수식, 지원/부족 원인 trace, 전역 paired 치환과 다른 ablation |
| 완료 기준 | 무마스크/비교차가 정확히 baseline이고, 합성 가짜 대비가 생기지 않음. 실영상 효과는 WP4에서 별도 판정 |

preprocessing 전체 교체는 포함하지 않는다. 실제 오검출이 kernel dependency에서 비롯된다는 대조가 있는 경우에만 고정 stencil 유효성 처리를 별도 최소 변경으로 제안한다.

### WP3 — 남은 지지와 후보 identity의 연결 보존

**목표:** ‘남은 지지가 있다’와 ‘올바른 후보를 복구했다’를 분리하고, 유효한 근거가 없어지는 첫 지점을 파악할 수 있게 한다.

| 항목 | 명세 |
|---|---|
| 재사용 owner | `PhaseCandidateAssembly`, material-path diagnostics, `oil_pipeline_diagnostics.py` |
| 기록 단위 | 영향을 받은 candidate × 실제 sampling window |
| 필요한 구분 | original/used support, native/centered geometry, mask eligibility/physical visibility |
| 금지 | 후보 index·source·Y 근접으로 물리적 label 자동 복사, 5점을 dense contour로 보간 |
| 산출물 | baseline–challenger 대응표, 생성/유지/권한/최종 선택의 단계별 변화 |
| 완료 기준 | 삭제·추가·변경된 후보와 최초 eligibility 변화가 분리되어 설명됨. 미확인 identity는 미확인으로 남음 |

전체 candidate에 거대한 새 진단 구조를 항상 붙이지 않는다. 기존 debug level 경로와 bounded sidecar를 이용하고, debug on/off가 동일한 detector 결과를 내도록 한다.

### WP4 — 하나의 고정된 paired 실영상 비교

**목표:** fragment·contour의 완전 분류가 아니라 report의 주요 움직임이 보존·개선되는지 판정한다.

먼저 실행 정책, mask scope, 영향 owner, 비교항목을 고정한다. 그 뒤 다음 두 가지를 비교한다.

```text
B0: 현재 승인된 baseline
B1: WP1–WP3의 opt-in scoped measurement 구현
```

수치 안전 처리의 기여를 분리해야 한다면 같은 구현에서 기능을 끈 하나의 대조를 추가한다. 실패한 전역 paired 평균을 다시 미세 조정하거나, 마스크 크기·seed·threshold를 연속 탐색하지 않는다.

실행 범위는 sample4 0–56초 전체와 다른 세 qualification window다. sample4의 기존 7개 target·3개 wrong-target binding을 보존하고, 40·42·44초뿐 아니라 49.5·52초 및 구간 끝의 변화를 함께 확인한다. 새로운 Y의 근접도만으로 성공 개수를 계산하지 않는다.

산출물은 기존 replay/evaluator/report owner를 이용한 baseline/challenger report, 단계별 trace, 구간 판정표다. 새로운 평가 프레임워크를 만들지 않는다. 판정은 §8을 따른다.

### WP5 — 승격 판단과 종료

**국소 후보 개선의 정보 가치가 있더라도 production 승격과 field qualification은 별도다.** O2의 반대 대조·holdout·Windows 절차가 충족되기 전 authority로 승격하지 않는다. 승인 가능한 후보가 만들어진 이후에만 Windows 실행 패킷을 준비한다. 지금 이미 닫힌 D1/D2 질문을 사용자에게 다시 요청하지 않는다.

다음 실행에서도 잘못된 주요 움직임이 줄지 않거나 보호 구간이 무너지면 이 분기를 해당 범위에서 종료한다. 원래 픽셀을 더 세밀하게 전부 라벨링하거나 한 좌표 주변의 파라미터를 계속 튜닝하는 것은 종료 조건을 우회하는 행위다. 추가 작업은 새로운 관측량 또는 별도로 입증된 구현 결함이 있을 때만 제안한다.

---

## 8. 제품 목적에 맞는 수용 기준

### 8.1 1차 기준: 구간의 움직임

| 평가축 | 수용 질문 | 실패 사례 |
|---|---|---|
| 이동 방향·반전 | 실제 상승/하강/반전 순서를 report에서 읽을 수 있는가? | 구조물로 owner가 바뀌어 급등·급락처럼 보임 |
| 주요 극값 | 보고서가 강조한 최고/최저가 실제 주요 계면 맥락인가? | 이미 잘못된 대상으로 검토된 row가 주요 극값이 됨 |
| 관측 소실·회복 | 짧은 누락 이후 같은 물리적 맥락으로 돌아오는가? | 잘못된 FULL/EMPTY 의미로 뒤 구간 전체가 막힘 |
| Foam 에피소드 | 발생·소멸·Oil과의 분리가 이해되는가? | mask 때문에 전체 episode가 사라지거나 여러 짧은 episode로 분절됨 |
| uncertainty | 보이지 않는 구간을 모른다고 남기는가? | 남은 두 조각을 깨끗한 전체 계면으로 과신 |

단일 frame의 작은 위치 변화나 짧은 누락은 그 자체로 제품 실패가 아니다. 반면 여러 초의 false owner, 주요 극값의 잘못된 의미, 후반 전체 관측 소실은 우선 해결할 실패다. 단순 평균 정확도·numeric row count보다 이 축을 먼저 읽는다.

### 8.2 보호 대조와 100% recall을 혼동하지 않는다

고정한 보호 사례에서 회귀가 없어야 한다는 요구는 ‘모든 미래 영상의 모든 frame을 100% 검출’하라는 요구가 아니다. 이미 전달되던 중요 맥락을 새 기능이 파괴하지 않게 하는 regression 기준이다.

7개 target의 물리적 대응은 유지하고 변경된 scalar/path의 truth는 자동 생성하지 않는다. 검토상 계면이 보이는 지점의 빈 출력은 누락으로 기록한다. 변형된 후보가 근처에 있다는 이유로 이를 복구로 치환하지 않는다. 다만 전체 구간의 의미가 좋아졌는지 판단하는 데 모든 미세 contour의 신규 라벨을 요구하지도 않는다.

### 8.3 hard contracts

- 원본 영상·recipe·truth 보존, source-frame 좌표와 frame identity 보존.
- 같은 frame의 선택 후보 Y = completed raw Y = CSV raw Y라는 provenance 계약 유지.
- interpolation/carry/보고서 smoothing으로 관측을 제조하지 않음.
- Oil/Foam 별 validity를 확인. raw count만 같다고 보존 판정하지 않음.
- 기능 OFF와 빈/비교차 범위는 baseline과 동일.
- debug NONE/BASIC/FULL 간 판단 결과 동일. 진단 실패가 물리적 authority를 만들지 않음.
- masked/unavailable을 clean/no-interface/FULL로 승격하지 않음.
- 처리량·메모리는 기존 qualification budget 안에서 검증. 이번 동시 실행 wall time은 성능 수용 증거로 쓰지 않음.

---

## 9. Windows 증거를 사용하는 방법

Windows 영상 자체와 annotated image의 bytes는 이번 Mac 작업에서 보지 않았다. 기존 문서의 사용자 전달 기록을 검토했다. 전달 기록과 직접 검증한 Mac 실행을 혼합해 ‘Windows에서 확인됐다’고 쓰지 않는다.

### 9.1 이미 확인한 두 가지 설계 제약

D1의 정정 결과는 총 73개 중 retained 45 / absent 28이다. review-001의 기존 7/7/9 해석은 0 not-selected / 11 tracklet-not-admitted / 12 absent로 정정됐다. 이미 닫힌 이 확인을 새 검증 과제로 다시 만들지 않는다.

D2의 target idx13은 canonical Y291이지만 native sector0는 Y315였고, 사용자는 그 부분을 그림자 또는 공동 경계로 보인다고 설명했다. 이것은 **한 후보 안에서도 local support가 다른 대상을 볼 수 있다**는 설계상 주의점이다. 후보 전체를 폐기하거나 나머지 sector를 모두 정답으로 선언할 근거는 아니다. Mac의 고정 XY 좌표를 이 Windows 영상에 옮겨 넣지 않는다. [R09, R10]

### 9.2 향후 통합 field gate

승격 후보가 생기면 다음 아홉 구간을 기존 reviewed truth 그대로 평가한다. 시각 경계의 ‘약’은 유지하고 exact-Y anchor를 만들어내지 않는다.

| Segment | 검토된 물리적 의미 |
|---|---|
| `WS1-BASE-FULL-PREFIX` | 480–약550초: 가득 참, 계면 없음, Foam 없음 |
| `WS1-BASE-DRAIN` | 약550–662초: 보이는 oil-air 계면 하강 |
| `WS1-BASE-RAPID-REFILL` | 662–약663.6초: 빠른 상승 후 상단에서 계면 소실 |
| `WS1-BASE-FULL-SUFFIX` | 약663.6–780초: 가득 참, 계면·Foam 없음 |
| `WS1-ACCUM-EMPTY` | 480–약653초: Oil·Foam 없음 |
| `WS1-ACCUM-ENTRY-SPLASH` | 약653–672초: 유입·splash·Oil 상승, Foam 아직 없음 |
| `WS1-ACCUM-FOAM-LAYERED` | 약672–680초: 상부 Foam과 하부 Oil 경계 분리 |
| `WS1-ACCUM-POST-FOAM` | 약680–700초: Foam 사라지고 Oil 계면은 남음 |
| `WS1-ACCUM-DRAIN` | 약700–780초: Oil 하강, 벽 잔류물은 대체 계면이 아님 |

Local PASS가 이 field gate를 대신하지 않는다. 이번 작업으로 Windows detector 성능 향상이나 처리량을 주장하지 않는다. [R11]

---

## 10. 테스트·검증 결과와 남은 범위

### 10.1 이번에 완료한 검증

| 항목 | 결과 |
|---|---|
| 기존 네 영상 baseline fingerprint | 4/4 일치, 299 sampled rows |
| sample4 추가 비교 | 4개 구성 × 113 rows 실행 |
| 전체 sampled result rows | 751 |
| 국소성·표본 대비·전처리 의존성 계약 검사 | 12 PASS |
| focused pytest | 72 PASS, 13.51초 |
| production Python source hash | 220개 변경 없음 |
| 동결 입력 hash | 16개 변경 없음 |
| `git diff --check` | PASS |
| tracked worktree / HEAD | clean / 원래 HEAD 유지 |
| governance checker | PASS, 단 tracked 변경이 없다는 범위 |
| production 적용 / commit / push | 없음 |

72개 pytest의 대상은 material path, supplemental path, artifact reference/diagnostics, measurement lineage, geometry 관련 테스트다. 12개 계약 검사는 별도의 실험 assertion이며 84개의 제품 unit test로 합산해 표현하지 않는다.

### 10.2 아직 하지 않은 것

- WP1–WP3의 정식 opt-in 구현 및 제외 영향 footprint에만 적용하는 local numerical guard.
- 모든 Oil family와 전처리 의존성에서 구조물 영향을 제거하는 통합 구현.
- 정확한 fragment/path/scalar truth의 신규 확정 또는 새 holdout 성능 평가.
- Windows 원본 영상 실행과 아홉 구간 field qualification.
- B/C/D의 실제 HTML 전체 렌더링 검수 및 성능 qualification.

이 항목들은 이번 성공 주장에 포함하지 않는다. 특히 ‘국소 XY를 시험했다’는 사실을 ‘국소 XY의 모든 구현 가능성을 시험했다’로 확장하지 않는다.

---

## 11. 작업 순서와 중단 규칙

다음 개발은 **WP1 → WP2 → WP3 → WP4 → WP5** 순서다. WP0는 이미 완료했으므로 문서·진단 준비를 반복하지 않는다.

첫 구현 묶음에서는 sample4의 특정 Y를 고치는 최적화가 아니라, 어떤 Glass에서도 명시적으로 지정한 국소 범위가 동일한 의미로 적용되는 primitive와 실제 후보 연결을 완성한다. 본 명세의 좌표는 regression fixture에만 남기고 production 분기에 사용하지 않는다.

다음 fixed comparison이 실패하면 사유를 다음 네 범주로 분리한다.

1. **측정/구현 결함:** 좌표 변환 오류, 비대칭 표본으로 만들어진 대비, 분모 오류. 계약에 따라 수정하고 동일 대조를 재실행할 수 있다.
2. **남은 지지 부족:** 사용할 증거가 없어져 공백이 생김. threshold를 낮추거나 제거 영역을 결과에 맞춰 움직이지 않는다.
3. **권한/연결/phase 문제:** 지지는 있지만 기존 단계에서 잘못 처리됨. 원인 증거를 묶어 별도 승인 범위로 분리한다.
4. **물리적 구분 정보 부족:** 남은 모양만으로 구분되지 않음. 더 긴 라벨 작업이나 score 탐색 대신 현재 분기를 종료한다.

한두 edge case 때문에 완료 조건을 무한히 늘리지 않는다. **주요 움직임의 잘못된 해석을 줄이고, 이미 이해 가능했던 구간을 유지할 수 있는가**가 진행·종료 기준이다.

---

## 12. 실행 산출물과 재현

### 12.1 원본 실행 디렉터리

```text
/Users/sunjaekim/Developer/oil_level_tracker/
  sample/output/s11-local-xy-exclusion-20261009-001/
```

이 디렉터리는 ignored local output이다. 저장소의 tracked source를 바꾸지 않았으며 원본 실행 자료가 Git에 자동 백업된 것은 아니다. 본 전달 문서와 요약 JSON도 원본 영상·trace·report bundle 전체의 백업이 아니다.

### 12.2 파일 목록

| 파일 또는 디렉터리 | 역할 |
|---|---|
| `preflight.json`, `runner-pin.json` | 최초 입력·source pin과 실행 범위 |
| `run_xy.py` | 네 baseline + 공유 XY 제외 실실행 |
| `results.json` | 최초 비교의 전체 public 변경 |
| `probe_contracts.py`, `probe-preflight.json`, `contract-results.json` | 12개 수치·기하·의존성 검사 |
| `real-support-readout.json` | 고정 지점의 기존/제외 후 phase sampling support |
| `run_measurement_scope.py`, `measurement-scope-preflight.json` | B/C owner 및 평균 연산 비교 |
| `measurement-scope-results.json` | B/C 실행 수치 |
| `run_pair_control.py`, `pair-control-preflight.json` | D 무마스크 대조 |
| `summarize_experiments.py` | 전체 결과 집계와 비교 그래프 |
| `compact-summary.json`, `detailed-summary.json` | validity 및 phase/selection까지 포함한 요약 |
| `sample4-*/raw.json`, `completed.json`, `tracking.json`, `report.json` | 각 단계의 실제 기록 |
| `sample4-baseline/…/report.html`, `sample4-local_xy_rectangle/…/report.html` | 실제 report bundle |
| `oil-comparison.png`, `foam-comparison.png` | completed raw 좌표 비교; 수치 존재와 validity를 별도로 읽을 것 |
| `sample4-original-controls.jpg`, `other-samples-original-rois.jpg` | 원본 영상에서 추출한 ROI 시각 검토 |
| `focused-tests.log`, `governance-check.log` | 테스트·검사 출력 |

### 12.3 재실행 방법

실행 스크립트는 기존 결과를 덮어쓰지 않도록 되어 있다. `sample/output/` 아래 새 디렉터리를 만들고 동결 preflight와 runner를 복사한 뒤 순서대로 실행한다. 스크립트가 `parents[3]`으로 repo root를 해석하므로 디렉터리 깊이는 유지한다. 기존 결과 디렉터리 안에서 같은 스크립트를 다시 실행하지 않는다.

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
# 새 sample/output/<run-id>/ 안에 해당 preflight/runner 파일을 먼저 준비한다.
.venv/bin/python sample/output/<run-id>/run_xy.py
.venv/bin/python sample/output/<run-id>/probe_contracts.py
.venv/bin/python sample/output/<run-id>/run_measurement_scope.py
.venv/bin/python sample/output/<run-id>/run_pair_control.py
.venv/bin/python sample/output/<run-id>/summarize_experiments.py
```

source/input pin이 다르면 기존 결과와 같은 실험이라고 주장하지 않는다. 새 HEAD에 적용할 때는 원래 preflight를 덮어쓰는 대신 변경된 입력·owner를 새 manifest로 고정한다. 성능 비교에서는 프로세스를 직렬로 실행하고 별도 반복 측정한다.

---

## 13. History Review

- **범위:** local measurement exclusion과 그 후보/sequence 파급. report나 UI 변경이 아님.
- **관련 node:** `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`.
- **검토한 실패:** F02 proposal starvation, F04 identity leakage, F06 Oil/Foam cross-coupling, F09 provenance/validity ambiguity, F10 case-specific/threshold escape.
- **재반복하지 않을 것:** family/whole-track rejection, reference overlap=artifact 판정, template로 전체 후보 거부, positive patch에 reference가 있다는 이유로 오류 판정, paired 평균의 전역 확대, hard-gate 우회.
- **기존 시도와의 차이:** 후보를 사후 거부하는 대신 명시적 X·Y sampling aperture를 먼저 바꾸어 기존 후보를 생성·측정했다. 새로운 numerical guard는 영향을 받은 footprint에만 한정하도록 설계한다.
- **보존 계약:** no interpolation/carry, same-frame provenance, independent series validity, unknown≠clean, 원본 truth 불변, bounded candidate budget.
- **로직맵 영향:** 이번 실행은 NONE. ignored prototype의 process-local wrapper만 사용했고 tracked production owner는 변경하지 않았다. WP1 구현 시 실제 변경 owner와 데이터 흐름을 갱신해야 한다.
- **실패 registry 영향:** 이번 실행에서 기존 항목을 은퇴시키거나 해결했다고 선언하지 않는다. 필요한 실행 증거만 추가한다.

## 14. Detector Governance

**현재 disposition:** `EXPERIMENT_COMPLETE / NOT_PROMOTED`.

공유 mask 실험과 전역 paired 실험은 adoption rejected다. Oil 측정 전용 실험은 다음 제한된 구현의 출발점으로 남긴다. candidate sampling 변경의 결과가 track/phase와 validity에 미치는 영향은 관측됐지만, 이를 근거로 기존 authority·phase 규칙을 함께 바꾸지 않는다. 이번 명세서의 작업 순서는 기존 O2/O3 및 Windows qualification 절차를 우회하지 않는다.

최종 결론은 **‘국소 X·Y 제외는 안 된다’도, ‘국소 제외만 넣으면 해결된다’도 아니다.** 정확한 다음 단계는 **제외 의도를 Oil의 실제 측정 범위에 제한하고, 영향을 받지 않은 측정을 보존하면서, 남은 지지로 report의 주요 움직임을 유지할 수 있는지 한 번의 고정된 구현 비교로 검증하는 것**이다.

---

## 15. 근거 인덱스

아래 R 항목은 위 HEAD에서 직접 읽은 repo 자료다. E 항목은 이번 로컬 실행 결과다. 문서 본문의 번호는 출처를 찾기 위한 표기이며 외부 논문·제품 근거를 의미하지 않는다.

| ID | repo 기준 경로 또는 실행 산출물 | 사용한 내용 |
|---|---|---|
| R01 | `docs/00-project/work-plan.md` | 최신 S11 상태·active owner·남은 작업 |
| R02 | `docs/60-evidence/s11/2026-10-09-d2-reference-measurement-comparison.md` | template/footprint/local sampling의 구분 |
| R03 | `docs/60-evidence/s11/2026-10-09-d2-sequence-context-feasibility.md` | 종료된 비교와 미시험 local-XY 범위 |
| R04 | `src/oil_tracker/adapters/vision/artifact_calibration.py` | signature와 whole-candidate rejection |
| R05 | `src/oil_tracker/adapters/vision/geometry_masks.py` | 실제 rectangular exclusions 및 공유 mask |
| R06 | `src/oil_tracker/adapters/vision/preprocessing.py` | CLAHE/blur/Sobel/Canny/closing 순서 |
| R07 | `src/oil_tracker/adapters/vision/oil_material_path.py`, `oil_supplemental_path.py`, `phase_candidate_assembler.py` | 실제 sector/scale/평균/후보 경로 |
| R08 | `docs/50-diagnostics/s11/2026-10-07-sample4-interval-candidate-lineage.md`, `docs/60-evidence/s11/2026-10-07-a2-target-binding.json` | 사람 검토 7 target·3 wrong-target·현재/최종 선택·first eligibility loss |
| R09 | `docs/60-evidence/s11/2026-10-08-next-work-intake.md` | D1 Windows 반환 기록 정정 및 한계 |
| R10 | `docs/60-evidence/s11/2026-10-08-d2-control-preflight.md` | Windows idx13 native support 검토와 한계 |
| R11 | `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` | Windows 9구간 물리적 기준 |
| R12 | `docs/20-architecture/s11-current-detector-logic-map.md` | current/sequence/public owner |
| R13 | `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` | no-repeat 및 비회귀 계약 |
| R14 | `docs/30-validation/s11-interface-observability-witness-validation.md`, `s11-detector-change-governance.md` | O2/O3/field 승격 기준 |
| E01 | 동반 실행 요약 JSON 및 local `preflight.json`, `results.json` | 고정 입력·실행 규모·최초 결과 |
| E02 | local `run_xy.py`, `runner-pin.json` | 실제 영상→detector→resolver→report 실행 |
| E03 | local `probe_contracts.py`, `contract-results.json`, `real-support-readout.json` | 12개 계약 검사와 sampling 측정 |
| E04 | local `run_measurement_scope.py`, `measurement-scope-preflight.json`, `measurement-scope-results.json` | Oil owner 분리 및 paired 비교 |
| E05 | local `run_pair_control.py`, `pair-control-preflight.json`, 해당 summary | paired 무마스크 대조 |
| E06 | local `compact-summary.json`, `detailed-summary.json`, 각 raw/completed/tracking/report | full-window 변화·Foam validity·phase 경로 |

