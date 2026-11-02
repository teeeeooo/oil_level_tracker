# Windows 요청: V2-4b 원본 영상 창과 복사·붙여넣기 (2026-11-02)

> 이 문서는 **Windows 워크스테이션에서 실행**하기 위한 요청이다.
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다. 요약하거나 줄을 줄이거나 직접 합계를 내지 않는다.
> - **[사용자]** 표시: 사용자가 앱 창에서 직접 조작하고 판단한다.
> - **통과 기준**은 아래 "통과 기준" 절에 있고, 실행 전에 고정됐다. 판정은 이 문서를 만든 쪽이 한다. 에이전트는 원문만 옮긴다.
> - 결과 파일은 Windows에 남기고, 맨 아래 **결과 양식**만 텍스트로 돌려준다.

## 무엇을 확인하나

V2-4 재확인 뒤 사용자가 첫 버전에 넣기로 한 두 기능이다(Product SSOT §6, 2026-11-02).

- **원본 영상 창:** 편집기 원본 영상 오른쪽 위의 **"크게 보기"**가 원본 영상을 앱 밖의 **따로 띄운 창**으로 연다. 두 창의 재생 위치는 서로 따라간다. 창은 다음에 열 때 놓았던 자리에서 열린다.
- **복사·붙여넣기:** 범위 도구로 고른 구간의 Oil과 Foam을 복사(Ctrl+C)해서, 한 곳씩(Ctrl+V) 또는 반복해서("반복 붙여넣기…") 붙인다. 높이는 복사한 그대로이고 스냅은 쓰지 않는다.

워크스테이션 검사 4개 중 둘을 쓴다.
- **`20261029-1910_SPL#1_Heating_coldstart`** (68분, 편집 없음): 원본 영상 창만 본다. **저장하지 않는다.**
- **`V2-3 확인`** (SPL#4, 냉각 on/off 영상, 제출한 적 없음): 복사·붙여넣기를 하고 **저장한다.**
- `20261029-1907_SPL#4_Cooling_onoff_#2`와 `20261029-1913_SPL#1_Heating_coldstart`는 열지 않는다.

**이번 실행에서는 어디서도 "제출"과 "고쳐서 다시 제출"을 누르지 않는다.**

## 0. 소스 확인 [에이전트]

1. **커밋 하나로 고정된 ZIP**을 받는다:
   `https://github.com/teeeeooo/oil_level_tracker/archive/f2d68500feab177e6b0829c7e7690b40b499c7e0.zip`
   **새 폴더**에 압축을 풀고(`oil_level_tracker-f2d6850…`) 그 폴더를 저장소 루트로 쓴다. 이전 실행의 폴더는 쓰지 않는다.
2. 저장소 루트에서 아래를 그대로 실행한다. 마지막 줄이 `checked=100 mismatched=0`이면 된다. `MISMATCH` 줄이 있으면 그 줄을 전부 원문으로 적는다.

```powershell
$expected = @{
  'DESIGN.md' = '91aeb0c438f6582bc2a4354a7c7c12d79514631b7eac2668fee395a179f9b94b'
  'pyproject.toml' = '3890d934fa7c238ab51c2994f5c2ed44bed9f83d0067eccb085be19ac8c58b9d'
  'scripts/check_docs_catalog.py' = '226a0293907b9b9b555a71d3aca5ba3b1f07369295403c3e44ee1d877efe0020'
  'scripts/compare_draft_methods.py' = '3c87c76b632c69f6b418fb39d923a10d40db0d15e4add08ac149427cf0a991f7'
  'scripts/compare_medians.py' = '947510c05253ef8081dedfac2409ca0709bc22c08bddb2dd3e0fcc8382ce6e9a'
  'scripts/inspection_summary.py' = '97fcb09ec75385f2f742ff7cdf56d6039fc3731accafaacdd0087fc6c0925318'
  'scripts/install_git_hooks.sh' = '762c1e1a4e38a99c086447b548ca071f84d29ac8e0aa0f26e8a717eb4e865008'
  'scripts/measure_editor.py' = '0991b8abf3b18ef11a58a4eb852c6868bc333c10626e87a71f706577b970ae27'
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
  'src/oil_tracker/app.py' = 'd077ea1ac42c1e086085f15b2e24ed4f25736df8594c4da3c04fb42bef752ac7'
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
  'src/oil_tracker/web/editor.js' = '99bcaf4c5eaa61d13a604baf3fb0a805e7805f486ff8c93a48e9456ee32308a5'
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
  'src/oil_tracker/web/video-window.js' = '168e926924d001bf3f8a540ebb24dc17910cace596b2af39e8e99115ae8b2662'
  'src/oil_tracker/web/video.html' = 'd96e42745c810a6209f5e19c99eabb730cfbdf9d42a45f90eac15e4be2c8bed5'
  'src/oil_tracker/web/videolink.js' = 'bd912fc9ab85b7305e04e40cb122939fdd01a6c6a2495a5e9dede70e0071272d'
  'tests/test_app.py' = 'ef1e264605b6477e4bc6c66e21d2631012155c81a8510c53104da9081580435e'
  'tests/test_application_editing.py' = 'fe2385457b3c73fe694e2ded3512c89ba603553a69fd6e914c71e4513e8880ee'
  'tests/test_application_inspections.py' = '61be939f7c862c92b05552f9460293b248cd6d52a7990829af3f57cdcd670454'
  'tests/test_application_recipes.py' = '154b61e3cf6e4aa81a68e2165f51e569eb7a78889207e617b273136f1c16cde8'
  'tests/test_architecture.py' = '42910fb569bd010342747d081d1c0cac7aa8c9f2641af24da92a2f4ab5317288'
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
  'tests/test_measure_editor_script.py' = '430c3960fc8e93f33b5b3dd6d3a684baf89df2768f71aca0dd211f36b65fd281'
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
  'tests/test_web_inspection_smoke.py' = '2980416f83a957bb31ec37be259e1055c48fb7c2910a3055499a1e1f93b577f9'
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

이 폴더에 **앱용 venv 하나**만 만든다(Playwright를 넣지 않는다).

```powershell
py -3.14 -m venv .venv-v2
.venv-v2\Scripts\python -m pip install -e . pytest
.venv-v2\Scripts\python --version
```

지난 백업들은 그대로 두고, 지금 상태를 새로 복사한다. 마지막 줄의 두 수가 같으면 된다.

```powershell
$src = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'OilLevelTracker\Inspections'
Copy-Item -LiteralPath $src -Destination 'C:\olt-v24b-window-backup\Inspections' -Recurse
"files_src=$((Get-ChildItem -LiteralPath $src -Recurse -File).Count) files_backup=$((Get-ChildItem -LiteralPath 'C:\olt-v24b-window-backup\Inspections' -Recurse -File).Count)"
```

창 자리 파일이 이미 있는지 본다(처음이면 `없음`).

```powershell
$place = Join-Path $env:LOCALAPPDATA 'OilLevelTracker\video-window.json'
if (Test-Path -LiteralPath $place) { Get-Content -LiteralPath $place } else { '없음' }
```

## 2. 테스트 (S2) [에이전트]

```powershell
.venv-v2\Scripts\python -m pytest -q
```

- 마지막 줄을 원문으로 적는다. 기대값은 `248 passed, 4 skipped`이다.
- 실패가 있으면 실패한 테스트 이름과 출력 마지막 30줄을 원문으로 적는다.

## 3. 실행 전 검사 목록 [에이전트]

출력을 **전부 원문으로** 적는다. 읽기만 한다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
```

## 4. 앱 실행 [에이전트 → 사용자]

```powershell
.venv-v2\Scripts\python -m oil_tracker
```

- 창이 열리면 **[사용자]**가 5절을 진행한다. 앱 창은 최대화해서 쓴다.
- 앱이 도는 동안 **콘솔에 나온 줄을 전부** 원문으로 적는다(5절의 W12에서 앱을 닫고 다시 열 때까지, 두 번 모두). 없으면 "없음".

## 5. 앱 창에서 직접 조작 [사용자]

각 항목에 **O / X**와 한 줄 소감을 남긴다. 키 입력은 그 창의 그래프나 빈 곳을 한 번 누른 뒤에 한다. "큰 창"은 "크게 보기"로 연 원본 영상 창이다.

### 원본 영상 창: SPL#1 (1910), 저장하지 않음

검사 목록에서 **`20261029-1910_SPL#1_Heating_coldstart`**의 "열기"를 누른다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| W1 | 오른쪽 위 원본 영상의 **"크게 보기"** | 앱 밖에 **따로 창**이 뜨는지(작업 표시줄에 창이 하나 더). 제목이 "원본 영상 — SPL#1_Heating_coldstart.mp4"인지. 프레임 전체가 보이고 BASE 타원, 0선, Oil 선이 겹쳐 있는지. 아래 오른쪽이 초록 "편집기와 같은 위치"인지 |
| W2 | 큰 창을 끌어 **다른 모니터로** 옮기고(모니터가 하나면 화면 한쪽으로) 크기를 키운다 | 창을 옮기고 키워도 프레임이 창에 맞춰 다시 그려지는지 |
| W3 | 앱 창에서 `Space`로 재생, 20초쯤 뒤 `Space`로 멈춤 | 두 창이 **함께** 재생되고 함께 멈추는지. 멈춘 뒤 두 창의 시각 글자가 같고, 큰 창의 그림이 또렷한지(정확한 프레임) |
| W4 | 큰 창에서 재생 단추 → 몇 초 뒤 다시 눌러 멈춤. 이어서 큰 창에서 `.`을 세 번, `,`를 한 번 | 큰 창에서 누른 대로 **앱 창도** 재생·멈춤하는지. `.` `,`로 두 창이 한 프레임씩 같이 움직이는지 |
| W5 | 큰 창 아래 이동 막대의 **가운데**를 클릭 | 두 창이 34분 근처로 가고, 앱 창 그래프가 그 시각을 보여 주는지 |
| W6 | 큰 창의 배속을 `4`로 고르고 재생, 몇 초 뒤 멈춤. 배속을 `1`로 되돌림 | 앱 창의 배속 칸도 4로 바뀌고 두 창이 4배로 재생되는지 |
| W7 | 큰 창의 **"원본 크기"** → 영상을 끌어 둘러봄 → "창에 맞춤". "선 겹쳐 보기"를 껐다 켬 | 원본 크기에서 오른쪽 위가 `100 %`이고 끌어서 움직이는지. 선 겹쳐 보기를 끄면 선이 사라지고 켜면 돌아오는지 |
| W8 | 앱 창에서 `G`(잡아끌기)로 재생 위치 근처 Oil 선을 위로 끌었다 놓음. 그다음 `Ctrl+Z` | 놓은 뒤 곧 큰 창의 Oil 선도 같은 높이로 옮겨지는지. `Ctrl+Z` 뒤 돌아오는지 |
| W9 | 큰 창을 **최소화**한 뒤 앱 창의 "크게 보기"를 다시 누름 | 큰 창이 다시 **앞으로** 나오는지(창이 둘이 되지 않음) |
| W10 | 앱 창의 "← 검사 목록". 저장 여부를 물으면 **저장하지 않고 나간다** | 큰 창이 **함께 닫히는지** |
| W11 | 1910을 다시 열고 "크게 보기" → 큰 창의 X로 닫기 → "크게 보기" 한 번 더 | 큰 창이 W2에서 **놓았던 모니터·자리·크기**로 열리는지. X로 닫은 뒤 앱 창이 그대로 쓰이고, 다시 누르면 또 열리는지 |
| W12 | 큰 창을 연 채로 **앱 창의 X**로 앱을 닫는다(저장 여부를 물으면 저장하지 않음). **[에이전트]**가 4절 명령으로 앱을 다시 띄운다. 1910을 열고 "크게 보기" → "← 검사 목록" | 앱을 닫으면 큰 창도 닫히는지. 다시 띄운 앱에서도 큰 창이 W11의 자리로 열리는지 |

### 복사·붙여넣기: SPL#4 (`V2-3 확인`), 저장함

검사 목록에서 **`V2-3 확인`**의 "열기"를 누른다. 이 영상은 압축기를 일정 간격으로 켜고 끄는 시험이다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| P1 | Glass BASE. 맥락 이미지에서 **한 주기**(압축기가 켜졌다 꺼졌다 다시 켜지기 전까지)를 고른다. 그 주기의 Oil 선을 필요하면 고치고, "그릴 선"을 **Foam**으로 바꿔 연필(`P`)로 그 주기의 Foam을 그린다. "그릴 선"을 Oil로 되돌린다 | 한 주기의 Oil과 Foam이 그려졌는지 |
| P2 | BASE 판정 칸의 **"이 Glass 확인"** | "✓ 확인함"이 되는지 |
| P3 | `R`(범위)로 그 주기를 가로로 끌어 고르고 `Ctrl+C` | 편집 칸에 "복사한 구간"과 그 시각·길이가 나오는지 |
| P4 | `Ctrl+V` → 마우스를 그래프 위로 움직임 → **다음 주기 시작**을 클릭 → `Esc` | 점선 복사본이 마우스를 따라다니는지. 클릭한 곳에 Oil과 Foam이 **복사한 높이 그대로** 붙는지. "1곳 붙임". BASE의 확인이 풀려 Glass 고르기가 "확인 전"인지 |
| P5 | `Ctrl+Z` 한 번 → `Ctrl+Shift+Z` 한 번 | `Ctrl+Z` 한 번에 붙인 Oil과 **Foam이 함께** 사라지고, `Ctrl+Shift+Z`로 함께 돌아오는지 |
| P6 | "반복 붙여넣기…" | 첫 시작(복사한 구간 바로 뒤), 주기(복사한 길이), 끝(`03:30.0`) 칸과 번호 붙은 점선 복사본이 보이는지. 아래 글이 붙을 개수와 시작 시각을 말하는지 |
| P7 | **주기** 칸을 실제 주기에 맞게 고친다(맞으면 그대로). 그래프에서 **1번 복사본을 끌어** 첫 시작을 옮겨 본다. `Enter` | 주기를 고치면 점선 위치와 개수가 바로 바뀌는지. 1번을 끌면 첫 시작 칸이 바뀌는지. `Enter`로 한 번에 붙는지(분석 범위 끝을 넘는 것은 잘림) |
| P8 | Glass를 **ACCUM**으로 바꾼 뒤 편집 칸을 봄. 다시 BASE | ACCUM에서는 붙여넣기 단추가 꺼져 있고 "BASE에서 복사했습니다…"가 나오는지 |
| P9 | 붙인 선을 맥락 이미지와 견주어 본다. `Ctrl+S`로 저장 | 저장되는지. 이 기능이 on/off 시험에 쓸 만한지 **소감**에 적는다 |

마지막으로 **전체 소감**을 한두 줄 남긴다. 앱 창의 X로 앱을 닫는다.

## 6. 결과 확인 [에이전트]

앱을 닫은 뒤 실행하고, 출력을 **전부 원문으로** 적는다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
$place = Join-Path $env:LOCALAPPDATA 'OilLevelTracker\video-window.json'
if (Test-Path -LiteralPath $place) { Get-Content -LiteralPath $place } else { '없음' }
```

## 통과 기준 (실행 전에 고정)

| ID | 통과 조건 |
|---|---|
| S1 | 0절 마지막 줄이 `checked=100 mismatched=0` |
| B | 1절 백업 줄의 `files_src`와 `files_backup`이 같다 |
| S2 | 2절 마지막 줄이 `248 passed, 4 skipped` |
| C | 5절의 W1–W12, P1–P9가 모두 O |
| T | 4절 콘솔에 `Traceback` 줄이 없다(두 번 실행 모두, 창을 닫을 때까지) |
| R1 | 6절이 `inspections=4 unreadable=0` |
| R2 | 6절의 `V2-3 확인`: `edits saved_at`이 3절보다 나중; `compressor=20.2`; BASE `edits glass` 줄의 `oil=`과 `foam=`에서 세 번째 수(직접 그림)가 각각 3절보다 크다; BASE가 `checked=no`; ACCUM `edits glass` 줄이 3절과 글자 그대로 같다 |
| R3 | 6절에서 `20261029-1907_SPL#4_Cooling_onoff_#2`, `20261029-1910_SPL#1_Heating_coldstart`, `20261029-1913_SPL#1_Heating_coldstart`의 줄이 3절과 글자 그대로 같고(1910은 `edits none` 그대로), 네 검사 모두 `sha256_check=same` |
| R4 | 6절의 `video-window.json`에 `x`, `y`, `width`, `height`가 모두 정수로 있고 `width` ≥ 960, `height` ≥ 600 |

## 결과 양식

```text
[S1] 0절 마지막 줄 = ; MISMATCH 줄 =
[env] python =
[B] 백업 줄 =
[place-before] 1절 창 자리 파일 =
[S2] pytest 마지막 줄 = ; (실패가 있으면 이름과 마지막 30줄)
[3] 검사 목록 출력 원문:
[4] 콘솔 줄 원문, 첫 실행 (없으면 "없음") =
[4] 콘솔 줄 원문, W12에서 다시 띄운 실행 (없으면 "없음") =
[W1] O/X ; 소감 =
[W2] O/X ; 소감 =
[W3] O/X ; 소감 =
[W4] O/X ; 소감 =
[W5] O/X ; 소감 =
[W6] O/X ; 소감 =
[W7] O/X ; 소감 =
[W8] O/X ; 소감 =
[W9] O/X ; 소감 =
[W10] O/X ; 소감 =
[W11] O/X ; 소감 =
[W12] O/X ; 소감 =
[P1] O/X ; 소감 =
[P2] O/X ; 소감 =
[P3] O/X ; 소감 =
[P4] O/X ; 소감 =
[P5] O/X ; 소감 =
[P6] O/X ; 소감 =
[P7] O/X ; 소감 =
[P8] O/X ; 소감 =
[P9] O/X ; 소감 =
[소감] =
[6] 검사 목록 출력 원문:
[6] 창 자리 파일 =
```
