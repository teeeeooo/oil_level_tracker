# Initial-State Retrospective FULL/EMPTY Reconstruction Architecture

## Purpose and authority

This document owns the durable sequence-level responsibility for **Initial-State
Retrospective FULL/EMPTY Reconstruction** on immutable detector result streams,
including R7/R8 streams. It is downstream of detector observations and upstream of official
event, judgment and state-aware report projection. Current sequencing remains
owned by the [roadmap](../00-project/roadmap.md) and
[work plan](../00-project/work-plan.md); implementation acceptance is owned by
the [dedicated validation contract](../30-validation/initial-state-retrospective-reconstruction-validation.md).

This responsibility does not modify S5-B current-frame evidence, the R8
Oil/state or Foam owners, final composition, or the serialized online temporal
owner. Those detector boundaries are authoritative in
[S5-B Oil Boundary Hypothesis Architecture](s5b-oil-boundary-hypothesis-architecture.md)
and [S11 Detector Responsibility Architecture](s11-detector-responsibility-architecture.md).
Historical D1–D5 routing is not a current authority surface.

## Placement and immutable observation boundary

The responsibility runs only after the analysis has collected its immutable observed `TrackingSample` sequence and before official event/judgment projection consumes any retrospective state interpretation.

R8 resolves only image-supported Oil/state inside the detector before
`TrackingSample` creation. A confirmed initial state is not detector evidence,
but the retrospective owner may later interpret the leading unresolved prefix
when anchor-grade direction proves a compatible transition. R8 retains the
historical `R7_OIL_ANCHOR` provenance flag for bundle compatibility; that
observation provenance therefore does not make this owner globally
`NOT_APPLICABLE`. A legacy stream explicitly carrying a prior-projected
`SEQUENCE_INITIAL_STATE_PRIOR` remains ineligible for a second projection.

- observed detector `fill_state`, validity, numeric Oil and Foam evidence remain historical observation and are never rewritten;
- retrospective FULL/EMPTY is a separate sequence interpretation with explicit status and provenance;
- no retrospective interpretation can manufacture a numeric Oil boundary, alter detector history, or become hidden state in the online temporal reducer;
- when downstream official semantics use retrospective interpretation, that use must remain explicitly attributable to retrospective provenance.

Legacy Oil compatibility uses the shared exact flag predicate in `domain/results.py`.
`R7_RESOLVED_OIL`, `R7_OIL_ANCHOR` or `R7_OIL_CONTINUATION` select the historical
anchor regime. Foam-only R7 flags do not. Modern streams keep canonical entrance
and hard-barrier checks, while actual legacy Oil retains its existing prefix
handling. [Compatibility design](s11-oil-compatibility-design.md) records scope.

## Initial authority and eligibility

A retrospective interval is eligible only when the current analysis run contains an explicit run/session-scoped user confirmation for the affected enabled Glass and that confirmed prior is `FULL_NO_INTERFACE` or `EMPTY_NO_INTERFACE`.

Persisted Recipe `initial_state` remains the selected prior, and the compatible Recipe schema continues to retain `AUTO`. Loading, copying or pre-populating that value does not prove current-run confirmation. `AUTO` is unresolved compatibility state, and an explicitly confirmed `UNKNOWN_REVIEW` may satisfy run readiness but grants no retrospective FULL/EMPTY authority. Other explicitly confirmed non-`AUTO` values keep their existing prior semantics but do not activate this responsibility.

Retrospective interpretation is limited to the **leading unresolved interval** before later direct sequence evidence establishes a defensible state trajectory. It is not a general gap-filling mechanism.

## Positive sequence evidence

Eligibility requires later real accepted detector evidence, not prior-seeded labels. The evidence set must materially establish the relevant numeric-boundary/topology/direction interpretation.

- direction evidence requires at least **two real accepted anchor-grade boundary
  observations** for R7/R8; legacy streams use their existing canonical boundary
  authority;
- on legacy R7 anchor streams the first anchor may already be mid-Glass;
  entrance topology is retained in provenance but does not block inference when
  anchor motion is compatible with the confirmed prior. Modern streams follow
  the [first-catch position guard](#modern-stream-first-catch-position-guard--2026-10-22)
  instead;
- prior-seeded or retrospectively interpreted state labels cannot serve as the sole confirmation of direction or topology;
- canonical ambiguity may remain inside an otherwise eligible leading prefix only when it introduces no barrier or contradiction, but ambiguity contributes no positive confirmation;
- insufficient positive evidence leaves the interval unresolved rather than converting the prior into truth.

## Barriers, contradiction and conflict

The leading prefix stops being retrospectively eligible when direct
image-supported state contradicts the confirmed prior or trusted Oil direction
is incompatible. Ordinary UNKNOWN, unavailable/decode-failure markers and
raw/rejected/pending Foam contribute no positive proof but do not erase the
explicit run-scoped initial context. They remain visible in observed data and
prevent any claim that the state was directly observed.

Direct contradictory sequence evidence overrides prior-based eligibility. A prior conflict yields **no retrospective interval**, a first-class conflict status and review requirement. A lack of enough confirming evidence without contradiction is **unresolved**, not conflict.

Malformed samples cannot contribute numeric or direction proof. Published Foam
does not confirm or contradict FULL/EMPTY by itself and grants no Oil/state
authority. A valid anchor-grade Oil observation may contribute direction even
when confirmed Foam coexists, while the Foam sample itself remains immutable and
is excluded from retrospective state projection.

## Modern-stream continuing-run rule — 2026-10-21

**Status: FROZEN 2026-10-21 before implementation (`67f1484`); IMPLEMENTED;
[local verification](../60-evidence/s11/2026-10-21-initial-state-report-local.md)**, with the user's decisions
recorded in the [Work Plan](../00-project/work-plan.md). It replaces the
two-observation direction test for modern (non-legacy-R7) streams. Legacy R7
anchor handling is unchanged. The
[first-catch position guard](#modern-stream-first-catch-position-guard--2026-10-22)
amends steps 4–6 from 2026-10-22.

**Why.** The ⑩ Windows BASE bundle shows two blocks, recorded in the
[report receipt](../60-evidence/s11/2026-10-21-top-exit-v3-local.md#report-and-judgment-receipt--2026-10-21):
- **Every UNKNOWN frame is a barrier.** The current resolver marks each such
  frame `R17_OBSERVATION_UNAVAILABLE`, and the barrier test matched the
  substring `UNAVAILABLE`. So the first frame stopped the interpretation.
- **The first two observations hardly moved.** They went Y363 → Y367 (4 px),
  below the 7.7 px tolerance, although the reviewed truth has a real drain from
  about 550 s.

**Rule:**
1. **Barriers.** These stay barriers:
   - hard-failure markers: the exact barrier flags, and any marker containing
     `UNAVAILABLE`, `FAILURE`, `FAILED`, `GLARE`, `FOG` or `DETECTION_LOST`;
   - published Foam without a numeric Oil boundary.

   The sequence resolvers' ordinary-UNKNOWN markers (`R6`/`R7`/`R16`/
   `R17_OBSERVATION_UNAVAILABLE` and `SEQUENCE_UNAVAILABLE`) are not barriers.
   A barrier before the first accepted boundary, or inside the run before a
   decision, leaves the interval UNRESOLVED.
2. **Run.** The run starts at the first accepted numeric boundary and continues
   through later accepted boundaries. Samples without one, such as UNKNOWN
   frames, are skipped. The run ends when consecutive accepted boundaries differ
   by more than the Glass's `temporal_max_jump_px`.
3. **Decisive move.** An accepted boundary is *beyond* when it differs from the
   first boundary by at least the existing direction tolerance:
   max(2 px, 1 % of the Glass diameter `2 × radius_y`). The first decisive move
   is two consecutive accepted boundaries beyond the tolerance on the same side.
4. **Decision.**
   - **Toward the prior's direction** (FULL: Y increases, the level falls;
     EMPTY: Y decreases, the level rises): ACCEPTED over the leading interval
     before the first accepted boundary, if that boundary passes the
     first-catch position guard; otherwise UNRESOLVED.
   - **Opposite:** CONFLICT, the existing meaning of incompatible trusted
     direction.
   - **No decisive move** before the run or the sequence ends: UNRESOLVED.

   Motion after the decision is not inspected, so a fall followed by a rise is
   still accepted.
5. **Unchanged:**
   - eligibility, the global contradiction scan and the all-missing hold;
   - NOT_APPLICABLE when the first sample already has a boundary;
   - no entrance-topology gate: topology stays provenance only (until
     2026-10-22; the first-catch position guard replaces this);
   - projection, event and judgment consumption, and RECOVERY's observed-only
     input.
6. **Provenance.** Interpretations decided by this rule record
   `initial_state_retrospective_v2`, and `initial_state_retrospective_v3` from
   the first-catch position guard on. The evidence is the first boundary plus
   the two decisive boundaries.

**Expected on ⑩ from the receipt (not a pass criterion):**
- **BASE: ACCEPTED.**
  - The first boundary is at 548.5 s (Y363).
  - The 565.5 s Y371 is beyond, but 566.0 s returns to Y363.
  - The decisive move is 567.5/568.0 s at Y374/375, downward.
  - The FULL prefix is 479.98–548.0 s, 137 rows.
  - Under `HOLD_ABOVE_ZERO`, judgment coverage becomes 553/601 = 92.0%. The
    level then decides.
- **Accum: UNRESOLVED.**
  - Five published-Foam rows precede the first boundary.
  - Separately, the first step (Y515 → Y482, 33 px) exceeds 32 px.
  - The reviewed truth has Oil entering from about 653 s, 16 s before the first
    boundary, so an EMPTY prefix to 669.5 s would have been wrong.

**Limit.** The Accum protection comes from the Foam barrier and the continuity
bound, not from the direction rule. A late first catch with neither would still
be accepted. The first-catch position guard below closes this for catches
outside the prior's entry region.

## Modern-stream first-catch position guard — 2026-10-22

**Status: FROZEN 2026-10-22 before implementation.** The user chose L2 from
[LCR-1](../50-diagnostics/s11/2026-10-22-reconstruction-late-catch-review.md#recommendation-l2)
on 2026-10-22. It amends the continuing-run rule above for modern streams only;
legacy R7 anchor handling is unchanged.

**Why.** The continuing-run rule accepts the prior over the whole leading
interval once the first decisive move points toward it, wherever the level was
first caught. So a level first caught after an unobserved transit still
reconstructs the prior up to the catch.
- **The error leans to PASS:** the prior is the compliant state of its hold
  rule (FULL under `HOLD_ABOVE_ZERO`, EMPTY under `HOLD_BELOW_ZERO`). Such a
  prefix inflates coverage and can hide a violation.
- **⑩ Accum:** the first catch (Y515, relative 0.787) lies inside the bottom
  band, 16 s after Oil began entering. Only a false entry Foam and a 33 px step
  (1 px over the limit) prevented a wrong EMPTY prefix.

**Rule.** When the first decisive move is toward the prior's direction, the
first accepted boundary y₀ is checked before ACCEPTED is returned. Its relative
position is the existing `boundary_relative_position` between the ellipse top
and bottom.
- **FULL:** relative ≤ 0.32 (`TOP_ENTRANCE_MAX_RELATIVE_POSITION`).
- **EMPTY:** relative ≥ 0.68 (`BOTTOM_ENTRANCE_MIN_RELATIVE_POSITION`), and y₀
  no more than `temporal_max_jump_px` above the effective-mask bottom,
  `center_y + radius_y × (1 − margin_ratio)`.
- **Otherwise: UNRESOLVED.** No interval is created. The reason names the first
  catch's position, and the evidence is the first boundary plus the decisive
  pair, as for CONFLICT.

**Why the asymmetry:**
- **FULL:** a full glass can show its level inside the top band. The user
  accepted FULL about 0.18 H below the top on BASE
  ([review-011](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#review-011-result--2026-10-21)),
  and D2 keeps FULL under the cap until a drain release. A catch there is the
  prior's own level.
- **EMPTY:** an empty glass shows no level. A level first seen more than one
  continuity step above the observable bottom must have been visible earlier.
- **No new threshold:** the step is the run's own continuity bound, the
  `temporal_max_jump_px` that already ends a run. The band caps it on small
  Glasses.

**Unchanged:**
- barriers, the run and the decisive move;
- CONFLICT, which is decided before position;
- NOT_APPLICABLE and the all-missing hold;
- legacy R7 streams, including their mid-Glass case;
- projection, event and judgment consumption, and RECOVERY's observed-only
  input.

**Provenance.** Every interpretation decided by the modern continuing-run rule
records `initial_state_retrospective_v3`, whether or not the guard acted.
Bundles written earlier keep v2.

**Expected, from the LCR-1 desk run (not a pass criterion):**
- **⑩ BASE:** ACCEPTED, unchanged (first catch Y363, relative 0.196).
- **⑩ Accum:** UNRESOLVED, unchanged (Foam barrier; the 33 px step).
- **The 24 kept local row lists:** status, interval, reason, barriers and
  evidence unchanged; continuing-run outcomes change provenance to v3.
- **Synthetic shapes:**
  - become UNRESOLVED: the Accum shape without Foam and with a 30 px first
    step, a standing EMPTY layer about 56 px up, a FULL catch 20 px below the
    band end and a FULL catch mid-Glass;
  - stay ACCEPTED: an EMPTY catch 10 px above the effective-mask bottom, and
    FULL emerging at the effective-mask top.

**Limits:**
- **Continuity:** the guard assumes the level moves at most one
  `temporal_max_jump_px` between samples. Where that is a large share of the
  height, the band does the capping.
- **Exclusions:** the guard does not read exclusion rectangles. An exclusion
  over the glass bottom raises the real observable bottom, which only makes
  the guard stricter (fails closed).
- **Inside the band:** a FULL catch inside the band after a slow unobserved
  fall is still accepted; the band is FULL precision under D2.
- **Accum 480–653 s:** still published UNKNOWN, not EMPTY. The guard cannot
  recover it; that needs onset evidence. The step-7 Windows request reads the
  Accum rows 640–672 s and the Accum geometry first.

## Non-authorities

This responsibility must not introduce:

- synthetic numeric Oil boundaries or out-of-range numeric stand-ins;
- interpolation or arbitrary middle-run gap filling;
- rewriting of detector samples, validity or serialized temporal history;
- a second/hidden temporal owner, lookahead authority inside S5-B, or
  retrospective authority inside the R8 Oil/state, Foam or composition owners;
- circular proof in which prior-derived labels become the evidence that confirms the prior.

`RECOVERY` and any other numeric Oil judgment remain dependent on observed numeric Oil where that judgment requires a numeric boundary.

R8 additionally permits a presentation-only hold when a current-run FULL/EMPTY
confirmation has no public Oil anywhere and no direct contradiction. It may draw
only a labeled graph/report background through analysis end. It creates no Oil
coordinate, does not alter observed coverage, and is not passed into event or
judgment evaluation. This all-missing hold is distinct from an anchor-backed
leading-prefix reconstruction whose inferred state can participate in official
state-aware semantics with provenance.

## Result and compatibility responsibility

Retrospective interpretation is persisted separately from original observed samples, with accepted/unresolved/conflict status and inference provenance. `tracking_data.csv` continues to preserve the detector's observed sample semantics; observed sample validity remains observed validity. Existing sessions/bundles without current-run confirmation retain their observed-only meaning and gain no synthetic confirmation authority.

Official result semantics must distinguish observed coverage from effective state-aware coverage when retrospective interpretation participates, and event/judgment evidence must record when inferred state affected official semantics. Bundles carrying retrospective official semantics use an explicit newer result/review semantics version while readers retain legacy v1 observed-only support. Older v1-only consumers must fail explicitly on newer retrospective semantics rather than silently presenting them as ordinary v1.

The versioned compatibility contract is authoritative; the physical artifact or field used to carry that version is an implementation decision unless another accepted owner establishes it.


## Implemented persistence and version shape

The implemented run-scoped confirmation lives only in `AnalysisSession.initial_state_confirmations`, keyed by Glass ID. Each confirmation snapshots the explicitly confirmed state together with `input_video_path` and `analysis_start_sec`; final readiness rejects a missing or mismatched snapshot. Recipe serialization is unchanged, and opening/replacing a video, changing analysis start or selected initial state, newly enabling a Glass, or establishing a fresh session invalidates or starts without confirmation as appropriate. GUI confirmation is an explicit analysis-start-frame action; CLI/headless `analyze` accepts only explicit repeatable `--initial-state-confirmation GLASS_ID=STATE` assertions matching the selected non-`AUTO` Recipe value and binds them to the current video/start context rather than deriving confirmation from Recipe persistence.

Bundles written with this responsibility use result/review semantics version **2**. `review_index.json` has `schema_version: 2` and `result_semantics_version: 2`, and `analysis_manifest.json` repeats the result semantics version plus a pointer to `retrospective_interpretation.json`. The separate retrospective artifact currently uses `schema_version: 1` and records the saved current-run confirmation provenance, per-Glass accepted/unresolved/conflict interpretation, evidence/interval provenance, and observed versus effective state-aware coverage. `session.json` carries the run confirmation snapshot; `tracking_data.csv` remains observed-only.

The reader treats legacy review-index v1 as result semantics v1 observed-only, supports the v2 shape above, and rejects unsupported or internally mismatched versions explicitly. Full-sequence re-detection may recompute only when the saved session contains current-run confirmation; legacy bundles without that confirmation remain observed-only. The extracted top/bottom entrance constants retain the pre-existing S5-B `0.32` / `0.68` topology boundaries for provenance and legacy interpretation. They do not gate a direction-compatible R7/R8 inference and do not change detector thresholds or authority. Since 2026-10-22 they also bound the modern [first-catch position guard](#modern-stream-first-catch-position-guard--2026-10-22).
