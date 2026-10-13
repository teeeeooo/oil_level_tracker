# N1–N3 역할 응답 결속과 다음 연구 범위 준비

기준 HEAD: `96955bc426441f65f7bf39516c0df81bfeb946e2`.
이 기록은 사용자 응답을 받은 뒤 완료한 **역할 결속과 입력 준비도 점검**이다.
모델 학습·추론·생산 detector 변경·Windows 실행은 하지 않았다.
현재 실행 권한과 다음 판단은 [Work Plan](../../00-project/work-plan.md)이 소유한다.

## 받은 판정과 보존한 정밀도

[사용자 원문](../../50-diagnostics/s11/2026-10-13-native-role-qualification/review-reply.json)을
기존 proposal·검토 그림·각 subject의 hash에 연결했다.

| Subject | 사용자 판정 | 후속 비교에서의 의미 |
|---|---|---|
| N1 — water f1232, fragment 1197 | 외부 Foam 상단. 흔들리는 액체 상단이라는 해석도 허용 | 허용 해석 집합을 유지하며 공통 target은 외부 표면. Foam/액체를 강제로 하나로 고르거나 양쪽 물질의 정밀 정답으로 만들지 않음 |
| N2 — 같은 frame, fragment 1542 | Foam 내부 변화 | 표시한 7-pixel fragment에 한정된 내부 변화 대조군 |
| N3 — sample4 f1620, fragment 120 | 외부 Foam 상단 | 표시한 19-pixel fragment의 외부 상단 역할 대응 확인 |

이는 전체 표시 경로의 **역할 대응**이며 한 픽셀 위치 정확도, 주변 재질 mask,
다른 junction arm·이웃 frame·후보 family의 정답이 아니다. N3의 Y813은 이제
단순 구간 hit를 넘어 해당 경로에 한정된 역할 근거를 갖는다. 기존 raw front Y833이
복구됐거나 downstream 손실만 남았다는 뜻은 아니다.

과거 G0의 `new_physical_labels=0`와 pending packet은 그 시점 기록 그대로 보존했다.
새 [qualification](../../50-diagnostics/s11/2026-10-13-native-role-qualification/qualification.json)은
별도 supplement로 3개 역할 단위를 결속한다. 기존 43 contexts/1,335 edges와 164 Oil
records, R/L·구간·water B/C·f1485 A/B 판정은 수정하지 않았다.

## 수행한 구현과 확인

[새 qualifier](../../../tests/diagnostics/s11_native_role_qualification.py)는 기존 G0/O2
pin·geometry·raster reader를 재사용한다. CR1 qualifier는 물리 자격 철회와 실용 근사
전용이므로 새 경로의 역할 승격을 그 API에 섞지 않았다. 원본 source path 전체의
hash, exact center edge/fragment, frame, source image와 native RGB 일치,
표시 crop 포함, 응답 scope를 검사한다. 가까운 경로나 다른 frame으로 옮기지 않는다.

후속 연구 후보의 입력은 각 G0 관측 column에서 Y−5/Y+5 중심의 **7×7 원본 RGB**다.
49개 픽셀이 모두 visible인 patch만 쓸 수 있고 padding·보간·재축소는 없다.
양쪽에 적어도 하나의 완전한 patch가 있어야 입력 가능하다. 순수 재질 분류 입력이라는
주장은 하지 않는다. 기존 25×11 R/L의 가용성/판정을 다시 계산하거나 완화한 결과도 아니다.

| Subject | 완전한 upper/lower patches | 실제 입력 union pixels, upper/lower | 경로 접촉·교차 pixels, upper/lower | 경로의 미검토 X 범위 pixels, upper/lower |
|---|---|---|---|---|
| N1 | 25 / 25 | 235 / 235 | 0 / 0 | 0 / 0 |
| N2 | 7 / 7 | 109 / 109 | 2 / 2 | 45 / 45 |
| N3 | 19 / 19 | 181 / 181 | 0 / 0 | 43 / 43 |

각 subject 내부 upper/lower 입력 교집합은 0이다. 그러나 **N1/N2 사이에는 90 pixels가
공유**된다. 이 둘을 별도 학습/검증 집합에 넣을 수 없다. 인접 patch의 중복 입력도
각 side에서 각각 N1 990, N2 234, N3 750 pixel uses로 기록했다. 독립 label 수는
patch 수가 아니라 fragment 수다. N2의 접촉·교차와 N3의 경로 밖 문맥은 유지하며,
이 pixels를 가스·Foam의 dense truth로 만들지 않는다.

- 새 focused tests 16개와 기존 G0 tests 21개, **총 37 PASS**.
- 실제 CLI를 `/private/tmp`에서 실행해 15,532-byte qualification을 생성했다.
- 별도 NumPy slice/usage raster 계산으로 세 경로·여섯 side의 전체 footprint,
  crop/mask 분모·입력 재사용·경로 교차·N1/N2 교집합을 대조했다.
- [검증 기록](../../50-diagnostics/s11/2026-10-13-native-role-qualification/verification.json)에
  명령·source hash·결과 hash를 보존했다. 생산 source에는 변경이 없다.

## 검토 가능한 다음 선택

[G1 사전 연구 제안](../../50-diagnostics/s11/2026-10-13-native-role-qualification/g1-pilot-proposal.json)은
입력 정보로 외부 표면/내부 변화를 구분할 수 있는지 **한 번만 제한 학습**하는 범위다.
기존 고정 DINOv2 유사도 비교의 재시도나 생산 classifier 채택이 아니다.

| 항목 | 제안하는 고정 범위 |
|---|---|
| Head | 공유 valid 3×3 Conv 3→8→8→4, 앞 두 층 ReLU; upper/lower별 평균을 순서대로 연결한 8→2 linear. 총 1,118 parameters |
| 학습 단위 | N1 외부 표면 / N2 내부 변화, fragment당 동일 가중치 cross entropy. RGB patch에 개별 정답을 붙이지 않음 |
| 전이 점검 | N3만 최종 1,000 step 후 한 번 평가. 이미 노출된 다른 영상의 positive probe이며 blind test가 아님 |
| 학습 조건 | seed 20261013 하나, CPU float32 2 threads, Adam lr 0.001, full-batch 1,000 steps, augmentation·사전학습·threshold 보정 없음 |
| 비용 상한 | 10분, peak RSS 1 GB, 임시 32 MB, 보존 6 MB; 기존 전체 workspace 3 GB 제한 유지. 기존 환경 재사용, 새 설치·download 없음 |
| 결과 해석 | N1/N2 fitting은 효능 근거가 아님. N3도 맞아야 제한된 노출 자료의 positive transfer로만 기록. 독립 internal/구조·반사 대조군 부족 때문에 **이 모집단으로 full G1 PASS는 불가** |
| 중단 | fit 실패, N3 오판/unknown, 입력·resource 오류를 기록하고 고정 시도 종료. seed/crop/offset/head 크기를 바꿔 재시도하지 않음 |

다른 선택은 **새 source의 native internal/구조·반사 대조군을 먼저 검토**하는 것이다.
이미 닫힌 R/L·구간·B 판정을 다시 묻는 것이 아니라 아직 대응이 없는 새 경로 단위가
필요하다. 어느 선택도 현 단계에서 O2/V5, Oil 소비, Foam raw-front/episode 수용이나
FIELD PASS를 만들지 않는다. 이 기록 작성 시 학습은 실행하지 않았다.

## 재현과 정리

```bash
<repo>/.venv/bin/python -B <repo>/tests/diagnostics/s11_native_role_qualification.py \
  --root <repo> \
  --reply <repo>/docs/50-diagnostics/s11/2026-10-13-native-role-qualification/review-reply.json \
  --output <new-managed-work>/qualification.json
```

[artifact lifecycle](../../40-operations/experiment-artifact-lifecycle.md)에 따라 새 run을
시작한 후 실행한다. 기존 출력은 덮어쓰지 않는다. 이번 run은
`s11-native-role-qualification-20261013-001`이며 compact 결과를 위 단일 추적 위치로
이동했다. 원본 이미지·영상·G0 readout·환경·모델을 복제하지 않았다. main worktree
하나만 확인했고 새로운 worktree나 병합 대상은 만들지 않았다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: 새 detector 효능/실패 원인은 미평가. N3는 기존 원시 경로의 역할 대응만 새로 확인하며, component-to-front 손실의 생산 복구나 이후 손실을 주장하지 않음.
- Logic-map impact: NONE — 오프라인 human qualification과 prospective input 검증만 추가. 실행 detector·candidate·schema·publication 경로 변경 없음.
- Failure-registry impact: NONE — 기하를 정답으로 승격하지 않고 새 사용자 역할 대응을 보존함. 공유 픽셀·불충분한 독립 대조군을 명시하며 새 실패 family나 성공한 repair를 주장하지 않음.
