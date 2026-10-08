# S11 O2 로컬 라벨·Shadow 평가 절차

이 절차는 업무 PC 내부의 **O2 평가 준비**를 위한 것이다. detector 재실행,
실제 계면 자동 판정, production 설정 변경, Windows 현장 합격을 수행하지 않는다.
현재 실행 상태는 [work-plan](../00-project/work-plan.md), 판단 기준은
[Witness Validation](../30-validation/s11-interface-observability-witness-validation.md)이 소유한다.

## 실행할 절차 선택

먼저 [W별 진행 상태와 다음 행동](../00-project/work-plan.md#s11-work-item-ledger)을
확인하고 현재 요청에 해당하는 절차만 실행한다. 아래 명령은 재현·재개용으로 보존한
것이며, 문서에 남아 있다는 이유로 완료된 실험이나 migration을 반복하지 않는다.
새 작업은 해당 W의 선행 조건과 입력 범위를 확인한다. 단계 완료 여부는 실행 성공
코드만으로 판단하지 않고 검증 결과를 근거로 work-plan에 반영한다.

## D1 recorded candidate-loss readout — Windows handoff

실행과 [저장된 review-001 대조](#d1-return-reconciliation--saved-review-001-only)의
반환이 완료되었다. D1은 전달된 기록 확인 범위에서 종료했으며,
[정정·종료 근거](../60-evidence/s11/2026-10-08-next-work-intake.md#d1-saved-record-reconciliation--closed)를
보존한다. 아래 최초 실행 명령은 보존용으로, 현재 재실행 요청은 없다.

2026-10-08 다음 작업의 제한된 기록 질의다. 기존 W3 audit의 후보 탈락 경계를
읽으며, 완료된 W3 실행·75개 target binding·사람 판독을 반복하지 않는다.
현재 인계 준비와 로컬 검증은 [intake 기록](../60-evidence/s11/2026-10-08-next-work-intake.md)이 소유한다.

필요한 것은 Python 3와 기존 첫 W3 `experiment.json` 한 파일이다. 도구는 stdlib만
사용하므로 앱 환경이나 OpenCV 설치가 필요 없다. 기존 Windows 데이터 폴더의
`experiments/target-context-audit-001/experiment.json`을 찾는다. 이 경로는 alias이며
실제 데이터 root를 추측하지 않는다. 다른 revision이면 기존에 기록된 해당 파일의
hash/정체성을 먼저 보고하고 멈춘다. 원본이나 기대 hash를 맞추려고 편집하지 않는다.

아래 실행 pin은 2026-10-08 사용자가 전달한 Windows 실제 hash로 정정했다.
[정정 출처와 이전 값](../60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md#d1-raw-file-pin-correction--2026-10-08)을 보존한다.
Windows에서 원본 파일 hash를 직접 계산하고, 첫 target/context audit의 schema
`s11-o2-target-audit-v1`, review-001/002/003의 후보 23/23/27개 및 기존
case/frame/Glass/packet 연결을 확인한다. 다른 dataset/revision이면 실행을 멈추고
차이를 보고한다. 전사 오류라는 설명은 아직 독립 확인되지 않았다.

저장소 루트 또는 별도 D1 ZIP을 푼 폴더에서 PowerShell로 실행한다. 입력 경로는
질문에 실제 전체 경로를 입력한다. 출력 폴더가 이미 있으면 기존 결과를 보존하고
`d1-candidate-loss-002`처럼 새 이름으로 바꾼다.

```powershell
$readerPath = ".\tests\diagnostics\s11_candidate_loss_audit.py"
$readerHash = "c5c4b058cc7d15d25006ab739bb8e851d4f00fe6f4f271c330817536110aad60"
if ((Get-FileHash -LiteralPath $readerPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $readerHash) {
    throw "Reader identity mismatch; stop and report."
}
$auditPath = Read-Host "기존 첫 W3 experiment.json의 전체 경로"
$expectedHash = "ba5fe84b28473f7e387e363ef7d40877f559c80b1852755d997e1dd04171937f"
if ((Get-FileHash -LiteralPath $auditPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) {
    throw "Audit hash differs from the user-reported correction; stop and report."
}
$outputPath = Join-Path (Split-Path -Parent $auditPath) "d1-candidate-loss-001"
py -3 $readerPath --audit $auditPath --expected-sha256 $expectedHash --output $outputPath
if ($LASTEXITCODE -ne 0) { throw "D1 readout failed; preserve inputs/partial output and report the error." }
$receipt = Get-Content -LiteralPath (Join-Path $outputPath "complete.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($receipt.status -ne "COMPLETE" -or $receipt.schema_version -ne "s11-recorded-candidate-loss-v1" -or
    $receipt.source_before_sha256 -ne $expectedHash -or $receipt.source_after_sha256 -ne $expectedHash -or
    $receipt.script_sha256 -ne $readerHash -or $receipt.detector_rerun -ne $false -or
    $receipt.video_read -ne $false -or $receipt.auto_acceptance -ne $false) {
    throw "Invalid D1 completion receipt"
}
foreach ($entry in $receipt.outputs.PSObject.Properties) {
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $outputPath $entry.Name) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $entry.Value) { throw "Output hash mismatch: $($entry.Name)" }
}
Get-Content -LiteralPath (Join-Path $outputPath "summary.md") -Raw -Encoding UTF8
```

`complete.json`은 읽기 작업의 완료만 뜻한다. `readout.json`과 `summary.md`는
새 결과이며 원본 audit·packet·label을 변경하지 않는다. 원본 영상 읽기, detector
실행, 라벨 재작성, 후보 추가, threshold 변경을 하지 않는다.

Windows에서 새 `readout.json`을 확인할 질문은 다음으로 한정한다.

- 세 case와 23/23/27개의 후보가 보존되는지, 누락/UNAVAILABLE가 있는지.
- review-002 idx0 및 review-003 idx10: retained 이전 손실에 대해 추가 기록이 있는지.
- review-002 idx10/12/16: 기록된 authority와 tracklet 미승인, 다른 exclusion의 구분.
- review-002 idx8/9 및 review-003 idx19: admitted row 뒤 실제 allowed mode/owner ID와 최종 선택 기록.
- review-001 admitted 음성 및 review-002 idx20: 같은 admission 조건을 음성도 통과하는지.

반환은 생성된 `summary.md`, `complete.json`, 위 질문의 **기록된 필드 표와 누락 필드**다.
표에는 case/frame, candidate index/offset/source/Y, witness/packet 연결, boundary,
recorded exclusions, phase mode/allowed IDs, selection outcome을 유지한다. 업무 식별
정보의 익명화가 필요하면 공유용 사본에만 적용하고 원본 hash와 구분한다.
전체 `readout.json`, 원본 audit·영상·packet은 Windows 로컬에 보존한다.

물리 label은 원본 broad interface 주석이고 `target_role=NOT_IMPORTED`다. 별도 75개
target batch와 index로 결합하지 않는다. `UNKNOWN_BEFORE_RETAINED_REFS`,
`PHASE_FILTER_UNAVAILABLE`, `FINAL_SELECTION_UNRESOLVED` 등은 확정 원인이 아니며,
없는 필드를 추론으로 채우지 않는다. 자료/필드가 없으면 그 사실과 정확한 missing
field를 반환하고 D1을 종료한다. 새 대규모 조사나 private-video replay로 확대하지 않는다.

## D1 return reconciliation — saved review-001 only

대조 반환 완료. 원본 audit과 readout의 일치가 보고되었으며 review-001은
retained 11 / absent 12로 정정했다. [완료 기록](../60-evidence/s11/2026-10-08-next-work-intake.md#d1-saved-record-reconciliation--closed)이
출처와 한계를 보존한다. 아래는 당시 요청이며 **추가 Windows 조회는 필요 없다**.

2026-10-08 반환 보고의 review-001 집계가 기존 W3 기록과 다르다. 기존 표는
retained 14개/absent 9개(legacy `not_selected` 7개, `tracklet_not_admitted` 7개),
이번 표는 retained 11개/absent 12개다. phase filter를 자세히 분류해도 retained
여부는 바뀌지 않으므로, 어느 표가 원본과 일치하는지 저장된 필드 확인을 요청했다.
[반환 검토 기록](../60-evidence/s11/2026-10-08-next-work-intake.md#d1-windows-return-received--reconciliation-open)이
상충하는 두 보고와 해석 정정을 보존한다.

Windows 에이전트는 기존 첫 audit `experiment.json`과 그 하위
`d1-candidate-loss-001/{readout.json,summary.md,complete.json}`만 읽는다.
새 소스 다운로드, D1/다른 audit 재실행, 영상 읽기나 원본 수정은 필요 없다.

1. 읽기 전후 네 파일의 SHA-256을 계산한다. audit은 위 정정 pin,
   readout은 `e4bf75c4e63c2a0a3fe169a3ff3bb72b99a3e2fbf504ca352358fe55ff923004`,
   summary는 `921fb9fd541295cc26ad60454cf8435a46193fc2f7bdac12d4a20ad14933fe13`과
   대조한다. receipt의 input/tool/output pins도 대조한다. 불일치는 고치지 말고 보고한다.
2. audit의 `target_audit[]`와 readout의 `cases[]`에서 실제 review-001
   `case_id`를 확인하여 각각 하나의 case를 선택한다. `scores[]`의 동일 case와
   readout의 `source_identity`에서 frame 11508, Glass/packet ID를 대조하여 반환한다.
3. 원본 case의 `recorded_funnel`과 해당 readout case의
   `readout.source_funnel`이 같은지 확인한다. 그 funnel을
   `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False,
   allow_nan=False)`로 직렬화한 UTF-8 SHA-256이 `readout.source_funnel_sha256`과
   같은지도 확인한다. 이는 raw 파일 hash와 구분한다.
4. 두 후보 목록을 **candidate_input_index로 결합**하여 23행을 JSON 파서로
   직접 추출한다. 원본 후보의 `status`, `first_known_loss`, member의
   `tracklet_admitted`/`selected`, row의 `phase_admitted`/`publishable`과,
   readout 후보의 `boundary`, `recorded_exclusions`, `selection_outcome`,
   `legacy_first_known_loss`를 반환한다. 각 필드의 존재 여부를 함께 표시하여
   missing/null/false를 구분한다. 중복·누락 index와 양쪽 index 집합 일치도 보고한다.
5. 원본 status/legacy loss, tracklet admission의 존재·값, readout boundary별
   집계를 직접 계산한다. 기존 7/7/9와 이번 0/11/12 중 어느 기록과 일치하는지,
   또는 둘 다 다른지 원본 기준으로 보고한다. case 전체의 phase와 selection도
   key 존재 여부를 보존하여 추출한다.
6. **생성되어 있던 `summary.md`와 `complete.json` 원문**, 위 23행과 검증 결과를
   반환한다. 새 서술형 요약으로 원문을 대체하지 않는다. 원본 파일과 전체 readout은
   Windows에 보존한다. D2 이후 작업은 시작하지 않는다.

선택 key가 존재하며 값이 null이면 `NONE_SELECTED`다. 이 도구의
`FINAL_SELECTION_UNRESOLVED`는 기록된 exclusion이 없고 phase filter가 알려진
미선택 후보의 boundary다. null을 누락된 선택 기록이나 이 boundary로 바꾸지 않는다.
`NOT_IN_RETAINED_REFS`의 member 부재를 admission false로 바꾸지도 않는다.
이 확인은 기록 대조이며 FIELD FAIL/O2 수락 상태를 변경하지 않는다.

## D2 — existing target-bound control query

실행 반환은 [근거 문서](../60-evidence/s11/2026-10-08-d2-control-preflight.md#windows-saved-field-return--query-closed)에
기록되었다. 아래는 재현용 절차이며 현재 재실행 요청이 아니다.
[Windows 내부 support 검토](#d2--windows-only-support-review)도 반환 완료되었다.
현재 이 조회나 support 검토를 재실행하라는 요청은 없다.

목적은 이미 역할 binding이 끝난 Accum drain f17383 한 case의 **26개 후보와
기존 판독 근거·측정 geometry 연결**이다. [D2 설계 진입 계약](../20-architecture/s11-interface-observability-witness-architecture.md#d2-boundary-role-design-entry)과
[고정 query manifest](../50-diagnostics/s11/2026-10-08-d2-control-query.json)를 사용한다.
새 모델을 고르기 전에 필요한 자료 반환이며 D1 재실행이나 target binding 반복이 아니다.

현재 소스를 GitHub에서 받아도 된다. 새 manifest가 포함된 저장소 root와 기존
`data/w4-passive-review-001/target-truth-001/target-truth.json`의 실제 경로를
사용한다. ZIP의 `.git` 부재는 실패가 아니다. 아래 코드는 manifest의 두 reader
SHA와 target artifact/content/physical-label 논리 hash를 확인하고, 기존 loader로
snapshot/packet binding을 검증한다. 다른 파일이나 pin으로 자동 대체하지 않는다.
Python 3.11 이상을 사용하며 앱 실행·detector·영상·새 scene 추출은 없다.

PowerShell에서 `$repo`, `$snapshot`을 실제 경로로 지정한다. 이미 있는 출력은
보존하며 새 `$output` 이름을 선택한다. 원본 JSON이나 packet locator를 수정하지 않는다.

```powershell
$repo = (Get-Location).Path
$snapshot = Read-Host "기존 target-truth-001/target-truth.json 전체 경로"
$query = Join-Path $repo "docs/50-diagnostics/s11/2026-10-08-d2-control-query.json"
$output = Join-Path (Split-Path -Parent $snapshot) "d2-accum-drain-controls-001.json"
@'
import hashlib, json, sys
from collections import Counter
from pathlib import Path
repo, query_path, source, output = [Path(p).resolve() for p in sys.argv[1:]]
def require(ok, message):
    if not ok:
        raise ValueError(message)
def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()
require(not output.exists() and output.parent.is_dir(), 'Choose a new output in an existing directory')
query_before = sha(query_path)
query = json.loads(query_path.read_text(encoding='utf-8'))
require(query['schema_version'] == 's11-d2-control-query-v1', 'Wrong query schema')
require(query['include_all_candidates_in_case'] is True, 'Complete case required')
code_paths = [repo / p for p in query['reader_files']]
require(all(sha(repo / p) == h for p, h in query['reader_files'].items()), 'Reader hash mismatch')
sys.path[:0] = [str(repo / 'src'), str(repo)]
from tests.diagnostics import s11_interface_shadow_evaluation as o2
snapshot = o2.read_json(source)
require(snapshot['artifact_sha256'] == query['target_artifact_sha256'], 'Target artifact mismatch')
require(snapshot['content_sha256'] == query['evaluation_content_sha256'], 'Evaluation content mismatch')
require(snapshot['payload']['mapping']['source_labels_sha256'] == query['source_labels_sha256'], 'Physical-label pin mismatch')
inputs = [query_path, source, *code_paths, *[(source.parent / p['path']).resolve() for p in snapshot['packets']]]
before = {str(p): sha(p) for p in inputs}
require(before[str(query_path)] == query_before, 'Query changed')
frozen, packets = o2.load_frozen(source)
require(frozen['target_truth']['artifact_sha256'] == query['target_artifact_sha256'], 'Loaded artifact mismatch')
spec = query['case']
case = o2.unique(frozen['content']['cases'], 'case_id', 'cases')[spec['case_id']]
frame = packets[case['packet_sha256']][case['case_id']]
require(case['partition'] == spec['partition'] == 'regression', 'Partition mismatch')
require(case['visibility'] == spec['target_visibility'], 'Visibility mismatch')
require(all(frame[k] == spec[k] for k in ('frame_index', 'glass_id')), 'Frame/Glass mismatch')
bindings = [b for b in snapshot['payload']['bindings'] if b['case_id'] == case['case_id']]
by_index = o2.unique(bindings, 'candidate_input_index', 'bindings')
require(set(by_index) == set(range(spec['candidate_count'])), 'Candidate inventory mismatch')
require(dict(Counter(b['target_role'] for b in bindings)) == spec['role_counts'], 'Role counts mismatch')
for role, indices in spec['fixed_role_indices'].items():
    require({i for i, b in by_index.items() if b['target_role'] == role} == set(indices), 'Role indices mismatch')
physical = o2.unique(snapshot['payload']['physical_labels']['cases'], 'case_id', 'physical cases')[case['case_id']]
annotations = o2.unique(physical['candidates'], 'candidate_input_index', 'annotations')
candidates = o2.unique(frame['witness']['candidates'], 'candidate_input_index', 'witness candidates')
require(set(annotations) == set(candidates) == set(by_index), 'Joined inventory mismatch')
rows = [{'binding': by_index[i], 'physical_annotation': annotations[i],
         'geometry': o2.review_geometry(candidates[i]), 'stored_witness': candidates[i]}
        for i in sorted(by_index)]
after = {str(p): sha(p) for p in inputs}
require(before == after, 'Input changed during query')
result = {'status': 'SAVED_FIELDS_ONLY', 'query_sha256': query_before,
          'target_artifact_sha256': snapshot['artifact_sha256'],
          'source_identity': {k: frame[k] for k in ('case_id', 'frame_index', 'glass_id', 'record_id', 'run_id')},
          'packet_sha256': case['packet_sha256'], 'partition': case['partition'],
          'role_counts': spec['role_counts'], 'candidates': rows,
          'input_before_sha256': before, 'input_after_sha256': after,
          'video_read': False, 'detector_rerun': False, 'prediction_or_scoring': False,
          'new_human_review': False, 'auto_acceptance': False}
o2.write_new(output, result)
print(json.dumps({'output': str(output), 'sha256': sha(output),
                  'candidate_count': len(rows), 'role_counts': spec['role_counts'],
                  'input_preserved': before == after}, ensure_ascii=True))
'@ | py -3 - $repo $query $snapshot $output
if ($LASTEXITCODE -ne 0) { throw "D2 saved-field query failed; preserve files and report the error." }
```

반환은 생성된 JSON과 다음의 기계 추출 표로 한정한다. 표는 원문을 수작업 전사하지 않는다.

- 26개 각 후보의 index/source/canonical Y, target role, physical identity,
  witness hash, native/center geometry 유무 및 기존 artifact tags·review note.
- target 4개/internal 3개의 모든 실제 sector X/Y와 측정 availability를 보존한다.
  원래 데이터의 band/scale 구분을 유지하고 material/static/glare 값의 missing/null/0을 구분한다.
- other 19개 중 개별 판독 근거가 실제 저장된 후보가 있으면 그 index와 원문을
  별도로 표시한다. group-reviewed 후보를 개별 검증된 광학 반례로 승격하지 않는다.
- 동일 case에 이미 저장된 plain crop/guide의 경로와 source-frame/geometry 연결
  근거만 찾는다. 알려진 passive 작업 폴더 밖으로 검색하지 않고 새 이미지/영상은
  열거나 만들지 않는다. 없거나 연결을 확인할 수 없으면 그 사실을 반환한다.

이 자료 자체를 cue-sharing 반례, classifier 성능 또는 새 물리 판독으로 선언하지 않는다.
자료가 부족하면 부족한 필드/연결을 적고 종료한다. 다른 case 선택, 재라벨링, 모델 fitting,
추가 metadata 순회로 확대하지 않는다. 고정된 26행의 반환 뒤 Mac 설계 검토가 다음 단계다.

<a id="d2--existing-support-file-transfer"></a>

## D2 — Windows-only support review

**반환 완료 — bounded review CLOSED.** [사용자 판독과 설계 검토 결과](../60-evidence/s11/2026-10-08-d2-control-preflight.md#windows-support-review-and-human-reply--bounded-review-closed)를
기록했다. 아래 프롬프트는 당시 절차 보존용이다. idx13 질문을 다시 묻거나
idx12 추가 표시로 자동 연장하지 않는다. 다음 전환은 Work Plan이 소유한다.

이전 ZIP/PNG 전달 요청은 철회되었다. 보안 PC의 파일 반출은 요구하지 않는다.
이미지와 원본 자료는 Windows에 두고, 사용자가 옮겨 적을 수 있는 **결과 텍스트만**
반환한다. Mac에서 영상을 직접 보지 못하는 것은 이 절차의 정상적인 조건이다.
완료된 D1/D2 조회와 target binding을 반복하지 않는다.

Windows 에이전트에게 아래 프롬프트를 전달한다. 소스 업데이트나 `.git`은 필요 없다.

```text
보안 PC 내부에서 D2 기존 support 검토를 진행해줘. 파일을 외부로 전달할 수 없으며,
사용자가 결과 보고서/텍스트만 Mac으로 옮겨 적을 수 있다. 이미지·ZIP 첨부나
이미지를 인코딩한 텍스트를 요청하지 말고, 허용된 로컬 도구/뷰어만 사용해줘.

완료된 D2 saved-field query와 기존 역할 라벨은 그대로 유지한다.
대상은 w4-passive-001-accum-drain / frame 17383 한 regression 장면이다.
목적은 후보에 연결된 실제 측정 위치에서 구별 근거와 반대 근거를 확인하는 것이다.
새 모델·threshold를 고르거나 26개 후보를 다시 판독하는 작업은 아니다.

기존 입력:
- C:\0.Coding\2.Reference\Oil level tracker\0.windows_diagnostic\data\w4-passive-review-001\target-truth-001\d2-accum-drain-controls-001.json
  raw SHA256: 91e0843e0747e18fd1ec35f0c7a87b37cf00145912f477900fdeca561a906b6b
- 이미 연결을 확인한 bundle의
  debug/frames/8fb6ebc7-7c56-401e-86c3-05514bf6380b_9f8aea91/f000017383_89c161ba4587/original_roi_512ed6ab.png
  raw SHA256: 3a4cc3265479a409acc445f1801c79a8cc3992f1acab1d7f69a287f96babd216
- 기존 accum_drain_f17383_plain.png / guide.png / between_guide.png 표시 자료.
  실제 파일명은 accum_drain_f17383_guide.png와
  accum_drain_f17383_between_guide.png이다. 원본 ROI를 기준으로 대조한다.

1. 기존 JSON/원본 ROI의 hash와 읽기 전후 불변을 확인하되 전체 audit을 반복하지 않는다.
   불일치 시 수정·재생성하지 말고 해당 파일만 보고하고 멈춘다.
   idx10(internal)과 idx13(target)의 저장된 5개 sector씩, 총 10행을 기계 추출한다:
   idx, sector 순서, source_x_range, native path_source_y, candidate_source_y.
   native/center의 X 범위가 다르면 별도 표시한다. 없는 값은 UNAVAILABLE이다.
   source 좌표를 ROI에 지목할 때 저장된 crop_origin=[1199,56]을 적용한다.
   요약된 sector Y를 이어서 원래 continuous contour였다고 가정하지 않는다.

2. 같은 장면의 원본 ROI와 기존 guide를 보안 PC 안에서 대조한다.
   guide가 native path인지 canonical center인지 확인한 범위에서만 사용한다.
   핵심은 idx13 첫 native sector Y315가 실제로 어느 특징에 놓이는지다.
   같은 후보의 나머지 네 sector 및 idx10 첫 sector Y302와 정확한 X 범위를 함께 본다.
   이 구간이 실제 target 경계를 따르는지, 다른 특징에 놓이는지, 가림/해상도 때문에
   판단할 수 없는지를 관측 근거와 함께 기술한다. Y 차이만으로 결론 내리지 않는다.
   이미지상 관찰과 물리적 해석을 구분하고, 기존 target 라벨은 바꾸지 않는다.

3. 같은 장면에서 이미 개별 판독된 non-target native 후보 idx11/12/14/15의
   기존 근거와 측정 위치를 확인한다. 이 중 target idx13과 실제로 비슷한 local cue를
   공유하는 반례가 관측된다면 최대 1개만 제안하고, 해당 sector X/Y, 공유하는 cue,
   구별 근거 또는 구별 불가능한 이유를 적는다. 없거나 확인할 수 없으면
   NOT_ESTABLISHED로 끝낸다. 단순히 가장 가까운 Y/높은 점수로 고르지 않는다.
   idx10은 실제 내부 경계 대조이며 반사/구조 음성의 대체물이 아니다.
   나머지 group negatives를 다시 판독하거나 다른 장면으로 확대하지 않는다.

4. 에이전트의 이미지 관찰을 human_review로 기록하지 않는다.
   물리적 판단에 사용자가 필요하면 Windows 화면에 실제 해당 구간을 보여주고,
   무엇이 미결인지 설명한 뒤 그 구간에 대한 질문 하나로 멈춘다.
   허용된 도구로 이미지를 확인할 수 없으면 그 제한을 적고 로컬 뷰어에서 사용자가
   볼 위치를 안내한다. 파일 반출을 대안으로 요청하지 않는다.
   이미 답한 target 정의나 전체 후보 identity를 다시 묻지 않는다.

반환은 옮겨 적기 쉬운 짧은 텍스트 보고서:
- INPUT: 기존 case/record, 두 입력 hash 일치와 전후 불변 PASS/FAIL.
- GEOMETRY: 위의 10행 표.
- OBSERVATION: idx13 첫 sector, 나머지 sector/idx10 대조의 관찰과 해석 한계.
- COUNTER_CONTROL: 후보 하나의 정확한 support와 근거, 또는 NOT_ESTABLISHED.
- HUMAN: 필요 없음 / 미해결 질문 하나 / 실제 사용자 답변(받은 경우만).
- CHANGES: 원본·라벨·소스 변경 없음, detector/video 실행 없음.

숫자는 JSON에서 기계 추출하고 관찰/추론/사용자 답변을 구분해줘.
전체 JSON/이미지/ZIP은 반출하지 않는다. D1/D2 query/bind-target 재실행,
영상 재생·decode, 새 이미지 생성, fitting, source 수정, commit/push는 하지 않는다.
```

이 반환은 Windows 관측에 근거한 텍스트 증거다. Mac에서 직접 이미지를 보았다고
기록하지 않으며, 에이전트 관찰만으로 truth나 O2 acceptance를 갱신하지 않는다.
구별 근거가 확인되지 않으면 미해결 조건을 보존하고 설계 가능 범위를 평가한다.

## Structure-context schema 문자 검증

사용자가 True/111을 확인했다. 실제 schema는 소문자 o의 `o2`이며 전달 표기만
잘못된 것으로 정리했다. 아래 검사는 재현용으로 보존하며 현재 반복 요청은 없다.

숫자 문맥 추가 반환은 완료되었다. 같은 후보 값이나 영상을 다시 요청하지 않는다.
두 번 반환된 schema의 `02`가 코드의 `o2`와 달라, 기존 출력에 아래 읽기 전용
검사만 실행한다. `$auditOutput`은 기존 structure-context-audit-001 폴더,
`$pythonExe`는 기존 Python 경로로 지정한다. JSON 내용을 수정하지 않는다.

```powershell
@'
import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
expected = "s11-" + chr(111) + "2-structure-context-audit-v1"
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
paths = [root / n for n in ("complete.json", "experiment.json", "summary.md")]
before = {p.name: h(p) for p in paths}
receipt = json.loads(paths[0].read_text(encoding="utf-8-sig"))
report = json.loads(paths[1].read_text(encoding="utf-8-sig"))
for name, obj in (("complete", receipt), ("experiment", report)):
    value = obj.get("schema_version")
    print(name, "is_string=", isinstance(value, str), "matches_expected=", value == expected,
          "codepoint_at_4=", ord(value[4]) if isinstance(value, str) and len(value) > 4 else None)
print("artifact_receipt_equal=", receipt.get("artifact_sha256") == report.get("artifact", {}).get("sha256"))
for name in ("experiment.json", "summary.md"):
    print(name, "matches_receipt_hash=", before[name] == receipt.get("outputs", {}).get(name))
print("read_preserved=", before == {p.name: h(p) for p in paths})
'@ | & $pythonExe - $auditOutput
```

표준 출력을 그대로 반환한다. 기대값은 두 schema 모두 matches_expected=True,
codepoint_at_4=111(소문자 o); 숫자 0은 48이다. 결과가 다르면 오타로 단정하거나
자동 수정하지 말고 그대로 보고한다. receipt/artifact/hash/read-preserved도
모두 True가 기대값이다. 이 검사는 classifier 성능 평가가 아니다.

## Structure-context 결과의 제한된 추가 반환

추가 반환 완료. 아래는 당시 요청을 보존한 것이며 현재 반복 요청은 없다.

실행 완료 보고와 코드/artifact 대조 결과는
[Windows 근거](../60-evidence/s11/s11-o2-structure-context-audit-windows-run-001.md)에
기록했다. 아래는 **이미 생성된 `structure-context-audit-001` 출력만 읽는 요청**이다.
새 소스 다운로드나 실험 재실행은 필요 없다. 숫자와 ID는 이미지/기억으로 옮기지
말고 JSON 파서로 추출한다.

- complete.json과 experiment.json의 `schema_version` 원문. 기대값은
  `s11-o2-structure-context-audit-v1` (소문자 o)이다. 다르면 수정하지 말고 그대로 보고.
- `target_audit[]`에서 세 case의 `case_id`와
  `recorded_funnel.structure_context`의 `record_id`, `glass_id`, `frame_index` 원문.
- 같은 structure_context의 candidates를 **candidate_input_index로 검색**하여:
  review-001 idx10; review-002 idx0/8/10/11/20; review-003 idx10/15.
  각 후보의 source, canonical_y, rejected, reject_reason과 아래 필드들을 반환.
- features와 penalties **각각**의 container state 및 fields 내
  `artifact_likelihood`, `static_prior_contribution`, `static_artifact_penalty`,
  `material_texture_conflict`, `optics_conflict`, `glare_conflict`,
  `calibrated_artifact_match`, `material_terminal_partition_support`,
  `boundary_likelihood`의 **state/value 원문**. missing/null/0을 합치지 않는다.
- 파일 전체나 과거 summary를 다시 작성하지 않고 선택한 JSON만 반환한다.
  읽기 전후 experiment.json/complete.json 해시가 같은지도 보고한다.

review-001 idx10은 기록상 template 제거 사례, 나머지는 identity 실패/양성 대조와
모호한 쌍의 문맥을 확인하는 제한된 집합이다. 정확도 평가 분모나 threshold 선정
집합으로 사용하지 않는다. template 존재만으로 identity를 판정하거나, 이 조회를
위해 labels/packet을 고치지 않는다. 이전 s1/s2 판정 충돌은 review-002 **idx10**,
Y=213/RefY=212 출처 문제는 review-003 **idx10 reference guide**라는 점도 유지한다.

## Recorded structure-context audit — 원래 번들만

실행 완료가 보고된 절차이며 아래 명령은 재현용이다. schema 문자 확인까지 완료되었으며 현재 추가 실행 요청은 없다.

목적: 별도 구조물 음성 후보(idx11 등)의 실패를 조사하기 위해, O1 band 표에는
빠져 있는 **원래 후보의 artifact/static/texture 관련 필드와 등록된 artifact
template 목록**이 R22-3 번들에 실제로 존재하는지 확인한다. 새로운 판별식의
성능 실험이 아니다. idx0/idx20의 모호함을 강제로 해소하거나 라벨을 바꾸지 않는다.

1. 새 `--structure-context` 옵션이 포함된 GitHub 소스 revision을 다운로드한다.
   별도의 변경 파일 ZIP은 필요 없다. 기존 `89acfb0` ZIP만으로는 실행할 수 없다. `--help`에서 옵션을 확인하고 실제
   commit(알 수 있으면), 변경 파일 SHA-256, Python 버전을 보고한다. 수정된
   소스의 실행을 이전 commit 단독 실행으로 표기하지 않는다.
2. 기존 W3와 같은 labels rev3/14/4, packet 3개, 원래 indexed R22-3 번들,
   최초 `fixed-score-current-labels-001/experiment.json`을 사용한다. 라벨 파일은
   모두 schema `s11-o2-labels-v2`; reference artifact는
   `655689e19d6fa3231bf4667b3af38b4ffa285f94b27aa9df30684a02867f9cf9`.
   경로만 실제 Windows 위치로 바꾼다. 원본 영상은 필요 없다.
3. 이미 존재하는 출력 폴더는 보존하고 새 이름으로 실행한다.

```powershell
$dataRoot = "D:\OilTracker\data"
$bundleRoot = "D:\OilTracker\bundles\R22-3"
$auditOutput = Join-Path $dataRoot "experiments\structure-context-audit-001"
$pythonExe = ".\.venv\Scripts\python.exe"
$labelsOne = Join-Path $dataRoot "reviews\review-001\labels-v2.json"
$labelsTwo = Join-Path $dataRoot "reviews\review-002\labels-v2.json"
$labelsThree = Join-Path $dataRoot "reviews\review-003\labels.json"
$reference = Join-Path $dataRoot "experiments\fixed-score-current-labels-001\experiment.json"
& $pythonExe tests/diagnostics/s11_shadow_experiment.py `
  --labels $labelsOne $labelsTwo $labelsThree `
  --target-audit --structure-context --bundle $bundleRoot `
  --reference $reference --output $auditOutput
if ($LASTEXITCODE -ne 0) { throw "Structure context audit failed; preserve inputs and report the error." }
$receipt = Get-Content -LiteralPath (Join-Path $auditOutput "complete.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$report = Get-Content -LiteralPath (Join-Path $auditOutput "experiment.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($receipt.status -ne "COMPLETE" -or $receipt.schema_version -ne "s11-o2-structure-context-audit-v1") {
    throw "Invalid completion receipt"
}
if ($report.schema_version -ne $receipt.schema_version -or $report.artifact.sha256 -ne $receipt.artifact_sha256) {
    throw "Artifact/receipt mismatch"
}
foreach ($entry in $receipt.outputs.PSObject.Properties) {
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $auditOutput $entry.Name) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $entry.Value) { throw "Output hash mismatch: $($entry.Name)" }
}
if ($report.reference.inputs_scores_evaluation_equal -ne $true -or
    $report.reference.artifact_sha256 -ne "655689e19d6fa3231bf4667b3af38b4ffa285f94b27aa9df30684a02867f9cf9") {
    throw "Reference mismatch"
}
if ($report.input_preservation.Count -ne 12) { throw "Unexpected input inventory; investigate without modifying sources" }
foreach ($entry in $report.input_preservation) {
    if ($entry.before_sha256 -ne $entry.after_sha256) { throw "Input changed during run" }
}
if ($report.auto_acceptance -ne $false -or $report.production_decisions_emitted -ne $false -or
    $report.field_disposition -ne "FIELD FAIL" -or $report.numeric_localization -ne "NOT_MEASURED") {
    throw "Unexpected decision status"
}
Get-FileHash -Algorithm SHA256 tests/diagnostics/s11_shadow_experiment.py, tests/diagnostics/s11_shadow_target_audit.py
Get-Content -LiteralPath (Join-Path $auditOutput "summary.md") -Raw -Encoding UTF8
```

반환할 것: **자동 생성 summary.md 전문**, 실제 코드 식별값, 라벨 revision,
COMPLETE·출력 해시·입력 12개 보존·reference 일치 결과. 상세 JSON은 로컬에
보존한다. 원래 W3의 band/sequence 내용도 JSON에 남으며, 새 요약에는 후보별
features/penalties의 present 값(0 포함), missing/null 개수, template 목록을
출력한다. template note/geometry와 각 필드의 상태는 JSON에서 확인 가능하다.

해석 규칙:

- `vessel_fitting_geometry_unavailable`은 template 미등록을 증명하지 않는다.
  이번에는 raw recipe의 등록 상태를 직접 확인한다. 빈 목록은 물리적 구조물
  부재가 아니다. 일치 점수나 `rejected`도 사람 identity 정답이 아니다.
- static은 지속성, texture는 기존 계산값이다. 독립된 물리적 근거로 격상하거나
  label별 수치를 보고 threshold/가중치를 선정하지 않는다.
- raw field 미기록, null, 0은 구분해서 보고한다. sequence witness가 UNAVAILABLE여도
  `recorded_funnel.structure_context`는 별도로 존재할 수 있다.
- 실패 시 라벨/packet/trace를 고치거나 새로 추출하지 않는다. 기존 입력·출력을
  보존하고 오류를 반환한다. 새 영상, 재라벨링, detector 재실행, template 등록,
  calibration/freeze 및 production 변경은 이 절차에 포함되지 않는다.

## Candidate identity 문맥 확인 — 기존 두 프레임만

기존 두 프레임의 확인과 출처·좌표 대조 결과는
[Windows 근거](../60-evidence/s11/s11-o2-identity-context-windows-review-001.md)에
기록했다. 아래 절차는 재현용으로 보존하며 현재 추가 실행 요청은 없다.
사용자는 경계의 오르내림과 유면 형성 모습을 앞뒤 약 5초씩 확인했지만, idx0/idx20이
실제 두 층인지 잔류액의 반사인지 확정하지 못했다고 설명했다. idx20의 더 강한 반사는
당시 선택 근거였으나 실제 유면도 강하게 반사할 수 있어 모호했다. 이 설명을 라벨
변경으로 간주하지 않는다. 같은 영상을 다시 요청하지 않고 평가 해석에 불확실성을
반영한다. [기존 평가 체계의 불확실성 처리 점검](../60-evidence/s11/s11-o2-reference-uncertainty-evaluation-audit.md)은
로컬 대조 테스트로 완료했으며 이를 위한 Windows 실행은 필요하지 않다. 과거 reply와
현행 판정을 섞거나 guide 숫자를 이미지 판독으로 재추정하지 않는다. 수치 연결은
packet/labels를 사용하고, 생성 코드의 hardcode나 guide는 그 권위를 대체하지 않는다.

이번 작업은 기존 사람이 판독한 근거가 현재 witness에 표현되어 있는지 확인한다.
새 점수 계산·라벨링·영상 구간 확장이 아니다.
[로컬 근거](../60-evidence/s11/s11-o2-identity-context-source-audit.md)를 먼저 읽는다.

1. 현재 라벨 revision 3/14/4와 기존 packet/bundle-link 연결을 유지한다.
   review-002와 review-003의 frame/Glass/source identity를 packet에서 확인한다.
2. 범위는 review-002 idx0, idx10, idx11, idx20 / review-003 idx10, idx15다.
   이 여섯 후보는 기존 두 프레임에 한정된다. idx는 해당 packet의 번호다.
3. 먼저 기존 replies, review_note, artifact_note 및 연결된 과거 직접 판독 기록을
   읽는다. 사람의 실제 문구와 출처를 인용한다. 추론을 사용자 판정으로 저장하지 않는다.
4. 이미 저장된 주석 없는 원본 crop/전체 프레임을 보고, 이어서 기존 guide와 대조한다.
   없으면 원래 bundle의 original_roi 자산을 exact frame/Glass로 찾는다. 자산이
   없거나 연결을 입증할 수 없으면 그 사실을 보고하고 임의의 인접 프레임을 쓰지 않는다.
   detector 실행이나 새 영상 탐색은 필요하지 않다.
5. 다음 열로 표를 반환한다: review/idx, 기존 identity, 직접 판독 인용·출처,
   실제 확인한 원본 이미지·frame/Glass, 관찰 근거와 이미지 범위,
   witness의 대응 필드 또는 누락 정보, 같은 근거를 가질 반례, 남은 불확실성.
   직접 판독과 에이전트의 새 관찰을 명확히 분리한다.

미리 정한 답을 찾지 않는다. 주변 영역의 연결·띠의 끝·구조물 모양·시간 문맥은
실제로 확인된 경우만 적는다. 단일 이미지에서 정지/움직임을 추측하지 않는다.
정답 Y와의 거리, 높은 점수, source 알고리즘, phase/선택 결과만으로 새 identity
근거를 만들지 않는다. 기록이 단순히 interface/non_interface만 말하면 그 이상의
인간 판독 근거는 미기록으로 남긴다. 기존 라벨을 재질문·변경하지 않는다.

라벨·packet 및 읽은 기존 자산은 수정하지 않고, 원본 JSON/영상은 Windows에
보존한다. 새 표를 파일로 저장한다면 기존 파일을 덮어쓰지 않는 새 분석 문서로
만든다. 읽은 파일의 실행 전후 해시와 연결 확인 결과를 함께 반환한다.
자료 부족 시 없는 항목만 보고한다. W3/W4 실험 재실행, contour/freeze, 점수식·
임계값 변경, SPL#2/3 또는 새로운 시간 구간 검토는 이 요청에 포함되지 않는다.

## 사람 판정의 불확실성과 기존 평가 해석

이 항목은 실행 명령이 아닌 결과 해석 기준이다.
[계약](../20-architecture/s11-interface-observability-witness-architecture.md#human-reference-uncertainty-and-model-abstention)에
따라 다음을 구분한다.

- labels의 `uncertain`은 사람이 검토했으나 미확정인 상태, `unreviewed`는
  미검토 상태다. 모델의 `UNRESOLVED`/`UNOBSERVABLE`과 별개다.
- 후속 설명에서 모호성이 드러나더라도 기존 라벨을 자동 변경하지 않는다.
  원래 결과의 correct/reversed는 고정된 라벨과의 일치/불일치이며, 보고서
  해석에는 해당 근거 문서의 불확실성 설명을 함께 제시한다.
- 불확실한 정답에 대한 모델의 지지는 검증된 성공이 아니다. conditional
  precision/accuracy만 떼어 보고하지 않고 unverified support, abstention,
  missing과 전체 후보·point·frame 분모를 함께 읽는다. 판단 보류가 많다는
  사실만으로 안전성이나 성공을 주장하지 않는다.
- 정식 라벨 수정이 별도로 요청되면 기존 revision/history 절차로 기록하고,
  새 freeze/hash에 대응하는 평가를 별도로 보존한다. 과거 frozen/output을
  덮어쓰거나, pair가 줄어든 것을 점수식 개선으로 합산하지 않는다.
- 이 기록은 모델 예측값을 만들거나 임계값을 고르는 근거가 아니다. 기존
  score 실험의 tie/null을 임의로 `UNRESOLVED` 예측으로 변환하지 않는다.

현재 idx0/idx20에 대한 정식 라벨 수정, 재평가 또는 추가 영상 요청은 없다.

## W4 paired-scale — 기존 라벨 실행

**첫 실행은 [Windows 결과](../60-evidence/s11/s11-o2-w4-paired-scale-windows-run-001.md)로 완료되었다.**
아래는 재현 절차이며 현재 재실행 요청은 없다. 기존 기본 W3 audit도 반복하지 않는다. 별도 structure-context 확장은 위의 해당 절차를 따른다.
같은 X의 두 경로점에서 동일 band width의 점수 차이를 먼저 구한 뒤 중앙값을
계산하는 방법을 시험한다. 기존 C/A/L 점수식과 locality는 유지한다.
후보 identity 분류기 구현이나 detector 개선 완료를 뜻하지 않는다.
[고정 가설·기각 기준](../50-diagnostics/s11/s11-o2-fixed-score-experiment.md#w4-paired-scale-local-comparison)을
따르며, 효과가 없으면 이 결과도 보존한다.

1. 새 코드 ZIP을 코드 폴더에 적용하고 기존 영구 데이터 폴더를 유지한다.
   실행 소스 commit/ZIP 식별값과 `s11_shadow_experiment.py` SHA-256을 기록한다.
2. 기존 status 도구로 review-001 `labels-v2.json` rev3, review-002
   `labels-v2.json` rev14, review-003 `labels.json` rev4를 확인한다.
   모두 schema `s11-o2-labels-v2`여야 한다. 파일명이나 revision을 맞추려고
   라벨을 변경하지 않는다. 차이가 있으면 실행 대신 보고한다.
3. 최초 `fixed-score-current-labels-001/experiment.json`을 사용한다.
   reference artifact SHA는
   `655689e19d6fa3231bf4667b3af38b4ffa285f94b27aa9df30684a02867f9cf9`다.
   W3/profile/ablation 출력 또는 frozen 파일로 대체하지 않는다.
4. 아래 `$dataRoot`, `$pythonExe`만 실제 환경에 맞춘다. 출력 폴더가 이미
   존재하면 삭제·덮어쓰기 없이 `paired-scale-002`처럼 새 이름을 사용한다.
   원래 packet 상대 경로를 유지한다. 번들·원본 영상은 필요하지 않다.

```powershell
$dataRoot = "D:\OilTracker\data"
$pythonExe = ".\.venv\Scripts\python.exe"
$pairOutput = Join-Path $dataRoot "experiments\paired-scale-001"
$labelsOne = Join-Path $dataRoot "reviews\review-001\labels-v2.json"
$labelsTwo = Join-Path $dataRoot "reviews\review-002\labels-v2.json"
$labelsThree = Join-Path $dataRoot "reviews\review-003\labels.json"
$reference = Join-Path $dataRoot "experiments\fixed-score-current-labels-001\experiment.json"
$expectedReference = "655689e19d6fa3231bf4667b3af38b4ffa285f94b27aa9df30684a02867f9cf9"
$prior = Get-Content -LiteralPath $reference -Raw -Encoding UTF8 | ConvertFrom-Json
if ($prior.artifact.sha256 -ne $expectedReference) { throw "Unexpected reference artifact" }
& $pythonExe tests/diagnostics/s11_shadow_experiment.py `
  --labels $labelsOne $labelsTwo $labelsThree `
  --paired-scale --reference $reference --output $pairOutput
if ($LASTEXITCODE -ne 0) { throw "Paired-scale run failed; preserve inputs and report the error." }
$receipt = Get-Content -LiteralPath (Join-Path $pairOutput "complete.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($receipt.status -ne "COMPLETE" -or $receipt.schema_version -ne "s11-o2-paired-scale-v1") {
    throw "Invalid completion receipt"
}
foreach ($entry in $receipt.outputs.PSObject.Properties) {
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $pairOutput $entry.Name) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $entry.Value) { throw "Output hash mismatch: $($entry.Name)" }
}
$report = Get-Content -LiteralPath (Join-Path $pairOutput "experiment.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($receipt.artifact_sha256 -ne $report.artifact.sha256) { throw "Artifact mismatch" }
if ($report.reference.inputs_scores_evaluation_equal -ne $true) { throw "Reference mismatch" }
if ($report.reference.artifact_sha256 -ne $expectedReference) { throw "Unexpected reference" }
foreach ($entry in $report.input_preservation) {
    if ($entry.before_sha256 -ne $entry.after_sha256) { throw "Input changed during run" }
}
Get-Content -LiteralPath (Join-Path $pairOutput "summary.md") -Raw -Encoding UTF8
```

자동 생성 `summary.md` 전문과 다음 검증 결과를 반환한다.

- 코드 식별값·artifact SHA, 라벨 revision/schema, reference 일치.
- COMPLETE, 출력 해시 2개, 입력 해시 보존(통상 7개: 라벨3＋packet3＋reference1).
- `EXPLORATORY_UNCALIBRATED` / `auto_acceptance=false` / `FIELD FAIL` /
  `numeric_localization=NOT_MEASURED` 유지.

summary의 `paired_scale` 결과가 이번 실험이다. 최상위 `scores`/`evaluation`은
기존 v1 재현값이므로 새 방식의 결과로 혼동하지 않는다. native_path 위치 비교와
non_interface 대조를 분리하고 candidate_center는 별도로 읽는다. 양쪽 공통
scale 위에서의 개선·악화와 legacy→공통 support 변화도 구분한다. pair=0은
성공이 아니며 모든 task 수를 합산하지 않는다. 상세 JSON은 Windows에 보존한다.

새 라벨, contour, freeze, detector 실행, 점수·임계값 조정, partition 변경은
수행하지 않는다. 수치를 수동 전사하거나 결과가 유리하도록 공식을 수정하지 않는다.

## W4 결과 후속 — 기존 JSON의 잔여 pair 확인

**추출과 대조가 완료되었다.** [결과 기록](../60-evidence/s11/s11-o2-w4-paired-scale-windows-run-001.md#follow-up-remaining-pair-inspection)을 참고한다.
아래는 당시 요청을 보존한 것이며 현재 추가 추출·재실행 요청은 없다.

추가 실험 없이 `experiments/paired-scale-001/experiment.json`만 읽는다.
`paired_scale`에서 `case_id=review-002`, `tasks`의
`native_path/interface_location_same_x`를 선택한다. `pairs` 중
`paired_outcome`이 `reversed` 또는 `unscorable`인 원본 객체를 그대로 반환한다.
현재 보고 기준 각각 1개다. 다르면 맞추지 말고 차이를 보고한다.

원본 객체에는 positive/negative 후보·basis·X·Y, legacy/joint/paired outcome,
두 difference, common_band_widths/common_scale_count, scales, excluded_scales가
포함되어야 한다. 수동 숫자 전사 없이 JSON으로 추출하고 입력 SHA-256 전후를
확인한다. 나머지 pair나 전체 private JSON 반출은 필요하지 않다.

목적은 남은 역전과 결측 원인을 구분하는 것이다. 이 확인으로 새 공식·임계값을
선택하지 않는다. detector·실험 재실행, 라벨 수정, freeze는 수행하지 않는다.

## W3 target/context audit — 기존 자료로 실행

**첫 실행은 [Windows 보고](../60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md)로 완료되었다.**
현재 추가 실행 요청은 없으며, 아래는 재현 절차다. 기존 라벨 후보에 어떤 문맥
측정값과 결정 과정이 기록되어 있는지 확인한다. 다음 W4 개선안을 선택하기 위한
점검이며, 새 점수식·분류기·라벨을 만들거나 detector를 다시 실행하지 않는다.

1. 최신 소스 ZIP을 코드 폴더에 풀고 영구 데이터 폴더는 그대로 둔다.
2. 기존 `status`로 활성 라벨을 확인한다: review-001 `labels-v2.json` revision 3,
   review-002 `labels-v2.json` revision 14, review-003 `labels.json` revision 4.
   세 파일 모두 schema `s11-o2-labels-v2`여야 한다. 각 packet 연결을 유지한다.
   다르면 맞추려고 수정하지 말고 차이를 보고한다.
3. **최초 fixed-score v1**의 `experiment.json`을 reference로 지정한다.
   알려진 폴더명은 `fixed-score-current-labels-001`, artifact SHA는
   `655689e19d6fa3231bf4667b3af38b4ffa285f94b27aa9df30684a02867f9cf9`다.
   locality/profile 결과나 예전 frozen r10/r3로 대체하지 않는다.
4. 해당 packet을 추출했던 **원래 R22-3 번들 폴더**를 `--bundle`로 지정한다.
   manifest, recipe_snapshot, session 및 indexed debug trace가 있어야 한다.
   이번 절차에서는 bundle을 생략하지 않는다. 원본 영상은 읽지 않는다.
5. 아래 세 경로만 실제 경로로 바꿔 저장소 루트에서 실행한다. 출력 폴더가 이미
   있으면 삭제하지 말고 `target-context-audit-002`처럼 새 이름을 쓴다.

```powershell
$dataRoot = "D:\OilTracker\data"                 # 기존 영구 데이터 폴더
$bundleRoot = "D:\OilTracker\bundles\R22-3"      # 원래 번들 폴더
$auditOutput = Join-Path $dataRoot "experiments\target-context-audit-001"
$pythonExe = ".\.venv\Scripts\python.exe"
$labelsOne = Join-Path $dataRoot "reviews\review-001\labels-v2.json"
$labelsTwo = Join-Path $dataRoot "reviews\review-002\labels-v2.json"
$labelsThree = Join-Path $dataRoot "reviews\review-003\labels.json"
$reference = Join-Path $dataRoot "experiments\fixed-score-current-labels-001\experiment.json"
& $pythonExe tests/diagnostics/s11_shadow_experiment.py `
  --labels $labelsOne $labelsTwo $labelsThree `
  --target-audit --reference $reference --bundle $bundleRoot --output $auditOutput
if ($LASTEXITCODE -ne 0) { throw "Target audit failed; preserve inputs and report the error." }
$receipt = Get-Content -LiteralPath (Join-Path $auditOutput "complete.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($receipt.status -ne "COMPLETE" -or $receipt.schema_version -ne "s11-o2-target-audit-v1") {
    throw "Invalid completion receipt"
}
foreach ($entry in $receipt.outputs.PSObject.Properties) {
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $auditOutput $entry.Name) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $entry.Value) { throw "Output hash mismatch: $($entry.Name)" }
}
$report = Get-Content -LiteralPath (Join-Path $auditOutput "experiment.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($report.reference.inputs_scores_evaluation_equal -ne $true) { throw "Reference mismatch" }
foreach ($entry in $report.input_preservation) {
    if ($entry.before_sha256 -ne $entry.after_sha256) { throw "Input changed during run" }
}
Get-Content -LiteralPath (Join-Path $auditOutput "summary.md") -Raw -Encoding UTF8
```

검증 오류나 reference 차이가 있으면 자동으로 라벨/packet을 고치거나 후보를 빼지
않는다. 부분 출력은 성공 결과로 취급하지 않는다. 오류 메시지와 어떤 입력이 다른지
보고하고 멈춘다. 새 detector 실행으로 대체하지 않는다.

출력은 `experiment.json`, 자동 생성 `summary.md`, `complete.json`이다.
`EXPLORATORY_UNCALIBRATED`, `auto_acceptance=false`, `FIELD FAIL`이 유지된다.
기존 점수는 재현 검사일 뿐 예측으로 변환하지 않는다. 따라서 target 집계의
`MISSING_PREDICTION`과 scalar `not_measured`는 예상된 상태다.

- 문맥 표: 후보/basis별 static overlap, material mean, glare의 가용 band 수와
  median/min/max. 서로 상관된 scale/band의 기술 통계이며 임계값 근거가 아니다.
  상세 JSON에는 전체 band의 missing/null/present와 나머지 문맥 필드가 남는다.
- 결정 과정 표: 원래 candidate offset·source·Y가 일치하는 **기록된** tracklet,
  phase, publishable, selected 상태. `UNKNOWN_BEFORE_RETAINED_REFS`는 더 앞의
  authority/top-k 원인을 구분할 기록이 없다는 뜻이다. `UNAVAILABLE`도 그대로
  보고한다. 기록된 sequence 선택이 최종 CSV 발행을 증명하는 것은 아니다.
- 라벨, history, packet, bundle-link와 기존 frozen/실험 파일은 보존한다.
  추가 질문, contour 생성, freeze/combine/evaluate, 영상 편집·재실행은 필요 없다.

**전달할 결과**: 코드 commit/ZIP 식별값, 라벨 revision과 논리 해시, artifact SHA,
COMPLETE·출력 해시·reference 재현·입력 전후 해시 검사 결과(검사 파일 수 포함),
그리고 **생성된 summary.md 내용**. case ID가 업무 식별정보이면 익명화한다.
수치를 직접 다시 작성하지 않는다. 전체 JSON·원본 영상·이미지·trace·실제 경로는
Windows 로컬에 보존한다. 오류/연결 불가 항목도 함께 전달한다.

이 결과를 받은 뒤 W4의 한 가지 가설과 필요한 대조를 결정한다. 기존 자료에 없는
정보를 확인하기 위한 추가 실행은 그때 구체적인 공백을 근거로 요청한다.

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

## 고정 점수 shadow 실험 — 기존 라벨로 실행

첫 실행은 **새 판독 없이** 기존 review-001/002/003의 현재 v2 labels와 packet을 사용한다.
목적은 후보/구간의 점수 순서를 정답과 자동 비교하는 것이며, calibrated classifier나
production detector를 실행하는 것이 아니다. [점수식·평가 계약](../50-diagnostics/s11/s11-o2-fixed-score-experiment.md)을 먼저 확인한다.

1. 새 코드 ZIP을 코드 폴더에만 풀고 기존 영구 데이터 폴더를 유지한다.
2. 실제 활성 v2 라벨 경로를 확인한다. review-001/002는 보통 `labels-v2.json`,
   review-003은 저장 당시 이름에 따라 `labels.json` 또는 `labels-v2.json`이다.
   파일명이 아니라 `schema_version=s11-o2-labels-v2`로 확인한다.
   최신 보고 기준 revision은 각각 **3 / 14 / 4**이며, 이후 정당한 새 기록이 있으면
   그 차이를 보고한다. 맞추려고 labels/history를 수정하지 않는다.
3. 각 파일의 기존 `status`로 revision, 연결, 소유자, 논리 해시를 확인한다.
   중복 case ID나 검증 오류가 있으면 원본을 고치거나 후보를 빼지 말고 오류를 보고한다.
4. 새 출력 폴더를 지정해 아래 명령을 실행한다. `--labels`는 파일 경로 세 개를 받는다.
   frozen r10/r3, comparison JSON, 원본 영상은 입력으로 넣지 않는다.

```powershell
# 아래 네 경로를 실제 로컬 경로로 바꾼다. review-003 파일명은 직접 확인한다.
$labelsOne = "D:\OilTracker\data\reviews\review-001\labels-v2.json"
$labelsTwo = "D:\OilTracker\data\reviews\review-002\labels-v2.json"
$labelsThree = "D:\OilTracker\data\reviews\review-003\labels.json"
$experimentOutput = "D:\OilTracker\data\experiments\fixed-score-001"
$pythonExe = ".\.venv\Scripts\python.exe"
& $pythonExe tests/diagnostics/s11_shadow_experiment.py --labels $labelsOne $labelsTwo $labelsThree --output $experimentOutput
if ($LASTEXITCODE -ne 0) { throw "Shadow experiment failed; do not treat partial output as complete." }
$receipt = Get-Content -LiteralPath "$experimentOutput\complete.json" -Raw -Encoding UTF8 | ConvertFrom-Json
foreach ($entry in $receipt.outputs.PSObject.Properties) {
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $experimentOutput $entry.Name) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $entry.Value) { throw "Output hash mismatch: $($entry.Name)" }
}
Get-Content -LiteralPath "$experimentOutput\summary.md" -Raw -Encoding UTF8
```

다른 cwd에서는 Python과 스크립트도 절대 경로로 지정한다. 새 pip 의존성은 없고
프로젝트의 기존 환경을 사용한다. 실행 중 라벨을 편집하지 않는다. 결과 폴더가 이미
있으면 재실행을 위해 원본을 삭제하지 말고 새 이름을 쓴다.

출력은 `experiment.json`, `summary.md`, `complete.json`이다. 완료 receipt가 없거나
해시가 맞지 않으면 부분 실패다. 도구는 입력의 전후 바이트 해시를 검사하며 원본
라벨·packet·history·bundle-link·frozen 파일을 수정하지 않는다. `status`는
`EXPLORATORY_UNCALIBRATED`, `auto_acceptance=false`, `FIELD FAIL`을 유지한다.
공식 `evaluate --predictions` 입력으로 이 결과를 넘기지 않는다.

세 방법은 `contrast_only`, `alignment_only`, `combined`다. 결과 해석:

- `identity_ordering`: 실제 계면 후보가 비계면 후보보다 높은 점수를 받는지.
- `interface_location`: interface 후보 안에서 near가 off보다 높은지. 같은 X만 비교한
  별도 집계도 확인한다. native_path와 candidate_center는 합치지 않는다.
- `identity_negative_control_same_x`: 실제 계면/near와 비계면/off의 대조다.
  Accum idx10/15의 비교는 여기에 해당하며 순수한 위치 오차 평가가 아니다.
- `improved/regressed`: 같은 유효 scale·구간을 사용하는 pair에서 combined가 기준
  방식의 오순서/동률을 올바른 순서로 바꿨는지, 또는 올바른 순서를 잃었는지.
- `unscorable`, 공통 scale/point 수, 미검토 수를 함께 본다. 계산 불가나 pair=0은 성공이
  아니다. 실제 계면 없는 review-001에서 높은 순위가 나와도 계면이라고 판정한 것은
  아니며, 이 실험에는 무계면을 기각하는 합격 임계값이 없다.

외부 전달용은 허용되는 범위에서 다음만 요약한다. 전체 JSON·영상·이미지·실제 경로는
로컬에 남기고, summary.md의 case ID가 업무 식별정보라면 익명 ID로 바꿔 요약한다.

- 사용 코드 ZIP/commit(알면), artifact SHA, 라벨 revision/논리 해시, 실행 성공 여부
- 리뷰별 identity와 native_path 위치 평가의 correct/reversed/tie/unscorable 수
- combined의 기준 방식 대비 improved/regressed 수와 가장 중요한 실패 1~3건
- 공통 유효 구간 부족·미검토 상위 후보 등 평가 한계, 입력 해시 보존 여부

새 라벨 생성, 780초 이후 탐색, partition 변경, detector 재실행, 임계값 조정은 요청하지 않는다.

## Locality 제거 대조 실험 — 첫 실행 결과 보존

고정 점수 첫 실행이 끝난 뒤 사용하는 절차다. 새 코드 ZIP은 코드 폴더에만 적용한다.
기존 review-001/002/003의 활성 v2 라벨(revision 3/14/4)과 packet, 첫 실행의
`experiment.json`·`summary.md`·`complete.json`은 그대로 보존한다.

1. 첫 실행 결과 폴더의 `complete.json`에 기록된 출력 해시를 위 절차대로 확인한다.
2. 위의 `$labelsOne`, `$labelsTwo`, `$labelsThree`, `$pythonExe`를 실제 경로로 설정한다.
   라벨은 첫 실행과 같은 순서로 지정한다. 새 prepare/freeze나 라벨 변경은 하지 않는다.
3. `$referenceExperiment`를 **첫 실행의 v1 experiment.json**으로 지정한다.
   이전에 만든 비교표나 `analysis-review-002-reversals.json`이 아니다.
4. 존재하지 않는 새 출력 폴더에 다음 명령을 실행한다.

```powershell
$referenceExperiment = "D:\OilTracker\data\experiments\fixed-score-current-labels-001\experiment.json"
$ablationOutput = "D:\OilTracker\data\experiments\locality-ablation-001"
& $pythonExe tests/diagnostics/s11_shadow_experiment.py --labels $labelsOne $labelsTwo $labelsThree --locality-ablation --reference $referenceExperiment --output $ablationOutput
if ($LASTEXITCODE -ne 0) { throw "Locality ablation failed; preserve inputs and report the error." }
$receipt = Get-Content -LiteralPath "$ablationOutput\complete.json" -Raw -Encoding UTF8 | ConvertFrom-Json
if ($receipt.schema_version -ne "s11-o2-locality-ablation-v1" -or $receipt.status -ne "COMPLETE") { throw "Unexpected ablation receipt" }
foreach ($entry in $receipt.outputs.PSObject.Properties) {
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $ablationOutput $entry.Name) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $entry.Value) { throw "Output hash mismatch: $($entry.Name)" }
}
Get-Content -LiteralPath "$ablationOutput\summary.md" -Raw -Encoding UTF8
```

도구가 기존 입력·v1 점수·평가의 정확한 재현을 먼저 검증한다. `reference ... differs`
오류가 나면 기존 라벨·결과를 수정하거나 새 기준 파일을 만들어 통과시키지 말고 오류를
보고한다. 이전 코드로 영상 detector를 다시 실행할 필요는 없다. Python/코드·스크립트
경로가 달라졌으면 기존 프로젝트 환경을 지정하며 새 의존성 설치는 필요 없다.

출력 파일명은 기존과 동일하지만 **새 폴더**에 생성한다. 새 JSON의
`locality_ablation[].common_support`와 `ca_supported`가 이번 결과다.
최상위 `scores`/`evaluation`은 재현 검증한 기존 방식 결과이므로 새 결과로 혼동하지 않는다.
`reference.inputs_scores_evaluation_equal=true`와 전체 입력 전후 해시도 확인한다.
원래 라벨 3+packet 3에 기준 experiment.json이 더해져 보통 입력 7개가 보존 검증된다.

이번 방법은 `without_locality=(C*A)^(1/3)`이다. 지수와 중앙값 집계를 유지한다.

- **common_support**: 기존과 동일 구간에서 without_locality가 combined 및 두 기준
  방식 대비 개선/악화하는지 확인한다. 이것이 locality 제거 자체의 대조다.
- **ca_supported**: far band가 없어도 C/A가 있으면 계산한다. 새 계산 가능 pair의
  correct/reversed/tie 수와 여전히 계산 불가인 수를 따로 본다. 기존에 계산 가능했던
  pair도 scale/point 추가로 중앙값 순서가 달라질 수 있으며 `retained_changed_order`로 표시한다.
- 두 부분을 합쳐 개선 건수를 만들지 않는다. identity와 위치, all-X와 same-X도 합산하지 않는다.

전달할 내용은 자동 생성된 요약에 근거한 아래 항목이다. 원본 자료는 로컬에 남긴다.

1. 코드/새 artifact 및 기준 artifact 식별값, revision, 재현·완료·해시 보존 여부.
2. 리뷰/task별 common_support의 without_locality correct/reversed/tie/unscorable,
   combined·contrast·alignment 대비 improved/regressed.
3. ca_supported의 newly_scorable 결과, still_unscorable, retained_changed_order.
4. 기존 BASE idx8 near Y397 vs idx10 off Y378의 같은 X 비교와 idx0 vs idx11
   identity 비교가 어떻게 바뀌었는지, 새 악화 사례가 있는지. 이 후보 번호는 보고용이며
   점수식의 조건으로 사용하지 않는다.

새 판독, 영상 탐색, 임계값 조정, detector 실행, production 판정 반영은 하지 않는다.
첫 실험과 마찬가지로 `EXPLORATORY_UNCALIBRATED`, `auto_acceptance=false`, FIELD FAIL이다.

## 후보 identity profile 실험 — 두 영역과 띠·기울기 비교

Locality 제거 대조 이후의 별도 가설 실험이다. 같은 review-001/002/003의 활성
v2 라벨(revision **3/14/4**)과 packet을 사용한다. 목적은 후보 주변의 네 밝기
band가 두 영역의 경계에 가까운지, 띠나 밝기 기울기에 가까운지를 비교하는 것이다.
새 점수 이름은 `two_region_profile`이다. 구조물도 같은 밝기 형태를 만들 수 있어
점수가 높다는 이유만으로 실제 계면을 확정하지 않는다.

새 코드 ZIP을 코드 폴더에 적용하고 기존 프로젝트 Python을 사용한다.
아래 경로는 예시이며 Windows의 영구 데이터 위치로 바꾼다. review-003은 파일명이
`labels.json`이어도 schema가 v2이면 정상이다. **기준 파일은 최초 고정 점수 실행의
v1 experiment.json**이며 locality-ablation 결과가 아니다. 먼저 해당 폴더의
complete.json에 기록된 출력 해시를 위 절차대로 확인한다.

```powershell
$pythonExe = ".\.venv\Scripts\python.exe"
$labelsOne = "D:\OilTracker\data\reviews\review-001\labels-v2.json"
$labelsTwo = "D:\OilTracker\data\reviews\review-002\labels-v2.json"
$labelsThree = "D:\OilTracker\data\reviews\review-003\labels.json"
$referenceExperiment = "D:\OilTracker\data\experiments\fixed-score-current-labels-001\experiment.json"
$profileOutput = "D:\OilTracker\data\experiments\identity-profile-001"
& $pythonExe tests/diagnostics/s11_shadow_experiment.py --labels $labelsOne $labelsTwo $labelsThree --identity-profile --reference $referenceExperiment --output $profileOutput
if ($LASTEXITCODE -ne 0) { throw "Identity profile failed; preserve inputs and report the error." }
$receipt = Get-Content -LiteralPath "$profileOutput\complete.json" -Raw -Encoding UTF8 | ConvertFrom-Json
if ($receipt.schema_version -ne "s11-o2-identity-profile-v1" -or $receipt.status -ne "COMPLETE") { throw "Unexpected profile receipt" }
foreach ($entry in $receipt.outputs.PSObject.Properties) {
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $profileOutput $entry.Name) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $entry.Value) { throw "Output hash mismatch: $($entry.Name)" }
}
Get-Content -LiteralPath "$profileOutput\summary.md" -Raw -Encoding UTF8
```

출력은 새 폴더의 `experiment.json`, `summary.md`, `complete.json` 세 파일이다.
기존 reference 입력·점수·평가가 정확히 재현되지 않으면 출력 전에 실패한다.
오류가 나면 원본을 수정하거나 reference를 새로 만들어 통과시키지 않는다.
`reference.inputs_scores_evaluation_equal=true`, 입력 7개 전후 해시 보존도 확인한다.

새 결과 위치는 `identity_profile[].common_support`와 `profile_supported`다.
최상위 `scores`/`evaluation`은 기존 v1 재현 자료다.

- **common_support**: 다섯 방법 모두 계산 가능한 동일 scale/point에서 후보 identity를
  비교한다. 새 필수 입력 때문에 v1보다 범위가 줄어들 수 있다.
- **profile_supported**: 네 band profile만으로 계산 가능한 범위에서 새 점수를 평가한다.
  newly_scorable의 correct/reversed/tie와 retained_changed_order를 별도 보고한다.
- 위치 near/off 평가는 이번 모드에서 수행하지 않는다. native_path는 후보 점수를
  측정하는 좌표로 사용하며, 그 점들의 near/off 판정을 identity로 바꾸지 않는다.

Windows 에이전트가 전달할 요약:

1. 코드 commit/새 artifact 및 기준 artifact 식별값, revision, 재현·완료·해시 보존 여부.
2. 리뷰별 common_support의 다섯 방법 correct/reversed/tie/unscorable,
   새 방법의 각 기준 대비 improved/regressed 및 계산 가능 후보·scale 범위.
3. profile_supported의 support 변화, 새 계산 가능 pair 결과, 결측 사유.
4. review-002 idx0 vs idx11의 identity 순서와 점수, 새 악화 사례 최대 3개.
   review-001의 top 후보와 review-002/003의 미검토 top 후보는 자동 판정하지 않는다.

자동 `summary.md`와 JSON에 있는 값을 사용하고 수치를 수동 재계산하거나 별도
비교 스크립트를 만들지 않는다. 허용된 범위의 요약만 전달하고 원본은 업무 PC에 둔다.
추가 영상·라벨링·freeze·detector 실행·임계값 조정은 필요 없다.
상태는 `EXPLORATORY_UNCALIBRATED`, `auto_acceptance=false`, FIELD FAIL을 유지한다.


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
분모에 남는다. classifier 성능 PASS로 해석하지 않는다. 이 준비 절차에서는 라벨 누락과 준비 상태만 확인한다. 현재 실행할 절차는
문서 상단과 work-plan을 따른다.

## 5. 이후 shadow classifier가 준비되면

새 W3 모델 연결은 [prediction v2 계약](../20-architecture/s11-interface-observability-witness-architecture.md#w3-separated-shadow-targets)을
사용한다. 아래 v1 설명은 호환성용이다. v2에는 target/operating-point 식별값,
명시적 evaluation_regime와 각 후보의 local_support/scalar가 필요하다.
탐색용 v2 예측만 `evaluate --exploratory`로 평가한다(regression 전용, fit_partitions=[]).
CALIBRATED의 기존 분할 검증은 유지한다. 현재 target/context audit에서는 예측을
작성하거나 이 명령을 실행하지 않는다. 사람이 라벨을 복사하여 예측을 만들지 않는다.


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

예측 v1 또는 예측 없는 실행은 `s11-o2-shadow-report-v2`로 출력한다.
예측 v2는 `s11-o2-shadow-report-v3`로 분리된 target 집계를 추가한다.
입력 라벨 버전도 명시하며 v1 frozen도 계속 읽는다. 기존 보고서는 수정하지 않는다.

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

## Ordered spatial context — existing two source frames

Purpose: retain the vertical order of raw-gray appearance outside existing O1
bands, using only the two previously reviewed source frames. This is a measurement
probe, not a new identity score, detector run, video interval or labeling request.
The [architecture](../20-architecture/s11-interface-observability-witness-architecture.md#w4-ordered-spatial-context--measurement-prototype)
and [local adapter evidence](../60-evidence/s11/s11-o2-spatial-context-source-adapter-local.md)
define provenance, baseline checks and limitations. FIELD FAIL remains unchanged.

Use the newly published source containing
`tests/diagnostics/s11_spatial_context_run.py`. A GitHub ZIP is sufficient; `.git`
is not required. Record the download commit and generated artifact/code hashes.
Use the existing Windows Python environment with this checkout's dependencies.
Resolve the existing local paths; do not create new review records or relink files:

- review-002 `labels-v2.json`, v2 schema, revision **14**, sibling `bundle-link.json`;
- review-003 `labels.json`, v2 schema, revision **4**, sibling `bundle-link.json`;
- original R22-3 bundle used for the preceding audits;
- original `SPL#1_Heating_coldstart.mp4` whose bytes match both existing bundle links.

Expected targets are review-002 frame **14386** (BASE), review-003 frame **16280**
(Accum). Use exact Glass IDs from validated records, not manually copied report
UUIDs. The program retains all existing candidates and both geometries within
these two frames, without filtering by labels. Review-001 is excluded from this
bounded source-image question; no SPL#2/SPL#3 or new time interval is requested.

PowerShell, from the new source root (replace paths with actual local locations):

```powershell
$labels002 = 'C:\actual\review-002\labels-v2.json'
$labels003 = 'C:\actual\review-003\labels.json'
$originalBundle = 'C:\actual\oil_level_analysis_R22-3개선_add_artifact_20260918_091507'
$originalVideo = 'C:\actual\SPL#1_Heating_coldstart.mp4'
$probeOutput = 'C:\actual\experiments\spatial-context-001'
python tests/diagnostics/s11_spatial_context_run.py `
  --labels "$labels002" "$labels003" --expected-revisions 14 4 `
  --bundle "$originalBundle" --video "$originalVideo" --output "$probeOutput"
```

The output must be new and outside both review directories and the bundle.
The CLI verifies existing video bytes, bundle identity, packet-to-indexed-trace,
scene/frame/Glass, crop geometry and revision before measuring. Stale link locators
are harmless because bundle/video paths are explicit; their identity hashes must
still match. If any identity/revision/crop/frame check fails, stop and return the
exact error. Do not edit the inputs, retry at another frame, or weaken checks.
This command does not use the earlier score `--reference`: it makes no scores and
retains the original O1 witness plus an explicit gray/support reconstruction check.

Verify COMPLETE and every output hash, including all generated images/plots:

```powershell
$receipt = Get-Content -LiteralPath (Join-Path $probeOutput 'complete.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$report = Get-Content -LiteralPath (Join-Path $probeOutput 'experiment.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($receipt.schema_version -cne 's11-o2-spatial-context-v1' -or $receipt.status -cne 'COMPLETE') { throw 'Invalid receipt' }
if ($report.schema_version -cne $receipt.schema_version -or $report.artifact.sha256 -cne $receipt.artifact_sha256) { throw 'Artifact mismatch' }
foreach ($entry in $receipt.outputs.PSObject.Properties) {
  $actual = (Get-FileHash -LiteralPath (Join-Path $probeOutput $entry.Name) -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -cne $entry.Value) { throw "Output hash mismatch: $($entry.Name)" }
}
foreach ($entry in $report.input_preservation) {
  if ($entry.before_sha256 -cne $entry.after_sha256) { throw "Input changed: $($entry.file_index)" }
  $actual = (Get-FileHash -LiteralPath $entry.path -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -cne $entry.after_sha256) { throw "Input changed after run: $($entry.file_index)" }
}
$report.cases | Select-Object case_id,frame_index,glass_id,revision,@{Name='baseline';Expression={$_.baseline_check.status}},@{Name='mismatched_bands';Expression={$_.baseline_check.mismatched_band_count}}
```

Expected flags: `EXPLORATORY_UNCALIBRATED`, `decision=NOT_EVALUATED`,
`auto_acceptance=false`, `production_decisions_emitted=false`,
`field_disposition=FIELD FAIL`, `numeric_localization=NOT_MEASURED`.
Input preservation normally covers **12 unique files**: five bundle files, two
labels, two packets, two links and one video. If actual count differs, report the
inventory; do not assume the count alone proves preservation.

Return the **program-generated summary.md**, source commit, artifact/code hashes,
COMPLETE/output/input-hash results and each case's baseline status/counts. Keep
full JSON and images local. Summary contains exact candidate-to-profile mappings;
use those numbers rather than OCR. PNGs are unannotated decoded source/crop/gray
and masks; SVGs plot raw gray versus source Y, with gaps and original candidate
markers. A difference in baseline bands is a reconstruction issue to inspect
before attributing differences to full-height sampling; it is not detector failure
or a reason to relabel. No automatic brightness threshold or physical conclusion
is generated, even when the run is COMPLETE. No additional human image judgment
is requested by this execution step.

## Ordered spatial context — stored-output inspection

The `spatial-context-001` run has reported COMPLETE/MATCH; receipt photograph,
count correction and supplied summary reconcile intake. Do not rerun the command
above. No new checkout/runtime is required for this inspection. Use only the
existing output folder: `experiment.json`, receipt, SVGs and source/crop/gray/mask
PNGs. Check consumed output hashes against the receipt locally; no repeated
human transcription of hashes/UUIDs is requested. Detailed JSON/images stay local.

Read profile arrays, points and `baseline_witness` directly from JSON. Figures
show shape, but numeric X/Y/intensity/counts must come from JSON, never OCR or
visual coordinate estimates. This is a qualitative correspondence inspection,
not a peak-selection/threshold fitting experiment. Do not invent transitions
when glare, crop clipping, sparse support or gradual appearance prevent a clear
observation. Do not equate zero glare with absence of reflection.

Bounded targets (confirm case/profile mappings from JSON before inspection):

| Case | Profiles | Markers / purpose |
|---|---|---|
| BASE review-002 | 5,6,7 | Native idx8/idx9 and structure-negative idx11 on three exact common X intervals |
| Accum review-003 | 5,6,7,8,9 | Native idx10 and idx15 on five exact common X intervals |
| BASE review-002 | 0,1,2,3,4 | Candidate-center idx0/idx20; unresolved human control, no required separation |

Each profile is shared by all candidates with the same X. Inspect appearance
around each candidate's distinct Y marker on that profile, not a comparison of
identical full-height arrays pretending they are candidate-specific scores.
Native-path and candidate-center remain separate. Positive identity does not
certify every native sector; preserve existing near/off qualifiers if used.

For each of the eight primary X strips, return a compact row containing:

1. case/profile/exact X, candidate IDs and JSON Y markers;
2. the original O1 band coverage for each examined marker, obtained from its exact
   candidate/X/center role/source Y/scales in `baseline_witness`; convert local Y
   ranges using crop origin; retain gaps rather than replacing a disjoint union
   with its bounding interval. If the matching center/band is absent, say so;
3. visible appearance beyond those sampled bands: sustained change, a further
   transition/return, no clear additional change, or not assessable. These are
   descriptive observations, not class labels. Link the source crop region and
   profile region; if citing row values/positions, extract them programmatically;
4. visible/effective/glare-excluded support at any cited rows and intervening null
   gaps. Never interpolate a missing interval to assert persistence or a return;
5. whether the added context appears different around the compared markers,
   shared/ambiguous, or censored. A structure can make a sustained step and a real
   interface can coexist with a return/reflection. No physical inference follows
   from shape alone.

Summarize the idx0/idx20 unresolved control separately across its five X strips;
do not force a 24px difference or stronger reflection into a decision. The
user's +/-5s observation already failed to establish physical identity confidently.
No additional clip or human relabeling is requested.

Return the bounded table and a short account of what extra appearance is actually
visible versus absent/ambiguous/censored. If the agent cannot open the plots/raw
images, report that limitation rather than claiming visual inspection. Optional
analysis notes must go to a separate new folder, outside the immutable experiment
output; preserve all original hashes. Do not add scores/descriptors, choose
thresholds, register templates, regenerate profiles, or run the detector. Report
FIELD FAIL/NOT_EVALUATED unchanged. This is the already-defined image/profile
correspondence step, not a new filming or qualification phase.


## Unpooled O1 spatial context — existing saved outputs

Use the current GitHub source and existing Python environment from the successful
spatial run. This is the next executable handoff, not a repeat of the original
video probe. Input is the intact `spatial-context-001` output folder (receipt,
JSON, PNGs and SVGs); no original video, bundle, labels or new human judgment is
needed. The tool checks the old receipt and saved pixels directly.

From the repository root in PowerShell, replace only the two directory paths:

```powershell
python tests/diagnostics/s11_joint_context_run.py `
  --source "D:\...\experiments\spatial-context-001" `
  --expected-source-artifact "6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910" `
  --output "D:\...\experiments\joint-context-001"
```

Choose a new output folder outside the old one. The source artifact is the
already-reconciled value; do not request another manual hash transcription. A
failure should be returned with its error; do not change the source files,
relax a baseline check or rerun the video detector to get past it.

Open `joint-context-001/viewer.html` in a browser. Select each target point by
exact case, candidate index, geometry basis, X and Y. Select existing band widths
to see separate recorded intervals. Turn overlays off for image inspection, and
uncheck Selected X strip to view the full crop. A coincident candidate/native
center can share O1 bands; `band_binding` and `recorded_role` expose that alias.
The four aligned panels show original crop, raw gray, O1 gradient magnitude and
absolute vertical derivative. Source Y increases downward. Magenta means an
invalid five-pixel stencil; black means valid zero. Preview scales are fixed
analytically (no per-image normalization); the NPZ arrays own exact values.

Use the same bounded comparisons, not the full candidate inventory:

| Case / basis | Exact X | Candidate markers | Purpose |
|---|---|---|---|
| review-002 / native_path | [130,236], [236,343], [343,449] | idx8 / idx9 / idx11 at their stored Y | Compare joint transition arrangement versus remote structure region |
| review-003 / native_path | [1218,1303], [1303,1388], [1388,1473], [1473,1558], [1558,1643] | idx10 / idx15 at their stored Y | Compare transition shape without row/column pooling |
| review-002 / candidate_center | [0,115], [115,231], [231,346], [346,462], [462,578] | idx0 Y382 / idx20 Y406 | Human-unresolved control; no required distinction |

Return one compact row per X comparison with exact geometry, a concrete
pixel/gradient appearance observation, mask/glare/border limitation, and one of
`different appearance`, `shared/ambiguous`, or `not assessable`. Describe whether
a transition extends across X, splits, terminates, or remains too weak to inspect.
Do not call an apparent extension a computed connected component or physical
Oil/structure boundary. Do not use the brightest edge, distance from a known
boundary, pixel polarity, or rejected flag as identity. A different appearance
is not a correct classification. Keep native and candidate-center views separate.
The human idx0/idx20 uncertainty stays unresolved even if image patterns differ.

Return generated `summary.md`, COMPLETE/output-hash/input-preservation checks and
that compact inspection together. Read coordinates/values from JSON/NPZ, not
image text. For two cases the tool emits 13 hashed outputs plus complete.json;
count programmatically. It rehashes the 31 original outputs plus their receipt,
not the earlier 12 video/bundle/label inputs. Preserve all original outputs and
keep detailed NPZ/JSON/images local. A separate new note may hold observations.
If the viewer/images cannot be inspected, report that boundary explicitly.

There is no new score, detector run, label change, threshold or image acquisition.
After this bounded inspection, decide from the evidence whether a specific joint
appearance hypothesis merits further work or should close without promotion.
Do not automatically request more metadata extractions or user relabeling.


## Unpooled O1 spatial context — report reconciliation

The joint run has been reported COMPLETE with artifact matching local source.
Use the existing `joint-context-001` outputs and separate analysis notes/code;
no new checkout, experiment rerun, video/labels or human verdict is needed.
[Evidence intake](../60-evidence/s11/s11-o2-joint-context-windows-run-001.md)
records the accepted scope and unresolved interpretation. Do not reopen the
source artifact by requesting another manual hash transcription.

1. Reconcile the custom statistic for review-003 / native idx10 /
   X[1388,1473] / sourceY217. The transfer lists vertical max 0.008 and 83/85
   columns with vm>0.05, which cannot both refer to raw valid pixels in the same
   window. Return the original extraction definition/code: NPZ key, units,
   source/local ranges, validity mask and reduction axes. For an explicit
   +/-60 inclusive-row check, origin[1199,56] gives local Y[101,222), X[189,274)
   and source Y[157,278). Return raw maximum and the count of columns containing
   any valid value>0.05 over that identical slice. This only checks the existing
   claim; it does not establish a classifier threshold. If the original max is
   a maximum of averages or uses another window, distinguish that quantity.
   Correct any other affected rows programmatically using the identified cause.
2. Complete the three originally requested BASE same-X comparisons, with one
   observation row per X: [130,236] idx8/9/11 Y397/382/901;
   [236,343] Y396/406/925; [343,449] Y397/419/922. Compare the three markers within
   each X, not one candidate from each of three different X strips. Give concrete
   appearance and mask limitations; mark censored comparisons not assessable.
3. Qualify assertions of no transition or an unbroken contour: for the current
   uint8 central difference and fixed display scales, an exact valid PNG zero
   denotes zero derivative, while a visually dark nonzero byte may be weak signal.
   A zero central difference does not prove uniform raw pixels; invalid endpoints
   do not establish physical termination or continuity. Equal thresholded column counts
   are not equal intensity distributions. Preserve idx0/idx20 ambiguity without
   another human review. Keep corrected notes outside the original output.

Return the narrow correction and any remaining limitation together. Do not
replace immutable JSON/NPZ/receipts or change detector, labels or thresholds.


## W4-R3 — existing saved material inventory

목적: 새 분석을 시작하기 전에 **SPL#1 480–780초의 기존 저장 자료 중 실제 유면과
구조물을 대조할 근거가 남아 있는지** 확인한다. [로컬 검토](../60-evidence/s11/s11-o2-w4-r3-existing-evidence-feasibility.md)가
알려진 사례와 재사용 owner를 정리한다. W4-R0/R1은 종료됐으며 이번 작업은 자료
존재·연결·기존 판독 근거의 inventory다. 새 판독이나 challenger 실험이 아니다.

### Windows 에이전트 전달 지시

GitHub ZIP으로 옮긴 현재 소스에서 work-plan의 W4-R3 handoff와 이 절차를 읽는다.
`.git`이 없어도 정상이다. 사용자 제공 ZIP 식별과 실제 파일 경로를 기록하되 검증하지
못한 commit을 검증했다고 쓰지 않는다. 새 패키지 설치나 전용 script 구현은 필요 없다.

**입력 범위:** 기존 `data/reviews` 또는 bundle-link가 가리키는 review 폴더,
`data/joint-context-001-notes` 등 기존 S11 판독 메모 폴더, 원래 R22-3 번들의
manifest/review_index/debug_index 및 그 인덱스로 지정한 소수 record와 저장 이미지.
실제 경로는 기존 작업 기록에서 확인한다. 원본 영상 파일을 열거나 decode하지 않는다.
SPL#2/3, 480–780초 밖의 자료, 디스크 전체 탐색, 모든 과거 번들 조사는 이번 범위가 아니다.

1. 기존 review-001/002/003은 labels/packet/link와 판독 메모의 연결 상태를 요약한다.
   완료된 idx0/idx20 재판독, R0 통계 재계산, 동일 이미지를 이용한 추가 appearance
   비교를 하지 않는다. 저장 경로·기존 판정 출처·알려진 한계만 재사용한다.
2. BASE source frame **14362와 14374**의 기존 이미지 및 직접 판독 메모가 남아
   있는지 확인한다. source frame, Glass, run, crop origin을 기존 기록으로 연결한다.
   정확한 frame이 없으면 nearest frame으로 대체하지 않는다. 다른 과거 번들에
   연결돼 있다면 그 출처를 기록하고 R22-3과 동일한 것으로 합치지 않는다.
   f14362 Y437은 기존 정정상 **위치 불일치**이며 구조물 음성 정답으로 쓰지 않는다.
3. 지정된 기존 reviews/notes 안에 **다른 frame의 기존 사람 판독 기록**이 있는지
   메타데이터·텍스트로만 확인한다. SPL#1 480–780초에 속하는 연결 가능한 기록을
   목록화한다. 추가 상세 확인은 알려진 다섯 frame 이외 **최대 3개 frame**으로
   제한하며 `(timestamp, glass_id, frame_index, record_id)` 순으로 선택한다.
   점수·밝기·모델 성패로 선택하지 않는다. 발견 수와 상한 때문에 읽지 않은 수를
   구분하고, 이 상한을 새 capture/라벨 수 또는 통계 표본 수로 해석하지 않는다.
4. 기존 manifest/index를 먼저 사용하고 필요할 때만 indexed record의 `images`
   참조를 확인한다. `ResultBundleReader`와 `DebugTraceRepository.summaries()` /
   `load_record()`를 재사용할 수 있다. 이미지 키 존재, 디스크 파일 존재, 저장된
   원본/주석 여부와 판독-이미지 연결을 구분한다. `artifact_availability`만 보고
   이미지가 존재하거나 판독 가능하다고 단정하지 않는다. 이미지 해석·새 mask
   계산은 하지 않는다. 기존 support 기록이 없으면 `support_not_measured`로 남긴다.
5. 구간별 행동 정답은 검색 문맥일 뿐 후보 identity 또는 정확한 Y 정답으로 쓰지
   않는다. 특히 approximate transition 근처에서는 순간 phase를 추정하지 않는다.
   기존 문서가 철회한 BASE 540s/Y437, 674s/Y435 또는 미확정 634s/Y360을
   검증된 유면 anchor로 복원하지 않는다.

**출력:** 원본 밖 기존 notes 폴더에 `w4-r3-existing-material-inventory.md` 한 개.
동일 메모가 있으면 먼저 읽고 완료 항목을 반복하지 않는다. 다음 표를 포함한다.

| source/run, Glass, frame/time | 기존 asset 경로 및 source/crop 연결 | 기존 사람 판독 인용·출처·불확실성 | identity / localization / no-interface 중 근거 범위 | 기존 valid support 정보 또는 미측정 | availability 및 다음에 필요한 조건 |
|---|---|---|---|---|---|

Availability는 `linked_saved_evidence`, `image_only_or_unlinked`, `trace_only`,
`not_found_in_searched_scope`, `not_checked`로 구분한다. 서로 다른 계면/구조물 사례가
있어도 동일 조건의 opposing control이라고 자동 선언하지 않는다. 실제 유면 positive,
명확한 structure negative, all-negative scene, unresolved control을 섞지 않는다.
특히 idx15의 artifact_tags가 비어 있다는 이유로 structure 분류를 새로 채우지 않는다.

실제로 읽은 작은 JSON/메모 파일은 전후 hash 보존을 기록한다. 기존 대용량 trace는
index 기반 읽기만 수행하고, 전체 재해시를 안 했다면 그 한계를 명시한다. 기존 receipt가
포괄하는 파일을 읽을 때는 해당 hash를 대조하되 이미 해결된 schema/artifact 수동
전사 검증을 다시 요구하지 않는다. 파일 없음·연결 불명·지원 미측정도 유효한 결과다.

**종료:** 검색 범위, 발견/미확인 수, 위 표, 가장 작은 남은 자료 공백을 함께 반환하고
멈춘다. 기존 원본/labels/history/frozen/recipe/mask는 수정하지 않는다. `prepare`,
새 packet/label, detector/extractor 실행, classifier/threshold 구현 또는 사용자 판정
요청은 하지 않는다. 기존 자료가 없다고 원영상 decode나 추가 capture로 자동 전환하지
않는다. 동일 SPL#1 자료는 독립 holdout이 아니며 FIELD FAIL / NOT_EVALUATED를 유지한다.


## W2 — one saved frame review preparation

**상태: 전달 보고로 완료.** [f14865 판독 결과](../60-evidence/s11/s11-o2-w2-f14865-scene-review.md)를
보존한다. 아래는 실행 당시 절차이며 프레임 선택·사용자 판독을 반복하지 않는다.

목적: 기존 기록에 없는 물리적 판독 근거를 얻을 수 있는지 **다른 저장 프레임 1장**으로
확인한다. [R3 결과와 한계](../60-evidence/s11/s11-o2-w4-r3-existing-evidence-feasibility.md#windows-inventory-received--2026-10-02)를
따르며, 현재 두 프레임의 반복 분석이나 새 challenger 구현으로 전환하지 않는다.
선택된 frame 14865의 두 경계는 사람 판독에서도 모호했다. 다음 절차만 수행한다.

- 대상은 같은 SPL#1의 BASE drain이다. 선택 범위는 **source 615–625초**, 목표
  620초로 미리 고정한다. 기존 약 600초 판독 및 ±5초 문맥과 떨어진 drain 내부의
  한 장을 얻기 위한 업무 범위이며, 이 시점이 더 잘 구분된다는 가정은 아니다.
  780초 이후나 SPL#2/3로 범위를 넓히지 않는다.
- 기존 R22-3 index에서 이 범위의 BASE record 중 `abs(source_time-620), frame_index,
  record_id` 순으로 첫 record 한 개를 선택한다. 점수·path 형상·이미지 선명도·예상
  정답으로 고르지 않는다. confidence/selected/rejected는 사람 정답이 아니다.
- 해당 record의 원본 무주석 이미지 참조와 실제 파일, run/Glass/source frame/time,
  crop origin/resize 여부를 직접 연결한다. 이미 저장된 원본만 표시한다. 최근 전달
  표의 시간값으로 추측하거나 FPS로 임의 재지정하지 않는다. source time 연결이
  불명확하거나 대상 record/원본이 없으면 그 한계를 반환하고 종료한다. 자동으로
  다른 프레임을 고르거나 원영상 decode·새 capture·mask 변경을 하지 않는다.
- 최초 표시에는 후보 선·점수·정답을 겹치지 않는다. 기존 이미지 파일을 열어
  사용자에게 보여주고 아래 질문 하나를 한다. 원본 파일을 수정하지 않는다.

> 이 이미지에서 실제 유면으로 확실하게 보이는 경계와, 유면이 아닌 구조물이나
> 반사로 확실하게 보이는 부분을 각각 짚어주실 수 있나요? 그렇게 구분한 보이는
> 특징도 알려주세요. 한쪽만 확실하거나 이 한 장으로 판단하기 어렵다면 그대로
> 말씀해주세요.

이것은 scene-level 판독이다. 별개 구조물/반사 여부를 강제하거나 정확한 px 정답을
요구하지 않는다. 움직임 확인이 필요하다는 답이면 필요한 문맥을 먼저 기록하고
멈춘다. 같은 장면을 임의로 확대 수집하거나 기존 idx0/idx20 clip으로 돌아가지 않는다.

사용자 답을 받기 전에는 identity/path 라벨을 작성하지 않는다. 답을 얻은 이후에도
기존 frame/candidate와 정확히 연결하고 현재 review-record 절차로 attribution,
uncertainty, revision을 보존하는 별도 단계가 필요하다. 새 candidate가 없으면 scene
truth와 candidate 부재를 구분하고 contour/Y를 만들어 채우지 않는다. 구별 근거가
없으면 uncertain/not-assessable 결과 자체를 보존한다. 한 장의 결과만으로 전역 규칙,
가중치·threshold·학습·성능 향상을 주장하지 않는다. FIELD FAIL은 유지한다.


## W2 — frame14865 scene-to-candidate correspondence

**목적:** 새 판독 메모의 두 대안 경계가 같은 frame의 어떤 저장 후보/경로와 공간적으로
대응하는지 확인한다. 정답 선택, 후보 identity 부여, 새 점수 계산 작업이 아니다.
[판독 결과와 한계](../60-evidence/s11/s11-o2-w2-f14865-scene-review.md)를 먼저 읽는다.

입력은 기존 R22-3 번들과 `w2-f14865-scene-review-reply-001.json`, 이미 표시한 원본
ROI다. record `f000014865_0c5e1375725c`, source frame14865, BASE, run
`a24c8fe9-3166-4c17-b69f-d9b4458711bd`를 직접 확인한다. source timestamp
619.994375와 origin(0,211)은 저장 메타데이터로 읽고 반올림 FPS에서 재생성하지 않는다.

1. `ResultBundleReader`, `DebugTraceRepository.load_record()` 및 기존
   `s11_interface_shadow_evaluation.extract_frame(record, case_id)`의 검증을 재사용한다.
   `extract_frame`은 메모리상 읽기 전용 projection으로 사용할 수 있다. `prepare`,
   `record`, 새 packet/label 생성, 영상 decode 또는 detector는 실행하지 않는다.
   witness 부재·index/provenance 불일치면 대체 trace를 추정하지 말고 종료한다.
2. 해당 frame의 **모든 Oil 후보**에 대해 원래 candidate_input_index, source,
   canonical_y, native path 유무, sector별 exact source X/Y를 표로 만든다.
   score 순서로 index를 바꾸거나 rejected/unadmitted 후보를 누락하지 않는다.
   native_path와 candidate_center는 분리한다. 다른 frame의 idx를 가져오지 않는다.
3. 사람 메모의 A(X 약178–483, Y 약385)와 B(X 약140–467, Y 약419–429)를
   정확한 contour/interval 정답으로 쓰지 않는다. 각 geometry와 기록된 X 범위의
   수치상 겹침 여부 및 Y/offset을 나란히 표시하되, 거리 cutoff나 nearest-winner를
   새로 만들지 않는다. 기울어진 B를 임의로 보간하지 않는다. 후보가 두 범위를
   지나거나 일부만 겹치는 경우도 그대로 남긴다. 이 표만으로 near/off/identity를
   결정하지 않는다. 좌표로 대응을 확정할 수 없으면 `ambiguous_correspondence`로 둔다.
4. 반사/잔류/눈금자 등 비계면 관찰에는 **기존 답변에 좌표가 실제 있는 경우에만**
   그 출처와 함께 공간 대응을 기록한다. 좌표가 없으면 `unbound_scene_observation`.
   화면상의 위치를 임의 추정해서 candidate negative나 artifact_tag를 만들지 않는다.
   상부 흰 점의 foam/이물질 언급은 미확정 가설이며 Foam 정답이 아니다.
5. 이미 있으면 band availability와 reason을 같은 geometry/scale 기준으로 인용한다.
   band availability를 새로운 gradient-valid 측정이나 물리적 식별 가능성으로
   바꾸지 않는다. 이번에는 NPZ 생성·mask 계산·추가 appearance 비교를 하지 않는다.

원본과 scene reply는 보존한다. notes 폴더의
`w2-f14865-scene-candidate-correspondence.md` 한 개에 위 표, 직접 읽은 출처,
읽은 소형 파일의 hash 연결/전후 보존과 검증 범위 한계, 남은 모호성을 기록하고 반환한다.
다른 프레임 탐색·사용자 재판정·라벨 이관으로 자동 진행하지 않는다. R2 진입이나
identity 개선을 주장하지 말고 FIELD FAIL / NOT_EVALUATED를 유지한다.


## W2 — frame14865 geometry report reconciliation

**완료(2026-10-02, 전달된 JSON 근거):** idx9–12의 native path와 19개 center-only
후보가 확인되어 이 확인 단계를 닫았다. [접수·정정 결과](../60-evidence/s11/s11-o2-w2-f14865-scene-review.md#geometry-reconciliation-received-and-bounded-w2-closed--2026-10-02)
참조. 아래는 수행 이력이며 재실행 지시가 아니다. 문서 해시 차이는 Git revision
차이로 해소됐고, 남은 집계·방향 설명은 전달된 JSON으로 로컬 정정했다.
새 Windows 작업이나 사용자 판정 요청은 없다.

대응 보고는 접수했다. 이번 확인은 그 보고의 “전 후보 5개 sector/native 없음”과
bw8 총 band 수(일부 후보 12/16, 나머지 20)의 불일치만 해소한다.
새 실험이나 사람 재판정 단계가 아니다. 기존 f14865 record를 같은 reader로 읽고
`frame = extract_frame(record, "w2-f14865")` 검증 결과에서 아래 projection을 만든다.
코드가 native 경로를 새로 생성하게 하지 않는다.

```python
import json

for candidate in sorted(frame["witness"]["candidates"],
                        key=lambda c: c["candidate_input_index"]):
    sectors = []
    for sector in candidate["sectors"]:
        sectors.append({
            key: sector[key] for key in (
                "sector", "source_x_range", "path_source_y", "candidate_source_y")
        })
        sectors[-1]["centers"] = [{
            "role": center["role"], "source_y": center["source_y"],
            "bw8": [{
                "band_width_px": scale["band_width_px"],
                "band_available": [band["available"] for band in scale["bands"]]
            } for scale in center["scales"] if scale["band_width_px"] == 8]
        } for center in sector["centers"]]
    print(json.dumps({
        "candidate_input_index": candidate["candidate_input_index"],
        "source": candidate["source"], "canonical_y": candidate["canonical_y"],
        "contour": candidate["contour"], "sector_count": len(sectors),
        "sectors": sectors
    }, ensure_ascii=False))
```

모든 23개 후보를 원래 index 순서로 출력한다. 필드가 없으면 실패한 JSON 경로를
기록하고 멈춘다. `get(..., None)`/기본값으로 missing을 null이나 “경로 없음”으로
바꾸지 않는다. `bw8=[]`도 scale 부재이며 0개 available과 다르다. coincident
native/center 위치에서는 center 객체가 한 번만 저장될 수 있으므로 저장된 role과
sector의 두 Y 필드를 함께 읽는다. band 합계는 candidate/role/width별로 구분한다.

이 출력으로 원래 note의 geometry/sector 수·X 범위와 band 집계 범위만 정정한다.
실제 X/Y 대응은 기존 `review_geometry(candidate)`를 재사용할 수 있다. 모든 후보를
포함하고 ±50/±10 등의 cutoff를 제거한다. A/B는 근사 관찰이므로 정확한 contour나
endpoint로 바꾸지 않는다. 경로가 정말 없으면 “captured geometry unavailable”로
기록하며 후보 생성 실패로 단정하지 않는다. 불일치가 남으면 어느 원본 필드끼리
충돌하는지만 남긴다. 별도 원인 조사나 재측정으로 자동 확장하지 않는다.

기존 `w2-f14865-scene-candidate-correspondence.md`의 원문을 보존하고 정정 부록에
위 JSON 출력과 변경된 결론을 붙여 반환한다. 원본 record/reply/이미지·labels는
보존하고 읽은 소형 입력의 hash 확인은 기존 절차를 따른다. 영상 decode, detector,
추가 이미지, NPZ/gradient, 사용자 재판정, packet/label 생성은 필요하지 않다.
이번 확인 후 멈춘다. FIELD FAIL / NOT_EVALUATED와 사람의 모호성은 유지한다.


## Existing controls — candidate-guided rationale presentation

**완료(2026-10-02, Windows 전달 보고):** 후보 표시 후 Accum idx10/idx15의 위아래
미세한 색상·외관 차이와 경계의 존재/부재에 대한 직접 답변을 받았다.
[근거 접수와 소스 검토](../60-evidence/s11/s11-o2-identity-context-windows-review-001.md#candidate-guided-human-rationale-received--2026-10-02)
참조. 아래는 수행한 절차이며 같은 판독을 다시 요청하지 않는다. 색상 측정은
아래 별도 color-side 절차를 따르며, 이 완료된 표시 절차를 반복하지 않는다.

**목적:** 이미 판정된 유면·비계면 사례에서 사용자가 detector의 실제 후보와 측정
영역을 보며 구별 근거를 설명할 수 있게 한다. 새 사례 선정이나 기존 identity
재판정이 아니다. [재사용 결정](../60-evidence/s11/s11-o2-w4-r3-existing-evidence-feasibility.md#existing-labeled-controls-retained--candidate-guided-presentation-decision)
참조. 현재 데이터로 물리적 구별 규칙이 입증됐다는 뜻은 아니다.

### 대상과 기존 자료

- 주 사례: review-003 / Accum / f16280 / revision 4.
  idx10 native Y=[209,210,217,219,220] (interface),
  idx15 native Y=[317,328,313,295,296] (non_interface).
  같은 X=[1218,1303), [1303,1388), [1388,1473), [1473,1558), [1558,1643).
- 보조 사례: review-002 / BASE / f14386 / revision 14.
  idx11 native Y=[901,925,922], X=[130,236), [236,343), [343,449)
  (non_interface / structure). 필요하면 기존 idx8/idx9 경로를 위치 참조로 함께
  표시하되 새 정답 경로나 시간적 연결로 취급하지 않는다.
- 기존 `joint-context-001/viewer.html`, 같은 폴더의 crop/gray/gradient 파일과
  experiment.json, review별 기존 plain/guide 이미지·packet·labels·reply를 재사용한다.
  Accum에는 기존 `idx15_f16280_crop_A_plain.png`,
  `idx15_f16280_crop_B_guide.png`와 path plain/guide가 보고돼 있다.
  BASE에는 `idx11_crop_A_plain.png`, `idx11_crop_B_guide.png`가 보고돼 있다.
  실제 경로는 기존 review 폴더에서 찾고 다른 이미지로 대체하지 않는다.

### 표시 순서

1. case/frame/Glass/revision과 후보 index/geometry를 기존 JSON에서 확인한다.
   숫자는 이미지 글자 판독으로 복원하지 않는다. 기존 guide를 쓰려면 원본·생성
   메타데이터/코드의 경로 연결과 좌표가 맞는지 확인한다. 확인되지 않은 guide는
   권위 좌표 표시로 쓰지 않고, 기존 viewer의 JSON 기반 표시를 사용한다.
   완료된 receipt·전체 bundle hash 감사나 detector 재실행을 반복하지 않는다.
2. **Accum 전체 원본 crop과 두 후보가 표시된 기존 guide를 사용자에게 실제로
   보여준다.** 파일명만 보고하지 않는다. idx10=기존 유면 판정,
   idx15=기존 비계면 판정이라는 범례와 frame/index를 설명한다. 그림은 detector가
   생성한 경계 후보이며, 최종 채택 위치나 사람의 정확한 contour 정답이 아니다.
3. 기존 viewer에서 `Selected X strip`을 해제해 전체 crop을 유지한다.
   `Overlays` off/on으로 원본과 측정 위치를 번갈아 보여준다. point는 반드시
   해당 idx의 `native_path`와 exact X를 선택한다. viewer는 한 번에 한 sector
   point만 표시하므로 전체 경로라고 설명하지 않는다. 같은 X에서 idx10/idx15를
   순서대로 보여준다. 시작 X=[1388,1473), 필요하면 나머지 기존 4개 sector를
   사용한다. 이는 설명용 위치 선택이며 평가 subset이나 가장 강한 신호 선택이 아니다.
4. 실제 측정 범위 설명이 필요하면 기존 BW6/12/18 중 동일 BW를 양쪽에 표시한다.
   초록 선은 source Y, 파랑/빨강 사각형은 available/unavailable band의 외곽이다.
   파랑 band도 모든 픽셀이 유효하다는 뜻은 아니다. magenta는 gradient view에서
   stencil이 무효라는 뜻이며, 물리 구조가 없다는 뜻이 아니다. 원본 RGB를 주
   판독 화면으로 유지한다. gradient 색상·강도만으로 사람의 identity를 유도하지 않는다.
5. BASE idx11은 기존 원본/guide로 glass 하단의 어떤 후보였는지 보여준다.
   viewer가 필요하면 native_path, 위의 실제 X/Y 및 BW8/16/24를 사용한다.
   이전 window invalid 비율은 그 window의 기록으로만 설명하고 전체 후보에
   적용하지 않는다. 가려진 경계를 새로운 비계면 근거로 삼지 않는다.

### 표시 후 한 번의 근거 질문

기존 reply에 정확히 같은 후보/영역의 구체적인 설명이 있으면 출처와 함께 재사용한다.
추가 설명이 필요한 경우, **사용자가 위 화면을 본 뒤** 다음처럼 묻고 답을 기다린다.

> 표시된 idx10과 idx15의 기존 판정은 그대로 두겠습니다. 두 후보를 구분할 때
> 어느 부분의 형상이나 주변 영역 관계를 보셨나요? 그림에서 후보 번호와 구간을
> 가리켜 설명해주시면 됩니다. 정확한 픽셀 범위는 필요 없습니다. 별도 단서를
> 특정하기 어렵거나 영상 움직임을 보고 판단했던 경우에도 그대로 말씀해주세요.

BASE는 사용자가 하단 구조물 사례를 설명할 때 보조로 사용한다. 두 장면의 답을
강제하거나 idx0/idx20의 기존 ±5초 모호성 판독을 다시 요청하지 않는다. 사용자가
새 판정을 제안해도 이번 단계에서 기존 labels에 쓰지 않고 제안과 불확실성을 기록한다.

### 반환과 종료

notes 폴더에 `existing-controls-candidate-guided-rationale.md`를 만든다. 실제 표시한
파일/point/role/BW, 기존 사람 기록의 인용, 새로운 사용자 답(있으면)과 에이전트
관찰을 구분한다. 각 근거에 대해 (a) 어느 후보/영역인지, (b) 기존 측정에서 이미
표현되는지/요약으로 소실되는지/측정되지 않는지/아직 모르는지, (c) 같은 근거를
가질 반례 가능성을 적는다. b/c는 확인된 출처가 없으면 unknown으로 둔다.
화면 표시 후 답을 기다리는 상태면 그렇게 보고하고 답을 만들어 채우지 않는다.

별도 점수·threshold·gradient/NPZ·새 overlay 생성·영상 decode·detector 실행·라벨
변경·새 frame 수집은 하지 않는다. 기존 출력은 보존하고 메모만 외부 notes에 저장한다.
단서가 없거나 mask로 확인 불가면 그 사실로 종료한다. 새 classifier나 R2를 자동
시작하지 않는다. FIELD FAIL / NOT_EVALUATED와 기존 모호성은 유지한다.

## Color-side measurement — existing saved outputs

**목적:** 사용자가 Accum idx10/idx15를 구별한 위아래 미세 색상 단서가 기존 gray
투영 밖에 남아 있는지 고정된 채널·band·support로 측정한다. 투명도 측정이나
identity 판정이 아니다. [계약](../20-architecture/s11-interface-observability-witness-architecture.md#w4-recorded-band-color-sides--saved-output-measurement),
[로컬 검증](../60-evidence/s11/s11-o2-color-side-local.md)을 따른다.
사용자 판독은 이미 접수됐으므로 같은 질문이나 새 사례 선정을 반복하지 않는다.

### 입력과 실행

GitHub ZIP을 옮긴 소스 폴더에서 기존 Python 환경으로 실행한다. `.git`이 없어도
된다. 사용자가 전달한 소스 commit과 실행기/측정 모듈의 SHA-256을 기록한다.
ZIP 폴더명으로 commit을 추정하지 않는다. 기존 `spatial-context-001` 출력 전체
32개 파일(31 hashed outputs + complete.json)을 입력으로 사용한다.
`joint-context-001`, review guide PNG, 영상·번들·labels로 대체하지 않는다.

아래 두 경로를 실제 data 폴더에 맞춘다. 출력은 입력 밖의 **새 폴더**여야 한다.
이미 존재하면 덮어쓰거나 삭제하지 않고 다른 신규 폴더를 사용한다.

```powershell
$spatialSource = "..\data\experiments\spatial-context-001"
$colorOutput = "..\data\experiments\color-side-001"
python tests/diagnostics/s11_joint_context_run.py --color-side --source "$spatialSource" --expected-source-artifact 6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910 --output "$colorOutput"
```

실행기는 기존 receipt/output hash, artifact, raw raster, frame/Glass/geometry,
원래 row context와 O1 baseline을 확인하고 BGR→gray가 저장 gray와 정확히 같은지
검증한다. 불일치하면 원인과 오류만 보고하고 새 COMPLETE를 성공으로 취급하지
않는다. 원본을 수정하거나 허용 오차를 조정해 통과시키지 않는다.

계산은 전체 point에 적용된다. 후보·sector·BW를 새로 고르거나 측정 창을 넓히지
않는다. 모든 band의 effective/non-glare 픽셀에서 B/G/R/gray를 같은 support로
측정하고, 같은 X 열의 below-minus-above를 계산한다. near/far는 별도이며 각
열의 차이를 동일 가중치로 평균한다. 숫자는 uint8 code value 단위(0..255)로,
기존 O1의 0..1 gray 평균과 직접 같은 단위로 비교하지 않는다. `B-G`, `R-G`
차이는 색상 단서이며 반사·조명에서도 나타날 수 있다.

### 결과 검증과 제한된 반환

1. `complete.json`과 `experiment.json` schema는 `s11-o2-color-side-v1`, receipt
   status는 COMPLETE. artifact SHA는 양쪽 일치해야 한다. expected source artifact는
   위 입력 pin이며 **새 color artifact와 다른 값**이다.
2. 출력은 `experiment.json`, `summary.md`, `color-side.csv` **3 hashed outputs**와
   `complete.json`, 총 **4개**. receipt의 세 파일 hash를 실제 bytes로 재계산한다.
   input_preservation은 원래 32파일 before=after=현재 실제 hash를 대조한다.
   영상·번들·labels의 새 해시 검사는 필요 없다.
3. 두 case를 구분한다: review-002 f14386, BASE
   `8f94fb85-d98e-4c71-9c97-3085168be1b2`, rev14, origin=[0,211], shape=[773,578],
   points=124, baseline MATCH/1416; review-003 f16280, Accum
   `8fb6ebc7-7c56-401e-86c3-05514bf6380b`, rev4, origin=[1199,56], shape=[584,462],
   points=158, baseline MATCH/1812. 이전 문서의 1012는
   [저장값 확인](../60-evidence/s11/s11-o2-color-side-local.md#saved-value-confirmation-received--2026-10-06)으로
   정정됐다. 원래 geometry/label provenance를 그대로 인용한다.
4. `EXPLORATORY_UNCALIBRATED`, `NOT_EVALUATED`, `auto_acceptance=false`,
   `production_decisions_emitted=false`, `FIELD FAIL`, `numeric_localization=NOT_MEASURED`
   유지. summary의 observed/unavailable/no-paired 수는 **상관된 측정 pair 수**이며
   성공/실패 후보 수나 독립 표본 수가 아니다.
5. 생성 summary와 위 검증을 반환한다. CSV는 코드로 읽고 아래 고정 비교를
   `case/idx/basis/X/Y/BW/near-or-far/status/paired_columns/total_columns`로 연결한다.
   모든 행의 B/G/R/gray 및 B-G/R-G 차이를 유지하며 가장 큰 값·유리한 sector만
   뽑지 않는다. 사람이 이미지 숫자를 읽거나 새로운 inline 측정식을 만들지 않는다.

반환 비교는 다음 세 묶음으로 분리한다. 계산 자체는 모든 point를 이미 포함한다.

- **주 비교:** review-003 idx10/idx15 `native_path`, 다섯 exact X, BW6/12/18,
  near/far 모두(60행). 두 후보 같은 X/BW/region의 status/support와 벡터를 대조한다.
- **보조:** review-002 idx11 `native_path`, 세 exact X, BW8/16/24, near/far(18행).
  unavailable을 비계면 단서나 zero로 해석하지 않는다. Accum과 표본을 합치지 않는다.
- **미해결 대조:** review-002 idx0/idx20 `candidate_center`, 다섯 exact X,
  BW8/16/24, near/far(60행). 기존 human ambiguity를 유지한다.

표 전사는 생성 CSV 행을 재사용한다. 상세 열별 배열은 로컬 JSON에 보존하고
상태/비교 벡터가 포함된 위 행만 전달한다. 반환이 길면 각 묶음을 별도 표/파일로
보존하고 경로와 행 수를 보고한다. 다음 코드는 **측정 없이** 해당 CSV 행을
표준 출력으로 고른다. 저장하려면 실험 폴더 밖 notes를 사용한다.

```python
import csv
import sys
from pathlib import Path

output = Path(r"..\data\experiments\color-side-001")  # 실제 실행 출력 경로
with (output / "color-side.csv").open(encoding="utf-8", newline="") as stream:
    reader = csv.DictReader(stream)
    writer = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in reader:
        key = (row["case_id"], int(row["candidate_input_index"]), row["geometry_basis"])
        if key in {
            ("review-003", 10, "native_path"), ("review-003", 15, "native_path"),
            ("review-002", 11, "native_path"),
            ("review-002", 0, "candidate_center"), ("review-002", 20, "candidate_center"),
        }:
            writer.writerow(row)
```

### 종료 조건

측정·해시·지정 비교 반환 후 멈춘다. CSV empty/JSON null은 zero가 아니다.
색상 차이의 유무만으로 유면/비계면, 투명도, 연결성, identity 개선, 임계값 또는
W4-R2 진입을 선언하지 않는다. 신규 gradient/NPZ/overlay, 영상 decode, detector
재실행, 새 frame/label/사용자 재판정은 필요 없다. 기존 출력과 라벨은 보존한다.
원본 컬러는 정보가 더 있다는 가설의 근거이며, 이번 단계는 고정된 측정의
정보 보존을 확인한다. 실제 구별력과 반례 여부는 반환 후 별도로 검토한다.

## Region competition — existing saved outputs

2026-10-06 준비. [work-plan](../00-project/work-plan.md#next-transition)의 다음 실행은
고정된 후보 조건부 영역 **외관 모델** 평가다. 기존 color-side 실행은 완료 상태이며
반복하지 않는다. 이것은 W4-R2 진입이나 Windows detector field qualification이 아니다.
[모델·정규화·한계](../20-architecture/s11-interface-observability-witness-architecture.md#w4-candidate-conditioned-region-competition--prototype-contract)와
[로컬 검증](../60-evidence/s11/s11-o2-color-side-local.md#region-prototype-implementation-and-windows-handoff--2026-10-06)을 먼저 확인한다.

### 소스 및 실행

사용자가 전달한 새 GitHub ZIP을 사용한다. `.git`이 없으면 사용자 제공 commit을
기록하고 아래 **파일 bytes SHA-256**으로 실행 소스를 대조한다. commit을 추정하거나
이전 ZIP에 새 파일 일부만 복사하지 않는다. 이 값은 이전 color-side 실행 코드와 다르다.

| 파일 / artifact | 고정 SHA-256 |
|---|---|
| `tests/diagnostics/s11_joint_context_run.py` | `63b54b9f94e9274071aff561c1466c6944df2fb15741b4712740c5e5c20103a1` |
| `tests/diagnostics/s11_region_competition.py` | `3627e7c2ad6e218fa797b68500d70e7c8be1e038354bbad32c0ebcd68fb60b17` |
| 신규 region artifact (8개 source 파일 + frozen spec) | `e6d17b0d54a909f226d265b9202151d017a76f6ed427009095c19b11bb04b3e8` |
| 입력 spatial artifact | `6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910` |

기존 Python/NumPy/OpenCV 환경, repo 루트에서 실행한다. 원본 영상·bundle·labels는
재오픈하지 않는다. 입력은 **spatial-context-001**이며 color-side/joint-context 출력이 아니다.
출력 디렉터리는 입력 밖의 새 경로여야 한다. 이미 있으면 덮어쓰지 말고 새 suffix를 쓴다.

```powershell
python tests/diagnostics/s11_joint_context_run.py `
  --source "..\data\experiments\spatial-context-001" `
  --expected-source-artifact "6aaf5f3ff6c4e1314d08cb7effb745ff5b721c03940c57002214b039ef544910" `
  --region-competition `
  --output "..\data\experiments\region-competition-001"
```

기존 로더가 32개 저장 입력의 receipt/raster/geometry/기존 band 재현을 검증하고,
모든 point/basis/width에 네 support/channel ablation과 네 고정 모델을 적용한다.
같은 후보 좌표를 사용하며 경계 위치/띠 폭을 재탐색하지 않는다. 계산은
`recorded_bands`/`candidate_envelope` × `gray`/`BGR`이다. `candidate_envelope`만
기존 band 사이와 중심 gap의 픽셀을 추가한다. 이 차이를 색상 효과로 돌리지 않는다.

### COMPLETE와 입력 보존

생성 후 다음을 **JSON/CSV/bytes에서 직접** 확인한다. 이미지 숫자를 판독하거나
보고용 통계를 별도 inline 측정식으로 다시 만들지 않는다.

1. receipt/report schema는 `s11-o2-region-competition-v1`, receipt는 COMPLETE.
   두 artifact SHA가 위 신규 region pin과 일치해야 한다. source artifact는 위 spatial pin.
2. `experiment.json`, `summary.md`, `region-competition.csv` **3 hashed outputs**,
   `complete.json` 포함 **4개**. receipt output 해시 전부 실제 파일 bytes와 대조한다.
3. `input_preservation` 32파일 각각 before=after=현재 input bytes SHA. 원본
   영상/bundle/labels를 다시 해시하지 않는다. receipt는 파일 검증 증거이지 identity 증거가 아니다.
4. review-002 f14386, BASE `8f94fb85-d98e-4c71-9c97-3085168be1b2`, rev14,
   origin=[0,211], shape=[773,578], points124, baseline MATCH/1416.
   review-003 f16280, Accum `8fb6ebc7-7c56-401e-86c3-05514bf6380b`, rev4,
   origin=[1199,56], shape=[584,462], points158, baseline MATCH/1812.
5. 각 point 3 widths × 4 views × 4 models. 전체 CSV는 **13,536 data rows**
   (BASE 5,952 + Accum 7,584). 모델 실패/null 행도 남아야 한다. 동일 native/center
   alias와 중첩 widths를 독립 표본으로 세지 않는다.
6. `EXPLORATORY_UNCALIBRATED`, `NOT_EVALUATED`, `auto_acceptance=false`,
   `production_decisions_emitted=false`, `FIELD FAIL`, `numeric_localization=NOT_MEASURED`
   유지. view의 physical identity는 UNRESOLVED, opposition은 not_measured.
7. 실행 경과 시간, Python/NumPy/OpenCV 버전과 소스 식별을 기록한다. 실패하면
   COMPLETE를 수동 생성하거나 모델/지원 조건을 바꾸지 말고 원래 오류를 보고한다.

### 고정 비교 반환

모델은 후보 선택 없이 전 inventory를 계산한다. 반환 비교는 기존 세 묶음이며
같은 X/BW에서 모든 모델과 네 ablation을 함께 유지한다.

- 주 비교: review-003 idx10/idx15 `native_path`, 5 X × 3 BW × 4 views × 4 models × 2 후보 = **480행**.
- 보조: review-002 idx11 `native_path`, 3 X × 3 BW × 4 views × 4 models = **144행**.
- 미해결: review-002 idx0/idx20 `candidate_center`, 5 X × 3 BW × 4 views × 4 models × 2 후보 = **480행**.

실험 폴더 밖 새 notes에 CSV를 보존한다. 아래는 행 선택만 하는 코드이며 새 측정이 아니다.
출력 경로만 실제 환경에 맞춘다. 주/보조/미해결 사례를 합산하거나 유리한 행만 고르지 않는다.

```python
import csv
from pathlib import Path

output = Path(r"..\data\experiments\region-competition-001")
notes = Path(r"..\data\region-competition-001-notes")
notes.mkdir(parents=True, exist_ok=False)
with (output / "region-competition.csv").open(encoding="utf-8", newline="") as stream:
    reader = csv.DictReader(stream)
    fields, rows = reader.fieldnames, list(reader)
groups = {
    "main": {("review-003", "10", "native_path"), ("review-003", "15", "native_path")},
    "auxiliary": {("review-002", "11", "native_path")},
    "unresolved": {("review-002", "0", "candidate_center"), ("review-002", "20", "candidate_center")},
}
for name, keys in groups.items():
    selected = [r for r in rows if (r["case_id"], r["candidate_input_index"], r["geometry_basis"]) in keys]
    with (notes / (name + ".csv")).open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(selected)
    print(name, len(selected), notes / (name + ".csv"))
```

반환은 생성 summary 전문, 위 검증 결과, 세 CSV의 경로/행 수를 포함한다. 수치 대조는
다음 **사전 지정 발췌**를 CSV에서 그대로 뽑는다: main X=[1388,1473), BW6 (32행),
auxiliary X=[236,343), BW8 (16행), unresolved X=[231,346), BW8 (32행).
`idx/basis/X/Y/BW/support/channels/model/status/train_pixels/test_pixels/heldout_mse`
및 horizontal/vertical pair count·MSE를 보존한다. 다른 sector/width는 삭제하지 않고
전체 비교 CSV/JSON에 유지한다. 출력이 길면 별도 파일로 보존해 경로를 반환한다.

MSE가 작다는 사실은 해당 고정 외관 모델의 적합도만 의미한다. gray와 BGR의 서로 다른
channel-space loss 차이를 직접 색상의 identity 개선량으로 해석하지 않는다.
원래 band/확장 영역 효과와 색상 효과를 분리하고, 모델이 관측하지 않은 return,
마스크 너머 연결성, 투명도 또는 구조물 identity를 추론하지 않는다. O1 unavailable을
확장 영역으로 복구하지 않는다. 모든 모델이 부적합하거나 반례가 공유되면 그대로 보고한다.

이 반환에서 멈춘다. 새 threshold/띠 폭/중심 재선택, winner-to-identity 변환, W4-R2
진입, 라벨 변경, detector/영상 decode, 새 gradient/overlay 및 사용자 재판정은 수행하지 않는다.

## Region cross-X/BW review — saved CSV only

Region 실행과 두 전사 항목 확인은 완료됐다. 이번 단계는 새 측정이 아닌 기존
`region-competition-001/region-competition.csv`의 전 구간 읽기 전용 검토다.
새 ZIP, 모델 실행, 영상/bundle/labels, source 재해시, 반복 receipt 확인은 필요 없다.
실행 당시 c2102c1 출력과 기존 notes를 사용한다. 원본 artifact는
`e6d17b0d54a909f226d265b9202151d017a76f6ed427009095c19b11bb04b3e8`이다.

### 입력과 전수성

1. CSV를 프로그램으로 읽는다. 주 비교는 review-003 idx10/idx15 native_path
   480행, 보조는 review-002 idx11 native_path 144행, 미해결은 review-002
   idx0/idx20 candidate_center 480행이다. notes의 main/auxiliary/unresolved.csv를
   사용한다면 원본 CSV의 동일 key 행과 일치하는지 대조한다. 불일치 시 원본 값을
   임의 복구하지 않고 key와 충돌만 보고한다.
2. 원래 행의 고유 key는 case/frame/idx/basis/X start-stop/Y/BW/support/channels/model.
   네 모델(smooth, partition, ribbon_bw, ribbon_2bw)을 같은 view의 네 열로 펼친다.
   모든 Y, band 역할, view_status/model_status, train/test 픽셀, heldout MSE,
   horizontal/vertical pair count와 MSE를 보존한다. 중복/missing model은 오류로
   보고하며 첫 행 선택으로 숨기지 않는다. null/빈 셀은 0으로 바꾸지 않는다.
3. 펼친 결과는 주 120 views, 보조 36 views, 미해결 120 views, 총 276 views다.
   observed와 unavailable/rank/split 실패를 따로 보존한다. 4개의 모델행에 반복된
   adjacency/support 값은 중복 측정이나 독립 증거가 아니다.
4. 비교 후보 연결은 같은 case/frame/basis/exact X/BW/support/channels로 한다.
   후보마다 source Y가 다르므로 두 Y를 나란히 유지한다. candidate_center와
   native_path를 혼합하거나 서로 다른 X/BW를 억지로 짝짓지 않는다.
   주 비교는 5 X × 3 BW × 4 views = 60쌍, 미해결도 60쌍이다.
   한쪽이라도 비교 불가인 pair는 불가 사유와 양쪽 상태를 남긴다.

### 확인할 질문

다음은 사전 지정 발췌에서 생긴 질문을 전 구간에 확인하는 **기술적 검토**다.
새 평가 점수/threshold/학습이나 독립 holdout 검정이 아니다.

- **주 비교:** 각 X/BW에서 idx10의 partition이 smooth보다 작은가, idx15에도
  같은 관계가 나타나는가? 네 모델의 오차 순서는 gray/BGR 및 bands/envelope에서
  어떻게 달라지는가? 반대 관계, 실제 수치 동률, 비교 불가 구간을 모두 기록한다.
  원한다면 기존 보고의 `100*(smooth-partition)/smooth`를 같은 view 안에서만
  함께 표시하되, smooth=0이면 undefined로 둔다. 이 비율을 판정식이나 cutoff로
  쓰거나 전체 후보 점수로 평균내지 않는다. 작은 부호 차이도 원값으로 남기며
  '의미 있는 차이'를 정하는 새 허용오차를 만들지 않는다.
- **보조:** idx11의 해당 발췌에서 ribbon_2bw 오차가 가장 작았다는 관계가 다른
  X/BW에서도 나타나는지, 변경/비교 불가 위치를 구분한다. 마스크 부족을 구조물
  근거로 쓰지 않는다. visible return이나 구조 identity는 MSE로 확정하지 않는다.
- **미해결:** idx0/idx20의 bands/envelope 모델 순서 변화가 어디에서 나타나는지
  기록한다. 기존 identity 라벨을 이 비교의 확정 양성/음성 정답으로 사용하지 않는다.
- **색상/관찰 범위 분리:** 같은 support에서 gray/BGR 비교, 같은 채널에서
  bands/envelope 비교를 분리한다. 다른 channel-space MSE나 다른 관측 픽셀 집합의
  MSE를 직접 비교해 성능 개선량으로 해석하지 않는다. BGR에서 순서가 달라져도
  실제 Oil 구별력이 개선됐다고 결론 내리지 않는다.

소수점 반올림 전 값으로 수치 비교하고, 출력에는 원값을 보존한다. 작은 차이의
안정성/통계적 유의성은 검증되지 않았다. 순서/빈도/다수결을 candidate identity로
환산하지 않는다. 어떤 구간에서 같은 설명이 공유되거나 차이가 사라지면 그대로 보고한다.

### 저장과 반환

기존 실험/notes 파일은 덮어쓰지 않는다. 새
`region-competition-001-notes/cross-x-bw-review-001/`에 다음을 저장한다.

- 전수 pivot CSV 세 파일: main 120, auxiliary 36, unresolved 120행.
- same-X pair 검토 표: main 60쌍, unresolved 60쌍. 한쪽 불가도 포함한다.
- `review.md`: 세 묶음별 관찰과 모든 반대/변경/동률/비교 불가 key 목록.
  근거 key에는 X/Y/BW/support/channels/idx를 포함하고 해당 네 MSE를 연결한다.

반환은 (a) 읽은 파일·출력 경로·행 수, (b) 세 묶음의 검토 결과,
(c) gray/BGR 변화와 bands/envelope 변화의 분리된 설명,
(d) 예외 key 전체와 대응 오차·상태를 포함한다. 내용이 길면 묶음을 나누어 반환하되
전체 표를 로컬에 보존하고 일부 예외만 유리하게 선택하지 않는다. 모든 구간이
동일하다는 주장도 실제 전수 key 대조 결과에 한정한다.

읽은 원본 파일 bytes는 작업 전후 불변인지 확인하되, 이미 닫힌 소스 해시/누락 행을
사용자에게 다시 확인 요청하지 않는다. **실제 검토 결과를 기록한 뒤 멈춘다.**
새 model fit/descriptor/threshold/띠 폭 변경, source decode, label 변경,
identity/연결성/투명도 판정, W4-R2 진입 또는 사용자 재판정은 수행하지 않는다.
FIELD FAIL / NOT_EVALUATED와 idx0/idx20 ambiguity는 유지한다.

## Passive control review — first bounded batch

사용자 입력 범위 결정: 동일 영상의 추가 구간/영역과 다른 기존 영상의 추가 판독은
가능하다. 동일 환경을 재구성할 수 없어 비교 촬영은 불가하다. 이번 단계는 기존
영상 기반 판독 준비이며, 완료된 region 실험이나 W2/R3 감사를 반복하지 않는다.
[설계 판단](../50-diagnostics/s11/s11-w4-post-region-design-assessment.md#input-feasibility-resolved--user-decision)을
따른다. 새 모델·측정값·threshold를 만들지 않고 후보와 사람 답의 연결을 확보한다.

### 범위와 사전 고정 선택

원본 R22-3 번들의 index를 재사용한다. 첫 묶음은 아래 **최대 3개 record**다.
시간은 source-video seconds이며, 아래 값은 표본 선택 규칙일 뿐 identity 입력이 아니다.
[기존 구간 판독](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#reviewed-timeline)이
선택 이유이며 candidate-level 정답을 자동 생성하지 않는다.

| 순서 / case_id | Glass | source 시간 범위 / 목표 | 채우려는 판독 공백 |
|---|---|---|---|
| 1 / w4-passive-001-accum-drain | Accum | [720,730] / 725 s | 잔류 흔적과 실제 유면이 함께 있을 수 있는 장면에서 혼동 후보의 정체 |
| 2 / w4-passive-001-base-full | BASE | [720,730] / 725 s | 유면이 없는 구간의 구조/반사 중 유면처럼 보이는 후보 |
| 3 / w4-passive-001-accum-postfoam | Accum | [685,695] / 690 s | Foam 소멸 후 남은 경계와 주변 흔적, 주 사례 밖의 긍정/모호성 대조 |

각 슬롯에서 정확한 Glass의 저장 record를
`abs(record.timestamp_sec-target), frame_index, record_id` 순으로 정렬해 첫 항목을
선택한다. 점수·MSE·예상 라벨·선명도·특정 Y로 고르지 않는다. 실제 record/frame/time,
Glass UUID, run_id는 index에서 읽으며 FPS 계산이나 이전 전사값으로 채우지 않는다.
서로 다른 Glass의 record가 같은 frame일 수 있으며, 이를 독립 표본으로 세지 않는다.

정확한 기존 판독이 이미 있으면 그 출처를 재사용한다. 기존 판독이 있다는 이유로
다음 프레임을 찾아 이동하지 않는다. 슬롯에 record/원본이 없거나 연결이 불명확하면
그 슬롯을 unavailable로 기록하고 추가 범위를 탐색하지 않는다. 대상이 모두 모호하거나
원하는 반례가 없더라도 성공 사례가 나올 때까지 교체하지 않는다. 3개는 작업량 상한이며
통계적 충분성이나 3개 독립 episode를 뜻하지 않는다.

### 준비물과 분할 규칙

1. 원본 실험·review-001/002/003은 수정하지 않는다. 새 외부 notes 폴더
   `data/w4-passive-review-001/`에 `selection-manifest.json`을 먼저 저장한다.
   위 선택 규칙/목적, 선택 record, 기존 판독 출처, 원본 이미지 경로·해시,
   crop origin/shape/resize, 실제 입력 경로 및 읽은 코드 기준을 기록한다.
2. 기존 `s11_interface_shadow_evaluation.py prepare/status/record`를 재사용한다.
   각 선택에 대응하는 새 `selection.json` 및 별도 packet/labels를 생성할 수 있다.
   `prepare`는 indexed trace를 읽는 작업이며 detector 실행이 아니다. dataset_id는
   `w4-passive-review-001`, case_id는 위 표를 사용한다. 나머지 필드는 실제 저장
   metadata와 기존 owner를 사용하고, 미확인 값/판독자/owner를 임의로 만들지 않는다.
3. **partition은 regression**, recording_group은 기존 SPL#1의 실제 그룹을 그대로
   사용한다. 같은 run/recording을 다른 이름으로 나누지 않는다. episode_id는 기존
   구간 매핑을 보존하며, 명확하지 않으면 같은 recording에 묶인 보수적 그룹으로
   기록한다. previously_reviewed는 실제 이전 판독 유무다. 새 프레임이어도 이
   녹화를 개발/보정/holdout으로 재분류하지 않는다. 기존 평가기는 recording-level
   lock을 적용하며 이를 우회하거나 label 문서를 수동 변경하지 않는다.
4. packet의 전체 Oil candidate를 보존한다. 후보 key는 candidate_input_index이고,
   source/kind/canonical_y와 모든 sector의 geometry_source/path_source_y/center
   role/X를 대조한다. native path가 없는 후보는 center-only로 표시한다. 서로 다른
   center role, score rank와 input index를 혼동하지 않는다. 선택/거절 후보도 누락하지
   않는다. 기존 bundle 연결을 출처로 참조하되 다른 packet에 bundle-link를 무작정
   복사하지 않는다. 새 연결이 필요하면 기존 link-bundle 절차를 적용한다.

### 화면과 사용자 질문

저장된 무주석 원본을 우선 사용한다. 이번 첫 묶음에서는 새 영상 decode나 detector
실행을 하지 않는다. 필요한 장면에 저장 raster가 없으면 그 공백을 보고한다. 사용자가
움직임 문맥을 요청하면 필요한 범위를 기록하고 별도 재생 단계로 남긴다. 정지영상 판독과
시간 문맥 판독을 섞어 쓰지 않는다.

- **plain RGB와 후보 가이드 둘 다 실제로 표시**한다. 사용자가 plain에서 detector가
  센싱한 대상을 추측하게 하지 않는다. 전체 crop을 유지하고 선택한 구간 확대를
  병행할 수 있다. 새 guide는 원본을 보존한 파생 표시물로 별도 저장한다.
- Windows의 기존 guide 생성 코드를 우선 재사용하며, 이번 packet geometry를 읽도록
  한다. 코드/원본/좌표 연결을 확인할 수 없는 오래된 guide는 쓰지 않는다. repo의
  `ReviewDebugOverlayRenderer`는 rank·score·selected/rejected와 canonical line을
  표시하므로 native-path 정답 가이드로 그대로 쓰지 않는다. 표시 준비가 안 되면
  사용자에게 숫자만 물어보지 말고 presentation_not_ready로 보고한다.
- 가이드의 후보 번호는 실제 input index, native는 저장된 sector 경로, center-only는
  경로가 아닌 수평 위치 가설로 구분한다. 끊긴 sector를 보간해 연결하지 않는다.
  판정색·점수·selected/rejected·기존 기대 라벨을 판독 화면에 넣지 않는다.
  겹치는 후보는 번호 목록을 유지하고 한 후보씩 토글/별도 표시한다.
- 전체 후보 목록을 유지한 채 사용자에게 혼동되는 표시 후보 또는 관찰 영역을
  지정하게 한다. 프레임당 **최대 2개 후보**, 총 최대 6개 추가 identity 답변이 첫
  묶음의 상한이다. 이는 목적 표집이므로 후보 전체 정확도나 유병률을 추정하지 않는다.
  반례는 기대한 판정으로 채우지 않는다. 가리킨 영역에 저장 후보가 없으면
  `unbound_scene_observation` 또는 proposal gap으로 보존한다.

한 번에 표시한 후보 하나에 대해 묻는다:

> 이 표시 후보는 전체적으로 실제 유면인가요, 다른 대상인가요, 아니면 판단하기
> 어려운가요? 그렇게 구분한 경계나 주변 특징도 짧게 설명해주세요. 후보 선의 일부가
> 유면에서 벗어나더라도 전체 정체와 구간별 위치는 따로 기록하겠습니다.

사용자의 실제 답만 기존 record 절차로 새 labels/replies/history에 보존한다. 매 답변은
직전 status의 expected SHA와 witness hash로 연결한다. artifact 종류는 사용자가 확실히
말한 경우만 기록하고, 단지 아래쪽에 있다는 이유로 structure/reflection을 지정하지
않는다. identity와 near/off, scalar 위치를 서로 전사하지 않는다. 이 묶음에서 정밀
contour/Y 정답을 별도 요구하지 않는다. `uncertain`은 완료된 유효 답변이며 자동 재질문
대상이 아니다. 기존 idx0/idx20·f14865 모호성 및 과거 labels는 유지한다.

여러 물질 경계를 구분해 답한 경우, 같은 답변의 note에 어느 영역 사이의 경계인지
사용자의 표현 그대로 보존한다. 물질 이름을 모르면 unknown으로 남긴다. 생성기의
`oil_air` kind나 위/아래 위치만으로 추적 대상 Oil 경계를 정하지 않는다. 실제 저장된
`interface` 답을 임의로 바꾸지 않되, 일반적인 물질 경계와 목표 Oil 경계의 대응이
미확인인 case는 대응을 명확히 하기 전 학습·목표 평가에 넣지 않는다. 현재 evaluator는
note를 읽어 자동 제외하지 않으므로 이는 운영상 사용 보류이며 새 schema 기능이 아니다.
이 구분을 위해 상한을 넘어 추가 판독하거나 다른 case에 같은 층 구조를 유도하지 않는다.

목표는 이후 [사용자가 확정한 최상단 실제 유체 경계](../rotary_oil_level_tracker_ssot_spec.md#다층-유체의-추적-대상)다.
유체 종류 분류는 필수가 아니며 실제 내부 경계는 물리적 interface 기록을 유지하되
추적 목표와 구분한다. 이번 묶음의 [확정된 대응](../60-evidence/s11/s11-o2-passive-control-review-001.md#target-resolved--uppermost-actual-fluid-boundary)은
별도 근거에 보존되어 있다. 같은 질문을 재요청하지 않는다. 원본 labels를 덮어쓰거나
기존 평가기가 note의 target 구분을 자동 적용한다고 가정하지 않는다.

### 다른 영상: 이번에는 metadata와 노출 이력만

알려진 작업 폴더의 기존 영상/번들 목록과 사용자가 이미 제공한 정보만 확인한다.
전체 PC를 검색하지 않는다. 다른 영상 경로가 알려져 있지 않으면 그 경로만 사용자에게
물어볼 수 있으며 SPL#1 준비는 계속한다. 각 파일에 basename/path, 기존 식별 해시가
있으면 그 값, 알려진 녹화 session/분할·파생 관계, 이전 사람 판독/모델개발 사용 이력,
기존 bundle/candidate 존재 여부를 `other-recordings-metadata.json`에 기록한다.
없는 metadata는 unknown이며 파일명만으로 독립 녹화라고 단정하지 않는다.

다른 영상의 이미지/clip/score를 이번에 열어 보거나 자동 decoder/detector를 실행하지
않는다. candidate 라벨이 이미 존재하면 그 존재와 partition metadata만 기록한다.
개발·보정·최종평가 역할은 이 이력과 독립성 검토 후 별도로 고정한다. 이미 개발에
노출된 자료를 untouched holdout으로 재명명하지 않는다. 다른 영상이 존재한다는
사실만으로 세 분할을 구성할 수 있다고 주장하지 않는다.

### 반환과 종료

반환물은 실제 선택 manifest, 전체 후보 inventory/packet 경로, 표시한 plain/guide
경로, 받은 사용자 답과 연결된 revision/출처, unavailable/proposal gap/uncertain 목록,
다른 영상 metadata 목록 및 읽은 원본 보존 확인이다. 새 작업 폴더에만 산출하며 원본
bytes의 before/after 확인 범위를 명시한다. 이전 receipt·전사 정정을 다시 감사하지 않는다.

첫 case를 실제 표시하고 사용자 답을 기다린다. 답을 받으면 위 상한 안에서 계속하고,
답이 없으면 판독 대기라고 보고한다. 최대 3 case/6 답변을 마치면 반환 후 멈춘다.
이 결과로 학습·threshold 선정·새 region fit·W4-R2 진입·field PASS를 선언하지 않는다.
새 모델은 다음 recording-role/control 검토 이후의 별도 단계다. FIELD FAIL /
NOT_EVALUATED는 유지된다.

## Passive control review — bind uppermost target truth

사용자 판독과 최상단 실제 유체 경계 목표는 확정됐다. 이번에는 기존
`data/w4-passive-review-001/prepared/labels.json`과 연결 packet만 읽어
평가용 목표 대응을 별도 snapshot으로 만든다. 원본 labels/replies/history를 수정하지
않는다. 재판독·새 이미지·decode·detector·prediction·학습·threshold 실행은 없다.
[구현 근거](../60-evidence/s11/s11-o2-passive-control-review-001.md#target-binding-implementation-and-windows-handoff)를 따른다.

### 입력과 식별

GitHub ZIP 소스도 허용한다. `.git` 부재는 실행 실패가 아니다. 다음 파일의 SHA-256을
대조하며 다른 값이면 실행하지 않고 실제 값을 반환한다.

| 파일 | SHA-256 |
|---|---|
| `tests/diagnostics/s11_interface_shadow_evaluation.py` | `5909c468871ed3c5cd2095c7c4a4a88df4d08569b10985c22e999aff0f42c808` |
| `tests/diagnostics/s11_target_truth.py` | `f50fd9039ef4fee608d4c518557aa6b69d8abaab2d380945a69b0e109d74cc61` |
| `docs/50-diagnostics/s11/s11-passive-001-target-role-mapping.json` | `3443a2cce1b011cf2db409dafd9e9a137ccc74aa50461eef80df38a707bea1e3` |

mapping의 `source_labels_sha256`은 **status의 논리 해시**
`55672fe9182129a3baef8ba8df57f12fdcd252d9296f2bb1ad4903d855ae02a8`다.
`Get-FileHash labels.json`의 파일 bytes 해시와는 다른 값일 수 있다. 자동 pin 교체,
경로 문자열 수정이나 source labels 재저장을 하지 않는다. 불일치하면 status의
논리 해시와 실제 bytes 해시를 구분해 반환하고 멈춘다.

mapping은 정확한 세 case/frame/Glass 및 후보 수 26/21/28을 대조하고, 다음 사용자
확정 대응을 적용한다. 점수·Y 거리로 후보를 다시 고르지 않는다.

- Accum drain: idx4/13/17/24 → target; idx5/10/18 → internal_interface.
- Accum post-Foam: idx5/6/10/19/20/25 → target.
- 각 case의 기존 `non_interface`만 명시적으로 계승: 19/21/22개.
- 원본 `interface` 13개를 보존하고, 목표상 10개와 내부 비대상 3개로 나눈다.
  내부 경계에 reflection/structure 등의 태그를 새로 부여하지 않는다.

### PowerShell 실행

소스 repo 루트에서 실행한다. `$DataRoot`만 실제 기존 데이터 위치에 맞춘다.
출력은 새 폴더 `target-truth-001`이며 기존 출력이 있으면 덮어쓰지 말고 반환한다.

```powershell
$DataRoot = 'C:\0.Coding\2.Reference\Oil level tracker\0.windows_diagnostic\data'
$Labels = Join-Path $DataRoot 'w4-passive-review-001\prepared\labels.json'
$Mapping = '.\docs\50-diagnostics\s11\s11-passive-001-target-role-mapping.json'
$Output = Join-Path $DataRoot 'w4-passive-review-001\target-truth-001'
if (Test-Path $Output) { throw 'Target output already exists; do not overwrite.' }

python tests/diagnostics/s11_interface_shadow_evaluation.py status --labels $Labels
if ($LASTEXITCODE -ne 0) { throw 'Source status failed.' }

python tests/diagnostics/s11_interface_shadow_evaluation.py bind-target `
  --labels $Labels --mapping $Mapping --output "$Output\target-truth.json"
if ($LASTEXITCODE -ne 0) { throw 'Target binding failed; do not change source or pins.' }

python tests/diagnostics/s11_interface_shadow_evaluation.py evaluate `
  --frozen "$Output\target-truth.json" --output "$Output\readiness.json"
if ($LASTEXITCODE -ne 0) { throw 'Target snapshot validation failed.' }
```

`bind-target`의 console 결과는 `BOUND_NOT_EVALUATED`다. 원본 labels·mapping·연결
packet의 bytes를 시작/종료에 확인한 뒤 새 파일을 생성한다. packet이 하나면 입력 수는
3개다. 저장된 전체 물리 labels/history, mapping, 후보별 physical annotation/packet/
witness 해시와 target role을 snapshot에 포함한다. source paths는 원래 판독의 일부로
보존하고, 현재 packet locator는 출력 위치 기준으로 별도 연결한다.

`evaluate`는 새 snapshot을 다시 읽고 packet 해시와 projection을 재검증한다. 이 실행에
`--predictions`나 `--exploratory`를 넣지 않는다. 원본 영상/번들 또는 region 실험은
열지 않는다. 기존 `freeze`를 원본 labels에 다시 실행할 필요가 없다.

### 확인·반환 후 종료

- snapshot schema `s11-o2-target-truth-v1`; report schema `s11-o2-target-shadow-report-v1`.
- console `artifact_sha256` = snapshot 값 = readiness `target_truth.artifact_sha256`.
  console `evaluation_truth_sha256` = snapshot `content_sha256` = readiness
  `frozen_labels_sha256`. artifact·evaluation-content·파일 bytes 해시는 서로 다른 역할이다.
- 물리 identity 수 `interface=13`, `non_interface=62`; target role 수 `target=10`,
  `internal_interface=3`, `other_non_target=62`. 목표 평가 identity 수는 10/65다.
- 원본 partition/recording group 유지, 총 3 case/75 candidate, regression만 존재.
  후보별 대응은 snapshot `payload.bindings`에 전수 보존한다.
- readiness `status=NOT_EVALUATED`, `auto_acceptance=false`, `field_disposition=FIELD FAIL`.
  `target_truth.local_scalar_entity_truth=NOT_TRANSFERRED`; path/contour/scalar/entity 및
  artifact subtype을 목표 정답으로 자동 이관하지 않았다. 예측 없는 coverage/recall
  수치는 detector 성능으로 해석하지 않는다.
- 원본 labels/읽은 packet의 전후 bytes 해시와 status 논리 해시 불변을 확인한다.
  새 snapshot/readiness의 `Get-FileHash -Algorithm SHA256`도 각각 기록한다.
  이 단계는 COMPLETE receipt를 생성하지 않으며, 그런 영수증이 있다고 보고하지 않는다.

반환: 사용 소스/세 파일 해시, 실제 입력·출력 경로, binding console 결과, 위 schema/
연결 해시/계수/보존 결과와 오류가 있으면 해당 오류. 상세 JSON은 업무 PC에 보존한다.
여기서 멈춘다. 새 모델 실행, 예측 파일 생성, 성능 비교, R2 진입이나 field PASS는
이 절차의 결과가 아니다.
