# Local corpus reuse for the uppermost-boundary target

Date: 2026-10-06. Inspected source: `77a3d3a1a243c4158984758a88aa7104bda83820`.
Scope: local file/metadata inspection and saved-image hash verification. No video
decode, detector execution, fitting, new human judgment or label change.

The user authorized continuing with the Mac corpus and will prepare independent
video separately. Independent-video delivery is not a prerequisite to this local
development work. Current gates remain owned by the [work plan](../../00-project/work-plan.md).

## Verified reuse inventory

All four local MP4s pass the existing `validate_local_corpus` byte-identity check.
All twelve MP4/recipe/truth hashes match the frozen
[corpus manifest](../../50-diagnostics/s11/s11-a-opencv-evidence-architecture-probe-manifest.json).
All 15 annotations match one saved D1 review item by run ID, Glass ID and frame;
recipe ID/hash, source-video hash and actual decoded timestamp also match.
All 30 clean/comparison PNG hashes match the saved D1 asset manifest. Forty-four
read inputs (12 corpus files, two D1 manifests, 30 images) retain their hashes.
This verifies stored identity, not fresh pixel decoding or physical truth.

| Video | Reviewed source frames | Usable / unusable | Existing review content and reuse |
|---|---|---|---|
| base_sample_1 | 144, 156, 240 | 3 / 0 | Oil Y=386, no Foam; notes identify overlay at 156/240. Weak Oil and overlay regression context. |
| sample2 | 0, 30, 60 | 3 / 0 | Oil Y=592; Foam front Y=320; notes identify reflection near ruler 50–60%. Reflection/Oil and independent Foam context. |
| sample3 | 900, 1035, 2848, 3147 | 2 / 2 | Oil Y=316/243 and Foam Y=286/195 on usable frames. Last two explicitly unusable due to focus; numeric truth absent. |
| sample4 | 0, 450, 900, 1470, 1680 | 5 / 0 | Reviewed Oil Y=860.5/852.5/848.5/855/858.5 and separate Foam fronts. Oil/Foam regression context. |

These are 13 usable **scalar Oil annotations**, not 13 candidate-identity labels,
independent objects or episodes. The ten Foam-present annotations retain their
separate front. Notes such as “Foam 0%” describe ruler position alongside a stored
Foam front; they are not automatically rewritten as Foam absence.

The [R22 baseline evidence](s11-r22-ownership-evidence-replacement.md#protected-baseline)
already documents development/replay exposure of every video. Preserve regression
roles for the complete sources; do not rename cases or split another region into
untouched holdout. Physical recording/session independence among the four files
and their relationship to SPL#1 are not established by filenames or distinct hashes.

## Compatibility with the clarified target

The [uppermost actual fluid boundary contract](../../rotary_oil_level_tracker_ssot_spec.md#다층-유체의-추적-대상)
does not merge Foam into Oil or select the minimum-Y raw proposal. Existing
`.oiltruth` Oil coordinates remain valid in their original scalar regression
scope. They contain no explicit multi-fluid target-role binding and no current
candidate input index, witness hash or reviewed per-sector contour.

All 15 annotations have `official_debug_record_id=null` and their historical
tracking references have `candidate_baseline_available=false`. The matched D1
comparison PNGs distinguish old published lines from **agent-proposed** dashed
lines. Neither those lines nor the D1 artifact bands may become current native
paths, new negative labels or target truth by coordinate proximity.

Reuse is therefore available now at two levels:

- Preserve all 13 usable scalar/Oil-Foam observations and two unusable controls
  for existing regression. No relabeling or repeated broad human review is needed.
- Use linked RGB/review notes to prepare exact-frame candidate-guided controls.
  Candidate identity, uppermost target role and optical-negative attribution need
  their own explicit correspondence; these are `not_bound` in the inventory.

The existing [public witness probe](../../../tests/diagnostics/s11_interface_witness_probe.py)
already loads the usable truth frames and retains candidates. Its distance bins
are geometry (`remote_geometry_not_proven_negative`), not physical labels. Reuse
the existing extraction/review owners for the next preparation, not a second
classifier or a nearest-Y truth converter. The committed historical probe summary
contains aggregate R22-2 results, not a current frame/candidate review packet.

## First bounded preparation set

Selection is by already recorded failure type, before any new scoring or replay:

| Source/frame | Existing review | Purpose | Remaining binding |
|---|---|---|---|
| base_sample_1 / 156 | S1-02 | Weak Oil versus explanatory overlay | Current proposals versus historical Oil/overlay observations |
| sample2 / 30 | S2-02 | Actual Oil versus reflection | Exact reflected candidate, target role and support |
| sample4 / 450 | S4-02 | Separate Oil and Foam fronts | Candidate correspondence without Foam-to-Oil label transfer |

These are preparation cases, not three newly certified opposing controls. All
other usable annotations remain in regression; no score-based selection occurred.
Next prepare the three exact-frame current candidate inventories with existing
diagnostic owners and paired plain/candidate guides. If stored current witnesses
cannot be reused, a bounded local capture must identify its new source/runtime
and frame provenance; it must not masquerade as the old D1 run. Seek human input
only for concrete unresolved candidate/target correspondence. No Windows run or
independent-video delivery is needed for this preparation.

## Local artifacts and verification

Ignored local directory: `sample/output/s11-local-target-reuse-20261006/`.

- `inventory.json`: complete 15-annotation provenance, original notes, 12 corpus
  file hashes, 44 preserved-input hashes, 30 saved-image links and explicit
  unbound candidate/target status. SHA-256:
  `ca6c0a50e7360d5079864abc7bb9854e45bdf7058d0cf452f84e29e79a3ba3cf`.
- `inventory.csv`: same 15 annotation rows without nested asset objects.
- `build_inventory.py`: bounded read-only inventory construction, using the
  existing corpus validator; no production or test source was added.
- `review-index.html`: three paired historical clean/comparison views with their
  authority limitation displayed. It references original images without editing.

The exact D1 root is
`sample/output/s6-d1-mobile-truth-review-pack/worker-0f0bf70-20260731T151330Z/`.
Historical pack-preparation “confirmation pending” text remains historical;
current checked-in `.oiltruth` contains the later user dispositions. No claim is
made that historical packet proposals equal current detector candidates.

Metadata joins, corpus/asset hashes and before/after preservation passed. No
detector efficacy, calibration, independent holdout, W4-R2 entry or FIELD PASS
is established. `FIELD FAIL` and `NOT_EVALUATED` remain unchanged.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-PROJECTION`
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`
- First harmful stage: unknown for a new local challenger; no new predictions were generated. The concrete preparation gap is missing current candidate/target attribution in scalar truth.
- Logic-map impact: NONE — only saved corpus/truth provenance and development routing were inspected; runtime candidate authority and projection are unchanged.
- Failure-registry impact: NONE — geometry is not promoted to physical identity, original truth/exposure is preserved and no private-coordinate branch or threshold is introduced.
