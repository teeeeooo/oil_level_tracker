# S11-R13 Phase-Identity Recovery Validation

## Gate status

**Status:** local PASS; exact-head private-Windows Base/Accum replay pending.

Local PASS authorizes another private-Windows Base/Accum replay. It does not
close S11.

The local result is recorded in
[S11-R13 phase-identity recovery evidence](../60-evidence/s11/s11-r13-phase-identity-recovery.md).

## Structural replacement gate

Source inspection and tests must prove:

- ordinary semantic candidates cannot bypass typed material conflict;
- the R12 semantic direct-anchor and versioned lower-reserve policies no longer
  own authority;
- one phase identity is reused by authority, trajectory and recurrence policy;
- calibrated diffuse proposals remain proposal/continuation-only until they
  independently satisfy that identity;
- active basic-trace fields use stable semantic names and expose path stages;
- obsolete no-reader versioned aliases are absent; and
- old bundle reading/public stored compatibility remains intact.

No field-video identifier, timestamp or truth coordinate is allowed in source.

## Base proposal and authority gates

Controlled raster tests must cover:

1. a diffuse horizontally distributed phase transition produces a bounded
   proposal without requiring a strict local maximum;
2. a flat row, narrow scratch, glare-only band and calibrated Artifact do not
   produce an authoritative interface;
3. proposal count and minimum spacing remain bounded;
4. motion/persistence without direct phase identity remains non-numeric; and
5. a real phase row can anchor continuations only through the shared typed
   identity.

Private Base reporting remains source-coordinate based at 540, 634 and 674 s.
Report proposal recall within 25 and 80 px separately from numeric coverage,
plus the longest wrong and missing runs. The former Y724–873 path must remain
absent.

## Accum composition and authority gates

Controlled sequence tests must prove:

- a weak, ambiguous, high-conflict ordinary semantic triple cannot anchor;
- a later high-boundary residue continuation cannot publish without a valid
  anchor component;
- a strong lower Oil boundary below an active Foam/material front can establish
  `ORDERED_LOWER_INTERFACE` even when the broad mask overlaps it;
- geometric lower separation without direct/corroborated phase evidence is not
  authority;
- recurring upper material cannot demote an independently identified lower Oil
  merely because the upper track is longer; and
- opposed Foam/residue and lower Oil cannot exchange trajectory support.

Private Accum reports exact numeric distribution, Y190–297 residue count,
Y425–475 reviewed-lower count, authority-reason distribution and longest runs.
At 672, 684 and 689 s, report near-truth candidate identity, authority,
opposition, path-stage result and final selection.

## Foam and graph gates

- The 650–700 s Foam funnel reports raw, eligible, confirmed, public and
  `foam_is_valid` counts.
- Confirmed Foam remains graphable when Oil/state is unresolved.
- Invalid finite Oil is not plotted.
- Invalid finite Foam is not plotted.
- Valid points on one series are unaffected by invalidity of the other.
- Initial-state hold remains visible as a disclosed band when numeric Oil is
  absent.

CSV values remain available for debug even when plotting filters them.

## Trace gate

For every selected and near-truth candidate, basic trace records stable fields
for evidence availability, phase identity, authority, cluster/trajectory,
Artifact match and final selection. Frame state records node kind/Y after:

1. best path;
2. continuation-run bound;
3. trajectory-spike suppression; and
4. completed-fill reacquisition suppression.

The first Oil-to-unknown stage must be directly observable without replay-time
monkey patching or source-code inference.

## Replay, regression and runtime gate

Run focused proposal/identity/trajectory/graph tests, four checked-in videos,
user-like Artifact replay, provenance checks, performance comparison and the
full suite.

```bash
.venv/bin/python -m tests.diagnostics.s11_r13_phase_identity_replay
.venv/bin/python -m tests.diagnostics.s11_r13_artifact_calibration_replay
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q src tests
git diff --check
```

Record numeric counts, checked-truth error, independent Foam counts, exact
same-frame provenance and R12/R13 same-session detector/resolver time. Coverage
alone is never PASS.

## Local gate result

- four-video replay: 299 rows / 121 numeric Oil;
- checked truth: 9/13 numeric, 5.28 px MAE, 11 px maximum error;
- same-frame provenance: PASS;
- sample3 completed-fill internal-material interval: zero numeric Oil;
- Artifact replay: 97/113 numeric Oil, zero Foam, complete provenance;
- direct runtime: 69.5 ms/frame versus documented R12 72.6 ms/frame; and
- repository regression: 1,537 passed.

The private Windows gates above remain open and are the only current execution
gate.
