# S11 실제 실행 인수인계 — 2026-10-13

## 현재 상태

- 저장소: `/Users/sunjaekim/Developer/oil_level_tracker`
- 기준 HEAD: `463ea1bb5aa2fb945a7f1871f0aa35f4940c8767`
- 작업 branch: `work/s11-material-reuse-20261013`
- 변경 상태: **로컬 미커밋. commit / push / merge 미실행.**
- 실행 판정: **REUSE_EXECUTED_NO_DETECTOR_PROMOTION**
- 유지: R22 behavior + R22-3/O1 diagnostics, Local XY OFF, O2 OPEN, FIELD FAIL.

실제 코드·테스트를 추가하고 기존 저장 증거를 이용해 실행했다.
완료한 범위는 이전 WP02/03 설계 중 **기존 자료의 역할·관측 지원·source 용도 연결**이다.
생산 detector 개선, 새 모델 학습, Windows 실증, report 판독 통과를 뜻하지 않는다.

## 이번에 구현한 것

`tests/diagnostics/s11_existing_material_reuse.py`는 기존 CR1 audit, 판정 정정 qualifier,
G0 Oil bindings, native-role qualifier를 재사용하는 오프라인 실행기다.

전체 164개 기록을 유지하고 160개 후보의 A1/O1 지원을 정확한 index/source/Y 및 subject hash로 검사한다.
최신 A/B 정정을 적용해 현재 후보 대응 6개, 거부 대상 3개, 별도 실용적 근사 B를 구분한다.
같은 후보를 다른 query ID로 중복 집계하거나 같은 Y의 다른 후보로 바꾸는 입력을 거부한다.

9개 원본 hash와 43개 context의 source 연결을 확인한다. 31개 고유 source-frame과 기존
1,335개 edge row는 모집단/지원 규모이지 독립 학습 정답의 개수가 아니다.
기존 N1–N5 판정 5개를 원래 qualifier로 재실행해 저장 결과와 동일함을 확인했다.

미소냉동 f1499의 중심열 전체 27개 native fragment를 복원했다. 기존 판정 범위와 양립하는
Foam 쪽 4개, Oil 쪽 3개를 원본 픽셀 위에 표시했다. 모두 UNREVIEWED이며 경로를 임의 선택하거나 라벨을 만들지 않았다.

## 실제 검증

| 검사 | 결과 |
|---|---|
| 새 검증 테스트 | 25개 |
| 관련 회귀 테스트 묶음 | **116 passed in 10.44 s** |
| 최종 실행 | `/private/tmp`에서 절대 경로로 실행, **5.6723 s** |
| CLI process-lifetime peak RSS | **203,931,648 bytes** |
| 재현성 | 첫 실행과 최종 실행의 JSON **284,322 bytes 전체 일치** |
| 원본/표시 검증 | 원본 ROI와 저장 RGB의 배열 동일성, 표시 경로 hash 확인 |
| Governance / whitespace | 통과 |
| Artifact lifecycle | **24 managed runs, errors 0** |
| 생산 코드/Recipe | HEAD 대비 diff 없음 |
| 휴대용 패치 | 기준 HEAD의 별도 임시 Git index에서 `git apply --check` 통과 |

메모리와 실행시간은 이 증거 연결 CLI의 측정값이지 detector 또는 Windows 성능이 아니다.
최초 실행 뒤 중복 후보 방어를 보강했고, 최종 실행 결과가 최초 결과와 바이트 단위로 같았다.
원본 이미지를 확인해 긴 설명의 겹침을 수정했으며 표시 좌표·원본 픽셀은 바꾸지 않았다.

## 다음 작업에 영향을 주는 확인 사항

### Oil: 후보 단위 판정과 native path 판정을 혼동하지 않는다

후보 대조군 9개 중 저장된 generator-path 상태가 있는 것은 3개이며 6개에는 없다.
양성 6개 중 4개가 경로 미저장이다. 경로가 있는 경우도 G0 표현은
POOLED_SECTOR_SAMPLES이므로 전체 픽셀 윤곽의 물리적 역할이 확인되었다는 뜻은 아니다.

후속 Oil 관측 비교는 이 9개를 **원래 후보 정밀도**로 사용할 수 있다.
하지만 스칼라 Y에서 수평선을 만들거나 새로운 윤곽을 추정해 native-fragment 학습 정답으로 쓰면 안 된다.
경로 정답이 부족하다는 이유로 후보 단위 비교까지 무조건 막는 것도 아니다.

A/f1485 idx19의 과거 판정은 이력으로 남지만 현재 물리적 대안에서는 제외된다.
B/idx8은 실용적 근사로 허용되었을 뿐 새 물리적 양성이 아니다.
거부 대상 3개는 “Oil target 아님”의 대조군이지 확정 “물리적 경계 아님” 라벨이 아니다.

### Foam: 기존 범위는 네 경로 중 하나를 자동 선택하지 않는다

고정 중심열 X578에서 기존 Foam upper 범위와 양립하는 경로는 다음과 같다.

| Fragment | Source Y | 완전한 7×7 상/하 patch |
|---|---:|---:|
| 963 | 332 | 16 / 16 |
| 995 | 336 | 13 / 13 |
| 1029 | 336 | 2 / 2 |
| 1031 | 336 | 2 / 2 |

두 edge row에서 네 fragment가 나온다. 짧은 branch를 임의 삭제하지 않았고 patch 수도 학습 가중치로 쓰지 않았다.
하부 Oil 범위의 1463/Y428, 1523/Y431, 1546/Y433은 보존 대조군이며 외부 표면 분류기의 음성이 아니다.
실제 native successor를 채택한다면 양성 상단 보존과 독립 반대 사례를 평가할 역할 대응을 구체화해야 한다.
이미 답변받은 N1–N5, 상단/하단 범위 질문을 다시 시작하거나 새 영상 확보를 선행조건으로 만들지 않는다.

## 인수인계 파일 위치

저장소 내 상세 기록:
`docs/60-evidence/s11/2026-10-13-existing-material-execution.md`

저장소 내 전체 결과:
`docs/50-diagnostics/s11/2026-10-13-existing-material-execution/`

이 폴더에는 `manifest.json`, **전체 `readout.json`**, `verification.json`,
`closeout-checks.json`, **`public-native-subject-review.png`**, `render_subject_packet.py`가 있다.

전체 readout SHA-256:
`e1052b1e5bbc7ccc40d71b445157c7f448b83e43d30ab4958261644812d2bb08`

검토 이미지 SHA-256:
`f0191b97ba7235f0022b59272863b5b73336ab82dd8cbb419464dab145e61814`

현재 Work Plan의 이전 “재사용 명세 미작성” checkpoint를 실제 실행 완료 상태로 갱신했다.
O2/V5·생산 소비자 승인·field 판정은 변경하지 않았다.

## 이 다운로드 패키지의 범위

`s11-material-reuse.patch`는 Work Plan 수정과 새 코드·테스트·명세/검증 JSON을 포함한다.
`repo-files/`는 새 텍스트 파일의 개별 사본이며, `RESULT_INDEX.json`은 원본 결과의 경로·hash·모집단·주요 대조군을 담는다.

**전체 164개-record readout과 검토 PNG는 로컬 저장소에 보존했고 이 휴대용 패키지에는 중복 포함하지 않았다.**
원본 영상, 기존 A1/O1 capture, reference bank, 모델/환경 파일도 포함하지 않는다.
패키지만 있는 새 clone에서 전체 자료 실행이 가능하다고 가정하면 안 된다.
필요한 원본이 없으면 기존 pin 검사를 우회하지 말고 현재 증거가 있는 Mac 작업 환경에서 재현한다.

원래 Mac 작업 트리에는 이미 변경이 있으므로 패치를 중복 적용하지 않는다.
다른 깨끗한 기준 작업 트리에서는 다음으로 적용 가능 여부를 먼저 확인한다.

```bash
git apply --check /path/to/s11-material-reuse.patch
git apply /path/to/s11-material-reuse.patch
```

패치와 `repo-files/`를 동시에 덮어쓰는 방식으로 적용하지 않는다.
전체 증거 파일과 영상은 패치에 포함되지 않는다.

## 재현 명령

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_existing_material_reuse.py \
  tests/unit/test_s11_native_role_preflight.py \
  tests/unit/test_s11_native_role_qualification.py \
  tests/unit/test_s11_contextual_role_preflight.py \
  tests/unit/test_s11_native_surface_trial.py

.venv/bin/python scripts/check_detector_governance.py --base-ref 463ea1b --include-worktree
.venv/bin/python scripts/experiment_artifacts.py check
git diff --check
```

자료 실행은 실제 `verification.json/cli_command`를 참고하되 **종료된 run의 work 경로를 재사용하지 않는다.**
새 managed run을 시작해 그 `work/`에 출력하거나 자동 폐기되는 TemporaryDirectory를 쓴다.

```bash
.venv/bin/python tests/diagnostics/s11_existing_material_reuse.py \
  --root /Users/sunjaekim/Developer/oil_level_tracker \
  --manifest docs/50-diagnostics/s11/2026-10-13-existing-material-execution/manifest.json \
  --output <new-managed-run>/work/readout.json
```

실행기는 기존 출력 덮어쓰기를 거부한다. 기존 sample/output의 A1/O1 capture와 pinned 입력들이 필요하다.
새 연구 실험을 수행한다면 기존 artifact lifecycle의 start/finish/retention 절차를 따른다.

## 하지 않은 것과 남은 승인

이번에는 새 학습, 실제 데이터에 대한 새 모델 추론, detector 전체 replay,
생산 선택/추적 코드 변경, Windows 실행, 독립 사용자의 report 판독을 하지 않았다.
기존 N3 상단을 잃은 native trial은 CLOSED_WITHOUT_PROMOTION 그대로다.
O2/V5 이전에 새 역할 관측을 생산 consumer에 연결하지 않는다.

다음 목적은 잘못된 Oil/Foam 움직임을 줄이면서 실제 움직임을 보존하는 관측과 선택의 검증이다.
검출 개수 증가, 모든 거절 또는 이 테스트 통과 자체를 report 맥락 개선으로 보고하지 않는다.
