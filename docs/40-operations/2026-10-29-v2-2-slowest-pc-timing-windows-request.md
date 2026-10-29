# Windows 요청: 최저 사양 PC 분석 시간 측정 (A4) (2026-10-29)

> 이 문서는 **사용자가 최저 사양급 PC의 터미널에서 직접** 실행하는 절차다. 그 PC에는 코딩 에이전트가 없다.
> - 명령 3줄을 차례로 붙여넣으면 스크립트가 단계별로 측정하고, 결과를 마크다운 파일로 저장하면서 화면에도 출력한다.
> - **판단 기준**은 아래 "판단 기준" 절에 있고, 실행 전에 고정됐다.
> - 결과 파일의 **내용 전체**를 돌려주면 된다.

## 무엇을 확인하나

인수 기준 A4는 68분짜리 SPL#1의 분석이 **3분(180초) 안**에 끝나는 것이다. 이 기준은 검사자 PC 가운데
가장 느린 사양급(Intel Xeon E5-1620 v3, RAM 16GB, NVIDIA Quadro K620)에서 지켜야 한다(Product SSOT §2).

- 워크스테이션에서는 87.4초였다([결과](../60-evidence/2026-10-29-v2-2-analysis-timing-windows-result.md)).
  같은 코드를 이 PC에 맞춰 환산하면 약 190–210초로, 한도를 넘는다.
- 그래서 영상 디코딩과 행별 중앙값 계산을 **동시에** 돌리도록 바꿨다. 이번에는 앱이 쓰는 분석 코드 그대로 시간을 잰다.
- 소프트웨어 디코딩과 하드웨어 디코딩(K620)으로 한 번씩, 모두 두 번 분석한다.
- 스크립트는 결과 파일 하나만 쓴다. 영상과 Recipe는 읽기만 한다.

## 1. 준비 [사용자]

1. **Python 3.14**: PowerShell에서 `py -3.14 --version`을 실행해 `Python 3.14.x`가 나오면 된다.
   없으면 python.org → Downloads → Windows에서 Python 3.14를 설치하고, PowerShell을 새로 연다.
2. **인터넷 연결**: 3절의 두 번째 명령이 OpenCV와 NumPy를 받는다. 인터넷이 없으면 5절을 따른다.
3. **워크스테이션에서 파일 2개를 복사**해 이 PC의 **로컬 디스크**(예: `C:\a4\`)에 둔다. 네트워크 드라이브에 두지 않는다.
   - `SPL#1_Heating_coldstart.mp4` (683,165,477 bytes)
   - `문서\OilLevelTracker\Recipes\SPL#1_test1_607bccb.recipe.json`
4. **소스**: 아래 주소의 ZIP을 받아 압축을 푼다. 커밋 하나로 고정된 코드다.
   `https://github.com/teeeeooo/oil_level_tracker/archive/2d43f4ca88382e802a921f2d18e0177986aeea71.zip`
5. 측정 중에는 **다른 프로그램을 닫는다.** 노트북이면 **전원을 연결**한다.

## 2. PowerShell 열기 [사용자]

압축을 푼 폴더(`oil_level_tracker-2d43f4ca…`, 안에 `scripts`와 `src` 폴더가 있다)를 탐색기로 열고,
주소창에 `powershell`을 입력한 뒤 Enter를 누른다. 그 폴더에서 PowerShell이 열린다.

## 3. 실행 [사용자]

아래 3줄을 한 줄씩 붙여넣고 Enter를 누른다. 마지막 줄의 두 경로는 1절에서 파일을 둔 실제 위치로 바꾼다
(`#`이 든 경로라 큰따옴표는 그대로 둔다).

```powershell
py -3.14 -m venv .venv-timing
.venv-timing\Scripts\python -m pip install opencv-python-headless==4.14.0.94 numpy==2.5.4
.venv-timing\Scripts\python scripts\time_analysis.py --video "C:\a4\SPL#1_Heating_coldstart.mp4" --recipe "C:\a4\SPL#1_test1_607bccb.recipe.json"
```

- 화면에 `[1/4]`부터 `[4/4]`까지 단계가 나온다. 분석 중에는 30초마다 `progress` 줄이 나온다.
- 두 번 분석하므로 몇 분에서 10분 정도 걸린다.
- 끝나면 결과 표가 출력되고, 마지막 줄에 `결과 파일: …\a4-timing-YYYYMMDD-HHMM.md` 경로가 나온다.
- 중간에 오류가 나도 스크립트는 다음 단계로 넘어가고, 오류 내용을 결과 파일에 적는다.

## 4. 돌려줄 것 [사용자]

- **결과 파일의 내용 전체.** 파일을 USB로 옮겨 붙여넣거나, 결과 표가 보이는 화면을 사진으로 찍는다.
- **메모:** 노트북인지 데스크톱인지, 전원 연결 여부, 닫지 못한 프로그램, 영상을 둔 디스크(SSD/HDD), 그 밖에 특이한 점.
- 2번째 명령(`pip install`)이 실패했다면 그 출력의 마지막 20줄.

## 5. 인터넷이 없을 때 [사용자]

인터넷이 되는 PC(워크스테이션)에서 OpenCV와 NumPy 설치 파일을 받아 USB로 옮긴다. Python 3.14 설치 프로그램도 같은 방법으로 옮긴다.

```powershell
py -3.14 -m pip download opencv-python-headless==4.14.0.94 numpy==2.5.4 --only-binary=:all: --platform win_amd64 --python-version 3.14 -d a4-wheels
```

`a4-wheels` 폴더를 측정 PC에 복사한 뒤, 3절의 두 번째 명령 대신 아래를 실행한다(경로는 실제 위치로).

```powershell
.venv-timing\Scripts\python -m pip install --no-index --find-links "C:\a4\a4-wheels" opencv-python-headless==4.14.0.94 numpy==2.5.4
```

## 6. 워크스테이션 (선택)

같은 ZIP으로 워크스테이션에서 3절을 한 번 더 실행하면, 같은 PC에서 새 코드가 얼마나 빨라졌는지(지난번 87.4초)와
그림이 같은지(`mean` 90.052)를 함께 볼 수 있다. 측정 PC 결과만으로도 판단은 된다.

## 판단 기준 (실행 전에 고정)

| ID | 조건 | 결정 |
|---|---|---|
| S1 | 결과 파일의 소스 줄이 `source=5f11f4928d2d files=38` | 소스가 맞다 |
| S2 | CPU 줄이 Xeon E5-1620 v3 또는 그와 비슷한 4코어 CPU | 최저 사양급 PC다 |
| C1 | software 실행 BASE의 `context`가 `8210x728`이고, `mean`이 워크스테이션의 90.052와 1.0 넘게 다르지 않다 | 같은 그림을 만든다 |
| T1 | software 실행의 `전체`가 **150초 이하** | 화면 작업(8단계)을 이대로 진행한다. 소프트웨어 디코딩을 쓴다 |
| T1 | 150초 초과 180초 이하 | 진행하되, V2-5 전에 더 줄인다 |
| T1 | 180초 초과 | 화면 작업 전에 속도를 더 높인다(영상 범위를 둘로 나눈 디코더 두 개, 또는 하드웨어 디코딩) |
| T2 | hardware 실행이 `HW 사용`=True이고, `전체`가 software보다 10% 이상 짧고, BASE `mean` 차이가 1.0 이하 | 이 PC급에서는 하드웨어 디코딩이 낫다. 어떻게 쓸지(설정 또는 자동 선택)를 사용자와 정한다. 아니면 소프트웨어 디코딩만 쓴다 |
| — | 결과 파일 끝이 `오류: 없음` | 오류가 없다 |

결과 표의 `wait`는 디코더가 중앙값 계산을 기다린 시간이다. 이 값이 크면 중앙값 계산이, 작으면 디코딩이 병목이다.
