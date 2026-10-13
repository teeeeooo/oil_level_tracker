# S11 전반 검토 명세 인수·타당성 검토 — 2026-10-13

**결과:** 첨부 6개 원본을 보존하고 실제 canary CLI와 저장 근거를 검증했다.
전체 detector 재작성 대신 native 경로·양측 역할·약한 판정의 결속을 다루는
**NSR-1 입력/readiness 설계**를 기존 owner에 채택했다. 제안된 7×7 역할 head는
데이터·학습 명세가 미완성이므로 연구 후보로 남긴다. 이번 작업은 문서 통합과
계획 수립이며 생산 구현이나 학습을 수행하지 않았다.

시작은 clean `main`, **`badf7caddebc7e75013ef02c888d2b72f13feb92`**였다.
실제 원격 main과 첨부 기준도 같았다. S11 ACTIVE / R22 behavior / R22-3·O1
diagnostics / O2 OPEN / FIELD FAIL / Local XY OFF를 유지한다. 현재 실행 상태는
[Work Plan](../../00-project/work-plan.md)이 소유하며, 이 기록은 새 field 결과가 아니다.

## 원본 배치와 권한

[원문 명세](../../70-reference/s11-program-review-2026-10-13/S11-program-review-and-work-spec-2026-10-13.md),
README, evidence audit JSON, 재현 스크립트, VERIFICATION.json, SHA256SUMS를
`docs/70-reference/s11-program-review-2026-10-13/`에 byte 그대로 보존했다.
[Import manifest](../../70-reference/s11-program-review-2026-10-13/import-manifest.json)는
ZIP hash·member 길이/hash·기존 중복 비교와 worktree 판단을 소유한다.

6개 합계는 **81,466 bytes**, 제공 checksum 5개가 모두 일치한다. 기존 tracked
파일 중 byte-identical인 원본은 없었다. 날짜가 비슷한 이전 review는 다른 기준과
판단을 기록하므로 중복으로 삭제하지 않는다. 원문 당시의 clean/미실행/권한 서술도
고치지 않는다. 이번 채택 내용은 다음 기존 owner에만 반영했다.

- 설계: [contextual-role supplement의 NSR/G0 계약](../../20-architecture/s11-contextual-role-observation-design.md#native-side-role-observation-and-g0-binding-contract).
- 수용: [Witness Validation의 G0/G1/G2 조건](../../30-validation/s11-interface-observability-witness-validation.md#native-side-role-readiness-and-feasibility).
- 실행 순서: [기존 WP01–WP10 ledger](../../00-project/work-plan.md#s11-work-item-ledger).

별도 live Work Plan이나 detector 버전을 만들지 않았다. 원문 Python은 pinned
historical reproduction helper이므로 `scripts/`나 제품·테스트 discovery로 옮기지
않았다. Git 이후 HEAD가 바뀌면 이 스크립트의 exact-head guard는 의도대로 멈춘다.
미래 실행을 위해 pin을 조용히 바꾸지 말고 해당 기준·입력·변경 범위를 먼저 확인한다.

## 이번에 실제 확인한 범위

문서 owner를 수정하기 전에 18개 근거 문서의 SHA-256과 줄 수를 첨부 audit와
대조했다. 모두 일치했다. 채택으로 바뀐 owner의 현재 hash가 원문과 다른 것은
정상이며, 원문 hash는 계속 `badf7ca`의 bytes를 가리킨다.

| 검사 | 독립 확인 결과 | 해석 범위 |
|---|---|---|
| Material-side preflight | 입력/source pin **142/142** 일치 | 새 모델 추론 없음 |
| 저장 default-run의 생산 source | **221/221** 일치 | 새 full replay나 모든 환경의 동일성 증명 아님 |
| 원본 sample4 / tracking CSV | 제공 SHA-256과 일치 | MP4는 hash만 읽었고 decode하지 않음 |
| 실제 CSV/events | **113행, Oil 101, Foam 26, events 31** | 숫자 제공률 89.38%는 정확도가 아님 |
| Oil extrema | 42 s / Y868 / MINIMUM, 44 s / Y822 / MAXIMUM | 원래 wrong-target 판정과 결속; 새 물리 판정 없음 |
| Foam 중단 | 마지막 수치 53 s, 54/55.5/56 s 수치 없음 | report의 기존 ‘거품 경계 관측 중단’ 문구 확인 |
| 저장 raw join | f1620/X595 범위812–816에 Canny Y813, 호환 raw 후보 0, 내부 Y833 축약 | 단일 Canny hit를 전체 경로 정답으로 승격하지 않음 |
| Native-feature canary | 전체 측정값과 배열 불변 결과가 첨부와 정확히 일치 | default settings의 의존성 시험; 개선 효과 NOT_EVALUATED |

저장 report graph를 직접 열어 42/44 s가 대표 극값으로 강조되는 것도 확인했다.
개발자의 시각 점검이며 독립 report 판독 시험은 아니다. Windows 9개 canonical
segment와 원문의 구간 ID/의미도 기존 reviewed-truth owner와 대조했다.

원문 CLI wrapper는 당시 syntax/help만 검사됐으므로 이번에는 **실제 entry**를
`/private/tmp` cwd에서 절대 경로로 실행했다. 기존 `.venv`를 사용했고 exit 0이었다.

```sh
cd /private/tmp
PYTHONDONTWRITEBYTECODE=1 /Users/sunjaekim/Developer/oil_level_tracker/.venv/bin/python \
  /Users/sunjaekim/Developer/oil_level_tracker/docs/70-reference/s11-program-review-2026-10-13/reproduce_native_feature_canary.py \
  --repo /Users/sunjaekim/Developer/oil_level_tracker \
  --output /Users/sunjaekim/Developer/oil_level_tracker/sample/output/s11-program-review-intake-20261013-001/work/canary.json
```

| Outside-mask fill | variance 변화 | edge density 변화 | texture 변화 | X595/Y813 변화 |
|---|---:|---:|---:|---|
| 0 | 1,581 | 100 | 430 | 세 값 모두 0 |
| 255 | 1,581 | 1,581 | 712 | 세 값 모두 0 |

visible 7,344 / masked 3,472픽셀, 변화 기준 `>1e-6`이다. 내부 입력과 원본 배열은
불변이다. 이번 측정 본체는 약 **0.0169 s**, import·전체 pipeline 비용은 제외한다.
원문 0.0623 s를 새 측정치로 재사용하지 않았다. AST와 `--help`도 정상이다.
생산 코드를 바꾸지 않았으므로 기존 focused test 9 passed는 **원문 실행 증거로
재사용**하며 이번에 다시 실행했다고 주장하지 않는다. 전체 regression, encoder,
학습, 전체 영상 replay, Windows, 독립 report 판독은 수행하지 않았다.

## 타당성 판단과 보완

| 명세 판단 | 검토 결론과 채택 조건 |
|---|---|
| 부분 재설계·raw-first | 현재 소스·lineage와 부합한다. Oil admission 두 경로와 Foam component-to-front를 구분하고 episode를 먼저 완화하지 않는다 |
| Native 경로 재사용 | 타당하나 component 경계 자체가 상단을 잃었을 수 있다. 기존 Canny fragment와 retained face의 reachability를 따로 기록해야 같은 손실을 선행 조건으로 반복하지 않는다 |
| 실제 receptive field | canary와 `_texture_evidence`의 필터 후 mask 적용이 뒷받침한다. 마스크 밖 입력이 합법적 문맥일 가능성 및 Y813 불변을 유지하므로 생산 버그로 판정하지 않는다 |
| 약한 판정의 재사용 | R/L은 region example, interval은 source constraint, B는 practical facet이다. 구간 내 edge가 하나뿐이어도 correspondence 없이 positive bag으로 바꾸지 않는다 |
| 7×7 head | 비용을 제한한 한 후보일 뿐 정보 충분성·학습 가능성 미입증. source별 학습 단위, 필요한 gas/liquid/opposition, 역할과 optical facet, 집계·loss·분할·운영점·자원이 아직 필요하다 |
| 순수 side 특징 | 7×7은 세 convolution의 이론적 범위다. preprocessing/padding/normalization/집계·head의 전체 의존성까지 확인해야 한다. 같은 쪽에 담겼다는 기하 조건도 물질 순도를 보증하지 않는다 |
| 네 가지 역할 | 투명 액체와 구조/광학 문맥이 같은 픽셀에 투영될 수 있다. 상호 배타적인 4-class softmax를 자동 채택하지 않고 역할·문맥 facet과 ambiguity 의미를 먼저 정의한다 |
| Interval loss 예시 | 분포 변수·정규화 범위·다중 경계·crop 상태가 미정이다. candidate recall 없이 적용하거나 새 좌표 회귀기로 확장하는 것은 이번 채택 범위가 아니다 |
| 효과 판정 | A/B/C/U, 실제 움직임 보존, 새 오선택·관측 손실을 함께 유지한다. all-unknown·reference self-match·분모 축소·반례 누락은 성공이 아니다 |

외부 방법론의 원문 abstract도 확인했다. [CCNN](https://arxiv.org/abs/1506.03648)은
출력 제약을 통한 약한 감독을, [ScribbleSup](https://arxiv.org/abs/1604.05144)는
sparse annotation을 통한 감독을 제시한다. [FCN](https://arxiv.org/abs/1605.06211)은
거친 의미와 세밀한 appearance 결합을 다룬다. **검토 판단:** 이 원리들은 제안의
가능성을 설명하지만 현재 압축기 데이터, 7×7 head, 역할 충분성이나 성능을 보증하지
않는다. benchmark 수치나 성공 가능성을 본 프로젝트로 전용하지 않았다.

따라서 이번 인수의 결론은 **방향과 G0 입력 계약 채택, 학습·classifier 효능 미수용**이다.
G0 구현에서는 모든 후보를 새로 라벨링하지 않고, 한 capability에 필요한 기존
판정의 실제 결속 가능성과 부족한 역할/반례를 명시한다. 다음 계획은 G0 → 별도
범위가 채택된 고정 G1 → WP04 shadow/V5 → 분리된 Oil 억제·positive 복구와 독립
Foam raw-front 변경 → 필요한 경우에만 episode → Windows/report·disposition이다.
O2/V5는 typed consumer의 gate이고, 독립 Foam 연구를 Oil 최종 결과에 종속시키지 않는다.

## 워크트리와 중복 정리

등록된 Git worktree는 main 하나, 이 작업의 앱 attachment는 0개였다. Codex managed
worktree 경로, Developer와 `/tmp`의 Git entry도 확인했으며 추가 Oil checkout은
없었다. Codex의 `may_web` checkout은 다른 프로젝트여서 유지했다.

두 미병합 S11 분기의 실제 local/remote head는 기존 intake 이후 변하지 않았다.
`work/s11-windows-first-detector-20261008` (`c4814bd`)와
`work/s11-spatial-identity-20261008` (`e5d4a04`)의 diff·마감 이력을 확인했다.
종료된 미승격 실험이며 채택된 saved-reader 책임은 main에 있다. 병합할 활성 sibling
변경이나 제거할 중복 worktree는 없었다. 이 고유 실패 이력과 무관한 기능/UI 분기는
유지했다. 이미 병합된 context/episode 이력도 재병합하지 않았다.

새 출력은 관리 run `sample/output/s11-program-review-intake-20261013-001` 아래에서만
생성했다. 새 canary JSON은 이미 원문 audit에 있는 전체 수치와 동일하므로 별도
영구 사본으로 남기지 않고, 원문·이 검증 기록을 `reuse`로 연결해 임시 출력을 정리했다.
전달 ZIP과 임시 압축 해제 원본도 저장소의 6개 원본과 byte 비교 후 제거했다.
ZIP의 압축 포장 bytes 재생성은 보장하지 않지만 모든 member의 bytes와 archive hash는
보존한다. 원본 영상·기존 보고서·CR1 환경/weights/cache·frozen 입력은 유지했다.
새 source snapshot, 영상 사본, 백업 ZIP, 모델 환경이나 worktree를 만들지 않았다.
과거 bulk 산출물의 폐기 범위는 [기존 retention owner](2026-10-12-pre-cr1-cleanup-checkpoint.md)를 따른다.

문서 검증은 변경 Markdown 9개의 local 링크 **1,195개**, 기존 Work Plan 유입 앵커
**26개**, 추가 파일 **8개**의 색인,
6개 원본 bytes, 기준 source/truth 보존, governance와 whitespace를 대상으로 했다.
종료된 관리 실행 **15개 / 오류 0**을 확인했다. 이 검증은 문서/보존 계약의 확인이며
생산 detector/Windows 수용을 의미하지 않는다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: the saved f1620 join locates upper loss at component-to-front reduction, not solely episode acceptance. The fresh native-feature canary measures dependency sensitivity only; production harm and physical role are NOT_EVALUATED and Y813 stays invariant. No new private Windows first cause is established.
- Logic-map impact: NONE — original intake, offline canary and G0 design/acceptance planning do not change executing owners, production code or schemas.
- Failure-registry impact: NONE — existing authority, representation, Foam and provenance entries cover the constraints; no new failure family or accepted repair is claimed.
