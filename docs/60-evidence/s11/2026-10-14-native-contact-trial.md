# NCT-1 — ordered native-side contact interaction

## Frozen protocol

This trial tests whether the **combination of two native side appearances**,
with separate Foam/liquid targets, preserves qualified uppers while rejecting
internal changes and structures across exposed source recordings. The
[architecture contract](../../20-architecture/s11-contextual-role-observation-design.md#ordered-side-contact-interaction-trial-nct-1)
defines the fixed kernel, loss, split, operating point and stop rule. Its joint
term differs from the closed native head's additive side score; the additive
and mean-RGB arms isolate that distinction without changing data or geometry.

Inputs reuse the [complete role corpus](../../50-diagnostics/s11/2026-10-14-semantic-role-readiness/corpus.json):
109 paths, 84 available native inputs, 17 qualified roles, 92 unknowns, four
recordings and six frames. The runner revalidates the complete corpus and all
source/path/RGB pins before fitting. All 48 saved semantic observations remain
unchanged and unused. Water C requires no new encoder output.

Exactly three arms × four held-recording folds × two independent targets are
fitted: **24 deterministic float64 solves**, using fixed ridge 0.01 and a zero
operating point. Class/source/path balancing prevents the four Miso uppers from
counting as four independent recordings. Opposite positive roles and N1 remain
partially specified; no pure patch labels or new negative truth is invented.
Unknown paths receive diagnostic predictions but no evaluation truth or fit loss.
Unavailable paths receive null scores, and UNKNOWN never counts as correct
opposition. No arm or hyperparameter is selected after inspecting outcomes.

The primary necessary condition is **14/14 Foam controls, 10/10 liquid controls
and N1's disjunction** on held-source predictions. Fitting results are separate.
Any failure closes this fixed operation without promotion. A control pass cannot
establish general classification, an untouched holdout, calibrated confidence,
raw-front recovery, a production consumer or Windows field effectiveness.

Execution entry: `tests/diagnostics/s11_native_contact_trial.py --root <repo>
--plan <plan.json> --output <managed-work>/readout.json`, from `/private/tmp`.
Source, tests, exact input pins and this protocol are frozen at a clean commit
before the run. Current Python/NumPy/Pillow are used, with BLAS/OMP thread limits
of one. Bound execution to 120 s, 1 GB RSS, 8 MB scratch and 3 MB retained. No
retired runtime/model is restored. Retain complete compact scores, final dual
coefficients, source/feature hashes and verification; remove owned intermediates.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F01`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: the prior shared surface observations fail qualified uppers versus structure before candidate consumption. This trial tests ordered-side interaction and separate role support at that observation boundary; it does not assert that downstream admission/ownership is repaired.
- Existing feature coverage: reuse all six pinned native frame geometries, visible-support decisions and both 7×7 side footprints from the complete corpus. No enlarged crop, new edge, semantic forward or inherited score enters the regressor. Sample4 exclusions/templates remain empty and Local XY OFF; completed D2/Local XY failures remain controls. Recipe/session/static-learning, production candidate/episode and report paths are bypassed, so this run cannot establish their efficacy or failure.
- Execution scope: one offline CLI validates saved source/roles/pixels, performs the 24 predeclared kernel solves and predicts the complete held-source population. No source video decode, temporal propagation, model download, GUI, production sequence/report replay or Windows qualification. The existing physical replies are never expanded to pure-side labels or unknown-path negatives.
- Logic-map impact: NONE — this adds an offline research operation; no executing production owner, setup parameter or runtime schema changes.
- Failure-registry impact: NONE — separate-head/support testing refines the existing appearance and coupling risks; no accepted repair or new general failure theorem is claimed.
