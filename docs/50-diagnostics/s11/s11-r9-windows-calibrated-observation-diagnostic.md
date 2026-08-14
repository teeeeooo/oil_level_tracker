# S11-R9 Secure-Windows Calibrated Observation Diagnostic

## Scope and identity

This record captures the private secure-Windows Base/Accum replay of the exact
R9 calibrated-observation implementation. Detector and sequence resolver
reported the R9 calibrated-observation v1 identities, and the reviewed Recipe
contained user-applied detector Artifact templates. Non-zero
`r8_calibrated_artifact_rejected_count` established that calibration was
actually applied even though the raw trace did not serialize the template
count directly.

The private videos are unavailable in the repository. Counts below are
operator-transferred evidence and must not be presented as a locally reproduced
PASS.

## Result

R9 failed the private field gate:

- Base remained 0/601 numeric Oil after reviewed Artifact calibration.
- Accum Oil coverage remained materially equivalent to R8 and real Foam was
  not visibly retained in the graph.
- The analysis-area editor no longer overlapped video, but its vertically
  stacked Artifact controls were hidden below a scroll fold at first open.

## Base candidate and resolver funnel

Reviewed source-frame Oil positions were 437 px at 540 s, 360 px at 634 s and
435 px at 674 s.

| time | nearest R9 candidate | error | initial/final authority | first stop |
|---:|---:|---:|---|---|
| 540 s | 391 px | 46 px | continuation / continuation | no trajectory support |
| 634 s | 376 px | 16 px | continuation / continuation | no trajectory support |
| 674 s | 351 px | 84 px | none | top-k pruned or hard-invalid |

At 634 s, calibrated rows at 376, 384 and 392 px had boundary likelihood
0.411–0.518, zero or negligible artifact likelihood and full visibility. The
376 and 384 px rows were continuation-eligible but had zero cluster,
trajectory, cross-representation and calibrated-seed support.

The complete resolver funnel was:

| stage | count |
|---|---:|
| initial continuation-eligible | 5,221 |
| post-track continuation-eligible | 5,002 |
| registered-motion support pass | 4,994 |
| per-candidate motion-coverage pass | 288 |
| Foam/artifact pass | 288 |
| ambiguity pass | 171 |
| locally corroborated rows | 27 |
| six-frame calibrated path | 0 |
| calibrated dynamic seed/run | 0 |

All 5,002 final continuation candidates stopped at
`NO_TRAJECTORY_SUPPORT`. Eight anchor-eligible occurrences stopped at
`NO_CLUSTER_SUPPORT`. The earlier shorthand `NO_CONTINUATION` was therefore
incorrect: continuation authority was abundant, but the bootstrap admitted no
complete trajectory.

The principal collapse was the requirement for high candidate-local registered
motion coverage on every path member. Slow Oil movement and intermittent local
motion support fragmented the remaining 171 candidates before a six-frame path
could form. Artifact calibration enabled the R9 bootstrap but did not relax
this incompatible evidence shape. Candidate recall was also incomplete at two
of the three reviewed checkpoints, so a resolver-only threshold change cannot
recover Base safely.

## Accum Foam publication and graph visibility

The Foam episode resolver confirmed five frames at 670.5, 671.5, 673.0, 674.5
and 676.0 s. All five were preserved in `tracking.csv` as finite
`raw_foam_front_y`, even though Oil/state remained unresolved and whole-sample
`is_valid` was false. Thus R9 did not erase confirmed Foam downstream.

The user-facing graph appeared empty because the five values were isolated by
missing samples and Foam was rendered as a line without point markers. A
line-only plot has no visible segment for an isolated observation. Whole-sample
validity must remain a review signal, not a reason to hide independently
confirmed Foam.

Six other raw sequence Foam candidates were not public: four were unconfirmed
and two at 676.5/677.0 s were rejected as Oil aliases. The rejected pairs were:

| time | Foam Y | selected Oil Y | separation |
|---:|---:|---:|---:|
| 676.5 s | 219 px | 236 px | 17 px |
| 677.0 s | 218 px | 235 px | 17 px |

The Oil rows were selected, anchor-eligible and public. Alias tolerance was not
10 px: the implementation used
`max(10 px, temporal_max_jump_px * 0.65)`. It therefore classified a legitimate
17 px Oil/Foam layer separation as the same boundary. Temporal Oil jump
tolerance is not a valid Foam/Oil identity tolerance.

## UI reproduction

The current dialog was rendered locally at both supported initial sizes. At
980×700 the vertical settings viewport was 210 px; at 1200×840 it was 236 px.
Both showed the Artifact explanation and two empty lists while hiding
**Detector 후보 찾기**, bulk-selection actions and status below the scroll fold.
The first-view information hierarchy therefore failed even without video
overlap.

## Root cause and successor boundary

R10 must address three independent owners:

1. calibrated candidate generation/retention must improve vertical recall
   without consuming ordinary proposal authority;
2. bootstrap must evaluate sparse motion keyframes and long-horizon path motion
   instead of requiring high local coverage on every member; and
3. Foam alias identity, Foam graph visibility and Artifact editor
   discoverability must be independent of Oil temporal jump and whole-sample
   validity.

Global threshold lowering, Glass/time branches, automatic Artifact acceptance,
numeric interpolation and Foam-created Oil authority remain prohibited.
