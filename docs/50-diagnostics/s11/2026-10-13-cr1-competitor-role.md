# CR1 49.5초 경쟁 후보의 역할 판정 — 2026-10-13

**후속 설명 반영 / B는 실용적으로 수용한 근사 위치이며, 물리적 경계 확인으로 해석한 결론은 정정한다.**
사용자는 처음에 **“같은 유면의 경계야”**라고 답했지만, 이후
[빨간 점을 추가한 이미지](2026-10-13-cr1-competitor-role-annotation.png)와 함께
점 위쪽에도 미세 Foam이 있으며 검출 한계 때문에 B 정도의 선을 Foam–Oil
경계로 수용한 것이라고 설명했다. [후속 답변 원문과 연결](2026-10-13-cr1-competitor-role-clarification.json)이
이번 판정의 의미를 소유한다. B의 실용적 수용은 유지하고, 정확한 물리적 경계
확인과 혼동하지 않는다.

[최초 답변과 당시 해석](2026-10-13-cr1-competitor-role-reply.json)은
`c248c9286b03093c213ee08bbb46cc7cb567f60b` 기준의 역사 기록으로 bytes를
보존한다. 그 안의 `confirmed_target`, 물리적 동일 경계 관계와 8/149 집계는
후속 설명으로 정정된 당시 해석이다. 실제 표시한
[비교 이미지](2026-10-13-cr1-competitor-role-review.png)의 `unreviewed` 문구도
최초 질문 당시 표기이며 현재 판정 상태가 아니다.

## 판정 범위

대상은 sample4 f1485/49.5 s의 `material_path` idx8/대표 Y841이다.
B의 중심 포함 구간 X586–605의 저장 표본은 Y838이며, 전체 저장 표본은
Y837–843이다. A는 `phase_transition_scan` idx19/Y836이다.
대표 Y, 구간 표본, 정확한 X595 교점은 여전히 다른 의미다.

- **물리적 설명:** 사용자가 빨간 점으로 표시한 부근 위쪽은 미세 Foam을 포함한다.
  점은 지역적 설명이며 정확한 윤곽·X595 교점·허용 오차로 수치화하지 않았다.
- **실용적 수용:** 사용자는 이 B 위치를 근사적인 Foam–Oil 경계 출력으로 허용했다.
  이를 삭제하거나 완벽한 픽셀 정답을 새 수용 조건으로 요구하지 않는다.
- **A와 주변으로의 확대 금지:** A도 표시한 부근보다 위쪽이다. 과거 A 라벨은
  보존하지만, A가 이 프레임의 물리적 정답 대안이라는 후속 평가 주장은 철회한다.
  이번 설명이 A의 새 실용적 승인이나 모든 sector의 물리적 음성을 뜻하지 않는다.

빨간 점을 B와 같은 수면의 앞뒤 투영이라고 재해석해 최초 결론을 복구하지 않는다.
Foam 상단 높이, 인접 프레임, 다른 후보 또는 전체 영상의 정답으로도 확대하지 않는다.
원래 CR1/preflight와 최초 reply는 수정하지 않고 이번 설명을 별도 권위로 연결한다.

## 고정 정책 가설에 미치는 영향

저장 점수와 기존 사전검사의 `observe`를 읽기 전용으로 재사용했다. 영상 디코드,
모델 재추론, 새로운 threshold/참조 탐색이나 detector 실행은 없다. CR1의
reference 유사도는 확률이나 보정된 물리적 역할 판정이 아니며 생산 선택에 연결되지 않았다.

| 후보 | local interface | local texture | interface signed margin | 사용자 역할 |
|---|---:|---:|---:|---|
| A / idx19 / Y836 | 0.7269062770211362 | 0.7113942668093107 | +0.015512010211825467 | 과거 대응 보존; 현재 물리적 대안 주장은 철회 |
| B / idx8 / Y841 | 0.8290812581924134 | 0.8502876849230638 | −0.02120642673065043 | 사용자가 실용적으로 허용한 근사 위치 |

B는 full/local 모두 texture 선호다. 따라서 제안된 **모든 anchor에서 local
interface 우세**라는 필요조건을 어떤 `tau_support`에서도 통과할 수 없다.
이는 **사용자가 허용한 근사 위치를 배제하는 조건**임은 보여주지만, 정확한 물리적
계면의 오분류·누락을 입증하지 않는다. 미세 Foam 설명은 texture 선호와 양립할 수
있지만 CR1의 물리 판정 성공을 증명하지도 않는다. 이 사례를 살리기 위한 margin
완화나 점수 argmax는 채택하지 않는다.

한편 A가 역할 점수 조건을 충족하고 원래 capture의 completed Oil Y가 836이라는
계산 사실은 그대로다. 그것이 실제 물리적 경계나 report 보존의 증거라는 해석은
철회한다. 새로운 consumer/sequence를 실행하지 않았으므로 개선·무손실·새 손실
판정도 없다. **물리적 역할/위치, 실용적 수용, 최종 report 영향**을 나눠 평가한다.

| 기록과 주장 범위 | 결과 |
|---|---|
| 전체 모집단 | 기존 164개 유지; 후보나 score를 새로 생성하지 않음 |
| 원래 고정 라벨 | 확인 7 / 미검토 150; 당시 scope와 기존 거부 3개·문맥 대조군 보존 |
| 최초 답변에서 유도한 8 / 149 및 7개 중 6개 | 물리적 확인/성능 분모라는 현재 해석 철회; 최초 reply에 역사 기록으로 남음 |
| 이번 추가 판정 | B 실용적 수용 1개 / 새 물리적 확인 0개 |
| f1485의 물리적 대안과 6프레임 보존 주장 | 이번 설명으로 입증되지 않음; 다른 원래 판정의 scope는 자동 변경하지 않음 |
| 독립 영상 / untouched holdout | 1 / 0으로 불변 |

근사 출력의 실용적 허용을 깨끗한 physical-role calibration label로 바꾸지 않는다.
반대로 물리적 정확도와 분리한 실용적 평가에서는 B 수용을 보존한다. 이 한 사례가
전체 허용 오차나 실패 면제 기준을 만들지는 않는다. 현재 단계와 다음 행동은
[Work Plan](../../00-project/work-plan.md)이 소유한다.

## 보존과 확인

최초 답변 JSON과 비교 이미지 140,806 bytes는 그대로 두고, 사용자 주석 이미지
174,231 bytes를 byte-for-byte 보존했다. 후속 reply가 두 이미지, 최초 답변,
원본/capture/점수를 hash로 연결한다. 빨간 점을 자동 추출하거나 새 정답선을
생성하지 않았다. 원본 영상·점수·frozen 실행 receipt와 생산 코드는 변경하지 않았다.
보존 목적은 검출 한계 때문에 허용한 위치가 물리적 정답으로 다시 승격되는 것을
막는 것이다. 같은 증거의 추가 영상·확대본은 만들지 않았다.

## 실행 도구에 판정 의미 반영

[기존 CR1 사전검사](../../../tests/diagnostics/s11_contextual_role_preflight.py)의
`--review-manifest`로 후속 설명을 실제 집계에 연결했다. 이 경로는 원래 audit
결과가 frozen readout과 완전히 일치하는지 확인한 뒤 별도의 작은 보충 결과만
쓴다. [판정 연결 manifest](2026-10-13-cr1-review-qualification/manifest.json)와
[실행 결과](2026-10-13-cr1-review-qualification/readout.json)는 각각 3,955 / 6,546 bytes다.

| 검증 항목 | 결과 |
|---|---|
| 원래 모집단·점수·좌표 | 164개 전부 기존 readout과 동일; 모델 호출·영상 decode 0 |
| 원래 라벨 | 미검토 150 / 확인 7 / 거부 3 / 내부 Foam 3 / 기존 CBR 대조 1 그대로 |
| 이번 물리적 qualification | A/B 2개 `NOT_QUALIFIED`; 나머지 162개는 기존 검토 범위만 보존 |
| 이번 실용적 수용 | B 1개만 `ACCEPTED_APPROXIMATION`; 나머지 163개는 이번 수용 판정 없음 |
| 새 물리적 정답 / untouched holdout | 각각 0개; 이를 detector 정확도 분모로 바꾸지 않음 |
| 실행 검증 | focused tests 42 passed in 0.42 s; 실제 CLI를 `/private/tmp`에서 실행해 164개 연결 확인 |

시간·후보 fingerprint·authority hash가 다르거나 B 설명을 A/같은 Y의 다른 후보에
적용하려는 입력은 거부한다. 물리적 정답 승격·새 threshold·덮어쓰기도 거부한다.
원래 명령은 기존 v1 결과를 유지한다. 새 출력의 `HISTORICAL_ONLY`는 기존 판정을
삭제하거나 모두 오답으로 바꾼다는 뜻이 아니다. 이번 보충 판정이 그 범위를
추가로 넓히지 않는다는 뜻이다.

재현은 기존 manifest와 `--review-manifest`의 위 manifest를 함께 지정하고
새 managed work 경로로 출력한다. 실행 `review-qualification-20261013-001`은
두 JSON만 정식 위치로 옮겨 참조하며 원본·이미지·전체 readout을 중복 저장하지 않는다.
최초 준비 명령의 import 경로가 빠져 manifest 생성 전에 중단된 시도는 루트 `.venv`와
명시적인 source import 경로로 정정했다. 그 실패는 model/decode 실행이나 결과를
남기지 않았고, 위 실제 CLI 검증은 준비 후 성공한 실행이다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: source-reply interpretation conflated practical acceptance with physical truth. B's physical false-negative claim and A's physical-alternative claim are withdrawn; no production failure stage is established by these replies.
- Logic-map impact: NONE — scoped source clarification and evaluation semantics only; candidate generation, admission, sequence and publication remain unchanged.
- Failure-registry impact: NONE — existing role/provenance and threshold-rescue guards cover the distinction; no new production mechanism or field outcome is asserted.
