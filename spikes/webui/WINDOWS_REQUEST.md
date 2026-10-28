# Windows 요청: 웹 UI spike 확인 (2026-10-28)

> 이 문서는 **Windows 쪽에서 실행**하기 위한 요청이다.
> - **[에이전트]** 표시: Windows 에이전트가 명령을 실행하고, 출력 **원문 줄**을 그대로 옮긴다.
> - **[사용자]** 표시: 사용자가 앱 창에서 직접 조작하고 판단한다.
> - 통과 기준은 [README](README.md#pass-criteria-frozen-before-the-first-windows-run)의 W1–W9이다. 실행 전에 고정됐다.
> - 결과 파일은 Windows에 남기고, 아래 **결과 양식**만 텍스트로 돌려준다.

## 0. 소스 확인 [에이전트]

1. GitHub에서 **`spike/webui` 브랜치**의 ZIP을 받는다(`main` 아님). 압축을 푼 폴더를 저장소 루트로 쓴다.
2. 아래 명령으로 파일별 SHA-256을 출력하고, 표와 다른 줄이 있으면 그 줄만 적는다.

   ```powershell
   Get-FileHash spikes\webui\app.py, spikes\webui\context.py, spikes\webui\server.py, spikes\webui\spike.spec, spikes\webui\requirements.txt, spikes\webui\static\* -Algorithm SHA256 | Format-Table Hash, Path -AutoSize
   ```

   | 파일 | SHA-256 |
   |---|---|
   | app.py | a7ce77db6bf9480adc2e15cab78f50b03cd55b6b5e989f2c199b408b27ee2292 |
   | context.py | edda06f79e4762ec39a66cf61e7a2fd9f1bf55dbc6a0661432a74c9c41958449 |
   | server.py | 62c1db08bb93b0c4769553e676c955013a8041be4a7c421dd4264fc0f2f4a857 |
   | spike.spec | 07ed19d4bbb673d192f16c275a877a2239a383bc5ea7833109f69c72f73ab602 |
   | requirements.txt | d255d197adb749fc5ec2e45496098930524cce88e432f9f9d6835d0aa3847153 |
   | static/editor.js | d98794fef6e43586c44eaec5ecfc786007bd8fa3ca4fd0eca8028d8b83de29f8 |
   | static/render.js | 1d07ed727a9acf95c87314636cfaeefd4e16a286b23eded23b7ffff810c4b478 |
   | static/index.html | 0e70393765857f95ea694344e0cedd25adafd9bbffcaee6142041f9291e45c1e |
   | static/style.css | 95789953d4cc7cd79a8212748cd804dd8ccad896f92197c42451103bc9e027b1 |

   Git이 줄바꿈을 CRLF로 바꾸면 해시가 달라질 수 있다. 그 경우 "CRLF 변환" 여부를 적는다.

## 1. 환경 [에이전트]

기존 v1 venv와 섞지 않도록 **새 venv**를 만든다.

```powershell
py -3.14 -m venv .venv-spike
.venv-spike\Scripts\python -m pip install -r spikes\webui\requirements.txt
.venv-spike\Scripts\python --version
.venv-spike\Scripts\python -m pip list | Select-String "pywebview|pythonnet|clr.loader|opencv|numpy|pyinstaller"
```

WebView2 런타임 버전을 확인한다. 둘 중 하나라도 값이 나오면 그 값을 적고, 둘 다 없으면 "없음"이라고 적는다.

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction SilentlyContinue).pv
(Get-ItemProperty 'HKCU:\Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction SilentlyContinue).pv
```

## 2. 소스로 실행 (W2–W4, W7) [에이전트 → 사용자]

영상과 Recipe는 지난 S11 실행과 같은 파일이다. **Recipe는 수정하지 않는다.** spike는 Recipe에서 Glass 타원과 기준선만 읽는다.

- **A. SPL#4 BASE:**
  - 영상: `SPL#4_Cooling_onoff_#2.mp4` (53,165,455 bytes인지 확인)
  - Recipe: `sample4_test_artifact_R22.oilrecipe`
- **B. SPL#1 BASE:**
  - 영상·Recipe: ⑩(`…_top_exit_v3_20261021_170933`)과 같은 것
  - Recipe 파일: 그 bundle의 `recipe_snapshot.oilrecipe`

```powershell
.venv-spike\Scripts\python spikes\webui\app.py --video "<SPL#4 영상>" --recipe "<SPL#4 Recipe>" --glass-name BASE --out C:\webui-spike\spl4-base
```

- Glass 이름이 `BASE`가 아니면 오류에 실제 이름 목록이 나온다. 그중 BASE에 해당하는 이름으로 다시 실행하고, 쓴 이름을 적는다.
- **방화벽이나 보안 경고 창이 뜨면** 허용하지 말고 닫는다. 창이 떴다는 사실과 문구를 적는다(W3).
- 창이 열리면 **[사용자]**가 아래 3절을 진행한다. 창을 닫은 뒤 콘솔의 `SPIKE `로 시작하는 줄을 **전부 원문 그대로** 적는다(`context_progress` 줄은 마지막 1줄만).
- 그다음 B(SPL#1 BASE)를 `--out C:\webui-spike\spl1-base`로 같은 방식으로 실행한다.

## 3. 앱 창에서 직접 조작 [사용자]

A와 B 각각에서 진행한다. 각 항목에 **O / X**와 한 줄 소감을 남긴다.

| ID | 할 일 | 볼 것 |
|---|---|---|
| W2 | 창이 뜨는지 확인 | 오른쪽 "진단" 첫 줄 `engine:` 값 (`WebView2 Edg/…`인지) |
| W4 | 맥락 이미지 확인 | 아래 패널에 시간×높이 이미지가 보이는지. 진단의 `context:` 줄 |
| W7 | 그래프 빈 곳을 여러 번 클릭 | 오른쪽에 원본 프레임과 선이 맞게 겹쳐 보이는지. 10번 이상 클릭한 뒤 진단의 `frame seek median` 값 |
| W5 | 점 드래그, 점 두 번 눌러 꼭짓점 전환, Delete로 삭제, Ctrl+Z / Ctrl+Shift+Z | 의도대로 되는지 |
| W5 | "새 선"으로 Foam 선 → 점 추가(A) 몇 개 | 주황 선이 생기는지 |
| W5 | 구간(S)으로 FULL 구간 드래그, 메모(M) 찍고 내용 입력 | 구간 띠, 메모 번호, 메모 목록 |
| W5 | 휠(시간 확대), Shift+휠(높이 확대), 빈 곳 드래그(이동), F(전체) | 부드러운지 |
| W6 | "스냅" 켠 상태에서 점을 맥락 이미지의 경계 근처로 드래그 | 경계에 붙는지 |
| W9 | 점이 많은 구간에서 빠르게 드래그 | 끊김이 있는지. 진단의 `render median / max` |
| — | "배경 제거 보기" 켜기/끄기 | 이미지가 바뀌는지 |
| W8 | "저장" → "보고서 만들기" | 보고서가 Edge로 열리는지 |
| W8 | 네트워크를 끊은 상태에서 보고서를 다시 열기 → "인쇄 / PDF 저장" → PDF로 저장 | PDF에 그래프·맥락 이미지·메모가 읽을 수 있게 나오는지 |
| — | 앱 안 "앱 안에서 인쇄" | 인쇄 대화상자가 뜨는지 (참고용) |
| — | 앱을 닫았다가 같은 명령으로 다시 실행 | "저장본 v001 불러옴"이 뜨는지 |

마지막으로 **전체 소감**을 한두 줄 남긴다: 이 방식으로 편집 화면을 계속 만들어도 되겠는지.

## 4. 패키징 (W1) [에이전트 → 사용자]

```powershell
.venv-spike\Scripts\pyinstaller --noconfirm spikes\webui\spike.spec
"{0:N1} MB" -f ((Get-ChildItem dist\oil-webui-spike -Recurse -File | Measure-Object Length -Sum).Sum / 1MB)
(Get-ChildItem dist\oil-webui-spike -Recurse -File).Count
dist\oil-webui-spike\oil-webui-spike.exe --video "<SPL#4 영상>" --recipe "<SPL#4 Recipe>" --glass-name BASE --out C:\webui-spike\spl4-base-exe
```

- 빌드가 실패하면 마지막 오류 20줄을 원문으로 적는다.
- exe 창이 뜨면 **[사용자]**가 W2(engine 값), W7(클릭 몇 번), W8(보고서 만들기)만 짧게 확인한다.
- 창을 닫은 뒤 `SPIKE ` 줄을 원문으로 적는다.

## 결과 양식 (이 블록만 텍스트로 돌려준다)

```
[0] 소스: SHA-256 불일치 줄 = (없음 / 해당 줄) ; CRLF 변환 = (예/아니오)
[1] python = ; pywebview = ; pythonnet = ; clr_loader = ; opencv = ; numpy = ; pyinstaller =
[1] WebView2 런타임 = (버전 / 없음)
[2-A] SPL#4 BASE 사용 Glass 이름 = ; 방화벽/보안 창 = (없음 / 문구)
[2-A] SPIKE 줄 원문:
...
[2-B] SPL#1 BASE 사용 Glass 이름 = ; 방화벽/보안 창 = (없음 / 문구)
[2-B] SPIKE 줄 원문:
...
[3-A] W2 = O/X (engine: ) ; W4 = ; W7 = (seek median: ) ; W5 = ; W6 = ; W9 = (render median/max: ) ; 배경 = ; W8 저장·열기 = ; W8 오프라인 PDF = ; 앱 안 인쇄 = ; 재실행 불러오기 =
[3-B] (같은 형식)
[3] 전체 소감 =
[4] 빌드 = 성공/실패 ; dist 크기 = MB ; 파일 수 =
[4] exe: W2 = (engine: ) ; W7 = ; W8 =
[4] SPIKE 줄 원문:
...
```
