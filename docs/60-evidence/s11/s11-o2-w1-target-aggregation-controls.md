# S11 O2 W1 — target and aggregation counter-controls

Date: 2026-10-01. Base: `540ec9d5a819ff9e2c3cbe81f8ab41630a9bb361`.
Scope: bounded source review plus executable synthetic target controls. No private
packet/video was read, and no Windows run, label edit, new score, production
decision, calibrated prediction or operating point was created.

The [W1 architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#w1-target-and-aggregation-contract--design-boundary)
owns semantics, [validation](../../30-validation/s11-interface-observability-witness-validation.md#w1-aggregation-challenger-controls--not-yet-acceptance-evidence)
owns acceptance, and [work-plan](../../00-project/work-plan.md#s11-work-item-ledger)
owns the next transition. This record verifies the W1 target/control boundary;
it does not claim a working replacement identity aggregator.

## Source review and reuse boundary

| Existing owner | Checked responsibility | Consequence for W1 |
|---|---|---|
| [score_candidate / evaluate_case](../../../tests/diagnostics/s11_shadow_experiment.py) | Median across available scales, then preferred-geometry points; labels only enter evaluation; exact native/center geometry and support counts retained | A local-position ranking becomes a candidate-identity ranking without a distinct identity model. Do not relabel partial positives to match that reduction |
| [profile_scale / identity_profile_views](../../../tests/diagnostics/s11_shadow_experiment.py) | Four gray means/ranges, step-versus-alternatives residuals, same median reduction | W0 rejection does not isolate sampling, pooling or physical shape collision; no further profile tuning follows from it |
| [review_geometry / path_summary / summarize](../../../tests/diagnostics/s11_interface_shadow_evaluation.py) | Identity and geometry-keyed qualitative judgments separate; no contour means no numeric location error; unresolved predictions counted with visible-frame recall | Reuse these evaluator owners for W3 rather than creating another comparison pipeline |
| [BandWitness / build_interface_witness](../../../src/oil_tracker/adapters/vision/oil_interface_witness.py), [measurement owner](../../../src/oil_tracker/adapters/vision/oil_interface_diagnostics.py) | Per-band static/material/glare, mask/valid extent, sampling ranges and lineage retained; glare excluded from visible pixels | Existing packets contain more context than C/A/L scores. Presence/meaning does not prove discriminatory utility or private availability |
| [OilCandidateEvidence](../../../src/oil_tracker/adapters/vision/oil_candidate_evidence.py), [phase identity](../../../src/oil_tracker/adapters/vision/oil_phase_identity.py), [authority](../../../src/oil_tracker/adapters/vision/oil_candidate_authority.py) | Production combines phase availability, boundary/material, texture, artifact/optics, spatial and representation context with explicit gates | These are existing responsibility owners, not ground-truth labels or an O2 classifier to copy wholesale. Motion is not required by every direct-interface route |
| [extract_frame](../../../tests/diagnostics/s11_interface_shadow_evaluation.py) | Packet retains witness and exact source identity; raw candidate rows are checked for provenance, not copied as full feature/context records | Production candidate features and temporal context cannot be assumed available in packet-only experiments |

Search covered existing score/profile/evaluator tests, witness raster tests,
historical glare fixtures and source/diagnostic implementations. Existing tests
already covered structural-step ties and unavailable-native preference. The new
test module groups W1's cross-target counterexamples through those same owners;
it adds no parallel scoring helper, CLI, schema or operational workflow.

## Reproduced counter-controls

Executable owner:
[test_s11_target_aggregation_contract.py](../../../tests/unit/test_s11_target_aggregation_contract.py).
Measurement-level constructions isolate reduction semantics; the last three
rows exercise actual O1 raster extraction. They are not independent video scenes.

| Control | Observed result / protected interpretation |
|---|---|
| Partial positive versus weak negative | Constructed contrast scores `[0,.9,0]` rank below `[.1,.1,.1]` under actual candidate median, while both near-versus-off pairs are correct locally. Holistic identity remains positive and two path points remain off |
| Isolated glare / hypothetical max | Max restores that partial-positive comparison but ranks the identical isolated glare above a full moderate positive. Max is a test-only rejected oracle, not a new method |
| Identical observables with opposite identities | Point evidence matches exactly and all three existing methods tie. Labels are used only in evaluation; no score or tie-break extracts physical truth from the annotations |
| Full and partial supported identity (scripted evaluator predictions) | Identity recall can be 1 with either all-near or off/near/off truth. Native path counts stay distinct; center aliases remain unreviewed. Empty contour leaves numeric error and full-path pass unmeasured; source Y is unchanged |
| Unresolved identical-observable collision (scripted evaluator predictions) | Both original human identities remain; two abstentions and zero visible-frame support recall are counted. No false support does not mean useful observation |
| Spatial layout | `[0,9,9]` and `[9,0,9]` measurement layouts have the same reduced scores but different geometry-indexed point evidence. A scalar discards arrangement; retaining arrangement alone still cannot solve identical-observable cases |
| Missing native / usable center | Three preferred native points stay unscorable although clean center measurements exist. No implicit geometry fallback |
| Partly missing scales | Three points remain in the denominator, with common-scale counts `[1,3,3]` out of `[3,3,3]`; no complete-coverage claim from a finite candidate score |
| Stationary interface / same-image structural step | O1 extraction is identical and profile scores are positive for the same constructed step image; witness decision stays NOT_EVALUATED. No motion gate or physical shape certificate is inferred |
| Interface crossing a static-reference region | O1 keeps static overlap `[0,0,1,0,0]`; clean siblings do not erase the central overlap. Existing C/A/L point outputs are identical with/without that context, showing it is omitted by the consumer. This does not establish that overlap distinguishes true interface from structure |
| Mask and glare occlusion | Two clipped/obscured sectors retain extent, unavailable bands and null score; clean sectors remain available. Excluded area/glare remain explicit rather than zero-strength negatives |

Scripted INTERFACE_SUPPORTED/UNRESOLVED inputs exercise the existing evaluator,
not the scorer's ability to emit those outputs. No automatic unresolved classifier
was implemented. Measurement-level values are chosen counterexamples, not fitted
thresholds. The spatial permutation uses normalized-delta inputs `[0,9,9]` etc.;
the partial-positive row lists their transformed contrast scores.

## Decision and remaining gap

The W1 aggregation rationale is to preserve geometry-indexed evidence and its
support/opposition/availability until a separately justified identity decision.
A local strength scalar answers a different question from holistic identity.
Neither median, max, motion, static overlap nor the existing step residual alone
is adopted as that decision. Indistinguishable supplied inputs require unresolved
inference, with both human truths retained and missed visible observations counted.
Independent scalar truth or a declared contour-to-scalar contract remains necessary
for scalar eligibility; no support-point average replaces a production candidate.

W1's target expectations and counterexamples are now executable and consistent.
The validated aggregation/classifier rule is still open. This is the October
specification's target-alignment boundary, not W4 efficacy or O2 acceptance.

**W2 collection is deferred, not completed.** Existing labels and synthetic controls
suffice to implement target accounting. More labels on identical observables cannot
make a score-only rule separate them. A later W4 proposal must name a measurable
context or geometry distinction, check its availability/provenance in existing
packets first, and request only the missing positive/negative controls if needed.
Private sampling error versus aggregation loss remains unresolved by these tests;
the synthetic median counterexample is not a causal claim about every BASE failure.

**Next boundary is W3:** extend the existing offline output/evaluator with distinct
candidate identity, exact local-support and scalar-eligibility meanings plus
abstention and visible-scene denominators. First verify with scripted decisions;
connect one W4 challenger separately. Preserve calibrated import and recording-group
guards. No additional Windows run, new video interval or human review is requested
by this W1 result. FIELD FAIL remains unchanged.

## Verification and identity

New W1 controls: **12 passed**. Combined focused suite: **155 passed in 5.08 s**:

```sh
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_target_aggregation_contract.py \
  tests/unit/test_s11_shadow_experiment.py \
  tests/unit/test_s11_identity_profile.py \
  tests/unit/test_interface_shadow_evaluation.py \
  tests/unit/test_s11_review_semantics.py \
  tests/unit/test_oil_interface_witness.py
```

Checked executable SHA-256 values:

| File/artifact | SHA-256 |
|---|---|
| New W1 test module | `fd9779ca4dc6668e1480083be288b19e814e341fcb51791df5861fa3212dfe9b` |
| Existing shadow experiment (unchanged) | `8cbb501faae75db588b7fe97027244f2bac6040a2e7a576122b73b6d2241f3a5` |
| Existing shadow evaluator (unchanged) | `d0de4554d23b73b2ad4ed9b74172202874fd4b94a1d8133528e41cacbfe3294c` |
| Identity-profile artifact (unchanged) | `776c8639cd2ac39a7ed7c9a5833348c6339a390d95fc1a5830a0967b481f6519` |

Governance, 120 relative document links/anchors and whitespace checks passed. No full
canonical/Qt suite, completed-window video replay, Windows performance or private
artifact validation was needed or performed: only tests and documents changed.
The two original audit specifications, score/evaluator code and runtime are preserved.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F01`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: in the constructed partial-positive control, candidate median reduction loses an otherwise correct local ordering; identical-observable physical identity remains unresolved. The first harmful stage for private cases is not established by this synthetic result.
- Logic-map impact: NONE — no production or offline scoring/evaluation control flow changed; tests call existing owners and documents define subsequent boundaries.
- Failure-registry impact: NONE — retained geometry, explicit missingness and no score-only physical authority enforce existing no-repeat rules without claiming a new field repair.
