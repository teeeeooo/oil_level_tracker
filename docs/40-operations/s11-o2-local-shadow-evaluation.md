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

## 영구 보관 위치 — ZIP 교체 전에 분리

코드와 업무 데이터를 분리한다. 아래 경로는 예시이며 에이전트가 실제 경로를 확인한다.

```text
D:\OilTracker\app\                       GitHub ZIP 교체 대상
D:\OilTracker\data\bundles\run-001\    결과 번들 전체
D:\OilTracker\data\reviews\review-001\
    packet.json                           실행 후보·witness (수정 금지)
    labels.json                           장면·후보 판정 (record로 저장)
    labels.json.history\                 저장 전 원본 스냅샷
    bundle-link.json                      번들·원본 영상 연결 증명 및 위치
    bundle-link.json.history\            경로 변경 전 스냅샷
    replies\                             사용자 회신을 옮긴 입력 JSON
```

원본 영상은 업무 PC의 기존 영구 위치에 둬도 된다. 이미 만든 R22-3 번들을 사용한다.
이 도구 변경 때문에 detector를 재실행하거나 R22-4로 바꾸지 않는다. 기존 v1
packet/labels도 그대로 읽는다. 데이터 파일을 Git에 올리거나 ZIP 폴더 안에 두지 않는다.
번들을 이동할 때는 trace만 꺼내지 않고 전체 폴더를 복사하고, 읽기 검증 전 원본은
삭제하지 않는다. 검토 폴더는 history를 포함하여 함께 보관·백업한다. history는
동일 디스크 고장에 대비한 백업을 대신하지 않는다.

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

## 2. 번들 연결 등록

prepare 후 한 번 등록한다. 기존 reader로 packet의 모든 record/witness가 실제 번들과
일치하는지 확인하고 manifest, recipe, session, trace, index의 SHA-256을 저장한다.
원본 영상도 한 번 전체 해시하므로 큰 파일에서는 시간이 걸릴 수 있다.

```powershell
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py link-bundle --labels "D:\OilTracker\data\reviews\review-001\labels.json" --bundle "D:\OilTracker\data\bundles\run-001" --video "D:\media\source.mp4" --reviewer "실제 확인자" --note "이 영상이 해당 번들의 입력 원본임을 확인" --output "D:\OilTracker\data\reviews\review-001\bundle-link.json"
```

이전 번들에는 입력 영상 해시가 없을 수 있다. 최초 영상-번들 대응은 사람의 확인
(`human_attestation`)이며, 해시를 계산했다고 그 대응이 자동 증명되는 것은 아니다.
이후 동일 바이트 확인에는 영상 해시를 사용한다. 장면 식별에는 영상 해시·0-based
프레임·원본 좌표 규격·Glass geometry를 보존한다. 이름/후보 번호만으로 재실행의
동일 장면이라고 확정하지 않는다. 설정·geometry 또는 영상 바이트가 다르면 이후
자동 정답 전사 대상이 아니며 별도 검토가 필요하다. 후보 번호·판정 자동 전사는
이번 도구에 없다.

등록 파일의 경로는 가능하면 상대 경로다. Windows 드라이브가 다르면 절대 경로를
기록한다. 번들/영상을 다른 위치로 옮겼으면 다음을 실행한다. 모든 등록 해시가
같아야 경로만 변경하며, 이전 경로도 이력에 남긴다. 다른 실행으로 교체할 수 없다.

```powershell
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py relink --link "D:\OilTracker\data\reviews\review-001\bundle-link.json" --bundle "E:\data\bundles\run-001" --video "E:\media\source.mp4" --reviewer "실제 확인자" --note "보관 위치 이동"
```

## 3. 에이전트 질문 → 사용자 회신 → 기록·재개

처음에는 한 프레임으로 흐름을 확인하고, 이후 같은 현상을 확인하는 3~5프레임
묶음으로 준비한다. 질문은 한 장·한 판단씩 진행하고 시간 비교가 필요할 때만 앞뒤
프레임을 나란히 보여준다. 전용 GUI는 만들지 않는다. 기존 원본 추출/가이드 도구를
찾아 재사용하며 source-frame 좌표·정확한 프레임·crop offset을 검증한다.

세션 시작/재개 시 다음 status를 읽는다. 표준 출력은 JSON이며 코드 실행 메시지는
표준 오류로 분리된다. 출력의 labels_sha256은 다음 답변 저장의 버전 확인값이다.

```powershell
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py status --labels "D:\OilTracker\data\reviews\review-001\labels.json" --link "D:\OilTracker\data\reviews\review-001\bundle-link.json"
```

status는 packet/label 해시와 연결을 확인하고 미검토·판단 보류 목록, 누락 owner를
보고한다. 경로 존재 여부도 표시하지만 매 질문마다 대용량 영상/trace를 재해시하지
않는다(`live_content_rehashed=false`). 실제 보관물 검증에는 relink를 사용한다.
이미 답한 질문을 반복하지 않고 다음 pending/unreviewed 항목부터 진행한다.
`unresolved`는 사용자가 판단을 보류한 답변으로, 자동으로 재질문하지 않는다.

에이전트는 “A 경로는 실제 계면과 일치 / 계면 근처지만 위치 불일치 / 다른 구조 /
판단 불가 중 무엇인가요?”처럼 중립적으로 묻는다. 다른 구조의 종류를 모르면
반사·잔유로 임의 확정하지 않는다. 기존 확인은 정확한 대상 대응과 원래 판단 근거를
확인해 재사용하며 에이전트가 새로운 인간 판정을 만들어 쓰지 않는다.

회신 한 건을 JSON으로 기록한다. 아래는 **형식 예시**이며 case ID, candidate ID,
witness hash와 판정은 실제 데이터/사용자 회신으로 교체한다. 이 예시는 후보를
판단 보류로 저장하며, 실제 계면 정답이나 contour를 제공하지 않는다.

```json
{
  "reviewer": "실제 판독자",
  "note": "사용자 회신: 이 표시만으로는 판단하기 어렵다.",
  "owners": {
    "label_owner": "정답 관리 담당자",
    "split_owner": "분할 관리 담당자",
    "split_rationale": "이미 검토한 녹화이므로 regression"
  },
  "case_id": "review-001",
  "visibility": "uncertain",
  "candidates": [{
    "candidate_input_index": 0,
    "witness_sha256": "labels.json의 해당 후보 해시",
    "label": "unresolved"
  }]
}
```

```powershell
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py record --labels "D:\OilTracker\data\reviews\review-001\labels.json" --update "D:\OilTracker\data\reviews\review-001\replies\reply-001.json" --expected-sha256 "직전 status의 labels_sha256"
```

- 첫 회신 이후 owners는 생략할 수 있다. owners만 확정하는 별도 회신도 가능하다.
- `visibility`는 visible/not_visible/uncertain. 후보의 `label`은 interface,
  localization_mismatch, reflection, residue, structure, unresolved, unobservable,
  unreviewed 중 하나다. 양성 interface/localization_mismatch는 visible에만 허용한다.
- 확인하지 않은 후보는 그대로 unreviewed에 둔다. 기존 후보를 삭제하지 않는다.
- 장면의 `contour`에는 **실제로 확인한** source X 구간별 Y 허용 범위를 넣는다.
  `source_x_range`는 반열린 구간, `source_y_interval`은 양 끝 포함 범위다.
  정확히 모르면 빈 배열로 둔다. contour 변경은 배열 전체 교체이므로 이전에 확인한
  구간도 포함해야 하며, 생략하면 기존 값을 유지한다.
- `entity_id`는 같은 물리 대상임을 확인했을 때만 기록한다. 생략하면 기존 값 유지,
  null이면 제거한다. source명·거리로 자동 지정하지 않는다.
- 장면의 가시성/contour와 후보의 label은 별도 필드다. scene_review에는 장면 판독
  근거를 보존하며 후보만 수정해도 장면 판독자의 기록을 덮어쓰지 않는다.
- 값·좌표·연결을 검사한 뒤 이전 labels 전체를 history에 보존하고 원자적으로 교체한다.
  review_history에 회신·이전 해시·시각을 남긴다. 오래된 해시나 다른 후보 해시는 거부한다.
  history는 변조 방지 서명이나 판독자 인증 체계는 아니다.
- 쓰기 lock이 있으면 두 에이전트가 동시에 쓰지 않도록 중단한다. 강제 종료 후 lock이
  남았으면 실행 중 writer가 없는지 확인하고 status로 JSON을 읽은 뒤 그 lock만 제거한다.
  오류가 났다고 labels/history를 삭제하거나 prepare로 초기화하지 않는다.
- 파일을 수동 편집하면 위 변경 이력 절차를 우회하므로 이후 판정은 record를 사용한다.
  기존 수동 작성 v1 라벨은 읽지만 과거 편집 이력을 소급 생성하지 않는다.

BASE의 위치 불일치를 반사/구조물 확정 negative로 바꾸지 않는다. 단일 Y를 모든
sector 정답으로 복사하지 않는다. packet과 witness 해시/후보 ID는 수정하지 않는다.

묶음 끝에는 status와 검증 결과에서 검토/미검토/보류 현황 및 미해결 사항만 요약한다.
원본 영상·상세 trace·라벨 원본은 업무 PC 안에 남긴다. 외부 공유는 조직의 허용 범위에
따르며 도구가 자동 업로드하지 않는다. freeze 실패는 누락 항목을 보고하고 원본 판정을
추정해 채우지 않는다.

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

여러 packet을 묶을 때 packet 참조 경로와 라벨을 보존하는 combine을 사용한다.
각 packet의 bundle-link와 history는 원래 검토 폴더에 계속 보관한다. link-bundle은
동일 번들의 검토용이므로 서로 다른 번들을 합친 labels에 새로 등록하지 않는다.
중복 case ID나 충돌하는 owner는 명시적으로 정리해야 한다. 합본 한도는 256 case다.

```powershell
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py combine --labels "D:\o2\A\labels.json" "D:\o2\B\labels.json" --dataset-id "o2-study-01" --output "D:\o2\study\labels.json"
```

## 4. 라벨을 고정하고 준비 상태 평가하기

```powershell
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py freeze --labels "D:\o2\study\labels.json" --output "D:\o2\study\frozen.json"
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py evaluate --frozen "D:\o2\study\frozen.json" --output "D:\o2\study\readiness.json"
```

freeze는 모든 case/후보의 존재, 라벨, 분할, 좌표와 해시를 검증한다. 경로를 제외한
논리 내용의 해시를 고정하므로 폴더를 이동해도 packet 연결 경로를 함께 보존하면 된다.
공백·JSON key 순서는 해시를 바꾸지 않지만 라벨·수치·배열 순서 변경은 바꾼다.
해시는 drift 검사이며 holdout의 미사용 이력을 증명하는 서명이 아니다.
frozen.json은 그 시점의 판정 스냅샷이며 이후 record로 바꿔도 기존 frozen은 바뀌지
않는다. 수정된 판정을 평가하려면 새 이름으로 다시 freeze한다. bundle-link는 별도
출처 기록이므로 frozen과 함께 원래 검토 폴더를 보존한다.

예측을 넣지 않은 결과는 **NOT_EVALUATED**이다. visible인데 후보가 없는 프레임도
분모에 남는다. classifier 성능 PASS로 해석하지 않는다. 지금 단계에서 Windows가
수행할 작업은 이 준비 상태와 라벨 누락을 확인하는 것까지다.

## 5. 이후 shadow classifier가 준비되면

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
