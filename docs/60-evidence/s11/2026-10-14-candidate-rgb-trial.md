# Candidate-local RGB 입력과 고정 비교

현재 상태와 다음 행동은 [Work Plan](../../00-project/work-plan.md)이 소유한다.
이 기록은 [고정 후보 계약](../../20-architecture/s11-contextual-role-observation-design.md#candidate-local-rgb-compatibility-successor)의
실제 입력 준비와 단일 실행을 다룬다. 기존 native-surface 학습 결과를 바꾸거나
후보 허용을 native 경로·주변 픽셀의 물리 라벨로 확장하지 않는다.
기존 모델의 rim 실패는 유지한다. 후속 [Windows 비교용 로컬 준비](#windows-comparison-local-preparation--2026-10-16)는
같은 가중치를 실제 Oil 후보 자격 조건에 연결한 별도 opt-in 범위다.
[Windows 비교 결과](#windows-rgb-result--2026-10-16)는 BASE 관측 전량 소실로
**REGRESSION / NOT_ADOPTED**로 종료했다. review-006은 미검토로 보존하며,
그 답변을 후보 종료나 다음 Local XY 준비의 전제조건으로 삼지 않는다.

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

## Sample3 A/B 후보 허용 수신과 입력 점검

사용자의 **“모두 허용”**을
[두 대표점의 실용적 허용](../../50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/acceptance.json)으로
기록했다. 원래 질문 packet은 변경하지 않는다. 다른 36개 후보, native 경로,
정확한 픽셀 정답·허용 오차, 프레임 사이 움직임에는 전파하지 않는다.

[고정 점검 계획](../../50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/qualification-plan.json)은
기존 재사용 CLI의 `--source-candidate-manifest`에서 실행한다. Recipe 원본 bytes와
관련 geometry/preprocessing 소스 5개가 archive pin과 같음을 확인했다. 파싱한
geometry와 detector settings도 저장 당시 runtime과 같다. 당시 runtime의
`UNKNOWN_REVIEW`와 Recipe의 `AUTO` 초기 상태 차이는 이번 공간 입력 점검에서
실행하지 않는 부분이다. Crop·glare 계산과 기존 7×7 patch reader를 재사용하며,
저장된 path/대표점의 밝기·가시성 band 16개와 먼저 비교한다.

판정 범위·source/frame/index/hash·누락/중복·이웃 후보와 가시성 변경 방어를
검증한 관련 테스트 97개가 통과했다. 이 단계는 새 모델 학습·점수 비교가 아니며,
이전 모델의 rim 실패와 기존 판정 정밀도는 유지한다.

`566f1d0`에서 고정한 후 `/private/tmp`에서 절대 경로 CLI를 실행했다.
[결과](../../50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/qualification.json)는
**SCOPED_CANDIDATES_QUALIFIED_INPUT_INCOMPLETE**이다. 밝기·가시성 band 16개가
모두 저장값과 일치했다. A는 상/하 각각 완전한 7×7 patch 95개를 확보하지만,
B는 상단 0개·하단 95개다. B의 실용적 허용은 유지되며 입력 부족을 오판정이나
성공적 거부로 세지 않는다. 전체 38개 중 30개 입력이 가용하고 8개가 부족하다.

| 촬영원 | 대응/실용적 허용 후보 | 반대 후보 |
|---|---:|---:|
| sample4 | 7 | 6 |
| 공개 미소냉동 | 4 | 1 |
| sample3 | 2 | 0 |

전체 기존 187개와 새 38개, 총 225개 기록/Oil 220개를 유지하며 후보 대조는
20개다. sample3 C는 지역 구조물 대조이며 후보 단위 라벨로 확대하지 않았고,
D는 계속 판별 불가다. 세 촬영원 모두에서 양·음성을 검증했다는 뜻은 아니다.
실행 1.254437 s, peak RSS 214,040,576 bytes, 결과 101,106 bytes. 관리 실행
`s11-oil-candidate-source-qualification-20261014-001`은 결과 하나만 canonical
위치에 보존하고 동일 사본을 제거했다.

다음 [상단 검토 계획](../../50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-review-plan.json)은
유일하게 입력이 부족한 허용 후보 B의 원래 upper strip만 보여준다. 판정 대상은
이미 허용된 유면 대표점이 아니라, 그 위에서 마스크가 제거한 영역의 물리적 역할이다.
변경 없는 glare와 digital-overlay/saturation 영역의 겹침을 기록한다. 코드의
분류 원인과 물리적 타당성은 다르므로 대체 마스크나 threshold는 적용하지 않는다.

`ce8e61f`에서 고정한 후 실행한
[검토 화면](../../50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-review.png)과
[결합 결과](../../50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-review.json)는
qualification의 RGB·가시성 배열 hash와 patch 의존성에 일치했다. 원래 upper strip
X823:848/Y215:226의 275픽셀 중 effective 밖은 0개, glare로 제거된 것은 225개,
남은 가시 픽셀은 50개다. 제거된 225개 모두 기존 `_digital_overlay_mask`와 겹치며
saturation과 겹치는 픽셀은 0개다. 이는 표시선 억제 분기의 기여를 확인하며,
해당 영역이 실제 표시선·반사라는 물리 판정을 제공하지 않는다. 다른 광학 분기와
중복되는 기여를 별도로 배제했다는 주장도 하지 않는다.

같은 원본 문맥과 마스크 표시를 나란히 놓고, 동일한 25×25 native 영역을 화면에서만
10배 확대했다. 원본 문맥·표시 영역·설명 모두 화면에 들어감을 직접 확인했다.
판정은 **AWAITING_UPPER_REGION_ROLE**이다. 기존 노란 Oil 대표점의 허용을 다시
묻지 않으며, 이 지역의 유체/거품·반사/구조물·혼합·판별 불가 역할만 필요하다.

실행 0.080230 s, peak RSS 107,905,024 bytes. 관리 실행
`s11-source-upper-mask-review-20261014-001`은 PNG 122,489 bytes와 JSON 7,361 bytes만
canonical 위치에 보존하고 작업 사본 둘을 제거했다. 관리 실행 35개 오류 0.
새 모델 호출·학습·대체 마스크·생산 변경·Windows 실행은 모두 0이다.

## Windows comparison local preparation — 2026-10-16

Cost-first의 Windows regression과 review-005 종료 후, 승인된 두 번째 비교를
준비했다. `--initial-full-observation --oil-candidate-rgb`로 ⑥을 실행하고
④ FULL+ON v2와 비교한다. Cost-first/Local XY는 OFF이며 기본 실행은 그대로다.
후보 판정·범위와 새로운 consumer는 [비교 설계](../../20-architecture/s11-physical-interface-evidence-repair-design.md#candidate-local-rgb-windows-comparison)에 고정했다.

기존 실험은 후보별 오프라인 판정만 했으므로, 런타임의 `OilCandidateRgb`는
고정 추론과 annotation만 담당한다. 실험 실행기의 학습·과거 자료 의존성을
제품에 가져오지 않는다. 6,594-byte 고정 가중치의 runtime copy는 package resource로
포함되며 SHA-256은 `8daffcdff5a59f6c8b2212c3e41aa911d676ac391d152a23857bd65d185636db`다.
역사 evidence copy는 보존한다. Torch·추가 다운로드·학습·cutoff 변경은 없다.

현재 프레임 projector는 기존 raw Oil 후보를 지우거나 점수를 바꾸지 않고 RGB
판정·floor/ceil 입력 hash/patch 수/logits를 붙인다. 기존 `candidate_is_eligible`이
완료 Oil 처리에서 추가 조건을 소비한다. COMPATIBLE만 이 조건을 통과하며
UNKNOWN/UNAVAILABLE/OPPOSED는 통과하지 않는다. 모델 허용이 기존 hard veto,
phase/owner/selection 조건을 무효화하거나 새 좌표를 만들지는 않는다. 동일 GUI
factory의 preview/analysis/preflight/redetection 경로와 detector/resolver 버전에
옵션을 전달했다. 현재 프레임 legacy 좌표와 최종 sequence/CSV는 구분한다.

기존 입력 182개 Oil 후보를 재사용한 계산 검증에서 **165 available 판정 전부 일치,
17 unavailable 유지**, 입력 patch hash/개수와 floor/ceil variant도 일치했다.
logit 최대 절대 오차는 `6.430396814138817e-6`으로 기존 `1e-4` 범위 안이다.
공유 strip convolution은 독립 patch 계산과도 일치한다. **f1140 idx7/10/22의
rim 오수용 3건도 그대로 재현**되며 이를 성공이나 보정된 확률로 바꾸지 않는다.

| 고정 로컬 입력 / 요청 창 | 행 | v2 Oil | RGB Oil | 새 출력 | 소실 | 양쪽 숫자 Y 변경 | 숫자 Foam |
|---|---:|---:|---:|---:|---:|---:|---:|
| base_sample_1 / 0–14.4 s | 30 | 12 | 7 | 2 | 7 | 3 | 0→0 |
| sample4 내부 ROI / 0–56 s | 113 | 16 | 12 | 9 | 13 | 3 | 76→76 |

기존 initial-FULL 비교의 ROI/2fps/static preparation 및 전체 AnalysisPipeline →
bundle/CSV/report 경로를 재사용했다. 이 로컬 FULL 초기값은 기계적 비교 조건이며
물리 정답이 아니다. 143개 기준 행·phase·events·raw hash와 report(생성 run_id만
제외)는 보존된 v2와 일치했다. RGB annotation만 제외하면 양쪽 raw 후보·현재
좌표·Foam 입력도 정확히 같다. 최종 숫자 Oil은 항상 같은 프레임의 COMPATIBLE
선택 후보 Y 및 CSV와 일치한다. 최종 Foam 7개 필드는 143행 전부 같으며,
sample4의 FULL/NONE debug 비교도 두 모드의 rows/phase/events/report/raw 및 RGB
annotation이 일치한다. 변경된 전체 행은 base 29/sample4 25이며 물리 정확도는
모두 NOT_EVALUATED로 남긴다. 숫자 감소 자체는 유효성 판정이 아니다.

**169개 서로 다른 테스트 통과**: RGB/GUI/관측 비교 35개와 넓힌 resolver,
initial-FULL, facade/cutover, Foam 통합, packaging 검사 140개 중 중복 6개를
제외한 수다. 가중치 누락/변조, non-repo cwd, 입력 부족/변형 불일치, 기본 OFF,
기존 veto 보존, 정확한 선택 좌표와 GUI 네 경로를 확인했다. 실제 GUI entry의
`--help`에도 새 옵션과 cost-first 동시 사용 금지가 표시된다.

관리 실행 `sample/output/s11-candidate-rgb-windows-prep-20261016-001`은 CLOSED이며
`evidence/`에 5개 파일, 1,118,712 bytes를 보존했다. FULL 중복은 동등성 확인 뒤
제거했고 임시 bundle/cache/작업용 plan도 정리했다. 관리 실행 80개 오류 0이다.

| 보존 경로 | SHA-256 |
|---|---|
| `frozen-model-verification.json` | `557ae984e206bd8b4de42ee9fa88bac71924be6d4eed4667350c6b362f22c273` |
| `verification.json` | `0994d2a4a2c0c5acc59d321fac68c95532d14d6cf0ba8d526130d1e7ae6f3fc7` |
| `none/base_sample_1/comparison.json` | `ad0c0b5781cf9080f166716fae342532a6a69151fb9f69b483780190411f3f61` |
| `none/sample4/comparison.json` | `14095b41e264606e885069870f08f40c8ed5eb4a453959e5d6ade782003e9955` |
| `implementation.patch` | `4c950378c1c6617545ae0965e77d66b85a7630b7a6e58354fc51c496fca8e0f0` |

로컬 전달 당시 Windows 비교는 미실행이었으며 [실행 절차와 짧은 프롬프트](../../40-operations/s11-current-windows-field-qualification.md#priority-2-candidate-rgb-comparison)를 제공했다.
review-004/005의 복수 허용·실용적 근사를 재사용하고 기존 O2/FIELD 상태를 유지한다.

## Windows RGB result — 2026-10-16

**REGRESSION / NOT_ADOPTED.** 사용자가 전달한 Windows 실행·CSV 요약을
수신했다. 원본 영상, CSV/JSONL과 review packet은 Windows에 있으며 Mac에서
직접 검사하지 않았다. 기준 ④의 최종 BASE 303행이 ⑥에서 모두 사라졌고,
이미 사용자에게 허용된 계면도 출력되지 않는다. 이는 실제 계면이 없다는 새
불확실성이 아니라 기존 판정에 대한 관측 손실이다. 전체 303개가 모두 정확한
계면이었다는 뜻도 아니다. 임계값 완화, 재학습, 재실행은 하지 않는다.

### Reported execution and final output

- 기준: `oil_level_analysis_22-3_initial_ON_v2_20261015_171421`, Windows의
  `0.windows_diagnostic/bundle/`에 보존된 ④를 재사용.
- 후보: `oil_level_analysis_22-3_initial_ON_v2_candidate_rgb_20261016_122107`,
  `sample/output/`에 보존된 ⑥. 전달 구현은 `d7e19ba`, 문서 전달 HEAD는 `1f0a00e`다.
  이번 회신은 실행 소스 SHA 원문을 포함하지 않으며, 보고된 resolver 접미사는
  `+initial-full-observation-v2+candidate-rgb-v1`이고 cost-first는 없다.
- 동일 영상/Recipe bytes와 세션 7개 필드의 일치가 보고됐다. 480–780초,
  2fps, FULL debug, BASE FULL/Accum EMPTY다. 실제 Recipe의 개별 Artifact/ROI
  값은 이 회신에 없으며 일치 확인을 다시 요구하지 않는다.
- `OpenCvPhaseDetector(initial_full_observation=True, candidate_rgb=True)`를
  사용하는 `AnalysisPipeline` / `AnalyzeVideoUseCase`의 **headless 실행**으로
  보고됐다. 약 24.8분은 단일 실행 시간이다. 실제 GUI 조작·패키지 검증으로
  바꾸어 기록하거나 GUI만을 위해 다시 실행하지 않는다.

다음은 전달된 최종 숫자 출력 집계다. BASE/Accum 각각 601행이며,
[검토 정답](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)의
구간을 앞 포함·뒤 제외(마지막 780초 포함)로 분리했다.

| Glass / 구간 | 표본 | ④ Oil | ⑥ Oil | ④ Foam | ⑥ Foam |
|---|---:|---:|---:|---:|---:|
| BASE FULL_PREFIX 480–550 | 139 | 3 | 0 | 0 | 0 |
| BASE DRAIN 550–652 | 205 | 170 | 0 | 0 | 0 |
| BASE REFILL 652–674 | 43 | 39 | 0 | 0 | 0 |
| BASE FULL_TRANSITION 674–675 | 2 | 0 | 0 | 0 | 0 |
| BASE FULL_SUFFIX 675–780 | 211 | 91 | 0 | 0 | 0 |
| BASE OUTSIDE | 1 | 0 | 0 | 0 | 0 |
| **BASE 합계** | **601** | **303** | **0** | **0** | **0** |
| Accum EMPTY 480–653 | 346 | 0 | 0 | 0 | 0 |
| Accum ENTRY_SPLASH 653–672 | 37 | 4 | 0 | 7 | 7 |
| Accum FOAM_LAYERED 672–680 | 16 | 10 | 3 | 11 | 11 |
| Accum POST_FOAM 680–700 | 41 | 0 | 0 | 0 | 0 |
| Accum DRAIN 700–780 | 160 | 22 | 0 | 22 | 22 |
| Accum OUTSIDE | 1 | 0 | 0 | 0 | 0 |
| **Accum 합계** | **601** | **36** | **3** | **40** | **40** |

BASE 후반 FULL의 91개 비유면 숫자가 없어졌지만 하강/회복의 209개 출력도
전부 사라졌다. 후자를 정확도 209건 손실로 세지는 않아도, 이미 허용된 관측의
소실과 전체 움직임 부재만으로 미채택 결론은 충분하다. Foam 불변과 episode/
confirmed count 동일은 사용자 보고이며 표는 숫자 수를 확인한다. 최종 모든
필드의 로컬 비교는 아니다. 이전부터 존재하던 ENTRY_SPLASH 7행 / DRAIN 22행의
Foam 출력이 정답이 됐다는 의미도 아니다.

### Reused judgments and unresolved summary details

1. review-004는 여섯 프레임의 **실용적 허용과 불확실성**으로 재사용한다.
   f15884의 409/396, f15908의 418/413.5, f15932의 411은 허용된 대안이다.
   f15872의 404.5 선호와 f15920의 413/416 선호를 기존 433.5/425의 확정
   `non_interface` 라벨로 바꾸지 않는다. f15896은 양쪽 모두 빈 값이며 이미
   허용한 417/419/407 관측이 계속 누락된다. 후보별 RGB 최초 거부 stage와
   OPPOSED/UNAVAILABLE의 정확한 분해는 이 요약만으로 확정하지 않는다.
2. 721/723초의 `Y311/309/312/317` 및 `Y329/353/356`은 Glass·좌표계·최종 행
   연결이 불명확하다. 기존 ④ BASE f17287@721.012의 CSV는 **Y694**, f17335@
   723.014는 **빈 값**이었다. 따라서 721초 제거는 BASE 전체 빈 출력과 양립하지만,
   **723초 BASE의 새 개선**은 성립하지 않는다. 771초 양쪽 UNKNOWN 보고는 유지한다.
   이 충돌은 기존 기록을 덮어쓰거나 RGB 종료를 위한 전체 trace 재분석 사유가 아니다.
3. `BASE COMPATIBLE=0`과 `eligible 8235→1`은 같은 수라고 확정할 수 없다.
   Accum의 `7790→1046`도 원시 필드 정의·분모가 없는 요약이다. 후보 판정 수와
   다른 단계 eligibility를 혼합하지 않고 **UNRECONCILED**로 남긴다. 최종 CSV
   BASE 0 / Accum 3과 별개이며 모든 BASE raw 후보가 사라졌다고 해석하지 않는다.
4. review-005의 f16076@670.5에서 허용한 482/479.5 소실은 추가 손실 근거다.
   f17431@727은 ④/⑥ 모두 빈 값이라는 보고를 유지하며 ⑤의 신규 관측과 섞지 않는다.

### Review-006 retained, no required follow-up

Windows `0.windows_diagnostic/data/reviews/review-006/`에 packet-v2, pending/
unreviewed labels, plain/guide 6장과 replies 폴더가 준비됐다고 보고됐다.
새 사용자 회신은 아직 없다. 아래 세 선택 위치와 LVLM 관찰을 분리해 보존한다.

| Accum frame / 시각 | ④ Oil Y | ⑥ Oil Y | 최종 출력 차이 |
|---|---:|---:|---|
| f16184 / 675.0 s | 317 | 498 | 양쪽 숫자, Y 변경 |
| f16208 / 676.0 s | 빈 값 | 485 | 신규 출력 |
| f16232 / 677.0 s | 269 | 444 | 양쪽 숫자, Y 변경 |

이 세 행이 ⑥의 전부라는 집계를 따르면 Accum은 **새 출력 1 / 소실 34 /
공통 숫자 Y 변경 2**, 순증가 −33이다. 이는 전달 수치에서 계산한 분해이며
별도 로컬 CSV 검사 결과가 아니다.

LVLM의 “Foam 하단/바닥 아티팩트”는 미확정 관찰이다. 이 구간의 정답은 상단
Foam과 하단 **Oil/Foam 계면**을 각각 추적하는 것이다. Oil-air가 아니라거나
Foam 아래라는 이유만으로 Oil 오검출이 되지 않는다. 실제 Oil/Foam 경계와 고정
바닥/반사 여부는 다르다. 세 후보에 정답/오검출 라벨을 자동 부여하지 않는다.
RGB 미채택은 이미 성립하므로 추가 강제 선택을 요청하지 않고 packet을 보존한다.
이후 사용자가 직접 답하면 기존 record/history 절차로 해당 범위에만 반영한다.

Cost-first → RGB 두 비교는 종료, 다음은 [Local XY 입력 준비](../../40-operations/s11-current-windows-field-qualification.md#priority-3-local-xy-input-preparation)다.
O2 OPEN / FIELD FAIL, 기본 detector, FULL 전환 미해결은 그대로다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F02`, `S11-F09`, `S11-F10`.
- First harmful stage: the Windows receipt establishes whole-BASE final observation loss, including previously allowed interfaces. RGB eligibility is the changed consumer, but exact per-candidate OPPOSED/UNAVAILABLE/other rejection counts and earliest loss are not established by the contradictory summary. Historical B input loss and reviewed rim false acceptance retain their narrower evidence above.
- Prior mechanisms reviewed: old CR1 category collision and all-four public sign failure; B practical acceptance; original native-head N3 loss; source-qualified candidate bindings and exact floor/ceil support.
- Difference from prior failures: one fixed native RGB candidate-compatibility trial changes input information and supervision, with sample4-only fit and exposed public transfer. It does not retry native external-surface labels, tune the failed role threshold or choose a new production winner.
- Existing feature coverage: historical and local preparation inputs remain frozen above. The received Windows pair reports matching video/Recipe/session, FULL debug, initial BASE FULL/Accum EMPTY, observation v2 with RGB only in ⑥; individual ROI/template/static-input values are not supplied. The existing scope-aware constructor and current GUI/sequence owners are unchanged. No mask repair, retraining or new setup is applied.
- Execution scope: this receipt is documentation-only. Windows reports headless detector/pipeline/use-case execution and completed CSV, not GUI operation; private artifacts were not inspected locally. Earlier 169 tests and local comparisons retain their original scope. No new detector execution, physical labels or field acceptance accompanies this receipt.
- Logic-map impact: NONE — the mapped RGB annotation/eligibility route still matches source; only its returned field disposition and next Windows input task change.
- Failure-registry impact: NONE — no new failure family or accepted detector repair; this checks candidate-level input capability under existing evidence boundaries.
