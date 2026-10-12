# S11 전체 검토 명세 인수와 후속 계획 — 2026-10-12

**기준:** clean `main`, fetch 후 `origin/main` 모두
`2c2ddd20b3dfe0eddcbc8d747b01e766522536a1`.
**범위:** 첨부·관련 native 산출물·워크트리 확인, 원본 보존과 중복 정리,
명세 타당성 검토, 후속 계획. Production 구현이나 모델 실행은 포함하지 않는다.
**결론:** 역할 관측 계층의 부분 재설계는 근거가 있다. CR-1은 다음 연구
후보로 계획에 반영하되, 바로 실행 가능한 완성 명세로 보지는 않는다.
기존 ML 제외 범위와 충돌하므로 사용자 범위 결정이 먼저 필요하며,
참조의 물리적 바인딩, token 해상도, 비교 실험과 평가 분리를 고정해야 한다.
O2 OPEN / FIELD FAIL / Local XY OFF는 유지한다.

## 보존·워크트리·중복 처리

| 자료 | 처리와 재현 경로 |
|---|---|
| ZIP의 10파일 | [원본 안내](../../70-reference/s11-program-review-2026-10-12/README.md)와 [명세](../../70-reference/s11-program-review-2026-10-12/S11-program-review-and-work-spec-2026-10-12.md)를 포함해 파일명/bytes 그대로 보존. 제공 checksum의 payload 9/9 일치 |
| 로컬 감사 7파일 | [import manifest](../../70-reference/s11-program-review-2026-10-12/import-manifest.json)가 전부 매핑. 고유 5파일은 `native-evidence/`, 동일 script/log 2파일은 첨부 bytes 재사용 |
| 초기/최종 peer JSON | 계산 결과는 같지만 metadata/bytes가 달라 둘 다 보존. 초기 파일을 최종 실행의 완전한 provenance로 바꾸지 않음 |
| 이번 검증 | [verification.json](2026-10-12-program-review-intake/verification.json), [fresh pytest JUnit](2026-10-12-program-review-intake/focused-tests.xml). 새 peer JSON은 보존된 최종 JSON과 byte-identical이므로 중복 저장하지 않음 |
| Git/worktree | Git 등록 워크트리는 현재 checkout 하나. 이 채팅 attachment는 없음. Codex managed-worktree root도 확인했으며 남아 있는 checkout은 다른 프로젝트 `may_web`; 병합·삭제 대상이 아님 |
| 정리 범위 | 매핑/해시 검증 후 `sample/output/s11-program-review-20261012-001/`의 7사본 제거. 입력인 sample4 raw/completed/summary와 다른 연구·영상은 보존. 역사적 branch를 중복 worktree로 간주해 삭제하지 않음 |

별도 Oil worktree나 이 작업에 병합할 미커밋 변경이 없어 source merge는
필요하지 않았다. 사용자 전달 ZIP은 원래 첨부 위치에 유지한다. 원본의 옛
절대경로/실행 지시는 감사 당시 provenance이며, 위 manifest가 현재 보관
경로와 이전 경로 복원 방법을 제공한다. 연구 script는 production/test
자동 수집 경로로 옮기지 않았다.

## 직접 확인한 결과

첨부 checker와 synthetic story test를 검토 후 실행했다. Integrity PASS와
16개 PASS는 내부 일관성 확인이며 detector/보고서 정답 판정이 아니다.
명세에 적힌 동일 5개 pytest 파일도 현재 checkout에서 새로 실행해
**124 passed**를 확인했다. 첨부의 과거 124개와 합산하지 않는다.

원본 `peer_probe.py`를 수정 없이 새 임시 출력 경로에서 실행했다.
sample4 113프레임 + public 3프레임에서 Oil 후보 **2,618개 연결**,
저장된 support **1,892개 일치 / mismatch 0**를 확인했다. 나머지 726개는
저장 support 필드가 없는 후보이며 별도 PASS 분모로 넣지 않는다.
상세 per-peer rows는 고정 sample4 프레임 241개와 public 69개, 총 310개다.
생산 코드 221개 hash와 public archive의 95개 logical file도 검증됐다.
재실행 결과는 보존된 [최종 native JSON](../../70-reference/s11-program-review-2026-10-12/native-evidence/peer-probe-verified.json)과 bytes까지 같다.

문서 링크/anchor와 governance는 통과했다. 전체 staged whitespace 검사에는
첨부 원문의 의도된 Markdown 줄바꿈 공백 4곳만 남으며, 원본 hash 보존을
위해 수정하지 않았다. 그 원본을 제외한 변경은 whitespace 검사도 통과했다.

이는 현재 support 함수를 동일 입력에 재적용한 재현성이다. 독립 수식 구현,
새 영상 replay, 모든 후보의 물리적 역할 인증 또는 모델 성능 검증은 아니다.

- Public Y288은 Y277 peer의 최대 기여 `0.2650188025`로 지지된다.
  실제 코드는 합산 투표가 아닌 max이므로 복제 후보의 표 누적 버그라는
  해석은 부적절하다. 검토 Oil 범위의 4후보 support는 모두 0이다.
- Sample4의 잘못된 44초와 보호할 42.5/52초 선택은 모두 continuation이며
  support가 0이다. Anchor-only 수정이나 support=0 일괄 veto는 충분하지 않다.
- Foam f1620은 올바른 upper가 episode 입력에서 소실된 사례가 아니다.
  기존 source-qualified raw-front 문제와 이후 episode 문제를 분리해야 한다.

## 명세 타당성과 보완

| 항목 | 판단과 반영 |
|---|---|
| Geometry / Role / Temporal identity 분리 | 채택할 설계 방향. 현재 provenance·owner·report를 재사용하며 역할 근거의 anchor/continuation 소비를 분리 검증 |
| DINOv2 CR-1 | 제한된 offline 연구 후보로 타당하나 미검증. 현 Work Plan은 learned 방법을 제외하므로 사용자에게 범위 변경을 질의. 명세 전달만으로 변경을 추정하지 않음; 허용되면 WP1에서 backend/실행 계약 확정 |
| 참조와 평가 | 지역 라벨을 exact contour로 만들지 않음. Query/인접 episode의 reference 유입, 동일 source 노출, reference 자기 재현을 분리. 확보되지 않은 holdout을 있다고 기록하지 않음 |
| Token 해상도 | 14 px patch의 source 환산 support와 상·하측/후보 간 겹침을 계측해야 함. Feature interpolation은 native 경계 관측을 새로 만들지 않음 |
| Full/local ablation | Local crop 확대는 해상도까지 바꾸므로 문맥 효과만 입증하지 못함. 같은 scale/lattice/support에서 한 개 intervention을 고정하고 padding 영향도 공개 |
| Synthetic reachability | 임의 feature vector와 bool로 된 synthetic 계약은 필요조건 일부만 확인. 기존 validation대로 실제 encoder→strip 연산을 통과한 입력과 대표 real positive/opposition 검사가 필요 |
| Foam WP3 | P5-a 관측 연구와 P5-b behavior 통합을 분리. 독립 raw-front 연구는 Oil 연구에 종속되지 않으며 typed 소비 시 O2/O3 필요. WP8은 조건부 |
| A/B/C/U 및 Windows 표 | 기존 story 계약과 부합하는 제안 worksheet. canonical truth, 9구간, 실제 독립 report 검토, 사전 residual budget을 대체하지 않음. 16개 synthetic test는 자동 물리 evaluator가 아님 |
| 4–6 engineer-day | 계획 가정이며 납기·성능 약속으로 채택하지 않음. 한 encoder/bank·두 표현의 고정 실험 한도를 유지 |

[DINOv2 공식 모델 카드](https://github.com/facebookresearch/dinov2/blob/main/MODEL_CARD.md)와
[공식 저장소](https://github.com/facebookresearch/dinov2)를 확인했다.
제안 backend는 patch feature 사용 근거가 있지만 압축기 역할 판별이나 CPU
처리 비용은 여기서 도출되지 않는다. [의료 용기 연구](https://arxiv.org/abs/2105.01456)와
[투명 액체 segmentation 연구](https://arxiv.org/abs/2203.01538)는 서로 다른
데이터/학습 문제를 다루므로 그대로 적용 가능한 성능 증거로 사용하지 않는다.

## 이후 실행 경로

실행 순서와 상태는 [Work Plan](../../00-project/work-plan.md#direction-decision-and-staged-follow-up)
한 곳에서 관리한다. WP0은 이번에 재현했다. 다음 분기는 기존 learned 방법
제외를 재개방할지 결정하는 것이며, 허용 시 WP1 preflight가 이어진다.
제외를 유지하면 CR-1은 보류하고 P2/P5-a의 별도 관측 설계 조건을 유지한다.
WP2 CR-1과 WP3 Foam 관측은 역할별로 독립 평가한다. 유효한 결과만
WP4 typed shadow → WP5 V5 Windows/O2 → WP6 O3 → WP7 O4로 이어진다.
WP8 Foam episode는 진입 근거가 있을 때만, WP9 통합 field/report와 WP10
disposition은 그 이후다. 이번에는 모델/Windows 실행을 요청하지 않는다.

세부 보완은 [bounded CR-1 design](../../20-architecture/s11-contextual-role-observation-design.md),
승인 조건은 [기존 validation의 추가 절](../../30-validation/s11-interface-observability-witness-validation.md#contextual-role-experiment-preflight)에
반영했다. 별도 상태 원장, 새로운 제품 수치 budget, 기존 실패의 소급 PASS는 없다.
Closed source 질문과 Local XY/row-distribution/mean/cost-order/S1–S3 종료는 유지한다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: public reviewed frame retains lower-region geometry but supplies cross-family support to an upper non-target anchor; sample4 wrong 44 s selection is continuation. Exact earlier physical identity loss remains unproven. Foam reviewed upper is lost before correct raw-front admission, so this does not establish episode causality.
- Logic-map impact: NONE — supplied-source preservation, current-function recomputation and future design/validation qualifications do not change executing owners.
- Failure-registry impact: NONE — findings refine known role/support/continuation and Foam-reduction failures; no production fix or new field acceptance is claimed.
