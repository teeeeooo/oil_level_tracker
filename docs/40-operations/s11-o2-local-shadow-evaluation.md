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
