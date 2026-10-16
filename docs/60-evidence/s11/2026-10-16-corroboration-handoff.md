# S11 인수인계 — 계면 corroboration 검증 / 2026-10-16

## 현재 결론

기준 커밋은 `fd92e9a60ebe19e18d440b431d20e8f717da8788`이다.
이번 작업은 로컬 후보 지지 검증기와 테스트, 근거·인수인계를 추가했다.
**검출기 동작과 Recipe·모델·기존 truth는 변경하지 않았다.**
S11 ACTIVE / O2 OPEN / FIELD FAIL은 유지된다. Local XY·cost-first·RGB는
미채택이며, 초기 FULL 관측 v2는 opt-in 비교 기준이지 정식 승격이 아니다.

현재 상태와 승인 범위는 [Work Plan](../../00-project/work-plan.md)이 소유한다.
이 문서는 [직전 Windows 체크포인트](2026-10-16-windows-comparison-checkpoint.md)
이후에 새로 실행한 로컬 검증만 인계하며, 기존 Windows 판정을 대체하지 않는다.

## 이번에 실제로 실행한 일

[진단 기록](../../50-diagnostics/s11/2026-10-16-corroboration-peer-screen.md)은
가설·입력 범위를 먼저 고정한 뒤 두 가지를 검사한다. P1은 기존 교차 표현
지지의 실제 기여 후보를 모두 추적한다. P2는 다른 후보의 도움 없이 기존
anchor 조건을 통과하는 후보만 지지를 제공하도록 하는 비순환 조건이다.
이는 후보 단계의 필요조건 시험이며, 완성된 detector A/B는 아니다.

Mac sample4의 기존 7프레임과 공개 압축기 영상의 기존 1프레임을 사용했다.
전체 187개를 유지하면서 원시 타입으로 **Oil 175 / Foam 8 / 참조 문맥 4**를
분리했다. 기존 목록에서 Oil로 잘못 선언된 Foam 7개는 모두 미검토 항목이다.
이 오류 때문에 첫 시도가 중단됐으며, 원본 목록이나 과거 모델을 고치지 않고
이번 검증기의 source-kind 대조를 보완했다. 정답 라벨은 바뀌지 않았다.

| 결과 | 해석 |
|---|---|
| Oil 175개: 전체 계산 = 개별 지지 후보의 최댓값 | 기존 점수 산식을 재구현하지 않고 실제 production 함수를 호출하여 확인 |
| 8프레임·175후보 역순 대조: 불일치 0 | 후보 나열 순서가 결과를 바꾸지 않음 |
| 허용된 material 후보의 지지 0.4122, 같은 프레임 rim material 후보 0.7605 | 단순한 지지 점수 하한 상향으로 이 양성·음성을 분리할 수 없음 |
| 두 rim 후보가 서로 다른 표현 계열로 상호 지지 | 계열이 다르다는 사실만으로 물리적 계면이 독립 확인된 것은 아님 |
| P2로 기존 material 지지를 잃는 후보 15개 | 허용 1 / 반대 2 / 미검토 12. 양성 보존 조건 실패로 미채택 |
| 관련 로컬 테스트 342 passed / 0 failed | 단위·메커니즘 검증이다. 현장 검출력이나 사용자 report 이해의 PASS가 아님 |

**P2는 구현·승격하지 않는다.** 약한 실제 계면을 보호하려면 비순환적인
측정 근거와 기존 강한 anchor 자격을 구별해야 한다. 허용된 11개 후보의
P2 지지가 모두 낮다고 해서 최종 Oil 관측 11개가 삭제됐다는 뜻은 아니다.
최종 sequence·CSV·report는 이번 시험에서 다시 실행하지 않았다.

## 읽을 근거와 재현

결과의 전체 분모·기여 후보·타입 불일치는
[readout.json.gz](../../50-diagnostics/s11/2026-10-16-corroboration-peer-screen/readout.json.gz)에 있다.
정확한 테스트 명령, 소스 해시, 순서 대조와 rim 반례는
[verification.json](../../50-diagnostics/s11/2026-10-16-corroboration-peer-screen/verification.json)에 있다.
설계와 검증 조건은 기존 [설계 owner](../../20-architecture/s11-physical-interface-evidence-repair-design.md#independent-corroboration),
[검증 owner](../../30-validation/s11-physical-interface-evidence-repair-validation.md#required-two-sided-controls)에 반영했다.

```sh
.venv/bin/python -m tests.diagnostics.s11_corroboration_peer_screen \
  --output /tmp/s11-corroboration-peer-readout.json
.venv/bin/python -m pytest -q tests/unit/test_s11_corroboration_peer_screen.py
.venv/bin/python scripts/check_detector_governance.py --base-ref fd92e9a --include-worktree
.venv/bin/python scripts/experiment_artifacts.py check
```

전체 재현은 Mac의 `sample/output/s11-a1-lineage-20261007-001/frames-final/` 등
해시가 고정된 저장 입력을 필요로 한다. GitHub source ZIP만으로 원본 입력이
자동 복원되지는 않는다. 코드와 압축 판독표는 영상 없이도 검토할 수 있다.
대형 원본·중복 영상은 새로 복사하지 않았고 Windows 원본은 반출하지 않았다.
관리 실행은 `sample/output/s11-corroboration-peer-screen-20261016-001/`과
`...-002/`이며, 첫 입력 계약 실패도 숨기지 않고 보존했다.

## 남은 문제와 다음 작업의 경계

721초 Y694 오출력의 승인 경로는 기존 Windows 수신 자료로 확인됐지만,
이번 로컬 rim 쌍이 그 프레임의 실제 원인이라는 뜻은 아니다. 당시의 실제
최대 지지 peer와 완전한 원시 물리 witness는 이 환경에 없다. 단순히 지지
점수를 높이거나 기존 anchor 자격을 중복 요구하는 후속안을 반복하지 말 것.
다음 검출기 제안은 실제 native contour와 양측 영역·측정 계보를 통해
허용된 약한 계면과 검토된 rim을 구별하는 근거부터 보여야 한다. 현재는
그 물리 판별기가 검증됐거나 구현 대상으로 선정된 상태가 아니다.

FULL은 별도 미완료 항목이다. 기존 preflight의 물리 endpoint Y220.870,
mask top Y243, 마지막 선택 Y352는 상단 도달을 증명하지 못한다. margin을
줄이거나 mask edge를 FULL로 재정의하지 않는다. ⑧은 실행되지 않았다.

Foam의 raw proposal 부재·역할 판별·episode 유지도 구분하여 보존한다.
Sample3 격리를 해제하거나 새로운 학습/모델 탐색을 시작하지 않는다.
Review-004/005의 복수 허용 후보·불확실성, 723/771초 보호 조건, 기존
9개 Windows 구간과 Oil/Foam 독립성을 후속 판정에서 잃지 않는다.

새 Windows 실행이나 추가 캡처를 지금 요청하지 않는다. 최종 제품 인수는
report에서 상승·하강·전환·Foam 출현/소멸과 관측 불확실성을 이해할 수
있는지로 판단한다. 작은 누락을 없애려고 전체 실제 움직임을 지우거나,
모든 구간을 UNKNOWN으로 만드는 것은 통과가 아니다. 실제 report-only
독립 판독과 현장 통합 인수는 아직 완료되지 않았다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F09`, `S11-F10`.
- First harmful stage: the received Windows false anchor precedes tracklet publication; local reviewed-rim cross-family support is confirmed separately, not equated with that private raster cause.
- Existing feature coverage: reuse frozen current candidates, source geometry/settings, Artifact/static/motion/mask evidence and original labels. No model, Local XY, sample3 decode or new detector configuration is enabled.
- Execution scope: offline pair attribution and nonrecursive support screen on 175 Oil candidates, full 187-unit typed inventory, 175 reversed-order checks and 342 local tests. No completed Windows or report-comprehension validation.
- Logic-map impact: NONE — diagnostic caller and handoff only; production ownership and evidence consumers unchanged.
- Failure-registry impact: NONE — the existing identity/appearance and provenance classes cover the rejected screen; no new adopted mechanism.
