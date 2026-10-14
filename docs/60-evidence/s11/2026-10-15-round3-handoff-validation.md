# S11 round 3 — handoff validation and disposition

Base: `7a57064046b0c650f552f6e4d9e2ceb73002972f`, main; round-1/2 dirty changes are preserved.
Current state and completion budget remain owned by [Work Plan](../../00-project/work-plan.md).

## Frozen scope before execution

Review the retained browser checker at its actual assurance boundary: labels and image loads do not prove that the visible canvas advances to the named frame. Reuse the existing checker and product source-sequence template. Demonstrate a stale-canvas false pass with a synthetic fixture, then add a bounded rendered-frame check and regression coverage. Verify the unchanged retained report only for this newly identified assurance gap; do not repeat DTO-1, confidence/authority trials, crop inventory, detection or video decoding.

Preserve baseline report, source pixels, role judgments and round-1 files. No production source/Recipe/UI change, new model, threshold experiment, Windows replay or invented reader response. Record actual reader comprehension as PENDING. A failed diagnostic check is not automatically a product defect.

Finish by validating the combined dirty change set, preparing a clean-HEAD-applicable handoff patch and verifying reconstruction without altering the primary checkout or publishing. Existing round-2 patch is incremental; it is not a clean-HEAD recovery package.

## Detector Governance

- Logic-map nodes: `RESULT-PRESENTATION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: at entry, the browser diagnostic asserted label/asset success without observing displayed canvas identity. This is an assurance gap, not evidence of a product rendering failure or a new physical detector cause.
- Existing feature coverage: reuse the saved completed sample4 report (empty exclusions/Artifact templates, Local XY OFF, 2 Hz, confirmed UNKNOWN). Browser checks exercise the already generated source-sequence controls; preparation/detection/completed resolution are bypassed. Synthetic controls reuse the executing product JS template, not physical scenes.
- Execution scope: local isolated Chrome and focused regression tests plus handoff reconstruction. No video decode, new numeric observations, independent human reading, target-Windows qualification or acceptance change.
- Logic-map impact: NONE — only diagnostic verification changes; product source-sequence renderer and all production routes remain unchanged.
- Failure-registry impact: NONE — displayed-frame versus label/source provenance is covered by F09; no mechanism is retired.

## Results

**생산 detector 개선은 없다.** 이번 변경은 기존 browser 검증기의 실제 화면 판별 공백을 고치고, 이전 1·2회차를 포함한 작업을 넘길 수 있도록 준비한 것이다. 제품 HTML/JS·수치·Recipe·기존 판정은 바꾸지 않았다. 실제 report-only 응답과 Windows 인수는 여전히 미완료이다.

| 확인 항목 | 실제 결과 | 한계 |
|---|---|---|
| 수정 전 검증기 반례 | 첫 타일에 고정한 synthetic 화면도 기존 checker는 exit 0; 새 회귀 테스트가 의도대로 실패 | 제품 report의 정지 화면 결함이 확인된 것은 아님 |
| 최종 관련 테스트 | **117 passed / 55.24초**, 신규 browser 대조군 4개 포함 | 전체 canonical/Qt/Windows 검증 아님 |
| 실제 retained report | 3개 source card, 8개 화면 상태 / 고유 source frame 7개 | 전체 497 source 레코드의 렌더링 전수 검증 아님 |
| 실제 화면·선택 타일·복원 화면 | 각 상태의 PNG SHA-256 세 값 모두 동일 | source tile의 물리적 정답이나 사용자 이해도 아님 |
| 기존 controls/assets | slider 4위치·next 동작, 이미지 30개 로딩, page/network error 0 | 현재 Mac Chrome와 고정 report에 한정 |
| 원본 보존 | report HTML SHA-256 유지; 1회차 코드 4개 진입 hash와 동일 | 과거 영상 전체 재검증이나 새 detector 실행 아님 |

보고서 hash는 `86fb91131be6c5316be5376a3c1c0ca8b35fca4cfc6c9ced8b9ffff9ec840172`이다.
실행 브라우저는 `Chrome/154.0.8037.98`, Node는 `v24.21.0`이다. 기존 환경을 사용했으며 설치하거나 브라우저 file-access 보안을 완화하지 않았다.

## 실패 보존과 검증 방법 보완

정상 `file://`의 canvas `getImageData`는 SecurityError였다. 보안을 낮추지 않고 CDP 화면 캡처를 사용했다. 최초 방법은 별도 absolute reference canvas를 겹쳐 비교했는데, synthetic 테스트 116개는 통과했지만 실제 report의 첫 화면에서는 배치가 달라 불일치했다. 해당 실패·스크린샷·검증 소스를 별도 관리 실행에 보존했고 제품 오류로 판정하지 않았다.

최종 방법은 스크롤을 즉시 이동하고 두 animation frame을 기다린 다음 실제 canvas를 캡처한다. 기존 픽셀을 offscreen canvas에 백업하고 **동일한 canvas·CSS 위치**에 선택된 source tile을 별도 경로로 그려 두 번째 캡처와 비교한다. finally에서 원래 픽셀을 복원하고 세 번째 캡처가 최초 화면과 같은지도 확인한다. 디스크의 보고서·제품 코드는 불변이며, 격리된 진단 브라우저의 픽셀만 일시적으로 덮었다가 복원한다. 새 테스트는 정상·정지·빈 화면·확대/소수점 위치의 네 경우다.

첫 red-test는 pytest가 만든 `current` symlink 때문에 artifact finish가 거절되었다. 해당 링크와 자기 테스트 디렉터리 안의 target을 확인한 후 링크만 제거하고 closeout했다. target이나 기존 증거를 임의 삭제하지 않았다. 이후 테스트는 일반 pytest 임시 경로를 사용했다.

## 보존 범위와 capability disposition

자동 수치의 물리적 정답, 원본 비교 UI의 작동, 실제 사람의 전체 맥락 이해를 분리한다. 기존 42/44초 잘못된 대표 극값과 A 맥락 왜곡 판정은 미해결이다. 원본 비교 보조의 이번 렌더링 범위만 확인했으며, 이를 근거로 제품 지원 범위를 줄이거나 제한 인수를 확정하지 않는다. actual reading, target-Windows nine segments, O2/V5 및 최종 acceptance는 그대로 남는다.

변경한 코드 owner는 [기존 browser helper](../../../tests/diagnostics/s11_report_browser_smoke.mjs), 새 회귀 테스트는 [browser regression](../../../tests/unit/test_s11_report_browser_smoke.py)이다. 이전 DTO-1과 confidence/authority-only 실험은 재실행하지 않았다. 새로운 detector candidate가 없으므로 Windows 비교를 다시 요구하지 않는다. 남은 한 회차를 또 다른 일반 audit/descriptor 탐색에 쓰지 않고 실제 판독과 WP10 결정에 사용한다.

## 실행·인수인계 경로

- `sample/output/s11-round3-assurance-gap-20261015-001/evidence/`: 수정 전 false-pass와 file-origin 제약, 진입 hash.
- `sample/output/s11-round3-closeout-20261015-001/evidence/`: 최초 reference 배치 방법의 실패·소스·비교 화면.
- `sample/output/s11-round3-closeout-20261015-002/evidence/`: 최종 browser.json, 테스트, 실행 요약, 통합 patch·변경 파일 manifest·재구성 receipt와 한국어 handoff.

통합 patch는 **clean `7a57064046b0c650f552f6e4d9e2ceb73002972f` 기준**의 1–3회차 변경 전체를 담는다. 현재 Mac 작업트리에는 이미 있으므로 재적용하지 않는다. 기존 ROUND2.patch는 1회차 dirty 상태 기준의 증분이므로 clean HEAD 복원에 사용하지 않는다. 정확한 재구성 결과와 hash는 `reconstruction.json`/`HANDOFF-MANIFEST.json`이 기록한다. 이전 source/media/report는 패키지에 중복 복사하지 않는다.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q tests/unit/test_s11_report_browser_smoke.py tests/unit/test_s11_report_context_audit.py tests/test_s11_dense_temporal_role_probe.py tests/unit/test_source_sequence_renderer.py tests/unit/test_report_presentation.py tests/unit/test_result_bundle_reader.py
node --check tests/diagnostics/s11_report_browser_smoke.mjs
.venv/bin/python -B scripts/check_detector_governance.py --base-ref 7a57064 --include-worktree
```

S11 ACTIVE / O2 OPEN / FIELD FAIL / Local XY OFF. commit·push·merge·release 없음. 실제 사람이 작성하지 않은 판독 기록은 PENDING 그대로다.
