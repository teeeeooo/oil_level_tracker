# S11-R15 State-Aware Material Ownership Evidence

## Disposition

R15 is implemented and passed the local replacement, exact replay,
same-frame provenance and full-regression gates. This authorizes private
Windows Base/Accum replay of the exact pushed head. It does not establish
private-field accuracy or close S11.

The validated runtime identity is:

- detector: `opencv-phase-detector-r15-state-aware-material-ownership-v1`;
- sequence resolver: `r15-state-aware-material-ownership-v1`; and
- local validation runtime head: `45a7632` (later documentation-only commits
  do not change runtime behavior).

## Replacement result

Foam/Oil ownership now uses only final resolved Oil for same-boundary aliasing.
The comparison is symmetric; a large negative separation is inverted topology,
not alias. Candidate-only Oil veto and prior-alias continuation state were
removed. Debug output reports the final material relation, matched Oil Y,
signed layer separation and Foam-specific rejection stages.

Confirmed initial EMPTY now admits Oil only after a lower-entry component shows
bounded upward progress across same-frame observations. A stationary lower
structure remains provisional. Anchor-backed continuation no longer uses a
fixed frame horizon: it extends only through an unbroken same-component path
with trajectory, registered motion, coverage and confidence.

Foam component classification now has one detached-material phenotype owner.
It distinguishes detached layers from compact detached droplets. A filled
bright droplet that the optics mask covers can be recovered inside the Foam
detector, but it becomes sequence-eligible only with registered internal and
adjacent dynamics. The shared Oil optics mask was deliberately left unchanged
after integration testing proved that changing it removed legitimate Oil
anchors.

## Exact four-video replay

`tests/diagnostics/s11_r15_material_ownership_replay.py` passed with fingerprint
checking enabled. The common process-isolated orchestration was extracted to
`tests/diagnostics/s11_isolated_replay.py`; the historical R14 runner now uses
the same owner instead of retaining a duplicate process/audit implementation.

| sample | rows | numeric Oil | Foam episodes | tracking fingerprint |
|---|---:|---:|---:|---|
| base_sample_1 | 30 | 30 | 0 | `0a68c47d...496a34` |
| sample2 | 5 | 3 | 0 | `834c323e...97b07` |
| sample3 | 151 | 43 | 2 | `c2fe7b1e...17d4c9` |
| sample4 | 113 | 111 | 2 | `2da3ba6c...28bfe2` |
| total | 299 | 187 | 4 | — |

All 187 numeric Oil rows retain equal-Y selected same-frame provenance. Final
numeric Oil is counted only when final resolved kind is Oil and final source Y
is finite; an intermediate candidate `selected` bit is not publication.

Combined checked truth is 10/13 numeric with 8.1 px mean absolute error and
24.5 px maximum error. Sample3's completed-fill internal-material interval has
zero numeric Oil, its late drain has 18 numeric rows, and sample4 has eight
strict reviewed-range matches. The final fingerprint-checked manifest is
`/private/tmp/s11-r15-final-verified/replay_manifest.json`; it was generated
after the shared-optics isolation fix and reproduced the accepted counts and
fingerprints.

## Automated validation

- Foam alias/independence, Oil continuation/EMPTY admission, debug trace and
  current detector contracts: 417 passed;
- Foam evidence, temporal, optics and detached-droplet focused regressions:
  69 passed before shared-optics isolation, followed by nine focused
  integration checks after isolation;
- full repository regression: 1,549 passed in 161.70 s;
- Python compile: passed;
- `git diff --check`: passed.

The first full run exposed one integration failure: a shared glare-mask change
removed Oil anchors from the reporting fixture. Commit `45a7632` restores the
shared optics contract and keeps droplet recovery under Foam ownership. The
failed report path and focused droplet/optics paths then passed, followed by the
clean full-regression result above.

## Remaining private Windows gate

Replay the exact pushed R15 head with the saved Base/Accum Recipes and Artifact
templates. Report Base Oil gaps, Accum initial-EMPTY false publication, real
bottom-entry admission, the 656.5--677 s dynamic Foam group, later static Y80
prefixes and detached/wall-droplet Foam separately. CSV values must equal final
sequence publication and retain same-frame provenance. Coverage alone is not
PASS.
