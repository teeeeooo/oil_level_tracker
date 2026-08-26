# S11-R18 Secure-Windows Field Result

**Status:** `OPERATOR-REPORTED FIELD FAIL — TRANSFERRED CAUSAL AUDIT FROZEN`

The later operator-transferred bundle/trace audit is frozen in
[S11-R18 Windows Causal Closure](../../50-diagnostics/s11/s11-r18-windows-causal-closure.md).
That audit narrows the owners but preserves explicit named unknowns requiring
one diagnostic-only rerun. This original field-result record remains the
authority for the initial visual report and is not rewritten as if the private
bundle were locally reproducible.

## Result

R18 has been run on the target Windows environment against the private sample
identified as `windows_sample1_heating_coldstart`. The operator reports that
Base published no Oil at all. Accum's earlier false detections appear to have
been removed, but its Oil detection rate became lower. Foam is detected only
partially and the operator cannot yet classify its behavior clearly.

This is sufficient to reject R18 as a field-qualified detector. It is not
sufficient to assign a code-level cause. No R18 output bundle, debug trace,
run ID, exact segment table, source-coordinate audit or same-frame provenance
audit is checked into this repository.

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
- Base Oil recall is unacceptable because the canonical reviewed truth
  contains a visible Base drain interval.
- Accum safety may have improved, but reduced false publication does not
  compensate for lower real-Oil recall.
- Foam precision, recall, episode identity and coordinate accuracy remain
  unclassified from the transferred observation.
- The result does not prove whether failure begins at proposal recall,
  authority, tracklet confirmation, initial-state lifecycle release, bounded
  selection, Foam episode confirmation or final publication.

The R5 history makes an edge-origin hard lock a mandatory hypothesis to check:
R18 starts confirmed initial FULL behind `FILLED_BARRIER` and releases it only
through a confirmed downward top-origin owner. That source contract and the
Base zero-Oil result establish a recurrence warning, not runtime causality.

## Named unknowns

- R18 bundle/run identity and exact transferred source head;
- per-segment Oil/Foam row counts and source-Y values;
- presence and state of Base truth-corridor candidates and tracklets;
- the first failed `_drain_release` condition, if that path was reached;
- Accum candidate/tracklet availability versus lifecycle hard-gate rejection;
- exact Foam confirmed/public frames inside and outside the canonical
  672–680 s Foam interval; and
- same-frame selected-candidate, sequence and CSV equality.

The linked transferred audit closes or narrows these original unknowns and
defines the smaller remaining set. Neither record authorizes an R19 behavior
implementation, threshold change, Recipe adjustment, private
coordinate/timestamp exception or detector-specific branch before the
instrumented same-video rerun.

## Detector Governance

- **Logic-map nodes:** `OIL-PROPOSAL`, `OIL-AUTHORITY`, `OIL-TRACKLET`,
  `OIL-PHASE-INITIAL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `FOAM-EPISODE`,
  `PUBLICATION-PROVENANCE`
- **Failure-registry entries:** `S11-F02`, `S11-F05`, `S11-F07`, `S11-F08`
- **First harmful stage:** `NOT_PROVEN` — the operator result contains no
  checked-in completed-window bundle or debug trace.
- **Logic-map impact:** `NONE` — a field result does not change current source
  ownership or control flow.
- **Failure-registry impact:** `UPDATED` — the registry now records the R18
  operator-reported failure and the R5/R18 recurrence warning.
