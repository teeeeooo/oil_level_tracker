# Windows 요청: V2-4 판정·제출·보고서 확인 (2026-10-30)

> 이 문서는 **Windows 워크스테이션에서 실행**하기 위한 요청이다.
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다. 요약하거나 줄을 줄이거나 직접 합계를 내지 않는다.
> - **[사용자]** 표시: 사용자가 앱 창과 브라우저에서 직접 조작하고 판단한다.
> - **통과 기준**은 아래 "통과 기준" 절에 있고, 실행 전에 고정됐다. 판정은 이 문서를 만든 쪽이 한다. 에이전트는 원문만 옮긴다.
> - 결과 파일은 Windows에 남기고, 맨 아래 **결과 양식**만 텍스트로 돌려준다.

## 무엇을 확인하나

V2-4에서 만든 것(Product SSOT §3·§5·§7)과 V2-3 재확인 뒤에 고친 두 가지를 본다. 시간 측정은 하지 않는다.

- **판정:** Glass마다 자동 판정(합격·불합격·검토 필요)과 그 근거, 사용자의 직접 판정(이유 필수), "이 Glass 확인". 확인한 뒤 그 Glass의 Oil 선을 고치면 확인이 풀린다.
- **검사 정보(보고서 머리글):** 압축기 모델과 시험 종류. 고치면 바로 저장된다.
- **제출과 버전:** 모든 Glass를 확인해야 "제출"이 켜진다. 제출한 버전은 읽기만 되고, "고쳐서 다시 제출"로 다음 버전을 고친다. 버전은 검사 폴더의 `versions\001`, `002`, …에 쌓인다.
- **보고서:** 제출할 때 `versions\NNN\report.html`이 생긴다. 한 파일로 오프라인에서 열리고, 브라우저에서 인쇄하면 A4 가로 PDF가 된다. 직접 판정한 Glass에는 "판정 사유:" 한 줄만 있고 "덮어씀"이라는 말은 없다. 68분 영상도 5 MB 이하(A7).
- **V2-3 후속(아직 Windows에서 못 봄):** 연필 "수평·수직"으로 거의 세로로 끌면 세로선이 된다. 점 잇기는 스냅을 켜면 두 점을 곧게 이은 선에서 8 px 안의 경계만 따른다(이미지 위·아래 끝으로 붙지 않는다).

워크스테이션의 `OilLevelTracker\Inspections`에 검사 4개가 있다. 이번에는 두 개만 쓴다.
- **`20261029-1907_SPL#4_Cooling_onoff_#2`**(Glass BASE, ACCUM, 편집한 적 없음): 판정, 제출 두 번(v1, v2), 보고서.
- **`20261029-1913_SPL#1_Heating_coldstart`**(V2-3에서 편집함, 예전 형식 파일): V2-3 후속, 제출 한 번, 68분 보고서.
- `20261029-1910_SPL#1_Heating_coldstart`과 `V2-3 확인`은 열지 않는다. Recipe는 고치지 않는다.

**제출은 되돌릴 수 없다**(앱은 버전을 지우지 않는다). 그래서 1절에서 검사 폴더를 먼저 복사해 둔다.

## 0. 소스 확인 [에이전트]

1. **커밋 하나로 고정된 ZIP**을 받는다:
   `https://github.com/teeeeooo/oil_level_tracker/archive/95de0641e7a3ee983e372a7d950004e83ec98a99.zip`
   **새 폴더**에 압축을 풀고(`oil_level_tracker-95de064…`) 그 폴더를 저장소 루트로 쓴다. 이전 실행의 폴더는 쓰지 않는다.
2. 저장소 루트에서 아래를 그대로 실행한다. 마지막 줄이 `checked=95 mismatched=0`이면 된다. `MISMATCH` 줄이 있으면 그 줄을 전부 원문으로 적는다.

```powershell
$expected = @{
  'DESIGN.md' = '196fa14a0f89fe74eda071f7cbb3947934cbaab6896b8007ec91791b0d6cb88a'
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
  'src/oil_tracker/adapters/desktop/__init__.py' = 'b22476cf640dd1af5930bedd04de759464331ef45fb32f2856ef5c68957f8363'
  'src/oil_tracker/adapters/http/__init__.py' = 'b359fe08245e9086c1171d961e9c51e0575dc33b23ada7af2d087b47b38b5f47'
  'src/oil_tracker/adapters/http/api.py' = '1c09ceaac6e98fd99ee534b4ef04d82d23917c77ade0969318b4d890df0c4cf1'
  'src/oil_tracker/adapters/http/jobs.py' = '4b13c0d72bc1345cc0d0ab6faf40cdd029ef22526cd1f0552393c957be553f22'
  'src/oil_tracker/adapters/http/server.py' = '0b951a1dd7e7799ccca739951e65e0e22cda40751b548ecdffbb13fcc9275234'
  'src/oil_tracker/adapters/report/__init__.py' = 'd9a20111969eb61283aae27ed1f1a252f9cd0e2836ccf47948badaa019a4e4c3'
  'src/oil_tracker/adapters/storage/__init__.py' = '5253f99b1985be481fe2837d01fc0533ecaed8103268631c3f2a2ccb8399a4aa'
  'src/oil_tracker/adapters/storage/files.py' = 'bed95d9f399133b31fbc853ee64c66fc20c69edcd50aab8bcfdf8a70d2cb36cb'
  'src/oil_tracker/adapters/storage/inspection_files.py' = 'bb858a665e3a79eb96fa2d472cbbc6dc0fd5f81ed53c648502c01d658f653340'
  'src/oil_tracker/adapters/storage/locations.py' = '54951aaf5cdfc94c5b9325ffe1a0017908790a85ac275f2a5c868d71262e1f0c'
  'src/oil_tracker/adapters/storage/recipe_files.py' = '8d6caa3b04d4c5301083de0afe900230732c39de7f07b1d5434a29e4491ca8ab'
  'src/oil_tracker/adapters/storage/values.py' = '41e214903650422c8c6ec77281ef25cb186b39c968317c08c22caa1a7009622a'
  'src/oil_tracker/adapters/video/__init__.py' = '7499b2d549136a86fbff18ea219095c124c22d83bbd6f750df692b9fed7967c1'
  'src/oil_tracker/adapters/video/analysis.py' = 'a9c1e37eda63c9b6bea1c70f4c5c0e557b81e904849ee7a8903324cd94280f35'
  'src/oil_tracker/adapters/video/context.py' = '923c0b3ba4015186dfed950d07c542f142b12f3ad7711561be4abed4cd68f548'
  'src/oil_tracker/adapters/video/draft.py' = '6de7034bf07c9fda6854a2941875217f4f7f3412db16a924ee9a36c4e5fb4532'
  'src/oil_tracker/adapters/video/frames.py' = '38357bf3f8abaf668a3e77c4a2375aad23c216667aa97733d591c6cb137fc3cb'
  'src/oil_tracker/adapters/video/trace.py' = '56df0c7552993c40ba4913706cc49de5318675af64f1b7f0db49105f5d1e4a27'
  'src/oil_tracker/app.py' = '4465ee560f09a0e14ac27cd72ffa55d5d0879cf35bb3684a94712d46af77be46'
  'src/oil_tracker/application/__init__.py' = 'c7de6525842604180e0f82b532883bece026ac01a556d364caf4c6d7ea0d0253'
  'src/oil_tracker/application/editing.py' = '64d4b08bbaccbeb56a38c52f8ba187261b5d74d596b57fc98cef4c947db2a1eb'
  'src/oil_tracker/application/inspections.py' = '12aabd7c926d47021dbbbbbab91ff6693d7eb9f354ba34eee6b20e54e431d573'
  'src/oil_tracker/application/ports.py' = '232f9672714afefe68096421108fc1a156a472e87f19da919bc9944b010bc2f5'
  'src/oil_tracker/application/recipes.py' = '9053abc7acf8de6056697c71b6d5df965734fd82e5fa187936720a819e652cc7'
  'src/oil_tracker/application/videos.py' = 'cf4721b61ca1173c2867ba23bb29e2d885407940895e91a4b21f04c5fbf28ce6'
  'src/oil_tracker/bootstrap.py' = '7813d5da7fe051abf29821fcc39d309b57dcae1b613c0c7a840a5b3fa9149f69'
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
  'src/oil_tracker/web/api.js' = '5c86367d4cce1d6cd2b16c5a2768d787ed5d58158b994b01988cc3c95f8ada89'
  'src/oil_tracker/web/app.css' = '60fdcfc73d496fe024992f842df01a3b1dded050517442f2e4775f9f3e70ffaf'
  'src/oil_tracker/web/editor.js' = 'd142a3576911a4e06af3bfe50a8d80999c15d268b3f76baf8f3e6c4d955f0f4d'
  'src/oil_tracker/web/frame.js' = '444689064c1f583b75982ad0fec87d8264467755e9a96a56fd5ddaccb95f35dc'
  'src/oil_tracker/web/header.js' = '7c4ed7fdf6c80479372c0596c3357e699e8bae232fdb2f164665f7e025c96728'
  'src/oil_tracker/web/index.html' = '6ed1d7f45cd08ef1fa97fd24e3f7f2c7e9236cf6193184587a44d981d687efd4'
  'src/oil_tracker/web/inspections.js' = 'd2d0efde4ffefc355ea323373fd17f806c0dffd66ad4278feb6d45850cc7263c'
  'src/oil_tracker/web/lines.js' = '84a4b3c3597f692c3f5688548b14dea27432d5f5b407321ef653932230048cc9'
  'src/oil_tracker/web/main.js' = '4c4c26bb1de7e0a86fb1b4b77301366f9979f0b16e5551cab65ad427a8502137'
  'src/oil_tracker/web/nav.js' = 'f06641803602beefae7c67a473daeffa9a9b5eec63f65b7cb0829954529af267'
  'src/oil_tracker/web/player.js' = 'e4acc63b72d574d61eea175e9639f0b2cfafce437a2e2ce5261527fdb00818d3'
  'src/oil_tracker/web/recipe.js' = '40e0e357f36e8724ffc9b9bca60c3f591f344f8cc19c8f27ba35c9dd0c17b588'
  'src/oil_tracker/web/render.js' = '259fec355a4c0237f130811a1cef034e2721c8ef5b6018784d1786a480ea5060'
  'src/oil_tracker/web/report.css' = '6d1b8c624f8cc52b24c278b9a8cf7b231e7a50292eeb0534b9a7eeb4b4d4af79'
  'src/oil_tracker/web/report.html' = '7c35a771ac347ecbb5ae169e538f77ae5de69f23b33859eca9d4d5a42a929213'
  'src/oil_tracker/web/report.js' = 'a41b05415e938b5e80efbeb1e7f9f08a2f6ebeb339a680e1cbae436a695d1f12'
  'src/oil_tracker/web/tokens.css' = 'b16f5ca2d9ccd1b58c48ac2e43db7ebb544434f7474b226e43f53ecbc804e04c'
  'src/oil_tracker/web/ui.js' = '1711ee95e43b48e79e7e6cdd34457a21fb0549d338fd28bbb1732ed458f641ce'
  'tests/test_app.py' = '51fd947f25dc46ff49d0247a08bec15cb8fc0c26db9ddac717c99776346c265f'
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
  'tests/test_http_api.py' = '61afc620856ccb73d8bfe1b3afc54061c5aff74d21c1fe93b9add4471d485aca'
  'tests/test_http_jobs.py' = 'fd538c2d448228f847ac1d201b47e133026bf66c9fb104a4cc11049f724c2d33'
  'tests/test_inspection_summary_script.py' = 'b95e84e4e704fd053e8e89ee252d0906c95ae87fea03b5a4cb68860f8fd19bc2'
  'tests/test_measure_editor_script.py' = '430c3960fc8e93f33b5b3dd6d3a684baf89df2768f71aca0dd211f36b65fd281'
  'tests/test_package.py' = '8d458fbb772dcd6a825e060c8fdcdad2eb7716a8f72ef6df8c3d437026f063f8'
  'tests/test_recipe_summary_script.py' = 'f90b3adff4b1fb43ae28ae2aead9c56c55f7dc22c09b10f8bf030e1a9598748b'
  'tests/test_report.py' = '2b5b83650907ca4bca0ff8fc59d141e64e80073f04568e9e168a0848d68f8642'
  'tests/test_storage_inspection_files.py' = '9acace3734a6fcab6edbe2329214cc665d528c0e1e2880ef92395f6d9e32f323'
  'tests/test_storage_recipe_files.py' = 'e784cacbad6b421ef8426a448d1e9661f8c05daf7b238930a3c52a5c77a50288'
  'tests/test_time_analysis_script.py' = '5e3659ac7b9810095eeefc14511b190e8e8eb398143f8e13b25cf463e07a1ac0'
  'tests/test_video_analysis.py' = 'ec97c4ed0d328ea42f2ae233168667cb40014decd172712cca01092f83a30d98'
  'tests/test_video_context.py' = '47115a4f03a31b3b491a136b519c9809497e3ef7289c19ec203b656ec1d6765e'
  'tests/test_video_frames.py' = '02f4c4495486e21ef5ff78ce9df8ba8334ce00d7dbc1a66e4b50f21101add21b'
  'tests/test_video_trace.py' = '28e2444339976b194025dda134bc30db8d1409964badc08b28619ee0c50a5c64'
  'tests/test_web_inspection_smoke.py' = '08542e332e809a3c5abe900b7ea7325edfb80f1f750133e77d23307f08258390'
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

이 폴더에 **앱용 venv 하나**만 만든다(Playwright를 넣지 않는다. 넣으면 2절의 테스트 수가 달라진다).

```powershell
py -3.14 -m venv .venv-v2
.venv-v2\Scripts\python -m pip install -e . pytest
.venv-v2\Scripts\python --version
```

검사 폴더를 통째로 복사해 둔다. 마지막 줄의 두 수가 같으면 된다.

```powershell
$src = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'OilLevelTracker\Inspections'
Copy-Item -LiteralPath $src -Destination 'C:\olt-v24-backup\Inspections' -Recurse
"files_src=$((Get-ChildItem -LiteralPath $src -Recurse -File).Count) files_backup=$((Get-ChildItem -LiteralPath 'C:\olt-v24-backup\Inspections' -Recurse -File).Count)"
```

## 2. 테스트 (S2) [에이전트]

```powershell
.venv-v2\Scripts\python -m pytest -q
```

- 마지막 줄을 원문으로 적는다. 기대값은 `242 passed, 4 skipped`이다(브라우저 테스트 세 모듈과 Windows에서 건너뛰는 하나).
- 실패가 있으면 실패한 테스트 이름과 출력 마지막 30줄을 원문으로 적는다.

## 3. 실행 전 검사 목록 [에이전트]

출력을 **전부 원문으로** 적는다. 읽기만 한다. SHA-256을 다시 계산하므로 몇 초 걸린다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
```

- 이번 스크립트는 검사마다 `header` 줄(보고서 머리글)을 더 찍고, `edits glass` 줄 끝에 직접 판정(`override=`), 이유 글자 수(`reason_chars=`), 확인 여부(`checked=`)를 더 찍는다. 제출한 버전이 있으면 `version` 줄이 나온다.

## 4. 앱 실행 [에이전트 → 사용자]

```powershell
.venv-v2\Scripts\python -m oil_tracker
```

- 창이 열리면 **[사용자]**가 5절을 진행한다. 창은 최대화해서 쓴다.
- 앱이 도는 동안 **콘솔에 나온 줄을 전부** 원문으로 적는다(창을 닫을 때까지). 없으면 "없음".

## 5. 앱 창과 브라우저에서 직접 조작 [사용자]

각 항목에 **O / X**와 한 줄 소감을 남긴다. 키 입력은 그래프나 빈 곳을 한 번 누른 뒤에 한다(입력 칸에 커서가 있으면 키가 글자로 들어간다). 막히면 **F1**로 도움말을 연다.

### SPL#4: 판정, 제출, 보고서

검사 목록에서 **`20261029-1907_SPL#4_Cooling_onoff_#2`**의 "열기"를 누른다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| J1 | 오른쪽 "판정 · BASE" 칸과 툴바의 Glass 고르기, "제출" 단추를 본다(단추에 마우스를 올린다) | 큰 판정 배지(합격·불합격·검토 필요)와 이유 한 줄, 근거 표(압축기 기동, 판정 규칙의 측정값, 유효 비율)가 있는지. Glass 고르기가 "BASE · 확인 전", "ACCUM · 확인 전"인지. "제출"이 꺼져 있고 "남은 Glass: BASE, ACCUM"이라고 하는지 |
| J2 | 오른쪽 "검사 정보"에서 압축기 모델에 `V24-모델`, 시험 종류에 `V24-시험`을 넣고 Enter | 입력한 대로 남는지(따로 저장 단추를 누르지 않는다) |
| J3 | Glass를 **ACCUM**으로 바꾼다. "덮어쓰기"에서 지금 배지와 **다른** 판정(합격이면 불합격, 아니면 합격)을 누르고, 이유를 비운 채 "이 Glass 확인" | "직접 판정한 Glass는 이유를 써야 확인할 수 있습니다." 알림이 나오고 확인되지 않는지 |
| J4 | 이유 칸에 `V24 확인용 직접 판정`을 넣고 "이 Glass 확인" | "✓ 확인함 HH:MM"이 나오는지. 배지가 고른 판정이고 옆에 "직접 판정 · 자동 판정은 …"이 있는지. Glass 고르기가 "ACCUM · (고른 판정)"인지 |
| J5 | Glass를 **BASE**로 바꾸고 "이 Glass 확인". 그다음 `G`(잡아끌기)로 BASE의 Oil 선을 조금 위로 끈다 | 끈 뒤 확인이 풀려 "이 Glass 확인"이 다시 나오고, Glass 고르기가 "BASE · 확인 전"인지 |
| J6 | "이 Glass 확인"을 다시 누르고 "제출" | "v1 제출" 창에 BASE와 ACCUM의 판정과 확인 시각, ACCUM 옆에 "직접 판정 (자동: …)", 압축기 모델 `V24-모델`과 시험 종류 `V24-시험`, `versions\001\report.html`이라는 설명이 있는지 |
| J7 | 창에서 "제출" | 툴바 아래 파란 막대에 "v1을 제출했습니다."가 나오는지. 도구 단추와 "저장"이 꺼지고 "편집" 칸이 사라졌는지. `P`를 눌러도 도구가 바뀌지 않고, 그래프를 끌면 보기만 움직이는지. 검사 정보 두 칸이 회색이고 눌러도 고칠 수 없는지 |
| J8 | 툴바의 "보고서 열기" | 기본 브라우저에 보고서가 열리는지. 1쪽: 제목 "오일 레벨 검사 보고서", 오른쪽 "v1", 압축기 모델 `V24-모델`, 시험 종류 `V24-시험`, 영상 파일, Recipe, 분석 범위, 압축기 기동, 판정 표 2줄, BASE의 그래프·맥락 이미지·시간축·두 표. 2쪽: ACCUM 제목 아래 **"판정 사유: V24 확인용 직접 판정" 한 줄**. 보고서 어디에도 **"덮어씀"이 없는지** |
| J9 | 브라우저에서 `Ctrl+P` | 미리 보기가 **A4 가로 2쪽**이고 배지 색과 그래프, 맥락 이미지가 보이는지. 인쇄는 하지 않고 닫는다. 브라우저 탭도 닫는다 |
| J10 | 앱에서 "← 검사 목록" | 1907 줄 상태가 "v1 제출함"이고 아래에 "BASE … · ACCUM …"(최종 판정)이 있는지 |
| J11 | 1907을 다시 "열기". 막대의 "고쳐서 다시 제출 (v2)…"을 누르고 묻는 창에서 확인 | 막대가 "v2을 고치는 중입니다."로, 제목 옆이 "v2 고치는 중 · …"으로 바뀌는지. 도구와 "편집" 칸이 돌아오고, 두 Glass가 확인된 채인지 |
| J12 | 막대의 "버전"에서 "v1 제출함 …"을 고른다. 다시 "v2 고치는 중"을 고른다 | v1은 읽기만 되고 "고쳐서 다시 제출" 단추가 없는지. v2로 돌아오면 도구가 다시 켜지는지 |
| J13 | 검사 정보의 시험 종류를 `V24-시험2`로 바꾸고 Enter. "제출" → 창에서 "제출" | 창 제목이 "v2 제출"이고 시험 종류가 `V24-시험2`인지. 제출 뒤 막대가 "v2을 제출했습니다."인지 |
| J14 | "보고서 열기" | 보고서 오른쪽 위가 "v2"이고 시험 종류가 `V24-시험2`인지. 브라우저 탭을 닫는다 |

### SPL#1: V2-3 후속과 68분 보고서

"← 검사 목록"에서 **`20261029-1913_SPL#1_Heating_coldstart`**의 "열기"를 누른다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| J15 | 화면을 본다 | 제목 옆이 "저장함 …"이고 지난 편집(메모 핀, 옮긴 기동)이 그대로인지. 판정 칸에 배지와 근거가 있고 Glass 고르기가 "BASE · 확인 전"인지. 검사 정보 두 칸이 비어 있는지 |
| U1 | 휠로 1–2분쯤 보이게 확대한다(지난 편집과 겹치지 않는 곳). "그릴 선" Oil, `P`(연필), 오른쪽 "수평·수직" 켜기. 선에서 **거의 세로로** 위나 아래로 짧게 끈다. "수평·수직" 끄기 | 누른 높이에서 포인터 높이까지 **세로선**(샘플 한 칸 폭의 계단)으로 그려지는지. 뾰족한 점이나 사선이 아닌지 |
| U2 | 스냅이 켜졌는지 확인한다("스냅" 켬). `L`(점 잇기). 그래프 아래 빨간 막대(빈 구간)나 선이 흐린 곳의 **양쪽**에 점 두 개를 30초–2분 떨어지게 찍고 `Enter` | 이어진 Oil 선이 두 점을 곧게 이은 선 가까이(8 px 안)에 있고, 맥락 이미지의 **위·아래 끝으로 붙지 않는지** |
| J16 | "이 Glass 확인" → "제출" → 창에서 "제출" | 막대가 "v1을 제출했습니다."인지 |
| J17 | "보고서 열기" | 68분 전체의 그래프와 맥락 이미지가 그려지는지. 열리는 데 몇 초 이상 걸리면 소감에 적는다. 브라우저 탭을 닫는다 |
| J18 | 앱 창의 X | 묻지 않고 닫히는지 |

마지막으로 **전체 소감**을 한두 줄 남긴다.

## 6. 결과 확인 [에이전트]

앱을 닫은 뒤 실행하고, 출력을 **전부 원문으로** 적는다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
```

- `version v=N` 줄의 `report_bytes=`는 그 버전 보고서 파일의 바이트 수다.
- `version glass` 줄은 제출한 판정이다: 최종(`verdict=`), 자동(`computed=`), 직접 판정(`override=`, 없으면 `-`), 이유 글자 수, 확인 시각.

## 통과 기준 (실행 전에 고정)

| ID | 통과 조건 |
|---|---|
| S1 | 0절 마지막 줄이 `checked=95 mismatched=0` |
| B | 1절 백업 줄의 `files_src`와 `files_backup`이 같다 |
| S2 | 2절 마지막 줄이 `242 passed, 4 skipped` |
| C | 5절의 J1–J18, U1, U2가 모두 O |
| T | 4절 콘솔에 `Traceback` 줄이 없다(창을 닫을 때까지) |
| R1 | 6절이 `inspections=4 unreadable=0` |
| R2 | 6절의 `20261029-1907_SPL#4_Cooling_onoff_#2`: `header` 줄이 `compressor_model="V24-모델" test_type="V24-시험2"`; `version v=1`과 `version v=2` 줄이 있고 둘 다 `report_bytes`가 1 이상; 두 버전 모두 ACCUM의 `version glass` 줄이 `override=`가 `-`가 아니고 `reason_chars=13`, BASE 줄이 `override=-`; 그 검사에 `edits none` 줄이 있다(v2를 제출해 작업본이 없다) |
| R3 | 6절의 `20261029-1913_SPL#1_Heating_coldstart`: `version v=1` 줄 하나, 그 `report_bytes`가 1 이상 5000000 이하(A7); `version glass` 줄의 `checked_at=`이 3절의 그 검사 `edits saved_at=`보다 나중; `edits none` 줄이 있다 |
| R4 | 6절에서 `20261029-1910_SPL#1_Heating_coldstart`과 `V2-3 확인`의 줄이 3절과 글자 그대로 같고, 네 검사 모두 `sha256_check=same` |

## 결과 양식

```text
[S1] 0절 마지막 줄 = ; MISMATCH 줄 =
[env] python =
[B] 백업 줄 =
[S2] pytest 마지막 줄 = ; (실패가 있으면 이름과 마지막 30줄)
[3] 검사 목록 출력 원문:
[4] 콘솔 줄 원문 (없으면 "없음") =
[J1] O/X ; 소감 =
[J2] O/X ; 소감 =
[J3] O/X ; 소감 =
[J4] O/X ; 소감 =
[J5] O/X ; 소감 =
[J6] O/X ; 소감 =
[J7] O/X ; 소감 =
[J8] O/X ; 소감 =
[J9] O/X ; 소감 =
[J10] O/X ; 소감 =
[J11] O/X ; 소감 =
[J12] O/X ; 소감 =
[J13] O/X ; 소감 =
[J14] O/X ; 소감 =
[J15] O/X ; 소감 =
[U1] O/X ; 소감 =
[U2] O/X ; 소감 =
[J16] O/X ; 소감 =
[J17] O/X ; 소감 =
[J18] O/X ; 소감 =
[소감] =
[6] 검사 목록 출력 원문:
```
