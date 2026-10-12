# S11 전체 검토와 detector 작업 명세 — 2026-10-12

## 먼저 읽을 파일

**`S11-program-review-and-work-spec-2026-10-12.md`**가 본문이다. 현재 상태와 실제 실행 결과, 판단 근거, 부분 재설계, WP0–WP10, 기존 계획과의 관계, Windows/report 종료 기준을 포함한다.

핵심 권고는 전체 detector 교체가 아니라 **현재 경계의 물리적 역할을 관측하는 계층의 부분 재설계**다. Oil은 anchor뿐 아니라 continuation에서 발생하는 잘못된 역할도 다뤄야 하고, Foam은 episode 완화보다 올바른 raw upper-front 관측이 먼저다. 신규 CR-1은 사전학습 시각 표현을 쓰는 제한된 실험 제안이지 구현·검증된 detector가 아니다.

| 파일 | 내용 |
|---|---|
| 본문 Markdown | 전체 검토, 설계, 작업 명세, 근거 색인 |
| `evidence/execution-receipt.json` | 실제 사용자 Mac에서 실행한 진단의 compact receipt |
| `scripts/peer_probe.py` | 실제 실행한 peer-support 재계산 script와 byte-identical |
| `evidence/focused-tests.log` | 새로 실행한 repo 관련 pytest 124개 통과 로그 |
| `story-contract.json` | A/B/C/U 및 Windows 9개 구간의 제안 체크리스트 |
| `scripts/test_story_contract.py` | 작은 오류를 전부 FAIL, 전부 unknown을 PASS로 바꾸지 않는 synthetic 계약 테스트 |
| `evidence/story-contract-tests.log` | 배포 컨테이너에서 실행한 synthetic 16개 테스트 결과 — repo 124개와 별개 |
| `scripts/check_delivery.py`, `SHA256SUMS.txt` | 배포 파일의 무결성·계수·주장 범위 확인 |

## 확인한 현재 상태

기준 HEAD는 `2c2ddd20b3dfe0eddcbc8d747b01e766522536a1`, branch는 `main`이다. 종료 시 `git status --short --branch`는 `## main...origin/main`이었다. Tracked 파일 변경·commit·push는 하지 않았다. 사용자 Mac의 ignored `sample/output/` 아래에는 이번 진단 산출물이 남아 있다.

S11 ACTIVE, O2 OPEN, FIELD FAIL은 유지한다. 이번 작업은 Oil 후보 2,618개 join과 저장 support 1,892개 재계산의 재현성, 관련 코드의 테스트 실행을 확인했다. **새 detector의 영상 정확도 개선, Windows 통과, 독립 report 이해도 통과는 확인하지 않았다.**

## 배포 묶음만으로 실행 가능한 확인

Python 3.10 이상, 표준 라이브러리만 사용한다.

```bash
python scripts/check_delivery.py
python scripts/test_story_contract.py
```

첫 명령은 파일과 실행 receipt의 무결성을, 두 번째는 이미 검토됐다고 가정한 작은 synthetic 입력의 분류 논리를 확인한다. 어느 명령도 실제 영상의 물리적 정답을 판정하거나 S11의 상태를 변경하지 않는다. 체크리스트의 모든 Windows 구간은 이번 실행 기준 `NOT_EVALUATED/U`다.

## 실제 peer probe 재현

이 script는 사용자의 기존 checkout 및 저장 증거를 필요로 한다. 이 ZIP에는 영상·모델 weight·기존 113프레임의 전체 capture·private Windows 원본이 없다. ZIP 단독으로 실행되는 detector 배포본이 아니다.

검증 당시 사용자 Mac 환경은 repo의 `.venv/bin/python` 및 설치된 의존성을 사용했다. 다음 명령에서 script의 절대 경로를 압축을 푼 위치로 지정한다. 출력 디렉터리는 **존재하지 않는 새 경로**여야 한다.

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
PYTHONPATH=src:. .venv/bin/python \
  /ABSOLUTE/PATH/TO/THIS/BUNDLE/scripts/peer_probe.py \
  --output sample/output/s11-peer-support-reproduction-NEW
```

이 실제 실행 script는 `assert`를 이용해 source/capture hash를 확인하므로 **`python -O`로 실행하지 않는다.** Production source pin이 바뀌었다면 실패가 정상이다. 새 HEAD로 검증하려면 별도의 baseline 검토가 필요하며, assertion을 지워 통과시키면 안 된다.

필요한 native 자료:

```text
sample/output/s11-p5-default-linkage-20261011-001/none/
  raw.json
  completed.json
  summary.json
sample/sample4.oilrecipe
docs/70-reference/s11-program-audit-2026-10-11/native-evidence/
  sample4-current-default.json
docs/50-diagnostics/s11/2026-10-12-public-compressor-source/pipeline-linkage/
  storage.json
  captures.zip
```

실행된 script SHA-256:

```text
0376cf9044715f21c3389e89bf2528964edcf5821cd87d649a8d3ede055dfb6e
```

전체 native 실행 산출물은 사용자 Mac의 다음 경로에 있다.

```text
sample/output/s11-program-review-20261012-001/
```

이 배포본의 receipt는 tool 출력과 실행 결과의 compact 요약이며, 원본 전체 JSON이라고 표시하지 않는다. 전체 per-peer row는 위 경로의 `verified-cli/peer-probe.json`을 사용한다. 12 px peer 표시 범위는 이번 두 Recipe의 실제 support 상한에 맞춘 진단 범위이며 새로운 production threshold가 아니다.

## 채택과 후속 구현

이번 spec은 별도의 ACTIVE 원장이나 기존 pilot의 소급 PASS 문서가 아니다. Work Plan/validation의 기존 owner와 O2/O3 승인 순서를 유지한다. WP1에서 신규 실험 입력·reference·모델·평가 범위를 먼저 고정하고, WP2/3의 새 역할 관측을 확인한 뒤 typed shadow, Windows, behavior, report 순으로 진입한다.

CR-1 모델 inference/training 및 production 통합은 이번에 실행하지 않았다. 새로운 source의 역할 일반화와 Windows CPU 비용도 아직 측정되지 않았다. 이 불확실성을 synthetic 테스트나 public sample의 numeric coverage로 대체하지 않는다.
