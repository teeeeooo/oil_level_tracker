# 로컬 실험 산출물 관리

**상태: 적용 중.** 새 가설 검토·로컬 재현 실행의 저장 절차와 종료 검사를 소유한다.
기본 흐름은 **임시 생성 → 필요한 증거만 보존 → 나머지 즉시 제거**다.
기존 frozen 실행, 원본 영상, 앱 사용자의 결과 bundle, 공용 cache, 개발 환경은
자동 삭제 대상이 아니다. CR-1 실행 권한과 전체 추가 3 GB 제한은 각각
[Work Plan](../00-project/work-plan.md#repository-cleanup-and-isolated-cr-1-sequence)과
[기존 실험 계약](../20-architecture/s11-contextual-role-observation-design.md#local-footprint-and-removal-contract)이 소유한다.

## 적용 위치

| 장치 | 책임 |
|---|---|
| 이 문서 | 무엇을 보존하고 언제 정리하는지에 대한 단일 절차 |
| `AGENTS.md` / 기존 S11 Skill | 실험 산출물을 만들기 전에 이 절차로 연결 |
| [experiment_artifacts.py](../../scripts/experiment_artifacts.py) | 새 실행의 소유 범위·입력·예산 기록, 보존 목록 확인, 자기 임시 파일 정리, 종료 검사 |
| [pre-push](../../.githooks/pre-push) | 로컬 관리 실행의 미완료·변조·미분류 파일·중복·예산 초과 시 push 중단. 삭제하지 않음 |

`sample/output`은 Git 제외이므로 원격 CI만으로 이 상태를 검증할 수 없다.
훅은 `core.hooksPath=.githooks`인 checkout에서 동작하며, 새 clone에서는 기존
`scripts/install_git_hooks.sh`로 설치한다. 훅은 우회 가능한 보조 검사이며 실행기나
실시간 디스크 quota가 아니다. 관리 표식 없이 임의로 만든 출력과 역사 폴더는
자동 탐지·정리하지 않는다. **새 연구 출력은 아래 입구를 사용**하고, 기존
runner도 출력 위치를 새 실행의 `work/`로 지정한다. 고정 경로가 필요한 역사
runner는 소스·원래 입력을 확인하고 필요한 복원본만 임시로 준비한다.

일반 단위테스트의 `tmp_path`/`TemporaryDirectory`는 기존 테스트 수명 주기를
그대로 사용한다. 영구 연구 출력이 없는 읽기 전용 조사·문서 수정 때문에
빈 관리 실행이나 별도 보존 기록을 만들지 않는다.

## 새 대용량 출력의 저장 위치

앞으로 생성하는 **대용량 연구·검증 출력은 반드시 Git 제외된 `sample/output/`
아래에서 관리**한다. 전체 trace·대형 JSON/JSONL, 연속 프레임·crop 묶음,
feature/배열, 실험 결과 bundle·ZIP 등이 해당한다.

- 기존 `experiment_artifacts.py start`로 실행 범위를 만들고 `work/`에 생성한다.
  종료 때 필요한 자료만 같은 실행의 `evidence/`에 보존한다.
- Git의 `docs/`에는 결론·조건·전체 분모를 담은 간결한 요약과 필요한 작은
  근거를 남기고, 대용량 원본은 로컬 상대 경로·SHA-256으로 연결한다.
  대용량 출력을 문서 첨부 목적으로 복사하거나 강제 추가하지 않는다.
- `sample/output/` 보존은 GitHub 백업이나 Windows 전달을 뜻하지 않는다.
  Windows 후보를 준비할 때 실제 필요한 입력·가중치·설정을 확인하고 전달
  구성에 명시한다. 이미 추적 중인 실행 필수 자료를 일괄 제외하지 않는다.
- 이 규칙은 새 출력부터 적용한다. 기존 자료의 삭제·이동·추적 해제는 별도
  저장소 정리 작업에서 검토하며, 예정된 cost-first·RGB·Local XY Windows
  비교에 쓰일 수 있는 현재 보존 자료는 그대로 둔다.

## 시작 전: 복제 대신 참조

- 기존 입력·완료 결과·counterexample을 먼저 찾는다. 입력 경로와 SHA-256,
  관련 source bytes, 조건·명령·runtime 버전을 기록한다. Git HEAD는 이력 좌표이며
  실제 관련 source hash도 함께 남긴다. dirty code라면 필요한 patch/고유 파일만 보존한다.
- 동일 입력·관련 source·parameters의 기존 관리 실행은 `start` 결과의
  `matching_closed_runs`로 알린다. 재사용 가능 여부를 확인한 뒤 실행한다.
  성능 재측정·독립 재검증 등 필요한 반복을 자동 생략하지 않는다. 재실행 이유와
  비교에 영향을 주는 runtime 차이는 parameters에 기록한다.
- 전체 소스 checkout, 원본 영상, 이미 있는 capture/reference bank를 복제하지 않는다.
  독립 비교에 실제로 필요한 산출물과 임시/최종 bytes 예산을 실행 전에 정한다.
  예산은 실행별 명시값이며 예산을 넘으면 조건·보존 방식을 재검토한다.
- CR-1의 실행 경로는 `sample/output/s11-cr1-workspace/runs/<run-id>`다. 환경·모델·cache를
  포함한 workspace 전체 3 GB 상한은 별도 합산 확인한다. 아래 run 검사만으로
  전체 CR-1 용량 계약을 충족했다고 주장하지 않는다.

다음은 형식 예시다. 파일 목록·parameters·예산은 해당 실험 계획으로 바꾼다.
plan과 보존 선택표는 작업용 임시 폴더에 만들고 정리한다. 그 내용은 최종 실행
표식에 포함되므로 같은 JSON을 여러 곳에 중복 보존할 필요가 없다.

```json
{
  "purpose": "고정 조건에서 가설을 반례와 비교",
  "sources": ["scripts/example_probe.py"],
  "inputs": ["sample/output/existing/capture.png"],
  "parameters": {"condition": "frozen", "command": "...", "runtime": "..."},
  "scratch_budget_bytes": 100000000,
  "retain_budget_bytes": 10000000
}
```

```bash
python3 scripts/experiment_artifacts.py start \
  --run sample/output/example-001 --plan /tmp/example-plan.json
```

기존 디렉터리는 입양하거나 덮어쓰지 않는다. 출력된 `work` 경로 아래에만
이번 실행의 중간 산출물을 쓴다. 관리 표식에는 입력·source의 길이/hash,
parameters, HEAD, 예산을 저장한다. 한 실행에는 하나의 writer만 사용한다.

## 실행 중: 임시 자료와 최종 증거 구분

재사용 가능한 기존 패턴은
[witness replay의 TemporaryDirectory](../../tests/diagnostics/s11_interface_witness_replay.py)다.
단계별 대용량 trace/bundle은 관리 `work/` 아래의 `TemporaryDirectory`에서 생성하고,
필요한 요약·검증·counterexample을 취한 뒤 context를 벗어나며 즉시 제거한다.
기존 runner를 단지 저장 방식 때문에 새로 구현하지 않는다.

FULL trace·전체 frame 이미지는 해당 비교가 요구할 때만 생성한다. 수치 비교는
후보 전체/분모/unknown을 잃지 않는 작은 표를 우선 사용하고 JSONL/큰 JSON은
소비자를 확인한 뒤 gzip으로 기록한다. PNG/NPZ/ZIP을 다시 압축하는 중복층은 피한다.
검토 이미지는 판단에 필요한 프레임·반례만 선택한다. dense feature는 비교 후 버린다.

큰 파일을 쓰는 배치 사이와 종료 전에 다음을 호출한다.

```bash
python3 scripts/experiment_artifacts.py check --allow-open
```

검사는 **호출 시점**의 논리적 파일 bytes와 metadata를 예산과 비교한다.
실시간 최고 사용량이나 APFS 물리 할당량을 측정하지 않는다. 갑작스러운 대량 쓰기를
막으려면 runner 자체도 생성량을 계산하고 스트리밍/배치 경계를 지켜야 한다.

## 종료: 명시한 것만 남기기

writer를 중지하고 **삭제했을 때 잃는 의사결정 정보**부터 심사한다. 문서·테스트에서
참조됨, 오래 보관함, 재현기가 기대함, 고유 hash임, 압축하면 작아짐은 각각
보존 가치의 증명이 아니다. 참조는 고쳐야 할 의존성을 찾는 데 사용한다.

보존할 자료가 있으면 실행별 `retention_review`에 다섯 가지를 기록한다.
같은 목적의 여러 파일은 하나의 검토로 묶고, 파일별 `reason`은 그 검토와 연결한다.

| 질문 / 필드 | 필요한 판단 |
|---|---|
| `decision_use` | 어떤 현재 결정·회귀 위험·구체적 후속 비교에 쓰는가? |
| `loss_if_removed` | 삭제하면 어떤 관측·반례·판정 근거를 잃는가? 이미 다른 owner에 있는가? |
| `reproduction` | 원본·source·조건으로 다시 만들 수 있는가? 비용과 재실행 금지·환경 차이는 무엇인가? |
| `minimality` | 작은 요약·전체 비교 표·핵심 반례·기존 참조로 대체할 수 없는 부분만 골랐는가? |
| `review_when` | 어느 결정·후속 기준 교체 시 보존 가치를 다시 심사할 것인가? |

그 판단에 필요한 다음 정보를 보존 목록으로 확정한다.

- 성공/실패/중단 판정, 입력·조건·source와 연결되는 간결한 요약;
- 비교 전체와 분모·누락·대조군을 확인할 수 있는 수치 자료;
- 판단에 필요한 긍정 사례와 핵심 반례, 필요한 경우 압축 원본 증거;
- 기존 파일을 다시 쓰지 않는 `reuse` 경로와 보존 이유.

실패한 가설도 재발 방지에 필요한 결론·조건·핵심 반례면 충분하다. 전체 실행을
그대로 재현할 가치가 없으면 모든 중간 trace·배열·소스 사본을 보존하지 않는다.
통과한 과거 test XML은 보통 commit·환경·명령·성공/실패/누락 수로 대체할 수 있다.
실패 상세가 미해결 원인 분석에 필요할 때만 해당 상세를 남긴다.

스크립트와 훅은 이 검토의 **기록 존재**와 파일 상태를 검사한다. 문장의 실질적
타당성·과학적 충분성·field acceptance를 승인하지 않는다. 담당자가 위 질문으로
가치를 설명하지 못하면 우선 보존 대상에서 제외하고, 안전한 삭제에 필요한 기존
참조·현재 재현 범위 설명을 함께 수정한다.

```json
{
  "verdict": "CLOSED WITHOUT PROMOTION: 고정 반례에서 가설 실패",
  "retention_review": {
    "decision_use": "같은 실패 가설을 조건 변경 없이 다시 시도하는 것을 방지",
    "loss_if_removed": "실패한 대조군과 전체 비교 분모를 확인할 근거가 사라짐",
    "reproduction": "source와 원본은 남지만 전체 실행 재측정은 이 작은 기록보다 비용이 큼",
    "minimality": "요약·전체 점수·핵심 반례만 남기며 dense feature와 전체 trace는 제거",
    "review_when": "후속 검증이 같은 실패를 더 작은 기준 증거로 대체할 때"
  },
  "keep": [
    {"path": "summary.json", "reason": "최종 판정과 전체 비교 분모"},
    {"path": "scores.jsonl.gz", "reason": "모든 후보와 대조군 점수"},
    {"path": "counterexample.png", "reason": "실패를 재검토할 핵심 반례"}
  ],
  "reuse": [],
  "discard_reason": "판정에 사용한 증거를 위에 보존했고 나머지는 재생성 가능한 중간물"
}
```

`keep`의 경로는 `work/` 기준이다. `reuse`는 `{"path":"저장소 상대 경로",
"reason":"재사용 이유"}` 형식이다. 출처만 있는 중단 실행은 구체적 판정·폐기 사유와
빈 `keep`으로 닫을 수 있다. 다른 관리 실행/입력과 같은 bytes는 참조로 남긴다.

```bash
python3 scripts/experiment_artifacts.py finish \
  --run sample/output/example-001 --selection /tmp/example-keep.json
python3 scripts/experiment_artifacts.py check
```

`finish`는 보존 자료가 있으면 가치 검토 5항목을 요구하며, 예산·경로·hash·중복을
먼저 확인한다. 검증 실패 시 삭제하지 않는다.
통과하면 같은 run의 선택하지 않은 `work/` 파일만 제거하고, 남은 디렉터리를
`evidence/`로 rename한다. 추가 전체 사본을 만들지 않는다. 판정·보존/재사용 hash·삭제
건수·크기는 `.artifact-run.json`에 남는다. 닫힌 증거는 덮어쓰지 않는다.

삭제 단계 중 중단되면 기록된 `closing` intent를 검토한 뒤 `--selection` 없이
같은 `finish` 명령을 재호출한다. 새로 생겼거나 바뀐 파일, symlink, 기존 폴더는
자동 삭제하지 않는다. metadata 쓰기 도중 남은 `.pending` 파일은 명시적으로
확인·복구해야 한다. 비정상 종료의 `open`/`closing` 표식은 다음 검사와 push에서
보고한다. 경과 시간이나 최근 접근 시각만으로 폐기하지 않는다.

완료 증거 문서는 기존 `50-diagnostics`/`60-evidence` owner에 연결하고,
로컬 대용량 payload는 Git에 넣지 않는다. 핵심 판정·관련 hash는 Git으로 남겨야 하며
로컬 marker만 존재한다고 원격 백업이 된 것은 아니다. 작업용 plan/선택표,
임시 복원본·테스트 데이터도 해당 작업의 소유 범위에서 제거한다.

보존은 영구 면책이 아니다. `review_when`의 사건이 생기거나 사용 목적이 끝났으면
그 작업의 closeout에서 기존 증거를 재심사한다. 더 작은 후속 증거로 대체하거나
가치가 없어진 자료는 참조를 정리하고 그때 제거한다. 따로 정기 백업 ZIP을 만들지
않는다. 관리 실행의 frozen marker를 조용히 바꾸지 말고 현재 owner에 폐기 사유,
살아 있는 대체 증거와 복구 불가 범위를 남긴 뒤 해당 실행 소유 자료를 정리한다.
입력·다른 실행의 `reuse` 소비 경로를 먼저 해소하며, 훅은 자동 삭제를 하지 않는다.

기존 저장 증거의 현재 보존·폐기 범위는
[정리 체크포인트](../60-evidence/s11/2026-10-12-pre-cr1-cleanup-checkpoint.md)의
`retention.json`을 따른다. 과거 통합/압축 manifest는 당시 기록이며 전체 복구
약속이 아니다. 과거 machine receipt의 bytes·판정을 새 결과처럼 재작성하지 않는다.
