# Windows 요청: V2-1 Recipe 화면 확인 (2026-10-29)

> 이 문서는 **Windows 쪽에서 실행**하기 위한 요청이다.
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다. 요약하거나 직접 합계를 내지 않는다.
> - **[사용자]** 표시: 사용자가 앱 창에서 직접 조작하고 판단한다.
> - **통과 기준 R1–R12**는 아래 "통과 기준" 절에 있고, 실행 전에 고정됐다.
> - 결과 파일은 Windows에 남기고, 맨 아래 **결과 양식**만 텍스트로 돌려준다.

## 무엇을 확인하나

V2-1의 Recipe 화면을 실제 Windows(WebView2)에서 처음 써 본다.
- Recipe 목록, 영상 열기(파일 대화상자), 프레임 넘기기와 재생;
- Glass 타원과 0선 편집(v1 방식), 판정 규칙 입력, 오류 표시;
- 저장(저장할 때 보이던 프레임이 기준 프레임), 다시 열기, 해상도가 다른 영상 거부, 폴더 열기;
- 데이터 폴더가 이 PC의 실제 문서 폴더(OneDrive로 옮겨졌으면 그 위치) 아래에 생기는지.

여기서 만드는 **SPL#4, SPL#1 Recipe는 실제 문서 폴더에 남는다.** V2-2부터 이 Recipe로 검사를 시작하므로 지우지 않는다.

## 0. 소스 확인 [에이전트]

1. GitHub에서 **`main` 브랜치**의 ZIP을 받는다. 압축을 푼 폴더를 저장소 루트로 쓴다.
   - 소스 기준 커밋은 `4ea7ade`이다. 그 뒤의 `main` 커밋은 문서만 바꾼다.
2. 저장소 루트에서 아래를 그대로 실행한다. 마지막 줄이 `checked=41 mismatched=0`이면 된다. `MISMATCH` 줄이 있으면 그 줄을 전부 원문으로 적는다.

```powershell
$expected = @{
  'pyproject.toml' = '3890d934fa7c238ab51c2994f5c2ed44bed9f83d0067eccb085be19ac8c58b9d'
  'scripts/recipe_summary.py' = '5e7e4960cfd659e1a9e887b9d0d17fd3517381b2ccd78b8e3a0f6f4968e5a8b3'
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
  'src/oil_tracker/web/api.js' = 'cc3f748894bd1313a6508596a777442f2d6839ccbeea406b150e609c4284a8ec'
  'src/oil_tracker/web/app.css' = '4436f788f74af8eea3a79cb33540fe8d7cd5a45038202735f84a1a8c96b09209'
  'src/oil_tracker/web/index.html' = 'e07fe71f8ffaa67420e7ba73a38f40ecc943febd8140f2854e8bd751c43a6507'
  'src/oil_tracker/web/recipe.js' = 'a4475d8a2d59f746d8c65c1336a03b82d7fcdd3be45b0592694a6804e94ff3d2'
  'src/oil_tracker/web/tokens.css' = '9b8eca00b9929ce4f77306b1fe8bb91d0d14fae4833742bb08543775d5b8f739'
  'tests/test_application_recipes.py' = '6ccd2b2c7b80a621f841544be71afa83141402cab8c7153dd8e7b22a1854d5f9'
  'tests/test_architecture.py' = '42910fb569bd010342747d081d1c0cac7aa8c9f2641af24da92a2f4ab5317288'
  'tests/test_docs_catalog.py' = 'bf999036473a5924f1ef312ab7e93e0b972819f5f6c167242a023996725fc4be'
  'tests/test_domain_recipe.py' = 'e942d210002723a8fc10f085d85aa32d655d750cdc387295e3cdb7f048f9a121'
  'tests/test_http_api.py' = 'c883161831c5360f9af9e4df22c60e939994845f07495ba042dae3fca46e0711'
  'tests/test_package.py' = '8d458fbb772dcd6a825e060c8fdcdad2eb7716a8f72ef6df8c3d437026f063f8'
  'tests/test_recipe_summary_script.py' = 'f90b3adff4b1fb43ae28ae2aead9c56c55f7dc22c09b10f8bf030e1a9598748b'
  'tests/test_storage_recipe_files.py' = 'e784cacbad6b421ef8426a448d1e9661f8c05daf7b238930a3c52a5c77a50288'
  'tests/test_video_frames.py' = 'd9f5f26130f4f6af240823c6b5e3dc5ce399688607a8a61a12230c7b4142cfeb'
  'tests/test_web_recipe_smoke.py' = '77e1f0d01afa8c06fde209db40fb79e6c0ef6c993fe8c2fb81b0e1ce64f705a3'
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

기존 venv와 섞지 않도록 **새 venv**를 만든다.

```powershell
py -3.14 -m venv .venv-v2
.venv-v2\Scripts\python -m pip install -e . pytest
.venv-v2\Scripts\python --version
.venv-v2\Scripts\python -m pip list | Select-String "pywebview|pythonnet|clr.loader|opencv|numpy|pytest"
```

WebView2 런타임 버전. 둘 중 값이 나오는 것을 적고, 둘 다 없으면 "없음"이라고 적는다.

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction SilentlyContinue).pv
(Get-ItemProperty 'HKCU:\Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction SilentlyContinue).pv
```

## 2. 테스트 (R2) [에이전트]

```powershell
.venv-v2\Scripts\python -m pytest -q
```

- 마지막 줄을 원문으로 적는다. 기대값은 `77 passed, 2 skipped`이다.
  - 건너뛰는 2개: 브라우저 스모크 검사(Playwright 미설치)와 macOS 전용 문서 폴더 검사.
- 실패가 있으면 실패한 테스트 이름과 출력 마지막 30줄을 원문으로 적는다.

## 3. 앱 실행 [에이전트 → 사용자]

```powershell
.venv-v2\Scripts\python -m oil_tracker
```

- 창이 열리면 **[사용자]**가 4절을 진행한다.
- **방화벽이나 보안 경고 창이 뜨면** 허용하지 말고 닫는다. 창이 떴다는 사실과 문구를 적는다.
- 창을 닫은 뒤 콘솔에 나온 줄을 **전부 원문으로** 적는다. 없으면 "없음"이라고 적는다.

## 4. 앱 창에서 직접 조작 [사용자]

영상은 지난 실행과 같은 파일이다.
- **SPL#4:** `SPL#4_Cooling_onoff_#2.mp4` (53,165,455 bytes)
- **SPL#1:** `SPL#1_Heating_coldstart.mp4`

각 항목에 **O / X**와 한 줄 소감을 남긴다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| R3 | 앱이 열리면 첫 화면 확인 | "Recipe" 목록이 보이는지. 맨 아래 "폴더" 경로 |
| R4 | "새 Recipe" → 파일 대화상자에서 SPL#4 선택 | 대화상자가 뜨는지, 첫 프레임이 보이는지 |
| R4 | 아래 막대를 끌어 넘기기, 재생(Space), 한 프레임씩(`,` `.`) | 프레임이 따라오는지 |
| R5 | "+ 추가" 두 번 → 이름을 `BASE`, `Accum`으로 | Glass 두 개가 생기는지 |
| R5 | 각 Glass를 화면의 유리에 맞추기: 손잡이 8개로 크기, 타원 안쪽 끌기로 이동, 0선은 선을 직접 위아래로 끌기, 화살표 키로 1 px(Shift 10 px), 휠 확대·Shift-드래그 이동 | 손에 맞는지. 0선이 타원 끝에서 멈추는지 |
| R5 | 각 Glass의 판정 방식과 값을 이 영상에 맞게 설정 | 방식을 바꾸면 그 방식의 칸만 보이는지 |
| R6 | "반지름 X"에 `abc` 입력 | "숫자를 입력하세요."와 위쪽 "문제 1개". 확인 후 원래 값으로 |
| R6 | 판정 방식이 "기준점 위/아래 유지"인 Glass에서 "허용 시간"에 `-1` → "저장" | "허용 시간: 0 이상이어야 합니다."가 뜨고 "문제를 고친 뒤 저장하세요."로 저장이 거부되는지. 확인 후 원래 값으로 |
| R7 | Recipe 이름을 `SPL#4 냉각`으로. 유리 윤곽이 잘 보이는 프레임으로 넘긴 뒤, **화면 아래 시각(mm:ss.s)을 적고** "저장" | "저장했습니다."가 뜨는지 |
| R9 | "목록" → 목록에서 `SPL#4 냉각` "열기" | 목록 행(이름, Glass, 프레임 크기, 수정일). 열면 저장한 기준 프레임과 Glass가 제자리에 보이는지 |
| R10 | 그 상태에서 "영상 열기" → SPL#1 선택 | 해상도가 다르면 "영상 해상도 …가 이 Recipe의 …와 다릅니다."로 거부되는지. 같으면 열린다(그때는 **저장하지 말고** "목록"으로) |
| R11 | 목록에서 "폴더 열기" | 탐색기가 Recipes 폴더로 열리는지 |
| R12 | "새 Recipe" → SPL#1 → "+ 추가" → 이름 `BASE`, 판정 방식 설정 → Recipe 이름 `SPL#1 가열` → 저장 | "저장했습니다."가 뜨는지 |

마지막으로 **전체 소감**을 한두 줄 남긴다: Glass 맞추기가 v1보다 편한지, 불편한 점.

## 5. 결과 확인 [에이전트]

앱을 닫은 뒤 실행하고, 출력을 **전부 원문으로** 적는다.

```powershell
.venv-v2\Scripts\python scripts\recipe_summary.py --video "<SPL#4 영상>" --video "<SPL#1 영상>"
[Environment]::GetFolderPath('MyDocuments')
```

## 통과 기준 (실행 전에 고정)

| ID | 통과 조건 |
|---|---|
| R1 | 0절 마지막 줄이 `checked=41 mismatched=0` |
| R2 | 2절 마지막 줄이 `77 passed, 2 skipped` |
| R3 | 창이 뜨고 목록이 보인다. 5절의 `documents=` 값이 `GetFolderPath('MyDocuments')` 값과 같고, 앱의 "폴더" 경로가 그 아래 `OilLevelTracker\Recipes`이다 |
| R4 | 파일 대화상자가 뜨고, 프레임 넘기기·재생·한 프레임 이동이 된다 |
| R5 | 사용자가 Glass 편집을 "쓸 만하다"(O)고 판단한다 |
| R6 | 두 오류 문구가 보이고, `-1`인 상태의 저장이 "문제를 고친 뒤 저장하세요."로 거부된다 |
| R7 | 5절의 `SPL#4 냉각` 줄이 `glasses=2 problems=0`이고, `source`가 SPL#4 파일 이름이며, `frame` 크기가 SPL#4 `video` 줄의 `size`와 같다 |
| R8 | 그 줄의 `t`가 R7에서 적은 시각과 0.1 s 안에서 같다 |
| R9 | 다시 연 Recipe의 기준 프레임과 Glass가 저장 전과 같은 자리에 보인다 |
| R10 | 5절 두 `video` 줄의 `size`가 다르면 거부, 같으면 열림 |
| R11 | 탐색기가 Recipes 폴더로 열린다 |
| R12 | 5절의 `SPL#1 가열` 줄이 `glasses=1 problems=0`이고, `source`가 SPL#1 파일 이름이다 |
| — | 3절 콘솔에 `Traceback` 줄이 없다 |

R1–R12가 모두 통과하면 V2-1을 닫는다. 실패한 항목은 고친 뒤 그 항목에 영향받는 것만 다시 확인한다.

## 결과 양식 (이 블록만 텍스트로 돌려준다)

```
[R1] 0절 마지막 줄 = ; MISMATCH 줄 = (없음 / 원문)
[env] python = ; pywebview = ; pythonnet = ; clr_loader = ; opencv = ; numpy = ; pytest =
[env] WebView2 = (버전 / 없음)
[R2] pytest 마지막 줄 = ; (실패 시 이름과 마지막 30줄)
[3] 방화벽/보안 창 = (없음 / 문구) ; 콘솔 줄 = (없음 / 원문)
[R3] O/X ; 앱 "폴더" 경로 =
[R4] O/X ; 소감 =
[R5] O/X ; 소감 = ; 설정한 판정 방식 = SPL#4 BASE: , SPL#4 Accum: , SPL#1 BASE:
[R6] abc = O/X ; -1 저장 거부 = O/X
[R7] 저장 = O/X ; 저장할 때 화면 시각 =
[R9] O/X
[R10] 결과 = (거부 / 열림) ; 문구 =
[R11] O/X
[R12] O/X
[소감] =
[5] 출력 원문:
...
```
