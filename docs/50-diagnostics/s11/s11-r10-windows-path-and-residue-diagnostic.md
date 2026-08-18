# S11-R10 Secure-Windows Path and Residue Diagnostic

## Scope and authority

This record preserves operator-transferred evidence from the exact R10
secure-Windows Base/Accum replay after reviewed Artifact calibration. The
private videos are unavailable in this repository, so the counts are diagnostic
input rather than a locally reproduced PASS.

R10 increased coverage but failed physical-interface accuracy. Base selected a
calibrated lower-structure path for the complete window, while Accum selected a
Foam/residue material path instead of the clearly visible lower Oil interface.

## Base calibrated bootstrap failure

Base published one wrong run from 480.0 through 777.5 s: 583/583 visually
incorrect frames with Y 673–937 while reviewed Oil was approximately Y
360–465. Selected source was `r9_calibrated_high_recall` on 567 frames.

The resolver marked all 567 rows as calibrated path members and anchors, but
only two were registered-motion keyframes:

| time | Y | motion support | motion coverage |
|---:|---:|---:|---:|
| 750.0 s | 845 | 0.571 | 0.600 |
| 774.0 s | 734 | 0.780 | 0.600 |

Those late keyframes retroactively promoted the path back to 480 s and forward
through the whole sequence. Average selected motion support/coverage was only
0.036/0.067. At 539.5 and 673.5 s no candidate existed within ±25 px of the
reviewed Oil; at 633.5 s a candidate 16 px away remained continuation-only with
no trajectory support. Bootstrap therefore converted candidate continuity into
authority without locally bounded motion evidence and could not repair the
separate candidate-recall deficit.

The frame flag `R8_CALIBRATED_ARTIFACT_REJECTED` appeared throughout, but the
selected wrong rows had `calibrated_artifact_match=0`. The flag means some
candidate in the frame matched a template, not that the selected row did.

## Accum Foam/residue reuse failure

Source-frame overlays at 684 and 689 s establish the actual Oil interface near
Y450. Public Oil at Y205/191 was a dry or diffuse Foam/residue/meniscus stain.
The earlier interpretation of Y191–230 as actual Oil was therefore incorrect.

At 677 s the confirmed Foam front was Y218 and selected Oil was an
`r6_material_path` row at Y235. R10 treated the positive 17 px separation as a
thin independent layer, even though both rows belonged to the same Foam
material. After public Foam disappeared, the same upper material track remained
anchor/trajectory-supported through the wrong Y191–297 interval.

The wrong run from 677.5 through 726.5 s contains 97 frames. It did not use the
R10 calibrated bootstrap. It used ordinary material-path authority with mean
registered motion/coverage near 0.91/0.91. High motion described moving
Foam/residue, not Oil identity.

Candidate-specific material texture conflict was high on representative wrong
rows (0.797 at 677 s, 0.750 at 689 s and 0.646 at 709.5 s), but current
authority does not consult that opposition. A wrong row at 684 s had conflict
zero after the Foam raster disappeared, proving that a current-frame-only gate
cannot close the complete residue track.

Actual-Oil-near candidates were often present but pruned before authority:

| time | candidate Y | error | source | rank / stop |
|---:|---:|---:|---|---|
| 670.0 s | 451 | 1 | r6 material path | 13 / top-k |
| 675.5 s | 466 | 16 | calibrated high recall | 22 / top-k |
| 677.0 s | 450 | 0 | oil hypothesis | 29 / top-k |
| 684.0 s | 454 | 4 | calibrated high recall | 24 / top-k |
| 689.0 s | 474 | 24 | calibrated high recall | 23 / top-k |
| 726.0 s | 458 | 8 | r6 material path | continuation / no trajectory |

## Structural cause

The active detector stacks D-era current-frame evidence, five additive
candidate families, compatibility tracking and the R6–R10 completed-window
resolver. `OpenCvPhaseDetector.detect()` and `OilObservationResolver` have
accumulated orchestration, authority, bootstrap, trajectory and projection
responsibilities. Version-prefixed dictionary fields act as internal interfaces,
and one candidate may reach anchor authority through multiple ordered Boolean
branches without an explicit authority reason.

R11 must therefore follow a behavior-preserving detector architecture reset.
Adding another local veto to the existing Boolean forest is not sufficient.

