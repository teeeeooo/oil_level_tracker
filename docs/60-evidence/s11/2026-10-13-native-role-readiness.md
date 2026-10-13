# NSR-1 G0 — native 경로·약한 판정 결속과 준비도

**검증 범위:** 기준 `d1a8b714161cef908b771d549501d544c8ffe763`에서 G0 오프라인
결속 도구를 구현하고 저장 입력으로 실행했다. 기하·원본 판정 연결은 검증됐지만,
물리적 역할 관측의 G1 진입은 `NOT_READY`다. 생산 detector, 학습, 가중치,
새 encoder, 전체 영상 replay 및 Windows 실행은 변경·수행하지 않았다.
현재 진행과 사용자 입력 대기는 [Work Plan](../../00-project/work-plan.md)이 소유한다.

## 구현과 재현

[기존 설계](../../20-architecture/s11-contextual-role-observation-design.md#native-side-role-observation-and-g0-binding-contract)의
새 입력 envelope를 [native preflight](../../../tests/diagnostics/s11_native_role_preflight.py)가 담당한다.
기존 Canny fragment, retained-component face, CR1/O2 pin 검사와 A/B 정정 도구를
호출한다. 별도 edge 생성·경로 연결·후보 선택·물리 label 생성은 없다.

- [manifest](../../50-diagnostics/s11/2026-10-13-native-role-readiness/manifest.json): 원래 43개 context의 순서·source/frame/time·geometry, source bytes, review authority와 지원 범위.
- [전체 readout](../../50-diagnostics/s11/2026-10-13-native-role-readiness/readout.json.gz): 1,335개 edge와 incident fragment·양측 support, 164개 Oil 기록, 원래 구간/영역/후보 단위, 준비도 표.
- [verification](../../50-diagnostics/s11/2026-10-13-native-role-readiness/verification.json): 테스트·실제 실행 비용·전체 모집단 재검산.

```bash
# 저장소 밖 cwd에서도 동일하게 실행. 출력은 새 managed run의 work 안에 둔다.
<repo>/.venv/bin/python -B <repo>/tests/diagnostics/s11_native_role_preflight.py \
  --root <repo> \
  --manifest <repo>/docs/50-diagnostics/s11/2026-10-13-native-role-readiness/manifest.json \
  --output <managed-work>/readout.json.gz
```

[artifact lifecycle](../../40-operations/experiment-artifact-lifecycle.md)의 `start` 후
실행한다. 출력 경로가 있으면 거부한다. Manifest의 source pin은 이 실행 당시 bytes를
요구하므로 관련 도구 변경 후에는 옛 manifest를 고치지 말고 새 실행을 선언한다.

## 확인한 결과

| 항목 | 결과와 해석 |
|---|---|
| 모집단 | 43 contexts, 1,335 center edges, 164 Oil records 전부 유지 |
| 의존성 그룹 | 같은 영상·프레임은 31개 그룹. native/reduced/다른 capture view를 독립 표본으로 세지 않음 |
| 기존 R/L 가용성 | 1,184 available / 119 support 부족 / 32 saved RGB 없음 그대로 보존. 이 분모는 기존 비교의 것으로, 새 기하 관측을 막는 규칙이 아님 |
| 경로 결속 | 중심 edge에 접한 fragment view 3,047개. 2,115개는 X-monotone partial path, 932개는 vertical/cycle/turn 때문에 위·아래 경로 support를 구성하지 않음 |
| 경로 support | 54개 view만 선언한 양측 25×11 point support가 모두 관측됨. 이것은 기하 가용성이지 역할 정답률이 아님. 나머지 경로·픽셀을 채우거나 제거하지 않음 |
| component faces | 저장 label이 남은 11 contexts에서 결속. 나머지 32개는 `UNAVAILABLE_SAVED_LABELS`; 은퇴한 label raster를 재생성하거나 과거 component 결과와 현재 raw 결과를 같다고 놓지 않음 |
| Oil native path | 31개 `native_generator_path`, 122개 `no_captured_native_path`, 11개 control/부재. pooled sector와 pixel contour는 다른 표현으로 유지 |
| 판정 정밀도 | R/L은 각각 한 regional appearance 단위. 구간 6개와 guide 4개는 후보 label을 만들지 않음. Water B/C의 no-Foam은 원래 upper band 범위에만 결속 |
| f1485 A/B | A/B 물리 자격 미확정, B의 practical approximation 별도 보존. 기존 164개 historical label/score를 덮어쓰지 않음 |
| 후속 효능 | 새로운 물리 label 0, independent holdout 0. 성공/실패 detector 판정이나 FIELD PASS를 만들지 않음 |

### 기하 support와 특징 dependency

각 fragment의 실제 column별 픽셀과 원래 mask를 참조해 upper/lower 요청·관측·crop·mask·
missing-path 수를 재구성할 수 있다. 지점이나 경로가 짧으면 없는 column은 그대로
미관측이다. 같은 column에 여러 Y가 있거나 방향이 모호하면 면을 임의로 만들지 않는다.
Junction에 닿은 경로도 incident 상태를 유지한다. 위/아래는 기하학적 vertical side이며
물리적 법선·재질 순도 판정이 아니다.

선택한 leaf 관측은 **저장 RGB point identity**뿐이다. native RGB의 dependency는 해당
픽셀이고, reduced raster는 resize 문맥을 가진다. 실제 head나 재질 특징은 실행하지 않았다.
Canny의 CLAHE·blur·hysteresis 문맥, 기존 Foam texture의 reflected box filter와
Canny 의존, output mask 이전 연산을 별도 registry에 남겼다. 이 경로들을 pure-side
독립 증거로 세지 않는다. 새 head 전체 footprint는 아직 미정이다.

Alternative fragment view 간 실제 픽셀 재사용과 양측 교집합도 계산한다.
이 모집단의 alternative-view upper/lower 교집합 수는 0이었지만, 합성 offset-path
대조에서는 교집합 1과 각 side의 중복 7을 정확히 기록했다. 공유 source, 인접 view,
상위 특징 문맥이 독립 표본이나 독립 투표가 되는 것은 아니다.

### 상단 구간과 원시 경로의 관계

| 원래 구간 | 구간 안 Canny source Y | 현재 의미 |
|---|---|---|
| Sample4 f1620 Foam upper | 813 | 19-pixel fragment, 끝에 junction 있음. 구간 일치만으로 전체 경로 positive가 되지 않음 |
| Water A/f1232 Foam upper | 477 | 57-pixel fragment. 기존 upper containment와 native 경로 자격은 구분 |
| Water B/f1438 surface | 485, 488 | 두 edge; no-Foam upper-band 판정이 둘 중 하나를 정답으로 고르지 않음 |
| Water C/f1643 surface | 491 | 한 edge여도 자동 positive가 아님 |
| Public f1499 Foam upper | 332, 336 | 복수 native 대안과 junction 유지 |
| Public f1499 Oil upper | 428, 431, 433 | 복수 대안 유지; 한 appearance-component face의 위치 일치도 물리 label이 아님 |

저장 component face로는 앞의 다섯 구간에 visible hit가 없고, public Oil 구간에는
하나가 있다. Sample4는 해당 G0 label raster 자체가 없으므로 `0개 hit`를 component
손실의 새 증거로 쓰지 않는다. 기존 기본 실행의 component-to-front 손실 판정은
[원래 P5 증거](../../50-diagnostics/s11/2026-10-11-p5-default-linkage.md)가 소유한다.
내부 Foam guide 3개는 exact center-edge join이 없으며, 가까운 경로에 label을 옮기지 않았다.

## 준비도와 다음 판단

| 선언한 capability | G0 판정 | 남은 근거 |
|---|---|---|
| 저장 edge/path/support 결속 | READY | 선언한 기하 범위에서만 완료 |
| 저장 component-face 결속 | READY, 11 contexts로 제한 | 32개 capture 부재를 명시; 복원 의무나 물리 absence로 해석하지 않음 |
| 원래 약한 판정과 Oil lineage 결속 | READY | 원래 정밀도·A/B 정정 유지 |
| 외부 Foam 상단과 내부 변화의 구분 | NOT_READY | native path의 실제 역할과 양측 역할, 실제 internal opposition, optical/structure opposition |
| Oil 경계 역할 관측 | NOT_READY | native 역할·선택한 특징의 전체 dependency·별도 calibration/evaluation |
| 학습 / 생산 소비 | NOT_READY | 구체적 방법의 별도 채택, G1, O2/V5와 행동 수용 |

첫 역할 검토는 **외부 Foam 상단과 내부 경로의 구분**으로 한정한다. 모든 후보나 네 가지
재질 class의 dense label을 요구하지 않는다. [검토 그림](../../50-diagnostics/s11/2026-10-13-native-role-readiness/native-role-review.png)과
[정확한 subject 명세](../../50-diagnostics/s11/2026-10-13-native-role-readiness/review-proposal.json)에
새로 표시한 세 경로의 대응 판단만 요청한다.

| Subject | 표시한 전체 경로 | 사용자 판단 전 상태 |
|---|---|---|
| N1 | Water f1232, X950/Y477을 지나는 57 pixels | PENDING |
| N2 | 같은 frame, X950/Y487을 지나는 7 pixels | PENDING |
| N3 | Sample4 f1620, X595/Y813을 지나는 19 pixels | PENDING |

응답은 `외부 Foam 상단 / Foam 내부 변화 / 액체 상단 / 구조·반사 / 위치 근사만 허용 /
판정 불가` 중 해당 역할 또는 일부 구간만 해당한다는 설명을 받는다. 기존 상단 구간·
R/L 재질 영역·water B/C·f1485 A/B 판정은 유지한다. 이번 질문은 새로 표시한 native 경로와
그 역할의 대응을 묻는다. 정확한 한 픽셀 오차나 전체 재질 mask를 요구하지 않는다.
근사만 허용하는 답은 physical positive로 바꾸지 않는다. N1/N2는 같은 frame이며
N3도 이미 노출된 개발 자료다. 답변이 와도 independent efficacy나 학습 허가를 뜻하지 않는다.

이를 assistant 시각 추정으로 채우면 검증할 역할을 스스로 정답으로 만드는 문제가 된다.
따라서 사용자 판단 전 G1 방법·학습·생산 소비를 진행하지 않는다. 역할이 확인된 범위만
재평가한 뒤 필요한 비교와 대조군, 비용을 고정한다. 새로운 학습 범위는 그때 별도 채택하며,
Windows는 이후 WP04의 V5에서 필요하다. 이번 중단은 Windows 실행 요청이 아니다.

## 검증과 정리

- Focused tests **21 PASS**: stale source/review, frame/PTS/geometry, duplicate/missing binding,
  구간 0/1/복수 edge, partial path·junction·crop/mask, shared faces·zero label,
  shared pixel, A/B 정정, non-repo/한글·공백 경로 CLI와 overwrite 거부.
  Glass/index/source/Y 검사는 호출하는 기존 CR1/O2 owner를 그대로 사용했다.
- 실제 CLI를 `/private/tmp`에서 실행: **2.795 s**, fresh-process peak RSS **299,204,608 bytes**,
  gzip readout **247,457 bytes**. 이는 Mac의 저장 자료 결속 비용이다.
- 별도 NumPy 재계산으로 2,670개 context side, 3,047개 incident path/hash/분모,
  전체 edge 목록과 좌표변환, A/B qualification을 대조했다. 생산 source **221개 hash 일치**.
- Managed G0 run `s11-native-role-readiness-20261013-002`에 단일 manifest/readout/verification
  위치를 연결했다. 초기 001의 출력은 alternative-view shared support를 추가한 최종표로
  대체하고 삭제했다. raw 영상·이미지·모델·기존 score는 복제하지 않았다.
- 검토 그림은 기존 pixels의 nearest-neighbor 표시이며, 저장 fragment 좌표를 그대로
  겹쳤다. 실제 생성물을 확인했다. [renderer](../../50-diagnostics/s11/2026-10-13-native-role-readiness/render_review.py)는
  기존 직사각형 reference renderer가 표현하지 못하는 native polyline만 담당한다.
  임시 proposal/render 출력은 review managed run에서 단일 추적 위치로 이동했다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F07`, `S11-F09`, `S11-F10`.
- First harmful stage: 새 물리 효능/손실 원인을 판정하지 않음. 기존 sample4 f1620 component-to-front 손실은 원래 P5 증거에서 유지하며, G0의 unavailable labels나 구간 hit로 원인을 추가 추론하지 않음.
- Logic-map impact: NONE — 기존 lossless geometry와 pin/qualification owner를 호출하는 오프라인 도구만 추가; 생산 실행 경로·schema·후보·selector 변경 없음.
- Failure-registry impact: NONE — 약한 판정의 정밀도와 shared support를 보존하는 G0 구현; 물리 identity/recall 복구나 새로운 실패 family를 주장하지 않음.
