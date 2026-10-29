# Docs — 폴더별 최초 Git 등록일순 색인

최초 Git 추가일(KST) 오름차순이며, 같은 날은 파일명 순입니다. 이동한 파일은 원래 추가일을
유지합니다. 이 목록은 탐색용 파생 자료이며 현재 상태나 권한을 소유하지 않습니다.
규칙은 [문서 지도](README.md#dates-and-the-catalog)가 소유하고,
[`scripts/check_docs_catalog.py`](../scripts/check_docs_catalog.py)가 pre-push에서 누락을 검사합니다.

## docs/

| 최초 Git 등록일 (KST) | 문서 | 역할 |
|---|---|---|
| 2026-10-28 | [README.md](README.md) | 문서 지도·권한 |
| 2026-10-28 | [catalog-by-created-date.md](catalog-by-created-date.md) | 이 색인 |

## docs/00-project/

| 최초 Git 등록일 (KST) | 문서 | 역할 |
|---|---|---|
| 2026-10-28 | [execution-policy.md](00-project/execution-policy.md) | 검증·Windows 실행·게시·종료 규칙 |
| 2026-10-28 | [recall-index.md](00-project/recall-index.md) | 과거 결정·v1 자료 경로 |
| 2026-10-28 | [roadmap.md](00-project/roadmap.md) | 마일스톤 순서·상태 |
| 2026-10-28 (`31229b7`) | [work-plan.md](00-project/work-plan.md) | 현재 단계·다음 행동 |

## docs/10-product/

| 최초 Git 등록일 (KST) | 문서 | 역할 |
|---|---|---|
| 2026-10-28 (`31229b7`) | [product.md](10-product/product.md) | Product SSOT: 목표·인수 기준·결정 |

## docs/20-architecture/

| 최초 Git 등록일 (KST) | 문서 | 역할 |
|---|---|---|
| 2026-10-28 | [architecture.md](20-architecture/architecture.md) | 모듈 경계·의존 규칙 |
| 2026-10-29 | [recipe-file.md](20-architecture/recipe-file.md) | Recipe 파일 형식·위치 |
| 2026-10-29 | [inspection-folder.md](20-architecture/inspection-folder.md) | 검사 폴더·분석 캐시 형식 |

## docs/40-operations/

| 최초 Git 등록일 (KST) | 문서 | 역할 |
|---|---|---|
| 2026-10-29 | [2026-10-29-v2-1-recipe-windows-request.md](40-operations/2026-10-29-v2-1-recipe-windows-request.md) | V2-1 Recipe 화면 Windows 확인 요청 |
| 2026-10-29 | [2026-10-29-v2-2-draft-comparison-windows-request.md](40-operations/2026-10-29-v2-2-draft-comparison-windows-request.md) | V2-2 Oil 초안 방식 비교 Windows 요청(SPL#4, SPL#1) |
| 2026-10-29 | [2026-10-29-v2-2-analysis-timing-windows-request.md](40-operations/2026-10-29-v2-2-analysis-timing-windows-request.md) | V2-2 분석 시간 측정(A4) Windows 요청 |
| 2026-10-29 | [2026-10-29-v2-2-slowest-pc-timing-windows-request.md](40-operations/2026-10-29-v2-2-slowest-pc-timing-windows-request.md) | V2-2 최저 사양 PC 분석 시간(A4) 측정 요청(사용자 터미널 실행) |

## docs/50-diagnostics/

| 최초 Git 등록일 (KST) | 문서 | 역할 |
|---|---|---|
| 2026-10-29 | [2026-10-29-draft-method-comparison.md](50-diagnostics/2026-10-29-draft-method-comparison.md) | V2-2 Oil 초안 방식 비교(spike 방식 대 동적 계획법) |

## docs/60-evidence/

| 최초 Git 등록일 (KST) | 문서 | 역할 |
|---|---|---|
| 2026-10-29 | [2026-10-29-v2-1-recipe-windows-result.md](60-evidence/2026-10-29-v2-1-recipe-windows-result.md) | V2-1 Recipe 화면 Windows 결과 판정 |
| 2026-10-29 | [2026-10-29-v2-2-analysis-timing-windows-result.md](60-evidence/2026-10-29-v2-2-analysis-timing-windows-result.md) | V2-2 분석 시간(A4) Windows 결과 판정 |
| 2026-10-29 | [2026-10-29-v2-2-draft-comparison-windows-result.md](60-evidence/2026-10-29-v2-2-draft-comparison-windows-result.md) | V2-2 Oil 초안 방식 비교 Windows 결과 |
| 2026-10-29 | [2026-10-29-v2-2-slowest-pc-timing-windows-result.md](60-evidence/2026-10-29-v2-2-slowest-pc-timing-windows-result.md) | V2-2 최저 사양 PC 분석 시간(A4) 결과 판정 |
