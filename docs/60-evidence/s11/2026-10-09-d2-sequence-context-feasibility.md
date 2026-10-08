# D2 registered reference and sequence-context feasibility

**Disposition:** bounded input-dependency readout complete, **CLOSED WITHOUT
PROMOTION** for using reference overlap/non-overlap or appearance persistence
as a physical discriminator. Broader D2-B opposing-control efficacy is still
NOT_ASSESSABLE; this is not a completed classifier evaluation or a rejection of
all reference/temporal approaches. No production behavior or field status changes.
Base: `5eba72d9424c4cb10df1b42fa0dd3072f48e9a13`.
The [receipt](2026-10-09-d2-sequence-context-feasibility.json) contains frozen inputs,
all-chain aggregates, representative checkpoints and local artifact hashes.

## User clarification and qualitative reply

The user supplied a marked 42.5 s crop and said:

> 내가 점 찍은 부분들 (픽셀의 정확한 xy를 따지지마 대략적으로 찍은거니까)이 foam의 경계로 보이는데

This is an approximate Foam-boundary interpretation in the indicated neighborhood,
not a contour, scalar coordinate, segmentation mask or exact obscuration label.
No red-dot coordinates were extracted. The supplied JPEG is preserved unchanged
at `sample/output/s11-d2-sequence-context-20261009-001/user-foam-boundary-rough.jpg`,
with its SHA-256 in the receipt. The earlier 44 s reviewed glass reference remains
unchanged; neither interpretation supplies the other frame's per-pixel identity.
The 42.5 s question is closed at this qualitative scope. Complete visibility of
each glass pixel remains unknown without requiring a further microscopic question.

The user clarified that their question concerned **detector granularity**, not
whether they had to perform manual review. Frame-wise computation does not imply
that every microscopic contour must be semantically classified, or that decisions
must use only one frame. `ObservationSequenceResolver` already composes temporal
Oil and Foam owners. The product outcome remains meaningful level movement and
Foam episodes, with local ambiguity retained where needed.

## Frozen comparison and reuse

Reused all **156 chains / 6,240 links** from the
[closed ordered-patch experiment](2026-10-07-a2-patch-correspondence.md), including
both cadences, directions, all original geometry views and all seed roles. No
matcher, detector or video decoding was rerun, and no successful-only seed subset
was used to calculate the aggregates. The three plotted examples are explicitly
illustrations of these already reviewed controls, not a new evaluation set.

For every link, intersect the actual ordered-BGR query/winning sampling rectangles
with the existing 125-pixel reviewed reference. The radius, original source X,
source crop origin and frame/index identity remain unchanged. Count the reference
pixels in the entire searched vertical domain separately. These are **sampling
footprints**, not candidate-owned observed Canny contours or physical overlaps.
Reference visibility at other times is not assumed. In particular, masking these
pixels and rerunning the matcher would be a different experiment, which was not
performed here.

The additional contextual input is the scoped human-attributed glass reference;
the old patch matcher had only appearance. This bounded pass asks whether that
context justifies promotion of its existing outputs. It does not fit a score,
change an operating point, grant authority or create new target/scalar labels.
All recordings and previous labels remain exposed regression, not holdout.

## Result at sequence scale

The already human-reviewed true-fluid central forward chain, f1275–1320:

| Measurement | Result |
|---|---:|
| Links in the reviewed interval | 45 |
| Query patches containing reviewed reference coordinates | 41 / 45 |
| Winning patches containing reviewed reference coordinates | 40 / 45 |
| Maximum sampled reference pixels in either patch | 36 |

Thus even this successful physical correspondence uses image patches that include
registered structure coordinates. A patch-overlap veto would discard most of its
links. This is not a claim that the selected fluid contour itself is a glass edge.

| Existing central chain | 43 s match Y | 44 s match Y | Reference pixels in winning patch at 43/44 s |
|---|---:|---:|---|
| True seed f1260/idx4, forward; known appearance drift | 888 | 888 | 0 / 0 |
| Reviewed f1275/idx12 forward fluid correspondence | 829 | 839 | 33 / 0 |
| Wrong-target seed f1320/idx21, backward appearance chain | 821 | 822 at seed | 44 / 44 at seed |

These are saved appearance coordinates, **not new scalar truth**. The old
confirmed-seed failure is not repaired by this join. A lower appearance alias
can persist while sampling none of this upper reference. Absence from the small
registered patch does not mean absence of other structure.

At native cadence, 22/42 target-seeded and 20/36 wrong-target-seeded chains have
search domains entirely disjoint from the reference. The same counts occur in
the sparse-cadence view. Seed role applies only to the original candidate; these
counts are not whole-chain physical labels or independent trials. In particular,
the wrong f1320 seed's sector 3 persists near Y819–820 with no reference pixels
in its search domain. Persistence and no-reference overlap do not confer identity.
The main positive chain also overlaps the reference; no overlap threshold is
selected afterward to exploit the displayed count differences.

Local plot:
`sample/output/s11-d2-sequence-context-20261009-001/sequence-context.png`.
It juxtaposes the reviewed positive, existing confirmed-seed drift, and persistent
wrong-target-seed appearance. Lines connect recorded measurements for readability;
they do not create observations or interpolate official detector output.

## Decision and next engineering boundary

Keep the implemented D2-A1 diagnostic, but do not wire overlap/non-overlap or
appearance persistence into rejection, authority, selection or report output.
The current combination has not established a physical decision or the required
stationary/crossing/optical counter-controls. More fine-grained attribution of this
same small glass pattern is not the next requirement. The simple promotion attempt
ends here; no tolerance search, reference expansion, new seed choice or whole-band
mask follows. This also does not imply that every future joint model must fail.

The next local design must name **additional boundary/region information** and
explain how the existing owner can retain it before another challenger is run.
Source inspection confirms `MaterialPathEvidence.rows` is genuinely a path through
at most five sector profiles; its diagnostics are not hiding a dense contour that
can simply be exported. Whole-boundary reasoning would need a concrete representation
and controls, not renaming those pooled rows or averaging the old patch tracks.
Reuse `oil_material_path`, existing raw observations and region owners where they
fit; do not duplicate them without that boundary. No new contour algorithm is
implemented or accepted by this closeout.

Preserve the existing major-motion/episode outcomes and four Mac regression windows.
A future model may leave local portions unresolved without requiring semantic
classification of every pixel, but motion-only anchors, stationary-as-structure,
whole-box labels and fabricated numeric output remain disallowed. O2 precedes
Oil authority/association changes; Foam work retains its separate owner/gate.
No further user judgment, Windows action, export or ML task is requested here.
Live sequencing is in [Work Plan](../../00-project/work-plan.md).

## Verification and preservation

The original matches hash agrees with its frozen execution receipt. All inputs
were checked before/after; the annotated JPEG is byte-preserved. The readout
accounts for all 156 chains and 6,240 links. The known human-positive interval
contains exactly 45 links; every dependency count is bounded by the same 125
reference pixels. Source and old labels/recipes are unchanged. The prior diagnostic
machine receipt is not rewritten; the new receipt records this follow-up separately.

No production tests or complete detector replay were repeated for this read-only
join. Verification covers saved-input identity, complete traversal/counts,
independent coordinate-set recomputation, document links and detector governance.
It does not add evidence of field effectiveness or a safe changed detector.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: existing appearance tracking can follow another structure despite a correct seed; this reference-footprint join adds no physical discrimination. Private first causes and local contour identity remain unknown.
- Logic-map impact: NONE — this saved-output readout and scope clarification add no executing detector owner or call path.
- Failure-registry impact: NONE — existing motion/geometry identity leakage and provenance guards remain; no mechanism is repaired or newly field-qualified.
