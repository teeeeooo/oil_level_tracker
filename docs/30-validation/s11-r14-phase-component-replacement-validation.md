# S11-R14 Phase-Component Replacement Validation

## Acceptance boundary

R14 passed its local regression/replay gate. Private Windows Base/Accum field
validation remains open; local success authorizes that replay but does not close
S11.

## Required automated gates

- phase identity unit tests cover calibrated corroboration, ordered-lower
  texture conflict and continuation-only fallbacks;
- component graph tests prove incompatible components cannot share trajectory
  or one continuation run, while same-component motion remains supported;
- low-conflict direct candidates receive soft recurrence opposition without
  hard demotion;
- Artifact templates do not change generated-candidate counts before rejection;
- existing same-frame publication and per-series validity tests pass;
- confirmed Artifact template selection supports Shift/Ctrl/Cmd semantics,
  select-all, clear-selection, bulk delete and multiple overlay highlights;
- Recipe save/load preserves the remaining templates after bulk deletion;
- full repository regression, compile and `git diff --check` pass; and
- bounded detector timing does not exceed the current documented local baseline
  by more than 1.5 times.

## Local replay

Run the existing four-video and user-like Artifact replays. Record final
numeric Oil, checked truth, MAE, maximum error, same-frame provenance, Foam
publication and fingerprints. Any accepted fingerprint change must be explained
by the R14 responsibility change rather than silently updated.

The accepted local replay processed 299 rows and published 187 numeric Oil
rows. Checked truth is 10/13 with 8.5 px MAE and 26 px maximum error; every
numeric row retains same-frame provenance. The sample3 internal completed-fill
interval publishes zero Oil, its late drain publishes 18 rows, and sample4 has
eight strict reviewed-range matches. Exact per-video counts and fingerprints
are owned by `tests/diagnostics/s11_r14_phase_component_replay.py` and the R14
evidence record.

The local runtime gate is 96.8 ms/frame over the decoded 113-frame sample4
workload, including official three-frame static learning and excluding seek,
report and debug output. This is below the 104.25 ms/frame acceptance ceiling,
although slower than R13 and therefore still a Windows observation item.
Python compile and the full repository regression pass with 1,542 tests.

## Private Windows gate

Use the saved Base/Accum Recipes, including Artifact templates. Record detector
and resolver version, final-publication integrity, proposal recall at reviewed
rows, identity/authority/component, component switches and path-stage outcome.
For Foam, report raw, eligible, confirmed, public and `foam_is_valid` separately
from Oil validity.

PASS requires materially correct reviewed Oil and Foam behavior, not coverage.
The known rim/bracket, broad material/residue and upper residue components must
not form a published Oil run. If reviewed Oil has no proposal, classify that as
generation failure instead of weakening authority globally.
