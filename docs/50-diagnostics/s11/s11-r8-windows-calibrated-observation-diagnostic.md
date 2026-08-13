# S11-R8 Windows Calibrated-Observation Diagnostic

## Scope and result

This document consolidates the secure-Windows R8 Base/Accum replay and the
follow-up exact-resolver investigation. It supersedes earlier coordinate and
candidate-nearness interpretations for these R8 bundles; it does not rewrite
the historical R7 evidence.

| Glass | numeric Oil | frames | coverage | dominant result |
|---|---:|---:|---:|---|
| Base | 0 | 601 | 0.0% | `UNKNOWN_REVIEW` 100% |
| Accum | 189 | 601 | 31.4% | Oil and Foam were not reliably separated |

R8 therefore failed the private field gate. Artifact calibration on/off was not
a meaningful Base comparison because neither run produced a public Oil frame.
Accum recovered much more Oil than R7, but part of the published path followed
the Foam front and the real Foam episode was suppressed.

## UI findings

The artifact proposal surface was discoverable through **분석 영역 편집**, but
the lower controls overlapped the video on the tested Windows layout. Selecting
a proposal gave no persistent highlight, so the operator could not reliably see
which source line/region was active. There was also no select-all plus explicit
bulk-apply workflow for a reviewed proposal set.

R9 must keep proposal application user-authorized while adding responsive
layout, selection highlight, multi-selection and an explicit bulk Artifact
action. Bulk selection is an editing convenience, not automatic truth; a real
Oil boundary can also be proposed and must not be accepted blindly.

## Base root cause and coordinate correction

The Recipe ellipse is source-frame geometry: center Y 597.71, radius Y 386.11,
top 211.60 and bottom 983.82. The R8 overlay images are also 1920×1080
source-frame images; they are not ROI-local crops. Direct overlay review and
exact debug timestamps give:

| event | time | reviewed source Y | near candidate within ±25 px | nearest candidate |
|---|---:|---:|---:|---:|
| descent | 539.998 s | 437 | none | 367 (70 px) |
| low | 634.008 s | 360 | 338 (22 px) | 338 |
| recovery/FULL | 674.007 s | 435 | none | 349 (86 px) |

The later `~660` values were detector candidates mistakenly relabeled as visual
truth. The earlier 366/580/327 review values likely came from a different R4
bundle. Neither set is valid R8 source-frame truth.

Base had 1,048 candidate-only and 3,747 continuation-eligible occurrences but
zero qualified anchors, zero final Oil and only two recurring tracks. The exact
540/634/674 analysis shows that artifact exclusion alone cannot solve Base:
the actual boundary is absent from the candidate lattice at two of three
reviewed points, and the one near candidate cannot form an anchor-backed run.
R9 therefore needs both calibrated candidate recall and a bounded bootstrap;
globally lowering thresholds would still allow the strong wrong rows to win.

## Accum Foam/Oil separation

Accum produced 241 qualified-anchor occurrences and 189 public Oil frames, but
the 672 s composition exposed a circular alias decision:

- final Oil Y was 448;
- raw real-Foam front Y was about 411, a 37 px separated layer;
- direct same-frame alias tolerance did not match those two rows; but
- `_episode_continues_oil_alias()` inherited a previously rejected alias track
  and suppressed the new Foam episode without current coincidence evidence.

Removing that Oil would reduce Oil coverage and allow roughly 7–15 Foam frames,
which confirms that Oil and Foam must remain independently publishable. A prior
alias rejection may be context, but cannot reject a later episode unless the
later episode again coincides with same-frame Oil evidence.

## Trace observability finding

`authority` was not removed from resolver logic. `debug_trace.jsonl` was written
before completed-window sequence resolution, so it contained current-frame
candidates and state but not final authority, cluster, trajectory, selection or
first reject stage. This forced unreliable source-code reconstruction and also
explains apparent contradictions between trace `selected=N` and public CSV.

R9 must preserve the raw record and append a compact final `sequence` section at
finalization. Each in-budget Oil candidate must expose initial/post-track/final
authority, cross-representation, semantic corridor, track opposition, cluster,
trajectory, selection and a summarized reject stage.

## R9 decision boundary

R9 remains one generic detector. Base and Accum are failure classes, not modes.
The accepted response is:

1. user-reviewed artifact geometry enables a bounded high-recall lane;
2. that lane cannot consume normal proposal capacity or corroborate an existing
   ordinary path;
3. dynamic bootstrap is allowed only when no qualified anchor path exists and
   requires a unique, moving, registered, Foam-separated multi-frame path;
4. a qualified existing path disables bootstrap entirely;
5. Foam alias continuation requires new same-frame coincidence evidence; and
6. raw samples and initial-state graph-hold semantics remain unchanged.
