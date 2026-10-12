# CR-1 착수 전 저장소 정리 체크포인트 — 2026-10-12

**결과: 사용자에게 설명한 1–3단계(조사 → 정리 → 보존 검증) 완료. CR-1 미착수.**
사용자가 이 체크포인트를 확인한 뒤 진행 여부를 알려주기로 했다. 현재 실행 권한과
다음 행동은 [Work Plan](../../00-project/work-plan.md#repository-cleanup-and-isolated-cr-1-sequence)이 소유한다.
기존 문서 표의 3번에 섞여 있던 WP1 조건 확정은 대화에서 확인한 범위대로 4번으로
정렬했다. 이번 작업은 CR-1 참조 선정·조건 동결·환경 구성·설치·실행을 하지 않았다.

기준 HEAD는 `d323f08922994d95bc3474d82324a7986ba2b681`, 시작 브랜치는 `main`,
미커밋 변경은 없었다. 등록 worktree는 현재 저장소 하나였으며 제거할 다른 worktree는
없었다. 이 문서가 추가된 체크포인트 커밋은 해당 파일의 Git 이력으로 확인한다.

## 정리 결과

용량은 `du -sk`의 할당량을 십진 GB/MB로 환산했다. 아래 사후 값은 삭제 직후이며,
이 체크포인트의 문서·압축 목록 약 1.64 MB와 이후 Git 객체가 추가되기 전이다.

| 항목 | 정리 전 | 삭제 직후 |
|---|---:|---:|
| 프로젝트 폴더 전체 | 7.538 GB | 7.307 GB |
| `sample/output` | 5.661 GB | 5.461 GB |
| 기존 `.venv` | 1.529 GB | 1.529 GB |

**삭제 대상의 실제 할당량 감소: 231,264,256 bytes (231.3 MB).**

| 제거 대상 | 파일 수 | 보존·복구 근거 |
|---|---:|---|
| 종료된 temporal-texture 실험의 전개 사본 | 59 | 기존 `sample/output/s11-temporal-texture-20261010-preserved.zip`의 해당 member와 길이·SHA-256 동일. ZIP 원본은 유지 |
| Python / pytest 캐시 | 741 | 기존 `.venv`와 Git 추적 파일을 제외한 재생성 가능한 캐시. source·판정 근거가 아님 |
| Graphify 파생 캐시 | 235 | `graphify-out/`만 정리. source·logic map·failure registry와 기존 refresh script/설치된 CLI는 유지 |
| 합계 | 1,035 | 삭제 목록에 있는 파일만 개별 제거하고 비어 있는 해당 하위 폴더만 정리 |

`water-f001438.npz`는 같은 ZIP에 있지만 별도 물 표면 검토의 입력이므로 원래 경로에
유지했다. 캐시 정리는 공유 pip/uv 캐시, 기존 `.venv`, Git 이력에 손대지 않았다.
새 native-data ZIP이나 모델 파일을 만들지 않았다.

## 보존 및 경로 검증

- `sample/output`의 211개 최상위 항목, 26,053개 파일/심볼릭 링크를 조사했다.
  삭제 뒤 남은 **25,755개 항목 전부**의 SHA-256 또는 링크 대상이 시작 시점과 일치한다.
- 정리 직후 기존 Git 추적 파일 **1,396개 전부**와 원본 영상 **8개 전부**가 시작 시점과
  동일했다. 이후 이 체크포인트와 소유 문서만 갱신했다. 영상은 디코드하지 않았다.
- candidate preflight의 **293개 입력**(제품 Python 221개 포함)이 기존 pin과 일치한다.
  그중 Git 제외 캡처/manifest **45개**는 원래 경로를 유지한다.
- peer audit의 sample4 `raw.json` / `completed.json` / `summary.json` 해시를 확인하고,
  저장 JSON의 raw/completed **113개 프레임**을 읽었다. public pipeline의 **3개 프레임**과
  ZIP의 **95개 logical 파일**도 기존 저장표의 길이·해시와 일치한다.
- temporal-texture ZIP의 원래 SHA-256과 **60개 member 전부**를 삭제 전후 확인했다.
  압축을 메모리로 풀어 원래 파일 바이트와 비교했으며, 큰 복사본을 디스크에 다시 쌓지 않았다.
- CR-1 workspace, 기존 `.venv`의 `torch`, Torch/Hugging Face 모델 캐시는 존재하지 않는다.
  모델 다운로드·설치·추론, CR-1 WP1 실행 및 Windows 실행은 하지 않았다.

기존 성공 테스트를 다시 수행한 것으로 보고하지 않는다. 이번 검증은 저장된 파일,
입력 경로, JSON 로딩과 무손실 압축 복원을 대상으로 한다. 제품 코드·의존성·패키징은
변경하지 않았고 **O2 OPEN / FIELD FAIL / Local XY OFF**는 유지한다.

S11 governance, 변경/신규 문서의 로컬 링크·앵커 20개, 신규 파일 4개의 색인 연결,
압축 JSON 왕복과 `git diff --check`를 확인했다. 문서 갱신 후에도 보호 입력 293개와
제품 `src/`의 Git 추적 파일 226개가 기준 바이트를 유지한다.

## 남긴 항목과 이유

동일한 내용이라는 이유만으로 서로 다른 실행의 필수 경로를 삭제하지 않았다.
Local XY의 큰 결과 폴더에는 현재 입력 캡처가 있고, P5 default-linkage는 최신 peer audit의
입력이다. Local XY native 165개 파일은 기존 saved-output verifier의 경로 계약을 유지한다.
과거 worktree snapshot, 고유 조사 결과와 독립적으로 제거 근거를 확정하지 못한 항목도
남겼다. 남은 5.461 GB 전체가 불필요하다는 뜻도, 전부 현재 필수라는 뜻도 아니다.

각 최상위 항목의 보존 사유와 제거 수는
[검증 receipt](2026-10-12-pre-cr1-cleanup/receipt.json)에 있다. 추가 감소량을 맞추기 위해
고유 증거를 지우거나 보존 의무를 낮추지 않았다. 원본 영상과 보존 ZIP은 계속 Git 밖에
있으며 새 clone만으로 모든 과거 실험을 재현할 수 있는 것은 아니다.

## 복구와 검토 경로

- [전체 시작 목록](2026-10-12-pre-cr1-cleanup/inventory.json.gz): 경로, 크기, 할당량,
  해시/링크 대상 및 시작 Git 상태. gzip 안에는 JSON만 있다.
- [삭제·복구 매핑](2026-10-12-pre-cr1-cleanup/removal-manifest.json.gz): 삭제한 파일마다
  원래 해시와 ZIP/member 또는 캐시 재생성 방법을 기록했다.
- [검증 receipt](2026-10-12-pre-cr1-cleanup/receipt.json): 사전/사후 용량, 보호 입력,
  보존 결과와 CR-1 미착수 확인. 위 두 압축 목록의 해시도 포함한다.

temporal-texture의 과거 native 경로가 필요한 경우, 삭제 매핑의 ZIP/member를 새 빈
임시 폴더에 풀고 길이·SHA-256을 확인한다. 원래 경로를 요구하는 과거 runner는 그때
필요한 파일만 원래 위치에 복원한 뒤 사용한다. 기존 파일을 덮어쓰거나 과거 실험을
새 영상 decode로 대체하지 않는다. 캐시는 필요할 때 Python/pytest 또는
`scripts/update_graphify_s11.sh`가 재생성할 수 있다.

다음 단계는 사용자 체크포인트 확인 후의 **4번: WP1 조건 확정과 격리 환경 준비**다.
최대 3 GB, 모델/참조 집합 하나, full/local 비교 및 미채택 시 제거라는
[실험 계약](../../20-architecture/s11-contextual-role-observation-design.md#local-footprint-and-removal-contract)은 유지한다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F09`, `S11-F10`
- First harmful stage: no new detector investigation; this checkpoint verifies storage and saved-input preservation. It does not change or resolve the previously recorded role/authority failures.
- Logic-map impact: NONE — only verified duplicate/cache removal and checkpoint routing; production source, runtime owners, source coordinates and publication behavior are unchanged.
- Failure-registry impact: NONE — existing failure evidence and its source bindings are preserved; no new mechanism, physical label or acceptance claim is introduced.
