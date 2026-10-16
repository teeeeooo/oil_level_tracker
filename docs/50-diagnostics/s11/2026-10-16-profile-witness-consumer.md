# PWC-1 — cross-validated pixel-profile witness through real consumers

## Question and frozen scope

Starting HEAD: `b5f93ecf9fc55b6473e105e8234b9d741f72a23e`.
Current authority: [Work Plan](../../00-project/work-plan.md).
RCI-1 demonstrated reviewed-role consumer feasibility, not a pixel discriminator.
This successor tests two explicit image-generating hypotheses without human labels
in extraction or runtime decisions. It is a diagnostic, NOT a production candidate.

Reuse all 113 sample4 P5 raw rows, original MP4 and saved Recipe. Decode exactly the
sampled frames; execute current geometry/preprocessing only for new pixel input.
Compare the seven shared saved rasters/masks bytewise. Original candidate extraction,
static learning, scores, settings and confirmed UNKNOWN initial state stay frozen.
Also screen every Oil unit in the eight-frame CRW roster, preserving the public
practical-alternative set, sparse physical roles and all unknowns. Windows ④–⑧,
721/723/771 s and reviews 004/005/008 constrain interpretation; no private replay.

## Fixed competing explanations

At the original candidate scalar (never relocalized), sample integer rows from
floor(Y)-L through ceil(Y)+L, L=3*existing O1 band+1; omit abs(row-Y)<2.
Reuse the five O1 sectors. Within a sector use only columns visible at EVERY
queried row; require at least two columns and 50% original sector width. At least
one usable sector is required; availability is not physical absence. A candidate
scalar probe is not its native path or a certified continuous contour.

Fit the sector's grayscale profile using alternating SOURCE-row parity; predict
the other parity, then reverse. This is per-query least squares, not supervised
training or restoration of the retired RGB/native/DINO models.

The continuous nuisance models are affine `[1,z]` and a continuous corner
`[1,z,abs(z)]`. H1's interface model is `[1,z,sign(z)]`; H2's is
`[1,z,abs(z),sign(z)]`, allowing different within-side slopes. Here z=(row-Y)/L.
All models use identical support/folds. Sum sector-balanced held-out MSE in each
fold. An interface preference requires that the chosen discontinuous model beat
BOTH continuous models in BOTH folds. A continuous-corner preference requires
that corner beat both affine and that interface model in both folds. Ties,
fold disagreement, unsupported/rank-deficient inputs are UNKNOWN, not negatives.
Numerical equality uses 1e-12 MSE tolerance only. No strength/count/radius tuning.
These are image-profile preferences, not automatically qualified physical roles.

H1 asks whether a localized corner versus a persistent jump can discriminate
known opposed/allowed candidates. H2 separately asks whether within-side gradients
explain useful boundaries lost by the common-slope assumption. Both are frozen
before real execution; neither is a response-tuned retry of the other.

## Consumer experiment and stopping rule

Execute baseline plus six full 113-row conditions: H1/H2 crossed with negative
member exclusion, positive authority only, and their combination. The pixel table,
not review labels, supplies every intervention; unknowns retain baseline behavior.
Reuse RCI-1's exact-member sequence eligibility and returned-authority seams, never
promoting HARD_INVALID. Original material conflicts, phase/history, assignment and
Foam owners remain active; this explicitly tests their compatibility, not a claim
that a descriptor has replaced their physical semantics. No label propagation,
score smoothing, carry, interpolation, coordinate edits or special timestamps.

Verify full baseline equality, every source/index/Y→selection→CSV join, all events,
per-series validity, extrema, useful existing observations and Foam episodes.
Retain ALL outcomes, including new unreviewed winners and harmful owner changes.
An isolated miss is not failure; losing a material motion episode, introducing
wrong extremes or sacrificing previously useful observations matters. Descriptor
agreement alone never establishes report comprehension. No automatic deployment
or fourth Windows comparison follows, even if local effects are useful.

Difference from prior CRW/P5 sign tests: fit explicit discontinuous and continuous
image models on row-disjoint predictions, not a band-sign conjunction or sector
count threshold. Difference from RGB/native trials: no learned source-global
weights, color-class claim or supervised fit. Difference from RCI-1: every runtime
role intervention comes from pixel preferences, with reviewed roles used ONLY for
post-run evaluation. Test provenance and semantics independently of observed gain.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-EPISODE`, `CSV-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`.
- First harmful stage: current reviewed wrong selections and positive exclusions remain the baseline. New pixel-model preference is not known physical identity; downstream effects and replacement extrema are measured rather than presumed corrected.
- Existing feature coverage: frozen P5 NONE raw and original Recipe/session; geometry and current preprocessing rerun only to supply matched current pixels/masks. Zero saved exclusions/templates; original static/Artifact outcomes retained in candidates. IFO, top-exit, cost-first, RGB and Local XY OFF. Completed Oil/Foam, samples/events, CSV and real graph/presentation execute; GUI, full HTML source-context owner and Recipe judgment do not.
- Execution scope: two preregistered pixel models on all 113 sample4 sampled frames and every CRW Oil unit; baseline plus six complete sequence/publication conditions. No private Windows video, new native path, formal truth, supervised fit or independent human report reading.
- Logic-map impact: NONE — diagnostic helpers and temporary restored seams only, with no production owner/default/call-route changes.
- Failure-registry impact: NONE — existing identity/coupling/provenance guards cover this unqualified hypothesis; no new physical failure class is assumed.

## Execution result — closed without promotion

Both hypotheses, all six intervention conditions, the verifier and synthetic tests
were frozen at `9c77abae2b1f2165a7dc70ba067e85ceb75949bc` before real execution.
There was one complete fixed run (89.76 s), not outcome-led threshold/model tuning.
Original 113 sampled frames supplied 2,549 Oil measurements. The eight-frame screen
reused 153 of those measurements plus 22 public candidates; it did not add eight
independent video sources. Original seven sample4 rasters and masks matched exactly.
The six physical sample4 correspondences, five practical acceptances and seven
oppositions in the sparse screen retain their original precision and denominators.

| Pixel hypothesis | Accepted 11: jump / corner / unknown | Opposed 7: jump / corner / unknown | Result |
|---|---:|---:|---|
| H1 common side slope | 8 / 2 / 1 | 2 / 4 / 1 | Six physical sample4 positives survive, but two known non-targets also prefer a jump; the public frame still has two useful alternatives |
| H2 separate side slopes | 11 / 0 / 0 | 7 / 0 / 0 | Flexibility preserves positives and admits every reviewed opposition; not a physical-role discriminator |

The public H1 alternatives lost are practical approximations, not two mandatory
physical detections. This is not why the family is rejected. Downstream episodes,
existing useful selections and replacement extrema provide the important result.
All 157 unassessed screen candidates remain unassessed. Extraction never reads a
human role, source-family score or temporal result. Compatibility adapter field
names are inherited from RCI, but carry explicitly marked pixel preferences;
all reported physical/practical statuses are independently rebound to real reviews.

| Completed condition | Numeric / valid Oil | Numeric / valid Foam | Original useful controls preserved / 3 | Physical correspondences selected / 6 | Reviewed opposed selected |
|---|---:|---:|---:|---:|---:|
| baseline | 101 / 101 | 26 / 26 | 3 | 3 | 3 |
| H1 negative member | 71 / 71 | 26 / 26 | 0 | 0 | 0 |
| H1 positive authority | 85 / 85 | 25 / 25 | 1 | 1 | 0 |
| H1 combined | 103 / 102 | 26 / 25 | 2 | 3 | 0 |
| H2 negative member | 101 / 101 | 26 / 26 | 3 | 3 | 3 |
| H2 positive authority | 86 / 84 | 23 / 21 | 1 | 2 | 0 |
| H2 combined | 86 / 84 | 23 / 21 | 1 | 2 | 0 |

The control columns diagnose preservation/replacement, not 100%-required recall.
H1 combined preserves 38/52 s and recovers 44 s, but loses 42.5 s and changes 54
selected identities. Old wrong 42/44 s extrema disappear; new extremes are
39 s/Y821 and 47.5 s/Y881, both unreviewed. The real graph now shows a large
47.5–51 s lower plateau followed by recovery. Original-pixel inspection does not
establish that new excursion as material motion. It cannot be counted as a
corrected maximum/minimum merely because the old known wrong candidates vanished.
H1 negative-only loses every Oil observation at 36–56 s; positive-only loses
44–56 s. These are material-context losses, not one or two edge-case misses.
H2 negative-only changes ten input candidates but no final selections. H2's
positive/combined conditions lose 46–56 s Oil and change reported Foam episodes
from one to two, with valid Foam 26→21. Accepting every reviewed positive at input
therefore does not ensure preservation of useful final movement context.

## Verification and interpretation limits

The verifier independently decoded all 113 frames, recomputed 2,164,608 direct
pixel references and 6,234 profiles, solved normal equations rather than calling
the extractor's least-squares helper, and checked all fold preferences. It verified
791 CSV rows, 633 exact Oil candidate/sequence/CSV joins, 17,843 authority calls,
200 domain events and 14 extrema with zero mismatches. All input and production
source hashes remained unchanged; the complete 113-row baseline equals the saved
P5 result. These counts certify arithmetic/provenance, not physical correctness.

Visual inspection covered all four retained original-pixel source atlases (113
sampled frames), baseline and representative negative/H1-combined/H2-positive real
report graphs, and original f1200/f1320 crops. The atlases' old captions describe
RCI-1, NOT PWC-1; only their byte-verified source pixels are reused here. New graph
risks are developer inspection, not newly approved truth or independent report
comprehension. Private Windows images/video were not accessed or re-executed.

**Disposition: CLOSED WITHOUT PROMOTION.** Neither scalar profile family qualifies
physical roles or improves integrated report context. No product source/default,
Recipe, model or truth changed. This does not reject all pixel/context mechanisms.
A successor must add a different, qualified boundary/side-role observation and
explain coherent consumer ownership, rather than increasing slope freedom,
changing the window/cutoff or granting anchor authority to a profile preference.
Keep RCI-1's positive/negative oracle feasibility as a diagnostic upper bound, not
a deployable fallback. FULL, independent Foam-front qualification and actual
report-only acceptance remain separate; no fourth Windows comparison is queued.

Reproduction, compact machine summary, retention and final tests are recorded in
the [handoff](../../60-evidence/s11/2026-10-16-profile-witness-handoff.md).

### Storage-only closeout verification

The artifact manager rejected duplicate CSV/graph payloads before deleting anything.
A post-run verifier-only change adds hash-checked, repository-contained aliases;
no extraction, model, role control, resolver or numerical output changes. The
original v1 numerical receipt remains retained. Five alias safety tests bring the
focused suite from 208 to 213 passing tests. The v2 storage receipt additionally
pins its own verifier source hash; final closure rechecks aliases after copies are
removed. This is storage reproduction, not another detector experiment.
