# S11 post-CR1 review package — 2026-10-12

## 읽는 순서

`S11-program-review-and-work-spec-post-CR1-2026-10-12.md`가 본문이다. 첫 부분에 결론·이번 실행 결과가 있고, 뒤에 운영정책, Oil/Foam 작업 명세, 10개 work package, Windows 9구간, 종료 기준과 기존 문서 관계가 있다.

`S11-review-execution-summary.json`은 이번 세션의 실제 검증 요약이다. 과거 결과와 이번 실행, 물리적 미평가를 구분한다.

`audit_cr1_saved.py`는 기존 repository의 검증기·cadence 계산을 재사용하고, 저장 CR1 점수/후보 경쟁/CSV를 읽는 재현 도구다. encoder·detector·임계값 선택을 실행하지 않는다. 소스와 영상, mask/prepared input, 기존 report가 baseline 경로에 남아 있어야 실행된다. 이 package만으로 모델 실험이 복구되는 것은 아니다.

## 재현

기준 HEAD: `0bc5af74dc0818a166fc99f7bbdf3b05cd7b65f1`.

기존 virtual environment를 사용한다. 새 dependency 설치나 모델 다운로드는 필요하지 않다. repository 경로와 package 경로는 실행 환경에 맞게 지정한다.

```sh
REPO="/Users/sunjaekim/Developer/oil_level_tracker"
PACKAGE="/absolute/path/to/s11-post-cr1-review-2026-10-12"

"$REPO/.venv/bin/python" "$PACKAGE/audit_cr1_saved.py" \
  --root "$REPO" --verify-video
```

JSON은 stdout으로 출력된다. 지속적인 실험 출력으로 보존하려면 repository의 `experiment-artifact-lifecycle.md`에 따라 managed run을 먼저 열고 그 output 위치에 저장한다. 이 스크립트는 출력 파일을 직접 생성하거나 기존 증거를 덮어쓰지 않는다. `python -O` 실행은 금지한다. 원 검증기가 assertion을 사용하기 때문이다.

`--verify-video`를 빼면 추가 원본 디코드 없이 saved-result 검증과 재집계만 한다. 옵션을 넣으면 sample4 11개 ROI와 공개 압축기 f1499를 대조한다. **sample3은 읽지 않는다.** 고정 영상·frame·crop 값은 과거 증거를 재현하는 audit fixture이며 생산 runtime의 예외 규칙이 아니다.

## 실제 확인한 실행 범위

Mac의 기존 Python REPL에서 동봉 스크립트와 byte-identical 소스를 compile/exec하고 `run(root, True)`를 실행했다. 기존 검증기 PASS, 12개 고유 source-frame 일치를 확인했다. 동일 소스 SHA-256: `b31773b892d0f5fddd3794051a207896016a986a96a86e779549a211eca09c8c`. standalone CLI subprocess 자체의 end-to-end 실행은 별도로 하지 않았다. Python 문법 검사도 통과했다.

다음 focused suite를 새로 실행해 109 tests가 통과했다.

```sh
cd "$REPO"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest \
  -q -p no:cacheprovider \
  tests/unit/test_s11_observation_cadence.py \
  tests/test_center_path_diagnostics.py \
  tests/unit/test_source_context_renderer.py
```

## 범위와 상태

이 package는 대화 산출물이다. repository에 문서·코드를 반영하거나 commit/push하지 않았다. CR1 재추론, 학습, 새 threshold 선택, production 변경, Windows 검증, 새로운 truth 라벨링을 하지 않았다. `S11 ACTIVE / field FAIL / O2 OPEN / Local XY OFF`를 유지한다. field FAIL은 기존 disposition이며 이 세션의 새 Windows 실행 결과가 아니다.

원본 영상, 모델·weights/cache, 대형 trace를 복제하지 않았다. CR1 환경은 유지했다. 새 policy family는 제안이며, 원 실험의 CLOSED_WITHOUT_PROMOTION과 후속 SCOPE_LIMITED_USEFULNESS를 변경하지 않는다.
