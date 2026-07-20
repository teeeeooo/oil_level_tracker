# Result Review Viewer Plan

## 1. 문서 목적

이 문서는 Rotary Oil Level Tracker의 분석 결과를 원본 영상과 함께 재생하고, 검출 결과를 overlay로 확인하는 `Result Review Viewer`의 사용자 경험, 데이터 계약, 구현 범위와 단계별 확장 계획을 정의한다.

전체 UX 우선순위와 Phase 순서는 [`UX_IMPROVEMENT_BACKLOG.md`](./UX_IMPROVEMENT_BACKLOG.md)를 따른다. 이 문서는 그중 **Phase 2B 이후 Result Review Viewer 관련 기능의 상세 설계 문서**다.

## 2. 목표

Result Review Viewer는 하나의 기반 위에서 두 목적을 지원한다.

1. **일반 사용자 결과 검토**
   - 분석 결과가 실제 영상과 일치하는지 직관적으로 확인
   - 이벤트와 낮은 신뢰도 구간을 빠르게 탐색
   - HTML 보고서만으로 이해하기 어려운 판정 근거를 영상으로 확인

2. **개발자 디버그 및 detector 개선**
   - 후보선, 점수, penalty와 상태 전이 근거 확인
   - 실패 장면을 재현하고 문제 유형을 분류
   - 향후 detector 회귀 테스트와 튜닝 자료로 활용

## 3. 핵심 원칙

- 원본 영상을 다시 인코딩하지 않고, 원본 프레임 위에 결과 데이터를 실시간 overlay한다.
- 일반 검토 모드와 디버그 모드는 같은 viewer와 timeline을 공유한다.
- 일반 모드에서는 최종 결과만 보여주고 내부 detector 정보는 숨긴다.
- 디버그 데이터는 선택적으로 저장하여 기본 분석 성능과 결과 용량을 보호한다.
- 분석 결과는 재현 가능해야 하며, 당시 recipe와 session snapshot을 기준으로 표시한다.
- 원본 영상이 이동되었을 때 사용자가 다시 지정할 수 있어야 한다.
- 기존 `report.html`, CSV, `.oilrecipe` 결과와 호환성을 유지한다.

## 4. 사용자 흐름

### 4.1 분석 완료 직후

분석 완료 대화상자에서 다음 행동을 제공한다.

- 결과 영상 검토
- 결과 보고서 열기
- 결과 폴더 열기
- 같은 프로필로 새 영상 분석
- 닫기

### 4.2 기존 결과 다시 열기

- Workbench에서 `결과 검토 열기` 선택
- 분석 결과 bundle 폴더 또는 `analysis_manifest.json` 선택
- viewer가 bundle 유효성을 점검
- 원본 영상 경로가 유효하면 바로 로드
- 원본 영상이 없으면 분석 당시 경로를 표시하고 파일 재지정 요청

## 5. 화면 구조

```text
┌ 좌측: 관찰창·이벤트 목록 ┬ 중앙: 원본 영상 + overlay ┬ 우측: 현재 시점 정보 ┐
└ 하단: 재생 제어 · timeline · 이벤트/신뢰도 marker · 그래프                ┘
```

### 5.1 좌측 패널

- 관찰창 선택
- 전체/선택 관찰창 필터
- 이벤트 목록
- 낮은 신뢰도 구간 목록
- 검토 필요 항목 목록
- 이전/다음 이벤트 이동

### 5.2 중앙 영상 영역

일반 모드 기본 overlay:

- ROI 타원
- 기준점
- 최종 선택된 oil-air boundary
- 최종 선택된 foam front
- 관찰창 이름
- 현재 상태
- 신뢰도
- 현재 재생 시각

선택적 overlay:

- 검출 제외 영역
- 이벤트 이름
- low-confidence 강조
- 여러 관찰창 동시 표시

### 5.3 우측 정보 패널

현재 시점 기준:

- 영상 timestamp와 frame index
- 선택 관찰창
- fill state
- 유면 위치와 기준점 대비 높이
- foam front 위치
- 최종 confidence
- 활성 event
- 검토 필요 사유

### 5.4 하단 timeline

- 재생/일시정지
- 이전/다음 frame
- 재생 속도
- seek
- 분석 시작·종료 marker
- 압축기 기동 marker
- 이벤트 marker
- low-confidence 구간
- 현재 시점 cursor

## 6. 일반 검토 모드

일반 검토 모드는 시험 담당자가 결과를 빠르게 이해하는 데 집중한다.

### MVP 기능

- 결과 bundle 열기
- 원본 영상 재생
- 관찰창 선택
- tracking data 기반 overlay 재생
- 이벤트 목록 클릭 시 해당 시점으로 이동
- 낮은 신뢰도 구간으로 이동
- 현재 시점 상세 정보 표시
- 현재 overlay 장면 이미지 저장
- 결과 보고서와 결과 폴더 열기

### 일반 모드에서 숨길 항목

- 전체 후보선
- 후보별 score breakdown
- edge map, mask와 gradient 이미지
- detector 내부 penalty
- temporal state 내부값

## 7. 디버그 모드

디버그 모드는 개발자 또는 고급 사용자가 검출 실패 원인을 분석할 때 사용한다.

### 표시 항목

- 전체 유면 후보선
- 후보별 총점과 순위
- edge, coverage, region, temporal, state 점수
- glare, border, exclusion, static, jump penalty
- smoothing 전후 위치
- 이전 frame 선택 위치
- detector state transition
- edge map, mask, gradient와 ROI crop
- 후보 탈락 사유

### 문제 장면 자동 분류

다음 조건을 만족하면 디버그 검토 목록에 등록한다.

- 최종 confidence가 기준 이하
- 후보가 없음
- 이전 frame 대비 위치 급변
- 후보 1위와 2위 점수 차이가 작음
- 짧은 구간에 상태가 반복 전환
- glare 또는 foam penalty가 높음
- 사용자가 수동으로 오류 표시

## 8. 디버그 저장 수준

분석 session에 다음 세 가지 저장 수준을 제공한다.

### `none`

- 최종 tracking sample과 event만 저장
- 저장 용량 최소

### `basic` — 기본값

- 이벤트, 낮은 신뢰도, 위치 급변과 검토 필요 frame만 debug trace 저장
- 실제 배포 환경의 기본 설정

### `full`

- 모든 분석 frame의 후보와 score breakdown 저장
- detector 개발과 회귀 검증용
- 결과 용량 증가 경고 표시

## 9. 결과 bundle 데이터 계약

기존 bundle은 유지하고 viewer용 index와 선택적 debug trace를 추가한다.

```text
analysis_result/
├─ report.html
├─ tracking_data.csv
├─ events.csv
├─ recipe_snapshot.oilrecipe
├─ session.json
├─ analysis_manifest.json
├─ review_index.json
├─ debug_trace.jsonl          # basic/full에서 선택적
├─ captures/
└─ debug/
```

### 9.1 `review_index.json`

viewer가 결과를 빠르게 여는 데 필요한 index다.

필수 정보:

- schema version
- 원본 영상 분석 당시 경로
- 영상 식별 정보와 가능한 경우 file hash
- 분석 시작·종료 시각
- 압축기 기동 시각
- 관찰창 ID와 이름
- tracking/event 파일 위치
- 이벤트 timestamp index
- low-confidence 구간
- debug trace 수준과 파일 위치

### 9.2 `tracking_data.csv`

viewer overlay에 필요한 최소 필드를 보장한다.

- timestamp
- frame index
- glass ID
- fill state
- selected oil boundary Y
- selected foam front Y
- confidence
- zero line Y 또는 snapshot에서 복원 가능한 정보
- valid/unknown 여부

### 9.3 `debug_trace.jsonl`

frame과 관찰창 단위의 선택적 진단 record다.

- timestamp와 frame index
- glass ID
- 후보 목록
- 후보별 score breakdown
- 최종 선택 후보
- penalty
- smoothing 전후 값
- previous temporal state
- debug artifact 상대 경로
- 자동 검토 사유

## 10. 아키텍처 방향

### Domain / Application

- 분석 결과와 debug trace의 데이터 모델 정의
- viewer가 사용할 query service 정의
- overlay rendering에 필요한 중립적인 presentation model 생성

### Infrastructure

- 결과 bundle reader
- CSV/JSONL index reader
- 원본 영상 path resolver
- frame reader와 optional short-clip exporter

### Presentation

- Result Review window
- timeline과 event navigator
- 일반 overlay renderer
- debug overlay renderer
- current-frame detail panel

분석 pipeline이 Qt widget이나 색상 등 UI 정보를 직접 생성하지 않도록 한다.

## 11. 부분 재검출 및 설정 비교 — 후속 확장

문제 frame에서 detector 설정을 임시 조정하고 다음 범위를 다시 검출한다.

- 현재 frame
- 앞뒤 짧은 구간
- 전체 분석 구간

기존 결과와 시험 설정 결과를 비교한다.

- 유면 위치
- confidence
- 선택 후보
- fill state
- event 변화

시험 설정은 자동으로 원본 recipe에 저장하지 않는다.

- 변경 폐기
- 현재 관찰창에 적용
- 모든 관찰창에 적용
- 새 프로필로 저장

## 12. 사용자 수동 정답과 디버그 패키지 — 후속 확장

### 수동 정답 표시

사용자가 잘못 검출된 frame에서 실제 유면 위치와 오류 유형을 지정할 수 있다.

오류 유형 예시:

- 유면 미검출
- 잘못된 후보 선택
- 거품 오인
- 반사광 오인
- 구조물 경계 오인
- ROI 설정 문제
- 상태 분류 오류

이 기록은 일반 분석 결과와 명확히 분리하고, 향후 benchmark와 regression fixture로 활용한다.

### 디버그 재현 패키지

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

## 13. 구현 단계

### Phase 2B-1 — Result Review Viewer MVP

- 결과 bundle reader
- 원본 영상 path 복원과 재지정
- tracking overlay 재생
- 관찰창 선택
- event/low-confidence 탐색
- 현재 시점 상세 정보
- overlay frame 저장

### Phase 2B-2 — 일반 검토 강화

- 그래프와 영상 timeline 동기화
- 검토 필요 항목 필터
- 결과 완료 화면과 연동
- 같은 프로필로 새 영상 분석

### Phase 2C-1 — Debug Viewer

- 일반/디버그 모드 전환
- 후보선과 score breakdown
- debug artifact 표시
- 실패 장면 자동 분류
- 디버그 재현 패키지 내보내기

### Phase 2C-2 — 재검출과 학습 자료화

- 현재 frame/짧은 구간 재검출
- 설정 변경 전후 비교
- 사용자 수동 정답 입력
- 회귀 검증 fixture export

### Phase 2C-3 — 공유용 결과 영상

- overlay가 합성된 annotated MP4 export
- 일반 사용자 공유용 preset
- 디버그 정보 포함 여부 선택

## 14. MVP 완료 조건

- 기존 분석 bundle을 열 수 있다.
- 원본 영상을 찾지 못하면 사용자가 대체 파일을 지정할 수 있다.
- 영상 재생 위치와 tracking overlay가 시간 기준으로 동기화된다.
- 선택한 관찰창의 ROI, 기준점, 유면 위치와 confidence가 표시된다.
- 이벤트와 낮은 신뢰도 항목을 클릭하면 해당 시점으로 이동한다.
- 일반 모드에는 최종 결과만 표시된다.
- overlay 포함 현재 장면을 이미지로 저장할 수 있다.
- 잘못되거나 불완전한 bundle은 원인을 포함한 오류 메시지를 제공한다.
- 기존 결과 파일 형식과 `report.html` 생성은 유지된다.
- unit, integration, offscreen GUI regression test가 통과한다.

## 15. 비범위

초기 MVP에서는 다음을 구현하지 않는다.

- 분석 중 실시간 annotated video 생성
- 전체 영상의 debug trace 강제 저장
- 원본 recipe 자동 덮어쓰기
- 사용자 수정값을 공식 판정 결과로 자동 대체
- 다중 사용자의 협업 검토
- 외부 서버 업로드 또는 cloud review

## 16. 결정 기록

- 결과 검토와 detector 디버그를 별도 앱으로 나누지 않고 하나의 viewer에서 mode로 분리한다.
- MVP는 원본 영상 위 실시간 overlay를 우선하며 annotated MP4 export는 후속으로 둔다.
- 기본 debug trace 수준은 `basic`으로 한다.
- viewer는 결과 bundle을 입력으로 사용하며 Workbench의 현재 편집 상태에 의존하지 않는다.
