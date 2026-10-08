# D2 optional registered-support capture and review

The user approved optional narrowing during recipe setup. The existing proposal
list now opens original/edge/support previews and lets the operator restrict a
review rectangle. An explicit checkbox records only the displayed visible raw
edges as reviewed support. Without it the scope remains uncertain. Existing
geometry-based rejection is unchanged; no new physical classifier is adopted.

Base: `2d760bbcff5ef762fe96d4dfd811ddcc660e3ac5`. The
[machine receipt](2026-10-08-d2-reference-ui.json) pins changed source and the
local saved-image demonstration. The [architecture contract](../../20-architecture/s11-interface-observability-witness-architecture.md#registered-support-reference--proposed-input-contract)
owns the format and semantics; [validation controls](../../30-validation/s11-interface-observability-witness-validation.md#registered-support-input-controls)
own acceptance. Live sequencing remains in [Work Plan](../../00-project/work-plan.md).

## Implementation and reuse

- Existing `OpenCvArtifactProposalService` keeps its list API and exact template
  geometry. It attaches bounded snapshots from existing debug images, including
  native path diagnostics when present. No second preprocessing run invents a
  cleaner reference.
- The new vision reference owner encodes/decodes rasters and restricts raw edges;
  matching stays in the unchanged calibration owner. The immutable domain snapshot
  and existing recipe serializer retain evidence without workstation paths.
- Bootstrap injects the raster review service through the application port;
  the UI imports no vision business adapter or raster framework.
- The nested preview reuses existing canvas image/zoom/pan behavior. It returns
  a reference to the private ROI editor copy. Existing outer Apply/Cancel, undo,
  dirty state and profile storage own the final change.
- Preflight omits reference-only metadata from behavior identity and retains
  old template fields. Legacy templates serialize exactly as before.

Snapshots are at most 640×160 original pixels and 1 MiB of canonical JSON, with
at most 16 per Glass. PNGs are embedded and hashed; cropping is explicit, with
no resizing or component expansion. Changed geometry or missing/corrupt data
cannot silently acquire authority. A snapshot does not claim the structure is
still visible in another frame.

## Verification

**87 focused tests passed** across reference capture, recipe roundtrip,
calibration/proposal, preflight identity, real Qt editor entry/lifecycle and
existing canvas/workbench owners and UI import boundaries. Thirteen new unit
cases and nine new Qt cases (including real bootstrap service composition)
include non-repository cwd/Unicode-path relocation, raw pixel equality, true
source time binding, corrupt/missing/oversized evidence, reference count bounds,
changed ROI/dimensions/settings/template geometry, connected/disconnected edge
restriction, masked/glared pixels, nested/outer cancellation and reopening.

Matcher decisions on 90 candidates spanning matching/nonmatching positions are
identical with and without references. Complete current-frame detections also
match for an empty/partial/Foam synthetic sequence using separate detector
instances. These are metadata-neutrality controls, not field effectiveness.

The saved f1320/44 s PNG and recipe from the prior setup audit were reused without
video decoding. A fresh proposal call returns the same **12 template geometries**
(random template IDs excluded) and preserves all 12 reference crops exactly.
Largest snapshot: **39,238 bytes**. A one-reference demonstration recipe is
**25,199 bytes**, saves and reloads exactly. Original input hashes are unchanged.
The assistant inspected the rendered editor and scope preview.

Local assets/runner: `sample/output/s11-d2-reference-ui-20261008-001/`.
The screenshot rectangle is a UI demonstration, saved as `mixed_or_uncertain`;
it is **not** a human optical label. Original recipes, images, target labels and
field evidence were not modified. No new user judgment was requested.

## Limits and next boundary

The UI supports rectangle restriction plus raw-edge confirmation, not freehand
tracing. Reviewed support does not change the old veto's scope. Automatic
exclusion, target recovery and cross-frame correspondence are not implemented.
The 49.5/52 s regression and other closed experiments remain unpromoted.

No Windows run, private image transfer, model fitting or O2/O3 entry occurred.
Native Windows rendering/packaging was not tested. Next specify a bounded
diagnostic correspondence rule with crossing/stationary/obscured and mixed
counter-controls before any detector consumer. Field disposition remains
`FIELD FAIL`; no immediate Windows task or physical judgment is needed.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: prior support identity is lost in the normalized template envelope; the first physical correspondence error remains unknown. This change preserves input evidence only.
- Logic-map impact: NONE — setup capture and private review do not change existing frame, authority, tracklet, matcher or publication flow.
- Failure-registry impact: NONE — explicit scoped evidence preserves F09 and avoids F04/F10 identity shortcuts; no new physical cause or accepted repair is claimed.
