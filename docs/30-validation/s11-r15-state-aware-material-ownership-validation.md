# S11-R15 State-Aware Material Ownership Validation

## Acceptance boundary

R15 is a replacement repair for the failed R14 private-Windows Base/Accum
result. Local regression authorizes, but does not replace, a new exact-head
Windows replay.

## Required automated gates

- Foam same-boundary aliasing uses symmetric distance and cannot classify a
  large inverted Oil/Foam separation as alias;
- unresolved Oil candidates cannot hard-veto a coherent dynamic Foam episode,
  and a prior alias cannot propagate without current authoritative coincidence;
- Foam candidates expose Foam-specific rejection stages in debug trace;
- confirmed initial EMPTY suppresses stationary lower components but admits a
  bounded upward Oil entry from the same-frame component rows;
- same-component registered-motion continuation may extend an anchor-backed
  tail, while a motion/coverage/confidence break ends it;
- incompatible Oil components still require an UNKNOWN handoff and every
  numeric row retains same-frame provenance;
- detached compact Foam material requires registered temporal dynamics, while
  fixed bright structures remain unpublished;
- existing Artifact, completed-fill, no-interface and Foam independence tests
  remain passing;
- exact local replay, full regression, compile and `git diff --check` pass.

## Private Windows gate

Replay Base/Accum with the saved Recipes and Artifact templates. Report final
Oil/Foam publication separately from candidate presence. Required reviewed
checks are:

- Base retains the R14 real-interface runs and reduces anchor-backed gaps
  without reintroducing lower-rim or reflection components;
- Accum publishes no Oil during the reviewed initial EMPTY interval and admits
  the real bottom-entry rise;
- the 672--677 s dynamic Foam episode is not rejected by inverted Oil topology
  or unselected Oil proposals;
- later static Y=80 Foam prefixes remain unconfirmed unless registered material
  evolution independently supports them;
- detached/wall-droplet Foam recall is reported separately from layer Foam;
- CSV numeric values equal final sequence publication and retain same-frame
  provenance.

Coverage alone is not PASS.
