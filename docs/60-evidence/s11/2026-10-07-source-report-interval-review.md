# Source/report interval review — prepared 2026-10-07

## Scope and disposition

Work Plan step 3, following report commits `6f7c309` and `31f51c5`.
The first sample4 human interpretation has returned (see below). The consequential
distortion is selected: incorrect Oil boundary tracking across the displayed
40–44-second transition, with correct observations to preserve. No detector
mechanism is selected or accepted, canonical truth is unchanged, and FIELD FAIL remains.
The user's current authorization says to proceed sequentially until their judgment
is required. This first checkpoint is answered; event compatibility and A1 follow it.

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

## Human reply received — 2026-10-07

The user states that only 42.5 seconds / f1275 correctly tracks actual Oil within
40–44 seconds. They additionally confirm 38 seconds / f1140, 49.5 seconds / f1485
and 52 seconds / f1560 as correctly tracking the actual surface.

| Source frame / time | Stored Oil height | User assessment |
|---|---:|---|
| f1140 / 38 s | +6 px | Correct |
| f1200 / 40 s | −15.5 px | Incorrect under the interval statement |
| f1260 / 42 s | −18 px | Incorrect under the interval statement |
| f1275 / 42.5 s | +15 px | Correct |
| f1320 / 44 s | +28 px | Incorrect under the interval statement |
| f1485 / 49.5 s | +14 px | Correct |
| f1560 / 52 s | +17 px | Correct |

The [verbatim reply and exact-frame joins](2026-10-07-sample4-interval-human-reply.json)
retain original source/result/image pins. The broad interval statement is kept as
stated; machine frame assessments cover only the displayed observations above,
not unseen intermediate frames. No exact replacement y, material type of the
wrong boundary, Foam truth, pixel tolerance or total error duration is inferred.
f1185/f1605/f1680 and sample3 receive no new labels.

This is enough to select a meaningful local detector target: remove the wrong Oil
boundary observations in the 40–44-second transition while preserving the four
confirmed correct observations. The report's low-to-high sequence cannot be
accepted as verified physical Oil recovery. The upstream first harmful stage is
still unknown and belongs to A1 lineage tracing, followed by a bounded A2
hypothesis. Event namespace compatibility remains the next separate Work Plan
unit; additional events from these values are not new physical evidence.

## Detector Governance

- Logic-map nodes: `RESULT-PRESENTATION`, `PUBLICATION-PROVENANCE`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: UNRESOLVED — report display repairs are complete at their bounded contract; the user confirms incorrect Oil tracking in the selected interval, but upstream first loss is not yet traced.
- Logic-map impact: NONE — read-only decoding of existing outputs and source.
- Failure-registry impact: NONE — no detector mechanism changed or failure retired.
