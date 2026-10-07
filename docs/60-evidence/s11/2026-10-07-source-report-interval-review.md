# Source/report interval review — prepared 2026-10-07

## Scope and disposition

Work Plan step 3, following report commits `6f7c309` and `31f51c5`.
Source/report comparison is prepared; human interpretation is PENDING. No detector
hypothesis is selected or accepted, no truth is edited, and FIELD FAIL remains.
The user's current authorization says to proceed sequentially until their judgment
is required. This is that checkpoint; event compatibility and A1 follow it.

The review targets were selected from the third audit before decoding: sample4's
late transition (38–44 seconds) and later Oil/Foam observation (49.5–56), plus
sample3's longest Oil gap (34.5345–81.0143) and reobserved descent through 100.0333.
A consequential distortion means changing the perceived direction/transition
order, sustaining another boundary as Oil, or treating missing Foam coordinates
as physical disappearance. No point-count or MAE acceptance threshold is added.

## Established observations and unresolved interpretation

| Interval | Stored result / source observation | Interpretation status |
|---|---|---|
| sample4 38–44 s | Oil +6 px at 38, −15.5 at 40, −18 at 42, +15 at 42.5, +28 at 44. Foam has separate values. At 40/42 the green line lies low in the image; at 44 it lies in the upper textured region. | The 42→42.5 step is +33 px in 0.5 s. Boundary identity, actual Oil movement and visibility need human interpretation; do not call this verified recovery. |
| sample4 49.5–56 s | Oil absent 50–51.5; Foam coordinates remain available. Oil returns at 52. Foam has no coordinates at 53.5/56; bright textured source regions remain. | Separate non-observation from physical absence. The latter is not established. |
| sample3 34.5345–81.0143 s | Two stored Oil anchors separated by 46.4798 s. Midpoint source at 57.7911 s shows different appearance; no Oil/Foam guide is drawn there. | The interior trajectory and material identities are unresolved. Static report now leaves this connection open. |
| sample3 81.0143–100.0333 s | Stored heights fall overall from +82 to −53 px, with intermittent gaps and small reversals; selected source crops show a descending visible boundary. | Direction is a qualitative reviewer observation, not a same-boundary truth label or per-frame accuracy result. |

The first human question is whether sample4's 40–44 second Oil transition is real
movement, selection of another boundary, or not determinable. If incorrect, a
qualitative description of where the Oil and Foam boundaries lie is sufficient;
no exhaustive labeling or exact pixel coordinate is requested. Prior C1 rim / C2
Foam and earlier candidate correspondence remain scoped to their original frames.
They do not establish identities here. Human-ROI experiments remain unadopted.

## Review material and reproducibility

Local `sample/output/s11-context-review-20261007-001/review.html` links existing
baseline and final static reports (same stored tracking) and presents sixteen
source/observation pairs: ten sample4 frames, six sample3 frames. Each pair has a
raw left panel and stored-coordinate right panel. The sole gap-midpoint panel is
source-only. The page requests report A/B interpretation before source inspection;
no user comprehension benefit is claimed before a reply.

Original videos remain `sample/sample4.mp4` (38–56 s) and `sample/sample3.mp4`
(30.03–105 s). Static HTML and image layout were inspected in a local browser.
Embedded browser video playback was not qualified and is not provided as evidence;
continuous motion should be checked in the original local video. Exact source
frames were decoded locally and the post-read frame position was verified.

The [manifest](2026-10-07-source-report-review-manifest.json) pins source head,
video/recipe/result hashes, exact frame and source time, crop bounds, each stored
row and image hash, the builder and HTML. Full-resolution private source and
images remain local; the original source pins match the four-video verification
receipt. `sample4-focus.png` provides the 40/42/44-second comparison for the reply.

## Detector Governance

- Logic-map nodes: `RESULT-PRESENTATION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: UNRESOLVED — report display repairs are complete at their bounded contract; the selected interval needs physical identity interpretation before a detector first-loss claim.
- Logic-map impact: NONE — read-only decoding of existing outputs and source.
- Failure-registry impact: NONE — no detector mechanism changed or failure retired.
