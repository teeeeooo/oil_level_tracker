# Docs — 폴더별 최초 Git 등록일순 색인

최초 Git 추가일(KST) 오름차순이며, 같은 날은 파일명 순입니다. 파일시스템 생성일이나
실제 최초 작성일을 뜻하지 않습니다. 이동 파일은 원본 추가 이력을 유지합니다.
Git 미등록 파일은 마지막에 두고 작성일을 별도로 표시합니다.

이 목록은 탐색용 파생 자료입니다. 현재 상태·작업 승인·의무는 해당 owner에서 확인합니다.
완료 증거의 오래된 상태 문구는 현재 지시가 아닙니다. 현재 계약의 유입 링크 수가 적어도 폐기 근거가 되지 않습니다.

- [문서 역할과 관리 규칙](README.md#document-maintenance-lifecycle)
- [현재 작업](00-project/work-plan.md) · [마일스톤](00-project/roadmap.md)
- [2026-10-03 정리 근거 및 승계 검토](90-archive/00-project/2026/2026-10-03-docs-reorganization.md)

## 날짜 근거

기존 246개: 기준 `aa0d1964bf493732fbe33bbdda33f4449f817b47`에서 `git log --follow --diff-filter=A`의
최초 추가 커밋 author 시각을 Asia/Seoul로 변환한 첨부 감사 자료를 사용했습니다.
이동 상세 날짜·추가 커밋은 [manifest](90-archive/00-project/2026/2026-10-03-docs-migration.json)에 있습니다.
이번 정리에서 추가한 색인·이동 manifest·정리 기록 3개는 `a5ae21cf18f0b50ba930e4f34cda3fc07148d69c`의 author 날짜(KST)로 최초 추가일을 확정했습니다.
새 파일을 Git에 등록하면 해당 미등록 행의 최초 추가일을 확정합니다. 파일 생성·이동 시 이 색인도 갱신합니다.
Report source-context 설계는 `f6c9e10`, 실행 증거는 `9414f2a`의 최초 추가 author 날짜(KST)로 확정했습니다.

## 폴더별 목록

현재 색인 수록 271개 파일. 이후 추가된 모든 repo 문서의 전수 목록을 보증하는 수치는 아닙니다.
`검토 후 유지`는 승계가 확인되지 않아 현 위치를 보존한다는 뜻이며,
그 문서의 과거 실행 지시 전체가 현행이라는 의미가 아닙니다.

### `docs/` — 3개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-07-20 | [rotary_oil_level_tracker_ssot_spec.md](rotary_oil_level_tracker_ssot_spec.md) | 현 위치 유지 |
| 2026-07-29 | [README.md](README.md) | 현 위치 유지 |
| 2026-10-03 | [catalog-by-created-date.md](catalog-by-created-date.md) | 파생 색인 |

### `docs/00-project/` — 5개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-07-29 | [roadmap.md](00-project/roadmap.md) | 현 위치 유지 |
| 2026-07-29 | [work-plan.md](00-project/work-plan.md) | 현 위치 유지 |
| 2026-08-07 | [retained-commitments.md](00-project/retained-commitments.md) | 현 위치 유지 |
| 2026-09-05 | [execution-policy.md](00-project/execution-policy.md) | 현 위치 유지 |
| 2026-09-07 | [recall-index.md](00-project/recall-index.md) | 현 위치 유지 |

### `docs/10-product/` — 2개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-07-20 | [result-review-viewer-plan.md](10-product/result-review-viewer-plan.md) | 현 위치 유지 |
| 2026-07-29 | [ux-improvement-plan.md](10-product/ux-improvement-plan.md) | 현 위치 유지 |

### `docs/20-architecture/` — 34개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-07-29 | [s5b-oil-boundary-hypothesis-architecture.md](20-architecture/s5b-oil-boundary-hypothesis-architecture.md) | 현 위치 유지 |
| 2026-08-07 | [initial-state-retrospective-reconstruction-architecture.md](20-architecture/initial-state-retrospective-reconstruction-architecture.md) | 현 위치 유지 |
| 2026-08-07 | [s11-detector-responsibility-architecture.md](20-architecture/s11-detector-responsibility-architecture.md) | 현 위치 유지 |
| 2026-08-09 | [result-observation-report-architecture.md](20-architecture/result-observation-report-architecture.md) | 현 위치 유지 |
| 2026-08-11 | [s11-r5-sequence-first-trajectory-architecture.md](20-architecture/s11-r5-sequence-first-trajectory-architecture.md) | 현 위치 유지 |
| 2026-08-11 | [s11-r6-optics-aware-observation-architecture.md](20-architecture/s11-r6-optics-aware-observation-architecture.md) | 현 위치 유지 |
| 2026-08-11 | [s11-r7-evidence-tiered-trajectory-architecture.md](20-architecture/s11-r7-evidence-tiered-trajectory-architecture.md) | 현 위치 유지 |
| 2026-08-12 | [s11-r8-observation-recovery-architecture.md](20-architecture/s11-r8-observation-recovery-architecture.md) | 현 위치 유지 |
| 2026-08-13 | [s11-r9-calibrated-observation-architecture.md](20-architecture/s11-r9-calibrated-observation-architecture.md) | 검토 후 유지 |
| 2026-08-14 | [s11-r10-calibrated-path-and-layer-architecture.md](20-architecture/s11-r10-calibrated-path-and-layer-architecture.md) | 검토 후 유지 |
| 2026-08-18 | [s11-r11-detector-architecture-reset.md](20-architecture/s11-r11-detector-architecture-reset.md) | 검토 후 유지 |
| 2026-08-18 | [s11-r12-phase-composition-replacement-architecture.md](20-architecture/s11-r12-phase-composition-replacement-architecture.md) | 검토 후 유지 |
| 2026-08-19 | [s11-r13-phase-identity-recovery-architecture.md](20-architecture/s11-r13-phase-identity-recovery-architecture.md) | 검토 후 유지 |
| 2026-08-20 | [s11-r14-phase-component-replacement-architecture.md](20-architecture/s11-r14-phase-component-replacement-architecture.md) | 검토 후 유지 |
| 2026-08-20 | [s11-r15-state-aware-material-ownership-architecture.md](20-architecture/s11-r15-state-aware-material-ownership-architecture.md) | 검토 후 유지 |
| 2026-08-24 | [s11-r16-directed-tracklet-material-lifecycle-architecture.md](20-architecture/s11-r16-directed-tracklet-material-lifecycle-architecture.md) | 검토 후 유지 |
| 2026-08-24 | [s11-r17-physical-observation-ownership-architecture.md](20-architecture/s11-r17-physical-observation-ownership-architecture.md) | 현 위치 유지 |
| 2026-08-25 | [s11-current-detector-logic-map.md](20-architecture/s11-current-detector-logic-map.md) | 현 위치 유지 |
| 2026-08-25 | [s11-r18-lifecycle-closure-architecture.md](20-architecture/s11-r18-lifecycle-closure-architecture.md) | 현 위치 유지 |
| 2026-08-26 | [s11-r18-causal-trace-observability-architecture.md](20-architecture/s11-r18-causal-trace-observability-architecture.md) | 검토 후 유지 |
| 2026-08-26 | [s11-r19-bounded-drain-release-chain-architecture.md](20-architecture/s11-r19-bounded-drain-release-chain-architecture.md) | 현 위치 유지 |
| 2026-08-31 | [s11-result-review-presentation-architecture.md](20-architecture/s11-result-review-presentation-architecture.md) | 현 위치 유지 |
| 2026-09-01 | [s11-r20-delayed-drain-reacquisition-architecture.md](20-architecture/s11-r20-delayed-drain-reacquisition-architecture.md) | 현 위치 유지 |
| 2026-09-04 | [s11-behavioral-lifecycle-and-foam-witness-architecture.md](20-architecture/s11-behavioral-lifecycle-and-foam-witness-architecture.md) | 현 위치 유지 |
| 2026-09-04 | [s11-r20-decision-witness-observability-architecture.md](20-architecture/s11-r20-decision-witness-observability-architecture.md) | 검토 후 유지 |
| 2026-09-06 | [s11-r21-truth-preserving-detector-repair-architecture.md](20-architecture/s11-r21-truth-preserving-detector-repair-architecture.md) | 현 위치 유지 |
| 2026-09-07 | [s11-agent-harness-v2-routing-design.md](20-architecture/s11-agent-harness-v2-routing-design.md) | 현 위치 유지 |
| 2026-09-10 | [s11-r22-oil-ownership-evidence-replacement-architecture.md](20-architecture/s11-r22-oil-ownership-evidence-replacement-architecture.md) | 현 위치 유지 |
| 2026-09-15 | [s11-physical-interface-evidence-repair-design.md](20-architecture/s11-physical-interface-evidence-repair-design.md) | 현 위치 유지 |
| 2026-09-15 | [s11-r22-1-interface-diagnostics-architecture.md](20-architecture/s11-r22-1-interface-diagnostics-architecture.md) | 현 위치 유지 |
| 2026-09-16 | [s11-r22-2-interface-path-diagnostics-architecture.md](20-architecture/s11-r22-2-interface-path-diagnostics-architecture.md) | 현 위치 유지 |
| 2026-09-17 | [s11-interface-observability-witness-architecture.md](20-architecture/s11-interface-observability-witness-architecture.md) | 현 위치 유지 |
| 2026-10-07 | [s11-report-source-context-design.md](20-architecture/s11-report-source-context-design.md) | 로컬 report 후보 설계 |
| 2026-10-08 | [s11-episode-source-review-design.md](20-architecture/s11-episode-source-review-design.md) | 원본 프레임 맥락 및 별도 텍스처 실험 계약 |

### `docs/30-validation/` — 32개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-07-20 | [golden-video-regression.md](30-validation/golden-video-regression.md) | 현 위치 유지 |
| 2026-07-29 | [real-world-validation-plan.md](30-validation/real-world-validation-plan.md) | 현 위치 유지 |
| 2026-08-04 | [test-authoring-portability-contract.md](30-validation/test-authoring-portability-contract.md) | 현 위치 유지 |
| 2026-08-07 | [initial-state-retrospective-reconstruction-validation.md](30-validation/initial-state-retrospective-reconstruction-validation.md) | 현 위치 유지 |
| 2026-08-07 | [s11-real-field-detector-effectiveness.md](30-validation/s11-real-field-detector-effectiveness.md) | 현 위치 유지 |
| 2026-08-09 | [result-observation-report-validation.md](30-validation/result-observation-report-validation.md) | 현 위치 유지 |
| 2026-08-11 | [s11-r5-sequence-first-trajectory-validation.md](30-validation/s11-r5-sequence-first-trajectory-validation.md) | 현 위치 유지 |
| 2026-08-11 | [s11-r6-optics-aware-observation-validation.md](30-validation/s11-r6-optics-aware-observation-validation.md) | 현 위치 유지 |
| 2026-08-11 | [s11-r7-evidence-tiered-trajectory-validation.md](30-validation/s11-r7-evidence-tiered-trajectory-validation.md) | 현 위치 유지 |
| 2026-08-12 | [s11-r8-observation-recovery-validation.md](30-validation/s11-r8-observation-recovery-validation.md) | 현 위치 유지 |
| 2026-08-13 | [s11-r9-calibrated-observation-validation.md](30-validation/s11-r9-calibrated-observation-validation.md) | 검토 후 유지 |
| 2026-08-14 | [s11-r10-calibrated-path-and-layer-validation.md](30-validation/s11-r10-calibrated-path-and-layer-validation.md) | 검토 후 유지 |
| 2026-08-18 | [s11-r11-detector-architecture-reset-validation.md](30-validation/s11-r11-detector-architecture-reset-validation.md) | 검토 후 유지 |
| 2026-08-18 | [s11-r12-phase-composition-replacement-validation.md](30-validation/s11-r12-phase-composition-replacement-validation.md) | 검토 후 유지 |
| 2026-08-19 | [s11-r13-phase-identity-recovery-validation.md](30-validation/s11-r13-phase-identity-recovery-validation.md) | 검토 후 유지 |
| 2026-08-20 | [s11-r14-phase-component-replacement-validation.md](30-validation/s11-r14-phase-component-replacement-validation.md) | 검토 후 유지 |
| 2026-08-20 | [s11-r15-state-aware-material-ownership-validation.md](30-validation/s11-r15-state-aware-material-ownership-validation.md) | 검토 후 유지 |
| 2026-08-24 | [s11-r16-directed-tracklet-material-lifecycle-validation.md](30-validation/s11-r16-directed-tracklet-material-lifecycle-validation.md) | 검토 후 유지 |
| 2026-08-24 | [s11-r17-physical-observation-ownership-validation.md](30-validation/s11-r17-physical-observation-ownership-validation.md) | 현 위치 유지 |
| 2026-08-25 | [s11-detector-change-governance.md](30-validation/s11-detector-change-governance.md) | 현 위치 유지 |
| 2026-08-25 | [s11-r18-lifecycle-closure-validation.md](30-validation/s11-r18-lifecycle-closure-validation.md) | 현 위치 유지 |
| 2026-08-25 | [windows-sample1-heating-coldstart-reviewed-truth.md](30-validation/windows-sample1-heating-coldstart-reviewed-truth.md) | 현 위치 유지 |
| 2026-08-25 | [windows_sample1_heating_coldstart.reviewed-truth.json](30-validation/windows_sample1_heating_coldstart.reviewed-truth.json) | 현 위치 유지 |
| 2026-08-26 | [s11-r18-causal-trace-observability-validation.md](30-validation/s11-r18-causal-trace-observability-validation.md) | 검토 후 유지 |
| 2026-08-26 | [s11-r19-bounded-drain-release-chain-validation.md](30-validation/s11-r19-bounded-drain-release-chain-validation.md) | 현 위치 유지 |
| 2026-09-01 | [s11-r20-delayed-drain-reacquisition-validation.md](30-validation/s11-r20-delayed-drain-reacquisition-validation.md) | 현 위치 유지 |
| 2026-09-04 | [s11-behavioral-lifecycle-and-foam-witness-validation.md](30-validation/s11-behavioral-lifecycle-and-foam-witness-validation.md) | 현 위치 유지 |
| 2026-09-04 | [s11-r20-decision-witness-observability-validation.md](30-validation/s11-r20-decision-witness-observability-validation.md) | 검토 후 유지 |
| 2026-09-06 | [s11-r21-truth-preserving-detector-repair-validation.md](30-validation/s11-r21-truth-preserving-detector-repair-validation.md) | 현 위치 유지 |
| 2026-09-10 | [s11-r22-oil-ownership-evidence-replacement-validation.md](30-validation/s11-r22-oil-ownership-evidence-replacement-validation.md) | 현 위치 유지 |
| 2026-09-15 | [s11-physical-interface-evidence-repair-validation.md](30-validation/s11-physical-interface-evidence-repair-validation.md) | 현 위치 유지 |
| 2026-09-17 | [s11-interface-observability-witness-validation.md](30-validation/s11-interface-observability-witness-validation.md) | 현 위치 유지 |

### `docs/40-operations/` — 5개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-07-20 | [manual-gui-windows-checklist.md](40-operations/manual-gui-windows-checklist.md) | 현 위치 유지 |
| 2026-09-07 | [s11-current-windows-field-qualification.md](40-operations/s11-current-windows-field-qualification.md) | 현 위치 유지 |
| 2026-09-15 | [s11-r22-1-windows-interface-measurement.md](40-operations/s11-r22-1-windows-interface-measurement.md) | 현 위치 유지 |
| 2026-09-16 | [s11-r22-2-windows-interface-measurement.md](40-operations/s11-r22-2-windows-interface-measurement.md) | 현 위치 유지 |
| 2026-09-17 | [s11-o2-local-shadow-evaluation.md](40-operations/s11-o2-local-shadow-evaluation.md) | 현 위치 유지 |

### `docs/50-diagnostics/` — 1개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-08-10 | [post-s11-structural-maintainability-assessment.md](50-diagnostics/post-s11-structural-maintainability-assessment.md) | 진단·근거 |

### `docs/50-diagnostics/s11/` — 48개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-08-04 | [s11-a-detector-direction-and-experiment-plan.md](50-diagnostics/s11/s11-a-detector-direction-and-experiment-plan.md) | 진단·근거 |
| 2026-08-04 | [s11-a-opencv-evidence-architecture-probe-manifest.json](50-diagnostics/s11/s11-a-opencv-evidence-architecture-probe-manifest.json) | 진단·근거 |
| 2026-08-04 | [s11-a-opencv-evidence-architecture-probe.md](50-diagnostics/s11/s11-a-opencv-evidence-architecture-probe.md) | 진단·근거 |
| 2026-08-04 | [s11-a-spatial-path-cross-roi-probe-manifest.json](50-diagnostics/s11/s11-a-spatial-path-cross-roi-probe-manifest.json) | 진단·근거 |
| 2026-08-04 | [s11-a-spatial-path-cross-roi-probe.md](50-diagnostics/s11/s11-a-spatial-path-cross-roi-probe.md) | 진단·근거 |
| 2026-08-05 | [s11-a-p2-spatial-interaction-probe-manifest.json](50-diagnostics/s11/s11-a-p2-spatial-interaction-probe-manifest.json) | 진단·근거 |
| 2026-08-05 | [s11-a-p2-spatial-interaction-probe.md](50-diagnostics/s11/s11-a-p2-spatial-interaction-probe.md) | 진단·근거 |
| 2026-08-05 | [s11-c-full-video-production-replay-visual-forensic-diagnostic.md](50-diagnostics/s11/s11-c-full-video-production-replay-visual-forensic-diagnostic.md) | 진단·근거 |
| 2026-08-05 | [s11-offline-temporal-trajectory-probe-manifest.json](50-diagnostics/s11/s11-offline-temporal-trajectory-probe-manifest.json) | 진단·근거 |
| 2026-08-05 | [s11-offline-temporal-trajectory-probe.md](50-diagnostics/s11/s11-offline-temporal-trajectory-probe.md) | 진단·근거 |
| 2026-08-07 | [README.md](50-diagnostics/s11/README.md) | 진단·근거 |
| 2026-08-09 | [s11-r2-foam-spatial-authority-diagnostic.md](50-diagnostics/s11/s11-r2-foam-spatial-authority-diagnostic.md) | 진단·근거 |
| 2026-08-09 | [s11-user-report-observability-diagnostic.md](50-diagnostics/s11/s11-user-report-observability-diagnostic.md) | 진단·근거 |
| 2026-08-10 | [s11-r3-sequence-observability-root-cause.md](50-diagnostics/s11/s11-r3-sequence-observability-root-cause.md) | 진단·근거 |
| 2026-08-10 | [s11-r4-windows-residual-authority-diagnostic.md](50-diagnostics/s11/s11-r4-windows-residual-authority-diagnostic.md) | 진단·근거 |
| 2026-08-11 | [s11-r5-current-frame-authority-root-cause.md](50-diagnostics/s11/s11-r5-current-frame-authority-root-cause.md) | 진단·근거 |
| 2026-08-11 | [s11-r5-secure-windows-field-failure.md](50-diagnostics/s11/s11-r5-secure-windows-field-failure.md) | 진단·근거 |
| 2026-08-11 | [s11-r6-checked-video-reconciliation.md](50-diagnostics/s11/s11-r6-checked-video-reconciliation.md) | 진단·근거 |
| 2026-08-11 | [s11-r6-secure-windows-field-failure.md](50-diagnostics/s11/s11-r6-secure-windows-field-failure.md) | 진단·근거 |
| 2026-08-11 | [s11-r7-checked-video-direct-image-reconciliation.md](50-diagnostics/s11/s11-r7-checked-video-direct-image-reconciliation.md) | 진단·근거 |
| 2026-08-12 | [s11-r7-windows-observation-recovery-diagnostic.md](50-diagnostics/s11/s11-r7-windows-observation-recovery-diagnostic.md) | 진단·근거 |
| 2026-08-13 | [s11-r8-windows-calibrated-observation-diagnostic.md](50-diagnostics/s11/s11-r8-windows-calibrated-observation-diagnostic.md) | 진단·근거 |
| 2026-08-14 | [s11-r9-windows-calibrated-observation-diagnostic.md](50-diagnostics/s11/s11-r9-windows-calibrated-observation-diagnostic.md) | 진단·근거 |
| 2026-08-18 | [s11-r10-windows-path-and-residue-diagnostic.md](50-diagnostics/s11/s11-r10-windows-path-and-residue-diagnostic.md) | 진단·근거 |
| 2026-08-18 | [s11-r11-windows-bootstrap-composition-diagnostic.md](50-diagnostics/s11/s11-r11-windows-bootstrap-composition-diagnostic.md) | 진단·근거 |
| 2026-08-19 | [s11-r12-windows-phase-authority-diagnostic.md](50-diagnostics/s11/s11-r12-windows-phase-authority-diagnostic.md) | 진단·근거 |
| 2026-08-20 | [s11-r13-windows-identity-component-diagnostic.md](50-diagnostics/s11/s11-r13-windows-identity-component-diagnostic.md) | 진단·근거 |
| 2026-08-20 | [s11-r14-windows-state-and-foam-ownership-diagnostic.md](50-diagnostics/s11/s11-r14-windows-state-and-foam-ownership-diagnostic.md) | 진단·근거 |
| 2026-08-23 | [s11-r16-current-frame-performance.md](50-diagnostics/s11/s11-r16-current-frame-performance.md) | 진단·근거 |
| 2026-08-23 | [s11-r16-r4-resolver-performance.md](50-diagnostics/s11/s11-r16-r4-resolver-performance.md) | 진단·근거 |
| 2026-08-23 | [s11-r16-r5-application-boundary.md](50-diagnostics/s11/s11-r16-r5-application-boundary.md) | 진단·근거 |
| 2026-08-23 | [s11-r16-refactor-performance-baseline.md](50-diagnostics/s11/s11-r16-refactor-performance-baseline.md) | 진단·근거 |
| 2026-08-24 | [s11-r16-local-coverage-owner-audit.md](50-diagnostics/s11/s11-r16-local-coverage-owner-audit.md) | 진단·근거 |
| 2026-08-24 | [s11-r16-windows-tracklet-and-foam-diagnostic.md](50-diagnostics/s11/s11-r16-windows-tracklet-and-foam-diagnostic.md) | 진단·근거 |
| 2026-08-25 | [s11-detector-mechanism-failure-registry.md](50-diagnostics/s11/s11-detector-mechanism-failure-registry.md) | 진단·근거 |
| 2026-08-25 | [s11-r17-windows-phase-and-episode-diagnostic.md](50-diagnostics/s11/s11-r17-windows-phase-and-episode-diagnostic.md) | 진단·근거 |
| 2026-08-26 | [s11-r18-windows-causal-closure.md](50-diagnostics/s11/s11-r18-windows-causal-closure.md) | 진단·근거 |
| 2026-09-06 | [s11-r21-replay-runtime-provenance-diagnostic.md](50-diagnostics/s11/s11-r21-replay-runtime-provenance-diagnostic.md) | 진단·근거 |
| 2026-09-15 | [s11-r22-reviewed-interface-causal-findings.md](50-diagnostics/s11/s11-r22-reviewed-interface-causal-findings.md) | 진단·근거 |
| 2026-09-17 | [s11-interface-witness-public-probe-summary.json](50-diagnostics/s11/s11-interface-witness-public-probe-summary.json) | 진단·근거 |
| 2026-09-17 | [s11-observation-redesign-execution-review.md](50-diagnostics/s11/s11-observation-redesign-execution-review.md) | 진단·근거 |
| 2026-09-17 | [s11-r23-native-polarity-rejection.md](50-diagnostics/s11/s11-r23-native-polarity-rejection.md) | 진단·근거 |
| 2026-09-17 | [s11-r23-rejected-native-polarity-prototype.patch](50-diagnostics/s11/s11-r23-rejected-native-polarity-prototype.patch) | 진단·근거 |
| 2026-09-17 | [s11-r23-rejected-native-polarity-results.json](50-diagnostics/s11/s11-r23-rejected-native-polarity-results.json) | 진단·근거 |
| 2026-09-17 | [s11-transparent-interface-detector-direction-assessment.md](50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md) | 진단·근거 |
| 2026-09-29 | [s11-o2-fixed-score-experiment.md](50-diagnostics/s11/s11-o2-fixed-score-experiment.md) | 진단·근거 |
| 2026-10-01 | [s11-detector-improvement-audit-and-work-spec-2026-10-01.md](50-diagnostics/s11/s11-detector-improvement-audit-and-work-spec-2026-10-01.md) | 진단·근거 |
| 2026-10-01 | [s11-w4-progress-audit-and-continuation-plan-2026-10-01-ba1bd6a.md](50-diagnostics/s11/s11-w4-progress-audit-and-continuation-plan-2026-10-01-ba1bd6a.md) | 진단·근거 |

### `docs/60-evidence/` — 1개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-08-07 | [README.md](60-evidence/README.md) | 완료 증거 |

### `docs/60-evidence/s10/` — 2개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-08-04 | [post-s10-windows-qt-platform-bootstrap-repair.md](60-evidence/s10/post-s10-windows-qt-platform-bootstrap-repair.md) | 완료 증거 |
| 2026-08-04 | [s10-windows-canonical-portability-qt-teardown-repair-evidence.md](60-evidence/s10/s10-windows-canonical-portability-qt-teardown-repair-evidence.md) | 완료 증거 |

### `docs/60-evidence/s11/` — 88개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-07-29 | [s5b-oil-boundary-hypothesis-history.md](60-evidence/s11/s5b-oil-boundary-hypothesis-history.md) | 완료 증거 |
| 2026-08-04 | [s11-real-field-detector-effectiveness-history.md](60-evidence/s11/s11-real-field-detector-effectiveness-history.md) | 완료 증거 |
| 2026-08-05 | [s11-b-spatial-positive-evidence-production.md](60-evidence/s11/s11-b-spatial-positive-evidence-production.md) | 완료 증거 |
| 2026-08-05 | [s11-d1-foam-structural-refractive-discrimination-oil-context-safety.md](60-evidence/s11/s11-d1-foam-structural-refractive-discrimination-oil-context-safety.md) | 완료 증거 |
| 2026-08-05 | [s11-d2-class-b-observation-proposal-representation.md](60-evidence/s11/s11-d2-class-b-observation-proposal-representation.md) | 완료 증거 |
| 2026-08-05 | [s11-d2-sample3-positive-evidence-recovery.md](60-evidence/s11/s11-d2-sample3-positive-evidence-recovery.md) | 완료 증거 |
| 2026-08-06 | [s11-d3-current-frame-semantic-authority-slimming.md](60-evidence/s11/s11-d3-current-frame-semantic-authority-slimming.md) | 완료 증거 |
| 2026-08-06 | [s11-d4-foam-support-structural-classification.md](60-evidence/s11/s11-d4-foam-support-structural-classification.md) | 완료 증거 |
| 2026-08-06 | [s11-d5-accepted-foam-oil-current-frame-semantic-authority-continuity.md](60-evidence/s11/s11-d5-accepted-foam-oil-current-frame-semantic-authority-continuity.md) | 완료 증거 |
| 2026-08-08 | [s11-detector-and-observed-graph-continuity.md](60-evidence/s11/s11-detector-and-observed-graph-continuity.md) | 완료 증거 |
| 2026-08-08 | [s11-slice-d-effectiveness-reconciliation.md](60-evidence/s11/s11-slice-d-effectiveness-reconciliation.md) | 완료 증거 |
| 2026-08-09 | [s11-post-r2-baseline-validation-repair-review.md](60-evidence/s11/s11-post-r2-baseline-validation-repair-review.md) | 완료 증거 |
| 2026-08-09 | [s11-r2-foam-spatial-authority-repair.md](60-evidence/s11/s11-r2-foam-spatial-authority-repair.md) | 완료 증거 |
| 2026-08-09 | [s11-user-observation-report-repair.md](60-evidence/s11/s11-user-observation-report-repair.md) | 완료 증거 |
| 2026-08-10 | [s11-r3-sequence-observability-integrity.md](60-evidence/s11/s11-r3-sequence-observability-integrity.md) | 완료 증거 |
| 2026-08-10 | [s11-r4-field-residual-authority.md](60-evidence/s11/s11-r4-field-residual-authority.md) | 완료 증거 |
| 2026-08-11 | [s11-r5-sequence-first-observation.md](60-evidence/s11/s11-r5-sequence-first-observation.md) | 완료 증거 |
| 2026-08-11 | [s11-r6-optics-aware-observation.md](60-evidence/s11/s11-r6-optics-aware-observation.md) | 완료 증거 |
| 2026-08-11 | [s11-r7-evidence-tiered-trajectory.md](60-evidence/s11/s11-r7-evidence-tiered-trajectory.md) | 완료 증거 |
| 2026-08-12 | [s11-r8-observation-recovery.md](60-evidence/s11/s11-r8-observation-recovery.md) | 완료 증거 |
| 2026-08-13 | [s11-r9-calibrated-observation.md](60-evidence/s11/s11-r9-calibrated-observation.md) | 완료 증거 |
| 2026-08-14 | [s11-r10-calibrated-path-and-layer.md](60-evidence/s11/s11-r10-calibrated-path-and-layer.md) | 완료 증거 |
| 2026-08-18 | [s11-r11-bounded-bootstrap-and-material-identity.md](60-evidence/s11/s11-r11-bounded-bootstrap-and-material-identity.md) | 완료 증거 |
| 2026-08-18 | [s11-r11-secure-windows-field-result.md](60-evidence/s11/s11-r11-secure-windows-field-result.md) | 완료 증거 |
| 2026-08-18 | [s11-r12-phase-composition-replacement.md](60-evidence/s11/s11-r12-phase-composition-replacement.md) | 완료 증거 |
| 2026-08-19 | [s11-r12-secure-windows-field-result.md](60-evidence/s11/s11-r12-secure-windows-field-result.md) | 완료 증거 |
| 2026-08-19 | [s11-r13-phase-identity-recovery.md](60-evidence/s11/s11-r13-phase-identity-recovery.md) | 완료 증거 |
| 2026-08-20 | [s11-r13-secure-windows-field-result.md](60-evidence/s11/s11-r13-secure-windows-field-result.md) | 완료 증거 |
| 2026-08-20 | [s11-r14-phase-component-replacement.md](60-evidence/s11/s11-r14-phase-component-replacement.md) | 완료 증거 |
| 2026-08-20 | [s11-r14-secure-windows-field-result.md](60-evidence/s11/s11-r14-secure-windows-field-result.md) | 완료 증거 |
| 2026-08-20 | [s11-r15-state-aware-material-ownership.md](60-evidence/s11/s11-r15-state-aware-material-ownership.md) | 완료 증거 |
| 2026-08-24 | [s11-r16-directed-tracklet-material-lifecycle.md](60-evidence/s11/s11-r16-directed-tracklet-material-lifecycle.md) | 완료 증거 |
| 2026-08-24 | [s11-r16-secure-windows-field-result.md](60-evidence/s11/s11-r16-secure-windows-field-result.md) | 완료 증거 |
| 2026-08-24 | [s11-r17-physical-observation-ownership.md](60-evidence/s11/s11-r17-physical-observation-ownership.md) | 완료 증거 |
| 2026-08-25 | [s11-r17-secure-windows-field-result.md](60-evidence/s11/s11-r17-secure-windows-field-result.md) | 완료 증거 |
| 2026-08-25 | [s11-r18-lifecycle-closure.md](60-evidence/s11/s11-r18-lifecycle-closure.md) | 완료 증거 |
| 2026-08-25 | [s11-r18-secure-windows-field-result.md](60-evidence/s11/s11-r18-secure-windows-field-result.md) | 완료 증거 |
| 2026-08-26 | [s11-r18-causal-trace-observability.md](60-evidence/s11/s11-r18-causal-trace-observability.md) | 완료 증거 |
| 2026-08-26 | [s11-r19-bounded-drain-release-chain.md](60-evidence/s11/s11-r19-bounded-drain-release-chain.md) | 완료 증거 |
| 2026-09-01 | [s11-r20-delayed-drain-reacquisition.md](60-evidence/s11/s11-r20-delayed-drain-reacquisition.md) | 완료 증거 |
| 2026-09-04 | [s11-behavioral-lifecycle-and-foam-witness.md](60-evidence/s11/s11-behavioral-lifecycle-and-foam-witness.md) | 완료 증거 |
| 2026-09-04 | [s11-r20-windows-evidence-consolidation.md](60-evidence/s11/s11-r20-windows-evidence-consolidation.md) | 완료 증거 |
| 2026-09-06 | [s11-r21-truth-preserving-detector-repair.md](60-evidence/s11/s11-r21-truth-preserving-detector-repair.md) | 완료 증거 |
| 2026-09-10 | [s11-r22-ownership-evidence-replacement.md](60-evidence/s11/s11-r22-ownership-evidence-replacement.md) | 완료 증거 |
| 2026-09-10 | [s11-r22-verification-summary.json](60-evidence/s11/s11-r22-verification-summary.json) | 완료 증거 |
| 2026-09-15 | [s11-r22-1-interface-diagnostics.md](60-evidence/s11/s11-r22-1-interface-diagnostics.md) | 완료 증거 |
| 2026-09-16 | [s11-r22-2-interface-path-diagnostics.md](60-evidence/s11/s11-r22-2-interface-path-diagnostics.md) | 완료 증거 |
| 2026-09-17 | [s11-o2-evaluation-control-summary.json](60-evidence/s11/s11-o2-evaluation-control-summary.json) | 완료 증거 |
| 2026-09-17 | [s11-o2-evaluation-foundation.md](60-evidence/s11/s11-o2-evaluation-foundation.md) | 완료 증거 |
| 2026-09-17 | [s11-r22-3-interface-witness-diagnostics.md](60-evidence/s11/s11-r22-3-interface-witness-diagnostics.md) | 완료 증거 |
| 2026-09-17 | [s11-r22-3-interface-witness-local-summary.json](60-evidence/s11/s11-r22-3-interface-witness-local-summary.json) | 완료 증거 |
| 2026-09-17 | [s11-r23-experiment-closeout.md](60-evidence/s11/s11-r23-experiment-closeout.md) | 완료 증거 |
| 2026-09-18 | [s11-o2-durable-review-records.md](60-evidence/s11/s11-o2-durable-review-records.md) | 완료 증거 |
| 2026-09-18 | [s11-o2-scoped-review-semantics.md](60-evidence/s11/s11-o2-scoped-review-semantics.md) | 완료 증거 |
| 2026-09-18 | [s11-o2-windows-review-001.md](60-evidence/s11/s11-o2-windows-review-001.md) | 완료 증거 |
| 2026-09-18 | [s11-o2-windows-review-002.md](60-evidence/s11/s11-o2-windows-review-002.md) | 완료 증거 |
| 2026-09-28 | [s11-o2-windows-review-003.md](60-evidence/s11/s11-o2-windows-review-003.md) | 완료 증거 |
| 2026-09-28 | [s11-o2-windows-review-comparison.md](60-evidence/s11/s11-o2-windows-review-comparison.md) | 완료 증거 |
| 2026-09-29 | [s11-o2-fixed-score-reversal-followup.md](60-evidence/s11/s11-o2-fixed-score-reversal-followup.md) | 완료 증거 |
| 2026-09-29 | [s11-o2-fixed-score-windows-run-001.md](60-evidence/s11/s11-o2-fixed-score-windows-run-001.md) | 완료 증거 |
| 2026-09-29 | [s11-o2-identity-profile-local.md](60-evidence/s11/s11-o2-identity-profile-local.md) | 완료 증거 |
| 2026-09-29 | [s11-o2-locality-ablation-windows-run-001.md](60-evidence/s11/s11-o2-locality-ablation-windows-run-001.md) | 완료 증거 |
| 2026-09-29 | [s11-o2-video-inventory.md](60-evidence/s11/s11-o2-video-inventory.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-identity-context-source-audit.md](60-evidence/s11/s11-o2-identity-context-source-audit.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-identity-context-windows-review-001.md](60-evidence/s11/s11-o2-identity-context-windows-review-001.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-identity-profile-windows-run-001.md](60-evidence/s11/s11-o2-identity-profile-windows-run-001.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-joint-context-local.md](60-evidence/s11/s11-o2-joint-context-local.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-joint-context-windows-run-001.md](60-evidence/s11/s11-o2-joint-context-windows-run-001.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-lateral-context-prototype-local.md](60-evidence/s11/s11-o2-lateral-context-prototype-local.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-reference-uncertainty-evaluation-audit.md](60-evidence/s11/s11-o2-reference-uncertainty-evaluation-audit.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-spatial-context-feasibility-local.md](60-evidence/s11/s11-o2-spatial-context-feasibility-local.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-spatial-context-prototype-local.md](60-evidence/s11/s11-o2-spatial-context-prototype-local.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-spatial-context-source-adapter-local.md](60-evidence/s11/s11-o2-spatial-context-source-adapter-local.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-spatial-context-windows-run-001.md](60-evidence/s11/s11-o2-spatial-context-windows-run-001.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-structure-context-audit-local.md](60-evidence/s11/s11-o2-structure-context-audit-local.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-structure-context-audit-windows-run-001.md](60-evidence/s11/s11-o2-structure-context-audit-windows-run-001.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-w1-target-aggregation-controls.md](60-evidence/s11/s11-o2-w1-target-aggregation-controls.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-w3-target-audit-windows-run-001.md](60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-w3-target-evaluation-local.md](60-evidence/s11/s11-o2-w3-target-evaluation-local.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-w4-paired-scale-local.md](60-evidence/s11/s11-o2-w4-paired-scale-local.md) | 완료 증거 |
| 2026-10-01 | [s11-o2-w4-paired-scale-windows-run-001.md](60-evidence/s11/s11-o2-w4-paired-scale-windows-run-001.md) | 완료 증거 |
| 2026-10-02 | [s11-o2-color-side-local.md](60-evidence/s11/s11-o2-color-side-local.md) | 완료 증거 |
| 2026-10-02 | [s11-o2-w2-f14865-scene-review.md](60-evidence/s11/s11-o2-w2-f14865-scene-review.md) | 완료 증거 |
| 2026-10-02 | [s11-o2-w4-r3-existing-evidence-feasibility.md](60-evidence/s11/s11-o2-w4-r3-existing-evidence-feasibility.md) | 완료 증거 |
| 2026-10-07 | [2026-10-07-report-source-context-validation.md](60-evidence/s11/2026-10-07-report-source-context-validation.md) | 로컬 후보 실행 증거 |

| 2026-10-08 | [2026-10-08-episode-source-review-validation.json](60-evidence/s11/2026-10-08-episode-source-review-validation.json) | 원본 프레임 검토 및 독립 텍스처 실험 실행 증거 |
| 2026-10-08 | [2026-10-08-episode-source-review-validation.md](60-evidence/s11/2026-10-08-episode-source-review-validation.md) | 원본 프레임 검토 및 독립 텍스처 실험 실행 증거 |
| 2026-10-09 | [2026-10-09-fixed-center-handoff.md](60-evidence/s11/2026-10-09-fixed-center-handoff.md) | 최초 추가 author 날짜(KST); 고정 중앙 측정 후 인수인계 |

### `docs/60-evidence/s6/` — 10개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-07-31 | [s6-additional-real-samples-evidence.md](60-evidence/s6/s6-additional-real-samples-evidence.md) | 완료 증거 |
| 2026-07-31 | [s6-base-sample-1-evidence.md](60-evidence/s6/s6-base-sample-1-evidence.md) | 완료 증거 |
| 2026-07-31 | [s6-bounded-runtime-soak-evidence.md](60-evidence/s6/s6-bounded-runtime-soak-evidence.md) | 완료 증거 |
| 2026-07-31 | [s6-domain-owner-review-addendum.md](60-evidence/s6/s6-domain-owner-review-addendum.md) | 완료 증거 |
| 2026-07-31 | [s6-provisional-truth-comparison.md](60-evidence/s6/s6-provisional-truth-comparison.md) | 완료 증거 |
| 2026-08-01 | [s6-d1-mobile-truth-review-pack.md](60-evidence/s6/s6-d1-mobile-truth-review-pack.md) | 완료 증거 |
| 2026-08-01 | [s6-f-one-hour-long-duration-stability.md](60-evidence/s6/s6-f-one-hour-long-duration-stability.md) | 완료 증거 |
| 2026-08-02 | [s6-d2-user-confirmed-product-truth.md](60-evidence/s6/s6-d2-user-confirmed-product-truth.md) | 완료 증거 |
| 2026-08-02 | [s6-d3-official-accuracy-baseline.md](60-evidence/s6/s6-d3-official-accuracy-baseline.md) | 완료 증거 |
| 2026-08-02 | [s6-d4-available-corpus-detector-repair.md](60-evidence/s6/s6-d4-available-corpus-detector-repair.md) | 완료 증거 |

### `docs/60-evidence/s7/` — 1개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-08-03 | [s7-annotated-mp4-export-evidence.md](60-evidence/s7/s7-annotated-mp4-export-evidence.md) | 완료 증거 |

### `docs/60-evidence/s8/` — 5개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-08-03 | [s8-a-run-identity-output-naming-evidence.md](60-evidence/s8/s8-a-run-identity-output-naming-evidence.md) | 완료 증거 |
| 2026-08-03 | [s8-b1-persistent-recent-result-access-evidence.md](60-evidence/s8/s8-b1-persistent-recent-result-access-evidence.md) | 완료 증거 |
| 2026-08-03 | [s8-b2-persistent-recent-profile-access-evidence.md](60-evidence/s8/s8-b2-persistent-recent-profile-access-evidence.md) | 완료 증거 |
| 2026-08-03 | [s8-c1-final-run-summary-evidence.md](60-evidence/s8/s8-c1-final-run-summary-evidence.md) | 완료 증거 |
| 2026-08-03 | [s8-c2-profile-current-test-separation-evidence.md](60-evidence/s8/s8-c2-profile-current-test-separation-evidence.md) | 완료 증거 |

### `docs/60-evidence/s9/` — 3개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-08-03 | [s9-a-unsaved-profile-close-guard-evidence.md](60-evidence/s9/s9-a-unsaved-profile-close-guard-evidence.md) | 완료 증거 |
| 2026-08-04 | [s9-b-workbench-zoom-pan-fit-evidence.md](60-evidence/s9/s9-b-workbench-zoom-pan-fit-evidence.md) | 완료 증거 |
| 2026-08-04 | [s9-c-field-overlay-interaction-polish-evidence.md](60-evidence/s9/s9-c-field-overlay-interaction-polish-evidence.md) | 완료 증거 |

### `docs/70-reference/` — 1개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-07-20 | [implementation-reference-log.md](70-reference/implementation-reference-log.md) | 현 위치 유지 |

### `docs/90-archive/` — 4개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-07-20 | [implementation-decisions.md](90-archive/implementation-decisions.md) | 아카이브 |
| 2026-07-20 | [initial-implementation-gaps.md](90-archive/initial-implementation-gaps.md) | 아카이브 |
| 2026-07-20 | [ux-improvement-backlog-2026-07.md](90-archive/ux-improvement-backlog-2026-07.md) | 아카이브 |
| 2026-07-21 | [real-world-stabilization-plan-2026-07.md](90-archive/real-world-stabilization-plan-2026-07.md) | 아카이브 |

### `docs/90-archive/00-project/2026/` — 2개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-03 | [2026-10-03-docs-migration.json](90-archive/00-project/2026/2026-10-03-docs-migration.json) | 아카이브 |
| 2026-10-03 | [2026-10-03-docs-reorganization.md](90-archive/00-project/2026/2026-10-03-docs-reorganization.md) | 아카이브 |

### `docs/90-archive/20-architecture/2026/` — 4개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-08-08 | [s11-subtractive-detector-simplification-architecture.md](90-archive/20-architecture/2026/s11-subtractive-detector-simplification-architecture.md) | 아카이브 |
| 2026-08-09 | [s11-foam-spatial-authority-repair-architecture.md](90-archive/20-architecture/2026/s11-foam-spatial-authority-repair-architecture.md) | 아카이브 |
| 2026-08-10 | [s11-r4-field-residual-authority-architecture.md](90-archive/20-architecture/2026/s11-r4-field-residual-authority-architecture.md) | 아카이브 |
| 2026-08-10 | [s11-sequence-observability-integrity-architecture.md](90-archive/20-architecture/2026/s11-sequence-observability-integrity-architecture.md) | 아카이브 |

### `docs/90-archive/30-validation/2026/` — 3개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-08-09 | [s11-foam-spatial-authority-repair-validation.md](90-archive/30-validation/2026/s11-foam-spatial-authority-repair-validation.md) | 아카이브 |
| 2026-08-10 | [s11-r4-field-residual-authority-validation.md](90-archive/30-validation/2026/s11-r4-field-residual-authority-validation.md) | 아카이브 |
| 2026-08-10 | [s11-sequence-observability-integrity-validation.md](90-archive/30-validation/2026/s11-sequence-observability-integrity-validation.md) | 아카이브 |

### `docs/90-archive/s11/` — 1개

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-09-07 | [windows-r7-r12-field-procedures.md](90-archive/s11/windows-r7-r12-field-procedures.md) | 아카이브 |

## 2026-10-06 추가 기록

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-06 | [Local corpus target reuse](60-evidence/s11/2026-10-06-local-corpus-target-reuse.md) | 로컬 truth·이미지 연결 검증; 작성일 2026-10-06 |
| 2026-10-06 | [Local Oil/Foam owner audit](50-diagnostics/s11/2026-10-06-local-oil-foam-owner-audit.md) | 세 프레임 저장 trace와 Oil/Foam 코드 대조 |
| 2026-10-06 | [Foam component diagnostics](20-architecture/s11-foam-component-diagnostics-architecture.md) | 탈락 영역·실제 predicate의 비권위 진단 기록 |

## 2026-10-07 audit adoption additions

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-07 | [Audit adoption checkpoint](60-evidence/s11/2026-10-07-audit-adoption-checkpoint.md) | 실제 체크아웃 A0B 반영·검증 및 인계 |
| 2026-10-07 | [First supplied audit](70-reference/s11-audit-2026-10-07/s11-audit-and-detector-work-spec-2026-10-07.md) | 원문 bytes 보존, 현재 상태 owner 아님 |
| 2026-10-07 | [Second supplied audit](70-reference/s11-audit-2026-10-07/s11-second-audit-and-detector-work-spec-2026-10-07.md) | 원문 bytes 보존; [JSON/ZIP/native evidence manifest](70-reference/s11-audit-2026-10-07/import-manifest.json) |
| 2026-10-07 | [Third supplied audit](70-reference/s11-audit-2026-10-07/s11-third-audit-report-context-work-spec-2026-10-07.md) | 원문 bytes 보존; 보고서 prototype 미채택, ZIP·JSON·worktree 복구 자료는 같은 manifest 참조 |
| 2026-10-07 | [Report context design](20-architecture/s11-report-context-presentation-design.md) | 보고서 수리의 범위와 과거 실패 검토 |
| 2026-10-07 | [Report context adoption](60-evidence/s11/2026-10-07-report-context-adoption.md) | 실제 반영 범위와 검증; 현재 단계는 Work Plan 참조 |
| 2026-10-07 | [sample4 interval candidate lineage](50-diagnostics/s11/2026-10-07-sample4-interval-candidate-lineage.md) | 일곱 프레임 후보와 사용자 확인용 대안; 같은 폴더 JSON manifest 참조 |
| 2026-10-07 | [A1 measurement lineage](60-evidence/s11/2026-10-07-a1-measurement-lineage.md) | 세 계측 공백 통합·무손실 검증; 같은 폴더 JSON receipt 및 후보 탈락 경로 |
| 2026-10-07 | [Pink-observation human reply](50-diagnostics/s11/2026-10-07-sample4-pink-human-reply.json), [A2 control preflight](50-diagnostics/s11/2026-10-07-sample4-a2-control-preflight.json) | 사용자 원문·불확실성 및 열 개 후보의 정확한 결합; 기존 candidate-lineage 문서가 해석 소유 |
| 2026-10-07 | [A2 target binding](60-evidence/s11/2026-10-07-a2-target-binding.md), [receipt](60-evidence/s11/2026-10-07-a2-target-binding.json), [temporal-context reply](50-diagnostics/s11/2026-10-07-sample4-temporal-context-human-reply.json) | 불확실한 물리 정체성과 명확한 오선택 분리; W3 기준 평가 및 원본 연속 프레임 검토 |
| 2026-10-07 | [A2 ordered-patch correspondence](60-evidence/s11/2026-10-07-a2-patch-correspondence.md), [receipt](60-evidence/s11/2026-10-07-a2-patch-correspondence.json), [human/seed review](60-evidence/s11/2026-10-07-a2-patch-correspondence-review.json) | 급격한 유면 변화의 30fps/2fps 대응 비교; 외관 연결과 물리 정체성 구분 |
| 2026-10-07 | [A2 region-context preflight](50-diagnostics/s11/2026-10-07-sample4-region-context-preflight.json) | 유면 위아래 영역의 물리적 해석 질문 및 21프레임 입력 정합성; 기존 candidate-lineage 문서가 해석 소유 |
| 2026-10-07 | [A2 joint temporal region exchange](60-evidence/s11/2026-10-07-a2-region-exchange.md), [receipt](60-evidence/s11/2026-10-07-a2-region-exchange.json) | A/B 답변 반영·고정 모델 W3 평가; 전체 보류 및 실제 유면 소실로 미채택 종료 |

## 2026-10-08 next-work intake additions

폴더별 파일명순이며, 최초 Git 추가일은 `df74414`의 author 날짜(KST)로 확인했습니다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-08 | [Next-work intake](60-evidence/s11/2026-10-08-next-work-intake.md) | 첨부 원본 등록, Work Plan 의무 보존, 별도 결과 폴더 압축·복구 검증 및 제거 |
| 2026-10-08 | [Supplied specification](70-reference/s11-next-work-2026-10-08/S11-next-work-spec-2026-10-08.md) | 외부 계획 원문 bytes 보존; D 작업과 기존 O/W 단계 연결 |
| 2026-10-08 | [Shared verification](70-reference/s11-next-work-2026-10-08/S11-next-work-verification-2026-10-08.json) | 전달받은 검증 요약 원본; 현지 receipt의 동일 복사본 아님 |
| 2026-10-08 | [Import manifest](70-reference/s11-next-work-2026-10-08/import-manifest.json) | 원본 hash, 고정 commit 출처, 로컬 보존 위치 |
| 2026-10-08 | [Results cleanup receipt](70-reference/s11-next-work-2026-10-08/results-cleanup-receipt.json) | 279개 파일의 로컬 압축 보존·복원 검증 후 sibling 결과 폴더 제거 |

## D2 control preflight additions

아래 파일의 최초 Git 등록일은 D2 preflight 추가 커밋의 author 날짜(KST) 기준이다.

| 최초 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-08 | [D2 control query](50-diagnostics/s11/2026-10-08-d2-control-query.json) | 기존 Windows target snapshot 한 case의 조회 pin·범위; 모델 freeze 아님 |
| 2026-10-08 | [D2 control preflight](60-evidence/s11/2026-10-08-d2-control-preflight.md) | 기존 대조/실패 경계, owner 재사용 검증, 필요한 Windows 반환 범위 |

## D2 region-connectivity feasibility additions

아래 파일은 동일한 합성 연결성 실험의 근거와 기계 receipt이다.

| 최초 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-08 | [D2 region-connectivity feasibility](60-evidence/s11/2026-10-08-d2-region-connectivity-feasibility.md), [receipt](60-evidence/s11/2026-10-08-d2-region-connectivity-feasibility.json) | 이상적 영역 연결성의 정보 이득과 단독 identity 한계; 실제 영상 실행 없이 미채택 종료 |

## D2 contact-observability preflight additions

| 최초 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-08 | [D2 contact-observability preflight](60-evidence/s11/2026-10-08-d2-contact-observability.md), [receipt](60-evidence/s11/2026-10-08-d2-contact-observability.json) | 기존 Mac 원본·후보 결합 검증과 국소 윤곽 접촉 관계의 사용자 판단용 표시; 분류기 실행 아님 |

## D2 saved-edge contact readout additions

| 최초 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-08 | [D2 saved-edge contact](60-evidence/s11/2026-10-08-d2-saved-edge-contact.md), [receipt](60-evidence/s11/2026-10-08-d2-saved-edge-contact.json) | 고정된 윤곽 가지 측정의 153후보 실행; 실제 접촉 관계를 재현하지 못해 미채택 종료 |

## D2 ordered-column clearance additions

| 최초 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-08 | [D2 column clearance](60-evidence/s11/2026-10-08-d2-column-clearance.md), [receipt](60-evidence/s11/2026-10-08-d2-column-clearance.json) | 153후보의 순서 보존 윤곽 거리 측정·시각 판독; f1260 국소 돌출 해석 질문과 출처 |
| 2026-10-08 | [D2 optical-reference receipt](60-evidence/s11/2026-10-08-d2-optical-reference.json) | 유리 반원 사용자 판독과 기존 3장 기준 재구성; 해석은 D2 column clearance 기록에 이어서 보존 |

## D2 existing recipe artifact comparison additions

| 최초 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-08 | [D2 recipe artifact comparison](60-evidence/s11/2026-10-08-d2-recipe-artifact-comparison.md), [receipt](60-evidence/s11/2026-10-08-d2-recipe-artifact-comparison.json) | 기존 구조물 등록의 실제 후보·UI 결합, 153후보 비교와 0–56초 전체 경로 비교; 위치 충돌·후속 유면 선택 손실로 실험 recipe 미채택 |
| 2026-10-08 | [D2 registration sequence causality](50-diagnostics/s11/2026-10-08-d2-registration-sequence-causality.md), [receipt](50-diagnostics/s11/2026-10-08-d2-registration-sequence-causality.json) | 저장 후보의 226개 결과 완전 재현, 묶음·추적·선택 손실 원인과 효과 없는 상호 대응 수정안 보존; 운영 코드 변경 없음 |
| 2026-10-08 | [D2 registered support design](60-evidence/s11/2026-10-08-d2-registered-support-design.md), [receipt](60-evidence/s11/2026-10-08-d2-registered-support-design.json) | 구조물 등록이 잃는 픽셀 정보의 재현·충돌 대조와 원본 근거 보존 설계; 추가 수동 지정의 허용 범위 판단 대기 |
| 2026-10-08 | [D2 reference capture UI](60-evidence/s11/2026-10-08-d2-reference-ui.md), [receipt](60-evidence/s11/2026-10-08-d2-reference-ui.json) | 사용자 승인에 따른 원본·윤곽 미리보기, 선택 범위·명시적 판독·프로필 보존 구현과 로컬 검증; 검출 판정 불변 |

## 18885d2 detector specification intake additions

2026-10-08 intake 커밋에 최초 등록. 원본과 현행 계약을 구분하며,
같은 원본을 수정해 진행 상태로 바꾸지 않는다.

| 최초 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-08 | [Intake review](60-evidence/s11/2026-10-08-spec-18885d2-intake.md), [machine record](60-evidence/s11/2026-10-08-spec-18885d2-intake.json) | 전체 첨부 검토·배치, 타당성 및 D2 준비성/진단/효과 게이트 보완 |
| 2026-10-08 | [Fresh replay preflight](60-evidence/s11/2026-10-08-spec-18885d2-replay-preflight.json), [receipt](60-evidence/s11/2026-10-08-spec-18885d2-replay-receipt.json) | 첨부 helper의 실제 재실행: 230 input pins, 226 complete outputs 불변 |
| 2026-10-08 | [Supplied README](70-reference/s11-detector-work-spec-18885d2-2026-10-08/README.md), [specification](70-reference/s11-detector-work-spec-18885d2-2026-10-08/S11-detector-design-and-work-spec-18885d2-2026-10-08.md) | 전달 원문 bytes 보존; D2–D6의 추가 설계 근거 |
| 2026-10-08 | [Verification summary](70-reference/s11-detector-work-spec-18885d2-2026-10-08/verification-summary.json), [SHA256SUMS](70-reference/s11-detector-work-spec-18885d2-2026-10-08/SHA256SUMS.txt), [replay helper](70-reference/s11-detector-work-spec-18885d2-2026-10-08/reproduce_saved_sequence_audit.py) | 전달 원문 bytes 보존; helper는 exact-head 역사 재현용 |
| 2026-10-08 | [Import manifest](70-reference/s11-detector-work-spec-18885d2-2026-10-08/import-manifest.json) | ZIP/전체 파일 identity, native 텍스트 복사본과 로컬 PNG 위치 |
| 2026-10-08 | [Native result](70-reference/s11-detector-work-spec-18885d2-2026-10-08/native-audit/AUDIT-RESULT.md), [source runner](70-reference/s11-detector-work-spec-18885d2-2026-10-08/native-audit/inspect_samples.py), [source receipt](70-reference/s11-detector-work-spec-18885d2-2026-10-08/native-audit/source-review-receipt.json) | 첨부가 참조한 로컬 원본 별도 보존; 42프레임 표본 맥락 |
| 2026-10-08 | [Native sequence runner](70-reference/s11-detector-work-spec-18885d2-2026-10-08/native-audit/verify_saved_sequences.py), [preflight](70-reference/s11-detector-work-spec-18885d2-2026-10-08/native-audit/sequence-verification-preflight.json), [receipt](70-reference/s11-detector-work-spec-18885d2-2026-10-08/native-audit/sequence-verification-receipt.json) | 첨부가 참조한 감사 당시 실행·입력 pin 원본 별도 보존 |

## D2-A0 reference readiness additions

| 최초 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-08 | [Reference readiness](60-evidence/s11/2026-10-08-d2-reference-readiness.md), [readout](60-evidence/s11/2026-10-08-d2-reference-readiness.json) | 기존 7개 recipe·153개 후보의 참조/측정 근거 확인과 44초 윤곽 범위의 새 물리적 판정 지점; detector·라벨 불변 |

## D2 reference measurement comparison additions

| 최초 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-09 | [Reference measurement diagnostic](60-evidence/s11/2026-10-09-d2-reference-measurement-comparison.md), [receipt](60-evidence/s11/2026-10-09-d2-reference-measurement-comparison.json) | 44초 125개 유리 윤곽의 사용자 판정과 진단 구현·출력 동일성 검증; 42.5초 겹침 여부 판정 지점 |
| 2026-10-09 | [Reference + sequence-context feasibility](60-evidence/s11/2026-10-09-d2-sequence-context-feasibility.md), [receipt](60-evidence/s11/2026-10-09-d2-sequence-context-feasibility.json) | 대략적 Foam 판독 반영, 기존 156개 추적/6,240개 연결과 등록 참조 대조; 겹침·지속성의 자동 판정 승격 보류 |


## Local XY specification intake additions

| 최초 등록일 | 문서/산출물 | 역할 |
|---|---|---|
| 2026-10-09 | [Local XY intake](60-evidence/s11/2026-10-09-local-xy-spec-intake.md) | 명세 타당성·설계 보완·WP1–WP5 대응과 로컬 재현 한계 |
| 2026-10-09 | [Intake verification](60-evidence/s11/2026-10-09-local-xy-spec-intake.json) | 165개 파일 목록·hash와 751개 saved completed 결과 재현 |
| 2026-10-09 | [Package routing](70-reference/s11-local-xy-2026-10-09/README.md) | 원문/현지 원본/검증 도구와 보존 위치 |
| 2026-10-09 | [Supplied specification](70-reference/s11-local-xy-2026-10-09/S11_Local_XY_Detector_Work_Spec_2026-10-09.md) | 원문 bytes 보존; production 미채택 |
| 2026-10-09 | [Supplied summary](70-reference/s11-local-xy-2026-10-09/S11_Local_XY_Execution_Summary_2026-10-09.json) | ZIP 및 별도 첨부가 동일; 파생 요약 원문 |
| 2026-10-09 | [Supplied handoff](70-reference/s11-local-xy-2026-10-09/HANDOFF.md) | 전달 시점 인계 원문; Work Plan이 현재 상태 소유 |
| 2026-10-09 | [Supplied checksums](70-reference/s11-local-xy-2026-10-09/SHA256SUMS.json) | 원문 파일 3개 SHA-256 |
| 2026-10-09 | [Import manifest](70-reference/s11-local-xy-2026-10-09/import-manifest.json) | 원문과 native 복사본 대응·전체 local ZIP hash |
| 2026-10-09 | [Intake verifier](70-reference/s11-local-xy-2026-10-09/verify_saved_outputs.py) | 영상 decode 없이 saved resolver·집계·파일 무결성 확인 |
| 2026-10-09 | [native-evidence/base_sample_1-baseline/summary.json](70-reference/s11-local-xy-2026-10-09/native-evidence/base_sample_1-baseline/summary.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/compact-summary.json](70-reference/s11-local-xy-2026-10-09/native-evidence/compact-summary.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/contract-results.json](70-reference/s11-local-xy-2026-10-09/native-evidence/contract-results.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/detailed-summary.json](70-reference/s11-local-xy-2026-10-09/native-evidence/detailed-summary.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/foam-comparison.png](70-reference/s11-local-xy-2026-10-09/native-evidence/foam-comparison.png) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/focused-tests.log](70-reference/s11-local-xy-2026-10-09/native-evidence/focused-tests.log) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/governance-check.log](70-reference/s11-local-xy-2026-10-09/native-evidence/governance-check.log) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/inspect_supporting_media.py](70-reference/s11-local-xy-2026-10-09/native-evidence/inspect_supporting_media.py) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/measurement-scope-preflight.json](70-reference/s11-local-xy-2026-10-09/native-evidence/measurement-scope-preflight.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/measurement-scope-results.json](70-reference/s11-local-xy-2026-10-09/native-evidence/measurement-scope-results.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/oil-comparison.png](70-reference/s11-local-xy-2026-10-09/native-evidence/oil-comparison.png) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/other-samples-original-rois.jpg](70-reference/s11-local-xy-2026-10-09/native-evidence/other-samples-original-rois.jpg) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/pair-control-preflight.json](70-reference/s11-local-xy-2026-10-09/native-evidence/pair-control-preflight.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/preflight.json](70-reference/s11-local-xy-2026-10-09/native-evidence/preflight.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/probe-preflight.json](70-reference/s11-local-xy-2026-10-09/native-evidence/probe-preflight.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/probe_contracts.py](70-reference/s11-local-xy-2026-10-09/native-evidence/probe_contracts.py) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/real-support-readout.json](70-reference/s11-local-xy-2026-10-09/native-evidence/real-support-readout.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/results.json](70-reference/s11-local-xy-2026-10-09/native-evidence/results.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/run_measurement_scope.py](70-reference/s11-local-xy-2026-10-09/native-evidence/run_measurement_scope.py) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/run_pair_control.py](70-reference/s11-local-xy-2026-10-09/native-evidence/run_pair_control.py) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/run_xy.py](70-reference/s11-local-xy-2026-10-09/native-evidence/run_xy.py) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/runner-pin.json](70-reference/s11-local-xy-2026-10-09/native-evidence/runner-pin.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/sample2-baseline/summary.json](70-reference/s11-local-xy-2026-10-09/native-evidence/sample2-baseline/summary.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/sample3-baseline/summary.json](70-reference/s11-local-xy-2026-10-09/native-evidence/sample3-baseline/summary.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/sample4-baseline/summary.json](70-reference/s11-local-xy-2026-10-09/native-evidence/sample4-baseline/summary.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/sample4-local_xy_rectangle/summary.json](70-reference/s11-local-xy-2026-10-09/native-evidence/sample4-local_xy_rectangle/summary.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/sample4-oil_measurement_only/summary.json](70-reference/s11-local-xy-2026-10-09/native-evidence/sample4-oil_measurement_only/summary.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/sample4-oil_measurement_paired_phase/summary.json](70-reference/s11-local-xy-2026-10-09/native-evidence/sample4-oil_measurement_paired_phase/summary.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/sample4-original-controls.jpg](70-reference/s11-local-xy-2026-10-09/native-evidence/sample4-original-controls.jpg) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/sample4-paired_phase_no_exclusion/summary.json](70-reference/s11-local-xy-2026-10-09/native-evidence/sample4-paired_phase_no_exclusion/summary.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/summarize_experiments.py](70-reference/s11-local-xy-2026-10-09/native-evidence/summarize_experiments.py) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |
| 2026-10-09 | [native-evidence/supporting-media-receipt.json](70-reference/s11-local-xy-2026-10-09/native-evidence/supporting-media-receipt.json) | 실험 당시 native bytes 보존; 문서 원본/제품 코드와 구분 |

## 2026-10-10 cc17924 handoff intake additions

원문·실험은 2026-10-09, intake와 최초 Git 등록은 2026-10-10이다 (`5c596a7`, author KST).

| 최초 Git 추가일 | 문서/산출물 | 역할 |
|---|---|---|
| 2026-10-10 | [Intake review](60-evidence/s11/2026-10-10-cc17924-handoff-intake.md) | 명세 검토·채택 조건; 현재 순서는 Work Plan 소유 |
| 2026-10-10 | [Intake verification](60-evidence/s11/2026-10-10-cc17924-handoff-intake.json) | 220개 로컬 inventory와 H0/G1 각 198개 저장 결정 검증 |
| 2026-10-10 | [README.md](70-reference/s11-detector-handoff-cc17924-2026-10-09/README.md) | 첨부 원문 bytes 보존; 원문 작성 2026-10-09 |
| 2026-10-10 | [S11-detector-design-work-spec-cc17924-2026-10-09.md](70-reference/s11-detector-handoff-cc17924-2026-10-09/S11-detector-design-work-spec-cc17924-2026-10-09.md) | 첨부 원문 bytes 보존; 원문 작성 2026-10-09 |
| 2026-10-10 | [S11-execution-summary-cc17924-2026-10-09.json](70-reference/s11-detector-handoff-cc17924-2026-10-09/S11-execution-summary-cc17924-2026-10-09.json) | 첨부 원문 bytes 보존; 원문 작성 2026-10-09 |
| 2026-10-10 | [SHA256SUMS.txt](70-reference/s11-detector-handoff-cc17924-2026-10-09/SHA256SUMS.txt) | 첨부 원문 bytes 보존; 원문 작성 2026-10-09 |
| 2026-10-10 | [delivery-validation.json](70-reference/s11-detector-handoff-cc17924-2026-10-09/delivery-validation.json) | 첨부 원문 bytes 보존; 원문 작성 2026-10-09 |
| 2026-10-10 | [verify_local_evidence.py](70-reference/s11-detector-handoff-cc17924-2026-10-09/verify_local_evidence.py) | 첨부 원문 bytes 보존; 원문 작성 2026-10-09 |
| 2026-10-10 | [Import manifest](70-reference/s11-detector-handoff-cc17924-2026-10-09/import-manifest.json) | 6개 첨부·21개 native 복사본·219개 로컬 archive의 대응 |
| 2026-10-10 | [native-evidence/base_sample_1-source-review.png](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/base_sample_1-source-review.png) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/center-projection-ablation-preflight.json](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/center-projection-ablation-preflight.json) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/center-projection-ablation.json](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/center-projection-ablation.json) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/center_projection_ablation.py](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/center_projection_ablation.py) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/closeout.json](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/closeout.json) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/foam-positive-partition-review.png](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/foam-positive-partition-review.png) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/focused-tests.log.txt](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/focused-tests.log.txt) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/inspect_visuals.py](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/inspect_visuals.py) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/oil-late-ablation-review.png](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/oil-late-ablation-review.png) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/oil-positive-partition-review.png](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/oil-positive-partition-review.png) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/partition-trial/preflight.json](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/partition-trial/preflight.json) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/partition-trial/readout.json](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/partition-trial/readout.json) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/sample2-source-review.png](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/sample2-source-review.png) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/sample3-source-review.png](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/sample3-source-review.png) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/sample4-source-review.png](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/sample4-source-review.png) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/side_partition_probe.py](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/side_partition_probe.py) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/verification-correction.txt](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/verification-correction.txt) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/verification.json](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/verification.json) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/verify_probe.py](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/verify_probe.py) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/visual-preflight.json](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/visual-preflight.json) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |
| 2026-10-10 | [native-evidence/visual-review.json](70-reference/s11-detector-handoff-cc17924-2026-10-09/native-evidence/visual-review.json) | 실험 당시 native bytes 보존; production/test discovery 밖의 원본 |

## 2026-10-10 CBR-1 comparison additions

이 변경에서 처음 Git에 등록한 CBR-1 실행·검증 자료다. 현재 순서는 Work Plan이 소유한다.

| 최초 Git 추가일(KST) | 파일 | 역할 |
|---|---|---|
| 2026-10-10 | [Comparison and causal review](50-diagnostics/s11/2026-10-10-current-boundary-reference.md) | 198개 고정 질의와 비채택 근거 |
| 2026-10-10 | [Preservation record](50-diagnostics/s11/2026-10-10-current-boundary-reference.json) | native 206개 inventory, 8개 Git 복사본과 로컬 archive hash |
| 2026-10-10 | [Preflight](50-diagnostics/s11/2026-10-10-current-boundary-reference/preflight.json) | 결과 전 고정한 입력·연산·자원·진전 조건 |
| 2026-10-10 | [Readout](50-diagnostics/s11/2026-10-10-current-boundary-reference/readout.json) | 전체 query 요약과 native detail hash |
| 2026-10-10 | [Verification](50-diagnostics/s11/2026-10-10-current-boundary-reference/verification.json) | 원본 배열 기반 독립 재계산 결과 |
| 2026-10-10 | [Frozen runner](50-diagnostics/s11/2026-10-10-current-boundary-reference/run.py) | 원 실행 코드 보존; docs 경로에서 실행하지 않음 |
| 2026-10-10 | [Saved-pixel verifier](50-diagnostics/s11/2026-10-10-current-boundary-reference/verify.py) | 원 검증 코드 보존; docs 경로에서 실행하지 않음 |
| 2026-10-10 | [Foam source/overlay](50-diagnostics/s11/2026-10-10-current-boundary-reference/foam-positive-review.png) | 사전 지정 프레임의 원본과 후보 |
| 2026-10-10 | [Oil source/overlay](50-diagnostics/s11/2026-10-10-current-boundary-reference/oil-positive-review.png) | 사전 지정 프레임의 원본과 후보 |
| 2026-10-10 | [Structure source/overlay](50-diagnostics/s11/2026-10-10-current-boundary-reference/rim-opposition-review.png) | 공통 참조 X 부재를 물리적 거부와 구별 |

## 2026-10-10 local truth qualification additions

Seven-video source and annotation audit; original truth and historical results
are preserved. Current state and future acceptance remain in their existing owners.
The first-addition author date was checked from Git in Asia/Seoul.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-10 | [Local truth and evaluation audit](60-evidence/s11/2026-10-10-local-truth-and-evaluation-audit.md) | 기존 15개 주석의 출처·불확실성과 7개 영상의 구간별 평가 용도 |
| 2026-10-10 | [Audit machine record](60-evidence/s11/2026-10-10-local-truth-and-evaluation-audit.json) | 입력 hash, 주석별 자격, 원본 확인 및 재현 코드; 새 정답 형식 아님 |

## 2026-10-10 water-first source qualification additions

Ten fixed development frames and a bounded post-pour material-role review.
No new detector or numeric truth is adopted.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-10 | [Water source qualification](50-diagnostics/s11/2026-10-10-water-first-source-qualification.md) | f205 유입 장면 정정, 41초대 물/거품 역할 질문과 기존 잔차 연산 결과 |
| 2026-10-10 | [Machine record](50-diagnostics/s11/2026-10-10-water-first-source-qualification.json) | 사전 입력·연산 고정, 전체 결과·검증·원본 코드와 hash |
| 2026-10-10 | [All ten frames](50-diagnostics/s11/2026-10-10-water-first-all-cases.png) | 전체 사례 원본 개요; 정답·후보 표식 없음 |
| 2026-10-10 | [Physical role review](50-diagnostics/s11/2026-10-10-water-first-water-role-review.png) | 41.108 / 47.981 / 54.821초 원본과 중앙 확대 |
| 2026-10-10 | [Immediate sampled context](50-diagnostics/s11/2026-10-10-water-first-water-role-neighbours.png) | f1225/f1232/f1239의 원본 확대 |
| 2026-10-10 | [Empty-reference differences](50-diagnostics/s11/2026-10-10-water-first-water-reference-difference.png) | f205/f1643 원본과 밝기 차이; 물리 분류 아님 |

## 2026-10-10 water Foam role and representation additions

The source-bound Foam reply and unchanged-owner support/stage readout.
No new physical contour labels or detector behavior are adopted.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-10 | [Foam role reply](50-diagnostics/s11/2026-10-10-water-foam-role-reply.json) | A/f1232 거품층 확인; 정확한 경계·인접 프레임 판정은 포함하지 않음 |
| 2026-10-10 | [Representation investigation](50-diagnostics/s11/2026-10-10-water-foam-representation.md) | 10개 고정 프레임의 기존 후보와 A 중앙 지지 소실 원인 |
| 2026-10-10 | [Machine record](50-diagnostics/s11/2026-10-10-water-foam-representation.json) | 사전 조건, 전체 단계 결과·코드·검증과 실패한 최초 실행 보존 |
| 2026-10-10 | [Complete component readout](50-diagnostics/s11/2026-10-10-water-foam-support-readout.json.gz) | 전체 718개 성분, 경계면 집계·중앙 교점의 원본 JSON을 압축 보존 |
| 2026-10-10 | [A support and perimeters](50-diagnostics/s11/2026-10-10-water-foam-support.png) | 원본·잔존 지지·모든 경계면 비교; 물리 정답 아님 |
| 2026-10-10 | [Fixed source contexts](50-diagnostics/s11/2026-10-10-water-foam-context-support.png) | 미리 고른 다섯 장면의 동일 영역 비교 |
| 2026-10-10 | [A central stages](50-diagnostics/s11/2026-10-10-water-foam-center-stages.png) | 기존 밝기 조건 이전의 윤곽과 단계별 중앙 지지 보존 여부 |
| 2026-10-10 | [Lower-interface visibility reply](50-diagnostics/s11/2026-10-10-water-lower-interface-reply.json) | A의 아래 물–거품 경계 불명확; 거품 존재와 아래 좌표 평가 자격을 구분 |

## 2026-10-10 ordered temporal-texture observation additions

Frozen source-bound investigation; current sequencing remains in Work Plan.
Native arrays and the verified archive remain local and are indexed by the machine record.

| 최초 Git 추가일(KST) | 파일 | 역할 |
|---|---|---|
| 2026-10-10 | [Temporal observation](50-diagnostics/s11/2026-10-10-temporal-texture-observation.md) | 17개 고정 사례의 시간순 무늬 변화, 광학 반례와 비채택 근거 |
| 2026-10-10 | [Machine record](50-diagnostics/s11/2026-10-10-temporal-texture-observation.json) | 네 실행의 preflight·실패·코드, 60개 native 파일과 독립 검산 |
| 2026-10-10 | [Complete readout](50-diagnostics/s11/2026-10-10-temporal-texture-readout.json.gz) | 235개 프레임 질의와 전체 1,754개 경계 주변 비교 |
| 2026-10-10 | [Water first five](50-diagnostics/s11/2026-10-10-temporal-texture-water-1.png) | f0/205/815/822/829 원본과 네 고정 변화 지도 |
| 2026-10-10 | [Water last five](50-diagnostics/s11/2026-10-10-temporal-texture-water-2.png) | f1225/1232/1239/1438/1643; 시간 누락 포함 |
| 2026-10-10 | [Sample4 all controls](50-diagnostics/s11/2026-10-10-temporal-texture-sample4.png) | 기존 일곱 대조 시점 전체 |
| 2026-10-10 | [A detailed maps](50-diagnostics/s11/2026-10-10-temporal-texture-A.png) | A의 원본과 변화 영역; 물리적 거품 mask나 경계 정답 아님 |
| 2026-10-10 | [Later-water role review](50-diagnostics/s11/2026-10-10-later-water-role-review.png) | 미검토 B/C 상단 띠의 거품 유무 판단용 원본 |

## 2026-10-10 later-water reply and source-feature review additions

| 최초 Git 추가일(KST) | 파일 | 역할 |
|---|---|---|
| 2026-10-10 | [B/C role reply](50-diagnostics/s11/2026-10-10-later-water-role-reply.json) | 두 장면의 거품층 없는 수면 확인; 개별 윤곽·수치 정답으로 확대하지 않음 |
| 2026-10-10 | [B source-feature preparation](50-diagnostics/s11/2026-10-10-water-surface-feature-review.json) | 기존 원본·좌표·표식의 출처와 화소 동일성; 수면 위치 기준 전제 확인 |
| 2026-10-10 | [B clean/marked detail](50-diagnostics/s11/2026-10-10-water-surface-feature-review.png) | 위쪽 약한 부분 1과 아래쪽 굵은 띠 2의 물리적 관계 판단용; 검출·정답 아님 |
| 2026-10-10 | [B same-surface reply](50-diagnostics/s11/2026-10-10-water-surface-feature-reply.json) | 두 부분이 같은 수면의 앞뒤임을 확인; 높이 기준 윤곽·정확한 좌표는 별도 |

## 2026-10-10 upper-projection choice and reference preparation

| 최초 Git 추가일(KST) | 파일 | 역할 |
|---|---|---|
| 2026-10-10 | [Upper-projection choice](50-diagnostics/s11/2026-10-10-upper-projection-choice.json) | 고정 중앙 열에서 같은 수면의 위쪽 윤곽을 읽는 기준 채택 |
| 2026-10-10 | [Reference preparation](50-diagnostics/s11/2026-10-10-upper-projection-reference.md) | 기존 추출기 재사용, 원시 경계와 물리적 정답 구분, B 위치 범위 검토 |
| 2026-10-10 | [Preparation machine record](50-diagnostics/s11/2026-10-10-upper-projection-reference.json) | 원본·배열·좌표·제안 범위의 출처와 전체 중앙 열 관측 |
| 2026-10-10 | [B proposed source interval](50-diagnostics/s11/2026-10-10-upper-projection-reference-review.png) | B 검토 당시 원본·표식; 승인 답변은 별도 파일로 보존 |
| 2026-10-10 | [B interval reply](50-diagnostics/s11/2026-10-10-upper-projection-interval-reply.json) | X950의 B 수면 위치 불확실성 범위를 승인한 사용자 답변 |
| 2026-10-10 | [B material-path interval audit](50-diagnostics/s11/2026-10-10-b-material-path-interval.md) | 기존 경로 최적화에서 중앙 위치 후보를 잃는 단계 확인 |
| 2026-10-10 | [B lane machine record](50-diagnostics/s11/2026-10-10-b-material-path-interval.json) | 두 고정 축척의 전체 원래 시드·경로·원인 확인과 재현 스크립트 |
| 2026-10-10 | [B sampling geometry](50-diagnostics/s11/2026-10-10-b-material-path-interval.png) | 승인 범위와 기존 후보의 실제 섹터 표본 위치 |
| 2026-10-10 | [A/C source review record](50-diagnostics/s11/2026-10-10-upper-projection-ac-review.json) | A 거품 상단·C 수면의 독립적인 위치 범위 제안; 미검토 |
| 2026-10-10 | [A/C source review](50-diagnostics/s11/2026-10-10-upper-projection-ac-review.png) | 원본 확대와 두 위치 범위를 묶은 사용자 검토 이미지 |

## 2026-10-10 reviewed A/C intervals and evaluation qualification

| 최초 Git 추가일(KST) | 파일 | 역할 |
|---|---|---|
| 2026-10-10 | [A/C interval reply](50-diagnostics/s11/2026-10-10-upper-projection-ac-reply.json) | 두 범위 승인 답변; A의 아래 경계 불명확 상태 유지 |
| 2026-10-10 | [A/B/C comparison](50-diagnostics/s11/2026-10-10-abc-source-interval-comparison.md) | 세 위치 기준과 기존 검출 표현 비교, 13개 과거 좌표 비교의 의미 명시 |
| 2026-10-10 | [Comparison machine record](50-diagnostics/s11/2026-10-10-abc-source-interval-comparison.json) | 고정 입력·전체 배열 비교·실패 보존·독립 검산·CLI 검증 |
| 2026-10-10 | [sample4 source qualification](50-diagnostics/s11/2026-10-10-sample4-center-source-review.md) | 기존 실제 Oil 사례 한 장의 중앙 위치 평가 가능성 질문 |
| 2026-10-10 | [sample4 preparation record](50-diagnostics/s11/2026-10-10-sample4-center-source-review.json) | 원본 crop 좌표·기존 Recipe 중앙 열·제안 범위·질문과 검산 |
| 2026-10-10 | [sample4 clean/marked source](50-diagnostics/s11/2026-10-10-sample4-center-source-review.png) | 42.5초 원본 6배 확대와 미검토 위치 범위; 검출 출력 아님 |
| 2026-10-10 | [sample4 interval reply](50-diagnostics/s11/2026-10-10-sample4-center-source-reply.json) | X595/833–841행의 위치 범위 승인; 과거 정답 파일·원본 제안 보존 |
| 2026-10-10 | [sample4 saved comparison](50-diagnostics/s11/2026-10-10-sample4-center-interval-comparison.md) | 저장된 후보 20개와 최종 Y835 비교; 단독 프레임 부재와 최종 성공 구분 |
| 2026-10-10 | [sample4 comparison record](50-diagnostics/s11/2026-10-10-sample4-center-interval-comparison.json) | 원본·전체 후보·선택 출처·화소 검산 및 실패 시도 보존 |
| 2026-10-10 | [Temporal usefulness question](50-diagnostics/s11/2026-10-10-temporal-usefulness-question.json) | 움직이는 유면을 판독하는 데 필요한 관측 간격 제안; 영상의 정답·위치 오차와 분리 |

## 2026-10-10 accepted Oil cadence and saved-output measurement

| 최초 Git 추가일(KST) | 파일 | 역할 |
|---|---|---|
| 2026-10-10 | [Temporal usefulness reply](50-diagnostics/s11/2026-10-10-temporal-usefulness-reply.json) | 가시적으로 움직이는 같은 Oil 유면의 관측 간격을 1초 이내 개발 목표로 승인 |
| 2026-10-10 | [Cadence evidence](60-evidence/s11/2026-10-10-oil-observation-cadence.md) | 기존 네 저장 결과의 실제 관측 간격과 sample4의 확인된 움직임 구간 비교 |
| 2026-10-10 | [Complete cadence record](50-diagnostics/s11/2026-10-10-oil-cadence-readout.json.gz) | 299개 원본 행·전체 간격·입력 해시·독립 검산·기존 물리 판단 연결 |
| 2026-10-10 | [Cadence gap capture](50-diagnostics/s11/2026-10-10-cadence-gap-capture.md) | 기존 출력과 같은 전체 재생에서 43/43.5초 누락의 최종 추적 ID 제한 확인 |
| 2026-10-10 | [Gap capture record](50-diagnostics/s11/2026-10-10-cadence-gap-capture.json.gz) | 기존 일곱 대조군과 새 두 프레임의 후보·선택 증거·원본·검산 보존 |
| 2026-10-10 | [43.5s relation question](50-diagnostics/s11/2026-10-10-cadence-gap-source-review.json) | 서로 다른 탈락 단계를 거친 두 후보 위치의 실제 Oil 관계 질문 |
| 2026-10-10 | [43.5s clean/marked source](50-diagnostics/s11/2026-10-10-cadence-gap-source-review.png) | 원본과 두 표시 비교; 위치 범위나 후보의 물리 정답으로 채택하지 않음 |

## 2026-10-10 sample3 retirement handoff

| 최초 Git 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-10 | [sample3 retirement handoff](60-evidence/s11/2026-10-10-sample3-retirement-handoff.md) | 기본 실행 제한·37개 검사·보존 범위·재개 순서를 묶은 인수인계 체크포인트 |


## 2026-10-11 isolated P1 implementation

| 최초 Git 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-11 | [P1 frozen preflight](50-diagnostics/s11/2026-10-11-center-path-preflight.json) | 기존 23조건·입력 해시·원래 그래프·예산 고정; source admission guard 사용 |
| 2026-10-11 | [P1 complete readout](50-diagnostics/s11/2026-10-11-center-path-trial.json) | 중앙 위치 대안 보존과 기존 출력 불변성; 물리 identity·field 효능 아님 |
| 2026-10-11 | [P1 implementation evidence](60-evidence/s11/2026-10-11-center-path-implementation.md) | 구현·oracle·실사·자원 검증과 직접 승격 기각; 현행 작업 권한 변경 없음 |

## 2026-10-11 program review and P1 closeout intake

원문 작성일과 최초 Git 등록일을 구분한다. 아래 87파일은 신규 보존 사본의 정확한 경로별 A 이력(`5631f1a`, author KST)으로 등록일을 확인했다. 빈 로그에 대한 자동 copy 추정은 과거 다른 빈 파일의 날짜를 물려주므로 사용하지 않았다. 두 import manifest가 원본 경로·hash와 중복 제거 대응을 소유한다.

| 최초 Git 등록일 | 파일 | 역할 |
|---|---|---|
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-intake/candidate-pytest.log.txt](60-evidence/s11/2026-10-11-program-intake/candidate-pytest.log.txt) | 이번 로컬 인수·통합·검증 기록 |
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-intake/candidate-pytest.xml](60-evidence/s11/2026-10-11-program-intake/candidate-pytest.xml) | 이번 로컬 인수·통합·검증 기록 |
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-intake/integrated-pytest.log.txt](60-evidence/s11/2026-10-11-program-intake/integrated-pytest.log.txt) | 이번 로컬 인수·통합·검증 기록 |
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-intake/integrated-pytest.xml](60-evidence/s11/2026-10-11-program-intake/integrated-pytest.xml) | 이번 로컬 인수·통합·검증 기록 |
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-intake/preflight.json](60-evidence/s11/2026-10-11-program-intake/preflight.json) | 이번 로컬 인수·통합·검증 기록 |
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-intake/prepare.log.txt](60-evidence/s11/2026-10-11-program-intake/prepare.log.txt) | 이번 로컬 인수·통합·검증 기록 |
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-intake/readout.json](60-evidence/s11/2026-10-11-program-intake/readout.json) | 이번 로컬 인수·통합·검증 기록 |
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-intake/replay.log.txt](60-evidence/s11/2026-10-11-program-intake/replay.log.txt) | 이번 로컬 인수·통합·검증 기록 |
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-intake.json](60-evidence/s11/2026-10-11-program-intake.json) | 이번 로컬 인수·통합·검증 기록 |
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-intake.md](60-evidence/s11/2026-10-11-program-intake.md) | 이번 로컬 인수·통합·검증 기록 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/README.md](70-reference/s11-center-path-closeout-2026-10-11/README.md) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/SHA256SUMS.txt](70-reference/s11-center-path-closeout-2026-10-11/SHA256SUMS.txt) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/candidate-files/docs/50-diagnostics/s11/2026-10-11-center-path-preflight.json](70-reference/s11-center-path-closeout-2026-10-11/candidate-files/docs/50-diagnostics/s11/2026-10-11-center-path-preflight.json) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/candidate-files/docs/50-diagnostics/s11/2026-10-11-center-path-trial.json](70-reference/s11-center-path-closeout-2026-10-11/candidate-files/docs/50-diagnostics/s11/2026-10-11-center-path-trial.json) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/candidate-files/docs/60-evidence/s11/2026-10-11-center-path-implementation.md](70-reference/s11-center-path-closeout-2026-10-11/candidate-files/docs/60-evidence/s11/2026-10-11-center-path-implementation.md) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/candidate-files/scripts/s11_center_path_trial.py](70-reference/s11-center-path-closeout-2026-10-11/candidate-files/scripts/s11_center_path_trial.py) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/candidate-files/tests/test_center_path_diagnostics.py](70-reference/s11-center-path-closeout-2026-10-11/candidate-files/tests/test_center_path_diagnostics.py) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/governance.log](70-reference/s11-center-path-closeout-2026-10-11/governance.log) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/implementation.patch](70-reference/s11-center-path-closeout-2026-10-11/implementation.patch) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/import-manifest.json](70-reference/s11-center-path-closeout-2026-10-11/import-manifest.json) | 원본·보존본 hash와 중복 산출물 대응 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/implementation/finalize.py](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/implementation/finalize.py) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/implementation/pytest.log](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/implementation/pytest.log) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/implementation/pytest.xml](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/implementation/pytest.xml) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/implementation/replay-comparison.json](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/implementation/replay-comparison.json) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/implementation-delivery/PAYLOAD-SHA256SUMS.txt](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/implementation-delivery/PAYLOAD-SHA256SUMS.txt) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/preflight.json](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/preflight.json) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/pytest.log](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/pytest.log) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/pytest.xml](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/pytest.xml) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/readout.json](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/readout.json) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/resource.json](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/resource.json) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/resource_probe.py](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/resource_probe.py) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/run.py](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/initial/run.py) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/CLOSEOUT.md](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/CLOSEOUT.md) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/before.json](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/before.json) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/diff-check.log](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/diff-check.log) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/governance.log](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/governance.log) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/package_verified.py](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/package_verified.py) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/patch-apply-check.log](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/patch-apply-check.log) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/prepare.log](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/prepare.log) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/pytest.log](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/pytest.log) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/pytest.xml](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/pytest.xml) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/00-s5-empty-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/00-s5-empty-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/01-s5-empty-height_200.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/01-s5-empty-height_200.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/02-s5-inclined-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/02-s5-inclined-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/03-s5-inclined-height_200.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/03-s5-inclined-height_200.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/04-s5-settled-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/04-s5-settled-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/05-s5-settled-height_200.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/05-s5-settled-height_200.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/06-s6-empty-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/06-s6-empty-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/07-s6-empty-height_200.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/07-s6-empty-height_200.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/08-s6-forming-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/08-s6-forming-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/09-s6-forming-height_200.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/09-s6-forming-height_200.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/10-s6-layer-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/10-s6-layer-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/11-s6-layer-height_200.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/11-s6-layer-height_200.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/12-s7-empty-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/12-s7-empty-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/13-s7-empty-height_200.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/13-s7-empty-height_200.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/14-s7-pouring-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/14-s7-pouring-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/15-s7-pouring-height_200.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/15-s7-pouring-height_200.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/16-s7-settled-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/16-s7-settled-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/17-s7-settled-height_200.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/17-s7-settled-height_200.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/18-water-B-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/18-water-B-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/19-water-B-height_200.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/19-water-B-height_200.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/20-water-A-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/20-water-A-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/21-water-A-height_200.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/21-water-A-height_200.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/22-sample4-f1275-native.json.gz](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/22-sample4-f1275-native.json.gz) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/preflight.json](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/preflight.json) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/readout.json](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay/readout.json) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay.log](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/replay.log) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/resume-verification.json](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/resume-verification.json) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/resume_verify.py](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume/resume_verify.py) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume-delivery/PAYLOAD-SHA256SUMS.txt](70-reference/s11-center-path-closeout-2026-10-11/native-evidence/resume-delivery/PAYLOAD-SHA256SUMS.txt) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/prior-execution-summary.json](70-reference/s11-center-path-closeout-2026-10-11/prior-execution-summary.json) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/pytest.log](70-reference/s11-center-path-closeout-2026-10-11/pytest.log) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/replay.log](70-reference/s11-center-path-closeout-2026-10-11/replay.log) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/resume-verification.json](70-reference/s11-center-path-closeout-2026-10-11/resume-verification.json) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/s11-resume-closeout-and-follow-on-spec-2026-10-11.md](70-reference/s11-center-path-closeout-2026-10-11/s11-resume-closeout-and-follow-on-spec-2026-10-11.md) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-center-path-closeout-2026-10-11/verify_delivery.py](70-reference/s11-center-path-closeout-2026-10-11/verify_delivery.py) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-review-2026-10-10/README.md](70-reference/s11-program-review-2026-10-10/README.md) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-review-2026-10-10/SHA256SUMS.txt](70-reference/s11-program-review-2026-10-10/SHA256SUMS.txt) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-review-2026-10-10/import-manifest.json](70-reference/s11-program-review-2026-10-10/import-manifest.json) | 원본·보존본 hash와 중복 산출물 대응 |
| 2026-10-11 | [70-reference/s11-program-review-2026-10-10/native-evidence/audit/SESSION_SUMMARY.md](70-reference/s11-program-review-2026-10-10/native-evidence/audit/SESSION_SUMMARY.md) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-program-review-2026-10-10/native-evidence/audit/audit_identity.json](70-reference/s11-program-review-2026-10-10/native-evidence/audit/audit_identity.json) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-program-review-2026-10-10/native-evidence/audit/audit_readonly.py](70-reference/s11-program-review-2026-10-10/native-evidence/audit/audit_readonly.py) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-program-review-2026-10-10/native-evidence/audit/inspect_media.unexecuted.txt](70-reference/s11-program-review-2026-10-10/native-evidence/audit/inspect_media.unexecuted.txt) | 원래 로컬 실행 증거 bytes 보존; 실행 등록 아님 |
| 2026-10-11 | [70-reference/s11-program-review-2026-10-10/s11-execution-summary-2026-10-10.json](70-reference/s11-program-review-2026-10-10/s11-execution-summary-2026-10-10.json) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-review-2026-10-10/s11-handoff-2026-10-10.md](70-reference/s11-program-review-2026-10-10/s11-handoff-2026-10-10.md) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-review-2026-10-10/s11-program-audit-and-detector-work-spec-2026-10-10.md](70-reference/s11-program-review-2026-10-10/s11-program-audit-and-detector-work-spec-2026-10-10.md) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-review-2026-10-10/s11-work-packages-2026-10-10.json](70-reference/s11-program-review-2026-10-10/s11-work-packages-2026-10-10.json) | 첨부 원문 bytes 보존 |

## 2026-10-11 P2 shared-support pilot

| 최초 Git 등록일 | 문서 | 역할 |
|---|---|---|
| 2026-10-11 | [P2-S1 investigation](50-diagnostics/s11/2026-10-11-p2-shared-support.md) | 공통 관측 영역에서의 역할 참조 비교와 제한 |
| 2026-10-11 | [Frozen preflight](50-diagnostics/s11/2026-10-11-p2-shared-support/preflight.json) | 원본·후보·참조·수치 조건·중단 기준 고정 |
| 2026-10-11 | [Saved-raster runner](50-diagnostics/s11/2026-10-11-p2-shared-support/run.py) | 고정 입력 확인 후 오프라인 비교 재현 |
| 2026-10-11 | [Complete P2-S1 readout](50-diagnostics/s11/2026-10-11-p2-shared-support/readout.json) | 14개 query·15개 문맥의 joint/ablation 결과 전부 보존 |
| 2026-10-11 | [Independent verifier](50-diagnostics/s11/2026-10-11-p2-shared-support/verify.py) | 원본 픽셀에서 공통 영역과 비용을 직접 재구성 |
| 2026-10-11 | [Verification receipt](50-diagnostics/s11/2026-10-11-p2-shared-support/verification.json) | 1,650개 비용·입력·소스 불변성 검증 |
| 2026-10-11 | [P5 source-position review](50-diagnostics/s11/2026-10-11-foam-upper-position-review.md) | 거품 상단 중앙 위치의 한정된 검토 근거 |
| 2026-10-11 | [P5 review source record](50-diagnostics/s11/2026-10-11-foam-upper-position-review.json) | 제안 범위·원본 hash·렌더러·검증과 질문 보존 |
| 2026-10-11 | [P5 native-pixel review figure](50-diagnostics/s11/2026-10-11-foam-upper-position-review.png) | 54초 원본과 중앙 위치 범위 제안 |
| 2026-10-11 | [P5 qualified position reply](50-diagnostics/s11/2026-10-11-foam-upper-position-reply.json) | X595·Y812–816 한정 사용자 판단과 원본 연결 |
| 2026-10-11 | [P5 saved-position comparison](50-diagnostics/s11/2026-10-11-foam-upper-position-comparison.json) | 원시 경계·지지 영역·후보·episode 단계 대조와 검증 |
| 2026-10-11 | [P5 saved-position reproducer](50-diagnostics/s11/2026-10-11-foam-upper-position-comparison.py) | 기존 배열의 경계·원본·검증값을 독립 재구성 |

## 2026-10-11 current-main program audit intake

이번 인수 범위의 64파일. 최초 Git 추가일은 `1841f87`의 author 날짜(KST, 2026-10-11)로 확인했다.

| 최초 Git 등록일 | 문서/산출물 | 역할 |
|---|---|---|
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-audit-intake.json](60-evidence/s11/2026-10-11-program-audit-intake.json) | 이번 인수 검토·검증·중복 정리 |
| 2026-10-11 | [60-evidence/s11/2026-10-11-program-audit-intake.md](60-evidence/s11/2026-10-11-program-audit-intake.md) | 이번 인수 검토·검증·중복 정리 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/README.md](70-reference/s11-program-audit-2026-10-11/README.md) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/S11-program-audit-and-detector-work-spec.md](70-reference/s11-program-audit-2026-10-11/S11-program-audit-and-detector-work-spec.md) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/SHA256SUMS.txt](70-reference/s11-program-audit-2026-10-11/SHA256SUMS.txt) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/evidence/audit-record.json](70-reference/s11-program-audit-2026-10-11/evidence/audit-record.json) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/evidence/p2-independent-verification.json](70-reference/s11-program-audit-2026-10-11/evidence/p2-independent-verification.json) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/evidence/p5-verification-summary.json](70-reference/s11-program-audit-2026-10-11/evidence/p5-verification-summary.json) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/evidence/sample4-current-default-checkpoints.json](70-reference/s11-program-audit-2026-10-11/evidence/sample4-current-default-checkpoints.json) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/evidence/source-frame-audit.json](70-reference/s11-program-audit-2026-10-11/evidence/source-frame-audit.json) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/evidence/source-ledger.json](70-reference/s11-program-audit-2026-10-11/evidence/source-ledger.json) | 첨부 원문 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/import-manifest.json](70-reference/s11-program-audit-2026-10-11/import-manifest.json) | 원본·native·중복·컨테이너 보존 매핑 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/base_sample_1-f000150.png](70-reference/s11-program-audit-2026-10-11/native-evidence/base_sample_1-f000150.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/base_sample_1-f000151.png](70-reference/s11-program-audit-2026-10-11/native-evidence/base_sample_1-f000151.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/base_sample_1-f000240.png](70-reference/s11-program-audit-2026-10-11/native-evidence/base_sample_1-f000240.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/base_sample_1-source-sheet.png](70-reference/s11-program-audit-2026-10-11/native-evidence/base_sample_1-source-sheet.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/collect_audit.py](70-reference/s11-program-audit-2026-10-11/native-evidence/collect_audit.py) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/focused-tests.log](70-reference/s11-program-audit-2026-10-11/native-evidence/focused-tests.log) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/focused-tests.xml](70-reference/s11-program-audit-2026-10-11/native-evidence/focused-tests.xml) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/inspect_media.py](70-reference/s11-program-audit-2026-10-11/native-evidence/inspect_media.py) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/p5-independent-verification.json](70-reference/s11-program-audit-2026-10-11/native-evidence/p5-independent-verification.json) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample2-f000000.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample2-f000000.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample2-f000030.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample2-f000030.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample2-f000060.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample2-f000060.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample2-source-sheet.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample2-source-sheet.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-checkpoint-summary.json](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-checkpoint-summary.json) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-current-default.json](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-current-default.json) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-current-default.log](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-current-default.log) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-default-summary.json](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-default-summary.json) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f000420.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f000420.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f000450.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f000450.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f000480.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f000480.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001200.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001200.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001260.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001260.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001275.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001275.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001290.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001290.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001305.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001305.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001320.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001320.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001485.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001485.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001560.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001560.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001620.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001620.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001635.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001635.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001665.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001665.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001680.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-f001680.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-source-sheet.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-source-sheet.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f000000.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f000000.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f000205.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f000205.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f000815.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f000815.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f000822.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f000822.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f000829.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f000829.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f001225.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f001225.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f001232.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f001232.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f001239.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f001239.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f001438.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f001438.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f001643.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-f001643.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-source-sheet.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample5-source-sheet.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample6-f000000.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample6-f000000.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample6-f000146.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample6-f000146.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample6-f000436.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample6-f000436.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample6-source-sheet.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample6-source-sheet.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample7-f000000.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample7-f000000.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample7-f000532.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample7-f000532.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample7-f001063.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample7-f001063.png) | 로컬 감사 원본 bytes 보존 |
| 2026-10-11 | [70-reference/s11-program-audit-2026-10-11/native-evidence/sample7-source-sheet.png](70-reference/s11-program-audit-2026-10-11/native-evidence/sample7-source-sheet.png) | 로컬 감사 원본 bytes 보존 |

### 2026-10-11 P5 default linkage and signed-conjunction preflight

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-11 | [50-diagnostics/s11/2026-10-11-p5-default-linkage.md](50-diagnostics/s11/2026-10-11-p5-default-linkage.md) | P5 진단/동결 비교 |
| 2026-10-11 | [50-diagnostics/s11/2026-10-11-p5-spatial-conjunction.md](50-diagnostics/s11/2026-10-11-p5-spatial-conjunction.md) | P5 진단/동결 비교 |
| 2026-10-11 | [50-diagnostics/s11/2026-10-11-p5-default-linkage/preflight.json](50-diagnostics/s11/2026-10-11-p5-default-linkage/preflight.json) | P5 진단/동결 비교 |
| 2026-10-11 | [50-diagnostics/s11/2026-10-11-p5-default-linkage/readout.json](50-diagnostics/s11/2026-10-11-p5-default-linkage/readout.json) | P5 진단/동결 비교 |
| 2026-10-11 | [50-diagnostics/s11/2026-10-11-p5-default-linkage/verify.py](50-diagnostics/s11/2026-10-11-p5-default-linkage/verify.py) | P5 진단/동결 비교 |
| 2026-10-11 | [50-diagnostics/s11/2026-10-11-p5-spatial-conjunction/preflight.json](50-diagnostics/s11/2026-10-11-p5-spatial-conjunction/preflight.json) | P5 진단/동결 비교 |
| 2026-10-11 | [50-diagnostics/s11/2026-10-11-p5-spatial-conjunction/run.py](50-diagnostics/s11/2026-10-11-p5-spatial-conjunction/run.py) | P5 진단/동결 비교 |
| 2026-10-11 | [50-diagnostics/s11/2026-10-11-p5-default-linkage/duplicate-cleanup.json](50-diagnostics/s11/2026-10-11-p5-default-linkage/duplicate-cleanup.json) | P5 고정 비교 결과/검증 |
| 2026-10-11 | [50-diagnostics/s11/2026-10-11-p5-spatial-conjunction/readout.json](50-diagnostics/s11/2026-10-11-p5-spatial-conjunction/readout.json) | P5 고정 비교 결과/검증 |
| 2026-10-11 | [50-diagnostics/s11/2026-10-11-p5-spatial-conjunction/verify.py](50-diagnostics/s11/2026-10-11-p5-spatial-conjunction/verify.py) | P5 고정 비교 결과/검증 |
| 2026-10-11 | [50-diagnostics/s11/2026-10-11-p5-spatial-conjunction/verification.json](50-diagnostics/s11/2026-10-11-p5-spatial-conjunction/verification.json) | P5 고정 비교 결과/검증 |


### 2026-10-12 P5-S3 staged intensity-region pilot

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p5-extremal-regions/preflight.json](50-diagnostics/s11/2026-10-12-p5-extremal-regions/preflight.json) | 밝기별 닫힌 영역 가설의 사전 고정 명세 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p5-extremal-regions.md](50-diagnostics/s11/2026-10-12-p5-extremal-regions.md) | P5-S3 실제 양성 실패 및 단계 종료 근거 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p5-extremal-regions/run.py](50-diagnostics/s11/2026-10-12-p5-extremal-regions/run.py) | P5-S3 고정 실행·검증 산출물 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p5-extremal-regions/readout.json](50-diagnostics/s11/2026-10-12-p5-extremal-regions/readout.json) | P5-S3 고정 실행·검증 산출물 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p5-extremal-regions/verify.py](50-diagnostics/s11/2026-10-12-p5-extremal-regions/verify.py) | P5-S3 고정 실행·검증 산출물 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p5-extremal-regions/verification.json](50-diagnostics/s11/2026-10-12-p5-extremal-regions/verification.json) | P5-S3 고정 실행·검증 산출물 |

### 2026-10-12 public compressor source intake

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source.md](50-diagnostics/s11/2026-10-12-public-compressor-source.md) | 새 공개 압축기 영상의 출처·용도·지역적 Foam 상단 확인 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame-preflight.json](50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame-preflight.json) | 두 경계 역할 확인 후 기존 검출기 원본/절반 해상도 관찰의 사전 고정 명세 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/artifact-verification.json](50-diagnostics/s11/2026-10-12-public-compressor-source/artifact-verification.json) | 공개 원본 출처·장면 검토·판단 및 무결성 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/lower-role-review.json](50-diagnostics/s11/2026-10-12-public-compressor-source/lower-role-review.json) | 공개 원본 출처·장면 검토·판단 및 무결성 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/native-at-50.png](50-diagnostics/s11/2026-10-12-public-compressor-source/native-at-50.png) | 공개 원본 출처·장면 검토·판단 및 무결성 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/native-review-plan.json](50-diagnostics/s11/2026-10-12-public-compressor-source/native-review-plan.json) | 공개 원본 출처·장면 검토·판단 및 무결성 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/native-review.json](50-diagnostics/s11/2026-10-12-public-compressor-source/native-review.json) | 공개 원본 출처·장면 검토·판단 및 무결성 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/provenance.json](50-diagnostics/s11/2026-10-12-public-compressor-source/provenance.json) | 공개 원본 출처·장면 검토·판단 및 무결성 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/render.py](50-diagnostics/s11/2026-10-12-public-compressor-source/render.py) | 공개 원본 출처·장면 검토·판단 및 무결성 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/screen-preflight.json](50-diagnostics/s11/2026-10-12-public-compressor-source/screen-preflight.json) | 공개 원본 출처·장면 검토·판단 및 무결성 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/source-contact-sheet.jpg](50-diagnostics/s11/2026-10-12-public-compressor-source/source-contact-sheet.jpg) | 공개 원본 출처·장면 검토·판단 및 무결성 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/upper-role-reply.json](50-diagnostics/s11/2026-10-12-public-compressor-source/upper-role-reply.json) | 공개 원본 출처·장면 검토·판단 및 무결성 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/inspect_detector.py](50-diagnostics/s11/2026-10-12-public-compressor-source/inspect_detector.py) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/prepare_position_review.py](50-diagnostics/s11/2026-10-12-public-compressor-source/prepare_position_review.py) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/capture-storage.json](50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/capture-storage.json) | 동일 NONE/FULL payload 중복 제거와 진단 JSON 무손실 압축 매핑 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/current-frame-readout.json](50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/current-frame-readout.json) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/current-frame-verification.json](50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/current-frame-verification.json) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/half-diagnostics.json.gz](50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/half-diagnostics.json.gz) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/half-images.npz](50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/half-images.npz) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/half-none.json](50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/half-none.json) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/native-diagnostics.json.gz](50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/native-diagnostics.json.gz) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/native-images.npz](50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/native-images.npz) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/native-none.json](50-diagnostics/s11/2026-10-12-public-compressor-source/current-frame/native-none.json) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/position-review/position-review.json](50-diagnostics/s11/2026-10-12-public-compressor-source/position-review/position-review.json) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/temporal-detail-preflight.json](50-diagnostics/s11/2026-10-12-public-compressor-source/temporal-detail-preflight.json) | 기포 시간 변화의 관측 가능성을 위한 31프레임 원본 검토 계획 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/temporal-detail/readout.json](50-diagnostics/s11/2026-10-12-public-compressor-source/temporal-detail/readout.json) | 기포 시간 변화 관측 검토: 원본 31프레임·출처·검증 및 설계 한계 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/temporal-detail/review.json](50-diagnostics/s11/2026-10-12-public-compressor-source/temporal-detail/review.json) | 기포 시간 변화 관측 검토: 원본 31프레임·출처·검증 및 설계 한계 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/temporal-detail/native-crops.npz](50-diagnostics/s11/2026-10-12-public-compressor-source/temporal-detail/native-crops.npz) | 기포 시간 변화 관측 검토: 원본 31프레임·출처·검증 및 설계 한계 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/temporal-detail/native-detail-sheet.png](50-diagnostics/s11/2026-10-12-public-compressor-source/temporal-detail/native-detail-sheet.png) | 기포 시간 변화 관측 검토: 원본 31프레임·출처·검증 및 설계 한계 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/review_temporal_detail.py](50-diagnostics/s11/2026-10-12-public-compressor-source/review_temporal_detail.py) | 기포 시간 변화의 관측 가능성을 위한 31프레임 원본 검토 계획 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/join_positions.py](50-diagnostics/s11/2026-10-12-public-compressor-source/join_positions.py) | 사용자 확정 범위와 저장 관측의 후보·중앙선·구성 영역 연결 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/position-review/position-join.json](50-diagnostics/s11/2026-10-12-public-compressor-source/position-review/position-join.json) | 사용자 확정 범위와 저장 관측의 후보·중앙선·구성 영역 연결 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/position-review/position-review.png](50-diagnostics/s11/2026-10-12-public-compressor-source/position-review/position-review.png) | 공개 영상의 고정 프레임 검출 관찰·검증 및 원본 위치 범위 검토 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/pipeline-preflight.json](50-diagnostics/s11/2026-10-12-public-compressor-source/pipeline-preflight.json) | 새 공개 영상의 3프레임 실제 파이프라인 연결 사전 고정 및 실행 어댑터 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/replay_pipeline.py](50-diagnostics/s11/2026-10-12-public-compressor-source/replay_pipeline.py) | 새 공개 영상의 3프레임 실제 파이프라인 연결 사전 고정 및 실행 어댑터 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/verify_pipeline.py](50-diagnostics/s11/2026-10-12-public-compressor-source/verify_pipeline.py) | 공개 영상의 실제 분석·최종 후보·CSV 연결 검증과 중복 제거한 원본 진단 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/pipeline-linkage/storage.json](50-diagnostics/s11/2026-10-12-public-compressor-source/pipeline-linkage/storage.json) | 공개 영상의 실제 분석·최종 후보·CSV 연결 검증과 중복 제거한 원본 진단 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/pipeline-linkage/captures.zip](50-diagnostics/s11/2026-10-12-public-compressor-source/pipeline-linkage/captures.zip) | 공개 영상의 실제 분석·최종 후보·CSV 연결 검증과 중복 제거한 원본 진단 기록 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-public-compressor-source/pipeline-linkage/readout.json](50-diagnostics/s11/2026-10-12-public-compressor-source/pipeline-linkage/readout.json) | 공개 영상의 실제 분석·최종 후보·CSV 연결 검증과 중복 제거한 원본 진단 기록 |

### 2026-10-12 scene-based evaluation routing

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-scene-evaluation-roster.json](50-diagnostics/s11/2026-10-12-scene-evaluation-roster.json) | 기존 근거의 장면·검증 목적 연결표 및 저장 baseline 해석; 새 truth 아님 |

### 2026-10-12 direction-decision intake

첨부 작성 기준은 2026-10-11이며, 아래 최초 Git 추가일과 구별한다.
최초 추가 커밋 `9db5d26`의 author 날짜(KST)로 16파일을 확정했다.

#### `docs/60-evidence/s11/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [60-evidence/s11/2026-10-12-direction-decision-intake.json](60-evidence/s11/2026-10-12-direction-decision-intake.json) | 이번 인수·검증 기록; 작성 2026-10-12 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-direction-decision-intake.md](60-evidence/s11/2026-10-12-direction-decision-intake.md) | 이번 인수·검증 기록; 작성 2026-10-12 |

#### `docs/70-reference/s11-direction-decision-2026-10-11/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/HANDOFF.md](70-reference/s11-direction-decision-2026-10-11/HANDOFF.md) | 첨부 원본 bytes 보존; 제공일 기준 2026-10-11 |
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/MANIFEST.sha256](70-reference/s11-direction-decision-2026-10-11/MANIFEST.sha256) | 첨부 원본 bytes 보존; 제공일 기준 2026-10-11 |
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/README.md](70-reference/s11-direction-decision-2026-10-11/README.md) | 첨부 원본 bytes 보존; 제공일 기준 2026-10-11 |
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/S11_PROGRAM_DECISION_AND_WORK_SPEC.md](70-reference/s11-direction-decision-2026-10-11/S11_PROGRAM_DECISION_AND_WORK_SPEC.md) | 첨부 원본 bytes 보존; 제공일 기준 2026-10-11 |
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/STORY_ACCEPTANCE_TEMPLATE.json](70-reference/s11-direction-decision-2026-10-11/STORY_ACCEPTANCE_TEMPLATE.json) | 첨부 원본 bytes 보존; 제공일 기준 2026-10-11 |
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/import-manifest.json](70-reference/s11-direction-decision-2026-10-11/import-manifest.json) | 원본/중복 보존 매핑; 작성 2026-10-12 |

#### `docs/70-reference/s11-direction-decision-2026-10-11/evidence/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/evidence/focused-tests.log](70-reference/s11-direction-decision-2026-10-11/evidence/focused-tests.log) | 첨부 원본 bytes 보존; 제공일 기준 2026-10-11 |
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/evidence/s2-decision-geometry.json](70-reference/s11-direction-decision-2026-10-11/evidence/s2-decision-geometry.json) | 첨부 원본 bytes 보존; 제공일 기준 2026-10-11 |
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/evidence/session-audit-summary.json](70-reference/s11-direction-decision-2026-10-11/evidence/session-audit-summary.json) | 첨부 원본 bytes 보존; 제공일 기준 2026-10-11 |
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/evidence/verifier-stdout.json](70-reference/s11-direction-decision-2026-10-11/evidence/verifier-stdout.json) | 첨부 원본 bytes 보존; 제공일 기준 2026-10-11 |

#### `docs/70-reference/s11-direction-decision-2026-10-11/native-evidence/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/native-evidence/default-reverification.log](70-reference/s11-direction-decision-2026-10-11/native-evidence/default-reverification.log) | 로컬 감사 고유 로그 bytes 보존 |
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/native-evidence/s2-reverification.log](70-reference/s11-direction-decision-2026-10-11/native-evidence/s2-reverification.log) | 로컬 감사 고유 로그 bytes 보존 |

#### `docs/70-reference/s11-direction-decision-2026-10-11/tools/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/tools/audit_s2_decision_geometry.py](70-reference/s11-direction-decision-2026-10-11/tools/audit_s2_decision_geometry.py) | 첨부 원본 bytes 보존; 제공일 기준 2026-10-11 |
| 2026-10-12 | [70-reference/s11-direction-decision-2026-10-11/tools/reproduce.sh](70-reference/s11-direction-decision-2026-10-11/tools/reproduce.sh) | 첨부 원본 bytes 보존; 제공일 기준 2026-10-11 |

### 2026-10-12 P2 ordered row distributions

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions.md](50-diagnostics/s11/2026-10-12-p2-row-distributions.md) | 행별 색 분포의 Oil 역할 비교: 사전 고정·수치 도달성·실행 및 검증 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/preflight.json](50-diagnostics/s11/2026-10-12-p2-row-distributions/preflight.json) | 행별 색 분포의 Oil 역할 비교: 사전 고정·수치 도달성·실행 및 검증 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/run.py](50-diagnostics/s11/2026-10-12-p2-row-distributions/run.py) | 행별 색 분포의 Oil 역할 비교: 사전 고정·수치 도달성·실행 및 검증 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/synthetic-readout.json](50-diagnostics/s11/2026-10-12-p2-row-distributions/synthetic-readout.json) | 행별 색 분포의 Oil 역할 비교: 사전 고정·수치 도달성·실행 및 검증 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/readout.json](50-diagnostics/s11/2026-10-12-p2-row-distributions/readout.json) | 행별 색 분포의 실패 판정 및 변경 없는 평균 비교의 별도 진단 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/verification.json](50-diagnostics/s11/2026-10-12-p2-row-distributions/verification.json) | 행별 색 분포의 실패 판정 및 변경 없는 평균 비교의 별도 진단 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/followup-preflight.json](50-diagnostics/s11/2026-10-12-p2-row-distributions/followup-preflight.json) | 행별 색 분포의 실패 판정 및 변경 없는 평균 비교의 별도 진단 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/followup.py](50-diagnostics/s11/2026-10-12-p2-row-distributions/followup.py) | 행별 색 분포의 실패 판정 및 변경 없는 평균 비교의 별도 진단 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/followup-readout.json](50-diagnostics/s11/2026-10-12-p2-row-distributions/followup-readout.json) | 변경 없는 행 평균 비교의 14맥락 전체 진단과 독립 수치 검증 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/followup-verification.json](50-diagnostics/s11/2026-10-12-p2-row-distributions/followup-verification.json) | 변경 없는 행 평균 비교의 14맥락 전체 진단과 독립 수치 검증 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/candidates-preflight.json](50-diagnostics/s11/2026-10-12-p2-row-distributions/candidates-preflight.json) | 변경 없는 평균 비교의 기존 160개 전체 후보 진단 사전 고정 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/candidates.py](50-diagnostics/s11/2026-10-12-p2-row-distributions/candidates.py) | 변경 없는 평균 비교의 기존 160개 전체 후보 진단 사전 고정 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/candidates-readout.json](50-diagnostics/s11/2026-10-12-p2-row-distributions/candidates-readout.json) | 전체 후보 비교에서 드러난 평균 외관 비교의 선택 한계 및 검증 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/candidates-verification.json](50-diagnostics/s11/2026-10-12-p2-row-distributions/candidates-verification.json) | 전체 후보 비교에서 드러난 평균 외관 비교의 선택 한계 및 검증 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/candidate-competition.png](50-diagnostics/s11/2026-10-12-p2-row-distributions/candidate-competition.png) | 전체 후보 비교에서 드러난 평균 외관 비교의 선택 한계 및 검증 |
| 2026-10-12 | [50-diagnostics/s11/2026-10-12-p2-row-distributions/plot-candidates.py](50-diagnostics/s11/2026-10-12-p2-row-distributions/plot-candidates.py) | 전체 후보 비교에서 드러난 평균 외관 비교의 선택 한계 및 검증 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-boundary-feasibility-handoff.md](60-evidence/s11/2026-10-12-boundary-feasibility-handoff.md) | 경계 판별 연구 체크포인트, 재개 순서와 로컬 입력·보관 검증 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-boundary-feasibility-handoff.json](60-evidence/s11/2026-10-12-boundary-feasibility-handoff.json) | 경계 판별 연구 체크포인트, 재개 순서와 로컬 입력·보관 검증 |

### 2026-10-12 program review intake

작성일/인수일은 2026-10-12입니다. 아래 20파일의 최초 Git 추가일은
`8d319ea`의 author 시각을 Asia/Seoul로 환산한 2026-10-12로 확정했습니다.

#### `docs/20-architecture/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [20-architecture/s11-contextual-role-observation-design.md](20-architecture/s11-contextual-role-observation-design.md) | CR-1 역할 관측 제안; 참조·해상도·비교 실험 조건; 작성일 2026-10-12 |

#### `docs/60-evidence/s11/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [60-evidence/s11/2026-10-12-program-review-intake.md](60-evidence/s11/2026-10-12-program-review-intake.md) | 명세 인수·재현 검증과 조건부 후속 계획; 작성일 2026-10-12 |

#### `docs/60-evidence/s11/2026-10-12-program-review-intake/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [60-evidence/s11/2026-10-12-program-review-intake/focused-tests.xml](60-evidence/s11/2026-10-12-program-review-intake/focused-tests.xml) | 명세 인수·재현 검증과 조건부 후속 계획; 작성일 2026-10-12 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-program-review-intake/verification.json](60-evidence/s11/2026-10-12-program-review-intake/verification.json) | 명세 인수·재현 검증과 조건부 후속 계획; 작성일 2026-10-12 |

#### `docs/70-reference/s11-program-review-2026-10-12/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/README.md](70-reference/s11-program-review-2026-10-12/README.md) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/S11-program-review-and-work-spec-2026-10-12.md](70-reference/s11-program-review-2026-10-12/S11-program-review-and-work-spec-2026-10-12.md) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/SHA256SUMS.txt](70-reference/s11-program-review-2026-10-12/SHA256SUMS.txt) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/import-manifest.json](70-reference/s11-program-review-2026-10-12/import-manifest.json) | 첨부 10파일·native 7파일 보존과 중복 경로 매핑; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/story-contract.json](70-reference/s11-program-review-2026-10-12/story-contract.json) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |

#### `docs/70-reference/s11-program-review-2026-10-12/evidence/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/evidence/execution-receipt.json](70-reference/s11-program-review-2026-10-12/evidence/execution-receipt.json) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/evidence/focused-tests.log](70-reference/s11-program-review-2026-10-12/evidence/focused-tests.log) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/evidence/story-contract-tests.log](70-reference/s11-program-review-2026-10-12/evidence/story-contract-tests.log) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |

#### `docs/70-reference/s11-program-review-2026-10-12/native-evidence/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/native-evidence/delivery-summary.json](70-reference/s11-program-review-2026-10-12/native-evidence/delivery-summary.json) | 로컬 감사 고유 산출물 bytes 보존; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/native-evidence/focused-tests.xml](70-reference/s11-program-review-2026-10-12/native-evidence/focused-tests.xml) | 로컬 감사 고유 산출물 bytes 보존; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/native-evidence/peer-probe-initial.json](70-reference/s11-program-review-2026-10-12/native-evidence/peer-probe-initial.json) | 로컬 감사 고유 산출물 bytes 보존; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/native-evidence/peer-probe-verified.json](70-reference/s11-program-review-2026-10-12/native-evidence/peer-probe-verified.json) | 로컬 감사 고유 산출물 bytes 보존; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/native-evidence/peer-probe.log](70-reference/s11-program-review-2026-10-12/native-evidence/peer-probe.log) | 로컬 감사 고유 산출물 bytes 보존; 작성일 2026-10-12 |

#### `docs/70-reference/s11-program-review-2026-10-12/scripts/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/scripts/check_delivery.py](70-reference/s11-program-review-2026-10-12/scripts/check_delivery.py) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/scripts/peer_probe.py](70-reference/s11-program-review-2026-10-12/scripts/peer_probe.py) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |
| 2026-10-12 | [70-reference/s11-program-review-2026-10-12/scripts/test_story_contract.py](70-reference/s11-program-review-2026-10-12/scripts/test_story_contract.py) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |

### 2026-10-12 pre-CR-1 cleanup checkpoint

아래 파일의 작성일은 2026-10-12입니다. 최초 Git 추가일은 `5389ff9`의
author 시각을 Asia/Seoul로 환산한 2026-10-12로 확정했습니다.
추가 통합 manifest와 receipt의 최초 Git 추가일은 `368788c`의 author 시각
(`2026-10-12T15:37:56+09:00`)으로 확인했습니다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [60-evidence/s11/2026-10-12-pre-cr1-cleanup-checkpoint.md](60-evidence/s11/2026-10-12-pre-cr1-cleanup-checkpoint.md) | 저장소 정리·보존 검증 및 CR-1 미착수 체크포인트 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-pre-cr1-cleanup/consolidation-receipt.json](60-evidence/s11/2026-10-12-pre-cr1-cleanup/consolidation-receipt.json) | 작성일 2026-10-12; 추가 산출물 통합·용량·선택 복원·입력 소비 검증 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-pre-cr1-cleanup/consolidation.json.gz](60-evidence/s11/2026-10-12-pre-cr1-cleanup/consolidation.json.gz) | 작성일 2026-10-12; 전체 경로별 유지/압축 보관·해시·참조·복구 매핑 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-pre-cr1-cleanup/inventory.json.gz](60-evidence/s11/2026-10-12-pre-cr1-cleanup/inventory.json.gz) | 정리 전 경로·해시·용량 목록 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-pre-cr1-cleanup/receipt.json](60-evidence/s11/2026-10-12-pre-cr1-cleanup/receipt.json) | 정리 전후 용량·입력 보존·체크포인트 검증 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-pre-cr1-cleanup/removal-manifest.json.gz](60-evidence/s11/2026-10-12-pre-cr1-cleanup/removal-manifest.json.gz) | 삭제 사유·기존 ZIP 복구 매핑·캐시 재생성 경계 |

### 2026-10-12 experiment artifact lifecycle and final compression

아래 파일의 작성일과 최초 Git 추가일은 2026-10-12입니다. 최초 추가 커밋
`c46e5e3`의 author 시각을 Asia/Seoul로 환산하여 확인했습니다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [40-operations/experiment-artifact-lifecycle.md](40-operations/experiment-artifact-lifecycle.md) | 새 로컬 연구 출력의 생성·예산·보존·정리 및 push 전 검사 절차 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-pre-cr1-cleanup/compressed-files.json](60-evidence/s11/2026-10-12-pre-cr1-cleanup/compressed-files.json) | 원본 5개와 gzip 4개/기존 ZIP object 1개 사이의 추가 보존 매핑 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-pre-cr1-cleanup/compression-receipt.json](60-evidence/s11/2026-10-12-pre-cr1-cleanup/compression-receipt.json) | 마지막 압축·삭제 후 복원·입력 보호 검증 및 관리 도구 검증 |

### 2026-10-12 retention-value review

아래 파일의 작성일과 최초 Git 추가일은 2026-10-12입니다. 최초 추가 커밋
`5f34477`의 author 시각(`2026-10-12T17:16:52+09:00`)으로 확인했습니다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-12 | [60-evidence/s11/2026-10-12-pre-cr1-cleanup/retention-receipt.json](60-evidence/s11/2026-10-12-pre-cr1-cleanup/retention-receipt.json) | 실제 폐기·용량·생존 입력 및 복구 범위 검증 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-pre-cr1-cleanup/retention.json](60-evidence/s11/2026-10-12-pre-cr1-cleanup/retention.json) | 의사결정별 보존 심사와 현재 생존/폐기 경로 |
| 2026-10-12 | [60-evidence/s11/2026-10-12-pre-cr1-cleanup/temporal-affine-counterexample.npz](60-evidence/s11/2026-10-12-pre-cr1-cleanup/temporal-affine-counterexample.npz) | 폐기 ZIP에서 선별한 작은 합성 실패 반례 |

### 2026-10-13 post-CR1 specification intake

원문 작성일은 2026-10-12이며 인수/manifest 작성일은 2026-10-13입니다.
아래 파일의 최초 Git 추가일은 `228becf`의 author 시각
(`2026-10-13T09:31:41+09:00`)을 Asia/Seoul로 확인하여 확정했습니다.

#### `docs/60-evidence/s11/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [60-evidence/s11/2026-10-13-post-cr1-review-intake.md](60-evidence/s11/2026-10-13-post-cr1-review-intake.md) | 독립 재현 검증·명세 채택 범위·워크트리 검토·계획 축약; 작성일 2026-10-13 |

#### `docs/70-reference/s11-post-cr1-review-2026-10-12/`

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [70-reference/s11-post-cr1-review-2026-10-12/README.md](70-reference/s11-post-cr1-review-2026-10-12/README.md) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |
| 2026-10-13 | [70-reference/s11-post-cr1-review-2026-10-12/S11-program-review-and-work-spec-post-CR1-2026-10-12.md](70-reference/s11-post-cr1-review-2026-10-12/S11-program-review-and-work-spec-post-CR1-2026-10-12.md) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |
| 2026-10-13 | [70-reference/s11-post-cr1-review-2026-10-12/S11-review-execution-summary.json](70-reference/s11-post-cr1-review-2026-10-12/S11-review-execution-summary.json) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |
| 2026-10-13 | [70-reference/s11-post-cr1-review-2026-10-12/SHA256SUMS.txt](70-reference/s11-post-cr1-review-2026-10-12/SHA256SUMS.txt) | 첨부 원본 bytes 보존; 작성일 2026-10-12 |
| 2026-10-13 | [70-reference/s11-post-cr1-review-2026-10-12/audit_cr1_saved.py](70-reference/s11-post-cr1-review-2026-10-12/audit_cr1_saved.py) | 첨부 historical 재현 스크립트; 제품/테스트 discovery 밖; 작성일 2026-10-12 |
| 2026-10-13 | [70-reference/s11-post-cr1-review-2026-10-12/import-manifest.json](70-reference/s11-post-cr1-review-2026-10-12/import-manifest.json) | ZIP/member hash·기존 중복·워크트리/브랜치 판단; 작성일 2026-10-13 |

### 2026-10-13 post-CR1 executable policy preflight

아래 파일의 작성일은 2026-10-13이다. 최초 추가 커밋 `72d676f`의
author 시각은 Asia/Seoul 기준 2026-10-13 11:18:57이며, 최초 Git 추가일도
2026-10-13으로 확인했다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-post-cr1-policy-preflight.md](50-diagnostics/s11/2026-10-13-post-cr1-policy-preflight.md) | 저장 관측 계약 검증·자료 적합성·한정된 후보 역할 질문 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-post-cr1-policy-preflight/manifest.json](50-diagnostics/s11/2026-10-13-post-cr1-policy-preflight/manifest.json) | 한 운영정책·geometry/bank·자료 노출·미지정 calibration·입력 pin |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-post-cr1-policy-preflight/readout.json.gz](50-diagnostics/s11/2026-10-13-post-cr1-policy-preflight/readout.json.gz) | 전체 164개 후보/문맥과 raw-vector·native-lineage 연결, 물리 결정 미실행 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-post-cr1-policy-preflight/review.html](50-diagnostics/s11/2026-10-13-post-cr1-policy-preflight/review.html) | f1485 A/B 원본 및 기록된 표본 위치 검토; 새 정답 아님 |

### 2026-10-13 CR1 competitor reply and additional input screen

아래 파일의 작성일은 2026-10-13이다. 최초 추가 커밋 `66a70a9`의
author 시각은 Asia/Seoul 기준 2026-10-13 12:43:46이며, 최초 Git 추가일도
2026-10-13으로 확인했다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-cr1-competitor-role.md](50-diagnostics/s11/2026-10-13-cr1-competitor-role.md) | B 최초 답변 해석의 정정: 미세 Foam의 물리적 설명과 근사 위치의 실용적 수용 구분 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-cr1-competitor-role-reply.json](50-diagnostics/s11/2026-10-13-cr1-competitor-role-reply.json) | 원문·후보·원본·점수·표시 이미지 연결; frozen 라벨의 명시적 보충 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-cr1-competitor-role-review.png](50-diagnostics/s11/2026-10-13-cr1-competitor-role-review.png) | 사용자가 실제 확인한 A/B 모바일 비교 이미지 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-public-compressor-input.md](50-diagnostics/s11/2026-10-13-public-compressor-input.md) | 기존 미획득 공개 원본의 네 시점 입력 품질 검사; 역할 판정 대기 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-public-compressor-input/native-f1147.png](50-diagnostics/s11/2026-10-13-public-compressor-input/native-f1147.png) | 사전 고정한 중간 시점의 원본 프레임 한 장 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-public-compressor-input/review.png](50-diagnostics/s11/2026-10-13-public-compressor-input/review.png) | 좌표 보존 모바일 확대; 새 정답/후보선 없음 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-public-compressor-input/source-review.json](50-diagnostics/s11/2026-10-13-public-compressor-input/source-review.json) | 원본·독립성 한계·실제 시점·입력 한계·질문 연결 |

### 2026-10-13 판정 의미 명확화

아래 파일의 작성일은 2026-10-13이다. 최초 추가 커밋 `44bd8cf`의
author 시각은 Asia/Seoul 기준 2026-10-13 14:27:04이며, 최초 Git 추가일도
2026-10-13으로 확인했다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-cr1-competitor-role-annotation.png](50-diagnostics/s11/2026-10-13-cr1-competitor-role-annotation.png) | 미세 Foam 범위를 빨간 점으로 표시한 사용자 첨부 원본 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-cr1-competitor-role-clarification.json](50-diagnostics/s11/2026-10-13-cr1-competitor-role-clarification.json) | 후속 원문·주석·기존 판정 연결과 물리적 정답/실용적 수용의 구분 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-public-compressor-role-reply.json](50-diagnostics/s11/2026-10-13-public-compressor-role-reply.json) | 새 공개 영상의 저화질 판별 불가 및 잠정 Foam 인상; 확정 라벨 없음 |

### 2026-10-13 판정 의미 실행 연결

아래 파일의 작성일은 2026-10-13이다. 최초 추가 커밋 `06cdf4b`의
author 시각은 Asia/Seoul 기준 2026-10-13 14:52:42이며, 최초 Git 추가일도
2026-10-13으로 확인했다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-cr1-review-qualification/manifest.json](50-diagnostics/s11/2026-10-13-cr1-review-qualification/manifest.json) | 고정 readout과 후속 설명의 정확한 후보·주장 연결 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-cr1-review-qualification/readout.json](50-diagnostics/s11/2026-10-13-cr1-review-qualification/readout.json) | 164개 원래 기록 보존 및 A/B 물리적 qualification·B 실용적 수용의 별도 집계 |

### 2026-10-13 공개 원본 CR1 이전 비교

아래 파일의 작성일은 2026-10-13이다. 최초 추가 커밋 `9e106cd`의
author 시각은 Asia/Seoul 기준 2026-10-13 15:06:19이며, 최초 Git 추가일도
2026-10-13으로 확인했다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-cr1-public-transfer.md](50-diagnostics/s11/2026-10-13-cr1-public-transfer.md) | 기존 reference를 다른 공개 원본의 경계 포함 범위에 적용하는 고정 진단 비교 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-cr1-public-transfer/preflight.json](50-diagnostics/s11/2026-10-13-cr1-public-transfer/preflight.json) | 추론 전 원본·geometry·35개 위치·자원·중단 기준 고정 |

### 2026-10-13 공개 원본 CR1 결과와 Foam 내부 검토

아래 파일의 작성일은 2026-10-13이다. 최초 추가 커밋 `0275ab2`의
author 시각은 Asia/Seoul 기준 2026-10-13 15:28:14이며, 최초 Git 추가일도
2026-10-13으로 확인했다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-cr1-public-transfer/readout.json](50-diagnostics/s11/2026-10-13-cr1-public-transfer/readout.json) | 고정 35개 위치 전체 점수·지원 좌표·실제 encoder 대조·자원 결과 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-foam-material-reference/proposal.json](50-diagnostics/s11/2026-10-13-foam-material-reference/proposal.json) | 독립 Foam 위·아래 비교에 쓸 내부 영역의 원본·좌표·새 검토 질문 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-foam-material-reference/reference-review.png](50-diagnostics/s11/2026-10-13-foam-material-reference/reference-review.png) | R 영역 위치와 가공하지 않은 원본 확대를 담은 모바일 검토 이미지 |

### 2026-10-13 Foam 두 모습의 기준 분리

아래 파일의 작성일은 2026-10-13이다. 최초 추가 커밋 `1497694`의
author 시각은 Asia/Seoul 기준 2026-10-13 15:56:20이며, 최초 Git 추가일도
2026-10-13으로 확인했다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-foam-material-reference/coarse-proposal.json](50-diagnostics/s11/2026-10-13-foam-material-reference/coarse-proposal.json) | 큰 기포 Foam 내부 L 영역의 미확정 판단·원본·좌표·노출 범위 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-foam-material-reference/coarse-review.png](50-diagnostics/s11/2026-10-13-foam-material-reference/coarse-review.png) | 물 A의 Foam 층과 개별 기포 맥락 및 L 원본 확대 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-foam-material-reference/render.py](50-diagnostics/s11/2026-10-13-foam-material-reference/render.py) | 기존 경계 구간 renderer를 바꾸지 않는 유한 내부 영역 검토 재현기 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-foam-material-reference/reply.json](50-diagnostics/s11/2026-10-13-foam-material-reference/reply.json) | R의 미세 Foam 승인과 큰 기포 Foam 별도 포괄 요구를 원문에 연결 |

### 2026-10-13 Foam 양측 비교 준비

처음 추가한 세 문서의 날짜는 `48cf500f44893c7ef39253f1a05bc6bc59ed53a9`의 author 날짜(KST)로 확정했습니다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-foam-material-reference/coarse-reply.json](50-diagnostics/s11/2026-10-13-foam-material-reference/coarse-reply.json) | L 영역의 큰 알갱이 Foam 내부 승인과 기준 노출 범위 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-foam-material-sides.md](50-diagnostics/s11/2026-10-13-foam-material-sides.md) | R/L 내부 기준을 경계 양측과 따로 비교하는 진단 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-foam-material-sides/preflight.json](50-diagnostics/s11/2026-10-13-foam-material-sides/preflight.json) | 추론 전 43장면·1,335경계·geometry·대조·자원 고정 |

### 2026-10-13 Foam 양측 비교 결과

두 결과 파일의 날짜는 `acf1ae122164435d8370579ae608174197fc6930`의 author 날짜(KST)로 확정했습니다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-foam-material-sides/readout.json.gz](50-diagnostics/s11/2026-10-13-foam-material-sides/readout.json.gz) | 전체 경계·결측·R/L 양측 점수·실제 encoder 대조·자원 결과 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-foam-material-sides/verification.json](50-diagnostics/s11/2026-10-13-foam-material-sides/verification.json) | 핀·좌표·지원·연산·guide 연결 및 고정 비교 미채택 검증 |

### 2026-10-13 역할 관측 인수인계

최초 추가일은 `bebe9e83914c934f1565db8ebbbae43756b9b673`의 author 날짜(KST)로 확정했습니다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [60-evidence/s11/2026-10-13-material-role-handoff.md](60-evidence/s11/2026-10-13-material-role-handoff.md) | 검증된 체크포인트·닫힌 판정·로컬 입력·후속 설계와 재개 메시지 |

### 2026-10-13 전반 검토 명세 인수

아래 8개 파일의 최초 추가일은 `dd3c986e5284110066f739d1beb972333a2aaa23`의 author 날짜(KST)
**2026-10-13**로 확정했습니다. 첨부 작성일·인수일과 Git 추가일을 구분합니다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [60-evidence/s11/2026-10-13-program-review-intake.md](60-evidence/s11/2026-10-13-program-review-intake.md) | 검증·타당성·채택 범위·정리 기록 |
| 2026-10-13 | [70-reference/s11-program-review-2026-10-13/README.md](70-reference/s11-program-review-2026-10-13/README.md) | 첨부 원본 bytes 보존; 작성일 2026-10-13 |
| 2026-10-13 | [70-reference/s11-program-review-2026-10-13/S11-evidence-audit-2026-10-13.json](70-reference/s11-program-review-2026-10-13/S11-evidence-audit-2026-10-13.json) | 첨부 원본 bytes 보존; 작성일 2026-10-13 |
| 2026-10-13 | [70-reference/s11-program-review-2026-10-13/S11-program-review-and-work-spec-2026-10-13.md](70-reference/s11-program-review-2026-10-13/S11-program-review-and-work-spec-2026-10-13.md) | 첨부 원본 bytes 보존; 작성일 2026-10-13 |
| 2026-10-13 | [70-reference/s11-program-review-2026-10-13/SHA256SUMS](70-reference/s11-program-review-2026-10-13/SHA256SUMS) | 첨부 원본 bytes 보존; 작성일 2026-10-13 |
| 2026-10-13 | [70-reference/s11-program-review-2026-10-13/VERIFICATION.json](70-reference/s11-program-review-2026-10-13/VERIFICATION.json) | 첨부 원본 bytes 보존; 작성일 2026-10-13 |
| 2026-10-13 | [70-reference/s11-program-review-2026-10-13/import-manifest.json](70-reference/s11-program-review-2026-10-13/import-manifest.json) | 원본 hash·배치·worktree mapping |
| 2026-10-13 | [70-reference/s11-program-review-2026-10-13/reproduce_native_feature_canary.py](70-reference/s11-program-review-2026-10-13/reproduce_native_feature_canary.py) | 첨부 원본 bytes 보존; 작성일 2026-10-13 |

### 2026-10-13 native G0 구현과 역할 검토

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [60-evidence/s11/2026-10-13-native-role-readiness.md](60-evidence/s11/2026-10-13-native-role-readiness.md) | G0 구현·전체 결속 검증·역할 준비도와 새 subject 질문의 범위 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-role-readiness/manifest.json](50-diagnostics/s11/2026-10-13-native-role-readiness/manifest.json) | 입력·source·geometry·원래 판정 pin |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-role-readiness/readout.json.gz](50-diagnostics/s11/2026-10-13-native-role-readiness/readout.json.gz) | 43-context/1,335-edge/164-Oil 전체 결속 표 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-role-readiness/verification.json](50-diagnostics/s11/2026-10-13-native-role-readiness/verification.json) | 테스트·실제 CLI·전체 support 재계산 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-role-readiness/review-proposal.json](50-diagnostics/s11/2026-10-13-native-role-readiness/review-proposal.json) | N1–N3 원본 경로·그림·판정 정밀도 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-role-readiness/native-role-review.png](50-diagnostics/s11/2026-10-13-native-role-readiness/native-role-review.png) | 원본과 native 경로를 나란히 표시한 검토 그림 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-role-readiness/render_review.py](50-diagnostics/s11/2026-10-13-native-role-readiness/render_review.py) | 원본 pixels/native polyline 검토 재현기 |

### 2026-10-13 native 역할 응답과 연구 범위 준비

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [60-evidence/s11/2026-10-13-native-role-qualification.md](60-evidence/s11/2026-10-13-native-role-qualification.md) | N1–N3 응답·입력 의존성·검증·다음 선택 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-role-qualification/review-reply.json](50-diagnostics/s11/2026-10-13-native-role-qualification/review-reply.json) | 사용자 원문과 정확한 subject/그림 결속 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-role-qualification/qualification.json](50-diagnostics/s11/2026-10-13-native-role-qualification/qualification.json) | 허용 역할 집합·완전한 RGB context·공유 dependency |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-role-qualification/verification.json](50-diagnostics/s11/2026-10-13-native-role-qualification/verification.json) | 37 tests·실제 CLI·독립 NumPy footprint 검증 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-role-qualification/g1-pilot-proposal.json](50-diagnostics/s11/2026-10-13-native-role-qualification/g1-pilot-proposal.json) | 별도 채택 전 한정 학습의 data/head/loss/split/비용/중단 제안 |

### 2026-10-13 다른 촬영원 대조군 검토 준비

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [60-evidence/s11/2026-10-13-native-opposition-review.md](60-evidence/s11/2026-10-13-native-opposition-review.md) | 대조군 우선 방향·새 N4/N5 질문·선정과 검증 범위 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-opposition-review/review-proposal.json](50-diagnostics/s11/2026-10-13-native-opposition-review/review-proposal.json) | 새 subject의 원본·전체 경로 결속·기존 N3 authority·선정 기록 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-opposition-review/native-opposition-review.png](50-diagnostics/s11/2026-10-13-native-opposition-review/native-opposition-review.png) | 원본 RGB와 N4/N5 경로, N3는 닫힌 기준 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-opposition-review/prepare_review.py](50-diagnostics/s11/2026-10-13-native-opposition-review/prepare_review.py) | 기존 graph/support owner를 쓰는 결속·검토 그림 재현기 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-opposition-review/verification.json](50-diagnostics/s11/2026-10-13-native-opposition-review/verification.json) | 실제 CLI·overwrite 거부·독립 경로와 6-side 입력 검증 |


### 2026-10-13 native 대조군 판정과 한정 학습

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-surface-trial/review-reply.json](50-diagnostics/s11/2026-10-13-native-surface-trial/review-reply.json) | N4/N5 원문·역할·추정과 확인된 context facet |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-surface-trial/qualification.json](50-diagnostics/s11/2026-10-13-native-surface-trial/qualification.json) | 기존 G0에 결속한 두 역할과 입력 범위 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-surface-trial/trial-manifest.json](50-diagnostics/s11/2026-10-13-native-surface-trial/trial-manifest.json) | 다섯 경로·촬영원 분리·고정 head/loss/seed·실패 기준 |
| 2026-10-13 | [60-evidence/s11/2026-10-13-native-surface-trial.md](60-evidence/s11/2026-10-13-native-surface-trial.md) | N4/N5 응답·고정 학습·N3 손실·검증·다음 자료 범위 판단 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-surface-trial/readout.json](50-diagnostics/s11/2026-10-13-native-surface-trial/readout.json) | 다섯 경로 최종 logits·손실/오수용·조건/비용·종료 판정 |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-surface-trial/final-weights.npz](50-diagnostics/s11/2026-10-13-native-surface-trial/final-weights.npz) | 재학습 없는 산술 재검증용 1,118개 최종 parameter |
| 2026-10-13 | [50-diagnostics/s11/2026-10-13-native-surface-trial/verification.json](50-diagnostics/s11/2026-10-13-native-surface-trial/verification.json) | 49 tests·입력/가중치·독립 NumPy 계산·실제 CLI 범위 |

### 2026-10-13 기존 자료 재사용 인수인계

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-13 | [60-evidence/s11/2026-10-13-existing-material-handoff.md](60-evidence/s11/2026-10-13-existing-material-handoff.md) | N1–N5 시험 종료·Artifact/마스크 이력·관리 보완 이후 체크포인트와 재개 메시지 |

### 2026-10-13 기존 자료 실행 — 2026-10-14 인수

첨부의 작성일은 2026-10-13이다. 아래 파일은 기존 작업 트리에 미커밋으로 있었으며,
인수 시 원본과 hash를 대조했다. 기존 실행 파일 7개의 최초 Git 추가일은
`d85a4c8fb8a10e62611592e531dee3f3f152fa17`의 author 날짜(KST)로 확정했다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-14 | [50-diagnostics/s11/2026-10-13-existing-material-execution/closeout-checks.json](50-diagnostics/s11/2026-10-13-existing-material-execution/closeout-checks.json) | 원 실행의 governance·산출물 종료 검사 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-13-existing-material-execution/manifest.json](50-diagnostics/s11/2026-10-13-existing-material-execution/manifest.json) | 원본·판정·source 용도·예산 pin |
| 2026-10-14 | [50-diagnostics/s11/2026-10-13-existing-material-execution/public-native-subject-review.png](50-diagnostics/s11/2026-10-13-existing-material-execution/public-native-subject-review.png) | 미확정 native 경로 7개의 원본 픽셀 검토 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-13-existing-material-execution/readout.json](50-diagnostics/s11/2026-10-13-existing-material-execution/readout.json) | 전체 164개 후보·native 경로·판정과 준비도 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-13-existing-material-execution/render_subject_packet.py](50-diagnostics/s11/2026-10-13-existing-material-execution/render_subject_packet.py) | 경로 검토 이미지 재현기 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-13-existing-material-execution/verification.json](50-diagnostics/s11/2026-10-13-existing-material-execution/verification.json) | 원 실행의 116 tests·CLI·원본과 경로 검증 |
| 2026-10-14 | [60-evidence/s11/2026-10-13-existing-material-execution.md](60-evidence/s11/2026-10-13-existing-material-execution.md) | 구현·실행·후속 범위 인수인계 |

### 2026-10-14 실제 실행 첨부 원본과 통합 mapping

원본의 작성일은 2026-10-13이다. 아래 3개 파일의 최초 Git 추가일은
`62cfe46fe079a64af3b5b7867e8951660a13513f`의 author 날짜(KST)로 확정했다.
코드·검증 JSON 사본은 기존 위치를 재사용하며, 중복 patch/checksum은 mapping에 복원 방법을 기록했다.

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-14 | [70-reference/s11-actual-execution-2026-10-13/RESULT_INDEX.json](70-reference/s11-actual-execution-2026-10-13/RESULT_INDEX.json) | 첨부의 휴대용 결과 색인 원본; live 결과 owner 아님 |
| 2026-10-14 | [70-reference/s11-actual-execution-2026-10-13/S11_HANDOFF.md](70-reference/s11-actual-execution-2026-10-13/S11_HANDOFF.md) | 첨부의 인수인계 원문; 당시 미커밋 상태 보존 |
| 2026-10-14 | [70-reference/s11-actual-execution-2026-10-13/import-manifest.json](70-reference/s11-actual-execution-2026-10-13/import-manifest.json) | 13개 member 배치·hash·수신 검증·중복 정리와 복원 방법 |

### 2026-10-14 Oil 정책 필요조건 검사

| 최초 등록일 (KST) | 파일 | 역할 |
|---|---|---|
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-policy-feasibility/manifest.json](50-diagnostics/s11/2026-10-14-oil-policy-feasibility/manifest.json) | 기존 연속 정책의 9개 대조군·연산·중단 조건 고정 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-policy-feasibility/readout.json](50-diagnostics/s11/2026-10-14-oil-policy-feasibility/readout.json) | 초기 참조 분리·A/B facet·9개 대조군 필요조건 결과 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-policy-feasibility/candidate-review-plan.json](50-diagnostics/s11/2026-10-14-oil-policy-feasibility/candidate-review-plan.json) | 공개 촬영원 후보 근사 허용 질문과 입력·범위 고정 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-policy-feasibility/prepare_candidate_review.py](50-diagnostics/s11/2026-10-14-oil-policy-feasibility/prepare_candidate_review.py) | 원본 후보 대표점·sector를 구분하는 검토 화면 재현기 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-policy-feasibility/candidate-review.png](50-diagnostics/s11/2026-10-14-oil-policy-feasibility/candidate-review.png) | 공개 Oil 범위 안 4개 후보의 점수 없는 근사 허용 검토 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-policy-feasibility/review.json](50-diagnostics/s11/2026-10-14-oil-policy-feasibility/review.json) | 23개 전체 후보·4개 질문 대상·pixel/hash 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-policy-feasibility/public-acceptance.json](50-diagnostics/s11/2026-10-14-oil-policy-feasibility/public-acceptance.json) | 네 후보 모두 허용한 사용자 답변과 subject·image·frame 결합 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-policy-feasibility/public-comparison-plan.json](50-diagnostics/s11/2026-10-14-oil-policy-feasibility/public-comparison-plan.json) | 기존 public 관측을 통한 실용적 후보 보존 필요조건 고정 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-policy-feasibility/public-readout.json](50-diagnostics/s11/2026-10-14-oil-policy-feasibility/public-readout.json) | 허용 후보 4개 모두 sign 조건 미충족인 반례와 전체 23개 분모 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/plan.json](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/plan.json) | 후보 RGB 관측·학습/평가 분리·변형·ablation·자원 고정 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/prepared.json](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/prepared.json) | 187개 전체 기록·실제 patch 의존성·15개 필수 대조 입력 고정 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/readout.json](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/readout.json) | 원본·평균 색 최종 결정과 187개 전체 분모·자원 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/final-weights.npz](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/final-weights.npz) | 재학습 없는 검증을 위한 최종 1,118개 가중치 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/verification.json](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/verification.json) | 전체 가용 후보의 독립 NumPy 산술·입력 검사 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/opposition-review-plan.json](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/opposition-review-plan.json) | 미판정 허용 18개에서 첫 프레임 3개만 묻는 사후 조사 범위 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/prepare_opposition_review.py](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/prepare_opposition_review.py) | 원본 픽셀·기존 판정·새 질문 후보를 분리하는 화면 재현기 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/opposition-review.png](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/opposition-review.png) | f1140에서 첫 잠재 오수용 후보 3개와 기존 허용 문맥 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/opposition-review.json](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/opposition-review.json) | 전체 18개 잠재 대조·질문 3개·원본/표식/hash 결합 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/rim-reply.json](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/rim-reply.json) | 사용자가 직접 확인한 세 후보의 glass-rim 역할과 Oil 근사 거부 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/rim-plan.json](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/rim-plan.json) | 원본 결과를 유지하는 사후 판정 결합·점수 순서 필요조건 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-candidate-rgb-trial/rim-readout.json](50-diagnostics/s11/2026-10-14-candidate-rgb-trial/rim-readout.json) | 세 rim 오수용과 단조 margin 정책의 보존 불가능 반례 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/review-plan.json](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/review-plan.json) | 기존 sample3 A/B에서 새 후보 두 개의 실용적 허용 질문 범위 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/prepare_review.py](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/prepare_review.py) | archive 원본 후보·픽셀을 연결하는 두 화면 재현기 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/candidate-review.png](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/candidate-review.png) | sample3 A/B의 후보 대표점 두 개와 별도 pooled sample 검토 화면 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/review.json](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/review.json) | 38개 후보·원본 픽셀 결합 및 두 후보의 미판정 범위 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/acceptance.json](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/acceptance.json) | A/B 두 노란 대표점의 실용적 Oil 근사 허용 답변 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/qualification-plan.json](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/qualification-plan.json) | 38개 후보를 유지하는 판정 결합·기존 입력 footprint 점검 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/qualification.json](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/qualification.json) | 20개 대조의 세 촬영원 범위와 sample3 B 상단 입력 부족 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-review-plan.json](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-review-plan.json) | B의 제거된 상단 영역만 묻는 새 역할 검토 범위 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/prepare_mask_review.py](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/prepare_mask_review.py) | 원본/기존 마스크 동일성·기여 영역 검토 재현기 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-review.png](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-review.png) | B 원본 상단 입력과 실제 제거 픽셀을 나란히 표시한 역할 질문 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-review.json](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-review.json) | 원본/가시성 hash·225개 제거 픽셀·predicate 겹침과 질문 결합 |
| 2026-10-14 | [60-evidence/s11/2026-10-14-candidate-rgb-trial.md](60-evidence/s11/2026-10-14-candidate-rgb-trial.md) | 후보 RGB 실제 준비·고정 단일 비교·검증 기록 |
| 2026-10-14 | [60-evidence/s11/2026-10-14-oil-policy-feasibility.md](60-evidence/s11/2026-10-14-oil-policy-feasibility.md) | 필요조건 실제 실행·한계 및 다른 촬영원 연결 |

### 2026-10-14 chromatic overlay 원래 연결 영역 검토

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-reply.json](50-diagnostics/s11/2026-10-14-oil-candidate-source-expansion/upper-mask-reply.json) | B 유체–빈공간 경계·지속 유입 흔들림의 지역 판정 |
| 2026-10-14 | [20-architecture/s11-chromatic-overlay-support-design.md](20-architecture/s11-chromatic-overlay-support-design.md) | 원래 연결 영역의 thin/wide 조건과 입력/추적 검증 계약 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-overlay-component-review.md](50-diagnostics/s11/2026-10-14-overlay-component-review.md) | 형태 처리로 원래 두께가 소실되는 원인과 고정 비교 |
| 2026-10-14 | [40-operations/s11-overlay-support-windows-comparison.md](40-operations/s11-overlay-support-windows-comparison.md) | 알려진 로컬 실패를 포함한 미채택 후보 Windows A/B 인수인계 |
| 2026-10-14 | [60-evidence/s11/2026-10-14-overlay-support-guard.md](60-evidence/s11/2026-10-14-overlay-support-guard.md) | B 입력 복구·341 집중 테스트·13-case 비교 및 sequence 실패 기록 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-overlay-component-review/plan.json](50-diagnostics/s11/2026-10-14-overlay-component-review/plan.json) | 원래 마스크의 다섯 프레임 원인 분석 pin |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-overlay-component-review/readout.json](50-diagnostics/s11/2026-10-14-overlay-component-review/readout.json) | 전체 열린 core와 원래 parent 비교 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-overlay-component-review/comparison-plan.json](50-diagnostics/s11/2026-10-14-overlay-component-review/comparison-plan.json) | 미채택 guard의 고정 paired 입력/source/정지 조건 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-overlay-component-review/frames.json](50-diagnostics/s11/2026-10-14-overlay-component-review/frames.json) | 실제 detector 경로와 원본 전처리 mask 동일성 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-overlay-component-review/replay-baseline.json.gz](50-diagnostics/s11/2026-10-14-overlay-component-review/replay-baseline.json.gz) | 기존 전처리 299행·전체 source/runtime/hash 기록 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-overlay-component-review/replay-candidate.json.gz](50-diagnostics/s11/2026-10-14-overlay-component-review/replay-candidate.json.gz) | 후보 전처리 299행·전체 source/runtime/hash 기록 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-overlay-component-review/replay-comparison.json](50-diagnostics/s11/2026-10-14-overlay-component-review/replay-comparison.json) | 13개 기존 비교 전체와 37개 changed row 필드 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-overlay-component-review/integrity-candidate.txt](50-diagnostics/s11/2026-10-14-overlay-component-review/integrity-candidate.txt) | 보호된 sequence barrier 회귀 실패 원문 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-overlay-component-review/verification.json](50-diagnostics/s11/2026-10-14-overlay-component-review/verification.json) | 소스 동결·테스트·행 변화·미채택 판정 |

### 2026-10-14 공개 native 경로 역할 검토 준비

| 최초 Git 등록일(KST) | 파일 | 역할 |
|---|---|---|
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/plan.json](50-diagnostics/s11/2026-10-14-native-role-review/plan.json) | 기존 상단 네 경로 전체·검토 이미지·원본 결합 범위 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/proposal.json](50-diagnostics/s11/2026-10-14-native-role-review/proposal.json) | 역할 미판정 질문 대상과 하부 Oil 보존 대조 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/inspection.json](50-diagnostics/s11/2026-10-14-native-role-review/inspection.json) | 인간 답변 없는 원본·경로·지원 검사 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/verification.json](50-diagnostics/s11/2026-10-14-native-role-review/verification.json) | 실제 CLI 및 기존 N1–N5 결과 보존 확인 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/reply.json](50-diagnostics/s11/2026-10-14-native-role-review/reply.json) | 네 상단 경로에 대한 사용자 Foam 상단 답변 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/qualification.json](50-diagnostics/s11/2026-10-14-native-role-review/qualification.json) | 네 Foam 상단 역할의 원본 경로 결합 결과 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/source-readiness.json](50-diagnostics/s11/2026-10-14-native-role-review/source-readiness.json) | 세 촬영원·아홉 native 경로의 역할 대조 준비 상태 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/opposition-plan.json](50-diagnostics/s11/2026-10-14-native-role-review/opposition-plan.json) | 새 Y442 행의 역할 미판정 검토 계획 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/opposition-proposal.json](50-diagnostics/s11/2026-10-14-native-role-review/opposition-proposal.json) | Y442의 모든 경로 세 개와 원본 결합 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/opposition-inspection.json](50-diagnostics/s11/2026-10-14-native-role-review/opposition-inspection.json) | 세 미판정 경로의 실제 픽셀·지원 검사 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/opposition-review.png](50-diagnostics/s11/2026-10-14-native-role-review/opposition-review.png) | 기존 Oil 경로와 구분한 새 하단 경로 검토 그림 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/opposition-verification.json](50-diagnostics/s11/2026-10-14-native-role-review/opposition-verification.json) | 실제 CLI·기존 결과 보존·156 테스트 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/opposition-reply.json](50-diagnostics/s11/2026-10-14-native-role-review/opposition-reply.json) | 하단 세 경로의 유리 rim 판정 원문 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/opposition-qualification.json](50-diagnostics/s11/2026-10-14-native-role-review/opposition-qualification.json) | 세 구조물 역할의 원본 경로 결합 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-review/qualified-source-readiness.json](50-diagnostics/s11/2026-10-14-native-role-review/qualified-source-readiness.json) | 12개 native 역할·촬영원·같은-frame dependency 집계 |
| 2026-10-14 | [60-evidence/s11/2026-10-14-native-role-order.md](60-evidence/s11/2026-10-14-native-role-order.md) | 별도 source 균형 역할 순서 비교의 고정 계약·검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-order/manifest.json](50-diagnostics/s11/2026-10-14-native-role-order/manifest.json) | 32개 경로·source 분리·역할 순서 학습/비교 입력 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-order/preparation-verification.json](50-diagnostics/s11/2026-10-14-native-role-order/preparation-verification.json) | 실제 준비 CLI·167 테스트·합성 loss/gradient 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-order/readout.json](50-diagnostics/s11/2026-10-14-native-role-order/readout.json) | native 순서 실패·평균 RGB 대조군의 전체 32개 경로 결과 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-order/native-weights.npz](50-diagnostics/s11/2026-10-14-native-role-order/native-weights.npz) | 종료된 native 순서 모델의 최종 가중치 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-order/mean_rgb-weights.npz](50-diagnostics/s11/2026-10-14-native-role-order/mean_rgb-weights.npz) | 제한된 고정 평균색 비교군 가중치 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-role-order/verification.json](50-diagnostics/s11/2026-10-14-native-role-order/verification.json) | 독립 NumPy 계산·52개 추론·덮어쓰기 거부 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/source-manifest.json](50-diagnostics/s11/2026-10-14-native-milk-review/source-manifest.json) | 기존 우유 원본·G0 참조와 역할 검토 범위 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/native-packet.json](50-diagnostics/s11/2026-10-14-native-milk-review/native-packet.json) | 고정 중심열의 우유 native 경로 16개 전체 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/plan.json](50-diagnostics/s11/2026-10-14-native-milk-review/plan.json) | 모델 점수 확인 전 세 행 전체 선택과 고정 가중치 참조 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/proposal.json](50-diagnostics/s11/2026-10-14-native-milk-review/proposal.json) | 새 경로 444·453·687의 역할 질문·원본 결합 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/review.png](50-diagnostics/s11/2026-10-14-native-milk-review/review.png) | 기존 하단 경계 질문과 구분한 세 native 경로 검토 그림 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/inspection.json](50-diagnostics/s11/2026-10-14-native-milk-review/inspection.json) | 인간 역할 판정 없이 실행한 세 경로 원본·지원 검사 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/verification.json](50-diagnostics/s11/2026-10-14-native-milk-review/verification.json) | 원본 동일성·기존 그림 바이트 보존·고정 입력 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/reply.json](50-diagnostics/s11/2026-10-14-native-milk-review/reply.json) | 컵 상단 두 구조물·687 확대 위치 불명확·원근 설명의 원문 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/qualification.json](50-diagnostics/s11/2026-10-14-native-milk-review/qualification.json) | 444·453 구조물 결합과 687 무정답 상태 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/location.png](50-diagnostics/s11/2026-10-14-native-milk-review/location.png) | 동일 687 확대 경로의 원본 위치 표시 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/location-proposal.json](50-diagnostics/s11/2026-10-14-native-milk-review/location-proposal.json) | 위치를 보강한 동일 687 경로의 한정 추가 질문 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/location-inspection.json](50-diagnostics/s11/2026-10-14-native-milk-review/location-inspection.json) | 위치 검토 경로의 원본·지원 무정답 검사 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/location-verification.json](50-diagnostics/s11/2026-10-14-native-milk-review/location-verification.json) | 경로·확대 픽셀 동일성 및 이전 검토 그림 보존 검사 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/location-reply.json](50-diagnostics/s11/2026-10-14-native-milk-review/location-reply.json) | 위치 확인 후 687을 큰 방울 하나의 실제 Foam 상단으로 확정한 원문 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-review/location-qualification.json](50-diagnostics/s11/2026-10-14-native-milk-review/location-qualification.json) | 동일 687 경로의 명시적 Foam 상단 판정 결합 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-order/manifest.json](50-diagnostics/s11/2026-10-14-native-milk-order/manifest.json) | 재학습 없는 평균색 비교군·16개 경로·두 순서 비교의 고정 입력 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-order/preparation-verification.json](50-diagnostics/s11/2026-10-14-native-milk-order/preparation-verification.json) | 21 테스트·실제 qualifier·cwd 독립 준비 및 13 입력 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-order/readout.json](50-diagnostics/s11/2026-10-14-native-milk-order/readout.json) | 고정 평균색 비교군의 우유 구조물 오순위와 16개 경로 전체 결과 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-milk-order/verification.json](50-diagnostics/s11/2026-10-14-native-milk-order/verification.json) | 26개 기존 점수 일치·13개 독립 계산·가중치 보존 검증 |

### 2026-10-14 우유 큰 거품의 고정 시간 문맥

| 최초 Git 등록일(KST) | 파일 | 역할 |
|---|---|---|
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context.md](50-diagnostics/s11/2026-10-14-milk-bubble-context.md) | 기존 큰 거품의 시간 대응 관측 가능성 검토 범위 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/plan.json](50-diagnostics/s11/2026-10-14-milk-bubble-context/plan.json) | 기존 25프레임·고정 영역·원본 및 source 핀 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/review_source.py](50-diagnostics/s11/2026-10-14-milk-bubble-context/review_source.py) | 기존 디코더를 재사용하는 한정 원본 추출·픽셀 검사 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/review.html](50-diagnostics/s11/2026-10-14-milk-bubble-context/review.html) | 동일 무손실 atlas의 프레임 이동·재생 화면 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/native-atlas.png](50-diagnostics/s11/2026-10-14-milk-bubble-context/native-atlas.png) | 25개 원본 영역을 한 번만 보존한 무손실 배열 이미지 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/readout.json](50-diagnostics/s11/2026-10-14-milk-bubble-context/readout.json) | 25개 프레임·시간·원본/영역 해시 및 추출 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/verification.json](50-diagnostics/s11/2026-10-14-milk-bubble-context/verification.json) | 실제 브라우저 25개 픽셀·표시 시간·동작·덮어쓰기 거부 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/review.json](50-diagnostics/s11/2026-10-14-milk-bubble-context/review.json) | 새 시간 대응 질문과 이벤트 판정 미제공 상태 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/export_portable.py](50-diagnostics/s11/2026-10-14-milk-bubble-context/export_portable.py) | 고정 검토 입력을 재디코딩 없이 단일 HTML로 포장 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/review-standalone.html](50-diagnostics/s11/2026-10-14-milk-bubble-context/review-standalone.html) | 이미지·25프레임·정적 비교를 내장한 원격 전달 파일 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/remote-contact-sheet.png](50-diagnostics/s11/2026-10-14-milk-bubble-context/remote-contact-sheet.png) | 처음·중간·마지막 원본의 동일 영역 비교 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/remote-export.json](50-diagnostics/s11/2026-10-14-milk-bubble-context/remote-export.json) | 기존 입력 핀·내장 이미지·출력 해시 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/remote-verification.json](50-diagnostics/s11/2026-10-14-milk-bubble-context/remote-verification.json) | 단일 파일 오프라인·JS 미사용 표시 및 25프레임 픽셀 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-milk-bubble-context/temporal-reply.json](50-diagnostics/s11/2026-10-14-milk-bubble-context/temporal-reply.json) | 동일 거품의 우측 성장 답변·한정 시간 대응·기존 추적 재사용 범위 |

### 2026-10-14 고정 사전학습 문맥 비교

| 최초 Git 등록일(KST) | 파일 | 역할 |
|---|---|---|
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-context.md](50-diagnostics/s11/2026-10-14-semantic-context.md) | 기존 4개 촬영원·분석 영역에 대한 사전학습 문맥 비교의 고정 계약 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-context/setup.json](50-diagnostics/s11/2026-10-14-semantic-context/setup.json) | 격리 환경·모델·구현 핀·용량·합성 입력 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-context/manifest.json](50-diagnostics/s11/2026-10-14-semantic-context/manifest.json) | 기존 48개 경로·5개 분석 영역·17개 비교의 재사용 입력 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-context/readout.json](50-diagnostics/s11/2026-10-14-semantic-context/readout.json) | 고정 사전학습 문맥의 48개 경로 전체 점수·우유 두 반례 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-context/verification.json](50-diagnostics/s11/2026-10-14-semantic-context/verification.json) | 78개 지원·724개 패치 평균·17개 판정·덮어쓰기 거부 검증 |
| 2026-10-14 | [60-evidence/s11/2026-10-14-semantic-context.md](60-evidence/s11/2026-10-14-semantic-context.md) | 15/17 순서·우유 실패·미채택 결론과 분리 관측 설계 한계 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-context/closeout.json](50-diagnostics/s11/2026-10-14-semantic-context/closeout.json) | 추가 모델·14개 의존성 정리와 기존 환경·체크포인트 보존 확인 |

### 2026-10-14 main 인수인계의 증거 색인 보완

이번 main 통합 범위에서 누락된 기존 증거의 색인을 보완했다. 기존 파일 날짜는
각 파일의 `git log --follow --diff-filter=A` 최초 author 시각을 KST로 변환했다.
파일이나 frozen 결과는 이동·변경하지 않았다.

| 최초 Git 등록일(KST) | 파일 | 역할 |
|---|---|---|
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory.md](50-diagnostics/s11/2026-10-14-raw-front-inventory.md) | A 원시 표현·base 접촉·상단 입력 누락의 원인 기록 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-12-cr1-context-comparison/runtime-retirement-20261014.json](50-diagnostics/s11/2026-10-12-cr1-context-comparison/runtime-retirement-20261014.json) | CR-1 모델·source·공유 연구 환경 정리의 보존 기록 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/plan.json](50-diagnostics/s11/2026-10-14-native-contact-trial/plan.json) | NCT-1·접촉 판독: s11-native-contact-trial-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/prepare_sample3_contact.py](50-diagnostics/s11/2026-10-14-native-contact-trial/prepare_sample3_contact.py) | 기존 sample3 A의 후보 접촉 검토 준비 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/readout.json](50-diagnostics/s11/2026-10-14-native-contact-trial/readout.json) | NCT-1·접촉 판독: s11-native-contact-trial-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-plan.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-plan.json) | NCT-1·접촉 판독: s11-source-contact-type-preparation-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-reply.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-reply.json) | NCT-1·접촉 판독: s11-source-contact-type-reply-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-review.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-review.json) | NCT-1·접촉 판독: s11-source-contact-type-review-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-review.png](50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-review.png) | 물리 역할 검토에 사용한 원본 경로 표시 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-verification.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-verification.json) | NCT-1·접촉 판독: s11-source-contact-display-verification-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-extension-plan.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-extension-plan.json) | NCT-1·접촉 판독: s11-native-role-extension-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-extension-verification.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-extension-verification.json) | NCT-1·접촉 판독: s11-native-role-extension-verification-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-extension.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-extension.json) | NCT-1·접촉 판독: s11-native-role-extension-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-native-readout.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-native-readout.json) | NCT-1·접촉 판독: s11-native-review-source-readout-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-reply.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-reply.json) | NCT-1·접촉 판독: s11-native-liquid-role-reply-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-inspection.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-inspection.json) | NCT-1·접촉 판독: s11-native-fragment-proposal-inspection-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-manifest.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-manifest.json) | NCT-1·접촉 판독: s11-native-review-source-reuse-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-plan.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-plan.json) | NCT-1·접촉 판독: s11-native-fragment-review-preparation-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-proposal.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-proposal.json) | NCT-1·접촉 판독: s11-native-fragment-role-review-proposal-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-verification.json](50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review-verification.json) | NCT-1·접촉 판독: s11-native-contact-review-verification-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review.png](50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-review.png) | 물리 역할 검토에 사용한 원본 경로 표시 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-native-contact-trial/verification.json](50-diagnostics/s11/2026-10-14-native-contact-trial/verification.json) | NCT-1·접촉 판독: s11-native-contact-verification-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-extension-plan.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-extension-plan.json) | base 경로·판독을 기존 corpus에 붙이는 계획 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-extension-verification.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-extension-verification.json) | base delta와 원본 RGB patch 독립 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-extension.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-extension.json) | base 두 경로의 append-only corpus delta |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-stage-plan.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-stage-plan.json) | 사용자 표시·단계 검사 source/입력·예산 핀 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-plan.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-plan.json) | 지역 Foam 상단 검토 이미지의 고정 계획 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-reply.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-reply.json) | 빨간 점 6개의 지역 상단 판독·원본 좌표 대응 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-review.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-review.json) | 동일 f144 지역 상단 질문의 원래 검토 기록 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-review.png](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-review.png) | 전체 원본 ROI·Y 눈금·기존 하단 경로 검토 이미지 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-stages.json.gz](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-stages.json.gz) | 표시 영역·중앙열의 기존 Foam 단계 값 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-user.jpg](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-user.jpg) | 사용자가 직접 빨간 점을 표시한 JPEG 원본 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-verification.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-foam-upper-verification.json) | 상단 표시 대응·9채널·368픽셀 독립 검증 결과 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-frame-entry-verification.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-frame-entry-verification.json) | 실제 기준 출력·후보·원본 raster 일치 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-frame-entry.json.gz](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-frame-entry.json.gz) | 실제 기준 프레임의 모든 후보·A1/O1·Foam 결과 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-g0-manifest.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-g0-manifest.json) | 기준 native G0 입력 manifest |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-g0-readout.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-g0-readout.json) | base G0 native 입력·경로 결과 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-native-readout.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-native-readout.json) | base 전체 native 경로·원본 지원 결과 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-plan.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-plan.json) | 기존 base f144 원본·설정·준비 source 핀 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-probe-plan.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-probe-plan.json) | 기준 실제 detect 한 프레임 실행 계획 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-raster.npz](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-raster.npz) | base 원본 ROI·effective/glare/Canny 기준 배열 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-reply.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-reply.json) | 150 거품–액체 접촉 원문 판독 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-reuse-manifest.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-reuse-manifest.json) | base 경로·자료 재사용 연결 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-review-inspection.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-review-inspection.json) | base native 경로 검토 진입 검사 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-review-plan.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-review-plan.json) | base 경로 검토의 고정 입력·계획 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-review-proposal.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-review-proposal.json) | base 두 native 경로의 무정답 검토 제안 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-review-verification.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-review-verification.json) | base 검토 이미지·원본 픽셀 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-review.png](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-review.png) | base 원본과 native 150/462 검토 이미지 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/base-source-preflight.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/base-source-preflight.json) | base 원본·Recipe·native 준비 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/bind_base.py](50-diagnostics/s11/2026-10-14-raw-front-inventory/bind_base.py) | 기존 corpus에 base 판독만 결합하는 조합기 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/inspect_foam_upper.py](50-diagnostics/s11/2026-10-14-raw-front-inventory/inspect_foam_upper.py) | 기존 observer·probe를 연결한 표시 위치 단계 검사 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/inventory.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/inventory.json) | A 전체 raw plateau·native graph 재현 결과 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/plan.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/plan.json) | A raw plateau/graph 입력·고정 실행 계획 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/prepare_base.py](50-diagnostics/s11/2026-10-14-raw-front-inventory/prepare_base.py) | 기존 준비·qualifier를 재사용하는 base 입력 구성 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/probe_base.py](50-diagnostics/s11/2026-10-14-raw-front-inventory/probe_base.py) | 기준 전처리를 사용한 실제 detect/debug 진입 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/render_base.py](50-diagnostics/s11/2026-10-14-raw-front-inventory/render_base.py) | 원본 base native 경로의 검토 표시 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/render_foam_extent.py](50-diagnostics/s11/2026-10-14-raw-front-inventory/render_foam_extent.py) | 전체 ROI·원본 Y 눈금을 보존하는 상단 검토 표시 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/verification.json](50-diagnostics/s11/2026-10-14-raw-front-inventory/verification.json) | A 표현 inventory의 독립 계산 검증 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/verify.py](50-diagnostics/s11/2026-10-14-raw-front-inventory/verify.py) | A 원본 photometry·plateau·graph 검산기 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-raw-front-inventory/verify_foam_upper.py](50-diagnostics/s11/2026-10-14-raw-front-inventory/verify_foam_upper.py) | 원본 채널·texture·외부 눈금의 독립 검산기 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/corpus-plan.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/corpus-plan.json) | 분리 역할·corpus 준비: s11-native-role-corpus-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/corpus-verification.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/corpus-verification.json) | 분리 역할·corpus 준비: s11-native-role-corpus-verification-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/corpus.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/corpus.json) | 분리 역할·corpus 준비: s11-native-role-corpus-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/liquid-qualification.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/liquid-qualification.json) | 분리 역할·corpus 준비: s11-native-liquid-role-qualification-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/liquid-reply.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/liquid-reply.json) | 분리 역할·corpus 준비: s11-native-liquid-role-reply-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/liquid-verification.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/liquid-verification.json) | 분리 역할·corpus 준비: s11-liquid-role-reply-verification-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/plan.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/plan.json) | 분리 역할·corpus 준비: s11-semantic-role-readiness-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/readout.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/readout.json) | 분리 역할·corpus 준비: s11-semantic-role-readiness-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/review-inspection.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/review-inspection.json) | 분리 역할·corpus 준비: s11-native-fragment-proposal-inspection-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/review-plan.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/review-plan.json) | 분리 역할·corpus 준비: s11-native-fragment-review-preparation-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/review-proposal.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/review-proposal.json) | 분리 역할·corpus 준비: s11-native-fragment-role-review-proposal-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/review.png](50-diagnostics/s11/2026-10-14-semantic-role-readiness/review.png) | 물리 역할 검토에 사용한 원본 경로 표시 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/verification.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/verification.json) | 분리 역할·corpus 준비: s11-semantic-role-readiness-verification-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-native-readout.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-native-readout.json) | 분리 역할·corpus 준비: s11-native-review-source-readout-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-reply.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-reply.json) | 분리 역할·corpus 준비: s11-native-liquid-role-reply-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-inspection.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-inspection.json) | 분리 역할·corpus 준비: s11-native-fragment-proposal-inspection-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-manifest.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-manifest.json) | 분리 역할·corpus 준비: s11-native-review-source-reuse-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-plan.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-plan.json) | 분리 역할·corpus 준비: s11-native-fragment-review-preparation-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-proposal.json](50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review-proposal.json) | 분리 역할·corpus 준비: s11-native-fragment-role-review-proposal-v1 |
| 2026-10-14 | [50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review.png](50-diagnostics/s11/2026-10-14-semantic-role-readiness/water-review.png) | 물리 역할 검토에 사용한 원본 경로 표시 |
| 2026-10-14 | [60-evidence/s11/2026-10-14-native-contact-trial.md](60-evidence/s11/2026-10-14-native-contact-trial.md) | NCT-1 — ordered native-side contact interaction |
| 2026-10-14 | [60-evidence/s11/2026-10-14-foam-input-handoff.md](60-evidence/s11/2026-10-14-foam-input-handoff.md) | b225dd1 main 통합·미채택 guard 철회·Foam 입력 조사 인수인계 |

인수인계 문서의 최초 Git 추가일은 `b225dd1297839dea1651ace087fe7d4bf479f848` author 시각의 KST 날짜로 확정했다.

### 2026-10-14 bounded-context 작업 추가 — Git 최초 등록일 미확정

| 작성일 / Git 상태 | 문서 | 구분 |
|---|---|---|
| 2026-10-14 / 미등록 | [60-evidence/s11/2026-10-14-bounded-context-experiment.md](60-evidence/s11/2026-10-14-bounded-context-experiment.md) | DTO-1 실제 영상·정적 광학 반례·독립 검산 및 3–4회 종료 예산 인수인계; 생산 승격 없음 |

### 2026-10-14 round-2 context 작업 추가 — Git 최초 등록일 미확정

| 작성일 / Git 상태 | 문서 | 구분 |
|---|---|---|
| 2026-10-14 / 미등록 | [60-evidence/s11/2026-10-14-round2-context-disposition.md](60-evidence/s11/2026-10-14-round2-context-disposition.md) | 기존 report·원본 시퀀스·browser 실행 검증, 간단한 rejection 정책 반례 및 판독 대기 인수인계; 생산 변경 없음 |

### 2026-10-15 round-3 handoff 작업 추가 — Git 최초 등록일 미확정

| 작성일 / Git 상태 | 문서 | 구분 |
|---|---|---|
| 2026-10-15 / 미등록 | [60-evidence/s11/2026-10-15-round3-handoff-validation.md](60-evidence/s11/2026-10-15-round3-handoff-validation.md) | 실제 canvas 프레임 검증 보완, 회귀 대조군과 1–3회차 통합 인수인계; detector·현장 인수와 구분 |

### 2026-10-15 초기 FULL 비교 준비

| 최초 등록 기준 | 문서 | 범위 |
|---|---|---|
| 2026-10-15 / 미등록 | [50-diagnostics/s11/2026-10-15-initial-full-comparison.md](50-diagnostics/s11/2026-10-15-initial-full-comparison.md) | 내부 ROI 고정과 초기 FULL 관측 경로 비교; 실제 Windows 판정은 별도 |

### 2026-10-16 Windows 비교 체크포인트

| 최초 Git 추가일 (KST) | 문서 | 범위 |
|---|---|---|
| 2026-10-16 | [60-evidence/s11/2026-10-16-windows-comparison-checkpoint.md](60-evidence/s11/2026-10-16-windows-comparison-checkpoint.md) | 세 후보·FULL preflight·721초 조사 완료 상태와 기존 판정·자료 위치, 다음 수정안 설계 재개용 인계 |

### 2026-10-16 corroboration peer 검증 추가

| 최초 Git 추가일 (KST) | 문서 | 범위 |
|---|---|---|
| 2026-10-16 | [50-diagnostics/s11/2026-10-16-corroboration-peer-screen.md](50-diagnostics/s11/2026-10-16-corroboration-peer-screen.md) | frozen P1/P2 실행, rim 상호 지지와 실제 계면 지지 손실, 미채택 판정 |
| 2026-10-16 | [50-diagnostics/s11/2026-10-16-corroboration-peer-screen/readout.json.gz](50-diagnostics/s11/2026-10-16-corroboration-peer-screen/readout.json.gz) | 187개 전체 분모, 175 Oil 후보 기여 peer·정답 범위·원시 타입 대조 |
| 2026-10-16 | [50-diagnostics/s11/2026-10-16-corroboration-peer-screen/verification.json](50-diagnostics/s11/2026-10-16-corroboration-peer-screen/verification.json) | source pin, 175 순서 대조, 342개 테스트와 정확한 반례 |
| 2026-10-16 | [60-evidence/s11/2026-10-16-corroboration-handoff.md](60-evidence/s11/2026-10-16-corroboration-handoff.md) | 결과·자료·재현·미채택/미완료 및 다음 세션 인수인계 |
| 2026-10-16 | [50-diagnostics/s11/2026-10-16-corroboration-peer-screen/preflight.md](50-diagnostics/s11/2026-10-16-corroboration-peer-screen/preflight.md) | 첫 입력 실패 실행이 고정했던 원문을 동일 SHA-256으로 보존한 읽기 전 명세 |
| 2026-10-16 | [50-diagnostics/s11/2026-10-16-corroboration-peer-screen/storage-reference-relocation.json](50-diagnostics/s11/2026-10-16-corroboration-peer-screen/storage-reference-relocation.json) | 가변 문서를 참조한 저장 실수의 경로 정정 기록; 원래 증거 해시·내용 불변 |

최초 Git 추가일은 `e8d205cca160a7f7a0a5fe4cdb0e4e316a7045cf`의 author 시각을 KST로 변환하여 확정했다.

### 2026-10-16 current-raster partition 검증

| 최초 Git 등록일 (KST) | 문서 | 범위 |
|---|---|---|
| 2026-10-16 | [50-diagnostics/s11/2026-10-16-raster-partition-screen.md](50-diagnostics/s11/2026-10-16-raster-partition-screen.md) | CRW-1 고정 가설·동일 위치 픽셀 대응·계면/비유면 양면 대조 |
| 2026-10-16 | [50-diagnostics/s11/2026-10-16-raster-partition-screen/summary.json](50-diagnostics/s11/2026-10-16-raster-partition-screen/summary.json) | 전체 분모·18개 검토 대조·별도 직접 픽셀 검산·source hash |
| 2026-10-16 | [60-evidence/s11/2026-10-16-raster-partition-handoff.md](60-evidence/s11/2026-10-16-raster-partition-handoff.md) | 입력의 부분적 유용성·단독 판별 한계·움직임 맥락 기준·재현과 재개 |

### RCI-1 후속 등록

| 최초 Git 추가일 | 문서 | 구분 |
|---|---|---|
| 2026-10-16 | [2026-10-16-role-consumer-context.md](50-diagnostics/s11/2026-10-16-role-consumer-context.md) | 검토 역할의 consumer 반사실 실험; 자동 판별기 아님 |
| 2026-10-16 | [2026-10-16-role-consumer-context/summary.json](50-diagnostics/s11/2026-10-16-role-consumer-context/summary.json) | 반복 개입 결과·검증·보존 해시 요약 |
| 2026-10-16 | [2026-10-16-role-consumer-handoff.md](60-evidence/s11/2026-10-16-role-consumer-handoff.md) | 전체 구간 consumer 검증·원본 대조·후속 실행 기준 |
