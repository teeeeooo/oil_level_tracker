# Rotary Oil Level Tracker — 프로젝트 SSOT 작업 명세서

> **문서 상태:** Authoritative / Single Source of Truth  
> **버전:** 1.0  
> **작성일:** 2026-07-20  
> **대상:** Codex, Claude Code 및 기타 구현 에이전트  
> **구현 기준:** 빈 저장소에서 처음부터 신규 구현  
> **배포 목표:** Windows one-folder 데스크톱 애플리케이션  
> **주요 기술:** Python, PySide6, OpenCV, NumPy, HTML/CSV export

---

## 0. 문서 권한과 적용 규칙

이 문서는 `Rotary Oil Level Tracker` 프로젝트의 제품 목적, 사용자 workflow, domain model, GUI, 영상 검출기, 결과물, 아키텍처, 테스트 및 구현 순서를 정의하는 **유일한 제품 구현 기준 문서(SSOT)** 이다.

현재 milestone 상태와 장기 순서는 [`00-project/roadmap.md`](00-project/roadmap.md), active branch의 exact gate·evidence·next action은 [`00-project/work-plan.md`](00-project/work-plan.md)가 소유한다. 승인된 feature architecture는 이 문서의 제품/호환성 요구를 유지하면서 내부 구현 계약을 구체화할 수 있다. 문서 탐색과 전체 권한 순서는 [`README.md`](README.md)를 따른다.

이 문서는 다음 기존 문서의 내용을 통합하고 대체한다.

- `rotary_oil_level_tracker_project_overview_updated.md`
- `rotary_oil_level_tracker_reference_review_updated.md`
- `oil_level_phase_boundary_detector_design_spec.md`

기존 문서는 배경 자료로만 취급한다. 기존 문서와 본 문서가 충돌할 경우 **본 문서를 우선한다**.

본 작업은 기존 코드의 호환성을 유지하는 수정 작업이 아니다. **새 저장소 또는 빈 코드베이스에서 처음부터 구현하는 신규 프로젝트**로 간주한다.

구현 중 임의로 요구사항을 축소하거나, 단순화를 이유로 core boundary를 무시하거나, GUI 안에 영상처리 로직을 직접 작성해서는 안 된다. 다만 detector의 threshold와 scoring weight처럼 실제 시험 영상으로 조정해야 하는 값은 설정값으로 관리하고, 문서의 예시값을 절대 정답으로 취급하지 않는다.

---

# 1. 프로젝트 목적

## 1.1 업무 배경

신규 Rotary 압축기가 도입되면 압축기 내부 실린더 윤활이 원활하게 이루어지는지 확인하기 위해 윤활유의 회수 상태를 확인한다.

시험에서는 압축기 하부 또는 실린더가 위치한 부위에 sight glass를 설치하고, webcam으로 glass 내부를 촬영한 뒤 OBS Studio 등으로 영상을 녹화한다. 현재는 시험자가 녹화 영상을 직접 보면서 다음 항목을 확인한다.

- 압축기 기동 후 유면이 어떻게 낮아지는지
- 유면 최저점이 언제인지
- 유면이 기준 높이까지 언제 회복되는지
- 기준 높이 이상 또는 이하 상태가 유지되는지
- 기포 또는 foam이 언제 발생하고 어디까지 올라오는지
- glass가 뿌옇거나 빛 반사로 관찰 불가능한 구간이 있는지

수동 판독은 시간이 오래 걸리고, 판독자에 따라 결과가 달라질 수 있으며, 그래프와 캡쳐 자료를 별도로 작성해야 한다.

## 1.2 제품 목표

본 프로그램은 녹화된 시험 영상을 대상으로 다음 작업을 지원하는 Windows 데스크톱 분석 도구이다.

```text
시험 영상 선택
→ sight glass 설정 Recipe 작성
→ 현재 frame에서 검출 결과 미리보기
→ 전체 분석 구간 tracking
→ oil-air boundary와 foam front 추적
→ 이벤트 검출
→ 그래프 및 이벤트 캡쳐 검토
→ HTML 보고서와 CSV raw data 생성
```

초기 목표는 완전 무인 자동 판정이 아니다. 프로그램은 검출 결과의 confidence와 `REVIEW_REQUIRED` 상태를 명시하여 **시험자의 판독을 정량적으로 보조**해야 한다.

Detector의 실용 목표는 개별 frame의 유면 Y를 pixel-perfect하게 맞추는 것보다, 사용자가 최종 graph에서 유면의 하강·상승·정체와 최저점/회복 흐름을 이해할 수 있도록 **충분히 자주, 같은 물리적 유면을 대략적으로 추적하는 numeric observation을 제공하는 것**이다. 따라서 detector 개선에서는 usable numeric coverage와 시간축상 관측 분포/graph movement readability를 pixel-level MAE보다 우선할 수 있다. 다만 glass 구조선·반사·glare 등 유면과 무관한 대상을 지속적으로 따라 graph의 방향이나 수준을 왜곡하는 gross wrong-interface 검출은 허용하지 않는다. 관측 근거가 없는 구간을 numeric으로 합성하는 방식으로 coverage를 높여서도 안 된다.

사용자용 결과 보고서의 목표는 detector 내부 상태를 정리하는 것이 아니라, 원본 sight-glass 영상에서 관측된 유면 흐름을 설명하는 것이다. 보고서는 관측된 최고·최저 유면, Foam 발생·소멸과 주요 변화 시점을 graph에 표시하고 해당 원본 영상 장면을 Glass 중심 캡처로 함께 보여준다. 후보 점수, rejection reason, Spatial sector와 같은 debug 정보는 CSV/Result Review/debug artifact에 분리하며 main report의 정보 구조를 지배해서는 안 된다.

## 1.3 제품 정체성

본 프로그램은 범용 머신비전 개발 플랫폼이 아니다.

상용 머신비전 SW의 검증된 패턴인 다음 workflow를 차용하되, Rotary 압축기 유면 시험에 필요한 기능만 제공한다.

```text
Setup
→ Validation / Preview
→ Analysis
→ Review
→ Export
```

---

# 2. 제품 범위

## 2.1 MVP 포함 범위

MVP는 다음 기능을 포함한다.

- PySide6 기반 Windows 데스크톱 GUI
- `Recipe(Profile) Workbench`
- 새 Recipe 생성 wizard
- wizard 건너뛰기 및 빈 Workbench 시작
- 녹화 영상 파일 선택
- 영상 재생, 일시정지, seek
- 재생 속도 선택: `0.5×`, `1×`, `1.5×`, `2×`, `4×`
- 분석 시작/종료 시각 지정
- 압축기 기동 시각 지정
- 분석 sampling FPS 지정
- 1~3개 이상의 glass 정의를 지원하는 list 기반 구조
- 영상 위에서 ellipse glass geometry 편집
- ellipse에서 자동 파생되는 crop ROI
- glass별 zero line 편집
- glass별 initial observation state
- glass별 mm/pixel 환산값
- glass별 판정 모드
- glass별 detection margin
- glass별 복수 exclusion zone
- 현재 frame의 oil-air 및 foam 후보 미리보기
- detector debug mode
- Recipe 저장/불러오기/검증
- 유면 및 foam tracking
- 이벤트 검출
- 그래프 생성
- 이벤트 frame 캡쳐
- HTML 보고서 생성
- CSV raw data 생성
- Windows one-folder 패키징

## 2.2 MVP 제외 범위

다음 기능은 MVP에서 구현하지 않는다.

- 실시간 webcam 분석
- OBS 직접 제어
- AI/딥러닝 segmentation
- YOLO, PyTorch, TensorFlow 의존성
- cloud/server/database
- 사용자 계정 및 권한 관리
- 여러 영상을 한 번에 처리하는 batch queue
- XLSX/PDF/PPT export
- 설치형 installer
- 범용 drag-and-drop vision pipeline editor
- polygon exclusion editor
- 자동 카메라 calibration
- 여러 카메라 동기화

향후 XLSX export를 추가할 수 있도록 `AnalysisResult`와 reporting port는 확장 가능하게 설계한다.

---

# 3. 핵심 용어

| 용어 | 정의 |
|---|---|
| **Recipe / Profile** | 반복 사용할 수 있는 glass geometry, zero line, detector 설정, 판정 규칙을 저장한 검사 설정 |
| **Analysis Session** | 현재 분석할 영상, 시간 범위, 압축기 기동 시각, sampling FPS, 출력 위치를 가진 실행 단위 |
| **Workbench Document** | UI에서 편집 중인 Recipe와 Analysis Session을 묶은 transient 상태 |
| **Glass** | 하나의 sight glass 검사 단위 |
| **Ellipse** | 사용자가 영상 위에서 지정하는 glass 외형 |
| **Crop ROI** | ellipse 외접 사각형에서 자동 파생되는 영상 crop 영역 |
| **Effective Detection Mask** | ellipse 내부에서 margin과 exclusion zone을 제외한 실제 검지 영역 |
| **Zero line** | 유면 높이의 기준선. 위쪽이 양수, 아래쪽이 음수 |
| **Oil-air boundary** | 공기와 clear oil 사이의 유면 경계 |
| **Foam front** | 하단과 연결된 foam/bubbly oil 영역의 최상단 경계 |
| **Candidate** | oil-air boundary 또는 foam front의 후보 위치 |
| **FillState** | 현재 glass 내부 관측 상태 |
| **Preview** | 선택한 현재 frame 한 장을 detector에 입력해 후보와 상태를 overlay로 확인하는 기능 |
| **Validation** | Recipe와 Analysis Session이 분석 가능한 상태인지 검사하는 기능 |
| **Review Required** | 자동 판정 신뢰도가 부족해 사람 확인이 필요한 상태 |

---

# 4. 최상위 사용자 Workflow

## 4.1 프로그램 시작

프로그램을 실행하면 `Recipe Workbench` 메인 창을 표시한다.

초기 상태는 다음 중 하나다.

1. 마지막 사용 Recipe를 자동으로 열지 않고 빈 Workbench를 표시한다.
2. 사용자는 `새 Recipe` 또는 `Recipe 불러오기`를 선택한다.
3. `새 Recipe` 선택 시 wizard를 실행하거나 wizard를 건너뛰고 빈 Workbench로 이동할 수 있다.

## 4.2 새 Recipe Wizard

Wizard는 다음 페이지로 구성한다.

### Page 1 — 영상 선택

- 분석할 영상 파일 선택
- 영상 metadata 표시
  - 파일명
  - 해상도
  - source FPS
  - duration
  - frame count
  - codec 정보가 가능한 경우 표시
- 지원 대상: MP4, MKV, AVI, MOV
- 영상 열기 실패 시 원인과 대응 메시지 표시

### Page 2 — 시험 시간 조건

- 분석 시작 시각
- 분석 종료 시각
- 압축기 기동 시각
- 분석 sampling FPS
- 재생 속도는 분석 설정이 아니므로 이 페이지에 저장하지 않는다.

### Page 3 — Recipe 기본 정보

- Recipe 이름
- 설명 또는 메모
- 선택적으로 기본 Glass A 생성
- 완료 후 Workbench로 이동

### Wizard 건너뛰기

사용자는 wizard를 건너뛰고 빈 Workbench로 이동할 수 있다. 빈 Workbench에서는 동일 항목을 메인 화면에서 직접 입력한다.

## 4.3 Glass 설정

1. 왼쪽 Glass 목록에서 `Glass 추가`를 선택한다.
2. Glass가 생성되면 중앙 영상 위에 기본 ellipse가 나타난다.
3. ellipse를 이동하고 크기를 조정해 실제 glass를 감싼다.
4. zero line을 위아래로 이동한다.
5. 오른쪽 설정 패널에서 상태, scale, 판정 모드, margin을 지정한다.
6. 필요하면 exclusion zone을 추가한다.
7. seek bar로 여러 시점으로 이동하며 preview 결과를 확인한다.
8. 동일 방식으로 Glass B, Glass C를 추가한다.

## 4.4 Recipe 검증 및 저장

- `저장`은 현재 작업을 Recipe 파일로 보존한다.
- `검증`은 전체 분석 readiness를 검사한다.
- 분석은 `VALIDATED` 상태에서만 실행한다.
- 저장 시에도 구조 검증을 수행하며, 손상된 geometry나 직렬화 불가능한 설정은 저장을 차단한다.
- 필수 분석 항목이 미완성인 경우 사용자는 `DRAFT` 상태로 저장할 수 있다.
- `VALIDATED` Recipe를 수정하면 자동으로 `DRAFT_DIRTY` 상태로 전환한다.

## 4.5 분석 실행

1. Recipe 및 Session 검증
2. 출력 폴더 선택 또는 기본 출력 폴더 생성
3. background worker에서 분석 실행
4. progress, 현재 시간, 현재 Glass, 처리 속도 표시
5. 취소 기능 제공
6. 완료 후 Review 화면으로 이동

## 4.6 결과 검토 및 export

- combined graph
- glass별 상세 graph
- fill state 구간
- oil-air boundary
- foam front
- 이벤트 목록
- 이벤트 캡쳐
- low-confidence 및 unknown 구간
- 전체 판정과 glass별 판정
- HTML/CSV 결과 경로

---

# 5. Recipe Workbench GUI 명세

## 5.1 전체 Layout

메인 화면은 세 영역과 상단 toolbar, 하단 transport 영역으로 구성한다.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ [새 Recipe] [불러오기] [저장] [검증] [분석] [결과 보기]   상태: DRAFT       │
├───────────────┬──────────────────────────────────────┬───────────────────────┤
│ Glass 목록     │ Video / Overlay Workbench            │ 선택 Glass 설정        │
│               │                                      │                       │
│ Glass A       │          영상 frame                  │ 이름                  │
│ Glass B       │       ellipse / zero / candidates    │ geometry              │
│               │                                      │ initial state         │
│ [Glass 추가]  │                                      │ mm/pixel              │
│ [삭제]        │                                      │ judgment mode         │
│               │                                      │ margin                │
│               │                                      │ exclusion zones       │
├───────────────┴──────────────────────────────────────┴───────────────────────┤
│ [재생/정지] [이전/다음 frame] [seek bar] [현재시각] [0.5× 1× 1.5× 2× 4×]   │
└──────────────────────────────────────────────────────────────────────────────┘
```

중앙 영상 영역이 가장 넓어야 한다.

## 5.2 상단 Toolbar

필수 action:

- `새 Recipe`
- `Recipe 불러오기`
- `Recipe 저장`
- `Recipe 검증`
- `분석 실행`
- `결과 보기`
- 선택적으로 `Debug mode`

Toolbar에는 다음 상태를 표시한다.

- `EMPTY`
- `DRAFT`
- `DRAFT_DIRTY`
- `VALIDATED`
- `ANALYZING`
- `ANALYZED`
- `ERROR`

## 5.3 왼쪽 Glass 목록

각 row에 표시:

- 이름
- enabled 상태
- 설정 완료 여부
- preview confidence 요약
- validation error/warning indicator

Action:

- Glass 추가
- 선택 Glass 삭제
- enabled toggle
- 위/아래 순서 변경은 선택 기능
- duplicate는 후속 기능

Domain model은 Glass 개수를 제한하지 않는다. MVP UI와 테스트 범위는 일반적인 1~3개 Glass를 기준으로 한다.

## 5.4 중앙 Video / Overlay Workbench

중앙 화면은 다음 기능을 담당한다.

- source video frame 표시
- ellipse overlay 표시
- selected/unselected glass 구분
- zero line 표시
- exclusion zone 표시
- preview candidate 표시
- selected oil-air boundary 표시
- selected foam front 표시
- confidence와 FillState 표시
- mouse hit test 및 geometry 편집
- source frame 좌표와 display 좌표 변환

### Overlay Z-order

아래에서 위 순서:

1. video frame
2. non-selected glass ellipse
3. selected glass ellipse 및 resize handles
4. detection margin / effective mask optional visualization
5. exclusion zones
6. zero line
7. rejected candidates
8. selected oil-air boundary
9. selected foam front
10. labels / confidence / state

## 5.5 영상 재생과 Seek

지원 재생 속도:

- 0.5×
- 1×
- 1.5×
- 2×
- 4×

필수 기능:

- play/pause
- frame step backward/forward
- seek bar
- 현재 timecode
- duration
- 현재 source frame index
- analysis start/end marker
- compressor start marker

`재생 속도`와 `분석 sampling FPS`는 서로 다른 개념이다.

- 재생 속도: 사용자가 영상을 보는 속도
- 분석 sampling FPS: 분석 엔진이 초당 몇 개의 timestamp를 처리할지 결정

분석 sampling FPS는 source FPS를 초과할 수 없다. Variable Frame Rate 영상은 frame 번호 간격이 아니라 timestamp 기반 sampling을 사용한다.

---

# 6. Overlay Geometry 명세

## 6.1 좌표계

모든 저장 geometry의 canonical coordinate는 **원본 source frame pixel 좌표**다.

- 원점: frame 좌상단
- x: 오른쪽이 양수
- y: 아래쪽이 양수
- engineering height: `zero_line_y - boundary_y`
- zero line 위쪽: 양수
- zero line 아래쪽: 음수

UI display 좌표는 항상 source frame 좌표로 역변환한 뒤 저장한다.

Recipe에는 `reference_frame_width`, `reference_frame_height`를 저장한다.

다른 해상도의 영상에 Recipe를 적용하면 다음 처리를 한다.

1. normalized 비율로 provisional remap
2. 사용자에게 resolution mismatch 경고
3. geometry 재검증 요구
4. Recipe가 다시 검증되기 전 분석 금지

## 6.2 Glass Ellipse

Canonical geometry:

```text
center_x
center_y
radius_x
radius_y
```

또는 직렬화 시 동등한:

```text
left
top
width
height
```

ellipse는 회전하지 않는 axis-aligned ellipse로 제한한다.

지원 interaction:

- ellipse 내부 drag: 이동
- 좌우 handle: 폭 조절
- 상하 handle: 높이 조절
- corner handle: 폭/높이 동시 조절
- 최소 크기 제한
- frame 바깥으로 이동 금지
- keyboard arrow 미세 이동은 선택 기능

Crop ROI는 ellipse 외접 사각형에서 자동 파생한다. 사용자는 별도의 rectangular ROI를 직접 편집하지 않는다.

## 6.3 Detection Margin

Margin은 glass 테두리, rim, gasket edge에 detector가 고정되는 것을 막기 위한 ellipse 내부 여백이다.

- 사용자 입력은 pixel 또는 ratio로 표시할 수 있다.
- canonical 저장은 `margin_ratio_x`, `margin_ratio_y` 또는 단일 `margin_ratio`
- effective detection mask는 ellipse mask를 inward erosion한 결과
- margin은 ellipse의 유효 반지름보다 작아야 한다.
- margin으로 인해 유효 면적이 최소 기준보다 작아지면 validation error

## 6.4 Zero Line

Zero line은 selected ellipse에 종속된 수평선이다.

표시:

- 점선
- 양끝 화살표 또는 handle
- `기준점` 라벨
- y값과 mm/pixel이 있으면 `0.0 mm` 표시

interaction:

- line drag로 y 이동
- source y좌표 숫자 입력
- ellipse vertical extent 내부에 있어야 함
- 표시 line의 좌우 끝은 해당 y에서 ellipse와 만나는 교점에 맞춘다.
- zero line 자체는 exclusion zone의 영향을 받지 않는다.

## 6.5 Exclusion Zone

MVP exclusion zone은 **axis-aligned rectangle**로 정의한다.

사용 목적:

- glass 표면 긁힘
- 마킹
- 강한 고정 반사
- 카메라 hotspot
- 반복적으로 detector가 고정되는 artifact

지원 기능:

- 추가
- 선택
- 이동
- 크기 조절
- 삭제
- 이름/메모 optional

규칙:

- 여러 개 지원
- ellipse와 교차하는 부분만 effective mask에서 제외
- frame 바깥 금지
- exclusion을 적용한 후 최소 유효 면적과 수평 coverage가 남아야 함
- 전체 ellipse를 사실상 가리는 exclusion 구성은 validation error

향후 polygon exclusion을 추가할 수 있지만 MVP에는 포함하지 않는다.

---

# 7. 오른쪽 Glass 설정 패널

## 7.1 기본 정보

- Glass 이름
- enabled
- 설명/메모 optional

## 7.2 Geometry

읽기/직접 입력:

- center x/y
- width/height
- derived crop ROI
- zero line y
- detection margin
- exclusion zone 목록

숫자 수정 시 중앙 overlay가 즉시 갱신되어야 한다.

## 7.3 Initial Observation State

사용자가 분석 시작 시점의 초기 관측 상태를 선택한다.

```text
AUTO
EMPTY_NO_INTERFACE
FILLING_VISIBLE
PARTIAL_VISIBLE
FULL_NO_INTERFACE
DRAINING_VISIBLE
FULL_WITH_FOAM
FOAMING_VISIBLE
UNKNOWN_REVIEW
```

`AUTO`는 detector가 초기 상태를 판단하도록 남겨 둔 compatibility/unresolved 값이다. Persisted Recipe의 `initial_state`는 **선택된 초기 prior**이며 detector의 hard truth가 아니다. 수동 상태도 영상 증거가 충분하면 다른 관측 상태로 전이할 수 있어야 한다.

### 7.3.1 Current-run confirmation과 retrospective interpretation

최종 분석은 enabled Glass마다 **현재 run/session의 초기 상태 확인**이 명시적으로 완료되어야 한다. 이 확인은 현재 video와 analysis-start context를 사용자가 직접 시각 판독했다는 run/session provenance이며, Recipe 저장·불러오기·복사나 pre-populated 값만으로 성립하지 않는다.

- `AUTO`는 최종 분석 readiness를 만족할 수 없다.
- 사용자가 실제로 판단할 수 없는 경우 명시적으로 확인한 `UNKNOWN_REVIEW`는 최종 분석 readiness를 만족할 수 있지만 retrospective FULL/EMPTY authority는 제공하지 않는다.
- 다른 명시적으로 확인된 non-`AUTO` 상태는 기존 initial-prior 의미를 유지한다.
- Initial-State Retrospective FULL/EMPTY Reconstruction은 명시적으로 확인된 `FULL_NO_INTERFACE` 또는 `EMPTY_NO_INTERFACE` prior에서만 활성화될 수 있다.
- persisted/copied initial-state 값은 current-run confirmation을 복사하거나 합성하지 않는다.

Detector가 남긴 observed `fill_state`, observed validity와 numeric Oil evidence는 immutable historical observation이다. Retrospective FULL/EMPTY는 별도 official sequence interpretation이며 observation을 다시 쓰지 않는다. Later direct sequence evidence가 prior와 모순되면 그 direct evidence가 retrospective eligibility를 무효화한다. Retrospective interpretation은 numeric Oil boundary를 합성하지 않는다.

## 7.4 mm/pixel

- optional
- 양수 실수
- 미입력 시 결과 단위는 pixel
- 입력 시 `height_mm = height_px × mm_per_pixel`
- 향후 2-point calibration으로 확장 가능

## 7.5 Judgment Mode

Glass별로 다음 판정 모드를 지원한다.

### A. `RECOVERY`

압축기 기동 후 유면이 zero line 이상으로 회복하고 지정 시간 동안 유지되는지 판정한다.

필수 parameter:

- recovery limit sec
- stable hold sec
- minimum valid coverage ratio
- unknown 구간 처리 정책

PASS 예:

```text
compressor_start + recovery_limit 이내에
smoothed oil-air level >= 0
AND stable_hold_sec 이상 유지
```

### B. `HOLD_BELOW_ZERO`

분석 구간 동안 유면이 zero line 아래에 유지되는지 판정한다.

parameter:

- allowed excursion sec
- allowed excursion height
- minimum valid coverage ratio

### C. `HOLD_ABOVE_ZERO`

분석 구간 동안 유면이 zero line 위에 유지되는지 판정한다.

parameter:

- allowed violation sec
- allowed violation depth
- minimum valid coverage ratio

자동 판정이 불가능하거나 valid coverage가 부족하면 `REVIEW_REQUIRED`다.

## 7.6 Detector Settings

일반 사용자는 기본 설정을 사용한다. 고급 설정은 접을 수 있는 section으로 둔다.

설정 후보:

- Canny thresholds
- Hough angle/length
- minimum horizontal coverage
- minimum region contrast
- minimum final confidence
- temporal max jump
- smoothing window
- glare threshold
- foam threshold
- state hold frames

설정에는 `기본값 복원` action을 제공한다.

---

# 8. Recipe와 Analysis Session 모델

## 8.1 모델 분리 원칙

Recipe를 특정 영상 파일 하나에 영구 고정하지 않는다.

### InspectionRecipe

반복 사용 가능한 설정:

- Recipe metadata
- reference resolution
- Glass definitions
- default judgment rules
- default detector settings
- schema version

### AnalysisSession

현재 실행에만 해당하는 정보:

- input video path
- video metadata
- analysis start/end
- compressor start
- analysis sampling FPS
- output directory
- run note
- Recipe snapshot reference

### WorkbenchDocument

UI에서 현재 편집 중인 aggregate:

```text
InspectionRecipe
+ AnalysisSession
+ dirty/validation state
+ current selected glass
+ current frame time
```

## 8.2 Recipe File

확장자:

```text
*.oilrecipe
```

내용은 UTF-8 JSON이다.

필수 root field:

```json
{
  "schema_version": 1,
  "recipe_id": "uuid",
  "name": "Rotary A setup",
  "description": "",
  "reference_frame": {
    "width": 1920,
    "height": 1080
  },
  "glasses": [],
  "defaults": {},
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

Session은 별도 파일로 저장할 수 있으나 MVP에서는 Recipe 옆에 optional `last_session`을 저장하지 않는다. 최근 파일 경로 같은 UI 편의 정보는 application settings에서 관리한다.

## 8.3 Recipe Versioning

- `schema_version` 필수
- unknown future version은 읽기 전용 또는 명시적 오류
- migration은 storage adapter에서 수행
- domain은 JSON raw structure를 직접 다루지 않는다.

---

# 9. Recipe Validation 명세

## 9.1 Validation Level

### Structural Validation

저장 자체를 차단하는 오류:

- NaN/Infinity 좌표
- 음수 또는 0 크기 ellipse
- frame 바깥 geometry
- 중복 glass ID
- 잘못된 enum
- JSON 직렬화 불가
- margin이 ellipse를 모두 제거
- exclusion zone 좌표 손상

### Readiness Validation

분석을 차단하지만 DRAFT 저장은 허용:

- 영상 없음
- Glass 없음
- zero line 미설정
- 분석 시간 범위 없음
- recovery mode인데 compressor start 없음
- analysis FPS 없음 또는 source FPS 초과
- enabled Glass의 필수 판정 rule 누락
- initial state/geometry 정합성 실패
- effective mask 면적 부족
- resolution mismatch 후 재검증 미완료

Final-analysis readiness additionally requires explicit current-run initial-state confirmation for every enabled Glass. `AUTO` or missing current-run confirmation blocks final analysis even when a persisted Recipe value exists. This run/session confirmation is not Recipe persistence and must not be inferred from save/load/copy behavior.

### Warning

저장과 분석을 허용하지만 사용자 확인:

- zero line이 ellipse 최상단/하단에 너무 가까움
- exclusion area 비율이 큼
- margin이 과도함
- mm/pixel 없음
- preview confidence 낮음
- 초기 상태가 preview state와 불일치
- analysis duration이 매우 짧음
- source codec/timestamp 신뢰성 경고

## 9.2 Validation UI

`Recipe 검증` 결과는 다음으로 표시한다.

- Error
- Warning
- Information

각 항목은 Glass ID와 수정 가능한 설정 위치를 포함해야 한다. 항목 클릭 시 해당 Glass와 field를 선택한다.

## 9.3 Save 정책

- structural error가 있으면 저장 금지
- readiness error가 있으면 `DRAFT`로 저장 가능
- validation 통과 시 `VALIDATED`
- validated Recipe 변경 시 `DRAFT_DIRTY`
- analysis 시작 시 자동 재검증

---

# 10. Preview 및 Debug UX

## 10.1 자동 Preview

선택한 Glass가 있을 때 사용자가 다음 동작을 하면 preview를 갱신한다.

- seek 종료
- frame step
- ellipse 수정 완료
- zero line 수정 완료
- exclusion 수정 완료
- detector setting 변경 완료
- initial state 변경

preview는 UI를 막지 않는 background task로 실행한다.

빠른 seek 중에는 매 frame마다 실행하지 않고 debounce한다. 사용자가 seek를 멈춘 뒤 짧은 지연 후 가장 최근 frame만 분석한다.

## 10.2 일반 Preview Overlay

일반 사용자에게 표시:

- selected oil-air boundary
- selected foam front
- top-k 후보 optional
- FillState
- overall confidence
- `LOW CONFIDENCE` / `REVIEW` badge
- valid area 경계 optional

## 10.3 Debug Mode

Debug mode는 developer/advanced user용이다.

권장 tabs:

```text
Overlay
ROI / Preprocess
Edges / Masks
Foam
Candidates
State
```

### Overlay

- ellipse
- effective mask
- zero line
- oil-air candidates
- foam candidates
- selected boundaries
- rejected candidate reason
- confidence
- state

### ROI / Preprocess

- original crop
- ellipse-masked crop
- grayscale
- normalized/CLAHE
- blurred image

### Edges / Masks

- Sobel profile
- Canny edge
- horizontal morphology
- Hough segments
- glare mask
- border/margin mask
- exclusion mask
- static artifact map

### Foam

- row texture profile
- edge density
- local variance
- temporal flicker
- bottom-connected foam mask
- selected foam front

### Candidates

필수 column:

```text
rank
kind
source
y
edge_strength
horizontal_coverage
region_contrast
texture_score
foam_score
temporal_score
state_transition_score
glare_penalty
border_penalty
exclusion_penalty
static_artifact_penalty
jump_penalty
final_score
rejected
reject_reason
```

### State

- previous state
- current state
- user initial prior
- transition score
- visibility confidence
- oil-air confidence
- foam confidence
- flags

## 10.4 Debug Export

선택 frame debug export:

```text
debug/
├─ frame_000123_overlay.png
├─ frame_000123_roi.png
├─ frame_000123_preprocessed.png
├─ frame_000123_canny.png
├─ frame_000123_masks.png
├─ frame_000123_foam.png
├─ frame_000123_candidates.csv
└─ frame_000123_debug.json
```

Debug artifact는 기본 결과물에 포함하지 않고 debug option이 활성화된 경우에만 생성한다.

---

# 11. Glass 내부 Phase 검출 설계

## 11.1 핵심 원칙

Detector는 “가장 강한 edge row”를 유면으로 선택해서는 안 된다.

다음 구조를 따른다.

```text
Effective ROI 생성
→ Preprocess
→ Artifact masks
→ Row features
→ 후보 생성
→ 후보 scoring
→ current-frame semantic / hard-safety 분류
→ serialized online observation 기록
→ 전체 분석 window의 Oil/FULL/EMPTY/UNKNOWN sequence resolution
→ Oil/state 확정 후 독립 Foam episode resolution
→ oil-air boundary / foam front 최종 projection
→ confidence와 debug data 반환
```

최종 numeric Oil은 해당 sampled frame에 실제 존재하는 hard-safe 후보 중 하나여야 한다. Sequence resolver는 다른 frame의 위치를 carry/interpolate/predict하여 빈 frame에 숫자를 만들 수 없다. 좌표 근거가 없는 frame은 explicit FULL/EMPTY state 또는 `UNKNOWN_REVIEW`로 남긴다.

## 11.2 Effective Detection Region

```text
ellipse mask
- inward margin
- exclusion zones
= effective detection mask
```

Crop은 ellipse bounding rectangle을 사용하되, 모든 feature 계산은 effective mask를 존중해야 한다.

## 11.3 Candidate Generators

### A. Sobel Gradient Peaks

기존 Sobel 방식은 최종 detector가 아니라 후보 생성기로만 사용한다.

- grayscale
- y-direction Sobel
- masked row energy
- local maxima top-k
- source=`sobel`

### B. Canny Horizontal Coverage

- grayscale/normalize
- blur
- Canny
- horizontal morphology
- row별 유효 폭 대비 coverage
- coverage threshold 이상을 후보화
- source=`canny`

### C. HoughLinesP

- Canny map 입력
- near-horizontal segment
- minimum line length
- maximum gap
- mask 교차율
- source=`hough`

### D. Region Boundary Candidate

후보 위/아래 band의 feature 차이를 직접 계산해 local maxima를 생성할 수 있다.

- intensity difference
- texture difference
- edge-density difference
- source=`region_boundary`

### E. Foam Front Candidate

foam은 단순 수평 edge보다 texture 변화로 검출한다.

- local variance
- Laplacian/texture energy
- small component density
- edge density
- temporal flicker
- bottom-connected foam-like region
- source=`foam_texture`

## 11.4 Candidate Scoring

Oil-air 후보 score feature:

- edge strength
- horizontal continuity
- above/below region contrast
- gradient direction
- valid area coverage
- temporal continuity
- state transition plausibility
- glare penalty
- border/rim penalty
- exclusion overlap penalty
- static artifact penalty
- jump penalty

Foam 후보 score feature:

- texture contrast
- edge density
- small component density
- temporal flicker
- bottom connectivity
- upward growth consistency
- glare penalty
- static artifact penalty

Score weight는 `DetectorSettings`에서 조절한다.

최고점 후보라도 minimum confidence 미만이면 선택하지 않는다.

Current-frame semantic이 최종 선택하지 않은 bounded hard-safe 후보도 completed-analysis sequence 비교를 위해 provenance와 함께 보존할 수 있다. Sequence comparison은 물리적 이동 연속성, material anchor cluster, no-interface state evidence와 conjunctive recurring-artifact opposition을 사용한다. 고정 row라는 사실만으로 후보를 hard reject하지 않으며, 매끄러운 path라는 이유만으로 약한 후보 chain을 numeric trajectory로 승격하지 않는다.

## 11.5 Artifact Handling

### Border / Rim

- margin 영역은 hard mask
- ellipse boundary에 가까운 후보는 penalty 또는 reject
- 후보가 mask 때문에 충분한 horizontal coverage를 확보하지 못하면 reject

### Glare / Reflection

- high-value/overexposure mask
- 후보와 glare overlap ratio 계산
- 고정 위치와 과도한 밝기를 함께 고려
- reflection을 유면으로 확정하지 않는다.

### Residue / Oil Trace

- static edge 가능성
- 강한 edge지만 above/below region contrast가 작은 경우 penalty
- temporal state와 맞지 않는 경우 penalty
- exclusion zone으로 수동 제거 가능

### Static Artifact Model

분석 전 또는 초반 frame sample에서 반복 edge를 누적할 수 있다.

- hard reject 금지
- penalty feature로만 사용
- 실제 유면이 정지해 있을 가능성을 고려

### User-confirmed Artifact Templates

Detector가 분석 ellipse 내부의 point/line/region artifact 후보를 제안할 수
있다. 사용자는 source frame 위의 선택 highlight를 확인하고 하나 또는
여러 후보를 명시적으로 Artifact로 적용한다. 일괄 적용은 사용자가 검토한
선택 집합에 대한 편집 편의이며 자동 truth가 아니다.

- 저장 geometry는 ellipse-relative normalized coordinate를 사용
- 선택 전에는 detector 결과나 Recipe를 변경하지 않음
- user-confirmed match는 후보 provenance를 보존한 채 publication에서 제외
- 하나의 Y 전체를 제거하지 않고 선택한 horizontal/spatial geometry만 적용
- calibration으로 모든 후보가 사라지면 `UNKNOWN_REVIEW` 유지
- calibration 자체는 Oil/Foam/FULL/EMPTY를 증명하지 않음

## 11.6 FillState

```python
EMPTY_NO_INTERFACE
FILLING_VISIBLE
PARTIAL_VISIBLE
FULL_NO_INTERFACE
DRAINING_VISIBLE
FULL_WITH_FOAM
FOAMING_VISIBLE
UNKNOWN_REVIEW
```

### FULL_NO_INTERFACE

- visible oil-air boundary 없음
- ROI가 oil-like 상태
- 내부 artifact를 억지 유면으로 선택하지 않음
- graph 데이터는 numeric level `null`
- 상태는 `ABOVE_VISIBLE_RANGE`

### DRAINING_VISIBLE

- 이전 상태가 full
- 상단 근처에서 air region이 출현
- boundary가 아래로 진행

### EMPTY_NO_INTERFACE

- visible oil-air boundary 없음
- ROI가 air-like 상태
- numeric level `null`
- 상태는 `BELOW_VISIBLE_RANGE`

### FILLING_VISIBLE

- 이전 상태가 empty
- 하단 근처에서 oil region 출현
- boundary가 위로 진행

### FULL_WITH_FOAM

- oil-air boundary 없음
- full 상태
- 하단과 연결된 foam 영역 존재
- foam front만 별도 반환

### FOAMING_VISIBLE

- oil-air boundary와 foam front가 동시에 존재하거나
- partial oil 상태에서 foam front가 별도 식별됨

### UNKNOWN_REVIEW

- 증거 부족
- glare/fogged
- candidate 충돌
- confidence 미달

## 11.7 Foam Front 정의

Foam front는 단순히 ROI 내 가장 높은 기포가 아니다.

MVP 정의:

> **Glass 하단과 연결된 foam/bubbly-oil 영역의 최상단 경계**

하단과 연결되지 않은 산발적 bubble cluster는 foam presence/coverage flag로 기록할 수 있지만 foam front line으로 확정하지 않는다.

## 11.8 Current-Frame Tracker and Final Sequence Resolver

Serialized current-frame tracker는 online/preview observation에 대해 다음을 수행한다.

- previous selected y
- estimated velocity
- max jump
- state transition bonus/penalty
- state hold frames
- raw/smoothed 값 분리
- short detection loss bridging
- full/empty out-of-range 상태 유지

고정 artifact는 시간적으로 안정적일 수 있으므로 “N frame 같은 위치”만으로 유면을 확정하면 안 된다.

Completed production analysis는 sampled window가 모두 수집된 뒤 하나의 bounded deterministic sequence owner를 추가로 적용한다.

- same-frame Oil 후보, explicit no-interface state와 UNKNOWN을 함께 비교
- confirmed initial FULL/EMPTY는 state prior로만 사용하고 numeric 위치로 변환 금지
- hard unavailable, severe glare/exclusion/border, 구조/물리 topology conflict 유지
- 장구간 후보 path는 독립 material anchor cluster가 없으면 UNKNOWN 처리
- near-black/reframe 구간은 전처리 후의 가짜 구조가 아니라 raw effective-ROI photometry로 unavailable 처리
- 최종 frame 수, timestamp, Glass identity 보존
- resolver 실패 또는 identity/cardinality 변경 시 분석 실패 처리

Final Oil/state가 확정된 뒤 Foam sequence owner가 current-frame component의 adjacent-frame 변화/front evolution을 비교한다. Static prelude, 한 방울/단일 frame component와 장기 미지원 gap은 Foam episode를 만들 수 없고, Foam은 Oil 후보나 FULL/EMPTY를 선택할 권한이 없다.

Final result의 missing run은 missing으로 유지한다. Graph의 점선 bridge는 저장된 두 관측 endpoint만 연결하는 display 표현이며 sample, event, judgment, overlay 또는 detector feedback을 만들지 않는다.

## 11.9 Detector Output

```python
PhaseDetection:
    glass_id
    frame_index
    time_sec
    fill_state

    oil_air_level_y
    oil_air_level_px_from_zero
    oil_air_level_mm_from_zero

    foam_front_y
    foam_front_px_from_zero
    foam_front_mm_from_zero

    oil_air_confidence
    foam_confidence
    visibility_confidence
    overall_confidence

    raw values
    smoothed values
    selected candidates
    sequence provenance / unavailable reason
    flags
    debug payload
```

---

# 12. Analysis Pipeline

## 12.1 Timestamp Sampling

- analysis start부터 end까지 timestamp schedule 생성
- requested sampling FPS에 맞춰 timestamp 선택
- source FPS보다 높은 sampling 금지
- VFR에서 `frame_index += N` 방식만 사용하지 않음
- 각 sample에 실제 decoded timestamp 기록

## 12.2 Multi-Glass Processing

한 frame을 decode한 뒤 enabled Glass를 모두 처리한다.

```text
decode frame once
→ Glass A effective crop/detect
→ Glass B effective crop/detect
→ Glass C effective crop/detect
```

같은 source frame을 Glass마다 재decode하지 않는다.

## 12.3 Background Analysis

GUI event loop를 block하지 않는다.

필수:

- worker thread/process
- progress callback
- cancellation token
- error propagation
- partial output는 실패 상태로 명확히 표시
- 취소 시 incomplete result를 최종 결과처럼 노출하지 않음

## 12.4 Analysis Stages

```text
1. Session/Recipe validation
2. Video open and metadata validation
3. Timestamp schedule
4. Optional static artifact sampling
5. Frame decode
6. Per-glass phase detection
7. Completed-window Oil/FULL/EMPTY/UNKNOWN sequence resolution (지원 detector)
8. Post-Oil Foam episode resolution (지원 detector)
9. TrackingSample 최종 projection
10. Legacy/current-frame stream의 eligible leading-interval retrospective FULL/EMPTY interpretation
11. Event detection
12. Judgment
13. Event frame capture
14. Graph rendering
15. HTML/CSV export
16. Result summary
```

---

# 13. Event Detection

Event detector는 raw image를 직접 해석하지 않고 immutable final-analysis `TrackingSample`과, legacy/current-frame stream에 적용 가능한 경우 별도로 provenance가 유지되는 retrospective sequence interpretation을 사용한다. R5 sequence-resolved state는 retrospective owner가 다시 변경하지 않는다. Retrospective state가 event semantics에 참여하면 inferred state 사용 사실이 first-class evidence로 남아야 하며 observed `fill_state` 자체는 변경하지 않는다.

필수 이벤트:

```text
ANALYSIS_START
ANALYSIS_END
COMPRESSOR_START

OIL_BOUNDARY_APPEARED_FROM_TOP
OIL_BOUNDARY_APPEARED_FROM_BOTTOM
OIL_DROP_START
MAXIMUM_OIL_LEVEL
MINIMUM_OIL_LEVEL
ZERO_CROSS_UP
ZERO_CROSS_DOWN
ZERO_STABLE_RECOVERY

FULL_NO_INTERFACE_START
EMPTY_NO_INTERFACE_START

FOAM_START
FOAM_FRONT_RISING
FOAM_REACH_ZERO
FOAM_REACH_TOP
FOAM_END

LOW_CONFIDENCE_START
LOW_CONFIDENCE_END
DETECTION_LOST
FOGGED_OR_GLARE
REVIEW_REQUIRED

JUDGMENT_PASS
JUDGMENT_FAIL
```

Event는 debounce와 minimum duration을 가져야 하며 한 frame noise로 생성하지 않는다.

Domain event 전체는 engineering/audit surface에 보존한다. 사용자 report는 이 목록을 그대로 확장하지 않고 최고·최저, 압축기 기동, Oil 변화와 bounded Foam episode 등 물리적 landmark를 선별한다. Report-only Foam episode grouping은 저장된 Foam observation을 변경하지 않는다.

각 event는 다음을 가진다.

- glass ID
- type
- start/end time
- representative frame
- oil level
- foam level
- confidence
- note
- capture path

---

# 14. 판정 명세

## 14.1 공통 Result State

```text
PASS
FAIL
REVIEW_REQUIRED
NOT_APPLICABLE
```

## 14.2 Valid Coverage

판정 전에 valid sample ratio를 계산한다.

```text
valid samples / expected samples
```

minimum valid coverage 미달이면 `REVIEW_REQUIRED`다.

`FULL_NO_INTERFACE`와 `EMPTY_NO_INTERFACE`는 observed confidence가 충분하고 상태가 명확하면 observed valid 상태로 계산할 수 있다. `UNKNOWN_REVIEW`, `DETECTION_LOST`는 observed invalid다. Retrospective interpretation은 observed sample validity를 바꾸지 않는다.

Official result semantics는 **observed coverage**와, retrospective interpretation이 공식 상태 의미에 참여할 때의 **effective state-aware coverage**를 구분해야 한다. Judgment가 retrospective state를 사용하면 그 provenance가 결과에 남아야 한다. `RECOVERY`처럼 numeric Oil recovery를 요구하는 판정은 retrospective FULL/EMPTY가 아니라 observed numeric Oil에 계속 의존한다.

## 14.3 RECOVERY

- 기준: oil-air level
- full 상태에서 시작한 경우 visible boundary가 나타난 뒤 평가할 수 있음
- foam front는 별도 정보이며 oil-air recovery를 대신하지 않음
- zero line 이상 crossing 후 stable hold 충족
- deadline 내 미충족: FAIL
- confidence 부족: REVIEW_REQUIRED

## 14.4 HOLD_BELOW_ZERO

- smoothed oil-air level이 threshold 아래 유지
- 허용 excursion 시간/높이 초과: FAIL
- full/above-visible 상태가 발생하면 FAIL 또는 rule 설정에 따라 처리
- unknown 과다: REVIEW_REQUIRED

## 14.5 HOLD_ABOVE_ZERO

- smoothed oil-air level이 threshold 위 유지
- 허용 violation 시간/깊이 초과: FAIL
- empty/below-visible 상태가 발생하면 FAIL
- unknown 과다: REVIEW_REQUIRED

## 14.6 Overall Result

기본 정책:

- enabled Glass 모두 PASS: PASS
- 하나라도 FAIL: FAIL
- FAIL은 없지만 하나라도 REVIEW_REQUIRED: REVIEW_REQUIRED
- 판정 대상이 없는 경우: NOT_APPLICABLE

---

# 15. 결과물

## 15.1 Output Bundle

```text
oil_level_analysis_YYYYMMDD_HHMMSS/
├─ report.html
├─ tracking_data.csv
├─ events.csv
├─ recipe_snapshot.oilrecipe
├─ session.json
├─ analysis_manifest.json
│
├─ captures/
│  ├─ glass_A_zero_recovery.png
│  ├─ glass_A_minimum.png
│  └─ glass_B_foam_start.png
│
├─ graphs/
│  ├─ combined_levels.png
│  ├─ glass_A_detail.png
│  └─ glass_B_detail.png
│
├─ assets/
│  └─ report assets
│
├─ logs/
│  └─ analysis.log
│
└─ debug/                 # debug export 활성화 시에만
```

## 15.2 tracking_data.csv

필수 column:

```text
run_id
glass_id
frame_index
timestamp_sec
fill_state

raw_oil_air_level_y
raw_oil_air_level_px_from_zero
raw_oil_air_level_mm_from_zero
smoothed_oil_air_level_px_from_zero
smoothed_oil_air_level_mm_from_zero
oil_air_confidence

raw_foam_front_y
raw_foam_front_px_from_zero
raw_foam_front_mm_from_zero
smoothed_foam_front_px_from_zero
smoothed_foam_front_mm_from_zero
foam_confidence

visibility_confidence
overall_confidence
is_valid
flags
```

mm/pixel이 없으면 mm column은 빈 값이다.

`tracking_data.csv`의 `fill_state`, numeric fields와 `is_valid`는 원래 detector observation을 보존한다. Retrospective FULL/EMPTY를 accepted하더라도 observed `fill_state`를 교체하지 않는다. Retrospective interpretation은 accepted/unresolved/conflict status와 inference provenance를 가진 별도 persisted result responsibility다.

## 15.3 events.csv

```text
run_id
glass_id
event_type
start_time_sec
end_time_sec
representative_frame_index
oil_level_px
oil_level_mm
foam_front_px
foam_front_mm
confidence
capture_path
note
```

## 15.4 HTML Report

필수 section:

1. Test/Run 및 전체 판정 summary
2. Combined graph
3. Glass별 관측 흐름 설명
4. Glass별 annotated oil-air/foam graph
5. 관측 최고·최저와 주요 물리 event
6. 주요 event의 inline Glass 중심 source capture
7. 직접 유면 위치가 없는 구간에 대한 간결한 설명
8. Glass별 plain-language 판정 안내와 warning
9. 접을 수 있는 Recipe/analysis/source/software provenance

HTML은 외부 네트워크 없이 열려야 하며 output bundle 안에서 상대 경로를 사용한다.

Main report는 raw event/confidence/debug table이나 source metadata dictionary dump를 표시하지 않는다. 전체 `events.csv`, `tracking_data.csv`, Result Review와 optional debug artifact는 별도 engineering/audit surface로 계속 제공한다.

## 15.5 Graph 표현 규칙

- 연속된 finite oil-air observation: 실선
- 하나 이상의 missing sample을 사이에 둔 두 finite Oil anchor의 graph-only 연결: 점선
- foam front: 별도 series
- FULL_NO_INTERFACE: top out-of-range state band
- EMPTY_NO_INTERFACE: bottom out-of-range state band
- UNKNOWN_REVIEW: review background band
- zero line: 고정 기준선
- 사용자에게 의미 있는 최고·최저/Foam/기준점 통과 등의 landmark: 한글 label marker
- numeric 값이 없는 full/empty 상태에 임의의 가짜 높이를 CSV에 쓰지 않는다.
- Oil series의 저장값은 관측 결과 그대로 유지한다. `null`/non-finite sample은 graph vertex로 만들지 않고, 저장된 finite Oil anchor들만 시간순으로 하나의 presentation trajectory로 연결한다. 직접 연속 observation은 실선, missing run을 건너는 연결은 점선으로 구분한다.
- 점선 bridge는 앞뒤 두 finite anchor만 vertex로 사용하며 누락 timestamp의 CSV/TrackingSample/overlay numeric 값을 만들거나 detector observation을 보간·수정하지 않는다. `UNKNOWN_REVIEW`와 no-interface 상태 표시는 연결 뒤에도 보이되 Oil movement를 가릴 정도로 지배적으로 렌더링하지 않는다.
- finite Oil anchor가 하나도 없으면 Oil line을 표시하지 않는다. Foam front는 실제 부재 의미를 보존하기 위해 누락 구간을 연결하지 않는다.
- retrospective FULL/EMPTY가 accepted되어도 graph/overlay에 새 numeric Oil anchor를 합성하지 않는다. Retrospective interpretation만으로 presentation polyline의 시작점·끝점 또는 중간 vertex를 추가할 수 없다.

## 15.6 Result semantics compatibility

Recipe schema는 기존 호환성을 유지하고 `AUTO`를 계속 보존한다. Current-run initial-state confirmation은 별도 session/run provenance이며 Recipe persistence가 아니다. 그 confirmation이 없는 기존 session/bundle은 기존 observed-only 의미를 유지한다.

기존 v1 observed-only result bundle은 기존 의미로 계속 읽을 수 있어야 한다. Retrospective interpretation이 official event/judgment/coverage semantics에 참여하는 신규 bundle은 **명시적인 더 새로운 result/review semantics version**을 사용해야 한다.

새 reader는 legacy v1 observed-only bundle과 새로운 retrospective semantics를 모두 지원한다. 반대로 v1-only application은 newer retrospective-semantics bundle을 ordinary v1처럼 조용히 표시해서는 안 되며 명시적으로 실패해야 한다.

Versioned compatibility와 separate retrospective provenance가 요구사항이다. Version field나 retrospective artifact가 어느 physical file/field에 위치하는지는 별도 accepted implementation contract가 정하지 않는 한 구현 책임으로 남긴다.

---

# 16. 기술 스택과 라이브러리

## 16.1 필수

- Python 3.11 계열
- PySide6
- NumPy
- OpenCV
- Jinja2
- matplotlib 또는 동등한 정적 graph renderer
- pytest
- PyInstaller

## 16.2 OpenCV 패키지

제품 GUI는 PySide6가 담당한다. OpenCV HighGUI에 의존하지 않는다.

권장:

```text
opencv-python-headless
```

다만 개발환경에서 `cv2.imshow` 등을 별도로 사용한다면 `opencv-python`을 선택할 수 있다. 두 패키지를 동시에 설치하지 않는다.

## 16.3 선택/후속

- pyqtgraph: GUI interactive graph
- openpyxl: 향후 XLSX
- scikit-image: experimental detector 비교
- scipy: advanced signal processing

scikit-image와 scipy는 MVP core 의존성으로 강제하지 않는다.

---

# 17. 아키텍처

## 17.1 원칙

- MVC 관점에서 View, Controller, Model/UseCase 분리
- Hexagonal Architecture 관점에서 core와 adapter 분리
- UI는 detector 구현을 모름
- application은 OpenCV/PySide6를 import하지 않음
- domain은 순수 Python
- report/export는 adapter
- dependency wiring은 bootstrap
- `AnalysisResult`가 모든 exporter의 공통 입력

## 17.2 의존성 방향

```text
ui → application → domain
adapters → application ports / domain
bootstrap → concrete wiring
```

금지:

```text
domain → cv2
domain → PySide6
application → cv2
application → PySide6
application → Jinja2/matplotlib/openpyxl
ui widget 내부에서 Canny/Hough/Sobel 구현
```

---

# 18. 권장 코드베이스 구조

```text
rotary-oil-level-tracker/
├─ pyproject.toml
├─ README.md
├─ .gitignore
│
├─ src/
│  └─ oil_tracker/
│     ├─ __main__.py
│     ├─ bootstrap.py
│     │
│     ├─ domain/
│     │  ├─ geometry.py
│     │  ├─ recipe.py
│     │  ├─ session.py
│     │  ├─ detection.py
│     │  ├─ tracking.py
│     │  ├─ events.py
│     │  ├─ judgment.py
│     │  ├─ results.py
│     │  ├─ enums.py
│     │  └─ validation.py
│     │
│     ├─ application/
│     │  ├─ ports/
│     │  │  ├─ video_reader.py
│     │  │  ├─ phase_detector.py
│     │  │  ├─ recipe_repository.py
│     │  │  ├─ report_exporter.py
│     │  │  ├─ result_store.py
│     │  │  └─ progress.py
│     │  ├─ use_cases/
│     │  │  ├─ create_recipe.py
│     │  │  ├─ load_recipe.py
│     │  │  ├─ save_recipe.py
│     │  │  ├─ validate_workbench.py
│     │  │  ├─ preview_detection.py
│     │  │  ├─ analyze_video.py
│     │  │  └─ export_result.py
│     │  └─ services/
│     │     ├─ recipe_validation_service.py
│     │     ├─ analysis_pipeline.py
│     │     ├─ event_detection_service.py
│     │     └─ judgment_service.py
│     │
│     ├─ adapters/
│     │  ├─ vision/
│     │  │  ├─ opencv_video_reader.py
│     │  │  ├─ geometry_masks.py
│     │  │  ├─ preprocessing.py
│     │  │  ├─ row_features.py
│     │  │  ├─ artifact_detector.py
│     │  │  ├─ candidate_generators.py
│     │  │  ├─ candidate_scorer.py
│     │  │  ├─ fill_state_classifier.py
│     │  │  ├─ foam_front_detector.py
│     │  │  ├─ temporal_tracker.py
│     │  │  ├─ opencv_phase_detector.py
│     │  │  └─ debug_renderer.py
│     │  │
│     │  ├─ reporting/
│     │  │  ├─ html_reporter.py
│     │  │  ├─ csv_exporter.py
│     │  │  ├─ graph_renderer.py
│     │  │  └─ templates/
│     │  │     └─ report.html.j2
│     │  │
│     │  ├─ storage/
│     │  │  ├─ json_recipe_repository.py
│     │  │  ├─ output_bundle_store.py
│     │  │  └─ image_capture_store.py
│     │  │
│     │  └─ system/
│     │     ├─ app_paths.py
│     │     ├─ settings_store.py
│     │     └─ logging_config.py
│     │
│     ├─ ui/
│     │  ├─ main_window.py
│     │  ├─ wizard/
│     │  │  └─ new_recipe_wizard.py
│     │  ├─ widgets/
│     │  │  ├─ glass_list_panel.py
│     │  │  ├─ video_overlay_canvas.py
│     │  │  ├─ transport_bar.py
│     │  │  ├─ glass_settings_panel.py
│     │  │  ├─ validation_panel.py
│     │  │  ├─ analysis_progress_dialog.py
│     │  │  ├─ result_review_view.py
│     │  │  └─ debug_panel.py
│     │  ├─ models/
│     │  │  └─ glass_list_model.py
│     │  └─ controllers/
│     │     ├─ workbench_controller.py
│     │     ├─ preview_controller.py
│     │     ├─ analysis_controller.py
│     │     └─ export_controller.py
│     │
│     ├─ config/
│     │  ├─ defaults.py
│     │  └─ schemas.py
│     │
│     └─ resources/
│        ├─ icons/
│        └─ styles/
│
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ gui/
│  ├─ fixtures/
│  │  ├─ images/
│  │  ├─ videos/
│  │  └─ recipes/
│  └─ golden/
│
├─ packaging/
│  └─ pyinstaller/
│     └─ oil_tracker.spec
│
├─ docs/
└─ scripts/
```

---

# 19. Domain Model 핵심

## 19.1 Geometry

```python
EllipseGeometry
ExclusionZone
ZeroLine
GlassGeometry
```

## 19.2 Recipe

```python
InspectionRecipe
GlassInspectionConfig
DetectorSettings
JudgmentRule
```

## 19.3 Session

```python
AnalysisSession
VideoMetadata
AnalysisRange
```

## 19.4 Detection

```python
FillState
BoundaryKind
BoundaryCandidate
PhaseDetection
PhaseDetectionDebugResult
```

## 19.5 Result

```python
TrackingSample
EventMarker
GlassAnalysisResult
AnalysisResult
ResultState
```

모든 dataclass/domain model은 GUI object, `np.ndarray`, OpenCV object를 직접 저장하지 않는다. Debug image 같은 binary/array payload는 application DTO 또는 adapter-owned artifact reference로 전달한다.

---

# 20. Threading, Responsiveness, Error Handling

## 20.1 UI Responsiveness

다음 작업은 main UI thread에서 수행하지 않는다.

- video full analysis
- report rendering
- large CSV write
- debug frame-range export
- long video seek/decode

단일 frame preview도 debounce 및 worker 사용을 권장한다.

## 20.2 Error Handling

사용자 메시지는 다음을 구분한다.

- 입력 오류
- Recipe validation 오류
- video decode 오류
- detector 오류
- export 오류
- 취소
- 예상하지 못한 내부 오류

내부 예외 stack trace를 그대로 사용자에게 노출하지 않는다. 로그 파일에는 상세 정보를 남긴다.

## 20.3 Recovery

- 분석 실패 시 Workbench 설정 유지
- save 실패 시 기존 Recipe 파일 손상 방지
- atomic write 사용
- output bundle 생성 중 실패하면 manifest에 `FAILED` 상태 기록 또는 임시 폴더 정리

---

# 21. 재현성 및 Audit 정보

`analysis_manifest.json`에 다음을 저장한다.

- app version
- detector version
- recipe schema version
- Recipe ID
- Recipe snapshot hash
- source video path
- video size, mtime
- optional video hash
- source metadata
- sampling FPS
- analysis range
- detector settings
- run start/end
- result status
- warnings/errors

같은 Recipe와 영상으로 재분석한 결과를 비교할 수 있어야 한다.

---

# 22. 테스트 전략

## 22.1 Unit Tests

필수:

- ellipse/display coordinate transform
- ellipse mask 생성
- margin erosion
- exclusion mask
- zero line px/mm 변환
- Recipe serialization round-trip
- schema version handling
- structural/readiness validation
- judgment modes
- event crossing/debounce
- candidate scoring
- glare/border penalty
- fill state transition
- foam bottom-connectivity

## 22.2 Synthetic Vision Fixtures

인공 이미지로 다음 케이스를 생성한다.

- partial oil with clear horizontal boundary
- full oil, no boundary
- empty glass, no boundary
- boundary entering from top
- boundary entering from bottom
- strong glass rim
- horizontal reflection
- residue line
- exclusion zone on artifact
- foam-like texture from bottom
- scattered bubbles not connected to bottom
- glare/fogged/unknown

## 22.3 Golden Video Fixtures

실제 시험 영상 일부를 짧은 fixture로 관리한다.

각 fixture에는 수동 annotation을 둔다.

- frame/timestamp
- expected FillState
- expected oil-air y range
- expected foam front y range
- expected event
- acceptable confidence state

정확도 threshold는 데이터셋 확보 후 결정한다. 단, regression harness는 초기부터 만든다.

## 22.4 Integration Tests

- Recipe + video → AnalysisResult
- AnalysisResult → HTML/CSV
- output bundle smoke test
- canceled analysis cleanup
- recipe resolution mismatch
- multi-glass single-decode path

## 22.5 GUI Tests

자동화 가능한 항목:

- main window 생성
- wizard navigation
- add/delete Glass
- model-panel binding
- save/load
- validation panel
- preview request routing

Geometry drag/resize와 overlay 정확성은 manual visual acceptance도 수행한다.

## 22.6 Headless Path

GUI가 제품의 핵심이지만 core use case는 GUI 없이 실행 가능해야 한다.

예:

```text
python -m oil_tracker.cli analyze --recipe setup.oilrecipe --video test.mp4
```

CLI 구현은 MVP의 필수 UI 기능은 아니지만, application use case와 integration test가 headless 실행 가능해야 한다.

---

# 23. 구현 순서 권한

이 제품 SSOT는 current milestone sequencing, status 또는 exact next gate를 소유하지 않는다. 초기 구현 단계에서 사용한 Milestone 0–9 순서는 역사적 구현 scaffolding으로 완료되었으며, 현재 프로젝트 순서는 [`00-project/roadmap.md`](00-project/roadmap.md), exact active gate는 [`00-project/work-plan.md`](00-project/work-plan.md)가 소유한다.

현재 실행 대상이 아니지만 명시적으로 유지해야 하는 `RETAINED` / `DEFERRED` / `EVIDENCE-GATED` 책임은 [`00-project/retained-commitments.md`](00-project/retained-commitments.md)에서만 라우팅한다. 이 SSOT의 제품 요구사항을 retained backlog나 milestone status로 재해석하지 않는다.

---

# 24. Acceptance 권한

최종 acceptance는 lifecycle checklist 하나가 아니라 책임별 owner로 분리한다.

- stable product/compatibility 요구사항: 이 SSOT와 `10-product/`;
- durable internal responsibility: `20-architecture/`;
- current validation/benchmark/test acceptance contract: `30-validation/`;
- Windows/package/manual 실행 절차: `40-operations/`;
- completed execution/audit proof: `60-evidence/`.

Milestone `DONE`, current gate 또는 다음 작업을 판단할 때 과거 체크박스나 evidence 파일의 당시 status를 사용하지 않는다. 그 판단은 roadmap/work-plan만 따른다.

---

# 25. 구현 시 금지사항

- 초기 편의를 이유로 `main_window.py`에 OpenCV detector를 구현하지 않는다.
- 가장 강한 Sobel/Canny/Hough line을 무조건 유면으로 선택하지 않는다.
- full/empty 상태에서 numeric 가짜 유면값을 CSV에 기록하지 않는다.
- foam과 oil-air boundary를 하나의 line으로 합치지 않는다.
- Recipe에 현재 video path를 영구적인 core identity로 저장하지 않는다.
- source/display 좌표를 혼용하지 않는다.
- 모든 분석을 UI thread에서 실행하지 않는다.
- scikit-image/scipy/AI 의존성을 근거 없이 추가하지 않는다.
- 기존 reference repository 코드를 license 확인 없이 복사하지 않는다.
- `REVIEW_REQUIRED`를 억지로 PASS/FAIL로 변환하지 않는다.

---

# 26. 구현 에이전트 보고 형식

각 milestone 완료 후 다음을 보고한다.

1. 구현 범위
2. 변경/신규 파일 목록
3. domain/application/adapter/UI 의존성 설명
4. 사용자 실행 방법
5. 실행한 테스트와 결과
6. 생성된 sample artifact
7. 알려진 한계
8. 다음 milestone에 넘길 사항
9. 본 SSOT와 달리 구현한 부분 및 근거

본 SSOT에서 벗어난 변경이 필요하면 구현 전에 명시적으로 기록하고, 사용자의 승인을 받아야 한다.

---

# 27. 최종 제품 Workflow 요약

```text
프로그램 실행
→ Recipe Workbench
→ 새 Recipe wizard 또는 빈 Workbench
→ 영상 선택 및 시험 시간 조건 입력
→ Glass 추가
→ ellipse로 glass 범위 지정
→ zero line / margin / exclusion / 초기 상태 / 판정 모드 설정
→ 여러 frame에서 자동 Preview 및 Debug 확인
→ Recipe 검증 및 저장
→ 전체 분석
→ oil-air / foam tracking
→ event 및 judgment
→ graph / capture Review
→ HTML + CSV output bundle
```

이 workflow와 본 문서의 architecture, detector state model, validation, 결과 schema가 프로젝트의 구현 기준이다.
