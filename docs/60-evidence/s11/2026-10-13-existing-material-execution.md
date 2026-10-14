# S11 실제 실행 결과와 인수인계 — 2026-10-13

**기준:** `463ea1bb5aa2fb945a7f1871f0aa35f4940c8767`.
**작업 branch:** `work/s11-material-reuse-20261013`.
**판정:** `REUSE_EXECUTED_NO_DETECTOR_PROMOTION`.
아래 원 실행은 깨끗한 작업 트리에서 시작했고, 10월 13일 인계 당시에는 로컬 미커밋 상태였다.
원문은 `d85a4c8fb8a10e62611592e531dee3f3f152fa17`에 보존했다.
후속 인수·검증·정리는 [10월 14일 보충](#receiving-integration-2026-10-14)을 따른다.
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

<a id="receiving-integration-2026-10-14"></a>

## 2026-10-14 첨부 인수·타당성 검토·통합

인수 기준도 `463ea1bb5aa2fb945a7f1871f0aa35f4940c8767`이었다.
첨부의 [원본 handoff](../../70-reference/s11-actual-execution-2026-10-13/S11_HANDOFF.md)와
[휴대용 결과 색인](../../70-reference/s11-actual-execution-2026-10-13/RESULT_INDEX.json)은
`70-reference`에 원문 그대로 보존했다. 이들은 당시의 미커밋 상태를 기록한 출처이며
현재 실행 지시나 결과 owner가 아니다. [인수 manifest](../../70-reference/s11-actual-execution-2026-10-13/import-manifest.json)는
ZIP의 13개 member와 실제 배치·hash·검증·중복 정리를 연결한다.

### 배치와 중복 판단

- `repo-files/`의 7개 파일은 현재 작업 트리와 모두 byte-identical이었다.
  실제 구현은 `tests/diagnostics`, 회귀 검증은 `tests/unit`, 전체 결과·검토 PNG는
  기존 `50-diagnostics`, 실행 설명은 이 문서에 유지했다. 패치를 다시 적용하지 않았다.
- ZIP의 `VERIFICATION.json`/`CLOSEOUT_CHECKS.json`은 기존 파일을 참조한다.
  패치 57,485 bytes는 `463ea1b` → `d85a4c8`의 파일별 Git diff를 원래 순서로
  결합하면 동일하다. `SHA256SUMS.txt`도 manifest의 member hash로 동일하게 복원된다.
  중복 patch·checksum 파일·압축 해제 트리·ZIP을 저장소에 추가하지 않았다.
- ZIP에서 제외된 `readout.json` 284,322 bytes와 PNG 157,674 bytes는 로컬에
  있었고, 첨부 색인의 hash와 일치했다. 코드·문서와 함께 원본 snapshot에 등록했다.
- 등록 Git worktree는 현재 한 개, 앱 attachment는 0개였다. Developer, Codex
  managed worktree와 `/private/tmp`의 제한된 Git entry 조사에서도 추가 Oil checkout은
  없었다. 다른 프로젝트의 `may_web`는 유지했다. 원격 fetch 후 main은 인수 기준과
  같았으며, `c4814bd`/`e5d4a04`의 미승격 실험 분기도 이전 검토와 같아 병합하지 않았다.
  이번 실행만 `d85a4c8`/`62cfe46`으로 보존·검토한 뒤 main에 fast-forward 통합했다.
  병합된 `work/s11-material-reuse-20261013` 로컬 branch는 제거했다.
- 13개 member 모두를 저장 파일/Git snapshot/명시한 재생성 방식으로 복원해 hash를
  확인한 뒤 전달 ZIP을 제거했다. 압축 컨테이너 bytes 재생성은 보장하지 않는다.
  이전 direction 인수의 `/private/tmp` 압축 해제 원본 11개도 이미 등록된 원본과
  byte 비교 후 제거했다. 비교되지 않은 고유 scratch, 원본 영상·capture와
  기존 모델 환경은 유지했다. 새 CLI/PNG 사본 두 개는 관리 절차로 폐기했다.

### 받는 쪽에서 다시 확인한 결과

| 검사 | 2026-10-14 결과 |
|---|---|
| 관련 테스트 5개 모듈 | **116 passed in 1.92 s**, skip 없음 |
| 실제 CLI, `/private/tmp` cwd | **0.9586 s**, process-lifetime peak RSS 203,915,264 bytes |
| 전체 결과 비교 | 기존 JSON 284,322 bytes와 완전 일치 |
| 현재 renderer 재실행 | PNG 157,674 bytes 완전 일치; RGB ROI와 경로 hash 재검증 |
| PNG 시각 점검 | 일곱 경로·좌표·UNREVIEWED·하부 보존 대조군 표시 확인; 새 물리 판정 없음 |
| 새 관리 실행 종료 | 재생성 사본 2개/441,996 bytes 폐기, 기존 결과만 reuse; 전체 **25개 / 오류 0** |
| 문서·보존 검사 | 변경 Markdown 8개, local 링크 1,266개, 기존 Work Plan 앵커 17개, 신규 문서/산출물 색인 10개, ZIP member 복원 13개 통과 |
| 생산 범위 | `src`, `pyproject.toml`, 기존 Recipe, frozen trial·truth 변경 없음 |

시간은 저장 입력 연결 도구의 이번 실행값이며 이전 5.6723 s를 정정하거나 detector
성능으로 비교하는 수치가 아니다. 원 실행의 검증 JSON은 재작성하지 않았다.
새 clone에는 ignored 영상·capture가 없으므로 실제 자료 재현에 현재 Mac 입력이
필요하다는 제한도 그대로다. 이번 인수에서는 학습·encoder 추론·영상 decode·전체
detector replay·Windows·독립 report 판독을 수행하지 않았다.

### 명세 타당성과 보완

**증거 연결 구현과 재사용 명세로는 타당하다. 다음 detector 관측의 실행 명세는 아직 아니다.**
기존 CR1/G0/qualifier/geometry 책임을 조합하며 생산 진입 경로를 추가하지 않았다.
이 모듈의 `main → audit`와 renderer의 실제 경로를 확인했고, pin·지원·좌표·판정
분리를 기존 결과 및 회귀 검증과 대조했다. 새로운 범용 binding/edge/학습 구현은 필요하지 않다.

후속 계획에서 특히 다음을 보완한다.

1. **촬영원 수와 Oil 평가 단위는 다르다.** 사용 가능한 Oil 대조군 9개는 모두
   sample4의 6개 frame에 속한다. 양성 6개 중 f1275/idx12는 기존 초기 참조이므로
   nonself 양성은 5개다. 9개 원본·43개 context·패치 수를 독립 라벨 수나 다른
   촬영원 성능으로 세지 않는다. 현재로서는 후보 단위 개발 비교만 가능하다.
2. **authority와 물리적 정답·최종 선택은 다르다.** 저장 대조군의 양성 6개는
   anchor 1 / continuation 2 / candidate-only 3, 거부 대상 3개는 anchor 2 /
   continuation 1이다. 이는 admission 단계의 비교 근거이며 최종 detector 혼동행렬이
   아니다. 기존 authority, peer-support 또는 CR1 category를 다시 이름만 바꾸어
   정답 관측으로 채택할 수 없다. 153개 미평가 후보와 A/B의 2개 비정답 상태도 유지한다.
3. **native 학습의 평가 계약은 미완성이다.** 미소냉동의 일곱 fragment는 모두
   미확정이며, 외부 upper 보존과 내부/구조 반대 사례의 source-separated 평가가
   아직 결속되지 않았다. sample4/water를 fit에 넣는 안은 N3의 기존 transfer 실패를
   개발 노출로 전환할 뿐, 새 독립 검증을 만들어 주지 않는다.
4. **비교 전 관측 계약을 먼저 확정한다.** 새 정보가 어느 기존 실패를 어떻게
   구분하는지, 실제 입력과 전체 dependency, 원래 판정 단위, source/episode 노출,
   하나의 고정 비교·ablation·자원/중단 기준을 기존 설계·검증 owner에 명시해야 한다.
   새 threshold·seed·crop 탐색이나 미확정 경로의 의사정답화는 후속 계획이 아니다.

현재 다음 작업과 순서는 [Work Plan의 후보 관측 준비 계획](../../00-project/work-plan.md#candidate-observation-follow-up)에
한 번만 기록한다. 이 검토로 O2/V5, 별도 behavior 수용, 독립 Foam raw/episode 조건이나
FIELD FAIL을 변경하지 않는다.

## Public native review preparation — 2026-10-14

BASE/Accum의 [기존 차단 지점](2026-10-14-overlay-support-guard.md#existing-bundle-analysis-reuse--planning-correction)은
재사용한다. 새로운 역할 관측이 실제 경계와 구조/내부 변화를 구분해야 하며,
admission flag 자체를 정답으로 쓰지 않는다. sample3 C의 원래 답변은 표시 부근의
구조물 역할이며 전체 후보/경로 정답은 아니다. 이 범위를 넓히거나 C/D·A/B를 다시
질문하지 않는다. 기존 RGB/native 학습은 종료 상태를 유지한다.

다음 준비는 이미 저장된 미소냉동 f1499의 상단 경로 네 개(963/995/1029/1031)를
원래 G0와 같은 source/frame/path hash로 묶는 것이다. 같은 Y336에 경로 세 개가
있어 한 행이나 하나의 긴 경로로 합치지 않는다. 기존 PNG를 그대로 참조하며
하부 Oil 세 경로는 이번 질문에서 제외하고 보존 대조로 남긴다. 원본 영상이나
검토 이미지를 복제하지 않는다. scratch 2 MB / 최종 추가 자료 100 KB 범위다.

기존 native qualifier를 확장해 역할 확정·애매함·판독 불가를 구분하고, 답변 전
proposal 검사에서는 모든 경로를 미판정으로 유지한다. 실제 실행은 저장 raster의
좌표·가시성·RGB와 검토 이미지 출처를 확인하는 범위다. Recipe 변경, detector
재실행, 새 학습·추론 또는 Windows 자료 재분석을 포함하지 않는다. 역할 대응이
필요한 새 경로만 사용자에게 확인하며 기존 상단 Foam/하단 Oil 구간 판정은 닫힌
채 유지한다.

[준비 계획](../../50-diagnostics/s11/2026-10-14-native-role-review/plan.json),
[질문 대상](../../50-diagnostics/s11/2026-10-14-native-role-review/proposal.json),
[실제 검사](../../50-diagnostics/s11/2026-10-14-native-role-review/inspection.json),
[검증 기록](../../50-diagnostics/s11/2026-10-14-native-role-review/verification.json)을 저장했다.
기존 qualifier의 `--prepare-plan`이 구간 안의 모든 경로를 보존하고,
`--inspect-proposal`이 인간 답변 없이 원본 결합을 검사한다. 답변 v3는 확정 역할만
capability target을 가지며 애매함/판독 불가는 null과 별도 개수로 보존한다.
같은 원본·프레임·경로를 다른 ID로 중복 집계하거나, 다른 검토 이미지를 연결하는
입력은 거부한다. 기존 v1/v2 출력은 바꾸지 않는다.

| 검증 | 결과 |
|---|---|
| 관련 unit/CLI 테스트 | **149 passed in 2.27 s** |
| 실제 CLI | `/private/tmp`에서 절대 경로로 준비 → 검사 완료 |
| 기존 N1–N5 | 원래 qualifier 실행 결과와 저장 결과 5개 모두 논리적으로 동일 |
| 이번 판정 상태 | 4개 모두 `PENDING_REVIEW`; 새 물리 판정·학습 라벨 0 |
| 경로/노출 | 원래 27개 참조 유지; 하부 Oil 3개 미판정 보존; 상단 네 경로의 같은-frame 쌍 6개 모두 독립 split 불허 |
| 준비·검사·기존 결과 대조 | 0.610 s; detector 처리시간 측정이 아님 |
| 보존·정리 | JSON 4개 30,530 bytes; 기존 PNG 재사용, 임시 JSON 중복 3개 제거 |

관리 실행 `s11-native-role-review-20261014-001` 종료 후 총 38개 실행 오류 0이다.
실행 당시 Git base는 `45c12e9`이며 변경된 qualifier의 실제 source SHA-256은
검증 기록과 관리 표식에 남겼다. 새 역할 답변은 아직 수신하지 않았다. 이후
관측/학습의 선택과 데이터 분리는 별도 계약이며, 이번 준비는 이전 head의 재학습이나
BASE·Accum 검출 개선을 입증하지 않는다.

## Public native Foam-upper reply — 2026-10-14

사용자 답변 **“Foam 상단”**은 바로 앞 질문에 포함한 963/995/1029/1031 네 경로
각각에 `EXTERNAL_FOAM_UPPER`로 연결한다. [원문 답변](../../50-diagnostics/s11/2026-10-14-native-role-review/reply.json)은
기존 proposal/display/subject hash를 참조한다. 판정 범위는 표시한 native 경로의
역할이며 주변 픽셀의 물질, 다른 프레임, 정밀 좌표 또는 하부 Oil 경로로 넓히지 않는다.

실행 범위는 기존 qualifier의 실제 CLI와 이전 N1–N5 결과 대조, 촬영원별 역할
대조군 집계다. 원래 43 context / 1,335 edge / 164 Oil 기록은 수정하지 않는다.
네 경로는 같은 프레임의 겹치는 지원을 사용하므로 독립 split이나 네 촬영원으로
계산하지 않는다. 예산은 scratch 2 MB / 최종 추가 자료 100 KB이며 모델 학습·추론,
영상 재분석, Windows 실행은 포함하지 않는다.

[실제 qualification](../../50-diagnostics/s11/2026-10-14-native-role-review/qualification.json)은
네 역할을 원본 경로에 연결했고 기존 N1–N5 재실행 결과도 저장 결과와 동일했다.
[촬영원별 준비 상태](../../50-diagnostics/s11/2026-10-14-native-role-review/source-readiness.json)는
9개 native 경로 / 3개 촬영원 / 4개 source-frame을 집계한다. 기존 Oil 후보 대조군
9개와는 다른 판정 단위다.

| 촬영원 | 외부 상단 경로 | Foam 내부 변화 | 구조물 경계 |
|---|---:|---:|---:|
| sample5 / 물 | 1 | 1 | 0 |
| sample4 | 1 | 1 | 1 |
| 미소냉동 공개 영상 | 4 | 0 | 0 |

공개 영상의 양성 보존 검사는 이제 가능하지만 내부 변화/구조물과의 구분은 아직
그 촬영원에서 평가할 수 없다. 네 경로의 같은-frame 쌍 6개 모두 독립 split 불허다.
하부 Oil 1463/1523/1546은 미판정 보존 대조로 남는다. 관리 실행
`s11-native-role-reply-20261014-001`은 새 JSON 3개 23,627 bytes를 정본에 남기고
중복 작업 파일 2개를 제거했다. qualifier source는 `2ed5617`의 bytes로 기록했으며
모델 호출과 새 학습은 0이다.

### Public lower native row: a new scoped question

공개 영상의 추가 역할 대조를 위해 저장된 **Y442의 모든 경로
1769/1788/1789**를 새 질문으로 준비한다. 원본 화면상 하단 유리 테두리 부근에
있는 경로이며 구조물인지 여부 자체가 미확정이다. 기존 Oil 보존 경로의 Y428/431/433,
방금 확인한 Foam 상단 Y332/336과 다르다. 위치·길이·모델 점수를 정답으로 쓰지
않고 같은 행의 짧은 갈래도 모두 포함한다. Y263의 상단 테두리 및 Y454의 하단
경로는 한쪽 지원이 없으므로 이번 양면 관측 대조용으로 선택하지 않는다.

기존 `prepare_proposal`에 정답 없는 행 선택을 추가하고, 기존 원본 경로 renderer의
행 선택을 재사용한다. 새로운 detector나 병렬 검토 구현을 만들지 않는다.
원래 RGB 배열 동일성·경로 hash·상하 지원을 검사하며, 답변 전에는 세 경로 모두
`PENDING_REVIEW`다. 학습/추론/영상 decode는 하지 않는다. scratch 2 MB / 최종 추가
자료 400 KB 안에서 질문 PNG 하나와 필요한 결합 JSON만 보존한다.

[행 선택 계획](../../50-diagnostics/s11/2026-10-14-native-role-review/opposition-plan.json),
[질문 대상](../../50-diagnostics/s11/2026-10-14-native-role-review/opposition-proposal.json),
[검토 그림](../../50-diagnostics/s11/2026-10-14-native-role-review/opposition-review.png),
[실제 검사](../../50-diagnostics/s11/2026-10-14-native-role-review/opposition-inspection.json),
[검증 기록](../../50-diagnostics/s11/2026-10-14-native-role-review/opposition-verification.json)을 남겼다.
원본 ROI와 저장 RGB가 같고, 표시한 세 경로 hash가 원래 G0와 일치한다.
상하 complete patch 수는 각각 **2/2, 6/6, 2/2**이며 같은-frame 쌍 3개 모두
독립 split 불허다. 역할은 세 개 모두 미판정이고 새 target은 0이다.

실제 renderer → 준비 → 검사 CLI를 `/private/tmp`에서 실행했다. 확장 후에도
기존 상단 proposal과 N1–N5 + 공개 상단 네 역할의 qualification 결과가 동일하며,
기존 일곱 경로 PNG 재생성 bytes도 정본과 동일했다. 관련 테스트는
**156 passed in 2.66 s**다. 관리 실행 `s11-public-native-opposition-20261014-001`은
최종 5개 파일 146,822 bytes만 남기고 작업 중복 6개를 제거했다.
추가 검토는 이 세 경로의 실제 역할에 대한 사용자 판단에서 멈춘다.
이는 새로운 source-transfer 성능, BASE/Accum 검출률 또는 생산 Foam 개선 결과가 아니다.

### Public lower rim reply — 2026-10-14

사용자 답변 **“구조물(유리 rim)”**을 하단 1769/1788/1789 세 경로 각각에
`STRUCTURE_BOUNDARY`와 확인된 rim 문맥으로 연결한다. [원문](../../50-diagnostics/s11/2026-10-14-native-role-review/opposition-reply.json)은
기존 proposal/display/subject hash를 고정한다. 실제 경로의 역할만 확정하며
주변 재질·다른 경로·프레임·dense mask로 전파하지 않는다.

기존 qualifier의 실제 CLI를 `/private/tmp`에서 실행하고 이전 9개 판정과
촬영원별 양성/내부/구조 대조를 검증한다. 원래 G0/CR1 결과와 기존 그림은
참조로 재사용한다. scratch 2 MB / 최종 추가 자료 100 KB이며 모델 호출,
학습, 영상 decode 또는 생산 동작 변경은 이 답변 결합에 포함하지 않는다.

[실제 qualification](../../50-diagnostics/s11/2026-10-14-native-role-review/opposition-qualification.json)과
[갱신된 source 집계](../../50-diagnostics/s11/2026-10-14-native-role-review/qualified-source-readiness.json)는
12개 경로 / 3개 촬영원 / 4개 source-frame을 확인했다. 외부 상단 6개,
내부 변화 2개, 구조물 4개다. 기존 9개 판정은 원래 결과와 동일하다.
같은-frame dependency 쌍 23개는 모두 독립 split 불허이며, 공개 영상의 27개
경로 중 7개만 판정됐고 20개는 미판정이다. 하부 Oil 1463/1523/1546도 포함한다.
공개 영상의 외부 상단 대 rim 비교가 이제 가능하지만 내부 Foam 판정이나
독립 holdout, Oil 재질 학습, 생산 관측 수용으로 확대하지 않는다.

관리 실행 `s11-public-rim-reply-20261014-001`은 정본 JSON 3개 22,454 bytes를
남기고 중복 2개를 제거했다. 다음 별도 연산은 [역할 순서 비교 계약](2026-10-14-native-role-order.md)이
기록하며 원래 실패한 native 분류 시험은 닫힌 상태로 보존한다.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `FOAM-CANDIDATE`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: no new production failure stage is established. The changed responsibility is exact evidence binding; historical, current physical and practical claims must not be conflated. Candidate-role versus native-path support insufficiency is measured, not a causal detector repair.
- Existing feature coverage: sample4 Recipe has zero exclusions/templates; Local XY OFF. Completed D2/Local XY failures are reused without re-execution. This saved-input supplement bypasses run preparation, static learning, current-frame detection, sequence and report, so it cannot establish their efficacy.
- Execution scope: the new offline CLI executed over pinned G0/CR1/A1 files and qualified replies, including source hashes, subject identities and saved masks/edges. The original-pixel review renderer reconstructed no new edge and assigned no role. No video decode, trained-media model inference/fitting, production consumer, Windows field execution or independent report reading ran in this study.
- Logic-map impact: NONE — production setup, admission, sequence and publication owners are unchanged; the new module composes existing diagnostic owners. Renderer changes only evidence display.
- Failure-registry impact: NONE — exact provenance and no source-specific promotion guards are reused; no mechanism is promoted or failure class retired.
