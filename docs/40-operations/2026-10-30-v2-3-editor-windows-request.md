# Windows 요청: V2-3 편집기 확인 (2026-10-30)

> 이 문서는 **Windows 워크스테이션에서 실행**하기 위한 요청이다.
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다. 요약하거나 줄을 줄이거나 직접 합계를 내지 않는다.
> - **[사용자]** 표시: 사용자가 앱 창에서 직접 조작하고 판단한다.
> - **통과 기준**은 아래 "통과 기준" 절에 있고, 실행 전에 고정됐다.
> - 결과 파일은 Windows에 남기고, 맨 아래 **결과 양식**만 텍스트로 돌려준다.

## 무엇을 확인하나

V2-3의 편집기를 실제 Windows(WebView2)에서 처음 써 본다.
- **시간 기준(A4–A6)을 이 PC에서 판정한다.** 2026-10-30부터 시간 기준은 워크스테이션에서 판정하고, 최저 사양 PC는 참고용이다(Product SSOT §2). 최저 사양 PC에서 쓴 측정 스크립트를 이 PC에서 돌린다(4절).
- **편집기(SPL#1):** 영상 재생과 멈춘 프레임, 확대·이동, 잡아끌기, 연필, 점 잇기, 범위 지우기, 판단 불가, 메모, 압축기 기동 표시, 실행 취소, 저장과 이어 하기.
- **저장하지 않은 편집:** 검사 목록으로 나갈 때와 **앱 창을 닫을 때(WinForms 확인 창)** 묻는지. macOS 테스트로는 확인할 수 없는 부분이다.
- **다시 분석과 원본 영상 경고(A9)**: 영상 사본으로 만든 새 검사로 확인한다. 원본 영상 파일은 건드리지 않는다.
- **V2-2 후속:** 분석 범위 띠의 노란색, 시각 칸의 `mm:ss.s` 표시, **검사 이름**(목록과 폴더 이름).

V2-2에서 만든 검사 3개(SPL#4 하나, SPL#1 둘)가 문서 폴더의 `OilLevelTracker\Inspections`에 있다. 그중 **SPL#1 하나만 편집한다.** 나머지는 열어 보기만 해도 되지만 저장하지 않는다. Recipe는 고치지 않는다.

시간을 재므로 **다른 무거운 프로그램은 가능하면 멈춘다.** 멈추지 못했으면 결과 양식에 적는다.

## 0. 소스 확인 [에이전트]

1. **커밋 하나로 고정된 ZIP**을 받는다:
   `https://github.com/teeeeooo/oil_level_tracker/archive/3ac76cec347e4b89fc56a9b61a8a809cfb18eeb8.zip`
   압축을 푼 폴더(`oil_level_tracker-3ac76cec…`)를 저장소 루트로 쓴다. 이전 실행의 폴더는 쓰지 않는다.
2. 저장소 루트에서 아래를 그대로 실행한다. 마지막 줄이 `checked=86 mismatched=0`이면 된다. `MISMATCH` 줄이 있으면 그 줄을 전부 원문으로 적는다.

```powershell
$expected = @{
  'DESIGN.md' = '075e695edc36acec070403003b6f41dccff7ef448f6321c347a004a4ec4c38d8'
  'pyproject.toml' = '3890d934fa7c238ab51c2994f5c2ed44bed9f83d0067eccb085be19ac8c58b9d'
  'scripts/check_docs_catalog.py' = '226a0293907b9b9b555a71d3aca5ba3b1f07369295403c3e44ee1d877efe0020'
  'scripts/compare_draft_methods.py' = '3c87c76b632c69f6b418fb39d923a10d40db0d15e4add08ac149427cf0a991f7'
  'scripts/compare_medians.py' = '947510c05253ef8081dedfac2409ca0709bc22c08bddb2dd3e0fcc8382ce6e9a'
  'scripts/inspection_summary.py' = '94741ba90dac9ddcf986c5d8ee248876f820616c39881cd1593058fd7349617b'
  'scripts/install_git_hooks.sh' = '762c1e1a4e38a99c086447b548ca071f84d29ac8e0aa0f26e8a717eb4e865008'
  'scripts/measure_editor.py' = '0991b8abf3b18ef11a58a4eb852c6868bc333c10626e87a71f706577b970ae27'
  'scripts/recipe_summary.py' = '5e7e4960cfd659e1a9e887b9d0d17fd3517381b2ccd78b8e3a0f6f4968e5a8b3'
  'scripts/time_analysis.py' = '72079e4a094f43ac97a896098eaed749628b06a7bc5e28eb1f530410506a751d'
  'src/oil_tracker/__init__.py' = '44b73c09a8a5c67a64bc97f0b0edc9aa6779d1fa5ddefafd61d89bb0d13ca615'
  'src/oil_tracker/__main__.py' = '4efc05fc1cffa5b074068f9bd0ab3ff84b8eaba4c70edbc5ce4d806c05a1a2d1'
  'src/oil_tracker/adapters/__init__.py' = '7b5021074fb335deb08bf8e6c61147b8380361a48f164c682d754a95975ab996'
  'src/oil_tracker/adapters/desktop/__init__.py' = '98138b5d7ba0b553bf97db6c4da6e2debf626e6c4bdeb7bee5333767dd1f0576'
  'src/oil_tracker/adapters/http/__init__.py' = 'b359fe08245e9086c1171d961e9c51e0575dc33b23ada7af2d087b47b38b5f47'
  'src/oil_tracker/adapters/http/api.py' = '43748d1aa069a435058bf33ae6f849bebc39bd79754ca8b98686ba386119f856'
  'src/oil_tracker/adapters/http/jobs.py' = '4b13c0d72bc1345cc0d0ab6faf40cdd029ef22526cd1f0552393c957be553f22'
  'src/oil_tracker/adapters/http/server.py' = 'c02802d3701834d14cd36eb9642fac56fdeae36bbe54f1271e8da14782658a22'
  'src/oil_tracker/adapters/storage/__init__.py' = '5253f99b1985be481fe2837d01fc0533ecaed8103268631c3f2a2ccb8399a4aa'
  'src/oil_tracker/adapters/storage/files.py' = 'bed95d9f399133b31fbc853ee64c66fc20c69edcd50aab8bcfdf8a70d2cb36cb'
  'src/oil_tracker/adapters/storage/inspection_files.py' = '1eccc9862ac6feaf620c88a7f2c9e81e003537622dc2e16de92d427eb79510bd'
  'src/oil_tracker/adapters/storage/locations.py' = '54951aaf5cdfc94c5b9325ffe1a0017908790a85ac275f2a5c868d71262e1f0c'
  'src/oil_tracker/adapters/storage/recipe_files.py' = '8d6caa3b04d4c5301083de0afe900230732c39de7f07b1d5434a29e4491ca8ab'
  'src/oil_tracker/adapters/storage/values.py' = '41e214903650422c8c6ec77281ef25cb186b39c968317c08c22caa1a7009622a'
  'src/oil_tracker/adapters/video/__init__.py' = '7499b2d549136a86fbff18ea219095c124c22d83bbd6f750df692b9fed7967c1'
  'src/oil_tracker/adapters/video/analysis.py' = 'a9c1e37eda63c9b6bea1c70f4c5c0e557b81e904849ee7a8903324cd94280f35'
  'src/oil_tracker/adapters/video/context.py' = '923c0b3ba4015186dfed950d07c542f142b12f3ad7711561be4abed4cd68f548'
  'src/oil_tracker/adapters/video/draft.py' = '645f4ddec0e9cf0460f874cd8fcddeb1304d0722adce029ca029167690ca4f16'
  'src/oil_tracker/adapters/video/frames.py' = '38357bf3f8abaf668a3e77c4a2375aad23c216667aa97733d591c6cb137fc3cb'
  'src/oil_tracker/adapters/video/trace.py' = '1c12dafee527aeafdd41f9c51d13a0f87b24fee4754dae93b428f06519dc5159'
  'src/oil_tracker/app.py' = '4465ee560f09a0e14ac27cd72ffa55d5d0879cf35bb3684a94712d46af77be46'
  'src/oil_tracker/application/__init__.py' = 'c7de6525842604180e0f82b532883bece026ac01a556d364caf4c6d7ea0d0253'
  'src/oil_tracker/application/editing.py' = 'dbd4423b9e5c8416fcd108260a967622541a6a23c04de793ca4921981181f937'
  'src/oil_tracker/application/inspections.py' = 'ff9a22824ff3ea8c418909848bc249be18003682e22c9be3d00342fb929f737c'
  'src/oil_tracker/application/ports.py' = 'a6317f495ead8617a24c687904bbb18ce5cd0d62390e8de04260641369c7a9e2'
  'src/oil_tracker/application/recipes.py' = '9053abc7acf8de6056697c71b6d5df965734fd82e5fa187936720a819e652cc7'
  'src/oil_tracker/application/videos.py' = 'cf4721b61ca1173c2867ba23bb29e2d885407940895e91a4b21f04c5fbf28ce6'
  'src/oil_tracker/bootstrap.py' = '1fdc8e4029f7a1773b2725e15bb473fdbfd25bc8532d961dfdd6ce1bf75faec9'
  'src/oil_tracker/domain/__init__.py' = '6bbe167d274a1996c8581b03b4abfa871febc6226c928aea077f1f3f8e10462e'
  'src/oil_tracker/domain/edits.py' = '4163d1c576daf74e93a6ee1ddc321a0057bf16a495fb56201a51b614eb0fffcc'
  'src/oil_tracker/domain/enums.py' = 'b1b528e36f1e9cad64038f04fff2cb45c40c14f85f1ad6c39d3f71aac0866a83'
  'src/oil_tracker/domain/geometry.py' = '7c05fab4fad05cb24631eed5d0495f5824bf7cf041a3bcfccb4bf07c03118600'
  'src/oil_tracker/domain/inspection.py' = '4a81cb5f6c598bd5dd55a2835e6b8a6a1b7248cfac7e0af4072066dae1bef560'
  'src/oil_tracker/domain/line.py' = 'a0329eb5164db3ea1db8f0a030e69d4952e11f9f7c009c1ef069c8bbcb088965'
  'src/oil_tracker/domain/problems.py' = '759fc6854d600618c43377e7193d6e604e55672d50a1844e3025758ea007c125'
  'src/oil_tracker/domain/recipe.py' = 'dd4a9a665312391f03c48799dea38c455f512aae517c08dc3d663fee0f5ff2af'
  'src/oil_tracker/web/api.js' = '5c86367d4cce1d6cd2b16c5a2768d787ed5d58158b994b01988cc3c95f8ada89'
  'src/oil_tracker/web/app.css' = 'ad5ab0646d7e90e8c22cd6c17bbcf3a8336f6083cfb3ae472be7332a1bad0f1c'
  'src/oil_tracker/web/editor.js' = 'd8ade93a3caf0c08ed2912eaffae302ec0a6cdb6d28bd3cf963b531d28e59f91'
  'src/oil_tracker/web/frame.js' = '444689064c1f583b75982ad0fec87d8264467755e9a96a56fd5ddaccb95f35dc'
  'src/oil_tracker/web/index.html' = '1371d06cf2c7c56e9ab02f25b0501322dd6833b8d8f6301db86d5acac902bf7c'
  'src/oil_tracker/web/inspections.js' = '8d194c7e46e85aa1a9973d3f2f645ea6097f80d301ad5be5195376f32edf411d'
  'src/oil_tracker/web/lines.js' = '80600153997b34bc5313cd8633ba4ffd27d36c265cc130a41405c61446f52b5d'
  'src/oil_tracker/web/main.js' = '4c4c26bb1de7e0a86fb1b4b77301366f9979f0b16e5551cab65ad427a8502137'
  'src/oil_tracker/web/nav.js' = 'f06641803602beefae7c67a473daeffa9a9b5eec63f65b7cb0829954529af267'
  'src/oil_tracker/web/player.js' = 'e4acc63b72d574d61eea175e9639f0b2cfafce437a2e2ce5261527fdb00818d3'
  'src/oil_tracker/web/recipe.js' = '40e0e357f36e8724ffc9b9bca60c3f591f344f8cc19c8f27ba35c9dd0c17b588'
  'src/oil_tracker/web/render.js' = '27280bf135b7e30e7930aa5734a384c65f4ef697754b39af2d84aedced8bb2f5'
  'src/oil_tracker/web/tokens.css' = 'dbada0057157414b04dd82e31ca33b85de506f097ba376885f234f2875242eb0'
  'src/oil_tracker/web/ui.js' = '1711ee95e43b48e79e7e6cdd34457a21fb0549d338fd28bbb1732ed458f641ce'
  'tests/test_app.py' = '51fd947f25dc46ff49d0247a08bec15cb8fc0c26db9ddac717c99776346c265f'
  'tests/test_application_editing.py' = '04f52e659da7a847595c0dc2d7f83fe3b2ad611bfbcc72733eb019469917468a'
  'tests/test_application_inspections.py' = 'ac15efb2959bde624eafb135dcad9f95285afd597030da03706bedee18e8dd4c'
  'tests/test_application_recipes.py' = '154b61e3cf6e4aa81a68e2165f51e569eb7a78889207e617b273136f1c16cde8'
  'tests/test_architecture.py' = '42910fb569bd010342747d081d1c0cac7aa8c9f2641af24da92a2f4ab5317288'
  'tests/test_compare_medians_script.py' = '3ced7c6a8096de3411be5f7fbc7db57a86ad81f531da41d3c418937b205ba119'
  'tests/test_docs_catalog.py' = 'bf999036473a5924f1ef312ab7e93e0b972819f5f6c167242a023996725fc4be'
  'tests/test_domain_edits.py' = '90fa950cad5ffe15e5939d3c2823e4df1c9ec31e3214468718b64035ba2eba30'
  'tests/test_domain_inspection.py' = '7306a9937e74a6dfecf1a2eae238f68128fba6b3545fb30e77fad317759e19aa'
  'tests/test_domain_recipe.py' = 'f916f1e77ef9f0559c7e3cee1dcab400a08dac94d1254cdefcb71dc91ad98b80'
  'tests/test_http_api.py' = '0d5b5954768462df277c4e0b825897225aaf790c41e53039894379fd95e5d434'
  'tests/test_http_jobs.py' = 'fd538c2d448228f847ac1d201b47e133026bf66c9fb104a4cc11049f724c2d33'
  'tests/test_inspection_summary_script.py' = '0e75aeb07dc40e873e07310dbfbf29ea0e9d3e3113ad6fd337889285ac4e157a'
  'tests/test_measure_editor_script.py' = '430c3960fc8e93f33b5b3dd6d3a684baf89df2768f71aca0dd211f36b65fd281'
  'tests/test_package.py' = '8d458fbb772dcd6a825e060c8fdcdad2eb7716a8f72ef6df8c3d437026f063f8'
  'tests/test_recipe_summary_script.py' = 'f90b3adff4b1fb43ae28ae2aead9c56c55f7dc22c09b10f8bf030e1a9598748b'
  'tests/test_storage_inspection_files.py' = '64ccdda4dd8ad39e845d9767ca4090077f3900100642732d6ff28e85b00d0db0'
  'tests/test_storage_recipe_files.py' = 'e784cacbad6b421ef8426a448d1e9661f8c05daf7b238930a3c52a5c77a50288'
  'tests/test_time_analysis_script.py' = '5e3659ac7b9810095eeefc14511b190e8e8eb398143f8e13b25cf463e07a1ac0'
  'tests/test_video_analysis.py' = 'ec97c4ed0d328ea42f2ae233168667cb40014decd172712cca01092f83a30d98'
  'tests/test_video_context.py' = '47115a4f03a31b3b491a136b519c9809497e3ef7289c19ec203b656ec1d6765e'
  'tests/test_video_frames.py' = '02f4c4495486e21ef5ff78ce9df8ba8334ce00d7dbc1a66e4b50f21101add21b'
  'tests/test_video_trace.py' = '8e842e92124b975a36ab6dba64fbdb06b14b6a9aeb56d4a88460ebbeb115c435'
  'tests/test_web_inspection_smoke.py' = '5ac5e3a8a6ab35f109f9e52f1a6e4356a8ecdc40fcbd9e431eb94b33824233ac'
  'tests/test_web_recipe_smoke.py' = 'b12f91f3c40feb9529c78c39409e597f56a325e53aca320818ecaaab9653bdb9'
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

이 폴더에 **새 venv 두 개**를 만든다. 앱용(`.venv-v2`)에는 Playwright를 넣지 않는다(넣으면 2절의 테스트 수가 달라진다).

```powershell
py -3.14 -m venv .venv-v2
.venv-v2\Scripts\python -m pip install -e . pytest
.venv-v2\Scripts\python --version
.venv-v2\Scripts\python -m pip list | Select-String "pywebview|pythonnet|clr.loader|opencv|numpy|pytest"
py -3.14 -m venv .venv-measure
.venv-measure\Scripts\python -m pip install opencv-python-headless==4.14.0.94 numpy==2.5.4 playwright==1.64.1
```

WebView2 런타임 버전. 둘 중 값이 나오는 것을 적고, 둘 다 없으면 "없음"이라고 적는다.

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction SilentlyContinue).pv
(Get-ItemProperty 'HKCU:\Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction SilentlyContinue).pv
```

## 2. 테스트 (S2) [에이전트]

```powershell
.venv-v2\Scripts\python -m pytest -q
```

- 마지막 줄을 원문으로 적는다. 기대값은 `198 passed, 4 skipped`이다.
  - 건너뛰는 4개: Playwright를 쓰는 검사 3개(설치하지 않음)와 macOS 전용 문서 폴더 검사.
- 실패가 있으면 실패한 테스트 이름과 출력 마지막 30줄을 원문으로 적는다.

## 3. 준비와 실행 전 검사 목록 [에이전트]

1. 영상 사본을 만든다. `<SPL#4 경로>`는 지난 실행에서 쓴 SPL#4 영상의 실제 경로로 바꾼다. **원본은 옮기거나 고치지 않는다.**

```powershell
New-Item -ItemType Directory -Force C:\olt-v23 | Out-Null
Copy-Item -LiteralPath "<SPL#4 경로>" -Destination "C:\olt-v23\SPL4_v23.mp4"
(Get-Item C:\olt-v23\SPL4_v23.mp4).Length
```

   마지막 줄이 `53165455`이면 된다.

2. 앱을 열기 전 검사 목록. 출력을 **전부 원문으로** 적는다. 읽기만 한다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
```

## 4. 시간 측정: A4·A5·A6 (M1–M3, A4, A5, A6) [에이전트]

최저 사양 PC에서 쓴 측정 스크립트를 이 PC에서 돌린다. SPL#1을 앱의 서버로 분석한 뒤, **Edge 창을 열어 편집기를 스스로 조작하며** 잰다(선 그리기, 끌기, 확대, 프레임 넘기기, 60초 재생). 마지막에 중앙값 계산 방식들을 견준다. 약 4분 걸린다.

- 측정 데이터는 이 폴더의 `a5a6-data-…`에 따로 쓴다. 문서 폴더의 검사와 Recipe는 읽기만 한다.
- 이 동안 **마우스와 키보드를 건드리지 않고**, Edge 창을 **최소화하거나 가리지 않는다.** [사용자]에게도 알린다.
- `<SPL#1 경로>`는 지난 실행의 SPL#1 영상 경로로 바꾼다. Recipe는 문서 폴더의 `OilLevelTracker\Recipes\SPL#1_test1_607bccb.recipe.json`이다(`#`이 든 경로라 큰따옴표는 그대로 둔다).

```powershell
.venv-measure\Scripts\python scripts\measure_editor.py --video "<SPL#1 경로>" --recipe "$([Environment]::GetFolderPath('MyDocuments'))\OilLevelTracker\Recipes\SPL#1_test1_607bccb.recipe.json"
```

- 끝나면 결과 표가 출력되고 `결과 파일: …\a5a6-editor-YYYYMMDD-HHMM.md`가 나온다. **그 파일의 내용 전체**를 결과 양식에 넣는다.
- 오류가 나면 스크립트가 결과 파일에 적고 끝난다. 그 파일을 그대로 넣는다.

## 5. 앱 실행 [에이전트 → 사용자]

```powershell
.venv-v2\Scripts\python -m oil_tracker
```

- 창이 열리면 **[사용자]**가 6절을 진행한다. 창은 최대화해서 쓴다.
- **방화벽이나 보안 경고 창이 뜨면** 허용하지 말고 닫는다. 창이 떴다는 사실과 문구를 적는다.
- 6.3절에서 앱을 한 번 닫고 같은 명령으로 다시 연다. **창을 닫을 때마다** 콘솔에 나온 줄을 전부 원문으로 적는다. 없으면 "없음".

## 6. 앱 창에서 직접 조작 [사용자]

각 항목에 **O / X**와 한 줄 소감을 남긴다. 키 입력은 그래프나 빈 곳을 한 번 누른 뒤에 한다(입력 칸에 커서가 있으면 키가 그 칸으로 간다). 막히면 **F1**로 도움말을 연다.

### 6.1 SPL#1 편집기 (이 검사만 편집한다)

검사 목록에서 **SPL#1 검사 두 개 중 하나**의 "열기"를 누른다. 이하 이 검사를 "SPL#1 편집 검사"라 부른다. 어느 것을 골랐는지(목록의 이름이나 만든 시각) 적는다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| E1 | 편집기가 열릴 때까지 기다린다 | 위에 그래프, 아래에 맥락 이미지, 오른쪽 위에 원본 영상(Glass 부분만, 선이 겹쳐 보임)이 뜨는지. 제목 옆 "초안 그대로". 툴바 아래 원본 영상 경고 막대가 **없는지** |
| E2 | Space로 재생, 10초쯤 보고 Space로 멈춤. `,` `.`로 한 프레임씩. 그래프의 여러 곳을 클릭 | 재생이 끊기지 않는지, 그래프의 재생 위치 선이 따라가는지. 멈춘 그림과 한 프레임 이동, 클릭한 시각의 그림이 바로바로 바뀌는지(느리면 느낌을 적는다) |
| E3 | 휠로 확대·축소, Shift+휠로 높이 확대, `H`(이동) 또는 Shift+끌기로 옮기기. 시간축 양 끝 숫자를 클릭해 `10:00`, `15:00` 입력. `N`으로 다음 빈 구간. "배경 제거 보기" 켰다 끄기 | 그래프와 맥락 이미지가 함께 움직이는지. 입력한 범위가 보이는지. 빈 구간으로 가는지(없으면 "뒤에 빈 구간이 없습니다.") |
| E4 | `G`(잡아끌기)로 Oil 선을 위아래로 끈다. **Alt**를 누른 채 한 번 더. `[` `]`로 끌기 폭 바꾸기. `S`로 스냅 끄고 끌어 보고 다시 켜기 | 선이 부드럽게 따라오는지, Alt로는 잡은 곳이 뾰족하게 꺾이는지. 끄는 동안 끊기거나 늦지 않은지 |
| E5 | `P`(연필). 오른쪽 "그릴 선"을 Oil로 두고 짧게 그린다. "그릴 선"을 **Foam**으로 바꿔 한 구간, **참조**로 바꿔 한 구간 그린다 | 그린 대로 선이 바뀌는지. Foam(주황)과 참조(점선)가 새로 생기는지 |
| E6 | "그릴 선"을 Oil로 되돌리고 `L`(점 잇기). 맥락 이미지에 점 하나, **그래프에** 점 하나를 찍는다. 포인터를 움직여 본다. `Backspace`로 마지막 점을 빼고 다시 찍은 뒤 `Enter` | 점 사이가 경계를 따라 점선으로 이어지는지, 포인터 쪽 미리 보기가 따라오는지. Enter 뒤 Oil 선이 그 구간에서 바뀌는지. 오른쪽에 "점 잇기 점 N개 · Oil" |
| E7 | `R`(범위)로 그래프를 가로로 끌어 몇 초를 고르고 `Delete`. 다른 곳을 골라 `U`. 그 범위의 일부를 다시 골라 "판단 불가 풀기" | Delete한 곳의 Oil 선이 사라지고 시간축 위에 빈 구간 막대, 오른쪽 "빈 구간"에 개수. U로 빗금이 생기고, 풀기로 고른 만큼 지워지는지 |
| E8 | `M`(메모)로 그래프를 클릭해 메모를 쓰고 "확인". 생긴 번호 핀을 클릭해 고치기 | 번호 핀과 오른쪽 메모 목록에 보이는지. 고친 내용이 반영되는지 |
| E9 | `G`로 그래프의 "기동" 점선을 좌우로 끈다 | 끌리는지. 오른쪽 "분석"의 압축기 기동에 "(설정 …에서 옮김)" |
| E10 | `Ctrl+Z` 여러 번, `Ctrl+Shift+Z` 여러 번 | 방금 한 편집들이 하나씩 되돌려지고 다시 되는지. 마지막에는 모든 편집이 되살아난 상태로 둔다 |
| E11 | (기록만) | 편집 반응 전체 느낌: 끌기, 연필, 점 잇기가 손을 따라오는지 |
| E12 | `Ctrl+S` | 제목 옆이 "저장함 HH:MM"으로 바뀌는지 |

### 6.2 저장하지 않은 편집

| ID | 할 일 | 볼 것 |
|---|---|---|
| E13 | Oil 선을 조금 끌고 "← 검사 목록" | "저장하지 않은 편집이 있습니다. 저장하지 않고 나갈까요?"가 뜨는지. **취소**하면 편집기에 남는지 |
| E14 | 그대로 **앱 창의 X**를 누른다 | Windows 확인 창에 "저장하지 않은 편집이 있습니다. 저장하지 않고 닫을까요?"가 뜨는지. 단추 이름을 적는다. **취소**(또는 "아니오")를 누르면 창이 그대로인지 |
| E15 | `Ctrl+S` 뒤 다시 **X** | 묻지 않고 닫히는지. 콘솔 줄을 적는다(5절) |

### 6.3 이어 하기

| ID | 할 일 | 볼 것 |
|---|---|---|
| E16 | 5절 명령으로 앱을 다시 열고 SPL#1 편집 검사를 "열기" | 제목 옆 "저장함 …". 6.1의 편집(Foam·참조 선, 점 잇기, 빈 구간, 빗금, 메모 핀, 옮긴 기동)이 그대로인지 |
| E17 | "← 검사 목록" | 묻지 않고 목록으로 가는지 |

### 6.4 새 검사: 이름, 다시 분석, 원본 경고 (V2-2 후속, A9)

영상은 3절에서 만든 사본 `C:\olt-v23\SPL4_v23.mp4`이다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| N1 | "새 검사" → `C:\olt-v23\SPL4_v23.mp4` → `SPL#4_test1_607bccb` → "다음" | 아래 막대의 분석 범위 띠가 **노란색**인지 |
| N2 | 분석 범위 시작 칸에 `10` 입력 후 Enter | 칸이 `00:10.0`으로 바뀌는지. 확인 후 `0`을 입력해 되돌린다(`00:00.0`) |
| N3 | 오른쪽 "검사 이름"에 `V2-3 확인` 입력. 00:20 근처에서 기동 시각 "지금". "분석 시작" | 분석이 끝나고 편집기가 열리는지. 제목이 `V2-3 확인`인지 |
| N4 | `R`로 **03:50–04:10** 근처를 골라 `Delete`, `Ctrl+S`. **이 검사에서는 이 편집만 한다** | 빈 구간이 생기고 "저장함" |
| N5 | 오른쪽 "분석"의 "범위 바꿔 다시 분석…" | 분석 설정이 열리고 왼쪽 위가 "← 편집기", 단추가 "다시 분석"인지 |
| N6 | 끝 칸에 `3:30` 입력 후 Enter | 칸이 `03:30.0`이 되고, "다시 분석하면 새 범위 밖의 편집이 사라집니다: Oil 샘플 N개."가 보이는지(N을 적는다) |
| N7 | "다시 분석" | 같은 문구로 묻는 창이 뜨는지. **확인**하면 분석 뒤 편집기가 다시 열리고, 그래프가 03:30에서 끝나는지 |
| N8 | "← 검사 목록" | 목록에 `V2-3 확인`이 이름으로 보이는지 |
| N9 | [에이전트]에게 사본 이름 바꾸기를 요청한다(아래). 바뀐 뒤 `V2-3 확인`을 "열기" | 툴바 아래에 "원본 영상을 찾을 수 없습니다: C:\olt-v23\SPL4_v23.mp4" 막대가 뜨는지(영상 칸에 오류가 떠도 된다) |
| N10 | [에이전트]에게 이름 되돌리기를 요청한다. 되돌린 뒤 막대의 "다시 확인" | 몇 초 안에 막대가 사라지는지 |
| N11 | "← 검사 목록" → "폴더 열기" | 탐색기의 `Inspections` 안에 `V2-3 확인` 폴더가 있는지 |

N9, N10에서 [에이전트]가 실행한다(앱은 열어 둔 채로):

```powershell
Rename-Item -LiteralPath C:\olt-v23\SPL4_v23.mp4 -NewName SPL4_v23_hidden.mp4
```

```powershell
Rename-Item -LiteralPath C:\olt-v23\SPL4_v23_hidden.mp4 -NewName SPL4_v23.mp4
```

마지막으로 **전체 소감**을 한두 줄 남긴다: 편집기에서 불편한 점, 찾기 어려웠던 도구나 키.

## 7. 결과 확인 [에이전트]

앱을 닫은 뒤 실행하고, 출력을 **전부 원문으로** 적는다. SPL#1의 SHA-256을 다시 계산하므로 몇 초 걸린다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
```

- `edits` 줄: `oil=`, `foam=`, `reference=`는 그 선의 샘플 수를 `초안/고침/그림/빈 샘플` 순서로 센 것이다.

## 통과 기준 (실행 전에 고정)

| ID | 통과 조건 |
|---|---|
| S1 | 0절 마지막 줄이 `checked=86 mismatched=0` |
| S2 | 2절 마지막 줄이 `198 passed, 4 skipped` |
| M1 | 4절 결과 파일의 소스 줄이 `source=4f9cb83ac6d9 files=54` |
| M2 | 4절의 CPU가 이 워크스테이션(AMD Ryzen Threadripper PRO 7945WX) |
| M3 | 4절 분석 줄에 `샘플 8210개` |
| A4 | 4절 분석(앱 서버로) 시간이 **180초 이하** |
| A5 | 4절 A5 표 **전체** 줄의 중앙값이 **16ms 이하**, 최대가 **50ms 이하** |
| A6-s | 4절 정확한 프레임(서버) 중앙값이 **100ms 이하** |
| A6-p | 4절 재생 방식이 `<video>`이고, 진행이 60초 중 **59.0초 이상**, waiting·stalled **0**, 버린 프레임이 전체의 **1% 이하** |
| E | 6.1–6.3의 E1–E17이 모두 O. E11은 기록만 한다 |
| E14 | 특히 앱 창의 X에 Windows 확인 창이 뜨고, 취소하면 창이 남으며, 저장한 뒤에는 묻지 않고 닫힌다 |
| N | 6.4의 N1–N11이 모두 O |
| R1 | 7절이 `unreadable=0`이고, `inspections=`가 3절 값 **+ 1**이다 |
| R2 | 7절에서 SPL#1 편집 검사의 `edits saved_at=` 줄이 있고 `compressor=`가 그 검사의 설정(`inspection` 줄의 `compressor=`)과 다르다. 그 `edits glass` 줄에서 `oil`의 고침·그림이 모두 1 이상, `foam`과 `reference`의 그림이 1 이상, `cannot_judge`가 1 이상, `memos`가 1 이상 |
| R3 | 7절에서 `V2-3 확인` 검사가 `folder="V2-3 확인" name="V2-3 확인"`, `state=ANALYSED`, `range=0.0-210.0`, `partial=no`, `sha256_check=same`이다. 그 `edits` 줄의 `times=`가 `analysis` 줄의 `times=`와 같고, 두 Glass 모두 `oil`의 고침이 **0**이다(새 범위 밖의 편집은 사라졌다) |
| R4 | 7절에서 나머지 V2-2 검사 두 개가 `edits none`이고 `sha256_check=same`이다 |
| — | 5절 콘솔에 `Traceback` 줄이 없다 |

- **A4·A5·A6의 판정은 4절(Edge)로 한다.** 앱 창(WebView2)은 같은 엔진이다. 패키지된 앱으로 하는 최종 판정은 V2-5에서 한다. E2와 E11은 앱 창에서 본 느낌으로 기록한다.
- 4절의 `A4: 중앙값 비교` 표는 기록만 한다.
- 모두 통과하면 V2-3을 닫는다. 실패한 항목은 고친 뒤 그 항목에 영향받는 것만 다시 확인한다.

## 결과 양식 (이 블록만 텍스트로 돌려준다)

```
[S1] 0절 마지막 줄 = ; MISMATCH 줄 = (없음 / 원문)
[env] python = ; pywebview = ; pythonnet = ; clr_loader = ; opencv = ; numpy = ; pytest =
[env] WebView2 = (버전 / 없음) ; 멈추지 못한 무거운 작업 = (없음 / 내용)
[S2] pytest 마지막 줄 = ; (실패 시 이름과 마지막 30줄)
[3] 사본 크기 줄 =
[3] 검사 목록 출력 원문:
...
[4] 측정 결과 파일 내용 전체:
...
[5] 방화벽/보안 창 = (없음 / 문구) ; 첫 번째 닫을 때 콘솔 줄 = (없음 / 원문) ; 두 번째 닫을 때 콘솔 줄 = (없음 / 원문)
[6.1] 고른 SPL#1 검사 =
[E1] O/X ; 소감 =
[E2] O/X ; 소감 =
[E3] O/X ; 소감 =
[E4] O/X ; 소감 =
[E5] O/X ; 소감 =
[E6] O/X ; 소감 =
[E7] O/X ; 소감 =
[E8] O/X ; 소감 =
[E9] O/X ; 소감 =
[E10] O/X ; 소감 =
[E11] 편집 반응 소감 =
[E12] O/X
[E13] O/X
[E14] O/X ; 확인 창 문구 = ; 단추 이름 =
[E15] O/X
[E16] O/X ; 소감 =
[E17] O/X
[N1] O/X
[N2] O/X
[N3] O/X
[N4] O/X
[N5] O/X
[N6] O/X ; 문구의 N =
[N7] O/X
[N8] O/X
[N9] O/X ; 막대 문구 =
[N10] O/X
[N11] O/X
[소감] =
[7] 검사 목록 출력 원문:
...
```
