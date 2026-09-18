# S11 O2 Windows review-001 — transferred review record

Recorded: 2026-09-18. Source: user-transferred Windows agent summary and subsequent
user clarifications. Original media, local labels, receipts and history were not
opened on this machine. This is a bounded review-workflow record, not Windows
qualification or detector acceptance. [Work plan](../../00-project/work-plan.md)
owns current status; the [O2 procedure](../../40-operations/s11-o2-local-shadow-evaluation.md)
and [validation contract](../../30-validation/s11-interface-observability-witness-validation.md)
own preparation/evaluation. The [canonical reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
is not modified by this record.

## Execution identity

| Item | Reported value | Basis |
|---|---|---|
| Bundle-generation commit | `d7c1ebe` | User confirms downloading and running this commit's ZIP; executed source bytes were not independently compared |
| Label-tool commit | `e3fac4b` | User confirms downloading and running this commit's ZIP; executed source bytes were not independently compared |
| Detector | `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1` | User reports bundle detector-version field |
| Resolver | `r22-oil-ownership-evidence-replacement-v1` | User reports bundle resolver field |
| Witness | `interface-observability-witness-trace-v1` | User reports trace schema |
| App version | `0.1.0` | User report; not a source revision identifier |
| Result semantics / recipe schema | `2` / `1` | Transferred summary |
| Reviewed target | BASE, source frame `11508` | Transferred summary; distinct from the proposed next target f14386 |

The two commits are user-attested provenance, not unknown and not machine-verified
execution fingerprints. No source hash or private identifier is invented here.

## Reported workflow and human decisions

- prepare/link-bundle/status/record succeeded. Packet contains 23 Oil candidates.
- Revision 1 saved candidate judgments and visibility; revision 2 added owners and
  retained review notes. Re-reading status showed no unreviewed/unresolved candidates
  and no missing owners. Exact owner strings were not included in the summary.
- The user explicitly confirms the reviewed targets were identifiable and the
  judgments were deliberate; earlier image-display difficulties do not invalidate them.
- Human scene judgment: **FULL WITH NO INTERFACE — no visible Oil interface**.
  Contour was left empty. No native-sector path review was performed.
- Reflection: 6 candidates, input IDs `0, 10, 13, 16, 17, 20`.
- Structure: 17 candidates, input IDs
  `1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15, 18, 19, 21, 22`.
- Cluster C/E notes preserve possible glass scratches, which the user categorized
  as structure. Structure and reflection can overlap; categories are the user's
  selected labels plus original explanations, not proven mutually exclusive causes.
- Classification remains NOT_EVALUATED. Freeze/evaluate were not reported as run.
  Those commands do not rerun the detector or automatically establish physical truth.

## Completed serialization correction

The transferred revision-2 report says `visibility=visible`, while its explicit
human scene judgment says no interface. In the O2 schema visibility refers to the
Oil interface, not image clarity. The requested correction is `not_visible`, with
all 23 candidate labels and empty contour retained through `record`.

The user subsequently confirms revision **2 → 3**, `visibility=not_visible`,
all other judgments unchanged, and `classifier_status=NOT_EVALUATED`. The empty
contour and 23 candidate labels are therefore retained by user report. This closes
the bounded human-review/save-consistency step for this frame. No freeze/evaluate
completion or independent read of the work-PC files is claimed. The repository
records the user's confirmation; it did not modify the local Windows labels.

## Workflow feedback retained without implementation changes

1. The agent initially asked without displaying/opening the review image or making
   its location easy to find.
2. Y-only questions were hard to identify visually. The user requests source-frame
   Y axes/ticks and clearly marked targets in review images.
3. Single candidate labels cannot fully express overlapping structure/reflection
   or unnamed causes such as glass scratches; original notes must remain available.

The user requested that these issues be understood without immediate code changes.
No labeling schema, image generator or production behavior is changed by this record.

## Next bounded review

Next review an interface-visible positive example:
BASE f14386 in the same R22-3 bundle, if the exact record exists. Earlier human
review identified material_path Y411.5 and separately native sector 1 X[130,236)
Y382 and sector 4 X[449,555) Y417 near the interface. These are routing references,
not permission to auto-label a new execution or treat a single Y as contour truth
at every X. Verify exact correspondence before reusing previous judgments. If the
record is absent, report it rather than substituting a nearby frame or rerunning.

Only new or changed targets need further human questions. Preserve all candidates
and unreviewed entries, and report a concise batch summary instead of another full
numerical trace report. No classifier accuracy or field repair follows from this
single no-interface review.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: offline visibility serialization contradicts the transferred human scene judgment; this is not a new inference about detector failure stages.
- Logic-map impact: NONE — this transferred evidence record does not change runtime, diagnostic tools or UI wiring.
- Failure-registry impact: NONE — provenance/label semantics are recorded under existing F09 without claiming new field acceptance.
