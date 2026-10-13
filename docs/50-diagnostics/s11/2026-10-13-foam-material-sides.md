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
테스트 **22 passed**. 실제 추론 결과는 고정 실행 후 이 기록에 연결한다.
이 검증은 물리적 구분·Foam raw 복구·Windows 성공의 증거가 아니다.

## Detector Governance

- Logic-map nodes: `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: existing source evidence places the sample4 raw-upper loss before episode assembly; this comparison has no selected physical front and cannot establish a new field cause. Missing side support and saved RGB are input unavailability, not correct rejection.
- Logic-map impact: NONE — separate offline material-side observation reuses existing rasters and the pinned encoder without changing the detector, authority, lifecycle or publication.
- Failure-registry impact: NONE — input qualification and pre-score preparation do not establish a new failure class. Appearance transition, copied patterns and exposed references remain limitations rather than physical authority.
