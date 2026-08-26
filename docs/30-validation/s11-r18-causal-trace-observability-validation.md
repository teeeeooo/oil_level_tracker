# S11-R18 Causal Trace Observability Validation

**Status:** `COMPLETE — DIAGNOSTIC-ONLY WINDOWS CAUSAL CLOSURE`

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

## Completed Windows closure disposition

The same private sample identifier
`windows_sample1_heating_coldstart` was run once with debug trace enabled. Do
not reuse
the R18 output bundle as runtime evidence for the instrumented source. Preserve
the R18 bundle as historical comparison only.

The closure audit records:

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

The completed audit is frozen in the [R18 Windows causal closure](../50-diagnostics/s11/s11-r18-windows-causal-closure.md): Base lower `Y > 800` entrance rejection is correct safety behavior while the actual interface earliest loss is before-or-at drain and unknown; Accum DRAIN has 264 evaluation rows and zero passed, with retained snapshot non-update cause and drain candidate identity/direction unknown; the owner-bounded selector abstain predicate is unknown; and Foam exact gates plus seven false ENTRY-SPLASH paths are known. Compared selected-candidate, completed-sequence and CSV fields are invariant on `1,202/1,202` common rows with zero mismatches. No further Windows diagnostic rerun is required for R19 design input. The [R19 validation contract](s11-r19-bounded-drain-release-chain-validation.md) is the approved successor gate; R19 remains unimplemented and field-unproven. A diagnostic mismatch, missing expected field or output regression in a future build still requires instrumentation correction—not a detector threshold or policy change.
