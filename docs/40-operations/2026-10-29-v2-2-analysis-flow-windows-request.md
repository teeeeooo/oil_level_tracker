# Windows 요청: V2-2 검사·분석 흐름 확인 (2026-10-29)

> 이 문서는 **Windows 워크스테이션에서 실행**하기 위한 요청이다.
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다. 요약하거나 줄을 줄이거나 직접 합계를 내지 않는다.
> - **[사용자]** 표시: 사용자가 앱 창에서 직접 조작하고 판단한다.
> - **통과 기준 R1–R15**는 아래 "통과 기준" 절에 있고, 실행 전에 고정됐다.
> - 결과 파일은 Windows에 남기고, 맨 아래 **결과 양식**만 텍스트로 돌려준다.

## 무엇을 확인하나

V2-2의 검사 화면을 실제 Windows(WebView2)에서 처음 써 본다.
- 앱이 **검사 목록**으로 열리고, 새 검사는 영상 → Recipe 선택 → 분석 설정 순서로 간다;
- 분석 설정: 분석 범위, 압축기 기동 시각, 이 검사에만 적용하는 Glass 위치 보정;
- **분석 시작**을 눌러야 검사 폴더가 생긴다. 그 전에 나가면 아무것도 남지 않는다;
- 진행 대화상자(진행률, 남은 시간, 취소), 분석 중 앱 닫기, 다시 열어 이어 하기;
- 분석 결과 화면(읽기 전용): 그래프, 맥락 이미지, "배경 제거 보기", Glass 선택;
- **A4 시간을 앱 안에서**: SPL#1(68분) 분석이 "분석 시작"부터 캐시 저장까지 몇 초인지. 같은 PC에서 측정 스크립트는 46.4초였다([결과](../60-evidence/2026-10-29-v2-2-slowest-pc-timing-windows-result.md));
- V2-1 후속(배속 칸, 도움말, F1)이 WebView2에서 되는지.

V2-1에서 만든 Recipe `SPL#4_test1_607bccb`, `SPL#1_test1_607bccb`를 그대로 쓴다. **Recipe는 고치지 않는다.** 여기서 만드는 검사 3개는 문서 폴더의 `OilLevelTracker\Inspections` 아래에 남는다. V2-3에서 이어 쓰므로 지우지 않는다.

시간을 재므로 **다른 무거운 프로그램(지난번의 e-mail embedding 작업 등)은 가능하면 멈춘다.** 멈추지 못했으면 결과 양식에 적는다.

## 0. 소스 확인 [에이전트]

1. **커밋 하나로 고정된 ZIP**을 받는다:
   `https://github.com/teeeeooo/oil_level_tracker/archive/0df5ce685ec6e6715e34bf709cc82aa096d71951.zip`
   압축을 푼 폴더(`oil_level_tracker-0df5ce68…`)를 저장소 루트로 쓴다. 이전 실행의 폴더는 쓰지 않는다.
2. 저장소 루트에서 아래를 그대로 실행한다. 마지막 줄이 `checked=72 mismatched=0`이면 된다. `MISMATCH` 줄이 있으면 그 줄을 전부 원문으로 적는다.

```powershell
$expected = @{
  'DESIGN.md' = 'b3def7a9d503dd0f4d9c1adaa1ae5f4bc2658c33f2b674616e4526650cdb9624'
  'pyproject.toml' = '3890d934fa7c238ab51c2994f5c2ed44bed9f83d0067eccb085be19ac8c58b9d'
  'scripts/check_docs_catalog.py' = '226a0293907b9b9b555a71d3aca5ba3b1f07369295403c3e44ee1d877efe0020'
  'scripts/compare_draft_methods.py' = '3c87c76b632c69f6b418fb39d923a10d40db0d15e4add08ac149427cf0a991f7'
  'scripts/inspection_summary.py' = '6a59d8f47373e096eb8c9b9a6118668109ca6cec494116975477b22f2a0c3b46'
  'scripts/recipe_summary.py' = '5e7e4960cfd659e1a9e887b9d0d17fd3517381b2ccd78b8e3a0f6f4968e5a8b3'
  'scripts/time_analysis.py' = '3646f4e8094a10dbe2ed8e48dabdcddbb895b3e3b076bb428f3b9ef74b3f9ab0'
  'src/oil_tracker/__init__.py' = '44b73c09a8a5c67a64bc97f0b0edc9aa6779d1fa5ddefafd61d89bb0d13ca615'
  'src/oil_tracker/__main__.py' = '4efc05fc1cffa5b074068f9bd0ab3ff84b8eaba4c70edbc5ce4d806c05a1a2d1'
  'src/oil_tracker/adapters/__init__.py' = '7b5021074fb335deb08bf8e6c61147b8380361a48f164c682d754a95975ab996'
  'src/oil_tracker/adapters/desktop/__init__.py' = 'fb18660afd9644a6fb9fb2f270a347dbad89b54681b4941bbb4bba2ee8453bff'
  'src/oil_tracker/adapters/http/__init__.py' = 'b359fe08245e9086c1171d961e9c51e0575dc33b23ada7af2d087b47b38b5f47'
  'src/oil_tracker/adapters/http/api.py' = 'cdadc98fdc3518bc3e5029c5b13c56c9943ea95ded078bd30965e1b717493b5d'
  'src/oil_tracker/adapters/http/jobs.py' = '4b13c0d72bc1345cc0d0ab6faf40cdd029ef22526cd1f0552393c957be553f22'
  'src/oil_tracker/adapters/http/server.py' = '9adb32c73e631a73a256fedfb4a8ad029f53a7dc608214d65388489f2c9597b7'
  'src/oil_tracker/adapters/storage/__init__.py' = '5253f99b1985be481fe2837d01fc0533ecaed8103268631c3f2a2ccb8399a4aa'
  'src/oil_tracker/adapters/storage/files.py' = 'bed95d9f399133b31fbc853ee64c66fc20c69edcd50aab8bcfdf8a70d2cb36cb'
  'src/oil_tracker/adapters/storage/inspection_files.py' = 'f73321eaebbe57f4a17f76e4eecfbf2c6d2cffbc874f08e95d09f4aee30a3bd7'
  'src/oil_tracker/adapters/storage/locations.py' = '54951aaf5cdfc94c5b9325ffe1a0017908790a85ac275f2a5c868d71262e1f0c'
  'src/oil_tracker/adapters/storage/recipe_files.py' = '8d6caa3b04d4c5301083de0afe900230732c39de7f07b1d5434a29e4491ca8ab'
  'src/oil_tracker/adapters/storage/values.py' = '41e214903650422c8c6ec77281ef25cb186b39c968317c08c22caa1a7009622a'
  'src/oil_tracker/adapters/video/__init__.py' = '7499b2d549136a86fbff18ea219095c124c22d83bbd6f750df692b9fed7967c1'
  'src/oil_tracker/adapters/video/analysis.py' = 'a9c1e37eda63c9b6bea1c70f4c5c0e557b81e904849ee7a8903324cd94280f35'
  'src/oil_tracker/adapters/video/context.py' = 'f2341ffe10c79448ca7fafcbd7e7667c67353c077388296f104dae9045b5a5f5'
  'src/oil_tracker/adapters/video/draft.py' = 'b3f4ca63e4855af3f5db914f72f6526321432c712646764d453440411618f907'
  'src/oil_tracker/adapters/video/frames.py' = '3b33e7d15a3acdce9273ef3d4f15a948a745682bbd1b8d4639205463bf68d5e6'
  'src/oil_tracker/app.py' = 'bf645a9d8f39652a259eeec053427ce69d1ccaf684749e2bb73f9fd6bb8e6a5b'
  'src/oil_tracker/application/__init__.py' = 'c7de6525842604180e0f82b532883bece026ac01a556d364caf4c6d7ea0d0253'
  'src/oil_tracker/application/inspections.py' = '6a93e92042e11ccc31e087e295097b0abc05f8419536894befa3132bbc150266'
  'src/oil_tracker/application/ports.py' = 'afdf10e44e1ad48711475342ef0387ef22c4fcdc404ae8d950a9297cf059ba6e'
  'src/oil_tracker/application/recipes.py' = '9053abc7acf8de6056697c71b6d5df965734fd82e5fa187936720a819e652cc7'
  'src/oil_tracker/application/videos.py' = 'fa426ac98d2fc5ca4d4b9f2cb262bf715e14a96249bb6be8d245d8e81106c713'
  'src/oil_tracker/bootstrap.py' = '65049f926fc32c9b7eae7384dc9495d8d141c9ff663f1b69accca1a764b53fb3'
  'src/oil_tracker/domain/__init__.py' = '6bbe167d274a1996c8581b03b4abfa871febc6226c928aea077f1f3f8e10462e'
  'src/oil_tracker/domain/enums.py' = '4683d222d4373fffd5ee37f3da0056da447214e666385d9c5eb7bf953f9a6f67'
  'src/oil_tracker/domain/geometry.py' = '7c05fab4fad05cb24631eed5d0495f5824bf7cf041a3bcfccb4bf07c03118600'
  'src/oil_tracker/domain/inspection.py' = '7c418f5f922641257728fdbe45ced741df56b3382cc808abc68678ea07fbbabe'
  'src/oil_tracker/domain/line.py' = 'a0329eb5164db3ea1db8f0a030e69d4952e11f9f7c009c1ef069c8bbcb088965'
  'src/oil_tracker/domain/problems.py' = '759fc6854d600618c43377e7193d6e604e55672d50a1844e3025758ea007c125'
  'src/oil_tracker/domain/recipe.py' = 'dd4a9a665312391f03c48799dea38c455f512aae517c08dc3d663fee0f5ff2af'
  'src/oil_tracker/web/api.js' = '73f96e12296dad564d2795da7192ca135acffe3aae238b6202d874fd650a06ba'
  'src/oil_tracker/web/app.css' = '12ef91434a82b4c5abd0b54ce02c2e713d36b4bd32d0b9f487a5623083529cbb'
  'src/oil_tracker/web/frame.js' = 'a90285c4559037ac0059d39a904d6b53630c7fe13831b5f78cce58099e3550e5'
  'src/oil_tracker/web/index.html' = 'bc2fbcf8010b69b58094376194a129652ca6591ea410162708d850083b2d651e'
  'src/oil_tracker/web/inspections.js' = '914961710ec9bf423e1f982a8c2c847f504c9a1e4846faebbe07b76385c87bb0'
  'src/oil_tracker/web/main.js' = '0636e7142af44f1a916cb5afcd7c4291d403cd59215ee83a5763e270f5bda905'
  'src/oil_tracker/web/nav.js' = 'f06641803602beefae7c67a473daeffa9a9b5eec63f65b7cb0829954529af267'
  'src/oil_tracker/web/recipe.js' = '40e0e357f36e8724ffc9b9bca60c3f591f344f8cc19c8f27ba35c9dd0c17b588'
  'src/oil_tracker/web/render.js' = '311c51c044c632f2a3b66d25757545dc4a414502d11e2ea4e108875c718a5894'
  'src/oil_tracker/web/result.js' = '16152e2787ec4f7acfaf2f7f95a5b094f93ff06e1500771d3808f8c54841ef6c'
  'src/oil_tracker/web/tokens.css' = '21c92959535596a6ca5704387256ef047e344371998081736b2316ae91e22f9e'
  'src/oil_tracker/web/ui.js' = '407037f36e0b33542b8bd64fa2e1b1c2ae5f349b35f11eda880bd696c26ee650'
  'tests/test_application_inspections.py' = '0c241af264032c9afe93b08c8ad38576b29801caf2b1923a745cdec1e239a663'
  'tests/test_application_recipes.py' = '50224c51361b207a2c8fd1c119a72a9f4a75328da896f0c1d50c1de5f93c2c99'
  'tests/test_architecture.py' = '42910fb569bd010342747d081d1c0cac7aa8c9f2641af24da92a2f4ab5317288'
  'tests/test_docs_catalog.py' = 'bf999036473a5924f1ef312ab7e93e0b972819f5f6c167242a023996725fc4be'
  'tests/test_domain_inspection.py' = '1affe6fa9387948c84a2ae81326fa540e68804b6a31e881a7341ebc1afeb5fa6'
  'tests/test_domain_recipe.py' = 'f916f1e77ef9f0559c7e3cee1dcab400a08dac94d1254cdefcb71dc91ad98b80'
  'tests/test_http_api.py' = '1782d73c153cb1d18825db32dcd58e993698b76931563b947ced8847f5bcfc20'
  'tests/test_http_jobs.py' = 'fd538c2d448228f847ac1d201b47e133026bf66c9fb104a4cc11049f724c2d33'
  'tests/test_inspection_summary_script.py' = '473860fbf49cf32ef0452b716dc147828893ae2c7b74b67c5ba8f2e0a19de284'
  'tests/test_package.py' = '8d458fbb772dcd6a825e060c8fdcdad2eb7716a8f72ef6df8c3d437026f063f8'
  'tests/test_recipe_summary_script.py' = 'f90b3adff4b1fb43ae28ae2aead9c56c55f7dc22c09b10f8bf030e1a9598748b'
  'tests/test_storage_inspection_files.py' = '9cd2b81668cd849484c80b71bc5ec34c9d3cc3d96d84eb10f054b357c4f5f0c6'
  'tests/test_storage_recipe_files.py' = 'e784cacbad6b421ef8426a448d1e9661f8c05daf7b238930a3c52a5c77a50288'
  'tests/test_time_analysis_script.py' = '5e3659ac7b9810095eeefc14511b190e8e8eb398143f8e13b25cf463e07a1ac0'
  'tests/test_video_analysis.py' = 'ec97c4ed0d328ea42f2ae233168667cb40014decd172712cca01092f83a30d98'
  'tests/test_video_context.py' = '6ca21e7f43818e0eac3074354b86e1b204d0b0a6af54dac933f071301167ab6b'
  'tests/test_video_frames.py' = 'd85ac1f56603e0aa08a462d6ad5a03229747c94e3e51c53f6b69515096783d57'
  'tests/test_web_inspection_smoke.py' = '656e10a779cd64c418a381aa2537b106c86e2c077e92d8cbd4b519558af6a8f2'
  'tests/test_web_recipe_smoke.py' = '3a0531e2080e5cdd45db5ddb2b9f0457b1a72b08b91b5b5b8698fec9ef267a8d'
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

이 폴더에 **새 venv**를 만든다(V2-1의 `.venv-v2`는 다른 폴더를 가리키므로 쓰지 않는다).

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

- 마지막 줄을 원문으로 적는다. 기대값은 `140 passed, 3 skipped`이다.
  - 건너뛰는 3개: 브라우저 스모크 검사 2개(Playwright 미설치)와 macOS 전용 문서 폴더 검사.
- 실패가 있으면 실패한 테스트 이름과 출력 마지막 30줄을 원문으로 적는다.

## 3. 실행 전 검사 목록 (R3) [에이전트]

앱을 열기 전에 실행하고, 출력을 **전부 원문으로** 적는다. 읽기만 한다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
```

셋째 줄의 `inspections=` 값을 6절과 비교한다.

## 4. 앱 실행 [에이전트 → 사용자]

```powershell
.venv-v2\Scripts\python -m oil_tracker
```

- 창이 열리면 **[사용자]**가 5절을 진행한다.
- **방화벽이나 보안 경고 창이 뜨면** 허용하지 말고 닫는다. 창이 떴다는 사실과 문구를 적는다.
- 5.3절에서 앱을 한 번 닫고 같은 명령으로 다시 연다. **창을 닫을 때마다** 콘솔에 나온 줄을 전부 원문으로 적는다. 없으면 "없음".

## 5. 앱 창에서 직접 조작 [사용자]

영상은 지난 실행과 같은 파일이다.
- **SPL#4:** `SPL#4_Cooling_onoff_#2.mp4` (53,165,455 bytes, 04:20.0)
- **SPL#1:** `SPL#1_Heating_coldstart.mp4` (683,165,477 bytes, 68:24.6)

각 항목에 **O / X**와 한 줄 소감을 남긴다. 키 입력은 프레임이나 빈 곳을 한 번 누른 뒤에 한다(입력 칸에 커서가 있으면 키가 그 칸으로 간다).

### 5.1 SPL#4: 설정만 하고 나가기

| ID | 할 일 | 볼 것 |
|---|---|---|
| R3 | 앱이 열리면 첫 화면 확인. **F1** | "검사" 목록이 첫 화면인지(검사가 없으면 "검사가 없습니다"). F1로 "도움말 · 검사 목록"이 뜨는지. Esc로 닫기 |
| R4 | "새 검사" → 파일 대화상자에서 SPL#4 선택 | Recipe 선택 창: 영상 이름과 "1920 × 1080 · 04:20.0", Recipe 목록(이름, Glass, 프레임 크기, 수정일). 회색으로 막힌 줄이 있으면 그 이름과 아래 문구를 적는다 |
| R4 | `SPL#4_test1_607bccb` 선택 → "다음" | 분석 설정 화면이 열리는지. 제목 "새 검사 · SPL#4_Cooling_onoff_#2.mp4" |
| R5 | 처음 상태 확인 | 위쪽 "문제 1개", 기동 시각 아래 "기준점 회복 Glass가 있어 압축기 기동 시각이 필요합니다.". 분석 범위 끝이 `04:20.0`, 그 아래 "샘플 520개" |
| R7 | 한 프레임씩: `.` 를 천천히 다섯 번, `,` 를 두 번 | 누를 때마다 그림이 한 번 바뀌고 **그대로 멈춰 있는지**(깜빡이거나 계속 다시 그리지 않는지). 시각이 앞뒤로 따라가는지 |
| R5 | 한/영 키로 **한글 입력**으로 바꾼 뒤, 아래 막대를 00:10 근처로 끌고 `[`, 00:30 근처로 끌고 `]` | 시작·끝 칸이 그 시각으로 바뀌는지. 아래 막대에 "시작", "끝" 표시와 그 사이 띠가 보이는지. 확인 후 영문 입력으로 되돌린다 |
| R5 | 00:20 근처에서 기동 시각의 "지금" | 기동 칸이 채워지고 막대에 "기동" 표시가 생기는지. "문제 1개"가 사라지는지 |
| R5 | 시작 칸에 `abc` 입력 | "시각을 mm:ss.s로 입력하세요."가 뜨는지. 확인 후 `10`으로 고친다 |
| R6 | 배속 칸 오른쪽 ▾ → `2×` → Space로 재생 | 메뉴가 뜨고 2배로 재생되는지. Space로 멈춘다 |
| R6 | 배속 칸에 `3x` Enter, `20` Enter, `abc` Enter, `0.5`를 입력하고 Esc | 차례로 3, 16(최대로 맞춰짐), 16 그대로(숫자가 아니면 되돌림), 16 그대로(Esc로 되돌림) |
| R6 | 오른쪽 위 "?" 단추, **F1**, `?` 키로 도움말 열기. 닫기는 Esc, "닫기", 창 바깥 클릭 | 세 방법 모두 "도움말 · 분석 설정"이 뜨고, 세 방법 모두로 닫히는지 |
| R8 | "← 검사 목록" | "분석을 시작하지 않으면 바꾼 설정은 저장되지 않습니다. 검사 목록으로 갈까요?"가 뜨는지. **확인**을 누르면 목록으로 가고, **새 줄이 생기지 않는지** |

### 5.2 SPL#4: 분석하고 결과 보기

| ID | 할 일 | 볼 것 |
|---|---|---|
| R9 | "새 검사" → SPL#4 → `SPL#4_test1_607bccb` → "다음" | 분석 범위는 **바꾸지 않는다**(00:00.0–04:20.0) |
| R9 | 압축기가 기동하는 시각으로 넘긴 뒤 기동 시각의 "지금" | 기동 시각이 이 영상에 맞는지는 사용자 판단. 모르겠으면 범위 안 아무 시각이나 된다 |
| R9 | 오른쪽 Glass 목록에서 **Accum** 줄을 누르고 → 키를 한 번 | Accum 줄에 "Recipe와 다름" 표시가 생기고, 중심 X가 1 커지는지 |
| R9 | "Recipe 위치로 되돌리기" → 다시 → 키를 **한 번** | 되돌리면 표시가 사라지고, 다시 누르면 생기는지. **이 1 px 보정은 남겨 둔다** |
| R9 | "분석 시작" | "분석 중" 창(진행 막대, %, 남은 시간)이 뜨고, 끝나면 결과 화면이 열리는지 |
| R9 | 결과 화면에서 Glass를 BASE ↔ Accum으로 바꾸고, "배경 제거 보기"를 켰다 끄기. F1 | 그래프(Oil 선, 0선, 기동 점선)와 맥락 이미지가 Glass마다 바뀌는지. 배경 제거 그림으로 바뀌는지. "도움말 · 분석 결과" |
| R9 | 창 크기를 바꿔 보기 | 그래프와 그림이 새 크기로 다시 그려지는지 |
| R9 | "← 검사 목록" | SPL#4 줄이 "분석 완료"로 보이는지 |

### 5.3 SPL#1: A4 시간 재기 (취소 없이)

이 검사는 **취소하지 않고 Glass 위치도 바꾸지 않는다.** A4 시간은 이 검사로 잰다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| R10 | "새 검사" → SPL#1 → `SPL#1_test1_607bccb` → "다음" | 끝이 `68:24.6`, "샘플 8,210개" |
| R10 | 기동 시각을 "지금"으로 넣고(5.2와 같이) "분석 시작". **분석 중에는 아무것도 누르지 않는다** | 진행률이 오르고, 남은 시간이 나오는지. 끝나면 결과가 열리는지. 걸린 시간을 대략 적는다(초시계 불필요) |
| R11 | 결과 화면에서 처음 그림이 다 뜰 때까지, "배경 제거 보기" 켜고 끄기, 창 크기 바꾸기 | **기록만 한다**: 그림이 뜨기까지 걸린 느낌, 전환이 늦거나 멈칫하는지 |

### 5.4 SPL#1: 취소, 앱 닫기, 이어서 분석

| ID | 할 일 | 볼 것 |
|---|---|---|
| R12 | 검사 목록 → "새 검사" → SPL#1 → `SPL#1_test1_607bccb` → "다음" → 기동 시각 "지금" → "분석 시작" | 진행 창이 뜨는지 |
| R12 | 10–40%에서 "취소" | "취소하는 중…" 뒤 분석 설정 화면으로 돌아오고, "분석을 취소했습니다. 설정은 남아 있습니다."가 뜨는지. 제목이 "검사 · SPL#1_…", 그 아래 "분석 안 됨" |
| R12 | "← 검사 목록" | 확인 창 없이 목록으로 가는지. 이 검사가 "분석 안 됨"으로 한 줄만 있는지 |
| R12 | 그 줄의 "열기" | 설정 화면에 같은 분석 범위와 기동 시각이 남아 있는지 |
| R13 | "분석 시작" → 10–40%에서 **앱 창을 닫는다**(오른쪽 위 X) | 창이 닫히고 콘솔이 몇 초 안에 프롬프트로 돌아오는지. 콘솔 줄을 적는다(4절) |
| R13 | 4절 명령으로 앱을 다시 연다 | 이 검사가 "분석 안 됨"으로 보이는지 |
| R13 | "열기" → "분석 시작" → 끝까지 기다린다 | 결과가 열리는지 |
| R14 | 검사 목록 아래 "폴더 열기" | 탐색기가 `OilLevelTracker\Inspections` 폴더로 열리는지. 폴더 3개가 보이는지 |

마지막으로 **전체 소감**을 한두 줄 남긴다: 새 검사부터 결과까지의 흐름, 설정 화면, 결과 화면에서 불편한 점.

## 6. 결과 확인 (R15) [에이전트]

앱을 닫은 뒤 실행하고, 출력을 **전부 원문으로** 적는다. SPL#1의 SHA-256을 다시 계산하므로 몇 초 걸린다.

```powershell
.venv-v2\Scripts\python scripts\inspection_summary.py
```

## 통과 기준 (실행 전에 고정)

| ID | 통과 조건 |
|---|---|
| R1 | 0절 마지막 줄이 `checked=72 mismatched=0` |
| R2 | 2절 마지막 줄이 `140 passed, 3 skipped` |
| R3 | 창이 뜨고 첫 화면이 검사 목록이며, F1로 그 화면의 도움말이 뜬다 |
| R4 | 파일 대화상자가 뜨고, Recipe 선택 창에 영상 정보가 보이고 `SPL#4_test1_607bccb`를 고를 수 있으며, "다음"으로 설정 화면이 열린다 |
| R5 | 처음 문제 1개와 그 문구, `04:20.0`과 샘플 520개가 보이고, 한글 입력 상태의 `[` `]`, "지금", `abc` 오류가 표의 설명대로 된다 |
| R6 | 배속 칸과 도움말이 표의 설명대로 된다. 특히 **F1이 WebView2에서 도움말을 연다** |
| R7 | 한 프레임 이동마다 그림이 한 번 바뀌고 멈춰 있다 |
| R8 | 확인 창이 뜨고, 확인 뒤 목록에 새 줄이 없다. 6절의 `inspections=`가 3절 값 **+ 3**이다(나간 설정은 폴더를 남기지 않는다) |
| R9 | 보정 표시가 생기고 되돌려지며, SPL#4 분석이 끝나 결과가 열리고, 두 Glass와 배경 제거 보기가 그려진다. 6절의 SPL#4 검사가 `state=ANALYSED`, `times=520`, BASE `recipe_diff="none"`, Accum `recipe_diff="cx +1"`, `cache glass` 두 줄이 `pieces=1 files=2/2`이고 BASE `rows=484`, Accum `rows=298` |
| R10 | SPL#1 첫 검사가 6절에서 `state=ANALYSED`, `times=8210`, `recipe_diff="none"`, `cache glass` 줄이 `rows=728 pieces=3 files=6/6`, `empty`가 87.5–88.5%(측정 스크립트의 88%와 같은 초안). **A4:** 그 검사의 `cache_written`이 **180 이하** |
| R12 | 취소 뒤 설정 화면과 문구가 표대로이고, 목록에 그 검사가 한 줄만 "분석 안 됨"으로 있으며, 다시 열면 설정이 남아 있다 |
| R13 | 앱 창을 닫으면 콘솔이 프롬프트로 돌아오고(10초 안), 다시 연 앱에서 그 검사가 "분석 안 됨"이며, 다시 분석해 결과가 열린다. 6절에서 그 검사가 `state=ANALYSED`, `times=8210`, `files=6/6` |
| R14 | 탐색기가 Inspections 폴더로 열린다 |
| R15 | 6절이 `unreadable=0`이고, 새 검사 3개 모두 `partial=no`, `sha256_check=same`이다. 세 검사의 `recipe_updated_at`이 각자의 `created_at`보다 앞선다(Recipe 파일은 그대로) |
| — | 4절 콘솔에 `Traceback` 줄이 없다 |

- **A4 판단(R10의 `cache_written`):** "분석 시작"을 누른 때(검사의 `created_at`, 초 단위)부터 캐시를 다 쓴 때까지다.
  - **180초 이하:** 이 PC에서 앱 안의 A4를 만족한다.
  - **60초를 넘으면** 앱이 측정 스크립트(46.4초)보다 더 하는 일이 있다는 뜻이다. V2-2는 닫되, 최저 사양 PC의 여유가 약 10초뿐이므로 V2-5 전에 원인을 찾는다.
- **R11은 기록만 한다.** 편집 응답(A5)은 V2-3에서 잰다.
- R1–R10, R12–R15가 모두 통과하면 V2-2를 닫는다. 실패한 항목은 고친 뒤 그 항목에 영향받는 것만 다시 확인한다.

## 결과 양식 (이 블록만 텍스트로 돌려준다)

```
[R1] 0절 마지막 줄 = ; MISMATCH 줄 = (없음 / 원문)
[env] python = ; pywebview = ; pythonnet = ; clr_loader = ; opencv = ; numpy = ; pytest =
[env] WebView2 = (버전 / 없음) ; 멈추지 못한 무거운 작업 = (없음 / 내용)
[R2] pytest 마지막 줄 = ; (실패 시 이름과 마지막 30줄)
[R3] 3절 출력 원문:
...
[4] 방화벽/보안 창 = (없음 / 문구) ; 첫 번째 닫을 때 콘솔 줄 = (없음 / 원문) ; 두 번째 닫을 때 콘솔 줄 = (없음 / 원문)
[R3] O/X ; 소감 =
[R4] O/X ; 소감 = ; 회색 줄 = (없음 / 이름과 문구)
[R5] O/X ; 소감 =
[R6] 배속 = O/X ; 도움말 단추 = O/X ; F1 = O/X ; ? 키 = O/X ; 닫기 세 방법 = O/X ; 소감 =
[R7] O/X ; 소감 =
[R8] 확인 창 = O/X ; 새 줄 없음 = O/X
[R9] O/X ; 소감 = ; 넣은 기동 시각 =
[R10] O/X ; 대략 걸린 시간 = ; 남은 시간 표시 소감 = ; 넣은 기동 시각 =
[R11] 결과 화면 소감 =
[R12] O/X ; 취소한 진행률 =
[R13] O/X ; 닫은 진행률 = ; 프롬프트로 돌아오기까지 =
[R14] O/X
[소감] =
[R15] 6절 출력 원문:
...
```
