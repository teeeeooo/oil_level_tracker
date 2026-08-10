# S11-R4 Windows Residual Authority Diagnostic

## Responsibility

This record classifies the first secure-Windows replay after R3. It separates demonstrated residual authority defects from metrics that remain non-reproducible in the repository checkout. Current sequencing belongs to the [work plan](../../00-project/work-plan.md); accepted behavior belongs to the linked R4 architecture and validation owners.

## Secure-Windows result received

The same private Base/Accum field video was replayed with R3. Relative to the prior detector:

- Base emitted `FOAM_STATIC_ARTIFACT_REJECTED` / `static_rejected` `313` times and reduced `FULL_WITH_FOAM` from `95.7%` to `32.1%`;
- Base exact `foam_static_artifact_overlap` averaged `0.793`, immediately below the existing `0.80` publication cutoff as a population;
- Accum emitted `286` weak-component, `61` row-incoherent and `37` ambiguous Foam rejections instead of accepting every Foam-like component;
- lifecycle output now includes MAX/MIN, Oil-drop and an Accum `EMPTY_NO_INTERFACE_START` event; and
- numeric Oil coverage remains `9.7%` for Base and `8.0%` for Accum, with `UNKNOWN_REVIEW` still dominant.

The operator's direct visual review remains the physical oracle for this unavailable video: Base starts full with no Foam and then drains from the top; Accum starts empty, rises, has real turbulent Foam only during the bounded rising interval, reaches its maximum and then drains.

## What R3 proved and what it did not

R3's publication separation is effective: a high raw Foam score no longer automatically means public Foam. The unchanged Base raw score is therefore not itself a regression. Current-frame appearance remains Foam-like; the missing responsibility is robust opposition and publication authority.

The exact-overlap rule is brittle at its decision boundary. The mean `0.793` population, together with hundreds of successful rejections and substantial remaining `FULL_WITH_FOAM`, is consistent with the same fixed component moving by a few mask pixels under blur, refraction or decode alignment. Lowering `0.80` globally would not distinguish that cause from genuine new Foam.

Strong S5-A evidence still bypasses the moderate persistence path. Any residual coherent component that misses the static cutoff can therefore publish immediately, become `FULL_WITH_FOAM`, constrain S5-B and create a retrospective `AUTHORITATIVE_FOAM` barrier.

The retrospective reducer checks the Foam barrier before checking whether the same immutable sample also contains an independently accepted canonical Oil boundary. That ordering discards evidence already proven by D5 below authoritative Foam. Foam-only observation must remain a barrier; Foam cannot veto independent numeric Oil merely by coexisting with it.

## Local Oil-static counterevidence

A repository-local probe measured best-candidate static overlap across the four accepted windows. Base and sample3 were `0.0`; sample4 stayed at or below `0.176`; the retained real sample2 interface reached `0.260` because its short start/middle/end preparation frames contain the true boundary at nearly the same row. A controlled learned static structural band produces values around `0.18` under the current band-normalized metric.

Therefore static Oil overlap is not a demonstrated hard discriminator. Promoting it to a hard veto could reject a physically real stationary interface. R4 does not change Oil thresholds, static-prior scoring or ambiguity authority from this evidence. The Windows fixed Oil-like candidate requires its own candidate-level static/residual metrics before any later Oil authority repair.

## Coordinate and onset claim boundary

The reported Accum sign change in pixels from zero cannot be classified as a coordinate bug without the private Recipe, source overlay and actual boundary coordinate. Production defines engineering position as `zero_line_y - source_y`, so crossing the configured zero line legitimately changes sign. R4 preserves this contract and requires overlay evidence at the Windows gate.

Sparse accepted observations can make `OIL_DROP_START` tens of seconds later than the physical onset. R4 must not backdate an event through missing observations. The user report should label the stored event as the first sustained decrease **observed** by the detector.

## Bounded repair hypothesis

R4 should test four independent seams:

1. exact static overlap remains sufficient, while a second conjunctive path requires high distance-tolerant current-to-static alignment and high reciprocal static-to-current alignment;
2. strong Foam onset requires two compatible consecutive samples, after which continuous strong evidence remains published without alternating dropout;
3. a pending coherent/non-static strong component retains D5 Oil-safety authority without gaining public Foam authority;
4. authoritative Foam without numeric Oil remains a retrospective barrier, while an independently accepted numeric Oil sample remains eligible direction/topology evidence; and
5. report wording states observation time rather than claiming hidden physical onset, and report grouping does not reject an already temporal-confirmed singleton a second time.

Failure of the secure replay after these mechanisms must reopen the earliest measured representation. It must not trigger global Foam-score, Oil-confidence or ambiguity relaxation.
