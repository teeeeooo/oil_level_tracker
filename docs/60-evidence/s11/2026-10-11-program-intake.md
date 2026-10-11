# S11 프로그램 명세 인수·P1 통합·후속 계획 검토 — 2026-10-11

**범위:** 사용자 제공 ZIP 두 개, P1 작업트리와 001/002/resume 실행 산출물의
보존·검토·로컬 병합·중복 정리. P2의 새 알고리즘 실행은 포함하지 않는다.
**시작 기준:** `main`과 `work/s11-center-alternatives-20261011` 모두
`8fea93f2cfa27c455114d0921bbeacb9f697ad13`; main clean, 후보에 9개 미커밋 변경.
**통합:** 원본 9개 파일을 `e9bef67a09649f01ecfa579468b46c5d1040b214`로 커밋하고
main에 fast-forward 병합했다. 이후 재현 도구의 baseline 확인만 보완했다.
**판정:** P1은 오프라인 표현 보존 도구로 통합 가능하다. 물리 판별·기본 실행
경로에는 채택하지 않았다. S11 ACTIVE / O2 OPEN / FIELD FAIL, Local XY OFF 유지.

## 보존 위치와 원본 검증

| 자료 | 저장소 위치 | 확인 범위 |
|---|---|---|
| 10월 10일 프로그램 명세 | [원본 패키지](../../70-reference/s11-program-review-2026-10-10/README.md), [manifest](../../70-reference/s11-program-review-2026-10-10/import-manifest.json) | 원본 6파일과 별도 로컬 감사 4파일; 제공 체크섬 전부 일치 |
| 10월 11일 구현 마감 명세·패치 | [원본 패키지](../../70-reference/s11-center-path-closeout-2026-10-11/README.md), [manifest](../../70-reference/s11-center-path-closeout-2026-10-11/import-manifest.json) | 원본 15파일; 9개 후보 파일 hash 및 patch 적용 가능성 일치 |
| 사용자 지정 재개 증거 | [CLOSEOUT](../../70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/CLOSEOUT.md), [receipt](../../70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/resume-verification.json), [JUnit](../../70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/pytest.xml), [log](../../70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/pytest.log), [replay](../../70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/) | 전부 바이트 보존; 원시 gzip 23개를 포함 |
| 최초·guard 적용 실행 | 두 번째 manifest의 `native_files` | 001/002/resume의 일반 파일 99개를 모두 목적지와 연결; 같은 hash는 보존본 재사용 |
| 이번 통합 검증 | [기계 기록](2026-10-11-program-intake.json), [새 검증 자료](2026-10-11-program-intake/) | 원본 실행과 구별한 검사·재실행·정리 결과 |

전체 제공 파일과 native JSON/gzip/XML/Python/text를 구조 검사했고,
001/002/resume의 원시 캡처는 각각 23/23 동일했다. 서로 다른 실행의
preflight/readout·시험 XML·resource 측정·스크립트는 고유한 바이트를 보존했다.
원본 감사 receipt는 제공 명세의 `8e6c7869…` digest와 일치한다.
전달 ZIP/TAR/Base64 7개는 내부 파일까지 대조했다. 두 고유한 내부 checksum
파일도 보존했고, 재인코딩된 운반용 컨테이너는 중복으로 분류했다.

제공 원문·원본 패치·기존 machine 기록은 수정하지 않았다. 기존 구현 evidence에는
이동 안내만 추가했고 원문 사본은 패키지 안에 남겼다. 원문에 적힌 과거 절대경로와
“미커밋/main clean”은 당시 기록이다. 현재 위치는 manifest, 현재 상태·권한은
[Work Plan](../../00-project/work-plan.md)이 소유한다. 보존된 복구·포장 스크립트는
역사 자료이며 production/test discovery에 등록하지 않는다.

## 명세 타당성 검토와 채택 범위

| 항목 | 판단 | 현행 계획에 반영한 경계 |
|---|---|---|
| P1 경로 대안 보존 | 타당하며 제한된 구현 완료 | 기존 그래프의 중앙 row별 최적 원시 경로를 보존. median 후검사를 통과하는 최적화나 물리 selector를 구현한 것은 아님 |
| forward DP 선택 | 원래 목적과 부합 | sector 수 → 원래 지역 점수 합, 좌→우 누적·seed/band/jump 유지. 작은 전수 oracle로 확인 |
| P1 결과 의미 | 표현 개선으로만 유효 | B 및 C reduced의 위치 호환 대안이 보존됨. pooled sector row는 고정 X의 실제 contour가 아님 |
| P1 사용 비용 | 명시적 offline 호출에 적합 | 빈 용기도 많은 대안을 남기고 비용이 있음. 상시 production 배선·runtime ID 변경 없음 |
| P2 공동 역할 비교 | 타당한 가설, 구현 준비는 미완성 | 실제 비교 가능한 반대 reference, 공통 support, residual 정규화·변환 자유도·수치 operating point가 먼저 필요 |
| P2 재사용 경로 | 원문 경로 정정 필요 | 실제 owner는 `tests/diagnostics/s11_boundary_temporal_probe.py`; 원문의 `scripts/...`에는 없음. 기존 constellation/ordered-patch를 새 발명처럼 반복하지 않음 |
| P3/P4 소유권·phase | 방향은 타당, 현재 채택 불가 | O2 및 별도 O3 계획 이후. cost-first 전역 변경이나 phase gate 동시 완화는 닫힌 실패를 반복함 |
| P5 Foam | 독립된 후속 과제로 타당 | 존재·upper 가시성·좌표·episode를 분리하고 raw-front 비교 동안 episode 고정 |
| P6/P7 목적 중심 평가 | 보고 관점으로 채택, gate 완화는 미채택 | A/B/C/U 분류는 해석 영향 설명에 사용. canonical 9구간·holdout·Windows·정식 수용 조건은 그대로 |

명세가 과거의 P1 미구현 상태를 기술한 부분은 10월 11일 마감 결과가 보충한다.
P1 성공을 P2 성공으로 확대하거나 이미 개발에 노출된 4개 recording/12개 frame을
23개 독립 holdout으로 셀 수 없다. 첫 001 JUnit은 392건, guard 적용 002와 resume은
396건으로 구분했다. 두 396건 실행은 같은 검사 집합의 반복이지 독립 792건이 아니다.

P2가 자동 detector 개선인지 optional reference를 쓰는 실험인지도 구분해야 한다.
구조물 비교가 미측정이면 positive 승리가 아니다. 같은 픽셀에서 만든 여러 값은
독립 표가 아니며, 공동 geometry만으로 coherent optical warp를 구별했다고 할 수 없다.
현행 holdout 부족은 그대로 남는다. 새 촬영이나 닫힌 사용자 판정의 반복을 선행
요구로 추가하지 않고, 가능한 개발 비교의 주장 범위를 제한한다.

## 통합 중 발견·수정한 재현 문제

원래 runner는 `--evidence-root`의 현재 `oil_material_path.py`를 baseline으로 읽었다.
후보가 main에 병합된 뒤에는 확장된 소스가 자기 자신과 byte/AST 비교되는 문제가
생긴다. 원래 분리된 checkout에서의 검증은 유효하지만, 통합 후 동일한 검증 주장을
유지하려면 기준을 고정해야 한다.

runner가 원래 Git object와 `0ccc85e5…` digest를 읽도록 보완하고, 새 preflight/readout에
baseline hash를 별도로 기록했다. 현재 코드·runner·입력 hash도 계속 고정한다.
Git 이력 부재나 baseline/manifest 불일치는 실패로 끝나며 조용한 대체는 없다.
저장소 밖 cwd에서 실행하는 CLI도 확인했다. 새로운 입력·threshold·후보 생성·P1 DP를
변경하지 않았고 `oil_material_path.py`는 원본 후보와 같은 `04178a2e…` 바이트다.

## 이번 직접 검증

- 원본 후보: 16개 관련 테스트 파일 **396 passed**, 실패/오류/skip 0.
- 통합 보완 후: 같은 파일 집합과 새 baseline 회귀 4건으로 **400 passed**,
  실패/오류/skip 0. 새 P1 파일은 62건이며 전체 저장소 suite를 뜻하지 않는다.
- main을 evidence root로, 저장소 밖 cwd에서 실제 `prepare` → `run` 완료.
  23조건 raw capture **23/23 SHA-256 동일**, 상태 33,674개·경로 12,477개 검산.
- 기존 29 input pin은 병합 전에 전부 일치했다. 새 manifest는 통합된 source를
  핀하므로 그 한 항목의 hash는 달라지고 나머지 28개 입력은 동일하다.
  원래 source는 별도의 역사 Git digest로 확인했다.
- 기존 기본 후보 필드 23/23 불변, 모든 원시 경로·입력 hash 검산 유지.
- S11 governance 통과. 추가한 로컬 링크/앵커 128개와 신규 카탈로그 87파일 확인.
  직접 작성한 활성 문서·코드는 `git diff --check` 통과. 전체 staged 검사에는
  제공 원문의 Markdown 줄바꿈/patch 문맥 공백 20건이 남으며, 원본 hash 보존을
  위해 그대로 두었다. 검사기나 저장소 규칙은 바꾸지 않았다.

새 전체 영상 decode, full sequence replay, Qt/전체 canonical suite, Windows,
report 효능 검증은 수행하지 않았다. 명시적 offline API와 runner 통합의 검증 범위이며
기존 R22 behavior·현장 합격을 새로 증명한다는 주장은 없다.

## 정리 범위와 재현

두 개의 등록 worktree 중 추가 P1 worktree의 모든 변경을 병합했다. 보존 manifest로
일반 산출물과 컨테이너 내부 파일을 다시 확인한 뒤 해당 worktree·병합 완료 브랜치와
원래 main의 중복 `s11-program-review-20261010-001` 폴더를 정리한다. 실제 완료 여부와
최종 worktree 목록은 [기계 receipt](2026-10-11-program-intake.json)의 `cleanup`에 기록한다.
다른 과거 실험 브랜치는 worktree가 아니며 채택되지 않은 코드가 있어 병합하지 않는다.

원본 미디어·Recipe·truth와 이 실험의 upstream crop/NPZ는 기존 main 경로에 유지한다.
원시 실행 증거는 이제 tracked reference 자료이지만, 모든 입력·환경을 담은 독립 실행
bundle은 아니다. 로컬 commit만 수행하며 원격 push는 이 작업에 포함하지 않는다.

통합 후 재현은 저장소의 Python 환경에서 다음을 사용한다. `$OUT`은 존재하지 않는
새 출력 경로여야 하며 완료된 historical 결과를 덮어쓰지 않는다.

```bash
.venv/bin/python scripts/s11_center_path_trial.py prepare --evidence-root "$PWD" --out "$OUT"
.venv/bin/python scripts/s11_center_path_trial.py run --evidence-root "$PWD" --out "$OUT"
```

즉시 다음 산출물은 P2 preflight이며 실제 순서는
[Work Plan](../../00-project/work-plan.md#adopted-program-and-immediate-p2-preparation),
설계와 수용 조건은 기존 [architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#p2-shared-support-role-comparison--proposal-entry)와
[validation](../../30-validation/s11-interface-observability-witness-validation.md#p2-shared-support-proposal-entry-and-program-evaluation)에 반영했다.
Roadmap의 milestone 상태·순서 및 retained commitments는 바뀌지 않는다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `TRACE-PUBLICATION`, `OIL-AUTHORITY`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: B's isolated lane loses position-compatible raw alternatives during per-seed winner compression. P1 preserves that representation; physical role, downstream ownership and the private Windows first cause remain separately unproven.
- Logic-map impact: NONE — the merged helper has no production consumer; the runner baseline correction and P2 proposal do not change executing detector control flow.
- Failure-registry impact: NONE — existing representation, identity, provenance and tuning guards cover this bounded integration; no new physical classifier or field repair is claimed.
