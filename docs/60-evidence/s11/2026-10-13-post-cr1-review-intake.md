# Post-CR1 명세 인수·검증 및 계획 정리 — 2026-10-13

**결과:** 첨부 5개 파일을 원문 그대로 보존했고, 저장 결과 재현과 설계 타당성
검토를 완료했다. 고정 local 역할 경쟁과 절대 지지도를 함께 보는 정책을 **설계
가설**로 채택한다. 임계값·calibration 자료·독립 평가 자료는 정해지지 않았다.
인수 단계에서 생산 detector, Recipe, truth, 모델·환경은 변경하지 않았다.

시작점은 clean `main`, `0bc5af74dc0818a166fc99f7bbdf3b05cd7b65f1`로 첨부의
기준 HEAD와 같다. 유지되는 판정은 `S11 ACTIVE / FIELD FAIL / O2 OPEN /
Local XY OFF`다. FIELD FAIL은 기존 사용자 보고의 유지이며 새 Windows 결과가
아니다. 현재 상태와 다음 실행은 [Work Plan](../../00-project/work-plan.md)이 소유한다.

## 원본과 배치

- [원문 명세](../../70-reference/s11-post-cr1-review-2026-10-12/S11-program-review-and-work-spec-post-CR1-2026-10-12.md),
  README, 실행 요약 JSON, 재현 스크립트, SHA256SUMS를 `70-reference`에 보존했다.
  [Import manifest](../../70-reference/s11-post-cr1-review-2026-10-12/import-manifest.json)는
  ZIP과 다섯 member의 길이·SHA-256, 워크트리/브랜치 판단을 기록한다.
- 원본 checksum 4개가 모두 일치한다. 다섯 파일과 byte-identical인 기존 tracked
  문서는 없다. 전달 ZIP은 저장소에 다시 복제하지 않았다.
- 스크립트는 원문 provenance로 유지한다. 기존 `verify_followup.py`와 cadence
  helper를 사용하는 historical audit이며 새 evaluator나 제품 실행 경로가 아니다.
- 새로운 채택 계약은 기존 [CR-1 설계](../../20-architecture/s11-contextual-role-observation-design.md#post-cr1-operating-policy-proposal)와
  [Witness Validation](../../30-validation/s11-interface-observability-witness-validation.md#post-cr1-operating-policy-and-consumer-acceptance)에
  반영했다. 원문의 당시 clean/status/미실행 서술은 역사 기록으로 그대로 둔다.

## 이번에 독립 확인한 결과

원문 스크립트를 검토한 뒤 실제 standalone CLI를 **repository 밖 `/private/tmp`**에서
절대 경로와 `--root /Users/sunjaekim/Developer/oil_level_tracker --verify-video`로 실행했다.
Python은 기존 `.venv`를 사용했고 bytecode 생성을 껐다. 첨부 세션에서 NOT_RUN이던
standalone entry까지 이번에는 exit 0으로 확인했다. detector/encoder 재실행은 없다.

| 확인 | 이번 결과 | 한계 |
|---|---|---|
| 원 검증기 | PASS: 164 records, 135 measured variants, 270 score-rank checks, 167 support checks, 24 duplicate groups, 221 production sources unchanged | 저장 증거의 일관성; 물리적 효과 아님 |
| 원시 점수·후보 경쟁 | 네 예시의 local 점수/부호 margin, 두 모드의 범위, 7개 시점의 maxima와 known-target rank 일치 | 미검토 후보에 라벨을 이전하지 않음 |
| 분류 조합 | 41/37/32/28/17/9 집계와 9개 nonself 기록의 category 충돌 일치 | 그룹 순서는 표시 차이이므로 `(full, local)` 키로 비교 |
| 원본 영상 | sample4 11개 원본 ROI 및 공개 압축기 f1499 원본 PNG 일치 | 12개 고유 프레임; sample3 미디코드, 새 truth 없음 |
| 실제 report/CSV | tracking 113, 유효 Oil 수치 101, Foam 26, events 31; 42 s Y868/−18 px 및 44 s Y822/+28 px 극값 일치 | 관측 수치와 물리적 정답은 별개 |
| 수치 cadence | 100쌍 중 98쌍 ≤1 s; 42.5→44 s 1.5 s, 49.5→52 s 2.5 s | 물리적 동일 계면 cadence NOT_EVALUATED |
| 관련 테스트 | **109 passed in 24.29 s** | 전체 suite·새 detector 효과·Windows 검증 아님 |

테스트 명령은 저장소에서 다음과 같다. 첨부의 8.81 s는 이전 실행 시간이며,
위 24.29 s는 이번 실행의 pytest 보고 시간이다.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest \
  -q -p no:cacheprovider \
  tests/unit/test_s11_observation_cadence.py \
  tests/test_center_path_diagnostics.py \
  tests/unit/test_source_context_renderer.py
```

원문 실행 요약의 수치·입력 hash를 새 CLI 출력과 대조하고, 네 margin과 CSV 극값 Y는
기존 raw score/CSV에서 별도로 계산했다. 스크립트 SHA-256은
`b31773b892d0f5fddd3794051a207896016a986a96a86e779549a211eca09c8c`다.
새 CLI stdout은 18,129 bytes,
`33098bb0d18d2d9183ccb70589ed04da698730eaa450903103eeebfc114fc90c`였으며
기존 완전 score table/원문 요약과 이 검증 기록으로 대체해 임시 사본을 폐기했다.

실제 report graph, sample4 Foam 상단 범위 이미지와 공개 압축기 상·하단 범위 이미지도
확인했다. graph는 42/44 s를 주요 극값으로 강조한다. 기존 사용자 역할/범위 판단을
재사용했으며 새 후보 라벨이나 독립 report 이해도 판정을 만들지 않았다.

## 타당성 판단과 채택 범위

| 판단 | 반영 및 남은 조건 |
|---|---|
| 부분 재설계가 적절 | 현재 후보/계보·bounded owner·Oil/Foam 독립성·같은 프레임 publication을 유지하고 역할 관측→후보 채택 접점만 다룬다 |
| 연속 점수 활용은 합리적인 가설 | local 절대 유사도 0.442885 / 0.726906 / 0.820188과 texture 대조 0.727457을 재현했다. 작은 margin의 실제 후보도 있으므로 category-only, 절대 점수 단독, 큰 margin 조건 모두 충분하지 않다 |
| 현재 결과는 운영점의 검증이 아님 | 1개 원본/0 untouched holdout, 150 UNREVIEWED다. WP03은 실제 자료 적합성과 노출을 먼저 기록해야 한다. 재분할만으로 blind holdout을 만들 수 없다 |
| 최고 점수는 후보 선택 근거가 아님 | 49.5 s 미검토 Y841이 확인된 Y836보다 두 모드에서 높다. 기존 source 판단으로 해결할 수 있는지 먼저 보고 필요한 새 질문만 제한한다 |
| positive eligibility와 negative evidence 분리 | 낮은 점수·동률·결측은 unresolved다. `INTERNAL_OR_ARTIFACT`는 별도의 검증된 부정 증거가 필요하며 uncalibrated observation은 NOT_EVALUATED다 |
| Oil 소비 두 단계 분리 | 실제 `_cross_representation_support`는 `max`다. 현재 admission owner가 anchor/continuation을 함께 처리한다. 첫 O3 slice의 억제와 후속 양성 authority 회복을 별도 비교한다. support=0 일괄 차단은 채택하지 않는다 |
| Foam raw 표현 우선 | component-to-front 코드와 기존 causal joins에 부합한다. 상단 표현/역할→실제 pipeline→correct raw의 downstream 손실이 있을 때만 episode로 간다. Oil texture bank는 Foam-upper bank가 아니다 |
| 제품 결과와 부분 진전 분리 | P0 영향 기준, 9개 canonical Windows ID와 원래 시간 정밀도를 유지한다. 잘못된 극값과 중요한 움직임 소거를 함께 본다. 100% 프레임 정답·새 시간/픽셀 허용치를 추가하지 않는다 |

이번 원문에서 현재 source와 충돌하는 수치·핵심 원인 설명은 발견하지 못했다.
다만 실행 가능한 명세가 되려면 **tau 선택 방법, geometry/scale 적용 범위,
calibration/held-out source, 역할 정답 정밀도, 자원 상한과 허용 잔여 영향**을
결과 전에 확정해야 한다. 현재 자료에 숫자를 맞추거나 그 공백을 코드로 덮지 않는다.
같은 encoder/bank를 쓰더라도 qualified native role가 없으면 물리적 consumer는 미진입이다.

후속 WP01–WP10은 [단일 ledger](../../00-project/work-plan.md#s11-work-item-ledger)에
기존 O/W/P/D gate와 연결했다. WP02–03 preflight → WP04 shadow/O2/V5 →
WP05 역할 조건 → WP06 양성 채택/입증된 후속 손실 수리 순서다. WP07 Foam은 독립
역할/표현 경로이며 WP08은 조건부다. WP09의 9구간·독립 report 읽기와 WP10 종료
판정은 최종 단계다. 이번 인수로 모델 재추론·생산 구현·Windows 작업을 실행하지 않았다.

## 워크트리와 산출물 정리

`git worktree list --porcelain`에는 현재 main 하나만 있고 앱 attachment도 없다.
통상 Codex worktree 경로와 Developer의 관련 checkout에서도 추가 저장소를 찾지 못했다.
제거할 중복 worktree나 병합할 활성 sibling 변경은 없었다.

남은 S11 분기 중 `work/s11-context-validation-20261007`과
`work/s11-episode-texture-20261008`은 main에 포함됐다.
`work/s11-windows-first-detector-20261008`의 `c4814bd`와
`work/s11-spatial-identity-20261008`의 `e5d4a04`는 종료된 실패 실험/진단이다.
실제 diff와 closeout을 확인했고, 이미 채택된 D1 reader 책임은 main에 존재한다.
미채택 실험을 병합하지 않았으며 기존 commit 링크와 branch는 보존했다.
무관한 과거 기능/UI 브랜치도 이번 detector 계획의 병합·삭제 대상으로 삼지 않았다.

Work Plan은 **1,069→243줄**, **95,863→25,710 bytes**로 줄였다. 완료 경과를
기존 진단/증거·recall로 연결하고 현재 계획 하나로 통합했다. 이미 종료된 CR-1을
“reference scope 답변 대기/점수 미실행”으로 설명하던 stale 문구를 제거했다.
단계·기준선·실패 판정·권한·미해결 의무를 유지했고 사용 중인 앵커와 오래된 CBR-1
링크용 별칭도 보존했다. 원문 감사나 machine truth는 축약하지 않았다.

새 검증 출력은 managed run
`sample/output/s11-post-cr1-intake-20261013-001`에서만 만들었다.
보존 가치는 이번 독립 검증 결론·조건과 원본 매핑에 있으므로 이 기록/원문/기존
readout을 참조하고 임시 stdout·plan·selection만 정리했다. 전체 영상·보고서·모델·
캐시는 복제하거나 삭제하지 않았다. 과거 산출물의 보존/폐기는
[기존 retention owner](2026-10-12-pre-cr1-cleanup-checkpoint.md)가 계속 담당한다.
변경 Markdown의 local 링크 1,095개와 Work Plan 유입 앵커 25개, 원본 checksum,
governance와 whitespace 검사가 통과했다. 새 managed run은 중복 stdout 1개를
제거하며 닫혔고 전체 5개 managed run의 closeout 검사 오류는 0이다.
기록 자체는 field acceptance가 아니다.

## 추가 정리와 CR1 환경 판단

사용자의 불필요한 원본/워크트리 정리 요청으로 `2f0f7de57113b5907f4df08dd443190e25329b39`
기준의 로컬 보존 가치를 다시 심사했다. 워크트리는 여전히 main 하나이며, 제거할
추가 checkout은 없다. CR-1은 생산 미채택이지만 후속 정책 검증의 연구 후보로
남는다. 최종 채택/기각은 아직 결정되지 않았다.

| 제거 항목 | 파일 수 | 논리 bytes | 할당 bytes |
|---|---:|---:|---:|
| 이전 `dist/oil_level_tracker-R22-1-source.zip` 및 checksum | 2 | 1,889,436 | 1,896,448 |
| 격리 CR-1 `cache/uv` 설치용 metadata | 31 | 3,010,517 | 3,080,192 |
| 저장소 내 파생 Python bytecode | 6 | 53,297 | 69,632 |
| Finder `.DS_Store` | 5 | 51,220 | 65,536 |
| 합계 | **44** | **5,004,470** | **5,111,808** |

삭제 전에 모두 untracked이고 frozen 입력과 겹치지 않으며 환경에서 cache로
연결되는 symlink가 없음을 확인했다. 설치는 `--link-mode copy`로 완료돼 있다.
cache는 설치 metadata만 담고 있으며 inference·저장 점수 검증의 입력이 아니다.
필요한 후속 설치 시 다시 생성할 수 있다. bytecode/Finder metadata도 재생성 가능하다.

이전 배포 ZIP의 SHA-256은
`78cef4c209877c12c9b027347678304c865fdfffce3c679ef7d3dcceb17f47d7`이다.
651개 source member 전부가 main의 Git 이력과 byte-identical했다. 645개는
`e95ffce1652b94af9f60ba429bffe7eb09fc8849`, 나머지 6개 문서는
`f1eea44cf46c39bc00641bb34e615b8ddb31aba5`와
`52274e9c4539524612df367cea787718ffdb1a42`에서 확인했다. 현재 후보 배포나 비교의
입력이 아니므로 소스 이력과 기존 R22-1 측정 기록으로 대체했다. ZIP 고유의
`SOURCE_IDENTITY.json`과 압축 포장 bytes는 폐기했으며 동일 ZIP 재생성을 보장하지 않는다.

보존한 CR-1 환경·모델/source 한 벌은 이후 새 자료에서 고정 표현을 검증할 때
재사용한다. 지금 없애면 저장 점수 해석은 가능하지만 추론 재개 전에 lock·source·
weight hash에 맞는 환경 재구성이 필요하다. 준비 입력과 전체 score table은
현재 역할 정책의 분모·반례·좌표 연결을 보존하는 최소 증거다. 원본 영상, 앱 환경,
첨부 원문 5개와 완료된 실험 증거도 유지했다. 정책의 기각·교체 또는 로컬 추론
사용 종료 시 환경 보존을 재심사한다. 이번 정리로 새 추론이나 field 판정을 만들지 않았다.

정리 후 CR-1 workspace는 **743,616,512 할당 bytes**이며 cache는 비었다.
Torch 2.14.1 / NumPy 2.5.4 / Pillow 12.3.0 import와 기존 5개 managed run 검사가
통과했다. readiness pin 172개도 일치한다. 이 중 준비 파일 3개는 완료 marker가
기록한 `work/`→`evidence/` 이동을 따라 확인했다.

과거 검증기를 현재 checkout에서 그대로 실행하면 갱신된 설계/validation 문서
2개의 frozen hash와 충돌한다. 해당 문서만 기준 `0bc5af7`의 bytes로 임시 복원하고
현재 저장 증거·생산 소스를 참조한 검증에서는 **164 records / 270 score-rank checks /
221 production sources unchanged PASS**였다. 이 검증을 위해 현재 문서나 frozen
receipt를 덮어쓰지 않았고 임시 복원본은 즉시 제거했다. 이는 현재 문서를 과거 pin과 같다고 주장하는
검증이 아니다. 변경 문서 local 링크 81개, governance, whitespace 검사도 통과했다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: existing joins place sample4/public Foam upper loss at component-to-front reduction and public Oil false selection at anchor admission despite retained lower candidates. Saved-score verification identifies information lost by category-only interpretation, not a newly verified physical classifier or a private Windows first cause.
- Logic-map impact: NONE — source intake, planning compaction and proposal/acceptance clarification only; all 221 production Python sources remain unchanged and no new runtime schema/consumer is introduced.
- Failure-registry impact: NONE — existing authority, representation, coupling and provenance risks cover this evidence; no new failure mechanism, promoted repair or field result is asserted.
