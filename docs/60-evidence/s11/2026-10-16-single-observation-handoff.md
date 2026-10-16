# S11 SOI-1 인수인계 — 단발 누락이 움직임 맥락에 미치는 영향

## 결론

**세 차례 검증·여섯 가설의 실행과 증거 보존을 완료했다. 제품 detector 변경은 채택하지 않았다.**
S11은 ACTIVE, O2는 OPEN, Windows FIELD FAIL 상태를 유지한다. 검출률 100%가 목표가 아니다.
단발 누락이 국소적으로 끝나는 경우와, 그 누락이 긴 관측 구간·극값·Foam 구간 구성을
바꾸는 경우를 구분했다. 이전 PWC/RCI의 한계는 유지하며 같은 픽셀 모델을 다시 조정하지 않았다.

핵심은 **누락 하나를 없애는 것보다 누락 이후의 잘못된 이력·상태 전환 확대를 막는 것**이다.
다만 이번 반사실 실험은 안전하게 배포할 수정안이 아니다. 원래 추적 이력을 고정하거나
원래 후보 목록을 정답처럼 사용하는 방법은 실제 누락 상황에 적용할 수 없다.

## 범위와 실행 기준점

작업 시작: `74c05b8eaca2802f29dc84f2eb2705d7c63fc260`, clean main.
실험 소스 고정 커밋은 다음과 같다. 최종 문서·검증기 커밋과 혼동하지 않는다.

| 단계 | 고정 커밋 | 실행 |
|---|---|---|
| H1–H3 전수 단발 누락 | `e00dffb1a912320ac4fe8e6affd81514d48f95b6` | 245개 개입 + 기준 1개 |
| H4–H5 단계 분리 | `30b1feaf99fa5b39d42cc147f2b831f507cd6e1d` | 원본 재현 4개 + 최종 Foam 31개 + 추적 이후 Oil 2개 |
| H6 대체 후보 유입 분리 | `bdcad30f1d343ceb9adaaa04a8e0e8b2272ed4d1` | 대조군 포함 4개 |

Mac sample4의 동일한 0–56초, 2 Hz, 113개 분석 시점과 저장된 raw 후보·Recipe를 사용했다.
합계 287개 completed-window 기록 / 32,431행이며, 반복 기준 실행을 포함한다.
287개 독립 영상이나 물리 정확도 시험이 아니다. 실제 resolver, sample, event,
report presentation을 실행했고 대표 조건에는 실제 CSV와 그래프를 생성했다.

## 검증 결과

| 가설 | 결과 | 판정 |
|---|---|---|
| H1 선택된 Oil 후보 하나의 누락은 대체로 국소적이다 | 101개 중 84개는 다른 시점 Oil 수치 불변. 그러나 42.5초 후보 하나를 제거하면 44–56초의 25개 분석 시점에서 Oil 출력이 모두 사라짐 | 대부분의 국소 누락과 큰 맥락 소실을 분리해야 함 |
| H2 한 시점 Oil 후보 전체 소실도 같은 영향이다 | 113개 중 69개는 다른 시점 Oil 수치 불변. 44초 소실 대표 조건은 수치 출력이 101→104개로 늘지만 극값은 +28/−18→+45/−32 px로 바뀜 | 검출 개수 증가를 개선으로 해석하면 안 됨; 새 극값의 물리적 타당성은 미검토 |
| H3 Foam 입력 소실은 Oil에 영향을 주지 않는다 | 31개 중 10개가 다른 시점 Oil 수치를 변경. 40초 조건은 Oil 100개·Foam 22개, report Foam 구간 1→2개 | 원시 Foam material/alias 문맥이 Oil 이력에 영향을 주는 경로 확인 |
| H4 최종 Foam 소비 단계만 바꾸어 원인을 분리한다 | 31개 모두 Oil 수치 불변. Foam은 25개 조건에서 다른 시점 수치 불변, 6개 조건은 구간 분할. 40초 조건은 해당 점만 빠지고 원래 1개 구간 유지 | 초기 material 문맥 영향과 최종 episode 영향을 구분; 최종 단계도 항상 국소적이라는 주장은 불가 |
| H5 추적 뒤에 동일 후보를 제거해 이력 재구성 영향을 분리한다 | 대표 2개 모두 개입 시점 Oil만 누락, 다른 시점 수치 불변 | 이력 재구성 경로의 영향 확인. 사라진 관측으로 만든 원래 이력을 썼으므로 배포 해법이 아님 |
| H6 새로 들어온 Y818 후보가 긴 소실의 필수 원인이다 | 그 후보만 제외하고 이력을 새로 계산해도 44–56초 소실 유지. Oil/Foam 수치와 CSV·event·그래프가 원래 소실 조건과 동일 | 이 사례의 필수 원인 가설 기각. 해당 Y/source 예외 처리로 접근하지 말 것 |

42.5초 개입은 f1275/idx12/calibrated_high_recall/Y835의 검토된 Oil 대응 후보다.
이후 내부 phase가 44초 `FILL_SPAN_MATERIAL_VETO`, 다음 시점부터 `FILLED_CAP_VETO`로
전환한다. **내부 filled barrier를 실제 FULL 관측으로 해석하지 않는다.**
이때 52초의 기존 양성 관측도 함께 소실한다. 주입한 한 점의 누락 자체가 아니라 이 파급을 본다.
재귀적 정지 구조 패널티, 추적 연결·확정, phase 차단 중 유일한 원인까지 분리한 것은 아니다.
새 Y818 후보의 필요성은 배제했지만, 적합한 이력·상태 책임 분리는 아직 설계가 필요하다.

기준 출력 역시 물리적 정답이 아니다. 한두 점 변경·누락이나 작은 시간 차이를 새 탈락 기준으로
만들지 않는다. 명확한 상승·하강·Foam 동반 구간의 맥락이 유지되는지를 우선한다.

## 기존 증거의 적용 범위

Mac 원본에서 만든 sample4의 113개 시점 아틀라스 4장과 실제 대표 report 그래프 4개를
재검토했다. 원본 재디코딩·새 픽셀 측정·새 물리 라벨링을 수행한 것은 아니다.
다른 Mac/public 소스의 기존 역할 판정과 실패 메커니즘은 설계 제약으로 재사용한다.
Sample3는 기존 격리 범위를 유지한다. 모든 영상에 대한 새로운 전수 재처리 결과로 확대하지 않는다.

Windows는 [비교 체크포인트](2026-10-16-windows-comparison-checkpoint.md)와
[기준 검토 구간](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)을
재사용했다. 실제 영상의 신규 실행이나 새 현장 검증은 없다. ④ 이후 세 비교의 회귀,
721초 조사 완료/물리 원인 미상, 9개 canonical 구간, review-004/005의 실용적 허용을 보존한다.
review-006은 미검토다. **FULL은 미완료, ⑧은 조건 실패로 NOT RUN**이며 상단 mask 경계를
실제 유리 상단으로 바꾸거나 margin을 줄이지 않는다. 새 Windows 실행 요청은 없다.

## 정합성 검증

| 범위 | 검산 |
|---|---|
| 1차 | 27,798행, Oil 원후보 결합 24,672건, Foam 동일 시점 후보 대응 6,343건, event 결합 7,135건, CSV 전체 필드 452행 |
| 2차 | 4,181행, event 1,103건, 단계별 원후보 결합 38,607건, CSV 전체 필드 339행 |
| 3차 | 452행, event 118건, 승인 후보 결합 7,346건, CSV 시점·좌표 113행 |

각 독립 검산의 불일치는 0건이다. 숫자·출처 정합성이지 물리 정확도나 독립 사용자 이해도 평가가 아니다.
최초 verifier는 ANALYSIS_END의 의도적인 좌표 없음에 잘못 실패했다. 실패 기록을 남기고,
시작/종료 event는 좌표가 없어야 하며 나머지는 smoothed sample과 누락 여부까지 같아야 하는
타입별 계약으로 정정했다. 실제 실험 출력은 수정하지 않았다.
보존 후 alias-aware 검산도 통과했다. 과거 검산 기록은 원래 verifier hash를 보존하고,
현재 재검산 hash와 동일한 측정 결과는 [요약](../../50-diagnostics/s11/2026-10-16-single-observation-influence/summary.json)에 따로 기록한다.

## 파일과 재현

아래 경로는 repository 기준이다. `sample/output`은 Git 제외 로컬 자료이며 GitHub 백업이나
Windows 전달 완료를 뜻하지 않는다. 원본·중간 모델·전체 checkout을 복제하지 않았다.

- 설계와 상세 결론: `docs/50-diagnostics/s11/2026-10-16-single-observation-influence.md`
- 간결한 수치·hash·검산 요약: 같은 이름의 하위 폴더 `summary.json`
- 1차: `sample/output/s11-single-observation-20261016-001/evidence/`
- 2차: `sample/output/s11-single-observation-causality-20261016-001/evidence/`
- 3차: `sample/output/s11-single-observation-backfill-20261016-001/evidence/`

세 실행 모두 관리 종료됐다. 각각 26/16/5개 파일, 합계 8,949,047 bytes를 보존했다.
기존 자료와 동일한 baseline 그래프 1개 및 H6의 CSV·그래프 4개는 hash alias로 재사용한다.
최초 실패 기록은 보존했고, 중복·대체된 임시 파일 6개만 제거했다. 전체 관리 실행 91개 점검에서 오류가 없다.

전수 재실행보다 저장된 산출물 검산을 먼저 사용한다. 저장소 루트에서 다음 함수를 호출한다.

```python
from pathlib import Path
from tests.diagnostics.s11_single_observation_verify import verify
from tests.diagnostics.s11_single_observation_causal_verify import verify as verify_stage, verify_backfill
root = Path.cwd()
p1 = root / 'sample/output/s11-single-observation-20261016-001/evidence'
p2 = root / 'sample/output/s11-single-observation-causality-20261016-001/evidence'
p3 = root / 'sample/output/s11-single-observation-backfill-20261016-001/evidence'
print(verify(root, p1)); print(verify_stage(root, p2, p1)); print(verify_backfill(root, p3, p1))
```

새 실행이 필요한 경우 각 실행기의 frozen source와 원래 raw/Recipe pins를 먼저 확인한다.
`experiment_artifacts.py start`로 새 경로와 예산을 만든 후 `work/`를 다음 모듈에 전달한다.
기존 `evidence/`를 출력 경로로 사용하거나 closed run을 덮어쓰지 않는다.

```text
python -m tests.diagnostics.s11_single_observation_influence --output <new-primary>/work
python -m tests.diagnostics.s11_single_observation_causality --parent <primary>/evidence --output <new-stage>/work
python -m tests.diagnostics.s11_single_observation_backfill --parent <primary>/evidence --output <new-backfill>/work
```

실행은 저장소 `.venv/bin/python`, 그래프는 `QT_QPA_PLATFORM=offscreen`을 사용한다.
새 출력도 가치 검토 후 명시한 자료만 보존하고 managed finish/check로 닫는다.
최종 focused 회귀검사는 7개 파일의 **226 passed**다. 전체 테스트 suite나 현장 PASS 주장이 아니다.

## 다음 작업자에게

현재 action owner는 [Work Plan](../../00-project/work-plan.md)이다. 우선순위는 관측 누락이
승인·확정 이력과 material phase 차단으로 확대되는 책임 경계를 좁히는 것이다.
기존 물리적 boundary/side-role 관측 필요성은 사라지지 않았다. 재평가 패널티와 연결·확정 중
첫 결정적 분기는 아직 미분리이며, 안전한 제품 수정안을 이번 결과만으로 선택하지 않는다.

실제 수정은 현재 시점의 검증 가능한 관측으로 책임져야 한다. 과거 Y 유지, 보간, 원래 이력
고정, 기준 후보 목록을 이용한 oracle, 일괄 anchor 승격이나 상태 gate 해제로 해결하지 않는다.
52초 같은 확인된 후속 관측의 소실 방지와 실제 FULL/EMPTY에서의 오출력 억제를 함께 검증한다.
Foam도 early material 문맥과 final episode를 구분하며, 모든 짧은 gap을 막기 위한 threshold
탐색으로 확대하지 않는다. 새 픽셀 모델·Y818 예외·Windows 재실행을 자동으로 시작하지 않는다.
제품 수정이 준비되면 동일한 장구간 맥락과 실제 report 산출물 기준으로 평가하고,
그 다음 O2 사용자 해석과 필요한 현장 qualification을 진행한다. 현재 어느 것도 완료로 표시하지 않는다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `CSV-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: selected eligibility loss changes admission/history and then internal phase gating; raw Foam changes same-frame Oil admission. Exact physical error origin and the decisive recurrence/association substage remain unknown. A renderer repair is not established.
- Existing feature coverage: original sample4 Recipe, UNKNOWN initial state, ellipse/margin 0.08 and zero user exclusions/templates; unchanged raw preprocessing/artifact/state evidence. All optional comparisons stay OFF. No extraction, fit or new truth.
- Execution scope: exhaustive raw eligibility withdrawals; final-Foam and frozen-track-history interventions; admission-backfill ablation with fresh downstream history; full resolver/sample/event/presentation and representative actual CSV/graphs, original source atlases and independent saved-output checks. No private Windows rerun, physical full-window accuracy or independent human comprehension.
- Logic-map impact: NONE — no production code/default, responsibility or call route changed.
- Failure-registry impact: UPDATED — F05/F06 gain local evidence pointers only; existing classes, safety contracts and field dispositions remain unchanged.
