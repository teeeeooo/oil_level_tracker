# Windows 요청: V2-3 편집기 재확인 (2026-10-30)

> 이 문서는 **Windows 워크스테이션에서 실행**하기 위한 요청이다.
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다. 요약하거나 줄을 줄이거나 직접 합계를 내지 않는다.
> - **[사용자]** 표시: 사용자가 앱 창에서 직접 조작하고 판단한다.
> - **통과 기준**은 아래 "통과 기준" 절에 있고, 실행 전에 고정됐다. 판정은 이 문서를 만든 쪽이 한다. 에이전트는 원문만 옮긴다.
> - 결과 파일은 Windows에 남기고, 맨 아래 **결과 양식**만 텍스트로 돌려준다.

## 무엇을 확인하나

[지난 실행](../60-evidence/2026-10-30-v2-3-editor-windows-result.md)에서 두 줄이 실패했고, 사용자 소감으로 편집기가 바뀌었다. **그것에 영향받는 것만** 다시 본다. 시간 측정(A4–A6)은 다시 하지 않는다.

- **R2 실패:** SPL#1 편집 검사의 저장된 편집에 Oil 그림과 판단 불가가 남지 않았다. 코드에서 잃어버리는 길은 찾지 못했고, 범위 Delete가 Oil 선만 지우던 규칙과 "판단 불가 풀기"가 고른 범위 전체를 지운 것으로 보인다. 이번에는 그린 곳과 **겹치지 않게** 지우고, 판단 불가의 **일부만** 풀어 저장한 뒤 센다.
- **콘솔 줄 실패:** 영상 스트리밍 중 `ConnectionAbortedError` Traceback이 콘솔에 찍혔다. 페이지가 연결을 끊는 것은 오류가 아니므로 이제 찍지 않는다. 재생과 클릭으로 다시 일으켜 본다.
- **사용자 소감으로 바뀐 것** (Product SSOT §6):
  - E3: 보이는 범위가 분석 범위 밖(`-` 시각)으로 나가지 않는다. 그래프 머리에 **"전체 보기"**.
  - E5: 연필의 **"수평·수직"** 스위치(그림판의 Shift처럼).
  - E6: 점 잇기가 **스냅을 따른다.** 켜면 경계를 따라, 끄면 곧게.
  - E7: Delete는 **"그릴 선"에서 고른 선**을 지운다. 버튼 이름이 그 선을 말한다("Foam 선 지우기"). 다른 도구를 고르면 범위가 풀린다. 범위 단추가 오른쪽 칸 밖으로 나가지 않는다.
  - N8: 검사 목록에서 이름과 같은 폴더 이름을 한 번 더 보이지 않는다.

지난 실행의 검사 4개가 문서 폴더의 `OilLevelTracker\Inspections`에 있다. **SPL#1 편집 검사(`20261029-1913_SPL#1_Heating_coldstart`)만 편집한다.** 나머지는 열지 않아도 된다. Recipe는 고치지 않는다.

## 0. 소스 확인 [에이전트]

1. **커밋 하나로 고정된 ZIP**을 받는다:
   `https://github.com/teeeeooo/oil_level_tracker/archive/8c9ea35c8446ac757007313657fb7d224c063334.zip`
   **새 폴더**에 압축을 풀고(`oil_level_tracker-8c9ea35c…`) 그 폴더를 저장소 루트로 쓴다. 이전 실행의 폴더는 쓰지 않는다.
2. 저장소 루트에서 아래를 그대로 실행한다. 마지막 줄이 `checked=86 mismatched=0`이면 된다. `MISMATCH` 줄이 있으면 그 줄을 전부 원문으로 적는다.

```powershell
$expected = @{
  'DESIGN.md' = 'd918b27fcde272afad52cf854f0a6fee4ad298e70a0a24824ae1de098eb88af9'
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
  'src/oil_tracker/adapters/http/api.py' = '840ab943041b3c20a6e984f6a43f59b40bdbce53872cc6491df3ff9114268c22'
  'src/oil_tracker/adapters/http/jobs.py' = '4b13c0d72bc1345cc0d0ab6faf40cdd029ef22526cd1f0552393c957be553f22'
  'src/oil_tracker/adapters/http/server.py' = '0b951a1dd7e7799ccca739951e65e0e22cda40751b548ecdffbb13fcc9275234'
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
  'src/oil_tracker/web/app.css' = '04639e58e98b75d9f620fbc52db825a23cd51deabf1bc600d7f6102be9756aff'
  'src/oil_tracker/web/editor.js' = 'a5e2ff3a03cb8f08c44d428291d469dd6255e5e4e6a81a02c64afacd260c1046'
  'src/oil_tracker/web/frame.js' = '444689064c1f583b75982ad0fec87d8264467755e9a96a56fd5ddaccb95f35dc'
  'src/oil_tracker/web/index.html' = '6aa7cbab4073017337455a0aa183ca94424b46cf08cc6612b0fd80bdd52c31df'
  'src/oil_tracker/web/inspections.js' = 'bb83dc0002fba6a9c76388ff5e9cd2c47170957b23724d9f9d3ebb103de54008'
  'src/oil_tracker/web/lines.js' = '0b10a64ed371466dbb1c5df834b28dbdd3bcc640c54fefb1382530174a9a6084'
  'src/oil_tracker/web/main.js' = '4c4c26bb1de7e0a86fb1b4b77301366f9979f0b16e5551cab65ad427a8502137'
  'src/oil_tracker/web/nav.js' = 'f06641803602beefae7c67a473daeffa9a9b5eec63f65b7cb0829954529af267'
  'src/oil_tracker/web/player.js' = 'e4acc63b72d574d61eea175e9639f0b2cfafce437a2e2ce5261527fdb00818d3'
  'src/oil_tracker/web/recipe.js' = '40e0e357f36e8724ffc9b9bca60c3f591f344f8cc19c8f27ba35c9dd0c17b588'
  'src/oil_tracker/web/render.js' = '27280bf135b7e30e7930aa5734a384c65f4ef697754b39af2d84aedced8bb2f5'
  'src/oil_tracker/web/tokens.css' = 'dbada0057157414b04dd82e31ca33b85de506f097ba376885f234f2875242eb0'
  'src/oil_tracker/web/ui.js' = '1711ee95e43b48e79e7e6cdd34457a21fb0549d338fd28bbb1732ed458f641ce'
  'tests/test_app.py' = '51fd947f25dc46ff49d0247a08bec15cb8fc0c26db9ddac717c99776346c265f'
  'tests/test_application_editing.py' = '36a804d6c7f9dc3f7ea4a7488e4a90e195ae9c5b5a1c0ba86bdfb89b2ad9ec17'
  'tests/test_application_inspections.py' = 'ac15efb2959bde624eafb135dcad9f95285afd597030da03706bedee18e8dd4c'
  'tests/test_application_recipes.py' = '154b61e3cf6e4aa81a68e2165f51e569eb7a78889207e617b273136f1c16cde8'
  'tests/test_architecture.py' = '42910fb569bd010342747d081d1c0cac7aa8c9f2641af24da92a2f4ab5317288'
  'tests/test_compare_medians_script.py' = '3ced7c6a8096de3411be5f7fbc7db57a86ad81f531da41d3c418937b205ba119'
  'tests/test_docs_catalog.py' = 'bf999036473a5924f1ef312ab7e93e0b972819f5f6c167242a023996725fc4be'
  'tests/test_domain_edits.py' = '90fa950cad5ffe15e5939d3c2823e4df1c9ec31e3214468718b64035ba2eba30'
  'tests/test_domain_inspection.py' = '7306a9937e74a6dfecf1a2eae238f68128fba6b3545fb30e77fad317759e19aa'
  'tests/test_domain_recipe.py' = 'f916f1e77ef9f0559c7e3cee1dcab400a08dac94d1254cdefcb71dc91ad98b80'
  'tests/test_http_api.py' = '16a10b6fc4ee476f50d9b04118d59ba47f79ab4bae232a30927a46b54947f48d'
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
  'tests/test_web_inspection_smoke.py' = 'cb6558e96d04b56a7cb00386537ccb6c89079a9680c8ebd22b3da054710b05e3'
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

이 폴더에 **앱용 venv 하나**만 만든다(Playwright를 넣지 않는다. 넣으면 2절의 테스트 수가 달라진다). 측정용 venv는 이번에 필요 없다.

```powershell
py -3.14 -m venv .venv-v2
.venv-v2\Scripts\python -m pip install -e . pytest
.venv-v2\Scripts\python --version
```

## 2. 테스트 (S2) [에이전트]

```powershell
.venv-v2\Scripts\python -m pytest -q
```

- 마지막 줄을 원문으로 적는다. 기대값은 `201 passed, 4 skipped`이다(지난번보다 3개 많다: 끊긴 연결 검사).
- 실패가 있으면 실패한 테스트 이름과 출력 마지막 30줄을 원문으로 적는다.

## 3. 실행 전 검사 목록 [에이전트]

출력을 **전부 원문으로** 적는다. 읽기만 한다. SHA-256을 다시 계산하므로 몇 초 걸린다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
```

## 4. 앱 실행 [에이전트 → 사용자]

```powershell
.venv-v2\Scripts\python -m oil_tracker
```

- 창이 열리면 **[사용자]**가 5절을 진행한다. 창은 최대화해서 쓴다.
- 앱이 도는 동안 **콘솔에 나온 줄을 전부** 원문으로 적는다(창을 닫을 때까지). 없으면 "없음".

## 5. 앱 창에서 직접 조작 [사용자]

각 항목에 **O / X**와 한 줄 소감을 남긴다. 키 입력은 그래프나 빈 곳을 한 번 누른 뒤에 한다. 막히면 **F1**로 도움말을 연다.

검사 목록에서 **`20261029-1913_SPL#1_Heating_coldstart`**(만든 시각 2026-10-29 19:13)의 "열기"를 누른다. 제목 옆이 "저장함 …"이고 지난번 편집(메모 핀, 옮긴 기동)이 보인다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| C1 | Space로 재생하고, 재생 중에 그래프 여러 곳을 빠르게 클릭한다(5번쯤). Space로 멈춘다 | 영상이 클릭한 곳으로 가는지. **콘솔에 줄이 생기지 않는지**(에이전트가 본다) |
| C2 | 휠로 많이 축소하고, `Shift`+끌기로 그래프를 **오른쪽으로 끝까지** 민다. 시간축 오른쪽 끝 숫자를 눌러 `20` 입력 후 Enter | 그래프 왼쪽 끝이 0:00에서 멈추고 더 밀리지 않는지. 20 입력 뒤 0:00–0:20이 보이고, **`-` 시각과 빈 그래프·빈 맥락 이미지가 없는지** |
| C3 | 그래프 머리 오른쪽의 **"전체 보기"** | 분석 범위 전체(약 68분)와 Glass 높이로 돌아오는지 |
| C4 | 휠로 1–2분쯤 보이게 확대한다(아래 C5–C8은 이 근처에서, **지난 편집과 겹치지 않는 곳**). "그릴 선" Oil, `P`(연필), 오른쪽 **"수평·수직"** 켜기. 가로로 길게, 조금 비스듬히 끈다. 이어서 다른 곳을 거의 세로로 짧게 끈다. "수평·수직" 끄기 | 첫 번째가 누른 높이의 **수평선**인지. 두 번째는 누른 시각의 한 점만 포인터 높이로 옮겨지는지(뾰족하게 튐) |
| C5 | `S`로 스냅을 **끄고** `L`(점 잇기). C4와 다른 곳에서 그래프에 점 두 개를 찍고 `Enter` | 점 사이 미리 보기와 확정한 Oil 선이 **곧은 선**인지 |
| C6 | `S`로 스냅을 **켜고**, 다른 곳에서 점 두 개를 찍는다. `S`를 한 번 껐다 다시 켠다. `Enter` | 켜면 경계를 따라 휘고, 끄면 곧게 바뀌고, 켜면 다시 휘는지 |
| C7 | `R`(범위)로 C4–C6과 **겹치지 않는** 곳을 몇 초 고른다. "그릴 선"을 **Foam**으로 바꾸고 `Delete`. "그릴 선"을 Oil로 되돌린다 | 버튼이 "Foam 선 지우기"였는지. 그 범위의 **Foam 선만** 사라지고 Oil 선은 남는지(Foam 선이 원래 없던 곳이면 그대로 둔다) |
| C8 | 다른 곳을 10초쯤 고르고 `U`. 빗금 안의 **일부만** 다시 끌어 고르고 "판단 불가 풀기" | "판단 불가 풀기"가 오른쪽 칸 **안에** 있는지. 고른 일부만 빗금이 지워지고 나머지는 남는지 |
| C9 | 범위가 고른 채로 `M`(메모)을 누른다 | 고른 범위(파란 띠)와 오른쪽 "선택한 범위" 칸이 사라지는지 |
| C10 | `Ctrl+S` 뒤 "← 검사 목록" | "저장함 HH:MM", 묻지 않고 목록으로 가는지 |
| C11 | 목록의 `V2-3 확인` 줄을 본다 | 이름과 영상 파일 이름 두 줄만 보이는지(`V2-3 확인`이 한 번만). 이름 없는 검사는 폴더 이름 줄이 그대로 있는지 |
| C12 | 앱 창의 X | 묻지 않고 닫히는지 |

마지막으로 **전체 소감**을 한두 줄 남긴다.

## 6. 결과 확인 [에이전트]

앱을 닫은 뒤 실행하고, 출력을 **전부 원문으로** 적는다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
```

- `edits glass` 줄의 `oil=`, `foam=`, `reference=`는 그 선의 샘플 수를 `초안/고침/그림/빈 샘플` 순서로 센 것이다.

## 통과 기준 (실행 전에 고정)

| ID | 통과 조건 |
|---|---|
| S1 | 0절 마지막 줄이 `checked=86 mismatched=0` |
| S2 | 2절 마지막 줄이 `201 passed, 4 skipped` |
| C | 5절의 C1–C12가 모두 O |
| T | 4절 콘솔에 `Traceback` 줄이 없다(C1의 재생과 클릭을 포함해 창을 닫을 때까지) |
| R1 | 6절이 `inspections=4 unreadable=0` |
| R2 | 6절에서 `20261029-1913_SPL#1_Heating_coldstart`의 `edits saved_at=`이 3절의 값보다 나중이고, `compressor=`가 3절과 같다. 그 `edits glass` 줄에서 `oil`의 그림이 **1 이상**, `foam`의 고침이 **1 이상**, `cannot_judge`가 **1 이상**, `memos`가 3절과 같다 |
| R3 | 6절에서 나머지 검사 세 개의 `edits` 줄(`edits none` 포함)이 3절과 글자 그대로 같고, 네 검사 모두 `sha256_check=same` |

## 결과 양식

```text
[S1] 0절 마지막 줄 = ; MISMATCH 줄 =
[env] python =
[S2] pytest 마지막 줄 = ; (실패가 있으면 이름과 마지막 30줄)
[3] 검사 목록 출력 원문:
[4] 콘솔 줄 원문 (없으면 "없음") =
[C1] O/X ; 소감 =
[C2] O/X ; 소감 =
[C3] O/X ; 소감 =
[C4] O/X ; 소감 =
[C5] O/X ; 소감 =
[C6] O/X ; 소감 =
[C7] O/X ; 소감 =
[C8] O/X ; 소감 =
[C9] O/X ; 소감 =
[C10] O/X ; 소감 =
[C11] O/X ; 소감 =
[C12] O/X ; 소감 =
[소감] =
[6] 검사 목록 출력 원문:
```
