# Candidate-local Foam gap context — 2026-10-09

Base: `2e5d6accf54b32040a05ceb0793cb07341eced0f`.
This saved-raster investigation follows the [ordered-gap representation](2026-10-09-foam-upper-gap-representation.md).
The [Work Plan](../../00-project/work-plan.md) owns current state.

## Question and frozen comparison

Can actual appearance support on each side of a retained edge, together with
independently reviewed structure coordinates, distinguish a physical Foam front?
The preflight freezes all seven existing frames, all 24 retained components,
both original inspection radii and all 848 pairs before contextual measurement.
No new candidate search, detector execution, video decoding or parameter sweep
is performed. Duplicate observations across radii remain separate; they are not
independent trials or accuracy denominators.

Reuse the existing saved raw/clean white masks, pre-arbitration chromatic mask,
label rasters and signed-gradient plateaus. For each of the two edges of every
pair, preserve the immediate raw flank pixels just outside its complete plateau
and all pixels in the intervening corridor. White, cleaned white and chromatic
membership stay separate. An `entering` predicate means false above and true
below; `crossing` means true on both immediate flanks. Neither means physical
Foam, air or structure. There is no mask union or scalar reduction.

Reference decoding, context binding and reviewed domain reuse the existing
`artifact_reference` / `artifact_reference_diagnostics` owners. The recipe's
44 s snapshot and 125 reviewed Canny pixels match the earlier pins; current
baseline geometry and detector settings also match. Reference and current
effective/glare availability remain explicit. Compare only exact source XY,
without dilation, nearest-point matching, temporal registration or inferred
visibility. The reference Canny operator and current raw-gradient operator are
different; their coordinate intersection is not optical object correspondence.
The diagnostic recipe's templates are not adopted into the sample recipe.

## Results and rejected shortcuts

The following table describes lower rising-edge alternatives at the existing
radius 8. Counts refer to observations within a component, not approved physical
edges or independent samples. All other components, upper edges and radius 4
observations are retained in the [machine record](2026-10-09-foam-gap-local-context.json).

| Time / context | Pairs | Entering raw white | Crossing chromatic support | Intersects reviewed domain | Exact reviewed Canny XY hit |
|---|---:|---:|---:|---:|---:|
| 14 s, mixed C2 | 37 | 11 | 0 | 0 | 0 |
| 15 s, mixed C2 | 36 | 14 | 0 | 0 | 0 |
| 16 s, mixed C2 | 32 | 12 | 0 | 0 | 0 |
| 16 s, confirmed rim C1 | 30 | 23 | 0 | 0 | 0 |
| 54 s, C1 | 73 | 39 | 39 | 17 | 7 |
| 54.5 s, C1, unreviewed | 78 | 38 | 43 | 21 | 5 |
| 55.5 s, C1 | 44 | 23 | 42 | 9 | 3 |
| 56 s, C1 | 54 | 23 | 34 | 10 | 5 |

**H1 — entering white support is insufficient.** The rim-control component
also contains 23 such alternatives. At 16 s, the combined immediate-side pattern
`raw white false→true / clean white false→true / chromatic false→false` occurs
in 10 mixed-C2 alternatives and 21 rim-C1 alternatives. Presence of this pattern
cannot certify a Foam front. This does not label every C2 pixel Foam or every C1
pixel glass. The rim remains inside the broad agent-prepared recipe; these
results do not claim failure under a human-corrected ROI.

**H2 — chromatic crossing cannot be adopted as an internal-texture veto.**
The agent inspected original, raw-white and chromatic overlays. Chromatic
membership extends through the narrow upper-space region as well as through
lower texture. At 55.5 s it spans 42 of 44 retained lower alternatives, including
alternatives in the visible upper-front region. That is an appearance-mask
observation and a risk to upper-front recovery, not a measured false-negative
rate against exact human contours. The earlier human-confirmed internal-texture
proposals and this upper region must remain distinct. No veto is implemented.

**H3 — exact reference intersections narrow the measurement but do not resolve
physical identity.** Only 7/3/5 lower alternatives at 54/55.5/56 s touch a reviewed
Canny coordinate. At 55.5 s all three hits have negative raw signed derivative
in the reference, versus positive derivative in the current edge. Even an exact
coordinate hit therefore must not automatically remove a current edge. A miss,
especially outside the reviewed domain, is not proof of non-structure. The
upper central side of the narrow gap lies above the existing review rectangle
Y[816,828), so that reference cannot attribute it.

Existing static maps were also inspected at their actual source owner. They
threshold persistence of horizontal responses or detected Foam masks; they are
not independently reviewed structure identity. Neither they nor the approximate
double-rim clicks are substituted for a complete current-frame structure mask.
No new rim-registration requirement, interpolated click mask or ROI change follows.

## Physical checkpoint

The existing reply confirming a small space and visible Foam upper surface at
54/55.5/56 s remains CLOSED. The lower cyan internal-texture reply also remains
CLOSED. No exact Foam contour or pixel tolerance is requested.

The new [comparison image](2026-10-09-foam-gap-upper-side-review.png) shows the
originals and all complete pairs in one central display scope, X[584,602),
Y[805,815). Pink marks the upper side, cyan the lower side. This scope is a
display aid only; it selects no production path or operating point.

The distinct question is **what physical feature forms the upper side of this
narrow space**: fixed glass rim/pattern, another overlapping feature, or not
assessable. The agent suspects the inner glass rim/pattern but cannot establish
that from these blurred pixels. This is a regional identity question, not another
question about whether the Foam surface is visible or a request to approve each
dot. Status at recording: **AWAITING HUMAN REGIONAL IDENTITY**.

A reply can ground a structure–space–material adjacency hypothesis against the
glass-only paired-edge control. It cannot itself create an exact exclusion mask,
transfer the 44 s reference, identify every retained edge or certify an automatic
selector. If unassessable, preserve the unknown instead of forcing an attribution.
At that checkpoint, selection work dependent on this interpretation stopped.
No Windows work or file export is needed for this checkpoint.

## Human fixed-structure reply and relative gap check

The user subsequently answered **“위쪽은 고정된 유리 테두리, 무늬야”**.
The [attributed reply](2026-10-09-foam-gap-upper-side-reply.json) closes the
upper-side question for the displayed 54/55.5/56 s central region. Together
with the earlier visible-space/Foam reply, this establishes the regional order
**fixed glass feature → small visible space → Foam upper surface**. It does not
certify the exact gradient positions, every cyan dot, a structure mask or a
cross-frame correspondence. The original measurement JSON remains unchanged.

The follow-up tests one narrower hypothesis before building an automatic rule:
can raw lower-minus-upper separation change distinguish this situation from
a glass-only paired-edge control? Source discovery reuses the existing ordered
gap observations, rather than another patch matcher or camera-registration owner.
The fixed preflight includes all earlier mixed-C2 time pairs, the 15→16 s rim
control, all three late time pairs, and a separate view of the already displayed
central pairs. Both original radii remain in the complete-component comparison;
the display view remains radius 8 only. No display label is transferred to the
unreviewed 54.5 s frame or to the rest of the component.

For each plateau, retain every integer position in its half-open interval.
Compute all feasible lower-minus-upper separations, then every same-X
before/after combination. Keep multiple alternatives and missing columns;
do not choose a nearest, strongest or smoothest match. A within-frame separation
cancels a uniform vertical translation algebraically, but these queries do not
establish camera motion, horizontal alignment or material correspondence.
These operator ranges are not calibrated physical uncertainty or air-gap thickness.

| Query context, radius 8 | Common X columns | Separation necessarily decreases | Zero change feasible | Separation necessarily increases |
|---|---:|---:|---:|---:|
| Confirmed-rim components, 15→16 s | 27 | 3 | 15 | 9 |
| Prior central display, 54→55.5 s | 15 | 5 | 2 | 8 |
| Prior central display, 54→56 s | 15 | 6 | 3 | 6 |
| Prior central display, 55.5→56 s | 14 | 2 | 11 | 1 |

Each row is a coordinate query over all available alternatives, not an accepted
material track or independent accuracy trial. In the central 54→55.5 s query,
the upper signed-gradient locations shift upward in 13/15 columns even though
the user identifies the physical feature as fixed glass. This neither contradicts
the reply nor proves glass motion: localization/appearance, camera effects and
unverified correspondence remain distinct unknowns. No numeric jitter tolerance
is calibrated from these values.

**Decision:** preserve the regional role attribution; close a nonzero relative-
separation shortcut without promotion. The glass-rim control also has nonzero
changes in 12/27 columns, and the central material context produces mixed signs.
Neither stationarity, gap change, the lower member of a pair, nor chromatic
crossing can independently become a Foam selector. This is not a failure of every
possible structure-relative method: the tested operation lacks verified local
correspondence and a calibrated localization model.

Independent integer enumeration verifies **17 comparisons / 234 common-column
queries / 329 pair combinations**. It also catches an aggregation issue: an
interval envelope spanning negative and positive alternatives can contain zero
when their actual union does not. The v2 record preserves the exact feasible
union and distinguishes `MIXED_SIGN_NO_ZERO` from `ZERO_POSSIBLE`, correcting 23
column fields in the broader readout. The table above is unaffected. Original
preflight, v1 result, correction script and corrected v2 result are all retained;
this is a readout correction, not an operating-point change.

The [relative-context machine record](2026-10-09-foam-gap-relative-context.json)
pins the four direct inputs and 221 unchanged production source files, complete
v2 comparisons, original result hash and scripts. It reuses the earlier verified
rasters through the immutable context record; it does not claim to reread those
67 raw inputs or rerun the detector. Local files remain in
`sample/output/s11-foam-gap-relative-20261009-001/`.
Source-identity and complete Cartesian-coverage checks also pass for all 329
combinations. Detector governance, whitespace and the document audit pass
(981 local links, 17 named obligations and unchanged protected owners).

### Consequence for subsequent work

The physical question is CLOSED; no further human/Windows step follows from this
reply. D5's next design requirement is a **joint correspondence and side-role
decision** before scalar selection: local structure evidence must correspond to
the current upper feature, and a separate material partition must support the
lower front. Ambiguous correspondence or localization remains unresolved.
Preserve both same-frame alternatives until that decision; do not let a support
mask's extreme or a motion score silently assign the roles. A nearby glass anchor
must be optional, since earlier real Foam does not require a narrow glass/Foam gap.
Any challenger needs an explicit decision/abstention rule and opposing controls
before enabling behavior; this reply alone supplies neither a deployment mask
nor an automatic classifier. The comparison adds a falsification control to that
design requirement without reopening any completed physical review.

## Verification and preserved artifacts

An independent readout verifier checks all **848 pairs / 1,696 edge records**
against the original pair inventory and saved raw arrays. It checks complete
pair-key coverage, raw corridor bytes and label IDs, flank membership predicates,
reference XY intersections/derivatives and every aggregate. All checks pass.
All **67 pinned inputs and 221 production source files** are unchanged before
and after measurement. The review image and its source-result binding are hashed.
Detector governance, whitespace checks and the existing document audit pass
(977 local links and 17 named-obligation assertions; protected owners unchanged).

No production or reusable diagnostic API changed. This is a new local join
script, so the earlier 28 helper tests, detector acceptance and full-sequence
comparisons are not rerun or claimed anew. No physical classifier, recipe,
formal label, Oil/Foam output or acceptance state is changed; O2 remains OPEN /
FIELD FAIL. All-abstain observations are not reported as detector success.

The machine record retains the preflight, complete observations, source/input
pins, verification result, question/display identity and scripts. Full expanded
outputs and inspected early/late figures remain in
`sample/output/s11-foam-gap-context-20261009-001/`. Existing raw artifacts are
preserved. The diagnostic MD/JSON, review PNG, Work Plan, recall route and F07
entry record this result so the three insufficient shortcuts need not be retried.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: automatic front identity remains unresolved before scalar selection. Regional upper-side structure identity is now confirmed, but raw coordinates and cross-frame correspondence remain unverified. Candidate-local appearance and relative separation changes also occur on the confirmed-rim control; no new causal selector or episode failure is inferred.
- Logic-map impact: NONE — saved-array context measurement has no production caller or decision authority.
- Failure-registry impact: UPDATED — F07 records candidate-local side-support ambiguity, exact-reference limitations, the closed fixed-glass reply and relative-gap falsification; no physical classifier is promoted.
