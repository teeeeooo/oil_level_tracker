# Result Review Viewer Plan

## 1. 문서 목적

이 문서는 Rotary Oil Level Tracker의 분석 결과를 원본 영상과 함께 재생하고, 검출 결과를 overlay로 확인하는 `Result Review Viewer`의 사용자 경험, 데이터 계약, 구현 범위와 단계별 확장 계획을 정의한다.

전체 UX 계약은 [UX improvement plan](./ux-improvement-plan.md), 품질 및 실영상 gate는 [real-world validation plan](../30-quality/real-world-validation-plan.md)을 따른다. 이 문서는 Phase 2B 이후 Result Review Viewer 관련 상세 설계 문서다.

## 2. 문서 소유권

이 문서는 Result Review의 사용자 흐름, 화면, bundle reader, 시간 동기화, debug/re-detection/truth 계약을 소유한다. 프로젝트 장기 상태는 [roadmap](../00-project/roadmap.md), active gate와 next action은 [work plan](../00-project/work-plan.md)이 소유한다. 과거 PR head와 validation count는 Git history에 보존하며 이 기능 문서에서는 중복 관리하지 않는다.

## 3. 목표

Result Review Viewer는 하나의 기반 위에서 두 목적을 지원한다.

1. **일반 사용자 결과 검토**
   - 분석 결과가 실제 영상과 일치하는지 직관적으로 확인
   - 이벤트와 낮은 신뢰도 구간을 빠르게 탐색
   - HTML 보고서만으로 이해하기 어려운 판정 근거를 영상과 graph로 확인

2. **개발자 디버그 및 detector 개선**
   - 후보선, 점수, penalty와 상태 전이 근거 확인
   - 실패 장면을 재현하고 문제 유형 분류
   - 향후 detector 회귀 테스트와 튜닝 자료로 활용

Phase 2B는 일반 사용자 결과 검토에 집중하고, detector 내부 정보는 Phase 2C에서만 노출한다.

## 4. 핵심 원칙

- 원본 영상을 다시 인코딩하지 않고 원본 frame 위에 저장된 결과를 실시간 overlay한다.
- 일반 Viewer는 저장된 tracking data만 사용하고 detector를 다시 실행하지 않는다.
- Viewer는 Workbench의 현재 recipe와 session이 아니라 결과 bundle의 snapshot을 사용한다.
- 일반 모드에서는 최종 결과만 표시하고 detector 내부 후보와 점수는 숨긴다.
- 원본 영상이 이동되었을 때 사용자가 세션 한정 대체 경로를 지정할 수 있다.
- 대체 영상의 geometry를 자동 scale하거나 이동하지 않는다.
- 기존 `report.html`, CSV와 `.oilrecipe` 형식을 유지한다.
- 신규 index가 없는 기존 결과 bundle도 계속 열 수 있어야 한다.
- Viewer의 video reader, playback state와 lifecycle은 Workbench와 분리한다.
- 결과 bundle 내부 asset은 root 밖으로 탈출하지 않도록 검증한다.
- 새 reader와 Workbench 후보는 준비가 완료된 뒤에만 active state로 교체한다.

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

### 5.2 분석 완료 직후

분석 완료 dialog에서 다음 행동을 제공한다.

- 결과 영상 검토
- 결과 보고서 열기
- 결과 폴더 열기
- 같은 profile로 새 영상 분석
- 닫기

Workbench는 먼저 `ANALYZED` 상태와 결과 bundle 경로를 확정한다. 후속 action 실패는 분석 성공 상태를 변경하지 않는다.

### 5.3 같은 profile로 새 영상 분석

- 결과 bundle의 recipe snapshot을 deep copy한다.
- 새 영상과 첫 frame을 임시 reader에서 준비한다.
- snapshot과 동일한 해상도만 shortcut으로 적용한다.
- 사용자가 현재 Workbench 교체를 확인한 뒤 한 번에 commit한다.
- 실패 또는 취소 시 기존 Workbench 전체 상태를 보존한다.
- 결과 snapshot과 기존 Viewer는 변경하지 않는다.

## 6. 화면 구조

```text
┌ 좌측: 관찰창·이벤트·검토 필터 ┬ 중앙: 원본 영상 + overlay ┬ 우측: 현재 시점 정보 ┐
│                               ├ interactive tracking graph ┤                      │
└ 하단: 재생 제어 · timeline · 이벤트/신뢰도 marker                               ┘
```

### 6.1 좌측 패널

- 관찰창 선택
- 관찰창별 판정 상태
- 이벤트 목록
- 낮은 신뢰도·검토 필요 구간 목록
- 검토 사유 category filter
- 현재 filter 결과 개수
- 이전/다음 항목 이동
- event confidence와 note
- event capture 존재 여부와 열기

한 번에 하나의 관찰창 overlay와 graph를 표시한다.

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

### 6.3 Interactive tracking graph

- 선택 관찰창의 oil-air 추세
- 값이 있을 때 foam-front 추세
- 기준점 Y=0
- 분석 시작·종료와 압축기 기동 marker
- event marker
- 현재 filter를 통과한 검토 interval
- 현재 actual decoded timestamp cursor
- graph 클릭 seek

단위 정책:

- `mm_per_pixel`과 usable mm 값이 있으면 mm
- 그 외에는 px
- smoothed 값 우선
- 같은 단위의 raw 값 fallback
- 값이 없으면 gap
- 누락값을 임의의 0으로 표시하지 않음

Playback 중에는 전체 series를 재생성하지 않고 cursor만 갱신한다.

### 6.4 우측 정보 패널

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

### 6.5 하단 timeline

- 재생과 일시정지
- 이전/다음 frame
- 0.5×, 1×, 1.5×, 2×, 4× 배속
- seek
- 분석 시작·종료 marker
- 압축기 기동 marker
- event marker와 duration
- low-confidence interval
- 현재 timestamp cursor

## 7. Phase 2B 구현 계약

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
- Phase 2B의 event timestamp index와 low-confidence interval은 index에 중복 저장하지 않고 CSV에서 load 시 계산한다.
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
- graph cursor, timeline, overlay와 detail을 actual decoded timestamp로 재동기화

### 7.5 검토 필요 interval과 filter

검토 category:

- `invalid`
- `low_confidence`
- `review_required`
- `foam`
- `glare_or_fog`
- `detection_lost`

다음 조건을 만족하는 sample은 검토 필요 대상으로 분류한다.

- `is_valid == false`
- snapshot의 `minimum_final_confidence` 미만
- `LOW_CONFIDENCE`
- `DETECTION_LOST`
- `FOGGED_OR_GLARE`
- `REVIEW_REQUIRED`
- `UNKNOWN_REVIEW`
- foam, review, glare, fog 또는 lost 관련 명시적 flag

연속 sample은 session sampling FPS 또는 timestamp 간격을 기준으로 interval로 묶는다.

대표 timestamp:

- 최저 confidence sample 우선
- 동률이면 가장 이른 timestamp
- 이후 frame index와 입력 순서로 deterministic 결정

Filter는 Viewer session 상태이며 공식 결과와 bundle을 변경하지 않는다.

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

새 대체 영상은 reader 생성, metadata 검증과 첫 frame decode가 성공한 뒤에만 active reader로 교체한다. 실패하면 기존 reader, frame, timestamp, overlay, details, path와 PNG 상태를 유지한다.

### 7.7 Event navigation과 asset action

- 관찰창별 timestamp 정렬
- point event와 duration event 지원
- event type 한글 label
- confidence와 note 표시
- capture path 존재 여부 표시
- activation 시 재생을 멈추고 event 시작 시각으로 seek
- 선택 event capture 열기
- `report.html` 열기
- 결과 bundle 폴더 열기

Bundle asset resolver는 다음을 거부한다.

- 절대경로
- `..`
- root 밖 resolve
- symlink root escape
- 존재하지 않는 파일
- 잘못된 file/directory type

### 7.8 Overlay PNG 저장

- 축소된 widget screenshot을 사용하지 않는다.
- 원본 frame 해상도로 overlay를 다시 render한다.
- ROI, 기준점, 최종 유면, foam, 상태, confidence와 timestamp를 포함한다.
- `.png` 확장자를 보정한다.
- Unicode 경로를 지원한다.
- 파일명에 사용할 수 없는 문자를 안전하게 치환한다.
- 공식 분석 결과 파일을 자동으로 덮어쓰지 않는다.

### 7.9 분석 완료와 같은 profile workflow

분석 완료 dialog:

- 전체 판정과 관찰창별 판정
- 결과 bundle 경로
- warning/error 개수
- 결과 영상 검토
- 결과 보고서 열기
- 결과 폴더 열기
- 같은 profile로 새 영상 분석

같은 profile workflow:

- recipe snapshot serialization round-trip deep copy
- 동일 해상도 영상만 shortcut 적용
- 새 reader, metadata와 첫 frame을 먼저 준비
- 사용자 교체 확인
- 성공 시 `recipe_path=None`, 새 session과 `DRAFT` state 적용
- session 시간, compressor start, output directory와 run note reset
- sampling FPS를 새 영상 FPS 이하로 clamp
- Undo, preview, preflight와 validation 상태 reset
- 실패·취소 시 기존 Workbench 전체 상태 보존

### 7.10 Lifecycle

- Viewer별 독립 `OpenCvVideoReader`
- bundle load 실패 시 기존 정상 bundle과 reader 유지
- 다른 정상 bundle을 적용할 때 기존 reader close
- Viewer close 시 playback timer와 reader close
- graph Matplotlib callback disconnect와 figure 정리
- generation 값으로 이전 frame update 무효화
- Workbench close 시 Viewer, completion dialog와 pending candidate 정리
- Viewer 조작이 Workbench current frame, selection, recipe, preview와 preflight 상태를 변경하지 않음

## 8. Phase 2B acceptance contract

- 기존 분석 bundle을 열 수 있다.
- 신규 bundle에 `review_index.json`을 생성한다.
- 원본 영상을 찾지 못하면 사용자가 대체 파일을 지정할 수 있다.
- 영상 재생 위치와 tracking overlay가 시간 기준으로 동기화된다.
- 선택 관찰창의 ROI, 기준점, 유면 위치와 confidence가 표시된다.
- event와 낮은 신뢰도 항목을 클릭하면 해당 시점으로 이동한다.
- interactive graph와 영상이 양방향 동기화된다.
- 검토 필요 항목을 machine category로 필터할 수 있다.
- report, 결과 폴더와 event capture를 안전하게 열 수 있다.
- 분석 완료 dialog에서 Viewer와 후속 작업으로 이동할 수 있다.
- 같은 profile로 새 영상을 준비하되 기존 상태를 원자적으로 보호한다.
- 일반 모드에는 최종 결과만 표시된다.
- overlay 포함 현재 장면을 원본 해상도 PNG로 저장할 수 있다.
- 잘못되거나 불완전한 bundle은 원인을 포함한 오류 메시지를 제공한다.
- 기존 결과 파일과 `report.html` 생성을 유지한다.
- unit, integration과 offscreen GUI regression test가 통과한다.

남은 수동 확인:

- Windows DPI scaling과 graph 문구·legend 잘림
- 실제 분석 결과 bundle
- 많은 sample의 장시간 영상 성능
- variable/keyframe-dependent 영상 seek
- playback 중 graph cursor 성능
- px/mm와 foam graph 실제 표시
- Windows에서 report, folder와 capture 열기
- 분석 완료 dialog action
- 같은 profile 새 영상 workflow
- 원본 영상 이동 후 재지정
- 잘못된 대체 영상 선택 후 기존 Viewer 상태 유지
- 관찰창 1~3개 전환
- 실제 oil/foam overlay 좌표
- Unicode 경로 PNG 저장
- Viewer와 Workbench 종료 후 file lock 해제

## 9. Phase 2C — Debug Viewer와 재검출

### 9.1 Debug Viewer

일반 Viewer와 timeline, graph 기반은 공유하되 mode와 데이터 책임을 분리한다.

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

분석 session에 다음 수준을 제공한다.

#### `none`

- 최종 tracking sample과 event만 저장
- Phase 2B 구현의 기본 상태

#### `basic` — 신규 session 기본값

- event, 낮은 신뢰도, 위치 급변과 검토 필요 frame만 trace 저장
- 일반 배포 환경의 기본값

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

구현 결과:

- 외부 `.oiltruth` annotation set
- confirmed/corrected/unusable disposition
- canonical source-frame 유면·거품 좌표
- annotation 수정·삭제·filter와 graph/timeline marker
- 공식/truth pure comparison
- current/selected/all regression fixture export
- official result bundle 불변

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

### 9.6 공유용 결과 영상 — S7 / Phase 2C-4

The accepted S6 real-video/runtime scope is complete, so the roadmap now selects S7 as the exact next implementation gate. Existing Result Review overlay and PNG rendering paths are prerequisites to reuse; annotated-video encoding itself has not started. Windows/manual GUI and PyInstaller one-folder validation is not a prerequisite for starting S7 and remains pending as the final release gate after the product feature sequence.

- approved result overlays rendered onto the source video;
- shareable annotated MP4 export;
- 일반 사용자 공유용 preset;
- 디버그 정보 포함 여부 선택.

Platform/release obligations remain governed by the [real-world validation plan](../30-quality/real-world-validation-plan.md) and milestone status by the [roadmap](../00-project/roadmap.md).

### 9.7 실사용 결과 시각화 안정화

These Phase 2C-4 prerequisites were completed by S4 and must remain preserved during S7:

- Matplotlib 한글 font resolver
- 사용자-facing `oil-air`를 `유면` 또는 `유면 경계`로 변경
- graph y축을 검출값 autoscale이 아니라 Glass 전체 분석 영역으로 고정
- 기준선 0과 분석 영역 위·아래 경계 표시
- Result Review와 HTML report의 동일 graph 범위 정책

## 10. 아키텍처 방향

### Domain / Application

- `ReviewBundle`, tracking sample, event와 interval model
- 시간 query service
- graph presentation model
- overlay presentation data
- debug trace model

### Infrastructure

- 결과 bundle reader
- CSV와 JSON index reader
- 원본 영상 path resolver
- bundle asset resolver
- read-only frame reader
- overlay renderer
- debug JSONL reader와 short-clip exporter

### Presentation

- Result Review window
- playback controller
- read-only canvas
- interactive tracking graph
- timeline과 event navigator
- current-frame detail panel
- debug overlay renderer와 artifact panel

분석 pipeline이 Qt widget, 색상 또는 화면 배치 정보를 직접 생성하지 않도록 한다.

Decoded frame과 debug artifact는 presentation adapter에서 detached `QImage`로 변환한 뒤 UI에 전달한다. Qt presentation은 NumPy/OpenCV를 직접 소유하지 않으며 architecture import guard에 temporary allowlist가 없어야 한다.

## 11. Phase 2C-1 설계 원칙

- 일반 mode는 기존 Phase 2B 동작과 결과만 유지한다.
- debug mode는 trace가 있는 bundle에서만 활성화한다.
- trace가 없는 기존 bundle은 정상적으로 일반 mode로 열린다.
- debug trace는 bundle 내부 상대경로와 schema version을 가진다.
- debug artifact 경로는 bundle root 밖으로 탈출할 수 없다.
- 기본 분석 성능과 결과 용량을 보호하기 위해 저장 수준을 명시한다.
- 후보와 score 표현은 저장 당시 detector 결과를 재현하며 Viewer에서 detector를 다시 실행하지 않는다.
- detector 재실행과 설정 비교는 Phase 2C-2에서 별도 임시 workspace와 비교 workflow로 구현했다.
- 공식 tracking result와 debug trace가 불일치하면 공식 결과를 수정하지 않고 사용자에게 상태를 표시한다.

## 12. Phase 2B 비범위

Phase 2B에서는 다음을 구현하지 않았다.

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
- Phase 2B는 원본 영상 위 실시간 overlay와 interactive graph를 우선하며 annotated MP4는 후속으로 둔다.
- Viewer는 결과 bundle snapshot을 사용하고 Workbench 현재 편집 상태에 의존하지 않는다.
- 신규 `review_index.json`은 기존 bundle과 backward-compatible하게 추가한다.
- event와 low-confidence index는 CSV에서 계산하며 중복 저장하지 않는다.
- 과거 session에 `debug_trace_level`이 없으면 `none`으로 읽어 기존 bundle 호환성을 유지한다.
- 신규 Workbench session의 기본 debug trace 수준은 문제 장면 중심의 `basic`이다.
- 디버그 재현 패키지는 공식 result bundle 내부 또는 symlink alias 하위에 저장할 수 없다.
