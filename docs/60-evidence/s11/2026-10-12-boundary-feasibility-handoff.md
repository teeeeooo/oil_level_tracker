# S11 경계 판별 연구 체크포인트 / 인수인계 — 2026-10-12

사용자가 요청한 작업 종료·재개용 스냅샷이다. 현재 상태와 다음 실행의 권한은
[Work Plan](../../00-project/work-plan.md), 전체 단계는
[Roadmap](../../00-project/roadmap.md)이 계속 소유한다. 이 문서는 새 실험이나
추가 기능을 승인하지 않으며, 다음 세션은 최신 소유 문서를 우선한다.

## 체크포인트

- 저장소: `/Users/sunjaekim/Developer/oil_level_tracker`, 브랜치 `main`.
- 연구·검증 기준: **`e19f6bdef167825c7dce3974ce585eee0dc7e475`**.
  handoff 시작 시 로컬 HEAD, `origin/main`, 실제 원격 main이 모두 일치했다.
- 이 문서와 [보존 검사 기록](2026-10-12-boundary-feasibility-handoff.json)을 추가하는
  후속 커밋이 문서 체크포인트다. `git log -1 --format='%H' --` 뒤에 이 문서 경로를
  지정하면 해당 커밋을 확인할 수 있다.
- 시작 시 변경 파일 없음, 등록 worktree는 현재 저장소 **하나**. 미커밋 변경이나
  이번 인계 때문에 보관·삭제할 중복 worktree는 없다.
- S11 ACTIVE, R22 behavior / R22-3·O1 diagnostics, O1 로컬 수용,
  **O2 OPEN / FIELD FAIL / Local XY OFF**를 유지한다.
- 직전 작업은 진단용 수식·테스트·고정 실험과 문서다. 제품 검출 코드는 바뀌지 않았고,
  실제 검출 성능 개선이나 Windows 수용을 입증하지 못했다.
- 현재 미응답 사용자 질문이나 대기 중인 Windows 실행은 없다. 여기서 종료하는 이유는
  사용자의 체크포인트·handoff 요청이며 S11 완료 판정이 아니다.

## 왜 이 작업을 하는가 / 전체 계획에서의 위치

목표는 압축기 영상을 일일이 읽는 수고를 줄이고, 믿을 수 있는 Oil/Foam 추세와
최저·최고·회복·발생 구간을 기존 Windows 앱의 그래프와 보고서로 전달하는 것이다.
몇 지점의 실패는 수용할 수 있지만, 다른 구조물을 유면으로 추적하여 주요 최저·최고값을
바꾸는 문제는 남아 있다. 이번 연구는 그 잘못된 경계 선택을 줄일 근거를 찾는 단계다.

| 순서 | 이 체크포인트의 위치와 다음 조건 |
|---|---|
| 앱 기반과 입출력 | S1–S10 완료. 설정, 결과 검토, CSV·보고서, 패키징 기반을 재사용한다. |
| 장면별 평가와 경계 판별 | 평가 역할 정리는 채택됨. **현재는 Oil/P2와 Foam/P5-a의 물리적 경계 판별 연구**이며 구현에 넘길 새 관측 방법은 미선정이다. |
| 판별 근거 검증 | 고정한 양성·반대·판정 불가 사례와 전체 후보에서 유효성을 입증한다. typed Witness는 O2 수용 전에 V5 Windows shadow가 필요하다. |
| 실제 추적·영상 전체 결과 | O2 뒤 별도 O3/O4 설계로 Oil의 지지·연결·단계 전환을 다룬다. Foam은 독립적인 raw-front 수용을 거치며, 올바른 raw 경계가 뒤에서 사라질 때만 P5-c를 연다. 기존 보고서의 영상 전체 유용성도 확인한다. |
| 최종 수용과 후속 정리 | 통합 후보의 Windows 9개 canonical 구간·자원·보고서 검증과 명시적 field 판정 후 S11-M/S12로 진행한다. |

단계별 별칭과 정확한 수용 조건은
[Work Plan의 순서표](../../00-project/work-plan.md#direction-decision-and-staged-follow-up)를 따른다.
아직 판별 후보가 없으므로 Windows 실행이나 추적·보고서 보정부터 시작하지 않는다.

## 이어받을 핵심 결과

| 근거 | 확인된 사실 / 경계 |
|---|---|
| [첨부 명세서 통합·판단](2026-10-12-direction-decision-intake.md) | 첨부 원본과 산출물은 기존 `70-reference` 및 evidence 경로에 보존됐다. compressor 대 water/beer/milk의 A/B 구분은 보류하고 장면·주장·업무 영향별 평가를 채택했다. 원래 sample1–4를 모두 정밀 truth로 취급하지 않는다. |
| [미소냉동 source 및 실제 파이프라인](../../50-diagnostics/s11/2026-10-12-public-compressor-source.md#bounded-application-pipeline-linkage) | 확인된 Oil 구간보다 위쪽 후보가 최종 Oil anchor로 채택된다. f1499에서 current Oil Y321, completed Oil Y288이며 lower 관측은 남아 있다. Foam current Y317도 이미 확인 범위 밖이므로, 뒤 단계의 유실만 고쳐 해결할 사례가 아니다. 세 프레임의 NONE/FULL과 72개 후보 계보를 검증했다. |
| [행별 색 분포 실험](../../50-diagnostics/s11/2026-10-12-p2-row-distributions.md) | 수치적으로 가능한 synthetic 양성은 통과했지만 고정한 실제 양성/반대 쌍에서 반대 역할을 판별하지 못했다. `CLOSED WITHOUT PROMOTION`. |
| [평균 비교의 전체 후보 결과](../../50-diagnostics/s11/2026-10-12-p2-row-distributions.md#complete-candidate-result-and-disposition) | 설정을 바꾸지 않은 평균 비교는 알려진 Oil 6개 중 4개를 유면 쪽으로 평가했다. 그러나 160개 전체 후보에서는 별도의 하단 후보도 같은 평가를 받고, 두 Oil 누락 프레임에서는 하단만 남았다. 원래 14개 기준 기록을 보존한 164개 query 결과이며 `DIAGNOSTIC_ONLY_NO_PROMOTION`. |

평균 비교의 4/6은 검출 정확도나 제품 성공률이 아니다. 미검토 하단 후보의 물리적 역할은
계속 UNREVIEWED이며, 단순 위치 차이를 새 오답 라벨로 승격하지 않는다. 결론은 이 외관
측정만으로 안전한 후보 선택을 뒷받침할 수 없다는 것이다. 모든 reference 기법이
불가능하다는 결론이나 전체 프레임 무오류 요구가 아니다.

## 닫힌 판단과 재개하지 않을 경로

- 사용자 확정: 미소냉동 밝은 층의 **윗 경계는 Foam 상단, 아랫 경계는 Oil 상단**.
  [위치 답변](../../50-diagnostics/s11/2026-10-12-public-compressor-source/position-review/position-review.json)은
  native f1499 / 50.016633 s / X578에서 Foam rows323–338, Oil rows421–435를 포함한다고
  확인했다. 한 픽셀 정답, 구간 내 모든 후보의 정답, 이웃 프레임 truth 또는 holdout이 아니다.
- 기존 sample4, water A/B/C, beer/milk의 역할·위치 답변도 해당 범위대로 닫혀 있다.
  필요한 사례만 [Recall Index](../../00-project/recall-index.md)로 찾아 재사용하고 다시 묻지 않는다.
- sample3는 계속 격리한다. 새 decode, 클립 발굴, relabeling, 연속 정확도 연구를 하지 않는다.
  필요성이 생긴 기존 engineering/legacy 재현만 기존 purpose guard 계약을 따른다.
- P2-S1, P5-S2/S3, H0/G1/CBR-1, Local XY와 이번 분포·평균 경로를 이름만 바꿔
  재시작하지 않는다. 임계값·window·reference·제외 영역·후보 순서를 조정해 구제하지 않는다.
- 같은 프레임의 관측 후보와 정확한 provenance, 고정 중앙 X, Oil/Foam의 독립 소유권,
  불명확한 관측의 fail-closed를 유지한다. nearest-Y, 이전 값 복사, 보간·보고서 보정으로
  검출 성공을 만들지 않는다.
- 일부 국소 실패를 허용한다는 원칙은 채택됐지만 수치 허용량은 미정이다. 결과를 본 뒤
  불리한 장면을 제외하거나 all-UNKNOWN을 성공으로 세지 않는다.
- ML, 추가 촬영 요구, 반복 수동 재지정, 새 제품 설정 또는 전체 재설계는 현재 채택된
  다음 작업이 아니다. 로컬 실험용 기준 문맥 세 개가 새로운 필수 사용자 설정이 된 것은 아니다.

## 다음 세션의 최소 시작 순서

1. `git status`, HEAD와 현재 Work Plan 상단을 확인한다. 이 스냅샷 이후 변경이 있으면
   최신 소유 문서를 따른다. 커밋·푸시 권한은 이미 주어졌으며 같은 확인을 반복하지 않는다.
2. [S11 skill](../../../.agents/skills/s11-detector-change/SKILL.md)의 bounded recall을 따른다.
   먼저 방금 닫힌 전체 후보 결과와 public-source pipeline 결과를 읽고, 관련 logic-map
   node와 F01/F03/F06/F09/F10 중 필요한 실패 항목만 펼친다. 전체 revision 탐색이나
   이미 통과한 모든 검사를 반복하는 것으로 시작하지 않는다.
3. [기존 successor 설계 진입점](../../20-architecture/s11-interface-observability-witness-architecture.md#successor-positive-reachability-and-independent-paths)에서
   **반복 무늬와 물리적 계면을 구별할, 기존 실패 모델에 없던 관측 정보 하나**를 구체화한다.
   P2/Oil과 P5-a/Foam은 독립 경로다. 어떤 기법도 이 handoff에서 선정된 것으로 가정하지 않는다.
4. 구현 전에 물리적 이유와 반대 설명, 실제 지원 픽셀, 수식·정규화, 누락·동률 처리,
   양성 도달 가능 영역, 한 가지 ablation과 고정 비교 범위를 정의한다. 실제 연산으로
   synthetic 양성을 측정한 뒤 고정된 실제 양성·반대 사례를 검사한다. 선택된 정답 위치만의
   통과를 전체 후보 선택의 성공으로 옮기지 않는다.
5. 구현할 근거가 생기면 기존 helper·candidate·selection owner를 먼저 재사용한다.
   [검증 진입 조건](../../30-validation/s11-interface-observability-witness-validation.md#successor-reachability-and-story-preflight)에
   따라 첫 실패에서 해당 모델을 닫고 근거와 한계를 남긴다. 새 사용자 판단이 결과를
   바꾸거나 실제 Windows 단계에 진입할 때만 사용자에게 알린다. 지금은 새 질문이 없다.

## 보존 자료와 재현 범위

[검사 기록](2026-10-12-boundary-feasibility-handoff.json)은 읽기 전용 해시·보관 검증이다.
새 영상 분석이나 실험 재실행 없이 다음을 확인했다.

- 최신 candidate preflight의 **293개 입력 해시 일치**, 그중 제품 Python 소스 **221개**.
- primary / follow-up / all-candidate readout 세 개와 기존 검증 receipt의 해시 일치.
  이전 32개 집중 테스트 통과 및 각각 396 / 2,970 / 26,928개의 독립 CDF 연산 검증은
  기존 결과를 재사용한다. 이번 문서 작업에서 테스트나 수치 실험을 다시 돌리지 않았다.
- public current-frame 저장물은 8개 logical 파일을 6개 payload로 정확히 복원 가능하다.
  pipeline ZIP은 95개 logical 파일 / 68개 unique member의 길이·해시가 모두 일치한다.
- 원본 `sample/public_miso_mHOS1-1ck60.mp4`의 13,480,200 bytes와 SHA-256 일치.
  public media와 기존 원본 영상은 Git 밖에 남는다. 다시 다운로드하거나 re-encode하지 않았다.

**새 clone만으로 모든 재실행 입력이 생기지는 않는다.** 현재 비교의 Git 제외 입력
45개는 아래 기존 디렉터리에 있으며, 정확한 파일 목록은 검사 기록과
[candidate preflight](../../50-diagnostics/s11/2026-10-12-p2-row-distributions/candidates-preflight.json)에 있다.

- `sample/output/s11-a1-lineage-20261007-001/frames-final/`: 29개 capture/PNG/manifest.
- `sample/output/s11-local-xy-implementation-20261009-001/v2-sample4-scoped-FULL/`:
  기존 f450, f1620, f1665, f1680 캡처의 16개 PNG. 긴 하위 경로는 manifest를 그대로 따른다.

이 자료는 동일 호스트에 보존한다. 다른 환경에서 해당 재현이 필요할 때만 기존 파일을
경로·바이트 그대로 옮겨 hash를 확인한다. 누락 파일을 새 decode로 조용히 대체하지 않는다.
public source의 Git 추적 캡처는
[current-frame 저장표](../../50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/capture-storage.json)와
[pipeline 저장표](../../50-diagnostics/s11/2026-10-12-public-compressor-source/pipeline-linkage/storage.json)가
압축 파일·alias를 소유한다. 중복 사본이나 전체 영상 ZIP을 새로 만들지 않았다.

## 재개용 메시지

```text
/Users/sunjaekim/Developer/oil_level_tracker에서 이어서 진행해줘.
AGENTS.md, docs/00-project/work-plan.md와
docs/60-evidence/s11/2026-10-12-boundary-feasibility-handoff.md를 먼저 확인해줘.
전체 목표는 Windows 앱으로 Oil/Foam 영상의 수작업 판독을 줄이는 것이고,
현재는 물리적 경계 판별 단계야. e19f6bd까지의 분포·평균 비교는 제품 적용 없이
종료했어. 전체 160개 후보에서 드러난 대안 위치와 기존 실패를 재사용해,
다음 구별 가능한 관측 근거 하나를 먼저 설계·검증해줘. 새 기법은 아직 미선정이야.
닫힌 역할·위치 질문, sample3 추가 분석, 임계값/reference 조정으로 실패 실험을
다시 열지 말아줘. 기존 owner를 재사용하고 과거 검증은 변경으로 무효화된 범위만
다시 확인해줘. 커밋·푸시는 자율적으로 진행하고, 내 새 판단이나 Windows 실행이
실제 필요한 지점에서 알려줘. O2 OPEN / FIELD FAIL은 유지해.
```

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`
- Failure-registry entries: `S11-F01`, `S11-F03`, `S11-F06`, `S11-F09`, `S11-F10`
- First harmful stage: the retained public-source pipeline admits an upper Oil anchor despite surviving lower observations; the closed regional appearance diagnostic lacks physical candidate-selection evidence. This handoff performs no new detector investigation or replay.
- Logic-map impact: NONE — checkpoint, input-preservation verification and resume routing only; no detector source, candidate authority, coordinates or product behavior changes.
- Failure-registry impact: NONE — retains the existing closed mechanisms and their limits; no new physical labels, remedy or field acceptance are asserted.
