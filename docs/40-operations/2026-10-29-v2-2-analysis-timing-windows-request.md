# Windows 요청: V2-2 분석 시간 측정 (A4) (2026-10-29)

> 이 문서는 **Windows 쪽에서 실행**하기 위한 요청이다.
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다. 요약하거나 줄을 줄이거나 직접 합계를 내지 않는다.
> - **통과 기준**은 아래 "판단 기준" 절에 있고, 실행 전에 고정됐다.
> - 결과 파일은 Windows에 남기고, 맨 아래 **결과 양식**만 텍스트로 돌려준다.

## 무엇을 확인하나

인수 기준 A4는 68분짜리 SPL#1의 분석이 **3분(180초) 안**에 끝나는 것이다.
[초안 비교 실행](../60-evidence/2026-10-29-v2-2-draft-comparison-windows-result.md)에서는
spike 방식으로 SPL#1 BASE의 context image 하나만 만드는 데 **202.1초**가 걸렸다.

V2-2의 분석 핵심을 제품 코드로 만들었다. 이번에는 그 코드로 시간을 잰다.
- 영상을 한 번 읽어 모든 Glass의 context image를 만든다. 행별 중앙값 계산을 빠른 방식으로 바꿨다.
- 배경 제거 뷰, Oil 초안, 캐시용 PNG 조각 만들기, 원본 SHA-256(별도 스레드)까지 함께 한다.
- 하드웨어 디코딩을 켰을 때와 껐을 때를 비교한다.
- 스크립트는 아무 파일도 쓰지 않는다. Recipe는 읽기만 한다.

시간 측정이라 **다른 무거운 프로그램은 닫고**, 노트북이면 **전원을 연결**한 상태에서 실행한다.

## 0. 소스 확인 [에이전트]

1. 이번에는 `main`이 아니라 **커밋 하나로 고정된 ZIP**을 받는다:
   `https://github.com/teeeeooo/oil_level_tracker/archive/f330e625c264a261225a72aaca1081331ac61902.zip`
   압축을 푼 폴더(`oil_level_tracker-f330e625…`)를 저장소 루트로 쓴다.
2. 저장소 루트에서 아래를 그대로 실행한다. 마지막 줄이 `checked=46 mismatched=0`이면 된다. `MISMATCH` 줄이 있으면 그 줄을 전부 원문으로 적는다.

```powershell
$expected = @{
  'DESIGN.md' = 'e9899fb36d24596caa04e67aaf5ce4ef593f37218e59f9cf6e8634c08a402e5e'
  'pyproject.toml' = '3890d934fa7c238ab51c2994f5c2ed44bed9f83d0067eccb085be19ac8c58b9d'
  'scripts/time_analysis.py' = '090e927e000779005cb701f8776b9908c61b207e9119e5588262567bfae3d607'
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
  'src/oil_tracker/adapters/video/context.py' = 'a894bf7a9422d2758e690bb71f2524f25d0f91508fd2ebf787cc9a99e972f8ea'
  'src/oil_tracker/adapters/video/draft.py' = '0d13e759aad12352d1e76b374d3fad6258997f0e5af40ce9dbbd7975184e3162'
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
  'src/oil_tracker/web/api.js' = 'cc3f748894bd1313a6508596a777442f2d6839ccbeea406b150e609c4284a8ec'
  'src/oil_tracker/web/app.css' = '12d0e1950eb5ff0f4bf2a5edf554c80a66f1d85201b61f5f83049c0025793db2'
  'src/oil_tracker/web/index.html' = '0a48d66011a76461af4f8fd0d86206ebd55f165b82da68fc1ac21597e6569f54'
  'src/oil_tracker/web/recipe.js' = '2f64a32e1f38ff55dc70ad9fdb79efb492483993dbd578845f42132940156902'
  'src/oil_tracker/web/tokens.css' = '21c92959535596a6ca5704387256ef047e344371998081736b2316ae91e22f9e'
  'tests/test_application_recipes.py' = '6ccd2b2c7b80a621f841544be71afa83141402cab8c7153dd8e7b22a1854d5f9'
  'tests/test_architecture.py' = '42910fb569bd010342747d081d1c0cac7aa8c9f2641af24da92a2f4ab5317288'
  'tests/test_docs_catalog.py' = 'bf999036473a5924f1ef312ab7e93e0b972819f5f6c167242a023996725fc4be'
  'tests/test_domain_recipe.py' = 'e942d210002723a8fc10f085d85aa32d655d750cdc387295e3cdb7f048f9a121'
  'tests/test_http_api.py' = 'c883161831c5360f9af9e4df22c60e939994845f07495ba042dae3fca46e0711'
  'tests/test_package.py' = '8d458fbb772dcd6a825e060c8fdcdad2eb7716a8f72ef6df8c3d437026f063f8'
  'tests/test_recipe_summary_script.py' = 'f90b3adff4b1fb43ae28ae2aead9c56c55f7dc22c09b10f8bf030e1a9598748b'
  'tests/test_storage_recipe_files.py' = 'e784cacbad6b421ef8426a448d1e9661f8c05daf7b238930a3c52a5c77a50288'
  'tests/test_time_analysis_script.py' = '9066baa0f97be9a8dc7b7674400c2f3b8b67aa34e25a7e79c1f2719894fdd662'
  'tests/test_video_context.py' = '07a493ffd997c3a7c06ccdfc79e8a3e8887da1044cbafd90db6b586fd69e8f72'
  'tests/test_video_frames.py' = 'd9f5f26130f4f6af240823c6b5e3dc5ce399688607a8a61a12230c7b4142cfeb'
  'tests/test_web_recipe_smoke.py' = '91e3747eee31875c5635ec662ea44877c3c670171c4f3dca379637b95747b61d'
  'tests/test_web_tokens.py' = 'cbb3d1c76b5be1f20f9b56c2e74837d7a69fc793c1fe767566e9da628f19234c'
}
$bad = 0
foreach ($k in $expected.Keys) {
  $h = (Get-FileHash -Algorithm SHA256 -LiteralPath $k).Hash.ToLower()
  if ($h -ne $expected[$k]) { "MISMATCH $k $h"; $bad++ }
}
"checked=$($expected.Count) mismatched=$bad"
```

## 1. 환경 [에이전트]

```powershell
py -3.14 -m venv .venv-v2
.venv-v2\Scripts\python -m pip install -e . pytest
.venv-v2\Scripts\python --version
.venv-v2\Scripts\python -m pip list | Select-String "opencv|numpy|pytest"
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
```

## 2. 테스트 (R2) [에이전트]

```powershell
.venv-v2\Scripts\python -m pytest -q
```

- 마지막 줄을 원문으로 적는다. 기대값은 `87 passed, 2 skipped`이다.
- 실패가 있으면 실패한 테스트 이름과 출력 마지막 30줄을 원문으로 적는다.

## 3. 시간 측정 [에이전트]

영상은 지난 실행과 같은 파일이다(SPL#1 `SPL#1_Heating_coldstart.mp4` 683,165,477 bytes,
SPL#4 `SPL#4_Cooling_onoff_#2.mp4` 53,165,455 bytes). Recipe는 V2-1 때 사용자가 만든 것이다.
아래 순서대로 **한 번씩** 실행하고, 각 실행의 **모든 출력 줄**(`progress` 줄 포함)을 원문으로 적는다.

```powershell
$recipes = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'OilLevelTracker\Recipes'
# T1: SPL#1, 소프트웨어 디코딩
.venv-v2\Scripts\python scripts\time_analysis.py --video "<SPL#1 영상>" --recipe "$recipes\SPL#1_test1_607bccb.recipe.json"
# T2: SPL#1, 하드웨어 디코딩 요청
.venv-v2\Scripts\python scripts\time_analysis.py --video "<SPL#1 영상>" --recipe "$recipes\SPL#1_test1_607bccb.recipe.json" --hardware
# T3: SPL#4 (Glass 2개), 소프트웨어 디코딩
.venv-v2\Scripts\python scripts\time_analysis.py --video "<SPL#4 영상>" --recipe "$recipes\SPL#4_test1_607bccb.recipe.json"
```

- 출력 줄의 뜻:
  - `pass …`: 영상을 한 번 읽는 데 든 시간과 그 내역(`grab` 디코딩, `retrieve` 프레임 꺼내기, `reduce` 행별 중앙값). `hardware_used`는 실제로 하드웨어 디코딩이 쓰였는지다.
  - `glass …`: Glass마다 context image 크기, 평균 화소값(`mean`), 배경 제거 뷰·초안·PNG 시간.
  - `analysis total`: 전체 시간. A4 한도는 180초다.
- 오류가 나면 그 출력 전체를 원문으로 적고 다음 실행으로 넘어간다.

## 판단 기준 (실행 전에 고정)

| ID | 조건 | 결정 |
|---|---|---|
| R1 | 0절 마지막 줄이 `checked=46 mismatched=0` | 소스가 맞다 |
| R2 | 2절 마지막 줄이 `87 passed, 2 skipped` | 테스트가 맞다 |
| T1 | SPL#1 소프트웨어의 `analysis total`이 **150초 이하** | 이 설계로 화면 작업을 계속한다 |
| T1 | 150초 초과 180초 이하 | 계속하되, 분석 구현(6단계)에서 더 줄일 방법을 찾는다 |
| T1 | 180초 초과 | 화면 작업 전에 먼저 속도를 더 높인다 |
| T2 | `hardware_used=True`이고, `analysis total`이 T1보다 10% 이상 짧고, Glass의 `mean`이 T1과 1.0 넘게 다르지 않다 | 하드웨어 디코딩을 기본으로 쓴다. 아니면 소프트웨어 디코딩을 쓴다 |
| T3 | 기준 없음 | Glass 2개일 때의 비용을 기록한다 |
| — | 모든 실행에서 `Traceback` 줄이 없다 | 오류가 없다 |

## 결과 양식 (이 블록만 텍스트로 돌려준다)

```
[R1] 0절 마지막 줄 = ; MISMATCH 줄 = (없음 / 원문)
[env] python = ; opencv = ; numpy = ; pytest =
[env] CPU = (Name, NumberOfCores, NumberOfLogicalProcessors 원문)
[R2] pytest 마지막 줄 = ; (실패 시 이름과 마지막 30줄)
[T1] 출력 원문:
...
[T2] 출력 원문:
...
[T3] 출력 원문:
...
[메모] = (다른 프로그램을 닫았는지, 전원 연결 여부, 그 밖에 특이한 점)
```
