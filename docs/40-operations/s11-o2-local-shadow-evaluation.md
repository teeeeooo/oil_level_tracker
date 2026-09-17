# S11 O2 로컬 라벨·Shadow 평가 절차

이 절차는 업무 PC 내부의 **O2 평가 준비**를 위한 것이다. detector 재실행,
실제 계면 자동 판정, production 설정 변경, Windows 현장 합격을 수행하지 않는다.
현재 실행 상태는 [work-plan](../00-project/work-plan.md), 판단 기준은
[Witness Validation](../30-validation/s11-interface-observability-witness-validation.md)이 소유한다.

## 준비물과 실행 위치

- `interface-observability-witness-trace-v1`이 들어 있는 R22-3 결과 번들.
  R22-1/R22-2 trace로 대체하지 않는다. 없으면 먼저 부재를 보고하고 별도로
  기존 GUI/프로필의 제한된 진단 실행을 준비한다.
- 사용자가 실제 프레임을 검토할 수 있는 기존 결과 검토 화면/원본 영상.
- 프로젝트 환경의 Python. 아래는 저장소 루트에서 실행하는 PowerShell 예시다.
  다른 cwd에서는 스크립트와 입력 경로를 절대 경로로 지정해도 동작한다.
- 결과 폴더는 새 이름을 사용한다. 도구는 기존 파일을 덮어쓰지 않는다.
  packet, labels, 예측과 평가 결과는 업무 PC 안에 보관한다. 자동 반출 기능은 없다.

도구: `tests/diagnostics/s11_interface_shadow_evaluation.py`

## 1. 먼저 한 프레임의 검토 packet 만들기

번들 index에서 정확한 `glass_id`와 0-based `frame_index`를 확인한 뒤
`selection.json`을 만든다. 아래 값은 형식 예시이며 실제 대상 값으로 교체한다.

```json
{
  "dataset_id": "o2-regression-review",
  "cases": [{
    "case_id": "review-001",
    "glass_id": "actual-glass-id",
    "frame_index": 0,
    "recording_group": "recording-A",
    "episode_id": "episode-A",
    "physical_case_id": "physical-frame-A",
    "transform_id": "original",
    "partition": "regression",
    "previously_reviewed": true
  }]
}
```

```powershell
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py prepare --bundle "D:\results\R22-3-bundle" --selection "D:\o2\selection.json" --output "D:\o2\review-001"
```

생성물은 `packet.json`과 `labels.json`이다. 기존 indexed trace reader를 사용해
선택한 Glass/frame의 정확한 record만 읽는다. 인접 프레임 대체나 점수순 일부
후보만 추출하지 않는다. 최대 64개 record/packet이며 우선 한 프레임으로 시작한다.
이미지는 복사하지 않고 기존 결과 화면에서 검토한다. packet에는 모든 Oil 후보의
O1 witness가 포함되므로 작은 텍스트라고 가정하지 않는다.

후보 연결은 `candidate_input_index` 동명 필드로 한다. `source/kind/Y/local_y/rejected`
일치와 전체 Oil 후보 집합을 검증한다. 배열 위치와 sequence offset을 섞지 않는다.
모든 초기 라벨은 `unreviewed`, 가시성은 `pending`이다. 자동 정답은 만들지 않는다.

## 2. 사람이 라벨과 분할을 확정하기

`labels.json`의 다음 항목을 실제 검토에 따라 채운다.

- 공통: `label_owner`, `split_owner`, `split_rationale`.
- 프레임: `visibility` = `visible` / `not_visible` / `uncertain`, `reviewer`,
  `review_note`. `label_basis=human_review`는 실제 인간 판독을 뜻한다.
  자동 생성 raster 제어만 `synthetic_construction`으로 구분한다.
- 후보 `label`: `interface`, `localization_mismatch`, `reflection`, `residue`,
  `structure`, `unresolved`, `unobservable`, `unreviewed` 중 하나.
  확인하지 않은 후보는 삭제하거나 반사로 추정하지 않고 `unreviewed`로 둔다.
- `contour`: 확인한 X 범위별 Y 범위만 기입한다. 예를 들어
  `{"source_x_range":[130,236],"source_y_interval":[380,384]}` 형식이다.
  X는 source-frame의 반열린 구간, Y는 양 끝을 포함하는 인간 검토 범위다.
  예시 수치를 정답으로 복사하지 않는다. 정확한 위치가 없으면 빈 배열로 둔다.
- `entity_id`: 동일 물리 대상이라고 검토한 후보/변환만 동일 ID로 연결한다.
  판정할 수 없으면 null. source명이나 거리로 자동 묶지 않는다.

대표 Y 하나를 모든 sector의 정답으로 복사하지 않는다. BASE의 검토된 위치
불일치를 반사/다른 구조물의 확정 negative로 바꾸지 않는다. 계면 정체와 위치
정확성을 별도로 기록한다. `interface`/`localization_mismatch`는 visible 프레임에만
허용된다. `packet_sha256`와 `witness_sha256`, 후보 ID는 수정하지 않는다.

분할 규칙:

- `partition`: `development`, `calibration`, `holdout`, `regression`.
- 이미 반복 검토하거나 설계에 사용한 자료는 `previously_reviewed=true`이며
  regression으로 유지한다. 같은 녹화의 새 프레임만 holdout으로 떼지 않는다.
- 같은 원본 녹화의 모든 Glass·에피소드·밝기/감마 변환·재실행은 같은
  `recording_group`과 partition에 둔다. 이 초기 도구는 episode 분할보다 보수적인
  recording 단위 분리를 사용한다. 한 bundle run을 여러 그룹명으로 나누는 것도 거부한다.
- `episode_id`와 `physical_case_id`는 원본의 물리적 구간/프레임 식별이다.
  transform만 달라도 원본 물리 프레임은 같은 physical_case_id를 쓴다.
- 별도 녹화의 독립성, 미사용 여부와 라벨의 물리적 정확성은 사람의 책임이다.
  도구가 서로 다른 run의 동일 영상을 자동 식별하거나 과거 열람 여부를 증명하지 않는다.

여러 packet을 묶을 때 원본 경로와 라벨을 보존하는 combine을 사용한다.
중복 case ID나 충돌하는 owner는 명시적으로 정리해야 한다. 합본 한도는 256 case다.

```powershell
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py combine --labels "D:\o2\A\labels.json" "D:\o2\B\labels.json" --dataset-id "o2-study-01" --output "D:\o2\study\labels.json"
```

## 3. 라벨을 고정하고 준비 상태 평가하기

```powershell
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py freeze --labels "D:\o2\study\labels.json" --output "D:\o2\study\frozen.json"
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py evaluate --frozen "D:\o2\study\frozen.json" --output "D:\o2\study\readiness.json"
```

freeze는 모든 case/후보의 존재, 라벨, 분할, 좌표와 해시를 검증한다. 경로를 제외한
논리 내용의 해시를 고정하므로 폴더를 이동해도 packet 연결 경로를 함께 보존하면 된다.
공백·JSON key 순서는 해시를 바꾸지 않지만 라벨·수치·배열 순서 변경은 바꾼다.
해시는 drift 검사이며 holdout의 미사용 이력을 증명하는 서명이 아니다.

예측을 넣지 않은 결과는 **NOT_EVALUATED**이다. visible인데 후보가 없는 프레임도
분모에 남는다. classifier 성능 PASS로 해석하지 않는다. 지금 단계에서 Windows가
수행할 작업은 이 준비 상태와 라벨 누락을 확인하는 것까지다.

## 4. 이후 shadow classifier가 준비되면

예측 파일은 `schema_version=s11-o2-shadow-predictions-v1`, `frozen_labels_sha256`,
`classifier_id`, classifier 파일의 `artifact_sha256`, `operating_point_description`,
`fit_partitions`(development/calibration만), `predictions`를 기록한다.
각 예측은 `case_id`, `candidate_input_index`, `witness_sha256`, `decision`, `reason`을
갖는다. decision은 `INTERFACE_SUPPORTED`, `INTERNAL_OR_ARTIFACT`, `UNRESOLVED`,
`UNOBSERVABLE`, `NOT_EVALUATED`이다. 선택적으로 `intervals`에 정확히 같은 witness
X 구간과 예측 `source_y_interval`을 넣는다. 새 Y 좌표는 만들지 않는다.

```powershell
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py evaluate --frozen "D:\o2\study\frozen.json" --predictions "D:\o2\study\predictions.json" --output "D:\o2\study\evaluation.json"
```

현재 도구에는 classifier나 학습/임계값 선택 기능이 없다. 평가용 unit control의
scripted predictions는 실제 알고리즘이 아니다. shadow 모델은 라벨/분할 고정 후
별도 구현한다. holdout/regression으로 operating point를 선택하는 선언은 거부된다.
모델 내부 학습 이력이나 증거 중복 가중치를 이 JSON 계약만으로 검증할 수는 없다.

출력은 partition별 confusion, negative 계열별 wrong support/rejection,
미검토 support, abstention/누락, visible-frame support recall을 분리한다.
identity precision은 위치 불일치도 실제 계면 정체로 세지만, localized-frame support는
`interface`만 센다. 미검토 support를 포함하는 보수적 precision도 함께 보고한다.

위치 오차는 동일 X 구간의 native path Y(없으면 그 candidate Y)를 인간 Y 범위와
비교한다. X 범위가 다르면 보간하지 않고 unmatched로 남긴다. interval coverage와
폭을 함께 보고하며, 예측 interval이나 정답 위치가 없으면 미측정으로 남긴다.
entity 쌍의 consistency는 사람의 동일대상 라벨이 있어야 계산한다.

평가는 자동 합격을 내지 않는다. O2의 실영상 구분력, 독립된 holdout 성능, 내부
증거 중복 사용 검토와 operating point 수용이 끝나야 O3로 넘어간다.
