# S11-R18 Secure-Windows Field Result

**Status:** `R19_DESIGN_INPUT_READY_WITH_NAMED_UNKNOWNS / field FAIL`

The corrected operator-transferred bundle/trace audit is frozen in
[S11-R18 Windows Causal Closure](../../50-diagnostics/s11/s11-r18-windows-causal-closure.md).
That audit narrows the owners and preserves explicit named unknowns. No
further Windows diagnostic rerun is needed before R19 design. This original
field-result record remains the
authority for the initial visual report and is not rewritten as if the private
bundle were locally reproducible.

## Result

R18 has been run on the target Windows environment against the private sample
identified as `windows_sample1_heating_coldstart`. The operator reports that
Base published no Oil at all. Accum's earlier false detections appear to have
been removed, but its Oil detection rate became lower. Foam is detected only
partially and the operator cannot yet classify its behavior clearly.

The corrected rerun preserves exact 1,202-row membership and same-frame
selected-candidate/sequence/CSV invariance, but those are provenance and
coverage facts, not frame recall. This is sufficient to reject R18 as a
field-qualified detector. It is not sufficient to assign a code-level cause
from the original operator report alone. That original report contained no
checked-in output bundle, debug trace, run ID, exact segment table,
source-coordinate audit or same-frame provenance audit; the transferred
rerun facts are recorded below, while the private artifacts remain external.

## Completed causal-observability rerun

The corrected transferred rerun used bundle
`oil_level_analysis_R18개선_add_artifact_modify_#2_20260826_135338`, run
`a0e9b034-4f58-4ad5-85be-294ab435015a`, for
`windows_sample1_heating_coldstart`. Canonical membership assigned every row
exactly once (601 Base + 601 Accum), with `unassigned=0` and `duplicates=0`:

| Segment | Rows | Oil | Foam |
|---|---:|---:|---:|
| `WS1-BASE-FULL-PREFIX` | 140 | 0 | 0 |
| `WS1-BASE-DRAIN` | 225 | 0 | 0 |
| `WS1-BASE-RAPID-REFILL` | 3 | 0 | 0 |
| `WS1-BASE-FULL-SUFFIX` | 233 | 0 | 0 |
| `WS1-ACCUM-EMPTY` | 347 | 0 | 0 |
| `WS1-ACCUM-ENTRY-SPLASH` | 37 | 17 | 7 |
| `WS1-ACCUM-FOAM-LAYERED` | 16 | 8 | 11 |
| `WS1-ACCUM-POST-FOAM` | 41 | 1 | 0 |
| `WS1-ACCUM-DRAIN` | 160 | 0 | 0 |
| **Total** | **1,202** | **26** | **18** |

Oil counts by segment are Base `0/0/0/0` and Accum `0/17/8/1/0`;
Foam counts are Base `0/0/0/0` and Accum `0/7/11/0/0`.

Only the compared same-frame fields were tested for invariance: selected
candidate, completed sequence and CSV values matched on all `1,202/1,202`
(`1202/1202`) common rows with zero mismatches. Exact sequence/CSV publication
counts were Oil `26` and Foam `18`. This is row/segment coverage, not
per-frame recall; individual reviewed Y anchors are absent and remain
`NOT_EVALUATED`.

The causal facts are: Base rapid-refill Oil presence `0` (`FAIL`) with exact Y
`NOT_EVALUATED`. The operational `Y <= 800` cohort has 245 release evaluation
rows and zero passed; the lower `Y > 800` (including `Y876–926`) entrance
rejection is correct safety behavior, not the actual Oil root cause. The
earliest harmful Base stage is before-or-at `OIL-PHASE-DRAIN` and
`NOT_PROVEN`. Accum 700–780 s DRAIN-only had 264 `release_evaluations` (264
eval rows) and zero passed; retained/non-updated established snapshot owner
`000388:0265` (`last_y=219`, `last_frame=398`, sequence offset) remained
non-updated. `release_evaluations` are evaluation rows, not raw proposals or a
sequential funnel, and the non-update cause plus actual drain candidate
identity/direction remain unknown. The initial EMPTY pre-entry hard gate is
direct behavior; partial-release was evaluated before the later fail-closed
`allowed=frozenset` result. A `release_evaluated=false` trace means no
evaluation rows, not proof that the function was not called.

Foam top-level eligibility exists under `candidate.features`, while nested
compact fields are separate diagnostics. Eligibility at 677.5–678.5 s fails
`layer_coherent` (with `supported_layer_shape` also failing at 678.5 s). At
679–679.5 s the first failure is `formation_witness`, whose formation first
fails `bounded_stable_front` because `mean_relative_front=.0411 <= .12`.
The bounded predicate uses `span <= max(3, h * .015)` and
`mean_relative_front > .12`, not front rise. Accum `h=583.2` gives `8.748`, so
span 9 fails. ENTRY-SPLASH false tracks `0020`/`0032` passed `directed_front`,
and `0036` passed `stable_layer`; POST-FOAM and DRAIN had zero confirmed Foam.
Deduplicate segment diagnostics by `segment_id`.

## Evidence boundary

The observations below are the complete transferred evidence:

| Glass/series | Operator observation | Field disposition |
|---|---|---|
| Base Oil | Oil detection `0`; no Oil was detected | FAIL |
| Accum Oil | Prior false detections appear removed; Oil detection rate is lower | FAIL / exact recall not measured |
| Foam | Some Foam detection is visible, but behavior is unclear | NOT EVALUATED |

The exact R18 source identity used on Windows is not bundle-proven here. The
locally accepted source baseline remains the R18 implementation on `main`, but
this record does not convert that repository identity into run provenance.

## Frozen conclusions

- R18 local acceptance did not predict field effectiveness.
- Base Oil rapid-refill presence is a FAIL; exact Base Y remains
  `NOT_EVALUATED` because no frame-exact truth was supplied. Base Oil recall is
  unacceptable because the canonical reviewed truth
  contains a visible Base drain interval.
- Accum safety may have improved, but reduced false publication does not
  compensate for lower real-Oil recall.
- Foam precision, recall, episode identity and coordinate accuracy remain
  unclassified from the transferred observation.
- The original operator result did not prove whether failure begins at
  proposal recall, authority, tracklet confirmation, initial-state lifecycle
  release, bounded selection, Foam episode confirmation or final publication;
  the corrected rerun narrows these boundaries as recorded above.

The R5 history makes an edge-origin hard lock a mandatory hypothesis to check:
R18 starts confirmed initial FULL behind `FILLED_BARRIER` and releases it only
through a confirmed downward top-origin owner. That source contract and the
Base zero-Oil result establish a recurrence warning, not runtime causality.

## Named unknowns

- Base actual interface first loss;
- Accum snapshot non-update cause and actual drain candidate identity/direction;
- owner-bounded selector abstain predicate; and
- exact reviewed Y anchors.

The linked transferred audit closes or narrows the original report unknowns
and defines this smaller remaining set. Neither record authorizes an R19
behavior implementation, threshold change, Recipe adjustment, private
coordinate/timestamp exception or detector-specific branch. No threshold or
design proposals are made in this evidence. The evidence is ready for R19
design input; no further Windows diagnostic rerun is needed before R19 design.

## Detector Governance

- **Logic-map nodes:** `OIL-PROPOSAL`, `OIL-AUTHORITY`, `OIL-TRACKLET`,
  `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`,
  `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-EPISODE`,
  `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `TRACE-PUBLICATION`
- **Failure-registry entries:** `S11-F02`, `S11-F05`, `S11-F07`, `S11-F08`,
  `S11-F09`, `S11-F10`
- **First harmful stage:** Base is before-or-at `OIL-PHASE-DRAIN` and
  `NOT_PROVEN`; Accum is before or inside partial-fill release with the exact
  predicate unknown; Foam gate findings are split between `FOAM-CANDIDATE`
  and `FOAM-EPISODE` as recorded in the corrected rerun.
- **Logic-map impact:** `NONE` — a field result does not change current source
  ownership or control flow.
- **Failure-registry impact:** `NONE` — this record reports the transferred
  R18 observations without changing the durable mechanism registry.
