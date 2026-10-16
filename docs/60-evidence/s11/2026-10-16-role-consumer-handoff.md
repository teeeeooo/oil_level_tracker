# S11 RCI-1 인수인계 — 역할 판정과 report 맥락의 연결 검증

## 결론과 현재 상태

**네 가지 가설의 전체 구간 검증과 원본 영상 대조를 완료했다.**
부정 후보 배제와 실제 계면 후보의 권한 부여를 함께 적용하면,
기존에 올바르게 선택된 38/42.5/52초 관측을 유지하면서 40/44초의
실제 계면 후보를 회복할 수 있었다. 단순 anchor 강등, 부정 후보 배제,
긍정 권한 부여 중 어느 한 가지로는 같은 결과를 얻지 못했다.

다만 이것은 **이미 검토된 후보 역할을 제한적으로 주입한 원인 분리 실험**이다.
영상 픽셀에서 역할을 자동 판정하는 새 detector를 구현하거나 채택한 결과가 아니다.
결합 실험의 5/6 회복을 100%로 만들기 위해 보류한 것이 아니다.
자동 역할 판별이 아직 없고, 새 극값과 미검토 소유권의 물리적 대응을
이 실험만으로 증명할 수 없으므로 production에 반영하지 않았다.

S11 ACTIVE, O1 locally accepted, W4/O2 OPEN, FIELD FAIL을 유지한다.
R22 기본 동작과 기존 report 기능은 변경하지 않았다. IFO v2는 기존 opt-in이며,
Local XY·cost-first·RGB·top-exit은 이번 실험에서 모두 OFF이다.
Windows 추가 실행이나 새로운 사용자 판정 요청은 만들지 않았다.

현재 상태의 유일한 owner는 [Work Plan](../../00-project/work-plan.md)이다.
[가설·실행 상세](../../50-diagnostics/s11/2026-10-16-role-consumer-context.md)와
[검증 요약 JSON](../../50-diagnostics/s11/2026-10-16-role-consumer-context/summary.json)에
전체 판정과 산출물 해시를 등록했다.

## 실행 기준과 실제 사용한 증거

시작 HEAD는 `b7576c72e2176256bc5323e52a80beaccfadb284`이다.
역할 개입 코드·가설·검증기는 **`15b735e10dfb1dd64c133d538673492f0d5722b7`**에
고정한 후 실행했다. 원본 source-context 보조 검증 코드는
**`dc38ba3f51ac62a5cad16e040b25768b325eb23b`**에 별도 고정했다.

| 자료 | 이번에 한 일 | 해석 한계 |
|---|---|---|
| Mac sample4 P5 원본 후보와 완료 결과 | 0–56초, 2 Hz, 113개 관측을 각 조건에서 전부 재실행 | 새 frame detector 추출이 아니라 저장 후보를 이용한 실제 완료 처리·출력 경로 실행 |
| Mac sample4 원본 MP4 | 같은 113개 표본을 다시 decode하고 4개 원본 atlas를 직접 검토 | native 30 Hz 전체 프레임 검토 또는 새로운 정답 작성이 아님 |
| 최신 CRW-1 역할 roster | sample4 물리적 대응 6개, 실용적 허용 1개, 부정 후보 6개를 정확한 frame/index/source/Y로 연결 | sector 수를 classifier로 사용하지 않음. 실용적 허용은 물리적 anchor 정답으로 승격하지 않음 |
| Windows 누적 진단·검토 | ④ IFO v2, 721초 false anchor, ⑤/⑥/⑦ 실패, ⑧ preflight 실패와 9개 canonical 구간을 설계 제약으로 대조 | 수신 증거 재검토이며 새 Windows 영상·CSV 실행이 아님 |
| public compressor / sample3 | 기존 CRW 역할과 실용 허용, 기존 quarantine 경계를 유지 | public 연속 구간과 sample3는 이번에 재실행하지 않음 |

이전 f1485 idx19의 물리적 대응을 다시 정답으로 사용하지 않았다.
현재 idx8/Y841의 practical-only 허용은 그대로 보존했다. 모든 미검토 대안은
미검토로 남겼으며, 같은 Y·같은 source·같은 track이라는 이유로 역할을 전파하지 않았다.

## 네 가지 가설의 실제 결과

기준선 외에 아래 네 조건을 실행했다. 각 조건은 **113개 관측 전체**에 적용했고,
Oil 완료 처리 → Foam 조합 → TrackingSample → events → CSV → report presentation →
실제 graph renderer까지 실행했다. 그래프를 나중에 평활화하거나 보간하지 않았다.

| 조건 | Oil 수치 관측 | 현재 물리 대응 후보 선택 | 부정 후보 선택 | 기존 유효한 3개 유지 | 새로 회복한 물리 대응 |
|---|---:|---:|---:|---:|---|
| 기준선 | 101 | 3 | 3 | 3 | 없음 |
| H1. 부정 후보의 anchor만 강등 | 101 | 3 | 1 | 3 | 없음 |
| H2. 부정 후보를 정확한 member 단위로 제외 | 104 | 2 | 0 | 2 | 없음 |
| H3. 물리 대응 후보에 positive authority만 부여 | 101 | 4 | 0 | 2 | 40초, 44초 |
| H4. H2와 H3 결합 | 106 | 5 | 0 | 3 | 40초, 44초 |

물리 대응 후보는 총 6개, 부정 후보는 총 6개인 **노출된 소수 제어 사례**이다.
이 표는 detector 정확도나 전체 영상 정답률이 아니다. 별도의 practical-only
후보 1개는 모든 조건에서 미선택이며, 이를 이유로 실험을 자동 실패시키지 않았다.

### H1 — anchor 권한만 줄이면 충분한가?

충분하지 않았다. 40/42초의 기존 잘못된 후보는 다른 후보로 바뀌었지만,
44초의 잘못된 최고 유면은 유지됐다. 새 최저 유면은 40초/Y867의 미검토 후보다.
최종 선택이 2개 바뀌었을 뿐 phase 소유권은 바뀌지 않았다.
따라서 corroboration에서 독립 anchor 자격만 줄이는 방식은 후속 continuation과
같은 행의 대체 후보가 만드는 report 문제를 해결한다고 볼 수 없다.

### H2 — 잘못된 후보만 제외하면 충분한가?

세 개의 알려진 잘못된 선택은 사라졌지만, 선택 14개와 phase witness 25개가 바뀌고
기존에 올바르게 선택된 52초 관측이 밀려났다. 수치 관측 101→104를 개선으로
계산하면 이 손실을 놓친다. 최저/최고는 51.5/53초의 미검토 대안으로 이동했다.

### H3 — 실제 계면 후보에 권한을 주면 충분한가?

40/44초를 회복했지만 기존 42.5초의 올바른 후보를 밀어냈다.
선택 16개가 바뀌었고, 42초는 권한 부여만으로 목표 후보가 최종 선택되지 않았다.
이는 현재 한 후보에 주는 긍정 권한과 주변 후보·소유권 경쟁이 분리되지 않음을 보여준다.

### H4 — 긍정·부정을 함께 전달하면 어떠한가?

기존의 올바른 세 관측을 모두 유지하고 40/44초를 회복했다.
40–44초의 기존 잘못된 큰 상하 변동을 제거하는 데 유용한 소비 경로가 확인됐다.
42초는 여전히 수치 관측이 없지만, 이를 메우기 위한 별도 threshold 조정은 하지 않았다.

그러나 최고 유면은 새로 51초/Y820, 최저는 2초/Y858로 선정됐다.
이 후보들은 여전히 미검토다. 원본 전 구간 atlas와 변경 그래프를 대조했지만,
특히 50.5–51초의 새 피크가 같은 계면을 계속 따른다고 확정하지 않았다.
기존 오검출 제거와 새 극값의 물리적 타당성은 다른 질문이다.

## Foam 및 report 관점의 해석

Foam 수치/유효 관측은 기준선 26/26, H1 26/26, H2 26/25,
H3·H4 25/25이다. report presentation은 모든 조건에서 주요 Foam episode를 1회로
표현한다. 전체 Foam episode가 사라지는 회귀는 이번에 없었다.

H3/H4의 새 39.5초 Oil Y838 때문에 기존 Foam Y841에 최종 Oil alias 거부가 적용됐고,
표본상 Foam 시작이 39.5→40초로 바뀌었다. **이 0.5초 차이 자체를 맥락 실패로
판정하지 않는다.** H2는 40초의 Foam Y840을 유지하지만 Oil Y831을 새로 선택해
위상 순서 충돌을 만들고 Oil/Foam 유효성을 모두 false로 바꿨다.
따라서 Foam 좌표 개수만 비교하면 부족하고, 독립 유효성과 episode 표현도 함께 봐야 한다.

추가로 최저·최고 이외의 **전체 domain event 143개**를 CSV와 대조했다.
H3에서는 41.5초 OIL_DROP_START가 새로 발생하지만 H4에서는 발생하지 않는다.
이 새 하강 사건의 물리적 의미는 아직 확정하지 않았으므로 실제 회복으로 계산하지 않는다.
단순 검출 개수뿐 아니라 운동 사건의 생성·소멸까지 확인해야 하는 구체적 근거다.
원본의 verifier v1 receipt는 그대로 보존하고, 후속 v2는 이 전체 이벤트 연결도 검사한다.

현재 비교용 result container의 상태는 명시적으로 REVIEW_REQUIRED이다.
자동 Recipe 합격 판정, 전체 HTML/source-context 생성 경로, GUI와 실제 독립 사용자의
report-only 이해도 평가는 새로 실행하지 않았다. 개발자의 그래프·원본 대조를
독립 사용자 판독 통과로 바꾸지 않았다.

## 검증 및 보존

기준선은 저장된 완료 결과의 모든 필드에서 **113/113 동일**했다.
독립 검증기는 **565개 CSV 관측, 513개 수치 Oil의 동일 프레임 후보 연결,
12,745개 authority 호출, 10개 극값**을 확인했고 불일치는 0이다.
이는 처리·출처·개입 범위 검증이지 물리적 정확도 검증이 아니다.

원본 보조 검증은 **113개 frame/time 연결과 113개 저장 PNG 원본 픽셀 복원 검사**를
통과했다. 원본 영상 SHA256도 일치한다. 새 정답은 작성하지 않았다.
신규 55개를 포함한 관련 unit test **210 passed**이며, detector governance와
artifact lifecycle check를 통과했다. 운영 source, Recipe, 원본 입력과 formal truth는 변경하지 않았다.

역할 개입 run은 19개 파일/1,589,066 bytes, 원본 보조 run은 7개 파일/2,042,577 bytes를
보존했다. 두 run 모두 CLOSED이며 전체 managed run 87개에서 오류는 0이다.
중복 combined 그래프와 중복 preflight만 정리하고 재현에 필요한 근거는 남겼다.

로컬 저장소 기준 산출물:

```text
sample/output/s11-role-consumer-20261016-001/evidence/
  comparison.json          조건별 결과와 report presentation
  readout.json.gz          전체 authority / 후보 행 / phase / 선택 trace
  verification.json        독립 검증 결과
  review.html              DIAGNOSTIC ROLE ORACLE 경고가 있는 비교 페이지
  <variant>/tracking.csv
  <variant>/events.csv
  <variant>/graphs/sample4_sight_glass_detail.png

sample/output/s11-role-source-context-20261016-001/evidence/
  source-context.json      영상·frame·crop·원본 픽셀 출처
  source-1.png ... source-4.png
  verification.json        저장 atlas의 독립 픽셀 검증
  input-relocation.json    생산 run의 work→evidence 이동과 동일 해시 확인
```

전체 checksum과 retained size는 요약 JSON에 있다. 첫 run 완료에 따른 비교 JSON의
경로 이동만 있었다. 두 번째 run의 당시 실행 경로는 원본 preflight에 보존하고,
현재 재사용 경로와 동일 bytes를 input-relocation.json에 연결했다.

## 후속 담당자의 실행 기준

**다음 작업은 새 input-only audit나 oracle 반복이 아니라, 픽셀에서 얻는 qualified
positive/negative 역할 증거를 실제 consumer에 연결할 한 개의 bounded 설계·구현이다.**
CRW-1은 입력 재료로 재사용하되, sector count나 중복 peer를 물리적 역할로 둔갑시키지 않는다.
부정 증거는 anchor에만 적용하지 않고 continuation과 후보 member의 재진입까지 일관되게
소비해야 한다. 긍정 증거는 기존 material/phase/owner 해석과의 관계를 명시해야 한다.
이름만 같은 source·track 전체에 정답을 전파하거나 raw texture conflict를 지워서는 안 된다.

선정 지표는 전체 구간의 알려진 잘못된 극값/가짜 반전 감소, 유용한 움직임 보존,
새 미검토 대안과 장기 소유권 변화, Oil/Foam 유효성과 episode 맥락이다.
42초 하나를 복원하기 위한 별도 예외나 완전 검출률 목표는 만들지 않는다.

Windows의 721초 false anchor와 723/771초 보호 조건, review-004/005의 복수·약한
허용을 별도로 유지한다. 이번 sample4 결과가 Windows 교정 결과를 대신하지 않는다.
FULL의 물리적 endpoint와 mask top은 여전히 다르며 ⑧은 NOT RUN이다.
9개 canonical 구간과 독립 report-only 판단은 최종 통합 acceptance에서 닫아야 한다.
Review-006은 계속 미검토, sample3는 기존 quarantine을 유지한다.

재현은 Mac의 기존 입력을 재사용해 **새 managed run**에서 실행한다.
아래 OUT은 scripts/experiment_artifacts.py start로 만든 빈 work 디렉터리다.
현재 보존된 evidence 폴더에 덮어쓰지 않는다.

```bash
.venv/bin/python -m tests.diagnostics.s11_role_consumer_intervention \
  --output "$OUT" --acknowledge-role-oracle
.venv/bin/python -m tests.diagnostics.s11_role_consumer_verify \
  --root . --directory "$OUT" --output "$OUT/verification.json"

.venv/bin/python -m tests.diagnostics.s11_role_source_context \
  --comparison sample/output/s11-role-consumer-20261016-001/evidence/comparison.json \
  --output "$SOURCE_OUT"
```

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: known sample4 wrong selections and positive authority rejection are the scoped baseline. The interventions reveal replacement/ownership/Foam composition effects, not the original optical cause or a new Windows causal repair.
- Existing feature coverage: exact P5 NONE raw/Recipe/session, no exclusions/templates, unchanged mask/static/Artifact preparation outcomes. All optional comparison flags OFF. Current completed Oil/Foam, samples, events, CSV, presentation and graphs executed; new extraction/model/Recipe judgment did not.
- Execution scope: 5 x 113 saved-candidate rows, current 13 scoped review bindings, plus 113 exact sampled original source frames. Temporary role injections restore on exit; original scores and practical/unknown labels preserved. Source inspection is post-run and not an independent human response.
- Logic-map impact: NONE — no production owner, default or call route changed; diagnostic-only seams and preserved artifacts document the existing route.
- Failure-registry impact: NONE — partial consumer feasibility and new unqualified extrema do not establish a new physical mechanism or promoted repair.
