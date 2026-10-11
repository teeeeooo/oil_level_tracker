# S11 프로그램 감사·Detector 작업 명세 — 2026-10-11

## 먼저 읽을 파일

- `S11-program-audit-and-detector-work-spec.md`: 현재 상태, 실제 실행, 원인별 설계, P0–P7 전체 작업, 수용 기준, Windows 9구간, 종료/rollback 계획.
- `evidence/audit-record.json`: 이번 직접 실행 및 하지 않은 검증의 범위.
- `evidence/sample4-current-default-checkpoints.json`: 현 main 기본 detector의 113행 실행에서 선택한 12개 checkpoint·극값 event·실행 비용. Live tool 출력에 근거한 **파생 요약**이며 전체 native receipt의 바이트 사본은 아님.
- `evidence/source-ledger.json`: 읽은 저장소 문서/코드의 Git ref·SHA-256·행 수.
- `evidence/source-frame-audit.json`: 직접 decode한 6개 영상/37개 frame과 9개 저장 raster 일치 기록.
- `evidence/p2-independent-verification.json`: 저장 P2 비용의 독립 재검산. 내부 `execution_head`와 `focused_tests`는 원래 실험의 provenance이며, 이번 fresh suite는 263건.
- `evidence/p5-verification-summary.json`: 기존 P5 raw-stage/position 결합 검사의 주요 필드를 보존한 요약. 이는 scoped/FULL 저장 증거이며 새 기본 NONE 실행의 raw trace가 아님.

나머지 5개 JSON은 Mac에서 작성한 완전한 entry를 CRC 검증해 바이트 보존했다. 그중 원래부터 파생 요약으로 작성된 P5 파일은 전체 native readout을 대신하지 않는다. 원본 영상, 비공개 Windows 자료, 새 사용자 판독, 전체 소스코드 또는 새 report HTML은 이 패키지에 없다.

## 기준과 변경 범위

Repository: `teeeeooo/oil_level_tracker`

HEAD: `4d84f70c5026d92330628bbae7650ac6288a8e12`

이번 작업에서 운영 코드·Recipe·truth·현재 work-plan을 수정하지 않았다. 커밋/푸시를 수행하지 않았다. tracked worktree는 감사 종료 확인 당시 clean이다. 새 자료는 Mac의 ignored output 폴더와 이 전달 패키지에만 있다. 명세의 P2/P5 역할 판별은 후속 구현 제안이지 채택된 classifier가 아니다.

## Mac의 상세 증거 위치

`/Users/sunjaekim/Developer/oil_level_tracker/sample/output/s11-program-audit-20261011-001/`

이 폴더에 263건 JUnit/log, 37개 source crop과 6개 contact sheet, source decode 스크립트, 전체 P5 재검산, 전체 sample4 기본 replay JSON, 실행 로그 및 portable evidence가 보존돼 있다. 이 절대경로는 연결된 Mac 경로이며 Linux sandbox 다운로드 경로가 아니다.

## 재실행 예시

아래는 이미 실행한 작업의 재현 경로다. 새 destination을 정해 기존 결과를 덮어쓰지 않는다. 같은 Python/runtime·source·Recipe identity가 필요하다. Mac 로컬의 공개/개발 자료만 사용하며 sample3이나 비공개 Windows 영상은 실행 대상이 아니다.

```sh
cd /Users/sunjaekim/Developer/oil_level_tracker

QT_QPA_PLATFORM=offscreen .venv/bin/python \
  tests/diagnostics/s11_interface_witness_replay.py \
  --root "$PWD" --sample sample4 --debug-level none \
  --output '<NEW-OUTPUT>/sample4-current-default.json'

.venv/bin/python \
  docs/50-diagnostics/s11/2026-10-11-p2-shared-support/verify.py \
  --readout docs/50-diagnostics/s11/2026-10-11-p2-shared-support/readout.json \
  --out '<NEW-OUTPUT>/p2-independent-verification.json'

.venv/bin/python \
  docs/50-diagnostics/s11/2026-10-11-foam-upper-position-comparison.py \
  --root "$PWD" --output '<NEW-OUTPUT>/p5-independent-verification.json'
```

## 해석 한계

263 tests PASS와 재검산 PASS는 detector 성능 PASS가 아니다. Oil 101/113의 수치 유효성은 물리 정확도가 아니다. 제품 output의 JUDGMENT_PASS는 detector FIELD PASS가 아니다. 공개된 인접 장면은 독립 holdout이 아니다. 1초 cadence는 별도로 확인한 가시적·움직이는 같은 Oil 계면에만 적용한다.

**S11 ACTIVE / O2 OPEN / FIELD FAIL 유지.** 이번 결과의 핵심은 유효 행 수가 많아도 잘못된 target이 최고/최저 event를 차지할 수 있다는 점이며, 후속 계획은 이 왜곡과 주요 움직임 손실을 줄이는 데 우선순위를 둔다.
