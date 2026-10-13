# S11 역할 관측 연구 체크포인트 / 인수인계 — 2026-10-13

사용자의 체크포인트·인수인계 요청에 따른 재개용 기록이다. 현행 상태·권한·다음
실행은 [Work Plan](../../00-project/work-plan.md)이 계속 소유한다. 이 스냅샷은
S11 완료나 새 검출 방식의 채택을 뜻하지 않는다.

## 체크포인트와 검증 범위

- 저장소 `/Users/sunjaekim/Developer/oil_level_tracker`, 브랜치 `main`.
- 연구 기준 **`d23f0a562f282e66380c8d68131478e5f0031ee5`**. 인계 시작 시 로컬
  HEAD와 실제 원격 main이 일치했고, 변경 파일 없이 등록 worktree 하나였다.
- 이 문서를 추가한 커밋이 인계 문서 체크포인트다. 이후 문서가 갱신됐는지는
  `git log -1 --format='%H' -- docs/60-evidence/s11/2026-10-13-material-role-handoff.md`로 확인한다.
- S11 ACTIVE / R22 behavior / R22-3·O1 diagnostics / **O2 OPEN / FIELD FAIL /
  Local XY OFF**를 유지한다. 새 생산 detector나 Windows 수용 결과는 없다.
- 미응답 사용자 질문·대기 중인 Windows 실행·진행 중인 관리 실험은 없다.
  이 세션은 사용자 요청에 따라 연구를 여기서 마무리하며, 재개 후 첫 일은 아래 설계안이다.
- 이번 인계에서는 입력 142개와 encoder/model 핀 159개의 bytes, 종료된 관리 실행
  14개, 임시 작업 폴더 제거를 확인했다. 새 모델 추론·영상 decode·검출 테스트는
  실행하지 않았다. 직전 코드 검증의 **22 passed**는 아래 결과 기록을 재사용한다.

## 이어받을 결정

| 근거 | 보존할 의미 |
|---|---|
| [Post-CR1 인수 기록](2026-10-13-post-cr1-review-intake.md) | 첨부 명세·재현 자료는 기존 owner에 배치됐다. WP01–WP10은 Work Plan의 기존 O/W/P gate에 연결된다. 전체 detector 재작성은 채택되지 않았다. |
| [B 판정 정정](../../50-diagnostics/s11/2026-10-13-cr1-competitor-role.md) | sample4 f1485의 B는 사용자가 실용적인 Foam–Oil 경계 근사로 허용했다. 물리적 순수 계면 정답이나 A/Y836의 새 양성 판정이 아니다. CR1의 texture 선호만으로 성공·실패를 판정하지 않는다. |
| [R 답변](../../50-diagnostics/s11/2026-10-13-foam-material-reference/reply.json) / [L 답변](../../50-diagnostics/s11/2026-10-13-foam-material-reference/coarse-reply.json) | R은 매우 미세한 Foam, L은 큰 알갱이 Foam의 **25×25 내부 기준 영역**으로 승인됐다. 두 질문은 CLOSED. 각 영상의 전체 mask·정확한 경계·이웃 프레임 truth가 아니다. 별도 기준을 유지하며 약한 유사도를 Foam 부재로 해석하지 않는다. |
| [고정 R/L 비교 결과](../../50-diagnostics/s11/2026-10-13-foam-material-sides.md) | 43개 장면, 1,335개 경계를 모두 보존했다. 1,184개 측정, 119개 지원 부족, 32개 RGB 없음. **CLOSED_WITHOUT_PROMOTION**이며 원래 CR1의 `SCOPE_LIMITED_USEFULNESS`를 덮어쓰지 않는다. |

이번 연산이 해결하지 못한 핵심은 세 가지다. sample4의 상단 포함 구간에 있는
Y813 경계는 상측 236/275픽셀만 유효하여 점수 계산 전에 빠졌다. 39픽셀은 기존
effective mask 밖이며 glare가 원인은 아니다. 이 경계를 새 오답으로 분류하면 안 된다.
또한 큰 알갱이→미세 알갱이의 **구성 대조 이미지**에서 두 기준 모두 양의 하측−상측
차이가 나왔고, local L 유사도는 실제 no-Foam 물 장면의 포함 구간과 겹쳤다.
세 내부 무늬 guide에는 정확한 중앙 Canny 연결이 없어 억제 성과를 평가하지 못했다.

R/L 초기화 영상은 노출된 기준 자료다. L이 포함되면서 물 A도 기준 episode가 됐고,
B/C는 같은 영상의 개발 대조군이다. 유형별 독립 일반화·물리적 선택·보정된 정확도는
NOT_EVALUATED다. 이미 검토한 자료를 holdout으로 다시 세지 않는다.

## 다음 세션의 첫 산출물

**기존 실패와 다른 관측 정보, 재사용할 코드 owner, 비교 방법과 통과·중단 조건을
명시한 실행 가능한 설계안 하나**가 첫 산출물이다. 새 알고리즘은 아직 선정되지 않았다.

1. 최신 Work Plan과 [S11 skill](../../../.agents/skills/s11-detector-change/SKILL.md),
   위 고정 비교 결과를 읽고 관련 logic-map/failure 항목만 확인한다. 전체 역사 탐색이나
   이미 충분히 통과한 실험 재실행부터 시작하지 않는다.
2. 기존 native candidate/path/support owner를 조사해 실제 상단·내부 무늬 후보와
   이용 가능한 양측 픽셀의 연결을 설계한다. 25×25 직사각형 지원 손실, 서로 공유되는
   token/context, Canny 중앙점과 실제 후보 경로의 차이를 각각 다룬다. 경로가 없으면
   가까운 경계에 맞춰 새 truth를 만들지 않는다.
3. 아래쪽 Foam 근거와 위쪽의 물리적 역할을 구분한다. 양쪽 모두 Foam인 미세/큰
   알갱이 전환과 실제 상단을 구별할 근거를 명시한다. 단순 유사도 차이·부호·두 기준의
   동의는 그 근거가 아니며, 기존 실패 연산의 crop/scale/reference/cutoff 재시도를
   이름만 바꿔 새 설계로 제시하지 않는다.
4. 입력·역할 증거가 충분한 한 가지 방법을 정한 뒤에만 비교 자료, 반대 사례, 결측,
   자원·중단 조건을 고정한다. wrong output 억제와 실제 관측 손실을 함께 평가한다.
   필요한 새 물리 판단은 원본 이미지로만 요청하고 이미 닫힌 질문은 반복하지 않는다.
5. 유효성이 확인되면 해당 수용 계약을 거쳐 Foam raw-front 경로를 연결한다.
   올바른 raw가 downstream에서 사라질 때만 episode 수정으로 간다. typed consumer는
   O2/V5/O3 조건을 지킨다. Oil의 42·44초 잘못된 report 극값과 실제 움직임 손실은
   별도 개선 의무로 남으며, 최종 Windows 9개 canonical 구간·report 이해도 검증을 유지한다.

설계·수용 조건은 [CR1/Foam 관측 설계](../../20-architecture/s11-contextual-role-observation-design.md#frozen-material-side-operation)와
[Witness Validation](../../30-validation/s11-interface-observability-witness-validation.md#post-cr1-operating-policy-and-consumer-acceptance)이 소유한다.
이번 인계 때문에 Windows 실행, 재학습·새 모델 탐색 또는 생산 연결이 승인되는 것은 아니다.
기존 커밋·푸시 자율 권한은 유지하며, 추가 촬영 불가와 sample3 분석 제한도 재질문하지 않는다.

## 저장 위치와 재현 경계

Git에는 [고정 preflight](../../50-diagnostics/s11/2026-10-13-foam-material-sides/preflight.json),
[전체 압축 점수](../../50-diagnostics/s11/2026-10-13-foam-material-sides/readout.json.gz),
[검증 요약](../../50-diagnostics/s11/2026-10-13-foam-material-sides/verification.json),
R/L 원문 답변·표시 이미지와 [실행기](../../../tests/diagnostics/s11_foam_material_sides.py)가 있다.
추론 전 고정 HEAD는 `48cf500f44893c7ef39253f1a05bc6bc59ed53a9`, 결과 커밋은
`acf1ae122164435d8370579ae608174197fc6930`이다.

- preflight SHA-256: `d414111b9afc891c0e290b4bd0d73a4702fc1abbde26c242a27082e09352730f`
- 압축 점수 SHA-256: `be7b5d9bbe120a2977dce32070e505372c1e2f4d1589a6e6cabbd6ab3b8a22d1`
- 검증 요약 SHA-256: `86347739ba0518f0970578e3352a270b8eec6b7eb8da93c33d804cc749e224a8`

preflight의 142개 핀 중 **124개 입력은 Git 밖의 로컬 파일**이며 실제 경로와 hash는
preflight를 그대로 따른다. A1 RGB, 기존 default 캡처, edge/public-path raster,
water support와 공개 원본의 선택 프레임이 해당한다. 이 호스트에는 모두 있고 hash가
일치하지만, 새 clone만으로는 전체 재현 입력이 준비되지 않는다. 누락을 새 decode나
그레이스케일 복제로 조용히 대체하지 않는다. 과거 폐기 범위는
[기존 retention owner](2026-10-12-pre-cr1-cleanup-checkpoint.md)를 유지한다.

단일 CR1 환경·모델·cache는 `sample/output/s11-cr1-workspace/{env,models,cache}`에
남는다. workspace 전체 할당량은 이번 확인 시 **746,438,656 bytes**, 기존 한도는
3 GB다. 현재 자동 재추론 작업은 없으며, 명시적 환경 정리 요청 전까지 유지한다.
관리 실행 14개는 모두 닫혔고, 이번 준비·실행·이미지 검토의 임시 폴더는 제거됐다.
이 인계를 위해 새 archive, 환경 사본, 영상 ZIP 또는 worktree를 만들지 않았다.

동일 호스트에서 입력 변경이 의심될 때만 다음 읽기 전용 검사를 재사용할 수 있다.
이는 닫힌 모델 실험의 재실행 명령이 아니다.

```bash
.venv/bin/python tests/diagnostics/s11_foam_material_sides.py --manifest docs/50-diagnostics/s11/2026-10-13-foam-material-sides/preflight.json --validate-only
.venv/bin/python scripts/experiment_artifacts.py check
```

스마트폰 검토에서 HTML과 도구 출력 이미지는 보이지 않은 적이 있다. 필요한 새
판단 이미지는 기존 PNG를 최종 답변에 직접 표시하고 원본 해상도 한계를 유지한다.
R/L 이미지를 다시 보여 달라는 요청은 새로운 물리 판단이나 자동 승인이 아니다.

## 재개용 메시지

```text
oil_level_tracker에서 이어서 진행해줘. AGENTS.md와
docs/00-project/work-plan.md,
docs/60-evidence/s11/2026-10-13-material-role-handoff.md를 먼저 확인해줘.
d23f0a5까지 R/L 내부 기준 승인과 고정 양측 비교를 마쳤고 제품 적용은 하지 않았어.
다음은 기존 native path/support를 재사용해 실제 상단을 잃지 않고 내부 appearance
전환과 구분할 새 관측 설계안 하나를 구체화하는 단계야. 새 검출법은 아직 미선정이야.
닫힌 실험의 crop/scale/reference/cutoff를 바꿔 재시도하거나 닫힌 사용자 판정을
다시 묻지 말고, 변경으로 무효화되지 않은 기존 검증을 재사용해줘.
커밋·푸시는 자율적으로 진행하고, 내 새 판단이나 Windows 작업이 필요한 때 알려줘.
```

## Detector Governance

- Logic-map nodes: `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `OIL-AUTHORITY`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: the completed material-side record identifies required-support loss before its own scoring; it does not change the established raw-front/episode distinction or establish a new Windows first cause. The handoff adds no new detector experiment.
- Logic-map impact: NONE — this requested checkpoint routes verified inputs, closed judgments and the next design deliverable without changing runtime owners or production behavior.
- Failure-registry impact: NONE — existing failure limits and closed experiments are preserved; no new mechanism or field acceptance is asserted.
