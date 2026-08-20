# S11-R14 Phase-Component Replacement Validation

## Acceptance boundary

R14 remains open until local regression/replay and private Windows Base/Accum
field validation pass. Local success authorizes the Windows replay; it does not
close S11.

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

