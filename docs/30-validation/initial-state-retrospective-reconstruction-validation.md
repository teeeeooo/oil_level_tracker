# Initial-State Retrospective FULL/EMPTY Reconstruction Validation Contract

## Scope

This document owns acceptance for the S11 sequence-level retrospective reconstruction responsibility defined by [Initial-State Retrospective FULL/EMPTY Reconstruction Architecture](../20-architecture/initial-state-retrospective-reconstruction-architecture.md). It validates downstream official semantics without reopening the accepted S5-B/S11 detector baseline.

The implementation is a **Lane C** change because it affects shared analysis workflow, official event/judgment/coverage semantics, persisted/result compatibility and a new downstream sequence owner. Current engineering sequencing remains in the [work plan](../00-project/work-plan.md).

## Run-readiness and confirmation acceptance

Acceptance must prove that final analysis:

- rejects `AUTO` for any enabled Glass and rejects missing current-run confirmation even when a persisted/copied Recipe value is populated;
- accepts an explicitly user-confirmed `UNKNOWN_REVIEW` for readiness while granting it no retrospective FULL/EMPTY authority;
- treats current-run confirmation as run/session provenance separate from Recipe persistence;
- invalidates confirmation after video replacement, same-Profile new-video preparation, analysis-start change, initial-state value change, a newly enabled/unconfirmed Glass, or establishment of a new analysis session;
- does not dirty the reusable Profile merely because an unchanged selected initial state is freshly confirmed;
- permits preflight while confirmation is unresolved but proves that preflight cannot silently establish confirmation;
- enforces the same final-analysis confirmation authority through GUI and programmatic/headless entry paths.

## Reconstruction semantics acceptance

Focused tests must cover symmetric `FULL_NO_INTERFACE` and `EMPTY_NO_INTERFACE` reconstruction and prove:

- an R7 stream is eligible only when at least two `R7_OIL_ANCHOR` observations
  establish compatible direction; a first mid-Glass catch remains eligible and
  its entrance topology is recorded as provenance;
- an R7 continuation-only observation cannot confirm the prior;
- a legacy stream already carrying `SEQUENCE_INITIAL_STATE_PRIOR` is not
  projected a second time;
- only the leading unresolved interval is eligible;
- later real accepted numeric-boundary/topology/direction evidence is required;
- direction evidence contains at least two real accepted boundary observations;
- prior-seeded or retrospectively inferred labels cannot circularly confirm the prior;
- eligible ambiguity may remain in a prefix without contributing confirmation;
- unavailable/failure/detection-lost/glare/fog evidence remains observed and
  contributes no confirmation, but does not erase the explicit initial context;
- published, raw, rejected or pending Foam neither confirms nor blocks the
  initial state by itself;
- malformed samples carrying hard-unavailable evidence cannot contribute their
  number as direction proof;
- prior conflict produces no retrospective interval plus first-class conflict/review;
- insufficient positive evidence remains unresolved rather than conflict;
- observed detector state and observed validity are immutable;
- no numeric Oil value is fabricated for retrospective FULL/EMPTY.

## Official semantics and persistence acceptance

Acceptance must demonstrate that:

- original `tracking_data.csv` observed `fill_state`, numeric fields and validity retain their observed meaning;
- retrospective accepted/unresolved/conflict state and provenance are separately persisted;
- observed coverage and effective state-aware coverage are distinguishable whenever retrospective interpretation participates;
- judgment/event outputs retain explicit provenance when retrospective state affects official semantics;
- `RECOVERY` numeric recovery remains dependent on observed numeric Oil rather than retrospective FULL/EMPTY;
- graph/overlay paths preserve numeric gaps and never synthesize an Oil line for inferred out-of-range state.
- an all-missing R8 confirmed-state hold is visibly labeled, leaves raw Oil and
  observed coverage unchanged, and cannot add state events or alter judgment;

## Versioned compatibility acceptance

Compatibility coverage must prove:

- the compatible Recipe schema retains `AUTO`, and legacy sessions/bundles without current-run confirmation retain their existing observed-only meaning;
- legacy v1 observed-only bundles remain readable with their existing meaning;
- bundles carrying retrospective official semantics identify an explicit newer result/review semantics version;
- new readers support both legacy v1 observed-only and the newer retrospective semantics;
- a v1-only consumer fails explicitly on a newer retrospective-semantics bundle instead of silently misrepresenting it as ordinary v1;
- the compatibility proof does not depend on an undocumented assumption about where the version field or retrospective artifact physically lives.

## Result Review and re-detection acceptance

Result Review acceptance must prove:

- observed detector state and retrospective interpretation are separately visible;
- observed `UNKNOWN_REVIEW` remains visible even when a retrospective interpretation is accepted;
- retrospective status exposes accepted/unresolved/conflict provenance;
- observed-detector comparison remains separate from retrospective-interpretation comparison;
- CURRENT/local re-detection does not silently reconstruct an initial sequence without the required full leading context;
- full-sequence re-detection may independently recompute retrospective interpretation only from the saved current-run confirmation plus rerun observations, with provenance distinct from the official saved interpretation.

## Preservation and claim boundary

The accepted S5-B and R8 current-frame/final observation authorities remain
unchanged. No detector thresholds, Oil/state or Foam resolver behavior, online
temporal behavior, Recipe schema migration, truth data or arbitrary middle-run
trajectory estimation is part of this acceptance contract. Historical D1–D5
routing is outside this compatibility contract.

The final Windows field-workflow check remains a later closure obligation after this Lane C implementation and its required validation are accepted; this contract does not authorize executing that final field check.
