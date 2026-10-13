# CR1 49.5초 경쟁 후보의 역할 판정 — 2026-10-13

**B/idx8 역할 질문 CLOSED — A/idx19와 같은 실제 Oil 유면 경계.**
사용자는 모바일 원본/후보 위치 이미지를 확인한 뒤 **“같은 유면의 경계야”**라고
답했다. [원문과 정확한 연결](2026-10-13-cr1-competitor-role-reply.json)은
`c248c9286b03093c213ee08bbb46cc7cb567f60b` 기준이며, 실제 보낸
[모바일 비교 이미지](2026-10-13-cr1-competitor-role-review.png)와 기존 HTML,
원본 PNG, capture, score table의 hash를 보존한다.

## 판정 범위

sample4 f1485/49.5 s의 `material_path` idx8/대표 Y841이 기존 확인된
`phase_transition_scan` idx19/Y836과 같은 실제 유면을 가리킨다는 **후보 대응**이다.
B의 중심 포함 구간 X586–605의 저장 표본은 Y838이며, 전체 저장 표본은 Y837–843이다.
대표 Y, 구간 표본, 정확한 X595 교점은 여전히 다른 의미다.

각 sector의 픽셀 정확도, 새 허용 오차, 인접 프레임이나 다른 후보의 정답으로
확대하지 않는다. A의 기존 판정은 유지한다. 원래 CR1/preflight의 `UNREVIEWED`
라벨과 hash는 당시 기록으로 보존하고, 이번 reply만 명시적인 추가 권위로 연결한다.
이 질문을 다시 열거나 위치가 비슷한 다른 후보에 라벨을 자동 전파하지 않는다.

## 고정 정책 가설에 미치는 영향

저장 점수와 기존 사전검사의 `observe`를 읽기 전용으로 재사용했다. 영상 디코드,
모델 재추론, 새로운 threshold/참조 탐색이나 detector 실행은 없다.

| 후보 | local interface | local texture | interface signed margin | 사용자 역할 |
|---|---:|---:|---:|---|
| A / idx19 / Y836 | 0.7269062770211362 | 0.7113942668093107 | +0.015512010211825467 | 기존 실제 유면 대응 |
| B / idx8 / Y841 | 0.8290812581924134 | 0.8502876849230638 | −0.02120642673065043 | 이번에 같은 실제 유면 대응 확인 |

B는 full/local 모두 texture 선호다. 따라서 제안된 **모든 anchor에서 local
interface 우세**라는 필요조건을 어떤 `tau_support`에서도 통과할 수 없다.
이는 조건의 실제 후보 누락 사례이며, B를 texture/structure라는 물리적 음성으로
분류할 근거가 아니다. 이 사례를 살리기 위한 margin 완화나 점수 argmax도 채택하지 않는다.

반면 A는 동일 프레임에서 기존 역할 필요조건을 충족한다. 원래 capture의 completed
Oil Y도 836이다. 따라서 이 답변만으로 중요한 움직임/숫자 관측이 지워진다고
결론낼 수 없다. 새로운 consumer/sequence를 실행하지 않았으므로 개선 또는
무손실 판정도 아니다. **후보 누락, 프레임의 실제 대안 존재, 최종 report 영향**을
각기 다른 분모로 남긴다.

| 노출된 자료의 갱신 | 결과 |
|---|---|
| 전체 모집단 | 기존 164개 유지; 후보나 score를 새로 생성하지 않음 |
| 확인 후보 / 미검토 후보 | 7 / 150 → 8 / 149; 기존 거부 3개와 문맥 대조군 유지 |
| 초기 reference가 아닌 확인 후보 | 7개 중 6개에서 local interface 선호; B는 texture 선호 |
| 그 확인 후보가 있는 고유 프레임 | 6개; 각 프레임에 local interface 선호인 기존 확인 후보가 적어도 하나 있음 |
| 독립 영상 / untouched holdout | 1 / 0으로 불변 |

위 집계는 `tau_support`를 적용한 eligibility, 정확도, calibration 또는 효능 검증이
아니다. 조건 실패를 숨기지도, 모든 후보를 맞혀야 한다는 새 종료 조건으로 바꾸지도
않는다. 독립 calibration/evaluation, geometry 이전, 역할 정밀도와 영향 범위는 아직
미해결이다. 현재 단계와 다음 행동은 [Work Plan](../../00-project/work-plan.md)이 소유한다.

## 보존과 확인

답변 JSON과 실제 표시 이미지 140,806 bytes만 새로 보존한다. 원본/영상/점수는
기존 파일을 참조한다. 이미지를 재가공하거나 frozen 실험 receipt를 고치지 않았다.
이동한 모바일 비교본의 hash는 reply와 일치한다. 원본 확대본과 matplotlib 임시
캐시는 전달 용도가 끝나면 정리한다. reply binding과 기존 source/candidate/time,
점수 margin 및 분모는 저장 자료를 직접 읽어 확인했다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: local descriptor preference would lose a source-confirmed candidate if treated as a necessary physical-role test; no production consumer exists and frame/sequence/report loss is not established.
- Logic-map impact: NONE — a scoped user correspondence and saved-score interpretation change; candidate generation, admission, sequence and publication remain unchanged.
- Failure-registry impact: NONE — existing role/provenance and threshold-rescue guards cover this counterexample; no new production mechanism or field outcome is asserted.
