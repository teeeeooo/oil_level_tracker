# S11 전체 진행 검토 · Detector 부분 재설계 · 작업 명세서

**검토일:** 2026-10-12  
**기준 저장소:** `teeeeooo/oil_level_tracker`  
**직접 확인한 checkout:** `/Users/sunjaekim/Developer/oil_level_tracker`  
**기준 HEAD:** `2c2ddd20b3dfe0eddcbc8d747b01e766522536a1` (`main`)  
**문서 성격:** 현재 상태 감사 + 실행한 추가 진단 + 후속 설계 제안. Production 변경·O2/O3 승인·FIELD PASS 문서가 아니다.

> 목표는 모든 프레임의 모든 경계를 맞히는 것이 아니다. 실제 report 산출물을 본 사용자가 액상 계면과 Foam의 움직임, 전환, 주요 사건을 잘못 이해하지 않도록 만드는 것이다.

## 0. 결론과 결정 권고

**전체 detector 재작성은 권고하지 않는다. 대신 “물리적 역할을 관측하는 계층”을 부분 재설계하고, 그 근거를 anchor와 continuation 양쪽에서 소비하도록 단계적으로 연결한다.** 현재 남은 일을 보고서 UI 개선이나 threshold 조정으로 대체해서는 안 된다.

| 결정 | 권고 |
|---|---|
| 지금 유지할 것 | 기존 frame/candidate provenance, bounded tracking, Oil/Foam 독립성, lifecycle, CSV/report 파이프라인, sample3 격리 |
| Oil 우선순위 | 경계가 있는지보다 **어느 경계가 추적 대상 액상 계면인지**를 판별하는 현재 프레임의 역할 근거 |
| Foam 우선순위 | **존재 판단 / 상단 위치 관측 / 시간적 episode 판정**을 분리. 먼저 올바른 raw upper-front 후보를 만들 것 |
| 다음 신규 연구 | 동일한 국소 RGB 통계의 변형이 아니라 **전체 sight-glass 문맥을 반영하는 사전학습 시각 표현**을 한정된 offline challenger로 시험 |
| 지금 하지 않을 것 | Local XY 재활성화, support/texture threshold 구제, anchor 조건만 수정, episode 완화, cost-order 재시도, report 보간으로 성능을 꾸미기 |
| S11 완료 판단 | 국소 오류 개수가 아니라 **맥락 왜곡(A), 핵심 맥락 소실(B), 허용 가능한 국소 잔차(C), 미평가(U)**를 분리하고 Windows 9개 구간과 실제 report 이해도를 검증 |

**권고의 강도도 구분한다.** “역할 관측 계층의 부분 재설계”는 현재 증거에 근거한 방향 결정이다. 이 문서의 `CR-1` 사전학습 표현 실험은 그 방향을 검증할 **새 연구 제안**이다. 이 모델이 실제 압축기에서 작동한다는 검증은 아직 없으며, 기존 O2 진입 조건을 이미 충족했다는 의미도 아니다.

완전 자동화를 장기 방향으로 유지하되, “모든 장면을 자동 판별하거나 Foam을 전면 포기하거나”라는 이분법은 채택하지 않는다. 지원 가능한 장면의 신뢰할 수 있는 측정과 관측 불가 상태를 구분하고, 일부 국소 누락이 있어도 중요한 변화가 남는 detector를 목표로 한다. 다만 **Foam 존재만 검출한 성과를 Foam 높이 자동측정 완료로 바꾸어 부르지는 않는다.**

---

## 1. 이번에 실제로 수행한 일과 수행하지 않은 일

### 1.1 수행한 일

현재 checkout의 HEAD·branch·작업트리, `AGENTS.md`, S11 skill, Work Plan, Roadmap, execution policy, logic map, failure registry, 관측 witness 설계·검증 계약을 직접 읽었다. 10월 12일 boundary feasibility handoff와 당일 distribution/mean 실험을 검토하고, sample4 기본 실행, P5 default linkage, public compressor의 current→completed→publication 증거를 비교했다. [E01–E12]

영상 검토는 **저장된 원본 프레임·source contact sheet·검토 그림**을 대상으로 했다. `base_sample_1`, `sample2`, `sample4`, `sample5`, `sample6`, `sample7`, 신규 public compressor의 시각 자료를 직접 확인했다. 전체 영상을 새로 연속 재생하거나 새로운 프레임 정답을 만든 것은 아니다. `sample3`는 새 decode·재라벨링·분석에서 제외했다. [E03, E10, E12]

추가로 **현재 production의 `_cross_representation_support()`를 저장된 모든 Oil 후보와 각 peer에 다시 적용하는 진단**을 구현·실행했다. 샘플별 기존 완료 결과와 후보 index/source/Y를 대조하고, 기록되어 있는 support를 재현했다. threshold, source, 후보 목록, 판별 결과를 바꾸지 않은 attribution 진단이다. [N01]

| 이번 실행의 범위 | 결과 |
|---|---:|
| sample4 저장 프레임 | 113 |
| public compressor 저장 프레임 | 3 |
| Oil 후보 index/source/Y 대조 | 2,618개: sample4 2,549 + public 69 |
| 저장 support 값 재계산 일치 | 1,892개: sample4 1,841 + public 51 |
| 저장 support와의 불일치 | 0 |
| 저장 support 필드가 없는 후보 | 726개 — 일치나 불일치로 계상하지 않음 |
| 비교 전후 hash가 유지된 production Python 파일 | 221개 |
| public 압축 archive 내 hash/byte length 검증 | 95개 logical file |
| 이번에 새로 실행한 관련 pytest | **124 passed in 4.69s** |

각 peer를 하나씩 넘겼을 때의 기여도 최댓값이 전체 후보 집합으로 계산한 support와 같은지도 확인했다. 따라서 아래 설명은 임의로 비슷한 수식을 만든 결과가 아니라 **현재 구현의 실제 support 경로 분해**다. 다만 support 함수 자체의 독립 구현 검증, 새 detector 성능 시험, 물리적 정답 인증은 아니다.

진단 최초 시도에서 오래된 sample4 receipt의 `raw/completed`가 전체 detection이 아니라 **row hash 목록**임을 확인하지 않아 TypeError가 발생했다. 출력 산출 전에 중단됐고, 이후 이미 존재하는 P5 default linkage의 hash-검증 raw/completed capture를 사용하도록 수정했다. 최종 CLI를 새 출력 디렉터리로 재실행했다. 초기 실패를 성능 실패나 PASS에 포함하지 않았다.

### 1.2 하지 않은 일

새로운 production detector 구현, 사전학습 모델 다운로드·추론·학습, Windows 실제 영상 실행, 신규 전체 영상 replay, 독립적인 report 이해도 시험, commit/push는 하지 않았다. 이번 결과의 정당한 표현은 **“원인 검토와 추가 진단을 실행하고, 다음 구현 범위를 설계했다”**이다. “Detector가 개선됐다”, “Windows가 통과했다”, “S11이 완료됐다”는 표현은 성립하지 않는다.

추가 진단 원본은 다음 ignored output 아래에 남겼다.

```text
sample/output/s11-program-review-20261012-001/
  peer_probe.py
  peer-probe.json                 # 첫 성공 실행
  peer-probe.log
  verified-cli/peer-probe.json    # 최종 CLI 재실행
  focused-tests.log
  focused-tests.xml
  delivery-summary.json
```

이 배포 묶음에는 동일한 실행 script와 compact receipt를 포함했다. 모든 native per-peer row와 원본 영상은 이 ZIP에 복제하지 않았다.

---

## 2. 프로젝트 전반의 현재 위치

### 2.1 제품 기반과 detector 실효성을 구분해야 한다

| 영역 | 현재 상태 | 이번 판단 |
|---|---|---|
| Phase 1/2, S1–S10 | Roadmap상 완료 | 분석·geometry·CSV/report·패키징을 다시 만들 이유가 없음 |
| S11 | 실제 영상 detector 실효성 회복 단계, ACTIVE | 제품 사용성이 확보된 것과 field 검출 신뢰성 확보는 다름 |
| O1 | 로컬에서 수용된 진단/관측 기반 | 원인 확인과 동일성 검증에 재사용 |
| W4/O2 | identity challenger OPEN, O2 미완료 | 후보가 보인다는 이유로 behavior 진입 금지 |
| 최근 Windows disposition | **FIELD FAIL 유지** | public sample 성공으로 대체 불가 |
| Local XY | OFF | 이미 실패한 실험을 기본 동작으로 되살리지 않음 |
| O3/O4 | 후속 behavior 및 ownership/lifecycle 단계 | 역할 근거가 생긴 다음 각각 분리 검증 |
| P5 | Foam raw 관측·역할·episode의 분리 과제 | raw가 잘못됐는데 episode를 먼저 완화하면 오히려 위험 |
| P6/O5, P7 | Windows 전 구간·report 이해도·최종 disposition | S11 종료를 결정하는 마지막 근거 |
| S11-M, S12 | 후속 유지보수/UI 과제 | 지금 우선순위를 가져오지 않음 |

근거는 현재 Work Plan과 Roadmap이다. 본 문서는 별도의 평행 상태 원장이 아니며 이 상태를 변경하지 않는다. [E01]

### 2.2 그동안 진전이 없었던 것은 아니다

후보·측정의 lineage, native geometry, trace/NONE equality, report source-context, source-qualified review, lifecycle provenance가 정리되어 이제 **어디에서 무엇을 잃었는지**를 구분할 수 있다. 이는 실질적인 기반 성과다. 그러나 진단 설명력이 높아졌다는 사실은 새로운 역할 판별 정보가 생겼다는 뜻이 아니다.

현재 반복은 대체로 “더 자세한 표현 → 선택된 몇 지점에서 확인 → 전체 후보 경쟁 또는 다른 장면에서 한계 확인 → 진단 종료”다. 다음 연구를 시작할 때는 지표·문서만 더 만들 것이 아니라 **현재 표현과 정보적으로 무엇이 다른지**, 그리고 그것이 A/B 오류를 어느 경로에서 줄이는지를 먼저 적어야 한다.

---

## 3. 증거의 범위와 신뢰 수준

### 3.1 전체 분모를 하나의 정확도로 합치지 않는다

현재 P0는 기존 7개 영상의 16개 local group과 Windows 9개 구간을 연결한다. Local group은 서로 겹치므로 25개의 독립 표본이 아니다. 신규 public compressor는 추가 개발 증거이며 자동으로 untouched holdout이 되지 않는다. 기존 영상과 known Windows 장면은 이미 개발에 노출되었다. [E02, E03]

| Source | 유용한 검증 역할 | 주의점 |
|---|---|---|
| Windows sample1 | BASE full/drain/refill, Accum empty/splash/layered/post-foam/drain | field 우선 근거. 이번에 실제 원본 실행하지 않음 |
| base_sample_1 | 어두운 약한 계면, overlay 오염 경계 | f151부터 선 overlay. overlay를 물리적 계면 정보로 학습하지 않음 |
| sample2 | 밝은 기포성/곡면 구조, 초기 짧은 구간 | 이후 reframing은 동일한 고정 geometry 정답으로 확장 불가 |
| sample3 | 격리된 legacy 자료 | 새 decode·정답 채굴 금지. SKIPPED이며 PASS가 아님 |
| sample4 | 고정 sight-glass, Oil/Foam 혼합, 잘못된 극값과 owner gap | 지금의 가장 강한 공개 detector/보고서 sentinel |
| sample5, water | 어두운 Foam A, 이후 물 표면 B/C, 액체 유입 | B/C와 A의 구별이 중요. 밝기만으로 Foam 정의 불가 |
| sample6, beer | Foam 존재, 앞·뒤 투영, 상단 crop-out | crop 아래 경계를 Foam top으로 대신 쓰지 않음 |
| sample7, milk | 백색 액체와 Foam 혼동 방지 | 하단 경계 불명확을 Foam 부재로 바꾸지 않음 |
| 신규 public compressor | 사용자가 구분한 상단 Foam/하단 Oil과 실제 pipeline 연결 | f1499의 구간 정답이지 인접 프레임·전체 tracklet의 정답은 아님 |

기존 `.oiltruth`의 13개 usable coordinate도 전부 정확한 fixed-center contour truth는 아니다. 제안 좌표·눈금 환산·지역 검토를 구분하고, nearest-Y를 물리적 동일성으로 바꾸지 않는다. 새 결과는 source/recipe/reader/frame/coordinate 기준을 함께 고정한다. [E03, E11]

### 3.2 지금 해석할 수 있는 것과 없는 것

저장된 source sheet를 통해 구조·외관·검토 위치는 확인했다. 그러나 sparse frame만 보고 전체 Foam의 시작·종료 시각, 모든 반전, 연속 1초 구간의 가시성을 새로 확정하지 않았다. 물리적으로 확인하지 못한 후보는 **unreviewed**이지 곧바로 false candidate가 아니다.

수치화에는 세 좌표 의미를 분리한다. 후보가 주장하는 scalar Y, 실제 local contour가 관측된 source Y, 사용자가 지정한 지역/구간은 서로 같다고 가정하지 않는다. Descriptor 계산의 interpolation도 실제 측정 좌표의 interpolation이나 빈칸 메우기를 허용하는 근거가 아니다.

---

## 4. 현재 detector의 구조와 보존할 자산

```text
현재 프레임/마스크/원시 측정
  ├─ Oil raw evidence → proposal/hypothesis → candidate
  │     → evidence/phase identity/authority
  │     → tracklet → lifecycle/owner → selector → projection
  └─ Foam component/front 후보 → Foam identity/episode
                              ↓
                 sequence composition / provenance
                              ↓
                   tracking CSV / events / report
```

프레임 계층에서 Oil 검출이 먼저 실행되고 Foam 관측이 뒤따르는 부분과, 완료 sequence에서의 composition/episode를 구분해야 한다. 현재 `Foam`의 completed 결과를 같은 프레임의 독립 Oil 관측 근거인 것처럼 순환 소비하는 설계는 피한다. 두 역할이 공유할 것은 source pixels·visibility·native geometry이지, 상대의 최종 선택 결과를 정답으로 간주하는 것이 아니다. [E04]

| Owner / 파일 | 현재 책임 | 후속 변경 원칙 |
|---|---|---|
| `phase_frame_detection.py` | frame evidence, Oil/Foam 추출 호출 | shared primitive 관측과 phase 의미 부여 분리 |
| `oil_shadow_observations.py` | raw/proposal/hypothesis | 무작정 후보 수 확대 대신 실제 관측 경계와 role descriptor 연결 |
| `oil_candidate_evidence.py` | feature의 semantic view | 새로운 role evidence를 기존 texture scalar에 몰래 섞지 않음 |
| `oil_observation_resolver.py` | admission, peer support, sequence 연결 | 새 근거의 적용 지점을 anchor와 continuation 양쪽에서 검증 |
| `oil_candidate_authority.py` | authority tier | score가 높다는 이유만으로 role support 없이 승격하지 않음 |
| `oil_phase_identity.py` | phase identity | broad texture opposition과 실제 상대 phase를 구분 |
| `oil_interface_tracklets.py` 등 | association·bounded identity | 의미 근거 없이 cost/maturity 정렬만 바꾸지 않음 |
| `foam_front_detector.py` | component→raw front | upper role을 component의 min/max Y로 대신하지 않음 |
| Foam episode owner | 시간적 event | 올바른 raw evidence 확인 후에만 소비 조건 수정 |
| report/CSV owners | 동일 측정과 맥락 전달 | 가짜 수치 생성 금지, detector 개선과 표시 개선 구분 |

변경 대상은 우선 관측/역할 계층이다. downstream ownership이 완벽해서 보존하는 것이 아니라, 이미 확인된 기능과 안전 계약을 한 번에 무너뜨리지 않기 위해 변경을 분리한다.

---

## 5. 가장 중요한 실패는 “몇 프레임 틀림”이 아니다

### 5.1 sample4: 숫자가 충분해도 이야기가 틀릴 수 있다

기존 controlled default 0–56초 / 2 Hz 실행은 113개 row 중 Oil 101개, Foam 26개의 valid numeric을 기록했다. 그런데 실제 events에는 **42초 `MINIMUM_OIL_LEVEL`**, **44초 `MAXIMUM_OIL_LEVEL`**이 들어 있고, 두 선택은 이미 검토된 잘못된 Oil 대상이다. [E06, E07]

최저/최고 높이가 각각 다른 구조를 따라간다면 사용자는 큰 배유·급상승이 일어났다고 읽을 수 있다. 이는 113개 중 2개라는 작은 오류율로 허용할 문제가 아니라 **report 핵심 요약을 바꾸는 A 오류**다. 반대로 중요 변화를 보존하는 일부 국소 누락은 C가 될 수 있다. 따라서 검출 수·평균 Y 오차만 최적화해서는 목적을 만족하지 못한다.

같은 저장 결과의 `JUDGMENT_PASS`는 설정된 judgment rule에 대한 application 결과일 뿐이다. 그것을 S11의 물리적 계면 정확성이나 field PASS로 읽어서는 안 된다. 이번에는 해당 rule 자체를 변경하지 않았다.

### 5.2 public compressor: 후보 부족만의 문제가 아니다

f1499에서 사용자 검토 Oil 지역은 source Y421–435, Foam 지역은 Y323–338이다. 실제 기존 pipeline의 current Oil은 Y321, completed Oil은 Y288이다. Oil 지역에는 Y424/425/427/430의 후보가 남아 있다. [E10]

따라서 이 지점은 단순히 “낮은 contrast여서 선을 하나도 찾지 못했다”가 아니다. **대상 지역의 후보가 있는데, 다른 후보가 더 강한 역할/권한 근거를 받아 선택되는 문제**가 포함된다. 단, 범위 안에 있는 네 후보 모두의 exact-Y와 전체 경로가 정답이라고 인증한 것은 아니다.

### 5.3 Foam: 잘못된 front가 episode에 들어가는 문제부터 해결한다

sample4 f1620/54초에서 검토 구간과 일치하는 center edge Y813은 존재하지만, raw Foam 후보는 내부 texture Y833이다. 이 후보를 episode가 거부한다. 올바른 Y813이 episode로 들어가서 잃어진 사례가 아니다. 따라서 지금 formation/persistence를 완화하면 **잘못된 Y833을 더 잘 통과시키는** 변경이 될 수 있다. [E07]

신규 public compressor에서도 raw component의 extent로 정한 front와 사용자 검토 upper region은 다르다. sample5 water A에서는 기존 lightness-floor가 어두운 Foam support를 잃는 별도 문제가 있다. 이를 하나의 시간적 smoothing 문제로 합치면 안 된다. [E07, E10]

---

## 6. 이번 추가 진단으로 좁힌 원인

### 6.1 Support 점수 자체는 Oil 역할의 분류기가 아니다

아래는 **현재 실제로 선택된 후보**의 support와 route를 이번에 다시 계산한 것이다. 정답/오류 표시는 기존 source-qualified review에서 가져왔으며 이 점수로 만든 라벨이 아니다. [N01, E06, E08]

| sample4 시각 | 선택 Y | 기존 검토 | Authority reason | 재계산 peer support |
|---:|---:|---|---|---:|
| 38.0 s | 844 | 보호할 올바른 후보 | `corroborated_material_path` | 0.412215 |
| 40.0 s | 865.5 | 잘못된 후보 | `ordered_lower_interface` | 0.409443 |
| 42.0 s | 868 | 잘못된 후보·최저점 | `ordered_lower_interface` | 0.703011 |
| 42.5 s | 835 | 보호할 올바른 후보 | `continuation` | **0** |
| 44.0 s | 822 | 잘못된 후보·최고점 | `continuation` | **0** |
| 49.5 s | 836 | 보호할 올바른 후보 | `ordered_lower_interface` | 0.825632 |
| 52.0 s | 833 | 보호할 올바른 후보 | `continuation` | **0** |

도출되는 결론은 세 가지다.

1. **Support=0을 일괄 거부하면 잘못된 44초뿐 아니라 올바른 42.5초·52초도 함께 제거한다.** 같은 scalar 값만으로 이 후보들을 구분할 수 없다. 이것은 모든 알고리즘의 불가능성 증명이 아니라, 이 scalar 하나가 역할 분류에 충분하지 않다는 관측이다.
2. **Anchor 판정만 고쳐서는 44초의 잘못된 최고점을 직접 막지 못한다.** 그 순간의 route는 continuation이다. 후속 role contradiction의 소비 계약에는 continuation과 owner continuation도 포함해야 한다.
3. `ordered_lower_interface`라는 enum 이름은 실제 물리적 Oil 역할의 인증서가 아니다. 잘못된 40/42초와 올바른 49.5초가 같은 route를 사용한다.

모든 protected point를 영구적으로 한 점도 잃지 말자는 새 제품 목표를 만드는 것은 아니다. 다음 실험에서 일부 손실을 허용하려면 **그 손실이 전체 움직임에 미치는 영향과 C 범위를 사전에 정하고** 검증해야 한다. 점수 threshold를 바꾼 뒤 사라진 정답을 사후에 “허용 오류”라고 바꾸면 안 된다.

### 6.2 Public의 잘못된 Y288은 어느 peer에서 지지를 받았는가

| 대상/peer | Y | support 기여 | 관측 |
|---|---:|---:|---|
| 최종 선택 `material_path`, index10 | 288 | **0.2650188025** | `corroborated_material_path` |
| peer index1, phase hypothesis | 277 | **0.2650188025** | 최댓값을 제공하는 peer |
| peer index2, phase hypothesis | 287 | 0.2142566886 | 더 가깝지만 기여도는 작음 |
| 사용자 Oil 지역 내 index5/9/13/20 | 430/425/427/424 | **모두 0** | 남아 있지만 지지를 받지 못함 |

현재 support는 peer들의 투표 합이 아니라 **조건을 통과한 peer 기여도의 max**다. 따라서 이를 “여러 복제 후보가 점수를 계속 더하는 버그”라고 진단하면 틀린다.

Oil 지역의 peer들은 eligibility는 있어도 broad material-texture conflict가 약 0.912–1.0으로 높아 support 경로에서 배제된다. 반면 잘못된 상단 Y288은 다른 proposal family의 Y277로부터 0.265의 지지를 얻는다. 현재 `corroborated_material_path` route의 representation-support 조건 0.24보다 높다. [N01, E04]

이 관측은 **“다른 추출 family의 가까운 경계”와 “물리적 액상 계면을 지지하는 독립 관측”이 같지 않음**을 보여 준다. 동시에 계면 주변 Foam texture를 broad opposition으로 뭉뚱그리면 실제 하단 계면을 지지할 후보들도 같이 묶여 거부될 수 있다.

그러나 이 결과만으로 texture gate를 올리거나 peer 거리 12 px를 줄이지 않는다. public의 Y277 peer를 제외하더라도 sample4의 다른 잘못된 route와 continuation 문제가 남고, 올바른 후보들의 support도 달라질 수 있다. 새로운 정보 없이 몇 sentinel에 맞는 숫자를 만드는 것은 재설계가 아니다.

### 6.3 원인 경로를 하나로 합치지 말 것

| 실패 | 이번 판단 | 첫 변경 대상 |
|---|---|---|
| 잘못된 peer 지지로 upper structure가 anchor 획득 | 역할을 증명하지 않는 cross-family 근접성 | 현재 프레임 role witness / authority 입력 |
| broad texture가 대상 지역을 함께 배제 | 주변 재질과 경계 역할이 분리되지 않음 | 경계 상·하측의 공간적 문맥 관측 |
| 잘못된 continuation이 최대 높이로 공개 | anchor-only 수정으로는 불충분 | 역할 모순의 continuation 소비, 이후 O4 |
| source-qualified 후보가 final owner 제한으로 제외 | 이미 별도 원인 확인됨 | 올바른 witness 확보 후 handoff/ownership |
| Foam의 올바른 upper가 raw 후보에 없음 | episode 이전에 정보 소실 | Foam 후보 표현/역할 |
| completed/CSV/report 동일하지만 잘못된 물리 대상 | provenance가 진실성까지 보증하지 않음 | detector→실제 report의 의미 평가 |

---

## 7. 이미 닫힌 실험을 다시 이름만 바꾸어 시작하지 않는다

| 기존 방향 | 확인된 한계 | 이번 설계에서의 처리 |
|---|---|---|
| Polarity/source/motion으로 identity 구분 | 실제 이동·외관 반전과 다른 구조를 안전하게 분리하지 못함 | 역할의 독립 근거로 사용하지 않음 |
| Native path/fragment, center-conditioned DP | 표현의 정확성·연결성 확보는 유용하나 Oil/Foam 역할을 자동 보증하지 않음 | 관측 geometry로 재사용, recall/role PASS로 과장 금지 |
| Local XY 제외 | 국소 오염을 지운다고 물리적 대상 판별이 해결되지 않음 | OFF 유지 |
| Cost-order owner probe | 일부 지점 회복과 동시에 다른 구조 선택·phase 변경 | 재시도하지 않고 O4가 별도임을 유지 |
| Ordered row-distribution pilot | 최초 고정 비교의 요구된 opposition 선호를 만족하지 못함 | CLOSED 그대로 보존 |
| Mean-reference follow-up | 검토 Oil 6개 중 4개 선호, 2개 unresolved; 후보 전체에서 하단 다른 경계들도 선호 | 구현 적격 challenger로 승격하지 않음 |
| Foam component의 양 극값/밝기·면적만 사용 | 내부 texture, 투영, crop, 어두운 Foam에 취약 | 새 upper-role 근거 없이 변형 재시도 금지 |
| Episode/persistence 완화 | 올바른 raw front가 없으면 오검지 승인만 늘 수 있음 | P5-c 진입 조건을 유지 |

10월 12일 전체 후보 mean 진단은 7 capture의 160 proposal과 4 control, 총 164 query로 확장되었다. Interface-preferred proposal 33개, unavailable 31개가 나왔지만, f1485/1560에서는 검토 Oil이 unresolved인 반면 더 하단의 경계들이 선호됐다. 추가 query 150개가 자동으로 검토된 false label이 되는 것은 아니다. 그럼에도 **선택된 정답 patch에서의 4/6 성과만으로 실제 selector에 넣을 수 없다는 점**은 분명하다. [E09]

해당 pilot에서 요구했던 “명시적 opposition 종류 선호”와 제품 단계의 “그 후보를 Oil로 승인하지 않음”은 다른 요구다. 후속 실험에서는 둘을 미리 구분한다. 단, 이를 이유로 닫힌 pilot을 소급 PASS로 바꾸지 않는다. 특히 **UNRESOLVED가 legacy fallback을 통과하면 실제 잘못된 숫자는 그대로 남을 수 있으므로**, unresolved를 곧바로 성공적인 veto라고 해석해서는 안 된다.

---

## 8. 권고 아키텍처: Geometry · Role · Temporal identity의 분리

### 8.1 세 질문을 따로 답한다

- **Geometry:** 현재 source pixels에서 어느 위치에 어떤 경계가 관측되는가?
- **Role:** 그 경계는 추적할 액상 계면인가, Foam의 상단인가, 유리 구조인가, 재질 내부 texture인가?
- **Temporal identity:** 역할이 지지된 현재 경계를 직전의 어느 물리적 계면과 이어 볼 수 있는가?

Y가 비슷하거나 모양이 매끄럽다는 이유로 두 번째 질문을 세 번째 질문이 대신 답하지 않는다. 반대로 역할이 Oil이라는 것만으로 서로 다른 두 경계가 같은 track ID임을 보증하지 않는다.

여기서 Oil은 기존 제품의 **추적 대상 액상 계면 역할**이다. RGB 영상으로 순수 Oil의 화학 조성을 식별한다는 의미가 아니다. 기존 `oil_air` 필드 이름도 실제 기체가 공기라는 물리적 단정으로 읽지 않는다.

### 8.2 제안 데이터 계약 — 기존 witness의 확장이지 새 평행 파이프라인이 아님

| 필드군 | 의미 | 금지 사항 |
|---|---|---|
| `source_ref` | source hash, frame index/PTS, recipe/geometry ID, reader mode | neighboring frame의 label 상속 |
| `candidate_ref` | 동일 프레임 원래 index, source, Y/geometry reference | 출력 Y를 사후 보간하거나 다른 후보로 치환 |
| `geometry_observation` | native contour support, fixed-center 관측 여부, visibility, localization uncertainty | 모델 score로 없는 native edge를 만들어 냄 |
| `role_assessment` | `SUPPORTED / CONTRADICTED / UNASSESSED`와 역할 및 근거 | unresolved를 physical absence나 contradiction으로 강제 변환 |
| `foam_presence` | Foam 존재의 관측 결과, 별도 가시성 상태 | Foam height=null을 Foam 없음으로 해석 |
| `foam_upper_observation` | 관측 가능한 실제 upper-front만 위치화 | component lower extent 또는 crop border를 upper로 대신 사용 |
| `evidence_lineage` | 동일 pixels에서 파생된 descriptor·모델·mask의 관계 | 여러 모델 view를 독립 센서 여러 표로 셈 |
| `model_provenance` | 모델/weight/전처리/참조 bank hash, score 의미 | similarity를 교정된 확률이라고 표기 |
| `consumer_disposition` | 관측 전용인지 O3에서 승인된 veto/support인지 | O2 shadow 결과를 즉시 publish 권한으로 사용 |

Foam presence와 upper localization을 분리하는 것은 새로운 detector 표현 제안이다. 기존 schema/episode/공개 필드를 이 문서만으로 변경하지 않는다. 먼저 diagnostics-only 계약과 field shadow로 판단한다.

### 8.3 Role 근거의 소비 원칙

`SUPPORTED`는 검증된 관측에 한해 새로운 authority 근거가 될 수 있다. `CONTRADICTED`는 후속 O3에서 승인된 계약에 따라 anchor와 continuation 양쪽의 대상을 배제한다. `UNASSESSED`는 새 지지·새 모순을 주지 않는다. 기존 fallback이 살아 있는 경우 실제 결과에 어떤 영향을 주는지 그대로 기록한다.

기존 identity를 무조건 연장하는 근거로 role missing을 쓰지 않는다. 한편 모든 프레임에 강한 새 role score를 요구해 전체를 UNKNOWN으로 만드는 것도 성공이 아니다. 정상 움직임 구간의 실제 coverage와 핵심 전환 유지 여부를 함께 측정한다.

이 단계에서 새로운 witness를 소비하려면 **“어떤 현재 관측이 추가되어 이전보다 더 믿을 만한가”**를 설명할 수 있어야 한다. 기존 frame score·peer proximity·motion의 이름을 바꾸어 `role_confidence`로 포장하는 변경은 제외한다.

---

## 9. 신규 연구 CR-1: 전체 문맥을 보는 candidate-conditioned role 표현

### 9.1 선택 이유와 한계

현재의 여러 실패는 25×25 patch의 평균색, 분포, broad texture, family/Y 근접성만으로 서로 다른 역할을 나누려는 데 집중되어 있다. 다음 challenger는 **경계 주변의 국소 차이와 그 경계가 유리·액체·거품 영역 안에서 차지하는 관계를 함께 보는 표현**이어야 한다.

첫 backend 후보로 **고정된 DINOv2 ViT-S/14의 contextual patch feature**를 제안한다. DINOv2의 공식 모델/논문은 사전학습 feature를 image/pixel task에 사용하는 접근을 제공한다. 의료용 투명 용기 연구도 용기·재질·부품·관계를 나누어 다루는 문제 설정을 보여 준다. 여기서 얻는 근거는 **관측 단위를 국소 경계에서 재질과 용기의 문맥으로 확장할 이유**이지, 이 모델이 압축기 Oil/Foam을 이미 정확히 판별한다는 증거가 아니다. [R01, R02]

DINOv2를 최신 최고 모델이라고 주장해서 선택하는 것은 아니다. 한 개의 작은 고정 encoder로 새 표현의 효용을 확인하기 위한 제안이다. 모델 교체 경쟁, end-to-end video model 학습, 전체 architecture 교체는 첫 실험의 범위가 아니다.

새 encoder가 **새 광학 정보**를 추가하지는 않는다. 추가되는 것은 사전학습된 통계적 표현과 넓은 시야의 문맥이다. Source 자체에 구별 가능한 정보가 없으면 여전히 UNASSESSED여야 한다. 이 제한을 모델 confidence로 덮지 않는다.

### 9.2 1차 실험의 고정 범위

| 항목 | 명세 |
|---|---|
| 실행 위치 | production 환경과 분리된 offline diagnostic 환경 |
| Encoder | ViT-S/14 한 개, weight와 구현 revision을 preflight에 pin; 학습·fine-tune OFF |
| 입력 | 검증된 native sight-glass ROI, 원래 source/geometry/visibility; 전체 source frame를 다른 host/API로 전송하지 않음 |
| 후보 집합 | 기존 저장 후보 전체와 승인된 native geometry 표현. 검토된 정답 후보만 crop하는 실행 금지 |
| Query metadata | image pixels·visibility·geometry만. timestamp, clip ID, Glass ID, 검토 Y, label은 특징 입력에서 제외 |
| Reference bank | 이미 source-qualified된 initialization 자료만 사용. 역할별 동일 개수로 고정, 해당 query 또는 주변 프레임을 결과 확인 후 추가 금지 |
| 역할 | 액상 계면, Foam upper, 구조/내부 texture의 구분 가능한 범위. 라벨 불충분 역할은 활성화하지 않음 |
| 출력 | 후보별 descriptor, role similarity, top-2 margin, missing/ambiguous 이유, 동일 픽셀 lineage |
| 실행 예산 | encoder 1개 × representation 2개(full-context/local-only), 고정 reference bank 1개; 결과를 본 뒤 bank/threshold를 순차 구조하지 않음 |
| 물리적 효력 | 첫 실행은 preference diagnostic만. production의 지지/거부 권한 없음 |

초기 corpus에는 여러 유형의 source qualification이 섞여 있다. **정확한 candidate role로 바인딩할 수 없는 지역/시각 라벨을 학습용 exact contour로 바꾸지 않는다.** reference를 만들 수 없는 역할은 그 원인을 쓰고 해당 head를 미평가로 남긴다. 불충분한 라벨을 채우기 위해 sample3를 다시 읽거나 unknown 후보를 negative로 만드는 것은 금지한다.

### 9.3 구체적 연산

1. 원래 ROI의 aspect ratio를 유지하고 고정 canvas로 변환한다. 입력 크기·padding·mask 규칙을 preflight에 한 번 기록한다. 확대가 native 해상도나 정답의 정밀도를 늘렸다고 주장하지 않는다.
2. 고정 encoder에서 ROI 전체를 본 **위치별 contextual token**을 얻는다. 모든 후보에 같은 global 평균 vector를 붙이는 방식은 사용하지 않는다. 공통 vector만으로는 후보 사이의 역할 차이가 생기지 않기 때문이다.
3. 각 native contour의 유효한 X support를 따라 상측 strip과 하측 strip을 잡는다. 후보 간 비교에 visibility/support 차이가 편향으로 작동하지 않게 공통 support 기준을 적용하고, 부족하면 unavailable로 남긴다.
4. 각 strip의 contextual feature를 정규화하여 `u`와 `v`로 만들고, 차분 `u−v`를 별도로 정규화한다. 첫 표현은 `z = normalize(concat(u, v, normalize(u−v)))`로 고정한다. near/far strip을 쓰는 확장이나 추가 feature weight 탐색은 첫 실험에 넣지 않는다.
5. 고정 reference의 같은 연산 결과와 cosine similarity를 비교한다. Cosine은 L2-normalized vector의 내적이며 score 범위는 [−1, 1]이다. 역할별 prototype 수를 같게 하고 mean 또는 max 중 하나를 preflight에 선택·고정한다. **첫안은 역할당 1개 prototype**으로 이 차이를 제거한다.
6. `diagnostic_preference`는 유효 score 중 유일한 최댓값일 때만 부여한다. 차이가 `1e−6` 이하이면 tie로 UNRESOLVED. reference/support 누락·zero norm·비유한 값은 UNAVAILABLE이다. 이 operating rule은 **순위 feasibility용**이며, 출하용 probability threshold가 아니다.
7. 같거나 인접한 Y의 복제 proposal은 원래 index별로 모두 보존하되, 동일 픽셀 support/descriptor를 공유하는 항목을 독립 성공 여러 개로 세지 않는다.

**물리적 역할 승인용 operating point는 별도다.** Preference 분리가 실제로 확인된 뒤 training/development split에서 `SUPPORTED / CONTRADICTED / UNASSESSED`의 허용 기준을 정하고, 보호 control·외부 source 실행 전에 동결한다. 근거가 부족하면 O2 진입을 요청하지 않는다. 순위 diagnostic의 유일 최댓값을 곧바로 `SUPPORTED`로 이름만 바꾸는 것은 금지한다.

### 9.4 반증 조건과 구조적 ablation

| 검증 | 합격에 필요한 정보 | 실패로 보는 경우 |
|---|---|---|
| Synthetic reachability | 서로 다른 유효 feature와 missing/tie 상태가 각각 도달 가능 | 항상 unresolved 또는 항상 한 역할 |
| Local-only ablation | 동일 encoder/정규화/reference를 사용하되 국소 crop만 보게 했을 때와 차이를 제시 | 이름만 full-context이고 출력·역할 차이에 새 정보가 없음 |
| 고정 참조 재현 | initialization score는 학습/참조 확인으로 별도 표기 | 자기 reference를 맞힌 것을 성능으로 셈 |
| 전체 후보 경쟁 | sample4 고정 query 전체에서 알려진 대상·오류·미검토 후보를 분리 보고 | 정답 후보 patch에 대해서만 좋은 결과 |
| 알려진 40/42/44초 오류 | known wrong candidate의 역할/승인 결과와 대체 후보 모두 확인 | 기존 오검지만 사라지고 다른 미검토 구조가 그 자리를 차지 |
| 보호된 정상 움직임 | 정확한 candidate 유지와 episode 맥락 유지 둘 다 계상 | all-UNKNOWN으로 오류를 숨김 |
| 신규 public compressor | source를 바꿔도 하단 대상 지역과 상단 구조의 경쟁을 유지 | sample4 위치·색·촬영 구도만 기억 |
| geometry 변환 control | 허용된 translation/resize와 source mapping을 따라 일관된 관측 | 절대 Y/clip identity로 결과가 결정됨 |
| 역할별 제약 | 어두운 water Foam, beer crop, milk 불명확성을 분리 | Foam=white, 가장 아래=Oil 같은 shortcut |

하나의 특징이 모든 장면에서 완전 분리되어야 제품을 만들 수 있다는 뜻은 아니다. 다만 새 표현의 정보적 차이 없이 기존의 실패를 다른 이름으로 반복하지 않기 위한 반증이다. 공개된 추가 후보의 역할이 불명확하면 제한된 증거로 남겨야 하며, 심사 통과를 위해 그 후보를 성공이나 실패 중 편한 쪽으로 임의 분류하지 않는다.

### 9.5 왜 graph cut이나 다른 분할 출력을 바로 붙이지 않는가

Eppel의 graph-cut 접근은 vessel contour와 pixel contrast로 경계를 찾으며 상단 10%를 gas/air, 하단 10%를 material로 가정한다. 현재의 FULL/EMPTY, 다층 Foam, rim, crop 조건에서는 그 anchor 가정이 보편적으로 성립한다고 할 수 없다. 따라서 기존 graph/contour 관측의 보조 아이디어일 수는 있어도 역할 판별의 직접 대체안은 아니다. [R03]

투명 액체의 self-supervised segmentation 연구는 colored liquid 영상과 transparent 영상, 자동 background label, 생성 모델을 이용하는 별도 데이터 생성 전략을 제시한다. 이 전략은 장래의 학습 데이터 확보 후보이지 지금 가진 압축기 영상에 즉시 적용되는 zero-setup detector가 아니다. 현 단계의 단기 작업에 새 촬영·착색·장비 변경을 필수 조건으로 추가하지 않는다. [R04]

### 9.6 배포·비용·보안 제약

모델은 먼저 offline-only dependency로 두고 `src` 및 기존 `.venv`를 오염시키지 않는다. 업무 PC의 데이터는 반출하지 않으며 최종 후보는 **weight/실행 파일 반입 후 네트워크 없는 로컬 추론**이 가능해야 한다. Runtime에서 hub 다운로드나 외부 API fallback이 실행되면 탈락이다.

Weight/코드 license, CPU 실행 가능성, Windows 패키지 크기, peak RSS, decoding을 포함한 시간, 관측 주기당 추가 비용을 기록한다. 이 문서는 실제 모델 latency·memory를 측정하지 않았으므로 숫자를 약속하지 않는다. 출력만 비슷하게 만드는 quantization·ONNX·모델 축소는 역할 타당성이 확인된 뒤 별도 equality/accuracy 검증을 거친다.

---

## 10. Foam 작업은 두 관측과 하나의 시간 판정으로 나눈다

### 10.1 존재와 위치를 같은 Boolean으로 만들지 않는다

| 관측 | detector가 말할 수 있는 것 | 말하면 안 되는 것 |
|---|---|---|
| Foam 존재 확인 + upper 관측 | Foam이 보이며 이 native 경계가 상단이다 | confidence만으로 source 밖 높이를 추정 |
| Foam 존재 확인 + upper crop/불명확 | Foam은 보이나 현재 상단 위치는 측정 불가 | height=null이므로 Foam이 사라졌다고 판단 |
| 가시 구간에서 Foam 부재 확인 | 해당 관측에서 Foam을 뒷받침하는 재질이 없다 | 단순 front 후보 거절을 물리적 부재로 승격 |
| 관측 불충분 | 존재/부재 모두 미평가 | “없음”으로 event 종료 |

존재만 검출하는 head가 먼저 작동할 수 있으나, 이는 **Foam 움직임 높이의 완전한 자동측정이 아니라 부분 성과**다. 상단 상승·하강의 맥락을 전달하려면 실제 위치 관측 또는 report의 원본 맥락과 결합한 검증이 필요하다.

### 10.2 Raw upper-front 재설계

Foam 후보는 Oil이 이미 선택한 band에 종속시키지 않고 shared current-frame geometry에서 생성한다. Native fragment/path를 단순히 합쳐 큰 component를 만든 뒤 min/max Y 하나를 선택하는 구조를 반복하지 않는다. 여러 관측 가능한 경계를 유지하되 각각의 상측/하측 문맥이 **Foam 상단 역할**을 지지하는지 평가한다.

기존 component label, brightness, edge, texture는 descriptor의 자료일 수 있다. 하지만 밝음 자체, bottom connection, component 면적, motion만으로 “Foam upper”를 선언하지 않는다. Beer의 앞/뒤 투영, milk의 불명확한 하단, water의 어두운 Foam을 별도 control로 둔다.

P5-b의 핵심 재현 목표는 f1620에서 **기존 내부 Y833을 더 잘 유지하는 것이 아니라 관측된 upper 지역의 올바른 native 후보가 존재하도록 하는 것**이다. 그 다음에 같은 후보가 completed와 report까지 살아남는지 검증한다.

### 10.3 Episode는 조건부 작업이다

올바른 raw upper가 입력됐는데 episode에서 사라지는 증거가 확보될 때만 P5-c를 연다. 현재 f1620 증거는 이 조건을 만족하지 않는다. Presence-based episode를 새로 도입한다면 그것은 기존 front 기반 episode의 threshold 조정이 아니라 **별도 input 의미와 검증 계약 변경**으로 다룬다.

Foam 시작, 마지막 관측, 물리적 소멸은 다른 시각이다. 마지막 numeric row를 자동으로 소멸 시각으로 승격하지 않는다. 허용 시각 오차도 Oil의 1초 요구를 Foam에 그대로 복사하지 않는다.

---

## 11. 전체 작업 패키지와 기존 계획의 관계

다음 표의 순서는 기본 의존성이다. Oil과 Foam 관측 실험은 공통 corpus/geometry 계약 아래 병행 가능하지만, Windows 검증·behavior 채택 전에 결과를 섞어 하나의 PASS로 만들지 않는다.

| ID | 작업 / 변경 범위 | 산출물 | 종료 및 다음 진입 조건 |
|---|---|---|---|
| WP0 | 현재 상태·first-harmful-stage·peer 지지 재현 | **이번 문서, peer probe, 124개 test 결과** | 이번에 실행 완료. Detector 개선은 아님 |
| WP1 | P0 scene ledger와 source/candidate/role reference를 재사용하여 CR-1 preflight 고정 | source·recipe·frame·reference·weight·support·holdout·예산 manifest | 새로운 라벨을 암묵 생성하지 않고 replay 입력을 식별할 수 있음 |
| WP2 | CR-1 전체 문맥 role feature, local-only ablation | diagnostics-only descriptor/competition 결과, 모든 unknown 포함 | 참조 자기 재현을 넘어 정보적 차이가 있고, bounded control 전체 결과 확보 |
| WP3 | P5-a/b: Foam presence와 native upper 후보/role 관측 | raw candidate population, presence/upper 구분, source join | 올바른 raw upper 생성과 negative/crop 불가 상태가 구분됨 |
| WP4 | 기존 typed witness에 신규 근거를 shadow 연결, operating point 동결 | API contract, trace, frozen policy, NONE/FULL equality, resource record | V2/V3/V4 및 entry 자료 완성. Production behavior 여전히 OFF |
| WP5 | **V5 Windows shadow, 이후 O2 판단** | 동일 private source의 9구간 결과·hash·review ledger | source/역할·오류/누락·정상 구간 영향 검증. Mac 결과로 우회 금지 |
| WP6 | O3 behavior: 승인된 role support/contradiction 소비 | 기본 후보군과 변경군의 실제 pipeline·report A/B | known A를 제거하면서 B를 악화시키지 않음. Unknown fallback 효과도 설명 |
| WP7 | O4: 역할이 확인된 계면의 owner/handoff/continuation 수정 | source-qualified candidate의 raw→owner→publication causal replay | 잘못된 owner 지속과 correct reappearance 누락을 동시 검증 |
| WP8 | P5-c, 필요한 경우에만 | 올바른 raw upper가 episode에서 소실되는 증거와 단일 수정 | false Foam 및 소멸 후 residue 음성 구간 비회귀 |
| WP9 | P6/O5: 9개 Windows 구간 + 실제 report 독립 이해도 | generated bundle, reviewed story ledger, A/B/C/U disposition | 핵심 움직임·사건 맥락을 전달. 미평가 범위 공개 |
| WP10 | P7: S11 disposition / 지원 범위 / 다음 release | 지원 장면·known limitation·회귀 corpus·최종 상태 | 그 후 S11-M/S12 우선순위 결정 |

### 11.1 구체적인 코드 작업 경계

**WP1–WP3:** 우선 `tests/diagnostics/`의 별도 helper와 preflight/evidence에서 작업한다. 제안 파일명은 `s11_context_role_probe.py`, `s11_foam_presence_upper_probe.py`이며 실제 owner 구현 전에 충돌 여부를 확인한다. 기존 native graph/contour helper를 복제하지 말고 재사용한다.

**WP4:** 기존 witness architecture와 validation 문서의 명시적 delta로 제안한다. 새로운 feature가 raw boundary likelihood, material-texture conflict, `representation_support`에 암묵적으로 섞이지 않게 typed 필드로 노출한다. Existing debug NONE 실행의 behavior가 바뀌면 shadow 단계 실패다.

**WP6:** `oil_candidate_authority.py`, `oil_phase_identity.py`, `oil_observation_resolver.py`의 소비 경계를 최소화한다. 잘못된 continuation이 current role contradiction을 무시해 공개되는 경로도 시험한다. 새 code path로 selected Y를 바꾸었다면 original candidate reference와 native geometry의 관계를 trace로 증명한다.

**WP7:** `oil_interface_tracklets.py`, lifecycle/selector/projection 관련 owner는 별도 변경 단위다. “가장 가까운 후보”, “가장 싼 match”, “더 오래된 track”을 물리적 동일성으로 대체하지 않는다. 기존 cost-order probe를 재실행하여 다른 이름으로 채택하지 않는다.

**WP8:** `foam_front_detector.py`의 raw 입력 의미가 확인된 후 episode owner를 수정한다. Front 좌표 route와 presence-only route를 혼합해 같은 validation 성공률로 보고하지 않는다.

### 11.2 연구의 시간·범위 상한

초기 CR-1은 **한 개 encoder, 한 개 reference bank, full/local 두 표현, 하나의 고정 전체 후보 실행**으로 제한한다. 결과를 보고 encoder·reference·threshold를 차례로 갈아 끼우는 자동 탐색은 이 work package에 포함하지 않는다.

첫 timebox는 **검토/개발 노력 4–6 engineer-day 정도를 계획 가정**으로 두되, 이는 현장 가용시간·모델 설치·추론 속도를 측정한 일정 약속이 아니다. Gate 통과를 위해 기간을 연장하는 대신, timebox 끝에서 다음 중 하나를 명시한다.

| 결과 | 다음 결정 |
|---|---|
| 새 표현의 discrimination이 있고 정상 문맥을 보존 | Operating point/typed shadow/V5로 진행 |
| 일부 역할만 유효 | 해당 역할의 부분 성과와 미지원 역할을 분리. Oil 성공을 Foam 성공으로 확대하지 않음 |
| 참조 프레임만 잘 맞거나 전체 경쟁에서 반복 혼동 | CR-1 닫음. 같은 bank/threshold 구제는 하지 않음 |
| 현재 source의 라벨/관측 정보로 평가 자체가 안 됨 | NOT_EVALUATED와 필요한 정보 종류를 명시. 모델 정확도 실패나 성공으로 바꾸지 않음 |
| CPU/Windows packaging이 제품 제약을 초과 | 성능과 배포성 결론을 분리하고 제한된 backend/지원 범위 결정 |

실패하면 모든 자동판별이 불가능하다고 결론내리지 않는다. 그러나 구체적인 정보 차이가 없는 다음 실험도 시작하지 않는다. 그때는 장기 supervised data 전략, 운영상 제한, 보조 관측 조건 중 **예산과 제품 효용이 명확한 경로**를 선택한다. 새 촬영이나 대규모 수동 라벨 작업을 당장 사용자의 필수 선행 과제로 떠넘기지는 않는다.

---

## 12. 검증 계약: 프레임 정확도가 아닌 맥락을 계측한다

### 12.1 세 층의 결과를 반드시 같이 남긴다

| 층 | 지표/기록 | 오용 방지 |
|---|---|---|
| 관측/후보 | 관측 가능한 target의 후보 존재, localization uncertainty, role preference/contradiction, 원래 index/lineage | 정답 후보를 미리 골라 놓은 뒤 “검출” 성공이라 부르지 않음 |
| 시간/사건 | 동일 계면의 상승·하강·반전, 극값 target identity, longest wrong run, longest missing run, Foam event의 존재·지속·종료 불확실성 | 모든 null을 정확한 abstention으로 처리하지 않음 |
| 실제 report | artifact만 본 독립 검토자가 이해한 변화/사건과 source-qualified story의 일치 | JSON equality나 Unit PASS를 comprehension PASS로 바꾸지 않음 |

기본 단위는 `scene_id + phase_role + evaluation_scope`이다. 관측 불가·미검토 분모를 별도로 공개하고, `0/0` 또는 전부 unknown을 100%로 표현하지 않는다. 잘못된 수치가 하나라도 극값·반전·Foam 생성/소멸을 뒤집으면 A가 될 수 있다. 반대로 한 점 누락이 별 영향을 주지 않는다면 사전 기준 아래 C가 될 수 있다.

### 12.2 A/B/C/U 판정

| 등급 | 정의 | 처리 |
|---|---|---|
| A — 맥락 왜곡 | 다른 구조를 Oil/Foam으로 따라 가짜 극값·방향 전환·사건을 만듦 | 알려진 중요 sentinel은 release 차단. 평균 검출률로 상쇄 금지 |
| B — 맥락 소실 | source에서 보이는 핵심 이동·회복·Foam event가 report에서 사라짐 | all-unknown 개선, 과도한 veto를 차단 |
| C — 국소 잔차 | 일부 누락·오검지·오차가 있지만 사전 정의한 핵심 맥락과 판단을 보존 | 허용 범위와 실제 잔차를 함께 기록. Error 자체는 삭제하지 않음 |
| U — 미평가 | source/geometry/role/시간적 가시성 근거가 부족 | PASS도 정확한 absence도 아님. 제한과 범위 공개 |

**새 공통 수치 budget을 이번 감사에서 임의 확정하지 않는다.** 현 validation의 1초 Oil 요구는 qualification된 visible moving Oil 범위에 적용한다. 이를 Foam 시작/종료, 모든 정지 계면, 모든 source에 그대로 강제하지 않는다. 새 pixel/seconds budget은 reference precision·sampling cadence·사용 목적과 함께 사전에 동결해야 한다. [E02]

### 12.3 잘못된 숫자 감소와 맥락 소실을 함께 평가한다

가짜 44초 최대값을 UNKNOWN으로 바꾸는 것은 A 개선의 후보지만 그것만으로 충분하지 않다. 42–44초의 실제 움직임 전체가 사라졌다면 B를 키운 것일 수 있다. 반대로 일부 지점을 버리고도 전후 실제 계면 움직임·source-context가 같은 이야기를 전달한다면 C로 정당화할 수 있다. 그 판단은 실험 후 유리한 프레임만 선택하는 방식이 아니라 고정된 episode 창과 report 검토로 수행한다.

새 역할 근거를 **항상 양성이나 명시적 음성 중 하나로 분류해야 하는 완전 분류기**로 만들 필요는 없다. 필요한 것은 그 근거를 실제 selector에 넣었을 때 A/B가 줄고 C/U가 정직하게 남는지다. 다만 특정 candidate를 unresolved로 둔 것이 실제 publication을 막는지 여부를 consumer 단계에서 반드시 확인한다.

### 12.4 실제 report 검토 절차

기존 reporter를 그대로 사용해 기본군/변경군의 완전한 bundle을 만든다. 개발자 설명·trace·정답표를 먼저 보지 않은 검토자가 각 artifact만 보고 “언제 액면이 내려가고 올라갔는지, 급격한 변화가 있었는지, Foam이 나타나고 유지/소멸했는지, 무엇이 측정 불확실한지”를 기록한다. 이후 source-qualified story와 비교한다.

원본 맥락 그림은 report의 정상적인 일부로 사용할 수 있다. 그렇다고 trace를 뒤져야만 잘못된 그래프를 정정할 수 있는 산출물을 합격시키지는 않는다. **보고서에 충분한 원본 맥락이 있다는 것과 숫자 그래프가 계속 엉뚱한 극값을 강조하는 것은 별도 문제**다.

이번에 contact sheet를 본 작성자의 판단은 이 독립 검토를 대신하지 않는다. 또한 public 113-row 결과의 NONE/FULL report model equality는 실제 이해도 시험이 아니다.

---

## 13. Windows 9구간 최종 검증표

기준은 기존 `windows-sample1-heating-coldstart-reviewed-truth.md`다. 아래 시간은 그 문서의 **대략적인 구간 경계**이며 새 exact timestamp truth를 만든 것이 아니다. source identity·frame/PTS·실제 구간 coverage를 실행 시 함께 기록한다. Private source hash가 기존 canonical 기록에 없는 부분은 다음 정당한 Windows 실행에서 read-only로 식별하며, 외부 반출을 요구하지 않는다. [E11]

| Canonical 구간 | 기대하는 맥락 | 가장 중요한 음성/퇴행 확인 |
|---|---|---|
| `WS1-BASE-FULL-PREFIX` 480–약550 s | FULL, 보이는 Oil 계면 없음, Foam 없음 | 유리 무늬를 Oil/Foam으로 만들지 않음 |
| `WS1-BASE-DRAIN` 약550–662 s | 액상 계면이 점진적으로 하강 | 장시간 다른 reflection track을 매끄럽게 따라가지 않음 |
| `WS1-BASE-RAPID-REFILL` 662–약663.6 s | 빠른 상승 후 상단에서 계면 소실/FULL | 급상승 전체를 지우거나 false 경계로 연결하지 않음 |
| `WS1-BASE-FULL-SUFFIX` 약663.6–780 s | FULL 유지, Oil/Foam 수치 부재가 타당 | 약725 s 하단 반사를 액면 재등장으로 오판하지 않음 |
| `WS1-ACCUM-EMPTY` 480–약653 s | EMPTY, Oil/Foam 없음 | 강한 정지 경계의 가짜 level/foam event |
| `WS1-ACCUM-ENTRY-SPLASH` 약653–672 s | Oil 상승, splash/wall 패턴 구별 | splash를 Oil 또는 Foam 상단으로 치환 |
| `WS1-ACCUM-FOAM-LAYERED` 약672–680 s | 상단 Foam과 하단 Oil의 별도 변화 | 상·하단 혼동, 두 곡선이 같은 texture/경계에 붙음 |
| `WS1-ACCUM-POST-FOAM` 약680–700 s | Foam 소멸 후 Oil 계면 지속 | 검출 종료와 물리적 소멸 혼동, residue Foam 유지 |
| `WS1-ACCUM-DRAIN` 약700–780 s | Oil 하강, 잔류 자국과 분리 | motion/appearance만으로 residue에 identity 고정 |

각 구간에 `actual coverage / numeric counts / wrong identity runs / missing runs / role evidence / phase-owner chain / source uncertainty / report interpretation / PASS-FAIL-NOT_EVALUATED`를 남긴다. 이전에 통과한 구간을 생략하지 않는다. 한 private 영상의 9개 구간을 9개의 독립 촬영 일반화 성능으로 표현하지도 않는다.

---

## 14. 이전 문서와의 관계 및 변경 관리

| 문서/계약 | 본 명세서와의 관계 |
|---|---|
| Work Plan / Roadmap | 현재 상태의 유일한 owner. 본 문서의 연구 제안은 아직 상태 변경이 아님 |
| 2026-09-17 direction assessment | 전체 재작성 대신 관측 계층 bounded redesign 방향을 유지하되, 국소 통계 연구 반복에서 벗어날 구체적 challenger를 제안 |
| Interface Observability Witness Architecture | native geometry·visibility·lineage·typed 소비를 재사용. Role/presence 확장은 명시적 delta로 심사 |
| Witness Validation / P0 / V2–V5 / O2–O4 | 순서를 유지. V5 Windows shadow 전에 O2 완료 선언 금지 |
| 2026-10-11 program audit 및 P5 default linkage | 101/113 수치 coverage와 잘못된 극값, raw Foam loss의 근거를 재사용 |
| 2026-10-12 boundary feasibility handoff | 현재 eligible successor 없음과 closed pilot을 그대로 인정. CR-1은 새 연구 제안이지 기존 pilot 재개가 아님 |
| Local XY / cost-order / mean-CDF pilot | 역사적 실패 기록 보존. 결과의 의미를 소급 변경하지 않음 |
| 본 묶음의 peer probe | 기존 F03/F04/F06/F09 경로를 더 구체화하는 diagnostic. Production owner 변경 없음 |

저장소에 채택할 때는 거대한 architecture 문서에 별도 상태 원장을 계속 쌓지 말고, 새 연구의 preflight·결과·명세서를 적절한 design/diagnostics/evidence 위치로 배치한 뒤 현재 Work Plan에 링크와 disposition만 추가한다. 새 기획이 채택되기 전에는 ACTIVE task나 field status를 바꾸지 않는다.

### History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-PROPOSAL`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: candidate fairness, raster/material corroboration, source/polarity identity, native contour/center representation, Local XY, cost-order owner attribution, Foam component/episode, mean/CDF/temporal role diagnostics, NONE/FULL publication linkage.
- Prior mechanisms rejected: role identity by Y proximity/family/motion alone; coordinate/time private exceptions; texture/support threshold rescue; component-extreme Foam repair; episode relaxation without correct raw front; report smoothing as detector correction.
- Preserved contracts: exact same-frame provenance, independent Oil/Foam ownership, bounded tracking/lifecycle, fail-closed unsupported measurement, source qualification, source/privacy restrictions, ordered shadow/behavior/field gates.
- Difference from prior failures: this audit decomposes actual max-peer support and separates wrong anchor from wrong continuation; the proposed CR-1 introduces contextual pretrained representation rather than another ordering or raw-color statistic; native geometry remains independently required.
- Logic-map impact: NONE — this delivery and its executed script do not change production ownership or behavior. Any later role/presence consumer is a proposed architecture delta requiring a separate owner update.
- Failure-registry impact: NONE — current findings refine existing role/support/continuation and Foam-reduction failure mechanisms; no new production mechanism or accepted fix is asserted.

### Detector Governance — executed diagnostic

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: for the public reviewed frame, existing cross-representation/texture-conditioned evidence supports an upper non-target anchor while lower-range candidates lack that support; the exact first historical physical identity error is not established. For sample4 f1320 the wrong selected candidate is continuation, not a new anchor; its earlier owner history remains governed by the existing causal record.
- Logic-map impact: NONE — the script calls the current support function on unchanged saved candidate inputs and records results, without modifying extraction, selection, authority, or publication.
- Failure-registry impact: NONE — attribution fits the existing insufficient-role-information and ownership failure families; passing recomputation does not promote a detector.

저장소에 실제 design/diagnostic 변경을 넣는 후속 작업은 해당 baseline을 명시한 governance check와 변경 owner의 focused tests를 수행한다. 이번 배포 Markdown을 생성한 것만으로 repository governance check를 실행했다고 주장하지 않는다.

---

## 15. 재현 방법과 산출물 사용법

### 15.1 이번 진단 재현

`peer_probe.py`는 이번에 Mac checkout에서 실행된 60-line 연구용 script의 **동일 bytes**다. SHA-256:

```text
0376cf9044715f21c3389e89bf2528964edcf5821cd87d649a8d3ede055dfb6e
```

Repo root에서 기존 `.venv`와 `src`를 사용하고, **존재하지 않는 새 출력 디렉터리**를 지정한다. Assertion 기반 pin 검사가 있으므로 `python -O`는 사용하지 않는다. Script가 사용하는 private-looking frame 번호는 평가용 입력 선택이며 production inference 조건이 아니다.

```bash
cd /Users/sunjaekim/Developer/oil_level_tracker
PYTHONPATH=src:. .venv/bin/python /path/to/this-package/scripts/peer_probe.py \
  --output /tmp/s11-peer-audit-new-directory
```

필수 native 입력은 `sample/output/s11-p5-default-linkage-20261011-001/none/{raw,completed,summary}.json`이다. 이들은 Git clone만으로 생기지 않을 수 있다. 현재 Mac에는 존재하며 이번 실행에서 사용했다. 없는 환경에서 sample3나 다른 replay로 조용히 대체하지 않는다. Original public ZIP와 tracked source/recipe/evidence도 필요하다.

Script는 모든 Oil 후보의 support를 계산하지만 detailed rows는 지정된 진단 프레임만 보존한다. 전체 계산 분모와 detailed row 분모를 구분한다. Radius 12 px peer excerpt는 이번 두 Recipe의 `temporal_max_jump_px=32`에 바인딩된 **진단 출력 범위**이며 새로운 detector threshold가 아니다. 다른 recipe를 조사하려면 먼저 generic output 범위와 검증 pin을 명시적으로 갱신해야 한다.

### 15.2 이번 pytest 재현

```bash
PYTHONPATH=src:. .venv/bin/python -m pytest -q \
  tests/unit/test_oil_candidate_authority.py \
  tests/unit/test_oil_observation_resolver.py \
  tests/unit/test_foam_episode_resolver.py \
  tests/unit/test_oil_measurement_lineage.py \
  tests/unit/test_s11_row_distribution_roles.py
```

관측·authority·episode·lineage·닫힌 실험 helper의 실행 건전성을 확인하는 테스트다. 실제 영상의 역할 정확도·report 이해도·Windows field 성능을 측정하지 않는다. 과거 handoff의 32개 테스트나 이전 audit의 검사 수를 이번 124개와 합쳐 “새로 통과한 총수”라고 하지 않는다.

### 15.3 배포 묶음

```text
S11-program-review-and-work-spec-2026-10-12.md
README.md
scripts/peer_probe.py
scripts/check_delivery.py
scripts/test_story_contract.py
story-contract.json
evidence/execution-receipt.json
evidence/focused-tests.log
evidence/story-contract-tests.log
SHA256SUMS.txt
```

`story-contract.json`은 A/B/C/U 판정과 Windows 9개 구간을 명시한 **제안 계약/체크리스트**다. 자동 정답 판정기나 채택된 production schema가 아니다. `test_story_contract.py`는 이 분류가 “모든 작은 오류=FAIL” 또는 “전부 unknown=PASS”로 뒤집히지 않도록 작은 synthetic 사례를 확인한다. 이 도구의 결과는 실제 report 이해도 시험과 별도다.

---

## 16. 최종 판단

현재 S11은 사용성 기반과 추적/증거 구조가 무너진 프로젝트가 아니다. **좋은 구조 위에서, 경계의 물리적 역할에 대한 관측이 약해 잘못된 구조를 충분히 그럴듯하게 추적하는 상태**다. 그 결과가 report의 극값과 episode 요약까지 올라간다.

따라서 다음 목표는 검출률 숫자를 더 높이는 것도, 모든 어려운 장면에 완벽한 분류기를 증명하는 것도 아니다. **잘못된 경계가 중요한 이야기의 주인공이 되는 것을 줄이고, 실제로 보이는 중요한 변화는 남기는 역할 관측**을 만들고 기존 파이프라인에 단계적으로 연결하는 것이다.

이번에 확인한 가장 실용적인 설계 제약은 다음과 같다.

- Anchor-only 수정은 44초 continuation 오류를 놓친다.
- Support=0 veto는 정상 continuation도 제거한다.
- Lower geometry가 존재해도 broad texture opposition으로 역할 근거를 잃을 수 있다.
- 올바른 Foam upper가 raw 단계에 없으면 episode 개선은 선행 과제가 아니다.
- 숫자/trace/CSV의 일치는 물리적 의미와 report 이해도를 대신하지 않는다.

이 제약을 반영한 **관측 계층 부분 재설계 + 제한된 새 표현 challenger + 전체 후보 경쟁 + 독립 Windows/report 종료 판단**이 현재의 권고다. 새로운 모델의 실효성은 아직 미검증이고, FIELD FAIL/O2 OPEN을 유지한다. 그 불확실성을 숨기지 않으면서도, 다음 구현과 최종 종료 판단까지의 경로는 위 work package로 구체화했다.

---

## 근거 색인

Repository 경로는 기준 HEAD의 root-relative 경로다. 긴 문서의 어떤 역할을 확인했는지 함께 적어두었다. 이 색인은 링크 없이도 checkout에서 찾을 수 있게 하기 위한 것으로, 라인 번호나 실행하지 않은 원본을 임의 생성한 인용이 아니다.

| ID | 근거 | 사용 범위 |
|---|---|---|
| E01 | `docs/00-project/work-plan.md`, `roadmap.md`, `execution-policy.md`, `AGENTS.md`, `.agents/skills/s11-detector-change/SKILL.md` | 현재 상태, 범위, routing |
| E02 | `docs/30-validation/s11-interface-observability-witness-validation.md` | P0, A/B/C/U, V2–V5/O2–O4, episode/field gate |
| E03 | `sample/README.md` | source inventory, qualification, sample3 제한 |
| E04 | `docs/20-architecture/s11-current-detector-logic-map.md`; `src/oil_tracker/adapters/vision/oil_observation_resolver.py`, `oil_candidate_authority.py`, `oil_candidate_evidence.py` | current ownership, 실제 peer support/authority 코드 |
| E05 | `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` | 반복 실패와 보존 계약 |
| E06 | `docs/70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-current-default.json`, `sample4-default-summary.json` | default 113 rows, 101/26 numeric, 31 events, 극값 |
| E07 | `docs/50-diagnostics/s11/2026-10-11-p5-default-linkage.md`, 동명 디렉터리 `readout.json` | NONE/FULL, raw Y813 부재/Y833, publication equality |
| E08 | `docs/50-diagnostics/s11/2026-10-10-cadence-owner-causality.md` | established-first assignment, owner restriction, 닫힌 cost-order probe |
| E09 | `docs/50-diagnostics/s11/2026-10-12-p2-row-distributions.md`, 동명 디렉터리 관련 preflight/readout | CDF/mean follow-up, 전체 후보 경쟁의 한계 |
| E10 | `docs/50-diagnostics/s11/2026-10-12-public-compressor-source/position-review/position-review.png`; `pipeline-linkage/{readout.json,storage.json,captures.zip}` | 사용자 Oil/Foam 범위, current/completed/candidate/publication 연결 |
| E11 | `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` | Windows 9구간 canonical story |
| E12 | `docs/60-evidence/s11/2026-10-12-boundary-feasibility-handoff.md` | 최신 closed pilot, retained evidence, 다음 entry 상태 |
| E13 | `docs/20-architecture/s11-interface-observability-witness-architecture.md` | bounded observation redesign/typed witness/consumer 계약 |
| E14 | `docs/50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md` | 9월의 bounded redesign 결론과 당시 public probe 한계 |
| E15 | `docs/70-reference/s11-program-audit-2026-10-11/native-evidence/*-source-sheet.png` | 이번에 직접 본 base/sample2/4/5/6/7 시각 자료 |
| N01 | 이번 `scripts/peer_probe.py`, `evidence/execution-receipt.json`, native `verified-cli/peer-probe.json` | 새 support attribution 재실행 |

### 외부 1차 자료 — 방법 선택의 근거, 압축기 성능 증거가 아님

| ID | 자료 | 반영 / 제한 |
|---|---|---|
| R01 | Oquab et al., **DINOv2: Learning Robust Visual Features without Supervision**, arXiv:2304.07193 (2023); 공식 `facebookresearch/dinov2` README, 2026-10-12 확인 | 고정 visual feature와 patch-level representation 후보. 압축기 role accuracy는 미검증 |
| R02 | Eppel, Xu, Aspuru-Guzik, **Computer vision for liquid samples in hospitals and medical labs using hierarchical image segmentation and relations prediction**, arXiv:2105.01456 (2021) | vessel/material/part/relation 분리. 의료 용기 데이터의 domain transfer 성능을 가정하지 않음 |
| R03 | Eppel, **Tracing liquid level and material boundaries in transparent vessels using the graph cut computer vision approach**, arXiv:1602.00177 (2016) | graph-cut 경계 관측과 top/bottom anchor 가정의 한계 |
| R04 | Narasimhan et al., **Self-supervised Transparent Liquid Segmentation for Robotic Pouring**, arXiv:2203.01538 / ICRA 2022 | 투명 액체 데이터 생성/학습의 장기 후보. 별도 데이터 조건이 있으며 현재 drop-in 해법이 아님 |
