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

1. 세 결과의 manifest/session/Recipe를 읽고 소스, ROI, 분석 창, FPS, 초기 상태와
   설정 차이를 기록한다. 사용자 번호 ①②③을 결과 표에도 유지한다. ON은
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
