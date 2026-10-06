# Local Foam front alternatives and motion-review preparation

Date: 2026-10-06. Base: `8184db7ac0e553b74ecb0660a28df0bf68b398fb`.
Changed diagnostic code is pinned by file hashes in the local report. Scope:
Mac development/regression only, not independent holdout or Windows qualification.
[Architecture](../../20-architecture/s11-foam-component-diagnostics-architecture.md#offline-boundary-alternative-prototype)
owns the representation; [work plan](../../00-project/work-plan.md) owns the gate.

## Implementation and validation

The prototype retains material-support geometry separately from every fully
bracketed local vertical-gradient maximum in fixed ±4/±8 windows. It reuses O1's
operator and validity rather than introducing a second gradient implementation.
No peak is selected as Foam. All fronts remain null, physical identity UNRESOLVED.
The saved-capture runner and interactive viewer retain all 14 components, including
rim negatives, mixed Foam/reflection support and base's missing relevant support.

Focused tests: **84 passed** across `test_s11_foam_front_alternatives.py`,
`test_s11_foam_support_geometry.py` and `test_s11_joint_context.py`. Tests include
synthetic competing edges, exact byte plateaus, mask/window/crop censoring,
identical-pixel reflection/material ambiguity, preservation and runner entrypoint.
Headless installed Chrome verified scene/radius/toggle/click controls, motion
frame loading, previous/next, half-speed play/pause, reset and slider end; no page
errors. Screenshots were inspected. This does not test an application UI or runtime
Foam behavior; neither changed.

## Saved-frame result and rejected promotion

Canonical output: `sample/output/s11-local-foam-front-alternatives-002/`.
Its predecessor `001` is a preserved preliminary run with floating-value plateau
comparison; only `002` uses exact byte-numerator plateau equality. This correction
was made to numerical representation, not to tune separation against human labels.

Counts below are column/window appearances, **not** rates of correct Foam identity.

| Case/component | Radius | Single peak | Multiple peaks | No bracketed peak | Censored |
|---|---:|---:|---:|---:|---:|
| sample4 C1, human rim | 4 | 39 | 39 | 0 | 0 |
| sample4 C2, Foam region / mixed top | 4 | 29 | 15 | 4 | 0 |
| sample4 C2 | 8 | 0 | 48 | 0 | 0 |
| sample2 C1, human rim | 4 | 6 | 3 | 0 | 0 |
| sample2 C2, Foam region / suspected reflection | 4 | 22 | 140 | 0 | 103 |
| sample2 C2 | 8 | 0 | 123 | 0 | 142 |

A single edge occurs on both human rim negatives and the Foam-region support.
Broadening the fixed inspection window exposes additional alternatives; it does
not identify which has the right physical cause. Noise/texture maxima are retained
because no amplitude cutoff is fitted. This falsifies using "single nearby edge"
as a sufficient Foam-boundary acceptance rule. It does **not** establish that the
central round feature is hardware, that every peak is a physical boundary, or that
all conceivable image methods must fail. No clean subinterval or interpolated
front is inferred. Base's absent relevant support remains a proposal/support gap.

The original 87 capture outputs plus their receipt were rehashed before/after:
**88/88 preserved**. No video, recipe or labels were reopened for this measurement.
Three generated outputs plus a separate receipt:

| File | SHA-256 |
|---|---|
| report.json | `877ca4ec045149f0905eac3bf1e2ba6243a18287a95946fbb2796a084ccaafcb` |
| viewer.html | `3b7d433191e03276ea69da16b580777a62f5d7aaa8296a049dd9f2d04d259a14` |
| receipt.json | `1393ff5656539a3159ad6c0bd2b73acd0f4906e69d2b8f3282c1d19d74cb26c6` |

Reproduce from repository root into a fresh output directory:

```bash
PYTHONPATH=.:src .venv/bin/python tests/diagnostics/s11_foam_front_alternatives_run.py \
  --capture sample/output/s11-local-foam-component-capture-001 \
  --output sample/output/s11-local-foam-front-alternatives-next \
  --expected-receipt-sha256 84b4b5e88c1ddf3b05da82591fef811be27844f6e282550a5e3d8451e52b9196
```

## Prepared human motion checkpoint — preparation record

Separate output: `sample/output/s11-local-foam-motion-review-001/`. This step
**does decode additional frames** of an already exposed Mac source under the
user's continuing local-work/additional-review authorization. It does not claim
the earlier single-frame measurement remained the scope of this new preparation.
No detector or tracking code runs, and no new physical label is assigned.

- Source: `sample/sample4.mp4`, SHA-256
  `ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892`.
- Fixed interval chosen before decoding: frames **390–510 inclusive**, 121 frames,
  **13–17 s at 30 fps**, around the previously reviewed frame 450.
- Fixed ROI: source origin **[543,798]**, shape **[104,104]**; same Glass as the
  captured sample4 case. No recentering, registration, enhancement or overlay.
- Backend frame positions verified before/after each decode. Frame 450 ROI is
  pixel-equal to the saved reviewed plain image. This establishes this anchor
  comparison, not universal historical pixel identity.
- Source video, capture metadata/receipt/plain image and all original 87 capture
  outputs preserved. Recipes, formal labels and truth files were not edited.
- Viewer: left static frame 450; right original ROI sequence with frame slider,
  next/previous, original or half-speed playback. Display enlargement adds no detail.
- Local `prepare.py`, manifest, viewer and 121 PNGs have 124 hashes in a separate
  receipt; receipt status is **PREPARED_FOR_HUMAN_REVIEW**, not acceptance COMPLETE.

| File | SHA-256 |
|---|---|
| manifest.json | `413c814f942f2b8791fd5c353f09e96f4c42881ee7b9a7d25047c676f175e5d7` |
| viewer.html | `db6c84cc11b2912222a7eb335980ba7d452054827bfe4e38a01e1ba20e857457` |
| receipt.json | `729175a4fe8e03c4b217fe36a6db8d2583c77cfe0128054d43070fa0e53ca229` |

Question presented: does the central round/arched feature move or deform with
surrounding Foam, remain fixed while Foam changes, or remain indeterminate?
This is a new temporal observation, not repetition of the prior material-region
question. A stationary appearance alone does not establish structure; insufficient
motion/resolution must remain uncertain. At preparation this reply was pending;
the subsequent response is recorded below. No Windows execution or new independent recording is required
for this checkpoint. Existing human ambiguity and FIELD FAIL remain unchanged.

## Human motion reply — stationary central feature

The user subsequently reported:

> 글래스 중앙의 원형·아치형 특징이 주변 Foam 경계와 함께 움직이지 않고 변형되지 않음, Foam이 변해도 같은 자리에 있음

This is a **direct qualitative human observation** on the prepared 13–17 s
sequence: the central appearance stays in place and does not deform while the
surrounding Foam changes. It closes the motion-review question. It does not
provide an exact affected region, point trajectory, numerical displacement or
stationarity tolerance, and does not label the whole C2 component as structure.

The observation strengthens the mixed-support concern: the saved support top
cannot be accepted wholesale as the moving Foam front. At this reply, hardware
versus reflection, the true boundary through/around it and generalization remained
unresolved. The subsequent structure clarification below resolves the feature
identity question through explicit human attribution. A stationary Foam layer is possible in
other contexts; motion or its absence must not become material identity by itself.
The original Foam-region observation remains intact, as do the prior Oil/Foam
path judgments. No formal labels, masks, scalar or episode decision changed.

Reply saved outside the immutable review outputs:
`sample/output/s11-local-foam-motion-review-001-notes/reply-001-central-stationary-feature.json`,
SHA-256 `af23ed2442a8eaf8f158918cecf1f57b8f0f18ba8447d0317e5ea016125767e0`.
All **124 registered review outputs** were rehashed before/after and remain
unchanged; the original preparation receipt remains PREPARED_FOR_HUMAN_REVIEW.
Its status is not retroactively edited into physical acceptance.

## Human clarification — regularly spaced circular structures

The user's subsequent clarification is:

> 일단 구조물임 가운데 원형부터 일정 간격으로 원형 구조물이 있음

The central circle and the circular features at regular intervals are now
**human-confirmed structures**. This supersedes the earlier structure-versus-
reflection uncertainty for the features described. The attribution comes from
this explicit human clarification, not from treating stationarity as an identity
rule. Their fixed appearance while Foam changes remains the preceding observation.

This gives a qualitative structure control inside the mixed Foam-region context.
It does not label the entire C2 component as structure, supply exact circle centers,
radii or pixel spacing, or determine the true Foam boundary behind/around them.
Do not synthesize equally spaced circle masks or delete an entire central strip.
Prior Foam-region attribution and Oil/Foam judgments remain preserved.

Append-only local reply:
`sample/output/s11-local-foam-motion-review-001-notes/reply-002-circular-structures.json`,
SHA-256 `d47e8142a19bd6d5d60963b4e96af19dd45ed42648cfe553cfc7b2073bdd0733`.
The prior reply remains byte-identical and all 124 registered review outputs are
preserved. Formal candidate labels, pixel masks and runtime decisions are unchanged.

### Next bounded verification and existing owner

Source inspection identifies `temporal_raster_evidence.py` as the existing owner
of camera/exposure-compensated raster evidence. `RegisteredFoamMotionTracker`
already measures registered overlap/turnover/internal change, but aggregates a
supplied Foam mask/front; that summary alone cannot establish which subpart of
this mixed support is a real Foam boundary. Do not fabricate per-frame Foam truth
by copying the frame-450 C2 mask through the sequence.

The next local experiment should reuse existing registration/exposure operations
where suitable and preserve local raster evidence at boundary alternatives on
these saved frames. Inspect registration validity and available support before
interpreting relative change. Compare the human-confirmed circular structures
with changing surrounding Foam appearance and verify their overlap with stored
boundary alternatives; retain rim negatives, mixed support and missing-support
cases as distinct limitations. Human context is attributed regression evidence,
not a hardcoded central exclusion or a physical pixel mask. No interpolation
through the feature, motion-only winner, new threshold or runtime promotion is
justified by this reply. This quantitative experiment has **not** been run here;
no additional video decode or Windows execution was performed while recording it.

## Detector Governance

- Logic-map nodes: `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: support-to-boundary promotion remains unvalidated; sample4's known box-based substrate veto is not repaired by selecting a local image peak. The human identifies the stationary, regularly spaced circular features as structures. Their exact overlap with saved boundary alternatives and the true Foam contour around them remain unmeasured.
- Logic-map impact: NONE — offline diagnostics and review preparation have no production caller, accepted scalar, temporal decision or publication effect.
- Failure-registry impact: NONE — existing identity leakage, correlated appearance and threshold-shortcut guards cover the rejected promotion; no new runtime mechanism or field efficacy claim.
