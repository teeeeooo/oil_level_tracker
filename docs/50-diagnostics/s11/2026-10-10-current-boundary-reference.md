# CBR-1 — current-boundary reference comparison

**2026-10-10 · CLOSED WITHOUT PROMOTION.** The fixed operation is implemented
and its arithmetic/provenance verified, but it does not support a physical
Oil/Foam challenger. Foam's unique outputs follow the lower glass rim; Oil has
no unique continuation output on the existing 0.5-second analysis grid. The
predeclared progression condition fails, so this variant ends before broader
regression, production integration or Windows qualification.

The [frozen operation](../../20-architecture/s11-interface-observability-witness-architecture.md#cbr-1-frozen-first-operation--2026-10-10)
and [acceptance contract](../../30-validation/s11-interface-observability-witness-validation.md#cbr-1-offline-comparison-entry)
own the method and gate. [Work Plan](../../00-project/work-plan.md) owns the next
transition. R22 behavior + R22-3/O1 diagnostics, Local XY OFF and O2 OPEN /
FIELD FAIL remain unchanged. All experimental physical decisions are
`NOT_EVALUATED`; rejecting measurement feasibility is not scoring an implemented
physical classifier as all-negative.

## Frozen implementation and inputs

- Intake was committed as `5c596a7`; the helper, tests and exact operation were
  committed as `376132fb725454973031bd8d6c57982caeaca2db` **before real outcomes**.
- Extended the existing offline owner
  [`s11_boundary_temporal_probe.py`](../../../tests/diagnostics/s11_boundary_temporal_probe.py),
  reusing the complete saved `measure_edge_fragments` geometry. No production
  caller, new segmentation framework, Recipe field or report path was introduced.
- Used all **167 saved rasters / 198 plan-frame queries**. The original plans,
  approximate reference points and source X correspondence were unchanged:
  Foam f420–510, Oil f1275–1350, Structure f450–480. Three initialization queries
  are excluded from continuation, leaving 90 + 75 + 30 = **195**.
- Compared visible native BGR samples at Y−2/Y+2 on current Canny fragments;
  no H0/Foam labels, transported LK positions, reference update, interpolation,
  grouping change or additional ablation entered inference.
- [Preflight](2026-10-10-current-boundary-reference/preflight.json) pins 341 input
  paths, 221 production Python files, both diagnostic owners and the runner.
  It also freezes the review frames, cadence and progression rule. These are
  exposed development/regression inputs, not independent holdout evidence.

## Complete comparison

Counts below describe **appearance hypotheses**, not correct detections or recall.
The analysis subset is absolute frame indices divisible by 15 at nominal 30 fps;
this stateless operation has no dependency on intermediate native frames.

| Plan | Continuation queries | Unique / ambiguous / no center | Longest unique / missing native run | Analysis-grid unique / queries |
|---|---:|---:|---:|---:|
| Foam | 90 | 40 / 50 / 0 | 5 / 8 | 3 / 6 |
| Oil | 75 | 19 / 56 / 0 | 5 / 16 | 0 / 5 |
| Structure appearance reference | 30 | 0 / 0 / 30 | 0 / 30 | 0 / 2 |

"Missing" here means no unique provisional center. It does not certify absent
physical fluid, loss of every current edge or a successful physical abstention.

| Continuation candidate funnel | Foam | Oil | Structure |
|---|---:|---:|---:|
| All observed fragments | 110,353 | 75,876 | 37,098 |
| Have reference X columns | 50,566 | 13,592 | 507 |
| Have usable visible paired samples | 41,133 | 9,678 | 323 |
| AB strictly preferred | 7,951 | 2,671 | 76 |
| AB-preferred fragments with center intersections | 158 | 172 | 0 |

These are fragment/query counts, including distinct junction alternatives;
they are not independent objects. Full per-frame counts, reasons, coordinates
and detail hashes are in the [readout](2026-10-10-current-boundary-reference/readout.json).

## What failed and what remains unknown

### Foam: wrong-region appearance survives

All **40** unique continuation outputs are Y879 or Y880, and a provisional
alternative at these rows exists in **90/90** continuation frames. This is a
description of the observed output range, not a newly fitted scoring tolerance.
The [source/overlay sheet](2026-10-10-current-boundary-reference/foam-positive-review.png)
shows the orange marks on the lower glass rim in the displayed f438/450/510
unique-output cases. This is the agent's source-image interpretation; existing
approximate user Foam references near the middle of the glass remain unchanged.
No new per-frame exact physical labels are manufactured.

At f450, fragment 1278 has six usable pairs and losses AB=787, BA=2027,
AA=1491, BB=1323. It passes the declared comparison at Y880. The unique rim
outputs use **4–14 pairs**, so dismissing only one-pair candidates would not
resolve this observed failure. The fixed variant is not retuned that way.
The longest unique-output run is five native frames; the wrong-looking rim
alternative remains present even when other fragments cause frame abstention.

### Oil: alternatives survive the role comparison

The [Oil sheet](2026-10-10-current-boundary-reference/oil-positive-review.png)
retains both upper-pattern and lower-boundary-vicinity alternatives. At f1320,
the AB-preferred center candidates are Y817 (13 pairs) and Y844 (21 pairs).
Thus this example loses a unique center at **role discrimination**, despite
both geometries and substantial paired support being available.

The five continuation analysis times 43, 43.5, 44, 44.5 and 45 seconds are all
ambiguous. Nineteen native-frame outputs, including Y825/826, do not demonstrate
the reviewed rapid-boundary movement through 42.5–44 seconds. Later exact
center truth, pixel error, physical wrong/missing-run lengths and event-quality
metrics remain **NOT_MEASURED**. The existing user's 45-second **right-hand**
LK-cluster judgment is separate from these central CBR outputs and stays closed.
No repeat interpretation request is needed to reject this variant.

### Structure: missing comparison is not rejection

The single Structure reference is at X561 while the fixed center is X595.
Across continuation, **none of 414 center-intersecting fragments** reaches a
reference X column; therefore none has usable paired support at the center.
The [control sheet](2026-10-10-current-boundary-reference/rim-opposition-review.png)
has no marks for that reason. This is a correspondence-availability failure,
not a measured negative-control success or 0% false-positive rate. No comparable
structure explanation was supplied to the positive-role queries; their field
remains `NOT_MEASURED`, as predeclared.

### Why four appearance losses do not supply four independent checks

For the identical sample domain, let U(A)/U(B) be upper-side residual sums
against reference A/B, and D(A)/D(B) the lower-side residuals. Then:

```text
AB = U(A) + D(B)       BA = U(B) + D(A)
AA = U(A) + D(A)       BB = U(B) + D(B)
AB + BA = AA + BB
```

Consequently, AB < AA and AB < BB already imply AB < BA. The condition is
equivalent to aggregate upper-side preference for A and lower-side preference
for B; it supplies no independent structural or material identity test.
This identity and decision equivalence hold for **all 51,783 measured
candidates** in the saved results. A lower rim with the same appearance ordering
can therefore pass without being the desired interface. The first supported
harmful stage is the provisional role comparison, before tracking/phase/episode
gates. Reference purity, general optical behavior and private Windows first
physical causes remain unknown.

This does not prove that references or conventional vision are impossible.
It rejects this particular measurement as sufficient evidence for progression.
More reference columns, minimum length, stencil changes or junction merging
would be after-result changes to the closed variant, not demonstrated repairs.

## Verification and preservation

- **88 focused tests passed**, including 20 new current-boundary cases, before
  real-data evaluation. They cover current-geometry binding, exact loss arithmetic,
  inclined stationary geometry, center/side visibility, missing/mixed references,
  ties, measured/unmeasured opposition, copied distractors, crossing alternatives,
  independent calls and budgets. They prove diagnostic invariants, not resistance
  to real optical warps or physical classification accuracy.
- An independent saved-pixel oracle imported no comparator. It reconstructed
  every query's source mapping, sample values, four losses, missing reasons,
  candidate status, center decision and aggregate outcomes from original NPZ
  arrays: **227,190 candidates / 82,708 pairs / 207,132 losses / 198 queries**,
  all matching. [Verification receipt](2026-10-10-current-boundary-reference/verification.json).
- All 341 input and 221 production-source pins still match. There was no source
  video decode, production rerun, runtime change, truth edit or Windows run.
  Saved comparison calls total 3.58 seconds, maximum 0.029 seconds per query on
  this Mac; this excludes acquisition and is not a target-platform benchmark.
- [Machine record](2026-10-10-current-boundary-reference.json) inventories 206
  original files and eight byte-identical Git copies: preflight, readout,
  verifier receipt, two scripts and three review sheets. Native candidate details
  remain under `sample/output/s11-cbr1-20261010-001/`; the local
  `native-evidence.zip` contains all 206 members, with every hash and CRC checked.
  The ignored archive is not an external backup or a self-contained replay
  package: upstream arrays/media remain local. Fresh clones get the compact
  records/scripts/figures, not the 198 native detail files or source media.
- Preserved scripts contain their original relative-root/output paths. They
  are archival source, not commands to execute from this documentation directory.
  Both write with exclusive creation and must not overwrite the frozen run.
- Repository checks cover 767 changed-document local links/anchors with no
  missing targets, byte/hash preservation, S11 governance against `cc17924`
  including the worktree, and `git diff --check`. All pass; changed scope is
  documentation and offline diagnostic/tests only.

## Consequence for subsequent work

The supplied specification's first-comparison stop rule applies: terminate this
variant, do not spend the four-Mac/public regression or Windows budget on it,
and do not change phase/episode gates to recover provisional coordinates.

The next design needs a **distinct, stated role-discriminating observation**
before another real-data trial. It must explain both the accepted f450 lower-rim
counterexample and the competing f1320 Oil candidates, provide actually comparable
opposition, and retain stationary/crossing/optically ambiguous controls. Spatial
or temporal context is only a design direction until a precise operation and
falsification rule exist; long edges, persistence or motion alone are not a
replacement identity certificate. A different name for the same side ordering
does not reopen this experiment. The broader optional-reference question stays
unresolved; no additional user setup or mandatory marker is adopted.

No new user pixel judgment or Windows execution is needed to reach this
disposition. A fresh mechanism proposal, or a product-scope change if required,
must precede the next implementation; current authority stays in Work Plan.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PROPOSAL`, `OIL-CANDIDATE`, `FOAM-CANDIDATE`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: the frozen appearance comparison admits observed lower-rim Foam alternatives and simultaneous upper/lower Oil alternatives; the Structure control also lacks common reference columns at the center. This is an offline measurement failure, not a newly identified production or Windows first physical cause.
- Logic-map impact: NONE — the existing offline probe gained an explicitly nonphysical measurement function; no production caller, candidate authority, publication route or accepted runtime changed.
- Failure-registry impact: NONE — the result instantiates existing appearance-identity leakage, representation/availability and provenance/tuning limits; no new failure class or physical repair is asserted.
