# Windows 요청: V2-5 인수 확인 — 빌드와 A1–A9 (2026-11-02)

> 이 문서는 **두 PC**에서 실행하는 요청이다.
> - **워크스테이션 (0–9절):** Windows 에이전트와 사용자가 함께 한다. 빌드를 만들고, 그 빌드로 A1–A9를 확인한다.
> - **최저 사양 PC (10절):** 에이전트가 없다. 사용자가 워크스테이션에서 만든 빌드를 **옮겨서 실행만** 한다(그 PC에서 빌드하지 않는다, 사용자 2026-11-02).
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다. 요약하거나 줄을 줄이거나 직접 합계를 내지 않는다.
> - **[사용자]** 표시: 사용자가 앱 창에서 직접 조작하고 판단한다.
> - **통과 기준**은 아래 "통과 기준" 절에 있고, 실행 전에 고정됐다. 판정은 이 문서를 만든 쪽이 한다.
> - 결과 파일은 Windows에 남기고, 맨 아래 **결과 양식** 두 개(워크스테이션, 최저 사양 PC)만 텍스트로 돌려준다.
>
> **개정 (2026-11-02, 두 번째 시도 뒤):** 5절의 스크립트가 빌드한 앱 창에 붙지 못했다.
> - 첫 시도(`7dc38e7`): pywebview가 WebView2의 브라우저 인자를 직접 정해서 스크립트가 쓰던 WebView2 환경 변수가 읽히지 않았다. `5bb9025`에서 앱이 디버깅 포트를 pywebview에 넘기게 고쳤다.
> - 두 번째 시도(`5bb9025`): 포트에는 붙었지만 Playwright에 앱 페이지가 없었다. WebView2가 페이지를 만들기 전에 붙은 것으로 본다. `daf381a`에서 포트가 앱 페이지를 보일 때까지 기다렸다가 붙고, 그래도 안 보이면 다시 붙는다. 끝내 안 되면 **빌드한 앱의 서버를 Edge에서** 재고, 결과의 브라우저 줄에 그렇게 적는다(포트의 대상 목록도 함께).
> - **0절부터 새 폴더에서 다시 한다.** 앞의 두 시도는 문서 폴더의 데이터를 바꾸지 않았다. 앞의 백업(`C:\olt-v25-backup`, `C:\olt-v25b-backup`)과 ZIP은 그대로 두고, 이번 백업은 `C:\olt-v25c-backup`에 만든다.

## 무엇을 확인하나

첫 버전의 인수 기준 A1–A9(Product SSOT §2)를 **PyInstaller 한 폴더 빌드**로 판정한다. 시간 기준(A4–A6)은 워크스테이션에서 판정하고, 최저 사양 PC는 참고로 본다.

- **빌드:** `scripts\build_package.py`가 `build\dist\OilLevelTracker\`에 빌드하고, 크기(A8: 200 MB 이하)를 재고, 빌드한 앱을 창 없이 띄워 화면 파일이 나오는지와 패키지 폴더 안에 아무것도 쓰지 않는지를 확인한다. 마지막 줄이 `package=PASS`면 된다.
- **빌드한 앱으로 잰다 (A4–A6):** `scripts\measure_editor.py --app`이 빌드한 `OilLevelTracker.exe`를 띄우고, 그 창(WebView2) 안에서 SPL#1 분석 시간, 끄는 동안 다시 그리기, 정확한 프레임, 1배 재생을 잰다. 앱 창이 뜨기까지 걸린 시간도 적는다.
- **사용자가 빌드한 앱으로 처음부터 끝까지 (A1–A3, A7, A9):** 새 Recipe 두 개(SPL#4, SPL#1)를 만들고, 새 검사 두 개를 분석·편집·확인·제출하고, 보고서를 연다. 저장 뒤 다시 열기, 제출한 버전 잠김, 다시 제출, 영상이 바뀌었을 때의 경고도 본다.
- **V2-1에서 Windows로 미뤄 둔 것:** 첫 프레임이 아닌 곳에서 저장한 Recipe, 해상도가 다른 영상을 거절하는 문구. 리디렉션된 문서 폴더(OneDrive)는 이 워크스테이션에서는 볼 수 없다(문서 폴더가 `C:\Users\…\Documents`). 판정에서 뺀다.
- **V2-4b 뒤 고친 것:** 큰 창에서 배속 재생할 때 끊기던 문제.
- **새로 생긴 것:** 앱 로그 `%LOCALAPPDATA%\OilLevelTracker\app.log`. 콘솔이 없는 빌드라 오류(Traceback)는 여기에 남는다. 앱 창이 뜬 시간(`window: page loaded … s after start`)도 여기에 적힌다.

**이번 실행에서 제출하는 것은 새로 만드는 두 검사뿐이다.** 기존 검사 4개(1907, 1910, 1913, `V2-3 확인`)에서는 "제출"과 "고쳐서 다시 제출"을 누르지 않는다. 제출은 되돌릴 수 없으므로 1절에서 데이터 폴더를 먼저 복사한다.

## 0. 소스 확인 [에이전트]

1. **커밋 하나로 고정된 ZIP**을 받는다:
   `https://github.com/teeeeooo/oil_level_tracker/archive/daf381ad19598cb76a79afb53bbc381e6fb7f374.zip`
   **새 폴더**에 압축을 풀고(`oil_level_tracker-daf381a…`) 그 폴더를 저장소 루트로 쓴다. 이전 실행의 폴더는 쓰지 않는다.
2. 저장소 루트에서 아래를 그대로 실행한다. 마지막 줄이 `checked=108 mismatched=0`이면 된다. `MISMATCH` 줄이 있으면 그 줄을 전부 원문으로 적는다.

```powershell
$expected = @{
  'DESIGN.md' = '9efef05381dce10101429f32a54620a8fd3a38878d90633a0b0b5c2270cf4d61'
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
  'src/oil_tracker/domain/recipe.py' = 'dd4a9a665312391f03c48799dea38c455f512aae517c08dc3d663fee0f5ff2af'
  'src/oil_tracker/domain/version.py' = 'dbddebb985f4fbb96733bfacba617493973ecc8238665dd9f3d06d7d3e5bbd03'
  'src/oil_tracker/web/api.js' = '2978dc60221d35c03733e282b2b36790bb8e5f3a4ec7fe3c3fa4c2126e745bc1'
  'src/oil_tracker/web/app.css' = 'e3bc27579833fe86de57c3e1aed245470634142aa43796ad5ce937dc40f2417b'
  'src/oil_tracker/web/editor.js' = '5f2eb96c9433cb744d3148b70cea62c6f08b48d25878611ac5c60cdeb88cd0bd'
  'src/oil_tracker/web/frame.js' = '444689064c1f583b75982ad0fec87d8264467755e9a96a56fd5ddaccb95f35dc'
  'src/oil_tracker/web/header.js' = '7c4ed7fdf6c80479372c0596c3357e699e8bae232fdb2f164665f7e025c96728'
  'src/oil_tracker/web/index.html' = '44ec27a99d3afad618ab5d4fdd379353f503f160bd926b2b023bc29aa619f0e2'
  'src/oil_tracker/web/inspections.js' = 'ef71c9db77d26facb587957d0db164d6bce57a1eccaaf80f2cfc14aacea1b634'
  'src/oil_tracker/web/lines.js' = 'c87372f3c132886186ad8445b64229fc2a3903dc60cc867137c98a2995ff6dd1'
  'src/oil_tracker/web/main.js' = '4c4c26bb1de7e0a86fb1b4b77301366f9979f0b16e5551cab65ad427a8502137'
  'src/oil_tracker/web/nav.js' = 'f06641803602beefae7c67a473daeffa9a9b5eec63f65b7cb0829954529af267'
  'src/oil_tracker/web/player.js' = '74474ce590909371763014cde673f8fc30eb4a517e2fe0e01e5c3b716c060949'
  'src/oil_tracker/web/recipe.js' = '40e0e357f36e8724ffc9b9bca60c3f591f344f8cc19c8f27ba35c9dd0c17b588'
  'src/oil_tracker/web/render.js' = 'b28a746f55e535fe3c2774908afcba9111f82a5476b9befc83757c5cb5ecc3dd'
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
  'tests/test_domain_inspection.py' = '7306a9937e74a6dfecf1a2eae238f68128fba6b3545fb30e77fad317759e19aa'
  'tests/test_domain_judgment.py' = '1518d7eb6c234793e67fbe4a5eb4fdad94e6036669eb275233d1d7abcac0ef13'
  'tests/test_domain_recipe.py' = 'f916f1e77ef9f0559c7e3cee1dcab400a08dac94d1254cdefcb71dc91ad98b80'
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
  'tests/test_web_inspection_smoke.py' = '5e396459f3365ecfbeb5cb6f38fdc2a28d25b24ab7ba0e0bc8b5f9cecd9d7896'
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

venv를 **두 개** 만든다. `.venv-v2`는 앱과 빌드(PyInstaller)용, `.venv-measure`는 측정(Playwright)용이다.

```powershell
py -3.14 -m venv .venv-v2
.venv-v2\Scripts\python -m pip install -e ".[package]" pytest
.venv-v2\Scripts\python --version
.venv-v2\Scripts\python -m PyInstaller --version
py -3.14 -m venv .venv-measure
.venv-measure\Scripts\python -m pip install opencv-python-headless==4.14.0.94 numpy==2.5.4 playwright==1.64.1
```

지난 백업들은 그대로 두고, 데이터 폴더 전체(Recipe와 검사)를 새로 복사한다. 마지막 줄의 두 수가 같으면 된다.

```powershell
$src = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'OilLevelTracker'
Copy-Item -LiteralPath $src -Destination 'C:\olt-v25c-backup\OilLevelTracker' -Recurse
"files_src=$((Get-ChildItem -LiteralPath $src -Recurse -File).Count) files_backup=$((Get-ChildItem -LiteralPath 'C:\olt-v25c-backup\OilLevelTracker' -Recurse -File).Count)"
```

앱 로그가 이미 있는지 보고, 있으면 줄 수를 적어 둔다(9절에서 이번 실행의 줄만 본다).

```powershell
$log = Join-Path $env:LOCALAPPDATA 'OilLevelTracker\app.log'
$logStart = if (Test-Path -LiteralPath $log) { (Get-Content -LiteralPath $log).Count } else { 0 }
"log_lines_before=$logStart"
```

## 2. 테스트 (S2) [에이전트]

```powershell
.venv-v2\Scripts\python -m pytest -q
```

- 마지막 줄을 원문으로 적는다. 기대값은 `261 passed, 4 skipped`이다(`.venv-v2`에는 Playwright가 없어서 브라우저 테스트 세 모듈이 건너뛰어지고, Windows에서 건너뛰는 테스트가 하나 있다).
- 실패가 있으면 실패한 테스트 이름과 출력 마지막 30줄을 원문으로 적는다.

## 3. 빌드 (A8 크기) [에이전트]

```powershell
.venv-v2\Scripts\python scripts\build_package.py
```

- 몇 분 걸린다. PyInstaller의 `INFO` 줄은 옮기지 않는다. **`folder=` 줄부터 마지막 `package=` 줄까지** 전부 원문으로 적는다.
- 빌드가 실패해 `folder=` 줄이 없으면, 출력 마지막 40줄을 원문으로 적고 멈춘다.

## 4. 최저 사양 PC로 옮길 묶음 [에이전트]

빌드 폴더를 ZIP 하나로 묶는다. 사용자가 이 ZIP을 USB로 최저 사양 PC에 옮긴다(10절).

```powershell
New-Item -ItemType Directory -Force -Path 'C:\olt-v25' | Out-Null
Compress-Archive -Path 'build\dist\OilLevelTracker' -DestinationPath 'C:\olt-v25\OilLevelTracker-daf381a.zip' -Force
$zip = Get-Item 'C:\olt-v25\OilLevelTracker-daf381a.zip'
"zip_bytes=$($zip.Length) zip_sha256=$((Get-FileHash -Algorithm SHA256 -LiteralPath $zip.FullName).Hash.ToLower())"
```

## 5. 빌드한 앱으로 측정 (A4, A5, A6, 앱 창) [에이전트 → 사용자]

`<SPL#1 경로>`를 이 PC의 `SPL#1_Heating_coldstart.mp4` 실제 경로로 바꿔 실행한다.

```powershell
.venv-measure\Scripts\python scripts\measure_editor.py --app build\dist\OilLevelTracker\OilLevelTracker.exe --video "<SPL#1 경로>" --recipe "$([Environment]::GetFolderPath('MyDocuments'))\OilLevelTracker\Recipes\SPL#1_test1_607bccb.recipe.json"
```

- **원격 데스크톱(RDP)으로 접속해 있으면** 결과에 적는다. 화면 그리기와 재생은 RDP의 영향을 받을 수 있어서, 가능하면 이 절은 워크스테이션 앞에서 한다.
- 스크립트가 **빌드한 앱을 띄운다.** 앱은 측정용 데이터 폴더(`a5a6-data-…`)를 쓰므로 문서 폴더의 검사는 건드리지 않는다.
- **[사용자]:** 앱 창이 뜨면 **최대화**한다. `[3/5]` 분석(약 1분) 동안 해 두면 된다. 그 뒤 `[4/5]`부터 앱 창이 **저절로 움직인다**(선 그리기, 끌기, 확대, 프레임 넘기기, 60초 재생, 약 5분). 이 동안 **마우스와 키보드를 건드리지 않고**, 앱 창을 최소화하거나 가리지 않는다.
- 끝나면 앱은 저절로 닫힌다. 결과 표가 출력되고 `결과 파일: …\a5a6-editor-YYYYMMDD-HHMM.md` 경로가 나온다. **결과 파일의 내용 전체**를 원문으로 적는다.
- 앱 창에 붙지 못하면 스크립트가 **Edge 창을 하나 더 열어** 빌드한 앱의 서버로 잰다. 이때는 앱 창 대신 **Edge 창을 최대화하지 않고 그대로 둔다**(창 크기는 스크립트가 정한다). 결과의 브라우저 줄이 `msedge (빌드한 앱의 서버; …)`가 된다.
- 결과 끝에 `앱 창을 찾지 못했습니다` 또는 `앱이 끝났습니다`가 있으면, 그 결과를 그대로 적은 뒤 `--app …` 부분만 빼고 같은 명령을 한 번 더 실행해(Edge에서 소스로 잰다) 그 결과 파일도 전부 적는다.

## 6. 실행 전 목록 [에이전트]

출력을 **전부 원문으로** 적는다. 읽기만 한다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
.venv-v2\Scripts\python scripts\recipe_summary.py
```

## 7. 해상도가 다른 영상 만들기 [에이전트]

거절 문구를 보려고 1280×720짜리 3초 영상을 만든다(SPL 영상은 모두 1920×1080이다).

```powershell
.venv-v2\Scripts\python -c "import cv2, numpy as np; w = cv2.VideoWriter(r'C:\olt-v25\res_1280x720.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30.0, (1280, 720)); [w.write(np.full((720, 1280, 3), 40 + i, np.uint8)) for i in range(90)]; w.release()"
(Get-Item 'C:\olt-v25\res_1280x720.mp4').Length
```

## 8. 빌드한 앱으로 처음부터 끝까지 [사용자, 몇 곳은 에이전트]

**[에이전트]**가 빌드한 앱을 띄운다. 콘솔이 없는 앱이라 출력은 없다(9절에서 로그를 본다).

```powershell
Start-Process -FilePath 'build\dist\OilLevelTracker\OilLevelTracker.exe'
```

각 항목에 **O / X**와 한 줄 소감을 남긴다. 앱 창은 최대화해서 쓴다. 키 입력은 그래프나 빈 곳을 한 번 누른 뒤에 한다. 막히면 **F1**로 도움말을 연다. "다시 띄운다"는 탐색기에서 `build\dist\OilLevelTracker\OilLevelTracker.exe`를 두 번 누르는 것이다.

### Recipe 두 개와 해상도 거절

| ID | 할 일 | 볼 것 |
|---|---|---|
| U1 | 검사 목록 툴바의 "Recipe" → "새 Recipe" → "영상 열기"로 `SPL#4_Cooling_onoff_#2.mp4`. 이동 막대로 **01:00 근처**로 간다. Glass 두 개(BASE, ACCUM)를 `SPL#4_test1_607bccb`와 같은 자리에 놓고 0선과 판정 규칙을 맞춘다. 이름 `V25 SPL#4`로 "저장" | 저장되고 Recipe 목록에 `V25 SPL#4`, Glass "BASE, ACCUM", 1920 × 1080이 보이는지 |
| U2 | `V25 SPL#4`를 다시 연다 | 저장할 때 보던 **01:00 근처 프레임**이 기준 프레임으로 보이는지(첫 프레임이 아님) |
| U3 | 같은 방법으로 `SPL#1_Heating_coldstart.mp4`에서 **10:00 근처**로 가서 Glass BASE 하나를 `SPL#1_test1_607bccb`와 같은 자리에 놓고 이름 `V25 SPL#1`로 저장 | 저장되고 목록에 보이는지 |
| U4 | 검사 목록 → "새 검사" → `C:\olt-v25\res_1280x720.mp4` → Recipe 고르기에서 `V25 SPL#4` | 해상도가 달라 고를 수 없다는 **이유가 보이는지**. 그 문구를 소감에 **그대로** 적는다. "취소"로 나온다 |

### SPL#4 새 검사: 분석, 편집, 저장 뒤 다시 열기, 판정, 제출

| ID | 할 일 | 볼 것 |
|---|---|---|
| U5 | "새 검사" → `SPL#4_Cooling_onoff_#2.mp4` → `V25 SPL#4` → "다음". 검사 이름 `V25 SPL#4 인수`, 분석 범위는 영상 전체, 압축기 기동 시각을 영상에서 찾아 넣고 "분석 시작" | 진행 막대가 끝나고 편집기가 열리는지 |
| U6 | BASE와 ACCUM의 Oil 선을 맥락 이미지에 맞게 고친다(필요하면 Foam도 그리고, 복사·붙여넣기를 써도 된다). `Ctrl+S` | "저장함 …"이 나오는지 |
| U7 | 선을 하나 더 조금 고치고 `Ctrl+S`. **앱 창의 X로 앱을 닫고 다시 띄운다.** `V25 SPL#4 인수`를 "열기" | 마지막에 저장한 선까지 **그대로** 있는지(A9 저장과 이어 하기) |
| U8 | 두 Glass의 선이 맥락 이미지와 맞는지 본다 | 맞으면 O (A2) |
| U9 | 각 Glass의 판정을 본다. 동의하면 그대로, 아니면 "덮어쓰기"로 판정을 고르고 이유를 쓴다. 두 Glass 모두 "이 Glass 확인" | 두 Glass가 "확인함"이 되는지. 최종 판정에 동의하거나 이유를 남겼으면 O (A3) |
| U10 | 검사 정보에 압축기 모델 `V25-모델`, 시험 종류 `V25-시험`. "제출" → 창에서 "제출" | "v1을 제출했습니다."가 나오고, 도구와 "저장"이 꺼지는지(잠김) |
| U11 | "보고서 열기" → 브라우저에서 `Ctrl+P` → "PDF로 저장"으로 `C:\olt-v25\V25-SPL4-v1.pdf`에 저장 | 보고서가 **인터넷 없이** 열리는지(파일에서 열림). PDF가 **A4 가로**이고 글, 그래프, 맥락 이미지가 읽을 만한지 (A7) |
| U12 | "고쳐서 다시 제출 (v2)…" → 확인. 시험 종류를 `V25-시험2`로 바꾸고 "제출" → 창에서 "제출" | "v2을 제출했습니다."가 나오는지. 막대의 "버전"에서 v1을 고르면 v1이 읽기만 되는지 (A9) |

### SPL#1 새 검사: 68분, 큰 창 배속

| ID | 할 일 | 볼 것 |
|---|---|---|
| U13 | "새 검사" → `SPL#1_Heating_coldstart.mp4` → `V25 SPL#1` → "다음". 검사 이름 `V25 SPL#1 인수`, 범위 전체, 압축기 기동 `485.0`초(08:05.0), "분석 시작" | 분석이 끝나고 편집기가 열리는지. 걸린 시간을 대략 소감에 적는다 |
| U14 | 편집기에서 `Space`로 1배 재생 30초쯤 → `Space` | 재생이 **멈칫하지 않는지** (A6) |
| U15 | "크게 보기" → 큰 창의 배속을 `4`로 고르고 30초쯤 재생 → 멈춤 → 배속 `1` | 큰 창 영상이 **끊기지 않고** 두 창이 함께 가는지(V2-4b 뒤 고친 것) |
| U16 | Oil 선을 맥락 이미지에 맞게 고치고, 선이 맞는지 본 뒤(A2) 판정을 확인하고(A3) 검사 정보에 `V25-모델` / `V25-시험`. "제출" → "제출" | "v1을 제출했습니다."가 나오는지 |
| U17 | "보고서 열기" → `Ctrl+P` → "PDF로 저장"으로 `C:\olt-v25\V25-SPL1-v1.pdf` | 68분 보고서가 열리고 PDF가 A4 가로로 읽을 만한지 (A7) |

### 영상이 바뀌었을 때의 경고 (A9)

| ID | 할 일 | 볼 것 |
|---|---|---|
| U18 | "← 검사 목록". **[에이전트]**가 아래 첫 블록을 실행한다(`V2-3 확인`이 쓰는 영상 끝에 1바이트를 붙인다). 그다음 `V2-3 확인`을 "열기" | 영상이 바뀌었다는 **경고 막대**가 나오는지 |
| U19 | "← 검사 목록"(저장하지 않는다). **[에이전트]**가 아래 둘째 블록으로 영상을 원래 길이로 되돌린다. `V2-3 확인`을 다시 "열기" | 경고가 **나오지 않는지** |

```powershell
# U18: 1바이트 붙이기
$v = 'C:\olt-v23\SPL4_v23.mp4'; "before_bytes=$((Get-Item $v).Length)"
$f = [IO.File]::Open($v, 'Append'); $f.WriteByte(0); $f.Close(); "after_bytes=$((Get-Item $v).Length)"
```

```powershell
# U19: 원래 길이로 되돌리기
$v = 'C:\olt-v23\SPL4_v23.mp4'
$f = [IO.File]::Open($v, 'Open'); $f.SetLength(53165455); $f.Close(); "restored_bytes=$((Get-Item $v).Length)"
```

마지막으로 앱 창의 X로 앱을 닫고, **전체 소감**을 한두 줄 남긴다.

## 9. 결과 확인 [에이전트]

앱을 닫은 뒤 실행하고, 출력을 **전부 원문으로** 적는다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
.venv-v2\Scripts\python scripts\recipe_summary.py
Get-Content -LiteralPath $log | Select-Object -Skip $logStart
Get-ChildItem 'C:\olt-v25\*.pdf' | ForEach-Object { "$($_.Name) bytes=$($_.Length)" }
```

`$log`와 `$logStart`가 없어졌으면(새 PowerShell) 1절의 세 줄을 다시 실행하지 말고, `Get-Content -LiteralPath (Join-Path $env:LOCALAPPDATA 'OilLevelTracker\app.log')`로 파일 전체를 적는다.

## 10. 최저 사양 PC: 옮긴 빌드 실행 [사용자]

그 PC에는 에이전트가 없다. PowerShell 명령 몇 줄과 앱 조작만 한다. **빌드하지 않는다.** Python이 깔려 있어도 빌드한 앱은 쓰지 않는다(앱 안에 들어 있다).

**준비:**
1. 워크스테이션의 `C:\olt-v25\OilLevelTracker-daf381a.zip`을 USB로 옮겨 `C:\olt-v25\`에 둔다(네트워크 드라이브에 두지 않는다).
2. 지난번 `C:\a4\`에 둔 `SPL#1_Heating_coldstart.mp4`와 `SPL#1_test1_607bccb.recipe.json`을 그대로 쓴다. 지웠다면 워크스테이션에서 다시 복사한다.
3. 다른 프로그램을 닫는다.

**PowerShell**(시작 메뉴에서 "PowerShell")에 아래를 한 줄씩 붙여넣는다. ZIP의 SHA-256을 확인하고, 풀고, Recipe를 앱의 Recipe 폴더에 넣는다.

```powershell
(Get-FileHash -Algorithm SHA256 'C:\olt-v25\OilLevelTracker-daf381a.zip').Hash.ToLower()
Expand-Archive -Path 'C:\olt-v25\OilLevelTracker-daf381a.zip' -DestinationPath 'C:\olt-v25' -Force
$recipes = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'OilLevelTracker\Recipes'; New-Item -ItemType Directory -Force -Path $recipes | Out-Null
Copy-Item 'C:\a4\SPL#1_test1_607bccb.recipe.json' $recipes
(Get-ChildItem 'C:\olt-v25\OilLevelTracker' -Recurse -File | Measure-Object Length -Sum).Sum
```

**앱 조작:** 각 항목에 O / X와 한 줄 소감을 남긴다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| L1 | 탐색기에서 `C:\olt-v25\OilLevelTracker\OilLevelTracker.exe`를 두 번 누른다. 초시계로 **검사 목록이 보일 때까지** 잰다. "Windows의 PC 보호" 창이 나오면 "추가 정보" → "실행"(그랬다면 소감에 적는다) | 앱 창이 열리고 검사 목록이 보이는지. 걸린 초를 소감에 적는다 |
| L2 | "Recipe" | `SPL#1_test1_607bccb`가 목록에 있는지 |
| L3 | "새 검사" → `C:\a4\SPL#1_Heating_coldstart.mp4` → `SPL#1_test1_607bccb` → "다음". 범위 전체, 압축기 기동 `485.0`초, "분석 시작". 초시계로 **분석이 끝날 때까지** 잰다 | 분석이 끝나고 편집기가 열리는지. 걸린 초를 소감에 적는다 |
| L4 | `G`로 Oil 선을 몇 번 끌어 보고, `P`로 짧게 그려 본다 | 선이 끌리는 대로 따라오는지(느리면 소감에) |
| L5 | `Space`로 1배 재생 30초쯤 → `Space`. 그다음 "크게 보기" → 큰 창에서 배속 `4`로 20초쯤 재생 → 멈춤 → 큰 창 닫기 | 작은 영상이 멈칫하지 않는지. 큰 창이 끊기지 않는지(끊기면 소감에) |
| L6 | "이 Glass 확인" → 검사 정보에 `V25-최저` → "제출" → "제출" → "보고서 열기" | 제출되고 보고서가 브라우저에 열리는지 |
| L7 | 앱 창의 X로 닫는다 | 닫히는지 |

닫은 뒤 PowerShell에 아래를 붙여넣고, 나온 줄을 전부 적는다.

```powershell
Get-Content -LiteralPath (Join-Path $env:LOCALAPPDATA 'OilLevelTracker\app.log')
```

## 통과 기준 (실행 전에 고정)

### 워크스테이션

| ID | 통과 조건 |
|---|---|
| S1 | 0절 마지막 줄이 `checked=108 mismatched=0` |
| B | 1절 백업 줄의 `files_src`와 `files_backup`이 같다 |
| S2 | 2절 마지막 줄이 `261 passed, 4 skipped` |
| A8-b | 3절이 `package=PASS`로 끝나고, `size_mb`가 200 이하, `package_files_changed=0`, 네 `page` 줄이 모두 `status=200` |
| A4 | 5절 결과의 분석 줄이 "빌드한 앱으로"이고 **180.0초 이하**, `샘플 8210개` |
| A5 | 5절 A5 표 **전체** 줄의 중앙값이 **16 ms 이하**, 최대가 **50 ms 이하** |
| A6 | 5절 정확한 프레임(서버) 중앙값이 **100 ms 이하**; 1배 재생이 `<video>`이고 진행이 60초 중 **59.0초 이상**, waiting·stalled **0**, 버린 프레임이 전체의 **1% 이하**; 8절 U14가 O |
| M | 5절 결과의 빌드한 앱 줄이 `OilLevelTracker.exe`이고, 결과 끝이 `오류: 없음`. 브라우저 줄이 `WebView2 (앱 창)`이면 빌드의 창에서 잰 것이고, `msedge (빌드한 앱의 서버; …)`이면 빌드의 서버를 같은 엔진(Edge)에서 잰 것으로 기록한다 (앱 창이 뜬 시간은 기록만) |
| A1 | 8절 U1–U17이 모두 O이고, 9절의 검사 목록에 `V25 SPL#4 인수`(Glass 2개)와 `V25 SPL#1 인수`(Glass 1개)가 있고 둘 다 `version v=1` 줄이 있다 |
| A2 | U8, U16이 O |
| A3 | 2절 S2 통과(판정 규칙의 단위 테스트 포함); 9절의 두 검사 모든 `version glass` 줄이 `verdict=`와 `computed=`가 같거나, 다르면 `override=`가 `-`가 아니고 `reason_chars`가 1 이상; U9가 O |
| A7 | 9절의 새 `version` 줄 세 개 모두 `report_bytes`가 1 이상 5,000,000 이하; U11, U17이 O; 9절에 PDF 두 개가 있다 |
| A9 | U7, U12, U18, U19가 O; 9절의 `V25 SPL#4 인수`에 `version v=1`과 `version v=2`가 있고 v2의 `header`가 `test_type="V25-시험2"`; U18 `after_bytes`가 `before_bytes`+1이고 U19 `restored_bytes=53165455`; 9절의 `V2-3 확인`이 `sha256_check=same` |
| V1 | 9절 Recipe 목록의 `V25 SPL#4`가 `frame=1920x1080 … glasses=2 problems=0`이고 `t=`가 0보다 크다; `V25 SPL#1`이 `glasses=1 problems=0`이고 `t=`가 0보다 크다; U2가 O |
| V2 | U4가 O이고 거절 문구가 적혀 있다(문구는 판정하는 쪽이 읽고 사용자와 정한다) |
| R | 9절의 `20261029-1907_SPL#4_Cooling_onoff_#2`, `20261029-1910_SPL#1_Heating_coldstart`, `20261029-1913_SPL#1_Heating_coldstart`, `V2-3 확인` 줄이 6절과 글자 그대로 같고, 6개 검사 모두 `sha256_check=same`; 9절 Recipe 목록에 `SPL#1_test1_607bccb`, `SPL#4_test1_607bccb` 줄이 6절과 같다 |
| T | 9절 로그에 `Traceback` 줄이 없다; 이번 실행의 `start:` 줄에 `(build)`가 있다 |
| W | U15가 O (큰 창 배속 끊김을 고친 것) |

### 최저 사양 PC (A8 실행 부분; 시간은 참고)

| ID | 통과 조건 |
|---|---|
| L-zip | 10절 첫 줄의 SHA-256이 4절 `zip_sha256`과 같다 |
| A8-r | L1–L7이 모두 O: 앱이 옮긴 빌드 그대로 그 PC에서 열리고, 분석·편집·제출·보고서까지 된다 |
| L-T | 10절 로그에 `Traceback` 줄이 없고, `start:` 줄에 `(build)`가 있다 |
| — | 기록만: L1(창이 뜬 초)과 로그의 `window: page loaded` 초, L3(분석 초), L4·L5 소감. 기준을 넘어도 인수 실패가 아니다(Product SSOT §2) |

## 결과 양식: 워크스테이션

```text
[S1] 0절 마지막 줄 = ; MISMATCH 줄 =
[env] python = ; PyInstaller =
[B] 백업 줄 =
[log-before] log_lines_before=
[S2] pytest 마지막 줄 = ; (실패가 있으면 이름과 마지막 30줄)
[3] 빌드 출력 원문 (folder= 줄부터 package= 줄까지):
[4] zip 줄 =
[5] RDP로 접속했나 (예/아니오) = ; 측정 결과 파일 원문:
[6] 검사 목록 출력 원문:
[6] Recipe 목록 출력 원문:
[7] 영상 크기 =
[U1] O/X ; 소감 =
[U2] O/X ; 소감 =
[U3] O/X ; 소감 =
[U4] O/X ; 거절 문구 원문 = ; 소감 =
[U5] O/X ; 소감 =
[U6] O/X ; 소감 =
[U7] O/X ; 소감 =
[U8] O/X ; 소감 =
[U9] O/X ; 소감 =
[U10] O/X ; 소감 =
[U11] O/X ; 소감 =
[U12] O/X ; 소감 =
[U13] O/X ; 분석에 걸린 시간 = ; 소감 =
[U14] O/X ; 소감 =
[U15] O/X ; 소감 =
[U16] O/X ; 소감 =
[U17] O/X ; 소감 =
[U18] O/X ; before_bytes= ; after_bytes= ; 소감 =
[U19] O/X ; restored_bytes= ; 소감 =
[소감] =
[9] 검사 목록 출력 원문:
[9] Recipe 목록 출력 원문:
[9] 로그 원문:
[9] PDF 줄 =
```

## 결과 양식: 최저 사양 PC

```text
[L-zip] SHA-256 줄 =
[L-size] 폴더 크기 줄 =
[L1] O/X ; 검사 목록까지 초 = ; 소감 =
[L2] O/X ; 소감 =
[L3] O/X ; 분석 초 = ; 소감 =
[L4] O/X ; 소감 =
[L5] O/X ; 소감 =
[L6] O/X ; 소감 =
[L7] O/X ; 소감 =
[로그] 원문 =
[PC] CPU·RAM·모니터 해상도 (알면) =
[소감] =
```
