# S11 review handoff — 2026-10-13

## 먼저 읽을 파일

**`S11-program-review-and-work-spec-2026-10-13.md`**가 본 검토와 후속 작업 명세서다. 현재 기준은 `badf7caddebc7e75013ef02c888d2b72f13feb92`다.

`S11-evidence-audit-2026-10-13.json`에는 실제 repo 조회에서 반환된 수치, source SHA-256 18개, 저장 CSV/영상 hash, 새 native feature canary 결과, 실행·미실행 구분이 있다. 이는 repo 조회 결과를 이 검토 패키지에 구조화한 기록이며, 새로운 전체 application replay 결과가 아니다.

`reproduce_native_feature_canary.py`는 같은 핵심 canary 계산을 재현하기 위한 standalone CLI다. 핵심 연산은 Mac에서 실제 실행했다. 배포한 CLI wrapper는 추가적인 pin/path/output guard를 포함하며, 패키지 마감 시 syntax와 `--help`를 검사했다. 이 wrapper의 전체 CLI를 Mac에서 다시 실행한 것으로 주장하지 않는다.

## 중요한 결론

현재 S11은 ACTIVE, O2 OPEN, FIELD FAIL, Local XY OFF다. 전체 detector 재작성 대신 native 경로에 결속된 역할 관측과 Foam raw front 축약을 제한적으로 재설계한다. 새 역할 head의 학습은 **별도 제안**이며, 기존 고정 encoder 실험으로 이미 승인되었다고 간주하지 않는다.

Work Plan과 기존 설계·검증 owner가 정본이다. 이 패키지는 외부 검토/제안이며 그것들을 자동 수정하지 않았다. 채택 시 delta만 기존 owner에 반영하고 새 Work Plan을 병렬 운영하지 않는다.

## canary 재현

현재 로컬 checkout과 보존된 ignored image inputs가 필요하다. 새 clone만으로 모든 입력이 확보된다고 가정하지 않는다. 고정된 source와 원본 image pin이 변했거나 기준 HEAD가 다르면 script는 종료한다.

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python \
  /absolute/path/to/reproduce_native_feature_canary.py \
  --repo /Users/sunjaekim/Developer/oil_level_tracker
```

기본 출력은 stdout이다. 저장이 필요하면 현재 저장소의 artifact lifecycle에 맞춰 새 실험을 준비하고, 그 새 output 경로를 `--output`으로 지정한다. 기존 파일을 덮어쓰지 않는다. encoder, training, video decode, full detector replay는 호출하지 않는다. 생산 source·원본 입력도 변경하지 않는다.

`DetectorSettings()` 기본값으로 기존 `_texture_evidence`의 의존성을 보는 진단이다. 실제 저장 Recipe의 full-feature replay, 물리 역할 판정 또는 detector 개선 시험이 아니다. 마스크 밖 0/255 변경은 합성 대조이고 원본 배열은 보존한다.

## 이번 확인한 실행 결과

142개 material input/source pin 일치, 저장 기본 실행과 생산 source 221개 일치, 기존 focused test 9개 통과, 관리 run 14개 오류 없음. 전체 회귀·Windows·독립 report 판독·새 encoder inference·학습은 수행하지 않았다. 이 패키지 작성으로 생산 코드나 gate 상태를 바꾸지 않았다.

`VERIFICATION.json`은 패키지 자체의 JSON/문서/코드 syntax 검사이며, 위 detector 시험과 혼동하지 않는다. `SHA256SUMS`는 패키지 파일 무결성 확인용이다.
