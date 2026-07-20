# Result Review Viewer Plan

## 1. 문서 목적

이 문서는 Rotary Oil Level Tracker의 분석 결과를 원본 영상과 함께 재생하고, 검출 결과를 overlay로 확인하는 `Result Review Viewer`의 사용자 경험, 데이터 계약, 구현 범위와 단계별 확장 계획을 정의한다.

전체 UX 우선순위와 Phase 순서는 [`UX_IMPROVEMENT_BACKLOG.md`](./UX_IMPROVEMENT_BACKLOG.md)를 따른다. 이 문서는 그중 **Phase 2B 이후 Result Review Viewer 관련 기능의 상세 설계 문서**다.

## 2. 구현 현황

### Phase 2B-1 — Result Review Viewer MVP

**완료**

PR #9 `feat: add result review viewer MVP`로 `main`에 반영했다.

- PR head: `2f948a57171586665b20c5f814f1d7d2c2863142`
- main merge SHA: `faeb31a54d1e7d88ebee79a8ee33769fb24dd8c0`
- 검증: Python 3.13 및 3.14에서 각각 `175 passed`
- 기존 bundle과 신규 `review_index.json` bundle 모두 지원
- 실제 Windows DPI, 장시간 실영상 seek와 overlay 좌표 검증은 수동 확인 항목으로 유지

### Phase 2B-2 — 일반 검토 강화

**다음 작업**

- tracking graph와 영상 timeline 동기화
- 그래프 클릭 seek
- 검토 필요 항목 필터
- 결과 보고서와 결과 폴더 연결
- 분석 완료 화면에서 Viewer 바로 열기
- 같은 profile로 새 영상 분석

### Phase 2C 이후

**예정**

- Debug Viewer
- detector 내부 후보와 score 표시
- 부분 재검출과 설정 비교
- 사용자 수동 정답과 regression fixture
- annotated MP4 export

## 3. 목표

Result Review Viewer는 하나의 기반 위에서 두 목적을 지원한다.

1. **일반 사용자 결과 검토**
   - 분석 결과가 실제 영상과 일치하는지 직관적으로 확인
   - 이벤트와 낮은 신뢰도 구간을 빠르게 탐색
   - HTML 보고서만으로 이해하기 어려운 판정 근거를 영상으로 확인

2. **개발자 디버그 및 detector 개선**
   - 후보선, 점수, penalty와 상태 전이 근거 확인
   - 실패 장면을 재현하고 문제 유형 분류
   - 향후 detector 회귀 테스트와 튜닝 자료로 활용

Phase 2B는 일반 사용자 결과 검토에 집중하고, detector 내부 정보는 Phase 2C에서만 노출한다.

## 4. 핵심 원칙

- 원본 영상을 다시 인코딩하지 않고 원본 frame 위에 저장된 결과를 실시간 overlay한다.
- Viewer는 detector를 다시 실행하지 않는다.
- Viewer는 Workbench의 현재 recipe와 session이 아니라 결과 bundle의 snapshot을 사용한다.
- 일반 모드에서는 최종 결과만 표시하고 detector 내부 후보와 점수는 숨긴다.
- 원본 영상이 이동되었을 때 사용자가 세션 한정 대체 경로를 지정할 수 있다.
- 대체 영상의 geometry를 자동 scale하거나 이동하지 않는다.
- 기존 `report.html`, CSV와 `.oilrecipe` 형식을 유지한다.
- 신규 index가 없는 기존 결과 bundle도 계속 열 수 있어야 한다.
- Viewer의 video reader, playback state와 lifecycle은 Workbench와 분리한다.

## 5. 사용자 흐름

### 5.1 기존 결과 열기

- Workbench의 `결과 검토` action 선택
- 최근 결과 또는 다른 결과 bundle 폴더 선택
- Viewer가 bundle 유효성 검사
- 원본 영상이 있으면 분석 시작 시점으로 로드
- 원본 영상이 없으면 분석 당시 경로를 표시하고 재지정 action 제공

Viewer 자체에서도 다른 bundle을 열 수 있다.

지원 입력:

- 결과 bundle directory
- `analysis_manifest.json`
- `review_index.json`

### 5.2 분석 완료 직후 — Phase 2B-2

분석 완료 화면에서 다음 행동을 제공한다.

- 결과 영상 검토
- 결과 보고서 열기
- 결과 폴더 열기
- 같은 profile로 새 영상 분석
- 닫기

이 흐름은 Phase 2B-2에서 구현한다.

## 6. 화면 구조

```text
┌ 좌측: 관찰창·이벤트 목록 ┬ 중앙: 원본 영상 + overlay ┬ 우측: 현재 시점 정보 ┐
└ 하단: 재생 제어 · timeline · 이벤트/신뢰도 marker · 그래프                ┘
```

Phase 2B-1에서는 그래프를 제외한 Viewer 기반을 구현했다.

### 6.1 좌측 패널

- 관찰창 선택
- 관찰창별 판정 상태
- 이벤트 목록
- 낮은 신뢰도·검토 필요 구간 목록
- 이전/다음 항목 이동
- event confidence와 note
- event capture 존재 여부

MVP는 한 번에 하나의 관찰창 overlay를 표시한다.

### 6.2 중앙 영상 영역

일반 모드 기본 overlay:

- ROI 타원
- 기준점
- 최종 oil-air boundary
- 최종 foam front
- 관찰창 이름
- fill state
- confidence
- 영상 timestamp
- tracking sample timestamp
- low-confidence 또는 invalid 상태 강조

Viewer canvas는 read-only다.

다음 편집 기능은 제공하지 않는다.

- ROI drag 또는 resize
- 기준점 drag
- exclusion 이동
- recipe mutation
- Undo command 생성

### 6.3 우측 정보 패널

현재 video timestamp와 선택된 tracking sample 기준:

- 영상 timestamp와 decoded frame index
- tracking sample timestamp
- 선택 관찰창
- fill state
- 유면 위치
- 기준점 대비 px와 mm
- foam front 위치
- overall confidence
- valid 여부
- flags
- 활성 event
- 검토 필요 사유
- boundary가 ROI 밖이어서 표시되지 않은 경우의 상태

### 6.4 하단 timeline

- 재생과 일시정지
- 이전/다음 frame
- 0.5×, 1×, 1.5×, 2×, 4× 배속
- seek
- 분석 시작·종료 marker
- 압축기 기동 marker
- event marker와 duration
- low-confidence interval
- 현재 timestamp cursor

## 7. Phase 2B-1 구현 계약

### 7.1 Result bundle reader

필수 기존 파일:

```text
analysis_result/
├─ report.html
├─ tracking_data.csv
├─ events.csv
├─ recipe_snapshot.oilrecipe
├─ session.json
├─ analysis_manifest.json
├─ review_index.json          # 신규 bundle
├─ captures/
├─ graphs/
├─ assets/
└─ logs/
```

Reader 규칙:

- CSV는 `utf-8-sig`로 읽는다.
- 숫자, bool, enum, nullable 값과 flags를 명시적으로 변환한다.
- sample과 event는 glass ID와 timestamp 기준으로 deterministic하게 정렬한다.
- `events.csv`가 header만 있는 경우 허용한다.
- usable tracking row가 없으면 bundle 오류다.
- tracking 또는 event의 glass ID가 recipe snapshot에 없으면 오류다.
- malformed row는 파일명과 row 위치를 포함한 사용자용 오류로 보고한다.
- bundle 내부 파일의 절대경로, `..`와 bundle root 밖 resolve를 거부한다.
- source video는 bundle 외부 절대경로일 수 있다.

### 7.2 `review_index.json`

신규 bundle은 schema version 1 index를 생성한다.

```json
{
  "schema_version": 1,
  "run_id": "...",
  "source_video_path": "...",
  "source_metadata": {},
  "analysis_range": [0.0, 120.0],
  "compressor_start_sec": 10.0,
  "recipe_snapshot": "recipe_snapshot.oilrecipe",
  "session": "session.json",
  "tracking_data": "tracking_data.csv",
  "events": "events.csv",
  "manifest": "analysis_manifest.json",
  "glasses": [],
  "debug_trace_level": "none"
}
```

원칙:

- bundle 구성 파일은 상대경로다.
- `analysis_manifest.json`은 `review_index` pointer를 가진다.
- 기존 CSV column과 report 파일은 변경하지 않는다.
- index가 없는 기존 bundle은 manifest, session, recipe와 CSV에서 동일한 `ReviewBundle` model로 복원한다.
- MVP의 event timestamp index와 low-confidence interval은 index에 중복 저장하지 않고 CSV에서 load 시 계산한다.
- 향후 대형 결과의 성능상 필요성이 확인되면 backward-compatible index 확장을 별도 schema version으로 검토한다.

### 7.3 `tracking_data.csv`

Viewer는 기존 CSV column을 그대로 사용한다.

주요 필드:

- `timestamp_sec`
- `frame_index`
- `glass_id`
- `fill_state`
- raw oil-air Y와 기준점 대비 px/mm
- smoothed oil-air 기준점 대비 px/mm
- raw foam-front Y와 기준점 대비 px/mm
- smoothed foam-front 기준점 대비 px/mm
- confidence
- `is_valid`
- flags

최종 overlay Y 복원:

Oil-air boundary:

1. `zero_line_y - smoothed_oil_air_level_px_from_zero`
2. 값이 없으면 `raw_oil_air_level_y`
3. 둘 다 없으면 표시하지 않음

Foam front:

1. `zero_line_y - smoothed_foam_front_px_from_zero`
2. 값이 없으면 `raw_foam_front_y`
3. 둘 다 없으면 표시하지 않음

복원된 Y가 타원 밖이면 boundary를 표시하지 않고 상세 패널에 상태를 남긴다.

### 7.4 시간 동기화

현재 decoded video timestamp 이하에서 가장 최근 tracking sample을 사용한다.

- exact timestamp가 있으면 exact sample
- sample 사이에서는 이전 sample 유지
- duplicate timestamp는 timestamp, frame index와 입력 순서로 deterministic하게 선택
- 분석 시작 전과 종료 후에는 tracking overlay를 표시하지 않음
- seek 후 요청 timestamp가 아니라 actual decoded timestamp를 사용
- video timestamp와 tracking sample timestamp를 별도로 표시

### 7.5 검토 필요 interval

다음 조건을 만족하는 sample은 검토 필요 대상으로 분류한다.

- `is_valid == false`
- snapshot의 `minimum_final_confidence` 미만
- `LOW_CONFIDENCE`
- `DETECTION_LOST`
- `FOGGED_OR_GLARE`
- `REVIEW_REQUIRED`
- `UNKNOWN_REVIEW`
- foam, review, glare 또는 lost 관련 명시적 flag

연속 sample은 session sampling FPS 또는 timestamp 간격을 기준으로 interval로 묶는다.

대표 timestamp:

- 최저 confidence sample 우선
- 동률이면 가장 이른 timestamp
- 이후 frame index와 입력 순서로 deterministic 결정

### 7.6 원본 영상 탐색과 재지정

탐색 순서:

1. 현재 Viewer session override
2. `review_index.json` source path
3. manifest source path
4. `session.json` input video path
5. bundle directory 또는 바로 위 directory의 동일 basename 파일

광범위한 디스크 검색은 하지 않는다.

대체 영상 검증:

- width와 height 불일치: 적용 거부
- FPS, duration과 codec 차이: warning
- geometry 자동 scaling 또는 이동 없음
- override는 bundle에 저장하지 않고 현재 Viewer session에서만 유지

영상이 없어도 bundle metadata, 관찰창, event와 검토 필요 목록을 볼 수 있다.

### 7.7 Event navigation

- 관찰창별 timestamp 정렬
- point event와 duration event 지원
- event type 한글 label
- confidence와 note 표시
- capture path 존재 여부 표시
- 선택 시 재생을 멈추고 event 시작 시각으로 seek

### 7.8 Overlay PNG 저장

- 축소된 widget screenshot을 사용하지 않는다.
- 원본 frame 해상도로 overlay를 다시 render한다.
- ROI, 기준점, 최종 유면, foam, 상태, confidence와 timestamp를 포함한다.
- `.png` 확장자를 보정한다.
- Unicode 경로를 지원한다.
- 파일명에 사용할 수 없는 문자를 안전하게 치환한다.
- 공식 분석 결과 파일을 자동으로 덮어쓰지 않는다.

### 7.9 Lifecycle

- Viewer별 독립 `OpenCvVideoReader`
- 다른 bundle을 열 때 기존 reader close
- 원본 영상 교체 시 기존 reader 정리
- Viewer close 시 playback timer 정지와 reader close
- generation 값으로 이전 frame update 무효화
- Workbench close 시 Viewer 정리
- Viewer 조작이 Workbench current frame, selection, recipe, preview와 preflight 상태를 변경하지 않음

## 8. Phase 2B-2 — 일반 검토 강화

### 8.1 Tracking graph

- 선택 관찰창의 oil level과 foam front 추세
- confidence 또는 valid 상태 표시
- 현재 재생 시각 cursor
- 그래프 클릭 시 영상 seek
- 영상 seek 시 그래프 cursor 동기화
- 분석 구간과 event marker 표시

Graph는 저장된 tracking data만 사용하며 detector를 실행하지 않는다.

### 8.2 검토 필터

- 전체 결과
- event만
- 낮은 신뢰도만
- invalid sample만
- foam·glare·lost 사유별 필터

필터는 공식 결과를 변경하지 않는다.

### 8.3 결과 action 연결

Viewer에서 다음 action을 제공한다.

- `report.html` 열기
- 결과 bundle 폴더 열기
- event capture 열기
- 같은 profile로 새 영상 분석

상대경로는 bundle root 밖으로 탈출하지 않도록 검증한다.

### 8.4 분석 완료 화면

분석 완료 후 단순 information box 대신 다음 행동을 제공한다.

- 결과 영상 검토
- 결과 보고서 열기
- 결과 폴더 열기
- 같은 profile로 새 영상 분석
- 닫기

Viewer 진입 실패가 분석 결과 자체를 실패 상태로 바꾸면 안 된다.

### 8.5 같은 profile로 새 영상 분석

- 분석 당시 `recipe_snapshot.oilrecipe`을 기반으로 새 Workbench 문서 구성
- 기존 결과 bundle과 공식 결과는 변경하지 않음
- 새 영상 선택 후 해상도와 geometry 확인
- session 시간과 output 경로는 새 시험 값으로 설정
- 사용자 확인 없이 현재 Workbench의 수정 중 recipe를 덮어쓰지 않음

## 9. Phase 2C — Debug Viewer와 재검출

### 9.1 Debug Viewer

일반 Viewer와 timeline 기반은 공유하되 mode를 분리한다.

표시 항목:

- 전체 유면 후보선
- 후보별 총점과 순위
- edge, coverage, region, temporal과 state 점수
- glare, border, exclusion, static과 jump penalty
- smoothing 전후 위치
- 이전 frame 선택 위치
- detector state transition
- edge map, mask, gradient와 ROI crop
- 후보 탈락 사유

### 9.2 Debug trace 수준

향후 분석 session에 다음 수준을 제공한다.

#### `none`

- 최종 tracking sample과 event만 저장
- 현재 Phase 2B 구현의 상태

#### `basic` — 향후 기본값

- event, 낮은 신뢰도, 위치 급변과 검토 필요 frame만 trace 저장

#### `full`

- 모든 분석 frame의 후보와 score breakdown 저장
- detector 개발과 회귀 검증용
- 결과 용량 증가 경고

### 9.3 부분 재검출과 설정 비교

문제 frame에서 detector 설정을 임시 조정하고 다음 범위를 다시 검출한다.

- 현재 frame
- 앞뒤 짧은 구간
- 전체 분석 구간

비교 항목:

- 유면 위치
- confidence
- 선택 후보
- fill state
- event 변화

시험 설정은 원본 recipe에 자동 저장하지 않는다.

- 변경 폐기
- 현재 관찰창에 적용
- 모든 관찰창에 적용
- 새 profile로 저장

### 9.4 사용자 정답과 regression 자료

사용자가 잘못 검출된 frame에서 실제 유면 위치와 오류 유형을 지정한다.

오류 유형 예시:

- 유면 미검출
- 잘못된 후보 선택
- 거품 오인
- 반사광 오인
- 구조물 경계 오인
- ROI 설정 문제
- 상태 분류 오류

공식 분석 결과와 사용자 수정값은 명확히 분리한다.

### 9.5 디버그 재현 패키지

```text
debug_case_YYYYMMDD_HHMMSS/
├─ frame.png
├─ context_before.png
├─ context_after.png
├─ roi_crop.png
├─ candidate_overlay.png
├─ edge_map.png
├─ detection_debug.json
├─ recipe_snapshot.oilrecipe
└─ short_clip.mp4
```

### 9.6 공유용 결과 영상

- overlay annotated MP4 export
- 일반 사용자 공유용 preset
- 디버그 정보 포함 여부 선택

## 10. 아키텍처 방향

### Domain / Application

- `ReviewBundle`, tracking sample, event와 interval model
- 시간 query service
- overlay presentation data
- 향후 debug trace model

### Infrastructure

- 결과 bundle reader
- CSV와 JSON index reader
- 원본 영상 path resolver
- read-only frame reader
- overlay renderer
- 향후 debug JSONL reader와 short-clip exporter

### Presentation

- Result Review window
- playback controller
- read-only canvas
- timeline과 event navigator
- current-frame detail panel
- Phase 2B-2 tracking graph
- Phase 2C debug overlay renderer

분석 pipeline이 Qt widget, 색상 또는 화면 배치 정보를 직접 생성하지 않도록 한다.

## 11. Phase 2B-1 완료 조건

다음 자동화 조건은 PR #9에서 충족했다.

- 기존 분석 bundle을 열 수 있다.
- 신규 bundle에 `review_index.json`을 생성한다.
- 원본 영상을 찾지 못하면 사용자가 대체 파일을 지정할 수 있다.
- 영상 재생 위치와 tracking overlay가 시간 기준으로 동기화된다.
- 선택 관찰창의 ROI, 기준점, 유면 위치와 confidence가 표시된다.
- event와 낮은 신뢰도 항목을 클릭하면 해당 시점으로 이동한다.
- 일반 모드에는 최종 결과만 표시된다.
- overlay 포함 현재 장면을 원본 해상도 PNG로 저장할 수 있다.
- 잘못되거나 불완전한 bundle은 원인을 포함한 오류 메시지를 제공한다.
- 기존 결과 파일과 `report.html` 생성을 유지한다.
- unit, integration과 offscreen GUI regression test가 통과한다.

남은 수동 확인:

- Windows DPI scaling과 문구 잘림
- 실제 분석 결과 bundle
- 장시간 또는 variable/keyframe-dependent 영상 seek
- 원본 영상 이동 후 재지정
- 잘못된 대체 영상 선택 후 기존 Viewer 상태 유지
- 관찰창 1~3개 전환
- 실제 oil/foam overlay 좌표
- Unicode 경로 PNG 저장
- Viewer 종료와 영상 교체 후 file lock 해제

## 12. 비범위

Phase 2B-1에서는 다음을 구현하지 않는다.

- tracking graph
- 그래프 클릭 seek
- 분석 완료 화면과 Viewer 연결
- 같은 profile로 새 영상 분석
- 여러 관찰창 동시 overlay
- detector 후보와 score
- debug trace 생성·읽기
- detector 재실행
- 부분 재검출
- 사용자 정답 라벨링
- annotated MP4 export
- 공식 판정 결과 수정
- 원본 recipe 자동 덮어쓰기
- 다중 사용자 협업 검토
- 외부 서버 업로드 또는 cloud review

## 13. 결정 기록

- 결과 검토와 detector 디버그를 별도 앱으로 나누지 않고 하나의 Viewer에서 mode로 분리한다.
- 일반 Viewer 기반은 Phase 2B, detector 내부 정보는 Phase 2C에서 구현한다.
- MVP는 원본 영상 위 실시간 overlay를 우선하며 annotated MP4는 후속으로 둔다.
- Viewer는 결과 bundle snapshot을 사용하고 Workbench 현재 편집 상태에 의존하지 않는다.
- 신규 `review_index.json`은 기존 bundle과 backward-compatible하게 추가한다.
- MVP에서 event와 low-confidence index는 CSV에서 계산하며 중복 저장하지 않는다.
- debug trace가 구현되기 전 신규 bundle의 `debug_trace_level`은 `none`이다.
- Phase 2C에서 debug trace를 구현할 때 실제 배포 기본 수준은 `basic`으로 전환하는 것을 목표로 한다.
