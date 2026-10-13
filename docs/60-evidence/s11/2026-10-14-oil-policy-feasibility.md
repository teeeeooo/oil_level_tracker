# Oil 후보 정책 필요조건 검사 — 2026-10-14

**결과: 물리 대응 대조군에서는 NOT_FALSIFIED_ON_EXPOSED_CONTROLS.**
기존 local 역할 점수 차이와 절대 지지도를 함께 쓰는 정책은 sample4의
현재 양성 6개를 보존하면서 거부 대상 3개를 분리할 가능성이 남아 있다.
초기 참조를 제외한 양성 5개에서도 같다. 이는 임계값 선택·성능 검증·생산
채택이 아니다. 현재 전이와 판단 요청은 [Work Plan](../../00-project/work-plan.md)이 소유한다.

## 고정한 연산과 결과

[Manifest](../../50-diagnostics/s11/2026-10-14-oil-policy-feasibility/manifest.json)와
구현을 clean `bd02021`에서 고정하고 기존 reuse CLI의 `--policy-manifest`로
실행했다. 별도 실행기를 만들지 않고 CR1 점수 owner에 필요조건 검사만 추가했다.
원래 reuse 감사가 164개 전체 및 최신 판정·지원 hash를 먼저 재검증한다.

| 검사항목 | 결과 |
|---|---|
| 물리 대응 양성 6개 | 전부 측정 가능, 모든 필수 anchor의 local margin > 1e-6 |
| 초기 참조 제외 | 양성 5개 동일 결과; 별도 영상 5개가 아님 |
| f1200 idx10 / f1260 idx15 거부 대상 | local margin 음수; 고정 sign 조건 미충족 |
| f1320 idx21 거부 대상 | sign 양수이나 지지도 0.442885; 양성 최저 0.744978보다 낮음 |
| 양성을 보존하면 반드시 통과하는 거부 대상 | 없음; 임계값 순서 모순 없음 |
| 전체 분모 | 164 records: 대응 6 / 거부 3 / A·B 미확정 2 / 미평가 153; 측정 132 / unavailable 32 |
| source 독립성 | scored recording 1, untouched holdout 0 |

두 수치 사이에서 운영점을 고르거나 breakpoint sweep을 하지 않았다.
지역 문맥 범주만으로 겹쳤던 일부 후보가 절대 지지도에서는 구분될 여지가
있다는 뜻이다. 같은 source에 맞춘 우연한 간격인지 아직 판단할 수 없다.

**실용적 허용은 별도 제한이다.** 이미 사용자가 근사값으로 허용한 f1485 B의
local margin은 −0.021206이므로 이 sign 조건을 모든 출력의 필수 필터로 쓰면
B를 보존하지 못한다. 이 결과를 물리적 false negative로 바꾸지도, 제품상
허용된 결과의 손실을 숨기지도 않는다. A의 철회된 물리 주장도 복구하지 않는다.
따라서 이 family를 바로 선택·추적의 공통 hard filter로 채택할 근거는 없다.

## 확인 및 보존

- 관련 계약 테스트 **137 passed in 1.83 s**. 추가 21개는 경계 동률, fractional
  최악 anchor, 결측·비유한값, 초기 참조 분리, 같은 좌표의 다른 subject와 roster
  변조를 검사한다. 이 숫자는 detector 정확도가 아니다.
- `/private/tmp`에서 절대 경로 CLI 실행: **0.957713 s**, process peak RSS
  **204,718,080 bytes**, 결과 **9,350 bytes**. 시간은 저장 자료 감사의 값이다.
- [전체 compact readout](../../50-diagnostics/s11/2026-10-14-oil-policy-feasibility/readout.json)
  SHA-256 `e5c1124020c0ee161805a56cabb55c463a6cc06b3ee92f329df05bf11e09ddf5`.
  원시 점수·이미지·전체 164개 표는 기존 pin을 참조하고 복제하지 않았다.
- 관리 실행 `s11-oil-policy-feasibility-20261014-001` 종료: readout 중복 1개 제거,
  tracked 결과만 재사용. 종료 시 26개 관리 실행 오류 0.

재현 시 새 관리 실행을 열고 다음의 모든 인자를 절대 경로로 주면 된다.

```sh
PYTHONDONTWRITEBYTECODE=1 <repo>/.venv/bin/python -B \
  <repo>/tests/diagnostics/s11_existing_material_reuse.py --root <repo> \
  --manifest <repo>/docs/50-diagnostics/s11/2026-10-13-existing-material-execution/manifest.json \
  --policy-manifest <repo>/docs/50-diagnostics/s11/2026-10-14-oil-policy-feasibility/manifest.json \
  --output <managed-work>/readout.json
```

## 다른 촬영원으로 이어갈 입력

기존 공개 압축기 f1499의 Oil 범위 X578/Y421–435는 이미 확정되어 다시 묻지
않는다. 23개 저장 후보 중 그 범위 안의 Oil 대표값은 idx5/Y430, idx9/Y425,
idx13/Y427, idx20/Y424의 네 개다. 점수와 무관하게 **모두** 검토 대상으로 묶는다.
idx9에는 중심 sector X[557,600)의 pooled Y429가 별도로 있다. 후보 대표값,
sector 값과 native 경로는 다르다.

이 네 후보를 해당 프레임의 **실용적으로 허용 가능한 유면 근사**로 취급할지는
기존 영역 판정에서 자동으로 따라오지 않는다. 이 선택이 정해지면 후속 평가를
`허용된 하부 후보 최소 하나 유지 / 범위 밖 상단 오출력 억제 / 미확정 보존`의
후보 수준으로 고정할 수 있다. 실제 미세 경로 정답이나 새 학습은 필요조건이 아니다.
반대로 일부만 허용되거나 구분 불가라면 그 범위 그대로 유지한다. 새 모델 점수를
보기 전에 이 acceptance 범위를 정한다. 이를 native 물리 라벨로 변환하지 않는다.

sample5의 A/B/C도 재검토하지 않는다. A는 Foam 상단, B/C는 Foam 없는 물 상단의
기존 범위 대조다. B는 저장된 경로 제안이 범위에 닿지 않아 후보 분류의 음성으로
세면 안 되고, C의 pooled 후보는 물 상단 제안 회수 대조일 뿐 Oil/Foam 후보 정답은
아니다. 공개 압축기는 실제 Foam/Oil 문맥이 있는 두 번째 source이며 기존 노출된
평가 자료로만 사용한다. 어느 경우에도 untouched holdout으로 바꾸지 않는다.

### 검토 화면과 종료 검사

[후보 화면](../../50-diagnostics/s11/2026-10-14-oil-policy-feasibility/candidate-review.png)에서
노란 십자는 후보 대표점이며 idx9의 청록 선분은 저장된 sector Y429다.
선분은 픽셀 윤곽이 아니다. 원본 영역과 저장 RGB 배열의 동일성, 23개 전체
후보의 index/source/Y, 네 개 질문 대상의 누락 없음이 실제 실행에서 확인됐다.
원본과 확대 화면을 직접 확인해 위치·legend·잘림 없는 배치를 검토했다.
[Subject 기록](../../50-diagnostics/s11/2026-10-14-oil-policy-feasibility/review.json)은
전체 23개 후보 hash와 질문 대상 4개의 미평가 상태를 보존한다.

`9c7d087`에서 입력·scope·renderer를 먼저 고정했다. 재현기는 기존 native-fragment
화면과 다른 **후보 대표점/pooled sector** envelope를 다루기 위한 작은 adapter다.
기존 position join과 O2/G0 pin reader를 재사용하며 frozen 렌더러를 수정하지 않는다.
별도 점수, 영상 decode, 새 물리 라벨은 없다. CLI는 `/private/tmp`에서 실행했다.
같은 plan으로 `prepare_candidate_review.py --root <repo> --plan
<repo>/docs/50-diagnostics/s11/2026-10-14-oil-policy-feasibility/candidate-review-plan.json
--output <new-managed-work>/review`를 실행하면 된다.

검토 PNG 159,587 bytes와 JSON 10,793 bytes만 Git 위치에 보존했다. 관리 실행
`s11-public-oil-candidate-review-20261014-001`의 중복 두 파일은 종료 시 제거했다.
이 실행을 포함한 관리 실행 27개 오류 0. 원본 영상·NPZ·capture 복제본은 만들지
않았다. 현재 허용 범위의 답변이 와야 후속 평가를 고정하므로 이 지점에서 멈춘다.
최종 문서 검사에서 변경 Markdown 7개의 로컬 링크 1,271개와 새 문서·산출물
7개의 catalog 등록을 확인했다. Detector Governance 및 whitespace 검사도 통과했다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: a candidate's regional preference cannot acquire physical identity or production authority from exposed score separation; practical B preservation remains a separate unsatisfied filter requirement.
- Prior mechanisms reviewed: fixed CR1 category collision and continuous support proposal; P2 cost/margin necessary-condition witness; current A/B qualification; closed public-source intervals and complete current/pipeline candidate captures.
- Difference from prior failures: evaluate the proposed CR1 continuous family without a threshold search, retaining exact controls, all unknowns and the reference/nonself distinction. Public review concerns scoped candidate approximation, not relabeling intervals as contours.
- Existing feature coverage: existing O1/A1/CR1 and public capture geometry only; Recipe exclusions/templates unchanged, Local XY OFF, no D2 or static-learning efficacy claim.
- Execution scope: saved-data audit and candidate-review preparation only; no encoder, production frame/sequence replay, report reading or Windows run.
- Logic-map impact: NONE — offline diagnostic extension only; production schema and executing owners unchanged.
- Failure-registry impact: NONE — no new failure family or accepted detector repair; this refines existing evidence/authority boundaries.
