# S11 방향 명세 인수·타당성 검토 — 2026-10-12

**범위:** 첨부 전체와 관련 로컬 worktree/원본 산출물 확인, 보존·중복 정리,
명세 검토와 후속 계획. 시작점은 clean `main` = fetch 후 `origin/main` =
`5c53aefe3bb3c5d1447b29ccb2f78d1adc5459c6`이다.
**판단:** 명세의 문제 우선순위와 S2 수학 감사는 타당하다. 지원 조건을 먼저
정하고 유용한 관측·운동 맥락을 평가하는 방향을 권고한다. 다만 지원 범위
축소나 종료 기준 변경을 채택한 것은 아니며, 구현 가능한 새 역할 판별법도
확보하지 못했다. O2 OPEN / FIELD FAIL / Local XY OFF를 유지한다.

## 보존과 재현

| 자료 | 위치·처리 |
|---|---|
| 첨부 11파일 | [원본 안내](../../70-reference/s11-direction-decision-2026-10-11/README.md), [명세](../../70-reference/s11-direction-decision-2026-10-11/S11_PROGRAM_DECISION_AND_WORK_SPEC.md). 파일명과 bytes 그대로 보존; manifest 10/10 일치 |
| 로컬 감사 9파일 | [이동·중복 manifest](../../70-reference/s11-direction-decision-2026-10-11/import-manifest.json). 고유 stdout 로그 2개 추가, 나머지 7개는 기존 repo/첨부의 동일 bytes 재사용 |
| 추가 수학 감사 | [감사 JSON](../../70-reference/s11-direction-decision-2026-10-11/evidence/s2-decision-geometry.json), [도구](../../70-reference/s11-direction-decision-2026-10-11/tools/audit_s2_decision_geometry.py). 기존 S2 진단에서 연결 |
| 평가 양식 | [STORY_ACCEPTANCE_TEMPLATE.json](../../70-reference/s11-direction-decision-2026-10-11/STORY_ACCEPTANCE_TEMPLATE.json). 기존 canonical 9개 ID와 일치; 전부 NOT_EVALUATED인 참고 양식 |
| 이번 직접 검증 | [intake receipt](2026-10-12-direction-decision-intake.json). 새 실행 결과·원본 대응·정리 상태를 기록 |

전체 S2 receipt는 기존 `2026-10-11-p5-spatial-conjunction/verification.json`,
default receipt는 `2026-10-11-p5-default-linkage/readout.json`, P2 receipt는
`2026-10-11-p2-shared-support/verification.json`과 각각 완전히 같다.
별도 전사본을 새 원본으로 만들지 않는다. 과거 `sample/output` 경로는 manifest의
`source → preserved_at`으로 복구할 수 있다. 첨부 ZIP과 upstream 영상·raster·trace는
이번 중복 정리 대상이 아니다.

첨부의 `reproduce.sh` 자체를 **이번에는 실제 실행**했다. clean 기준 HEAD에서
검증기 3종, 수학 감사, focused test **162 passed / 25.46 s**가 통과했다.
수학 감사와 세 full receipt는 보존 원본과 byte equality까지 확인했다.
원문의 162 passed / 18.13 s는 이전 실행이며, P2 receipt 내부의 80 passed도
과거 pre-run 메타데이터다. 세 숫자를 별개 신규 시험으로 합산하지 않는다.

원본 wrapper는 clean `5c53aef`만 허용하므로 이 인수 커밋 이후 HEAD에서는
의도적으로 실행을 거절한다. 원문을 고쳐 pin을 느슨하게 하지 않는다.
수학 감사 단독 실행은 checked-in readout/preflight만 필요하지만, 원래 pixel/default
검증에는 보존된 ignored 입력이 필요하다. ZIP만으로 전체 실행은 불가능하다.

## 타당성 판단과 필요한 보완

| 항목 | 판단·반영 |
|---|---|
| 제품 목적 | 판독 보조와 충분한 same-interface 관측은 기존 제품 SSOT §1.2와 부합한다. 보편적 물질 판별 보장과 현장 유용성을 구별하되, 이를 실제 지원 조건이나 수용 기준이 이미 정해졌다는 뜻으로 읽지 않는다 |
| 주요 Oil 오류 | 보존 default report의 42 s 최저점 −18 px와 44 s 최고점 +28 px를 확인했다. 기존 source review의 wrong targets가 주요 극값을 만든다. 101/113 numeric은 이를 상쇄하지 못함 |
| Foam의 최초 손실 | default linkage 전체 113행/2,611 후보 연결이 재현됨. sample4의 살아 있는 Y813 대안이 component→front에서 내부 Y833으로 축약되는 문제와 water A의 밝기 support 손실을 분리하는 설명이 타당 |
| S2 비용식 | 2,556 cost triple에서 `C_U−C_N=0.5−b`, `C_U−C_I=a−0.5` 재현. 두 실제 양성의 b≈0.123/0.157은 U의 최소비용 조건에 미달. threshold 완화로 순위를 뒤집을 수 없음 |
| S2 ablation | 대비 있는 2,592 side에서 `0.5≤r0≤1` 확인. 위 side 대비가 양수이면 U가 I보다 엄격히 우세할 수 없음. 이 결과는 일반 비학습 방법의 불가능성 증명이 아님 |
| 합성 양성 표현 | §3.2의 합성 실패는 **동결된 joint 모델**에 한정한다. 기존 stationary/inclined 합성 예제의 ablation은 upper-cellular를 선호하며 복제 구조물도 동일하게 통과한다. ablation 전체나 가능한 모든 입력의 양성 영역이 없다는 주장은 하지 않음 |
| 구현 명세의 준비도 | 역할·support·fixed-X·consumer 분리는 유효하다. 그러나 새 관측 연산, 물리 연결, 대립 설명, missing/tie 규칙과 실제 positive reachability가 없으므로 P2/P5-a successor는 implementation-ready가 아님 |
| Windows 순서 | §8의 최종 통합 후 한 번 검증이라는 표현은 조건부다. **typed Witness의 O2 수용에는 V5 Windows shadow가 먼저 필요**하며, 이후 별도 O3 계획과 최종 9구간 field 검증을 거친다. 두 gate를 합치지 않음 |
| story 평가 | A/B/C/U와 1초 Oil 목표는 기존 계약의 구체화에 유용하다. 주요 episode, 허용 C 잔여·공백, Foam 시간 기준, source/truth 범위, holdout은 아직 완성된 수용 명세가 아님 |
| 참고 양식 | 9개 구간의 이름·의미는 맞지만 per-series contiguous run, 실제 시간/프레임 coverage, runtime/Recipe/source identity, owner/phase 전이와 분모를 기존 canonical report 요구에 맞게 보완해야 함. null 양식 자체는 gate나 truth가 아님 |

[KRÜSS AR279](https://pceu.kruss-scientific.com/en/know-how/application-reports/ar279-foam-behavior-of-toothpaste)의
LED/line sensor 높이 측정과 prism/camera 구조 측정의 분리,
[JMLR 논문](https://jmlr.org/beta/papers/v11/el-yaniv10a.html)의 risk–coverage 관점은
원 출처와 부합한다. 둘 다 현재 RGB sight-glass 검출 성능이나 새 역할 가설의
근거로 전환할 수 없다. ML·재촬영·장비 추가를 제안에 끼워 넣지 않는다.

## 후속 계획에 반영한 범위

현재 단계·실행 순서는 [Work Plan](../../00-project/work-plan.md#direction-decision-and-staged-follow-up)이
소유한다. 이번 변경에서 수학적 가능성 → 합성 양성 → 대표 실제 양성·대립 →
전체 동작 순서와 gate 의존성을 기존 [architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#successor-positive-reachability-and-independent-paths),
[validation](../../30-validation/s11-interface-observability-witness-validation.md#successor-reachability-and-story-preflight)에 반영했다.
이는 검증 절차의 보완이며 지원 범위 축소·새 classifier 채택은 아니다.

다음 P0 산출물은 다음 내용을 가진 **구체적인 범위·평가 계약 초안**이다.

- 입력/가시성에 근거한 지원·관측불가·미확정 조건과 평가 분모. 모델 성공 여부나
  영상명으로 지원 범위를 정하지 않으며 sample4 visible upper와 Accum layered를 유지한다.
- source로 보호할 주요 극값·반전·회복·Foam episode와 그 truth의 실제 정밀도.
  Oil 1초 적용 구간, 시작/끝 미관측, 허용 잔여와 Foam 시간 기준을 별도로 적는다.
- target-domain acceptance와 공개 stress 자료의 역할, 기존 노출 여부와 실제
  holdout 확보 가능성. 같은 episode/frame의 재분할로 holdout을 만들지 않는다.
- 현행 제품·검증 계약과 달라지는 조항의 명시적 diff. Water A 제외,
  copied-distractor gate 변경, 핵심 Foam 기능 철회는 이 인수로 승인되지 않았다.

그 뒤 Oil/P2와 Foam/P5-a는 서로의 성공을 선행 조건으로 삼지 않는다.
먼저 근거가 생긴 쪽에서 한 가설·한 structural ablation을 사전 고정해 검증한다.
Oil은 O2/V5 → 별도 O3 authority/association → 필요한 phase 순서,
Foam은 자기 역할/parent acceptance → raw front → correct raw의 독립적 소실이
확인될 때만 episode 순서다. Foam도 typed Witness를 소비하면 O2/O3를 거친다.
새 가설을 구체화하지 못하면 구현 준비 완료로 쓰지 않고 그 설계 한계를 남긴다.
단순 자료구조 개편, threshold 재조정, 새 report 기능은 선행 산출물이 아니다.

## 워크트리·정리 및 검증 한계

Git 등록, `.git/worktrees`, Codex managed Git 연결, 이 task의 attachment,
Developer의 관련 sibling checkout을 확인했다. **이 Mac에는 main 한 개**이고
병합·제거할 다른 활성 worktree는 없다. 로컬 branch 19개의 head/ancestry도
기록했다. 과거 미채택 실험·S12/legacy branch는 worktree 중복이 아니며,
고유 역사 근거를 삭제하거나 detector 코드로 병합하지 않았다.

로컬 감사 폴더 9파일/302,759 bytes의 모든 보존본을 확인했다. 보존 커밋을 만든
후 해당 원본 중복과 빈 폴더만 제거하며, 최종 결과는 receipt의 `cleanup`에 기록한다.
사용자 첨부, 기존 원본 media·실험 입력, 다른 출력 폴더는 유지한다.

이번 검증은 저장 증거·산술·문서 계약의 정합성이다. 새 영상 decode, detector
replay, 독립적인 report 이해도 실험, full canonical suite나 Windows 실행은
하지 않았다. source review의 물리 판단을 재라벨링하지 않았고, 새 운영 소스·설정·
truth·FIELD PASS를 만들지 않았다. governance, 신규 링크/앵커 49개, 카탈로그 16파일과 보존 매핑 20건을 확인했다.
새로 작성한 변경의 공백 검사는 통과했다. 전체 `git diff --check`는 첨부 원문
명세 3–5행의 Markdown hard break 공백 3건만 보고한다. 원문 hash 보존을 위해
고치지 않았으며, 해당 원본 이외 모든 변경은 통과했다. 상세 결과는 receipt에 있다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: the existing default linkage supports component-to-front loss of the qualified sample4 upper alternative; water A separately loses dark support at the lightness predicate. The added algebra explains the rejected offline S2 decision region, not a new private-Windows cause or a repair.
- Logic-map impact: NONE — only reference preservation, successor preflight and planning are changed; current runtime ownership, consumers and publication remain unchanged.
- Failure-registry impact: NONE — existing representation, identity, Foam-front, provenance and tuning failures cover this intake; no new mechanism or field acceptance is established.
