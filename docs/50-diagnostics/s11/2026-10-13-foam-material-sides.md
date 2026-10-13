# Foam 내부 기준 두 유형의 경계 양측 비교

기준 HEAD: `d7d45094b9d3a797e6b6cfd0f87d834458f49569`.
이 기록은 독립 P5-a 진단의 조건과 결과를 소유한다. 현재 진행 상태는
[Work Plan](../../00-project/work-plan.md), 해석 계약은
[material-side 설계](../../20-architecture/s11-contextual-role-observation-design.md#frozen-material-side-operation)가 소유한다.

## 확정된 입력과 비교 범위

[R 답변](2026-10-13-foam-material-reference/reply.json)은 공개 압축기 f1499의
25×25 영역을 매우 미세한 Foam 내부로 승인했다. [L 답변](2026-10-13-foam-material-reference/coarse-reply.json)의
원문은 “큰 알갱이 Foam 내부 기준으로 사용 가능”이다. 물 A/f1232의
`[938,485,963,510)` 영역에만 해당하며, 기존 불명확한 하단을 재판정하지 않는다.
두 제안·원본·표시 이미지의 bytes는 보존하고 답변을 별도로 연결했다.

한 기준과 닮지 않았다는 이유로 다른 Foam을 비-Foam으로 분류할 수 없다.
두 기준을 합치거나 최대값 하나로 선택하지 않고 각각의 상측·하측 유사도,
하측−상측 차이, 양측 평균을 보존한다. 미세↔큰 알갱이 전환도 Foam 내부에서
발생할 수 있다. 만들어 낸 혼합 이미지의 대조 결과는 실제 장면의 역할 정답이 아니다.

[고정 preflight](2026-10-13-foam-material-sides/preflight.json)는 기존 S2 42개
저장 raster와 공개 압축기 native raster를 사용한다. 모든 중앙열의 가시 Canny
경계 1,335개를 결과와 무관하게 포함한다. 1,184개는 필요한 25×11 양측 지원이
있고, 119개는 지원이 부족하며, 32개는 해당 장면의 저장 RGB가 없다.
RGB 없는 장면은 sample4 f420/f480/f1635이며 회색 이미지를 RGB처럼 만들거나
새로 디코딩하지 않는다. 이용 가능한 sample4 RGB 11개와 기존 grayscale은 일치한다.

R의 공개 영상과 L의 물 A episode는 기준 초기화에 사용한 노출 자료다.
물 B/C는 같은 영상의 대조군이다. sample4/맥주/우유도 기존에 검토된 개발 자료이며,
untouched holdout은 0개다. 큰 알갱이의 독립적인 일반화 성능은 별도 자료 없이
평가했다고 주장할 수 없다. 기존 내부 무늬·rim 위치는 실제 중앙 경계가 없으면
지원 없음으로 남긴다. 구간에 들어온 모든 경계를 정답으로 바꾸지 않는다.

## 재사용과 실행 조건

[실행기](../../../tests/diagnostics/s11_foam_material_sides.py)는 기존 CR1 encoder와
dimension-aware padding/weights를 그대로 사용한다. CR1의 기존 역할 bank와
joint descriptor는 고정 산출물이므로, 새 Foam 내부 의미와 per-side 연산을
별도 offline 진입점에 둔다. 새 경계 생성기·모델·생산 경로는 없다.

기존 ROI 전체를 정사각형 padding 후 224로 변환하는 full/local 조건을 고정한다.
source/token 크기, 변환 좌표와 양측 token overlap을 모두 기록한다. 큰 ROI에서는
25 native pixels가 한 token보다 작을 수 있으며, 특히 full token은 영역 밖의
맥락도 포함한다. 가중 평균이 순수한 물질 분할이라는 뜻은 아니다.

최대 1,247회 forward, 계산 600초, forward당 10초, peak RSS 2 GB,
압축 결과 6 MB와 전체 workspace 3 GB 한도를 고정한다. 실제 encoder를 거치는
remote-pixel 대조와 내부 appearance 혼합 대조를 먼저 실행한다. 핀·geometry·대조·자원
실패 시 중단하며, 점수를 본 뒤 reference/crop/scale/cutoff를 바꿔 재시도하지 않는다.

준비 검증: 신규 양측 의미·결측·mask/좌표·경계 목록 테스트와 기존 transfer geometry
테스트 **22 passed**. 저장소 밖 cwd에서 실제 `--validate-only` 진입도 통과했다.
이 검증은 물리적 구분·Foam raw 복구·Windows 성공의 증거가 아니다.

## 고정 실행 결과

실행 HEAD는 `48cf500f44893c7ef39253f1a05bc6bc59ed53a9`다.
[전체 점수](2026-10-13-foam-material-sides/readout.json.gz)와
[검증·구간/guide 연결](2026-10-13-foam-material-sides/verification.json)을 보존했다.
**CLOSED_WITHOUT_PROMOTION**: 두 내부 기준의 승인은 유효하지만, 이 고정 연산으로
물리적 상단 선택·비-Foam 거부·유형별 일반화가 입증되지는 않았다. 기존 CR1의
`SCOPE_LIMITED_USEFULNESS`는 이 별도 결과로 덮어쓰지 않는다.

| 관측 | 의미와 한계 |
|---|---|
| 공개 압축기 Foam 포함 구간 Y332/336에서 full R 하측−상측은 +0.131698 / +0.093342. Oil 포함 구간 Y428/431/433은 −0.083270 / −0.073617 / −0.068155 | 두 구간의 방향 차이는 남는다. R 초기화 장면이며 각 Canny 경계의 물리적 정답을 판정한 것은 아니다 |
| 물 A/Foam 포함 구간 Y477의 local L 하측 유사도 0.954765. no-Foam B/C 포함 구간 Y485/488/491은 0.952506 / 0.970490 / 0.962316 | 높은 L 유사도가 Foam 층 존재를 고유하게 나타내지 않는다. 모두 같은 영상의 노출 맥락이며 class 정확도는 계산하지 않는다 |
| 큰 알갱이 위 / 미세 알갱이 아래의 구성 대조에서 local 하측−상측: R +0.605302, L +0.220212 | Foam 내부 appearance 전환도 두 기준에 모두 양의 방향 차이를 만들 수 있다. 단일 부호나 두 기준 동의가 상단 역할을 증명하지 않는다 |
| sample4 상단 포함 구간의 유일한 중앙 경계 Y813: 상측 236/275, 하측 275/275 지원 | 39픽셀이 기존 effective mask 밖이다. glare 때문이 아니다. 이번 직사각형 지원 요구가 점수 계산 전에 입력을 잃으며, 기존 detector가 이 경계를 제거했다거나 틀린 경계라는 뜻이 아니다 |
| 세 내부 무늬 guide Y833/837/838의 정확한 중앙 Canny 연결 없음 | 인접 경계로 옮겨 맞추지 않았으며 내부 무늬 억제 성과는 평가 불가다 |

R은 token당 14.25 native pixels, L은 51.875다. 승인한 25픽셀 폭은 encoder
canvas에서 각각 약 24.56 / 6.75픽셀이고, 물 A Y477 양측 token 가중치 overlap은
0.767689다. 서로 다른 native pixel을 샘플링해도 encoder에서 상당한 정보를
공유한다. 이는 고정된 입력 계약의 해상도 한계이며 실제 큰 알갱이 자체를 모델이
구분할 수 없다는 일반적 결론은 아니다. 이번 점수를 보고 ROI/scale를 바꿔 구제하지 않는다.

43개 장면과 1,335개 경계를 모두 보존했다. 1,184개에서 4,736개
`경계 × full/local × R/L` 쌍이 측정됐고, 119개는 지원 부족, 32개는 RGB 없음이다.
기준 장면인 R은 13개 중 9개, L은 97개 중 94개 경계를 측정했지만, 이 수치는
각 Foam 유형의 검출률이 아니다. 실제 fine/large 내부 전환과 독립적인 유형별
상단·반대 사례의 물리적 정답은 여전히 **NOT_EVALUATED**다.

검증은 142개 입력/source 핀, runner의 159개 backend 핀, 전체 좌표·지원 수,
모든 점수 쌍의 유한성·차이·평균, 가중치 질량·중복 및 원본 reference 결합을 확인했다.
실제 encoder remote-pixel 대조와 순서 교환 대조도 통과했다. 이는 연산의 일관성이지
역할 분류의 성공이 아니다. 1,242회 forward, 계산·모델 로드 합계 56.97초,
peak RSS 880.4 MB, 압축 점수 342,536 bytes다. 디스크 읽기/preflight와 전체
앱·영상 decode·Windows 비용을 포함하는 측정은 아니다.

## 다음 설계가 해결해야 할 경계

이번 결과는 reference 하나를 추가하거나 유사도 임계값을 정할 근거가 아니다.
다음 역할 관측안은 (1) 실제 상단에서 이용 가능한 물리적 양측 지원,
(2) source/encoder 해상도와 token 공유, (3) Foam 내부 appearance 전환 및
no-Foam 맥락을 함께 다뤄야 한다. 기존 native path/support owner와 저장 raster를
먼저 재사용하고, 이 고정 연산의 crop/scale/reference/cutoff 재시도를 별도 이름으로
반복하지 않는다. 현재 자료만으로 보정된 class·상단·부재·episode 결정을 발행하지 않는다.
R/L 승인 영역은 후속 입력으로 보존하되 독립 평가 자료로 다시 세지 않는다.

관리 실행은 준비 `material-sides-preflight-20261013-001`과 본 실행
`material-sides-20261013-001`이다. 입력 이미지·모델을 복제하지 않았고, dense token은
보존하지 않았다. 재현에는 위 frozen preflight와 실행기를 사용한다. 검토 후 남긴
자료는 전 경계 점수, 검증 요약과 기존 입력 참조이며 임시 plan/선택표는 정리한다.
생산 source·기존 실험 결과·Windows field 판정은 변경하지 않았다.

## Detector Governance

- Logic-map nodes: `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: existing source evidence places the sample4 raw-upper loss before episode assembly; this comparison has no selected physical front and cannot establish a new field cause. Missing side support and saved RGB are input unavailability, not correct rejection.
- Logic-map impact: NONE — separate offline material-side observation reuses existing rasters and the pinned encoder without changing the detector, authority, lifecycle or publication.
- Failure-registry impact: NONE — this completed fixed material-side comparison supplies counterexamples and unavailable-input limits within existing failure classes. It does not define a new detector mechanism or field failure; the exact frozen operation is closed without a threshold/geometry retry.
