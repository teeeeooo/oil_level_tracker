# S11-R16 Directed Tracklet and Material Lifecycle Evidence

## Disposition

R16 is implemented and passed the repaired local structural, causal,
provenance, checked-video, performance and full-regression gates. Independent
review rejected prior candidate head
`178fdf951d7142c39c6a54109cbaece8b204c476`; this record replaces its
invalidated replay and timing evidence and supports a fresh independent audit
of the repaired exact committed candidate. It does not establish private-field
accuracy, supersede R15 as the field authority or close S11.

The validated runtime identity is:

- detector: `opencv-phase-detector-r16-directed-interface-tracklets-v1`;
- sequence resolver: `r16-directed-interface-tracklets-v1`; and
- repaired semantic source/test commit:
  `6462a21c327241f9f0e91fe749ed1892abeb0776`
  (the following documentation-only commit does not alter runtime behavior).

## Implementation result

R16 separates physical row identity, material-phase ownership, publication
eligibility and fixed-lag selection. Directed tracklets terminate ambiguous
merge/split assignments in both directions. The repaired split rule terminates
one established parent matched ambiguously to multiple near-cost children, but
retains a clearly ranked child and ignores a child whose clear predecessor is a
different track. The phase lifecycle publishes allowed physical IDs before
scoring, preserves distinct IDs across explicit handoffs and keeps the filled
barrier closed until a confirmed drain owner exists. Projection chooses one
deterministic publishable member of the selected same-frame row; it never pools
sibling confidence or carries a coordinate.

The initial visible-interface fill repair links only one unique immediate
predecessor to a later strong dynamic owner. The predecessor contributes owner
chain continuity but not observations, extrema, direction or coordinates.
Foreign branches, ambiguous handoffs, bounded owner loss and material conflict
remain `UNKNOWN`.

Drain release, continuation, successor and re-entry now apply the full
same-frame row material veto, so a clean direct member cannot mask a
high-conflict material-path sibling. Phase re-entry also rejects a new owner
that is within the absolute jump bound but reverses above the prior drain Y
beyond the ordinary handoff tolerance.

The former completed-fill reacquisition veto is absent. The resolver facade is
2,513 lines and `OilPathLifecycleOwner` is 162 lines, below their decomposition
guards of 2,700 and 260. The fixed-lag selector, directed tracklets and phase
lifecycle are separate modules.

## Exact four-video replay

The repaired exact-clean-head replay processed 299 rows with 155 numeric Oil
rows:

| Sample | Rows | Numeric Oil | Tracking fingerprint |
|---|---:|---:|---|
| `base_sample_1` | 30 | 27 | `a784eb475ac29675f6e3369c2b5729f1aac7e7c6836d5fa5f679e081c52c9955` |
| `sample2` | 5 | 3 | `09c8451ac0d27ecbec81092a7da9a1137cf327bcc1fced2fbba0a00fd221e0b3` |
| `sample3` | 151 | 21 | `c30fdb0de8f452df24f9873f3d1079686f5a5d6fd3a525d42ae7180269adbaf5` |
| `sample4` | 113 | 104 | `a504337fa4338f6f03ccc742cbce55950251af2ddd4aa74ec859a82dbd010624` |
| **Total** | **299** | **155** | — |

Same-frame provenance violations were zero in every sample. Checked truth was
6/13 numeric with 7.667 px mean absolute error and 24.5 px maximum error.
Sample3 kept the material barrier non-numeric through 80.5138 s, then published
a coherent same-frame drain sequence from Y233 at 81.0143 s through Y342 at
96.5298 s. Six rows were numeric in `90 <= t < 103`; the material-conflict row
at 96.0293 s and every row at or after 97 s were `UNKNOWN`. This censors both
the unrelated upper branch and the backwards Y315 re-entry exposed by the
split repair. Sample4 retained 14/16 reviewed visible rows, 8/16 strict-range
matches and 10/10 Foam checks. Base and sample2 had zero false Foam; sample3
retained five reviewed dynamic Foam rows in two episodes.

Against the retained R15 replay, numeric deltas were Base `-3`, sample2 `0`,
sample3 `-22` and sample4 `-7` (`187 -> 155`). Against the independently
rejected pre-repair R16 replay, only sample3 changed (`30 -> 21`); Base,
sample2 and sample4 counts and fingerprints remained identical.
Candidate-level reconciliation found the removed sample3 rows in symmetric
split, completed-fill/cap, current-row material-conflict or backwards-re-entry
windows. The detailed causes are preserved in the
[R16 owner audit](../../50-diagnostics/s11/s11-r16-local-coverage-owner-audit.md).

## Causality and boundedness evidence

The stage confirmation and selector/onset policies each use six sampled
frames. They do not imply a six-frame end-to-end commitment. A composed
counterexample first observes a dynamic owner at frame 3 and confirms it only
at frame 7: a prefix ending at target `t+6` differs in phase reason and owner
metadata. The repository-owned end-to-end horizon is 11 sampled frames, or a
12-frame inclusive envelope through `t+11`. A hostile suffix after `t+11`
cannot alter target Y, physical tracklet, phase, reason or owner chain.

Production-source inspection found no Base/sample identifiers, reviewed
timestamps, truth-Y names or audited Y243/Y316/Y368 coordinates in detector
owners.

## Automated validation

- adversarial split, material-veto and reverse-re-entry repair controls:
  6 passed;
- focused production set including both evidence-specific corpus contracts:
  132 passed in 25.39 s;
- canonical repository suite: 1,629 passed in 153.44 s;
- Python compilation of `src` and `tests`: passed;
- production hardcoding search: no matches; and
- `git diff --check`: passed.

The R16 characterization fingerprint is
`c5329baeb0c0dba257b8fe48761d54c7ca4c879427955202c7e0cf0bb9564578`.

## Performance evidence

The checked workload is sample4 from 0--56 s at 2 FPS, debug disabled, using
official static learning, completed-window resolution and bundle output. Three
runs all retained 113 rows, 104 numeric Oil and fingerprint
`a504337fa4338f6f03ccc742cbce55950251af2ddd4aa74ec859a82dbd010624`.

| Measurement | R16 median | Delta from R0 |
|---|---:|---:|
| End-to-end wall time | 11.757 s | -24.1% |
| Real-time factor | 0.210 | -24.1% |
| Detector mean latency | 64.424 ms/frame | -18.4% |
| Completed-window resolution | 0.2022 s | -90.2% |

The performance runner rejected dirty or mismatched source state and recorded
the repaired source/test head plus `source_worktree_clean=true`. Accuracy,
abstention and provenance were not traded for the speed gains.
Private-Windows/package timing was not available locally.

## Reproducibility artifacts

- exact-clean-head replay manifest:
  `/var/folders/s2/wbnr4dhn1z1bk7tcl342s8bw0000gn/T/r16-audit-repair-four-final.fdf1y2xl/replay_manifest.json`;
- exact-clean-head performance manifest:
  `/tmp/r16-audit-repair-perf-final.BiYPYc/performance_profile.json`; and
- candidate-level repair trace:
  `/tmp/r16-drain-veto-audit.oI75nm/oil-debug-trace-s52awykr/debug_trace.jsonl`.

These ignored local outputs are reproducibility aids, not checked-in truth.
The exact counts, fingerprints and behavioral assertions above remain the
durable evidence if the temporary files are removed.

## Unresolved external gate

Private-Windows Base/Accum replay was not available in this checkout. R15
therefore remains the field authority. The repaired R16 source/test commit and
its following documentation-only commit still require a fresh independent
exact-head audit before push, followed by replay of that pushed head with the
saved Recipes and Artifact templates. Oil accuracy, Accum initial EMPTY
false-positive suppression, real bottom-entry admission, Foam publication and
CSV equality remain separate external checks. Per the authorized sequence, the
UI/UX evidence audit begins only after the R16 push and does not waive this
private detector gate.
