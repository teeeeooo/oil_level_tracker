# S11-A Detector Direction and Experiment Plan

## Status and purpose

**Status:** `ACTIVE — design direction agreed; source repair not yet started`

This document records the post-S10 S11-A investigation result and the agreed detector direction before any production detector mutation.
It supplements [S11 Real-Field Detector Effectiveness Recovery](s11-real-field-detector-effectiveness-plan.md) and does not replace the S5-B observability contract.

The private Windows field video is diagnostic input only. It cannot leave the company environment and is not a repeatable S11 development corpus.
The reproducible engineering corpus for S11 is the repository-local `sample/` set with its preserved Recipes, user-confirmed `.oiltruth`, S6 benchmark datasets and controlled regressions.

## Evidence boundary

The private field evidence establishes a real product failure class:

- Base can contain a visually clear Oil boundary while the detector emits `ambiguous` and `NO_UPDATE`;
- Accum can become dark/low-contrast and receive strong `FULL_NO_INTERFACE` / `EMPTY_NO_INTERFACE` evidence;
- accepted numeric Oil appears only intermittently as lighting changes;
- these observations motivate repair but are not authoritative truth or reproducible acceptance fixtures.

S11 must therefore improve a general detector mechanism using reproducible repository evidence rather than tuning to private-video timestamps, filenames, hashes, ROI identities or manually copied field thresholds.

## Reproducible S11 corpus

The current local corpus remains the S6-owned four-video set:

- `base_sample_1.mp4` / Recipe / `.oiltruth`;
- `sample2.mp4` / Recipe / `.oiltruth`;
- `sample3.mp4` / Recipe / `.oiltruth`;
- `sample4.mp4` / Recipe / `.oiltruth`.

The product truth contains `15` reviewed frames: `13` usable and `2` unusable.
The latest S6-D4 feature result recovered numeric Oil on `7/13` usable cases with `4.43 px` raw Oil MAE over the seven matches, while preserving Foam precision `7/7` and recall `7/10`.

The six remaining usable Oil misses are intentionally valuable S11 cases:

- sample1 frames `156` and `240`: visible Oil with strong explanatory horizontal overlay;
- sample2 frames `0`, `30`, `60`: reflection plus Oil/Foam compound evidence;
- sample3 frame `900`: Oil/Foam compound evidence;
- sample4 has no remaining Oil-coverage miss in the D4 corpus.

S11 does not require the private Windows video to be repeatedly re-analyzed. Field observations define failure classes; local truth and controlled transformations provide reproducible experiments.

## Field-to-local failure reproduction

A read-only diagnostic probe applied uniform brightness factors to truth-positive local frames without changing geometry or truth.
The probe is not benchmark evidence and must not be promoted to accuracy truth; it exists to test failure mechanisms.

Observed examples:

- sample1 frame `144`: native numeric Oil at `395`, but `0.60×` brightness became ambiguous and `0.45×` became `FULL_NO_INTERFACE` with no-interface `0.596`, uniformity/full likelihood `0.837`;
- sample3 frame `900`: native ambiguity/no-interface `0.545`; `0.60×` became `FULL_NO_INTERFACE` at `0.601`, and `0.45×` reached `0.647`;
- sample3 frame `1035`: native truth-near Oil `245` vs truth `243`; `0.60×` lost numeric Oil and `0.45×` became `FULL_NO_INTERFACE`;
- sample1 overlay frames `156`/`240` behaved non-monotonically: moderate darkening could recover a numeric boundary although native frames remained ambiguous.

This reproduces the field-derived exposure sensitivity class using repository data and also proves that the present competition is non-monotonic. A global threshold reduction or one brightness cutoff is therefore not an acceptable design.

## External design findings

General transparent-vessel computer-vision literature supports a multi-evidence boundary model rather than a strongest-horizontal-line rule.
The 2014 Eppel/Kachman liquid-surface study found the most useful indicators to include relative intensity change normal to the candidate curve, edge-density change and gradient direction relative to the curve normal. It specifically reports relative intensity difference as more robust to illumination than absolute intensity difference.

Later transparent-vessel work used constrained path or graph optimization to trace material boundaries across the vessel rather than committing to one independent row. Those methods are relevant as a later spatial-consistency option, but reflections and vessel structure remain explicit false-boundary risks.

OpenCV already provides the necessary primitive family for the next experiment: CLAHE/local normalization, Sobel/Scharr derivatives, Canny, Hough lines and line-segment detection. Official OpenCV documentation notes that the 3×3 Scharr derivative may be more accurate than 3×3 Sobel, but local probes did not show evidence that replacing Sobel alone solves the current failures.

References:

- Eppel & Kachman, 2014, `Computer vision-based recognition of liquid surfaces and phase boundaries in transparent vessels, with emphasis on chemistry applications`, arXiv:1404.7174.
- Eppel, 2015, `Tracing the boundaries of materials in transparent vessels using computer vision`, arXiv:1501.04691.
- Eppel, 2016, `Tracing liquid level and material boundaries in transparent vessels using the graph cut computer vision approach`, arXiv:1602.00177.
- OpenCV documentation for Sobel/Scharr, Canny, Hough and LineSegmentDetector primitives.

### Local relative-contrast probe

The literature direction also reproduced locally. Around the user-truth Oil Y, uniform darkening reduced absolute grayscale phase contrast approximately in proportion to exposure while a simple relative contrast `|ΔI| / local intensity` remained substantially more stable.

- sample3 frame `900`: absolute contrast `0.1176 → 0.0510` from `1.00× → 0.45×`, while relative contrast stayed `0.5556 → 0.5532`;
- sample4 frame `450`: absolute contrast `0.2863 → 0.1294`, while relative contrast stayed `1.0069 → 1.0154`;
- sample3 frame `1035`: relative contrast remained about `0.25–0.26` across the same brightness sweep although the production detector eventually lost numeric Oil.

This does not define the final formula or threshold. It is mechanism evidence that exposure-normalized phase information is worth testing before replacing the OpenCV primitive stack.

## Selected architecture direction

S11 keeps the OpenCV/NumPy production stack for the first repair cycle. A new classical-CV dependency or ML runtime is not justified by current evidence.

The selected order is:

1. add exposure-robust relative/local photometric phase evidence;
2. separate observable-interface evidence from FULL/EMPTY appearance evidence in the no-interface owner;
3. fuse the new evidence with retained Sobel/Canny/Hough, polarity, visibility and structural protection rather than replacing them;
4. evaluate bounded spatial path consistency only if the first two changes leave important compound misses;
5. evaluate new temporal positive evidence only if current-frame location/evidence is repeatedly credible but canonical acceptance still discards it.

Scharr and LineSegmentDetector are supplemental experiments, not selected replacements. Optical flow is not the first temporal mechanism because stationary true Oil is valid and illumination changes can manufacture apparent motion.

The design must preserve S5-B latent-truth versus observable-outcome separation. Repeated ambiguity alone cannot become positive evidence, and genuinely unidentifiable glare/Oil collisions remain fail-closed.

## Architecture probe before production repair

The next implementation unit should first compare bounded experimental variants against the same frozen truth and regressions:

- `P0`: current production behavior;
- `P1`: relative/local-normalized phase evidence added without weakening existing negatives;
- `P2`: exposure-decoupled no-interface evidence, separating interface absence from FULL/EMPTY appearance;
- `P3`: `P1 + P2` combined;
- supplemental only: Scharr and LineSegmentDetector corroboration probes.

Each variant must be exercised on native frames and controlled photometric transformations such as brightness, gamma and contrast changes. Transformations preserve source geometry/truth identity but are diagnostic/metamorphic evidence, not new user truth.

Required comparison dimensions include:

- native Oil coverage and truth-near Oil error;
- retention of truth-positive Oil across photometric variants;
- false no-interface on truth-positive scenes;
- structural/rim/glare false-Oil protection;
- Foam precision/recall and Oil/Foam separation;
- `UNKNOWN_REVIEW` / ambiguity behavior;
- deterministic CPU/memory/resource bounds.

A higher `13/13` local coverage number is not sufficient by itself. Acceptance requires mechanism-level improvement without corpus-specific branching or negative-protection regression.

## Lane and ownership implication

The actual source lane remains evidence-dependent until the architecture probe shows the smallest sufficient change.

- A bounded change inside existing preprocessing/evidence owners that preserves S5-B observability semantics, temporal ownership, public/persisted schemas and dependencies may be classified as Lane B with explicit evidence.
- A change to no-interface observability meaning, canonical positive-evidence semantics, temporal photometric/component history, validation architecture or runtime dependencies is Lane C and requires fresh independent audit.

Given the current leading direction touches no-interface and positive-evidence semantics, S11 source work should begin with a **provisional Lane C** assumption and may narrow only if the probe proves a materially smaller existing-owner defect.

## Claim boundary

This document does not declare detector accuracy PASS, general-field coverage, field-video reproduction equivalence or a final root cause.
It records the agreed engineering direction and the reproducible experiment needed to select the repair.

The private field video remains outside repository authority. S12 UI/UX refinement remains a separate successor and must not be combined with S11 detector work.
