# S11 실제 실행 결과와 인수인계 — 2026-10-13

**기준:** `463ea1bb5aa2fb945a7f1871f0aa35f4940c8767`.
**작업 branch:** `work/s11-material-reuse-20261013`.
**판정:** `REUSE_EXECUTED_NO_DETECTOR_PROMOTION`.
시작 시 작업 트리는 깨끗했다. 이 기록의 변경은 로컬 미커밋 상태이며 commit/push/merge하지 않았다.
현재 단계와 승인 상태는 [Work Plan](../../00-project/work-plan.md)이 소유한다.

## 완료한 실제 작업

이전 설계의 기존 자료 재사용 단계를 실행 가능한 코드로 구현하고 실제 자료로 실행했다.
[실행기](../../../tests/diagnostics/s11_existing_material_reuse.py)는 기존 CR1 audit,
판정 정정 qualifier, G0 Oil bindings, native-role qualifier를 조합한다.
기존 도구나 frozen 결과를 새 구현으로 교체하지 않았다.

- 전체 164개 기록을 유지하면서 A1/O1 후보 지원 160개를 exact subject hash와 index/source/Y로 연결했다.
- 원래 10개 후보 판정을 최신 A/B 정정과 결합했다. 현재 후보 대응 6개, 거부 대상 3개, 별도 실용적 근사 B 1개를 구분한다.
- 9개 원본 hash와 source별 제안 용도를 확인하고 43개 context의 파생 view를 같은 source에 묶었다.
- 기존 N1–N5 판정 5개를 원래 qualifier로 재실행하여 저장 결과와 동일함을 확인했다.
- 미소냉동의 중심열 전체 27개 native fragment를 재구성했다. 판정 범위와 양립하는 7개는 원본 픽셀 위에 표시했다.

[Manifest](../../50-diagnostics/s11/2026-10-13-existing-material-execution/manifest.json),
[전체 실행 결과](../../50-diagnostics/s11/2026-10-13-existing-material-execution/readout.json),
[검증 기록](../../50-diagnostics/s11/2026-10-13-existing-material-execution/verification.json),
[경로 검토 이미지](../../50-diagnostics/s11/2026-10-13-existing-material-execution/public-native-subject-review.png)가 실제 산출물이다.
원본 영상과 기존 capture/reference bank는 복제하지 않았다.

## 검증 결과

| 항목 | 실제 결과 |
|---|---|
| 새 검증 테스트 | 25개; 정정 판정·중복 후보·같은 Y의 다른 후보·source 분리·hash/좌표·덮어쓰기 방어 |
| 관련 테스트 묶음 | **116 passed in 10.44 s** |
| 실제 CLI 재실행 | `/private/tmp`에서 절대 경로로 실행, **5.6723 s** |
| 메모리 | CLI process-lifetime peak RSS **203,931,648 bytes**; detector/Windows 성능 측정이 아님 |
| 결과 동일성 | 첫 실행과 최종 source 실행의 JSON **284,322 bytes 전체 일치** |
| 입력 범위 | 9 source / 43 context / 31 source-frame / 기존 1,335 edge row |
| 원본·표시 검증 | 검토 이미지의 원본 ROI가 저장된 RGB와 배열 동일; 표시 경로 hash 확인 |
| 생산 경로 | `src`, `pyproject.toml`, 기존 Recipe의 HEAD 대비 diff 없음 |

첫 실행 후 같은 후보를 다른 query ID로 중복 집계하는 입력을 거부하도록 보강했다.
두 번째 실행은 이 최종 실행기로 재현했다. 이미지 초안의 긴 설명이 겹쳐 보인 부분은
문구만 줄여 다시 렌더링했으며 경로·원본 픽셀·판정은 바꾸지 않았다.
이러한 내부 수정은 새 detector 가설이나 모델 trial이 아니다.

## 구현으로 확인한 중요한 제약

### 1. Oil 후보 정답과 native path 정답은 다르다

현재 후보 단위 대조군 9개 중 `native_generator_path`가 3개,
`no_captured_native_path`가 6개다. 양성 6개 중 4개는 경로가 저장되어 있지 않다.
경로가 있는 경우도 G0의 표현은 `POOLED_SECTOR_SAMPLES`이며, 해당 전체 픽셀
윤곽의 역할이 확인되었다는 의미가 아니다.
따라서 6개 양성과 3개 거부 대상을 **후보 단위 관측 비교**에 쓰는 것은 가능하지만,
Y에서 수평선을 만들어 native-fragment 학습 정답으로 바꾸면 안 된다.
새 도구는 후보 비교 준비와 native-path/pure-side 라벨 준비를 서로 다른 상태로 반환한다.

A/f1485 idx19는 과거 라벨을 보존하되 현재 물리적 대안 주장에서는 제외했다.
B/idx8은 사용자가 허용한 근사 위치로 유지하되 새 물리적 양성으로 쓰지 않는다.
거부 대상 3개 역시 `OPPOSED_OIL_TARGET`일 뿐 확정 `NON_INTERFACE` 라벨이 아니다.
전체 164개에서 이 범위로 미평가인 153개를 음성으로 바꾸지 않았다.

### 2. 공개 영상에 새로 필요한 것은 영상 자체가 아니라 구체적 대응이다

미소냉동 f1499의 같은-frame 고정 중심열 X578을 사용했다.
전체 중심열 27개 fragment를 유지했으며 아래는 기존 판정 범위와 양립하는 부분집합이다.
범위 내부의 모든 경로를 정답으로 간주하거나 길이가 긴 경로를 선택하지 않았다.

| 기존 범위 | fragment | 중심열 source Y | 완전한 7×7 상/하 patch 수 |
|---|---:|---:|---:|
| Foam upper | 963 | 332 | 16 / 16 |
| Foam upper | 995 | 336 | 13 / 13 |
| Foam upper | 1029 | 336 | 2 / 2 |
| Foam upper | 1031 | 336 | 2 / 2 |
| Oil upper | 1463 | 428 | 10 / 10 |
| Oil upper | 1523 | 431 | 경로 방향 미확정 |
| Oil upper | 1546 | 433 | 경로 방향 미확정 |

이 7개는 모두 **UNREVIEWED**다. patch 수는 독립 표본 수나 모델 가중치가 아니다.
Foam 범위의 두 edge row에서 4개 fragment가 나오므로 row와 path를 혼동하지 않는다.
하부 Oil 범위의 경로는 보존 대조군이지, 외부 표면 classifier의 음성 정답이 아니다.
검토 이미지는 새로운 사용자 질문을 자동 발행하거나 정답을 생성하지 않는다.
현재 있는 원본·판정을 다시 전달해 달라고 요청하지 않는다.

## 다음 작업자 인수인계

이전 전체 설계의 WP02/03 기존 자료 역할·지원·source 분리 단계를 **실행 완료**했다.
WP04의 실제 역할 관측, O2 승인, Windows V5 shadow, WP05/06 소비자 변경,
WP07 raw Foam upper 회복, WP09 실제 report 판독을 완료한 것은 아니다.
이 결과는 검출률 개선 또는 허위 42/44초 report 극값 제거의 증거가 아니다.

후속 Oil 비교는 `oil_units[*].candidate_role_comparison_ready`의 9개를 원래 후보
정밀도로 사용하고, 전체 164개/미평가/경로 부재를 계속 보존해야 한다.
선정할 관측은 기존 실패 기법과의 차이·전체 feature dependency·source별 평가를 먼저
명시해야 한다. native 경로를 필수로 하는 관측에 이 후보 라벨을 자동 전용하지 않는다.
실제 기준은 잘못된 움직임 억제와 실제 움직임 보존이며, 모든 출력 거절은 통과가 아니다.

후속 native Foam 시험을 선택할 경우에는 이 실행의 `native_review_packets`에서
정확한 경로/지원/정밀도를 이어받는다. source별 분리는 sample4/water 개발,
미소냉동 fit 제외 exposed 평가의 **제안**이며 학습 명령이 아니다.
실제 외부 upper 보존과 독립 반대 사례를 모두 평가할 역할 대응이 부족한 상태다.
필요한 대응만 구체적으로 확인해야 하며 기존 N1–N5·상단/하단 구간 질문은 반복하지 않는다.
기존 실패 head의 seed/crop/threshold 변경이나 재학습은 이 결과에서 자동으로 이어지지 않는다.

생산 consumer는 O2/V5 및 별도 behavior 수용 이전에 연결하지 않는다.
Foam episode 수정은 실제로 올바른 raw upper가 downstream에서 사라진 증거가 있을 때 연다.
Windows 영상 반출이나 신규 영상 확보를 선행조건으로 만들지 않는다.

### 재현과 파일 상태

새 코드는 `tests/diagnostics/s11_existing_material_reuse.py`, 새 테스트는
`tests/unit/test_s11_existing_material_reuse.py`다. 그림 생성기는 같은 진단 폴더의
`render_subject_packet.py`이며 기존 frozen N1–N5 renderer는 수정하지 않았다.

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_existing_material_reuse.py \
  tests/unit/test_s11_native_role_preflight.py \
  tests/unit/test_s11_native_role_qualification.py \
  tests/unit/test_s11_contextual_role_preflight.py \
  tests/unit/test_s11_native_surface_trial.py
.venv/bin/python scripts/check_detector_governance.py --base-ref 463ea1b --include-worktree
```

실제 실행 명령은 `verification.json/cli_command`에 있다. 재실행 시 종료된 run의
`work/` 경로를 그대로 재사용하지 말고, artifact lifecycle에 따라 새 managed run의
`work/` 또는 자동 폐기되는 `TemporaryDirectory`로 출력한다. 실행기는 기존 파일
덮어쓰기를 거부한다. 기존 입력 중 `sample/output`의 A1/O1 capture가 필요하므로
이 파일 몇 개만 있는 새 clone에서는 전체 재현이 되지 않는다. 테스트/패치와 영상·capture
의존성을 구분해야 하며 원본 데이터가 없는 환경에서 검사 생략을 PASS로 바꾸지 않는다.

로컬 관리 실행 `s11-material-reuse-20261013-001/002`는 결과를 위 진단 폴더의
단일 사본으로 옮겨 재사용하고 종료한다. 원본 영상, 기존 bank, Torch/DINO 환경은 건드리지 않는다.
생산 source·기존 Recipe·기존 frozen trial 파일의 변경은 없으며, R22/R22-3,
Local XY OFF, O2 OPEN, FIELD FAIL을 유지한다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: no new production failure stage is established. The changed responsibility is exact evidence binding; historical, current physical and practical claims must not be conflated. Candidate-role versus native-path support insufficiency is measured, not a causal detector repair.
- Existing feature coverage: sample4 Recipe has zero exclusions/templates; Local XY OFF. Completed D2/Local XY failures are reused without re-execution. This saved-input supplement bypasses run preparation, static learning, current-frame detection, sequence and report, so it cannot establish their efficacy.
- Execution scope: the new offline CLI executed over pinned G0/CR1/A1 files and qualified replies, including source hashes, subject identities and saved masks/edges. The original-pixel review renderer reconstructed no new edge and assigned no role. No video decode, trained-media model inference/fitting, production consumer, Windows field execution or independent report reading ran in this study.
- Logic-map impact: NONE — production setup, admission, sequence and publication owners are unchanged; the new module composes existing diagnostic owners. Renderer changes only evidence display.
- Failure-registry impact: NONE — exact provenance and no source-specific promotion guards are reused; no mechanism is promoted or failure class retired.
