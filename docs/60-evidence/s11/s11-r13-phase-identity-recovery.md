# S11-R13 Phase-Identity Recovery Evidence

## Disposition

R13 is implemented and passed the local architecture, checked-video replay,
Artifact workflow, provenance, runtime and repository gates. This authorizes
replay of the exact pushed head on the private Windows Base/Accum videos. It
does not establish private-field accuracy or close S11.

R13 is a replacement of the remaining R12 authority leak, not another
versioned threshold layer. New Oil authority is owned by a shared typed phase
identity. Stale semantic-direct, terminal-fallback, track-promotion and
duplicate registered-dynamic authority paths were removed.

## Structural and implementation result

The final implementation introduces `DIRECT_INTERFACE`,
`ORDERED_LOWER_INTERFACE`, `CONTINUATION_ONLY` and `OPPOSED_MATERIAL` identities
before authority and trajectory decisions. Candidate family names no longer
grant authority. High material-texture conflict blocks an ordinary candidate
from anchoring; the ordered-lower exception requires an active upper material
front plus independent lower-boundary corroboration.

The calibrated high-recall lane now proposes bounded multi-scale diffuse phase
transitions when user Artifact calibration is present. Those proposals remain
continuation-only until the shared identity contract is met. A completed-fill
barrier suppresses lower internal material caps immediately; drain reopening
requires an observed gap and confirmed downward reacquisition. Short-window
recovery is bounded to at most three seconds or six frames and cannot authorize
long anchor-free paths.

Result Review now masks Oil and Foam by their own validity bit. Finite invalid
debug coordinates remain in CSV but cannot become plotted points. Active Foam
diagnostics use stable semantic names; public versioned flags and old evidence
input aliases remain only where stored-result compatibility has readers.

A file-level audit found every module under `adapters/vision` referenced by
production or tests, so no whole module was deleted speculatively. The cleanup
instead removed confirmed stale control paths and no-reader diagnostic aliases.

## Checked-video replay

The isolated four-video replay processed 299 rows:

| sample | rows | numeric Oil |
|---|---:|---:|
| base_sample_1 | 30 | 6 |
| sample2 | 5 | 5 |
| sample3 | 151 | 32 |
| sample4 | 113 | 78 |
| total | 299 | 121 |

All 121 numeric Oil rows have an equal-Y selected same-frame candidate. Combined
checked user truth is 9/13 numeric with 5.28 px mean absolute error and 11 px
maximum error. The sample3 completed-fill internal-material interval has zero
numeric Oil, and sample4 has seven strict reviewed-range matches. This is a
local regression result, not evidence for the private Base/Accum videos.

The runner is `tests/diagnostics/s11_r13_phase_identity_replay.py`; its manifest
is `sample/output/s11-r13-phase-identity/replay_manifest.json`. Accepted
fingerprints are:

- base_sample_1: `9be36db34d83253bd6b5c0c2f94191103c3f38abc353e008a9d561b2078ce43c`;
- sample2: `9b2aa706a631482d5e5893822c6193e2120878878490279b282e70c94cfb262a`;
- sample3: `76e42925c2dec1e80ef133fc4f52b9ecf55df6f376fbf761e6e00f80758fe0ba`;
  and
- sample4: `6bbcea601b01d0eae7d26f54b2b5e850e21bb6598cccb1c828c3fcd0b69747e1`.

## User-like Artifact replay

The sample4 workflow selected detector proposal zero and created a normalized
line template centered at `(0.5192, 0.8269)`. Reanalysis increased numeric Oil
from the uncalibrated R13 reference 78/113 to 97/113, with zero Foam and complete
same-frame provenance. Checked truth is 2/5 numeric with 0.5 px MAE/maximum
error; nine reviewed visible points fall inside the strict range.

Calibration removes matching geometry only. It does not grant authority to an
unmatched diffuse row, and a high-conflict phase-scan proposal cannot use the
ordered-lower exception. The runner is
`tests/diagnostics/s11_r13_artifact_calibration_replay.py`; its manifest is
`sample/output/s11-r13-artifact-calibration/artifact_calibration_manifest.json`
with fingerprint
`ef66e7980008545537d2d963ed86b5f11ff9ad1e20e1ea4e99eedbe7b7c7e75a`.

## Runtime gate

Three direct runs over the same decoded 113 sample4 frames included official
three-frame static learning and excluded video seek, report and debug output.

| head | detector median | resolver median | total median | mean/frame |
|---|---:|---:|---:|---:|
| R12 documented reference | 7.107 s | 1.085 s | 8.203 s | 72.6 ms |
| R13 implementation | 7.106 s | 0.753 s | 7.859 s | 69.5 ms |

R13 total time is about 4.2% lower than the documented R12 result on the same
machine and workload definition. The detector is effectively unchanged while
the replacement resolver is lower. This is a bounded local comparison, not a
claim about Windows wall-clock performance.

## Repository gate

- exact four-video replay: passed with fixed counts and fingerprints;
- exact user-like Artifact replay: passed;
- full repository regression: 1,537 passed in 116.68 s;
- Python compile: passed; and
- `git diff --check`: passed before closeout.

## Remaining Windows gate

Replay the exact pushed R13 head with the saved Base/Accum Artifact templates.
The trace must report the R13 detector and resolver versions.

For Base, report proposal recall within 25 and 80 px at 540, 634 and 674 s,
numeric coverage, qualified identity/anchor counts, and longest missing/wrong
runs. The former Y724–873 reflection/bracket path must remain absent.

For Accum, report the 650–700 s Foam funnel independently from Oil, the number
of Oil rows in the known residue band Y190–297, and reviewed-lower selection in
Y425–475. At 672, 684 and 689 s, include phase identity, authority, opposition,
path-stage mutation and final selection for the nearest reviewed lower row.
Coverage alone is not PASS.
