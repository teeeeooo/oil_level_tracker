# Windows 요청: V2-2 Oil 초안 방식 비교 (2026-10-29)

> 이 문서는 **Windows 쪽에서 실행**하기 위한 요청이다.
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다. 요약하거나 줄을 줄이거나 직접 합계를 내지 않는다.
> - **[사용자]** 표시: 사용자가 그림을 직접 보고 판단한다.
> - **판단 기준**은 아래 "판단 기준" 절에 있고, 실행 전에 고정됐다.
> - 결과 파일은 Windows에 남기고, 맨 아래 **결과 양식**만 텍스트로 돌려준다.

## 무엇을 확인하나

V2-2에서 만들 Oil 초안이 **어떤 경계를 따라가야 하는지** 정한다. 배경은
[초안 방식 비교](../50-diagnostics/2026-10-29-draft-method-comparison.md)에 있다.
macOS의 작은 표본에서는 영상 내내 같은 높이에 있는 띠(유리 구조물로 보임)를
따라가는 방식이 많았다. 그래서 인수 기준 영상인 SPL#4와 SPL#1에서 직접 본다.

- 비교 스크립트가 Glass마다 context image 위에 네 가지 초안 선을 그린다.
- 사용자가 그림을 보고 어느 선이 오일 경계를 따라가는지 고른다.
- 제품 코드는 바꾸지 않는다. 스크립트는 문서 폴더의 Recipe를 **읽기만** 한다.
- SPL#1 BASE 하나의 context image를 만드는 시간도 함께 나온다(A4 참고값).

## 0. 소스 확인 [에이전트]

1. GitHub에서 **`main` 브랜치**의 ZIP을 새로 받는다. 압축을 푼 폴더를 저장소 루트로 쓴다.
   - 소스 기준 커밋은 `4f58ead`이다. 그 뒤의 `main` 커밋은 문서만 바꾼다.
2. 저장소 루트에서 아래를 그대로 실행한다. 마지막 줄이 `checked=25 mismatched=0`이면 된다. `MISMATCH` 줄이 있으면 그 줄을 전부 원문으로 적는다.

```powershell
$expected = @{
  'pyproject.toml' = '3890d934fa7c238ab51c2994f5c2ed44bed9f83d0067eccb085be19ac8c58b9d'
  'scripts/compare_draft_methods.py' = '3c87c76b632c69f6b418fb39d923a10d40db0d15e4add08ac149427cf0a991f7'
  'src/oil_tracker/__init__.py' = '44b73c09a8a5c67a64bc97f0b0edc9aa6779d1fa5ddefafd61d89bb0d13ca615'
  'src/oil_tracker/__main__.py' = '4efc05fc1cffa5b074068f9bd0ab3ff84b8eaba4c70edbc5ce4d806c05a1a2d1'
  'src/oil_tracker/adapters/__init__.py' = '7b5021074fb335deb08bf8e6c61147b8380361a48f164c682d754a95975ab996'
  'src/oil_tracker/adapters/desktop/__init__.py' = 'fb18660afd9644a6fb9fb2f270a347dbad89b54681b4941bbb4bba2ee8453bff'
  'src/oil_tracker/adapters/http/__init__.py' = 'b359fe08245e9086c1171d961e9c51e0575dc33b23ada7af2d087b47b38b5f47'
  'src/oil_tracker/adapters/http/api.py' = '3dd969546b35c2b5166a3ca318ee7592a094d524a4b65c201cfd5b683910db4e'
  'src/oil_tracker/adapters/http/server.py' = '9adb32c73e631a73a256fedfb4a8ad029f53a7dc608214d65388489f2c9597b7'
  'src/oil_tracker/adapters/storage/__init__.py' = '5253f99b1985be481fe2837d01fc0533ecaed8103268631c3f2a2ccb8399a4aa'
  'src/oil_tracker/adapters/storage/files.py' = '79c88a416835311279d4a3337a5b9b3b63e3b3a164497334f2adb0c1d920ecfe'
  'src/oil_tracker/adapters/storage/locations.py' = '54951aaf5cdfc94c5b9325ffe1a0017908790a85ac275f2a5c868d71262e1f0c'
  'src/oil_tracker/adapters/storage/recipe_files.py' = '0e777870d5a79ad8f21fba2d2f6f90b8f5e703f2054e17d1233309ef64f25f07'
  'src/oil_tracker/adapters/video/__init__.py' = '7499b2d549136a86fbff18ea219095c124c22d83bbd6f750df692b9fed7967c1'
  'src/oil_tracker/adapters/video/frames.py' = '57826ae57b75619ccfb976051e521842e7787f2f6cac3251b68b9dfbe3f8f4a7'
  'src/oil_tracker/app.py' = 'bf645a9d8f39652a259eeec053427ce69d1ccaf684749e2bb73f9fd6bb8e6a5b'
  'src/oil_tracker/application/__init__.py' = 'c7de6525842604180e0f82b532883bece026ac01a556d364caf4c6d7ea0d0253'
  'src/oil_tracker/application/ports.py' = 'e40a702c0f7fae794b12b7468ec5f09f7d2f1d7e7fd5cb460a9546b5d2206c14'
  'src/oil_tracker/application/recipes.py' = '8fde6b0fe2a9f05997f83729f17c9013a9ab19f74b026e1daff28043781cbb9e'
  'src/oil_tracker/application/videos.py' = '7ab81c2cd0c370081b9021a587e1bee762fd057af6f9a40807f17eb960880a46'
  'src/oil_tracker/bootstrap.py' = '0167d3ea4e4a0fa1ca07e36f5329fdab5b2e4bf062600f9aef5861f572678db3'
  'src/oil_tracker/domain/__init__.py' = '6bbe167d274a1996c8581b03b4abfa871febc6226c928aea077f1f3f8e10462e'
  'src/oil_tracker/domain/enums.py' = 'bbdd0b35161fef4b170eb39da092406719a35ba86a767b6c62aa33ab8a4c1601'
  'src/oil_tracker/domain/geometry.py' = '7c05fab4fad05cb24631eed5d0495f5824bf7cf041a3bcfccb4bf07c03118600'
  'src/oil_tracker/domain/recipe.py' = '52666104177ece65f8a978b0f9fa1aef190d39f06bd0f35071fe8f06b248ced6'
}
$bad = 0
foreach ($k in $expected.Keys) {
  $h = (Get-FileHash -Algorithm SHA256 -LiteralPath $k).Hash.ToLower()
  if ($h -ne $expected[$k]) { "MISMATCH $k $h"; $bad++ }
}
"checked=$($expected.Count) mismatched=$bad"
```

## 1. 환경 [에이전트]

새 폴더에 **새 venv**를 만든다.

```powershell
py -3.14 -m venv .venv-v2
.venv-v2\Scripts\python -m pip install -e .
.venv-v2\Scripts\python --version
.venv-v2\Scripts\python -m pip list | Select-String "opencv|numpy"
```

## 2. 실행 [에이전트]

영상은 V2-1 때와 같은 파일이다(SPL#4 `SPL#4_Cooling_onoff_#2.mp4` 53,165,455 bytes, SPL#1
`SPL#1_Heating_coldstart.mp4` 683,165,477 bytes). Recipe는 V2-1 때 사용자가 만든 것을 쓴다.

```powershell
$recipes = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'OilLevelTracker\Recipes'
Get-ChildItem $recipes -Filter *.recipe.json | Select-Object Name, Length
.venv-v2\Scripts\python scripts\compare_draft_methods.py --video "<SPL#4 영상>" --recipe "$recipes\SPL#4_test1_607bccb.recipe.json" --out draft-compare
.venv-v2\Scripts\python scripts\compare_draft_methods.py --video "<SPL#1 영상>" --recipe "$recipes\SPL#1_test1_607bccb.recipe.json" --out draft-compare
Get-ChildItem draft-compare | Select-Object Name, Length
```

- Recipe 파일 이름이 다르면, 목록에서 **Glass가 BASE·Accum인 SPL#4 Recipe**와 **BASE인 SPL#1 Recipe**를 골라 그 이름으로 실행하고, 어떤 파일을 썼는지 적는다.
- SPL#1은 영상 전체를 한 번 읽어서 몇 분 걸린다.
- 모든 출력 줄을 **원문 그대로** 적는다.

## 3. 그림 보기 [사용자]

`draft-compare` 폴더의 그림:
- `SPL#4_Cooling_onoff_#2-1-BASE.png`, `SPL#4_Cooling_onoff_#2-2-Accum.png`
- `SPL#1_Heating_coldstart-1-BASE.png` (폭 8,210 px, 확대해서 본다), `…-1-BASE-overview.png` (전체를 한눈에)

그림 한 장에 패널이 위에서부터 네 개 있다. 패널마다 같은 context image(가로 = 시간, 0.5초가 한 열 / 세로 = Glass 높이)에 선 하나가 그려져 있다.

| 패널 | 선 색 | 방식 |
|---|---|---|
| A | 보라 | spike 방식: 열마다 가장 강한 경계 |
| B | 파랑 | 동적 계획법: 가장 강한 경계를 따라 이어지는 경로 |
| D | 빨강 | 동적 계획법, **배경 제거 뷰**에서: 영상 내내 같은 높이에 있는 띠를 지운 뒤 |
| F | 청록 | 동적 계획법, **고정 띠를 약하게**: v1의 고정 구조물 표시를 흉내 |

- 회색 음영은 그 방식이 "판정 불가"로 표시한 구간이다.
- **SPL#1 BASE 참고**(v1 때 사용자 검토): 550–652초 유면이 서서히 내려감, 652–674초 회복, 674–675초 사이 FULL. 전체 그림에서 550초는 가로 1,100 px, 674초는 1,348 px 근처다. overview 그림에서는 각각 약 322 px, 394 px다.

Glass마다 **오일 경계를 가장 잘 따라가는 패널**(A / B / D / F / 없음)을 고르고, 한 줄 소감을 남긴다. 예: "D는 처음 20분 맞고 그 뒤 아래 띠로 떨어짐", "B는 내내 유리 아래쪽 띠". 회색 구간이 적절한지도 본다.

## 판단 기준 (실행 전에 고정)

| 조건 | 결정 |
|---|---|
| 0절 마지막 줄이 `checked=25 mismatched=0`이고, 세 Glass의 `glass name=` 줄이 모두 나온다 | 실행이 유효하다 |
| 한 방식이 세 Glass 모두에서 가장 낫거나 같이 가장 낫다 | 그 방식을 제품 초안의 경계로 쓴다 |
| Glass마다 가장 나은 방식이 다르다 | 사용자와 다시 정한다(예: Glass마다 고르는 설정) |
| F가 가장 낫다 | Recipe에 고정 구조물을 표시하는 기능을 다시 넣을지 사용자와 정한다(Product SSOT 변경) |
| 세 Glass 모두 "없음" | 초안 방식을 사용자와 다시 정한다 |

## 결과 양식 (이 블록만 텍스트로 돌려준다)

```
[R1] 0절 마지막 줄 = ; MISMATCH 줄 = (없음 / 원문)
[env] python = ; opencv = ; numpy =
[2] Recipe 목록 = (원문) ; 쓴 Recipe 파일 =
[2] 출력 원문:
...
[3] SPL#4 BASE: 가장 나은 것 = (A/B/D/F/없음) ; 소감 =
[3] SPL#4 Accum: 가장 나은 것 = ; 소감 =
[3] SPL#1 BASE: 가장 나은 것 = ; 소감 =
[3] 회색(판정 불가) 구간 = (적절 / 부족 / 과다) ; 소감 =
```
