# S11 O2 fixed-score shadow experiment

Status: executable exploratory experiment; **not a calibrated identity classifier**.
Owner: `tests/diagnostics/s11_shadow_experiment.py`. Operational entry:
[local O2 procedure](../../40-operations/s11-o2-local-shadow-evaluation.md#고정-점수-shadow-실험--기존-라벨로-실행).
The [work plan](../../00-project/work-plan.md) owns current acceptance;
[V3](../../30-validation/s11-interface-observability-witness-validation.md#v3--operating-point-discipline)
continues to govern calibrated decisions. No existing partition rule is relaxed.

## Question and boundary

Does a locally concentrated, aligned intensity transition rank reviewed interfaces
above artifacts, and reviewed near positions above off positions, more often than
contrast or alignment alone? Existing retrospective controls contain opposing
contrast polarities and high-alignment structural negatives. They motivate a
combined-evidence experiment, not a fitted threshold or generalization claim.

This executable reads R22-3 packets and current v2 labels, computes scores without
labels, then evaluates orderings against the labels. It never decodes video, runs
the detector, writes labels, alters candidate geometry or emits calibrated
`INTERFACE_SUPPORTED`/`INTERNAL_OR_ARTIFACT` decisions. There is no optimization,
training, cutoff search, production integration or O3 promotion. Output schema
`s11-o2-score-experiment-v1` is deliberately distinct from the calibrated
`s11-o2-shadow-predictions-v1` import contract. Do not rename it for import.

The existing loader, strict JSON reader, packet/witness/geometry label validator,
logical/file hashes and deterministic percentile implementation are reused. This
separate diagnostic owner is needed because the existing evaluator scores typed
candidate decisions and numeric intervals, not uncalibrated evidence ordering or
qualitative path-order errors. It does not duplicate freeze or label persistence.

## Fixed hypothesis v1

For one captured center and scale, let d be stored signed_delta, z be stored
normalized_delta, a/b the two near-band normal_alignment values, and f/g the two
far-band gray means. All band names are matched by name, not array position.

- Contrast baseline C = abs(z) / (1 + abs(z)).
- Alignment baseline A = (a + b) / 2.
- Local concentration L = abs(d) / (abs(d) + abs(g - f) + 1/255).
- Combined score S = (C * A * L)^(1/3).

C compresses unbounded normalized contrast; A treats both near sides symmetrically;
L tests whether local contrast dominates the more distant context. The fixed
1/255 gray-unit floor avoids zero division. Equal geometric weighting is a
predeclared heuristic, **not an empirically optimal or probabilistic model**.
These choices and code hashes are embedded in the artifact. A failed comparison
is evidence against this combination; do not silently retune parameters after
seeing a result. Neither delta polarity, family name, Glass, frame, absolute Y,
selected/rejected status nor user identity labels are predictor features. Exact
coordinates are used only for measurement provenance and review matching.

The features share current-frame RGB derivation. Multiplication is an evidence
score, not an assertion of statistical independence. Captured normal_alignment
uses O1's vertical approximation; this tool estimates no physical curve normals.
Raw material/texture/static/peak features are not added speculatively to v1.

## Aggregation, availability and geometry

Per-point score is the deterministic median across available captured scales;
per-candidate score is the median across available points of native_path if that
geometry exists, otherwise candidate_center. It is not a majority vote on physical
identity. There is no fallback from unavailable native evidence to center scores.
Both point roles are retained for separate path evaluation. When O1 omits a
redundant center because its Y exactly equals the native Y, the identical native
measurement may be reused with `exact_center_alias=true`; the two human labels
remain separate and no path label is copied.

Each scale retains the consumed measurements, missing/null/present status,
availability and all three scores. False availability is not zero contrast.
Invalid numeric types, nonfinite values or out-of-range band means/alignment are
rejected; missing or unavailable required evidence produces null scores. A zero
score is a measured result. Pixel-error metrics are NOT_MEASURED: no human contour
is inferred from qualitative labels.

Raw per-method scores retain their individual availability. **Rankings and paired
ablations use matched_scores**, calculated using exactly the scales and points
where all three methods have usable evidence. Counts include common scale/point
support and unscorable candidate/pair totals. Thus extra baseline-only observations
cannot masquerade as a method improvement. Partial support remains partial; an
unscorable negative is not a correct rejection. Aggregation across only some
available points cannot certify a complete path. Absolute scale widths remain
attached to every point, and comparisons never pair candidates across cases.

## Automatic evaluation

- Candidate identity: within each case, every reviewed interface/non_interface
  candidate pair is checked for score order. Uncertain/unreviewed candidates are
  retained in inventories and rankings, not converted into negatives.
- Location: near/off pairs **within human interface identity**, separately for
  native_path and candidate_center. Report both all-X and exact-common-X subsets.
- Identity-negative control: interface/near versus non_interface/off at exact
  common X, explicitly distinct from the location task. This keeps the Accum
  idx10/15 comparison from being reported as pure localization discrimination.
- Outcomes: correct, reversed, tie (absolute tolerance 1e-12), unscorable. Combined
  improvements/regressions versus each baseline use common scorable pairs; all
  pair identities/geometry remain in JSON. Ties do not break by candidate index.
- Top ranks show all tied winners and their known identity, including unknown
  and all-negative scenes. There is no abstention cutoff. Zero positive/negative
  pairs is insufficient evaluation, not success. Counts of scales, points and
  pairs are correlated and are never reported as independent frame trials.

This supplies an executable ranking hypothesis and concrete failure list. It does
not supply calibrated identity decisions, a near/off classifier, numeric error,
coverage at an operating point, or a full detector accuracy result. A later typed
classifier requires the existing V3 prerequisites and a separately specified
operating point. Scores here must not be used as production acceptance thresholds.

## Runtime and integrity

Explicit v2 labels inputs only; all cases must remain regression. Each input and
the combined in-memory set pass existing validators (including cross-file case,
physical-record and recording/run checks). No combine file is written; stored
owners and partitions are unchanged. Conflicting case IDs or duplicate records
fail rather than silently deduplicate. Current labels are supplied explicitly;
old frozen snapshots are never auto-selected. Source-video binding remains the
existing bundle-link/attestation workflow and is not independently proven here.

Output goes to a new directory, with no overwrite:

- `experiment.json`: scores, matched scores, coverage, per-case pair errors,
  input label revision/logical and byte hashes, packet logical hashes, source-code
  artifact fingerprint and Python/platform identity.
- `summary.md`: rendered solely from that report, including pair outcomes,
  improvements/regressions, candidate rankings and unreviewed path counts.
- `complete.json`: emitted last, containing hashes of both outputs. It confirms
  completion only when the hashes match; partial artifacts without it are invalid.

Input byte hashes are checked before/after computation and publication. Changes
or an existing writer lock fail the run. Do not edit labels concurrently. This is
change detection, not a filesystem lock against unrelated programs. Data stays on
the Windows PC; the tool uploads nothing. The code fingerprint includes this
script and the evaluator/hash owners; Git/ZIP identity can additionally be noted
by the operator. No historical execution commit is inferred from app version.

Resource limits fail explicitly: 64 cases, 128 candidates per case, 16 sectors per
candidate, eight scales per center, 10,000 potential pairs per comparison. Input
JSON retains the existing 128 MiB limit. No data are silently truncated.

## Local validation / Windows scope

Synthetic tests exercise fixed formulas, polarity invariance, missing/null/zero,
center/native mapping, equal-center alias without label inheritance, matched
support, identity/location separation, all-negative/unreviewed rankings, ties,
reversed pairs, duplicate/stale provenance and input preservation. CLI tests use
real serialized O1 synthetic-raster packets, migrated labels, a non-repository
working directory and Korean/spaced paths. Multi-review loading runs through the
actual command owner. These checks do not establish private-video discrimination.

Windows must run the existing three reviewed inputs and inspect common coverage,
wrong orderings and top non-interface ranks before another feature change.
If common support is inadequate, report that limitation instead of calling
missing evidence a successful classifier rejection. No additional annotations,
new video windows, split changes, freeze, detector rerun or threshold fitting are
needed to execute this first experiment.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: potentially treating correlated evidence scores, missing support or retrospectively selected thresholds as physical identity; this experiment exposes support/order errors without promoting scores to detector authority.
- Logic-map impact: NONE — offline packet consumer changes no detector, selector, witness writer or production publication.
- Failure-registry impact: NONE — generic two-sided retrospective controls test an explicit hypothesis; no private-coordinate rule or calibrated field repair is introduced.
