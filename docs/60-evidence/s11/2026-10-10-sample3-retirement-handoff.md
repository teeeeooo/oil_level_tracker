# S11 sample3 실행 제한 체크포인트 / 인수인계 — 2026-10-10

사용자가 요청한 실행 제한 구현과 인수인계 스냅샷이다. 현재 상태와 다음 순서는
[Work Plan](../../00-project/work-plan.md)이 소유한다. 이번 체크포인트에서 새 검출
기법, sample3 추가 분석, 클립 추출 또는 Windows 검증을 시작하지 않았다.

## 기준과 완료 범위

- 저장소: `/Users/sunjaekim/Developer/oil_level_tracker`, 브랜치 `main`.
- 시작 기준: `71500cc5e923591aca277d729a988367b57224df`; 시작 시 원격 main과 같고 깨끗했다.
- 구현 체크포인트: **`45da3513b6ebc30b6ac38a6ad12456ba78c4fb3f`**.
  이 문서와 재개 링크를 추가하는 후속 커밋은 문서 체크포인트다.
- `src/`, 네 Recipe, 네 `.oiltruth`, 기존 판정 및 원본 미디어는 변경하지 않았다.
  영상의 물리적 이동·삭제 대신 기존 경로에서 **논리적으로 격리**했다.
- 상태: S11 ACTIVE, R22 behavior / R22-3·O1 diagnostics, O1 로컬 수용,
  O2 OPEN / FIELD FAIL, Local XY OFF. 이번 검증은 검출 정확도 개선이나 field PASS가 아니다.
- 현재 등록된 worktree는 위 저장소 하나다. 사용자 판단이나 Windows 작업을 기다리는
  새 질문은 없다. 이번 종료 지점은 사용자가 요청한 인수인계 체크포인트다.

## 재발 방지 장치

[`s11_corpus_access.py`](../../../tests/diagnostics/s11_corpus_access.py)는 기존 corpus
입력, replay provenance/session, 전체 replay의 부모·worker 진입점에서 재사용한다.
기존 hash 검증과 별도로 사용 목적을 판별하는 작은 공통 모듈이며, 검출기 분기나 새
평가 시스템이 아니다. R7–R13의 독립 orchestrator도 같은 guard를 호출한다.

| 경로 | 확인한 동작 |
|---|---|
| 기본 전체 replay / sample3 직접 session | 분석·worker 시작 전에 `QUARANTINED` 오류; sample3만 조용히 빼고 실행하지 않음 |
| corpus 의존 pytest | 완전한 입력이 있어도 목적 미지정이면 사유를 표시하며 SKIPPED; 전체 회귀 PASS로 취급하지 않음 |
| `legacy-regression` | 기존 회귀 재현을 명시적으로 실행; 네 영상 범위와 13개 legacy 항목 유지 |
| `engineering-replay` | 필요한 기존 decode/provenance/output/동일 동작 확인용; 새로운 sample3 튜닝 권한 아님 |
| 입력 hash 불일치 / 허용된 입력 decode 실패 | 기존 hard failure 유지; skip으로 숨기지 않음 |
| runtime / replay manifest | 목적과 `physical_acceptance=NOT_EVALUATED` 기록; 기존 runtime/tracking fingerprint와 분리 |

명령과 제한은 [sample README](../../../sample/README.md#sample3-use-restriction),
계약은 [architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#retired-local-source-admission)와
[validation](../../30-validation/s11-interface-observability-witness-validation.md#retired-source-execution-checks)에 있다.
사용 목적은 실행할 명령에만 부여한다. 셸 프로필, CI 전역 또는 전체 테스트 fixture에
환경변수를 설정해 항상 허용 상태로 만들지 않는다.

이 장치는 개발 도구의 기본 경로를 제한한다. OS 파일 접근 통제는 아니며 일반 제품
CLI/UI는 임의 영상을 열 수 있다. 새 임시 스크립트로 raw OpenCV를 직접 호출하거나
파일 이름을 바꿔 우회하지 않는다. 새 source reader는 기존 guard를 재사용한다.
독립된 새 근거 없이 sample3 사용 목적을 연구·튜닝으로 확대하지 않는다.

## 검증 근거

구현 체크포인트와 동일한 소스에서 다음 집중 검사를 수행했다.

```bash
.venv/bin/python -m pytest -q \
  tests/test_s11_corpus_access.py \
  tests/test_s11_local_corpus_portability.py \
  tests/test_s11_replay_provenance.py
```

- **37 passed / 15.02 s**. 목적 누락·오류, 두 허용 목적, 12개 전체 replay 진입점의
  조기 차단, 직접 session 및 실제 CLI, hash/decode 실패, 13개 원래 case 보존,
  원래 runtime fingerprint 보존을 확인했다. 실제 subprocess는 repository 밖 cwd에서
  한글·공백 인자, child의 exit code, 목적 상속과 부모 환경 불변을 검사했다.
- 실제 `tests/test_s11_sequence_observability_integrity.py` 기본 실행은
  **1 skipped / 0.27 s**, 이유는 `QUARANTINED`. 영상 분석을 수행하거나 PASS로
  대체한 결과가 아니다.
- 명시적 wrapper로 기존 input preflight와 case loader를 실행해 네 영상의
  **12개 MP4/Recipe/truth hash 일치**, **13개 legacy case 유지**를 확인했다.
  sample3 MP4는 `c2a45b2b3aa025dea405bfecad79228547f80bf8e1a9e337a400cc09f29f3c04`.
- A/B 원래 답변·사용자 표시 이미지, C/D 답변·검토 이미지 **4개 frozen hash 일치**.
- 구현 변경의 governance, 문서 내부 링크/앵커 **342개**, `git diff --check` 통과.
  최종 문서 변경도 같은 governance 및 관련 링크 검사의 대상이다.
- 새 전체 영상 replay, 전체 canonical/Qt suite, Windows 테스트는 수행하지 않았다.
  입력 사용 제한의 검사이며 기존 검출 성능 증거를 대체하지 않는다.

## 닫힌 판단과 실험

- sample3 [A/B reply](../../50-diagnostics/s11/2026-10-10-sample3-gap-source-reply.json):
  75.04/78.04s 표시선 부근이 Oil. exact pixel, 허용 오차, 전체 윤곽 또는 두 시점 사이
  연속 구간의 truth가 아니다.
- sample3 [C/D reply](../../50-diagnostics/s11/2026-10-10-sample3-confirmation-role-reply.json):
  C는 glass 외부 프레임 구조물, D는 초점 때문에 판독 불가. D를 Oil 부재나
  successful abstention으로 바꾸지 않는다. 과거 95/105s unusable도 유지한다.
- [sample3 scope](../../50-diagnostics/s11/2026-10-10-sample3-evaluation-scope.md):
  위치 이동·초점 변화가 있는 전체 고정-Recipe 구간은 주 물리 정확도/연속성 기준이
  아니다. 46.48s numeric gap을 닫기 위한 단계별 재분석이나 usable clip 발굴은 종료한다.
- sample3 recent-direction-only와 sample4 cost-order-only probe는
  CLOSED WITHOUT PROMOTION. H0/G1/CBR-1 및 Local XY도 재개하지 않는다.
  기존 151개 sample3 행과 실패한 variant, 모든 legacy scalar는 그대로 보존한다.
- 고정 Glass 중앙 X에서 물리적으로 식별된 위쪽 image projection을 측정한다는
  선택은 확정됐다. lower fallback, 평균, 다른 X, 보간으로 빈 관측을 채우지 않는다.
  ≤1초 cadence 목표는 별도로 가시적 움직임이 확인된 같은 Oil 계면에만 적용한다.

## 다음 세션의 시작점

1. `git status`, 현재 HEAD와 Work Plan 상단을 확인하고
   [S11 skill](../../../.agents/skills/s11-detector-change/SKILL.md)의 bounded recall을 따른다.
   이 문서는 구현 시점의 기록이고 현재 Work Plan이 우선한다.
2. sample3는 frozen A/B/C/D 자료를 필요할 때 인용하는 것으로 마친다. 전체 replay나
   source review를 재개하는 것이 다음 작업이 아니다. 과거 재현이 실제 필요한 변경에만
   목적 wrapper를 사용하고 기존 결과를 먼저 재사용한다.
3. [water A/B/C 비교](../../50-diagnostics/s11/2026-10-10-abc-source-interval-comparison.md)와
   [sample4 비교](../../50-diagnostics/s11/2026-10-10-sample4-center-interval-comparison.md)에서
   **물리적 경계와 유리 무늬를 구별할 새 관측 근거 하나**를 정한다. 기법은 아직
   선정되지 않았다. 역할별 양성·반대·판정 불가 사례와 비교 범위를 결과 전에 고정한다.
4. water A는 Foam 상단이지만 아래 경계 불명확; B/C는 Foam 층 없는 수면이다.
   승인된 X950 범위는 각각 A rows476–481, B484–489, C489–494다. sample4 f1275는
   X595 rows833–841 범위이고 f1305의 ②는 Oil, ①은 Foam 또는 glass 표면 무늬다.
   이 역할·범위는 닫혔고 이웃 프레임이나 전체 track으로 확장하지 않는다.
   beer/milk의 층·투영·가시성 대조군도 해당 범위대로 유지한다.
5. 기존 측정·후보 생성 owner를 먼저 찾고 이전 실패와 차이가 있는 제한된 변경 하나만
   구현한다. 전체 재설계, ML, threshold/window sweep, 새 촬영 요구는 현재 범위가 아니다.
   새 물리 판단이 결론을 바꾸거나 실제 Windows 실행이 필요한 지점에서만 사용자에게
   알려 멈춘다. 기존 질문을 반복하지 않는다.

## 로컬 자료와 새 clone

원본 일곱 MP4와 `sample/output/`는 계속 Git에서 제외된다. 새 clone에 있다고
가정하지 않는다. 다음 자료는 체크포인트 작성 시 존재를 확인했으며 삭제하지 않는다.

- `sample/output/s11-sample3-reappearance-20261010-001/`: 기존 전체 replay와 native 자료.
- `sample/output/s11-episode-texture-20261008-001/`: 기존 detection/resolution 보존 자료.
- 추적 중인 [sample3 causal archive](../../50-diagnostics/s11/2026-10-10-sample3-reappearance-causality.json.gz):
  10,042,881 bytes, 기존 전체 행·probe·검증 소스. 이 파일의 존재가 새 replay 실행을 뜻하지 않는다.
- 추적 중인 [water 비교 기록](../../50-diagnostics/s11/2026-10-10-abc-source-interval-comparison.json)과
  [sample4 비교 기록](../../50-diagnostics/s11/2026-10-10-sample4-center-interval-comparison.json)은
  각 source/array 경로·hash와 저장된 비교를 연결한다. private Windows 영상/PNG/ZIP 반출은 요구하지 않는다.

## 재개용 메시지

```text
/Users/sunjaekim/Developer/oil_level_tracker에서 이어서 진행해줘.
AGENTS.md, 현재 docs/00-project/work-plan.md와
docs/60-evidence/s11/2026-10-10-sample3-retirement-handoff.md를 확인해줘.
sample3는 기본 실행이 제한됐고 추가 분석·클립 발굴·튜닝은 종료했어.
기존 판정과 실패한 실험을 다시 열지 말고, qualified water B/C와 scoped sample4
근거를 바탕으로 다음 물리적 경계 판별 관측 하나부터 제안·검증해줘.
기존 owner를 재사용하고 구현을 단순하게 유지해. ML과 추가 sub-agent는 제외해줘.
관련 커밋·푸시는 자율적으로 진행하고 내 새 판단이나 Windows 작업이 실제 필요한
지점에서만 멈추고 알려줘. 현재 O2 OPEN / FIELD FAIL은 유지해.
```

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F09`, `S11-F10`
- First harmful stage: unqualified source geometry/visibility was being treated as a whole-window physical oracle before evaluation; the exact earliest detector association error remains unproven. The guard changes offline source admission only.
- Logic-map impact: NONE — no production source, detector control flow, Recipe, truth or publication value changes; purpose metadata is outside numerical fingerprints.
- Failure-registry impact: NONE — existing provenance and case-specific tuning safeguards cover this evaluation restriction; no new mechanism or field improvement is claimed.
