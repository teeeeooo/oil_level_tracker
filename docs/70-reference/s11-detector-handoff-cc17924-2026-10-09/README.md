# S11 detector 설계·작업 명세서 인계 패키지

기준 HEAD: `cc179244c89ea59bd097fa165ea493942629e23e` / 2026-10-09.

## 읽을 순서

1. `S11-detector-design-work-spec-cc17924-2026-10-09.md`: 조사 결과, 실제 실험, 다음 구현 방식, D2–D6 작업·검증·중단 기준.
2. `S11-execution-summary-cc17924-2026-10-09.json`: 실행 범위, 정확한 수치, 원본 로컬 산출물 경로와 SHA-256, 미검증 범위.
3. `verify_local_evidence.py`: 기존 로컬 산출물이 전달 요약과 같은지 확인하는 read-only 보조 도구.

이 패키지의 CBR-1은 다음 구현 제안이다. 이번에 실행한 H0/G1은 physical selector로 승격하지 않았다. production, Recipe, truth, 기존 report는 변경하지 않았고 커밋·푸시도 하지 않았다. O2 OPEN / FIELD FAIL은 유지된다.

## 로컬 산출물 확인

Mac 체크아웃의 다음 ignored 디렉터리에 실행 스크립트, 배열, preflight, 상세 수치, 검토 그림이 남아 있다.

```text
/Users/sunjaekim/Developer/oil_level_tracker/sample/output/s11-design-audit-cc17924-20261009-001/
```

Python 3.11 이상에서 다음 명령을 실행한다. 이 보조 도구는 detector나 Windows 작업을 실행하지 않는다.

```bash
python3 verify_local_evidence.py \
  --repo-root /Users/sunjaekim/Developer/oil_level_tracker
```

종료 코드 0은 기록된 로컬 자료의 hash와 기준 HEAD 일치다. 코드 1은 hash 불일치, 코드 2는 자료 부재·다른 HEAD·불완전한 확인이다. hash 일치는 detector 정확도나 field acceptance가 아니다. `sample/output/`와 영상은 Git ignored이므로 새 clone에는 없을 수 있다. 영상·array가 없는 배포용 완전 재현 패키지라고 해석하지 않는다.

원본 Mac 영상, private Windows 자료, 기존 `.oiltruth`, native 실험 배열은 첨부하지 않았다. 조사용 원본 runner는 위 로컬 디렉터리에 있으며, 본 ZIP의 helper는 그 결과를 변경하지 않고 검사한다. `SHA256SUMS.txt`는 전달 패키지 파일의 무결성 목록이다.
