# Windows 요청: P-2b 재확인 — 줄인 편집기 도움말로 2.0.0 다시 빌드, R 보충 (2026-11-03)

> 이 문서는 **Windows 워크스테이션에서만** 실행한다. 최저 사양 PC는 이번에 하지 않는다(아래 "최저 사양 PC").
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다. 요약하거나 줄을 줄이거나 직접 합계를 내지 않는다. **검사 목록처럼 긴 출력도 파일로 미루지 말고 결과 양식에 그대로 붙인다.**
> - **[사용자]** 표시: 사용자가 직접 조작하고 판단한다.
> - **통과 기준**은 아래 "통과 기준" 절에 있고, 실행 전에 고정됐다. 판정은 이 문서를 만든 쪽이 한다.

## 무엇을 확인하나

- **R 보충:** 앞 실행([요청](2026-11-03-p2b-release-windows-request.md), [결과](../60-evidence/2026-11-03-p2b-release-windows-result.md))의 R은 검사 목록 원문이 전달되지 않아 판정하지 못했다. 에이전트가 남긴 두 파일을 비교한다.
- **줄인 편집기 도움말:** 사용자 소감(2026-11-03)대로 편집기의 F1 도움말을 줄였다.
  - 모든 키와 마우스 동작은 남기고, 각각 한 줄로 줄였다.
  - 제출·버전·다시 분석·원본 영상 경고 설명은 빼고, "사용 설명서"를 보라는 한 줄을 남겼다.
  - 바뀐 파일은 `src/oil_tracker/web/index.html`과 `DESIGN.md` 둘뿐이다.
- **배포판 다시 만들기:** 앱이 바뀌었으므로 같은 버전(2.0.0)으로 ZIP을 다시 만든다. **앞 실행의 ZIP(`920dfbef…`)은 배포하지 않는다.**

데이터는 바꾸지 않는다. 제출한 `V25b 선택 확인`을 읽기 전용으로 열어 도움말만 본다.

## 0. R 보충 [에이전트]

앞 실행의 두 검사 목록을 비교한다. 출력 줄을 **모두** 원문으로 적는다.

```powershell
$dir = Join-Path $env:USERPROFILE '.cline-sr\data\sr\tool-result-spills\1793686553645_i7t1d'
$before = Get-Content -LiteralPath (Join-Path $dir 'run_commands-call_3b03a138fe34411997f1460c-1-result-fc0a1e46-0161-419a-bb5f-1df14929700c.txt')
$after = Get-Content -LiteralPath (Join-Path $dir 'run_commands-call_a47d0d48c589468e82b4c205-0-result-a8d9cbdf-4d46-42c8-acce-65b365322ad1.txt')
Compare-Object $before $after | ForEach-Object { "$($_.SideIndicator) $($_.InputObject)" }
"checks_after=$(($after | Select-String 'sha256_check=').Count) same_after=$(($after | Select-String 'sha256_check=same').Count)"
```

## 1. 소스 확인 [에이전트]

1. **커밋 하나로 고정된 ZIP**을 받는다:
   `https://github.com/teeeeooo/oil_level_tracker/archive/11e4745b955fb3ab6c0aeb45ad41b75281aa9320.zip`
   **새 폴더**에 압축을 풀고(`oil_level_tracker-11e4745…`) 그 폴더를 저장소 루트로 쓴다.
2. 저장소 루트에서 아래를 그대로 실행한다. 마지막 줄이 `checked=154 mismatched=0`이면 된다. `MISMATCH` 줄이 있으면 그 줄을 전부 원문으로 적는다.

```powershell
$expected = @{
  'DESIGN.md' = 'e3bacd16aa9c732b45ee7f92f16221797b5523a11342e6cf6fc93c9e87755c9c'
  'packaging/OilLevelTracker.ico' = 'ca5077a6396176d41ee30d17c461803b2195fb6346b930341aa4765dd24537e1'
  'packaging/OilLevelTracker.spec' = 'edc65743b2fdd3e2b94a95a49d1c3bf2a6a78b4b2c79bafda7c05fb83d00713d'
  'packaging/app-icon-small.svg' = 'a97b844336ca10a2b02fe334a0fed0653f5b514a6973cb61368bca45e6c91dff'
  'packaging/app-icon.svg' = '8bab7f0688c6a330a0c5128ec4e1fbabd849d2c55ed30a1ff15394ad28641ad5'
  'packaging/install-guide.html' = 'e094ae2d7e41587175f34827e0b65c7b8596f9b5684d51925ceb2a48b2636da6'
  'pyproject.toml' = '6c29e94fb46e1527b5f22aa9b5b11d476cb0037494dfb4e51884d78e122dc003'
  'scripts/build_package.py' = '5c5481ce9ca55dc2e0121a17a6f600d9383ac6d7fa8a3a0d8c2fa8fa0671172f'
  'scripts/check_docs_catalog.py' = '226a0293907b9b9b555a71d3aca5ba3b1f07369295403c3e44ee1d877efe0020'
  'scripts/compare_draft_methods.py' = '3c87c76b632c69f6b418fb39d923a10d40db0d15e4add08ac149427cf0a991f7'
  'scripts/compare_medians.py' = '947510c05253ef8081dedfac2409ca0709bc22c08bddb2dd3e0fcc8382ce6e9a'
  'scripts/inspection_summary.py' = '97fcb09ec75385f2f742ff7cdf56d6039fc3731accafaacdd0087fc6c0925318'
  'scripts/install_git_hooks.sh' = '762c1e1a4e38a99c086447b548ca071f84d29ac8e0aa0f26e8a717eb4e865008'
  'scripts/make_icon.py' = '5e7f29d28acdd8270f9892c727a60c12dc92e99e72dc10c4da354eae0649e5c4'
  'scripts/measure_editor.py' = '3436a7dab0dc9c5d56f5f7022e9e21d56b78c0b492fb39081b96c9dfc4c2e740'
  'scripts/recipe_summary.py' = '5e7e4960cfd659e1a9e887b9d0d17fd3517381b2ccd78b8e3a0f6f4968e5a8b3'
  'scripts/render_intro.py' = '01d3dfade7c0a6779b8adcb59863ce386c0ab951b54b80d49fb1f5992f3a0b65'
  'scripts/render_manual.py' = '579b24711138c1f7b9e51d00d38b8ce1c6349000599d1fe170e4d9f7283fb52f'
  'scripts/time_analysis.py' = '72079e4a094f43ac97a896098eaed749628b06a7bc5e28eb1f530410506a751d'
  'src/oil_tracker/__init__.py' = 'b8e686d843e87c0be9ee70c031566da4715b75face09f9ea5e267e9b962c9a02'
  'src/oil_tracker/__main__.py' = '4efc05fc1cffa5b074068f9bd0ab3ff84b8eaba4c70edbc5ce4d806c05a1a2d1'
  'src/oil_tracker/adapters/__init__.py' = '7b5021074fb335deb08bf8e6c61147b8380361a48f164c682d754a95975ab996'
  'src/oil_tracker/adapters/desktop/__init__.py' = '7eac15b6dc58008bfd5d1baaf133bda0cddec43805746e7ca4b3f76917b84b00'
  'src/oil_tracker/adapters/http/__init__.py' = 'b359fe08245e9086c1171d961e9c51e0575dc33b23ada7af2d087b47b38b5f47'
  'src/oil_tracker/adapters/http/api.py' = 'f77b6c7186a7b5ed0512f698daabb7290bf7e0cf52b079cd2bb391f39e7720b4'
  'src/oil_tracker/adapters/http/jobs.py' = '4b13c0d72bc1345cc0d0ab6faf40cdd029ef22526cd1f0552393c957be553f22'
  'src/oil_tracker/adapters/http/relay.py' = '0cd42f7243965b803cb34be95ee9249315332428dad509a59464f2733b1209f0'
  'src/oil_tracker/adapters/http/server.py' = '0b951a1dd7e7799ccca739951e65e0e22cda40751b548ecdffbb13fcc9275234'
  'src/oil_tracker/adapters/report/__init__.py' = '5dc9b732dcfcb111970679c96d04216181c476d34efa465f1d2c988d5ecdc5a3'
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
  'src/oil_tracker/application/manual.py' = '000f923632182a96e9901a76fd67e98b3def893782b9ae39d54f0596b6d93aa7'
  'src/oil_tracker/application/ports.py' = '372542fb3603a7598cda7e407ca9622c63fa3fc62f9f74c4562bb82fa068dd72'
  'src/oil_tracker/application/recipes.py' = '9053abc7acf8de6056697c71b6d5df965734fd82e5fa187936720a819e652cc7'
  'src/oil_tracker/application/videos.py' = 'cf4721b61ca1173c2867ba23bb29e2d885407940895e91a4b21f04c5fbf28ce6'
  'src/oil_tracker/bootstrap.py' = '2bc431e714988f9c544276b0e94952a6a0ef9e88c9812304803fbfba27af3c8f'
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
  'src/oil_tracker/web/editor.js' = 'e2af633408689c3aa62a81717f2741d858bffb401deb58dcacc545844552e825'
  'src/oil_tracker/web/frame.js' = '444689064c1f583b75982ad0fec87d8264467755e9a96a56fd5ddaccb95f35dc'
  'src/oil_tracker/web/header.js' = '7c4ed7fdf6c80479372c0596c3357e699e8bae232fdb2f164665f7e025c96728'
  'src/oil_tracker/web/index.html' = '6605b01198ed5711f25bc4463d9064b9cd26598e0bcd258ef5668ede20e95c72'
  'src/oil_tracker/web/inspections.js' = 'b9e61fea39cc76fb246ddf312282b3bffc651f7a2403fa316149405c41de4125'
  'src/oil_tracker/web/lines.js' = '365ca0249a01c0c208bfb3487f58b911534e565321e43ce8e146924d35ad4663'
  'src/oil_tracker/web/main.js' = '4c4c26bb1de7e0a86fb1b4b77301366f9979f0b16e5551cab65ad427a8502137'
  'src/oil_tracker/web/manual/clips/grab.mp4' = 'c31978702df9f5c0c6bdab8b70bb2921a8ddf74e3696e886fb266096fd52df44'
  'src/oil_tracker/web/manual/clips/pencil.mp4' = '3e1839f255a725eb3866b9cf3255501055c3a5ec1e0c485a228c2dd557cd5bce'
  'src/oil_tracker/web/manual/clips/points.mp4' = '71f072cb803b2b8a538ec0ea40cc908f4648acd3b7e5d5bbc4147e8fc91935c7'
  'src/oil_tracker/web/manual/clips/range-delete.mp4' = '8aa892990677f25f98254ca9654ea8fb682653e5d46a85b92c9c19b23cc14a41'
  'src/oil_tracker/web/manual/clips/recipe-glass.mp4' = '0a12fdb6009601575d625e60af32b82613866f9f26e770ef1c81a7840afeefa0'
  'src/oil_tracker/web/manual/clips/view.mp4' = '2ea8a42cb4ff8ecd0a53f57f83b923bf8cd5e4a8f07bf7fca20fc51a150a7bb7'
  'src/oil_tracker/web/manual/img/background.webp' = '277103208c87f070031ad98b575f35869bb67b1cb398e28162932acaa093d85e'
  'src/oil_tracker/web/manual/img/cannot-judge.webp' = '7489baccc0e5830212a79badeba14c273384e3344b119c64981e1a14a6ef92b0'
  'src/oil_tracker/web/manual/img/checked.webp' = 'dddc1ff1c1af1be0575d8cb4b6db20992ff79dca39939c1b3b5f1dd8a765c09c'
  'src/oil_tracker/web/manual/img/copy.webp' = '5f556198d0d91658cbc43ff0cd83911a9d90dbc2741523f56e47af1170665af2'
  'src/oil_tracker/web/manual/img/editor-checked-thumb.webp' = 'c8c44d64837c3458b9ba7e29bcacecefc9e610aeb01b33809e5a6e93b774a4f4'
  'src/oil_tracker/web/manual/img/editor-checked.webp' = 'ed3603cf4965784caca538bbebeaa04d6e5b07ba607eabd05e490269776e0f53'
  'src/oil_tracker/web/manual/img/editor-thumb.webp' = '89391b8ffaf93e53edbf39790e26eba46ea015307f96d87b02e5141aff0ade10'
  'src/oil_tracker/web/manual/img/editor.webp' = 'd8848c20d26a4c759cca2d82c2e15cbb52fdc1de26f211b9fa90efebe1ef3bf5'
  'src/oil_tracker/web/manual/img/judgment.webp' = '952d89cdeafe9088977b74da60c65925a3e18f2d7442ade84a39373c492a46e4'
  'src/oil_tracker/web/manual/img/list-empty-thumb.webp' = '01b9b8342592d28069d915d76318a63b09d0030a7f346898a7f34daff812f13d'
  'src/oil_tracker/web/manual/img/list-empty.webp' = 'cdc2e827bf19c59f454a5c2d5ca9136bb3d2d6d5561dcde52ee0755acbc4bd92'
  'src/oil_tracker/web/manual/img/list.webp' = '0970402b55a4aabc12708481a2ee1b853b9296b254223992686dc192e3f9a44b'
  'src/oil_tracker/web/manual/img/memo-dialog.webp' = '8bbdb6544ac078be74c022a5c0315098d21212047020eb20ce67013010d4ebf8'
  'src/oil_tracker/web/manual/img/memo-list.webp' = 'b577c679f247705bc4a8dbd28db1d4d33ce643e99f0abcd7f5056263e73d93b6'
  'src/oil_tracker/web/manual/img/override.webp' = 'e1c04432a46d6c9bb308b2012d05c535305155bdf6bf757b58ce358e768bcac2'
  'src/oil_tracker/web/manual/img/pick-recipe.webp' = '17194bd461665d250ddecf16310c29b20dd86390efe53d0411393b92fb02234e'
  'src/oil_tracker/web/manual/img/picked.webp' = '5c9944f7ca3b3b715194ebe47341d2d3d3590af51be079dc4f8c749115926ca6'
  'src/oil_tracker/web/manual/img/progress.webp' = '87b4663080e149a7f57af957066a4b234c6b089676b20ce99cc695489a407a1e'
  'src/oil_tracker/web/manual/img/recipe-list.webp' = '28e45be62c1e217bf07413688e473a6234cecdc9c295023246eec702e5b93114'
  'src/oil_tracker/web/manual/img/recipe-new.webp' = '64d1e24caf05748b0aa184858dc25183e22c928c0d8334509f1cc471f6623e9d'
  'src/oil_tracker/web/manual/img/recipe-rule.webp' = 'e7bca8c35d0a69a17794474be7b8eb4bdf71bd644223ff2ebdab14d82e3a6ff0'
  'src/oil_tracker/web/manual/img/recipe-screen-thumb.webp' = '992dfc87caee50aeb926d04ef4b3d30e2b4b5b2912304123731ae87a59a01444'
  'src/oil_tracker/web/manual/img/recipe-screen.webp' = '8f7fd6208b43f2535881696bd64d6047b72cd13662e856f081ff77a6b733f8bd'
  'src/oil_tracker/web/manual/img/report.webp' = '5b18229ef6bf0f81a19aa74a382647066fa0d35d03bc4d4a8b001fefbb9bb2c9'
  'src/oil_tracker/web/manual/img/selection.webp' = '4963333983ff74ac6154f1d8de3b5bbfc70d9a59aa46af4979777f69a27c149f'
  'src/oil_tracker/web/manual/img/setup-fields.webp' = '5d21ed875d8e374d627afaffd99e5e8eb3d1a73e1bf52ddb7703448190043b3e'
  'src/oil_tracker/web/manual/img/setup-thumb.webp' = '85ea50bb92da8f709d9acf1c1735826739050e40be5333499fb5efd73122e901'
  'src/oil_tracker/web/manual/img/setup.webp' = '89d0955c58c8b264e45d433d83ed7e91242b2ffddcdbd8a4d08436796bdceeb3'
  'src/oil_tracker/web/manual/img/source-warning.webp' = '36666f5b9b7db75380d86bcd95cdb6e6606bf5d14dbbbb2f19ceaebc36e53aeb'
  'src/oil_tracker/web/manual/img/submit-dialog.webp' = '1d06a0edb82fee1159edf802aea094fc8e987712d8199ffeb743d4014b3c5a57'
  'src/oil_tracker/web/manual/img/submitted.webp' = '1b9629783aacaca13d5f8e3e788f41645e84bf685e7646c1305de4b533cdc2d7'
  'src/oil_tracker/web/manual/img/toolbar-checked.webp' = '150d5231496a4bd1eff9cb4170236d0b19ead3a24066eb0b8390c33ca220935c'
  'src/oil_tracker/web/manual/index.html' = '4ed0cbfbca51e99dd8bc642d884ea6b5f036219aad3cdbac990bc3ce21fa8496'
  'src/oil_tracker/web/manual/manual.css' = '8f87991407002b3e597337acce3bad0d4f335b26faa44545bbe0a0e3699e4299'
  'src/oil_tracker/web/manual/manual.js' = 'b466ac8ff3efe712560037a6ca233ec996a6348dbabdf93e6d120477551a2b40'
  'src/oil_tracker/web/nav.js' = 'b00d4e58890c6e0439a8fab85e9de1c2642b477f6e8a5a395cb4670b7c5457dd'
  'src/oil_tracker/web/player.js' = '74474ce590909371763014cde673f8fc30eb4a517e2fe0e01e5c3b716c060949'
  'src/oil_tracker/web/recipe.js' = '40e0e357f36e8724ffc9b9bca60c3f591f344f8cc19c8f27ba35c9dd0c17b588'
  'src/oil_tracker/web/render.js' = '938ae6eb5045355845c9290c488e2913e4bbc69fef5997abcd3e664b45228114'
  'src/oil_tracker/web/report.css' = '9f7bfbfad83a580c29e0b80d6917be2542fa6156c1f40d85a5d8f1da545638fe'
  'src/oil_tracker/web/report.html' = '7c35a771ac347ecbb5ae169e538f77ae5de69f23b33859eca9d4d5a42a929213'
  'src/oil_tracker/web/report.js' = 'dcc9d066de87e59008376d56fc7318b65a5d8c4188eea2c0c14cd6ebaaaf98dc'
  'src/oil_tracker/web/tokens.css' = 'b62496aefa7cb8b269d0ff1fb502fc80594c4f436c4b10f2f0ea28fb28af51c0'
  'src/oil_tracker/web/ui.js' = '1711ee95e43b48e79e7e6cdd34457a21fb0549d338fd28bbb1732ed458f641ce'
  'src/oil_tracker/web/video-window.js' = '9a01cd86c9b2e176fa3d02bbed6f459638e9ae393ca242010930ff62f96fe469'
  'src/oil_tracker/web/video.html' = 'd96e42745c810a6209f5e19c99eabb730cfbdf9d42a45f90eac15e4be2c8bed5'
  'src/oil_tracker/web/videolink.js' = '8070edc5c61d1b6522321f0eeea3686f489761063f8921eca6fb3ab7978e3a2d'
  'tests/test_app.py' = 'a8078d73f08515814c0da1d84635bdf3cf8f4fa084b5864863aef0f1720de846'
  'tests/test_app_icon.py' = '35031cff80216ce395ab8ff729dbcae3f1c9a674e47432f8c7c4e66e707e1b2f'
  'tests/test_application_editing.py' = 'fe2385457b3c73fe694e2ded3512c89ba603553a69fd6e914c71e4513e8880ee'
  'tests/test_application_inspections.py' = '61be939f7c862c92b05552f9460293b248cd6d52a7990829af3f57cdcd670454'
  'tests/test_application_recipes.py' = '154b61e3cf6e4aa81a68e2165f51e569eb7a78889207e617b273136f1c16cde8'
  'tests/test_architecture.py' = '42910fb569bd010342747d081d1c0cac7aa8c9f2641af24da92a2f4ab5317288'
  'tests/test_build_package_script.py' = '88bdc8e32e0abe57c949986fb14055b3aa1bd082f5562d844572eac860947eb0'
  'tests/test_compare_medians_script.py' = '3ced7c6a8096de3411be5f7fbc7db57a86ad81f531da41d3c418937b205ba119'
  'tests/test_docs_catalog.py' = 'bf999036473a5924f1ef312ab7e93e0b972819f5f6c167242a023996725fc4be'
  'tests/test_domain_edits.py' = '0df182eeb5cacbe1ffd51afed77427cd7411c8ceda2203628065f5bbb61f1fe3'
  'tests/test_domain_inspection.py' = '620ae6feae8f54bfa8fcb5ab7fc0fa23bb68b1545373b58c08f6af4b71c02db4'
  'tests/test_domain_judgment.py' = '1518d7eb6c234793e67fbe4a5eb4fdad94e6036669eb275233d1d7abcac0ef13'
  'tests/test_domain_recipe.py' = 'cb734519d22a238079f1cbdba7b0ecffb580f4b7ae6d2de0f60315bd8845a829'
  'tests/test_http_api.py' = 'fe5c949f1111a1ee85febe2326610a4d294f5f17fd2c2ef7a0d7385cba204724'
  'tests/test_http_jobs.py' = 'fd538c2d448228f847ac1d201b47e133026bf66c9fb104a4cc11049f724c2d33'
  'tests/test_http_relay.py' = '236ec206ad92ad23eb1c20d4c23e8b11f03355b9344fddbfee050fdeb0160e8a'
  'tests/test_inspection_summary_script.py' = 'b95e84e4e704fd053e8e89ee252d0906c95ae87fea03b5a4cb68860f8fd19bc2'
  'tests/test_manual.py' = '0a7069b0c4c45296c1a52e2a194304f177fb68faf8764d248846c71ddccebd7f'
  'tests/test_measure_editor_script.py' = 'd193a60fc745b51ba74d5977a993d561fc64350aed96e126ba7a96245ff83543'
  'tests/test_package.py' = '8d458fbb772dcd6a825e060c8fdcdad2eb7716a8f72ef6df8c3d437026f063f8'
  'tests/test_recipe_summary_script.py' = 'f90b3adff4b1fb43ae28ae2aead9c56c55f7dc22c09b10f8bf030e1a9598748b'
  'tests/test_report.py' = 'f35321389138aa734128a4c17d5240c81ad0adc821d749486048bd7b10f70c66'
  'tests/test_storage_inspection_files.py' = '9acace3734a6fcab6edbe2329214cc665d528c0e1e2880ef92395f6d9e32f323'
  'tests/test_storage_recipe_files.py' = 'e784cacbad6b421ef8426a448d1e9661f8c05daf7b238930a3c52a5c77a50288'
  'tests/test_time_analysis_script.py' = '5e3659ac7b9810095eeefc14511b190e8e8eb398143f8e13b25cf463e07a1ac0'
  'tests/test_video_analysis.py' = 'ec97c4ed0d328ea42f2ae233168667cb40014decd172712cca01092f83a30d98'
  'tests/test_video_context.py' = '47115a4f03a31b3b491a136b519c9809497e3ef7289c19ec203b656ec1d6765e'
  'tests/test_video_frames.py' = '02f4c4495486e21ef5ff78ce9df8ba8334ce00d7dbc1a66e4b50f21101add21b'
  'tests/test_video_trace.py' = '28e2444339976b194025dda134bc30db8d1409964badc08b28619ee0c50a5c64'
  'tests/test_web_inspection_smoke.py' = '5d1d4052a1d5d647537a357f59d30a4475f362549192353e02da0ce0fd83c726'
  'tests/test_web_recipe_smoke.py' = 'cfe24b5388ea6f4e9720cfc4ee0be7b0395002c00049ec1f1fe41bce04b13038'
  'tests/test_web_tokens.py' = 'cbb3d1c76b5be1f20f9b56c2e74837d7a69fc793c1fe767566e9da628f19234c'
}
$bad = 0
foreach ($k in $expected.Keys) {
  $h = (Get-FileHash -Algorithm SHA256 -LiteralPath $k).Hash.ToLower()
  if ($h -ne $expected[$k]) { "MISMATCH $k $h"; $bad++ }
}
"checked=$($expected.Count) mismatched=$bad"
```

## 2. 환경 [에이전트]

```powershell
py -3.14 -m venv .venv-v2
.venv-v2\Scripts\python -m pip install -e ".[package]" pytest
.venv-v2\Scripts\python --version
$log = Join-Path $env:LOCALAPPDATA 'OilLevelTracker\app.log'
$logStart = if (Test-Path -LiteralPath $log) { (Get-Content -LiteralPath $log).Count } else { 0 }
"log_lines_before=$logStart"
```

## 3. 테스트 [에이전트]

```powershell
.venv-v2\Scripts\python -m pytest -q
```

마지막 줄을 원문으로 적는다. 기대값은 `271 passed, 4 skipped`이다. 실패가 있으면 이름과 마지막 30줄.

## 4. 빌드와 배포판 ZIP [에이전트]

```powershell
.venv-v2\Scripts\python scripts\build_package.py --release
```

`version=` 줄부터 마지막 `package=` 줄까지 전부 원문으로 적는다(`INFO` 줄은 옮기지 않는다).

## 5. exe 속성과 ZIP 구성 [에이전트]

```powershell
$exe = Get-Item 'build\dist\OilLevelTracker\OilLevelTracker.exe'
"product=$($exe.VersionInfo.ProductName) product_version=$($exe.VersionInfo.ProductVersion) file_version=$($exe.VersionInfo.FileVersion)"
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [IO.Compression.ZipFile]::OpenRead((Resolve-Path 'build\release\OilLevelTracker-2.0.0.zip').Path)
$guide = (-join [char[]](0xC124, 0xCE58, 0x20, 0xC548, 0xB0B4)) + '.html'
$top = @($zip.Entries | ForEach-Object { ($_.FullName -split '/')[0] } | Sort-Object -Unique)
"zip_entries=$($zip.Entries.Count) top_count=$($top.Count) guide_name_ok=$($top -contains $guide) app_folder_ok=$($top -contains 'OilLevelTracker')"
$zip.Dispose()
```

## 6. ZIP을 새 폴더에 풀어 실행 [에이전트]

```powershell
New-Item -ItemType Directory -Force -Path 'C:\olt-p2b\ws2' | Out-Null
Expand-Archive -LiteralPath 'build\release\OilLevelTracker-2.0.0.zip' -DestinationPath 'C:\olt-p2b\ws2' -Force
(Get-ChildItem -LiteralPath 'C:\olt-p2b\ws2').Count
Start-Process -FilePath 'C:\olt-p2b\ws2\OilLevelTracker\OilLevelTracker.exe'
```

## 7. 확인 [사용자]

각 항목에 **O / X**와 한 줄 소감을 남긴다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| H1 | 6절에서 열린 앱에서 `V25b 선택 확인`을 연다(제출한 v1, 읽기 전용). `F1` | 제목이 "도움말 · 편집기"이고, **모든 줄이 한 줄**인지. "도구"와 "보기" 두 묶음 뒤에 **"…자세한 설명은 "사용 설명서"에 있습니다."** 한 줄이 있는지. 아래에 "버전 2.0.0". **이 정도면 충분히 짧은지** 소감을 남긴다 |
| H2 | 도움말 창의 **"사용 설명서"** | Edge로 설명서가 열리는지 |
| H3 | 앱 창의 X로 앱을 닫는다. `build\release\OilLevelTracker-2.0.0.zip`을 `C:\0.Coding\0.Release\`에 복사해 **앞 실행의 ZIP을 덮어쓴다** | 덮어쓴 뒤 그 파일의 SHA-256(아래 명령)이 4절 `zip_sha256`과 같은지 |

```powershell
(Get-FileHash -Algorithm SHA256 'C:\0.Coding\0.Release\OilLevelTracker-2.0.0.zip').Hash.ToLower()
```

## 8. 로그 [에이전트]

앱을 닫은 뒤 실행하고, 출력을 전부 원문으로 적는다.

```powershell
Get-Content -LiteralPath $log | Select-Object -Skip $logStart
```

## 최저 사양 PC

이번에는 하지 않는다. 설치 과정과 설치 안내는 앞 실행에서 확인했고 바뀌지 않았다. 그 PC에 설치된 2.0.0은 앞 ZIP(`920dfbef…`)이다. 시험용으로 두어도 되고, 새 ZIP으로 바꾸려면 설치 안내의 "새 버전으로 바꾸기"대로 한다.

## 통과 기준 (실행 전에 고정)

| ID | 통과 조건 |
|---|---|
| R | 0절에서 다른 줄이 모두 `V25b 선택 확인`의 줄이거나, `sha256_check=video_missing`이 `sha256_check=same`으로 바뀐 줄뿐이다(사용자가 옮겼다 되돌린 영상). `=>` 쪽에 `V25b 선택 확인`의 `version v=1` 줄이 있다. 마지막 줄이 `checks_after=7 same_after=7` |
| S1 | 1절 마지막 줄이 `checked=154 mismatched=0` |
| S2 | 3절 마지막 줄이 `271 passed, 4 skipped` |
| P | 4절에 `version=2.0.0`, `package=PASS`, `size_mb` 200 이하, `package_files_changed=0`, `zip=` 줄이 있다 |
| Z | 5절이 `product=Oil Level Tracker product_version=2.0.0 file_version=2.0.0`이고, `top_count=2 guide_name_ok=True app_folder_ok=True`, `zip_entries`가 4절 `files` 값보다 1 크다. 6절의 수가 `2` |
| H | H1–H2가 모두 O이고, H3의 해시가 4절 `zip_sha256`과 같다 |
| T | 8절에 `Traceback` 줄이 없고, 이번 `start:` 줄이 모두 `start: 2.0.0 (build)` |

## 결과 양식

```text
[R] 0절 출력 원문 (모든 줄):
[S1] 1절 마지막 줄 = ; MISMATCH 줄 =
[env] python =
[log-before] log_lines_before=
[S2] pytest 마지막 줄 =
[4] 빌드 출력 원문 (version= 줄부터 package= 줄까지):
[5] 출력 원문 (두 줄):
[6] 폴더 항목 수 =
[H1] O/X ; 충분히 짧은가 = ; 소감 =
[H2] O/X ; 소감 =
[H3] 해시 = ; O/X
[8] 로그 원문:
[소감] =
```
