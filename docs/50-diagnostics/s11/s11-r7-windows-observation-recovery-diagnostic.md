# S11-R7 Windows Observation-Recovery Diagnostic

## Scope and authority

This document consolidates the secure-Windows R7 Base/Accum investigation that
triggered R8. It is diagnostic evidence, not the current acceptance contract.
The trace contained 1,202 basic records, 601 per Glass, plus `tracking.csv`.

R7 field outcome was a failure:

| Glass | numeric Oil | sampled frames | public coverage | dominant state |
|---|---:|---:|---:|---|
| Base | 0 | 601 | 0.0% | `UNKNOWN_REVIEW` |
| Accum | 37 | 601 | 6.2% | `UNKNOWN_REVIEW` |

Direct review expected Base descent near 540 s, low near 634 s and recovery near
674 s. Accum began rising near 653 s, real Foam began near 672 s, reached its
high near 685 s and was first published only near 689 s.

## Foam findings

Single-frame Foam appearance could not distinguish the Glass artifacts:

| interval | real Foam | raw candidate | sequence eligible | strong evidence | public Foam |
|---|---:|---:|---:|---:|---:|
| Base 480–680 s | no | 264 | 0 | 127 | 0 |
| Accum 668–688 s | yes | 19 | 14 | 12 | 0 |

Base glare, scratches and haze had Foam score mean 0.817, whiteness 0.987 and
texture 0.933. Those static terms resembled real Foam. The useful separation
was temporal and geometric: registered internal/dynamic motion means were
0.047/0.049 for Base versus 0.947/0.947 for Accum; mean width/fill ratios were
0.317/0.195 versus 0.710/0.530.

The Accum resolver saw 19 raw, 14 eligible and 7 confirmed Foam frames across
two episodes. Confirmed timestamps were 670.5, 671.5, 673.0, 674.5, 676.0,
676.5 and 677.0 s. Before composition, three frames were `FULL_WITH_FOAM` and
four were `UNKNOWN_REVIEW`; none had R7 image-supported state. All seven were
dropped from public Foam. R8 must therefore preserve a confirmed Foam coordinate
when Oil/state is unavailable, while leaving the state `UNKNOWN_REVIEW`.

Conversely, local sample4 showed that a confirmed Foam track can be the same
material boundary as Oil. R8 consequently rejects an episode only when it
repeatedly coincides with a high-authority Oil boundary track; the raw candidate
and alias reason remain auditable.

## Oil candidate lattice

At every requested Windows checkpoint a candidate existed close to the reviewed
Oil boundary:

| Glass/time | candidate Y | reviewed Y | absolute error | R7 result |
|---|---:|---:|---:|---|
| Base 485 s | 344 | 327 | 17 | continuation, no trajectory |
| Base 540 s | 368 | 366 | 2 | continuation, no trajectory |
| Base 634 s | 592 | 580 | 12 | candidate only |
| Base 674 s | 349 | 327 | 22 | continuation, no trajectory |
| Accum 653 s | 532 | 552 | 20 | track opposition |
| Accum 672 s | 448 | 435 | 13 | candidate only |
| Accum 685 s | 192 | 192 | 0 | track opposition |
| Accum 689 s | 196 | 191 | 5 | accepted anchor |

All Base frames had Oil candidates but no numeric publication. Across candidate
occurrences, Base had 1,517 candidate-only, 3,257 continuation and six anchor
entries, but zero qualified-anchor frames, zero trajectory frames and zero
numeric frames. Five of the six sparse anchors were visually wrong and the
remaining one unclear; none formed a cluster.

In Base 530–680 s, a reviewed-boundary-near candidate existed on only 100/299
frames: ordinary only 39, material-path only 27 and both 34. The remaining 199
frames lacked a near-boundary representation. Of 165 near ordinary candidates,
95 failed material support, 96 failed boundary likelihood and 38 failed
horizontal coverage; none failed artifact, ambiguity, optics, texture or
topology gates. Semantic entry was 0/108, so no triple was attempted. This is a
representation/continuity problem, not a global threshold problem.

## Counterfactuals and corrections

Neutralizing only `material_texture_conflict` left Base at zero but changed
Accum numeric frames from 37 to 136, trajectory frames from 38 to 170 and
qualified-anchor occurrences from 86 to 251. Accum 685 s became accepted. This
proves Foam-derived texture must not veto otherwise independent Oil evidence.

Neutralizing topology as well reduced Accum to 128 numeric frames and 157
trajectory frames. Topology is therefore not globally disabled in R8.

Allowing a dynamic material path with registered Oil motion and coverage to
fall through the no-semantic-corridor branch changed Accum from 136 to 181
numeric frames without changing Base. Newly numeric candidates had no
`artifact_signature > 0.46` and only one had `boundary < 0.18`.

At Accum 672 s, the best path selected `Y=448`, emission 0.891, Oil confidence
0.8332 and trajectory 1.0, but the fixed two-frame pre-anchor edge cut it from
the final run. R8 uses a bounded dynamic horizon instead of a fixed edge.

Corrected bookkeeping:

- B-only was 14 frames, not 144: track opposition 10, qualified-anchor loss 1,
  trajectory-component loss 3.
- qualified-anchor 251 counted occurrences; 148 counted frames after cluster
  support. They are different stages.
- the D counterfactual exactly matched B; its earlier claimed 672 s recovery was
  a post-hoc ref manipulation and is not evidence.

## R8 decision boundary

R8 uses one generic detector for both Glasses. It does not branch on Base,
Accum, time or video identity. It adds bounded representation, removes the
Foam-texture Oil veto, preserves confirmed independent Foam, bounds dynamic
continuation and provides explicit user artifact calibration. It does not lower
all thresholds, interpolate missing Oil or let an initial state create numeric
Oil.

