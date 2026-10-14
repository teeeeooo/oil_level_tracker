# Windows ZIP 설치 환경: 기존/후보 bundle 비교

**Windows 결과 수신 전. 후보는 미채택 상태다.** Windows는 Git clone을 사용할 수
없는 격리 환경이며, 사용자가 GitHub 소스 ZIP을 받아 각각의 폴더에 압축 해제한다.
이 절차는 그 환경에서 **GUI로 분석을 완료한 결과 bundle을 비교**하는 방식이다.
이미 있는 베이스라인 bundle을 먼저 확인하며, 무조건 두 번 재실행하지 않는다.

이전 문서의 Git checkout 절차는 이 환경에 맞지 않았다. 또한
`python -m oil_tracker`는 GUI를 열고 사용자 입력을 기다리는 명령이다.
분석이나 두 bundle의 비교를 자동 실행하지 않는다. Windows 담당 에이전트는
폴더 경로를 받았다는 이유만으로 GUI를 띄워 놓고 기다리지 말고, 먼저 기존
bundle과 소스의 비교 가능 여부를 확인한다. GUI 분석은 아래의 사용자 작업이다.

현재 후보의 [로컬 결과](../60-evidence/s11/2026-10-14-overlay-support-guard.md)는
B 입력 복구와 기존 sequence 테스트 1개 실패를 함께 기록한다. 이 비교는 그 실패를
공개한 상태의 현장 조사다. [현재 field 절차](s11-current-windows-field-qualification.md),
[후보 계약](../20-architecture/s11-chromatic-overlay-support-design.md),
[원본 영상 판정](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)이
각각 실행·검증·물리적 판정의 기준이다.

## 1. 기존 베이스라인 bundle부터 재사용 여부 확인

다음 항목을 `analysis_manifest.json`, `session.json`,
`recipe_snapshot.oilrecipe`와 사용한 소스 폴더에서 확인한다.

| 비교 항목 | 확인 내용 |
|---|---|
| 영상 | 동일한 원본 bytes. 경로가 달라도 가능하며 파일 SHA-256으로 식별 |
| 프로필 | 활성 Glass, ROI, zero line, detector settings, Artifact/exclusion 설정, 초기 상태가 동일 |
| 실행 조건 | 분석 시작/종료, 압축기 기동 시각, sampling FPS, 초기 상태 확인이 동일 |
| 소스 | 기존 bundle을 실제 생성한 소스 ZIP/폴더가 식별되는지 확인 |
| 실행 환경 | Python/OpenCV 등 환경 차이를 기록. 차이가 있으면 마스크 변경만의 효과나 속도 변화로 단정하지 않음 |
| 기록 수준 | NONE/BASIC/FULL과 trace의 실제 프레임 범위를 확인. 기록 수준이 달라도 전체 tracking 비교는 가능 |

run ID, 실행 날짜, 결과 폴더명은 달라도 된다. 두 입력 영상이 같은지 경로 이름만으로
판단하지 않는다. 현재 bundle manifest는 영상의 cryptographic hash와 전체 소스
commit/hash를 자동 기록하지 않으므로, 그 정보가 저장되어 있다고 가정하지 않는다.
현재 남아 있는 소스 폴더가 과거 bundle을 만든 폴더인지도 확인한다.

조건과 소스가 맞으면 **기존 베이스라인 bundle을 보존하고 후보만 새로 실행**한다.
기존 버전이나 조건이 다르거나 일부를 확인할 수 없어도 우선 전후 결과로 읽을 수는
있지만, 이를 지정된 소스 쌍의 통제된 A/B 결과라고 보고하지 않는다. 부족한 정보와
비교 범위를 먼저 정리하고 필요한 경우에만 지정 베이스라인을 재실행한다.

## 2. Git 없이 소스 식별

| 항목 | 식별값 |
|---|---|
| 지정 베이스라인 ZIP의 원본 commit | `747c1bccaa8dab18d6cb3a2b3dc3e549bcfc668f` |
| 후보 코드 동결 commit | `0073defdd34d71c489f63acb4af574a244e7447d` |
| 결과/인수인계가 포함된 후보 ZIP 기준 commit | `72775f84adefd6ef1e269eaef653dc4c575cf095` — 동결 후보와 `src`/`tests` 동일 |
| 후보 preprocessing SHA-256 | `c25950c59b604c74f35db8973130a81078e8658c8cc571a3464a2855ec17b902` |
| Detector version, 두 버전 공통 | `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1` |
| Resolver version, 두 버전 공통 | `r22-oil-ownership-evidence-replacement-v1` |

사용자가 제공한 각 압축 해제 폴더와 다운로드한 ZIP의 원본 commit/URL을 기록한다.
**폴더명이나 detector version 문자열만으로 두 버전을 구분하지 않는다.**
Git 명령, `.git` 디렉터리, Windows의 네트워크 접속은 필요 없다.

전체 소스의 기준 파일별 SHA-256은 이미 보존된
[baseline manifest](../50-diagnostics/s11/2026-10-14-overlay-component-review/replay-baseline.json.gz)와
[candidate manifest](../50-diagnostics/s11/2026-10-14-overlay-component-review/replay-candidate.json.gz)의
`source_files`에 있다. Windows 담당 에이전트는 Python 표준 `gzip`/`json`/`hashlib`로
각 폴더의 `src/**/*.py` 경로 집합과 파일 bytes를 그 표와 대조할 수 있다.
소스 원본을 복제하거나 Git tree ID를 재구성할 필요가 없다. preprocessing 파일
하나의 hash만 맞는 것은 전체 소스 일치의 증명이 아니다. 다른 버전인 기존 설치를
지정 베이스라인으로 이름만 바꾸지 않는다.

## 3. 사용자가 GUI에서 분석 완료

1. 위 조건을 만족하는 기존 베이스라인 bundle을 확보한다. 없거나 맞지 않으면
   베이스라인 폴더의 프로그램으로 한 번 실행해 완료된 bundle을 만든다.
2. 후보 폴더의 프로그램을 실행하고 **같은 원본 영상과 프로필**을 연다.
   기존 `recipe_snapshot.oilrecipe`를 재사용할 수 있다. `session.json`의 분석 구간,
   sampling FPS, 압축기 기동 시각을 맞추고, 각 Glass의 분석 시작 상태를 확인한다.
   새 정규 비교라면 canonical 구간은 **480–780 s**, 기존 설정은 **2 Hz**다.
   기존 bundle의 조건이 다르면 그것을 숨긴 채 동일 비교라고 취급하지 않는다.
3. `분석 기록 옵션`을 선택하고 설정 점검 후 **분석을 시작해 결과 저장 완료까지**
   기다린다. 이 단계는 GUI 창을 여는 명령에 포함되어 있지 않다.
4. 후보 결과를 별도 이름/출력 폴더로 저장한다. 원래 베이스라인 bundle은 그대로
   보존한다. 같은 프로필, 마스크 설정, 초기 상태와 Local XY OFF를 유지한다.

기록 수준은 다음과 같이 사용한다.

- `문제 장면만 저장 — 권장`(BASIC): 전체 tracking CSV와 선택된 장면의 후보/마스크
  trace를 보존한다. 기존 bundle이 이 수준이어도 우선 비교할 수 있다.
- `모든 장면 저장 — 개발용`(FULL): 모든 **분석 sample**의 상세 기록을 보존한다.
  이번 마스크 원인을 빠짐없이 비교하려면 유용하지만 시간과 용량이 증가한다.
  원본 영상의 모든 프레임을 저장한다는 뜻은 아니다.
- `저장 안 함`(NONE): 전체 tracking 비교는 가능하나 해당 실행의 마스크/후보 trace는
  없다. trace 부재만으로 기존 결과 전체를 폐기하거나 자동 재실행하지 않는다.

기존 BASIC/후보 FULL처럼 수준이 다르면 결과 비교와 확보된 장면의 원인 검토는
가능하다. 다만 실행시간 차이를 detector 속도 차이라고 해석하지 않는다. trace가
없는 변경 장면은 원인 미확인으로 남기고, 추가 실행이 필요한 범위를 먼저 정한다.

## 4. 결과 전달과 비교

Windows 담당 에이전트에 **베이스라인 bundle 경로, 후보 bundle 경로, 각각을 만든
소스 폴더/ZIP 식별 정보**를 제공한다. 다른 환경으로 옮길 때에는 각 완료된 bundle
폴더 전체를 ZIP으로 묶는다. `data trace`나 CSV만 골라내지 않는다.

현재 bundle의 주요 파일은 다음과 같다. 없거나 구버전 형식이면 그 상태를 기록한다.

- `analysis_manifest.json`, `session.json`, `recipe_snapshot.oilrecipe`
- `tracking_data.csv`, `events.csv`, `retrospective_interpretation.json`
- `review_index.json`, `report.html`, `assets/`, `graphs/`
- trace가 있는 경우 `debug/debug_index.json`, `debug/debug_trace.jsonl`, `debug/frames/`

비교자는 먼저 입력/프로필/실행 범위를 확인하고, Glass와 source frame/time으로
**전체 tracking 행**을 대응시킨다. 누락/추가 행, Oil/Foam 좌표, 상태, flags와
selected-candidate 출처를 비교한 다음, 확보된 trace의 원본 ROI·glare mask·후보를
읽어 변경 원인을 좁힌다. BASIC의 선택 장면만으로 전체 변화 분모를 만들지 않는다.

물리적 개선 판정은 기존 [아홉 WS1 구간](s11-current-windows-field-qualification.md#4-reconcile-all-reviewed-segments)을
모두 포함해 수행한다. 수치 개수, 그래프 모양이나 후보 출력 자체가 정답은 아니다.
부족한 trace/원본 판정은 명시하며, 기존 로컬 sequence 실패도 계속 미해결 항목으로
남긴다. 이 문서 수정으로 Windows 실행, 후보 채택 또는 FIELD PASS가 성립하지 않는다.
