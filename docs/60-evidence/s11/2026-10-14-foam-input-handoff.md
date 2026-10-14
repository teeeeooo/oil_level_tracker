# S11 main 체크포인트 / Foam 입력 조사 인수인계 — 2026-10-14

사용자의 체크포인트·인수인계 요청으로 남기는 재개 기록이다. 현재 상태와 다음
실행의 단일 owner는 [Work Plan](../../00-project/work-plan.md)이다. 이번 도달점은
사용자 판독의 결합과 실제 기준 실행기의 입력 누락 원인 확인이며, 검출력 개선이나
후보 채택·S11 완료가 아니다.

## 체크포인트

| 항목 | 확인한 상태 |
|---|---|
| 저장소 | `/Users/sunjaekim/Developer/oil_level_tracker` |
| 인계 위치 | `main` — 미채택 guard를 철회한 뒤 진단 도구·판정·증거를 통합 |
| 인계 대상 연구 HEAD | **`421757afd58776a5e13d4ee226e4a2a317f5a858`** — 인계 시작 시 원격 작업 브랜치와 일치 |
| 인계 시작 시 원격 main | `747c1bccaa8dab18d6cb3a2b3dc3e549bcfc668f` |
| 구현 철회·증거 통합 커밋 | **`b225dd1297839dea1651ace087fe7d4bf479f848`**, main에 fast-forward 반영 |
| 인계 시작 상태 | 변경 파일 없음; 등록 worktree는 현재 checkout 하나; 관리 run 66개 모두 종료·오류 0 |
| 수용 상태 | S11 ACTIVE, R22 behavior / R22-3·O1 diagnostics, **O2 OPEN / FIELD FAIL / Local XY OFF** |
| 대기 중인 작업 | 미응답 판독 질문·진행 중 실험·요청해 둔 Windows 실행 없음. 사용자 요청에 따라 여기서 인계 |

이 문서를 추가한 커밋이 인계 문서 체크포인트다. 문서 이력은 다음으로 확인한다.

```bash
git log -1 --format='%H' -- docs/60-evidence/s11/2026-10-14-foam-input-handoff.md
```

**미채택 구현을 철회하고 main에서 인계한다.** 사용자 지시에 따라 `0073def`의
overlay-support guard와 그 동작을 요구하는 테스트 두 개를 제거하고, 두 파일을
`747c1bc` bytes로 복원했다. 전체 `src/`는 위 기준 main과 동일하다. 13-case 비교
통과와 별개로 남았던 sequence 실패를 기준 동작 복원 후 검증하며, 실패한 후보의
동작을 채택하거나 assertion을 느슨하게 하지 않는다. 후보 코드·원래 테스트는
Git commit `0073def`에서, 모든 측정은 기존 readout에서 복구 가능하다.
새 patch/ZIP이나 다른 생산 구현 사본은 만들지 않는다.

검증된 진단 도구·판정·실패 기록·후속 설계를 main에 fast-forward로 통합해 이력을
보존했다. 원격 main 게시와 `work/s11-overlay-component-20261014`의 원격 ref 제거를
한 atomic push로 처리하고, main에 병합된 로컬 ref도 삭제했다. 다른 기존 브랜치는
이번 후보 정리 대상이 아니다. 저장소 작업 위치는 main이고 추가 worktree는 없다.

## 재개 시 읽을 범위

1. [Work Plan](../../00-project/work-plan.md)의 현재 gate·next transition과
   [S11 skill](../../../.agents/skills/s11-detector-change/SKILL.md).
2. [원인 조사 — 표시한 상단](../../50-diagnostics/s11/2026-10-14-raw-front-inventory.md#marked-upper-loss-before-material-components)과
   [raw Foam 입력 선행 조건](../../20-architecture/s11-contextual-role-observation-design.md#raw-foam-representation-prerequisite).
3. 과거 실패가 필요하면 [recall index](../../00-project/recall-index.md)의 해당 행만
   따라간다. CR-1부터 전체 이력을 다시 조사하거나 완료된 비교부터 재실행하지 않는다.
4. 실제 변경 owner와 수용 범위는 [logic map](../../20-architecture/s11-current-detector-logic-map.md#quick-start--design-index),
   [Witness validation](../../30-validation/s11-interface-observability-witness-validation.md#post-cr1-operating-policy-and-consumer-acceptance),
   [physical-interface validation](../../30-validation/s11-physical-interface-evidence-repair-validation.md)을 따른다.

## 확인된 사실과 그대로 남은 한계

| 확인된 사실 | 다음 작업에서 보존할 의미 |
|---|---|
| base_sample_1/f144, 4.8048 s, X696: path 150은 **거품–액체 하단 접촉** | [정확한 경로 판독](../../50-diagnostics/s11/2026-10-14-raw-front-inventory/base-reply.json)이다. 근처 Oil Y395나 pooled-sector 경로의 동일성을 뜻하지 않는다. 기존 f144 `foam_present=false`는 새 물리 target에서 제외하지만 원래 `.oiltruth` bytes는 보존한다. f156의 별도 충돌은 해결되지 않았다. |
| 같은 프레임의 빨간 점 6개는 **거품 상단의 지역 위치**, 원본 Y 약 367–370 부근 | [원문 JPEG](../../50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-user.jpg)와 [대응 기록](../../50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-reply.json)을 보존했다. 점들이 감싼 국소 형상만 해당하며, 정확한 scalar·native 경로·전체 층·pure-side mask·인접 프레임 정답은 아니다. 질문은 CLOSED다. |
| 표시 영역 368픽셀 모두 유효, glare 0; Lab L 16–64 < 기존 white floor 125; raw white/warm support 및 Canny 0 | [실제 owner 관측](../../50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-stages.json.gz)에서 cleanup/component 이전부터 입력이 없다. Texture는 일부 존재하지만 역할 근거가 아니다. threshold 하나를 낮추거나 추적을 고치면 회복된다는 증거는 없다. |
| 전체 fresh-frame 결과는 기존 저장 결과와 동일: Oil 후보 22개, 선택 Y395; Foam 후보 0개 | [전체 후보 receipt](../../50-diagnostics/s11/2026-10-14-raw-front-inventory/base-frame-entry.json.gz)를 재사용한다. 두 weak-rejected Foam component는 이미 확인된 하단보다 아래에 있다. 현재 프레임 조사이며 전체 window/episode/report 최초 손실은 아니다. |
| native corpus는 137개 경로 / 19 qualified / 118 unknown, native input 101 / saved semantic input 39 | [기존 corpus](2026-10-14-semantic-context.md#water-upper-reply-and-complete-native-corpus)와 [708](../../50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-extension.json), [f144 delta](../../50-diagnostics/s11/2026-10-14-raw-front-inventory/base-extension.json)를 그대로 연결한다. Foam–liquid 양성은 세 recording hash, liquid–air는 하나다. 서로 다른 hash가 독립 촬영을 입증하지 않으며, 이번 빨간 점은 qualified 경로 수를 늘리지 않는다. |
| sample3 A는 액체–빈공간, 후보/지역 정밀도이며 baseline native 경계가 없음 | raw plateau graph도 바로 쓸 수 있는 물리 경로로 검증되지 않았다. A/B와 C/D의 기존 범위 및 sample3 전체-window 제한을 보존한다. 가까운 Y로 native 정답을 만들지 않는다. |

**로컬 `base_sample_1`은 사용자의 Windows 영상에 있는 `BASE`가 아니다.**
Windows BASE 검출률 0%와 Accum 문제는 [기존 bundle 분석 재사용 기록](2026-10-14-overlay-support-guard.md#existing-bundle-analysis-reuse--planning-correction)을
따른다. 사용자 전달 비교의 tracking 1,202행은 run_id 외 동일하며 Accum 해석은
69.88% → 5.99%로 바뀌었다. 이 차이를 overlay 하나의 인과 효과로 확정하지 않는다.
기준 manifest 불일치를 이유로 비교를 버리거나 같은 Windows 실행을 다시 요청하지
않는다. 전달 bundle의 Darwin 메타데이터와 실제 Windows 검증 여부는 구분한다.

## 닫힌 연구와 첫 후속 산출물

CR-1 첫 trial은 CLOSED_WITHOUT_PROMOTION, 전체 검토는 SCOPE_LIMITED_USEFULNESS다.
[사용자 요청에 따른 runtime 정리](2026-10-13-post-cr1-review-intake.md#cr1-runtime-retirement-2026-10-14)가
완료돼 모델/source와 공유 연구 환경은 제거됐고, 필요한 판정·점수·핀·입력은 남아 있다.
RGB/평균색의 rim 오인, N3를 잃은 native head, 공개 rim 순서에 실패한 NRO-1,
우유 컵 경계에 실패한 SCM-1, NCT-1과 raw plateau graph의 한계는 각 기록대로 닫혔다.
그 모델을 복원하거나 seed/crop/head/threshold 변경으로 같은 시험을 재개하지 않는다.
기존 상단·하단·rim·우유 큰 방울·물 하단 판독 불가 질문도 반복하지 않는다.

재개 후 첫 산출물은 **실행 가능한 raw Foam 관측 설계 하나**다. 알고리즘은 아직
선정되지 않았다. 위 선행 조건은 구현 완료나 검증된 새 검출기를 뜻하지 않는다.

1. 기존 ROI 원본을 사용해 Canny/white/chromatic seed가 없는 위치의 관측을 어떻게
   보존할지, 기존 원시 표현·failed trial과 어떤 정보가 다른지 명시한다. 현재 owner와
   호출 경로를 조사한 뒤 재사용할 수 없는 책임에만 새 구현을 둔다.
2. **후보를 만들 수 있음**과 **물리 역할을 구별함**을 각각 시험한다. N3, 공개 상단
   4개, milk의 큰 방울 상단 및 물·base의 지역 상단을 보존하면서 기존 내부 변화와
   유리 rim 대조군을 함께 다룬다. 지역 box와 겹친 것만으로 정확한 경로 검출 성공을
   세거나, 입력 결측·전부 거부를 음성 분류 성공으로 세지 않는다.
3. 입력·source별 사용 범위, 역할 정밀도, 비교식·통과/중단 조건·자원 예산을 실행
   전에 고정한다. [기존 기능 검토](../../30-validation/s11-detector-change-governance.md#existing-system-review-before-execution)와
   [산출물 관리](../../40-operations/experiment-artifact-lifecycle.md)를 따른다.
   새로운 물리 판정이나 중요한 선택이 필요해질 때만 질문한다.
4. 실제 올바른 raw upper가 확보된 뒤 current candidate/sequence로 연결한다. Episode
   손실은 올바른 raw upper가 downstream에서 사라진 근거가 있을 때 다룬다.
   O2/V5와 최종 Windows 9개 구간·독립 report 판독은 각각 기존 수용 gate를 유지한다.

사용자의 커밋·푸시 자율 권한은 유지한다. Windows는 Git clone 없이 GitHub ZIP을
압축 해제해 사용하는 격리 PC이며, 필요한 지점에 도달하면 멈추고 실행 범위를 알린다.
현재는 Windows 재실행 준비 단계가 아니다. 원격에서 로컬 HTML 이미지·영상이 보이지
않으므로 다음 물리 검토에는 직접 표시한 이미지나 전달 가능한 파일을 쓴다.
[20분 분석 + 약 5분 후처리 성능 문제](../../00-project/retained-commitments.md#windows-analysis-throughput-after-detector-improvement)는
검출력 개선 뒤로 유보돼 있다. FULL/NONE 차이를 원인으로 재단하지 않는다.

## 로컬 입력과 검증 인계

새 연구 run이나 ZIP·영상·worktree 복제 없이 기존 파일을 참조한다. 핵심 코드와
작은 증거는 Git에 있고, 아래 `sample/output` 원본은 로컬 의존성이다. 새 clone이나
GitHub source ZIP만으로 모든 재현 입력이 갖춰졌다고 가정하지 않는다.

- [원본 입력 plan](../../50-diagnostics/s11/2026-10-14-raw-front-inventory/base-plan.json):
  `sample/output/s11-truth-audit-20261010-002/base_sample_1/f000144.png`, 같은 run의
  `capture.json`, `sample/base_sample_1.mp4`, `.oilrecipe`, `.oiltruth`의 위치·SHA.
- [실제 기준 진입 plan](../../50-diagnostics/s11/2026-10-14-raw-front-inventory/base-probe-plan.json)과
  [probe](../../50-diagnostics/s11/2026-10-14-raw-front-inventory/probe_base.py):
  `OpenCvPhaseDetector.detect` 및 debug projection. [기존 비교 plan](../../50-diagnostics/s11/2026-10-14-overlay-component-review/comparison-plan.json)의
  baseline `747c1bc…`, preprocessing SHA `55e33486…`를 사용한다. CLI를 그대로
  실행할 때는 해당 Git object가 필요하다. Windows ZIP에서 Git 기반 이 연구 helper를
  실행하라고 지시하지 않는다.
- [표시 결합·단계 plan](../../50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-stage-plan.json)과
  [검사기](../../50-diagnostics/s11/2026-10-14-raw-front-inventory/inspect_foam_upper.py)는
  기존 물 자료의 observer와 위 probe를 재사용한다. 실제 실행·독립 검산 명령은
  [원인 기록](../../50-diagnostics/s11/2026-10-14-raw-front-inventory.md#marked-upper-loss-before-material-components)에 있다.
  새 재현이 필요하면 새 managed work와 그 안의 font/cache 경로를 사용한다.

최근 f144 baseline helper와 독립 검산기는 기준 source를 사용한다. 반면 폐기된
overlay **후보 비교**의 원래 plan은 candidate source hash를 요구하므로, 복원된
main에서 그 후보 CLI를 그대로 실행하면 pin 검사가 실패한다. 이는 올바른 거부다.
과거 candidate 재현은 해당 Git commit의 실행 범위이며, main의 source나 frozen
plan을 바꿔 통과시키지 않는다.

이번 인계에서는 **4개 plan이 참조한 고유 핀 40개**와 **실제 프레임 receipt의 source
221개**를 검증했다. 전처리 한 파일은 위 baseline Git object와 비교했으며 나머지는
현재 파일 bytes와 비교했다. 저장된 독립 검산 receipt가 가리키는 단계 readout SHA도
일치한다. 전체 corpus/모든 영상/Windows 환경을 새로 검증했다는 뜻은 아니다.
철회 후에는 저장된 baseline receipt의 **221개 source 모두 현재 파일 bytes와 직접
일치**함도 확인했다. 변경 문서의 링크·anchor **379개**, main 통합 범위의 새 문서
157개 색인 연결, governance·whitespace 검사도 통과했다.

직전 구현 단계의 **48 tests PASS**, 368픽셀·9개 채널·8개 눈금의 독립 검산을 해당
범위에서 재사용한다. source 복원 후 새로 수행한 검증은 다음과 같다.

| 검사 | 결과와 범위 |
|---|---|
| 이 브랜치에서 추가/수정한 진단 unit 10개 파일 + optics/Foam 3개 파일 | **254 passed in 6.67 s**; model weight나 실제 학습 없이 입력 결합·qualifier·표현·계산 및 기존 전처리/거품 계약 확인 |
| `tests/test_s11_sequence_observability_integrity.py` | **1 passed in 21.13 s**; `s11_corpus_access --purpose legacy-regression`으로 한 명령만 허용. 미채택 후보의 실패를 숨기지 않고 baseline 복원 후 기존 assertion 전체 통과 |
| `git diff 747c1bc -- src tests/test_optics_preprocessing.py` | 차이 없음. production source 전체와 기존 optics test 파일이 기준과 동일 |
| `experiment_artifacts.py check` | 관리 run **66개, 오류 0** |

새로운 가설·물리 수용·학습·Windows 시험은 실행하지 않았다. Sequence 검사는
engineering regression이며 sample3의 물리 평가 제한을 해제하지 않는다.
직전 run의 중간 cache 6개는 제거됐고, 원문 JPEG·plan·스크립트·결과는 canonical
위치 한 곳에 있다. 이번 main 통합 범위에서 빠진 기존 증거 81개의 날짜 색인을 실제 최초 Git 추가일로 보완했다.

## 재개용 메시지

```text
oil_level_tracker에서 이어서 진행해줘.
docs/00-project/work-plan.md와
docs/60-evidence/s11/2026-10-14-foam-input-handoff.md를 읽고,
기존 실패와 다른 raw Foam 관측의 실행 가능한 설계부터 진행해줘.
main에서 421757a까지의 판독·원인 검증을 재사용하고, 철회한 overlay 후보를
다시 활성화하지 말아줘. 커밋·푸시는 자율적으로 진행하되
내 물리 판정이나 Windows 작업이 필요하면 멈추고 알려줘.
```

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: 새 판정 없음. f144의 유효 영역에서 raw white/warm membership과 Canny가 없어 cleanup/component 이전에 누락된 기존 결과를 인계한다. private Windows BASE나 전체 sequence 최초 손실로 확대하지 않는다.
- Existing feature coverage: 최근 probe는 원래 Recipe ellipse/margin/settings, 빈 exclusions/templates/reference와 Local XY OFF를 사용했다. fresh detector에 이전 temporal/static 학습·session 확인·완료 resolver/report는 없었다. 이번 인계는 이 실행 범위와 baseline 치환을 확인하며 설정을 바꾸지 않는다.
- Execution scope: Git/워크트리·관리 run·기존 40개 pin/221개 source·저장 receipt 확인, baseline source/test 복원, 관련 진단 unit suite와 기존 sequence regression, 문서·색인 및 main 인계. sequence 검사는 기존 engineering regression이며 새 물리 판독·모델·Windows 수용은 없다.
- Logic-map impact: UPDATED — 실행되지 않는 original-component guard 설명을 제거하고 기준 opened-core 전처리와 현재 source의 일치를 복구한다. owner 연결 순서는 그대로다.
- Failure-registry impact: NONE — 기존 입력 누락·provenance·역할 수용 한계를 전달하며 새 실패 family나 개선 수용을 추가하지 않는다.
