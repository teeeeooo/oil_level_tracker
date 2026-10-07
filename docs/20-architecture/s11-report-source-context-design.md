# S11 report source-context design

Frozen starting point: `a17d9871693ea23efc7da141fb599b6f5ba472b7` (2026-10-07).
Scope: bounded report candidate; does not change detector identity or field status.
Current execution authority remains [Work Plan](../00-project/work-plan.md).

## Purpose and acceptance unit

A useful report preserves the order and direction of major interface/Foam motion,
material transitions and important uncertainty. Per-frame recall is diagnostic,
not the product objective. Local misses/errors are tolerable unless they invent,
hide or reverse a consequential episode. Perfect output on seven reviewed frames
is neither necessary nor sufficient for report acceptance.

The existing report promotes reviewed wrong sample4 observations at 42/44 seconds
to global extrema. sample3 has a long Oil-observation gap covering visible change.
These are episode-level obstacles, not permission to interpolate missing Oil.

## Bounded source-context view

Add a separate time–height image below the numerical graph. Each column is the
per-row median RGB of the central 40% of the configured ellipse bounding width,
using only pixels inside the ellipse. Keep the original color/exposure; no CLAHE,
classification, track, truth, Oil/Foam output or optical masking enters this image.
This is spatial compression of source pixels, not another boundary detector.
Reflections, fixed structures, overlays and curved/local features remain possible.

Use a uniform requested-time grid within the analysis interval, at no more than
the analysis sampling rate and at most 360 columns per Glass. Record requested
and actual decoded times/frame IDs; failures or excessive seek error stay blank.
The rendered raster is at most 240 height bins; vertical bin medians are disclosed
as compression, never new measurements. No temporal interpolation or hidden
carry is allowed. Source failure must not fail an otherwise valid result bundle;
metadata and the report disclose unavailable context. Cancellation still aborts.
PNG/JSON assets remain in the offline bundle; raw videos are not copied.

Foam plot timestamps also receive the existing two-second report connection cap.
Missing Foam stays missing, with no endpoint bridge. Keep every finite marker.
Oil/CSV/events/Result Review/judgment and detector version remain unchanged.

## Verification frozen before candidate execution

1. Unit controls: static and translating source bands, dark/light polarity,
   reflections preserved, masking/resize/zero-axis correctness, source immutability,
   irregular seek/decode failure, absent video, resource bounds and cancellation.
2. Foam controls: long timestamp jump and explicit missing value never connect;
   single observations remain visible; both report graphs use the same helper.
3. Fresh four-video baseline/candidate pipelines: identical tracking, events,
   recipes, per-series validity and same-frame provenance; validate offline assets.
4. Compare raw scenes and graphs over whole qualification windows. Report separately
   software integrity, available context and remaining incorrect physical claims.
   Existing user target correspondences remain exposed regression evidence only.
5. No detector promotion, independent-human usability PASS or Windows PASS is
   inferred from a more informative visualization. No new human review required.

## History Review

- Logic-map nodes: `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: report gap/endpoint/namespace repairs; A2 all-abstention region-exchange closure; R10 motion-only false-path promotion.
- Prior mechanisms rejected: smoothed/interpolated repair, whole-track privilege, relaxed region conjunction, reviewed-Y tuning.
- Preserved contracts: original observations, independent Oil/Foam, immutable truth/recipes, bounded resources and separate field acceptance.
- Difference from prior failures: a separately labeled raw-source visualization never grants identity or changes a numerical observation.
- Logic-map impact: UPDATED — register the independent raw-pixel asset under `RESULT-PRESENTATION`; detector/control-flow/publication authority remains unchanged.
- Failure-registry impact: NONE — addresses presentation exposure under F09 without declaring an upstream physical-identity repair.
