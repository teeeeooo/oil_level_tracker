# Windows 요청: V2-5 재확인 — 선택 도구, 고른 선 지우기, FULL/EMPTY (2026-11-02)

> 이 문서는 **Windows 워크스테이션에서 실행**하기 위한 요청이다(최저 사양 PC는 이번에 하지 않는다).
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다. 요약하거나 줄을 줄이거나 직접 합계를 내지 않는다.
> - **[사용자]** 표시: 사용자가 빌드한 앱 창에서 직접 조작하고 판단한다.
> - **통과 기준**은 아래 "통과 기준" 절에 있고, 실행 전에 고정됐다. 판정은 이 문서를 만든 쪽이 한다.
> - 결과 파일은 Windows에 남기고, 맨 아래 **결과 양식**만 텍스트로 돌려준다.

## 무엇을 확인하나

V2-5 워크스테이션 실행 뒤 사용자가 첫 버전에 넣기로 한 것(Product SSOT §6, 2026-11-02)을 **새 빌드**로 본다. 코드가 바뀌었으므로 빌드와 A4–A6 측정도 다시 한다.

- **선택 도구 (V):** 편집기를 열면 켜져 있는 기본 도구다. 클릭하면 그 시각으로 가고(원본 영상이 그 프레임), 선을 클릭하면 끊김 없이 이어진 선이 골라진다. 끌어도 아무것도 바뀌지 않는다.
- **고른 선 지우기:** Delete는 고른 선(Oil, Foam, 참조)을 지운다. 범위 도구로 고른 범위가 남아 있으면 범위 안만, 없으면 이어진 선 전체.
- **FULL/EMPTY:** 연필·점 잇기·잡아끌기로 Glass 맨 위나 맨 아래에서 화면 6 px 안을 그리면 정확히 맨 위/맨 아래에 붙는다(붙는 동안 그 가장자리가 파랗게, "FULL에 붙음"/"EMPTY에 붙음"). 범위 칸의 **FULL로 / EMPTY로**는 범위 안 Oil을 한 번에 맨 위/맨 아래로 그린다.
- **해상도 거절 문구:** "영상 해상도(1280×720)가 이 Recipe의 해상도(1920×1080)와 다릅니다."로 바뀌었다.
- **보고서 머리글(압축기 모델, 시험 종류):** 편집기에는 칸이 없다. 분석 설정에서 넣고, **"제출" 창에서 확인하고 고친다**(지난 요청서의 "검사 정보에"는 틀린 안내였다). 이번에는 제출하지 않는다.

새 검사 하나(`V25b 선택 확인`)를 만들어 쓴다. **어디서도 "제출"을 누르지 않는다.** 기존 검사 6개는 열지 않는다.

## 0. 소스 확인 [에이전트]

1. **커밋 하나로 고정된 ZIP**을 받는다:
   `https://github.com/teeeeooo/oil_level_tracker/archive/8448e79322f9172a62d6ff92b4f448918e9bca08.zip`
   **새 폴더**에 압축을 풀고(`oil_level_tracker-8448e79…`) 그 폴더를 저장소 루트로 쓴다.
2. 저장소 루트에서 아래를 그대로 실행한다. 마지막 줄이 `checked=108 mismatched=0`이면 된다. `MISMATCH` 줄이 있으면 그 줄을 전부 원문으로 적는다.

```powershell
$expected = @{
  'DESIGN.md' = '6e6dbb70689e554b4f86da64b976857e77c962ff60d9ef2eb6237e650a9bf169'
  'packaging/OilLevelTracker.ico' = 'ca5077a6396176d41ee30d17c461803b2195fb6346b930341aa4765dd24537e1'
  'packaging/OilLevelTracker.spec' = '2c229402696c64f969b9b9a9106e4c2e62c3d5e08e94e3127b5471baf29529b2'
  'packaging/app-icon-small.svg' = 'a97b844336ca10a2b02fe334a0fed0653f5b514a6973cb61368bca45e6c91dff'
  'packaging/app-icon.svg' = '8bab7f0688c6a330a0c5128ec4e1fbabd849d2c55ed30a1ff15394ad28641ad5'
  'pyproject.toml' = '4c17276234891f16b770b47aa2847bafc4a4d667f5756fb573ccb571d1e0ea30'
  'scripts/build_package.py' = '20313b4f0744e463747d7d2c33f2aa08b614a04a5357002b23f402d6b618017b'
  'scripts/check_docs_catalog.py' = '226a0293907b9b9b555a71d3aca5ba3b1f07369295403c3e44ee1d877efe0020'
  'scripts/compare_draft_methods.py' = '3c87c76b632c69f6b418fb39d923a10d40db0d15e4add08ac149427cf0a991f7'
  'scripts/compare_medians.py' = '947510c05253ef8081dedfac2409ca0709bc22c08bddb2dd3e0fcc8382ce6e9a'
  'scripts/inspection_summary.py' = '97fcb09ec75385f2f742ff7cdf56d6039fc3731accafaacdd0087fc6c0925318'
  'scripts/install_git_hooks.sh' = '762c1e1a4e38a99c086447b548ca071f84d29ac8e0aa0f26e8a717eb4e865008'
  'scripts/make_icon.py' = '5e7f29d28acdd8270f9892c727a60c12dc92e99e72dc10c4da354eae0649e5c4'
  'scripts/measure_editor.py' = '3436a7dab0dc9c5d56f5f7022e9e21d56b78c0b492fb39081b96c9dfc4c2e740'
  'scripts/recipe_summary.py' = '5e7e4960cfd659e1a9e887b9d0d17fd3517381b2ccd78b8e3a0f6f4968e5a8b3'
  'scripts/time_analysis.py' = '72079e4a094f43ac97a896098eaed749628b06a7bc5e28eb1f530410506a751d'
  'src/oil_tracker/__init__.py' = '44b73c09a8a5c67a64bc97f0b0edc9aa6779d1fa5ddefafd61d89bb0d13ca615'
  'src/oil_tracker/__main__.py' = '4efc05fc1cffa5b074068f9bd0ab3ff84b8eaba4c70edbc5ce4d806c05a1a2d1'
  'src/oil_tracker/adapters/__init__.py' = '7b5021074fb335deb08bf8e6c61147b8380361a48f164c682d754a95975ab996'
  'src/oil_tracker/adapters/desktop/__init__.py' = '7eac15b6dc58008bfd5d1baaf133bda0cddec43805746e7ca4b3f76917b84b00'
  'src/oil_tracker/adapters/http/__init__.py' = 'b359fe08245e9086c1171d961e9c51e0575dc33b23ada7af2d087b47b38b5f47'
  'src/oil_tracker/adapters/http/api.py' = '2b78ad999eca0e89f506e6e3b896a5948367f966e81fba7c62d95af7ea1ea84b'
  'src/oil_tracker/adapters/http/jobs.py' = '4b13c0d72bc1345cc0d0ab6faf40cdd029ef22526cd1f0552393c957be553f22'
  'src/oil_tracker/adapters/http/relay.py' = '0cd42f7243965b803cb34be95ee9249315332428dad509a59464f2733b1209f0'
  'src/oil_tracker/adapters/http/server.py' = '0b951a1dd7e7799ccca739951e65e0e22cda40751b548ecdffbb13fcc9275234'
  'src/oil_tracker/adapters/report/__init__.py' = '3cc2afd7bd84ce88e75fdeb6d4671f4304ae23a7b7101c70cc9cf6ac68ee76c3'
  'src/oil_tracker/adapters/storage/__init__.py' = '5253f99b1985be481fe2837d01fc0533ecaed8103268631c3f2a2ccb8399a4aa'
  'src/oil_tracker/adapters/storage/files.py' = 'bed95d9f399133b31fbc853ee64c66fc20c69edcd50aab8bcfdf8a70d2cb36cb'
  'src/oil_tracker/adapters/storage/inspection_files.py' = 'bb858a665e3a79eb96fa2d472cbbc6dc0fd5f81ed53c648502c01d658f653340'
  'src/oil_tracker/adapters/storage/locations.py' = '6d0760ad86754972d583d1f673b2e6c5bdefa2ee839b5c702a562d5fb38ff11a'
  'src/oil_tracker/adapters/storage/recipe_files.py' = '8d6caa3b04d4c5301083de0afe900230732c39de7f07b1d5434a29e4491ca8ab'
  'src/oil_tracker/adapters/storage/values.py' = '41e214903650422c8c6ec77281ef25cb186b39c968317c08c22caa1a7009622a'
  'src/oil_tracker/adapters/video/__init__.py' = '7499b2d549136a86fbff18ea219095c124c22d83bbd6f750df692b9fed7967c1'
  'src/oil_tracker/adapters/video/analysis.py' = 'a9c1e37eda63c9b6bea1c70f4c5c0e557b81e904849ee7a8903324cd94280f35'
  'src/oil_tracker/adapters/video/context.py' = '923c0b3ba4015186dfed950d07c542f142b12f3ad7711561be4abed4cd68f548'
  'src/oil_tracker/adapters/video/draft.py' = '6de7034bf07c9fda6854a2941875217f4f7f3412db16a924ee9a36c4e5fb4532'
  'src/oil_tracker/adapters/video/frames.py' = '38357bf3f8abaf668a3e77c4a2375aad23c216667aa97733d591c6cb137fc3cb'
  'src/oil_tracker/adapters/video/trace.py' = '56df0c7552993c40ba4913706cc49de5318675af64f1b7f0db49105f5d1e4a27'
  'src/oil_tracker/app.py' = '688a77df18d7b8121147c25ed57ce0ef1392ccd7cee656288f2d4a832d5c4f6a'
  'src/oil_tracker/application/__init__.py' = 'c7de6525842604180e0f82b532883bece026ac01a556d364caf4c6d7ea0d0253'
  'src/oil_tracker/application/editing.py' = '90dc434dfb8742aadc5d448a5503c78c439fc50852c634bab6a80c7a882e9844'
  'src/oil_tracker/application/inspections.py' = '12aabd7c926d47021dbbbbbab91ff6693d7eb9f354ba34eee6b20e54e431d573'
  'src/oil_tracker/application/ports.py' = '372542fb3603a7598cda7e407ca9622c63fa3fc62f9f74c4562bb82fa068dd72'
  'src/oil_tracker/application/recipes.py' = '9053abc7acf8de6056697c71b6d5df965734fd82e5fa187936720a819e652cc7'
  'src/oil_tracker/application/videos.py' = 'cf4721b61ca1173c2867ba23bb29e2d885407940895e91a4b21f04c5fbf28ce6'
  'src/oil_tracker/bootstrap.py' = '80a00111bf0c332ec1eb9e78c5850da1ce44726b6f6be7af3b3827939348ce77'
  'src/oil_tracker/domain/__init__.py' = '6bbe167d274a1996c8581b03b4abfa871febc6226c928aea077f1f3f8e10462e'
  'src/oil_tracker/domain/edits.py' = '569066c8cf5f6e35a58e136ae938986fa6cec5e92d26577a079e2e32c135f73c'
  'src/oil_tracker/domain/enums.py' = '3a11b6382ec2db380c02c518f348c233a46d1801f2d02c7fb99a88a9987cd014'
  'src/oil_tracker/domain/geometry.py' = '7c05fab4fad05cb24631eed5d0495f5824bf7cf041a3bcfccb4bf07c03118600'
  'src/oil_tracker/domain/inspection.py' = 'c780c501bc39071cd9751d8c350732a8de24cfa46d562357e163ecf4591193a9'
  'src/oil_tracker/domain/judgment.py' = '043691e8d99fc6ff46152779669102e4d890583ad46e0f5bc2e61f4e2dff5076'
  'src/oil_tracker/domain/line.py' = 'a0329eb5164db3ea1db8f0a030e69d4952e11f9f7c009c1ef069c8bbcb088965'
  'src/oil_tracker/domain/problems.py' = '759fc6854d600618c43377e7193d6e604e55672d50a1844e3025758ea007c125'
  'src/oil_tracker/domain/recipe.py' = 'dfb2552237414e16dc6aaca8dc11400f8588398cf6f59c2e7f4351b3a9d0b0d4'
  'src/oil_tracker/domain/version.py' = 'dbddebb985f4fbb96733bfacba617493973ecc8238665dd9f3d06d7d3e5bbd03'
  'src/oil_tracker/web/api.js' = '2978dc60221d35c03733e282b2b36790bb8e5f3a4ec7fe3c3fa4c2126e745bc1'
  'src/oil_tracker/web/app.css' = 'e3bc27579833fe86de57c3e1aed245470634142aa43796ad5ce937dc40f2417b'
  'src/oil_tracker/web/editor.js' = '34af7657c83f1db5a9d3344a5115eda29562855fbc289f1125c5b9d054be63a3'
  'src/oil_tracker/web/frame.js' = '444689064c1f583b75982ad0fec87d8264467755e9a96a56fd5ddaccb95f35dc'
  'src/oil_tracker/web/header.js' = '7c4ed7fdf6c80479372c0596c3357e699e8bae232fdb2f164665f7e025c96728'
  'src/oil_tracker/web/index.html' = 'e3753f6a5e66e3dae26ac069e3905a766555046ea447cfcadbc2f376a9aed4d9'
  'src/oil_tracker/web/inspections.js' = 'ef71c9db77d26facb587957d0db164d6bce57a1eccaaf80f2cfc14aacea1b634'
  'src/oil_tracker/web/lines.js' = '365ca0249a01c0c208bfb3487f58b911534e565321e43ce8e146924d35ad4663'
  'src/oil_tracker/web/main.js' = '4c4c26bb1de7e0a86fb1b4b77301366f9979f0b16e5551cab65ad427a8502137'
  'src/oil_tracker/web/nav.js' = 'f06641803602beefae7c67a473daeffa9a9b5eec63f65b7cb0829954529af267'
  'src/oil_tracker/web/player.js' = '74474ce590909371763014cde673f8fc30eb4a517e2fe0e01e5c3b716c060949'
  'src/oil_tracker/web/recipe.js' = '40e0e357f36e8724ffc9b9bca60c3f591f344f8cc19c8f27ba35c9dd0c17b588'
  'src/oil_tracker/web/render.js' = '938ae6eb5045355845c9290c488e2913e4bbc69fef5997abcd3e664b45228114'
  'src/oil_tracker/web/report.css' = '9f7bfbfad83a580c29e0b80d6917be2542fa6156c1f40d85a5d8f1da545638fe'
  'src/oil_tracker/web/report.html' = '7c35a771ac347ecbb5ae169e538f77ae5de69f23b33859eca9d4d5a42a929213'
  'src/oil_tracker/web/report.js' = 'dcc9d066de87e59008376d56fc7318b65a5d8c4188eea2c0c14cd6ebaaaf98dc'
  'src/oil_tracker/web/tokens.css' = 'b62496aefa7cb8b269d0ff1fb502fc80594c4f436c4b10f2f0ea28fb28af51c0'
  'src/oil_tracker/web/ui.js' = '1711ee95e43b48e79e7e6cdd34457a21fb0549d338fd28bbb1732ed458f641ce'
  'src/oil_tracker/web/video-window.js' = '8df13fd7143b17687188f899695f061d94c3209a2ef68e43dbc893ff920136f3'
  'src/oil_tracker/web/video.html' = 'd96e42745c810a6209f5e19c99eabb730cfbdf9d42a45f90eac15e4be2c8bed5'
  'src/oil_tracker/web/videolink.js' = '8070edc5c61d1b6522321f0eeea3686f489761063f8921eca6fb3ab7978e3a2d'
  'tests/test_app.py' = 'a8078d73f08515814c0da1d84635bdf3cf8f4fa084b5864863aef0f1720de846'
  'tests/test_app_icon.py' = '35031cff80216ce395ab8ff729dbcae3f1c9a674e47432f8c7c4e66e707e1b2f'
  'tests/test_application_editing.py' = 'fe2385457b3c73fe694e2ded3512c89ba603553a69fd6e914c71e4513e8880ee'
  'tests/test_application_inspections.py' = '61be939f7c862c92b05552f9460293b248cd6d52a7990829af3f57cdcd670454'
  'tests/test_application_recipes.py' = '154b61e3cf6e4aa81a68e2165f51e569eb7a78889207e617b273136f1c16cde8'
  'tests/test_architecture.py' = '42910fb569bd010342747d081d1c0cac7aa8c9f2641af24da92a2f4ab5317288'
  'tests/test_build_package_script.py' = '0be23b30841a2ead1bb428467b7a4deced46ad0ca2dbd16091229389547be9b8'
  'tests/test_compare_medians_script.py' = '3ced7c6a8096de3411be5f7fbc7db57a86ad81f531da41d3c418937b205ba119'
  'tests/test_docs_catalog.py' = 'bf999036473a5924f1ef312ab7e93e0b972819f5f6c167242a023996725fc4be'
  'tests/test_domain_edits.py' = '0df182eeb5cacbe1ffd51afed77427cd7411c8ceda2203628065f5bbb61f1fe3'
  'tests/test_domain_inspection.py' = '620ae6feae8f54bfa8fcb5ab7fc0fa23bb68b1545373b58c08f6af4b71c02db4'
  'tests/test_domain_judgment.py' = '1518d7eb6c234793e67fbe4a5eb4fdad94e6036669eb275233d1d7abcac0ef13'
  'tests/test_domain_recipe.py' = 'cb734519d22a238079f1cbdba7b0ecffb580f4b7ae6d2de0f60315bd8845a829'
  'tests/test_http_api.py' = 'ad2afb0bbe4ca9d9b16e594da0efd30821441a0cb2fd477c2aa18430f51f7d57'
  'tests/test_http_jobs.py' = 'fd538c2d448228f847ac1d201b47e133026bf66c9fb104a4cc11049f724c2d33'
  'tests/test_http_relay.py' = '236ec206ad92ad23eb1c20d4c23e8b11f03355b9344fddbfee050fdeb0160e8a'
  'tests/test_inspection_summary_script.py' = 'b95e84e4e704fd053e8e89ee252d0906c95ae87fea03b5a4cb68860f8fd19bc2'
  'tests/test_measure_editor_script.py' = 'd193a60fc745b51ba74d5977a993d561fc64350aed96e126ba7a96245ff83543'
  'tests/test_package.py' = '8d458fbb772dcd6a825e060c8fdcdad2eb7716a8f72ef6df8c3d437026f063f8'
  'tests/test_recipe_summary_script.py' = 'f90b3adff4b1fb43ae28ae2aead9c56c55f7dc22c09b10f8bf030e1a9598748b'
  'tests/test_report.py' = '567f0e045473ad96055ebd5e2555cf3339e51225fb518bad1fddfadfbb06a798'
  'tests/test_storage_inspection_files.py' = '9acace3734a6fcab6edbe2329214cc665d528c0e1e2880ef92395f6d9e32f323'
  'tests/test_storage_recipe_files.py' = 'e784cacbad6b421ef8426a448d1e9661f8c05daf7b238930a3c52a5c77a50288'
  'tests/test_time_analysis_script.py' = '5e3659ac7b9810095eeefc14511b190e8e8eb398143f8e13b25cf463e07a1ac0'
  'tests/test_video_analysis.py' = 'ec97c4ed0d328ea42f2ae233168667cb40014decd172712cca01092f83a30d98'
  'tests/test_video_context.py' = '47115a4f03a31b3b491a136b519c9809497e3ef7289c19ec203b656ec1d6765e'
  'tests/test_video_frames.py' = '02f4c4495486e21ef5ff78ce9df8ba8334ce00d7dbc1a66e4b50f21101add21b'
  'tests/test_video_trace.py' = '28e2444339976b194025dda134bc30db8d1409964badc08b28619ee0c50a5c64'
  'tests/test_web_inspection_smoke.py' = '5a3d5dbca068953d0bf658572f5e6c4a054917a188a71685e36ed393c4fa5fbc'
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

## 1. 환경과 백업 [에이전트]

```powershell
py -3.14 -m venv .venv-v2
.venv-v2\Scripts\python -m pip install -e ".[package]" pytest
.venv-v2\Scripts\python --version
py -3.14 -m venv .venv-measure
.venv-measure\Scripts\python -m pip install opencv-python-headless==4.14.0.94 numpy==2.5.4 playwright==1.64.1
$src = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'OilLevelTracker'
Copy-Item -LiteralPath $src -Destination 'C:\olt-v25d-backup\OilLevelTracker' -Recurse
"files_src=$((Get-ChildItem -LiteralPath $src -Recurse -File).Count) files_backup=$((Get-ChildItem -LiteralPath 'C:\olt-v25d-backup\OilLevelTracker' -Recurse -File).Count)"
$log = Join-Path $env:LOCALAPPDATA 'OilLevelTracker\app.log'
$logStart = if (Test-Path -LiteralPath $log) { (Get-Content -LiteralPath $log).Count } else { 0 }
"log_lines_before=$logStart"
```

## 2. 테스트 (S2) [에이전트]

```powershell
.venv-v2\Scripts\python -m pytest -q
```

마지막 줄을 원문으로 적는다. 기대값은 `261 passed, 4 skipped`이다. 실패가 있으면 이름과 마지막 30줄.

## 3. 빌드 [에이전트]

```powershell
.venv-v2\Scripts\python scripts\build_package.py
```

`folder=` 줄부터 마지막 `package=` 줄까지 전부 원문으로 적는다(`INFO` 줄은 옮기지 않는다).

## 4. 빌드한 앱으로 측정 (A4, A5, A6) [에이전트 → 사용자]

지난번과 같다. `<SPL#1 경로>`를 실제 경로로 바꾼다.

```powershell
.venv-measure\Scripts\python scripts\measure_editor.py --app build\dist\OilLevelTracker\OilLevelTracker.exe --video "<SPL#1 경로>" --recipe "$([Environment]::GetFolderPath('MyDocuments'))\OilLevelTracker\Recipes\SPL#1_test1_607bccb.recipe.json"
```

- **[사용자]:** 앱 창이 뜨면 최대화하고, `[4/5]`부터 끝날 때까지 마우스와 키보드를 건드리지 않는다. RDP인지 결과에 적는다.
- **결과 파일의 내용 전체**를 원문으로 적는다.

## 5. 실행 전 검사 목록 [에이전트]

**8절을 시작하기 전에** 실행하고, 출력을 전부 원문으로 적는다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
```

## 6. 앱 실행 [에이전트]

```powershell
Start-Process -FilePath 'build\dist\OilLevelTracker\OilLevelTracker.exe'
```

## 7. 새 검사 만들기 [사용자]

"새 검사" → `SPL#4_Cooling_onoff_#2.mp4` → Recipe `V25 SPL#4` → "다음". 검사 이름 **`V25b 선택 확인`**, 범위 전체, 압축기 기동 `11.0`초, "분석 시작". 편집기가 열린다. Glass는 **BASE**.

## 8. 앱 창에서 직접 조작 [사용자]

각 항목에 **O / X**와 한 줄 소감을 남긴다. 앱 창은 최대화해서 쓴다. 키 입력은 그래프나 빈 곳을 한 번 누른 뒤에 한다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| N1 | 툴바를 본다. 그래프의 **선이 없는 곳**을 몇 번 클릭하고, 끌어 본다 | 툴바 맨 앞 **"선택"**이 켜져 있는지. 클릭한 시각으로 재생 위치가 가고 원본 영상이 그 프레임을 보이는지. 끌어도 선과 보기가 바뀌지 않고 제목 옆에 "저장 안 함"이 생기지 않는지 |
| N2 | **Oil 선**을 클릭한다 | 클릭한 곳에서 이어진 Oil 선이 굵고 옅은 띠로 보이는지. 오른쪽 "편집"에 **"고른 선 · Oil · 시작 – 끝"** 칸이 생기고 "그릴 선"이 Oil인지 |
| N3 | `Delete` → `Ctrl+Z` | Delete로 그 이어진 선 **전체**가 지워지는지. Ctrl+Z로 돌아오는지 |
| N4 | `R`(범위)로 Oil이 있는 곳을 30초쯤 끌어 고른다. 툴바의 **"선택"**을 누르고, 범위 **안의** Oil 선을 클릭한다 | 범위가 **남아 있는지**. 고른 선 칸의 단추가 **"고른 선을 범위 안만 지우기"**이고, 범위 안 부분이 흰 점선으로 보이는지 |
| N5 | `Delete` → 결과를 본 뒤 `Ctrl+Z` | Oil이 **범위 안만** 지워지고, 범위 밖 Oil과 같은 범위의 Foam·참조는 그대로인지. Ctrl+Z로 돌아오는지 |
| N6 | 범위 안 Oil을 다시 클릭한 뒤 `Esc`, 한 번 더 `Esc` | 첫 Esc에 고른 선만 풀리고 범위는 남는지. 둘째 Esc에 범위가 풀리는지 |
| N7 | "그릴 선"을 **참조**로, `P`(연필)로 그래프 가운데에 짧은 선을 그린다. "선택"으로 그 참조 선을 클릭하고 `Delete` | 고른 선 칸이 "참조 · …"이고, Delete로 참조 선이 지워지는지. "그릴 선"을 Oil로 되돌린다 |
| N8 | `R`로 20초쯤 고르고 범위 칸의 **"FULL로"**. 결과를 본 뒤 `Ctrl+Z`. 같은 범위에서 **"EMPTY로"** → `Ctrl+Z` | FULL로: 그 범위 Oil이 Glass 맨 위로 그려지고 그래프 아래에 FULL 띠가 생기는지. EMPTY로: 맨 아래, EMPTY 띠. Ctrl+Z로 돌아오는지 |
| N9 | `P`(연필)로 Glass **맨 위 선에서 1–3 px 아래**를 가로로 10초쯤 그린다(누른 채로 잠깐 멈춰 본다) | 그리는 동안 맨 위 선이 파랗게 되고 오른쪽에 **"FULL에 붙음"**이 보이는지. 놓은 뒤 그 부분이 FULL 띠가 되는지. `Ctrl+Z` |
| N10 | `L`(점 잇기)로 Glass **맨 아래 선 근처**(1–3 px 위)에 점 두 개를 20초쯤 떨어지게 찍고 `Enter` | 두 점 사이가 맨 아래에 붙어 EMPTY 띠가 되는지. `Ctrl+Z` |
| N11 | `G`(잡아끌기)로 Oil 선 한 점을 잡아 맨 위 근처까지 끈다(놓기 전 "FULL에 붙음"을 본다). `Ctrl+Z`. 이어서 압축기 기동 표시(보라 점선)를 잡아끌기로 조금 옮겨 본 뒤 `Ctrl+Z` | 잡은 점이 맨 위에 붙는지. 기동 표시는 **잡아끌기에서만** 옮겨지는지(선택 도구에서는 클릭해도 재생 위치만 바뀜) |
| N12 | 선을 하나 그린 뒤 `Ctrl+S`. "제출"이 켜지면 눌러 **"제출" 창만 열고** 압축기 모델·시험 종류 칸을 확인한 뒤 **"취소"** (모든 Glass를 확인해야 켜지므로, 꺼져 있으면 각 Glass의 "이 Glass 확인"을 먼저 누른다) | 저장되는지. 제출 창에 두 칸이 있고 고칠 수 있는지. **제출하지 않고** 취소한다 |
| N13 | "← 검사 목록" → "새 검사" → `C:\olt-v25\res_1280x720.mp4` → Recipe 고르기에서 `V25 SPL#4`를 본 뒤 "취소" | 문구가 **"영상 해상도(1280×720)가 이 Recipe의 해상도(1920×1080)와 다릅니다."**인지 |

마지막으로 **전체 소감**을 한두 줄 남기고, 앱 창의 X로 앱을 닫는다.

## 9. 결과 확인 [에이전트]

앱을 닫은 뒤 실행하고, 출력을 전부 원문으로 적는다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
Get-Content -LiteralPath $log | Select-Object -Skip $logStart
```

## 통과 기준 (실행 전에 고정)

| ID | 통과 조건 |
|---|---|
| S1 | 0절 마지막 줄이 `checked=108 mismatched=0` |
| B | 1절 백업 줄의 두 수가 같다 |
| S2 | 2절 마지막 줄이 `261 passed, 4 skipped` |
| A8-b | 3절이 `package=PASS`, `size_mb` 200 이하, `package_files_changed=0` |
| A4–A6 | 4절 결과의 브라우저 줄이 `WebView2 (앱 창)`; 분석 180.0초 이하·샘플 8210개; A5 전체 중앙값 16 ms 이하·최대 50 ms 이하; 정확한 프레임 중앙값 100 ms 이하; 1배 재생 `<video>`, 59.0초 이상, waiting 0, 버린 프레임 1% 이하; `오류: 없음` |
| C | 8절 N1–N13이 모두 O |
| R | 9절에 `V25b 선택 확인`이 있고(`edits saved_at` 줄, `version` 줄 없음), 나머지 검사 6개의 줄이 5절과 글자 그대로 같고, 7개 모두 `sha256_check=same` |
| T | 9절 로그에 `Traceback` 줄이 없고, 이번 `start:` 줄이 모두 `(build)` |

## 결과 양식

```text
[S1] 0절 마지막 줄 = ; MISMATCH 줄 =
[env] python =
[B] 백업 줄 =
[log-before] log_lines_before=
[S2] pytest 마지막 줄 =
[3] 빌드 출력 원문 (folder= 줄부터 package= 줄까지):
[4] RDP로 접속했나 (예/아니오) = ; 측정 결과 파일 원문:
[5] 검사 목록 출력 원문 (8절 전):
[N1] O/X ; 소감 =
[N2] O/X ; 소감 =
[N3] O/X ; 소감 =
[N4] O/X ; 소감 =
[N5] O/X ; 소감 =
[N6] O/X ; 소감 =
[N7] O/X ; 소감 =
[N8] O/X ; 소감 =
[N9] O/X ; 소감 =
[N10] O/X ; 소감 =
[N11] O/X ; 소감 =
[N12] O/X ; 소감 =
[N13] O/X ; 문구 원문 = ; 소감 =
[소감] =
[9] 검사 목록 출력 원문:
[9] 로그 원문:
```
