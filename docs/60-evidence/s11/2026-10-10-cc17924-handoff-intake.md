# cc17924 detector handoff — intake and design review

**검토일:** 2026-10-10. **시작 기준:** clean `main` /
`cc179244c89ea59bd097fa165ea493942629e23e`.
요청 범위는 첨부 전체 확인·배치, 명세 타당성 검토와 후속 계획이다.
첨부 안의 다음 작업 착수 메시지는 인용된 제안이며 이번 intake에서 실행하지 않았다.

**판정: CBR-1은 제한된 후속 실험 방향으로 타당하다. 다만 구현 전 대응·지원집합·자원·판정
규칙을 확정해야 하며, 성능이 입증된 detector 설계로 채택하지 않는다.**
H0/G1 비채택, 고정 Glass-center 측정, 독립 Oil/Foam, 기존 report 재사용은 유지한다.
R22 behavior + R22-3/O1 diagnostics, Local XY OFF, O2 OPEN / FIELD FAIL은 그대로다.
현재 순서는 [Work Plan](../../00-project/work-plan.md#cbr-1-next-work-after-the-cc17924-intake)이 소유한다.

## 보존 위치와 권한

| 자료 | 배치와 확인 범위 |
|---|---|
| 첨부 ZIP의 6개 파일 | [원본 패키지](../../70-reference/s11-detector-handoff-cc17924-2026-10-09/README.md)에 모두 byte-for-byte 보존. README, 명세서, 실행 요약, helper, delivery-validation, SHA256SUMS 원문을 수정하지 않았다. |
| 원 실험의 텍스트·스크립트·그림 21개 | 패키지의 `native-evidence/`에 원본과 구분해 복사. 4개 Python runner, 8개 JSON, log/txt 각 1개, 그림 7개다. runtime/test discovery에 등록하지 않았다. |
| 원 실험의 배열 198개 | 원래 `sample/output/s11-design-audit-cc17924-20261009-001/partition-trial/` 유지. 아래 로컬 archive에도 포함된다. |
| 전체 원 실험 보존 | `sample/output/s11-handoff-intake-cc17924-20261010-001/native-evidence.zip`: 캐시를 제외한 **219개 / 원문 6,154,685 bytes**, 모든 member hash와 CRC 확인. 첨부 ZIP도 같은 디렉터리에 보존했다. |
| 이번 검토의 증거 | [검증 receipt](2026-10-10-cc17924-handoff-intake.json)에 220개 로컬 파일 목록·hash, 검증 범위와 사용한 일회성 검사 코드 원문을 기록. [import manifest](../../70-reference/s11-detector-handoff-cc17924-2026-10-09/import-manifest.json)는 원문/복사본/로컬 archive를 연결한다. |

로컬 archive는 Git ignored이며 외부 백업이 아니다. 새 clone에는 native 배열과 원본 영상이
없다. 이 archive도 모든 upstream 입력이나 영상을 포함한 독립 재현 패키지는 아니다.
원래 파일·경로는 이동하거나 삭제하지 않았다. `.pyc` 1개는 hash만 목록화하고 캐시로 제외했다.
이전 handoff·truth·실험 문서는 당시의 증거로 유지한다.
Native `focused-tests.log` 복사본은 저장소의 `*.log` ignore 규칙 때문에
`focused-tests.log.txt`라는 이름으로 보존했다. 내용 bytes는 동일하고 manifest가 원래 경로를 기록한다.

## 이번에 직접 확인한 것

- 원본 **6/6개**를 읽고, ZIP CRC와 SHA256SUMS의 **5/5개** 선언 hash를 확인했다.
  checksum 파일 자체까지 포함한 6개 hash를 import manifest에 별도로 기록했다.
- 첨부 `verify_local_evidence.py`를 읽은 뒤 실행했다. **14개 native artifact + 367개 input
  pins = 381개 경로** 일치, 누락·불일치 0, 현재 HEAD 일치다.
- 이전 fixed-center checkpoint의 **415개 pins**를 별도로 확인했다. 이 안에는 production
  Python **221개**가 포함된다. G1 preflight **200개 pins**와 영상/Recipe **8개 pins**도 일치한다.
  이 집합들은 겹치므로 합산해 고유 증거 수로 부르지 않는다. 381과 415는 서로 다른 검사 범위다.
- 원 실험 디렉터리 **220개 / 6,172,910 bytes**를 inventory했다. 캐시 외 모든 파일의 형식을
  확인했고, 198개 NPZ의 모든 배열을 `allow_pickle=False`로 읽어 타입·shape·유한값·저장
  label/distance 관계와 입력 crop/mask 동일성을 대조했다. JSON은 파싱하고 Python은 AST를
  확인했다. 7개 PNG 모두 파일 검증과 육안 검토를 수행했다.
- H0의 **198개** 저장 중앙 결정을 기존 oriented face에서 재계산하고, G1의 **198개** 결정을
  저장 label raster의 중앙 상하 pixel 쌍에서 직접 열거했다. 후보 목록·좌표·초기 프레임 표시·
  비공식 출력과 continuation 집계가 일치했다. 아래 수치는 동일 입력을 재사용한 결과다.
- 첨부가 인용한 현재 코드 owner, fixed-center 계약과 canonical Windows truth의 **9개 segment**를
  대조했다. 구간 ID·대략적 전이·Oil/Foam 해석에서 충돌을 찾지 못했다.

**이번에 다시 실행하지 않은 것:** H0 분할 알고리즘, detector, 영상 decode, pytest,
Windows 작업 및 신규 물리적 truth 작성. 기록된 **84 pytest passes**, 9개 구성 검증 그룹
(그중 32개 작은 graph oracle 사례), delivery helper의 6개 구성 검증, 18개 decode는
당시 실행 결과다. 이번 hash·저장 배열 검증을 그 테스트들의 새 실행이나 field PASS로 세지 않는다.

| 계획 | 초기 제외 continuation | H0 단일 후보 | G1 단일 후보 | G1 최장 연속 native frame |
|---|---:|---:|---:|---:|
| Oil | 75 | 3 | 15 | 4 |
| Foam | 90 | 21 | 50 | 10 |
| Rim opposition | 30 | 0 | 0 | 0 |

고유 raster는 **167개**, plan/frame query는 **198개**, 초기 query 3개를 제외한 분모는
**195개**다. 이는 후보 가용성이고 정확도·recall·successful abstention이 아니다.
Rim의 한 점과 양성 참조 21/22점은 정보량이 맞는 대조군이 아니므로 0 false positives를 입증하지 않는다.

G1은 기존 brightness-support face와 맞아야 한다는 제약이 geometry 손실을 추가한다는
해석을 지지한다. 그러나 [f1348 검토 그림](../../70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/oil-late-ablation-review.png)의
중앙 표시가 밝은 영역 내부에 놓인다는 agent 관찰은 여전히 역할 혼동의 의심 근거다.
사용자 exact point truth로 승격하지 않으며, 45 s 오른쪽 LK 군집에 관한 기존 사용자 답변을
번복하지 않는다. H0/G1을 retune하거나 production으로 승격할 근거는 없다.

## 명세 타당성과 필요한 보완

| 판단 | 검토 결과와 후속 조건 |
|---|---|
| 방향은 타당 | 과거 점을 이동시킨 위치에서 seed를 만들던 H0와 달리, 현재 관측 경계를 먼저 정하고 그 위치에서 역할 근거를 측정한다. 앞단 geometry/identity 문제를 phase·episode 완화로 덮지 않는 순서가 기존 소유 구조와 맞는다. |
| 새 물리 정보가 입증된 것은 아님 | A/B BGR L1은 여전히 appearance 비교다. 측정 위치를 바꾸는 것은 의미 있는 연산 변경이지만, 구조물·복제 texture·optical warp를 구별하는 독립 증거 자체는 아니다. strict minimum만으로 physical authority를 주지 않는다. |
| 현재 geometry 생성 규칙이 덜 정해짐 | `measure_boundary_faces`는 **주어진 label**의 경계를 열거할 뿐 label을 생성하지 않는다. 이를 단독 detector처럼 사용할 수 없다. 기존 `measure_edge_fragments`와 face 입력의 역할을 구분하고, Oil이 옛 Foam/H0 mask에 종속되지 않도록 실제 후보 입력을 고정해야 한다. |
| 참조 대응 규칙이 빠짐 | 수식의 공통집합 S는 현재 fragment와 초기 reference의 pixel 대응을 전제한다. 곡률·분기·누락·위아래 방향·혼합 참조·서로 다른 X에서 어떤 pixel을 비교하는지 명세만으로 유일하게 정해지지 않는다. 대략적 초기 점을 pure material mask나 완성된 대응으로 간주하지 않는다. |
| 비교·자원 계약 보완 필요 | explanation마다 같은 S/가중치를 쓰고 missing opposition을 분리해야 한다. stencil, normalization, tie 계산, 후보·sample·연산·출력 예산과 초과 처리를 사전 고정한다. helper별 한계만으로 전체 후보×참조 계산량이 제한되지는 않는다. |
| 실험 진전 기준을 고정해야 함 | P0/P1/P2 rubric은 합리적이지만 “유의미한 개선”만으로 실행 결정을 재현할 수 없다. 기존 판단이 가능한 사건·구간, wrong/missing-run 분모, 개선/비회귀·NOT_ASSESSABLE 조건을 결과 전에 정한다. 새 보편 시간·오차 threshold는 만들지 않는다. |
| 자료·cadence 한계 유지 | 167개 raster/198개 query는 sample4의 인접·재사용 개발 자료다. 4개 Mac 회귀와 public 3종을 더해도 새 holdout은 생기지 않는다. native-rate 결과를 실제 analysis cadence의 성능으로 환산하지 않고, 기존 scalar truth를 새 center-Y MAE로 바로 쓰지 않는다. |

기존 구현 탐색에서 reference 비교는
[`s11_boundary_temporal_probe.py`](../../../tests/diagnostics/s11_boundary_temporal_probe.py),
현재 edge fragment는
[`s11_contour_contact_probe.py`](../../../tests/diagnostics/s11_contour_contact_probe.py),
face는 [`s11_foam_support_geometry.py`](../../../tests/diagnostics/s11_foam_support_geometry.py),
높이 변환은 [`geometry.py`](../../../src/oil_tracker/domain/geometry.py)가 이미 소유한다.
CBR-1 책임은 이 offline probe의 좁은 확장으로 계획한다. 기존 patch/constellation 함수는
전체 appearance 이동을 찾는 연산이므로 현재 후보에 결박된 역할 비교를 그대로 제공하지 않는다.
새 segmentation/tracking framework나 production 진입점은 필요하지 않다.

첨부 P01의 [OpenCV watershed 문서](https://docs.opencv.org/4.13.0/d3/db4/tutorial_py_watershed.html)도
확인했다. 지정한 marker/unknown의 역할을 설명하는 참고 자료이며 Oil/Foam 의미나 이 실험의
효과를 입증하지 않는다. H0는 실제로 자체 minimax graph 연산을 사용한다.

## 채택 범위와 다음 작업

위 보완을 [Witness Architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#cbr-1-current-boundary-reference-comparison--proposed-offline-contract)와
[Witness Validation](../../30-validation/s11-interface-observability-witness-validation.md#cbr-1-offline-comparison-entry)에 반영했다.
명세 원문을 현행 계약으로 덮어쓰거나 두 번째 진행 원장을 만들지 않았다.

다음 작업은 **CBR-1 preflight → D2-A/D2-B 측정 구현·구성 검증 → 전체 고정 query 비교**다.
유용한 근거가 있으면 4개 Mac 회귀와 별도 D5 Foam 검증으로 넓힌다. 그 뒤에야 O2의 실제
holdout/운영점/Windows shadow, 별도 O3/O4 통합, D6의 9구간 field qualification을 검토한다.
구체적인 순서·진전 조건은 Work Plan 한 곳에 유지한다. 현재 사용자 판단이나 Windows 실행을
추가로 요청할 이유는 없다. 구현 성과·신규 scalar truth·O2/field 통과는 아직 없다.

## 보존된 helper 사용 범위

저장소 루트에서 아래 원본 helper는 기존 로컬 파일 identity만 검사한다.

```bash
.venv/bin/python docs/70-reference/s11-detector-handoff-cc17924-2026-10-09/verify_local_evidence.py \
  --repo-root .
```

기준 HEAD가 바뀌면 원본 helper의 `INCOMPLETE_OR_DIFFERENT_HEAD`는 정상적인 역사적 범위
표시다. HEAD 일치만으로 dirty source까지 모두 검증하는 도구도 아니다. 이번에는 별도
production pins를 확인했다. `native-evidence/verify_probe.py`와 ablation/visual runner는
원래 출력에 쓰는 top-level 코드가 있으므로 보관 복사본을 실행하지 않는다. 이번 검증은
원 실험 기록을 덮어쓰지 않는 별도 read-only 계산으로 수행했다.

## 저장소 반영 검증

변경된 Markdown의 로컬 링크/anchor 743개에서 누락이 없고, 새 파일 30개는 날짜 색인에
Git 미등록으로 표시했다. 원본 6개와 native 복사본 21개의 bytes, 원래 로컬 파일 220개와
보존 archive의 hash를 최종 대조했다. S11 governance(`--base-ref cc17924 --include-worktree`)와
`git diff --check`가 통과했다. 변경은 `docs/` 안에 한정되며 production/test source, Recipe,
truth, roadmap의 milestone 상태를 바꾸지 않았다. 커밋·푸시는 수행하지 않았다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PROPOSAL`, `OIL-CANDIDATE`, `FOAM-CANDIDATE`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: saved H0 support-face filtering adds a verified geometry-stage loss relative to G1; reference/side identity remains unresolved, with agent-observed suspected wrong-region output at f1348. No new production/Windows first physical cause or dense truth is established.
- Logic-map impact: NONE — original evidence preservation, saved-array verification and a proposed offline contract change no executing detector owner, candidate authority or publication route.
- Failure-registry impact: NONE — representation starvation, appearance identity leakage, cross-series coupling and provenance/tuning guards already cover the observed limitations; H0/G1 stay unpromoted and field disposition is unchanged.
