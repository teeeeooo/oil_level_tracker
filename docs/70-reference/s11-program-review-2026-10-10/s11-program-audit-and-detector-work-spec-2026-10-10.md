# S11 프로젝트 전반 검토 및 Detector 설계·작업 명세서

> **검토 기준:** 2026-10-10, `main @ 8fea93f2cfa27c455114d0921bbeacb9f697ad13`  
> **저장소:** `teeeeooo/oil_level_tracker`  
> **문서 성격:** 현재 상태 감사 + 채택 제안. 구현 완료 문서나 새로운 상태 권한 문서가 아니다.  
> **현행 상태:** S11 ACTIVE · R22 behavior / R22-3·O1 diagnostics · O1 로컬 수용 · O2 OPEN / FIELD FAIL · Local XY OFF.

## 1. 결론

**프로젝트를 처음부터 재설계할 필요는 없다. 완성된 분석·검토·출력 체계와 책임 분리는 유지하고, detector 내부의 관측 표현 → 경계 역할 판별 → 추적 소유권 연결을 순서대로 보강하는 것이 타당하다.** 다만 다음 작업을 또 하나의 국소 원인 조사로 끝내서는 안 된다. 각각의 변경이 주요 상승·하강·급격한 재유입·Foam 생성/소멸을 report에서 더 정확히 읽게 만드는지까지 연결해야 한다.

현재 가장 중요한 구분은 다음과 같다.

| 구분 | 이번 검토의 결론 |
|---|---|
| 제품 기반 | Recipe, 분석 실행, 검토, export, 원본 장면 대조 등은 이미 상당 부분 갖춰졌다. S1–S10 완료와 S11 검출 성능 미완료를 구분한다. |
| 최근 진전 | 평가 자료의 적격성, 손실 단계, 좌표 의미와 재현성을 크게 정리했다. 그러나 `cc17924` 이후 현재 HEAD까지 `src/` 변경은 없다. 이 기간의 진전은 채택된 detector 성능 개선이 아니다. |
| 현장 효능 | 현재 기준 FIELD FAIL이다. 로컬 테스트, hash 일치, 후보 개수 증가로 이 상태를 바꿀 수 없다. |
| 핵심 병목 | 보이지 않는 경계를 만드는 문제가 아니라, 보이는 계면에 해당하는 대안을 일찍 잃거나, 남아 있는 대안을 잘못된 역할/추적 ID에 연결하는 문제다. |
| 설계 방향 | 단일 승자 압축을 늦춘 관측 표현, 비교 가능한 구조물 반대 근거, 현재 프레임 근거에 묶인 소유권 연결, Foam 존재와 실제 상단 위치의 분리를 우선한다. |
| 종료 기준 | 프레임별 정답률 100%가 아니라 주요 물리 사건의 방향·순서·존재를 report가 왜곡하지 않는지다. 짧은 잔여 오류와 주요 사건을 뒤집는 오류를 구별한다. |

위 상태 판단은 현재 Work Plan·Roadmap, 실제 Git 비교, 검토 기록에 근거한다. [R01–R04, R06–R15]

**권고:** S11을 “완벽한 경계 판별기를 찾는 연구”가 아니라 “정해진 사용 범위에서 주요 움직임의 해석을 방해하는 detector 실패를 줄이는 개선 프로그램”으로 운영한다. 단, 이를 근거 없는 좌표 보간, truth 맞춤 분기, 허용되지 않은 gate 완화로 바꾸면 안 된다.

## 2. 이번 세션에서 실제로 수행한 일

### 2.1 접근·검증 범위

Mac 로컬 저장소에 직접 접근해 현재 HEAD, 원격과의 일치, 작업 트리, 진행 문서, S11 skill, 실행 정책, 현행 logic map, 실패 registry, 최근 인수인계 및 주요 machine record를 확인했다. 실제 `oil_material_path.py`의 후보 생성·중복 제거·조기 종료 구현도 읽었다. 최신 인과 기록과 해당 코드 책임을 대조했다.

7개 MP4의 존재·hash와 기존 Recipe/truth를 확인했고, source-bound 원본 crop/contact sheet, 후보 대조 이미지, 저장된 최종 report 브라우저 화면을 직접 보았다. 물·맥주·우유 영상의 역할/가시성 대조군, Sample4의 빠른 움직임·후반 Foam·잘못된 rim 선택을 포함한다.

**이번 세션은 새 전체 영상 재생, 새 detector replay 또는 Windows 실행을 하지 않았다.** 원본 영상에 hash로 연결된 기존 프레임 자료와 저장 결과를 검토한 것이다. 새 native-frame 디코드용 초안은 도구 요청 차단 이후 실행하지 않고 `.unexecuted.txt`로 남겼다. 따라서 “영상 전체를 새로 돌려 성능을 검증했다”는 주장을 하지 않는다.

### 2.2 새로 확인한 검증 결과

| 실행 | 이번 결과 | 증명하지 않는 것 |
|---|---:|---|
| 6개 주요 machine record의 파일/hash 연결 검증 | 667/667 일치, 누락 0, 불일치 0 | 물리적 판정의 정확성 |
| corpus 접근 제한·portability·provenance·cadence·sequence integrity 집중 검사 | 55 passed, 1 skipped / 8.49초 | 전체 corpus PASS, detector 효능 |
| material path·Foam support geometry·contour contact·boundary temporal 집중 검사 | 56 passed / 1.77초 | 실제 영상의 새 검출률 |
| 실제 source 차이: `cc17924..HEAD -- src` | 변경 없음 | 모든 과거 출력의 현 HEAD 재생 일치 |
| 검사 전/후 작업 트리 | clean, `main`/`origin/main` 일치 | 전체 canonical/Qt/Windows suite 통과 |

두 pytest 실행의 합계는 **111 passed, 1 skipped**다. 종료 시 소스 226개·미디어 7개·Recipe/truth 8개, 총 241개 파일의 최초 hash가 모두 유지됐고, 현행 HEAD 기준 detector governance와 `git diff --check`도 통과했다. 이 governance 실행은 변경 없는 저장소 범위에 대한 검사이며 전달용 명세서 자체의 CI 통과를 뜻하지 않는다. skip은 Sample3 QUARANTINED 정책에 따른 의도된 미실행이며 PASS로 합산하지 않는다. 같은 소스에 대한 집중 검사일 뿐, 전체 제품 검증이 아니다.

로컬 상세 receipt: `sample/output/s11-program-review-20261010-001/audit_identity.json`  
receipt SHA-256: `8e6c78695e47895058e3e913b9eed75b4a0ffa75bce9168e1d3c2d246222ee76`.

실행 결과 요약은 동봉 `s11-execution-summary-2026-10-10.json`에 있다. 요약 파일은 위 원본 receipt의 byte-identical 복사본이 아니다.

### 2.3 변경하지 않은 것

`src/`, Recipe, `.oiltruth`, 과거 판정, 원본 미디어, 현행 Work Plan/architecture/validation을 수정하지 않았다. commit/push도 하지 않았다. 새 파일은 감사용 ignored 출력과 이 전달 문서뿐이다. 아래 알고리즘과 작업 패키지는 **제안**이며 새 검출 성능으로 보고하지 않는다.

## 3. 프로젝트 전체 진행 상황

| 영역 | 현재 성숙도/상태 | 다음 개발 자원의 배분 |
|---|---|---|
| Recipe·GUI·분석·export·기본 검증 | Roadmap상 S1–S10 완료 | 유지·회귀 방어. 이번 주력 아님 |
| report 해석 지원 | source context와 원본 episode 탐색 도입 | 기존 기능으로 최종 검증. 추가 UI 구축을 선행하지 않음 |
| 관측 provenance | same-frame 후보→sequence→CSV 계약과 진단 수단 확보 | 보존. 추가 진단은 실제 의사결정을 바꿀 때만 |
| O1 관측 추출 | 로컬 수용 | 기존 추출·loader·metric 재사용 |
| O2 물리 역할 판별 | OPEN, 채택된 후속 challenger 없음 | 최우선 핵심 개발 |
| Oil association / phase | 기존 구현은 있으나 실영상 소유권 실패가 남음 | O2 근거와 결합한 제한 변경 후 독립 검증 |
| Foam front / episode | 원시 support와 실제 front 혼동이 확인됨 | Oil과 병행 가능한 별도 경계 측정 축 |
| Windows 사용 범위 검증 | FIELD FAIL, 현 후보의 공식 통과 없음 | 정확한 후보를 묶어 9구간 평가 |
| S11-M·S12 | 계획 단계 | detector 유효 변경 이후 유지보수·필요 UI로 이동 |

**프로젝트 완성도를 하나의 백분율로 제시하지 않는다.** 기능적 완성도는 높아졌지만 사용 목적을 좌우하는 detector의 현장 적합성은 아직 열려 있기 때문이다. “S1–S10 완료”와 “실용적으로 완전히 쓸 수 있다”는 같은 말이 아니다. [R01, R02]

### 3.1 유지할 자산

가장 가치 있는 자산은 버전별 임시 알고리즘의 수가 아니라, 동일 프레임 추적성, 독립적인 Oil/Foam 결과, 실제 사용자 물리 판정, 실패한 메커니즘 기록, 그리고 원본과 report를 비교할 수 있는 실행 체계다. 이를 버리고 전체 파이프라인을 교체하면 이미 막은 오류가 다시 생길 위험이 있다.

### 3.2 운영상 병목

여러 실험에서 “이 특징만으로 물리적 정체성을 증명하지 못한다”는 결론까지는 도달했지만, 그것이 어떤 사용 구간에서 얼마나 해로운 오선택을 줄였는지와 연결되지 않으면 개발이 정체된다. 반대로 몇 개 사례가 좋아졌다는 이유로 재현성·독립성 검사를 생략해도 안 된다.

다음부터는 **표현 보존의 성공, 역할 판별의 성공, 최종 움직임 해석의 성공을 서로 다른 산출물로 평가**한다. 표현 개선에 곧바로 완전한 detector 효능을 요구하지 않고, 표현 개선만으로 제품 성과를 선언하지도 않는다.

## 4. 제품 목적을 실제 평가 규칙으로 바꾸기

### 4.1 최상위 질문

사용자가 최종 report를 보고 다음을 구분할 수 있어야 한다.

- Oil이 내려가는지 올라가는지, 급격한 재유입과 재반전이 언제 일어나는지.
- 경계가 실제로 보이지 않는 FULL/EMPTY 상태인지, 검출기가 관측을 놓친 것인지.
- Foam이 언제 생기고 없어지는지, 상단 Foam과 하단 Oil 경계를 혼동하지 않는지.
- 표시된 높이가 관측값인지, 알려지지 않은 구간인지, 단순한 화면상 연결인지.

이 네 질문을 기존 report와 원본 대조에서 평가한다. 별도의 새 대시보드를 만들어야 평가 가능한 구조로 바꾸지 않는다.

### 4.2 오류의 우선순위 — 채택 제안

| 등급 | 예 | 처리 원칙 |
|---|---|---|
| A: 맥락을 뒤집는 오류 | 하강을 상승으로 표현, Foam 내부 무늬가 Oil이 됨, FULL 구간에 긴 가짜 계면, 실제 Foam 소멸 뒤 지속된 가짜 episode | 해당 주요 구간을 수용하지 않음 |
| B: 맥락을 지우는 오류 | 보이는 주요 하강·재유입이 통째로 누락, 반전 전후를 연결할 근거 부족, 긴 오소유권 고착 | detector 개선의 우선 대상 |
| C: 국소 잔여 오류 | 주요 흐름·극값·재유입·episode 경계의 해석을 바꾸지 않는 짧은 누락/작은 위치 오차 | 길이·위치·영향을 명시하고 사용자 사용 범위 수용 가능 |
| U: 판독 불가 | 초점 불량, 가림, 경계가 영상 밖, 물리 역할/가시성 미확정 | missing/negative/정상 abstention으로 바꾸지 않음 |

이는 현행 gate를 자동 변경하는 규칙이 아니다. **A/B/C 분류를 acceptance 문서에 명시적으로 반영하는 제안**이다. 특히 장면 길이와 사건 속도가 다른데 모든 오류에 같은 허용 시간을 임의로 주지 않는다.

### 4.3 지표의 역할

1. **주요 사건 합치:** 상승/하강/반전/진입/소멸의 순서와 방향. 정확한 pixel truth가 없어도 기존 구간 판정으로 평가할 수 있다.
2. **잘못된 물리 대상의 연속 유지 시간:** 숫자가 매끈한지보다 구조물·잔류물·다른 상을 얼마나 오래 추적했는지가 중요하다.
3. **관측 가능한 동일 Oil 계면의 시간 간격:** 이미 채택된 개발 목표는 실제 source time 기준 최대 1.0초다. 움직임이 별도로 확인된 구간에만 적용한다.
4. **높이·불확실성:** 고정 중앙 X와 선택된 image projection에서 관측한 위치를 비교한다. 부분 역할 판정을 전체 contour truth로 늘리지 않는다.
5. **미판정 비율:** 오검지와 별도로 남긴다. 전부 UNKNOWN이면 오검지 0이어도 효용은 개선되지 않는다.

단순 숫자 출력률은 보조 지표다. 초기 FULL/EMPTY, 가려진 구간까지 출력률 분모에 넣고 숫자를 늘리는 방향으로 최적화하지 않는다. ≤1초 목표도 잘못된 물리 대상의 숫자로 채우면 실패다. [R11, R12]

### 4.4 중요한 비대칭

수백 초 동안의 작은 흔들림과 1.6초의 급격한 재유입은 중요도가 다르다. ≤1초 간격만 만족해도 사건의 시작·방향·종료를 놓칠 수 있다. 급격한 사건은 **진입 전, 가시적 이동, 상단 이탈/후속 무계면 상태**의 관계를 함께 검토한다. 이 때문에 cadence 하나를 최상위 합격률로 삼지 않는다.

## 5. 증거에 근거한 현재 실패 구조

### 5.1 Sample4: 후보가 있는데 소유권 제약 때문에 사라진다

기존 사용자 판정으로 42.5–44.0초는 같은 Oil 계면의 가시적 빠른 움직임이다. 저장된 최종 결과는 다음과 같다. [R06, R11]

| 시각 | 저장된 Oil | 현재 물리 판정 범위 |
|---|---:|---|
| 42.5초 / f1275 | Y835 | 선택 후보가 맞음. 중앙 X595의 검토 범위 rows833–841과 호환 |
| 43초 / f1290 | 없음 | numeric 누락 |
| 43.5초 / f1305 | 없음 | guide② Oil 위치가 후보에 존재하나 최종 소유권에서 제외 |
| 44초 / f1320 | Y822 | 기존 사용자 판정상 잘못된 Oil 대상 |

44초 숫자를 유효한 연속점으로 세면 안 된다. 실제로는 한 개의 지원된 관측 뒤에 1.5초 동안 지원된 결과가 이어지지 않는다. 따라서 현재 결과는 이 구간의 ≤1초 유용성 목표를 보여주지 못한다.

43초의 동일 Y836 행을 두 tracklet이 경쟁한다. 기존 established track의 비용은 0.850825, 다른 track의 비용은 0.010200이지만 established 우선순위가 전자를 선택한다. phase owner는 후자의 과거 ID에 남고, 현재 행의 handoff는 요구된 anchor profile을 충족하지 못한다. 최종 selector는 점수를 매기기 전에 허용 ID에 맞지 않는 행을 모두 제거한다.

**확정되는 원인:** 현재 후보 존재 → 할당 경쟁 → phase owner와 현재 행의 분리 → allowed-owner 필터 손실.  
**확정되지 않는 것:** 이 track 전체가 처음부터 어느 물리 경계였는지, 가장 이른 물리적 오연결 시점, 후보의 모든 sector 좌표가 실제 계면인지.

과거 cost-order-only 실험은 43/43.5초 숫자를 되살렸지만 15개 Oil 행과 19개 phase 행을 바꿨고, 56초에는 상부 무늬 쪽으로 이동했다. **정렬 순서를 전역적으로 바꾸는 수리는 기각된 상태**다. 단순히 “정확한 후보가 있는데 gate가 빡빡하다”로 요약하면 중요한 역회귀를 놓친다.

### 5.2 Water B: 최종 후보 수가 아니라 더 이른 경로 압축이 문제다

B/f1438에서 사용자 확인 upper projection은 source X950, rows484–489다. 기존 first material-path lane은 native 33개 seed/33개 경로에서 6개를 남기고, reduced에서는 12개에서 6개를 남긴다. 그런데 검토 위치와 호환되는 중앙 sector sample은 **최종 top-k 전에도 0개**다. [R07]

저장 profile에는 검토 rows의 유효한 지역 근거가 있고, 기존 band·adjacent-step·polarity 조건을 지키는 5-sector 경로도 존재한다. 그럼에도 `_polarity_path_for_seed`가 seed/polarity당 점수 우승 경로 하나로 압축하면서 해당 대안을 잃는다.

따라서 “top-k를 늘려보자”는 우선 수리가 아니다. 이 사례의 첫 지원된 손실은 **per-seed 최적 경로를 하나만 보존하는 단계**다. 다만 한 lane의 위치 표현 손실이지, 전체 application의 물리 선택 실패율을 측정한 것은 아니다.

### 5.3 C는 B와 다르다

C/f1643의 native lane에는 검토 중앙 범위와 호환되는 경로가 남는다. reduced lane에는 없다. 이 비교만으로 C의 가장 이른 손실을 B와 동일한 원인으로 단정할 수 없다. native 결과만 골라 “해결했다”고 해도 안 된다. 고정된 두 해상도를 모두 유지하면서 입력 축소, profile 구성, path 압축을 구분한다. [R08]

### 5.4 Foam: “거품처럼 보이는 영역”과 “실제 front”를 구분해야 한다

A/f1232는 사용자 확인 Foam 층이고, 상단 위치는 X950 rows476–481이다. 아래쪽 물–Foam 경계는 불명확하다. 검토된 상단 위치에는 Canny edge가 있지만, 기존 절대 밝기 조건 때문에 raw white support가 처음부터 0이다. 해당 위치의 손실은 cleanup이나 episode gate보다 앞선다. [R08, R09]

반대로 Sample4 후반의 기존 Foam front Y833/Y837/Y838은 사용자 판정상 실제 front가 아니라 Foam 내부 texture다. 이를 episode gate가 거절한 것은 “정답 front를 놓쳤다”는 근거가 아니다. Foam이 있다는 사실은 맞더라도 그 후보 위치가 맞다는 뜻은 아니다. [R10]

따라서 Foam 개발은 다음을 독립적으로 다뤄야 한다.

| 질문 | 허용되는 결과 |
|---|---|
| Foam이 있는가? | 존재/부재/불명확 |
| upper Foam–air outline이 가시적인가? | 가시/가림·프레임 밖/불명확 |
| 고정 X에서 위치를 측정할 수 있는가? | 실제 source-coordinate 관측/구간 불확실성/미측정 |
| 동일 front가 시간적으로 이어지는가? | bounded episode 근거/불명확 |

한 질문의 긍정을 다른 질문의 좌표로 대체하지 않는다. Oil 하단이 불명확해도 Foam 상단은 별도로 유효할 수 있다.

### 5.5 CBR-1은 재명명해서 반복할 실험이 아니다

기존 reference-side 비교는 unique Foam 출력 40개가 모두 하단 glass rim Y879/880에 모였고, Oil은 기존 0.5초 분석 간격에서 후속 5개 시점 모두 모호했다. 구조물 대조군은 고정 중앙과 reference X가 달라 비교 자체가 없었다. 이는 “구조물을 잘 거절했다”가 아니다. [R13]

또한 `AB + BA = AA + BB`이므로 AB를 나머지와 비교한 수치가 독립된 여러 물리 증거가 되는 것은 아니다. 같은 side preference를 여러 번 센 셈이다. 새 판별 설계는 이 선형 의존성과 구조물 비교 불가능 문제를 설명해야 한다.

## 6. 데이터 사용 계획

| 자료 | 앞으로의 용도 | 금지하는 해석 |
|---|---|---|
| Windows canonical 9구간 | 대상 사용 환경의 사건·방향·Oil/Foam 역할 평가 | 로컬 원인을 그대로 전이, 미측정 exact Y 생성 |
| Sample4의 확인된 후보·구간 | Oil/구조물/내부 Foam 반대 사례와 가시적 움직임 | sparse 확인을 전체 track 정답으로 확대 |
| 물 A/B/C | Foam upper, no-Foam water upper, 위치 표현의 차이 | 세 frame을 독립 recording/holdout으로 계산 |
| 기울어진 물 f822 | 실제 변형 수면 보호 | slope·큰 움직임을 splash negative로 처리 |
| 맥주 | 동일 thin layer의 앞/뒤 투영, upper가 화면 밖인 경우 | 두 arc를 두 물리 층 또는 두께로 해석 |
| 우유 | 밝은 bulk liquid와 Foam/가시성 분리 | white=Foam, 불명확한 lower를 숫자로 생성 |
| base_sample_1·sample2 | 기존 유효 범위의 회귀·출력 호환성 | 기존 scalar agreement를 새로운 물리 정확도로 표현 |
| Sample3 | 명시적 기존 회귀/engineering compatibility에 한정 | gap 최적화, clip mining, 전체 고정 Recipe 구간의 주 정확도 지표 |

Sample3의 파일을 읽을 수 있다는 사실과 연구·튜닝에 사용해도 된다는 권한은 다르다. 새 source reader도 기존 guard를 호출해야 한다. 필요한 legacy 실행은 해당 명령에만 목적을 지정한다. source를 다른 이름으로 복사하거나 직접 OpenCV 호출로 제한을 우회하지 않는다. [R14, R15]

**새 촬영, Windows 원본 반출, 새로운 대규모 annotation 작업을 선행 조건으로 추가하지 않는다.** 기존 판정으로 가능한 부분을 먼저 개발한다. 다만 아직 없는 물리 역할·독립 holdout을 있는 것처럼 기록할 수는 없다. 기존 자료에서 불가능한 주장은 범위를 축소해 보고한다.

## 7. 전체 설계: 유지할 것과 바꿀 것

### 7.1 유지할 실행 경계

```text
현재 프레임의 실제 영상 근거
  → 후보/경로와 관측 불확실성
  → Oil 역할·authority → tracklet → phase owner → 최종 selector
  → 동일 프레임 Oil projection
  → 독립 Foam candidate/episode와 한 번의 composition
  → CSV / event / report
```

report·truth·과거 출력이 상위 detector의 근거가 되지 않도록 한다. 동일 프레임 후보 Y, sequence raw Y, CSV raw Y의 관계를 유지한다. 새로운 경로 형태를 도입하더라도 publication contract 변경은 별도 승인과 migration 대상이다. [R03, R04]

### 7.2 바꿀 설계 축

**A. 관측 대안 보존:** 물리 역할을 결정하기 전에 중앙 위치가 다른 경로를 하나의 점수 우승 경로로 지우지 않는다.

**B. 역할별 경쟁:** 계면·내부 texture·구조물·동일 수면의 다른 투영을 구분해 비교한다. 여러 상관된 특징을 독립 증거 수로 부풀리지 않는다.

**C. 물리 근거를 가진 현재 행 중심 association:** established ID는 관리 정보이지 현재 물리 정체성의 우선권이 아니다. 다만 이를 cost-first로 뒤집는 대신, 현재 행의 적격한 물리 근거와 명시적 handoff가 실제 선택까지 전달되게 한다.

**D. Foam 경계의 독립 측정:** material support extent와 front 좌표를 분리한다. raw white support가 없거나 component가 내부 texture여도, 별도의 실제 상단 경계 관측 가능성은 보존한다.

변경은 기존 owner 안의 제한적 교체로 한다. 새 전체 segmentation framework, 별도 병렬 detector, ML, 대규모 UI/annotation 시스템은 현재 권고 범위가 아니다.

## 8. 작업 패키지 P0 — 목적·범위와 baseline 고정

**연결:** 기존 D2/D3·W4와 validation의 product cadence 계약. 새 버전 체계를 추가하지 않는다.

한 장의 고정 manifest에 source/run/Glass, 사용 목적, 확인된 역할, 가시성, 원본 시간, 평가 가능한 좌표 범위, 반대 사례, UNKNOWN 범위를 기록한다. 기존 W3 packet/label/source identity 소유자를 재사용한다. legacy scalar와 물리 평가를 같은 필드에 넣지 않는다.

새 trial 전 baseline raw/sequence/report 참조, 실행 소스·설정, 비교 범위, prototype 관측식, 변경 가능한 항목과 종료 조건을 고정한다. 일곱 MP4 전체를 매번 돌릴 필요는 없다. 바뀌는 owner를 검증하는 고정 사례와 이를 해석할 주변 구간을 사용하되, 결과를 본 뒤 불리한 frame을 제외하지 않는다.

**완료 조건:** 기존 질문을 다시 하지 않고 어떤 결과가 이번 변경의 진전인지 판별할 수 있는 비교 계약이 있다. 기본 corpus guard를 유지하며 새로운 gold/holdout을 조작하지 않는다.

## 9. 작업 패키지 P1 — 중앙 위치 조건부 경로 대안 보존

**성격:** 구체적인 표현 개선 설계. 실제 영상에서 새로 실행하거나 채택하지 않았다. 물리 분류기가 아니다.  
**주 owner:** `oil_material_path.py`, 기존 material-path diagnostic sidecar와 saved-profile loader.  
**노드:** `OIL-PROPOSAL`, `OIL-CANDIDATE`, `OIL-PROJECTION`.  
**실패:** F01/F02/F09/F10.

### 9.1 먼저 바꿀 단 하나의 연산

현행 seed/polarity별 단일 최적 경로 대신 **중앙 sector의 각 유효 row를 조건으로 하는 최적 점수와 backpointer**를 보존한다. 모든 seed의 개별 경로를 무제한 나열하거나 production `top_k`를 먼저 늘리는 방식이 아니다.

기존의 유효 node, signed profile, step 제한, seed band, polarity, 점수 정의를 그대로 둔다. 각 기존 seed graph에서 중앙 sector `c`와 유효 row `y`에 대해:

```text
M(seed, polarity, y)
  = 기존 제약을 만족하고 중앙 row=y를 지나는 모든 경로의 최대 기존 점수

출력 = 유효한 y별 score/backpointer/관측 support/원래 seed·polarity lineage
       + 도달 불가능한 y와 그 이유
```

기존 경로 점수가 node/transition 합으로 분해되는 범위는 forward/backward DP를 사용한다. 경로 전체에 의존하는 후처리 점수·적격 조건은 성급히 분해하지 말고 기존 scorer로 확인한다. 작은 synthetic graph의 완전 열거와 반드시 대조한다. **DP가 원래 점수와 동일하다는 것을 먼저 검증한 후** real profile에 적용한다.

이 연산은 중앙 row가 다른 대안을 역할 판별 전까지 남긴다. 어떤 row가 Oil인지는 결정하지 않는다. B의 검토 범위는 결과 비교에만 사용하고 search band, seed, score 또는 retain 조건에 입력하지 않는다.

### 9.2 중요한 범위 제한

- 최초 비교는 현행 seed와 제약을 유지한다. 기울어진 수면의 seed 부재·global band 제한까지 동시에 바꾸지 않는다.
- B의 이미 알려진 압축 손실을 복구하는 것과 f822의 경사 수면 전체를 표현하는 것은 다른 개선이다.
- 초기 출력은 diagnostic sidecar만 사용한다. resolver candidate beam과 기본 동작은 byte/field 동등성을 유지한다.
- 중복 제거는 lineage 보존 후 하며, 같은 median이라는 이유로 서로 다른 중앙 대안을 먼저 지우지 않는다.
- 후보 수·메모리·원래 부적격 대안의 유입을 함께 기록한다. 유효 row 수는 입력 높이로 유한하지만, seed×row backpointer 저장량까지 예산에 포함한다.

### 9.3 중앙 sector sample ≠ 실제 중앙 X의 contour

B/C의 sector는 넓은 X band를 pooling한 것이다. 조건부 경로에 올바른 중앙 row가 포함돼도 그 값이 X950의 실제 edge라는 뜻은 아니다.

따라서 후속 native 중앙 관측은 역할이 식별된 branch에서 **고정 X를 실제로 가로지르는 관측 support만** 사용한다. 같은 수면의 upper image projection 선택은 확정된 측정 규약이지만, 모든 edge 중 최상단을 선택하라는 규칙이 아니다. 중앙 교차가 없으면 측정 불가이며, 옆 column·median·아래 branch로 대신하지 않는다.

### 9.4 비교·완료·기각

B native/reduced에서 기존 profile상 도달 가능한 중앙 대안의 보존 여부를 확인한다. C native의 기존 호환 경로가 유지되는지, C reduced가 여전히 미해결인지 별도로 기록한다. A·기울어진 물·Sample4·구조물 사례는 각자 알려진 범위대로만 평가한다.

**표현 단계 완료:** 원래 적격 그래프의 중앙 대안이 winner compression 때문에 조기에 사라지지 않고, 원래 score·도달 가능성·lineage가 독립 oracle과 일치한다.  
**제품 단계 완료가 아님:** 후보 개수 증가·검토 범위 포함은 물리 identity, O2 PASS 또는 report 개선이 아니다.  
**기각:** truth를 search에 사용, 기존 지원 없는 row 생성, branch 평균, 무제한 memory, 기본 결과 변화가 sidecar와 뒤섞임.

## 10. 작업 패키지 P2 — 비교 가능한 역할·구조물 reference의 공동 경쟁

**성격:** 첫 검증 대상으로 제안하는 제한적 가설. 효능 미검증. 기존 CBR-1, joint geometry, side-strip 실험의 성공 선언이 아니다.  
**연결:** D2/D3 · W4/O2. O3 publication authority가 아니다.

### 10.1 왜 단순한 새 특징 하나를 더하지 않는가

현재 증거는 edge 연결, 두 색 영역, 상대 움직임, 양쪽 strip, 공통 변환 중 어느 하나만으로 계면을 확정할 수 없음을 보여준다. 그러나 “어떤 영상에서도 반례가 없어야 한다”를 실용 검출기의 요구로 삼을 이유도 없다. **정해진 사용 범위에서 주요 false identity와 실제 경계를 경험적으로 구분하고, 구분 불가능한 경우를 남기는가**가 목표다.

새 observable로 제안하는 것은 **동일한 현재 후보의 여러 부분이, 역할이 알려진 계면 reference와 실제 비교 가능한 구조물 reference 중 어느 쪽의 공동 공간 관계를 더 잘 설명하는가**다. CBR-1처럼 양성 쪽만 비교되고 구조물 쪽은 X가 없어 NOT_MEASURED인 상태를 승리로 계산하지 않는다.

### 10.2 고정할 입력과 연산 — 설계 진입 범위

입력은 기존 native crop/mask, 관측된 현재 경계 fragment 또는 정확히 한정된 path support, 이전에 검토된 역할 reference와 source identity다. reference는 전체 pixel 정답 mask가 아니라 **불확실성 범위가 있는 지역 exemplar**로 취급한다. 검토 당시 없는 정확한 contour·component ID·전체 track label을 만들어 넣지 않는다.

첫 prototype은 다음의 **하나의 공동 비교**만 수행한다.

1. 현재 관측 경계의 동일한 support 집합을 양성/구조물/내부 texture 가설 모두에 제공한다. 공통으로 관측되는 영역이 없으면 비교 불가다.
2. 한 reference의 여러 부분을 하나의 제한된 공간 변환으로 현재 support에 등록한다. 각 부분이 제각각 다른 패턴으로 이동하는 자유로운 strip matching을 사용하지 않는다. 변환 종류·공간 범위·parts 정의·sampling은 outcome을 보기 전에 고정한다.
3. 같은 변환 아래에서 관측된 경계 배치와 양쪽 appearance를 함께 읽고, 가설별 residual·가용 support·누락·구조물 반대 근거를 반환한다. 동일 pixels/lineage로 나온 값은 여러 독립 투표로 세지 않는다.
4. 모든 비교 대상에 실제 측정이 있으면 동일 support에서의 상대 우위와 모호성을 계산한다. 양성만 fit 가능하다는 이유나 minimum이 유일하다는 이유만으로 물리 승격하지 않는다.
5. 기존 W3 identity/local/scalar targets에 맞춰 결과를 평가한다. 역할 우위가 있어도 branch/중앙 측정이 불명확하면 높이는 미측정이다.

**P1과 달리 P2는 곧바로 production 구현할 수 있는 확정 알고리즘 명세가 아니라, 실행 여부를 판정할 가설·preflight 명세다. 이 단계에는 아직 고정된 수치 operating point가 없다.** 이를 숨기지 않는다. 코드 작성 전 기존 helper의 수치 규약, reference support 선택, transform capacity, 공통 support 최소 조건, 실제 residual 식을 짧은 preflight로 완성하고 synthetic collision/control을 먼저 확인한다. 결과 후에 transform 자유도·window·threshold를 늘리는 일은 별도 새 가설이지 이번 variant의 보정이 아니다.

### 10.3 기존 실패와 실질적으로 다른 부분

| 과거 방법 | P2에서 검증할 차이 |
|---|---|
| CBR-1의 분리된 side reference 합 | 현재 후보 전체의 동일 support, parts의 공동 등록, 실제 경쟁 가능한 구조물 가설 |
| independent side-strip transport | parts별 독립 이동 대신 하나의 공간 대응 관계 |
| common geometry만 사용 | geometry 적합도를 역할 인증으로 사용하지 않고 양성·반대 exemplar를 함께 비교 |
| optional positive reference만으로 추적 | 반대 설명이 측정되는지 확인하고, negative NOT_MEASURED를 positive로 해석하지 않음 |
| 가까운 edge에 LK를 snap | public 위치는 현재 관측 geometry에서만 취하며 transported 좌표는 correspondence 가설일 뿐 |

이 차이가 실제로 정보를 추가하는지는 미검증이다. 공통 변환과 role 비교의 결합도 coherent optical warp를 이기지 못할 수 있다. 그러므로 **P2는 확정된 해법이 아니라 한 번의 유한한 실험으로 선택/기각할 대상**이다.

### 10.4 반드시 포함할 반증 사례

CBR-1의 f450 하단 rim, f1320 상부 pattern/하부 Oil 경쟁, 기존 rim-jump reference, 고정 pattern optical warp, copied distractor, 움직이지 않는 실제 interface, polarity 변화, 잘린 upper front, 기울어진 실제 물 표면을 보존한다. 이러한 synthetic/실사 대조군은 서로 다른 검증 범위를 가진다.

정지 계면이나 구조 reference가 없는 장면에서 이 신규 비교가 미측정인 것은 허용되지만, 그것을 올바른 rejection으로 세지 않는다. 이후 기본 detector에 연결할 때도 “움직임 또는 reference가 없으면 Oil이 아니다”라는 필수 gate로 만들 수 없다.

### 10.5 실용성·사용자 개입의 경계

기존에 허용된 optional reference와 저장된 검토 자료를 offline에서 먼저 활용한다. 이 명세는 새로운 필수 marker, 프레임별 annotation 또는 촬영 조건을 도입하지 않는다. 실제 필요한 reference의 역할이 기존 자료로 정당화되지 않으면 해당 시험을 비교 불가로 남긴다. 자동 detector 개선과 별도의 “사용자 초기화가 필요한 assisted mode”를 혼동하지 않는다.

P2가 reference 의존 모드에서만 효과가 있으면 그 사실을 명시하고, 이를 기본 자동 detector의 향상으로 발표하지 않는다. 추가 사용자 설정을 요구하는 모드 채택은 별도 제품 결정이다.

### 10.6 종료 조건

한 개의 고정 prototype과 사전에 선언한 한 개의 구조적 ablation까지만 수행한다. 핵심 반대 사례의 의미 있는 오선택 감소와 확인된 Oil/Foam 보호가 함께 나타나지 않거나, 대부분의 결과가 비교 불가라면 **CLOSED WITHOUT PROMOTION**으로 종료한다. 더 많은 비슷한 descriptor를 추가하며 계속 같은 질문을 반복하지 않는다.

반대로 일부 미해결 edge case가 남아도 주요 양성·반대 사례를 개선하고 residual risk가 명확하면 그 범위의 challenger로 다음 gate에 제출할 수 있다. 모든 synthetic optical ambiguity를 현실의 false identity와 동일한 합격 기준으로 묶지 않는다. **확실히 동일한 관측으로 반대 물리 정답을 요구하는 case는 미해결이어야 하지만, 실제 영상 전부를 미해결로 만드는 면제 사유도 아니다.**

## 11. 작업 패키지 P3 — Oil 역할 근거의 association 전달

**연결:** D4a / W5 / O3. 현재 구현·승격 권한을 자동 부여하지 않는다.  
**주 owner:** `oil_candidate_authority.py`, `oil_interface_tracklets.py`, `oil_observation_resolver.py`, immutable `OilFrameDecision` 및 기존 diagnostics.

핵심은 더 가까운 후보나 오래된 ID를 선택하는 것이 아니라, **현재 후보의 독립적인 역할 근거가 실제 할당·허용 owner·최종 출력까지 일관되게 전달되는지**다.

현재 프레임의 관측 적격성 → 역할 모순/불확실성 → predecessor와의 물리 호환성 → bounded association을 구별한다. established 여부는 이 조건을 통과한 후보들 사이의 안정화 정보이지, 더 강한 현재 물리 반대 근거를 덮는 우선권이 아니어야 한다. exact ordering과 margin은 별도 O3 구현 계획에서 결정한다.

**필수 불변식:** 현재 행이 다른 물리 역할이면 과거 ID를 이유로 채택하지 않는다. 타당한 current row를 잃은 owner에 새 좌표/ID를 복사하지 않는다. 두 물리 handoff가 경쟁하면 ambiguity를 남긴다. motion-only/nearby-only 경로가 anchor로 승격되지 않는다.

검증은 f1305 한 frame만 보지 않고 기존 Sample4 전체 saved 0–56초 창의 모든 changed row를 확인한다. 38·42.5·49.5·52초의 보호된 정확 후보, 40·42·44초의 기존 잘못된 후보, 54–56초의 역할 관계를 각각 기존 판정 범위대로 유지한다. “기존 오답이 없어졌다”와 “대체값이 맞다”를 분리한다.

**완료 조건:** 물리적으로 지원된 관측이 ownership 단계에서 불필요하게 사라지는 구간이 줄고, 추가된 행이 주요 잘못된 대상·phase 전환을 만들지 않는다. 42.5–44초의 source-qualified cadence와 전체 창의 changed-row ledger를 함께 제출한다.

## 12. 작업 패키지 P4 — lifecycle/phase는 별도로 수리

**연결:** D4b / W6 / O4. P3와 한꺼번에 gate를 완화하지 않는다.  
**owner:** `oil_phase_lifecycle.py`의 기존 FULL barrier, fill/drain, bounded release/handoff 책임.

다음의 서로 다른 실패를 각각 테스트한다.

| 상황 | 필요한 의미 | 금지할 우회 |
|---|---|---|
| 초기 FULL 후 실제 하강 | 현재의 물리 계면 근거로 barrier release | FULL prior를 좌표로 사용 |
| 초기 EMPTY 후 유입 | 실제 상승 경계의 진입 | lower structure를 유입으로 승인 |
| 충전 중 잠시 owner 상실 | 제한된 current evidence로 재획득 또는 UNKNOWN | 무제한 OPEN 재시작 |
| 충전 후 하강 반전 | 새로운 방향을 현재 근거로 확인 | stale velocity만 반전 근거로 사용 |
| 급격한 재유입 후 상단 이탈 | 계면 상승 뒤 coordinate-free FULL | 아래 rim/잔류물로 추적 대상 이전 |

과거 release window, grace, confirmation count를 일괄 늘리지 않는다. 한 source-bound 인과가 지원하는 transition 하나를 변경하고, 반대 방향·stationary structure·ambiguous handoff·FULL/EMPTY 안전성을 함께 검증한다.

로컬 phase 테스트 통과만으로 Windows 원인을 해결했다고 선언하지 않는다. Windows 구간-level truth는 특정 과거 exact Y와 다르며, 예전 판정과 충돌하면 최신 reviewed truth가 우선한다. [R04, R16]

## 13. 작업 패키지 P5 — Foam 경계 측정과 episode 분리

**연결:** 기존 D5. Oil association을 기다리며 미뤄둘 필요는 없지만 final adoption은 독립 검증한다.  
**owner:** `foam_front_detector.py`, 기존 raw evidence/fragment sidecar, `foam_material_identity.py`, 이후 `foam_episode_resolver.py`.

첫 변경 범위는 **raw appearance component가 실제 upper front를 제공하는지**다. brightness/whiteness는 보조 evidence로 유지하되 유일한 front proposal 조건으로 취급하지 않는 후보 표현을 검토한다. A의 dark Foam upper edge와 Sample4의 좁은 upper gap 양쪽 관측을 보존하고, 그중 어느 것이 역할에 맞는지 P2 수준의 반대 설명과 비교한다.

기존 “component 최상단/최하단”, “bbox gap”, “lower member”, “paired edge가 있다”를 그대로 front로 승격하지 않는다. 실제로 가시적 upper가 없으면 Foam 존재는 남더라도 scalar는 미측정이다. Beer의 프레임 밖 upper를 lower로 바꾸지 않고, milk의 불분명한 lower를 Oil 값으로 채우지 않는다.

**첫 비교에서 episode resolver는 고정한다.** raw front가 옳아졌는지와 episode의 관측 연속성이 적절한지를 분리해야 하기 때문이다. 검토된 실제 upper proposal이 충분히 남는데도 episode 단계에서 의미 있는 구간을 잃는다는 증거가 생긴 뒤에만 episode 변경을 별도 제출한다.

**완료 조건:** Foam 내부 texture/rim을 front로 선택하는 주요 오류를 줄이면서, 확인된 실제 Foam upper 관측을 보존한다. Oil 미관측이 Foam을 자동 거절하지 않으며 Foam mask가 Oil 후보를 지우지 않는다. Foam 존재·가시성·좌표·episode별 결과를 따로 제출한다.

## 14. 기존 계획과의 관계 및 실행 순서

본 문서의 P 번호는 전달용 작업 패키지다. 저장소의 O/W/D 체계를 대체하지 않는다.

| 전달 패키지 | 기존 계획과의 연결 | 출력 | 후속 조건 |
|---|---|---|---|
| P0 목적/평가 범위 | D2/D3 · W4 운영 | 하나의 고정 비교 manifest | 현재 소스·사용 목적·사례가 유효 |
| P1 조건부 경로 보존 | D2/D3 · O1 관측 확장 제안 | trace-only 대안/lineage 비교 | 표현 불변성·resource 검증 |
| P2 역할 공동 경쟁 | D2/D3 · W4/O2 | 한정된 shadow challenger 또는 기각 | 기존 O2 acceptance 필요 |
| P3 Oil association | D4a · W5/O3 | role evidence가 반영된 bounded assignment | 별도 O3 설계·gate |
| P4 lifecycle | D4b · W6/O4 | 근거 있는 한정된 transition 수리 | association과 독립 회귀 |
| P5 Foam front | D5 · FOAM-CANDIDATE/IDENTITY/EPISODE | front identity 개선, 후속 episode 비교 | 독립 Oil/Foam 계약 |
| P6 통합/Windows/report | D6 · W7/O5 | 9구간 전체 결과·맥락 수용 판단 | 정확한 runtime의 승인 |
| P7 S11 종결/정리 | S11 → S11-M/S12 | 남은 한계·유지보수 backlog | 주요 사용 시나리오 수용 |

**권장 의존 관계:** P0 → P1과 P2 준비 → 역할 근거가 있는 P2 challenger → P3 → P4 → P6. P5는 후보/경계 수준에서 병행 설계 가능하며 P6에서 합류한다. 이는 추가 sub-agent나 실제 동시 수정 권고가 아니라 작업 의존성이다.

P1만 성공하고 P2가 실패하면 진전은 “표현 개선 후보”까지다. 이를 detector 완료로 포장하지 않는다. P2가 특정 assisted mode에서만 성공하면 자동 mode의 field 결과와 분리한다. P3가 국소 cadence를 고치고 P4가 주요 FULL/EMPTY 오류를 만들면 통합 후보는 거절한다.

## 15. 구현 변경표

| 대상 | 허용하는 첫 변경 | 동반 검증 | 지금 하지 않을 변경 |
|---|---|---|---|
| `oil_material_path.py` | 기존 score·제약을 보존하는 중앙 조건부 sidecar | 완전 열거 oracle, lineage, 기본 출력 동일 | top-k/threshold/window sweep |
| 기존 material-path/fragment diagnostic owner | 대안 식별·support·source mapping 보존 | native/reduced·pixel centre·missing support | 새 별도 파일 loader/framework |
| `s11_boundary_temporal_probe.py` 및 기존 reference helper | P2의 명시적 공동 비교 한 개 | 실제 comparable opposition, shared support, copied/warp controls | CBR-1 stencil만 바꿔 재시험 |
| `oil_candidate_authority.py` / `oil_interface_tracklets.py` | 승인된 역할 근거 전달, bounded assignment | 모든 changed row·현재 후보·ID chain | 전역 cost-first·maturity 삭제 |
| `oil_phase_lifecycle.py` | 지원된 transition 하나 | FULL/EMPTY·반대 방향·모호성 | 모든 release/handoff 동시 완화 |
| `foam_front_detector.py` | material support와 actual front 후보 분리 | A dark Foam, no-Foam B/C, internal texture, cropped upper | white/chromatic mask union으로 front 확정 |
| `foam_episode_resolver.py` | raw front 개선 뒤 증명된 손실만 | 실제 상단 후보의 episode 유지·false episode | 원시 오답을 살리기 위한 조기 gate 완화 |
| report/CSV | 원칙적으로 변경 없음 | 기존 최종 값·표시·원본 대조 | 보간·스무딩으로 detector 숫자 수선 |

표에 제시한 파일명은 현행 소유자다. 새로운 API/schema/production wiring이 필요해지면 해당 architecture·validation·logic map을 같은 변경에서 갱신한다. sidecar를 만들었다는 이유로 resolver가 자동 소비하게 하지 않는다.

## 16. P6 — Windows 9구간 검증과 report 수용

기존 reviewed truth는 interval 행동과 물리 역할에 관한 권한이다. source file hash는 다음 실제 Windows 접근 때 read-only로 보강하되, 이 작업만을 위해 지금 사용자에게 원본/PNG/ZIP을 요청하지 않는다. [R16]

| 필수 Segment ID | 구간(source s) | report에서 이해돼야 할 것 | 대표 거절 사유 |
|---|---|---|---|
| WS1-BASE-FULL-PREFIX | 480–약550 | 가득 차 있지만 보이는 경계 없음 | Oil/Foam 가짜 경계 지속 |
| WS1-BASE-DRAIN | 약550–662 | Oil–air 계면이 나타나 내려감 | 중요한 하강 누락·구조물로 이전 |
| WS1-BASE-RAPID-REFILL | 662–약663.6 | 빠르게 올라가 상단으로 사라짐 | 하강으로 오해·상단 이탈 뒤 낮은 행 추적 |
| WS1-BASE-FULL-SUFFIX | 약663.6–780 | 다시 가득 찬 무계면 상태 | 아래 반사/구조물에 숫자 지속 |
| WS1-ACCUM-EMPTY | 480–약653 | 초기 비어 있음 | 구조물을 Oil/Foam으로 표시 |
| WS1-ACCUM-ENTRY-SPLASH | 약653–672 | Oil 유입·상승, 아직 Foam 없음 | splash/벽 흔적이 Oil owner 또는 Foam |
| WS1-ACCUM-FOAM-LAYERED | 약672–680 | 위 Foam과 아래 Oil 경계 분리 | Foam 상단을 Oil로 추적·둘 중 주요 층 소실 |
| WS1-ACCUM-POST-FOAM | 약680–700 | Foam 사라지고 Oil은 보임 | Foam 잔류 episode·Oil 소실 |
| WS1-ACCUM-DRAIN | 약700–780 | 반전 후 Oil 하강, 벽 잔류물과 구별 | owner lock·잔류물 추적·가짜 Foam |

각 행은 실제 sampling 범위, final Oil/Foam 숫자와 연속 구간, source-Y 범위·방향, longest missing/wrong run, owner/phase 변화, PASS/FAIL/NOT_EVALUATED를 모두 가진다. BASE Foam은 전 구간 부재, Accum Foam은 검토된 layered 구간에만 존재한다.

### 16.1 정답률 대신 판정하는 방법

검토자는 먼저 후보 버전명을 가리지 않아도 되는 source truth와 report를 대조해 사건의 방향·순서·존재를 확인한다. 공정한 A/B 사용성 비교를 할 때는 가능한 범위에서 변경 버전의 기대 결과를 먼저 설명하지 않는다. 자동 출력 자체로 정답을 정의하지 않는다.

exact Y가 없는 구간은 좌표 오차율을 만들지 않고, 행동·역할·최장 잘못된 run과 미관측 영향을 평가한다. C 등급의 잔여 오류는 목록으로 남기고 사용 범위 수용 여부를 명시한다. A/B 등급 오류는 다른 구간의 높은 숫자 출력률로 상쇄하지 않는다.

### 16.2 사용자 Windows 작업 부담 줄이기

새로운 미세 descriptor마다 Windows 재실행을 요청하지 않는다. 로컬에서 첫 비교·반증·resource·회귀를 끝낸 후보만 전달한다. shadow와 behavior 검증은 현재 gate의 순서와 승인 조건을 지키되, manifest·runner·요약 형식을 미리 통일한다. gate를 건너뛰기 위해 shadow와 behavior 결과를 하나의 PASS로 합치지 않는다.

허용된 numeric/decision report만 반출하고 private 영상/이미지는 업무 PC에 남긴다. 특정 구간에서 새 물리 판단이 실제로 필요한 경우에만 그 질문을 묶어 요청한다. 현재 닫힌 A/B/C·Sample4·Sample3 질문을 다시 열지 않는다.

## 17. 실험 예산과 실패 종료 규칙

실험의 종료는 “더 할 수 없어서”가 아니라 사전에 정한 비교가 어떤 결정을 지원했는지로 정한다.

| 단계 | 예산 제안 | 종료 산출물 |
|---|---|---|
| P1 표현 prototype | 기존 고정 native/reduced 한 쌍·원래 적격 조건 | 보존/손실 위치·자원·기본 동작 동일 여부 |
| P2 역할 prototype | 하나의 고정 방식 + 사전 선언된 한 ablation | 핵심 양성/반대 사례 변화 및 비교 불가 비율 |
| P3 association | 동일 saved 전체 창의 baseline/candidate | 모든 changed row·ID·phase 비교 |
| P4/P5 behavior | owner 하나씩 변경 | 좋은 관측 보존과 나쁜 관측 제거의 동시 검증 |
| P6 | gate를 통과한 정확한 후보 | 9구간 전체·사용성·성능·잔여 한계 |

새 trial을 열기 전 이전 방식과 다른 입력 정보 또는 결합 관계를 한 문장으로 설명할 수 있어야 한다. 설명이 “threshold/window/이웃 frame을 더 늘렸다”뿐이면 F10 회귀 위험으로 우선 기각한다.

다만 이 규칙을 “모든 물리 상황에 대한 새로운 증명 없이는 구현 불가”로 사용하지 않는다. 성능 주장의 범위를 제한한 실용 challenger는 경험적 검증 대상으로 적법하다. 명확한 ambiguous control을 UNKNOWN으로 남기는 것과 모든 실제 입력을 UNKNOWN으로 만들고 안전하다고 하는 것은 다르다.

## 18. S11을 언제 끝낼 것인가

**종결 제안:** 다음 다섯 조건을 만족하면 detector 검출률 100%가 아니어도 S11의 목적 중심 종결을 검토한다.

1. canonical 주요 구간에서 Oil 이동 방향·주요 반전·FULL/EMPTY·Foam 생성/소멸의 해석을 바꾸는 A/B 등급 오류가 해소되거나 명시적으로 수용 범위 밖으로 정의돼 있다. 실패 사례를 숨겨 범위를 사후 축소하지 않는다.
2. 채택한 가시적 이동 구간에서 supported cadence를 평가했고, 미달·판독 불가·짧은 잔여 오류를 각각 설명한다. “0개 pair”를 합격으로 계산하지 않는다.
3. same-frame provenance, 독립 Oil/Foam, no carry/interpolation, FULL/EMPTY 안전성, runtime 재현성이 유지된다.
4. 실제 업무 PC에서 정확한 후보의 성능·실행 부담·report 대조가 수용됐다. 로컬 PASS만으로 끝내지 않는다.
5. 미해결 C/U 항목은 일반 detector의 범위·주의사항·후속 backlog로 남아 있고, 사용자가 report에서 무엇을 믿을 수 있는지 알 수 있다.

이는 모든 canonical frame의 완벽한 정답 요구가 아니다. 또한 현재 FIELD FAIL을 임의로 바꾸는 선언도 아니다. **제품 범위 수용과 detector field acceptance를 문서상 명확히 기록하는 절차**가 필요하다.

### 18.1 데이터가 모두 노출된 경우의 정직한 한계

현재 공개·로컬 평가 자료는 대부분 이미 개발에 노출됐다. 이를 random frame split으로 untouched holdout처럼 만들 수 없다. 현행 O2의 holdout 요구는 그대로 적용하고, 충족되지 않은 항목은 NOT_EVALUATED로 남긴다.

새 촬영 불가 상황에서 기존 자료의 한정된 사용 범위 검증과 더 넓은 일반화 주장을 구분하는 것은 가능하다. 필요하면 이 구분을 validation의 명시적인 product-scope 결정으로 제안하되, **완료를 위해 몰래 gate를 완화하거나 이미 본 자료를 미관측 자료로 이름만 바꾸지 않는다.** 이번 명세는 해당 acceptance 변경을 수행하지 않았다.

### 18.2 종결 이후

S11-M은 실제 채택된 경로와 불변식을 중심으로 테스트·진단·문서의 중복을 정리한다. 실패한 실험의 evidence는 보존하되 정상 실행 경로와 섞지 않는다. Work Plan의 오래된 경과는 적절한 evidence/archive로 옮기고 현재 상태·다음 작업·gate만 남긴다. 이 문서 정리를 detector 작업의 선행 프로젝트로 만들지 않는다.

S12는 사용자 검토 과정에서 실제 남은 불편만 다룬다. 이미 구축된 원본 대조 기능 위에 또 다른 우회 설명 UI를 만들어 detector 오류를 감추지 않는다.

## 19. 연구 참고와 채택하지 않는 대안

투명 용기 경계 연구에는 용기 형상을 이용한 가능한 경로 탐색, 경계 주변 intensity/edge/gradient 평가, 최단 경로와 graph cut 접근이 존재한다. 이 문서에서는 해당 논문의 초록·방법 설명을 확인했으며, 원 데이터나 성능 수치를 재현하지 않았다. [X01–X03]

이 연구들은 **경계 후보를 하나의 행 점수가 아니라 경로로 다룰 근거**를 제공한다. 그러나 유리 무늬·앞뒤 투영·초기 FULL·Oil/Foam의 물리 역할을 이 프로젝트에서 자동으로 해결했다는 증거가 아니다. 특히 위쪽 10%를 air, 아래쪽 10%를 material로 가정하는 graph-cut 초기화는 현재 FULL/EMPTY·cropped upper 조건과 충돌할 수 있다. 그대로 이식하지 않는다.

따라서 외부 패키지 교체, 전체 segmentation 재설계, deep learning 도입을 지금의 기본 처방으로 제안하지 않는다. 먼저 이미 밝혀진 표현 손실과 비교 불가능한 역할 경쟁을 제한적으로 수정하는 편이 문제와 변경 효과의 연결이 명확하다.

## 20. 채택 절차와 rollback

이 명세를 실행 계획으로 채택할 때는 Work Plan에 P0/P1/P2의 기존 D/W/O 연결과 다음 고정 실험을 간단히 등록한다. 변경할 architecture/validation owner에 제안된 계약을 반영하고, 실제 실행 route가 바뀔 때만 logic map을 수정한다.

각 behavior 변경은 하나의 독립 commit/검증 단위로 나눈다. baseline, variant, 설정, runtime fingerprint, 모든 changed row, negative/unknown 결과, resource 정보를 같은 manifest에 묶는다. 실패 시 variant만 비활성화/되돌리고 원래 판정·영상·결과 파일은 보존한다. Local XY는 OFF를 유지한다.

source 변경이 생기면 해당 source의 집중 검사 후 canonical non-Qt/Qt 및 필요한 corpus replay를 현행 정책대로 수행한다. Sample3가 필요한 기존 호환 검사만 명시적 목적 wrapper를 쓴다. defaults에 전역 허용 환경변수를 추가하지 않는다.

## 21. 기존 문서와의 권한 관계

| 문서 | 관계 |
|---|---|
| `docs/00-project/work-plan.md` | 현행 상태·실행 순서의 유일한 권한. 본 문서는 이 HEAD에 대한 제안 snapshot |
| `docs/00-project/roadmap.md` | 프로젝트 phase/S 단계 권한. P 번호로 대체하지 않음 |
| 현행 logic map / failure registry | 실제 실행 owner와 재발 금지 교훈. 현재 구현을 새 제안과 혼동하지 않음 |
| interface-observability architecture/validation | O1–O5, role/target/중앙 scalar/cadence/자료 사용 gate를 보존 |
| Windows reviewed truth | canonical 행동·물리 역할 권한. 과거 exact Y/출력 개수보다 우선 |
| 최근 10/10 진단·인수인계 | 닫힌 원인·질문·실험 결과. 이번 설계의 입력이지 덮어쓸 대상 아님 |
| 이전 10/07–10/09 전달 명세 | 당시 snapshot 보존. 현재 Work Plan에 없는 이전 즉시 실행 항목은 자동 재개하지 않음 |
| 이 문서 | 프로젝트 전체 우선순위·설계·작업 패키지·종결 제안. 코드 채택/field PASS 증거 아님 |

## 22. History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PROPOSAL`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F01`, `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: early winner/authority collapse, material-path seed/polarity compression, local/native/reduced geometry, motion/bootstrap identity, established-first assignment and failed cost-order counterfactual, phase owner loss, dark-Foam support absence, internal front misidentification, Local XY, independent strip transport, common-geometry/reference feasibility, CBR-1 loss identity, Sample3 source retirement.
- Prior mechanisms rejected: blanket top-k or threshold/window expansion, global cost-first assignment, white/chromatic mask union as identity, raw-edge closure, nearest-edge snapping, motion/common geometry alone as identity, unavailable negative control as successful rejection, Sample3 gap tuning, coordinate interpolation/carry, private source/time/Y branches, mandatory new acquisition and ML redesign.
- Preserved contracts: same-frame provenance, independent Oil/Foam validity, bounded owners, explicit missing/ambiguous evidence, current scalar projection scope, no truth-to-runtime leakage, corpus purpose guard, unchanged historical evidence, current O2/O3/field gates.
- Difference from prior failures: P1 preserves centre-conditioned alternatives without claiming identity or changing the production beam; P2 requires genuinely comparable positive/opposing references over shared current support and joint spatial correspondence rather than treating separable side losses as independent certificates; P3/P4 follow qualified current evidence instead of loosening ownership/phase to fill numeric gaps; product acceptance explicitly distinguishes local residual error from destruction of movement context.
- Logic-map impact: NONE — this is an unimplemented design proposal; no executing owner, API, control flow or projection changed in this session.
- Failure-registry impact: NONE — existing mechanisms and no-repeat rules cover the findings; no new successful physical classifier or new failure class is asserted.

## 23. Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: B isolated material-path lane loses reviewed-position compatibility in per-seed/polarity winner compression; A isolated Foam upper support is absent at initial brightness-dependent raw support; Sample4 f1305 Oil location is excluded by final owner restriction with assignment/handoff contributors already traced. C reduced earliest loss and the earliest whole-track physical identity error remain unqualified. These local findings do not establish the current private Windows first harmful stage.
- Logic-map impact: NONE — only read-only audit and focused tests ran; no production route changed.
- Failure-registry impact: NONE — this report reuses existing causal evidence and explicitly preserves uncertainty and field failure.

## 24. 근거 인덱스

아래 R 항목은 특별한 표시가 없으면 검토 HEAD의 repository-relative path다. 문서의 오래된 pending 문구보다 후속 source-bound reply와 Work Plan의 현재 판정을 우선했다. 이미지에 당시 “unreviewed”가 적혀 있어도 이후 reply가 확인한 범위를 별도로 적용했다.

| ID | 원문·근거 |
|---|---|
| R01 | `docs/00-project/work-plan.md` — 현행 상태, O/W/D 흐름, 닫힌 실험, 다음 허용 범위 |
| R02 | `docs/00-project/roadmap.md` — S1–S10 완료, S11 ACTIVE, 후속 S11-M/S12 |
| R03 | `docs/20-architecture/s11-current-detector-logic-map.md` — 전체 index와 실제 owner 상세, R22/O1 추가 경계 |
| R04 | `docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md` — F01–F10 전체 |
| R05 | `src/oil_tracker/adapters/vision/oil_material_path.py` — 생성 함수, 5-sector profile, seed/path, median 기반 dedup, top-k 조기 종료 |
| R06 | `docs/50-diagnostics/s11/2026-10-10-cadence-owner-causality.md` 및 `.json.gz` |
| R07 | `docs/50-diagnostics/s11/2026-10-10-b-material-path-interval.md` 및 `.json` |
| R08 | `docs/50-diagnostics/s11/2026-10-10-abc-source-interval-comparison.md` 및 `.json` |
| R09 | `docs/50-diagnostics/s11/2026-10-10-water-foam-representation.md` 및 `.json` |
| R10 | `docs/50-diagnostics/s11/2026-10-09-local-xy-sequence-causality.md`, registry F07의 후속 증거 링크들 |
| R11 | `docs/60-evidence/s11/2026-10-10-oil-observation-cadence.md` |
| R12 | `docs/30-validation/s11-interface-observability-witness-validation.md`, V3/cadence/V4/V5/O2/O3/field 및 corpus 계약 |
| R13 | `docs/50-diagnostics/s11/2026-10-10-current-boundary-reference.md` 및 하위 preflight/readout/verification |
| R14 | `docs/60-evidence/s11/2026-10-10-sample3-retirement-handoff.md` |
| R15 | `tests/diagnostics/s11_corpus_access.py` 및 이번 corpus 집중 테스트 결과 |
| R16 | `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` — 9구간/좌표·역할/기존 오해 정정 |
| R17 | `docs/50-diagnostics/s11/2026-10-09-public-scene-controls.md` 및 후속 water/beer/milk 역할 reply |
| R18 | `docs/50-diagnostics/s11/2026-10-10-sample4-center-interval-comparison.md` 및 `.json` |
| R19 | `docs/20-architecture/s11-interface-observability-witness-architecture.md` — region competition, fixed-centre, upper projection, reference/CBR 및 retired source 계약 |
| R20 | `docs/30-validation/s11-detector-change-governance.md`, `.agents/skills/s11-detector-change/SKILL.md`, `AGENTS.md` |
| R21 | `sample/output/s11-program-review-20261010-001/audit_identity.json` — 이번 새 hash/Git 검증 receipt |
| R22 | `sample/output/s11-episode-texture-20261008-001/`의 base/sample2/sample4 최종 report 브라우저 캡처 — 저장된 UI/원본 대조 화면, 새 실행 아님 |

### 직접 확인한 영상 증거 화면

`2026-10-10-upper-projection-ac-review.png`, `2026-10-10-upper-projection-reference-review.png`, `2026-10-10-cadence-gap-source-review.png`, `2026-10-10-sample4-center-source-review.png`, `2026-10-09-local-xy-foam-front-review.png`, CBR-1의 `foam-positive-review.png`/`oil-positive-review.png`, public scene controls의 water/beer/milk source sheet를 직접 검토했다. reference 그림은 질문 당시 표시를 포함하므로 후속 reply와 결합해 읽었다.

### 외부 1차 참고 문헌

- **X01.** Sagi Eppel, Tal Kachman. *Computer vision-based recognition of liquid surfaces and phase boundaries in transparent vessels, with emphasis on chemistry applications*. `arXiv:1404.7174`, 2014. 용기 윤곽과 가능한 경로, intensity/edge/gradient 주변 정보. 초록 확인.
- **X02.** Sagi Eppel. *Tracing the boundaries of materials in transparent vessels using computer vision*. `arXiv:1501.04691`, 2015. 용기 윤곽에 끝점을 둔 곡선과 Dijkstra 기반 boundary 탐색. 초록 확인.
- **X03.** Sagi Eppel. *Tracing liquid level and material boundaries in transparent vessels using the graph cut computer vision approach*. `arXiv:1602.00177`, 2016. top/bottom 10% seed 가정과 graph cut. 초록 확인.

논문의 일반적 방법 설명을 이 프로젝트의 성능 보증이나 새 실험 결과로 사용하지 않았다.

---

**최종 권고:** 관측 표현과 역할 판별을 먼저 개선하되 그 성과를 Oil/Foam의 주요 사건 복구까지 연결한다. 이미 닫힌 Sample3·Local XY·CBR-1을 반복하지 않는다. 동시에 모든 frame의 완벽한 물리 판정을 S11 종료 조건으로 삼지 않는다. 이번 산출물은 그 전체 경로와 검증·기각·종결 기준을 정한 설계이며, detector 개선의 구현 완료 보고는 아니다.
