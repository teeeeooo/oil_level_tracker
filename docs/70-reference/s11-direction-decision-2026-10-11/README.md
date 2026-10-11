# S11 direction review — 5c53aef

## 핵심 결론

**지원 범위를 명시한 자동측정과 운동 맥락 중심 검증을 권고한다.** 완전 범용 물리 판별을 S11의 무제한 선행 조건으로 두지 않는다. 그렇다고 현재 검출기가 제한 범위에서 검증됐거나 S11을 완료해도 된다는 뜻은 아니다.

전체 설명과 모듈·단계별 계약은 `S11_PROGRAM_DECISION_AND_WORK_SPEC.md`를 읽는다. 바로 인수인계할 때는 `HANDOFF.md`부터 읽는다.

## 실제 실행과 제안의 경계

현재 `main @ 5c53aefe3bb3c5d1447b29ccb2f78d1adc5459c6`의 저장 증거를 재검증했다. verifier 3종, 집중 테스트 162개가 통과했다. 새로 S2 비용식과 ablation 정규화의 결정 영역을 검증했다. 운영 detector, truth, Recipe, episode, Work Plan, FIELD FAIL은 바꾸지 않았다. 새 Windows 실행·MP4 전체 재디코딩·commit/push는 하지 않았다.

`STORY_ACCEPTANCE_TEMPLATE.json`은 비어 있는 평가 양식이다. 실행 결과, 물리 truth 또는 현재 gate를 대체하지 않는다.

## 재현

S2 수학 감사는 아래처럼 실행한다. stdlib만 사용하고, pinned repo의 checked-in preflight/readout만 필요하다. Python의 `-O` 옵션이나 `PYTHONOPTIMIZE`를 사용하지 않는다.

```bash
python3 tools/audit_s2_decision_geometry.py \
  --root /absolute/path/to/oil_level_tracker \
  --out /tmp/s11-s2-geometry-fresh.json
```

원래 pixel/default verifier와 집중 테스트를 재실행하려면 다음을 사용한다. 정확한 head, repo `.venv`, 보존된 ignored raster/trace가 필요하다. 저장 자료가 없으면 ZIP만으로 대체 실행할 수 없다.

```bash
bash tools/reproduce.sh /absolute/path/to/oil_level_tracker /tmp/s11-review-new-run
```

이 셸 래퍼는 전달 편의를 위해 작성했고 해당 파일 자체를 이번 Mac에서 다시 실행하지는 않았다. 그 안의 verifier·pytest 명령은 이번 세션에서 개별 실행했다. 수학 감사 Python 파일은 실제 Mac 실행본과 SHA-256이 일치한다.

## 증거 사본

`evidence/verifier-stdout.json`은 실제 재실행 stdout 요약을 전사한 파일이다. 대형 원본 verification receipt의 전체 사본이 아니다. `evidence/s2-decision-geometry.json`과 Python 감사 도구는 Mac 원본 해시와 **byte equality**까지 확인했다.

Mac 원본 보존 위치:

```text
/Users/sunjaekim/Developer/oil_level_tracker/sample/output/
  s11-direction-decision-5c53aef-001/
```

검증한 사실과 제안의 불확실성을 구별한다. 테스트 PASS를 물리 검출 성능 PASS로 읽지 않는다. 과거 native/reduced 영상은 개발 노출 자료이며 holdout이 아니다. 영상/이미지와 대형 trace는 이 패키지에 포함하지 않는다.
