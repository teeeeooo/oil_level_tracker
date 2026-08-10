# Initial-State Retrospective FULL/EMPTY Reconstruction Architecture

## Purpose and authority

This document owns the durable sequence-level responsibility for **Initial-State Retrospective FULL/EMPTY Reconstruction**. It is downstream of immutable detector observations and upstream of official event, judgment and state-aware coverage projection. Current sequencing remains owned by the [roadmap](../00-project/roadmap.md) and [work plan](../00-project/work-plan.md); implementation acceptance is owned by the [dedicated validation contract](../30-validation/initial-state-retrospective-reconstruction-validation.md).

This responsibility does not modify S5-B current-frame evidence, S11 D1–D5 authority, or the serialized online temporal owner. Those accepted detector boundaries remain authoritative in [S5-B Oil Boundary Hypothesis Architecture](s5b-oil-boundary-hypothesis-architecture.md) and [S11 Detector Responsibility Architecture](s11-detector-responsibility-architecture.md).

## Placement and immutable observation boundary

The responsibility runs only after the analysis has collected its immutable observed `TrackingSample` sequence and before official event/judgment projection consumes any retrospective state interpretation.

- observed detector `fill_state`, validity, numeric Oil and Foam evidence remain historical observation and are never rewritten;
- retrospective FULL/EMPTY is a separate sequence interpretation with explicit status and provenance;
- no retrospective interpretation can manufacture a numeric Oil boundary, alter detector history, or become hidden state in the online temporal reducer;
- when downstream official semantics use retrospective interpretation, that use must remain explicitly attributable to retrospective provenance.

## Initial authority and eligibility

A retrospective interval is eligible only when the current analysis run contains an explicit run/session-scoped user confirmation for the affected enabled Glass and that confirmed prior is `FULL_NO_INTERFACE` or `EMPTY_NO_INTERFACE`.

Persisted Recipe `initial_state` remains the selected prior, and the compatible Recipe schema continues to retain `AUTO`. Loading, copying or pre-populating that value does not prove current-run confirmation. `AUTO` is unresolved compatibility state, and an explicitly confirmed `UNKNOWN_REVIEW` may satisfy run readiness but grants no retrospective FULL/EMPTY authority. Other explicitly confirmed non-`AUTO` values keep their existing prior semantics but do not activate this responsibility.

Retrospective interpretation is limited to the **leading unresolved interval** before later direct sequence evidence establishes a defensible state trajectory. It is not a general gap-filling mechanism.

## Positive sequence evidence

Eligibility requires later real accepted detector evidence, not prior-seeded labels. The evidence set must materially establish the relevant numeric-boundary/topology/direction interpretation.

- direction evidence requires at least **two real accepted boundary observations**;
- prior-seeded or retrospectively interpreted state labels cannot serve as the sole confirmation of direction or topology;
- canonical ambiguity may remain inside an otherwise eligible leading prefix only when it introduces no barrier or contradiction, but ambiguity contributes no positive confirmation;
- insufficient positive evidence leaves the interval unresolved rather than converting the prior into truth.

## Barriers, contradiction and conflict

The leading prefix stops being retrospectively eligible when sequence evidence introduces an inference barrier or contradicts the confirmed prior. Barriers materially include unavailable/failure/detection-lost/glare/fog evidence, authoritative Foam, and other direct evidence that prevents a defensible FULL/EMPTY interpretation across the interval.

Direct contradictory sequence evidence overrides prior-based eligibility. A prior conflict yields **no retrospective interval**, a first-class conflict status and review requirement. A lack of enough confirming evidence without contradiction is **unresolved**, not conflict.

Hard unavailable/failure/detection-lost/glare/fog evidence remains a barrier even if malformed input also carries a number. Authoritative Foam is a barrier when the sample has no independently accepted finite canonical Oil boundary. When valid numeric Oil coexists with Foam, D5 has already applied the physical topology constraint; that numeric observation may contribute direction/topology evidence, while the Foam sample itself remains immutable and is excluded from retrospective state projection. Foam-only prefixes remain unresolved.

## Non-authorities

This responsibility must not introduce:

- synthetic numeric Oil boundaries or out-of-range numeric stand-ins;
- interpolation or arbitrary middle-run gap filling;
- rewriting of detector samples, validity or serialized temporal history;
- a second/hidden temporal owner, lookahead authority inside S5-B, or retrospective authority inside D1–D5;
- circular proof in which prior-derived labels become the evidence that confirms the prior.

`RECOVERY` and any other numeric Oil judgment remain dependent on observed numeric Oil where that judgment requires a numeric boundary.

## Result and compatibility responsibility

Retrospective interpretation is persisted separately from original observed samples, with accepted/unresolved/conflict status and inference provenance. `tracking_data.csv` continues to preserve the detector's observed sample semantics; observed sample validity remains observed validity. Existing sessions/bundles without current-run confirmation retain their observed-only meaning and gain no synthetic confirmation authority.

Official result semantics must distinguish observed coverage from effective state-aware coverage when retrospective interpretation participates, and event/judgment evidence must record when inferred state affected official semantics. Bundles carrying retrospective official semantics use an explicit newer result/review semantics version while readers retain legacy v1 observed-only support. Older v1-only consumers must fail explicitly on newer retrospective semantics rather than silently presenting them as ordinary v1.

The versioned compatibility contract is authoritative; the physical artifact or field used to carry that version is an implementation decision unless another accepted owner establishes it.


## Implemented persistence and version shape

The implemented run-scoped confirmation lives only in `AnalysisSession.initial_state_confirmations`, keyed by Glass ID. Each confirmation snapshots the explicitly confirmed state together with `input_video_path` and `analysis_start_sec`; final readiness rejects a missing or mismatched snapshot. Recipe serialization is unchanged, and opening/replacing a video, changing analysis start or selected initial state, newly enabling a Glass, or establishing a fresh session invalidates or starts without confirmation as appropriate. GUI confirmation is an explicit analysis-start-frame action; CLI/headless `analyze` accepts only explicit repeatable `--initial-state-confirmation GLASS_ID=STATE` assertions matching the selected non-`AUTO` Recipe value and binds them to the current video/start context rather than deriving confirmation from Recipe persistence.

Bundles written with this responsibility use result/review semantics version **2**. `review_index.json` has `schema_version: 2` and `result_semantics_version: 2`, and `analysis_manifest.json` repeats the result semantics version plus a pointer to `retrospective_interpretation.json`. The separate retrospective artifact currently uses `schema_version: 1` and records the saved current-run confirmation provenance, per-Glass accepted/unresolved/conflict interpretation, evidence/interval provenance, and observed versus effective state-aware coverage. `session.json` carries the run confirmation snapshot; `tracking_data.csv` remains observed-only.

The reader treats legacy review-index v1 as result semantics v1 observed-only, supports the v2 shape above, and rejects unsupported or internally mismatched versions explicitly. Full-sequence re-detection may recompute only when the saved session contains current-run confirmation; legacy bundles without that confirmation remain observed-only. The extracted top/bottom entrance constants retain the pre-existing S5-B `0.32` / `0.68` topology boundaries and do not change detector thresholds or authority.
