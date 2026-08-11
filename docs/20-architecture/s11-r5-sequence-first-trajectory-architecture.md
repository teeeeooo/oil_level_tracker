# S11-R5 Sequence-First Observation Architecture

**Status:** `LOCAL_ACCEPTED — SECURE WINDOWS REQUIRED`

## Purpose

R5 changes the authority used for a completed video analysis. The report must describe the physically plausible Oil-level and Foam history that can be supported by the video, rather than expose a disconnected collection of current-frame decisions.

R5 does not lower global thresholds and does not synthesize a coordinate between observations. It retains the existing ROI, preprocessing, material proposals, hypothesis features, hard visual-safety checks and export/report infrastructure. It replaces the final-analysis decision seam that currently discards all but one current-frame hypothesis before temporal reasoning can see them.

The causal record is the [R5 root-cause diagnostic](../50-diagnostics/s11/s11-r5-current-frame-authority-root-cause.md). Acceptance is owned by the [R5 validation contract](../30-validation/s11-r5-sequence-first-trajectory-validation.md).

## Evidence that reopens the architecture

The secure-Windows R4 replay demonstrates an architectural failure rather than an isolated threshold defect:

- Base has no visual Foam, yet fixed glare/residue repeatedly creates high raw Foam evidence and still controls portions of the reported history;
- Base and Accum publish numeric Oil in only about `9.7%` and `8.0%` of frames while producing roughly ten Oil hypotheses per frame;
- `UNKNOWN_REVIEW` occupies about `72–87%` of the sequences even though a human uses movement before and after a weak frame to follow the interface;
- the confirmed initial FULL/EMPTY state loses practical authority before the first real transition; and
- a first accepted candidate after a long gap can be mislabeled as a minimum, maximum or drop onset even when it is a fixed artifact.

Repository-local blind review supplies the reproducible companion evidence. In sample3, correct-range material representation exists in most visually positive anchor frames, but current-frame semantics removes much of it before the serialized reducer runs. The previous accepted-observation interpolation probe was insufficient because it could only bridge already accepted coordinates and could reinforce an accepted wrong boundary. R5 instead resolves the candidate lattice itself.

## Final-analysis authority

The completed analysis path becomes:

```text
frame raster
  -> current-frame preprocessing and bounded material hypotheses
  -> per-frame evidence packet (all hard-safe Oil hypotheses, state evidence, raw Foam evidence)
  -> whole-window sequence resolver
       - recurring-artifact tracks
       - FULL / EMPTY / visible-boundary / UNKNOWN state path
       - independent Foam episode path
  -> one sequence-resolved observation per sampled frame
  -> TrackingSample / events / user report
```

Current-frame detection remains useful for preview and debug. It is no longer the final publication authority for a completed analysis when the detector exposes the R5 sequence resolver. The legacy serialized reducer remains a current-frame compatibility path; it does not feed its selected coordinate back into the R5 lattice.

## Per-frame evidence packet

Every sampled frame contributes only evidence produced from that frame:

- at most the configured bounded Oil hypothesis count, with source Y, boundary, artifact and ambiguity likelihoods, visibility/availability, broad and narrow phase support, static overlap, glare, exclusion and border conflict;
- typed no-interface likelihood and its FULL/EMPTY components when available;
- hard-unavailable, severe-glare and pipeline-failure facts;
- the raw Foam component, current-frame material/topology features, learned-static overlap and adjacent-frame bounded appearance-change features; and
- frame/time/source geometry needed to project a selected observation.

The packet contains no truth coordinate, sample/video identity, report result or future label. Candidate arrays remain bounded by the existing proposal limit. Adjacent-frame appearance comparison retains at most one normalized Foam raster per Glass and scalar registration/turnover metrics.

## Oil and fill-state lattice

For frame `t`, the resolver builds the following nodes:

- one node for each hard-safe Oil hypothesis;
- `FULL_NO_INTERFACE`;
- `EMPTY_NO_INTERFACE`; and
- `UNKNOWN_REVIEW`.

An Oil node's emission combines positive material likelihood, visibility/availability and independent broad/narrow support, then subtracts artifact/ambiguity, glare/exclusion/border and recurring-static-track opposition. No single weak feature is a hard veto. A hypothesis with hard unavailability, severe visual conflict, impossible geometry or authoritative physical topology never enters the lattice.

FULL/EMPTY emissions come from affirmative typed no-interface evidence. A current-frame `UNKNOWN_REVIEW` result is not itself proof of either state. An explicit current-run FULL/EMPTY confirmation supplies a strong initial state prior and bounded persistence, but never supplies an Oil coordinate.

Transitions encode physical continuity:

- nearby candidate-to-candidate motion is preferred; increasingly large jumps receive increasing cost;
- a stable candidate may remain stationary when its material evidence is strong;
- FULL can expose a boundary only through the upper entrance band, and EMPTY only through the lower entrance band;
- a visible boundary can disappear into FULL/EMPTY only through the corresponding edge band;
- UNKNOWN is always available, so the resolver is never forced to invent a line; and
- short missing spans may preserve state continuity, but may not create a numeric coordinate without a current-frame candidate.

An unconfirmed FULL/EMPTY transition additionally requires affirmative same-frame no-interface support. A trajectory that merely approaches an edge cannot materialize a state and accumulate persistence reward by itself. Near-black frames are classified as hard unavailable from raw effective-ROI photometric statistics before CLAHE can turn codec black into apparent structure.

Direct current-frame selections act as bounded anchors only when they retain material support and low artifact opposition. Long analysis windows require a cluster of compatible anchors; a pair is sufficient only in a genuinely short window. Candidate-only points may connect nearby anchors, but a long interval between independent anchor clusters stays UNKNOWN. This prevents a soft candidate chain from turning one fixed row into a continuous report line while retaining low-contrast movement inside a supported run.

The implementation uses deterministic bounded dynamic programming. It keeps only scalar costs/back-pointers for the sampled window and at most `candidate_top_k` Oil nodes per frame. Tie-breaking is stable by state kind, source Y and hypothesis identity.

## Recurring artifact tracks

A stationary coordinate is not automatically an artifact: a real level may remain steady. R5 therefore applies recurring-artifact opposition only when the same narrow Y track is repeatedly present and its evidence is conjunctively artifact-like:

- long-lived recurrence at nearly the same source Y;
- low coordinate/feature variation;
- high artifact, learned-static, glare or border opposition; and
- lack of material/motion support relative to a competing continuous path.

The result is a soft path cost, not a hard global row exclusion. This prevents the fixed lower edge described in the Windows replay from winning merely through repetition while preserving a genuinely stationary, material-supported interface such as the retained sample2 case.

## Sequence-resolved observation and provenance

When an Oil node wins, its coordinate is copied from that frame's actual hypothesis. The output carries `SEQUENCE_RESOLVED_OIL` and candidate-level provenance. It is an observed candidate selected with sequence context, not an interpolated or predicted coordinate.

When FULL or EMPTY wins, the output has a valid state and no numeric Oil. When UNKNOWN wins, it stays unavailable and invalid. R5 never carries a last coordinate through UNKNOWN, creates a midpoint, or turns the confirmed initial state into detector truth.

The report may draw a solid sequence-resolved run because every point in the run has a current-frame candidate. Existing dashed display-only bridges remain presentation-only and keep all prior restrictions.

## Initial-state responsibility

Only a current-run user confirmation grants initial FULL/EMPTY authority. It remains active until the sequence supplies either:

- a compatible boundary entering through the expected edge and continuing in the expected direction; or
- independent affirmative evidence that contradicts the prior, in which case the result requires review.

Foam-like appearance alone cannot erase the confirmed state. The confirmation does not choose an Oil hypothesis, add a numeric sample or override a hard unavailable/glare frame. Existing retrospective reconstruction remains a compatibility/audit projection for detectors without R5; an R5-resolved leading state is already explicit and must not be reconstructed a second time.

## Foam episode responsibility

Raw Foam classification and public Foam history are separated.

R5 evaluates Foam as an episode after resolving Oil/state. A public Foam episode requires sustained material support plus temporal evidence that distinguishes a changing layer from fixed Glass appearance. The bounded episode evidence includes front/area/shape evolution, adjacent-mask turnover, learned-static overlap and row coherence. Constant high score, a static glare crescent, a single bubble or one-frame component is insufficient.

Foam does not choose Oil or FULL/EMPTY. Composition occurs only after the Oil/state path is fixed:

- visible Oil plus confirmed Foam becomes `FOAMING_VISIBLE`;
- resolved FULL plus confirmed Foam becomes `FULL_WITH_FOAM`;
- Foam-only UNKNOWN remains `UNKNOWN_REVIEW`; and
- rejected raw Foam remains diagnostic evidence and carries no fill-state, retrospective or event authority.

Episode start/end are the first/last supported sampled observations. No backdating through a missing interval is permitted.

An accepted episode does not retroactively authorize a static prelude. Public onset begins at the first adjacent-frame change/front evolution that confirms the material component, and only bounded persistence may follow the last changing observation. This keeps a later real Foam episode from converting earlier glare/residue into Foam history.

## Report consequence

The primary report consumes sequence-resolved samples and continues to focus on the observation narrative: level trajectory, FULL/EMPTY intervals, bounded Foam episodes, highest/lowest level and state-change moments with Glass-focused captures. Raw candidates, rejection scores and resolver costs remain in debug artifacts, not in the main report.

Highest/lowest and Oil-drop events require a supported run; a lone point after a long UNKNOWN interval cannot establish an extremum or onset by itself. Event time means first observed support, not an estimated hidden physical time.

`OIL_DROP_START` also requires an observed numeric baseline, a multi-sample confirmation window, a material net decrease and a majority of decreasing steps. A one-step candidate switch is not a lifecycle event. Zero crossings require the new side of zero to persist for the debounce interval before publication.

## Rejected alternatives

R5 explicitly rejects:

- global Canny/Hough/confidence/ambiguity relaxation;
- selecting top-1/top-2 merely to increase numeric coverage;
- linear interpolation, last-value carry-forward or Kalman prediction as a reported Oil coordinate;
- treating every stationary line as an artifact;
- allowing Foam to outrank or replace Oil/state resolution;
- preserving exact legacy output fingerprints as physical truth;
- sample, frame, Recipe or truth-specific branches; and
- claiming secure-Windows acceptance from repository-local samples.

## Cutover and fallback boundary

R5 is enabled only for a completed analysis window and only when the detector implements the sequence contract. Other detector implementations and focused single-frame preview/redetection retain the existing conversion path. A resolver exception aborts analysis visibly; it must not silently fall back to the known-bad current-frame report stream.

If direct visual audit shows that a real boundary hypothesis is absent in most clear frames, stop sequence tuning and repair representation first. If the lattice increases continuous wrong-interface duration, suppresses retained real Foam, or requires identity-specific constants, do not cut it over.
