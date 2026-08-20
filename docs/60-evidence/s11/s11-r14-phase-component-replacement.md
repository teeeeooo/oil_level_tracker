# S11-R14 Phase-Component Replacement Evidence

## Disposition

R14 is implemented and passed the local architecture, exact replay,
same-frame provenance, completed-fill/drain, Artifact-editor and runtime gates.
This authorizes private Windows Base/Accum replay of the exact pushed head. It
does not establish private-field accuracy or close S11.

## Replacement result

Artifact templates remain candidate-local rejection data but no longer enable
or resize high-recall generators. The bounded calibrated and phase-transition
proposal lanes run independently of template count. Calibrated direct identity
requires cross-representation support; recurrence alone cannot demote a clean
direct row.

Trajectory, Viterbi transitions and continuation bounds now share explicit
component ownership. An Oil-to-Oil transition cannot cross components. A recent
direct Foam seed may identify the first independently supported lower interface
for at most three seconds; stale Foam/residue continuation only opposes Oil.
The nearest plausible lower interface alone may anchor. Completed-fill
reopening requires upper-Glass entry plus coherent downward progress, preventing
an internal moving cap from releasing the barrier.

Debug trace exposes effective track opposition, component identity and the
best-path, continuation-bound, spike-suppressed and completed-fill stage result.
Every numeric Oil remains one equal-Y selected candidate from the same frame.

## Confirmed Artifact editing

The analysis-area editor now supports Shift range selection, Ctrl/Cmd toggle,
select-all, clear-selection and bulk deletion for confirmed templates. Every
selected template is highlighted on the video overlay. The editor still mutates
only its private Recipe copy until Apply, and existing Recipe persistence owns
the final saved template list.

## Exact four-video replay

The isolated replay processed 299 rows:

| sample | rows | numeric Oil |
|---|---:|---:|
| base_sample_1 | 30 | 30 |
| sample2 | 5 | 3 |
| sample3 | 151 | 43 |
| sample4 | 113 | 111 |
| total | 299 | 187 |

All 187 numeric rows have equal-Y selected same-frame provenance. Combined
checked truth is 10/13 numeric with 8.5 px MAE and 26 px maximum error. The
sample3 completed-fill internal-material interval has zero numeric Oil; its late
drain has 18 numeric rows. Sample4 has eight strict reviewed-range matches.

The runner is `tests/diagnostics/s11_r14_phase_component_replay.py`; the local
manifest used for closeout was
`/tmp/s11-r14-phase-component-final/replay_manifest.json`. Accepted tracking
fingerprints are:

- base_sample_1: `0a68c47d131ec3c0414d78c3dd8e61422ab484ba403c7320d4af0e28bd496a34`;
- sample2: `834c323e96c1df35f9ff17f746510c99dfece43b10cd015d15206a6d11b97b07`;
- sample3: `c2fe7b1eb3de3ad5b169f61ba06c9ebcc7aec016c6e6a082f3517ca3d517d4c9`;
  and
- sample4: `4e654710c728e504fe81bec647d617b2b13f6fbe2b311d614f2e0345e7501e8c`.

## Runtime gate

Three direct runs over the same decoded 113 sample4 frames included official
three-frame static learning and excluded video seek, report and debug output.

| head | detector median | resolver median | total median | mean/frame |
|---|---:|---:|---:|---:|
| R13 documented reference | 7.106 s | 0.753 s | 7.859 s | 69.5 ms |
| R14 implementation | 8.907 s | 2.033 s | 10.940 s | 96.8 ms |

R14 is slower than R13 but remains below the predeclared 104.25 ms/frame gate.
The additional cost is observable and remains a Windows validation item; this
local comparison is not a Windows wall-clock claim.

## Repository gate

- exact four-video replay: passed with fixed counts and fingerprints;
- focused phase/component, publication and Artifact-editor regressions: passed;
- historical coordinate thresholds were updated to the current checked-video
  26 px contract without weakening same-frame, fill-barrier or drain behavior;
- full repository regression: 1,542 passed in 161.25 s;
- Python compile: passed; and
- `git diff --check`: passed before closeout.

## Remaining Windows gate

Replay the exact pushed R14 head with the saved Base/Accum Artifact templates.
Record detector/resolver version, final-publication integrity, reviewed-row
proposal recall, phase and component identity, effective opposition and every
path-stage result. For Foam, report raw, eligible, confirmed, public and
`foam_is_valid` independently from Oil and legacy overall validity.

The known rim/bracket, broad material/residue and upper residue components must
not form a published Oil run. If a reviewed Oil row has no proposal, report a
generation failure rather than weakening authority globally.
