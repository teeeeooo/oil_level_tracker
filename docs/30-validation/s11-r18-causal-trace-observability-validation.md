# S11-R18 Causal Trace Observability Validation

**Status:** current validation contract for the diagnostic-only rerun build

## Local acceptance

1. Existing Oil phase and Foam episode behavior tests remain unchanged and
   pass.
2. Initial-FULL and partial-fill release diagnostics report the same ordered
   predicates used by the decision, including first failure, selected ID and
   ambiguity.
3. Foam eligibility and episode diagnostics report exact gate results and the
   directed-front or stable-layer formation branch.
4. Nested dictionaries and lists survive JSONL sequence annotation.
5. Existing characterization, same-frame provenance, CSV mapping, Artifact,
   graph, and full regression suites pass without approved-output changes.
6. Detector governance and whitespace checks pass.

## Windows closure run

Run the same private sample identifier
`windows_sample1_heating_coldstart` once with debug trace enabled. Do not reuse
the R18 output bundle as runtime evidence for the instrumented source. Preserve
the R18 bundle as historical comparison only.

The returned audit must:

- verify source/runtime versions and 1,202-row Glass/segment assignment;
- confirm selected-candidate, completed-sequence, and CSV equality;
- enumerate Base `initial_full_drain_release` evaluations by first failed
  predicate and identify any qualifying/ambiguous release;
- enumerate Accum `partial_fill_drain_release` calls, established-fill last Y,
  every predicate, qualifying/selected IDs and ambiguity;
- report Foam candidate eligibility failed gates, track/segment membership,
  alias result, segment predicates and formation branch for 653–680 s; and
- compare publication only against canonical segment truth, leaving individual
  Y accuracy `NOT_EVALUATED` without reviewed anchors.

R19 behavior design begins only after this audit. A diagnostic mismatch, a
missing expected field, or any output regression blocks design and requires an
instrumentation correction—not a detector threshold or policy change.
