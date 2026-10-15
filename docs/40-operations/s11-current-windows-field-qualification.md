# S11 Current Windows Field Qualification

**Status:** `ACTIVE PROCEDURE` — candidate-current, revision-neutral.

This document is the executable target-Windows field procedure for whichever S11 detector candidate the current Work Plan names. It intentionally does not hard-code R7–R12 or any future revision number. A candidate becomes the subject of this procedure only when `docs/00-project/work-plan.md` and the user's granted scope make Windows qualification current.

## 1. Preconditions and identity

Before running private media:

1. Confirm Windows qualification is authorized and identify the candidate from `docs/00-project/work-plan.md`.
2. Record the exact pushed source SHA being qualified. Do not qualify an unpushed or subsequently mutated head as though it were the reviewed candidate.
3. Read the candidate's current architecture and validation/work specification linked by the Work Plan. Record expected detector/resolver/schema identities from those owners rather than from historical checklists.
4. Read `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` and `docs/30-validation/windows_sample1_heating_coldstart.reviewed-truth.json` completely enough to enumerate all nine `WS1-*` segments.
5. Run the `windows-qualification` and `s11-detector-change` Skill contracts. Resolve any required governance/history owner before interpreting results.

If source, candidate identity, or reviewed-truth authority is ambiguous, stop before execution rather than blending revision evidence.

An isolated Windows machine may use a GitHub source ZIP extracted into a folder;
Git installation, cloning and network access on that machine are not prerequisites.
Bind the archive to its published commit and verify extracted source-file hashes.
An existing completed bundle may be reused when its actual producing source,
video, Recipe and session conditions are established. Review an uncertain older
bundle as historical output first; do not silently label it the designated baseline
or require a rerun solely because `.git` or complete debug trace is absent.
The [retired overlay comparison](s11-overlay-support-windows-comparison.md)
records the ZIP/manual-GUI/bundle workflow, not a current candidate request.
A GUI launch alone does not start an analysis; a manual run requires the
operator to complete setup and start analysis. Use the Work Plan for current
candidate identity, not the retired comparison's commit or branch.

### October 15 first initial-FULL comparison

This is the first exploratory OFF/ON comparison named by the Work Plan, before
cost-first assignment, candidate RGB or Local XY. False positives are permitted
for inspection and must be reported. Formal field acceptance still follows the
nine-segment procedure below. The [comparison record](../50-diagnostics/s11/2026-10-15-initial-full-comparison.md)
separates local implementation/verification from subsequent qualitative Windows feedback.

Windows 담당자는 다음 순서로 진행한다.

1. Work Plan에 지정된 커밋의 소스 ZIP을 별도 폴더에 풀고 기존 Windows Python
   환경을 사용한다. 원본 영상과 bundle은 Windows에 보관한다. ZIP 커밋/URL,
   실제 import 경로, Python/OpenCV/NumPy 버전을 기록한다.
2. 원본을 보며 **BASE와 Accum 각각 유체가 움직일 수 있는 용기 내부 전체**로
   ROI를 확인한다. 시작·하강·재충전·종료 장면을 확인하고 외부 rim/컵 테두리를
   제외한다. 순간적인 액면 높이에 맞춰 ROI를 줄이지 않는다. Recipe를 한 번
   저장한 뒤 OFF/ON에 동일하게 사용한다. Mac sample4 좌표를 옮겨 쓰지 않는다.
3. 기준 비교는 기존 480–780초 창, 같은 FPS·영점·스케일·초기 상태·판정 설정을
   사용한다. BASE는 FULL, Accum은 EMPTY 초기 확인을 유지한다. ROI가 바뀌면
   이전 bundle을 같은 조건의 OFF 결과로 간주하지 말고 OFF부터 실행한다.
   기존 bundle은 생성 소스와 입력/설정이 같은 경우 재사용할 수 있다.
4. 아래 OFF 실행으로 GUI에서 직접 분석을 시작하고 완료 bundle을 보존한다.
   GUI를 닫은 뒤 ON으로 다시 열어 같은 조건으로 분석한다. 결과 경로/이름을
   구분하고, 실행 중 설정을 조정하지 않는다. 두 실행의 debug 수준도 같게
   두며 기본 BASIC이면 충분하다. 원인 추적에 필요한 추가 상세 실행은 결과를
   읽은 다음 결정한다.

ZIP 루트에서 PowerShell로 실행한다. `python`은 기존 Windows 환경의 Python을
가리켜야 한다. `PYTHONPATH`는 다른 ZIP의 editable 설치가 선택되는 것을 막는다.

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
python -c "import oil_tracker; print(oil_tracker.__file__)"
python -m oil_tracker
```

OFF GUI를 닫은 후 같은 터미널에서 실행한다.

```powershell
python -m oil_tracker --initial-full-observation
```

ON 창 제목에는 `초기 FULL 관측 비교`, detector/resolver 버전에는
`+initial-full-observation-v1`이 붙어야 한다. 이 옵션은 Recipe 초기 상태를
자동 변경하지 않는다. 원시 후보·association·기존 drain/refill 규칙을 유지하면서
초기 FULL에서 허용되는 현재 계면 후보만 방향 미확정으로 출력한다. 새 출력의
CSV flag는 `OIL_DIRECTION_UNCONFIRMED`이고 보고서는 이를 방향 요약/하강 시작
판정에 사용하지 않는다고 설명한다. 후보가 없거나 다른 hard gate에 막힌 지점,
이미 drain/refill 상태로 전환한 뒤의 손실은 이 옵션의 해결 범위가 아니다.

먼저 BASE의 약 550–662초 하강과 662–663.6초 급속 재충전이 원본과 대조해
얼마나 드러나는지, 앞뒤 FULL 구간에 잘못된 선이 생기는지 확인한다. 보고서만
읽은 판단과 원본 대조 결과를 구분한다. Accum과 Foam 변화도 함께 기록하되
정확한 Y truth가 없는 곳은 위치 정확도를 단정하지 않는다. 아래 9개 구간을
모두 열거하고 아직 보지 않은 곳은 `NOT_EVALUATED`로 남긴다.

Mac에 전달할 최소 결과는 **소스/ROI/설정 동일 여부, 구간별 OFF→ON 관측 변화,
복원된 움직임, 오검출과 긴 공백, 보고서 해석 가능 여부, 실제 runtime**의 텍스트
요약이다. 비공개 영상·이미지·bundle을 Mac으로 전송할 필요는 없다. 이 결과를
받아 첫 수정의 효과와 남은 실패를 판단한 뒤 조건부 후보 순서를 적용한다.

### October 15 completed-bundle inspection

FULL+ON의 BASE 출력은 확인됐지만, 첫 하강 등장 누락과 중간 하강·상승의 추가
누락이 남았다. 사용자가 정정한 실제 상단 이탈 후 상태는 **기존/ON 모두
`UNKNOWN_REVIEW`**다. 원하는 동작은 실제 상승 계면을 상단까지 추적한 뒤
계면이 밖으로 사라지면 좌표 없는 `FULL_NO_INTERFACE`로 전환하는 것이다.
이 단계에서는 Windows에 있는 **완료 bundle을 읽고 텍스트 결과를 전달**한다.
사용자 요청에 따라 이번 저장 결과 점검에서는 해시 비교와 실행환경 검증을
생략한다. 이 생략을 이유로 재실행이나 추가 환경 확인을 요구하지 않는다.

사용자는 **① 초기 FULL+OFF, ② 초기 UNKNOWN+OFF, ③ 초기 FULL+ON**의 세 bundle을
보유하고 있다고 확인했다. 기존 ②↔③ 점검을 다음 세 비교로 보완한다.

| 비교 | 점검 목적 |
|---|---|
| **①↔③ — 주 비교** | 초기 FULL을 고정하고 ON으로 복원된 관측과 추가 손실 확인 |
| ①↔② | OFF를 고정하고 초기 상태 FULL/UNKNOWN에 따른 추적 차이 확인 |
| ②↔③ | UNKNOWN+OFF에서 보였지만 FULL+ON에서 놓친 실제 유면 구간과 최초 차단 단계 확인 |

①↔③에서 옵션 외 소스·설정이 같아야 ON의 효과를 분리할 수 있고, ①↔②에서도
초기 상태 외 조건이 같아야 한다. ②↔③은 초기 상태와 옵션을 함께 바꾸므로
그 차이를 ON만의 회귀로 해석하지 않는다. 세 비교 모두 기존 결과를 재사용한다.

1. 세 결과에 저장된 ROI, 분석 창, FPS, 초기 상태와 설정 차이를 기록한다.
   사용자 번호 ①②③을 결과 표에도 유지한다. ON은
   `analysis_manifest.json`의 Glass별 `sequence_resolver` 버전 접미사
   `+initial-full-observation-v1`로 확인한다. HTML 상단 버전만으로 판정하지 않는다.
2. `tracking_data.csv`를 Glass와 실제 frame/time으로 맞춘다. 첫 하강 등장,
   중간 하강·상승에서 추가로 누락되는 첫 지점, 상승의 마지막 실제 관측과
   직후 UNKNOWN 구간을 찾는다. 각 지점과 앞뒤 인접 표본에 대해 세 결과의
   `raw_oil_air_level_y`, `fill_state`, `oil_is_valid`/`is_valid`, confidence,
   flags를 작은 표로 남긴다. 숫자 관측 없음과 숫자는 있지만 유효하지 않음을
   구분한다. CSV 차이 자체를 실제 유면의 정답으로 삼지 않는다.
3. 해당 frame/time이 저장된 `debug/debug_trace.jsonl`에 있으면 원시 `state`와
   완료 결과 `sequence.state`를 함께 읽는다. 실제 저장된
   `sequence_decision_witness`의 phase/reason/allowed IDs, row admission/
   publishability, selected candidate와
   `sequence_material_phase_diagnostics.initial_full_observation`의 실패 조건을
   옮긴다. 원시 `oil_no_interface_full_likelihood`도 함께 기록한다. 상단 이탈은
   **재충전 종료 자체가 안 됨 / 종료됐지만 FULL 상태 후보가 없음 / 상태 후보가
   있어도 허용 집합이나 선택 단계에서 차단됨**을 구분하고, 저장 증거가 없는
   분기는 `UNAVAILABLE`로 남긴다. BASIC trace에 해당 행이 없는 것은 원시 후보가
   없었다는 뜻이 아니다. 가까운 trace 행을 같은 프레임의 결정으로 대체하지 않는다.
4. 아래의 9개 정답 구간 표에 CSV 관측 범위·Oil/Foam 수·공백과 실제로 확인한
   판정만 기록한다. 아직 시각 검토하지 않은 부분은 `NOT_EVALUATED`로 남기고,
   끝에는 처음 확인 가능한 손실 단계와 부족한 증거를 적는다. 원본·이미지·bundle은
   Windows에 유지하며, 이 점검만을 위해 영상을 다시 분석하거나 옵션을 바꾸지 않는다.

새 스크립트나 별도 검출 경로는 필요하지 않다. 기존 CSV/JSONL과 저장된 결정
기록을 사용한다. 점검 결과로 다음 수정 범위를 정한 뒤 추가 실행 필요성을
판단한다. 대용량 점검 출력을 만드는 경우 기존 [관리 출력 규칙](experiment-artifact-lifecycle.md)을
따라 `sample/output/` 안에 보관한다.

### October 15 audit reconciliation

전달된 첫 점검문은 BASE의 774초 숫자 관측을 실제 상단 이탈로 해석했지만,
기존 정답에서는 BASE가 약 663.6초에 FULL이 된 뒤 780초까지 계면이 없다.
또 source Y는 아래로 증가하므로 `dir=+1`을 상승으로 해석할 수 없다.
[수신 기록의 정정 사항](../50-diagnostics/s11/2026-10-15-initial-full-comparison.md#windows-three-bundle-audit-intake--reconciliation-required)을
읽고 기존 세 bundle에서 다음 내용만 다시 추출한다. 새 분석·해시 비교·환경
검증은 하지 않는다.

1. **548.5–550초:** ②의 Y363 출력과 ③의 Y367 출력 사이에 ③이 처음 허용되는
   시점과 앞선 누락 조건을 확인한다. 550초 한 점이 있다는 사실만으로 첫 등장
   누락 전체가 해결됐다고 판정하지 않는다.
2. **약 550–662초 하강 구간:** ②에 숫자 Oil이 있고 ③에는 없는 첫 지점과
   바로 앞뒤 표본을 찾는다. 실제 후보와 실패 조건을 기록하고, ②의 출력이라는
   이유만으로 물리적으로 옳은 유면이라고 확정하지 않는다.
3. **662–664초와 바로 앞뒤 표본:** 실제 재충전/상단 이탈에 해당하는 CSV와
   저장 trace를 비교한다. 774초 같은 분석창의 마지막 숫자 출력으로 대체하지
   않는다. 후보 Y·상태·허용 ID·선택·초기 FULL 관측 조건을 함께 읽는다.

원본 JSONL 한 행을 `record`라고 할 때 필드 위치는 다음과 같다.

| 내용 | 실제 저장 경로 |
|---|---|
| 원시 FULL 가능도 | `record.state.oil_no_interface_full_likelihood` |
| 최종 상태/좌표 | `record.sequence.fill_state`, `record.sequence.positions.raw_oil_y` |
| 최종 결정 | `record.sequence.state.sequence_decision_witness` |
| motion/허용 집합 진단 객체 (`diag`) | `record.sequence.state.sequence_material_phase_diagnostics` |
| release / recovery / established fill | `diag.release_stage`, `diag.release_evaluated`, `diag.release_evaluations`, `diag.recovery_qualifying_tracklet_ids`, `diag.recovery_selected_tracklet_id`, `diag.recovery_ambiguous`, `diag.established_fill_present` 등 |
| ON 관측 조건 | `diag.initial_full_observation`의 `motion_phase`, `motion_reason`, `blocked_by_current_state`, `evaluations`, `qualifying_tracklet_ids` |

release 계열은 `initial_full_observation`의 **상위 객체**에 있다. 원시 가능도는
`sequence.state`가 아니라 원시 `state`에 있다. BASIC/FULL은 저장 프레임·이미지가
다를 수 있지만, 저장된 행의 메타데이터/sequence 직렬화에는 별도 필드 생략 분기가
없다. 올바른 경로에도 값이 없을 때만 해당 경로와 함께 `UNAVAILABLE`로 남긴다.

`selected_authority_tier=HARD_INVALID`는 선택 후보가 없을 때의 기본값이기도 하며,
모든 원시 후보가 hard-invalid라는 증거가 아니다. recovery의 일부 `passed=true`도
최종 release 성공과 다르므로 qualifying/selected ID와 최종 phase reason을 함께
기록한다. `observed_interface`는 현재 프레임의 관측 허용 결과이며, 그 전후의
motion runtime은 계속 초기 `filled_barrier`일 수 있다.

결과는 세 구간의 작은 표와 최초 확인 가능한 차단 조건으로 요약한다. 기존 정답과
반대인 663.6초 이후 숫자 출력은 실제 상승 복원으로 집계하지 않는다. 첫 점검의
전체 observed 0/0.514/0.308과 회고적 ACCEPTED 홀드는 물리적 정답률이 아니다.

### Remaining three-record extraction

**완료.** 표 A/C와 별도 false-key 답변으로 필요한 세 행을 확보했다.
표 B의 누락 열은 원문 false-key 목록으로 바로잡았다. f13271은
`anchor_eligible, interface_identity`, f15884는 `anchor_eligible`, f15908은
`current_confirmed_owner, anchor_eligible`에서 실패한다. 세 raw outcome은
boundary/ambiguous이므로 FULL likelihood 0은 기본값이다. 상세 근거는
[진단 기록](../50-diagnostics/s11/2026-10-15-initial-full-comparison.md#three-record-predicate-intake)에
보존했다. 전체 JSON·후보 표·동일 세 행을 다시 요청하지 않는다.

### October 15 v2 Windows comparison

로컬 검증과 게시를 마친 v2 소스는 Work Plan의 현재 ZIP 링크를 사용한다.
이번에는 **기존 ③ FULL+ON v1과 새 ④ FULL+ON v2**를 비교한다.
① FULL+OFF와 ② UNKNOWN+OFF는 보존하고, ②는 누락 위치를 찾는 참고로만 쓴다.
추가 해시 비교·환경 감사나 기존 세 실행의 재분석은 요청하지 않는다.

1. 새 소스 폴더에서 기존 Windows Python으로 아래 GUI를 실행한다. 창 제목은
   `초기 FULL 관측 비교`, 실행 결과의 resolver 접미사는
   `+initial-full-observation-v2`다. 옵션 없이 실행하면 계속 OFF다.
2. 기존과 같은 영상·Recipe·ROI·480–780초·2 fps를 사용하고, BASE 초기 FULL과
   Accum 초기 EMPTY를 유지한다. GUI에서 직접 분석을 시작하고 새 bundle에 저장한다.
   BASIC trace면 이번 수치 비교에 충분하다. 원본 영상으로 위치/움직임을 대조한다.
3. 기존 ③과 새 ④의 첫 등장, 553.5/662.5/663.5초 출력, 실제 662–663.6초 재충전
   궤적을 비교한다. 숫자가 늘어난 것과 실제 유면이 복원된 것을 구분한다.
   663.6–780초의 숫자 후보는 정답상 FULL 구간의 오검출로 별도 집계한다.
   774초를 상단 이탈로 해석하지 않으며 source Y 감소가 상승이다.
4. 결과는 짧은 표로 전달한다: 구간별 유효한 복원/오검출/남은 공백,
   실제 상단에 닿는 마지막 계면의 시각과 위치, Accum/Foam 변화.
   새로운 실패가 나타날 때만 해당 판정의 false predicate 키를 덧붙인다.
   전체 JSON이나 66행 후보 표를 반복 전송할 필요는 없다.

721.01초에 대한 후속 표는 대상이 BASE이며 네 bundle 모두 같은
`oil-tracklet:000474:0424` 후보를 가진다고 보고한다. 후보 범위는 약
717–750.5초/Y675–748, 116회이며 여러 source의 같은 프레임 후보를 포함한다.
최종 출력의 첫/마지막 시각이나 116개 유효 관측으로 해석하지 않는다.
아래 [721초 후보/최종 출력 확인](#721-second-candidate-and-output-check)에
남은 항목을 좁혔다. 기존 전체 트랙릿 비교나 대상 Glass 확인을 반복하지 않는다.

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location).Path "src")
python -m oil_tracker --initial-full-observation
```

v2는 이미 승인된 현재 관측에 매번 새 앵커를 요구하던 조건을 수정한다.
방향 라벨은 계속 `PARTIAL_VISIBLE + OIL_DIRECTION_UNCONFIRMED`다.
**상단 소실 → FULL 전이는 이번 변경에 포함되지 않는다.** 이 결과에서 실제
재충전 owner의 연속성이 확인되면 그 전이를 별도로 구현한다. 중간 소실을
FULL로 바꾸거나 663.6초를 코드에 넣어서는 안 된다. 정식 FIELD PASS는 여전히
아래의 전체 9개 구간과 현재 acceptance owner가 판단한다.

### V2 final output reconciliation

첫 v1/v2 비교 답변은 세 기준 프레임의 IFO 조건 통과를 확인했지만,
후보 수·tracklet admitted 수와 `ambiguous/reacquisition_pending` 분포로
최종 출력이 같다고 결론냈다. 이 값들은 최종 숫자 Oil 또는 FULL 상태의
집계가 아니다. 아래 **기존 bundle의 최종 결과 확인을 먼저** 수행하고,
721.01초 추가 오검출 검토는 그 다음으로 유지한다. 소스 변경·재실행·해시
검증·전체 JSON 전달은 요청하지 않는다.

1. ③/④ 각각 `tracking_data.csv`에서 BASE `glass_id`만 골라 전체 행 수,
   `raw_oil_air_level_y`가 비어 있지 않은 행 수와 그 첫/마지막 시각,
   `fill_state=FULL_NO_INTERFACE` 행 수를 적는다. 빈 칸을 숫자 0으로
   바꾸거나 두 Glass를 합치지 않는다. `oil_is_valid`와 숫자 존재도 구분한다.
2. f13271/f15884/f15908을 버전별 6행 표로 적는다:
   `record.sequence.state.sequence_material_phase`,
   `record.sequence.state.sequence_material_phase_diagnostics.allowed_tracklet_ids`,
   `record.sequence.state.sequence_resolved_kind`,
   `record.sequence.positions.raw_oil_y`, CSV의 `raw_oil_air_level_y`,
   `fill_state`, `oil_is_valid`. 없음과 null/빈 값을 그대로 구분한다.
3. v2 CSV Oil이 계속 비어 있는 프레임에 한해서만
   `record.sequence.state.sequence_decision_witness`에서 해당 tracklet 행의
   `phase_admitted`/`publishable`과 `selection`을 덧붙인다. 이전의 모든
   후보 표를 다시 보내지 않는다.

기준 프레임이 실제 허용되고 최종 Oil도 생겼다면 관측 단계 수정 효과가 있는
것이다. 최종 값이 계속 없다면 witness로 그 다음 차단 지점을 좁힌다. 어느
경우에도 숫자 출력만으로 실제 유면 복원이라고 판정하지 않는다.
723초·771초의 재질/동일성 차단은 BASE FULL 구간의 오검출 억제일 수 있으므로
실패 조건이라는 이유만으로 완화하지 않는다. Accum/Foam 최종 동일성도 이후
최종 CSV 좌표/유효성으로 비교하며 원시 상태·후보 개수만으로 확정하지 않는다.

### 721-second candidate and output check

네 bundle의 BASE 후보 추적이 같다는 답변을 받았다. BASE는 이 구간에서
정답상 FULL이므로 비유면 후보라는 판단은 기존 정답과 사용자 영상 관찰에
근거한다. 궤적의 비단조성이나 direction 0↔1만으로 아지랑이를 확정하지 않는다.
현재 확인 중인 최종 CSV 점검에 아래 항목만 추가한다.

1. ①/②/③/④ 각각 **721초·723초에 대응하는 실제 표본**을 8행으로 정리한다.
   frame/time, `record.sequence.state.sequence_material_phase`,
   `sequence_material_phase_diagnostics.allowed_tracklet_ids`,
   `sequence_decision_witness.selection.selected_candidate`의 tracklet ID/Y,
   CSV `raw_oil_air_level_y`, `fill_state`, `oil_is_valid`를 적는다.
   두 diagnostics/witness 경로는 모두 `record.sequence.state` 아래다.
   선택 후보가 없으면 null을 보존하고, 후보 트랙릿의 Y로 대신 채우지 않는다.
2. ③에서 이 트랙릿이 처음 admitted 됐다고 보고한 **720초 표본 하나**의
   `record.sequence.candidates`에서 `tracklet_confirmation_profile`,
   `tracklet_confirmation_start_frame`, `tracklet_confirmation_end_frame`,
   `tracklet_direction`, `tracklet_recent_direction`,
   `tracklet_net_progress_px`, `tracklet_recent_net_progress_px`만 덧붙인다.
   기준 source/row를 함께 적고 같은 트랙릿의 중복 후보 표는 반복하지 않는다.

해석 주의: +1은 source Y 증가(하강), -1이 상승이다. 0↔1은 상하 반전의
증거가 아니다. 기존 direction/net progress는 최초 확정 창에서 유지될 수
있으며, 제시된 support 0.36/coverage 0.44만으로 motion 확정 기준
(각각 0.50)을 통과했다고 말할 수 없다. 앵커 확정/유지 경로와 구분한다.
723초 재질 veto가 오검출을 차단했다면 보존한다. 재실행·해시 비교·전체 JSON이나
전체 궤적 재추출은 필요 없다. 영상에서 아지랑이인지 식별하지 못하면 광학적
원인은 미확인으로 남긴다.

## 2. Private source identity

For `windows_sample1_heating_coldstart`, record without exposing the real filename:

- SHA-256;
- byte size;
- width and height;
- FPS;
- duration; and
- Recipe/Glass/ROI settings used for the run.

Use the operator alias only. The source fingerprint strengthens identity; it does not redefine the reviewed timeline.

## 3. Execute the supported production path

Run the current supported Windows production workflow with the candidate named by the Work Plan. Preserve the normal detector, completed-window resolver, publication/report path, and same-frame provenance owners.

Do not:

- tune thresholds or add case-specific configuration during qualification;
- use detector proposals, overlays, prior row counts, graph bridges, or an old bundle as physical truth;
- interpolate/carry a missing numeric observation;
- replay a historical R7–R12 procedure instead of the current candidate contract; or
- convert a diagnostic-only trace field into publication authority.

Collect the current validation contract's required runtime/performance/provenance evidence. General GUI scaling and packaging obligations remain in `manual-gui-windows-checklist.md` when those surfaces are part of the current qualification scope.

## 4. Reconcile all reviewed segments

Report every segment from the reviewed-truth owner individually:

- `WS1-BASE-FULL-PREFIX`
- `WS1-BASE-DRAIN`
- `WS1-BASE-RAPID-REFILL`
- `WS1-BASE-FULL-SUFFIX`
- `WS1-ACCUM-EMPTY`
- `WS1-ACCUM-ENTRY-SPLASH`
- `WS1-ACCUM-FOAM-LAYERED`
- `WS1-ACCUM-POST-FOAM`
- `WS1-ACCUM-DRAIN`

For each segment record sampled coverage, Oil/Foam numeric runs, selected source-Y range/direction where physically reviewable, longest missing/wrong-interface run, relevant lifecycle/owner transitions when available, and `PASS`, `FAIL`, or `NOT_EVALUATED`.

Exact coordinate accuracy is `NOT_EVALUATED` where no reviewed source-Y anchor exists. Presence/absence, material identity, ordering, direction, false-boundary rejection, and same-frame provenance remain valid acceptance dimensions without exact Y anchors.

## 5. Field disposition

A run is not `FIELD PASS` merely because local/canonical tests passed or aggregate coverage improved. Apply the current candidate validation contract plus canonical reviewed truth.

Any supported failure must identify the earliest harmful stage that the available evidence can establish. If the stage cannot be established, record the missing evidence and keep it unknown rather than inventing a causal mechanism.

A field `FAIL` does not authorize another detector revision automatically. Any follow-on behavior change starts from the newly observed failing stage and the current failure registry/logic map under a separately authorized detector task.

## 6. Evidence and closeout

Store completed field measurements under the current `docs/60-evidence/s11/` owner; causal investigation belongs under `docs/50-diagnostics/s11/`. Include the required `## Detector Governance` block from `docs/30-validation/s11-detector-change-governance.md`.

Update `docs/00-project/work-plan.md` only when field disposition, accepted baseline, named blocker/unknown, or next transition changes. Update the Roadmap only if formal milestone state changes. Do not rewrite archived R7–R12 procedures or older field evidence to match the new result.
