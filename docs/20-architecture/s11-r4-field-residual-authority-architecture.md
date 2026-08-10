# S11-R4 Field Residual Authority Architecture

**Status:** `ACTIVE`

## Purpose

R4 owns the bounded residual repair supported by the first secure-Windows R3 replay. Its objective is to prevent fixed or one-frame Foam-like appearance from controlling fill state, Oil routing and initial-state interpretation while preserving real Foam and independently accepted Oil evidence.

The causal record is the [R4 Windows residual diagnostic](../50-diagnostics/s11/s11-r4-windows-residual-authority-diagnostic.md). R3 dark-cap and row-coherence responsibilities remain intact. Source video identity, frame identity, truth and private timestamps remain prohibited production inputs.

## Prior design and external-reference review

R4 reuses, rather than replaces, the accepted S11 evidence model. The review trail is recorded in the [implementation reference log](../70-reference/implementation-reference-log.md): transparent-vessel work supports relative/multi-line/path evidence, while the controlled-illumination study makes fixed optics and refraction explicit competing causes. The commercial sight-glass material supports confidence and application-specific uncertainty but supplies no transferable Foam discriminator. This evidence favors registered fixed-appearance opposition and bounded temporal confirmation; it does not justify global Canny/Hough/score loosening, a new ML owner or forced numeric publication.

## Repair A — registered static-Foam opposition

### Failure model

The R3 exact overlap is `current support ∩ learned support / current support`. It is intentionally strict but changes abruptly at `0.80`. A fixed component displaced by a few pixels can fall just below the cutoff even when its shape and location remain materially the same.

### Match contract

For the current candidate mask and learned static-Foam map, compute:

- exact current coverage using the unchanged pixel intersection;
- tolerant current coverage against a dilated learned map; and
- reciprocal learned-map coverage against a dilated current mask.

The dilation radius is deterministic and crop-bounded: one percent of the smaller raster dimension, rounded and clamped to `1–3 px`. The component is static-dominated when either:

1. exact current coverage is at least `0.80`; or
2. exact coverage is at least `0.70`, tolerant current coverage is at least `0.90`, and reciprocal learned coverage is at least `0.70`.

The second path is conjunctive. It handles mask jitter without converting a small partial overlap or a materially larger new Foam layer into static proof. A real layer indistinguishable from fixed appearance in all representative frames remains observationally non-identifiable and fails closed.

Raw score, exact/tolerant/reciprocal metrics, radius and mask remain diagnostic. Static dominance withholds public Foam, tracker/fill authority and S5-B context exactly as R3 did.

## Repair B — strong-Foam onset confirmation

Strong evidence no longer bypasses all temporal confirmation. A new strong component requires two consecutive front-compatible samples before publication. Compatibility uses the existing `foam_max_front_jump_px` envelope. The gate retains only bounded scalar state: count, last Y and last score.

After confirmation, each continuous strong sample remains accepted; the state must not be cleared on acceptance and produce alternating pending/accepted output. A jump, weak/ambiguous/glare result, static rejection or row-incoherent rejection clears the chain. Moderate evidence keeps its configured persistence requirement and may compose with a compatible strong chain.

This introduces at most one sampling interval of strong-Foam onset latency. It removes isolated strong false events without smoothing masks, extending Foam through dropouts or changing S5-A evidence scores.

Publication delay does not remove current-frame physical safety. During the first pending strong sample, a coherent component that is not static-dominated may constrain S5-B immediately through the existing D5 front/mask rules. It still cannot update public Foam, fill state, the Foam tracker or retrospective Foam history until confirmation. Static, row-incoherent, moderate-pending and other rejected evidence receives neither publication nor this safety authority. This keeps D1 publication and Oil-routing responsibilities distinct and prevents a one-frame false-Oil hole.

## Repair C — Foam/numeric retrospective composition

Initial-state reconstruction keeps the following ordering:

1. direct prior contradiction and hard unavailable/failure/glare barriers remain authoritative;
2. determine whether the immutable sample contains a valid finite canonical Oil boundary;
3. authoritative Foam is a barrier only when no such independent numeric Oil exists; and
4. a Foam-plus-Oil sample may contribute numeric topology/direction evidence, but the Foam sample itself is never rewritten by retrospective projection.

This follows D5 responsibility: accepted Foam constrains Oil, while the accepted Oil boundary remains independently canonical below that constraint. It does not allow Foam state, the confirmed prior or a retrospectively projected label to become positive Oil evidence. Foam-only prefixes remain unresolved.

## Repair D — observed-onset and confirmed-Foam report semantics

`OIL_DROP_START` is generated from stored finite observations and cannot identify an earlier physical onset hidden inside an observation gap. User-facing labels and descriptions therefore say **first observed sustained decrease**, while the stored timestamp and event schema remain unchanged.

The report does not backdate, interpolate or estimate a hidden start time. Direct graph runs, dashed display-only bridges, state/review bands and source captures retain their existing authority.

The detector publication gate already proves two compatible strong samples (or the configured moderate chain). Report presentation therefore must not require a second independent two-positive gate. A single stored public Foam sample carrying `FOAM_STRONG_EVIDENCE` or `FOAM_MODERATE_EVIDENCE` may form a bounded report episode; an unconfirmed one-sample Foam-like value remains flicker and is omitted. Episode time starts at the stored public sample and is never backdated to the hidden pending sample.

## Explicitly rejected alternatives

R4 does not authorize:

- lowering the exact static threshold by itself;
- changing Foam whiteness, chroma, texture or score thresholds merely because raw Base score stays high;
- hard-rejecting Oil from learned-static overlap, because a retained stationary sample2 interface provides direct counterevidence;
- relaxing Oil confidence, ambiguity, no-interface or reacquisition thresholds to chase `70%` coverage;
- changing the zero-line sign convention or applying an offset without source-overlay reproduction;
- retrospective projection across Foam-only or hard unavailable barriers; or
- event backdating, numeric interpolation, identity branches or report-derived detector feedback.

## Ownership and resource boundary

- `OpenCvPhaseDetector` owns mask-to-map match calculation and debug projection.
- `FoamTemporalGate` owns static-dominance and onset-publication decisions.
- S5-A remains raw current-frame Foam evidence owner.
- S5-B remains the only current-frame Oil semantic owner and its serialized reducer remains the only online Oil temporal owner.
- Initial-state reconstruction remains downstream of immutable TrackingSamples.
- Report presentation owns observed-onset wording and grouping of already confirmed public Foam; event timestamps and stored detector samples are unchanged.

The repair adds no dependency, public Recipe/result schema, raster history or unbounded state.

## Stop boundary

Narrow or revert a mechanism if it suppresses a repository-local genuine Foam episode, loses the confirmed `8/13` Oil truth surface, converts a retained negative to numeric Oil, projects through Foam-only evidence, creates alternating Foam publication, or changes a detector timestamp to improve apparent event latency.
