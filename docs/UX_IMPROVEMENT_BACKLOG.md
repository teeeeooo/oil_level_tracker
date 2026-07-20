# Rotary Oil Level Tracker UX Improvement Backlog

## 1. 문서 목적

이 문서는 Rotary Oil Level Tracker의 전체 UX 개선 방향, 구현 순서, Phase별 범위와 완료 상태를 관리하는 계획 문서다.

Result Review Viewer의 화면, 데이터 계약, 일반 검토 모드와 디버그 모드에 대한 상세 설계는 [`RESULT_REVIEW_VIEWER_PLAN.md`](./RESULT_REVIEW_VIEWER_PLAN.md)를 따른다.

## 2. 최종 목표

영상 편집 경험이 없는 일반 사용자가 다음 흐름을 별도 설명 없이 완료할 수 있도록 한다.

1. 시험 영상 선택
2. 분석 시간 설정
3. 유면 관찰창과 기준점 설정
4. 설정 품질 사전 점검
5. 분석 실행
6. 결과 보고서 확인
7. 원본 영상 위 overlay로 분석 결과 검토
8. 필요한 경우 문제 장면을 디버그 자료로 저장

UX 개선은 다음 세 가지 사용자 확신을 단계적으로 높이는 방향으로 진행한다.

- **설정 확신:** 무엇을 입력해야 하고 무엇이 잘못되었는지 알 수 있다.
- **분석 전 확신:** 현재 설정으로 영상 전체를 안정적으로 검출할 수 있는지 확인할 수 있다.
- **분석 후 확신:** 판정 결과가 실제 영상과 일치하는지 직접 검토할 수 있다.

## 3. Phase 현황

| Phase | 주제 | 상태 |
|---|---|---|
| Phase 1 | Workbench 복잡도 축소와 복구 가능한 편집 | 완료 |
| Phase 2A | 설정 완성도와 분석 전 사전 검증 | 완료 |
| Phase 2B | 분석 결과 영상 검토 Viewer | 진행 중 — 2B-1 완료 |
| Phase 2C | 개발용 디버그, 재검출과 공유 확장 | 예정 |
| Phase 2D | 반복 시험 운영과 복구 자동화 | 후보 |

## 4. Phase 1 — Workbench 복잡도 축소와 편집 안정성

### 상태

**완료**

PR #4 `feat: add guided workbench UX phase 1`로 `main`에 반영했다.

### 구현 항목

#### 4.1 기본 설정 / 고급 설정 분리

기본 화면에는 일반 사용자가 자주 사용하는 항목만 표시한다.

- 관찰창 이름
- 분석 포함 여부
- 분석 시작 시 상태
- 판정 방식
- 기준점 안내와 ROI 집중 편집 진입
- 검출 제외 영역

고급 설정에 다음 항목을 배치한다.

- 중심 X/Y와 너비/높이
- mm/pixel
- 테두리 제외 비율
- 검출기 세부 파라미터

#### 4.2 ROI 집중 편집 모드

- 큰 별도 화면에서 타원, 기준점과 제외 영역 편집
- 적용 전 원본 profile 유지
- 적용, 취소와 관찰창 초기화
- 적용 결과를 하나의 undo 작업으로 기록

#### 4.3 하단 고정 실행 영역

- 현재 설정 상태와 오류 개수
- 설정 점검
- 프로필 저장
- 분석 실행

#### 4.4 실행 취소 / 다시 실행

- 타원 이동과 크기 변경
- 기준점 이동
- 제외 영역 추가, 삭제와 이동
- 우측 패널 주요 설정 변경
- `Ctrl+Z`, `Ctrl+Y`

#### 4.5 입력 필드별 즉시 오류 안내

- 오류 입력 빨간 테두리
- 경고 입력 주황 테두리
- 인접한 한글 메시지
- 전체 오류·경고 개수 표시
- 오류가 있으면 분석 실행 비활성화
- 설정 점검 결과 선택 시 해당 입력으로 이동

### 완료 조건

- 기본 모드에서 좌표와 detector 파라미터가 숨겨진다.
- 고급 설정에서 기존 설정을 모두 수정할 수 있다.
- ROI 집중 편집의 취소는 원본을 변경하지 않는다.
- 적용은 하나의 undo 작업으로 기록된다.
- 주요 편집을 undo/redo할 수 있다.
- 하단 실행 영역이 항상 보인다.
- validation 결과가 필드와 하단 상태에 즉시 반영된다.
- 기존 `.oilrecipe` 호환성을 유지한다.
- 전체 offscreen GUI regression test가 통과한다.

## 5. Phase 2A — 설정 완성도와 분석 전 사전 검증

### 상태

**완료**

- Phase 2A-1 `Workbench Readiness Feedback`: 완료
- Phase 2A-2 `Multi-frame Preflight Check`: 완료
- Phase 2A-3 `Observation-window Settings Copy`: 완료

Phase 2A-1은 PR #5 `feat: add workbench readiness feedback`로 `main`에 반영했다.

- PR head: `d915e1fe6aff81057a519436fc34e61406885b8f`
- main merge SHA: `25f3257e3b29682e8fa15cad5a5359373ee0d5a3`
- 검증: Python 3.13 및 3.14에서 각각 `63 passed`

Phase 2A-2는 PR #6 `feat: add multi-frame preflight checks`로 `main`에 반영했다.

- PR head: `bf2bb571adbc8abb7a2e9203fa8332fa2936e404`
- main merge SHA: `44780b9f520b73d87e8701ac6216df04be5ef669`
- 검증: Python 3.13 및 3.14에서 각각 `102 passed`

Phase 2A-3은 PR #7 `feat: add observation-window settings copy`로 `main`에 반영했다.

- PR head: `d501525db0514c2ec78deef12a1d698ef9bc8ae7`
- main merge SHA: `742db20be1a797443410d5b07f563e0dcceb3420`
- 검증: Python 3.13 및 3.14에서 각각 `128 passed`

### 목적

사용자가 분석을 실행하기 전에 모든 관찰창이 제대로 설정되었고, 영상의 여러 시점에서 안정적인 검출이 가능한지 확인할 수 있게 한다.

### Phase 2A-1 — Workbench Readiness Feedback

**완료**

#### 5.1 관찰창별 설정 완료 상태

왼쪽 관찰창 목록에 다음 상태와 가장 중요한 사유를 표시한다.

- 완료
- 확인 필요
- 수정 필요
- 분석 제외

Global session issue는 모든 관찰창의 오류로 전파하지 않고, 해당 관찰창과 연결된 validation issue만 사용한다.

#### 5.2 문제 관찰창 이동과 작업 진행 단계

- 첫 번째 error 관찰창으로 이동
- error가 없으면 첫 번째 warning 관찰창으로 이동
- 관련 입력 필드 focus 및 scroll
- 관찰창 목록, 설정 패널과 canvas 선택 동기화
- 상단 작업 단계 표시
- 영상 선택, 시간 설정, 관찰창 설정, 설정 점검과 분석 실행 단계 클릭 이동

#### 5.3 일반 사용자용 현재 장면 검출 카드

현재 장면의 최종 검출 결과만 간단히 표시한다.

- fill state
- confidence
- 기준점 대비 유면 위치
- mm/pixel 설정 시 mm 환산값
- 검출 상태: 정상 / 확인 필요 / 실패

후보선과 내부 score는 일반 화면에서 숨기고 `ROI 상세보기` 또는 후속 Debug Viewer에서 제공한다.

#### 5.4 Preview 안정성과 분석 실행 조건

- 관찰창, frame과 timestamp 전환 시 stale preview 차단
- 새 preview 요청 중 이전 확정 결과 제거
- 명시적 설정 점검 후에만 `VALIDATED` 상태 진입
- 설정 변경 후 `DRAFT_DIRTY`로 전환하고 재점검 요구
- `.oilrecipe` schema와 detector algorithm 유지

### Phase 2A-2 — Multi-frame Preflight Check

**완료**

분석 구간의 대표 시점을 자동 검사한다.

권장 시점:

- 분석 시작
- 압축기 기동 직후
- 분석 구간 25%, 50%, 75%
- 분석 종료 직전

결과:

- 관찰창·시점별 성공, 경고와 실패
- 관찰창별 최저 confidence
- 후보 없음
- 비정상적인 위치 급변
- 거품 영향 또는 사용자 확인 가능성
- 문제 시점으로 즉시 이동
- 재점검 시 이전 결과와 진행 상태 교체

이번 단계는 전체 분석 결과를 생성하지 않으며, 분석 전 설정 품질 확인을 위한 제한된 sample 검사로 구현한다.

### Phase 2A-3 — Observation-window Settings Copy

**완료**

- 선택한 관찰창을 source로 사용
- 복수 target과 분석 제외 target 지원
- 판정 설정, detector 설정, 테두리 제외 범위와 초기 상태를 기본 복사
- mm/pixel과 타원 크기는 선택적으로 복사
- target의 ID, 이름, 분석 포함 여부, 타원 중심, 기준점과 제외 영역 유지
- mutable 설정은 deep copy하여 source와 target 간 alias 방지
- 타원 크기는 모든 target에 적용 가능한지 먼저 검증하고 원자적으로 적용
- 복수 target 변경 전체를 한 번의 Undo/Redo로 처리
- no-op이면 recipe, Undo stack과 preflight 상태를 변경하지 않음
- 적용 후 readiness, validation, preview와 preflight context 갱신

### Phase 2A 전체 완료 조건

- 모든 관찰창의 준비 상태가 왼쪽 목록에 표시된다.
- 미완료 관찰창과 첫 번째 오류로 바로 이동할 수 있다.
- 현재 장면의 검출 품질을 일반 사용자가 이해할 수 있는 형태로 표시한다.
- 여러 대표 시점의 사전 점검 결과를 분석 실행 전에 확인할 수 있다.
- 실패 시점 선택 시 영상이 해당 위치로 이동한다.
- 선택한 설정을 다른 관찰창에 복사할 수 있다.
- 기존 분석 결과와 recipe schema를 변경하지 않는다.

## 6. Phase 2B — 분석 결과 영상 검토 Viewer

### 상태

**진행 중**

- Phase 2B-1 `Result Review Viewer MVP`: 완료
- Phase 2B-2 `일반 검토 강화`: 다음 작업

Phase 2B-1은 PR #9 `feat: add result review viewer MVP`로 `main`에 반영했다.

- PR head: `2f948a57171586665b20c5f814f1d7d2c2863142`
- main merge SHA: `faeb31a54d1e7d88ebee79a8ee33769fb24dd8c0`
- 검증: Python 3.13 및 3.14에서 각각 `175 passed`
- 실제 Windows DPI, 실영상 seek와 overlay 좌표 검증은 수동 확인 항목으로 유지

### 목적

분석 완료 후 사용자가 원본 영상을 재생하면서 검출된 유면 위치와 판정 근거를 overlay로 확인할 수 있게 한다.

상세 설계와 데이터 계약은 [`RESULT_REVIEW_VIEWER_PLAN.md`](./RESULT_REVIEW_VIEWER_PLAN.md)를 따른다.

### Phase 2B-1 — Viewer MVP

**완료**

- 기존 및 신규 결과 bundle 열기
- `review_index.json` 생성과 index 없는 기존 bundle 복원
- 원본 영상 자동 탐색과 session 한정 재지정
- 관찰창 선택
- ROI, 기준점, 최종 유면 위치와 foam front overlay
- 영상과 tracking timestamp 동기화
- 이벤트와 낮은 신뢰도 구간 탐색
- 현재 시점 상세 정보
- overlay 포함 원본 해상도 PNG 저장
- Workbench와 분리된 read-only Viewer 및 독립 video reader

### Phase 2B-2 — 일반 검토 강화

**다음 작업**

- tracking graph와 영상 동기화
- 그래프 클릭 시 해당 시점 이동
- 검토 필요 항목만 필터
- 결과 보고서와 결과 폴더 연결
- 같은 프로필로 새 영상 분석
- 분석 완료 대화상자에서 Viewer 바로 열기

### 완료 조건

- 분석 결과와 원본 영상을 함께 열 수 있다.
- 최종 검출 위치가 원본 영상 위에 정확한 시점으로 표시된다.
- 이벤트 또는 낮은 신뢰도 항목으로 즉시 이동할 수 있다.
- 원본 영상이 이동된 경우 사용자가 새 경로를 지정할 수 있다.
- 일반 검토 모드에서는 detector 내부 후보와 점수를 노출하지 않는다.
- Viewer가 현재 Workbench 편집 상태가 아니라 결과 bundle snapshot을 사용한다.

## 7. Phase 2C — 개발용 디버그와 결과 확장

### 목적

Result Review Viewer를 detector 문제 재현, 튜닝과 회귀 검증에 활용한다.

### Phase 2C-1 — Debug Viewer

- 일반/디버그 모드 전환
- 전체 후보선 표시
- 후보별 score breakdown
- penalty와 smoothing 전후 위치
- edge map, mask, gradient와 ROI crop
- 실패 장면 자동 분류
- 디버그 재현 패키지 내보내기

### Phase 2C-2 — 부분 재검출과 비교

- 현재 frame 다시 검출
- 앞뒤 짧은 구간 다시 검출
- 설정 변경 전후 결과 비교
- 시험 설정을 현재 관찰창, 모든 관찰창 또는 새 profile에 적용
- 원본 profile 자동 덮어쓰기 금지

### Phase 2C-3 — 사용자 정답과 회귀 자료

- 실제 유면 위치 수동 표시
- 오류 유형 분류
- 공식 분석 결과와 사용자 수정값 분리
- regression fixture export
- detector benchmark 자료로 활용

### Phase 2C-4 — 공유용 결과 영상

- overlay annotated MP4 export
- 일반 검토용 preset
- 디버그 정보 포함 여부 선택

### 완료 조건

- 문제 frame에서 후보와 최종 선택 근거를 확인할 수 있다.
- debug trace 저장 수준을 `none`, `basic`, `full`로 선택할 수 있다.
- 기본 배포 설정은 문제 frame 중심의 `basic`이다.
- 문제 장면을 독립적인 재현 패키지로 저장할 수 있다.
- 임시 detector 설정으로 부분 재검출하고 원본과 비교할 수 있다.

## 8. Phase 2D — 반복 시험 운영과 복구 자동화 후보

Phase 2A~2C 이후 실제 사용 피드백을 바탕으로 우선순위를 다시 판단한다.

후보 기능:

- 자동 저장과 비정상 종료 복구
- 종료 전 저장 확인
- 실행 전 최종 요약 화면
- 분석 진행 중 숫자 중심 상태 요약
- 분석 완료 후 다음 행동 제공
- 결과 폴더와 naming convention 관리
- 최근 profile과 최근 결과 목록
- 동일 profile로 연속 영상 분석
- Wizard 최소화와 Workbench 역할 재정의

## 9. 공통 후속 UX 후보

Phase와 별개로 필요성이 확인되면 포함한다.

- 기준점 drag 확대 안내창
- 방향키 1px, `Shift`+방향키 5px 이동
- 타원 resize 중 크기 tooltip
- 비율 유지와 중심 기준 resize modifier
- ROI zoom, pan, 화면 맞춤
- 입력 필드와 overlay 요소의 양방향 강조
- detector 설정 변경 전후 비교
- 프로필 설정과 이번 시험 session 설정의 시각적 분리
- 상단 toolbar 추가 단순화

## 10. 구현 순서 원칙

1. 기존 Phase가 `main`에 병합되고 검증된 뒤 다음 Phase용 branch를 생성한다.
2. 하나의 PR은 하나의 사용자 목적을 중심으로 구성한다.
3. domain schema 변경이 필요한 경우 UI 구현 전에 데이터 계약을 먼저 확정한다.
4. 일반 사용자 화면과 디버그 화면을 혼합하지 않는다.
5. 자동화가 불확실한 경우 사용자가 검토하고 수정할 수 있는 경로를 제공한다.
6. 전체 pytest, integration과 offscreen GUI regression test를 완료 조건에 포함한다.
7. 실제 Windows DPI와 실영상 검토는 merge 전 수동 확인 항목으로 유지한다.
8. Phase 완료 마킹은 해당 구현 PR이 `main`에 병합된 뒤에만 기록한다.

## 11. 현재 다음 작업

현재 `main`에는 Phase 1, Phase 2A 전체와 Phase 2B-1이 완료되어 있다.

다음 구현 순서는 다음과 같다.

1. **Phase 2B-2:** 일반 검토 강화
2. **Phase 2C:** Debug Viewer와 재검출 확장
3. **Phase 2D:** 반복 시험 운영과 자동 복구 기능 재평가
