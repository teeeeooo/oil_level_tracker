# S11 전수 감사 및 Detector 개선 작업 명세서

> 기준: `teeeeooo/oil_level_tracker`, `main@9f41d2f8a517da21f570f57ed1b4e2009a9d48db`  
> 감사일: 2026-10-07, Asia/Seoul  
> 성격: 현행 S11/W4의 보완 감사와 후속 구현 명세. 새 작업계획의 병렬 소유자가 아니다.  
> 판정: **S11 계속 ACTIVE / FIELD FAIL 유지 / W4 OPEN / O2 미승격 / W5·O3 이후 조건부**  
> 작업 방식: 로컬 저장소·영상 직접 읽기, 현행 코드 실행, 별도 프로세스의 반증 실험. 운영 코드·정답·레시피·기존 문서·golden 수정 없음.

## 0. 결론과 바로 이어갈 작업

**전체 detector를 다시 만드는 것보다, `영상 증거 → 물리적 경계 권한` 사이의 계약을 제한적으로 재설계하는 것이 우선이다.** 후보 생성·시간축 추적·상태기계·출력 검증을 한꺼번에 갈아엎을 근거는 부족하다. 반대로 현재 단일 점수와 기존 특징의 이름을 유지한 채 문턱만 조정하는 접근도 충분하지 않다.

이번 감사에서 가장 중요한 판단은 다음과 같다.

| 판단 | 근거 | 조치 |
|---|---|---|
| 현행 canonical은 아직 green이 아니다. | 2,313개 중 2,310 통과, 3 실패. 두 지문 실패는 진단 추가/이유 정정에 따른 비교 범위 문제로 해당 fixture에서 분리 재현했고, 나머지는 인코딩 명시 누락이다. | 진단을 무시하는 전역 필터나 golden 재작성 대신, 동작 회귀와 버전별 진단 계약을 분리해 수리한다. |
| 재현·출력 출처 관리와 실제 물리적 정답은 별개다. | 4개 영상의 현행 재생성 결과는 모두 같은 프레임 후보 출처를 보존하지만, 기존 정답 좌표와 상당한 차이가 나는 사례도 남는다. | 재현 성공을 검출 성공으로 보고하지 않는다. |
| 일부 phase-scan 특징은 이름이 암시하는 독립된 증거가 아니다. | 측정 가능한 sector 비율을 수평 경계 지지도로 쓰고, 같은 밝기 차이를 broad와 narrow 양쪽에 넣는다. 단순 기울기도 구성한 지지 문맥에서 anchor가 된다. | 측정값의 의미·유효성·출처를 분리하고, 그다음 admission 정책을 바꾼다. |
| 현재 paired-edge 표현은 같은 방향의 두 기울기와 반대 방향의 복귀 기울기를 구별하지 못할 수 있다. | 새 4개 계측 반례에서 legacy 요약이 동일했다. 기존 opposite-sign 단독 수정은 안전 반례를 깨뜨려 이미 기각됐다. | 기존 artifact 점수를 먼저 빼지 않는다. 두 현상을 별도 계측하되 texture/optical opposition을 보존한다. |
| Y821 사례는 중요한 진단점이지만, 모든 운영 조건의 대표 실패가 아니다. | 같은 수정 ROI·같은 frame420에서 30fps는 Y821, 2fps는 Y852를 선택했다. | 30fps 진단, 2fps 운영 재생, 시작 이전 문맥을 각각 고정하여 평가한다. |
| source-family 권한을 통째로 낮추는 것은 해결책으로 채택할 수 없다. | 30fps 진단에서는 Y821→Y852였지만 다른 후보다. 4영상 합계 Oil 162행은 같으면서 sample2 frame60 관측이 사라졌다. 조건부 MAE 개선도 이 누락을 숨겼다. (§6) | 이 변경은 인과관계 실험으로만 보관하고 제품에 넣지 않는다. |
| Foam 영역 발견과 Foam 상단 경계 소유권이 분리되어야 한다. | rim 제거 후에도 Foam과 중앙 구조가 섞인 component의 상단 극값이 선택될 수 있다. | component 유지와 local front 사용 가능 여부를 별도로 판정한다. |

**먼저 §11의 `W4-A0B: canonical 기준 정리`로 현재 3개 테스트 실패를 닫고, 그다음 `W4-A1: 증거 의미의 손실 없는 분리`를 진행한다.** A1은 현재 출력과 모든 기존 결정을 그대로 보존하는 계측 변경으로 끝낸다. 이어서 `W4-A2`에서 단 하나의 candidate-identity challenger를 평가한다. 새로운 classifier도 없는데 Windows 반복 실행·재라벨링·descriptor 확장을 먼저 요구하지 않는다.

### 이번에 실제로 수행한 것과 하지 않은 것

- 수행: 저장소와 S11 소유 문서·현재 실패 이력 검토, vision 모듈 전수 목록/구조 조사, 4개 원본 MP4와 12개 입력 pin 확인, 13개 기존 정답 프레임 재디코딩·직접 시각 검토, debug on/off 쌍 검출, 4영상 애플리케이션/보고서 재생, 합성 계측 반례, 121프레임 resolver 반사실 실험, 동일 ROI의 sampling/prefix 실험, 별도 4영상 반사실 재생, canonical 테스트 실행.
- 미수행: 보안 Windows 원본의 직접 열람, 새 독립 holdout에 대한 평가, classifier 학습·운영점 선택, 제품 코드 수정·배포, 현장 합격 판정, 사람의 새 정답 판정 생성.
- 새 샘플의 존재를 추측하거나 기존 영상의 다른 프레임을 독립 holdout으로 둔갑시키지 않았다. 사용자 제공 예정인 별도 영상의 기존 계획을 유지한다.

---

## 1. 감사 범위와 기준 고정

### 1.1 저장소·환경

| 항목 | 실제 확인값 |
|---|---|
| 로컬 경로 | `/Users/sunjaekim/Developer/oil_level_tracker` |
| 기준 HEAD | `9f41d2f8a517da21f570f57ed1b4e2009a9d48db` |
| 브랜치 | `main`; 시작 시 `origin/main`과 일치 |
| 시작 작업트리 | clean |
| 추적 파일 | 756개: `src` 216, `tests` 249, `docs` 259, 기타 32 |
| vision 모듈 | 44개, 24,399행, AST상 함수/메서드 667개 |
| 실행 환경 | Python 3.14.4 / OpenCV 4.14.0 / NumPy 2.5.1 / pytest 9.1.1 |
| 플랫폼 | macOS 26.6.2, arm64; PySide6/Qt 6.11.1 |
| 새 실험 위치 | `/tmp/s11-audit-20261007-vaUpfB/` |
| 보존 확인 | 2026-10-07 00:44:41 KST 종료 검증: HEAD 동일, 작업트리 clean, 추적 756개 파일 전부 SHA-256 동일, 원본 12개 corpus pin 및 별도 sequence 입력 모두 동일 |

`전수`는 전체 파일·vision 모듈 목록, 현행 logic-map의 모든 노드, failure-registry의 모든 실패군, 현재 W/O 단계 및 canonical 테스트 선택을 대상으로 한다. 756개 파일의 모든 행을 사람이 읽듯 정독했다는 뜻은 아니다. 수동 심층 코드 검토는 원인과 직접 관계된 생성기·증거 변환·authority·resolver·Foam·출력 경로에 집중했다. 부록 C의 모듈 목록과 §5의 테스트 결과가 실행 범위를 구분한다.

프로젝트 도구의 환경 요약에 나타난 일반 Python 설정과 달리, 저장소의 `.venv/bin/python`은 정상 사용 가능했다. 테스트와 영상 분석은 이 환경으로 실행했다. 일반 환경에서 실행할 수 없다는 이유로 감사를 중단하지 않았다.

### 1.2 원본 입력의 범위

| 영상 | 원본 크기(byte) | 현행 고정 재생 구간 | 2fps 출력 행 |
|---|---:|---|---:|
| `base_sample_1.mp4` | 12,408,143 | 0–14.4초 | 30 |
| `sample2.mp4` | 1,970,224 | 0–2초 | 5 |
| `sample3.mp4` | 10,001,682 | 30.03–105초 | 151 |
| `sample4.mp4` | 16,224,936 | 0–56초 | 113 |

전체 재생은 299행이다. 원본 전체를 모든 프레임에서 정답 판정한 것은 아니며, 기존 고정 qualification window를 재사용했다.

입력 identity는 파일명만 확인한 것이 아니다. 저장소 manifest의 MP4·`.oilrecipe`·`.oiltruth` **12개 SHA-256**을 대조했다. 원래 recipe는 그대로 두었다. 사람이 수정한 sample4 ROI는 기존 별도 파일 `sample/output/s11-local-human-roi-comparison-001/sample4-human-roi.oilrecipe`를 진단 실험에서만 사용했다.

> **주의:** 이 네 영상은 이미 반복 검토된 개발/회귀 자료다. 신규 성능 일반화나 독립 검증의 증거로 승격할 수 없다.

---

## 2. 현행 S11 단계 감사

현재 상태 소유자는 `docs/00-project/work-plan.md`다. `roadmap.md`나 과거 감사 문서의 오래된 계획을 우선하여 단계를 재개하지 않는다. 아래는 이 감사 시점의 해석이며, live ledger를 변경한 것이 아니다. [S01–S05]

| 단계 | 현행 상태 | 감사 판단 / 다음 진입 조건 |
|---|---|---|
| O1 | interface witness 추출 로컬 구현·검증 | 원인 추적 기능이다. 물리적 정답 자체를 만드는 기능은 아니다. |
| W0 | 기존 O2 fixed-profile Windows 결과 확인 후 미승격 종료 | 반복 실행만으로 재개하지 않는다. |
| W1 | target/aggregation 계약과 반례 정리·검증 | 실제 경계인지와 추적할 최상위 실제 유체 경계인지를 분리한 방향을 유지한다. |
| W2 | bounded scene/geometry review 종료 | 동일 geometry 질문·native-path 존재 확인을 다시 요청하지 않는다. |
| W3 | 출력/evaluator 분리 및 target/context 연결 검증 | 수치 정답이 없는 레코드에 임의 Y 오차를 부여하지 않는다. |
| W4 | 여러 appearance 실험 미승격 종료; candidate-identity challenger OPEN | 지금의 핵심 단계다. 손실 없는 계측 분리와 검증 가능한 challenger가 필요하다. |
| O2 | acceptance OPEN | 독립 역할 분리·고정 운영점·정해진 Windows shadow 평가가 아직 닫히지 않았다. |
| W5 / O3 | 제안 단계, gated | 시간축 지원/association 개선을 O2 통과로 착각하지 않는다. 먼저 identity 효과를 보인다. |
| W6 / O4 | 제안 단계, gated | handoff/phase 변경은 W5 이후에 한다. |
| W7 / O5 | 대기 | 통합 후보의 현장 검증이 필요하다. 현재 FIELD FAIL을 유지한다. |

### 2.1 이미 정리된 증거를 다시 미결로 돌리지 않을 것

기존 Windows review의 75개 candidate는 13개 physical interface와 62개 non-interface로 나뉘며, 실제 추적 target은 10개, 실제 경계이지만 target이 아닌 것은 3개다. 다만 group judgment와 개별 judgment가 섞여 있다. 이를 75개의 독립 관측 표본처럼 취급하면 안 된다. 현재 이 묶음에는 challenger 예측에 근거한 성공 판정이 붙어 있지 않다. [S01, S04]

기존 region-model 실험의 **30/36 model-order mismatch**는 모델의 loss 순서가 기대와 다른 결과다. `83.3% 검출 오차율`이나 `83.3% identity 정확도`가 아니다. 모델 순위를 바꿔서 identity를 해결하려던 해당 실험은 이미 미승격으로 닫혔다. [S01, S04]

현재 target의 핵심은 최상위 **실제 유체 경계**이며, 단순히 가장 위의 밝은 선이나 항상 Oil이라고 이름 붙인 재료가 아니다. Accum의 내부 실제 경계도 target이 아닐 수 있다. Foam은 별도의 관측 계열이다. sample4의 확인된 Oil–Foam 위치와 Foam–air 위치를 하나의 Y로 합치지 않는다.

---

## 3. 기존 문서와 이 명세의 관계

| 문서 | 유지할 역할 | 이 문서와의 관계 |
|---|---|---|
| `docs/00-project/work-plan.md` | 현재 작업 상태·다음 행동의 단일 소유자 | 변경하지 않았다. 승인된 후속 작업만 짧게 연결한다. |
| `docs/00-project/roadmap.md` | 프로젝트 단계 수준 안내 | 본 감사로 S11 완료나 W5 착수를 표시하지 않는다. |
| `docs/20-architecture/s11-current-detector-logic-map.md` | 현재 runtime 소유 경로 | 현재 경로를 감사했다. 제안 경로를 이미 구현된 것처럼 쓰지 않는다. |
| `docs/30-validation/s11-detector-change-governance.md` | 변경·검증·증거 보존 규칙 | 그대로 적용한다. |
| `docs/30-validation/s11-interface-observability-witness-validation.md` | O 단계·witness 계약 | O2 이후 진입 조건을 완화하지 않는다. |
| `docs/30-validation/s11-behavioral-lifecycle-and-foam-witness-validation.md` | 보호할 behavioral 계약 | identity 개선을 이유로 기존 lifecycle·publication 계약을 약화하지 않는다. |
| `docs/50-diagnostics/s11/s11-detector-improvement-audit-and-work-spec-2026-10-01.md` | 이전 전반 감사와 설계 근거 | 상위 방향을 계승한다. 다시 시작하는 R 번호를 만들지 않는다. |
| `docs/50-diagnostics/s11/s11-w4-progress-audit-and-continuation-plan-2026-10-01-ba1bd6a.md` | 당시 W4 후속 조건 | 이후 수집된 ROI·identity·authority 증거와 이번 실행 결과로 구체화한다. |
| `docs/50-diagnostics/s11/2026-10-06-foam-structure-reference-audit.md` | 최신 local geometry/structure/authority 조사 | 사실·사람의 판정을 보존한다. 30fps 결과의 적용 범위와 신규 반증을 보완한다. |
| 본 문서 | 2026-10-07 고정 HEAD 감사와 W4 세부 실행 명세 | 기존 문서를 대체하지 않는 보완 명세. `W4-A*`는 기존 W4 안의 작업 단위다. |

진행 중인 문서의 이동·압축·아카이브 작업은 이 감사에 포함하지 않았다. 과거에 실패한 문서를 지워서 이번 변경이 처음 시도되는 것처럼 보이게 하지 않는다.

---

## 4. 원본 영상 직접 확인

13개 사용 가능한 기존 scalar annotation의 실제 source frame을 다시 디코딩했다. decoder frame 전후 위치를 확인하고, ROI 원본 PNG와 검토용 contact sheet를 새로 저장했다. 별도로 sample4 frame410/420/450/480의 기존 원본 crop도 직접 확인했다. 영상 설명은 아래 범위의 시각적 관찰이며 새 정답 라벨이 아니다.

| 영상 | 직접 보이는 특징 | 감사상 의미 |
|---|---|---|
| Base | 낮은 대비의 유리 내부. frame156/240 원본에는 빨강·초록 설명선이 이미 인코딩되어 있다. | 추가 overlay를 그리지 않았어도 원본 자체가 순수 광학 장면은 아니다. 해당 legacy truth의 시각적 충돌을 무시하지 않는다. |
| sample2 | 미세 기포/질감이 넓게 분포하고 밝은 띠와 실제 계면 후보가 인접한다. | 밝은 띠 하나, texture 존재 하나로 Oil/Foam identity를 확정하기 어렵다. 기존 사람의 candidate 판정을 유지한다. |
| sample3 | 초기 흐린 경계와 이후 색·질감이 강한 영역이 한 영상 안에서 바뀐다. | 고정 밝기 방향이나 단일 appearance 조건으로 전체를 설명하는 설계는 보호 사례를 놓칠 수 있다. |
| sample4 | 104×104 원본 ROI 안에 외곽 rim, 내부 곡선/구조, 밝은 물질 영역과 낮은 유체 경계가 공존한다. | 넓은 component 하나를 선택해 상단 극값을 반환하는 것만으로는 혼합된 지지의 identity가 보장되지 않는다. |

Contact sheet는 보기 위한 최근접 확대이며 새로운 해상도나 세부 정보를 생성하지 않는다. 비정방형 crop은 표시를 위해 정방형으로 배치되므로 정밀 위치 측정에는 원본 PNG와 source 좌표를 사용한다. 화면의 빨강·초록 선은 이 감사가 추가한 detector 정답선이 아니다.

### 4.1 동일 프레임 후보 존재와 raw 최종 선택

매 프레임 fresh detector로 `debug=False`와 `debug=True`를 각각 실행했다. **13/13의 반환 detection 전체가 동일**했다. 이 검사는 디버그 기능에 따른 결과 변경을 검사하며, 시간축 품질이나 물리적 정확도를 검사하는 것은 아니다.

| 영상 / frame | 기존 truth Y | raw Oil Y | Oil 후보 수 | 가장 가까운 후보 Y | 좌표 거리(px) |
|---|---:|---:|---:|---:|---:|
| Base / 144 | 386 | 395 | 22 | 387 | 1 |
| Base / 156 | 386 | 없음 | 24 | 387 | 1 |
| Base / 240 | 386 | 없음 | 25 | 387 | 1 |
| sample2 / 0 | 592 | 없음 | 26 | 594 | 2 |
| sample2 / 30 | 592 | 없음 | 28 | 592 | 0 |
| sample2 / 60 | 592 | 없음 | 27 | 593 | 1 |
| sample3 / 900 | 316 | 319 | 25 | 317 | 1 |
| sample3 / 1035 | 243 | 245 | 23 | 243 | 0 |
| sample4 / 0 | 860.5 | 없음 | 23 | 861 | 0.5 |
| sample4 / 450 | 852.5 | 없음 | 24 | 853 | 0.5 |
| sample4 / 900 | 848.5 | 848 | 23 | 848 | 0.5 |
| sample4 / 1470 | 855 | 없음 | 20 | 863 | 8 |
| sample4 / 1680 | 858.5 | 없음 | 23 | 854 | 4.5 |

이 결과로 모든 문제가 후보 부족이라고 볼 수는 없다. 그러나 모든 후보 생성 문제가 해결됐다고 볼 수도 없다. 특히 뒤의 두 sample4 프레임은 nearest distance부터 다른 양상이다. 가장 가까운 후보라는 이유로 해당 후보의 물리적 identity를 truth에서 자동 복사해서는 안 된다. 이 표는 후보 존재/위치와 선택 문제를 분리하기 위한 것이다.

---

## 5. 현행 코드의 새 실행 결과

### 5.1 canonical 테스트

| 선택 | 통과 | 실패 | 반대 선택 제외 | 실행 시간 |
|---|---:|---:|---:|---:|
| `not qt_app` | 2,056 | 3 | 254 | pytest 1,259.95초 |
| `qt_app` | 254 | 0 | 2,059 | pytest 57.44초 |
| 합집합 | **2,310** | **3** | 중복 없음 | 동시 실행 실험이 있어 성능 benchmark로 사용하지 않음 |

JUnit의 `(classname, name)` 집합은 2,059개와 254개이며 **교집합 0, 합집합 2,313**이다. 실패 관련 두 파일만 새 프로세스에서 다시 실행해도 **3 failed / 4 passed**였다. 테스트 순서·전체 suite의 앞선 상태만으로 발생한 실패는 아니다.

#### 실패 F-A: current-frame characterization fingerprint

`tests/test_r16_refactor_characterization.py:270`의 기대값은 `b9770bca…`, 실제값은 `de186867…`였다. commit `b559a11`의 trace-only 추가 두 항목인 `artifacts.state.foam_component_diagnostics`와 `artifacts.images.foam_component_labels`만 비교 payload에서 제외했더니 **기존 전체 fingerprint `b9770bca0b310ff1881c7e9cf3e67fb838ce39cb04059ef9615d3071b9b4ffee`와 정확히 일치**했다. namespace 하나만 제외했을 때는 일치하지 않아, image 추가도 원인임을 구분했다.

이는 이 fixture에서 기존 detection·candidate·score·기존 image/state가 그대로라는 증거다. 진단 제외 코드는 감사 프로세스 안에서만 실행했고 테스트 파일은 수정하지 않았다. 새로운 진단 자체를 검사하는 별도 계약은 계속 필요하다.

#### 실패 F-B: completed-window characterization fingerprint

`tests/test_r16_refactor_characterization.py:322`의 기대값은 `34775284…`, 실제값은 `a4e58877…`였다. 직전 HEAD의 `evaluate_phase_identity` 함수만 별도 프로세스에서 실행하면 **기존 test 전체가 통과**하고 기대 지문과 정확히 일치했다. 새 함수와 이전 함수의 보호 payload 차이는 11프레임 중 3–7번 프레임의 **20개 leaf 값**뿐이다. 전부 4종의 `*_failed_gates` 이유 문자열에 `boundary_advantage`가 추가된 것이다. 다른 leaf 차이는 없었다.

따라서 이 fixture의 실패는 최신 reason 정정이 behavior snapshot에도 포함된 문제로 좁혀졌다. 최신 이유를 이전의 잘못된 이유로 되돌려 제품을 수정하라는 뜻이 아니다. 현재 이유의 정확성을 검사하면서, 열거된 진단 필드와 behavior의 동등성을 각각 검증하는 수리가 필요하다. 모든 키에 대한 `failed_gates` 전역 삭제나 expected hash 교체로 넘어가면 안 된다.

#### 실패 F-C: 테스트 text I/O의 encoding 누락

`tests/test_test_authoring_policy.py:42`가 찾은 호출은 다음 5개다.

```text
tests/test_foam_component_diagnostics.py:86:read_text
tests/unit/test_s11_foam_front_alternatives.py:131:write_text
tests/unit/test_s11_foam_front_alternatives.py:133:write_text
tests/unit/test_s11_foam_front_alternatives.py:137:write_text
tests/unit/test_s11_foam_front_alternatives.py:151:read_text
```

해당 테스트 fixture의 UTF-8 계약을 확인하고 각 호출에 명시적 encoding을 부여하는 테스트 유지보수 작업이다. 정책 테스트를 비활성화할 이유는 없다. 이번 감사에서는 5개 호출을 고치지 않았으므로 **최종 canonical 판정은 여전히 3 failed**다.

이 진단은 `canonical_failure_diagnosis.json`, `diagnose_canonical_failures.py`, `failure-rerun.xml/log`에 보존했다. 진단-only 불일치를 원인별로 분리했다는 사실과 canonical이 아직 실패 중이라는 사실을 동시에 기록한다.

실행 선택은 `not qt_app`과 `qt_app`의 서로 다른 두 집합이다. 같은 node를 중복 합산하지 않았다. 이번 canonical 결과는 **운영 코드가 변경되지 않은 baseline**의 결과다. 아래 임시 ablation의 제품 적합성을 의미하지 않는다.

### 5.2 4영상 애플리케이션·보고서 재생

기존 고정 구간, 2fps, 명시적 UNKNOWN 초기 상태를 사용했다. `AnalysisPipeline`과 `OutputBundleStore`를 통과시켜 CSV/그래프/보고서 bundle을 새로 만들었다. 영상별 새 프로세스를 사용했다.

| 영상 | 전체 행 | Oil 수치 행 | Foam 수치 행 | 기존 scalar truth 중 수치 반환 | 수치가 있는 truth의 MAE(px) |
|---|---:|---:|---:|---:|---:|
| Base | 30 | 28 | 0 | 3/3 | 12.333 |
| sample2 | 5 | 4 | 0 | 2/3 | 6.500 |
| sample3 | 151 | 29 | 5 | 2/2 | 12.750 |
| sample4 | 113 | 101 | 26 | 4/5 | 7.625 |
| 합계 | **299** | **162** | **31** | **11/13** | 합산 정확도로 사용하지 않음 |

모든 Oil 수치 행에서 same-frame provenance가 확인됐고, 해당 provenance 누락은 **0**이었다. 반면 truth 대비 sample3 frame900의 좌표 차이는 24.5px, sample4 frame1470은 22px였다. 숫자가 많이 나온다는 것과 올바른 계면을 잡는다는 것은 다르다.

위 MAE는 다음 이유로 field accuracy가 아니다.

1. 보류된 두 truth 사례를 제외한 조건부 오차다. 수치 반환률과 반드시 함께 읽어야 한다.
2. 기존 evaluator는 정답 시점에서 가장 가까운 2fps 출력 행을 사용한다. Base frame144와156은 둘 다 5.005초의 같은 행과 비교됐다. 정밀 exact-frame localization 결과와 혼용하면 안 된다.
3. 원본 설명선과 사람의 최신 의미 판정이 충돌하는 Base annotation 등은 이미 시각적 한계가 기록되어 있다.
4. 네 영상은 모두 노출된 회귀 자료다. 전체 영상의 모든 구간에 밀집된 독립 정답이 있는 것이 아니다.

### 5.3 fingerprint를 다룬 방식

| 영상 | 이번 tracking SHA-256 |
|---|---|
| Base | `5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7` |
| sample2 | `85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976` |
| sample3 | `feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1` |
| sample4 | `e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1` |

이번 custom runner는 현행 HEAD를 **characterization**하기 위해 historical fingerprint expectation을 넣지 않았다. 그러므로 이 실행을 `historical golden PASS`로 표현하지 않는다. 기존 R18 helper의 sample4 `0f202947…`을 새 값으로 덮어쓰지도 않았다. 같은 문자열이 나오는 세 영상과, 다른 이력이 있는 sample4를 분리해 보존했다. 현재 입력 pin과 현재 실행 산출물의 출처는 별도로 확인했다.

이번 실행의 runtime fingerprint는 `7b14134e3f811d06e45ea2cd44686b5ffedd22dc7e2848fd2e04bd838f8aa20d`이고 decoder는 FFMPEG다. OpenCV build SHA-256은 `c201b5ba726b7370afc3cb0d338454e2964afe1aa907849908b27850ecc043cf`다. 비교할 historical runtime expectation을 지정하지 않았으므로 helper의 exact reproducibility 상태는 `TRACKING_UNVERIFIED`이다. 이는 source/입력 pin 미확인을 뜻하지 않고, 과거 runtime·golden과의 정확한 동등성 승격을 하지 않았다는 뜻이다.

---

## 6. 가설 설정과 반증 실험

### H1. “phase-scan의 높은 coverage는 경계가 넓게 지지됨을 의미한다”

**그대로는 성립하지 않는다.** `_phase_transition_profile`은 5개 sector에서 상하 band의 유효 픽셀이 충분한 sector 수를 세고 이를 `coverage`로 반환한다. 해당 sector에 연결된 실제 계면이 있는지를 세지 않는다. 단색 입력에서도 중앙 coverage는 1.0이고 response는 0이다. 단색에서 후보가 안 나오는 방어는 별도로 존재한다. [S07]

새 실험은 6가지 appearance를 양·음 두 방향으로 만들어 총 12개 입력을 사용했다. glare/static map은 없고, phase-scan 입력에는 CLAHE 대신 원 gray를 그대로 넣어 이 생성기의 의미만 분리했다.

| 합성 appearance | 방향별 후보 수 | 중앙 response / coverage / scale consistency | 구성 문맥에서 anchor 수(방향별) |
|---|---:|---|---:|
| 단색 | 0 | 0 / 1 / 0 | 0 |
| 일정한 수직 밝기 기울기 | 3 | 약 0.4354 / 1 / 0.6667 | 3 |
| 국소적인 완만한 step | 3 | 0.6875 / 1 / 0.6667 | 3 |
| 선명한 step | 1 | 1 / 1 / 1 | 1 |
| 밝아졌다 원래 값으로 돌아오는 띠 | 2 | 0.3125 / 1 / 0.6667 | 2 |
| 같은 방향의 두 step | 2 | 1 / 1 / 1 | 2 |

**실험의 한계:** authority 계산에는 `material_texture_conflict=0`, `representation_support=0.24`를 명시적으로 구성했다. 실제 전체 파이프라인이 이 두 사실을 자동으로 관측했다는 뜻이 아니다. 또한 같은 raster appearance가 실제 defocused boundary와 illumination 양쪽에서 생길 수 있다. 표를 물리적 negative classifier의 정확도처럼 사용하지 않는다.

생성기는 high-recall 목적상 이런 후보를 남길 수 있다. 문제는 측정 가능성과 밝기 변화에 경계 identity의 권한이 부여되는 연결부다. 이 반례만으로 phase-scan을 지우거나 선형 기울기를 전부 negative 처리하지 않는다.

### H2. “broad와 narrow가 동시에 높으므로 독립된 경계 증거가 있다”

현재 phase-scan에서는 같은 `strength`가 `broad_strength`와 `narrow_peak_strength` 양쪽에 들어간다. `narrow_horizontal_coverage`에는 앞서 설명한 measurable-sector coverage가 들어간다. 이를 `OilCandidateEvidence`가 다시 material support에 사용한다. [S07, S08]

현재 식을 이 후보군에 대입하면 다음과 같다.

```text
boundary = .42*s + .24*c + .18*k + .16*a
material = .34*boundary + .18*s + .14*s + .13*c + .07*k + .05*p
         = .4628*s + .2116*c + .1312*k + .0544*a + .05*p
```

여기서 `s`는 같은 pooled intensity response, `c`는 측정 가능한 sector 비율이다. 이 계산 자체가 수학적으로 잘못됐다는 뜻은 아니다. 그러나 여러 독립적인 물리 계면 관측이 모였다는 해석은 지지하지 않는다. feature 이름만 바꾸거나 항 하나를 삭제해 기존 cutoff를 그대로 쓰는 것도 새로운 점수 체계를 몰래 도입하는 일이다.

`_cross_representation_support`에는 같은 family 제외, texture/artifact/optics 반대 증거 제외, 일부 calibrated 조합 제한이 이미 있다. 따라서 “아무 방어도 없다”는 결론은 틀리다. 다만 family가 다르고 Y가 가깝다는 사실이 같은 X support의 독립 물리 관측임을 완전히 보장하지는 않는다. 이 부분은 지지 footprint를 확인하는 후속 설계 대상이다. [S09]

### H3. “paired-edge가 크면 왕복하는 얇은 광학 띠다”

`_narrow_summary`는 중심에서 일정 거리 이상 떨어진 절대-gradient의 강한 행을 pair로 고른다. pair 선택 자체는 두 기울기의 부호가 반대인지 요구하지 않는다. [S10]

새 계측 실험은 같은 에너지·coverage·위치에서 partner 부호만 바꿨다. 양/음 방향 반전을 포함한 4개 반례에서 legacy `paired_edge_strength`는 모두 약 **0.8**이고, 같은 방향 shoulder와 반대 방향 return의 legacy 요약 전체가 같았다. 별도 `center_signed`, `partner_signed`, `same_sign`, `opposite_sign`, `both_samples_valid`를 읽으면 계측상 차이를 보존할 수 있었다. 읽기 전후 기존 배열과 legacy 반환은 바뀌지 않았다.

이것은 **새 identity 알고리즘의 성공이 아니라, 손실 없는 추가 계측이 가능한지 검증한 결과**다. 같은 방향은 곧 Oil, 반대 방향은 곧 artifact라는 규칙을 만들지 않았다.

기존에 opposite-sign 조건만 넣었던 prototype은 80개 관련 테스트 중 5개가 실패했고, 특히 `alternating-below-latent-cause-collision`이 경계로 승격되는 안전 회귀가 있었다. 이 실패를 그대로 존중한다. 계측 오류/명칭 문제를 고친다는 이유로 기존 texture opposition까지 제거해서는 안 된다. [S04]

### H4. “확인된 Y854는 생성되지 않거나 점수 정렬에서 잘린다”

sample4 frame420에서 사람이 확인한 Oil–Foam 위치 Y854는 candidate list에 남아 있었다. 최신 reason repair 후 실제 실패 이유는 `boundary_advantage`였다. boundary 약 0.43154, artifact 약 0.54594로 차이는 −0.11440이며 요구값 +0.08을 충족하지 못한다. representation, 최근 Foam, separation이 없어서 떨어진 것이 아니다. [S04, S08, S11]

이번에 저장된 121프레임을 현행 resolver로 다시 실행한 baseline도 Oil 30행 / Foam 104행, frame420 Oil Y821을 재현했다. 따라서 이 구간의 문제는 단순한 후보 누락·export 왜곡으로 설명되지 않는다.

반대로 exact-row Canny를 새 필수 조건으로 추가하면 확인된 Y854의 그 행 coverage가 0인 기존 반례에 걸린다. 좁은 contour band와 정확한 한 raster row는 같은 관측 단위가 아니다. 기존 실패안을 다시 채택하지 않는다.

### H5. “문제 후보군의 anchor 권한만 낮추면 해결된다”

운영 소스를 수정하지 않고, 별도 프로세스에서 `phase_transition_scan`의 `ANCHOR_ELIGIBLE`만 `CONTINUATION_ELIGIBLE`로 낮추는 반사실 실험을 했다. 후보를 삭제하거나 Y를 바꾸지 않았다. 특정 영상·frame·Y를 조건으로 사용하지 않았다. 이 규칙은 원인 확인용이며 제품 설계안이 아니다.

| 같은 수정 ROI, frame390–510, 121행 | baseline | anchor demotion |
|---|---:|---:|
| authority 판정 호출 | 2,511 | 2,511 |
| 강등한 판정 호출 | 0 | 180 |
| Oil 수치 행 | 30 | 62 |
| Foam 수치 행 | 104 | 99 |
| frame420 Oil Y | 821 | 852 |
| frame420 선택 source | `phase_transition_scan` | `calibrated_high_recall` |
| frame420 후보 수 | 24 | 24 |

Y854 reference에서 좌표상 거리가 33px에서 2px로 줄었지만, **다른 candidate를 선택한 것**이다. 그 candidate에 Y854의 사람 판정을 자동 이전하거나, 사람이 제공하지 않은 2px 허용오차로 정답을 선언할 수 없다. Oil 수치 행 증가와 Foam 수치 행 감소도 성능 향상이라고 단정할 수 없다.

같은 규칙을 원래 recipe·고정 2fps·전체 4영상 pipeline에도 적용했다. 사전에 “기존 수치 truth가 사라지거나 좌표 오차가 증가하면 보호 회귀에서 교체안 기각”을 판정 규칙으로 두었다.

| 영상 | baseline Oil / 전체 행 | ablation Oil / 전체 행 | truth 수치 반환 baseline → ablation | 관측 변화 |
|---|---:|---:|---:|---|
| Base | 28/30 | 29/30 | 3/3 → 3/3 | truth 비교값은 동일; 전체 수치 1행 증가 |
| sample2 | 4/5 | 3/5 | **2/3 → 1/3** | **frame60 Oil Y603 → 없음**; frame30 Y590 유지 |
| sample3 | 29/151 | 29/151 | 2/2 → 2/2 | tracking fingerprint도 동일 |
| sample4 | 101/113 | 101/113 | 4/5 → 4/5 | truth 수치와 Foam 수 동일, 전체 tracking fingerprint는 변화 |
| 합계 | **162/299** | **162/299** | **11/13 → 10/13** | 합계 coverage는 손해를 숨긴다. |

**판정: 교체안으로 기각.** sample2의 기존 수치 관측이 사라져 사전 회귀 조건을 충족하지 못했다. 기존 Y603 자체도 truth Y592와 11px 차이가 있었으므로 이를 정확한 관측이라고 부르는 것은 아니다. 다만 근거 없이 누락시킨 결과를 개선으로 승격할 수 없고, 다른 보호 사례에 대한 비용이 드러났다.

특히 sample2의 조건부 MAE는 **6.5px → 2px**로 좋아 보인다. 이유는 11px 오차 사례가 보류되어 평균에서 빠졌기 때문이다. 두 비교 모두 값이 나온 행의 same-frame provenance 누락은 0이다. 따라서 provenance 통과·합계 수치 수 유지·조건부 MAE 개선만으로는 이 변경의 타당성을 판단할 수 없다.

이번 family-level demotion을 production에 복사하지 않는다. 30fps 특정 사례의 개선처럼 보이는 결과와 4영상 회귀 손실을 함께 저장하고, 계측 의미와 candidate별 identity readout을 먼저 정리한다.

### H6. “30fps 진단 결과를 그대로 2fps 운영 실패로 일반화해도 된다”

그렇지 않다. 같은 수정 ROI, 같은 현재 소스, 같은 source frame을 사용해 sampling과 시작 문맥을 바꿨다. 이 실험은 서로 다른 workload를 비교한 것이지, 동일 입력 조건의 알고리즘 A/B 성능 비교가 아니다.

| 조건 | 프레임 수 | raw Oil/Foam | completed Oil/Foam | frame420 최종 Oil Y/source |
|---|---:|---:|---:|---|
| 390–510, 매 프레임 30fps | 121 | 77 / 114 | 30 / 104 | 821 / phase-scan |
| 390–510, 15프레임 간격 2fps | 9 | 6 / 8 | 7 / 8 | 852 / phase-scan |
| 0–510, 15프레임 간격 2fps | 35 | 22 / 21 | 34 / 22 | 852 / phase-scan |

원본 decoder 위치와 timestamp를 검사했다. 일부 기존 saved detections를 건너뛰어 만든 가짜 2fps가 아니라 각 조건에서 fresh detector로 실제 프레임을 검출했다.

30fps와 2fps에서는 motion·frame-offset 창·tracklet·상태 문맥이 함께 달라진다. 어느 하나의 시간 문턱만을 원인으로 특정한 실험은 아니다. 또한 prefix 실험에는 0–13초 정보가 추가되지만 별도 static calibration을 학습시킨 것은 아니다. 결과가 비슷해 보이는 조건만 선택해 합격을 선언하지 않는다.

**의미:** 30fps 실패 관찰은 유효하지만 적용 범위를 밝혀야 한다. 실제 지원 sampling에 대한 진입 조건을 고정해야 하며, phase-scan이 2fps에서는 좌표상 가까운 Y852를 제공한다는 사실도 함께 남겨야 한다. source-family blacklist는 이 정보를 잃는다.

---

## 7. Foam 경로의 독립 감사

기존 사람의 판정과 ROI 교정 결과를 유지한다. sample4의 원래 ROI는 rim을 포함했고, 사람이 교정한 별도 ROI에서는 frame450/480의 해당 rim component 픽셀이 제거됐다. 그러나 이는 전체 identity 문제의 종결이 아니다. [S04, S12]

현재 component 처리에는 다음 서로 다른 문제가 있다.

**첫째, 입구 geometry 오염.** `geometry_masks.py`는 recipe대로 mask를 만들었다. 기존 조사에서 rim이 보였던 것은 mask 적용 누락이 아니라 지정된 ROI가 rim을 포함했던 문제였다. 따라서 계산 코드를 탓하며 전역 margin을 바꾸거나 전체 영상의 recipe를 자동 수정하지 않는다.

**둘째, component 의미의 혼합.** 실제 Foam에 중앙 구조/반사·다른 경계가 붙으면 component 수준의 white/texture/shape 점수가 높아도 모든 front 위치가 Foam인 것은 아니다. 범위가 겹치는 bbox만으로 substrate 관계를 판단하는 실패도 이미 검토됐다. 반대로 bbox veto를 제거하기만 하면 혼합 지지가 해결되는 것도 아니다.

**셋째, front의 국소 소유권.** `_component_evidence`는 bottom-connected component에서 `ys.min()`을 front로 쓰고, detached component에서는 해당 phenotype의 front를 쓴다. 기존 mixed-support 사례에서 상단 극값이 중앙 구조의 상승 부분을 포함할 수 있다. 넓은 영역의 평균 score는 이 국소 지점의 identity를 대체하지 못한다.

**넷째, temporal 확인의 범위.** Foam episode resolver는 후보의 episode 증거를 확인한다. 오염된 spatial front를 실제 경계로 다시 그리는 장치가 아니다. 안정적으로 반복된다는 이유만으로 혼합된 상단 극값을 물리적 Foam front로 인증할 수 없다.

따라서 Foam 개선은 **component 후보 보존 → local front support 분리 → identity/오염 상태 → scalar 사용 가능 여부 → temporal episode**의 순서로 다룬다. Oil 변경만으로 Foam 문제도 해결됐다고 보고하지 않는다.

---

## 8. 현재 logic-map 노드별 감사

아래 표는 소유 경로와 실제 이번 검사 범위를 대응시킨 것이다. `보존`은 field accuracy PASS가 아니라 현행 계약을 보호한다는 뜻이다. [S02]

| 정확한 노드 ID | 주요 owner / 감사 관점 | 이번 판단 |
|---|---|---|
| `FRAME-EVIDENCE` | `OpenCvPhaseDetector.detect`, `CurrentFrameEvidenceOwner.observe` | recipe mask 적용, original/normalized 구분, 13개 fresh frame debug 동등성 검증. |
| `OIL-RAW-EVIDENCE` | `extract_raw_observations` | broad/narrow/pulse의 측정 의미·availability 분리가 필요하다. |
| `OIL-PROPOSAL` | `build_bounded_proposals` | 가까운 후보가 남은 사례와 이미 geometry 차이가 큰 사례를 분리한다. 무조건 budget 증설하지 않는다. |
| `OIL-HYPOTHESIS` | `evaluate_semantic_hypotheses`, `OilHypothesisPipeline.run` | 같은/반대 부호 lobe가 legacy summary에서 충돌한다. texture/optics opposition 단독 제거는 기각한다. |
| `OIL-CANDIDATE` | `assemble_phase_candidates`, `project_production_result` | 후보군별 feature 의미가 다르다. phase scan의 broad/narrow/coverage 중복 해석을 분리한다. |
| `FOAM-CANDIDATE` | `detect_bottom_connected_foam`, frame owner | component 보존과 국소 front 사용 가능성을 따로 평가한다. |
| `FOAM-IDENTITY` | `track_foam_material_identity`, Oil admission의 관측 문맥 | upper material/ordered-lower reserve는 관측 문맥이다. 자체 Oil/Foam publication 권한으로 확대하지 않는다. |
| `OIL-AUTHORITY` | `evaluate_phase_identity`, `evaluate_candidate_authority`, `_candidate_refs` | 핵심 수정 경계. 직접 identity의 긍정 근거와 반대 증거, 단순 appearance를 분리한다. |
| `OIL-TRACKLET` | `DirectedInterfaceTrackletBuilder.resolve`, `OilTrackletOppositionOwner` | 같은 frame의 지지와 물리 owner 계약을 보호한다. Y 근접/family 차이만으로 독립성을 과장하지 않는다. |
| `OIL-PHASE-INITIAL` | `OilMaterialPhaseLifecycleOwner` | 확인된 FULL/EMPTY/UNKNOWN이 좌표를 만들어내지 않는 계약을 보존한다. |
| `OIL-PHASE-FILL` | fill chain/confirmation/reentry | 후보 identity보다 먼저 gate를 완화하지 않는다. |
| `OIL-PHASE-DRAIN` | direct/recovery/refill/handoff | 기존 direction/owner/lease 계약을 보존한다. 이번 별도 문턱 변경 없음. |
| `OIL-SELECTOR` | `build_interface_layers`, `BoundedOilInterfaceSelector` | 잘못 허용된 후보를 안정적으로 고를 수 있다. selector 교체가 첫 수정점은 아니다. |
| `OIL-PROJECTION` | `OilResolutionProjectionOwner`, decision witness | 4영상 baseline/반사실의 수치가 같은 프레임 후보에 연결되는지 확인했다. arbitrary Y/carry 금지. |
| `FOAM-EPISODE` | `FoamEpisodeResolver.resolve` | spatial front 재국소화 장치가 아니다. frame-offset와 source-time 제한을 sampling 문맥과 함께 평가한다. |
| `SEQUENCE-COMPOSITION` | `ObservationSequenceResolver.resolve` | Oil/state 먼저, Foam 다음. 최종 Oil의 bounded alias 문맥 외에 상대 계열의 권한을 빌리지 않는다. |
| `PUBLICATION-PROVENANCE` | 최종 detection에서 observation/sample/event로의 연결 | raw/current/final과 same-frame source를 구별하고, 생성한 application 결과의 provenance를 검사했다. |
| `RESULT-PRESENTATION` | graph/report/review model | 보고서 bundle을 재생성했다. presentation이 새로운 관측을 생성하지 않는 계약 유지. |
| `CSV-PUBLICATION` | 최종 sample의 CSV 직렬화 | 299행의 시각·glass·수치/보류를 재조회했다. 단순 숫자 수를 identity 정확도로 보고하지 않는다. |
| `TRACE-PUBLICATION` | JSONL/diagnostic/witness serialization | 새로운 Foam 진단과 정확해진 failed-gates가 기존 fingerprint 비교 범위에 반영되지 않은 실패를 분리했다. |

위 20개는 기준 HEAD logic-map의 정확한 노드 ID다. 별도의 `FOAM-TEMPORAL` 또는 병렬 pipeline owner를 새로 정의하지 않았다. 표는 현행 계약에 이번 검사를 대응한 것이며 모든 내부 분기의 현장 correctness를 주장하지 않는다.

---

## 9. 실패 이력과의 충돌 검사

`S11-F01`부터 `S11-F10`까지를 모두 검토 대상으로 삼았다. 아래는 실패군의 감사 요약이지 registry의 정식 제목을 새로 정의한 것이 아니다. [S03]

| 실패 ID / 현행 registry 제목 | 이번 관찰·보존할 방어 |
|---|---|
| `S11-F01` — Pre-selection authority collapse | 강한 appearance나 early selection이 최종 물리 권한을 대신하지 않도록 후보와 typed authority를 분리한다. |
| `S11-F02` — Proposal/representation recall starvation | 가까운 후보가 있어도 identity는 별도다. 후보가 먼 sample4 후반 사례도 감추지 않고 first-loss를 나눈다. |
| `S11-F03` — Motion/bootstrap authority overreach | motion·smoothness·높은 sampling 관측 수가 same-frame identity를 만들지 못한다. |
| `S11-F04` — Component identity leakage and alias continuation | Y-adjacency, source-family, mixed support를 물리 owner의 동일성으로 간주하지 않는다. |
| `S11-F05` — Initial-state and material-phase hard-lock asymmetry | identity 개선을 이유로 FULL/EMPTY/UNKNOWN gate를 함께 풀거나 숫자를 생성하지 않는다. |
| `S11-F06` — Foam/Oil/material evidence cross-coupling | Oil ablation 후 Foam 결과도 변했다. 각 계열의 authority와 최종 alias 문맥을 따로 검사한다. |
| `S11-F07` — Foam episode false dynamics and stale episode identity | static/mixed front의 반복을 실제 Foam front로 승격하지 않는다. spatial identity와 bounded episode를 분리한다. |
| `S11-F08` — Lifecycle closure and owner-loss dead ends | fill/drain/reentry/handoff의 기존 보호 계약을 먼저 유지하고 W4와 lifecycle 수정의 원인을 섞지 않는다. |
| `S11-F09` — Coordinate, validity and provenance ambiguity | 숫자의 same-frame 출처가 맞아도 identity는 틀릴 수 있다. 진단-only 차이와 behavior fingerprint도 별도로 보호한다. |
| `S11-F10` — Global-threshold or case-specific escape hatch | global cutoff, family blacklist, private Y/polarity 분기, truth/golden 수정으로 실패를 덮지 않는다. |

최근 반증에서 결과가 좋아 보인 source-family demotion도 위 원칙의 예외가 아니다. 특정 family를 믿거나 불신하는 규칙으로 실제 interface identity를 대신하지 않는다.

---

## 10. 권장 설계: 증거 의미와 물리적 권한을 분리

### 10.1 유지할 구조

현재 frame detector → candidate assembly → Oil admission/tracklet/lifecycle/selector → Foam episode → application/report의 골격은 유지한다. 공개 수치의 same-frame provenance, Oil/Foam 별도 계열, 제한된 연산량, explicit UNKNOWN/FULL/EMPTY, protected behavioral tests는 그대로 둔다.

전면 재설계가 필요한 것은 전체 앱이 아니라 **일부 evidence representation과 그 evidence가 authority를 얻는 경계**다. 이 경계를 명확히 바꾸면 기존 잘 동작하는 데이터 입출력·UI·report·상태기계를 함께 뒤흔들 필요가 없다.

### 10.2 분리할 네 가지 질문

```text
1) 이 위치에서 무엇을 실제로 측정했나?
   intensity / gradient / texture / local support / optics / temporal observation

2) 이 관측이 물리적 interface라는 판단을 지지하는가?
   interface / unresolved / opposed 또는 unavailable

3) 실제 interface라면 이번 검사의 target인가?
   target / real-but-nontarget / unresolved

4) 지금 프레임에서 어느 좌표를 공개할 수 있는가?
   exact candidate/contour binding / ambiguous geometry / unavailable
```

`측정 가능`, `물리 경계`, `추적 target`, `숫자 반환 가능`은 서로 다른 상태다. 물리 경계로 확인됐지만 contour가 섞였으면 scalar는 보류할 수 있다. 반대로 strong scalar appearance가 있어도 identity가 불명확하면 직접 anchor로 승격하지 않는다.

### 10.3 추가할 계측 계약 — 초기에는 shadow 전용

다음은 의미 계약이다. 정확한 class/file 배치는 기존 types/adapter 소유권에 맞춰 결정하며 새 병렬 runtime owner를 만들지 않는다.

```python
@dataclass(frozen=True)
class BoundaryMeasurementV2:
    candidate_token: str          # 같은 frame의 원래 candidate와 결합
    frame_token: str
    raster_token: str             # original-gray / normalized 등, recipe·crop hash 포함
    support_token: str            # 실제 사용한 X/Y support와 mask lineage
    available_sector_fraction: float | None
    observed_boundary_support: float | None  # 계면 지지의 정의를 별도로 가진 계측
    signed_normal_profile: tuple[float, ...] | None
    same_sign_shoulder: float | None
    opposite_sign_return: float | None
    profile_localization: float | None       # 단순 slope와 국소 변화의 구분 근거
    optics_opposition: float | None
    texture_opposition: float | None
    support_contamination: str   # clean / mixed / unresolved / unavailable
```

중요한 것은 필드 수를 늘리는 것이 아니라 **의미를 바꾸지 않고 연결할 수 있게 하는 것**이다.

- `None`/unavailable와 측정값 0을 구분한다. 특히 static map을 학습하지 않았다는 사실은 artifact가 없다는 물리 증명이 아니다.
- legacy `paired_edge_strength`는 V1 소비자를 위해 그대로 둔다. 새로운 의미를 같은 이름에 조용히 덮어쓰지 않는다.
- available-sector를 connected-boundary coverage로 다시 쓰지 않는다. 후자의 계측이 구현되지 않았으면 미계측으로 둔다.
- source family는 디버깅·lineage 정보이지 identity 정답이 아니다.
- 기존 max/mean 값이 다른 X/Y 위치에서 왔다면 같은 관측의 독립 corroboration처럼 합치지 않는다.
- 같은 부호인지 확인하는 것과 그 부호가 물리적으로 Oil을 뜻한다는 가정은 다르다. 전자는 계측, 후자는 이 명세가 허용하지 않는 shortcut이다.

### 10.4 candidate-identity challenger의 구체적인 방향

**기존 bounded candidate와 native path를 출발점으로 삼는다.** 새 region-family의 최저 loss 순위를 다시 identity 정답으로 쓰지 않는다. 후보마다 실제 support columns와 path normal 방향에서 원 gray의 상하 관측을 저장하고, 가능한 경우 normalized 특징과 병렬로 비교한다.

우선 비교할 정보는 다음 네 묶음으로 제한한다.

| 정보 묶음 | 확인할 차이 | 금지할 해석 |
|---|---|---|
| 국소 normal-profile 구조 | 일정한 slope / 국소적인 넓은 transition / shoulder / return / 복수 peak | 가장 선명한 peak가 곧 Oil이라는 결론 |
| 관측 support의 분포 | 유효 sector와 실제 측정 support, 단절·오염·곡률의 차이 | 단순 X 점유율만으로 연결된 물리 계면 인증 |
| 반대 증거 | optics, texture collision, structural overlap와 각 availability | 반대 증거가 미측정이면 clean으로 확정 |
| representation의 동일 지점 결합 | 서로 다른 proposal이 공통 X 영역의 같은 경계를 지지하는지 | Y 근접만으로 독립적인 두 번의 관측으로 간주 |

첫 readout은 복잡한 segmentation network보다 작고 감사 가능한 형태가 적합하다. 다만 이것은 “작은 모델이면 정확하다”는 보장이 아니다. 규칙형이든 regularized classifier든 feature/출력/partition/운영점을 고정하고 같은 표로 평가한다. 현재 3개 review case의 75개 후보만으로 신뢰할 수 있는 현장 일반화가 입증됐다고 주장하지 않는다.

판독 가능한 실제 target의 admission 개선과 알려진 non-target의 오승격 억제를 **동시에** 보여야 한다. 불명확한 candidate는 negative로 바꾸지 않고 unresolved로 남긴다. 동일한 observable raster에 서로 다른 latent cause가 가능한 충돌 controls에서는 근거 없는 확신을 늘리지 않는다.

---

## 11. 구현 작업 명세 — 기존 W4 내부의 작업 단위

### W4-A0. 이번 감사 증거 고정 및 실행 기반 정리

**상태:** 이번 감사에서 실행 증거를 생성했다. 저장소 편입은 별도 변경이다.

입력은 고정 HEAD, 기존 12개 corpus pin, 별도 human ROI와 기존 121프레임 saved detections다. 산출물은 scripts, 각 JSON 결과, canonical JUnit/log, source inventory, 최종 보존 receipt다. 이번 `/tmp` 산출물을 검토 후 정식 evidence 위치에 복사할 때는 해시를 보존하고 새 레코드로 추가한다. 기존 `s11-local-*` 디렉터리 파일을 덮어쓰지 않는다.

완료 조건은 실험별 source/입력/recipe/sampling/initial-state/label-role이 식별되고, baseline과 반사실 결과가 명확히 구분되는 것이다. temporary path만 남기지 않도록 정식 편입 시 evidence 문서에서 raw artifact 위치와 hash를 연결한다.

### W4-A0B. canonical 기준과 진단 계약 수리 — 새 변경 전 선행 작업

**목적:** 현행 3개 실패를 명시적으로 닫고, 이후의 behavioral 개선이 테스트 기준 변경에 가려지지 않게 한다. (§5.1)

수정 대상은 우선 `tests/test_r16_refactor_characterization.py`, `tests/test_foam_component_diagnostics.py`, `tests/unit/test_s11_foam_front_alternatives.py`다. detector 계산을 이전 버전으로 되돌리지 않는다.

1. current-frame legacy view에서 commit `b559a11`의 정확한 두 trace 추가를 명시적으로 분리한다. 기존 golden은 보존하고, 새로운 diagnostics/image의 shape·boundedness·source binding은 별도 테스트로 유지한다.
2. completed-window view에서는 4종 이유 필드의 진단 스키마 변화를 명시적으로 검증한다. 비교에서 실제 authority 등급·통과 여부·선택 후보·Y·score를 제외하지 않는다. 최신 함수의 올바른 이유 검사는 남기고, behavior와 reason-version을 별도 snapshot/동등성 계약으로 정의한다. `failed_gates`라는 문자열이 들어간 모든 키를 무차별 제거하지 않는다.
3. 위 5개 text I/O 호출에 fixture와 일치하는 `encoding="utf-8"`를 명시한다. 정책 테스트는 유지한다.

완료 조건은 실패 3건의 targeted 검사 통과, 기존 reason/component tests 유지, **2,313개 현행 선택 전체의 재실행 green**, 새로 추가한 regression tests 통과, 그리고 public replay 입력·behavior fingerprint 보존이다. 테스트 수가 늘면 증가분과 기존 2,313개를 구별한다. 이번 감사는 수정하지 않았으므로 이 작업은 아직 미완료다.

### W4-A1. 증거 의미의 손실 없는 분리

**목적:** 현재 점수·선택을 그대로 둔 채 실제 측정과 이름 사이의 간극을 관측 가능하게 만든다.

| 항목 | 명세 |
|---|---|
| 변경 후보 | `oil_shadow_types.py`, `oil_shadow_observations.py`, `oil_supplemental_path.py`, trace/diagnostics adapter |
| 소비자 경계 검토 | `oil_candidate_evidence.py`, `phase_candidate_assembler.py`; 처음에는 behavior를 바꾸지 않는다. |
| 필수 산출물 | V2 계측/availability/lineage 계약, legacy와 나란한 직렬화, synthetic + real-frame regression tests |
| 금지 | cutoff 변경, legacy likelihood 재계산 변경, 후보 삭제/증설, authority 등급 변경, truth/recipe 수정 |
| 종료 조건 | 모든 기존 반환 값은 새 diagnostic 필드를 제외하고 동일; 4영상 public row fingerprint 동일; resource bound 검증 |

필수 반례는 일정 slope, 넓은 국소 step, 얇은 return, same-sign shoulder, polarity reversal, fragmentation, masking/unavailable, glare/static 정보 없음, texture collision이다. 이번 12개 appearance·4개 lobe probe를 정식 테스트로 정리하되 constructed context와 실제 pipeline 문맥을 혼동하지 않는다.

`same_sign_shoulder`와 `opposite_sign_return`을 나누는 작업이 기존 `artifact_likelihood`를 낮추는 변경으로 합쳐지면 A1 범위를 벗어난다. 별도 A2 실험으로 다시 제출한다.

### W4-A2. 단일 identity challenger와 반증 가능한 admission 실험

**진입 조건:** A0B로 canonical 기준을 닫고, A1의 출력 동등성 및 기존 collision controls를 통과한다.

기존 후보에 대한 bounded local-profile/support readout을 하나만 설계한다. 이름만 다른 여러 heuristic을 같은 평가 자료에 반복 튜닝하지 않는다. 결과는 제품 authority를 덮어쓰지 않는 shadow table로 시작한다.

| 필수 입력/출력 | 요구사항 |
|---|---|
| 입력 | same-frame candidate token + 실제 support + V2 계측 + 그 계측의 availability |
| 제외 입력 | sample 이름, private frame index, absolute source Y, review label, 다음 frame의 사람 판정 |
| 허용 위치 정보 | 후보 내부 local geometry와 정규화된 상대 좌표. 위치 자체를 target 정답으로 쓰지 않는다. |
| identity 출력 | interface / opposed / unresolved / unavailable, 판단에 사용한 구체적 계측 |
| target 출력 | target / real-but-nontarget / unresolved; identity와 별도 축 |
| scalar 출력 | 원 candidate/contour binding 또는 geometry unavailable. 새로운 Y 생성 금지 |
| 비교 | baseline admission, challenger admission, 최종 selection을 따로 기록 |

반증 목표는 “Y854를 무조건 통과시킨다”가 아니다. 확인된 correspondence를 불필요하게 거절한 이유를 바로잡으면서, 821 같은 미확정 appearance와 기존 texture collision을 확정 경계로 만들지 않는 것이다. Y821의 물리 객체를 noise나 structure로 확정하는 새 라벨은 만들지 않는다.

승격 검토에는 다음을 모두 제출한다.

- 기존 보호 scalar/identity 사례의 손해와 이익을 case별로 공개한다. 숫자가 없어진 경우 오차 평균에서 조용히 빼지 않는다.
- 실제 nontarget과 unresolved를 구분하여 오승격 수를 보고한다. 3개의 실제 internal interface를 target으로 잘못 끌어올리는지 검사한다.
- original recipe와 이미 존재하는 human ROI 결과를 섞어 순위를 만들지 않는다. 서로 다른 조건으로 보고한다.
- challenger가 바꾼 첫 stage와 최종 출력 변화가 연결된다. candidate-only 손실, temporal association 손실, selector 손실을 하나의 failure count로 합치지 않는다.

**즉시 기각 조건:** known collision의 확정 경계화, blanket family/polarity/position 규칙, 한 프레임 개선을 위해 다른 보호 사례 악화, 미측정 값을 clean evidence로 취급, 같은 정답의 반복 사용을 holdout으로 주장하는 경우.

### W4-A3. Foam local-front support 분리

**목적:** component가 실제 Foam을 포함한다는 판단과, 반환하려는 front 지점이 Foam이라는 판단을 분리한다.

주 owner는 `foam_front_detector.py`; `foam_material_identity.py`, diagnostics, 기존 component/episode tests를 함께 검토한다. `foam_episode_resolver.py`의 시간 문턱 조정으로 먼저 해결하지 않는다.

구현은 기존 component를 유지한 채, native local front의 column별 support와 structural/optical/mixed overlap을 따로 저장하는 것부터 시작한다. bbox 관계를 실제 공통 column support의 관계로 대체할 때도 기존 bbox 결과를 단독 삭제하여 candidate를 무조건 살리는 변경을 하지 않는다.

`front_support_status`를 `usable / mixed / unresolved / unavailable`로 다루고, 필요한 support가 부족하면 component identity와 scalar availability를 따로 반환한다. 이 상태가 공개 출력 계약을 바꾸는 시점에는 version/consumer/test 변경을 함께 한다.

필수 regression controls는 rim C1, 유효 Foam C2, 중앙 구조와 Foam이 붙은 mixed support, 구조가 없는 실제 curved Foam front, 얇은 glare, detached/bottom-connected/layer/droplet, no-Foam/no-interface다. 사람의 기존 A/C/D·B 판정과 14초/16초 근사 클릭을 재사용한다. 근사 클릭에 임의 pixel tolerance를 붙이지 않는다.

A3에서 새로운 front 선택이 생기면 후보 전체의 임의 min/max가 아니라 그 frame의 명시적 support contour에 연결해야 한다. 어떤 front를 선택해도 같은 scalar가 나오는 fixture만으로 정확성을 주장하지 않는다.

### W4-A4. 운영점·평가·sample-rate 문맥 고정

**목적:** 개선 여부를 명확한 한 표로 판정할 수 있게 한다.

기존 W3 evaluator와 target binding을 재사용한다. 새로운 독립 평가 프레임워크를 병렬로 만들지 않는다. 불필요한 재검토 요청 대신 예측 결과가 붙은 현재 table을 제출한다.

| 평가축 | 고정할 계약 |
|---|---|
| candidate inclusion | 고정 candidate universe와 누락/새 후보 처리 규칙 |
| identity | physical interface, physical non-interface, unresolved |
| target | target, real-but-nontarget, unresolved |
| localization | exact-frame 또는 명시적 nearest-time; scalar/contour 단위 및 uncertainty |
| sampling | 실제 지원 operating point; 2fps 고정 replay와 30fps diagnostic은 별도 |
| prefix | cold-window와 allowed warmup/prefix의 범위 |
| recipe | original/human-corrected 별도 pin; 유리별 사용자 geometry 확인 범위 |
| temporal evidence | 실제 elapsed time와 observed-frame count 모두 기록 |
| partition | recording/session lineage로 dev/calibration/holdout/regression 역할 고정 |
| compute | candidate/sector/scale/sample 수 상한과 CPU/RSS 계측, baseline과 같은 조건 |

설계/학습과 calibration은 개발 역할 자료 안에서 한다. 최종 holdout을 본 뒤 운영점을 바꾸면 그 결과는 개발 결과로 재분류한다. 기존 네 영상의 미검토 frame도 같은 촬영 lineage라면 독립 holdout으로 보지 않는다. [W03, W04]

이 감사는 운영 sampling을 바꾸도록 승인하지 않는다. 지원할 sampling 범위를 확장하려면 별도 제품 계약과 검증이 필요하다. 현재 결과의 차이를 근거로 30fps를 금지하거나 2fps면 정확하다고 단정하지 않는다.

### W4-A5. O2 승격 검토 패킷

A2/A3에서 실제로 평가할 challenger가 만들어진 뒤에만 준비한다. 입력 pin, candidate/token binding, prediction table, 고정 운영점, 한계/보류, first-loss stage, 반례 결과, 재현 scripts가 하나의 패킷이어야 한다.

기존 75개 review와 W3 binding은 이미 완료된 범위 안에서 재사용한다. 현 단계에서 예측도 없는 동일 Windows 작업을 다시 요구하지 않는다. 별도 영상은 사용자가 진행 중인 기존 계획에 따라 역할을 고정하고, holdout이면 설계자가 픽셀을 보기 전에 지정한다.

O2를 통과했다고 W5 association이나 W6 lifecycle까지 통과한 것은 아니다. 진짜 identity 개선이 확인된 후 기존 support/association, handoff/phase 경로로 연결한다.

---

## 12. 회귀·승격 검사표

| 검사 | 통과 조건 | 실패 시 처리 |
|---|---|---|
| canonical 기준 | 기존 실패 3건의 원인별 수리 후 전체 선택 통과 | baseline 실패를 새로운 기능 실패와 섞지 않고, golden으로 숨기지 않음 |
| 입력 보존 | source/MP4/recipe/truth identity 모두 고정 | 즉시 중지하고 어떤 입력이 달라졌는지 분리한다. |
| 진단 전용 변경 | 새 diagnostic 필드를 제외한 전체 반환 동일 | A1 미완료. behavior 변경과 섞지 않는다. |
| pulse/texture controls | 기존 unresolved collision이 확정 boundary가 되지 않음 | scorer 단독 완화 기각 |
| broad/diffuse control | exact-row edge 부재만으로 확인된 넓은 경계 제거 안 함 | exact-row 필수 gate 기각 |
| source-family control | 같은 family의 유효/불명확 사례를 모두 공개 | family blacklist 기각 |
| scalar provenance | 모든 수치가 같은 frame의 원 후보/contour와 결합 | 출력 승격 차단 |
| bounded sequence | cardinality/frame/glass/timestamp·초기 상태 계약 보존 | W5/W6 변경으로 분리 감사 |
| Oil/Foam | 각 identity/availability와 상호 문맥의 사용 이유가 명시됨 | 한 계열 성공으로 다른 계열 합격 표시 금지 |
| 평가 단위 | exact-frame와 nearest-time, point와contour, group과individual 구분 | metric 재작성; 기존 truth를 수정하지 않음 |
| holdout | 역할·노출·촬영 lineage·운영점 고정 | 개발 증거로만 보고 |
| 비용 | 같은 머신/입력/스레드 조건의 paired 시간·RSS 비교 | 이번 동시 실행 wall time을 성능 기준으로 쓰지 않음 |
| 현장 qualification | 정해진 Windows source/runtime/recipe/영상·판정 계약 충족 | FIELD FAIL 또는 NOT_EVALUATED 유지 |

정확도와 coverage에는 다음 분모를 사용한다.

```text
numeric coverage = 수치가 반환된 평가 단위 / 전체 유효 평가 단위
identity precision = 올바른 확정 identity / 모든 확정 identity
non-target promotion = target으로 승격한 확정 nontarget / 평가한 확정 nontarget
selective localization error = 수치가 있는 정답 단위의 위치 오차
abstention = unresolved / unavailable를 구분하여 각각 집계
```

분모가 없는 precision은 0이나 100%가 아니라 계산 불가다. sparse 정답에서 하나의 MAE만으로 결론을 내리지 않는다. 같은 recording의 frame과 그 frame 안의 후보는 상관된 관측이다. 75 candidate를 독립 Bernoulli 표본으로 간주한 좁은 신뢰구간을 붙이지 않는다. 적은 recording group에서 bootstrap 숫자를 내더라도 일반화 보장으로 사용하지 않는다.

보류를 허용하는 시스템은 coverage와 선택된 예측의 위험을 함께 평가해야 한다. 해당 원리는 selective classification 문헌의 risk–coverage 관점과 일치하지만, 그 논문의 보장을 현재 heuristic detector에 그대로 적용할 수는 없다. [W05, W06]

---

## 13. 변경 순서·리뷰·중단 규칙

권장 변경 순서는 **canonical 기준 수리 → 계측 계약 → 진단 직렬화/동등성 → shadow readout → 보정/평가 → 제한된 admission 교체 → O2 검토**다. Foam front 계약은 독립된 변경으로 준비해 Oil의 점수 변화와 원인을 섞지 않는다.

| 변경 단위 | 함께 묶을 것 | 함께 묶지 말 것 |
|---|---|---|
| A0B 기준 수리 | 열거된 진단 계약·encoding·legacy behavior 동등성 | golden 교체·skip/xfail·제품 behavior 변경 |
| A1 계측 | type/adapter/diagnostic/tests | score·gate·recipe 변경 |
| A2 shadow | 고정 readout + prediction table + 반례 | lifecycle/fill/drain 완화 |
| A3 Foam | local-front support + 명시적 geometry availability | Oil scalar를 Foam hint로 생성 |
| A4 평가 | 기존 evaluator 보완 + partition/operating-point | 새 candidate를 조용히 분모에서 제외 |
| 승격 | authority 사용 변경 + 전체 검증 + 상태 문서 링크 | historical golden/truth 수정으로 실패 제거 |

하나의 반례를 고친 뒤 다른 실제 경계나 안전 collision이 나빠지면 그 변경은 기각하거나 다시 설계한다. 테스트 expected 값을 먼저 고쳐서 개선으로 만들지 않는다. 반례가 ambiguity의 실제 한계를 보여주면 unresolved를 보존하면서 다른 판독 가능한 구간의 성능을 개선한다.

미래의 리팩터링은 필요할 수 있다. 특히 큰 resolver/lifecycle 모듈은 변경 영향 추적 비용이 높다. 그러나 파일을 잘게 나누는 것만으로 지금의 image-to-identity 문제가 해결되지는 않는다. 의미 계약과 결과 동등성을 먼저 고정한 후 소유 경계를 따라 분리한다.

---

## 14. 재실행 방법과 산출물

### 14.1 이 감사에서 실행한 명령

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
AUDIT=/tmp/s11-audit-20261007-vaUpfB

# 이미 실행한 감사 파일이다. 재실행 전 새 출력 디렉터리로 복사한다.
# 이 경로를 그대로 재사용하면 기존 감사 결과를 덮어쓸 수 있다.
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen \
  .venv/bin/python -m pytest -m 'not qt_app' -p no:cacheprovider \
  --junitxml="$AUDIT/nonqt.xml"

PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen \
  .venv/bin/python -m pytest -m qt_app -p no:cacheprovider \
  --junitxml="$AUDIT/qt.xml"

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$AUDIT/diagnose_canonical_failures.py"
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$AUDIT/run_semantic_probes.py"
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$AUDIT/run_sequence_probes.py"
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen \
  .venv/bin/python "$AUDIT/run_public_replay.py"
PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen \
  .venv/bin/python "$AUDIT/run_public_ablation.py"
```

위 scripts는 고정 저장소 경로와 당시 입력을 재사용하는 감사용 코드다. 일반 배포용 CLI가 아니다. `run_sequence_probes.py`와 `run_public_ablation.py`의 monkeypatch는 실행 프로세스 안에만 있고 원본 module 파일을 쓰지 않는다. 종료 시 제품 behavior에 남는 변경은 없다.

canonical 테스트와 일부 영상 분석이 동시 실행됐으므로 wall time은 성능 비교의 근거로 쓰지 않는다. 후속 성능 평가는 baseline/challenger를 같은 시스템 조건에서 직렬 paired 실행해야 한다.

### 14.2 주요 산출물

| 파일/디렉터리 | 내용 |
|---|---|
| `baseline.json` | 시작 HEAD/status/runtime와 추적 756개 파일의 SHA-256 |
| `nonqt.log`, `nonqt.xml`, `qt.log`, `qt.xml` | canonical 선택별 실행·JUnit 결과 |
| `canonical_failure_diagnosis.json`, `failure-rerun.xml/log` | 기존 3개 실패의 개별 재현과 diagnostic-only 분리 증거 |
| `diagnose_canonical_failures.py` | 비교 payload의 열거된 차이 확인; 테스트·제품 소스를 쓰지 않는 진단 script |
| `audit_summary.json` | 전달용으로 축약한 실제 실행 결과와 원본 artifact 연결 |
| `vision_inventory.json` | vision 44개 모듈의 AST/행 수 목록 |
| `semantic_probes.json` | 12 appearance, 4 lobe controls와 13 fresh frame 쌍 검출 |
| `contact-sheet-1.png`, `contact-sheet-2.png` | 13개 source-frame 원본 ROI의 시각 검토용 배치 |
| `*-raw-crop.png` | 실제 crop PNG; 수치 판정에는 여기에 원래 좌표를 사용 |
| `sequence_probes.json` | 121행 baseline/ablation 및 3개 sampling/prefix 실험 |
| `public_summary.json`, `public-replay/` | 4영상 baseline application/report bundles |
| `public_ablation_summary.json`, `public-ablation/` | 같은 4영상의 anchor-demotion 반증 bundles |
| `final_receipt.json` | 종료 identity/보존·테스트 집합·산출물 해시 |

종료 확인 시각은 **2026-10-07 00:44:41 KST**다. 아래는 사용자의 Mac에 보관된 실제 산출물의 SHA-256이며, 다운로드한 이 명세서 자체의 해시와는 다르다.

| 로컬 산출물 | SHA-256 |
|---|---|
| `final_receipt.json` | `01c1dd064af477483d0ff139986f1d01a25516d8a8daec08eb48959897af76a7` |
| `audit_summary.json` | `e31cdb59e8ef73161915d09bb68b58057ffb1c06f7609f42a148a0f0a9f3f952` |
| `semantic_probes.json` | `19d87a64e5e379c5970ad73b870b77d6ddbe528c5183669430d1e0b537c78dcc` |
| `sequence_probes.json` | `d09c183577c7ad172e2a2089d4572b872d34ca470334627e9d2ad9f81934f73a` |
| `public_summary.json` | `de9a450102bee1f87f7127d272ea2eb44f35f12e93cf89478ef9946046cf6bde` |
| `public_ablation_summary.json` | `6fba4148c2c8e64261de41eac6b66d79584564584347019966a994068d40a73e` |
| `canonical_failure_diagnosis.json` | `1d1484c6e5013235ef103384a3e525e8a142bd416fce435bd35f0d5ad3401a2b` |
| `nonqt.xml` | `483dc94411aa53239a1170e80f4ccd16a6292dabc0a7acfd86bb533b41c582ce` |
| `qt.xml` | `0c306a9048e8d046f8e36715f9e312c2e4ad1a1f1411323bf7b0b8921e6db4ba` |
| `s11-audit-evidence.zip` | `67d3dc64cfda459be1762e34ec15f00fd88111d66e84908684b537eba456bec6` |

로컬 경량 패킷은 `/tmp/s11-audit-20261007-vaUpfB/s11-audit-evidence.zip`(23,758byte)이다. 5개 실행/진단 script, 실제 결과를 축약한 `audit_summary.json`, 진단 상세, receipt, 모듈 inventory를 담았고 원본 영상·이미지·대형 trace는 넣지 않았다. 채팅에 제공한 `s11-audit-execution-summary-2026-10-07.json`은 주요 결과를 별도로 정리한 전달용 요약이며, 위 로컬 `audit_summary.json`의 원본 복사본은 아니다.

`/tmp`는 영구 보관 위치가 아니다. 정식 evidence 편입 시 원래 디렉터리를 지우기 전에 receipt의 모든 해시를 대조하고, 기존 docs 폴더 정리 규칙에 맞는 새 날짜의 evidence 문서로 연결한다. 현재 work-plan을 다른 파일로 대체하지 않는다.

---

## 15. 외부 자료가 뒷받침하는 범위

OpenCV 공식 설명의 CLAHE는 contrast를 재분배하는 처리이고, 지역 histogram에서 noise도 증폭될 수 있음을 명시한다. 현재 코드의 normalized response가 원 gray의 물리적 계면 증거와 동일하지 않다는 점을 구분해야 한다. 다만 이것만으로 sample4 Y821을 noise라고 확정하지 않는다. [W01]

Canny는 gradient·non-maximum suppression·hysteresis를 거친 edge detector다. 따라서 edge 출력 자체가 Oil/Foam의 물질 identity를 의미하지 않으며, exact-row edge가 없다고 넓거나 흐린 계면이 없다고 결론내릴 수도 없다. 후자는 이번 repo의 확인된 경계 반례와 함께 해석한 설계 판단이다. [W02, S04]

group/time-dependent validation, preprocessing과 모델 선택에서의 leakage 방지 원칙은 recording lineage별 역할 분리를 뒷받침한다. 이를 적용하더라도 지금의 작은 개발 corpus가 갑자기 독립 현장 검증 자료가 되는 것은 아니다. [W03, W04]

Selective classification은 보류와 risk–coverage를 함께 다룬다. 이는 `숫자가 많이 나옴`과 `확정 숫자의 신뢰성`을 함께 평가해야 한다는 설계 근거다. 이번 감사에서 학습형 selective model을 훈련하거나 그 통계적 보장을 구현한 것은 아니다. [W05, W06]

기존 상용 광학 센서나 별도 촬영 조건 변경은 가능한 다른 문제 설정이지만, 현재 사용자가 선택한 passive existing-video 경로의 즉시 해결책으로 요구하지 않는다. 이 명세는 하드웨어 구매나 새로운 촬영 실험을 W4의 선행 필수 조건으로 추가하지 않는다.

---

## 16. History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-PROPOSAL`, `OIL-HYPOTHESIS`, `OIL-CANDIDATE`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`, `CSV-PUBLICATION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R22 ownership/evidence baseline, O1 witness, W0–W4 진척과 target binding, 미승격 region/position/color 실험, 제거된 R23 polarity, local Foam/structure/ROI/candidate review, 최신 phase failed-gates repair, 기각된 opposite-sign-only pulse repair.
- Prior mechanisms rejected: private-coordinate/source-family shortcut, global threshold relaxation, available-sector를 boundary support로 재명명, geometry·motion·polarity 단독 identity, artifact cue 단독 제거, exact-row edge 강제, truth/golden 변경으로 회귀 제거, downstream interpolation/carry.
- Preserved contracts: same-frame numeric provenance, separate Oil/Foam, explicit uncertainty, bounded candidates/compute, initial-state/lifecycle protection, 독립 역할 분리 및 Windows field qualification.
- Difference from prior failures: 기존 점수에서 반대 증거를 바로 빼지 않고 계측 의미를 손실 없이 분리한다. 새 authority 실험을 full-window 반증과 sampling 문맥에 연결한다. 더 가까운 Y와 검증된 identity를 구분한다.
- Logic-map impact: **NONE** — 이번 감사는 운영 제어 흐름을 변경하지 않았다. 제안 구현의 실제 owner/호출 변경이 생길 때 별도 갱신한다.
- Failure-registry impact: **NONE** — 현행 실패군과 방어 계약을 유지한다. 이번 증거는 이를 구체화하는 감사 자료이며 registry의 기존 실패를 삭제하거나 PASS로 바꾸지 않는다.

## 17. Detector Governance

- First harmful stage: human-ROI 30fps sample4 frame420에서 확인된 Y854는 생성/보존되지만 authority 단계에서 `boundary_advantage`로 직접 소유권을 얻지 못한다. admitted Y821의 물리 identity는 unresolved다. 이 결과는 2fps의 같은 프레임 선택과 다르므로 sampling 문맥을 명시한다.
- Foam first harmful stage: 원래 ROI의 rim 유입과, ROI 교정 후 mixed component의 spatial-front 소유권은 서로 다른 문제다. episode confirmation 전에 구분한다.
- Validation scope: 현행 canonical, exposed four-video application replay, 13 raw-frame debug equality, synthetic measurement controls, saved-sequence ablation, fresh sampling/prefix replay, separate public ablation. 각 결과의 의미는 §5–6에 한정된다.
- Promotion decision: **NONE**. 이번에 생성한 반사실 변경은 제품에 남기지 않았다. classifier/operating point/independent holdout/Windows field success를 주장하지 않는다.
- Current disposition: **FIELD FAIL 유지 / O2 OPEN / W4 candidate-identity 개선 미확정 / W5·O3 이후 gated.**

---

## 부록 A. 주요 source 위치

모든 `[Sxx]`는 기준 HEAD `9f41d2f8a517da21f570f57ed1b4e2009a9d48db`의 파일을 뜻한다. 생성한 실행 결과는 §14의 파일과 final receipt로 식별한다.

| ID | Source |
|---|---|
| S01 | `docs/00-project/work-plan.md`; `docs/00-project/roadmap.md` |
| S02 | `docs/20-architecture/s11-current-detector-logic-map.md` |
| S03 | `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` |
| S04 | `docs/50-diagnostics/s11/2026-10-06-foam-structure-reference-audit.md`, 특히 401–690행 |
| S05 | `docs/30-validation/s11-interface-observability-witness-validation.md`; `s11-detector-change-governance.md` |
| S06 | `tests/diagnostics/s11_evidence_probe.py:129–216`, `tests/diagnostics/s11_report_observability_replay.py:35–134,193–318` |
| S07 | `src/oil_tracker/adapters/vision/oil_supplemental_path.py:182–388` |
| S08 | `src/oil_tracker/adapters/vision/oil_candidate_evidence.py:56–223`; `oil_candidate_authority.py` |
| S09 | `src/oil_tracker/adapters/vision/oil_observation_resolver.py:1535–1614` |
| S10 | `src/oil_tracker/adapters/vision/oil_shadow_observations.py:1546–1640,1825–1998` |
| S11 | `src/oil_tracker/adapters/vision/oil_phase_identity.py`; `oil_observation_resolver.py` |
| S12 | `src/oil_tracker/adapters/vision/foam_front_detector.py:688–1016`; `geometry_masks.py:22–55` |
| S13 | `src/oil_tracker/adapters/vision/preprocessing.py:22–36`; `phase_candidate_assembler.py` |
| S14 | `tests/diagnostics/s11_observation_replay_audit.py:112–178`; `s11_r18_lifecycle_closure_replay.py` |
| S15 | `tests/test_oil_observability_margin_regression.py`; `tests/test_oil_shadow_evidence.py`; `tests/unit/test_oil_supplemental_path.py` |
| S16 | `.agents/skills/s11-detector-change/SKILL.md`; `AGENTS.md`; `docs/00-project/execution-policy.md` |
| S17 | `tests/test_r16_refactor_characterization.py:232–331`; `tests/test_test_authoring_policy.py:31–42`; `tests/test_foam_component_diagnostics.py`; `tests/unit/test_s11_foam_front_alternatives.py` |

## 부록 B. 확인한 외부 1차 자료

확인일: 2026-10-07. 이 자료들은 원리·검증 설계를 보조하며, repository나 실제 Windows 결과를 대신하지 않는다.

- [W01] OpenCV, *Histograms – 2: Histogram Equalization*, CLAHE 설명. https://docs.opencv.org/4.13.0/d5/daf/tutorial_py_histogram_equalization.html
- [W02] OpenCV, *Canny Edge Detection*. https://docs.opencv.org/4.13.0/da/d22/tutorial_py_canny.html
- [W03] scikit-learn, *Cross-validation: evaluating estimator performance*, group/time-dependent data 설명. https://scikit-learn.org/stable/modules/cross_validation.html
- [W04] scikit-learn, *Common pitfalls and recommended practices*, data leakage 설명. https://scikit-learn.org/stable/common_pitfalls.html
- [W05] El-Yaniv & Wiener, *On the Foundations of Noise-free Selective Classification*, JMLR 11, 2010. https://jmlr.org/papers/v11/el-yaniv10a.html
- [W06] Gangrade, Kag & Saligrama, *Selective Classification via One-Sided Prediction*, AISTATS/PMLR 130, 2021. https://proceedings.mlr.press/v130/gangrade21a.html

## 부록 C. vision 모듈 전수 inventory

공통 위치는 `src/oil_tracker/adapters/vision/`이다. 고정 HEAD의 AST 집계이며 행 수는 복잡도·결함 수·수동 정독 여부를 뜻하지 않는다. 기능 검증 범위는 §5–8과 구분한다.

| 파일 | 전체 행 | AST 함수/메서드 |
|---|---:|---:|
| `__init__.py` | 0 | 0 |
| `artifact_calibration.py` | 222 | 7 |
| `artifact_proposal.py` | 109 | 3 |
| `debug_renderer.py` | 42 | 1 |
| `fill_state_classifier.py` | 133 | 3 |
| `foam_episode_resolver.py` | 1105 | 24 |
| `foam_front_detector.py` | 1078 | 26 |
| `foam_material_identity.py` | 202 | 8 |
| `foam_temporal_gate.py` | 262 | 7 |
| `geometry_masks.py` | 55 | 1 |
| `observation_sequence_resolver.py` | 152 | 2 |
| `oil_candidate_authority.py` | 300 | 1 |
| `oil_candidate_evidence.py` | 277 | 7 |
| `oil_decision_witness.py` | 178 | 5 |
| `oil_hypothesis_projection.py` | 258 | 8 |
| `oil_interface_diagnostics.py` | 296 | 6 |
| `oil_interface_selector.py` | 596 | 26 |
| `oil_interface_tracklets.py` | 1310 | 33 |
| `oil_interface_witness.py` | 305 | 7 |
| `oil_material_path.py` | 651 | 12 |
| `oil_observation_resolver.py` | 2641 | 55 |
| `oil_phase_identity.py` | 161 | 2 |
| `oil_phase_lifecycle.py` | 3310 | 73 |
| `oil_phase_topology.py` | 63 | 1 |
| `oil_pipeline_diagnostics.py` | 241 | 9 |
| `oil_pipeline_validation.py` | 1143 | 29 |
| `oil_sequence_types.py` | 91 | 1 |
| `oil_shadow_observations.py` | 2234 | 55 |
| `oil_shadow_pipeline.py` | 1237 | 61 |
| `oil_shadow_temporal.py` | 165 | 6 |
| `oil_shadow_types.py` | 1123 | 83 |
| `oil_spatial_fallback.py` | 813 | 13 |
| `oil_supplemental_path.py` | 602 | 9 |
| `opencv_phase_detector.py` | 272 | 13 |
| `opencv_video_reader.py` | 67 | 7 |
| `phase_candidate_assembler.py` | 352 | 5 |
| `phase_frame_detection.py` | 944 | 10 |
| `preprocessing.py` | 182 | 4 |
| `review_debug_overlay_renderer.py` | 166 | 5 |
| `review_overlay_renderer.py` | 105 | 4 |
| `row_features.py` | 140 | 5 |
| `source_video_resolver.py` | 104 | 4 |
| `temporal_raster_evidence.py` | 542 | 17 |
| `temporal_tracker.py` | 170 | 9 |
| **합계 44개** | **24,399** | **667** |

---

**인계 문장:** 현행 `work-plan.md`와 이 문서의 기준 HEAD 차이를 먼저 확인한 뒤, 기존 W4 안에서 A0B의 canonical 3개 실패를 원인별로 닫은 뒤 A1 계측/lineage 분리를 시작한다. 이번 ablation을 production patch로 복사하지 않는다. 계측 동등성과 기존 collision 보호를 확인한 다음에만 단일 identity challenger의 예측·오승격·보류·scalar 손실을 평가한다.
