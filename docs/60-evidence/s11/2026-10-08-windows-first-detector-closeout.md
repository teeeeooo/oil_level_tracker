# Windows-first detector investigation: closeout and handoff — 2026-10-08

## Decision and scope

This bounded investigation is ready for handoff as **verified diagnostic tooling
and closed experiments**, not as an improved production detector. Main base is
`49c6d3aebeaf90aea96cd5be4c0e91115011f5a7`; continuation branch is
`work/s11-windows-first-detector-20261008`. Production `src/`, dependencies,
recipes and truth are unchanged. Current status remains owned by the
[Work Plan](../../00-project/work-plan.md). FIELD FAIL, W4/O2 OPEN, independent
report comprehension and A0Q uncertainty are not closed by this work.

The recovered request prioritizes Windows evidence and consequential movement
context over perfect per-frame detection. The authoritative
[nine Windows segments](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
and [transferred W3 audit](s11-o2-w3-target-audit-windows-run-001.md) remain primary.
The latter shows true and false candidates in admitted rows, and some true
candidates absent before retained references. These facts do not prove that the
terminal barrier is the cause or that admitted candidates should be published.
Private Windows packets, complete audit JSON and video were unavailable locally.
No new Windows result, label, coordinate or interval is inferred.

The already exposed Mac sample3/sample4 material is a secondary diagnostic and
rejection screen. These are neither independent holdout nor Windows qualification.
The [design](../../20-architecture/s11-terminal-contradiction-shadow-design.md)
records the hypotheses and retained tooling boundary.

## H1 and H1b are closed without promotion

H1 withheld inferred FULL confirmation when the terminal observation had material
opposition. The existing terminal-owner control failed: an Oil Y64 was published
where the baseline requires null. The retained run has 153 passes and one failure.

H1b kept the terminal frame null while postponing the FILLED barrier. It still
failed the material-ownership barrier assertion in the same control (153 passes,
one failure). On 151 saved sample3 observations, Oil output increased from 29 to
65 rows; Foam remained five. Same-frame membership does not establish identity
for the added rows, and there is no human correctness judgment for those rows.
The two rejected patches and failed logs are preserved, and production source is
restored. Do not bypass the failing assertion or reinterpret increased output as
an efficacy result. No further H1/H1b threshold or barrier relaxation is selected.

## Verified recorded-exclusion diagnostic

The existing W3 `recorded_funnel` producer remains the owner of packet/sequence
joins. A separate standard-library-only reader, `s11_candidate_loss_audit.py`,
refines an existing hash-pinned W3 audit using its recorded allowed-owner filter.
It preserves original data, identity uncertainty and all exclusions while making
`not_selected` more useful for later exact-row investigation. It does not rerun
models/media, infer target truth, select candidates or change the original audit.
The separate file is intentional: it can be copied to Windows and executed
without installing the application or its scientific/GUI dependencies.

On the unchanged 151-row Mac sample3 saved input, the fresh replay is byte-identical
to the pre-interruption baseline (`resolution.json` SHA-256
`793383b4265d15bc0e37086814bdf0dc4487c810db60e04f7e2dbdea203cb774`). It retains 29
numeric Oil and five numeric Foam rows. The refined readout also matches the
previous result byte-for-byte. It binds all 29 selected Oil members and partitions
3,324 candidate records as follows:

| Recorded boundary | Records |
|---|---:|
| Before retained refs; earlier cause unknown | 887 |
| Tracklet not admitted | 1,056 |
| Same-frame selected member | 29 |
| Final selection unresolved | 59 |
| Owner not allowed | 229 |
| Explicit phase hard gate | 1,064 |

These correlated candidate records are not frames or accuracy samples. The old
1,352 `not_selected` records separate into 1,064 explicit hard gates, 229 owner
exclusions and 59 unresolved final selections. This local result cannot relabel
the private Windows cases or identify their first causal failure.

The saved-detection replay helper is a bounded wrapper around the existing
resolver. It avoids re-decoding video for an isolated counterfactual and validates
input restoration, frame ordering and immutability. It does not replace a complete
application/report run or certify physical correctness.

## LabPics inference completed; fixed ranking rejected

The pre-interruption hypothesis used the author's published material-segmentation
checkpoint, fixed channels, original BGR preprocessing and per-image checkpoint
reset. Full-source input is the primary view; cropped ROI is a separately reported
ablation. The frozen rule ranks existing candidates using upper/lower material
probability differences over their recorded sectors. No new Y is proposed, no
weights are fitted and no output-dependent threshold is selected.

The first attempt completed one full-frame map and failed on the next checkpoint
reset because the model's half/float conversions created inference tensors.
The resumed runner changes only output destination and `torch.inference_mode()`
to `torch.no_grad()`, preserving the original failed artifacts. This follows the
[PyTorch guidance on inference-mode restrictions](https://docs.pytorch.org/docs/2.14/generated/torch.autograd.grad_mode.inference_mode.html).
All channels of the first frame remain pixel-value identical to the failed run.

The resumed run completed 14 image inferences: seven frames in two views, with
306 candidate records (153 per view). Independent recomputation from all 14 saved
maps verifies the scores, mask support, distinct sectors and missing values.
All 126 frozen input/source pins remain unchanged. Each view has 139 scorable
and 14 unscorable candidates; missing evidence is not a zero score.

| Frame | Confirmed target index | Primary full-frame rank | ROI rank |
|---|---:|---:|---:|
| 1140 | 9 | 5 | 2 |
| 1200 | 4 | 18 | 2 |
| 1260 | 4 | 18 | 7 |
| 1275 | 12 | 13 | 10 |
| 1320 | 9 | 11 | 5 |
| 1485 | 19 | 20 | 11 |
| 1560 | 20 | 15 | 12 |

The primary view ranks the wrong alternative above the target in all three
explicit pairs. The ROI view reverses those three pairwise orderings, but other
candidates outrank the true targets. Neither view places any of the seven reviewed
targets in its top tie set. A hypothetical top-ranked replacement would retain
none of the baseline's four correct selections and recover none of the three
missed targets. This is not a measured production accuracy score; unreviewed
alternatives are not declared physical artifacts.

The frozen ranking is CLOSED WITHOUT PROMOTION. The ROI pairwise signal is
retained as a limited observation, not substituted for the failed primary view
or retuned into a successful detector. This closes this particular model/readout,
not all learned material representations or detector improvement in general.

## Verification and exact scope

After resumption, six focused modules passed **245 tests**: recorded-loss audit,
saved replay, W3 targets, phase identity diagnostics, phase lifecycle and Oil
observation resolver. Tests include standalone/Unicode/foreign-cwd CLI execution,
malformed inputs, immutable source audits, original W3 compatibility and the
previously failed baseline terminal guard. The earlier 237-pass record remains
preserved and is not added to the new count.

The real saved-replay CLI was also run from `/tmp` with explicit package paths;
151-row resolution and refined-readout byte equality establish the entry-path
check. No fresh full 2,488-case suite, Qt run, application video run or Windows
qualification is claimed. Production source/dependency identity and the focused
boundaries justify this verification scope. Governance and whitespace checks
must pass on the delivered commit. The companion JSON pins local evidence and
code files; the handoff receipt records final base/head and repository status.

## Handoff and next boundary

Native evidence is under main's ignored directory:
`sample/output/s11-windows-first-detector-20261008-001/`.
It contains original failed attempts, replay results, readouts, model download
receipt, frozen hypothesis, original/resumed runners, maps and evaluation. The
isolated model environment/checkpoint are local assets, not runtime dependencies.
The delivery ZIP excludes that environment, the large model checkpoint/archive
and raw source videos; it includes the diagnostic code, branch patch, summaries,
selected reproducibility scripts, saved results and checksums. Follow the receipt
for exact included files. The repository remains sufficient for the standalone
readout; full model re-execution additionally needs the pinned public checkpoint
and the preserved source-input locations.

An operator with the **original W3 audit bytes** can optionally perform the narrow
recorded-filter query without a detector/media/label rerun:

```powershell
py -3 tests/diagnostics/s11_candidate_loss_audit.py --audit <existing-experiment.json> --expected-sha256 ba5fe04b28473f70387e363ef7d40077f559c80b1852755d997e1dd04171937f --output <new-readout-directory>
```

That SHA belongs specifically to the transferred first W3 target audit. A different
artifact needs its own previously recorded hash; do not edit the file to match.
This is an optional bounded query to resolve a named owner-filter question, not
another requested broad inventory, annotation cycle or field qualification.

Next detector work needs a distinct mechanism and Windows-relevant positive and
negative controls for actual boundary reappearance, continued full material and
residue/structure opposition. If private JSON is supplied, use the diagnostic to
separate explicit filtering from unresolved selection before changing an owner.
The local experiments supply neither a justified release predicate nor a useful
replacement ranking. Do not repeat them through threshold tuning, loosen the cap,
or interpolate missing values. S11 remains active with no new user judgment
required for this completed bounded investigation.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: Windows first causal stage remains unproven; the local saved readout distinguishes explicit recorded phase/owner exclusions from unresolved final selection without assigning physical identity.
- Logic-map impact: NONE — production source and original W3 producer are unchanged; standalone saved-output diagnostics add no detector owner.
- Failure-registry impact: NONE — hypotheses are rejected within existing phase/provenance/identity failure classes, with no new field repair or general physical cause established.
