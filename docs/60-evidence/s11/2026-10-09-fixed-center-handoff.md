# S11 fixed-center checkpoint / handoff — 2026-10-09

사용자가 요청한 세션 인수인계 스냅샷이다. 현재 상태와 실행 순서는
[Work Plan](../../00-project/work-plan.md)이 계속 소유한다. 이후 변경과 충돌하면
현재 owner를 따른다. 이 체크포인트에서 새 검출 실험이나 Windows 작업은 시작하지 않았다.

## 기준과 확인 결과

- 저장소: `/Users/sunjaekim/Developer/oil_level_tracker`, 브랜치 `main`.
- 작업 기준 HEAD: `40e870de52aee11e58413666fcc3b2e74f3b1760`.
  handoff 작성 시작 시 로컬 HEAD와 `origin/main`이 같고 작업 트리는 깨끗했다.
  이 문서를 추가하는 커밋은 별도 문서 체크포인트이며 위 검증 기준을 대체하지 않는다.
- `git worktree list --porcelain`: 현재 저장소 하나만 등록되어 있다.
  과거 보존 디렉터리의 삭제 또는 새로운 워크트리 생성은 하지 않았다.
- 최신 [기계 기록](../../50-diagnostics/s11/2026-10-09-fixed-center-readout.json)에
  고정된 입력·production source·로컬 출력 **413개 경로의 SHA-256을 재확인**, 불일치 0.
  여기에는 production Python 221개가 포함된다. 검출기를 재실행한 결과가 아니다.
- handoff 변경의 governance, 문서 링크/앵커 및 `git diff --check` 통과.
  `src/`와 `tests/`의 변경은 없다.
- 상태 스냅샷: S11 ACTIVE, O1 로컬 수용, O2 OPEN / FIELD FAIL.
  Local XY는 CLOSED WITHOUT PROMOTION이며 OFF. 실제 경계 판별과 통합은 미완료다.

## 확정한 결정과 완료 범위

사용자는 “일관성이랑 구현의 편이성이 좋은 방향으로하자 어렵게 갈 필요 없음”이라고
요청했다. 이에 기존 권장안인 **고정 Glass 중앙 X에서 현재 경계의 Y를 읽는 기준**을
선택했다. 높이 Y를 시간에 대해 고정하는 뜻이 아니다.

- 기존 `GlassGeometry.ellipse.center_x`와 px/mm 변환을 재사용한다. 새 설정은 없다.
- 경계 인식에는 주변 영상과 시간 문맥을 쓸 수 있다. 측정 위치만 고정한다.
- Oil/Foam은 독립적으로 판별·측정한다. 중앙에서 해당 경계가 없거나 모호하면
  그 역할만 UNKNOWN; 다른 X의 중앙값, 보간 또는 이전 높이로 대체하지 않는다.
- 이는 다음 오프라인 후보의 측정 목표다. 현재 runtime, W3 원래 candidate Y,
  Recipe/UI 및 보고서 동작은 변경하지 않았다.

| 보존된 결과 | 근거 및 재개 시 해석 |
|---|---|
| 고정 중앙 좌표 추출 | [readout](../../50-diagnostics/s11/2026-10-09-fixed-center-readout.md): 저장된 176개 raster / 792개 교차면을 독립 픽셀-이웃 열거와 대조, 5개 구성된 좌표·누락 제어 통과. 실제 경계 정확도 또는 성공적 abstention 검증이 아님 |
| 현재 support의 전체 둘레 | [current boundary](../../50-diagnostics/s11/2026-10-09-reference-current-boundary.md): 167개 raster ON/OFF 동일, 73,444개 면 검증. 유리·텍스처가 섞이고 일부 실제 경계가 빠짐 |
| 선택적 양성 참조 | [feasibility](../../50-diagnostics/s11/2026-10-09-material-reference-feasibility.md): 고정 패턴 매칭은 잘못된 특징으로 이동하여 CLOSED WITHOUT PROMOTION. LK는 일부 대응을 유지하지만 물리적 경계 선택 권한이 없음 |

문서·governance 검사는 직전 커밋에서 통과했다. 기존 31개 참조/LK 관련 집중 테스트와
34개 support geometry 테스트는 각 근거 문서의 당시 실행 결과이며 이번 handoff에서
다시 돌리지 않았다. 입력/소스가 바뀌지 않은 검증을 재개라는 이유만으로 반복하지 않는다.

## 다음 세션의 시작점

1. `git status`, 현재 HEAD, Work Plan 상단을 확인하고
   [S11 skill](../../../.agents/skills/s11-detector-change/SKILL.md)의 제한된 recall을 따른다.
   직전 기록의 pending 문구보다 현재 Work Plan이 우선한다.
2. [중앙 측정 계약](../../20-architecture/s11-interface-observability-witness-architecture.md#fixed-center-height-target--selected-for-the-offline-challenger)과
   [W1 검증 계약](../../30-validation/s11-interface-observability-witness-validation.md#w1-aggregation-challenger-controls--not-yet-acceptance-evidence)을 읽는다.
   중앙/가시구간 평균 중 무엇을 쓸지 다시 질문하지 않는다.
3. 남은 구현 문제는 **현재 영상의 실제 경계를 유리·텍스처와 구별하고 선택하는 것**이다.
   구체적인 다음 판별 기법은 아직 확정되지 않았다. 기존 선택적 참조와 양성/음성/모호한
   대조 자료를 재사용하여, 이전 실패와 차이가 있는 작고 검증 가능한 규칙 하나를 먼저
   명시한다. 추가 관측 근거, 선택/UNKNOWN 조건과 고정 비교 범위를 작성한 뒤 구현한다.
   중앙값 읽기 자체를 새로운 판별기나 성능 개선으로 취급하지 않는다.
4. 구현 탐색은 기존 owner부터: `src/oil_tracker/domain/geometry.py`,
   `tests/diagnostics/s11_foam_support_geometry.py`,
   `tests/diagnostics/s11_boundary_temporal_probe.py`.
   support label, 위/아래 면, 최근접 점, LK 생존만으로 실제 경계를 승인하지 않는다.
   단순한 배열 조회/변환을 위해 별도 framework나 새 UI를 만들 필요는 없다.
5. 다음 실제 변경에 맞는 집중 검증과 governance를 수행한다. 모호한 **새 물리적 판단**이
   결론을 바꾸는 경우에만 원본과 최소 표시를 보여주고 질문한다. Windows 실행이 실제로
   필요해지면 그 지점에서 중단하고 전달 절차를 준비한다. 현재 대기 중인 질문은 없다.

사용자는 관련 작업의 커밋·푸시를 자율적으로 허용했다. 머신러닝은 제외하고,
추가 sub-agent 사용 금지와 단순한 구현 선호를 유지한다. private Windows 영상/PNG/ZIP
반출을 요청하지 않는다. 기존 Mac 영상은 재사용할 수 있으나 노출된 regression 자료다.

## 다시 열지 않을 판단과 실험

- D1 저장 기록 조회와 D2 Windows 기존 자료/부분 support 검토는 종료되었다.
  새 설계의 구체적 필요 없이 재실행·재라벨링·반출을 요청하지 않는다.
- [45 s Oil 답변](../../50-diagnostics/s11/2026-10-09-material-reference-late-oil-reply.json):
  오른쪽 LK 그룹은 Foam–Oil 경계에 남아 있는 것으로 보인다는 **부분적·정성적 대응**이다.
  전체 추적 실패나 exact point whitelist로 바꾸지 않는다.
- [참조 경로](../../00-project/recall-index.md)의 기존 sample4 Foam 상단/내부 텍스처,
  고정 유리 테두리·원형 무늬, water 경사 수면 판단은 그대로 유지한다.
  beer의 두 윤곽은 같은 얇은 거품층 앞/뒤이고, milk의 아래 거품–우유 경계는 구분하기 어렵다.
  이를 새 scalar truth나 조밀한 픽셀 판정으로 확장하지 않는다.
- 고정 패턴 실패, raw support의 혼합/누락, Local XY 실패를 threshold/window 조정,
  보간, 값 유지, 수작업 생존점 선택으로 구제하지 않는다. 실패 이유는 해당 기록에 남아 있다.

## 로컬 자료와 새 clone의 차이

아래 디렉터리는 모두 작성 시 존재를 확인했다. 저장소의 `sample/output/` 아래이며
Git에 포함되지 않는 Mac 로컬 자료다. 현재 checkout에서 이어갈 때 삭제/정리하지 않는다.

- `s11-fixed-center-20261009-001/` — 마지막 preflight, `run.py`, readout, 원본 중앙 열과 도표.
- `s11-reference-current-perimeters-20261009-001/` — 167개 현재 support 원본 배열.
- `s11-material-reference-20261009-001/`, `s11-material-reference-verification-20261009-001/`
  — 고정 패턴 실행과 독립 검증.
- `s11-semantic-seed-tracks-20261009-001/`, `s11-seed-observed-edges-20261009-001/`
  — 연속 LK와 현재 edge 대조.
- `s11-support-faces-20261009-001/` — public native/reduced 대조 입력.
- `s11-reference-height-target-20261009-001/` — 측정 위치 선택을 설명한 합성 예시.

Git에는 계약, MD/JSON 기록, 고정 입력/출력 hash, 보존 runner 소스와 선택된 그림이 있다.
새 clone에는 전체 media/NPZ/capture가 자동으로 내려오지 않는다. 없는 자료를 있다고
가정하거나 hash 확인만으로 재현 완료라고 주장하지 않는다. `/tmp`의 임시 runner 대신
로컬 보존 `run.py`와 추적 중인 기계 기록을 사용한다.

## 재개용 메시지

```text
/Users/sunjaekim/Developer/oil_level_tracker에서 이어서 진행해줘.
AGENTS.md와 docs/60-evidence/s11/2026-10-09-fixed-center-handoff.md,
현재 docs/00-project/work-plan.md를 확인하고 다음 작업을 진행해줘.
고정 중앙 측정 기준은 확정됐고 실제 경계 판별 규칙은 아직 미완성이야.
일관성과 구현의 단순함을 우선하고 기존 판정·종료된 실험은 다시 열지 마.
관련 커밋·푸시는 자율적으로 해도 되고, 내 새 판단이나 Windows 작업이
실제로 필요한 지점에서만 멈추고 알려줘. 머신러닝과 추가 sub-agent는 제외해줘.
```

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F07`, `S11-F09`
- First harmful stage: current appearance support can mix or miss the physical boundary before role selection; the exact role-specific first loss remains unresolved. This handoff adds no new causal conclusion.
- Logic-map impact: NONE — checkpoint and navigation only; no executing source or detector owner changes.
- Failure-registry impact: NONE — links preserve already recorded failures and closed judgments; no new experiment or mechanism claim.
