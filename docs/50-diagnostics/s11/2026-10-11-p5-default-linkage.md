# P5 default application linkage

The controlled default run reproduces the previous audit and confirms the raw
Foam loss at component-to-front reduction. At f1620/54 s, the observed center
edge Y813 lies in the reviewed interval, but the only raw Foam candidate is
internal texture Y833. The episode rejects that wrong candidate. This does not
justify relaxing the episode or substituting either component extreme.

The [frozen preflight](2026-10-11-p5-default-linkage/preflight.json),
[readout](2026-10-11-p5-default-linkage/readout.json) and
[independent verifier](2026-10-11-p5-default-linkage/verify.py) bind base
`a58a7c69c5d7e25e47be0dff9ce882d54c1b7926`, all 221 production Python files,
existing replay helpers, source/Recipe/truth and the qualified source reply.
The existing `s11_local_xy_replay` recorder ran serially in fresh processes with
variant `off`, NONE then FULL, the complete 0–56 s / 2 Hz window, explicit
UNKNOWN initial state and unchanged Recipe. Local XY remained OFF. The legacy
recorder's run label says “Local XY fixed comparison”; that name does not enable
the scoped experiment. Unconfirmed AUTO operator setup was not evaluated.

| Check | Result |
|---|---|
| All raw and completed detections, including features/decisions | NONE = FULL, 113 each |
| Tracking and report presentation model, ignoring only run ID | Exact equality |
| Full trace to NONE current candidates by original index/source/Y/features | 2,611 exact joins |
| Trace raw/final positions to detections and public tracking | 113 exact joins |
| Prior audit raw/completed hashes, tracking CSV and events | Exact equality; 113 rows, 31 events |
| Fingerprint | `e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1` |
| All seven prior Foam source frames | Component records and center gray/visibility/labels/edges equal |
| Oil / Foam valid numerics | 101 / 26; physical accuracy is not inferred |
| Production / Recipe / truth / episode changes | None |

At f1620, current component C1 spans source Y[808,834), its lower-edge rule
selects Y833, and candidate input index22 carries that exact coordinate. The
sequence witness refers to the same candidate and fails `formation_witness`
(`bounded_stable_front`). Final raw/smoothed Foam and public Foam are null.
No correct Y813 candidate reached the episode. The current smoothed Y813 is
compatibility state, not selected same-frame provenance. The separate water A
lightness-floor finding and all closed source judgments are unchanged.

The preflight transcribed f1275 in place of the saved Foam set's f420. The first
verifier failed that lookup. Its correction preserves the preflight, audits
the union of eight frames, and retains all seven reviewed Oil checkpoints.
Both frames already belonged to the frozen full-window runs; no replay,
selection or operating point changed. F1635 remains unreviewed.

Measured pipeline time is 11.40 s NONE and 29.78 s FULL; process peak RSS is
321,683,456 and 330,989,568 bytes on Darwin. These times exclude bundle rendering
and must not be compared as a speedup against the prior 109-second end-to-end
audit. The FULL trace is 180,561,353 bytes. The NONE bundle is retained under
`sample/output/s11-p5-default-linkage-20261011-001/none/`, and FULL staging is
retained in its sibling directory. A second FULL HTML bundle was not rendered;
the complete report model was compared. This is not independent report
comprehension, Windows qualification, a new role model or detector improvement.

Reproduction uses the unchanged runner twice with `--sample sample4 --variant off
--level NONE` / `FULL`, `--preflight` pointing to the record above, and new output
directories. Run the verifier with `--root <repo> --runs <two-run-parent>
--output <new-json>`. It refuses to overwrite a result and rechecks source/input
hashes. Current sequencing and remaining gates belong to the Work Plan.

After the independent runs and equality checks, four byte-identical output pairs
were [coalesced with verified hard links](2026-10-11-p5-default-linkage/duplicate-cleanup.json).
Both replay paths remain usable; 26,546,181 logical duplicate bytes share storage.
No unique trace/report asset was removed, and this does not measure APFS free space.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `TRACE-PUBLICATION`, `RESULT-PRESENTATION`
- Failure-registry entries: `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: confirmed in the controlled default application run at component-to-front reduction, before episode processing; raw Y813 is absent from Foam candidates while internal Y833 is passed onward.
- Logic-map impact: NONE — existing detector, recorder, sequence and publication owners execute unchanged; the new script independently checks their saved outputs.
- Failure-registry impact: NONE — this closes the default/NONE versus scoped/FULL evidence gap for the existing F07 component-extreme failure, without a new causal mechanism or repair claim.
