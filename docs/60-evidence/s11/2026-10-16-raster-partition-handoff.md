# S11 인수인계 — CRW-1 원본 픽셀 경계·분할 검증 / 2026-10-16

## 결론과 완료 범위

**새 측정 코드 구현, 고정 가설의 실제 입력 검증, 결과·인수인계를 완료했다.
검출기 성능 개선이나 보고서 이해도 향상을 입증한 것은 아니다.**
판정은 **입력 측정의 부분적 유용성 확인 / 단독 물리 판별 미검증 / 제품 미승격**이다.
현행 상태는 **S11 ACTIVE / O2 OPEN / FIELD FAIL**이며
[Work Plan](../../00-project/work-plan.md)이 상태와 다음 전환을 소유한다.

시작 HEAD는 `20d5d4d555e1296959a75f3c2c0eb96b12de6e71`이다.
가설·측정기·별도 검산기·31개 신규 테스트를 실제 입력 실행 전에
`7845f890c52e2c6fab2b4b1a84f2e2139f9ded3e`로 고정했다.
제품 `src/`, Recipe, 모델, 정답, 최종 Oil/Foam, report는 변경하지 않았다.
최종 결과 문서의 게시 HEAD는 Git 이력에서 확인한다.

## 이번에 직접 실행한 것

[CRW-1 설계·실행 기록](../../50-diagnostics/s11/2026-10-16-raster-partition-screen.md)과
[기계 판독 요약](../../50-diagnostics/s11/2026-10-16-raster-partition-screen/summary.json)에 전체 조건·분모를 남겼다.
기존 sample4 7프레임과 공개 압축기 f1499, 총 8개 저장 원본 raster를 사용했다.
187개 항목은 실제 Oil 175 / Foam 8 / 문맥 4이며, Oil만 새로 측정했다.
157개 미검토 Oil과 물리적 대응·실용적 허용의 차이는 그대로 보존했다.

동일한 가로 위치의 픽셀끼리만 경계 위·아래를 비교했다. 경계 인접 두 행과
그 바깥 네 밴드를 분리하고, 네 밴드 모두 유효한 동일 위치만 사용했다.
기존 5개 sector와 밴드 폭을 재사용하고, 모든 동률 peak·대안·탐색 경계에서
잘린 관측을 남겼다. 새 측정은 기존 native 경로로 둔갑시키지 않았으며,
후보 Y를 바꾸거나 여러 sector peak를 검증된 연속 윤곽으로 선언하지 않았다.
같은 추출기가 같은 위치를 반복 관측하면 독립 지지표가 아니라 중복 측정이다.

| 가설 / 검사 | 고정 조건의 결과 | 판단 |
|---|---|---|
| 현재 raster에서 경계 위치를 다시 관측할 수 있는가 | 허용 11개 중 10개에 3개 이상 유효 sector peak | 입력의 부분적 가용성. 물리적 역할·연속 윤곽 검증 아님 |
| 양측 분할이 허용 계면을 보존하는가 | 허용 11개 중 8개, 검토 프레임 8개 중 7개에 허용 후보의 분할 조건 존재 | 부분적으로 유용한 측정. 검출률이나 연속 추적 성능 아님 |
| 검토된 비대상과 구분되는가 | 비대상 7개 중 6개는 같은 조건 불충족, 1개는 충족 | 단독 판별기로 사용할 근거 부족 |
| 기존 peer가 같은 측정을 반복하는가 | 85개 방향성 관계 중 33개는 일부, 7개는 3개 이상 sector에서 같은 분할 행 공유 | 같은 추출의 중복이므로 독립 표로 합산하지 않음 |
| 별도 직접 픽셀 검산 | gradient 6,133개 / 4-band 1,244개, 불일치 0 | 측정 산술 재현 |
| 관련 테스트 | 123 passed / 0 failed, 7.17초 | 신규 31개 + 기존 관련 92개 |

검토된 허용 후보 11개는 기존 물리적 대응 6개와 실용적 근사 허용 5개다.
공개 압축기 한 프레임의 허용 대안 4개 중 2개가 조건을 만족했다. 이것을
“절반 검출 실패”로만 볼 필요는 없다. 해당 프레임을 표현할 대안은 남는다.
반대로 8개 정지 프레임의 결과만으로 움직임 전체가 보존됐다고 할 수도 없다.

f1140에서는 허용 material 후보가 3개 sector를 유지했고 검토된 rim 3개는
그보다 적었다. 그러나 f1200에서는 비대상 idx10/Y865.5가 4개로,
허용 idx4/Y841의 3개보다 많았다. f1320에서는 허용·비대상 모두 2개였다.
따라서 **지지 sector 수를 키우거나 최댓값을 고르는 방식은 물리적 정답이 아니다.**
이를 고치려고 밴드·탐색 폭·개수 임계값을 재조정하지 않았다.

## 보고서의 움직임 맥락에 대한 판단

이번에 폐기한 것은 “이 분할 개수만으로 계면을 승인한다”는 해석이지,
부분적으로 유용한 측정 전체가 아니다. 한두 후보의 누락·비대상 잔존만으로
보고서 전체 실패를 선언하지 않는다. 실제 선택된 잘못된 계면의 지속시간,
거짓 극값·방향 반전, 회복/Foam episode 소실 여부로 영향도를 판단해야 한다.
이번에는 최종 sequence를 바꾸지 않았으므로 그 개선 효과는 미측정이다.

[Windows 수신 비교](2026-10-16-windows-comparison-checkpoint.md)는 재실행하지 않았다.
④ initial-FULL v2는 BASE 수치 Oil 185→303행으로 회복했지만 721초 비유면
Y694를 노출했다. ⑤ cost-first는 BASE 회복 구간을 잃었고, ⑥ RGB는 BASE
수치를 모두 잃었으며, ⑦ Local XY는 비유면 대체 출력과 허용 Accum 계면
소실이 있었다. 세 후보가 미채택인 이유는 완벽하지 않아서가 아니라 실제
움직임을 더 잘 전달하는 통합 개선이 입증되지 않았기 때문이다.

FULL은 별도 미완료다. 물리 endpoint Y220.870 / mask top Y243 / 마지막
선택 Y352로 상단 도달이 입증되지 않아 ⑧은 실행되지 않았다. mask edge를
FULL로 바꾸지 않는다. 721초 원시 peer·광학 원인은 여전히 미확인이며,
이번 Mac 결과를 그 원인의 증명으로 사용하지 않는다. 723초 material veto,
771초 identity 보호, review-004/005의 복수 허용·불확실성을 유지한다.

[정식 Windows 9개 구간](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#reviewed-timeline)과
실제 독립 report-only 판독이 최종 인수에 남는다. BASE 하강 550–652초,
회복 652–674초, FULL 전환 674–675초라는 정정을 보존한다. Accum의 유입,
Foam 형성·층상 구간, Foam 소실 후 Oil 유지, 이후 하강도 함께 평가한다.
Oil 관측으로 Foam의 raw proposal·역할·episode 문제를 해결했다고 하지 않는다.

## 다음 담당자가 이어갈 범위

입력 산술·native 유무 audit부터 반복하지 않는다. 새 물리 판별/consumer는
아직 선정되지 않았다. 다음 작업 단위는 기존 측정·반례를 재사용해
[설계 owner](../../20-architecture/s11-physical-interface-evidence-repair-design.md#independent-corroboration)에서
**어떤 물리적 역할 근거를 어느 승인 조건에 적용할지**를 명시하고,
[검증 owner](../../30-validation/s11-physical-interface-evidence-repair-validation.md#required-two-sided-controls)에 따라
최종 선택·episode·극값 비교까지 갈 수 있는 진입 조건을 정하는 것이다.
단순히 또 다른 점수표를 만드는 작업으로 확대하지 않는다.

새 비교에 진입하려면 실제 계면 보존과 비유면의 잘못된 소유권 억제를 함께
설명해야 한다. 100% 후보 일치가 아니라 검토된 움직임·불확실성이 유지되는지,
같은 프레임 candidate→sequence→CSV 값이 일치하는지 평가한다.
약한 관측을 전부 제거하거나 결과 그래프를 보간해 매끈하게 만들지 않는다.
CRW-1의 지지 개수만으로 authority를 승격하거나 hard gate를 추가하지 않는다.

닫힌 seed-anchor/두-native 조건, cost-first/RGB/Local XY/학습 실험은 반복하지
않는다. Sample3 격리와 review-006 미검토를 유지한다. 지금 새 Windows 실행,
CSV 추출, 이미지 전달은 요청하지 않는다. 실제 필요해진 Windows/사람 판단은
그때 필요한 최소 범위로 분리한다. FULL 상단 계약과 독립 Foam 경로, 실제
report 판독은 이 입력 실험의 완료로 닫히지 않는다.

직접 시각 확인은 저장된 f1140/f1275/f1485 ROI 3장, 수치 실행은 8개 raster다.
모든 영상을 처음부터 끝까지 재생한 것은 아니다. 그 밖의 Mac/public 자료와
Windows 결과는 current owner 및 연결된 기존 검토 기록을 재사용했다.
격리 Windows 원본 영상·이미지를 Mac으로 반출하지 않았다.

## 재현·보존 위치

코드는 `tests/diagnostics/s11_raster_partition_screen.py`, 별도 직접 픽셀 검산기는
`tests/diagnostics/s11_raster_partition_verify.py`이며, 테스트는
`tests/unit/test_s11_raster_partition_screen.py`다. 원본 raster·visibility 입력이
필요하므로 GitHub source ZIP만으로 모든 입력이 복구되는 것은 아니다.

관리 실행 `sample/output/s11-raster-partition-20261016-001/`은 종료 처리했다.
보존 파일은 `evidence/readout.json.gz`와 `evidence/verification.json` 두 개다.
전체 readout은 371,355 bytes이며 SHA-256은
`5458e62d198a821056996fabe736b9510d4b699571cd5497f88006c67a4723fc`다.
대용량 자료를 Git에 복사하지 않았고, 요약 JSON은 전체 분모·검산 결과·코드
hash를 보존한다. 기존 원본·frozen 증거는 변경하지 않았다.
관리 검사에서 **85개 run / 오류 0건**을 확인했다.

재현이 실제로 필요할 때는 [산출물 관리 절차](../../40-operations/experiment-artifact-lifecycle.md)에
따라 새 managed run을 만들고, 그 `work/` 경로를 `WORK`로 지정한다.
아래 명령은 닫힌 실행을 덮어쓰거나 새 Windows 실행을 요청하는 것이 아니다.

```sh
.venv/bin/python -m tests.diagnostics.s11_raster_partition_screen \
  --output "$WORK/readout.json.gz"
.venv/bin/python -m tests.diagnostics.s11_raster_partition_verify \
  --readout "$WORK/readout.json.gz" --output "$WORK/verification.json"
```

```sh
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_raster_partition_screen.py \
  tests/unit/test_s11_corroboration_geometry_screen.py \
  tests/unit/test_s11_corroboration_peer_screen.py \
  tests/unit/test_oil_interface_diagnostics.py \
  tests/unit/test_oil_interface_witness.py \
  tests/unit/test_oil_measurement_lineage.py
```

## 종료 검사

문서 정리 후 같은 123개 테스트를 재검증해 **123 passed / 0 failed, 7.61초**를
확인했다. 앞의 7.17초는 실행 전 고정된 동일 코드의 최초 관련 검증 기록이다.
추가·변경 상대 링크/anchor **22개 / 오류 0건**, governance 및
`git diff --check` 통과를 확인했다. 측정기·검산기·테스트의 고정 source hash는
불변이며, 시작 HEAD 대비 제품 `src/`와 Recipe 변경은 없다.

## 재개용 프롬프트

```text
Oil Level Tracker S11을 이어가자. work-plan과
2026-10-16-raster-partition-handoff.md를 먼저 읽어줘.
CRW-1은 원본 raster의 경계·분할 측정을 구현·검증했지만 단독 물리 판별은
미검증이야. 허용 7/8 프레임의 부분적 유용성과 모든 미검토/실용적 허용을
보존하고, f1200의 역순 지지수와 f1320 동률을 임계값 튜닝으로 해결하지 마.
입력 audit를 반복하지 말고, 물리적 역할 근거를 어느 consumer에 적용할지와
최종 선택·episode·거짓 극값 비교까지의 진입 조건을 구체화해줘.
목표는 100% 후보 일치가 아니라 report로 실제 움직임 맥락을 이해하는 거야.
닫힌 Windows 비교·모델·CSV 추출은 재개하지 말고, FULL·Foam·실제 보고서
판독의 미완료 경계를 유지해줘. 작업 결과와 인수인계를 함께 마무리해줘.
```

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: the transferred 721 s false material anchor is known; its raw peer/optical cause is not. CRW-1 measures local input and exposes count-only role ambiguity before authority, without explaining private Windows causality.
- Existing feature coverage: frozen sample4/public current pixels, effective/glare visibility, O1 sectors and original candidate bindings are reused. Recipe, Artifact/static setup and comparison switches retain their saved scopes. No model, static learning, Local XY, initial-FULL or completed resolver is executed by this diagnostic entry.
- Execution scope: one frozen 187-unit screen, 175 actual Oil observations, 85 directed peer relations, direct-loop arithmetic and 123 focused tests. Original labels/kinds/Y are preserved. No production consumer, qualified continuous contour, final Oil/Foam output, Windows replay or independent report reading is claimed.
- Logic-map impact: NONE — input diagnostic and handoff only; production defaults, owners and publication remain unchanged.
- Failure-registry impact: NONE — existing identity/provenance/threshold-shortcut risks cover the result; no field repair or new failure class is asserted.
