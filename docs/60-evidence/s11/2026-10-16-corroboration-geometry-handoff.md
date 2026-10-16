# S11 인수인계 — native 경로·원본 측정 검증 / 2026-10-16

## 현재 결론

**이번 로컬 가설 검증과 인수인계는 완료했다. 검출 성능 개선이나 S11 완료를
입증한 것은 아니다. Production detector·Recipe·모델·정답은 변경하지 않았다.**
현재 상태는 **S11 ACTIVE / O2 OPEN / FIELD FAIL**이며,
[Work Plan](../../00-project/work-plan.md)이 상태·권한·다음 전환을 소유한다.

시작 기준은 `7f121997aa2bb5c12818326f66d44555145cf807`이다.
검증기·38개 신규 테스트·가설은 실행 전에
`7ee6d909781a2053782b1fab17e0f60d251e2d71`로 고정했다.
이 문서는 그 실행 결과를 인계한다. 최종 문서 게시 커밋은 Git 이력으로 확인한다.

## 실제로 새로 검증한 것

[직전 peer screen](../../50-diagnostics/s11/2026-10-16-corroboration-peer-screen.md)의
기존 점수와 전체 후보를 재사용했다. 실패한 seed-anchor 조건을 다시 시험하거나
임계값을 조정하지 않았다. 새 가설은 **지지하는 두 후보에 실제 native 경로가
모두 있는가, 원본 영상의 양측 영역 측정은 재현되는가**였다.

| 항목 | 결과 | 판단 범위 |
|---|---|---|
| 입력 | sample4 7프레임 + 공개 압축기 f1499, 총 187개 | 실제 Oil 175 / Foam 8 / 문맥 4. 과거 타입·라벨 유지 |
| Native 경로 | Oil 175개 중 35개. 허용 11개 중 4개 | 경로 가용성이지 검출률·정확도가 아님 |
| 기존 지지 관계 | 방향을 가진 85쌍 중 양쪽 native 경로가 있는 쌍 0개 | 공통 native 윤곽 비교 G2는 **평가 불가** |
| 원본 재계산 | 4,136개 밴드 참조, 고유 창 2,867개, 불일치 0 | 회색조 유효 픽셀 수·평균·표준편차의 산술 검증 |
| 최대 수치 차이 | 2.7721516911195994e-08, 허용 오차 1e-7 | 물리 판별 임계값이 아닌 부동소수점 재현 오차 |
| 관련 테스트 | **92 passed / 0 failed**, pytest 5.67초 | 신규 38개 + 기존 측정·witness·lineage·peer 검사 |

허용된 f1140 material idx9에는 native 경로가 있지만 지지 peer idx4에는 없다.
검토된 rim material idx10에는 경로가 있지만 peer idx7·idx22에는 없다.
따라서 **윤곽을 비교했더니 rim 구별에 실패했다는 결과가 아니다. 두 경로를
비교할 입력 자체가 없었다.** 입력 부재를 물리적 비계면·영상 불가시로 바꾸지 않는다.

기존 생성기는 material 계열에서 실제 sector 경로를 보존하고, 일반·calibrated
후보의 이 지지 관계에는 그 경로가 없다. 현재 지지 계산은 서로 다른 후보 계열의
Y 근접성과 스칼라 근거를 사용한다. native 윤곽의 물리적 일치를 확인하는 함수가 아니다.
상세 source 경로와 전체 결과는 [진단 기록](../../50-diagnostics/s11/2026-10-16-corroboration-geometry-screen.md)에 있다.

**현재 데이터에 두 native 경로 필수 조건을 추가하지 않는다.** 이 표본의 기존
양의 지지가 전부 사라져 실제 계면의 지지도 잃는다. 최종 detector를 다시 실행한
것은 아니므로 이를 ‘최종 Oil 11개 소실’로 표현해서도 안 된다.

## 보고서의 움직임 맥락을 기준으로 한 판단

[Windows 수신 체크포인트](2026-10-16-windows-comparison-checkpoint.md)의 기존 비교는
재실행하지 않았다. ④ initial-FULL v2는 BASE 수치 출력이 185→303행으로 늘었지만
721초 비유면 Y694도 노출했다. ⑤ cost-first는 BASE 회복 구간을 잃었고,
⑥ RGB는 BASE 출력을 전부 잃었다. ⑦ Local XY는 비유면 대체 출력과 허용된 Accum
계면 소실이 있어 모두 미채택이다. 일부 누락을 없애거나 오출력 수를 줄였다는
이유만으로 실제 움직임 전체를 지운 후보를 승격하지 않는다.

작은 누락·흔들림보다 **거짓 극값·방향 반전, 오래 유지되는 잘못된 계면,
실제 회복/Foam episode 전체 소실**을 우선한다. 이번 산술 검증은 이러한
보고서 문제의 해결을 입증하지 않는다. 실제 독립 report-only 판독도 아직 없다.

Windows 원본은 격리 PC에 있으며 Mac으로 반출하지 않았다. 이번 직접 실행은
8개 저장 프레임의 입력·밴드 검증이다. 모든 원본 영상을 처음부터 끝까지 재생하거나
모든 Windows 구간을 새로 분석한 것이 아니다. 나머지는 현재 owner와 수신 근거로 검토했다.

## 다음 담당자가 이어갈 지점

첫 단계는 임계값 추가가 아니라 **약한 실제 계면과 rim 모두에 대해 현재 픽셀에서
대응하는 윤곽·양측 영역·측정 계보를 확보하는 구체적 설계**다. 기존 generator
native 경로, 별도로 재관측한 윤곽 가설, 단순 candidate-center 밴드를 구분한다.
중앙 Y나 가까운 peak를 원래 후보의 native 경로로 둔갑시키지 않는다. 재관측 경로는
새 측정이며 물리적 역할·localization 검증이 필요하다. 현재 판별기나 operating
point가 선정된 것은 아니다. [설계 owner](../../20-architecture/s11-physical-interface-evidence-repair-design.md#independent-corroboration)와
[양면 대조 조건](../../30-validation/s11-physical-interface-evidence-repair-validation.md#required-two-sided-controls)에 이 입력 공백을 반영했다.

후속안은 review-004/005의 복수 허용·불확실성을 보존하고, 실제 움직임을 지우지
않으면서 검토된 비유면을 구별해야 한다. 723초 material veto·771초 identity 보호,
Oil/Foam 독립성과 동일 프레임 candidate→sequence→CSV 일치는 계속 필요하다.
당장 새 Windows 실행·추출·이미지 검토를 요청하지 않는다. 닫힌 세 비교, P2 seed
가설, 모델 학습·복원·튜닝을 재개하지 않는다. Sample3와 review-006의 상태도 유지한다.

FULL은 별도 미해결이다. 기존 상단 preflight의 물리 endpoint Y220.870,
mask top Y243, 마지막 선택 Y352로는 상단 도달을 증명하지 못해 ⑧은 실행되지 않았다.
mask edge를 FULL로 바꾸거나 margin을 줄여 통과시키지 않는다. 상단 관측 계약과
실제 전환·유지 검증이 남아 있다. Foam의 raw proposal 부재, 역할 구분, episode
유지는 서로 다른 과제이며 Oil의 지지 조건으로 해결됐다고 할 수 없다.

최종 인수는 [정식 Windows 9개 구간](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#reviewed-timeline)과
실제 report-only 판독으로 해야 한다. BASE 하강 550–652초, 회복 652–674초,
FULL 전환 674–675초라는 정정 기록을 유지한다. 663.6초 경계를 다시 쓰지 않는다.

## 재현·산출물·검증

코드: `tests/diagnostics/s11_corroboration_geometry_screen.py`.
[readout.json.gz](../../50-diagnostics/s11/2026-10-16-corroboration-geometry-screen/readout.json.gz)는 전체 후보·지지 관계,
[verification.json](../../50-diagnostics/s11/2026-10-16-corroboration-geometry-screen/verification.json)은 실행 head·명령·결과를 보존한다.

```sh
.venv/bin/python -m tests.diagnostics.s11_corroboration_geometry_screen \
  --output /tmp/s11-corroboration-geometry-readout.json.gz
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_corroboration_geometry_screen.py \
  tests/unit/test_s11_corroboration_peer_screen.py \
  tests/unit/test_oil_interface_diagnostics.py \
  tests/unit/test_oil_interface_witness.py \
  tests/unit/test_oil_measurement_lineage.py
```

재현에는 Mac에 보존된 A1 capture·visibility 입력이 필요하다. GitHub source ZIP만으로
전 입력을 복구할 수 있는 것은 아니다. 새 영구 연구 출력은 관리 실행으로 생성한다.
이번 관리 실행은 `sample/output/s11-corroboration-geometry-20261016-001/`이며
종료 처리했다. 결과 2개 파일 20,514 bytes를 보존하고 불필요한 테스트 log·임시
plan/selection은 제거했다. 기존 원본·frozen 증거는 변경하지 않았다.
관리 검사에서 84개 run / 오류 0건, governance 통과, 추가·변경 상대 링크
23개 / 오류 0건, `git diff --check` 통과를 확인했다. 원격 게시와 최종 head는
Git 이력으로 확인하며, 공개 응답의 완료 커밋은 게시 확인 후 기록한다.

## 재개용 프롬프트

```text
Oil Level Tracker S11을 이어가자. work-plan과
2026-10-16-corroboration-geometry-handoff.md를 먼저 읽어줘.
85개 기존 지지 쌍에 양쪽 native 경로가 없어 공통 윤곽 비교는 평가 불가였고,
원본 gray band 산술은 재현됐어. 두 native 경로 필수 gate부터 추가하지 마.
약한 실제 계면·복수 허용 후보를 보존할 현재-raster 윤곽/양측 영역/계보 설계를
구체화하고, 입력·물리 역할 검증 후에만 authority 변경을 판단해줘.
닫힌 Windows 비교·CSV 추출·모델 학습은 반복하지 말고, FULL·Foam·실제 report
판독의 미완료 경계를 유지해줘. 결과와 인수인계를 함께 마무리해줘.
```

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: the transferred Windows 721 s false material anchor is known; its actual raw peer/optical cause remains unknown. The new local screen finds missing native peer geometry before any physical corroboration consumer.
- Existing feature coverage: frozen sample4/public current candidates, masks, original pixels, O1 native/center measurements and exact source identities are reused. No Recipe, Artifact/static setup, comparison switch, model or truth changes; original kind disagreements and practical alternatives remain.
- Execution scope: 187 units, 85 directed support relations, 4,136 band references and 92 local tests; no two-native physical comparison, completed detector replay, private Windows execution or independent report reading. Handoff and existing design/validation owners are updated.
- Logic-map impact: NONE — diagnostic and handoff only; production consumers, ownership, defaults and publication remain unchanged.
- Failure-registry impact: NONE — existing identity/provenance/shortcut failures cover this unavailable-input boundary; no physical repair or field success is claimed.
