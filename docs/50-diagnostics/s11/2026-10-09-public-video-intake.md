# Three new public-video controls — 2026-10-09

Base: `99aa9d84ede5e5829a04c34b87edf46a42434b3e`.
The user supplied three videos in `sample/` and requested an assessment of their
usefulness and how to use them. This is an **agent visual intake**, not a detector
comparison, physical ground-truth annotation or implementation trial. The
[Work Plan](../../00-project/work-plan.md) retains current gate authority.

**Assessment:** all three are useful, complementary development controls. Use
water first for structure/interface correspondence, beer next for separate
liquid/Foam boundaries, and milk for opaque-liquid/white-appearance opposition.
They do not replace compressor sight-glass or Windows acceptance.

## Identity and exposure

| Local filename | Size (bytes) | Resolution | Reported playback FPS | Decoded frames | Nominal duration |
|---|---:|---|---:|---:|---:|
| `public_water_fill_pexels_6381722.mp4` | 21,089,117 | 1920 × 1080 | 29.970030 | 1,644 | 54.855 s |
| `public_beer_fill_pexels_5538050.mp4` | 18,990,737 | 2732 × 1440 | 25 | 583 | 23.320 s |
| `public_milk_fill_pexels_11158788.mp4` | 11,532,102 | 1920 × 1080 | 23.976024 | 1,064 | 44.378 s |

All **3,291 frames decode sequentially** with counts matching metadata. Before
pixel inspection, the intake freezes all three as `development_intake`; no
tracked prior reference was found, but outside-session exposure is unknown.
The overview uses first/last plus seven evenly spaced frames per file. The
bounded temporal follow-up uses quarter-time centers ±0.25 playback seconds and
fixed display-only crops. There are **45 unique visually inspected frames**;
decoding every frame does not mean every frame was visually reviewed.

SHA-256, exact reviewed indices, native/crop image hashes, scripts, input-preserved
checks and preflights are in the [machine record](2026-10-09-public-video-intake.json).
Pexels IDs are derived from filenames; upstream pages, acquisition lineage,
recording-session independence and original filming speed are unverified. These
durations are playback time, not certified physical speed. All original bytes
remain unchanged. MP4s and generated images remain ignored and local.

All three have now been exposed during design intake. They can support frozen
later development comparisons, but none is an untouched final holdout. Do not
split adjacent frames or reduced-resolution copies into separate partitions.
The three files add scene diversity without proving independent field sampling.

## What the images contribute

### Water: highest priority for the current correspondence problem

The inspected opening frames show an empty tall glass with a fixed patterned
base. Filling creates strongly moving, sloped splash surfaces and bubbles; later
views show a comparatively settled upper water boundary while bubbles diminish.
The framing appears stable in the inspected views. The empty image provides
same-scene structure context that was obscured by Foam in prior sample4 references.

Use approximate **0–7 s** as initial empty/structure context, **13–34 s** for
pouring/splash/bubble alternatives, and **41–55 s** for the settling surface and
persistent base-pattern opposition. These are proposed inspection windows based
on the sampled frames, not exact onset/cessation labels. This directly tests
whether a method keeps following the same visible surface instead of hopping to
fixed decorative patterns or moving bubbles. A fixed glass object can change
appearance under water/refraction; an empty-frame subtraction is not a safe mask.

The dark background and side lighting make transparent-liquid highlights visible
but introduce strong view-dependent contours. A splash sheet or isolated bubble
top is not automatically a reportable level. No single scalar is assigned to
the oblique pouring surface by this intake, and water is not a Foam-free label
for every transient pixel.

### Beer: most useful for independent liquid and Foam outputs

Early views show a fixed thick base/rim while the liquid and frothy layer rise.
Later views expose a much clearer liquid–Foam transition and evolving bubbles.
Inspect approximately **3–9 s** for forming froth and visible upper surface, and
**17–23 s** for the liquid–Foam transition and bubble changes. Early boundaries
are diffuse/turbulent and not automatically two clean reference contours.

Crucially, the **upper Foam–air surface leaves the source image** during filling;
the 11.4–11.88 s views are clipped at the top, and late views show the Foam layer
entering through the upper image border. This is useful unavailable-coordinate
opposition: a visible liquid–Foam boundary must not be copied into the independent
Foam-top output. Foam presence can be known while its top coordinate is unavailable.
The exact crop-exit time has not been measured.

The beer clip therefore cannot test full visible-Foam-top tracking through its
entire duration. It remains valuable for separating boundary roles and preserving
per-output visibility. Its large, well-lit tumbler differs from the small sight glass.

### Milk: complementary white-appearance and simpler-surface control

The opening views show an empty glass; middle views show an opaque white liquid
body rising under a stream; late views show a settled body with surface bubbles
or a thin frothy region. Use approximately **0–6 s**, **11–28 s**, and **33–44 s**
for those three contexts. The high-contrast body supports a simpler boundary
formation check while the fixed rim/base remain visible distractors.

The useful opposition is **bulk white liquid versus surface froth**, not a claim
that this entire video has no Foam. A method must not label every white body
pixel as Foam, nor equate a falling stream or wall splash with the layer surface.
The agent cannot certify an exact milk/froth dividing contour from this intake.
Appearance differs strongly from transparent Oil, so a good milk result alone
has limited transfer value.

## Recommended use and limits

1. Create a small source-bound control sheet from the proposed contexts **before
   viewing detector predictions**: visible material boundary, fixed structure,
   moving internal/splash feature, and unavailable/uncertain geometry. Reuse the
   existing review/evaluation owners; these preliminary readings are not human truth.
2. For the next joint correspondence/side-role proposal, use water's empty/filled
   same-scene relation first. Add beer's separate boundary/crop cases and milk's
   white-body opposition. Do not rerun the already rejected independent-strip rule
   as though changing the video alone makes it a new mechanism.
3. Test a bounded new observable on native pixels first. Then freeze one
   aspect-preserving reduced-resolution comparison to expose detail loss at
   sight-glass-like projected size. The derivative remains the same case/partition;
   do not tune scaling to obtain success or claim it reproduces the real optics.
4. Preserve the original Mac sample4 real-front/glass controls and the other Mac
   regression windows. Any mechanism must return to those scenes before promotion;
   the private Windows shadow/holdout and field gates remain separate.

These videos add empty references, clear changing material coverage, visible
fixed structures and crop-based unavailable cases. That can reveal whether a
failure comes from a proposed rule or from lost image detail, reducing reliance
on repeated microscopic interpretation of sample4. This intake establishes no
coverage of the compressor's low-pixel circular glass patterns, coated/dirty
viewing window, layered Oil chemistry, full drain/reversal/re-entry sequence or
certified scalar truth. The observed filling scenes cannot close those acceptance
dimensions.

No production detector, Recipe, threshold, model, label or acceptance state is
changed. No ML or Windows execution is needed for this assessment. Full intake
outputs and six overview/temporal sheets remain in
`sample/output/s11-public-video-intake-20261009-001/`. Further human judgment is
needed only if a concrete proposed control has an ambiguous physical role; no
per-frame or exact-pixel labeling request follows from this intake.

Input/output hash checks, detector governance and whitespace checks pass. The
document audit checks 998 local links and 17 named obligations with no errors;
protected owners remain unchanged. No production tests are rerun for this intake.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PROPOSAL`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: NOT_EVALUATED — no detector was executed on these files. The visible scene/control possibilities do not diagnose a new detector failure or certify a physical selector.
- Logic-map impact: NONE — local video intake changes no implementation or control-flow owner.
- Failure-registry impact: NONE — proposed control coverage reuses existing motion, appearance, coupled-output and provenance guards; no new mechanism or efficacy result.
