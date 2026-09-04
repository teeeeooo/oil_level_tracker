# S11 Behavioral Lifecycle and Foam Witness — Local Completion Evidence

**Status:** `LOCAL PASS / WINDOWS REQUIRED`
**Evidence class:** completed local implementation, validation and review record
**Current status authority:** [S11 work plan](../../00-project/work-plan.md)

## Decision and scope

This record closes the approved two-seam S11 behavioral slice at local scope:

1. delayed drain-attempt admission now requires the existing positive
   direction, directional agreement and positive progress before consuming the
   episode-scoped attempt; and
2. Foam formation authority now uses bounded local witness windows and actual
   dynamic stable support rather than whole-track future support or a
   total-row shortcut.

The fresh Sol final review is recorded at
`/Users/sunjaekim/.codex/workflow-runs/oil_level_tracker/r20-behavior-20260904-final-approved.md`
with `FINAL_GATE: PASS`. The independent repair audit is recorded at
`/Users/sunjaekim/.codex/workflow-runs/oil_level_tracker/r20-behavior-20260904-audit-repair1.md`
with `AUDIT PASS`. The implementation and repair cards remain provenance, not
current status authority.

This is a generic local behavioral improvement record. It does not repair or
qualify the user-reported Windows field failure, claim physical Foam recall
improvement, regenerate goldens, or reopen private-media investigation.

## Identity and implementation fingerprints

The approved comparison base was
`119f218f2cf232e90f8e591e28feaab54f6fb42f`. The implementation/audit worktree
was on `main` at that base before closeout. The six source/test files touched
by the behavior slice were independently fingerprinted as follows:

| path | SHA-256 |
| --- | --- |
| `src/oil_tracker/adapters/vision/foam_episode_resolver.py` | `22f852c2634576b73caa2d31df62b2d577387e697d77ce00ecf91b5a267f5479` |
| `src/oil_tracker/adapters/vision/oil_phase_lifecycle.py` | `841df52ab8d678e1946ed7088c46ddae85217099d0f3fd7f53e8511adc700aaa` |
| `tests/test_s11_behavioral_repairs_integration.py` | `6fd563aba3e6dbc5096bdb6a0e58c619de86e35be2c34f307d04eeeae27bfba7` |
| `tests/test_s11_sequence_observability_integrity.py` | `7114a509368b01fee10ee3fc2f05369f90ddbb0f4972bc41b5b79770e2861bce` |
| `tests/unit/test_foam_episode_resolver.py` | `6d485c2212fd445a79b156fbd59a259892d0b1546d32cbcdb586453b20139fa8` |
| `tests/unit/test_oil_phase_lifecycle.py` | `8f1486abff88e94fe117d54f48757695e4eee2225d11830c895166f7f13dd246` |

No source/test/truth file was changed during this documentation closeout.

## Accepted behavioral witnesses

### Delayed drain readiness and completed-sequence provenance

The repaired integration constructs real `BoundaryCandidate` objects and runs
the completed `OpenCvPhaseDetector.resolve_sequence` path. It establishes an
initial-EMPTY fill at frames 0–2, then a confirmed post-grace distractor at
frames 9–13 and a distinct ready downward owner at frames 16–19.

The distractor coordinates `[90, 80, 100, 90, 110]` have signed direction
`+1` (positive image-Y movement), net progress `10.0` and directional
agreement `0.50`, below the policy `0.60`. It is non-ready because agreement
is insufficient; it is not an upward/direction-negative claim. Its frame-13
diagnostics retain the ownerless attempt (`available`) and fail first at
`drain_directional_agreement`. The approved-base comparison is red at the
non-consumption assertion.

The later owner has direction `+1`, net progress `40.0` and agreement `1.0`.
It consumes the attempt at frame 18; the unchanged bounded chain reaches its
threshold at frame 19, where the selected same-frame candidate publishes Y
`105.0` with the expected delayed-reacquisition reason. The integration proves
one selected candidate for each numeric row, selected-Y equality, exact
sequence → `TrackingSample` → CSV raw-Y equality, and no carry,
interpolation or snapshot-coordinate publication. Current is green; base is
red.

### Bounded Foam witness and dynamic stable support

`_foam_witness_windows` scans backward by index and preserves the prior
inclusive four-frame/2.0-second horizon without a full-prefix slice at every
endpoint. Its former slice-based implementation is output-equivalent on the
three recorded cases. A deterministic 1,200-item no-slice regression rejects
slices, checks both bounds and the final five-member window, and records
exactly `7,185 = 1,200 * 6 - 15` indexed reads.

Formation support is the union of same-frame members of passing local windows,
with maximal connected accepted-support runs counted once per track. Stable
support counts rows satisfying
`min(internal_motion, dynamic_support) >= 0.15`; three dynamic rows are
required, or exactly two dynamic rows may use the existing substantial
area/width exception. A static extent-changing tail cannot complete the
witness.

## Local corpus and source-image dispositions

The documented four-video replay used the checked-in recipes and reviewed
truth with:

```text
PYTHONPATH=src python3 -m tests.diagnostics.s11_r18_lifecycle_closure_replay \
  --output-root /tmp/oil_level_tracker_r20_behavior_corpus \
  --skip-fingerprint-check
```

It exited `0` with one isolated worker per video, 13 truth cases, 299
tracking rows and 162 numeric Oil rows. `--skip-fingerprint-check` was
required because this behavior slice intentionally changes bounded Foam
output; no golden was regenerated and the old fingerprint was not promoted to
truth.

| local sample | base tracking fingerprint | current tracking fingerprint | rows / numeric Oil | Foam result |
| --- | --- | --- | --- | --- |
| `base_sample_1` | `5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7` | unchanged | 30 / 28 | 0 episodes |
| `sample2` | `85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976` | unchanged | 5 / 4 | 0 episodes |
| `sample3` | `feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1` | `ab8043290174b40065987de1b189b826e0f06b7ae684cc78fc71054471f7799b` | 151 / 29 | 1 episode, 2 confirmed Foam rows |
| `sample4` | `0f2029475506c87aac3ec46bf118b3ae9a1ead0da45eb0d214e1d23ececf9154` | `e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1` | 113 / 101 | 1 episode, 26 confirmed Foam rows |

Overall local result: 13 truth cases, 11 numeric truth cases, MAE
`9.636363636363637 px`, maximum error `24.5 px`, coverage-adjusted MAE
`11.923076923076923 px`, same-frame provenance `PASS`; Sample3 completed-fill
remained `0` and late-drain numeric remained `12`; Sample4 visible-range
match remained `8`. Existing local truth misses are Sample2 t=0 and Sample4
t=0. These metrics are local evidence only and do not qualify Windows.

The intended Sample3 change removes Foam publication at 30.5305 s, 31.0310 s
and 32.0320 s, where the base constant front borrowed later segment evidence.
The direct ROI contact sheet
`/tmp/r20_sample3_frames/contact_29_40_roi.jpg` has SHA-256
`392109122cf4c6699a8d1901d8d40d9baaba11ff780ca1c2fdba839e2d2dba7b`; it
shows a fixed bright front in that prelude and a later rising local suffix at
about 37.0–38.0 s. The old base event capture
`sample3_sight_glass_02_FOAM_START_30.53.png`
(`12ca98cb70118150ddc43a07df36ccdf2625b7e679e2630a92d57e14572063f7`)
is not retained as an authority claim; the current direct source-frame
capture `sample3_sight_glass_02_FOAM_START_37.04.png`
(`2c3179204fa6ecb826e1790042ede4fb8f5129aa42badbf02bff359ba4ffbb33`)
supports the bounded onset disposition.

Sample4 also changes: Foam rows at 53.5 s and 54.0 s are left unconfirmed,
moving the public Foam-end landmark from 54.5 s to 53.5 s. The source ROI
contact sheet `/tmp/r20_sample4_frames/contact_roi.jpg` has SHA-256
`aed725954b794b9918c42351ea7723b8fb4b2513ffba439c0bd60990478a997a`.
The reviewed local material is pale/static without bounded local front
evolution after the 53.0 s dynamic witness; current failure is the bounded
stable-front gate. This is conservative fail-closed abstention, not evidence
of physical Foam absence and not improved recall. Late static/slow-layer
recall may decrease. Base/current end captures are
`sample4_sight_glass_03_FOAM_END_54.50.png`
(`b512e7a03a8f9cd9dfa21d5b947975ac920ead15dd0e246701a92fc417d8ccb9`) and
`sample4_sight_glass_03_FOAM_END_53.50.png`
(`154456e6271c010baa76540d4e9fabe5ea2e20b44d47b673cce8723b224f1d72`).
Source MP4 identities are unchanged: Sample3
`c2a45b2b3aa025dea405bfecad79228547f80bf8e1a9e337a400cc09f29f3c04` and
Sample4 `ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892`.

## Executed versus reused validation

### Executed or directly rechecked for the repaired head

| command/check | result | evidence identity |
| --- | --- | --- |
| `.venv/bin/python -m pytest -q tests/unit/test_foam_episode_resolver.py` | 25 passed | `/tmp/r20_repair1_foam.log`, SHA-256 `92536fc7d51cb85803c588bfd5cf246aa599a5906917e893e1a8b6b0085758a5` |
| former-slice/indexed Foam helper equivalence | 3 cases PASS | `/tmp/r20_repair1_foam_equivalence.log`, SHA-256 `c08c73fd858c88eaeaa340a801a2c5c2a1c14c9a6b4400c90d70807357ff3f0b` |
| `.venv/bin/python -m pytest -q tests/test_s11_behavioral_repairs_integration.py` | 1 passed | `/tmp/r20_repair1_integration_current.log`, SHA-256 `93c97c10af4fc8b54296201243c032c5e8295479ca6b4adc06019033d6f9e282` |
| approved-base integration comparison | expected FAIL at non-ready attempt assertion | `/tmp/r20_repair1_integration_baseline.log`, SHA-256 `72e25748233a0fac5f30a4f53071f0664d7cb755fd08d41e3c23d7517ca410f9` |
| fresh combined targeted Foam + integration run | 26 passed | audit terminal result |
| 1,200-item no-slice direct check | PASS; 7,185 reads | audit terminal result |
| direct runtime candidate diagnostic check | PASS; +1 / 10.0 / .50, attempt False→True, frame19 Y=105.0 | audit terminal result |
| `.venv/bin/python -m compileall -q src tests` | exit 0 | `/tmp/r20_repair1_compile.log`, empty-output SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `git diff --check` | exit 0 | `/tmp/r20_repair1_diffcheck.log`, empty-output SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| relative docs links | 646 checked, 0 missing | `/tmp/r20_repair1_links.log`, SHA-256 `aa2ec78c18fae213c2131df3f94c5d864acdd576cbf1496f7c30d0b691b52d1a` |
| `python3 scripts/check_detector_governance.py --base-ref 119f218f2cf232e90f8e591e28feaab54f6fb42f --include-worktree` | exit 0, `S11 detector governance passed.` | `/tmp/r20_repair1_governance.log`, SHA-256 `5054252290d7f2a5f8913daf1f690a541c7a6f4f2f04082fd264770893528818` |

### Reused without rerun

The full `.venv` suite (`1713 passed`), Qt partition (`252 passed`), adjacent
owner suite (`149 passed`) and four-video replay/truth output above were run
before the repair-1 audit and reused after final review. The repair changed
the Foam helper implementation without changing its output (three-case
equivalence plus the deterministic bound), changed the integration witness,
and left `oil_phase_lifecycle.py` unchanged. This is why the broad results
remain valid without a full rerun. The earlier focused 110-test result and
old integration shape are not reused as decisive repair evidence.

The corpus root manifests are `/tmp/oil_level_tracker_r20_behavior_corpus/replay_manifest.json`
(SHA-256 `2bd68ce8dbe5189c3136b8f2321ba4edd0889871ef2658dafad10568e6356188`)
and approved-base `/tmp/r20_base_replay/replay_manifest.json` (SHA-256
`9306f171ca093eb75449111f3193aef9de4f772911f0604752dfe41892359afc`).
These outputs, the sample-image dispositions and unchanged Oil/publication
provenance are reused as local evidence only.

## Deferred boundaries

Base release and rapid refill remain unresolved. Accum initial entry, fill
continuity/layered/post-Foam behavior and strict drain continuation/re-entry
remain unresolved. Their residuals require separate physical candidate/
identity evidence and transition contracts; no threshold widening, fake
coordinate, ID conflation, or row-only reversal was introduced here.

The user-reported Windows result remains `FIELD FAIL`; canonical Windows
field qualification and reviewed-Y effectiveness remain required. No Windows
PASS, physical Foam absence, physical recall improvement or automatic replay is
claimed. Optional decision-witness observability remains retained design-only
work.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: delayed attempt admission after established partial-fill owner loss (`OIL-PHASE-FILL`/`OIL-PHASE-DRAIN`) and bounded local Foam episode confirmation (`FOAM-EPISODE`); canonical Windows effectiveness and reviewed-Y outcome remain unknown pending required field replay.
- Logic-map impact: `UPDATED — the active map records the accepted delayed-readiness and bounded Foam-witness owners and routes completed evidence here.`
- Failure-registry impact: `UPDATED — existing F07/F08 guards record the constrained adaptations without adding a causal class or claiming field causality.`

The detector governance block passed; no new failure class was added. This
evidence document is the completed local record, while current sequencing
remains in the work plan and predecessor diagnostics, truth, retained
commitments and optional observability records remain historical/non-current
as routed by `docs/README.md`.
