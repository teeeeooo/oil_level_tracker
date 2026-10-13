# N4/N5 역할 결속과 native 외부 상단 한정 학습 결과

**결과: `CLOSED_WITHOUT_PROMOTION`.** 고정 시험은 N4 내부 변화와 N5 rim을
외부 상단으로 오인하지 않았지만, 실제 외부 상단 N3도 배제했다. 따라서 이
관측기를 Foam raw upper 복구나 생산 detector에 사용할 근거를 얻지 못했다.
실행 기준은 clean `019ccfd9fae3ea5b3421af5e186a0c053dba0922`이며,
실제 자료 학습은 **한 번, 1,000 updates**다. 현재 다음 단계와 권한은
[Work Plan](../../00-project/work-plan.md)이 소유한다.

## 사용자 응답의 정확한 범위

[원문과 subject 결속](../../50-diagnostics/s11/2026-10-13-native-surface-trial/review-reply.json)을
새 supplement로 보존했다. 기존 N1–N3, G0, 검토 그림은 수정하지 않았다.

| Subject | 확정 역할 | 별도 문맥·확신 범위 |
|---|---|---|
| N4 | Foam 내부 변화 | 경로가 glass 표면 원형 무늬의 경계에 강하게 반응하는 듯하다는 **사용자 추정**. 측정으로 입증한 원인이나 확정 구조물 정답으로 바꾸지 않음 |
| N5 | 구조물 경계 | 원형 rim이라는 확인된 문맥. 내부 Foam으로 재분류하지 않음 |

[qualification](../../50-diagnostics/s11/2026-10-13-native-surface-trial/qualification.json)은
이 두 역할을 기존 표시 fragment에만 결속한다. pixel tolerance, 주변 재질 mask,
다른 frame, junction arm, 후보 family나 전체 Glass로 전파하지 않는다. N4의
역할과 잠재적 구조·광학 영향은 공존할 수 있으며 순수 side-material label이 아니다.
기존 [N4/N5 그림](../../50-diagnostics/s11/2026-10-13-native-opposition-review/native-opposition-review.png)의
청록색 N3와 분홍색 N4/N5가 그대로 검토 대상이다.

## 학습 전에 고정한 시험

[manifest](../../50-diagnostics/s11/2026-10-13-native-surface-trial/trial-manifest.json)와
코드를 먼저 커밋했다. 모든 촬영원은 이미 노출된 개발 자료이며 untouched holdout은 없다.

- **학습:** water 촬영의 N1 외부 상단 / N2 내부 변화, 한 경로당 동일 가중치.
- **최종 전이 비교:** sample4의 N3 외부 Foam 상단 / N4 내부 변화 / N5 rim.
  학습·early stop·checkpoint 선택에 이 세 항목을 사용하지 않았다.
- **출력:** 외부 상단 후보 / 외부 상단이 아닌 경로. 내부 변화와 구조물은 평가상
  후자에 속하지만 물리 역할이 같다는 뜻은 아니다. 학습에는 구조물 예제가 없다.
- **관측:** 기존 native 경로의 완전한 upper/lower 7×7 RGB patches, RGB/255,
  shared valid Conv 3→8→8→4, side별 mean 후 Linear 8→2. 총 1,118 parameters.
  위치·촬영원·시각·patch 개수·역할·사용자 추정은 model feature가 아니다.
- **조건:** CPU float32, 2 threads, seed 20261013, Adam 0.001, 1,000 full-batch
  updates, augmentation/정규화/보간/모델 선택/threshold 조정 없음. 동률은 UNKNOWN.
- **실패 기준:** 필수 fit/transfer 어느 하나라도 오답 또는 UNKNOWN이면 이 고정
  시험을 종료한다. 전부 맞아도 full G1, O2, FIELD 통과는 아니다.

완전한 patch 수는 각 side에서 N1 25, N2 7, N3 19, N4 11, N5 17이다.
N1/N2의 90 shared pixels와 N3/N4의 98 shared pixels는 같은 촬영원 안에 남는다.
다른 frame의 N5도 sample4 그룹이다. unavailable upper-rim 두 경로와 나머지
43-context/1,335-edge/164-Oil G0 population은 기존 기록을 참조하며, 미실행 경로를
negative 성공이나 accuracy 분모에 넣지 않았다. 큰 RGB/mask/영상 사본은 만들지 않았다.

## 결과와 의미

[전체 다섯 경로 readout](../../50-diagnostics/s11/2026-10-13-native-surface-trial/readout.json).
아래 margin은 `외부 상단 logit − 비외부 상단 logit`이며 보정된 확률이 아니다.

| Subject | 사용 | margin | 관측 결과 | 판정 |
|---|---|---:|---|---|
| N1 | fit | +10.4673 | 외부 상단 | 학습 대상 적합 |
| N2 | fit | −10.6881 | 비외부 상단 | 학습 대상 적합 |
| N3 | 전이 | −15.6553 | 비외부 상단 | **실제 외부 상단 손실** |
| N4 | 전이 | −38.3211 | 비외부 상단 | 이 경로의 내부 변화는 잘못 수용하지 않음 |
| N5 | 전이 | −16.0074 | 비외부 상단 | 이 rim은 잘못 수용하지 않음 |

두 학습 대상은 맞았지만, 새 촬영원의 세 경로가 모두 비외부로 분류됐다.
`2/3 정답`을 성능 개선으로 제시하지 않는다. 필요한 양성 N3를 보존하지 못했기
때문이다. 이는 **해당 학습 자료·7×7 연산·고정 조건의 전이 실패**이며, 모든 학습법의
실패나 native 역할 관측의 불가능성을 입증하지 않는다. 학습 자료 부족과 표현의
한계를 이 다섯 경로로 분리할 수도 없다. N4/N5 결과는 유리 패턴의 원인 규명이나
일반적인 rim 안전성을 입증하지 않는다. N3를 학습에 넣고 같은 N3 성공을 새로운
전이 성과로 보고하는 변경도 하지 않았다.

## 검증과 비용

[검증 기록](../../50-diagnostics/s11/2026-10-13-native-surface-trial/verification.json).

- 49 focused tests PASS: 기존 G0/qualification, facet 확신 범위, structure 역할 보존,
  촬영원 leakage, 전체 입력 footprint, UNKNOWN 및 wrong-acceptance 집계.
- v1 N1–N3 qualification을 동일 내용으로 재현하고 v2 N4/N5의 실제 CLI와
  10개 side의 입력 bytes를 검사했다. 실행·preparation CLI는 `/private/tmp`에서 수행했다.
- 실제 자료 전에 합성 입력으로 1,118 parameters, gradient update, mean pooling의
  patch 복제 불변성과 별도 NumPy convolution 계산을 확인했다. 실제 source pixels는
  이 사전 검사에 사용하지 않았다.
- 종료 후 저장된 가중치와 직접 RGB slice만 사용한 별도 NumPy float64 계산으로
  다섯 최종 logits를 대조했다. 최대 절대 오차 **0.0000076338 미만**, 산술 비교용
  검증 허용치 0.0001 이내이며 결정은 모두 같다. 재학습이나 판정 cutoff가 아니다.
- 같은 output의 두 번째 CLI는 계산 전에 overwrite를 거부했고 파일 hashes가 유지됐다.
  실제 trial은 7.337 s, process peak RSS 372,588,544 bytes였다. 당시 기존 workspace는
  약 746 MB로, 600 s / 1 GB RSS / 32 MB scratch / 6 MB retained / 전체 3 GB 한도 이내다.
- 기존 Python audit guard의 network/write 거부 self-test 두 건을 확인했다.
  새 설치·다운로드·DINOv2 가중치 변경·영상 decode·Windows 실행은 없었다.
  `src/`와 `pyproject.toml`은 작업 시작점 대비 변경이 없다.

## 보존과 다음 판단

새 preparation run과 학습 run은 [관리 절차](../../40-operations/experiment-artifact-lifecycle.md)로
닫았다. reply/qualification/manifest와 readout/검증/6,594-byte
[최종 가중치](../../50-diagnostics/s11/2026-10-13-native-surface-trial/final-weights.npz)만
단일 tracked 위치에 보존한다. 가중치는 이 실패의 산술 재검증용이며 생산 모델이 아니다.
중간 checkpoint, optimizer state, tensor 사본, 새 검토 이미지, 중복 환경은 남기지 않는다.

**권고하는 다음 범위는 학습 전 역할 자료 확보**다. 이번 실패는 그대로 닫고,
water·sample4를 모두 개발 촬영원으로 쓰려면 **제3 촬영원의 독립된 양성·내부 변화·
구조물 대응**이 먼저 필요하다. 보유한 public 미소냉동 f1499의 저장 RGB/Canny와
기존 지역별 역할 근거는 검토 자료 후보지만, 현재는 정확한 native 경로 positive/
opposition 묶음이 자격화되어 있지 않다. 지역 판단을 다시 묻거나 그대로 edge label로
복제하지 않고, 원본과 기존 path를 연결한 소수의 새 subject로 자격 여부를 확인한다.
입력/역할 대조군이 성립하지 않으면 NOT_READY로 끝내고 재학습하지 않는다.

이 자료 확보 방향을 채택하면 (1) 기존 source/역할 정보만으로 후보와 부족한 항목을
정리하고, (2) 새 native correspondence가 필요한 항목만 사용자에게 제시하고,
(3) 확보된 역할과 source 분리를 바탕으로 **별도 학습 가설과 손실/실패 기준을 먼저
설계**한다. 새 학습의 규모·모델·성공 기준은 아직 채택되지 않았다. 다른 선택은
학습 접근을 보류하고 역할 관측 설계를 재검토하는 것이다. 현재는 이 연구 범위
판단에서 멈추며, Windows 실행이나 FIELD 판정 변경은 요구하지 않는다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: 고정된 offline native-context head가 실제 외부 상단 N3를 비외부로 분류함. 저장 geometry/입력·산술 오류는 검사 범위에서 배제했으나, 학습 자료와 표현의 어느 요인이 전이 실패를 만들었는지는 미확정.
- Logic-map impact: NONE — 새 작업은 scoped reply와 offline 학습 시험이며 생산 detector·Witness·raw-front·episode·publication 실행 경로는 변경하지 않음.
- Failure-registry impact: NONE — 실제 양성 손실로 고정 시험을 닫고 compact 반례를 보존함. 기존 recall/역할 혼동 실패와 구별되는 새로운 물리 실패 family나 승인된 repair를 주장하지 않음.
