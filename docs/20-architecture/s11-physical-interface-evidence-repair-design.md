# S11 Physical Interface Evidence Repair Design

**Design status:** full physical-witness proposal remains unaccepted; the separately
bounded initial-FULL, cost-first and candidate RGB comparisons below are authorized
for exploratory implementation.
Revision naming and runtime promotion are not assigned
by this document. The [work plan](../00-project/work-plan.md) owns execution state.

[R22-2 native path diagnostics](s11-r22-2-interface-path-diagnostics-architecture.md)
extends R22-1 measurement extraction only. It does not implement the proposed
`OilInterfaceWitness` classifier, independent-support promotion, physical
association, handoff or direction-neutral observation described below. A
captured path is generator evidence, not a certified physical interface.

The [2026-09-17 R23 experiment](../50-diagnostics/s11/s11-r23-native-polarity-rejection.md)
was rejected and removed from production after protected public regressions.
Native gray-polarity inversion alone cannot classify replacement or break
association, even across three common sectors or only before confirmation.
The full witness and its paired acceptance controls below remain required.

The subsequent [detector direction assessment](../50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md)
confirms a bounded observation-layer redesign rather than a whole-detector
rewrite or more scalar-threshold tuning. The subordinate
[Interface Observability Witness Architecture](s11-interface-observability-witness-architecture.md)
owns the next trace-only extraction stage for item 1 below. It does not activate
independent support, association, handoff or direction-neutral phase behavior.

## Problem and chosen direction

The [reviewed R22 investigation](../50-diagnostics/s11/s11-r22-reviewed-interface-causal-findings.md)
identifies two different failures. A visible Accum boundary has an admitted
tracklet but cannot replace the allowed fill owner, while its independent
representation support is blocked by broad texture conflict. In BASE, a
candidate with reviewed location error and a boundary-aligned candidate share
one tracklet, creating an upward trajectory that fails the existing downward
release test. That association does not establish actual upward Oil motion.

The later human review narrows the BASE label: f14362 sector 2 Y437 is near
the interface but offset, so physical identity of that point is unresolved;
it is not a certified internal-structure negative. At f14386, sector 1 Y382
and sector 4 Y417 were separately confirmed near the interface. Scalar
candidate Y411.5 must not be imposed as exact truth across that curved path.
Future labels must separate localization mismatch from material/structure identity.

The design gives current-frame interface evidence an explicit, shared contract.
That evidence supports independent corroboration, physical association and
phase ownership. Motion remains a separate measurement over verified
associations. A visible interface may be observed without declaring drainage.

The design covers four changes, in this order:

1. Measure local interface structure and distinguish texture presence from
   contradictory internal structure; use this in independent corroboration.
2. Prevent uncertain physical associations from contributing direction,
   progress or confirmation evidence.
3. Replace fill-owner handoff's source-family privilege with current interface
   evidence and an explicit, bounded ownership transition.
4. Add a separately validated direction-neutral visible-interface phase for
   initial-FULL reacquisition and established-fill stabilization.

Items 1--3 must work before the full item-4 acceptance can be claimed. The October 15
comparison below isolates publication under existing evidence with false positives
explicitly allowed; it does not claim those stronger witnesses exist. None is a claim that all
reported Windows gaps will be repaired.

## October 15 initial-FULL observation comparison

The user prioritizes making BASE movement and uncertainty readable and accepts
false positives during the first Windows comparison. Implement a default-OFF
`initial_full_observation` option through the existing detector/resolver construction
and GUI launch path. The baseline and trial use one source version, one frozen
Recipe/ROI and identical run settings. Candidate generation, scores, association,
confirmation, drain thresholds and Foam owners are unchanged. Cost-first/RGB/Local XY
are separate later comparisons.

At an `INITIAL_FULL_BARRIER` frame only, after the ordinary direct/recovery routes,
the lifecycle may admit current rows already admitted by a bounded confirmed
tracklet, with at least continuation authority, compatible identity and strict
current/history material support. Version 2 reuses that existing confirmation for
continuation-only rows and for provisional witness frames already admitted within
the builder's bounded confirmation window. A provisional row without admission or
a confirmation profile still fails. LOST/TERMINATED rows remain ineligible.
Current no-interface state evidence, typed contradictions and
release ambiguity still block the route. The allowed set contains only these current
tracklets; the existing selector retains its competing-owner ambiguity check and
same-owner/explicit-handoff transition rules. No unconstrained OPEN or copied owner
history is introduced. Missing/unconfirmed/currently invalid rows cannot be carried.

This is a per-frame observation projection from the constrained initial-FULL motion
context, named `OBSERVED_INTERFACE`; it creates no new motion chain, lease or reseed.
Ordinary motion lifecycle and recovery diagnostics continue unchanged. A later
qualified downward release still takes its normal route. Closure/absence suppresses
observation immediately; an expired tracklet must qualify again through the existing
builder. Post-fill/refill barriers and initial EMPTY are outside this route.

Published trial observations use `PARTIAL_VISIBLE` and an explicit
`OIL_DIRECTION_UNCONFIRMED` flag, with the same-frame selected candidate's exact Y.
They must not be used to assert a drain-start event or a report direction summary.
The existing report observation note explains their uncertainty and false-positive risk.
Other samples retain their existing event semantics. Trace records the trial mode and actual observation
admission predicates separately from the unchanged failed drain predicates.
Detector version and GUI title identify trial use; normal launch remains baseline.

Existing anchor/phase flags admit some reviewed non-interface candidates, including
the D1 opposition. This comparison does not solve physical discrimination or satisfy
the full section-4 witness contract. Measure recoveries and false positives together;
neither more numeric values nor local mechanism tests establish field PASS.
The [validation supplement](../30-validation/s11-physical-interface-evidence-repair-validation.md#october-15-exploratory-comparison)
owns mechanical checks and the first Windows review.

### Version 2 admission correction

The [three-record Windows intake](../50-diagnostics/s11/2026-10-15-initial-full-comparison.md#three-record-predicate-intake)
identifies version 1's repeated anchor/direct-identity check as an additional
publication barrier, even after tracklet admission. Version 2 removes only that
duplicate requirement and the current-lifecycle confirmation delay. It does not
alter candidate authority, confirmation windows or phase motion transitions, and
does not make every UNKNOWN-start output available under initial FULL. The
existing material/identity vetoes and final publishability/ambiguity rules still
apply. Evaluations separate required predicates from descriptive authority,
phase identity, lifecycle and confirmation-profile values.

This intentionally widens an exploratory observation mode, including any false
identities already admitted by the existing tracklet builder. It is not a new
physical identity witness or a motion-only drain release. No pixels, coordinates,
timestamps or Glass IDs from the Windows reply enter production rules.
Version 1 remains reproducible at its pinned commit; version 2 is identified by
`+initial-full-observation-v2` in detector and resolver metadata. The launch option
and default OFF remain unchanged.

Top-exit FULL publication is a separate unresolved transition. The three raw
outcomes are boundary/ambiguous, so their FULL likelihood zero is a default rather
than positive no-interface evidence. This correction creates neither a FULL node
from that zero nor a FULL hold from an ordinary missing observation. Verify the
recovered topward owner against the actual refill before designing that transition.

## October 16 top-exit FULL closure

After all three individual Windows mechanisms were closed without adoption, the
user authorized this order: **④ v2 top-exit FULL closure, then investigation of
the non-interface output around 721 s**. The latter is not an identity fix to
bundle into this change. The optional `top_exit_full` constructor/GUI mode adds
`+top-exit-full-v1`; it defaults OFF and compares separately against unchanged
initial-FULL v2 with cost-first, RGB and Local XY OFF.

Reuse `OilPathLifecycleOwner`, after bounded selection and spike censorship but
before projection. This seam has the actual selected owner; the earlier material
phase loop sees several admitted hypotheses and cannot certify which one was
observed. This is a causal coordinate-free lifecycle decision, not a CSV/report
rewrite, a numeric interpolation, or a bypass of candidate admission. The closure
body lives in `oil_top_exit_full.close_top_exit_full`; the lifecycle owner calls
it at this seam with the existing policy and per-frame hard-unavailability. It
moved there on 2026-10-20 to restore the lifecycle/module size guards, and its
behavior is unchanged. Preserve
every selected numeric Oil node, including wrong identities still needing the
subsequent 721 s investigation.

Use a bounded window of consecutive same-owner selected observations. Reuse
existing confirmation count/window, jump, progress, material and direction
limits. Require mature admitted observations, a direct/ordered-lower anchor in
the window, strict current/history material clearance and actual upward source-Y
progress. The last measurement must reach the configured ellipse top within the
existing row-localization tolerance, not merely the broad entrance band. The
upper endpoint is a geometry assumption to check against the physical visible
Glass top on Windows; a crop/margin edge is not automatically that physical top.
Local mask inspection found the endpoint band outside the effective mask for both
retained Recipes. This candidate therefore has no demonstrated real-video positive
closure. Check Windows endpoint reachability from existing ④ inputs before a full
run; if it fails, resolve the geometry contract first instead of tuning the band.
No reviewed time, source Y or Glass identity enters the rule.

Only the immediately following usable frame with no phase-admitted Oil, no
current EMPTY evidence and no ambiguity/contradiction can confirm disappearance.
Ordinary mid-height loss, owner switches, static top structures, missing raster
quality, black/glare/unavailable frames and censored current Oil cannot close.
After confirmation, coordinate-free FULL may continue only through usable,
unopposed absence frames. Any new current interface, state contradiction or
unavailability ends that evidence episode; no stale resumption or owner transfer.
Missing observations before closure never receive a coordinate or retroactive FULL.

Record source frame/time/owner/Y for the bounded witness, actual predicates,
geometry boundary, reset reason and inferred-state origin. Keep raw current-image
FULL likelihood unchanged, including zero. `OIL_TOP_EXIT_FULL` distinguishes
this temporal evidence from `R17_IMAGE_SUPPORTED_STATE`; sample validity must
recognize the typed coordinate-free result without inventing an Oil measurement.
Foam still resolves independently afterward, so compare final composition as
well as its raw coordinates. This option can expose a mechanical transition but
does not establish physical identity or field acceptance.

## October 21 top-exit revision (v2)

**Status: FROZEN 2026-10-21 before implementation; IMPLEMENTED (default OFF);
[local controls PASS](../60-evidence/s11/2026-10-21-top-exit-v2-local.md);
[Windows ⑨ FAIL against the pre-registered outcome — NOT ADOPTED](../60-evidence/s11/2026-10-21-top-exit-v2-local.md#windows-top-exit-v2-comparison--2026-10-21).**
BASE FULL started at 663.0 s, on a refill blank frame with a reviewed visible
interface. The closure needed items 1 and 2, and item 4 held it. The
pre-registration below is unchanged. The
user chose item 6 = 6a and authorized implementation with the local controls
below. A Windows comparison needs a separate go. The
[predicate-check receipt](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#predicate-check-receipt--2026-10-21)
showed that only `independent_anchor` failed on ④. The user's decisions are
recorded in
[OTR-1](../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#decision-record--2026-10-21):
- D1: the ellipse is the Glass;
- D2: S with D2b persistence, failing closed per frame;
- D1b′ and revision items 1–5;
- item 3 = 3a; item 6 = 6a.

The rules, tests, controls and pass criteria below do not change after results.

v2 replaces v1's configured-top endpoint and its episode-ending rules. v1 keeps
its local evidence above; it was never run on Windows.

**Unchanged from v1:**
- **Seam:** `close_top_exit_full`, called from `OilPathLifecycleOwner` after
  bounded selection and spike censoring, before projection.
- **Switch:** the same `top_exit_full` / `--oil-top-exit-full` option, default
  OFF. The suffix becomes `+top-exit-full-v2`; v1 is replaced in place.
- **Output:** coordinate-free FULL with `OIL_TOP_EXIT_FULL`. The raw image FULL
  likelihood is untouched. Selection before closure is unchanged.
- **Scope:** Foam stays independent. The option cannot be combined with
  cost-first, RGB or Local XY. No new Recipe field, constant, time, Y or Glass
  identity enters the rule. T1–T8 and T10 are unchanged (D1b′ moves the endpoint
  only).

| Item | v1 | v2 | Reused quantity |
|---|---|---|---|
| 1. Endpoint (D1b′) | Last row within max(1, 0.012H) of the configured top | Last window row inside the top band: (y_last − top) / H ≤ 0.27 | `entrance_band_ratio` (T1, T7) |
| 2. Continuity | Any downward step resets the window | A downward step up to the reversal tolerance keeps it. Upward steps stay bounded by the maximum jump. Progress is still first to last row | `handoff_direction_reversal_tolerance_px` = max(1, 0.012H) |
| 3a. Unselected exit row | Any phase-admitted Oil at an unknown frame resets | The owner's publishable row may close the window (below) | Selector publishability, allowed set |
| 4. Ending (D2b) | Any admitted Oil, EMPTY, ambiguity or unusable frame ends the episode | Only DRAINING (a qualified T5 release) or EMPTY evidence ends it (below) | Material phase from the lifecycle |
| 6a. Anchor | One window row `ANCHOR_ELIGIBLE` with direct or ordered-lower identity | v1's rule, **or** the last window row's tracklet profile is `anchor_corridor` or `anchor_trajectory` and at least one window row is `direct_interface` or `ordered_lower_interface` | Tracklet confirmation profile |

**3a — the unselected exit row.**
- **Applies only** at a frame where the bounded path resolved unknown, the window
  is not empty, and the frame is usable, not EMPTY and not opposed.
- **The row:** the owner is the window's last tracklet. The frame's publishable
  layer must hold exactly one row of that owner, and the owner must be in the
  frame's allowed set (read from the phase diagnostics; an unconstrained frame
  allows it). The row passes the same per-row checks as a selected row
  and the continuity rule. The phase layer holds no other tracklet.
- **Bounds:**
  - it only extends a window of selected rows; it never seeds one;
  - at most one unselected row per window, as its last row, so the next frame
    must be the disappearance.

  This follows OTR-1 S5: the miss sits in the exit frame itself.
- **Output:** the witness marks the row `selected: false`, with source, Y and row
  ID. Its value is never published; that frame stays UNKNOWN.

**4 — the FULL episode after confirmation (D2b).**
- **FULL holds.** Each later frame publishes coordinate-free FULL while the
  material phase is not DRAINING and EMPTY evidence is clear. This includes
  frames where the selector chose Oil, such as IFO v2 exposures of the 721 s
  class; those rows are not published.
- **Fail closed per frame (confirmed by the user, 2026-10-21).** An unusable or
  opposed frame publishes UNKNOWN without ending the episode.
- **End.** DRAINING (`DRAIN_RELEASE_CONFIRMED` or a recovery release; read from
  the lifecycle's material phase before top-exit rewrites it) or EMPTY evidence
  ends the episode. It cannot resume, and normal selection continues.
- **Risk.** A real drain that the lifecycle does not release would stay FULL.
  On ④ the lifecycle stayed in `INITIAL_FULL_BARRIER` in every sampled window.
  The reviewed interval ends at 780 s, so it does not score this.

**Tests (synthetic, unit).**

| Kind | Case | Expected |
|---|---|---|
| Positive | ④ shape: rising owner rows with one anchor row, a lag step within tolerance, a last unselected publishable row at an unknown frame, then disappearance | FULL from the disappearance frame; the witness names the unselected row |
| Positive | Last row inside the band, not at the top | FULL. v1's "broad entrance is not top exit" case flips |
| Positive | After closure, an IFO exposure is selected as Oil; later DRAINING | FULL through the exposure; Oil after DRAINING; no resumption |
| Positive | Unusable frame inside the episode | That frame UNKNOWN; FULL on the next frames |
| Negative | Last row below the band | No FULL |
| Negative | Downward step above the tolerance | Window resets |
| Negative | Unselected row of another tracklet; two publishable rows of the owner; another admitted tracklet in the frame | Reset |
| Negative | Unselected row as the window seed; two unselected rows; an unselected row followed by an owner row | No FULL |
| Negative | EMPTY evidence inside the episode | Episode ends; no resumption |
| Kept | v1 negatives: mid-Glass loss, stationary, downward, switch, provisional, opposed, competitor, bad disappearance frame, prior-only, ordering invariance, stacking ban, Foam composition | Unchanged |

Rewritten v1 cases:
- "reversal before loss" uses a reversal above the tolerance;
- "unavailable frame ends the episode" becomes a per-frame UNKNOWN;
- "new numeric interface ends FULL" becomes FULL until DRAINING, plus a release
  case.

**Local controls.** Production path through the existing
`tests.diagnostics.s11_initial_full_comparison --top-exit-comparison` entry: IFO v2
in both arms, top-exit v2 ON against OFF, 2 fps, the qualification windows, debug
NONE, in one managed run. The entry gains sample2, an original-Recipe option for
sample4 and an UNKNOWN initial-state option; nothing else in it changes.

| Input | Initial state | Truth | Pass |
|---|---|---|---|
| sample4, original Recipe, 0–56 s | UNKNOWN (qualification state) | Never FULL | Zero top-exit FULL rows, in particular none at 54.5–56 s (G) |
| sample4, October 15 interior Recipe | FULL (stress, as on October 16) | Never FULL | Zero top-exit FULL rows |
| base_sample_1, original Recipe | FULL (stress, as on October 16) | No FULL | Zero top-exit FULL rows |
| sample2, original Recipe, 0–2 s | FULL (stress) | Full-like, no interface, no rise | Zero top-exit FULL rows (prior-only FULL is forbidden) |

In every control the raw inputs and all rows must match ON and OFF exactly; with
zero closures that is the whole output. Any failing control stops the work;
nothing is retuned.

**Windows (needs a separate go).** One comparison on ④'s inputs: ④ v2 against
④ v2 + top-exit v2. Pre-registered:
- **BASE:**
  - FULL starts within 672–675 s; 673.5 s is expected;
  - no FULL before 672 s;
  - FULL holds through 675–780 s with no numeric Oil row.
- **Accum:** zero top-exit FULL rows; the truth has no FULL.
- **Both Glasses:** rows before closure are identical.

Failure is any of: FULL before 672 s or in Accum; a changed row before closure;
or FULL ending inside 675–780 s.

## October 21 top-exit revision (v3)

**Status: FROZEN 2026-10-21 before implementation (`e88d387`); IMPLEMENTED
(default OFF); [local controls PASS](../60-evidence/s11/2026-10-21-top-exit-v3-local.md);
[Windows ⑩ PASS against the pre-registered outcome](../60-evidence/s11/2026-10-21-top-exit-v3-local.md#windows-top-exit-v3-comparison--2026-10-21)
(BASE FULL from 674.0 s; not promoted; see the
[promotion preparation](#october-22-top-exit-promotion-preparation)).** After the
[⑨ FAIL](../60-evidence/s11/2026-10-21-top-exit-v2-local.md#windows-top-exit-v2-comparison--2026-10-21)
the user chose option B: v2 plus a disappearance confirmed by the next frame.
The rules, tests, controls and pass criteria below do not change after results.
A Windows ⑩ comparison follows only after the local controls pass.

**What ⑨ showed:**
- **Where it closed:** v2 closed on a single blank frame mid-refill (f15896,
  663.0 s).
- **What review-004 sees there:** a visible interface. The candidates were
  excluded as admitted-0 `INCOMPATIBLE_BRANCH`.
- **The next frame:** at 663.5 s, ④ selected Oil again (Y418, an accepted
  alternative).
- **Why:** v2 treats one frame without an admitted Oil row as an exit.

**Unchanged from v2:**
- **Items:** 1 (band endpoint), 2 (lag continuity), 3a (unselected exit row),
  4 (D2b episode) and 6a (anchor), together with the seam, switch, output and
  scope.
- **Selection:** numeric selection before closure is unchanged.
- **Suffix:** becomes `+top-exit-full-v3`; v2 is replaced in place.

**7. Confirmed disappearance (new).**
- **Disappearance frame d.** When every v2 predicate passes, the closure is only
  *pending*:
  - frame d keeps its resolved node, which is unknown, exactly as in v2's
    baseline;
  - its record shows `TOP_EXIT_FULL_PENDING` with the witness, predicates and
    `anchor_source`.
- **Confirming frame d + 1.** The closure is confirmed only if d + 1 passes all
  of these checks:
  - bounded gap from d (0 < dt ≤ the witness's maximum gap);
  - usable raster;
  - EMPTY clear;
  - not opposed;
  - no current interface (no phase-admitted Oil row);
  - resolved node unknown;
  - material phase not DRAINING.

  These are the disappearance-frame conditions applied once more, plus the D2b
  episode-end conditions.
- **On confirmation:**
  - FULL starts at d + 1 with `TOP_EXIT_FULL_CONFIRMED`; frame d stays UNKNOWN;
  - nothing is back-filled;
  - the episode then follows item 4 unchanged.
- **On cancellation:**
  - any failed check cancels the pending closure (`confirmation = CANCELLED`);
  - frame d + 1 is then processed as an ordinary frame; the witness was already
    cleared at d, so a selected Oil row at d + 1 starts a new witness.
- **No pending at the last frame.** A pending closure on the last frame never
  becomes FULL.
- **No new quantity.** Item 7 adds no threshold, constant, time, Y or Glass
  identity. "One frame" is the smallest confirmation: the next frame must say
  the same thing.

**Diagnostics:**
- `version: v3` and `confirmation` (`PENDING`, `CONFIRMED` or `CANCELLED`).
- `confirmation_predicates` on frame d + 1.
- `disappearance_frame_index` and `confirmation_frame_index` in the closure
  copied into every episode record.

**Expected on ④ from existing receipts (not a pass criterion):**
- **663.0 s:** pending. At 663.5 s ④ selects Oil, so the closure is cancelled.
- **663.5–673.0 s:** no evaluation. ④ has Oil on every row through 672.5 s, and
  673.0 s holds the unselected 0319 row (a current interface).
- **673.5 s:** pending, if the v2 predicates pass as the predicate check
  predicts.
- **674.0 s:** confirmed. ⑨'s Table Q shows that 674.0 s is usable, unopposed,
  not EMPTY and without a current interface. FULL then starts at 674.0 s.
- **675–780 s:** the episode should match ⑨, with the same frame gaps and the
  same end conditions.

**Known limits:**
- **Longer blanks still close.** A blank of two or more frames inside the band,
  after a qualifying witness, still closes.
- **673.5 s is unproven on a run.** The closure there rests on stored values and
  two inferences.
- **The upstream exclusion stays.** The `INCOMPATIBLE_BRANCH` exclusion at
  663.0 s is not repaired (option C); f15896 stays UNKNOWN.

**Tests (synthetic, unit).**

| Kind | Case | Expected |
|---|---|---|
| Rewritten | Every v2 positive (selected rise, band endpoints, lag step, ④-shaped unselected exit row, drain release, lower interface) | FULL from the confirming frame; the disappearance frame stays UNKNOWN; the record there says `TOP_EXIT_FULL_PENDING` |
| Rewritten | Unusable or EMPTY frame inside the episode | Moved one frame later, so it falls inside a confirmed episode; same expectations as v2 |
| New negative | ⑨ shape: a witness into the band, one blank frame, then the selected interface again | No FULL; numeric output equal to OFF; `confirmation = CANCELLED` on the reappearing frame |
| New negative | Bad confirming frame: unavailable or fogged, black raster, EMPTY, time gap, a current Oil row | No FULL |
| New negative | Pending on the last frame | No FULL |
| New positive | ④ shape: a cancelled pending, a continued rise, then a real exit | FULL only from the second exit's confirming frame; earlier rows equal to OFF |
| Kept | All other v2 cases | Unchanged |

**Local controls.** These are the same four controls, entry, settings and pass
criteria as v2, in a new managed run: sample4 original/UNKNOWN, sample4
interior/FULL, base_sample_1/FULL and sample2/FULL. Each must show zero top-exit
FULL rows, and raw inputs and all rows must match ON and OFF. Item 7 can only
remove closures, so v2's zero is expected. Any failing control stops the work.

**Windows ⑩ (after local PASS; the user forwards the request).** One comparison
on ④'s inputs: ④ v2 against ④ v2 + top-exit v3. The criteria are unchanged
from ⑨:
- **BASE:**
  - FULL starts within 672–675 s; 674.0 s is expected;
  - no FULL before 672 s;
  - FULL holds through 675–780 s with no numeric Oil row.
- **Accum:** zero top-exit FULL rows.
- **Both Glasses:** rows before closure are identical.

Failure is any of: FULL before 672 s or in Accum; a changed row before closure;
or FULL ending inside 675–780 s.

The request also asks for these diagnostics:
- the records at 663.0 and 663.5 s (pending, then cancelled);
- 673.5 s: pending, with its witness and false predicates;
- 674.0 s: confirmed.

They explain a failure; they are not extra pass criteria.

## October 22 top-exit promotion preparation

**Status: PREPARATION (user decision 2026-10-22).** v3's rules, tests and
default OFF are unchanged.

**SPL#4 BASE truth corrected (user, 2026-10-27).** Review-015 shows the
timeline's "FULL at 24–25 s" was Foam at the top. Review-016 places the
Oil FULL onset at 27.5 s. The correction is recorded in the
[acceptance owner](../30-validation/s11-physical-interface-evidence-repair-validation.md#top-exit-v3-promotion-acceptance--2026-10-22);
it changes no design or criterion. The [Work Plan](../00-project/work-plan.md) owns the
promotion state; this section defines what a promotion would consist of.

**Promotion unit:** the pair `initial_full_observation=True` +
`top_exit_full=True` (`+initial-full-observation-v2+top-exit-full-v3`).
- **Tested only as a pair:** top-exit has run only with IFO v2 ON (④, ⑨, ⑩ and
  the local controls).
- **IFO v2 is narrow:** it evaluates only on a Glass with a confirmed initial
  FULL that is still in `INITIAL_FULL_BARRIER`. On any other Glass top-exit
  acts alone.

**Two stages:**
1. **Integrated candidate (decided):** the pair is the FULL lifecycle component
   of the WP09 integrated candidate configuration. No default or runtime
   behavior changes.
2. **Production default (pending):** only after the
   [promotion acceptance](../30-validation/s11-physical-interface-evidence-repair-validation.md#top-exit-v3-promotion-acceptance--2026-10-22)
   passes and the user decides.

**Why ⑩ is not enough for the default:**
- **⑩ is the design case.** Every v3 rule was chosen on SPL#1 BASE 660–675 s:
  - item 1 from review-011;
  - item 2 from the 350→352 step;
  - 3a from the 673.0 s receipt;
  - 6a from the predicate check;
  - item 7 from the ⑨ failure.

  ⑩ kept its pre-registration, but it tests the case the rules were fitted to.
  An unseen positive is required (overfitting risk).
- **One confirmed path:** the only confirmed closure used the 6a anchor, the 3a
  exit row and next-frame confirmation. A window-row anchor reached only a
  cancelled pending (663.0 s).
- **No real-video negative:** none of the four local controls reached a
  disappearance evaluation.
- **Untested risks:** a blank of two or more frames inside the band, and the
  release after a top-exit FULL (`OIL-PHASE-DRAIN`, F08). Under D2b a false FULL
  persists until a release.
- **Wider effect:** since `139ba87`, FULL rows count toward judgment coverage
  and show as `FULL 판정` bands. A default change alters official results for
  every run with a fill.

**Not part of this preparation:** any rule change or tuning, the 27 % cap
(LBT-1 outcome G) and option C.

## October 22 contested fill-owner gate

**Status: FROZEN 2026-10-22 before implementation (`8386b45`); IMPLEMENTED
2026-10-22 (`2cb0b52`, opt-in, default OFF);
[local checks PASS](../60-evidence/s11/2026-10-22-fill-owner-contest-local.md).**
[Windows comparison PASS](../60-evidence/s11/2026-10-23-step7-windows-receipt.md#spl4-gate-comparison)
(2026-10-23): SPL#4 BASE loses exactly its 14 wrong-target rows and Accum one
false EMPTY sample; SPL#1 is unchanged. Promotion HELD (user, 2026-10-23): "승격 보류 -> 얻는거 잃는게 비슷한 수준으로 보임". The gate stays opt-in, default OFF. This is the (나)
half of step 6 in the Mac-only order of the
[Work Plan](../00-project/work-plan.md). The user moved it ahead of E3 and B
after [DSR-1](../50-diagnostics/s11/2026-10-22-d-scope-review.md#recommendation).
It replaces DSR-1 option 1's wording ("a fill owner keeps ownership only while
it follows the level"), for the reason below.

**User decisions (2026-10-22):**
- **Rule:** adopt this gate in place of motion validity.
- **Activation:** opt-in, default OFF, as proposed below.
- **sample7 target:** 0016's published Y is correct. The line where 0006/0013
  ran is the same surface. The video is shot slightly from above, so the milk
  surface shows as an ellipse: 0016 follows its front arc, 0006/0013 its back
  arc. The user checked 0016 at 21.5, 25.0 and 31.5 s; the rows between follow
  the same tracklet (inference).
- **Product geometry:** product videos are mostly shot head-on, like local
  sample4 (a round sight glass), where the surface shows as a line.
- **Cost accepted:** the gate removes sample7's 20 correct rows (below), on the
  ground that such arc pairs should be rare in head-on product videos.

### What the kept readouts show

A desk reading of the kept [FOA-1](../50-diagnostics/s11/2026-10-22-fill-owner-ambiguity-local.md)
readouts (closed managed run `s11-fill-owner-contest-desk-20261022-001`; no
detector run).

- **Motion does not separate the owners.**
  - **Method:** each owner's recent trajectory is rebuilt over six frames and
    tested with the existing R21 topward predicate (upward, agreement ≥ 0.60,
    progress ≥ max(4, 0.025 H)).
  - **Result:** the lower owners pass about as often as the upper ones. They
    rise in parallel, below them.

    | Video | Lower owners pass | Upper owners pass | Lower owners sit |
    |---|---:|---:|---|
    | sample5 | 40 of 61 frames | 12 of 17 frames | 140–270 px below the surface, in the bubbly water |
    | sample7 | 26 of 33 frames | 11 of 16 frames | 50–85 px below the upper owners: the front arc of the same surface (user) |

  - **Exception:** only sample5 0004 is mostly stationary (4 of 10).
  - **What stands from FOA-1:** its source reading. A continuing row carries
    its confirmation witness's direction, net progress and agreement for the
    tracklet's whole life.
  - **What does not:** "stopped following the level" fits 0004 only. The other
    sample5 owners follow another rising boundary inside the water.
  - **So:** a rule that keeps ownership only while the owner rises would keep
    most wrong owners.
- **Two lifecycle paths publish the wrong rows.** Both are verified in source.
  - **Win by attrition (main path).**
    - `FILL_OWNER_AMBIGUOUS` keeps every contested chain. By contrast,
      `FILL_COMPLETION_AMBIGUOUS`, `FILL_CHAIN_AMBIGUOUS` and
      `FILL_PHASE_REENTRY_AMBIGUOUS` drop the chains they cannot separate.
    - When the other owners age out, the survivor becomes the single
      `FILL_MOTION_OWNER`, replaces the established fill and publishes.

    | Recording | Rows from this path | Status |
    |---|---|---|
    | sample5 | 17 of the 21 wrong rows: 20.0 s, 36.0 s, 40.5–44.0 s and 46.0–50.5 s (via 0064's handoff successor 0106) | Agent-checked against the surface estimates |
    | sample7 | all 20 rows of 0016, 22.0–31.5 s | Correct (user): the front arc of the same surface |
    | SPL#4 | the re-adopted low owner 0018 (14 rows) fits this path | Confirmed on Windows (2026-10-23): gated as contested with 0035 |

  - **Fresh low start.** After a fill is established, a new chain from the
    lower entrance band becomes the owner although it lies far below the
    established level. sample5 24.5–25.5 s and 54.0–54.5 s: 4 rows, 193–226 px
    below. This design does not address it.

### Rule

A tracklet that shared a fill-owner ambiguity cannot become the publishing fill
owner by outlasting the others.

1. **Mark.** Every tracklet in the dynamic-owner set of a `FILL_OWNER_AMBIGUOUS`
   frame is contested. A tracklet whose current fill chain lists a contested
   tracklet (a handoff successor) is contested too.
2. **Gate.** The gate applies in OPEN or FILLING when both hold:
   - the lifecycle would allow one fill owner (`FILL_MOTION_OWNER`,
     `FILL_PHASE_REENTRY`, `FILL_CURRENT_ANCHOR_HANDOFF`, or the single owner
     under `FILL_CHAIN_AMBIGUOUS`);
   - that tracklet or its owner chain is contested.

   Then:
   - the allowed set and the owner chain become empty;
   - the reason becomes `FILL_OWNER_CONTESTED`;
   - the frame counts as ambiguous, like `FILL_OWNER_AMBIGUOUS`;
   - the fill-onset intent does not rewrite earlier frames for that owner.
3. **No state change.** Chains, the established fill, the ownerless barrier and
   the release, re-entry and recovery evaluations all evolve exactly as
   without the gate. Only the frame decision differs. The selector, projection
   and publication consume it unchanged.
4. **End.** The marks clear when the phase becomes `FILLED_BARRIER` or
   `DRAINING`. Fill-span completion (`FILL_SPAN_CONFIRMED`) and drain releases
   are not gated.

**Why:** while two dynamic fill owners coexist, the lifecycle has no evidence of
which one is the fill surface. The others ageing out is not such evidence: the
tracker can lose the true level as easily as a structure (sample5 0011 in a
turbulent rise). The rule applies existing no-repeat rules to a path they missed:
- `S11-F04`: ambiguous splits, merges and stale aliases terminate or abstain;
- `S11-F08`: no release on an ambiguous row;
- [section 3](#3-established-fill-owner-transfer): a still-valid competing
  owner gives UNKNOWN.

**sample7 is a false ambiguity.** Its two owners were the front and back arcs
of one obliquely viewed surface. Counting them as two fill owners breaks an
existing rule (`S11-F07`: do not count projected arcs as independent
interfaces). The lifecycle has no view-geometry input to recognise such a pair.
The gate therefore cannot tell sample7's correct survivor from sample5's wrong
ones.

**What it does not do:**
- It adds no numeric Oil. It only empties allowed sets.
- It does not mark owners on a chain-handoff ambiguity (`FILL_CHAIN_AMBIGUOUS`);
  no local recording shows a win after one.
- It does not find the true level. Under an EMPTY initial state an admitted
  level that started mid-Glass still cannot own the fill (sample5 0059/0060).
- The fresh low start remains (4 sample5 rows).
- Fast-fill FULL ((가), SPL#4) is unaffected.
- **Cost:** a true level that survives a contest also goes UNKNOWN until the
  episode ends. Locally the gate removes 17 wrong sample5 rows and 20 correct
  sample7 rows. The Windows check therefore reads every changed row.

**Activation:** an opt-in comparison, default OFF.
- **Path:** GUI `--oil-fill-owner-contest` → the existing detector factory →
  `OpenCvPhaseDetector` → `ObservationSequenceResolver` →
  `OilObservationResolverConfig` → `OilMaterialPhasePolicy` →
  `OilMaterialPhaseLifecycleOwner`.
- **Version suffix:** `+fill-owner-contest-v1`. The frame diagnostics gain the
  contested IDs only when the option is ON.
- **Combinations:** combinable with IFO v2 and top-exit v3, so the reference can
  be the WP09 integrated candidate. Refused with cost-first, candidate RGB and
  Local XY, as top-exit is.
- **Default:** production is unchanged until a Windows comparison and the
  user's decision.

**Checks:** the [contested fill-owner gate checks](../30-validation/s11-physical-interface-evidence-repair-validation.md#contested-fill-owner-gate-checks--2026-10-22)
fix the local controls, the predictions and the stop conditions before any run.

## October 27 co-located fill owners (E4)

**Status: APPROVED 2026-10-27 as drafted (user: "일단 구현은 이대로 진행해보자"); frozen before code; IMPLEMENTED 2026-10-27 at `9ee11a4` (opt-in, default OFF); [local checks](../60-evidence/s11/2026-10-27-fill-owner-colocation-local.md) FAIL on a frozen stop condition (sample5 events outside the predicted frames); the user accepted those changes and queued the Windows SPL#4 comparison ("1번으로 진행하자. 범위 밖 변경이지만 오히려 신뢰도가 올라가는 변경으로 생각됨").** The
first step of the order the user chose after the
[partition desk review](../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#partition-demotion-desk-review--2026-10-27):
"결국 E3까지 가긴해야되는데 하나씩 짚어보자는거네. 추천 순서대로 진행하자"
(E4 → E2 → E1 → E3).

**Problem (review-015).** On SPL#4 BASE at 22.5–24.0 s, the two dynamic fill
owners 0018 and 0035 are both on the reviewed level. Every owner row is within
1.0–28.5 px of the mark. `FILL_OWNER_AMBIGUOUS` still empties the allowed set,
so frames that any owner would have answered correctly publish UNKNOWN.

### Rule

1. **Co-located owners.** In a frame where the lifecycle would report
   `FILL_OWNER_AMBIGUOUS` (more than one dynamic fill owner, no chain
   ambiguity), the owners are co-located when both hold:
   - every dynamic owner has at least one observed row in the frame;
   - all those rows lie within one association step of each other:
     max(row Y) − min(row Y) ≤ `maximum_jump_px`. That is the Recipe's
     `temporal_max_jump_px`, 32 px on SPL#4.
2. **Decision.** For co-located owners:
   - the allowed set is the dynamic-owner set and the phase stays FILLING;
   - the reason is `FILL_OWNER_COLOCATED`;
   - the frame is not counted as ambiguous;
   - the selector chooses among the owners' rows as it chooses among any
     allowed set.
3. **No state change.** Chains, the established fill, the onset intent, the
   ownerless barrier and every release, re-entry and recovery evaluation evolve
   exactly as they do under `FILL_OWNER_AMBIGUOUS`. Only the frame's allowed
   set, reason and ambiguity flag differ.
4. **Contest marks.** A co-located frame is not an ambiguity, so it adds no
   mark for the contested fill-owner gate when that option is ON.

**Why:**
- The ambiguity rule exists because the lifecycle cannot tell which of two
  owners is the fill surface.
- When both owners are observed in the same frame within one association
  step, any choice is within the tolerance the tracklet layer already uses for
  one surface.
- A missing row is not co-location. On SPL#4 at 24.0 s, 0035 has no row; at
  24.5–27.0 s only one owner has a row while the level is far above. Those
  frames stay ambiguous.

**What it does not do:**
- It does not merge chains or choose a fill owner for later frames.
- It does not find the level above two low owners.
- It does not change any tracklet, authority or association.
- **sample7's arc pair is not affected.** Its owners are 50–85 px apart,
  beyond one step.
- **Its risk is two low owners within one step of each other.** Releasing
  them would publish a low row. The local check reads every released frame
  against the surface estimates.

**Desk prediction from kept readouts** (FOR-1 runs, no detector run):
- **sample5:** 3 of 48 ambiguous frames are co-located: 9.5, 10.0 and 11.0 s.
  - Owner rows span 22–28 px.
  - At 9.5 and 10.0 s they lie around the agent surface estimate.
  - At 11.0 s they lie 24.5–52.5 px below it, so the outcome depends on the
    selector's choice.
- **sample7:** 0 of 24.
- **SPL#4** (step-12 rows):
  - 23.0 and 23.5 s are co-located; their owner candidates span 24 px and
    lie within 32 px of the review-015 marks.
  - 22.5 s is not co-located (span ≥ 37.5 px); 24.0 s is not (0035 has no
    row).
  - 24.5–27.0 s are not (one owner row each).

**Activation:** opt-in, default OFF, wired like the contested gate.
- **Path:** GUI `--oil-fill-owner-colocation` → the existing detector factory →
  `OpenCvPhaseDetector` → `ObservationSequenceResolver` →
  `OilObservationResolverConfig` → `OilMaterialPhasePolicy` →
  `OilMaterialPhaseLifecycleOwner`.
- **Version suffix:** `+fill-owner-colocation-v1`.
- **Combinations:** combinable with IFO v2, top-exit v3 and the contested
  gate. Refused with cost-first, candidate RGB and Local XY.
- **Checks:** [frozen with this draft](../30-validation/s11-physical-interface-evidence-repair-validation.md#co-located-fill-owner-checks--2026-10-27).

## October 23 fast-rise association

**Status: FROZEN 2026-10-23 before implementation; IMPLEMENTED 2026-10-23 (`4f0665b`,
opt-in, default OFF); [local checks FAIL](../60-evidence/s11/2026-10-23-fast-rise-local.md):
F1/F4 pass (no change), F2/F3 fail (no seed fired on the stand-ins). Not adopted.** The user approved the
draft and its checks ("1. 동의함 대체로 빠른 배출은 저정도 속도보다는 느림 /
2. 로컬 구현 먼저 동의함"). Fast drains are usually slower than this, so
upward only stands. Local implementation comes first; the Windows readout and
the SPL#4 run come later.
This is option 2 of [FFF-1](../50-diagnostics/s11/2026-10-23-fast-fill-full-review.md),
chosen by the user, after the
[local cause check](../50-diagnostics/s11/2026-10-23-fast-fill-full-review.md#local-cause-check-result--2026-10-23)
confirmed the mechanism.

### Problem

`DirectedInterfaceTrackletBuilder._match_cost` refuses any pair with
|Δy| > `maximum_jump_px` × gap. The cap is the Recipe `temporal_max_jump_px`,
32 px per sample.
- **Why fast rises fail:** a level that rises faster than the cap per sample
  starts a new single-row tracklet on every frame. None of them gains the 3
  observations and the net progress that admission needs, so the level never
  becomes an owner. FULL then has no owner to close on.
- **What the cap protects:** it is also what keeps nearby components apart
  (`S11-F04`). A cap of 9 px breaks sample7 on froth jitter alone. At 1 fps,
  sample5 shows a stale low owner publishing 20–105 px below the level.
- **What a fix must do:** it cannot simply widen the cap. It must accept
  beyond-cap motion only when that motion is a consistent fast rise of one
  physical row.

### Rule

There are two parts, both inside `OIL-TRACKLET`, and both only for upward
motion (source Y decreasing), the fill direction FFF-1 addresses.

**1. Fast-rise seed.** It runs after the normal assignment of frame t, on
leftovers only.
- **Inputs:**
  - an unassigned row hypothesis h(t);
  - an active tracklet A whose only observation is a row h(t−2);
  - an active tracklet B whose only observation is a row h(t−1).
  - A and B must both be unassigned in frame t.
- **The steps:** s1 = y(t−1) − y(t−2) and s2 = y(t) − y(t−1).
- **A seed needs all of the following:**
  - **Beyond the cap, upward:** both steps are upward and exceed
    `maximum_jump_px`. Any motion the current cap admits is therefore
    untouched.
  - **Bounded:** each step is at most 3 × `maximum_jump_px`. This is the only
    new constant. The SPL#4 inference is about 2.2× and sample5 at 0.5 fps
    about 2.3×.
  - **Constant velocity:** |s2 − s1| ≤ `row_hypothesis_tolerance_px`.
  - **Independent same-frame witness on all three rows:** the existing
    `_representation_bridge` independent-witness predicate. That is an
    anchor-eligible member, a physical proposal, and registered motion support
    and coverage at or above the confirmation minima (0.50).
  - **Same representation:** the three rows share a representation class.
  - **Unique:** no other (A, B, h) combination in frame t qualifies with
    any of these three rows. Otherwise there is no seed (fail closed).
- **Result:**
  - A takes the rows of B and h(t), giving three observations, and gets the
    fast-rise mark.
  - B is dropped. It was a single-row provisional tracklet; no identity
    existed beyond it.
  - Admission then runs the existing confirmation unchanged: observations,
    progress, direction and motion or anchors.

**2. Fast-rise continuation.** It applies to a marked tracklet in later
frames.
- **What changes:** `_match_cost` skips the absolute |Δy| gate for an upward
  step.
- **What stays:**
  - the velocity-prediction gate, |y − (last + v × gap)| ≤ `maximum_jump_px`;
  - the representation check;
  - lost frames;
  - ambiguity termination.
- **Bound and cost:** the step is still at most 3 × `maximum_jump_px` × gap.
  The cost's position term is normalised by max(`maximum_jump_px`, |v|) ×
  gap.
- **End of the mark:** it clears once |v| ≤ `maximum_jump_px`, and the
  tracklet then matches as today.
  - A level that stops at the top, or disappears into FULL, fails the
    prediction gate and the tracklet is lost.
  - That loss is the disappearance top-exit already closes on.

**Provenance:** every observation is an existing same-frame row hypothesis.
Nothing is interpolated, carried or created from motion. The output only
changes which tracklet a row belongs to.

### Difference from prior failures

- **`S11-F03`, motion promoted to identity.** Motion never produces a row or
  a coordinate. It is one of four same-frame conditions on three physical rows,
  together with an anchor-eligible member, a physical proposal and a shared
  representation.
- **`S11-F04`, geometry as identity.** This is the main residual risk.
  - The link rests on three rows in a constant-velocity line, plus the
    witnesses.
  - It applies only beyond the current cap and only upward, and it refuses
    any non-unique combination.
  - The controls must show it never fires on the local 2 fps runs.
- **"Globally reduced jump thresholds" (rejected earlier).** Nothing global
  changes: rows within the cap follow exactly today's path.
- **`S11-F05`/`F08`.** Fill phases, releases, top-exit and the initial EMPTY
  lower-entry contract are untouched.
  - A seeded level becomes a fill owner only under the existing rules.
  - If its first row is not in the lower entrance band, it is not a fill
    owner; this is a named limit.

### Activation

- **Flag:** opt-in GUI `--oil-fast-rise-association`, default OFF. It reaches
  `DirectedTrackletPolicy` through the existing detector factory → resolver
  config path.
- **Version:** `+fast-rise-association-v1`.
- **Combinations:** combinable with IFO v2 and top-exit v3. Refused with
  cost-first, candidate RGB and Local XY. Independent of the held fill-owner
  gate.
- **Default:** production is unchanged until its checks and the user's
  decision.

### Known limits

- **No real local fast fill.** sample5 at 0.5 fps and sample5 with the cap
  narrowed to 9 px are stand-ins.
- **SPL#4's recorded rows may not form a line.** The higher candidates are
  Y463 at 22.5 s and Y462, Y534 and Y651–660 at 24.5 s. Rows at 23.0–24.0 s
  were not listed, so whether a constant-velocity triplet exists is unknown.
  A read-only SPL4_B_ref readout of every Oil candidate at 20.5–25.5 s, with
  the witness fields, would answer it before any Windows run.
- **The seed needs three frames.** At 2 fps, a level that crosses the Glass
  in fewer than about 3 samples is still missed.
- **Fast drains are out of scope.** The user says they are usually slower than
  this.

**Checks:** the
[fast-rise association checks](../30-validation/s11-physical-interface-evidence-repair-validation.md#fast-rise-association-checks--2026-10-23).

## Cost-first assignment comparison

The first of the three authorized Windows candidates reuses the exact intervention
from the [October 10 frozen cost-order-only probe](../50-diagnostics/s11/2026-10-10-cadence-owner-causality.md#one-frozen-attribution-counterfactual).
Add a default-OFF `cost_first_assignment` constructor option and GUI launch flag
`--oil-cost-first-assignment`. For the intended Windows pair, enable
`--initial-full-observation` in both runs and add the cost-first flag only to the
trial. The options are independent; cost-first does not change the Recipe's initial
state or silently enable initial-FULL observation.

Only `DirectedInterfaceTrackletBuilder._established_first_pairs` changes when ON:
sort by `(cost, tracklet ID, row ID)` instead of giving established tracks priority
before cost. Existing reciprocal reservations, including their subsequent ordering,
are unchanged. Match-cost terms, eligible pairs, ambiguity, confirmation, authority,
phase release, final selection and Foam ownership retain their existing policies.
This is not a global reassignment solver or a removal of `INCOMPATIBLE_BRANCH`.
Changed associations may still alter later motion, phase and final Foam composition;
those effects must be measured rather than presumed absent.

Reuse the existing GUI detector factory for preview, analysis, preflight and partial
redetection. ON appends `+cost-first-assignment-v1` to detector and both resolver
versions and shows `Oil cost-first 비교` in the window title. The same-frame raw
proposals are unchanged; the comparison acts during completed Oil resolution.
OFF must retain the pre-change outputs and runtime identities.

The qualified review-004 alternatives and f15896 pre-IFO exclusion are comparison
cases, not new thresholds or unique target coordinates. No private frame/time/Glass
rule enters code. Preserve the 721 s non-Oil output, FULL suffix, and 723/771 s
protective rejections as controls. The earlier local probe's upper-texture error
remains a failure; this option is not adopted and does not implement top-exit FULL.

Local verification covers the real launch/factory path, bounded tracklet
controls, resolver/publication integration, and a paired real-video replay using
the already frozen initial-FULL interior ROI inputs. Reuse the existing replay
runner and managed artifact entry; do not reconstruct the retired October 10 raw
inputs or refit a model. Windows effectiveness remains pending.

## Candidate-local RGB Windows comparison

Priority 2 reuses the [frozen candidate model](../60-evidence/s11/2026-10-14-candidate-rgb-trial.md)
without fitting, cutoff changes or a new mask. The historical rim failure remains
FALSIFIED_BY_REVIEWED_RIM. The new work is the opt-in connection to completed
Oil eligibility; the old trial scored isolated candidates and had no production
consumer. Compare FULL+observation v2 with v2+RGB, with cost-first and Local XY OFF.

`--oil-candidate-rgb` is default OFF and independent of initial-FULL. Package the
unchanged 6,594-byte weights with SHA-256
`8daffcdff5a59f6c8b2212c3e41aa911d676ac391d152a23857bd65d185636db` as a runtime
resource; retain the historical evidence copy. No Torch/model download is needed.
NumPy inference implements the same three valid convolutions, two ReLUs, ordered
side means and classifier. Shared convolution over a 25-pixel-wide native strip
reuses overlapping 7×7 computations; it must equal independent per-patch inference.

For every finite Oil candidate, use the Recipe ellipse's rounded source center X
and the candidate's source Y, converted by the actual crop origin. Preserve the
existing ±12 native side footprint, all complete visible/glare-free 7×7 patches,
RGB /255 and required floor/ceil Y variants. No resize, padding, replacement mask,
pure-side labels or private Glass/time/Y rules. Every required variant must choose
the same class; ties/disagreement are UNKNOWN, missing support is UNAVAILABLE.

Apply the model as an **additional completed-Oil eligibility condition**:
only OIL_CANDIDATE_COMPATIBLE passes this condition. OPPOSED, UNKNOWN and
UNAVAILABLE do not. Compatibility never raises authority, changes a score,
rescues an existing rejection or supplies an interface coordinate. Preserve all
raw proposals with their RGB result and input provenance; do not delete denied
candidates. The existing `candidate_is_eligible` owner consumes the added
condition before tracklet/phase/selection. Current-frame legacy positions remain
provisional; the comparison claims concern completed sequence/CSV output.
No-interface evidence, association, ownership, selector and direct Foam policy
are unchanged. Final Foam effects must still be compared after composition.

The normal frame projector computes RGB annotations independent of debug level.
The shared GUI factory carries the flag to preview, analysis, preflight and
redetection; detector/resolver identities append `+candidate-rgb-v1`. Missing or
corrupt packaged weights abort enabled construction; a resolver configured for
RGB must not silently accept Oil inputs without the RGB annotation. Cost-first
and RGB cannot be enabled together in this single-mechanism comparison.

Before any local replay, freeze this consumer and input rule. Verify all retained
available candidate logits/decisions against the old readout, including the three
known rim false accepts. Verify missing support, fractional variants, crop origin,
hard-invalid preservation, raw Foam/proposal preservation, OFF equality, actual
GUI routing and exact selected/CSV provenance. Reuse the two frozen local clips
and interior Recipes; their FULL initial state is a mechanism stress condition,
not physical truth. Retain losses and unknowns without tuning. Windows physical
comparison and the third Local XY candidate remain separate.

## 1. Interface evidence and independence

### Responsibility and data

Add an immutable per-candidate `OilInterfaceWitness` at `FRAME-EVIDENCE` /
`OIL-CANDIDATE`, normalized by `OilCandidateEvidenceIndex`. This is a proposed
type. The witness is computed from the current source raster and effective
mask before authority, selection or final Foam publication. It includes:

| Field group | Required meaning |
|---|---|
| Provenance | Source-frame index, crop transform, candidate identity, measurement channel and shared derivation identity; array sort order is not identity |
| Spatial support | Valid common column sectors, local contour Y per sector, edge localization and uncertainty; missing sectors stay unavailable |
| Two-sided context | Signed band contrast and material/texture summaries immediately above and below the contour in each valid sector, with broader context for internal stripes |
| Opposition | Existing artifact, border, exclusion, glare and optics evidence plus local internal-structure evidence; no final Foam decision |
| Decision | `INTERFACE_SUPPORTED`, `INTERNAL_OR_ARTIFACT`, or `UNRESOLVED`, with evaluated predicates and availability |

Reuse the material path's five-sector decomposition as the initial bounded
measurement grid; at least three spatially distinct usable sectors are needed
for the new distributed witness. Sample other candidate families on the same
grid. Do not assume that an aggregated median Y describes a curved contour.
Per-sector bands must exclude the edge itself and respect the effective mask.
Persist small descriptors, not full frame histories. Evidence enrichment does
not add proposals or enlarge the candidate beam.

An edge peak alone, material-mask bottom, high row texture, two generator names,
or vertical ordering is insufficient. `INTERFACE_SUPPORTED` needs localized
boundary support and a coherent two-sided partition across the valid sectors,
with usable artifact/optics evidence and no contradictory internal-stripe
context. Photometric sign is measured; Oil is not universally assumed dark or
bright. The new measurements must distinguish interface partition from a
bright stripe inside otherwise comparable material on both sides.

The current scalar `material_texture_conflict` remains in diagnostics and in
legacy behavior until its replacement is validated. A new high-texture route
requires the positive local partition witness for both participating peers;
it does not zero the scalar or remove artifact/optics gates. Missing new
descriptors cannot activate this route. Existing clean-evidence routes retain
their current requirements during implementation comparison.

### Independent corroboration

The [October 16 peer screen](../50-diagnostics/s11/2026-10-16-corroboration-peer-screen.md#nonrecursive-seed-condition-rejected-without-retuning)
falsifies a shortcut: requiring an ordinary peer to pass legacy anchor authority
with zero representation support removes an already accepted material candidate's
support. Different-family raw rim candidates can also support each other more
strongly than the accepted interface. Neither a larger support floor nor a
pre-existing-anchor requirement replaces the physical witness below. Preserve
noncircular measurement dependencies without demanding legacy anchor status of
a weak raw peer. This is a rejected local necessary-condition screen, not a new
runtime rule or a replay of the private 721 s frame.

The subsequent [native-geometry screen](../50-diagnostics/s11/2026-10-16-corroboration-geometry-screen.md#executed-results)
finds captured native paths for 35/175 Oil candidates, but none of the 85 directed
positive support pairs has both paths. The required common-native comparison
is therefore not assessable on these saved pairs. Basic raster-band arithmetic
reproduces; neither fact validates a physical discriminator. Do not install a
both-native hard gate over the existing packets and call their lost support a
successful false-anchor repair.

Keep three input types distinct: an actual generator path; a separately
re-observed current-raster contour hypothesis with its own extraction lineage;
and a scalar-center sampling window. Only the first two can supply proposed
contour geometry, and either still needs physical-role/localization qualification.
A re-observed hypothesis is new measured evidence, not retroactively a native
path of the original candidate. It must retain alternatives, unavailable sectors
and explicit pixel-to-candidate correspondence. Candidate Y, nearest peaks and
peak hulls cannot silently become a contour or calibrated uncertainty. A concrete
localizer/partition design and its two-sided controls must precede any consumer;
this clarification selects no production extraction algorithm or operating point.

The fixed [CRW-1 raster-partition screen](../50-diagnostics/s11/2026-10-16-raster-partition-screen.md#execution-result)
now implements a diagnostic-only input: matched-column edge measurements and
matched-position four-band context, with every tied peak and censored sector
retained. Generator-native and scalar-center seeds remain explicitly different;
the resulting sector peak sets are neither continuous contours nor inherited
native truth. This is useful partial input, not a qualified material-role witness.
A larger count of supported sectors can favor a reviewed non-target over an
accepted interface, and another positive/negative pair ties. Do not convert
that count to authority or tune its cutoff to those cases. Shared exact rows
from this same extractor are measurement aliases, not independent peer votes.
The physical-role/localization and consumer validation below remain required;
CRW-1 supplies no new production field, peer support or selection policy.

Construct evidence before authority in a directed order: raw witness → eligible
peer relation → independent support → phase identity → authority. A candidate
cannot use its new anchor status to validate the peer that granted that status.
Rejected-by-selection or pruned peers may supply eligible raw evidence; a
hard-invalid peer may not.

Different source-family strings are necessary only where the existing family
contract requires them; they are never sufficient proof of independence.
Duplicated candidates and descendants of one measurement contribute once.
An edge-localization channel and a separately measured region-partition channel
may corroborate on a common physical contour; aliases of one edge extraction
may not. Peer agreement uses common-sector contour overlap and uncertainty as
well as bounded Y distance. Preserve calibrated-only bootstrap prohibitions.

`OilCandidateRef` carries the resulting witness identity and contributing peer
identities. Phase identity and lifecycle consume this same typed result rather
than recomputing different texture/source shortcuts. Existing ordered-lower
contradictions remain explicit vetoes; proximity to a Foam row never creates
Oil identity.

### Material gate consumption

Changing the peer gate alone is insufficient: scalar material conflict is also
read by authority, row/tracklet aggregation, phase admission, release and
selector continuation support. Introduce one typed material-compatibility
decision at these seams for the new witness route. `INTERNAL_OR_ARTIFACT`
remains a veto. `INTERFACE_SUPPORTED` may satisfy material compatibility despite
high broad texture only with the required local partition and independent
support; it does not bypass other authority or lifecycle predicates.
`UNRESOLVED` supplies no exception to existing material gates.

Retain raw scalar values and the legacy threshold outcome in diagnostics next
to the typed outcome. Do not write a fabricated zero into current or historical
conflict. Evaluate compatibility on each actual contributing member/observation:
a true contradiction cannot be erased by a cleaner member, a median or a later
anchor. Unsupported members cannot borrow the row's positive witness to become
publishable. Historical compatibility covers the verified motion/confirmation
observations; no new witness can sanitize a false predecessor.

This is a semantic replacement of broad-texture vetoes where the new witness
is complete. Existing drain direction, minimum progress, entrance and expiry
requirements remain unchanged. Compound extraction-to-publication tests must
prove that a downstream legacy scalar gate does not silently cancel the new
typed decision, and that true material contradictions still block it.

## 2. Physical association before motion

`DirectedInterfaceTrackletBuilder` continues to enforce the existing maximum
gap, jump, prediction, one-to-one assignment and ambiguity bounds. Add a typed
association result: `SAME_INTERFACE`, `DIFFERENT_INTERFACE`, or `UNRESOLVED`.

For candidates with usable witnesses, compare common-sector contour shape and
two-sided context after bounded registration. Use spatially distributed
displacement agreement to distinguish physical movement from selecting another
stripe. A single band-motion scalar, shared direct/ordered class or shared
source does not certify an association. A contradiction must not be averaged
away by other members of a row.

- A stable or moving same-interface match retains its physical tracklet ID.
- A physically different current interface starts a fresh ID and fresh motion
  history. The predecessor's anchor count, direction, progress and lease cannot
  be copied to it.
- An unresolved match cannot add a displacement edge or confirm the previous
  identity. Retain a bounded provisional alternative and publish UNKNOWN until
  identity is established. Do not convert missing evidence into a successful
  same-interface result. Existing ambiguity handling remains active.

Use only verified displacement edges for recent and confirmation trajectories.
Fresh confirmation cannot reach backwards across an unresolved/different edge.
Preserve valid rapid movement and physical reversals when distributed evidence
supports them; do not lower the global jump bound or forbid upward motion.
Existing bounded retrospective confirmation may certify eligible observations
inside its window, but may not import the false predecessor into the new ID.

## 3. Established-fill owner transfer

Replace the source-specific condition in `_is_current_fill_anchor_handoff`
with a shared interface-witness requirement. A proposed successor must be a
current admitted anchor with a confirmed, uncontradicted physical identity,
usable current interface evidence and the existing bounded phase geometry.
Continuation authority alone is insufficient. Initial EMPTY entrance remains
the existing dynamic lower-entry contract.

There are two explicit cases:

1. **Identity-preserving handoff:** exactly one successor is independently
   confirmed and physically compatible with the last verified owner observation
   within ordinary loss grace. Transfer phase ownership, append its distinct ID
   and retain a bounded phase link. Do not copy the predecessor's measurements.
2. **Owner correction:** the old owner is positively contradicted and exactly
   one independently confirmed current interface exists. Start a fresh
   direction-neutral observation episode under section 4; do not claim it is a
   continuation of the old structure or inherit its fill/drain motion.

If the predecessor's identity is unavailable rather than positively
contradicted, case 2 does not apply. If an old owner is still valid and competes
with the successor, or multiple successors qualify, emit UNKNOWN and retain
the existing bounded ambiguity/loss handling. Expired snapshots cannot be
refreshed merely because another candidate appears.

The current temporary handoff leaves the original chain unchanged. The proposed
replacement records whether transfer was committed, which fresh owner is
allowed next, and when the link expires. A temporary allowance must not be
reported as a committed transfer. On loss of the successor, do not fall back
to a stale predecessor coordinate or silently return to its identity.

The selector remains a consumer of the explicit allowed owner set. It must not
solve a handoff failure by selecting a higher-scoring unallowed tracklet.

## 4. Direction-neutral visible-interface ownership

Propose an explicit `OBSERVED_INTERFACE` phase, separate from `DRAINING` and
`FILLING`. This is a deliberate extension of the current four-state lifecycle,
not a reinterpretation of the existing `downward_direction` predicate.

| From / trigger | Proposed transition and publication |
|---|---|
| Initial `FILLED_BARRIER`, strong bounded current interface witness | Enter `OBSERVED_INTERFACE` with one fresh owner; publish only an eligible selected current candidate |
| Established fill, confirmed stable interface or qualified owner correction | Enter `OBSERVED_INTERFACE`; preserve material-presence context but do not transfer unverified motion |
| `OBSERVED_INTERFACE`, verified sufficient downward motion | Enter `DRAINING` under existing direction/progress/material requirements using this identity's motion history |
| `OBSERVED_INTERFACE`, verified upward motion | Enter the appropriate fill/refill path with existing direction and closure evidence; no fabricated FULL transition |
| Current supported no-interface FULL evidence | Close observations and return to coordinate-free `FILLED_BARRIER` |
| Missing, hard-invalid or contradictory current row | Publish UNKNOWN immediately; context may survive only the existing bounded loss grace |
| Expired or ambiguous context | Clear owner eligibility and return to the constrained originating context, never unconstrained OPEN |

Initial-FULL admission to this new phase requires all of the following:

- an independently supported current interface witness, including two-sided
  raster partition and artifact/optics clearance, that contradicts a homogeneous
  no-interface interpretation;
- a unique physical owner confirmed within the existing bounded confirmation
  window, using fresh qualifying observations and no unresolved association;
- no hard current no-interface/identity contradiction, competing qualified
  owner, unavailable mandatory evidence or internal-structure classification;
- an eligible actual candidate on every published frame. A window witness
  cannot publish a frame with no eligible boundary candidate.

This is stronger than existing `ANCHOR_ELIGIBLE`/`ANCHOR_CORRIDOR` alone.
Stationarity and persistence are not positive interface evidence. The new route
may observe a genuinely stationary boundary only with independently validated
raster identity. It may not release an existing drain gate on stationary or
upward progress. Homogeneous opaque FULL, fixed reflection, wall residue and
internal stripes remain no-numeric controls.

Keep initial EMPTY ineligible for this route until its own entrance is
established. Do not mutate the configured initial state. Each supported current
observation refreshes only the ordinary owner-loss age; an absent row cannot
refresh it. Reacquisition needs a fresh bounded witness, not an extended lease.
Keep existing direct/near/delayed drain ordering for frames qualifying those
routes; the new observed-interface route follows them and cannot override
ambiguity or a hard veto reported by a prior route. It does not reset a
consumed delayed attempt in an existing episode.

Downstream projection must audit every phase switch. This state means visible
Oil with unknown movement direction; it does not manufacture fill/drain events,
change coordinate conversion or become a fallback coordinate. Final Foam
resolution remains independent.

## Decisions, calibration and implementation boundary

The chosen owner boundaries, required predicates, fail-closed behavior and
transition semantics above are design decisions. Numeric operating points for
partition strength, contour/context similarity, registration uncertainty and
internal-stripe discrimination are **not yet validated** by the transferred
scalar reports. They must be selected from public/synthetic positive and
negative raster controls before enabling the corresponding new route. Reuse
existing spatial, temporal and resource bounds where applicable; do not choose
thresholds to include a private Y jump or make a private conflict value pass.

Current authority consumes scalar support, not a qualified physical witness.
O1 already retains basic two-sided measurements and some native paths/lineage;
reuse those rather than assuming extraction is wholly absent. The geometry
screen shows the missing cross-family contour input, while physical role and
measurement independence remain unqualified. Any necessary new bounded
measurements and their actual decisions must be explicit. If the controls
cannot distinguish a stationary interface from an internal structure, section 4
remains unenabled; do not weaken its evidence requirements.

Implementation sequence is witness extraction and controls, independent support,
association and confirmation, committed fill handoff, then the new phase and
projection audit. Initial-FULL adoption is a distinct acceptance gate. The
[validation contract](../30-validation/s11-physical-interface-evidence-repair-validation.md)
defines the required cases and measurements. No production change is made by
this proposal.

## Diagnostics

Record actual predicate inputs, thresholds, availability and reasons rather
than rerunning decisions for trace output. Include:

- stable candidate identity, peer measurement lineage and peer exclusion;
- interface/partition/stripe decision and usable sectors;
- predecessor/current row identities, association result, displacement edges
  actually included in each motion window;
- phase handoff versus owner correction, attempted/committed distinction,
  allowed-set exclusion and ambiguity before path scoring;
- visible-interface acquisition/expiry/closure source, current witness endpoint,
  and chain-specific reset identity and reason.

Persist resolver offset and source-frame index as separate fields. Document
whether a legacy candidate offset refers to pre-sort input; do not relabel it
as the serialized array index. Diagnostic detail must not change output.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R22 cross-representation texture veto and material-member temporary handoff; R16/R21 bounded association and confirmation; R18 initial-state and partial-fill gates; R19/R22 release lease bounds; R10/R11 smooth false-identity paths and F06's textured true/false material counterexamples; the cost-first Windows regression, qualified review-004/005 and frozen RGB model's rim failure/input contract. For the 2026-10-22 contested fill-owner draft: FOA-1's owner readout, DSR-1, the R18 fill-ownership ambiguity outcomes (`FILL_OWNER_AMBIGUOUS` keeps the contested chains; completion, chain and re-entry ambiguity drop them) and the R21 recent topward predicate. For the 2026-10-23 fast-rise draft: FFF-1's mechanism reading and local cause check (association cap, `INSUFFICIENT_NET_PROGRESS`), the existing `_representation_bridge` independent witness, and the velocity-prediction gate.
- Prior mechanisms rejected: scalar texture neutralization, generator-count identity, globally reduced jump thresholds, stationary drain release, continuation-only takeover, stale owner or coordinate copy, unrestricted OPEN recovery, lease extension as an identity repair, private video/Glass/coordinate conditions, and the locally regressing R23 native-polarity-only association veto. For the fill-owner draft: motion-only owner validity (the desk reading shows the low owners rising in parallel with the level) and vertical order as identity (topmost or lowest owner), which F04 forbids and which would pick a Foam top or a bubble boundary. For the fast-rise draft: a higher sampling rate (user: too slow for products) and a widened or time-scaled cap (it would merge nearby components; sample7 shows jitter alone matters).
- Preserved contracts: one generic detector, bounded current-candidate provenance, initial EMPTY entrance, independent Oil/Foam, fail-closed ambiguity, no carried/interpolated observations, verified physical IDs before motion and unchanged drain direction/progress/entrance/expiry bounds. The fill-owner gate keeps the initial EMPTY lower-entry contract, all chain, barrier and release state and fill-span completion; it only empties allowed sets. The fast-rise draft changes only which tracklet a beyond-cap upward row joins; rows within the cap, fill phases, releases and top-exit are untouched.
- Existing feature coverage: this clarification reuses the frozen A1/public original raster, visibility masks, O1 path/center bands and exact candidate provenance. Source review follows retained diagnostic paths through phase_candidate_assembler and phase_frame_detection to oil_interface_diagnostics, then contrasts the scalar authority consumer. Existing Recipe, Artifact/static/motion and all comparison options are unchanged; earlier top-exit/RGB/IFO scopes remain in their result owners. The 2026-10-22 fill-owner draft reads the FOA-1 baseline readouts (IFO v2, top-exit OFF; both arms identical there) with the frozen empty-fill Recipes. Its planned check reuses the top-exit negative controls and the comparison runner, with IFO v2 + top-exit v3 as the reference arm. The fast-rise draft builds on FFF-1's cause-check run (sample5/sample7 at 2/1/0.5 fps and a cap-only arm, debug NONE) and plans the same six top-exit negative controls plus the sample5 stand-ins.
- Execution scope: the linked frozen 7ee6d90 diagnostic had no two-native comparison inputs; CRW-1 at 7845f89 adds diagnostic-only matched current-raster sector observations over the same 187 units and 85 relations. Its direct-loop arithmetic and 123 focused tests verify measurement contracts, not continuous contours or physical roles. This update selects no production extractor/consumer, fits no model and changes no sequence, report or private Windows execution. The 2026-10-20 top-exit move is behavior-preserving: the existing top-exit unit tests, resolver decomposition guards, production-surface test and R16 characterization goldens pass. No detector run or Windows execution was exercised. The 2026-10-21 top-exit v2
  section was implemented at `1f68c46` and failed its one Windows run (⑨); its
  record is in the v2 evidence. The v3 section was frozen from that receipt and
  review-004 before any code change, then implemented with its local controls;
  its record is in the v3 evidence. The 2026-10-22 promotion preparation adds
  a design section and pre-registered acceptance criteria only; no code, run or
  Windows execution. The SPL#4 entry conditions added the same day apply those
  criteria to the user's reviewed recording before any output on it; no run.
  Their recorded file size was later corrected from a relay typo, caught by
  the Windows identity check before any detector run. The 2026-10-22
  contested fill-owner gate and its checks were frozen the same day, before any
  code or run. Its only execution so far is the closed desk run
  `s11-fill-owner-contest-desk-20261022-001` over kept FOA-1 readouts: no
  detector run, video decode, code or Windows execution. The user's sample7
  judgment and product-geometry statement are recorded in the section.
  The implementation adds synthetic lifecycle tests, wiring tests and a
  comparison-runner mode; the frozen local controls run afterwards and
  are recorded in their evidence. The 2026-10-23 fast-rise section was
  frozen before any code; its implementation and local checks are recorded
  in their evidence. The 2026-10-27 note records the user's SPL#4 BASE truth
  correction from review-015 and review-016 (human frame reviews, no run); no design,
  criterion or code changes. The 2026-10-27 co-located fill-owner (E4) section
  is a draft frozen with its checks before any code; its prediction reads the
  kept FOR-1 readouts and the relayed step-12 rows only. Its implementation
  adds synthetic lifecycle tests, wiring tests and a comparison-runner mode;
  the frozen local controls run afterwards and are recorded in their evidence
  (closed run `s11-fill-owner-colocation-local-20261027-001`, no Windows
  execution). The user's decision to accept sample5's out-of-frame changes and
  to queue the Windows comparison is recorded beside the frozen checks, which
  are not edited; no run or code change.
- Difference from prior failures: distinguish measured input availability from physical-role discrimination before choosing a consumer. Neither the rejected legacy seed-anchor shortcut nor a new both-native gate can erase accepted weak support and count as a repair. New raster contours would require their own lineage and qualification; source Y/peak hull substitution, mask tuning and missing-evidence bypass remain prohibited. The fill-owner gate removes a win by attrition after a recorded ambiguity; it adds no allowance, coordinate, lease or threshold and changes no lifecycle state. The fast-rise draft adds one bounded association route for beyond-cap upward rows (seed of three witnessed rows in a constant-velocity line, then prediction-gated continuation); it is not a widened cap, adds no coordinate and leaves within-cap association unchanged.
- Logic-map impact: NONE — this update records the E4 local result; its feature row and 4.3 paragraph were committed to the map with the implementation (`9ee11a4`). Earlier: the fast-rise local result changed nothing; its feature row and 4.2 paragraph were committed to the map with the implementation (`4f0665b`). Earlier: the gate's feature row and 4.3 paragraph were committed with its implementation (`2cb0b52`); the v3 implementation evidence records the top-exit row and paragraph.
- Failure-registry impact: NONE — F03/F04/F09/F10 already cover physical-identity, provenance and evidence-shortcut risks. The new result is an availability boundary, not a newly adopted failure mechanism or field repair. The attrition path is an instance of F04 (stale continuation after an ambiguity), F05 (EMPTY-phase fill ownership) and F08 (owner re-adoption); no new entry.
