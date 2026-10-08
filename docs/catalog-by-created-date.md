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

현재 색인 수록 270개 파일. 이후 추가된 모든 repo 문서의 전수 목록을 보증하는 수치는 아닙니다.
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

### `docs/60-evidence/s11/` — 87개

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
