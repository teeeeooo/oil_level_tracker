# Sample3 source-role closure and qualified evaluation use

Date: 2026-10-10. Base head: `c4ad1267ac1e1d996cd2b72626c8f8af2261285c`.
This records the [C/D reply](2026-10-10-sample3-confirmation-role-reply.json)
and applies the existing
[source/truth qualification contract](../../30-validation/s11-interface-observability-witness-validation.md#local-source-and-truth-qualification).
No new detector experiment, relabelled scalar benchmark or behavior change.

## Source judgment — closed

The user identifies **C/f1949/65.031633s as a glass external-frame structure** and
**D/f2024/67.534133s as not visible because of focus loss**. The reply also reports
glass-position changes and intermittent focus loss within sample3. It does not
define exact start/end times for those conditions.

The frozen [C/D image](2026-10-10-sample3-confirmation-role-review.png) and
questions remain unchanged. Their short marks bind these physical judgments to
the shown features, not exact Y truth or every nearby candidate. C is regional
non-Oil opposition. D is unassessable, not a physical Oil-absence label, a false
candidate label or evidence that any particular detector abstention is correct.

In the [saved causal trace](2026-10-10-sample3-reappearance-causality.md), the
marked C phase-scan candidate belongs to provisional track 000066:0063. The
same internal track is confirmed at D with `ANCHOR_TRAJECTORY`. Its confirmation
window contains the reviewed structure and an unobservable endpoint, so the
reported 22px upward progress is **not certified Oil movement**. This closes
the earlier role question; it does not establish every intervening association
edge or the precise contribution of glass/image displacement versus appearance.
The recent-basis-only probe remains CLOSED WITHOUT PROMOTION.

## Suitability depends on the claim

Sample3's full 30.03–105s replay is **unsuitable as the primary physical accuracy,
continuous-tracking or one-second-cadence benchmark** under one unchanged Recipe.
That does not erase the recording or its qualified local evidence.

The actual current entry path is
[`CurrentFrameEvidenceOwner.observe`](../../../src/oil_tracker/adapters/vision/phase_frame_detection.py)
→ [`build_mask_bundle`](../../../src/oil_tracker/adapters/vision/geometry_masks.py):
crop, ellipse, margin and exclusions are constructed from `glass.geometry`.
[`GlassGeometry`](../../../src/oil_tracker/domain/geometry.py) also owns the fixed
zero line. The current crop path does not relocate the geometry to follow the
visible glass. Registered raster motion supplies local evidence; it does not
by itself establish a new glass coordinate system or revalidate calibration.

Consequently, position changes can mix external structure into an old mask,
change which physical column a source X samples, and contaminate apparent
interface motion. Focus loss separately removes the evidence needed to judge a
boundary. These are input/geometry/observability limitations, not reasons to
force the phase gate to publish more numbers.

| Retained evidence | Permitted use | Not justified |
|---|---|---|
| Full saved replay | Decode/output/provenance compatibility, deterministic behavior, geometry/blur stress | Whole-window physical accuracy or continuous visible-Oil recall |
| C external-frame feature | Regional structure rejection and contaminated-history counter-control | Whole-frame Oil absence or truth for every nearby member |
| D and old 95/105s focus-loss views | Unassessable localization; inspect unsupported claims separately | Exact position errors, false-negative scoring for an invisible boundary, automatic all-abstain PASS |
| User-marked A/B at 75.04/78.04s | Regional visible-Oil positives; missing output remains documented | Exact scalar/contour, calibrated height, valid inherited track or continuous truth between views |
| Old 30.03/34.5345s annotations | Original qualitative/ruler scope and legacy scalar comparison | Newly certified fixed-center pixel truth or silent Recipe correction |

Future use of a stable subsegment requires source-based bounds chosen before
new outcomes, compatible glass geometry and adequate visibility for the metric.
If a separate geometry or reset is needed, declare a new configuration/experiment
and compare baseline and candidate under the same frozen setup. Do not silently
re-crop an old replay, cherry-pick easy frames or reinterpret unchanged outputs
as an accuracy improvement after removing difficult references.

## Development consequence

Close this sample3 causal branch at the input/identity qualification. Do not make
closing its long numeric gap or preserving a questionable old value the main
optimization target. Preserve every saved row and all 13 legacy scalar values;
the existing comparator still reports its original PASS/FAIL as **legacy scalar
agreement**, with physical acceptance NOT_EVALUATED.

Return positive discrimination work to the already qualified **water/sample5
B/C surface cases** and the **scoped sample4 target-domain positives/opposition**.
Beer/milk remain separate layer/projection/visibility controls. These clearer
views are not automatically calibrated, continuously labeled or untouched
holdouts, and public drinking glasses do not replace target-domain validation.
The next mechanism still needs a distinct physical observation and a frozen
positive/opposing/unresolved comparison under O2; this reply licenses no new
threshold, phase or tracking shortcut.

No further sample3 source review or Windows task is required to adopt this
evaluation scope. Supporting moving glass as ordinary calibrated input would
need a separate geometry/registration contract; this investigation adds no such
feature or promise. Local qualification does not change the field disposition.

## Verification

- Reply, question, image, source and prior causal archive hashes bind. C/D
  diagnostic markers each join exactly one saved candidate; source/index/track
  and lifecycle values are checked against the prior 151-row evidence.
- Earlier A/B, unusable labels, saved Recipe and original legacy comparison
  remain unchanged. No new video replay or detector test is needed for these
  source-role and evaluation-interpretation updates.
- Focused reference/link checks, detector governance and `git diff --check`
  cover the changed documentation and metadata.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`.
- First harmful stage: C supplies a reviewed non-Oil feature in the internal confirmation history and D is unobservable; that history cannot certify Oil motion at `OIL-TRACKLET`. The exact earliest wrong association edge remains unproven. The baseline's later phase exclusion is not sufficient reason for a phase repair.
- Logic-map impact: NONE — current geometry and tracklet owners are inspected without changing their behavior.
- Failure-registry impact: NONE — this is a newly bound source instance of the existing motion/identity/provenance risks, not a new mechanism or field qualification.
