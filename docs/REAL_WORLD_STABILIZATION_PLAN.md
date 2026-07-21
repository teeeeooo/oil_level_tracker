# Rotary Oil Level Tracker Real-World Stabilization Plan

## 1. 문서 목적

이 문서는 실제 compressor 영상과 Windows Workbench를 사용하면서 확인된 UI, 분석 lifecycle, 결과 graph와 detector 정확도 문제를 관리한다.

전체 Phase 상태와 우선순위는 [`UX_IMPROVEMENT_BACKLOG.md`](./UX_IMPROVEMENT_BACKLOG.md)를 따르고, Result Review Viewer의 상세 데이터·화면 계약은 [`RESULT_REVIEW_VIEWER_PLAN.md`](./RESULT_REVIEW_VIEWER_PLAN.md)를 따른다.

이 문서는 Phase 2C-3 완료 후 Phase 2C-4 공유용 결과 영상으로 바로 진행하지 않고, 실사용 안정화와 detector 정확도 검증을 먼저 수행하기 위한 실행 계획이다.

## 2. 기준 시점

- 작성일: 2026-07-21
- Phase 2C-3 PR: #27 `feat: add user truth annotations and regression fixtures`
- Phase 2C-3 PR exact head: `7cf152083b72394a90ae1118a94084c32b0c9033`
- Phase 2C-3 main merge SHA: `c9f130f58d51c79b29cf3594a0cbd44b3a570d78`
- Phase 2C-3 canonical validation: Python 3.13 및 3.14에서 각각 `485 passed`
- S1 PR: #29 `feat: add detector benchmark foundation`
- S1 PR exact head: `73edfedb61948e2ff0431ed31075db1ac5d682ef`
- S1 main merge SHA: `ced132f5927554c658a9993155a8d4afa121b011`
- S1 focused validation: Python 3.13에서 `66 passed`, failure/skip 없음
- S1 canonical validation: Python 3.13 및 3.14에서 각각 `542 passed`, failure/skip 없음

Phase 2C-3으로 외부 `.oiltruth` 사용자 정답 세트와 regression fixture export가 확보됐고, S1으로 같은 자료를 읽고 현재 detector를 정량 평가하는 benchmark foundation이 확보됐다. 이후 detector 변경은 S1 결과를 baseline 근거로 사용한다.

## 3. 최상위 원칙

### 3.1 Detector 정확도가 최우선 제품 문제다

실제 영상에서 흰색 Foam과 투명 오일 교반·아지랑이를 구분하지 못하고, 유면 높이 추적도 안정적이지 않다.

단, 실제 사용자 정답 없이 threshold만 조정하지 않는다.

순서:

1. 사용자 정답 fixture 수집
2. 현재 detector baseline 측정
3. 실패 유형 분리
4. algorithm 변경
5. 같은 fixture dataset 재검증
6. 실제 compressor 영상 수동 검증

### 3.2 Detector 구현 선택 기준

S1 benchmark와 S5 detector 개선에는 다음 기준을 적용한다. 이 기준은 기존 작업 순서를 변경하지 않고 구현 선택과 acceptance를 구체화한다.

- 대규모 학습 모델은 기본 범위에서 제외한다.
- 추가 model checkpoint와 GPU runtime dependency를 도입하지 않는다.
- OpenCV·NumPy 기반의 경량 알고리즘을 우선한다.
- threshold와 scoring weight는 단일 영상이 아니라 여러 fixture category의 benchmark 결과로 보정한다.
- 설정값은 가능한 한 기존 `DetectorSettings`에서 관리하고 serialization, fingerprint와 backward compatibility 대상에 포함한다.
- 한 영상의 성능만 높이기 위한 hard-coded 예외, fixture ID 분기와 파일명 기반 분기를 금지한다.
- 낮은 confidence나 상충 evidence는 강제 유면·Foam 상태로 확정하지 않고 `UNKNOWN_REVIEW`와 review-required 경로로 처리한다.
- 정확도 외에 배포 용량, CPU 처리 속도, 메모리와 Windows one-folder 호환성을 acceptance criterion에 포함한다.
- GPU가 없는 일반 업무용 Windows PC에서 동작해야 한다.
- 학습 모델이 필요하다는 근거가 생기더라도 기존 S5 범위를 자동 확장하지 않고 별도 설계·승인 작업으로 분리한다.

### 3.3 UI architecture 규칙을 유지한다

`src/oil_tracker/ui`는 `cv2`와 `numpy`를 직접 import하지 않는다.

Phase 2C-3에서 presentation adapter를 추가하고 기존 직접 import를 제거했다. 현재 `src/oil_tracker/ui/widgets/result_review_canvas.py`만 temporary architecture allowlist로 남아 있다.

이 예외는 신규 구현의 선례가 아니며, Phase 2C-4 전에 제거한다.

### 3.4 사용자 화면 용어를 일관되게 한다

| 기존 사용자 용어 | 변경 사용자 용어 |
|---|---|
| ROI | 분석 영역 |
| ROI 집중 편집 | 분석 영역 편집 |
| ROI 상세보기 | 분석 영역 상세보기 |
| 관찰창 | Glass |
| oil-air | 유면 또는 유면 경계 |
| Foam | 거품. 개발자 화면에서만 Foam 병기 가능 |
| 길이 환산 | 실제 길이 환산 — 선택 사항 |

내부 class명, JSON key, CSV column과 backward-compatible schema 이름은 호환성 때문에 유지할 수 있다.

## 4. 실사용 문제와 개선 방향

### RW-01. Workbench 진행 단계 텍스트 잘림

#### 현상

진행 단계가 단계명과 상태의 두 줄로 표시되며 글자의 위아래가 잘린다.

#### 원인

고정 높이 button에 줄바꿈된 두 줄 text를 표시하며, Windows DPI와 font metric에 따라 필요한 높이가 달라진다.

#### 개선

한 줄로 표시한다.

예:

```text
✓ 영상 선택 · 완료
▶ 설정 점검 · 현재
⚠ Glass 설정 · 확인 필요
```

상세 설명은 tooltip과 status bar에서 제공한다.

#### 완료 조건

- button text에 줄바꿈 없음
- 1280px 폭에서 5단계 표시
- Windows 100%, 125%, 150% DPI에서 clipping 없음

### RW-02. 중앙 영상이 너무 작음

#### 현상

분석 영상 설정, 현재 장면 검출, 영상과 transport가 중앙에 수직으로 쌓여 영상이 작다.

#### 개선

좌측 영역을 상하로 분리한다.

```text
┌ 현재 장면 검출 ┐
│ compact summary │
├────────────────┤
│ Glass 목록      │
│ 추가·삭제·복사 │
└────────────────┘
```

중앙은 분석 영상 설정, 영상 canvas와 transport에 집중한다.

### RW-03. 재생 control이 영상과 겹쳐 보임

#### 판단

코드상 transport는 canvas 아래 별도 layout row다. 실제 겹침은 DPI scaling, minimum size 합계와 시각적 경계 부족에 의한 layout compression 가능성이 높다.

#### 개선

- 전용 `VideoPlaybackPanel`로 canvas와 transport를 묶는다.
- transport를 fixed-height row로 둔다.
- canvas만 stretch한다.
- 명확한 spacing과 border를 둔다.
- GUI geometry test로 widget 교차가 없음을 검증한다.

### RW-04. 기본 설정의 어색한 줄바꿈

#### 현상

`ROI 위치와 크기`가 좁은 form 안에서 다시 줄바꿈되어 읽기 어렵다.

#### 개선

해당 summary section을 제거한다.

기본 설정에는 다음만 둔다.

- Glass 이름
- 분석 포함 여부
- 분석 영역 편집
- 기준선
- 분석 시작 상태
- 판정 방식
- 실제 길이 환산 — 선택 사항

상세 좌표는 분석 영역 편집 dialog 또는 고급 설정에서만 표시한다.

같은 작업에서 word-wrap과 FormLayout label을 일괄 점검한다.

### RW-05. ROI 용어가 사용자에게 불명확함

사용자-facing text의 `ROI`를 `분석 영역`으로 변경한다.

내부 artifact key와 serialization field는 breaking change 없이 유지한다.

### RW-06. 관찰창 용어가 일관되지 않음

사용자-facing `관찰창`을 `Glass`로 통일한다.

기존 profile에서 사용자가 지정한 Glass 이름은 변경하지 않는다.

### RW-07. 거품 가능성 안내 후 수행할 action이 없음

#### 현상

현재 장면 검출에 `거품 영향 가능성을 확인해 주세요`가 표시되지만 사용자가 무엇을 해야 하는지 알 수 없다.

#### 개선

문구를 다음처럼 분리한다.

```text
검출 해석: 거품 가능성이 감지됨
권장 조치: 영상에서 실제 거품인지 확인하세요.
```

Action:

- 분석 시작 장면에 가까우면 `초기 상태 설정으로 이동`
- 결과 검토 중이면 `사용자 정답으로 기록`

현재 장면의 detector 결과를 recipe 초기 상태로 자동 저장하지 않는다.

`판정` label은 `검출 안내`로 변경한다.

### RW-08. 설정 panel 스크롤 중 값이 변경됨

#### 원인

ScrollArea 내부의 `QSpinBox`, `QDoubleSpinBox`와 `QComboBox`가 wheel event를 소비한다.

#### 개선

wheel-safe control을 공통 적용한다.

- mouse wheel은 parent scroll area에 전달
- 값은 keyboard, arrow button 또는 직접 입력으로 변경
- 기본·고급 설정의 모든 wheel-sensitive field에 적용

### RW-09. 실제 길이 환산이 필수처럼 보임

#### 원인

`mm_per_pixel`이 고급 설정에 있으며 미설정 시 항상 validation warning을 생성한다.

#### 개선

기본 설정으로 옮긴다.

```text
실제 길이 환산 — 선택 사항
☐ mm 단위도 함께 표시
   1 px = [      ] mm
```

정책:

- default 미선택
- 미선택 시 warning 없음
- 결과는 px로 정상 생성
- 선택했는데 값이 유효하지 않을 때만 error
- tooltip으로 분석 실행에 필수가 아님을 설명

### RW-10. 분석 progress 100% 후 완료 dialog가 늦게 표시됨

#### 원인

현재 progress는 detector frame loop만 표시한다. 100% 이후 event capture, CSV, graph, snapshot, debug copy, HTML과 atomic finalize가 진행된다.

#### 개선

stage 기반 progress를 제공한다.

1. 영상 분석
2. 이벤트와 판정 계산
3. 결과 이미지 생성
4. CSV와 snapshot 저장
5. graph와 보고서 생성
6. bundle 마무리

Frame 분석 100%를 전체 완료로 표시하지 않는다. Atomic finalize 직후에만 최종 완료 signal과 dialog를 표시한다.

### RW-11. 여러 시점 점검 panel이 작고 영상을 가림

#### 원인

여러 시점 점검이 bottom dock으로 central Workbench를 축소하며, 많은 table column을 작은 높이에 표시한다.

#### 개선

Workbench당 하나의 modeless window로 전환한다.

- 기본 1100×680
- 최소 900×540
- 시점 선택 시 Workbench 영상 seek
- Workbench 영상은 계속 표시
- 실행, 취소와 재점검
- Glass별 요약과 시점별 결과 table resize
- profile 변경 시 stale 처리

### RW-12. Foam과 투명 오일 아지랑이를 구분하지 못함

#### 현재 원인

현재 foam 후보는 grayscale local variance, edge density, 하단 연결성과 component 면적에 크게 의존한다.

투명 오일의 교반·굴절 아지랑이도 variance와 edge density가 높고 하단과 연결될 수 있다. Foam candidate가 하나 생기면 fill state가 Foam 상태로 강하게 바뀌는 구조도 오검출을 확대한다.

#### 개선 후보

- HSV/Lab 밝기·채도·백색도 evidence
- glare와 Foam mask 분리
- variance와 edge density의 단순 OR 제거
- multi-scale texture와 component shape
- temporal persistence와 front 이동 연속성
- 아지랑이 transient/refractive motion 특징
- Foam state 전환 전 minimum evidence gate
- 불확실한 경우 Foam 확정 대신 `UNKNOWN_REVIEW`

Algorithm 선택은 benchmark 결과와 3.2 구현 선택 기준을 따른다.

### RW-13. 유면 검출과 tracking 정확도가 낮음

#### 현재 원인

현재 detector는 Sobel, Canny, Hough와 region contrast candidate 중 frame별 최고 점수를 greedy하게 선택하고 최근 median으로 smoothing한다.

취약점:

- Glass 구조물과 반사선
- 교반 굴절 경계
- 잘못된 이전 candidate가 temporal prior를 오염
- full/empty no-interface 상태의 가짜 line
- single-frame score 고착

#### 개선 후보

- generator 간 candidate consensus
- gradient polarity와 위·아래 intensity model
- 고정 구조물 suppression 강화
- single-frame greedy 선택 대신 temporal candidate path
- confidence-gated tracker update
- tracker prior와 rejected candidate 분리
- no-interface hypothesis를 candidate와 함께 비교
- 낮은 confidence나 상충 evidence에서 `UNKNOWN_REVIEW`

Algorithm 선택은 benchmark 결과와 3.2 구현 선택 기준을 따른다.

### RW-14. Result Review graph 한글이 깨짐

#### 원인

Qt application font는 Matplotlib에 적용되지 않는다. Default DejaVu Sans에 한글 glyph가 없을 수 있다.

#### 개선

공용 Matplotlib font resolver를 추가한다.

우선순위 예:

1. Malgun Gothic
2. Noto Sans CJK KR
3. Noto Sans KR
4. Apple SD Gothic Neo

적용 대상:

- Result Review graph
- 재검출 comparison graph
- HTML report PNG graph

Font를 찾지 못하면 log와 명시적인 fallback 정책을 사용한다.

### RW-15. 결과 graph 용어와 y축이 실제 Glass를 표현하지 못함

#### 문제

- `oil-air`가 사용자에게 노출된다.
- y축이 검출값만 기준으로 autoscale된다.

#### 개선

사용자-facing series는 `유면`과 `거품 경계`로 표시한다.

Graph model에 분석 영역 전체 y축 범위를 추가한다.

```text
top = zero_line_y - analysis_area_top_y
bottom = zero_line_y - analysis_area_bottom_y
```

- 상세 graph는 해당 Glass 전체 분석 영역 사용
- combined graph는 모든 Glass 범위를 포함
- 기준선 0, 분석 영역 위·아래 경계 표시
- 누락값을 0으로 대체하지 않음
- Result Review와 HTML report가 동일한 범위 정책 사용

## 5. Detector benchmark dataset

Phase 2C-3 fixture를 다음 category로 수집한다.

1. 뚜렷한 유면
2. 투명 오일 가득 참
3. 투명 오일 교반·아지랑이
4. 실제 흰색 Foam
5. 반사광·흐림
6. 구조물 수평 경계
7. 빠른 오일 유입·배출
8. full/empty no-interface

Dataset에는 category, 예상 fill state, 유면·거품 truth와 unusable 사유를 포함한다.

Threshold와 scoring 보정은 단일 영상이 아니라 위 category를 균형 있게 포함한 dataset 결과를 기준으로 한다.

## 6. Benchmark 지표

- oil boundary MAE px
- Glass 높이 대비 normalized error
- median, P90과 P95 error
- valid detection coverage
- fill-state accuracy
- Foam precision과 recall
- 아지랑이 장면 Foam false-positive rate
- no-interface false-boundary rate
- event timestamp difference
- detector version과 settings snapshot
- dataset, settings와 run fingerprint
- 이전 baseline 대비 category별 delta

Raw와 smoothed 위치는 별도로 측정한다.

## 7. 새 작업 순서

### S0 — Phase 2C-3 완료

**완료**

- 외부 `.oiltruth`
- confirmed/corrected/unusable workflow
- 사용자 유면·거품 위치와 상태
- 오류 유형과 메모
- 공식 결과와 truth 분리
- regression fixture dataset export
- Qt presentation image boundary

### S1 — Detector benchmark foundation

**완료**

PR #29 `feat: add detector benchmark foundation`로 `main`에 반영했다.

- PR exact head: `73edfedb61948e2ff0431ed31075db1ac5d682ef`
- main merge SHA: `ced132f5927554c658a9993155a8d4afa121b011`
- focused validation: Python 3.13에서 `66 passed`, failure/skip 없음
- canonical validation: Python 3.13 및 3.14에서 각각 `542 passed`, failure/skip 없음
- Actions artifact 없음
- 임시 validation PR, branch와 workflow cleanup 완료

Algorithm과 threshold는 변경하지 않았다.

구현 범위:

- Phase 2C-3 regression dataset reader
- schema, identity, path, manifest와 SHA-256 검증
- current `OpenCvPhaseDetector` benchmark runner
- 독립 case와 sequence 간 temporal state 격리
- 8개 category별 metric
- raw/smoothed 유면과 Foam 위치 분리
- coverage, fill state, Foam precision/recall, shimmer와 no-interface metric
- JSON/CSV/Markdown atomic 결과
- dataset/run/settings fingerprint
- previous baseline comparison
- headless CLI
- fixture 수집, 실행과 해석 절차

S1은 대규모 학습 모델, model checkpoint, GPU dependency와 algorithm tuning을 도입하지 않았다. 기존 `DetectorSettings` snapshot을 그대로 사용했고 단일 영상용 hard-coded 예외를 추가하지 않았다.

### S2 — UI raster boundary architecture refactor

**다음 작업**

범위:

- `result_review_canvas.py`의 `cv2`와 `numpy` import 제거
- overlay rendering을 vision/presentation adapter로 이동
- PNG encoding과 filesystem write를 storage adapter로 이동
- concrete renderer와 filesystem wiring을 UI 밖 bootstrap/composition root로 이동
- architecture allowlist 제거

### S3 — Workbench usability stabilization

대상:

- RW-01~RW-09
- RW-11
- 사용자 용어 통일
- Windows DPI layout 검증

### S4 — Analysis lifecycle와 결과 시각화 안정화

대상:

- RW-10
- RW-14
- RW-15
- stage progress
- 한글 font
- 유면 용어
- 전체 Glass y축

### S5-A — Foam과 아지랑이 구분 개선

S1 benchmark를 기준으로 Foam false-positive를 줄인다.

구현·acceptance 기준:

- OpenCV·NumPy 기반 경량 algorithm을 우선한다.
- 대규모 학습 모델, model checkpoint와 GPU dependency를 기본 범위에 포함하지 않는다.
- threshold와 scoring weight는 여러 fixture category의 precision, recall과 shimmer false-positive 결과로 보정한다.
- 설정값은 가능한 한 `DetectorSettings`에서 관리하고 serialization과 fingerprint 대상에 포함한다.
- 단일 영상, fixture ID나 파일명에 대한 hard-coded 예외를 금지한다.
- evidence가 낮거나 상충하면 Foam 상태를 강제하지 않고 `UNKNOWN_REVIEW`로 처리한다.
- 배포 용량 증가, CPU frame 처리 시간, memory와 Windows one-folder packaging을 측정한다.

### S5-B — 유면 경계와 temporal tracking 개선

S1 benchmark를 기준으로 위치 오차, false boundary와 tracker contamination을 줄인다.

구현·acceptance 기준:

- OpenCV·NumPy 기반 경량 candidate, scoring과 temporal algorithm을 우선한다.
- 대규모 학습 모델, model checkpoint와 GPU dependency를 기본 범위에 포함하지 않는다.
- threshold와 scoring weight는 여러 fixture category의 MAE, P90/P95, coverage와 no-interface false-boundary 결과로 보정한다.
- 설정값은 가능한 한 `DetectorSettings`에서 관리하고 serialization과 fingerprint 대상에 포함한다.
- 단일 영상, fixture ID나 파일명에 대한 hard-coded 예외를 금지한다.
- confidence가 낮거나 candidate evidence가 상충하면 위치나 fill state를 강제하지 않고 `UNKNOWN_REVIEW`로 처리한다.
- 배포 용량 증가, CPU frame 처리 시간, memory와 Windows one-folder packaging을 측정한다.

S5-A와 S5-B를 하나의 대형 PR로 합치지 않는다.

### S6 — 실제 영상 validation gate

- 동일 fixture dataset 재실행
- baseline과 새 detector 비교
- 여러 category에서 threshold와 setting의 일반화 확인
- 실제 compressor 영상 수동 확인
- Windows 장시간 실행
- event와 judgment 회귀
- memory와 CPU 처리 속도
- 배포 용량 변화
- Windows one-folder packaging과 GPU 없는 PC 실행
- file lock과 resource cleanup

Detector 개선이 수치로 확인되지 않거나 Windows CPU/배포 acceptance를 충족하지 않으면 다음 단계로 진행하지 않는다.

### S7 — Phase 2C-4 공유용 결과 영상

다음 조건 이후에 시작한다.

- UI raster boundary 정리 완료
- Workbench 실사용 문제 해결
- graph 용어·font·y축 정책 확정
- detector validation gate 통과

Annotated MP4 rendering과 encoding은 UI 밖의 adapter/application 계층에서 구현한다.

## 8. 구현 순서 요약

1. **S1 Detector benchmark foundation — 완료**
2. **S2 UI raster boundary architecture refactor — 다음 작업**
3. **S3 Workbench usability stabilization**
4. **S4 Analysis lifecycle·결과 시각화 안정화**
5. **S5-A Foam/아지랑이 구분**
6. **S5-B 유면 검출·tracking**
7. **S6 실제 영상 validation gate**
8. **S7 Phase 2C-4 annotated MP4**

## 9. 완료 마킹 정책

- 각 단계는 구현 PR이 `main`에 병합된 뒤에만 완료로 표시한다.
- 자동 test를 실행하지 않은 플랫폼에 대해 PASS를 주장하지 않는다.
- Windows DPI, Windows one-folder와 실제 compressor 영상 검증은 별도로 기록한다.
- Detector 변경은 benchmark 전후 수치, runtime, memory와 배포 영향 evidence를 함께 기록한다.
- Phase 2C-4는 S6 gate 통과 전 시작하지 않는다.
