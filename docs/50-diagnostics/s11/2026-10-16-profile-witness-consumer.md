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
