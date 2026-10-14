# Candidate-local RGB 입력과 고정 비교

현재 상태와 다음 행동은 [Work Plan](../../00-project/work-plan.md)이 소유한다.
이 기록은 [고정 후보 계약](../../20-architecture/s11-contextual-role-observation-design.md#candidate-local-rgb-compatibility-successor)의
실제 입력 준비와 단일 실행을 다룬다. 기존 native-surface 학습 결과를 바꾸거나
후보 허용을 native 경로·주변 픽셀의 물리 라벨로 확장하지 않는다.

## 실행 전 입력 고정

`31d6bdb`에서 [plan](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/plan.json),
adapter와 검증 조건을 먼저 커밋했다. 기존 역할·실용적 허용과 전체 후보 결합을
재실행하고 저장 결과와 일치시킨 뒤 원본 RGB 및 유효 mask의 7×7 patch를 검사했다.
source hash가 다른 sample4와 공개 영상을 각각 fit과 노출된 transfer로 분리했다.

[준비 결과](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/prepared.json)는
**INPUTS_READY**다. 전체 187개 기록 = Oil 후보 182개 + 비후보 context 4개 + Foam
후보 1개다. Oil 후보 165개는 필요한 floor/ceil 입력을 모두 갖추고, 17개는 입력
부족으로 남는다. 학습 대조 10개와 공개 비교 5개는 모두 입력이 있다. 불가 후보를
정상 음성으로 세거나 mask 밖 픽셀을 채우지 않았다.

준비 파일은 모든 후보, 각 변형의 patch 중심·개수·배열 hash, 원본·관련 source pin을
포함한다. 원본 픽셀 배열은 복제하지 않는다. 2,703,912-byte 출력의 JSON 표현만
압축해 parser 동등성을 확인한 424,387-byte 파일 하나를 보존했다. SHA-256은
`95af399faaf64f0f07a2ffd486af604527cb0225f6f140414613b7e3f24f7ad0`이다.
관리 실행 `s11-candidate-rgb-preflight-20261014-001`은 큰 중복을 제거하고 닫았으며,
이때 전체 관리 실행 29개 오류 0이었다. 이 단계는 모델을 만들거나 학습하지 않았다.

관련 후보·결합·역할·native 계약 테스트 138개가 통과했다. 실제 준비 entry도
완료했으며 학습은 별도로 준비 결과까지 커밋한 clean HEAD에서 한 번 실행한다.

## 단일 학습과 비교 결과

준비 파일까지 고정한 clean HEAD `a7c956f79e48336f0f4c9c303d4a122d5a9bdb4f`에서
격리 Python 3.14.7 / Torch 2.14.1 / NumPy 2.5.4 / Pillow 12.3.0으로 실행했다.
작업 폴더는 `/private/tmp`, 모델은 기존 1,118개 parameter 구조, seed 20261013,
CPU float32, 2 threads, Adam 0.001, 1,000 updates, 최종 checkpoint 하나다.
공개 영상은 loss에 들어가지 않았다. 후보별 변형의 평균 CE를 먼저 구한 뒤
학습 후보 10개를 같은 비중으로 평균했다. 11개 변형은 11개 독립 라벨이 아니다.

[최종 결과](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/readout.json)는
**LIMITED_EXPOSED_CANDIDATE_TRANSFER**다.

| 고정 대조 | 원본 patch | side 평균 색 ablation |
|---|---:|---:|
| sample4 fit 올바른 구분 | 10 / 10 | 10 / 10 |
| 공개 영상 허용 하부 후보 보존 | 4 / 4 | 4 / 4 |
| 공개 영상 기존 오출력 idx3 거부 | 1 / 1 | 1 / 1 |
| 필수 대조의 미측정·변형 불일치 | 0 | 0 |

비교 조건은 충족했지만, 입력 가능한 165개 후보의 결정이 **평균 색 ablation과
전부 같다**. 따라서 세밀한 native 패턴이 성공 원인이라는 주장은 성립하지 않는다.
이것은 다른 head를 재학습한 비교가 아니라 같은 최종 가중치의 평균 색 입력
검사다. 7개 sample4 양성에는 B의 실용적 허용과 과거 초기 참조가 포함되어 있으며,
이들의 학습 성공은 일반화나 독립 평가가 아니다. 공개 영상도 이미 노출된 한
프레임이다. logits는 보정된 확률이 아니며 물리 정확도는 NOT_EVALUATED다.

전체 187개 기록을 남겼다. sample4 미판정 후보는 허용 44개 / 거부 92개 / 입력
부족 14개, 공개 미판정 후보는 허용 0개 / 거부 14개 / 입력 부족 3개다. 이 수치는
모델 결정 분포이며 참·거짓 판정 수가 아니다. 비후보 context 4개와 Foam 1개는
NOT_EVALUATED다. 원래 fit 10개 및 공개 대조 5개와 혼합해 정확도를 만들지 않는다.

특히 미판정 허용 후보 중 18개는 해당 프레임의 기존 허용 후보와 ±12-pixel
입력 영역이 겹치지 않는 하단 위치다. 원본 영상상 테두리 부근으로 보이지만
그 모습만으로 사용자 판정을 부여하지 않았다. 후속 검토는 시간순 첫 해당
프레임 f1140/38 s의 **idx7/Y887, idx10/Y880, idx22/Y882**만 질문한다. 같은
프레임의 기존 idx9/Y844 판정은 다시 묻지 않는다. 이는 최종 점수를 본 뒤의
오수용 조사이며 untouched holdout이나 18개 전체의 물리 라벨이 아니다.

## 실행·산술 검증과 정리

실제 명령은 다음과 같다. 출력은 새 관리 실행의 `work/` 아래여야 한다.

```sh
<repo>/sample/output/s11-cr1-workspace/env/bin/python -B \
  <repo>/tests/diagnostics/s11_candidate_rgb_trial.py run --root <repo> \
  --manifest <repo>/docs/50-diagnostics/s11/2026-10-14-candidate-rgb-trial/prepared.json \
  --output <repo>/sample/output/s11-cr1-workspace/runs/<new-run>/work/trial
```

실행은 75.619699 s, peak RSS 367,919,104 bytes였으며 workspace 사전 할당량은
746,455,040 bytes로 3 GB 이내다. 학습 forward 11,000회, 최종 각 view 169회였다.
감사 hook의 사전 네트워크·외부 쓰기 차단 검사만 denied로 기록됐고, 실제
네트워크·영상 decode·production replay는 없다. 시간은 이 작은 오프라인 시험의
비용이며 detector 지연시간이 아니다.

[가중치](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/final-weights.npz)를
다시 학습하지 않고 NumPy float64의 `sliding_window_view` + `einsum` convolution,
ReLU, side mean과 linear 연산으로 독립 계산했다.
[검증](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/verification.json)은
입력·patch hash, 165개 후보 / view당 169개 변형의 모든 logits와 결정을 확인한다.
Torch float32 대비 최대 절대 오차는 원본 `6.430397e-6`, 평균 색 `3.260615e-5`로
사전 허용 `1e-4` 이내이며 모든 결정이 같다. 필수 대조의 최종 후보별 CE도
검증 기록에 남겼다. 이는 산술 확인이며 분류기 정확도 승인과 다르다.

관리 실행 `candidate-rgb-20261014-001`은 readout 100,545 bytes, 가중치 6,594 bytes,
검증 5,947 bytes를 Git의 한 위치로 옮기고 같은 세 중복을 제거했다. 중간 가중치나
dense feature는 저장하지 않았다. 종료 시 관리 실행 30개 오류 0. 생산 source,
Recipe, 의존성·package 구성은 바꾸지 않았고 Windows도 실행하지 않았다.

## 첫 미판정 허용 후보의 검토 화면

`5d10b6d`에서 질문 범위와 renderer를 먼저 커밋했다.
[검토 화면](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/opposition-review.png)은
sample4 f1140/38 s의 원본 ROI와 새 후보 idx7/Y887, idx10/Y880, idx22/Y882를
각각 표시한다. 초록 idx9/Y844는 기존 허용 문맥이고 노란 십자만 새 질문이다.
십자는 후보 대표점이며 수평 경로·주변 픽셀 라벨이 아니다. 원본 104×104를
nearest-neighbor 3배로 표시하고 원본 문맥 배열 동일성을 검사했다. 화면을 직접
확인해 원본·표식·설명에 잘림이나 겹침이 없음을 확인했다.

[Subject 결합](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/opposition-review.json)은
187개 전체 join, 18개 전체 잠재 대조와 시간순 첫 프레임의 3개 질문을 검증하고
각 query/source/image hash를 보존한다. model call과 새 라벨은 모두 0이다.
14–16 s의 C1/N5 원형 테두리 판정과 40–44 s의 기존 오출력 판정은 닫힌 범위로
유지했다. 이 기록들은 지금 표시한 38 s의 세 후보에 대한 실용적 허용 판정이
아니므로 새 후보만 묻는다. 모델 점수는 화면에 표시하지 않았다.

관리 실행 `s11-candidate-rgb-review-20261014-001`은 검토 PNG 69,254 bytes와 JSON
8,407 bytes만 Git 위치에 보존하고 중복 둘을 제거했다. 관리 실행 31개 오류 0.
답변이 오면 exact subject에 허용/거부/미판정으로 결합해 저장된 모델 결정과
비교한다. 다른 15개나 이웃 후보·프레임으로 확대하지 않으며 새 학습은 하지
않는다. 세 후보 중 거부가 있다면 현재 모델의 실제 오수용으로 기록해야 한다.

공개 전 변경 Markdown 7개의 로컬 링크 1,190개와 새 docs 파일 13개의 catalog
등록을 확인했다. Detector Governance와 whitespace 검사도 통과했다. 현재 Oil
worktree는 main 한 개이며 이 작업의 임시 plan/선택표/산술 script 9개는 관리
표식과 검증 기록을 남긴 뒤 제거했다. 고정된 기존 환경·원본·다른 작업 자료는
복제하거나 삭제하지 않았다.

## Rim 답변 수신 — 같은 날 후속

사용자는 **“노란 하단 후보는 구조물이야 glass 주변 rim임.”**이라고 답했다.
[답변 결합](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/rim-reply.json)은
f1140의 idx7/10/22를 glass-rim 구조물 및 Oil 근사 거부로만 기록한다. 하위 유형은
사용자가 직접 제시했다. 질문 밖의 다른 15개, native 경로 전체, 주변 픽셀이나
Recipe 제외 영역에는 확장하지 않는다. 초록 idx9 판정은 유지한다.

[저장 결과 검사 계획](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/rim-plan.json)은
기존 재사용 실행기를 확장해 표시 이미지·원본·후보·변형을 결합하고, 새 반대
대조의 원본/평균 색 결정을 확인한다. 단일 margin cutoff의 필요조건만 조사하며
학습·추론·임계값 선택을 하지 않는다. 원래 limited readout은 수정하지 않는다.

`9ef0aae`에서 코드를 고정한 뒤 `/private/tmp`에서 실행한
[결과](../../50-diagnostics/s11/2026-10-14-candidate-rgb-trial/rim-readout.json)는
**FALSIFIED_BY_REVIEWED_RIM**이다. 세 rim 모두 원본 및 평균 색 입력에서
Oil 호환으로 판정됐다. 원래 15개 대조의 limited 통과는 당시 비교 사실로 유지하고,
현재 분류 능력은 채택하지 않는 것으로 종료한다. 3/3은 사후 선정된 반례의
오수용 수이며 전체 모집단의 오수용률 추정이 아니다.

| 입력 view | 가장 높은 rim margin | 가장 높은 기존 양성 margin | 모든 반대를 제거하면서 양성 하나라도 보존 |
|---|---:|---:|---|
| 원본 | idx7: 18.800531 | f1200 idx4: 14.790019 | 불가능 |
| side 평균 색 | idx7: 17.813394 | f1260 idx4: 14.198208 | 불가능 |

margin은 두 logit의 차이며 확률이 아니다. 필수 변형별 margin의 최솟값이 공통
임계값보다 클 때만 허용하는 단조 정책에서의 필요조건이다. 임계값은 선택하지
않았다. 모든 확정 양성보다 높은 rim을 제거하면 양성도 모두 사라진다. 모델이나
전체 학습의 불가능성을 의미하지는 않으며, 이 결과를 같은 모델의 cutoff 변경으로
구제하지 않는다.

전체 187개 / Oil 182개를 검증했다. 원래 대조 15개, 새 대조 3개, 미판정 Oil
164개와 그 안의 입력 부족 17개를 구분했다. 질문 밖의 잠재 후보 15개는 여전히
미판정이다. 새 방어 테스트 15개를 포함한 관련 76개가 통과했다. 실제 실행은
0.969787 s, peak RSS 205,684,736 bytes, 출력 17,615 bytes이며 추가 model call은 0이다.
관리 실행 `s11-candidate-rgb-rim-20261014-001`은 결과 하나만 Git 위치에 보존하고
동일한 작업용 사본을 제거했다.

## 기존 다른 촬영원으로 후보 판정 확장 준비

다음 작업은 새 학습을 먼저 반복하는 것이 아니라, sample4의 새 구조물 대조와
함께 쓸 수 있는 다른 촬영원의 후보 판정을 정리하는 것이다. 기존 sample3 A/B의
[regional 판정](../../50-diagnostics/s11/2026-10-10-sample3-gap-source-reply.json)과
[허용 평가 범위](../../50-diagnostics/s11/2026-10-10-sample3-evaluation-scope.md)를
읽었다. A/B의 Oil 존재는 확정이며 전체 영상의 위치·초점 문제, C 구조물과 D
판별 불가는 그대로 유지한다. 두 정지 프레임을 쓰는 것은 전체 구간을 물리 정확도
기준으로 되살리는 것이 아니다.

[후보 질문 계획](../../50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/review-plan.json)은
옛 archive의 각 A/B 상단 row에 저장된 유일한 material-path 후보를 질문한다:
**A/f2249 idx6, X835/Y219; B/f2339 idx5, X835/Y227**. Row는 탐색 기준일 뿐 물리
권한이 아니며, A 20개와 B 18개, 전체 38개 후보를 분모에 남긴다. 중앙 sector의 별도 pooled
Y는 A216/B227이고 native contour가 아니다. 기존 빨간 점을 좌표·허용 폭으로
추출하지 않는다. 새 모델 점수 없이 대표값의 실용적 허용만 묻는다.

Archive renderer는 기존 pin reader와 current/native candidate 결합을 재사용한다.
원본 archive는 압축 해제 시 95,879,807 bytes로 CR1의 8 MiB JSON reader 범위를
넘으므로 전역 제한을 높이지 않고, 이 고정 archive만 exact-size / 100 MB 상한으로
읽는다. 원본 프레임·기존 crop·닫힌 review 화면의 픽셀 동일성을 확인하도록 했다.
모델 입력의 가시성 계약·학습 split·음성 촬영원 범위는 별도 준비 전까지 미정이다.
새 학습, candidate score, 영상 decode, 생산·Recipe 변경은 이 준비에 포함되지 않는다.

`5d64853`에서 계획과 renderer를 고정한 뒤 `/private/tmp`에서 절대 경로로 실행했다.
[검토 화면](../../50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/candidate-review.png)과
[결합 결과](../../50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/review.json)는
38개 current/native 후보 결합, 원본 프레임에서 자른 RGB와 기존 crop의 배열 동일성,
이전 검토 화면의 원본 영역 동일성을 모두 통과했다. 모델 점수 없이 노란 십자로
후보 대표점을, 청록선으로 별도 중앙 pooled sample을 표시했다. 실제 PNG의
표식·원본·설명에 잘림이 없음을 확인했다. 노란 두 대표점의 실용적 Oil 근사 허용은
**AWAITING_TWO_SCOPED_CANDIDATE_JUDGMENTS**이며 다른 36개는 미판정이다.

실제 준비는 0.837868 s, peak RSS 607,453,184 bytes였다. 관리 실행
`s11-oil-candidate-source-review-20261014-001`은 PNG 160,336 bytes와 JSON
29,367 bytes만 위 Git 위치에 보존하고 동일한 작업 사본 둘을 제거했다. 두 노출
프레임은 별도 데이터·split 계약 전까지 미래 fit에서 보류한다. 모델별 입력 준비는
`NOT_PREPARED`이며 새 판정·추론·학습은 0이다. 관리 실행 33개가 모두 종료됐고
오류는 0이다. Windows 실행이나 생산 동작의 개선을 주장하지 않는다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: a regional role preference loses practically accepted candidates before any selector can preserve them; RGB compatibility must retain both accepted alternatives and opposed controls.
- Prior mechanisms reviewed: old CR1 category collision and all-four public sign failure; B practical acceptance; original native-head N3 loss; source-qualified candidate bindings and exact floor/ceil support.
- Difference from prior failures: one fixed native RGB candidate-compatibility trial changes input information and supervision, with sample4-only fit and exposed public transfer. It does not retry native external-surface labels, tune the failed role threshold or choose a new production winner.
- Existing feature coverage: existing saved candidate population, original RGB, effective/glare masks and source pins; Recipe exclusions/templates unchanged, Local XY OFF, no D2 efficacy claim.
- Execution scope: completed input preparation and one predeclared offline 1,118-parameter / 1,000-step fit, full-population final inference, mean-color ablation and independent arithmetic verification. The existing reuse CLI executed the explicit rim-reply binding and saved margin check. The separate archive adapter prepares two sample3 candidate questions from existing regional-positive views with complete current/native joins and source-pixel checks. No new inference, training, automatic labels for other candidates, production replay, report reading, O2 acceptance or Windows execution.
- Logic-map impact: NONE — offline diagnostic only; production owners and schemas unchanged.
- Failure-registry impact: NONE — no new failure family or accepted detector repair; this checks candidate-level input capability under existing evidence boundaries.
