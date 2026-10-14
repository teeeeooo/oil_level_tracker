# S11 round 2 — retained-report context and candidate disposition

**Execution baseline:** `7a57064046b0c650f552f6e4d9e2ceb73002972f`; round-1 dirty changes are preserved.
**Scope frozen before execution:** inspect the retained completed sample4 report, its original source-crop assets and qualified reply bindings. Do not rerun detection, fit a feature, tune a threshold or change report output.
The [Work Plan](../../00-project/work-plan.md#bounded-completion-budget--2026-10-14) owns current state and the 3–4-round budget.

## Frozen questions and execution plan

1. Verify final samples/events, the two reviewed wrong extrema and the preserved 42.5 s observation using the existing `ResultBundleReader`. Reuse corrected candidate-role evidence without turning unknowns into negatives.
2. Check the sufficiency of **confidence-only monotone rejection** and **authority/reason/failed-gate-only rejection** by exact positive/opposition contradictions. These are saved-evidence feasibility checks, not new detector trials or claims that all richer mechanisms are impossible.
3. Verify all three embedded source-sequence manifests, local asset availability, sprite bounds, overlapping original crop equality and the complete f1275–f1320 interval. Original report pixels are reused; no new video decode or contour truth is created.
4. Run the retained HTML in an isolated headless local Chrome session and exercise existing controls. Record actual browser results separately from human comprehension. Do not alter the HTML, add controls or infer physical correctness from rendered pixels.
5. Keep independent report-only reading **PENDING** unless an actual attributable response is received. Select no production package unless wrong-output suppression and genuine-motion preservation have an evidence-supported mechanism.

Existing inputs: [scene roster](../../50-diagnostics/s11/2026-10-12-scene-evaluation-roster.json), [qualified candidate reuse](../../50-diagnostics/s11/2026-10-13-existing-material-execution/readout.json), [saved complete run](../../50-diagnostics/s11/2026-10-11-p5-default-linkage/readout.json), and the retained `s11-p5-default-linkage-20261011-001/none/` report bundle. Exact byte pins are recorded by the managed run.

Execution budgets: temporary browser/profile and diagnostics **200 MB**; retained compact audit/browser evidence **2 MB**. Reuse all original media, report assets and prior Windows results. Tests use temporary fixtures; no new training/runtime installation, sample3 replay, Windows run, commit or push.

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F03`, `S11-F09`, `S11-F10`.
- First harmful stage: retained wrong targets already have final same-frame numeric observations before extrema presentation; no fresh Windows cause is established. Current frame, candidate authority and completed samples remain distinct.
- Existing feature coverage: retained sample4 Recipe has empty exclusions and Artifact templates, Local XY OFF, 2 Hz completed analysis with confirmed UNKNOWN initial state. The stored run exercised production preparation and completion; this audit reuses outputs and bypasses fresh preparation/detection/sequence resolution. Closed D2/Local XY and DTO-1 results are not retried.
- Execution scope: offline saved-bundle/qualified-evidence inspection and existing report browser controls only. No detector consumer or report output changes; no source video decoding, independent human response or target-Windows execution is implied.
- Logic-map impact: NONE — existing product reader, report assets and authority responsibilities are reused without changing their executing routes.
- Failure-registry impact: NONE — saved confidence/authority contradictions and source/report distinction are instances of existing guards, not new physical truth or a retired failure class.

## 실행 결과와 결정

**생산 detector 변경은 없다.** 2회차의 저장 증거·보고서 실행 검증은 수행했으나,
계획에 있던 실제 독립 report-only 판독은 **응답 대기**이다. 따라서 2회차 전체
인수 완료나 S11 완료라고 기록하지 않는다. 현재 검토한 제한된 두 정책으로는
잘못된 대표 극값을 안전하게 고치는 behavior package를 선택할 수 없었다.
이는 더 풍부한 관측·기법 전체의 불가능성 판정이 아니다.

| 실제 검증 | 결과 | 해석 한계 |
|---|---|---|
| 기존 completed bundle | 113행 / Oil 수치 101 / Foam 수치 26 / event 31 | 검출 정확도가 아니다 |
| producing `src/` byte pin | 221/221 일치 | 새 detector 실행·Windows 검증이 아니다 |
| 과거 표시 관측 7개 결속 | 시간·Y·높이·유효성·상태·flags 일치 | f1485의 뒤이은 물리 판정 제한은 유지한다 |
| 대표 최저/최고 | 42초 Y868 / 44초 Y822, 모두 기존 opposed target | 기존 A 맥락 왜곡 항목 유지; report에서 숨기거나 새 정답으로 바꾸지 않았다 |
| 현행 candidate 역할 전체 | 164개 = target correspondence 6 / opposition 3 / unassessed 153 / not-qualified 2 | 9개를 164개 전체의 정확도 평가로 바꾸지 않았다 |
| 원본 시퀀스 3개 | 497개 available 레코드 / 고유 source frame 379 | 겹치는 구간이 있어 497개 독립 프레임이 아니다 |
| 겹친 source crop | 118회 동일 RGB bytes | 저장된 crop끼리의 확인; 원본 MP4 재decode 검증은 아니다 |
| 검토된 42.5–44초 | f1275–f1320 연속 46프레임이 기존 report에 모두 존재 | detector가 46프레임을 올바르게 측정한다는 뜻이 아니다 |
| 별도 CSV/OpenCV 검산 | 113행·497 RGB crop 레코드 대조 PASS | 새로운 물리 판정이나 독립 인간 판독이 아니다 |
| 실제 오프라인 Chrome | 시퀀스 3개, slider 4개 위치·next 버튼, 이미지 30개 로딩 PASS; page error 0 | Windows/모바일 브라우저 일반화·사용자 이해도는 미평가 |
| 관련 테스트 | 새 23개 포함 96 passed / 6.91초 | 전체 canonical/Qt/Windows suite가 아니다 |

### 폐기한 두 가지 간단한 수정

**Confidence만으로 낮은 값을 버리는 방식:** 실제 대상인 42.5초의 confidence는
0.789100531485429인데, 잘못된 42초 검출은 0.8345865128564426이다.
`confidence >= cutoff`를 유지 조건으로 쓰면, 전자를 보존하면서 후자만 버릴 수 없다.
52초의 실제 대상(0.825143160650107)도 같은 42초 반례보다 낮다.
임계값 탐색이나 detector 재실행 없이 저장 값의 순서만으로 이 제한된 정책의
반례를 확인했다. 모든 confidence 활용법을 부정하는 결과는 아니다.

**Authority/reason/failed-gate만으로 거르는 방식:** 실제 대상 f1275/idx12 및
f1560/idx20과 opposed f1320/idx21은 다음 tuple을 똑같이 갖는다.

```text
CONTINUATION_ELIGIBLE / continuation / [ordered_lower_cross_representation]
```

이 tuple만을 입력으로 받는 결정은 세 후보를 다르게 처리할 수 없다.
Candidate source family에도 실제 대상과 opposed 예가 함께 있다.
이 때문에 authority 하나를 금지하거나 특정 candidate family를 제거하는
package를 만들지 않았다. 이미 리뷰된 급격한 실제 운동을 단순 jump 제한으로
지우는 것도 수정으로 채택하지 않는다. 새로운 시간·위치 branch, 모델, DTO-1
변형이나 Foam episode 완화도 실행하지 않았다.

### 보고서에서 확인한 사용 가능성과 미확정 부분

실제 Chrome의 `file://` 모드에서 기존 HTML을 수정하지 않고 열었다.
특별한 file-access 플래그 없이 source slider의 42.5/44/46/40초 위치와 처음·끝
button 상태, next 동작 및 로컬 이미지를 확인했다. 44초 source card의 실제 화면도
열어 확인했다. 원본 crop에 계면선을 새로 그리거나 수치를 보간하지 않았다.

원본 시퀀스는 다음과 같다: Foam 문맥 37.5–55초 240개(시간축 subsampling),
대표 극값 주변 40–46초 181개(native 30 fps), 긴 Oil 관측 공백 49.5–52초
76개(native 30 fps). Foam 마지막 수치는 53초이며 report는 53.5초를
**관측 중단**으로 표현한다. 물리적 소멸을 확정하는 표현이 아니다. 55.5/56초는
이 source-sequence 범위 밖이므로 끝까지의 Foam 상태 판독을 새로 인증하지 않는다.

**확인한 것은 판독 자료의 존재·일관성·실행 가능성이다. 실제 사람이 요약·그래프와
원본 시퀀스를 함께 보고 잘못된 대표 극값에 휘둘리지 않고 움직임을 이해하는지는
아직 답변이 없다.** Agent의 graph/capture/source-card 점검은 개발자 점검으로만
기록하며, 실제 독립 판독 또는 새로운 C 잔여 오류 수용으로 승격하지 않는다.

## 다음 회차의 시작점

저장 report를 다시 생성하거나 baseline Windows 분석을 다시 요청하지 않는다.
다음 필요한 입력은 원래의 report-only 판독 응답이다. 보고서의 예상 정답을 먼저
설명하지 않고, 첫 인상과 report 내 원본 비교 후 판단을 별도로 적는다. 이미 이
결과를 알고 있는 검토자는 노출 사실을 기록하며 naive/blind 판독이라고 부르지 않는다.
`REPORT-READING-RECORD.json`의 미응답 칸은 그대로 두었다.

판독 후에도 A/B blocker가 남고 근거가 있는 단일 수정이 없으면, 다음 회차를 다시
descriptor/threshold 연구로 바꾸지 말고 WP10에서 **자동 수치 해석 / 원본 비교
보조 / 미지원·미평가 범위**를 명시해 개발 동결·제한 인수 여부를 결정한다.
새로운 지원 범위 변경에는 사용자 결정이 필요하다. 유효한 후보가 없으므로
3회차의 candidate Windows replay를 미리 요구하지 않는다. O2/V5와 기존 9개
canonical Windows segment는 삭제·통과 처리하지 않는다.

## 코드, 실행 기록 및 재현

추가한 것은 [저장 보고서 audit](../../../tests/diagnostics/s11_report_context_audit.py),
[기존 HTML browser smoke](../../../tests/diagnostics/s11_report_browser_smoke.mjs),
[회귀 테스트](../../../tests/unit/test_s11_report_context_audit.py)이다. 새 detector나
제품 UI, 대체 acceptance evaluator가 아니다.

관리 실행은 `sample/output/s11-round2-context-20261014-001/evidence/`의
`audit.json`·`execution.json`과 `sample/output/s11-round2-browser-20261014-002/evidence/`의
browser·별도 검산·인수인계 자료로 분리했다. 첫 browser 시도는 **검증 스크립트의
괄호 문법 오류**로 실패했으며 report 오류가 아니다. 해당 실패를 보존하고 새 source
pin의 별도 browser 실행에서 수정 확인했다. 임시 browser profile만 정리했으며
기존 영상·report·truth·round-1 변경은 보존한다.

```sh
# 실제 사용한 focused test entry (repo root)
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q \
  tests/unit/test_s11_report_context_audit.py \
  tests/unit/test_source_sequence_renderer.py \
  tests/unit/test_report_presentation.py tests/unit/test_result_bundle_reader.py
```

Audit CLI는 `/private/tmp`에서 repo를 `PYTHONPATH`로 지정하여 실제 실행했다.
재현 때도 관리 run을 먼저 등록하고 `--output`에는 새 `work/` 경로를 사용한다.
Browser entry는 `node tests/diagnostics/s11_report_browser_smoke.mjs REPORT WORK_DIRECTORY`이며
현재 helper는 Mac의 설치된 Chrome 경로를 명시한다. Windows용 실행기로 오해하지 않는다.

S11 ACTIVE / O2 OPEN / FIELD FAIL / Local XY OFF. commit·push·merge·release 없음.
