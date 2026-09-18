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
packet/labels도 그대로 읽으며, 새 구간별 기록은 아래 migrate 절차로 labels v2에 저장한다.
데이터 파일을 Git에 올리거나 ZIP 폴더 안에 두지 않는다.
번들을 이동할 때는 trace만 꺼내지 않고 전체 폴더를 복사하고, 읽기 검증 전 원본은
삭제하지 않는다. 검토 폴더는 history를 포함하여 함께 보관·백업한다. history는
동일 디스크 고장에 대비한 백업을 대신하지 않는다.

## 기존 review-001 / review-002 재개 — 먼저 한 번만 변환

**기존 번들에 prepare를 다시 실행하지 않는다.** 새 코드 ZIP만 교체하고
기존 review 폴더의 packet/labels/history/replies/bundle-link는 유지한다.
각 검토 폴더에 아래를 한 번씩 실행한다. 판독자 별칭은 기존 기록의 실제 별칭을
사용하며, 변환 담당자를 새로운 물리적 판독자로 간주하지 않는다.

```powershell
$reviewDir = "D:\OilTracker\data\reviews\review-002"
$pythonExe = ".\.venv\Scripts\python.exe"
$o2Script = "tests/diagnostics/s11_interface_shadow_evaluation.py"
$beforeReview = & $pythonExe $o2Script status --labels "$reviewDir\labels.json" --link "$reviewDir\bundle-link.json" | ConvertFrom-Json
& $pythonExe $o2Script migrate --labels "$reviewDir\labels.json" --output "$reviewDir\labels-v2.json" --expected-sha256 $beforeReview.labels_sha256 --reviewer "기존 기록 담당자 별칭" --note "판정 변경 없이 v2 형식으로 변환"
& $pythonExe $o2Script status --labels "$reviewDir\labels-v2.json" --link "$reviewDir\bundle-link.json"
```

- 이후 status/record/combine/freeze의 `--labels`는 **labels-v2.json**을 지정한다.
  기존 labels.json과 그 history는 보존한다. 둘을 번갈아 편집하지 않는다.
- 이미 schema_version이 `s11-o2-labels-v2`이면 migrate를 반복하지 않는다.
  출력 파일이 이미 있으면 덮어쓰지 않는다. 그 파일의 status와 migration 출처를
  확인해 재개하고, 오류가 있다고 원본이나 이력을 삭제하지 않는다.
- migration에는 원본 논리/파일 해시, 출처 경로, 변환 담당자·시각이 기록된다.
  원본 JSON 스냅샷은 labels-v2.json.history에 저장되고, 과거 review_history는
  그대로 이어진다. **변환만으로 revision_count는 증가하지 않는다.**
- v1 interface/localization_mismatch → identity=interface, reflection/structure/
  residue → non_interface와 해당 artifact_tags, unresolved/unobservable → uncertain,
  unreviewed → unreviewed. 원래 후보 라벨·설명·판독자 등은 legacy_annotation에 보존한다.
- path_reviews는 빈 목록에서 시작한다. 기존 후보 라벨을 모든 sector 판정으로
  복사하지 않는다. 이미 명시적으로 확인한 경로 판정은 원래 회신과 정확한
  frame/X/Y/basis를 대조한 후 별도 record로 옮긴다. 노트에서 추측해 자동 생성하지 않는다.
- review-001은 revision 3, not_visible, non_interface 23개(기존 reflection 6,
  structure 17)가 보존되는지 확인한다. review-002는 revision 4, visible,
  identity=interface IDs 8/9/10/12, unreviewed 19개가 보존되는지 확인한다.
  이 숫자는 전달받은 체크포인트 확인용이며 도구의 분기/정답 규칙이 아니다.
- bundle-link는 변경할 필요가 없다. packet 해시가 유지되어 같은 receipt로 확인된다.
  기존 frozen/report를 덮어쓰지 않고 필요하면 새 이름으로 freeze/evaluate한다.
  no-model 결과 NOT_EVALUATED는 정상이다. 새 번들 재실행이나 사용자 재판정은 필요 없다.

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
새 labels는 `s11-o2-labels-v2`이며 모든 초기 identity는 `unreviewed`, 가시성은
`pending`이다. 자동 정답은 만들지 않는다.

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
`uncertain`은 사용자가 판단을 보류한 답변으로, 자동으로 재질문하지 않는다.
v1의 unresolved/unobservable은 status에서 uncertain으로 읽되 원래 기록은 유지한다.

에이전트는 **질문 전에 이미지를 직접 열거나 표시하고 정확한 파일 경로를 알려준다.**
가이드에는 source-frame Y 눈금과 후보 A/B/C, 질문할 sector/X 구간을 표시한다.
Y 숫자만 질문하지 않는다. 주석 없는 원본도 함께 열 수 있도록 제공한다.
질문은 다음을 분리하고 한 번에 필요한 것만 묻는다.

- 후보 정체: “표시한 후보 A는 전체적으로 실제 유면을 가리키나요, 다른 대상인가요?”
- 경로 적합성: “A의 강조한 구간은 계면 부근인가요, 벗어났나요?”
- 위치 정답: 수치 평가가 필요할 때만 독립적인 X별 Y 범위를 확인한다.

후보가 interface이면서 일부 구간은 off_interface일 수 있다. 전체 후보 판정으로
각 경로점까지 맞다고 기록하지 않는다. structure/reflection은 동시에 기록할 수 있고,
흠집 등 자세한 설명은 artifact_note로 남긴다. 라벨 종류 부족을 사용자의 불명확함으로
바꾸지 않는다. 기존 회신으로 이미 확정한 것은 정확한 대응을 확인해 재사용한다.

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
    "identity": "uncertain"
  }]
}
```

```powershell
.\.venv\Scripts\python.exe tests/diagnostics/s11_interface_shadow_evaluation.py record --labels "D:\OilTracker\data\reviews\review-001\labels.json" --update "D:\OilTracker\data\reviews\review-001\replies\reply-001.json" --expected-sha256 "직전 status의 labels_sha256"
```

- 첫 회신 이후 owners는 생략할 수 있다. owners만 확정하는 별도 회신도 가능하다.
- `visibility`는 visible/not_visible/uncertain. 후보의 `identity`는 interface,
  non_interface, uncertain, unreviewed다. interface는 visible에만 허용한다.
- `artifact_tags`는 reflection/structure/residue/other의 중복 없는 목록이고 복수 선택이
  가능하다. `artifact_note`는 자유 설명이다. 태그가 없어도 non_interface일 수 있다.
  태그 수는 독립 증거 수가 아니며 후보 정체의 표를 늘리지 않는다.
- v1 파일에 기존 `label`을 저장하는 명령도 계속 지원하지만, 새 identity/path 필드는
  migrate한 v2에만 허용한다. 새 형식과 옛 필드를 같은 후보에 섞지 않는다.
- 확인하지 않은 후보는 그대로 unreviewed에 둔다. 기존 후보를 삭제하지 않는다.
- 장면의 `contour`에는 **실제로 확인한** source X 구간별 Y 허용 범위를 넣는다.
  `source_x_range`는 반열린 구간, `source_y_interval`은 양 끝 포함 범위다.
  정확히 모르면 빈 배열로 둔다. contour 변경은 배열 전체 교체이므로 이전에 확인한
  구간도 포함해야 하며, 생략하면 기존 값을 유지한다.
- `entity_id`는 같은 물리 대상임을 확인했을 때만 기록한다. 생략하면 기존 값 유지,
  null이면 제거한다. source명·거리로 자동 지정하지 않는다.
- 장면의 가시성/contour와 후보의 identity는 별도 필드다. scene_review에는 장면 판독
  근거를 보존하며 후보만 수정해도 장면 판독자의 기록을 덮어쓰지 않는다.
- 값·좌표·연결을 검사한 뒤 이전 labels 전체를 history에 보존하고 원자적으로 교체한다.
  review_history에 회신·이전 해시·시각을 남긴다. 오래된 해시나 다른 후보 해시는 거부한다.
  history는 변조 방지 서명이나 판독자 인증 체계는 아니다.
- 쓰기 lock이 있으면 두 에이전트가 동시에 쓰지 않도록 중단한다. 강제 종료 후 lock이
  남았으면 실행 중 writer가 없는지 확인하고 status로 JSON을 읽은 뒤 그 lock만 제거한다.
  오류가 났다고 labels/history를 삭제하거나 prepare로 초기화하지 않는다.
- 파일을 수동 편집하면 위 변경 이력 절차를 우회하므로 이후 판정은 record를 사용한다.
  기존 수동 작성 v1 라벨은 읽지만 과거 편집 이력을 소급 생성하지 않는다.

경로 판정 회신 예시(숫자는 **형식 예시**, 실제 status의 reviewable_geometry와
사용자 답변으로 대체). 이 회신은 후보 정체와 contour를 바꾸지 않는다.

```json
{
  "reviewer": "실제 판독자",
  "note": "사용자가 강조한 경로점은 계면 부근이라고 확인함.",
  "review_basis": "direct_human_review",
  "case_id": "review-002",
  "candidates": [{
    "candidate_input_index": 9,
    "witness_sha256": "해당 후보의 실제 해시",
    "path_reviews": [{
      "geometry_basis": "native_path",
      "source_x_range": [130, 236],
      "source_y": 382,
      "judgment": "near_interface"
    }]
  }]
}
```

- `geometry_basis`: native_path 또는 candidate_center. 정확한 X/Y가 해당 witness에
  있어야 저장된다. sector 번호나 다른 후보의 Y만으로 매칭하지 않는다.
- `judgment`: near_interface/off_interface/uncertain/unreviewed. near_interface는
  질적 판정이며 픽셀 허용 오차를 의미하지 않는다. near_interface에는 visible이 필요하다.
- path_reviews는 **지정한 geometry만 추가·수정**한다. 생략한 구간은 그대로 유지한다.
  빈 목록은 기존 경로 판정을 지우지 않는다. 특정 판정을 미검토로 되돌리려면
  그 geometry에 unreviewed를 명시한다. 변경 전 판정은 history에 남는다.
- 이미 답한 판정을 옮기는 경우 review_basis를 예를 들어
  `prior_direct_review_exact_geometry_checked`로 쓰고 note에 원래 검토 근거를 적는다.
  기록 시각은 이번 저장 시각이며 과거 판독 시각으로 꾸미지 않는다.
- status는 native_path와 candidate_center 각각의 near/off/uncertain/unreviewed 수와
  review_coverage를 보고한다. 경로가 없는 후보는 실제 candidate_center를 대상으로
  검토할 수 있다. 경로 검토 0개여도 후보 정체 검토 완료와 혼동하지 않는다.
  native_path를 검토한 후보에 candidate_center까지 반드시 추가로 검토할 필요는 없다.
  두 중심은 별도 질문이며, 이번에 확인할 목적에 해당하는 쪽만 기록한다.

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

출력은 `s11-o2-shadow-report-v2`이며 입력 라벨 버전도 명시한다. v1 frozen도 읽지만
새 보고서는 v2로만 쓴다. 기존 v1 보고서는 수정하지 않는다.

- 후보 정체 precision/recall, non_interface 오지지, uncertain/unreviewed 지지를 분리한다.
  태그별 집계는 겹칠 수 있지만 후보 정체는 후보당 한 번만 센다.
- `visible_frame_identity_support_recall`은 계면 후보 지지율이다. 기존
  localized-support 이름을 사용하지 않으며 위치가 맞다는 뜻도 아니다.
- `qualitative_path_review`는 전체 후보와 모델이 지지한 후보 각각의 구간 판정·
  미검토 coverage를 표시한다. 부분적 일치를 전체 경로 성공으로 집계하지 않는다.
- `localization.all_interface_proposals`와 `supported_interface_proposals`는 각각
  전체 계면 후보와 지지된 계면 후보의 수치 오차다. 동일 X의 native path Y(없으면
  후보 중심)를 별도로 판독한 contour와 비교한다. candidate/peak 값으로 contour를
  채우지 않는다. X가 다르면 보간하지 않고 unmatched다.
- matched/eligible sector 수와 coverage, 오차·예측 interval 폭/coverage를 함께 본다.
  contour가 없으면 not_measured/null이며 오차 0으로 간주하지 않는다.
  전체 경로의 coverage/허용오차 합격 기준은 아직 없으므로 full_path_localization_pass는 null이다.

entity 쌍의 consistency는 사람의 동일대상 라벨이 있어야 계산한다.

평가는 자동 합격을 내지 않는다. O2의 실영상 구분력, 독립된 holdout 성능, 내부
증거 중복 사용 검토와 operating point 수용이 끝나야 O3로 넘어간다.
