# D2-A0 reference and candidate-support readiness

At `1c01bb59a529d2b95fefbe8a4bbda4292d6ebd1a`, the bounded technical readout is
complete; real reference attribution remains pending. This is not completion of
all D2-A0 gates or D2-A1 implementation. The user asked to proceed until a new
physical judgment was needed; the concrete checkpoint below is that boundary.

The [machine record](2026-10-08-d2-reference-readiness.json) pins 24 inputs and
the local runner/preflight. All input hashes are unchanged. The readout reuses
seven saved A1 frames and seven known recipes; no video decoding, detector or
resolver rerun, label/recipe edit, model fitting or Windows work occurred.
Runtime remains R22/R22-3, O2 OPEN and field disposition `FIELD FAIL`.

## Bounded readiness result

The four original Mac recipes and the D2 baseline copy have no templates.
The registered-pink experiment has one geometry-only template. The UI demo has
one reference in `mixed_or_uncertain` state, with valid recipe context. None of
these seven recipes supplies eligible `reviewed_support`. This is a bounded
current-work check, not a claim about every historical recipe or Windows data.

All 153 saved Oil candidates join by original input index, source and exact Y
across current detections, measurement lineage and interface diagnostics:

| Family | Candidates | Available existing evidence | Limitation / reuse decision |
|---|---:|---|---|
| `oil_hypothesis` | 59 | Exact hypothesis/measurement lineage for all 59; broad/narrow scalar and band evidence | Raw observations are profile aggregates. Do not invent an object contour from the whole horizontal band. Reuse `oil_shadow_observations` / `oil_pipeline_diagnostics`. |
| `material_path` | 30 | Native sector X/Y, chosen contrast channel and scale for all 30 | Existing generator can expose contrast sampling footprints; these are neither continuous paths nor complete masks of all score dependencies. |
| `raster_material_path` | 1 | Native sector geometry for the one candidate | Same material-path owner; keep separate lineage and basis. |
| `phase_transition_scan` | 21 | 315 band records: three radii × five sectors × 21 candidates | Existing `phase_transition_support` owns exact pooled band ranges. Expose measurement footprints separately from observed edges. |
| `calibrated_high_recall` | 42 | Candidate/scalar and supplemental row-profile source | No captured candidate-owned edge set or complete footprint sidecar. Retain unavailable rather than fill nearest edges. |
| `distributed_sobel_path` | 0 in these cases | Current generator source inspected | Grouped row-profile mechanism, not an observed contour; real availability remains NOT_MEASURED in this bounded sample. |

No candidate-owned observed-edge mask is retained by these inspected routes.
That is a source-backed representability finding, not a count of failed physical
interfaces. The 153 candidates remain the same exposed regression set; no new
scene inventory or target labels were created. Thirty-one native-path records
must not be called missing merely because the separate A1 lineage field says
`different_candidate_family`.

The smallest useful first integration would reuse the existing exact phase-band
and native contrast footprints with explicitly different statistics. An
`observed_raw_edge` comparison must stay unavailable wherever no such candidate
evidence exists. The reference alone cannot make those candidates edge tracers.
No new detector family, learned model or broad veto is implied.

## Concrete physical-review checkpoint

The assistant inspected the existing 44 s original and scoped preview, and the
closed 42 s semicircle review. The 44 s preview shows repeated curved edges, but
the assistant cannot establish that every displayed edge is glass structure
rather than mixed fluid/Foam. The earlier pink-candidate negative judgment and
42 s lower-semicircle judgment remain closed; neither labels these 44 s pixels.

The existing UI demonstration provides a reviewable proposal, **not an accepted
reference**:

- source f1320 / 44 s, crop origin `(543, 798)`, size `104×58`;
- proposed crop-local rectangle `(20, 18, 35, 12)`;
- half-open source rectangle `X[563,598), Y[816,828)`;
- 125 displayed eligible raw Canny pixels, mask SHA-256
  `d0238a02681fae24ca4f093290ed8dee9515609e0991201add8c171a766691e8`;
- snapshot SHA-256
  `600c6bc47b2b8f5d6a3ac89e80760c5d432d9739434e9c4d48db78394d1abb80`.

Original and marked views remain at
`sample/output/s11-d2-reference-ui-20261008-001/support-original.png` and
`support-scope.png`, with hashes in the machine record. The question asks whether
all marked edges may be attributed to fixed glass structure/pattern, whether
fluid/Foam is included, or whether the scope is unjudgeable. A rectangle alone
and an assistant interpretation do not change `review_state`.

If confirmed, preserve the user's exact scope in a new diagnostic recipe copy,
keeping original recipes and prior demo unchanged. If mixed/unknown, retain
that result and assess whether the input contract supports a useful smaller
scope; do not demand arbitrary pixel certainty or automatically reopen the
0/28 s Foam-covered reference question. Confirmation would establish only one
reference control, not full crossing/stationary/obscured controls or O2 readiness.

## Resource and implementation boundary

Fifty reads of the existing 20,830-byte snapshot gave median 0.408 ms and p95
0.438 ms locally. This measures decode only for one small reference, not detector
throughput, comparator overhead, maximum-size inputs or Windows performance.
The 640×160 crop / 1 MiB / 16-reference storage limits remain unchanged.
Incremental comparison latency/RSS/trace caps are **not frozen** yet; they must
be fixed against representative eligible inputs before D2-A1 integration.

Source inspection and metadata diagnostics can proceed without a human label,
and synthetic contract work remains permitted. This turn stops at the user's
requested physical-judgment boundary before choosing the real comparison scope.
No unused comparator or guessed mask was added to production. The existing
[comparison design](../../20-architecture/s11-interface-observability-witness-architecture.md#registered-support-diagnostic-comparison--planned-contract)
and [gates](../../30-validation/s11-interface-observability-witness-validation.md#registered-support-comparison-gates)
continue to own later implementation. Live sequencing is in
[Work Plan](../../00-project/work-plan.md).

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: no candidate-owned observed-edge set is retained by the inspected measurement routes; missing lineage must not be replaced with arbitrary nearby edges. This is not a newly proven physical error cause.
- Logic-map impact: NONE — this source/readiness audit changes no production owner, call path or runtime behavior.
- Failure-registry impact: NONE — physical attribution and pooled measurement geometry remain distinct; no accepted repair or new field result is claimed.
