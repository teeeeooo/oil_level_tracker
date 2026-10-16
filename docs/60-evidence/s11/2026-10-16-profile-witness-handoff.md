# S11 PWC-1 — 픽셀 가설 반복 검증 및 인수인계

## 결론

**두 가설·여섯 개 개입 조건을 실제 완료 sequence와 report 산출까지 검증했고,
이번 후보는 제품에 채택하지 않는다.** 일부 누락 때문이 아니다. 후반 Oil
움직임을 통째로 잃거나, 검증되지 않은 큰 하강·회복과 극값을 새로 만들고,
Foam 관측 구간을 분리하는 문제가 확인됐다. 기본 detector 동작은 그대로다.

작업 시작 HEAD는 `b5f93ecf9fc55b6473e105e8234b9d741f72a23e`이다.
가설·실행기·독립 검산기·단위 테스트를 실제 실행 전에
`9c77abae2b1f2165a7dc70ba067e85ceb75949bc`에 고정했다.
한 고정 실행에서 기준선과 6개 조건을 모두 처리했다. 결과를 보고
창 크기·임계값·모델 차수를 바꾼 재시도는 하지 않았다.

현행 상태는 [Work Plan](../../00-project/work-plan.md)이 소유한다.
이 기록은 실행 당시의 증거이며 S11/O2/Windows 인수를 대신하지 않는다.
[고정 설계와 결과](../../50-diagnostics/s11/2026-10-16-profile-witness-consumer.md),
[기계 요약](../../50-diagnostics/s11/2026-10-16-profile-witness-consumer/summary.json)을 함께 읽는다.

## 실제 확인·실행 범위

Mac `sample4.mp4`의 0–56초, 2 Hz, **113개 전체 표본 프레임**을 원본에서
다시 읽고 2,549개 Oil 후보를 측정했다. 별도 희소 검토 집합은 sample4
7개 프레임의 153개 후보와 public 1개 프레임의 22개 후보, 합계 175개다.
이는 8개 독립 영상이 아니다. 원본 영상 전체 프레임을 detector로 새로
추출한 것도 아니다. 기존 후보 추출 결과를 고정하고 새 픽셀 관측과
완료 Oil/Foam resolver, events, CSV, 실제 graph/report-presentation을 실행했다.
기존 7개 sample4 raster/mask와 새 입력이 모두 정확히 같음을 확인했다.

Windows는 [완료 비교 기록](2026-10-16-windows-comparison-checkpoint.md)의
④–⑧, 721/723/771초 제약, review-004/005/007/008의 범위를 재사용했다.
④의 BASE 수치 증가 185→303/601과 721초 오선택은 함께 유지한다.
⑤–⑦의 회귀와 ⑧의 endpoint preflight 실패를 새 성공으로 바꾸지 않았다.
Windows 비공개 원본 영상·이미지의 새 실행이나 추가 추출은 하지 않았다.
Sample3의 전체 구간 물리 판정 격리와 review-006 미검토도 그대로다.

## 두 가설과 여섯 조건

H1은 경계 양측이 공통 기울기를 가진 채 밝기가 불연속적으로 달라지는
모델이다. H2는 양측의 기울기도 각각 허용한다. 두 모델 모두 연속적인
밝기 변화와 꺾임 모델을 대조군으로 삼았다. 홀수·짝수 원본 행을
서로 나눠 예측 오차를 검증했고, 원래 후보 Y를 이동시키지 않았다.
사람의 정답은 영상 계산이나 개입 결정에 사용하지 않았다.

각 모델에서 부정 선호 후보의 정확한 member 제외, 긍정 선호 후보의
authority 승격, 둘의 결합을 별도로 시험했다. HARD_INVALID는 승격하지
않고 기존 material/phase/history/association/Foam 조건을 그대로 통과시켰다.
픽셀 모델의 선호가 물리적 Oil 역할과 같다는 전제는 검증 대상이지 사실이 아니다.

| 조건 | Oil 수치 / 유효 | Foam 수치 / 유효 | 원래 유용한 물리 대조 3개 보존 | 최종 선택된 기존 반대 대조 |
|---|---:|---:|---:|---:|
| 기준선 | 101 / 101 | 26 / 26 | 3 | 3 |
| H1 부정 후보 제외 | 71 / 71 | 26 / 26 | 0 | 0 |
| H1 긍정 권한 부여 | 85 / 85 | 25 / 25 | 1 | 0 |
| H1 결합 | 103 / 102 | 26 / 25 | 2 | 0 |
| H2 부정 후보 제외 | 101 / 101 | 26 / 26 | 3 | 3 |
| H2 긍정 권한 부여 | 86 / 84 | 23 / 21 | 1 | 0 |
| H2 결합 | 86 / 84 | 23 / 21 | 1 | 0 |

모든 조건의 분모는 같은 113개 표본이다. 마지막 열의 0은 전체 오검출 0이
아니다. 새로 선택된 미검토 후보를 정답으로 세지 않았다. 원래 유용한
대조는 38/42.5/52초이며 이 세 점을 모두 맞혀야 한다는 제품 규칙도 아니다.

**H1 결합의 부분적 성과와 거부 이유.** 38/52초를 보존하고 44초의 검토된
계면을 회복했다. 하지만 42.5초를 잃고 선택 후보가 54행에서 바뀌었다.
기존 잘못된 42/44초 극값 대신 39초/Y821 최고점과 47.5초/Y881 최저점이
생겼다. 둘 다 미검토이며, 실제 그래프에는 47.5–51초의 큰 하강·정체·회복이
나타난다. 원본과 대조해 이 움직임을 올바른 물리 변화로 인정할 근거를
확보하지 못했다. 수치 101→103만으로 개선이라고 결론 내릴 수 없다.

**H1 단독 조건의 문제.** 부정 제외만 적용하면 36–56초 Oil이 모두 사라지고,
긍정 권한만 적용하면 44–56초가 사라진다. 몇 개의 누락이 아니라 후반
움직임 맥락의 상실이다.

**H2의 문제.** 입력에서 허용 후보 11개를 모두 긍정 평가했지만 반대 후보
7개도 전부 긍정 평가했다. 긍정/결합 조건의 최종 결과는 46–56초 Oil을
잃고, report의 주요 Foam 구간이 1회에서 2회로 분리된다. 유효 Foam도
26→21이다. 입력 긍정률이 높다는 사실은 사용자 맥락 보존을 보장하지 않는다.

H1의 public 실용 근사 후보 두 개 누락이나 0.5초 Foam 변화 자체를
실패 이유로 삼지 않았다. 핵심은 새 극값·장기 공백·후반 움직임·Foam
구간 구성이다. 실제 독립 사용자의 report-only 판독은 실시하지 않았다.

## 검증 결과

고정 전 관련 테스트 85개, 수치 실행 후 관련 회귀 테스트 **208개 통과**.
보존 검산기 보완까지 포함한 최종 결과는 아래의 **213개 통과**다.
직접 픽셀 합과 별도 normal-equation 계산으로 2,164,608개 픽셀 참조와
6,234개 profile을 검산했다. 공개된 결과는 791개 CSV행, 633개 같은 프레임
Oil 후보→sequence→CSV 연결, 17,843개 authority 호출, 200개 domain event,
14개 극값을 별도 검산했으며 불일치는 0이다. 원래 113행 전체 baseline도 같다.

이 검증은 계산·연결·개입 범위의 검증이며 물리 검출 정확도나 report 인수
통과가 아니다. 113개 원본 표본의 atlas 4장과 baseline/H1/H2 실제 그래프를
대조했다. 재사용 atlas의 캡션은 이전 RCI 실험 것이므로 PWC 결과로 해석하지
않는다. 새 물리 truth나 전체 tracklet 역할은 추가하지 않았다.
첫 회귀 실행의 pytest는 208개 통과했지만 shell이 예약 변수 `status` 대입에서
종료 코드 1을 냈다. 이름을 바꾼 wrapper로 같은 검사를 다시 실행해 코드 0과
208개 통과를 확인했다. 알고리즘 실패나 수치 재시도와 구분한다.

## 인수인계 파일과 재현

Git에는 설계·결과·기계 요약·실행기·독립 검산기·테스트를 남긴다.
대용량 native 증거는 다음 로컬 관리 경로에 둔다.

`sample/output/s11-profile-witness-20261016-001/evidence/`

`measurements.json.gz`는 전체 후보의 동일-support 픽셀 profile/fold/계수를,
`readout.json.gz`는 일곱 조건의 모든 member/authority/owner/최종 선택을,
`comparison.json`은 대조군·변경·events/report-presentation을 담는다.
`verification.json`, `verification-storage.json`, `tests-retention.log`, 각 조건의 CSV와 detail 그래프,
`review.html`이 검산과 시각 비교 진입점이다. 이 로컬 자료는 Git 원격 백업이
아니며, 정확한 경로와 SHA-256은 기계 요약 및 관리 retention 기록을 따른다.

원본/현재 생산 소스 hash가 맞는 checkout에서 재검산할 때는 새 실험을
만들지 않고 다음처럼 읽기 검사를 실행할 수 있다. 바뀐 입력을 재분류하지 않는다.

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
from tests.diagnostics.s11_profile_role_verify import verify
root = Path.cwd()
print(verify(root, root/'sample/output/s11-profile-witness-20261016-001/evidence'))
PY
```

## 다음 작업의 경계

후속 구현에 채택할 자동 판별기는 없다. RCI의 검토 역할 개입에서 보인
가능성과 이번 픽셀 모델의 실제 실패를 함께 사용한다. 다음 설계는 원래
경계와 양측의 역할을 같은 관측에 묶는 **다른 종류의 증거**를 먼저 제시하고,
정확한 후보 member·authority·history/owner 소비가 왜 함께 유효한지 설명해야
한다. profile 창/차수/임계값 조정이나 점수 선호를 곧바로 anchor로 만드는
추가 실험은 이 결과의 후속 작업으로 제안하지 않는다.

제품 종료 판단에서는 잘못된 전역 극값, 실제와 다른 큰 방향 전환, 한
재료의 전체 episode 소실을 본다. 한두 점 누락, 42초 한 지점 복원,
허용된 여러 근사 중 유일 정답 강요는 종료 조건이 아니다.
FULL의 실제 출구 도달, Windows 9개 구간 인수, 독립 사용자의 report-only
판독은 여전히 열려 있다. 추가 Windows 실행·대량 추출 요청은 없다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-EPISODE`, `CSV-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: unqualified scalar profile preferences enter member/authority changes; downstream owner competition loses useful observations or adds unreviewed extremes. No new physical first-cause label is asserted.
- Existing feature coverage: saved current-frame candidate/static/Artifact evidence retained; original geometry/preprocessing supplies pixels. All optional switches OFF. Completed Oil/Foam, independent validity, events, CSV and actual graph/presentation execute. GUI, full HTML source-context generation and Recipe judgment are outside this diagnostic run.
- Execution scope: two fixed models, six interventions plus baseline, 113 sampled frames, 175 sparse-screen Oil candidates. Independent arithmetic/source/publication checks and developer visual inspection; no private Windows replay or independent human report acceptance.
- Logic-map impact: NONE — diagnostic verification/storage only; no production owner/default change.
- Failure-registry impact: NONE — existing identity/coupling/provenance guards explain the scope-limited rejection; no new production failure class or threshold adopted.

## 최종 보존·검증 완료

저장 중 중복 payload를 발견해 수치나 이미지 내용을 바꾸지 않고
`artifact-aliases.json`에 원래 경로·보존 경로·SHA-256을 기록했다.
저장 전용 검산기 보완은 `7917c1e`이며, 원래 수치 실행은 여전히 `9c77aba`다.
추가 경로/hash 안전성 테스트 5개를 포함해 **최종 213개 테스트가 통과**했다.
검산기 v2의 source SHA-256은
`80fa254775dc0404bbd14f3a5b421db8cc9ee1b64eafd9e9476754f7f4bb15cb`이다.

관리 실행은 CLOSED이며 24개 파일, payload 8,727,329 bytes를 보존했다.
중복 CSV/그래프 5개는 hash 고정 alias로 연결했고, 불필요·중복 파일
15개를 관리 절차로 제거했다. 정리 후 원본 픽셀부터 모든 수치·CSV·event와
5개 alias를 다시 검산해 저장된 v2 receipt와 정확히 같음을 확인했다.
전체 관리 실행 **88개, 오류 0**이다. 독립 물리 판정이나 인수 통과를 뜻하지 않는다.

`src/`, Recipe, 원본 media, 기존 검토 truth는 변경하지 않았다.
남은 현재 상태·재개 기준은 Work Plan에 반영한다. 인수인계 후 source나
입력 hash가 달라지면 이 실행을 다른 조건의 PASS로 옮겨 쓰지 않는다.

추가 읽기 검사에서 수치 Foam 175행 모두가 같은 프레임의 원래 Foam
후보 중 하나와 동일 Y임을 확인했다. 이는 후보 집합에 대한 membership
확인이며 물리적 정답이나 유일한 후보 식별을 추가한 것은 아니다.
`review.html`의 일곱 그래프 링크도 중복 제거 이후 모두 유효하다.
