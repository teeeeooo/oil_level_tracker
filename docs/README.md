# Documentation Map and Authority

This file is the **documentation-routing SSOT**. It classifies documents and points to current owners; it does not duplicate project history or task execution policy.

Read this router when creating, moving, renaming, archiving, or changing document ownership, or when the correct owner/location is unclear. Editing an already-known owner does not require rereading this file merely because the path is under `docs/`.

폴더별 파일 탐색은 [최초 Git 등록일순 색인](catalog-by-created-date.md)을 사용합니다.
색인은 탐색용 파생 자료이며 현재 상태나 권한을 소유하지 않습니다.

## Fresh reading path

Read only the smallest set needed for the task:

1. If current state/authorization matters, read [`00-project/work-plan.md`](00-project/work-plan.md).
2. If broader milestone order matters, read [`00-project/roadmap.md`](00-project/roadmap.md).
3. Read the relevant durable owner under [`10-product/`](10-product/) or [`20-architecture/`](20-architecture/) and the applicable acceptance contract under [`30-validation/`](30-validation/).
4. Use [`00-project/recall-index.md`](00-project/recall-index.md) only for past-dependent work or unclear prior rationale.
5. Use [`40-operations/`](40-operations/), [`50-diagnostics/`](50-diagnostics/), [`60-evidence/`](60-evidence/), and [`70-reference/`](70-reference/) only when the task needs procedure, causal detail, completed proof, or external provenance.

The stable product specification is [`rotary_oil_level_tracker_ssot_spec.md`](rotary_oil_level_tracker_ssot_spec.md). Repository execution state and verification semantics are owned by [`00-project/execution-policy.md`](00-project/execution-policy.md).

## Directory taxonomy

| Directory | Responsibility | Authority boundary |
|---|---|---|
| `00-project/` | roadmap, current work, execution policy, compact recall routing, retained/deferred routing | project sequence/current gate; not feature design history |
| `10-product/` | user-facing/product contracts | durable behavior and UX intent |
| `20-architecture/` | durable responsibility/design contracts | accepted ownership/invariants; not execution chronology |
| `30-validation/` | validation, benchmark and test-acceptance contracts | what must be demonstrated for acceptance |
| `40-operations/` | executable Windows/package/manual procedures | how to perform operational checks; not proof they passed |
| `50-diagnostics/` | investigations, probes and machine manifests | causal/reproducibility support; never current gate authority |
| `60-evidence/` | completed implementation/audit/validation records | historical proof; contemporaneous status does not become current authority |
| `70-reference/` | external/reference provenance | supporting provenance only |
| `90-archive/` | superseded historical context | not current authority |

## Authority hierarchy

When documents disagree, use the owner for the responsibility in question:

1. stable product requirements — [`rotary_oil_level_tracker_ssot_spec.md`](rotary_oil_level_tracker_ssot_spec.md);
2. milestone order/state — [`00-project/roadmap.md`](00-project/roadmap.md);
3. exact active gate — [`00-project/work-plan.md`](00-project/work-plan.md);
4. repository execution/verification/publication semantics — [`00-project/execution-policy.md`](00-project/execution-policy.md);
5. retained non-current commitments — [`00-project/retained-commitments.md`](00-project/retained-commitments.md);
6. relevant durable product/architecture owner;
7. current validation contract;
8. operational procedure;
9. diagnostics/evidence/reference as supporting provenance;
10. archive only for historical context.

Historical status, old next-action prose, prior branch results, and old milestone labels never override current owners.

## Update rules

- Current status, gate, blockers, or next transition → `00-project/work-plan.md`.
- Milestone order, formal state, or milestone scope → `00-project/roadmap.md`.
- Retained/deferred/evidence-gated but non-current work → `00-project/retained-commitments.md`.
- Execution, verification, freeze, publication, or closeout semantics → `00-project/execution-policy.md`.
- Durable product/architecture behavior → owning `10-product/` or `20-architecture/` contract.
- Acceptance obligation → `30-validation/`; completed measurements/results → `60-evidence/`.
- Operational procedure → `40-operations/`; investigation/probe → `50-diagnostics/`.
- Superseded material → `90-archive/` only after proving every still-current contract has another active owner.

Do not copy current status into architecture, diagnostics, or evidence merely for convenience. Do not rewrite historical evidence to sound current.

## Current S11 routing

S11 remains the active detector-effectiveness milestone. Current state and authorization are owned only by the [Work Plan](00-project/work-plan.md).

For an S11 detector change, use the repository-local `s11-detector-change` Skill. It performs bounded routing through the current implementation map, relevant failure history, current architecture/validation, and the mechanical governance contract.

Current durable S11 owners:

- detector responsibilities — [`20-architecture/s11-detector-responsibility-architecture.md`](20-architecture/s11-detector-responsibility-architecture.md);
- current executing control-flow map — [`20-architecture/s11-current-detector-logic-map.md`](20-architecture/s11-current-detector-logic-map.md);
- predecessor R21 truth-preserving detector repair architecture — [`20-architecture/s11-r21-truth-preserving-detector-repair-architecture.md`](20-architecture/s11-r21-truth-preserving-detector-repair-architecture.md);
- predecessor R21 validation/work specification — [`30-validation/s11-r21-truth-preserving-detector-repair-validation.md`](30-validation/s11-r21-truth-preserving-detector-repair-validation.md);
- current R22 Oil ownership/evidence replacement design — [`20-architecture/s11-r22-oil-ownership-evidence-replacement-architecture.md`](20-architecture/s11-r22-oil-ownership-evidence-replacement-architecture.md);
- current R22 acceptance contract — [`30-validation/s11-r22-oil-ownership-evidence-replacement-validation.md`](30-validation/s11-r22-oil-ownership-evidence-replacement-validation.md);
- diagnostic-only native path contract over R22 behavior — [`20-architecture/s11-r22-2-interface-path-diagnostics-architecture.md`](20-architecture/s11-r22-2-interface-path-diagnostics-architecture.md);
- transparent-interface redesign decision and public baseline probe — [`50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md`](50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md);
- O1 trace-only observation-layer contract — [`20-architecture/s11-interface-observability-witness-architecture.md`](20-architecture/s11-interface-observability-witness-architecture.md);
- O2 local label/freeze/evaluation procedure — [`40-operations/s11-o2-local-shadow-evaluation.md`](40-operations/s11-o2-local-shadow-evaluation.md);
- trace/shadow acceptance contract — [`30-validation/s11-interface-observability-witness-validation.md`](30-validation/s11-interface-observability-witness-validation.md);
- broader proposed physical-interface behavior repair — [`20-architecture/s11-physical-interface-evidence-repair-design.md`](20-architecture/s11-physical-interface-evidence-repair-design.md);
- proposed behavior acceptance contract — [`30-validation/s11-physical-interface-evidence-repair-validation.md`](30-validation/s11-physical-interface-evidence-repair-validation.md);
- sequential native path measurement procedure — [`40-operations/s11-r22-2-windows-interface-measurement.md`](40-operations/s11-r22-2-windows-interface-measurement.md);
- durable causal failure history — [`50-diagnostics/s11/s11-detector-mechanism-failure-registry.md`](50-diagnostics/s11/s11-detector-mechanism-failure-registry.md);
- canonical private-Windows reviewed truth — [`30-validation/windows-sample1-heating-coldstart-reviewed-truth.md`](30-validation/windows-sample1-heating-coldstart-reviewed-truth.md);
- current-candidate target-Windows field procedure — [`40-operations/s11-current-windows-field-qualification.md`](40-operations/s11-current-windows-field-qualification.md);
- general Windows GUI/package checklist — [`40-operations/manual-gui-windows-checklist.md`](40-operations/manual-gui-windows-checklist.md);
- completed S11 evidence collection — [`60-evidence/s11/`](60-evidence/s11/).

R18–R20 predecessor architecture/validation and earlier diagnostics remain historical provenance. They are reachable through the current logic map, failure registry, evidence collection, and Git history; this router does not enumerate them.

## S11 audit specifications and execution routing

The supplemental specifications form a sequence of design rationale and
follow-up audits, not competing current authorities:

| Document | Role | How to use it |
|---|---|---|
| [2026-09-17 execution review](50-diagnostics/s11/s11-observation-redesign-execution-review.md) | Grounds the bounded observation redesign and O1–O5 sequence against `577f98a` | Preserve design rationale and constraints; use the current architecture/validation for actual implementation |
| [2026-10-01 audit/work specification](50-diagnostics/s11/s11-detector-improvement-audit-and-work-spec-2026-10-01.md) | Audits progress at `85a01cd`, identifies target/pooling risks and proposes W0–W7 | Use its named work items through the current work-plan ledger; do not treat its dated pending/completion prose as live status |
| [2026-10-01 W4 progress audit](50-diagnostics/s11/s11-w4-progress-audit-and-continuation-plan-2026-10-01-ba1bd6a.md) | Audits `ba1bd6a` and proposes W4-R0–R5 continuation within W4 | Addendum to the prior specifications; preserve the original audit and use the live ledger for the active substep |

The three 2026-10-07 supplied audits and their machine summaries are preserved
byte-for-byte as [external source material](70-reference/s11-audit-2026-10-07/import-manifest.json).
The [adoption checkpoint](60-evidence/s11/2026-10-07-audit-adoption-checkpoint.md)
records the actual checkout integration and validation. The second audit refines
the first; A0B/A0Q/A1–A4 are bounded work within W4, not new milestones. The
[third audit](70-reference/s11-audit-2026-10-07/s11-third-audit-report-context-work-spec-2026-10-07.md)
supplies the original report prototype and prioritizes source/report movement
context. The [report adoption record](60-evidence/s11/2026-10-07-report-context-adoption.md)
identifies the subset subsequently implemented. Its two-second display cap is
still a proposal; current report and
detector acceptance owners remain authoritative. Recovery ZIPs preserve all
three inspected worktrees' unadopted source changes; full local snapshots and
native evidence are located by the checkpoint and its preservation receipt. Their
historical “main unchanged” statements remain true of the audit, while the Work
Plan owns current adoption and next work. Rejected experimental scripts stay in
the preserved ZIP, outside production and test discovery.

The W4 attachment is preserved byte-for-byte under the filename above; only the
transfer prefix and trailing `-1` were removed. W4-R0–R5 are internal continuation
steps, not a new milestone or a replacement acceptance contract.

The September attachment named
`s11-detector-redesign-review-and-execution-spec-2026-09-17-1.md`
was retained under `s11-observation-redesign-execution-review.md`.
The October filename is retained. Neither source audit is rewritten as work
progresses. October supplements September's direction; it does not restart O1
or supersede preserved runtime/provenance/acceptance contracts.

Use this route for subsequent work:

1. [S11 work-item ledger](00-project/work-plan.md#s11-work-item-ledger) — O/W mapping,
   live state, dependencies, next action and completion evidence.
2. [Witness Architecture](20-architecture/s11-interface-observability-witness-architecture.md)
   — target meanings and implementation responsibilities, including W1.
3. [Witness Validation](30-validation/s11-interface-observability-witness-validation.md)
   — controls and acceptance gates. A defined contract is not a passing result.
4. [O2 operations](40-operations/s11-o2-local-shadow-evaluation.md) — execute only
   the procedure selected by the ledger/current request; retained commands do not
   mean a closed experiment must be rerun.
5. [Evidence](60-evidence/s11/) — completed local checks and transferred Windows
   results, including rejected hypotheses and their limits.

The ledger is the only live W-status list. This router owns the relationship
between documents, not another copy of progress. W0–W4 refine work within O2;
W5/W6/W7 map to O3/O4/O5. O2 acceptance remains a separate gate before W5, not
an automatic consequence of finishing an experiment.

## Supporting collection indexes

- S11 diagnostics — [`50-diagnostics/s11/`](50-diagnostics/s11/)
- completed evidence — [`60-evidence/README.md`](60-evidence/README.md)
- retained/deferred commitments — [`00-project/retained-commitments.md`](00-project/retained-commitments.md)
- implementation/reference provenance — [`70-reference/implementation-reference-log.md`](70-reference/implementation-reference-log.md)

## Archive policy

`90-archive/` preserves superseded context and decision history. Archived documents may retain their original language. Repair links when needed for navigation, but never promote an archived statement back into current authority without updating a current owner.

- Supplemental observation redesign execution review — [50-diagnostics/s11/s11-observation-redesign-execution-review.md](50-diagnostics/s11/s11-observation-redesign-execution-review.md); supporting proposal, implemented definitions belong to the Witness Architecture.

## Document maintenance lifecycle

이 절은 문서 생성·갱신·종료·아카이브의 관리 기준입니다. 위 권한 체계와
[실행 정책](00-project/execution-policy.md)을 보충하며 별도 상태 원장을 만들지 않습니다.

문서 구조·생명주기 관리·조사·아카이브·현재 상태 축약은 [Oil 문서 정리 Skill](../.agents/skills/oil-docs-maintenance/SKILL.md)로 연결합니다. 새 프로젝트와 기존 프로젝트에 공통인 구조 설계·관리 절차는 사용 가능한 전역 `docs-management` Skill이 담당하며, Oil의 분류·권한·관리 규칙 원본은 이 문서에 유지합니다. 일반 오탈자 수정이나 기능 문서 작성에는 전체 정리 절차를 적용하지 않습니다.

### 새 문서와 갱신

- 먼저 이름과 책임으로 기존 owner를 찾습니다. 기존 계약 변경은 그 문서를 갱신합니다.
- 새 파일은 독립된 질문·계약·실행 증거 범위가 있을 때 만듭니다. 같은 실행의 후속 결과와 정정은 기존 기록에 날짜와 출처를 붙여 추가합니다.
- 현재 상태는 Work Plan의 해당 항목을 교체합니다. 완료 경과·테스트 수·전달 이력을 계속 덧붙이지 않습니다.
- 다른 문서는 결론 한두 문장과 owner 링크만 둡니다. recall-index에는 재개 이유와 경로를 남기며 live 상태를 복제하지 않습니다.
- 외부 감사 원문은 보존합니다. 감사 당시 pending 문구를 현재 지시로 해석하지 않습니다.
- 새 기록에는 목적, 근거 HEAD/입력, 결과, 한계와 현행 owner를 명시합니다. 로컬 검증·사용자 전달·추정을 구분합니다.

### 날짜와 탐색

- [날짜순 색인](catalog-by-created-date.md)은 실제 폴더별 → 최초 Git 추가일(KST) → 같은 날 파일명 순입니다. 색인의 링크는 활성 의존성으로 자동 전파하지 않습니다.
- 최초 Git 추가일은 rename을 추적한 추가 커밋의 author 날짜입니다. 실제 작성일, 사건일, 마지막 수정일, 아카이브일과 구분합니다. Git 미등록 파일은 작성일을 별도 표시하고 날짜를 꾸며내지 않습니다.
- 파일 생성·이동 시 같은 변경에서 색인을 갱신합니다. Git 등록 후에는 해당 미등록 항목의 날짜 근거도 확정합니다.
- 지속 owner와 기존 파일은 안정된 이름을 유지합니다. 새 일회성 기록만 `YYYY-MM-DD-topic.md`를 권장합니다. 날짜 정렬을 위해 기존 파일명이나 파일시스템 시간을 일괄 변경하지 않습니다.
- 기존 문서에 일괄 metadata를 삽입하지 않습니다. 날짜·분류는 색인과 이동 기록으로 보완합니다.

### 작업 종료 시 함께 정리

1. 결과·정정·미해결 조건을 기존 evidence/diagnostic owner에 확정합니다.
2. Work Plan에는 현재 결론, 남은 조건, 다음 행동과 근거 링크만 남깁니다. 닫힌 실험을 pending 문구 때문에 재개하지 않습니다.
3. owner가 교체됐다면 이전 문서의 유효 조항과 successor의 정확한 절을 대조합니다. 완료 증거는 `60-evidence`, 인과 근거는 `50-diagnostics`에 유지할 수 있습니다.
4. 대체된 계약·절차만 아래 조건에 따라 아카이브하고 색인·유입/유출 링크를 갱신합니다.

### 아카이브와 보호

오래됨, 큰 크기, 유입 링크 없음, 실험 실패 또는 완료는 단독 이동 근거가 아닙니다.
구현 완료 후에도 동작을 정의하는 계약은 현행입니다. 다음을 확인해야 이동합니다.

- 현재 의무의 정확한 successor 또는 명시적 폐기 근거가 있고, 유보 의무의 유일한 owner가 아닙니다.
- 코드·테스트·현재 절차·외부 handoff의 경로 소비를 확인합니다. 불명확하면 현 위치를 유지하고 이동 기록에 이유를 남깁니다.
- 기본 보호 대상은 현행 계약·truth·machine fixture·감사 원문입니다. 사용자가 특정 owner의 정리를 요청한 경우 그 범위 안에서 의미와 사용 중 앵커를 보존해 편집합니다. 이미 허용된 정리에 재승인을 요구하지 않습니다.
- JSON/patch·fingerprint·기준 출력은 일반 문서 편집 대상이 아닙니다. 별도 소비자 검증 없이 이동하거나 다시 생성하지 않습니다.
- 목적지는 `90-archive/<원래 분류>/<최초 Git 등록 연도>/<기존 basename>`입니다. 기존 아카이브를 재이동하거나 폴더마다 `old/archive`를 추가하지 않습니다.
- 이동 기록은 원본/목적지, 최초 추가 커밋·날짜, 원문/결과 hash, 사유, successor/절, 유입 참조, 링크 교정과 복구 방법을 보존합니다. 링크 교정과 의미 변경을 구분합니다.
- 역사 증거의 수치·당시 판정은 덮어쓰지 않습니다. `CLOSED WITHOUT PROMOTION`, `FIELD FAIL`, unknown, deferred를 DONE으로 바꾸지 않습니다.

### 크기 점검과 검증

Work Plan은 약 140–200줄/10–16 KiB를 검토 목표로 삼습니다. roadmap이
100줄/8 KiB를 넘거나 recall의 한 셀에 여러 실행 경과가 쌓이면 역할을 점검합니다.
강제 상한은 없으며 의무·불확실성·승인 범위를 지워서 길이를 맞추지 않습니다.
계약·절차는 길이보다 책임을 기준으로 나누고, 활성 절차는 먼저 섹션 링크로 탐색합니다.

문서 정리에서는 기준 HEAD와 작업 트리를 확인하고 다음을 검증합니다.

- 파일 누락·목적지 충돌, Markdown 경로·제목 앵커, 코드의 고정 경로 참조;
- 보호 대상의 경로·hash, 이동 문서의 링크 외 원문 동일성, 현재 상태 보존;
- `git diff --check` 및 S11 문서 변경 시 기존 governance 검사.

문서 정리만으로 detector/Windows 재실행을 요구하지 않습니다. 실제 fixture
소비자가 바뀌면 해당 테스트를 검증합니다. 복구는 기준 Git blob과 이동 매핑으로
해당 변경만 되돌립니다. milestone 종료·owner 교체·Work Plan 누적 시 재점검하며,
시간 경과만으로 자동 아카이브하거나 정기 작업을 예약하지 않습니다.
