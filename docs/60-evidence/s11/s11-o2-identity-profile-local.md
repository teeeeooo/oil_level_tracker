# S11 O2 identity profile — local implementation evidence

Date: 2026-09-29. Scope: offline candidate identity experiment, extending
`tests/diagnostics/s11_shadow_experiment.py` from base `15f06dc`.
[Experiment specification](../../50-diagnostics/s11/s11-o2-fixed-score-experiment.md)
and [Windows procedure](../../40-operations/s11-o2-local-shadow-evaluation.md)
own the mechanism and execution instructions. No private Windows input was read
or re-executed here. Current state remains owned by the work plan.

## Delivered boundary

`--identity-profile --reference <original v1 experiment.json>` compares the shape
of four O1 gray band means against fixed step/ramp/excursion templates. Existing
geometry preference and scale/point medians remain in force. Candidate identity
is evaluated without path judgments; original v1 reference results stay separate.
Common-support comparisons and profile-only coverage are distinct. The new
score has no label fit, threshold, prediction decision or production authority.

A same-profile structural edge intentionally ties an interface in the synthetic
identity test: this experiment cannot certify physical identity from shape alone.
Missing far-band evidence remains unavailable. Masked-band midpoint approximation
and correlated scales/points limit interpretation. The model is a testable
hypothesis, not a claimed field fix.

Runtime artifact SHA-256 (code and specifications):
`776c8639cd2ac39a7ed7c9a5833348c6339a390d95fc1a5830a0967b481f6519`.
Root and receipt schema: `s11-o2-identity-profile-v1`.

## Verification

Focused local suite: **164 tests passed across the final checked scope**.
The initial six-file run passed 163 tests. A subsequent added identity-ranking
control and summary-only enhancement were checked by rerunning the 64 tests in
the identity-profile and existing score-experiment suites; the other 100 passing
tests were not invalidated. New identity-profile coverage is 22 tests.

```text
tests/unit/test_s11_identity_profile.py
tests/unit/test_s11_shadow_experiment.py
tests/unit/test_interface_shadow_evaluation.py
tests/unit/test_s11_review_semantics.py
tests/unit/test_s11_review_records.py
tests/unit/test_oil_interface_witness.py
```

Controls include real O1 synthetic step/stripe rasters; polarity, constant/weak
profiles and offsets; a same-profile structural counterexample; signed ranking;
missing/null/invalid evidence; separate support views; unavailable native-path
preference without center fallback; label/metadata blindness; reference/input
drift rejection; immutable source/reference files; no output overwrite; and the
real CLI from outside the repository under Korean/spaced paths. Default and
locality-ablation regression tests pass. CLI help exposes mutually exclusive modes.

Governance and whitespace checks pass. Production code, labels, packets, prior
experiments and field disposition are unchanged. No canonical full-suite, Qt,
public completed-window replay or native Windows performance run was required or
performed for this offline consumer. Windows discrimination is pending; no
calibration, independent holdout validation or FIELD PASS is claimed.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: assigning physical identity from a shape or edge score that a structural boundary can also produce; the explicit structural-step tie and separated identity evaluation retain that ambiguity.
- Logic-map impact: NONE — only the offline packet experiment and its procedure change; production selector, measurements, ownership and publication remain unchanged.
- Failure-registry impact: NONE — a label-blind fixed-profile hypothesis is tested, without calibrated identity acceptance, private-coordinate branches or field-repair claims.
