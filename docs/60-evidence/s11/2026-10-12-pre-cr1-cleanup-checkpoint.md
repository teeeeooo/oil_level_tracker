# CR-1 착수 전 저장소 정리 체크포인트 — 2026-10-12

**결과: 보존 가치 심사와 실제 폐기까지 완료. CR-1 미착수.**
사용자가 이 체크포인트를 확인한 뒤 진행 여부를 알려주기로 했다. 현재 실행 권한과
다음 행동은 [Work Plan](../../00-project/work-plan.md#repository-cleanup-and-isolated-cr-1-sequence)이 소유한다.
기존 문서 표의 3번에 섞여 있던 WP1 조건 확정은 대화에서 확인한 범위대로 4번으로
정렬했다. 이번 작업은 CR-1 참조 선정·조건 동결·환경 구성·설치·실행을 하지 않았다.

1차 정리 기준 HEAD는 `d323f08922994d95bc3474d82324a7986ba2b681`, 시작 브랜치는 `main`,
미커밋 변경은 없었다. 등록 worktree는 현재 저장소 하나였으며 제거할 다른 worktree는
없었다. 이 문서가 추가된 체크포인트 커밋은 해당 파일의 Git 이력으로 확인한다.

## 보존 가치 재심사와 실제 폐기

사용자가 링크·기존 test의 참조만으로는 보존 명분이 약하다고 지적하고 진행을
승인했다. clean `f474bc3415fe5ace5c8e6e83e0c9afe8d34af339`에서, 전체 복구를
우선하던 이전 정책을 **현재 의사결정에 필요한 최소 증거 보존**으로 바꿨다.
단순 압축·이전이나 다른 위치의 백업이 아니라 로컬 payload의 실제 폐기다.

| 측정 (`du -sk`) | 이번 정리 전 | 이번 정리 후 |
|---|---:|---:|
| `sample/output` 실제 할당량 | 2.578 GB | 0.172 GB |
| 로컬 산출물 파일 수 | 3,326 | 252 |
| 프로젝트 전체 | 4.432 GB | 약 2.03 GB |
| 기존 `.venv` | 1.529 GB | 1.529 GB |

**추가 회수량 2,406,248,448 bytes, 약 2.41 GB.** 3,074개 파일과 빈 디렉터리
1,242개를 제거했다. 전체 수치는 새 Git 객체 반영 전이며, 남은 출력의 논리적
크기는 171,066,303 bytes다. 이전 ZIP에 든 경로까지 포함하면 원래 25,755개
논리 항목 중 25,503개의 전체 바이트 복구를 종료했다.

### 무엇을 남겼는가

- 현재 sample4 후보 160개의 바인딩과 Oil/Foam 반례를 가진 캡처 입력 45개.
- 기존 42개 S2 raster view의 원래 crop·mask·graph 자료. 후속 비교의 양성·대조군
  기반을 유지한다. 전체 trace나 닫힌 S2 실험의 완전 재실행을 보장하지 않는다.
- water/beer/milk의 선택한 native source 16장, base/sample2/3/4의 원래 검토
  geometry와 reader 불확실성, 재실행이 제한된 sample3의 판단 자료 8개.
- 현재 peer attribution에 필요한 raw/completed/summary 3개와 독립 보고서
  이해도 검토에 쓸 실제 HTML bundle 한 벌. 과거 보고서 모음은 폐기했다.

범주가 겹치는 경로를 합쳐 **252개**다. 각 목적·삭제 시 정보 손실·최소 형태·재심사
시점은 [보존 심사와 현재 목록](2026-10-12-pre-cr1-cleanup/retention.json)에 기록했다.
원본 영상 8개, 추적 중인 truth·최종 비교·실패 기록·제공 명세와 Git source 이력은
유지했다. 이전 보호 pin 293개에는 제품 소스 221개가 포함되며, 이를 모두 별도의
필수 산출물로 세지 않는다. 후속 입력 계약이 확정되면 남긴 캡처도 다시 심사한다.

### 무엇을 폐기했고 무엇으로 설명할 수 있는가

1. 1.207 GB 통합 ZIP, 과거 FULL trace·중간 배열·반복 이미지·source checkout
   사본과 전달용 ZIP을 폐기했다. 닫힌 실험의 결론·조건·완전한 비교 readout과
   핵심 실패는 기존 Git 기록에서 확인한다. 전체 과거 실행의 native 자료를
   다시 검증할 수 있다는 주장은 종료한다.
2. 205 MB temporal-texture ZIP과 후속 검토가 끝난 `water-f001438.npz`를 폐기했다.
   네 attempt의 runner·입력·실패, 전체 수치와 검토 그림은 기존 Git 파일에 있다.
   유일한 작은 [affine 반례 배열](2026-10-12-pre-cr1-cleanup/temporal-affine-counterexample.npz)
   14,031 bytes만 추가로 꺼내 hash를 확인했다. optical-warp 반례 결과도 원래
   complete readout에 있으며, 성공/실패 분모를 유리하게 줄이지 않았다.
3. Local XY의 165파일 전체 native corpus와 전달 ZIP은 폐기했다. 제공 원문,
   실행 요약·검증 기록·overview는 Git에 있고, 다음 판단에 쓰는 원본 PNG만 남겼다.
   과거 전체 verifier는 이미 source pin 차이로 실패했으며 이제 입력도 폐기됐다.
4. 2,072개가 모두 통과한 과거 test XML은 commit·기존 검증 owner와 집계값으로
   대체했다. 이 사례의 test/failure/error/skip 수와 원본 hash는 심사 기록에 있다.
   개별 통과 test의 이름·실행 시간은 보존 목적이 없어 제거했다.

**현재 상태는 `retention.json`이 우선한다.** `consolidation.json.gz`,
`compressed-files.json` 및 아래 이전 receipt는 당시 보존 증거이며 현재 전체 복구
약속이 아니다. 폐기 자료를 요청하거나 남은 파일과 섞어 요청하면 복원 도구는
`Intentionally retired` 오류를 반환하고 목적지를 만들지 않는다. 복구해야 할 때는
현재 목록의 개별 경로를 선택한다. 원본 매체가 있다고 옛 환경·출력을 정확히
재현할 수 있다고 가정하지 않으며 sample3/Windows 새 실행 권한도 생기지 않는다.

### 검증과 관리 적용

[폐기 receipt](2026-10-12-pre-cr1-cleanup/retention-receipt.json)에 실제 용량·파일 수와
검증 결과를 남겼다. 삭제 전 모든 대상이 이전 inventory/압축 map의 hash와 같음을
확인했고, 삭제 후 252개 생존 파일·293개 기존 pin·원본 영상 8개의 hash를 확인했다.
현재 peer 비교는 영상 decode 없이 116프레임·2,618 candidate join·1,892 support
일치·불일치 0으로 재현했다. 로컬 검증은 field acceptance를 뜻하지 않는다.
실제 CLI로 생존 JSON/PNG를 복원해 bytes·mode·mtime를 확인했고, 폐기 경로와
혼합 선택은 목적지 생성 없이 거부됐다. 남긴 보고서의 local 참조 34개도 확인했다.
peer 전체 readout은 HEAD metadata를 제외하고 기존 Git 보존본과 같다.

관리 도구의 `finish`와 `check`는 보존 자료가 있을 때 **용도·손실 정보·재생성·
최소 형태·재심사 시점** 5항목을 요구한다. 테스트 20개가 통과했다. 훅은 기록과
파일 상태를 검사할 뿐 문장으로 적힌 가치가 타당하다고 판정하지 않는다.
[관리 owner](../../40-operations/experiment-artifact-lifecycle.md)가 실제 판단과
사용 목적 종료 시 정리를 소유한다. 새 Skill·훅·주기적 보관 ZIP은 만들지 않았다.
CR-1 WP1 동결·설치·다운로드·추론은 수행하지 않았다.

## 이전 단계: 추가 압축과 관리 절차 적용

사용자 요청에 따라 clean `1073c67666477af2d88c76615458070d82413de8`에서
마지막 압축 대상과 앞으로의 관리 방법을 적용했다. 아래의 이전 정리 수치는
각 단계 당시 기록이다. 당시에는 기존 통합 manifest와 추가 압축 매핑으로
전부 복구할 수 있었다. 이후 폐기 여부는 위 `retention.json`이 우선한다.
역사 receipt·제공 원문의 bytes와 당시 판정을 덮어쓰지 않았다.

| 이번 대상 | 원본 논리 크기 | 최종 추가 저장 |
|---|---:|---:|
| 전체 trace JSONL 2개 | 359.78 MB | gzip 43.58 MB |
| matches / human ROI JSON 2개 | 91.43 MB | gzip 13.35 MB |
| Local XY sample3 completed JSON 1개 | 21.93 MB | 기존 ZIP의 동일 object 재사용; 새 사본 없음 |
| 합계 | 473.15 MB | 56.93 MB |

새 gzip 4개를 만들고 원래 전개 파일 5개를 제거했다. JSON 1개는 이미 기존
보관 ZIP에 있어 중복 gzip도 제거했다. `sample/output`의 실제 할당량은
**2.998 → 2.578 GB**, 파일 수는 **3,327 → 3,326개**가 됐다.
`du -sk` 기준 추가 회수량은 **419,971,072 bytes, 약 420 MB**다.
프로젝트 전체는 최종 문서·Git 객체 반영 전 약 **4.43 GB**다. `.venv` 1.529 GB는
유지했다. 논리 bytes와 APFS/파일시스템 할당량은 서로 다른 측정값이다.

- [추가 압축 매핑](2026-10-12-pre-cr1-cleanup/compressed-files.json): 기존 manifest hash,
  원래 경로·길이·SHA-256과 gzip/기존 ZIP object 대응.
- [검증 receipt](2026-10-12-pre-cr1-cleanup/compression-receipt.json): 전후 실제 용량,
  삭제 후 복원·형식 검증과 현재 입력 보호 결과.
- [관리 절차](../../40-operations/experiment-artifact-lifecycle.md): 지침·스크립트·기존
  Skill 연결·기존 pre-push 훅의 책임과 실제 시작/종료 명령.

모든 gzip은 삭제 전에 원본 길이/hash와 일치했고, 원본 제거 후 선택 복원 도구로
5개 모두 복원해 bytes·mode·mtime와 JSON/JSONL 로딩을 확인했다. ZIP 재사용으로
바꾼 1개도 중복 gzip 제거 후 다시 복원했다. 임시 복원본은 즉시 제거했다.
관리 도구와 복구 도구 테스트 17개가 통과했으며 실제 pre-push 경로의 미완료 실행
차단과 정리 후 허용도 임시 Git 저장소에서 확인했다. Skill frontmatter는 기존과
같고 추가 경로/문서 링크를 확인했다. 공식 Skill validator는 기존 환경에
PyYAML이 없어 실행하지 못했으며 이를 위해 의존성을 추가하지 않았다.
기존 전개 파일 중 남은 3,321개, 현재 입력 pin 293개, 원본 영상 8개와 기존
1.207 GB ZIP의 해시는 그대로다. 현재 peer 입력은 이번 이동 대상이 아니며,
이미 통과한 peer 재현을 다시 실행한 것으로 보고하지 않는다.

과거 trace/JSON 경로를 직접 소비하는 도구는 먼저 필요한 파일을 복원해야 한다.
특히 Local XY sample3의 `completed.json`도 현재는 원위치에 전개되어 있지 않다.
그 corpus의 과거 전체 verifier는 이전 정리 전부터 source pin 차이로 실패했으며,
이번 복원 검증을 해당 verifier의 PASS로 확대하지 않는다.

새 `start`는 기존 폴더를 덮어쓰지 않고 입력·관련 source·조건·예산을 기록한다.
`finish`는 명시한 증거만 남기고 해당 실행의 나머지 임시 파일을 제거한다.
동일한 입력·source·조건의 완료 실행을 알려 주며, 동일 payload는 `reuse`로
연결한다. `check`와 로컬 pre-push는 미완료·중복·예산 초과·잔여 파일을 검사한다.
frozen 역사 폴더에는 자동 삭제를 적용하지 않으며 훅 자체는 읽기 전용이다.
전체 생산 detector·의존성·패키징 및 CR-1 미착수/field 상태는 유지한다.

## 앞선 산출물 통합 결과

사용자가 25,755개 잔여 항목과 작은 감소량을 지적한 뒤 추가 정리를 요청했다.
1차 정리는 일부 전개 사본과 캐시 제거였으며 전체 산출물 구조의 정리 완료로
볼 수 없었다. 추가 작업 기준은 clean `main`의
`ffb60127e77c82fe430f574d7a88ffb0d9981810`이다. 아래 수치는 `du -sk`의
실제 할당량이며 추가 문서·Git 객체가 생기기 전 삭제 직후 값이다.

| 항목 | 추가 정리 전 | 추가 정리 후 |
|---|---:|---:|
| 프로젝트 전체 | 7.311 GB | 4.849 GB |
| `sample/output` | 5.461 GB | 2.998 GB |
| 산출물 파일·링크 | 25,755개 | 3,327개 |
| 기존 `.venv` | 1.529 GB | 1.529 GB |

**추가 순감소: 2,461,147,136 bytes, 약 2.46 GB.** 첫 정리 전 7.538 GB와
비교하면 누적 약 2.69 GB 감소다. 실제 제거한 전개 항목은 22,429개
(일반 파일 22,412개와 링크 17개), 비어 있는 관련 디렉터리는 2,644개다.
원본을 버리지 않고 9,486개 고유 payload와 경로·해시·mode·링크 대상 목록을
**1,207,296,048 bytes의 로컬 ZIP 하나**로 보존했다. 같은 내용은 한 번만
저장하며 복원할 때는 경로별 독립 파일로 만든다.

- ZIP: `sample/output/s11-preserved-outputs-20261012.zip`.
- 전체 경로별 keep/archive 및 참조 근거: [통합 manifest](2026-10-12-pre-cr1-cleanup/consolidation.json.gz).
- 실제 용량·삭제·보존·검증 결과: [추가 정리 receipt](2026-10-12-pre-cr1-cleanup/consolidation-receipt.json).
- 선택 복원 도구: [restore_s11_outputs.py](../../../scripts/restore_s11_outputs.py).

이 통합 시점에 원래 경로에 남긴 3,326개 파일은 기존 tracked 문서·코드·machine manifest의
직접 파일 참조, 현재 candidate pin, peer probe의 `none` bundle, Local XY
165파일 검증 corpus와 그 동반 파일이다. HTML 검토 화면의 이미지 58개도
추가로 남겨 기존에 연결되던 로컬 참조 140개를 보존했다. 과거 소스·문서 사본을
통합하면서 산출물 내 Python은 4,103→78개, Markdown은 2,117→2개로 줄었다.
현재 경로에 남아 있다는 사실만으로 모든 과거 자료가 현행 acceptance 입력이라는
뜻은 아니다. 반대로 일부 파일이 남은 과거 실행 폴더를 완전한 실행 bundle로
간주해서도 안 된다. 전체 과거 실행이 필요하면 해당 prefix를 먼저 복원한다.

### 추가 정리 검증

- ZIP의 모든 고유 payload를 실제로 압축 해제하여 원본 길이·SHA-256과 대조했다.
  삭제 직전 원본을 다시 확인했고, 삭제 뒤 남긴 3,326개 파일도 모두 재검증했다.
- 현재 입력 pin 293개, 원본 영상 8개, 기존 Git 추적 파일 전체가 삭제 시점에
  그대로였다. 이후 문서와 복구 도구·그 테스트만 추가/수정했다.
- 원본 제거 **후** 최종 ZIP에서 과거 소스 사본 758파일·4링크와 보고서
  285파일을 저장소 밖의 새 임시 폴더에 복원했다. 바이트·mode·링크 대상을
  원래 목록과 대조했다. 복구 도구의 선택 복원, 사본 독립성, 덮어쓰기 거부,
  손상·경로 탈출·링크 제한 및 실패 시 롤백 테스트 5개가 통과했다.
- 현재 peer probe를 원본 script 그대로 실행해 sample4 113 + public 3프레임,
  candidate join 2,618개, 저장 support 일치 1,892개와 mismatch 0을 확인했다.
  결과는 현재 HEAD metadata를 제외한 모든 필드가 기존 보존 결과와 같다.
- Local XY 165파일의 해시·JSON/이미지/CSV/Python 등 형식과 HTML 참조를
  확인했다. **과거 전체 verifier는 삭제 전부터 현재 source pin 차이로 중단됐다.**
  최초 실패는 `artifact_reference_diagnostics.py`이며, 정리 전후 같은 bytes다.
  이 검사를 PASS로 기록하거나 assertion을 완화하지 않았다. 상세 차이는 receipt에 있다.
- 새 영상 decode, frame detector, CR-1 모델 설치·실행, Windows 실행은 하지 않았다.
  S11 acceptance와 FIELD FAIL/O2 OPEN/Local XY OFF는 바뀌지 않는다.

### 현재 보존 자료의 선택 복원

아래 예시는 현재 보존된 기준 결과 요약을 새 폴더에 복원한다. destination의 부모는
존재하고 destination 자체는 없어야 한다. 원래 저장소 파일을 덮어쓰지 않는다.
이전 `s11-report-r1` 전체 보고서 등은 폐기했으므로 복구 대상으로 사용하지 않는다.

```bash
python3 scripts/restore_s11_outputs.py \
  --prefix sample/output/s11-p5-default-linkage-20261011-001/none/summary.json \
  --destination /tmp/oil-s11-report-recovery
```

단일 파일 경로도 `--prefix`에 넣을 수 있다. 출력 아래에 원래의
`sample/output/...` 경로가 재현된다. 도구는 manifest 옆 `retention.json`을 확인해
폐기 경로를 먼저 거부한다. 이전 `compressed-files.json` 형식도 읽을 수 있지만
이번 목록의 5개 압축 대상은 모두 폐기했으므로 더 이상 복구할 수 없다.
현재 남은 경로는 로컬 원본의 hash를 확인해 복사한다. 과거 symlink 17개도
폐기 대상이며 `--include-symlinks`로 폐기를 우회할 수 없다. 검토 후 임시 복원본은
제거하여 같은 사본이 다시 누적되지 않게 한다.

ZIP/gzip은 Git 제외 로컬 자료이며 **원격 백업이 아니다**. manifest·receipt·복구 도구는
커밋되지만 새 clone에 과거 native 데이터가 자동으로 생기지 않는다. 기존 작은
복구 ZIP이나 과거 hash 목록만으로 폐기 자료를 복원할 수 있다고 가정하지 않는다.
새 작업의 보존 원칙은 [문서 라우터](../../README.md#로컬-실험-산출물-보존)를 따른다.

## 1차 정리 결과

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

## 1차 보존 및 경로 검증

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

## 1차 정리에서 남긴 항목과 이유

동일한 내용이라는 이유만으로 서로 다른 실행의 필수 경로를 삭제하지 않았다.
Local XY의 큰 결과 폴더에는 현재 입력 캡처가 있고, P5 default-linkage는 최신 peer audit의
입력이다. Local XY native 165개 파일은 기존 saved-output verifier의 경로 계약을 유지한다.
과거 worktree snapshot, 고유 조사 결과와 독립적으로 제거 근거를 확정하지 못한 항목도
남겼다. 남은 5.461 GB 전체가 불필요하다는 뜻도, 전부 현재 필수라는 뜻도 아니다.

각 최상위 항목의 보존 사유와 제거 수는
[검증 receipt](2026-10-12-pre-cr1-cleanup/receipt.json)에 있다. 추가 감소량을 맞추기 위해
고유 증거를 지우거나 보존 의무를 낮추지 않았다. 원본 영상과 보존 ZIP은 계속 Git 밖에
있으며 새 clone만으로 모든 과거 실험을 재현할 수 있는 것은 아니다.

## 1차 정리의 복구와 검토 경로

- [전체 시작 목록](2026-10-12-pre-cr1-cleanup/inventory.json.gz): 경로, 크기, 할당량,
  해시/링크 대상 및 시작 Git 상태. gzip 안에는 JSON만 있다.
- [삭제·복구 매핑](2026-10-12-pre-cr1-cleanup/removal-manifest.json.gz): 삭제한 파일마다
  원래 해시와 ZIP/member 또는 캐시 재생성 방법을 기록했다.
- [검증 receipt](2026-10-12-pre-cr1-cleanup/receipt.json): 사전/사후 용량, 보호 입력,
  보존 결과와 CR-1 미착수 확인. 위 두 압축 목록의 해시도 포함한다.

이 절의 ZIP/member 복원 매핑은 1차 정리 당시 기록이다. 이후 가치 심사에서
temporal-texture ZIP을 포함한 보관 묶음을 폐기했으므로 현재 복원 안내로 사용하지
않는다. 현재 생존 자료는 위 `retention.json`과
[현재 보존 자료의 선택 복원](#현재-보존-자료의-선택-복원)을 따른다. 폐기된 과거
실행을 새 영상 decode로 대체하지 않는다. 캐시는 필요할 때 Python/pytest 또는
`scripts/update_graphify_s11.sh`가 재생성할 수 있다.

다음 단계는 사용자 체크포인트 확인 후의 **4번: WP1 조건 확정과 격리 환경 준비**다.
최대 3 GB, 모델/참조 집합 하나, full/local 비교 및 미채택 시 제거라는
[실험 계약](../../20-architecture/s11-contextual-role-observation-design.md#local-footprint-and-removal-contract)은 유지한다.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F09`
- First harmful stage: no new detector investigation; this checkpoint verifies storage, selected recovery and current saved-input consumption. It does not change or resolve role/authority failures.
- Logic-map impact: NONE — storage consolidation followed by explicit value-based retirement changes availability only; production owners, source coordinates and publication behavior are unchanged.
- Failure-registry impact: NONE — tracked failure verdicts, conditions, complete comparison readouts and selected counterexamples survive. Retired native payloads are explicitly unavailable; the old hash inventory is not a backup. No new mechanism, physical label or field acceptance is claimed.
