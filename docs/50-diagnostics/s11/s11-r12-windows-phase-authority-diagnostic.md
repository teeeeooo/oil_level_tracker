# S11-R12 Secure-Windows Phase and Authority Diagnostic

## Scope and provenance

This diagnostic reconciles the secure-Windows R12 Base/Accum replay with
source-frame visual review and the final CSV/sequence records supplied from the
isolated workstation. The transferred package came from a GitHub ZIP and
contains no Git SHA. The sequence resolver reports
`r12-phase-composition-replacement-v1`; `detector_version` is absent. All counts
below are therefore tied to that bundle and resolver version.

Several intermediate reports were corrected before this record was written:

- `foam_is_valid` is `True`, not `False`, on the reviewed confirmed-Foam rows;
- CSV contains 92, not 95, Oil rows in Y190–297; and
- R11 compatibility fields named `calibrated_dynamic_seed`, `path_member` and
  `motion_keyframe` do not define R12 independent anchors.

## Final output

| Glass | rows | numeric Oil | public Foam | legacy valid | Oil valid | Foam valid |
|---|---:|---:|---:|---:|---:|---:|
| Base | 601 | 0 | 0 | 0 | 0 | 0 |
| Accum | 601 | 164 | 43 | 0 | 0 | independently true on published rows |

The zero aggregate `oil_is_valid`/legacy-valid count is consistent with the
field failure. Foam is a separate series: for example, 670.5 and 673.0 s have
`foam_is_valid=True`, confidence 0.96 and confirmed same-frame coordinates
while Oil is unresolved.

## Base: proposal absence precedes sequence failure

Reviewed source coordinates are Y437 at 540 s, Y360 at 634 s and Y435 at
674 s.

| time | candidates within 25 px | candidates within 80 px | nearest | first material failure |
|---:|---:|---:|---|---|
| 540 s | 0 | 2 | Y391, 46 px | no local proposal at the reviewed row |
| 634 s | 2 | 7 | Y380, 20 px | continuation only; no trajectory support |
| 674 s | 0 | 0 | none | no representation generated a proposal |

The 634 s Y380 high-recall and Y338 material-path rows are both
`CONTINUATION_ELIGIBLE`, but cluster and trajectory support are zero. Across
Base, 7,069 final continuation candidates stop at `NO_TRAJECTORY_SUPPORT` and
the qualified-anchor count is zero.

R12 therefore fixed the previous unsafe behavior without solving recall. The
R11 Y724–873 reflection/bracket path has zero R12 numeric rows, anchors and path
members. This is a valid safety improvement, not a Base effectiveness pass.

The replacement implication is two-stage:

1. add a bounded, horizontally distributed phase-change proposal that does not
   require the reviewed row to be a strict local maximum; and
2. keep that proposal continuation-only until independent same-frame phase
   identity exists. Proposal recovery must not recreate motion-only authority.

## Accum: weak upper residue creates anchor authority

CSV contains 164 Oil rows. Their exact distribution is:

- Y181–188: three rows;
- Y190–297: 92 rows in 676.0–685.0 s and 690.0–726.5 s runs;
- Y299–350: 52 rows; and
- reviewed lower-Oil band Y425–475: 17 rows.

The 92 selected residue rows decompose as follows.

| dimension | distribution |
|---|---|
| source | high recall 32; material path 32; Oil hypothesis 28 |
| authority reason | continuation 59; semantic-sequence anchor 25; corroborated-material-path 8 |
| trajectory support | 92/92 |
| cluster support | 33/92 |
| material-texture conflict >= 0.5 | 85/92 |
| bounded Foam-material identity >= 0.5 | 0/92 |

The 33 semantic/corroborated anchor rows are the seed set that makes all 92
rows trajectory-supported. Calling this run “anchor-free” because the removed
R11 calibrated fields are zero is incorrect.

Representative false semantic anchors expose the authority leak:

| time | Y | boundary | ambiguity | texture conflict | cross-representation | semantic support |
|---:|---:|---:|---:|---:|---:|---:|
| 676 s | 251 | 0.275 | 0.611 | 0.950 | 0.675 | 1.000 |
| 684 s | 196 | 0.268 | 0.607 | 0.750 | 0.714 | 1.000 |

Both are non-material-path `oil_hypothesis` rows. The R12
`semantic_sequence_anchor` gate checks texture conflict only when
`material_path=True`, so these weak, ambiguous, high-conflict ordinary rows
bypass the conflict gate and become independent anchors. Later high-boundary
material/high-recall residue rows then continue the wrong component.

This is not fixed by a universal texture-conflict rejection. The reviewed
lower Oil at 672 s also lies inside the broad material mask and receives
texture conflict 1.0. Its strong candidates at Y438 and Y461 are continuation
eligible with trajectory support, but the final frame is unknown. At 684 and
689 s, reviewed lower candidates near Y450 are demoted by track opposition
while upper residue wins.

The required distinction is composition-aware:

- an upper Foam/residue row must not anchor merely through semantic continuity;
- a strong, lower, ordered Oil boundary may remain admissible even when a
  broad Foam/material raster overlaps it; and
- trajectory/track opposition must compare physical phase identity, not only
  recurring Y buckets or generic semantic support.

The basic Windows trace records only the final
`GLOBAL_PATH_OR_RUN_BOUND` result at 672 s. It does not record the node after
each path stage, so claims about the exact first `_best_path` versus
`_bound_continuation_runs` mutation are inference, not observed evidence. R13
trace must emit the first path-stage transition directly.

## Foam and validity

The 650–700 s Foam funnel is:

| stage | frames |
|---|---:|
| raw Foam front | 44 |
| sequence eligible | 34 |
| episode confirmed / CSV finite | 20 |

At 670.5 and 673 s, confirmed Foam is independently valid despite missing Oil.
`R8_FOAM_WITHOUT_RESOLVED_OIL_STATE` describes composition context; it does not
invalidate Foam. This proves the R12 per-series storage/composition repair is
working and must be retained.

The review model carries each point's validity, but
`ui/widgets/result_review_graph.py` currently plots every finite value without
masking invalid points. The renderer therefore violates the R12 downstream
contract even though CSV and the graph model are correct.

## Replacement boundary

R13 must replace, not layer around, the remaining failed policy:

- semantic anchor authority must use the same typed phase/conflict contract for
  every candidate family;
- ordered lower Oil must have an explicit composition identity rather than a
  global “texture clean” requirement;
- trajectory components and recurring-track opposition must preserve that
  identity;
- Base proposal recovery must not create automatic anchor authority;
- per-stage path decisions must be observable in basic trace;
- graph rendering must mask Oil and Foam with their own validity; and
- obsolete R11 compatibility diagnostics and stale R12 aliases must be removed
  from active control flow while old bundle reading remains compatible.

No private Glass ID, timestamp, filename or truth coordinate may enter
production behavior.
