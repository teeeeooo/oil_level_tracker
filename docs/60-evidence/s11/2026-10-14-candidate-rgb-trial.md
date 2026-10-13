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

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: a regional role preference loses practically accepted candidates before any selector can preserve them; RGB compatibility must retain both accepted alternatives and opposed controls.
- Prior mechanisms reviewed: old CR1 category collision and all-four public sign failure; B practical acceptance; original native-head N3 loss; source-qualified candidate bindings and exact floor/ceil support.
- Difference from prior failures: one fixed native RGB candidate-compatibility trial changes input information and supervision, with sample4-only fit and exposed public transfer. It does not retry native external-surface labels, tune the failed role threshold or choose a new production winner.
- Existing feature coverage: existing saved candidate population, original RGB, effective/glare masks and source pins; Recipe exclusions/templates unchanged, Local XY OFF, no D2 efficacy claim.
- Execution scope: completed input preparation and one predeclared offline 1,118-parameter / 1,000-step fit, full-population final inference, mean-color ablation and independent arithmetic verification. The next scoped review reuses the pinned RGB/candidate reader, with a separate renderer for three same-frame unreviewed representative points; no new inference or labels. No production replay, report reading, O2 acceptance or Windows execution.
- Logic-map impact: NONE — offline diagnostic only; production owners and schemas unchanged.
- Failure-registry impact: NONE — no new failure family or accepted detector repair; this checks candidate-level input capability under existing evidence boundaries.
