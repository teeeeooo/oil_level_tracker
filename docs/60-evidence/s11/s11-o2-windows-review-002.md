# S11 O2 Windows review-002 — one reviewed interface candidate

Recorded: 2026-09-18. Source: user-transferred Windows review summary. Original
media, local labels and receipts were not opened on this machine. This is bounded
human-review evidence, not a classifier score or Windows field qualification.
[Work plan](../../00-project/work-plan.md) owns current status; the
[O2 procedure](../../40-operations/s11-o2-local-shadow-evaluation.md) and
[validation contract](../../30-validation/s11-interface-observability-witness-validation.md)
own the workflow and acceptance. This does not revise
[canonical reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md).

## Reported identity and persistence

| Item | Value |
|---|---|
| Bundle-generation ZIP commit | `d7c1ebe`, user-attested |
| Label-tool ZIP commit | `e3fac4b`, user-attested |
| Detector | `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1` |
| Resolver | `r22-oil-ownership-evidence-replacement-v1` |
| Witness | `interface-observability-witness-trace-v1` |
| Result semantics | `2` |
| Target | BASE, source frame `14386` |
| Persisted revision | `1` |
| Visibility / contour | `visible` / empty |
| Candidate inventory | 23: one interface, 22 unreviewed |
| Owners / classifier | no missing owners / `NOT_EVALUATED` |

prepare/link-bundle/status/record succeeded by report. The final status read
retained candidate input index 9's interface judgment. Source-video association
remains the registered human attestation, not a retroactive proof from a digest.
Executed source bytes were not independently compared with either ZIP commit.

## Reviewed candidate and paths

`candidate_input_index=9`, `source=material_path`, `canonical_y=411.5`.
The agent displayed four native-sector paths with Y ticks. The user judged all
four near the actual interface, and candidate 9 was recorded as `interface`.

| Sector | Source X extent (half-open) | Native source Y | Review basis |
|---|---|---|---|
| 1 | [130, 236) | 382 | Previous R22-2 user judgment reused after reported coordinate correspondence check |
| 2 | [236, 343) | 406 | New user confirmation |
| 3 | [343, 449) | 419 | New user confirmation |
| 4 | [449, 555) | 417 | Previous R22-2 user judgment reused after reported coordinate correspondence check |

These are reviewed candidate path positions, not independently measured exact
truth coordinates or tolerance intervals. The summary describes visual agreement
with the curved interface; no additional physical meniscus model is inferred.
Sector positions must not be replaced with scalar Y411.5 at all X locations.
Since contour is empty, quantitative localization error remains unmeasured.
The per-sector judgments appear in the transferred report; whether their full
provenance is retained in the candidate's local review_note has not been reported.

## Remaining inventory and next review

Unreviewed IDs: `0–8, 10–22`. None is automatically a negative merely because
candidate 9 is an interface. No unresolved judgments or errors were reported.
Source counts are 8 oil_hypothesis, 5 material_path, 6 calibrated_high_recall,
3 phase_transition_scan and 1 distributed_sobel_path.

Together with [review-001](s11-o2-windows-review-001.md), the record supplies a
no-visible-interface example and a reviewed interface candidate. It is not a
balanced discrimination dataset or proof of generalization. All these repeatedly
reviewed checkpoints remain regression data.

Next keep review-002 and resume a small group of 2–3 distinct, potentially
confusable proposals in this same frame. Inspect the full inventory before
selecting review targets; use comparable X/path geometry where available rather
than ranking, source family or scalar Y alone. Selection for review does not
filter the stored inventory. Display neutral A/B/C targets and source Y ticks;
ask one judgment at a time. Other candidates stay unreviewed. Duplicate-looking
proposals do not inherit labels without verified correspondence. Preserve the
user's explanations when structure/reflection overlap or an unnamed cause is
identified. Confirm the existing sector notes are retained, without repeating
already answered questions. Do not fabricate contour intervals from path Ys.

Freeze/evaluate have not been reported as run. No detector rerun or implementation
change follows from this single positive candidate.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: none newly inferred; this record preserves the transferred interface judgment separately from unreviewed proposals and unmeasured localization.
- Logic-map impact: NONE — evidence and next-review routing do not alter detector, diagnostic-tool or UI execution.
- Failure-registry impact: NONE — a human-reviewed candidate does not establish a new causal detector failure or field repair.
