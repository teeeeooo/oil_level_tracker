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

## Prepared human motion checkpoint — no answer yet

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
motion/resolution must remain uncertain. Await that reply before adopting a
boundary mechanism. No Windows execution or new independent recording is required
for this checkpoint. Existing human ambiguity and FIELD FAIL remain unchanged.

## Detector Governance

- Logic-map nodes: `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`
- First harmful stage: support-to-boundary promotion remains unvalidated; sample4's known box-based substrate veto is not repaired by selecting a local image peak. Central structure/reflection identity remains unknown pending temporal observation.
- Logic-map impact: NONE — offline diagnostics and review preparation have no production caller, accepted scalar, temporal decision or publication effect.
- Failure-registry impact: NONE — existing identity leakage, correlated appearance and threshold-shortcut guards cover the rejected promotion; no new runtime mechanism or field efficacy claim.
