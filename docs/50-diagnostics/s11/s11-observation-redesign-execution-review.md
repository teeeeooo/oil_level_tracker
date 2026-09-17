# S11 투명 계면 검출 재검토 및 실행 명세서

> 보관 위치: 근거 재검토와 실행 제안을 담은 진단 문서. 구현의 단일 기준은
> [Witness Architecture](../../20-architecture/s11-interface-observability-witness-architecture.md),
> 수용 기준은 [Witness Validation](../../30-validation/s11-interface-observability-witness-validation.md)이다.
> 아래의 `577f98a` 기준 검토·실행 기록은 역사적 사실로 보존한다.

- 작성일: 2026-09-17
- 검토 저장소: `teeeeooo/oil_level_tracker`
- 검토 기준 커밋: `577f98af116e7f59b07bc8a8356606c4dd7f9bea`
- 기준 동작: R22 / 진단 런타임 `opencv-phase-detector-r22-2-interface-path-diagnostics-v1`
- 문서 성격: 기존 설계의 근거 재검토와 구현 구체화 제안. 저장소의 기존 architecture/validation/work-plan을 대체하지 않는다.
- 승인 범위: 이 문서는 구현안이며, 신규 detector의 구현·승인·Windows 실검증을 의미하지 않는다.
- 현장 상태: `FIELD FAIL` 유지.
- 보안 경계: 업무용 Windows의 원본 영상, 파생 이미지, 상세 trace, annotation, 학습 가중치 및 통계의 반출을 전제하지 않는다.

## 1. 결론

**전체 detector를 폐기하지 않는다. 임계값 조정 중심 개선은 멈추고, 관측·계면 표현층을 제한적으로 재설계한다.**

보존할 대상은 R22의 같은 프레임 좌표 출처, Oil/Foam 독립성, 제한된 시간창, 물리적 추적 소유권, 모호할 때 숫자를 내지 않는 규칙, 후단 출력 계약이다. 바꿀 대상은 실제 계면을 단일 Y 값과 후보 점수만으로 다루는 관측 표현, 후보 주변의 물리적 구분 근거, 구간별 위치 불확실성이다.

단, 모든 현장 실패를 관측층 하나의 원인으로 묶지 않는다. 실제 계면 후보가 있어도 authority 또는 phase allowed-set에서 막히는 실패는 별도 경로로 남는다. 관측층 개선이 이들 후단 문제까지 자동으로 해결한다는 주장은 하지 않는다. [R1–R6]

이 결론은 현재 main에 이미 기록된 방향과 일치한다. 따라서 새로운 R번호나 경쟁하는 아키텍처를 추가하는 대신, 기존 O1–O5 단계의 구현과 중단·진행 판정 기준을 구체화한다. 정식 구현·수용 조건은 기존 Witness Architecture와 Witness Validation을 따른다. [R10, R11]

### 선택지 판단

| 선택지 | 판단 | 이유 |
|---|---|---|
| 기존 점수·threshold 계속 조정 | 중단 | 실제 계면과 반사·잔유·구조물의 신호가 겹치는 문제를 숫자 하나로 해결한다는 근거가 없다. |
| 전체 detector 재작성 | 현재는 부적절 | 검증된 provenance·Oil/Foam 독립성·상태 안전장치를 다시 만드는 비용이 크고, 광학 정보 부족을 해결하지 못한다. |
| 관측층 제한 재설계 | 우선 진행 | 곡선 위치, 주변 문맥, 불확실성을 보존한 뒤 후단에 전달할 수 있다. |
| 학습 기반 모델로 즉시 전환 | 첫 단계로 채택하지 않음 | 압축기 도메인의 검증 분할과 라벨이 먼저다. 단, 반출 불가가 업무 PC 내부의 오프라인 학습까지 금지하는 것은 아니다. |
| 촬영 조건 개선 | 소프트웨어와 병행 검토 | 영상을 더 잘 해석하는 문제와 구분 가능한 영상을 얻는 문제를 분리해야 한다. |
| 전용 센서 대체 | 조건부 확장안 | 광학 관측이 요구 운전영역에서 계속 불충분할 때 검토한다. 센서의 액면 감지가 오일 성분 식별이나 연속 Y 측정과 같지는 않다. |

## 2. 근거와 신뢰 범위

### 2.1 저장소에서 확인한 상태

현재 work-plan은 O1의 trace-only contour/context observability witness 구현을 다음 단계로 정한다. R22-2는 R22 판단을 바꾸지 않는 진단 확장이고, R23 polarity-only association 실험은 회귀 때문에 철회되어 있다. [R1, R2, R5]

현재 코드의 `measure_oil_interfaces()`는 거절된 Oil 후보도 포함하여 다섯 구간에서 후보 중심과 native material path를 측정한다. 반환값은 진단 전용이고 `classification=not_evaluated`이다. 호출 지점은 `phase_frame_detection.py`의 `PhaseDebugProjector.project()`이며, 결과는 `artifacts.state.oil_interface_diagnostics`에 들어간다. [R7, R8]

### 2.2 이번 검토에서 직접 재실행한 공개 검사

기존 `tests/diagnostics/s11_interface_witness_probe.py`를 수정 없이 실행했다.

| 항목 | 이번 실행 결과 |
|---|---:|
| 실제 원본 기준 프레임 | 13개 |
| 원본 포함 영상 변환 조건 | 7개 |
| frame/transform 측정 | 91개 |
| 각 조건에서 정답 Y ±8 px 안에 후보가 있는 프레임 | 각각 13/13 |
| 원본의 최근접 후보 오차 | 중앙값 1 px / 최대 8 px |
| 원본 프레임당 Oil 후보 수 | 중앙값 24개 |
| 원본 프레임당 정답 근처 후보 수 | 중앙값 4개 |
| 입력 video/recipe/truth 해시 | 기존 manifest와 일치 |
| 전체 결과 SHA-256 | `f2ec4f6636f1fba30c02a8d5726fec131399cedf2bbbb4e83a80c7330d2e893d` |
| 저장소의 기존 결과 SHA-256과 비교 | 동일 |
| 관련 기존 단위 테스트 | `tests/unit/test_oil_interface_diagnostics.py`: 14 passed |
| 실행 환경 | Python 3.14.4 / OpenCV 4.14.0 / NumPy 2.5.1 |

91개는 독립된 장면 91개가 아니라 같은 13개 장면에 대한 변환 측정이다. 또한 ±8 px는 진단용 기하학적 근접 기준이지, 제품의 허용오차나 실제 계면이라는 인증이 아니다.

이 결과가 지지하는 결론은 **현재 공개 기준점에서 후보 부족보다 후보 간 구분의 모호성이 크다**는 것이다. 전체 공개 영상의 연속 추적 성공, 업무 영상의 후보 재현율, 최종 검출률 100%를 의미하지 않는다. 재실행에서는 completed-window resolver를 실행하지 않았고 static map 학습도 수행하지 않았다. [R2, R9]

이번 실행의 로컬 상세 결과는 `/tmp/s11-external-review-WQA9RynM/public-probe.json`이다. `/tmp` 결과는 영구 evidence 보관소가 아니므로 경로가 아니라 입력 manifest와 위 결과 해시를 재현 기준으로 삼는다.

동일 공개 검사의 재현 명령은 다음과 같다. private 영상용 명령이 아니다.

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
out_dir="$(mktemp -d /tmp/s11-public-probe-XXXXXXXX)"
PYTHONPATH=src:. .venv/bin/python \
  tests/diagnostics/s11_interface_witness_probe.py \
  --transforms original,brightness_0.80,brightness_1.20,gamma_0.80,gamma_1.25,contrast_0.80,contrast_1.20 \
  --output "$out_dir/public-probe.json"
PYTHONPATH=src:. .venv/bin/python -m pytest \
  tests/unit/test_oil_interface_diagnostics.py -q
```

### 2.3 현장 근거는 최소 세 실패로 나눈다

| 실패 종류 | 확보된 근거 | 설계상 조치 | 아직 말할 수 없는 것 |
|---|---|---|---|
| 곡선 위치를 단일 Y로 축약 | BASE의 구간별 계면 위치가 다르며, 근처지만 어긋난 위치가 같은 tracklet의 이동으로 해석된 checkpoint가 있다. | common-X 구간별 위치와 위치 불확실성 보존 | 어긋난 점이 다른 물체였다고 단정할 수 없다. |
| 실제 후보가 후단에서 배제 | Accum의 실제 경계 근처 후보가 존재하지만, 기존 phase allowed-set에 새 tracklet이 없어 배제된 checkpoint가 있다. | witness 검증 뒤 support, handoff, phase admission을 각각 수정 | texture gate 하나를 풀면 전체 구간이 복구된다는 보장은 없다. |
| 물리적 구분 근거 부족 | 후보군에 광학·구조적 대안이 많고 기존 contrast 통계가 겹친다. | 다중 문맥 측정, 반사·잔유 negative, 촬영 A/B 비교 | 모든 미검출 구간이 원래 안 보였다는 결론은 낼 수 없다. |

특히 BASE f14362의 native sector 2는 최신 사용자 검토에서 계면 부근의 위치 불일치로 정정되었다. 이를 확정된 내부 구조물 negative로 학습시키면 안 된다. Accum의 특정 peer가 texture gate에서 제외되는 것은 확인되었지만, 같은 Y 근처에 다른 source 후보가 있다는 사실만으로 독립 근거가 성립하지 않는다. [R3]

현재 방향성 문제가 있는 tracklet을 분리해도, 실제 계면이 정지했다면 하강 증거가 새로 생기지는 않는다. 따라서 association 개선과 초기 FULL에서의 현재 계면 관측 허용은 별도 검증 대상이다.

## 3. 먼저 고정할 측정 대상

### 3.1 이 프로젝트에서 우선 측정할 것

현재 검토된 현장 truth를 기준으로 다음을 작업 정의로 사용한다.

- 일반 구간: 관측창 안에서 보이는 하부 액상 영역의 상단 계면.
- Foam 분리 구간: 상부 Foam front와 하부 Oil/Foam boundary를 별도 관측.
- FULL/EMPTY 구간: 보이는 계면이 없으면 숫자 Y를 만들지 않는다.
- 구조물, 벽면 잔유, splash, glare는 액면의 대체물이 아니다. [R6]

`OIL_AIR`라는 현재 enum 이름을 실제 냉매 기체의 화학적 식별 결과로 해석하지 않는다. 이 단계에서 enum 이름을 바꾸거나 기존 truth를 재작성하지도 않는다.

### 3.2 혼동하지 않을 것

**액면 위치 측정, 오일/냉매 성분 식별, 윤활 적정성 판정은 서로 다른 출력이다.**

오일과 냉매가 하나의 액상으로 혼합된 조건이라면, 액면 영상만으로 그 액체의 높이와 오일 농도를 동시에 안다고 정의해서는 안 된다. 반대로 실제로 상분리된 두 액체의 계면이 측정 대상이라면, 그 계면에 대한 별도 라벨·광학 구분성·검증이 필요하다.

이는 현재 영상이 반드시 혼합 단일상이라는 진단이 아니다. 오일 종류, 냉매, 운전조건 및 창의 관측 위치를 확인하지 않았으므로 이 부분은 측정 계약의 경계다.

최소 유지 높이 판정은 기존 zero-line/px-to-mm 보정과 관측창이 대표하는 위치를 사용해야 한다. 관측창의 액면 하나로 실린더 내부 모든 윤활부의 유막이나 오일 질량분율을 보증한다고 범위를 넓히지 않는다.

## 4. 외부 연구·상용 접근법의 적용 범위

아래는 공개 1차 자료에서 확인한 원리다. 자체 재현 실험이나 압축기 현장 성능 검증을 수행한 것은 아니다.

| 자료 | 확인한 접근법 | 이 프로젝트에 가져올 것 | 그대로 가져오지 않을 것 |
|---|---|---|---|
| Eppel & Kachman, 2014 | 용기 안 후보 곡선 주변의 상대 밝기, edge density 변화, 곡선 법선 대비 gradient 방향 사용 | 단일 행 대신 구간별 곡선과 양측 문맥 비교 | 강한 edge 하나를 물리 계면으로 확정 |
| Eppel, 2015 | 용기 반사·기능 부품의 edge와 내용물의 edge를 구분하기 위한 곡률 기반 접근 | 창/벽/구조물의 optical opposition을 명시 | 용기 대칭성·곡률 가정을 실제 압축기 창에 무검증 적용 |
| TCLD / DTLD, ECCV 2024 | 투명 용기와 투명 액체의 contact line을 Bézier 표현으로 추정; color rectification 사용 | 곡선 표현, 조명 변화 대응, domain label 설계 | 바이오 실험실 데이터의 성능을 압축기에 적용한 성능으로 해석 |
| Verso & Liberzon, 2015, BOS | 배경 패턴과 참조 영상의 굴절 변위를 측정; 유리/액체 광학 경로의 보정 필요 | 광경로가 허용될 때 structured-background 비교 실험 | 후면 광경로가 없는 금속 구조에 그대로 적용 |
| IVC sight-glass video analytics | ROI 설정, 복수 분석 방법, reading별 confidence 제공 | 촬영 조건별 방법 선택과 불확실성 관리라는 상용 설계 방향 | 공개되지 않은 내부 알고리즘을 범용 정답으로 간주 |
| KEYENCE fill-level inspection | 카메라·조명·보정 및 rule-based/AI 검사 조합 | 알고리즘과 취득 조건을 함께 검토 | 병 충전 검사 조건을 압축기 유동 장면과 동일시 |
| Copeland oil controls | float, electronic oil control, sight-glass 연계 감시 제품군 | 독립 점검용 센서 또는 제품 경계 확장 가능성 | 특정 압축기 제품을 rotary에 호환된다고 단정하거나, 점 감지를 연속 계면 좌표로 대체 |

TCLD의 “dual transparent”는 **액체와 용기가 모두 투명하다**는 뜻이다. 오일과 냉매라는 두 액체를 구별한다는 뜻이 아니다. 공개 데이터는 27,458개 이미지지만, 그 규모가 이 프로젝트의 domain generalization을 보증하지 않는다. [E1–E7]

IVC PDF는 두 페이지를 확인했다. 나머지 논문 근거는 arXiv 초록과 저자 공개 README 등 확인 가능한 범위에 한정했다. 접근에 실패한 KRIWAN 상세 페이지 및 일부 Sensors 전문은 이번 추가 결론의 직접 근거로 사용하지 않았다. 외부 코드·가중치를 복사하지 않았다.

## 5. 재설계 경계

```text
프레임 + ROI + 현재 영상 근거
    │
    ├─ 기존 후보 생성: 우선 보존
    │
    └─ [O1 신규 관측 sidecar]
         ├─ 구간별 실제 경로 / 후보 중심
         ├─ 양측 문맥 / 광학 방해
         ├─ 위치의 모호성 / 근거의 출처
         └─ 아직 판정하지 않음
                │
                └─ [O2 shadow: 판단만 기록]
                       │
                       └─ [별도 승인된 O3]
                            support / association
                                  │
                                  └─ [별도 O4]
                                       phase / handoff
                                             │
                                             └─ 기존 selector / projection / CSV
```

O1과 O2에서는 새로운 결과가 production candidate의 feature, penalty, eligibility, authority, tracklet 또는 phase 결정에 들어가지 않는다.

보존하는 계약은 다음과 같다.

1. 모든 숫자 Oil/Foam은 선택된 같은 프레임 후보의 좌표이다.
2. UNKNOWN을 interpolation, carry, 과거 좌표 복사로 메우지 않는다.
3. Oil/Foam의 유효성과 소유권을 분리한다.
4. private Glass, frame, 시간, 정답 Y를 production 분기에 넣지 않는다.
5. 광학적으로 불분명하다는 이유로 FULL/EMPTY를 추정하지 않는다.
6. 현장 qualification은 exact runtime에 대해 별도로 한다. [R1, R4, R5]

## 6. O1 구현 상세 제안

이 절의 파일명·함수명은 기존 설계에 대한 구현 제안이다. 실제 승인 전에는 production의 새 인터페이스로 간주하지 않는다.

### 6.1 구현 위치

| 파일 | 이번 설계에서 제안하는 역할 |
|---|---|
| `src/oil_tracker/adapters/vision/oil_interface_witness.py` | 새 immutable 측정 타입과 집계 결과 |
| `src/oil_tracker/adapters/vision/oil_interface_diagnostics.py` 또는 별도 measurement helper | frame-local profile cache와 신규 측정. 기존 R22-2 필드는 동일하게 유지 |
| `src/oil_tracker/adapters/vision/oil_material_path.py` | 기존 native sample 및 생성 출처 재사용. production 경로·점수 변경 금지 |
| `src/oil_tracker/adapters/vision/phase_candidate_assembler.py` | 기존 pre-sort candidate index와 sidecar 결합 유지 |
| `src/oil_tracker/adapters/vision/phase_frame_detection.py`의 `PhaseDebugProjector` | 새 trace namespace 직렬화 |
| `src/oil_tracker/adapters/vision/oil_candidate_evidence.py` | O1/O2에서는 변경하지 않음. O3 전까지 신규 witness 소비 금지 |

`frozen=True`만으로 내부 dict까지 immutable해지는 것은 아니다. 측정 record는 tuple과 frozen value object로 구성하고, production candidate의 mutable dictionary를 그대로 참조하지 않는다. raster 전체는 저장하지 않는다.

### 6.2 식별자와 좌표

witness key는 적어도 다음을 구분한다.

```text
source_frame_index
glass_id
candidate_input_index_before_trace_sort
candidate_source
candidate_source_y
crop_origin_x, crop_origin_y
```

같은 source/Y의 중복 후보도 input index로 구분한다. score 순서의 index를 원래 후보 index로 대체하지 않는다.

candidate 중심과 native path 중심은 둘 다 보존한다. native path가 없으면 candidate 중심 측정으로 표시하되, 그것을 실제 경로를 얻었다고 표시하지 않는다. 다른 후보의 native path를 빌려오지 않는다.

기존 source Y, crop-local Y, pixel sampling center를 각각 기록한다. 소수점 Y를 sample pixel center로 반올림하더라도 원래 Y를 덮어쓰지 않는다.

### 6.3 다섯 구간과 세 스케일

첫 구현은 기존 다섯 구간과 bounded candidate 수를 재사용한다. 구간별 실제 X extent와 native Y가 있으면 그 값으로 측정한다. 두 표현 비교에는 동일한 X 범위를 사용한다.

새 측정의 스케일은 기본 band 폭 `b`에 대한 고정된 세 스케일로 정의한다. 예를 들어 `b, 2b, 3b`를 사용할 수 있으나 이는 측정 커널 설계 값이며, physical interface 판정 threshold가 아니다. 기존 R22-2의 band 정의를 바꾸지는 않는다.

각 scale에서 구간별로 아래를 측정한다.

- 실제 sample pixel 범위, 의도한 범위, valid pixel 수/비율.
- 양측 gray 평균·분산, signed difference와 absolute difference.
- 양측 edge density와 그 차이.
- gradient의 크기와 법선 방향에 대한 정렬 정도.
- raw material map의 양측 요약과 availability.
- glare, saturation, border/exclusion, static reference의 가용성과 overlap.
- native center와 candidate center에서 측정한 값의 차이.

첫 O1에서 법선을 수직으로 근사하면 `normal_mode=vertical_approximation`으로 남긴다. 이후 실제 곡선 법선 측정과 혼용하지 않는다. 구간이 부족하면 곡선을 보간해서 측정한 것처럼 만들지 않는다.

### 6.4 상대 contrast의 정확한 의미

예시 측정값은 다음과 같다. 이것은 채택할 classifier 식이 아니라 raw descriptor의 정의다.

```text
delta_s = mean(below_s) - mean(above_s)
noise_s = sqrt(var(below_s) + var(above_s) + sigma_floor^2)
normalized_delta_s = delta_s / noise_s
edge_density_delta_s = density(below_s) - density(above_s)
```

`sigma_floor`는 수치 안정화 및 잡음 바닥의 정의이며 명시적 parameter로 기록한다. undefined division을 0으로 숨기지 않는다. raw delta와 분모도 같이 남겨 정규화만으로 confidence가 커진 경우를 식별한다.

밝기 반전 시 signed delta는 바뀔 수 있다. 이를 `DIFFERENT_INTERFACE`나 artifact의 충분조건으로 사용하지 않는다. absolute difference만 사용해 정보를 잃는 것도 피한다.

near/far 문맥 차이는 내부 stripe 구분에 유용한 가설이지만, 기존 공개 자료에서 분포가 겹친다. 따라서 `abs(near)-abs(far)` 하나를 새 hard veto로 만들지 않는다.

### 6.5 근거 출처와 독립성

다음 두 개념을 구분한다.

- **상보적 특징:** 같은 RGB에서 얻은 brightness, edge density, gradient, texture처럼 서로 다른 정보를 요약한 값.
- **독립 취득 근거:** 별도 reference, 적절히 등록된 조명 pair, 다른 센서처럼 취득 경로가 구분되는 값.

같은 gray에서 파생된 Sobel/Canny와 renamed source는 독립 투표가 아니다. raw material map도 현재 RGB에서 파생되었다면 공통 raster ancestry를 기록한다.

반대로 “독립 센서 두 개가 없으면 모든 passive RGB 관측 불허” 같은 새 규칙도 만들지 않는다. 같은 RGB의 상보적 특징은 분류에 유용할 수 있다. 독립성을 과장하지 않고 실제 false positive 억제 성능으로 검증한다.

### 6.6 위치 불확실성과 peak

각 구간에 bounded local search 범위, 최대 세 개의 peak, 동률 처리, 검색 범위 clipping, peak 목록 truncation 여부를 기록하도록 제안한다.

동률 peak를 하나 선택해야 할 때는 결정적인 규칙을 사용하고 그 규칙을 trace schema에 명시한다. 동률 plateau의 범위나 다중 peak의 존재를 단일 정확 좌표로 축약하지 않는다. flat profile에서는 peak가 없다고 기록한다.

중요한 규칙:

- diagnostic peak로 production candidate Y를 이동시키지 않는다.
- native generator path도 physical truth는 아니다.
- scale별 위치 변화와 구간별 후보 편차는 모호성 descriptor이다.
- O1의 interval/hull은 **보정된 통계적 신뢰구간이 아니다**.
- O2 이후 실제 reviewed contour 대비 interval coverage와 interval 폭을 함께 평가한다.
- 전체 ROI를 포함하는 넓은 interval로 coverage만 높인 결과를 정확한 측정으로 인정하지 않는다.

### 6.7 관측 가능성의 의미

O1의 `FrameOpticalObservability.status`와 `OilInterfaceWitness.decision`은 기존 설계대로 `NOT_EVALUATED`로 둔다.

**프레임 품질이 나쁘다는 측정과 계면이 물리적으로 관측 불가능하다는 판정은 같지 않다.** 노출 metadata가 없다는 사실만으로 현재 영상의 유효한 계면을 부정하지 않는다. 해당 취득 모드에 필수인 reference가 없으면 그 특정 channel을 unavailable로 처리한다.

관측 실패의 상태를 최소한 다음처럼 구분한다.

| 상태 | 뜻 |
|---|---|
| usable measurement | raw feature를 정해진 조건으로 측정함 |
| unavailable channel | 해당 band/reference/geometry가 없음 |
| unresolved identity | 후보는 있으나 계면인지 대안 구조물인지 구분 불충분 |
| localization ambiguous | 물리적 후보의 위치가 여러 곳 또는 넓은 범위에 있음 |
| no visible interface | human truth나 수용된 상태 계약에서 보이는 계면 없음 |
| unobservable under tested mode | 정해진 취득 모드에서 방어 가능한 판정 근거가 부족함 |

classifier의 `UNOBSERVABLE` 출력으로 human-visible 프레임을 평가 분모에서 제거하지 않는다. 모델이 놓친 것과 사람도 구분하지 못하는 것을 구분해야 한다.

### 6.8 성능과 debug 분리

Debug NONE에서는 신규 witness 측정·직렬화를 실행하지 않는다. BASIC/FULL에서는 현재 결정 이후 생성되는 sidecar로 연결한다.

frame-local cache는 동일한 X extent/profile을 재사용한다. trace는 기존 bounded K × 5 sectors × 3 scales × bounded peaks로 제한한다. full raster, 누적 frame history, 중복 dictionary 전체를 저장하지 않는다.

O1/O2 출력은 `PhaseDetection.debug_metrics`나 resolver가 읽는 candidate dictionary에 들어가지 않는다. trace namespace만 추가한다. JSON에는 NaN/Infinity를 허용하지 않으며 unavailable은 null과 이유로 나타낸다.

## 7. O2: 진단을 실제 의사결정 실험으로 바꾸기

O1의 목적은 trace를 더 길게 만드는 것이 아니다. 다음 세 가설을 한정된 실험으로 판정하는 것이다.

### H1 — 현재 영상에는 구분 가능한 정보가 있고 표현이 부족했다

같은 실제 계면의 정지·이동·밝기 반전 positive와, 반사·stripe·잔유 negative를 분리한다. 동일 Y 부근의 서로 다른 물체를 포함한다.

통과 조건은 calibration에서 고정한 operating point가 episode holdout에서 wrong-structure support를 억제하면서 실제 계면의 유효 coverage를 유지·개선하는 것이다. 모든 프레임에서 abstain하는 classifier는 통과하지 못한다.

### H2 — 후보 생성 단계에서 이미 실제 계면을 잃는다

Windows의 human-reviewed visible frame에서 모든 후보와 제거된 후보를 대상으로 recall funnel을 기록한다.

```text
실제 계면이 보임
 -> raw 후보 중 실제 계면 근처/동일 곡선 존재?
 -> hard validity 통과?
 -> representation/evidence 충분?
 -> authority 획득?
 -> 물리 tracklet 연결?
 -> phase allowed-set 포함?
 -> selector 선택?
 -> 같은 프레임 값이 정확하게 공개?
```

정답 contour 후보가 처음부터 없으면 authority threshold를 만지지 않는다. 별도의 proposal-lane 변경을 설계하고 용량·negative controls부터 검증한다.

### H3 — 현재 취득 방식에서 물리적 구분 정보가 부족하다

사람의 원본/시간 문맥 검토와 촬영 A/B 비교를 통해 판단한다. “trace feature로 구분 안 됨”만으로 원본 영상도 구분 불가라고 결론 내리지 않는다.

촬영 조건을 바꿔야 구분성이 생기면 acquisition contract를 추가한다. 새로운 RGB feature나 학습 모델에서도 holdout의 구분성이 확보되지 않으면, 근거 없이 threshold를 낮추지 않고 센싱 경계를 재검토한다.

### Positive / negative / unresolved controls

| 종류 | 필수 사례 |
|---|---|
| Positive | 정지한 실제 계면, 양방향 이동, 곡선, 낮은 contrast, texture가 높은 계면, 실제 이동 중 밝기 극성 반전, 부분 glare |
| Negative | 얇은 내부 stripe, 벽/피팅 edge, 정지·이동 반사, 잔유, splash, 동일 계측의 중복 source, full/empty 장면의 강한 구조물 |
| Unresolved | 반사와 계면이 겹침, 여러 contour가 동시에 가능, 유효 구간 부족, 넓은 위치 모호성, reference 등록 불량 |
| Localization-only | 실제 계면 근처지만 위치가 어긋난 candidate. 확정 artifact negative와 분리 |

합성 control은 정의한 현상의 메커니즘 검증이다. 실제 압축기 광학을 완전히 재현했다고 취급하지 않는다.

## 8. O3/O4에서만 바꿀 후단

### 8.1 물리 association

후속 association은 같은 X 구간의 contour displacement와 uncertainty를 비교해야 한다. 프레임마다 살아남은 구간이 바뀌어 scalar median Y가 이동한 현상을 실제 계면 이동으로 바로 해석하지 않는다.

등록 오차가 있는 acquisition에서는 배경/창 기준 이동과 계면 이동을 구분한다. 구간 대응이 없거나 competing structures가 있으면 unresolved를 유지한다. 극성 반전, source 이름, 단순한 시간 지속성은 identity를 단독으로 결정하지 않는다.

후단의 anchor와 continuation 구분은 보존한다. 새 witness에서 `UNRESOLVED`가 나왔다고 무조건 artifact로 재분류해서 모든 continuation을 제거하지 않는다. 기존 물리 owner의 제한된 연속 관측과 새 owner 확정을 별도 평가하되, 현재 프레임 후보가 없으면 숫자를 만들지 않는다.

### 8.2 authority/support

실제 계면에 texture가 있다는 이유로 broad material score가 일괄 veto되지 않게 만드는 방향은 타당하다. 그러나 texture threshold를 전체적으로 완화하는 대신, local interface support와 국소 contradiction의 정의를 검증한 뒤 적용한다.

어떤 두 source가 근처에 있다는 이유만으로 anchor를 승격하지 않는다. 현재 허용되는 동일-frame member와 lineage, physical support 조건을 명시한다.

### 8.3 phase / handoff

Accum의 owner 전환 문제는 새 physical owner에 대한 적격성 검증과 committed handoff가 필요하다. 임시 선택만 바꿔 두고 allowed-set에는 이전 owner가 남는 상태를 검증한다.

초기 FULL에서도 현재 계면이 명확한 경우, **현재 계면 관측**과 **하강 방향 확정**을 별도로 다루는 방향을 O4에서 검증한다. FULL barrier 삭제나 제한 없는 OPEN 복귀가 아니다.

R23의 밝기 반전 positive, 초기 EMPTY의 구조물 거절, FULL prefix/suffix의 무숫자 출력, Oil/Foam 분리 모두 유지해야 한다. [R1, R3–R6]

## 9. 업무 PC 내부 검증 설계

### 9.1 기본 보안 모드

반출 금지는 원본 영상만의 문제가 아니다. 상세 trace, crop, feature 배열, source hash, annotation, 모델 가중치, 요약 통계도 조직 정책의 적용을 받을 수 있다.

기본 실행은 네트워크를 사용하지 않는 로컬 runner로 한다. 별도 승인 없이 어떤 자료도 ChatGPT, GitHub, 개인 Mac, 클라우드 저장소로 전송하지 않는다. 필요한 코드·의존성·승인된 공개 가중치만 반입한다.

이번 검토는 이미 저장소에 존재하는 보고서만 읽었으며, 업무 PC의 private media를 원격 실행하거나 새로 반출하지 않았다.

### 9.2 라벨과 분할

라벨은 detector의 선택 결과나 candidate 위치를 보지 않은 원본 검토에서 우선 작성한다. 일부는 두 번째 검토자 또는 반복 검토로 불일치 수준을 측정한다. 불일치는 억지로 단일 정답으로 합치지 않는다.

로컬 manifest에는 다음을 구분한다.

```text
media identity / episode identity / source frame identity
canonical segment ID
target interface kind
physical label
per-sector contour or localization interval, when reviewed
annotation certainty and reviewer provenance
development / calibration / untouched holdout role
acquisition mode and available metadata
```

같은 episode의 인접 프레임과 photometric 변환은 같은 partition에 둔다. 창/조명/운전조건을 달리한 일반화를 주장하려면 그 축의 holdout도 별도로 둔다.

현재까지 반복해서 본 selected checkpoint는 회귀 검사이지 untouched holdout이 아니다. 원본 영상이 하나뿐이면 평가 가능한 일반화의 범위가 그 영상 안으로 제한됨을 명시한다.

### 9.3 모든 canonical segment 보고

다음 9개 구간은 빠짐없이 보고한다. 경계 시간은 기존 truth의 대략적 시간이며 frame-exact 정답으로 사용하지 않는다. [R6]

| Segment | 필수 의미 |
|---|---|
| `WS1-BASE-FULL-PREFIX` | numeric Oil/Foam 없음 |
| `WS1-BASE-DRAIN` | 하강 실제 계면, false structure와 miss 구분 |
| `WS1-BASE-RAPID-REFILL` | 빠른 상승 관측 후 계면 종료 |
| `WS1-BASE-FULL-SUFFIX` | 반사/하부 구조물로 owner가 넘어가지 않음 |
| `WS1-ACCUM-EMPTY` | numeric Oil/Foam 없음 |
| `WS1-ACCUM-ENTRY-SPLASH` | Oil 계면과 splash/잔유 분리, Foam 오검출 억제 |
| `WS1-ACCUM-FOAM-LAYERED` | 상부 Foam과 하부 Oil 독립 관측 |
| `WS1-ACCUM-POST-FOAM` | Foam 종료, 실제 Oil 유지 |
| `WS1-ACCUM-DRAIN` | 실제 하강 계면과 잔유 분리 |

### 9.4 지표

다음은 합격 숫자가 아니라 반드시 함께 보고할 지표 정의다.

- **Proposal recall:** human-visible 계면 중 실제 contour를 포함한 후보가 존재하는 비율. 판정 전 raw 후보와 각 pruning 이후를 분리한다.
- **지원 precision:** interface-supported 후보 중 물리적으로 실제 계면인 비율. 정답 근처의 다른 물체는 정답으로 세지 않는다.
- **최종 유효 coverage:** 실제 계면이 보이는 구간 중 올바른 계면을 허용오차 안에서 공개한 비율.
- **오검출:** no-interface 구간의 numeric 출력 및 visible 구간의 wrong-structure 출력. 비율, 횟수, 지속시간, 최장 연속 오검출을 함께 보고한다.
- **위치 오차:** reviewed contour가 있는 X 구간에 대해서만 px/mm 오차를 계산한다. scalar truth만 있는 구간에서 미검토 contour 오차를 만들어내지 않는다.
- **미검출:** 실제 계면이 보이는데 숫자를 내지 않은 시간과 최장 연속 gap.
- **불확실성:** interval coverage와 폭, abstention 비율, unobservable 오분류.
- **추적·상태:** identity split/merge, owner handoff, refill 종료, phase transition 지연.
- **성능:** source sampling 간격, 실제 처리시간, 메모리, trace 크기, debug NONE 대비 overhead.

불균일한 sampling이면 frame 비율과 시간 가중 비율을 함께 제시한다. 숫자를 낸 프레임의 정확도만 보고 coverage 저하를 숨기지 않는다. O1/O2의 shadow 수치는 production 정확도 개선으로 보고하지 않는다.

### 9.5 제품 허용기준

`ε_level_mm`, `C_min`, `F_max`, `T_gap_max`, 처리시간·메모리 예산은 제품 목적과 계측 분해능에 따라 정하고, holdout 확인 전에 고정한다. 근거 없이 99% 같은 합격률을 이 문서에서 발명하지 않는다.

요구치를 아직 정하지 못해도 O1 구현과 분포 측정은 진행할 수 있다. 다만 수치 성능의 최종 승인은 보류한다. 필수 safety negative에서 새 false numeric을 만드는 변경, 같은-frame provenance 위반, private case 분기는 수치 목표와 무관하게 불합격이다.

빠른 refill 구간에서는 실제로 몇 프레임을 관측했는지 확인한다. sampling을 늘리는 실험은 검출 알고리즘 변경과 별도 축으로 실행한다. 드문 sampling 때문에 놓친 것을 threshold 문제로 해석하지 않고, sampling 증가가 물리 identity를 보증한다고도 해석하지 않는다.

## 10. 촬영계 비교 실험

제품을 구매하거나 압축기를 개조하는 요청으로 해석하지 않는다. 아래는 안전·기구·광경로 검토 후 가능한 것만 비교하는 설계다.

| 모드 | 비교할 내용 | 선행조건 / 주의점 |
|---|---|---|
| A. 현재 영상 | 현재 기준선의 human visibility와 detector 오류 | 기존 시험과 동일한 입력·구간 |
| B. 고정 취득 | exposure/gain/focus/white balance/카메라 자세 고정 효과 | 고정 가능한 장비인지 확인. metadata 없음은 unknown |
| C. 제어 조명 | 확산 전면/측면, 가능한 경우 후면 조명의 계면 구분성 | 밝게만 만드는 것이 목표가 아님. glare 및 실제 계면 소실도 평가 |
| D. 편광/조명 pair | 반사 감소와 계면 보존을 동시에 비교 | 빠른 유동의 시차, 등록 오차, 편광으로 유효 계면 신호도 약해질 가능성 |
| E. structured background | 패턴 굴절·변위의 구분성 | 배경→유체→카메라 광경로와 유리/유체 보정 필요 |
| F. 독립 센서 | 특정 높이의 액체 존재 또는 별도 검증 | 압력·온도·유체·설치 호환성 필요. 연속 contour truth나 오일 농도 센서로 오인 금지 |

BOS는 굴절률 관련 변위를 측정하는 접근이다. 온도·농도·용기 광학 효과를 보정하지 않은 변위를 곧바로 액면이나 오일 성분으로 해석하지 않는다. 후면이 막힌 구조라면 E는 현재 fixture에서 부적용으로 기록하고 소프트웨어 필수조건에서 제외한다. [E4]

촬영 모드 비교는 가능한 한 동일한 운전조건·계면 상태에서 반복하고 순서 효과를 관리한다. 다른 cycle의 다른 액면을 조명 개선 효과로 오인하지 않는다.

## 11. 진행·중단 판정

| 관측 결과 | 다음 행동 | 하지 않을 행동 |
|---|---|---|
| 실제 후보가 충분하고 새 문맥으로 구분 가능 | O2 holdout 후 O3 support/association으로 이동 | 즉시 전체 phase threshold 변경 |
| 실제 후보 자체가 자주 없음 | 별도 proposal 생성/보존 개선 | selector로 없는 후보 복원 |
| 실제 계면 witness는 통과하나 allowed-set에서 차단 | 해당 phase/handoff 경로를 별도 수정 | unrelated optics feature 추가로 시간 소모 |
| raw 특징의 구분력이 부족하지만 사람이 반복 구분 가능 | domain label 확보 후 다른 공간·시간 표현 또는 오프라인 학습 평가 | “투명해서 원천 불가”라고 단정 |
| 취득 모드를 개선해야만 구분 가능 | acquisition contract와 함께 평가 | 현재 passive 조건의 threshold 완화 |
| 모든 시험 모드에서 요구 구간의 근거가 불충분 | 센싱 방식·측정 범위 재설계 | UNKNOWN을 임의 숫자로 채우기 |
| holdout이 너무 작거나 오염됨 | 증명 범위 제한, 새로운 episode로 구체적 검증 | 증강 91개를 91개 독립 검증 사례로 주장 |

O1을 끝없이 확장하지 않는다. 새 descriptor를 추가할 때마다 “어떤 positive/negative 쌍을 어떤 원리로 구분하려는지”를 기록하고, 같은 질문에 이미 답하는 필드와 중복시키지 않는다.

## 12. 구현 순서와 완료 기준

### O1 — typed extraction

기존 진단에 immutable witness와 bounded raw 측정을 추가한다. 완료 기준은 field 검출력 개선이 아니라 아래의 동작 불변성이다.

```text
debug NONE vs BASIC vs FULL
candidate count/order/source/Y/features/penalties/selected/rejected 동일
completed sequence / Oil / Foam / events / CSV 동일
기존 R22-2 diagnostic namespace 동일
신규 namespace만 추가
정확한 coordinate join / missing / finite JSON / bounds 검증
```

### O2 — shadow discrimination

라벨과 partition을 먼저 고정하고 positive/negative/unresolved control을 만든다. calibration에서 operating point를 고정한 다음 Windows 내부 holdout을 평가한다. 결과가 production으로 유입되지 않도록 차단한다.

### O3 — support / physical association

O2의 실제 구분력이 확인된 뒤 typed witness를 authority·association에 연결한다. 불확실한 위치를 잘못된 이동으로 해석하지 않는지, duplicate lineage가 가짜 corroboration을 만드는지 검증한다.

### O4 — handoff / observation-vs-phase

Accum owner handoff와 초기 FULL에서의 direction-neutral observation을 별도 변경으로 검증한다. 두 문제를 하나의 대규모 리팩터링에 묶지 않는다.

### O5 — Windows qualification

exact candidate runtime, 모든 canonical segment, error/coverage/false-run/throughput에 대한 실검증을 완료해야 한다. O1/O2의 local PASS나 기존 fingerprint 일치는 field qualification이 아니다.

각 단계는 실패 시 직전 수용 상태로 돌아갈 수 있어야 한다. O1/O2 rollback은 sidecar 제거이며, R22-2 판단은 동일해야 한다.

## 13. 이번에 완료한 일과 남긴 경계

### 완료

- GitHub와 Mac checkout에서 동일 HEAD 및 clean 상태 확인.
- 현재 work-plan, logic map, failure registry, reviewed truth, R22 causal findings, 기존 O1 architecture/validation 검토.
- 실제 측정 함수와 debug 호출부 및 공개 probe 코드 확인.
- 공개 연구·상용 1차 자료를 대조하여 적용 가능성과 비적용 범위 구분.
- 91개 공개 frame/transform probe를 재실행하여 기존 결과의 전체 해시 재현.
- 관련 기존 단위 테스트 14개 PASS 및 `git diff --check` PASS.
- 본 실행 명세서 작성.

### 이번에 하지 않은 일

- production detector 수정 또는 새 R번호 부여.
- O1/O2 구현 완료 주장.
- 4개 영상 전체의 completed-window behavioral replay 및 전체 canonical/Qt suite 재실행.
- private Windows 영상 접근, 신규 현장 추적, private 데이터 반출.
- checkpoint 좌표를 기준으로 threshold 학습.
- commit, push, merge 또는 기존 골든 변경.

따라서 이번 산출물은 **재설계 경계를 확인하고 다음 구현을 구체화한 명세서와 공개 기준선 재현 결과**다. 현장 검출력이 개선되었다는 결과 보고서는 아니다.

## 14. 참고 자료

저장소 링크는 모두 검토 기준 커밋에 고정했다. 외부 링크는 2026-09-17 확인 범위다.

### 저장소 근거

- [R1: Current Work Plan](https://github.com/teeeeooo/oil_level_tracker/blob/577f98af116e7f59b07bc8a8356606c4dd7f9bea/docs/00-project/work-plan.md)
- [R2: Transparent-Interface Detector Direction Assessment](https://github.com/teeeeooo/oil_level_tracker/blob/577f98af116e7f59b07bc8a8356606c4dd7f9bea/docs/50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md)
- [R3: R22 Reviewed Interface Causal Findings](https://github.com/teeeeooo/oil_level_tracker/blob/577f98af116e7f59b07bc8a8356606c4dd7f9bea/docs/50-diagnostics/s11/s11-r22-reviewed-interface-causal-findings.md)
- [R4: Current Detector Logic Map](https://github.com/teeeeooo/oil_level_tracker/blob/577f98af116e7f59b07bc8a8356606c4dd7f9bea/docs/20-architecture/s11-current-detector-logic-map.md)
- [R5: Detector Mechanism Failure Registry](https://github.com/teeeeooo/oil_level_tracker/blob/577f98af116e7f59b07bc8a8356606c4dd7f9bea/docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md)
- [R6: Canonical Windows Reviewed Truth](https://github.com/teeeeooo/oil_level_tracker/blob/577f98af116e7f59b07bc8a8356606c4dd7f9bea/docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
- [R7: oil_interface_diagnostics.py](https://github.com/teeeeooo/oil_level_tracker/blob/577f98af116e7f59b07bc8a8356606c4dd7f9bea/src/oil_tracker/adapters/vision/oil_interface_diagnostics.py)
- [R8: phase_frame_detection.py](https://github.com/teeeeooo/oil_level_tracker/blob/577f98af116e7f59b07bc8a8356606c4dd7f9bea/src/oil_tracker/adapters/vision/phase_frame_detection.py)
- [R9: Public Probe Summary](https://github.com/teeeeooo/oil_level_tracker/blob/577f98af116e7f59b07bc8a8356606c4dd7f9bea/docs/50-diagnostics/s11/s11-interface-witness-public-probe-summary.json)
- [R10: Existing Witness Architecture](https://github.com/teeeeooo/oil_level_tracker/blob/577f98af116e7f59b07bc8a8356606c4dd7f9bea/docs/20-architecture/s11-interface-observability-witness-architecture.md)
- [R11: Existing Witness Validation](https://github.com/teeeeooo/oil_level_tracker/blob/577f98af116e7f59b07bc8a8356606c4dd7f9bea/docs/30-validation/s11-interface-observability-witness-validation.md)

### 외부 1차 자료

- [E1: Eppel & Kachman, 2014 — Computer vision-based recognition of liquid surfaces and phase boundaries in transparent vessels](https://arxiv.org/abs/1404.7174)
- [E2: Eppel, 2015 — Using curvature to distinguish between surface reflections and vessel contents](https://arxiv.org/abs/1506.00168)
- [E3: Wang et al., ECCV 2024 — TCLD 저자 공개 저장소 / README](https://github.com/dualtransparency/TCLD)
- [E4: Verso & Liberzon, 2015 — Background Oriented Schlieren in a Density Stratified Fluid](https://arxiv.org/abs/1506.08889)
- [E5: IVC — Monitoring Liquid Levels in Reactor Vessels with Video Analytics, revision 2024-08-22, pp. 1–2](https://ivcco.com/wp-content/uploads/IVC-App-Note-Video-Analytics-Sight-Glass.pdf)
- [E6: KEYENCE — Fill-Level Inspection for the Food and Beverage Packaging](https://www.keyence.com/products/vision/industries/food-beverage-packaging/fill-level-inspection.jsp)
- [E7: Copeland — HVAC Oil Controls](https://www.copeland.com/en-in/products/valves-controls-and-system-protectors/oil-controls)

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R22 typed ownership/evidence, R22-2 native-path diagnostics, the public observability probe, corrected BASE/Accum checkpoints, rejected R23 polarity-only association, canonical Windows truth, existing O1 architecture and validation.
- Prior mechanisms rejected: scalar threshold widening, polarity/source/motion-only identity, duplicated lineage votes, private-coordinate tuning, missing-as-zero, uncertainty-based exclusion of visible misses, unbounded trace expansion, stale coordinate/owner transfer and downstream interpolation.
- Preserved contracts: generic bounded detector; selected same-frame provenance; independent Oil/Foam; coordinate-free FULL/EMPTY; fail-closed ambiguity; separate target-Windows acceptance.
- Difference from prior failures: separates measurement target, proposal recall, physical discrimination, localization uncertainty and phase admission; defines offline evaluation and explicit decision experiments rather than adding unbounded diagnostics or fitting a new threshold to selected checkpoints.
- Logic-map impact: NONE — this standalone execution proposal does not change runtime ownership or production code.
- Failure-registry impact: NONE — this document refines responses to existing mechanisms and claims no newly proven private-field cause.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: segment-specific. Public sampled-frame evidence supports high geometric proposal recall with unresolved physical discrimination. Corrected private checkpoints separately expose contour-localization/association uncertainty and phase allowed-set exclusion; full private intervals remain unproven.
- Logic-map impact: NONE — no executable behavior changed in this review.
- Failure-registry impact: NONE — no historical truth is rewritten, and FIELD FAIL remains unchanged.
