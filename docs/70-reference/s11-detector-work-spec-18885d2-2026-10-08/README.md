# S11 detector 설계·작업 명세 패키지

기준: `teeeeooo/oil_level_tracker` / `main @ 18885d226a7a7745bc2d062fd750ec263b9c78f6`.

## 파일

| 파일 | 용도 |
|---|---|
| `S11-detector-design-and-work-spec-18885d2-2026-10-08.md` | 결론, 현재 상태, 새 설계, D2–D6 작업 단위, controls, Windows acceptance, 중단 기준, 근거 색인 |
| `verification-summary.json` | 이번 실제 실행과 상속된 증거를 구분한 공유용 검증 요약 |
| `reproduce_saved_sequence_audit.py` | 현재 pinned code로 저장된 두 시퀀스를 다시 확인하는 portable helper |
| `SHA256SUMS.txt` | 공유 패키지 구성 파일의 무결성 확인 |

새로운 detector 패치나 채택된 production 설계가 아니다. Source code, 원본 recipe, truth/golden, tracked Work Plan은 변경하지 않았다. Windows 원본 영상, private ZIP, sample 영상·screenshot은 패키지에 포함하지 않는다.

## 바로 이어서 수행할 작업

먼저 명세서 §5–§7을 따른다. 기존 reference 입력과 실제 candidate-support lineage를 연결하는 **diagnostic-only D2-A**가 첫 작업이다. `mixed_or_uncertain` demo를 실제 reviewed-support control로 승격하지 않는다. Input readiness·controls·comparison rule을 고정하고 한 번의 bounded 비교 후 go/no-go를 결정한다. D1 재조사, UI 재개발, broad gate 완화, 기존 실패 실험 재튜닝으로 시작하지 않는다.

현재 상태 owner는 계속 `docs/00-project/work-plan.md`다. 이 명세서를 채택할 경우 필요한 durable 조항을 architecture/validation owner에 반영하고, 별도 중복 상태 원장을 만들지 않는다.

## 시퀀스 재현

이 helper는 Git에 포함되지 않은 기존 Mac 비교 outputs가 있는 checkout에서만 실행할 수 있다. Repository 가상환경을 사용한다. HEAD가 다르거나 tracked 변경이 있으면 의도적으로 중단한다. Output은 반드시 아직 없는 경로를 지정한다.

```bash
/path/to/oil_level_tracker/.venv/bin/python \
  /path/to/package/reproduce_saved_sequence_audit.py \
  --repo /path/to/oil_level_tracker \
  --output /path/to/oil_level_tracker/sample/output/s11-sequence-recheck-new
```

입력은 `sample/output/s11-d2-recipe-artifact-20261008-001/`의 baseline/registered recipe와 raw/completed JSON이다. 원본 영상을 디코딩하지 않고 현재 completed resolver만 실행한다. 성공 기대값은 113개 × 2변형 complete detection의 전체 필드 동일성이다. 이것은 검출력 개선 증명이 아니다.

패키지 helper는 실제 native runner를 portable CLI로 정리한 별도 파일이다. 패키지 형태에서는 Python compilation과 CLI help를 확인했다. 문서의 226개 재현 결과는 Mac의 `verify_saved_sequences.py` 실행 결과이며, helper 파일 자체를 원격 corpus에서 실행했다고 주장하지 않는다.

## 원본 감사 산출물 위치

Mac repo의 아래 ignored 디렉터리에 실행 당시 스크립트, source-contact sheets 및 원본 receipt가 남아 있다.

```text
sample/output/s11-current-detector-work-spec-20261008-002/
```

`verification-summary.json`은 도구 결과에서 옮긴 공유용 요약이다. 230개 전체 pin 및 프레임별 ROI pixel hash는 native preflight/receipt가 소유한다. 공유 JSON을 원본 receipt의 byte-preserved 복사본으로 취급하지 않는다.

현재 결론은 **설계·감사 완료 / 새 detector efficacy 미검증 / Windows FIELD FAIL 유지**다.
